信息图表将数据、信息和知识转化为可感知的视觉语言。它们结合了视觉设计与数据可视化，通过直观的符号压缩复杂信息，帮助受众快速理解和记忆要点。

`信息图表 = 信息结构 + 视觉表达`

本任务使用 [AntV 信息图表](https://infographic.antv.vision/) 创建视觉信息图表。

在开始任务之前，您需要了解 AntV 信息图表的语法规范，包括模板列表、数据结构、主题等。

## 规范

### AntV 信息图表语法

AntV 信息图表语法是一种自定义的 DSL，用于描述信息图表渲染配置。它使用缩进来描述信息，具有强大的鲁棒性，便于 AI 流式输出和信息图表渲染。它主要包含以下信息：

1. template：使用模板来表示文本信息结构。
2. data：信息图表数据，包括标题、描述、数据项等。数据项通常包含标签、描述、图标等字段。
3. theme：主题包含调色板、字体等样式配置。

例如：

```plain
infographic list-row-horizontal-icon-arrow
data
  title 标题
  desc 描述
  lists
    - label 标签
      value 12.5
      desc 解释
      icon document text
theme
  palette #3b82f6 #8b5cf6 #f97316
```

### 语法规范

- 第一行必须是 `infographic <template-name>`，模板从下面的列表中选择（见“可用模板”部分）。
- 使用 `data` / `theme` 块，块内使用两个空格缩进。
- 键值对使用“键 空格 值”；数组使用 `-` 作为条目前缀。
- icon 使用图标关键词（例如，`star fill`）。
- `data` 应包含标题/描述 + 模板特定的主要数据字段（不一定是 `items`）。
- 主要数据字段选择（仅使用一个，避免混合）：
  - `list-*` → `lists`
  - `sequence-*` → `sequences`（可选 `order asc|desc`）
  - `compare-*` → `compares`（支持 `children` 用于分组比较），可以包含多个比较项
  - `hierarchy-structure` → `items`（每个项对应一个独立层次，每个级别可以包含子项，最多可嵌套 3 层）
  - `hierarchy-*` → 单个 `root`（树结构，通过 `children` 嵌套）；
  - `relation-*` → `nodes` + `relations`；简单的关系图可以省略 `nodes`，在关系中使用箭头语法
  - `chart-*` → `values`（数值统计，可选 `category`）
  - 不确定时使用 `items` 作为备用
- `compare-binary-*` / `compare-hierarchy-left-right-*` 二元模板：必须有两个根节点，所有比较项都挂在这两个根节点的子节点下
- `hierarchy-*`：使用单个 `root`，通过 `children` 嵌套（不要重复 `root`）
- `theme` 用于自定义主题（调色板、字体等）
  例如：暗色主题 + 自定义配色方案
  ```plain
  infographic list-row-horizontal-icon-arrow
  theme dark
    palette
      - #61DDAA
      - #F6BD16
      - #F08BB4
  ```
- 使用 `theme.base.text.font-family` 指定字体，例如手写风格 `851tegakizatsu`
- 使用 `theme.stylize` 选择内置样式并传递参数
  常见样式：
  - `rough`：手绘效果
  - `pattern`：图案填充
  - `linear-gradient` / `radial-gradient`：线性/径向渐变

  例如：手绘风格（rough）

  ```plain
  infographic list-row-horizontal-icon-arrow
  theme
    stylize rough
    base
      text
        font-family 851tegakizatsu
  ```

- 不要输出 JSON、Markdown 或解释性文本

### 数据语法示例

按模板类别提供数据语法示例（使用相应字段，避免同时添加 `items`）：

- `list-*` 模板

```plain
infographic list-grid-badge-card
data
  title 功能列表
  lists
    - label 快速
      icon flash fast
    - label 安全
      icon secure shield check
```

- `sequence-*` 模板

```plain
infographic sequence-steps-simple
data
  sequences
    - label 第一步
    - label 第二步
    - label 第三步
  order asc
```

- `hierarchy-*` 模板

```plain
infographic hierarchy-structure
data
  root
    label 公司
    children
      - label 部门 A
      - label 部门 B
```

- `compare-*` 模板

```plain
infographic compare-swot
data
  compares
    - label 优势
      children
        - label 强大的品牌
        - label 忠诚的用户
    - label 劣势
      children
        - label 高成本
        - label 发布缓慢
```

象限图

```plain
infographic compare-quadrant-quarter-simple-card
data
  compares
    - label 高影响 & 低努力
    - label 高影响 & 高努力
    - label 低影响 & 低努力
    - label 低影响 & 高努力
```

- `chart-*` 模板

```plain
infographic chart-column-simple
data
  values
    - label 访问量
      value 1280
    - label 转化率
      value 12.4
```

- `relation-*` 模板

> 边缘标签语法：A -label-> B 或 A -->|label| B

```plain
infographic relation-dagre-flow-tb-simple-circle-node
data
  nodes
    - id A
      label 节点 A
    - id B
      label 节点 B
  relations
    A - approves -> B
    A -->|blocks| B
```

- 备用 `items` 示例

```plain
infographic list-row-horizontal-icon-arrow
data
  items
    - label 项目 A
      desc 描述
      icon sun
    - label 项目 B
      desc 描述
      icon moon
```

### 可用模板

- chart-bar-plain-text
- chart-column-simple
- chart-line-plain-text
- chart-pie-compact-card
- chart-pie-donut-pill-badge
- chart-pie-donut-plain-text
- chart-pie-plain-text
- chart-wordcloud
- compare-binary-horizontal-badge-card-arrow
- compare-binary-horizontal-simple-fold
- compare-binary-horizontal-underline-text-vs
- compare-hierarchy-left-right-circle-node-pill-badge
- compare-quadrant-quarter-circular
- compare-quadrant-quarter-simple-card
- compare-swot
- hierarchy-mindmap-branch-gradient-capsule-item
- hierarchy-mindmap-level-gradient-compact-card
- hierarchy-structure
- hierarchy-tree-curved-line-rounded-rect-node
- hierarchy-tree-tech-style-badge-card
- hierarchy-tree-tech-style-capsule-item
- list-column-done-list
- list-column-simple-vertical-arrow
- list-column-vertical-icon-arrow
- list-grid-badge-card
- list-grid-candy-card-lite
- list-grid-ribbon-card
- list-row-horizontal-icon-arrow
- list-sector-plain-text
- list-zigzag-down-compact-card
- list-zigzag-down-simple
- list-zigzag-up-compact-card
- list-zigzag-up-simple
- relation-dagre-flow-tb-animated-badge-card
- relation-dagre-flow-tb-animated-simple-circle-node
- relation-dagre-flow-tb-badge-card
- relation-dagre-flow-tb-simple-circle-node
- sequence-ascending-stairs-3d-underline-text
- sequence-ascending-steps
- sequence-circular-simple
- sequence-color-snake-steps-horizontal-icon-line
- sequence-cylinders-3d-simple
- sequence-filter-mesh-simple
- sequence-funnel-simple
- sequence-horizontal-zigzag-underline-text
- sequence-mountain-underline-text
- sequence-pyramid-simple
- sequence-roadmap-vertical-plain-text
- sequence-roadmap-vertical-simple
- sequence-snake-steps-compact-card
- sequence-snake-steps-simple
- sequence-snake-steps-underline-text
- sequence-stairs-front-compact-card
- sequence-stairs-front-pill-badge
- sequence-timeline-rounded-rect-node
- sequence-timeline-simple
- sequence-zigzag-pucks-3d-simple
- sequence-zigzag-steps-underline-text

**模板选择建议：**

- 严格序列（过程/步骤/发展趋势）→ `sequence-*`
  - 时间线 → `sequence-timeline-*`
  - 楼梯图 → `sequence-stairs-*`
  - 路线图 → `sequence-roadmap-vertical-*`
  - 之字形路径 → `sequence-zigzag-*`
  - 圆形进度 → `sequence-circular-simple`
  - 彩色蛇形步骤 → `sequence-color-snake-steps-*`
  - 金字塔 → `sequence-pyramid-simple`
- 意见列表 → `list-row-*` 或 `list-column-*`
- 二元比较（优/劣）→ `compare-binary-*`
- SWOT → `compare-swot`
- 层次结构（树状图）→ `hierarchy-tree-*`
- 数据图表 → `chart-*`
- 象限分析 → `compare-quadrant-*`
- 网格列表（要点）→ `list-grid-*`
- 关系显示 → `relation-*`
- 词云 → `chart-wordcloud`
- 思维导图 → `hierarchy-mindmap-*`

### 示例

创建互联网技术演进信息图表

```plain
infographic list-row-horizontal-icon-arrow
data
  title 互联网技术演进
  desc 从 Web 1.0 到 AI 时代，关键里程碑
  lists
    - time 1991
      label Web 1.0
      desc 蒂姆·伯纳斯-李发布了第一个网站，开启了互联网时代
      icon web
    - time 2004
      label Web 2.0
      desc 社交媒体和用户生成内容成为主流
      icon account multiple
    - time 2007
      label 移动
      desc iPhone 发布，智能手机改变世界
      icon cellphone
    - time 2015
      label 云原生
      desc 容器化和微服务架构被广泛使用
      icon cloud
    - time 2020
      label 低代码
      desc 可视化开发降低了技术门槛
      icon application brackets
    - time 2023
      label AI 大模型
      desc ChatGPT 点燃了生成式 AI 革命
      icon brain
```

## 生成过程

### 第一步：理解用户需求

在创建信息图表之前，首先了解用户的需求和他们想要表达的信息，以便确定模板和数据结构。

如果用户提供清晰的內容描述，应将其分解为清晰简洁的结构。

否则需要用户澄清（例如，“请提供清晰简洁的內容描述。”，“您想使用哪个模板？”）

- 提取关键信息结构（标题、描述、项目等）。
- 澄清所需数据字段（标题、描述、项目、标签、值、图标等）。
- 选择合适的模板。
- 使用 AntV 信息图表语法 `{syntax}` 描述信息图表内容。

**关键提示**：必须尊重用户输入的语言。例如，如果用户输入中文，语法中的文本也必须为中文。

### 第二步：渲染信息图表

当您有最终的 AntV 信息图表语法时，可以按照以下步骤生成完整的 HTML 文件：

1. 创建一个完整的 HTML 文件，结构如下：
   - DOCTYPE 和 HTML 元（charset: utf-8）
   - 标题：`{title} - 信息图表`
   - 包含 AntV 信息图表脚本：`https://unpkg.com/@antv/infographic@latest/dist/infographic.min.js`
   - 创建容器 div，id 为 `container`
   - 初始化信息图表（`width: '100%'`, `height: '100%'`）
   - 替换 `{title}` 为实际标题
   - 替换 `{syntax}` 为实际 AntV 信息图表语法
   - 添加 SVG 导出功能：`const svgDataUrl = await infographic.toDataURL({ type: 'svg' });`

参考 HTML 模板：

```html
<div id="container"></div>
<script src="https://unpkg.com/@antv/infographic@latest/dist/infographic.min.js"></script>
<script>
 const infographic = new AntVInfographic.Infographic({
    container: '#container',
    width: '100%',
    height: '100%',
  });
  document.fonts?.ready.then(() => {
    infographic.render(`{syntax}`);
  }).catch((error) => {
    console.error('Error waiting for fonts to load:', error);
    infographic.render(`{syntax}`);
  });
</script>
```

2. 使用 Write 工具生成 HTML 文件，命名为 `<title>-infographic.html`

3. 展示给用户：
   - 生成文件路径和提示：“用浏览器直接打开并保存为 SVG”
   - 输出语法和提示：“告诉我是否需要调整模板/颜色/內容”

**注意**：HTML 文件必须包含：

- 通过导出按钮进行 SVG 导出
- 容器是响应式的，宽度和高度都是 100%
