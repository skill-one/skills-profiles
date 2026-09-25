# GKE TPU 动态切片监控与管理

监控 TPU 切片自定义资源的状态，排查配置失败问题，验证动态切片上的工作负载清单，并执行清理操作。

## 前置条件

-   项目已启用 Cloud Logging。
-   已配置 `kubectl` 和 `gcloud` 命令行工具以访问 GKE 集群。

## 诊断工作流

### 第 0 步：上下文获取与时间窗口定义

使用集群工具或以下参数收集项目、集群和切片上下文：

-   **项目 ID**：`{project_id}`（例如，`my-gcp-project`）
-   **集群名称**：`{cluster_name}`（例如，`tpu-cluster`）
-   **区域/区域**：`{location}`（例如，`us-central1-a`）
-   **切片名称**：`{slice_name}`（例如，`test-slice`）
-   **问题时间**：`{timestamp}`（可选；默认为最后 30 分钟窗口 `[T - 30m]` 到 `[T + 30m]`）

--------------------------------------------------------------------------------

### 第 1 步：描述切片自定义资源 [低风险]

当需要检查、排查或检查切片状态时，立即使用可用的集群工具执行 `kubectl describe slice {slice_name}` 进行检查。将生成的 `Status.Conditions` 输出与下表中的条件进行解析，以诊断确切状态并提供具体建议。

-   **命令**：

    ```bash
    kubectl describe slice {slice_name}
    ```

#### 状态与原因分析

分析 `Status.Conditions`（尤其是 `Type: Ready` 及其 `Reason` 和 `Status`）：

| 生命周期状态 / 原因 | 含义 | 推荐操作 |
| :--- | :--- | :--- |
| **`SliceNotCreated`** | GKE 切片控制器正在初始化切片并执行资源检查。 | 等待几分钟并重新检查切片状态。 |
| **`SliceCreationFailed`** | 前置条件验证失败（例如，选择的节点不存在、节点已被其他切片使用，或拓扑结构与分区数量不匹配）。 | 验证所选节点是否存在、未分配，且拓扑结构与分区数量匹配。 |
| **`ACTIVATING`** | GKE 正在积极形成和配置 TPU 切片。 | 监控节点配置过程。 |
| **`ACTIVE`** | TPU 切片已成功形成并准备好承载工作负载。 | 继续部署或检查工作负载。 |
| **`ACTIVE_DEGRADED`** | 切片可用，但一个或多个子块已降级。 | 监控工作负载日志中的互连或设备错误。检查有故障的节点虚拟机。 |
| **`FAILED`** | GKE 无法形成 TPU 切片（例如，所选节点不属于同一预留块）。 | 确保所有所选节点都属于同一预留块。 |
| **`DEACTIVATING`** | 切片正在拆除（由用户删除或关键系统故障触发）。 | 等待拆除完成，或如果卡住则修补 finalizers。 |
| **`INCOMPLETE`** | 切片 CR 删除前的最终阶段。 | 无需操作；资源将很快被移除。 |

#### 配置失败排查清单

在调查切片创建或配置失败（`SliceCreationFailed` 或 `FAILED`）时，执行以下验证步骤：

1. **节点存在与分配检查**：验证集群中是否存在所选的 TPU 节点，且未被其他切片分配（`kubectl get nodes -l cloud.google.com/gke-tpu-slice`，`kubectl get slice -A`）。
2. **拓扑对齐**：确认分区数量与请求的拓扑维度匹配（例如，拓扑 `2x2` 需要 4 个节点）。
3. **预留块对齐检查**：确认所有所选 TPU 节点都属于同一预留和预留块。

--------------------------------------------------------------------------------

### 第 2 步：验证工作负载规范 [低风险]

确保工作负载清单正确配置以目标动态切片。

#### 1. 单切片工作负载要求

检查 Pod 模板是否包含以下注解和选择器：

-   **注解**：
    -   `cloud.google.com/gke-tpu-slice-topology: "{topology}"`（例如，
        `"4x4x4"`)
-   **NodeSelector**：
    -   `cloud.google.com/gke-tpu-topology: "{topology}"`（例如，`"4x4x4"`)
    -   `cloud.google.com/gke-tpu-accelerator: "{accelerator_type}"`（例如，
        `"tpu7x"`)
    -   `cloud.google.com/gke-tpu-slice: "{slice_name}"`（例如，`"test-slice"`）

#### 2. 多切片（JobSet）工作负载要求

如果部署多切片 JobSet，请验证：

-   **JobSet 注解**：
    -   `alpha.jobset.sigs.k8s.io/exclusive-topology:
        cloud.google.com/gke-tpu-slice`
-   **Pod 模板注解**：
    -   `cloud.google.com/gke-tpu-slice-topology: "{topology}"`
-   **Pod 模板 NodeSelector**：
    -   `cloud.google.com/gke-tpu-topology: "{topology}"`
    -   `cloud.google.com/gke-tpu-accelerator: "{accelerator_type}"`
    -   *注意：不要手动在 nodeSelector 中指定 `cloud.google.com/gke-tpu-slice`；JobSet 会自动处理切片分配。*

--------------------------------------------------------------------------------

## 解决方案与管理工作流

### 解决方案 1：强制删除卡住的切片 [高风险]

如果切片卡在 `DEACTIVATING` 或由于 stuck finalizers 导致删除无限期挂起：

1. **识别原因**：解释切片资源上的 finalizers（`metadata.finalizers`）阻止 Kubernetes 完成资源删除。
2. **提出解决方案**：建议使用 JSON 补丁操作从元数据路径（`/metadata/finalizers`）中删除 finalizers：

    ```bash
    kubectl patch slice {slice_name} --type json -p='[{"op": "remove", "path": "/metadata/finalizers"}]'
    ```
3. **提供警告**：明确警告用户删除 finalizers 会绕过标准控制器拆除，可能导致底层虚拟机、网络或加速器资源未清理或遗留。
4. **关键安全指令**：响应必须明确要求用户确认（例如，*"通过 JSON 补丁删除 `/metadata/finalizers` 是高风险操作，可能会遗留未清理或遗留的资源。您确认要应用此补丁到切片 `{slice_name}` 吗？*"），并在应用或执行补丁前暂停等待用户确认。

--------------------------------------------------------------------------------

### 解决方案 2：禁用并清理切片控制器 [高风险]

如果需要禁用动态切片：

1.  **检查现有切片**：

    ```bash
    kubectl get slice -A
    ```
    确保所有切片都已删除后再禁用控制器。

2.  **通过 gcloud 禁用切片控制器**：

    ```bash
    gcloud container clusters update {cluster_name} \
        --location={location} \
        --no-enable-slice-controller
    ```
3.  **删除切片 CRD**：

    ```bash
    kubectl delete crd slices.accelerator.gke.io
    ```
4.  **清理节点标签**：从集群中所有节点移除 GKE TPU 切片标签：

    ```bash
    kubectl label nodes --all cloud.google.com/gke-tpu-slice- cloud.google.com/gke-tpu-slice-topology-
    ```
-   **安全规则**：提出确切命令并在执行禁用或破坏性清理步骤前确认。
