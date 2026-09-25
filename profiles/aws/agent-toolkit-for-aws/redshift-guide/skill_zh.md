# Amazon Redshift 指南

## Redshift 并非 PostgreSQL（请先阅读）

Redshift 使用 PostgreSQL 的网络协议，并共享许多表面语法，因此大型语言模型假设 PostgreSQL 的行为会延续——这通常并不成立。差异体现在系统表（`pg_catalog` 不完整）、DDL（没有索引，没有序列）、函数（`string_agg`，对表使用 `SUBSTR`，仅领导者节点可用的函数）、类型（`text` 列变为 `VARCHAR(256)`）以及比较语义（尾随空格，未强制约束）。**假设存在差异，并参考下方文档进行验证——不要基于 PostgreSQL 习惯进行回答。** 常见的 PostgreSQL→Redshift 差异请参考 `references/redshift-sql-syntax.md`。

**最佳实践**：使用 [AWS MCP 服务器](https://docs.aws.amazon.com/aws-mcp/)——它在一个隔离的、记录审计日志的环境中运行下方的 AWS CLI 和 Redshift 数据 API 调用。此处提供的所有指导均为纯 AWS CLI 和 SQL，无需使用该服务器。

## 第 0 步：无服务器还是按需？

在回答之前必须确定这一点——API、系统表和功能有所不同。如果问题中说明是哪种类型，则从问题中获取；**如果没有说明，则必须询问。** `SELECT version()` 无法识别类型。

- **无服务器**——通过 *工作组*（以及命名空间）识别。数据 API 调用需要 `--workgroup-name`；用户会说“工作组”或“无服务器”。
- **按需**——通过 *集群* 识别。数据 API 调用需要 `--cluster-identifier`；用户会说“集群”。

| 目标 | 系统视图 | 凭据 API |
|---|---|---|
| **按需** | `SYS_`，所有 `SVV_` + `STL_`，`STV_`，`SVL_`，`SVCS_`（仅单 AZ — 在多 AZ 中禁用） | `redshift:GetClusterCredentials` |
| **无服务器** | `SYS_` + `SVV_` 的子集（仅此子集，没有 `STL`/`STV`/`SVL`/`SVCS`） | `redshift-serverless:GetCredentials` |

## 关键事实

- **`SHOW` 命令是主要元数据接口**——`SHOW DATABASES`，`SHOW SCHEMAS`，`SHOW TABLES`，`SHOW COLUMNS`，`SHOW TABLE`，`SHOW VIEW`。不要默认使用 `pg_catalog` 或 `information_schema`。→ **加载 `references/redshift-sql-metadata.md` 以回答元数据/发现问题以及任何“关系不存在”报告**——它包含诊断流程。
- **`SYS_` 视图是首选的系统视图**——它们在所有地方都可用。`STL_`，`STV_`，`SVL_` 和 `SVCS_` 仅在按需单 AZ 中可用，并且一些 `SVV_` 视图在无服务器中不受支持。→ **加载 `references/redshift-sql-metadata.md` 以回答任何系统视图或监控问题。**
- **`sys_load_error_detail`** 用于 `COPY` 调试（不是 `stl_load_errors`，后者仅在按需单 AZ 中可用）。
- **`DATEADD/DATEDIFF`**——单位优先参数顺序：`DATEADD(day, -30, GETDATE())`，`DATEDIFF(day, start, end)`。
- **`APPROXIMATE COUNT(DISTINCT col)`**——Redshift 特有，约 2% 的误差，在大型数据集上比精确 `COUNT(DISTINCT)` 快得多。
- **`MERGE ... REMOVE DUPLICATES`**——当源和目标具有相同架构时的简化去重。
- **`COPY` 应使用 IAM_ROLE**（命名空间角色，不是调用者角色）+ 支持显式文件列表的 MANIFEST + MAXERROR 用于错误容忍。
- **`SUBSTR()` 仅在领导者节点上可用**——对字面量有效，但对表列会出错（`SUBSTR() 函数不受支持（提示：使用 SUBSTRING 代替）`）。对列使用 `SUBSTRING()`。
- **`UNIQUE` / `PRIMARY KEY` / `FOREIGN KEY` 仅提供信息**——不强制执行（允许重复行且无错误）。优化器提示；在应用程序中或通过 `MERGE` 强制完整性。`NOT NULL` 是强制执行的。
- **`SHOW VIEW <schema.name>`** 返回常规视图、物化视图或延迟绑定视图的定义。MV 新鲜度：`SVV_MV_INFO` (`is_stale`)。
- **`TOP N` 和 `LIMIT N` 都有效**（`TOP N PERCENT` 无效）。`text` 列变为 `VARCHAR(256)`——使用 `VARCHAR(max)` 或显式长度。
- **Iceberg 表使用 `CREATE TABLE ... USING ICEBERG`**（不是 `STORED AS ICEBERG`，不是 `TABLE_FORMAT=ICEBERG`）。
- **数据共享支持读写操作**——消费者在生产者授予写权限后可以写入。将数据共享写上的“权限拒绝”视为**缺失授权**，而不是不支持的操作。→ **加载 `references/redshift-sql-metadata.md` 以了解要求和限制。**

## 安全防护措施

**禁止：** 删除数据库，无 `WHERE` 的删除，`publicly-accessible=true`，对所有授予所有权限
**警告后确认：** 大型表的 `RESIZE`，`RESTORE`，`VACUUM`，`ALTER PASSWORD`，WLM 配置更改
**确认：** 创建，特定授权，`COPY`，`UNLOAD`

## 安全注意事项

在生成任何连接、加载数据或导出数据的操作时应用这些默认值。详细信息请参考注明的参考文件。

- **传输中：** 数据 API 仅支持 HTTPS。对于 JDBC/ODBC 设置 `require_ssl` 参数，并使用 `sslmode=verify-full` 连接以检查服务器证书。
- **静态存储：** 启用集群/命名空间加密，并在 `UNLOAD` 中添加 `ENCRYPTED KMS_KEY_ID '<arn>'`——它将查询结果写入 S3，在 Redshift 自身的加密范围之外。→ `references/redshift-sql-ddl-copy.md`
- **凭据：** 优先使用 `SecretArn`（秘密管理器）或 IAM 身份中心；`DbUser` 可以接受，因为它会发出临时凭据。永远不要将数据库密码放在代码、环境变量或 SQL 文本中。→ `references/redshift-sql-recipes-load-api.md`
- **最小权限：** 将命名空间 `IAM_ROLE` 的范围限制到特定存储桶和前缀（`s3:GetObject` 对 `arn:aws:s3:::<bucket>/<prefix>/*`），而不是 `s3:*` 或管理式完全访问策略，并使其信任策略基于 `aws:SourceArn`（集群/命名空间 ARN）和 `aws:SourceAccount`——仅 `SourceArn` 仍然允许账户中的其他资源假设它。按对象授予权限，而不是 `GRANT ALL ON ALL`。
- **审计：** CloudTrail 记录 `redshift-data:*` API 调用，但不记录执行的 SQL；启用 Redshift 审计日志（`useractivitylog`，`connectionlog`，`userlog`）以记录 SQL。两者都捕获查询文本和用户活动，因此必须加密所有正在使用的目标：CloudWatch 日志组（`aws logs associate-kms-key`），CloudTrail 路径（SSE-KMS），以及审计日志 S3 存储桶（SSE-S3——审计日志到 S3 仅支持 S3 管理密钥，不支持 KMS）。无服务器仅支持将审计日志发送到 CloudWatch。
- **网络：** 保持 `PubliclyAccessible=false` 并通过 VPC 端点连接。不要将端口 5439 打开到 `0.0.0.0/0` 或 `::/0`——将入站规则范围限制到特定 CIDR 或引用的安全组。
- **敏感数据：** 数据 API 结果保留 24 小时，`sys_load_error_detail` 可能会回显拒绝行的片段，因此将语句 ID 和加载错误输出视为敏感数据。
- **进一步阅读：**
  [Amazon Redshift 中的安全](https://docs.aws.amazon.com/redshift/latest/dg/db-security.html)
  以了解这些默认值的完整指导。

## 路由表

**强制要求：** 当问题匹配下方某行时，你必须加载并阅读参考文件，然后再回答。

**在提供故障排除步骤之前询问目标是否为按需或无服务器——除非问题已经说明，否则使用该信息并不要重新确认。**

| 用户意图 | 路由到 |
|---|---|
| "CREATE TABLE"，"DISTKEY/SORTKEY"，"ENCODE"，"IDENTITY"，"COPY"，"UNLOAD"，"IAM_ROLE"，"Iceberg 表" | `references/redshift-sql-ddl-copy.md` |
| "LISTAGG"，"DATEADD/DATEDIFF"，"NVL/DECODE"，"类型映射"，"text 类型"，"VARBYTE"，"递归 CTE" | `references/redshift-sql-functions-types.md` |
| "QUALIFY"，"PIVOT/UNPIVOT"，"MERGE"，"TOP N"，"SUBSTR 错误"，"UNIQUE/PK 不强制执行"，"尾随空格"，"领导者节点函数"，"JSON"，"SUPER"，"PartiQL"，"嵌套/半结构化数据" | `references/redshift-sql-extensions-semantics.md` |
| "系统视图"，"SVV_/SYS_"，"SHOW 命令"，"STL vs SYS"，"列出表"，"distkey/sortkey 查找"，"数据共享发现"，"两部分 vs 三部分"，"权限拒绝"，"GRANT"，"权限"，**"关系/表不存在"** | `references/redshift-sql-metadata.md` |
| "如何编写 SQL"，"PostgreSQL vs Redshift"，"哪个 SQL 参考"，一般方言问题 | `references/redshift-sql-syntax.md`（6 个 SQL 参考的索引 + PostgreSQL vs Redshift 失败表） |
| "COPY 失败"，"加载错误"，"数据 API 轮询"，"异步查询"，"数据 API 流量限制" | `references/redshift-sql-recipes-load-api.md` |
| "物化视图"，"MV 刷新"，"AUTO REFRESH"，"陈旧视图" | `references/redshift-sql-materialized-views.md` |
| 一般 Redshift 问题未匹配上述内容 | 直接从一般知识回答 |
| Aurora，RDS，DynamoDB，Athena（非 Redshift） | **拒绝。** 说明此技能仅适用于 Amazon Redshift。不要为其他数据库服务提供建议。 |

## 数据 API 快速参考

→ **在回答任何数据 API、COPY 错误或异步查询问题之前，必须加载 `references/redshift-sql-recipes-load-api.md`。** 它包含有界轮询循环，`HasResultSet` 和 `ResourceNotFoundException` 处理，每个目标的参数，以及认证选项。

数据 API 调用默认为**异步**——使用长轮询（`--wait-time-seconds`，1–30）而不是盲目休眠，并保持有界循环以处理可能超过 30 秒的工作。无服务器使用 `--workgroup-name`，按需使用 `--cluster-identifier`。
