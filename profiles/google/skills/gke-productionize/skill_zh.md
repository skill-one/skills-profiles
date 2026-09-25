# GKE 生产化技能

该技能作为高级协调器，用于准备 GKE 集群及其工作负载以供生产使用。

> [!IMPORTANT]
> 这是一个**元技能**或**协调器技能**。您需要调用并运行本文件中列出的许多其他专业技能，作为整体生产化过程的一部分。不要尝试直接在此技能中实现所有生产就绪功能；相反，使用此技能来评估环境，然后委托给每个领域的特定技能。

## 范围

该技能适用于：

-   单个应用程序（已在 Kubernetes 上或未在 Kubernetes 上）。
-   一组应用程序。
-   目标集群。

## 工作流程

### 1. 发现阶段

在提供建议之前，发现当前环境的状态。

#### 集群发现

运行以下命令以了解集群设置：

-   检查集群详细信息：`gcloud container clusters describe {cluster_name} --location {location} --project {project}`
-   检查 Autopilot 与标准：在描述输出中查找以下块：

    ```yaml
    autopilot:
      enabled: true
    ```
-   检查发布通道：查找 `releaseChannel`。

#### 工作负载发现

如果针对特定应用程序，发现其配置：

-   获取部署/StatefulSet 详细信息：`kubectl get deployment {app_name} -n {namespace} -o yaml`
-   检查专用命名空间和标签：`kubectl get namespace {namespace} -o yaml`（查找 Pod 安全标准标签）。
-   检查专用服务账户使用情况：`kubectl get pods -n {namespace} -o custom-columns="NAME:.metadata.name,SERVICE_ACCOUNT:.spec.serviceAccountName"`
-   检查资源请求和限制。
-   检查就绪、就绪和启动探针。
-   检查 HPA：`kubectl get hpa -n {namespace}`
-   检查 PDB：`kubectl get pdb -n {namespace}`
-   检查 NetworkPolicies：`kubectl get networkpolicy -n {namespace}`

### 2. 生产就绪评估

**在实施之前，您必须运行以下每个相关专业领域的技能，并将其指导纳入您的评估和计划中。否则，将导致非合规的生产配置。**

#### A. 应用程序引导（预 Kubernetes）

如果应用程序尚未在 GKE 上运行，您必须运行 `gke-app-onboarding` 技能，用于规划容器化、镜像构建和基本部署。

#### B. 可扩展性与资源管理

确保工作负载具有适当的资源和自动扩展。

-   **操作**：您必须运行 `gke-workload-scaling` 技能来配置 HPA、VPA 和资源限制。

#### C. 可观察性

确保已实施充分的日志记录和监控。

-   **操作**：您必须运行 `gke-observability` 技能来设置 Cloud Logging、Monitoring 和 Managed Prometheus。

#### D. 可靠性

确保高可用性和优雅降级。

-   **操作**：您必须运行 `gke-reliability` 技能来配置区域集群、PDB 和健康探针。

#### E. 安全性

强化集群和工作负载。

-   **操作**：您必须运行 `gke-platform-security` 和 `gke-workload-security` 技能，用于 Workload Identity、Network Policies 和 Shielded Nodes。
-   **命名空间隔离**：确保工作负载在专用命名空间中运行，并通过标签强制执行 Pod 安全标准 (PSS)。
-   **最小权限**：确保工作负载使用专用 ServiceAccounts 而不是 `default` ServiceAccount。

#### F. 备份与灾难恢复

确保有状态数据得到保护。

-   **操作**：您必须运行 `gke-backup-dr` 技能来配置 GKE 的备份和恢复程序。

#### G. 边缘安全与入站

保护外部访问。

-   **操作**：您必须运行 `gke-service-networking` 技能，用于 Gateway API、Ingress 和 Cloud Armor。

#### H. 成本优化

确保资源的有效使用。

-   **操作**：您必须运行 `gke-cost-optimization` 技能，用于右键单击、配额和 Spot VMs 的策略。

#### I. 升级与维护姿态

确保安全、可预测的升级姿态。

-   **操作**：您必须运行 `gke-upgrades` 技能，用于发布通道选择、维护窗口/排除和节点池升级策略。

#### J. Golden Path 默认值审计

确保集群配置与推荐默认值匹配。

-   **操作**：您必须运行 `gke-golden-path` 技能，以将集群与 Golden Path 默认值进行比较，并报告偏差及其严重性和修复建议。

### 3. 生产就绪评分

在评估后，提供一份摘要报告，每个领域提供 RAG（红色、黄色、绿色）状态和整体就绪分数。这有助于优先处理修复工作。

以确定性的方式应用此评分标准，以便对相同环境进行重复评估产生相同的结果：

1.  **每个领域的标准**：对于每个评估领域（A-J），列出执行的具体检查（来自领域技能的指导），并将每个检查分类为 **通过**、**失败-关键**（生产阻塞，例如，没有资源请求、没有状态数据的备份、在受限制环境中公共控制平面）或 **失败-次要**（改进，例如，缺少 VPA 建议没有 Spot 使用用于批处理）。
2.  **RAG 映射（每个领域）**：
    -   **红色** = 一个或多个失败-关键检查。
    -   **黄色** = 没有失败-关键，但一个或多个失败-次要检查。
    -   **绿色** = 所有检查通过。
3.  **领域分数**：绿色 = 100，黄色 = 50，红色 = 0。
4.  **加权总分**：将安全性、可靠性和备份/灾难恢复的权重设为 2x；所有其他评估领域的权重设为 1x。总分 = (领域分数 x 权重之和) / (权重之和)，四舍五入到最接近的整数。从两个和中排除不适用（例如，完全无状态工作负载的备份/灾难恢复）的领域，并注明排除情况。
5.  **就绪判定**：≥ 90 且没有红色领域 = "生产就绪"；70-89 且没有红色领域 = "需要后续处理"；其他情况 = "未就绪生产"。

在报告中显示每个领域的检查列表、RAG 状态、权重和计算出的总分。

## 适应性指南

-   **单个应用程序**：关注健康探针、HPA、资源限制、PDB 和特定应用程序的 Workload Identity。
-   **集群范围**：关注集群自动扩展器、多区域设置、发布通道、维护窗口和默认 Network Policies。
-   **主动执行**：主动执行相关技能（例如，可观察性、安全性、可扩展性、可靠性），以评估并提出改进建议，在应用状态更改实现之前寻求用户确认。
