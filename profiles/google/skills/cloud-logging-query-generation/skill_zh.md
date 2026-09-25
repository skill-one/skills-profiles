# 生成 Logging 查询语言 (LQL) 查询

使用此技能为 Cloud Logging 生成正确的 Logging 查询语言 (LQL) 查询。

## 核心规则

1.  **严格的语法要求：**

    *   **始终使用双引号 (`"`)** 表示字符串字面量。不要使用单引号 (`'`)。
    *   将布尔运算符全部大写：`AND`、`OR`、`NOT`。
    *   始终使用括号分组术语并显式强制优先级。

2.  **常见陷阱：**

    *   **实例 ID 与实例名称：** 对于 `gce_instance` 资源类型，**不要**将实例名称与实例 ID 进行比较。实例名称是字符串（例如，`my-instance`）。实例 ID 是数字。如果你只有名称，则通过实例名称搜索 `SEARCH("my-instance")`，或者如果该标签对资源可用，则使用 `resource.labels.instance_name`。
    *   **资源类型准确性：** 不要猜测资源类型。你必须查阅服务特定的参考文件以查找正确的 `resource.type` 值。例如，在按转发规则名称或区域筛选时，使用 `internal_http_lb_rule` 而不是 `http_load_balancer`。

3.  **输出格式和占位符：**

    *   仅输出**原始 LQL 查询文本**。不要包含对话填充。除非用户明确要求，否则不要用 markdown 代码块包裹查询。允许使用 `--` 的有效 LQL 注释，并且这是包含说明或警告的唯一可接受方式。
    *   **不要阻塞缺失的变量。** 如果用户的请求缺少特定标识符（如项目 ID、实例名称或 IP 地址），不要向他们询问澄清。如果查询功能需要特定字段（如区域日志的日志桶名称），则插入用尖括号 `< >` 括起来的大写占位符字符串（例如，`"<PROJECT_ID>"`）。**关键**：如果你为用户遗漏的变量包含占位符，它将作为显式过滤器导致日志被遗漏。因此，如果该字段不是严格必需的，你必须完全省略包含占位符的过滤器/行。例如，如果用户没有指定实例，则完全省略 `resource.labels.instance_id="..."`，但必须包含 `logName=".../projects/<PROJECT_ID>/..."` 并使用占位符，如果正在构建需要严格项目 ID 的区域日志桶查询。

4.  **推荐字段：**

    *   当查询针对特定的 Google Cloud 服务或资源时，包含 `resource.type` 和 `log_id` 限制。全局查询（例如，“最新的错误日志”）不需要这些限制。

## 详细参考

参考 `references/api_reference.md` 了解 LQL 语法规则，包括运算符、NULL 处理、`SEARCH` 和正则表达式。

## 服务参考文件

生成查询前，你必须阅读特定服务的示例。LQL 模式和 `resource.type` 值是服务特定的。**不要在找到文件中的基础模式后停止阅读。你必须验证状态跟踪（如 `previousState`）是否有特定要求，或资源特定日志 ID 是否在模式块下方的段落或特定查询示例中详细说明。**

**对于以下服务，请阅读列出的确切文件：**

*   [App Engine](references/query_app_engine.md)
*   [BigQuery](references/query_bigquery.md)
*   [Cloud Deployment Manager](references/query_deployment_manager.md)
*   [Cloud Functions](references/query_cloud_functions.md)
*   [Cloud Observability (Monitoring, Logging, Trace)](references/query_cloud_observability.md)
*   [Cloud Run](references/query_cloud_run.md)
*   [Cloud Source Repositories](references/query_cloud_source_repositories.md)
*   [Cloud Spanner](references/query_spanner.md)
*   [Cloud SQL](references/query_cloud_sql.md)
*   [Cloud Storage](references/query_cloud_storage.md)
*   [Cloud Tasks](references/query_cloud_tasks.md)
*   [Compute Engine (GCE)](references/query_compute_engine.md)
*   [Dataflow](references/query_dataflow.md)
*   [Dataproc](references/query_dataproc.md)
*   [Kubernetes Engine (GKE)](references/query_gke.md)
*   [IAM & Service Accounts](references/query_iam.md)
*   [Networking (VPC, Load Balancing, 和其他)](references/query_networking.md)
*   [Security (Audit logging)](references/query_security.md)
*   [Service Usage (Enable/Disable API, Quotas)](references/query_service_usage.md)
*   [第三方（例如，Nginx, Apache）](references/query_third_party.md)

**对于未列出的 Google Cloud 服务：** 如果服务未列在上方，则根据你的通用知识编写 LQL 查询。

## 查询生成规则

1.  **资源类型：** 当你专注于特定服务时，在查询中明确定义 `resource.type`。对于某些查询，你可能需要跨多个类型进行搜索（例如，`resource.type=("bigquery_project" OR "bigquery_dataset")`）。
2.  **审计和 Admin 日志：** 如果用户要求审计日志、Admin 日志、API 日志或关于谁创建了、更新了、删除了、读取了或访问了资源的日志：
    *   你必须阅读
        [references/query_audit_logs.md](references/query_audit_logs.md) 以获取正确的 `protoPayload` 模式路径和常见示例。
    *   如果没有列出特定示例，通过组合服务和动词猜测 `protoPayload.methodName`。猜测时，你必须使用作用域 `SEARCH()` 函数（例如，`SEARCH(protoPayload.methodName, "compute.instances.insert")`）而不是精确匹配运算符（`=`），以避免版本前缀不匹配。**不要**使用冒号运算符（`:`），因为它可能导致子字符串误报。
    *   对于通用 API 启用/禁用事件（例如，服务被禁用），始终使用 `resource.type="audited_resource"`。
3.  **处理未知模式（关键）：** 如果用户要求按特定字段或条件筛选，并且你无法在参考文件中找到匹配的示例或模式，**你必须使用全局搜索生成查询。**
    *   只有当你确信其确切名称时，才指定 `jsonPayload.*` 或 `protoPayload.*` 字段结构。
    *   使用 `SEARCH()` 函数在正确的 `resource.type` 内全局查找关键词。
    *   **强制 LQL 注释：** 当交付使用 `SEARCH` 的查询时，你必须在使用 `--` 在查询顶部添加 LQL 注释，表明你使用了全局关键字搜索，因为精确模式不在你的参考中。**不要**输出对话文本，严格遵循输出格式规则。

## 支持链接

*   [Cloud Logging 查询语言文档](https://docs.cloud.google.com/logging/docs/view/logging-query-language)
*   [监控资源类型目录](https://docs.cloud.google.com/logging/docs/api/v2/resource-list)
*   [Cloud Logging 查询库](https://docs.cloud.google.com/logging/docs/view/query-library)
