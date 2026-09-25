# /pika:ugc-ads

## 参数

| 参数 | 默认 | 备注 |
|---|---|---|
| `url` | 必填 | 产品 URL — 驱动类别检测和节拍替换 |
| `avatar_url` | 内置回退 | 人设肖像 URL；作为 `@Image1` 引用传入。当省略时，技能使用预生成的皮克斯风格女性创作者肖像 |
| `provider` | `seedance` | seedance：擅长 UGC 自拍 / 讲头视角，具有原生唇同步，单提示多节拍，支持 3:4。kling：显式 `shots[]`，仅支持 9:16/16:9 |
| `aspect_ratio` | `9:16` | `3:4` 仅限 seedance（kling 拒绝 3:4） |
| `variants` | 未设置 | 可选逗号列表，用于共享生成输出。支持：`9:16`，`16:9`，`1:1`。保持昂贵的 UGC 渲染共享，然后在最终阶段重新构图。 |
| `category` | 自动 | `HAUL` / `APP` / `FOOD` / `BEAUTY` / `FITNESS` / `TECH`；从 URL 自动选择 |
| `captions` | `true` | TikTok 风格的词语块字幕烧录在最终视频顶部 |

## 成本透明度门

在执行任何付费 MCP 调用之前，调用一次 `identity_balance({verbose: true})`。显示当前余额、近期消耗率和剩余运行时间，然后使用以下确切消息门控运行：

> 预计成本：典型的 Seedance UGC 广告（包括回退/重试预算）约 4,000 信用点（约 40 美元）。这超过了 5 美元，请回复 `proceed` 继续或 `cancel` 停止。

在用户回复 `proceed` 之前，不要调用任何付费 MCP 工具。如果用户回复 `cancel`，则停止而无需生成。门控在产品 URL 知道后、在头像分析、截图捕获、视频生成、字幕或付费重试之前运行。

## 运行时预期

典型端到端运行时间：**6–12 分钟**。分解：

- 第 1 步（WebFetch）+ 第 3 步（capture_website 截图）：~10–30 秒
- 第 7 步 (`generate_reference_video`): ~3–5 分钟（seedance）, ~5–7 分钟（kling）
- 第 7b/c 步（卡通化 + 重试）：如果 seedance 审查拒绝头像，增加 ~1–2 分钟
- 第 8 步（确定性品牌/规格叠加）：1-2 个 `edit_text_overlay` 调用，~30 秒–5 分钟总时间
- 第 9 步（字幕）：单个 `add_captions` 调用，~30 秒–5 分钟（转录 + 一次性烧录）

如果运行时间超过 15 分钟而没有进展，则有问题——检查工具报告的生成状态和错误消息。


## 生成前时钟保护

在技能开始时，一旦产品 URL 可用且成本门已通过，启动计时器。等待用户 `proceed` 回复花费的时间不计入准备时间，并且不得触发此保护。第一个付费生成调用是 `generate_reference_video`，这是耗时的付费阶段，必须在技能开始后的 5 分钟内调用。如果你在技能开始后的 5 分钟内没有调用 `generate_reference_video`，则在任何付费生成调用之前停止，并报告 `failed_pre_generation_timeout` 以及你目前拥有的内容：抓取的产品事实、选择的类别、头像来源、截图状态、草稿对话以及确切的阻止器。不要继续改进脚本措辞、提示基础或拍摄顺序。

在准备阶段的每个检查点之后，在付费生成调用之前打印单行进度检查点：
- `Stage 1/3 done — product fetched and categorized.`
- `Stage 2/3 done — avatar and screenshot ready, composing dialogue.`
- `Stage 3/3 done — prompt locked, calling Seedance now.`

脚本和提示迭代最多 2 次。在最多 2 次迭代后，将你拥有的内容发送到 `generate_reference_video`；不要继续润色钩子、结尾或屏幕特写措辞。


## 长任务 `task_status` 投票

当任何长时间运行的生成或编辑调用返回带有或没有初始状态的 `task_id`（包括 `{task_id}`，`{task_id, status: "queued"}` 或初始 `queued`，`running` 或 `processing` 状态）时，立即记录任务 ID 和开始时间。

- 在终端 (`completed | failed | cancelled`) 之前，在紧密循环中调用 `task_status({task_id})`。不要手动睡眠和不要 Bash 投票；工作进程保持每个状态调用打开。
- 在状态为 `queued`，`running` 或 `processing` 时，每 60 秒发出一条可见的进度行：`Seedance i2v queued for {N}m {S}s... still processing`。在投票 Kling、GPT-image-2、字幕或编辑任务时，替换提供者/阶段标签。
- 在 `completed` 时，解包返回的结果 URL 并继续。
- 在 `failed` 或 `cancelled` 时，向用户显示失败，包括 `task_id`，状态和最后的状态消息。
- 在原始提交后的 15 分钟内，如果任务仍然非终端，调用 `task_cancel({task_id})`，然后向用户显示失败。如果取消报告任务已经终端，再次调用状态一次并报告终端结果。
- 在原始任务仍然为 `queued`，`running` 或 `processing` 时，不要提交重复请求。
- 异步投票预算：一个活动任务和一个 15 分钟投票窗口。在投票上限用尽后，取消任务并显示失败，而不是提交另一个付费渲染，除非后续步骤明确允许在原始任务终端后进行单独的受限制重试。

## 引擎选择：Seedance 默认，Kling 回退

对于 UGC 自拍/讲头广告，默认使用 Seedance，因为它擅长原生唇同步、单提示多节拍和可选 3:4 输出。当调用者显式传递 `provider=kling`，或在使用停止消息后用户选择 Kling 时，在 Seedance 用尽受限制的卡通化重试后使用 Kling。Kling 的权衡是更严格的宽高比支持，但有一个单独的审查路径和显式的拍摄分割。


## 步骤

### 0. 解析输入（空参数菜单）

从 `$ARGUMENTS` 中剥离标志和 `key=value` 参数。如果没有任何产品 URL 剩余，并且先前上下文中没有可用的产品 URL，则打印此菜单并停止：

> **哪个产品应该推广 UGC 广告？** 必填：
>
> - **产品 URL** — 用于抓取产品名称、类别、视觉参考和语言的页面
>
> 可选：`avatar_url=`, `provider=seedance|kling`, `aspect_ratio=9:16|3:4`, `variants=9:16,16:9,1:1`, `category=auto|HAUL|APP|FOOD|BEAUTY|FITNESS|TECH`, `captions=true|false`.

如果产品 URL 存在，则无声跳过此步骤。


### 1. 抓取 + 分类

`WebFetch` URL：拉取 `product_name`，`brand_name`，价值主张，品牌颜色，产品形式，包装，英雄文案，目标用户，类别，**以及页面的主要语言**。如果传递 `category=`；否则信任 WebFetch 信号；回退到 HAUL 用于实体，APP 用于数字。

从抓取的页面构建两个基于事实的列表：

```json
{
  "grounded_specs": [
    {
      "claim_text": "250W 总输出",
      "value": "250",
      "unit": "W",
      "source_quote": "包含确切值的可见源页面文本",
      "source_url": "<产品 URL>"
    }
  ],
  "claims_allowlist": ["250W 总输出"]
}
```

每个数字规格声明（`W`，`mAh`，`%`，分钟，端口，价格，尺寸，数量，充电速度，电池大小，排名）必须来自可见的源页面文本，并包括 `source_quote`。如果源页面没有明显支持数字，则将其从 `grounded_specs` 和 `claims_allowlist` 中排除。不要从产品类别、型号名称、常识或竞争对手页面推断规格。


### 2. 解析头像（如果缺失则回退到内置）

- 如果传递了 `avatar_url` → 原样使用。
- 如果没有传递 → 使用内置回退：
  ```
  https://cdn.pika.art/v2/files/agent/17d62bf9-0edb-49e4-9ba9-2c5419fa518f/seedream-1777624057811.jpeg
  ```
  预生成的皮克斯风格 3D 动画肖像，年轻的女性创作者——预卡通化，因此 seedance 审查直接接受它，足够中性以适应任何类别。注意在最终摘要中说明已使用回退，以便调用者知道下次提供自己的肖像以保持人设一致性。


### 2.5 头像类型探测（用于创作者肖像）

在步骤 7 之前和任何付费 `generate_reference_video` 调用之前，运行此探测。它适用于调用者提供的 `avatar_url`，内置回退或任何作为 `@Image1` 选择的创作者肖像。内置回退已经是非 IP 风格的创作者，但仍然在最终摘要中记录其来源。

调用 `analyze_media` 一次：

```
query: "对付费视频生成进行图像分类。这是一张真实人物的肖像照片，一个 AI 生成的逼真肖像，一个风格化/插画角色，还是一个可识别的商标/版权角色，例如蝙蝠侠、皮卡丘或米奇？仅返回严格的 JSON：{ \"avatar_type\": \"real_human\" | \"ai_realistic\" | \"stylized_illustrated\" | \"recognized_ip\", \"recognized_character\": string | null, \"moderation_risk\": \"low\" | \"medium\" | \"high\", \"recommendation\": \"proceed\" | \"warn\" | \"reject\" }.当没有识别特定角色时，`recognized_character` 使用 null；永远不要在该字段中写入“none”，“unknown”或解释性文字。"
```

根据结果路由：
- **识别的 IP / 版权风险** -> **仅在** `avatar_type` 为 `"recognized_ip"`，或 `recognized_character` 称呼特定角色（例如 `"Batman"`），或当 `moderation_risk` 为 `"high"` 且 `recommendation` 为 `"reject"` 时 **停止**。将 `recognized_character: null`，空字符串，`"none"`, `"unknown"`, `"n/a"` 和低/中 `moderation_risk` 视为本身不足以停止。在真实/风格化路由之前运行此检查。即使 `avatar_type` 为风格化/插画，蝙蝠侠仍然是蝙蝠。

- **真实人类 / AI 生成的逼真** -> 正常进行。
- **风格化 / 插画** -> 正常进行，并显示可见警告，说明风格化头像可能被 Kling 接受，但在 Seedance 审查下可能不一致；只有当用户提供了或接受了该头像时才继续。
- **商标/版权** -> **停止** 在生成之前。向用户显示此消息：`头像似乎是商标角色 ([X])。大多数视频提供者将进行审查并拒绝生成。传递 `avatar_url=<真实照片 URL>` 以覆盖。


### 3. 捕获产品截图（尽力而为）

调用 `capture_website` with `mode: "screenshot"`。使用 `mobile=true` 对于手持产品类别（APP / FITNESS / BEAUTY）以便捕获的页面渲染为肖像手机屏幕；`mobile=false` 对于桌面上下文类别（HAUL / TECH / FOOD）。

如果调用失败（超时，浏览器池宕机），重试 **一次**。如果仍然失败，则不使用截图继续——技能降级但功能正常。特写节拍描述页面仅通过文字。Beat 2 的 `reference_images` 仅包含 `[avatar_url]`。

捕获 URL → `screenshot_url`（或 null）。


### 4. 组合提示

完整提示是一个传递给 **一个** `generate_reference_video` 调用的多节拍字符串。结构化文字（非 Markdown 破折号）。每个节拍都有一个 `Says: "..."` 行用于唇同步。目标语速约为每秒 5.5–6 个词，整个 15 秒广告（约 85–90 个词）。`@Image1` 是头像，`@Image2` 是当可用时截图。

**所有 `Says: "..."` 行都使用步骤 1 检测的语言编写。** Seedance 和 kling 唇同步处理多语言；如果产品页面是中文 / 日文 / 西班牙文 / 等，对话应为该语言。步骤 5 的钩子原型是语言无关的——调整修辞方式以适应语言的天然语调。

**规格接地规则：禁止编造数字。** 任何口语或视觉数字/单位声明必须逐字出现在 `claims_allowlist` 中。如果一个数字不在 `claims_allowlist` 中，则定性重写该行（例如，“充电快”，“多个端口”，“大电池”）或省略声明。不要说“50% 在 28 分钟内”，“3 个端口”，“140W”，价格，数量或时间窗口，除非该确切声明有源支持。

**品牌/规格文本渲染规则：** 不要要求 Seedance 或视频模型渲染品牌标志、产品标志、包装标签或规格文本。视频模型文本会变得混乱。提示可以显示 `@Image2` 作为参考，但任何必须可读的新品牌名称或规格副本都是稍后通过确定性步骤 8 叠加添加。

```
HOOK (0–3 秒) <视觉设置 + 创作者框架 + 脸/身体提示>. 对着镜头快速且充满活力地说: "<钩子行>". <风格锚点——手持 POV，真实，原始, 原始>.
跳切 1 (3–6 秒) <广角 POV — 创作者的身体语言，产品部分在边缘框内>. <脸提示>, 快速说: "<设置行>".
跳切 2 (6–9 秒) <下一个视觉节拍 — 可以是显示 @Image2 的屏幕特写，或者另一个反应节拍，取决于对话弧将揭示的节拍>. 说（如果它是屏幕特写，语音继续覆盖该镜头），快速且自信: "<揭示行>".
跳切 3 (9–12 秒) <下一个视觉节拍 — 同样的逻辑; 跳切之一是屏幕特写，其他是广角 POV 反应镜头>. 快速说: "<见解转折行>".
结尾 (12–15 秒) <自拍 POV, 胸部中景, 相同设置>. 对着镜头快速: "<结尾行>".

头像是 image 1，资产是 image 2
```

**屏幕特写节拍——广告中仅有一个：**
- 将屏幕特写放在哪个跳切（1, 2 或 3）上，取决于 *揭示* 行落在哪个跳切上。大多数广告将其放在跳切 2 上；如果叙事需要在更早或更晚的时间放置，则跳切 1 或跳切 3 也行。根据内容选择，而不是按槽位编号。

- 屏幕特写节拍显示 `@Image2` 恰好如上所示，并包含一个指向手势（一根手指从帧边缘进入，指向英雄文本或产品——没有点击，没有滑动，没有滚动，没有悬停在 CTA 上）。整个广告中唯一的屏幕交互是指向手势。

- 其他跳切是广角 POV 反应镜头：手放在膝盖上，床上，或两侧。

**信任 @Image2** — 当产品页面显示时，参考图像；不要用文字描述其 UI。描述 UI 会导致模型发明额外的面板/下拉菜单/侧边栏/动画。参考图像；信任它。

**确切一个** 屏幕特写节拍 — 提示组合 |  |  |
| **Write all Says lines in the language detected from step 1** | 提示骨架 | 强制 TikTok 风格的多切节奏，而不是一个连续的主持人镜头。 |
| **Trust @Image2** | 屏幕特写规则 | 防止在提供真实截图时发明产品 UI。 |
| **exactly one** screen-close-up beat | 提示组合 | 防止广告变成屏幕录制而不是创作者风格的揭示。 |
| **forbid inventing numbers** | 提示接地 | 防止不支持的规格声明进入叙述或叠加。 |
| **Deterministic brand/spec overlays** | 步骤 8 | 保持可读的品牌名称和规格副本，避免视频模型文本渲染。 |
| **single add_captions call** | 字幕步骤 | 避免串联文本叠加造成的质量损失和漂移。 |

## 示例

- `/pika:ugc-ads https://pika.me avatar_url=https://cdn/face.png` → APP_REVEAL, 9:16, seedance, 真实截图, 字幕开启
- `/pika:ugc-ads https://maisonbrune.com avatar_url=https://cdn/face.png aspect_ratio=3:4` → HAUL_UNBOX, 3:4, seedance
- `/pika:ugc-ads https://pika.me avatar_url=https://cdn/face.png provider=kling captions=false` → APP_REVEAL, 9:16, kling shots[], 无字幕
- `/pika:ugc-ads https://pika.me` → 没有 `avatar_url` → 使用内置的皮克斯风格女性创作者肖像，运行端到端
