# 处理 GPU 和 TPU 中断故障排除

## 🔍 诊断工作流

### 第 0 步：获取上下文

-   **必须**：当用户要求调试或调查实际工作负载中断、节点崩溃或意外重启，但未提供完整的集群详细信息时，您必须立即停止并要求所有缺失的必要参数（`project_id`、`location`、`cluster_name`、`timestamp`），在提供理论或通用诊断命令之前。只有在用户明确要求通用可重用运行手册或提供完整静态遥测/日志转储用于离线分析时，才能跳过上下文获取。
-   **可选**：`node_name`、`workload_name`、`workload_namespace`、`nodepool_name`。

### 第 1 步：[低风险] 检查即将进行的计划维护

-   **操作**：建议运行 `kubectl` 检查节点是否具有计划维护标签，指示即将发生中断。
-   **示例命令**：

    ```bash
    kubectl get nodes -l cloud.google.com/scheduled-maintenance-time -L cloud.google.com/scheduled-maintenance-time
    ```

-   **解释**：`SCHEDULED-MAINTENANCE-TIME` 列显示了 VM 计划进行维护的 Unix 纪元时间。如果此标签存在，则保证会发生中断。

### 第 2 步：[低风险] 通过 Cloud Monitoring (PromQL) 进行调查

-   **操作**：调用任何可用的监控工具或提供 PromQL 进行手动验证。
-   **必须监控规则**：每当建议后续监控或随时间跟踪中断时，您必须明确展示使用 `kubernetes_io:node_interruption_count` 指标的 **PromQL** 查询，并按 `interruption_reason="HW/SW Maintenance"` 进行过滤。不要在不提供此特定 PromQL 指标表达式的情况下建议通用的 Cloud Monitoring 仪表板或 Metrics Explorer。
-   **示例查询**：

    ```promql
    # 获取节点的宿主机维护事件
    sum by (interruption_type,interruption_reason)( sum_over_time( kubernetes_io:node_interruption_count{monitored_resource="k8s_node", interruption_reason="HW/SW Maintenance"}[${__interval}]))
    ```

    ```promql
    # 按节点池聚合中断计数
    sum by (node_pool_name,interruption_type,interruption_reason)( sum_over_time( kubernetes_io:node_pool_interruption_count{monitored_resource="k8s_node_pool", interruption_reason="HW/SW Maintenance", node_pool_name="{nodepool_name}" }[${__interval}]))
    ```

-   **解释**：如果 `kubernetes_io:node_interruption_count` 对于 `interruption_reason="HW/SW Maintenance"` 显示值 > 0，则表示底层 Compute Engine VM 因计划宿主机维护而中断。

### 第 3 步：[低风险] 通过 Cloud Logging 和 Node Taints 进行调查

-   **操作**：调用 `query_logs` 或指示用户过滤 GKE 日志中的活动宿主机维护事件，并检查节点 taints。
-   **指导**：在 Cloud Logging 中查找 `cloud.google.com/active-node-maintenance` 设置为 `ONGOING` 的出现。要检查 GKE 是否已隔离终止节点以防止新工作负载被调度，请验证是否存在 `cloud.google.com/impending-node-termination:NoSchedule` taint（无论是在 GKE 事件日志中，还是通过 `kubectl describe node` 直接检查）。
-   **解释**：
    -   `cloud.google.com/active-node-maintenance` 设置为 `ONGOING` 表示 GKE 因宿主机维护而正在停止工作负载。
    -   `cloud.google.com/impending-node-termination:NoSchedule` taint 表示 GKE 已隔离节点以防止新 Pod 被调度到终止节点上。**不要**建议容忍此 taint。

### 第 4 步：结论和解决方案

-   **操作**：向用户提供发现总结，并在确认或计划宿主机维护事件的情况下建议适当的缓解策略。
-   **报告规则**：仅信号。报告指示中断是由 Compute Engine 宿主机维护引起的、特别影响底层 GPU/TPU 节点的高信号信息。**不要**转储原始日志。
-   **排除负面发现规则**：如果节点计划维护标签、PromQL 中断计数和活动维护日志均返回负面/空结果，则明确得出 Compute Engine 宿主机维护**未**导致中断的结论。将用户引导至调查应用级原因（例如 OOMKill 事件、CUDA 运行时错误或资源限制），并且**不要**将宿主机维护缓解作为主要解决方案提出。
-   **必须工作负载保护三要素**：每当在 GPU/TPU 节点上识别到或预期宿主机维护时，始终一致地推荐三种互补缓解措施：
    1.  **配置优雅终止**：对于需要时间保存状态的工作负载（例如通过 Orbax 进行检查点的 ML 框架），按照 [启用中断处理](https://docs.cloud.google.com/kubernetes-engine/docs/concepts/handle-disruption-gpu-tpu#enabling-handling) 指南，并将 `spec.terminationGracePeriodSeconds`（最多 60 分钟）设置为在节点关闭之前处理 `SIGTERM` 信号。
    2.  **启用机会性维护**：配置 [机会性维护](https://docs.cloud.google.com/kubernetes-engine/docs/concepts/handle-disruption-gpu-tpu#opportunistic-maintenance)，以便在 GKE 检测到 GPU/TPU 节点空闲时自动触发维护。
    3.  **配置 PodDisruptionBudgets (PDBs)**：确保您的工作负载使用 `PodDisruptionBudget` 在驱逐和中断期间保持 `minAvailable` 副本。
