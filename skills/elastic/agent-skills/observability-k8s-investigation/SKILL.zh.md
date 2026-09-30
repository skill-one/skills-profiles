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

此技能和 [参考资料/query-recipes.md](references/query-recipes.md) 中的所有 ES|QL 查询都通过 `POST /_query` 运行。使用 `GET kbn:/api/alerting/rules/_find` 读取告警状态。字段存在性检查使用 `GET /<index>/_mapping` 或 `GET /_field_caps`。[操作](#operations) 表将每个映射到其 `elastic` CLI 等效命令。

## 范围

**在范围内：** OTel 接收器命名空间索引（`metrics-kubeletstatsreceiver.otel-*`、`metrics-k8sclusterreceiver.otel-*`、`logs-k8seventsreceiver.otel-*`、`logs-k8sobjectsreceiver.otel-*`）和 OTel 语义约定（`k8s.pod.name`、`k8s.namespace.name`、`k8s.container.restarts`）。

**超出范围：**

- 遗留的 Elastic Agent Kubernetes 集成（`metrics-kubernetes.*`、`logs-kubernetes.*`、`kubernetes.*` 字段）。
  已弃用——不要针对这些路径编写查询。
- APM 层分析（服务 SLO 违规、事务错误率、上游依赖健康）。不同领域——一旦 K8s 根本原因被排除或确认，转交给 **observability-sre-triage** 技能，该技能负责 SLO 状态和消耗率、活动告警规则、吞吐量、延迟、错误率、依赖健康和日志分流。当工作负载根本不是 Kubernetes 托管的时，也使用该技能。
- 集群创建、容量规划、成本优化。不同领域。

## 指南

这些适用于每次调查。如有疑问，在编写综合分析之前重新阅读它们。

**证据的缺失不是证据。不要从空结果中编造结论。** 如果日志查询返回 0 行，日志可能未收集或 Pod 没有最近的日志行——这并不意味着“依赖不可用”或任何其他特定故障模式。报告 `no_logs_available` 并相应地权衡其余信号。

**空依赖数据 ≠ 上游健康。** 没有使用 APM 仪器化（负载生成器、工作器）的服务不会发出目标指标。报告 `insufficient_dependency_data`，而不是“上游正常”。

**共病症状不是原因。** 两个服务同时退化通常共享上游，而不是因果关系。只有在 (a) 一个服务的退化明显先于另一个服务，并且 (b) 差值较大（错误率 >5×、延迟 >3×）时，才归因于因果关系。

**OOMKilled 默认 ≠ 内存泄漏。** 限制可能只是工作负载工作集 undersized。通过内存曲线的形状区分它们：单调上升到限制并在每次重启时重置，负载平坦且最近没有部署，是泄漏特征——以高置信度确认它。当形状不明确时（尖峰、昼夜、负载相关）——而不是作为每个 OOMKilled 发现的先决条件——使用 7 天相同小时的基线。

**错误终止默认 ≠ 应用程序错误。** 首先检查 `k8s.container.cpu_limit_utilization`。CFS 限制导致的 liveness probe 超时是此空间中最常见的误诊。

**平均 CPU 隐藏限制。** Pod 在 40–60% 的平均 `cpu_limit_utilization` 下可能看起来健康，但在 p99 时受到严重限制。Linux 在 100ms 期间执行 CPU 限制；突发工作负载在期间内达到配额并停滞。查看最大值和 p95，而不仅仅是平均值。

**重启计数是布尔值，不是计数器。** `k8s.container.restarts` 直接从 K8s API 拉取，并且 kubelet 可以随时修剪它，因此绝对值不可靠。将其视为 `== 0`（没有最近重启）与 `> 0`（最近重启）；不要从中推导出回退定时或“线性与指数”模式。通过 K8s `Killing` / `BackOff` 事件确认重启模式。

**优先报告不确定性而不是制造信心。** 如果证据是模糊的，综合分析应该说明这一点。竞争假设是有效输出。

同样，不要制造不确定性。上述规则是关于模糊证据，而不是语气。当关键信号存在并得到证实时，以高置信度确认它。将一个明确的发现降低到“中等”与过度声明一样都是缺陷。

**提交综合分析并停止。** 在 HYPOTHESIS 行中只声明一次置信度——不要再次按要点声明。除非结果改变了结论，否则不要叙述运行了哪些查询，也不要将告警重述给读者。在 RECOMMENDED NEXT STEPS 或 DOWNSTREAM IMPACT 上结束；永远不要以“想让我进一步调查吗？”等提议结束。后续工作属于建议列表，建议以建议的形式表达。

## 索引和字段

### 哪里查找

| 信号                | 索引模式                                       | 用途                                                                 |
| --------------------- | --------------------------------------------------- | ------------------------------------------------------------------- |
| Pod/容器运行时       | `metrics-kubeletstatsreceiver.otel-*`               | CPU、内存、网络、文件系统。利用率比率。                               |
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
| `k8s.namespace.name`                             | 仅指标                     | 命名空间。映射但 **null** 在 k8seventsreceiver     |
| `attributes.k8s.namespace.name`                  | k8seventsreceiver           | 事件上的命名空间——在此处按此形式过滤         |
| `k8s.container.name`                             | 所有 k8s                     | Pod 中的容器                                    |
| `k8s.deployment.name`                            | k8sclusterreceiver + others | 父部署                                       |
| `k8s.pod.phase`                                  | k8sclusterreceiver          | Pending=1/Running=2/Succeeded=3/Failed=4/Unknown=5      |
| `k8s.container.restarts`                         | k8sclusterreceiver          | 容器重启总数                           |
| `k8s.container.status.last_terminated_reason`    | k8sclusterreceiver          | `OOMKilled`、`Error`、`Completed`、`ContainerCannotRun` |
| `k8s.pod.status_reason`                          | k8sclusterreceiver          | Pod 级别原因 (`Evicted`、`NodeLost`)                |
| `k8s.container.memory_limit_utilization`         | kubeletstatsreceiver        | 0.0–1.0+（可能暂时超过 1）          |
| `k8s.container.cpu_limit_utilization`            | kubeletstatsreceiver        | 0.0–N（在 CFS 限制下经常 >1）              |
| `k8s.pod.memory_limit_utilization`               | kubeletstatsreceiver        | 整个 Pod 的聚合；在使用它之前查看下注         |
| `k8s.pod.cpu_limit_utilization`                  | kubeletstatsreceiver        | 整个 Pod 的聚合；在使用它之前查看下注         |
| `k8s.pod.memory.usage` / `.working_set`          | kubeletstatsreceiver        | 字节                                                   |
| `k8s.node.condition_memory_pressure`             | k8sclusterreceiver          | 1 = 压力, 0 = 正常                                    |
| `k8s.node.condition_ready`                       | k8sclusterreceiver          | 0 = NotReady                                            |
| `k8s.hpa.current_replicas` / `.desired_replicas` | k8sclusterreceiver          | HPA 状态                                               |
| `attributes.k8s.event.reason`                    | k8seventsreceiver           | 事件原因（在此处过滤）                           |
| `body.text`                                      | k8seventsreceiver / logs    | 事件消息 / 日志消息                             |
| `k8s.object.name`                                | k8seventsreceiver           | 涉及对象名称（日志属性，使用扁平形式）      |

### 容器级与 Pod 级限制利用率

在 **容器** 级别读取限制利用率。`k8s.container.cpu_limit_utilization` 和 `k8s.container.memory_limit_utilization` 是默认值；Pod 级别的配对是不同的测量，不是同义词。

接收器在 **同一数据流中的单独文档** 上发出这两类：Pod 级字段出现在不携带 `k8s.container.name` 的文档上，而容器级字段仅出现在携带 `k8s.container.name` 的文档上。因此，`STATS ... BY k8s.container.name` 返回每个 Pod 级字段的 `null`，反之亦然。在 9.6.0 集群上 1 小时测量：42,240 个没有容器名称的文档中，360 个携带 `k8s.pod.cpu_limit_utilization`，没有携带容器字段；18,240 个有容器名称的文档中，900 个携带容器字段，没有携带 Pod 字段。

可用性也存在差异。容器级利用率针对每个声明限制的容器发出，而 Pod 级聚合需要 **每个** Pod 中的容器都声明它。在两个实时集群 3 小时内，没有 Pod 携带 Pod 级字段而没有携带容器级字段，而 27 个 Pod 携带容器级字段但缺少 Pod 级字段——它们都是多容器 Pod，其中只有一些容器声明了限制。在 sidecar 注入的 Pod 上进行 Pod 级限制检查会静默返回 `null`。

| 集群       | 仅容器级 | 两个级别 | 无   | 仅 Pod 级 |
| ------------- | -------------------- | ----------- | ------- | -------------- |
| forge-factory | 18                   | 7           | 44      | 0              |
| k8s-demo      | 9                    | 6           | 40      | 0              |

仅在问题确实关于整个 Pod 时使用 Pod 级字段——总消耗与其容器限制的总和——并且在确认它们已填充后。**observability-sre-triage** 应用相同规则，因此这两个技能对同一 Pod 返回相同的答案。

### 字段可用性

上述几个字段在标准的 kube-stack 收集器中默认关闭，需要显式配置。在依赖它们之前使用 `GET /<index>/_mapping` 或 `GET /_field_caps` 验证存在性；如果缺失，按注释说明回退，并在综合分析中说明替代方案。

| 字段                                                              | 可能缺失的原因                                                                                                       | 备用方案                                                                                                                                                                                                                                                                                                                                                               |
| ------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `k8s.container.status.last_terminated_reason`                      | k8sclusterreceiver中的可选指标；受`metrics_collected.metadata`配置控制。                                      | 从K8s `Killing` / `OOMKilling`事件（在`logs-k8seventsreceiver.otel-*`中）和应用程序日志中的退出代码中推断。                                                                                                                                                                                                                                                           |
| `k8s.pod.status_reason`                                            | 同样 — k8sclusterreceiver上的可选指标。                                                                                 | 从事件中推断：`Evicted`，`NodeLost`，`Preempted`。                                                                                                                                                                                                                                                                                                                  |
| `k8s.container.cpu_limit_utilization` / `memory_limit_utilization` | 仅在容器声明相应限制时发出，并且仅在kubeletstatsreceiver指标启用时发出。 | `k8s.pod.cpu.node.utilization` / `k8s.pod.memory.node.utilization`以节点容量的分数表示消耗，无论是否声明限制都会发出；或者对基线趋势绝对`container.cpu.usage` / `container.memory.usage`。这两个备用方案都位于pod级文档上，因此按`k8s.pod.name`分组，而不是`k8s.container.name`。 |
| `k8s.pod.cpu_limit_utilization` / `memory_limit_utilization`       | 需要pod中的每个容器声明该限制，因此大多数多容器pod上不存在。                       | 使用容器级字段，这些字段更频繁地可用。                                                                                                                                                                                                                                                                                                                              |
| `k8s.node.condition_memory_pressure`                               | 受k8sclusterreceiver `node_conditions_to_report`（默认省略此条件）控制。                                             | 比较`k8s.node.memory.usage`与`k8s.node.allocatable_memory`，或在节点上查找`Evicted`事件。                                                                                                                                                                                                                                                                            |

如果使用备用方案，请在综合分析中注明（例如，`(via memory.usage; limit_utilization not collected)`)，以便读者知道该信号是间接的。

## ES|QL常见问题

在编写查询之前，了解这些。它们都会静默地产生错误答案，而不是大声失败。

**`VALUES()`对于单个唯一值返回标量，对于多个值返回数组。** 假设数组形状的模板（例如，`| first`）在标量时提取字符串的第一个字符。使用`MV_FIRST(VALUES(...))`或处理两者。

**`VALUES()`比这个技能的基础版本更新。** 它在Serverless上已GA，但在Stack上仅在8.14.0版本中为预览，仅在9.4.0版本中为GA，在8.14.0版本以下根本不存在。在使用它之前检查`GET /`：`build_flavor: "serverless"`表示它可用，否则读取`version.number`。如果不可用，将字段移入`BY`子句而不是聚合——每行唯一值携带相同的信息：

```esql
| STATS restarts = MAX(k8s.container.restarts), phase = MAX(k8s.pod.phase)
    BY term_reason = k8s.container.status.last_terminated_reason
| SORT restarts DESC
| LIMIT 10
```

**`PERCENTILE`不适用于OTel `histogram`类型**（截至8.15）。对于APM持续时间百分位数，使用`AVG`对`aggregate_metric_double`摘要字段（`AVG(transaction.duration.summary)`将总和除以value_count）进行计算。对于真正的百分位数，回退到Kibana查询DSL。

**`COUNT(agg_metric_double)`返回`value_count`（事件），而不是文档数。** `SUM(field)`给出总和组件；`AVG(field)`给出总和/value_count。不要使用`SUM(transaction.duration.summary)`作为事件计数代理——它返回总持续时间。

**K8s指标在ES|QL中使用扁平的OTel字段路径。** `k8s.pod.name`，而不是`resource.attributes.k8s.pod.name`。嵌套形式用于原始日志文档。

## 故障模式分类

分类词汇——跨工作负载、节点、控制平面、自动扩展和网络层每个模式的信号和佐证检查，以及当两个模式适用时该做什么——存在于[references/failure-modes.md](references/failure-modes.md)。在分类之前阅读它。

## 信号解释

### 内存

- **在30-60分钟内单调上升** → 泄漏。检查该语言的GC指标：JVM `jvm.gc.duration`，Go `process.runtime.go.gc.pause_ns`，Node `v8js_gc_duration`。GC频率/暂停随稳定活动集的上升是泄漏的经典特征。
- **昼夜/负载相关尖峰** → 负载驱动，不是泄漏。考虑HPA调优或限制增加。
- **达到1.0然后重启** → 确认OOMKilled。应用程序日志中的退出代码137（SIGKILL）一致。

### CPU

- `cpu_limit_utilization > 1.0` 持续 → CFS限流。节点有备用CPU；pod受到配额限制。
- 限流的症状（不是限流指标本身）：liveness probe超时，p99延迟4-16倍p50，上游队列背压，错误原因容器终止。
- 平均值可能看起来健康，而p95被限流。不要单独信任平均值。

### 重启模式

- `restarts > 0` 最近 → 工作负载一直在重启。不要将幅度读入计数（见_重启计数是布尔值_）；从K8s `Killing` / `BackOff`事件时间戳（在`logs-k8seventsreceiver.otel-*`中）确认模式。
- 与内存压力相关（`memory_limit_utilization → 1.0`）的重启 → OOMKilled路径。
- 没有内存/CPU压力的重启 → 探针配置错误，应用程序错误，或启动依赖失败。拉取`Unhealthy`和`Killing`事件。

### 终止原因

- `OOMKilled` → 内存路径。
- `Error` → 非零退出。检查应用程序日志；如果为空/最小，则检查CPU限流，然后再将其归因于应用程序逻辑。
- `Completed` → 运行完成。对于Jobs/CronJobs/init容器是正常的；否则异常。
- `ContainerCannotRun` → 运行时/镜像/执行问题。检查镜像拉取事件。

## 调查流程

> 调查不是清单。下面的部分描述了一个_典型_的弧——**根据你发现的内容压缩、跳过或重新访问它们。** 当你有足够证据可以在已知置信度下综合时即可终止。在收益递减点之后追踪信号是一种故障模式，而不是彻底性。

### 定位

确定目标：`k8s.pod.name`，`k8s.namespace.name`，可选`k8s.deployment.name`和`service.name`。如果没有给定时间窗口，对于pod级调查默认为最后一小时，对于事件关联默认为最后2小时，对于持续/未解决的故障默认为最后6小时。

如果警报有效负载已经告诉你故障模式（例如，它专门在`OOMKilled`时触发），请记下并跳过分类；直接进入确认和基线比较。

### 描述

获取工作负载最近行为的形状：重启计数、终止原因、阶段、利用率。通常一个或两个查询就足够了。

```esql
FROM metrics-k8sclusterreceiver.otel-*
| WHERE k8s.pod.name == "<pod>" AND k8s.namespace.name == "<ns>"
  AND @timestamp > NOW() - 1 hour
| STATS restarts = MAX(k8s.container.restarts),
        term_reasons = VALUES(k8s.container.status.last_terminated_reason),
        phase = MAX(k8s.pod.phase)
```

`VALUES()`需要Serverless或Stack 8.14+（GA 9.4）。在较旧的Stack集群上使用[ES|QL常见问题](#esql-gotchas)中的`BY`子句重写，而不是从查询中省略终止原因。

```esql
FROM metrics-kubeletstatsreceiver.otel-*
| WHERE k8s.pod.name == "<pod>" AND @timestamp > NOW() - 15 minutes
| STATS mem_pct = ROUND(MAX(k8s.container.memory_limit_utilization) * 100, 1),
        cpu_pct = ROUND(MAX(k8s.container.cpu_limit_utilization) * 100, 1)
    BY k8s.container.name
```

按容器分组：sidecar注入的pod有多个，并且只有声明限制的那些会报告利用率。如果所有列都返回`null`，则没有声明限制——按照[字段可用性](#field-availability)下的描述回退，而不是将`null`读作空闲。

### 分类

使用[references/failure-modes.md](references/failure-modes.md)中的分类法。关键信号应匹配；“调查”列告诉你要寻找的佐证。

当两个模式适用时，记下两者，并继续具有更强关键信号的其中一个。可以在佐证过程中修改。

### 佐证

拉取你的分类预测你会找到的证据。典型来源：

**K8s事件**对于命名空间和时间窗口：

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

**命名空间是此接收器上的日志属性，而不是资源属性。** 过滤`attributes.k8s.namespace.name`，而不是扁平的`k8s.namespace.name`。扁平形式在此数据流上映射，因此使用它的查询会解析并执行并返回**没有错误**的零行——在一个Stack 9.4.4集群上，扁平字段在832个事件中的0个上被填充，而`attributes.`形式在所有事件上都携带命名空间，因此扁平过滤器丢弃了300个匹配的`BackOff`，`Killing`和`Unhealthy`事件。扁平的`k8s.*`路径在`metrics-kubeletstatsreceiver.otel-*`和`metrics-k8sclusterreceiver.otel-*`上工作，其中命名空间是资源属性；事件接收器是例外。在`metrics-kubeletstatsreceiver.otel-*`和`metrics-k8sclusterreceiver.otel-*`上确认`COUNT(attributes.k8s.namespace.name)`与`COUNT(*)`之前不要信任空事件结果。

**应用程序日志**如果可用——查看终止时间戳之前的200行。如果不可用，标记`no_logs_available`；不要编造日志模式。

**APM**如果pod运行的是instrumented service——从pod资源属性解析`service.name`以供后续关联。SLO/延迟/错误率分析本身是APM层的工作，不在此技能范围内。

**基线比较**——对于基于利用率的发现，将当前值与7天前的同一小时进行比较。只有相对于此工作负载的正常值，“高内存”才有意义。

### 检查上游原因（有条件）

只有当症状模式表明它时才进行。阈值：上游错误率 >5× 基线 _或_ 延迟 >3× 基线，并且退化发生在目标服务上的症状之前。共症状不能建立因果关系。

如果`metrics-service_destination.1m.otel-default`对于服务没有行，报告`insufficient_dependency_data`——不是“上游健康。”

### 检查最近变更（有条件）

`SuccessfulCreate` / `Pulled`事件在过去2小时内通常与部署相关。`logs-k8sobjectsreceiver.otel-*`显示configmap/secret/deployment spec变更。在症状发生15分钟内发生变更是一个强关联，但仍然是一个关联——验证它可能解释了分类的模式。

### 综合并停止

一旦你有足够证据支持已知置信度的假设，就立即综合。你不需要完成所有前面的部分——调查在以下任一情况下终止：

- 你有一个高置信度假设和佐证，或者
- 你有一个低/中置信度假设，并且进一步的查询不太可能改变情况（例如，日志不可用，APM未instrumented，未发现最近变更）。

### 综合

默认结构：

```text
假设（置信度：高 | 中 | 低）
<一段话：服务、症状、最可能的原因。从分类词汇中命名故障模式。>

证据
- <来自描述的发现，附带具体指标或值。>
- <来自事件/日志/APM的发现。>
- <来自基线比较、依赖检查或变更关联（如果进行）。>

置信度说明
<如果不是'高'。缺少的具体证据或模糊之处。>

建议下一步
1. <最可操作的——通常是配置检查或观察指标。>
2. <次要的。>

下游影响
<依赖此工作负载的服务，或'未发现下游依赖'。>
```

**扩展。** 整个综合分析运行250-400字。HYPOTHESIS是两到三句话。EVIDENCE是三到五个单行要点，每个都引用具体值而不是重新解释它。RECOMMENDED NEXT STEPS是两到三个单行项目——是你实际会首先做的，而不是所有可以做的事情。DOWNSTREAM IMPACT是一两句。有充分证据的警报可以舒适地适应这个结构；长度不是彻底性，并且当班读者在扫描中段事件时不会超过第一屏。

**当有两个假设同时存在时：** 将HYPOTHESIS替换为COMPETING HYPOTHESES；列出两者，说明你倾向于哪一个以及原因，并列出可以消除歧义的证据。

**当没有发现事件时**（症状已解决，或警报看似虚假）：直接说明。
`ALERT FIRED BUT SYSTEM APPEARS HEALTHY`是有效输出。列出你检查了什么以及你没有发现什么。

### 置信度校准

从**高**开始并根据缺失内容降级：

- 降级到**中**如果：主要信号清晰但佐证缺失（没有日志，没有APM，无法进行基线比较）。或者：两个模式适用而你无法消除歧义。
- 降级到**低**如果：只有一个信号支持假设，信号冲突，或者该模式需要你无法获取的证据。

当应用程序日志数据缺失并且假设依赖于应用程序行为时，永远不要返回**高**。缺乏证据不能佐证假设。

### 查询配方

最常重启的pods、CPU限流、节点内存压力、准入拒绝和触发警报路径的现成查询位于[references/query-recipes.md](references/query-recipes.md)。

### 示例

### "为什么我的pod CrashLoopBackOff-ing？"

首先描述：获取重启计数、终止原因、内存和CPU利用率。

- 如果 `last_terminated_reason == "OOMKilled"` 且内存利用率达到 1.0 → 内存路径。与 7 天基线数据对比：单调上升表示泄漏；尖峰表示负载驱动。如果已知语言，检查 GC 指标。
- 如果 `last_terminated_reason == "Error"` 且 `cpu_limit_utilization > 1.0` → CPU 限制路径。与存活探针配置（initialDelaySeconds, timeoutSeconds）和 K8s 的 `Unhealthy` 事件对比。
- 如果 `last_terminated_reason == "Error"` 且 CPU 正常 → 应用逻辑路径。在终止前拉取最近日志。
- 如果 `last_terminated_reason == "ContainerCannotRun"` → 镜像/执行路径。检查 K8s 的 `Failed` 拉取事件。

综合判断，给出适当置信度。如果错误路径下日志不可用，降级为中等置信度并说明。

### "我的发布卡住了吗？"

权威信号：`k8s.deployment.available < k8s.deployment.desired` 持续超过 10 分钟。

诊断约束：

- 新 ReplicaSet 的 K8s 事件：`FailedCreate` → 承认拒绝（配额、webhook、PSP）。`FailedScheduling` → 没有节点匹配。
- 新 Pod 利用率：所有内存为 0% → 从未启动（镜像拉取失败）；高 CPU 且低内存 → 启动缓慢触发就绪探针。
- HPA 状态：负载下稳定 `current_replicas < desired_replicas` → 未就绪 Pod 抑制。

### "警报已触发但一切看起来正常"

可能且值得明确命名。检查：

- 症状是否已解决？将当前利用率/重启率与警报触发点对比。
- 警报是否是已衰减的瞬时峰值？
- 警报是否适当调整（例如，评估窗口过短）？

输出：`ALERT FIRED BUT SYSTEM APPEARS HEALTHY` 并说明你检查的内容。如果模式反复出现，建议调整警报设置。

## 相关

- **工作流：** `K8s CrashLoopBackOff 调查` — 警报触发的自动版本，对应上述 Pod 级路径。运行确定性 ESQL + 分支；这项技能提供工作流缺乏的解释层。
- **Forge 基因库：** 16 种 K8s 失败场景（OOMKill 级联、CPU 限制、探针配置错误、节点 NotReady、承认 webhook 阻塞等）验证这项技能的覆盖范围。

## 运维

| HTTP API (缩写)                | `elastic` CLI 命令                                             |
| ----------------------------------- | ----------------------------------------------------------------- |
| `GET /`                             | `elastic es info`                                                 |
| `POST /_query`                      | `elastic es esql query --format tsv --query '<esql>'`             |
| `GET /<index>/_mapping`             | `elastic es indices get-mapping --index '<index>'`                |
| `GET /_field_caps`                  | `elastic es field-caps --index '<index>' --fields '<fields>'`     |
| `GET kbn:/api/alerting/rules/_find` | `elastic kb alerting get-alerting-rules-find --filter '<filter>'` |
