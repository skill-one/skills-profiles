# GKE JobSet 中断故障排除

使用此技能系统性地诊断和解决 GKE 集群上大型 AI/ML 工作负载的 JobSet 中断、重启和抢占问题。

## ⚠️ 前置条件及沙箱规则

-   您的集群必须在 `kube-state-metrics` 中启用 JobSet 指标包。
-   为 Google Cloud 项目启用 Cloud Logging 和 Cloud Monitoring。
-   **自主及沙箱执行规则**：如果 API 查询、工具或命令遇到 `403 权限被拒绝`、认证错误或网络隔离，**请勿进入认证或凭证故障排除循环**。用获取到的变量（`{project_id}`、`{cluster_name}`、`{workload_name}`、`{start_time}`、`{end_time}`）填充查询模板，如果可用，检查任何本地暂存的遥测数据或模拟数据文件，并自主完成诊断工作流和解决建议。

## 🔍 诊断工作流

### 第 0 步：上下文获取和时间窗口定义

使用工具、工作区文件、环境详细信息或用户提示上下文独立收集上下文：

-   **项目 ID** (`{project_id}`)
-   **集群名称** (`{cluster_name}`)
-   **工作负载名称（JobSet 名称）** (`{workload_name}`)
-   **工作负载命名空间** (`{namespace}`)
-   **问题时间** (`{issue_time}`)

如果用户未明确提供特定变量，请检查集群资源或日志以确定它们，或使用提供的 `{variable}` 占位符。

#### 时间处理规则

1.  **自主时间窗口**：如果提供了相对时间（例如，“X 分钟前”）或未提供确切时间戳，则根据当前时间或可用日志时间戳计算查询窗口。
2.  **窗口计算**：如果可用 `{issue_time}`（或计算为 `T`），则设置 `{start_time}` = `T - 30m` 和 `{end_time}` = `T + 30m`。

--------------------------------------------------------------------------------

### 第 1 步：识别 JobSet 重启和尝试 [低风险]

验证 JobSet 是否正在经历重启循环，并确定重启的频率。

#### 可视化图表 / MQL 查询 - 重启

-   **MQL 查询规范**：

    ```mql
    fetch prometheus_target
    | metric 'prometheus.googleapis.com/kube_jobset_restarts/gauge'
    | filter resource.cluster_name == '{cluster_name}' && metric.jobset_name == '{workload_name}'
    | align next_older(1m)
    | every 1m
    | group_by [metric.jobset_name], [val: max(value)]
    ```

#### PromQL 指标查询 - 重启

-   **PromQL 查询规范**：

    ```promql
    kube_jobset_restarts{jobset_name="{workload_name}", cluster="{cluster_name}"}
    ```

-   **诊断逻辑**：重启的非零或递增值表示 JobSet 正由于工作节点故障或中断而被控制器主动重启。

-   **自动化**：报告结果后自动进入第 2 步。

--------------------------------------------------------------------------------

### 第 2 步：检查 Nodepool 中断 [低风险]

确定 JobSet 重启是否由物理节点池级事件（如 spot 抢占、维护或主机终止）触发。

#### A. 指标查询（Nodepool 中断计数）

##### 可视化图表 / MQL 查询 - 中断

-   **MQL 查询规范**：

    ```mql
    fetch k8s_node_pool
    | metric 'kubernetes.io/node_pool/interruption_count'
    | filter cluster_name == '{cluster_name}'
    | align next_older(10m)
    | every 10m
    | group_by [metric.interruption_type, metric.interruption_reason, metadata.system.node_pool_name], [val: sum(value)]
    ```

##### PromQL 查询 - 中断

-   **PromQL 查询规范**：

    ```promql
    sum by (interruption_type, interruption_reason, node_pool_name, cluster_name) (
      avg_over_time(kubernetes_io:node_pool_interruption_count{cluster_name="{cluster_name}"}[10m])
    )
    ```

#### B. 日志查询（Nodepool 生命周期事件）

-   **LQL 日志过滤器规范**：

    ```sql
    resource.type="gke_nodepool"
    AND resource.labels.cluster_name="{cluster_name}"
    AND timestamp >= "{start_time}"
    AND timestamp <= "{end_time}"
    ```

-   **诊断逻辑**：

    -   **PreemptionEvent**：Spot 虚拟机被抢占，或节点被缩放。
    -   **MaintenanceEvent**：节点池更新或 Google 安排的维护。
    -   **TerminationEvent**：严重的宿主机故障。检查 `interruption_reason` 或日志以查找宿主机问题。
    -   查看 [故障特征](references/failure_signatures.md) 以了解节点终止日志和抢占事件的示例。

-   **自动化**：自动进入第 3 步。

--------------------------------------------------------------------------------

### 第 3 步：检查节点和底层主机 VM [低风险]

将节点就绪失败与物理宿主机 VM 关联起来，查看是否有单个故障主机反复失败协调器 Pod。

#### A. 指标查询（节点就绪状态检查）

##### 可视化图表 / MQL 查询 - 节点状态

-   **MQL 查询规范**：

    ```mql
    fetch k8s_node
    | metric 'kubernetes.io/node/status_condition'
    | filter cluster_name == '{cluster_name}' && metric.condition == 'Ready' && metric.status == 'False'
    | align next_older(1m)
    | every 1m
    | group_by [node_name, metadata.user.gke_nodepool], [val: max(value)]
    ```

##### PromQL 查询 - 节点状态

-   **PromQL 查询规范**：

    ```promql
    sum by (status, condition, node_pool_name) (
      kubernetes_io:node_status_condition{cluster_name="{cluster_name}", condition="Ready", status="False"}
    )
    ```

#### B. 指标查询（节点到主机元数据拓扑关联）

-   **MQL 查询规范**：

    ```mql
    fetch k8s_node
    | metric 'kubernetes.io/node/cpu/total_cores'
    | filter cluster_name == '{cluster_name}'
    | align next_older(1m)
    | every 1m
    | group_by [node_name, metadata.user.gce_topology_host, metadata.user.gke_nodepool], [val: max(value)]
    ```

#### C. 日志查询（节点故障日志）

-   **LQL 日志过滤器规范**：

    ```sql
    resource.type="k8s_node"
    AND resource.labels.cluster_name="{cluster_name}"
    AND (textPayload:"host error" OR textPayload:"kernel panic" OR textPayload:"hardware failure" OR textPayload:"NodeNotReady")
    AND timestamp >= "{start_time}"
    AND timestamp <= "{end_time}"
    ```

-   **诊断逻辑**：识别特定节点是否不健康（`Ready=False` 或 `Unknown`），并通过 `metadata.user.gce_topology_host` 将其关联到 GCE 物理主机 ID。检查同一主机是否反复失败。

-   **自动化**：自动进入第 4 步。

--------------------------------------------------------------------------------

### 第 4 步：检查 Pod 和工作节点 / 容器故障 [低风险]

分析 Pod 状态阶段并检索协调器工作节点日志，以识别应用程序级崩溃或网络死锁。

> **必需执行顺序**：在检查特定工作节点容器日志（第 C 部分）之前，您**必须**分析 Pod 状态阶段（第 A 部分）和不可调度 Pod 指标（第 B 部分），以评估整体工作负载健康状况。

#### A. 指标查询（Pod 生命周期阶段）

##### 可视化图表 / MQL 查询 - Pod 阶段

-   **MQL 查询规范**：

    ```mql
    fetch k8s_pod
    | metric 'kubernetes.io/pod/status/phase'
    | filter cluster_name == '{cluster_name}' && pod_name ==~ '{workload_name}.*'
    | align next_older(10m)
    | every 10m
    | group_by [metric.phase], [val: count()]
    ```

##### PromQL 查询 - Pod 阶段

-   **PromQL 查询规范**：

    ```promql
    sum by (phase) (
      avg_over_time(kube_pod_status_phase{cluster="{cluster_name}", pod=~"{workload_name}.*"}[10m])
    )
    ```

#### B. 指标查询（不可调度 Pod 计数）

-   **MQL 查询规范**：

    ```mql
    fetch k8s_pod
    | metric 'kubernetes.io/pod/status/unschedulable'
    | filter cluster_name == '{cluster_name}' && pod_name ==~ '{workload_name}.*'
    | align next_older(10m)
    | every 10m
    | group_by [pod_name], [val: max(value)]
    ```

#### C. 日志查询（工作节点容器日志）

-   **LQL 日志过滤器规范**：

    ```sql
    resource.type="k8s_container"
    AND resource.labels.cluster_name="{cluster_name}"
    AND labels."k8s-pod/jobset_sigs_k8s_io/jobset-name"="{workload_name}"
    AND timestamp >= "{start_time}"
    AND timestamp <= "{end_time}"
    ```

-   **诊断逻辑**：

    1.  检查 Pod 时间线以发现挂起或不可调度的 Pod。
    2.  使用工作节点容器日志分析切片 0（协调器）中的工作节点 0，以查找 NCCL 超时、集体通信问题或 MegaScale 挂起。

-   **自动化**：进入解决步骤。

--------------------------------------------------------------------------------

## 🛠️ 解决方案工作流

### 解决方案 1：抢占和自动缩放优化 [低风险]

如果第 2 步显示 Spot VM 上存在高抢占计数：

-   **操作**：建议将关键长时间运行训练工作负载切换到 **GKE 保留/按需 VM**，或利用 **紧凑放置策略** 以最小化碎片化中断。
-   **理由**：消除 spot 市场抢占，减少训练重启。

### 解决方案 2：隔离故障主机 VM [高风险]

如果第 3 步确定特定主机 ID（`gce-topology-host`）在多次尝试中始终失败或触发重启：

-   **操作**：建议隔离/排空 GKE 节点，删除底层 GCE VM 实例以触发实例重新创建，并向 Google Cloud 支持开立支持工单，指定物理主机 ID。
-   **理由**：GKE 自动修复将在健康的物理硬件上重新创建 VM 实例，防止无限重启循环。

--------------------------------------------------------------------------------

## 📋 复制粘贴清单

-   [ ] 收集上下文并计算 `{start_time}`（`{issue_time} - 30m`）和 `{end_time}`（`{issue_time} + 30m`）窗口。
-   [ ] 查询 JobSet 重启尝试。
-   [ ] 检查 Nodepool 中断（spot 抢占与硬件终止）。
-   [ ] 查询节点到主机映射，并检查节点日志以查找物理主机错误。
-   [ ] 检查 Pod 时间线状态和协调器工作节点容器日志。
-   [ ] 建议适当的调度策略（按需 vs Spot）或主机 VM 隔离。
