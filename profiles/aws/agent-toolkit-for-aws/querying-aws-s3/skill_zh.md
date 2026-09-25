# 查询 AWS S3 系统表

## 概述

**最适合** [AWS MCP 服务器](https://docs.aws.amazon.com/agent-toolkit/latest/userguide/getting-started-aws-mcp-server.html) 进行沙盒执行和审计日志记录。以下所有命令都使用 AWS CLI，并在任何配置了 AWS 凭证的环境中工作。使用 IAM 角色或临时凭证；避免使用长期有效的访问密钥。

Amazon S3 元数据提供持续更新的 Apache Iceberg 表格，捕获通用存储桶的对象级元数据。S3 存储透镜导出聚合的存储和活动指标作为 Iceberg 表格。两者都是只读的，存储在 AWS 管理的 `aws-s3` 表格存储桶中，并通过 Amazon Athena 可查询。

系统表格优先于原始 S3 API (`list-objects-v2`, `head-object`)，因为：

- `list-objects-v2` 每页分页 1000 个对象 — 对于大型存储桶（数百万或数十亿个对象）效率低下。清单表格在任何规模下都以秒为单位回答 `SELECT COUNT(*)`。
- `list-objects-v2` 无法识别上传对象的用户、IP 地址或删除时间。只有日志表格具有 `requester`、`source_ip_address` 和删除事件跟踪。
- 通过标签过滤需要每个对象调用 `get-object-tagging`。清单表格将 `object_tags` 作为可查询的映射列。

## 决策树

| 用户意图 | 使用此技能？ | 表格 | 替代方案 |
|---|---|---|---|
| 我的存储桶中有多少对象 | **是** | inventory | — |
| 最近上传/删除了什么 | **是** | journal | — |
| 谁编写/删除了对象（审计） | **是** | journal (requester, source_ip) | — |
| 存储类别分解 | **是** | inventory | — |
| 通过标签或用户元数据查找对象 | **是** | inventory | — |
| 搜索注释内容 | **是** | annotation | 单个对象 → 直接 API `get-object-annotation` |
| 写入/更新注释 | **否** | — | 直接 API: `put-object-annotation`（表格是只读的） |
| 查询对象*内部*的数据 | **否** | — | `querying-data-lake` |
| 存储桶级存储指标/趋势 | **是** | Storage Lens 表格 | — |
| 启用元数据跟踪 | **是** | 请参阅启用部分 | — |

## 常见任务

### 1. 检查是否已配置

查询之前，请确认目标存储桶已启用 S3 元数据。

```bash
aws s3api get-bucket-metadata-configuration --bucket <BUCKET> --region <REGION>
```

**解释响应:**

- `MetadataConfigurationNotFound` 错误 → 未启用。请参阅下方的启用部分。
- `TableStatus: ACTIVE` → 可查询。
- `TableStatus: BACKFILLING` → 可查询，但清单可能不完整。
- `TableStatus: FAILED` → 检查错误字段（通常为 IAM）。

**对于存储透镜:**

```bash
aws s3control get-storage-lens-configuration --account-id <ACCOUNT> --config-id <CONFIG_ID> --region <REGION>
```

查找 `DataExport.StorageLensTableDestination.IsEnabled: true`。

### 2. 启用（如果未配置）

**在存储桶上启用 S3 元数据:**

```bash
aws s3api create-bucket-metadata-configuration \
  --bucket <BUCKET> \
  --region <REGION> \
  --metadata-configuration '{
    "JournalTableConfiguration": {"RecordExpiration": {"Expiration": "DISABLED"}},
    "InventoryTableConfiguration": {"ConfigurationState": "ENABLED"}
  }'
```

要同时启用注释（需要服务角色）：

```bash
aws s3api create-bucket-metadata-configuration \
  --bucket <BUCKET> \
  --region <REGION> \
  --metadata-configuration '{
    "JournalTableConfiguration": {"RecordExpiration": {"Expiration": "ENABLED", "Days": 90}},
    "InventoryTableConfiguration": {"ConfigurationState": "ENABLED"},
    "AnnotationTableConfiguration": {"ConfigurationState": "ENABLED", "Role": "<ROLE_ARN>"}
  }'
```

**启用存储透镜 S3 表格导出:**

```bash
aws s3control put-storage-lens-configuration \
  --account-id <ACCOUNT> \
  --config-id <CONFIG_ID> \
  --region <REGION> \
  --storage-lens-configuration '{
    "Id": "<CONFIG_ID>",
    "IsEnabled": true,
    "AccountLevel": {"BucketLevel": {}},
    "DataExport": {
      "StorageLensTableDestination": {"IsEnabled": true}
    }
  }'
```

**在 Glue 中注册 S3 表格联合目录**（Athena 访问所需）：

```bash
aws glue create-catalog --region <REGION> --cli-input-json '{
  "Name": "s3tablescatalog",
  "CatalogInput": {
    "FederatedCatalog": {
      "Identifier": "arn:aws:s3tables:<REGION>:<ACCOUNT>:bucket/*",
      "ConnectionName": "aws:s3tables"
    }
  }
}'
```

有关设置权限和 IAM 角色要求的详细信息，请参阅下方的“安全注意事项”。

### 3. 验证权限

查询需要：

- Athena 执行权限
- S3 表格读取权限（请参阅安全注意事项中的最小权限策略）
- 在 Glue 中注册的 S3 表格联合目录（`s3tablescatalog`）
- 配置了输出位置 SSE-KMS 加密的 Athena 工作组

如果出现 `CATALOG_NOT_FOUND` 错误，则 Glue 集成可能未启用。请参阅：
[将 S3 表格与 AWS 分析服务集成](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-tables-integrating-aws.html)

### 4. 确定目标表格

**S3 元数据表格** — 命名空间为 `b_<bucket-name>`：

| 表格 | 它捕获的内容 |
|-------|-----------------|
| `journal` | 事件日志 — 每个 CREATE、DELETE、UPDATE_METADATA 和注释事件。近实时。 |
| `inventory` | 当前状态 — 每个对象一行（最新版本）。1 小时内更新。 |
| `annotation` | 注释有效负载 — `text_value` 列包含完整内容。近实时。 |

**存储透镜表格** — 命名空间为 `lens_<config-id>_exp`：

| 表格 | 它捕获的内容 |
|-------|-----------------|
| `default_storage_metrics` | 每个存储桶/前缀：对象计数、大小、存储类别分解。每日。 |
| `default_activity_metrics` | 每个存储桶/前缀：GET/PUT/DELETE 请求计数。每日。 |
| `bucket_property_metrics` | 存储桶配置：版本控制、加密、生命周期设置。每日。 |

### 5. 查询

**查询语法:**

```sql
"s3tablescatalog/aws-s3"."<namespace>"."<table>"
```

**约束:**

- 您必须在使用前确认工作组和输出位置
- 您必须确保 Athena 工作组强制对查询结果进行 SSE-KMS 加密
- 您必须警告用户表格是只读的 — 没有 INSERT/UPDATE/DELETE
- 您应该使用本技能中记录的键列来构建查询。如果您需要完整架构（例如，AWS 添加了新列），请在任何单个命名空间上运行一次 `get-tables` — 相同类型的所有实例的架构都是相同的：

  ```
  aws glue get-tables --catalog-id "<ACCOUNT>:s3tablescatalog/aws-s3" --database-name "<namespace>" --region <REGION>
  ```

**日志 — 审计谁更改了什么:**

```sql
SELECT key, record_type, record_timestamp, requester, source_ip_address
FROM "s3tablescatalog/aws-s3"."b_<bucket>"."journal"
WHERE record_type = 'DELETE'
  AND record_timestamp > current_timestamp - interval '24' hour
ORDER BY record_timestamp DESC;
```

**日志 — 跟踪注释事件:**

```sql
SELECT key, record_type, annotation.name, record_timestamp
FROM "s3tablescatalog/aws-s3"."b_<bucket>"."journal"
WHERE record_type IN ('CREATE_ANNOTATION', 'DELETE_ANNOTATION', 'UPDATE_ANNOTATION_METADATA')
ORDER BY record_timestamp DESC LIMIT 20;
```

**清单 — 通过存储类别查找对象:**

```sql
SELECT key, size, storage_class, last_modified_date
FROM "s3tablescatalog/aws-s3"."b_<bucket>"."inventory"
WHERE storage_class = 'GLACIER'
ORDER BY size DESC LIMIT 50;
```

**清单 — 通过标签查找对象:**

```sql
SELECT key, size, object_tags
FROM "s3tablescatalog/aws-s3"."b_<bucket>"."inventory"
WHERE object_tags['environment'] = 'staging';
```

**注释 — 搜索跨有效负载:**

```sql
SELECT object_key, name, text_value
FROM "s3tablescatalog/aws-s3"."b_<bucket>"."annotation"
WHERE text_value LIKE '%error%';
```

**注释 — 提取 JSON 字段:**

```sql
SELECT object_key, json_extract_scalar(text_value, '$.status') as status
FROM "s3tablescatalog/aws-s3"."b_<bucket>"."annotation"
WHERE name = 'pipeline_status'
  AND json_extract_scalar(text_value, '$.status') = 'FAILED';
```

**存储透镜 — 存储分布:**

```sql
SELECT *
FROM "s3tablescatalog/aws-s3"."lens_<config-id>_exp"."default_storage_metrics"
LIMIT 20;
```

### 路由：Athena vs 直接 API

| 情景 | 使用 |
|----------|-----|
| 单个已知对象 + 注释名称 | 直接 API: `get-object-annotation` |
| 跨多个对象进行聚合/计数 | Athena 在注释或清单表格上 |
| 跨注释有效负载进行全文搜索 | Athena 使用 `LIKE` 或 `json_extract_scalar` |
| 写入/更新注释 | 直接 API: `put-object-annotation`（表格是只读的） |
| 存储桶上未配置功能 | 直接 API 循环（`list-objects-v2` + `head-object`）；建议启用 S3 元数据 |

## 故障排除

| 错误 | 原因 | 解决方法 |
|-------|-------|-----|
| `CATALOG_NOT_FOUND` | S3 表格未在 Glue 中注册 | 启用集成：S3 控制台 > 表格存储桶 > 启用集成 |
| 日志结果为空 | 功能刚刚启用；尚未记录任何事件 | 上传/删除一个对象并等待 ~1 分钟 |
| 清单结果为空 | 表格仍为 `BACKFILLING` | 检查状态；等待 ACTIVE（取决于对象数量，分钟到小时不等） |
| 查询表格时 `AccessDenied` | 缺少 `s3tables:GetTable` 或 `GetTableMetadataLocation` | 请参阅下方的安全注意事项 |
| 命名空间错误 | 存储桶名称包含点 | 点被转换为命名空间中的下划线：`my.bucket` → `b_my_bucket` |
| 无存储透镜数据 | 首次交付最多需要 48 小时 | 等待；无历史回填 |

## 安全注意事项

### 最小权限 IAM 策略

将权限范围到特定的表格存储桶 ARN，而不是使用通配符：

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3tables:GetTable",
        "s3tables:GetTableMetadataLocation",
        "s3tables:GetTableData",
        "s3tables:GetNamespace",
        "s3tables:ListTables",
        "s3tables:ListNamespaces",
        "s3tables:GetTableBucket"
      ],
      "Resource": [
        "arn:aws:s3tables:<REGION>:<ACCOUNT>:bucket/aws-s3",
        "arn:aws:s3tables:<REGION>:<ACCOUNT>:bucket/aws-s3/*"
      ]
    }
  ]
}
```

### 数据敏感性

日志查询结果可能包含敏感字段：

- `requester` — 进行请求的 AWS 账户 ID 或服务主体
- `source_ip_address` — 请求者的 IP 地址

包含这些字段的查询结果应存储在加密的、受访问控制的存储位置。避免记录或共享包含 IP 地址或主体标识符的原始查询输出。

### 查询结果加密

配置 Athena 工作组使用 `EncryptionConfiguration` 对查询结果进行静态加密：

```json
{
  "ResultConfiguration": {
    "EncryptionConfiguration": {
      "EncryptionOption": "SSE_KMS",
      "KmsKey": "arn:aws:kms:<REGION>:<ACCOUNT>:key/<KEY_ID>"
    }
  }
}
```

### 审计跟踪

为 Athena (`StartQueryExecution`, `GetQueryResults`) 和 S3 表格 (`s3tables:GetTableData`) API 调用启用 CloudTrail 日志记录，以维护谁查询了哪些元数据的审计跟踪。确保 CloudTrail 日志使用 SSE-KMS 加密，并存储在启用了访问日志记录的存储桶中。

## 其他资源

- [S3 元数据概述](https://docs.aws.amazon.com/AmazonS3/latest/userguide/metadata-tables-overview.html)
- [日志表格架构](https://docs.aws.amazon.com/AmazonS3/latest/userguide/metadata-tables-schema.html)
- [清单表格架构](https://docs.aws.amazon.com/AmazonS3/latest/userguide/metadata-tables-inventory-schema.html)
- [示例元数据查询](https://docs.aws.amazon.com/AmazonS3/latest/userguide/metadata-tables-example-queries.html)
- [S3 注释概述](https://docs.aws.amazon.com/AmazonS3/latest/userguide/annotations-overview.html)
- [存储透镜 S3 表格导出](https://docs.aws.amazon.com/AmazonS3/latest/userguide/storage-lens-s3-tables-naming.html)
- [设置权限](https://docs.aws.amazon.com/AmazonS3/latest/userguide/metadata-tables-permissions.html)
- [将 S3 表格与 AWS 分析服务集成](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-tables-integrating-aws.html)
