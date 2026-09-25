# APM 服务健康

使用 [可观测性 API](https://www.elastic.co/docs/solutions/observability/apis) 评估 APM 服务健康，通过 **ES|QL** 对 APM 索引、Elasticsearch API 以及（用于关联和 APM 特定逻辑）Kibana 仓库进行查询。使用 SLO、触发警报、机器学习异常、吞吐量、延迟（平均/p95/p99）、错误率和依赖项健康。

## 查找位置

- **可观测性 API** ([可观测性 API](https://www.elastic.co/docs/solutions/observability/apis))：使用 **SLO API** ([Stack](https://www.elastic.co/docs/api/doc/kibana/group/endpoint-slo) | [Serverless](https://www.elastic.co/docs/api/doc/serverless/group/endpoint-slo)) 获取 SLO 定义、状态、消耗速率和错误预算。使用 **警报 API** ([Stack](https://www.elastic.co/docs/api/doc/kibana/group/endpoint-alerting) | [Serverless](https://www.elastic.co/docs/api/doc/serverless/group/endpoint-alerting)) 列出和管理服务的警报规则及其警报。在需要时使用 **APM 注释 API** 创建或搜索注释。
- **ES|QL 和 Elasticsearch**：使用 **ES|QL** 查询 `traces*apm*,traces*otel*` 和 `metrics*apm*,metrics*otel*`，获取吞吐量、延迟、错误率和依赖项式聚合（见 [使用 ES|QL 查询 APM 指标](#using-esql-for-apm-metrics)）。使用 Elasticsearch API（例如 `POST _query` 用于 ES|QL，或查询 DSL）按 Elasticsearch 仓库中的文档对索引和搜索进行操作。
- **APM 关联**：运行 **apm-correlations** 脚本以获取与服务相关的高延迟或失败事务的属性。它首先尝试 Kibana 内部 APM 关联 API，然后回退到 `traces*apm*,traces*otel*` 上的 Elasticsearch significant_terms。见 [APM 关联脚本](#apm-correlations-script)。
- **基础设施**：通过 traces 中的 **资源属性**（例如 `k8s.pod.name`、`container.id`、`host.name`）进行关联；使用 ES|QL/Elasticsearch 查询基础设施或指标索引以获取 CPU 和内存。**OOM** 和 **CPU 限制** 直接影响 APM 健康。
- **日志**：使用 **ES|QL** 或 Elasticsearch 在按 `service.name` 或 `trace.id` 过滤的日志索引上进行搜索，以解释行为和根本原因。
- **可观测性实验室**：[可观测性实验室](https://www.elastic.co/observability-labs) 和 [APM 标签](https://www.elastic.co/observability-labs/blog/tag/apm) 用于查找模式和故障排除。

## 健康标准

在可用的情况下，综合以下所有因素来评估健康：

| 信号                | 检查内容                                                             |
| --------------------- | ------------------------------------------------------------------------- |
| **SLO**              | 消耗速率、状态（健康/退化/违反）、错误预算。                             |
| **触发警报**     | 服务或依赖项的开放或最近触发的警报。                                    |
| **机器学习异常**      | 异常作业；延迟、吞吐量或错误率的分数和严重程度。                        |
| **吞吐量**        | 请求率；与基线或先前时间段进行比较。                                   |
| **延迟**           | 平均、p95、p99；与 SLO 目标或历史记录进行比较。                         |
| **错误率**        | 失败/总请求；尖峰或持续升高。                                         |
| **依赖项健康** | 下游延迟、错误率、可用性（ES\|QL、API、Kibana 仓库）。                 |
| **基础设施**    | CPU 使用率、内存；pods/containers/hosts 上的 OOM 和 CPU 限制。       |
| **日志**              | 按 service 或 trace ID 过滤的应用日志，以获取上下文和根本原因。      |

如果 SLO 被违反、关键警报正在触发，或者机器学习异常表明严重退化，则将服务视为 **不健康**。通过基础设施（OOM、CPU 限制）、依赖项和日志（服务/trace 上下文）进行关联，以解释原因并建议下一步操作。

## 使用 ES|QL 查询 APM 指标

从 Elasticsearch 查询 APM 数据（`traces*apm*,traces*otel*`、`metrics*apm*,metrics*otel*`）时，在可用的情况下默认使用 **ES|QL**。

- **可用性**：ES|QL 在 **Elasticsearch 8.11+**（技术预览；8.14 中 GA）中可用。它在 [Elastic 可观测性 Serverless 完整层](https://www.elastic.co/docs/solutions/observability/observability-serverless-feature-tiers) 中始终可用。
- **限定为服务**：始终按 `service.name`（当相关时按 `service.environment`）进行过滤。结合 `@timestamp` 上的时间范围：

```esql
WHERE service.name == "my-service-name" AND service.environment == "production"
  AND @timestamp >= "2025-03-01T00:00:00Z" AND @timestamp <= "2025-03-01T23:59:59Z"
```

- **示例模式**：随时间变化的吞吐量、延迟和错误率：见 Kibana `trace_charts_definition.ts`（`getThroughputChart`、`getLatencyChart`、`getErrorRateChart`）。使用 `from(index)` → `where(...)` → `stats(...)` / `evaluate(...)`，并使用 `BUCKET(@timestamp, ...)` 和 `WHERE service.name == "<service_name>"`。
- **性能**：添加 `LIMIT n` 以限制行数和 token 使用。当只需要趋势时，优先使用较粗的 `BUCKET(@timestamp, ...)`（例如 1 小时）；较细的桶会增加工作量和结果大小。

## APM 关联脚本

当只有部分事务具有高延迟或失败时，运行 **apm-correlations** 脚本以列出与这些事务相关的属性（例如主机、服务版本、pod、区域）。脚本首先尝试 Kibana 内部 APM 关联 API；如果不可用（例如 404），则回退到 `traces*apm*,traces*otel*` 上的 Elasticsearch significant_terms。

```bash
# 延迟关联（在慢事务中过度表示的属性）
node skills/observability/service-health/scripts/apm-correlations.js latency-correlations --service-name <name> [--start <iso>] [--end <iso>] [--last-minutes 60] [--transaction-type <t>] [--transaction-name <n>] [--space <id>] [--json]

# 失败事务关联
node skills/observability/service-health/scripts/apm-correlations.js failed-correlations --service-name <name> [--start <iso>] [--end <iso>] [--last-minutes 60] [--transaction-type <t>] [--transaction-name <n>] [--space <id>] [--json]

# 测试 Kibana 连接
node skills/observability/service-health/scripts/apm-correlations.js test [--space <id>]
```

**环境**：`KIBANA_URL` 和 `KIBANA_API_KEY`（或 `KIBANA_USERNAME`/`KIBANA_PASSWORD`）用于 Kibana；对于回退，`ELASTICSEARCH_URL` 和 `ELASTICSEARCH_API_KEY`。使用与调查相同的时间范围。

## 工作流程

```text
服务健康进度:
- [ ] 第 1 步：确定服务（和时间范围）
- [ ] 第 2 步：检查 SLO 和触发警报
- [ ] 第 3 步：检查机器学习异常（如果配置）
- [ ] 第 4 步：检查吞吐量、延迟（平均/p95/p99）、错误率
- [ ] 第 5 步：评估依赖项健康（ES|QL/APIs / Kibana 仓库）
- [ ] 第 6 步：与基础设施和日志关联
- [ ] 第 7 步：总结健康并建议操作
```

### 第 1 步：确定服务

确认服务名称和时间范围。从请求中解析服务；如果范围内有多个服务，则针对最相关的一个。使用 ES|QL 在 `traces*apm*,traces*otel*` 或 `metrics*apm*,metrics*otel*` 上（例如 `WHERE service.name == "<name>"`）或 Kibana 仓库 APM 路由获取服务级数据。如果用户未提供时间范围，则假设为最后一小时。

### 第 2 步：检查 SLO 和触发警报

**SLO**：调用 **SLO API** 获取服务的 SLO 定义和状态（延迟、可用性）、健康/退化/违反、消耗速率、错误预算。**警报**：对于活动的 APM 警报，调用 `/api/alerting/rules/_find?search=apm&search_fields=tags&per_page=100&filter=alert.attributes.executionStatus.status:active`。在检查一个服务时，包括 `params.serviceName` 匹配服务和 `params.serviceName` 缺失（所有服务规则）的规则。不要查询 `.alerts*` 索引以进行活动状态检查。与 SLO 违规或指标变化关联。

### 第 3 步：检查机器学习异常

如果使用机器学习异常检测，请查询服务和时间范围内的机器学习作业结果或异常记录（通过 Elasticsearch ML API 或索引）。注意高严重度异常（延迟、吞吐量、错误率）；使用异常时间窗口来缩小第 4-5 步。

### 第 4 步：检查吞吐量、延迟和错误率

使用 ES|QL 对 `traces*apm*,traces*otel*` 或 `metrics*apm*,metrics*otel*` 进行服务和时间范围查询，以获取吞吐量（例如 req/分钟）、延迟（平均、p95、p99）、错误率（失败/总数或 5xx/总数）。示例：

```esql
FROM traces*apm*,traces*otel*
| WHERE service.name == "api-gateway"
  AND @timestamp >= ... AND @timestamp <= ...
| STATS request_count = COUNT(*), failures = COUNT(*) WHERE event.outcome == "failure" BY BUCKET(@timestamp, 1 hour)
| EVAL error_rate = failures / request_count
| SORT @timestamp
| LIMIT 500
```

延迟百分位数和确切字段名：见 Kibana `trace_charts_definition.ts`。

### 第 5 步：评估依赖项健康

通过 ES|QL 在 `traces*apm*,traces*otel*`/`metrics*apm*,metrics*otel*`（下游服务/跨度聚合）或 **Kibana 仓库** 中的 APM 路由处理程序获取依赖项和服务映射数据，这些处理程序公开依赖项/服务映射数据。对于服务和时间范围，注意下游延迟和错误率；将慢速或失败的依赖项标记为可能的原因。

### 第 6 步：与基础设施和日志关联

- **APM 关联（当仅受部分影响时）**：运行 `node skills/observability/service-health/scripts/apm-correlations.js latency-correlations|failed-correlations --service-name <name> [--start ...] [--end ...]` 以获取相关属性。按这些属性过滤并获取 trace 样本或错误以确认根本原因。见 [APM 关联脚本](#apm-correlations-script)。
- **基础设施**：使用 traces 中的 **资源属性**（例如 `k8s.pod.name`、`container.id`、`host.name`）并使用 ES|QL 或 Elasticsearch 查询基础设施/指标索引以获取 **CPU** 和 **内存**。**OOM** 和 **CPU 限制** 直接影响 APM 健康；将它们的时间窗口与 APM 退化关联。
- **日志**：使用 ES|QL 或 Elasticsearch 在按 `service.name == "<service_name>"` 或 `trace.id == "<trace_id>"` 过滤的日志索引上进行搜索，以解释行为和根本原因（异常、超时、重启）。

### 第 7 步：总结并建议

声明健康（健康/退化/不健康）并说明原因；列出具体的下一步操作。

## 示例

### 示例：针对特定服务的 ES|QL

使用 `WHERE service.name == "<service_name>"` 和时间范围进行限定。吞吐量和错误率（1 小时桶；`LIMIT` 限制行数和 token）：

```esql
FROM traces*apm*,traces*otel*
| WHERE service.name == "api-gateway"
  AND @timestamp >= "2025-03-01T00:00:00Z" AND @timestamp <= "2025-03-01T23:59:59Z"
| STATS request_count = COUNT(*), failures = COUNT(*) WHERE event.outcome == "failure" BY BUCKET(@timestamp, 1 hour)
| EVAL error_rate = failures / request_count
| SORT @timestamp
| LIMIT 500
```

延迟百分位数和确切字段名：见 Kibana `trace_charts_definition.ts`。

### 示例：“服务 X 是否健康？”

1. 解析服务 X 和时间范围。调用 **SLO API** 和 **警报 API**；运行 ES|QL 对 `traces*apm*,traces*otel*`/`metrics*apm*,metrics*otel*` 查询吞吐量、延迟、错误率；查询依赖项/服务映射数据（ES|QL 或 Kibana 仓库）。
2. 评估 SLO 状态（违反/退化？）、触发规则、机器学习异常和依赖项健康。
3. 回答：健康 / 退化 / 不健康，并说明原因和下一步操作（例如 [可观测性实验室](https://www.elastic.co/observability-labs)）。

### 示例：“服务 Y 为什么慢？”

1. 服务 Y 和慢速时间范围。调用 **SLO API** 和 **警报 API**；运行 ES|QL 查询 Y 和依赖项；查询机器学习异常结果。
2. 通过 ES|QL 比较平均延迟（p95/p99）与先前时间段；从依赖项数据识别高延迟或失败的依赖项。
3. 总结（例如 p99 升高；依赖项 Z 升高）并建议（调查 Z；可观测性实验室用于延迟）。

### 示例：将服务关联到基础设施（OpenTelemetry）

使用 spans/traces 上的 **资源属性** 获取服务的运行时（pods、containers、hosts）。然后检查相同时间窗口内 APM 问题的这些资源的 CPU 和内存：

- 从服务的 traces 或 metrics 中读取资源属性，例如 `k8s.pod.name`、`k8s.namespace.name`、`container.id` 或 `host.name`。
- 运行 ES|QL 或 Elasticsearch 搜索基础设施/指标索引，按这些资源值和事件时间范围过滤。检查 **CPU 使用率** 和 **内存消耗**（例如 `system.cpu.total.norm.pct`）；查找与 APM 延迟或错误尖峰对齐的 **OOMKilled** 事件、**CPU 限制** 或持续的高 CPU/内存。

### 示例：按服务或 trace ID 过滤日志

为了理解特定服务或单个 trace 的行为，按以下方式过滤日志：

- **按服务**：运行 ES|QL 或 Elasticsearch 搜索按 `service.name == "<service_name>"` 和时间范围过滤的日志索引，以获取服务上下文中的应用日志（错误、警告、重启）。
- **按 trace ID**：在调查特定请求时，从 APM trace 中获取 `trace.id` 并按 `trace.id == "<trace_id>"`（或日志模式中的等效字段）过滤。具有该 trace ID 的日志显示完整请求路径并有助于解释失败或延迟。

## 指南

- 使用 **可观测性 API** ([SLOs API](https://www.elastic.co/docs/api/doc/kibana/group/endpoint-slo)、[警报 API](https://www.elastic.co/docs/api/doc/kibana/group/endpoint-alerting)) 和 **ES|QL** 在 `traces*apm*,traces*otel*`/`metrics*apm*,metrics*otel*`（8.11+ 或 Serverless）上，按 `service.name`（当相关时按 `service.environment`）过滤。对于活动 APM 警报，调用 `/api/alerting/rules/_find?search=apm&search_fields=tags&per_page=100&filter=alert.attributes.executionStatus.status:active`。在检查一个服务时，评估两种规则类型：`params.serviceName` 匹配目标服务的规则，以及 `params.serviceName` 缺失（所有服务规则）的规则。在声明健康之前，将任何一种视为适用于服务。在确定当前活动警报时，不要查询 `.alerts*` 索引；使用上述警报 API 响应作为真实来源。对于 APM 关联，运行 **apm-correlations** 脚本（见 [APM 关联脚本](#apm-correlations-script)）；对于依赖项/服务映射数据，使用 ES|QL 或 Kibana 仓库路由处理程序。对于 Elasticsearch 索引和搜索行为，见 Elasticsearch 仓库中的 **Elasticsearch** API。
- 始终使用 **用户的时
