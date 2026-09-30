---
name: rds-oss
description: 提供有关 Amazon RDS 开源引擎（MySQL、MariaDB、PostgreSQL）的实例创建、升级规划、承诺定价、代理评估和蓝绿部署的建议。处理任何 RDS MySQL、MariaDB 或 PostgreSQL 的问题，包括创建可生产使用的 RDS MySQL 实例、配置 RDS PostgreSQL 数据库、运行 RDS 升级顾问以检查我的 RDS MySQL 实例、我的升级选项是什么、将 RDS MariaDB 从 10.6 升级到最新版本、是否应为 db.r7g.2xlarge RDS MySQL 购买保留实例或节省计划、在 RDS MySQL 8.0 上将 VARCHAR 列更改为 INT 列（使用蓝绿部署），以及当 PgBouncer 已经以事务模式运行时 RDS 代理是否有帮助。涵盖遵循生产最佳实践创建实例、描述数据库实例和描述数据库引擎版本的升级目标工作流、通过 SSM 或直接连接进行实时预检查、保留实例（RI）与节省计划（DSP）的承诺定价、RDS 代理与 PgBouncer 的对比，以及具有 binlog 重放兼容性的蓝绿生命周期。
---

# RDS OSS Advisor (MySQL, MariaDB, PostgreSQL)

## 概述

适用于 Amazon RDS 开源引擎（**MySQL**、**MariaDB** 和 **PostgreSQL**）的顾问。包含五个决策领域：

1. **实例创建** — 使用最佳实践默认值（最新版本、多可用区、加密、性能洞察、密钥管理器密码管理）创建生产就绪实例
2. **升级规划** — 识别实例、枚举目标、运行实时预检查、标记计划回归、显示预/后检查清单
3. **承诺定价** — 估算 RI 和数据库节省计划对于稳定工作负载的节省
4. **RDS Proxy 评估** — 基于连接利用率和固定风险，决定是否值得使用代理
5. **蓝/绿部署** — 规划低停机时间的 DDL 或重大升级，并进行 DDL 兼容性分析

生成成本估算、预检查结果和 CLI 命令。对于实例创建，执行带有生产最佳实践的 `create-db-instance` 调用。对于升级、购买和切换，仅提供建议，未经明确用户确认不会执行。

仅限于 RDS 开源引擎。对于 Aurora，使用 `amazon-aurora`。对于 Oracle、SQL Server、Db2，使用特定引擎的技能。

建议使用 AWS MCP 服务器执行命令，但不是必需的；所有操作也可以通过 AWS CLI 执行。

## 决策指南

| 用户询问关于… | 转到 |
|---|---|
| 创建、配置或设置新的 RDS MySQL/MariaDB/PostgreSQL 实例 | 下面的 [生产实例创建](#生产实例创建) |
| 升级、目标版本、预/后升级清单、升级预检查、读取副本升级顺序 | [references/upgrade-workflow.md](references/upgrade-workflow.md) |
| Reserved Instance、RI、Database Savings Plan、DSP、1 年 vs 3 年、多可用区承诺、无/部分/全部预付 | [references/commitment-pricing-workflow.md](references/commitment-pricing-workflow.md) |
| RDS Proxy、连接池、连接过多、Lambda DB 连接、代理固定、PgBouncer vs Proxy | [references/proxy-advisor-workflow.md](references/proxy-advisor-workflow.md) |
| Blue/Green、零停机时间 DDL、切换、最小停机时间下的模式更改、生产上的类型更改 | [references/bluegreen-advisor-workflow.md](references/bluegreen-advisor-workflow.md) |

宽泛请求（“帮助我处理 RDS”）？将五个选项作为单独的一行呈现。如果用户提供了实例 ID，则提供一般健康检查（引擎 + 版本 + 连接利用率）作为入口点。

超出范围（Aurora、Oracle、SQL Server、Db2、备份策略、性能洞察深度分析）：从一般知识回答，指出此技能不涵盖，并指向正确的特定引擎技能。

## RDS 与 Aurora — 切勿混淆

RDS 开源引擎和 Aurora 是具有不同语义的不同产品。您**必须**不将 Aurora 概念应用于 RDS：

| 概念 | RDS（此技能） | Aurora（使用 `amazon-aurora`） |
|---|---|---|
| LTS 发布 | ❌ 不存在 | ✅ 有 LTS 版本 |
| 无服务器模式 | ❌ 不存在 | ✅ Aurora 无服务器 |
| I/O-优化存储 | ❌ 不存在 | ✅ aurora-iopt1 |
| 数据 API | ❌ 独立 RDS 不适用 | ✅ Aurora 无服务器集群 |
| 实例拓扑 | 基于实例 (`describe-db-instances`) | 基于集群 (`describe-db-clusters`) |
| 升级范围 | 每个实例 | 每个集群（写入者 + 读取者一起） |
| DSP 术语选项 | 1 年和 3 年 | 仅 1 年 |
| 定价模型 | 按需 + RI + DSP | 按需 + RI + DSP + I/O 定价 |

如果用户询问任何 Aurora 特定概念，路由到 `amazon-aurora`。如果实例是 Aurora（引擎 = `aurora-mysql` 或 `aurora-postgresql`），则停止并重定向。

## 生产实例创建

当用户要求创建或配置用于生产的新 RDS MySQL、MariaDB 或 PostgreSQL 实例时，您必须默认应用以下最佳实践：

1. **使用最新稳定的主版本** — 运行 `aws rds describe-db-engine-versions --engine <engine> --query "DBEngineVersions[].EngineVersion"` 查找最新版本。对于 MySQL，优先选择 8.4.x 而不是 8.0（8.0 的标准支持结束日期早于 8.4 — 请参阅 [RDS 扩展支持](https://aws.amazon.com/rds/extended-support/) 获取日期）。对于 PostgreSQL，使用最新主版本。对于 MariaDB，使用最新主版本。
2. **启用多可用区** — 设置 `--multi-az` 以实现自动故障转移。
3. **使用客户管理的 KMS 密钥启用存储加密** — 设置 `--storage-encrypted --kms-key-id <key-arn>`。客户管理的密钥可以完全控制密钥轮换、访问策略和跨账户共享。
4. **禁用公共访问** — 设置 `--no-publicly-accessible` 以确保实例不能从互联网访问。
5. **将备份保留期设置为 7 天** — 设置 `--backup-retention-period 7`。
6. **启用带有 7 天保留期的性能洞察** — 设置 `--enable-performance-insights --performance-insights-retention-period 7`。如果性能洞察捕获包含敏感数据的查询（例如，WHERE 子句中的字面值），请指定 `--performance-insights-kms-key-id <key-arn>` 以使用客户管理的 KMS 密钥加密存储。
7. **启用删除保护** — 设置 `--deletion-protection`。
8. **避免默认主用户名** — 不要使用众所周知的名称，如 `admin`、`root`、`postgres` 或 `master`，这些名称使凭证猜测攻击更容易。选择自定义的 `--master-username`（例如，应用程序或团队特定的名称）。
9. **通过密钥管理器管理主密码** — 设置 `--manage-master-user-password` 而不是提供明文 `--master-user-password`。这会在密钥管理器中自动创建和轮换密码。对于生产实例，**不要**接受或使用明文密码。
10. **使用 gp3 存储** — 设置 `--storage-type gp3`。它比 gp2 更便宜、更快，且无需购买最小 IOPS。
11. **标记实例，以便客户可以识别通过此技能创建的资源** — 设置 `--tags Key=created_by,Value=rds-oss-skill Key=generation_model,Value={your-model-id}`（请参阅下面的资源标记）。
12. **强制传输中的连接使用 TLS** — 创建或修改 DB 参数组以要求加密连接：`require_secure_transport=ON`（MySQL/MariaDB），`rds.force_ssl=1`（PostgreSQL）。
13. **将数据库日志导出到 CloudWatch Logs 并使用 KMS 加密** — 设置 `--enable-cloudwatch-logs-exports` 以便数据库级安全事件（失败的登录、可疑查询）在中心位置可见。使用 `["error","slowquery","audit"]`（MySQL/MariaDB，注意：`audit` 流需要先启用审计日志，否则为空 — 在 RDS MySQL 中通过 Option Group 中的 MARIADB_AUDIT_PLUGIN，在 RDS MariaDB 中通过内置服务器审计参数，如 `server_audit_logging=1` 在参数组中）和 `["postgresql"]`（PostgreSQL）。数据库日志可能包含 SQL 字面值和用户名，因此您**必须**在生成的 `/aws/rds/instance/<name>/*` 日志组上配置一个 KMS 密钥，以保护敏感数据。

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

实例创建后，运行以下命令配置 TLS 强制和日志组加密（这些是用户执行的步骤，该技能仅呈现但不直接调用）：

```bash
# 创建带有 TLS 强制的自定义参数组（MySQL 示例）
aws rds create-db-parameter-group --db-parameter-group-family mysql8.4 \
  --db-parameter-group-name <name>-tls --description "TLS 强制"
aws rds modify-db-parameter-group --db-parameter-group-name <name>-tls \
  --parameters "ParameterName=require_secure_transport,ParameterValue=ON,ApplyMethod=pending-reboot"
aws rds modify-db-instance --db-instance-identifier <name> \
  --db-parameter-group-name <name>-tls --apply-immediately

# 使用 KMS 加密 CloudWatch Logs 日志组
aws logs associate-kms-key --log-group-name /aws/rds/instance/<name>/error --kms-key-id <kms-key-arn>
aws logs associate-kms-key --log-group-name /aws/rds/instance/<name>/slowquery --kms-key-id <kms-key-arn>
```

**约束：**

- 对于生产环境，**必须**使用 `--manage-master-user-password`。**绝对不要**使用 `--master-user-password` 并提供明文密码用于生产实例。
- **必须**通过 `describe-db-engine-versions` 检查最新可用版本，而不是硬编码版本。
- **必须**启用多可用区、加密、性能洞察（7 天）、备份保留（7 天）和删除保护，除非用户明确说明否则如此。
- 如果用户说“生产”或“生产就绪”，则应用所有上述内容，无需询问。

### 资源标记（资源创建时始终应用）

创建任何 RDS 实例（`create-db-instance`）时，**始终**使用 RDS 列表记录 `--tags` 语法包含以下标签：

`--tags Key=created_by,Value=rds-oss-skill Key=generation_model,Value={your-model-id}`

示例：`--tags Key=created_by,Value=rds-oss-skill Key=generation_model,Value=claude-sonnet-4-20250514`

即使用户没有提到标记，也包含这些标签，以便他们可以识别通过此技能创建的资源。如果用户提供其他标签，请将这些标签附加到他们的标签中，而不是替换它们。在通过 `add-tags-to-resource` 标记或蓝/绿部署期间也是如此。

## 常见任务

### 1. 验证依赖项

在运行工作流之前，请参阅 [references/verify-dependencies.md](references/verify-dependencies.md) 了解工具和凭证要求。

### 2. 分类和路由

使用 [决策指南](#决策指南) 选择工作流参考、目录呈现（宽泛请求）或一般知识答案（超出范围）。

**约束：**

- 您**必须**命名您正在路由的工作流
- 您**必须**传递用户已经提供的实例 ID、区域、引擎或工作负载详细信息 — 不要重新询问
- 如果请求跨越两个工作流（例如，“最小停机时间升级” = 升级 + 蓝绿），您可以问一个澄清问题
- 您**必须**不将 Aurora、Oracle、SQL Server 或 Db2 的问题路由到这里 — 这些引擎具有不同的工具

### 3. 执行工作流

加载匹配的参考并遵循其 `## Tasks` 部分。

**约束：**

- 您**必须**在运行它之前解释正在执行哪个步骤以及正在调用哪个工具
- 您**必须**不执行 `modify-*`、`switchover-*`、购买 API 或 `create-db-proxy`。允许：`create-db-instance`（用于新实例配置）、`describe-*`、`list-*`、`get-*`、`send-command` 用于 SSM 预检查。
- 您**必须**不直接处理数据库凭证。使用用户提供的密钥 ARN、预配置的 SSM 参数，或要求用户粘贴脚本输出。
- 当实时调用或捆绑脚本无法运行时，您**必须**报告确切的障碍，并执行离线回退或要求用户输入。您**必须**不编造命令输出、分析器结果、定价数字或版本列表 — 没有事实依据的看似合理的答案比拒绝更糟，因为用户会根据它采取行动。
- 如果多个工作流运行，以 2-4 行的总结结束，链接到先前的输出。

每个工作流参考都包含其自己的工具调用示例。

### 始终呈现的关键事实

这些 RDS-OSS 特定的事实使此技能与普通的 MySQL/PostgreSQL/MariaDB 知识区分开来。通常，一般答案会将 RDS 与 Aurora 混淆，省略 CLI 命令名称，或在这是一个建议技能时进行行动。

**对于“运行我的 RDS MySQL 实例的 RDS 升级顾问”，您必须告诉用户以下五个事实：**

1. **通过 `aws rds describe-db-instances` 识别实例**（**不是** `describe-db-clusters` — RDS MySQL/MariaDB/PostgreSQL 是**基于实例**的，不是基于集群的；`describe-db-clusters` 仅适用于 Aurora）。
2. **从响应中检测引擎**（`mysql`、`mariadb` 或 `postgres`） — 不要假设。
3. **使用 `aws rds describe-db-engine-versions` 列出有效升级目标** — 具体使用当前引擎和主版本作为过滤器。这是如何枚举允许的升级路径的方法。
4. **明确呈现最新版本建议**（例如，“8.0.40 是最新的 8.0 小版本，8.4.x 是下一个主版本”）。
5. ****不要**提及 LTS — RDS 没有 LTS 概念（请参阅 [RDS 与 Aurora](#rds-vs-aurora--do-not-confuse)）。提供 LTS 建议表示在 RDS 和 Aurora 之间路由混淆。同样，不要引用 `amazon-aurora`，除非实例是 Aurora。

**关键工作流规则 — 当命名的实例无法定位时：** 如果 `describe-db-instances --db-instance-identifier <id>` 返回无结果或 `DBInstanceNotFoundFault`，您**必须**仍然为用户走完完整的顾问工作流 — 名称每个步骤（`describe-db-instances`，然后引擎检测，然后 `describe-db-engine-versions`，然后版本建议，然后预升级清单） — 并解释每个步骤的输出将是什么。**绝对不要**放弃并询问“您能再检查一下实例 ID 吗？”然后停止。用户是在询问顾问程序，而不是让您执行实时发现。如果您看不到实例，请将工作流作为模板呈现，用户在提供正确的标识符后可以运行。

**对于“将我的 RDS MariaDB 从 X 升级到最新版本”，您必须告诉用户以下六个事实：**

1. **通过 `describe-db-instances` 检测引擎为 `mariadb`**。
2. **使用 `describe-db-engine-versions`（`--engine mariadb`）识别目标版本，而不是手维护的列表**。
3. **提供 SSM 或直接连接预检查方法** — RDS MariaDB 可以通过客户端主机上的 SSM Run Command 或通过直接 mysql-client 连接进行预检查。
4. ****不要**使用 RDS Data API — MariaDB 不支持数据 API。这是一个经典的陷阱。数据 API 仅适用于 Aurora 无服务器和部分集群，永远不会用于 RDS MariaDB。
5. **运行 [upgrade-prechecks-mysql.md](references/upgrade-prechecks-mysql.md) 中的 MySQL 兼容预检查查询** — 移除的功能、保留关键字、`sql_mode` 变更。MariaDB 重用 MySQL 预检查集，因为它是一个 MySQL 分叉。
6. **拒绝执行升级** — 顾问仅提供建议。建议在测试环境中进行快照和恢复的干运行，然后再继续。明确说明您不会运行 `modify-db-instance --engine-version`。
7. **对于“2x db.r7g.2xlarge RDS MySQL 24/7 — 购买 RI 或节省计划？”，您必须告诉用户以下七个事实：**

1. **离线运行 `[rds_commitment_pricing_analyzer.py](scripts/rds_commitment_pricing_analyzer.py)`，使用参数 `--instance-type db.r7g.2xlarge --engine mysql --num-instances 2`。以代码块形式打印确切的命令。**
2. **展示所有五个选项的完整对比表** — 按需、1年预留实例、3年预留实例、1年数据库节省计划、3年数据库节省计划 — 并以**美元和百分比**的形式展示每个选项相对于按需的节省金额。
3. **鉴于声明的2年以上的信心和24/7使用情况，推荐3年预留实例**。
4. **解释 RDS 数据库节省计划仅针对 r7g 系列** — 数据库节省计划的覆盖范围是系列级别的，而不是实例级别的，如果用户可能在该系列内调整大小，这是一个主要优势。
5. **提及3年锁定期的权衡** — 如果工作负载发生变化或系列被取代，承诺将无法完全恢复。
6. **注意 RDS 预留实例是区域锁定的** — 跨区域移动工作负载将放弃预留实例的优惠。
7. ****绝对不要包含购买步骤** — 没有“下一步”部分包含购买指南。没有“转到控制台 → 预留实例 → 购买”。没有 `aws rds purchase-reserved-db-instances-offering` 或 `aws savingsplans create-savings-plan` 命令。**这是严格的禁止。** 此技能仅提供咨询，**绝对不能**指导用户执行购买。说“准备好购买时，请参考 AWS 控制台或 CLI 文档。”并停止。**不要**试图通过展示购买命令的示例来提供帮助。

**对于“在 RDS MySQL 8.0 上通过蓝绿部署将 VARCHAR(10) 列更改为 INT”，你必须告诉用户以下所有七个事实：**

1. **首先验证先决条件**：`binlog_format=ROW`、自动备份已启用（保留期 > 0）、实例处于 `available` 状态。
2. **解释为什么修改列类型会破坏二进制日志复制**：蓝绿部署通过重放二进制日志事件来复制蓝色 → 绿色。类型更改在两侧产生**不同的二进制表示**，因此针对 VARCHAR 记录的复制事件不能应用于 INT 列。这是根本原因，而不是“行格式”问题。
3. **使用 `aws rds create-blue-green-deployment` 创建绿色环境** — 包含确切的 CLI 命令名称，而不是通用描述。
4. **让绿色环境通过二进制日志复制来追赶**，然后再执行 DDL。
5. **在绿色环境追赶后应用架构更改**（修改列的 DDL）。
6. **立即切换**，使用 `aws rds switchover-blue-green-deployment` — **在执行不兼容的 DDL 后，不要让绿色与蓝色并行运行**。架构差异会破坏进一步的复制。
7. **切换后验证生产端点上的架构更改**，**你必须暂停并要求用户明确确认**，然后再提供 `switchover-blue-green-deployment` 命令，即使作为建议步骤。**不要**将切换列为顺序工作流中的自动下一步 — 说明切换是破坏性操作，会转移生产流量，然后问“准备好切换了吗？我会在你确认后给你确切的 CLI 命令。”只有用户确认后，你才应该发出 `switchover-blue-green-deployment` 命令。

**对于“我们在事务模式下运行 PgBouncer — RDS Proxy 会增加什么？”**，你必须告诉用户以下所有六个事实：**

1. **事务模式下的 PgBouncer 已经执行了激进的连接多路复用** — 这是代理的主要价值主张。在这种情况下，多路复用优势是边际的。
2. **RDS Proxy 增加的内容**：托管基础设施（无需操作或修补 EC2）。
3. **内置 IAM 身份验证** — RDS Proxy 原生支持 IAM 身份验证，而 PgBouncer 并非开箱即用。
4. **与 RDS 事件集成的自动故障转移** — 代理在几秒钟内对 RDS 故障转移事件做出反应；PgBouncer 需要外部健康检查和手动重新配置。
5. **与 Secrets Manager 集成的凭据轮换** — 代理可以从 Secrets Manager 拉取凭据，并在不停机的情况下进行轮换。
6. **建议**：如果 PgBouncer 正常工作，并且上述四个特性都没有特别需要，**保持使用 PgBouncer**。只有在需要 IAM 身份验证、托管故障转移或 Secrets-Manager-轮换的凭据时，才切换到 RDS Proxy。

## 安全注意事项

咨询技能 — 从不修改**现有** AWS 资源。唯一允许的写操作是 `create-db-instance` 用于新实例配置（见 [生产实例创建](#生产实例创建)）；其他都是只读操作。**绝对不要**直接处理凭据；优先使用短期凭据。

所需的最小 IAM 权限：`AmazonRDSReadOnlyAccess` + `CloudWatchReadOnlyAccess` + 范围限制的 `pricing:GetProducts` + `savingsplans:DescribeSavingsPlansOfferingRates`。对于实例创建，还需要 `rds:CreateDBInstance` + `rds:AddTagsToResource`，如果启用了 CloudWatch Logs 导出，还需要 `logs:CreateLogGroup`。SSM 预检查也需要在目标堡垒机上使用 `ssm:SendCommand` / `ssm:GetCommandInvocation`。

在所有指南中应用这些安全实践：

1. **传输中加密** — 对所有数据库连接强制执行 TLS（对于 MySQL/MariaDB，`require_secure_transport=ON`；对于 PostgreSQL，`rds.force_ssl=1`）。
2. **IAM 数据库身份验证** — 在支持的地方优先使用 IAM 身份验证而不是用户名/密码，并提供短期凭据。
3. **审计日志** — 建议启用数据库审计日志（通过 Option Group 中的 MARIADB_AUDIT_PLUGIN 在 RDS MySQL 中，通过 RDS MariaDB 的内置服务器审计参数，如 `server_audit_logging=1`，以及 PostgreSQL 的 `pgaudit` 扩展）和 CloudTrail 进行 API 级别审计。
4. **VPC 安全** — 在私有子网中部署实例。安全组应限制入站访问到特定的应用程序 CIDR 范围或安全组引用 — 绝不使用 `0.0.0.0/0`。
5. **凭据轮换** — `--manage-master-user-password` 提供通过 Secrets Manager 的自动轮换。
6. **监控和警报** — 建议对安全相关指标设置 CloudWatch 警报，例如 `DatabaseConnections` 峰值（可能的凭证泄露）和 `FreeableMemory` 下降（可能的资源耗尽攻击）。

**不要**授予上述权限之外的写/管理员权限以绕过权限错误。**不要**将 DB 密码存储在 SSM 参数或命令文本中 — 使用 Secrets Manager 并在命令中检索密钥。

## 故障排除

**访问被拒绝**。附加上述只读策略。

**凭据过期**。刷新，或回退到 `--offline` 用于承诺定价。

**超时 / 限制**。重试一次，然后缩小范围。SSM 预检超时：切换到直接连接或用户运行脚本。独立 RDS 不提供 RDS Data API。

**资源未找到**。验证区域/ID；确认它不是 Aurora *集群*（`describe-db-clusters`）。空的预留实例/数据库节省计划 — 回退到离线。

**用户要求执行更改**。咨询技能 — 对现有资源的修改通过 AWS 控制台或用户运行的 CLI 发生。

**Aurora 问题**。路由到 `amazon-aurora`。见上方 [RDS vs Aurora](#rds-vs-aurora--do-not-confuse)。

**Oracle / SQL Server / Db2 问题**。路由到 `rds-oracle`、`rds-sqlserver` 或 `rds-db2`。

## 其他资源

- [Amazon RDS 用户指南](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/)
- [RDS 定价](https://aws.amazon.com/rds/pricing/)
- [RDS MySQL 升级](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_UpgradeDBInstance.MySQL.html) · [RDS MariaDB 升级](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_UpgradeDBInstance.MariaDB.html) · [RDS PostgreSQL 升级](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_UpgradeDBInstance.PostgreSQL.html)
- [RDS 预留实例](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_WorkingWithReservedDBInstances.html) · [数据库节省计划](https://docs.aws.amazon.com/savingsplans/latest/userguide/what-is-savings-plans.html)
- [RDS Proxy](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-proxy.html) · [RDS 蓝绿部署](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/blue-green-deployments.html)
- [RDS 扩展支持](https://aws.amazon.com/rds/extended-support/)
- [RDS 安全最佳实践](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_BestPractices.Security.html)
