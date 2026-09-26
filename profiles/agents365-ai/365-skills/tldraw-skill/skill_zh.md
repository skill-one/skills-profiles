# tldraw 白板图表

## 概述

使用 `@kitschpatrol/tldraw-cli` 将现代白板风格的图表生成 `.tldr` JSON 文件，并导出为 PNG/SVG。tldraw 生成干净的手绘美学图表，具有丰富的形状库和平滑的箭头路由——非常适合休闲或白板风格的可视化。

**格式：** `.tldr` JSON
**导出：** PNG, SVG (通过 `@kitschpatrol/tldraw-cli`)
**美学：** 默认为手绘白板风格；可通过 `font` 属性切换为干净字体。

## 何时使用

**明确触发：** 用户说 "图表"、"流程图"、"绘制"、"可视化"、"白板图表"、"tldraw 图表"、"架构图表"、"勾勒出这个"。

**主动触发：**

- 解释具有 3 个以上交互组件的系统
- 描述多步骤流程、数据流或管道
- 显示服务/模块之间的关系
- 架构概述、序列流、决策树、机器学习模型层

**何时跳过：** 简单列表或表格就足够了，用户想要一个精致的商业演示图表（更倾向于 drawio-skill），或者用户处于快速问答流程中。

**不要使用它——转而使用其他方式：**

- Logo / 纯色图形 / 填充图标：tldraw 没有不透明填充 (`solid` = 浅色；白底黑字无法再现) → 使用 drawio 技能或原始矢量文件。
- 精确的矢量几何或严格的（空心箭头）UML → drawio（或 plantuml 用于 UML）。
- 多个节点的自动布局 → mermaid（tldraw 需要手动坐标）。
- 对现有图像的像素精确复制 → 不是图表技能任务。

## 前置条件

```bash
# 安装 tldraw-cli
npm install -g @kitschpatrol/tldraw-cli

# 验证
tldraw --version
```

在 macOS、Windows 和 Linux 上工作完全相同。

**首次导出注意：** `tldraw export` 通过 pinned Chrome 构建（通过 puppeteer）进行渲染。首次导出可能会失败，提示 `Could not find Chrome (ver. <x>)`。错误会指明它需要的确切版本——安装一次，然后导出即可工作：

```bash
# 错误消息会指明版本；在此处替换它
npx puppeteer browsers install chrome@<version-from-error>
```

(安装到 `~/.cache/puppeteer`；每个 CLI 版本只需安装一次。)

## 工作流程

开始之前，评估用户的请求是否足够具体。如果关键细节缺失，请问 1-3 个专注的问题：

- **图表类型** — 哪个预设？(架构、流程图、序列、ML/DL、ERD、UML 或通用)
- **输出格式** — PNG (默认)、SVG？
- **输出位置** — 默认是用户的当前工作目录；尊重用户给出的任何明确路径（例如 "把它放在 `./artifacts/`"）。如果他们没有提到，就不要问。
- **范围/保真度** — 有多少个组件？任何特定的技术或标签？

如果请求已经指定了这些细节或明显简单（例如，"绘制 X 的流程图"），则跳过澄清。

1. **检查依赖项** — 验证 `tldraw --version` 成功；如果缺失，运行 `npm install -g @kitschpatrol/tldraw-cli`。
2. **规划** — 确定形状（每个节点的几何类型）、连接（带源/目标的箭头）、布局（TB 或 LR，按层/角色分组）。在编写 JSON 之前，先勾勒出坐标网格。
3. **生成** — 编写 `.tldr` JSON 文件。默认输出目录是用户的当前工作目录；如果用户指定了路径或目录（例如 `./artifacts/`），则先运行 `mkdir -p` 并在那里写入。将 PNG/SVG 导出的步骤 4 和 7 的相同目录选择应用于步骤 4 和 7。
4. **导出草稿** — 运行 CLI 生成 PNG 以供预览。
5. **自我检查** — 使用代理的内置视觉能力读取导出的 PNG，捕获明显问题，在显示给用户之前自动修复（需要支持视觉的模型，如 Claude Sonnet/Opus）。如果视觉不可用，则跳过此步骤。
6. **审查循环** — 将图像显示给用户，收集反馈，应用有针对性的 JSON 编辑，重新导出，重复直到获得批准。
7. **最终导出** — 将批准的版本导出到所有请求的格式；报告 `.tldr` 源文件和导出图像的文件路径。

### 步骤 5：自我检查

导出草稿 PNG 后，使用代理的视觉能力（例如，Claude 的图像输入）读取图像，并在显示给用户之前检查这些问题。如果代理不支持视觉，则跳过自我检查并直接显示 PNG。

tldraw 自己的 AI 代理会标记三个结构性缺陷——**文本溢出**（标签框太小）、**文本重叠**和**无家可归的箭头**（箭头有一个未连接的端点）。下面三行目标这些；从一开始就正确调整框大小（见“调整框以适应标签”），它们很少发生。

| 检查 | 查找内容 | 自动修复操作 |
| ------- | ----------------- | ----------------- |
| 文本溢出 | 标签溢出形状的边界，或者框看起来比设置的更高（tldraw 会自动增长尺寸不足的框） | 增加 `w`/`h` 以适应标签——见下文的尺寸公式 |
| 文本重叠 | 两个带文本的形状的标签接触或重叠，影响可读性 | 将形状分开 ≥200px |
| 无家可归的箭头 | 箭头的一端未连接到形状（悬浮） | 绑定两端：每个箭头的 `start` 和 `end` 都需要一个与现有形状匹配的 `boundShapeId` |
| 画布外形状 | 坐标为负或远离主组的形状 | 移动到靠近集群的正坐标 |
| 箭头形状重叠 | 箭头在视觉上穿过一个无关的形状 | 调整 `bend` 值或移动端点到不同的 `normalizedAnchor` 侧 |
| 堆叠的箭头 | 多个箭头在同一路径上重叠 | 在形状周长上分配 `normalizedAnchor`（使用不同的 x/y 值） |

- 最大 **2 个自我检查轮次**——如果两个修复后仍有问题，则直接显示给用户。
- 每次修复后重新导出并重新读取新的 PNG。

### 步骤 6：审查循环

自我检查后，显示导出的图像并要求用户提供反馈。

**有针对性的编辑规则**——对于每种反馈，应用最小的 JSON 修改：

| 用户请求 | JSON 编辑操作 |
| ------------- | ----------------- |
| 更改 X 的颜色 | 通过 `props.text` 匹配 X 找到形状，更新 `props.color` |
| 添加一个新节点 | 追加一个新的形状记录，位置靠近相关节点 |
| 删除一个节点 | 删除形状记录以及绑定到它的任何箭头记录 |
| 移动形状 X | 更新形状的 `x`/`y` 字段 |
| 调整形状 X 的大小 | 更新 `props.w`/`props.h` |
| 从 A 到 B 添加箭头 | 追加一个新的箭头记录，绑定到 A 和 B 的形状 ID |
| 更改标签文本 | 在匹配的形状或箭头上更新 `props.text` |
| 更改布局方向 | **完全再生**——重新规划网格并重建 |

**规则：**

- 对于单个元素更改：原地编辑现有的 JSON——保留先前的布局调整。
- 对于布局范围的更改（例如，交换 LR↔TB，“重新开始”）：重新生成完整的 JSON。
- 用相同的 `{name}.png` 每次迭代覆盖——不要创建 `v1`、`v2`、`v3` 文件。
- 应用编辑后，重新导出并显示更新后的图像。
- 循环继续直到用户说批准 / 完成 / LGTM。
- **安全阀：** 5 次迭代轮次后，建议用户在 tldraw.com 或桌面应用程序中打开 `.tldr` 文件进行精细调整。

---

## 文件格式

### 完整 .tldr 骨架

```json
{
  "tldrawFileFormatVersion": 1,
  "schema": {
    "schemaVersion": 1,
    "storeVersion": 4,
    "recordVersions": {
      "asset": {"version": 1, "subTypeKey": "type", "subTypeVersions": {"image": 2, "video": 2, "bookmark": 0}},
      "camera": {"version": 1},
      "document": {"version": 2},
      "instance": {"version": 17},
      "instance_page_state": {"version": 3},
      "page": {"version": 1},
      "shape": {"version": 3, "subTypeKey": "type", "subTypeVersions": {"group": 0, "embed": 4, "bookmark": 1, "image": 2, "text": 1, "draw": 1, "geo": 7, "line": 0, "note": 4, "frame": 0, "arrow": 1, "highlight": 0, "video": 1}},
      "instance_presence": {"version": 4},
      "pointer": {"version": 1}
    }
  },
  "records": [
    {"id": "document:document", "typeName": "document", "gridSize": 10, "name": "", "meta": {}},
    {"id": "page:page1", "typeName": "page", "name": "Page 1", "index": "a1", "meta": {}}
    /* 形状和箭头在这里 */
  ]
}
```

**关键规则：**

- `document:document` 和 `page:page1` 记录始终是必需的。
- 所有形状都放在页面记录之后的 `records` 数组中。
- 所有形状都有 `"parentId": "page:page1"`。
- 形状 ID 使用格式 `"shape:xxx"` 并具有唯一后缀（例如，`"shape:s1"`，`"shape:a1"`）。
- `index` 值是分数索引键。使用 `"a"` + **一个** 基于六进制的字符，按顺序：`"a0"`–`"a9"`，然后 `"aA"`–`"aZ"`，然后 `"aa"`–`"az"`（62 个有序键——足够任何正常图表使用）。
- **不要追加第二个字符：`"a10"` 无效。** 并且永远不要使用以 `"b"`/`"c"` 开头的（`"b1"`，`"c1"`，`"b0"`）——它们编码一个更长的整数部分，因此它们是格式不正确的分数键并触发 `invalidRecords`。坚持使用上述单个字符 `"a*"` 键。

---

## Geo 形状记录

```json
{
  "id": "shape:s1",
  "typeName": "shape",
  "type": "geo",
  "parentId": "page:page1",
  "index": "a1",
  "x": 100,
  "y": 100,
  "rotation": 0,
  "isLocked": false,
  "opacity": 1,
  "meta": {},
  "props": {
    "w": 180,
    "h": 60,
    "geo": "rectangle",
    "color": "blue",
    "labelColor": "black",
    "fill": "semi",
    "dash": "draw",
    "size": "m",
    "font": "draw",
    "text": "API Gateway",
    "align": "middle",
    "verticalAlign": "middle",
    "growY": 0,
    "url": ""
  }
}
```

### Geo 类型

| `geo` 值 | 用于 |
| ------------- | --------- |
| `rectangle` | 服务、模块、组件 |
| `ellipse` | 数据库、开始/结束节点 |
| `oval` | 圆形标签的起始/结束终止符（流程图） |
| `diamond` | 决策点 |
| `cloud` | 外部服务、基础设施 |
| `hexagon` | 事件中心、消息总线 |
| `triangle` | 网关、负载均衡器 |
| `star` | 高亮、关键特性 |
| `pentagon` | 阶段、里程碑 |
| `octagon` | 停止/终端/阻塞状态 |
| `trapezoid` | 手动操作、转换 |
| `rhombus` / `rhombus-2` | 平行四边形——输入步骤（左/右倾斜） |
| `arrow-right` / `arrow-left` / `arrow-up` / `arrow-down` | 方向流块、数据移动 |
| `x-box` | 失败/无效/拒绝状态（带 ✕ 的框） |
| `check-box` | 通过/验证/完成状态（带 ✓ 的框） |
| `heart` | 强调（技术图表中很少需要） |

所有 20 个 `geo` 值都是有效的；上面的列出了技术图表中有用的子集。

### 颜色面板

| `color` | 用于 |
| --------- | --------- |
| `blue` | 客户端、核心服务 |
| `green` | 成功、数据库、存储 |
| `orange` | 队列、事件总线、警告 |
| `red` | 外部 API、错误、警报 |
| `light-red` | 软警报、次要警告 |
| `violet` | 网关、安全、认证 |
| `yellow` | 决策、缓存 |
| `grey` | 中性、背景、遗留 |
| `light-blue` | 次要服务、元数据 |
| `light-violet` | 软认证/安全、次要网关 |
| `light-green` | 软成功、次要存储 |
| `white` | 空白/空节点、占位符（与 `fill: solid` 配合使用） |
| `black` | 标题、强调 |

完整面板（13）：`black`、`grey`、`light-violet`、`violet`、`blue`、`light-blue`、`yellow`、`orange`、`green`、`light-green`、`light-red`、`red`、`white`。

### 样式选项

| 属性 | 值 | 备注 |
| ---------- | -------- | ------- |
| `fill` | `semi`, `solid`, `none`, `pattern` | `semi` = 浅色填充（推荐） |
| `dash` | `draw`, `solid`, `dashed`, `dotted` | `draw` = 手绘默认 |
| `size` | `s`, `m`, `l`, `xl` | `m` = 默认 |
| `font` | `draw`, `sans`, `serif`, `mono` | `draw` = 默认白板样式 |

---

## 箭头记录

```json
{
  "id": "shape:a1",
  "typeName": "shape",
  "type": "arrow",
  "parentId": "page:page1",
  "index": "aG",
  "x": 0,
  "y": 0,
  "rotation": 0,
  "isLocked": false,
  "opacity": 1,
  "meta": {},
  "props": {
    "dash": "draw",
    "size": "m",
    "fill": "none",
    "color": "black",
    "labelColor": "black",
    "bend": 0,
    "start": {
      "type": "binding",
      "boundShapeId": "shape:s1",
      "normalizedAnchor": {"x": 0.5, "y": 1},
      "isExact": false
    },
    "end": {
      "type": "binding",
      "boundShapeId": "shape:s2",
      "normalizedAnchor": {"x": 0.5, "y": 0},
      "isExact": false
    },
    "arrowheadStart": "none",
    "arrowheadEnd": "arrow",
    "text": "",
    "font": "draw"
  }
}
```

### 箭头连接规则

- 箭头记录的 `x` 和 `y` 始终是 `0, 0`。
- 使用 `"type": "binding"` 与 `boundShapeId` 连接到特定形状。
- `normalizedAnchor` 指定箭头连接到目标形状的位置（0–1 范围）：
  - `{x: 0.5, y: 0}` = 顶部中心
  - `{x: 0.5, y: 1}` = 底部中心
  - `{x: 0, y: 0.5}` = 左侧中心
  - `{x: 1, y: 0.5}` = 右侧中心
  - `{x: 0.5, y: 0.5}` = 中心
- 在箭头属性中添加 `"text": "label"` 以进行标记连接。
- 使用 `"bend": 20`（或 `-20`）以轻微弯曲，避免与其他箭头重叠。
- 对于虚线/点线箭头（例如，异步流、可选链接），设置 `"dash": "dashed"` 或 `"dotted"`。
- 设置 `"spline": "cubic"` 以获得平滑的曲线箭头（默认 `"line"` 是直角/肘形）。对于跳过连接和后端边，很有用。

### 箭头头

`arrowheadStart` 和 `arrowheadEnd` 每个都接受以下 9 个值（在 `@kitschpatrol/tldraw-cli` 中全部渲染）：

| 值 | 看起来像 | 用于 |
| ------- | ----------- | --------- |
| `none` | (无头) | 单向箭头的开始 |
| `arrow` | 开放 V | 默认流方向 |
| `triangle` | 填充 ▶ | UML 继承 / "is-a" |
| `diamond` | 填充 ◆ | UML 组合 / 聚合（在所有者端） |
| `dot` | ● | 序列图消息端点 |
| `square` | ■ | 终端/固定端点 |
| `bar` | \| | "停止" / 边界标记 |
| `pipe` | \|\| | 替代边界标记 |
| `inverted` | 空心 V | 淡化方向 |

默认箭头使用 `"arrowheadStart": "none"`, `"arrowheadEnd": "arrow"`. 对于双向链接，将两端都设置为 `"arrow"`。

### 在形状上分布箭头

当多个箭头连接到同一个形状时，为防止堆叠，分配不同的 `normalizedAnchor` 点：

| 位置 | x | y | 使用时 |
| ---------- | --- | --- | ---------- |
| 顶部中心 | 0.5 | 0 | 连接到上方的节点 |
| 顶部左侧 | 0.25 | 0 | 从顶部开始的第二个连接 |
| 顶部右侧 | 0.75 | 0 | 从顶部开始的第三个连接 |
| 右侧中心 | 1 | 0.5 | 连接到右侧的节点 |
| 底部中心 | 0.5 | 1 | 连接到下方的节点 |
| 左侧中心 | 0 | 0.5 | 连接到左侧的节点 |

**规则：** 如果一个形状在一侧有 N 个连接，请均匀分布（例如，底部有 3 个连接 → x = 0.25, 0.5, 0.75）。

### 在两个相同节点之间有多个箭头

上面的箭头分布规则用于连接到不同节点的箭头。当 **N 个箭头连接到相同的两个节点**（例如，双向请求/响应，或 A↔B 的多个关系）时，锚点无法分离它们——相反，应对称地分布 `bend` 值以使箭头扇形展开到不同的弧线：

- 选择一个最大 `bend` 量（≈ 30–60；节点相距较远时，使用更大的值）。
- 为 N 个箭头分配均匀间隔的 `bend` 值，从 `-amount` 到 `+amount`：
  - **2 个箭头** → `bend: -amount`, `bend: +amount`
  - **3 个箭头** → `bend: -amount`, `0`, `+amount`
  - 一般：`bend[i] = -amount + i * (2*amount / (N-1)` for `i = 1..N-1`
- 一个直角箭头加上一个弯曲的箭头（`bend: 0` 和 `bend: 40`）对于请求/响应对来说，可读性清晰。

---

## 容器 & 注释形状

除了 `geo` 和 `arrow` 之外，还有两种形状类型对于技术图表很有用。

### Frame（带标签的容器——层、子系统、泳道）

`frame` 是一个原生的矩形容器，带有标题。使用它将层或子系统分组，带有可见边界；堆叠多个 `frame` 来近似泳道。

```json
{
  "id": "shape:frame1", "typeName": "shape", "type": "frame",
  "parentId": "page:page1", "index": "a1",
  "x": 60, "y": 60, "rotation": 0, "isLocked": false, "opacity": 1, "meta": {},
  "props": { "w": 360, "h": 220, "name": "Backend Tier", "color": "black" }
}
```

- `props.name` 是显示在 `frame` 左上角的标题。
- **子形状设置 `"parentId": "shape:frame1"`**（不是 `page:page1`），并且它们的 `x`/`y` 是相对于 `frame` 的左上角，而不是页面。位于 `x: 40, y: 60` 的子形状位于框内 40px 远，下方 60px 远。

`frame` 渲染为干净的（非手绘）矩形——适合结构分组。箭头仍然可以正常绑定到 `frame` 之外。

### Note（便签注释/标注）

`note` 是一个便签——非常适合 TODO、标注和叠加在图表上的注释。

```json
{
  "id": "shape:n1", "typeName": "shape", "type": "note",
  "parentId": "page:page1", "index": "a4",
  "x": 480, "y": 80, "rotation": 0, "isLocked": false, "opacity": 1, "meta": {},
  "props": { "color": "yellow", "size": "m", "text": "TODO: 添加重试\n逻辑在这里",
    "font": "draw", "align": "middle", "verticalAlign": "middle",
    "growY": 0, "fontSizeAdjustment": 0, "url": "", "scale": 1, "labelColor": "black" }
}
```

- 注释没有 `w`/`h`——它是一个固定的方形（~200px）的便签，会根据较长的文本自动增长。不要添加 `w`/`h`。
- `yellow` 是经典的便签颜色；任何面板颜色都可以使用。
- 尽量少用注释——用于图表的注释，而不是作为主要节点（使用 `geo`）。

---

## 索引排序规则

索引控制 z-order（堆叠）。使用此顺序：

```
a1, a2, a3, a4, a5, a6, a7, a8, a9,
aA, aB, aC, aD, aE, aF, aG, aH, aI, aJ, aK, aL, aM,
aN, aO, aP, aQ, aR, aS, aT, aU, aV, aW, aX, aY, aZ,
aa, ab, ac, ... az          ← 超过 aZ 后继续；永远不要 "a10"
```

- `geo` 形状首先：`a1` 通过 `aF`（或需要多少）。
- 箭头形状之后：`aG`, `aH`, 等。
- 每个形状必须具有 **唯一的** 索引。

---

## 布局技巧

**间距——根据复杂程度缩放：**

| 图表复杂度 | 节点 | 水平间距 | 垂直间距 |
| ------------------- | ------- | ---------------- | -------------- |
| 简单 | ≤5 | 200px | 150px |
| 中等 | 6–10 | 280px | 200px |
| 复杂 | >10 | 350px | 250px |

**调整框以适应标签（在自我检查之前做这个）**：`draw` 字体很宽。根据标签计算 `w`/`h` 以确保文本不会剪切。对于默认 `draw` 字体，每个字符的宽度和行高近似值：

| `size` | 字符宽度 (px) | 行高 (px) |
| -------- | ----------------- | ------------------ |
| `s` | 11 | 18 |
| `m` (默认) | 15 | 28 |
| `l` | 22 | 40 |
| `xl` | 32 | 56 |

使用 `padding = 16` 在每侧：

- `w = ceil(longest_line_chars * char_width + 2*padding)`, 然后向上取整到下一个 10 的倍数。
- `h = ceil(num_lines * line_height + 2*padding)`, 四舍五入到 10 的倍数。

示例：大小为 `m` 的框标记为 `"API Gateway"`（11 个字符，1 行）→ `w ≈ 11*15 + 32 = 197 → 200`, `h ≈ 28 + 32 = 60`.多行标签（带有 `\n`）计算最长行的 `w` 和行数的 `h`。稍微偏大一点——额外的填充看起来很好，太窄的框会硬换行。单词在字母中间换行。

**为什么这很重要：** 如果框太小，tldraw 会默默地 **增长它的高度**（它设置形状的 `growY`）——所以框最终比 `h` 你写的要大，会与它下面的内容冲突。从一开始就正确调整 `w`/`h` 可以保持 `growY` 为 0 并保持你的布局完整。这是导出后 "图表看起来拥挤 / 框重叠" 最常见的原因。

**路由走廊：** 在形状行/列之间，留出额外的 ~80px 空间，箭头可以在不穿过其他形状的情况下路由。永远不要将形状放在箭头需要穿越的间隙中。

**网格对齐：** 将所有 `x`, `y`, `w`, `h` 值对齐到 **10 的倍数**——这匹配 tldraw 的默认 `gridSize: 10` 并使手动编辑更容易。

**一般规则：**

- 在分配 x/y 坐标之前规划网格——在分配之前先在脑海中勾勒出节点位置。
- 将相关的节点分组到同一水平或垂直带内。
- 将高度连接的 "中心" 节点放置在中央，以便箭头向外辐射而不是交叉。
- 对于跨越多个下游服务的宽形状（如跨越多个下游服务的 API Gateway），设置 `w` 以覆盖整个跨度。
- 将子节点在父节点下方居中对齐（相同的中心 x）以避免对角线路由。
- **事件总线模式：** 将总线放置在服务行的 **中心**，而不是下方——服务在两侧都可以用短的水平箭头 (`normalizedAnchor.x = 1` 左侧, `0` 右侧) 到达它，消除交叉。

**水平连接永远不会跨越同一行中的垂直节点；用于对等和发布连接。**

**避免箭头形状重叠：**

- 在最终确定坐标之前，在脑海中勾勒出每个箭头的路径——如果它必须穿过一个无关的形状，则移动形状或使用 `bend` 使其绕过。
- 对于树形/层次结构布局：将节点分配到层（行），仅在相邻层之间连接以最小化交叉。

**对于星形/中心布局：** 将中心放置在 hub，卫星围绕它——箭头保持短而径向。

**导出命令**

```bash
# 检查 CLI 版本
tldraw --version

# PNG 以 2 倍缩放（推荐）——输出为 ./
tldraw export diagram.tldr -f png --scale 2 -o ./

# SVG — 输出为 ./
tldraw export diagram.tldr -f svg -o ./

# 透明背景
tldraw export diagram.tldr -f png --scale 2 --transparent -o ./

# 暗色主题
tldraw export diagram.tldr -f png --scale 2 --dark -o ./

# 自定义输出目录（例如 CI 艺术目录）——如果缺失，则创建它，然后导出到那里
mkdir -p ./artifacts && tldraw export diagram.tldr -f png --scale 2 -o ./artifacts/
```

**注意：** `-o` 是输出 **目录**，不是文件路径。输出文件以输入文件命名（`diagram.tldr` → `diagram.png`）。

### 导出后自动启动

提供将 `.tldr` 文件在用户的默认 tldraw 查看器/编辑器中打开：

| OS | 命令 |
| ---- | --------- |
| macOS | `open diagram.tldr` |
| Linux | `xdg-open diagram.tldr` |
| Windows | `start diagram.tldr` |

或者上传到 <https://tldraw.com>（将 `.tldr` 文件拖放到）以供浏览器编辑。

---

## 常见错误

| 错误 | 修复 |
| --------- | ----- |
| `tldraw` 命令未找到 | 运行 `npm install -g @kitschpatrol/tldraw-cli` |
| 导出时 `Could not find Chrome (ver. X)` | 安装 pinned 构建：`npx puppeteer browsers install chrome@X`（使用错误中指定的确切版本） |
| 导出时 `invalidRecords` | 使用单字符 `a` 键 (`a1`…`a9`, `aA`…`aZ`, `aa`…`az`）；`a10`, `b1`, `c1` 是格式不正确的分数键并触发 `invalidRecords`。坚持使用上述单个字符 `"a*"` 键。

---

## 降级链

当工具不可用时，优雅地降级：

| 情景 | 行为 |
| ---------- | ---------- |
| `tldraw-cli` 缺失 | 仅生成 `.tldr` JSON；指示用户将 `.tldr` 文件拖放到 <https://tldraw.com> 或安装 CLI |
| 视觉不可用以进行自我检查 | 跳过自我检查（步骤 5）；直接显示用户导出的 PNG |
| 导出失败 | 验证 JSON 与 `python3 -m json.tool file.tldr > /dev/null`；交付 `.tldr` 文件并建议用户在 tldraw.com 中打开以进行精细调整 |
