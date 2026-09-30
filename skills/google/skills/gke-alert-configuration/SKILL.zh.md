---
name: gke-alert-configuration
description: 在 Terraform 中为 Google Kubernetes Engine (GKE) 集群、工作负载和服务配置警报策略，使用 PromQL 和 Google Cloud 托管的 Prometheus 服务。在编写、分析、验证或部署 Terraform 警报策略以使用多窗口多燃烧率 SLO 警报监控 GKE 服务延迟、流量、错误率，以及内存饱和和集群健康状况（如 CrashLoopBackOff 和 Node NotReady 条件）时使用。不适用于非 GKE 计算运行时，例如独立的 Compute Engine VM 或没有 GKE 的独立 Cloud Run 服务。
---

# GKE 告警配置

本技能提供了创建健壮、高信号告警策略的指南和最佳实践，用于使用 Google Cloud 托管的 Prometheus 服务和 Terraform 创建 Google Kubernetes Engine (GKE) 工作负载的告警策略。它确保全面覆盖 **4 个黄金信号** 和关键集群健康指标，同时最大限度地减少告警噪音。

--------------------------------------------------------------------------------

## 关键规则

*   **非 GKE 独立运行时的负向触发器和作用域重定向**：
    *   本技能严格限定于使用 PromQL 和 Google Cloud 托管的 Prometheus 服务进行监控的 Google Kubernetes Engine (GKE) 工作负载、集群和服务。
    *   **不应用于非 GKE 计算运行时**，例如独立的 Compute Engine 虚拟机或无 GKE 的独立 Cloud Run 服务。
    *   **立即停止并直接响应（不要编辑文件）**：当用户请求非 GKE 计算基础设施的告警配置时：
        1.  **不要在磁盘上编写、创建、编辑或验证任何 Terraform 文件**。
        2.  **立即停止并直接在聊天中响应用户**：
            *   **明确说明超出范围**：明确指出独立的 Compute Engine 虚拟机监控或独立的 Cloud Run 监控不在本特定于 GKE 的 PromQL 告警技能范围内，该技能专为 GKE 工作负载使用 Google Cloud 托管的 Prometheus 服务和 PromQL 设计。
            *   **不要生成 GKE PromQL 告警**：不要创建或生成 Kubernetes PromQL 告警策略，也不要为非 GKE 基础设施虚构 Kubernetes 容器、Pod 或节点资源。
            *   **引导用户**：引导并重定向用户使用标准的 `google_monitoring_alert_policy` 配置 `condition_threshold` 或 MQL，或推荐相关的专业 Cloud 可观测性技能，例如 `compute.googleapis.com/instance/cpu/utilization` 或 `run.googleapis.com/request_latencies`。
*   **强制 `kube-state-metrics` (KSM) 成本防护栏**：
    *   在 Google Cloud 托管的 Prometheus 服务中部署开源的 `kube-state-metrics` 会产生可计费指标摄取成本。
    *   **立即停止并先请求权限（不要编辑文件）**：当请求的告警规则依赖于 **Tier 2 KSM 指标**（例如 `kube_cronjob_*`、`kube_pod_status_phase`、`kube_persistentvolume_*`、`kube_deployment_*`、`kube_statefulset_*`、`kube_job_*` 或 `kube_daemonset_*`）时，**在获得用户批准之前，不要编写、创建、编辑或验证任何 Terraform 文件或生成告警策略**。
    *   相反，你必须**立即停止并直接响应用户**：
        1.  **提醒用户**请求的告警需要 `kube-state-metrics`。
        2.  **解释成本影响**：详细说明 `kube-state-metrics` 在 Google Cloud 托管的 Prometheus 服务中会产生可计费样本摄取成本。
        3.  **请求明确授权**：在假设、启用或生成 KSM 依赖的告警配置之前，必须先请求用户的明确授权。
        4.  **建议过滤或白名单**：建议并推荐仅过滤或白名单特定的所需指标，例如使用具有 `metricRelabeling` (`action: keep`) 的 `PodMonitoring` 资源或 KSM `--metric-allowlist` 来最小化摄取成本。提供一个具体的白名单示例。
    *   **始终优先选择非 KSM 本地替代方案**（Tier 1 cAdvisor 或文档中记录的本地 GKE 指标 [metrics_and_alerts_catalog.md](references/metrics_and_alerts_catalog.md)），例如使用 `container_memory_working_set_bytes` 和 `container_spec_memory_limit_bytes` 而不是 `kube_pod_container_resource_limits`。
    *   **在响应中明确 Tier 和成本附加费**：在生成或推荐告警策略的每个响应中，你必须**明确说明其分类 Tier 和成本影响**：
        *   **Tier 1 本地或标准指标**（GKE 内置指标、cAdvisor `container_*`、kubelet 卷统计、kubelet 节点状态和控制平面指标；参见 [metrics_and_alerts_catalog.md](references/metrics_and_alerts_catalog.md)）：说明它是 **Tier 1 本地或标准指标，且 KSM 成本附加费为 0**。
        *   **Tier 2 KSM 指标**：说明它是 **Tier 2 KSM 依赖指标**，并遵循上述权限和白名单防护栏。*(提示：通常，以 `kube_` 开头的表示资源状态或元数据的指标属于 Tier 2)。*
*   **批准文件编辑的计划-验证-执行循环**：在工 作区中对磁盘上的已批准 Terraform 文件进行修改、添加或合并时，请遵循三阶段工作流程：
    1.  **计划**：起草一个结构化的变更计划 (`changes.json`)，其中包含建议的策略资源名称、PromQL 表达式、分组标签和持续时间。
    2.  **验证**：运行预编辑验证脚本 (`python3 scripts/validate_config.py --plan changes.json`) 来验证 PromQL 语法、回溯窗口、持续时间规则，并确保没有重复的信号。
    3.  **执行**：计划通过验证后，将更改原位应用到目标 Terraform 配置 (`alerts.tf`)。
    4.  *注意*：在直接在聊天中回答问题或提供 Terraform 片段时，如果不需要磁盘修改，请在响应中输出完整的、有效的 Terraform HCL 块。
*   **配置 4 个黄金信号和集群健康**：始终确保目标 Kubernetes 工作负载或服务具有以下告警覆盖范围：
    1.  **延迟**（P95 响应时间）
    2.  **错误**（多窗口多燃烧率 SLO 告警，例如 Fast Burn 1 小时 / 5 分钟，系数 14.4，Slow Burn 6 小时 / 30 分钟，系数 6.0；不要使用简单的静态比率）
    3.  **流量**（突然下降或完全消失的指标使用 `absent()` 或 `default 0` 语法，或过载峰值）
    4.  **饱和（仅内存限制利用率）**：在描述或配置集群或项目的告警策略时，仅包含**内存饱和**（`container_memory_working_set_bytes` / `container_spec_memory_limit_bytes`）。**不要**包含 CPU 饱和告警或列出 `container_cpu_usage_seconds_total` 作为告警指标，因为 CPU 是可压缩的，并由 CFS 配额限制，而不是导致不可压缩的致命终止（OOM）。
    5.  **集群健康**（Pod CrashLooping、Node NotReady）
*   **仅 PromQL（托管 Prometheus）**：你必须使用 `condition_prometheus_query_language` 并使用 PromQL。**不要**使用 MQL 或标准的 `condition_threshold`，除非用户明确请求。Google Cloud 托管的 Prometheus 服务是 GKE 的标准遥测摄取路径。
*   **仅 Terraform**：生成的可观测性配置**仅**作为 Terraform（`.tf`）文件编写，例如 `alerts.tf` 和 `variables.tf`。
*   **动态多资源告警（不要硬编码）**：除非用户明确请求，否则你**不能**在告警条件中硬编码特定的 Pod 名称、节点名称或服务名称。告警策略必须编写为动态覆盖资源：
    *   始终使用分组聚合（`by (cluster, namespace, service, pod, container)`）而不是过滤到单个实例。这允许单个告警策略动态跟踪每个服务或 Pod。
    *   始终声明并使用 Terraform 变量 `project_id`、`cluster_name` 和 `namespace` (`var.project_id`、`var.cluster_name`、`var.namespace`)，以便跨环境重用配置。始终在 `variables.tf`（或在配置中）定义这些变量，并在策略或 PromQL 标签匹配器中引用所有三个。
*   **回溯中不要有冗余的持续时间窗口**：
    *   当 PromQL 表达式已经使用聚合回溯窗口（例如 `increase(...[15m]) > 3` 或多窗口 SLO 燃烧率）时，查询时间窗口已经平滑了瞬态峰值。
    *   在 PromQL 回溯窗口之上添加 Terraform 持续时间会增加检测时间（MTTD），而不会提供额外的平滑效益。
    *   在这种情况下，将 Terraform `duration = "0s"`（或 `"60s"`）。不要在 `[15m]` 之上强制 `duration = "300s"`，这会延迟关键的 CrashLooping 告警长达 20 分钟（15 分钟 + 5 分钟）。
    *   仅在瞬时仪表条件上使用 `duration = "300s"`，例如 `kube_node_status_condition == 0`。
*   **使用 SLO 燃烧率而不是简单比率**：对于错误率告警，始终生成多窗口多燃烧率（MWMBR）SLO 告警（例如 14.4 倍的燃烧率，1 小时和 5 分钟窗口，用于 99% 的 SLO），而不是简单的错误率比率（`rate(5xx)/rate(total) > 0.05`），后者在低流量时会产生过多的误报。
*   **健壮的流量下降检测（`absent()` / `default 0`）**：在监控流量降至零时，不要单独使用 `rate(...) == 0`，因为当没有请求发生时 Prometheus 时间序列会完全消失（评估为空向量而不是 0）。使用 `default 0` 语法，例如 `sum(rate(...[5m])) default 0 == 0`，或 `absent(...) == 1`。
*   **通知通道**：默认情况下，不要在用户输入之前配置任何通知通道。如果用户明确提供了一个通知通道，请配置告警使用它。否则，你必须在你的响应中提示用户是否希望配置一个。
*   **参考 GKE 指标和开源告警目录**：在设计和生成评估套件或告警策略时，参考 [metrics_and_alerts_catalog.md](references/metrics_and_alerts_catalog.md) 以获取公共 GKE 指标（`kubernetes.io/`）和开源 Kubernetes 告警（`awesome-prometheus-alerts`）。
*   **纯英文响应**：你必须包括对告警作用的纯英文解释。解释告警测量什么，阈值代表什么，触发器表示什么。
*   **用户标签**：在所有 `google_monitoring_alert_policy` 资源中包含一个 `user_labels` 块，以跟踪由本技能创建的策略：

    ```terraform
    user_labels = {
      created-with-google-skill = "gke-alert-configuration"
    }
    ```

--------------------------------------------------------------------------------

## Terraform 中的告警策略结构

告警策略必须使用 `google_monitoring_alert_policy` 资源并使用 `condition_prometheus_query_language` 进行定义。始终在 `variables.tf` 中声明 `project_id`、`cluster_name` 和 `namespace`。

```hcl
# variables.tf
variable "project_id" {
  type        = string
  description = "Google Cloud 项目 ID"
}

variable "cluster_name" {
  type        = string
  description = "GKE 集群名称"
}

variable "namespace" {
  type        = string
  description = "目标 Kubernetes 命名空间"
  default     = "default"
}

variable "slo_target" {
  type        = number
  description = "SLO 目标分数（例如 0.99 表示 99%）"
  default     = 0.99
}
```

```hcl
# alerts.tf
# 示例：多窗口多燃烧率（MWMBR）SLO 告警（Fast Burn：14.4 倍，1 小时和 5 分钟窗口）
resource "google_monitoring_alert_policy" "k8s_service_error_rate_slo" {
  project      = var.project_id
  display_name = "[K8s] ${var.cluster_name} - 服务错误率 SLO Fast Burn"
  combiner     = "OR"

  conditions {
    display_name = "错误预算 Fast Burn（1 小时和 5 分钟窗口 14.4 倍）"
    condition_prometheus_query_language {
      query    = <<-EOT
        (
          (
            sum(
              rate(
                http_requests_total{
                  cluster="${var.cluster_name}",
                  namespace="${var.namespace}",
                  status=~"5.."
                }[5m]
              )
            ) by (service, namespace, cluster)
            /
            sum(
              rate(
                http_requests_total{
                  cluster="${var.cluster_name}",
                  namespace="${var.namespace}"
                }[5m]
              )
            ) by (service, namespace, cluster)
          ) > (1 - ${var.slo_target}) * 14.4
        )
        and
        (
          (
            sum(
              rate(
                http_requests_total{
                  cluster="${var.cluster_name}",
                  namespace="${var.namespace}",
                  status=~"5.."
                }[1h]
              )
            ) by (service, namespace, cluster)
            /
            sum(
              rate(
                http_requests_total{
                  cluster="${var.cluster_name}",
                  namespace="${var.namespace}"
                }[1h]
              )
            ) by (service, namespace, cluster)
          ) > (1 - ${var.slo_target}) * 14.4
        )
      EOT
      duration = "0s"
    }
  }
}
```

--------------------------------------------------------------------------------

## 遥测指标和 PromQL 示例

对于 GKE 指标（`kubernetes.io/`）、社区开源告警（`awesome-prometheus-alerts`）、KSM 成本防护栏和非 KSM 本地替代方案，你必须阅读并遵循：

*   [metrics_and_alerts_catalog.md](references/metrics_and_alerts_catalog.md)

对于与每个黄金信号对应的特定 PromQL 查询，你必须阅读并遵循：

*   [promql_queries.md](references/promql_queries.md)

对于 GKE 集群先决条件、启用 Google Cloud 托管的 Prometheus 服务收集、配置 PodMonitoring 自定义抓取以及启用控制平面指标收集（API Server、Controller Manager、Scheduler），你必须阅读并遵循：

*   [gke_configuration_prerequisites.md](references/gke_configuration_prerequisites.md)

--------------------------------------------------------------------------------

## 工具脚本和验证循环

在仓库中工作时，使用 `validate_config.py` 脚本验证变更计划和 Terraform 配置：

*   **预编辑计划验证**：起草一个 `changes.json` 计划，指定建议的策略、查询和持续时间，并在编辑前验证它：
    *   命令：`python3 scripts/validate_config.py --plan changes.json`
*   **编辑后和目录验证**：扫描目录中的现有或已修改的 Terraform 文件，以确保没有重复或语法错误：
    *   命令：`python3 scripts/validate_config.py --directory [TARGET_TF_DIR]
        --cluster-var "${var.cluster_name}"`
    *   单个文件验证：`python3 scripts/validate_config.py --file
        [PATH_TO_TF_FILE]`

--------------------------------------------------------------------------------

## 技术注意事项和陷阱

*   **回溯窗口与持续时间缓冲**：
    *   不要向已经使用聚合回溯窗口（如 `increase(...[15m])`）或多窗口 SLO 指标率的警报添加大的 `duration = "300s"` 缓冲。
    *   `increase(...[15m]) > 3` 中的 `[15m]` 窗口已经平滑了峰值。添加 `duration = "300s"` 会通过强制重启计数保持在 3 以上额外 5 分钟连续时间，从而延迟警报长达 20 分钟。
    *   使用回溯窗口函数时，使用 `duration = "0s"` 或 `"60s"`。将 `duration = "300s"` 保留用于原始瞬时仪表条件，例如 `kube_node_status_condition == 0`。
*   **仅针对集群告警的内存饱和**：
    *   不要为集群或工作负载监控配置 CPU 饱和警报。CPU 是可压缩的（由 CFS 调度器限制），而内存是不可压缩的（会触发 OOMKills）。
    *   使用 `container_memory_working_set_bytes` / `container_spec_memory_limit_bytes` 配置内存饱和。
*   **缺失资源限制盲点（强制说明）**：比较使用与限制（如 `container_spec_memory_limit_bytes`）的饱和警报，如果工作负载在其 Kubernetes 配置文件中未配置显式内存限制，则 **无法解析** 或返回 `NaN`。
    *   **强制指令**：每次生成、讨论或推荐比较使用与限制（包括使用 `container_spec_memory_limit_bytes` 的非 KSM cAdvisor 替代方案）的内存饱和警报时，你 **必须明确说明并在你的回复中警告用户**，容器内存限制必须在 Kubernetes Pod 配置文件或清单中显式配置（`resources.limits.memory`），以便饱和查询能够解析（而不是返回 `NaN` 或无法解析）。
*   **线性磁盘预测 (`predict_linear`)**：当使用 `predict_linear(kubelet_volume_stats_available_bytes[6h:5m], 4 * 24 * 3600) < 0` 预测卷耗尽时，解释 `predict_linear` 使用最近回溯窗口（例如 6 小时）的线性回归来预测可用磁盘何时会低于 0（例如，在 4 天内）。将 `kubelet_volume_stats_available_bytes` 标识为具有零 KSM 超额成本的 Tier 1 原生 kubelet 指标。
*   **API 服务器错误和客户端指标**：
    *   `apiserver_request_total` 和 `rest_client_requests_total` 是具有零 KSM 成本超额的 Tier 1 控制平面指标。解释 `apiserver_request_total` 监控 API 服务器端点的 5xx HTTP 错误率，而 `rest_client_requests_total` 监控与 API 服务器通信的 REST 客户端发送的 4xx 和 5xx 请求。
*   **流量消失陷阱 (`absent()` / `default 0`)**：
    *   当流量完全降至零时，Prometheus 和 GMP 停止发出 `http_requests_total` 时间序列。
    *   `sum(rate(...[5m])) == 0` 评估为空向量，阻止告警触发。
    *   始终使用 `sum(rate(...[5m])) default 0 == 0` 或 `absent(...) == 1` 以可靠地检测流量完全丢失。
*   **崩溃重启与正常重启**：容器偶尔重启可能是正常的，例如作业完成或小规模滚动更新。使用 `kube_pod_container_status_restarts_total` 并设置 `duration = "0s"` 来告警 **频繁** 重启（例如 15 分钟内重启超过 3 次），以避免噪音。
*   **节点升级**：在 GKE 集群升级期间，节点会被排空并重启，这可能触发“节点 NotReady”告警。警告用户这些告警可能在维护窗口期间触发，或建议如果支持则配置维护窗口。

--------------------------------------------------------------------------------

## 额外资源

*   [Google Cloud 管理服务 Prometheus 文档](https://docs.cloud.google.com/monitoring/managed-prometheus.md.txt)
*   [GKE 可观察性和监控概念](https://docs.cloud.google.com/kubernetes-engine/docs/concepts/monitoring.md.txt)
*   [Google Cloud 在 Terraform 中的告警策略](https://docs.cloud.google.com/monitoring/alerts/terraform-alert-policy.md.txt)
*   [Google Cloud 监控定价](https://docs.cloud.google.com/monitoring/pricing.md.txt)
*   [Google SRE 工作簿：SLO 告警](https://sre.google/workbook/alerting-on-slos/)
*   [Awesome Prometheus 告警仓库](https://github.com/samber/awesome-prometheus-alerts)
