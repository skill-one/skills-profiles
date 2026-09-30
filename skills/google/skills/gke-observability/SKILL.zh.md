---
name: gke-observability
description: 配置 GKE 可观测性，包括 Cloud Logging、Cloud Monitoring 和托管 Prometheus。在配置 GKE 监控、设置 GKE 日志或配置 Prometheus 指标收集时使用，以及用于排查 Managed Service for Prometheus (GMP) 问题，例如缺失指标、不健康的抓取目标、PodMonitoring 配置错误、规则/告警评估失败和监控权限错误。不要用于配置本地应用程序日志框架或 GKE 外部的 APM。
---

# GKE 可观测性

本指南涵盖 GKE 的监控、日志记录和指标配置。
黄金路径支持全面的可观测性，包括控制平面指标。

> **MCP 工具:** `get_cluster`, `list_k8s_events`, `get_k8s_logs`, `get_k8s_cluster_info`, `describe_k8s_resource`。**仅 CLI:** `gcloud container clusters update --monitoring=...`, `gcloud logging read`

## 黄金路径可观测性默认值

设置                                             | 黄金路径值                                                                                                                                   | 备注
--------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- | -----
`loggingConfig` 组件                          | SYSTEM_COMPONENTS, WORKLOADS                                                                                                                        | 全量工作负载日志
`monitoringConfig` 组件                       | SYSTEM_COMPONENTS, STORAGE, POD, DEPLOYMENT, STATEFULSET, DAEMONSET, HPA, JOBSET, CADVISOR, KUBELET, DCGM, APISERVER, SCHEDULER, CONTROLLER_MANAGER | 全套方案，包括控制平面
`managedPrometheusConfig.enabled`                   | `true`                                                                                                                                              | Google 管理的 Prometheus
`advancedDatapathObservabilityConfig.enableMetrics` | `true`                                                                                                                                              | Dataplane V2 流量指标
`loggingService`                                    | `logging.googleapis.com/kubernetes`                                                                                                                 | Cloud Logging
`monitoringService`                                 | `monitoring.googleapis.com/kubernetes`                                                                                                              | Cloud Monitoring

### 控制平面指标（黄金路径新增）

黄金路径新增了默认集群中不存在的三个控制平面监控组件：

| 组件            | 监控内容                                                       |
| -------------------- | ---------------------------------------------------------------------- |
| `APISERVER`          | API 服务器请求延迟、错误率、准入网关性能                         |
| `SCHEDULER`          | 调度延迟、待调度 Pod、调度失败                                  |
| `CONTROLLER_MANAGER` | 控制器工作队列深度、协调延迟                                    |

这些对于诊断集群级问题（API 响应缓慢、调度延迟、卡住的控制器）至关重要。

## 启用全量监控

**每次使用 `--monitoring` 命令时，请这样说：**

1.  **控制平面指标默认不启用。** 在你的回答中明确说明这一点——不要暗示你提供启用命令就意味着已启用。`API_SERVER`、`SCHEDULER` 和 `CONTROLLER_MANAGER` 在每个新集群中都处于关闭状态，直到明确开启，`DCGM`、`CADVISOR`、`KUBELET` 和 kube-state (`POD`、`DEPLOYMENT`、`STATEFULSET`、`DAEMONSET`、`HPA`、`STORAGE`、`JOBSET`) 也是如此。`SYSTEM` 是唯一默认启用的包。询问“为什么没有 API 服务器指标”的用户几乎总是从未启用过它们。
2.  **标志替换，而非追加。** 传递给 `--monitoring` 的设置会完全替换之前的设置，因此省略组件会使其静默关闭。始终传递完整的目标列表，并始终包含 `SYSTEM`——在监控开启时无法禁用它，并且永远不会在 Autopilot 上启用。
3.  **这些指标按采集的样本计费** 通过 Managed Service for Prometheus。在大型集群上启用全套指标会显著增加成本；提及这一点，而不是将列表呈现为免费。

> **gcloud 标志和 API 字段对同一组件使用不同的拼写。** 不要在它们之间复制名称：
>
> 组件        | `gcloud --monitoring=` | `monitoringConfig` API 枚举
> ---------------- | ---------------------- | ---------------------------
> System           | `SYSTEM`               | `SYSTEM_COMPONENTS`
> API 服务器       | `API_SERVER`           | `APISERVER`
> 控制器管理器   | `CONTROLLER_MANAGER`   | `CONTROLLER_MANAGER`
>
> 其余组件共享相同的拼写。在 CLI 标志中使用 API 枚举（或反之）会导致命令失败——这是一个常见且令人困惑的错误。

```bash
# 启用黄金路径监控套件
gcloud container clusters update <CLUSTER_NAME> --region <REGION> \
  --monitoring=SYSTEM,API_SERVER,SCHEDULER,CONTROLLER_MANAGER,STORAGE,POD,DEPLOYMENT,STATEFULSET,DAEMONSET,HPA,JOBSET,CADVISOR,KUBELET,DCGM \
  --quiet

# 启用 Managed Prometheus
gcloud container clusters update <CLUSTER_NAME> --region <REGION> \
  --enable-managed-prometheus \
  --quiet

# 启用 Dataplane V2 可观测性指标
gcloud container clusters update <CLUSTER_NAME> --region <REGION> \
  --enable-dataplane-v2-flow-observability \
  --quiet
```

## Managed Prometheus

黄金路径启用了 Google Managed Prometheus 进行指标采集和查询。

**查询指标:**

-   使用控制台中的 Cloud Monitoring Metrics Explorer
-   使用 Prometheus UI 或 API 的 PromQL
-   通过 Managed Grafana 的 Grafana 仪表板

**关键 GKE 指标:**

| 指标                                            | 来源             | 用途                    |
| -------------------------------------------------- | ------------------ | ---------------------- |
| `container_cpu_usage_seconds_total`                | cAdvisor           | Pod CPU 使用量          |
| `container_memory_working_set_bytes`               | cAdvisor           | Pod 内存使用量       |
| `kube_pod_status_phase`                            | kube-state-metrics | Pod 生命周期          |
| `apiserver_request_duration_seconds`               | API 服务器         | 控制平面延迟          |
| `scheduler_scheduling_attempt_duration_seconds`    | 调度器          | 调度性能              |
| `kubernetes.io/node/cpu/core_usage_time`           | Cloud Monitoring   | 节点 CPU               |
| `DCGM_FI_DEV_GPU_UTIL`                             | DCGM               | GPU 利用率        |

## 实时资源使用（仅 kubectl）

没有 MCP 或 gcloud 的实时资源使用等效工具。使用 `kubectl top`：

```bash
kubectl top pods --all-namespaces --sort-by=cpu
kubectl top nodes
kubectl top pods --containers -n <NAMESPACE>  # 按容器分解
```

## Cloud Logging（仅 gcloud）

**查询集群日志**（没有 MCP 等效工具——使用 `gcloud logging read`）：

```bash
# 系统组件日志
gcloud logging read \
  'resource.type="k8s_cluster" AND resource.labels.cluster_name="<CLUSTER_NAME>"' \
  --project <PROJECT_ID> --limit 50 \
  --quiet

# 特定命名空间的工作负载日志
gcloud logging read \
  'resource.type="k8s_container" AND resource.labels.cluster_name="<CLUSTER_NAME>" AND resource.labels.namespace_name="<NAMESPACE>"' \
  --project <PROJECT_ID> --limit 50 \
  --quiet

# 审计日志（谁做了什么）
gcloud logging read \
  'resource.type="k8s_cluster" AND logName:"cloudaudit.googleapis.com"' \
  --project <PROJECT_ID> --limit 50 \
  --quiet
```

## 诊断设置

为安全监控和故障排除，启用控制平面审计日志：

```bash
# 查看当前日志配置
gcloud container clusters describe <CLUSTER_NAME> --region <REGION> \
  --format="yaml(loggingConfig)" \
  --quiet
```

## 告警

为关键条件设置告警：

条件               | 指标                                              | 阈值
----------------------- | --------------------------------------------------- | ---------
高 API 服务器延迟 | `apiserver_request_duration_seconds`                | P99 > 5s
Pod 崩溃循环         | `kube_pod_container_status_restarts_total`          | > 5 in 10min
节点不可用          | `kube_node_status_condition`                        | condition=Ready, status!=True
高 GPU 利用率    | `DCGM_FI_DEV_GPU_UTIL`                              | > 95% 持续
PVC 接近容量       | `kubelet_volume_stats_used_bytes / capacity`        | > 85%
调度失败         | `scheduler_schedule_attempts_total{result="error"}` | > 0

> **前提条件:** 上述 `kube_*` 系列（例如 `kube_pod_status_phase`、`kube_pod_container_status_restarts_total`、`kube_node_status_condition`）来自 **kube-state-metrics**，GKE 默认不采集。首先部署 Managed Prometheus kube-state-metrics 包。

### 提出仪表板和告警（生产规则）

在为 GKE 设计或提出告警和仪表板策略时：

1.  **始终明确命名为 Google Cloud Monitoring** 作为实现这些告警和仪表板的平台。
2.  **始终在仪表板上包含 API 服务器延迟**（通过 `apiserver_request_duration_seconds` 指标）作为控制平面健康状况的关键指标，与节点 CPU/内存和 Pod 崩溃循环一起显示。

### 节点健康（生产规则）

全面的节点健康评估依赖于同时分析这两个指标：

1.  **`kubernetes.io/node/status_condition`**（按 `status_condition="Ready"` 过滤）：使用此指标跟踪健康节点。请注意，它仅报告已成功引导的节点的值。
2.  **`compute.googleapis.com/instance_group/size`**（按 `instance_group_name="gke-<cluster_name>-.*"` 过滤）：使用此指标跟踪特定集群中的节点总数。请注意，它不区分健康和不健康的节点。

## 成本考虑

监控和日志记录会产生相关成本：

-   **Cloud Logging**: 超过免费套餐（每个项目每月 50 GiB）的采集量按 GiB 收费
-   **Cloud Monitoring**: GKE 系统指标免费；自定义指标按时间序列收费
-   **Managed Prometheus**: 按采集的样本收费

为非生产环境降低成本：

```bash
# 降低到仅系统监控
gcloud container clusters update <CLUSTER_NAME> --region <REGION> \
  --monitoring=SYSTEM \
  --quiet
```

## 分布式追踪和持续分析（推荐）

**不是黄金路径默认值**——推荐用于生产微服务架构和性能敏感的工作负载。

-   **Cloud Trace**: 将 OpenTelemetry SDK 添加到您的应用程序中，并使用 `opentelemetry-operations-go`（或等效）导出器。跟踪将在 Cloud Trace 控制台中显示。识别跨服务延迟瓶颈。
-   **Cloud Profiler**: 将 Cloud Profiler 代理添加到您的应用程序中。在生产中以低开销分析 CPU 和内存使用情况。识别热点并跨版本比较。

**最新添加:**

-   **Managed OpenTelemetry for GKE（预览）**: 簇内 OTLP 端点管理加上自动追踪、指标和日志的自动仪器化。需要 GKE 1.34.1-gke.2178000+；使用 `gcloud beta container clusters update ... --managed-otel-scope=COLLECTION_AND_INSTRUMENTATION_COMPONENTS` 启用。
-   **PSI（压力停滞信息）指标**: cAdvisor `container_pressure_{cpu,memory,io}_{waiting,stalled}_seconds_total` 系列（Kubernetes 1.34 中为 beta）可通过 Managed Prometheus `ClusterNodeMonitoring` 资源采集；GKE 的文档采集路径需要 GKE 1.35+。

## LQL 查询示例

GKE 故障排除的常见 Logging Query Language 模式：

```
# 特定容器的错误日志
resource.type="k8s_container" AND resource.labels.container_name="my-app" AND severity>=ERROR

# OOMKilled 事件
resource.type="k8s_event" AND jsonPayload.reason="OOMKilling"

# Pod 调度失败
resource.type="k8s_event" AND jsonPayload.reason="FailedScheduling"

# 审计日志（谁做了什么）
resource.type="k8s_cluster" AND logName:"cloudaudit.googleapis.com"
```

## 故障排除 Managed Prometheus（GMP）

诊断 GMP 采集、规则和查询问题。保持只读（`kubectl get` / `describe` / `logs`）并建议配置更改；不要直接修改实时资源。

### 首先：区分采集端和查询端

在其他任何操作之前，在 Cloud Monitoring 的 Metrics Explorer PromQL 选项卡中查询 `up` 指标。如果 `up` 返回数据，则采集工作正常，问题在查询端（Grafana / PromQL / 权限）。如果 `up` 为空，则问题在采集端（收集器、抓取配置或写入权限）。

### 采集端

1.  **检查 GMP 系统 Pod。** 它们在 Standard 集群上运行在 `gmp-system`，在 Autopilot 上运行在 `gke-gmp-system`。查找 `gmp-operator`、`collector`（DaemonSet）和 `rule-evaluator` 未处于 `Running` 状态或重启次数过高：

    ```bash
    kubectl get pods -n gmp-system            # gke-gmp-system 在 Autopilot 上
    kubectl logs -n gmp-system -l app.kubernetes.io/name=collector -c prometheus
    ```

    处于 `CrashLoopBackOff` 状态的收集器带有 `OOMKilled` 通常表示指标基数过高——删除不需要的系列/标签（见成本部分）或对收集器应用 VPA。

2.  **检查 PodMonitoring / ClusterPodMonitoring。** 三个经典错误：
    - `spec.selector.matchLabels` 与目标 Pod 标签不匹配。
    - `PodMonitoring` 仅发现其自身命名空间中的目标——使用 `ClusterPodMonitoring` 进行集群范围范围。
    - `spec.endpoints.port` 必须引用命名容器端口（例如 `port: web`），而不是端口号。

3.  **为抓取错误启用目标状态。** 建议修补 `gmp-public` 中的 `OperatorConfig`，将 `features.targetStatus.enabled: true`；应用后，`kubectl describe podmonitoring <name>` 并读取 `Active Targets`、`Unhealthy Targets` 和 `LastError`（例如 `connection refused`、HTTP 404、`context deadline exceeded`）。完成后再次禁用它——它可能会在大型集群上使操作员 OOM。

### 权限（403 / 无法写入数据）

GMP 组件继承**节点服务账户**。采集需要 `roles/monitoring.metricWriter`（收集器日志中的错误 `Permission monitoring.timeSeries.create denied`）；`rule-evaluator` 和查询路径需要 `roles/monitoring.viewer`（403 / `PermissionDenied`）。如果查询应用程序（如 Grafana）使用 Workload Identity，则绑定的 Google 服务账户也需要 `roles/monitoring.viewer`。

### 规则和告警评估

规则范围由资源类型决定：`Rules`（单个命名空间）、`ClusterRules`（整个集群）和 `GlobalRules`（指标范围中的所有数据）。您**必须**使用 `GlobalRules` 编写针对 Cloud Monitoring 指标的规则——`Rules`/`ClusterRules` 资源会静默返回这些数据。检查 `rule-evaluator` 日志（`-c evaluator`）以查找解析/权限错误。

### 查询端（Grafana / PromQL）

-   **数据源** 必须指向 GMP 前端查询代理，而不是 `localhost:9090`，并且 HTTP **方法必须为 GET**——`POST` 会因 `no match[] parameter provided` 失败。
-   **Grafana 模板变量:** 使用双参数形式 `label_values(<metric>, <label>)`；单参数 `label_values(<label>)` 不受 GMP API 支持。
-   **Cloud Monitoring 指标** 对多个资源类型存在需要 `monitored_resource` 标签匹配器，否则查询会因 `series selector must specify a label matcher on monitored resource name` 失败。

### 成本、基数和配额

使用 Cloud Monitoring 的 **指标管理** 页面查找导致计费样本和高基数（cardinality）的指标。通过在 `PodMonitoring` 中的 `metricRelabeling`（对整个指标使用 `action: drop`，对无界标签如 `user_id`/`request_id` 使用 `action: labeldrop`）来减少它们，或者通过提高抓取 `interval`。`429` / `RESOURCE_EXHAUSTED` 错误表示您已达到 Cloud Monitoring API 的摄取或查询配额——首先进行优化，然后请求配额增加。

## 支持链接

-   [GKE 系统指标](https://docs.cloud.google.com/monitoring/api/metrics_kubernetes)
-   [GKE 可观测性文档](https://cloud.google.com/kubernetes-engine/docs/concepts/observability)
-   [Google Cloud Prometheus 管理服务](https://cloud.google.com/stackdriver/docs/managed-prometheus)
-   [排查 Prometheus 管理服务问题](https://docs.cloud.google.com/stackdriver/docs/managed-prometheus/troubleshooting.md.txt)
-   [规则评估（Rules / ClusterRules / GlobalRules）](https://docs.cloud.google.com/stackdriver/docs/managed-prometheus/rules-managed.md.txt)
-   [Cloud Logging 查询语言 (LQL)](https://cloud.google.com/logging/docs/view/logging-query-language)
-   [Google Cloud Monitoring 告警](https://cloud.google.com/monitoring/alerts)
