# 架构图设计规范

使用内联 SVG 图形和 CSS 样式创建专业的技术架构图，以自包含的 HTML 文件形式呈现。

> **版本 1.1** · MIT 许可证 · 作者：[Cocoon AI](mailto:hello@cocoon-ai.com)

## 设计系统

### 色彩搭配

使用以下语义色彩表示组件类型：

| 组件类型 | 填充 (rgba) | 描边 |
|---------|------------|------|
| 前端     | `rgba(8, 51, 68, 0.4)` | `#22d3ee` (青色-400) |
| 后端     | `rgba(6, 78, 59, 0.4)` | `#34d399` (橄榄绿-400) |
| 数据库   | `rgba(76, 29, 149, 0.4)` | `#a78bfa` (紫色-400) |
| AWS/云   | `rgba(120, 53, 15, 0.3)` | `#fbbf24` (琥珀色-400) |
| 安全     | `rgba(136, 19, 55, 0.4)` | `#fb7185` (玫瑰色-400) |
| 消息总线 | `rgba(251, 146, 60, 0.3)` | `#fb923c` (橙色-400) |
| 外部/通用 | `rgba(30, 41, 59, 0.5)` | `#94a3b8` (石板灰-400) |

### 字体排印

对所有文本使用 JetBrains Mono 字体（等宽字体，技术美学）：
```html
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
```

字体大小：组件名称使用 12px，子标签使用 9px，注释使用 8px，微标签使用 7px。

### 视觉元素

**背景**：`#020617` (石板灰-950) 带有细微的网格图案：
```svg
<pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
  <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#1e293b" stroke-width="0.5"/>
</pattern>
```

**组件框**：圆角矩形 (`rx="6"`)，1.5px 描边，半透明填充。

**安全组**：虚线描边 (`stroke-dasharray="4,4"`)，透明填充，玫瑰色。

**区域边界**：更大的虚线描边 (`stroke-dasharray="8,4"`)，琥珀色，`rx="12"`。

**箭头**：使用 SVG 标记器绘制箭头头：
```svg
<marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
  <polygon points="0 0, 10 3.5, 0 7" fill="#64748b" />
</marker>
```

**箭头 z-顺序**：在 SVG 中尽早绘制连接箭头（在背景网格之后），以便它们渲染在组件框之后。SVG 元素按文档顺序绘制，因此先绘制的箭头会出现在后绘制的形状之前。

**遮罩箭头在透明填充背后**：由于组件框使用半透明填充 (`rgba(..., 0.4)`)，箭头会穿透显示。要完全遮罩箭头，在绘制半透明样式矩形之前，在相同位置绘制一个不透明的背景矩形（例如，`fill="#0f172a"`）：
```svg
<!-- 不透明背景以遮罩箭头 -->
<rect x="X" y="Y" width="W" height="H" rx="6" fill="#0f172a"/>
<!-- 样式化的组件在上层 -->
<rect x="X" y="Y" width="W" height="H" rx="6" fill="rgba(76, 29, 149, 0.4)" stroke="#a78bfa" stroke-width="1.5"/>
```

**认证/安全流程**：玫瑰色 (`#fb7185`) 的虚线。

**消息总线/事件总线**：服务之间的小型连接元素。使用橙色 (`#fb923c` 描边，`rgba(251, 146, 60, 0.3)` 填充)：
```svg
<rect x="X" y="Y" width="120" height="20" rx="4" fill="rgba(251, 146, 60, 0.3)" stroke="#fb923c" stroke-width="1"/>
<text x="CENTER_X" y="Y+14" fill="#fb923c" font-size="7" text-anchor="middle">Kafka / RabbitMQ</text>
```

### 间距规则

**关键**：当垂直堆叠组件时，确保适当间距以避免重叠：

- **标准组件高度**：服务 60px，较大组件 80-120px
- **组件之间的最小垂直间距**：40px
- **内联连接器（消息总线）**：放置在组件之间的间隙中，而不是重叠

**示例垂直布局**：
```
组件 A：y=70,  高度=60  → 结束于 y=130
间隙：         y=130 到 y=170   → 40px 间隙，放置总线于 y=140 (20px 高)
组件 B：y=170, 高度=60  → 结束于 y=230
```

**错误**：当组件 B 开始于 y=170 时将消息总线放置在 y=160（导致重叠）
**正确**：将消息总线放置在 y=140，在 40px 间隙中居中（y=130 到 y=170）

### 图例位置

**关键**：将图例放置在所有边界框（区域边界、集群边界、安全组）之外。

- 计算所有边界结束的位置（y 位置 + 高度）
- 将图例放置在最低边界至少 20px 下方
- 如有需要，扩展 SVG viewBox 高度以适应

**示例**：
```
Kubernetes 集群：y=30, 高度=460 → 结束于 y=490
图例应从：y=510 或更低开始
SVG viewBox 高度：至少 560 以适应图例
```

**错误**：图例位于 y=470，在结束于 y=490 的集群边界内
**正确**：图例位于 y=510，在集群边界下方，将 viewBox 高度扩展

### 布局结构

1. **头部** - 带有脉冲点指示器的标题、副标题和导出工具栏
2. **主 SVG 图表** - 包含在圆角边框卡片中
3. **摘要卡片** - 图表下方 3 卡片网格，包含关键信息
4. **页脚** - 最小元数据行

### 导出工具栏（内置）

每个图表都附带一个不显眼的 `⋯` 切换按钮在头部。点击它将显示三个按钮 — 📋 复制（高 DPI PNG 到剪贴板，缩放：2），🖼️ PNG（高 DPI PNG 下载），📄 PDF（PNG 嵌入单页 PDF 中 via jsPDF）。工具栏默认折叠回图标，以免杂乱图表。所有三种格式都使用相同的 html2canvas 捕获（排除工具栏并在内容周围添加 32px 边距），因此 PDF 保留了暗色主题，而无需通过浏览器的打印对话框。

生成新图表时，在模板中保留以下内容：
- `<head>` 中的两个 CDN 脚本（固定版本，带有 Subresource Integrity 哈希和 `crossorigin="anonymous"`）：
  - `https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js` — `integrity="sha384-ZZ1pncU3bQe8y31yfZdMFdSpttDoPmOZg2wguVK9almUodir1PghgT0eY7Mrty8H"`
  - `https://cdn.jsdelivr.net/npm/jspdf@2.5.2/dist/jspdf.umd.min.js` — `integrity="sha384-en/ztfPSRkGfME4KIm05joYXynqzUgbsG5nMrj/xEFAHXkeZfO3yMK8QQ+mP7p1/"`
  - SRI 确保生成的图表对 CDN 侵害具有抗篡改能力。不要修改哈希；如果版本更新，必须重新计算新哈希。
- `id="report-container"` 在最外层的 `.container` div 上（这是捕获的内容）
- `.toolbar` 标记，带有 `.toolbar-actions`（默认折叠）和 `.toolbar-toggle`（`⋯` 按钮）
- `.toolbar` CSS + `@media print { .toolbar { display: none !important; } }`
- `copyAsImage()`, `downloadPNG()`, 和 `downloadPDF()` 脚本在 `</body>` 之前，所有使用 `getBoundingClientRect()` + `html2canvas(document.body, { x, y, width, height, ignoreElements })` 捕获精确矩形，带有呼吸空间且无工具栏

注意事项：剪贴板 API 需要用户操作和安全的上下文（https/file/localhost）。SVG `<foreignObject>` 在 html2canvas 中渲染不一致 — 坚持使用纯 `<svg>` 形状和 `<text>`。将 `scale: 2` 提高到 `3` 或 `4` 以获得更高分辨率的输出。

### 组件框模式

```svg
<rect x="X" y="Y" width="W" height="H" rx="6" fill="FILL_COLOR" stroke="STROKE_COLOR" stroke-width="1.5"/>
<text x="CENTER_X" y="Y+20" fill="white" font-size="11" font-weight="600" text-anchor="middle">LABEL</text>
<text x="CENTER_X" y="Y+36" fill="#94a3b8" font-size="9" text-anchor="middle">sublabel</text>
```

### 信息卡片模式

```html
<div class="card">
  <div class="card-header">
    <div class="card-dot COLOR"></div>
    <h3>Title</h3>
  </div>
  <ul>
    <li>• Item one</li>
    <li>• Item two</li>
  </ul>
</div>
```

## 模板

复制并自定义 `resources/template.html` 中的模板。关键自定义点：

1. 更新 `<title>` 和头部文本
2. 如有必要修改 SVG viewBox 尺寸（默认：`1000 x 680`）
3. 添加/删除/重新定位组件框
4. 绘制组件之间的连接箭头
5. 更新三个摘要卡片
6. 更新页脚元数据

## 输出

始终生成单个自包含的 `.html` 文件，包含：
- 嵌入式 CSS（无外部样式表，仅 Google Fonts）
- 内联 SVG（无外部图像）
- 无需 JavaScript（纯 CSS 动画）

该文件应在任何现代浏览器中直接打开时正确渲染。导出工具栏使用两个 CDN 脚本（html2canvas 和 jsPDF）— 无其他 JavaScript 依赖。
