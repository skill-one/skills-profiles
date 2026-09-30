---
name: observability-k8s-investigation
description: 使用 OTel 远程遥测（EDOT）调查 Kubernetes 工作负载、节点和控制平面问题。在诊断 Pod 失败（CrashLoopBackOff、OOMKilled、Error）、节点压力、资源耗尽、镜像拉取失败、准入拒绝、自动缩放异常，或关联 K8s 状态与应用程序信号时使用。仅限 OTel 接收路径——传统的 ECS Kubernetes 集成形状不在范围内。
---

# Kubernetes 调查

使用通过 EDOT（Elastic Distribution of OpenTelemetry）和 kube-stack 收集器收集的 OTel 远程监控数据诊断 Kubernetes 问题。关联集群状态、Pod 运行时指标、K8s 事件、应用程序日志和 APM，以跨工作负载、节点和控制平面层识别根本原因。

<!-- begin-partial: preamble -->

## 环境配置

此技能通过 `elastic` CLI 执行 Elasticsearch 操作。如果未安装 [`elastic` CLI](https://github.com/elastic/cli#configuration)，请告知用户其用途。不要猜测凭证、直接调用 HTTP API 或尝试其他解决方案。

此技能以 HTTP 简写形式引用操作（例如，`GET /`、`GET /_cat/indices`、`GET /{index}/_mapping`、`GET /{index}/_settings/index.mode`、`POST /_query`）。文档末尾的 [操作](#operations) 表将每个简写映射到等效的 `elastic` CLI 命令——始终使用 CLI 而不是直接调用 HTTP API。

<!-- end-partial: preamble -->

### 无集群访问的分析

上述 CLI 检查会阻止查询集群——但它不会阻止分析。当用户已经在问题中提供了证据（指标值、计数、状态原因、日志行、告警有效载荷、配置）时，从该证据中推理并给出结论。

当您确实需要用户未提供的数据时，仍然说明您将检查什么以及如何——命名将解决问题的特定查询、索引和字段——然后请求 CLI 设置。没有集群的检查名称是有用的；仅请求设置的回答则没有用。

此技能和 [参考资料/查询配方.md](references/query-recipes.md) 中的所有 ES|QL 查询都通过 `POST /_query` 运行。告警状态通过 `GET kbn:/api/alerting/rules/_find` 读取。字段存在性检查使用 `GET /<index>/_mapping` 或 `GET /_field_caps`。[操作](#operations) 表将每个映射到其 `elastic` CLI 等效命令。

## 范围

**在范围内：** OTel 接收器命名空间索引（`metrics-kubeletstatsreceiver.otel-*`、`metrics-k8sclusterreceiver.otel-*`、`logs-k8seventsreceiver.otel-*`、`logs-k8sobjectsreceiver.otel-*`）和 OTel 语义约定（`k8s.pod.name`、`k8s.namespace.name`、`k8s.container.restarts`）。

**超出范围：**

- 遗留的 Elastic Agent Kubernetes 集成（`metrics-kubernetes.*`、`logs-kubernetes.*`、`kubernetes.*` 字段）。已弃用——不要针对这些路径编写查询。
- APM 层分析（服务 SLO 违规、事务错误率、上游依赖健康）。不同领域——一旦 K8s 根本原因被排除或确认，转交给 **observability-sre-triage** 技能，该技能负责 SLO 状态和消耗率、活动告警规则、吞吐量、延迟、错误率、依赖健康和日志引流。当工作负载根本不是 Kubernetes 托管的时，也使用该技能。
- 集群供应、容量规划、成本优化。不同领域。

## 指南

这些适用于每次调查。如有疑问，请在编写综合分析之前重新阅读它们。

**证据的缺失不是证据。不要从空结果中编造结论。** 如果日志查询返回 0 行，日志可能未收集或 Pod 没有最近的日志行——这并不意味着“依赖不可用”或任何其他特定故障模式。报告 `no_logs_available` 并相应地权衡其余信号。

**空的依赖数据 ≠ 上游健康。** 没有使用 APM 仪器化（负载生成器、工作进程）的服务不会发出目标指标。报告 `insufficient_dependency_data`，而不是“上游正常”。

**共病症状不是原因。** 两个服务同时退化通常共享上游，而不是因果关系。只有在 (a) 一个服务的退化明显先于另一个服务，并且 (b) 差值较大（>5× 错误率，>3× 延迟）时，才归因于因果关系。

**OOMKilled 默认 ≠ 内存泄漏。** 限制可能只是工作负载工作集 undersized。通过内存曲线的形状区分它们：单调上升到限制并在每次重启时重置，负载平坦于先前一周且没有最近的部署，是泄漏特征——以高置信度确认它。当形状不明确时（尖峰、昼夜、负载相关）——而不是作为每个 OOMKilled 发现的先决条件——寻找 7 天相同小时的基线。

**错误终止默认 ≠ 应用程序错误。** 首先检查 `k8s.container.cpu_limit_utilization`。CFS 限制导致 liveness probe 超时是最常见的误诊。

**平均 CPU 隐藏限制。** Pod 在 40–60% 的平均 `cpu_limit_utilization` 下可能看起来健康，但在 p99 时受到严重限制。Linux 在 100ms 期间执行 CPU 限制；突发工作负载在期间内达到配额并停滞。查看最大值和 p95，而不仅仅是平均值。

**重启计数是布尔值，不是计数器。** `k8s.container.restarts` 直接从 K8s API 拉取，并且 kubelet 可以随时修剪它，因此绝对值不可靠。将其视为 `== 0`（没有最近的重启）与 `> 0`（最近重启）；不要从中推导出回退定时或“线性与指数”模式。通过 K8s `Killing` / `BackOff` 事件确认重启模式。

**优先报告不确定性而不是制造信心。** 如果证据是模糊的，综合分析应该说明这一点。竞争假设是有效输出。

同样，不要制造不确定性。上述规则是关于模糊证据，而不是语气。当关键信号存在且得到证实时，以高置信度确认它。将一个明确的发现降低到“中等”与过度声明一样都是缺陷。

**提交综合分析并停止。** 在 HYPOTHESIS 行中只声明一次置信度——不要再次按要点声明。除非结果改变了结论，否则不要叙述运行了哪些查询，也不要将告警重述给读者。在 RECOMMENDED NEXT STEPS 或 DOWNSTREAM IMPACT 上结束；永远不会以“想让我进一步调查吗？”之类的提议结束。后续工作应列入建议列表，并以建议的形式表达。

## 索引和字段

### 哪里可以查找

| 信号                | 索引模式                                       | 使用                                                                 |
| --------------------- | --------------------------------------------------- | ------------------------------------------------------------------- |
| Pod/容器运行时      | `metrics-kubeletstatsreceiver.otel-*`               | CPU、内存、网络、文件系统。利用率比率。                               |
| 集群状态         | `metrics-k8sclusterreceiver.otel-*`                 | 重启、阶段、最后一次终止原因、HPA、配额、节点状态                     |
| K8s 事件            | `logs-k8seventsreceiver.otel-*`                     | Killing、BackOff、FailedScheduling、Evicted、镜像拉取事件              |
| K8s 对象快照  | `logs-k8sobjectsreceiver.otel-*`                    | 部署/服务/配置文件状态随时间变化                        |
| 应用程序日志      | `logs-*.otel-*`                                     | `body.text`、`severity_text`，按 `k8s.pod.name` 过滤                |
| APM                   | `traces-*.otel-*`、`metrics-service_*.otel-default` | 通过 `service.name` + K8s 资源属性关联                   |
| ML 异常          | `.ml-anomalies-*`                                   | 内存增长、重启率、限制作业（如果配置）          |

### 关键字段

扁平 OTel 路径在 ES|QL 中有效。优先考虑扁平形式以提高可读性；嵌套 `resource.attributes.*` 形式仅用于原始日志文档。

| 字段                                            | 索引                       | 它是什么                                              |
| ------------------------------------------------ | --------------------------- | ------------------------------------------------------- |
| `k8s.pod.name`                                   | 所有 k8s                     | Pod 名称                                                |
| `k8s.namespace.name`                             | 仅指标                     | 命名空间。映射但 **null** 在 k8seventsreceiver 中     |
| `attributes.k8s.namespace.name`                  | k8seventsreceiver           | 事件上的命名空间——在那里按此形式过滤                 |
| `k8s.container.name`                             | 所有 k8s                     | Pod 中的容器                                        |
| `k8s.deployment.name`                            | k8sclusterreceiver + others | 父部署                                       |
| `k8s.pod.phase`                                  | k8sclusterreceiver          | Pending=1/Running=2/Succeeded=3/Failed=4/Unknown=5      |
| `k8s.container.restarts`                         | k8sclusterreceiver          | 容器重启总数                                       |
| `k8s.container.status.last_terminated_reason`    | k8sclusterreceiver          | `OOMKilled`、`Error`、`Completed`、`ContainerCannotRun` |
| `k8s.pod.status_reason`                          | k8sclusterreceiver          | Pod 级别原因（`Evicted`、`NodeLost`）                |
| `k8s.container.memory_limit_utilization`         | kubeletstatsreceiver        | 0.0–1.0+（可以暂时超过 1）                          |
| `k8s.container.cpu_limit_utilization`            | kubeletstatsreceiver        | 0.0–N（在 CFS 限制下经常 >1）                      |
| `k8s.pod.memory_limit_utilization`               | kubeletstatsreceiver        | 整个 Pod 汇总；在使用它之前查看下注记                 |
| `k8s.pod.cpu_limit_utilization`                  | kubeletstatsreceiver        | 整个 Pod 汇总；在使用它之前查看下注记                 |
| `k8s.pod.memory.usage` / `.working_set`          | kubeletstatsreceiver        | 字节                                                   |
| `k8s.node.condition_memory_pressure`             | k8sclusterreceiver          | 1 = 压力, 0 = 正常                                    |
| `k8s.node.condition_ready`                       | k8sclusterreceiver          | 0 = NotReady                                            |
| `k8s.hpa.current_replicas` / `.desired_replicas` | k8sclusterreceiver          | HPA 状态                                               |
| `attributes.k8s.event.reason`                    | k8seventsreceiver           | 事件原因（按此过滤）                               |
| `body.text`                                      | k8seventsreceiver / logs    | 事件消息 / 日志消息                             |
| `k8s.object.name`                                | k8seventsreceiver           | 涉及对象名称（日志属性，使用扁平形式）              |

### 容器级与 Pod 级限制利用率

在 **容器** 级别读取限制利用率。`k8s.container.cpu_limit_utilization` 和 `k8s.container.memory_limit_utilization` 是默认值；Pod 级别的配对是不同的测量，不是同义词。

接收器在同一个数据流中的**分离文档**上发出这两类：Pod 级别字段出现在不携带 `k8s.container.name` 的文档上，而容器级别字段仅出现在携带 `k8s.container.name` 的文档上。因此，`STATS ... BY k8s.container.name` 返回每个 Pod 级别字段的 `null`，反之亦然。在 9.6.0 集群上对 42,240 个没有容器名称的文档进行一小时测量：360 个文档携带 `k8s.pod.cpu_limit_utilization` 而没有容器字段；18,240 个文档携带容器名称，900 个文档携带容器字段而没有 Pod 字段。

可用性也存在差异。容器级别利用率针对每个声明限制的容器发出，而 Pod 级别汇总需要**每个** Pod 中的容器都声明它。在两个实时集群的三小时测量中，没有 Pod 携带 Pod 级别字段而没有携带容器级别字段，而 27 个 Pod 携带容器级别字段而没有携带 Pod 级别字段——它们都是多容器 Pod，其中只有一些容器声明了限制。在 sidecar 注入的 Pod 上进行的 Pod 级别限制检查会静默返回 `null`。

| 集群       | 仅容器级别 | 两个级别 | 无   | 仅 Pod 级别 |
| ------------- | -------------------- | ----------- | ------- | -------------- |
| forge-factory | 18                   | 7           | 44      | 0              |
| k8s-demo      | 9                    | 6           | 40      | 0              |

仅在问题是关于整个 Pod 时才使用 Pod 级别字段——总消耗与其容器限制的总和——并且仅在确认它们已填充后。**observability-sre-triage** 应用相同规则，因此这两个技能对同一 Pod 返回相同的答案。

### 字段可用性

上述几个字段在标准的 kube-stack 收集器中默认关闭，需要显式配置。在使用它们之前通过 `GET /<index>/_mapping` 或 `GET /_field_caps` 验证其存在性；如果缺失，按注释说明回退，并在综合分析中说明替代方案。

| 字段                                                                 | 可能缺失的原因                                                                                                       | 回退方案                                                                                                                                                                                                                                                                                                                                                               |
| ------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `k8s.container.status.last_terminated_reason`                      | k8sclusterreceiver 中的可选指标；受 `metrics_collected.metadata` 配置控制。                                      | 通过 `logs-k8seventsreceiver.otel-*` 中的 K8s `Killing` / `OOMKilling` 事件和应用日志中的退出码进行推断。                                                                                                                                                                                                                                                           |
| `k8s.pod.status_reason`                                            | 相同——k8sclusterreceiver 中的可选指标。                                                                                 | 从事件推断：`Evicted`、`NodeLost`、`Preempted`。                                                                                                                                                                                                                                                                                                                  |
| `k8s.container.cpu_limit_utilization` / `memory_limit_utilization` | 仅为声明了对应限制的容器输出，且仅在启用 kubeletstatsreceiver 指标时输出。 | `k8s.pod.cpu.node.utilization` / `k8s.pod.memory.node.utilization` 表示资源消耗占节点容量的比例，无论是否声明限制均会输出；或者将绝对的 `container.cpu.usage` / `container.memory.usage` 与基线趋势对比。两种回退方案均位于 pod 级文档中，因此请按 `k8s.pod.name` 而非 `k8s.container.name` 分组。 |
| `k8s.pod.cpu_limit_utilization` / `memory_limit_utilization`       | 要求 pod 中的每个容器都声明该限制，因此在大多数多容器 pod 中缺失。                       | 使用容器级字段，这些字段的可用率通常更高。                                                                                                                                                                                                                                                                                                |
| `k8s.node.condition_memory_pressure`                               | 受 k8sclusterreceiver 的 `node_conditions_to_report` 控制（默认不包含此项）。                                             | 将 `k8s.node.memory.usage` 与 `k8s.node.allocatable_memory` 进行比较，或查找节点上的 `Evicted` 事件。                                                                                                                                                                                                                                                        |

如果使用了回退方案，请在综合结论中注明（例如，`(via memory.usage; limit_utilization not collected)`），以便读者了解该信号是间接的。

## ES|QL 注意事项

在编写查询之前，请了解以下内容。其中每一项都会静默地产生错误答案，而不是明显报错。

**`VALUES()` 在只有一个去重值时返回标量，多个时返回数组。** 如果模板假设数组形状（例如，`| first`），在标量情况下会提取字符串的第一个字符。请使用 `MV_FIRST(VALUES(...))` 或处理两种情况。

**`VALUES()` 比此技能的基础最低版本更新。** 它在 Serverless 上已正式可用（GA），但在 Stack 中从 8.14.0 开始为预览版，仅在 9.4.0 中正式可用，而在 8.14.0 以下版本中则完全不存在。使用前请检查 `GET /`：如果 `build_flavor: "serverless"` 则可用，否则读取 `version.number`。在不可用的情况下，不要聚合该字段，而是将其移到 `BY` 子句中——每个去重值对应一行，承载相同的信息：

```esql
| STATS restarts = MAX(k8s.container.restarts), phase = MAX(k8s.pod.phase)
    BY term_reason = k8s.container.status.last_terminated_reason
| SORT restarts DESC
| LIMIT 10
```

**`PERCENTILE` 在 OTel `histogram` 类型上不起作用**（截至 8.15）。对于 APM 持续时间百分位数，请使用 `aggregate_metric_double` 汇总字段（`AVG(transaction.duration.summary)` 将 sum 除以 value_count）的 `AVG`。若要获取真正的百分位数，请回退到 Kibana Query DSL。

**`COUNT(agg_metric_double)` 返回 `value_count`（事件数），而非文档数。** `SUM(field)` 给出总和分量；`AVG(field)` 给出 sum/value_count。不要将 `SUM(transaction.duration.summary)` 用作事件计数的代理指标——它返回的是总持续时间。

**K8s 指标在 ES|QL 中使用扁平的 OTel 字段路径。** 使用 `k8s.pod.name`，而非 `resource.attributes.k8s.pod.name`。嵌套形式用于原始日志文档。

## 故障模式分类

分类词汇表——涵盖工作负载、节点、控制平面、自动扩缩容和网络各层中每种模式的关键信号和佐证检查，以及当两种模式都符合时应采取的措施——位于
[references/failure-modes.md](references/failure-modes.md) 中。请在分类前先阅读它。

## 信号解释

### 内存

- **在 30–60 分钟内单调上升** → 泄漏。检查该语言的 GC 指标：JVM `jvm.gc.duration`，Go
  `process.runtime.go.gc.pause_ns`，Node `v8js_gc_duration`。GC 频率/暂停时间上升但存活集合稳定，是典型的泄漏特征。
- **昼夜规律 / 与负载相关的尖峰** → 由负载驱动，而非泄漏。考虑调整 HPA 或增加限制。
- **达到 1.0 后重启** → 确认为 OOMKilled。应用日志中退出码 137 (SIGKILL) 一致。

### CPU

- `cpu_limit_utilization > 1.0` 持续存在 → CFS 节流。节点有空闲 CPU；该 pod 受到配额限制。
- 节流的症状（而非节流指标本身）：存活探针超时、p99 延迟是 p50 的 4–16 倍、上游队列反压、Error-reason 容器终止。
- 平均值可能看起来正常，而 p95 受到节流。不要仅依赖平均值。

### 重启模式

- 最近 `restarts > 0` → 工作负载一直在重启。不要从计数解读严重程度（参见 _Restart count is
  boolean_）；请从 `logs-k8seventsreceiver.otel-*` 中的 K8s `Killing` / `BackOff` 事件时间戳确认模式。
- 重启与内存压力相关（`memory_limit_utilization → 1.0`） → OOMKilled 路径。
- 无内存/CPU 压力的重启 → 探针配置错误、应用 bug 或启动依赖失败。获取
  `Unhealthy` 和 `Killing` 事件。

### 终止原因

- `OOMKilled` → 内存路径。
- `Error` → 非零退出。检查应用日志；如果为空/最少，请在归因于应用逻辑之前先检查 CPU 节流。
- `Completed` → 运行至完成。对于 Jobs/CronJobs/init 容器属正常；其他情况下异常。
- `ContainerCannotRun` → 运行时/镜像/执行问题。检查镜像拉取事件。

## 调查流程

> 调查不是检查清单。以下各部分描述了一个_典型_弧线——**根据发现结果压缩、跳过或重新审视这些部分。** 一旦拥有足够证据以在已知置信度下进行综合，请立即终止。在收益递减点之后继续追逐信号是一种故障模式，而非彻底性。

### 定位

确定目标：`k8s.pod.name`、`k8s.namespace.name`，可选 `k8s.deployment.name` 和 `service.name`。如果未给出时间窗口，pod 级调查默认使用最近 1 小时，事件关联使用最近 2 小时，进行中/未解决的事故使用最近 6
小时。

如果警报负载已经告诉你故障模式（例如，专门针对 `OOMKilled` 触发），请注明这一点并跳过分类；移至确认和基线比较。

### 表征

获取工作负载近期行为的形状：重启计数、终止原因、阶段、利用率。通常一到两个查询就足够了。

```esql
FROM metrics-k8sclusterreceiver.otel-*
| WHERE k8s.pod.name == "<pod>" AND k8s.namespace.name == "<ns>"
  AND @timestamp > NOW() - 1 hour
| STATS restarts = MAX(k8s.container.restarts),
        term_reasons = VALUES(k8s.container.status.last_terminated_reason),
        phase = MAX(k8s.pod.phase)
```

`VALUES()` 需要 Serverless 或 Stack 8.14+（9.4 正式可用）。在较旧的 Stack 集群上使用
[ES|QL 注意事项](#esql-gotchas) 中的 `BY`-子句重写，而不是从查询中移除终止原因。

```esql
FROM metrics-kubeletstatsreceiver.otel-*
| WHERE k8s.pod.name == "<pod>" AND @timestamp > NOW() - 15 minutes
| STATS mem_pct = ROUND(MAX(k8s.container.memory_limit_utilization) * 100, 1),
        cpu_pct = ROUND(MAX(k8s.container.cpu_limit_utilization) * 100, 1)
    BY k8s.container.name
```

按容器分组：注入 sidecar 的 pod 有多个容器，只有声明限制的容器才会报告利用率。如果每列都返回 `null`，则未声明限制——请按照
[字段可用性](#field-availability) 中所述的回退方案操作，而不是将 `null` 解释为空闲。

### 分类

使用 [references/failure-modes.md](references/failure-modes.md) 中的分类法。关键信号应匹配；“Investigate”列告诉你寻求哪些佐证。

当两种模式都符合时，注明两者，并继续处理关键信号更强的那种。你可以在佐证过程中修正。

### 佐证

获取你的分类预测你会发现的证据。典型来源：

**K8s 事件** 针对命名空间和时间窗口：

```esql
FROM logs-k8seventsreceiver.otel-*
| WHERE attributes.k8s.namespace.name == "<ns>"
  AND @timestamp > NOW() - 2 hours
  AND attributes.k8s.event.reason IN (
    "BackOff", "Killing", "Unhealthy", "Failed",
    "FailedScheduling", "Evicted", "SuccessfulRescale",
    "Pulling", "Pulled", "Started", "Created"
  )
| SORT @timestamp DESC
| KEEP @timestamp, attributes.k8s.event.reason, body.text, k8s.object.name
| LIMIT 30
```

**命名空间在此接收器上是日志属性，而非资源属性。** 过滤 `attributes.k8s.namespace.name`，而非扁平的 `k8s.namespace.name`。扁平形式在此数据流上已映射，因此使用它的查询会解析并执行并返回**零行且无错误**——在一个 Stack
9.4.4 集群上，扁平字段在 832 个事件中的 0 个中填充，而 `attributes.` 形式在所有事件中都携带命名空间，因此扁平过滤器丢弃了 300 个匹配的 `BackOff`、`Killing`
和 `Unhealthy` 事件。扁平的 `k8s.*` 路径在 `metrics-kubeletstatsreceiver.otel-*` 和
`metrics-k8sclusterreceiver.otel-*` 上有效，其中命名空间是资源属性；事件接收器是例外。在信任空的事件结果之前，请用 `COUNT(attributes.k8s.namespace.name)` 对比 `COUNT(*)` 进行确认。

**应用日志** 如果可用——查看终止时间戳之前的最近 200 行。如果不存在，标记
`no_logs_available`；不要虚构日志模式。

**APM** 如果 pod 运行插桩服务——从 pod 资源属性中解析 `service.name` 以供后续关联。SLO / 延迟 / 错误率分析本身属于 APM 层工作，超出此技能范围。

**基线比较** —— 对于基于利用率的发现，将当前值与 7 天前同一小时的值进行比较。“内存高”仅相对于该工作负载的正常值有意义。

### 检查上游原因（条件）

仅在症状模式建议时追究。阈值：上游错误率 >5 倍基线 _或_ 延迟 >3 倍基线，
且退化在目标服务的症状之前开始。共同症状不能确立因果关系。

如果 `metrics-service_destination.1m.otel-default` 对该服务没有行，报告 `insufficient_dependency_data` ——
而不是“上游健康”。

### 检查近期变更（条件）

最近 2 小时内的 `SuccessfulCreate` / `Pulled` 事件通常与部署相关。`logs-k8sobjectsreceiver.otel-*`
显示 configmap/secret/deployment 规范变更。症状发生后 15 分钟内的变更是强相关性，但仍只是相关性——验证它是否合理地解释了你分类的模式。

### 综合并停止

一旦拥有足够证据以在已知置信度下支持假设，请立即综合。你无需完成前面所有章节——调查在以下任一情况终止：

- 你有一个带有佐证的高置信度假设，或
- 你有一个低/中置信度假设，且进一步查询不太可能改变局面（例如，日志不可用，APM 未插桩，未找到近期变更）。

## 综合

默认结构：

```text
HYPOTHESIS (confidence: high | medium | low)
<一段话：服务，症状，最可能的原因。指出分类法中的故障模式。>

EVIDENCE
- <来自表征的发现，带有具体的指标或值。>
- <来自事件 / 日志 / APM 的发现。>
- <来自基线比较、依赖检查或变更关联的发现（如果已追究）。>

CONFIDENCE NOTE
<仅在非 'high' 时。具体缺失或模糊的证据是什么。>

RECOMMENDED NEXT STEPS
1. <最具操作性——通常是配置检查或要观察的指标。>
2. <次要。>

DOWNSTREAM IMPACT
<依赖于此工作负载的服务，或 '未识别下游依赖。'>
```

**规模。** 整个综合为 250–400 字。HYPOTHESIS 为两到三句。EVIDENCE 为三到五行单行项目符号，每项引用具体值而非重新解释。RECOMMENDED NEXT STEPS 为两到三项单行项目——你实际会首先执行的，而非所有可能执行的项目。DOWNSTREAM IMPACT 为一到两句。证据充分的警报可轻松容纳于此；长度并非彻底性，且在事故中途扫描的值班读者不会看完第一屏。

**当两个假设并存时：** 用 COMPETING HYPOTHESES 替换 HYPOTHESIS；列出两者，说明你倾向哪一个及原因，并列出能区分它们的证据。

**当未发现事故时**（症状已解决，或警报似乎是虚假的）：直接说明。
`ALERT FIRED BUT SYSTEM APPEARS HEALTHY` 是有效的输出。列出你检查了什么以及未发现什么。

### 置信度校准

从 **high** 开始，并根据缺失的内容降级：

- 如果主要信号清晰但缺乏佐证（无日志，无 APM，无法进行基线比较）则降级为 **medium**。或者：两种模式符合且无法区分。
- 如果仅有一个信号支持假设，信号冲突，或该模式需要无法获取的证据，则降级为 **low**。

当应用日志数据缺失且假设依赖于应用行为时，永不返回 **high**。证据缺失不能佐证假设。

## 查询配方

最频繁重启的 pod、CPU 节流、节点内存压力、准入拒绝和触发警报路径的现成查询位于 [references/query-recipes.md](references/query-recipes.md) 中。

## 示例

### “为什么我的 pod 处于 CrashLoopBackOff 状态？”

先进行表征：获取重启计数、终止原因、内存和 CPU 利用率。

- 如果 `last_terminated_reason == "OOMKilled"` 且内存利用率达到 1.0 → 内存路径。与 7 天基线数据对比：单调上升表示泄漏；尖峰表示负载驱动。如果已知语言，检查 GC 指标。
- 如果 `last_terminated_reason == "Error"` 且 `cpu_limit_utilization > 1.0` → CPU 限制路径。与存活探针配置（initialDelaySeconds, timeoutSeconds）和 K8s 的 `Unhealthy` 事件对比。
- 如果 `last_terminated_reason == "Error"` 且 CPU 正常 → 应用逻辑路径。在终止前拉取最近的日志。
- 如果 `last_terminated_reason == "ContainerCannotRun"` → 镜像/执行路径。检查 K8s 的 `Failed` 拉取事件。

综合判断，给出适当的置信度。如果错误路径下日志不可用，降级为中等置信度并说明。

### "我的发布卡住了吗？"

权威信号：`k8s.deployment.available < k8s.deployment.desired` 持续超过 10 分钟。

诊断约束：

- 新的 ReplicaSet 上的 K8s 事件：`FailedCreate` → 承认拒绝（配额、webhook、PSP）。`FailedScheduling` → 没有节点匹配。
- 新 Pod 的利用率：所有内存均为 0% → 未启动（镜像拉取失败）；高 CPU 且低内存 → 启动缓慢触发就绪探针。
- HPA 状态：负载下稳定 `current_replicas < desired_replicas` → 未就绪 Pod 抑制。

### "警报已触发但一切看起来正常"

可能且值得明确命名。检查：

- 症状是否已解决？将当前利用率/重启率与警报触发点对比。
- 警报是否是已衰减的瞬时峰值？
- 警报是否适当调整（例如，评估窗口过短）？

输出：`ALERT FIRED BUT SYSTEM APPEARS HEALTHY` 并说明你检查的内容。如果模式反复出现，建议调整警报设置。

## 相关

- **工作流：** `K8s CrashLoopBackOff 调查` — 警报触发的自动版本的 Pod 级路径。运行确定性 ESQL + 分支；这项技能提供了工作流缺乏的解释层。
- **Forge 基因库：** 16 个 K8s 失败场景（OOMKill 级联、CPU 限制、探针配置错误、节点 NotReady、承认 webhook 阻塞等）验证这项技能的覆盖范围。

## 运维

| HTTP API (简称)                | `elastic` CLI 命令                                             |
| ----------------------------------- | ----------------------------------------------------------------- |
| `GET /`                             | `elastic es info`                                                 |
| `POST /_query`                      | `elastic es esql query --format tsv --query '<esql>'`             |
| `GET /<index>/_mapping`             | `elastic es indices get-mapping --index '<index>'`                |
| `GET /_field_caps`                  | `elastic es field-caps --index '<index>' --fields '<fields>'`     |
| `GET kbn:/api/alerting/rules/_find` | `elastic kb alerting get-alerting-rules-find --filter '<filter>'` |
