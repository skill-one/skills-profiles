---
name: excalidraw
description: 在用户请求图表、流程图、架构图或可视化时使用。也应在解释包含3个或更多组件的系统、复杂数据流或从视觉呈现中受益的关系时主动使用。生成.excalidraw文件，并通过Kroki API或使用excalidraw-brute-export-cli本地导出为PNG/SVG格式。
---

# Excalidraw 图表

## 概述

生成 `.excalidraw` JSON 文件并导出为 PNG/SVG。

**两种导出选项：**

- **Kroki API** (`curl`) — 无需安装，仅支持 SVG 输出
- **excalidraw-brute-export-cli** — 基于 Firefox 的本地工具，支持 PNG + SVG

**支持的格式：** PNG（仅限本地 CLI），SVG（两种选项）。PDF 格式**不支持**。

## 何时使用

**明确触发条件：** 用户说 "画图"、"diagram"、"visualize"、"flowchart"、"draw"、"架构图"、"流程图"

**主动触发条件：**

- 解释包含 3 个以上交互组件的系统
- 描述多步骤流程或决策树
- 并列比较架构或方法

**避免使用场景：** 当简单的列表或表格足够时，或用户处于快速问答流程中

**不适用时 — 转向其他工具：**

- 精美、精确的图表、严格的 UML 或品牌供应商图标 → **drawio**。
- Git 中的图表作为代码、从文本自动布局 → **mermaid**（通用）或 **plantuml**（UML）。
- 无限画布白板或程序化自由笔触 → **tldraw**。

## 前置条件

### 选项 A：Kroki API（推荐 — 无需安装，仅支持 SVG）

```bash
# 仅需 curl（macOS/Linux/Windows Git Bash 已预装）
curl --version
```

无需额外设置。SVG 通过 `https://kroki.io` 渲染。

### 选项 B：本地 CLI（导出 PNG 需要）

CLI 使用 **Firefox**（非 Chromium）。检查并安装：

```bash
npm install -g excalidraw-brute-export-cli
npx playwright install firefox
```

**macOS 一次性补丁（必须）：**

```bash
CLI_MAIN=$(npm root -g)/excalidraw-brute-export-cli/src/main.js
sed -i '' 's/keyboard.press("Control+O")/keyboard.press("Meta+O")/' "$CLI_MAIN"
sed -i '' 's/keyboard.press("Control+Shift+E")/keyboard.press("Meta+Shift+E")/' "$CLI_MAIN"
```

**Windows/Linux：** 无需补丁。

## 工作流程

1. **检查依赖** — 使用 Kroki (curl) 获取 SVG；使用本地 CLI 获取 PNG
2. **规划** — 选择视觉隐喻（见 **Relationship-to-layout map**），然后选择图表类型和配色方案
3. **生成** — 编写 `.excalidraw` JSON 文件（大型图表按部分生成）
4. **导出** — 运行 Kroki 或 CLI 命令
5. **验证渲染效果** — 查看导出的 PNG，修复任何缺陷，重新导出（见 **Verify the Render**）
6. **审核循环** — 向用户展示图像，根据请求进行最小化 `.excalidraw` 编辑，重新导出直至批准（见 **Review Loop**）
7. **报告** — 告知用户输出文件路径

## 设计原则

### 默认样式

- `roughness: 0` — 所有技术图表使用干净、现代的样式（仅在用户要求手绘/休闲风格时使用 `1`）
- `fontFamily: 2` (Helvetica) — 专业外观；仅休闲/草图风格使用 `1` (Virgil)，代码片段使用 `3` (Cascadia)
- `fillStyle: "solid"` — 默认填充

### 容器：优先使用文本而非方框

每个标签周围加方框会使图表看起来像线框图。最干净的 Excalidraw 图表使用**自由浮动文本和线条**构建结构，并为真正是*组件*的内容保留填充方框。

- **默认不使用容器** — 除非方框确实值得使用，否则使用独立的 `text` 元素。
- **仅在以下情况使用方框**：元素是真实的系统组件、箭头绑定到它、形状本身携带意义（决策菱形、开始/结束椭圆）或它分组区域。
- 目标是**文本元素在方框内的比例低于 30%**。
- 对于时间线、树形和层次结构，使用**线条/连接器 + 自由浮动标签**，而不是堆叠的矩形。大小、粗细和颜色创建层次结构，无需方框。

### 字体大小层级

| 级别 | 大小 | 用途 |
| ------- | ------ | --------- |
| 标题 | 28px | 图表标题 |
| 标题 | 24px | 区域/组标题 |
| 标签 | 20px | 主要元素标签 |
| 描述 | 16px | 次要文本、描述 |
| 备注 | 14px | 注释、小字 |

### 配色方案

遵循 **60-30-10 规则**：60% 空白/中性色，30% 主要强调色，10% 高亮色。

**语义填充颜色**（使用比 `strokeColor` 深一度的颜色）：

| 类别 | 填充 | 描边 | 用途 |
| ---------- | ------ | -------- | --------- |
| 主要/输入 | `#dbeafe` | `#1e40af` | 入口点、API、用户界面 |
| 成功/数据 | `#dcfce7` | `#166534` | 数据存储、成功状态 |
| 警告/决策 | `#fef9c3` | `#854d0e` | 决策点、条件 |
| 错误/关键 | `#fee2e2` | `#991b1b` | 错误、警报、关键路径 |
| 外部/存储 | `#f3e8ff` | `#6b21a8` | 外部服务、数据库、AI/ML |
| 流程/默认 | `#e0f2fe` | `#0369a1` | 标准流程步骤 |
| 触发/开始 | `#fed7aa` | `#c2410c` | 开始节点、触发器、事件 |
| 中性/容器 | `#f1f5f9` | `#475569` | 组、泳道、背景 |

**文本颜色：**

| 级别 | 颜色 |
|-------|-------|
| 标题 | `#1e293b` |
| 标签 | `#334155` |
| 描述 | `#64748b` |

**规则：不要凭空创造新颜色。** 从此调色板中选择。

### 箭头语义

| 样式 | 含义 |
| ------- | --------- |
| 实线 (`strokeStyle: "solid"`) | 主要流程、主路径 |
| 虚线 (`"dashed"`) | 响应、异步、回调 |
| 点线 (`"dotted"`) | 可选、参考、弱依赖 |

## Excalidraw JSON 结构

### 文件骨架

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "claude-code",
  "elements": [],
  "appState": { "viewBackgroundColor": "#ffffff" }
}
```

### 元素类型

| 类型      | 用途                          |
|-----------|----------------------------------|
| rectangle | 方框、组件、模块               |
| ellipse   | 开始/结束节点、数据库       |
| diamond   | 决策点                  |
| arrow     | 有向连接             |
| line      | 无向连接           |
| text      | 独立标签                |

`image`、`frame` 和 `embeddable` **不在此技能范围内**：`image` 需要单独的 `files` 映射加上 `fileId`，框架/嵌入在导出路径中渲染不一致。坚持使用上述六种类型 — 对于由这些基本元素构建的现成图标，见**社区形状和图标库**下方。

### 社区形状和图标库

需要真实的 AWS / Azure / GCP / 网络 / UML / BPMN 图标而不是普通方框？Excalidraw 社区库（200+ `.excalidrawlib` 文件）几乎完全由上述**相同矢量基本元素**构建 — 因此它们的项**通过 Kroki 和本地 CLI 渲染**，无需 `image` 元素和 `files` 映射。使用 `scripts/excalidraw_lib.py` 中的辅助工具：

```bash
# 1. 查找库（匹配名称/描述/项名称）
python scripts/excalidraw_lib.py search aws

# 2. 列出其项（索引、名称、元素数量；标记任何基于图像的项）
python scripts/excalidraw_lib.py items slobodan/aws-serverless.excalidrawlib

# 3. 首先构建基础场景，然后在 (x, y) 处放置一项。ID 是命名空间的，坐标会转换，所以它合并时不会冲突：
python scripts/excalidraw_lib.py merge scene.excalidraw \
    slobodan/aws-serverless.excalidrawlib 0 455 257 --scale 0.9 --prefix lambda
```

**规则：**

- **仅限矢量。** `merge` 拒绝任何包含 `image` 元素的项（无法通过导出路径渲染）；`items` 会提前标记它们。
- **谨慎使用。** 图标只是一个带标签的节点 — 保持设计系统的间距、标签和箭头语义。图标强调图表；它们不能替代图表。
- 箭头**不绑定到库组** — 使用明确的边缘到边缘 `points` 绘制连接器（绑定不会影响静态导出）。导出器直接绘制你的 `points`。因此计算端点边缘对齐：将箭头的 `x`/`y` 设置为源形状的边界（面向目标的边），将最后一个点设置为目标的边界。中心对中心点会使线穿过两个形状。
- 库是 MIT 授权的；礼貌的致谢是受欢迎的，不是必需的。
- 仍然运行**Verify the Render** — 图标边界框不同，所以检查对齐和间距。

### 元素尺寸

根据标签文本计算元素宽度以防止截断：

```
拉丁文:  width = max(160, charCount * 9)
CJK 文:   width = max(160, charCount * 18)
混合文:  逐个估算每个字符，求和
```

高度：单行标签使用 `60`，每增加一行添加 `24`。

**独立的 `text` 不自动换行。** 对于多行独立标签，请自己插入手动 `\n` 行符 — 目标是每行 ≤ ~30 个拉丁字符（≤ ~15 个 CJK 字符）在 16px 下 — 并为每行添加 `24` 高度。（文本*绑定在形状内*通过 `containerId` 换行自动，所以调整容器大小而不是添加 `\n`。）

### 必须属性（所有元素）

```json
{
  "id": "auth_service",
  "type": "rectangle",
  "x": 100, "y": 100,
  "width": 160, "height": 60,
  "angle": 0,
  "strokeColor": "#1e40af",
  "backgroundColor": "#dbeafe",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "roughness": 0,
  "opacity": 100,
  "seed": 100001,
  "boundElements": [
    { "id": "arrow_to_db", "type": "arrow" },
    { "id": "label_auth", "type": "text" }
  ]
}
```

使用**描述性字符串 ID**（例如，`"api_gateway"`，`"arrow_gw_to_auth"`）而不是随机字符串。

给每个元素一个唯一的 `seed`（整数）。按部分命名：100xxx，200xxx，300xxx。

### JSON 字段规则

- `boundElements`：为空时使用 `null`，永远不要 `[]`
- `updated`：始终使用 `1`，永远不要时间戳
- 不要包含：`frameId`，`index`，`versionNonce`，`rawText`
- 箭头中的 `points`：始终从 `[0, 0]` 开始
- `seed`：必须是一个正整数，每个元素唯一

### 属性值

仅使用以下值 — 所有值均已验证可通过 Kroki 和本地 CLI 渲染：

| 属性 | 有效值 |
| ---------- | -------------- |
| `fillStyle` | `"solid"`，`"hachure"`，`"cross-hatch"`，`"zigzag"` |
| `strokeStyle` | `"solid"`（或省略），`"dashed"`，`"dotted"` |
| `fontFamily` | `1` (Virgil，手绘)，`2` (Helvetica)，`3` (Cascadia，代码) |
| `textAlign` | `"left"`，`"center"`，`"right"` |
| `verticalAlign` | `"top"`，`"middle"`，`"bottom"` |
| `startArrowhead` / `endArrowhead` | `null`，`"arrow"`，`"triangle"`，`"bar"`，`"dot"`，`"circle"`，`"diamond"`，`"crowfoot_many"` |

箭头默认为 `endArrowhead: "arrow"` 和 `startArrowhead: null` — 省略两者以绘制标准单向箭头。使用 `"triangle"` 表示 UML 继承，`"diamond"` 表示组合，`"crowfoot_many"` 表示 ER 实体基数。

> **需要复制粘贴模板或完整属性/箭头头目录？** 阅读 `references/schema-reference.md` — 完整元素模板（组件+标签、绑定箭头、箭头标签、泳道区域、思维导图连接器）和每个验证过的属性值。

### 形状内的文本（包含文本）

当文本属于形状内部时，双向绑定它们：

```json
{
  "id": "label_auth",
  "type": "text",
  "text": "Auth Service",
  "fontSize": 20,
  "fontFamily": 2,
  "textAlign": "center",
  "verticalAlign": "middle",
  "strokeColor": "#1e293b",
  "containerId": "auth_service"
}
```

**关键：文本 `strokeColor` 是文本颜色。** 始终将其显式设置为文本颜色调色板中的深色。不要省略它 — 省略文本上的 `strokeColor` 可能导致文本不可见，因为它会与形状背景混合。

父形状必须在它的 `boundElements` 中列出文本：

```json
"boundElements": [{ "id": "label_auth", "type": "text" }]
```

### 箭头绑定（双向）

箭头必须绑定到形状，形状必须引用绑定的箭头：

```json
{
  "id": "arrow_gw_to_auth",
  "type": "arrow",
  "points": [[0, 0], [200, 0]],
  "startBinding": { "elementId": "api_gateway", "gap": 5, "focus": 0 },
  "endBinding": { "elementId": "auth_service", "gap": 5, "focus": 0 }
}
```

`api_gateway` 和 `auth_service` 都必须在它们的 `boundElements` 中包含：

```json
"boundElements": [{ "id": "arrow_gw_to_auth", "type": "arrow" }]
```

**端点必须到达形状边界。** `startBinding`/`endBinding`（及其 `gap`）仅影响 excalidraw.com 上的交互式编辑 — 它们**不**在通过 Kroki 或本地 CLI 导出时裁剪线条。导出器直接绘制你的 `points`。因此计算端点边缘对齐：将箭头的 `x`/`y` 设置为源形状的边界（面向目标的边），将最后一个点设置为目标的边界。中心对中心点会使线穿过两个形状。

### 箭头标签

要为箭头添加标签，像形状文本一样绑定一个 `text` 元素：设置标签的 `containerId` 为**箭头**的 ID，并将标签添加到箭头的 `boundElements`。Excalidraw 然后将在箭头上居中标签并遮罩文本后面的线条，所以它保持可读（没有删除线）。

```json
{
  "id": "arrow_valid_to_grant",
  "type": "arrow",
  "points": [[0, 0], [0, 120]],
  "boundElements": [{ "id": "lbl_yes", "type": "text" }]
}
```

```json
{
  "id": "lbl_yes",
  "type": "text",
  "text": "Yes",
  "fontSize": 14,
  "width": 36,
  "strokeColor": "#1e293b",
  "containerId": "arrow_valid_to_grant"
}
```

**关键：标签 `width` 必须适合文本（`charCount * 9`），而不是箭头长度。** Excalidraw 遮罩标签的完整边界框后面的线条 — 宽度与箭头相同的标签会遮罩*整个*箭头，导致线条消失，只剩下浮动文本。保持标签宽度小。

### 箭头路由

**L 形（肘形）箭头** — 正交路由，3 个以上点：

```json
"points": [[0, 0], [100, 0], [100, 150]]
```

**肘形箭头** — 自动右角路由：

```json
{
  "type": "arrow",
  "points": [[0, 0], [0, -50], [200, -50], [200, 0]],
  "elbowed": true
}
```

**曲线箭头** — 平滑路由，带有航路点：

```json
{
  "type": "arrow",
  "points": [[0, 0], [50, -40], [200, 0]],
  "roundness": { "type": 2 }
}
```

### 分组

相关元素共享 `groupIds`。嵌套组按从内到外的顺序列出 ID：

```json
"groupIds": ["inner_group", "outer_group"]
```

## 图表模式

为每种图表类型选择正确的视觉模式。

### Relationship-to-layout map

在锁定*图表类型*之前，选择与想法中关系匹配的*视觉隐喻* — 它比类型标签更能驱动布局：

| 想法中的关系 | 视觉隐喻 | 构建 |
| --- | --- | --- |
| 一对多（广播、分发） | **Fan-out** | 一个节点，箭头向外辐射 |
| 多对一（聚合、合并） | **Convergence** | 多个输入，箭头指向一个节点 |
| 父亲对子女（层次结构） | **Tree** | 树干 + 分支*线*，自由浮动文本 |
| 重复循环（循环、反馈） | **Cycle** | 节点在一个环中，曲线箭头回到起点 |
| 输入 → 转换 → 输出 | **Assembly line** | 从左到右的步骤管道 |
| A 与 B（比较） | **Side-by-side** | 在共享基线上并行的两个列 |
| 前 / 后，阶段分隔 | **Gap** | 组之间使用空白或虚线分隔 |
| 模糊/重叠状态 | **Cloud** | 重叠的椭圆，没有硬边界 |

### 间距参考

| 场景 | 间距 |
| ---------- | --------- |
| 带标签箭头间距（形状之间） | 150–200px |
| 无标签箭头间距 | 100–120px |
| 列间距（带标签箭头） | 400px (220px 盒子 + 180px 间距) |
| 列间距（无标签箭头） | 340px (220px 盒子 + 120px 间距) |
| 行间距 | 280–350px (150px 盒子 + 130–200px 间距) |
| 区域/容器填充 | 儿童周围 50–60px |
| 区域/容器不透明度 | 25–40 |
| 任何元素之间的最小间距 | 40px |

### 流程图（LR 或 TB）

- 椭圆表示开始/结束，菱形表示决策，矩形表示流程
- 水平间距 200px，垂直间距 150px
- 决策分支："是" 向前，"否" 向下
- 3–10 步（最大 15）

### 架构 / 系统图表

- 按上表使用列间距；当连接有标签时使用带标签箭头间距
- 将相关服务分组到虚线 `Neutral` 容器（不透明度：30，填充：50px）
- 左侧或顶部放置网关/入口，数据库在右侧或底部
- 3–8 个实体（最大 12）

### 序列图

- 参与者（矩形在顶部）之间 200px
- 垂直生命线作为虚线
- 水平箭头表示消息，垂直间距 60px
- 实线箭头 = 请求，虚线箭头 = 响应

### 思维导图

- 中心节点：最大（200x100），`Trigger`颜色
- 第一级：150x70，`Primary`颜色，围绕中心径向分布
- 第二级：120x50，`Process`颜色
- 第三级：90x40，`Neutral`颜色
- 使用线条（而非箭头）表示连接
- 4-6个分支（最多8个），每个分支2-4个子主题
- **将第一级分支放置在中心`(cx, cy)`周围半径`R ≈ 280`的圆上**：对于第`i`个分支`n`，`角度 = 2π·i/n`，`x = cx + R·cos(角度)`，`y = cy + R·sin(角度)`。均匀间距可防止自选位置产生的交叉线混乱。

### 游泳区

- 使用大透明矩形（`Neutral`填充，`"dashed"`边框，不透明度：30）作为泳道边界
- 泳道标签作为独立文本放置在泳道左上角（不绑定到矩形），28px字体
- 元素在泳道内从左到右流动
- 箭头跨泳道进行交接

## 分区构建

对于包含**10+元素**的图表，**不要一次性生成整个JSON**。分区构建：

1. **首先规划所有分区** — 列出元素ID、位置和跨分区绑定
2. **编写第一分区** — 创建包含初始元素的文件
3. **追加第二分区** — 读取文件，向`elements`数组添加新元素
4. **重复** — 直至所有分区完成
5. **最终检查** — 验证所有`boundElements`和`startBinding`/`endBinding`引用是否一致

按分区命名空间元素种子（100xxx，200xxx，300xxx）以避免冲突。

## 导出

### 选项A：Kroki API（仅SVG — 无需安装）

```bash
# 通过Kroki API生成SVG
curl -s -X POST https://kroki.io/excalidraw/svg \
  -H "Content-Type: text/plain" \
  --data-binary "@diagram.excalidraw" \
  -o diagram.svg

# 通过本地Kroki Docker（离线模式）
curl -s -X POST http://localhost:8000/excalidraw/svg \
  -H "Content-Type: text/plain" \
  --data-binary "@diagram.excalidraw" \
  -o diagram.svg
```

### 选项B：本地CLI（PNG + SVG）

```bash
# 2倍缩放PNG，背景嵌入（推荐）
excalidraw-brute-export-cli -i diagram.excalidraw -o diagram.png -f png -s 2 -b true

# 1倍缩放PNG
excalidraw-brute-export-cli -i diagram.excalidraw -o diagram.png -f png -s 1 -b true

# SVG
excalidraw-brute-export-cli -i diagram.excalidraw -o diagram.svg -f svg -s 1 -b true
```

**必需标志**：`-f`（格式：`png`或`svg`）和`-s`（缩放：`1`，`2`或`3`）。

**可选标志**：`-b true`将`viewBackgroundColor`嵌入图像中 — **导出默认为透明**，仅在需要透明背景时省略`-b`（或传递`-b false`）。`-d true`导出暗黑模式；`-e true`嵌入场景，使PNG/SVG在excalidraw.com中重新打开为可编辑绘图。（长形式也有效：`--background`，`--dark-mode`，`--embed-scene`，`--format`，`--scale`，`--input`，`--output`。）

## 验证渲染

**无法从JSON判断图表**。JSON可能完美，但图像可能存在文本被裁剪、框重叠或箭头穿过形状的情况。导出后，*查看结果并修复* — 这是最高效的步骤。

1. **渲染为PNG**（图像必须可查看 — PNG，即使最终用户想要SVG）：

   ```bash
   excalidraw-brute-export-cli -i diagram.excalidraw -o /tmp/check.png -f png -s 2 -b true
   ```

   查看`/tmp/check.png`（Claude可直接读取PNG）。*视觉审核需要本地CLI；如果仅使用Kroki（SVG），则回退到以下结构检查。*
2. **审核图像**：

   | 查找 | 修复 |
   | ---------- | ----- |
   | 文本被裁剪/溢出形状 | 加宽形状（`max(160, charCount * 9)`，CJK需乘以2）或用`\n`预换行 |
   | 框或标签重叠 | 使用间距参考重新布局（≥40px间隙） |
   | 箭头直接穿过形状 | 将端点移动到形状边界而非中心 |
   | 箭头不可见 — 仅显示标签 | 缩小标签`width`以适应文本 |
   | 元素离屏或无连接漂浮 | 重新定位/连接它 |
   | **同构测试**：在脑海中删除所有文本 — 结构本身是否仍传达信息？ | 如果不是，布局错误，非标签错误 — 重新结构 |

3. **修复JSON并重新导出**。重复直至干净 — 通常1-3次。仅对简单2-3元素图表跳过。

## 审核循环

验证渲染修复*缺陷*；审核循环包含*用户的*需求。渲染干净后，展示并收集反馈，然后对每个请求应用**最小的`.excalidraw`编辑**并重新导出：

| 用户请求 | 编辑操作 |
| --- | --- |
| 更改标签 | 编辑`text`（或绑定的标签元素） |
| 更改颜色 | 更新`backgroundColor` / `strokeColor` |
| 添加/删除元素 | 追加或删除元素（修复任何`boundElements` / 绑定引用） |
| 移动/调整大小 | 更新`x` / `y` / `width` / `height` |
| 重新结构/重路由 | 重新应用模式的间距和路由规则，或重新生成 |

- 每轮覆盖相同的`diagram.excalidraw` / 输出文件 — 不要创建`v1`，`v2`，…
- 每次编辑后重新运行**验证渲染**（更改可能引入新的裁剪/重叠）。
- **安全阀**：5轮后，建议用户在[excalidraw.com](https://excalidraw.com)精细调整 — 输出保留箭头绑定，因此可完全编辑。

## 反模式

**永远不要在大型背景/区域矩形上放置`text`**。Excalidraw将文本居中放置在形状中间，与包含元素重叠。相反，使用位于区域顶部的独立`text`元素。

**避免跨区域箭头**。长对角线箭头创建视觉杂乱。在区域内或沿区域边缘路由箭头。如果无法避免跨区域连接，沿边界路由。

**谨慎使用箭头标签**。将标签绑定到箭头（见**箭头标签**），使线条被文本遮挡而非穿过它 — 但保持标签`width`与文本匹配，而非箭头长度。标签长度≤12个字符，并确保连接形状间≥120px清晰空间。当连接含义从上下文明显时省略标签。

**不要在包含其他元素的容器上使用填充背景**。使用`opacity: 30`（或25-40范围）的区域/容器矩形，以便包含元素保持可见。

**始终为文本元素设置明确的`strokeColor`**。文本`strokeColor`是渲染文本颜色。如果省略，文本可能继承父形状的背景颜色而变得不可见。使用`#1e293b`（标题）、`#334155`（标签）或`#64748b`（描述）来自文本颜色调色板。

## 常见错误

| 错误 | 修复 |
| --------- | ----- |
| Kroki返回HTTP 400 | 发送`-H "Content-Type: text/plain"`（非`application/json`，Kroki将其作为`{"diagram_source": ...}`包装并拒绝）；确保有效的JSON，包含`"type": "excalidraw"`和`"elements"`数组 |
| Kroki仅输出SVG | 使用本地CLI（`excalidraw-brute-export-cli`）生成PNG |
| 导出失败提示"缺少必需标志" | 始终传递`-f png`和`-s 2` |
| 导出失败提示"可执行文件不存在" | 运行`npx playwright install firefox` |
| macOS：超时等待文件选择器 | 应用上述macOS Meta补丁 |
| 箭头`points`未相对于原点 | `points`始终从`[0,0]`开始 |
| 元素缺少`id` | 每个元素使用描述性字符串ID |
| 元素重叠 | 使用间距参考表；最小40px间隙 |
| 箭头在excalidraw.com中不可交互 | 向引用所有绑定箭头/文本的形状添加`boundElements` |
| 箭头/线条直接穿过形状 | 计算端点在形状边界而非中心 — 绑定不会裁剪静态导出 |
| 箭头不可见 — 仅显示标签 | 绑定标签`width`跨越整个箭头并遮挡线条；设置标签`width`以适应文本（`charCount * 9`） |
| 导出的PNG/SVG无背景 | CLI导出默认透明；传递`-b true`以嵌入`viewBackgroundColor` |
| 文本未居中在形状内 | 在文本上设置`containerId`，并将文本添加到形状的`boundElements` |
| 所有文本大小相同 | 使用字体大小层级：28 → 24 → 20 → 16 → 14 |
| 图表看起来单调 | 应用调色板中的语义颜色，遵循60-30-10规则 |
| 文本不可见/与背景同色 | 始终为文本元素设置`strokeColor`为深色（`#1e293b`，`#334155`或`#64748b`） |
| 文本在区域/容器内重叠 | 不要将文本绑定到区域矩形；在顶部使用独立文本 |
| 文本在形状内被截断 | 使用宽度公式：`max(160, charCount * 9)`，CJK需乘以2 |
| `boundElements: []`导致问题 | 使用`null`表示空的`boundElements`，切勿使用`[]` |
