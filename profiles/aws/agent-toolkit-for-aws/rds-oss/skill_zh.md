# RDS OSS Advisor (MySQL, MariaDB, PostgreSQL)

## 概述

针对 Amazon RDS 开源引擎（**MySQL**、**MariaDB** 和 **PostgreSQL**）的顾问。包含五个决策领域：

1. **实例创建** — 使用最佳实践默认设置（最新版本、多可用区、加密、性能洞察、密钥管理器密码管理）创建生产就绪实例
2. **升级规划** — 识别实例、枚举目标、运行实时预检查、标记计划回归、显示预检查/后检查清单
3. **承诺定价** — 为稳定工作负载估算预留实例 (RI) 和数据库节省计划 (DSP) 的节省
4. **RDS Proxy 评估** — 基于连接利用率和固定风险，决定是否值得使用代理
5. **蓝绿部署** — 规划低停机时间的 DDL 或主要升级，并进行 DDL 兼容性分析

生成成本估算、预检查结果和 CLI 命令。例如，在实例创建时，会使用生产最佳实践执行 `create-db-instance` 调用。对于升级、购买和切换，仅提供建议，不会在未经明确用户确认的情况下执行。

仅限于 RDS 开源引擎。对于 Aurora，请使用 `amazon-aurora`。对于 Oracle、SQL Server、Db2，请使用特定于引擎的技能。

建议使用 AWS MCP 服务器执行命令，但不是必需的；所有操作也可以通过 AWS CLI 执行。

## 决策指南

| 用户询问关于… | 前往 |
|---|---|
| 创建、配置或设置新的 RDS MySQL/MariaDB/PostgreSQL 实例 | 下面的 [Production Instance Creation](#production-instance-creation) |
| 升级、目标版本、预/升级检查清单、升级预检查、读取副本升级顺序 | [references/upgrade-workflow.md](references/upgrade-workflow.md) |
| 预留实例 (RI)、数据库节省计划 (DSP)、1 年 vs 3 年、多可用区承诺、无/部分/全部预付 | [references/commitment-pricing-workflow.md](references/commitment-pricing-workflow.md) |
| RDS Proxy、连接池、连接过多、Lambda 数据库连接、代理固定、PgBouncer vs Proxy | [references/proxy-advisor-workflow.md](references/proxy-advisor-workflow.md) |
| 蓝绿、零停机时间 DDL、切换、最小停机时间下的模式更改、生产上的类型更改 | [references/bluegreen-advisor-workflow.md](references/bluegreen-advisor-workflow.md) |

对于宽泛的请求（“帮助我处理 RDS”），将五个选项作为单独的一行呈现。如果用户提供了实例 ID，则提供一般健康检查（引擎 + 版本 + 连接利用率）作为入口点。

超出范围（Aurora、Oracle、SQL Server、Db2、备份策略、性能洞察深度分析）：从一般知识中回答，指出此技能不涵盖，并指向正确的特定于引擎的技能。

## RDS 与 Aurora — 不要混淆

RDS 开源引擎和 Aurora 是不同的产品，具有不同的语义。您**必须**不将 Aurora 的概念应用于 RDS：

| 概念 | RDS（此技能） | Aurora（使用 `amazon-aurora`） |
|---|---|---|
| LTS 发布 | ❌ 不存在 | ✅ 有 LTS 版本 |
| 无服务器模式 | ❌ 不存在 | ✅ Aurora 无服务器 |
| I/O 优化存储 | ❌ 不存在 | ✅ aurora-iopt1 |
| 数据 API | ❌ 独立 RDS 不提供 | ✅ Aurora 无服务器集群 |
| 实例拓扑 | 基于实例 (`describe-db-instances`) | 基于集群 (`describe-db-clusters`) |
| 升级范围 | 每个实例 | 每个集群（写入者 + 读取者一起） |
| DSP 术语选项 | 1 年和 3 年 | 仅 1 年 |
| 定价模型 | 按需 + RI + DSP | 按需 + RI + DSP + I/O 定价 |

如果用户询问任何 Aurora 特定的概念，请路由到 `amazon-aurora`。如果实例实际上是 Aurora（引擎 = `aurora-mysql` 或 `aurora-postgresql`），请停止并重定向。

## 生产实例创建

当用户要求创建或配置用于生产的新 RDS MySQL、MariaDB 或 PostgreSQL 实例时，您**必须**默认应用以下最佳实践：

1. **使用最新稳定的主版本** — 运行 `aws rds describe-db-engine-versions --engine <engine> --query "DBEngineVersions[].EngineVersion"` 查找最新版本。对于 MySQL，优先选择 8.4.x 而不是 8.0（8.0 的标准支持结束日期早于 8.4 — 请参阅 [RDS 扩展支持](https://aws.amazon.com/rds/extended-support/) 获取日期）。对于 PostgreSQL，使用最新主版本。对于 MariaDB，使用最新主版本。
2. **启用多可用区** — 设置 `--multi-az` 以实现自动故障转移。
3. **使用客户管理的 KMS 密钥启用存储加密** — 设置 `--storage-encrypted --kms-key-id <key-arn>`。客户管理的密钥可以完全控制密钥轮换、访问策略和跨账户共享。
4. **禁用公共访问** — 设置 `--no-publicly-accessible` 以确保实例无法从互联网访问。
5. **将备份保留设置为 7 天** — 设置 `--backup-retention-period 7`。
6. **启用具有 7 天保留期的性能洞察** — 设置 `--enable-performance-insights --performance-insights-retention-period 7`。如果性能洞察捕获包含敏感数据的查询（例如，WHERE 子句中的字面值），请指定 `--performance-insights-kms-key-id <key-arn>` 以使用客户管理的 KMS 密钥进行加密存储。
7. **启用删除保护** — 设置 `--deletion-protection`。
8. **避免默认主用户名** — 不要使用众所周知的名称，如 `admin`、`root`、`postgres` 或 `master`，这些名称使凭证猜测攻击更容易。选择自定义的 `--master-username`（例如，应用程序或团队特定的名称）。
9. **通过密钥管理器管理主密码** — 设置 `--manage-master-user-password` 而不是提供明文的 `--master-user-password`。这会在密钥管理器中自动创建和轮换密码。对于生产实例，**绝对不要**接受或使用明文密码。
10. **使用 gp3 存储** — 设置 `--storage-type gp3`。它比 gp2 更便宜、更快，且没有最低 IOPS 购买要求。
11. **标记实例，以便客户可以识别通过此技能创建的资源** — 设置 `--tags Key=created_by,Value=rds-oss-skill Key=generation_model,Value={your-model-id}`（请参阅下面的资源标记）。
12. **强制传输中的连接使用 TLS** — 创建或修改数据库参数组以要求加密连接：`require_secure_transport=ON`（MySQL/MariaDB），`rds.force_ssl=1`（PostgreSQL）。
13. **将数据库日志导出到 CloudWatch Logs 并使用 KMS 加密** — 设置 `--enable-cloudwatch-logs-exports`，以便数据库级安全事件（失败的登录、可疑查询）在中心位置可见。使用 `["error","slowquery","audit"]`（MySQL/MariaDB）（注意：`audit` 流需要先启用审计日志，否则为空 — 在 RDS MySQL 中通过 Option Group 中的 MARIADB_AUDIT_PLUGIN，在 RDS MariaDB 中通过内置服务器审计参数，如 `server_audit_logging=1` 在参数组中）和 `["postgresql"]`（PostgreSQL）。数据库日志可能包含 SQL 字面值和用户名，因此您**必须**在生成的 `/aws/rds/instance/<name>/*` 日志组上配置一个 KMS 密钥，以保护静态敏感数据。

**示例 CLI（MySQL 8.4，生产就绪）：**

```bash
aws rds create-db-instance \
  --db-instance-identifier <name> \
  --engine mysql \
  --engine-version 8.4 \
  --db-instance-class <class> \
  --allocated-storage 100 \
  --storage-type gp3 \
  --storage-encrypted \
  --kms-key-id <kms-key-arn> \
  --no-publicly-accessible \
  --multi-az \
  --manage-master-user-password \
  --master-username <custom-non-default-username> \
  --backup-retention-period 7 \
  --enable-performance-insights \
  --performance-insights-retention-period 7 \
  --performance-insights-kms-key-id <kms-key-arn> \
  --deletion-protection \
  --enable-cloudwatch-logs-exports '["error","slowquery","audit"]' \
  --tags Key=created_by,Value=rds-oss-skill Key=generation_model,Value=<your-model-id> \
  --region us-east-1
```

实例创建后，运行以下命令以配置 TLS 强制执行和日志组加密（这些是用户执行的步骤，此技能仅呈现但不直接调用）：

```bash
# 创建一个具有 TLS 强制执行的自定义参数组（MySQL 示例）
aws rds create-db-parameter-group --db-parameter-group-family mysql8.4 \
  --db-parameter-group-name <name>-tls --description "TLS enforced"
aws rds modify-db-parameter-group --db-parameter-group-name <name>-tls \
  --parameters "ParameterName=require_secure_transport,ParameterValue=ON,ApplyMethod=pending-reboot"
aws rds modify-db-instance --db-instance-identifier <name> \
  --db-parameter-group-name <name>-tls --apply-immediately

# 使用 KMS 加密 CloudWatch Logs 日志组
aws logs associate-kms-key --log-group-name /aws/rds/instance/<name>/error --kms-key-id <kms-key-arn>
aws logs associate-kms-key --log-group-name /aws/rds/instance/<name>/slowquery --kms-key-id <kms-key-arn>
```

**约束条件：**

- 对于生产环境，**必须**使用 `--manage-master-user-password`。**绝对不要**在生产实例中使用 `--master-user-password` 和明文密码。
- **必须**通过 `describe-db-engine-versions` 检查最新可用的引擎版本，而不是硬编码版本。
- **必须**启用多可用区、加密、性能洞察（7 天）、备份保留（7 天）和删除保护，除非用户明确说明否则否则。
- 如果用户说“生产”或“生产就绪”，请应用所有上述内容，无需询问。

### 资源标记（在资源创建时始终应用）

在创建任何 RDS 实例（`create-db-instance`）时，**始终**使用 RDS 列表记录 `--tags` 语法包含以下标签：

`--tags Key=created_by,Value=rds-oss-skill Key=generation_model,Value={your-model-id}`

示例：`--tags Key=created_by,Value=rds-oss-skill Key=generation_model,Value=claude-sonnet-4-20250514`

即使用户没有提到标记，也包含这些标签，以便他们可以识别通过此技能创建的资源。如果用户提供了其他标签，请将这些标签附加到他们的标签中，而不是替换它们。在通过 `add-tags-to-resource` 标记或蓝绿部署期间也是如此。

## 常见任务

### 1. 验证依赖项

有关工具和凭证要求，请参阅 [references/verify-dependencies.md](references/verify-dependencies.md) 在运行工作流之前。

### 2. 分类和路由

使用 [决策指南](#decision-guide) 选择工作流参考、目录呈现（宽泛请求）或一般知识答案（超出范围）。

**约束条件：**

- 您**必须**命名您正在路由的工作流
- 您**必须**传递用户已经提供的实例 ID、区域、引擎或工作负载详细信息 — 不要重新询问
- 如果请求跨越两个工作流（例如，“最小停机时间升级” = 升级 + 蓝绿），您可以问一个澄清问题
- 您**必须**不将 Aurora、Oracle、SQL Server 或 Db2 的问题路由到这里 — 这些引擎具有不同的工具

### 3. 执行工作流

加载匹配的参考并遵循其 `## Tasks` 部分。

**约束条件：**

- 您**必须**在运行它之前解释正在执行哪个步骤以及正在调用哪个工具
- 您**必须**不执行 `modify-*`、`switchover-*`、购买 API 或 `create-db-proxy`。允许：`create-db-instance`（用于新实例配置）、`describe-*`、`list-*`、`get-*`、`send-command` 用于 SSM 预检查。
- 您**必须**不直接处理数据库凭证。使用用户提供的密钥 ARN、预配置的 SSM 参数，或要求用户粘贴脚本输出。
- 当实时调用或捆绑脚本无法运行时，您**必须**报告确切的障碍，并执行离线回退或要求用户输入。您**必须**不编造命令输出、分析器结果、价格数字或版本列表 — 没有事实依据的看似合理的答案比拒绝更糟，因为用户会根据它采取行动。
- 如果多个工作流运行，用 2-4 行的总结链接到先前的输出。

每个工作流参考都包含其自己的工具调用示例。

### 必须呈现的关键事实

这些 RDS-OSS 特定的关键事实使此技能与普通的 MySQL/PostgreSQL/MariaDB 知识区分开来。通常，一般答案会将 RDS 与 Aurora 混淆，省略 CLI 命令名称，或在这是一个建议技能时进行操作。

对于“运行我的 RDS MySQL 实例的 RDS 升级顾问”，您**必须**告诉用户以下五个事实：

1. **通过 `aws rds describe-db-instances` 识别实例**（不是 `describe-db-clusters` — RDS MySQL/MariaDB/PostgreSQL 是**基于实例**的，不是基于集群的；`describe-db-clusters` 仅适用于 Aurora）。
2. **从响应中检测引擎**（`mysql`、`mariadb` 或 `postgres`）— 不要假设。
3. **使用 `aws rds describe-db-engine-versions` 列出有效升级目标** — 具体使用当前引擎和主版本作为过滤器。这是如何枚举允许的升级路径的方法。
4. **明确推荐最新版本**（例如，“8.0.40 是最新的 8.0 小版本，8.4.x 是下一个主版本”）。
5. **不要提及 LTS** — RDS 没有 LTS 概念（请参阅 [RDS 与 Aurora](#rds-vs-aurora--do-not-confuse)）。提供 LTS 建议表明在 RDS 和 Aurora 之间路由时存在混淆。

**关键工作流规则 — 当命名的实例无法定位时：** 如果 `describe-db-instances --db-instance-identifier <id>` 返回无结果或 `DBInstanceNotFoundFault`，您**必须**仍然为用户执行完整的顾问工作流 — 名称每个步骤（`describe-db-instances`，然后是引擎检测，然后是 `describe-db-engine-versions`，然后是版本推荐，然后是预升级检查清单）— 并解释每个步骤的输出会是什么样子。**绝对不要**退出并询问“您能再检查一下实例 ID 吗？”然后停止。用户是在询问顾问程序，而不是让您执行实时发现。如果您看不到实例，请将工作流作为模板呈现，用户在提供正确的标识符后可以运行。

对于“将 RDS MariaDB 从 X 升级到最新版本”，您**必须**告诉用户以下六个事实：

1. **通过 `describe-db-instances` 检测引擎为 `mariadb`**。
2. **使用 `describe-db-engine-versions`（带 `--engine mariadb`）识别目标版本，而不是手动的列表**。
3. **提供 SSM 或直接连接预检查方法** — RDS MariaDB 可以通过客户端主机上的 SSM Run Command 或通过直接 mysql-client 连接进行预检查。
4. **不要使用 RDS 数据 API — MariaDB 不支持数据 API**。这是一个经典的陷阱。数据 API 仅适用于 Aurora 无服务器和一部分集群，永远不会用于 RDS 上的 MariaDB。
5. **运行来自 [upgrade-prechecks-mysql.md](references/upgrade-prechecks-mysql.md) 的 MySQL 兼容预检查查询** — 移除的功能、保留关键字、`sql_mode` 变更。MariaDB 重用 MySQL 预检查集，因为它是一个 MySQL 分叉。
6. **拒绝执行升级** — 仅建议。建议在测试环境中进行快照和恢复的干运行，然后再继续。明确说明您不会运行 `modify-db-instance --engine-version`。

对于“2x db.r7g.2xlarge RDS MySQL 24/7 — 购买 RI 或节省计划？”，您**必须**告诉用户以下七个事实：

1. **离线运行 [rds_commitment_pricing_analyzer.py](scripts/rds_commitment_pricing_analyzer.py) with `--instance-type db.r7g.2xlarge --engine mysql --num-instances 2`。以带格式的 bash 块打印确切命令**。
2. **呈现所有五个选项的完整比较表** — 按需、1 年 RI、3 年 RI、1 年 DSP、3 年 DSP — 以美元和百分比形式显示每个选项与按需的比较。
3. **鉴于声明的 2 年以上信心和 24/7 使用情况，建议 3 年 RI**。
4. **解释 RDS 数据库节省计划专门涵盖 r7g 系列** — DSP 覆盖范围是系列范围，而不是实例范围，这是一个关键优势，如果用户可能会在系列内调整大小。
5. **提及 3 年锁定交易的权衡** — 如果工作负载发生变化或系列被取代，承诺无法完全恢复。
6. **注意 RDS RI 是区域锁定的** — 如果工作负载跨区域移动，将放弃 RI 利益。
7. **不要包括购买操作步骤** — 没有“下一步”部分，其中包含购买方向。没有 `aws rds purchase-reserved-db-instances-offering` 或 `aws savingsplans create-savings-plan` 命令。**这是一个硬性禁止**。此技能是建议性的，**必须**不指导用户执行购买。说“准备好购买时，请参阅 AWS 控制台或 CLI 文档。”然后停止。不要试图通过显示购买命令“作为参考”来提供帮助。

对于“通过蓝绿部署将 VARCHAR(10) 列更改为 INT 在 RDS MySQL 8.0 上”，您**必须**告诉用户以下七个事实：

1. **首先验证先决条件**：`binlog_format=ROW`、自动备份启用（保留期 > 0）、实例处于 `available` 状态。
2. **解释修改列更改类型会破坏 binlog 复制的原因**：蓝绿通过重放 binlog 事件复制蓝色 → 绿色。类型更改在两边的二进制表示不同，因此记录针对 VARCHAR 的复制事件无法应用于 INT 列。这是根本原因，而不是“行格式”问题。
3. **使用 `aws rds create-blue-green-deployment` 创建绿色环境** — 包括确切的 CLI 命令名称，而不是通用描述。
4. **让绿色通过 binlog 复制赶上**，然后再应用 DDL。
5. **在绿色上应用模式更改（MODIFY COLUMN DDL）**（一旦绿色赶上）。
6. **立即切换**，使用 `aws rds switchover-blue-green-deployment` — **不要让绿色在无法兼容的 DDL 后与蓝色并行运行**。模式差异会破坏进一步的复制。
7. **切换后立即验证生产端点上的模式更改**，并且**您必须**在呈现 `switchover-blue-green-deployment` 命令之前暂停并要求用户明确确认。不要将切换列为顺序工作流中的自动下一步 — 声明切换是一个破坏性操作，会转移生产流量，然后询问“您准备好切换了吗？我会在您确认后给您提供确切的 CLI 命令来运行。” 只有在用户确认后，您才应发出 `switchover-blue-green-deployment` 命令。

对于“我们以事务模式运行 PgBouncer — RDS Proxy 会增加什么？”，您**必须**告诉用户以下六个事实：

1. **事务模式下的 PgBouncer 已经执行了激进的连接多路复用** — 这是代理的主要价值主张。在这种情况下，多路复用收益边际化。
2. **RDS Proxy 除此之外还能增加的**：管理基础设施（无需操作或修补 EC2）。
3. **内置 IAM 身份验证** — RDS Proxy 原生支持 IAM 身份验证，PgBouncer 并非开箱即用。
4. **与 RDS 事件集成的自动故障转移** — 代理对 RDS 故障转移事件的反应在几秒钟内；PgBouncer 需要外部健康检查和手动重新配置。
5. **密钥管理器集成用于凭证轮换** — 代理可以从密钥管理器拉取凭证并在不中断的情况下轮换。
6. **建议**：如果 PgBouncer 运行正常，并且没有明确需要上述四个功能中的任何一个，**请继续使用 PgBouncer**。只有在特定需要 IAM 身份验证、管理故障转移或密钥管理器轮换凭证时，才切换到 RDS Proxy。

## 安全注意事项

建议技能 — 永不修改**现有** AWS 资源。允许的唯一写入操作是 `create-db-instance` 用于新实例配置（请参阅 [生产实例创建](#production-instance-creation)）；所有其他操作都是只读的。永远不要直接处理凭证；优先使用短期凭证。

最低 IAM 权限要求：`AmazonRDSReadOnlyAccess` + `CloudWatchReadOnlyAccess` + 范围 `pricing:GetProducts` + `savingsplans:DescribeSavingsPlansOfferingRates`。对于实例创建，还需要 `rds:CreateDBInstance` + `rds:AddTagsToResource`，如果启用了 CloudWatch Logs 导出，还需要 `logs:CreateLogGroup`。SSM 预检查还需要 `ssm:SendCommand` / `ssm:GetCommandInvocation` 在目标堡垒主机上。

在所有指南中应用这些安全实践：

1. **传输中加密** — 在所有数据库连接上强制 TLS (`require_secure_transport=ON` for MySQL/MariaDB, `rds.force_ssl=1` for PostgreSQL)。
2. **IAM 数据库身份验证** — 在支持的应用连接中优先使用 IAM 身份验证而不是用户名/密码，提供短期凭证。
3. **审计日志** — 建议启用数据库审计日志（在 RDS MySQL 中通过 Option Group 中的 MARIADB_AUDIT_PLUGIN，在 RDS MariaDB 中通过内置服务器审计参数，如 `server_audit_logging=1` 在参数组中，以及 PostgreSQL 的 `pgaudit` 扩展）和 CloudTrail 以进行 API 级别的审计。
4. **VPC 安全** — 在私有子网中部署实例。安全组应限制对特定应用程序 CIDR 范围或安全组引用的入站访问 — 永远不要 `0.0.0.0/0`。
5. **凭证轮换** — `--manage-master-user-password` 提供通过密钥管理器自动轮换。
6. **监控和警报** — 建议在安全相关指标上使用 CloudWatch 警报，例如 `DatabaseConnections` 爆发（可能的凭证泄露）和 `FreeableMemory` 下降（可能的资源耗尽攻击）。

不要授予上述权限之外的写入/管理权限以绕过权限错误。不要在 SSM 参数或命令文本中存储数据库密码 — 在命令中检索密钥。

## 故障排除

**访问被拒绝。** 附加上述只读策略。

**凭证过期。** 刷新，或回退到 `--offline` 进行承诺定价。

**超时/限流。** 重试一次，然后缩小范围。SSM 预检查超时（大型模式）：切换到直接连接或用户运行脚本。独立 RDS 不提供 RDS Data API。

**资源未找到。** 验证区域/ID；确认它不是 Aurora *集群*（`describe-db-clusters`）。空的 RI/DSP 提供程序 — 回退到离线。

**用户要求执行更改。** 建议技能 — 对现有资源的修改通过 AWS 控制台或用户运行的 CLI 发生。

**Aurora 问题。** 路由到 `amazon-aurora`。请参阅 [RDS 与 Aurora](#rds-vs-aurora--do-not-confuse)。

**Oracle / SQL Server / Db2 问题。** 路由到 `rds-oracle`、`rds-sqlserver` 或 `rds-db2`。

## 其他资源

- [Amazon RDS 用户指南](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/)
- [RDS 定价](https://aws.amazon.com/rds/pricing/)
- [RDS MySQL 升级](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_UpgradeDBInstance.MySQL.html) · [RDS MariaDB 升级](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_UpgradeDBInstance.MariaDB.html) · [RDS PostgreSQL 升级](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_UpgradeDBInstance.PostgreSQL.html)
- [RDS 预留实例](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_WorkingWithReservedDBInstances.html) · [数据库节省计划](https://docs.aws.amazon.com/savingsplans/latest/userguide/what-is-savings-plans.html)
- [RDS Proxy](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-proxy.html) · [RDS 蓝绿部署](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/blue-green-deployments.html)
- [RDS 扩展支持](https://aws.amazon.com/rds/extended-support/)
- [RDS 安全最佳实践](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_BestPractices.Security.html)
