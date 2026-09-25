# 配置云日志记录

使用此功能配置云日志记录资源，例如日志桶、日志视图或日志接收器。

> [!IMPORTANT] **沙盒网络限制（对代理测试至关重要）**：
> 在评估期间或在受限的沙盒环境中，对 Google Cloud API 的网络流量会被阻止。**请勿**运行网络发现命令以查找资源名称、项目 ID 或组织 ID。始终使用用户提示或说明中提供的确切项目 ID 或占位符，例如 `{project_id}`。假设这些资源存在，并直接使用配置命令进行操作。运行这些发现命令会导致执行挂起并超时。

## 安全性和确认级别（至关重要）

在代表用户执行任何命令之前，您必须根据请求的操作遵守以下安全级别：

1.  **R级：只读**
    *   **描述**：仅读取状态或查询日志的命令。
    *   **示例命令**：
        *   `gcloud logging read`
        *   `gcloud logging buckets list`
    *   **规则**：无需确认。您可以立即执行这些命令以收集信息。
2.  **M级：变更（非计费）**
    *   **描述**：不会产生直接存储或计费成本的非计费元数据创建或配置修改，并且不会影响资源安全/访问策略。
    *   **示例命令**：
        *   `gcloud logging views create`
        *   `gcloud logging views update`
        *   `gcloud logging scopes create`
        *   `gcloud logging buckets create`
    *   **规则**：无需确认。您可以立即执行这些命令以应用配置。
3.  **B级：计费和安全敏感的变更（高风险）**
    *   **描述**：创建计费资源或集成的操作，或修改安全和 IAM 访问控制策略（存在权限提升风险）。
    *   **示例命令**：
        *   `gcloud logging metrics create`
        *   `gcloud logging links create`
        *   `gcloud projects add-iam-policy-binding`
    *   **规则**：**需要交互式确认**。这些命令创建会产生计费成本的资源或更改安全访问权限。您必须在使用之前向用户展示确切的、字面的命令并获取用户确认。**绝对不能**在询问确认的同时执行。
4.  **D级：导致不可逆数据丢失**
    *   **描述**：永久丢弃或删除日志的操作，例如接收器排除。
    *   **示例命令**：
        *   `gcloud logging buckets delete`
        *   `gcloud logging sinks update --add-exclusion`
    *   **规则**：**需要明确输入确认**。这些命令会立即且不可逆地丢弃或删除日志，或者可能导致日志数据不被存储。您必须要求明确输入确认，例如 "是，丢弃日志"，并在用户回复之前停止执行。

## 入门指南

如果缺少 `gcloud` 可执行文件，请参考
[Google Cloud CLI 安装指南](https://docs.cloud.google.com/sdk/docs/install-sdk.md.txt)
进行安装。

## 创建日志桶（合规性和分析）（M级）

要创建具有特定保留策略的区域日志桶以用于监管合规性，并启用可观察性分析：

> [!WARNING] **强制可观察性分析降级警告**：在提供指导、编写指南或起草关于云日志记录成本优化或排除的命令时，您**必须**在最终文本响应和任何生成的指南中明确包含以下警告："在日志桶升级以使用可观察性分析后，**无法降级**以移除分析功能。"

```bash
gcloud logging buckets create {bucket_id} \
    --project={project_id} \
    --location={region} \
    --retention-days={retention_days} \
    --enable-analytics
```

*   `{bucket_id}`：例如，`my-custom-bucket`
*   `{region}`：例如，`us-central1`。您必须使用区域日志桶才能使用可观察性分析。
*   `{retention_days}`：例如，`365`

直到日志通过日志接收器路由到日志桶，日志桶才会产生存储或摄取费用。

### 验证日志桶（R级）

检查日志桶的配置以验证其合规性：

```bash
gcloud logging buckets describe {bucket_id} \
    --location={region} \
    --project={project_id}
```

### 将日志路由到日志桶（B级）

> [!IMPORTANT] **计费操作（B级）**：将日志条目路由到桶会产生基于存储数据量的持续费用。在运行此命令之前，您必须获取交互式用户确认。

只有当日志接收器过滤器匹配条目并目标为该桶时，日志条目才会存储在日志桶中。

要将日志条目路由到日志桶：

```bash
gcloud logging sinks create {sink_id} \
    projects/{project_id}/locations/{region}/buckets/{bucket_id} \
    --log-filter='{filter_expression}' \
    --project={project_id}
```

--------------------------------------------------------------------------------

## 基于日志的指标

基于日志的指标统计匹配过滤器的日志条目数量，使您能够跟踪错误率并设置告警策略。

### 1. 创建基于日志的计数器指标（B级）

> [!IMPORTANT] **计费操作（B级）**：创建基于日志的指标会产生基于报告的数据点量的持续费用。在运行此命令之前，您必须获取交互式用户确认。

要统计特定日志模式的 occurrences，例如 "OutOfMemory" 错误：

```bash
gcloud logging metrics create {metric_name} \
    --log-filter='{filter_expression}' \
    --description='{description}' \
    --project={project_id}
```

*   `{metric_name}`：例如，`oom_error_count`
*   `{filter_expression}`：例如，`textPayload:"OutOfMemory"`
*   `{description}`：例如，"OOM 日志条目的计数"

参考
[REST 资源：projects.metric](https://docs.cloud.google.com/logging/docs/reference/v2/rest/v2/projects.metrics.md.txt#LogMetric)
了解指标字段的限制。

### 2. 验证基于日志的指标（R级）

要验证指标是否存在并检查其配置，请使用 `describe` 命令：

```bash
gcloud logging metrics describe {metric_name} \
    --project={project_id}
```

--------------------------------------------------------------------------------

## 限制对敏感日志的访问（安全）

任何具有项目上 `roles/logging.viewer` 角色的用户都可以通过 `_Default` 日志视图查看项目 `_Default` 日志桶中的日志。要限制日志的可见性：

> [!IMPORTANT] **歧义处理（代理指南）**：如果用户要求 "排除"、"隐藏" 或 "删除" 敏感日志，而没有明确说明是否要停止存储它们，您**必须**默认为**将它们从默认视图排除（步骤 1）**。这是一个安全、非破坏性的 M 级操作。只有在用户明确使用破坏性术语，如 *"停止存储"*、*"永久丢弃"* 或 *"接收器排除"* 时，才配置存储排除（在 "从存储中丢弃敏感日志" 部分下）。

### 1. 从默认视图排除敏感日志（M级）

要显式地将敏感日志排除于一般访问，请更新 `_Default` 日志视图的过滤器：

```bash
gcloud logging views update _Default \
    --bucket=_Default \
    --location=global \
    --project={project_id} \
    --log-filter='NOT LOG_ID("cloudaudit.googleapis.com/data_access") AND NOT LOG_ID("externalaudit.googleapis.com/data_access") AND NOT LOG_ID("{sensitive_log_id}")'
```

### 2. 创建日志视图（M级）

创建一个新的日志视图，其中包含项目 `_Default` 日志桶中的敏感日志。例如，一个访问 `{sensitive_log_id}` 的 "security-logs-view"

```bash
gcloud logging views create security-logs-view \
    --bucket=_Default \
    --location=global \
    --project={project_id} \
    --log-filter='LOG_ID("{sensitive_log_id}")' \
    --description="敏感日志"
```

### 3. 使用 IAM 条件授予日志视图访问权限（B级）

> [!IMPORTANT] **安全操作（B级）**：授予权限会更改访问控制策略，必须在执行前由用户明确确认。

要限制对日志视图的访问，请使用 IAM。在授予权限时，始终附加一个 IAM 条件，该条件将授予限制为特定日志视图。例如，仅授予 `{security_group_email}` 访问 `_Default` 桶中的 `security-logs-view`：

```bash
gcloud projects add-iam-policy-binding {project_id} \
--member='group:{security_group_email}' \
--role='roles/logging.viewAccessor' \
--condition="expression=resource.name=='projects/{project_id}/locations/global/buckets/_Default/views/security-logs-view',title=Restricted to Specific Log View,description=Only allows access to the specified log view"
```

将 `{location}` 替换为日志桶的位置，例如 `global` 或区域位置，如 `us-central1`。

### 4. 验证敏感日志限制（R级）

要验证您的敏感日志日志视图配置是否正确：

```bash
gcloud logging views describe {view_id} \
    --bucket={bucket_id} \
    --location={region} \
    --project={project_id}
```

确保 `filter` 块包含适当的限制表达式。

--------------------------------------------------------------------------------

## 从存储中丢弃敏感日志（D级）

如果您的组织合规性策略禁止存储敏感日志，您可以配置排除项，在它们写入磁盘之前丢弃它们。

> [!CAUTION] **破坏性操作（D级）**：从所有日志接收器排除日志会立即且不可逆地删除日志条目。
>
> **安全规则**：在运行此命令之前，您必须要求用户进行明确输入确认，例如，"我确认我想从存储中排除 `{sensitive_log_id}` 日志"，然后停止工具执行并等待用户回复。

**使用接收器排除从存储中排除敏感日志**

```bash
gcloud logging sinks update _Default \
    --project={project_id} \
    --add-exclusion=name=exclude-sensitive,filter='LOG_ID("{sensitive_log_id}")'
```

--------------------------------------------------------------------------------

## 成本优化（降低日志记录成本）

云日志记录的成本基于摄取和存储的数据量。您可以通过排除高容量、低价值日志或对它们进行采样来降低成本。每个将日志路由到不同日志桶的日志接收器都会导致成本增加，并且是优化的候选对象。

> [!CAUTION] **破坏性操作（D级）**：本节中的排除可能会立即停止存储日志条目。
>
> **安全规则**：在执行排除或采样更新之前，您必须要求明确输入确认（例如，"我确认我想排除负载均衡器日志"）。

### 排除所有高容量日志（D级）

要完全停止将特定类型的日志摄取到日志桶中，请向路由到该桶的日志接收器添加排除项。

```bash
gcloud logging sinks update {sink_id} \
    --project={project_id} \
    --add-exclusion=name={exclusion_name},filter={exclusion_filter}
```

*   `{sink_id}`：例如 '_Default'
*   `{exclusion_name}`：例如 'exclude-lb-logs'
*   `{exclusion_filter}`：例如 'resource.type="http_load_balancer"'

### 采样高容量日志（D级）

如果您需要一些日志进行分析，但想减少容量，请在排除过滤器中使用 `sample()` 函数。

> [!IMPORTANT] `sample(field, fraction)` 函数匹配 `fraction` 的日志。当用于**排除过滤器**时，匹配的日志会被**丢弃**。如果您排除 90% 的日志条目，则只有 10% 被保留。要排除 90%，请在排除过滤器中使用 `sample(insertId, 0.9)`。

要排除 90% 的 `DEBUG` 严重性日志：

```bash
gcloud logging sinks update _Default \
    --project={project_id} \
    --add-exclusion=name=sample-debug-logs,filter='severity=DEBUG AND sample(insertId, 0.9)'
```

### 验证日志排除和成本优化（R级）

要验证日志排除是否正确，请列出接收器的详细信息并检查 `exclusions` 以确保您的过滤器存在。例如，对于 `_Default` 接收器：

```bash
gcloud logging sinks describe _Default --project={project_id}
```

--------------------------------------------------------------------------------

## 参考资料和支持链接

*   [Google Cloud Logging - 计数器指标](https://docs.cloud.google.com/logging/docs/logs-based-metrics/counter-metrics.md.txt)
*   [Google Cloud Logging - 自定义日志视图](https://docs.cloud.google.com/logging/docs/logs-views.md.txt)
*   [Google Cloud Logging - 排除](https://docs.cloud.google.com/logging/docs/routing/overview.md.txt)
