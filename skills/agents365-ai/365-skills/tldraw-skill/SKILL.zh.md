---
name: tldraw-skill
description: 当用户请求图表、流程图、架构图或可视化时使用。在解释包含3个或更多组件的系统、复杂数据流或从视觉呈现中受益的关系时，也应主动使用。生成 .tldr JSON 文件，并使用 @kitschpatrol/tldraw-cli 本地导出为 PNG/SVG。
---

# tldraw 白板图表

## 概述

生成现代白板风格的图表，以 `.tldr` JSON 文件格式保存，并使用 `@kitschpatrol/tldraw-cli` 导出为 PNG/SVG。tldraw 生成干净的手绘美学图表，具有丰富的形状库和流畅的箭头路由——非常适合休闲或白板风格的可视化。

**格式：** `.tldr` JSON
**导出：** PNG, SVG (通过 `@kitschpatrol/tldraw-cli`)
**美学：** 默认为手绘白板风格；可通过 `font` 属性切换为干净字体。

## 何时使用

**明确触发：** 用户说“图表”、“流程图”、“绘制”、“可视化”、“白板图表”、“tldraw 图表”、“架构图表”、“勾勒出这个”。

**主动触发：**

- 解释具有 3 个以上交互组件的系统
- 描述多步骤流程、数据流或管道
- 显示服务/模块之间的关系
- 架构概述、序列流、决策树、机器学习模型层

**跳过使用场景：** 简单列表或表格就足够时，用户想要一个精制的商业演示图表（优先考虑 drawio-skill），或用户处于快速问答流程中。

**不使用它的情况——转而使用其他方式：**

- Logo / 实心色图形 / 填充图标：tldraw 没有**不透明填充**（`solid` = 浅色；白底深色无法再现）→ 使用 **drawio** 技能或原始矢量文件。
- 精确的矢量几何或严格的（空心箭头）UML → **drawio**（或 **plantuml** 用于 UML）。
- 多节点自动布局 → **mermaid**（tldraw 需要手动坐标）。
- 像素精确的现有图像副本 → 不是图表技能任务。

## 前置条件

```bash
# 安装 tldraw-cli
npm install -g @kitschpatrol/tldraw-cli

# 验证
tldraw --version
```

在 macOS、Windows 和 Linux 上工作完全相同。

**首次导出注意：** `tldraw export` 通过 puppeteer 渲染固定版本的 Chrome。首次导出可能会因 `Could not find Chrome (ver. <x>)` 而失败。错误会命名它需要的确切版本——安装一次，然后导出即可工作：

```bash
# 错误消息命名了版本；在此处替换它
npx puppeteer browsers install chrome@<version-from-error>
```

(安装到 `~/.cache/puppeteer`；每个 CLI 版本只需安装一次。)

## 工作流程

开始之前，评估用户的请求是否足够具体。如果关键细节缺失，请问 1-3 个专注的问题：

- **图表类型** — 哪个预设？（架构、流程图、序列、ML/DL、ERD、UML 或通用）
- **输出格式** — PNG（默认）、SVG？
- **输出位置** — 默认是用户的当前工作目录；尊重用户给出的任何明确路径（例如 "放在 `./artifacts/` 中"）。如果他们没有提到，不要询问。
- **范围/保真度** — 有多少组件？是否有任何特定的技术或标签？

如果请求已经指定了这些细节或显然很简单（例如，“绘制 X 的流程图”），则跳过澄清。

1. **检查依赖项** — 验证 `tldraw --version` 成功；如果缺失，运行 `npm install -g @kitschpatrol/tldraw-cli`。
2. **规划** — 确定形状（每个节点的几何类型）、连接（带源/目标的箭头）和布局（TB 或 LR，按层/角色分组）。在编写 JSON 之前绘制坐标网格。
3. **生成** — 编写 `.tldr` JSON 文件。默认输出目录是用户的当前工作目录；如果用户指定了路径或目录（例如 `./artifacts/`），首先运行 `mkdir -p` 并在那里写入。将相同的目录选择应用于步骤 4 和 7 中的 PNG/SVG 导出。
4. **导出草稿** — 运行 CLI 生成一个用于预览的 PNG。
5. **自我检查** — 使用代理的内置视觉功能读取导出的 PNG，捕获明显问题，在向用户展示之前自动修复（需要支持视觉的模型，如 Claude Sonnet/Opus）。如果视觉不可用，跳过此步骤。
6. **审查循环** — 向用户展示图像，收集反馈，应用有针对性的 JSON 编辑，重新导出，重复直到批准。
7. **最终导出** — 将批准的版本导出到所有请求的格式；报告 `.tldr` 源文件和导出图像的文件路径。

### 步骤 5：自我检查

导出草稿 PNG 后，使用代理的视觉功能（例如 Claude 的图像输入）读取图像，并在向用户展示之前检查这些问题。如果代理不支持视觉，直接展示 PNG。

tldraw 的 AI 代理标记了三个结构缺陷——**文本溢出**（标签框太小）、**文本重叠** 和 **无家可归的箭头**（一个未连接的箭头端点）。下表中的前三个行针对这些问题；从一开始正确调整框大小（见“调整框以适应标签”），它们很少发生。

| 检查 | 查找内容 | 自动修复操作 |
| ------- | ----------------- | ----------------- |
| 文本溢出 | 标签溢出形状边界，或框看起来比设置的更高（tldraw 会自动扩展undersized box） | 增加 `w`/`h` 以适应标签——见下文的调整大小公式 |
| 文本重叠 | 两个带文本形状的标签接触或重叠，影响可读性 | 将形状分开 ≥200px |
| 无家可归的箭头 | 一个端点未连接到形状的箭头（漂浮） | 绑定两端：每个箭头的 `start` 和 `end` 需要一个与现有形状匹配的 `boundShapeId` |
| 画布外形状 | 坐标为负或远离主组的形状 | 移动到靠近集群的正坐标 |
| 箭头形状重叠 | 箭头在视觉上穿过无关的形状 | 调整 `bend` 值或移动端点到不同的 `normalizedAnchor` 侧 |
| 堆叠的箭头 | 在同一路径上重叠的多个箭头 | 在形状周长上分配 `normalizedAnchor`（使用不同的 x/y 值） |

- 最大 **2 个自我检查轮次**——如果两个修复后仍有问题，无论如何都向用户展示。
- 每次修复后重新导出并重新读取新的 PNG。

### 步骤 6：审查循环

自我检查后，向用户展示导出的图像并请求反馈。

**有针对性的编辑规则**——对于每种类型的反馈，应用最小的 JSON 更改：

| 用户请求 | JSON 编辑操作 |
| ------------- | ----------------- |
| 更改 X 的颜色 | 通过 `props.text` 匹配 X 找到形状，更新 `props.color` |
| 添加新节点 | 追加一个新的形状记录，使用下一个可用索引，靠近相关节点 |
| 删除节点 | 删除形状记录及其任何绑定到它的箭头记录 |
| 移动形状 X | 更新形状的 `x`/`y` 字段 |
| 调整形状 X 的大小 | 更新 `props.w`/`props.h` |
| 添加从 A 到 B 的箭头 | 追加一个新的箭头记录，绑定到 A 和 B 的形状 ID |
| 更改标签文本 | 在匹配的形状或箭头上更新 `props.text` |
| 更改布局方向 | **完全再生**——重新规划网格并重新构建 |

**规则：**

- 对于单元素更改：原地编辑现有 JSON——保留先前的布局调整。
- 对于布局范围更改（例如，交换 LR↔TB，“重新开始”）：重新生成完整 JSON。
- 每次迭代覆盖相同的 `{name}.png`——不要创建 `v1`、`v2`、`v3` 文件。
- 应用编辑后，重新导出并展示更新后的图像。
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
    /* 形状和箭头在此处添加 */
  ]
}
```

**关键规则：**

- `document:document` 和 `page:page1` 记录**始终**需要。
- 所有形状都在页面记录后的 `records` 数组中。
- 所有形状都有 `"parentId": "page:page1"`。
- 形状 ID 使用格式 `"shape:xxx"` 并具有唯一后缀（例如 `"shape:s1"`，`"shape:a1"`）。
- `index` 值是分数索引键。使用 `"a"` + **一个**基 62 字符，按顺序：`"a0"`–`"a9"`，然后 `"aA"`–`"aZ"`，然后 `"aa"`–`"az"`（62 个有序键——足够任何正常图表使用）。
- **不要追加第二个字符：`"a10"` 无效。** 并且永远不要使用以 `"b"`/`"c"` 开头的（`"b1"`，`"c1"`，`"b0"`）——它们编码更长的整数部分，因此它们是格式错误的分数键并触发 `invalidRecords`。坚持使用上述单个字符 `"a*"` 键。

---

## 几何形状记录

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

### 几何类型

| `geo` 值 | 用于 |
| ------------- | --------- |
| `rectangle` | 服务、模块、组件 |
| `ellipse` | 数据库、开始/结束节点 |
| `oval` | 药丸形状的流程图开始/结束终止符 |
| `diamond` | 决策点 |
| `cloud` | 外部服务、基础设施 |
| `hexagon` | 事件中心、消息总线 |
| `triangle` | 网关、负载均衡器 |
| `star` | 高亮、关键功能 |
| `pentagon` | 阶段、里程碑 |
| `octagon` | 停止/终端/阻塞状态 |
| `trapezoid` | 手动操作、转换 |
| `rhombus` / `rhombus-2` | 平行四边形——I/O 步骤（左/右倾斜） |
| `arrow-right` / `arrow-left` / `arrow-up` / `arrow-down` | 方向流块、数据移动 |
| `x-box` | 失败/无效/拒绝状态（带 ✕ 的框） |
| `check-box` | 通过/验证/完成状态（带 ✓ 的框） |
| `heart` | 装饰（技术图表中很少需要） |

所有 20 个 `geo` 值都是有效的；上述是技术图表的有用子集。

### 色彩调色板

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

完整调色板（13）：`black`，`grey`，`light-violet`，`violet`，`blue`，`light-blue`，`yellow`，`orange`，`green`，`light-green`，`light-red`，`red`，`white`。

### 样式选项

| 属性 | 值 | 备注 |
| ---------- | -------- | ------- |
| `fill` | `semi`，`solid`，`none`，`pattern` | `semi` = 淡色填充（推荐） |
| `dash` | `draw`，`solid`，`dashed`，`dotted` | `draw` = 手绘默认 |
| `size` | `s`，`m`，`l`，`xl` | `m` = 默认 |
| `font` | `draw`，`sans`，`serif`，`mono` | `draw` = 默认白板样式 |

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

- 箭头记录 `x` 和 `y` 始终是 `0, 0`。
- 使用 `"type": "binding"` 并 `boundShapeId` 连接到特定形状。
- `normalizedAnchor` 指定箭头连接到目标形状的位置（0–1 范围）：
  - `{x: 0.5, y: 0}` = 顶部中心
  - `{x: 0.5, y: 1}` = 底部中心
  - `{x: 0, y: 0.5}` = 左侧中心
  - `{x: 1, y: 0.5}` = 右侧中心
  - `{x: 0.5, y: 0.5}` = 中心
- 在箭头属性中添加 `"text": "label"` 用于带标签的连接。
- 使用 `"bend": 20`（或 `-20`）进行轻微弯曲以避免与其他箭头重叠。
- 对于虚线/点线箭头（例如异步流、可选链接），设置 `"dash": "dashed"` 或 `"dotted"`。
- 设置 `"spline": "cubic"` 用于平滑曲线箭头（默认 `"line"` 是直角/肘形）。适用于跳过连接和后向边。

### 箭头头

`arrowheadStart` 和 `arrowheadEnd` 每个都接受以下 9 个值（所有在 `@kitschpatrol/tldraw-cli` 中渲染）：

| 值 | 看起来像 | 用于 |
| ------- | ----------- | --------- |
| `none` | (无头) | 单向箭头的开始 |
| `arrow` | 开放 V | 默认流方向 |
| `triangle` | 填充 ▶ | UML 继承 / "是" |
| `diamond` | 填充 ◆ | UML 组合 / 聚合（在所有者端） |
| `dot` | ● | 序列图消息端点 |
| `square` | ■ | 终端 / 固定端点 |
| `bar` | \| | "停止" / 边界标记 |
| `pipe` | \|\| | 替代边界标记 |
| `inverted` | 空心 V | 次要强调方向 |

默认箭头使用 `"arrowheadStart": "none"`，`"arrowheadEnd": "arrow"`。对于双向链接，将两端都设置为 `"arrow"`。

### 在形状上分布箭头

当多个箭头连接到同一形状时，分配不同的 `normalizedAnchor` 点以防止堆叠：

| 位置 | x | y | 使用场景 |
| ---------- | --- | --- | ---------- |
| 顶部中心 | 0.5 | 0 | 连接到上方的节点 |
| 顶部左 | 0.25 | 0 | 从顶部开始的第 2 个连接 |
| 顶部右 | 0.75 | 0 | 从顶部开始的第 3 个连接 |
| 右侧中心 | 1 | 0.5 | 连接到右侧的节点 |
| 底部中心 | 0.5 | 1 | 连接到下方的节点 |
| 左侧中心 | 0 | 0.5 | 连接到左侧的节点 |

**规则：** 如果一个形状在一侧有 N 个连接，均匀分布它们（例如，底部 3 个连接 → x = 0.25，0.5，0.75）。

### 同两个节点之间的多个箭头

上述规则用于分布箭头连接到*不同*节点。当 **N 个箭头连接同一对**（例如，双向请求/响应，或 A↔B 的几个关系）时，锚点无法分离它们——相反，对称地分配 `bend` 值使箭头扇形展开成不同的弧：

- 选择一个最大 `bend` `amount`（≈ 30–60；节点相距较远时更大）。
- 将 N 个箭头均匀分配从 `−amount` 到 `+amount` 的弯曲：
  - **2 个箭头** → `bend: -amount`，`bend: +amount`
  - **3 个箭头** → `bend: -amount`，`0`，`+amount`
  - 一般：`bend[i] = -amount + i * (2*amount / (N-1))` for `i = 0..N-1`
- 一个直箭头加上一个弯曲的箭头（`bend: 0` 和 `bend: 40`）对于请求/响应对清晰易读。

---

## 容器与注释形状

除了 `geo` 和 `arrow`，两种更多形状类型对技术图表很有用。

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

- `props.name` 是在框架左上角显示的标题。
- **子形状设置 `"parentId": "shape:frame1"`**（不是 `page:page1`），它们的 `x`/`y` 是相对于框架的左上角，而不是页面。一个位于 `x: 40, y: 60` 的子形状会从框架原点向内 40px 并向下 60px 处放置。
- 框架渲染为干净的（非手绘）矩形——适合结构化分组。箭头仍然可以正常跨框架绑定。

### 注意（粘性笔记注释 / 调用）

一个 `note` 是一个粘性笔记——非常适合 TODO、调用和将注释叠加在图表上。

```json
{
  "id": "shape:n1", "typeName": "shape", "type": "note",
  "parentId": "page:page1", "index": "a4",
  "x": 480, "y": 80, "rotation": 0, "isLocked": false, "opacity": 1, "meta": {},
  "props": { "color": "yellow", "size": "m", "text": "TODO: add retry\nlogic here",
    "font": "draw", "align": "middle", "verticalAlign": "middle",
    "growY": 0, "fontSizeAdjustment": 0, "url": "", "scale": 1, "labelColor": "black" }
}
```

- 一个笔记没有 **`w`/`h`**——它是一个固定大小的正方形（约 200px），会自动增长以适应较长的文本。不要添加 `w`/`h`。
- `yellow` 是经典的粘性颜色；任何调色板颜色都可以使用。
- 少量使用笔记——用于关于图表的注释，而不是作为主要节点（使用 `geo`）。

---

## 索引排序规则

索引控制 z-order（堆叠）。使用以下顺序：

```
a1, a2, a3, a4, a5, a6, a7, a8, a9,
aA, aB, aC, aD, aE, aF, aG, aH, aI, aJ, aK, aL, aM,
aN, aO, aP, aQ, aR, aS, aT, aU, aV, aW, aX, aY, aZ,
aa, ab, ac, ... az          ← 超过 aZ 后继续；永远不要 "a10"
```

- 地理形状优先：`a1` 到 `aF`（或根据需要更多）。
- 箭头形状之后：`aG`, `aH` 等。
- 每个形状必须有一个 **唯一** 的索引。

---

## 布局技巧

**间距——随复杂度缩放：**

| 图表复杂度 | 节点 | 水平间距 | 垂直间距 |
| ------------------- | ------- | ---------------- | -------------- |
| 简单 | ≤5 | 200px | 150px |
| 中等 | 6–10 | 280px | 200px |
| 复杂 | >10 | 350px | 250px |

**调整框大小以适应标签（提前做，不要在自检中做）：** `draw` 字体较宽。根据标签计算 `w`/`h`，确保文本不会被裁剪。对默认 `draw` 字体按字符宽度和行高进行估算：

| `size` | 字符宽度 (px) | 行高 (px) |
| -------- | ----------------- | ------------------ |
| `s` | 11 | 18 |
| `m` (默认) | 15 | 28 |
| `l` | 22 | 40 |
| `xl` | 32 | 56 |

每边 `padding = 16`：

- `w = ceil(longest_line_chars * char_width + 2*padding)`，然后向上舍入到下一个 10 的倍数。
- `h = ceil(num_lines * line_height + 2*padding)`，向上舍入到 10 的倍数。

示例：一个大小为 `m` 的框标记为 `"API Gateway"`（11 个字符，1 行）→ `w ≈ 11*15 + 32 = 197 → 200`，`h ≈ 28 + 32 = 60`。多行标签（带有 `\n`）按 **最长** 行计算 `w`，按行数计算 `h`。略微大一点——额外的填充看起来很好，太窄的框会硬换行中间的单词。

**为什么这很重要：** 如果框的高度不足以容纳文本，tldraw 会静默地 **在渲染时增加高度**（它设置形状的 `growY`）——因此框最终比你写的 `h` 大，会与它下面的内容发生碰撞。提前正确调整大小可以保持 `growY` 为 0，并保持你的布局完整。这是导出后“图表看起来拥挤 / 框重叠”的最常见原因。

**路由走廊：** 在形状行/列之间，留出额外的 ~80px 空间，箭头可以在不跨越其他形状的情况下路由。永远不要将形状放置在箭头需要穿越的间隙中。

**网格对齐：** 将所有 `x`、`y`、`w`、`h` 值对齐到 **10 的倍数**——这匹配 tldraw 的默认 `gridSize: 10`，并使手动编辑更轻松。

**一般规则：**

- 在分配 x/y 坐标之前规划网格——首先在脑海中勾勒节点的位置。
- 将相关的节点分组在同一水平或垂直带中。
- 将高度连接的“中心”节点放置在中央，以便箭头向外辐射，而不是交叉。
- 对于跨越多个下游服务的宽形状（如 API Gateway），将 `w` 设置为覆盖整个跨度。
- 将子节点在其父节点下方居中对齐（相同的中心 x）以避免对角线路由。
- **事件总线模式**：将总线（六边形）放置在服务行的 **中心**，而不是下方——两侧的服务可以用短水平箭头（`normalizedAnchor.x = 1` 左侧，`0` 右侧）到达它，消除交叉。
- 水平连接永远不会跨越同一行中的垂直节点；使用它们进行对等和发布连接。

**避免箭头形状重叠：**

- 在最终确定坐标之前，在脑海中跟踪每个箭头路径——如果它必须跨越不相关的形状，要么移动形状，要么使用 `bend` 使其弯曲绕过。
- 对于树/层次布局：将节点分配到层（行），仅在相邻层之间连接以最小化交叉。
- 对于星形/中心布局：放置中心枢纽，卫星围绕它——箭头保持短且径向。

---

## 图表类型预设

当用户请求特定图表类型时，应用以下匹配的形状、颜色和布局约定。

### 架构图表

| 元素 | `geo` | `color` | 备注 |
| --------- | ------- | --------- | ------- |
| 客户端（Web/移动） | `rectangle` | `blue` | 顶行，按客户端类型标记 |
| 服务 / 模块 | `rectangle` | `blue` | 中间行，按层分组 |
| 数据库 | `ellipse` | `green` | 底行，每个服务一个 |
| 缓存 | `ellipse` | `yellow` | 位于其所属服务旁边 |
| 队列 / 事件总线 | `hexagon` | `orange` | **服务行的中心**用于中心模式 |
| 网关 / 负载均衡器 | `triangle` | `violet` | 服务的上方 |
| 外部 API | `cloud` | `red` | 画布边缘，虚线箭头进入 |
| 认证 / 安全 | `rectangle` | `violet` | 通常靠近网关 |

**布局：** 按层数 TB 或 LR；≥4 层 → TB。中心节点居中。间距随复杂度缩放（见上表）。

### 流程图

| 元素 | `geo` | `color` | 备注 |
| --------- | ------- | --------- | ------- |
| 开始 / 结束 | `ellipse` | `green` | 始终在顶部和底部 |
| 处理步骤 | `rectangle` | `blue` | 默认动作框 |
| 决策 | `diamond` | `yellow` | 始终标记出射箭头（是 / 否） |
| I/O | `rectangle`（`dash: dashed`） | `orange` | 通过虚线边框与处理区分 |
| 子流程 | `rectangle` | `violet` | 表示可调用的子流程 |

**布局：** TB，~200px 垂直间距。决策分支向左/右分支，然后合并回中心。始终在箭头的 `props.text` 中标记决策分支。

### 序列图

tldraw 没有本地生命线形状。使用以下方式近似：

| 元素 | `geo` | `color` | 备注 |
| --------- | ------- | --------- | ------- |
| 角色 / 对象标题 | `rectangle` | `blue` | 列的顶部 |
| 生命线 | `rectangle`（`w: 2`，`fill: solid`，`color: grey`） | `grey` | 每个角色标题下方的细垂直线 |
| 同步消息 | 箭头（`arrowheadEnd: arrow`） | `black` | 实心水平箭头 |
| 异步消息 | 箭头（`dash: dashed`） | `black` | 虚线水平箭头 |
| 返回消息 | 箭头（`dash: dashed`，`color: grey`） | `grey` | 灰色虚线 |

**布局：** 按角色 LR（200–280px 间隔），按时间 TB。每个消息是在两个生命线之间增加 `y` 的水平箭头。

### 机器学习 / 深度学习模型图表

用于神经网络架构图表——适合论文图和解释器。

| 元素 | `geo` | `color` | 备注 |
| --------- | ------- | --------- | ------- |
| 输入 / 输出 | `rectangle` | `green` | 堆栈的顶部和底部 |
| 卷积 / 池化 | `rectangle` | `blue` | 标准层块 |
| 注意力 / Transformer | `rectangle` | `violet` | 自注意力块的不同颜色 |
| RNN / LSTM / GRU | `rectangle` | `yellow` | 循环层 |
| FC / 线性 | `rectangle` | `orange` | 稠密投影层 |
| 损失 / 激活 | `rectangle` | `red` | 最终损失 / softmax / 激活 |
| 跳过连接 | 箭头（`bend: 30`，`dash: dashed`） | `grey` | 弯曲虚线绕行 |

**张量形状注释：** 在 `props.text` 中第二行包含维度。tldraw 渲染 `\n` 为 JSON 字符串中的实际换行符，因此使用真实的换行符（JSON 编码器将写入 `\n`）：

```
"text": "Conv2D\n(B, 64, 32, 32)"
```

**布局：** TB（数据从上到下流动），层间距 ~150px。跳过连接绕过主堆栈。

### ER 图（ERD）

tldraw 缺少本地表格/行形状。将每个实体近似为带有多行文本标签的高矩形。

| 元素 | `geo` | `color` | 备注 |
| --------- | ------- | --------- | ------- |
| 实体 | `rectangle`（`fill: solid`，`color: light-blue`） | `light-blue` | 标题 + 列作为一行多行文本标签 |
| 列列表 | 嵌入在 `props.text` 中，行之间用 `\n` 分隔 | — | 用 `*` 前缀标记 PK，用 `>` 标记 FK |
| 关系 | 箭头（`arrowheadStart: arrow`，`arrowheadEnd: arrow`） | `black` | 两端都有箭头表示多对多 |
| 可选 / 弱关系 | 箭头（`dash: dashed`） | `grey` | 虚线表示可选 FK |

通过 `props.text` 标记箭头的基数（例如，`1..*`，`0..1`）。

**布局：** TB 或网格；实体间距 ≥300px 以留出列列表空间。

### UML 类图表

| 元素 | `geo` | `color` | 备注 |
| --------- | ------- | --------- | ------- |
| 类 | `rectangle`（`fill: solid`，`color: light-blue`） | `light-blue` | 标题 + 属性 + 方法作为一行多行 `text` |
| 继承 | 箭头（`arrowheadEnd: triangle`） | `black` | tldraw 渲染填充的 `triangle` 箭头——指向父类 |
| 组合 | 箭头（`arrowheadStart: diamond`，`arrowheadEnd: none`） | `black` | tldraw 渲染填充的 `diamond` 头——放在所有者（整体）端 |
| 聚合 | 箭头（`arrowheadStart: diamond`） | `black` | 相同的 `diamond` 头；通过标签或注释区分组合 |
| 关联 | 箭头（`arrowheadEnd: arrow`） | `black` | 标准箭头 |

**注意：** tldraw 的 `triangle`/`diamond` 箭头是 **填充的**，而严格的 UML 使用 *空心的* 三角形（继承）和填充/空心的菱形（组合/聚合）。形状在草图和解释器中正确显示；对于空心头的出版级 UML，drawio-skill（单独技能）更合适。

**布局：** TB，类间距 ~250px，接口在实现上方。

---

## 导出命令

```bash
# 检查 CLI 版本
tldraw --version

# PNG 按 2x 缩放（推荐）——输出 ./diagram.png
tldraw export diagram.tldr -f png --scale 2 -o ./

# SVG — 输出 ./diagram.svg
tldraw export diagram.tldr -f svg -o ./

# 透明背景
tldraw export diagram.tldr -f png --scale 2 --transparent -o ./

# 暗色主题
tldraw export diagram.tldr -f png --scale 2 --dark -o ./

# 自定义输出目录（例如 CI 产物目录）——如果不存在则创建，然后导出到那里
mkdir -p ./artifacts && tldraw export diagram.tldr -f png --scale 2 -o ./artifacts/
```

**注意：** `-o` 是输出 **目录**，不是文件路径。输出文件以输入文件命名（`diagram.tldr` → `diagram.png`）。

### 导出后自动启动

提供选项在用户的默认 tldraw 查看器/编辑器中打开 `.tldr` 文件：

| OS | 命令 |
| ---- | --------- |
| macOS | `open diagram.tldr` |
| Linux | `xdg-open diagram.tldr` |
| Windows | `start diagram.tldr` |

或者上传到 <https://tldraw.com>（拖放 `.tldr` 文件）以在浏览器中编辑。

---

## 常见错误

| 错误 | 修复 |
| --------- | ----- |
| `tldraw` 命令未找到 | 运行 `npm install -g @kitschpatrol/tldraw-cli` |
| 导出时 `Could not find Chrome (ver. X)` | 安装固定构建：`npx puppeteer browsers install chrome@X`（使用错误中确切的版本） |
| 导出时 `invalidRecords` | 使用单字符 `a` 键（`a1`…`a9`，`aA`…`aZ`，`aa`…`az`）；`a10`，`b1`，`c1` 是不规范的分数索引键 |
| 空白/空导出 | 验证 `document:document` 和 `page:page1` 记录是否存在 |
| 输出文件未找到 | `-o` 是目录；文件名与输入匹配：`tldraw export foo.tldr -o ./` → `./foo.png` |
| 箭头不显示 | 使用 `"type": "binding"` 并设置 `boundShapeId`；将箭头的 `x`/`y` 设置为 `0,0` |
| 形状重叠 | 在分配 x/y 之前规划 200px+ 网格；随复杂度缩放间距 |
| 框比预期高 / 与下方碰撞 | 标签溢出 undersized 框，所以 tldraw 在渲染时自动增加了高度 (`growY`)。提前使用调整公式调整 `w`/`h` 到标签大小 |
| 文本不可见 | 检查 `props.text` 是否设置；如果 `fill: "none"`，确保文本颜色与背景对比 |
| 索引冲突 | 所有形状必须具有唯一的 `index` 值 |
| 形状 ID 冲突 | 使用唯一 ID：`"shape:s1"`，`"shape:s2"`，`"shape:a1"`，等。 |
| 导出失败 | 确保 `.tldr` 文件是有效的 JSON：`python3 -m json.tool file.tldr > /dev/null` |
| 多行标签 | 在 JSON 字符串中使用真实的换行符（`"text": "Line1\nLine2"`）；tldraw 尊重 `\n` |
| 箭头跨越形状 | 使用 `bend` 使其弯曲绕过，或将端点移动到不同的 `normalizedAnchor` |
| 迭代循环永远不会结束 | 5 轮后，建议用户在 tldraw.com 打开 `.tldr` 进行微调 |

---

## 降级链

当工具不可用时，优雅降级：

| 场景 | 行为 |
| ---------- | ---------- |
| `tldraw-cli` 缺失 | 仅生成 `.tldr` JSON；指示用户将 `.tldr` 文件拖放到 <https://tldraw.com> 或安装 CLI |
| 视觉检查不可用于自检 | 跳过自检（步骤 5）；直接向用户展示导出的 PNG |
| 导出失败 | 使用 `python3 -m json.tool` 验证 JSON；交付 `.tldr` 文件并建议在 tldraw.com 打开 |
