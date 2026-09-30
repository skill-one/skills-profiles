---
name: founder-product-video
description: 当用户要求创始人产品视频或任务与以下示例匹配时使用。根据产品链接 + 用户提供的图像，生成一个65秒的创始人风格产品视频。输出为16:9 1080p MP4格式——包含4个15秒的SeeDance创始人讲话片段 + 5秒的品牌结束卡片 + 背景音乐。用户的实际产品截图会在SeeDance生成后合成到产品展示画面中，因此可读的UI和品牌文字是真实的，而非AI想象。触发条件——"创始人视频"、"产品视频"、"60秒路演视频"、"为[URL]制作[创始人]的视频"、"创始人讲解视频"。需要Pika MCP支持。使用提供的品牌工具包文件夹（`brand.json`或导出的品牌工具包`brand.md`、包含token和logo资源）；如果不存在工具包，请先运行build-a-brand。
---

# founder-product-video

您根据产品 URL 和用户提供的图像生成一个 65 秒的创始人风格产品视频：60 秒的创始人演讲视频主体加上 5 秒的品牌结尾卡片。用户提供的图像（产品照片/网站截图/应用截图）作为视觉参考流入 SeeDance，生成后复合数字产品屏幕/品牌标识，因此可读的用户界面是确定的，而不是模型渲染的。

没有切入镜头。不提取网站 CSS。AI 生成、确定性渲染、字幕、拼接和音乐混合默认通过 Pika MCP 工具进行。下三分屏覆盖是可选的，默认使用 MCP 组合，仅将本地 ffmpeg 作为紧急回退。

## 成本透明门

在调用任何付费 MCP 调用之前，调用一次 `identity_balance({verbose: true})`。显示当前余额、近期消耗率和剩余运行时间，然后用以下确切消息门控运行：

> 预计成本：典型的四幕 Seedance 创始人视频和支持资产约 4,000 信用点（约 40 美元）。这超过了 5,000，请回复 `proceed` 继续 或 `cancel` 停止。

在用户回复 `proceed` 之前，不要调用任何付费 MCP 工具。如果用户回复 `cancel`，则不生成。对于非交互式 `--quick` 或 `--config` 调用者，需要在配置中要求 `cost_ack=proceed`；如果不存在，则停止并显示估计值，而不是花费信用点。

## [0] 摄入 — 在任何管道步骤之前首先运行

**如果使用空参数调用**，则打印此菜单原文并停止 — 等待用户粘贴输入：

> **您想制作什么样的创始人视频？** 必须提供：
> - **产品 URL** — `https://...`（任何具有真实主页的内容）
> - **创始人** — 姓名 + 职位，例如 *"Eli Kim, CEO"*
> - **创始人照片** — 本地路径、https URL，或 `generate`（我将创建肖像）

可选（省略时使用合理默认值）：品牌套件路径 · 自定义手机截图 · 音乐 · 画幅（16:9 / 9:16 / 1:1）· 地点图像 · 语音风格 · 产品类型

示例：`/founder-product-video https://example.com --founder "Eli Kim, CEO" --photo ~/Pictures/eli.jpg`

**如果参数在交互模式下包含部分输入**，则跳过菜单，逐个询问以收集缺失的必填字段 — 问，等待，再问下一个。不要将问题捆绑在一个块中。如果用户未经提示提供字段（例如，他们在触发消息中粘贴了 URL），则跳过该问题，并在最后确认一次该值。不要开始管道，直到所有必填字段都回答完毕。如果适用非交互式快速通道，则使用步骤 [0.5]。

### [0.5] 非交互式快速通道

当调用者传递 `--quick` 或 `--config <path>`，或调用者声明他们是从 CI、子代理、批处理作业或任何其他非交互式 harness 运行时，使用此路径。

本节优先于下方的交互式问/等指令。当适用时，使用此快速通道，并且不要落入多轮摄入，除非 `url` 或创始人姓名/角色确实缺失。

- `--config <path>` 指向一个包含规范输入契约预烘焙值的 JSON 文件：`url`、`brand_kit_path` 或 `build_brand`、`founder_name`、`founder_role`、`founder_photo`、`assets`、`music_url`、`aspect_ratio`、`location_image_url`、`voice_style`、`product_type` 和 `lower_third`。
- `--quick` 表示使用默认值进行可选附加项，如果省略 `brand-kit`，则使用 `build-a-brand --quick` 自动构建品牌套件，并且在未提供照片时使用 `founder_photo = "generate"`。
- 对于 `--quick` 或 `--config`，不要在品牌套件分支、创始人照片生成提示、可选附加项提示、脚本选择或结尾卡片/字幕默认值处停止确认。直接记录假设并继续。
- 如果 `url` 或创始人姓名/角色在参数或配置中找不到，则停止一次，并显示一个紧凑的缺失字段列表，而不是开始多轮问答循环。

**1. 产品 URL** *(必填)* — `https://...`。用于（a）步骤 [1] 中的简报和（b）为下方的品牌套件分支提供输入。

**2. 品牌套件** *(必填)* — 交互模式：询问 *"您已经有了品牌套件文件夹，还是应该先构建一个？"*  
- 如果是路径 -> 使用它 (`state.brand_kit_path = <path>`)。接受 `brand.json` 或导出的 `build-a-brand` 套件，其中包含 `brand.md`、`tokens/tokens.json` 和标志资产。
- 如果是 "build" -> 调用 URL/brief 上的 `build-a-brand` 技能并等待导出的品牌套件。这是一个完整的身份工作流程，可能会暂停以供用户选择；在交互模式下显示这些提示。  
- 快速通道：如果配置提供 `brand_kit_path`，则使用它。如果配置设置 `build_brand` 或 `--quick` 省略 `brand-kit`，则对 URL/brief 调用 `build-a-brand --quick` 并等待导出的品牌套件；不要显示 `build-a-brand` 提示或停止以供身份选择。在任一分支后，设置 `state.brand_kit_path`。如果路径不存在且品牌套件无法构建，则停止并显示一个紧凑的缺失字段列表。

**3. 创始人身份** *(必填)* — 交互模式：一起询问所有三个：
- `founder_name` — 例如 "Avery"
- `founder_role` — 例如 "CEO, ExampleCo"
- `founder_photo` — 本地路径 / https URL / 或字面字符串 `generate` 以自动创建肖像。如果 `generate`，提示用户输入一行氛围（"温暖、休闲的智能服装" / "皮克斯风格的 3D 动画" / 等等）— 这将成为步骤 [4] 中 `generate_image` 的种子提示。  
- 快速通道：使用来自参数/配置的创始人值。如果省略 `founder_photo`，则设置 `founder_photo = "generate"` 并使用从产品色调派生的中性创始人肖像氛围；不要为单独的照片氛围提示停止。

默认不使用下三分屏，以保持快乐路径简洁。如果用户明确要求下三分屏，则记录 `state.lower_third = true`；在交互模式下，确认 `edit_video_compose` 将在渲染后添加透明覆盖层。

**4. 可选附加项** — 交互模式：作为单个消息提供这些，如果没有在同一轮中回复答案，则继续进行。快速通道：使用下方的默认值，无需询问。
- *自定义图像* — 列表 `assets`（产品照片/应用截图）显示在创始人手机上。**省略时默认：** 如果存在 `brand.json.screenshots`，则使用截图；否则，在品牌套件中查找明显的截图或产品图像；否则，在步骤 [2] 之前使用 `capture_website(mode:"screenshot")` 捕获产品 URL。除非 `product_type` 明确为 `service` 且用户接受仅环境视频，否则在没有真实产品 UI / 产品图像的情况下不要继续到脚本或 SeeDance。在快速通道中，如果未提供/品牌套件/捕获的资产不存在，则停止并显示紧凑的缺失资产错误，而不是无声地发送一个通用的讲话头视频。
- *音乐* — 本地路径 / https URL / 或 `generate`（器乐，~60s）。默认：通过 Kling 背景模式生成。
- *下三分屏* — 可选。默认：关闭。如果启用，则通过 MCP 渲染透明 `.mov`，然后使用 `edit_video_compose` 将其叠加到主体上。
- *画幅* — `16:9`（默认）、`9:16`、`1:1`。
- *地点* — 默认为 `state.brand.colors.accent` 中的平面无缝背景（干净的影棚拍摄外观，角色对单一品牌颜色，无论品牌的主色调是什么）。如果用户想要办公室、户外等，则使用路径 / URL / 文本描述覆盖。
- *语音风格* — SeeDance 的 VO 指导字符串，例如 "温暖、真实的创始人能量，对话式"。默认：从 `brief.tone` 派生。
- *产品类型* — `digital | physical_apparel | physical_object | consumable | service`。默认：在步骤 [2] 中从资产分析自动派生。

在阶段 0 完成后，将所有收集的值存储在 `state.inputs` 中。如果您已经为本次运行创建了本地工作目录，则可以选择将相同的对象作为 `<workdir>/inputs.json` 持久化；不要要求预定义的工作目录环境变量。然后进入管道步骤 [1]。

### [0.6] 创始人照片的 Avatar 类型探测

在调用任何付费 `generate_reference_video` 之前，在本地上传或用户提供的 URL 规范化后，对解析的创始人照片/头像 URL 运行此 Avatar 类型探测。这适用于用作角色参考的任何创始人照片 — 无论是通过 `--photo` 提供 还是生成。

调用一次 `analyze_media`：

```
query: "为付费视频生成对这张图像进行分类。它是一张真实人脸的照片、AI 生成的逼真肖像、风格化/插画角色，还是像蝙蝠侠、皮卡丘或米老鼠这样的可识别的商标/版权角色？仅返回严格的 JSON：{ \"avatar_type\": \"real_human\" | \"ai_realistic\" | \"stylized_illustrated\" | \"recognized_ip\", \"recognized_character\": string | null, \"moderation_risk\": \"low\" | \"medium\" | \"high\", \"recommendation\": \"proceed\" | \"warn\" | \"reject\" }。当没有识别特定角色时，使用 null for `recognized_character`；永远不要在该字段中写入 \"none\"、\"unknown\" 或解释性文字。"
```

根据结果路由：
- **已识别的 IP / 版权风险** -> **仅在** `avatar_type` 为 `"recognized_ip"`，或 `recognized_character` 称呼特定角色（例如 `"Batman"`），或当 `moderation_risk` 为 `"high"` 且 `recommendation` 为 `"reject"` 时 **停止**。将 `recognized_character: null`、空字符串、`"none"`、`"unknown"`、`"n/a"` 和低/中 `moderation_risk` 视为单独不足以停止。在真实/风格化路线之前运行此检查。即使 `avatar_type` 是风格化/插画，chibi 蝙蝠侠仍然是蝙蝠侠。
- **真实人类 / AI 生成的逼真** -> 正常进行。
- **风格化/插画** -> 带可见警告继续，因为风格化头像可能对 Seedance 像征和审核不太可靠，然后只有在用户提供或接受该头像时才继续。
- **商标/版权** -> **在生成前停止**。显示此消息：`您的创始人照片似乎是商标角色（[X]）。大多数视频提供商会审核并拒绝生成。通过 --photo <真实照片 URL> 覆盖。` 对于此技能，`--photo <真实照片 URL>` 是接受的明确标志；您也可以提及跨技能 `--avatar <真实照片 URL>` 说法，因为用户可能知道这种惯例。

## 必填输入（规范契约）

在阶段 0 之后，这些是下游步骤消费的字段：

- `url` — 产品网站（https://）。驱动步骤 [1] 简报。
- `brand_kit_path` — 品牌套件文件夹。必填。结尾卡片和下三分屏在存在时消费 `brand.json`，否则消费 `brand.md`、`tokens/tokens.json` 和来自 `build-a-brand` 导出的标志资产。见步骤 [4.5]。
- `founder_name` + `founder_role` + `founder_photo` — 从摄入中必填。步骤 [4] 在任何 SeeDance 调用之前将 `founder_photo` 规范化为 `founder_photo_url` 和 `character_url`。
- `assets` — 可选数组 `{ url, role?, caption? }`。默认为品牌套件捕获的截图；当品牌套件没有截图时，在步骤 [2] 之前捕获产品 URL，并将返回的 `image_url` 存储为真实产品 UI 资产。`role` 是一个提示字符串，将资产映射到脚本节拍（`hero`、`feature_a`、`cta` 等）。
- `location_image_url` — 可选。默认为生成的纯色背景，位于 `state.brand.colors.accent`。
- `music_url` — 可选。默认为 `generate`（步骤 [7] 中的 Kling 60s 背景床）。
- `aspect_ratio` — 默认 `16:9`。
- `voice_style` — 可选，默认为 `brief.tone`。
- `product_type` — 可选，在步骤 [2] 中自动派生。

## 状态

在处理过程中保持一个简单的 `state` 对象，并保存每个 CDN URL，以便可以恢复部分运行。将 `task_status` 值 `completed` 视为成功的终端状态（`failed` 和 `cancelled` 是失败的终端），然后当存在时解包 `result.structuredContent`。最终视频存储在 Pika 的 CDN 上；除非 MCP 组合不可用且您明确触发步骤 [8b] 中的本地下三分屏回退，否则不需要本地工作空间。

## 长任务 `task_status` 命令

当任何长时间运行的生成或编辑调用返回带有或没有初始状态的 `task_id` 时，包括 `{task_id}`、`{task_id, status: "queued"}` 或初始 `queued`、`running` 或 `processing` 状态，立即在 `state` 中记录任务 ID 和开始时间。

- 在终端 (`completed | failed | cancelled`) 之前，在紧密循环中调用 `task_status({task_id})`。不要手动睡眠和不要 Bash 轮询；工作进程会保持每个状态调用打开。
- 在状态为 `queued`、`running` 或 `processing` 时，每 60 秒发出一条可见进度行：`Seedance i2v queued for {N}m {S}s... still processing`。在轮询音乐、字幕、渲染、拼接、混合或编辑任务时，替换提供者/阶段标签。
- 在 `completed` 时，解包返回的结果 URL 并将其保存到 `state`。
- 在 `failed` 或 `cancelled` 时，向用户显示失败，包括 `task_id`、状态和最后的状态消息。
- 从原始提交开始 15 分钟后，如果任务仍然非终端，则调用 `task_cancel({task_id})`，然后向用户显示失败。如果取消报告任务已经终端，则再次调用状态一次并报告终端结果。
- 在原始任务仍然为 `queued`、`running` 或 `processing` 时，不要提交重复请求。

## 管道概述

```
[阶段 0] 摄入          您（Claude）：询问用户 URL + 品牌套件（路径或构建）+ 创始人（姓名/角色/照片）+ 可选附加项
  → [0.5] 品牌套件自动构建（仅当用户说 "build"）
                          调用 `build-a-brand`；在非交互模式下使用 `build-a-brand --quick`
  → [1] 分析简报             pika MCP：产品名称 + 标语 + 功能 + 氛围 + CTA
  → [2] 解决产品 UI 资产     pika MCP：使用提供的/品牌套件截图，或捕获产品 URL
  → [2] 分析媒体 × N         pika MCP：理解每个真实资产显示的内容
  → [3] 编写脚本             您（Claude）：4 幕 × 15s；将资产映射到各幕
  → [4] 创始人/地点参考     pika MCP：上传或生成创始人参考；携带用户提供的自定义地点
  → [4.5] 品牌套件摄取     解析 `brand.json` 或 `brand.md` + tokens → `state.brand`；如果需要，生成默认品牌色调地点
  → [5] 并行生成参考视频 × 4  pika MCP：SeeDance 各幕，资产图像作为参考
  → [5.5] 数字 UI 覆盖     pika MCP：将真实产品 UI / 标识符复合到数字揭示各幕 + OCR QA
  → [6] 编辑拼接各幕         pika MCP：60s 拼接基础（仅对话音频）
  → [7] 生成音乐             pika MCP：Kling 60s 软器乐背景床
  → [8] 字幕/下三分屏       pika MCP：添加 `add_captions` 以用于字幕；将下三分屏渲染为透明 `.mov`，然后在启用下三分屏时使用 `edit_video_compose` 将其叠加到主体上。
  → [9] 渲染 HTML 动画     pika MCP：5s 结尾卡片 — 作者内联 HTML，品牌套件内联字体，画幅与主体匹配，无角落杂乱，CSS @keyframes（不是 GSAP）
  → [10] 编辑拼接 + 音频混合  pika MCP：拼接主体 + 结尾卡片，然后混合音乐到完整的 ~65s
  → [10.5] 最终时长探测     pika MCP：分析最终_url 并在交付前强制执行 55s 时长下限
  → [11] 最终_url            保存 MCP 返回的最终_url；仅在本地回退创建了最终 MP4 时上传
  → [12] 交付
```

## 运营注意事项

保持主工作流专注于序列化。历史服务器验证细节存储在 `references/ops-notes.md` 中；这里仅保留活动约束：

- 每个SeeDance表演使用一个独特的`seed`（101、202、303、404）。相同的生成参数可以重放缓存的失败。
- Kling音乐底生成使用`provider: "kling-audio"`、`mode: "text_to_audio"`、`background: true`和`duration_seconds: 60`；MCP工作器生成一个10s的Kling种子并在本地扩展。
- 如果SeeDance拒绝真实人物创始人照片，重新生成创始人参考，使用更强的风格化，而不是重试相同的拒绝参考。
- 对于本地品牌套件标志，仅上传适合标志的栅格资产（`image/png`、`image/jpeg`或`image/webp`）。不要将SVG发送到`upload_asset`；从`build-a-brand`选择PNG导出或先栅格化。
- 在结束卡HTML中使用CSS `background-image: url(...)`来引用CDN托管的标志/照片资产；`<img crossorigin>`被CDN CORS阻止。
- 使用服务器端确定性工具来生成字幕、下三分之一合成、连接和混合。本地ffmpeg仅在`edit_video_compose`不可用且`state.lower_third = true`时作为备用。
- 将每个15s的表演分解为3个时间编码的子镜头。单镜头表演看起来是静态的。
- 以风格匹配位置构图开始每个表演，并在所有4个表演提示中重复相同的`WARDROBE LOCK:`句子。

## [1] 分析简报

```
analyze_brief(
  sources=[{ type: "url", url: <product_url> }],
  context: "创始人风格的60秒产品视频。需要：产品名称、一句话标语、3-5个关键特性、目标受众、品牌语气和行动号召。"
)
```
将结果保存为`brief`。你将在整个过程中引用`brief.product_name`、`brief.tagline`、`brief.key_features`、`brief.tone`和`brief.call_to_action`。

## [2] 解决产品UI资产，然后分析每个资产并推导出`product_type`

在分析资产之前，规范化`assets`，以便产品揭示镜头有一个真实的视觉参考：

1. 首先使用任何调用者提供的`assets`。
2. 如果没有提供，当存在时，从`brand.json.screenshots`中读取屏幕截图。
3. 如果`brand.json`没有屏幕截图，在品牌套件中查找明显的栅格屏幕截图或产品图像（`screenshots/`、`assets/`、`product/`或像`hero`、`screen`、`app`、`dashboard`、`product`这样的图像文件名）。
4. **在执行上述检查后，如果`assets`为空，对产品URL调用`capture_website`**：

```
capture_website(
  url: <product_url>,
  mode: "screenshot",
  mobile: false
)
# 将结果.image_url保存为assets[0].url，角色为"website_capture"。
```

如果产品可能是移动优先的，还运行第二个捕获，`mobile: true`，并在可用时保留两个URL。在继续之前将这些保存为真实的产品UI资产。

不要在没有至少一个真实产品UI/产品图像资产的情况下继续脚本编写、`generate_reference_video`或任何付费SeeDance调用，除非调用者明确设置了`product_type: "service"`并接受了一个仅限环境的视频。如果捕获失败或返回没有`image_url`，显示：`无法捕获<url>。请提供屏幕截图或托管的产品资产；创始人产品视频不会在没有真实产品UI的情况下静默发货。`

对于`assets`中的每个条目，运行`analyze_media`以提取内容+视觉风格+**资产类型**。在一个工具批处理中并行运行所有操作：

```
analyze_media(
  media: <asset.url>,
  query: '简要描述此产品图像。返回STRICT JSON:
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

如果`usable_product_assets`为空，并且你尚未尝试URL捕获，对产品URL调用`capture_website(mode:"screenshot")`，将返回的`image_url`附加到`assets`，对捕获运行`analyze_media`，在相同的新索引处保存分析，并重新构建`usable_product_assets`。因此，捕获的屏幕截图必须有自己的`asset_index`；不要重用标志/英雄/信息图的索引用于产品揭示。

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

如果用户明确传递了`product_type`，则使用该值并跳过自动推导；`service`仅在明确选择/接受时才有效。`product_type`值驱动**步骤[3]中选择的镜头以及步骤[5]中创始人如何揭示产品**。如果搞错，视频将在屏幕上显示错误的东西。

## 产品类型→揭示模式（此技能中最重要的表格）

`product_type`（在步骤[2]中设置）控制要选择的镜头，并且控制每个镜头中资产的揭示方式。**SeeDance提示中的揭示节拍是产品特定的；使用错误的节拍会使创始人手持一部手机，而品牌是T恤。**

对于`digital`产品，SeeDance提示仅负责创始人、摄像机移动、手机手势和一个空白/中性屏幕占位符。**不要要求Seedance或视频模型渲染可读的品牌标志或产品UI文本。** 真实的屏幕截图、产品UI和确切的品牌拼写在步骤[5.5]中合成。

| product_type | 揭示镜头 | 揭示节拍（用于SeeDance提示） | 哪些镜头获得资产 |
|---|---|---|---|
| `digital` | C-phone, E-phone | "创始人将她的手机举向摄像机；手机有一个为真实UI覆盖保留的空白中性屏幕占位符；不要渲染可读的UI文本或品牌标志" | 仅C和E镜头 |
| `physical_apparel` | G-hold, G-wear, E-detail | "创始人将一件炭洗图形T恤举向摄像机；衬衫设计完全匹配@ImageN——匹配图案/图形，不要凭空捏造" 或 "创始人穿着来自@ImageN的T恤——完全匹配图案" | 每个可见T恤的镜头（C/E/F + "穿着"变体） |
| `physical_object` | C-hold, E-detail, F-twoshot | "创始人举起[产品名称]朝向摄像机；产品完全匹配@ImageN——匹配形状、颜色、品牌" | 显示产品的镜头 |
| `consumable` | C-hold, E-detail, H-using | "创始人拿着/使用[产品]；包装/产品与@ImageN完全匹配" | 显示产品的镜头 |
| `service` | A, B, D, F（环境） | 没有特定的产品揭示——专注于创始人+环境 | 没有镜头参考资产 |

对于物理产品，每个在画面中显示产品的镜头都应传递该资产作为参考图像；否则SeeDance倾向于发明一个看起来通用的产品。对于服装，如果创始人穿着T恤并且脚本说"我们制作T恤"，那么创始人需要参考其中一个资产，即使在不是揭示时刻的镜头中也是如此。在`reference_images`中传递资产URL，并编写提示语言，如"创始人穿着来自@Image3的T恤——图案完全匹配"。

## [3] 编写脚本+角色声音+每镜头资产+每行节拍（你来做——不调用模型）

三个子产品，全部由你（Claude）在一个内联JSON中编写：

1. **`character_voice_profile`** — 描述角色默认交付的3-4行（贯穿所有表演以保持一致性）
2. **每镜头的`asset_index` + `reveal_beat`** — 这个镜头中可见的资产及其揭示方式
3. **每镜头的`beats[]`** — 行动指导，带有`emotion` + `physical` + 句子之间沉默节拍

这是将通用AI谈话头与真正有意图的角色区分开来的地方。在编写之前，阅读所有四个子部分下方（[3.0]创始人声音、[3a]角色声音配置文件、[3b]节拍、[3c]过渡、[3c.1]表演能量、[3d]完整JSON）。

### [3.0] 创始人声音——写一个广告，而不是功能列表

这项技能中最常见的失败模式是对话读起来像营销页面要点列表（"它可以推理。编码。甚至写你的电子邮件。没有代理。没有选择器。没有维护。将其连接到LangChain。LlamaIndex。MCP。GitHub上有24000颗星星。MIT许可。生产级.")——干净的副本，但不是创始人会在摄像机前销售他们产品的样子。现场反馈：*"脚本听起来像要点列表，而不是创始人会在摄像机前销售他们的产品。*"

在摄像机前向自己的产品进行广告的真正创始人使用：
- **第一人称所有权** — "我建造的"、"我们发布的"、"我们自己使用"、"老实说我们只是想让它无处不在"
- **个人利益或起源时刻** — 表演1应参考创始人亲身经历的挫折，而不是抽象地参考产品。"每次我尝试构建X，我都会遇到同样的墙"比"X很困难"更有力
- **对话连接词** — "看"、"老实说"、"事情是"、"所以"、"实际上"、"..."用于思考。这些在写作中是抛开的词，但自然说话的呼吸
- **"赌注"框架产品** — "如果X只是工作呢？"、"我们问自己"、"整个想法是"。创始人将他们的产品视为他们自己问自己的问题的答案，而不是能力列表
- **一个具体的锚点** — 一个具体数字、一个具体时间、一个具体场景。"去年24000名开发人员关注了我们"比"它很受欢迎"更有力。"在凌晨3点布局崩溃"比"刮削器不可靠"更有力
- **邀请能量CTA** — "来试试我们"、"去玩玩"、"我们只是想让它无处不在"。不是"停止刮削。开始提取。"（那是Don Draper的标语，不是创始人）。

**禁止模式**（每个都是用户经验证禁止的，不要重复）：

| ❌ 禁止模式 | 示例 | 原因 |
|---|---|---|
| 三重否定咒语 | "没有代理。没有选择器。没有维护。" | 感觉像营销咒语，不是人类语言 |
| 能力断奏 | "它可以推理。编码。甚至写你的电子邮件。" | 读起来像功能清单 |
| 集成列表作为广告 | "将其连接到LangChain。LlamaIndex。MCP。" | 列出集成一次通过——永远不要作为3个节拍的钩子 |
| 标语结尾 | "停止刮削。开始提取。" | 纯广告文案。创始人以邀请结束，而不是口号 |
| 规格作为广告 | "MIT许可。生产级。" | 规格放在README中，不是创始人摄像机前的口 |
| "只是"作为列表中的填充 | "只是一个API调用。只是一个任何URL。只是一个结构化JSON。" | "只是"重复读起来像营销强调，不是自然语言 |

**允许模式**（用这些代替）：

| ✅ 模式 | 示例 |
|---|---|
| 个人利益钩子 | "老实说——每次我尝试构建X，都发生了同样的事情。..." |
| "如果"框架 | "所以我们制作了Y。整个想法是：如果Z只是工作呢？" |
| 一个具体声明 | "去年我们达到了24000颗星星。人们正在将我们连接到 everywhere。" |
| 随意的痛苦旁注 | "把它交给一个URL。得到干净的 结构化数据。布局改变？没关系。" |
| 邀请结尾 | "如果你的代理需要实际看到活网——来试试我们。" |

**结构**（4个表演，每个表演约30-40个字=120-160个字，约50-60秒说）：

- **表演1：个人利益/痛苦。** 第一人称。参考创始人亲身经历的特定挫折。干净地落在命名的问题上。
- **表演2：赌注。** "所以我们制作了X。想法是——如果[痛苦]只是工作呢？" 一句话关于它实际上做什么（URL→数据，提示→图像等）。
- **表演3：证据+社区。** 一个具体数字（星星、客户、ARR）。一个随意的集成或使用场景的提及。语气：安静的自信，不是吹嘘。
- **表演4：邀请。** "如果[读者情况]——来试试我们。[URL]。[一条邀请线]。以温暖结束，而不是口号。

**在批准脚本之前自我测试。** 大声朗读每个表演的对话。如果你会在摄像机前为创始人感到尴尬，重写它。如果它听起来像30秒的商业旁白，重写它。如果一个段落有超过两个连续的短片段的标点符号，重写它。

### [3a] 推导`character_voice_profile` + `wardrobe_lock`

两个分开的字段，都需要：

**`character_voice_profile`**（3-4行）——角色如何交付所有内容：节奏、默认表情、标志性手势、手习惯、暂停行为、微笑何时出现。参考`brief.tone` + 角色参考图像（`character_image_url`或你生成的创始人参考）+ `product_type`。这是演员的"环境"——不是他们说什么，而是他们是谁。它贯穿所有4个表演，以保持一致性感觉是故意的，而不是偶然的。

**`wardrobe_lock`**（1句话）——角色在所有表演中穿着什么。SeeDance为每个15s生成读取@Image1，并且可能在表演之间解释不同的服装。衣柜锁句子在每个表演的提示中逐字重复，以保持服装一致。阅读创始人参考照片中穿着的服装并明确描述它。示例：*"在整个4个表演中穿着相同的炭洗连帽衫和深色乐队T恤，黑框眼镜"*。如果没有明确的衣柜锁，后面的表演可能会在第一个表演匹配@Image1时发明不同的服装。

**语气模板起点**（编排者选择/自定义自简报语气）：

| `brief.tone` | 默认节奏 | 面部 | 手部 | 停顿 |
|---|---|---|---|---|
| `casual` | 对话式，就像在咖啡馆向朋友解释 | 默认轻微似笑非笑，揭示要点时挑眉 | 做重大声明时摊开手掌，思考时手托下巴 | 以持续眼神交流代替填补沉默 |
| `playful` | 轻快断奏，富有表现力 | 俏皮感集中在眼部，频繁挑眉，笑意在笑点后一拍才到来 | 轻微肩部弹跳，生动地用手指计数 | 简短停顿，带着意味深长的眼神 |
| `professional` | 节奏稳健，从容不迫 | 柔和直接的眼神接触，克制的微笑 | 手部位置刻意而非持续，单一开掌手势 | 自信的沉默，不急于填补 |
| `technical` | 分析性，稍慢 | 默认分析性表情，眼睛转动思考后回归落点 | 手托下巴的思考手势，指向假想的图表 | 思考性停顿，视线向左上方看 |
| `disruptive / edgy` | 断奏，短句配以突发停顿 | 干燥面无表情为默认，俏皮的咧嘴笑闪现后随即消失 | 身体保持静止，面部承担主要表现 | 犀利停顿，头部轻微倾斜 |

**实例说明 —— 开发工具创始人（casual 语气，3D 皮克斯风格，20 岁女性）**：
> “休闲自信，就像在咖啡馆向朋友介绍产品。默认轻微似笑非笑。关键揭示时挑眉。思考时手托下巴，在做出重大‘亮相 A P I’声明时摊开手掌。以持续眼神交流代替填补沉默。面无表情地抛出笑点，让一丝小笑在一拍之后才浮现。”

**实例说明 —— 街头服饰创始人（playful/edgy 语气）**：
> “犀利、干燥的机智。说话快，用短句和突发停顿。默认轻微似笑非笑并抬起一边眉毛。对痛点（‘无聊’、‘平庸’）翻白眼。俏皮咧嘴笑在笑点处闪现但立即消失。手大多保持静止 —— 面部承担主要表现。”

### [3b] 逐行 `beats[]` —— 行级指导，而非幕级

每个镜头的对白被拆分为 `beats`。每个 beat 是一个短句子（或一段刻意的沉默），并配有独立的 `emotion` + `physical` 指导。beat 之间的沉默是表演的一部分 —— 用凝视、微表情、手势过渡来填充它。

包含 `text: "(beat)"` 的 beat 是无声的（无口述文本）—— 它仅描述句子之间自然停顿期间发生的视觉内容。在对白 beat 之间需要持续停顿以强调时，使用这些标记。

在步骤 [5] 构建 SeeDance 提示词时，beats 成为逐镜头的表演指导（去掉 `(beat)` 标记的对白文本成为 `<<<voice_1>>>` 负载）。

### [3c] `transition_from_prev` —— 编排同一片段中镜头间的连续摄影机运动

**SeeDance 的根本限制**：每个 15 秒的 SeeDance 生成渲染一个虚拟环境和一个虚拟摄影机。当多镜头提示词声明“镜头 C，然后镜头 A”但未指定它们之间的连续摄影机移动时，SeeDance 默认*重新取景*相同的摄影机位置（缩放或裁剪）。结果读起来像是跳跃式缩放，而非真正的剪切 —— 背景相同，人物大小不同。

**修复方法**：幕中除第一个镜头外的每个镜头必须声明一个 `transition_from_prev` 字段 —— 一行描述将我们从上一个镜头的取景带到当前镜头的*连续摄影机运动*。这样 SeeDance 就不得不渲染一个实际的空间移动，这意味着在该片段的片段中，人物身后会出现房间的不同部分。

模式：命名摄影机的起始位置，命名它结束的位置，命名连接它们的移动。有效的运动动词：轨道推入，拉远，推近，环绕，弧形，滑行，升降升起，升降降下，向上摇，向下摇，向左/右漂移。

示例：

| `transition_from_prev` | 效果 |
|---|---|
| “摄影机拉远并向左弧形移动，揭示她身后现在在画面内的砖墙和站立式办公桌” | 真实的空间变化 —— 不同的背景部分 |
| “推过手机屏幕，进入她面部的更紧密取景 —— 她身后的房间模糊” | 使用焦点转移 + 轨道移动的连续运动 |
| “摄影机以稳定距离顺时针围绕她滑行，在新的一侧拾取白板和植物” | 环绕揭示新背景 |
| “从她拿着手机的手拉远至中景，然后向右漂向窗户光线” | 两步连续移动 |
| ❌ “切至中景” / ❌ “现在我们看到她在中景” | 这些未描述运动 —— SeeDance 回退到同位置重新取景 |

**幕中的第一个镜头没有 `transition_from_prev`** —— 它确立取景。该幕中后续的每个镜头都有一个。

**SeeDance 可以在单个 15 秒片段内执行硬切，若明确提示。** 在带时间码的子镜头之间写 `Hard cut:`（代替 `Transition:`）以表示不同的取景变化 —— SeeDance 会遵守此规则并渲染真正的剪切，而非重新取景。将 `Transition:` 保留用于连续运动交接，其中你希望摄影机在取景之间滑行。模式：硬切感觉像真实编辑过的作品（不同取景，不同摄影机角度，不同表演能量）；转场感觉像单个移动长镜头。

### [3c.1] 表演能量底线 —— 每个 beat 都需要明确的身体动作

一种常见的失效模式：beats 仅以面部微表情编写（“轻微点头”，“挑眉”，“眼睛注视摄影机”）。SeeDance 将此渲染为近乎冻结的创始人 —— 眼睛几乎不动，缺乏存在感。结果读起来像是“静态，冻结，没有兴奋感”。

规则：每个 beat 的 `physical` 字段需要至少包含以下之一：
- 手部或手臂手势（开掌，用手指计数，轻蔑地一甩，指向自己/摄影机，手放胸前，更宽的手臂扫过，手触太阳穴思考）
- 躯干移动（前倾，后仰，轻微身体转向，肩部移动）
- 比微动更大的头部动作（向左/右转并转回，倾斜 8° 以上，缓慢摇头，随节奏点头）
- 定向眼神闪烁结合眉毛运动（向下看然后迅速抬眼看向摄影机等）

仅面部 beat 仅在以下情况下可接受：
- 口述句子之间的无声 `(beat)` 标记（那些*旨在*静止 —— 凝视是关键）
- 幕结束时的最终落地 beat，当摄影机已在移动时（摄影机承担主要工作）

编写 SeeDance 提示词时，确保组装的 “Acting beats” 块在物理上显得密集 —— 如果你扫描它看到连续五个 beat 都说“轻微点头”或“轻微假笑”而无其他动作，创始人看起来会像冻结的。用更大的动作重写。

### [3d] 脚本 JSON

```json
{
  "product_type": "<来自步骤 [2]>",
  "character_voice_profile": "休闲自信，就像在咖啡馆向朋友解释。默认轻微似笑非笑。关键揭示时挑眉。思考时手托下巴，做重大声明时摊开手掌。以持续眼神交流代替填补沉默。面无表情地抛出笑点，让一丝小笑在一拍之后浮现。",
  "segments": [
    {
      "act": 1,
      "shots": [
        {
          "type": "A",
          "asset_index": null,
          "beats": [
            { "text": "助手们非常出色。", "emotion": "陈述式的尊重 —— 说她真心这么认为", "physical": "柔和直接的眼神接触，轻微点头" },
            { "text": "(beat)", "physical": "微妙假笑浮现，眼睛注视摄影机" },
            { "text": "但这也有点...", "emotion": "俏皮的转折，省略号悬挂", "physical": "头轻微向右倾斜，省略号处视线短暂上移" },
            { "text": "缺乏形状。", "emotion": "面无表情地落地", "physical": "眼睛回到摄影机，单一轻蔑耸肩" }
          ]
        },
        {
          "type": "B",
          "asset_index": null,
          "transition_from_prev": "摄影机从中景缓慢推入更紧密的特写，轻微向右偏离轴线，使她身后的砖墙和窗户光线的不同切面可见",
          "beats": [
            { "text": "没有面部。没有声音。没有自己的个性。", "emotion": "断奏式轻蔑", "physical": "每个词时小摇头，‘个性’时挑眉" },
            { "text": "(beat)", "physical": "凝视持续，眼睛锁定摄影机，柔和微笑开始浮现" },
            { "text": "只是一个等待指令的空壳助手。", "emotion": "平淡，略带无奈的面无表情", "physical": "中性面部" },
            { "text": "(beat)", "physical": "柔和自信的微笑浮现，前倾开始" },
            { "text": "这即将改变。", "emotion": "坚定的信念，转折", "physical": "眼神锁定，‘改变’时单一自信点头" }
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
          "reveal_beat": "角色将手机举向摄影机，位于胸部高度，屏幕面向观众。屏幕是保留给步骤 [5.5] 中真实产品 UI 叠加的干净空白中性占位符；不要渲染可读的 UI 文本、品牌字标或虚假的应用界面。",
          "beats": [
            { "text": "遇见 A P I。", "emotion": "带有低调自豪的介绍", "physical": "手机举向摄影机，眼睛从屏幕闪烁到镜头" },
            { "text": "一个工作流，赋予你的产品面部、声音和故事。", "emotion": "温暖稳定的构建", "physical": "自由手用手指计数三样 —— 面部，声音，故事" }
          ]
        },
        {
          "type": "A",
          "asset_index": null,
          "transition_from_prev": "摄影机从手机拉远并轻微向左弧形移动，手机降低出画，结束在角色中景，此时她身后的办公桌和白板可见",
          "beats": [
            { "text": "以及制作视频、图像、音频的能力。", "emotion": "扩展承诺", "physical": "开掌手势在每个项目上扫得更宽" },
            { "text": "就在聊天内。", "emotion": "落地踢脚", "physical": "手平稳落下，眉毛上扬，轻微微笑浮现" }
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
            { "text": "设置只需三十秒。", "emotion": "理所当然的安慰", "physical": "走过一张办公桌，短暂瞥一眼笔记本电脑" },
            { "text": "打开仪表板，粘贴 URL，登录。", "emotion": "快速节奏检查清单", "physical": "边走边用手指计数三" }
          ]
        },
        {
          "type": "E",
          "asset_index": 1,
          "reveal_beat": "手持手机的特写。屏幕是保留给步骤 [5.5] 中真实产品 UI 叠加的干净空白中性占位符；不要渲染可读的 UI 文本、品牌字标或虚假的应用界面。",
          "transition_from_prev": "摄影机快速从她肩后推入，落在她手和手机的紧密特写上，loft 背景完全失焦",
          "beats": [
            { "text": "你的应用变成向导。", "emotion": "温和的意外揭示", "physical": "对着手机小笑，然后看向摄影机，眼神温暖" }
          ]
        },
        {
          "type": "A",
          "asset_index": null,
          "transition_from_prev": "摄影机从手机拉远并向上摇以找到她的面部，在中景中，砖墙和午后光线现在在她身后可见，位于 loft 中与镜头 D 不同的侧面",
          "beats": [
            { "text": "或者你构建的任何人。", "emotion": "休闲旁白", "physical": "小耸肩，轻微假笑" },
            { "text": "(beat)", "physical": "凝视持续，假笑淡化为温暖真诚" },
            { "text": "现在像与人一样与她交谈。", "emotion": "真正的重点 —— 安静的信念", "physical": "‘人’时单一点头，眼神锁定" }
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
            { "text": "技能已捆绑。", "emotion": "休闲自信，列表介绍", "physical": "下巴轻微倾斜，意味深长的眼神" },
            { "text": "播客。解说视频。U G C 广告。", "emotion": "节奏性三拍列表", "physical": "每个词时小点头，‘U G C’时挑眉" },
            { "text": "全部来自聊天。", "emotion": "落地标签", "physical": "开掌手势平稳落下，轻微微笑浮现" }
          ]
        },
        {
          "type": "B",
          "asset_index": null,
          "transition_from_prev": "摄影机从更宽的品牌背景取景缓慢推入亲密的中特写；环境退入柔和焦外，角色占据更多画面",
          "beats": [
            { "text": "所以停止与通用 A I 搏斗。", "emotion": "直接对话，低调挑战", "physical": "眉毛上扬，头部轻微倾斜" },
            { "text": "(beat)", "physical": "凝视持续，假笑增强" },
            { "text": "给它一个真实的存在。", "emotion": "品牌线，坚定地说出", "physical": "轻微向摄影机前倾，眼神锁定" },
            { "text": "从 example 点 com 斜杠 demo 开始。", "emotion": "温暖 CTA，邀请", "physical": "柔和自信的微笑，‘demo’时单一收尾点头" }
          ]
        }
      ]
    }
  ]
}
```

**逐镜头资产分配规则**：
1. **对于数字产品**：只有镜头 `C` 和 `E` 获得 `asset_index`（手机揭示时刻）。这些是步骤 [5.5] 的叠加指针，并排除在 Seedance 参考图像数组之外。其他镜头显示创始人而无特定 UI 参考。
2. **对于实体产品**：任何产品在画面中可见的镜头都获得 `asset_index`。资产是该产品外观的真实来源。幕可以在多个镜头中重用同一资产，或每个镜头显示不同资产以展示产品多样性。
3. **对于服务产品**：任何地方都不使用 `asset_index` —— 脚本依赖对话 + 环境。

每个非 null 的 `asset_index` 必须来自 `usable_product_assets[*].asset_index`。切勿将仅标志、仅英雄、信息图表、抽象品牌或 `other` 资产索引分配给产品揭示镜头。在对白中使用产品细节时，优先使用 `usable_product_assets[*].analysis.key_elements` 和 `usable_product_assets[*].analysis.visible_copy`，以便口述推介与屏幕上显示的真实产品工件保持一致。

**逐幕参考图像数组** = 该幕镜头中 Seedance 安全资产 URL 的并集。数字 `digital_screen` 资产不是 Seedance 安全的；它们保持仅叠加用于步骤 [5.5]。在 SeeDance 提示词中，按非数字资产在数组中的位置引用为 `@Image3`、`@Image4`（位置 3+ —— 位置 1 和 2 始终是角色 + 位置参考）。协调器在步骤 [5] 构建提示词时计算此映射。

**对话规则** —— 所有 4 幕的总计必须读出声在 55–60 秒内（~150 词/分钟 = 总计 ~150 词，每幕 ~37 词）。短促，有力，可发音。避免破折号（创始人不发音它们）。使用自然缩写。**引用用户的实际产品功能**（取自 `usable_product_assets[*].analysis.key_elements` 和 `usable_product_assets[*].analysis.visible_copy`），而非虚构的。

### TTS 发音重写

SeeDance 的原生唇形同步 TTS 逐字读取 `<<<voice_1>>>` 文本 —— 它没有语义意识知道“Ari”是名字，“Vercel”发音为“ver-SELL”，“UGC”是要拼写的缩略词，或“example.com”是 URL。按照你希望*发音*的方式重写对白文本，然后提交。应用这些替换：

| 模式 | 错误（直译） | 正确（为TTS重写） |
|---|---|---|
| 结尾为 `-i` 的名字 | "Ari" → "ah-REE" | **"Airy"**（或 "Tess" / "Mae" / "Sam" — 发音） |
| 发音拼写不熟悉的名字 | "Aoife" → 混乱 | **"Eefa"**（发音） |
| 非发音的产品/品牌名来自 `state.brand.name` 或 `brief.product_name` | "Vercel" → "Verkon"; "Linear" → "Lineer" | 创建一个仅用于TTS的发音别名，例如 **"ver-SELL"**，并在对话中/`<<<voice_1>>>` 内部提及品牌时使用它。 |
| 需要拼读的缩写 | "UGC" → "uhg" / "ugg"; "MCP" → "mehp" / 无声 | **"U G C"** / **"M C P"**（字母间用单个空格） |
| 将缩写当作单词念出 | "NASA" → "nasa" ✅（已经正确）；"IKEA" → "ikea" ✅ | 保持原样 |
| 域名点 | "example.com" → "examplecom" | **"example dot com"** |
| URL斜杠/路径 | "example.com/API" → "examplecom-api" | **"example dot com slash A P I"** |
| 符号 | "$50" → 无声；"@user" → "at user" 或无声 | **"fifty bucks"** / **"at-sign user"** |
| 格式奇怪的数字 | "2026" → 模糊不清 | **"twenty twenty-six"** 用于年份；**"two thousand"** 用于整数百位 |

当不确定品牌如何发音缩写（NASA 对比 N.A.S.A.）或非明显的产品名时，检查品牌的官方网站/视频。对于不明确的缩写，默认使用拼写的字母；对于非发音的名字，使用简单的发音别名。对于包含品牌的域名，结合两种重写方式：`Vercel.com` 在 `<<<voice_1>>>` 负载中变为 `ver-SELL dot com`。

**示例** — 原始脚本与TTS安全重写：

```
原始:  "UGC ads. All from chat. Launch the API. Start at example.com/API."
TTS-safe:  "U G C ads. All from chat. Launch the A P I. Start at example dot com slash A P I."

原始:  "Your app becomes Ari."
TTS-safe:  "Your app becomes Airy."

原始:  "Vercel ships at vercel.com."
TTS-safe:  "ver-SELL ships at ver-SELL dot com."
```

仅在对话文本中保留重写内容——你的脚本JSON的 `dialogue` 字段将逐字流入SeeDance提示，然后进入每个 `<<<voice_1>>>` 块。视觉界面保留规范原始拼写：`state.brand.name`，`brief.product_name`，产品UI覆盖层，标志，片尾文字，URL，文件名和QA预期必须保持不变。切勿用发音别名替换确定性视觉文本。

## 拍摄类型参考

每个拍摄根据 `product_type` 有不同变体。选择匹配的变体。

⚠️ **避免使用SeeDance会逐字解释的电影行业拍摄术语。** SeeDance将命名拍摄类型视为字面食谱——包括术语所隐含的任何*主体*。具体：
- ❌ "Two-shot" → 添加第二个人到画面（术语在电影中意为“两个主体的拍摄”，但SeeDance只看到“two” + “person”）。
- ❌ "Three-shot" — 同样陷阱。
- ❌ "Over-shoulder" / "OTS" → 在前景为角色添加一个虚幻的肩膀/后脑，供角色互动。角色会朝向那个虚幻的人，而不是相机。
- ❌ "Master shot" — 可能被误解为“老板/他们的主人”。
- ✅ "Medium shot", "Close-up", "Wide" 是安全的；它们在日常口语中常用。

每个情况下的修复方法是**描述相机看到的画面**，而不是暗示额外主体的电影词汇。示例：
- "Over-shoulder reveal" → "角色举起手机朝向相机，屏幕面向观众，高度在胸部"
- "Two-shot" → "角色与[产品/标志/环境]在画面中的宽框"
- "POV" → "从角色视线的低角度"

| 拍摄 | 所有变体 | 相机 |
|------|-------------|--------|
| A | 中景，腰部以上，角色居中。（没有产品在画面中，或者如果 `physical_apparel`：角色穿着品牌的衬衫——传递资产作为参考并添加 `reveal_beat`。） | 缓慢的微妙推近摇摄 |
| B | 中近景，胸部以上，亲密。。（没有产品，或者如果 `physical_apparel`：衬衫从领口可见，参考资产。） | 轻柔的手持呼吸动作 |
| C | **手机/产品直接对准相机。** `digital` → 角色举起手机朝向相机，高度在胸部，屏幕面向观众，步骤 [5.5] 的真实UI覆盖层使用空白中性屏幕占位符。（不是“over-shoulder”——这种词汇会触发虚幻的人。） `physical_apparel` → 角色举起T恤朝向相机，印花面向观众，匹配 @ImageN。 `physical_object` → 角色举起产品朝向相机。 `consumable` → 角色举起包装朝向相机。 | 缓慢推近朝向被举起的对象 |
| D | 广景+环境，全身在开阔空间中。（没有特定的产品时刻。） | 缓慢的跟踪拍摄，视差深度 |
| E | **近景揭示。** `digital` → 近景角色手持手机，步骤 [5.5] 的真实UI覆盖层使用空白中性屏幕占位符。 `physical_apparel` → 近景角色手持衬衫布料，设计清晰可见。 `physical_object` → 近景手持产品，细节镜头。 `consumable` → 近景使用/食用/饮用产品。 | 微妙调焦，缓慢仰拍 |
| F | **品牌环境拍摄。** 更宽的框，角色被产品/环境背景包围。 `digital` → 角色在品牌风格的环境中，没有可读的产品UI或标志。 `physical_apparel` → 角色穿着品牌的T恤，印花在画面中间清晰可见。 `physical_object` → 角色在书桌/架子上放置产品。 | 缓慢拉远，轻柔缩放 |

## [4] 创始人+自定义位置参考图像

在调用任何SeeDance之前准备 `character_url`：

- 如果 `founder_photo` 是HTTPS URL，设置 `founder_photo_url = character_url = founder_photo`。
- 如果 `founder_photo` 是本地路径，使用 `upload_asset` 上传它，然后设置 `founder_photo_url = character_url = public_url`。
- 如果 `founder_photo` 是 `generate`，调用 `generate_image` 并使用返回的URL：

```
generate_image(
  prompt: "<founder vibe>. 专业创始人肖像，干净工作室灯光，清晰对焦在面部，自信表情，适合作为视频生成的角色参考。",
  aspect_ratio: "3:4",
  resolution: "2K"
)
```

仅当用户提供了自定义位置时处理位置：

- 如果 `location_image_url` 是HTTPS URL，设置 `location_url = location_image_url`。
- 如果它是本地路径，使用 `upload_asset` 上传它并设置 `location_url = public_url`。
- 如果它是文本描述，使用 `generate_image` 生成自定义位置参考。
- 如果没有提供自定义位置，在此处不做任何操作。步骤 [4.5] 在 `state.brand` 存在后会生成默认品牌色调背景。

将结果URL保存到 `state`。如果SeeDance因内容政策拒绝创始人参考，参见“已知基础设施问题”——使用更强的风格化重新生成。

## [4.5] 品牌套件摄入（始终——阶段0保证 `brand_kit_path`）

`brand_kit_path` 由阶段0需要——无论是用户提供的还是首先使用 `build-a-brand` 构建。解析一次并跨片尾和下三分之一重复使用。如果在交互模式下缺少文件夹，请要求用户提供或重建品牌套件再继续。在非交互式快速通道中，首先尝试 `build-a-brand --quick` 分支；如果那不能生成套件，则停止并显示一个紧凑的缺失字段列表。

首选源是存在时的 `brand.json`。否则从 `build-a-brand` 导出中提取：
- `brand.md` 用于名称、标语、声音、字体名称和标志描述。
- `tokens/tokens.json` 用于颜色和字体令牌。
- `logo/` 资产用于标志、符号/图标和组合标志。

提取到 `state.brand`：

| `state.brand` 字段 | 源 | 备注 |
|---|---|---|
| `name` | `brand.json.name` 或 `brand.md` 快速参考 | 品牌显示名称 |
| `wordmark_path` | `logo.wordmark.path` 或最佳光栅 `logo/wordmark/*.{png,jpg,jpeg,webp}` | 通过 `upload_asset` 上传本地光栅资产，将 `public_url` 保存为 `state.brand.wordmark_url`；不要上传SVG |
| `icon_url` | `logo.icon_mark.path` 或最佳光栅 `logo/symbol/*.{png,jpg,jpeg,webp}` | 通过 `upload_asset` 上传本地光栅资产，将 `public_url` 保存为 `state.brand.icon_url`；不要上传SVG |
| `colors.primary` | 调色板角色 `ink_primary`，`surface_dark` 或 `tokens.color.text` | 文本和边框颜色 |
| `colors.surface` | 调色板角色 `surface_page_bg`，`surface_white` 或 `tokens.color.background` | 页面/背景颜色 |
| `colors.accent` | 调色板/CTA/主要品牌颜色或 `tokens.color.primary` | 片尾CTA药丸背景+下三分之一强调色 |
| `colors.highlight` | 调色板/令牌中的次要亮色/高亮色 | 下三分之一边框/高亮 |
| `fonts.display_family` | 字体显示令牌或 `brand.md` | 如果可用则直接使用；否则回退到 Space Grotesk |
| `fonts.text_family` | 字体正文/文本令牌或 `brand.md` | 回退到系统无衬线字体 |
| `fonts.mono_family` | 如果存在字体单字令牌 | 回退到 Space Mono |

**上传步骤是必需的**，当品牌套件资产是本地文件时。没有公共标志/图标URL，`render_html_animation` 渲染的HTML无法访问它们。使用MCP `upload_asset` 流程仅上传光栅标志文件，并将返回的 `public_url` 值保存到 `state.brand`。`upload_asset` 拒绝 `image/svg+xml`；如果最佳标志是SVG，选择品牌套件中的兄弟PNG导出或通过将SVG内联在HTML `<svg>` 块中并使用返回的PNG `public_url` 通过 `html_to_png` 光栅化SVG为PNG。

**品牌色调背景默认位置**——当 `location_url` 未由步骤[4]设置时，通过 `html_to_png` 渲染纯色PNG，使用 `state.brand.colors.accent`。匹配请求的视频宽高比，以免后续裁剪参考：

| `aspect_ratio` | 背景尺寸 |
|---|---|
| `16:9` | 1920×1080 |
| `9:16` | 1080×1920 |
| `1:1` | 1080×1080 |

将返回的 `file_url` 保存为 `location_url`。这产生干净的工作室拍摄美学——角色在品牌的强调色平无缝墙背景前，没有家具或背景细节。这比AI生成的办公室场景更可靠，并可靠地渲染SeeDance。

```
html_to_png(
  html: "<body style='margin:0;background:{accent}'></body>",
  format: "png",
  mode: "sync",
  raster_options: { viewport_px: { width: W, height: H }, device_scale: 1 }
)
# 保存结果.file_url 为 location_url
```

## [5] 并行生成4个SeeDance场景

**关键**：步骤[5]需要 `generate_reference_video`（多参考）。此技能提示模板中的 `@Image1` / `@Image2` / `@Image3` 令牌**仅由 `generate_reference_video` 解析**。如果你错误地调用了 `generate_video`（单图像i2v），`@ImageN` 令牌将被静默忽略，SeeDance将仅从提示文本中产生幻觉UI，通常会拼写错误产品名。在启动任何付费视频生成之前，停止并修复工具调用。

对于 `product_type: "digital"`，这现在是一个风格/手势生成步骤，而不是可读UI步骤。不要要求SeeDance拼写产品名，渲染可读的品牌标志，或重现产品屏幕文本。手机揭示必须要求空白中性屏幕占位符，因为真实产品UI将在步骤[5.5]中合成。不要在 `reference_images` 中传递 `digital_screen` 资产；任何 `digital_screen` 资产索引都是步骤[5.5]仅有的覆盖指针，即使混合或明确非数字运行也有物理资产。

对于每个场景，**收集该场景中所有拍摄中 `asset_index` 值的并集** 来构建 `reference_images` 数组：

```
act_asset_indices = unique(shot.asset_index for shot in act.shots if shot.asset_index !== null)
act_asset_entries = usable_product_assets.filter(entry.asset_index in act_asset_indices)
if act_asset_entries.length !== act_asset_indices.length: 停止；拍摄引用了不可用/缺失的 asset_index
seedance_asset_entries = act_asset_entries.filter(entry => entry.asset_type !== "digital_screen")
act_asset_urls    = [entry.asset_url for entry in seedance_asset_entries]
reference_images  = [character_url, location_url, ...act_asset_urls]
```

资产条目的位置在 `reference_images` 中决定了其 `@ImageN` 令牌（位置1,2是角色+位置；可用的产品资产从位置3开始）。在编写提示时，将每个非数字拍摄的 `asset_index` 映射到匹配的 `seedance_asset_entries` 位置。对于任何 `digital_screen` 资产，不要在SeeDance提示中引用 `@ImageN` 令牌；使用空白手机屏幕占位符语言，并让步骤[5.5]消耗原始 `act_asset_entries` 条目。

### 提示模板

**通过 `@Image1` 参考而非描述性提示文本来指代角色。** 当提示说“年轻的创意街头服饰创始人”并且 `@Image1` 是角色参考时，这两个描述可能会冲突——SeeDance可能会试图通过发明第二个人物来满足两者。相同规则适用于位置和 `@Image2`。让参考图像承载视觉身份。

每个场景的提示有三层，从上到下：

1. **角色+位置身份**（始终相同的开篇行）。
2. **角色声音**——场景提示逐字重复 `script.character_voice_profile`。这通过每个拍摄传递演员个性。
3. **每拍摄块**——每个拍摄获取其构图（或 `reveal_beat` 如果定义），然后是来自拍摄 `beats[]` 的“表演节奏”列表，然后是 `<<<voice_1>>>` 内部的对话。

⚠️ **开篇行、`WARDROBE LOCK:`, `Background context:`, `<<<voice_1>>>`, `Transition:` / `Hard cut:`, 以及结尾的 `Native lip-synced dialogue audio, no music overlay.` 行都是承重**——每个行都有文档记录在 `## Load-bearing phrases` 靠近底部的特定失败模式。任何行的释义都会无声地破坏配方（字面背景、唱歌歌词、跳跃变焦、服装漂移等）。逐字保留它们；它们周围的连接散文是你的创作范围。

模板：

```
角色（匹配 @Image1）在一个设置中，其视觉风格、调色板、灯光和材料与 @Image2 匹配。

CHARACTER VOICE: {script.character_voice_profile}
WARDROBE LOCK (跨所有4个场景逐字重复): {script.wardrobe_lock}

拍摄 {first}: {如果拍摄.reveal_beat 存在: 拍摄.reveal_beat ELSE: 构图 + 相机表中的拍摄}. 背景上下文: {空间中的独特物理位置——哪个墙 / 窗户 / 特征在角色后面}。
表演节奏：
  • "{beat[0].text}" — {beat[0].emotion}; {beat[0].physical}.
  • (沉默) — {沉默节奏物理}.
  • "{beat[N].text}" — {beat[N].emotion}; {beat[N].physical}.
<<<voice_1>>>{连接 beat 文本，排除 (beat) 标记，保留原文中的句点和逗号}<<<voice_1>>

[如果2个以上拍摄在当前场景中:] 过渡: {拍摄[1].transition_from_prev}.
拍摄 {second}: {构图或 reveal_beat}. 背景上下文: {与拍摄 {first} 不同的物理位置——不同墙 / 不同角度 / 不同背景特征}.
表演节奏: ...
<<<voice_1>>>...<<<voice_1>>

[如果3个拍摄:] 过渡: {拍摄[2].transition_from_prev}.
拍摄 {third}: ... 背景上下文: {第三个独特物理位置——必须与拍摄 {first} 和 {second} 视觉不同}。

原生口型同步对话音频，无音乐覆盖。
```

模板说明：
- 以 **"匹配 @Image1 的角色在视觉风格与 @Image2 相符的场景中"** 开头——绝不能是 "在匹配 @Image2 的地点内"。SeeDance 会根据 @Image2 中的文字背景进行读取，如果使用 "在地点内"——参见已知基础设施缺陷。
- 不要用散文描述角色——SeeDance 从 `@Image1` 中读取视觉身份。例外：通过 `WARDROBE LOCK` 行明确锁定衣橱（例如："整个 4 个场景都穿着相同的煤灰色连帽衫搭配深色乐队 T 恤"）。仅 @Image1 无法跨不同的 15 秒世代锁定衣橱。
- 不要添加与参考资料相矛盾的美学形容词。如果 `@Image1` 是 3D 皮克斯风格的角色，不要在任何提示中添加 "照片逼真"。
- **角色声音 + WARDROBE LOCK 行每个提示只出现一次，在镜头之前**。它们为 SeeDance 初始化演员的整体氛围和服装连续性。
- **每个镜头块都包含一个 `背景上下文:` 行**，描述空间中的一个独特物理位置——不同的墙壁，不同的窗户，与其他镜头不同的背景特征。这迫使 SeeDance 渲染场景多样性，同时将品牌美学锚定在 @Image2 上。
- **`(beat)` 标记保持在 `<<<voice_1>>>` 负载之外**。它们只是动作指示——对话文本中句子之间的自然停顿就是它们发生的地方。
- **每个场景块（第一个场景除外）都获得一个 `Transition: …` 行**，由 `shot.transition_from_prev` 构建。这叙述了镜头之间的相机移动，迫使 SeeDance 渲染真实的空间运动（角色身后房间的不同部分）而不是无动机的重新构图，看起来像跳跃变焦。

### 工作示例——`physical_apparel`，第 2 场景（带声音和停顿）

第 2 场景有 `[C, A]` 镜头。镜头 C 有 `asset_index: 0` 并有一个关于搜索历史 T 恤的揭示停顿。镜头 A 没有资产索引。资产 0 = `@Image3`。角色声音配置文件是来自步骤 [3a] 的街头服饰创始人示例。

```
匹配 @Image1 的角色在视觉风格、调色板、照明和材料与 @Image2 相符的场景中。

角色声音：尖锐的干幽默。快速说话，句子简短，突然停顿。默认轻微的微笑，一只眉毛抬起。在痛点上翻白眼。在笑点时露出淘气的微笑，但立即消失。双手基本保持静止——脸部做所有工作。
衣橱锁定：在整个 4 个场景中始终穿着相同的煤洗品牌图形 T 恤，搭配未扣上的靛蓝色牛仔 chore 外套。

镜头 C：角色将煤洗图形 T 恤举向相机，平放在胸高。衬衫设计完全匹配 @Image3——'我看到了你的搜索历史'，带有醒目的白色文字的惊恐猫插图。精确匹配图案，不要虚构。相机：缓慢的横向弧形摇摄朝向视线。背景上下文：站在储物架附近，右侧阁楼的砖墙，来自相机左侧的柔和正午窗光。
表演停顿：
  • "你知道你差点输入的那个东西吗？"——知道低声指责；'差点输入'时眉毛抬起，轻微头倾。
  • "那个奇怪的搜索？"——保持表情，眉毛保持抬起，微笑的暗示出现。
  • (沉默)——停顿落地，微笑增长，眼睛看向镜头。
  • "你的猫看到了。"——淘气的冷面；稍微抬高衬衫，自信地点头。
<<<voice_1>>>你知道你差点输入的那个东西吗？那个奇怪的搜索？你的猫看到了。<<<voice_1>>>

过渡：相机从持有的衬衫中拉回，略微向左弧形，衬衫从画面中落下，我们以中景结束，现在可以看到服装架和砖墙。
镜头 A：中景，腰部以上，角色居中，看向相机。相机：缓慢的微妙推入摇摄。
表演停顿：
  • "我们把它变成了 T 恤。"——事实上的揭示；眉毛抬起，轻微的微笑出现。
  • "——带态度的图形 T 梭。"——品牌行标点；'态度'上出现微笑，眼睛保持。
<<<voice_1>>>我们把它变成了 T 恤——带态度的图形 T 梭。<<<voice_1>>>

原生唇同步对话音频，无音乐叠加。
```

### 镜头间物理产品一致性

对于 `physical_apparel`，如果角色在多个场景中**穿着**品牌的 产品（例如，没有特定产品揭示的场景，但角色仍在品牌 T 恤中），选择一个英雄衬衫资产，并使用提示语言如 *"角色穿着来自 @Image3 的 T 恤——图案完全匹配"* 将其传递给这些场景。否则 SeeDance 会发明一个看起来通用的衬衫，这将破坏资产覆盖目标。

### 并行发射所有 4 个场景——每个场景 3 个子镜头

在单个工具批量中并行发射所有 4 个场景。每个场景提示应包含 3 个时间编码的子镜头；单个 15 秒剪辑渲染为静态、冻结的创始人，无论提示多么详细。如果一个运行看起来"非常静态，没有肢体语言，相机工作无聊"，修复方法是将每个场景分解为提示中的 3 个时间编码的子镜头。

**默认分解：每个场景 3 个子镜头**，按对话密度大小（例如 `(0-4s)`，`(4-9s)`，`(9-15s)`）。

每个子镜头需要：
1. **不同的相机构图**——绝不能有两个连续的子镜头使用相同的镜头类型。混合中景/特写/广角/低角度。用户将多样性视为制作价值。
2. **不同的相机运动**——推入，拉回，横向弧形，轨道，手持，静态保持，聚焦切换。不全是"缓慢推入"。
3. **空间中不同的物理位置**——参见"已知基础设施缺陷"中的位置参考规则。每个镜头必须描述角色身后不同的墙壁/窗户/特征，以便 SeeDance 在空间中移动而不是重复一个字面上的背景。
4. **每个停顿一个有活力的物理动作**——参见上文 [3c.1]。手势，倾斜，转头，肩膀移动。没有仅面部动作的停顿。
5. **该窗口的对话子部分**，用 `<<<voice_1>>>...<<<voice_1>>>` 令牌在镜头块内包裹。

SeeDance 发射模式：

```
generate_reference_video(
  provider: "seedance",
  resolution: "1080p",
  aspect_ratio: "16:9",
  duration: 15,
  seed: 101,                   # 每个场景唯一（101，202，303，404）——打破幂等性缓存
  sound: true,                 # 来自每个 <<<voice_1>>> 块的原生唇同步
  reference_images: [character_url, location_url, ...本场景的资产],
  prompt: <完整提示——见上方模板，3 个时间编码的子镜头内联>
)
# ... × 4 场景，全部在相同消息中 ...
```

说明：
- 每个场景在 SeeDance 上运行约 3-8 分钟。如果生成异步完成，请遵循 MCP 工具返回的状态句柄，直到场景达到终端状态。
- 完整提示（开头行 + CHARACTER VOICE + 3 个子镜头与表演停顿 + 每个镜头的 `<<<voice_1>>>` + 过渡行）放在单个 `prompt` 参数中。SeeDance 没有 `shots:[]` 数组——多镜头结构编码在散文中。
- 使用唯一种子（101，202，303，404），以便看起来相同的调用不会哈希到相同的缓存任务 ID。`seed` 参数仅限 SeeDance。

将返回的 4 个 URL 按提交顺序保存为 `act_urls = [act1, act2, act3, act4]`。

## [5.5] 确定性数字 UI 叠加

此步骤在所有四个 Seedance 场景可用后运行，并在步骤 [6] 之前运行。为提高效率，首先运行下文的跨场景身份 QA，并使用最终接受的 `act_urls`；如果身份 QA 后来重试一个场景，丢弃旧的叠加输出并重新运行此步骤。其工作是为数字产品揭示提供像素级基础：观众看到的手机/产品屏幕视觉来自真实的捕获屏幕或渲染文字标志，而不是来自 Seedance。

如果 `product_type !== "digital"`，设置 `ui_grounded_act_urls = act_urls` 并继续。

如果 `product_type === "digital"`：

1. 从每个脚本镜头中构建 `digital_reveal_shots`，其类型为 `C` 或 `E`。每个脚本 `C` 或 `E` 数字揭示必须具有非空的 `asset_index`，并且该索引必须解析为 `usable_product_assets` 中的 `digital_screen` 条目。如果任何脚本 C/E 数字揭示有 `asset_index: null`，停止并显示脚本镜头；不要继续到 Seedance 连接或复制原始 `act_urls`。从验证的揭示镜头构建 `digital_reveal_plan`。每个计划的叠加存储：
   - `act`，`shot`，`asset_index`，`asset_url`
   - `visible_copy` 来自 `usable_product_assets[*].analysis.visible_copy`
   - `brand_name = state.brand.name`
   - 预期文本列表：确切的 `brand_name` 加上任何简短、可读的 `visible_copy` 短语对提案很重要

   如果 `digital_reveal_plan` 为空，停止并显示脚本镜头加上 `usable_product_assets`；不要无声地发送一个数字产品视频而没有真实 UI。如果任何脚本 C/E 数字揭示指向缺失或非 `digital_screen` 资产，停止在组合之前。当数字揭示缺少其叠加时，不要复制原始 `act_urls`；只有没有数字揭示镜头的场景才能通过不变。

2. 对于每个唯一的 `asset_url`，使用 `render_html_animation` 渲染 15 秒叠加剪辑，使用 `format: "mov"` 当需要 alpha 时。将返回的 URL 保存为 `ui_overlay_clip_url`。
   - HTML 应该将真实的屏幕截图/捕获 UI 放置在具有正确纵横比的圆角手机屏幕框架内。
   - 如果真实屏幕截图的品牌文字标志在缩放后太小而无法阅读，请包括一个确切的确定性文字标志行使用 `state.brand.name`；不要发明一个更短的别名。
   - 保持叠加背景透明或视觉隔离，以便它作为确定性手机/UI 叠加工作在生成的场景上。

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

使用手机屏幕位置，当生成的手机目标足够稳定时。如果手机目标不够稳定以干净地覆盖，使用稳定的叠加面板位置，该位置不会覆盖创始人脸部或标题区域。将每个编辑结果保存到 `ui_grounded_act_urls[act - 1]`；未修改的场景从 `act_urls` 复制通过。

4. 当合成通道后仍需要短确切的品牌标签时，调用 `edit_text_overlay` 在该场景上使用 `text: state.brand.name`。这仅用于确定性品牌拼写，不是标题。将更新后的 URL 保存回 `ui_grounded_act_urls[act - 1]`。

5. 在与 `extract_frame` 和 `analyze_media` 连接之前，对每个叠加揭示场景运行 OCR QA：

```
extract_frame(video_url: ui_grounded_act_urls[act - 1], time_s: <揭示镜头的中点时间>)

analyze_media(
  media: overlay_qa_frame_url,
  query: "OCR 读取产品 UI 或文字标志上的所有可见文本。仅返回 JSON： {
    \"brand_name_visible\": \"yes\" | \"no\" | \"unclear\",
    \"brand_name_exact\": \"yes\" | \"no\" | \"unclear\",
    \"visible_copy_ok\": \"yes\" | \"no\" | \"unclear\",
    \"garbled_text\": string[],
    \"misspellings\": string[],
    \"verdict\": \"clean\" | \"degraded\" | \"catastrophic\"
  }.确切的预期品牌名称是 ${brand_name}。预期的确切的可见_copy 是 ${visible_copy}; visible_copy_ok: "yes" 仅当重要的预期 UI 复本存在/可读，或当没有提供短可见_copy 时。例如 Lineer, Figoff, 随机字母，格式错误的 UI 复本，或替换预期可见_copy 的 AI-想象 UI 复本都是 garbled/misspelled."
)
```

只有 `brand_name_visible: "yes"`，`brand_name_exact: "yes"`，`visible_copy_ok: "yes"`，和 `verdict: "clean"` 可以继续。如果 OCR 说品牌缺失，拼写错误，混乱，预期的可见_copy 缺失/被替换，或 `verdict` 是 `degraded` / `catastrophic`，停止并显示 `overlay_qa_frame_url`，`ui_overlay_clip_url`，预期的 `brand_name`，预期的 `visible_copy`，和 QA JSON。不要继续到步骤 [6] 与原始或 AI 想象的手机文本。

### 步骤 [6] 之前的跨场景身份 QA

在 `edit_concat` 之前，对单个可比较的视觉文物运行跨场景身份检查。目标是捕获创始人替换，以便在 60 秒身体已经拼接后仍然可以重新生成不良场景。

1. 从每个场景的三个子镜头窗口中提取一个代表性帧。场景中间的一个帧不够；创始人替换可能发生在第一个或最后一个子镜头中，仍然可以通过。
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

2. 使用 `html_to_png` 渲染一个身份联系表。使用 CSS `background-image: url(...)` 对每个远程图像。该表必须包含 13 个标记面板在一个图像中：`创始人参考` (`founder_photo_url` / `character_url`)，然后 `场景 1 镜头 1`，`场景 1 镜头 2`，`场景 1 镜头 3`，通过 `场景 4 镜头 3`。将返回的文件保存为 `identity_contact_sheet_url`。

```
html_to_png(
  html: "<html>... founder reference ... 场景 1 镜头 1 ... 场景 1 镜头 2 ... 场景 1 镜头 3 ... 场景 2 镜头 1 ... 场景 3 镜头 1 ... 场景 4 镜头 3 ...</html>",
  format: "png",
  mode: "sync",
  raster_options: { viewport_px: { width: 2200, height: 1600 }, device_scale: 1 }
)
```

3. 对 `identity_contact_sheet_url` 运行一个 `analyze_media` 调用：

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
  将创始人参考面板与所有 12 个场景面板（场景 1 镜头 1 到场景 4 镜头 3）进行比较：检查脸部、头发、年龄、体型和衣橱；不要将正常的姿势、表情、相机角度或照明变化视为身份漂移。"
)
```

如果无法渲染联系表，停止并显示联系表失败；不要继续未验证身份。只有干净的 `yes` / `yes` / `yes` 身份 QA 才能继续。如果 QA 返回 `same_founder_as_reference: "no"` 或 `same_founder_as_reference: "unclear"`，`same_founder_across_acts: "no"` 或 `same_founder_across_acts: "unclear"`，`wardrobe_consistent_with_lock: "no"` 或 `wardrobe_consistent_with_lock: "unclear"`，`bad_act_numbers` 非空，`bad_frame_labels` 非空，或 `verdict: "degraded"` 或 `verdict: "catastrophic"`，不要继续到拼接。仅重试不良场景一次，使用相同的提示，相同的 `reference_images`，以及新的种子（`original_seed + 1000`）加上一句提示：`身份连续性是强制性的：整个场景的镜头创始人始终是 @Image1 的人。` 重试后，提取重试场景的所有三个帧时间，重建完整的联系表，并重新运行相同的 QA。如果任何 `act_urls` 条目在不良场景重试后更改，丢弃 `ui_grounded_act_urls` 和任何以前的叠加/OCR 证据，重新运行步骤 [5.5] 对最终 `act_urls`，然后在其 OCR QA 之前运行步骤 [6]。如果重试仍然失败跨场景身份 QA，停止并显示 `identity_contact_sheet_url`，不良场景 URL(s)，`bad_frame_labels`，和 QA JSON；不要发送一个拼接的视频，其中创始人不同。

### 时长下限和部分场景恢复

在步骤[6]之前，必须提供所有4个act_urls。不要拼接部分act列表。

三个完成的act加上结束卡片会生成一个约50秒的资产，这低于55秒的时长底线，并且不能报告为成功的创始人视频。

如果一个SeeDance act达到失败终端、达到`cancelled`状态，或者由长时间轮询合约终端或成功取消，而其他act已完成：
- 使用相同的提示、`reference_images`、`duration`、`sound`、`resolution`和`aspect_ratio`重新尝试缺失的act一次，但使用新的种子（`original_seed + 1000`）。不要重新运行成功的act。
- 如果重试完成，将那个URL插入原始act槽位，并继续使用`act_urls = [act1, act2, act3, act4]`。
- 如果重试无法完成，停止并暴露上游SeeDance超时。你可以返回完成的act URL作为诊断预览，但不要交付部分拼接作为`final_url`，不要称其为生产就绪，并且不要进行到步骤[6]。

在原始任务仍然是`queued`、`running`或`processing`时，不要重试停滞的act。继续以可见进度轮询它，然后在使用缺失act的重试之前，在15分钟的总上限之前调用`task_cancel({task_id})`。

## [6] 将act拼接成60秒基础

```
edit_concat(video_urls=ui_grounded_act_urls)
```
保存为`base_url`（60秒，16:9，原生对话音频）。`ui_grounded_act_urls`对于非数字产品等于`act_urls`；对于数字产品它包含步骤[5.5]叠加揭示act。当存在数字UI叠加计划时，不要将原始`act_urls`输入拼接。

## [7] 生成背景音乐 — INSTRUMENTAL，目标约60秒

**模式是固定的。声音是每个品牌的创意决策。** 使用Kling音频，因为它支持`background: true`，并且MCP工作现在处理长床间隙：它生成一个10秒的Kling种子，然后使用ffmpeg本地循环/交叉渐变以请求的60秒扩展它。WHAT提示中放入什么流派/乐器/情绪是你的工作——选择一个符合品牌基调、创始人声音和产品的东西。不要逐字复制下面的钢琴示例；这只是可能的声音，不是模板。

### 固定模式（不要更改）：
- `provider: "kling-audio"`
- `mode: "text_to_audio"`
- `background: true`
- `duration_seconds: 60`
- 没有`lyrics`字段。Kling只使用提示。
- 没有第二个提供程序调用或手动平铺。MCP工作拥有单种子扩展路径。
- `prompt`必须为`<= 200`个字符。Kling使用验证代码`1201`拒绝更长的提示，所以保持风格快照简短。

### 创意决策（每个视频——从`brief.tone` + 脚本氛围 + 产品背景中选择）：

不同品牌的声音注册示例。不要使用这些字面意思——匹配你品牌的氛围：

| 品牌注册 | 流派方向 | 声音调色板 |
|---|---|---|
| 技术/开发工具/B2B SaaS | 企业电影配乐，苹果主题平静 | 温暖的钢琴，柔和的合成垫，稀疏的低频脉冲，80–90 BPM |
| 活泼/街头服饰/消费 | lo-fi嘻哈，休闲节拍 | 灰尘鼓，爵士和弦刺，黑胶唱片嘶嘶声，70–85 BPM |
| 颠覆性/边缘/金融科技/加密货币 | 最小化电子，黑暗合成波 | 模拟合成贝斯，侧链垫，半时间鼓点，90–100 BPM |
| 时尚/奢侈/生活方式 | 最小化浩室，现代时尚电影配乐 | 过滤的浩室垫，柔和的4-on-floor鼓点，法国触和弦，100–110 BPM |
| 健身/能量/运动 | 驱动电子脉冲，健身注册 | 脉冲合成贝斯，构建arp，踩镲八分音符，110–125 BPM |
| 食物/酒店/咖啡馆 | 乐器温暖，独立民谣 | 指弹吉他，轻击镲，轻柔的立式贝斯，80–95 BPM |
| 电影/品牌故事/纪录片 | 管弦乐配乐，希望的高潮 | 弦乐层，柔和的钢琴主旋律，膨胀的铜管，速度构建 |
| 游戏/开发工具/创作者工具 | 芯片音乐-现代混合，复古像素 | 方波主旋律，现代合成垫，响亮的镲，105–120 BPM |

不确定时：阅读`brief.tone`（技术/休闲/活泼/专业/颠覆性），并选择一个不会在创始人声音配置文件+脚本的情感弧旁边感觉奇怪的注册。匹配能量，不要与之对抗。

### 典型调用（将你的创意方向代入提示，保持`<= 200`个字符）：

```
generate_music(
  provider: "kling-audio",
  mode: "text_to_audio",
  background: true,
  duration_seconds: 60,
  prompt: "<=200 chars: 软乐器背景床；<注册>，<主要乐器>，<情绪>，<BPM>；无歌词；为旁白留出空间>"
)
```

工作原理（承重）：
- **Kling生成一个10秒种子**：付费提供程序调用保持简短并支持背景。
- **工作本地扩展**：MCP循环/交叉渐变10秒种子，使用本地ffmpeg达到`duration_seconds: 60`，然后返回扩展的CDN `audio_url`。
- **`prompt`字段携带风格快照**。包括"软乐器背景床"、"无歌词"和"为旁白留出空间"，以便混音不要与创始人对话对抗。保持它`<= 200`个字符；如果Kling返回`1201`，缩短相同的风格想法，而不是重试长提示。

保存为`music_url`。读取`result.duration_seconds`：
- 如果`>= 55s` → 混音。预期路径与Kling工作扩展。
- 如果`< 55s` → 不要无声接受短的床。使用相同的`kling-audio`调用重试一次；如果它仍然返回短，停止并暴露工具结果，因为工作扩展路径没有满足合同。

**禁止的反模式**（每个都经验性地导致失败）：
- ❌ `provider: "minimax-music"`用于默认生成的床——MiniMax不支持`background: true`，并且可以在旁白下前景化旋律。
- ❌ 在技能中手动10秒平铺——MCP工作已经本地扩展了一个10秒的Kling种子。
- ❌ 仅在`prompt`文本中放入持续时间（"60秒乐器"）——使用`duration_seconds: 60`。
- ❌ 添加`lyrics`字段——这个路径是Kling提示唯一的。
- ❌ 对每个品牌复制相同的钢琴和垫示例——配方是模式，不是声音。每个品牌选择一个注册。

## [8] 组合层——下三分之二+字幕

> **管道顺序注意**——音乐混音在步骤[10]发生，在结束卡片拼接之后。在拼接结束卡片之前将音乐混入正文会留下沉默的结束卡片（音乐轨道在剪辑处结束）。始终：正文上的叠加 → 结束卡片 → 拼接 → 然后在整个组装剪辑上混入音乐。

首先使用MCP工具。`add_captions`处理字幕计时和服务器端烧入；`render_html_animation`处理授权的HTML动画；`edit_video_compose`处理透明下三分之二叠加。

### 默认路径

| 请求层 | 默认操作 |
|---|---|
| 无下三分之二，无字幕 | `body_with_overlays_url = base_url` |
| 仅字幕 | 调用`add_captions(video_url: base_url, caption_mode:"auto", style:"classic", position:"bottom", font:"inter")`；将返回的`url`保存为`body_with_overlays_url` |
| 仅下三分之二 | 通过`render_html_animation`渲染下三分之二`.mov`，然后调用`edit_video_compose`；将返回的`url`保存为`body_with_overlays_url` |
| 下三分之二+字幕 | 首先渲染并组合下三分之二，然后调用`add_captions`在组合后的检查点URL上 |

如果`state.lower_third`为false或未设置，跳过[8a]和[8b]。这保持了默认路径完全MCP原生。

不要调用本地Whisper/字幕脚本或链接的`edit_text_overlay`用于字幕。如果原始脚本拼写很重要，只有在您已经从可信来源获得精确的计时段时才传递手动`subtitles[]`；否则优先选择`add_captions`自动瀑布。

### [8a] 渲染下三分之二（仅当`state.lower_third = true`）

除非`state.lower_third = true`，否则跳过此子步骤。通过`render_html_animation`使用`format: "mov"`（ProRes 4444 with yuva420p——保留alpha）。**不要使用`format: "webm"`**——HyperFrames目前以VP9 `pix_fmt=yuv420p`的形式发出webm，没有alpha通道，所以"透明"区域会变成纯黑像素，组合后的LT会在药丸外显示黑色框。`.mov` ProRes路径是目前唯一的alpha路径。

- 原生尺寸：800×220（匹配在1280×720帧上的放置大小，所以没有缩放伪影）
- 药丸：`state.brand.colors.primary`背景（默认`#0d0d0d`），`state.brand.colors.highlight`边框（默认`#fefbcf`），`state.brand.colors.accent`阴影（默认`#cfc3ff`），18px边框半径
- 两行文本：`founder_name`（Space Grotesk 800，80px，白色）+ `founder_role`（Space Grotesk 500，28px，黄油色）
- 无logo在药丸内——品牌标志存在于结束卡片中；下三分之二是关于人的
- CSS `@keyframes`仅：从`translateX(-900px)`滑入0–0.6s，3秒左右轻微框阴影脉冲，4–5秒滑出。不要使用GSAP用于下三分之二动画；结束卡片适用相同的每帧搜索问题。
- 保存URL为`lower_third_url`（文件扩展名`.mov`）

如果您需要验证`.mov`，检查视频流像素格式并确认它包含alpha（`yuva...`）。如果是`yuv...`，alpha被丢弃——切换渲染格式或重新渲染。

### [8b] 下三分之二叠加

仅当下三分之二启用时使用。默认使用MCP组合路径：

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

将返回的`url`保存为`body_with_lower_third_url`。

本地备用合同，仅当MCP组合不可用时：
- 仅为此本地组合步骤下载`base_url`和`lower_third_url`。
- 在`x=50`，`y=video_height - 220 - 100`处叠加800×220的下三分之二，启用`t=0..5s`。
- 保留原始正文音频而不重新编码，以便口型同步保持精确。
- 使用视觉无损H.264设置进行本地检查点。
- 使用`upload_asset`上传检查点并保存返回的`public_url`作为`body_with_lower_third_url`。

如果请求字幕，调用`add_captions(video_url: body_with_lower_third_url, ...)`并保存其返回的`url`作为`body_with_overlays_url`。如果不请求，`body_with_overlays_url = body_with_lower_third_url`。

### [8c] 通过MCP的字幕

默认调用：

```
add_captions(
  video_url: <base_url or body_with_lower_third_url>,
  caption_mode: "auto",
  style: "classic",
  position: "bottom",
  font: "inter",
  font_color: "#ffffff",
  highlight_color: state.brand.colors.accent or "#cfc3ff",
  outline_color: state.brand.colors.primary or "#111111",
  font_size: 42
)
```

将返回的`url`保存为`body_with_overlays_url`。返回的`transcript`对QA很有用，但视频URL是管道工件。

## [9] 动画结束卡片（5秒）——直接HTML作者，通过HyperFrames渲染

我们这里不使用`generate_slide_animation`。该工具将HTML作者工作委托给滑块卡片LLM，这例行添加角落杂乱（左上角标志，右下角URL），选择错误的纵横比，并生成无法可靠地在HyperFrames的每帧搜索中播放的动画。相反，协调者直接编写结束卡片的HTML，并通过`render_html_animation`渲染它。使用与下三分之二相同的引擎。

### 硬规则——经验验证，不要偏离

这些不是风格偏好。每个都是通过渲染、提取帧、与预期比较和观察特定失败发现的。任何这些的逆转都会重现一个已知错误。

1. **纵横比与正文视频匹配。** 读取`aspect_ratio`（默认`16:9`）。计算`data-width` × `data-height`用于`#stage`：`16:9 → 1920×1080`，`9:16 → 1080×1920`，`1:1 → 1080×1080`。硬编码错误方向会产生侧边拼接，正文和结束卡片并排播放而不是按顺序播放。

2. **无角落杂乱。** 无左上角标志。无右下角URL。无标题旁边的图标椭圆。结束卡片是一个居中的消息+CTA。品牌标志由字体和调色板暗示；明确的标志与标题竞争，并读作杂乱。（如果用户明确要求标志，将其集成到居中的堆栈中——永远不会在角落里。）

3. **使用CSS `@keyframes`进行入口动画，而不是GSAP `tl.from()`。** HyperFrames Chrome通过BeginFrame逐帧搜索；GSAP的`tl.from()`在第一次播放时懒加载其初始状态，并且在仅搜索播放下永远不会触发——每帧渲染静态最终状态，没有入口动画。CSS `@keyframes`与Chrome的合成器时钟绑定，并按帧确定性动画。通过`#stage` / `#card` `data-duration`属性声明持续时间；不要添加GSAP脚本只是为了建立时间。GSAP的重复帧捕获显示在t=0和t=2s时相同的帧；切换到CSS `@keyframes`修复了它。

4. **所有入口动画必须在`t = duration - 0.5s`完成。** 半秒保持，以便最终状态在剪辑前可读。使用`duration: 5s`，那就是`animation-delay + animation-duration <= 4.5s`。

5. **使用绝对定位而不是flex进行动画元素。** Flex布局在HyperFrames Chrome中在帧0时没有完全稳定，这加剧了上述GSAP-from()错误——元素在动画中途弹出，因为flex完成了它的第二次遍历。纯绝对定位从帧0提供稳定、确定性的布局。

6. **给每个`@font-face`一个唯一的`font-family`名称；不要依赖权重匹配。** 声明两个`@font-face { font-family: "telka"; ... font-weight: 700/500; }`块应该允许CSS `font-weight: 500`选择500面——但在HyperFrames Chrome中，对于某些权重匹配不可靠。使用不同的系列：`"telka-ext-900"`，`"telka-700"`，`"telka-500"`。当权重匹配失败时，标语可能会渲染在衬线备用字体中；将标语切换到明确加载的系列可以避免这种情况。

7. **`telkaextended-900-normal.woff2`和`telka-700-normal.woff2`在HyperFrames Chrome中是已知的可工作。`telka-500-normal.woff2`是已知的损坏——它通过fontTools成功解析（正确的OS/2.usWeightClass=500，有效的cmap，正确的系列名称），但Chrome无声拒绝`@font-face`声明并回退到系统衬线。** 解决方案：使用`telka-700`作为标语（同一系列，稍重——视觉上仍然符合品牌）。如果未来的结束卡片需要中等权重，在发货前通过渲染+提取帧30来测试候选woff2。不要相信"Telka 400"或"Telka 300"只是因为Telka 700有效就会工作。

8. **直接作为base64内联品牌字体。** Pika CDN不接受字体上传（mime允许列表），并且不发送CORS标头，所以`@font-face` URL引用在HyperFrames Chrome中失败，字体无声回退到系统衬线。使用`pyftsubset`将每个woff2子集为标题+标语+CTA中的字形，base64编码，嵌入为`data:font/woff2;base64,...`。子集文件通常为5–10 KB每个。

9. **不要为品牌设计编写CSS `font-family`备用链。** 如果品牌字体加载失败，备用链隐藏了失败——你发货时认为它是Telka，实际上是Helvetica。使用`font-family: "telka-700"`单独（无备用）。然后字体加载失败会渲染Chrome的默认衬线，这在视觉上很明显并触发修复。

10. **组合合同** — HyperFrames合同：`<div id="stage" data-composition-id="main" data-start="0" data-duration="5" data-width="W" data-height="H">` 包裹一个单一的直接子元素`<div id="card" class="clip" data-start="0" data-duration="5" data-track-index="0">`，该子元素包含所有其他内容。可见的定时元素必须包含`class="clip"`，因为HyperFrames使用它来控制可见性，并且clip必须嵌套在组合根元素内，而不是作为兄弟元素。`#stage`的多轨道直接子元素与帧查找交互不佳。（通过镜像工作的lower-third结构来解决。）

11. **运行时就绪钩子** — 在`</body>`之前包含一个小型兼容性钩子：
    `window.__hf = { duration: 5, seek: (t) => { document.documentElement.style.setProperty("--hf-time", String(t)); } };`。
    CSS `@keyframes`仍然驱动视觉动画，但钩子使prod帧捕获路径在探测`window.__hf`时准备就绪。如果工作器报告`window.__hf在45000毫秒后未就绪`，则将HTML视为`render_html_animation`无效；修复组合合同或钩子并重新渲染。不要回退到静态PNG。

12. **渲染后始终在t=0、t=1s、t=2s提取帧并进行视觉比较。** 如果帧0和2看起来相同，则入口动画未运行。如果标语看起来像衬线字体，则品牌字体未加载。不要仅依赖URL。不要在没有此检查的情况下发货。（用户在添加帧提取之前连续三次渲染时捕获了这些失败。）

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
#    @font-face数据URL（当display_b64/body_b64存在时）、标题行、
#    标语、CTA、调色板值和尺寸W/H。

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
│                  ────                       │ ← 短强调分隔符（scaleX内）
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
|-------|------|------|
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

如果品牌套件缺乏字体（`state.brand.fonts`为null）— 回退到系统`-apple-system, sans-serif`用于标语/CTA，但将标题降级为系统显示字重。不要使用回退字体渲染品牌字体结束卡片；它们总是看起来不正确。在交付步骤中标记，以便用户知道品牌套件不完整。

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
  query: "返回包含此视频duration_seconds的JSON对象。"
)
```

将结果保存为`final_duration_seconds`。它必须在`>= 55`和`<= 75`之前报告`final_url`作为完成的交付物。
如果`final_duration_seconds`低于55秒，将运行视为失败的局部组装：不要交付URL作为最终版本，不要标记技能完成，并返回到缺少动作的恢复流程。如果所有4个动作都存在但探测仍然低于55秒，停止并暴露连接/提供者截断以供调查，而不是用无关素材填充。

## [11] 最终URL

将`final_url`保存到`state`。如果本地回退组装生成了最终MP4，通过`upload_asset`上传该检查点，并用返回的`public_url`替换`final_url`。

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
检查`brief.product_name` / `product_name`在任何出现的地方拼写正确，任何手机屏幕/产品屏幕显示预期的产品而不是想象的替代品，必需的产品资产在预期的动作中可见，并且最终视频没有黑帧或部分动作截断。
```

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
- 动作级的`.mp4`本身很有价值（例如，用户可能想为特定频道剪辑单个动作）
- 用户通常要求将生成的引用保存在视频旁边，以便他们可以重用这些资产。默认情况下编码。

## [13] 交付

向用户报告`final_url`。包括：
- 资产包URL/路径仅当用户要求时
- 从`final_duration_seconds`的总时长（~65秒=60秒主体+5秒结束卡片）
- 对重新运行有用的中间URL或本地文件：`base_url`、可选的`body_with_overlays_url`、`music_url`、`end_card_url`、`final_url`以及每个`act_urls[i]`
- 简要（`brief.product_name` / `brief.tagline`），以便用户确认模型是否选择了正确的产品
- 资产进入哪个动作的1行摘要，以便用户确认位置

## 验证门

| 步骤 | 检查 |
|------|------|
| 简要 | `product_name`非空 |
| 资产分析 | 每个资产一个JSON对象，每个对象具有非空的`content_description`和`best_for_act` |
| 脚本 | 4个动作；总对话100–180字；每个资产至少由一个动作引用，或明确注明为未使用 |
| 引用 | `character_url`和`location_url`是https URL |
| 动作 | 返回所有4个act_urls（每个具有唯一种子）；对于包含非空`asset_index`的镜头，使用`analyze_media`检查一个镜头以确认资产实际上可见，并且揭示模式对于`product_type`正确（例如，对于`physical_apparel`，验证创始人正在持有/穿着带有正确印刷的实际T恤 — 不是在手机屏幕上显示） |
| 拼接 | 返回`base_url` |
| 音乐 | 返回URL；`duration_seconds >= 55`来自`kling-audio`背景床路径；如果低于55，重试一次，然后停止并暴露 |
| 覆盖层 | 返回`body_with_overlays_url`（如果步骤[8]跳过则为`body_with_overlays_url = base_url`） |
| 结束卡片 | 返回作为MP4的`end_card_url`；使用`extract_frame`/`analyze_media`检查早期帧：帧0应显示空背景（入口之前），稍后的第一秒帧应显示部分入口 — 确认CSS @keyframes正在运行，而不是静态的 |
| 最终组装 | `edit_concat`返回的`assembled_url`；音乐存在时`edit_audio_mix`返回的`final_url`，否则`final_url = assembled_url` |
| 最终时长 | 在交付前`analyze_media`报告`final_duration_seconds >= 55`和`<= 75` |
| 本地回退上传 | 仅当使用本地回退组装时：将`final_url`替换为上传的`public_url` |

## 失败模式

除“时长下限和部分动作恢复”中记录的缺失动作重试外，在第一次验证失败时停止并暴露。不要自动重试昂贵的调用（SeeDance动作每次运行3–8分钟 — 重复失败会消耗积分）。

### 从上游5xx在analyze_brief / generate_image / generate_reference_video / generate_music / upload_asset中恢复

如果任何付费生成、简要分析、音乐、渲染、编辑或资产MCP调用返回：
- `code: "provider_5xx"` AND `retry_class: "retry_after_backoff"`
- 或来自任何上游提供者（Seedance、Kling、OpenAI、Gemini、存储）的HTTP 502 / 503 / 504

这样做：
1. 等待5秒。
2. 重新调用完全相同的MCP工具，使用完全相同的参数。不要重写简要、产品名称、创始人照片、动作提示、种子、参考图像顺序、音乐提示或上传负载。
3. 如果重试也因5xx失败，中止并向用户显示：“提供者两次返回了瞬态上游错误。1-2分钟后重试；这通常会自行解决。”

不要重试超过一次。此路径用于瞬态提供者中断；在5xx后更改创意输入会创建不同的工件并可能重复支出。

### 从上游4xx / moderation_blocked中恢复

如果`generate_image`在创建创始人/位置/产品参考时返回上游4xx或`moderation_blocked`：
1. 不要重试相同的提示；审核和大多数4xx验证失败是确定性的。
2. 如果资产不是用户关键，当替代品仍然符合简要时，尝试一次回退提供者。对于创始人身份照片，没有回退提供者应改变用户的身份；请求更安全的用户提供的参考。
3. 如果回退提供者也失败或会改变产品/创始人身份，向用户显示：“图像提供者拒绝了此参考提示。提供不同的参考图像或选择不太容易识别/风格化的方向。”

对于Seedance动作审核，仅在其适用的情况下遵循时长下限/缺失动作恢复。不要运行重复的盲动作重试。

### 从上游429（速率限制）中恢复

如果任何上游返回带有回退提示的HTTP 429：
1. 等待提示的回退，或如果没有提示则等待30秒。
2. 重新调用完全相同的MCP工具，使用完全相同的参数。
3. 不要重试超过一次。如果它仍然返回429，中止并暴露速率限制消息。

### `capture_website`返回空 / 页面未加载

此技能通常使用`analyze_brief`提取产品事实，但URL简要辅助程序可能调用`capture_website`。如果`capture_website`返回200但`action_bboxes`为空或`recording_viewport`为0x0：
1. 不要重试；页面在捕获环境中未成功渲染。
2. 暴露：“无法捕获<url>。页面可能被阻止/付费墙/需要认证。请提供产品简要、截图或托管资产。”。

### `upload_asset`网络/认证失败

如果`upload_asset`在将创始人照片、产品资产、品牌标志、lower-thirds或回退本地组装转换为托管URL时失败，不要继续使用本地文件系统路径在`reference_images`或HTML中。仅对上述5xx或429类重试一次。对于`auth_error`、不支持的MIME、网络故障或重复上传失败，停止并请求托管URL或支持的光栅导出。

### 长时间运行的`task_status`超过上限

每个异步MCP调用要么返回内联结果，要么返回`{task_id, status}`用于轮询。在使用以下上限之前决定任务是否卡住：
- Seedance i2v：每调用10分钟
- Kling音频：每调用5分钟
- gpt-image-2高质量：每调用3分钟
- 渲染/编辑/上传辅助程序：每调用5分钟

使用较早者：提供者的上限x1.5或任何技能特定的硬轮询上限，包括上述Long-running task_status轮询合同中的15分钟总上限。如果`task_status`返回`status: "processing"`或`status: "queued"`超过该较早限制，调用`task_cancel({task_id})`并暴露：“提供者运行时间异常；中止。重试。”

| 症状 | 原因 | 解决方法 |
|---|---|---|
| `generate_reference_video` 返回 402 "余额不足" 错误，且 UUID 熟悉 | Idempotency 缓存重放了一个旧的失败结果，参数相同 | 每次调用时传递一个唯一的 `seed`（101 / 202 / 303 / 404 用于 4 个场景），使哈希值不同。 |
| SeeDance 在创始人参考上返回 422 "可能包含真实人物肖像" 错误 | 内容策略过滤器触发（间歇性——同一张照片可能在下次尝试中通过） | 重新生成创始人肖像，使用更强的风格化（"皮克斯/迪士尼 3D 动画美学"）。不要自动重试相同的参考——会消耗积分。 |
| 创始人衬衫在场景之间变化 | 每个场景都重新读取 @Image1，没有服装锁定 | 在每个场景提示中添加 `WARDROBE LOCK:` 行，内容完全相同。 |
| 所有 4 个场景都有相同的物理背景 | 开头行说 "在匹配 @Image2 的位置内部" —— 字面理解 | 以 "在视觉风格、调色板、灯光和材料匹配 @Image2 的场景中" 开头 + 添加每个镜头的 `Background context:` 行。 |
| 创始人看起来像被冻结了 / 没有肢体语言 | 节奏是仅面部；场景是单镜头 | 每个场景添加 3 个时间编码的子镜头，带有明确的 `Transition:` 行；每个节奏都需要手/躯干/头部动作（见 [3c.1]）。 |
| 最终视频长度小于 55 秒 | 一个 SeeDance 场景超时，或最终连接修剪了身体，导致部分运行 | 不要将其作为最终版本交付。使用新种子重试缺失的场景，同时保留成功的场景；如果无法完成，停止并显示上游 SeeDance 超时。 |
| 音乐提示被拒绝，代码为 `1201` | `kling-audio` 提示超过 200 个字符的提供者限制 | 将提示缩短为标准 <= 200 个字符的快照风格。保留 `soft instrumental background bed`、`no vocals` 和 `leave room for narration`；不要更改提供者、持续时间或背景模式。 |
| 音乐返回 < 55 秒 | `kling-audio` 工作程序扩展没有满足 60 秒的请求 | 确认调用使用了 `provider: "kling-audio"`、`mode: "text_to_audio"`、`background: true` 和 `duration_seconds: 60`。重试一次；如果仍然短，停止并显示工具结果。 |
| 音乐压倒了对话 | 提示要求前景旋律而不是床铺 | 重新生成一次，使用 "soft instrumental background bed, no vocals, leave room for narration"，并在步骤 [10] 中将 `audio_volume` 保持为 0.16 或更低。 |
| 字幕拼写错误产品名称 | 自动转录规范化了语音音频 | 如果您已经有了可信的时间戳片段，请仅使用手动 `subtitles[]`；否则，不要默认运行本地 Whisper，而是显示转录限制。 |
| 下三分之一覆盖在药丸外部显示黑色框 | webm 格式编码时没有 alpha (yuv420p) | 使用 `format: "mov"`（ProRes 4444 yuva）重新渲染。使用 `ffprobe \| grep pix_fmt` 验证显示 `yuva*`。 |
| 最终视频音频比视频短 | 本地回退连接使用了 `-c copy`，音频参数不匹配 | 优先使用 MCP `edit_concat`。如果本地连接不可避免，请在连接前将所有输入标准化为 aac/44100/stereo/192k。 |
| 结束卡片在 t=0 和 t=2s 渲染相同（没有入场动画） | 使用了 GSAP `tl.from()` 而不是 CSS `@keyframes` | 将入场转换为 CSS `@keyframes`；仅保留 GSAP 桥接用于持续时间寻址。 |
| 结束卡片标语渲染为衬线后备 | woff2 字体在 HyperFrames Chrome 中加载失败 | 每个字体使用唯一的 `font-family` 名称（不是重量匹配）；将 woff2 子集并 base64 内联；在发货前提取第 30 帧进行验证。 |
| `render_html_animation` 失败，`window.__hf` 在 45000ms 后未准备好 | 结束卡片 HTML 没有暴露运行时就绪钩子或有效的嵌套 `class="clip"` 组合 | 添加/修复 `window.__hf` 钩子和 `class="clip"` 子元素，然后重新渲染 MP4。不要回退到静态 PNG，并且不要在 `end_card_url` 是视频 URL 之前继续。 |

## 承重短语

这些字符串直接放入 SeeDance 提示（或 HTML 渲染）中。每个都经过经验验证——释义会无声地破坏配方。编辑提示时，搜索这些锚点并保持其完整性。

| 短语 | 放入 | 为什么承重 |
|---|---|---|
| `The character (matching @Image1) in a setting whose visual style, palette, lighting and materials match @Image2.` | 每个场景提示的开头行 | "在视觉风格匹配的场景中" 允许 SeeDance 每个镜头变化背景；"在匹配位置内部" 在所有 4 个场景中重现字面背景。 |
| `WARDROBE LOCK: …`（后面跟着所有 4 个提示中相同的服装句子） | 每个 `CHARACTER VOICE:` 行下的标题行 | 锁定跨单独 15 秒生成的服装。@Image1 单独可以在场景之间漂移。 |
| `Background context: …`（每个子镜头一个，每个位置不同） | 每个镜头块内 | 强制 SeeDance 每个镜头渲染不同的物理位置——不同的墙、不同的角度、不同的背景特征。没有它，所有 3 个子镜头都会出现在同一个角落。 |
| `<<<voice_1>>>…<<<voice_1>>>` | 每个镜头的对话有效负载 | SeeDance 原生口型同步标记。标记是引擎知道要口型同步什么的方式；没有它们就没有口型同步。 |
| `Transition: …` / `Hard cut:` | 相同提示中子镜头之间 | `Transition:` 描述连续的摄像机运动（滑翔 / 推拉 / 轨道）；`Hard cut:` 触发真正的剪辑。没有它们，SeeDance 默认为同一位置的重新帧，看起来像跳变变焦。 |
| `Native lip-synced dialogue audio, no music overlay.` | 每个场景提示的结尾行 | 防止 SeeDance 在对话下方层叠自己的环境音乐，这会与步骤 [10] 中的专用音乐床冲突。 |
| `provider: "kling-audio"`, `mode: "text_to_audio"`, `background: true`, `duration_seconds: 60` | 步骤 [7] `generate_music` 调用 | 使用唯一的后台支持音乐提供者，触发 MCP 工作人员的 10 秒 Kling 种子 + 本地 ffmpeg 扩展路径。 |

## 不要做的事情

- **不要以 "在匹配 @Image2 的位置内部" 开头 SeeDance 提示**——在所有场景中重现字面背景。使用 "在视觉风格...匹配 @Image2"。 |
- **不要在提示中用散文描述角色**——@Image1 承载身份。散文冲突会产生幽灵角色或错误的服装。例外：`WARDROBE LOCK:` 行。 |
- **不要使用电影行业镜头术语**——"双人镜头" / "三人镜头" / "过肩镜头" / "OTS" / "全景镜头" 触发 SeeDance 幽灵主体伪影。用平实的语言描述摄像机看到的内容。 |
- **不要将下三分之一渲染为 webm**——alpha 不会被保留（HyperFrames 发射 yuv420p）。使用 `format: "mov"`（ProRes 4444 yuva）。使用 `ffprobe \| grep pix_fmt` 验证。 |
- **不要用 `generate_slide_animation` 为结束卡片**——该工具的幻灯片卡片 LLM 添加角落杂乱，生成的动画无法确定性地寻址。直接编写内联 HTML 并通过 `render_html_animation` 渲染。 |
- **不要链式 pika MCP `edit_text_overlay` / overlay 调用用于任意文本/字幕组合**——这会级联质量损失并可能引入口型同步漂移。使用 `add_captions` 用于字幕，并使用单个组合/本地传递用于有界的下三分之一。例外：步骤 [5.5] 确定性的数字 UI 覆盖故意使用一个有界 `edit_video_compose` 传递加上可选的精确品牌 `edit_text_overlay`，然后进行 OCR QA，以防止 Seedance 渲染的品牌/UI 文本。 |
- **除非 MCP 不可用，否则不要使用本地 `ffmpeg concat -c copy` 进行最终组装**——旧的音频掉落问题在本地连接行为中。默认使用 MCP `edit_concat` + `edit_audio_mix`。 |
- **不要跨场景使用相同的参数启动 SeeDance**——MCP idempotency 缓存哈希到相同的任务 ID 并重放旧结果（有时是失败结果）。每个场景传递唯一的 `seed`。 |
- **不要使用 MiniMax 作为默认生成的床**——它不支持 `background: true`，并且会在旁白下方前景化旋律。 |
- **不要在技能中手动平铺 10 秒 Kling 剪片**——MCP 工作人员拥有本地 ffmpeg 扩展路径，用于 `duration_seconds: 60`。 |
- **不要为每个品牌复制示例音乐声音**——配方是 Kling 背景床调用，而不是特定的乐器。选择与 `brief.tone` 匹配的音域（见步骤 [7] 表）。 |

## 引擎选择：仅 seedance（带注意事项）

SeeDance (`fal-seedance-2-i2v` 通过 `generate_reference_video` `provider: "seedance"`) 是唯一的视频引擎。测试后选择：

- **vs Kling v3-omni**：Kling 有真正的 `shots[]` 硬切数组（更干净的多人镜头），但拒绝 `seed` 参数（缓存破坏更难），并且 4 × pro 1080p 输出总和 >50MB 超出 `edit_concat` 上传限制（强制本地连接）。Kling 对真实人物照片的内容策略更宽松——如果 SeeDance 的间歇性 422 成为硬障碍，值得将其作为备用考虑。
- **vs Happy Horse `happyhorse-1.0-r2v`**（阿里巴巴 DashScope）：生成干净的 1080p，具有原生口型同步，但多镜头提示方向较弱，明显不如 SeeDance 现代化。 |
- **SeeDance 赢得是因为**：原生 `<<<voice_1>>>` 口型同步，接受 `seed`（缓存破坏），对真实人物照片足够宽容，95%+ 运行通过内容过滤器，单个 15 秒提示带时间编码的子镜头提供了足够的变异性，适用于对话头。 |

如果 SeeDance 出现故障或其内容过滤器开始反复拒绝创始人参考，文档中记录的回退是使用更强的风格化重新生成创始人肖像（皮克斯/迪士尼 3D 美学）。在管道中途切换引擎会改变提示、连接和资产大小流中的太多假设。 |

## 运行时预期

每个步骤的墙上时间。总运行时间约为 12–18 分钟，主要由并行 SeeDance 批处理主导。

| 步骤 | 墙上时间 | 备注 |
|---|---|---|
| [1] analyze_brief | 20–60 秒 | |
| [2] analyze_media × N | 每个资产 15–30 秒，并行 | |
| [4] founder/custom 位置参考 | 每个 10–60 秒 | 上传本地创始人照片，使用提供的 URL，或生成创始人肖像；默认位置等待 [4.5] |
| [4.5] 品牌套件摄入 + 默认位置 | 10–30 秒 | 解析品牌套件，上传标志资产，如果需要，渲染匹配宽度的品牌强调背景 |
| [5] SeeDance × 4 并行 | 5–9 分钟墙（最慢的场景） | 每个场景 3–8 分钟，可能异步完成 |
| [5.5] 数字 UI 覆盖 | 30–120 秒（数字产品） | 渲染真实 UI / 字标覆盖剪辑，将它们合成到揭示场景中，然后在进行 OCR QA 之前连接 |
| [6] edit_concat（场景 → 60 秒身体） | 30–60 秒 | |
| [7] generate_music | 30–90 秒，如果 <55 秒则重试一次 | Kling 生成一个 10 秒种子，然后工作员本地扩展到 ~60 秒 |
| [8a] render LT 作为 .mov | 60–120 秒 | ProRes 4444 慢于 webm，但仅有的带 alpha 的路径 |
| [8] add_captions | 30–90 秒 | 字幕仅，或在下三分之一检查点后 |
| [8b] 本地下三分之一覆盖回退 | 20–60 秒 | 仅当下三分之一启用时 |
| [9] render end card | 60–120 秒 | |
| [10] edit_concat + edit_audio_mix | 30–90 秒 | 服务器端标准化连接和音乐混合 |
| **总计** | **12–18 分钟** | |

## 默认值

- 4 × 15 秒 SeeDance 场景，并行，唯一种子（101、202、303、404）
- **角色身份来自 `@Image1` 参考**——避免在提示中描述角色（不要 "Founder Avery"，不要 "年轻的创意街头风创始人"）。每个提示都以 **"The character (matching @Image1) in a setting whose visual style, palette, lighting and materials match @Image2."** 开头。使用 "inside the location matching @Image2" 会使 SeeDance 在所有场景中重现字面背景。唯一的例外是每个场景提示中的 `WARDROBE LOCK:` 行，以保持跨 4 个单独 15 秒生成的服装一致性。 |
- **避免电影行业镜头术语**，SeeDance 会字面理解——永远不要写 "双人镜头"、"三人镜头" 或 "全景镜头"。镜头 F 是 "品牌上下文镜头"。 |
- **每个脚本都有一个 `character_voice_profile`**（3-4 行描述默认交付——节奏、标志性手势、暂停行为）。在每个场景的 SeeDance 提示中重复字面 `CHARACTER VOICE: …`。 |
- **每个镜头都有 `beats[]`**，而不是场景级 `acting`。每个节奏都有 `text` + `emotion` + `physical`。沉默 `(beat)` 条目指示在说出句子之间发生什么（保持凝视、微表情、手势过渡）。节奏作为每个镜头的 "Acting beats" 块在 SeeDance 提示中发出。 |
- **每个场景中第一个镜头之外的镜头都有 `transition_from_prev`**——一个连续摄像机移动描述，将我们从之前的构图带到这个构图（推拉、弧形、推过、拉回、轨道）。没有它，多镜头场景会读取为跳变变焦，因为 SeeDance 会重新帧同一虚拟摄像机位置，而不是在空间中移动。 |
- **在将对话文本连接到 `<<<voice_1>>>` 有效负载之前应用 TTS 发音重写**（Ari → Airy，API → A P I，example.com → example dot com，等等）。见步骤 [3] 中的 "TTS 发音重写"。 |
- 16:9，1080p（SeeDance `resolution: "1080p"`） |
- 用户提供的资产根据产品类型适当揭示：
  - `digital` → 在镜头 C 和 E 中的手机空白占位符，然后在步骤 [5.5] 中合成真实 UI / 字标 |
  - `physical_apparel` → 创始人穿着/持有实际 T 恤；将资产作为参考传递到每个出现衬衫的镜头（而不仅仅是一个揭示节奏） |
  - `physical_object` → 创始人拿起产品；将资产传递到所有产品可见的镜头 |
  - `consumable` → 创始人使用/吃/喝；相同的模式 |
  - `service` → 没有资产揭示；仅环境和对话 |
  - 音乐：目标 ~60 秒乐器——调用 `generate_music`，使用 `provider: "kling-audio"`、`mode: "text_to_audio"`、`background: true` 和 `duration_seconds: 60`。将 `prompt` 保持在 <= 200 字符，并包括 "soft instrumental background bed"、"no vocals" 和 "leave room for narration"。如果少于 55 秒，则重试一次，然后停止并显示，而不是接受短的床。 |
  - 5 秒结束卡片通过 `render_html_animation`——根据步骤 [9] 编写内联 HTML，将品牌字体作为 base64 内联。从 `state.brand`（在步骤 [4.5] 中设置）获取品牌 → 真实标志、真实调色板、真实字体。 |
  - **字幕通过 `add_captions`**。默认使用服务器端逐词字幕烧入。字体选择是工具支持的集合（`inter`、`bebas-neue`、`noto-cjk`）；使用品牌强调颜色而不是本地自定义字体 drawtext。 |
  - **下三分之一回退**。默认关闭。如果 `state.lower_third = true`，通过 `render_html_animation(format:"mov")` 渲染 5 秒品牌药丸左下角；最终覆盖使用 `edit_video_compose`，或者如果 MCP 组合不可用，则仅进行本地 ffmpeg 传递。 |
  - **最终组装通过 MCP**。使用 `edit_concat` 用于身体 + 结束卡片，然后使用 `edit_audio_mix` 用于音乐。本地连接/混合是回退，不是规范路径。 |
  - 提供者：`seedance` 仅。参考标记是 `@Image1` / `@Image2` / `@Image3`。原生口型同步通过每个子镜头的 `<<<voice_1>>>...<<<voice_1>>>` 标记。真实人物创始人照片在大多数情况下通过内容过滤器；间歇性 422 → 使用更强的风格化重新生成。
