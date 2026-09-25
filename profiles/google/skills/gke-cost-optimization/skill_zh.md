# GKE 成本优化

本指南涵盖降低 Google Kubernetes Engine (GKE) 成本，同时保持安全可靠态势的策略和工作流程。

## 工作流程与优化策略

### 1. 前置条件：成本分配与监控

为跨命名空间和标签进行计费跟踪启用 GKE 成本分配 (`--enable-cost-allocation`)，检查实时集群利用率 (`kubectl top`)，或在 BigQuery (`bq`) 中运行历史成本分解查询，请使用 **`gke-cost-analysis`** 技能。一旦跟踪激活并诊断出浪费，请应用以下优化工作流程。

### 2. 配置资源配额

资源配额限制多租户集群中租户的资源消耗总量，防止成本失控。模板：[assets/resource-quota-example.yaml](assets/resource-quota-example.yaml)（设置命名空间 + `hard` 限制，然后 `kubectl apply -f`）。

### 3. Pod 资源调整（VPA & MPA）

调整 Pod 资源请求以匹配实际利用率。过度配置的请求是最大的浪费来源之一。

-   **使用推荐模式下的 VPA** (`updateMode: "Off"` — 推荐但不驱逐）：

```bash
# 1. 以推荐模式部署 VPA（模板：assets/vpa-recommendation-mode.yaml）
kubectl apply -f assets/vpa-recommendation-mode.yaml
# 2. 等待 24+ 小时收集数据，然后读取推荐结果
kubectl get vpa {deployment_name}-vpa -o jsonpath='{.status.recommendation}'
```

-   **优化规则：**

条件                     | 操作                             | 节省程度
----------------------------- | ---------------------------------- | -------
CPU 请求 >5x P95 实际值    | 调整为 `P95 * 1.2`              | 高
内存请求 >3x P95 实际值    | 调整为 `P95 * 1.2`              | 高
CPU 请求 >2x P95 实际值    | 调整为 `P95 * 1.2`              | 中
未设置资源请求            | 添加请求（启用 bin-packing）      | 中

-   **使用 MPA**：在水平扩展和垂直扩展时，同步协调 HPA 和 VPA 推荐结果，以避免冲突的扩展事件。
-   **查看成本推荐**：在 Google Cloud Console (`成本管理` > `GKE 成本优化`) 中检查内置的 Pod 资源调整建议。

### 4. 通过 ComputeClasses 和 NodeSelector 使用 Spot VM

为容错型工作负载使用 Spot VM，可降低 60-90% 的成本。

#### 4.1 ComputeClass 配置

对于具有按需回退的 Spot 优先 ComputeClass（优先级排序，`activeMigration`，机器家族选择），请使用 **`gke-compute-classes`** 技能 — ComputeClass YAML 生成和优先级配置是其领域，而非本技能的范畴。

#### 4.2 直接选择工作负载的 Spot 容量 (`nodeSelector`)

对于 GKE Autopilot 中的无状态或批处理工作负载，使用 `nodeSelector` 直接目标 Spot 容量：

> [!WARNING] **抢占警告**：Spot VM 可随时被抢占，并会提前 30 秒通知。工作负载必须容错，并至少运行 2 个副本以实现高可用性。在推荐 Spot VM 时，始终明确告知用户此抢占风险。

精确的 Pod 级别选择器为：

```yaml
nodeSelector:
  cloud.google.com/gke-spot: "true"
```

完整的示例 Deployment（副本 >= 2，`terminationGracePeriodSeconds: 25`，`preStop` 钩子）：[assets/spot-deployment-example.yaml](assets/spot-deployment-example.yaml)。

**适合使用 Spot 的工作负载：**

工作负载                          | 是否适合使用 Spot?
--------------------------------- | ---------------
批处理 / 数据处理           | 是
开发 / 测试环境           | 是
无状态 Web/API（副本 >= 2） | 是（配合 PDB）
带检查点的工作负载           | 是
有状态工作负载（数据库）    | 否
单副本关键服务            | 否

### 5. 机器类型选择

在选择节点形状或配置 ComputeClasses 时：

| 家族        | 用例                                          | 相对成本 |
| ------------- | ------------------------------------------------- | ------------- |
| e2            | 通用型，突发型                              | 最低        |
| t2a / t2d     | 水平扩展（Arm/AMD），优化性价比  | 低           |
| n4a           | 基于Axion Arm，通用型性价比                | 低          |
| n4 / n4d      | 通用型（Intel/AMD），灵活形状      | 低-Medium    |
| c4a           | 基于Axion Arm，通用型，高效率            | Medium        |
| c3 / c4       | 计算优化型（Intel）                         | Medium-High   |
| c3d / c4d     | 计算优化型（AMD），高吞吐量          | Medium-High   |
| ek-standard   | Autopilot 增强                                | Medium        |
| m3 / x4       | 内存优化型，SAP HANA，大型数据库       | High          |
| g2 (L4 GPU)   | AI 推理                                      | High          |
| a3 (H100 GPU) | AI 训练                                       | Highest       |
| a4 / a4x      | 超级扩展 AI（Blackwell GPU）                   | Highest       |

### 6. 承诺使用折扣 (CUDs)

对于具有可预测基线使用量的稳态工作负载，购买 1 年或 3 年 CUDs：

-   **基于资源的 CUDs**（承诺到机器家族/区域）：1 年约 30% 以上折扣，3 年约 55%（因机器家族而异）。
-   **灵活 CUDs**（基于消费，跨家族/区域可移植）：较低折扣（1 年约 28%，3 年约 46%）以换取灵活性。
-   **Autopilot**：Autopilot 特定 CUDs 于 2026 年 1 月停止 — 新的承诺覆盖 Autopilot 使用的是基于消费的 Compute 灵活 CUDs（现有的 Autopilot CUDs 承诺将在其期限届满时到期）。
-   自动应用于匹配的区域使用量。
-   通过 Google Cloud Console > 计费 > 承诺使用折扣购买。

**仅根据稳态基线大小调整承诺。** 无论是否使用，承诺都会按完整期限计费，因此过度承诺到峰值使用会将折扣转化为浪费。测量实际使用量的底部值（在代表性时间段内），承诺该值，并用本技能中已有的弹性选项覆盖超出部分：

-   **基线**（始终运行）→ 基于资源的 CUDs。
-   **可变 / 爆发型** → 在按需容量上使用自动扩展。
-   **可中断型**（批处理，CI，无状态工作负载）→ Spot VM，可与自动扩展堆叠，无需承诺。

在推荐 CUDs 时，明确说明分割比例，而不是暗示整个占用都应该承诺。

### 7. 集群管理与多租户

-   **空闲的开发集群**：GKE 没有停止/启动操作，集群管理费只要集群存在就会累积。为降低空闲成本，将节点池缩放到零 (`gcloud container clusters resize {cluster_name} --node-pool {pool_name} --num-nodes 0`) 或通过 IaC（Terraform/Config Connector）删除并重新创建集群。
-   **调整标准节点池大小**：使用 Cluster Autoscaler 并设置适当的 min/max 限制。
-   **使用廉价的预热空间替代过度配置的节点**：预初始化节点保持挂起状态的缓冲区（预览版，GKE 1.36.0-gke.2253000+）— 您只需支付磁盘 + IP，而不是完整节点价格，恢复时间约 30 秒。参见 **`gke-cluster-autoscaler`** 技能。
-   **多租户整合**：使用命名空间和 ResourceQuotas 将单个集群跨多个工程团队共享，而不是为每个团队维护集群。

## 成本与利用率监控

为检查实时节点/Pod 利用率 (`kubectl top nodes/pods`)，查看集群成本预算 (`gcloud billing budgets list`)，或在 BigQuery (`bq query`) 中查询详细计费报告，请参考 **`gke-cost-analysis`** 技能。
