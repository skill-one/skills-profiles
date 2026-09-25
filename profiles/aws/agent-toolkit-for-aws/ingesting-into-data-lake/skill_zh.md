# 数据湖导入

将数据从源移动到数据湖中的可查询表格。此技能假定源连接（如果需要）已存在。对于 Glue 连接设置或故障排除，委托给 `connecting-to-data-source`。

## 哲学

**除非环境另有说明，否则默认使用 S3 表格。** S3 表格是新数据湖工作的推荐目标。如果用户的目录清单显示他们尚未采用 S3 表格，建议在他们的现有通用存储桶上使用标准 Iceberg，而不是强迫他们改变策略。

## 常见任务

连接时，你必须使用 AWS MCP 服务器工具执行命令——它们提供验证、沙盒执行和审计日志。如果 MCP 不可用，则回退到 AWS CLI。在执行每个步骤之前，你必须向用户解释。

## 工作流

### 1. 验证依赖项和上下文

- 你必须检查 AWS MCP 工具或 AWS CLI 是否可用，并在缺失时通知用户
- 你必须确认目标 AWS 区域，并使用 `aws sts get-caller-identity` 验证凭证
- 对于 SageMaker 统一工作室项目角色，请注意目标表格和连接可能仅限于项目范围内。有关调用者 ARN 检测模式，请参阅 `querying-data-lake`。

### 2. 分类源

| 用户说... | 源类型 | 参考 |
|---|---|---|
| "上传我的文件"、"本地 CSV"、"移动到 S3" | 本地文件 | [local-upload.md](references/local-upload.md) |
| "从 S3 加载"、"从 s3:// 导入 CSV/JSON/Parquet" | S3 文件 | [s3-files.md](references/s3-files.md) |
| "从 Oracle/Postgres/MySQL/SQL Server/Redshift/RDS/Aurora 导入" | JDBC | [jdbc-ingest.md](references/jdbc-ingest.md) |
| "从 Snowflake 拉取"、"Snowflake 表格到 S3" | Snowflake | [snowflake-ingest.md](references/snowflake-ingest.md) |
| "从 BigQuery 导入"、"GCP 分析到 S3" | BigQuery | [bigquery-ingest.md](references/bigquery-ingest.md) |
| "导出 DynamoDB"、"DynamoDB 到数据湖" | DynamoDB | [dynamodb-ingest.md](references/dynamodb-ingest.md) |
| "迁移 Glue 表格"、"将 Hive 转换为 Iceberg" | 目录迁移 | [catalog-migration.md](references/catalog-migration.md) |

如果用户提到 Salesforce、ServiceNow、SAP、MongoDB、Kafka 或其他 SaaS/流式源，则拒绝——这些在本版本中不受支持。

如果源表格由模糊或业务名称引用（例如，“迁移我们的订单表格”、“从销售仓库拉取”），则委托给 `finding-data-lake-assets` 在继续之前解决。

### 3. 确认连接是否存在（如果适用）

对于 JDBC、Snowflake 和 BigQuery 源，需要一个 Glue 连接。检查：

```bash
aws glue get-connection --name <CONNECTION_NAME> --region <REGION>
```

如果连接不存在，停止并委托给 `connecting-to-data-source` 创建和测试它。在验证连接之前，不要继续导入。

本地文件、S3 文件、DynamoDB 和目录迁移不需要 Glue 连接。

### 4. 明确目标

在创建或写入任何表格之前，你必须询问用户（或根据目录清单建议）：

- **数据库/命名空间**：是否存在特定的目标数据库？或者应该创建一个？
- **表格**：现有表格（追加/合并）还是新表格（委托给 `creating-data-lake-table`）？
- **格式**：S3 表格（默认）、标准 Iceberg 或原始 Parquet？

**感知目录的默认值：**

如果你已经运行过 `exploring-data-catalog` 或可以快速检查，请使用现有内容：

- 账户有一个 `s3tablescatalog` 联邦目录和活动的表格存储桶：建议 S3 表格
- 账户有通用存储桶和 Iceberg 表格，且没有使用 S3 表格：建议在他们的现有存储桶上使用标准 Iceberg
- 账户在 S3 上使用 Parquet/ORC 而没有 Iceberg 元数据：询问是否现在采用 Iceberg（建议是）或继续使用原始文件

不要强迫未采用 S3 表格的客户。请参阅 [iceberg-catalog-config-and-usage.md](references/iceberg-catalog-config-and-usage.md)。

**本步骤的委托：**

- 目标表格不存在 -> `creating-data-lake-table`
- 目标数据库由模糊术语命名 -> `finding-data-lake-assets`
- 用户不知道存在什么 -> `exploring-data-catalog`

### 5. 执行源工作流

阅读源特定参考并遵循其阶段。每个阶段都是自包含的，包含作业模板、注意事项和故障排除：

- 本地 / S3 / JDBC / Snowflake / BigQuery / DynamoDB / 目录迁移——每个源一个参考

常见的 Glue 5.1 或更高版本作业配置和 PySpark 模板在 [glue-job-config.md](references/glue-job-config.md) 和 [glue-job-scripts.md](references/glue-job-scripts.md) 中共享。

### 6. 验证

运行所有三个，不要跳过：

1. 行数与预期匹配（源与目标）
2. 关键列的空值检查
3. 抽查 3-5 个样本行

请参阅 [data-quality-validation.md](references/data-quality-validation.md)。

### 7. 调度（如果周期性）

对于周期性管道，创建一个具有 cron 调度的 Glue 触发器。请参阅 [testing-and-scheduling.md](references/testing-and-scheduling.md)。简单的单步管道使用 Glue 触发器；多步带分支的管道使用 MWAA。

## 参数路由

- 仅 S3 路径：推断一次性加载，从 S3 文件开始步骤 2
- 连接名称：从命名连接开始步骤 3
- 表格名称：开始步骤 4，询问这是源还是目标
- `--target` 标志：在步骤 4 中预填目标格式
- 无参数：交互式引导

## 注意事项

- S3 表格需要 Glue 5.1 或更高版本，并且 `--datalake-formats iceberg` 作业参数
- 所有 `spark.sql.catalog.*` 配置必须放在 `--conf` 作业参数中，绝不能放在 `spark.conf.set()` 中。否则，Glue 5.x 会抛出 `AnalysisException: Cannot modify the value of a static config`。请参阅 [iceberg-catalog-config-and-usage.md](references/iceberg-catalog-config-and-usage.md) 以获取正确的目录配置。
- S3 表格目录配置中必须包含 `warehouse` 参数。没有它，Spark 会因“无法派生默认存储库位置”而失败。
- S3 表格中的表格和列名必须全部小写
- `overwritePartitions()` 仅替换 DataFrame 中存在的分区——对于带删除的全量刷新，请使用 `createOrReplace()`
- 标准 Iceberg 目标必须包含 `LOCATION` 子句；S3 表格绝不能
- DynamoDB 不需要 Glue 连接——不要尝试创建一个
- 导入期间连接失败委托回 `connecting-to-data-source`；在本技能中不要调试网络/凭证
- 对于 SageMaker 统一工作室项目中的目标表格，确保项目角色在 Glue 作业运行之前具有对目标命名空间的写入权限

## 故障排除

| 错误 | 可能原因 | 操作 |
|---|---|---|
| S3 访问被拒绝 | 缺少 IAM 权限 | 检查 Glue 角色是否有 s3:GetObject、s3:PutObject |
| S3 表格访问被拒绝 | 缺少 s3tables:* 权限 | 向 Glue 角色添加 S3 表格内联策略 |
| CTAS 超时 | 数据集太大，Athena 无法处理 | 切换到 Glue ETL 或使用 WHERE 过滤器进行批处理 |
| JDBC 连接超时/认证失败 | 连接级问题 | 委托给 `connecting-to-data-source` |
| 吞吐量超限（DynamoDB） | 读取百分比过高 | 降低 `read.percent` 或使用原生导出 |

请参阅 [error-handling.md](references/error-handling.md) 以获取完整目录。

## 参考

### 源特定

- [local-upload.md](references/local-upload.md) -- 本地文件
- [s3-files.md](references/s3-files.md) -- S3 文件（CSV、JSON、Parquet、Avro、ORC）
- [jdbc-ingest.md](references/jdbc-ingest.md) -- Oracle、SQL Server、PostgreSQL、MySQL、RDS、Aurora、Redshift
- [snowflake-ingest.md](references/snowflake-ingest.md) -- Snowflake
- [bigquery-ingest.md](references/bigquery-ingest.md) -- BigQuery
- [dynamodb-ingest.md](references/dynamodb-ingest.md) -- DynamoDB（导出和 Glue 直接读取）
- [catalog-migration.md](references/catalog-migration.md) -- 现有 Glue 目录表格（Hive、自管理的 Iceberg）

### 跨领域

- [iceberg-catalog-config-and-usage.md](references/iceberg-catalog-config-and-usage.md) -- S3 表格、标准 Iceberg、原始文件：目录配置、引擎访问模式
- [glue-job-config.md](references/glue-job-config.md) -- 作业大小、监控、重试
- [glue-job-scripts.md](references/glue-job-scripts.md) -- PySpark 模板（追加、upsert、自定义 SQL、全量刷新）
- [incremental-loading.md](references/incremental-loading.md) -- 水印策略
- [testing-and-scheduling.md](references/testing-and-scheduling.md) -- Glue 触发器、MWAA
- [data-quality-validation.md](references/data-quality-validation.md) -- 行数、空值检查、Glue 数据质量
- [schema-evolution.md](references/schema-evolution.md) -- ALTER TABLE ADD COLUMNS、嵌套 JSON
- [type-transformations.md](references/type-transformations.md) -- 类型冲突解决
- [format-specific-loading.md](references/format-specific-loading.md) -- CSV/JSON/Parquet/Avro/ORC 特定
- [athena-loading.md](references/athena-loading.md) -- Athena INSERT INTO 作为简单加载回退
- [error-handling.md](references/error-handling.md) -- 导入错误（连接错误委托给 connecting-to-data-source）
- [upload-options.md](references/upload-options.md) -- aws s3 cp vs sync、multipart

### 迁移特定

- [ctas-patterns.md](references/ctas-patterns.md) -- Athena CTAS 语法和分区转换
- [glue-etl-migration.md](references/glue-etl-migration.md) -- 通过 Glue 5.1 或更高版本的 PySpark 进行大表格迁移
- [migration-validation.md](references/migration-validation.md) -- 完整验证清单
- [migration-troubleshooting.md](references/migration-troubleshooting.md) -- CTAS 失败、可见性、分区

### JDBC 特定

- [jdbc-schema-discovery.md](references/jdbc-schema-discovery.md) -- Crawler、直接检查、自定义 SQL
- [jdbc-performance.md](references/jdbc-performance.md) -- 并行读取、分区
