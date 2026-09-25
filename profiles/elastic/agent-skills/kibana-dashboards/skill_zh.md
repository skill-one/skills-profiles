# Kibana 仪表板和 Lens 可视化

使用 Kibana 9.4+ 仪表板和可视化 API 创建、更新和删除 Kibana 仪表板和独立的 Lens 可视化。生成最小的、可比较的 JSON 正文；优先使用内联面板定义而不是库引用；在编写指标或图表层之前选择正确的数据集类型（数据视图与 ES|QL）。

<!-- begin-partial: preamble -->

## 环境配置

此技能通过 `elastic` CLI 执行 Elasticsearch 操作。如果未安装 [`elastic` CLI](https://github.com/elastic/cli#configuration)，请告知用户其用途。不要猜测凭证、直接调用 HTTP API 或尝试其他解决方案。

此技能以 HTTP 简写形式引用操作（例如，`GET /`、`GET /_cat/indices`、`GET /{index}/_mapping`、`GET /{index}/_settings/index.mode`、`POST /_query`）。文档末尾的 [操作](#operations) 表将每个简写映射到等效的 `elastic` CLI 命令——始终使用 CLI 而不是直接调用 HTTP API。

<!-- end-partial: preamble -->

## 前置条件

**版本要求：** Kibana 9.4+（仪表板和可视化 API）。

**ES|QL 位置：**

- 独立库图表：`PUT kbn:/api/visualizations/{id}` 并使用 `data_source.type: "esql"`。
- 仪表板中嵌入的 ES|QL 面板：通过 `PUT kbn:/api/dashboards/{id}` 使用内联 `vis` 面板 `config` 并设置 `data_source.type: "esql"`。
- 当用户明确请求 ES|QL 时，不要使用 `data_source.type: "data_view_reference"` 或索引模式聚合——持久化的 Lens 状态必须使用基于文本的 ES|QL 数据源（`textBased` / `esql`），而不是数据视图计数操作。

## 流程

1. **验证 Kibana 连接。** 调用 `GET kbn:/api/status`。如果调用失败，停止并显示错误——不要猜测端点或凭证。读取 `version.number` 以确认集群满足 9.4+ 要求。

2. **分类任务。** 确定用户是否需要 **仪表板**（面板集合，可选时间范围）、**独立的 Lens 可视化**（通过 ID 引用的库项或单独使用）或 **两者**。确定是否提供了确定性的保存对象 ID——当提供时，使用该 ID 进行 upsert（`PUT`），而不是 `POST`（后者自动生成 ID）。

3. **在构建指标或层之前选择数据集类型。**

   | 用户意图                                      | 数据集                                                                    | 指标 / 轴模式                                                                                                                    |
   | ------------------------------------------------ | -------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
   | 简单计数或对保存的数据视图进行聚合             | `data_source.type: "data_view_reference"` 并使用 `ref_id`                    | `metrics: [{ type: "primary", operation: "count" }]`（或其他聚合操作）                                                   |
   | 临时索引模式                                 | `data_source.type: "data_view_spec"` 并使用 `index_pattern` 和 `time_field` | 相同的聚合 `operation` 字段                                                                                                      |
   | ES\|QL 查询（明确或复杂逻辑）                 | `data_source.type: "esql"` 并使用 `query`                                    | `metrics: [{ type: "primary", column: "<alias>" }]` 或层轴 `{ column: "<alias>" }` — **永远**不在指标上使用 `operation: "count"` |

   在 ES|QL 查询中编写聚合（`STATS count = COUNT()`），然后按名称引用结果列。

4. **在创建或更新仪表板时构建仪表板正文。** 请求正文是扁平的——`title`、`panels` 和可选的 `time_range` 位于根目录。写入时不要用 `{ data: ... }` 包裹。必填字段：
   - `title` — 用户请求的确切字符串。
   - `panels` — 数组；当用户请求空仪表板时使用 `[]`（不要省略键或编造面板）。
   - `time_range` — 当用户指定默认时间过滤器时，设置 `{ "from": "<expr>", "to": "<expr>" }`（例如 `{ "from": "now-7d", "to": "now" }`）。提供 `time_range` 会在打开时保留仪表板时间过滤器（相当于在 UI 中启用时间恢复）。

   **使用确定性的 ID 进行 upsert：**

   ```json
   {
     "title": "Sales Overview",
     "panels": [],
     "time_range": { "from": "now-7d", "to": "now" }
   }
   ```

   当用户提供该 ID 时，使用上述正文调用 `PUT kbn:/api/dashboards/eval-sales-overview`。

   **内联 ES|QL 指标面板示例**（在 `panels` 中）：

   ```json
   {
     "type": "vis",
     "id": "total-requests",
     "grid": { "x": 0, "y": 0, "w": 12, "h": 6 },
     "config": {
       "title": "Total Requests",
       "type": "metric",
       "data_source": {
         "type": "esql",
         "query": "FROM logs* | STATS count = COUNT()"
       },
       "metrics": [{ "type": "primary", "column": "count" }]
     }
   }
   ```

   优先使用内联 `config` 属性而不是 `config.ref_id` 以生成可移植的仪表板。阅读 [仪表板 API 参考](references/dashboard-api-reference.md) 以了解面板类型、网格布局和复制工作流。

5. **当用户请求库图表时构建独立的 Lens 可视化。** 使用可视化 API。提供 ID 时使用 `PUT kbn:/api/visualizations/{id}` 进行 upsert；否则 `POST kbn:/api/visualizations` 并从响应中报告生成的 ID。

   **ES|QL 指标（来自日志的总计数）：**

   ```json
   {
     "type": "metric",
     "title": "Total Requests",
     "data_source": {
       "type": "esql",
       "query": "FROM logs* | STATS count = COUNT()"
     },
     "metrics": [{ "type": "primary", "column": "count" }]
   }
   ```

   当需要该 ID 时，调用 `PUT kbn:/api/visualizations/eval-total-requests`。API 持久化一个 Lens 保存对象，其数据源状态使用 ES|QL（`textBased` / `esql`），而不是索引模式聚合。

   阅读 [Lens API 参考](references/lens-api-reference.md) 和
   [图表类型参考](references/chart-types-reference.md) 以了解 xy、仪表、热力图和其他图表模式。

6. **执行并确认。** 使用 `PUT kbn:/api/dashboards/{id}` 或 `PUT kbn:/api/visualizations/{id}`（或 `POST` 当未提供 ID 时）执行写入。使用 `GET kbn:/api/dashboards/{id}` 或
   `GET kbn:/api/visualizations/{id}` 确认。将 ID 和标题报告给用户——在没有成功读取回的情况下不要声称成功。

7. **在请求时列出、导出或删除。** 调用 `GET kbn:/api/dashboards` 或 `GET kbn:/api/visualizations` 以发现现有对象。调用 `DELETE kbn:/api/dashboards/{id}` 或 `DELETE kbn:/api/visualizations/{id}` 以删除对象。对于保存对象的批量导出或导入，调用 `POST kbn:/api/saved_objects/_export` 或
   `POST kbn:/api/saved_objects/_import`。

## 仪表板网格

仪表板使用 **48 列** 网格。在 16:9 屏幕上，大约 **20–24 行** 可以显示在视口上方——在该区域目标 **8–12 个面板**。

| 宽度   | 列数 | 高度（行） | 用例                 |
| ------- | ------- | ------------- | ------------------------ |
| 全宽    | 48      | 14–16         | 宽时间序列、表格       |
| 半宽    | 24      | 10–12         | 主要图表             |
| 四分之一 | 12      | 5–6           | KPI 指标              |
| 六分之一 | 8       | 4–5           | 密集指标行            |

**网格填充：** 当堆叠行时，将下一个面板的 `y` 设置为前一个面板的 `y + h`。共享同一行的面板应使用相同的 `h`。不要将 markdown 面板作为仪表板标题——改用描述性图表标题。

## ES|QL 模式

**时间序列桶**（仪表板时间选择器注入 `?_tstart` / `?_tend`）：

```esql
FROM logs*
| WHERE @timestamp <= ?_tend AND @timestamp > ?_tstart
| STATS count = COUNT() BY BUCKET(@timestamp, 75, ?_tstart, ?_tend)
```

时间序列 xy 图表上的 x 轴设置为 `"scale": "temporal"`。参见
[图表类型参考](references/chart-types-reference.md) 以了解轴和层详细信息。

**静态参考值**——在查询中使用 `EVAL`，然后按名称引用列：

```esql
FROM logs* | STATS count = COUNT() | EVAL goal = 15000
```

## 示例

示例 JSON 定义位于 [assets/](assets/) 下：`demo-dashboard.json`、`dashboard-with-visualizations.json`、`metric-esql.json`、`bar-chart-esql.json`、`line-chart-timeseries.json`。

## 指南

1. **精确匹配用户的 ID 和标题**——不要替换自动生成的 ID。
2. **尊重空面板**——当用户请求 `panels: []` 时，发送空数组；不要添加占位符面板。
3. **请求时使用 ES|QL**——使用 `data_source.type: "esql"` 和列引用；永远不要用数据视图上的 `operation: "count"` 满足 ES|QL 请求。
4. **最小化负载**——省略可推导的默认值；让 API 注入样式和元数据。
5. **确认写入**——创建或更新后始终使用 `GET` 读取回。
6. **在生成复杂图表前读取引用**——指标和 xy 模式在数据视图和 ES|QL 之间不同；查阅
   [图表类型参考](references/chart-types-reference.md) 生成分区或表格图表前。

## 常见问题

| 错误                               | 可能原因                | 解决方法                                                                          |
| ----------------------------------- | --------------------------- | ---------------------------------------------------------------------------- |
| GET 后 404                         | 错误的 ID 或空间           | 确认 ID 并重试 `GET kbn:/api/dashboards/{id}`                          |
| 400 验证失败                      | ES\|QL 列不匹配      | 对齐 `metrics[].column` / 层 `column` 与查询中的 `STATS` 别名  |
| ES\|QL 面板保存为数据视图     | 错误的数据集类型          | 使用 `data_source.type: "esql"`，而不是 `data_view_reference`                    |
| 空仪表板缺少时间过滤器         | 省略了 `time_range`        | 当需要默认范围时，包含 `{ "from": "now-7d", "to": "now" }`                 |
| XY 图表失败                    | 缺少层 `data_source` | 将 `data_source` 放在每个层中，而不仅仅是根目录                    |

## 操作

自 CLI v0.3.0 起，仪表板和可视化 API 拥有专用的 `elastic kb dashboards` 和
`elastic kb visualizations` 命令，用于通过 ID 列出、读取、更新和删除对象。`create-*-redirect` 命令目前不接受请求正文，因此要写入新对象，请提供 ID 并使用 `update-*-redirect`（PUT）命令，该命令通过 `--input-file` 传递 JSON 正文。要一次性编写多个对象，构建保存对象的 NDJSON 并使用 `post-saved-objects-import` 导入它（使用 `post-saved-objects-export` 读取回）。

| HTTP API (简写)                   | `elastic` CLI 命令                                                                                                                                             |
| -------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GET kbn:/api/status`                  | `elastic kb system get-status`                                                                                                                                    |
| `POST kbn:/api/saved_objects/_import`  | `elastic kb saved-objects post-saved-objects-import --file '<path.ndjson>' --overwrite`                                                                           |
| `POST kbn:/api/saved_objects/_export`  | `elastic kb saved-objects post-saved-objects-export --objects '[{"type":"<type>","id":"<id>"}]'`                                                                  |
| `GET kbn:/api/dashboards`              | `elastic kb dashboards get-dashboards-redirect`                                                                                                                   |
| `GET kbn:/api/dashboards/{id}`         | `elastic kb dashboards get-dashboard-redirect --id '<id>'`                                                                                                        |
| `PUT kbn:/api/dashboards/{id}`         | `elastic kb dashboards update-dashboard-redirect --id '<id>' --input-file '<path.json>'`                                                                          |
| `DELETE kbn:/api/dashboards/{id}`      | `elastic kb dashboards delete-dashboard-redirect --id '<id>'`                                                                                                     |
| `POST kbn:/api/dashboards` (无 ID)     | `create-dashboard-redirect` 目前不接受正文——提供 ID 并使用 `update-dashboard-redirect`，或通过 `post-saved-objects-import`（类型 `dashboard`）编写             |
| `GET kbn:/api/visualizations`          | `elastic kb visualizations get-visualizations-redirect`                                                                                                           |
| `GET kbn:/api/visualizations/{id}`     | `elastic kb visualizations get-visualization-redirect --id '<id>'`                                                                                                |
| `PUT kbn:/api/visualizations/{id}`     | `elastic kb visualizations update-visualization-redirect --id '<id>' --input-file '<path.json>'`                                                                  |
| `DELETE kbn:/api/visualizations/{id}`  | `elastic kb visualizations delete-visualization-redirect --id '<id>'`                                                                                             |
| `POST kbn:/api/visualizations` (无 ID) | `create-visualization-redirect` 目前不接受正文——提供 ID 并使用 `update-visualization-redirect`，或通过 `post-saved-objects-import`（类型 `lens`）编写             |
