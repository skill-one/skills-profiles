# Sentry 演示文稿构建器

使用 React + Vite + Recharts 创建交互式、数据驱动的演示文稿幻灯片，采用 Sentry 设计系统进行样式设计，并构建为单个可分发的 HTML 文件。

## 第 1 步：收集需求

向用户询问：
1. 演示文稿的主题是什么？
2. 需要多少张幻灯片（通常为 5-8 张）？
3. 需要哪些数据/图表？（时间序列、比较、图表、区域图表）
4. 叙事结构是什么？（问题→解决方案、之前→之后、技术深入探讨）

### 数据评估（关键）

在设计任何幻灯片之前，评估源内容是否包含**真实的定量数据**（数字、百分比、测量值、时间序列、成本、指标）。仅在存在真实数据的幻灯片中创建 Recharts 可视化。不要为了填充图表而编造、估算或虚构数据。

- **包含真实数据** → 使用 Recharts 图表（条形图、面积图、折线图等）
- **没有数据** → 使用基于文本的布局：卡片、表格、项目符号列、图表或引言块。不要创建带有编造数字的图表。

如果源内容完全是定性的（叙述、观点、策略、流程描述），演示文稿应使用零个图表。Recharts 和 `Charts.jsx` 只有在至少有一张幻灯片需要可视化真实数据时才应包含在项目中。

## 第 2 步：搭建项目

创建项目结构：

```
<project-name>/
├── index.html
├── package.json
├── vite.config.js
└── src/
    ├── main.jsx
    ├── App.jsx
    ├── App.css
    └── Charts.jsx
```

### index.html

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link href="https://fonts.googleapis.com/css2?family=Rubik:wght@300;400;500;600;700&display=swap" rel="stylesheet" />
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=swap" rel="stylesheet" />
    <title>TITLE</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
```

### package.json

```json
{
  "name": "PROJECT_NAME",
  "private": true,
  "type": "module",
  "scripts": { "dev": "vite", "build": "vite build", "preview": "vite preview" },
  "dependencies": { "react": "^18.3.1", "react-dom": "^18.3.1", "recharts": "^2.15.3" },
  "devDependencies": { "@vitejs/plugin-react": "^4.3.4", "vite": "^6.0.0", "vite-plugin-singlefile": "^2.3.0" }
}
```

### vite.config.js

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { viteSingleFile } from 'vite-plugin-singlefile'

export default defineConfig({ plugins: [react(), viteSingleFile()] })
```

### main.jsx

```jsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './App.css'

ReactDOM.createRoot(document.getElementById('root')).render(<App />)
```

## 第 3 步：构建幻灯片系统

阅读 `references/design-system.md` 了解 Sentry 的完整调色板、排版、CSS 变量、布局工具和动画系统。

### App.jsx 结构

将幻灯片定义为返回 JSX 的函数数组：

```jsx
const SLIDES = [
  () => ( /* 幻灯片 0：标题 */ ),
  () => ( /* 幻灯片 1：背景 */ ),
  // ...
];
```

每个幻灯片函数返回一个 `<div className="slide-content">`，包含：
1. 一个 `<h2>` 标题
2. 可选的副标题段落
3. 主要内容（图表、卡片、图表、表格）
4. 动画类：`.anim`、`.d1`、`.d2`、`.d3` 用于交错淡入

不要在标题上方添加分类标签（例如，“背景”、“实验”）。它们看起来很通用且没有价值。让标题自己说话。

### 导航

实现键盘导航（右箭头/空格 = 下一张，左箭头 = 上一张）和底部导航覆盖层，包含上一张/下一张按钮、点指示器和幻灯片编号。导航**没有边框或背景**——它透明地浮动。一个小的低对比度 Sentry 图形水印固定在每张幻灯片的左上角。

```jsx
function App() {
  const [cur, setCur] = useState(0);
  const go = useCallback((d) => setCur(c => Math.max(0, Math.min(SLIDES.length - 1, c + d))), []);

  useEffect(() => {
    const h = (e) => {
      if (e.target.tagName === 'INPUT') return;
      if (e.key === 'ArrowRight' || e.key === ' ') { e.preventDefault(); go(1); }
      if (e.key === 'ArrowLeft') { e.preventDefault(); go(-1); }
    };
    window.addEventListener('keydown', h);
    return () => window.removeEventListener('keydown', h);
  }, [go]);

  return (
    <>
      {cur > 0 && <div className="glyph-watermark"><SentryGlyph size={50} /><span className="watermark-title">TITLE</span></div>}
      <div className="progress" style={{ width: `${((cur + 1) / SLIDES.length) * 100}%` }} />
      {SLIDES.map((S, i) => (
        <div key={i} className={`slide ${i === cur ? 'active' : ''}`}>
          <div className={`slide-content${i === cur ? ' anim' : ''}`}>
            <S />
          </div>
        </div>
      ))}
      <Nav cur={cur} total={SLIDES.length} go={go} setCur={setCur} />
    </>
  );
}
```

## 第 4 步：创建图表（仅当存在数据时）

**重要提示：** 仅创建由源内容提供的真实、具体数据的图表。如果一张幻灯片的内容是定性的（策略、学习成果、流程描述、观点），请使用基于文本的布局（卡片、表格、项目符号列表、列）。永远不要编造数字、虚构百分比或生成合成数据来填充图表。如果您不确定数据是真实的还是推断的，请不要创建图表。

如果没有幻灯片需要图表，请完全跳过此步骤——不要创建 `Charts.jsx` 或导入 Recharts。

当存在真实数据时，请阅读 `references/chart-patterns.md` 了解 Recharts 组件模式，包括轴配置、颜色常量、图表类型和数据生成技术。

将所有图表组件放在 `Charts.jsx` 中。关键模式：

- 使用 `ResponsiveContainer` 并指定高度
- 包裹在 `.chart-wrap` div 中，最大宽度为 920px
- 使用 `useMemo` 进行数据生成
- **颜色规则**：使用受 Tableau 启发的分类调色板（`CAT[]`）来区分数据系列和组。仅在颜色本身传达意义时（好/坏、成功/失败、警告）使用语义颜色（`SEM_GREEN`、`SEM_RED`、`SEM_AMBER`）
- 常见图表：`ComposedChart` 带有堆叠的 `Area`/`Line`、`BarChart`、自定义 SVG 图表
- **图表中的每个数据点都必须来自源内容。** 不要插值、外推或四舍五入数字以使图表看起来更好。

## 第 5 步：使用 Sentry 设计系统进行样式设计

应用设计系统参考的完整 CSS。关键元素：

- **字体**：Google Fonts 中的 Rubik
- **颜色**：UI 亮边的 CSS 变量（`--purple`、`--dark`、`--muted`）。仅在颜色传达意义时使用语义 CSS 变量（`--semantic-green`、`--semantic-red`、`--semantic-amber`）。所有其他数据可视化使用分类调色板（`CAT[]`）
- **幻灯片**：绝对定位，不透明度过渡
- **动画**：`fadeUp` 关键帧，交错延迟
- **布局**：`.cols` 弹性行，`.cards` 网格，`.chart-wrap` 容器
- **标签**：`.tag-purple`、`.tag-red`、`.tag-green`、`.tag-amber` 用于幻灯片标签
- **标志**：从 `references/sentry-logo.svg`（完整标志）或 `references/sentry-glyph.svg`（仅图形容号）读取官方 SVG。不要硬编码近似值——始终使用这些文件中的精确 SVG 路径。

## 第 6 步：常见幻灯片模式

### 标题幻灯片
标志（来自 `references/sentry-logo.svg` 或 `references/sentry-glyph.svg`）+ h1 + 副标题 + 作者/日期信息。

### 问题/背景幻灯片
标签 + 标题 + 2 列卡片网格，带图标标题。

### 数据比较幻灯片
标签 + 标题 + 并列图表或之前/之后比较表格。

### 技术深入探讨幻灯片
标签 + 标题 + 全宽图表 + 下方注释项目符号。

### 总结/决策幻灯片
标签 + 标题 + 3 列布局，带类别标题和项目符号列表。

## 第 7 步：迭代和优化

初始搭建后：
1. 运行 `npm install && npm run dev` 启动开发服务器
2. 迭代图表数据模型和视觉设计
3. 调整动画、颜色和布局间距
4. 构建最终输出：`npm run build` 在 `dist/` 中生成单个 HTML 文件

## 输出预期

一个工作中的 React + Vite 项目，满足：
- 渲染为键盘可导航的幻灯片演示文稿
- 使用 Sentry 品牌标识（颜色、字体、图标）
- 仅在具有来自源内容的真实定量数据的幻灯片中使用 Recharts 可视化——没有编造数据
- 如果没有幻灯片具有真实数据，则完全省略 `Charts.jsx` 和 Recharts 依赖
- 构建为单个可分发的 HTML 文件
- 幻灯片过渡时有平滑的淡入动画
