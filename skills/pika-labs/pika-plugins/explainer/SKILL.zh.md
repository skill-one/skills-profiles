---
name: explainer
description: 在用户要求解释或任务与以下示例匹配时使用。~60-80秒的解释视频，适用于任何URL——GitHub仓库、产品页面、文档网站、博客文章或发布内容。URL浏览的规范工作流程。在用户要求“解释这个URL/仓库/网站/产品”、“为[URL]制作浏览视频”、“演示这个网站”、“Loom风格的[URL]解释”、“github.com/...的解释”或“解释这个产品链接”时使用。通过真实浏览器驱动URL，生成头像口型同步，并合成在1280×800 macOS Sonoma框架和246像素左下角头像圆圈中。GitHub URL会激活仓库感知模式（README扫描+实时演示检测）；其他URL使用通用页面浏览流程。
---

# /pika:explainer

生成一个 60-80 秒的 URL 解释视频：通过浏览器沿着节拍表时间线驱动 URL，生成与旁白同步的角色头像，并将所有内容合成在 1280×800 的 macOS Sonoma 画框中，画框内有一个 240 像素的内部角色（包括 3 像素白色描边环的 246 像素外部角色），位于画布 (20, 476) 位置，并在每个中间节拍上对元素进行放大。适用于任何 URL — 产品页面、文档网站、博客文章、发布页面。GitHub URL 会激活仓库感知模式（README 扫描 + 活动演示检测）；所有其他 URL 使用通用页面漫游流程。

**使用方法：** `/pika:explainer <url> [--focus "角度"] [--avatar <url>] [--voice <id>] [--lipsync-provider pika|kling] [--preview] [--live-url <url>]`

## 成本透明度门

在进行任何付费 MCP 调用之前，调用一次 `identity_balance({verbose: true})`。显示当前余额、近期消耗率和剩余运行空间，然后使用以下确切消息来控制运行：

> 预计成本：约 50-500 个信用（~$0.50-$5.00），具体取决于唇同步提供者、旁白、字幕和预览模式。这可能达到 $5，请回复 `proceed` 继续或 `cancel` 停止。

在用户回复 `proceed` 之前，不要调用任何付费 MCP 工具。如果用户回复 `cancel`，则停止而不生成。门控在 URL 和可选标志已知后运行，但在角色生成、语音、唇同步、字幕或视频合成之前运行。

## 行为

### 默认值 — 快速启动，无需不必要的中间流程确认

- **无声解析头像 / 语音。** 从不问“我应该使用你的头像吗？”或“哪个语音？”再启动。如果提供了显式覆盖（`--avatar`，`--voice`），则尊重；否则生成一个主持人头像并选择默认语音，然后继续。有关完整解析瀑布流的详细信息，请参阅步骤 1。
- **只有成本透明度门会要求 `proceed`。** 步骤 5 预览通常通过 `--preview` **选择性地**提供显式头像，但当头像源是 `generated` 或 `regenerated` 回退时，它会变成强制自动预览。在成本门之后，流程端到端运行，除了那个必需的回退头像预览护栏。
- **也不征集 `--focus`。** 从页面结构进行自信的第一次尝试；如果角度错过了，用户可以重新运行 `--focus "X"`。

这些默认值符合媒体生成工具（Midjourney / Sora / Runway / HeyGen / Pika.art）的行业标准：提交 → 渲染 → 返回。账户信用余额 + 提供者回退（步骤 9）是规范护栏。

### 局部头像图像在 Claude 桌面版上

Claude 桌面版目前无法将内联粘贴的图像传递给 MCP 工具（Anthropic 端限制）。如果用户内联粘贴了一张照片，或提到了他们想作为 `--avatar` 的本地文件，请暂停步骤 1 并友好地发送他们这个 — 类似于：

> 提醒 — 粘贴的图像目前无法在 Claude 桌面版的 MCP 工具中到达（Anthropic 限制）。为您的头像有两个简单的选项：
>
> - **粘贴一个 URL** 如果它已经托管（Imgur、S3、您的网站） — 最快
> - **附加图像文件** 这样我可以在生成之前上传它。

当本地文件到达时，使用 `upload_asset` 将其转换为公共 URL，并使用返回的 `public_url` 作为 `--avatar <url>` 在步骤 1 之前。已经托管的 `https://...` URL 可以按原样使用并跳过此步骤。如果完全未提供头像，将无声生成主持人肖像（步骤 1）。

### 步骤 0 — 解析 URL（空参数菜单）

从 `$ARGUMENTS` 中剥离标志（`--focus`，`--avatar`，`--voice`，`--live-url`，`--lipsync-provider`，`--no-captions`，`--preview`，`--skip-preview`，`--yes`）和 `key=value` 参数。**如果剩余内容不包含 `https://...` URL**（或为空 / 仅空白），请将此菜单**逐字**作为您的完整响应打印，然后**停止并等待用户的下一条消息**。在此处调用工具有风险记录或解释错误页面。如果 `$ARGUMENTS` 已经包含一个 URL，则无声跳过此步骤并继续步骤 1。

> **您想让我漫游哪个 URL？** 适用于以下任何内容：
>
> - **一个 GitHub 仓库** — 例如 `https://github.com/anthropics/claude-code`（激活仓库感知模式：README 扫描 + 活动演示检测）
> - **一个产品页面 / 发布页面** — 例如 `https://pika.art`
> - **一个文档网站** — 例如 `https://docs.anthropic.com`
> - **一个博客文章 / 文章 URL**
>
> 输出：1280×800 macOS Sonoma 画框，带有左下角的头像唇同步和在每个中间节拍上对元素进行放大的效果。默认流程在成本门之后端到端运行；如果您想对显式头像进行 3 秒唇同步的合理性检查，请传递 `--preview`。生成 / 重新生成的回退头像会自动运行该预览护栏。
>
> 回复 URL 并开始。
>
> *提示：您不需要输入 `/pika:explainer` — 只要说类似“漫游 <url>”、“制作 <url> 的演示视频”或“解释这个仓库：<github-url>”，我会自动启动这个技能。*

当用户回复一个 URL 时，将其视为解析输入并继续步骤 1。不要重新提示。

### 步骤 1 — 解析输入 + 检测模式

必需：`url`（必须是 `https://...`）。
可选：`--avatar <url>`（主持人照片；如果省略，则生成）、`--voice <minimax-voice-id>`、`--focus "..."`（编辑指导融入 vo_text）、`--live-url <url>`（强制提供活动演示 URL — 仅 GitHub 模式）、`--lipsync-provider <pika|kling>`（默认为 **`pika`** — parrot a2v，~2-5 分钟墙钟，头部动作略夸张。传递 `kling` 以获得更紧凑的以面部为中心的输出，约 5-30 分钟墙钟 — Kling 产生的主持人照片头部动作很少，但需要较长时间；保留用于高风险渲染）、`--no-captions`（跳过步骤 11 的字幕消耗 — 默认是字幕开启）、`--preview`（选择性地提供步骤 5 预览门以显式头像；生成和重新生成的回退头像会自动运行预览门）。`--skip-preview` 和 `--yes` 被接受为向后兼容的无操作。

**模式检测：**
- **GitHub 模式** — URL 主机是 `github.com` 并且路径匹配 `/{owner}/{repo}`（仓库根路径之后没有进一步路径段）。激活仓库感知附加功能：README 扫描、活动演示检测、GitHub 特定选择器。
- **通用 URL 模式** — 任何其他内容（产品页面、文档网站、博客文章、更深的 GitHub 路径，如 `/blob/HEAD/path`）。跳过 GitHub 附加功能；使用通用 CSS 选择器并漫游 URL 本身。

**头像解析（无声 — 从不询问用户）：**
1. 如果传递了 `--avatar <url>`，则使用它。
2. 否则，调用一次 `generate_image` 并使用提示 `"专业的主持人，友好的技术解说员，工作室肖像，1:1，自然光照"` 并使用返回的 URL。不要询问用户“我应该生成一个吗？” — 只是无声生成。

跟踪 `avatar_source` 作为 `explicit`、`generated` 或 `regenerated` 之一。

**头像适用性门（在任何唇同步消耗之前强制执行）：**

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
这张图像是否适合说话头唇同步：一个单人的、正面、连贯的人类面部，并且有可见的嘴巴？标记无面部、面具、吉祥物、仅插图、非人类或变形的头像。
```

仅当 `is_single_front_facing_coherent_human_face == true`、`has_visible_mouth == true`、`is_faceless_or_masked == false`、`is_mascot_illustration_or_non_human == false`，并且 `face_suitability_score >= 75` 时才传递。

如果头像失败并且 `avatar_source` 是 `explicit`，则在付费唇同步之前停止并要求 `--avatar <看起来像照片的 URL>` 或允许生成主持人肖像。如果头像失败并且 `avatar_source` 是 `generated`，则调用一次 `generate_image` 并使用提示 `"逼真的专业主持人肖像，单人的、正面、连贯的人类面部，可见的嘴巴，友好的技术解说员，中性的工作室背景，1:1，自然光照"`；设置 `avatar_source = "regenerated"` 并在重新生成的头像上重新运行此适用性门。如果重新生成的头像也失败，则中止并显示清晰的错误，而不是尝试唇同步。

每当 `avatar_source` 是 `generated` 或 `regenerated` 时，设置 `avatar_auto_preview_required = true`；否则为 false，除非用户传递了 `--preview`。

**语音解析（无声 — 从不询问用户）：**
1. 如果传递了 `--voice <id>`，则使用它。
2. 否则，选择一个与解析的头像的明显性别相匹配的休闲 MiniMax `speech-2.8-hd` 预设：
   - **女性编码的头像** → `English_PlayfulGirl`（温暖、休闲、明显是女性声音 — 已验证）
   - **男性编码的头像** → `English_Jovialman`（温暖、休闲男性）
   - **不清楚 / 中性** → `English_Jovialman`（默认）

   从头像适用性门结果中推断性别。不要询问用户。

   **不要使用 `English_FriendlyPerson`** — 尽管在 MiniMax 的目录中被归类为“女性”，但它的显示名称是“Friendly Guy”，在播放时读作男性。`English_PlayfulGirl` 是休闲女性选择的规范。其他已验证的女性替代方案：`English_Upbeat_Woman`、`English_LovelyGirl`、`English_radiant_girl`。

下面的流程按步骤注释：**仅 GitHub**、**仅通用** 或 **两者** 模式。

### 步骤 2 — 读取源（不调用 MCP）

**两者模式：** 使用 Claude 的 `WebFetch` 获取输入 URL 以拉取页面的主要内容（h1、英雄部分、标题、主要文本）。

在此源读取期间构建 `proper_noun_glossary`。包括产品、仓库、公司、模型、框架和 URL/域、页面标题、h1、README 标题、仓库元数据、包名称和重复的大写标记的规范拼写。对于 GitHub 仓库，保留 README/源扫描显示的确切拼写，例如 `Ollama`、`Llama`、`DeepSeek`、`Gemma`。稍后在编写旁白和燃烧手动字幕时使用此词汇表，以便字幕文本不会语音漂移到类似“Olama”或“DeepSeq”的错误拼写。

**GitHub 模式附加：** 还获取顶级文件树、（尽力）`package.json` / `pyproject.toml`，并通过 `gh api repos/{owner}/{repo}` 获取 GitHub API 仓库元数据（`homepage`、`description`、`language`、`topics`）。按优先级检测候选 `live_url`：

1. 用户提供的 `--live-url`。
2. **GitHub API `meta.homepage` 字段** — 当维护者在 GitHub 设置中配置了仓库的 homepage 时设置。
3. `package.json` `"homepage"` 字段。
4. README 中的第一个匹配项 `https?://[^\s)\"'<>]+(?:vercel\.app|netlify\.app|github\.io|fly\.dev|railway\.app|render\.com|herokuapp\.com|surge\.sh)[^\s)\"'<>]*`。
5. **README 中任何其他 URL，徽章区域 / "Live Demo" / "项目页面" / "演示" 文本指向的。** 允许列表正则表达式遗漏任意自定义域（例如 `<project>-project-page.com`）；当 README 明确指定了项目页面时，优先于 github.io 回退。
6. GitHub Pages 惯例 `https://{owner}.github.io/{repo}` — 但仅当深层树包含前端信号（`index.html`、`App.tsx`、`App.jsx`、`App.vue`、`app.py`、`main.py`）时。

如果没有候选者解析，则节拍表会跳过节拍 6-7。

**通用 URL 模式：** 输入 URL 本身是节拍表漫游的唯一 URL — 没有活动 URL 推断，没有额外的元数据获取。跳过步骤 2.5 和步骤 3.0；直接跳转到步骤 3。

### 步骤 2.5 — 验证 `live_url` 可达性（仅 GitHub 模式，不调用 MCP）

如果选择了候选 `live_url`，在编写节拍 6-7 之前验证它是否提供真实内容。使用 `WebFetch` 对候选进行调用并检查响应：

- 如果响应状态是 4xx / 5xx，**将 `live_url` 设置为 None** 并跳过节拍 6-7。github.io 回退特别可以作为主机名访问，但通常返回 404（“这里没有 GitHub Pages 网站”）对于尚未启用 Pages 的仓库 — 录制 404 页面会浪费 ~12 秒的解释内容。
- 如果响应渲染了 GitHub Pages “404 — 这里没有 GitHub Pages 网站。”模板（启发式：响应正文包含 `"There isn't a GitHub Pages site here"`），则跳过 `live_url` 并跳过节拍 6-7。
- 否则，保留 `live_url` 以用于节拍 6-7。

这与检查 `live_url` 的旧可达性门类似，该门使用短超时并跟随重定向。

### 步骤 2.6 — 通用 URL 预飞行（仅通用 URL 模式，不调用 MCP）

在为非 GitHub URL 编写节拍之前，WebFetch 输入 URL 并检查响应。此步骤防止三种常见的通用 URL 失败模式：（a）录制验证码 / 机器人阻止页面而不是内容，(b)  cookie/同意横幅吞噬视频的前 ~3 秒，(c) 通用 CSS 选择器遗漏页面的实际英雄 / 部分。

**A. 机器人阻止 / 验证码检测 — 如果匹配则中止：**

如果响应正文包含任何：

- `"Verify you are human"` / `"verify you are not a robot"`
- `"captcha"` / `"CAPTCHA"` / `"reCAPTCHA"`
- `"403 Forbidden"` / `"Access Denied"`
- `"Just a moment"` + `cf-chl-bypass`（Cloudflare 挑战）
- `"We're sorry, something went wrong"`（亚马逊风格的机器人阻止）
- 一个 `<title>` 或 h1 仅是“Robot Check” / “Are you a robot?”

→ **中止** 并向用户显示清晰错误："通用 URL 模式无法渲染此网站 — 页面在无头 Chrome 下显示机器人检测 / 验证码挑战。尝试不同的 URL，或首先运行真实用户版本的页面以验证它干净地加载。"

**B. Cookie / 同意横幅检测 — 使用 `extra_css` + 可选点击解除：**

扫描响应以查找这些模式（不区分大小写）：

- 以 `onetrust-`、`truste-`、`cookie-banner`、`cookie-consent`、`gdpr-`、`consent-`、`cmp-` 开头的 ID / 类
- 匹配 `(?i)accept (all )?cookies` / `(?i)agree.{0,10}cookies` / `(?i)i (accept|agree)`
- Apple 特定横幅：id `ac-gdpr-banner` 或类 `as-globalfooter-curtain`
- Google 同意：`[role="dialog"]` 包含文本 "Before you continue"

如果检测到，设置 `cookie_banner_present = true`。多层防御 — 录制使用 BOTH：

1. **CSS 注入 (`extra_css`)** 在 `capture_website` 调用中隐藏常见横幅，即使点击下面错过了，横幅在视觉上也会消失。
2. **一个 `click` `timed_action`** 在 `at_s: 0.0` 对最可能的关闭选择器执行（从 WebFetch DOM 中提取，例如 `#onetrust-accept-btn-handler`、`[aria-label*="Accept all" i]`、`button[id*="accept"]`）。

`extra_css` 有效负载（使用此内容逐字 — 覆盖 ~80% 的同意平台）：

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

**C. 真实 DOM 元素识别 — 发出具体选择器：**

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

如果没有 `--focus`，从通用结构提示中选择主题——静默地继续，并自信地尝试第一次。**不要**在触发之前询问用户“我应该关注什么？”；如果第一次尝试错过了他们想要的视角，用户可以通过使用 `--focus "the X feature"` 重新运行来迭代。如果提供 `--focus`，锚定主题选择在短语上：使用与它匹配的实际页面部分，忽略无关的营销铬。

### Step 3.0 — 必要的 README 部分扫描（GitHub 模式仅限，无 MCP 调用）

在编写主题表之前，**扫描 README**（不区分大小写，全文）以查找任何这些部分名称。如果找到匹配项，你**必须**在 Step 3 中添加一个专门的主题，如果需要，替换通用主题 4–5 中的一个：

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

**GitHub 标题 slug 规则：** 小写字母和空格→连字符，删除非 `[a-z0-9-]` 字符。所以 "How it works" → `#user-content-how-it-works`，"Quick Start" → `#user-content-quick-start`。GitHub 目前将 README 标题渲染为 `.markdown-heading` 包装器，带有 `.heading-element` 和一个兄弟永久链接锚点。通过 slug 目标定位包装器，然后定位标题：`.markdown-heading:has(#user-content-<slug>) .heading-element`。

**GitHub DOM 在 2026-05-28 验证：** 当前 repo-root 页面在 `strong[itemprop="name"] a` 处暴露仓库名称；渲染的 README 正文在 `.markdown-body`；README 标题在 `.markdown-body h1.heading-element`；README 部分标题在 `.markdown-heading:has(#user-content-<slug>) .heading-element`，`.markdown-body h2.heading-element` 作为广泛部分标题回退。验证期间，如果任何 `action_bboxes[].found` 值对于 GitHub 主题为 false，请停止并重新验证 GitHub 的当前 DOM，然后再继续；不要依赖默认位置回退用于仓库漫游视觉。

**选择器合同：** `bbox_selector` 需要是一个纯 CSS 选择器，可以通过 `document.querySelector` 解析（`capture_website` 通过 `page.evaluate` 运行平滑滚动 JS，它使用浏览器的原生选择器引擎）。避免 Playwright 扩展，如 `:has-text("...")`、`text=...` 或 `:visible`：这些在 Playwright 的 `page.query_selector` 中解析（所以 bbox 捕获找到元素），但在平滑滚动的 `document.querySelector` 中静默失败（所以页面不会滚动到目标，`bbox.y` 最终位于文档-Y 而不是 `top - 60 px`，这会触发 Step 8b 的 `bbox.y > recording_viewport.h` 退化过滤器并回退到默认位置缩放）。CSS Level 4 `:has(...)` 是纯的，并在现代 Chromium 中受支持。

这些部分是大多数解释性仓库中最信息的视觉元素。遗漏它们会产生一个通用漫游；包含它们会给解释性一个具体的“展示，不要说”主题。Step 3.0 将这些视为硬性要求而不是偶然指导，并包括七个 OSS README 中常见的高信号标题。

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

**硬性约束（在发出主题表之前验证——如果任何项失败，则拒绝草稿）：**
1. 每个主题都需要所有五个字段：`t_start`、`t_end`、`action`（带有 `type` 和 `url`）、`zoom_target`（带有 `selector`）、`vo_text`。缺少字段 ⇒ 拒绝并重新编写。
2. 主题 0 的 `t_start` = 0.0；`t_end[i] == t_start[i+1]`（连续性）。
3. `len(vo_text.split()) / 2.5` ≈ `t_end - t_start` 每个主题。目标为该估计的 ±10%；如果您的草稿比 2.5 wps 密集，请收紧 `vo_text` 直到它适合。
4. **最后一个主题的 `t_end` 总和 ≤ 80 秒。**（参考输出为 86.5s 包括介绍；唇同步音频为 ~83s。Kling 头像/image2video 在当前负载下可靠地卡在 ~90 秒音频之后——超过 80 秒有 20 分钟 Kling 超时风险。）
5. **在 165 和 200 之间的总说话字数。**
6. 每个主题的 `zoom_target.selector` 需要是对该主题落点页面的有效 CSS 选择器。**GitHub 模式更偏好**当前 GitHub 仓库/README 选择器：`strong[itemprop="name"] a`、`.markdown-body h1.heading-element`、`.markdown-heading:has(#user-content-<slug>) .heading-element`、`.markdown-body h2.heading-element`、`.blob-code-inner`、`.highlight`、`.octicon-star`、`nav`。**通用 URL 模式更偏好**强大的通用选择器：`h1`、`[role="main"]`、`main`、`header`、`nav`、`.hero`、`.feature`、`section h2`、`[class*="cta"]`、`[class*="hero"]`、`button`、`a[href]`。**选择器需要在主题的动作沉淀后的渲染页面解析**——在发出之前，通过 WebFetch 查看可见的 DOM 进行验证。
7. `vo_text` 是 1-2 句对话式句子。开发语音。没有舞台指示。没有 markdown。
8. `action.url` 是一个有效的 `https://...` URL，当 `action.type == "navigate"` 时；`action` 类型为 "navigate" 时必需。

**Step 4 之前自检：** 验证 `total_words` 在 `[165, 200]` 中 AND `total_seconds`（= `beats[-1].t_end`）在 `[65, 80]` 中。如果任何一个超出边界，请重新编写主题表——不要继续到 TTS。 （不需要“打印”任何地方——这是一个内部草稿验证；只需拒绝草稿并重新编写，直到它通过。）

**结构骨架——GitHub 模式（承重，用于视觉合同——匹配原始，但 Step 3.0 如果适用会覆盖）：**

- **主题 1：** `navigate` 仓库根，缩放 `strong[itemprop="name"] a`（仓库名），钩子句子。
- **主题 2–3：** `navigate` 到特定源文件（`https://github.com/{owner}/{repo}/blob/HEAD/<path>`），缩放 `.blob-code-inner` 或 `.highlight`。选择与叙述声明匹配的文件——不要导航到您不会谈论的文件。
- **主题 4–5：** `scroll_to` README 部分，缩放 `.markdown-heading:has(#user-content-<slug>) .heading-element`、`.markdown-body h2.heading-element`、`.markdown-body`。**如果 Step 3.0 提出了必要部分，用这些替换这些槽位。**
- **主题 6–7（仅当 `live_url` 存活 Step 2.5）：** `navigate` 到 `live_url`，缩放 `nav` / `h1` / `.hero` / `main` / `button` / `.feature`。
- **主题 8：** 回到仓库根，缩放 `.octicon-star`，结束语。

**结构骨架——通用 URL 模式：**

- **主题 1：** `navigate` 到输入 URL，缩放 `h1` 或 `[class*="hero"] h1`（页面的主要标题），钩子句子。
- **主题 2–3：** `scroll_to` 页面的英雄/价值主张/第一个功能部分。缩放 `.hero`、`[class*="hero"]`、`[class*="feature"]` 或 `section:nth-of-type(1) h2`。选择可见元素，叙述参考。
- **主题 4–5：** `scroll_to` 更深的部分——功能列表、截图、定价、社会证明。缩放 `section h2`、`[class*="feature"] img`、`[class*="testimonial"]`、`[class*="pricing"]` 或页面上的任何突出语义元素。
- **主题 6–7：** `scroll_to` CTA / 注册 / 演示嵌入。缩放 `[class*="cta"]`、`button`、`a[class*="button"]` 或 `[id*="signup"]`。（通用模式中没有演示导航——输入 URL 就是演示。）
- **主题 8：** `scroll_to` 页脚/结束元素，缩放 `footer h2`、`footer` 或回到顶部使用 `h1`。结束语。

如果提供 `--focus`，将它的角度编织到 `vo_text` 中，而不改变结构骨架。优先选择**CSS 选择器而不是 `text_content`** 在 `zoom_target.selector` 中——bbox 捕获仅限于选择器（见已知差距）。

### Step 4 — TTS

调用 `generate_speech`，`provider: "minimax-tts"`，`text: <full vo_text join>`，可选 `voice_id`（来自 `--voice` 或 Step 1 默认预设）。捕获 `result.audio_url`（调度器返回音频在 `audio_url` 下，而不是 `url`）和 `result.duration_seconds`。

**陈旧语音回退检测：** 调度器使用默认 `Calm_Woman` 语音重新尝试一次 Minimax `status_code:2054`（语音 ID 未找到——通常是每个代理工作空间的指针，Minimax 在 7 天不活动后自动删除）。在重试成功时，响应包含文档模式之外的两个额外字段（透传）：`voice_id_requested`（工作员首先尝试的已种植但陈旧的 ID）和 `fallback_reason: "invalid_minimax_voice_id"`。**如果在响应中看到 `fallback_reason == "invalid_minimax_voice_id"`，请向用户显示一条简短消息，类似于：**"您注册的语音在 Minimax 上过期（7 天不活动后自动回收）；我们使用了系统默认。如果想要个性化，请通过 `clone_voice` 重新克隆。" 渲染不会失败——它只是使用默认语音——所以这是信息性的，不是重试触发器。

**Cookie-横幅音频填充（通用 URL 模式，`cookie_banner_present == true` 从 Step 2.6 §B）：** 当 Step 4 调用使用默认 Minimax 路径时，在调用 `generate_speech` 之前将 Minimax 的暂停标记 `<#1.5#>` 添加到 `text:` 参数中。Minimax 的 `speech-2.8-hd` 尊重 `<#N#>` 作为 N 秒的沉默；返回的 `audio_url` 和 `duration_seconds` 本地包含 1.5s 的前导。如果 Step 4 使用 `provider="elevenlabs"`，跳过 Minimax 标记并使用以下回退音频混合填充路径。这使音频与 Step 4.5 中在 Step 4.5 中应用的 cookie 拒绝 +1.5s 偏移对齐。

**回退**（仅当烟雾测试显示标记被此语音忽略时）：正常调用 `generate_speech`，然后 `edit_audio_mix` 将结果叠加到 1.5s 的静音基座上，偏移 1.5s。**然后调用 `analyze_media(url=<padded_audio_url>)` 探测填充的持续时间并重新绑定 `duration_seconds = result.duration_seconds`** 在 Step 4.5 消耗它之前。`analyze_media` 是**唯一的权威持续时间探测**——不要依赖 `edit_audio_mix` 的返回有效负载（它的持续时间字段没有合同保证）。

### Step 4.5 — 音频长度验证 + 主题表重缩放

应用于 Step 4 后的 `audio_duration_seconds`（包括任何 cookie 前导填充）。最终状态：`beats[].t_start` / `t_end` 是匹配音频播放时间线的绝对墙钟秒。**所有 `beats[]` 变化都在这里发生**；步骤 6 和 8 是只读消费者。

**门 1 — Kling 停滞上限（提供者上限，原始音频_duration_seconds）：**
如果 `audio_duration_seconds > 90`，中止并重新编写主题表，使用更紧的字数预算。Kling 头像/image2video 在 ~90 秒后停滞。

**门 2 — 退化 TTS（说话内容长度）：**
计算 `narration_duration = audio_duration_seconds - (1.5 if cookie_banner_present else 0.0)`。如果 `narration_duration < 30s`，重试 Step 4 一次（并重新计算 `narration_duration` 从重试的音频）。如果重试也返回 `narration_duration < 30s`，中止并调查——可能失败模式：截断的 Minimax 响应、静音音频、vo_text 未正确连接。

**门 3 — 重缩放：**
- `narration_duration = audio_duration_seconds - (1.5 if cookie_banner_present else 0.0)`
- `scale = narration_duration / beats[-1].t_end`
- 如果 `scale < 0.5` 或 `scale > 1.5`，中止并重新编写。结构破坏的 TTS（或字数预算差异很大）；重缩放无法挽救它。
- 对于每个主题：`beat.t_start *= scale; beat.t_end *= scale`
- 如果 `cookie_banner_present`：对于每个主题，`beat.t_start += 1.5; beat.t_end += 1.5`
- **最终钳位：** `beats[-1].t_end = audio_duration_seconds`（精确）。保证浮点等式的不变性，无论 cookie 模式或累积浮点漂移如何。

**门 3 通过后**，发出一条单行操作员日志以显示缩放值，供运行后诊断：

```
Rescaled beats by scale=X.XX (audio=Y.YYs, narration_duration=Z.ZZs, cookie_pad=W.Ws)
```

**建议（不是门）：** 缩放接近 1.0 是理想的。`scale > 1.2` 意味着音频明显比预期慢——视觉感觉“拉伸”但保持同步。`scale < 0.85` 意味着音频更快——视觉感觉“匆忙”但保持同步。两者都通过门；如果用户报告“感觉节奏不对”而不是“不同步”，请重新编写，使用更紧或更松的字数预算。

### Step 5 — 预览门（可选或回退头像自动预览）

仅当用户未通过 `--preview` **且** `avatar_auto_preview_required == false` 时跳过 Step 5。自动预览在头像来自静默生成的回退或 Avatar 适合性门重新生成的头像时强制执行。这些路径是面无表情或非人类头像可能不知不觉进入的地方，所以一个便宜短预览是此前的守门人，在完整的 60-80 秒唇同步花费之前。

`--skip-preview` 和 `--yes` 被接受为无操作，以向后兼容——它们是旧的 opt-out 标志。

如果提供了 `--preview` 或者 `avatar_auto_preview_required == true`：

1. 使用 `provider: "minimax-tts"` 的 `generate_speech`，可选 `voice_id`，以及 `text: "Hi, I'm your presenter. Let's explore this repo together."` → `preview_audio_url`。
2. 使用 `provider: <resolved_lipsync_provider>`（默认为 `pika`；如果提供了 `--lipsync-provider kling`，则使用 `kling`），`image: <avatar>`，`audio: preview_audio_url` 的 `generate_lipsync` → `preview_lipsync_url`（裸唇同步，约 3 秒）。这里使用与步骤 9 将用于完整音频相同的提供者，预览的作用是在长杆渲染之前确认头像+声音+提供者的组合。
3. 向用户逐字呈现：

   > 预览准备就绪：`<preview_lipsync_url>`
   > 这确认了头像+声音的组合。完整渲染是一个长杆（~5-30 分钟 Kling 唇同步在完整音频上）。
   > 回复 `yes` 继续，或回复任何其他内容取消。

4. 匹配 `^(yes|go|proceed|confirm|y)$`（不区分大小写）。任何其他内容 → 停止，不再进行 MCP 调用。

### 步骤 6 — 构建 `timed_actions` 和录制

将节拍表转换为 `capture_website` `timed_actions`。**每个节拍一个 `timed_action`** — 设置 `bbox_selector` 为节拍的 `zoom_target.selector`，`capture_website` 内部捕获该元素的后续动作 bbox（遗留 600 ms 稳定 → 平滑滚动到 `top - 60 px` → 1300 ms 动画后 → 测量，所有服务器端）。

按顺序为每个节拍发出一个条目：

- **`navigate` 节拍**：`{type: "navigate", at_s: <t_start>, url: <action.url>, bbox_selector: <zoom_target.selector>}`。工作器导航，等待绝对 `at_s + 0.6 s`，滚动 `bbox_selector` 进入视图，并测量 bbox — 所有这些都不需要调用者安排后续步骤。
- **`scroll_to` / `hover` 节拍**：`{type: "scroll", at_s: <t_start>, selector: <action.selector or zoom_target.selector>, bbox_selector: <zoom_target.selector>}`。动作自己的 `selector` 驱动页面滚动；`bbox_selector` 驱动 bbox 测量（可以相同也可以不同 — 通常相同）。(`capture_website` 没有 `hover`；滚动到视图是类似操作。)

**不要在编写的节拍之前添加引言滚动**。唇同步音频从节拍表的 `t=0` 开始计时；前置引言会使屏幕录制向前移动约 3 秒，而音频未移动，导致音频/视频不同步。`capture_website` 录制从 `t=0` 开始，并加载了节拍 0 的 URL，所以第一个编写的节拍是视觉定位点。

调用 `capture_website`：

- `url: <节拍 0 的 action.url>`
- `timed_actions: <上面构建的 N 元素列表>`（每个节拍一个条目）
- `duration_s: ceil(audio_duration_seconds)` — `beats[].t_start` 和 `t_end` 已经在步骤 4.5 中重新缩放到 TTS 音频时间线，所以 `duration_s` 只是音频长度。旧的 `max(...)` 防御措施防止 TTS 越界不再需要。

**通用 URL 模式添加**（根据步骤 2.6 预飞行）：

- `extra_css: <来自步骤 2.6 §B 的 cookie-banner 隐藏 CSS 负载>` — 防御性：通过 `display: none !important;` 隐藏常见的同意平台，即使可选点击错过，横幅在录制中也是不可见的。
- **为 SPA / 懒加载页面添加一个 `wait` 动作** `{type: "wait", at_s: 0.0, ms: 2500}`（根据步骤 2.6 §D）；对于“正常”页面使用 1500ms。这为英雄图像的懒加载、字体的交换和滚动触发的动画准备好时间，在第一个节拍触发之前。
- **如果 `cookie_banner_present` 来自步骤 2.6 §B**，还添加一个 `click` 动作 `{type: "click", at_s: 0.5, selector: <从 WebFetch DOM 检测到的关闭选择器>}`。**`beats[]` 数组已经在步骤 4.5 中向前移动了 `+1.5s` 来计算 cookie 关闭的延迟，并且 TTS 音频已经在步骤 4 中填充了 1.5 秒的静音（无进一步移动需要。** 节拍 1 的 `timed_action.at_s` 读取 `beats[0].t_start` 直接，这在 cookie 模式下是 1.5。
- **如果 `cookie_banner_present == false`**，不需要 cookie 横幅动作；只需添加前置等待动作。

捕获 `video_url`，`recording_viewport`，`action_bboxes`。结果返回 `recording_viewport: {w, h}` 和 `action_bboxes: [{idx, selector, found, bbox: {x,y,w,h}}]` 以及 `video_url`。

**`action_bboxes[].idx` 语义**：`idx` 字段是输入 `timed_actions` 数组中的位置。

- **GitHub 模式**：一个定时动作每个节拍，`idx` 与节拍索引 1:1 映射 — 步骤 8 直接使用 `entry.idx` 作为 `beat_idx`。
- **通用 URL 模式**：前置的 `wait`（以及可选的 cookie 关闭 `click`）将数组向前移动 1 或 2。计算 `beat_idx = entry.idx - prepend_count`，其中 `prepend_count` 是 1（仅等待）或 2（等待 + 点击）。跳过 `beat_idx < 0` 的条目（这些是设置动作，不是节拍）。

每个条目的 `selector` 字段报告 `bbox_selector`（即 `zoom_target.selector`），而不是动作自己的 `selector`。

**通用 URL bbox 命中率警告**：在 `capture_website` 返回后，在步骤 8 消耗测量之前计算 bbox 覆盖率：

```
bbox_total_count = 带有 zoom_target.selector 的编写的节拍数量
bbox_found_count = `found` 为 true 且 bbox 不会退化时节拍条目的计数
bbox_hit_rate = bbox_found_count / max(1, bbox_total_count)
```

使用上述相同的 `prepend_count` 映射，以便前置设置动作不计入命中率。使用步骤 8b 过滤器将 bbox 视为退化（使用 `bbox.y > recording_viewport.h` 或 `bbox.h > recording_viewport.h * 1.5`）。如果 `bbox_hit_rate < 0.70`，设置 `bbox_warning` 为此精确的用户可见句子，并传递到步骤 12：

> 在 `<missed>/<total>` 节拍上错过了针对元素的目标缩放 — 那些节拍将使用帧中心进行缩放。该网站可能使用混淆的类名或滚动触发的渲染。

### 步骤 7 — 浏览器边框

`edit_browser_frame`：

- `video_url: <步骤 6 video_url>`
- `url: (live_url 如果 GitHub 模式且存活了步骤 2.5 否则 input_url，截断到 65 个字符)`
- `tab_title: <30 个字符的标题>` — GitHub 模式：`(meta.description 或 repo_name 或 "")[:30]`。通用 URL 模式：页面的 `<title>`（来自步骤 2 中的 WebFetch）或 URL 的主机名，截断到 30 个字符。防止 `None`/空。

返回 `framed_url`（1280×800 Sonoma + 边框）。

### 步骤 8 — 构建 `zoom_keyframes` 并应用

常量：

- `INTRO_BEATS = 2` — 按 **节拍表索引** 门控。跳过索引 0 和 1 的缩放（上述结构骨架中的“节拍 1”和“节拍 2”）。
- `HOLD_GAP = 0.6` — 秒钟的 1.0× 在每个缩放之前和之后。
- `MIN_BEAT_DUR = 1.5` — 低于此的节拍被跳过（没有空间进行有意义的缩放）。
- `SCALE = 1.35`（精确的元素目标缩放）。
- `FALLBACK_SCALE = 1.25`（默认位置回退，当没有可用的 bbox 时）。
- `FALLBACK_RAMP = 0.4`。

**注意**：`beats[].t_start` / `t_end` 已经在步骤 4.5 中重新缩放（如果适用，则进行了 cookie 移动）到音频时间线。HOLD_GAP (0.6s)，MIN_BEAT_DUR (1.5s)，以及 1.0s 内部间隔检查都基于这些最终值 — 它们是渲染视频中真实的秒数。

`edit_browser_frame` 的内部内容偏移：`CONTENT_X=56, CONTENT_Y=108, CONTENT_W=1168, CONTENT_H=637`。

坐标转换（录制 px → 帧内 px）：

```
cx_framed = 56  + (bbox.x + bbox.w/2) * (1168 / recording_viewport.w)
cy_framed = 108 + (bbox.y + bbox.h/2) * (637  / recording_viewport.h)
```

**使用每个节拍默认位置 + bbox 覆盖模式构建缩放列表。** 遗留的设置遵循“每个非引言节拍都获得缩放 — 如果可用则基于 bbox，否则为默认位置”的规则。在此重现该规则：

**步骤 8a — 为每个非引言、足够长的节拍预填充默认位置关键帧。**

默认位置的常量：
- `DEFAULT_CX = 56 + 1168 // 2`（帧画布的中心）
- `DEFAULT_CY = 108 + 637 // 3`（内容区域的上三分之一，大多数 GitHub UI 突出显示的位置）

从索引 `INTRO_BEATS`（= 2）到末尾遍历节拍表。对于每个节拍：

- 如果 `t_end - t_start < MIN_BEAT_DUR`（1.5s），跳过 — 太短，无法进行有意义的缩放。
- 计算关键帧的内部间隔为 `[t_start + HOLD_GAP, t_end - HOLD_GAP]`。如果该间隔短于 1.0s，跳过。
- 否则，预填充该节拍在每节拍映射（称为 `zoom_keyframes_by_beat[beat_idx]`）中的槽位为 `{cx: DEFAULT_CX, cy: DEFAULT_CY, scale: FALLBACK_SCALE (1.25), ramp_s: FALLBACK_RAMP (0.4)}` 加上修剪的 `t_start`/`t_end`。

**步骤 8b — 使用 bbox 导出的精确缩放覆盖，其中 `action_bboxes` 提供了可用的测量。**

对于 `action_bboxes` 中的每个条目：

- **GitHub 模式**：`beat_idx = entry.idx`，因为步骤 6 每个节拍发出一个定时动作。
- **通用 URL 模式**：`beat_idx = entry.idx - prepend_count`，因为步骤 6 前置了等待动作，有时还有 cookie 关闭点击。如果 `beat_idx < 0`，跳过；该条目属于设置，不是编写的节拍。
- 如果 `beat_idx < INTRO_BEATS`，跳过。
- 如果 `entry.found` 为 false，跳过。
- 如果该节拍已经在 `zoom_keyframes_by_beat` 中（在步骤 8a 中由 `MIN_BEAT_DUR`/`1.0s` 规则过滤掉），跳过。
- **过滤退化的 bbox**：如果 `bbox.y > recording_viewport.h`（屏幕外捕获 — 页面没有及时滚动元素进入视图）或 `bbox.h > recording_viewport.h * 1.5`（全页 `<main>` 元素 — 产生无意义的缩放中心），跳过。
- 使用上述录制-px → 帧内-px 转换计算 `cx_framed`/`cy_framed` 从 bbox 中心。覆盖该节拍的槽位为 `{cx: cx_framed, cy: cy_framed, scale: SCALE (1.35), ramp_s: min(0.5, (t_end - t_start) * 0.15)}`。

**最终列表**：按 `t_start` 对 `zoom_keyframes_by_beat` 的值排序，以产生 `zoom_keyframes` 数组。

这保证了每个非引言、足够长的节拍都获得缩放 — 当 bbox 捕获工作时精确，否则为默认位置。避免了“整个运行时间都是平视频”的失败模式。

如果 `len(zoom_keyframes) > 0`，调用 `edit_animate_zoom`，`video_url: framed_url, zoom_keyframes`。返回 `zoomed_url`。否则（没有符合条件的节拍 — 应该很少，因为步骤 3 的 65-80 秒约束）跳过并使用 `framed_url` 作为 `zoomed_url`。

### 步骤 9 — 唇同步完整音频

`generate_lipsync`：

- `provider: <resolved_lipsync_provider>` — **默认：`pika`**（鹦鹉 a2v）。如果明确传递 `--lipsync-provider kling`，则尊重 `kling`。
- `image: <avatar>`
- `audio: <步骤 4 audio_url>`
- **kling 仅限旋钮**：当 `provider == "kling"` 时，添加 `mode: "pro"` 和 `prompt: "talking head, face centered, mouth syncs to audio, minimal head movement, professional presenter"` 以获得更精致的主持人感觉。两者在 `pika` 上都默默地被忽略（鹦鹉有自己的驱动程序）。

**提供者权衡**：

| 提供者 | 墙上时间 | 头部动作 | 何时使用 |
|---|---|---|---|
| **`pika`**（默认） | ~2–5 分钟 | 稍微更戏剧化、自然 | 大多数运行时的默认值 — 快速迭代、可观看输出、比 kling 快 10 倍 |
| `kling`（可选） | ~5–30 分钟 | 最小、面朝中心、主持人风格 | 高风险渲染，其中头像必须像专业的主持人一样阅读；容忍长杆 |

服务器端等待覆盖调用内联；如果响应形状是 `{task_id, status: "queued"}`，在紧密循环中轮询 `task_status`（不睡眠）直到状态达到终止状态（`completed`，`failed` 或 `cancelled`）。在 `completed` 时，捕获 `lipsync_url`。在 `failed` / `cancelled` 时，回退到 **另一个** 提供者（kling ↔ pika），如下面的故障转移说明所示。

**故障转移**：
- 如果 `pika` 失败（很少见 — 鹦鹉 a2v 在典型的解释音频长度上很稳健）→ 一次重试 `provider: "kling"`。
- 如果 `kling` 超过工作器的 1200 秒上限而停滞（作为重复的 `processing` 状态且没有完成）→ 回退到 `provider: "pika"`。步骤 4.5 的音频长度门控应该在该到达这里之前捕获长音频的情况，但故障转移处理了残余风险。

**为什么 pika 是默认值**：
- 速度 — 典型的解释性墙上时间从 ~10–15 分钟降至 ~5–7 分钟总时间，因为唇同步是长杆。
- 质量足够好 — 鹦鹉 a2v 是自然主义的；轻微的额外头部动作在 60-80 秒的视频中读作投入而不是分散注意力。
- Kling-mode-pro 精致主要在 246 像素的圆圈内部是不可见的 — 面部区域太小，无法在大多数观众中察觉到最小头部动作的差异。

为了获得参考输出的典型“专业主持人”感觉，显式传递 `--lipsync-provider kling`。

**面部连贯性门控**（在 PiP 合成之前强制执行）：

捕获 `lipsync_url` 后，在步骤 10 之前对原始唇同步视频进行采样。调用 `extract_frame(video_url=<lipsync_url>, at_times=[1.0, audio_duration_seconds * 0.5, max(1.0, audio_duration_seconds - 1.0)])` 以获取开始/中间/结束帧。在批量模式下，捕获 `frame_urls = extract_result.urls` 并忽略 `url` 字段，除非 `urls` 缺失时作为后备使用。因为 `analyze_media.media` 接受单个 URL 字符串，对每个帧 URL 进行一次 `analyze_media` 调用；不要传递数组。

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

在继续之前汇总帧裁决。只有当所有采样帧中的最低/最差 `face_integrity_score` 大于等于 `75`，每个 `is_coherent_human_face == true`，每个 `has_visible_mouth == true`，并且每个 `is_abstract_melting_mask_or_non_human == false` 时才通过。保留每个帧的观察结果，以便中止消息可以命名是开始、中间还是结束帧失败。

如果门控在第一个提供者上失败，使用另一个提供者（pika ↔ kling）并使用相同的头像和音频，然后再次运行这个面部连贯性门控。如果两个提供者都失败，中止并返回清晰的错误，并返回门控观察结果；**不要**继续到步骤 10 与损坏的主持人。如果第二个提供者通过，则使用该提供者的 `lipsync_url` 下游。

从应用 `proper_noun_glossary` 规范拼写后，将最终合并的 `vo_text` 构建 `caption_script_text`。不要依赖自动转录来解释说明中的品牌/型号名称：即使浏览器框架显示正确文本，自动转录也可能在发音上错误地拼写可见的专有名词。

在调用工具之前选择字幕位置：
- 默认 `position: "bottom"` (`caption_position = "bottom"`) 用于普通解释说明页面。
- 当当前节拍计划或捕获页面在经典底部条会覆盖的位置显示重要英雄文本、标题、价值主张、CTA 或代码时，使用 `position: "top"` (`caption_position = "top"`)。

调用 `add_captions(video_url=<final_url>, style="classic", caption_mode: "manual", subtitle_text: <caption_script_text>, position: <caption_position>)`。手动模式将修正的旁白文本分布在检测到的持续时间上，并防止专有名词漂移。将结果捕获为 `captioned_url`。

仅当用户传递了 `--no-captions`（在步骤 1 中解析）时才跳过此步骤——默认情况下开启字幕。（注意：`/pika:podcast` 不会烧录字幕——解释说明中的旁白比快速双主持人对话更适合转录。）

### 步骤 12 — 返回

如果步骤 6 中设置了 `bbox_warning`，则在最终 URL 前立即发出它，以便用户知道在某些节拍上视觉降级为中心帧缩放。然后发出 `captioned_url`（如果步骤 11 被跳过，则为 `final_url`）在一行中：`Done: <url>`。

## 飞行后质量门

在声明成功之前，对 `captioned_url` 或 `final_url` 调用 `analyze_media` 并请求结构化判断：

```
仅返回 JSON：{
  "verdict": "clean" | "degraded" | "catastrophic",
  "observations": string[],
  "quality_warning": string | null,
  "re_roll_suggestion": string | null
}
检查字幕是否存在，除非使用了 `--no-captions`，缩放目标 / bbox 聚焦落在旁白的 UI 元素上，没有空白帧或白色闪烁问题，以及头像 PiP 不会覆盖重要页面内容。
还验证主持人的面部保持连贯（不是抽象的、融化的、无面的、戴面具的或非人类的），`proper_noun_glossary` 中的专有名词在字幕中拼写正确，并且字幕不会遮挡或覆盖旁白所指的英雄文本、标题、价值主张副本、CTA 或代码。
```

- 如果 `verdict` 是 `clean`，正常发出最终 URL。
- 如果 `verdict` 是 `degraded`，发出最终 URL 加上 `quality_warning`，以便用户在发布前可以查看。
- 如果 `verdict` 是 `catastrophic`，不要将解释说明标记为完成；而是显示判断和 `re_roll_suggestion` 而不是声明成功。

## 失败模式

| 症状 | 可能原因 | 恢复 |
|---|---|---|
| OAuth / 401 在第一次 MCP 调用时 | 用户的 Pika 连接器令牌丢失或过期 | 停止并告诉用户重新验证 Pika MCP 连接器；在认证成功之前不要重试付费步骤。 |
| `capture_website` 返回空白帧、空的 `action_bboxes` 或被阻止的页面 | 目标 URL 受限制、被机器人检测到、被 cookie 覆盖或渲染后 | 使用 WebFetch 文本备用方案进行事实依据，如果不足够，则请求粘贴的源材料或更简单的 URL。 |
| TTS 或唇同步提供程序返回临时的 5xx / 429 | 提供程序队列或速率限制 | 在提示的回退后重试完全相同的调用一次；如果它再次失败，停止并提供程序错误和最后一个完成的检查点。 |
| 字幕或最终 QA 报告中不可读的专有名词、遮挡、空白帧或不一致的头像 | 生成的媒体未准备好发布 | 返回 `not publish-ready` 并附带 QA JSON 和具体的重录建议；不要使用灾难性判断声明成功。 |

## 承重短语

这些锚点跨页面类型保留视觉契约：

| 短语 | 位置 | 为什么承重 |
|---|---|---|
| `vanilla CSS that resolves via document.querySelector` | 选择器契约 | 保持滚动、bbox 捕获和缩放目标在 `capture_website` 内对齐。 |
| `GitHub URLs activate repo-aware mode` | 模式检测 | 防止通用产品页面节拍替换 README/代码演示节拍。 |
| `8-10 beats`, `65-80 seconds`, `165-200 words` | 节拍表编写 | 保持旁白、屏幕录制、唇同步和字幕在可靠持续时间信封内。 |
| `all beats[] mutations happen here` | 音频重缩放步骤 | 确保后续捕获/缩放/合成步骤消耗一个稳定的时序线。 |
| `extra_css` cookie-banner 隐藏有效负载 | 通用 URL 预飞行 | 当点击横幅失败时减少第一帧横幅遮挡。 |

## 引擎选择：Pika 唇同步默认，Kling 选择加入

默认使用 Pika/parrot 唇同步，因为它更快，并将大多数解释说明保持在较短的迭代循环中。仅在用户明确请求 `--lipsync-provider kling` 或当高风险渲染需要一个更居中的主持人外观并且可以忍受更长的长杆阶段时使用 Kling。

屏幕捕获、浏览器框架、缩放、PiP 和字幕围绕这个唇同步选择保持确定性编辑/合成步骤。

## 运行时预期

典型运行时间 Pika 唇同步为 5-10 分钟，Kling 唇同步为 10-30+ 分钟：

| 步骤 | 运行时间 | 备注 |
|---|---:|---|
| URL 读取 + 预飞行 | 10-60s | GitHub README 扫描或通用 URL DOM/cookie 检查 |
| TTS + 音频重缩放 | 30-90s | 节拍时间在实际音频长度后标准化 |
| 屏幕录制 | 60-180s | 取决于页面加载和导航次数 |
| 浏览器框架 + 缩放 | 1-3 min | 确定性编辑/合成阶段 |
| 唇同步 | 2-5 min Pika / 5-30 min Kling | Kling 是选择加入的，因为它是最长的杆 |
| PiP + 字幕 | 1-3 min | 当设置了 `--no-captions` 时跳过字幕 |

## 已知的差距（作为后续服务器端工作携带）

- **Kling 头像模式和提示可用。** 要启用专业主持人模式，传递 `--lipsync-provider kling` 并且步骤 9 的调用应添加 `mode: "pro"` 加上类似 `"talking head, face centered, mouth syncs to audio, minimal head movement, professional presenter"` 的提示。这是减少唇同步中戏剧性头部运动的品质杠杆。
- **没有调用者控制的屏幕录制白色帧修剪。** `capture_website` 有内部修剪启发式算法，但不会将其暴露给调用者。在解释说明开始时可见为短暂的白色闪烁，此时页面仍在加载。800ms 的 `wait` 动作在 `at_s: 0.0` 处缓解了这种情况，通过给页面时间来绘制，但不会修剪已录制的白色帧。工作线程增强。
- **没有在每节拍导航上等待 `networkidle`。** `capture_website` 结算到 `domcontentloaded` 加上 bbox 捕获分支的 600 ms 后动作结算（服务器端，当 `bbox_selector` 设置时），但最终渲染发生在 `domcontentloaded` 后的 SPA 碎片页面仍然可能被 bbox 对抗未挂载的代码块。工作线程增强：在 `timed_actions[].navigate` 上暴露一个 `wait_until` 钩子。
- **没有每步输出大小验证门。** 一个稳健的文件大小检查将验证 TTS ≥ 50KB、预览 ≥ 100KB、屏幕 ≥ 200KB、唇同步 ≥ 500KB，以及最终 ≥ 1MB 在每步之后。MCP 路径仅返回 URL；验证文件大小需要每步一个额外的 `analyze_media` 调用（每步 ~30s 开销）。一旦用户端延迟预算允许，值得添加。目前，下游失败级联（例如零字节的 TTS → 沉默的唇同步 → 空白合成）仅在步骤 11 处显示。
- **`text_content` bbox 捕获未实现。** `capture_website` v1 仅对具有 CSS `selector` 的步骤返回 `action_bboxes`。`text_content` 仅步骤不产生条目。在 `zoom_target` 中优先使用 CSS 选择器以确保缩放覆盖。
- **节拍表措辞是非确定性的。** 运行相同的输入两次会产生不同的 vo_text 和不同的缩放位置。视觉 *种类* 是契约，而不是像素精确的再现。
- **通用 URL 模式质量因网站而异。** 现代 indie / SaaS 登录页面具有语义标记（`<h1>` + 清晰的 `<section>` + 命名类钩子）工作良好。大品牌企业网站（apple.com、microsoft.com、amazon.com）遇到几个已知限制：(a) **机器人检测** — 页面可能在无头 Chrome 下提供降级版本，或 captcha；步骤 2.6 §A 在这些情况下中止，但启发式算法不是详尽的；(b) **混淆的类名** — `tile-headline` 而不是 `hero-title` 击败了通用选择器；步骤 2.6 §C 的 WebFetch DOM 扫描有所帮助，但并不完美；(c) **滚动触发的动画不播放** — IntersectionObserver 驱动的英雄揭示在真实用户滚动时触发，而不是 Playwright 的 `scrollIntoView`；记录的帧可能是一个静态占位符；(d) **懒加载图像** — `loading="lazy"` 的 picture/source 元素可能在 600ms 或 2500ms 结算窗口内未解析；bbox 落在透明占位符上。解决方案：优先选择更简单/更小的营销页面进行启动演示，始终传递 `--focus "the X feature"` 来锚定节拍选择，接受大品牌网站需要后续服务器 PR（cookie 横幅点击重试 + `wait_until=networkidle` + 通过 `IntersectionObserver` polyfill 触发动画）。
- **Cookie 横幅点击是单次尝试。** 步骤 2.6 §B 对从 WebFetch DOM 提取的取消选择器发出一次 `click`。如果 WebFetch 的 HTML 不包含横幅（渲染后 JS）或选择器错误，点击会无声地错过——`extra_css` 有效负载是承重防御。工作线程增强：支持每个 `click` 动作的一个后备选择器列表，以便工作线程按顺序尝试每个。
