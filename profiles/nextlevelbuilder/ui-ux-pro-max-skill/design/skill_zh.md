# 设计

统一设计技能：品牌、设计令牌、UI、标志、企业识别计划（CIP）、幻灯片、横幅、社交媒体照片、图标。

## 使用场景

- 品牌身份、声音、资产
- 设计系统令牌和规范
- 使用 shadcn/ui + Tailwind 进行 UI 样式设计
- 标志设计和 AI 生成
- 企业识别计划（CIP）交付物
- 演示文稿和提案演示文稿
- 社交媒体、广告、网络、印刷的横幅设计
- 社交媒体照片（Instagram、Facebook、LinkedIn、Twitter、Pinterest、TikTok）

## 子技能路由

| 任务 | 子技能 | 详情 |
|------|-----------|---------|
| 品牌身份、声音、资产 | `brand` | 捆绑的兄弟技能 |
| 令牌、规范、CSS 变量 | `design-system` | 捆绑的兄弟技能 |
| shadcn/ui、Tailwind、代码 | `ui-styling` | 捆绑的兄弟技能 |
| 标志创建、AI 生成 | Logo（内置） | `references/logo-design.md` |
| CIP 模板、交付物 | CIP（内置） | `references/cip-design.md` |
| 演示文稿、提案演示文稿 | Slides（内置） | `references/slides.md` |
| 横幅、封面、页眉 | Banner（内置） | `references/banner-sizes-and-styles.md` |
| 社交媒体图像/照片 | Social Photos（内置） | `references/social-photos-design.md` |
| SVG 图标、图标集 | Icon（内置） | `references/icon-design.md` |

## 脚本路径

此技能及其 `references/` 中的脚本路径相对于包含此 SKILL.md 的目录，而不是相对于项目：`scripts/<file>` 是此技能自己的 `scripts/` 文件夹，而 `../<skill>/scripts/<file>` 是与它一起安装的兄弟子技能。从该目录（Claude Code 在技能加载时报告它为技能的基本目录）构建完整路径，并将工作目录保持在项目根目录——脚本相对于它读取和写入项目文件，例如 `docs/brand-guidelines.md`、`assets/design-tokens.json` 或 `src/`。

## 标志设计（内置）

55+ 风格，30 种调色板，25 种行业指南。Gemini Nano Banana、Atlas Cloud 和 MuAPI 图像生成。

### 标志：生成设计简报

```bash
python3 scripts/logo/search.py "tech startup modern" --design-brief -p "BrandName"
```

### 标志：搜索风格/颜色/行业

```bash
python3 scripts/logo/search.py "minimalist clean" --domain style
python3 scripts/logo/search.py "tech professional" --domain color
python3 scripts/logo/search.py "healthcare medical" --domain industry
```

### 标志：使用 AI 生成

**始终**使用白色背景生成输出标志图像。

```bash
python3 scripts/logo/generate.py --brand "TechFlow" --style minimalist --industry tech
python3 scripts/logo/generate.py --prompt "coffee shop vintage badge" --style vintage
python3 scripts/logo/generate.py --brand "TechFlow" --provider atlas
python3 scripts/logo/generate.py --brand "TechFlow" --provider muapi
python3 scripts/logo/generate.py --brand "TechFlow" --provider muapi --muapi-model nano-banana-pro
```

**重要提示：**当脚本失败时，直接尝试修复它们。

生成后，**始终**通过 `AskUserQuestion` 询问用户关于 HTML 预览。如果同意，请使用捆绑的 `ui-ux-pro-max` 技能进行画廊。

## CIP 设计（内置）

50+ 交付物，20 种风格，20 个行业。Gemini Nano Banana（Flash/Pro）。

### CIP：生成简报

```bash
python3 scripts/cip/search.py "tech startup" --cip-brief -b "BrandName"
```

### CIP：搜索域

```bash
python3 scripts/cip/search.py "business card letterhead" --domain deliverable
python3 scripts/cip/search.py "luxury premium elegant" --domain style
python3 scripts/cip/search.py "hospitality hotel" --domain industry
python3 scripts/cip/search.py "office reception" --domain mockup
```

### CIP：生成模板

```bash
# 带有标志（推荐）
python3 scripts/cip/generate.py --brand "TopGroup" --logo /path/to/logo.png --deliverable "business card" --industry "consulting"

# 完整 CIP 集合
python3 scripts/cip/generate.py --brand "TopGroup" --logo /path/to/logo.png --industry "consulting" --set

# Pro 模型（4K 文本）
python3 scripts/cip/generate.py --brand "TopGroup" --logo logo.png --deliverable "business card" --model pro

# 无标志
python3 scripts/cip/generate.py --brand "TechFlow" --deliverable "business card" --no-logo-prompt
```

模型：`flash`（默认，`gemini-2.5-flash-image`），`pro`（`gemini-3-pro-image-preview`）

### CIP：渲染 HTML 演示文稿

```bash
python3 scripts/cip/render-html.py --brand "TopGroup" --industry "consulting" --images /path/to/cip-output
```

**提示：**如果不存在标志，请首先使用上面的标志设计部分。

## 幻灯片（内置）

使用 Chart.js、设计令牌和文案公式制作战略 HTML 演示文稿。

加载 `references/slides-create.md` 以获取创建工作流。

### 幻灯片：知识库

| 主题 | 文件 |
|-------|------|
| 创建指南 | `references/slides-create.md` |
| 布局模式 | `references/slides-layout-patterns.md` |
| HTML 模板 | `references/slides-html-template.md` |
| 文案 | `references/slides-copywriting-formulas.md` |
| 策略 | `references/slides-strategies.md` |

## 横幅设计（内置）

跨越社交媒体、广告、网络、印刷的 22 种艺术方向风格。此工作流不需要捆绑包之外的内容：`references/banner-sizes-and-styles.md` 和捆绑的 `ui-ux-pro-max` 技能用于风格和调色板指导。浏览器研究、图像生成和屏幕截图捕获是可选的运行时功能；当不可用时，请使用提供的资源、CSS 构建的视觉效果以及运行时的标准预览或捕获工作流。

加载 `references/banner-sizes-and-styles.md` 以获取完整的尺寸和风格参考。

### 横幅：工作流

1. **收集需求**通过 `AskUserQuestion`——目的、平台、内容、品牌、风格、数量
2. **研究**——阅读 `references/banner-sizes-and-styles.md` 并使用捆绑的 `ui-ux-pro-max` 技能进行风格和调色板指导；如果浏览器研究可用且允许，则收集 3–5 个参考
3. **设计**——在精确的平台尺寸创建 HTML/CSS 横幅；使用提供的资源或 CSS 构建的视觉效果，或如果运行时提供授权的图像生成功能
4. **导出**——使用运行时的浏览器或屏幕截图功能以精确尺寸捕获 PNG；如果不可用，请提供 HTML/CSS 源代码并标记 PNG 导出为待定
5. **展示**——并排显示所有选项，根据反馈进行迭代

### 横幅：快速尺寸参考

| 平台 | 类型 | 尺寸（px） |
|----------|------|-----------|
| Facebook | 封面 | 820 x 312 |
| Twitter/X | 页眉 | 1500 x 500 |
| LinkedIn | 个人 | 1584 x 396 |
| YouTube | 频道艺术 | 2560 x 1440 |
| Instagram | 故事 | 1080 x 1920 |
| Instagram | 发布 | 1080 x 1080 |
| Google Ads | 中等矩形 | 300 x 250 |
| 网站 | 英雄 | 1920 x 600-1080 |

### 横幅：顶级艺术风格

| 风格 | 适合 |
|-------|----------|
| 极简主义 | SaaS、科技 |
| 粗体排版 | 宣布 |
| 渐变 | 现代品牌 |
| 照片 | 生活方式、电商 |
| 几何图形 | 科技、金融科技 |
| 玻璃态 | SaaS、应用 |
| 霓虹/赛博朋克 | 游戏、活动 |

### 横幅：设计规则

- 安全区域：关键内容在中央 70-80%
- 每个横幅一个 CTA，右下角，最小 44px 高度
- 最大 2 种字体，正文最小 16px，标题 ≥32px
- 广告文本少于 20%（Meta 处罚）
- 印刷：300 DPI、CMYK、3-5mm 印刷出血

## 图标设计（内置）

15 种风格，12 个类别。Gemini 3.1 Pro Preview 生成 SVG 文本输出。

### 图标：生成单个图标

```bash
python3 scripts/icon/generate.py --prompt "settings gear" --style outlined
python3 scripts/icon/generate.py --prompt "shopping cart" --style filled --color "#6366F1"
python3 scripts/icon/generate.py --name "dashboard" --category navigation --style duotone
```

### 图标：生成批量变化

```bash
python3 scripts/icon/generate.py --prompt "cloud upload" --batch 4 --output-dir ./icons
```

### 图标：多尺寸导出

```bash
python3 scripts/icon/generate.py --prompt "user profile" --sizes "16,24,32,48" --output-dir ./icons
```

### 图标：顶级风格

| 风格 | 适合 |
|-------|----------|
| outlined | UI 接口、Web 应用 |
| filled | 移动应用、导航栏 |
| duotone | 营销、着陆页 |
| rounded | 友好应用、健康 |
| sharp | 科技、金融科技、企业 |
| flat | 材料设计、Google 风格 |
| gradient | 现代品牌、SaaS |

**模型：** `gemini-3.1-pro-preview`——文本输出（SVG 是 XML 文本）。不需要图像生成 API。

## 社交媒体照片（内置）

跨平台社交媒体图像设计：HTML/CSS → 屏幕截图导出。使用捆绑的 `ui-ux-pro-max`、`brand` 和 `design-system` 技能；屏幕截图导出通过 Chrome 无头模式、Playwright 或 Puppeteer 运行（见参考）。

加载 `references/social-photos-design.md` 以获取尺寸、模板、最佳实践。

### 社交媒体照片：工作流

1. **编排**——使用运行时的本地任务列表跟踪以下步骤；并行子代理用于独立工作
2. **分析**——解析提示：主题、平台、风格、品牌上下文、内容元素
3. **构思**——3-5 个概念，通过 `AskUserQuestion` 呈现
4. **设计**——捆绑的 `brand` → `design-system` → `ui-ux-pro-max` 技能；每个想法 × 尺寸的 HTML
5. **导出**——Chrome 无头模式、Playwright 或 Puppeteer 精确 px 屏幕截图（在工具支持的情况下为设备缩放因子的 2 倍；见参考）
6. **验证**——在可用浏览器或图像查看器中打开导出的 PNG 并检查；修复布局/样式问题并重新导出
7. **报告**——设计决策摘要到 `plans/reports/`
8. **组织**——将输出文件和报告分类到项目的资源目录

### 社交媒体照片：关键尺寸

| 平台 | 尺寸（px） | 平台 | 尺寸（px） |
|----------|-----------|----------|-----------|
| IG Post | 1080×1080 | FB Post | 1200×630 |
| IG Story | 1080×1920 | X Post | 1200×675 |
| IG Carousel | 1080×1350 | LinkedIn | 1200×627 |
| YT Thumb | 1280×720 | Pinterest | 1000×1500 |

## 工作流

### 完整品牌包

1. **标志** → `scripts/logo/generate.py` → 生成标志变体
2. **CIP** → `scripts/cip/generate.py --logo ...` → 创建可交付模板
3. **演示文稿** → 加载 `references/slides-create.md` → 构建提案演示文稿

### 新设计系统

1. **品牌**（品牌技能）→ 定义颜色、排版、声音
2. **令牌**（设计系统技能）→ 创建语义令牌层
3. **实现**（ui-styling 技能）→ 配置 Tailwind、shadcn/ui

## 参考

| 主题 | 文件 |
|-------|------|
| 设计路由 | `references/design-routing.md` |
| 标志设计指南 | `references/logo-design.md` |
| 标志风格 | `references/logo-style-guide.md` |
| 标志颜色 | `references/logo-color-psychology.md` |
| 标志提示 | `references/logo-prompt-engineering.md` |
| CIP 设计指南 | `references/cip-design.md` |
| CIP 可交付物 | `references/cip-deliverable-guide.md` |
| CIP 风格 | `references/cip-style-guide.md` |
| CIP 提示 | `references/cip-prompt-engineering.md` |
| 幻灯片创建 | `references/slides-create.md` |
| 幻灯片布局 | `references/slides-layout-patterns.md` |
| 幻灯片模板 | `references/slides-html-template.md` |
| 幻灯片文案 | `references/slides-copywriting-formulas.md` |
| 幻灯片策略 | `references/slides-strategies.md` |
| 横幅尺寸和风格 | `references/banner-sizes-and-styles.md` |
| 社交媒体照片指南 | `references/social-photos-design.md` |
| 图标设计指南 | `references/icon-design.md` |

## 脚本

| 脚本 | 目的 |
|--------|---------|
| `scripts/logo/search.py` | 搜索标志风格、颜色、行业 |
| `scripts/logo/generate.py` | 使用 Gemini AI 生成标志 |
| `scripts/logo/core.py` | Logo 数据的 BM25 搜索引擎 |
| `scripts/cip/search.py` | 搜索 CIP 可交付物、风格、行业 |
| `scripts/cip/generate.py` | 使用 Gemini 生成 CIP 模板 |
| `scripts/cip/render-html.py` | 从 CIP 模板渲染 HTML 演示文稿 |
| `scripts/cip/core.py` | CIP 数据的 BM25 搜索引擎 |
| `scripts/icon/generate.py` | 使用 Gemini 3.1 Pro 生成 SVG 图标 |

## 前置条件

**Python：**此技能使用 Python 脚本。在 Windows 上，使用 `python` 而不是 `python3`（例如，`python scripts/logo/search.py` 而不是 `python3 scripts/logo/search.py`）。

检查是否安装了 Python：
```bash
python3 --version || python --version
```

## 设置

```bash
export GEMINI_API_KEY="your-key"  # https://aistudio.google.com/apikey
pip install google-genai pillow

# 可选 MuAPI 提供商（不需要额外的 Python 包）
export MUAPI_API_KEY="your-key"
```

MuAPI 使用异步模型端点和预测结果 API。有关认证，请参阅
[MuAPI API 参考](https://muapi.ai/docs/api-reference)，有关当前模型特定模式，请参阅
[ nano-banana 模型合同](https://api.muapi.ai/api/v1/models/nano-banana)
或
[ nano-banana-pro 模型合同](https://api.muapi.ai/api/v1/models/nano-banana-pro)
。标志生成器支持这两个文档化的模型别名，并发送它们共享的必需 `prompt` 字段和可选的 `aspect_ratio` 字段；Pro 模型还接受可选的 `resolution` 字段，此专注的标志工作流将其保留为提供者默认值。

> **Windows 注意：**在需要时使用 `python` 而不是 `pip`（例如，`python -m pip install ...`）。

## 集成

**捆绑子技能：** brand、design-system、ui-styling
**相关技能：** ui-ux-pro-max
