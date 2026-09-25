# 云监控 PromQL 生成器

使用此技能从任何云监控指标类型生成有效的 PromQL 查询。本指南适用于所有云监控指标类型，通过将云监控指标和资源描述符映射到 PromQL 结构来应用。

## 工作流程

### 解析项目 ID（关键 & 阻塞）

在执行任何其他操作（如搜索代码、读取参考或运行验证）之前，您**必须**验证 Google Cloud 项目 ID 是否可用：

1.  **检查提示/负载**：在用户的提示或输入中查找项目 ID。
2.  **检查环境**：如果提示中不存在项目 ID，您**必须**运行 `gcloud config get-value project` 尝试从环境中解析它。
3.  **请求澄清（阻塞）**：如果项目 ID 不在提示中**并且** `gcloud` 命令失败、返回空字符串或不可用，您**必须**立即停止。不要生成 PromQL 查询，不要运行验证脚本，不要使用占位符（如 `YOUR_PROJECT_ID`）。您必须拒绝继续进行，并要求用户提供项目 ID。

### 检查指标和资源描述符

1.  **首先使用提供的描述符**：如果用户的提示中已经包含指标描述符详细信息（如 `metric.type`、`metricKind`、`valueType` 或 `monitoredResourceTypes`）或特定的资源过滤器值，请直接使用这些值，而不是调用云监控 API。
2.  **发现缺失的描述符**：如果精确的指标描述符（`metric.type`、`metricKind`、`valueType`）缺失或未充分指定，请使用以下路径之一解析目标指标类型的描述符：
    *   **模糊查询**：如果提示模糊（例如 `"VM CPU 使用率"`），请首先使用 `cloud-monitoring-metric-selection` 技能来识别具体的指标类型。
    *   **已知指标类型**：如果您已经有了具体的指标类型名称（例如 `compute.googleapis.com/instance/cpu/utilization`），但需要其描述符，请调用 `google-cloud-monitoring:list_metric_descriptors` MCP 工具。如果该工具缺失，请参考 `cloud-monitoring-metric-selection` 技能来配置云监控 MCP 服务器。
    *   **备用方案**：如果 MCP 工具无法配置，则回退到直接进行云监控 API 调用。
3.  **识别关键字段**：从检索到的描述符中，识别四个关键模式属性：
    *   **`type`**：云监控指标类型字符串。
    *   **`metricKind`**：`GAUGE`、`DELTA` 或 `CUMULATIVE`。
    *   **`valueType`**：`INT64`、`DOUBLE`、`DISTRIBUTION` 或 `BOOL`。
    *   **`monitoredResourceTypes`**：用于资源范围和分组兼容的 `resource.type` 字符串。

### 解析资源过滤器 & 发现协议

要按特定资源实例过滤数据，请应用以下资源规则和发现协议：

1.  **监控资源过滤器**：始终在您的查询中包含 `monitored_resource="<type>"` 过滤器，以防止跨共享指标名称的服务发生冲突。
    *   **示例**：`monitored_resource="gae_app"`
2.  **保留用户字面量（关键）**：**始终**使用用户提示中提供的字面资源名称、命名空间和 ID。**不要**用云监控发现过程中找到的活动资源名称覆盖或替换这些值，除非用户明确要求您查找活动资源。遥测发现只能用于识别指标类型名称和标签键，**不能**用于覆盖用户输入。
3.  **资源标识符映射**：
    *   **直接和特定键**：使用最具体的资源标识符。**示例**：`version_id`、`cluster_name`。
    *   **名称到 ID 解析**：如果用户按资源*名称*（例如 `"instance-1"`）进行过滤，但资源模式使用数字 ID（如 `instance_id`），请使用 PromQL 字符串名称标签，而不是数字 ID 标签。**示例**：`instance_name`、`metadata_system_name`。
    *   **复合标识符**：对于具有分层标识符的资源（如 Cloud SQL 数据库），将过滤器格式化为单个复合键。**不要**将它们拆分为单独的 `project_id` 和子资源标签。**示例**：`database_id="{project_id}:{instance_name}"`。
4.  **资源标签发现**：`google-cloud-monitoring:list_metric_descriptors` 工具仅返回指标特定的标签。如果监控资源的标签模式未知，请直接从云监控 v3 REST API (`projects.monitoredResourceDescriptors.get`) 获取资源描述符：

    ```bash
    TOKEN=$(gcloud auth application-default print-access-token 2>/dev/null || gcloud auth print-access-token)
    curl -s -H "Authorization: Bearer ${TOKEN}" \
    "https://monitoring.googleapis.com/v3/projects/{project_id}/monitoredResourceDescriptors/{monitored_resource_type}"
    ```

    HTTP 200 OK 响应将返回包含该资源精确资源标签键的 `MonitoredResourceDescriptor` 对象。

### 选择聚合结构 & 默认值

查询结构和聚合函数（如 `rate`、`histogram_quantile`、`sum` 或 `avg`）取决于指标类型及其可视化方式。

1.  **参考参考**：作为单一事实来源，参考 [云监控到 PromQL 基本聚合参考](references/basic_aggregations.md)，将云监控属性（指标类型、值类型、Aligner、Reducer）映射到其 PromQL 结构。
2.  **SRE 聚合 & 可视化规则**：
    *   **不要**跨资源实例对比率/百分比利用率指标（如 CPU % 或内存限制利用率）进行求和或求平均。相反，保持它们未聚合（原始指标）、按实例分组或用 `topk(30, avg_over_time(...))` 包裹。
    *   **状态标签过滤（关键）**：只有 `agent.googleapis.com/memory/percent_used` 和 `agent.googleapis.com/disk/percent_used` 指标需要 `{state!="free"}`。**不要**按 `{state="used"}` 进行过滤。

### 格式化 & 验证查询

在呈现任何 PromQL 查询之前，请使用 linter 验证它们：

#### Python 依赖项

在执行验证脚本 (`scripts/validate_promql.py`) 之前，安装所需的 Python 依赖项：

```bash
python3 -c "import promql_parser" || pip install promql-parser
```

#### 验证过程

1.  **格式约束**：
    *   **指标名称规范化**：使用此配方将云监控指标类型转换为 PromQL 指标名称：
        1.  **分割域和路径**：使用第一个斜杠（`/`）分割云监控指标类型，以分离域和路径。
            *   **示例**：
                `storage.googleapis.com/network/received_bytes_count` -> 域 `storage.googleapis.com`，路径 `network/received_bytes_count`
        2.  **规范化域**：将域中的所有点（`.`）替换为下划线（`_`）。
            *   **示例**：`storage.googleapis.com` -> `storage_googleapis_com`
        3.  **规范化路径**：将路径中的所有点（`.`）和斜杠（`/`）替换为下划线（`_`）。
            *   **示例**：`network/received_bytes_count` -> `network_received_bytes_count`
        4.  **用冒号连接**：将规范化的域和规范化的路径用冒号（`:`）连接。
            *   **示例**：
                `storage_googleapis_com:network_received_bytes_count`
        5.  **原生 Prometheus 指标**：如果指标类型没有斜杠，请保持原样。
            *   **示例**：`up` -> `up`，`http_requests_total` -> `http_requests_total`
        6.  **分布后缀**：如果指标的 `valueType` 是 `DISTRIBUTION`，请在规范化名称的末尾追加 `_bucket`。
            *   **示例**：
                `cloudfunctions.googleapis.com/function/execution_times` ->
                `cloudfunctions_googleapis_com:function_execution_times_bucket`
    *   确保最终查询是**单行且无注释**（无 `#` 或 `//`）。云监控查询转换会折叠空白，并可能导致代码尾随注释被忽略或引发解析错误。
    *   **分组子句语法**：确保分组子句（如 `by (label)`）仅跟在聚合运算符（如 `sum`、`avg`、`min`、`max` 或 `count`）之后。**不要**将分组子句直接放在指标选择器之后。
        *   **不正确**：`metric{...} by (label)`
        *   **正确**：`sum(rate(metric{...}[5m])) by (label)`
    *   **带格式的输出代码块**：**始终**在最终响应中将最终验证的 PromQL 查询包裹在带格式的 `promql` 代码块中。
2.  **Linter 验证**：
    *   将所有生成的查询作为一个批次进行验证：`python3 <技能路径>/scripts/validate_promql.py --query '<q1>' '<q2>'`
    *   如果验证失败，请阅读 [PromQL 错误恢复指南](references/promql_error_recovery.md)，以诊断和修复常见的类型不匹配和语法错误，然后再重复循环。

## 参考

*   [云监控 PromQL 基本聚合参考](references/basic_aggregations.md)
*   [云监控 PromQL 错误恢复指南](references/promql_error_recovery.md)
*   [云监控 PromQL 文档](https://docs.cloud.google.com/monitoring/promql.md.txt)
*   [云监控监控资源类型参考](https://docs.cloud.google.com/monitoring/api/resources.md.txt)
