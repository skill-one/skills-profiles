---
name: draw-io-diagram-generator
description: 在创建、编辑或生成 draw.io 图表文件（.drawio、.drawio.svg、.drawio.png）时使用。涵盖 mxGraph XML 编写、形状库、样式字符串、流程图、系统架构、时序图、ER 图、UML 类图、网络拓扑、布局策略、hediet.vscode-drawio VS Code 扩展，以及从请求到可打开文件的完整代理工作流程。
---

# Draw.io 图表生成器

这项技能可以让你生成、编辑和验证具有正确 mxGraph XML 结构的 draw.io (`.drawio`) 图表文件。所有生成的文件都可以立即在 [Draw.io VS Code 扩展](https://marketplace.visualstudio.com/items?itemName=hediet.vscode-drawio) (`hediet.vscode-drawio`) 中打开，无需任何手动修复。你也可以选择在 draw.io 网页版或桌面版中打开这些文件。

---

## 1. 何时使用此技能

**触发短语（在看到这些短语时加载此技能）**

- "创建图表"、"绘制流程图"、"生成架构图"
- "设计时序图"、"制作 UML 类图"、"构建 ER 图"
- "添加 .drawio 文件"、"更新图表"、"可视化流程"
- "记录架构"、"展示数据模型"、"图表化服务交互"
- 任何要求生成或修改 `.drawio`、`.drawio.svg` 或 `.drawio.png` 文件的请求

**支持的图表类型**

| 图表类型     | 模板可用   | 描述         |
|-------------|-----------|--------------|
| 流程图     | `assets/templates/flowchart.drawio` | 带决策和分支的流程流 |
| 系统架构   | `assets/templates/architecture.drawio` | 多层/分层服务架构 |
| 时序图     | `assets/templates/sequence.drawio` | 参与者生命线和定时消息流 |
| ER 图     | `assets/templates/er-diagram.drawio` | 数据库表及其关系 |
| UML 类图   | `assets/templates/uml-class.drawio` | 类、接口、枚举、关系 |
| 网络拓扑   | （使用形状库） | 路由器、服务器、防火墙、子网 |
| BPMN 工作流 | （使用形状库） | 业务事件、任务、网关 |
| 思维导图   | （手动）   | 中心主题和辐射分支 |

---

## 2. 前置条件

- 如果启用 VS Code 集成，请安装 drawio 扩展：**draw.io VS Code 扩展** — `hediet.vscode-drawio`（扩展 ID）。安装方法：
  ```
  ext install hediet.vscode-drawio
  ```
- **支持的文件扩展名**：`.drawio`、`.drawio.svg`、`.drawio.png`
- **Python 3.8+**（可选）— 用于 `scripts/` 中的验证和形状插入脚本

---

## 3. 逐步代理工作流程

对于每个图表生成任务，请按以下步骤操作。

### 第 1 步 — 理解请求

询问或推断：
1. **图表类型** — 是什么类型的图表？（流程图、架构、UML、ER、时序、网络...）
2. **实体 / 参与者** — 主要组件、参与者、类或表是什么？
3. **关系** — 它们如何连接？方向是什么？基数是什么？
4. **输出路径** — 应该在哪里保存 `.drawio` 文件？
5. **现有文件** — 我们是创建新文件还是编辑现有文件？

如果请求不明确，根据上下文推断最合理的图表类型（例如："显示表" → ER 图，"显示 API 调用流程" → 时序图）。

### 第 2 步 — 选择模板或从零开始

- **使用模板**：当图表类型与 `assets/templates/` 中的类型匹配时。复制模板结构并替换占位符值。
- **从零开始**：用于新颖的布局。从最小的有效骨架开始：

```xml
<!-- 生成新文件时，将 modified 设置为当前的 ISO 8601 时间戳 -->
<mxfile host="Electron" modified="" version="26.0.0">
  <diagram id="page-1" name="Page-1">
    <mxGraphModel dx="1422" dy="762" grid="1" gridSize="10" guides="1"
                  tooltips="1" connect="1" arrows="1" fold="1"
                  page="1" pageScale="1" pageWidth="1169" pageHeight="827"
                  math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <!-- 你的单元格放在这里 -->
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

> **规则**：id `0` 和 `1` 永远是必需的，并且必须是前两个单元格。永远不要重用它们。

### 第 3 步 — 规划布局

在生成 XML 之前，勾勒出逻辑位置：
- 按行或层级组织（使用泳道表示层）
- **水平间距**：同一行形状之间 40–60px
- **垂直间距**：层级行之间 80–120px
- 标准形状大小：`120x60` px（处理框），`160x80` px（泳道）
- 默认画布：A4 横向 = `1169 x 827` px

### 第 4 步 — 生成 mxGraph XML

**顶点单元格**（每个形状）：
```xml
<mxCell id="unique-id" value="Label"
        style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;"
        vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="120" height="60" as="geometry" />
</mxCell>
```

**边单元格**（每个连接器）：
```xml
<mxCell id="edge-id" value="Label (可选)"
        style="edgeStyle=orthogonalEdgeStyle;html=1;"
        edge="1" source="source-id" target="target-id" parent="1">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

**关键规则**：
- 每个单元格 id 必须在文件中**全局唯一**
- 每个顶点必须有一个 `mxGeometry` 子元素，包含 `x`、`y`、`width`、`height`、`as="geometry"`
- 每个边必须具有 `source` 和 `target`，匹配现有的顶点 id — **例外**：悬浮边（例如时序图生命线）在 `<mxGeometry>` 内使用 `sourcePoint`/`targetPoint`；见 §4 时序图
- 每个单元格的 `parent` 必须引用一个现有的单元格 id
- 当标签包含 HTML (`<b>`、`<i>`、`<br>`) 时，在 style 中使用 `html=1`
- 在标签中转义 XML 特殊字符：`&` => `&amp;`，`<` => `&lt;`，`>` => `&gt;`

### 第 5 步 — 应用正确的样式

使用标准的语义色板以保持一致性：

| 目的       | fillColor | strokeColor |
|-----------|----------|------------|
| 主要 / 信息 | `#dae8fc` | `#6c8ebf`  |
| 成功 / 开始 | `#d5e8d4` | `#82b366`  |
| 警告 / 决策 | `#fff2cc` | `#d6b656`  |
| 错误 / 结束 | `#f8cecc` | `#b85450`  |
| 中性       | `#f5f5f5` | `#666666`  |
| 外部 / 合作方 | `#e1d5e7` | `#9673a6`  |

按图表类型常见的样式字符串：

```
# 圆角处理框（流程图）
rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;

# 菱形决策框
rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;

# 开始/结束终端
ellipse;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;

# 数据库圆柱
shape=mxgraph.flowchart.database;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;

# 泳道容器（层级）
swimlane;startSize=30;fillColor=#dae8fc;strokeColor=#6c8ebf;fontStyle=1;

# UML 类框
swimlane;fontStyle=1;align=center;startSize=40;fillColor=#dae8fc;strokeColor=#6c8ebf;

# 接口 / 限定符框
swimlane;fontStyle=3;align=center;startSize=40;fillColor=#f5f5f5;strokeColor=#666666;

# ER 表容器
shape=table;startSize=30;container=1;collapsible=1;childLayout=tableLayout;

# 正交连接器
edgeStyle=orthogonalEdgeStyle;html=1;

# ER 关系（鸟脚）
edgeStyle=entityRelationEdgeStyle;html=1;endArrow=ERmany;startArrow=ERone;
```

> 参考 `references/style-reference.md` 获取完整的样式键目录和 `references/shape-libraries.md` 获取所有形状库名称。

### 第 6 步 — 保存和验证

1. **写入文件** 到请求的路径，扩展名为 `.drawio`
2. **运行验证器**（可选但推荐）：
   ```bash
   python .github/skills/draw-io-diagram-generator/scripts/validate-drawio.py <path-to-file.drawio>
   ```
3. **告诉用户** 如何打开文件：
   > "在 `<filename>` 中使用 VS Code 打开 — 它将自动使用 draw.io 扩展渲染。你也可以选择使用 draw.io 的网页版或桌面版。"
4. **提供图表的简要描述**，以便用户知道可以期待什么。

---

## 4. 图表类型配方

### 流程图

关键元素：开始（椭圆）→ 处理（圆角矩形）→ 决策（菱形）→ 结束（椭圆）

```xml
<!-- 开始节点 -->
<mxCell id="start" value="开始"
        style="ellipse;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;"
        vertex="1" parent="1">
  <mxGeometry x="500" y="80" width="120" height="60" as="geometry" />
</mxCell>

<!-- 处理 -->
<mxCell id="p1" value="处理步骤"
        style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;"
        vertex="1" parent="1">
  <mxGeometry x="500" y="200" width="120" height="60" as="geometry" />
</mxCell>

<!-- 决策 -->
<mxCell id="d1" value="条件?"
        style="rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;"
        vertex="1" parent="1">
  <mxGeometry x="460" y="320" width="200" height="100" as="geometry" />
</mxCell>

<!-- 箭头：开始到 p1 -->
<mxCell id="e1" value=""
        style="edgeStyle=orthogonalEdgeStyle;html=1;"
        edge="1" source="start" target="p1" parent="1">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

### 架构图（3 层）

使用**泳道容器**表示每个层级。所有服务框都是其泳道的子元素。

```xml
<!-- 层级泳道 -->
<mxCell id="tier1" value="客户端层"
        style="swimlane;startSize=30;fillColor=#dae8fc;strokeColor=#6c8ebf;fontStyle=1;"
        vertex="1" parent="1">
  <mxGeometry x="60" y="100" width="1050" height="130" as="geometry" />
</mxCell>

<!-- 层级内的服务（parent="tier1"，坐标相对于层级） -->
<mxCell id="webapp" value="Web 应用"
        style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;"
        vertex="1" parent="tier1">
  <mxGeometry x="80" y="40" width="120" height="60" as="geometry" />
</mxCell>
```

> 层级之间的连接器使用绝对坐标和 `parent="1"`。

### 时序图

关键元素：参与者（顶部）、生命线（虚线垂直线）、激活框、消息箭头。

- 生命线：`edge="1"`，`endArrow=none`，`dashed=1`，无 `source`/`target` — 在 `<mxGeometry>` 中使用 `sourcePoint`/`targetPoint`
- 同步消息：`endArrow=block;endFill=1`
- 返回消息：`endArrow=open;endFill=0;dashed=1`
- 自调用：通过右侧两个 Array 点循环边到右侧再返回

**最小 XML 片段**：

```xml
<!-- 参与者（小人） -->
<mxCell id="actorA" value="客户端"
        style="shape=mxgraph.uml.actor;pointerEvents=1;dashed=0;whiteSpace=wrap;html=1;aspect=fixed;"
        vertex="1" parent="1">
  <mxGeometry x="110" y="80" width="60" height="80" as="geometry" />
</mxCell>

<!-- 服务框 -->
<mxCell id="actorB" value="API 服务器"
        style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;"
        vertex="1" parent="1">
  <mxGeometry x="480" y="100" width="160" height="60" as="geometry" />
</mxCell>

<!-- 生命线 — 悬浮边：使用 sourcePoint/targetPoint，不使用 source/target 属性 -->
<mxCell id="lifA" value=""
        style="edgeStyle=none;dashed=1;endArrow=none;"
        edge="1" parent="1">
  <mxGeometry relative="1" as="geometry">
    <mxPoint x="140" y="160" as="sourcePoint" />
    <mxPoint x="140" y="700" as="targetPoint" />
  </mxGeometry>
</mxCell>

<!-- 激活框（生命线上的细矩形） -->
<mxCell id="actA1" value=""
        style="fillColor=#dae8fc;strokeColor=#6c8ebf;"
        vertex="1" parent="1">
  <mxGeometry x="130" y="220" width="20" height="180" as="geometry" />
</mxCell>

<!-- 同步消息 -->
<mxCell id="msg1" value="POST /orders"
        style="edgeStyle=elbowEdgeStyle;elbow=vertical;html=1;endArrow=block;endFill=1;"
        edge="1" source="actA1" target="actorB" parent="1">
  <mxGeometry relative="1" as="geometry" />
</mxCell>

<!-- 返回消息（虚线） -->
<mxCell id="msg2" value="201 Created"
        style="edgeStyle=elbowEdgeStyle;elbow=vertical;dashed=1;html=1;endArrow=open;endFill=0;"
        edge="1" source="actorB" target="actA1" parent="1">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

> **注意**：生命线是悬浮边，在 `<mxGeometry>` 中使用 `sourcePoint`/`targetPoint` 而不是 `source`/`target` 属性。这是 draw.io 时序图的标准化模式。

### ER 图

使用 `shape=table` 容器，`childLayout=tableLayout`。行是 `shape=tableRow` 单元格，`portConstraint=eastwest`。每个行内的列是 `shape=partialRectangle`。

关系箭头使用 `edgeStyle=entityRelationEdgeStyle`：
- 一对一：`startArrow=ERone;endArrow=ERone`
- 一对多：`startArrow=ERone;endArrow=ERmany`
- 多对多：`startArrow=ERmany;endArrow=ERmany`
- 强制：`ERmandOne`，可选：`ERzeroToOne`

### UML 类图

类框是泳道容器。属性和方法是普通文本单元格。分隔符是高度为 0 的泳道子元素。

按关系类型使用的箭头样式：

| 关系       | Style String |
|-----------|--------------|
| 继承（扩展） | `edgeStyle=orthogonalEdgeStyle;html=1;endArrow=block;endFill=0;` |
| 实现（实现） | `edgeStyle=orthogonalEdgeStyle;dashed=1;html=1;endArrow=block;endFill=0;` |
| 组合       | `edgeStyle=orthogonalEdgeStyle;html=1;startArrow=diamond;startFill=1;endArrow=none;` |
| 聚合       | `edgeStyle=orthogonalEdgeStyle;html=1;startArrow=diamond;startFill=0;endArrow=none;` |
| 依赖       | `edgeStyle=orthogonalEdgeStyle;dashed=1;html=1;endArrow=open;endFill=0;` |
| 关联       | `edgeStyle=orthogonalEdgeStyle;html=1;endArrow=open;endFill=0;` |

---

## 5. 多页图表

为复杂系统添加多个 `<diagram>` 元素：

```xml
<mxfile host="Electron" version="26.0.0">
  <diagram id="overview" name="概述">
    <!-- 概述 mxGraphModel -->
  </diagram>
  <diagram id="detail" name="详细视图">
    <!-- 详细视图 mxGraphModel -->
  </diagram>
</mxfile>
```

每个页面都有其独立的单元格 id 命名空间。相同的 id 值可以在不同页面中存在而不冲突。

---

## 6. 编辑现有图表

修改现有的 `.drawio` 文件时：

1. **先读取** 文件以理解现有的单元格 id、位置和父级层次结构
2. **确定目标图表页面** — 通过索引或 `name` 属性
3. **分配新的唯一 id**，避免与现有 id 冲突
4. **尊重容器层次结构** — 泳道子元素的坐标相对于其父元素
5. **验证边** — 移动节点后，确认边 source/target id 仍然有效

使用 `scripts/add-shape.py` 安全地添加单个形状，无需编辑原始 XML：
```bash
python .github/skills/draw-io-diagram-generator/scripts/add-shape.py docs/arch.drawio "新服务" 700 380
```

---

## 7. 最佳实践

**布局**
- 形状对齐到 10px 网格（所有坐标都是 10 的倍数）
- 将相关形状分组到泳道容器内
- 每页一个图表主题；使用多页文件表示复杂系统
- 每页的单元格数量控制在 40 个以内，以提高可读性

**标签**
- 在每个页面的顶部添加标题文本单元格 (`text;strokeColor=none;fillColor=none;fontSize=18;fontStyle=1`)
- 始终在顶点形状上设置 `whiteSpace=wrap;html=1`
- 保持标签简洁 — 每个形状最多 3 个词

**样式一致性**
- 在整个项目中始终使用第 3 步第 5 节的语义色板
- 优先使用 `edgeStyle=orthogonalEdgeStyle` 以获得干净的直角连接器
- 除非必要，否则不要在标签中内联任意 HTML

**文件命名**
- 使用连字符：`order-service-flow.drawio`，`database-schema.drawio`
- 将图表与它们所文档化的代码放在一起：`docs/` 或 `architecture/`

---

## 8. 故障排除

| 问题 | 可能原因 | 解决方法 |
|---|---|---|
| 在 VS Code 中文件打开为空白 | 缺少 id=0 或 id=1 的单元格 | 在任何其他单元格之前添加两个根单元格 |
| 图形位置错误 | 容器内的子元素 — 坐标是相对的 | 检查 `parent`；相对于容器调整 x/y 坐标 |
| 边缘不可见 | source 或 target id 与任何顶点不匹配 | 验证两个 id 是否完全按原文存在 |
| 图表显示 "压缩" | mxGraphModel 是 base64 编码的 | 在 draw.io 网页中打开，文件 > 导出 > XML（未压缩） |
| 图形样式未渲染 | shape= 名称中存在拼写错误 | 检查 `references/shape-libraries.md` 以获取确切的样式字符串 |
| 标签显示转义的 HTML | 单元格上 html=0 且带有 HTML 标签 | 在单元格样式中添加 `html=1;` |
| 容器子元素与容器边缘重叠 | 容器高度太小 | 在 mxGeometry 中增加容器高度 |

---

## 9. 验证清单

在交付任何生成的 `.drawio` 文件之前，请验证：

- [ ] 文件以 `<mxfile>` 根元素开头
- [ ] 每个 `<diagram>` 都有一个非空的 `id` 属性
- [ ] `<mxCell id="0" />` 是每个图表中的第一个单元格
- [ ] `<mxCell id="1" parent="0" />` 是每个图表中的第二个单元格
- [ ] 所有单元格的 `id` 值在每个图表中都是唯一的
- [ ] 每个顶点单元格都有 `vertex="1"` 和一个作为 `geometry` 的 `<mxGeometry>` 子元素
- [ ] 每个边单元格都有 `edge="1"` 并满足以下条件之一：(a) `source`/`target` 指向现有的顶点 id，或 (b) 在其 `<mxGeometry>` 中包含 `<mxPoint as="sourcePoint">` 和 `<mxPoint as="targetPoint">`（浮点边 — 用于序列图生命线）
- [ ] 除 id=0 外，每个单元格都有一个指向现有 id 的 `parent`
- [ ] 包含 HTML 标签的标签样式中包含 `html=1`
- [ ] XML 格式正确（无未关闭的标签，无未转义的 `&`、`<`、`>` 在属性值中）
- [ ] 每页顶部存在一个标题标签单元格

运行自动验证器：
```bash
python .github/skills/draw-io-diagram-generator/scripts/validate-drawio.py <file.drawio>
```

---

## 10. 输出格式

交付图表时，始终提供：

1. **`.drawio` 文件** 写入到请求的路径
2. **一句话摘要** 说明图表展示的内容
3. **如何打开它**：
   > "在 VS Code 中打开 `<filename>` — draw.io 扩展程序将自动渲染它。或者，你也可以在 draw.io 网页应用或桌面应用中打开它（如果更喜欢）。"
4. **如何编辑它**（如果用户可能进行自定义）：
   > "点击任何图形以选择它。双击以编辑标签。拖动以重新定位。"
5. **验证状态** — 验证器脚本是否运行并通过

---

## 11. 参考

所有配套文件都在 `.github/skills/draw-io-diagram-generator/` 中：

| 文件 | 内容 |
|---|---|
| `references/drawio-xml-schema.md` | 完整的 mxfile / mxGraphModel / mxCell 属性参考、坐标系、保留单元格、验证规则 |
| `references/style-reference.md` | 所有样式键及其允许值、顶点和边样式键、图形目录、语义调色板 |
| `references/shape-libraries.md` | 所有图形库类别（通用、流程图、UML、ER、网络、BPMN、模型、K8s）及其样式字符串 |
| `assets/templates/flowchart.drawio` | 可用的流程图模板 |
| `assets/templates/architecture.drawio` | 4 层系统架构模板 |
| `assets/templates/sequence.drawio` | 3 角色序列图模板 |
| `assets/templates/er-diagram.drawio` | 3 表格 ER 图，包含鸟键关系 |
| `assets/templates/uml-class.drawio` | 接口 + 2 类 + 枚举，带关系箭头 |
| `scripts/validate-drawio.py` | 验证任何 `.drawio` 文件 XML 结构的 Python 脚本 |
| `scripts/add-shape.py` | 将新图形添加到现有图表的 Python 命令行工具 |
| `scripts/README.md` | 如何使用脚本及示例 |
