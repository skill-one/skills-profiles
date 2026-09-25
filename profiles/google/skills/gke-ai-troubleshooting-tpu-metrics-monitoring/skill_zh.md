# GKE TPU 指标监控指南

该技能使代理能够使用 GKE 系统指标监控 GKE TPU 工作负载、节点和节点池。它有助于诊断工作负载中断或性能问题是否由底层基础设施引起。

## 第 0 步：强制上下文

使用可用的 GKE 和 Cloud 工具独立收集所需的上下文（例如集群详细信息或节点池名称），或使用提供的 `{variable}` 占位符：

- `{project_id}`：GCP 项目 ID。
- `{cluster_name}`：GKE 集群名称。
- `{location}`：GKE 集群位置（区域或区域）。
- `{node_name}`：(可选) 特定 GKE 节点的名称。
- `{node_pool_name}`：(可选) GKE 节点池的名称。

---

## 诊断步骤

### 第 1 步：验证 TPU 运行时指标配置 [低风险] [自动]

在分析运行时指标之前，请验证工作负载是否已配置为导出这些指标。这确保了集群和容器环境已设置为自动指标抓取，并能够查看加速器健康状况。

- **操作**：验证 Pod 规范和集群是否满足以下先决条件：
  - TPU 容器上暴露 `containerPort: 8431`（Prometheus 指标抓取所需）。
  - 如果使用 JAX，则 JAX 版本为 `0.4.14` 或更高版本（早期版本不导出运行时指标）。
  - GKE 版本为 `1.27.4-gke.900` 或更高版本（TPU 运行时指标支持所需）。
  - 集群上已启用 GKE 系统指标（Cloud Monitoring 消纳所需）。

### 第 2 步：监控 TPU 运行时指标 [低风险] [自动]

如果配置正确，以下指标将在 Cloud Monitoring 中可用（监控资源 `k8s_node` 和 `k8s_container`）：

- **容器指标**：
  - `kubernetes.io/container/accelerator/duty_cycle`：过去采样周期（60 秒）中，TensorCores 在 TPU 芯片上主动处理的时间百分比。
  - `kubernetes.io/container/accelerator/memory_used`：分配的加速器内存字节数。
  - `kubernetes.io/container/accelerator/memory_total`：加速器总内存字节数。
- **节点指标**：
  - `kubernetes.io/node/accelerator/duty_cycle`
  - `kubernetes.io/node/accelerator/memory_used`
  - `kubernetes.io/node/accelerator/memory_total`

### 第 3 步：检查节点状态条件 [低风险] [自动]

查询 GKE 节点的状态条件（GKE 版本 `1.32.1-gke.1357001` 或更高版本）。

- **PromQL 查询（检查特定节点是否就绪）**：
  ```promql
  kubernetes_io:node_status_condition{monitored_resource="k8s_node", cluster_name="{cluster_name}", node_name="{node_name}", condition="Ready", status="True"}
  ```
- **PromQL 查询（列出具有非就绪条件且为 True 的节点）**：
  ```promql
  kubernetes_io:node_status_condition{monitored_resource="k8s_node", cluster_name="{cluster_name}", condition!="Ready", status="True"}
  ```
- **PromQL 查询（列出未就绪的节点）**：
  ```promql
  kubernetes_io:node_status_condition{monitored_resource="k8s_node", cluster_name="{cluster_name}", condition="Ready", status="False"}
  ```
- **PromQL 查询（集群范围内的节点状态）**：
  ```promql
  avg by (condition,status)(avg_over_time(kubernetes_io:node_status_condition{monitored_resource="k8s_node"}[5m]))
  ```

### 第 4 步：检查节点池状态 [低风险] [自动]

查询多主机 TPU 节点池的状态。

- **PromQL 查询（验证特定节点池是否正在运行）**：
  ```promql
  kubernetes_io:node_pool_status{monitored_resource="k8s_node_pool", cluster_name="{cluster_name}", node_pool_name="{node_pool_name}", status="Running"}
  ```
- **PromQL 查询（按状态分组监控节点池）**：
  ```promql
  count by (status)(count_over_time(kubernetes_io:node_pool_status{monitored_resource="k8s_node_pool"}[5m]))
  ```
  _可能的状态_：`Provisioning`、`Running`、`Error`、`Reconciling`、`Stopping`。

### 第 5 步：检查节点池可用性 [低风险] [自动]

查询多主机 TPU 节点池中的所有节点是否可用。

- **PromQL 查询（检查可用性随时间变化）**：
  ```promql
  avg by (node_pool_name)(avg_over_time(kubernetes_io:node_pool_multi_host_available{monitored_resource="k8s_node_pool", cluster_name="{cluster_name}"}[5m]))
  ```
  _值_：`1`（True，所有节点可用）或 `0`（False，部分节点不可用）。

### 第 6 步：分析节点中断 [低风险] [自动]

查询 GKE 节点的中断次数。

- **PromQL 查询（中断和原因的分解）**：
  ```promql
  sum by (interruption_type,interruption_reason)(sum_over_time(kubernetes_io:node_interruption_count{monitored_resource="k8s_node"}[5m]))
  ```
  _中断类型_：`TerminationEvent`、`MaintenanceEvent`、`PreemptionEvent`。
  _中断原因_：`HostError`、`Eviction`、`AutoRepair`。
- **PromQL 查询（过滤主机维护事件）**：
  ```promql
  sum by (interruption_type,interruption_reason)(sum_over_time(kubernetes_io:node_interruption_count{monitored_resource="k8s_node", interruption_reason="HW/SW Maintenance"}[5m]))
  ```
- **PromQL 查询（按节点池聚合的中断计数）**：
  ```promql
  sum by (node_pool_name,interruption_type,interruption_reason)(sum_over_time(kubernetes_io:node_pool_interruption_count{monitored_resource="k8s_node_pool", interruption_reason="HW/SW Maintenance", node_pool_name="{node_pool_name}"}[5m]))
  ```

### 第 7 步：计算恢复和中断指标 [低风险] [自动]

计算过去 7 天的平均恢复时间（MTTR）和平均中断间隔时间（MTBI）。

- **PromQL 查询（MTTR - 平均恢复时间）**：
  ```promql
  sum(sum_over_time(kubernetes_io:node_pool_accelerator_times_to_recover_sum{monitored_resource="k8s_node_pool", cluster_name="{cluster_name}"}[7d])) / sum(sum_over_time(kubernetes_io:node_pool_accelerator_times_to_recover_count{monitored_resource="k8s_node_pool",cluster_name="{cluster_name}"}[7d]))
  ```
- **PromQL 查询（MTBI - 平均中断间隔时间）**：
  ```promql
  sum(count_over_time(kubernetes_io:node_memory_total_bytes{monitored_resource="k8s_node", node_name=~"gke-tpu.*|gk3-tpu.*", cluster_name="{cluster_name}"}[7d])) / sum(sum_over_time(kubernetes_io:node_interruption_count{monitored_resource="k8s_node", node_name=~"gke-tpu.*|gk3-tpu.*", cluster_name="{cluster_name}"}[7d]))
  ```

### 第 8 步：监控 TPU 主机指标 [低风险] [自动]

对于 GKE 版本 `1.28.1-gke.1066000` 或更高版本，监控 TPU 主机性能。

- **容器指标**：
  - `kubernetes.io/container/accelerator/tensorcore_utilization`：当前 TensorCore 的利用率百分比。
  - `kubernetes.io/container/accelerator/memory_bandwidth_utilization`：当前正在使用的加速器内存带宽百分比。
- **节点指标**：
  - `kubernetes.io/node/accelerator/tensorcore_utilization`
  - `kubernetes.io/node/accelerator/memory_bandwidth_utilization`
