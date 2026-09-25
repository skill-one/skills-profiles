# App Sizzle — GPT-Image-2 增强型 iOS 应用预告片

从真实应用屏幕生成精炼的 15 秒应用预告片。每个选定的屏幕都会在 Seedance 之前通过 GPT-image-2，因此压缩的捕获将变得更干净，而不会发明 UI。

## 成本透明门

在任何付费 MCP 调用之前，调用一次 `identity_balance({verbose: true})`。显示当前余额、最近烧毁率和剩余运行空间，然后使用以下确切消息来控制运行：

> 预计成本：典型的运行（包括屏幕增强和 Seedance 视频）约 3,000-4,000 个信用（约 30-40 美元）。这超过了 5,000，因此回复 `proceed` 继续或 `cancel` 停止。

在用户回复 `proceed` 之前，不要调用任何付费 MCP 工具。如果用户回复 `cancel`，则停止而不会生成。对于非交互式 `--quick` 或 `--config` 调用者，要求在配置中包含 `cost_ack=proceed`；如果缺失，则用估计值而不是花费信用来停止。

**生成合同：** 使用 `resolution="1080p"`，`duration=15` 和 `sound=True`。跳过 `fast=true`，因为它将 Seedance 限制在 720p。技能拥有持续时间，因此用户只需提供应用标识、屏幕、标志和宽高比。

视觉美学是**从应用的个性中派生出来的**——不是默认为流态玻璃。代理从其图标、屏幕和类别中读取应用的灵魂，然后选择一种处理方式。用户提供应用标识和资产；代理决定所有其他内容（模式、提示、相机、风格）。

---

## 生成前时钟保护

在技能启动时，一旦可用所需的应用标识和屏幕/标志源通过成本门，开始计时器。等待用户 `proceed` 回复或非交互式 `cost_ack=proceed` 的时间不计入准备时间，并且不得触发此保护。如果需要输入或真实资产缺失，则在 Stage 0 或 Stage 0.5 停止并询问它们；不要绕过资产门。对于具有所需输入的运行，第一个付费生成调用是 GPT-image-2 的 `generate_image_edit` 增强传递，必须在技能启动后的 5 分钟内调用。如果你在技能启动后的 5 分钟内没有调用第一个 `generate_image_edit` 增强传递，则在任何付费生成调用之前停止，并报告 `failed_pre_generation_timeout` 以及你目前拥有的内容：获取的资产、选定的屏幕、功能图、弧线、增强提示状态、Seedance 提示草稿（如果有）以及确切的阻止器。不要继续改进分析、增强措辞、提示措辞或相机语言。

在付费生成调用之前，在准备阶段的每个阶段之后立即打印单行进度检查点：
- `Stage 1/3 done — assets sourced and screened, analyzing screenshots.`
- `Stage 2/3 done — feature map and arc written, locking enhancement prompts.`
- `Stage 3/3 done — enhancement prompts locked, calling GPT-image-2 now.`

功能图和增强提示的编写在第一次 `generate_image_edit` 调用之前的最多 2 次内完成。在最多 2 次之后，将你拥有的内容发送到 `generate_image_edit`；不要继续改进增强措辞、屏幕分析或弧线语言。Seedance 提示的编写在增强完成后最多 2 次内完成；然后，将你拥有的内容发送到 `generate_reference_video`。

## 长任务 `task_status` 投票

当任何长时间运行的生成或编辑调用返回带有或没有初始状态的 `task_id`，包括 `{task_id}`，`{task_id, status: "queued"}` 或初始 `queued`，`running` 或 `processing` 状态时，立即记录任务 ID 和开始时间。

- 在终端 (`completed | failed | cancelled`) 之前，以紧密循环调用 `task_status({task_id})`。不要手动睡眠和不要 Bash 投票；工作程序保持每个状态调用打开。
- 每隔 60 秒发出一条可见的进度行，当状态为 `queued`，`running` 或 `processing` 时：`Seedance i2v queued for {N}m {S}s... still processing`。在投票 Kling、GPT-image-2、叠加或编辑任务时，替换提供者/阶段标签。
- 在 `completed` 时，展开返回的结果 URL 并继续。
- 在 `failed` 或 `cancelled` 时，向用户显示失败，包括 `task_id`、状态和最后的状态消息。
- 在原始提交后的 15 分钟内，如果任务仍然非终端，则调用 `task_cancel({task_id})` 并向用户显示失败。如果取消报告任务已经终端，则再次调用状态一次并报告终端结果。
- 在原始任务仍然是 `queued`、`running` 或 `processing` 的情况下，不要提交重复请求。

## 模式：参考到视频

主要：`generate_reference_video(provider="seedance", resolution="1080p")` 使用 3-5 张屏幕 + 应用图标/标志作为最终参考。

当以下情况时，回退到 `provider="kling", quality_mode="pro"`（= 1080p）：
- Seedance 返回非音频 `partner_validation_failed`（名人面孔、屏幕录制 UI）
- Seedance 返回 `insufficient_balance`
- Seedance 保持 `queued`/`running` 直到返回超时，例如 `seedance timed out after ...`

不要将生成的音频审核视为立即 Kling 回退。请参阅 Generate Video 首先的 Seedance 生成的音频审核恢复运行手册。

Kling 提示使用 `<<<image_1>>>` … `<<<image_5>>>` 令牌，而不是 `@Image1` … `@Image5`。丢弃 `resolution` 参数（Kling 使用 `quality_mode` 代替）。参见 Gotchas。

---

## Stage 0 — 资产获取

如果使用空参数且没有相关先前的上下文，则打印此菜单原文并停止。不要调用工具，直到用户提供应用标识和屏幕源。

```
To make your app promo, I need:

1. App name + one-line description of what it does
   (e.g. "Nova — an AI journaling app for iOS")

2. Where should I pull the app screens from?
   — iOS App Store: give me the App Store URL or app name → I'll use
     `fetch_appstore_screens` to fetch screenshots, metadata, and icon
   — Web app / website: give me the URL → I'll capture it with Pika MCP
   — Local files / URLs: drop the paths and I'll upload them

3. Brand logo — path or URL (preferred) or skip to use the App Store icon
   The logo anchors the end card and prevents Seedance from hallucinating brand text.
   If you don't have a logo file, use the fetched App Store icon as the fallback.

4. Aspect ratio: 16:9 (landscape/YouTube) / 9:16 (Reels/TikTok) / 1:1. Optional: `variants=16:9,9:16,1:1` to export multiple deliverables from one render.
```

如果触发消息或先前的上下文已经提供了部分内容，则在触摸任何工具之前，仅询问缺失的必要字段。这是用户需要回答的唯一问题；代理决定模式、提示、相机和风格。

一旦回答，代理：
1. 获取屏幕（MCP App Store 获取 / 网站捕获 / 上传本地文件）
2. **分析每个屏幕**（Stage 1）— 读取每个截图，映射 UI → 功能
3. **设计叙事弧线**（Stage 2）— 在触摸提示模板之前构建 15 秒的故事结构
4. 选择 3-5 张最佳屏幕用于预告片（按叙事角色排序）
5. 上传标志 + 屏幕以获取公共 URL
6. 编写屏幕特定提示（模板 A 或 B）
7. 以 1080p 生成

---

## Stage 0.5 — 资产门

在调用任何生成工具之前，验证两个资产都在手头：

| 资产 | 需要 | 如果缺失 |
|-------|----------|------------|
| 真实应用屏幕（≥1 个实际获取的图像） | 是 | 停止并询问屏幕 |
| 标志或应用图标 | 是 | 使用 `fetch_appstore_screens` 图标（当使用 App Store 源时）；否则停止并询问标志/图标 |

如果其中任何一个缺失，告诉用户确切需要什么，并等待。真实资产是使预告片扎根的东西；文本到视频占位符使 Seedance 发明 UI。

避免：
- 使用文本到视频作为替代，而预期屏幕
- 在提示中描述想象中的 UI（“一个深色控制面板...”）而没有真实的参考图像
- 进行“我现在使用占位符”
- 根据应用名称或描述编造应用的样子

向前唯一可接受的路径是用户提供的真实资产。如果 MCP 获取或捕获失败（App Store 返回为空，网站截图出错），报告发生了什么并要求用户手动提供屏幕。永远不要编造它们。

### 人像类型探测用于人类或角色资产

应用屏幕和应用图标是唯一的默认视觉锚点。App-sizzle 不是一个创始人/创作者面孔技能，因此缺少屏幕或标志永远不会用用户头像填充。

在任何付费 `generate_image_edit` 或 `generate_reference_video` 调用之前，仅在用户提供的屏幕、标志、预告片图像、吉祥物、创始人照片或角色资产包括一个突出的人物或角色，它将成为增强或视频参考时，运行此 Avatar-type 探测。对于包含偶然面孔的普通应用屏幕，请选择另一个屏幕或在上传之前裁剪面孔。

调用一次 `analyze_media` 在该资产上：

```
query: "Classify this image for paid video generation. Is it a photograph of a real human face, an AI-generated realistic portrait, a stylized / illustrated character, or a recognizable trademarked / copyrighted character such as Batman, Pikachu, or Mickey Mouse? Return strict JSON only: { \"avatar_type\": \"real_human\" | \"ai_realistic\" | \"stylized_illustrated\" | \"recognized_ip\", \"recognized_character\": string | null, \"moderation_risk\": \"low\" | \"medium\" | \"high\", \"recommendation\": \"proceed\" | \"warn\" | \"reject\" }. Use null for `recognized_character` when no specific character is recognized; never write \"none\", \"unknown\", or explanatory prose in that field."
```

根据结果进行路由：
- **recognized IP / 版权风险** -> **仅当** `avatar_type` 是 `"recognized_ip"`，或者 `recognized_character` 指名特定角色（例如 `"Batman"`），或者当 `moderation_risk` 是 `"high"` 且 `recommendation` 是 `"reject"` 时停止。将 `recognized_character: null`，空字符串，`"none"`, `"unknown"`, `"n/a"` 和低/中 `moderation_risk` 视为本身不足以停止。在运行此检查之前，即使 `avatar_type` 是风格化的/插画的，chibi Batman 仍然是 Batman。
- **真实人类 / AI 生成的逼真** -> 仅当这是合法的应用屏幕或用户提供的预告片资产时才继续；否则请求数据 UI。
- **风格化的/插画的** -> 使用可见警告，因为风格化角色可能会降低 Seedance 的可靠性，但不要用它们替代缺失的屏幕。
- **商标的 / 版权的** -> **在生成之前停止**。显示此消息：`The supplied avatar appears to be a trademarked character ([X]). Most video providers will moderate this and refuse to generate. Pass --avatar <real-looking-photo-url> to override.` 对于 app-sizzle，请要求非 IP 应用屏幕/标志，而不是使用头像覆盖作为屏幕替代。

---

## 屏幕获取

### iOS App Store

使用 Pika MCP `fetch_appstore_screens`；不要使用本地抓取器。它接受完整的 App Store URL、数字应用 ID 或应用名称搜索词：

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

如果 `fetch_appstore_screens` 返回没有屏幕，报告错误并要求用户提供 3-5 张真实屏幕加上标志/图标。不要回退到 Playwright/headless App Store 捕获，不要编造 UI。

在获取 App Store 资产后，选择显示核心 UI 的 3-5 张屏幕。跳过：
- 纯文本/启动屏幕（没有 UI）
- 空白或加载状态
- 包含面孔的屏幕（可能会触发内容政策）

**屏幕选择原则 — 最大化视觉对比度。** 每个选定的屏幕应该尽可能与其他屏幕不同：深色与浅色背景，UI 密集与照片为主，微距特写与宽网格，极简与繁忙。如果你的所有屏幕看起来都相似，Seedance 将它们混合成视觉泥浆。Dazz Cam 成功的原因：3D 相机网格 + Polaroid 输出 + VHS 面板 + 突眼球 — 四个完全不同的视觉世界。预告片失败的原因：四个相同 UI 的屏幕在稍微不同的滚动位置上。

### 网站应用 / 网站（自动捕获）

使用 Pika MCP 的捕获工具：

```python
capture_website(url="https://example.com", mode="screenshot")
# Returns image_url — use directly as a reference
```

每个要包含的独立页面/视图调用一次。

### 本地文件

用户提供路径 → 通过 Pika MCP 上传每个（见资产上传部分下方）。

---

## Stage 1 — 应用分析

在获取屏幕后，**使用 Claude 的视觉读取每个截图**，在编写提示的任何文字之前。这是最重要的步骤——跳过它，你将得到一个通用的流态玻璃块，没有任何故事。

对于每个截图，记录：
- **显示什么 UI** — 例如 "聊天输入框带有建议的提示", "视频时间轴带有 AI 编辑芯片", "显示生成剪辑的代理结果卡"
- **它代表什么功能** — 例如 "创建条目", "代理在工作", "输出/分享"
- **情绪注册** — 这是力量时刻、轻松时刻还是啊哈时刻？

此外，从 `fetch_appstore_screens` 结果或用户提供的描述中提取应用元数据：
- 应用名称、副标题、一行价值主张
- 类别和目标用户

**Stage 1 的输出：一个编号的功能图：**
```
Screen 1 — [filename]: 显示 [X UI]. 代表 [Y 功能]. 时刻: [hook/build/reveal].
Screen 2 — [filename]: ...
...
```

映射完成后，为每个屏幕的**视觉独特性**打分：它看起来是否与其他屏幕完全不同？优先选择具有不同调色板、不同布局密度和不同主题的屏幕。一个伟大的集合具有最大化的视觉跨度——钩子应该感觉与构建完全不同，构建应该感觉与揭示完全不同。

**在完成 Stage 1 之前，不要继续到 Stage 2。**

---

## Stage 2 — 叙事架构

每个 15 秒的预告片都需要一个脊柱。在触摸提示模板之前，设计故事弧线。

### 4 拍结构

| 拍 | 秒钟 | 工作 | 哪些屏幕 |
|------|------|------|-----------------|
| **钩子** | 0–3s | 抓住注意力 — 显示最引人注目的 UI 时刻或解决的问题 | 最具视觉冲击力的屏幕 |
| **构建** | 3–10s | 功能演示，按逻辑用户旅程顺序 | 2-3 张连续屏幕 |
| **揭示** | 10–13s | 拉回或产品概述 — “这就是它的工作”时刻 | 宽景或最完整的屏幕 |
| **标志** | 13–15s | 品牌锁定 — 字标出现，强调色脉冲 | 标志 (@Image6 或最后一个参考). `COMING SOON` 是稍后作为生成后文本叠加层添加的。 |

### 故事弧线类型 — 根据应用选择一个

| 弧线 | 使用时机 | 结构 |
|------|------------|-----------|
| **问题 → 解决方案** | 产品ivity/工具应用 | 钩子 = 痛点 UI → 构建 = 应用解决问题 → 揭示 |
| **功能游行** | 功能丰富的应用 | 钩子 = 最令人印象深刻的功能 → 构建 = 2 个其他功能 → 揭示 |
| **旅程** | 消费/生活方式应用 | 钩子 = 入口点 → 构建 = 体验 → 揭示 |
| **转换** | 前后类型应用 | 钩子 = “之前” → 构建 = 过程 → 揭示 = “之后” |

### Stage 2 的输出

在生成之前，明确地写出弧线：

```
Arc type: [Problem→Solution / Feature Parade / Journey / Transformation]
Hook (0-3s): Screen [N] — [what happens] — camera: [extreme close-up on X]
Build (3-10s): Screen [N] → [N] → [N] — [what each reveals] — camera: [whip pan / orbital / etc.]
Reveal (10-13s): Screen [N] — [what it shows] — camera: [pull-back to show full product]
Logo (13-15s): @Image[N] — 字标在 [accent color] 光芒中完整出现。不要要求视频模型渲染 `COMING SOON`；它被添加为生成后的文本叠加层。
```

在定义弧线之前，不要编写 Seedance 提示。

---

## Stage 2.5 — GPT-Image-2 增强

在定义弧线并选择 3-5 张屏幕后，使用 GPT-image-2 增强每个屏幕，然后再上传到 Seedance。这可以将压缩的网站捕获和 App Store 缩略图提升到更干净、更高保真度的参考。

对于每个选定的屏幕（包括标志/结束卡参考）：

```python
result = generate_image_edit(
    provider="gpt-image-2",
    prompt="High quality version, preserve all content exactly",
    images=["<original_cdn_url>"],
    aspect_ratio="16:9",   # match the capture — use 9:16 for portrait screens
    quality="medium",
)
# use result.image_url (or result.url) as the Seedance reference
```

**规则：**
- 保持提示与所示完全相同 — 短的、非描述性的。描述图像内容会使 GPT-image-2 产生幻觉。
- 匹配 `aspect_ratio` 与原始捕获（桌面 = 16:9，移动 = 9:16）。
- 并行运行所有增强（每个屏幕一个调用）。
- 使用增强的 URL 作为 Seedance 调用的 `reference_images` 数组 — 不要使用原始的。
- 保持你的 Stage 1 功能图描述不变 — 它们描述了原始内容，增强图像保留了原始内容。

---

## Stage 3 — 提示编写

在功能图（Stage 1）和弧线（Stage 2）在手中时，编写 Seedance 提示。每个 `@Image` 描述都必须引用真实的 UI 内容，绝不要写像“一个移动界面带有控件”这样的通用描述。

根据阅读应用的屏幕选择模板，而不是默认为流态玻璃。阅读以下其中之一，根据应用的个性；另一个模板永远不会加载：

- **模板 A — 电影叙事**（默认；产品ivity、AI、创意、社交、食物、游戏）：阅读 `references/template-a-cinematic.md`。经过验证的 BEAT-结构模板加上示例。
- **模板 B — 流态玻璃**（仅限摄影、相机、滤镜应用，其中镜头/滤镜隐喻适用）：阅读 `references/liquid-glass.md`。模板 B 骨架加上玻璃转换词汇。

强调色始终来自品牌 — 阅读图标和主要 UI 颜色，永远不要编造一个。

### 两个模板的规则

- 每个来自 Stage 1 功能图的 `@Image` 描述
- 相机方向来自 Stage 2 弧线
- 不要写“应用界面”或“移动屏幕” — 要具体
- 保持在 200 字以内
- **为什么特异性很重要：** Seedance 使用 `@ImageN` 描述作为其主要简报 — “一个深色聊天界面”与“一个 VHS 三面板网格，城市街道、滑板公园和海岸日落，带有复古时间戳叠加”产生完全不同的结果。从 Stage 1 功能图中复制最具体的视觉细节，逐字复制。

---

## 生成视频

**主要 — Seedance:**
```python
generate_reference_video(
    provider="seedance",
    reference_images=["<url1>", "<url2>", "<url3>", "<url4>", "<url5>"],  # 3–5 张屏幕 + 图标
    prompt="<prompt using @Image1 … @Image5 tokens>",
    resolution="1080p",   # always
    duration=15,          # always
    sound=True,           # always
    aspect_ratio="16:9",  # or 9:16 / 1:1 per user request
    seed=<int>,           # 设置一个；重复使用它以进行内容政策恢复
)
```

### Seedance 生成的音频审核恢复

如果 Seedance 完成生成并返回一个 422，其正文包括 `type: "content_policy_violation"`, `reason: "partner_validation_failed"`, `loc: ["body", "generated_video"]`, `msg: "Output audio has sensitive content."`, 将其视为可恢复的生成音频审核假阳性。

重试预算：生成音频恢复最多最多 3 次恢复渲染：一个 `sound=False` 探测，一个 `sound=True` 重播，和一个 Kling 回退。超出此上限后，停止或按文档记录成功 silent URL 的 Kling 回退；不要继续探测 Seedance。

1. 用 `sound=False` 和相同的 `seed` 重试完全相同的提示和 `provider` 与原始失败的 Seedance 调用。
2. 如果 silent 探测成功，用 `sound=True` 和相同的提示/参考集重播。
3. 如果 `sound=True` 重播成功，将恢复的 silent URL 路由到 Stage 4 作为 `generated_teaser_url`。保留 silent 探测 URL 仅作为调试上下文。
4. 如果 silent 探测失败，将失败视为视频/参考审核，并使用 Kling 回退。
5. 如果 silent 探测成功但 `sound=True` 重播再次失败，运行一次 Kling 回退。如果 Kling 不可用，将 silent URL 路由到 Stage 4 作为 `generated_teaser_url` 并明确指出生成音频审核仍然不稳定。

不要在重试路径中更改提示、参考、aspect ratio、duration 或 seed。更改任何内容都会将 silent 探测变为一个新的生成，而不是测试是否仅生成的音频触发了审核。

### Seedance 超时恢复

如果 Seedance 在 15 分钟总轮询上限之前返回终端超时，将其视为提供者队列饱和，而不是提示/内容失败。不要等待提供者超时字符串，例如 `seedance timed out after 900s` 或 `seedance timed out after 1200s`。

当发生这种情况时，运行 Kling 回退，使用相同的选定的参考、相同的节拍结构、`duration=15`、`sound=True` 和 `quality_mode="pro"`。将 `@ImageN` 提示令牌转换为 `<<<image_N>>>` 之前调用 Kling。

在 15 分钟总时间内，按照轮询合同上述进行：在 15 分钟总时间内取消处于非终端状态的原任务，而不是在原始可能仍然活跃的情况下开始回退。

不要在超时后继续重试 Seedance 除非用户明确要求等待 Seedance。超时路径已经花费了启动演示的时钟预算；切换提供者是此技能的文档恢复。

**回退 — Kling（非音频 partner_validation_failed 或 insufficient_balance）：**
```python
generate_reference_video(
    provider="kling",
    reference_images=["<url1>", "<url2>", "<url3>", "<url4>", "<url5>"],
    prompt="<prompt using <<<image_1>>> … <<<image_5>>> tokens>",
    quality_mode="pro",   # = 1080p on Kling (NOT resolution=)
    duration=15,
    sound=True,
    aspect_ratio="16:9",
)
```

### Kling 排队/交接恢复

Kling 回退是异步的。如果 `generate_reference_video(provider="kling")` 返回 `task_id`，请按照长运行 `task_status` 调用合同使用长运行轮询合同。
