# 数据血缘摘要

该技能指导代理调查和总结特定焦点资产（表级血缘）或特定字段的血缘图（列级血缘）。它提供了一种直观的从左到右的演示，说明数据如何进入和离开资产，将复杂的节点和链接细节抽象为简单的英语。

## 前置条件

该技能依赖于**Google Cloud 数据血缘（知识目录）MCP 服务器**进行图遍历。确保您可以在上游和下游两个方向上运行 `search_lineage` 查询。有关详细的连接配置和工具模式，请参阅 [MCP 使用](references/mcp-usage.md)。

## 工作流逻辑

### 1. 获取血缘

通过向 MCP 工具发出*两次单独的调用*，从焦点点（上游和下游）双向获取血缘图：一次使用 `"direction": "UPSTREAM"`，另一次使用 `"direction": "DOWNSTREAM"`。

*   **位置策略**：您**必须**使用 `read_url` 工具从提供的 [知识目录位置](https://docs.cloud.google.com/dataplex/docs/locations.md.txt) 链接动态获取完整的位置列表。为确保不会遗漏跨区域血缘，始终使用此链接验证当前的 GCP 区域列表，然后再填充 `locations` 数组。您**必须**使用从该链接获取的所有支持物理区域填充 `locations` 数组。您还可以选择性地使用 `bq show` 或 `gcloud storage ls` 确定资产的具体活动区域。
*   **搜索参数**：在调用 `search_lineage` 时，使用 `maxDepth = 10`、`maxResults = 5000` 和 `maxProcessPerLink = 10` 作为稳健的默认值。例如，一个 DOWNSTREAM 调用应格式化为如下所示（根据需要扩展 `locations` 数组）：

    ```json
    {
      "parent": "projects/project_id/locations/us",
      "locations": [
        "us",
        "us-central1",
        "us-east1",
        "us-west1",
        "europe-west1",
        "asia-northeast1"
      ],
      "rootCriteria": {
        "entities": {
          "entities": [
            {
              "fullyQualifiedName": "bigquery:project.dataset.table"
            }
          ]
        }
      },
      "direction": "DOWNSTREAM",
      "limits": {
        "maxDepth": 10,
        "maxResults": 5000,
        "maxProcessPerLink": 10
      }
    }
    ```

    确保您也使用 `"direction": "UPSTREAM"` 进行类似的调用以获取上游血缘。

*   **列级血缘 (CLL)**：`search_lineage` 工具可以通过配置 `field` 数组来查找所有列级血缘 (CLL)。如果请求表级血缘 (TLL)，请配置调用以通过使用 `"*"` 通配符获取 CLL 链接以及 TLL 链接。例如：

    ```json
    "rootCriteria": {
      "entities": {
        "entities": [
          {
            "fullyQualifiedName": "bigquery:project.dataset.table",
            "field": [
              "*"
            ]
          }
        ]
      }
    }
    ```

    如果评估特定列，请将 `"*"` 替换为特定列名（例如，`"efficiency_score"`）。

### 2. 总结

使用以下提示指南生成总结。

*   **角色**：扮演一位专家数据血缘分析师，生成简洁、易于理解的从左到右的数据流演示。
*   **结构与流程**：立即开始总结文本，结构如下：
    *   **整体流程类型**：声明推断的流程类型和数据域（例如，“这似乎是一个特征工程工作流...”）。
    *   **系统概述**： upfront 列出主要涉及的系统。如果请求的是列级血缘，您**必须** upfront 明确声明分析的范围仅限于指定的字段。
    *   **上游血缘**：使用确切的粗体标题 `**上游血缘：**`。叙述必须详细说明数据如何到达焦点资产，提及关键源系统、项目和处理任务（例如，Dataproc 上的 Spark）。
    *   **下游血缘**：使用确切的粗体标题 `**下游血缘：**`。详细说明数据从焦点资产到最终消费者系统的去向。
    *   **分析元数据**：显示用于 API 调用的参数，以提供有关总结边界的透明度。输出必须包含：
        *   **搜索的位置**：`{list_of_locations_queried}`
        *   **父位置**：`{parent_path}`
        *   **深度限制**：`{maxDepth}`
        *   **每个链接处理限制**：`{maxProcessPerLink}`
        *   **用户提示**：一个提示，建议他们可以要求使用扩展的位置（如果没有全部使用）或深度重新运行。
*   **粒度约束**：
    *   优先考虑系统、项目和数据集之间的流，而不是单个文件/表。
    *   如果少于 5 个，您**必须**明确列出特定资产名称（例如，源表、中间视图、消费者表）。如果少于 5 个，不要只是总结计数；请明确命名它们。否则，如果有 5 个或更多，按计数聚合（例如，“5 GCS 桶”）。
    *   仅提及*最终源*、*最终消费者*和*总资产*的计数。
    *   如果只涉及一个项目，不要对每个数据集重复项目名称。
*   **语气**：避免使用术语和像“有明显的事实点”这样的通用短语。要直接明了。最终输出是 Markdown。

### 3. 返回总结

将最终的总结输出返回给用户。

## 外部文档

-   [Google Cloud 知识目录数据血缘文档](https://docs.cloud.google.com/dataplex/docs/about-data-lineage.md.txt)
-   [使用数据血缘 MCP 服务器](https://docs.cloud.google.com/dataplex/docs/use-lineage-mcp.md.txt)
-   [知识目录数据血缘 API 参考](https://docs.cloud.google.com/dataplex/docs/reference/data-lineage/rest.md.txt)
