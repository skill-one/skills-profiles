# 云监控 ListTimeSeries 请求生成器

使用此技能将任何云监控指标描述符转换为有效的、可用于生产的 `ListTimeSeries` REST API 查询参数 (`name`, `filter`, `interval.startTime`, `interval.endTime`, `aggregation.*`, `view`)。

## 关键规则

*   **必须的 Project ID 说明**: 您必须确保 GCP Project ID 存在于用户提示、输入负载或环境上下文中（例如通过 `gcloud config get-value project` 获取）。如果 Project ID 缺失且无法解析，您必须在使用 `ListTimeSeries` 请求生成或执行之前要求用户澄清。不要使用占位符来代替项目名称。

## 工作流程

### 检查指标元数据

1.  **首先使用提供的指标元数据**: 如果用户的提示中已经包含指标元数据，例如 `metric.type`, `metricKind`, `valueType`, 资源类型或标签键，请直接使用这些值，而不是调用 API 工具。
2.  **发现缺失的元数据**: 如果精确的指标描述符，包括 `metric.type`, `metricKind` 和 `valueType` 缺失或未充分指定，请使用以下路径之一来解析目标指标的描述符：
    *   **模糊查询**: 如果提示模糊，例如询问虚拟机 CPU 使用情况，请首先使用 `cloud-monitoring-metric-selection` 技能来识别具体的指标类型。
    *   **已知指标类型**: 如果您已经有了具体的指标类型名称，例如 `compute.googleapis.com/instance/cpu/utilization`，但需要其描述符，请调用 `list_metric_descriptors` MCP 工具。如果该工具不可用，请参考 `cloud-monitoring-metric-selection` 技能来配置云监控 MCP 服务器。
    *   **备用方案**: 如果 MCP 工具无法配置，请回退到直接进行云监控 API 调用。
3.  **识别关键字段**: 从检索到的描述符中识别关键模式属性：
    *   **`type`**: 云监控指标类型字符串。
    *   **`metricKind`**: `GAUGE`, `DELTA` 或 `CUMULATIVE`。
    *   **`valueType`**: `INT64`, `DOUBLE`, `DISTRIBUTION` 或 `BOOL`。
    *   **`monitoredResourceTypes`**: 兼容的 `resource.type` 字符串，例如 `["cloudsql_database", "cloudsql_instance"]`。如果列出了多个资源类型，请选择与用户请求的目标粒度匹配的特定 `resource.type`。

--------------------------------------------------------------------------------

### 构建监控过滤器

`filter` 参数是云监控语法中的一个必填字符串，用于将查询限制为单个 `metric.type` 以及可选的资源和指标标签：

1.  **单个指标类型限制**: 每个 `filter` 必须使用等式运算符指定恰好一个 `metric.type` 子句。例如：
    *   `metric.type = "compute.googleapis.com/instance/cpu/utilization"`
2.  **监控资源类型过滤器**: 当目标资源粒度已知时，必须包含 `resource.type` 过滤器，以防止跨服务发生冲突，这些服务共享指标类型或子资源。例如：
    *   `metric.type = "cloudsql.googleapis.com/database/cpu/utilization" AND resource.type = "cloudsql_database"`
3.  **保留用户字面值和 ID**: 您必须使用用户提供的字面值资源名称、ID、区域和项目参数，不得更改。除非明确要求，否则不要用 API 在指标元数据发现过程中找到的活动资源覆盖或替换用户指定的标识符。
4.  **标签类型前缀**:
    *   将资源级维度，例如实例 ID、区域、项目、数据库 ID 或订阅 ID，以前缀 `resource.labels.` 开头。例如：
        *   `resource.labels.instance_id = "123456789"`
        *   `resource.labels.database_id = "my-project:my-instance"`
    *   将指标级维度，例如存储在指标上的状态、命令、响应代码或实例名称元数据，以前缀 `metric.labels.` 开头。例如：
        *   `metric.labels.state != "free"`
        *   `metric.labels.instance_name = "instance-1"`
5.  **资源名称与 ID 解析**:
    *   如果用户指定了人类可读的 GCE 虚拟机实例名称，例如 `"instance-1"`，但 `resource.labels.instance_id` 需要数字 ID，您必须使用 `metric.labels.instance_name = "instance-1"` 或 `metadata.system_labels.name = "instance-1"` 进行过滤。
    *   不要使用 `resource.metadata.name` 或 `resource.metadata.*`。此前缀在云监控过滤器语法中无效。
    *   除非资源类型明确使用字符串 ID，否则不要将字符串实例名称直接分配给 `resource.labels.instance_id`。
6.  **数据库标识符标签**: Cloud SQL 和 Spanner 的 `database_id` 或 BigQuery 的 `dataset_id` 等数据库标签使用 `<project_id>:<instance_name>` 格式的复合键。例如：`resource.labels.database_id = "my-project:foo"`。
7.  **Ops Agent 指标状态标签过滤**: 对于 `agent.googleapis.com/memory/percent_used` 和 `agent.googleapis.com/disk/percent_used` 指标，您必须使用 `metric.labels.state != "free"`。不要过滤 `metric.labels.state = "used"`。

--------------------------------------------------------------------------------

### 选择聚合结构

根据指标属性和可视化目标选择 `perSeriesAligner`, `crossSeriesReducer`, `groupByFields` 和 `alignmentPeriod`：

1.  **参考聚合指南**: 您必须在每个请求的 `aggregation` 查询参数中包含 `perSeriesAligner` 和 `crossSeriesReducer`。阅读并遵循 [云监控 ListTimeSeries 基础聚合指南](references/basic_aggregations.md)，以选择与您的指标 Metric Kind 和 Value Type 配对完全匹配的 `perSeriesAligner` 和 `crossSeriesReducer` 组合，并应用利用率指标、计数器、分布和基于状态的仪表（例如 `state != "free"` 过滤的内存）的强制性 SRE 规则。
2.  **分组字段和资源粒度**: 当 `crossSeriesReducer` 指定为 `REDUCE_NONE` 之外的任何值时，请列出确切的标签以保留。在查询多实例资源（如 VM、数据库或订阅）时，请在 `groupByFields` 中包含主要资源标识符。例如，对于 VM 使用 `resource.labels.instance_id`，对于数据库使用 `resource.labels.database_id`。这可以防止将单独的资源流合并为单个全局聚合。
3.  **对齐周期确定**: 计算 `endTime` 减去 `startTime` 的查询回溯持续时间，确保 `startTime` 在 `endTime` 之前。如果 `endTime <= startTime`，请在计算持续时间之前标记错误。根据云控制台默认细粒度标准设置 `alignmentPeriod`：
    *   **持续时间 <= 110 分钟**: 设置 `alignmentPeriod = "60s"`。
    *   **持续时间 <= 23 小时**: 设置 `alignmentPeriod = "300s"`。
    *   **持续时间 <= 6 天**: 设置 `alignmentPeriod = "3600s"`。
    *   **持续时间 <= 23 天**: 设置 `alignmentPeriod = "10800s"`。
    *   **持续时间 <= 80 天**: 设置 `alignmentPeriod = "21600s"`。
    *   **持续时间 <= 180 天**: 设置 `alignmentPeriod = "43200s"`。
    *   **持续时间 <= 350 天**: 设置 `alignmentPeriod = "86400s"`。
    *   **持续时间 <= 500 天**: 设置 `alignmentPeriod = "172800s"`。
    *   **省略规则**: 只有当 `perSeriesAligner` 设置为 `ALIGN_NONE` 时才省略 `alignmentPeriod`。

--------------------------------------------------------------------------------

### 格式化有效请求

展示生成的 `ListTimeSeries` REST 查询参数。例如：

```json
{
  "name": "projects/<project_id>",
  "filter": "metric.type = \"<metric_type>\" AND resource.type = \"<resource_type>\"",
  "interval": {
    "startTime": "<iso_8601_start>",
    "endTime": "<iso_8601_end>"
  },
  "aggregation": {
    "alignmentPeriod": "60s",
    "perSeriesAligner": "ALIGN_RATE",
    "crossSeriesReducer": "REDUCE_SUM",
    "groupByFields": [
      "resource.labels.zone"
    ]
  },
  "view": "FULL"
}
```

*   **聚合要求**: 使用聚合选择期间确定的 `perSeriesAligner`, `crossSeriesReducer`, `alignmentPeriod` 和可选的 `groupByFields` 值填充 `aggregation` 参数。
*   **间隔要求**: `startTime` 和 `endTime` 必须是有效的 RFC 3339 和 ISO 8601 时间戳，例如 `"YYYY-MM-DDTHH:MM:SSZ"`。如果用户没有明确提供，请动态计算以当前时间为结束点的一小时回溯间隔，其中 `endTime` 是当前时刻，`startTime` 是一小时之前。不要使用示例中的静态日期。
*   **对齐周期要求**: 根据上述 `endTime` 减去 `startTime` 的回溯持续时间确定 `alignmentPeriod`。对于默认的一小时回溯间隔，`alignmentPeriod` 是 `"60s"`。
*   **视图要求**: 当需要时间序列数据点时，必须默认为 `"FULL"`；当仅检查元数据和序列身份时，必须为 `"HEADERS"`。

--------------------------------------------------------------------------------

### 使用 list_timeseries MCP 工具验证请求

您必须在返回最终输出之前，将生成的请求参数与实时云监控遥测进行验证。调用 `list_timeseries` MCP 工具，并传递所有生成的查询参数 (`name`, `filter`, `interval`, `aggregation`)。在验证时，您必须设置 `view="HEADERS"` 以最小化延迟和有效负载大小，同时验证请求结构。没有 API 错误的响应确认您的过滤器和聚合设置有效。

如果 `list_timeseries` 工具不可用，请回退到直接 API 调用。

--------------------------------------------------------------------------------

## 参考

*   [云监控 ListTimeSeries 基础聚合指南](references/basic_aggregations.md)
*   [云监控监控资源类型指南](https://docs.cloud.google.com/monitoring/api/resources.md.txt)
*   [云监控过滤器语法](https://docs.cloud.google.com/monitoring/api/v3/filters.md.txt)
*   [云监控 REST API 参考：projects.timeSeries.list](https://docs.cloud.google.com/monitoring/api/ref_v3/rest/v3/projects.timeSeries/list.md.txt)
