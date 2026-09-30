---
name: ugc-ads
description: 在用户要求ugc广告或任务与以下示例匹配时使用。多剪辑跳跃剪辑ugc产品广告——钩子+3跳跃剪辑+尾声，15秒，9:16竖屏（3:4可选，仅限seedance），第一人称视角自拍，每个节拍都有带有本地口型的对话，5幕叙事弧（设定→命名→揭示→转折→高潮）。六类精华（HAUL / APP / FOOD / BEAUTY / FITNESS / TECH）从输入URL自动选择。创作者风格原始ugc自拍，多节拍对话式对话。在用户要求“制作ugc广告”、“跳跃剪辑产品广告”、“第一人称产品展示”、“创作者风格广告”、“带货风格广告”、“开箱广告”、“抖音风格产品视频”或“关于[URL]的自拍广告”时使用。
---

# /pika:ugc-ads

## 参数

| 参数 | 默认值 | 备注 |
|---|---|---|
| `url` | 必填 | 产品 URL — 用于驱动类别检测和镜头替换 |
| `avatar_url` | 内置回退 | 人设肖像 URL；作为 `@Image1` 引用传入。如果省略，技能将使用预生成的皮克斯风格女性创作者肖像 |
| `provider` | `seedance` | seedance：擅长 UGC 自拍 / 讲头视角，具有原生唇形同步，单提示多镜头，支持 3:4。kling：需要显式 `shots[]`，仅支持 9:16/16:9 |
| `aspect_ratio` | `9:16` | `3:4` 仅限 seedance（kling 拒绝 3:4） |
| `variants` | 未设置 | 可选的逗号分隔列表，用于共享生成导出。支持：`9:16`，`16:9`，`1:1`。保持昂贵的 UGC 渲染共享，然后在最终阶段重新构图 |
| `category` | 自动 | `HAUL` / `APP` / `FOOD` / `BEAUTY` / `FITNESS` / `TECH`；从 URL 自动选择 |
| `captions` | `true` | TikTok 风格的词语块字幕，烧录在最终视频顶部 |

## 成本透明度门禁

在执行任何付费 MCP 调用之前，调用一次 `identity_balance({verbose: true})`。显示当前余额、近期消耗速率和剩余额度，然后用以下精确消息门禁运行：

> 预计成本：典型的 Seedance UGC 广告（含回退/重试预算）约 4,000 信用点（约 40 美元）。这超过了 5 美元，请回复 `proceed` 继续或 `cancel` 停止。

在用户回复 `proceed` 之前，不要调用任何付费 MCP 工具。如果用户回复 `cancel`，则不生成并停止。门禁在产品 URL 确定之后、头像分析、截图捕获、视频生成、字幕或付费重试之前运行。

## 运行时预期

典型端到端运行时间：**6–12 分钟**。分解：

- 第 1 步（WebFetch）+ 第 3 步（capture_website 截图）：~10–30s
- 第 7 步（`generate_reference_video`）：seedance 约 3–5 分钟，kling 约 5–7 分钟
- 第 7b/c 步（卡通化 + 重试）：如果 seedance 审核拒绝头像，增加 ~1–2 分钟
- 第 8 步（确定性品牌/规格叠加）：1-2 次 `edit_text_overlay` 调用，总计 ~30s–5 分钟
- 第 9 步（字幕）：单个 `add_captions` 调用，~30s–5 分钟（转录 + 一次性烧录）

如果运行超过 15 分钟没有进展，则有问题 — 检查工具报告的生成状态和错误消息。

## 生成前时钟墙

在技能启动后，一旦产品 URL 可用且成本门禁通过，启动计时器。等待用户 `proceed` 回复的时间不计入准备时间，且不得触发此门禁。第一个付费生成调用是 `generate_reference_video`，这是耗时最长的付费阶段，必须在技能启动后 5 分钟内调用。如果你在技能启动后 5 分钟内没有调用 `generate_reference_video`，则在任何付费生成调用之前停止，并报告 `failed_pre_generation_timeout` 以及你目前拥有的内容：抓取的产品事实、选择的类别、头像来源、截图状态、草稿对话和确切障碍。不要继续优化脚本措辞、提示基础或镜头顺序。

在每个准备阶段之后、在付费生成调用之前打印单行进度检查点：
- `Stage 1/3 done — product fetched and categorized.`
- `Stage 2/3 done — avatar and screenshot ready, composing dialogue.`
- `Stage 3/3 done — prompt locked, calling Seedance now.`

脚本和提示迭代最多 2 轮。在最多 2 轮之后，将你拥有的内容发送到 `generate_reference_video`；不要继续优化钩子、结尾或屏幕特写措辞。

## 长任务 `task_status` 投票

当任何长运行生成或编辑调用返回带有或没有初始状态的 `task_id`（包括 `{task_id}`，`{task_id, status: "queued"}` 或初始 `queued`，`running` 或 `processing` 状态），立即记录任务 ID 和启动时间。

- 在终端（`completed | failed | cancelled`）之前，在紧密循环中调用 `task_status({task_id})`。不要手动睡眠和不要 Bash 投票；工作进程会保持每个状态调用打开。
- 在状态为 `queued`，`running` 或 `processing` 时，每 60 秒发出一条可见进度行：`Seedance i2v queued for {N}m {S}s... still processing`。在轮询 Kling、GPT-image-2、字幕或编辑任务时，替换提供者/阶段标签。
- 在 `completed` 时，解包返回的结果 URL 并继续。
- 在 `failed` 或 `cancelled` 时，向用户显示失败，包括 `task_id`、状态和最后的状态消息。
- 从原始提交开始，15 分钟后如果任务仍非终端，调用 `task_cancel({task_id})`，然后向用户显示失败。如果取消报告任务已终端，再次调用状态一次并报告终端结果。
- 在原始任务仍为 `queued`，`running` 或 `processing` 时，不要提交重复请求。
- 异步投票预算：一个活动任务和一个 15 分钟投票窗口。在投票上限用尽后，取消任务并显示失败，而不是提交另一个付费渲染，除非后续步骤明确允许在原始任务终端后进行单独的受限制重试。

## 引擎选择：Seedance 默认，Kling 回退

对于 UGC 自拍/讲头广告默认使用 Seedance，因为它擅长原生唇形同步、单提示多镜头节奏和可选 3:4 输出。当调用者显式传递 `provider=kling`，或 Seedance 用尽卡通化重试上限后用户选择 Kling 时使用 Kling。Kling 的权衡是更严格的宽高比支持，但需要单独的审核路径和显式的镜头分割。

## 步骤

### 0. 解析输入（空参数菜单）

从 `$ARGUMENTS` 中剥离标志和 `key=value` 参数。如果产品 URL 不存在且先前上下文中没有可用的产品 URL，打印此菜单并停止：

> **应推广哪个产品？** 必填：
>
> - **产品 URL** — 用于抓取产品名称、类别、视觉参考和语言的页面
>
> 可选：`avatar_url=`，`provider=seedance|kling`，`aspect_ratio=9:16|3:4`，`variants=9:16,16:9,1:1`，`category=auto|HAUL|APP|FOOD|BEAUTY|FITNESS|TECH`，`captions=true|false`.

如果产品 URL 存在，则无声跳过此步骤。

### 1. 抓取 + 分类

`WebFetch` URL：拉取 `product_name`，`brand_name`，价值主张，品牌颜色，产品形式，包装，英雄文案，目标用户，类别，**以及页面的主要语言**。如果传递 `category=`；否则信任 WebFetch 信号；回退到 HAUL（物理），APP（数字）。

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

每个数值规格声明（`W`，`mAh`，`%`，分钟，端口，价格，尺寸，数量，充电速度，电池大小，排名）必须来自可见源页面文本并包含 `source_quote`。如果源页面没有明显支持数字，则将其排除在 `grounded_specs` 和 `claims_allowlist` 之外。不要从产品类别、型号名称、常识或竞争对手页面推断规格。

### 2. 解析头像（缺少时回退到内置）

- 如果传递了 `avatar_url` → 直接使用。
- 如果未传递 → 使用此内置回退：
  ```
  https://cdn.pika.art/v2/files/agent/17d62bf9-0edb-49e4-9ba9-2c5419fa518f/seedream-1777624057811.jpeg
  ```
  预生成的 3D 动画皮克斯风格年轻女性创作者肖像 — 预卡通化，因此 seedance 审核直接接受，足够中性以适应任何类别。在最终摘要中注明回退使用，以便调用者知道下次提供自己的肖像以保持人设一致性。

### 2.5 头像类型探测（创作者肖像）

在步骤 7 之前和任何付费 `generate_reference_video` 调用之前运行此探测。它适用于调用者提供的 `avatar_url`、内置回退或任何作为 `@Image1` 选择的创作者肖像。内置回退已经是非 IP 风格的创作者，但仍然在最终摘要中记录其来源。

调用一次 `analyze_media`：

```
query: "为付费视频生成分类此图像。它是真实人脸的照片、逼真的 AI 生成肖像、风格化/插画角色，还是像蝙蝠侠、皮卡丘或米奇这样的可识别的商标/版权角色？仅返回严格 JSON：{ \"avatar_type\": \"real_human\" | \"ai_realistic\" | \"stylized_illustrated\" | \"recognized_ip\"， \"recognized_character\": 字符串 | null， \"moderation_risk\": \"low\" | \"medium\" | \"high\"， \"recommendation\": \"proceed\" | \"warn\" | \"reject\" }。当未识别特定角色时，`recognized_character` 为 null；在字段中永远不要写 \"none\"、\"unknown\" 或解释性散文。"
```

根据结果路由：
- **识别的 IP / 版权风险** -> **仅当** `avatar_type` 为 `"recognized_ip"`，或 `recognized_character` 命名特定角色（例如 `"Batman"`），或当 `moderation_risk` 为 `"high"` 且 `recommendation` 为 `"reject"` 时才停止。将 `recognized_character: null`、空字符串、`"none"`、`"unknown"`、`"n/a"` 和低/中 `moderation_risk` 视为单独不足以停止。在真实/风格化路由之前运行此检查。即使 `avatar_type` 是风格化/插画，chibi 蝙蝠侠仍然是蝙蝠侠。
- **真实人类 / AI 生成逼真** -> 正常进行。
- **风格化/插画** -> 正常进行，但显示可见警告，说明风格化头像可能被 Kling 接受，但在 Seedance 审核下可能不一致；只有当用户提供或接受该头像时才继续。
- **商标/版权** -> **停止** 在生成之前。显示此消息：`头像似乎是商标角色 ([X])。大多数视频提供商会审核并拒绝生成。传递 avatar_url=<真实照片 URL> 覆盖。`

### 3. 捕获产品截图（尽力而为）

调用 `capture_website`，`mode: "screenshot"`。对于手持产品类别（APP / FITNESS / BEAUTY）使用 `mobile=true`，以便捕获的页面渲染为肖像手机屏幕；`mobile=false` 对于桌面上下文类别（HAUL / TECH / FOOD）。

如果调用失败（超时、浏览器池宕机），重试 **一次**。如果仍然失败，则不捕获截图 — 技能降级但功能正常。特写镜头然后仅通过文字描述页面。Beat 2 的 `reference_images` 只是 `[avatar_url]`。

捕获 URL → `screenshot_url`（或 null）。

### 4. 构作曲本

完整提示是一个传递给 **一个** `generate_reference_video` 调用的多镜头字符串。结构化散文（非 markdown 项目符号）。每个镜头都有一个 `Says: "..."` 行用于唇形同步。目标节奏为整个 15 秒广告约 5.5–6 个词/秒（≈85–90 个词）。`@Image1` 是头像，`@Image2` 是可用时截图。

**所有 `Says: "..."` 行都使用步骤 1 检测的语言编写。** Seedance 和 Kling 都处理多语言唇形同步；如果产品页面是中文/日语/西班牙语/等，对话应为该语言。步骤 5 的钩子原型是语言无关的 — 调整修辞动作以适应语言的自然语域。

**规格接地规则：** 禁止编造数字。任何说或视觉中的数字/单位声明必须逐字出现在 `claims_allowlist` 中。如果数字不在 `claims_allowlist` 中，则定性重写行（“充电快”，“多个端口”，“大电池”）或省略声明。不要说“28 分钟内 50%”，“3 个端口”，“140W”，价格，数量或时间窗口，除非该确切声明有源支持。

**品牌/规格文本渲染规则：** 不要要求 Seedance 或视频模型渲染品牌标志、产品标志、包装标签或规格文本。视频模型文本会变得混乱。提示可以显示 `@Image2` 作为参考，但任何必须可读的新品牌名称或规格副本都将在后续的确定性步骤 8 叠加中添加。

```
HOOK (0–3 秒) <视觉设置 + 创作者框架 + 面部/身体提示>。对镜头快速且充满活力地说：“<钩子行>”。<风格锚点 — 手持视角，真实，原始>。

JUMP CUT 1 (3–6 秒) <广角 POV — 创作者的身体语言，产品部分在边缘帧中>。<面部提示>，快速说：“<设置行>”。

JUMP CUT 2 (6–9 秒) <下一个视觉镜头 — 可以是显示 @Image2 的屏幕特写，也可以是另一个反应镜头，取决于对话弧将揭示放在哪个镜头上>。说（如果它是屏幕特写，则镜头上的声音继续），快速且自信地说：“<揭示行>”。

JUMP CUT 3 (9–12 秒) <下一个视觉镜头 — 同样逻辑；JUMP CUT 中一个是屏幕特写，其他是广角 POV 反应镜头>。快速说：“<洞察转折行>”。

OUTRO (12–15 秒) <自拍 POV，胸部中部构图，相同设置>。对镜头快速说：“<结尾行>”。

头像为图像 1，资产为图像 2
```

**屏幕特写镜头 — 广告中仅一个，位置由对话驱动：**
- 将屏幕特放在哪个 JUMP CUT（1、2 或 3）上，*揭示* 行落在上面。大多数广告将其放在 JUMP CUT 2 上；如果叙事需要在更早或更晚，JUMP CUT 1 或 JUMP CUT 3 也行。根据内容选择，而不是槽位编号。
- 屏幕特写镜头显示 `@Image2` 恰好如初，并包括一个指向手势（一根手指从帧边缘进入，指向英雄文本或产品 — 无点击、无滑动、无滚动、无 CTA 悬停）。点手势是整个广告中唯一的屏幕交互。
- 其他 JUMP CUT 是广角 POV 反应镜头：手放在膝盖、床上或两侧。

**信任 `@Image2`** — 当产品页面显示时，参考图像；不要用散文描述其 UI。描述 UI 会触发模型编造额外的面板/下拉菜单/侧边栏/动画。参考图像；信任它。

### 5. 类别本质

每个本质是你阅读的 5 镜头前的简报。从步骤 1 的类别中选择一个，并编写针对真实产品的实际 `Says: "..."` 行。

**类别数值门禁：** 类别原型是修辞/相机指导，不是编造日期、持续时间、数量、折扣、成本、评分、充电时间、端口数量、输出数字或紧迫性窗口的权限。任何数字短语必须重写，除非 `claims_allowlist` 中有匹配的数字。当 `claims_allowlist` 缺少匹配数字时，使用非数字语言，例如“使用后”、“在例行程序中”、“源支持规格”、“首发优惠”或“现在可用”。

#### HAUL_UNBOX
- **何时使用及原因**：时尚、手袋、珠宝、鞋履、设计师新品、街头潮流、奢侈化妆品（具有包装故事）、配饰——任何品牌包装与材质/纹理相结合才是价值主张的领域。观众通过虚拟开箱的快感能量（多巴胺）和“我刚拿到”的社会证明而转化；材质和五金才是顾客所支付的，因此特写镜头落在材料上，而非功能上。不是技术（→ TECH_UNBOX），也不是护肤/化妆应用（→ BEAUTY_APPLY）。
- **感官锚点**：纸巾摩擦声、布料滑动声、五金件碰撞声（链条/搭扣/扣环）、指尖下的皮革/布料纹理、金属箔光泽。
- **场景**：自然光下的未整理床铺；背景是浴室镜子，用于结尾时手持展示；街头潮流新品可能使用书桌/地板。
- **特写节奏点**：不是屏幕——产品特写。`@Image2` 是产品照片（或品牌网站手机视图）；单指指向五金细节（链条、搭扣、压印Logo）。
- **对话角色**：钩子是**神秘悬念**——将开箱包装成观众还不知道内容的神秘事物；不要在钩子句中提及产品名称。弧线：钩子悬念开箱 → 品牌名称+新品背景 → 特写五金时揭示材质/轮廓 → 触感/可穿戴性洞察（身体感受）→ 引导观众想象自己拥有这件物品的笑点。

#### APP_REVEAL
- **何时使用及原因**：SaaS、AI工具、移动/网页应用、代理式产品、开发工具、生产力工具——任何屏幕即产品的领域。观众在看到实时UI快速完成操作时转化；特写节奏点是演示，书签是社交证明。不是纯硬件（→ TECH_UNBOX）。
- **感官锚点**：微拇指手势、品牌色高亮、UI充满微小动画、环境房间音。
- **场景**：舒适的卧室或沙发视角；画面边缘是牛仔裤/运动裤；温暖的窗户光线。
- **特写节奏点**：床上的笔记本电脑（桌面截图）或手中的手机（手机截图——在步骤3中将`mobile=true`）。 
- **对话角色**：钩子是**困惑的好奇**——创作者还无法归类这个物品，这正是要点。不要在钩子中使用功能列表或营销语言；侧重于“我不知道该叫它什么”/“这太疯狂了”的基调，让观众等待名称。弧线：困惑钩子 → 人类语言中命名产品+交互模型 → 特写展示页面时揭示它产生的具体结果（逗号分隔的示例）→ 个人洞察转折（用户工作流程中它取代/改变的内容）→ 笑点+隐含/明确的“去试试”CTA。

#### FOOD_ASMR
- **何时使用及原因**：食品品牌、饮料、厨房工具、零食、提供外卖产品的餐厅——任何感官高峰（倾倒/滋滋声/蒸汽/第一口）承载价值主张的领域。观众通过饥饿反应转化——展示感官高峰，不要描述它。
- **感官锚点**：包装摩擦声、刀在板上的声音、滋滋声、倾倒水流、升腾的蒸汽、第一口满足的呼气。
- **场景**：大理石台面或温暖的原木厨房，俯视构图。
- **特写节奏点**：产品/菜肴特写，而不是屏幕；如果品牌有外卖/食谱应用，手放在台面上。
- **对话角色**：钩子是**展示而非描述**——将其塑造成观众正在观看的演示，而不是描述。钩子句落在手或第一配料已经动作中；视觉传递好奇心。弧线：演示钩子 → 命名产品+第一印象 → 感官高峰发生时叙述（倾倒/滋滋声/蒸汽）→ 满足洞察（“这是新的默认选择”）→ 笑点传递食谱或购物链接。

#### BEAUTY_APPLY
- **何时使用及原因**：护肤品、化妆品、香水、护发产品、身体护理——任何前后对比+应用仪式才是价值主张的领域。观众在匹配光线下看到视觉转化时转化；钩子与结尾的对称性才是销售结果的卖点。不是包装重量的奢侈品（→ HAUL_UNBOX）。
- **感官锚点**：泵压、挤压、皮肤滑行、光泽提升、液滴成珠、刷子扫过。
- **场景**：浴室镜子、自然日光或梳妆台灯光；钩子和结尾使用相同角度。
- **特写节奏点**：手持的产品特写（瓶装/管装/手拿粉盒），而不是屏幕。
- **对话角色**：钩子是**日常使用社交证明**——通过日常特定时刻暗示真实使用，而不是虚构时长。钩子种植了在后续拍摄中出现的对称性回报。弧线：日常使用钩子 → 命名+来源支持的要点成分或声明 → 叙述应用过程（特写手指/刷子与皮肤接触）→ 结尾拍摄（与钩子相同角度）→ 笑点暗示排他性或回购意图。

#### FITNESS_TRANSFORM
- **何时使用及原因**：健身设备、补充剂、恢复工具、运动服、带追踪功能的健身应用——任何工作到结果转化才是价值主张的领域。观众通过可共鸣的挣扎后的应得回报转化——展示蛋白粉瓶还不够，你必须展示锻炼过程。
- **感官锚点**：沉重呼吸、勺子击中粉末、设备咔哒声、汗水反射光线、锻炼后呼气。
- **场景**：健身房或家庭健身房；画面边缘是运动装备；地板或台面高度。
- **特写节奏点**：手拿手机显示应用统计数据/心率/经过时间，或产品包装特写（罐子里的勺子、瓶中倾倒）。
- **对话角色**：钩子是**可共鸣的阻力**——命名挣扎/摩擦/不想做（“我根本不想做这个”、“今天差点错过”、“这本来是休息日”）；通过分享疲惫感赢得信任，在展示工作之前展示它。弧线：阻力钩子 → 命名产品+非数字例行程序或来源支持的声明 → 叙述锻炼中时刻，特写展示设备或勺子 → 赢得信任的满足洞察 → 笑点将框架为持续使用。

#### TECH_UNBOX
- **何时使用及原因**：小工具、硬件、电子产品、智能家居设备、可穿戴设备、外设、AI硬件（框架笔记本电脑、AirPods、Whoop、Rabbit r1、Friend 项链、机械键盘、人体工学设备）——任何设备+初次使用时刻才是价值主张的领域。开箱仪式传递高端定位；观众在看到“它真的能工作/它做什么”时转化——初次使用节奏点是转化时刻。不是HAUL（→ HAUL_UNBOX），也不是纯软件/SaaS（→ APP_REVEAL）。
- **感官锚点**：多功能刀切割、塑料剥离、泡沫滑出、开机提示音、触感按钮按压、触觉点击、风扇启动。
- **场景**：木制书桌，开箱时俯视构图；手持初次使用；书桌/笔记本电脑使用时背景。
- **特写节奏点**：开箱并开机后的设备本身。`@Image2` 通常是设备屏幕在关键UI时刻的真实照片（初次测量、配对状态、英雄功能打开）；如果设备没有屏幕，则使用设备使用中干净的英雄照片。
- **对话角色**：钩子是**到达仪式**——命名这正在发生*现在*（“刚拿到这个”、“打开它”）。期待>描述；钩子种植了“它做什么？”的问题，初次使用节奏点回答。不要先带规格。弧线：到达钩子 → 当特写是设备在做事情时，命名+来源支持的规格头条（如果`claims_allowlist`有，否则定性头条）→ 初次使用揭示 → 工作流程改变洞察（“这取代/改变/修复了我的X”）→ 笑点传递找到它的地方，不编造成本或紧迫性。

### 6. 语音——模型默认
此技能没有语音克隆输入；视频模型使用其默认语音生成口语对话。不获取或传递语音样本。继续步骤7。

### 7. 生成——首次尝试使用头像，拒绝时卡通化，重试
在步骤2.5中的Avatar型探测通过后，尝试**首次**使用步骤2中解析的头像（调用者提供的或内置回退）**原样**调用。只有在Seedance拒绝调用时才重新设计。

重试预算：Seedance生成最多2次视频尝试：7a中的原始头像渲染，加一个7c中的卡通化头像重试。不要开始第三次Seedance渲染。如果第二次尝试失败，显示7d消息或在用户明确请求`provider=kling`或选择停止消息后切换到Kling。

**7a. 首次尝试——头像原样**
调用`generate_reference_video`：
- `provider`：`seedance`（默认）或`kling`（如果用户传递`provider=kling`）
- `aspect_ratio`：`9:16`（默认）；`3:4`仅在seedance上允许
- `resolution`：`720p`（seedance仅）
- `duration`：15
- `reference_images`：`[avatar_url, screenshot_url]`（如果步骤3失败，则删除`screenshot_url`）
- `prompt`：步骤4中的多节奏字符串
- `sound`：true（默认——环境音+模型生成的口型同步）

对于`provider=kling`：将多节奏文本转换为`shots: [{prompt, duration}, ...]`（5个镜头×3秒=15秒总和），加上顶级`prompt`总结广告。参考使用`<<<image_1>>>` / `<<<image_2>>>`而不是`@Image1` / `@Image2`。

如果调用返回`{ task_id, status: "queued" }`，使用上述异步轮询预算轮询`task_status(task_id)`，直到终端（`completed | failed | cancelled`）。在`completed`时，捕获`result.url` → `video_url`并继续步骤8。

**7b. 拒绝时——自动将头像卡通化**
如果7a在`image_urls` / `reference_images`返回`422 content_policy_violation`（seedance + fal-queue内容政策标记为过于逼真的肖像——即使是某些Pixar风格的3D头像也会被标记），原地重新设计头像：

调用`generate_image_edit`：
- `provider: "seedream"`（原生Pixar/3D动画外观）
- `images: [avatar_url]`
- `aspect_ratio`：与广告相同的宽高比
- `resolution: "1K"`
- `watermark: false`（seedream独有开关——确保下游口型同步重新渲染时重新设计的头像干净无提供者水印）
- `prompt: "风格化3D游戏角色渲染——虚幻引擎5 / Overwatch / Valorant / Apex Legends视觉风格。解剖学基础的面部比例，带有微妙风格化：略大的表达性眼睛，明确的雕塑型颧骨平面，平滑皮肤着色器（比逼真更平滑，无微孔细节），理想化但可信的特征。基于像素的材质，带有微弱的次表面散射，基于发丝的头发模拟，清晰的布料着色器。电影感三点工作室灯光，强烈的轮廓光。显然是风格化的AAA级游戏角色渲染——不是逼真人，不是Pixar塑料玩具卡通，不是夸张的大头比例。同一个人，同副眼镜，同套服装，同配件。居中中等肖像，中性室内背景。"`

捕获返回URL → `avatar_url_cartoon`。

**7c. 重试seedance使用卡通化头像**
重跑7a中的完全相同的`generate_reference_video`调用，将头像参考替换为：`reference_images: [avatar_url_cartoon, screenshot_url]`（如果步骤3失败，则为`[avatar_url_cartoon]`）。所有其他参数不变。捕获`result.url` → `video_url`。

**7d. 最终回退——仍然拒绝**
如果7c也返回`content_policy_violation`，停止。告诉用户：即使自动重新设计后，头像对seedance内容政策来说仍然过于逼真；请他们自己提供更风格化的肖像，或使用`provider=kling`重新运行（kling有单独的内容政策流程，接受逼真头像）。

### 8. 确定性品牌/规格叠加
在字幕之前，添加可读的品牌/规格文本，使用确定性后生成叠加。这故意与Seedance提示分开，因为视频模型文本渲染会损坏品牌标志和规格标签。

从步骤1构建叠加文本：

```json
{
  "brand_overlay_text": "<brand_name>",
  "grounded_spec_overlay_text": "<claims_allowlist中的一个简短来源支持的声明，或空>",
  "overlay_font_color": "#111111 | #ffffff"
}
```

规则：
- `brand_overlay_text`始终是WebFetch中的`brand_name`。如果`brand_name`为空，使用`product_name`；不要让模型编造标志/字标。
- `grounded_spec_overlay_text`必须为空或`claims_allowlist`中的一个确切声明。永远不要叠加一个`claims_allowlist`中不存在的数字。
- 选择`overlay_font_color`以与生成帧对比，而不是品牌美学。如果截图/产品表面是浅色或未知，使用`#111111`；仅在明显深色的片段中使用`#ffffff`。飞行后的OCR必须能够读取叠加。
- 不要使用此步骤生成字幕或逐字字幕；步骤9使用单个`add_captions`调用处理字幕。

调用`edit_text_overlay`一次用于品牌名称：

```
edit_text_overlay(
  video_url: video_url,
  text: brand_overlay_text,
  position: "top_left",
  font_size: 54,
  font_color: overlay_font_color,
  start_s: 0.2,
  end_s: 15
)
```

将返回的URL保存为`brand_guarded_url`。如果`grounded_spec_overlay_text`非空，再次在`brand_guarded_url`上调用`edit_text_overlay`：

```
edit_text_overlay(
  video_url: brand_guarded_url,
  text: grounded_spec_overlay_text,
  position: "top_right",
  font_size: 42,
  font_color: overlay_font_color,
  start_s: 6,
  end_s: 10
)
```

将返回的URL保存为`guarded_video_url`。如果不需要规格叠加，则设置`guarded_video_url = brand_guarded_url`。如果任何叠加调用返回`{ task_id }`，使用长任务合同轮询`task_status`。如果确定性叠加失败，停止并显示失败，而不是交付一个仅可读品牌/规格文本依赖于Seedance的视频。

在字幕之前对叠加窗口运行帧级OCR。视频级分析可能会错过短暂的角落叠加，因此提取一个帧，同时两个叠加应该可见：

```
extract_frame(
  video_url: guarded_video_url,
  time_s: grounded_spec_overlay_text ? 7 : 1
)
# 将返回的url保存为overlay_qa_frame_url

analyze_media(
  media: overlay_qa_frame_url,
  query: "预期品牌文本: ${brand_overlay_text}
预期规格文本: ${grounded_spec_overlay_text}
仅返回JSON: { \"visible_text_ocr\": string[], \"brand_visible\": boolean, \"spec_visible\": boolean, \"observations\": string[] }。OCR读取所有可见文本。brand_visible仅在上述预期品牌文本可读时为true。spec_visible为空或预期规格文本可读时为true。"
)
```

如果`brand_visible`为false，或者当`grounded_spec_overlay_text`非空时`spec_visible`为false，停止并重新渲染确定性叠加一次，使用相反的`overlay_font_color`（`#111111` ↔ `#ffffff`）。重新提取`overlay_qa_frame_url`并运行相同的OCR检查。如果重试仍然失败，停止并显示`overlay_qa_frame_url`和OCR JSON；不要继续到字幕。

### 9. 字幕——单次输出风格化烧录（默认开启）
如果请求`variants`，不要在此步骤运行单输出`add_captions`调用。保留`guarded_video_url`未加字幕，并继续到**宽高比变体**，其中每个请求的宽高比首先重新构图，然后重新构图后加字幕。

调用 `add_captions`：
- `video_url`：步骤 8 中的 `guarded_video_url`
- `style`：`"tiktok"`（默认 — 单词逐个紫色高亮，Bebas Neue 字体，全部大写，渲染在框架的**底部**；经典的 TikTok 创作者风格，保持面部和屏幕清晰）。替代选项：`"hormozi"`（中下黄色高亮，更激进 — 覆盖手持手机特写节拍的部分），`"classic"`（纯色底部字幕条，最安全），`"karaoke"`（渐进式彩色填充，也在底部）。
- `font_size`：`60` — 覆盖每个样式的默认值；针对 9:16 比例的可读性进行调整，且不主导框架。
- `language`：传递步骤 1 中检测到的页面语言 BCP-47 代码（`"en"`，`"zh"`，`"ja"`，`"es"` 等） — 跳过自动检测并避免将 CJK 字符集路由到仅支持拉丁字符的字体路径。

捕获返回的 URL → `final_url`。

## 纵横比变体

当用户希望从同一 UGC 广告中获取垂直短形式、横屏和方形内容流时，使用可选的 `variants=9:16,16:9,1:1`。`variants` 覆盖 `aspect_ratio` 以使用原生 `9:16`；`aspect_ratio=3:4` 仅用于单输出，且不能与变体结合使用。如果用户请求带有 `aspect_ratio=3:4` 的 `variants`，则使用原生 `9:16` 变体流程，并说明 `3:4` 仅适用于单输出运行。

对原生 `9:16` 广告调用一次 `generate_reference_video`，然后运行步骤 8 的确定性叠加一次以生成 `guarded_video_url`。不要重新运行产品获取、头像分析、截图捕获、头像卡通化、Seedance/Kling 生成、确定性叠加或任何其他昂贵的提供者调用以生成额外变体。

不要运行步骤 9 的单输出 `add_captions` 调用。首先构建原始 `variant_sources`，然后构建一个扁平的 `variant_urls` 对象：

```json
{
  "9:16": "<native final_url>",
  "16:9": "<edit_reframe url>",
  "1:1": "<edit_reframe url>"
}
```

- 对于 `9:16`，设置 `variant_sources["9:16"] = guarded_video_url`。
- 对于 `16:9` 和 `1:1`，调用 `edit_reframe(video_url=guarded_video_url, target_aspect="<aspect>", fill_mode="blur")` 并将每个返回的 URL 保存到 `variant_sources`。模糊填充保留完整的原生垂直广告，背景模糊，而不是裁剪掉创作者或字幕。
- 如果 `captions=true`，在重新构图后添加字幕：对每个 `variant_sources` 值运行 `add_captions`，以便烧录的字幕定位正确，然后将这些带字幕的 URL 保存到 `variant_urls`。如果 `captions=false`，直接将原生和重新构图的 URL 保存到 `variant_urls`。
- 设置 `final_url = variant_urls["9:16"]`，以便主要交付物与请求的原生变体匹配。
- 将 `edit_reframe` 和每个变体的字幕烧录视为廉价的最终合成/重新构图阶段。如果重新构图失败，返回成功的变体 URL 以及失败的纵横比和工具错误；不要重新提交昂贵的生成。

> **注意 — 变体使用模糊填充。** `16:9` 和 `1:1` 保持完整的原生 `9:16` 广告在模糊背景上可见。保持创作者、产品和字幕居中以提高可读性，但不要将这些输出描述为裁剪的变体。

### 10. 返回

返回一行 `final_url`，并加上一行摘要：运行了哪个类别、头像是否为调用者提供/内置回退/卡通化恢复、截图是否使用或回退到文本、选择的提供者、检测到的对话语言以及是否在烧录字幕。如果请求了 `variants`，请在同一响应中包含扁平的 `variant_urls` 对象。

## 事后质量门禁

在声明成功之前，当字幕被烧录时，对 `final_url` 调用 `analyze_media`，当 `captions=false` 时，对 `guarded_video_url` 调用 `analyze_media`，并请求结构化判断。如果请求了 `variants`，对每个 `variant_urls` 值运行相同的门禁，并按纵横比记录任何警告。

在调用 `analyze_media` 之前，将具体预期代入查询：包括确切的 `brand_name`、确切的 `product_name` 和实际的 `claims_allowlist` 值作为 JSON 数组。不要为模型留下占位符进行推断。

```
预期品牌：${brand_name}
预期产品：${product_name}
允许的数字/规格声明：${JSON.stringify(claims_allowlist)}

仅返回 JSON：{
  "verdict": "clean" | "degraded" | "catastrophic",
  "visible_text_ocr": string[],
  "unauthorized_numeric_claims": string[],
  "observations": string[],
  "quality_warning": string | null,
  "re_roll_suggestion": string | null
}
OCR 读取所有可见文本。在检查 `brand_name` 和 `product_name` 是否在任何位置正确拼写、确定性品牌/规格叠加是否清晰可读、当请求时字幕是否存在且未损坏，以及除非它完全匹配上面实际的 `claims_allowlist` 值，否则不会出现可见的数字声明时，使用上述具体的预期值。还检查头像/创作者是否保持视觉稳定，产品截图或文本回退是否与产品页面匹配，以及是否存在黑色框架或错误的产品拍摄。
```

- 如果 `verdict` 是 `clean`，正常返回 `final_url`。
- 如果 `verdict` 是 `degraded`，返回 `final_url` 加上 `quality_warning`，以便用户在发布前进行审查。
- 如果 `verdict` 是 `catastrophic`，如果 `visible_text_ocr` 包含损坏的品牌/规格文本，如果 `brand_name` 拼写错误，或者如果 `unauthorized_numeric_claims` 包含不在 `claims_allowlist` 中的声明，不要将广告标记为完成；而是显示 `verdict` 和 `re_roll_suggestion` 而不是声明成功。

## 失败模式

| 症状 | 可能原因 | 恢复 |
|---|---|---|
| 产品页面无法获取或捕获 | 页面受保护、被阻止或产品证据不足 | 如果调用者提供的产品信息明确，则仅使用调用者提供的产品信息；否则停止并请求产品摘要或更好的 URL。 |
| 头像预检标记可识别的 IP、不安全形象或无法使用的面部框架 | 提供的创作者图像不适合付费生成 | 在付费生成之前停止并请求更安全的创作者图像，或者在没有调用者头像提供时回退到内置的卡通化创作者。 |
| 提供者在图像/视频生成期间返回 4xx 或 `moderation_blocked` | 提示、源图像或产品内容被确定性拒绝 | 不要重试相同的负载。删除被拒绝的输入或仅在下一阶段有文档化回退提供者时切换到文档化的回退提供者。 |
| 确定性叠加 OCR 在一次颜色重试后失败 | 品牌规格文本仍然无法读取 | 停止并返回 `overlay_qa_frame_url` 和 OCR JSON；不要继续进行字幕或最终交付。 |
| 变体重新构图或每个变体的字幕烧录失败 | 廉价的最终合成步骤在昂贵的原生广告成功后失败 | 返回成功的变体以及失败的纵横比/工具错误；不要重新运行产品获取、头像准备或视频生成。 |

## 承重短语

这些锚点防止广告漂移成通用的产品演示：

| 短语 | 位置 | 为什么承重 |
|---|---|---|
| `HOOK + 3 JUMP CUTs + OUTRO` | 提示骨架 | 强制 TikTok 风格的多切节奏，而不是连续的主持人镜头。 |
| `Every beat has a Says: "..." line` | 提示骨架 | 为视频引擎提供所有节拍的明确口型材料。 |
| `Trust @Image2` | 屏幕特写规则 | 防止在已经提供真实截图时发明产品 UI。 |
| `exactly one` 屏幕特写节拍 | 提示组合 | 防止广告变成屏幕录制而不是创作者风格的揭示。 |
| `Write all Says lines in the language detected from step 1` | 对话规则 | 防止本地化产品页面默认使用英语对话。 |
| `forbid inventing numbers` | 提示基础 | 防止不支持的规格声明进入旁白或叠加。 |
| `Deterministic brand/spec overlays` | 步骤 8 | 防止可读的品牌名称和规格文本出现在视频模型文本渲染中。 |
| `single add_captions call` | 字幕步骤 | 避免因链式文本叠加而导致的质量损失和漂移。 |

## 示例

- `/pika:ugc-ads https://pika.me avatar_url=https://cdn/face.png` → APP_REVEAL, 9:16, seedance, 真实截图, 字幕开启
- `/pika:ugc-ads https://maisonbrune.com avatar_url=https://cdn/face.png aspect_ratio=3:4` → HAUL_UNBOX, 3:4, seedance
- `/pika:ugc-ads https://pika.me avatar_url=https://cdn/face.png provider=kling captions=false` → APP_REVEAL, 9:16, kling shots[], 无字幕
- `/pika:ugc-ads https://pika.me` → 没有 `avatar_url` → 使用内置的 Pixar 风格女性创作者肖像，运行端到端
