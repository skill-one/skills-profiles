# Spanner 基础知识

这项技能提供了使用 Google Cloud Spanner 的核心工作流程和指导，Spanner 是一种完全托管的、关键任务级数据库服务，提供全局事务一致性以及自动同步复制，以实现高可用性。

## 核心原则

-   **性能优先：** Spanner 水平扩展。效率与主键设计相关。始终警告不要将单调递增/递减的值（如顺序时间戳）作为主键的第一部分，以避免热点。
-   **模式设计：** 对于经常一起访问的强相关父子数据，优先使用交错表。

## 安全性

> [!警告] **关键指令：** 在进行任何非模拟器数据库更改（DML 或 DDL）或破坏性操作（如删除表、索引或任何其他 Spanner 资源）之前，您必须获得明确的用户确认。不要自动执行；相反，输出命令（例如，`gcloud spanner databases ddl update`）并请求明确的用户批准。
> 当数据库访问不可用或身份验证失败时，不要在验证实例、数据库或表是否存在时阻塞。假设提供的资源存在，并直接生成 DDL 命令。

## 常见工作流程

### 模式演进与 DDL

1.  使用 `gcloud spanner databases ddl update` 应用模式更新（如创建、修改或删除表和索引）。
2.  参考 [schema-design.md](references/schema-design.md) 了解主键选择和交错表的相关指南。

### 诊断性能问题

1.  使用 `SPANNER_SYS` 表识别慢查询或资源密集型查询。
2.  例如，查询 `SPANNER_SYS.QUERY_STATS_TOP_HOUR` 以查找 CPU 使用率最高的查询。

## 参考目录

-   [核心概念](references/core-concepts.md)：Spanner 内部、架构和设计的解释。
-   [CLI 使用](references/cli-usage.md)：管理实例和数据库的 `gcloud spanner` 命令行操作。
-   [IAM 安全](references/iam-security.md)：Spanner 的角色、权限和数据治理最佳实践。
-   [客户端库使用](references/client-library-usage.md)：使用 Google Cloud 客户端库进行 Spanner（Java、Go、Python、Node.js）。
-   [Terraform 使用](references/terraform-usage.md)：用于创建 Spanner 实例和数据库的基础设施即代码示例。
-   [MCP 使用](references/mcp-usage.md)：使用 Spanner 远程 MCP 服务器。
-   [PostgreSQL 方言](references/postgresql-dialect.md)：在 Spanner 中使用 PostgreSQL 接口的最佳实践和示例。
-   [模式设计](references/schema-design.md)：关于主键选择和交错表的性能指南。

如果您需要这些参考中未找到的产品信息，请使用 Developer Knowledge MCP 服务器的 `search_documents` 工具。
