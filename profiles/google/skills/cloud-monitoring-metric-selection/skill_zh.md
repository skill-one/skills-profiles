# 指标选择（服务查询与本地关键词过滤）

使用此技能识别最相关的 Google Cloud Monitoring 指标描述符。它从 API 查询目标服务的所有指标描述符，并在代理的上下文中使用关键词匹配进行本地过滤。

## 关键规则

*   **始终查询实时 API**：你必须始终通过调用 `list_metric_descriptors` MCP 工具动态检索最新的指标描述符。
*   **必填项目 ID 和资源参数说明**：在调用任何 API 工具（例如 `list_metric_descriptors`）之前，你必须确保 GCP 项目 ID 在提示、URI 或环境上下文中提供。如果无法解析项目 ID，你必须要求用户澄清或提供它，然后再执行 API 查询。不要针对未确认的默认或占位符项目名称（例如 `mock-project`、`my-project-id`、`unused` 或 `YOUR_PROJECT_ID`）运行 API 查询。
*   **降级报告**：如果 API 调用失败并使用降级源（例如公共文档），你必须声明错误、降级源以及非实时数据的风险（例如潜在的陈旧性、丢失自定义指标或模式不匹配）。

## 工作流程

### 第 1 步：验证和自动配置 MCP

1.  检查是否有任何匹配 `list_metric_descriptors` 的工具（例如 `google-cloud-monitoring:list_metric_descriptors`、`mcp_google-cloud-monitoring_list_metric_descriptors` 或类似模式）在你的活动工具集中可用。
2.  **通过唯一 URL 验证**：为确保你正在调用正确的 Google Cloud Monitoring 工具，请确认底层的 MCP 服务器配置指向：**`https://monitoring.googleapis.com/mcp`**。
3.  如果工具**缺失**：

    *   找到用户环境的 MCP 配置文件。检查常见路径：
        -   `~/.gemini/config/mcp_config.json`
        -   `~/.codeium/windsurf/mcp_config.json`
        -   `cline_mcp_settings.json`
        -   `claude_desktop_config.json`
    *   直接更新/合并配置文件，使用以下服务器配置。**关键**：合并 JSON 对象以保留 `mcpServers` 中的任何现有 MCP 服务器。不要覆盖文件。

        ```json
        "google-cloud-monitoring": {
          "url": "https://monitoring.googleapis.com/mcp",
          "authProviderType": "google_credentials",
          "enabledTools": [
            "list_metric_descriptors"
          ]
        }
        ```

    *   打印一条清晰的消息，通知用户已配置 `google-cloud-monitoring` MCP 服务器，并要求他们重新启动或开始新的聊天会话以刷新工具。停止调用其他工具并结束回合。

### 第 2 步：分析请求并提取关键词

1.  **解析项目 ID 和标识符**：检查提示、资源 URI 或环境上下文中的 GCP 项目 ID 和资源标识符。根据上述关键规则，不要使用占位符项目名称。
2.  **识别服务前缀**：将目标 GCP 服务映射到其标准前缀（例如 `compute`、`spanner`、`bigquery`、`storage`）。
3.  **提取指标概念**：从用户提示中提取指标关键词（例如 "CPU"、"内存"、"扫描的字节数"、"延迟"、"连接数"），并将其映射到搜索子字符串。

*示例查询分析：*

*   **用户提示**： "检查 Cloud Storage 存储桶写入吞吐量和请求计数"
*   **资源 URI**：
    `//storage.googleapis.com/projects/my-project/buckets/my-bucket`
*   **服务前缀**： `storage`（映射到 `storage.googleapis.com`）
*   **指标关键词**： `write`、`throughput`、`request`、`count`
*   **映射子字符串**： `write`、`throughput`、`request_count`、`count`

### 第 3 步：通过 `list_metric_descriptors` 工具查询指标描述符

使用 `list_metric_descriptors` MCP 工具（使用 `pageSize: 200`）查询每个已识别服务前缀的所有指标描述符。由于 Google Cloud Monitoring 过滤器不允许将多个 `metric.type` 限制与 `OR` 结合，你必须**为每个已识别的服务前缀发起单独的查询**（顺序或并行）。

如果任何响应包含 `nextPageToken`，你必须必须执行连续的后续调用，传递 `pageToken`，直到检索完该前缀的所有剩余描述符，然后再进行过滤。

*过滤模式构建*：将目标服务域映射到其适当的前缀样式：

1.  **标准 Google Cloud 服务**：
    `starts_with("<service_prefix>.googleapis.com/")`（例如 `bigquery.googleapis.com/`、`redis.googleapis.com/`）。
2.  **Ops Agent（访客操作系统）**： `starts_with("agent.googleapis.com/")`（用于访客操作系统内存/磁盘指标）。
3.  **Kubernetes / GKE 本地**： `starts_with("kubernetes.io/")`
4.  **Istio 服务网格**： `starts_with("istio.io/")`
5.  **Knative Serving / Autoscaler**： `starts_with("knative.dev/")`
6.  **自定义/外部指标**：使用 `starts_with("custom.googleapis.com/")` 或 `starts_with("external.googleapis.com/")`。

*示例工具调用有效负载*：如果请求中针对 Spanner 和 Compute Engine，执行这两个工具调用：

1.  Spanner 查询：

```json
{
  "name": "projects/my-project-id",
  "filter": "metric.type = starts_with(\"spanner.googleapis.com/\")",
  "pageSize": 200
}
```

1.  Compute Engine 查询：

```json
{
  "name": "projects/my-project-id",
  "filter": "metric.type = starts_with(\"compute.googleapis.com/\")",
  "pageSize": 200
}
```

使用这些有效负载调用 `list_metric_descriptors` 工具。

### 第 4 步：本地过滤与降级协议

汇总第 3 步返回的所有描述符，并在你的 LLM 上下文中进行本地过滤：

1.  **关键词过滤**：通过将目标指标关键词（例如 "cpu"、"latency"）与描述符的 `type`、`displayName` 和 `description` 字段匹配来过滤列表。
2.  **资源对齐**：检查指标是否包含与目标资源粒度匹配的标签（例如，如果针对数据库资源，检查 `database` 标签）。不要尝试直接动态匹配资源类型字符串，因为 Google Cloud Monitoring 资源映射（如 Spanner 数据库映射到 `spanner_instance`）可能不太直观。

#### 故障排除与 API 降级

如果任何工具调用失败、超时或返回空结果，使用以下策略：

*   **情况 A：API 语法错误**：检查错误消息，修正过滤语法，然后重试。
*   **情况 B：超时/速率限制**：使用较小的页面大小（例如 `pageSize: 20`）重试一次。
*   **情况 C：不可恢复的失败/空列表**：
    1.  验证目标服务是否在项目中启用。
    2.  搜索 Google Cloud 公共文档以验证服务的标准指标。

### 第 5 步：输出选定指标

对于每个服务域，仅返回与用户意图直接相关的 5-15 个关键指标。

你必须以干净的 Markdown 表格形式报告选定的指标，按服务分组（即每个服务前缀一个表格）。表格必须包括以下列："Metric Type"、"Display Name"、"Description"、"Metric Kind"、"Value Type"、"Unit" 和 "Monitored Resource Types"。将 Google Cloud Monitoring `list_metric_descriptors` 工具调用响应对象中的字段直接映射到表格列：

*   **Metric Type**：映射到 `type` 字段（例如 `spanner.googleapis.com/instance/cpu/utilization`）。
*   **Display Name**：映射到 `displayName` 字段。
*   **Description**：映射到 `description` 字段。
*   **Metric Kind**：映射到 `metricKind` 字段（例如 `GAUGE`、`DELTA`、`CUMULATIVE`）。
*   **Value Type**：映射到 `valueType` 字段（例如 `INT64`、`DOUBLE`、`DISTRIBUTION`、`BOOL`）。
*   **Unit**：映射到 `unit` 字段（例如 `1`、`By`、`s`、`ms`）。
*   **Monitored Resource Types**：映射到 `monitoredResourceTypes` 列表字段（例如 `["spanner_instance"]`）。

*示例输出表格：*

Metric Type                                       | Display Name             | Description                                 | Metric Kind | Value Type | Unit | Monitored Resource Types
:------------------------------------------------ | :----------------------- | :------------------------------------------ | :---------- | :--------- | :--- | :-----------------------
`spanner.googleapis.com/instance/cpu/utilization` | Instance CPU Utilization | Fraction of allocated CPU currently in use. | GAUGE       | DOUBLE     | 1    | `["spanner_instance"]`

## 参考文档和链接

*   **Google Cloud Monitoring 指标列表**：
    [GCP Metrics Documentation](https://cloud.google.com/monitoring/api/metrics_gcp)
*   **MetricDescriptor MCP 工具参考**：
    [MCP Tools Reference: monitoring.googleapis.com](https://docs.cloud.google.com/monitoring/api/ref_v3_mcp/mcp/tools_list/list_metric_descriptors)
*   **Monitoring 过滤语法指南**：
    [Monitoring Filters](https://cloud.google.com/monitoring/api/v3/filters)
