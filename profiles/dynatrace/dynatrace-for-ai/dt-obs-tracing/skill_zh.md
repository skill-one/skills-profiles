# 应用追踪技能

## 概述

Dynatrace中的分布式追踪由跨度组成——代表工作单元的基本单元。通过Grail中的追踪功能，每个跨度都可以通过DQL访问，并且所有属性都支持全文搜索。本技能涵盖了追踪基础知识、常见分析模式以及特定跨度类型的查询。

---

## 用例

### 1. 调查缓慢请求
- **目标**：查找并诊断超过延迟阈值的请求
- **触发条件**："缓慢请求"、"高延迟"、"p99响应时间"、"查找超过5秒的追踪"
- **完成**：列出缓慢追踪，包含持续时间、端点、服务和追踪ID，用于深入分析

### 2. 分析请求失败
- **目标**：识别失败请求、失败原因和异常模式
- **触发条件**："失败跨度"、"HTTP 500错误"、"异常分析"、"按服务失败率"
- **完成**：按原因（HTTP代码、异常、gRPC状态）进行失败分解，并提供示例追踪

### 3. 映射服务依赖关系
- **目标**：理解服务之间的通信模式和外部API调用
- **触发条件**："服务依赖关系"、"X调用哪些服务"、"出站HTTP调用"
- **完成**：显示服务之间调用次数、延迟和错误率的依赖关系图

---

## 核心概念

### 理解追踪和跨度

**跨度**代表分布式追踪中的逻辑工作单元：
- HTTP请求、RPC调用、数据库操作
- 消息系统交互
- 内部函数调用
- 自定义仪器点

**跨度类型**：
- `span.kind: server` - 服务接收的入站调用
- `span.kind: client` - 服务发出的出站调用
- `span.kind: consumer` - 服务接收消息消费的入站调用
- `span.kind: producer` - 服务发出消息生产的出站调用
- `span.kind: internal` - 服务内部的内部操作

**根跨度**：入站调用请求根跨度（`request.is_root_span == true`）代表服务接收的入站调用。使用此功能分析端到端请求性能。

### 关键追踪属性

追踪分析的基本属性：

| 属性 | 描述 |
|-----------|-------------|
| `trace.id` | 唯一追踪标识符 |
| `span.id` | 唯一跨度标识符 |
| `span.parent_id` | 父跨度ID（根跨度为null） |
| `request.is_root_span` | 布尔值，请求入口为true |
| `request.is_failed` | 布尔值，如果请求失败则为true |
| `duration` | 跨度持续时间（纳秒） |
| `span.timing.cpu` | 跨度的整体CPU时间（稳定） |
| `span.timing.cpu_self` | 排除子跨度后的CPU时间（稳定） |
| `dt.smartscape.service` | 服务Smartscape节点ID |
| `dt.service.name` | Dynatrace服务名称，通过服务检测规则派生。它等于Smartscape服务节点名称。 |
| `endpoint.name` | 端点/路由名称 |

### 服务上下文

跨度通过Smartscape节点ID和检测到的服务名称`dt.service.name`引用服务，该名称也存在于每个跨度中。

```dql
fetch spans
| summarize spans=count(), by: { dt.smartscape.service, dt.service.name }
```

**节点函数**：
- `getNodeName(dt.smartscape.service)` - 添加`dt.smartscape.service.name`字段，包含人类可读的服务名称
- `getNodeField(dt.smartscape.service, "attribute_name")` - 访问特定节点属性

**📖 了解更多**：有关高级实体选择器、基础设施关联和硬件分析的详细信息，请参阅[实体查找](references/entity-lookups.md)。

### 采样和推算

由于以下原因，一个跨度可以代表多个实际操作：
- **聚合**：一个跨度中包含多个操作（`aggregation.count`）
- **ATM（自适应流量管理）**：基于代理的头部采样
- **ALR（自适应负载减少）**：服务器端采样
- **读取采样**：通过`samplingRatio`参数的查询时采样

**何时推算**：在计算实际操作数量时始终推算（不仅仅是跨度）。使用乘数因子：

```dql
fetch spans
| fieldsAdd sampling.probability = (power(2, 56) - coalesce(sampling.threshold, 0)) * power(2, -56)
| fieldsAdd sampling.multiplicity = 1 / sampling.probability
| fieldsAdd multiplicity = coalesce(sampling.multiplicity, 1)
                         * coalesce(aggregation.count, 1)
                         * dt.system.sampling_ratio
| summarize operation_count = sum(multiplicity)
```

**📖 了解更多**：有关详细公式和示例，请参阅[采样和推算](references/sampling-extrapolation.md)。

## 常见查询模式

### 基本跨度访问

获取跨度并按类型探索：

```dql
fetch spans | limit 1
```

按函数和类型探索跨度：

```dql
fetch spans
| summarize count(), by: { span.kind, code.namespace, code.function }
```

### 请求根过滤

列出请求根跨度（服务入站调用）：

```dql
fetch spans
| filter request.is_root_span == true
| fields trace.id, span.id, start_time, response_time = duration, endpoint.name
| limit 100
```

### 服务性能摘要

使用错误率分析服务性能：

```dql
fetch spans
| filter request.is_root_span == true
| summarize
    total_requests = count(),
    failed_requests = countIf(request.is_failed == true),
    avg_duration = avg(duration),
    p95_duration = percentile(duration, 95),
  by: {dt.service.name}
| fieldsAdd error_rate = (failed_requests * 100.0) / total_requests
| sort error_rate desc
```

### 追踪ID查找

查找特定追踪中的所有跨度：

```dql
fetch spans
| filter trace.id == toUid("abc123def456")
| fields span.name, duration, dt.service.name
```

## 性能分析

### 响应时间百分位数

按端点计算百分位数：

```dql
fetch spans
| filter request.is_root_span == true
| summarize {
    requests=count(),
    avg_duration=avg(duration),
    p95=percentile(duration, 95),
    p99=percentile(duration, 99)
  }, by: { endpoint.name }
| sort p99 desc
```

**💡 最佳实践**：使用百分位数（p95、p99）而不是平均值进行性能分析。

### 缓慢追踪检测

查找超过阈值的请求：

```dql
fetch spans, from:now() - 2h
| filter request.is_root_span == true
| filter duration > 5s
| fields trace.id, span.name, dt.service.name, duration
| sort duration desc
| limit 50
```

### 持续时间桶与示例

```dql
fetch spans, from:now() - 24h
| filter http.route == "/api/v1/storage/findByISBN"
| summarize {
    spans=count(),
    trace=takeAny(record(start_time, trace.id))
  }, by: { bin(duration, 10ms) }
| fields `bin(duration, 10ms)`, spans, trace.id=trace[trace.id], start_time=trace[start_time]
```

### 性能时间序列

提取响应时间作为时间序列：

```dql
fetch spans, from:now() - 24h
| filter request.is_root_span == true
| makeTimeseries {
    requests=count(),
    avg_duration=avg(duration),
    p95=percentile(duration, 95),
    p99=percentile(duration, 99)
  }, by: { endpoint.name }
```

**📖 了解更多**：有关高级模式和时序技术，请参阅[性能分析](references/performance-analysis.md)。

## 失败调查

### 失败请求摘要

按服务汇总失败：

```dql
fetch spans
| filter request.is_root_span == true
| summarize
    total = count(),
    failed = countIf(request.is_failed == true),
  by: { dt.service.name }
| fieldsAdd failure_rate = (failed * 100.0) / total
| sort failure_rate desc
```

### 失败原因分析

按失败检测原因分解：

```dql
fetch spans
| filter request.is_failed == true and isNotNull(dt.failure_detection.results)
| expand dt.failure_detection.results
| summarize count(), by: { dt.failure_detection.results[reason] }
```

**失败原因**：
- `http_code` - 触发失败的HTTP响应代码
- `grpc_code` - 触发失败的gRPC状态代码
- `exception` - 导致失败的异常
- `span_status` - 指示失败的跨度状态
- `custom_rule` - 匹配的自定义失败检测规则

### HTTP代码失败

按HTTP状态代码查找失败：

```dql
fetch spans
| filter request.is_failed == true
| filter iAny(dt.failure_detection.results[][reason] == "http_code")
| summarize count(), by: { http.response.status_code, endpoint.name }
| sort `count()` desc
```

### 最近失败请求

列出带详细信息的最近失败：

```dql
fetch spans
| filter request.is_root_span == true and request.is_failed == true
| fields
    start_time,
    trace.id,
    endpoint.name,
    http.response.status_code,
    duration
| sort start_time desc
| limit 100
```

**📖 了解更多**：有关异常分析和自定义规则调查，请参阅[失败检测](references/failure-detection.md)。

## 服务依赖关系

### 服务间分析

分析服务通信模式：

```dql
fetch spans, from:now() - 1h
| filter isNotNull(server.address)
| fieldsAdd
    remote_side = server.address
| summarize
    call_count = count(),
    avg_duration = avg(duration),
    by: {dt.service.name, remote_side}
| sort call_count desc
```

### 出站HTTP调用

识别外部API依赖关系：

```dql
fetch spans
| filter span.kind == "client" and isNotNull(http.request.method)
| summarize
    calls = count(),
    avg_latency = avg(duration),
    p99_latency = percentile(duration, 99),
  by: { dt.service.name, server.address, server.port }
| sort calls desc
```

## 追踪聚合

### 完整追踪分析

聚合追踪中的所有跨度，以了解完整请求流程：

```dql
fetch spans, from:now() - 30m
| summarize {
    spans = count(),
    client_spans = countIf(span.kind == "client"),

    // 追踪中涉及的端点
    endpoints = toString(arrayRemoveNulls(collectDistinct(endpoint.name))),

    // 提取追踪中的第一个请求根
    trace_root = takeMin(record(
        root_detection_helper = coalesce(
            if(request.is_root_span, 1),
            if(isNull(span.parent_id), 2),
            3),
        start_time, endpoint.name, duration
      ))
}, by: { trace.id }

| fieldsFlatten trace_root
| fieldsRemove trace_root.root_detection_helper, trace_root

| fields
    start_time = trace_root.start_time,
    endpoint = trace_root.endpoint.name,
    response_time = trace_root.duration,
    spans,
    client_spans,
    endpoints,
    trace.id
| sort start_time
| limit 100
```

**根检测策略**：使用`takeMin(record(...))`与检测助手可靠地找到根请求：
1. 优先级1：`request.is_root_span == true`的跨度
2. 优先级2：没有父节点的跨度（根跨度）
3. 优先级3：所有其他跨度

### 多服务追踪

查找跨越多个服务的追踪：

```dql
fetch spans, from:now() - 1h
| summarize {
    services = collectDistinct(dt.service.name),
    trace_root = takeMin(record(root_detection_helper = coalesce(if(request.is_root_span, 1), 2), endpoint.name))
}, by: { trace.id }
| fieldsAdd service_count = arraySize(services)
| filter service_count > 1
| fields endpoint = trace_root[endpoint.name], service_count, services = toString(services), trace.id
| sort service_count desc
| limit 50
```

## 请求级分析

### 请求属性

访问OneAgent在请求根跨度上捕获的自定义请求属性：

```dql
fetch spans
| filter request.is_root_span == true
| filter isNotNull(request_attribute.PaidAmount)
| makeTimeseries sum(request_attribute.PaidAmount)
```

**字段模式**：`request_attribute.<name>`, `captured_attribute.<name>`（始终为数组）

→ [请求属性](references/request-attributes.md) — 请求属性、捕获属性和请求ID聚合的完整模式

## 跨度类型

| 跨度类型 | 检测 | 关键字段 | 参考 |
|-----------|-------|------------|-----------|
| HTTP服务器（入站） | `span.kind == "server" and isNotNull(http.request.method)` | `http.route`, `http.request.method`, `http.response.status_code` | [http-spans.md](references/http-spans.md) |
| HTTP客户端（出站） | `span.kind == "client" and isNotNull(http.request.method)` | `server.address`, `server.port` | [http-spans.md](references/http-spans.md) |
| 数据库 | `span.kind == "client" and isNotNull(db.system)` | `db.system`, `db.namespace`, `db.statement` | [database-spans.md](references/database-spans.md) |
| 消息 | `isNotNull(messaging.system)` | `messaging.system`, `messaging.destination.name`, `messaging.operation.type` | [messaging-spans.md](references/messaging-spans.md) |
| RPC / gRPC | `isNotNull(rpc.system)` | `rpc.system`, `rpc.service`, `rpc.method`, `rpc.grpc.status_code` | [rpc-spans.md](references/rpc-spans.md) |
| 无服务器 / FaaS | `isNotNull(faas.name) and span.kind == "server"` | `faas.name`, `faas.trigger.type`, `cloud.provider` | [serverless-spans.md](references/serverless-spans.md) |

**⚠️ 数据库跨度**：可以聚合（一个跨度=N次调用）。始终使用`aggregation.count`推算以获得准确的操作计数。

**📖 每种跨度类型的详细模式**：请参阅上述参考文件。

## 高级主题

### 异常分析

异常存储为跨度内的`span.events`：

```dql
fetch spans
| filter iAny(span.events[][span_event.name] == "exception")
| expand span.events
| fieldsFlatten span.events, fields: { exception.type }
| summarize {
    count(),
    trace=takeAny(record(start_time, trace.id))
  }, by: { exception.type }
| fields exception.type, `count()`, trace.id=trace[trace.id], start_time=trace[start_time]
```

**💡 小贴士**：使用`iAny()`检查跨度事件数组中的条件。

→ [日志关联](references/logs-correlation.md) — 连接日志和追踪，按日志内容过滤追踪
→ [网络分析](references/networking-analysis.md) — 客户端IP、DNS解析、子网分析

## 最佳实践

| 领域 | 规则 |
|------|------|
| **过滤** | 首先应用`request.is_root_span == true`和端点过滤 |
| **采样** | 使用`samplingRatio`（例如，`100` = 读取1%）以提高性能 |
| **百分位数** | 使用p95/p99而不是平均值进行性能分析 |
| **根跨度** | 使用`request.is_root_span == true`进行端到端分析 |
| **追踪分组** | 按`trace.id`分组以获取完整追踪指标 |
| **请求分组** | 按`request.id`分组以获取仅OneAgent请求指标 |
| **推算** | 始终应用乘数因子以获得准确的操作计数 |
| **示例** | 使用`takeAny(record(start_time, trace.id))`以启用UI深入分析 |

---

## 故障排除

| 问题 | 原因 | 解决方案 |
|---------|-------|----------|
| 持续时间值似乎不正确（太大） | `duration`以纳秒为单位，不是毫秒 | 除以`1000000`或与`5s`（DQL持续时间字面量）比较 |
| 跨度计数与预期请求量不匹配 | 未考虑采样或聚合 | 使用乘数推算——请参阅采样和推算参考 |
| `getNodeName(dt.smartscape.service)` 返回null | 服务尚未解析或OneAgent未监控 | 验证OneAgent是否监控该服务；实体解析可能有短延迟 |
| `request.is_root_span` 过滤器返回空 | 查询仅OpenTelemetry的追踪而没有OneAgent | 使用`isNull(span.parent_id)`作为根跨度检测的备用方法 |
| `trace.id` 过滤器返回无结果 | 追踪ID未转换为UID格式 | 使用`filter trace.id == toUid("abc123...")`用于基于字符串的追踪ID |
| 数据库跨度计数过低 | 数据库跨度被聚合（一个跨度=N次调用） | 始终使用`aggregation.count`推算以获得数据库操作计数 |

## 相关技能

- **dt-dql-essentials** — 查询追踪数据的DQL核心语法
- **dt-app-dashboards** — 将追踪查询嵌入仪表板
- **dt-migration** — Smartscape实体模型和关系导航

---

## 参考

特定主题的详细文档：

- **[性能分析](references/performance-analysis.md)** - 高级时序、持续时间桶、端点排名
- **[失败检测](references/failure-detection.md)** - 失败原因、异常调查、自定义规则
- **[采样和推算](references/sampling-extrapolation.md)** - 乘数计算、数据库推算
- **[请求属性](references/request-attributes.md)** - 请求属性、捕获属性、请求ID聚合
- **[实体查找](references/entity-lookups.md)** - 高级节点查找、基础设施关联、硬件分析
- **[HTTP跨度分析](references/http-spans.md)** - 状态代码、有效载荷分析、客户端IP
- **[数据库跨度分析](references/database-spans.md)** - 推算计数、慢查询、语句分析
- **[消息跨度分析](references/messaging-spans.md)** - Kafka、RabbitMQ、SQS吞吐量和延迟
- **[RPC跨度分析](references/rpc-spans.md)** - gRPC、SOAP、服务依赖关系
- **[无服务器跨度分析](references/serverless-spans.md)** - Lambda、Azure Functions、冷启动分析
- **[日志关联](references/logs-correlation.md)** - 连接日志和追踪、关联模式
- **[网络分析](references/networking-analysis.md)** - IP地址、DNS解析、通信映射
