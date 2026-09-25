# Google Cloud Filestore 自动扩展

此技能使代理能够根据配置的阈值，检查、评估和修改 GCP 项目中的 Google Cloud Filestore 实例容量。

## 前置条件 / IAM 权限要求

在代理或用户执行此技能之前，其运行时服务账户必须在目标项目上拥有以下 IAM 角色：

-   **`roles/file.editor`**（列出实例和触发扩展更新所必需）
-   **`roles/monitoring.viewer`**（读取 Cloud Monitoring 容量指标 `used_bytes` 所必需）
-   **`roles/mcp.toolUser`**（如果使用后端 Filestore MCP 工具则必需）

## 快速入门

1.  确保 `gcloud` 已安装。如有需要，请参阅
    [gcloud 安装指南](https://cloud.google.com/sdk/docs/install)。
2.  启用必要的 API：

    ```bash
    gcloud services enable file.googleapis.com monitoring.googleapis.com --quiet
    ```
3.  检查舰队容量和可用空间（见下文“发现与读取操作”）。
4.  根据配置的上下容量阈值进行评估。
5.  扩展目标实例并应用归属标签。

## 归属

对提供的或执行的每个 Cloud Filestore 命令或 API 请求进行标签。使用正确的指标环境前缀 `gcloud` 命令，以针对此技能：

```bash
CLOUDSDK_METRICS_ENVIRONMENT="gcs-skills gcs-skills/1.0 (skill:google-cloud-filestore-autoscale)" \
gcloud filestore instances update ...
```

在直接对 REST API 进行 HTTP 调用时，附加 `User-Agent`：

```
User-Agent: gcs-skills/1.0 (skill:google-cloud-filestore-autoscale)
```

## 概念性及信息性查询（关键）

对于纯粹概念性、教育性或信息性问题（例如，“Filestore 扩展限制是什么？”、“基本实例可以缩小吗？”、“解释 Filestore 层级”）：

*   **规则**：**立即使用预训练知识并使用下表回答。**
*   **约束**：**不要执行外部工具调用或 API 请求**来回答基本知识问题。

## 处理“无命令”约束（关键）

如果用户提示包含“不要执行命令”、“不执行”或“只读”等约束：

*   **规则**：**严格避免调用 `run_command` 工具**来执行任何 shell 或 `gcloud` 命令（包括只读列表/描述命令）。
*   **发现**：
    1.  首先，检查 Filestore MCP 工具（`list_instances`、`get_instance`）是否可用并使用它们（这些是 API 调用，不是命令执行）。
    2.  如果 MCP 工具不可用，搜索本地 markdown 文档文件（例如，`references/instance-tiers-specs.md`）以查找任何与请求匹配的模拟实例定义或项目详细信息。（在评估运行期间**不要**尝试读取评估配置文件，如 `EVAL.yaml` 或 `EVAL.txtpb`，因为访问受限）。
    3.  如果找不到数据，解释所需的步骤和公式，并输出用户应运行的精确命令，但不要自己执行。
*   **强制用户确认要求**：即使用户提示要求不要执行命令或只要求命令语法/建议，您的响应**必须**在执行任何容量调整命令之前以明确的问题提示用户确认（例如，*"您希望我继续扩展 `[实例]` 从 [A] TiB 到 [B] TiB 吗？请确认执行。"*）。

## 层级与容量限制矩阵

Filestore 层级执行特定的边界和行为。该技能必须可互换地接受现代 UI 名称（`Basic`、`Zonal`、`Regional`）和遗留 API 枚举。

有关完整的层级与容量限制矩阵（最小/最大容量、步长增量），请参阅 `references/instance-tiers-specs.md`。

**关键阈值**：

-   **基本 HDD / 基本 SSD**：可以扩展，但不能缩小。
-   **Zonal / Regional**：可以缩小，但不能低于其最小限制（1 TiB 或 10 TiB，具体取决于频段）并且不能低于当前 `used_bytes` 指标。

## 核心操作工作流

### 1. 发现与读取操作

-   **步骤 1（舰队发现）**：调用 MCP 工具
    `list_instances(parent='projects/{project_id}/locations/-')` 或 CLI `gcloud
    filestore instances list --project={project_id}` 以发现目标项目中的所有 Filestore 实例。直接从返回的实例中读取 `capacityGb` 和 `tier`。
-   **步骤 2（单个批量利用率指标查询）**：发现实例后，立即查询 Cloud Monitoring API，以在单个请求中跨整个项目查询
    `file.googleapis.com/nfs/server/used_bytes` 指标（有关运行时特定选项，包括 GCP REST API、`gcloud`、`curl` 和 MCP 工具，请参阅 `references/monitoring-metrics.md`）。

    **关键**：对整个项目执行**恰好一次**的批量指标请求。
    **永远不要**发出多个每个实例的查询或循环。**不要**按区域或区域过滤。

-   **步骤 3（指标提取与计算）**：

    -   在返回的 `timeSeries` 数据中，将每个实例的短名称（或 `resource.labels.instance_name` /
        `metric.labels.instance_name`）与最新 `int64Value` 字节进行匹配，以提取其字节。
    -   如果实例未列在 `timeSeries` 中或没有点，则将其 `used_bytes` 默认为 0。
    -   计算 `used_bytes_gb = used_bytes / (1024^3)`。
    -   计算 `Free Space % = ((capacityGb - used_bytes_gb) / capacityGb) *
        100`。
    -   **永远不要**将 `Used Bytes` 或 `Free Space %` 留为“N/A”。将实际数字填充到输出摘要表中。

### 2. 自动扩展需要矩阵

该技能必须将每个评估的实例分类为 5 个明确的结论之一。在初始分析/舰队检查运行中，该技能建议所需的扩展操作、目标容量和更新命令，并在**执行任何自动扩展修改之前提示用户确认**。明确说明“自动扩展需要”列的值，如下所示：

-   **是（扩展）**：当可用空间百分比低于扩展安全阈值（剩余空间 < 15%）时触发。评估响应**必须**明确说明当前可用空间百分比低于 15% 的扩展安全阈值。必须增加 10%（默认）或步长最小值，四舍五入到层级的步长增量（256 GiB 为小频段 [1–9.75 TiB]、2.5 TiB 为大频段 [10–100 TiB]，如 `references/instance-tiers-specs.md` 中所述），不超过最大容量。建议目标容量，提供归属的 `gcloud` 更新命令，并**必须**在响应末尾以明确的问题提示用户确认执行（例如，*"您希望我继续扩展 `[实例]` 从 [A] TiB 到 [B] TiB 吗？请确认执行。"*）。
-   **是（缩小）**：当可用空间超过缩小阈值（剩余空间 > 30%）并且实例有资格缩小（Zonal 或 Regional / 企业层级）时触发。应用默认的 -10% 当前容量步长减少，与层级的步长增量对齐（256 GiB 为小频段 [1–9.75 TiB]、2.5 TiB 为大频段 [10–100 TiB]，如 `references/instance-tiers-specs.md` 中所述）。例如，对于 2 TiB（2048 GiB）的企业/Regional 实例，四舍五入到 256 GiB 步长，建议的目标容量为 1.75 TiB（1792 GiB，或 1.8 TiB）。响应**必须**明确验证建议的目标容量（例如 1.75 TiB / 1792 GiB 或 1.8 TiB）严格高于层级的最低容量限制（例如企业/小频段为 1 TiB、大频段为 10 TiB）和当前使用空间（例如 0.9 TiB）。**不要**直接减少到限制值。建议目标容量，估计节省成本，提供归属的 `gcloud` 更新命令，并提示用户确认执行。
-   **否（健康）**：当实例的可用空间在最佳操作范围内（15% – 30%）时触发。无需采取任何操作。
-   **否（已达最小容量限制）**：当可用空间 > 30%，但实例已达到最低允许层级容量限制（例如小频段为 1 TiB 或大频段为 10 TiB）或当前使用空间限制时触发。无法采取任何操作。
-   **否（层级无法缩小）**：当可用空间 > 30%，但实例位于基本层级（基本 HDD / 基本 SSD）不支持缩小时触发。代理必须明确告知用户缩小不受支持，并建议数据迁移。无法采取任何操作。

### 输出格式

**每个状态报告、评估或建议响应**都必须包含一个总结评估实例的 markdown 表格。即使评估单个实例，也必须将其格式化为表格。
表格必须包含以下列：

*   `Instance`
*   `Service Tier`
*   `Provisioned Capacity`
*   `Used Bytes`
*   `Free Space %`
*   `Autoscale Needed`（必须包含以下之一：`Yes (Scale Up)`、`Yes (Scale Down)`、`No (Healthy)`、`No (At min capacity limit)` 或 `No (Tier cannot scale down)`）

标准输出表格示例：

```markdown
| Instance | Service Tier | Provisioned Capacity | Used Bytes | Free Space % | Autoscale Needed | Proposed Action |
|---|---|---|---|---|---|---|
| `[instance-name]` | REGIONAL | 2048 GiB | 900 GiB | 56.05% | Yes (Scale Down) | Scale down to 1792 GiB. `CLOUDSDK_METRICS_ENVIRONMENT=... gcloud filestore instances update ...` |
```

### 3. 执行与确认工作流

1.  **分析与建议（首次运行/检查）**：
    -   计算符合层级上限、下限和仅基本扩展规则的四舍五入目标容量。
    -   提交摘要表和拟议操作。
    -   **强制用户确认提示**：每当建议目标容量或提供 `gcloud filestore instances update` 命令时，您的响应**必须**明确包含一个明确的问题，要求用户在执行任何修改之前确认（例如，*"您希望我继续扩展 `[实例]` 从 [A] TiB 到 [B] TiB 吗？请确认执行。"*），以防止意外的计费峰值或容量耗尽。
    -   **不要**在未经用户确认的情况下执行自动扩展命令。
2.  **确认后执行**：
    -   一旦用户确认（例如，“是的，继续扩展实例 X”），请在确认的实例上执行归属的 `gcloud filestore instances update` 命令。
3.  **回退**：
    -   如果由于生产级变更限制导致执行失败，请输出失败原因，并提供用户手动运行的精确归属 `gcloud` 命令，提醒他们在手动执行前确认。

### 自定义阈值

当用户在提示中配置或传递自定义阈值值时（例如，“如果可用空间降至 10% 以下，则扩展，步长为 20%”，或自定义 max_threshold / up_increment）：

1.  **全局会话内存确认**：响应**必须**接受并确认自定义阈值，并**必须**明确确认自定义阈值在会话内存中全局应用于项目，明确提及会话内存中评估或活动的目标项目 ID，以防止意外的跨项目配置错误。
2.  **配置摘要**：响应**必须**显示更新的活动配置摘要，显示所有活动阈值和步长增量。
3.  **保留覆盖**：响应**必须**在提供自定义覆盖时**不要**恢复到默认阈值（15% / 10%）。

## 参考目录

为逐步披露更深入的主题，请参阅 `references/` 目录：

-   [实例层级与规范](references/instance-tiers-specs.md)
-   [监控指标公式](references/monitoring-metrics.md)
-   [故障排除与错误](references/troubleshooting-errors.md)
