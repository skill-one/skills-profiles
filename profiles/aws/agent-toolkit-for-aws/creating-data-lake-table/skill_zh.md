# 使用 Amazon S3 Tables 创建数据湖表

## 概述

Amazon S3 Tables 提供受管理的 Iceberg 表，具有自动压缩和快照管理功能。可通过 Athena 和 Iceberg 兼容引擎进行查询。

## 常见任务

连接时，您必须使用 AWS MCP 服务器工具，它们提供命令验证、沙盒执行和审计日志记录。如果 MCP 不可用，请回退到 AWS CLI。

## 决策指南

**创建之前，您必须检查已存在的内容：**

当用户提到数据库时，您必须运行 `aws glue get-tables --database-name <NAME>`。

| 您发现的内容 | 操作 |
|---------------|--------|
| 模糊的数据库名称（例如“我们的分析数据库”） | 您必须停止。委托给 `finding-data-lake-assets` 来解决。 |
| 具有相同名称的非 S3-Tables 表 | 您必须停止。委托给 `finding-data-lake-assets`。在用户确认之前，您不得创建。 |
| 具有相同名称的现有 S3 Tables 表 | 您必须检查架构是否匹配。如果兼容，请重用；如果用户确认，请重新创建。 |
| 没有匹配的表 | 继续创建（步骤 1-8）。 |
| 用户明确要求创建新的 S3 Tables 表 | 跳过检查，继续创建。 |

**创建路径：**

- **S3 中的现有数据**：创建空表（步骤 1-8），然后使用 `ingesting-into-data-lake` 技能。
- **Glue ETL 管道**：首先阅读 `references/table-creation-glue-etl.md`，然后执行步骤 1-6。
- **Lake Formation 访问控制**：搜索 AWS 文档中的 `"S3 Tables 与 Lake Formation 集成"`。

### 1. 验证依赖项

**约束：**

- 您必须检查 AWS MCP 服务器工具或 AWS CLI 是否可用，并在缺失时通知用户。
- 您必须确认目标 AWS 区域，并使用 `aws sts get-caller-identity` 验证凭证。

### 2. 理解架构

- **显式架构**：验证 Iceberg 类型。
- **松散描述**：询问列、类型、粒度。提出并确认。
- **现有的 S3 数据**：仅从文件标题中推断架构。首先创建空表，然后使用 `ingesting-into-data-lake` 技能。

**约束：**

- 您必须阅读 `references/best-practices.md` 了解 Iceberg 类型映射、分区和命名。
- 您必须提前要求所有必需的参数：表名、列、类型、分区策略。有关架构演化，请参阅 `references/athena-ddl-path.md`。
- 您必须使用所有小写名称——Glue 会拒绝混合大小写并返回 `GENERIC_INTERNAL_ERROR`。命名空间和表名不得包含连字符。
- 您应建议基于访问模式进行分区的列。

### 3. 创建表存储桶

名称：3-63 个字符，小写，数字，连字符。

```bash
aws s3tables create-table-bucket --name <BUCKET_NAME> --region <REGION>
```

捕获 `table-bucket-arn`。加密（默认为 SSE-S3，SSE-KMS）和存储类（STANDARD，INTELLIGENT_TIERING）在创建时设置。请参阅 `references/best-practices.md`。

**约束：**

- 您必须使用 `aws s3tables list-table-buckets` 检查现有存储桶，并要求用户选择或创建新的存储桶。
- 如果使用 SSE-KMS，KMS 密钥策略必须允许 S3 Tables 维护服务主体读取数据。搜索 AWS 文档中的 `"S3 Tables KMS 密钥策略"` 以获取所需的策略。
- 如果存储桶创建失败，请参阅 `references/best-practices.md` 了解常见错误。

### 4. 创建命名空间

```bash
aws s3tables create-namespace --table-bucket-arn <ARN> --namespace <NAMESPACE>
```

**约束：**

- 您必须首先列出现有的命名空间，并在相关时建议重用。
- 您必须使用小写名称且不包含连字符。

### 5. 创建 Glue 数据目录集成

检查 `s3tablescatalog` 是否存在（每个区域每个账户创建一次）：

```bash
aws glue get-catalog --catalog-id s3tablescatalog
```

如果未找到，则创建（需要 `glue:CreateCatalog`，`glue:passConnection`）：

```bash
aws glue create-catalog --name "s3tablescatalog" --catalog-input '{
  "FederatedCatalog": {
    "Identifier": "arn:aws:s3tables:<REGION>:<ACCOUNT_ID>:bucket/*",
    "ConnectionName": "aws:s3tables"
  },
  "CreateDatabaseDefaultPermissions": [{"Principal": {"DataLakePrincipalIdentifier": "IAM_ALLOWED_PRINCIPALS"}, "Permissions": ["ALL"]}],
  "CreateTableDefaultPermissions": [{"Principal": {"DataLakePrincipalIdentifier": "IAM_ALLOWED_PRINCIPALS"}, "Permissions": ["ALL"]}],
  "AllowFullTableExternalDataAccess": "True"
}'
```

使用 `aws glue get-catalogs --parent-catalog-id s3tablescatalog` 进行验证。

### 6. 配置访问控制

S3 Tables 使用 `s3tables:*` IAM 命名空间（不是 `s3:*`）。

**查询主体权限（存储桶策略）：**

- `s3tables:GetTableBucket`，`s3tables:GetNamespace`，`s3tables:GetTable`，`s3tables:GetTableMetadataLocation`，`s3tables:GetTableData`

**查询主体权限（IAM 策略）：**

- `glue:GetCatalog`，`glue:GetDatabase`，`glue:GetTable`

您必须针对正确的 ARN 模式进行范围限制。您必须阅读 `references/access-control.md` 以获取确切的资源 ARN。

**约束：**

- 您必须要求用户提供查询主体的 ARN。
- 您不得授予比必要更广泛的权限。
- 您不得自动创建 IAM 角色，请验证现有角色并指导用户。

### 7. 创建表

| 环境 | 路径 |
|---------|------|
| 默认（任何用户） | **S3 Tables API**（下方） |
| 用户特别希望 SQL DDL | **Athena DDL**（请参阅 `references/athena-ddl-path.md`） |
| Glue ETL 管道 | **Spark DDL** 通过 `--conf` 作业参数（不是 `spark.conf.set()`）。您必须阅读 `references/table-creation-glue-etl.md` 以获取 `--conf` 字符串。 |

**默认：S3 Tables API：**

```bash
aws s3tables create-table \
  --table-bucket-arn <ARN> \
  --namespace <NAMESPACE> \
  --name <TABLE_NAME> \
  --format ICEBERG \
  --metadata '<METADATA_JSON>'
```

元数据 JSON 必须嵌套在 `"iceberg"` 键下：

```json
{"iceberg":{"schema":{"fields":[
  {"name":"order_date","type":"date","required":true},
  {"name":"customer_id","type":"string","required":true},
  {"name":"amount","type":"double","required":false}
]},
"partitionSpec":{"fields":[
  {"sourceId":1,"fieldId":1000,"transform":"month","name":"order_date_month"}
]}}}
```

**约束：**

- `partitionSpec.sourceId` 必须引用有效的架构字段 ID。
- 创建后进行架构演化，请使用 Athena DDL。请参阅 `references/athena-ddl-path.md`。
- 您必须使用 `schemaV2` 处理复杂类型（列表、映射、结构）并具有显式字段 ID。请参阅 `references/best-practices.md`。
- 您应搜索 AWS 文档中的 `"IcebergPartitionField S3 Tables"` 以获取支持的分区转换。

### 8. 验证并确认

您必须使用 `aws s3tables get-table` 进行验证，并使用 `DESCRIBE <table_name>` 通过 Athena 确认可查询性，使用 `--query-execution-context '{"Catalog":"s3tablescatalog/<BUCKET_NAME>","Database":"<NAMESPACE>"}'`。不要将目录放入 SQL 中。提供摘要：存储桶 ARN、命名空间、表、架构、分区。

## 故障排除

| 错误 | 原因 | 解决方法 |
|-------|-------|-----|
| "Table location can not be specified" | CREATE TABLE 中的 LOCATION | 删除 LOCATION 子句。S3 Tables 自动管理存储。 |
| `AccessDeniedException` 与 `s3:*` 策略 | 使用 `s3:*` 而不是 `s3tables:*` | S3 Tables 使用 `s3tables:*` 命名空间。更新 IAM 策略。 |

## 其他资源

- [access-control.md](references/access-control.md) -- IAM 权限、ARN 模式、权限错误
- [best-practices.md](references/best-practices.md) -- Iceberg 类型、分区、命名、常见错误
- [athena-ddl-path.md](references/athena-ddl-path.md) -- Athena DDL、架构演化
- [table-creation-glue-etl.md](references/table-creation-glue-etl.md) -- 通过 Glue ETL 的 Spark DDL
- 加载数据：`ingesting-into-data-lake` 技能
