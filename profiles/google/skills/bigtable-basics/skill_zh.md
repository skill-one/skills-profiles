# Bigtable 基础知识

这项技能提供了使用 Google Bigtable 进行管理和开发的核心工作流程和指导。

## 核心原则

-   **控制平面与数据平面：**
    -   使用 **`gcloud`** 执行控制平面操作：管理实例、集群、应用配置文件、备份和 IAM。创建表、逻辑视图、物化视图和授权视图。
    -   使用 **`cbt`** 执行数据平面操作：更新表、列族，以及读写数据。
-   **性能优先：** Bigtable 是一个 NoSQL 数据库。效率与行键设计紧密相关。始终要警告全表扫描的风险。
-   **客户端选择：** 对于生产用例，优先选择 **Java** 或 **Go**，因为它们比其他语言具有更好的性能和功能覆盖范围。
-   **可观察性：** 在诊断性能或热点问题时，**必须**将 **Key Visualizer**（通过 Cloud Console）作为主要的诊断工具，因为它提供了跨行键访问模式的最细粒度视图。这应随后通过 gcloud CLI 中的热表工具和表统计信息，以及 `cbt read` 下的 `include-stats=full` 选项来诊断慢查询。

> [!IMPORTANT] **安全规则：** 在进行非模拟器数据库更改之前，**必须**获得用户的明确确认。在提供修改数据库结构或数据的命令或说明时，**必须**提及此安全要求。

## 快速入门指南

### 1. 查询数据

使用 SQL 进行复杂的转换或聚合，并使用键值 API 进行简单的查询模式。*注意：在 `_key` 上使用精确匹配、前缀（`_key LIKE 'myprefix%'`）或范围谓词以避免昂贵的无界扫描。建议在可能的情况下，使用显式行范围（`_key BETWEEN 'start' AND 'end'`）作为前缀匹配的更高效的替代方案。*

如果由于多个无法全部包含在单个模式中的访问模式而无法避免昂贵的扫描（无论是无界扫描还是前缀或范围查询扫描大范围），请考虑以下两种选项之一：

-   如果查询将用于面向用户和/或延迟敏感的应用程序，请使用针对附加访问模式进行优化的连续物化视图。
-   如果次要访问模式不频繁，例如 ETL、机器学习模型训练或分析只读任务，请使用 Bigtable 数据增强。

### 2. 操作数据

使用键值 API 进行插入、更新、增量删除操作。SQL API 是只读的。

### 3. 数据模型定义（DDL）

SQL API 不支持 DDL 操作。表的创建、删除和更新应使用 gcloud CLI 进行。逻辑视图和连续物化视图定义为 SQL 查询，但必须使用 gcloud CLI 创建。

## 参考指南

-   **CLI 操作**：
    -   [infrastructure_management.md](references/infrastructure_management.md)：提供实例、集群和表模式。
    -   [cli_data_access.md](references/cli_data_access.md)：通过 `cbt` CLI 读写数据。
-   **设计与发现**：
    -   [schema_design.md](references/schema_design.md)：表和连续物化视图的行键和性能的最佳实践。
    -   [dataplex.md](references/dataplex.md)：Bigtable 资产的目录搜索。
-   **查询与代码**：
    -   [sql_guide.md](references/sql_guide.md)：通过 SQL 和 CLI 查询结构化行键。
    -   [client_libraries.md](references/client_libraries.md)：Go/Java/Python 的高性能代码模式。

## 常见工作流程

### 模式演进（DevOps）

1.  **优先使用 Terraform** 进行生产模式更改，以防止意外数据丢失。
2.  对于手动 `cbt` 更改，在提出任何修改建议之前，首先通过列出表的列族和 GC 策略来检查现有状态：

    ```bash
    cbt ls {table}
    ```

    如果需要修改，创建列族或更新 GC 策略：

    ```bash
    cbt createfamily {table} {family}
    cbt setgcpolicy {table} {family} "maxversions=5 AND maxage=30d"
    ```

3.  参考
    [infrastructure_management.md](references/infrastructure_management.md) 获取完整语法。

## 外部资源

*   [Cloud Bigtable 文档](https://cloud.google.com/bigtable/docs)
*   [Bigtable SQL 参考](https://cloud.google.com/bigtable/docs/googlesql-overview)
*   [cbt CLI 参考](https://cloud.google.com/bigtable/docs/cbt-reference)
*   [gcloud bigtable 参考](https://cloud.google.com/sdk/gcloud/reference/bigtable)
