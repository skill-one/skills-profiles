# 应用服务技能

使用 DQL 监控应用服务性能、健康状态和特定运行时指标。

---

## 核心能力

### 1. 服务性能（RED 指标）

使用基于指标的时序查询监控服务的 **速率、错误、耗时**。

**关键指标：**
- `dt.service.request.response_time` - 响应时间（微秒）
- `dt.service.request.count` - 请求次数
- `dt.service.request.failure_count` - 失败请求次数

**常见用例：**
- 响应时间监控（平均、p50、p95、p99）
- 错误率跟踪和峰值检测
- 流量分析（吞吐量、峰值、增长）
- 性能下降检测
- 多集群比较

**快速示例：**
```dql
timeseries {
  p95 = percentile(dt.service.request.response_time, 95),
  total_requests = sum(dt.service.request.count),
  failures = sum(dt.service.request.failure_count)
}, by: {dt.service.name}
| fieldsAdd p95_ms = p95[] / 1000, error_rate_pct = (failures[] * 100.0) / total_requests[]
```

→ **对于详细查询：** 参考 [references/service-metrics.md](references/service-metrics.md)

### 2. 高级服务分析

基于跨度的查询，适用于需要灵活过滤和自定义聚合的复杂场景。

**用例：**
- 基于自定义阈值的 SLA 合规性跟踪
- 多维度的服务健康评分
- 操作/端点级别的性能分析
- 自定义错误分类
- 基于错误详情的失败模式检测

**快速示例：**
```dql
fetch spans, from: now() - 1h | filter request.is_root_span == true
| fieldsAdd meets_sla = if(request.is_failed == false AND duration < 3s, 1, else: 0)
| summarize total = count(), sla_compliant = sum(meets_sla), by: {dt.service.name}
| fieldsAdd sla_compliance_pct = (sla_compliant * 100.0) / total
```

→ **对于详细查询：** 参考 [references/service-metrics.md](references/service-metrics.md)

### 3. 服务消息指标

监控基于消息的服务通信（队列、主题）。

**关键指标：**
- `dt.service.messaging.publish.count` - 发送到队列或主题的消息数
- `dt.service.messaging.receive.count` - 从队列或主题接收的消息数
- `dt.service.messaging.process.count` - 成功处理的消息数
- `dt.service.messaging.process.failure_count` - 处理失败的消息数

**用例：**
- 消息吞吐量监控（发布/接收速率）
- 消息处理失败跟踪
- 队列/主题健康分析
- 消费者延迟检测（发布与接收速率比较）

**快速示例：**
```dql
timeseries {
  published = sum(dt.service.messaging.publish.count),
  received = sum(dt.service.messaging.receive.count),
  processed = sum(dt.service.messaging.process.count),
  failed = sum(dt.service.messaging.process.failure_count)
}, by: {dt.service.name}
```

→ **对于详细查询：** 参考 [references/service-metrics.md](references/service-metrics.md)

### 4. 服务网格监控

监控服务网格入口性能和开销。

**关键指标：**
- `dt.service.request.service_mesh.response_time` - 网格响应时间（微秒）
- `dt.service.request.service_mesh.count` - 网格请求次数
- `dt.service.request.service_mesh.failure_count` - 网格失败次数

**用例：**
- 网格与直接性能比较
- 网格开销计算
- 网格失败分析
- gRPC 流量监控
- 多集群网格性能

**快速示例：**
```dql
timeseries {
  direct_p95 = percentile(dt.service.request.response_time, 95),
  mesh_p95 = percentile(dt.service.request.service_mesh.response_time, 95)
}, by: {dt.service.name}
| fieldsAdd mesh_overhead_ms = (mesh_p95[] - direct_p95[]) / 1000
```

→ **对于详细查询：** 参考 [references/service-metrics.md](references/service-metrics.md)

### 5. 特定运行时监控

特定技术运行时性能和资源使用指标。

**Java/JVM** - [references/java.md](references/java.md)
- 内存：堆、池、元空间
- GC：影响、暂停、频率、暂停时间
- 线程：计数监控、泄漏检测
- 类：加载、卸载、增长

**Node.js** - [references/nodejs.md](references/nodejs.md)
- 事件循环：利用率、活跃句柄
- V8 堆：内存使用、总量
- GC：收集时间、暂停
- 进程：RSS 内存

**.NET CLR** - [references/dotnet.md](references/dotnet.md)
- 内存：按代消耗
- GC：收集次数、暂停时间
- 线程池：线程、排队工作
- JIT：编译时间

**Python** - [references/python.md](references/python.md)
- 线程：活跃线程计数
- 堆：分配块
- GC：按代收集、暂停时间
- 对象：收集、不可收集

**PHP** - [references/php.md](references/php.md)
- OPcache：命中率、内存、重启
- GC：有效性、持续时间
- JIT：缓冲区使用
- Interned strings：使用、缓冲区

**Go** - [references/go.md](references/go.md)
- Goroutines：计数、泄漏检测
- GC：暂停、收集时间
- 内存：按状态堆、提交
- 调度器：工作线程、队列大小
- CGo：调用频率

---

## 使用此技能的场景

✅ **适用于：**
- 监控服务性能（响应时间、错误、流量）
- 计算 SLA 合规性
- 分析服务网格性能
- 监控消息吞吐量和处理失败
- 排查特定运行时问题（GC、内存、线程）
- 多集群服务比较
- 操作/端点级别分析

❌ **不适用于：**
- 基础设施指标（使用基础设施技能）
- 日志分析（使用日志技能）
- 分布式追踪工作流（使用 traces/spans 技能）
- 数据库性能（使用数据库技能）
- 产品文档或配置问题 → 使用 `ask-dynatrace-docs`

---

## 代理指令

### 先执行，后优化

当用户请求分析——阈值检查、异常检测、性能比较——**立即**使用合理的默认值。不要询问用户你可以合理假设的参数值。

为什么这很重要：分析工具（例如 `static-threshold-analyzer`）需要特定的输入，如阈值值和服务范围。用户期望结果，而不是参数访谈。选择合理的默认值，在响应中明确说明，并允许用户优化。

**未指定时的默认值：**

| 参数 | 默认值 | 理由 |
|-----------|---------|-----------|
| 响应时间阈值 | 1000 ms (= 1,000,000 µs 在指标的基单位中) | 常见 SLA 边界 |
| 服务范围 | 所有服务 | 显示最相关的违规 |
| 时间范围 | 从请求，或阈值检查的 30 分钟，一般分析的 2 小时 | 匹配典型的操作窗口 |

**示例：阈值违规请求**
1. 使用 `create-dql` 构建一个 `avg(dt.service.request.response_time)` 的时序查询，按 `dt.smartscape.service` 分组
2. 将查询传递给 `static-threshold-analyzer`，阈值 = 1000000 (µs)，alertCondition = ABOVE
3. 使用 `get-entity-name` 解析实体 ID 为名称
4. 使用服务名称、时间戳、值和持续时间呈现违规

**理解用户措辞：** 像 "固定阈值"、"阈值" 或 "限制" 这样的短语命名的是 *类型* 的分析——静态阈值检查——而不是你期望已经知道的特定数字。"固定" 区分静态截止值与动态或季节性基线。当你看到这些短语时，应用上表中的 1000 ms 默认值并呈现结果——用户可以然后根据默认值是否符合他们的意图进行优化。

### 范围边界

此技能涵盖 **服务性能指标和特定运行时监控**。如果用户询问产品文档或配置问题（例如，"如何添加自定义传感器？"、"如何配置服务检测？"），请使用 `ask-dynatrace-docs`——此技能不包含配置指南。

### 理解用户意图

**将用户问题映射到功能：**

| 用户请求 | 使用功能 | 关键文件 |
|--------------|----------------|-----------|
| "服务性能"、"响应时间"、"错误率" | 服务性能 (RED) | service-metrics.md |
| "SLA 跟踪"、"健康评分" | 高级服务分析 | service-metrics.md |
| "服务网格"、"Istio"、"Linkerd"、"网格开销" | 服务网格监控 | service-metrics.md |
| "消息"、"队列"、"主题"、"发布"、"消费者" | 服务消息指标 | service-metrics.md |
| "JVM GC"、"Java 内存"、"堆" | 特定运行时 (Java) | java.md |
| "Node.js 事件循环"、"V8 堆" | 特定运行时 (Node.js) | nodejs.md |
| ".NET CLR"、"GC 代" | 特定运行时 (.NET) | dotnet.md |
| "Python GC"、"线程计数" | 特定运行时 (Python) | python.md |
| "OPcache"、"PHP GC" | 特定运行时 (PHP) | php.md |
| "goroutines"、"Go GC"、"调度器" | 特定运行时 (Go) | go.md |

### 查询构建模式

**1. 基于指标的（时序）**
- **用于：** 标准监控、仪表板、告警
- **模式：** `timeseries <metric> = <aggregation>(<metric_name>), by: {dimensions}`
- **文件：** service-metrics.md、所有特定运行时文件

**2. 基于跨度的（fetch spans）**
- **用于：** 复杂过滤、自定义逻辑、详细分析
- **模式：** `fetch spans | filter request.is_root_span == true | fieldsAdd ... | summarize ...`
- **文件：** service-metrics.md（高级服务分析部分）

**3. 比较查询**
- 使用 `append` 进行基线比较
- 使用 `shift: -15m` 进行时间偏移基线
- **示例：** 性能下降检测

### 响应构建指南

**始终包括：**
1. **指标名称** - 清晰的指标标识符
2. **聚合方式** - 数据如何聚合（平均、求和、百分位数）
3. **分组** - 使用的维度 (`dt.service.name`, `k8s.workload.name` 等)
4. **单位转换** - 在适当情况下将微秒转换为毫秒
5. **过滤** - 相关阈值或条件

**在引用特定运行时内容时：**
- **检查** 用户的技术栈
- **仅提供** 相关的特定运行时查询（不要用所有 6 个运行时淹没用户）
- **解释** 特定运行时指标（例如，"OPcache 命中率"衡量 PHP 操作码缓存效率）

---

## 常见工作流

### 工作流：服务健康检查
```
1. 检查响应时间（RED 指标）
2. 检查错误率（RED 指标）
3. 检查流量模式（RED 指标）
4. 如果怀疑特定运行时问题 → 加载特定运行时参考
```

### 工作流：SLA 监控
```
1. 定义 SLA 标准（例如，< 3s 响应时间 AND < 1% 错误率）
2. 使用基于跨度的查询进行自定义 SLA 逻辑
3. 计算合规百分比
4. 过滤非合规服务
```

### 工作流：服务网格分析
```
1. 检查网格响应时间
2. 比较网格与直接性能
3. 计算网格开销
4. 分析网格失败率
```

### 工作流：特定运行时故障排除
1. 确定技术栈 → 加载特定运行时参考
2. 检查内存/GC 指标 → 线程/goroutines → 运行时功能

---

## 故障排除

| 问题 | 原因 | 解决方案 |
|---------|-------|----------|
| 响应时间值看起来太大 | 指标以微秒为单位 | 除以 1000 转换为毫秒 |
| 没有服务网格指标数据 | 服务网格未配置 | 验证网格边车注入是否启用 |
| 运行时指标缺失 | 错误的技术或没有 OneAgent | 确认运行时是否受支持且 OneAgent 处于活动状态 |
| `dt.smartscape.service` 返回 SmartscapeId，而不是名称 | 需要实体名称解析 | 使用 `getNodeName(dt.smartscape.service)` |
| 错误率始终为零 | 使用了错误的失败指标 | 使用 `dt.service.request.failure_count`，而不是自定义字段 |

---

## 参考

**核心服务监控：**
- [references/service-metrics.md](references/service-metrics.md) - 完整 RED 指标、SLA 跟踪、服务网格查询

**特定运行时监控：**
- [references/java.md](references/java.md) - Java/JVM 监控
- [references/nodejs.md](references/nodejs.md) - Node.js 监控  
- [references/dotnet.md](references/dotnet.md) - .NET CLR 监控
- [references/python.md](references/python.md) - Python 监控
- [references/php.md](references/php.md) - PHP 监控
- [references/go.md](references/go.md) - Go 运行时监控
