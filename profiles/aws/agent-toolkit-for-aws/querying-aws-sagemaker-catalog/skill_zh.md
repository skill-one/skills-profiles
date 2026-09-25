# 查询 AWS SageMaker 目录系统表

## 概述

**最适合与** [AWS MCP 服务器](https://docs.aws.amazon.com/aws-mcp/) 配合使用，以进行沙盒执行和审计日志记录。以下所有命令都使用 AWS CLI，并在任何配置了 AWS 凭证的环境中运行。

Amazon SageMaker 统一工作室（其目录功能在本文中称为 SageMaker 目录）将资产元数据导出为每日快照 Apache Iceberg 表，存储在 AWS 管理的 `aws-sagemaker-catalog` 表存储桶中。这使您能够对整个数据目录库存进行 SQL 查询——资产计数、治理差距、所有权审计和历史比较——而无需构建自定义 ETL。

数据按 `snapshot_time` 进行分区，每日导出一次（每个区域大约在午夜）。该表是只读的。

## 决策树

| 用户意图 | 使用此技能？ | 替代方案 |
|---|---|---|
| 目录状态 SQL 分析（计数、治理、趋势） | **是** | — |
| 历史比较（“上周目录发生了什么变化”） | **是** — 通过 `snapshot_time` 实现时间旅行 | — |
| 查找没有所有者或描述的资产 | **是** | — |
| 通过名称或概念查找特定表 | **否** | `finding-data-lake-assets` 或 Glue 发现 `search` |
| 交互式浏览/枚举目录 | **否** | `exploring-data-catalog` |
| 在表的*数据上*运行查询 | **否** | `querying-data-lake` |
| 管理目录元数据（添加描述、标签） | **否** | Glue 发现 `put-form-type` / `associate-glossary-terms` |

## 常见任务

### 1. 检查是否已配置

```bash
aws datazone get-data-export-configuration \
  --domain-identifier <DOMAIN_ID> \
  --region <REGION>
```

- 如果不存在域：`aws datazone list-domains --region <REGION>`
- 如果未启用导出：引导用户启用。
- 每个账户每个区域一个域。

验证表存储桶是否存在：

```bash
aws s3tables list-table-buckets --region <REGION> \
  --query "tableBuckets[?name=='aws-sagemaker-catalog']"
```

### 2. 启用

**使用 KMS 加密（推荐用于生产）：**

```bash
aws datazone put-data-export-configuration \
  --domain-identifier <DOMAIN_ID> \
  --region <REGION> \
  --enable-export \
  --encryption-configuration kmsKeyArn=<KMS_KEY_ARN>,sseAlgorithm=aws:kms
```

> **注意**：创建后无法更改加密。对于敏感的目录数据，始终指定 KMS。

不使用加密（仅用于快速测试）：

```bash
aws datazone put-data-export-configuration \
  --domain-identifier <DOMAIN_ID> \
  --region <REGION> \
  --enable-export
```

首次数据将在 24 小时内可用。请参阅：
[导出资产元数据](https://docs.aws.amazon.com/sagemaker-unified-studio/latest/userguide/export-asset-metadata.html)

### 3. 验证查询权限

需要：

- 在 Glue 中注册的 S3 Tables 联邦目录（`s3tablescatalog`）
- 对表授予 Lake Formation SELECT + DESCRIBE 权限

授予权限：

```bash
aws lakeformation grant-permissions \
  --principal DataLakePrincipalIdentifier=<ROLE_ARN> \
  --resource '{"Table": {"CatalogId": "<ACCOUNT>:s3tablescatalog/aws-sagemaker-catalog", "DatabaseName": "asset_metadata", "Name": "asset"}}' \
  --permissions DESCRIBE SELECT \
  --region <REGION>
```

### 4. 查询

**查询语法：**

```sql
"s3tablescatalog/aws-sagemaker-catalog"."asset_metadata"."asset"
```

**约束：**

- 您*必须*始终按 `snapshot_time` 过滤——否则，查询将扫描所有历史快照并返回重复项
- 您*必须*在执行前确认工作组和输出位置
- 默认使用 `DATE(snapshot_time) = CURRENT_DATE` 获取当前状态
- 您*应该*使用本文档中记录的关键列构建查询。如果您需要完整架构，请运行一次 `get-tables`：

  ```
  aws glue get-tables --catalog-id "<ACCOUNT>:s3tablescatalog/aws-sagemaker-catalog" --database-name "asset_metadata" --region <REGION>
  ```

**关键列：**

| 列名 | 包含内容 | 用途 |
|--------|--------------|-------|
| `snapshot_time` | 分区键——每日快照时间戳 | **始终在此列上过滤** |
| `asset_id` | 唯一的目录资产标识符 | 查找的主键 |
| `resource_type_enum` | GlueTable、RedshiftTable、S3Collection 等。 | 按资产类型过滤 |
| `resource_id` | ARN 或原生标识符 | 与源系统交叉引用 |
| `asset_name` | 商业友好名称 | 显示、搜索 |
| `resource_name` | 技术名称（表名、前缀） | 过滤 |
| `business_description` | 商业上下文（如果未提供则为 NULL） | 治理差距 |
| `extended_metadata` | `map<string,string>` — 灵活的键值属性 | 使用括号表示法：`extended_metadata['owningEntityId']` |
| `asset_created_time` | 资产首次出现在目录中的时间 | 增长分析 |
| `asset_updated_time` | 最后修改时间 | 新鲜度检查 |

**当前目录状态：**

```sql
SELECT resource_type_enum, COUNT(*) as count
FROM "s3tablescatalog/aws-sagemaker-catalog"."asset_metadata"."asset"
WHERE DATE(snapshot_time) = CURRENT_DATE
GROUP BY resource_type_enum
ORDER BY count DESC;
```

**没有业务描述的资产：**

```sql
SELECT asset_name, resource_name, resource_type_enum, account_id
FROM "s3tablescatalog/aws-sagemaker-catalog"."asset_metadata"."asset"
WHERE DATE(snapshot_time) = CURRENT_DATE
  AND business_description IS NULL;
```

**过去 30 天的资产增长：**

```sql
SELECT DATE(snapshot_time) as date, COUNT(*) as total_assets
FROM "s3tablescatalog/aws-sagemaker-catalog"."asset_metadata"."asset"
WHERE DATE(snapshot_time) >= CURRENT_DATE - INTERVAL '30' DAY
GROUP BY DATE(snapshot_time)
ORDER BY date DESC;
```

**时间旅行——比较当前与 7 天前（新增描述）：**

```sql
SELECT t.asset_id, t.resource_name,
       p.business_description as before,
       t.business_description as now
FROM "s3tablescatalog/aws-sagemaker-catalog"."asset_metadata"."asset" t
JOIN "s3tablescatalog/aws-sagemaker-catalog"."asset_metadata"."asset" p
  ON t.asset_id = p.asset_id
WHERE DATE(t.snapshot_time) = CURRENT_DATE
  AND DATE(p.snapshot_time) = CURRENT_DATE - INTERVAL '7' DAY
  AND p.business_description IS NULL
  AND t.business_description IS NOT NULL;
```

**按所有者分类的资产：**

```sql
SELECT extended_metadata['owningEntityId'] as owner, COUNT(*) as count
FROM "s3tablescatalog/aws-sagemaker-catalog"."asset_metadata"."asset"
WHERE DATE(snapshot_time) = CURRENT_DATE
  AND extended_metadata['owningEntityId'] IS NOT NULL
GROUP BY extended_metadata['owningEntityId']
ORDER BY count DESC;
```

**按元数据表单字段过滤：**

```sql
SELECT *
FROM "s3tablescatalog/aws-sagemaker-catalog"."asset_metadata"."asset"
WHERE DATE(snapshot_time) = CURRENT_DATE
  AND extended_metadata['<metadata-form-name>.<field-name>'] = '<field-value>';
```

## 关键行为

- **每日快照** — 每个区域大约在午夜导出
- **始终按 `snapshot_time` 过滤** — 否则您将获得所有历史记录（重复项、慢）
- **每个账户每个区域一个域** — 要切换域，请先删除配置
- **除 S3 Tables 存储和 Athena 查询外无额外费用**
- **只读** — 要更新资产元数据，请使用 Glue 发现 API 或 SageMaker 统一工作室

## 故障排除

| 错误 | 原因 | 解决方法 |
|-------|-------|-----|
| `aws-sagemaker-catalog` 存储桶未找到 | 导出未启用 | 运行 `put-data-export-configuration --enable-export` |
| 使用 `CURRENT_DATE` 时结果为空 | 首次导出尚未运行（最多需要 24 小时） | 等待；尝试昨天的日期 |
| 查询时出现 `AccessDenied` | 缺少 Lake Formation 授权 | 对表授予 SELECT + DESCRIBE 权限 |
| `CATALOG_NOT_FOUND` | S3 Tables 未在 Glue 中注册 | 启用集成：S3 控制台 > 表存储桶 > 启用集成 |
| 结果中出现重复行 | 缺少 `snapshot_time` 过滤 | 添加 `WHERE DATE(snapshot_time) = CURRENT_DATE` |
| `extended_metadata` 键返回 NULL | 该资产不存在该键 | 检查可用键：`SELECT DISTINCT key FROM ... CROSS JOIN UNNEST(map_keys(extended_metadata)) AS t(key) WHERE DATE(snapshot_time) = CURRENT_DATE` |
| 无法更新导出加密 | 创建时仅设置加密 | 删除并重新创建导出配置 |

## 安全注意事项

**数据敏感性**：目录元数据会暴露组织结构，包括资产名称、所有权、账户 ID、命名约定和内部资源标识符。默认情况下，将查询结果视为敏感数据。

**静态加密**：创建导出配置时始终启用 KMS 加密。创建后无法更改加密。此外，请对您的 Athena 工作组输出存储桶配置 SSE-KMS。

**最小权限访问**：仅对需要目录分析的角色授予 Lake Formation SELECT + DESCRIBE 权限，避免授予对整个 `aws-sagemaker-catalog` 存储桶的访问权限。

**审计跟踪**：为 DataZone (`PutDataExportConfiguration`, `GetDataExportConfiguration`)、Athena (`StartQueryExecution`, `GetQueryResults`) 和 S3 Tables API 调用启用 CloudTrail 日志记录，以跟踪谁查询了目录元数据。

**凭证卫生**：使用具有临时凭证的 IAM 角色进行查询。避免为访问目录元数据的用户使用长期有效的访问密钥。当不再需要访问权限时，请缩小范围或旋转主体。

## 其他资源

- [导出资产元数据](https://docs.aws.amazon.com/sagemaker-unified-studio/latest/userguide/export-asset-metadata.html)
- [资产表架构](https://docs.aws.amazon.com/sagemaker-unified-studio/latest/userguide/export-asset-metadata.html#asset-table-schema)
- [将 S3 Tables 与分析服务集成](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-tables-integrating-aws.html)
- [Lake Formation 权限](https://docs.aws.amazon.com/lake-formation/latest/dg/granting-catalog-permissions.html)
