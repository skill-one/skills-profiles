# 图表生成器

创建专业的 SVG 图表，支持多种图表类型。所有输出都是单个自包含的 `.svg` 文件，包含嵌入的样式和字体。

## 支持的图表类型

| 类型 | 使用场景 | 主要特征 |
|------|-------------|-------------------|
| **架构** | 系统组件及关系 | 分组的方框、连接箭头、区域边界 |
| **流程图** | 决策逻辑、流程步骤 | 菱形决策、圆角步骤方框、方向流 |
| **时序** | 按时间顺序排列的交互 | 垂直生命线、水平消息、激活条 |
| **结构** | 类图、ER 图、组织结构图 | 分隔的方框、类型关系（继承、组合） |
| **思维导图** | 头脑风暴、主题探索 | 中心节点、辐射分支、有机布局 |
| **时间线** | 按时间顺序排列的事件 | 水平/垂直轴、事件标记、时间段 |
| **说明** | 概念解释、比较 | 自由布局、图标、注释、视觉隐喻 |
| **状态机** | 状态转换、生命周期 | 圆角状态节点、标记转换、开始/结束标记 |
| **数据流** | 数据转换管道 | 处理气泡、数据存储、外部实体 |

## 设计系统

### 色彩方案

组件类别的语义色彩：

| 类别 | 填充 (rgba) | 描边 | 使用场景 |
|----------|-------------|--------|---------|
| 主要 | `rgba(8, 51, 68, 0.4)` | `#22d3ee` (青色) | 前端、用户界面、输入 |
| 次要 | `rgba(6, 78, 59, 0.4)` | `#34d399` (祖母绿) | 后端、服务、处理 |
| 三级 | `rgba(76, 29, 149, 0.4)` | `#a78bfa` (紫色) | 数据库、存储、持久化 |
| 强调 | `rgba(120, 53, 15, 0.3)` | `#fbbf24` (琥珀色) | 云服务、基础设施、区域 |
| 警报 | `rgba(136, 19, 55, 0.4)` | `#fb7185` (玫瑰色) | 安全、错误、警告 |
| 连接器 | `rgba(251, 146, 60, 0.3)` | `#fb923c` (橙色) | 总线、队列、中间件 |
| 中性 | `rgba(30, 41, 59, 0.5)` | `#94a3b8` (石板色) | 外部、通用、未知 |
| 高亮 | `rgba(59, 130, 246, 0.3)` | `#60a5fa` (蓝色) | 激活状态、焦点、当前步骤 |

对于流程图和时序图，按角色（参与者、决策、流程）分配颜色，而不是按技术。

### 字体

使用嵌入的 SVG `@font-face` 或系统等宽字体回退：

```svg
<style>
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&amp;display=swap');
  text { font-family: 'JetBrains Mono', 'SF Mono', 'Cascadia Code', monospace; }
</style>
```

按角色分配字体大小：
- **标题:** 16px，权重 700
- **组件名称:** 11-12px，权重 600
- **子标签/描述:** 9px，权重 400，颜色 `#94a3b8`
- **注释/笔记:** 8px，权重 400
- **微标签（箭头上）:** 7-8px

### 核心视觉元素

**背景:** `#0f172a` (石板900) 带有细微网格：
```svg
<defs>
  <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
    <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#1e293b" stroke-width="0.5"/>
  </pattern>
</defs>
<rect width="100%" height="100%" fill="#0f172a"/>
<rect width="100%" height="100%" fill="url(#grid)"/>
```

**箭头标记（标准）:**
```svg
<marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
  <polygon points="0 0, 10 3.5, 0 7" fill="#64748b"/>
</marker>
```

**彩色箭头标记 — 按需创建每个颜色:**
```svg
<marker id="arrow-cyan" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
  <polygon points="0 0, 10 3.5, 0 7" fill="#22d3ee"/>
</marker>
```

**开放箭头标记（用于异步/返回消息）:**
```svg
<marker id="arrow-open" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
  <polyline points="0 0, 10 3.5, 0 7" fill="none" stroke="#64748b" stroke-width="1.5"/>
</marker>
```

### SVG 结构与分层

按以下顺序绘制元素以获得正确的 z-排序（SVG 从后向前绘制）：

1. 背景填充 + 网格图案
2. 区域/分组边界（虚线轮廓）
3. 连接箭头和线条
4. 不透明遮罩矩形（与组件方框位置相同，`fill="#0f172a"`）
5. 组件方框（半透明填充 + 描边）
6. 文本标签
7. 图例（右下角或底部区域，所有边界外）
8. 标题块（左上角）

不透明遮罩矩形技巧至关重要 — 没有它，半透明组件填充会显示箭头下方：
```svg
<!-- 遮罩层：不透明背景以隐藏箭头 -->
<rect x="100" y="100" width="160" height="60" rx="6" fill="#0f172a"/>
<!-- 视觉层：样式化的组件 -->
<rect x="100" y="100" width="160" height="60" rx="6" fill="rgba(8,51,68,0.4)" stroke="#22d3ee" stroke-width="1.5"/>
<text x="180" y="125" fill="white" font-size="11" font-weight="600" text-anchor="middle">API 网关</text>
<text x="180" y="141" fill="#94a3b8" font-size="9" text-anchor="middle">Kong / Nginx</text>
```

### 间距规则

这些规则防止重叠 — 严格遵循：

- **组件方框高度:** 50-70px（标准），80-120px（大/复杂）
- **组件之间的最小间隙:** 垂直 40px，水平 30px
- **箭头标签间隙:** 距离任何方框边缘 10px
- **区域边界填充:** 包含组件的内部边缘周围 20px
- **图例位置:** 至少低于最低图表元素 20px
- **标题块:** 距离左上角 20px，图表内容区域外
- **viewBox:** 始终扩展以适应所有内容 + 所有边 30px 填充

### 组件模式

**标准方框（服务/流程）:**
```svg
<rect x="X" y="Y" width="160" height="60" rx="6" fill="#0f172a"/>
<rect x="X" y="Y" width="160" height="60" rx="6" fill="FILL" stroke="STROKE" stroke-width="1.5"/>
<text x="CX" y="Y+24" fill="white" font-size="11" font-weight="600" text-anchor="middle">Name</text>
<text x="CX" y="Y+40" fill="#94a3b8" font-size="9" text-anchor="middle">description</text>
```

**决策菱形（流程图）:**
```svg
<g transform="translate(CX, CY)">
  <polygon points="0,-35 50,0 0,35 -50,0" fill="#0f172a"/>
  <polygon points="0,-35 50,0 0,35 -50,0" fill="rgba(120,53,15,0.3)" stroke="#fbbf24" stroke-width="1.5"/>
  <text y="4" fill="white" font-size="10" font-weight="600" text-anchor="middle">Condition?</text>
</g>
```

**数据库圆柱体:**
```svg
<g transform="translate(X, Y)">
  <rect x="0" y="10" width="120" height="50" rx="2" fill="#0f172a"/>
  <ellipse cx="60" cy="10" rx="60" ry="12" fill="#0f172a"/>
  <ellipse cx="60" cy="60" rx="60" ry="12" fill="#0f172a"/>
  <rect x="0" y="10" width="120" height="50" fill="rgba(76,29,149,0.4)"/>
  <ellipse cx="60" cy="10" rx="60" ry="12" fill="rgba(76,29,149,0.4)" stroke="#a78bfa" stroke-width="1.5"/>
  <ellipse cx="60" cy="60" rx="60" ry="12" fill="rgba(76,29,149,0.4)" stroke="#a78bfa" stroke-width="1.5"/>
  <line x1="0" y1="10" x2="0" y2="60" stroke="#a78bfa" stroke-width="1.5"/>
  <line x1="120" y1="10" x2="120" y2="60" stroke="#a78bfa" stroke-width="1.5"/>
  <text x="60" y="40" fill="white" font-size="11" font-weight="600" text-anchor="middle">PostgreSQL</text>
</g>
```

**区域边界:**
```svg
<rect x="X" y="Y" width="W" height="H" rx="12" fill="none" stroke="#fbbf24" stroke-width="1" stroke-dasharray="8,4"/>
<text x="X+12" y="Y+16" fill="#fbbf24" font-size="9" font-weight="600">AWS us-east-1</text>
```

**安全组:**
```svg
<rect x="X" y="Y" width="W" height="H" rx="8" fill="none" stroke="#fb7185" stroke-width="1" stroke-dasharray="4,4"/>
<text x="X+10" y="Y+14" fill="#fb7185" font-size="8" font-weight="500">VPC / 安全组</text>
```

## 类型特定布局指南

确定此 `SKILL.md` 文件的目录路径为 `{baseDir}`。开始布局前，读取参考文件。参考文件位于 `{baseDir}/references/`，包含详细的布局算法和示例。

### 架构图
→ 读取 `{baseDir}/references/architecture.md`

要点：从左到右或从上到下的数据流。将相关服务分组在区域边界内。使用总线/连接器在层之间连接。将数据库放置在底部或右侧。

### 流程图
→ 读取 `{baseDir}/references/flowchart.md`

要点：从上到下的主要流程。菱形用于决策，退出箭头上标有 Yes/No 标签。圆角矩形用于开始/结束。使用高亮颜色表示成功路径。

### 时序图
→ 读取 `{baseDir}/references/sequence.md`

要点：参与者作为顶部的方框，垂直虚线生命线，水平箭头表示消息（实线=同步，虚线=返回）。时间向下流动。激活条显示处理。如果复杂，编号消息。

### 结构图
→ 读取 `{baseDir}/references/structural.md`

要点：分隔的方框（类图：名称/属性/方法）。关系线：实线填充菱形=组合，实线空菱形=聚合，虚线箭头=依赖，实线三角形=继承。

### 思维导图
自由辐射布局，从中心概念开始。使用有机曲线（`<path>` 带三次贝塞尔曲线）作为分支。使用调色板变化分支颜色。中心节点字体较大，向外逐渐减小。

### 时间线
水平或垂直轴线。事件标记为圆形或菱形。描述文本偏移到交替两侧以避免重叠。使用颜色对事件类型进行分类。

### 状态机
圆角矩形状态，双边框表示复合状态。填充圆圈表示初始状态，靶心表示最终状态。曲线箭头表示自转换。用 `event [guard] / action` 格式标记所有转换。

## 输出规则

1. 输出一个 **单个 `.svg` 文件** — 不依赖外部依赖，仅 Google Fonts 导入
2. 设置 `viewBox` 以适应所有内容并带有 30px 填充；**不要**设置固定的 `width`/`height` 属性（让 SVG 响应式缩放）
3. 在根 `<svg>` 元素上包含 `xmlns="http://www.w3.org/2000/svg"`
4. 将所有 `<style>`、`<defs>`、标记和图案放在 SVG 顶部
5. 使用 `text-anchor="middle"` 对齐居中标签；确保文本不会溢出方框
6. **中文文本支持:** 当标签包含中文字符时，使用 `font-family: 'JetBrains Mono', 'Noto Sans SC', 'PingFang SC', sans-serif'` 并增加方框宽度 — CJK 字符较宽
7. **保存位置:** 如果输入是文件，保存到 `{inputFileDir}/diagram/`。否则保存到 `{projectDir}/diagram/{topic-slug}/`。如果不存在，则创建目录

## 脚本

确定此 `SKILL.md` 文件的目录路径为 `{baseDir}`。脚本路径：`{baseDir}/scripts/main.ts`。

解析 `${BUN_X}` 运行时：如果安装了 `bun` → `bun`；如果可用 `npx` → `npx -y bun`；否则建议安装 bun。

### SVG → @2x PNG

保存 SVG 后，将其转换为 @2x PNG：

```bash
${BUN_X} {baseDir}/scripts/main.ts <svg-path> [options]
```

选项：
- `-s, --scale <n>` — 缩放因子（默认：2）
- `-o, --output <path>` — 自定义输出路径（默认：`<input>@2x.png`）
- `--json` — JSON 输出

## 流程

1. 从用户请求中识别图表类型
2. 如果该类型存在，读取相关的参考文件
3. 规划布局：列出所有组件，确定分组和流方向，计算位置
4. 按上述顺序绘制 SVG
5. 验证间距规则 — 无重叠，图例在边界外，viewBox 足够大
6. 保存 SVG 文件
7. 运行 `${BUN_X} {baseDir}/scripts/main.ts <svg-path>` 生成 @2x PNG
8. 向用户展示这两个文件
