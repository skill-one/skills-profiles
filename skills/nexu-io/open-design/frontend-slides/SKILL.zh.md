---
name: frontend-slides
description: 以OpenDesign为例，一个成熟的AI工作流：具体说明本地代理如何读取您的文件并在您的桌面上进行设计——为初次接触AI的团队和领导层构建的决策级AI素养演示文稿。
---

# 前端幻灯片

完全无依赖、动画丰富的 HTML 幻灯片，完全在浏览器中运行。来自 MIT 授权的 [zarazhangrui/frontend-slides](https://github.com/zarazhangrui/frontend-slides) 的精选内容。

从本插件文件夹中的 `example.html` 开始。它是经过验证的种子：复制其舞台 CSS、幻灯片外壳，以及整个 `SlidePresentation` 控制器脚本，然后替换幻灯片内容。不要重新编写舞台系统、导航脚本或设计令牌架构。

## 严格规范（锁定——每个演示文稿都必须满足所有这些）

### 固定 16:9 舞台 — 不可协商

- 每个演示文稿都在固定 **1920×1080** 的画布上编写：`.deck-viewport`（填充窗口）包裹 `.deck-stage`（1920×1080，`transform-origin: 0 0`）。
- JavaScript 统一缩放整个舞台：`factor = min(innerWidth/1920, innerHeight/1080)`，然后 `translate(x, y) scale(factor)` 以带有画框/立柱框的方式居中。在 `resize` 时重新运行。
- 不要根据设备重新布局幻灯片内容。幻灯片内没有响应式断点。所有幻灯片测量值在 1920×1080 的设计尺寸下都是固定的 px。
- 在 `<style>` 块中包含 `references/viewport-base.css` 的全部内容（种子已经嵌入它）。

### 幻灯片结构

- 每页是一个 `<section class="slide">`，直接位于 `.deck-stage` 内。一个标准的演示文稿大约有 10 张幻灯片；将内容拆分成更多幻灯片，而不是缩小字体。
- 幻灯片切换使用 `.active` / `.visible` 类切换 `visibility`、`opacity`、`pointer-events`——**永远不要 `display: none/block`**（布局类如 `display: flex` 在子元素上会覆盖它，并一次性显示所有幻灯片）。
- 没有滚动，没有溢出，没有重叠的面板，1920×1080 下没有舒适的阅读尺寸以下的文本。

### 导航运行时（保留种子的脚本）

- 键盘：`←`/`→`、`↑`/`↓`、`Space`、`PageUp`/`PageDown`、`Home`/`End`。
- 哈希路由：当前幻灯片镜像到 `#/<index>`；深度链接和 `hashchange` 恢复幻灯片。
- 鼠标滚轮（约 650 毫秒的防抖）和触摸滑动（≥40 像素阈值）。
- 页面计数器边框位于 `.deck-controls`，固定位置**在**缩放舞台之外。

### 设计令牌

- 所有颜色、字体、尺寸和缓动效果都位于 `:root` CSS 自定义属性中；通过仅编辑令牌来重新主题。
- 字体：来自 Google Fonts 或 Fontshare 的独特网络字体——**永远不要**使用 Inter、Roboto、Arial 或系统字体作为显示类型。避免 `#6366f1` 靛蓝色和白色渐变等陈词滥调。
- 从 `references/STYLE_PRESETS.md` 中选择一个预设（12 个精选预设：Bold Signal、Electric Studio、Creative Voltage、Dark Botanical、Notebook Tabs、Pastel Geometry、Split Pastel、Vintage Editorial、Neon Cyber、Terminal Green、Swiss Modern、Paper & Ink）或使用相同的纪律设计自定义系统。种子提供 **Bold Signal**。

### 布局词汇（从这些中组合幻灯片）

`title-card`（彩色焦点卡片）、`agenda`（编号编辑列表）、`section divider`（巨型轮廓数字）、`bullets`（图标 + 标题 + 支持线，最多 4-6）、`big-stat`（超大数字 + 侧注）、`quote`、`two-column comparison`、`principle grid`（2×2 卡片）、`CSS bar chart`（scaleY 动画条）、`closing`。保持幻灯片编号左上角，面包屑导航右上角，基线规则底部——这个边框是演示文稿的标志。

### 动画

- 通过 `.reveal` 元素进入，当幻灯片获得 `.visible` 时过渡；使用 `transition-delay` 步骤（~0.1 秒）错开。
- 每个演示文稿有一个独特的缓动效果（种子：`cubic-bezier(0.16, 1, 0.3, 1)`）；仅动画 `transform` 和 `opacity`。
- `prefers-reduced-motion` 支持是强制性的（包含在 viewport-base.css 中）。
- 使用 `references/animation-patterns.md` 将动画特性与内容的感受相匹配。

### 密度模式

询问（或推断）演示文稿是演讲者主导还是阅读优先：

- **低密度 / 演讲者主导**——每张幻灯片一个想法，大字体，最多 1-3 个要点，更多幻灯片。
- **高密度 / 阅读优先**——自包含幻灯片，结构化网格/表格，最多 4-6 张卡片，仍然没有溢出。

### 输出合同

- 单个自包含的 `.html` 文件：所有 CSS 和 JS 内联，没有构建步骤，没有外部 JS 库，没有 CDN 脚本。
- 图标是内联 SVG。没有来自慢速 CDNs 的远程图像；CSS 生成的视觉效果（渐变、形状、图案）是一流的路径。
- 每个部分都进行注释：`/* === SECTION NAME === */`。
- CSS 小技巧：永远不要直接否定 CSS 函数（`-clamp()` 被静默忽略）——使用 `calc(-1 * clamp(...))`。

## 参考（按需阅读）

| 文件 | 何时 |
| ---- | ---- |
| `references/STYLE_PRESETS.md` | 选择视觉方向 |
| `references/viewport-base.css` | 强制舞台 CSS — 完整嵌入 |
| `references/html-template.md` | 控制器架构，内联编辑模式，图像管道 |
| `references/animation-patterns.md` | 将效果与感受相匹配 |

## 致谢

设计系统、固定舞台模型、预设和工作流程来自上游的 MIT 授权的 [zarazhangrui/frontend-slides](https://github.com/zarazhangrui/frontend-slides)（© 2025 Zara Zhang）。LICENSE 文件随本插件文件夹一起提供；在重新分发时保持其位置。
