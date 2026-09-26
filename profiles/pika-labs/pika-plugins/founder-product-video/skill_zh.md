# founder-product-video

您可以根据产品网址和用户提供的图像生成一个65秒的创始人风格产品视频：60秒的创始人演讲视频主体加上5秒的品牌结尾卡片。用户提供的图像（产品照片/网站截图/应用截图）将作为视觉参考流入SeeDance，生成后会将数字产品屏幕/品牌标识合成为可读的UI，而不是模型渲染。

没有切换镜头。不提取网站CSS。AI生成、确定性渲染、字幕、拼接和音乐混合默认通过Pika MCP工具进行。下三分之一覆盖层是可选的，默认使用MCP合成，只有在紧急情况下才使用本地ffmpeg作为后备方案。

## 成本透明度门

在任何付费MCP调用之前，调用一次 `identity_balance({verbose: true})`。显示当前余额、近期燃烧率和剩余运行空间，然后用确切的消息门控运行：

> 预计成本：典型的四幕Seedance创始人视频和支持性资产大约需要4000积分（约40美元）。这超过了5美元，请回复 `proceed` 继续或 `cancel` 停止。

在用户回复 `proceed` 之前，不要调用任何付费MCP工具。如果用户回复 `cancel`，则停止生成。对于非交互式 `--quick` 或 `--config` 调用者，需要在配置中要求 `cost_ack=proceed`；如果缺失，则停止并显示估计值，而不是花费积分。

## [0] 摄入 — 在任何管道步骤之前运行

**如果使用空参数调用**，打印此菜单原文并停止 — 等待用户粘贴输入：

> **您想制作什么样的创始人视频？** 必须提供：
> - **产品网址** — `https://...`（任何具有真实主页的内容）
> - **创始人** — 姓名 + 职位，例如 *"Eli Kim, CEO"*
> - **创始人照片** — 本地路径、https URL，或 `generate`（我将创建肖像）

可选（省略时使用合理默认值）：品牌套件路径 · 自定义手机截图 · 音乐 · 画幅（16:9 / 9:16 / 1:1）· 位置图像 · 语音风格 · 产品类型

示例：`/founder-product-video https://example.com --founder "Eli Kim, CEO" --photo ~/Pictures/eli.jpg`

**如果参数在交互模式下包含部分输入**，跳过菜单，逐个询问以收集缺失的必填字段 — 问，等待，再问下一个。不要将问题捆绑在一个块中。如果用户在提示之前提供某个字段（例如，他们在触发消息中粘贴了URL），则跳过该问题，并在最后确认一次该值。不要在所有必填字段都回答之前开始管道。如果适用非交互式快速通道，则使用步骤 [0.5]。

### [0.5] 非交互式快速通道

当调用者传递 `--quick` 或 `--config <path>`，或调用者声明他们是从CI、子代理、批处理作业或其他任何非交互式框架运行时，使用此路径。

本节优先于下方的交互式询问/等待说明。当适用时，使用此快速通道，并且除非 `url` 或创始人姓名/角色确实缺失，否则不要跳转到多轮摄入。

- `--config <path>` 指向一个包含规范输入契约预烘焙值的JSON文件：`url`、`brand_kit_path` 或 `build_brand`、`founder_name`、`founder_role`、`founder_photo`、`assets`、`music_url`、`aspect_ratio`、`location_image_url`、`voice_style`、`product_type` 和 `lower_third`。
- `--quick` 表示使用默认值进行可选附加项，如果省略 `brand-kit`，则使用 `build-a-brand --quick` 自动构建品牌套件，并且在未提供照片时使用 `founder_photo = "generate"`。
- 对于 `--quick` 或 `--config`，不要在品牌套件分支、创始人照片生成提示、可选附加项提示、脚本选择或结尾卡片/字幕默认值处停止确认。直接记录假设并继续。
- 如果 `url` 或创始人姓名/角色在参数或配置中找不到，则停止一次，并显示一个紧凑的缺失字段列表，而不是开始多轮问答循环。

**1. 产品网址** *(必填)* — `https://...`。用于（a）步骤 [1] 中的简报生成和（b）为下方的品牌套件分支提供输入。

**2. 品牌套件** *(必填)* — 交互模式：询问 *"您已经有品牌套件文件夹，还是应该先构建一个？"* 
- 如果是路径 -> 使用它 (`state.brand_kit_path = <path>`)。接受 `brand.json` 或导出的 `build-a-brand` 套件，其中包含 `brand.md`、`tokens/tokens.json` 和标志资产。
- 如果是 "build" -> 调用 `build-a-brand` 技能对 URL/简报进行操作，并等待导出的品牌套件。这是一个完整的身份工作流程，可能会暂停以供用户选择；在交互模式下显示这些提示。
- 快速通道：如果配置提供 `brand_kit_path`，则使用它。如果配置设置 `build_brand` 或 `--quick` 省略 `brand-kit`，则对 URL/简报调用 `build-a-brand --quick` 并等待导出的品牌套件；不要显示 `build-a-brand` 提示或停止以供身份选择。在任一分支后，设置 `state.brand_kit_path`。如果路径不存在且无法构建品牌套件，则停止并显示一个紧凑的缺失字段列表。

**3. 创始人身份** *(必填)* — 交互模式：一起询问所有三个：
- `founder_name` — 例如 "Avery"
- `founder_role` — 例如 "CEO, ExampleCo"
- `founder_photo` — 本地路径 / https URL / 或字面字符串 `generate` 以自动创建肖像。如果 `generate`，提示用户输入一句话的基调（"温暖、休闲、时尚的着装" / "皮克斯风格的3D动画" / 等等）— 这将成为步骤 [4] 中 `generate_image` 的种子提示。
- 快速通道：使用来自参数/配置的创始人值。如果省略 `founder_photo`，则设置 `founder_photo = "generate"` 并使用从产品基调中推导出的中性创始人肖像基调；不要停止以供单独的照片基调提示。

默认情况下不使用下三分之一覆盖层，以便保持快乐路径简洁。如果用户明确要求下三分之一覆盖层，则记录 `state.lower_third = true`；在交互模式下，确认 `edit_video_compose` 将在渲染后添加透明覆盖层。

**4. 可选附加项** — 交互模式：作为单个消息提供一次，如果没有在同一轮中回复答案，则继续进行。快速通道：使用下方的默认值，无需询问。
- *自定义图像* — 显示在创始人手机上的资产列表（产品照片 / 应用截图）。**省略时默认：** 如果存在 `brand.json.screenshots`，则使用其中的截图，否则在品牌套件中查找明显的截图或产品图像，否则在步骤 [2] 之前使用 `capture_website(mode:"screenshot")` 捕获产品URL。除非 `product_type` 明确为 `service` 并且用户接受仅环境视频，否则在没有真实产品UI/产品图像的情况下不要继续到脚本或 SeeDance。在快速通道中，如果不存在提供的/品牌套件/捕获的资产，则停止并显示一个紧凑的缺失资产错误，而不是无声地发送一个通用的讲话头视频。
- *音乐* — 本地路径 / https URL / 或 `generate`（器乐，~60秒）。默认：通过Kling背景模式 `generate`。
- *下三分之一覆盖层* — 可选。默认：关闭。如果启用，则通过MCP渲染透明 `.mov`，然后使用 `edit_video_compose` 将其叠加到主体上。
- *画幅* — `16:9`（默认）、`9:16`、`1:1`。
- *位置* — 默认为 `state.brand.colors.accent` 中的平面无缝背景（干净的影棚拍摄外观，角色对单一品牌颜色，无论品牌是什么强调色）。如果用户想要办公室、户外等，则使用路径 / URL / 文本描述覆盖。
- *语音风格* — SeeDance的VO方向字符串，例如 "温暖、真实的创始人能量，对话式"。默认：从 `brief.tone` 派生。
- *产品类型* — `digital | physical_apparel | physical_object | consumable | service`。默认：在步骤 [2] 中从资产分析自动派生。

在阶段0完成后，将所有收集的值存储在 `state.inputs` 中。如果您已经为本次运行创建了本地工作目录，则可以选择将相同的对象作为 `<workdir>/inputs.json` 持久化；不要要求预定义的工作目录环境变量。然后进入步骤 [1] 的管道。

### [0.6] 创始人照片的Avatar类型探测

在任何付费 `generate_reference_video` 调用之前，在本地上传或用户提供的URL规范化后的创始人照片/头像URL上运行此Avatar类型探测。这适用于用作角色参考的任何创始人照片 — 无论是通过 `--photo` 提供 还是生成。

调用一次 `analyze_media`：

```
query: "为付费视频生成分类此图像。它是真实人脸的照片、AI生成的逼真肖像、风格化/插图角色，还是像蝙蝠侠、皮卡丘或米老鼠这样的可识别的商标/版权角色？仅返回严格的JSON：{ \"avatar_type\": \"real_human\" | \"ai_realistic\" | \"stylized_illustrated\" | \"recognized_ip\", \"recognized_character\": string | null, \"moderation_risk\": \"low\" | \"medium\" | \"high\", \"recommendation\": \"proceed\" | \"warn\" | \"reject\" }。当没有识别特定角色时，使用null作为 `recognized_character`；永远不要在该字段中写入 \"none\"、\"unknown\" 或解释性文字。"
```

根据结果路由：
- **识别的IP / 版权风险** -> **仅在** `avatar_type` 为 `"recognized_ip"`，或 `recognized_character` 称呼特定角色（例如 `"Batman"`），或当 `moderation_risk` 为 `"high"` 且 `recommendation` 为 `"reject"` 时 **停止**。将 `recognized_character: null`、空字符串、`"none"`、`"unknown"`、`"n/a"` 和低/中 `moderation_risk` 视为单独不足以停止。在真实/风格化路线之前运行此检查。即使 `avatar_type` 是风格化/插图，chibi蝙蝠侠仍然是蝙蝠侠。
- **真实人类 / AI生成的逼真** -> 正常进行。
- **风格化 / 插图** -> 带有可见警告继续进行，因为风格化头像可能对Seedance肖像和审核不太可靠，然后只有在用户提供或接受该头像时才继续。
- **商标/版权** -> **在生成前停止**。显示此消息：`您的创始人照片似乎是商标角色（[X]）。大多数视频提供商会审核并拒绝生成。使用 --photo <真实照片URL> 覆盖。` 对于此技能，`--photo <真实照片URL>` 是接受的明确标志；您也可以提及跨技能 `--avatar <真实照片URL>` 说法，因为用户可能知道这个惯例。

## 必填输入（规范契约）

在阶段0之后，这些是下游步骤消费的字段：

- `url` — 产品网站（https://）。驱动步骤 [1] 简报。
- `brand_kit_path` — 品牌套件文件夹。必填。结尾卡片和下三分之一覆盖层在存在时消耗 `brand.json`，否则消耗 `brand.md`、`tokens/tokens.json` 和来自 `build-a-brand` 导出的标志资产。见步骤 [4.5]。
- `founder_name` + `founder_role` + `founder_photo` — 从摄入中必填。步骤 [4] 在任何 SeeDance 调用之前将 `founder_photo` 规范化为 `founder_photo_url` 和 `character_url`。
- `assets` — 可选数组 `{ url, role?, caption? }`。默认为品牌套件捕获的截图；当品牌套件没有截图时，在步骤 [2] 之前捕获产品URL，并将返回的 `image_url` 存储为真实产品UI资产。`role` 是一个提示字符串，将资产映射到脚本节拍（`hero`、`feature_a`、`cta` 等）。
- `location_image_url` — 可选。默认为生成的实色背景，位于 `state.brand.colors.accent`。
- `music_url` — 可选。默认为 `generate`（步骤 [7] 中的Kling 60秒背景铺底）。
- `aspect_ratio` — 默认 `16:9`。
- `voice_style` — 可选，默认为 `brief.tone`。
- `product_type` — 可选，在步骤 [2] 中自动派生。

## 状态

在处理过程中保持一个简单的 `state` 对象，并保存每个CDN URL，以便可以恢复部分运行。将 `task_status` 值 `completed` 视为成功的终端状态（`failed` 和 `cancelled` 是失败的终端），然后当存在时解包 `result.structuredContent`。最终视频存储在Pika的CDN上；除非MCP合成不可用并且您明确触发步骤 [8b] 中的本地下三分之一后备方案，否则不需要本地工作空间。

## 长任务 `task_status` 投票

当任何长时间运行的生成或编辑调用返回带有或没有初始状态的 `task_id` 时，包括 `{task_id}`、`{task_id, status: "queued"}` 或初始 `queued`、`running` 或 `processing` 状态，立即在 `state` 中记录任务ID和开始时间。

- 在终端 (`completed | failed | cancelled`) 之前，在 `task_status({task_id})` 中以紧密循环调用，直到终端。不要手动睡眠，不要使用Bash轮询；工作进程会保持每个状态调用打开。
- 在状态为 `queued`、`running` 或 `processing` 时，每60秒发出一条可见的进度行：`Seedance i2v queued for {N}m {S}s... still processing`。在轮询音乐、字幕、渲染、拼接、混合或编辑任务时，替换提供者/阶段标签。
- 在 `completed` 时，解包返回的结果URL并将其保存到 `state`。
- 在 `failed` 或 `cancelled` 时，向用户显示失败，包括 `task_id`、状态和最后的状态消息。
- 从原始提交开始，15分钟后如果任务仍然非终端，调用 `task_cancel({task_id})`，然后向用户显示失败。如果取消报告任务已经终端，则调用状态一次并报告终端结果。
- 在原始任务仍然是 `queued`、`running` 或 `processing` 时，不要提交重复请求。

## 管道概述

```
[阶段0] 摄入          您（Claude）：询问用户网址 + 品牌套件（路径或构建）+ 创始人（姓名/角色/照片）+ 可选附加项
  → [0.5] 品牌套件自动构建（仅当用户说 "build"）
                          调用 `build-a-brand`；在非交互模式下使用 `build-a-brand --quick`
  → [1] 分析简报             pika MCP：产品名称 + 标语 + 功能 + 调性 + CTA
  → [2] 解析产品UI资产       pika MCP：使用提供的/品牌套件截图，或捕获产品URL
  → [2] 分析媒体 × N         pika MCP：理解每个真实资产显示的内容
  → [3] 编写脚本            您（Claude）：4幕 × 15秒；将资产映射到幕
  → [4] 创始人/位置参考     pika MCP：上传或生成创始人参考；携带提供的自定义位置
  → [4.5] 品牌套件摄入      解析 `brand.json` 或 `brand.md` + tokens → `state.brand`；如果需要，生成默认品牌强调位置
  → [5] 并行生成参考视频 × 4  pika MCP：SeeDance幕，资产图像作为参考
  → [5.5] 数字UI覆盖层      pika MCP：将真实产品UI/标识合成为数字揭示幕 + OCR QA
  → [6] 编辑拼接幕          pika MCP：60秒拼接基础（仅对话音频）
  → [7] 生成音乐            pika MCP：Kling 60秒柔和器乐背景铺底
  → [8] 字幕/下三分之一覆盖层  pika MCP：添加字幕的 `add_captions`；将下三分之一渲染为透明 `.mov`，然后在启用下三分之一时使用 `edit_video_compose` 将其叠加到主体上。
  → [9] 渲染HTML动画        pika MCP：5秒结尾卡片 — 作者内联HTML，品牌套件内联字体，画幅与主体匹配，无角落杂乱，CSS @keyframes（不是GSAP）
  → [10] 编辑拼接 + 音频混合  pika MCP：拼接主体 + 结尾卡片，然后混合音乐到完整的~65秒
  → [10.5] 最终时长探测     pika MCP：分析最终_url 并在交付前强制执行55秒时长下限
  → [11] 最终_url            保存MCP返回的最终_url；仅在本地后备方案创建了最终MP4时才上传
  → [12] 交付
```

## 运营注意事项

保持主要工作流程专注于排序。历史服务器验证细节存储在 `references/ops-notes.md` 中；这里仅保留活动约束：

- 每个SeeDance表演使用一个独特的`seed`（101、202、303、404）。相同的生成参数可以重放缓存的失败。
- Kling音乐底生成使用`provider: "kling-audio"`、`mode: "text_to_audio"`、`background: true`和`duration_seconds: 60`；MCP工作器生成一个10s的Kling seed，并在本地扩展。
- 如果SeeDance拒绝真实人物创始人照片，重新生成创始人参考，而不是重试相同的拒绝参考。
- 对于本地品牌套件标志，仅上传适合标志的栅格资产（`image/png`、`image/jpeg`或`image/webp`）。不要将SVG发送到`upload_asset`；从`build-a-brand`选择PNG导出或先栅格化。
- 在最终卡片的HTML中使用CSS `background-image: url(...)`来引用CDN托管的标志/照片资产；`<img crossorigin>`被CDN CORS阻止。
- 使用服务器端确定性工具来生成字幕、下三分之一合成、连接和混合。本地ffmpeg仅在`edit_video_compose`不可用且`state.lower_third = true`时作为备用。

将每个15s的表演分解为3个时间编码的子镜头。单镜头表演看起来很静态。
以风格匹配位置构图开头，并在所有4个表演提示中重复相同的`WARDROBE LOCK:`句子。

## [1] 分析简报

```
analyze_brief(
  sources=[{ type: "url", url: <product_url> }],
  context: "创始人风格的60秒产品视频。需要：产品名称、一句话标语、3-5个关键特性、目标受众、品牌语气和行动号召。"
)
```
将结果保存为`brief`。您将在整个过程中引用`brief.product_name`、`brief.tagline`、`brief.key_features`、`brief.tone`和`brief.call_to_action`。

## [2] 解决产品UI资产，然后分析每个资产并推导出`product_type`

在分析资产之前，规范化`assets`，以便产品揭示镜头有真实的视觉参考：

1. 首先使用任何调用者提供的`assets`。
2. 如果没有提供，当存在时，从`brand.json.screenshots`中读取屏幕截图。
3. 如果`brand.json`没有屏幕截图，查找品牌套件中明显的栅格屏幕截图或产品图像（`screenshots/`、`assets/`、`product/`或像`hero`、`screen`、`app`、`dashboard`、`product`这样的图像文件名）。
4. **在执行上述检查后，如果`assets`为空，则在产品URL上调用`capture_website`**：

```
capture_website(
  url: <product_url>,
  mode: "screenshot",
  mobile: false
)
# 将结果.image_url保存为assets[0].url，角色为"website_capture"。
```

如果产品可能是移动优先的，还运行第二个捕获，`mobile: true`，并在可用时保留两个URL。在继续之前将这些保存为真实的产品UI资产。

不要在没有至少一个真实产品UI/产品图像资产的情况下继续脚本编写、`generate_reference_video`或任何付费SeeDance调用，除非调用者明确设置了`product_type: "service"`并接受了一个仅限环境的视频。如果捕获失败或返回没有`image_url`，则显示：`无法捕获<url>。请提供屏幕截图或托管的产品资产；创始人产品视频不会在没有真实产品UI的情况下静默发货。`

对于`assets`中的每个条目，运行`analyze_media`以提取内容+视觉风格+**资产类型**。在一个工具批处理中并行运行所有内容：

```
analyze_media(
  media: <asset.url>,
  query: '简要描述此产品图像。返回严格的JSON：
  {
    "content_description": "1行总结图像中可见的内容",
    "asset_type": "digital_screen | physical_apparel | physical_object | consumable | infographic | other",
    "key_elements": ["3-5个特定的UI元素/特性/图像中的对象"],
    "visible_copy": "任何可见的文本——标题、按钮标签、标语、T恤图形文本（或空字符串）",
    "primary_colors": ["#hex", "#hex", "#hex"],
    "vibe": "1行视觉感受",
    "best_for_act": "hook | problem | solution | proof"
  }
  仅返回JSON。'
)
```

`asset_type`解码器：
- `digital_screen` — 应用UI/网站屏幕截图/SaaS仪表板/移动应用捕获
- `physical_apparel` — T恤、连帽衫、帽子、任何可穿戴物品（模特+服装）
- `physical_object` — 小工具、配件、包装商品、任何手持物品
- `consumable` — 食物、饮料、补充剂（某种使用/食用/饮用的东西）
- `infographic` — 图表、图表、数据可视化、插图
- `other` — 任何其他；描述并选择最佳匹配

保存为`asset_analyses[i]`。

分析后，构建：

```
usable_product_assets = asset_analyses
  .map((analysis, i) => ({
    asset_index: i,           # 要在script.shots[].asset_index中使用的原始assets[]索引
    asset_url: assets[i].url, # 传递给reference_images的公共URL
    asset_type: analysis.asset_type,
    analysis
  }))
  .filter(entry.asset_type in [
    "digital_screen",
    "physical_apparel",
    "physical_object",
    "consumable"
  ])
```

如果`usable_product_assets`为空，并且您尚未尝试URL捕获，则在产品URL上调用`capture_website(mode:"screenshot")`，将返回的`image_url`附加到`assets`，在捕获上运行`analyze_media`，将分析保存在相同的新索引处，并重新构建`usable_product_assets`。因此，捕获的屏幕截图必须有自己的`asset_index`；不要重用标志/英雄/信息图的索引来产品揭示。

不要从仅标志、仅英雄、信息图、抽象品牌或`other`资产自动推导出`product_type = "service"`。这些不是真实的产品揭示锚点。如果`usable_product_assets`在捕获尝试后为空，除非调用者明确设置了`product_type: "service"`并接受了一个仅限环境的视频，否则停止。相反，显示缺少资产的错误，而不是落入服务揭示模式。

### 推导`product_type`

查看`usable_product_assets`中占主导地位的`asset_type`：

```
product_type = mode(usable_product_assets[i].asset_type) → 映射到 {
  digital_screen → "digital"
  physical_apparel → "physical_apparel"
  physical_object → "physical_object"
  consumable → "consumable"
}
```

如果用户明确传递了`product_type`，则使用该值并跳过自动推导；`service`仅在明确选择/接受时才有效。`product_type`值驱动**步骤[3]中选择的镜头以及步骤[5]中创始人如何揭示产品**。如果搞错了，视频会在屏幕上显示错误的东西。

## 产品类型→揭示模式（此技能中最重要的表格）

`product_type`（在步骤[2]中设置）控制要选择的镜头，并且如何在每个镜头中揭示资产。**SeeDance提示中的揭示节拍是产品特定的；使用错误的节拍会使创始人拿着手机为T恤品牌。**

对于`digital`产品，SeeDance提示仅负责创始人、摄像机移动、手机手势和一个空白/中性屏幕占位符。**不要要求Seedance或视频模型渲染可读的品牌标志或产品UI文本。** 真实的屏幕截图、产品UI和确切的品牌拼写将在步骤[5.5]中合成。

| product_type | 揭示镜头 | 揭示节拍（用于SeeDance提示） | 哪些镜头获得资产 |
|---|---|---|---|
| `digital` | C-phone, E-phone | "创始人将她的手机举向摄像机；手机有一个为真实UI覆盖保留的空白中性屏幕占位符；不要渲染可读的UI文本或品牌标志" | 仅C和E镜头 |
| `physical_apparel` | G-hold, G-wear, E-detail | "创始人将一件炭洗图形T恤举向摄像机；衬衫设计完全匹配@ImageN——匹配图案/图形，不要虚构" 或 "创始人穿着来自@ImageN的T恤——完全匹配图案" | 每个可见T恤的镜头（C/E/F + "穿着"变体） |
| `physical_object` | C-hold, E-detail, F-twoshot | "创始人举起[产品名称]朝向摄像机；产品完全匹配@ImageN——匹配形状、颜色、品牌" | 显示产品的镜头 |
| `consumable` | C-hold, E-detail, H-using | "创始人拿着/使用[产品]；包装/产品与@ImageN完全匹配" | 显示产品的镜头 |
| `service` | A, B, D, F（环境） | 没有特定的产品揭示——专注于创始人+环境 | 没有镜头参考资产 |

对于物理产品，每个在画面中显示产品的镜头都应传递该资产作为参考图像；否则SeeDance倾向于虚构一个看起来通用的产品。对于服装，如果创始人穿着T恤，而脚本说“我们制作T恤”，那么创始人需要参考其中一个资产，即使在不是揭示时刻的镜头中也是如此。在`reference_images`中传递资产URL，并编写提示语言，如“创始人穿着来自@Image3的T恤——图案完全匹配”。

## [3] 编写脚本+角色声音+每镜头资产+每行节拍（你来做——不调用模型）

三个子产品，全部由你（Claude）以一个内联JSON编写：

1. **`character_voice_profile`** — 描述角色默认交付的3-4行（贯穿所有表演以保持一致性）
2. **每镜头的`asset_index` + `reveal_beat`** — 这个镜头中可见的资产及其揭示方式
3. **每镜头的`beats[]`** — 行动指导，带有`emotion` + `physical` + 句子之间沉默的节拍

这是将通用AI谈话头与真正有意图的角色区分开来的地方。在下面的四个子部分（[3.0]创始人声音、[3a]角色声音配置文件、[3b]节拍、[3c]过渡、[3c.1]表演能量、[3d]完整JSON）阅读之前，再编写。

### [3.0] 创始人声音——写一个提案，而不是功能列表

这项技能中最常见的失败模式是阅读起来像营销页面要点列表的对话（“它可以推理。编码。甚至写你的电子邮件。没有代理。没有选择器。没有维护。将其连接到LangChain。LlamaIndex。MCP。GitHub上有两万四千颗星星。MIT许可。生产级。”）——干净的副本，但它不是创始人会摄像机前推销自己产品的样子。现场反馈：*"脚本听起来像要点列表，而不是创始人会在摄像机前推销自己的产品。"*。

在摄像机前推销自己产品的真实创始人使用：
- **第一人称所有权** — "我建造的"、"我们发布的"、"我们自己使用"、"老实说我们只是想让它无处不在"
- **个人利益或起源时刻** — 表演1应参考创始人亲身经历的挫折，而不是抽象地参考产品。"每次我尝试构建X，我都会遇到同样的墙"比"X很困难"更有力
- **对话连接词** — "看"、"老实说"、"事情是"、"所以"、"实际上"、"..."用于思考。这些在写作中是抛开的词，但自然说话的呼吸。
- **"赌注"框架的产品** — "如果X只是工作呢？"、"我们问自己"、"整个想法是"。创始人将他们的产品视为自己问自己的问题的答案，而不是能力列表。
- **一个具体的锚点** — 一个特定的数字、一个特定的时间、一个特定的场景。"去年两万四千名开发者星标了它"比"它很受欢迎"更有力。"在凌晨3点布局崩溃"比"刮削器不可靠"更有力
- **邀请能量CTA** — "来试试我们"、"去玩玩"、"我们只是想让它无处不在"。不是"停止刮削。开始提取。"（那是Don Draper的标语，不是创始人）。

**禁止模式**（每个都是用户实证指出的，不要重复）：

| ❌ 禁止模式 | 示例 | 原因 |
|---|---|---|
| 三重否定咒语 | "没有代理。没有选择器。没有维护。" | 感觉像营销咒语，不是人类语言 |
| 能力断奏 | "它可以推理。编码。甚至写你的电子邮件。" | 读起来像功能清单 |
| 集成列表作为提案 | "将其连接到LangChain。LlamaIndex。MCP。" | 一次通过一次提及集成是好的——永远不要作为3个节拍的钩子 |
| 标语结尾 | "停止刮削。开始提取。" | 纯广告文案。创始人以邀请结尾，而不是标语 |
| 规格作为提案 | "MIT许可。生产级。" | 规格放在README中，不是创始人摄像机前的嘴 |
| "只是"作为列表中的填充 | "只是一个API调用。只是一个任何URL。只是一个结构化JSON。" | "只是"重复读起来像营销强调，不是自然语言 |

**允许模式**（用这些代替）：

| ✅ 模式 | 示例 |
|---|---|
| 个人利益钩子 | "老实说——每次我尝试构建X，都发生同样的事情。..." |
| "如果"框架 | "所以我们制作了Y。整个想法是：如果Z只是工作呢？" |
| 一个具体的声明 | "去年我们达到两万四千颗星。人们将我们连接到 everywhere。" |
| 随意的痛苦旁注 | "把它交给一个URL。得到干净的结构化数据。布局改变？没关系。" |
| 邀请结尾 | "如果你的代理需要实际看到活网——来试试我们。" |

**结构**（4个表演，每个表演约30-40个字=120-160个字，约50-60秒说）：

- **表演1：个人利益/痛苦。** 第一人称。参考创始人亲身经历的特定挫折。干净地落在命名的问题上。
- **表演2：赌注。** "所以我们制作了X。想法是——如果[痛苦]只是工作呢？" 一句话说明它实际上做什么（URL→数据，提示→图像等）。
- **表演3：证据+社区。** 一个具体的数字（星标、客户、ARR）。一个随意的集成或使用提及。语气：安静的自信，不是吹嘘。
- **表演4：邀请。** "如果[读者情况]——来试试我们。[URL]。[一条邀请的线]。". 以温暖而不是标语结束。

**在批准脚本之前自我测试。** 大声朗读每个表演的对话。如果你会在摄像机前作为创始人说它感到尴尬，重写它。如果它听起来像30秒的商业旁白，重写它。如果一个段落有超过两个连续的短片段的标点符号，重写它。

### [3a] 推导`character_voice_profile` + `wardrobe_lock`

两个分开的字段，都需要：

**`character_voice_profile`**（3-4行）——角色如何交付所有内容：节奏、默认表情、标志性手势、手习惯、暂停行为、微笑何时出现。参考`brief.tone` + 角色参考图像（`character_image_url`或你生成的创始人参考）+ `product_type`。这是演员的"环境"——不是他们说什么，而是他们是谁。它贯穿所有4个表演，以保持一致性感觉是故意的，而不是偶然的。

**`wardrobe_lock`**（1句话）——角色在所有表演中穿着什么。SeeDance为每个15s生成读取@Image1，并且可能在表演之间解释不同的服装。衣柜锁句子在每个表演的提示中逐字重复，以保持服装一致。阅读创始人参考照片中穿着的服装并明确描述它。示例：*"在整个4个表演中穿着相同的炭洗连帽衫和深色乐队T恤，黑框眼镜"*。如果没有明确的衣柜锁，后面的表演可能会在第一个表演匹配@Image1的情况下发明不同的服装。

**语气模板起点**（编排者挑选/自定义自简报语气）：

| `brief.tone` | 默认语速 | 表情 | 手势 | 停顿 |
|---|---|---|---|---|
| `casual` | 交谈式，像在咖啡厅向朋友解释 | 默认略带微笑，眉梢一挑时泄露 | 大声宣告时手势展开平放，思考时手托下巴 | 持续眼神接触而非填充沉默 |
| `playful` | 轻快顿挫，富有表现力 | 恶作剧藏在眼神中，频繁眉梢一挑，笑点在妙语之后才到来 | 轻轻肩部晃动，生动地数手指 | 知道ingly的短暂停顿 |
| `professional` | 稳定语速，从容不迫 | 温和直接的眼神接触，克制的微笑 | 手势位置刻意而非持续，单手展开手势 | 自信的沉默，不填充 |
| `technical` | 分析性，稍慢 | 分析性默认，思考时眼珠转动后回到原位 | 手托下巴思考手势，指向想象中的图表 | 思考时的停顿，眼神向上偏左 |
| `disruptive / edgy` | 顿挫，句子简短且突然停顿 | 干燥的平板默认，恶作剧的微笑突破后又消失 | 身体保持静止，表情是关键 | 尖锐的停顿，轻微的头部倾斜 |

**示例工作——开发者工具创始人（休闲语调，3D 皮克斯 20 多岁女性）**：
> "休闲自信，像在咖啡厅向朋友解释产品。默认略带微笑。关键揭示时眉梢一挑。思考时手托下巴，大声宣告时手势展开平放。停顿时保持眼神接触而非填充沉默。妙语直白落地，小微笑在之后才到来。"

**示例工作——街头服饰创始人（俏皮/锐利语调）**：
> "敏锐的干练幽默。快速简短句子，突然停顿。默认轻微微笑，单眉一挑。对痛点（'无聊'，'普通'）时翻白眼。恶作剧的微笑在妙语中突破但立即消失。手部基本保持静止——表情是关键。"

### [3b] 按行 `beats[]` — 行级指导，非表演级

每个镜头的对话被分成 `beats`。每个 beat 是一个简短句子（或刻意沉默），有自己的 `emotion` + `physical` 指导。beat 之间的沉默是表演的一部分——用持久的凝视、微表情、手势过渡来填充。

带有 `text: "(beat)"` 的 beat 是沉默（没有说出的文字）——它只是描述句子之间自然停顿时发生的视觉动作。在需要强调并保持时刻的对话 beat 之间使用这些。

当在步骤 [5] 构建 SeeDance 提示时，beats 成为每镜头的表演指导（没有 `(beat)` 标记的对话文本成为 `<<<voice_1>>>` 有效载荷）。 

### [3c] `transition_from_prev` — 在同一剪辑中镜头间编排连续的摄像机运动

**SeeDance 的基本限制**：每个 15 秒的 SeeDance 生成渲染一个虚拟环境和一个虚拟摄像机。当多镜头提示声明“镜头 C，然后镜头 A”而没有指定两者之间的连续摄像机移动时，SeeDance 默认为 *重新构图* 相同的摄像机位置（缩放或裁剪）。结果读作跳跃缩放，而不是真正的切换——背景相同，角色在不同尺寸。

**解决方法**：在一个表演中，除了第一个镜头之外，每个镜头都必须声明一个 `transition_from_prev` 字段——对从上一个镜头构图到这个镜头的 *连续摄像机运动* 的一行描述。SeeDance 然后必须渲染一个实际的空间穿越，这意味着在剪辑中角色的不同部分出现在背景中。

模式：命名摄像机的起始位置，命名它最终到达的位置，命名连接它们的动作。有效的移动动词：推近，拉远，推入，环绕，弧线，滑行，摇上，摇下，仰视，俯视，向左/右漂移。

示例：

| `transition_from_prev` | 效果 |
|---|---|
| "摄像机拉远并左弧线，露出她身后的砖墙和站立式办公桌" | 真实的空间变化——不同背景部分 |
| "推过手机屏幕进入她脸部的更近构图——房间在她身后模糊" | 使用摇焦 + 推近的连续运动 |
| "摄像机以稳定距离顺时针环绕她，捕捉到新侧面的白板和植物" | 环绕揭示新背景 |
| "从她拿着手机的手部拉远到中景，然后向右漂移到窗户光线下" | 两步连续移动 |
| ❌ "切换到中景" / ❌ "现在我们看到她在中景" | 这些不描述运动——SeeDance 落回相同位置的重新构图 |

**一个表演中的第一个镜头没有 `transition_from_prev`**——它确立了构图。该表演中的每个后续镜头都得到一个。

**SeeDance 在单个 15 秒剪辑中可以在明确提示时进行硬切。** 在时间编码的子镜头之间写 `Hard cut:`（而不是 `Transition:`）以进行不同的构图变化——SeeDance 尊重这一点并渲染真实的切换，而不是重新构图。保留 `Transition:` 用于连续运动的转场，你想让摄像机在构图之间滑行。模式：硬切感觉像真实的剪辑作品（不同的构图，不同的摄像机角度，不同的表演能量）；转场感觉像单个长镜头的移动。

### [3c.1] 表演能量底线——每个 beat 需要明确的身体动作

常见的失败模式：beats 仅用面部微表情编写（"轻微点头"，"眉梢一挑"，"眼神锁定摄像机"）。SeeDance 渲染为近乎冻住的创始人——眼睛几乎不动，没有存在感。结果读作"静态，冻住，没有兴奋。"

规则：每个 beat 的 `physical` 字段至少需要一个：
- 手或手臂手势（张开手掌，数手指， dismissive 挥动，指向自己/摄像机，手托胸口，手臂大幅挥动，手托太阳穴思考）
- 躯干移动（向前倾，向后倾，轻微身体转动，肩部移动）
- 头部动作大于微表情（向左/右转动并返回，倾斜 8°+，缓慢摇头，节奏性点头）
- 方向性眼动结合眉毛运动（向下看然后快速看向摄像机，等等）

仅面部 beat 只有在以下情况下才可接受：
- 在说出的话句之间的沉默 `(beat)` 标记（这些是*故意*静止的——持久的凝视才是重点）
- 在表演已经移动的镜头末尾的最终落地 beat（摄像机做工作）

编写 SeeDance 提示时，确保组装的 "Acting beats" 块读起来身体密度高——如果你扫视它并看到五行 beat 都写着 "轻微点头" 或 "小微笑" 而没有其他动作，创始人会看起来冻住。重写时加入更大的动作。

### [3d] 脚本 JSON

```json
{
  "product_type": "<从步骤 [2] 获得>",
  "character_voice_profile": "休闲自信，像在咖啡厅向朋友解释产品。默认略带微笑。关键揭示时眉梢一挑。思考时手托下巴，大声宣告时手势展开平放。停顿时保持眼神接触而非填充沉默。妙语直白落地，小微笑在之后才到来。",
  "segments": [
    {
      "act": 1,
      "shots": [
        {
          "type": "A",
          "asset_index": null,
          "beats": [
            { "text": "助手非常出色。", "emotion": "断言的尊重——像她真的这么认为一样", "physical": "温和直接的眼神接触，轻微点头" },
            { "text": "(beat)", "physical": "细微的微笑到来，眼神锁定摄像机" },
            { "text": "但它有点...", "emotion": "俏皮的转折，省略号悬停", "physical": "轻微头部向右倾斜，省略号悬停时眼神短暂向上飘" },
            { "text": "无形的。", "emotion": "平板落地", "physical": "眼神回到摄像机，单手 dismissive 摇头" }
          ]
        },
        {
          "type": "B",
          "asset_index": null,
          "transition_from_prev": "摄像机缓慢推近从中等构图进入更紧的特写，略微向右偏轴，以便在背景中看到砖墙和窗户光线的不同切片",
          "beats": [
            { "text": "没有脸。没有声音。没有自己的个性。", "emotion": "顿挫的 dismissal", "physical": "每个词都伴随小摇头，'个性'时眉梢一挑" },
            { "text": "(beat)", "physical": "持久的凝视，眼神锁定摄像机，软微笑开始到来" },
            { "text": "只是一个等待命令的空助手。", "emotion": "平板，略带无奈的平板", "physical": "中性表情" },
            { "text": "(beat)", "physical": "软自信的微笑到来，身体开始前倾" },
            { "text": "这即将改变。", "emotion": "坚定的信念，转折", "physical": "眼神锁定，'改变'时单手自信点头" }
          ]
        }
      ]
    },
    {
      "act": 2,
      "shots": [
        {
          "type": "C",
          "asset_index": 0,
          "reveal_beat": "角色将手机举到胸部高度朝向摄像机，屏幕面向观众。屏幕是一个干净的空白中性占位符，在步骤 [5.5] 中保留用于真实产品 UI 叠加；不要渲染可读的 UI 文本，品牌标志或伪造的应用界面。",
          "beats": [
            { "text": "遇见 API。", "emotion": "安静的介绍，带着自信", "physical": "手机抬起朝向摄像机，眼神从屏幕转向镜头" },
            { "text": "一个工作流程，给你的产品一个脸，一个声音，一个故事。", "emotion": "温暖稳定的构建", "physical": "空闲手逐个手指计数——脸，声音，故事" }
          ]
        },
        {
          "type": "A",
          "asset_index": null,
          "transition_from_prev": "摄像机从手机拉远并略微左弧线，手机随着镜头出画，我们现在聚焦于一个中景的镜头，背景中可见书架和白板，但与镜头 D 的一侧不同",
          "beats": [
            { "text": "以及制作视频、图片、音频的能力。", "emotion": "扩展承诺", "physical": "每项内容手势展开更宽" },
            { "text": "都在聊天中。", "emotion": "落地的标签", "physical": "手势平放，轻微微笑到来" }
          ]
        }
      ]
    },
    {
      "act": 3,
      "shots": [
        {
          "type": "D",
          "asset_index": null,
          "beats": [
            { "text": "设置只需三十秒。", "emotion": "事实性的安慰", "physical": "走过书架，短暂瞥一眼笔记本电脑" },
            { "text": "打开仪表板，粘贴 URL，登录。", "emotion": "快速节奏清单", "physical": "数三个手指时边走边说" }
          ]
        },
        {
          "type": "E",
          "asset_index": 1,
          "reveal_beat": "手部特写。屏幕是一个干净的空白中性占位符，在步骤 [5.5] 中保留用于真实产品 UI 叠加；不要渲染可读的 UI 文本，品牌标志或伪造的应用界面。",
          "transition_from_prev": "摄像机快速推近她的肩膀上方，落在她手部和手机紧实的特写上，阁楼背景完全模糊",
          "beats": [
            { "text": "你的应用成为向导。", "emotion": "软惊喜的揭示", "physical": "对手机微笑，然后看向摄像机，眼神温暖" }
          ]
        },
        {
          "type": "A",
          "asset_index": null,
          "transition_from_prev": "摄像机从手机拉远并仰视，找到中景中的她的脸，背景中可见书架和下午光线的另一侧，与镜头 D 不同",
          "beats": [
            { "text": "或者你创造的任何人。", "emotion": "休闲的旁白", "physical": "小耸肩，轻微微笑" },
            { "text": "(beat)", "physical": "持久的凝视，微笑淡入温暖真诚" },
            { "text": "现在像对待一个人一样和她交谈。", "emotion": "真正的重点——安静的信念", "physical": "'人'时单手点头，眼神锁定" }
          ]
        }
      ]
    },
    {
      "act": 4,
      "shots": [
        {
          "type": "F",
          "asset_index": null,
          "beats": [
            { "text": "技能捆绑在一起。", "emotion": "休闲自信，介绍清单", "physical": "下巴轻微上扬，知道ingly 的表情" },
            { "text": "播客。解释视频。UGC 广告。", "emotion": "节奏性的三拍清单", "physical": "每个都伴随小点头，'UGC' 时眉梢一挑" },
            { "text": "都在聊天中。", "emotion": "落地的标签", "physical": "手势平放，轻微微笑到来" }
          ]
        },
        {
          "type": "B",
          "asset_index": null,
          "transition_from_prev": "摄像机缓慢推近从更宽的品牌背景构图进入亲密的中等特写；环境退化为软焦，角色占据更多画面",
          "beats": [
            { "text": "所以停止与通用 AI 搏斗。", "emotion": "直接的地址，低调的挑战", "physical": "单眉一挑，轻微头部倾斜" },
            { "text": "(beat)", "physical": "持久的凝视，微笑增长" },
            { "text": "给它一个真实的存在。", "emotion": "品牌标语，带着确定性说", "physical": "略微前倾朝向摄像机，眼神锁定" },
            { "text": "从 example.com/slash/demo 开始。", "emotion": "温暖的 CTA，邀请", "physical": "软自信的微笑，'demo' 时单手收尾点头" }
          ]
        }
      ]
    }
  ]
}
```

**每镜头资产分配规则**：
1. **对于数字产品**：只有镜头 `C` 和 `E` 获得一个 `asset_index`（手机揭示时刻）。这些是步骤 [5.5] 的叠加指针，并且不包含在 Seedance 参考图像数组中。其他镜头显示创始人，没有特定的 UI 参考。
2. **对于实体产品**：任何在画面中显示产品的镜头都获得一个 `asset_index`。资产是真实产品外观的来源。表演可以跨多个镜头重用同一资产，或每镜头显示不同资产以展示产品多样性。
3. **对于服务产品**：任何地方都没有 `asset_index`——脚本依赖于对话 + 环境。

每个非空的 `asset_index` 必须来自 `usable_product_assets[*].asset_index`。永远不要将仅包含标志、英雄、信息图表、抽象品牌或 `other` 资产索引分配给产品揭示镜头。当在对话中使用产品细节时，优先使用 `usable_product_assets[*].analysis.key_elements` 和 `usable_product_assets[*].analysis.visible_copy`，以便说出的推销与屏幕上显示的真实产品工件保持一致。

**每表演参考图像数组** = 该表演镜头的 Seedance 安全资产 URL 的并集。数字 `digital_screen` 资产不是 Seedance 安全的；它们仅在步骤 [5.5] 中作为叠加保留。在 SeeDance 提示中，通过其在数组中的位置引用非数字资产，如 `@Image3`，`@Image4`（位置 3+——位置 1 和 2 始终是角色 + 环境参考）。编排器在步骤 [5] 构建提示时计算此映射。

**对话规则**——所有 4 个表演中总计必须朗读 55-60 秒（~150 wpm = ~150 个单词总计，~37 个单词每个表演）。简短，有力，可说。避免 em-dashes（创始人不说它们）。使用自然缩写。**参考用户实际的产品功能**（从 `usable_product_assets[*].analysis.key_elements` 和 `usable_product_assets[*].analysis.visible_copy` 绘制），而不是编造的。

| 模式 | 错误（直译） | 正确（改写为 TTS 格式） |
|---|---|---|
| 以 `-i` 结尾的名字 | "Ari" → "ah-REE" | **"Airy"**（或 "Tess" / "Mae" / "Sam"——按发音拼写） |
| 拼写不常见的名字 | "Aoife" → 混乱 | **"Eefa"**（按发音拼写） |
| 来自 `state.brand.name` 或 `brief.product_name` 的非发音产品/品牌名 | "Vercel" → "Verkon"；"Linear" → "Lineer" | 创建仅用于 TTS 的发音别名，例如 **"ver-SELL"**，在对话 / `<<<voice_1>>>` 中每次提及该品牌时使用此别名。 |
| 需要逐字母拼读的缩写 | "UGC" → "uhg" / "ugg"；"MCP" → "mehp" / 静音 | **"U G C"** / **"M C P"**（字母间用单个空格分隔） |
| 作为单词读出的缩写 | "NASA" → "nasa" ✅（已正确）；"IKEA" → "ikea" ✅ | 保持原样 |
| 域名中的点号 | "example.com" → "examplecom" | **"example dot com"** |
| URL 中的斜杠 / 路径 | "example.com/API" → "examplecom-api" | **"example dot com slash A P I"** |
| 符号 | "$50" → 静音；"@user" → "at user" 或静音 | **"fifty bucks"** / **"at-sign user"** |
| 格式不常见的数字 | "2026" → 有歧义 | 年份用 **"twenty twenty-six"**；整千数字用 **"two thousand"** |

对于品牌如何发音某个缩写（NASA vs N.A.S.A.）或不明显的产品名存在疑问时，请查阅品牌官网 / 官方视频。对于不明确的缩写，默认使用逐字母拼读；对于非发音名称，使用简单的发音别名。对于包含品牌名的域名，将两种改写方式结合：`Vercel.com` 在 `<<<voice_1>>>` 载荷中变为 `ver-SELL dot com`。

**完整示例** —— 原始剧本 vs TTS 安全改写：

```
Original:  "UGC ads. All from chat. Launch the API. Start at example.com/API."
TTS-safe:  "U G C ads. All from chat. Launch the A P I. Start at example dot com slash A P I."

Original:  "Your app becomes Ari."
TTS-safe:  "Your app becomes Airy."

Original:  "Vercel ships at vercel.com."
TTS-safe:  "ver-SELL ships at ver-SELL dot com."
```

改写仅保留在*对话文本*中——你的剧本 JSON 的 `dialogue` 字段会原样流入 SeeDance 提示词，然后进入每个 `<<<voice_1>>>` 块。视觉表面保持原始的标准拼写：`state.brand.name`、`brief.product_name`、产品 UI 叠加层、文字标识、尾版文字、URL、文件名和 QA 预期值必须保持不变。切勿用发音别名替换确定性视觉文本。

## 镜头类型参考

每个镜头根据 `product_type` 有不同变体。选择与你的情况匹配的变体。

⚠️ **避免使用 SeeDance 会字面理解的影视行业镜头术语。** SeeDance 将命名镜头类型视为字面配方——包括该术语所隐含的*任何被暗示的主体*。具体而言：
- ❌ "Two-shot"（双人镜头）→ 会在画面中增加第二个人（该术语在影视中意为"包含两个主体的镜头"，但 SeeDance 只看到"two" + "person"）。
- ❌ "Three-shot"（三人镜头）——同样的陷阱。
- ❌ "Over-shoulder" / "OTS"（过肩镜头）→ 会在前景添加一个幻象的肩膀/后脑勺，让角色与之互动。角色会*朝向那个幻象人物*表演，而非朝向镜头。
- ❌ "Master shot"（全景总镜）——可能被误读为"the master / their boss"（大师/老板）。
- ✅ "Medium shot"（中景）、"Close-up"（特写）、"Wide"（远景）是安全的；它们在日常用语中常见。

所有情况的修复方法都是**用普通语言描述摄像机看到什么**，而非使用暗示额外主体的影视词汇。示例：
- "Over-shoulder reveal"（过肩揭示）→ "the character holds her phone up toward camera, screen facing the viewer at chest height"（角色将手机举向镜头，屏幕面向观众，位于胸部高度）
- "Two-shot"（双人镜头）→ "wide framing of the character with [product/logo/environment] in frame"（包含[产品/标志/环境]的宽幅取景，角色在其中）
- "POV"（第一人称视角）→ "low camera angle from the character's eyeline"（从角色视平线的低机位角度）

| 镜头 | 所有变体 | 运镜 |
|------|-------------|--------|
| A | 中景，腰部以上，角色居中。（画面中无产品，或者如果 `physical_apparel`：角色穿着品牌的T恤——将素材作为参考传入并添加 reveal_beat。） | 缓慢细微的推近（dolly in） |
| B | 中近景，胸部以上，亲密感。（无产品，或者如果 `physical_apparel`：T恤从领口可见，引用素材。） | 轻柔的手持呼吸感运动 |
| C | **手机/产品展示——直接面向镜头。** `digital` → 角色在胸部高度将手机举向镜头，屏幕面向观众，使用一个空白中性屏幕占位符供步骤 [5.5] 叠加真实 UI。（不要写"过肩镜头"——该词汇会触发幻象人物。）`physical_apparel` → 角色将T恤举向镜头，印花面向观众，匹配 @ImageN。`physical_object` → 角色将产品举向镜头。`consumable` → 角色将包装举向镜头。 | 缓慢向所持物品推近 |
| D | 远景 + 环境，全身置于开阔空间。（无特定产品展示时刻。） | 缓慢跟踪镜头，视差景深 |
| E | **特写揭示。** `digital` → 手持手机的特写，屏幕为空白中性占位符，供步骤 [5.5] 叠加真实 UI。`physical_apparel` → 手持T恤面料的特写，设计清晰可见。`physical_object` → 手中产品的特写，细节镜头。`consumable` → 使用/食用/饮用产品的特写。 | 细微的焦点转换（rack focus），缓慢仰摇 |
| F | **品牌环境镜头。** 较宽的取景，角色周围有产品/环境背景。`digital` → 角色处于品牌风格环境中，无可读产品 UI 或文字标识。`physical_apparel` → 角色穿着品牌T恤，印花在画面中部清晰可见。`physical_object` → 角色与桌/架上的产品。 | 缓慢拉远，轻柔变焦 |

## [4] 创始人 + 自定义地点参考图

在任何 SeeDance 调用之前准备 `character_url`：

- 如果 `founder_photo` 是 HTTPS URL，设置 `founder_photo_url = character_url = founder_photo`。
- 如果 `founder_photo` 是本地路径，使用 `upload_asset` 上传，然后设置 `founder_photo_url = character_url = public_url`。
- 如果 `founder_photo` 是 `generate`，调用 `generate_image` 并使用返回的 URL：

```
generate_image(
  prompt: "<founder vibe>. Professional founder portrait, clean studio lighting, sharp focus on face, confident expression, suitable as character reference for video generation.",
  aspect_ratio: "3:4",
  resolution: "2K"
)
```

仅当用户提供了自定义地点时处理地点：

- 如果 `location_image_url` 是 HTTPS URL，设置 `location_url = location_image_url`。
- 如果是本地路径，使用 `upload_asset` 上传并设置 `location_url = public_url`。
- 如果是文字描述，使用 `generate_image` 生成自定义地点参考图。
- 如果未提供自定义地点，此处不做任何操作。步骤 [4.5] 会在 `state.brand` 存在后生成默认的品牌色背景。

将生成的 URL 保存到 `state` 中。如果 SeeDance 后来因内容策略拒绝创始人参考图，请参见"已知基础设施问题"——使用更强的风格化重新生成。

## [4.5] 品牌套件导入（始终执行——Stage 0 保证存在 `brand_kit_path`）

`brand_kit_path` 是 Stage 0 的必需项——由用户提供，或先通过 `build-a-brand` 构建。解析一次后在尾版和下三分之一字幕条中复用。如果在交互模式下文件夹缺失，请用户先提供或重建品牌套件再继续。在非交互快速通道中，先尝试 `build-a-brand --quick` 分支；如果无法生成套件，停止一次并给出一个紧凑的缺失字段列表。

首选来源是存在时的 `brand.json`。否则从 `build-a-brand` 导出中提取：
- `brand.md` 中的名称、标语、语气、字体名称和标志描述。
- `tokens/tokens.json` 中的颜色和字体 token。
- `logo/` 中的文字标识、符号/图标和组合标识素材。

提取到 `state.brand`：

| `state.brand` 字段 | 来源 | 备注 |
|---|---|---|
| `name` | `brand.json.name` 或 `brand.md` 快速参考 | 品牌显示名称 |
| `wordmark_path` | `logo.wordmark.path` 或最佳位图 `logo/wordmark/*.{png,jpg,jpeg,webp}` | 通过 `upload_asset` 上传本地位图素材，将 `public_url` 保存为 `state.brand.wordmark_url`；不要上传 SVG |
| `icon_url` | `logo.icon_mark.path` 或最佳位图 `logo/symbol/*.{png,jpg,jpeg,webp}` | 通过 `upload_asset` 上传本地位图素材，将 `public_url` 保存为 `state.brand.icon_url`；不要上传 SVG |
| `colors.primary` | 色板角色 `ink_primary`、`surface_dark` 或 `tokens.color.text` | 文字和边框颜色 |
| `colors.surface` | 色板角色 `surface_page_bg`、`surface_white` 或 `tokens.color.background` | 页面/背景颜色 |
| `colors.accent` | 色板或 `tokens.color.primary` 中的 CTA/主品牌色 | 尾版 CTA 胶囊按钮背景 + 下三分之一字幕条强调色 |
| `colors.highlight` | 色板或 tokens 中的次级亮色/高光色 | 下三分之一字幕条边框 / 高亮 |
| `fonts.display_family` | 排版展示 token 或 `brand.md` | 可用则直接使用；回退到 Space Grotesk |
| `fonts.text_family` | 排版正文/文本 token 或 `brand.md` | 回退到系统无衬线字体 |
| `fonts.mono_family` | 排版等宽 token（如存在） | 回退到 Space Mono |

**当品牌套件素材为本地文件时，上传步骤是必须的。** 没有公开的 wordmark/icon URL，`render_html_animation` 渲染的 HTML 无法访问它们。仅使用 MCP `upload_asset` 流程处理位图标志文件，并将返回的 `public_url` 值保存到 `state.brand`。`upload_asset` 会拒绝 `image/svg+xml`；如果最佳标志是 SVG，请选择品牌套件中同级的 PNG 导出文件，或通过 `html_to_png` 将 SVG 内联在 HTML `<svg>` 块中将其栅格化为 PNG，使用返回的 PNG `public_url`。

**品牌色背景默认地点** —— 当步骤 [4] 未设置 `location_url` 时，使用 `state.brand.colors.accent` 通过 `html_to_png` 渲染纯色 PNG。匹配所需的视频宽高比，以免参考图后续被裁切：

| `aspect_ratio` | 背景尺寸 |
|---|---|
| `16:9` | 1920×1080 |
| `9:16` | 1080×1920 |
| `1:1` | 1080×1080 |

将返回的 `file_url` 保存为 `location_url`。这将产生干净的影棚拍摄美学——角色站在品牌自身强调色的纯色无缝背景前，无家具或背景细节。这比 AI 生成的办公室场景更可靠，SeeDance 渲染也更稳定。

```
html_to_png(
  html: "<body style='margin:0;background:{accent}'></body>",
  format: "png",
  mode: "sync",
  raster_options: { viewport_px: { width: W, height: H }, device_scale: 1 }
)
# Save result.file_url as location_url
```

## [5] 并行生成 4 个 SeeDance 幕

**关键**：步骤 [5] 需要 `generate_reference_video`（多参考图）。本技能提示词模板中的 `@Image1` / `@Image2` / `@Image3` 标记**仅由** `generate_reference_video` 解析。如果你误调了 `generate_video`（单图 i2v），`@ImageN` 标记会被静默忽略，Seedance 会仅凭提示词文本幻象出 UI，通常会拼错产品名称。在触发任何付费视频生成之前，停下来修正工具调用。

对于 `product_type: "digital"`，这现在是风格/手势生成步骤，而非最终可读 UI 步骤。不要要求 Seedance 拼出产品名称、渲染可读的品牌文字标识、或复现产品屏幕文案。手机揭示必须要求使用空白中性屏幕占位符，因为真实产品 UI 在步骤 [5.5] 中合成。不要在 `reference_images` 中传入 `digital_screen` 素材；任何 `digital_screen` 素材索引仅是步骤 [5.5] 的叠加指针，即使混合运行或显式非数字运行也包含实体素材。

对于每一幕，**收集该幕中所有镜头的 `asset_index` 值的并集**来构建 `reference_images` 数组：

```
act_asset_indices = unique(shot.asset_index for shot in act.shots if shot.asset_index !== null)
act_asset_entries = usable_product_assets.filter(entry.asset_index in act_asset_indices)
if act_asset_entries.length !== act_asset_indices.length: stop; a shot references an unusable/missing asset_index
seedance_asset_entries = act_asset_entries.filter(entry => entry.asset_type !== "digital_screen")
act_asset_urls    = [entry.asset_url for entry in seedance_asset_entries]
reference_images  = [character_url, location_url, ...act_asset_urls]
```

素材条目在 `reference_images` 中的位置决定了其 `@ImageN` 标记（位置 1、2 分别是角色 + 地点；可用产品素材从位置 3 开始）。编写提示词时，将每个非数字镜头的 `asset_index` 映射到其对应的 `seedance_asset_entries` 位置。对于任何 `digital_screen` 素材，不要在 Seedance 提示词中引用 `@ImageN` 标记；使用空白手机屏幕占位符的语言，让步骤 [5.5] 消费原始的 `act_asset_entries` 条目。

### 提示词模板

**通过 `@Image1` 参考指代角色，而非描述性提示词文本。** 当提示词同时写了"young creative streetwear founder"而 `@Image1` 是角色参考时，两个描述可能互相冲突——SeeDance 可能试图同时满足两者而编造一个第二个人物。地点和 `@Image2` 适用同样的规则。让参考图承载视觉身份。

每一幕的提示词有三层，从上到下：

1. **角色 + 地点身份**（始终是相同的开头行）。
2. **角色声音**——幕提示词逐字重复 `script.character_voice_profile`。这使演员的人格贯穿每个镜头。
3. **逐镜头块**——每个镜头获得其构图（或如果定义了 `reveal_beat` 则用 reveal_beat），然后一个基于镜头 `beats[]` 构建的逐行"表演节拍"列表，然后是 `<<<voice_1>>>` 内的对话。

⚠️ **开头行、`WARDROBE LOCK:`、`Background context:`、`<<<voice_1>>>`、`Transition:` / `Hard cut:`，以及结尾的 `Native lip-synced dialogue audio, no music overlay.` 行都是承重的**——每一行都在文档底部的 `## Load-bearing phrases` 中记录了它所防止的具体故障模式。改写其中任何一行都会静默破坏配方（字面背景、歌词演唱、跳变焦、服装漂移等）。保留它们原样；周围的连接性文字由你来撰写。

模板：

```
The character (matching @Image1) in a setting whose visual style, palette, lighting and materials match @Image2.

CHARACTER VOICE: {script.character_voice_profile}
WARDROBE LOCK (verbatim across all 4 acts): {script.wardrobe_lock}

Shot {first}: {if shot.reveal_beat exists: shot.reveal_beat ELSE: composition + camera from Shot table}. Background context: {distinct physical position in the space — which wall / window / feature is behind the character}.
Acting beats:
  • "{beat[0].text}" — {beat[0].emotion}; {beat[0].physical}.
  • (silence) — {silence beat physical}.
  • "{beat[N].text}" — {beat[N].emotion}; {beat[N].physical}.
<<<voice_1>>>{joined beat texts excluding (beat) markers, with periods and commas as written}<<<voice_1>>>

[If 2+ shots in this act:] Transition: {shot[1].transition_from_prev}.
Shot {second}: {composition or reveal_beat}. Background context: {a DIFFERENT physical position from Shot {first} — different wall / different angle / different background feature}.
Acting beats: ...
<<<voice_1>>>...<<<voice_1>>>

[If 3 shots:] Transition: {shot[2].transition_from_prev}.
Shot {third}: ... Background context: {a THIRD distinct physical position — must be visually different from Shots {first} and {second}}.

Native lip-synced dialogue audio, no music overlay.
```

模板说明：
- 以 **"匹配 @Image1 的角色在视觉风格与 @Image2 相符的场景中"** 开头——绝不能是 "在匹配 @Image2 的地点内"。SeeDance 会根据 @Image2 中的文字描述背景，如果你说 "在地点内"——参见已知基础设施缺陷。
- 不要用散文描述角色——SeeDance 从 `@Image1` 中读取视觉身份。例外：通过 `WARDROBE LOCK` 行明确锁定衣橱（例如："整个 4 个场景都穿着相同的煤灰色连帽衫搭配深色乐队 T 恤"）。仅 @Image1 无法跨不同的 15 秒世代锁定衣橱。
- 不要添加与参考资料相矛盾的美学形容词。如果 `@Image1` 是 3D 皮克斯风格的角色，不要在任何提示中添加 "照片逼真"。
- **角色声音 + WARDROBE LOCK 行在每个提示中只出现一次，在镜头之前**。它们为 SeeDance 初始化演员的整体氛围和服装连续性。
- **每个镜头块都包含一条 `Background context:` 行**，描述空间中的一个独特物理位置——不同的墙壁、不同的窗户、与其他镜头（在此场景中）以及理想情况下与其他场景不同的背景特征。这迫使 SeeDance 渲染场景多样性，同时将品牌美学锚定在 @Image2 上。
- **`(beat)` 标记保持在 `<<<voice_1>>>` 负载之外**。它们只是动作指示——对话文本中句子之间的自然停顿就是它们发生的地方。
- **场景中第一个镜头之后的每个镜头都得到一个 `Transition: …` 行**，由 `shot.transition_from_prev` 构建。这叙述了镜头之间的相机移动，迫使 SeeDance 渲染真实的空间运动（角色身后房间的不同部分），而不是一个没有动机的重新构图，看起来像跳跃变焦。

### 示例工作——`physical_apparel`，第 2 场景（带声音和停顿）

第 2 场景有镜头 `[C, A]`。镜头 C 有 `asset_index: 0` 并有一个关于搜索历史 T 恤的揭示停顿。镜头 A 没有资产索引。资产 0 = `@Image3`。角色声音配置文件是来自步骤 [3a] 的街头服饰创始人示例。

```
匹配 @Image1 的角色在视觉风格、调色板、照明和材料与 @Image2 相符的场景中。

角色声音：敏锐的干幽默。快速地说，句子简短，突然停顿。默认轻微的微笑，一只眉毛抬起。在痛点上翻白眼。在妙语连珠时露出淘气的微笑，但立即消失。双手基本保持静止——脸部做所有工作。
衣橱锁定：在整个 4 个场景中始终穿着相同的煤洗品牌图形 T 恤，搭配未扣上的靛蓝色牛仔 chore 外套。

镜头 C：角色将煤洗图形 T 恤举向相机，平放在胸高。衬衫设计完全匹配 @Image3——'我看到了你的搜索历史'，带有粗体白色字体的震惊猫插图。精确匹配图案，不要虚构。相机：缓慢的横向弧形摇摄朝向眼线。背景上下文：站在阁楼右侧的砖墙附近的服装架旁，来自相机左侧的柔和正午窗户光线。
动作停顿：
  • "你知道那个你差点输入的东西吗？"——知道低声指责；'差点输入'时眉毛抬起，轻微倾斜头部。
  • "那个奇怪的搜索？"——保持表情，眉毛保持抬起，暗示微笑出现。
  • (沉默)——停顿发生，微笑增长，眼睛看向镜头。
  • "你的猫看到了。"——淘气的冷面；稍微抬高衬衫，单次自信点头。
<<<voice_1>>>你知道那个你差点输入的东西吗？那个奇怪的搜索？你的猫看到了。<<<voice_1>>>

过渡：相机从持有的衬衫中拉回，略微向左弧形，衬衫随着我们结束中景镜头而离开画面，现在可以看到服装架和砖墙。
镜头 A：中景，腰部以上，角色居中，看向相机。相机：缓慢的微妙推入摇摄。
动作停顿：
  • "我们把它做成了 T 恤。"——事实揭示；眉毛抬起，轻微微笑出现。
  • "——带态度的图形 T 恤。"——品牌行标点；在'态度'上露出微笑，眼睛保持。
<<<voice_1>>>我们把它做成了 T 恤——带态度的图形 T 恤。<<<voice_1>>>

原生唇同步对话音频，无音乐叠加。
```

### 镜头间物理产品一致性

对于 `physical_apparel`，如果角色在多个场景中**穿着**品牌的 产品（例如，没有特定产品揭示但角色仍在品牌 T 恤中的场景），选择一个英雄衬衫资产，并使用提示语言如 *"角色穿着来自 @Image3 的 T 恤——图案完全匹配"* 将其传递给这些场景。否则 SeeDance 会发明一件看起来通用的衬衫，这将破坏资产覆盖目标。

### 并行发射所有 4 个场景——每个场景 3 个子镜头

在单个工具批量中并行发射所有 4 个场景。每个场景提示应包含 3 个时间编码的子镜头；单个 15 秒镜头剪辑渲染为静态、冻结的创始人，无论提示多么详细。如果一个运行看起来"非常静态，没有肢体语言，相机工作无聊"，修复方法是将每个场景分解为提示中的 3 个时间编码的子镜头。

**默认分解：每个场景 3 个子镜头**，按对话密度大小（例如 `(0-4s)`，`(4-9s)`，`(9-15s)`）。

每个子镜头需要：
1. **不同的相机构图**——绝不能有两个连续的子镜头使用相同的镜头类型。混合中景/特写/广角/低角度。用户将多样性视为制作价值。
2. **不同的相机运动**——推入、拉回、横向弧形、轨道、手持、静态保持、聚焦滑动。不全是"缓慢推入"。
3. **空间中不同的物理位置**——参见"已知基础设施缺陷"中的位置参考规则。每个镜头必须描述角色身后不同的墙壁/窗户/特征，以便 SeeDance 在空间中移动，而不是重复一个字面上的背景。
4. **每个停顿一个有活力的物理动作**——参见上文 [3c.1]。手势、倾斜、转头、肩膀移动。没有仅面部动作的停顿。
5. **该窗口的对话子部分**，用 `<<<voice_1>>>...<<<voice_1>>>` 令牌在镜头块内包裹。

SeeDance 发射模式：

```
generate_reference_video(
  provider: "seedance",
  resolution: "1080p",
  aspect_ratio: "16:9",
  duration: 15,
  seed: 101,                   # 每个场景唯一（101, 202, 303, 404）——打破幂等性缓存
  sound: true,                 # 来自每个 <<<voice_1>>> 块的原生唇同步
  reference_images: [character_url, location_url, ...本场景的资产],
  prompt: <完整提示——见上文模板，3 个时间编码的子镜头内联>
)
# ... × 4 场景，全部在相同消息中 ...
```

说明：
- 每个场景在 SeeDance 上运行约 3-8 分钟。如果生成异步完成，请遵循 MCP 工具返回的状态句柄，直到场景达到终止状态。
- 完整提示（开头行 + CHARACTER VOICE + 3 个子镜头与动作停顿 + 每个镜头的 `<<<voice_1>>>` + 过渡行）放在单个 `prompt` 参数中。SeeDance 没有 `shots:[]` 数组——多镜头结构编码在散文中。
- 使用唯一种子（101, 202, 303, 404），以便看起来相同的调用不会哈希到相同的缓存任务 ID。`seed` 参数仅限 seedance。

将返回的 4 个 URL 按提交顺序保存为 `act_urls = [act1, act2, act3, act4]`。

## [5.5] 确定性数字 UI 叠加

此步骤在所有四个 Seedance 场景可用后运行，并在步骤 [6] 之前运行。为提高效率，首先运行下文的跨场景身份 QA，并使用最终接受的 `act_urls`；如果身份 QA 后来重试某个场景，丢弃旧的叠加输出并重新运行此步骤。其工作是为数字产品揭示提供像素级基础：观众看到的手机/产品屏幕视觉来自真实的捕获屏幕截图或渲染文字标志，而不是来自 Seedance。

如果 `product_type !== "digital"`，设置 `ui_grounded_act_urls = act_urls` 并继续。

如果 `product_type === "digital"`：

1. 从每个脚本镜头中构建 `digital_reveal_shots`，其类型为 `C` 或 `E`。每个脚本 `C` 或 `E` 数字揭示必须具有非空的 `asset_index`，并且该索引必须解析为 `usable_product_assets` 中的 `digital_screen` 条目。如果任何脚本 C/E 数字揭示有 `asset_index: null`，停止并显示脚本镜头；不要继续到 Seedance concat 或复制原始 `act_urls`。从验证的揭示镜头构建 `digital_reveal_plan`。每个计划的叠加存储：
   - `act`，`shot`，`asset_index`，`asset_url`
   - `visible_copy` 来自 `usable_product_assets[*].analysis.visible_copy`
   - `brand_name = state.brand.name`
   - 预期文本列表：确切的 `brand_name` 加上任何简短、可读的 `visible_copy` 短语对提案很重要

   如果 `digital_reveal_plan` 为空，停止并显示脚本镜头加上 `usable_product_assets`；不要无声地发送一个没有真实 UI 的数字产品视频。如果任何脚本 C/E 数字揭示指向缺失或非 `digital_screen` 资产，停止在组合之前。当数字揭示缺少其叠加时，不要复制原始 `act_urls`；只有没有数字揭示镜头的镜头才能通过不变。

2. 对于每个唯一的 `asset_url`，使用 `render_html_animation` 渲染 15 秒叠加剪辑，使用 `format: "mov"` 当需要 alpha 时。将返回的 URL 保存为 `ui_overlay_clip_url`。
   - HTML 应该将真实的屏幕截图/捕获 UI 放置在带有正确纵横比的圆角手机屏幕框架内。
   - 如果真实屏幕截图的品牌文字标志在缩放后太小而无法阅读，请包括一个确切的确定性文字标志行使用 `state.brand.name`；不要发明一个更短的别名。
   - 保持叠加背景透明或视觉隔离，以便它作为确定性手机/UI 叠加工作。

3. 使用 `edit_video_compose` 将叠加合成到每个计划的场景上：

```
edit_video_compose(
  base_video_url: act_urls[act - 1],
  overlays: [{
    video_url: ui_overlay_clip_url,
    position_px: <安全的手机屏幕或面板位置>,
    width_px: <足够大以供 OCR 读取品牌/产品 UI>
  }]
)
```

当生成的手机目标稳定时使用手机屏幕位置。如果手机目标不够稳定以干净地覆盖，使用稳定的叠加面板位置，不要覆盖创始人脸部或标题区域。将每个编辑结果保存到 `ui_grounded_act_urls[act - 1]`；未修改的镜头从 `act_urls` 复制通过。

4. 当合成通道后仍需要短确切的品牌标签时，调用 `edit_text_overlay` 在该场景上使用 `text: state.brand.name`。这仅用于确定性品牌拼写，不是标题。将更新后的 URL 保存回 `ui_grounded_act_urls[act - 1]`。

5. 在与 `extract_frame` 和 `analyze_media` 合并之前，对每个叠加揭示场景运行 OCR QA：

```
extract_frame(video_url: ui_grounded_act_urls[act - 1], time_s: <揭示镜头的中点>)

analyze_media(
  media: overlay_qa_frame_url,
  query: "OCR/读取产品 UI 或文字标志上所有可见文本。仅返回 JSON： {
    \"brand_name_visible\": \"yes\" | \"no\" | \"unclear\",
    \"brand_name_exact\": \"yes\" | \"no\" | \"unclear\",
    \"visible_copy_ok\": \"yes\" | \"no\" | \"unclear\",
    \"garbled_text\": string[],
    \"misspellings\": string[],
    \"verdict\": \"clean\" | \"degraded\" | \"catastrophic\"
  }.确切的预期品牌名称是 ${brand_name}。确切的预期 visible_copy 是 ${visible_copy}; visible_copy_ok: "yes" 仅当重要的预期 UI 文本存在/可读时，或当没有短 visible_copy 时。例如 Lineer, Figoff, 随机字母，格式错误的 UI 文本，或替换预期 visible_copy 的 AI-想象 UI 文本是 garbled/misspelled."
)
```

只有 `brand_name_visible: "yes"`，`brand_name_exact: "yes"`，`visible_copy_ok: "yes"`，和 `verdict: "clean"` 才能继续。如果 OCR 说品牌缺失、拼写错误、混乱，预期的 visible_copy 缺失/被替换，或 `verdict` 是 `degraded` / `catastrophic`，停止并显示 `overlay_qa_frame_url`，`ui_overlay_clip_url`，预期的 `brand_name`，预期的 `visible_copy`，和 QA JSON。不要继续到步骤 [6] 使用原始或 AI-想象的手机文本。

### 步骤 [6] 之前的跨场景身份 QA

在 `edit_concat` 之前，对单个可比较的视觉文物运行跨场景身份检查。目标是捕获创始人交换，以便在 60 秒身体已经拼接后可以重新生成，而不是之后。

1. 从每个场景的三个子镜头窗口中提取一个代表性帧。场景中间的一个帧不够；创始人交换可以在第一个或最后一个子镜头中发生，仍然可以通过。

```
identity_frame_times_s = [2, 7, 12]
for each act_urls[i]:
  for each time_s in identity_frame_times_s:
    extract_frame(video_url: act_urls[i], time_s)
# 保存为 act_identity_frames = [
#   { label: "场景 1 镜头 1", act: 1, shot: 1, time_s: 2, url: ... },
#   ...
#   { label: "场景 4 镜头 3", act: 4, shot: 3, time_s: 12, url: ... }
# ]
```

2. 使用 `html_to_png` 渲染一个身份接触表。使用 CSS `background-image: url(...)` 为每个远程图像。表单必须包括 13 个标记面板在一个图像中：`founder reference` (`founder_photo_url` / `character_url`)，然后 `场景 1 镜头 1`，`场景 1 镜头 2`，`场景 1 镜头 3`，通过 `场景 4 镜头 3`。将返回的文件保存为 `identity_contact_sheet_url`。

```
html_to_png(
  html: "<html>... founder reference ... 场景 1 镜头 1 ... 场景 1 镜头 2 ... 场景 1 镜头 3 ... 场景 2 镜头 1 ... 场景 3 镜头 1 ... 场景 4 镜头 3 ...</html>",
  format: "png",
  mode: "sync",
  raster_options: { viewport_px: { width: 2200, height: 1600 }, device_scale: 1 }
)
```

3. 在 `identity_contact_sheet_url` 上运行一个 `analyze_media` 调用：

```
analyze_media(
  media: identity_contact_sheet_url,
  query: "仅返回 JSON： {
    \"same_founder_as_reference\": \"yes\" | \"unclear\" | \"no\",
    \"same_founder_across_acts\": \"yes\" | \"unclear\" | \"no\",
    \"wardrobe_consistent_with_lock\": \"yes\" | \"unclear\" | \"no\",
    \"bad_act_numbers\": number[],
    \"bad_frame_labels\": string[],
    \"identity_observations\": string[],
    \"verdict\": \"clean\" | \"degraded\" | \"catastrophic\"
  }
  将 founder reference 面板与所有 12 个场景面板（场景 1 镜头 1 到场景 4 镜头 3）比较：检查脸、头发、年龄、体型和衣橱；不要将正常的姿势、表情、相机角度或照明变化视为身份漂移。"
)
```

如果无法渲染接触表，停止并显示接触表失败；不要继续使用未验证的身份。只有干净的 `yes` / `yes` / `yes` 身份 QA 才能继续。如果 QA 返回 `same_founder_as_reference: "no"` 或 `same_founder_as_reference: "unclear"`，`same_founder_across_acts: "no"` 或 `same_founder_across_acts: "unclear"`，`wardrobe_consistent_with_lock: "no"` 或 `wardrobe_consistent_with_lock: "unclear"`，`bad_act_numbers` 非空，`bad_frame_labels` 非空，或 `verdict: "degraded"` 或 `verdict: "catastrophic"`，不要继续到 concat。仅重试有问题的场景一次，使用相同的提示、相同的 `reference_images`，以及新的种子（`original_seed + 1000`）加上一句提示：`身份连续性是强制性的：整个场景中镜头内的创始人始终是 @Image1 的人。` 重试后，提取重试场景的所有三个帧时间，重建完整的接触表，并重新运行相同的 QA。如果任何 `act_urls` 条目在重试后更改，丢弃 `ui_grounded_act_urls` 和任何以前的叠加/OCR 证据，重新运行步骤 [5.5] 对最终 `act_urls`，然后在步骤 [6] 之前运行其 OCR QA。如果重试仍然失败跨场景身份 QA，停止并显示 `identity_contact_sheet_url`，有问题的场景 URL(s)，`bad_frame_labels`，和 QA JSON；不要发送一个拼接的视频，其中创始人不同。

### 时长下限和部分场景恢复

在步骤 [6] 之前，必须提供所有 4 个 act_urls。不要拼接部分 act 列表。

三个完成的 act 加上结尾卡片会产生一个约 50 秒的资产，这低于 55 秒的时长底线，并且不能报告为成功的创始人视频。

如果一个 SeeDance act 达到失败终端、达到 `cancelled` 状态，或者由长时间轮询合约终端或成功取消，而其他 act 已完成：
- 使用相同的提示、`reference_images`、`duration`、`sound`、`resolution` 和 `aspect_ratio` 重新尝试缺失的 act 一次，但使用新的种子（`original_seed + 1000`）。不要重新运行成功的 act。
- 如果重试完成，将那个 URL 插入原始 act 插槽，并继续使用 `act_urls = [act1, act2, act3, act4]`。
- 如果重试无法完成，停止并暴露上游 SeeDance 超时。你可以返回完成的 act URL 作为诊断预览，但不要交付部分拼接作为 `final_url`，不要称其为生产就绪，并且不要进行到步骤 [6]。

在其原始任务仍为 `queued`、`running` 或 `processing` 时，不要重新尝试停滞的 act。继续使用可见进度轮询它，然后在 15 分钟的总上限之前使用缺失 act 的重试之前调用 `task_cancel({task_id})`。

## [6] 将 act 拼接成 60 秒基础

```
edit_concat(video_urls=ui_grounded_act_urls)
```
保存为 `base_url`（60 秒，16:9，原生对话音频）。`ui_grounded_act_urls` 对于非数字产品等于 `act_urls`；对于数字产品它包含步骤 [5.5] 叠加揭示 act。当存在数字 UI 叠加计划时，不要将原始 `act_urls` 输入拼接。

## [7] 生成背景音乐 — INSTRUMENTAL，目标约 60 秒

**模式是固定的。声音是每个品牌的创意决策。** 使用 Kling 音频，因为它支持 `background: true`，并且 MCP 工作器现在处理长床间隙：它生成一个 10 秒的 Kling 种子，然后使用 ffmpeg 本地扩展循环/交叉渐变到请求的 60 秒。WHAT 种类/乐器/情绪放入提示是你的工作——选择一个符合品牌调性、创始人声音和产品的声音。不要逐字复制下面的钢琴示例；这只是可能的声音，不是模板。

### 固定模式（不要更改）：
- `provider: "kling-audio"`
- `mode: "text_to_audio"`
- `background: true`
- `duration_seconds: 60`
- 没有 `lyrics` 字段。Kling 仅使用提示。
- 没有第二个提供程序调用或手动平铺。MCP 工作器拥有单种子扩展路径。
- `prompt` 必须是 `<= 200` 个字符。Kling 使用验证代码 `1201` 拒绝更长的提示，所以保持风格快照简短。

### 创意决策（每个视频——从 `brief.tone` + 脚本氛围 + 产品背景中挑选）：

不同品牌的声音注册示例。不要使用这些字面意思——匹配你品牌的氛围：

| 品牌注册 | 音乐方向 | 声音调色板 |
|---|---|---|
| 技术/开发工具/B2B SaaS | 企业电影配乐，苹果主题平静 | 温暖的钢琴，柔和的合成器垫，稀疏的低频脉冲，80–90 BPM |
| 俏皮/街头服饰/消费 |低保真嘻哈，休闲节拍 | 灰尘鼓，爵士和弦刺，黑胶嘶嘶声，70–85 BPM |
| 颠覆性/边缘/金融科技/加密货币 | 极简电子，黑暗合成器浪潮 | 模拟合成器贝斯，侧链垫，半时间鼓点，90–100 BPM |
| 时尚/奢侈/生活方式 | 极简浩室，现代时尚电影配乐 | 过滤的浩室垫，柔和的 4 拍鼓点，法国触感和弦，100–110 BPM |
| 健身/能量/运动 | 驱动电子脉冲，健身注册 | 脉冲合成器贝斯，构建的音调，踩镲八分音符，110–125 BPM |
| 食物/酒店/咖啡馆 | 乐器温暖，独立民谣 | 指弹吉他，轻击小军鼓，轻柔的立式贝斯，80–95 BPM |
| 电影/品牌故事/纪录片 | 管弦乐配乐，希望的高潮 | 弦乐层，柔和的钢琴主音，膨胀的铜管，速度构建 |
| 游戏/开发工具/创作者工具 | 芯片音乐-现代混合，复古像素 | 方波主音，现代合成器垫，响亮的鼓，105–120 BPM |

不确定时：阅读 `brief.tone`（技术/休闲/俏皮/专业/颠覆性）并选择一个不会与创始人声音配置文件和脚本的情感弧感到奇怪的注册。匹配能量，不要与之对抗。

### 典型调用（将你的创意方向代入提示，保持 <= 200 字符）：

```
generate_music(
  provider: "kling-audio",
  mode: "text_to_audio",
  background: true,
  duration_seconds: 60,
  prompt: "<=200 字符：柔和的乐器背景床；<注册>，<主要乐器>，<情绪>，<BPM>；无歌词；为旁白留出空间"
)
```

工作原理（承重）：
- **Kling 生成一个 10 秒种子**：付费提供程序调用保持简短并支持背景。
- **工作器本地扩展**：MCP 使用本地 ffmpeg 循环/交叉渐变 10 秒种子以达到 `duration_seconds: 60`，然后返回扩展的 CDN `audio_url`。
- **`prompt` 字段携带风格快照**。包括“柔和的乐器背景床”、“无歌词”和“为旁白留出空间”，以便混音不会与创始人对话对抗。保持它 <= 200 字符；如果 Kling 返回 `1201`，请缩短相同的风格想法，而不是重试长提示。

保存为 `music_url`。读取 `result.duration_seconds`：
- 如果 `>= 55s` → 混合。预期路径与 Kling 工作器扩展。
- 如果 `< 55s` → 不要无声接受短的床。使用相同的 `kling-audio` 调用重试；如果它仍然返回短，停止并暴露工具结果，因为工作器扩展路径没有满足合同。

**禁止的反模式**（每个都经验性地导致失败）：
- ❌ `provider: "minimax-music"` 用于默认生成的床——MiniMax 不支持 `background: true`，并且可以在旁白下前景化旋律。
- ❌ 在技能中手动 10 秒平铺——MCP 工作器已经本地扩展一个 10 秒的 Kling 种子。
- ❌ 仅在 `prompt` 文本中放入持续时间（“60 秒乐器”）——使用 `duration_seconds: 60`。
- ❌ 添加 `lyrics` 字段——这个路径仅 Kling 提示。
- ❌ 对每个品牌复制相同的钢琴和垫示例——配方是模式，不是声音。每个品牌选择一个注册。

## [8] 组合层——下三分之二 + 字幕

> **管道顺序注意**——音乐混合在步骤 [10] 发生，在结尾卡片拼接之后。在拼接结尾卡片之前将音乐混合到正文会留下结尾卡片无声（音乐轨道在剪辑处结束）。始终：正文上的叠加层 → 结尾卡片 → 拼接 → 然后在整个组装剪辑上混合音乐。

首先使用 MCP 工具。`add_captions` 处理字幕计时和服务器端烧入；`render_html_animation` 处理授权的 HTML 动画；`edit_video_compose` 处理透明下三分之二叠加层。

### 默认路径

| 请求层 | 默认操作 |
|---|---|
| 无下三分之二，无字幕 | `body_with_overlays_url = base_url` |
| 仅字幕 | 调用 `add_captions(video_url: base_url, caption_mode:"auto", style:"classic", position:"bottom", font:"inter")`；将返回的 `url` 保存为 `body_with_overlays_url` |
| 仅下三分之二 | 通过 `render_html_animation` 渲染下三分之二 `.mov`，然后调用 `edit_video_compose`；将返回的 `url` 保存为 `body_with_overlays_url` |
| 下三分之二 + 字幕 | 首先渲染并组合下三分之二，然后调用 `add_captions` 在组合的检查点 URL 上 |

如果 `state.lower_third` 为 false 或未设置，跳过 [8a] 和 [8b]。这保持了默认路径完全为 MCP 原生。

不要调用本地 Whisper/字幕脚本或链接的 `edit_text_overlay` 用于字幕。如果精确原始脚本拼写很重要，仅在您已经从可信来源获得精确的计时段时传递手动 `subtitles[]`；否则优先选择 `add_captions` 自动瀑布。

### [8a] 渲染下三分之二（仅当 `state.lower_third = true`）

除非 `state.lower_third = true`，否则跳过此子步骤。通过 `render_html_animation` 渲染，格式为 `mov`（ProRes 4444 with yuva420p——保留 alpha）。**不要使用 `format: "webm"`**——HyperFrames 目前以 VP9 `pix_fmt=yuv420p` 的形式发出 webm，没有 alpha 通道，因此“透明”区域会变成纯黑像素，组合的下三分之二会显示黑色框在药丸之外。`.mov` ProRes 路径是目前唯一的 alpha 路径。

- 原生尺寸：800×220（匹配 1280×720 帧上的放置大小，因此没有缩放伪影）
- 药丸：`state.brand.colors.primary` 背景（默认 `#0d0d0d`），`state.brand.colors.highlight` 边框（默认 `#fefbcf`），`state.brand.colors.accent` 滤影（默认 `#cfc3ff`），18px 边框半径
- 两行文本：`founder_name`（Space Grotesk 800，80px，白色）+ `founder_role`（Space Grotesk 500，28px，黄油色）
- 不在药丸内放 logo——品牌标志存在于结尾卡片中；下三分之三是关于人的
- CSS `@keyframes` 仅：从 `translateX(-900px)` 滑入 0–0.6s，3 秒左右轻微框阴影脉冲，4–5s 滑出。不要使用 GSAP 用于下三分之二动画；结尾卡片适用相同的每帧搜索问题。

保存 URL 为 `lower_third_url`（文件扩展名 `.mov`）

如果您需要验证 `.mov`，检查视频流像素格式并确认它包含 alpha（`yuva...`）。如果是 `yuv...`，alpha 被丢弃——切换渲染格式或重新渲染。

### [8b] 下三分之二叠加层

仅当下三分之二启用时使用。默认使用 MCP 组合路径：

```
edit_video_compose(
  base_video_url: base_url,
  overlays: [{
    video_url: lower_third_url,
    position_px: { x: 50, y: <video_height - 220 - 100> },
    width_px: 800,
    height_px: 220,
    start_s: 0,
    end_s: 5
  }]
)
```

将返回的 `url` 保存为 `body_with_lower_third_url`。

本地后备合同，仅当 MCP 组合不可用时：
- 仅为此本地组合步骤下载 `base_url` 和 `lower_third_url`。
- 在 `x=50`，`y=video_height - 220 - 100` 处叠加 800×220 的下三分之二，启用 `t=0..5s`。
- 保留原始正文音频不重新编码，以便口型同步保持精确。
- 使用视觉无损 H.264 设置进行本地检查点。
- 使用 `upload_asset` 上传检查点并保存返回的 `public_url` 为 `body_with_lower_third_url`。

如果请求字幕，调用 `add_captions(video_url: body_with_lower_third_url, ...)` 并将其返回的 `url` 保存为 `body_with_overlays_url`。如果不请求，`body_with_overlays_url = body_with_lower_third_url`。

### [8c] 通过 MCP 的字幕

默认调用：

```
add_captions(
  video_url: <base_url 或 body_with_lower_third_url>,
  caption_mode: "auto",
  style: "classic",
  position: "bottom",
  font: "inter",
  font_color: "#ffffff",
  highlight_color: state.brand.colors.accent 或 "#cfc3ff",
  outline_color: state.brand.colors.primary 或 "#111111",
  font_size: 42
)
```

将返回的 `url` 保存为 `body_with_overlays_url`。返回的 `transcript` 对 QA 很有用，但视频 URL 是管道工件。

## [9] 动画结尾卡片（5 秒）——直接 HTML 作者，通过 HyperFrames 渲染

我们这里不使用 `generate_slide_animation`。该工具将 HTML 作者工作委托给滑块卡片 LLM，这例行添加角落杂乱（左上角标志，右下角 URL），选择错误的纵横比，并产生无法可靠在 HyperFrames 的每帧搜索中播放的动画。相反，协调者直接编写结尾卡片的 HTML，并通过 `render_html_animation` 渲染。使用与下三分之二相同的引擎。

### 硬规则——经验验证，不要偏离

这些不是风格偏好。每个都是通过渲染、提取帧、与预期比较和观察特定故障发现的。逆转其中任何一个将重现一个已知错误。

1. **纵横比与正文视频匹配。** 读取 `aspect_ratio`（默认 `16:9`）。计算 `#stage` 的 `data-width` × `data-height`：`16:9 → 1920×1080`，`9:16 → 1080×1920`，`1:1 → 1080×1080`。硬编码错误方向会产生正文和结尾卡片并排播放而不是按顺序播放的侧边栏拼接。

2. **无角落杂乱。** 无左上角标志。无右下角 URL。无标题旁边的图标圆角。结尾卡片是一个居中的信息 + CTA。品牌标志由字体和调色板暗示；明确的 logo 与标题竞争，并读作杂乱。（如果用户明确要求 logo，将其集成到居中的堆栈中——永远不要放在角落。）

3. **使用 CSS `@keyframes` 而不是 GSAP `tl.from()` 进行进入动画。** HyperFrames Chrome 通过 BeginFrame 每帧搜索；GSAP 的 `tl.from()` 懒惰地在第一次播放时记录其初始状态，并且在仅搜索播放下永远不会触发——每帧渲染静态最终状态，没有进入动画。CSS `@keyframes` 与 Chrome 的合成器时钟绑定，并按帧确定性地动画。通过 `#stage` / `#card` `data-duration` 属性声明持续时间；不要添加 GSAP 脚本来建立时间。GSAP 的重复帧捕获显示 t=0 和 t=2s 时相同的帧；切换到 CSS `@keyframes` 修复了它。

4. **所有进入动画必须在 `t = duration - 0.5s` 完成时。** 半秒保持，以便最终状态在剪辑前可读。使用 `duration: 5s` 那是 `animation-delay + animation-duration <= 4.5s`。

5. **使用绝对定位而不是 flex 进行动画元素，而不是 flex。** Flex 布局在 HyperFrames Chrome 中在帧 0 之前没有完全稳定，这加剧了上述 GSAP-from() 故障——元素在动画中途弹出，因为 flex 完成了它的第二次遍历。纯绝对定位从帧 0 提供稳定、确定性的布局。

6. **给每个 `@font-face` 一个唯一的 `font-family` 名称；不要依赖权重匹配。** 声明两个 `@font-face { font-family: "telka"; ... font-weight: 700/500; }` 块应该允许 CSS `font-weight: 500` 选择 500 面板——但在 HyperFrames Chrome 中，对于某些权重，匹配不可靠。使用不同的家族：`"telka-ext-900"`，`"telka-700"`，`"telka-500"`。当权重匹配失败时，标语可能会渲染在衬线后备中；切换标语到明确加载的家族避免这种情况。

7. **`telkaextended-900-normal.woff2` 和 `telka-700-normal.woff2` 在 HyperFrames Chrome 中是已知可工作的。`telka-500-normal.woff2` 是已知损坏的——它通过 fontTools 成功解析（正确的 OS/2.usWeightClass=500，有效的 cmap，正确的家族名称），但 Chrome 沉默地拒绝 @font-face 声明并回退到系统衬线。** 解决方案：使用 `telka-700` 作为标语（相同家族，稍重——视觉上仍然符合品牌）。如果未来的结尾卡片需要中等权重，通过渲染+提取帧 30 在发货前测试候选 woff2。不要相信“Telka 400”或“Telka 300”只是因为 Telka 700 有效就会工作。

8. **直接作为 base64 内联品牌字体。** Pika CDN 不接受字体上传（mime 允许列表）并且不发送 CORS 标头，因此 `@font-face` URL 引用在 HyperFrames Chrome 中失败，字体沉默地回退到系统衬线。使用 `pyftsubset` 将每个 woff2 子集为标题+标语+CTA 中的字形，base64 编码，嵌入为 `data:font/woff2;base64,...`。子集文件通常为 5–10 KB 每个文件。

9. **不要为品牌设计编写 CSS `font-family` 后备链。** 如果品牌字体加载失败，后备链会隐藏故障——你发货时认为它是 Helvetica，实际上是 Telka。使用 `font-family: "telka-700"` 单独（无后备）。然后字体加载失败会渲染 Chrome 的默认衬线，这在视觉上很明显并触发修复。

10. **组合合同** — HyperFrames合同：`<div id="stage" data-composition-id="main" data-start="0" data-duration="5" data-width="W" data-height="H">` 包裹一个单一的直接子元素`<div id="card" class="clip" data-start="0" data-duration="5" data-track-index="0">`，该子元素包含所有其他内容。可见的计时元素必须包含`class="clip"`，因为HyperFrames使用它来控制可见性，并且剪辑必须嵌套在组合根元素内，而不是作为兄弟元素。`#stage`的多轨道直接子元素与帧搜索交互不佳。（通过镜像工作的小三结构修复。）

11. **运行时就绪钩子** — 在`</body>`之前包含一个小型兼容性钩子：
    `window.__hf = { duration: 5, seek: (t) => { document.documentElement.style.setProperty("--hf-time", String(t)); } };`。
    CSS `@keyframes`仍然驱动视觉动画，但钩子使生产帧捕获路径在探测`window.__hf`时准备就绪。如果工作器报告`window.__hf在45000毫秒后未就绪`，则将HTML视为`render_html_animation`无效；修复组合合同或钩子并重新渲染。不要回退到静态PNG。

12. **渲染后始终在t=0、t=1s、t=2s提取帧并进行视觉比较。** 如果帧0和2看起来相同，则入口动画未运行。如果标语看起来像衬线字体，则品牌字体未加载。不要仅依赖URL。不要在没有此检查的情况下发布。 （用户在添加帧提取之前连续三次渲染时捕获了这些失败。）

### 构建步骤

```python
# 1. 确定画布
W, H = {"16:9": (1920, 1080), "9:16": (1080, 1920), "1:1": (1080, 1080)}[aspect_ratio]

# 2. 从state.brand选择调色板+字体（带回退）
bg      = state.brand.colors.surface  if state.brand else "#ffffff"
ink     = state.brand.colors.primary  if state.brand else "#0d0d0d"
accent  = state.brand.colors.accent   if state.brand else (accent_color or "#0d0d0d")
display_font_path = state.brand.fonts.display_path  # 例如 brand-kit/.../telkaextended-900-normal.woff2
body_font_path    = state.brand.fonts.body_path     # 用于标语+CTA
# 如果state.brand没有字体，使用下面的回退分支并在交付步骤中标记。

# 3. 将字体子集为仅标题/标语/CTA中使用的字符
glyphs = set(brief.product_name + brief.tagline + brief.call_to_action + " .,'-//")
if display_font_path and body_font_path:
    # 使用标准的fontTools pyftsubset命令或等效的本地字体子集工具。
    # 然后将子集的woff2字节base64编码并内联在@font-face数据: URL中。
    display_b64 = "<base64子集的display woff2字节>"
    body_b64 = "<base64子集的body woff2字节>"
else:
    display_b64 = body_b64 = None

# 4. 内联编写HTML。不要加载预设/模板文件。
#    包含#stage/#card合同、CSS @keyframes、绝对定位，
#    当display_b64/body_b64存在时包含@font-face数据URL、标题行、标语、CTA、调色板值和维度W/H。

# 5. 渲染
end_card_url = render_html_animation(html=filled, fps=30, quality="standard", format="mp4")
```

### 布局（居中堆叠 — 无角落）

```
┌─────────────────────────────────────────────┐
│ ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ │ ← 顶部强调条（从左到右动画擦除）
│                                             │
│            BIG TITLE LINE 1                 │ ← display字体900，向上滑动
│            BIG TITLE LINE 2                 │ ← display字体900，向上滑动（交错）
│                                             │
│                  ────                       │ ← 短强调分隔符（scaleX向内）
│                                             │
│             tagline goes here               │ ← body字体500，淡入+上升
│                                             │
│         ╭─ Start with X ─╮                  │ ← CTA药丸，强调背景，墨水边框，回弹+呼吸
│         ╰─────────────────╯                 │
│                                             │
└─────────────────────────────────────────────┘
```

### 动画时间参考（5秒结束卡片，CSS @keyframes）

所有动画都作为CSS `animation: name duration easing delay forwards`在相应元素上实现。元素的预动画CSS状态是“从” — 无需JS。

| t (s) | 元素 | 动画 |
|-------|---------|-----------|
| 0.00–0.85 | accent-top | `scaleX:0 → 1`, `cubic-bezier(0.16,1,0.3,1)` |
| 0.25–1.00 | title line 1 (`#title .l1`) | `y:120, opacity:0 → y:0, opacity:1` |
| 0.42–1.17 | title line 2 (`#title .l2`) | 相同，交错 |
| 1.00–1.50 | divider | `scaleX:0, opacity:0 → 1, 1` |
| 1.20–1.75 | tagline | `y:30, opacity:0 → y:0, opacity:0.9` |
| 1.55–2.15 | CTA pill | `y:60, opacity:0, scale:0.92 → y:0, opacity:1, scale:1`, `cubic-bezier(0.34,1.56,0.64,1)` (回弹弹出) |
| 2.60–4.20 | CTA pill | `scale:1 → 1.05 → 1`, 交替（微妙呼吸） |
| 2.80–4.80 | accent-top | `opacity:1 → 0.55 → 1`, 交替（轻柔闪烁） |
| 4.80–5.00 | hold | (最终可读状态) |

参考实现模式：使用居中堆叠HTML配方。在协调器中内联编写填充的HTML，并直接传递给`render_html_animation`；不要调用捆绑的辅助脚本或依赖单独的`presets/`目录。

如果品牌套件缺乏字体（`state.brand.fonts`为null）— 回退到系统`-apple-system, sans-serif`用于标语/CTA，但将标题降级为系统显示字重。不要使用回退字体渲染品牌字体结束卡片；它们总是看起来不对。在交付步骤中标记，以便用户知道品牌套件不完整。

将返回的MP4 URL保存为`end_card_url`。`end_card_url`必须是一个MP4视频片段，而不是静态PNG，因为步骤[10]将其与主体视频连接。仅在需要本地视觉QA帧或本地回退组装时下载它。

## [10] 通过MCP组装主体+结束卡片+音乐

使用服务器端确定性编辑工具进行最终组装。当前的MCP服务器`edit_concat`在连接前规范化不匹配的输入，`edit_audio_mix`在混合音乐轨道时保留原始视频音频。

```
assembled = edit_concat(video_urls=[body_with_overlays_url, end_card_url])
assembled_url = assembled.url

if music_url:
  mixed = edit_audio_mix(video_url=assembled_url, audio_url=music_url, audio_volume=0.16)
  final_url = mixed.url
else:
  final_url = assembled_url
```

混合音乐应在连接后，而不是之前，以便乐谱继续通过结束卡片。如果`edit_audio_mix`因为音乐文件太短或格式错误而失败，设置`final_url = assembled_url`，暴露音乐问题，并在交付前仍然运行步骤[10.5]；不要重新运行昂贵的SeeDance动作。

### [10.5] 最终时长下限

在向用户报告`final_url`之前，探测组装结果：

```
analyze_media(
  media: final_url,
  query: "返回包含此视频duration_seconds的JSON."
)
```

将结果保存为`final_duration_seconds`。它必须在`>= 55`和`<= 75`之前报告`final_url`作为完成的交付物。
如果`final_duration_seconds`低于55秒，将运行视为失败的局部组装：不要将URL作为最终交付，不要标记技能完成，并返回到缺少动作的恢复。如果所有4个动作都存在但探测仍然低于55秒，停止并暴露连接/提供者截断以供调查，而不是用无关素材填充。

## [11] 最终URL

将`final_url`保存到`state`。如果本地回退组装生成了最终MP4，通过`upload_asset`上传该检查点，并将`final_url`替换为返回的`public_url`。

## 交付后质量门

在声明成功之前，对`final_url`调用`analyze_media`并请求结构化裁决：

```
仅返回JSON：
{
  "verdict": "clean" | "degraded" | "catastrophic",
  "observations": string[],
  "quality_warning": string | null,
  "re_roll_suggestion": string | null
}
检查`brief.product_name` / `product_name`在任何出现的地方拼写正确，任何手机屏幕/产品屏幕显示预期的产品而不是幻觉的替代品，必需的产品资产在预期的动作中可见，并且最终视频没有黑帧或部分动作截断。
``}

- 如果`verdict`是`clean`，正常交付最终URL。
- 如果`verdict`是`degraded`，交付最终URL加上`quality_warning`，以便用户在发布前审查。
- 如果`verdict`是`catastrophic`，不要将视频标记为完成；暴露裁决和`re_roll_suggestion`，而不是声明成功。

## [12] 资产包（可选）

首先返回最终URL。如果用户要求可编辑的源资产，提供包含以下内容的包：

- `final_url`
- `act_urls`
- `character_url`、`location_url`以及任何产品/截图资产URL
- `music_url`
- `end_card_url`
- 可选的`lower_third_url` / `body_with_overlays_url`
- 脚本、品牌快速参考和动作到资产映射

为什么这很重要：
- 用户可以交换图层（创始人照片、子计时、音乐）并重新渲染，而无需重新获取所有内容
- 品牌套件是相同品牌未来视频的唯一真实来源 — 重用它只需一个文件夹复制
- 动作级的`.mp4`本身很有价值（例如，用户可能只想为特定频道剪辑一个动作）
- 用户通常要求将生成的引用保存在视频旁边，以便他们可以重用这些资产。默认编码。

## [13] 交付

向用户报告`final_url`。包括：
- 资产包URL/路径仅在用户要求时
- 从`final_duration_seconds`的总时长（~65秒=60秒主体+5秒结束卡片）
- 对重新运行有用的中间URL或本地文件：`base_url`、可选的`body_with_overlays_url`、`music_url`、`end_card_url`、`final_url`以及每个`act_urls[i]`
- 简要（`brief.product_name` / `brief.tagline`），以便用户确认模型是否选择了正确的产品
- 资产进入哪个动作的1行摘要，以便用户确认位置

## 验证门

| 步骤 | 检查 |
|------|-------|
| 简要 | `product_name`非空 |
| 资产分析 | 每个资产一个JSON对象，每个对象具有非空的`content_description`和`best_for_act` |
| 脚本 | 4个动作；总对话100–180字；每个资产至少由一个动作引用，或明确注明为未使用 |
| 引用 | `character_url`和`location_url`是https URL |
| 动作 | 返回所有4个act_urls（每个具有唯一种子）；对于包含非空`asset_index`的镜头，使用`analyze_media`检查一个镜头以确认资产实际上可见，并且揭示模式对于`product_type`正确（例如，对于`physical_apparel`，验证创始人正在拿着/穿着带有正确印刷的实际T恤 — 不是在手机屏幕上显示） |
| 拼接 | 返回`base_url` |
| 音乐 | 返回URL；`duration_seconds >= 55`来自`kling-audio`背景床路径；如果低于55，重试一次，然后停止并暴露 |
| 覆盖层 | 返回`body_with_overlays_url`（如果步骤[8]跳过则为`body_with_overlays_url = base_url`） |
| 结束卡片 | 返回作为MP4的`end_card_url`；使用`extract_frame`/`analyze_media`检查早期帧：帧0应显示空背景之前入口，稍后的第一秒帧应显示部分入口 — 确认CSS @keyframes正在运行，而不是静态 |
| 最终组装 | `edit_concat`返回的`assembled_url`；音乐存在时`edit_audio_mix`返回的`final_url`，否则`final_url = assembled_url` |
| 最终时长 | 在交付前`analyze_media`报告`final_duration_seconds >= 55`和`<= 75` |
| 本地回退上传 | 仅如果使用本地回退组装：将`final_url`替换为上传的`public_url` |

## 失败模式

除“时长下限和部分动作恢复”中记录的缺失动作重试外，在第一次验证失败时停止并暴露。不要自动重试昂贵的调用（SeeDance动作每次运行3–8分钟 — 重复失败会消耗积分）。

### 从上游5xx在analyze_brief / generate_image / generate_reference_video / generate_music / upload_asset中恢复

如果任何付费生成、简要分析、音乐、渲染、编辑或资产MCP调用返回：
- `code: "provider_5xx"` AND `retry_class: "retry_after_backoff"`
- 或来自任何上游提供者（Seedance、Kling、OpenAI、Gemini、存储）的HTTP 502 / 503 / 504

这样做：
1. 等待5秒。
2. 重新调用完全相同的MCP工具，并使用完全相同的参数。不要重写简要、产品名称、创始人照片、动作提示、种子、参考图像顺序、音乐提示或上传负载。
3. 如果重试也以5xx失败，中止并向用户显示：“提供者两次返回了瞬态上游错误。1-2分钟后重试；这通常会自行解决。”

不要重试超过一次。此路径用于瞬态提供者中断；在5xx后更改创意输入会创建不同的工件，并可能重复支出。

### 从上游4xx / moderation_blocked中恢复

如果`generate_image`在创建创始人/位置/产品参考时返回上游4xx或`moderation_blocked`：
1. 不要重试相同的提示；审核和大多数4xx验证失败是确定性的。
2. 如果资产不是用户关键，仅在替代品仍然符合简要时尝试一次回退提供者。对于创始人身份照片，不应使用回退提供者更改用户的身份；请求更安全的用户提供的参考。
3. 如果回退提供者也失败或会改变产品/创始人身份，向用户显示：“图像提供者拒绝了此参考提示。提供不同的参考图像或选择不太容易识别/风格化的方向。”

对于Seedance动作审核，仅在其适用的地方遵循时长下限/缺失动作恢复。不要运行重复的盲目动作重试。

### 从上游429（速率限制）中恢复

如果任何上游返回带有回退提示的HTTP 429：
1. 等待提示的回退，或如果没有提示则等待30秒。
2. 重新调用完全相同的MCP工具，并使用完全相同的参数。
3. 不要重试超过一次。如果它仍然返回429，中止并显示速率限制消息。

### `capture_website`返回空 / 页面未加载

此技能通常使用`analyze_brief`提取产品事实，但URL简要辅助程序可能调用`capture_website`。如果`capture_website`返回200但`action_bboxes`为空或`recording_viewport`为0x0：
1. 不要重试；页面在捕获环境中未能渲染。
2. 暴露：“无法捕获<url>。页面可能被阻止/付费墙/需要认证。请提供产品简要、截图或托管资产。”

### `upload_asset`网络/认证失败

如果`upload_asset`在将创始人照片、产品资产、品牌标志、小三或回退本地组装转换为托管URL时失败，不要继续使用本地文件系统路径在`reference_images`或HTML中。仅对上述5xx或429类重试一次。对于`auth_error`、不支持的MIME、网络故障或重复上传失败，停止并请求托管URL或支持的光栅导出。

### 长时间运行的`task_status`超过上限

每个异步MCP调用要么返回内联结果，要么返回`{task_id, status}`用于轮询。在使用以下上限之前决定任务是否卡住：
- Seedance i2v：每调用10分钟
- Kling音频：每调用5分钟
- gpt-image-2高质量：每调用3分钟
- 渲染/编辑/上传辅助程序：每调用5分钟

使用较早者：提供者的上限x1.5或任何技能特定的硬轮询上限，包括上述Long-running task_status轮询合同中的15分钟总上限。如果`task_status`返回`status: "processing"`或`status: "queued"`超过该较早限制，调用`task_cancel({task_id})`并暴露：“提供者运行异常长时间；中止。重试。”

| 症状 | 原因 | 解决方法 |
|---|---|---|
| `generate_reference_video` 返回 402 "余额不足" 且带有熟悉的 UUID | 等幂缓存重放了一个旧的失败结果，参数相同 | 每次调用传递一个唯一的 `seed`（101 / 202 / 303 / 404 用于 4 个场景）以便哈希值不同。 |
| SeeDance 在创始人参考上返回 422 "可能包含真实人物肖像" | 内容策略过滤器触发（间歇性——同一张照片可能在下次尝试中通过） | 重新生成创始人肖像，使用更强的风格化（"皮克斯/迪士尼 3D 动画美学"）。不要自动重试相同的参考——会消耗积分。 |
| 创始人衬衫在场景之间变化 | 每个场景都重新读取 @Image1，没有服装锁定 | 在每个场景提示中添加 `WARDROBE LOCK:` 行，内容完全相同。 |
| 所有 4 个场景都有相同的物理背景 | 开头行说 "在匹配 @Image2 的位置内部" —— 字面理解 | 以 "在视觉风格、调色板、灯光和材料匹配 @Image2 的场景中" 开头 + 添加每个镜头的 `Background context:` 行。 |
| 创始人看起来像被冻结的 / 没有肢体语言 | 节奏是仅面部；场景是单镜头 | 每个场景添加 3 个时间编码的子镜头，带有明确的 `Transition:` 行；每个节奏都需要手/躯干/头部动作（见 [3c.1]）。 |
| 最终视频小于 55 秒 | 一个 SeeDance 场景超时或最终连接修剪了身体，产生了一个不完整的运行 | 不要将其作为最终版本交付。使用新种子重试缺失的场景，同时保留成功的场景；如果无法完成，停止并显示上游 SeeDance 超时。 |
| 音乐提示被拒绝，代码 `1201` | `kling-audio` 提示超过了 200 个字符的提供者限制 | 将提示缩短为标准的 <= 200 字符风格快照。保留 `soft instrumental background bed`、`no vocals` 和 `leave room for narration`；不要更改提供者、持续时间或背景模式。 |
| 音乐返回 < 55 秒 | `kling-audio` 工作程序扩展没有满足 60 秒的请求 | 确认调用使用了 `provider: "kling-audio"`、`mode: "text_to_audio"`、`background: true` 和 `duration_seconds: 60`。重试一次；如果仍然短，停止并显示工具结果。 |
| 音乐压倒了对话 | 提示要求前景旋律而不是床铺 | 重新生成一次，使用 "soft instrumental background bed, no vocals, leave room for narration"，并在步骤 [10] 中将 `audio_volume` 保持为 0.16 或更低。 |
| 字幕错拼产品名称 | 自动转录标准化了语音音频 | 如果您已经有了可信的时间戳片段，请仅使用手动 `subtitles[]`；否则，不要默认运行本地 Whisper，而是显示转录限制。 |
| 下三分之一覆盖在药丸外部显示黑色框 | webm 格式编码时没有 alpha (yuv420p) | 使用 `format: "mov"`（ProRes 4444 yuva）重新渲染。使用 `ffprobe \| grep pix_fmt` 验证显示 `yuva*`。 |
| 最终视频音频比视频短 | 本地备用连接使用了 `-c copy` 且音频参数不匹配 | 优先使用 MCP `edit_concat`。如果本地连接不可避免，请在连接前将所有输入标准化为 aac/44100/stereo/192k。 |
| 结束卡片在 t=0 和 t=2s 渲染相同（没有进入动画） | 使用了 GSAP `tl.from()` 而不是 CSS `@keyframes` | 将进入转换为 CSS `@keyframes`；仅保留 GSAP 桥接用于持续时间寻址。 |
| 结束卡片标语渲染为衬线备用 | woff2 字体在 HyperFrames Chrome 中加载失败 | 每个字体使用唯一的 `font-family` 名称（不是重量匹配）；将 woff2 子集并 base64 内联；在发货前提取第 30 帧进行验证。 |
| `render_html_animation` 失败，`window.__hf` 在 45000ms 后未准备好 | 结束卡片 HTML 没有暴露运行时就绪钩子或有效的嵌套 `class="clip"` 组合 | 添加/修复 `window.__hf` 钩子和 `class="clip"` 子元素，然后重新渲染 MP4。不要回退到静态 PNG，并且不要在 `end_card_url` 是视频 URL 之前继续。 |

## 承重短语

这些字符串直接放入 SeeDance 提示（或 HTML 渲染）。每个都经过经验验证——释义会导致无声故障。编辑提示时，搜索这些锚点并保持其完整性。

| 短语 | 放入 | 为什么承重 |
|---|---|---|
| `The character (matching @Image1) in a setting whose visual style, palette, lighting and materials match @Image2.` | 每个场景提示的开头 | "在视觉风格匹配的场景中" 允许 SeeDance 每个镜头变化背景；"在匹配位置内部" 在所有 4 个场景中重现字面背景。 |
| `WARDROBE LOCK: …`（后面跟着所有 4 个提示中相同的服装句子） | 每个 `CHARACTER VOICE:` 行下的标题行 | 锁定跨单独 15 秒生成的服装。@Image1 单独可以在场景之间漂移。 |
| `Background context: …`（每个子镜头一个，每个位置不同） | 每个镜头块内 | 强制 SeeDance 每个镜头渲染不同的物理位置——不同的墙壁、不同的角度、不同的背景特征。没有它，所有 3 个子镜头都会出现在同一个角落。 |
| `<<<voice_1>>>…<<<voice_1>>>` | 每个镜头的对话有效负载 | SeeDance 原生口型同步标记。标记是引擎知道要口型同步什么的方式；没有它们就没有口型同步。 |
| `Transition: …` / `Hard cut:` | 同一提示中子镜头之间 | `Transition:` 描述连续的摄像机运动（滑行 / 推拉 / 弧线）；`Hard cut:` 触发真正的剪辑。没有其中任何一个，SeeDance 默认为同一位置的重新帧，看起来像跳变变焦。 |
| `Native lip-synced dialogue audio, no music overlay.` | 每个场景提示的结尾 | 防止 SeeDance 在对话下方层叠自己的环境音乐，这会与步骤 [10] 中的专用音乐床冲突。 |
| `provider: "kling-audio"`, `mode: "text_to_audio"`, `background: true`, `duration_seconds: 60` | 步骤 [7] `generate_music` 调用 | 使用唯一的后台支持音乐提供者，触发 MCP 工作人员的 10 秒 Kling 种子 + 本地 ffmpeg 扩展路径。 |

## 不要做的事情

- **不要以 "在匹配 @Image2 的位置内部" 开头 SeeDance 提示**——在所有场景中重现字面背景。使用 "在视觉风格...匹配 @Image2"。 |
- **不要在提示中描述角色**——@Image1 承载身份。散文冲突会产生幽灵角色或错误的服装。例外：`WARDROBE LOCK:` 行。 |
- **不要使用电影行业镜头术语**——"双人镜头" / "三人镜头" / "过肩镜头" / "OTS" / "全景镜头" 触发 SeeDance 幽灵主体伪影。用普通语言描述摄像机看到的内容。 |
- **不要将下三分之一渲染为 webm**——alpha 不会保留（HyperFrames 发射 yuv420p）。使用 `format: "mov"`（ProRes 4444 yuva）。使用 `ffprobe \| grep pix_fmt` 验证。 |
- **不要使用 `generate_slide_animation` 为结束卡片**——该工具的幻灯片卡片 LLM 添加角落杂波，产生的动画无法确定性地寻址。直接编写内联 HTML 并通过 `render_html_animation` 渲染。 |
- **不要链式 pika MCP `edit_text_overlay` / overlay 调用用于任意文本/字幕组合**——这会级联质量损失并可能引入口型同步漂移。使用 `add_captions` 用于字幕，并使用单个组合/本地传递用于有界的下三分之一。例外：步骤 [5.5] 确定性的数字 UI 覆盖故意使用一个有界 `edit_video_compose` 传递加上可选的精确品牌 `edit_text_overlay`，然后进行 OCR QA，以防止 Seedance 渲染的品牌/UI 文本。 |
- **除非 MCP 不可用，否则不要使用本地 `ffmpeg concat -c copy` 进行最终组装**——旧的音频掉落问题在本地连接行为中。默认使用 MCP `edit_concat` + `edit_audio_mix`。 |
- **不要跨场景使用相同的参数启动 SeeDance**——MCP 等幂缓存哈希到相同的任务 ID 并重放旧结果（有时是失败的）。每个场景传递唯一的 `seed`。 |
- **不要使用 MiniMax 作为默认生成的床**——它不支持 `background: true` 并且会将旋律置于叙述下方。 |
- **不要在技能中手动平铺 10 秒 Kling 剪片**——MCP 工作人员拥有本地 ffmpeg 扩展路径用于 `duration_seconds: 60`。 |
- **不要为每个品牌复制示例音乐声音**——配方是 Kling 背景床调用，而不是特定的乐器。选择与 `brief.tone` 匹配的音域（见步骤 [7] 表）。 |

## 引擎选择：仅 seedance（带注意事项）

SeeDance (`fal-seedance-2-i2v` 通过 `generate_reference_video` `provider: "seedance"`) 是唯一的视频引擎。测试后选择：

- **vs Kling v3-omni**：Kling 有真正的 `shots[]` 硬切数组（更干净的多人镜头），但拒绝 `seed` 参数（缓存破坏更难），并且 4 × pro 1080p 输出总和 >50MB 超出 `edit_concat` 上传限制（强制本地连接）。Kling 对真实人物照片的内容策略更宽松——如果 SeeDance 的间歇性 422 成为硬障碍，值得将其作为备用考虑。
- **vs Happy Horse `happyhorse-1.0-r2v`**（阿里巴巴 DashScope）：产生干净的 1080p 带原生口型同步，但多镜头提示方向较弱，明显不如 SeeDance 现代化。 |
- **SeeDance 赢得是因为**：原生 `<<<voice_1>>>` 口型同步，接受 `seed`（缓存破坏），对真实人物照片足够宽容，95%+ 运行通过内容过滤器，单个 15 秒提示带时间编码子镜头足以提供足够变化用于讲话者。 |

如果 SeeDance 出现故障或其内容过滤器开始反复拒绝创始人参考，文档中记录的备用方案是重新生成创始人肖像，使用更强的风格化（皮克斯/迪士尼 3D 美学）。在管道中途切换引擎会改变提示、连接和资产大小流中的太多假设。 |

## 运行时预期

每个步骤的时钟时间。总运行时间约为 12–18 分钟，主要由并行 SeeDance 批次主导。

| 步骤 | 时钟时间 | 备注 |
|---|---|---|
| [1] analyze_brief | 20–60 秒 | |
| [2] analyze_media × N | 每个资产 15–30 秒，并行 | |
| [4] founder/custom 位置参考 | 每个 10–60 秒 | 上传本地创始人照片，使用提供的 URL，或生成创始人肖像；默认位置等待 [4.5] |
| [4.5] 品牌套件摄入 + 默认位置 | 10–30 秒 | 解析品牌套件，上传标志资产，如果需要渲染匹配宽度的品牌强调背景 |
| [5] SeeDance × 4 并行 | 5–9 分钟时钟（最慢的场景） | 每个场景 3–8 分钟，可能异步完成 |
| [5.5] 数字 UI 覆盖 | 30–120 秒用于数字产品 | 渲染真实 UI / 商标覆盖剪辑，将它们合成到揭示场景中，然后在进行 OCR QA 之前连接 |
| [6] edit_concat（场景 → 60 秒主体） | 30–60 秒 | |
| [7] generate_music | 30–90 秒，如果 <55 秒则重试一次 | Kling 生成一个 10 秒种子，然后工作人员本地扩展到 ~60 秒 |
| [8a] render LT 为 .mov | 60–120 秒 | ProRes 4444 慢于 webm 但仅 alpha 路径 |
| [8] add_captions | 30–90 秒 | 字幕仅，或在下三分之一检查点后 |
| [8b] 本地下三分之一覆盖备用 | 20–60 秒 | 仅当下三分之一启用时 |
| [9] render end card | 60–120 秒 | |
| [10] edit_concat + edit_audio_mix | 30–90 秒 | 服务器端标准化连接和音乐混合 |
| **总计** | **12–18 分钟** | |

## 默认值

- 4 × 15 秒 SeeDance 场景，并行，唯一种子（101、202、303、404）
- **角色身份来自 `@Image1` 参考**——避免在提示中描述角色（没有 "Founder Avery"，没有 "年轻的创意街头风创始人"）。每个提示以 **"The character (matching @Image1) in a setting whose visual style, palette, lighting and materials match @Image2."** 开头。使用 "在匹配 @Image2 的位置内部" 会使 SeeDance 在所有场景中重现字面背景。唯一的例外是每个场景提示中的 `WARDROBE LOCK:` 行，以保持跨 4 个单独 15 秒生成的服装一致。
- **避免电影行业镜头术语**，SeeDance 会字面理解——永远不要写 "双人镜头"、"三人镜头" 或 "全景镜头"。镜头 F 是 "品牌上下文镜头"。
- **每个脚本都有一个 `character_voice_profile`**（3-4 行描述默认交付——节奏、标志性手势、暂停行为）。在每个场景的 SeeDance 提示中重复字面 `CHARACTER VOICE: …`。
- **每个镜头都有 `beats[]`**，不是场景级 `acting`。每个节奏都有 `text` + `emotion` + `physical`。沉默 `(beat)` 条目指示在说出句子之间发生什么（保持凝视、微表情、手势过渡）。节奏作为每个镜头的 "Acting beats" 块在 SeeDance 提示中发出。
- **每个场景中第一个镜头之外的镜头都有 `transition_from_prev`**——一个连续摄像机移动描述，将我们从之前的构图带到这个构图（推拉、弧线、推过、拉回、轨道）。没有它，多镜头场景会读取为跳变变焦，因为 SeeDance 会重新帧同一虚拟摄像机位置，而不是在空间中移动。
- **在将对话文本连接到 `<<<voice_1>>>` 有效负载之前应用 TTS 发音重写**（Ari → Airy，API → A P I，example.com → example dot com，等等）。见步骤 [3] 中的 "TTS 发音重写"。
- 16:9，1080p（SeeDance `resolution: "1080p"`）
- 用户提供的资产根据产品类型适当揭示：
  - `digital` → 在镜头 C 和 E 中的手机空白占位符，然后在步骤 [5.5] 中合成真实 UI / 商标
  - `physical_apparel` → 创始人穿着/持有实际 T 恤；将资产作为参考传递到每个出现衬衫的镜头（而不仅仅是一个揭示节奏）
  - `physical_object` → 创始人举起产品；将资产传递到所有产品可见的镜头
  - `consumable` → 创始人使用/吃/喝；相同模式
  - `service` → 无资产揭示；仅环境和对话
- 音乐：目标 ~60 秒乐器——调用 `generate_music` 使用 `provider: "kling-audio"`、`mode: "text_to_audio"`、`background: true` 和 `duration_seconds: 60`。将 `prompt` 保持在 <= 200 字符，并包括 "soft instrumental background bed"、"no vocals" 和 "leave room for narration"。如果少于 55 秒，则重试一次，然后停止并显示而不是接受短的床。
- 5 秒结束卡片通过 `render_html_animation`——根据步骤 [9] 编写内联 HTML，将品牌字体作为 base64 内联。从 `state.brand`（在步骤 [4.5] 中设置）获取品牌 → 真实标志、真实调色板、真实字体。
- **字幕通过 `add_captions`。** 默认使用服务器端逐词字幕烧入。字体选择是工具支持的集合（`inter`、`bebas-neue`、`noto-cjk`）；使用品牌强调颜色而不是本地自定义字体 `drawtext`。
- **下三分之一备用。** 默认关闭。如果 `state.lower_third = true`，通过 `render_html_animation(format:"mov")` 渲染 5 秒品牌药丸左下；最终覆盖使用 `edit_video_compose`，或者如果 MCP 组合不可用，则进行单个本地 ffmpeg 传递。
- **最终组装通过 MCP。** 使用 `edit_concat` 用于主体 + 结束卡片，然后使用 `edit_audio_mix` 用于音乐。本地连接/混合是备用，不是规范路径。
- 提供者：`seedance` 仅。参考标记是 `@Image1` / `@Image2` / `@Image3`。原生口型通过每个子镜头的 `<<<voice_1>>>...<<<voice_1>>>` 标记。真实人物创始人照片在大多数情况下通过内容过滤器；间歇性 422 → 使用更强的风格化重新生成。
