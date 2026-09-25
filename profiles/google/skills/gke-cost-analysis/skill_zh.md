# GKE 成本分析

此技能提供关于 GKE 相关成本、账单报告和利用率分析的问答指导。

## 概述

当用户询问 GKE 成本相关问题时（例如，“我的跨项目成本是多少？”“我最昂贵的命名空间是什么？”“我的集群成本为何飙升？”），使用此技能通过 BigQuery 账单导出、成本分配元数据和实时集群指标提供结构化且专业的回答。

## 指令

处理成本相关问题时：

1.  **提供直接答案**：清晰简洁地回答具体的成本问题或分析请求。
2.  **解释 BigQuery 集成**：解释如何查询 BigQuery 获取历史成本明细。注意 GKE 成本来自 GCP 账单详细 BigQuery 导出（`gcp_billing_export_resource_v1_*`）。
3.  **检查并验证成本分配**：解释必须在集群上启用 GKE 成本分配（`--enable-cost-allocation`）以实现命名空间、标签和工作负载级别的账单粒度。如果查询返回空标签，请提供启用它的 `gcloud` 命令。
4.  **分析定价驱动因素与利用率**：在诊断成本驱动因素时，解释集群是处于 Autopilot（按请求的 Pod CPU/内存计费）还是 Standard 模式（按底层 VM 节点大小+控制平面费用计费），并比较实时利用率（`kubectl top`）与已请求的请求。
5.  **提供可操作的命令/查询**：提供具体的 BigQuery CLI（`bq query`）命令或只读的 `gcloud`/`kubectl` 检查命令。在可用时优先选择 `bq` 而不是 BigQuery Studio。

## 关键点与定价驱动因素

-   **数据源**：GKE 成本来自 GCP 账单详细 BigQuery 导出。用户必须提供其 BigQuery 表的完整路径（包含账单账户 ID 的数据集名称和表名称）。
-   **粒度要求**：必须在集群上启用 GKE 成本分配（`--enable-cost-allocation`）以在 BigQuery 中填充 `goog-k8s-cluster-name`、`k8s-namespace`、`k8s-workload-name` 和 `k8s-workload-type` 标签。
-   **Autopilot 与 Standard 成本驱动因素**：
    -   **Autopilot 定价**：直接按 Pod 资源请求（`requests.cpu`、`requests.memory`、临时存储）计费。无论 Pod 是否实际使用这些 CPU 周期或内存，请求过量的 Pod 都会推高账单。
    -   **Standard 定价**：按已配置的节点池 VM（`e2`、`n4`、`c3` 等）计费。空闲节点或多个低利用率开发集群会导致额外的基础设施成本。
    -   **集群管理费**：每个集群每小时约 0.10 美元，适用于 Standard 和 Autopilot 模式。免费套餐为每个账单账户的一个符合条件的集群豁免此费用。
-   **积分与折扣影响**：在分析 `cost` 与 `cost_before_credits` 时，注意承诺使用折扣（CUDs）和 Spot VM 会以积分或降低费率的形式出现在账单导出中。
-   **工具与语法**：优先使用 BigQuery CLI（`bq`）。编写 Standard SQL 查询时，使用点（`.`）而不是冒号（`:`）来分隔项目 ID 和数据集名称（`{project_id}.{dataset_name}.{table_name}`）。
-   **默认值**：除非另有说明，否则假设最后 30 天，行限制为 10，按成本降序排序（`ORDER BY cost DESC`）。

## 实时集群与成本监控

使用只读 CLI 命令检查当前集群预算、节点利用率和 Pod 资源消耗与请求：

```bash
# 查看账户的账单预算（需要成本管理 API）
gcloud billing budgets list --billing-account={billing_account} --quiet

# 查看集群的实时节点资源利用率
kubectl top nodes

# 查看命名空间中的 Pod 资源使用情况（与请求限制比较以诊断浪费）
kubectl top pods --all-namespaces --containers
```

> **警告 — 集群修改，非只读**：启用 GKE 成本分配会修改集群。在运行前获取用户的明确确认，并注意命名空间/工作负载标签仅在启用后才会填充到账单导出中（无历史回填）。
>
> ```bash
> gcloud container clusters update {cluster_name} \
>     --enable-cost-allocation \
>     --region {region}
> ```

## 应用成本优化

根据分析结果应用调整大小更改（例如设置 `VPA` 推荐模式、将 CPU/内存调整为 `P95 * 1.2`、通过 `nodeSelector` 或 `ComputeClass` 配置 Spot VM、强制执行 `ResourceQuotas` 或选择机器类型和 CUDs），使用 **`gke-cost-optimization`** 技能。

## BigQuery 查询模板

准备好的 `bq query` 模板——单个工作负载成本、每个工作负载每个集群的分解、每个命名空间的分解——带有占位符策略和默认值（30 天、`LIMIT 10`、`ORDER BY cost DESC`）位于 [references/billing-queries.md](references/billing-queries.md)。所有参数（数据集、表、项目、集群等）都必须替换为用户值。

注意：检查 `goog-k8s-cluster-name` 标签是否存在将总账单数据专门限制为 GKE 成本。
