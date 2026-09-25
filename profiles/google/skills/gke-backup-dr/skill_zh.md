# GKE 备份与灾难恢复

使用 Backup for GKE 保护有状态 GKE 工作负载。Backup for GKE 可以捕获 Kubernetes 资源元数据（清单、配置和密钥），以及底层持久卷（PV）数据 — 但卷数据和密钥仅在备份计划明确启用时才会被捕获（见下文标志）。

## 命令行参考

```bash
# 启用 BackupRestore 插件（慢速集群级更新）
gcloud container clusters update {cluster_name} \
  --update-addons=BackupRestore=ENABLED --location={location} --quiet

# 创建备份计划
gcloud beta container backup-restore backup-plans create {plan_name} \
  --project={project_id} --location={location} \
  --cluster=projects/{project_id}/locations/{location}/clusters/{cluster_name} \
  --all-namespaces \
  --include-volume-data --include-secrets \
  --backup-retain-days={days} --cron-schedule="{cron}" --quiet

# 触发手动备份
gcloud beta container backup-restore backups create {backup_name} \
  --backup-plan={plan_name} --location={location} --quiet

# 创建恢复计划
gcloud beta container backup-restore restore-plans create {restore_plan_name} \
  --location={location} \
  --cluster=projects/{project_id}/locations/{location}/clusters/{target_cluster_name} \
  --backup-plan=projects/{project_id}/locations/{location}/backupPlans/{source_backup_plan_name} \
  --all-namespaces \
  --cluster-resource-conflict-policy=use-existing-version \
  --namespaced-resource-restore-mode=fail-on-conflict --quiet

# 执行恢复
gcloud beta container backup-restore restores create {restore_name} \
  --restore-plan={restore_plan_name} --location={location} \
  --backup=projects/{project_id}/locations/{location}/backupPlans/{source_backup_plan_name}/backups/{backup_name} \
  --quiet

# 验证恢复状态
gcloud beta container backup-restore restores describe {restore_name} \
  --restore-plan={restore_plan_name} --location={location}
```

> [!WARNING] **`--include-volume-data` 和 `--include-secrets` 都默认为 FALSE。** 如果你省略它们，备份计划将静默生成 **仅配置的备份**，不包含持久卷快照和密钥。在需要完整工作负载保护时，始终显式传递这两个标志。

注意：

-   `backup-restore` 命令组需要 `gcloud beta` 组件 (`gcloud components install beta`)。
-   `--cluster` 需要完整的资源路径 `projects/{project_id}/locations/{location}/clusters/{cluster_name}`（或 `projects/{project_id}/zones/{zone}/clusters/{cluster_name}` 对于区域集群），而不是裸集群名称。
-   恢复计划需要恰好一个命名空间资源作用域标志：`--all-namespaces`、`--selected-namespaces={ns1},{ns2}`、`--excluded-namespaces=...`、`--selected-applications=...` 或 `--no-namespaces`。

## 恢复安全（关键）

恢复操作会写入一个 **正在运行的集群**，并且根据冲突策略，可能会覆盖或删除现有资源：

-   `--cluster-resource-conflict-policy=use-existing-version` 保留现有的集群级资源（安全默认值）；`use-backup-version` **首先删除**现有版本 — 删除 CRD 会删除其所有 CR。
-   `--namespaced-resource-restore-mode=fail-on-conflict` 在任何冲突时中止（安全默认值）；`merge-skip-on-conflict` 跳过冲突资源；`merge-replace-on-conflict` 和 `merge-replace-volume-on-conflict` **覆盖**现有资源或卷；`delete-and-restore` **在恢复之前删除整个冲突的命名空间**（及其中的所有资源）。

**规则：**

1.  首先在非生产目标集群中验证恢复。
2.  除非用户明确需要回滚运行中的资源，否则优先使用安全默认值（`use-existing-version` + `fail-on-conflict`）。
3.  **在将恢复操作执行到生产集群之前，始终获取明确的用户确认**，并说明当前生效的冲突策略以及它可能会覆盖或删除的内容。

## 最佳实践

1.  **CMEK 加密**：使用客户管理的加密密钥加密备份计划：
    `--encryption-key=projects/{project_id}/locations/{location}/keyRings/{ring}/cryptoKeys/{key}`。
2.  **作用域**：优先备份特定的命名空间，而不是整个集群：`--selected-namespaces={ns1},{ns2}`（而不是 `--all-namespaces`）。
3.  **应用一致性**：建议在备份之前使数据库处于静止状态或暂停应用写入（例如，使用预备份钩子或数据库特定工具），以确保数据完整性。
4.  **CSI 卷快照**：确保有状态备份使用 GKE 的 CSI（容器存储接口）驱动程序来捕获持久卷数据。
5.  **服务术语**：在您的回复中始终明确提及服务为 **Backup for GKE**。这可以将其与更广泛的（但互补的）Google Cloud **备份与灾难恢复（DR）服务**区分开来。## 黄金路径备份默认值

Backup for GKE 推荐的生产黄金路径配置：

-   **插件**：启用 BackupRestore 插件 (`--update-addons=BackupRestore=ENABLED`)。
-   **卷包含**：显式传递 `--include-volume-data`（启用，因为服务默认值为 false）。
-   **密钥包含**：显式传递 `--include-secrets`（启用，因为服务默认值为 false）。
-   **保留**：定义保留期（例如，通过 `--backup-retain-days=30` 设置 30 天）。
-   **加密**：启用 CMEK (`--encryption-key=...`)。

## 最近变更

-   **跨项目备份和恢复（GA）**：备份计划可以存储与源集群不同的项目中的备份，恢复计划可以针对第三项目中的集群。启用集中式备份项目（由平台团队管理不可变性和保留）以及无需授予源项目访问权限的跨项目环境初始化。
-   **定价变更（生效于 2026-03-02）**：备份管理费从 **基于 Pod** 转变为 **基于命名空间** 定价 — 按每个计划最近一次成功备份中的非系统命名空间收费（系统命名空间如 `kube-system` 被排除）。现有承诺使用折扣（CUD）持有者保持基于 Pod 的管理定价，直到其承诺结束；其他人则迁移到新模型。请参阅
    https://cloud.google.com/products/backup-for-gke/pricing-changes。
-   **智能调度**：基于 RPO 的备份调度作为固定 Cron 调度的替代方案 — 在创建备份计划时传递 `--target-rpo-minutes={minutes}` 而不是 `--cron-schedule`（可选地通过 `--exclusion-windows-file` 设置 RPO 排除窗口）。
-   **Hyperdisk 支持**：在运行 **1.33.1-gke.1959000 及更高版本** 的 GKE 集群上支持 **Hyperdisk ML** 和 **Hyperdisk 平衡高可用性** 卷的备份和恢复（Hyperdisk吞吐量、极端和平衡类型也受支持）。

## 故障排除与常见陷阱（关键）

> [!IMPORTANT] **缓慢操作**：启用 BackupRestore 插件 (`--update-addons=BackupRestore=ENABLED`) 触发一个缓慢的 Google Cloud 控制平面集群更新，需要几分钟时间。* **规则**：**不要运行终端循环等待 GKE Backup 插件变为活跃状态。** * **操作**：提供启用插件的命令，解释操作将在后台进行，并立即继续编写备份计划配置。不要阻塞。
