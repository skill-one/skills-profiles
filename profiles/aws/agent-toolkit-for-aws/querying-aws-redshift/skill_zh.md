# 查询 AWS Redshift 系统表

## 概述

**最适合**在 [AWS MCP 服务器](https://docs.aws.amazon.com/aws-mcp/) 上进行沙盒执行和审计日志记录。以下所有命令都使用 AWS CLI，并在配置了 AWS 凭证的任何环境中工作。使用 IAM 角色或临时凭证；避免使用长期存在的访问密钥。

Redshift 可以将 **系统表** — 即 `SYS_*` 监控数据，例如 `sys_query_history`、`sys_query_detail` 和 `sys_connection_log` — 发布到 **S3 表**，作为持续更新的 Apache Iceberg 表。

整个过程中使用的术语：**系统表** 指的是一般的 `SYS_*` 数据集，并且每个表都与发布的 Iceberg 表一一对应。当本技能说 **`SYS_` 视图** 时，它指的是集群本身上查询的实时集群对象——这是一个视图，它与发布的 S3 表副本是不同的东西。这适用于 **预置集群** 和 **无服务器命名空间**。它是现有日志记录 API 的可选扩展。发布的表是只读的，存储在 AWS 管理的 `aws-redshift` 表桶中，并且可以通过任何 Iceberg 兼容引擎查询，包括 Amazon Athena 和 Amazon Redshift 本身。

当分析历史记录或高容量的系统表数据时，优先于实时集群内 `SYS_` 视图查询 S3 表副本，因为：

- 集群内的 `SYS_` 视图具有有限的数据保留期；S3 表保留的历史记录远超其范围。
- 查询 S3 表不会给正在运行的 Redshift 集群增加负载。
- 日志记录是 Iceberg 表，因此可以从任何 Iceberg 兼容引擎大规模查询，并与其他湖数据联合。

## 决策树

| 用户意图 | 使用此技能？ | 替代方案 |
|---|---|---|
| 为集群或命名空间开启 S3 表日志发布 | **是** | — |
| 确认集群/命名空间正在发布 / 查找其 S3 表命名空间 | **是** | — |
| 从 Redshift 系统表中查询非实时数据 | **是** | — |
| 为 Redshift 监控和审计构建每日/每周/每月仪表板 | **是** | — |
| 选择性停止 S3 表发布 | **是** | — |
| 从 Redshift 查询已发布的系统表（跨数据库） | **是** | — |
| 从 Athena 查询已发布的系统表 | **是** | — |
| 检查实时集群上的 *当前、实时* `SYS_` 状态 | **否** | 直接在集群上查询 `SYS_` 视图 |
| 查询客户表 *内部* 的数据 | **否** | 在集群上直接执行 Redshift SQL |

## 支持的数据源

| 计算类型 | 启用/禁用 API | 状态 API | 粒度选项 |
|---|---|---|---|
| Redshift 预置集群 | `redshift enable-logging` / `redshift disable-logging` | `redshift describe-logging-status` | `cluster`（默认），`account` |
| Redshift 无服务器命名空间 | `redshift-serverless update-namespace` with `--s3-table-action Enable`/`Disable` | `redshift-serverless get-namespace` | `namespace`（默认），`account` |

两种计算类型都发布到相同的 AWS 管理的 `aws-redshift` 表桶，发布后查询方式相同。它们的不同之处仅在于启用/禁用 API 表面和状态响应的大小写——请参阅 [常见任务](#common-tasks) 中的标志和字段表。

本技能不涵盖的内容：Redshift 审计日志发送到 S3 或 CloudWatch（`useractivitylog`、`userlog`、`connectionlog`），它们使用 Serverless 上的单独 `--log-exports` 机制，并且不是 `SYS_*` 系统表。

## 常见任务

### 1. 检查配置

在查询之前，确认集群或命名空间是否正在发布到 S3 表。

```bash
# 预置
aws redshift describe-logging-status --region <REGION> --cluster-identifier <CLUSTER_ID>
# 无服务器
aws redshift-serverless get-namespace --region <REGION> --namespace-name <NAMESPACE_NAME>
```

**解释响应。** 两种计算类型返回 *相同* 的信息，但字段名称和大小写 *不同*——预置使用 PascalCase 在 `S3Tables` 下，无服务器使用 camelCase 在 `namespace.s3TablePublishStatus` 下：

| 含义 | 预置 (`describe-logging-status`) | 无服务器 (`get-namespace`) |
|---|---|---|
| 未启用 | `LoggingEnabled: false` 或没有 `S3Tables` 块 | 没有 `s3TablePublishStatus` 块 |
| 目标包括 S3 表 | `LogDestinationType` 包含 `s3table` | `logDestinationType` 包含 `s3table` |
| 发布的 `SYS_*` 表列表 | `S3Tables.S3Tables` | `namespace.s3TablePublishStatus.s3Tables` |
| **确切的 S3 表命名空间**（查询所需） | `S3Tables.S3TableNamespace` | `namespace.s3TablePublishStatus.s3TableNamespace` |
| 粒度 | `S3Tables.S3TableGranularity` (`cluster`/`account`) | `namespace.s3TablePublishStatus.s3TableGranularity` (`namespace`/`account`) |
| 每个表的最后摄取时间 | `S3Tables.LastIngestionTimes` | `namespace.s3TablePublishStatus.lastIngestionTimes` |
| 所有可用的系统表已发布 | `S3Tables.EnabledAll` | `namespace.s3TablePublishStatus.enabledAll` |

注意：

- `LogDestinationType` 在有多个目标激活时是一个 **逗号连接的列表**——例如 `"cloudwatch,s3table"`。使用子字符串/包含检查，而不是与 `s3table` 进行等值比较。
- 空的 `LastIngestionTimes` / `lastIngestionTimes` 映射，或者列出的表作为已发布但不在映射中，表示该表的数据可能仍在传输中。比较连续值以确认新数据已到达。
- 在无服务器上，**不要**读取此功能的顶层 `logExports` 字段——该字段包含 CloudWatch/S3 审计日志（`useractivitylog`、`userlog`、`connectionlog`），与 `SYS_*` S3 表发布无关。

### 2. 启用（如果未配置）

```bash
# 预置
aws redshift enable-logging --region <REGION> --cluster-identifier <CLUSTER_ID> --log-destination-type s3table --log-exports <SYS_TABLE>... --s3-table-granularity <cluster|account> --s3-table-kms-key-id <KMS_KEY_ARN>
# 无服务器
aws redshift-serverless update-namespace --region <REGION> --namespace-name <NAMESPACE_NAME> --log-destination-type s3table --s3-table-names <SYS_TABLE>... --s3-table-action Enable --s3-table-granularity <namespace|account> --s3-table-kms-key-id <KMS_KEY_ARN>
```

`--s3-table-kms-key-id` 是故意包含在两个命令中的，而不是可选附加项。省略它不会失败——表会回退到 AWS 拥有的密钥，您无法对其进行审计、通过策略限制或撤销。因为 `SYS_*` 表包含 `query_text`、`user_name` 和 `remote_host`，将客户管理的密钥视为默认值，仅在一次性环境中丢弃该标志。

从 AWS 控制台启用：

Amazon Redshift 控制台 > 集群 > 选择您的集群 > 选项卡 > 集成 / 系统表集成

**两种计算类型对同一功能使用不同的标志。** 不要将预置标志名称用于无服务器：

| 目的 | 预置 (`enable-logging`) | 无服务器 (`update-namespace`) |
|---|---|---|
| 发布哪些系统表 | `--log-exports` | `--s3-table-names` |
| 启用与禁用 | 分离的 `enable-logging` / `disable-logging` 操作 | `--s3-table-action Enable` \| `Disable` |
| 粒度 | `--s3-table-granularity` `cluster` \| `account` | `--s3-table-granularity` `namespace` \| `account` |
| 客户管理的 KMS 密钥 | `--s3-table-kms-key-id` | `--s3-table-kms-key-id` |
| 验证而不应用 | `--dry-run` | `--dry-run` |

注意：

- 粒度：预置支持 `cluster`（默认）或 `account`；无服务器支持 `namespace`（默认）或 `account`。
- `cluster`/`namespace` 粒度 → 每个集群/命名空间一个 S3 表；`account` → 每个账户每个区域所有集群/命名空间一个共享表。
- 使用 `all` 发布所有可用的 `SYS_*` 表——`--log-exports all`（预置），`--s3-table-names all`（无服务器）。
- **强烈建议生产环境使用存储加密。** 没有 `--s3-table-kms-key-id`，发布的表使用 AWS 拥有的密钥加密，您无法对其进行审计、通过策略限制或撤销。`SYS_*` 表包含 `query_text`、`user_name` 和 `remote_host`（见 [安全注意事项](#security-considerations)），因此传递客户管理的密钥。使用 `${SKILL_DIR}/references/security.md` 中的完整密钥策略授予密钥访问权限，而不是简化的操作列表——它需要 **两个** 服务主体（`systemtables.redshift.amazonaws.com` 用于发布，`maintenance.s3tables.amazonaws.com` 用于表维护/压缩）。仅配置发布主体会导致写入成功，而压缩静默失败。
- 两个操作都接受 `--dry-run` 以验证请求而不进行任何更改。预置在成功时返回 `DryRunOperation` 错误（“由于 DryRun 标志设置，请求将成功”）；无服务器返回空正文和退出代码 0。请注意，无服务器的 dry-run 仅验证请求 *形状*，而不是参数值，因此在那里成功的 dry-run 并不保证值被接受。

**选择性禁用：**

```bash
# 预置
aws redshift disable-logging --region <REGION> --cluster-identifier <CLUSTER_ID> --log-destination-type s3table --log-exports <SYS_TABLE>...
# 无服务器
aws redshift-serverless update-namespace --region <REGION> --namespace-name <NAMESPACE_NAME> --log-destination-type s3table --s3-table-names <SYS_TABLE>... --s3-table-action Disable
```

### 3. 验证权限

两种路径的完整设置命令：**`${SKILL_DIR}/references/permissions-setup.md`**。在创建角色或注册资源之前加载它。

**Athena 路径**——需要 Glue 中注册的 `s3tablescatalog/aws-redshift` 目录、具有输出位置的工组，以及 S3 表的读取权限。确认目录可查询：

```bash
aws glue get-databases --region <REGION> \
  --catalog-id "<ACCOUNT>:s3tablescatalog/aws-redshift"
```

返回的命名空间 → 已注册并可查询。`EntityNotFoundException` / `CATALOG_NOT_FOUND` → S3 表集成未启用（S3 控制台 > 表桶 > 启用集成）。**加密工组输出位置**——Athena 将完整结果集（包括 `query_text` 和 `user_name`）写入 S3。

**Redshift 自动挂载路径**——需要一个预置 RA3 集群和一个四步设置：创建 `query_s3_tables` 角色（信任策略必须命名 *两者* `redshift.amazonaws.com` 和 `lakeformation.amazonaws.com`，后者带有所有四个 `sts:AssumeRole`、`sts:SetContext`、`sts:SetSourceIdentity`、`sts:TagSession`），将其附加到集群，将表桶注册到 Lake Formation，并将 Redshift 服务关联角色添加到 `ReadOnlyAdmins`。导致大多数失败的约束：

- **同时检查 `aws:SourceAccount` 上的两个信任声明**——裸服务主体是混淆代理风险。
- **不要将 `AWSLakeFormationDataAdmin` 附加到集群的查询角色。** 它仅在执行设置时需要，并且仅在设置期间需要。集群的角色只需要读取权限。
- **自动挂载是一个轮询，而不是回调**——目录最多需要 300 秒才能出现在 `pg_database`。集群重启会强制立即发现。

### 4. 确定目标表

**命名空间**——从 API 中解析，不要构造：

- 从 `describe-logging-status` 读取 `S3Tables.S3TableNamespace`（预置）或从 `get-namespace` 读取 `s3TablePublishStatus.s3TableNamespace`（无服务器），并原样使用。
- 仅限卫生检查：API 值通常遵循 `<namespace_arn_id>_sys`（对于 `cluster`/`namespace` 粒度）和 `<account>_sys`（对于 `account` 粒度）。仅用于验证值是否正确——当 API 响应不可用时，切勿生成命名空间。

**表**——每个可发布的系统表都与 `aws-redshift` 表桶中的一个表一一对应。不要从记忆中的列表工作——按以下顺序在运行时解析：

1. **此集群/命名空间的已发布集**——`S3Tables.S3Tables`（预置）或 `s3TablePublishStatus.s3Tables`（无服务器）来自上面的状态调用，例如 `sys_query_history`。这是对“我现在可以查询什么”的唯一权威答案。
2. **此 API 接受的集**——`aws redshift enable-logging help`（接受的 `--log-exports` 值）或 `aws redshift-serverless update-namespace help`（接受的 `--s3-table-names` 值）。
3. **每个表包含的内容**——公共 [Redshift SYS 监控视图参考](https://docs.aws.amazon.com/redshift/latest/dg/cm_chap_system-tables.html)，它记录了每个 `SYS_*` 视图及其列。AWS 会随着时间的推移添加视图，因此将文档视为当前列表，而不是硬编码一个。

列名和类型来自相同的公共参考，或来自实时表：

```bash
aws glue get-table --region <REGION> \
  --catalog-id "<ACCOUNT>:s3tablescatalog/aws-redshift" \
  --database-name "<NAMESPACE>" --name "<SYS_TABLE>"
```

在阅读公共文档与已发布的表时，有两个注意事项：枚举值列（`query_type`、`status`、`event`）会随着时间的推移获得值，因此使用 `SELECT DISTINCT` 确认，而不是过滤假设的集合；已发布的 Iceberg 表会添加仓库标识列（`warehouse_name`、`warehouse_namespace_arn` 和对等体），而集群内的 `SYS_` 视图没有这些列——它们是区分多个集群在 `account` 粒度下发布的方式。

### 5. 查询

#### 从 Athena 查询

**查询语法：**

```sql
"s3tablescatalog/aws-redshift"."<NAMESPACE>"."<SYS_TABLE>"
```

#### 从 Redshift（自动挂载目录）

一旦自动挂载目录设置完成（见 `${SKILL_DIR}/references/permissions-setup.md`），使用跨数据库语法查询：

```sql
"aws-redshift@s3tablescatalog"."<NAMESPACE>".<SYS_TABLE>
```

#### 从 Redshift（外部模式）

或者，创建一个指向 S3 表目录的外部模式：

```sql
CREATE EXTERNAL SCHEMA <schema_name>
FROM DATA CATALOG
DATABASE '<NAMESPACE>'
CATALOG_ID '<ACCOUNT>:s3tablescatalog/aws-redshift'
IAM_ROLE 'arn:aws:iam::<ACCOUNT>:role/query_s3_tables'
REGION '<REGION>';

SELECT * FROM <schema_name>.<SYS_TABLE> LIMIT 10;
```

#### 约束

- 您 **必须** 在编写任何 SQL 查询之前运行 `describe-logging-status` 或 `get-namespace` 以获取命名空间——切勿手动构造
- 对于 Athena 查询，您 **必须** 在执行前确认工组和输出位置
- **时间列以微秒为单位。** 除以 `1000000.0` 转换为秒
- 表是 **只读的**——没有 `INSERT`/`UPDATE`/`DELETE`
- 始终添加 `LIMIT`，如果用户未指定；尽可能在 `start_time`/`record_time` 上过滤

#### 示例

针对常见需求的 SQL 工作示例——最长的查询、错误分析、连接审计、队列时间趋势、跨表连接——在 **`${SKILL_DIR}/references/example-queries.md`** 中。其中两条规则适用于它们中的每一个：

- **时间列以微秒为单位。** 除以 1,000,000 转换为秒。报告 `elapsed_time` 作为原始值会高估持续时间 10^6 倍。
- **在 Iceberg 分区列**（`year`/`month`/`day` 或表的自身分区）上过滤，除了任何时间戳谓词之外，或者引擎扫描完整历史记录。

### 路由：Athena vs Redshift vs 直接 SYS_ 访问

| 情景 | 使用 |
|----------|-----|
| 历史记录/高容量日志分析，无集群负载 | Athena 或 Redshift 在 S3 表上 |
| 已连接到 Redshift 集群，想查询 S3 表日志 | Redshift 跨数据库或外部模式 |
| 将系统表日志与其他湖数据联合 | Athena 或 Redshift Spectrum |
| 集群实时当前状态 | 直接在集群上查询 `SYS_` 视图 |
| 快速临时查询，无需 Redshift 集群访问 | Athena |

## 关键行为

- **无回填**——仅发布启用后记录的事件才交付到 S3 表
- **从 API 获取命名空间**——始终从 `describe-logging-status`（`S3Tables.S3TableNamespace`）或 `get-namespace`（`s3TablePublishStatus.s3TableNamespace`）读取命名空间；切勿手动构造
- **微秒时间**——所有持续时间列以微秒为单位；除以 1000000.0 转换为秒
- **只读**——发布的表无法写入
- **预置和 Serverless**——相同的表桶（`aws-redshift`），不同的启用 API
- **任何 Iceberg 兼容引擎**——从 Athena、Redshift 或任何读取 Iceberg 的引擎查询

## 故障排除

| 错误 | 原因 | 解决方法 |
|-------|-------|-----|
| `aws-redshift` 表桶未找到 | S3 表集成未启用或日志记录未开始 | 运行 `enable-logging`（预置）或 `update-namespace`（无服务器）with `--log-destination-type s3table` |
| Athena 中的 `CATALOG_NOT_FOUND` | S3 表未在 Glue 中注册 | 启用集成：S3 控制台 > 表桶 > 启用集成 |
| 启用后 Athena 表为空 | 摄取仍在进行中 | 检查 `LastIngestionTimes`（预置）/ `lastIngestionTimes`（无服务器）；等待并重新查询 |
| 命名空间中缺少 `SYS_*` 表 | 启用时未包含系统表 | 重新运行启用时包含该表，或使用 `all` — `--log-exports`（预置），`--s3-table-names`（无服务器） |
| 命名空间错误/为空 | 构造命名空间而不是从 API 读取 | 使用来自 describe/get 响应的命名空间——`S3Tables.S3TableNamespace`（预置）或 `s3TablePublishStatus.s3TableNamespace`（无服务器） |
| 状态响应中根本没有 `S3Tables` / `s3TablePublishStatus` 字段，即使发布已开启 | AWS CLI / SDK 过时。该字段被 **静默省略** 而不是引发错误，因此看起来与功能被禁用完全相同 | 升级 CLI/SDK，然后重新运行。在采取行动之前确认发布实际上已关闭——检查 `aws-redshift` 表桶中的命名空间，或 `LogDestinationType` 包含 `s3table` |
| `Unknown options: --log-exports, --log-export-action` 在无服务器上 | 使用预置标志名称针对 `update-namespace` | 使用 `--s3-table-names` 和 `--s3-table-action` — 见启用部分中的标志表 |
| `AccessDenied` 查询表 | 缺少 `s3tables:GetTable` 或 `GetTableData` | 见 `references/security.md` |
| 从 `sys_connection_log` 获取的空结果 | 查询身份缺乏可见性 | 使用具有超级用户级别访问权限的身份 |
| 目录未出现在 `pg_database` 中 | LF 资源未注册，或 SLRs 不是 ReadOnlyAdmins | 完成 `references/permissions-setup.md` 中的 Lake Formation 步骤，等待 5 分钟或重启 |
| 从 Glue “无法假设角色” | 信任策略中缺少 `sts:SetContext`/`sts:SetSourceIdentity`，或缺少 `AWSLakeFormationDataAdmin` | 修复信任策略并附加 `AWSLakeFormationDataAdmin` |
| `VerificationStatus: NOT_VERIFIED` | Lake Formation 注册后正常 | 如果查询正常工作，则无需采取任何操作 |
| Redshift 中查询失败，提示 “不存在” | 目录尚未自动挂载（轮询延迟） | 等待最多 300 秒或重启集群 |

## 安全注意事项

完整策略、密钥策略和检测设置：**`${SKILL_DIR}/references/security.md`**。在授予权限之前阅读它。不可协商的：

- **将 IAM 限制到 S3 表目录**，而不是通配符。Glue 数据库/表 ARN 嵌套在 `s3tablescatalog/aws-redshift` 下——裸 `database/*` 形式授予整个账户的元数据读取权限。`lakeformation:GetDataAccess` 是唯一必须使用 `"Resource": "*"` 的操作；使用 `aws:ResourceAccount` `StringEquals` 条件进行约束。
- **密钥策略需要两个主体**，而不是一个：`systemtables.redshift.amazonaws.com`（发布者）和 `maintenance.s3tables.amazonaws.com`（压缩）。仅授予发布者允许写入，而压缩静默失败。
- **`query_text` 可以包含凭证**，而不仅仅是架构——插值 SQL 和 `CREATE USER ... PASSWORD` 原封不动地出现在 `sys_query_history`。将对该表的广泛访问视为密钥暴露决策；使用 Lake Formation 限制该列。
- **发布本身是可审计的，值得对其发出警报。** `s3tables.amazonaws.com` `AccessDenied` 峰值和 `sys_connection_log` 失败认证计数是两个需要发出警报的信号；使用客户管理的密钥加密警报主题。
