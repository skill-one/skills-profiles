---
name: golang-observability
description: Go日常可观测性——生产环境中的持续信号。涵盖结构化日志记录（使用slog）、Prometheus指标、OpenTelemetry分布式追踪、使用pprof/Pyroscope的持续性能分析、服务器端RUM事件追踪、告警以及Grafana仪表盘。适用于为生产监控配置Go服务、设置指标或告警、添加OpenTelemetry追踪、关联日志与追踪、将旧日志记录器（zap/logrus/zerolog）迁移至slog、为新功能添加可观测性，或使用客户数据平台（CDP）实现符合GDPR/CCPA要求的追踪。不适用于临时性的深度性能分析（→参见`samber/cc-skills-golang@golang-benchmark`和`samber/cc-skills-golang@golang-performance`技能）。
---

**角色：** 你是一位 Go 可观测性工程师。你将每一个未被观测的生产系统视为负债——主动进行监控，关联信号以诊断，并且永不将一个功能视为完成，直到它变得可观测。

**编排模式：** 在审计模式下，将五个信号特定的子代理（指标、日志、追踪、剖析、RUM）分发出去，以审计代码库中的可观测性覆盖范围，并合并它们的覆盖结果。在 Claude Code 中，使用 `ultracode` 明确启用多代理编排。

**模式：**

- **编码/监控**（默认）：为新的或现有的代码添加可观测性——声明指标，添加片段，设置结构化日志，配置 pprof 开关。遵循顺序监控指南。
- **审查模式**——审查 PR 的监控变更。检查新代码是否导出了预期的信号（声明的指标、打开和关闭的片段、结构化日志字段一致）。顺序执行。
- **审计模式**——审计代码库中现有的可观测性覆盖范围。启动最多 5 个并行子代理——每个信号一个（指标、日志、追踪、剖析、RUM）——以同时检查覆盖范围。

> **社区默认。** 如果公司技能明确覆盖了 `samber/cc-skills-golang@golang-observability` 技能，则优先使用该技能。

# Go 可观测性最佳实践

可观测性是指通过系统的外部输出理解其内部状态的能力。在 Go 服务中，这意味着五个互补的信号：**日志**、**指标**、**追踪**、**剖析**和**RUM**。每个信号回答不同的问题，它们共同为你提供对系统行为和用户体验的全面可见性。

在使用可观测性库（Prometheus 客户端、OpenTelemetry SDK、供应商集成）时，请参考库的官方文档和代码示例以获取当前的 API 签名。

## 最佳实践摘要

1. **使用结构化日志**与 `log/slog` — 生产服务必须发出结构化日志（JSON），而不是自由形式的字符串。
2. **选择合适的日志级别** — 调试用于开发，信息用于正常操作，警告用于降级状态，错误用于需要关注的失败情况。
3. **带上下文记录日志** — 使用 `slog.InfoContext(ctx, ...)` 将日志与追踪关联起来。
4. **优先使用 Histogram 而不是 Summary** 用于延迟指标 — Histogram 支持服务器端聚合和百分位数查询。每个 HTTP 端点必须具有延迟和错误率指标。
5. **在 Prometheus 中保持标签基数低** — 绝对不要使用无界值（用户 ID、完整 URL）作为标签值。
6. **使用 Histograms + `histogram_quantile()` 在 PromQL 中跟踪百分位数**（P50、P90、P99、P99.9）。
7. **在新项目中设置 OpenTelemetry 追踪** — 早期配置 TracerProvider，然后在所有地方添加片段。
8. **为每个有意义的操作添加片段** — 服务方法、数据库查询、外部 API 调用、消息队列操作。
9. **到处传播上下文** — 上下文是跨服务边界传递 trace_id、span_id 和截止日期的载体。
10. **通过环境变量启用剖析** — 无需重新部署即可开启/关闭 pprof 和持续剖析。
11. **关联信号** — 将 trace_id 注入日志，使用 exemplars 将指标与追踪关联起来。
12. **功能只有在可观测时才算完成** — 声明指标，添加适当的日志，创建片段。
13. **[awesome-prometheus-alerts](https://samber.github.io/awesome-prometheus-alerts/) 提供约 500 个现成的告警规则**，按技术分类，用于基础设施和依赖项监控。

## 参考文档

- → 查看 `samber/cc-skills-golang@golang-error-handling` 技能以了解单一处理规则。
- → 查看 `samber/cc-skills-golang@golang-troubleshooting` 技能以了解使用可观测性信号诊断生产问题。
- → 查看 `samber/cc-skills-golang@golang-security` 技能以保护 pprof 端点并避免日志中的 PII。
- → 查看 `samber/cc-skills@promql-cli` 技能以从 CLI 查询和探索 Prometheus 中的 PromQL 表达式。

### Go 1.26+: slog multi-handler

对于简单的分发到多个 slog handler，优先使用标准库 `slog.NewMultiHandler`，然后再添加第三方 handler-composition 依赖。

```go
logger := slog.New(slog.NewMultiHandler(
    slog.NewJSONHandler(os.Stdout, nil),
    auditHandler,
))
```

仅在标准库 handler-composition 不足以满足需求时，才使用第三方 slog handler 库。

## 五种信号

| 信号 | 回答的问题 | 工具 | 使用场景 |
| --- | --- | --- | --- |
| **日志** | 发生了什么？ | `log/slog` | 离散事件、错误、审计记录 |
| **指标** | 多少 / 多快？ | Prometheus 客户端 | 聚合测量、告警、SLO |
| **追踪** | 时间去哪儿了？ | OpenTelemetry | 跨服务的请求流、延迟分解 |
| **剖析** | 为什么慢 / 使用内存？ | pprof、Pyroscope | CPU 热点、内存泄漏、锁竞争 |
| **RUM** | 用户如何体验？ | PostHog、Segment | 产品分析、漏斗、会话回放 |

## 详细指南

每种信号都有一个专门的指南，包含完整的代码示例、配置模式和成本分析：

- **[结构化日志](references/logging.md)** — 为什么结构化日志对于大规模日志聚合很重要。涵盖 `log/slog` 设置、日志级别（Debug/Info/Warn/Error）以及何时使用每个级别、请求与 trace ID 的关联、使用 `slog.InfoContext` 的上下文传播、请求范围的属性、slog 生态系统（handlers、formatters、middleware）以及从 zap/logrus/zerolog 迁移策略。

- **[指标收集](references/metrics.md)** — Prometheus 客户端设置和四种指标类型（Counter 用于变化率、Gauge 用于快照、Histogram 用于延迟聚合）。深入探讨：为什么 Histograms 比 Summaries 更好（支持服务器端聚合、支持 `histogram_quantile` PromQL）、命名约定、PromQL-as-comments 规则（在指标声明上方编写查询以提高可发现性）、生产级 PromQL 示例、多窗口 SLO 燃烧率告警，以及高基数标签问题（为什么无界值如用户 ID 会破坏性能）。

- **[分布式追踪](references/tracing.md)** — 何时以及如何使用 OpenTelemetry SDK 追踪跨服务的请求流。涵盖片段（创建、属性、状态记录）、`otelhttp` middleware 用于 HTTP 监控、使用 `span.RecordError()` 记录错误、追踪采样（为什么在大规模下无法收集所有数据）、跨服务边界传播追踪上下文，以及成本优化。

- **[剖析](references/profiling.md)** — 使用 pprof 进行按需剖析（CPU、堆、goroutine、mutex、block profiles）——如何在生产环境中启用它、使用认证保护它，以及通过环境变量在不重新部署的情况下切换。使用 Pyroscope 进行持续剖析以实现始终可见的性能。每种剖析类型的成本影响和缓解策略。

- **[真实用户监控](references/rum.md)** — 了解用户实际如何体验你的服务。涵盖产品分析（事件跟踪、漏斗）、Customer Data Platform 集成，以及关键合规性：GDPR/CCPA 同意检查、数据主体权利（用户删除端点），以及跟踪的隐私清单。服务器端事件跟踪（PostHog、Segment）和身份键最佳实践。

- **[告警](references/alerting.md)** — 主动问题检测。涵盖四个黄金信号（延迟、流量、错误、饱和度）、[awesome-prometheus-alerts](https://samber.github.io/awesome-prometheus-alerts/) 提供约 500 个按技术分类的现成规则、Go 运行时告警（goroutine 泄漏、GC 压力、OOM 风险）、严重级别，以及破坏告警的常见错误（使用 `irate` 而不是 `rate`、缺少 `for:` 持续时间以避免抖动）。

- **[Grafana 仪表板](references/dashboards.md)** — 用于 Go 运行时监控的预构建仪表板（堆分配、GC 暂停频率、goroutine 数量、CPU）。解释如何安装标准仪表板、如何根据你的服务自定义它们，以及每个仪表板如何回答不同的操作问题。

## 关联信号

当信号连接起来时，它们最强大。你的日志中的 trace_id 允许你从日志行跳转到完整的请求追踪。指标上的 exemplar 将延迟峰值与导致它的确切追踪关联起来。

### 日志 + 追踪：`otelslog` 桥接器

```go
import "go.opentelemetry.io/contrib/bridges/otelslog"

// 创建一个自动注入 trace_id 和 span_id 的 logger
logger := otelslog.NewHandler("my-service")
slog.SetDefault(slog.New(logger))

// 现在，每个带上下文的 slog 调用都包含追踪关联
slog.InfoContext(ctx, "order created", "order_id", orderID)
// 输出包括：{"trace_id":"abc123", "span_id":"def456", "msg":"order created", ...}
```

### 指标 + 追踪：Exemplars

```go
// 在记录 histogram 观察值时，将 trace_id 作为 exemplar 添加
// 这样你就可以从 P99 峰值直接跳转到有问题的追踪
obs := histogram.WithLabelValues("POST", "/orders")
if eo, ok := obs.(prometheus.ExemplarObserver); ok {
    eo.ObserveWithExemplar(duration, prometheus.Labels{"trace_id": traceID})
} else {
    obs.Observe(duration)
}
```

## 迁移旧日志记录器

如果项目当前使用 `zap`、`logrus` 或 `zerolog`，请迁移到 `log/slog`。它是 Go 1.21 以来标准库的日志记录器，具有稳定的 API，生态系统已围绕它进行整合。继续使用第三方日志记录器意味着维护一个没有好处的额外依赖项。

**迁移策略：**

1. 使用 `slog.SetDefault()` 添加 `slog` 作为新的日志记录器。
2. 在迁移期间，通过现有的日志记录器路由 slog 输出：[samber/slog-zap](https://github.com/samber/slog-zap)、[samber/slog-logrus](https://github.com/samber/slog-logrus)、[samber/slog-zerolog](https://github.com/samber/slog-zerolog)
3. 逐步替换所有 `zap.L().Info(...)` / `logrus.Info(...)` / `log.Info().Msg(...)` 调用为 `slog.Info(...)`
4. 完全迁移后，移除桥接器 handler 和旧的日志记录器依赖

## 可观测性的完成定义

功能在生产环境中准备就绪，当且仅当它变得可观测。在将功能标记为完成之前，请验证：

- [ ] **声明了指标** — 操作/错误计数器、延迟直方图、饱和度指标。每个指标变量在其声明上方都有 PromQL 查询和告警规则作为注释。
- [ ] **日志记录是正确的** — 使用 `slog` 的结构化键值对、使用上下文变体（`slog.InfoContext`）、日志中不包含 PII、错误必须被记录或返回（绝不能两者兼有）。
- [ ] **创建了片段** — 每个服务方法、数据库查询和外部 API 调用都有一个相关属性的片段，使用 `span.RecordError()` 记录错误。
- [ ] **存在仪表板和告警** — 你的指标注释中的 PromQL 已连接到 Grafana 仪表板和 Prometheus 告警规则。常见的基础设施依赖项的现成告警规则可在 [awesome-prometheus-alerts](https://samber.github.io/awesome-prometheus-alerts/) 获取。
- [ ] **跟踪了 RUM 事件** — 在服务器端跟踪关键业务事件（PostHog/Segment）、身份键是 `user_id`（不是电子邮件）、在跟踪前检查同意。

## 常见错误

```go
// ✗ 错误 — 同时记录和返回（错误在链中多次记录）
if err != nil {
    slog.Error("query failed", "error", err)
    return fmt.Errorf("query: %w", err)
}

// ✓ 正确 — 带上下文返回，在顶层只记录一次
if err != nil {
    return fmt.Errorf("querying users: %w", err)
}
```

```go
// ✗ 错误 — 高基数标签（无界用户 ID）
httpRequests.WithLabelValues(r.Method, r.URL.Path, userID).Inc()

// ✓ 正确 — 只有有界标签值
httpRequests.WithLabelValues(r.Method, routePattern).Inc()
```

```go
// ✗ 错误 — 未传递上下文（破坏追踪传播）
result, err := db.Query("SELECT ...")

// ✓ 正确 — 上下文传递，追踪继续
result, err := db.QueryContext(ctx, "SELECT ...")
```

```go
// ✗ 错误 — 使用 Summary 用于延迟（无法跨实例聚合）
prometheus.NewSummary(prometheus.SummaryOpts{
    Name:       "http_request_duration_seconds",
    Objectives: map[float64]float64{0.99: 0.001},
})

// ✓ 正确 — 使用 Histogram（可聚合，支持 histogram_quantile）
prometheus.NewHistogram(prometheus.HistogramOpts{
    Name:    "http_request_duration_seconds",
    Buckets: prometheus.DefBuckets,
})
```
