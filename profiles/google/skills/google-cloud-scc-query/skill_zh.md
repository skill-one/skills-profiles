# Google Cloud Security Command Center 查询技能

提供查询和检索 Google Cloud Security Command Center 中的安全发现、外部暴露、有毒组合、漏洞、威胁和敏感数据风险等信息的 `gcloud` CLI 命令指南，仅限于只读模式。

> [!IMPORTANT] 不存在 `gcloud scc findings describe` 命令（无效选项：'describe'）。若要按名称检索特定发现的详细信息，始终使用带 `name` 过滤条件的 `gcloud scc findings list` 命令。

--------------------------------------------------------------------------------

## 核心执行规则

1.  **只读 & 无推测 (父级范围必需)**：所有执行操作必须严格保持只读模式。每个 `gcloud scc findings list` 或 `group` 命令都严格要求显式指定 `{parent}` 范围 (`organizations/{id}`, `projects/{id}` 或 `folders/{id}`)。如果提示中缺少父级范围且无法从完整的发现名称中推断，**请勿执行任何 `gcloud` 命令**（不要在没有父级的情况下执行查询，且永远不要检查 `gcloud config`）。在执行命令前立即停止并要求用户提供父级资源范围。
2.  **有界执行 & 无失控循环**：
    -   限制工具调用仅限于完成查询所必需的操作（直接查询通常只需 1 次调用，列表→深入分析工作流通常需要 2 次调用）。
    -   如果命令因权限/认证错误失败，或特定发现查询返回 `[]`，立即停止。不要尝试使用不同的标志进行盲目的暴力重试，且永远不要在本地工作区搜索凭证。
3.  **错误时立即停止**：如果任何命令因 `PERMISSION_DENIED`、`IAM_PERMISSION_DENIED`、凭证过期或网络超时而失败，立即停止并报告原始错误消息。不要在工作区搜索凭证或运行诊断循环。
4.  **模糊或多个发现**：当请求单个发现报告时提供多个发现名称，或列表返回多个发现时，不要调查所有发现或单方面选择一个。立即停止而不运行查询，并要求用户明确他们想要获取详细信息的具体发现名称。如果查询返回零个发现，立即报告不存在活动发现并停止。
5.  **不要查询攻击路径资源**：仅分析 Security Command Center 发现 JSON 有效负载中的数据。不要运行命令来描述、验证或查询底层 Google Cloud 资源（例如 VM、Cloud Storage 桶、服务账户或 IAM 策略）。
6.  **父级范围解析**：
    -   对于列表和分组，将父级资源路径格式化为 `organizations/{org_id}`、`projects/{project_id}` 或 `folders/{folder_id}`。
    -   对于特定发现名称的深入分析查询，提取 `/sources/...` 之前的 `{parent}` 资源前缀：
        -   `organizations/{org_id}/sources/...` → `{parent}` 是 `organizations/{org_id}`
        -   `folders/{folder_id}/sources/...` → `{parent}` 是 `folders/{folder_id}`
        -   `projects/{project_id}/sources/...` → `{parent}` 是 `projects/{project_id}` 无论发现资源名称是全局（4段）还是位置限定（5段，带 `/locations/{location}/`），都提取父级前缀。使用提取的 `{parent}` 执行深入分析查询。不要拒绝或停止项目级或文件夹级发现。

--------------------------------------------------------------------------------

## 数据驻留与区域端点

当数据驻留（DRZ）启用时，发现仅在其指定的区域位置（`us`、`eu` 或 `me-central2`）存储和可访问。跨不同位置的查询不会返回其他区域的发现。

### 1. 位置参数化

所有 `gcloud scc findings` 命令都要求通过 `--location={location}` 指定目标位置：

-   **默认**：`global`（数据驻留未启用或用于全局发现时使用）。
-   **支持的区域位置**：
    -   `us`（美国多区域）
    -   `eu`（欧盟多区域）
    -   `me-central2`（沙特阿拉伯王国区域位置）

### 2. API 端点覆盖

当区域位置（`us`、`eu` 或 `me-central2`）的组织启用数据驻留（DRZ）时，在执行发现查询之前配置区域 API 端点覆盖：

```bash
gcloud config set api_endpoint_overrides/securitycenter https://securitycenter.{LOCATION}.rep.googleapis.com/
```

欧盟（`eu`）区域的示例：

```bash
gcloud config set api_endpoint_overrides/securitycenter https://securitycenter.eu.rep.googleapis.com/
```

要重置端点以恢复默认的全局路由：

```bash
gcloud config unset api_endpoint_overrides/securitycenter
```

### 3. 位置限定发现资源名称

区域发现资源名称包含 `/locations/{location}/` 路径段：

-   组织级：
    `organizations/{org_id}/sources/{source_id}/locations/{location}/findings/{finding_id}`
-   文件夹级：
    `folders/{folder_id}/sources/{source_id}/locations/{location}/findings/{finding_id}`
-   项目级：
    `projects/{project_id}/sources/{source_id}/locations/{location}/findings/{finding_id}`

对位置限定发现名称执行深入分析时：

1.  提取 `{parent}` 范围（`/sources/...` 之前的前缀，例如 `organizations/{org_id}`）。
2.  从 `/locations/{location}/` 中提取 `{location}`（例如 `eu`、`us`、`me-central2`）。如果发现名称中不存在，则默认为 `global`（或用户指定的位置）。
3.  使用 `--location={location}` 和 `--filter="name=\"{finding_name}\""` 执行查询。

--------------------------------------------------------------------------------

## 基于意图的查询策略

### 1. 深入分析（特定发现详细信息）

**意图**：用户提供特定发现名称或明确要求检索单个发现的全部详细信息。 \
**操作**：使用 `gcloud scc findings list` 命令，对 `name` 进行严格过滤且不使用 `--field-mask` 以检索完整的 JSON 有效负载。指定 `--location={location}`（除非指定区域位置或发现名称中包含区域信息，否则默认为 `global`）。

```bash
gcloud scc findings list {parent} \
  --location={location} \
  --filter="name=\"{finding_name}\"" \
  --format="json" --limit=1
```

### 2. 列表（过滤投影）

**意图**：用户希望列出符合标准的活动发现，而无需拉取完整的嵌套有效负载。 \
**操作**：使用 `--field-mask` 投影来限制输出大小。指定 `--location={location}`（除非查询特定区域，否则默认为 `global`）。

```bash
gcloud scc findings list {parent} \
  --location={location} \
  --filter="{filter_expression}" \
  --field-mask="finding.name,finding.parentDisplayName,finding.findingClass,finding.category,finding.state,finding.eventTime,finding.severity,finding.resourceName" \
  --format="json" --order-by="severity,event_time desc" --limit=100
```

| 意图 / 目标发现类别 | `--filter` 表达式                      |
| :------------------ | :------------------------------------- |
| **所有活动发现**     | `state="ACTIVE"`                       |
| **漏洞**            | `state="ACTIVE" AND                    |
:                    : findingClass="VULNERABILITY"`              |
| **配置错误**         | `state="ACTIVE" AND                    |
:                    : findingClass="MISCONFIGURATION"`           |
| **有毒组合**         | `state="ACTIVE" AND                    |
:                    : findingClass="TOXIC_COMBINATION"`          |
| **外部暴露**         | `state="ACTIVE" AND                    |
:                    : findingClass="EXTERNAL_EXPOSURE"`          |
| **威胁**            | `state="ACTIVE" AND findingClass="THREAT"` |
| **观察结果**         | `state="ACTIVE" AND                    |
:                    : findingClass="OBSERVATION"`                |
| **敏感数据风险**     | `state="ACTIVE" AND                    |
:                    : findingClass="SENSITIVE_DATA_RISK"`        |
| **瓶颈**            | `state="ACTIVE" AND                    |
:                    : findingClass="CHOKEPOINT"`                 |
| **立场违规**         | `state="ACTIVE" AND                    |
:                    : findingClass="POSTURE_VIOLATION"`          |
| **密钥**            | `state="ACTIVE" AND findingClass="SECRET"` |
| **SCC 错误**         | `state="ACTIVE" AND                    |
:                    : findingClass="SCC_ERROR"`                  |
| **特定类别**         | `state="ACTIVE" AND category="{category}"` |

### 3. 发现与聚合（分组）

**意图**：用户希望获取高级计数或概览（例如，“最常见的发现是什么？”、“按类别显示摘要”）。 \
**操作**：使用 `gcloud scc findings group`。指定 `--location={location}`（除非查询特定区域，否则默认为 `global`）。`--group-by` 的允许字段严格为：`resource_name`、`category`、`state`、`parent`。

```bash
gcloud scc findings group {parent} \
  --location={location} \
  --group-by="{group_by_field}" \
  --filter="state=\"ACTIVE\"" \
  --format="json"
```

--------------------------------------------------------------------------------

## 有效负载分析与交接

一旦检索到发现 JSON 有效负载：

*   **对于 `TOXIC_COMBINATION` 发现**：
    1.  验证 `attackExposure` 字段是否存在且 `score > 0`。
    2.  检查攻击路径节点、边或引用的 `attackExposureResult` 以识别暴露资源和攻击轨迹。
*   **对于 `VULNERABILITY` 发现**：
    1.  从 `vulnerability` 对象中提取 CVSS 分数、利用信号（`exploitationActivity`、`observedInTheWild`、`zeroDay`）、上游修复状态（`upstreamFixAvailable`）和受影响软件包详细信息，以评估风险：
        -   `vulnerability.cve.id`
        -   `vulnerability.cve.cvssv3.baseScore`
        -   `vulnerability.cve.cvssv3.attackVector`
        -   `vulnerability.cve.exploitationActivity`
        -   `vulnerability.cve.observedInTheWild`
        -   `vulnerability.cve.zeroDay`
        -   `vulnerability.cve.upstreamFixAvailable`
        -   `vulnerability.offendingPackage.packageName`
        -   `vulnerability.offendingPackage.packageVersion`
        -   `vulnerability.fixedPackage.packageVersion`
        -   `vulnerability.securityBulletin.suggestedUpgradeVersion`
*   **交接**：不要起草修复计划、修补资源或执行配置命令。将提取的发现有效负载传递给适当的修复或 IAM 分析技能以管理修复操作循环。

--------------------------------------------------------------------------------

## 参考模式

有关 Security Command Center 发现的 JSON 结构，请参阅 [finding_schema.md](references/finding_schema.md)。
