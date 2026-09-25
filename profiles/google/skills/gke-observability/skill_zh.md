# GKE 可观测性

本指南涵盖 GKE 的监控、日志记录和指标配置。
黄金路径可全面实现可观测性，包括控制平面指标。

> **MCP 工具：** `get_cluster`、`list_k8s_events`、`get_k8s_logs`、
> `get_k8s_cluster_info`、`describe_k8s_resource`。**仅 CLI：** `gcloud
> container clusters update --monitoring=...`、`gcloud logging read`

## 黄金路径可观测性默认值

设置                                             | 黄金路径值                                                                                                                                   | 备注
--------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- | -----
`loggingConfig` 组件                          | SYSTEM_COMPONENTS、WORKLOADS                                                                                                                        | 全量工作负载日志
`monitoringConfig` 组件                       | SYSTEM_COMPONENTS、STORAGE、POD、DEPLOYMENT、STATEFULSET、DAEMONSET、HPA、JOBSET、CADVISOR、KUBELET、DCGM、APISERVER、SCHEDULER、CONTROLLER_MANAGER | 全套方案，包括控制平面
`managedPrometheusConfig.enabled`                   | `true`                                                                                                                                              | Google 管理的 Prometheus
`advancedDatapathObservabilityConfig.enableMetrics` | `true`                                                                                                                                              | 数据平面 V2 流量指标
`loggingService`                                    | `logging.googleapis.com/kubernetes`                                                                                                                 | Cloud Logging
`monitoringService`                                 | `monitoring.googleapis.com/kubernetes`                                                                                                              | Cloud Monitoring

### 控制平面指标（黄金路径新增）

黄金路径新增了默认集群中不存在的三个控制平面监控组件：

| 组件            | 监控内容                                                       |
| -------------- | ---------------------------------------------------------------- |
| `APISERVER`          | API 服务器请求延迟、错误率、准入网关性能                     |
| `SCHEDULER`          | 调度延迟、待调度 Pod、调度失败                  |
| `CONTROLLER_MANAGER` | 控制器工作队列深度、协调延迟                    |

这些对于诊断集群级问题（API 响应缓慢、调度延迟、卡住的控制器）至关重要。

## 启用全量监控

**每次提供 `--monitoring` 命令时，请这样说：**

1.  **控制平面指标默认情况下是禁用的。** 在你的回答中明确说明这一点——不要暗示你提供启用命令就意味着已启用。`API_SERVER`、`SCHEDULER` 和 `CONTROLLER_MANAGER` 在每个新集群上都是关闭的，并且在明确启用之前不会收集任何数据，`DCGM`、`CADVISOR`、`KUBELET` 和 kube-state (`POD`、`DEPLOYMENT`、`STATEFULSET`、`DAEMONSET`、`HPA`、`STORAGE`、`JOBSET`) 也是如此。`SYSTEM` 是唯一默认启用的包。询问“为什么没有 API 服务器指标”的用户几乎总是从未启用过它们。
2.  **该标志替换，而不是追加。** 传递给 `--monitoring` 的设置会完全覆盖之前的设置，因此省略组件会使其被静默禁用。始终传递完整的目标列表，并且始终包含 `SYSTEM`——在监控启用时无法禁用它，并且在 Autopilot 上永远不会启用。
3.  **这些指标按收集的样本数量计费** 通过 Managed Service for Prometheus。在一个大型集群上启用全套指标会显著增加成本；提及这一点，而不是将列表呈现为免费。

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

黄金路径启用了 Google Managed Prometheus 用于指标收集和查询。

**查询指标：**

-   使用控制台中的 Cloud Monitoring Metrics Explorer
-   使用 Prometheus UI 或 API 的 PromQL
-   通过 Managed Grafana 的 Grafana 仪表板

**关键的 GKE 指标：**

| 指标                                            | 来源             | 用途                    |
| -------------------------------------------------- | ------------------ | ---------------------- |
| `container_cpu_usage_seconds_total`                | cAdvisor           | Pod CPU 使用量          |
| `container_memory_working_set_bytes`               | cAdvisor           | Pod 内存使用量       |
| `kube_pod_status_phase`                            | kube-state-metrics | Pod 生命周期          |
| `apiserver_request_duration_seconds`               | API 服务器         | 控制平面延迟          |
| `scheduler_scheduling_attempt_duration_seconds`    | 调度器          | 调度性能                |
| `kubernetes.io/node/cpu/core_usage_time`           | Cloud Monitoring   | 节点 CPU               |
| `DCGM_FI_DEV_GPU_UTIL`                             | DCGM               | GPU 利用率        |

## 实时资源使用（仅限 kubectl）

没有 MCP 或 gcloud 的实时资源使用等效项。使用 `kubectl top`：

```bash
kubectl top pods --all-namespaces --sort-by=cpu
kubectl top nodes
kubectl top pods --containers -n <NAMESPACE>  # 按容器分解
```

## Cloud Logging（仅限 gcloud）

**查询集群日志**（没有 MCP 等效项——使用 `gcloud logging read`）：

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

## 警报

为关键条件设置警报：

条件               | 指标                                              | 阈值
----------------------- | --------------------------------------------------- | ---------
高 API 服务器延迟 | `apiserver_request_duration_seconds`                | P99 > 5s
Pod 崩溃循环         | `kube_pod_container_status_restarts_total`          | > 5 in 10min
节点不可用          | `kube_node_status_condition`                        | condition=Ready, status!=True
高 GPU 利用率    | `DCGM_FI_DEV_GPU_UTIL`                              | > 95% 持续
PVC 接近容量       | `kubelet_volume_stats_used_bytes / capacity`        | > 85%
调度失败         | `scheduler_schedule_attempts_total{result="error"}` | > 0

> **前提条件：** 上述 `kube_*` 系列（例如 `kube_pod_status_phase`、`kube_pod_container_status_restarts_total`、`kube_node_status_condition`）来自 **kube-state-metrics**，GKE 默认不收集。首先部署 Managed Prometheus kube-state-metrics 包。

### 提出仪表板和警报（生产规则）

在为 GKE 设计或提出警报和仪表板策略时：

1.  **始终明确指定 Google Cloud Monitoring** 作为实现这些警报和仪表板的平台。
2.  **始终在仪表板上包含 API 服务器延迟**（通过 `apiserver_request_duration_seconds` 指标）作为控制平面健康状况的关键指标，同时包括节点 CPU/内存和 Pod 崩溃循环。

### 节点健康（生产规则）

全面的节点健康评估依赖于同时分析这两个指标：

1.  **`kubernetes.io/node/status_condition`**（按 `status_condition="Ready"` 过滤）：使用此指标跟踪健康节点。请注意，它仅报告已成功引导的节点的值。
2.  **`compute.googleapis.com/instance_group/size`**（按 `instance_group_name="gke-<cluster_name>-.*"` 过滤）：使用此指标跟踪特定集群中的节点总数。请注意，它不会区分健康和不健康的节点。

## 成本考虑

监控和日志记录具有相关成本：

-   **Cloud Logging**：超出免费套餐（每个项目每月 50 GiB）的每 GiB 收费
-   **Cloud Monitoring**：GKE 系统指标免费；自定义指标按时间序列收费
-   **Managed Prometheus**：按收集的样本数量收费

为非生产环境降低成本：

```bash
# 降低到仅系统监控
gcloud container clusters update <CLUSTER_NAME> --region <REGION> \
  --monitoring=SYSTEM \
  --quiet
```

## 分布式追踪和持续分析（推荐）

**不是黄金路径默认值**——推荐用于生产微服务架构和性能敏感的工作负载。

-   **Cloud Trace**：将 OpenTelemetry SDK 添加到您的应用程序中，并使用 `opentelemetry-operations-go`（或等效）导出器。跟踪将在 Cloud Trace 控制台中显示。识别跨服务延迟瓶颈。
-   **Cloud Profiler**：将 Cloud Profiler 代理添加到您的应用程序中。在生产中以低开销分析 CPU 和内存使用情况。识别热点并跨版本比较。

**最新添加：**

-   **Managed OpenTelemetry for GKE（预览）**：集群内 OTLP 端点管理加上对跟踪、指标和日志的自动仪器化。需要 GKE 1.34.1-gke.2178000+；使用 `gcloud beta container clusters update ... --managed-otel-scope=COLLECTION_AND_INSTRUMENTATION_COMPONENTS` 启用。
-   **PSI（压力停滞信息）指标**：cAdvisor `container_pressure_{cpu,memory,io}_{waiting,stalled}_seconds_total` 系列（Kubernetes 1.34 中为 beta）可通过 Managed Prometheus `ClusterNodeMonitoring` 资源收集；GKE 的文档收集路径需要 GKE 1.35+。

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

## 支持链接

-   [GKE 系统指标](https://docs.cloud.google.com/monitoring/api/metrics_kubernetes)
-   [GKE 可观测性文档](https://cloud.google.com/kubernetes-engine/docs/concepts/observability)
-   [Google Cloud Managed Service for Prometheus](https://cloud.google.com/stackdriver/docs/managed-prometheus)
-   [Cloud Logging Query Language (LQL)](https://cloud.google.com/logging/docs/view/logging-query-language)
-   [Google Cloud Monitoring 警报](https://cloud.google.com/monitoring/alerts)
