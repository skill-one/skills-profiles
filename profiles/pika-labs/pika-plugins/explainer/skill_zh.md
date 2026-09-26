# /pika:explainer

生成一个 60-80 秒的 URL 解释视频：通过一个节拍表时间线驱动真实浏览器沿着 URL 浏览，生成一个与旁白同步的角色头像，并将所有内容合成在 1280×800 的 macOS Sonoma 画框中，画框内有一个 240 像素的内部头像（包括 3 像素宽的白色描边环，外径为 246 像素），位于画布 (20, 476) 位置，并在每个中间节拍处对元素进行放大。适用于任何 URL — 产品页面、文档网站、博客文章、发布页面。GitHub URL 会激活仓库感知模式（README 扫描 + 活动演示检测）；所有其他 URL 使用通用页面浏览流程。

**使用方法：** `/pika:explainer <url> [--focus "角度"] [--avatar <url>] [--voice <id>] [--lipsync-provider pika|kling] [--preview] [--live-url <url>]`

## 成本透明度门

在进行任何付费 MCP 调用之前，调用一次 `identity_balance({verbose: true})`。显示当前余额、近期消耗率和剩余运行时间，然后使用以下确切消息来控制运行：

> 预计成本：约 50-500 个信用（~$0.50-$5.00），具体取决于唇同步提供者、旁白、字幕和预览模式。这可能达到 $5，请回复 `proceed` 继续或 `cancel` 停止。

在用户回复 `proceed` 之前，不要调用任何付费 MCP 工具。如果用户回复 `cancel`，则停止并等待用户的下一条消息。门控在 URL 和可选标志已知后、头像生成、语音、唇同步、字幕或视频合成之前运行。

## 行为

### 默认值 — 快速启动，无需不必要的中间流程确认

- **无声解析头像 / 语音。** 从不询问“我应该使用您的头像吗？”或“哪个语音？”再启动。如果提供了显式覆盖（`--avatar`，`--voice`），则尊重；否则生成一个主持人头像并选择默认语音，然后继续。有关完整解析瀑布流的详细信息，请参阅步骤 1。
- **只有成本透明度门会要求 `proceed`。** 步骤 5 预览通常通过 `--preview` 进行显式头像的 **opt-in**，但当头像源是 `generated` 或 `regenerated` 的回退时，它会变成强制自动预览。在成本门之后，流程会端到端运行，除了那个必需的回退头像预览保护措施。
- **也不征集 `--focus`。** 从页面结构进行自信的第一次尝试；如果角度错过了，用户可以重新运行 `--focus "X"`。

这些默认值符合媒体生成工具（Midjourney / Sora / Runway / HeyGen / Pika.art）的行业标准：提交 → 渲染 → 返回。账户信用余额 + 提供者回退（步骤 9）是标准的保护措施。

### 局部头像图像在 Claude 桌面版上

Claude 桌面版目前无法将内联粘贴的图像传递给 MCP 工具（Anthropic 端限制）。如果用户内联粘贴了一张照片，或者提到了他们想用作 `--avatar` 的本地文件，请暂停步骤 1 并友好地发送他们以下内容：

> 提醒 — 粘贴的图像目前无法在 Claude 桌面版的 MCP 工具中到达（Anthropic 限制）。为您的头像有两个简单的选项：
>
> - **粘贴一个 URL** 如果它已经托管（Imgur、S3、您的网站）——最快
> - **附加图像文件** 让我可以在上传之前上传它。

当本地文件到达时，使用 `upload_asset` 将其转换为公共 URL，并使用返回的 `public_url` 作为 `--avatar <url>` 在步骤 1 之前。已经托管的 `https://...` URL 可以直接使用并跳过此步骤。如果完全未提供头像，将无声生成主持人肖像（步骤 1）。

### 步骤 0 — 解析 URL（空参数菜单）

从 `$ARGUMENTS` 中剥离标志（`--focus`，`--avatar`，`--voice`，`--live-url`，`--lipsync-provider`，`--no-captions`，`--preview`，`--skip-preview`，`--yes`）和 `key=value` 参数。**如果剩余内容不包含 `https://...` URL**（或为空 / 仅空白），请将此菜单**逐字**作为您的完整响应打印，然后**停止并等待用户的下一条消息**。在此处调用工具有风险记录或解释错误页面。如果 `$ARGUMENTS` 已经包含一个 URL，则无声跳过此步骤并继续步骤 1。

> **您想让我浏览哪个 URL？** 适用于以下任何内容：
>
> - **一个 GitHub 仓库** — 例如 `https://github.com/anthropics/claude-code`（激活仓库感知模式：README 扫描 + 活动演示检测）
> - **一个产品页面 / 发布页面** — 例如 `https://pika.art`
> - **一个文档网站** — 例如 `https://docs.anthropic.com`
> - **一个博客文章 / 文章 URL**
>
> 输出：1280×800 macOS Sonoma 画框，带有左下角的头像唇同步，并在每个中间节拍处对元素进行放大。默认流程在成本门之后端到端运行；如果您想对显式头像进行 3 秒的唇同步健康检查，请传递 `--preview`。生成 / 重新生成的回退头像会自动运行该预览保护措施。
>
> 回复 URL 并开始。
>
> *提示：您不需要输入 `/pika:explainer` — 只要说类似“浏览 <url>”、“制作 <url> 的演示视频”或“解释这个仓库：<github-url>”，我会自动启动这个技能。*

当用户回复一个 URL 时，将其视为解析输入并继续步骤 1。不要重新提示。

### 步骤 1 — 解析输入 + 检测模式

必需：`url`（必须是 `https://...`）。
可选：`--avatar <url>`（主持人照片；如果省略，则会生成）、`--voice <minimax-voice-id>`、`--focus "..."`（编辑指导融入 vo_text）、`--live-url <url>`（强制提供活动演示 URL — 仅 GitHub 模式）、`--lipsync-provider <pika|kling>`（默认为 **`pika`** — parrot a2v，~2-5 分钟墙钟，头部动作略夸张。传递 `kling` 以获得更紧凑的以面部为中心的输出，约 5-30 分钟墙钟 — Kling 产生的主持人照片头部动作很少，但需要较长时间；保留用于高风险渲染）、`--no-captions`（跳过步骤 11 的字幕消耗 — 默认是字幕开启）、`--preview`（选择进入步骤 5 预览门控以显式头像；生成和重新生成的回退头像会自动运行预览门控）。`--skip-preview` 和 `--yes` 被接受为向后兼容的无操作。

**模式检测：**
- **GitHub 模式** — URL 主机是 `github.com` 并且路径匹配 `/{owner}/{repo}`（仓库根路径之后没有进一步路径段）。激活仓库感知功能：README 扫描、活动演示检测、GitHub 特定选择器。
- **通用 URL 模式** — 任何其他内容（产品页面、文档网站、博客文章、更深的 GitHub 路径，如 `/blob/HEAD/path`）。跳过 GitHub 功能；使用通用 CSS 选择器并浏览 URL 本身。

**头像解析（无声 — 从不询问用户）：**
1. 如果传递了 `--avatar <url>`，则使用它。
2. 否则，调用一次 `generate_image`，使用提示 `"专业主持人，友好的技术解说员，工作室肖像，1:1，自然光照"`，并使用返回的 URL。**不要**询问用户“我应该生成一个吗？” — 只是无声生成。

跟踪 `avatar_source` 作为 `explicit`、`generated` 或 `regenerated` 之一。

**头像适用性门控（在任何唇同步消耗之前强制执行）：**

在步骤 4 TTS 之前和任何 `generate_lipsync` 预览/完整调用之前，对解析的头像图像调用一次 `analyze_media(media=<avatar>, query=<gate_query>)`。这是唯一需要头像分析的情况，因为头像是中心解说资产，一个糟糕的生成头像可能会浪费整个渲染。

门控查询：

```
仅返回 JSON：{
  "is_single_front_facing_coherent_human_face": boolean,
  "has_visible_mouth": boolean,
  "is_faceless_or_masked": boolean,
  "is_mascot_illustration_or_non_human": boolean,
  "face_suitability_score": 0-100,
  "apparent_gender": "female" | "male" | "unclear",
  "reason": string
}
这张图像是否适合进行解说头像唇同步：一个正面的、连贯的人类面部，有可见的嘴巴？标记无面部、面具、吉祥物、仅插图、非人类或变形的头像。
```

仅当 `is_single_front_facing_coherent_human_face == true`、`has_visible_mouth == true`、`is_faceless_or_masked == false`、`is_mascot_illustration_or_non_human == false`，并且 `face_suitability_score >= 75` 时才通过。

如果头像失败且 `avatar_source` 是 `explicit`，则在付费唇同步之前停止并要求 `--avatar <看起来像照片的 URL>` 或允许生成主持人肖像。如果头像失败且 `avatar_source` 是 `generated`，则调用一次 `generate_image`，使用提示 `"逼真的专业主持人肖像，正面的、连贯的人类面部，可见的嘴巴，友好的技术解说员，中性的工作室背景，1:1，自然光照"`；设置 `avatar_source = "regenerated"` 并在重新生成的头像上重新运行此适用性门控。如果重新生成的头像也失败，则中止并显示清晰的错误，而不是尝试唇同步。

每当 `avatar_source` 是 `generated` 或 `regenerated` 时，设置 `avatar_auto_preview_required = true`；否则为 false，除非用户传递了 `--preview`。

**语音解析（无声 — 从不询问用户）：**
1. 如果传递了 `--voice <id>`，则使用它。
2. 否则，选择与解析的头像的明显性别相匹配的休闲 MiniMax `speech-2.8-hd` 预设：
   - **女性编码头像** → `English_PlayfulGirl`（温暖、休闲、明显女性声音 — 已验证）
   - **男性编码头像** → `English_Jovialman`（温暖、休闲男性）
   - **不清楚 / 中性** → `English_Jovialman`（默认）

   从头像适用性门控结果中推断性别。**不要**询问用户。

   **不要使用 `English_FriendlyPerson`** — 尽管在 MiniMax 的目录中被归类为“女性”，但它的显示名称是“Friendly Guy”，在播放时读作男性。`English_PlayfulGirl` 是休闲女性选择的规范。其他已验证的女性替代方案：`English_Upbeat_Woman`、`English_LovelyGirl`、`English_radiant_girl`。

下面的流程按步骤注释：**仅 GitHub**、**仅通用** 或 **两者** 模式。

### 步骤 2 — 读取源（不调用 MCP）

**两者模式：** 使用 Claude 的 `WebFetch` 获取输入 URL，以拉取页面的主要内容（h1、英雄部分、标题、主要文本）。

在此源读取期间构建 `proper_noun_glossary`。包括产品、仓库、公司、模型、框架和 URL/域、页面标题、h1、README 标题、仓库元数据、包名称和重复的大写标记的规范拼写。对于 GitHub 仓库，保留 README/源扫描显示的确切拼写，例如 `Ollama`、`Llama`、`DeepSeek`、`Gemma`。稍后在编写旁白和燃烧手动字幕时使用此词汇表，以便字幕文本不会语音漂移到拼写错误，如 "Olama" 或 "DeepSeq"。

**GitHub 模式补充：** 还获取顶级文件树、（尽力）`package.json` / `pyproject.toml`，以及通过 `gh api repos/{owner}/{repo}` 获取的 GitHub API 仓库元数据（`homepage`、`description`、`language`、`topics`）。按优先级检测候选 `live_url`：

1. 用户提供的 `--live-url`。
2. **GitHub API `meta.homepage` 字段** — 当维护者在 GitHub 设置中配置了仓库的 homepage 时设置。
3. `package.json` `"homepage"` 字段。
4. README 中的第一个匹配项 `https?://[^\s)\"'<>]+(?:vercel\.app|netlify\.app|github\.io|fly\.dev|railway\.app|render\.com|herokuapp\.com|surge\.sh)[^\s)\"'<>]*`。
5. **任何其他 URL 在 README 中，徽章区域 / "Live Demo" / "项目页面" / "演示" 文本指向的。** 允许列表正则表达式遗漏任意自定义域（例如 `<project>-project-page.com`）；当 README 明确指定了项目页面时，优先于 github.io 回退。
6. GitHub Pages 惯例 `https://{owner}.github.io/{repo}` — 但仅当深层树包含前端信号（`index.html`、`App.tsx`、`App.jsx`、`App.vue`、`app.py`、`main.py`）时。

如果没有候选者解析，则节拍表会跳过节拍 6-7。

**通用 URL 模式：** 输入 URL 本身是节拍表浏览的唯一 URL — 没有活动 URL 推断，没有额外的元数据获取。跳过步骤 2.5 和步骤 3.0；直接跳转到步骤 3。

### 步骤 2.5 — 验证 `live_url` 可达性（仅 GitHub 模式，不调用 MCP）

如果选择了候选 `live_url`，在编写节拍 6-7 之前验证它是否提供真实内容。使用 `WebFetch` 对候选进行调用并检查响应：

- 如果响应状态是 4xx / 5xx，**将 `live_url` 设置为 None** 并跳过节拍 6-7。github.io 回退特别可以作为主机名访问，但通常返回 404（“这里没有 GitHub Pages 网站”）对于尚未启用 Pages 的仓库 — 录制 404 页面会浪费 ~12 秒的解释内容。
- 如果响应渲染了 GitHub Pages "404 — 这里没有 GitHub Pages 网站。" 模板（启发式：响应正文包含 `"There isn't a GitHub Pages site here"`），则跳过 `live_url` 并跳过节拍 6-7。
- 否则，保留 `live_url` 以用于节拍 6-7。

这与检查 `live_url` 的旧可达性门控相同，该门控使用短超时并跟随重定向。

### 步骤 2.6 — 通用 URL 预飞行（仅通用 URL 模式，不调用 MCP）

在为非 GitHub URL 编写节拍之前，使用 WebFetch 获取输入 URL 并检查响应。此步骤防止三种常见的通用 URL 失败模式：（a）录制验证码 / 机器人阻止页面而不是内容，(b)  cookie/同意横幅吞噬视频的前 ~3 秒，(c) 通用 CSS 选择器遗漏页面的实际英雄 / 部分。

**A. 机器人阻止 / 验证码检测 — 如果匹配则中止：**

如果响应正文包含任何：

- `"Verify you are human"` / `"verify you are not a robot"`
- `"captcha"` / `"CAPTCHA"` / `"reCAPTCHA"`
- `"403 Forbidden"` / `"Access Denied"`
- `"Just a moment"` + `cf-chl-bypass`（Cloudflare 挑战）
- `"We're sorry, something went wrong"`（亚马逊风格的机器人阻止）
- 一个 `<title>` 或 h1 仅显示“Robot Check” / “Are you a robot?”

→ **中止** 并向用户显示清晰错误："通用 URL 模式无法渲染此网站 — 页面正在使用无头 Chrome 显示机器人检测 / 验证码挑战。尝试不同的 URL，或者先运行真实用户版本的页面以验证它是否干净地加载。"

**B. Cookie / 同意横幅检测 — 使用 `extra_css` + 可选点击解除：**

扫描响应以查找这些模式（不区分大小写）：

- 以 `onetrust-`、`truste-`、`cookie-banner`、`cookie-consent`、`gdpr-`、`consent-`、`cmp-` 开头的 ID / 类
- 匹配 `(?i)accept (all )?cookies` / `(?i)agree.{0,10}cookies` / `(?i)i (accept|agree)` 的按钮
- Apple 特定横幅：id `ac-gdpr-banner` 或类 `as-globalfooter-curtain`
- Google 同意：`[role="dialog"]` 包含文本 "Before you continue"

如果检测到，设置 `cookie_banner_present = true`。多层防御 — 录制使用 BOTH：

1. **CSS 注入 (`extra_css`)** 在 `capture_website` 调用中隐藏常见横幅，即使点击下面错过了，横幅在视觉上也会消失。
2. **一个 `click` `timed_action`** 在 `at_s: 0.0` 对最可能的关闭选择器执行（从 WebFetch DOM 中提取，例如 `#onetrust-accept-btn-handler`、`[aria-label*="Accept all" i]`、`button[id*="accept"]`）。

`extra_css` 负载（使用此文本逐字 — 覆盖 ~80% 的同意平台）：

```
#onetrust-banner-sdk, #onetrust-pc-sdk, #onetrust-consent-sdk { display: none !important; }
#truste-consent-track, #truste-consent-content, .truste_box_overlay { display: none !important; }
[id*="gdpr-cookie"], [id*="cookie-consent"], [id*="cookie-banner"] { display: none !important; }
[class*="cookie-banner"], [class*="cookie-consent"], [class*="consent-banner"] { display: none !important; }
[class*="CookieBanner"], [class*="CookieConsent"], [class*="ConsentBanner"] { display: none !important; }
#ac-gdpr-banner, .as-globalfooter-curtain { display: none !important; }  /* Apple */
[role="dialog"][aria-label*="cookie" i], [role="dialog"][aria-label*="consent" i] { display: none !important; }
.cmp-container, .cmp-modal, .cmp-banner { display: none !important; }
```

**C. 实际 DOM 元素识别 — 发出具体选择器：**

通用 CSS 选择器（`h1`、`[class*="hero"]`、`section h2`）在语义化/标记良好的网站上有效，但在大型企业网站上会遗漏伪装的类名（apple.com 使用 `tile-headline` / `as-headline-section-title`，而不是 `hero-*`）。对于每个主题，优先选择 WebFetch 中观察到的**实际 DOM 元素**：

- 读取渲染的 HTML/markdown WebFetch 返回的内容。注意页面的实际主要 `<h1>` 文本和类。
- 注意页面的部分结构（h2 标题及其父容器）。
- 注意任何突出的 CTA / 注册 / 定价元素。
- 对于每个通用 URL `zoom_target.selector`，按顺序应用此**选择器阶梯**：
  1. 在渲染的 DOM 中观察到稳定 id 或类（`#hero`、`.tile-headline`、`.as-headline-section-title`、`.pricing-card`），当它是人类可读且具体时。
  2. 可访问性/链接属性（`[aria-label*="Get started" i]`、`a[href*="pricing"]`、`a[href="/new"]`）用于 CTA 或导航主题。
  3. 语义结构（`main > section:nth-of-type(N) h2`、`main section:nth-of-type(N) [role="img"]`、`footer h2`），当类名看起来是生成的（Tailwind `_1a2b3c`、CSS 模块 `module__hero___xYz`）时。
  4. 广泛的回退（`h1`、`main`、`section h2`、`button`、`a[href]`），仅当前三个选项不可用时。

所有发出的选择器必须是纯 CSS，`document.querySelector` 可以解析。**不要发出 `:contains(...)`、`:has-text(...)`、`text=...` 或 XPath**；这些都是 Playwright/text-query 的便利功能，在 `capture_website` 的平滑滚动路径中不会工作。如果需要文本匹配，请针对附近的稳定 `href`、`aria-label`、id/类或位置选择器。

**D. SPA / 懒加载检测——增加初始等待时间：**

如果 WebFetch 响应中的可见标题少于 3 个或文本内容最少，页面可能是 SPA 渲染的，在 `domcontentloaded` 之后。在任何主题触发之前，发出更长的初始 `wait` 动作（`{type: "wait", at_s: 0.0, ms: 2500}`），而不是默认的 600ms 沉淀。

**E. `--focus` 在提供时受尊重（不要征集）：**

如果没有 `--focus`，从通用结构提示中选择主题——静默地继续，并自信地尝试第一次。**不要**在触发之前询问用户“我应该关注什么？”；如果第一次尝试错过了他们想要的视角，用户可以通过使用 `--focus "the X feature"` 重新运行来迭代。如果提供 `--focus`，锚定主题选择在短语上：使用与它匹配的页面部分，忽略无关的营销铬。

### Step 3.0 — 必要的 README 部分扫描（GitHub 模式仅限，无 MCP 调用）

在编写主题表之前，**扫描 README**（不区分大小写，全文）以查找任何这些部分名称。如果找到匹配项，你**必须**在 Step 3 中添加一个专门的主题，如果必要，则替换通用主题 4–5 中的一个：

| README 包含... | 必要的主题 |
|---|---|
| `overview` / `what is` | 滚动到该标题；缩放 `.markdown-heading:has(#user-content-overview) .heading-element`（或匹配的 slug） |
| `how it works` | 滚动到该标题；缩放 `.markdown-heading:has(#user-content-how-it-works) .heading-element` |
| `audio layer` / `audio timeline` | 滚动到音频层图表；缩放渲染的图形或其周围标题 |
| `claude code` / `mcp integration` | 滚动到该部分；缩放 `article pre` 或 `.highlight`（终端截图/代码块） |
| `architecture` / `system design` | 滚动到该部分；缩放 `.markdown-heading:has(#user-content-architecture) .heading-element` |
| `features`（当顶部突出时） | 滚动到该标题；缩放 `.markdown-heading:has(#user-content-features) .heading-element` |
| `getting started` / `quick start` / `installation` | 滚动到该标题；缩放 `.markdown-heading:has(#user-content-installation) .heading-element`（或匹配的 slug）——如果想要安装代码块，则回退到 `article pre` |
| `usage` / `examples` | 滚动到该标题；缩放 `.markdown-heading:has(#user-content-usage) .heading-element`（或匹配的 slug）——或它下面的第一个代码块 |

**GitHub 标题 slug 规则：** 小写，空格→短横线，删除非 `[a-z0-9-]` 字符。所以 "How it works" → `#user-content-how-it-works`，"Quick Start" → `#user-content-quick-start`。GitHub 目前将 README 标题渲染为 `.markdown-heading` 包装器，带有 `.heading-element` 和一个同级的永久链接锚点。通过 slug 目标，然后是标题：`.markdown-heading:has(#user-content-<slug>) .heading-element`。

**GitHub DOM 在 2026-05-28 验证：** 当前 repo-root 页面在 `strong[itemprop="name"] a` 处暴露仓库名称；渲染的 README 正文在 `.markdown-body`；README 标题在 `.markdown-body h1.heading-element`；README 部分标题在 `.markdown-heading:has(#user-content-<slug>) .heading-element`，`.markdown-body h2.heading-element` 作为广泛部分标题回退。验证期间，如果任何 `action_bboxes[].found` 值对于 GitHub 主题为 `false`，请停止并重新验证 GitHub 的当前 DOM，然后再继续；不要依赖默认位置回退用于仓库漫游视觉。

**选择器合同：** `bbox_selector` 需要是一个纯 CSS 选择器，可以通过 `document.querySelector` 解析（`capture_website` 通过 `page.evaluate` 运行平滑滚动 JS，它使用浏览器的原生选择器引擎）。避免 Playwright 扩展，如 `:has-text("...")`、`text=...` 或 `:visible`：它们在 Playwright 的 `page.query_selector` 中解析（所以 bbox 捕获找到元素），但在平滑滚动的 `document.querySelector` 中静默失败（所以页面不会滚动到目标，`bbox.y` 最终位于文档-Y 而不是 `top - 60 px`，这会触发 Step 8b 的 `bbox.y > recording_viewport.h` 退化过滤器并回退到默认位置缩放）。CSS Level 4 `:has(...)` 是纯的，并在现代 Chromium 中受支持。

这些部分是大多数解释性仓库中最信息的视觉元素。遗漏它们会产生一个通用漫游；包含它们会给解释性一个具体的“展示，不要说”主题。Step 3.0 将这些视为硬性要求而不是偶然指导，并包括七个常见于 OSS README 的高信号标题。

### Step 3 — 编写主题表（主线程，无 MCP 调用）

编写一个包含 8–10 个主题的 JSON 数组，**硬性总时长为 65–80 秒，硬性总字数为 165–200 字**（假设说话速度为每秒 2.5 个字）。每个主题：

```jsonc
{
  "t_start": 0.0,
  "t_end": 7.5,
  "action": { "type": "navigate" | "scroll_to" | "hover", "url": "...", "selector": "..." },
  "zoom_target": { "selector": "...", "description": "..." },
  "vo_text": "要说的确切字词——1 到 2 句对话式句子"
}
```

**硬性约束（在发出主题表之前验证——如果任何失败则拒绝草稿）：**
1. 每个主题需要所有五个字段：`t_start`、`t_end`、`action`（带 `type` 和 `url`）、`zoom_target`（带 `selector`）、`vo_text`。缺少字段 ⇒ 拒绝并重新编写。
2. 主题 0 的 `t_start` = 0.0；`t_end[i] == t_start[i+1]`（连续性）。
3. `len(vo_text.split()) / 2.5` ≈ `t_end - t_start` 每个主题。目标为该估计的 ±10%；如果您的草稿比 2.5 wps 密集，请收紧 `vo_text` 直到它适合。
4. **最后一个主题的 `t_end` 总和 ≤ 80 秒。**（参考输出为 86.5s 包括介绍；嘴唇同步音频为 ~83s。Kling 头像/image2video 在当前负载下可靠地卡在 ~90 秒的音频之后——超过 80 秒有 20 分钟的 Kling 超时风险。）
5. **在 165 和 200 之间的总说话字数。**
6. 每个主题的 `zoom_target.selector` 需要页面的有效 CSS 选择器。**GitHub 模式更偏好**当前 GitHub 仓库/README 选择器：`strong[itemprop="name"] a`、`.markdown-body h1.heading-element`、`.markdown-heading:has(#user-content-<slug>) .heading-element`、`.markdown-body h2.heading-element`、`.blob-code-inner`、`.highlight`、`.octicon-star`、`nav`。**通用 URL 模式更偏好**强大的通用选择器：`h1`、`[role="main"]`、`main`、`header`、`nav`、`.hero`、`.feature`、`section h2`、`[class*="cta"]`、`[class*="hero"]`、`button`、`a[href]`。**选择器需要在主题的动作动作结束后在渲染的页面上解析**——在发出之前，通过 WebFetch 查看可见的 DOM。

如果提供了 `--preview` 或者 `avatar_auto_preview_required == true`：

1. 使用 `provider: "minimax-tts"` 的 `generate_speech`，可选的 `voice_id`，以及 `text: "Hi, I'm your presenter. Let's explore this repo together."` → `preview_audio_url`。
2. 使用 `provider: <resolved_lipsync_provider>`（默认为 `pika`；如果提供了 `--lipsync-provider kling`，则使用 `kling`），`image: <avatar>`，`audio: preview_audio_url` 的 `generate_lipsync` → `preview_lipsync_url`（裸唇同步，约 3 秒）。这里使用与步骤 9 将用于完整音频相同的提供者，预览的作用是在长杆渲染之前确认头像+声音+提供者的组合。
3. 向用户逐字呈现：

   > 预览准备就绪：`<preview_lipsync_url>`
   > 这确认了头像+声音的组合。完整渲染是一个长杆（~5–30 分钟 Kling 唇同步在完整音频上）。
   > 回复 `yes` 继续，或回复任何其他内容取消。

4. 匹配 `^(yes|go|proceed|confirm|y)$`（不区分大小写）。任何其他内容 → 停止，不再进行 MCP 调用。

### 步骤 6 — 构建 `timed_actions` 并录制

将节拍表转换为 `capture_website` `timed_actions`。**每个节拍一个 `timed_action`** — 设置 `bbox_selector` 为节拍的 `zoom_target.selector`，`capture_website` 内部捕获该元素的后续动作 bbox（遗留 600 ms 稳定 → 平滑滚动到 `top - 60 px` → 1300 ms 动画后 → 测量，所有服务器端）。

按顺序为每个节拍发出一个条目：

- **`navigate` 节拍**：`{type: "navigate", at_s: <t_start>, url: <action.url>, bbox_selector: <zoom_target.selector>}`。工作器导航，等待绝对 `at_s + 0.6 s`，滚动 `bbox_selector` 进入视图，并测量 bbox — 所有这些都不需要调用者安排后续步骤。
- **`scroll_to` / `hover` 节拍**：`{type: "scroll", at_s: <t_start>, selector: <action.selector or zoom_target.selector>, bbox_selector: <zoom_target.selector>}`。动作自己的 `selector` 驱动页面滚动；`bbox_selector` 驱动 bbox 测量（可以相同也可以不同 — 通常相同）。(`capture_website` 没有 `hover`；滚动到视图是类似操作。）

**不要在编写的节拍之前添加引言滚动**。唇同步音频从节拍表的 `t=0` 开始计时；前置引言会使屏幕录制向前移动约 3 秒，而音频未移动，导致音频/视频不同步。`capture_website` 录制从 `t=0` 开始，节拍 0 的 URL 已经加载，所以第一个编写的节拍是视觉定位点。

调用 `capture_website`：

- `url: <节拍 0 的 action.url>`
- `timed_actions: <上面构建的 N 元素列表>`（每个节拍一个条目）
- `duration_s: ceil(audio_duration_seconds)` — `beats[].t_start` 和 `t_end` 已经在步骤 4.5 中重新缩放到 TTS 音频时间线，所以 `duration_s` 只是音频长度。旧的 `max(...)` 防御措施防止 TTS 超出范围不再需要。

**通用 URL 模式添加**（根据步骤 2.6 预飞行）：

- `extra_css: <来自步骤 2.6 §B 的 cookie-banner-hiding CSS 负载>` — 防御性：通过 `display: none !important;` 隐藏常见的同意平台，即使可选点击错过，横幅在录制中也是不可见的。
- **为 SPA / 懒加载页面添加一个 `wait` 动作** `{type: "wait", at_s: 0.0, ms: 2500}`（根据步骤 2.6 §D）；对于“正常”页面使用 1500ms。这为英雄图像的懒加载、字体的交换和滚动触发的动画准备好时间，在第一个节拍触发之前。
- **如果 `cookie_banner_present` 来自步骤 2.6 §B**，还添加一个 `click` 动作 `{type: "click", at_s: 0.5, selector: <从 WebFetch DOM 检测到的关闭选择器>}`。**`beats[]` 数组已经在步骤 4.5 中向前移动了 `+1.5s` 来计算 cookie 关闭的延迟，并且 TTS 音频已经在步骤 4 中填充了 1.5 秒的静音（步骤 4）；这里不需要进一步移动。节拍 1 的 `timed_action.at_s` 读取 `beats[0].t_start` 直接，这在 cookie 模式下是 1.5。**
- **如果 `cookie_banner_present == false`**，不需要 cookie 横幅动作；只需添加前置等待动作。

捕获 `video_url`，`recording_viewport`，`action_bboxes`。结果返回 `recording_viewport: {w, h}` 和 `action_bboxes: [{idx, selector, found, bbox: {x,y,w,h}}]` 以及 `video_url`。

**`action_bboxes[].idx` 语义**：`idx` 字段是输入 `timed_actions` 数组中的位置。

- **GitHub 模式**：由于每个节拍一个 `timed_action`，`idx` 与节拍索引 1:1 映射 — 步骤 8 直接使用 `entry.idx` 作为 `beat_idx`。
- **通用 URL 模式**：前置的 `wait`（以及可选的 cookie 关闭 `click`）将数组向前移动 1 或 2。计算 `beat_idx = entry.idx - prepend_count`，其中 `prepend_count` 是 1（仅等待）或 2（等待 + 点击）。跳过 `beat_idx < 0` 的条目（这些是设置动作，不是节拍）。

每个条目的 `selector` 字段报告 `bbox_selector`（即 `zoom_target.selector`），而不是动作自己的 `selector`。

**通用 URL bbox 命中率警告**：在 `capture_website` 返回后，在步骤 8 消耗测量之前计算 bbox 覆盖率：

```
bbox_total_count = 带有 zoom_target.selector 的编写的节拍数量
bbox_found_count = `beat` 条目中 `found == true` 且 bbox 不是一个退化的计数的数量
bbox_hit_rate = bbox_found_count / max(1, bbox_total_count)
```

使用上述相同的 `prepend_count` 映射，以便前置设置动作不计入命中率。使用步骤 8b 过滤器将 bbox 视为退化（使用步骤 8b 过滤器，`bbox.y > recording_viewport.h` 或 `bbox.h > recording_viewport.h * 1.5`）。如果 `bbox_hit_rate < 0.70`，设置 `bbox_warning` 为此精确的用户可见句子，并传递到步骤 12：

> 在 `<missed>/<total>` 节拍上错过了针对元素的目标缩放 — 那些节拍将使用帧中心进行缩放。该网站可能使用混淆的类名或滚动触发的渲染。

### 步骤 7 — 浏览器界面

`edit_browser_frame`：

- `video_url: <步骤 6 video_url>`
- `url: (如果 GitHub 模式且存活了步骤 2.5 则 live_url 否则 input_url，截断到 65 个字符)`
- `tab_title: <30 个字符的标题>` — GitHub 模式：`(meta.description 或 repo_name 或 "")[:30]`。通用 URL 模式：页面的 `<title>`（来自步骤 2 中的 WebFetch）或 URL 的主机名，截断到 30 个字符。防止 `None`/空。

返回 `framed_url`（1280×800 Sonoma + 界面）。

### 步骤 8 — 构建 `zoom_keyframes` 并应用

常量：

- `INTRO_BEATS = 2` — 按 **节拍表索引** 门控。跳过索引 0 和 1 的缩放（上述结构骨架中的“节拍 1”和“节拍 2”）。
- `HOLD_GAP = 0.6` — 每次缩放前和缩放后的 1.0× 秒。
- `MIN_BEAT_DUR = 1.5` — 低于此的节拍被跳过（没有空间进行有意义的缩放）。
- `SCALE = 1.35`（精确的元素目标缩放）。
- `FALLBACK_SCALE = 1.25`（默认位置回退，当没有可用的 bbox 时）。
- `FALLBACK_RAMP = 0.4`。

**注意**：`beats[].t_start` / `t_end` 在步骤 4.5 中已经重新缩放（如果适用，则进行了 cookie 移动）到音频时间线。`HOLD_GAP`（0.6s），`MIN_BEAT_DUR`（1.5s），以及 1.0s 内部间隔检查都基于这些最终值 — 它们是渲染视频上的真实秒数。

`edit_browser_frame` 的内部内容偏移：`CONTENT_X=56, CONTENT_Y=108, CONTENT_W=1168, CONTENT_H=637`。

坐标转换（录制 px → 帧内 px）：

```
cx_framed = 56  + (bbox.x + bbox.w/2) * (1168 / recording_viewport.w)
cy_framed = 108 + (bbox.y + bbox.h/2) * (637  / recording_viewport.h)
```

**使用每个节拍默认值 + bbox 覆盖模式构建缩放列表。** 遗留的设置遵循“每个非引言节拍都获得缩放 — 如果可用则基于 bbox，否则为默认位置”的规则。在这里重现这个规则：

**步骤 8a — 为每个非引言、足够长的节拍预填充默认位置关键帧。**

默认位置的常量：
- `DEFAULT_CX = 56 + 1168 // 2`（帧画布的中心）
- `DEFAULT_CY = 108 + 637 // 3`（内容区域的上三分之一，大多数 GitHub UI 突出显示的位置）

从索引 `INTRO_BEATS`（= 2）到末尾遍历节拍表。对于每个节拍：

- 如果 `t_end - t_start < MIN_BEAT_DUR`（1.5s），跳过 — 太短，无法进行有意义的缩放。
- 计算关键帧的内部间隔为 `[t_start + HOLD_GAP, t_end - HOLD_GAP]`。如果该间隔短于 1.0s，跳过。
- 否则，预填充该节拍在每节拍映射（称为 `zoom_keyframes_by_beat[beat_idx]`）中的槽位为 `{cx: DEFAULT_CX, cy: DEFAULT_CY, scale: FALLBACK_SCALE (1.25), ramp_s: FALLBACK_RAMP (0.4)}` 加上修剪的 `t_start`/`t_end`。

**步骤 8b — 使用 bbox 导出的精确缩放覆盖。**

对于 `action_bboxes` 中的每个条目：

- **GitHub 模式**：`beat_idx = entry.idx`，因为步骤 6 每个节拍发出一个 `timed_action`。
- **通用 URL 模式**：`beat_idx = entry.idx - prepend_count`，因为步骤 6 前置了等待动作，有时还有 cookie 关闭点击。如果 `beat_idx < 0`，跳过；该条目属于设置，不是编写的节拍。
- 如果 `beat_idx < INTRO_BEATS`，跳过。
- 如果 `entry.found` 为 false，跳过。
- 如果该节拍已经在 `zoom_keyframes_by_beat` 中（在步骤 8a 中由 `MIN_BEAT_DUR`/`1.0s` 规则过滤掉），跳过。
- **过滤退化的 bbox**：如果 `bbox.y > recording_viewport.h`（屏幕外捕获 — 页面没有及时滚动元素进入视图）或 `bbox.h > recording_viewport.h * 1.5`（全页 `<main>` 元素 — 产生无意义的缩放中心），跳过。
- 使用上述录制-px → 帧内-px 转换计算 `cx_framed`/`cy_framed` 从 bbox 中心。用 `{cx: cx_framed, cy: cy_framed, scale: SCALE (1.35), ramp_s: min(0.5, (t_end - t_start) * 0.15)}` 覆盖该节拍的槽位。

**最终列表**：按 `t_start` 对 `zoom_keyframes_by_beat` 的值排序，以产生 `zoom_keyframes` 数组。

这保证了每个非引言、足够长的节拍都获得缩放 — 当 bbox 捕获工作时精确，否则默认定位。避免了“整个运行时间都是平视频”的失败模式。

如果 `len(zoom_keyframes) > 0`，调用 `edit_animate_zoom`，`video_url: framed_url, zoom_keyframes`。返回 `zoomed_url`。否则（没有符合条件的节拍 — 给定步骤 3 的 65-80 秒约束，这种情况应该很少见）跳过并使用 `framed_url` 作为 `zoomed_url`。

### 步骤 9 — 唇同步完整音频

`generate_lipsync`：

- `provider: <resolved_lipsync_provider>` — **默认：`pika`**（鹦鹉 a2v）。如果明确传递 `--lipsync-provider kling`，则尊重 `kling`。
- `image: <avatar>`
- `audio: <步骤 4 audio_url>`
- **kling 仅限旋钮**：当 `provider == "kling"` 时，添加 `mode: "pro"` 和 `prompt: "talking head, face centered, mouth syncs to audio, minimal head movement, professional presenter"` 以获得更精致的主持人感觉。两者在 `pika` 上都默默地被忽略（鹦鹉有自己的驱动程序）。

**提供者权衡**：

| 提供者 | 墙上时间 | 头部动作 | 何时使用 |
|---|---|---|---|
| **`pika`**（默认） | ~2–5 分钟 | 稍微更戏剧化、自然 | 大多数运行时的默认值 — 快速迭代、可观看的输出、比 kling 快 10 倍 |
| `kling`（可选） | ~5–30 分钟 | 最小、面朝中心、主持人风格 | 高风险渲染，其中头像必须像专业的主持人一样阅读；容忍长杆 |

服务器端等待覆盖调用，如果响应形状是 `{task_id, status: "queued"}`，则在紧密循环中轮询 `task_status`（不睡眠），直到状态达到终端状态（`completed`，`failed` 或 `cancelled`）。在 `completed` 时，捕获 `lipsync_url`。在 `failed` / `cancelled` 时，回退到 **另一个** 提供者（kling ↔ pika），如下面的故障转移说明所示。

**故障转移**：
- 如果 `pika` 失败（很少见 — 鹦鹉 a2v 在典型的解释音频长度上很稳健）→ 一次重试，`provider: "kling"`。
- 如果 `kling` 超过工作器的 1200 秒上限而停滞（作为重复的 `processing` 状态且没有完成可见）→ 回退到 `provider: "pika"`。步骤 4.5 的音频长度门控应该在该到达这里之前捕获长音频的情况，但故障转移处理残留风险。

**为什么 pika 是默认值**：
- 速度 — 典型的解释性墙上时间从 ~10–15 分钟降至 ~5–7 分钟总时间，因为唇同步是长杆。
- 质量足够好 — 鹦鹉 a2v 是自然主义的；轻微的额外头部动作在 60-80 秒的剪辑和头像圆 PiP 中读作投入而不是分散注意力。
- Kling-mode-pro 精致主要在 246 像素的圆圈内不可见 — 面部区域太小，无法让最小头部动作的差异在大多数观众中注册。

为了获得参考输出的典型“专业主持人”感觉，显式传递 `--lipsync-provider kling`。

**面部连贯性门控**（在 PiP 合成之前强制执行）：

捕获 `lipsync_url` 后，在步骤 10 之前对原始唇同步视频进行采样。调用 `extract_frame(video_url=<lipsync_url>, at_times=[1.0, audio_duration_seconds * 0.5, max(1.0, audio_duration_seconds - 1.0)])` 获取开始/中间/结束帧。在批量模式下，捕获 `frame_urls = extract_result.urls` 并忽略 `url` 字段，除非 `urls` 缺失时作为后备。因为 `analyze_media.media` 接受单个 URL 字符串，对每个帧 URL 做一个 `analyze_media` 调用；不要传递数组。

对于每个 `frame_url`，调用 `analyze_media(media=<frame_url>, query=<single_frame_gate_query>)` 并使用此查询：

```
仅返回 JSON：{
  "face_integrity_score": 0-100,
  "is_coherent_human_face": boolean,
  "has_visible_mouth": boolean,
  "is_abstract_melting_mask_or_non_human": boolean,
  "observation": string,
  "recommended_action": "pass" | "retry_other_provider" | "abort"
}
这个帧是否显示一个连贯的人类主持人面部，有可见的嘴巴，不是抽象的块、融化的面具、吉祥物、无面部的插图或失真的非人面部？
```

在继续之前汇总帧裁决。只有当所有采样帧的最小/最差 `face_integrity_score` 都 `>= 75`，每个 `is_coherent_human_face == true`，每个 `has_visible_mouth == true`，并且每个 `is_abstract_melting_mask_or_non_human == false` 时才通过。保留每个帧的观察结果，以便中止消息可以命名是开始、中间还是结束帧失败。

如果门控在第一个提供者上失败，使用另一个提供者（pika ↔ kling）重试一次，使用相同的头像和音频，然后在第二个原始 `lipsync_url` 上再次运行这个面部连贯性门控。如果两个提供者都失败，中止并返回清晰的错误，并返回门控观察结果；**不要**继续到步骤 10 使用损坏的主持人。如果第二个提供者通过，则使用该提供者的 `lipsync_url` 下游。

在应用 `proper_noun_glossary` 规范拼写后，从最终拼接好的 `vo_text` 构建 `caption_script_text`。解说类视频中不要依赖自动转录来处理品牌/型号名称：即使浏览器画面中显示的文字正确，自动转录也可能对可见的专有名词进行语音拼写错误。

在调用工具之前确定字幕位置：
- 普通解说页面默认使用 `position: "bottom"`（`caption_position = "bottom"`）。
- 当当前节拍计划或捕获页面显示下三分之一区域有重要的主视觉文字、标题、价值主张、CTA 或代码（经典底部字幕条会遮挡这些内容）时，使用 `position: "top"`（`caption_position = "top"`）。

调用 `add_captions(video_url=<final_url>, style="classic", caption_mode: "manual", subtitle_text: <caption_script_text>, position: <caption_position>)`。手动模式会将修正后的解说文本均匀分配到检测到的时长内，并防止专有名词漂移。将结果保存为 `captioned_url`。

仅当用户传入了 `--no-captions`（在步骤 1 中解析）时跳过此步骤——默认为开启字幕。（注意：`/pika:podcast` **不会**烧录字幕——解说类视频中的旁白比快节奏的双主持人对话更容易转录。）

### 步骤 12 — 返回

如果步骤 6 中设置了 `bbox_warning`，在最终 URL 之前立即输出该警告，让用户知道某些节拍的视觉效果降级为画面中心缩放。然后在一行中输出 `captioned_url`（如果步骤 11 被跳过则为 `final_url`）：`Done: <url>`。

## 飞行后质量门

在宣告成功之前，对 `captioned_url` 或 `final_url` 调用 `analyze_media`，请求结构化判定：

```
仅返回 JSON：{
  "verdict": "clean" | "degraded" | "catastrophic",
  "observations": string[],
  "quality_warning": string | null,
  "re_roll_suggestion": string | null
}
检查字幕是否存在（除非使用了 --no-captions），缩放目标 / bbox 焦点是否落在被解说的 UI 元素上，是否存在空白帧或白闪问题，以及头像 PiP 是否遮挡了重要的页面内容。
同时验证主讲人面部保持连贯（不出现抽象、融化、无脸、面具或非人现象），`proper_noun_glossary` 中的专有名词在字幕中拼写正确，且字幕没有遮挡或覆盖主视觉文字、标题、价值主张文案、CTA 或解说正在指向的代码。
```

- 如果 `verdict` 为 `clean`，正常输出最终 URL。
- 如果 `verdict` 为 `degraded`，输出最终 URL 以及 `quality_warning`，以便用户在发布前审查。
- 如果 `verdict` 为 `catastrophic`，不要将解说视频标记为完成；输出判定结果和 `re_roll_suggestion`，而非宣告成功。

## 故障模式

| 症状 | 可能原因 | 恢复方法 |
|---|---|---|
| 首次 MCP 调用时出现 OAuth / 401 | 用户的 Pika 连接器令牌缺失或已过期 | 停止并告知用户重新认证 Pika MCP 连接器；在认证成功之前不要重试付费步骤。 |
| `capture_website` 返回空白帧、空 `action_bboxes` 或被阻止的页面 | 目标 URL 需要登录、被反爬虫检测、被 Cookie 覆盖，或在等待窗口之后才完成渲染 | 在事实依据充分时使用 WebFetch 文本回退；否则请求粘贴源材料或更简单的 URL。 |
| TTS 或口型同步提供商返回瞬态 5xx / 429 | 提供商队列或速率限制 | 在提示的回退时间后对完全相同的调用重试一次；如果再次失败，停止并附带提供商错误和最后一个已完成的检查点。 |
| 字幕或最终 QA 报告专有名词不可读、遮挡、空白帧或头像不连贯 | 生成的媒体未达到可发布标准 | 返回 `not publish-ready`，附带 QA JSON 和具体的重滚建议；不要在 catastrophic 判定时宣告成功。 |

## 关键短语

这些锚点在不同页面类型之间维持视觉契约：

| 短语 | 位置 | 为何关键 |
|---|---|---|
| `vanilla CSS that resolves via document.querySelector` | 选择器契约 | 使滚动、bbox 捕获和缩放在 `capture_website` 内部保持一致的对齐。 |
| `GitHub URLs activate repo-aware mode` | 模式检测 | 防止通用产品页节拍替代 README/代码讲解节拍。 |
| `8-10 beats`、`65-80 seconds`、`165-200 words` | 节拍表编写 | 使解说、屏幕录制、口型同步和字幕保持在可靠的时长范围内。 |
| `all beats[] mutations happen here` | 音频重缩放步骤 | 确保后续的捕获/缩放/合成步骤消费一个稳定的时间线。 |
| `extra_css` cookie 横幅隐藏载荷 | 通用 URL 预检 | 在横幅点击未命中时减少首帧横幅遮挡。 |

## 引擎选择：Pika 口型同步为默认，Kling 为可选

默认使用 Pika/parrot 口型同步，因为它更快，使大多数解说视频保持短迭代循环。仅当用户显式请求 `--lipsync-provider kling` 或高 stakes 渲染需要更居中的主讲人形象且能容忍更长的长杆阶段时，才使用 Kling。屏幕捕获、浏览器画面、缩放、PiP 和字幕围绕口型同步选择仍然是确定性的编辑/合成步骤。

## 运行时预期

使用 Pika 口型同步时典型实际耗时为 5-10 分钟，使用 Kling 口型同步时为 10-30+ 分钟：

| 步骤 | 实际耗时 | 备注 |
|---|---:|---|
| URL 读取 + 预检 | 10-60 秒 | GitHub README 扫描或通用 URL DOM/Cookie 检查 |
| TTS + 音频重缩放 | 30-90 秒 | 节拍时序在实际音频时长后归一化 |
| 屏幕录制 | 60-180 秒 | 取决于页面加载和导航次数 |
| 浏览器画面 + 缩放 | 1-3 分钟 | 确定性编辑/合成阶段 |
| 口型同步 | 2-5 分钟 Pika / 5-30 分钟 Kling | Kling 为可选，因为它是长杆步骤 |
| PiP + 字幕 | 1-3 分钟 | 设置 `--no-captions` 时跳过字幕 |

## 已知缺陷（作为后续服务端工作跟进）

- **Kling 头像模式和提示词已可用。** 要启用精致主讲人模式，传入 `--lipsync-provider kling`，步骤 9 的调用应添加 `mode: "pro"` 以及类似 `"talking head, face centered, mouth syncs to audio, minimal head movement, professional presenter"` 的提示词。这是减少口型同步中剧烈头部运动的品质杠杆。
- **屏幕录制没有调用方可控的白帧裁剪。** `capture_website` 内部有裁剪启发式但不向调用方暴露。在页面仍在加载时表现为解说视频开头的短暂白闪。`at_s: 0.0` 处的 800ms `wait` 动作通过给页面渲染时间有所缓解，但不会裁剪已录制的白帧。工作区增强项。
- **每节拍导航没有 `networkidle` 等待。** `capture_website` 结算到 `domcontentloaded` 加上 bbox 捕获分支的 600ms 操作后等待（服务端，当设置了 `bbox_selector` 时），但 SPA blob 页面在 `domcontentloaded` 之后才完成最终渲染，仍可能对着未挂载的代码块进行 bbox。工作区增强：在 `timed_actions[].navigate` 上暴露 `wait_until` 参数。
- **没有逐步输出大小验证门。** 健壮的文件大小检查应在每步之后验证 TTS ≥ 50KB、预览 ≥ 100KB、屏幕 ≥ 200KB、口型同步 ≥ 500KB、最终 ≥ 1MB。MCP 路径仅返回 URL；验证文件大小需要每步额外一次 `analyze_media` 调用（每次约 30 秒开销）。一旦用户端延迟预算允许就值得添加。目前，下游故障级联（例如零字节 TTS → 静默口型同步 → 空白合成）仅在步骤 11 才暴露。
- **`text_content` bbox 捕获未实现。** `capture_website` v1 仅对带有 CSS `selector` 的步骤返回 `action_bboxes`。仅有 `text_content` 的步骤不产生条目。在 `zoom_target` 中优先使用 CSS 选择器以保证缩放覆盖。
- **节拍表措辞不确定。** 对相同输入运行两次会产生不同的 vo_text 和不同的缩放位置。视觉*类型*是契约，而非像素级精确复现。
- **通用 URL 模式的品质因站点而异。** 带有语义化标记（`<h1>` + 清晰的 `<section>` + 命名 class 钩子）的现代独立/SaaS 落地页表现良好。大型企业站点（apple.com、microsoft.com、amazon.com）遇到多个已知限制：(a) **反爬虫检测** — 无头 Chrome 下页面可能提供降级版本或验证码；步骤 2.6 §A 会因这些中止但启发式并非穷尽；(b) **混淆的类名** — 用 `tile-headline` 而非 `hero-title` 使通用选择器失效；步骤 2.6 §C 的 WebFetch DOM 扫描有帮助但不完美；(c) **滚动触发动画不播放** — IntersectionObserver 驱动的主视觉揭示在真实用户滚动时触发，而非 Playwright 的 `scrollIntoView`；录制的帧可能是静态占位符；(d) **懒加载图片** — 带有 `loading="lazy"` 的 picture/source 元素在 600ms 或 2500ms 结算窗口内可能尚未解析；bbox 落在透明占位符上。变通方法：发布演示优先选择更简单/更小的营销页面，始终传入 `--focus "the X feature"` 锚定节拍选择，接受大型站点需要后续服务端 PR（cookie 横幅点击重试 + `wait_until=networkidle` + 通过 `IntersectionObserver` polyfill 触发动画）。
- **Cookie 横幅点击为单次尝试。** 步骤 2.6 §B 对从 WebFetch DOM 中提取的关闭选择器发出一次 `click`。如果 WebFetch 的 HTML 不包含横幅（JS 后渲染）或选择器错误，点击会静默失败——`extra_css` 载荷是关键防线。工作区增强：支持每个 `click` 动作的回退选择器列表，使工作区按顺序尝试。

## 认证

如果任何调用返回 401：用户的 OAuth 令牌已过期或尚未签发。下一次需要认证的 MCP 调用会自动触发 OAuth（浏览器打开 `@pika.art` Google 登录）。对于非交互环境，设置 `MCP_AUTH_TOKEN`。

## 示例

GitHub 模式（仓库感知：README 扫描 + 实时演示检测）：

- `/pika:explainer https://github.com/leigest519/OpenGame`
- `/pika:explainer https://github.com/anthropics/claude-cookbooks --focus "Claude Code MCP integration"`
- `/pika:explainer https://github.com/openai/whisper --preview`（测试新头像时选择进入预览门）

通用 URL 模式（任何非 GitHub URL — 直接驱动页面）：

- `/pika:explainer https://pika.art`
- `/pika:explainer https://vercel.com --focus "the deployment workflow"`
- `/pika:explainer https://docs.anthropic.com/en/docs/claude-code/plugins`
- `/pika:explainer https://your-product-page.com --avatar https://cdn.example.com/me.png --preview`
