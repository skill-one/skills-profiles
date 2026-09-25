# PPTX 生成器与编辑器

## 概述

该技能处理所有 PowerPoint 任务：读取/分析现有演示文稿、通过 XML 操作编辑基于模板的演示文稿，以及使用 PptxGenJS 从零创建演示文稿。它包含完整的设计系统（调色板、字体、样式配方）以及每种幻灯片类型的详细指南。

## 快速参考

| 任务 | 方法 |
|------|------|
| 读取/分析内容 | `python -m markitdown presentation.pptx` |
| 基于模板编辑或创建 | 参考 [编辑演示文稿](references/editing.md) |
| 从零创建 | 参考 下面的 [从零创建工作流](#creating-from-scratch-workflow) |

| 项目 | 值 |
|------|------|
| **尺寸** | 10" x 5.625" (LAYOUT_16x9) |
| **颜色** | 6 位十六进制无 # (例如，`"FF0000"`) |
| **英文字体** | Arial (默认)，或批准的替代字体 |
| **中文字体** | Microsoft YaHei |
| **页面标签位置** | x: 9.3"，y: 5.1" |
| **主题键** | `primary`，`secondary`，`accent`，`light`，`bg` |
| **形状** | RECTANGLE，OVAL，LINE，ROUNDED_RECTANGLE |
| **图表** | BAR，LINE，PIE，DOUGHNUT，SCATTER，BUBBLE，RADAR |

## 参考文件

| 文件 | 内容 |
|------|------|
| [slide-types.md](references/slide-types.md) | 5 种幻灯片页面类型（封面、目录、分隔符、内容、总结）+ 额外的布局模式 |
| [design-system.md](references/design-system.md) | 调色板、字体参考、样式配方（Sharp/Soft/Rounded/Pill）、排版和间距 |
| [editing.md](references/editing.md) | 基于模板的编辑工作流、XML 操作、格式规则、常见陷阱 |
| [pitfalls.md](references/pitfalls.md) | QA 流程、常见错误、关键的 PptxGenJS 陷阱 |
| [pptxgenjs.md](references/pptxgenjs.md) | 完整的 PptxGenJS API 参考 |

---

## 读取内容

```bash
# 文本提取
python -m markitdown presentation.pptx
```

---

## 从零创建 — 工作流

**在没有模板或参考演示文稿的情况下使用。**

### 第 1 步：研究与需求

搜索以了解用户需求——主题、受众、目的、语气、内容深度。

### 第 2 步：选择调色板和字体

使用 [调色板参考](references/design-system.md#color-palette-reference) 选择与主题和受众相匹配的调色板。使用 [字体参考](references/design-system.md#font-reference) 选择字体搭配。

### 第 3 步：选择设计风格

使用 [样式配方](references/design-system.md#style-recipes) 选择与演示文稿语气相匹配的视觉风格（Sharp、Soft、Rounded 或 Pill）。

### 第 4 步：规划幻灯片大纲

将**每张幻灯片**分类为 [5 种页面类型](references/slide-types.md) 中的确切一种。规划每张幻灯片的内容和布局。确保视觉多样性——不要在幻灯片之间重复相同的布局。

### 第 5 步：生成幻灯片 JS 文件

在 `slides/` 目录中为每张幻灯片创建一个 JS 文件。每个文件必须导出一个同步的 `createSlide(pres, theme)` 函数。遵循 [幻灯片输出格式](#slide-output-format) 和 [slide-types.md](references/slide-types.md) 中类型特定的指南。如果可用，使用子代理并发生成最多 5 张幻灯片。

**告诉每个子代理：**
1. 文件命名：`slides/slide-01.js`，`slides/slide-02.js`，等。
2. 图片放在：`slides/imgs/`
3. 最终 PPTX 放在：`slides/output/`
4. 尺寸：10" x 5.625" (LAYOUT_16x9)
5. 字体：中文 = Microsoft YaHei，英文 = Arial（或批准的替代字体）
6. 颜色：6 位十六进制无 #（例如。`"FF0000"`)
7. 必须使用主题对象契约（见 [主题对象契约](#theme-object-contract)）
8. 必须遵循 [PptxGenJS API 参考](references/pptxgenjs.md)

### 第 6 步：编译成最终 PPTX

创建 `slides/compile.js` 以组合所有幻灯片模块：

```javascript
// slides/compile.js
const pptxgen = require('pptxgenjs');
const pres = new pptxgen();
pres.layout = 'LAYOUT_16x9';

const theme = {
  primary: "22223b",    // 深色背景/文本
  secondary: "4a4e69",  // 次要强调色
  accent: "9a8c98",     // 高亮颜色
  light: "c9ada7",      // 轻强调色
  bg: "f2e9e4"          // 背景颜色
};

for (let i = 1; i <= 12; i++) {  // 根据需要调整数量
  const num = String(i).padStart(2, '0');
  const slideModule = require(`./slide-${num}.js`);
  slideModule.createSlide(pres, theme);
}

pres.writeFile({ fileName: './output/presentation.pptx' });
```

运行：`cd slides && node compile.js`

### 第 7 步：QA（必需）

参考 [QA 流程](references/pitfalls.md#qa-process)。

### 输出结构

```
slides/
├── slide-01.js          # 幻灯片模块
├── slide-02.js
├── ...
├── imgs/                # 幻灯片中使用的图片
└── output/              # 最终文件
    └── presentation.pptx
```

---

## 幻灯片输出格式

每张幻灯片是一个**完整的、可运行的 JS 文件**：

```javascript
// slide-01.js
const pptxgen = require("pptxgenjs");

const slideConfig = {
  type: 'cover',
  index: 1,
  title: '演示文稿标题'
};

// 必须是同步的（不是异步）
function createSlide(pres, theme) {
  const slide = pres.addSlide();
  slide.background = { color: theme.bg };

  slide.addText(slideConfig.title, {
    x: 0.5, y: 2, w: 9, h: 1.2,
    fontSize: 48, fontFace: "Arial",
    color: theme.primary, bold: true, align: "center"
  });

  return slide;
}

// 独立预览 - 使用特定的幻灯片文件名
if (require.main === module) {
  const pres = new pptxgen();
  pres.layout = 'LAYOUT_16x9';
  const theme = {
    primary: "22223b",
    secondary: "4a4e69",
    accent: "9a8c98",
    light: "c9ada7",
    bg: "f2e9e4"
  };
  createSlide(pres, theme);
  pres.writeFile({ fileName: "slide-01-preview.pptx" });
}

module.exports = { createSlide, slideConfig };
```

---

## 主题对象契约（强制）

编译脚本传递一个具有这些**确切键**的主题对象：

| 键 | 目的 | 示例 |
|------|------|------|
| `theme.primary` | 最深的颜色，标题 | `"22223b"` |
| `theme.secondary` | 深色强调色，正文 | `"4a4e69"` |
| `theme.accent` | 中等色调强调色 | `"9a8c98"` |
| `theme.light` | 轻强调色 | `"c9ada7"` |
| `theme.bg` | 背景颜色 | `"f2e9e4"` |

**绝对不要使用其他键名**，如 `background`，`text`，`muted`，`darkest`，`lightest`。

---

## 页码标签（强制）

所有幻灯片**除封面页外**都必须在右下角包含页码标签。

- **位置**：x: 9.3"，y: 5.1"
- 仅显示当前页码（例如 `3` 或 `03`），不显示 "3/12"
- 使用调色板颜色，保持微妙

### 圆形标签（默认）

```javascript
slide.addShape(pres.shapes.OVAL, {
  x: 9.3, y: 5.1, w: 0.4, h: 0.4,
  fill: { color: theme.accent }
});
slide.addText("3", {
  x: 9.3, y: 5.1, w: 0.4, h: 0.4,
  fontSize: 12, fontFace: "Arial",
  color: "FFFFFF", bold: true,
  align: "center", valign: "middle"
});
```

### 药丸标签

```javascript
slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
  x: 9.1, y: 5.15, w: 0.6, h: 0.35,
  fill: { color: theme.accent },
  rectRadius: 0.15
});
slide.addText("03", {
  x: 9.1, y: 5.15, w: 0.6, h: 0.35,
  fontSize: 11, fontFace: "Arial",
  color: "FFFFFF", bold: true,
  align: "center", valign: "middle"
});
```

---

## 依赖项

- `pip install "markitdown[pptx]"` — 文本提取
- `npm install -g pptxgenjs` — 从零创建
- `npm install -g react-icons react react-dom sharp` — 图标（可选）
