---
name: html-ppt
description: HTML PPT Studio — 用于创建专业静态 HTML 演示文稿，支持多种风格、布局和动画效果，所有功能均基于模板驱动。当用户需要演示文稿、PPT、幻灯片、演讲稿、演示文稿、幻灯片、演讲稿、制作一份 PPT、制作一份幻灯片、小红书图文或任何需要美观且支持键盘导航的多页提案/报告/分享文档时，均可使用。触发关键词包括“演示文稿”、“PPT”、“幻灯片”、“演示文稿”、“演讲稿”、“分享稿”、“小红书图文”、“演讲幻灯片”、“提案演示文稿”、“技术分享”、“技术演示”。
---

# html-ppt — HTML PPT Studio

专业作者 HTML 演示文稿为静态文件。一个主题文件 = 一种外观。一个布局文件 = 一种页面类型。一个动画类 = 一种进入效果。所有页面共享基于 token 的设计系统在 `assets/base.css` 中。

## 安装

```bash
npx skills add https://github.com/lewislulu/html-ppt-skill
```

一条命令，无需构建。纯静态 HTML/CSS/JS，仅使用 CDN webfonts。

目标机器无网络？将 CLI 指向本地副本 (`npx skills add ./html-ppt-skill`)，或直接将此文件夹复制到代理的技能目录 — `~/.claude/skills/html-ppt/` 为 Claude Code。幻灯片离线渲染；仅 webfonts 回退到系统堆栈。参见 [README.md](README.md#offline--manual-install)。

## 技能提供什么

- **36 个主题** (`assets/themes/*.css`) — minimal-white, editorial-serif, soft-pastel, sharp-mono, arctic-cool, sunset-warm, catppuccin-latte/mocha, dracula, tokyo-night, nord, solarized-light, gruvbox-dark, rose-pine, neo-brutalism, glassmorphism, bauhaus, swiss-grid, terminal-green, xiaohongshu-white, rainbow-gradient, aurora, blueprint, memphis-pop, cyberpunk-neon, y2k-chrome, retro-tv, japanese-minimal, vaporwave, midcentury, corporate-clean, academic-paper, news-broadcast, pitch-deck-vc, magazine-bold, engineering-whiteprint
- **15 个完整幻灯片模板** (`templates/full-decks/<name>/`) — 完整的多幻灯片演示文稿，具有作用域的 `.tpl-<name>` CSS。8 个从真实世界的演示文稿中提取 (xhs-white-editorial, graphify-dark-graph, knowledge-arch-blueprint, hermes-cyber-terminal, obsidian-claude-gradient, testing-safety-alert, xhs-pastel-card, dir-key-nav-minimal)，7 个场景脚手架 (pitch-deck, product-launch, tech-sharing, weekly-report, xhs-post 3:4, course-module, **presenter-mode-reveal** — 演讲者模式专用)
- **36 个布局** (`templates/single-page/*.html`) 带有逼真的演示数据，包括 **5 个真实图像布局** (single / full-bleed / image+text / gallery / before-after)
- **27 个 CSS 动画** (`assets/animations/animations.css`) 通过 `data-anim`
- **20 个 canvas FX 动画** (`assets/animations/fx/*.js`) 通过 `data-fx` — particle-burst, confetti-cannon, firework, starfield, matrix-rain, knowledge-graph (force-directed), neural-net (pulses), constellation, orbit-ring, galaxy-swirl, word-cascade, letter-explode, chain-react, magnetic-field, data-stream, gradient-blob, sparkle-trail, shockwave, typewriter-multi, counter-explosion
- **键盘运行时** (`assets/runtime.js`) — 箭头键、T (主题)、A (动画)、F/O, **S (演讲者模式: 带有 CURRENT / NEXT / SCRIPT / TIMER 卡片的磁性卡片弹出)**, N (笔记抽屉), R (在演讲者中重置计时器)
- **触摸导航** — 在手机和平板电脑上左右滑动以切换幻灯片
- **FX 运行时** (`assets/animations/fx-runtime.js`) — 在幻灯片进入时自动初始化 `[data-fx]`，在离开时清理
- **主题 / 布局 / 动画 / 完整幻灯片画廊的展示幻灯片**
- **用于 PNG 导出的无头 Chrome 渲染脚本**

## 何时使用

当用户要求任何基于幻灯片的输出或将文本/笔记转换为可演示的演示文稿时使用。优先选择此方案而不是从头开始构建。

### 🎤 演讲者模式 (演讲者模式 + 逐字稿)

如果用户提到任何：**演讲 / 分享 / 讲稿 / 逐字稿 / speaker notes / presenter view / 演讲者视图 / 提词器**，或说类似“我要去给团队讲 xxx”、“要做一场技术分享”、“怕讲不流畅”、“想要一份带逐字稿的 PPT” — **使用 `presenter-mode-reveal` 完整幻灯片模板**，并在每个幻灯片的 `<aside class="notes">` 中编写 150–300 字的逐字稿。

参见 [references/presenter-mode.md](references/presenter-mode.md) 了解完整的创作指南，包括演讲脚本写作的 3 条规则：
1. **不是讲稿，是提示信号** — 加粗核心词 + 过渡句独立成段
2. **每页 150–300 字** — 2–3 分钟/页的节奏
3. **用口语，不用书面语** — "因此"→"所以"，"该方案"→"这个方案"

所有完整幻灯片模板都支持 S 键演讲者模式（它已构建在 `runtime.js` 中）。**S 打开一个带有 4 张磁性卡片的新弹出窗口**：
- 🔵 **CURRENT** — 当前幻灯片的像素级 iframe 预览
- 🟣 **NEXT** — 下一张幻灯片的像素级 iframe 预览
- 🟠 **SPEAKER SCRIPT** — 大字体逐字稿 (可滚动)
- 🟢 **TIMER** — 已用时间 + 幻灯片计数器 + 上一页/下一页/重置按钮

每张卡片都可以通过其标题**拖动**，并通过右下角的手柄**调整大小**。卡片的布局/大小会持久化到每个演示文稿的 `localStorage`。一个“重置布局”按钮会恢复默认排列。

**为什么预览是像素级精确的**：每个预览都是一个 `<iframe>`，它加载实际的演示文稿 HTML，带有 `?preview=N` 查询参数；`runtime.js` 检测到此并仅渲染第 N 张幻灯片，没有 Chrome。因此预览使用与观众视图**相同的 CSS、主题、字体和视口** — 颜色和布局保证完全相同。

**平滑导航**：在幻灯片切换时，演讲者窗口向每个 iframe 发送 `postMessage({type:'preview-goto', idx:N})`。iframe 仅在幻灯片之间切换 `.is-active` — **不重新加载，不闪烁**。两个窗口也通过 `BroadcastChannel` 保持同步。

只有 `presenter-mode-reveal` 是从底层设计围绕此功能，并在每张幻灯片上都有适当的示例逐字稿。

演讲者窗口中的键盘：`← →` 导航 (同步观众) · `R` 重置计时器 · `Esc` 关闭弹出窗口。
观众窗口中的键盘：`S` 打开演讲者 · `T` 循环主题 · `← →` 导航 (同步演讲者) · `F` 全屏 · `O` 概览。

## 在您创作任何内容之前 — 始终询问或建议

**在您理解三件事之前不要开始编写幻灯片。** 直接询问用户，或者 — 如果他们已经交给您丰富的内容 — 提出优雅的默认值并确认。

1. **内容 & 观众。** 演示文稿是关于什么的，有多少张幻灯片，谁在观看 (工程师 / 高管 / 小红书读者 / 学生 / VC)?
2. **风格 / 主题。** 哪个 36 个主题适合？如果不确定，根据语气推荐 2-3 个候选者：
   - 商业 / 投资者提案 → `pitch-deck-vc`, `corporate-clean`, `swiss-grid`
   - 技术分享 / 工程 → `tokyo-night`, `dracula`, `catppuccin-mocha`, `terminal-green`, `blueprint`
   - 小红书图文 → `xiaohongshu-white`, `soft-pastel`, `rainbow-gradient`, `magazine-bold`
   - 学术 / 报告 → `academic-paper`, `editorial-serif`, `minimal-white`
   - 尖端 / 网络 / 发布 → `cyberpunk-neon`, `vaporwave`, `y2k-chrome`, `neo-brutalism`
3. **起点。** 15 个完整幻灯片模板之一，或空白？指向最接近的 `templates/full-decks/<name>/` 并询问是否合适。如果用户的內容暗示了明显的事情 (例如，“我要做产品发布会” → `product-launch`)，自信地建议它，而不是盲目地询问。

一个好的开场信息看起来像：

> 我可以给你做这份 PPT！先确认三件事：
> 1. 大致内容 / 页数 / 观众是谁？
> 2. 风格偏好？我建议从这 3 个主题里选一个：`tokyo-night`（技术分享默认好看）、`xiaohongshu-white`（小红书风）、`corporate-clean`（正式汇报）。
> 3. 要不要用我现成的 `tech-sharing` 全 deck 模板打底？

只有当这些明确后，才能搭建演示文稿并开始编写。

## 快速入门

1. **搭建新的演示文稿。** 从仓库根目录：
   ```bash
   ./scripts/new-deck.sh my-talk
   open examples/my-talk/index.html
   ```
2. **选择一个主题。** 打开演示文稿并按 `T` 循环。或者硬编码它 (`../assets/` 这里是一个占位符 — 使用文件其余部分已经使用的任何前缀；`new-deck.sh` 已将其设置为正确的深度):
   ```html
   <link rel="stylesheet" id="theme-link" href="../assets/themes/aurora.css">
   ```
   目录在 [references/themes.md](references/themes.md)。
3. **选择布局。** 将 `<section class="slide">...</section>` 块从 `templates/single-page/` 中的文件复制到您的演示文稿中。替换演示数据。
   目录在 [references/layouts.md](references/layouts.md)。
4. **添加动画。** 将 `data-anim="fade-up"` (或 `class="anim-fade-up"`) 放在任何元素上。在 `<ul>`/网格上，使用 `anim-stagger-list` 进行序列化显示。对于 canvas FX，使用 `<div data-fx="knowledge-graph">...</div>` 并包含 `<script src="../assets/animations/fx-runtime.js"></script>`。
   目录在 [references/animations.md](references/animations.md)。
5. **使用一个完整幻灯片模板。** 从它开始搭建，不要手动复制它 — 模板的 `../../../assets/` 是相对于 *它自己的* 位置，所以手动复制会导致路径深度错误：
   ```bash
   ./scripts/new-deck.sh my-talk -t pitch-deck
   ```
   每个文件夹都是自包含的，具有作用域的 CSS。目录在 [references/full-decks.md](references/full-decks.md) 和 `templates/full-decks-index.html` 中的画廊。
6. **渲染为 PNG。**
   ```bash
   ./scripts/render.sh templates/theme-showcase.html       # 一次性
   ./scripts/render.sh examples/my-talk/index.html 12      # 12 张幻灯片
   ```

## 创作规则 (重要)

- **始终从一个模板开始。** 不要从头开始创作幻灯片 — 首先从 `templates/single-page/` 复制最接近的布局，然后替换内容。
- **使用 token，而不是直接颜色。** 每个颜色、半径、阴影都应来自 `assets/base.css` 中定义的 CSS 变量，并由主题覆盖。好：`color: var(--text-1)`。坏：`color: #111`。
  顶部覆盖 `--accent` 填充的文本是人们经常出错的地方：它需要 `color: var(--accent-ink)`，因为这里的强调色从 `#ffffff` 到 `#000000`，没有直接墨水在所有它们上都是可读的。
- **不要发明新的布局文件。** 优先组合现有的。只有当 36 个都不合适时，才添加一个新的 `templates/single-page/*.html`。
- **在幻灯片上放置图像？** 从五个 `image-*` 布局之一开始，并使用 `.img-frame` — 参见 *图像* 下面的内容。永远不要将裸的 `<img>` 放入幻灯片中：未框定的图像会忽略幻灯片的高度，并将其余部分推离页面。
- **尊重 chrome 插槽。** `.deck-header`, `.deck-footer`, `.slide-number` 和进度条由 `assets/base.css` + `runtime.js` 提供。
- **声明式地添加一次标志。** 将 `data-logo` 放在 `<body>` 上 — 不要将 `<img>` 粘贴到每张幻灯片中。参见 *自定义标志* 下面的内容。
- **以键盘优先。** 始终包含运行时，例如 `<script src="../assets/runtime.js"></script>`，以便演示文稿支持 ← → / T / A / F / S / O / 哈希深度链接。
- **永远不要手动编辑 `../` 深度在资产路径中。** 每个 `assets/` 引用都是相对于包含它的文件：`templates/deck.html` 使用 `../assets/`，`templates/single-page/*.html` 使用 `../../assets/`，而 `templates/full-decks/*/index.html` 使用 `../../../assets/`。将文件复制到新的深度会无声地破坏所有它们。使用 `./scripts/new-deck.sh <name> [parent] [-t <template>]` 来搭建，它会计算演示文稿落地的前缀并验证每个引用是否解析。
- **每页一个逻辑页面。** `runtime.js` 使 `.slide.is-active` 可见；所有其他幻灯片都被隐藏。
- **提供笔记。** 在每张幻灯片内部用 `<div class="notes">…</div>` 包裹演讲者笔记。按 S 打开覆盖层。
- **永远不要在幻灯片本身上放置仅演讲者可见的文本。** 描述性文本，如“这一页展示了……”或“Speaker: 这里可以补充……”或面向演讲者的解释性标题，必须放在 `<div class="notes">` 内，而不是作为可见的 `<p>` / `<span>` 元素在幻灯片上。`.notes` 类默认为 `display:none` — 它仅在 S 覆盖层中显示。幻灯片应仅包含面向观众的內容（标题、要点、数据、图表、图像）。

## 图像

`templates/single-page/` 中的五个布局使用真实图像。根据页面需要承载多少图像来选择：

| 我有… | 使用 | 为什么 |
|---|---|---|
| 一个截图 / 图表 / 图表 | `image-single.html` | `.img-frame.contain` — 信封，**从不裁剪** |
| 一个应该承载页面的照片 | `image-full-bleed.html` | 填满幻灯片，渐变遮罩使标题可读 |
| 一个图像加上一个论点 | `image-text-split.html` | 50/50；添加 `flip` 到 `.split` 将图像移到右侧 |
| 3–6 个图像 | `image-gallery.html` | 统一网格；混合源比例由框架规范化 |
| 一个之前和一个之后 | `image-compare.html` | 两侧尺寸相同，结论在每个下面 |

`image-grid.html` 和 `image-hero.html` **不在**此列表中：它们是渐变占位符布局，根本没有 `<img>`。当您想要便当墙的形状而没有提供图片时，请使用它们。

这五个都基于 `assets/base.css` 中的一个基本元素：

```html
<figure class="img-frame"><img src="shot.png" alt=""></figure>
<figure class="img-frame contain" style="--img-ratio:4/3"><img src="diagram.svg" alt=""></figure>
```

- `.img-frame` 拥有**宽高比和裁剪**；`<img>` 用 `object-fit: cover` 填充它。这就是允许用户交换任何形状的照片而不会破坏布局的原因。
- `.img-frame.contain` 信封而不是裁剪 — **始终用于截图、图表和标志。**
- `--img-ratio` (默认 `16/10`) 和 `--img-pos` (`object-position`) 调整它。
- `.img-scrim` / `.img-cap` / `.img-tag` 是遮罩、标题和角落药丸。
- 从演示文稿引用的图像是相对于演示文稿自己的 `index.html` 解析的 — 将它们保留在演示文稿文件夹中，例如 `examples/my-talk/shot.png`。
- `assets/demo-images/` 持有这些布局使用的占位符艺术品：手绘 SVG，每个约 1 KB，**无需网络**。

## 自定义标志

要使用公司 / 产品标志来品牌化演示文稿，请在 `<body>` 上声明一次：

```html
<body data-logo="logo.svg"
      data-logo-position="bottom-right"
      data-logo-size="40px">
```

| 属性 | 默认 | 备注 |
|---|---|---|
| `data-logo` | — | 图像 URL，相对于演示文稿自己的 HTML 文件。必需。 |
| `data-logo-position` | `top-right` | `top-left` / `top-right` / `bottom-left` / `bottom-right` |
| `data-logo-size` | `44px` | 任何 CSS 长度；设置标志的**高度**，宽度跟随宽高比 |
| `data-logo-opacity` | `.9` | `1` 对于全强度 |
| `data-logo-alt` | `""` | Alt 文本 |

- **在一张幻灯片上跳过它** 使用 `<section class="slide" data-no-logo>` — 通常封面和任何全出血图像幻灯片都有自己的品牌。
- **微调插入** 使用 `.deck-logo` 上的 `--logo-inset-x` / `--logo-inset-y`。
- **手动放置**，如果您想将其放置在 chrome 插槽或四个预设不覆盖的位置：
  ```html
  <div class="deck">
    <img class="deck-logo" data-pos="bottom-left" src="logo.svg" alt="">
  ```
  这个路径完全不需要 JS — `base.css` 以相同的方式样式化两者。
- 标志在演讲者预览中显示，并且在**打印/PDF 导出**的**每一页**上显示（与头部/尾部/进度条 chrome 不同，打印会隐藏）。`data-no-logo` 幻灯片在那里也会被跳过。每页打印由 `runtime.js` + `@media print` 绘制；省略运行时的演示文稿仍然在屏幕上显示标志，但仅在 PDF 的某一页上。

## 写作指南

参见 [references/authoring-guide.md](references/authoring-guide.md) 了解逐步演练：文件结构、命名、如何将大纲转换为演示文稿、如何根据观众选择布局和主题、如何制作中英双语演示文稿，以及如何导出。

## 目录 (按需加载)

- [references/themes.md](references/themes.md) — 所有 36 个主题及其适用场景。
- [references/layouts.md](references/layouts.md) — 所有 36 个布局类型。
- [references/animations.md](references/animations.md) — 27 个 CSS + 20 个 canvas FX 动画。
- [references/full-decks.md](references/full-decks.md) — 所有 15 个完整幻灯片模板。
- [references/presenter-mode.md](references/presenter-mode.md) — **演讲者模式 + 逐字稿编写指南（技术分享/演讲必看）**.
- [references/authoring-guide.md](references/authoring-guide.md) — 完整工作流程。

## 文件结构

```
html-ppt/
├── SKILL.md                 (此文件)
├── references/              (详细目录，按需加载)
├── assets/
│   ├── base.css             (token + 基础元素 — 每个演示文稿不编辑)
│   ├── demo-images/*.svg    (图像-*布局的离线占位符)
│   ├── fonts.css            (网络字体导入)
│   ├── runtime.js           (键盘 + 演示者 + 概览 + 主题循环)
│   ├── themes/*.css         (36个token覆盖，每个主题一个)
│   └── animations/
│       ├── animations.css   (27个命名CSS入口动画)
│       ├── fx-runtime.js    (自动初始化[数据-fx]在幻灯片进入时)
│       └── fx/*.js          (20个canvas特效模块：粒子/图形/烟花…)
├── templates/
│   ├── deck.html                  (最小6页启动器)
│   ├── theme-showcase.html        (36页，每个主题iframe隔离)
│   ├── layout-showcase.html       (所有36个布局的iframe导览)
│   ├── animation-showcase.html    (20个特效 + 27个CSS动画幻灯片)
│   ├── full-decks-index.html      (所有15个完整演示文稿模板的画廊)
│   ├── full-decks/<name>/         (15个作用域多页演示文稿模板)
│   └── single-page/*.html         (36个带演示数据的布局文件)
├── scripts/
│   ├── new-deck.sh                (从deck.html生成演示文稿)
│   └── render.sh                  (无头Chrome → PNG)
└── examples/demo-deck/            (完整可工作的演示文稿)
```

## 渲染为PNG

`scripts/render.sh` 包装无头Chrome
`/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`。对于多页捕获，
runtime.js暴露`#/N`深度链接，render.sh迭代1..N。

```bash
./scripts/render.sh templates/single-page/kpi-grid.html        # 单页
./scripts/render.sh examples/demo-deck/index.html 8 out-dir    # 8页，自定义目录
```

## 键盘快捷键

```
←  →  Space  PgUp  PgDn  Home  End    导航
左划/右划 (触摸)              导航 — 手机和平板，无需键盘
F                                       全屏
S                                       打开演示者窗口 (磁性卡片：当前/下一/脚本/计时器)
N                                       快速笔记抽屉 (底部覆盖层)
R                                       重置计时器 (在演示者窗口)
?preview=N                              URL参数 — 强制预览模式 (单页，无Chrome)
O                                       幻灯片概览网格
T                                       循环主题 (读取data-themes属性)
A                                       当前幻灯片循环演示动画
#/N在URL                              深度链接到第N页
Esc                                     关闭所有覆盖层
```

## 许可证 & 作者

MIT。版权所有 (c) 2026 lewis &lt;sudolewis@gmail.com&gt;。
```
