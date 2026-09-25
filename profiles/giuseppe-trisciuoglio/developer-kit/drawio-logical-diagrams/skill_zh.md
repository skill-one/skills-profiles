# draw.io 逻辑图创建

## 概述

使用 draw.io 的原生 XML 格式创建专业的逻辑图，用于逻辑流程图、系统架构可视化和抽象过程表示，使用通用形状和符号。

## 何时使用

- 创建显示系统组件之间数据流的逻辑流程图
- 设计逻辑架构图（抽象系统结构）
- 构建BPMN业务流程图
- 绘制UML图（类、序列、活动、状态）
- 创建用于系统分析的DFD（数据流图）
- 制作具有分支逻辑的决策流程图
- 可视化系统交互和序列
- 无需云特定信息的逻辑系统设计文档

**不应用于：** AWS/Azure/GCP架构图（使用 `aws-drawio-architecture-diagrams`）。

## 说明

### 创建逻辑图

1. **分析请求**：理解要绘制的系统/流程
2. **选择图类型**：流程图、架构图、BPMN、UML、DFD等
3. **识别元素**：确定参与者、过程、数据存储、连接器
4. **草拟XML结构**：创建具有适当根单元的mxGraphModel
5. **添加形状**：创建具有适当样式的mxCell元素
6. **添加连接器**：使用边元素连接元素
7. **验证XML**：验证XML格式良好且所有ID唯一（见下方验证清单）
8. **输出**：为用户编写.drawio文件

### XML验证清单

在输出文件前，请验证：

- [ ] 所有标签均正确关闭（无未关闭的`<mxCell>`、`</mxGeometry>`等）
- [ ] 所有单元ID唯一（0和1为保留的根单元，使用从2开始的连续整数）
- [ ] 所有`source`和`target`属性引用现有单元ID
- [ ] 所有`parent`属性引用现有单元ID
- [ ] 所有坐标（x, y, width, height）为正数
- [ ] 特殊字符被转义（`<` → `&lt;`，`>` → `&gt;`，`&` → `&amp;`）
- [ ] 多行标签使用`&#xa;`或`<br>`与`html=1`样式

### 关键XML组件

| 组件 | 描述 |
|-------|-------|
| `mxfile` | 根元素，包含主机和版本 |
| `diagram` | 包含图表定义 |
| `mxGraphModel` | 画布设置（网格、页面大小） |
| `root` | 所有单元的容器（必须包含id="0"和id="1"） |
| `mxCell` | 单个形状（顶点）或连接器（边） |

## draw.io XML结构

```xml
<mxfile host="app.diagrams.net" agent="Claude" version="24.7.17">
  <diagram id="logical-flow-1" name="Logical Flow">
    <mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" guides="1"
      tooltips="1" connect="1" arrows="1" fold="1" page="1"
      pageScale="1" pageWidth="1169" pageHeight="827" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <!-- 形状和连接器在此处 -->
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

**关键规则：**
- ID "0"和"1"为根单元保留
- 使用从"2"开始的连续整数ID
- 架构图使用横向方向
- 所有坐标必须为正数并对齐网格（10的倍数）

## 通用形状和样式

### 基本形状类型

| 形状 | 样式 |
|-------|-------|
| 矩形 | `rounded=0;whiteSpace=wrap;html=1;` |
| 圆角矩形 | `rounded=1;whiteSpace=wrap;html=1;` |
| 椭圆/圆形 | `ellipse;whiteSpace=wrap;html=1;` |
| 菱形 | `rhombus;whiteSpace=wrap;html=1;` |
| 圆柱 | `shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;` |
| 六边形 | `shape=hexagon;perimeter=hexagonPerimeter2;whiteSpace=wrap;html=1;` |
| 梯形 | `shape=ext;double=1;rounded=0;whiteSpace=wrap;html=1;` |

### 标准颜色面板

| 元素类型 | 填充颜色 | 边框颜色 | 使用 |
|--------------|------------|--------------|-------|
| 过程 | `#dae8fc` | `#6c8ebf` | 操作/动作 |
| 决策 | `#fff2cc` | `#d6b656` | 条件分支 |
| 开始/结束 | `#d5e8d4` | `#82b366` | 终端状态 |
| 数据/存储 | `#e1f5fe` | `#0277bd` | 数据库/文件 |
| 实体 | `#f3e5f5` | `#7b1fa2` | 外部系统 |
| 错误/停止 | `#f8cecc` | `#b85450` | 错误状态 |
| 角色/用户 | `#ffe0b2` | `#f57c00` | 用户/角色 |
| 容器 | `#f5f5f5` | `#666666` | 分组区域 |

### 连接器样式

**标准流程：**
```
edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=classic;endFill=1;strokeColor=#666666;strokeWidth=2;
```

**虚线（替代/可选）：**
```
edgeStyle=orthogonalEdgeStyle;dashed=1;dashPattern=5 5;strokeColor=#666666;
```

**箭头头样式：**
- `endArrow=classic;endFill=1` - 填充三角形
- `endArrow=open;endFill=0` - 空心箭头
- `endArrow=blockThin;endFill=1` - 方形箭头

## 图表类型

| 类型 | 关键元素 |
|------|--------------|
| 逻辑流程 | 角色（橙色）、服务（蓝色）、数据存储（青色）、外部系统（紫色） |
| 逻辑架构 | 带嵌套组件的分层容器 |
| BPMN | 圆形（开始/结束）、圆角矩形（活动）、菱形（网关） |
| UML序列 | 垂直生命线与消息箭头 |
| DFD | 方形（实体）、圆形（过程）、开矩形（数据存储） |

## 参考文件

有关详细的形状示例和样式参考，请参阅：
- [shape-styles.md](references/shape-styles.md) - 完整形状示例和样式参考
- [diagram-templates.md](references/diagram-templates.md) - 即用模板

## 示例

### 示例1：订单处理流程

**请求：** "创建一个逻辑流程图，显示订单处理：客户提交订单，系统验证，如果有效则处理付款并发货，如果无效则通知客户。"

```xml
<mxfile host="app.diagrams.net" agent="Claude" version="24.7.17">
  <diagram id="order-flow-1" name="Order Processing">
    <mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="827" math="0" shadow="0">
      <root>
        <mxCell id="0"/><mxCell id="1" parent="0"/>
        <mxCell id="2" value="开始" style="ellipse;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=12;" vertex="1" parent="1"><mxGeometry x="80" y="50" width="80" height="40" as="geometry"/></mxCell>
        <mxCell id="3" value="提交订单" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;" vertex="1" parent="1"><mxGeometry x="60" y="130" width="120" height="60" as="geometry"/></mxCell>
        <mxCell id="4" value="验证订单?" style="rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=12;" vertex="1" parent="1"><mxGeometry x="80" y="230" width="80" height="80" as="geometry"/></mxCell>
        <mxCell id="5" value="通知客户" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;fontSize=12;" vertex="1" parent="1"><mxGeometry x="220" y="240" width="100" height="50" as="geometry"/></mxCell>
        <mxCell id="6" value="处理付款" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;" vertex="1" parent="1"><mxGeometry x="60" y="350" width="120" height="60" as="geometry"/></mxCell>
        <mxCell id="7" value="发货订单" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;" vertex="1" parent="1"><mxGeometry x="60" y="450" width="120" height="60" as="geometry"/></mxCell>
        <mxCell id="8" value="结束" style="ellipse;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=12;" vertex="1" parent="1"><mxGeometry x="80" y="550" width="80" height="40" as="geometry"/></mxCell>
        <mxCell id="10" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#666666;strokeWidth=2;" edge="1" parent="1" source="2" target="3"><mxGeometry relative="1" as="geometry"/></mxCell>
        <mxCell id="11" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#666666;strokeWidth=2;" edge="1" parent="1" source="3" target="4"><mxGeometry relative="1" as="geometry"/></mxCell>
        <mxCell id="12" value="否" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#b85450;strokeWidth=2;fontSize=11;" edge="1" parent="1" source="4" target="5"><mxGeometry relative="1" as="geometry"/></mxCell>
        <mxCell id="13" value="是" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#82b366;strokeWidth=2;fontSize=11;" edge="1" parent="1" source="4" target="6"><mxGeometry relative="1" as="geometry"/></mxCell>
        <mxCell id="14" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#666666;strokeWidth=2;" edge="1" parent="1" source="6" target="7"><mxGeometry relative="1" as="geometry"/></mxCell>
        <mxCell id="15" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#666666;strokeWidth=2;" edge="1" parent="1" source="7" target="8"><mxGeometry relative="1" as="geometry"/></mxCell>
        <mxCell id="16" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#b85450;strokeWidth=2;" edge="1" parent="1" source="5" target="8"><mxGeometry relative="1" as="geometry"/></mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

### 示例2：三层逻辑架构

**请求：** "为具有表示层、业务逻辑层和数据层的Web应用程序创建逻辑架构图。"

```xml
<mxfile host="app.diagrams.net" agent="Claude" version="24.7.17">
  <diagram id="three-tier-1" name="Three-Tier Architecture">
    <mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="827" math="0" shadow="0">
      <root>
        <mxCell id="0"/><mxCell id="1" parent="0"/>
        <mxCell id="2" value="用户" style="ellipse;whiteSpace=wrap;html=1;fillColor=#ffe0b2;strokeColor=#f57c00;fontSize=12;" vertex="1" parent="1"><mxGeometry x="40" y="340" width="60" height="40" as="geometry"/></mxCell>
        <mxCell id="3" value="表示层" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;fontSize=14;fontStyle=1;" vertex="1" parent="1"><mxGeometry x="160" y="40" width="300" height="180" as="geometry"/></mxCell>
        <mxCell id="4" value="Web浏览器" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;" vertex="1" parent="3"><mxGeometry x="20" y="30" width="80" height="50" as="geometry"/></mxCell>
        <mxCell id="5" value="移动应用" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;" vertex="1" parent="3"><mxGeometry x="120" y="30" width="80" height="50" as="geometry"/></mxCell>
        <mxCell id="7" value="应用层" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;fontSize=14;fontStyle=1;" vertex="1" parent="1"><mxGeometry x="160" y="260" width="300" height="180" as="geometry"/></mxCell>
        <mxCell id="8" value="API网关" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=12;" vertex="1" parent="7"><mxGeometry x="20" y="30" width="80" height="50" as="geometry"/></mxCell>
        <mxCell id="9" value="业务逻辑" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;" vertex="1" parent="7"><mxGeometry x="110" y="30" width="80" height="50" as="geometry"/></mxCell>
        <mxCell id="11" value="数据层" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;fontSize=14;fontStyle=1;" vertex="1" parent="1"><mxGeometry x="160" y="480" width="300" height="180" as="geometry"/></mxCell>
        <mxCell id="12" value="主数据库" style="shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;fillColor=#e1f5fe;strokeColor=#0277bd;fontSize=12;" vertex="1" parent="11"><mxGeometry x="20" y="30" width="60" height="80" as="geometry"/></mxCell>
        <mxCell id="13" value="缓存" style="shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;fillColor=#fff3e0;strokeColor=#e65100;fontSize=12;" vertex="1" parent="11"><mxGeometry x="100" y="30" width="60" height="80" as="geometry"/></mxCell>
        <mxCell id="20" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#666666;strokeWidth=2;" edge="1" parent="1" source="2" target="4"><mxGeometry relative="1" as="geometry"/></mxCell>
        <mxCell id="21" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#666666;strokeWidth=2;" edge="1" parent="1" source="4" target="8"><mxGeometry relative="1" as="geometry"/></mxCell>
        <mxCell id="22" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#666666;strokeWidth=2;" edge="1" parent="1" source="8" target="9"><mxGeometry relative="1" as="geometry"/></mxCell>
        <mxCell id="23" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#666666;strokeWidth=2;" edge="1" parent="1" source="9" target="12"><mxGeometry relative="1" as="geometry"/></mxCell>
        <mxCell id="24" value="查询" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=open;endFill=0;strokeColor=#666666;strokeWidth=1;fontSize=10;dashed=1;" edge="1" parent="1" source="9" target="13"><mxGeometry relative="1" as="geometry"/></mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

有关其他模板（微服务架构、事件驱动、决策树、序列、DFD），请参阅[diagram-templates.md](references/diagram-templates.md)。

## 限制和警告

### 关键限制

1. **XML有效性**：始终正确关闭标签并转义特殊字符
2. **唯一ID**：所有单元ID必须唯一（除父单元"0"和"1"外）
3. **有效引用**：`source`/`target`必须引用现有单元ID
4. **正坐标**：所有x, y值必须 >= 0

### 警告

- XML文件必须格式良好，否则将在draw.io中无法打开
- 无效的父引用会导致元素消失
- 负坐标将元素放置在可见画布之外

## 最佳实践

1. 在所有图表中为每种元素类型使用一致的颜色
2. 保持箭头笔直，弯曲最小
3. 将标签放置在箭线至少20px处
4. 将相关元素分组到容器中
5. 使用12-14px字体大小用于标签，10-11px用于注释
6. 所有坐标对齐网格（10的倍数）
7. 使用高对比度颜色，不要仅依赖颜色传递含义
