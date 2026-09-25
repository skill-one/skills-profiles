# 业务流程与集成图生成器

**快速入门：** 选择图类型 → 声明事件/网关/任务的模板图标 → 分组到池/泳道 → 使用箭头语法连接 → 用 ` ```plantuml ` 分隔符包裹。

> ⚠️ **重要提示：** 始终使用 ` ```plantuml ` 或 ` ```puml ` 代码分隔符。绝对不要使用 ` ```text ` — 它将不会渲染为图表。

## 关键规则

- 每个图表以 `@startuml` 开头并以 `@enduml` 结尾
- 使用 `left to right direction` 用于流程（从左到右读取 start→end）
- 使用 `mxgraph.bpmn.*` 用于 BPMN 事件、网关和任务标记
- 使用 `mxgraph.eip.*` 用于企业集成模式图标
- 使用 `mxgraph.lean_mapping.*` 用于价值流映射符号
- 默认颜色会自动应用 — 你不需要指定 `fillColor` 或 `strokeColor`
- 使用 `rectangle "Pool" { ... }` 用于 BPMN 池和泳道
- 顺序流使用 `-->`，消息流使用 `..>`（虚线）

**完整模板参考：** 参考 [stencils/README.md](../uml/stencils/README.md) 获取 9500+ 可用图标。

## Mxgraph 模板语法

```
mxgraph.<library>.<icon> "Label" as <alias>
```

### BPMN 模板系列 (`mxgraph.bpmn.*`)

**事件** — 圆形用于流程触发和结果：

| 图标 | 含义 |
|------|---------|
| `mxgraph.bpmn.event.start` | 开始事件 |
| `mxgraph.bpmn.event.end` | 结束事件 |
| `mxgraph.bpmn.event.terminateEnd` | 终止结束 |
| `mxgraph.bpmn.event.timerStart` | 定时开始 |
| `mxgraph.bpmn.event.timerCatching` | 定时中间 |
| `mxgraph.bpmn.event.messageStart` | 消息开始 |
| `mxgraph.bpmn.event.messageCatching` | 消息捕获 |
| `mxgraph.bpmn.event.messageEnd` | 消息结束 |
| `mxgraph.bpmn.event.errorEnd` | 错误结束 |
| `mxgraph.bpmn.event.errorBound` | 错误边界 |
| `mxgraph.bpmn.event.signalStart` | 信号开始 |
| `mxgraph.bpmn.event.signalEnd` | 信号结束 |

**网关** — 菱形用于分支/合并：

| 图标 | 含义 |
|------|---------|
| `mxgraph.bpmn.gateway2.exclusive` | 排他性网关 (XOR) |
| `mxgraph.bpmn.gateway2.parallel` | 并行网关 (AND) |
| `mxgraph.bpmn.gateway2.inclusive` | 包容性网关 (OR) |
| `mxgraph.bpmn.gateway2.complex` | 复杂网关 |

**任务** — 使用 `rectangle` 表示任务，模板标记表示类型任务：

| 图标 | 含义 |
|------|---------|
| `mxgraph.bpmn.user_task` | 用户任务 |
| `mxgraph.bpmn.service_task` | 服务任务 |
| `mxgraph.bpmn.script_task` | 脚本任务 |
| `mxgraph.bpmn.manual_task` | 手动任务 |
| `mxgraph.bpmn.business_rule_task` | 业务规则任务 |

**数据** — 类似文档的形状：

| 图标 | 含义 |
|------|---------|
| `mxgraph.bpmn.data2.dataObject` | 数据对象 |
| `mxgraph.bpmn.data2.dataInput` | 数据输入 |
| `mxgraph.bpmn.data2.dataOutput` | 数据输出 |

### EIP 模板系列 (`mxgraph.eip.*`)

| 图标 | 含义 |
|------|---------|
| `mxgraph.eip.messageChannel` | 消息通道 |
| `mxgraph.eip.deadLetterChannel` | 死信通道 |
| `mxgraph.eip.content_based_router` | 基于内容的路由器 |
| `mxgraph.eip.message_filter` | 消息过滤器 |
| `mxgraph.eip.splitter` | 分隔器 |
| `mxgraph.eip.aggregator` | 聚合器 |
| `mxgraph.eip.message_translator` | 消息转换器 |
| `mxgraph.eip.content_enricher` | 内容丰富器 |
| `mxgraph.eip.messaging_gateway` | 消息网关 |
| `mxgraph.eip.channel_adapter` | 通道适配器 |
| `mxgraph.eip.messaging_bridge` | 消息桥接器 |
| `mxgraph.eip.recipient_list` | 接收者列表 |
| `mxgraph.eip.wire_tap` | 线路监视器 |
| `mxgraph.eip.event_driven_consumer` | 事件驱动消费者 |
| `mxgraph.eip.competing_consumers` | 竞争消费者 |
| `mxgraph.eip.process_manager` | 进程管理器 |

### 价值流映射模板系列 (`mxgraph.lean_mapping.*`)

| 图标 | 含义 |
|------|---------|
| `mxgraph.lean_mapping.outside_sources` | 供应商/客户 |
| `mxgraph.lean_mapping.manufacturing_process` | 流程步骤 |
| `mxgraph.lean_mapping.supermarket` | 超市（库存缓冲区） |
| `mxgraph.lean_mapping.fifo_lane` | FIFO 泳道 |
| `mxgraph.lean_mapping.production_kanban` | 生产看板 |
| `mxgraph.lean_mapping.withdrawal_kanban` | 提取看板 |
| `mxgraph.lean_mapping.signal_kanban` | 信号看板 |
| `mxgraph.lean_mapping.truck_shipment` | 卡车运输 |
| `mxgraph.lean_mapping.operator` | 操作员 |
| `mxgraph.lean_mapping.inventory_box` | 库存 |
| `mxgraph.lean_mapping.kaizen_lightening_burst` | Kaizen 爆发 |
| `mxgraph.lean_mapping.mrp_erp` | MRP/ERP 系统 |
| `mxgraph.lean_mapping.warehouse` | 仓库 |
| `mxgraph.lean_mapping.push_arrow` | 推送箭头 |
| `mxgraph.lean_mapping.timeline2` | 时间线 |

### 连接类型

| 语法 | 含义 | 用例 |
|--------|---------|----------|
| `A --> B` | 实线箭头 | 顺序流（任务→任务） |
| `A ..> B` | 虚线箭头 | 消息流（跨池）/ 异步触发 |
| `A --> B : "label"` | 带标签的实线 | 条件流（网关分支） |
| `A ..> B : "label"` | 带标签的虚线 | 命名消息/信号 |

### 快速示例

```plantuml
@startuml
left to right direction

mxgraph.bpmn.event.start "开始" as start
rectangle "审核\n请求" as review
mxgraph.bpmn.gateway2.exclusive "已批准?" as gw
rectangle "处理\n订单" as process
rectangle "通知\n拒绝" as reject
mxgraph.bpmn.event.end "结束" as end_ok
mxgraph.bpmn.event.end "结束" as end_fail

start --> review
review --> gw
gw --> process : "是"
gw --> reject : "否"
process --> end_ok
reject --> end_fail
@enduml
```

## 图表类型

| 类型 | 目的 | 关键模板 | 示例 |
|------|---------|--------------|---------|
| 订单处理 | 电子商务/履行 | `mxgraph.bpmn.event.*`, `mxgraph.bpmn.gateway2.*` | [order-processing.md](examples/order-processing.md) |
| 审批工作流 | 多级审批 | `mxgraph.bpmn.event.*`, `mxgraph.bpmn.gateway2.*` | [approval-workflow.md](examples/approval-workflow.md) |
| EIP 消息 | 消息路由与转换 | `mxgraph.eip.*` | [eip-messaging.md](examples/eip-messaging.md) |
| ETL 管道 | 数据提取与加载 | `mxgraph.bpmn.event.*`, `mxgraph.eip.*` | [etl-pipeline.md](examples/etl-pipeline.md) |
| 价值流 | 精益制造流程 | `mxgraph.lean_mapping.*` | [value-stream.md](examples/value-stream.md) |
| 微服务编排 | 服务编排 | `mxgraph.bpmn.event.*`, `mxgraph.eip.*` | [microservice-orchestration.md](examples/microservice-orchestration.md) |
| 事件驱动架构 | 发布/订阅事件流 | `mxgraph.bpmn.event.*`, `mxgraph.eip.*` | [event-driven.md](examples/event-driven.md) |
| 客户服务 | 支持工单生命周期 | `mxgraph.bpmn.event.*`, `mxgraph.bpmn.gateway2.*` | [customer-service.md](examples/customer-service.md) |
