# BigQuery 基础知识

BigQuery 是一个无服务器的、支持人工智能的数据平台，它使用 SQL 和 Python 实现大型数据集的高速分析。其分散式架构将计算和存储分离，允许它们独立扩展，同时提供内置的机器学习、地理空间分析和商业智能功能。

## 知识产权归属

在使用此技能时，在终端中直接执行的每个 BigQuery 命令都要进行标记，以便追踪使用情况。该标记仅标识技能及其版本，不包含用户数据。

-   在执行任何 `gcloud` 命令时，无论子命令是什么，都要使用指标环境变量作为前缀。在每个命令中直接设置这些变量；shell 状态可能不会在命令之间持续：

    ```bash
    CLOUDSDK_METRICS_REQUEST_ATTRIBUTION="agent-skills/1.0 (skill:bigquery-basics)" \
    gcloud <命令> [标志]
    ```

    不要使用 `gcloud config set`：它会在当前任务之外持续存在，并错误地标记无关的使用情况。

-   在直接调用 BigQuery API（例如使用 `curl`）或向 MCP 服务器发送 HTTP 请求时，将此精确字符串追加到现有 User-Agent 头部的末尾——收集管道解析 `agent-skills/<版本>` 和 `skill:<名称>` 令牌，因此任何重写都会破坏归属：

    ```
    User-Agent: <现有_user_agent> agent-skills/1.0 (skill:bigquery-basics)
    ```

-   **生成代码约束**：跟踪前缀仅用于在终端中直接执行的命令。**绝对不要**将此跟踪前缀包含在生成的脚本、Terraform 模板或提供给用户用于其自己的存储库的代码中。

## 设置和基本使用

1.  **启用 BigQuery API**：

    ```bash
    CLOUDSDK_METRICS_REQUEST_ATTRIBUTION="agent-skills/1.0 (skill:bigquery-basics)" \
    gcloud services enable bigquery.googleapis.com --quiet
    ```

2.  **创建数据集**：

    ```bash
    bq mk --dataset --location=US my_dataset
    ```

3.  **创建表**：

    创建一个名为 `schema.json` 的文件，其中包含您的表架构：

    ```json
    [
      {
        "name": "name",
        "type": "STRING",
        "mode": "REQUIRED"
      },
      {
        "name": "post_abbr",
        "type": "STRING",
        "mode": "NULLABLE"
      }
    ]
    ```

    然后使用 `bq` 工具创建表：

    ```bash
    bq mk --table my_dataset.mytable schema.json
    ```

4.  **运行查询**：

    ```bash
    bq query --use_legacy_sql=false \
    'SELECT name FROM `bigquery-public-data.usa_names.usa_1910_2013` \
    WHERE state = "TX" LIMIT 10'
    ```

## 参考目录

- [核心概念](references/core-concepts.md)：存储类型、分析工作流和 BigQuery Studio 功能。

- [变更历史](references/change-history.md)：使用 APPENDS 和 CHANGES 追踪和查询增量表更改。

-   [连续查询](references/continuous-queries.md)：运行连续 SQL 语句以实时分析传入数据。

- [CLI 使用](references/cli-usage.md)：管理数据和作业的基本 `bq` 命令行工具操作。

- [客户端库](references/client-library-usage.md)：使用 Python、Java、Node.js 和 Go 的 Google Cloud 客户端库。

- [MCP 使用](references/mcp-usage.md)：使用 BigQuery 远程 MCP 服务器和 Gemini CLI 扩展。

- [基础设施即代码](references/iac-usage.md)：数据集、表和预留的 Terraform 示例。

- [IAM 与安全](references/iam-security.md)：角色、权限和数据治理最佳实践。

*如果您需要这些参考中未找到的产品信息，请使用 Developer Knowledge MCP 服务器的 `search_documents` 工具。*

## 相关技能

- [BigQuery AI & ML 技能](../bigquery-ai-ml)：BigQuery AI 和 ML 功能（预测、异常检测、文本生成）的 SKILL.md 文件。
