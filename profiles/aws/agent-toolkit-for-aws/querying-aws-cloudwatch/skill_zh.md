# 查询 AWS CloudWatch 系统表

## 概述

**最适合**与 [AWS MCP 服务器](https://docs.aws.amazon.com/aws-mcp/) 配合使用，用于沙盒执行和审计日志记录。以下所有命令都使用 AWS CLI，并在任何配置了 AWS 凭证的环境中运行。

CloudWatch 日志 S3 表集成将日志数据导出为 Apache Iceberg 表，存储在 AWS 管理的 `aws-cloudwatch` 表存储桶中。这可以通过 Amazon Athena 进行 SQL 分析，并将日志数据与非 CloudWatch 数据（S3 元数据、业务表等）相关联。除 CloudWatch 摄入定价外，无需额外存储费用。

## 决策树

| 用户意图 | 使用此技能？ | 替代方案 |
|---|---|---|
| 在大量日志数据上运行 SQL | **是** | — |
| 将日志与 S3 元数据或其他表相关联 | **是** — 跨目录连接 | — |
| 快速日志搜索 / 模式匹配 | **否** | CloudWatch 日志洞察（适用于临时查询） |
| 实时日志流式传输/跟踪 | **否** | CloudWatch 日志控制台或 `logs filter-log-events` |
| 在日志模式上设置警报 | **否** | CloudWatch 指标过滤器 / 警报 |
| 查询集成启用前的历史日志 | **否** | CloudWatch 日志（S3 表中无回填） |

## 支持的数据源

通过 S3 表集成，可以使用以下数据源。每个数据源在 SQL 查询中使用一个命名空间模式。并非所有 AWS 提供的数据源在所有区域都可用；请检查 CloudWatch 控制台的“数据源”选项卡以获取当前可用性。

| 数据源 | 命名空间模式 | 常见用例 |
|---|---|---|
| VPC 流日志 | `amazon_vpc__flow` | 网络流量分析、被拒绝的连接 |
| WAF 日志 | `aws_waf__logs` | 被阻止的请求、规则命中分析 |
| CloudFront 访问日志 | `amazon_cloudfront__access` | CDN 流量模式、错误率 |
| Route 53 解析器查询日志 | `amazon_route53resolver__query` | DNS 查询分析 |
| 网络防火墙日志 | `aws_networkfirewall__logs` | 防火墙规则命中、丢弃流量 |
| EKS 审计日志 | `amazon_eks__audit` | Kubernetes API 审计跟踪 |
| 验证访问日志 | `amazon_verifiedaccess__logs` | 零信任访问决策 |
| SES 邮件日志 | `amazon_ses__mail` | 邮件投递/退回跟踪 |
| VPC Lattice 访问日志 | `amazon_vpclattice__access` | 服务间访问模式 |
| Step Functions 日志 | `aws_stepfunctions__logs` | 工作流执行调试 |
| 全球加速器流日志 | `aws_globalaccelerator__flow` | 全球网络流量 |
| NLB 访问日志 | `elastic_load_balancing__nlb_access` | 负载均衡器请求跟踪 |
| Shield 日志 | `aws_shield__logs` | DDoS 缓解事件 |
| Cognito 日志 | `amazon_cognito__logs` | 身份验证/身份操作 |
| ElastiCache 日志 | `amazon_elasticache__logs` | Redis 慢日志、引擎日志 |
| SageMaker 日志 | `amazon_sagemaker__logs` | 机器学习训练/推理事件 |
| WorkMail 审计日志 | `amazon_workmail__audit` | 邮件安全/合规 |
| Bedrock Agent 日志 | `aws_bedrock_agent_core__logs` | AI 代理调用 |
| 客户 VPN 日志 | `aws_client_vpn__connections` | VPN 连接跟踪 |
| 实体解析日志 | `aws_entity_resolution__logs` | 记录匹配操作 |
| MediaPackage 访问日志 | `aws_elemental_mediapackage__access` | 流媒体交付指标 |
| MediaTailor 日志 | `aws_elemental_mediatailor__logs` | 广告插入事件 |
| 转发家族日志 | `aws_transfer_family__logs` | SFTP/FTPS 文件传输跟踪 |
| 站点到站点 VPN 日志 | `aws_site_to_site_vpn__logs` | VPN 隧道诊断 |

> **注意**：此表列出了 24 个最常查询的数据源。集成总共支持 43+ 个 AWS 提供的数据源。使用 `list-namespaces` 在 `aws-cloudwatch` 存储桶上发现您账户中所有可用的数据源。命名空间模式遵循 `<服务>__<类型>` 的约定。

## 常见任务

### 1. 检查配置

```bash
# 检查是否存在 aws-cloudwatch 表存储桶
aws s3tables list-table-buckets --region <REGION> \
  --query "tableBuckets[?name=='aws-cloudwatch']"
```

- 空结果 → 集成未启用。引导用户完成设置。
- 存储桶存在但无命名空间 → 集成已启用但尚未捕获日志数据（仅捕获关联后的事件）。

列出可用表：

```bash
aws s3tables list-namespaces --table-bucket-arn arn:aws:s3tables:<REGION>:<ACCOUNT>:bucket/aws-cloudwatch --region <REGION>

aws s3tables list-tables --table-bucket-arn arn:aws:s3tables:<REGION>:<ACCOUNT>:bucket/aws-cloudwatch --namespace <NAMESPACE> --region <REGION>
```

### 2. 启用/配置

**创建集成：**

```bash
aws observabilityadmin create-s3-table-integration \
  --region <REGION> \
  --encryption '{"SseAlgorithm": "aws:kms", "KmsKeyArn": "<KMS_KEY_ARN>"}' \
  --role-arn <SERVICE_ROLE_ARN>
```

**关联特定数据源（推荐）：**

```bash
aws logs associate-source-to-s3-table-integration \
  --region <REGION> \
  --integration-arn <INTEGRATION_ARN> \
  --data-source '{"name": "<source-name>", "type": "<source-type>"}'
```

**关联所有数据源（通配符）：**

> ⚠️ **警告**：通配符关联会将所有当前和未来的数据源交付到 S3 Tables。使用特定关联以更严格控制哪些日志数据会出现在可查询的表中。

```bash
aws logs associate-source-to-s3-table-integration \
  --region <REGION> \
  --integration-arn <INTEGRATION_ARN> \
  --data-source '{"name": "*", "type": "*"}'
```

有关 IAM 要求（服务角色信任策略、权限策略、条件键），请参阅下文中的“安全注意事项”。

### 3. 验证查询权限

需要：

- S3 Tables 联邦目录在 Glue 中注册（`s3tablescatalog`）
- Lake Formation SELECT + DESCRIBE 权限（或支持区域的 IAM 模式）
- Athena 执行权限

授予权限：

```bash
aws lakeformation grant-permissions \
  --principal DataLakePrincipalIdentifier=<ROLE_ARN> \
  --resource '{"Table": {"CatalogId": "<ACCOUNT>:s3tablescatalog/aws-cloudwatch", "DatabaseName": "<NAMESPACE>", "Name": "<TABLE>"}}' \
  --permissions DESCRIBE SELECT \
  --region <REGION>
```

### 4. 查询

**查询语法：**

```sql
"s3tablescatalog/aws-cloudwatch"."<namespace>"."<table>"
```

**约束：**

- 您**必须始终**在编写任何 SQL 查询之前，在目标命名空间上运行 `get-tables` 并将命令包含在响应中——架构因数据源而异。即使您已经知道可能的架构，也**永远不要跳过**此步骤。在目标命名空间上运行一次 `get-tables`（一次调用返回所有表+列+类型+描述）：

  ```
  aws glue get-tables --catalog-id "<ACCOUNT>:s3tablescatalog/aws-cloudwatch" --database-name "<namespace>" --region <REGION>
  ```

- 您**必须**在执行前确认工作组和输出位置
- 您**必须**告知用户只有关联后的日志才可用（无回填）

**示例——VPC 流日志被拒绝的流量：**

```sql
SELECT srcaddr, dstaddr, dstport, protocol, packets, bytes
FROM "s3tablescatalog/aws-cloudwatch"."amazon_vpc__flow"."<table>"
WHERE action = 'REJECT'
ORDER BY bytes DESC
LIMIT 50;
```

**示例——WAF 被阻止的请求：**

```sql
SELECT timestamp, action, terminatingRuleId, httpSourceId
FROM "s3tablescatalog/aws-cloudwatch"."aws_waf__logs"."<table>"
WHERE action = 'BLOCK'
ORDER BY timestamp DESC
LIMIT 50;
```

**示例——将 VPC 流日志与 S3 对象元数据相关联：**

```sql
SELECT f.srcaddr, f.dstaddr, f.bytes, j.key, j.record_type
FROM "s3tablescatalog/aws-cloudwatch"."amazon_vpc__flow"."<table>" f
JOIN "s3tablescatalog/aws-s3"."b_<bucket>"."journal" j
  ON f.srcaddr = j.source_ip_address
WHERE j.record_type = 'CREATE'
  AND f.action = 'ACCEPT';
```

## 关键行为

- **无回填**——仅关联后的新日志事件会交付到 S3 Tables
- **保留遵循日志组**——当日志组保留期过期时，数据将从表中删除
- **删除日志组**会从 S3 表中删除其数据
- **无额外存储费用**——包含在 CloudWatch 定价中
- **架构按数据源区分**——在构建复杂查询前，始终在目标命名空间上运行 `get-tables`

## 故障排除

| 错误 | 原因 | 解决方法 |
|-------|-------|-----|
| `aws-cloudwatch` 存储桶未找到 | 集成未创建 | 运行 `create-s3-table-integration` |
| 存储桶存在但无命名空间 | 未关联数据源，或关联后无日志流量 | 关联源；生成流量 |
| Athena 中的 `CATALOG_NOT_FOUND` | S3 Tables 未在 Glue 中注册 | 启用集成：S3 控制台 > 表存储桶 > 启用集成 |
| `AccessDenied` 查询 | 缺少 Lake Formation 授权或 IAM 权限 | 见下文“安全注意事项” |
| 空结果 | 日志仅在关联后生成；无回填 | 确认关联存在且日志源正在生成数据 |
| 架构不匹配/列未找到 | AWS 更新了日志类型架构 | 在命名空间上运行 `get-tables` 获取当前列 |

## 安全注意事项

### 服务角色信任策略

服务角色必须允许 `logs.amazonaws.com` 假设它。始终包含 `aws:SourceAccount` 和 `aws:SourceArn` 条件键以防止混淆代理攻击：

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "logs.amazonaws.com"
            },
            "Action": "sts:AssumeRole",
            "Condition": {
                "StringEquals": {
                    "aws:SourceAccount": "<ACCOUNT>"
                },
                "ArnLike": {
                    "aws:SourceArn": ["arn:aws:logs:<REGION>:<ACCOUNT>:log-group:<LOG_GROUP_NAME>"]
                }
            }
        }
    ]
}
```

### 服务角色权限策略

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": ["logs:integrateWithS3Table"],
            "Resource": ["arn:aws:logs:<REGION>:<ACCOUNT>:log-group:<LOG_GROUP_NAME>"],
            "Condition": {
                "StringEquals": {
                    "aws:ResourceAccount": "<ACCOUNT>"
                }
            }
        }
    ]
}
```

### KMS 密钥策略（用于加密数据）

如果使用客户管理的 KMS 密钥，请授予服务主体访问权限：

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "EnableSystemTablesKeyUsage",
            "Effect": "Allow",
            "Principal": {"Service": "systemtables.cloudwatch.amazonaws.com"},
            "Action": ["kms:DescribeKey", "kms:GenerateDataKey", "kms:Decrypt"],
            "Resource": "arn:aws:kms:<REGION>:<ACCOUNT>:key/<KEY_ID>",
            "Condition": {"StringEquals": {"aws:SourceAccount": "<ACCOUNT>"}}
        },
        {
            "Sid": "EnableS3TablesMaintenanceKeyUsage",
            "Effect": "Allow",
            "Principal": {"Service": "maintenance.s3tables.amazonaws.com"},
            "Action": ["kms:GenerateDataKey", "kms:Decrypt"],
            "Resource": "arn:aws:kms:<REGION>:<ACCOUNT>:key/<KEY_ID>",
            "Condition": {"StringLike": {"kms:EncryptionContext:aws:s3:arn": "<TABLE_OR_TABLE_BUCKET_ARN>/*"}}
        }
    ]
}
```

### 数据敏感性

日志数据可能包含 PII，包括 IP 地址、用户代理、请求参数和身份验证令牌。默认情况下，将所有导出的日志表视为敏感数据。

### 访问控制最佳实践

- 使用 Lake Formation 列级安全来限制对敏感列（例如 `srcaddr`、`source_ip_address`、`httpRequest`）的访问。而不是通配符，授予对特定表和列的权限。
- 在 Athena 工作组输出存储桶上配置 SSE-KMS 加密，以保护查询结果。
- 优先使用特定数据源关联而不是通配符（`*/*`），以限制哪些数据源被导出到可查询的表中。

### 审计跟踪

为 Athena (`StartQueryExecution`、`GetQueryResults`) 和 Lake Formation (`GrantPermissions`、`RevokePermissions`) API 调用启用 CloudTrail 日志，以维护谁查询了哪些数据的审计跟踪。

## 其他资源

- [CloudWatch 日志 S3 表集成](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/s3-tables-integration.html)
- [支持的 AWS 提供的数据源](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/AWS-logs-and-resource-types.html)
- [集成的 IAM 权限](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/s3-tables-integration.html#s3-tables-integration-iam-permissions)
- [将 S3 表集成到分析服务](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-tables-integrating-aws.html)
- [Lake Formation 权限](https://docs.aws.amazon.com/lake-formation/latest/dg/granting-catalog-permissions.html)
