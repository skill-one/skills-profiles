---
name: app-sizzle
description: 在用户要求应用炫酷效果或任务与以下示例匹配时使用。从真实的App Store截图生成电影感的1080p iOS应用预告片视频，并在生成前对每个选定的屏幕进行GPT-image-2增强处理。输出是一个节奏感强的电影预告片，由GPT增强的截图构建，结尾带有品牌标志/图标以及确定的`即将推出`覆盖层。屏幕来源自Pika MCP App Store抓取、实时网站（自动捕获）、用户提供的文件或URL。生成前会先获取真实屏幕和品牌资产。触发条件：应用炫酷效果、应用预告片、应用推广、iOS应用推广视频、应用视频、应用产品视频、即将推出、seedance、动态图形、为我的应用制作推广、为[应用]制作视频、gpt增强推广。不适用于：短形式消费者内容如GRWM、vlogs、UGC或非应用产品广告（使用content-video）；应用炫酷效果专门用于从App Store屏幕或真实应用UI获取的iOS应用预告片视频。
---

# App Sizzle — GPT-Image-2 增强版 iOS 应用预告片

从真实应用界面生成一段精炼的 15 秒应用预告片。每个选定的界面会通过 GPT-image-2 处理后再进行 Seedance 压缩，使得压缩后的截图成为更清晰的参考，而不会凭空捏造 UI。

## 成本透明度门禁

在进行任何付费 MCP 调用时，先调用一次 `identity_balance({verbose: true})`。展示当前余额、近期消耗速率和剩余额度，然后用以下精确信息来门禁运行：

> 预计成本：典型运行（包含截图增强和 Seedance 视频）约 3,000-4,000 信用点（约 $30-$40）。这超过了 $5，请回复 `proceed` 继续或 `cancel` 停止。

在用户回复 `proceed` 之前，不要调用任何付费 MCP 工具。如果用户回复 `cancel`，则停止生成。对于非交互式 `--quick` 或 `--config` 调用者，需要在配置中要求 `cost_ack=proceed`；如果缺失，则停止并给出估计，而不是花费信用点。

**生成合同：** 使用 `resolution="1080p"`，`duration=15`，以及 `sound=True`。跳过 `fast=true`，因为它会将 Seedance 限制在 720p。技能拥有时长和声音，用户只需提供应用标识、界面截图、标志和宽高比。

视觉效果是从**应用的个性**中提取的——不是默认为流光玻璃效果。代理从应用的图标、截图和类别中读取应用的灵魂，然后选择处理方式。用户提供应用标识和资源；代理决定其他所有事情（模式、提示、相机、风格）。

---

## 生成前时钟计时器保护

在技能启动时，一旦所需的应用标识和界面/标志来源可用，并且成本门禁已通过，就启动一个计时器。等待用户 `proceed` 回复或非交互式 `cost_ack=proceed` 所花费的时间不计入准备时间，并且不得触发此门禁。如果所需输入或真实资源缺失，则在 Stage 0 或 Stage 0.5 停止并要求提供；不要绕过资源门禁。对于已持有所需输入的运行，第一个付费生成调用是 GPT-image-2 的 `generate_image_edit` 增强传递，必须在技能启动后的 5 分钟内调用。如果你在技能启动后的 5 分钟内没有调用第一个 `generate_image_edit` 增强传递，则在任何付费生成调用之前停止，并报告 `failed_pre_generation_timeout` 以及你目前拥有的内容：获取的资源、选定的界面、特征图、弧线、增强提示状态、如果有的话 Seedance 提示草稿以及确切的障碍。不要继续细化分析、增强措辞、提示措辞或相机语言。

在每次准备阶段之后，并在付费生成调用之前打印单行进度检查点：
- `Stage 1/3 done — assets sourced and screened, analyzing screenshots.`
- `Stage 2/3 done — feature map and arc written, locking enhancement prompts.`
- `Stage 3/3 done — enhancement prompts locked, calling GPT-image-2 now.`

特征图和增强提示的编写在第一次 `generate_image_edit` 调用之前最多进行 2 次。在最多 2 次之后，将你拥有的内容发送到 `generate_image_edit`；不要继续润色增强措辞、界面分析或弧线语言。Seedance 提示的编写在增强完成后最多进行 2 次；然后，将你拥有的内容发送到 `generate_reference_video`。

## 长任务 `task_status` 投票

当任何长运行生成或编辑调用返回带有或没有初始状态的 `task_id` 时，包括 `{task_id}`，`{task_id, status: "queued"}` 或初始 `queued`，`running` 或 `processing` 状态，立即记录任务 ID 和启动时间。

- 在一个紧密的循环中调用 `task_status({task_id})`，直到终端 (`completed | failed | cancelled`)。不要手动睡眠和不要使用 Bash 投票；工作进程保持每个状态调用打开。
- 在状态为 `queued`，`running` 或 `processing` 时，每 60 秒发出一条可见的进度行：`Seedance i2v queued for {N}m {S}s... still processing`。在轮询 Kling、GPT-image-2、叠加或编辑任务时，替换提供者/阶段标签。
- 在 `completed` 时，解包返回的结果 URL 并继续。
- 在 `failed` 或 `cancelled` 时，向用户展示失败，包括 `task_id`，状态和最后的状态消息。
- 在原始提交后的 15 分钟内，如果任务仍然非终端，则调用 `task_cancel({task_id})`，然后向用户展示失败。如果取消报告任务已经终端，则调用状态一次并报告终端结果。
- 在原始任务仍然为 `queued`，`running` 或 `processing` 时，不要提交重复请求。

## 模式：参考到视频

主要：`generate_reference_video(provider="seedance", resolution="1080p")` 使用 3-5 张截图 + 应用图标/标志作为最终参考。

当以下情况时，回退到 `provider="kling", quality_mode="pro"`（= 1080p）：
- Seedance 返回非音频 `partner_validation_failed`（名人面孔、屏幕录制 UI）
- Seedance 返回 `insufficient_balance`
- Seedance 保持排队/运行，直到返回超时，例如 `seedance timed out after ...`

不要将生成的音频审核视为立即 Kling 回退。请参阅 Generate Video 首先的 Seedance 生成的音频审核恢复运行手册。

Kling 提示使用 `<<<image_1>>>` … `<<<image_5>>>` 令牌，而不是 `@Image1` … `@Image5`。丢弃 `resolution` 参数（Kling 使用 `quality_mode` 代替）。参见 Gotchas。

---

## Stage 0 — 资源获取

如果使用空参数且没有相关先验上下文，则打印此菜单原文并停止。在用户提供应用标识和界面来源之前，不要调用任何工具。

```
要制作您的应用预告片，我需要：

1. 应用名称 + 一行描述其用途
   （例如 "Nova — 一个用于 iOS 的 AI 日记应用"）

2. 我应该从哪里获取应用界面？
   — iOS App Store：给我 App Store URL 或应用名称 → 我将使用
     `fetch_appstore_screens` 来获取截图、元数据和图标
   — 网页应用 / 网站：给我 URL → 我将使用 Pika MCP 捕获它
   — 本地文件 / URL：粘贴路径，我将上传它们

3. 品牌标志 — 路径或 URL（首选）或跳过以使用 App Store 图标
   标志锚定结束卡片，防止 Seedance 凭空捏造品牌文本。
   如果您没有标志文件，请使用获取的 App Store 图标作为后备。

4. 宽高比：16:9（横向/YouTube） / 9:16（Reels/TikTok） / 1:1. 可选：`variants=16:9,9:16,1:1` 以从一个渲染中导出多个交付物。
```

如果触发消息或先验上下文已经提供了部分内容，则在触摸任何工具之前，仅要求提供缺失的必要字段。这是用户唯一需要回答的问题；代理决定模式、提示、相机和风格。

回答后，代理：
1. 获取界面（MCP App Store 获取 / 网站捕获 / 上传本地文件）
2. **分析每个界面**（Stage 1）— 读取每个截图，映射 UI → 特征
3. **设计叙事弧线**（Stage 2）— 在触摸提示模板之前构建 15 秒的故事结构
4. 选择 3-5 张最佳界面用于预告片（按叙事角色排序）
5. 上传标志 + 界面以获取公共 URL
6. 编写特定界面的提示（模板 A 或 B）
7. 1080p 生成

---

## Stage 0.5 — 资源门禁

在调用任何生成工具之前，验证两个资源都在手：

| 资源 | 需要 | 如果缺失 |
|-------|----------|------------|
| 真实应用截图（≥1 实际获取的图像） | 是 | 停止并要求截图 |
| 品牌标志或应用图标 | 是 | 使用 `fetch_appstore_screens` 图标（当使用 App Store 获取时）；否则停止并要求标志/图标 |

如果其中任何一个缺失，请明确告诉用户需要什么，并等待。真实资源使预告片保持真实；文本到视频占位符使 Seedance 凭空捏造 UI。

避免：
- 使用文本到视频作为预期界面的替代
- 在提示中描述想象中的 UI（“一个深色控制面板...”）而没有真实的参考图像
- “我现在使用占位符”
- 根据名称或描述编造应用外观

向前唯一可接受的路径是用户提供的真实资源。如果 MCP 获取或捕获失败（App Store 返回空，网站截图出错），报告发生了什么并要求用户手动提供界面。永远不要编造它们。

### 人形/角色资源探测

应用截图和应用图标是唯一的默认视觉锚点。App-sizzle 不是创始人/创作者面孔技能，因此缺少屏幕或标志永远不会用用户头像填充。

在任何付费 `generate_image_edit` 或 `generate_reference_video` 调用之前，仅在用户提供的屏幕、标志、预告片图像、吉祥物、创始人照片或角色资源中包含一个突出的个人或角色，该个人或角色将成为增强或视频参考时，运行此 Avatar-type 探测。对于普通的带有偶然面孔的界面，请选择另一个截图或在上传之前裁剪面孔。

对资源调用一次 `analyze_media`：

```
query: "为付费视频生成对图像进行分类。这是一张真实人脸的照片、一个 AI 生成的逼真肖像、一个风格化的/插画的角色，还是一个可识别的商标/版权角色，例如蝙蝠侠、皮卡丘或米老鼠？仅返回严格的 JSON：{ \"avatar_type\": \"real_human\" | \"ai_realistic\" | \"stylized_illustrated\" | \"recognized_ip\", \"recognized_character\": string | null, \"moderation_risk\": \"low\" | \"medium\" | \"high\", \"recommendation\": \"proceed\" | \"warn\" | \"reject\" }。当没有识别特定角色时，使用 null for `recognized_character`；永远不要在 `recognized_character` 字段中写 \"none\"、\"unknown\" 或解释性文字。"
```

根据结果路由：
- **识别的 IP / 版权风险** -> **仅当** `avatar_type` 为 `"recognized_ip"`，或 `recognized_character` 指定一个特定角色（例如 `"Batman"`），或当 `moderation_risk` 为 `"high"` 且 `recommendation` 为 `"reject"` 时停止。将 `recognized_character: null`、空字符串、`"none"`、`"unknown"`、`"n/a"` 和低/中 `moderation_risk` 视为单独不足以停止。在真实/风格化路线之前运行此检查。即使 `avatar_type` 是风格化/插画，chibi 蝙蝠侠仍然是蝙蝠侠。
- **真实人类 / AI 生成的逼真** -> 仅当这是合法的应用截图或用户提供的预告片资源时才继续；否则要求应用 UI。
- **风格化/插画** -> 继续并发出可见警告，风格化角色可能会降低 Seedance 的可靠性，但不要用它们替代缺失的屏幕。
- **商标/版权** -> **停止** 在生成之前。展示此消息：`提供的头像似乎是商标角色 ([X])。大多数视频提供者将进行审核并拒绝生成。传递 --avatar <真实照片 URL> 来覆盖。` 对于 app-sizzle，要求非 IP 应用截图/标志，而不是使用头像覆盖作为屏幕替代。

---

## 界面获取

### iOS App Store

使用 Pika MCP `fetch_appstore_screens`；不要使用本地爬虫。它接受完整的 App Store URL、数字应用 ID 或应用名称搜索词：

```
fetch_appstore_screens(
  query: <app_store_url | numeric_app_id | search_term>,
  country: "us",
  max_screens: 10,
  include_icon: true
)
```

预期结果形状：

```
{
  "app_url": "https://apps.apple.com/...",
  "metadata": { "name": "...", "subtitle": "...", "description": "...", "category": "...", "icon_url": "https://..." },
  "icon": { "url": "https://cdn.pika.art/...", "source_url": "https://is...mzstatic.com/...", "filename": "appstore-icon.png", "mime_type": "image/png", "width": 1024, "height": 1024 },
  "screenshots": [
    { "url": "https://cdn.pika.art/...", "source_url": "https://is...mzstatic.com/.../1290x2796bb.png", "filename": "appstore-screen-01.png", "mime_type": "image/png", "width": 1290, "height": 2796 }
  ],
  "count": 1
}
```

如果 `fetch_appstore_screens` 返回没有截图，报告错误并要求用户提供 3-5 张真实截图加上标志/图标。不要回退到 Playwright/headless App Store 捕获，也不要编造 UI。

在 App Store 资源获取后，选择显示核心 UI 的 3-5 张截图。跳过：
- 纯文本/启动屏幕（没有 UI）
- 空白或加载状态
- 包含面孔的屏幕（可能会触发内容政策）

**界面选择原则——最大化视觉对比。** 每个选定的屏幕应该尽可能与其他屏幕不同：深色背景与浅色背景、UI 密集与照片密集、微距特写与宽网格、极简与繁忙。如果你的所有屏幕看起来都相似，Seedance 将它们混合成视觉上的浆糊。Dazz Cam 成功的原因：3D 相机网格 + Polaroid 输出 + VHS 面板 + 鱼眼球——四个完全不同的视觉世界。预告片失败的原因：四个相同 UI 的屏幕，仅在稍微不同的滚动位置。

### 网页应用 / 网站（自动捕获）

使用 Pika MCP 的捕获工具：

```python
capture_website(url="https://example.com", mode="screenshot")
# 返回 image_url — 直接使用作为参考
```

对每个要包含的独立页面/视图调用一次。

### 本地文件

用户提供路径 → 通过 Pika MCP 上传每个（见下文资源上传部分）。

---

## Stage 1 — 应用分析

在获取界面后，使用 Claude 的视觉功能**读取每个截图**，在编写任何提示之前。这是最重要的步骤——跳过它，你将得到一个没有故事的通用玻璃球。

对于每个截图，记录：
- **显示的 UI 是什么** — 例如 "聊天输入带有建议提示"，"视频时间轴带有 AI 编辑芯片"，"代理结果卡片显示一个生成的片段"
- **它代表什么功能** — 例如 "创建条目"，"代理在工作"，"输出/分享"
- **情绪基调** — 这是力量时刻、轻松时刻还是啊哈时刻？

还从 `fetch_appstore_screens` 结果或用户提供的描述中获取应用元数据：
- 应用名称、副标题、一行价值主张
- 类别和目标用户

**Stage 1 的输出：** 一个编号的特征图：
```
Screen 1 — [filename]: 显示 [X UI]。代表 [Y 功能]。时刻：[hook/build/reveal]。
Screen 2 — [filename]: ...
...
```

特征图之后，为每个屏幕评分**视觉独特性**：它看起来是否与其他映射的屏幕完全不同？优先选择具有不同调色板、不同布局密度和不同主题的屏幕。一个优秀的集合具有最大化的视觉跨度——钩子应该感觉与构建完全不同，构建应该感觉与揭示完全不同。

在编写出此图之前，不要继续到 Stage 2。

---

## Stage 2 — 叙事架构

每个 15 秒的预告片都需要一个骨干。在触摸提示模板之前设计故事弧线。

### 四节拍结构

| 节拍 | 秒数 | 工作 | 哪些屏幕 |
|------|---------|-----|-----------------|
| **钩子** | 0–3s | 抓住注意力 — 显示最戏剧性的 UI 时刻或解决的问题 | 最具视觉冲击力的屏幕 |
| **构建** | 3–10s | 功能演示，按逻辑用户旅程顺序 | 2-3 张连续的屏幕 |
| **揭示** | 10–13s | 拉回或产品概览——"这就是它做什么"的时刻 | 广角或最完整的屏幕 |
| **标志** | 13–15s | 品牌锁定——标志出现，强调色脉冲 | 标志 (@Image6 或最后一个参考)。`COMING SOON` 后来作为后生成文本叠加添加。 |

### 叙事弧线类型——根据应用选择一个

| 弧线 | 使用时机 | 结构 |
|-----|------------|-----------|
| **问题 → 解决方案** | 产品性/工具应用 | 钩子 = 痛点 UI → 构建 = 应用解决它 → 揭示 = 结果 |
| **功能展示** | 功能丰富的应用 | 钩子 = 最令人印象深刻的功能 → 构建 = 2 个更多功能 → 揭示 = 概览 |
| **旅程** | 消费者/生活方式应用 | 钩子 = 入口 → 构建 = 体验 → 揭示 = 结果 |
| **转换** | 前后类型应用 | 钩子 = "之前" → 构建 = 过程 → 揭示 = "之后" |

### Stage 2 的输出

在生成之前，明确写出弧线：
```
弧线类型：[问题→解决方案 / 功能展示 / 旅程 / 转变]
钩子（0-3秒）：屏幕[N] — [发生什么] — 摄像机：[对X的极端特写]
构建（3-10秒）：屏幕[N] → [N] → [N] — [每个揭示的内容] — 摄像机：[甩动/轨道/等]
揭示（10-13秒）：屏幕[N] — [它展示的内容] — 摄像机：[拉远以显示完整产品]
标志（13-15秒）：@Image[N] — 文字标志在[强调色]光束中整体出现并保持。不要要求视频模型渲染`即将推出`的文本；它稍后作为生成后的文本叠加层添加。
```

在定义弧线之前，不要写出Seedance提示。

---

## 第二阶段.5 — GPT-Image-2增强

在定义弧线并选择3-5个屏幕后，使用GPT-image-2在上传到Seedance之前增强每个屏幕。这可以将压缩的网站捕获和App Store缩略图提升到更干净、更高保真度的参考。

对于每个选定的屏幕（包括标志/结束卡参考）：

```python
result = generate_image_edit(
    provider="gpt-image-2",
    prompt="高质量版本，保留所有内容完全",
    images=["<原始cdn_url>"],
    aspect_ratio="16:9",   # 匹配捕获 — 竖屏屏幕使用9:16
    quality="medium",
)
# 使用result.image_url（或result.url）作为Seedance参考
```

**规则：**
- 保持提示完全不变 — 简短、非描述性。描述图像内容会使GPT-image-2产生幻觉。
- 匹配`aspect_ratio`到原始捕获（桌面=16:9，移动=9:16）。
- 并行运行所有增强（每个屏幕一个调用）。
- 使用增强的URL作为Seedance调用中的`reference_images`数组 — 不是原始的。
- 保持你的第一阶段功能图描述不变 — 它们描述原始内容，增强图像保留这些内容。

---

## 第三阶段 — 提示编写

手持功能图（第一阶段）和弧线（第二阶段），编写Seedance提示。每个`@Image`描述必须参考功能图中的真实UI内容 — 永远不要写像“一个带控制的移动界面”这样的通用描述。

根据应用截图选择模板；不要默认使用液态玻璃。根据应用的个性阅读其中之一；另一个不会加载：

- **模板A — 电影叙事**（默认；生产力、AI、创意、社交、食品、游戏）：阅读`references/template-a-cinematic.md`。经过验证的BEAT结构模板加上已验证的示例。
- **模板B — 液态玻璃**（仅限摄影、相机、滤镜应用，其中镜头/滤镜隐喻适用）：阅读`references/liquid-glass.md`。模板B骨架加上玻璃转换词汇。

强调色始终来自品牌 — 阅读图标和主要UI颜色，永远不要凭空发明一个。

### 两个模板的规则

- 每个`@Image`描述直接来自第一阶段功能图
- 摄像机方向直接来自第二阶段弧线
- 永远不要写“应用界面”或“移动屏幕” — 要具体
- 保持少于200字
- **为什么具体性很重要：** Seedance使用`@ImageN`描述作为其主要简报 — “一个深色聊天界面”与“一个VHS三面板网格的城市街道、滑板公园和带有复古时间戳覆盖的沿海日落”会产生完全不同的结果。从你的第一阶段功能图中逐字复制最具体的视觉细节。

---

## 生成视频

**主要 — Seedance:**
```python
generate_reference_video(
    provider="seedance",
    reference_images=["<url1>", "<url2>", "<url3>", "<url4>", "<url5>"],  # 3-5个屏幕+图标
    prompt="<使用@Image1 … @Image5标记的提示>",
    resolution="1080p",   # 总是
    duration=15,          # 总是
    sound=True,           # 总是
    aspect_ratio="16:9",  # 或 9:16 / 1:1 按用户请求
    seed=<int>,           # 设置一个；为内容策略恢复重复使用它
)
```

### Seedance生成音频审核恢复

如果Seedance完成生成然后返回一个422，其正文包括`type: "content_policy_violation"`，`reason: "partner_validation_failed"`，`loc: ["body", "generated_video"]`，和`msg: "Output audio has sensitive content."`，将其视为可恢复的生成音频审核误报。

重试预算：生成音频恢复最多在原始失败的Seedance调用后获得3次恢复渲染：一个`sound=False`探测，一个`sound=True`重播，和一个Kling回退。超出此上限后，停止或按文档记录精确路由成功的静音URL；不要继续探测Seedance。

1. 使用相同的提示和`reference_images`，`sound=False`和相同的`seed`重试。
2. 如果静音探测成功，使用相同的提示/参考集，`sound=True`和相同的种子重试。
3. 如果`sound=True`重播成功，将恢复的声音URL路由到第四阶段作为`generated_teaser_url`。将静音探测URL仅作为调试上下文保留。
4. 如果静音探测失败，将其视为视频/参考审核失败，并使用Kling回退。
5. 如果静音探测成功但`sound=True`重播再次失败，运行Kling回退一次。如果Kling不可用，将静音URL路由到第四阶段作为`generated_teaser_url`，并明确指出生成音频审核仍然不稳定。

在此恢复路径中不要更改提示、参考、宽高比、持续时间或种子。更改任何内容都会将静音探测变成一个新的生成，而不是测试是否只有生成音频触发了审核。

### Seedance超时恢复

如果Seedance在15分钟的总轮询上限之前返回终端超时，将其视为提供者队列饱和，而不是提示/内容失败。不要等待提供者超时字符串，例如`seedance timed out after 900s`或`seedance timed out after 1200s`。

当这种情况发生时，使用相同的选定参考、相同的节拍结构、`duration=15`、`sound=True`和`quality_mode="pro"`运行Kling回退。

在15分钟总时间内，按照上述轮询合同：取消非终端任务并显示失败，而不是在原始可能仍然活跃时开始回退。

在超时后不要重试Seedance，除非用户明确要求等待Seedance。超时路径已经花费了启动演示的时钟预算；切换提供者是记录的恢复。

**回退 — Kling（非音频partner_validation_failed或余额不足）：**
```python
generate_reference_video(
    provider="kling",
    reference_images=["<url1>", "<url2>", "<url3>", "<url4>", "<url5>"],
    prompt="<使用<<<image_1>>> … <<<image_5>>>标记的提示>",
    quality_mode="pro",   # = 1080p on Kling (NOT resolution=)
    duration=15,
    sound=True,
    aspect_ratio="16:9",
)
```

**Seedance标记：** `@Image1` … `@Image5` | **Kling标记：** `<<<image_1>>>` … `<<<image_5>>>`

Seedance约束：跳过`fast=True`因为它在720p上封顶；跳过`negative_prompt`因为Seedance拒绝它；跳过`auto_duration`因为此路径固定为15秒。

Kling约束：使用`quality_mode="pro"`获取1080p；Kling拒绝`resolution=`。

### Kling排队/交接恢复

Kling回退是异步的。如果`generate_reference_video(provider="kling")`返回`task_id`，使用上述长轮询合同使用`task_status`直到它达到终端状态。

如果`task_status`返回状态：`queued`且`statusMessage`包含`Worker handoff: task was requeued for retry on another worker.`，将其视为工作器重启交接，而不是渲染失败。继续轮询`task_status(task_id)`；下一个工作器应该重新获取相同的任务。

如果`statusMessage`以`Kling is at capacity`开头，将其视为提供者容量等待。继续轮询相同任务，同时`lastUpdatedAt`继续移动并且任务仍在15分钟总上限内。

在原始任务仍然`queued`或`running`时不要提交重复的Kling请求。重复会消耗提供者配额并使工件来源不明确。

如果`status`保持`queued`超过10分钟且没有`lastUpdatedAt`移动，捕获`task_id`、`status`、`statusMessage`和`lastUpdatedAt`，然后继续相同的任务直到15分钟总上限。在15分钟总时间内，使用`task_cancel({task_id})`取消停滞的原始任务并显示失败。不要从此路径重试新的Kling请求；切换提供者或支付调用后重新提交会带来重复支出和不清晰的工件来源。

---

## 资产上传（本地文件→公共URL）

如果用户提供本地文件路径，在调用生成之前将它们转换为公共URL：

1. 读取文件大小和MIME类型。
2. 调用`upload_asset(filename, mime_type, size_bytes)`。
3. 使用返回的`presigned_url`通过主机客户端的文件上传功能上传字节。
4. 使用返回的`public_url`作为生成调用中的参考URL。

支持的MIME类型：`image/png`，`image/jpeg`，`image/webp`，`video/mp4`，`audio/mpeg`，`audio/wav`

---

## 第四阶段 — 确定性即将推出叠加层

不要要求Seedance或Kling渲染`即将推出`。视频模型会混淆新的排版，尤其是全部大写的CTA文本，所以最后两秒使用确定性`即将推出`叠加层作为生成后的文本叠加层。

在Seedance或Kling返回15秒预告URL后，调用：

```python
edit_text_overlay(
    video_url=<generated_teaser_url>,
    text="即将推出",
    position="底部居中",
    font_size=56,
    font_color="白色",
    start_s=13,
    end_s=15,
)
```

如果`edit_text_overlay`返回`{ task_id }`，轮询`task_status`直到它达到`completed`、`failed`或`cancelled`，然后解包返回的URL。将返回的URL保存为`final_url`。如果叠加层调用失败，显示该失败和未叠加的预告URL作为诊断预览；不要交付只有由视频模型生成的`即将推出`文本的预告。

---

## 宽高比变体

当用户想要为YouTube、Reels/TikTok和方形信息流生成相同的应用预告，而无需支付单独生成时，使用可选`variants=16:9,9:16,1:1`。保持遗留`aspect=`作为单输出缩写；当`variants`存在时，使用原生`16:9`作为源宽高比，除非用户明确请求仅一个变体。

一次调用`generate_reference_video`生成原生`16:9`预告，然后运行第四阶段一次以产生`final_url`。不要重新运行截图来源、GPT-image-2增强、Seedance/Kling生成或任何其他昂贵提供者调用以生成额外变体。

在`final_url`存在后，构建一个扁平的`variant_urls`对象：

```json
{
  "16:9": "<final_url>",
  "9:16": "<edit_reframe url>",
  "1:1": "<edit_reframe url>"
}
```

- 对于`16:9`，设置`variant_urls["16:9"] = final_url`。
- 对于`9:16`和`1:1`，调用`edit_reframe(video_url=final_url, target_aspect="<aspect>", fill_mode="blur")`，使完整的预告在模糊背景上保持可见，而不是被中心裁剪。
- 将`edit_reframe`视为廉价的最终合成/重帧阶段。如果重帧失败，返回成功的变体URL加上失败的宽高比和工具错误；不要重新提交昂贵的生成。

> **注意 — 变体使用模糊填充。** `9:16`和`1:1`保持完整的原生`16:9`预告在模糊背景上可见。为了可读性，将关键主题（产品、标志、标题）居中，但不要将这些输出描述为裁剪变体。

## 飞行后质量门

在声明成功之前，对`final_url`调用`analyze_media`并要求结构化裁决。如果`variants`被请求，对每个`variant_urls`值和键运行相同的门，并按宽高比警告任何警告。

```
仅返回JSON：{
  "verdict": "clean" | "degraded" | "catastrophic",
  "observations": string[],
  "quality_warning": string | null,
  "re_roll_suggestion": string | null
}
检查COMING SOON是否可见且拼写正确在最终叠加层、品牌颜色是否存在、应用屏幕/产品屏幕是否可读，以及没有黑帧或错误产品镜头。
```

- 如果`verdict`是`clean`，正常返回最终URL。
- 如果`verdict`是`degraded`，返回最终URL加上`quality_warning`，以便用户在发布前查看。
- 如果`verdict`是`catastrophic`，不要调用运行完成；显示verdict和`re_roll_suggestion`而不是声明成功。

## 结果交付

将最终Pika CDN URL作为主要交付物。如果`variants`被请求，在同一响应中返回扁平的`variant_urls`对象。如果主机客户端需要本地媒体标记，在确认CDN URL可达后在此技能流程外创建该本地预览。

**如果生成完成异步：** 跟随MCP工具返回的状态处理程序，直到视频达到终端状态，然后交付最终URL。

---

## 提示指南

> **提示是第一阶段+第二阶段的输出，不是起点。** 从想象中填写模板 — 从你构建的功能图和弧线中填写。没有第一阶段分析的提示将产生一个通用的玻璃块。

### 摄像机词汇

使用具体的摄像机语言 — Seedance对此做出响应：

| 术语 | 效果 |
|------|------|
| `极端微距特写[特定元素]` | 拉近距离拍摄 — 玻璃边缘、按钮、图标 |
| `撞击式对[元素]进行变焦` | 快速推入，创造能量 |
| `甩动到` | 硬横向切换，带有运动模糊 |
| `围绕[元素]进行轨道式摆动` | 360°弧线绕浮动面板 |
| `推入漂移` | 慢速、电影般的推镜头 |
| `拉远以显示` | 经典产品揭示 — 显示完整形状 |
| `硬切到黑` | 清洁的节拍 |

交替快速剪辑与慢速漂移 — 纯快速剪辑感觉混乱，纯慢速漂移感觉无聊。

（玻璃转换词汇在`references/liquid-glass.md`中 — 仅在模板B路径中相关。）

### 设备构图

对于产品拍摄，将设备锁定到黑色虚空 — 永远不要放置在环境中：

```
# 漂浮的桌面屏幕（SaaS / 桌面应用）
在纯黑色背景下以3D空间中漂浮的桌面屏幕，倾斜如MacBook产品拍摄。屏幕上的UI元素变成带反射和折射的半透明玻璃。没有文本、没有标志、没有字。
# iPad揭示
一个iPad Pro在空黑色空间中漂浮，以电影般的倾斜角度，如苹果产品拍摄。iPad是一个真实的固体设备，有可见的边框 — 只有屏幕内容有玻璃效果。设备缓慢旋转。没有文本、没有标志。
# MacBook
一个MacBook Pro在空黑色空间中漂浮，以电影般的倾斜角度打开。屏幕显示[内容]。光线捕捉到铝制边缘。没有文本、没有标志。
```

### 参考计数指南

所有运行都是15秒，1080p。根据叙事弧线选择3-5个屏幕。

| Refs | 用途 |
|------|------|
| **3** | 标准 — 每个节拍一个屏幕（钩子/构建/揭示）+ 图标作为@Image4 |
| **4** | 两个构建节拍 + 钩子 + 图标 |
| **5** | 功能丰富 — 钩子 + 三个构建节拍 + 图标。不要超过5。 |

**黄金规则：1个参考对应~3秒视频。**

---

## 承重短语

这些短语是经验性的提示/流程锚点。在简化技能时保持它们：

| 术语 | 位置 | 为什么需要承重 |
|---|---|---|
| `高质量版本，保留所有内容完全一致` | GPT-image-2 增强传递 | 在清理压缩伪影时，保持增强传递不凭空创造 UI。 |
| `在此弧定义之前，不要编写 Seedance 提示` | 阶段 2.5 门控 | 防止与所选屏幕不相关的通用运动提示。 |
| `提示是阶段 1 + 2 的输出，而不是起点` | 提示指南 | 强制代理使用屏幕特征图和故事弧，而不是从想象中填充模板。 |
| `纯黑色背景` / `悬浮在空旷的黑色空间中` | 设备框架提示 | 使产品照片专注于应用 UI，而不是幻觉环境。 |
| `实体化整体` / `结晶为单一形态` / `作为完整元素淡入` | Logo 揭示措辞 | 避免逐字母 Logo 构建，这会导致品牌文本混乱。 |

---

## 运行时预期

典型运行时间为 4-8 分钟。所有在第一个付费 `generate_image_edit` 增强调用之前的预生成阶段必须适应上述 5 分钟的警戒时间。如果它们不适应，请停止并报告部分准备，而不是继续。

| 步骤 | 墙上时钟 | 备注 |
|---|---:|---|
| 资产获取 | 10-60 秒 | 通过 `fetch_appstore_screens` 从 App Store 获取；网站捕获取决于页面加载 |
| 屏幕分析 + 弧 | <=2 分钟 | 将此限制在最大 2 次提示/分析传递内 |
| GPT-image-2 增强 | 30-90 秒 | 仅在仍然在 5 分钟预生成警戒时间内并行运行所选屏幕 |
| Seedance 生成 | 3-5 分钟 | 生成的音频内容政策恢复添加一个静音探测和一个相同种子的声音重播 |
| Kling 备用 | 5-15 分钟 | 容量等待或工作手交可能暂时显示 `queued`；遵循 Kling 队列/手交恢复运行手册 |
| 下载验证 | <30 秒 | 交付前的本地合理性检查 |

## 引擎选择：Seedance 主要，Kling 备用

Seedance 是默认选项，因为它擅长处理抛光的运动图形参考和 1080p 应用预告片。Kling 是备用选项，用于内容政策、平衡或 Seedance 超时失败，因为它对某些屏幕内容更加宽容，并且对 1080p 使用 `quality_mode="pro"`。

## 失败模式

### 从 `generate_image_edit` / `generate_reference_video` / `upload_asset` 的上游 5xx 恢复

如果任何付费生成或资产 MCP 调用返回：
- `code: "provider_5xx"` AND `retry_class: "retry_after_backoff"`
- 或来自任何上游提供者（OpenAI、Seedance、Kling、存储）的 HTTP 502 / 503 / 504

执行以下操作：
1. 等待 5 秒。
2. 使用完全相同的参数重新调用相同的 MCP 工具。不要更改所选屏幕、提示文本、种子、`sound`、提供者、图像顺序或上传有效负载。
3. 如果重试也以 5xx 失败，请中止并向用户显示：“提供者两次返回了瞬态上游错误。1-2 分钟后重试；这通常会自行清除。”

不要重试超过一次。不要将 5xx 视为内容或内容政策问题；重写应用弧可能会消耗积分而不会解决停机问题。

### 从上游 4xx / `moderation_blocked` 恢复

如果 `generate_image_edit` 使用 `provider="gpt-image-2"` 返回上游 4xx 或 `moderation_blocked`，在增强屏幕截图时：
1. 不要重试相同的提示；内容政策和大多数 4xx 验证失败是确定性的。
2. 如果参考在没有增强的情况下仍然有效，请跳过增强并使用原始屏幕。如果质量太低，请尝试一次备用提供者进行增强；不要更改所选的应用屏幕或 Seedance 提示。
3. 如果备用提供者也失败，请向用户显示：“图像提供者拒绝了此屏幕截图增强提示。提供更清晰的屏幕截图、裁剪面部/录制 UI，或继续使用原始屏幕。”

对于 Seedance 非音频内容政策失败，请使用以下文档中的 Kling 备用选项；这是此技能的视频备用提供者路径。

### 从上游 429（速率限制）恢复

如果任何上游返回带有回退提示的 HTTP 429：
1. 等待提示的回退时间，如果没有提示则等待 30 秒。
2. 使用完全相同的参数重新调用相同的 MCP 工具。
3. 不要重试超过一次。如果它仍然返回 429，请中止并显示速率限制消息，而不是提交重复的付费渲染。

### `capture_website` 返回空 / 页面未加载

如果网站模式调用 `capture_website` 并返回 200，但 `action_bboxes` 为空或 `recording_viewport` 为 0x0：
1. 不要重试；网站在捕获环境中未能加载。
2. 显示：“无法捕获 <url>。页面可能被阻止 / 收费墙 / 需要认证。请提供 3-5 张屏幕截图和 Logo/图标。”

### `upload_asset` 网络 / 认证失败

如果 `upload_asset` 在将本地屏幕、Logo 或覆盖层转换为托管 URL 时失败，请不要继续使用 `reference_images` 或 HTML 中的本地路径。仅对上述 5xx 或 429 类别重试一次。对于 `auth_error`、不支持的 MIME、网络故障或重复上传失败，请停止并要求托管 PNG/JPEG/WebP 资产。

### 长运行的 `task_status` 超出上限

每个异步 MCP 调用返回要么是内联结果，要么是 `{task_id, status}` 用于轮询。在使用这些上限之前，在决定任务卡住之前使用：
- Seedance i2v：每调用 10 分钟
- Kling 备用：每调用 15 分钟
- gpt-image-2 高质量：每调用 3 分钟
- 上传/编辑/渲染助手：每调用 5 分钟

使用较早者：提供者的上限 x 1.5 或任何技能特定的硬轮询上限，包括上述 15 分钟总轮询合同中的上限。如果 `task_status` 返回 `status: "processing"` 或 `status: "queued"` 超过该较早限制，请调用 `task_cancel({task_id})` 并显示：“提供者运行时间异常；中止。重试。”

| 症状 | 原因 | 修复 |
|---|---|---|
| `fast=True` 与 `resolution="1080p"` | Seedance 快速模式上限为 720p | 移除 `fast`；保持 `resolution="1080p"` |
| `negative_prompt` 被拒绝 | Seedance 不接受此字段 | 使用正面表述，例如“平滑运动，稳定相机” |
| Seedance 生成的音频内容政策：`content_policy_violation` / `partner_validation_failed`，`generated_video`，“输出音频包含敏感内容。” | 通常对非敏感的应用预告片参考是误报 | 遵循限制的生成音频恢复运行手册：相同种子 `sound=False` 探测，相同种子 `sound=True` 重播，然后最多一次 Kling 备用 |
| Seedance 超时，例如 `seedance timed out after ...` | 提供者队列饱和或尾部延迟超过了工具预算 | 运行 Kling 备用；除非用户明确要求等待，否则不要继续重试 Seedance |
| Seedance 在视频上的 `partner_validation_failed` | 屏幕内容包含录制 UI、名人面孔或类似的审核触发器 | 切换到 `provider="kling"` 并将标记转换为 `<<<image_N>>>` |
| 屏幕截图中的面孔触发内容政策 | 屏幕截图包含真人 | 上传前裁剪面孔，或使用 Kling |
| 6+ 参考图像降低质量 | 模型混合了过多的参考 | 保留 3-5 个参考，大致每 3 秒一个 |
| 提示尾部被忽略 | 提示超过约 200 个字 | 剪辑到节拍结构和具体的 UI 细节 |
| 输出中的文本混乱 | 视频模型被要求渲染新文本 | 保持文本为现有参考图像内容；在后期制作中覆盖任何新的品牌标识 |
| Logo 揭示幻觉字母形式 | “组装/构建/构造”语言触发逐字渲染 | 使用“实体化整体”、“结晶为单一形态”或“作为完整元素淡入” |
| 任务返回 `{ task_id }` 而不是内联 | 长运行生成超出了内联预算 | 遵循长运行轮询合同：轮询 `task_status({task_id})`，发出 60 秒的进度行，在 15 分钟总时间内取消/显示，并在完成时解包 `result.structuredContent` |
| Kling 任务返回状态：`queued` 在之前运行后 | 工作手交或提供者容量等待 | 遵循 Kling 队列/手交恢复运行手册和长运行轮询合同。不要提交重复；继续轮询，直到终止或 15 分钟总时间内取消/显示 |
| Kling 拒绝 `resolution=` | Kling 使用不同的质量旋钮 | 使用 `quality_mode="pro"` |
| App Store 图标 URL 指向促销艺术 | App Store 元数据备用找到功能艺术作品 | 优先使用 `fetch_appstore_screens` 返回的 `icon.url`；如果缺失，请要求提供 Logo/图标文件 |
