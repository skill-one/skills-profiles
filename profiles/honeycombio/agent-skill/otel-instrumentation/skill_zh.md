# OpenTelemetry Honeycomb 仪器化

SDK 设置、自定义追踪段、属性、追踪段事件、采样和分层遥测。

关于概念基础（为什么宽事件很重要，属性如何连接到调查），请参阅 **observability-fundamentals** 技能。

## OTLP 配置和 SDK 设置

每个 OTel SDK 需要这些环境变量才能将数据发送到 Honeycomb：

### 必要的环境变量

**基本配置：**
```bash
OTEL_SERVICE_NAME=your-service-name
OTEL_EXPORTER_OTLP_ENDPOINT=https://api.honeycomb.io
OTEL_EXPORTER_OTLP_HEADERS="x-honeycomb-team=YOUR_API_KEY"
```

**可选但推荐：**
```bash
# 协议选择（默认：http/protobuf）
OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf  # 或 grpc

# 信号特定端点（覆盖基本端点以特定信号）
OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=https://api.honeycomb.io/v1/traces
OTEL_EXPORTER_OTLP_METRICS_ENDPOINT=https://api.honeycomb.io/v1/metrics
```

**对于指标（首选）：** 使用现代 OTLP 指标和原生数据点。使用数据集提示来确认目标类型（`metrics` 或 `events`）。使用以下方式验证：
```bash
OTEL_EXPORTER_OTLP_METRICS_HEADERS="x-honeycomb-team=YOUR_API_KEY"
```

### 协议选择

`OTEL_EXPORTER_OTLP_PROTOCOL` 决定了线路格式和传输：
- `http/protobuf`（默认，推荐）— HTTP 使用 protobuf 编码
- `grpc` — 使用 protobuf 编码的 gRPC
- `http/json` — 使用 JSON 编码的 HTTP（负载较大，较慢）

除非您有特定的基础设施要求使用 gRPC，否则请使用 `http/protobuf`。

### 信号特定端点

默认情况下，OTel SDK 将 `/v1/traces` 和 `/v1/metrics` 添加到 `OTEL_EXPORTER_OTLP_ENDPOINT`。
使用信号特定端点变量来覆盖：
- `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT` — 完整的追踪 URL（包括 `/v1/traces`）
- `OTEL_EXPORTER_OTLP_METRICS_ENDPOINT` — 完整的指标 URL（包括 `/v1/metrics`）

当将信号路由到不同的后端或使用非标准端点时，这很有用。

### 常见陷阱

**静默认证失败：** OTLP 导出器需要 `x-honeycomb-team` 标头进行认证。如果没有它，Honeycomb 将静默拒绝请求——没有错误，没有数据。设置 `OTEL_EXPORTER_OTLP_HEADERS="x-honeycomb-team=YOUR_API_KEY"` 或以编程方式传递标头。如果从 `.env` 加载密钥，请确保 dotenv 在 SDK 初始化之前运行。

**指标：** 优先使用现代 OTLP 指标和原生数据点。数据集提示标识目标类型（`metrics` 或 `events`），因此默认情况下不要添加 `x-honeycomb-dataset`。仅在提示或配置需要将旧路由到命名事件数据集时使用该标头。追踪不需要它；它们通过 `service.name` 路由。

有关环境变量值、语言特定依赖项和设置代码（Go、Python、Node.js、Java、Ruby、.NET、Rust），请参阅
`${CLAUDE_PLUGIN_ROOT}/skills/otel-instrumentation/references/sdk-setup-by-language.md`。

## 自定义仪器化

### 向现有追踪段添加属性（最高影响）

向自动仪器化的追踪段添加业务上下文——不需要新的追踪段。从上下文中获取当前追踪段并调用 `SetAttributes`（Go）、`set_attribute`（Python）或 `setAttribute`（Node.js），并使用用户、租户、业务和部署上下文。

### 创建自定义追踪段

包装重要的业务操作以在追踪瀑布中可见。使用 `tracer.Start(ctx, "operation-name")`（Go）、`tracer.start_as_current_span("operation-name")`（Python）或 `tracer.startActiveSpan("operation-name", callback)`（Node.js）。

有关所有语言中的完整代码示例，请参阅
`${CLAUDE_PLUGIN_ROOT}/skills/otel-instrumentation/references/custom-instrumentation.md`。

## 何时创建追踪段

并非每个函数都需要追踪段。两个问题决定了是否值得创建追踪段：

1. **它是否有趣？** — 这项工作是否对整体请求的性能（延迟或失败）有显著影响？
2. **它是否可聚合？** — 如果按名称和属性分组此追踪段，它是否会产生有用的趋势和比较？

| 操作 | 有趣吗？ | 可聚合吗？ | 创建追踪段吗？ |
| :--- | :--- | :--- | :--- |
| HTTP 请求处理器 | 是——可变延迟，可能失败 | 是——按路由、方法、状态分组 | **是** |
| 数据库查询 | 是——I/O 密集型，易出错 | 是——按查询类型、表分组 | **是** |
| 外部 API 调用 | 是——网络延迟、依赖关系 | 是——按端点、状态分组 | **是** |
| 缓存查找 | 是——快速与慢速路径 | 是——按缓存名称、命中/未命中分组 | **是** |
| 消息队列发布/消费 | 是——异步边界、延迟 | 是——按队列、消息类型分组 | **是** |
| 业务逻辑事务 | 是——有意义的状态变化 | 是——按类型、结果分组 | **是** |
| 私有辅助函数 | 否——微不足道的 CPU，可预测 | 否——过于细致 | **否** |
| 循环迭代 | 可能——如果慢 | 否——无界基数 | **否** |
| 获取器/设置器 | 否——没有有意义的持续时间 | 否——没有可分组的 | **否** |
| 输入验证（纯 CPU） | 否——快速、可预测 | 可能 | **否** |
| 业务逻辑编排 | 否——只是调用仪器化代码 | 否——持续时间是子代之和 | **否** |

**常见错误：**
- **追踪段过多：** 包含数百万个 2ms 追踪段的追踪过于详细且很少具有可操作性。将它们合并——合并为一个追踪段，或者将详细信息作为父追踪段的属性捕获。
- **追踪段过少：** 将数小时的工作合并为单个不透明的处理器，让您猜测时间花在哪里。
- **遗留测试追踪段：** 名为 `test-span`、`debug-span` 或类似的追踪段是污染数据集的产物。在完成之前，删除任何仅用于验证追踪是否正常工作的追踪段。

不确定时，请优先考虑在现有追踪段上使用**属性**，而不是创建新的子追踪段。

#### 时间属性（无需子追踪段测量子操作）

将重要的子操作持续时间作为属性记录在父追踪段上。与子追踪段相比，这些更容易查询，并且可以直接与 BubbleUp 一起使用。

```go
// Go：时间认证并在现有追踪段上记录
span := trace.SpanFromContext(r.Context())
authStart := time.Now()
user, err := authenticate(r)
span.SetAttributes(attribute.Float64("auth.duration_ms", float64(time.Since(authStart).Milliseconds())))
```

```python
# Python：时间认证并在现有追踪段上记录
span = trace.get_current_span()
auth_start = time.monotonic()
user = authenticate(request)
span.set_attribute("auth.duration_ms", (time.monotonic() - auth_start) * 1000)
```

#### 异常遥测：事件详细信息加上追踪段级维度

使用 Logs API 发送新的异常事件。在相关追踪段活动时发送记录，并包括标准异常字段（`exception.type`、`exception.message`、`exception.stacktrace`，当适用时 `exception.escaped`）、ERROR 严重性，以及 `event.name="exception"`。当操作失败时，单独将追踪段状态设置为 ERROR。

在 Honeycomb 中，与追踪关联的异常日志在追踪中显示为 `span_event` 注释，并携带 `trace.trace_id` 和 `trace.parent_id`。其完整的 `exception.*` 负载保留在派生自日志的事件上；它**不会**被提升到包含的追踪段上。搜索异常事件行，然后跟随其追踪 ID 检查周围的追踪。

使用低基数追踪属性进行聚合和告警：
- `error=true` 和追踪段状态指示操作失败。
- `exception.slug` 是错误位置的静态、可搜索标识符。
- 可选的错误类别比完整的异常消息更安全，用于 `GROUP BY`。

```text
Logs-API 异常事件：event.name=exception, body=exception, meta.signal_type=log
遗留追踪段事件异常：name=exception, meta.signal_type=trace
两者都可能具有：meta.annotation_type=span_event
```

`record_exception` / `RecordError` 仍然是现有 SDK 和代码的兼容性 API，但在 Logs API 支持可用时，不要将其作为唯一的指导。它们还可以产生父追踪段异常字段，而单独的 Logs-API 事件不会产生。

通过追踪段维度查找操作失败：`WHERE error = true AND exception.slug does-not-exist`。
查找 Logs-API 异常事件：`event.name=exception AND exception.type exists`，并跟随采样的 `trace.trace_id` 进入 `get_trace`，并设置 `show_events=true`。

有关扩展示例和 MCP 调查配方，请参阅
`${CLAUDE_PLUGIN_ROOT}/skills/otel-instrumentation/references/custom-instrumentation.md`。

#### 可选的兼容性：使用 LogRecordProcessor 提升异常字段

如果现有的追踪段级仪表板、告警或查询依赖于 Honeycomb 历史上的异常字段提升，请在批处理/导出处理器之前添加自定义 **LogRecordProcessor**。当它看到异常日志时，它应该使用日志记录的解析上下文来找到正在记录的追踪段，并提升配置的最小字段集，例如 `error=true`、`error.type`、`exception.type`、`exception.slug` 或错误类别。

不推荐使用独立的 `SpanProcessor`：追踪处理器接收追踪生命周期回调，而不是日志记录。默认情况下保留完整的 `exception.message` 和 `exception.stacktrace` 在 Logs API 事件上；仅在遗留查询兼容性明确要求时才将它们复制到追踪段上。处理器必须在追踪上下文有效时同步运行，在日志到达批处理导出之前。当没有正在记录的追踪段时，它应该 no-op，并且不得推断日志记录未在日志记录中添加的字段。

这是一个可选的迁移层，而不是查询 Logs API 事件。代理应将追踪段提升字段视为依赖仪器的，并继续查询 `event.name=exception` 事件行以进行完整诊断。

## 仪器化什么

### 高价值（首先仪器化）
- API 入口点（HTTP 处理器、gRPC 方法）
- 数据库查询（大多数 SDK 自动仪器化）
- 外部 HTTP 调用（大多数 SDK 自动仪器化）
- 消息队列生产者/消费者

这些通常由 OTel SDK 自动仪器化，并形成您追踪的骨架。

### 中等价值（下一步）
- 业务逻辑操作（结账、支付、履行）
- 缓存操作（命中、未命中、驱逐）
- 身份验证和授权检查
- 后台作业执行

这些是您的业务逻辑。如果没有在此处添加自定义追踪段，您可以看到请求很慢，但不知道*为什么*——追踪瀑布中有间隙，其中重要的工作无法可见。

### 要添加的属性

属性是 BubbleUp 在调查期间使用的维度。您添加的每个属性都是 BubbleUp 可以用于比较以找出异常请求差异的新轴。
有关按类别组织的完整目录、推理和示例查询，请参阅
`${CLAUDE_PLUGIN_ROOT}/skills/otel-instrumentation/references/wide-event-attributes.md`。

关于属性在概念上为何重要的原因，请参阅 **observability-fundamentals** 技能。

## 追踪段事件、Logs API 事件和追踪段链接

- **时间点事件**：优先使用 Logs API 发送新事件，尤其是异常。在追踪段活动时发送，以便记录携带追踪上下文。在 Honeycomb 中，相关联的日志显示为 `meta.annotation_type=span_event` 注释，但其事件名称在 `event.name`（通常 `body`）中，而不是 `name`。
- **遗留追踪段事件**：`span.add_event` / `AddEvent` 仍然是有效的兼容性路径。其事件名称在 `name` 中，其信号类型是 `trace`。
- **追踪段链接**：连接不同追踪层次结构中的追踪段（异步处理、发散/汇聚、跨系统关联）。创建一个 `Link` 到相关的追踪段上下文。

有关人类仪器化示例和安全的 Honeycomb MCP 查询→样本→追踪工作流，请参阅
`${CLAUDE_PLUGIN_ROOT}/skills/otel-instrumentation/references/custom-instrumentation.md`
和 **production-investigation** 技能。

## 采样

### 采样策略

采样是权衡——没有免费的午餐：

- **头部采样** 优先考虑成本而不是可调试性。您节省了资源，但 0.1% 的错误在 1% 的采样率下实际上会消失。头部采样对下游发生的事情无感知。
- **尾部采样** 优先考虑保真度而不是简单性。您保留有趣的追踪，但需要基础设施（Refinery 或 Collector）来缓冲和评估完整的追踪。

数学很重要：如果错误发生率为 0.1%，而您以 1% 头部采样，您将捕获大约 1/100,000 的这些错误。在中等流量下，该错误可能永远不会出现在您的数据中。

### 头部采样（SDK 级别）
在创建追踪段时决定是否采样。简单但可能会错过有趣的追踪段。
- 通过 `OTEL_TRACES_SAMPLER` 环境变量配置
- `always_on`（默认）、`always_off`、`traceidratio`（例如，采样 10%）
- `parentbased_traceidratio` 尊重父代采样决策
- **适用于**：非常高吞吐量的服务，您可以容忍错过罕见事件

### 尾部采样（Collector/Refinery）
在追踪段完成后决定。保留有趣的追踪段（错误、慢请求）。
- 使用 Honeycomb 的 **Refinery** 进行生产尾部采样
- 或配置 OTel Collector 的 `tail_sampling` 处理器
- 可以基于：延迟、错误状态、特定属性、追踪持续时间采样
- **适用于**：调试性重要的服务——保留错误和异常，同时采样常规流量

### 采样对 Honeycomb 的影响
- 采样减少数据量并降低成本
- SLOs、BubbleUp 和查询结果自动调整采样率
- 追踪完整性可能受影响——如果服务未一致采样，可能会丢失追踪段
- 从不采样开始，然后根据需要添加以进行成本管理

## 分层遥测

OpenTelemetry 是“追踪优先”的——上下文传播是关联所有信号粘合剂。但有效的可观察性会为不同目的叠加多个信号类型。

选择正确信号的三问测试：

1. **什么需要因果关系和完整请求上下文？** → 追踪（追踪段）
2. **什么需要低成本长期存储和快速告警？** → 指标
3. **什么罕见与常见，以及审计要求是什么？** → 日志/事件

**跨追踪段显示直方图的模式：** 对于高吞吐量 HTTP 服务，为每个处理的请求同时发出一个追踪段和一个直方图指标。这允许您以 1% 的采样率采样追踪段以控制成本，而直方图提供最后的救命稻草告警——并且示例将异常指标点链接回特定追踪段以进行更深入的调查。

该技术是*分层*（而不是重复），因为每个信号提供不同级别的不同视图。

有关分层对于流式传输、异步作业、ETL 和无服务器架构至关重要的架构模式，请参阅
`${CLAUDE_PLUGIN_ROOT}/skills/otel-instrumentation/references/architectural-patterns.md`。

有关 AWS Lambda 特定模式——在 AWS 管理的 OTel 层和手动 SDK 设置之间进行选择、forceFlush、SDK 2.x 设置、跨 Lambda 追踪传播、标头规范化、TOKEN 与 REQUEST 授权器迁移——请参阅
`${CLAUDE_PLUGIN_ROOT}/skills/otel-instrumentation/references/lambda.md`。

## Honeycomb 中的日志

OTel 也可以发送日志。如果您有现有的日志基础设施，OTel Collector 可以摄取日志并将它们作为结构化事件转发到 Honeycomb：

- **OTel SDK 日志桥接器**：捕获现有日志库的日志（Go 中的 `slog`、Python 中的 `logging`、Node.js 中的 `winston`/`pino`）并将其作为 OTel 日志记录导出。
- **OTel Collector `filelog` 接收器**：读取日志文件，解析它们，导出为 OTLP。

通过 OTel 发送的日志以结构化事件的形式到达 Honeycomb，具有与追踪相同的查询功能。

## 命名约定

- **追踪段名称**：描述操作（`HTTP GET /api/users`、`db.query SELECT`、`process-payment`）
- **属性名称**：使用点分隔的命名空间（`user.id`、`order.total`、`cache.hit`）
- **遵循 OTel 语义约定**，如果适用（`http.method`、`db.system`、`rpc.service`）
- **自定义属性**：使用您自己的命名空间（`app.`、`checkout.`、`mycompany.`）

## 其他资源

### 参考文件
- **`${CLAUDE_PLUGIN_ROOT}/skills/otel-instrumentation/references/sdk-setup-by-language.md`** — Go、Python、Node.js、Java、Ruby、.NET、Rust 的 OTLP 配置和 SDK 设置
- **`${CLAUDE_PLUGIN_ROOT}/skills/otel-instrumentation/references/local-collector-debug-test.md`** — 通过 Docker 运行本地 OTel Collector 以验证追踪段、日志和指标，而无需 Honeycomb 账户；包括用于检查 NDJSON 输出的 `jq` 命令
- **`${CLAUDE_PLUGIN_ROOT}/skills/otel-instrumentation/references/custom-instrumentation.md`** — 自定义仪器化模式，带完整代码示例（时间属性、异常 slugs、异步请求摘要）
- **`${CLAUDE_PLUGIN_ROOT}/skills/otel-instrumentation/references/collector-config.md`** — OTel Collector 配置，用于格式转换、处理和采样
- **`${CLAUDE_PLUGIN_ROOT}/skills/otel-instrumentation/references/wide-event-attributes.md`** — 按类别组织的规范属性目录，附带示例查询
- **`${CLAUDE_PLUGIN_ROOT}/skills/otel-instrumentation/references/architectural-patterns.md`** — 流式传输、异步、ETL 和无服务器架构的追踪设计模式
- **`${CLAUDE_PLUGIN_ROOT}/skills/otel-instrumentation/references/lambda.md`** — AWS Lambda：OTel 层与手动 SDK 设置权衡、forceFlush 和每个请求延迟、SDK 2.x 设置、跨 Lambda 追踪传播、标头规范化、TOKEN 与 REQUEST 授权器迁移

### 跨参考
- 对于为什么宽事件和属性很重要的概念基础：**observability-fundamentals** 技能
- 仪器化后，使用 **query-patterns** 技能验证数据是否已到达
