# BigQuery 资产影响分析

该技能指导代理在 BigQuery 表或视图被报告为损坏、过时、缺失时，或当用户计划维护并希望了解修改或暂停资产更新的后果时，执行下游影响分析（爆炸半径评估）。

它主要依赖于 **Google Cloud 数据血缘（知识目录）MCP 服务器** 来发现资产之间的关系。

## 前置条件

该技能需要访问 Google Cloud 数据血缘 API，并具有到数据血缘 MCP 服务器的活动客户端连接。有关详细的连接配置和工具模式，请参阅 [MCP 使用](references/mcp-usage.md)。

## 分析工作流

### 1. 解析资产的完全限定名称 (FQN)

*   确保您拥有 BigQuery 资产的正确 FQN 格式：
    *   *格式*：`bigquery:{project_id}.{dataset_id}.{table_or_view_id}`
    *   *示例*：`bigquery:my-prod-project.analytics.orders`

### 2. 确定位置和父路径

识别要搜索的位置并构建数据血缘 API 请求：

*   **发现资产位置**：运行命令 `bq show --format=json
    {project_id}:{dataset_id}` 并提取 `location` 字段（例如，
    `us-central1` 或 `us`）。如果由于权限或缺少工具导致位置发现失败，请提示用户输入数据集的位置。
*   **设置父路径**：使用项目 ID 和 MCP 服务器的位置设置 `parent` 路径。查阅 `DataLineageServer` 工具定义以找到配置的区域或位置（例如，`us`）。格式为：
    `projects/{project_id}/locations/{mcp_server_location}`。
*   **配置搜索范围**：将发现的资产位置包含在负载的 `locations` 数组中（例如，`["us-central1"]` 或 `["us",
    "us-central1"]`）。

### 3. 获取下游血缘图

调用 `DataLineageServer:search_lineage` 工具以获取下游关系。

*   **方向**：设置为 `DOWNSTREAM`。
*   **搜索参数**：使用 `max_depth = 10` 和 `max_process_per_link = 5`
    作为稳健的默认值。

### 4. 确定爆炸半径

遍历返回的血缘链接以构建影响图：

*   **受影响的资产**：每个链接的 `target` 代表依赖于您源资产的下游资产。
*   **转换过程**：检查每个链接上的 `processes` 字段。这可以识别传播数据的 ETL 管道、BigQuery 视图或计划查询。
*   **直接与间接影响**：
    *   **直接影响（深度 1）**：直接消费源资产的资产。如果链接具有 `dependency_type: EXACT_COPY`，请将目标标记为
        “直接过时 / 相同副本”。
    *   **间接影响（深度 > 1）**：下游更远的资产，这些资产将经历级联过时数据或故障。

### 5. 总结并格式化输出

使用以下结构向用户清晰地展示您的发现：

1.  **执行摘要**：说明受影响的下游资产总数和影响的最大深度。
2.  **关键路径**：突出显示高优先级下游资产（例如，名称中包含“prod”、“dashboard”、“reporting”或“master”的资产）。
3.  **爆炸半径表**：一个干净的 Markdown 表格列出依赖项。您**必须**包含所有列：

    | 下游资产                 | 转换过程                     | 深度 | 影响类型 |
    | :----------------------- | :-------------------------- | :--- | :------- |
    | `bigquery:project.dataset.table` | `projects/p/locations/l/processes/proc` | 1     | 直接      |
    | `bigquery:project.dataset.view`  | `projects/p/locations/l/processes/view` | 2     | 间接    |
4.  **分析元数据**：提供有关搜索参数和边界的透明度，以便用户可以选择扩展它们：
    *   **搜索的位置**：`{list_of_locations_queried}`
    *   **父位置**：`{parent_path}`
    *   **深度限制**：`{max_depth}`
    *   **每个链接的处理限制**：`{max_process_per_link}`
    *   *给用户的提示*：让用户知道他们可以请求使用扩展位置或更大的深度限制重新运行分析。

## 关键约束与安全措施

1.  **正确解释空响应**：
    *   如果血缘响应为空，请立即假设在查询位置不存在依赖项，并报告给用户。
2.  **严格禁止绕过**：
    *   仅使用 `DataLineageServer:search_lineage` 工具获取下游关系。
3.  **首先验证资产存在**：
    *   如果 `bq show` 指示源表不存在，请停止并直接向用户报告。不要尝试猜测替代表名，除非用户明确指示您这样做。
4.  **无输出捷径或幻觉工件**：
    *   请直接在最终响应中呈现完整的下游爆炸半径表。避免告诉用户您已创建单独的 Markdown 文件或工件包含详细信息，除非您已明确执行文件写入工具来创建它。

## 参考目录

-   [MCP 使用](references/mcp-usage.md)：使用 Google Cloud 数据血缘远程 MCP 服务器和工具偏好。

## 外部文档

-   [Google Cloud 知识目录数据血缘文档](https://cloud.google.com/dataplex/docs/about-data-lineage)
-   [使用数据血缘 MCP 服务器](https://docs.cloud.google.com/dataplex/docs/use-lineage-mcp)
-   [知识目录数据血缘 API 参考](https://cloud.google.com/dataplex/docs/reference/data-lineage/rest)
