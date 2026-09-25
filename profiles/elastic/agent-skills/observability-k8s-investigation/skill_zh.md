# Kubernetes 调查

使用通过 EDOT（Elastic Distribution of OpenTelemetry）和 kube-stack 收集的 OTel 远程监控数据诊断 Kubernetes 问题。关联集群状态、Pod 运行指标、K8s 事件、应用程序日志和 APM，以跨工作负载、节点和控制平面层识别根本原因。

<!-- begin-partial: preamble -->

## 环境配置

此技能通过 `elastic` CLI 执行 Elasticsearch 操作。如果未安装 [`elastic` CLI](https://github.com/elastic/cli#configuration)，请告知用户其用途。不要猜测凭证、直接调用 HTTP API 或尝试其他解决方案。

此技能以 HTTP 简写形式引用操作（例如，`GET /`、`GET /_cat/indices`、`GET /{index}/_mapping`、`GET /{index}/_settings/index.mode`、`POST /_query`）。文档末尾的 [操作](#operations) 表将每个简写映射到等效的 `elastic` CLI 命令——始终使用 CLI 而不是直接调用 HTTP API。

<!-- end-partial: preamble -->

### 无集群访问的分析

上述 CLI 检查会阻止查询集群——它不会阻止分析。当用户已经在问题中提供了证据（指标值、计数、状态原因、日志行、警报有效载荷、配置）时，从该证据中推理并给出结论。

当您确实需要用户未提供的数据时，仍然要说明您将检查什么以及如何——命名具体的查询、索引和字段，这些将解决该问题——然后请求 CLI 设置。没有集群的检查结果是有用的；仅请求设置的检查则没有用。

此技能和 [参考资料/query-recipes.md](references/query-recipes.md) 中的所有 ES|QL 查询都通过 `POST /_query` 运行。使用 `GET kbn:/api/alerting/rules/_find` 读取警报状态。字段存在性检查使用 `GET /<index>/_mapping` 或 `GET /_field_caps`。[操作](#operations) 表将每个映射到其 `elastic` CLI 等效命令。

## 范围

**在范围内：** OTel 接收器命名空间的索引（`metrics-kubeletstatsreceiver.otel-*`、`metrics-k8sclusterreceiver.otel-*`、`logs-k8seventsreceiver.otel-*`、`logs-k8sobjectsreceiver.otel-*`）和 OTel 语义约定（`k8s.pod.name`、`k8s.namespace.name`、`k8s.container.restarts`）。

**超出范围：**

- 遗留的 Elastic Agent Kubernetes 集成（`metrics-kubernetes.*`、`logs-kubernetes.*`、`kubernetes.*` 字段）。已弃用——不要针对这些路径编写查询。
- APM 层分析（服务 SLO 违规、事务错误率、上游依赖健康）。不同领域——一旦 K8s 根本原因被排除或确认，转交给 **observability-sre-triage** 技能，该技能拥有 SLO 状态和燃烧速率、活动警报规则、吞吐量、延迟、错误率和依赖健康以及日志分流。当工作负载根本不是由 Kubernetes 托管的时，也使用该技能。
- 集群创建、容量规划、成本优化。不同领域。

## 指南

这些适用于每次调查。如有疑问，请在编写综合分析之前重新阅读它们。

**缺乏证据不是证据。不要从空结果中编造。** 如果日志查询返回 0 行，日志可能没有被收集或 Pod 没有最近的行——这并不意味着“依赖不可用”或任何其他特定故障模式。报告 `no_logs_available` 并相应地权衡其余信号。

**空依赖数据 ≠ 上游健康。** 没有使用 APM 仪器（负载生成器、工作器）的服务不会发出目标指标。报告 `insufficient_dependency_data`，而不是“上游正常”。

**共病症状不是原因。** 两个服务同时退化通常共享上游，而不是因果关系。只有在 (a) 一个服务的退化明显先于另一个服务，并且 (b) 差值很大（>5× 错误率，>3× 延迟）时，才将因果关系归因于它。

**OOMKilled ≠ 默认内存泄漏。** 限制可能只是工作集的 undersized。通过内存曲线的形状区分它们：单调上升到限制并在每次重启时重置，负载平坦相对于先前的周数且没有最近的部署，是泄漏的特征——以高置信度承诺它。当形状不明确时，使用 7 天同一小时的基线——尖峰、昼夜或负载相关——而不是作为每个 OOMKilled 发现的前置条件。

**错误终止 ≠ 默认应用程序错误。** 首先检查 `k8s.container.cpu_limit_utilization`。CFS 限制导致 liveness probe 超时是最常见的误诊。

**平均 CPU 隐藏限制。** Pod 在 40–60% 的平均 `cpu_limit_utilization` 下可能看起来很健康，同时在 p99 时受到严重限制。Linux 在 100ms 期间执行 CPU 限制；突发工作负载在期间达到配额并停滞。查看最大值和 p95，而不仅仅是平均值。

**重启计数是布尔值，不是计数器。** `k8s.container.restarts` 直接从 K8s API 拉取，并且可以被 kubelet 在任何时候修剪，因此绝对值是不可靠的。将其视为 `== 0`（没有最近的重启）与 `> 0`（最近正在重启）；不要从中推导出回退时间或“线性与指数”模式。通过 K8s `Killing` / `BackOff` 事件确认重启模式。

**优先报告不确定性而不是制造信心。** 如果证据是模糊的，综合分析应该说明这一点。竞争假设是有效的输出。

**同样，不要制造不确定性。** 上述规则是关于模糊的证据，而不是关于语气。当关键信号存在且得到证实时，以高置信度承诺它。将一个明确的结果降低到“中等”与过度声明一样都是缺陷。

**提供综合分析并停止。** 在 HYPOTHESIS 行中只声明一次置信度——不要再次针对每个要点。不要叙述运行了哪些查询，除非结果改变了结论，并且不要将警报重述给读者。在 RECOMMENDED NEXT STEPS 或 DOWNSTREAM IMPACT 上结束；永远不要以“想让我进一步调查吗？”之类的提议结束。后续工作属于建议列表，应以建议的形式提出。

## 索引和字段

### 哪里可以查找

| 信号                | 索引模式                                       | 使用                                                                 |
| --------------------- | --------------------------------------------------- | ------------------------------------------------------------------- |
| Pod/容器运行时      | `metrics-kubeletstatsreceiver.otel-*`               | CPU、内存、网络、文件系统。利用率比率。                               |
| 集群状态         | `metrics-k8sclusterreceiver.otel-*`                 | 重启、阶段、最后终止原因、HPA、配额、节点状态                     |
| K8s 事件            | `logs-k8seventsreceiver.otel-*`                     | Killing、BackOff、FailedScheduling、Evicted、镜像拉取事件      |
| K8s 对象快照  | `logs-k8sobjectsreceiver.otel-*`                    | 部署/服务/配置状态随时间变化                        |
| 应用程序日志      | `logs-*.otel-*`                                     | `body.text`、`severity_text`，按 `k8s.pod.name` 过滤            |
| APM                   | `traces-*.otel-*`，`metrics-service_*.otel-default` | 通过 `service.name` + K8s 资源属性进行关联                   |
| ML 异常          | `.ml-anomalies-*`                                   | 内存增长、重启率、限制作业（如果配置）          |

### 关键字段

扁平 OTel 路径在 ES|QL 中有效。优先使用扁平形式以提高可读性；嵌套的 `resource.attributes.*` 形式仅用于原始日志文档。

| 字段                                            | 索引                       | 它是什么                                              |
| ------------------------------------------------ | --------------------------- | ------------------------------------------------------- |
| `k8s.pod.name`                                   | 所有 k8s                     | Pod 名称                                                |
| `k8s.namespace.name`                             | 仅限指标                  | 命名空间。映射，但 **null** 在 k8seventsreceiver 上     |
| `attributes.k8s.namespace.name`                  | k8seventsreceiver           | 事件上的命名空间——在此处过滤此形式                 |
| `k8s.container.name`                             | 所有 k8s                     | Pod 中的容器                                    |
| `k8s.deployment.name`                            | k8sclusterreceiver + others | 父部署                                       |
| `k8s.pod.phase`                                  | k8sclusterreceiver          | Pending=1/Running=2/Succeeded=3/Failed=4/Unknown=5      |
| `k8s.container.restarts`                         | k8sclusterreceiver          | 容器重启总数                           |
| `k8s.container.status.last_terminated_reason`    | k8sclusterreceiver          | `OOMKilled`、`Error`、`Completed`、`ContainerCannotRun` |
| `k8s.pod.status_reason`                          | k8sclusterreceiver          | Pod 级原因（`Evicted`、`NodeLost`）                |
| `k8s.container.memory_limit_utilization`         | kubeletstatsreceiver        | 0.0–1.0+（可能暂时超过 1）          |
| `k8s.container.cpu_limit_utilization`            | kubeletstatsreceiver        | 0.0–N（在 CFS 限制下经常 >1）              |
| `k8s.pod.memory_limit_utilization`               | kubeletstatsreceiver        | 整个 Pod 的聚合；在使用它之前注意以下说明          |
| `k8s.pod.cpu_limit_utilization`                  | kubeletstatsreceiver        | 整个 Pod 的聚合；在使用它之前注意以下说明          |
| `k8s.pod.memory.usage` / `.working_set`          | kubeletstatsreceiver        | 字节                                                   |
| `k8s.node.condition_memory_pressure`             | k8sclusterreceiver          | 1 = 压力，0 = 正常                                    |
| `k8s.node.condition_ready`                       | k8sclusterreceiver          | 0 = NotReady                                            |
| `k8s.hpa.current_replicas` / `.desired_replicas` | k8sclusterreceiver          | HPA 状态                                               |
| `attributes.k8s.event.reason`                    | k8seventsreceiver           | 事件原因（在此处过滤）                           |
| `body.text`                                      | k8seventsreceiver / logs    | 事件消息 / 日志消息                             |
| `k8s.object.name`                                | k8seventsreceiver           | 涉及对象名称（日志属性，使用扁平形式）      |

### 容器级与 Pod 级限制利用率

在 **容器** 级别读取限制利用率。`k8s.container.cpu_limit_utilization` 和 `k8s.container.memory_limit_utilization` 是默认值；Pod 级别的配对是不同的测量值，不是同义词。

接收器在同一数据流中发出两个系列的文档：没有 `k8s.container.name` 的文档上出现 Pod 级字段，而仅包含 `k8s.container.name` 的文档上才出现容器级字段。因此，`STATS ... BY k8s.container.name` 返回每个 Pod 级字段的 `null`，反之亦然。在 9.6.0 集群上对一小时进行测量：在 42,240 个没有容器名称的文档中，360 个包含 `k8s.pod.cpu_limit_utilization`，没有包含容器字段；在 18,240 个包含容器名称的文档中，900 个包含容器字段，没有包含 Pod 字段。

可用性也存在差异。容器级利用率针对每个声明限制的容器发出，而 Pod 级聚合需要 **每个** Pod 中的容器都声明它。在两个活跃集群上经过三个小时的测量：没有 Pod 包含 Pod 级字段而没有包含容器级字段，而 27 个 Pod 包含容器级字段而没有包含 Pod 级字段——它们中的每一个都是多容器 Pod，其中只有一些容器声明了限制。在多容器 Pod 上对 Pod 级重启进行检查时，会静默返回 `null`。

| 集群       | 仅容器级别 | 两者级别 | 既无级别 | 仅 Pod 级别 |
| ------------- | -------------------- | ----------- | ------- | -------------- |
| forge-factory | 18                   | 7           | 44      | 0              |
| k8s-demo      | 9                    | 6           | 40      | 0              |

仅在问题是关于整个 Pod 时才使用 Pod 级字段——总消耗与其容器限制的总和相比——并且在使用它之前确认它们已填充。**observability-sre-triage** 应用相同的规则，因此这两个技能对同一 Pod 返回相同的答案。

### 字段可用性

上述几个字段在标准的 kube-stack 收集器中默认关闭，需要明确配置。在使用它们之前，使用 `GET /<index>/_mapping` 或 `GET /_field_caps` 验证存在性；如果缺失，按说明回退，并在综合分析中说明替代方案。

| 字段                                                              | 为什么可能缺失                                                                                                       | 回退                                                                                                                                                                                                                                                                                                                                                               |
| ------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `k8s.container.status.last_terminated_reason`                      | k8sclusterreceiver 中的可选指标；受 `metrics_collected.metadata` 配置的约束。                                      | 从 K8s `Killing` / `OOMKilling` 事件中推断 `logs-k8seventsreceiver.otel-*` 和应用程序日志中的退出代码。                                                                                                                                                                                                                                                           |
| `k8s.pod.status_reason`                                            | 相同——k8sclusterreceiver 上的可选指标。                                                                                 | 从事件中推断：`Evicted`、`NodeLost`、`Preempted`.                                                                                                                                                                                                                                                                                                                  |
| `k8s.container.cpu_limit_utilization` / `memory_limit_utilization` | 仅当容器声明相应的限制并且 kubeletstatsreceiver 指标启用时才发出。                                                       | `k8s.pod.cpu.node.utilization` / `k8s.pod.memory.node.utilization` 表达消耗作为节点容量的分数，无论是否声明限制；或者将绝对值 `container.cpu.usage` / `container.memory.usage` 与基线趋势。两者都在 Pod 级文档上，因此按 `k8s.pod.name` 而不是 `k8s.container.name` 分组。 |
| `k8s.pod.cpu_limit_utilization` / `memory_limit_utilization`       | 需要 Pod 中的每个容器都声明限制，因此大多数多容器 Pod 上都缺失。                                                               | 使用容器级字段，它们出现的频率更频繁。                                                                                                                                                                                                                                                                                                                              |
| `k8s.node.condition_memory_pressure`                               | 受 k8sclusterreceiver `node_conditions_to_report`（默认省略此条件）约束。                                             | 比较 `k8s.node.memory.usage` 与 `k8s.node.allocatable_memory`，或者查找节点上的 `Evicted` 事件。                                                                                                                                                                                                                                                        |

如果使用了回退，请在综合分析中注明（例如，`(通过 memory.usage；limit_utilization 未收集)`)，以便读者知道信号是间接的。

## ES|QL 注意事项

在编写查询之前，了解这些。它们中的每一个都默默地产生错误答案，而不是大声失败。

**`VALUES()` 返回单个不同值为标量，多个值为数组。** 假设数组形状的模板（例如，`| first`）在标量时提取字符串的第一个字符。使用 `MV_FIRST(VALUES(...))` 或处理两者。

**`VALUES()` 比此技能的基线版本新。** 它在 Serverless 上是 GA，但在 Stack 上是 8.14.0 的预览版本，并且在 9.4.0 才是 GA，而且在 8.14.0 之前根本不存在。在使用它之前，检查 `GET /`：`build_flavor: "serverless"` 表示它可用，否则读取 `version.number`。如果不可用，将字段移到 `BY` 子句中而不是聚合——每个不同值的一行携带相同的信息：

```esql
FROM metrics-k8sclusterreceiver.otel-*
| WHERE k8s.pod.name == "<pod>" AND @timestamp > NOW() - 1 hour
| STATS restarts = MAX(k8s.container.restarts),
        term_reasons = VALUES(k8s.container.status.last_terminated_reason),
        phase = MAX(k8s.pod.phase)
| SORT restarts DESC
| LIMIT 10
```

**`PERCENTILE` 在 OTel `histogram` 类型上无效**（截至 8.15）。对于 APM 持续时间百分位数，使用 `AVG` 在 `aggregate_metric_double` 摘要字段上（`AVG(transaction.duration.summary)` 将总和除以 value_count）。对于真正的百分位数，回退到 Kibana 查询 DSL。

**`COUNT(agg_metric_double)` 返回 `value_count`（事件），而不是文档计数。** `SUM(field)` 给出总和组件；`AVG(field)` 给出总和 / value_count。不要使用 `SUM(transaction.duration.summary)` 作为事件计数代理——它返回总持续时间。

**K8s 指标使用扁平 OTel 字段路径在 ES|QL 中。** `k8s.pod.name`，而不是 `resource.attributes.k8s.pod.name`。嵌套形式仅用于原始日志文档。

## 故障模式分类

分类词汇——每个模式在工作负载、节点、控制平面、自动扩展和网络层的关键信号和证实检查，以及当两个模式适用时该做什么——位于 [参考资料/failure-modes.md](references/failure-modes.md)。在分类之前阅读它。

## 信号解释

### 内存

- **在 30–60 分钟内单调上升** → 泄漏。检查语言的 GC 指标：JVM `jvm.gc.duration`、Go `process.runtime.go.gc.pause_ns`、Node `v8js_gc_duration`。稳定的活跃集上的 GC 频率/暂停上升是典型的泄漏特征。
- **昼夜 / 负载相关尖峰** → 负载驱动，不是泄漏。考虑 HPA 调整或限制增加。
- **达到 1.0，然后重启** → 确认 OOMKilled。应用程序日志中的退出代码为 137（SIGKILL）一致。

### CPU

- `cpu_limit_utilization > 1.0` 持续 → CFS 限制。节点有剩余 CPU；Pod 被配额阻塞。
- 限制的症状（不是限制指标本身）：liveness probe 超时、p99 延迟 4–16× p50、上游队列背压、错误原因容器终止。
- 平均值可能看起来健康，而 p95 受到限制。不要单独信任平均值。

### 重启模式

- `restarts > 0` 最近 → 工作负载一直在重启。不要将数量读入重启次数（见 _重启计数是布尔值_）；从 K8s `Killing` / `BackOff` 事件的时间戳在 `logs-k8seventsreceiver.otel-*` 中确认模式。
- 与内存/CPU 压力相关的重启 → OOMKilled 路径。
- 没有内存/CPU 压力的重启 → 探针配置错误、应用程序错误或启动依赖失败。拉取 `Unhealthy` 和 `Killing` 事件。

### 终止原因

- `OOMKilled` → 内存路径。
- `Error` → 非零退出。首先检查 `k8s.container.cpu_limit_utilization`。CFS 限制导致 liveness probe 超时是最常见的误诊。
- `Completed` → 成功完成。对于 Jobs/CronJobs/init 容器是正常的；否则异常。
- `ContainerCannotRun` → 运行时/镜像/执行问题。检查镜像拉取事件。

## 调查流程

> 调查不是清单。下面的部分描述了典型的弧形——**根据您找到的内容压缩、跳过或重新访问它们。在您有足够证据以已知置信度综合假设时终止。在回报递减的收益处追查信号是失败模式，而不是彻底性。

### 定位

确定目标：`k8s.pod.name`、`k8s.namespace.name`，可选 `k8s.deployment.name` 和 `service.name`。如果没有给定时间窗口，默认为 pod 级调查的最后一小时，事件关联的最后一小时，持续事件/未解决事件的最后一小时。

如果警报有效载荷已经告诉您失败模式（例如，它专门在 `OOMKilled` 上触发），请记下并跳过分类；移动到确认和基线比较。

### 特征化

获取工作负载最近行为的形状：重启计数、终止原因、内存和 CPU 利用率。通常一个或两个查询就足够了。

```esql
FROM metrics-k8sclusterreceiver.otel-*
| WHERE k8s.pod.name == "<pod>" AND k8s.namespace.name == "<ns>"
  AND @timestamp > NOW() - 1 hour
| STATS restarts = MAX(k8s.container.restarts),
        term_reasons = VALUES(k8s.container.status.last_terminated_reason),
        phase = MAX(k8s.pod.phase)
```

`VALUES()` 需要 Serverless 或 Stack 8.14+（GA 9.4）。在较旧的 Stack 集群上，使用 [ES|QL 注意事项](#esql-gotchas) 中的 `BY` 子句重写而不是从查询中删除终止原因。

```esql
FROM metrics-kubeletstatsreceiver.otel-*
| WHERE k8s.pod.name == "<pod>" AND @timestamp > NOW() - 15 minutes
| STATS mem_pct = ROUND(MAX(k8s.container.memory_limit_utilization) * 100, 1),
        cpu_pct = ROUND(MAX(k8s.container.cpu_limit_utilization) * 100, 1)
    BY k8s.container.name
```

按容器分组：注入的 sidecar Pod 有几个，并且只有那些声明限制的容器报告利用率。如果所有列都返回 `null`，则没有声明限制——按说明回退，并在综合分析中说明替代方案。

### 分类

使用 [参考资料/failure-modes.md](references/failure-modes.md) 中的分类。关键信号应匹配；“Investigate” 列告诉您要寻求的证实。

当两个模式适用时，记下两者，说明您倾向于哪一个以及原因，并列出可以消除它们的证据。在证实过程中可以修改。

### 证实

拉取您的分类预测您将找到的证据。典型来源：

**K8s 事件** 对于命名空间和窗口：

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

**命名空间是此接收器的日志属性，而不是资源属性。** 过滤 `attributes.k8s.namespace.name`，而不是扁平的 `k8s.namespace.name`。扁平形式在此数据流中映射，因此使用它的查询会解析并执行，并返回 **零行且无错误**——在 Stack 9.4.4 集群上，扁平字段在 832 个事件中的 0 个被填充，而 `attributes.` 形式在所有事件中都携带了命名空间，因此扁平过滤器丢弃了 300 个匹配的 `BackOff`、`Killing` 和 `Unhealthy` 事件。扁平 `k8s.*` 路径在 `metrics-kubeletstatsreceiver.otel-*` 和 `metrics-k8sclusterreceiver.otel-*` 中有效，其中命名空间是资源属性；事件接收器是例外。通过 `COUNT(attributes.k8s.namespace.name)` 对 `COUNT(*)` 进行比较以信任空事件结果。

**应用程序日志** 如果可用——在终止时间戳之前查看 200 行。如果不可用，标记 `no_logs_available`；不要编造日志模式。

**APM** 如果 Pod 运行受仪器服务——从 Pod 资源属性解析 `service.name` 以供后续关联。SLO / 延迟 / 错误率分析本身是 APM 层工作，超出此技能的范围。

**基线比较** —— 对于基于利用率的发现，将当前值与 7 天前的同一小时进行比较。只有相对于此工作负载的正常值，“高内存”才有意义。

### 检查上游原因（有条件）

只有当症状模式表明需要时才进行。阈值：上游错误率 >5× 基线，并且负载开始于目标服务上的症状之前。共病症状不建立因果关系。

如果 `metrics-service_destination.1m.otel-default` 对服务没有行，报告 `insufficient_dependency_data`——不是“上游健康”。

### 检查最近变化（有条件）

`SuccessfulCreate` / `Pulled` 事件在最后 2 小时内通常与部署相关。`logs-k8sobjectsreceiver.otel-*` 显示 configmap/secret/deployment 规格变化。在症状开始 15 分钟内发生变化是强相关性，但仍然只是相关性——验证它可能解释了您已分类的模式。

### 综合分析并停止

在获得足够证据以支持已知置信度的假设时，立即综合。您不需要完成前面的每个部分——调查在以下任一情况下终止：

- 您有一个高置信度假设和证实，或者
- 您有一个低/中置信度假设，并且进一步的查询不太可能改变情况（例如，日志不可用，APM 没有仪器，没有找到最近的更改）。

### 综合

默认结构：

```text
HYPOTHESIS (置信度：高 | 中 | 低)
<一段话：服务、症状、最可能的根本原因。命名分类中的故障模式。>

EVIDENCE
- <特征化中的发现，附带具体的指标或值。>
- <来自事件/日志/APM 的发现。>
- <来自基线比较、依赖检查或更改关联的发现。>

CONFIDENCE NOTE
<如果不是“高”。缺少的具体证据或模糊性。>

RECOMMENDED NEXT STEPS
1. <最可操作的——通常是一个配置检查或要观察的指标。>
2. <次要的。>

DOWNSTREAM IMPACT
<依赖于此工作负载的服务，或“未识别下游依赖关系”。>
```

**规模。** 整个综合分析运行 250–400 字。HYPOTHESIS 是两到三个句子。EVIDENCE 是三到五个单行，每个都引用具体的值，而不是重新解释它。RECOMMENDED NEXT STEPS 是两到三个单行——您实际上会首先执行的建议，而不是所有可以执行的建议。DOWNSTREAM IMPACT 是一个或两个句子。一个有充分证据的警报可以舒适地适应其中，长度不是彻底性，并且扫描中段事件的值班读者不会超过第一屏。

**当有两个假设同时存在时：** 将 HYPOTHESIS 替换为 COMPETING HYPOTHESES；列出两者，说明您倾向于哪一个以及原因，并列出可以消除它们的证据。

**当没有事件发生**（症状已解决，或者警报看起来不健康）：直接说明。`ALERT FIRED BUT SYSTEM APPEARS HEALTHY` 是一个有效的输出。列出您检查了什么以及您没有发现的内容。

**相关**

- **工作流程：`K8s CrashLoopBackOff Investigation`——警报触发的自动化的 Pod 级路径上的版本。运行确定性 ESQL + 分支；此技能提供了缺少的解释层，该层缺少工作流程。
- **Forge genome library：16 个 K8s 故障场景（OOMKill 级联、CPU 限制、探针配置错误、节点 NotReady、admission webhook 阻塞，等等）验证此技能的覆盖范围。
