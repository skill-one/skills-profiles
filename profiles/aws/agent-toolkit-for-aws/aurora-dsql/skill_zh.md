# Amazon Aurora DSQL

## 概述

Aurora DSQL 是一种无服务器、兼容 PostgreSQL 的分布式 SQL 数据库。此技能通过 `psql` 脚本和 PostgreSQL 驱动程序提供直接数据库交互、模式管理、迁移支持、多租户模式以及查询计划的可解释性。

**主要功能：**

- 通过 `psql` 和生成的 IAM 认证令牌执行直接查询（参见 [`scripts/psql-connect.sh`](scripts/psql-connect.sh)）
- 使用 DSQL 约束进行模式管理（每笔交易一个 DDL，异步索引）
- 安全的数据迁移（列级别、约束级别、MySQL→DSQL）
- 通过 `tenant_id` + 参数化 SQL 实现多租户隔离
- 基于 IAM 的认证，令牌过期时间为 15 分钟
- 慢查询的查询计划诊断（EXPLAIN ANALYZE + GUC 实验）

推荐使用 `psql` 和 `aws dsql generate-db-connect-auth-token` 进行 IAM 认证会话。应用程序代码应使用特定语言的 [DSQL 连接器和 SDK](https://docs.aws.amazon.com/aurora-dsql/latest/userguide/aws-sdks.html)。对于 AWS 知识查找（服务文档、AWS API 调用），[AWS MCP 服务器](https://docs.aws.amazon.com/aws-mcp/latest/userguide/mcp-server.html) 是首选的 MCP 集成。

---

## 参考文件

按需加载这些文件以获取详细指导：

### [development-guide.md](references/development-guide.md)

**何时：** 在实现模式更改或数据库操作之前始终加载
**包含：** [最佳实践](references/development-guide.md)、DDL 规则、连接模式、事务限制、数据类型序列化模式、应用程序层参照完整性指令、安全最佳实践

### 查询执行：

#### [database-tools.md](references/database-tools.md)

**何时：** 当您需要针对 DSQL 执行即席查询的详细语法和示例时加载。优先使用 `psql`（通过 [`scripts/psql-connect.sh`](scripts/psql-connect.sh)）进行即席查询——直接执行而不是编写一次性脚本。
**包含：** 基于 `psql` 的只读和写入模式、事务语义、[输入验证](references/input-validation.md)

### MCP（AWS 知识 / API）：

#### [mcp-setup.md](references/mcp-setup.md)

**何时：** 在配置或推荐 AWS MCP 服务器进行 AWS 知识查找、AWS API 访问或每个助手安装时加载。
**包含：** 何时使用 `psql` 与 AWS MCP 服务器、指向规范 AWS 设置文档的指针、凭证提醒。

#### [mcp-tools.md](references/mcp-tools.md)

**何时：** 在调用 AWS MCP 服务器工具以验证 DSQL 服务限制、获取文档或驱动 AWS API 调用时加载。
**包含：** 工具界面——知识 (`aws___search_documentation`，`aws___read_documentation`，`aws___recommend`，`aws___retrieve_skill`，`aws___list_regions`，`aws___get_regional_availability`) 和 API (`aws___call_aws`，`aws___run_script`，`aws___get_tasks`，`aws___get_presigned_url`)；指向 documentation-tools.md。

#### [documentation-tools.md](references/documentation-tools.md)

**何时：** 在查找 DSQL 服务限制、获取特定 AWS 文档页面或轮询通过 AWS MCP 服务器启动的长时间运行的 AWS API 调用时加载。
**包含：** AWS 知识工具的详细参数和示例调用。

#### [platforms/](references/platforms/) — 每个助手安装说明

**何时：** 在在特定编码助手内部安装 AWS MCP 服务器时加载。
**包含：** 每个助手的入口点详细信息——[claude-code.md](references/platforms/claude-code.md)，[codex.md](references/platforms/codex.md)，[gemini.md](references/platforms/gemini.md)，[kiro.md](references/platforms/kiro.md)。

### [language.md](references/language.md)

**何时：** **必须** 在编写 DSQL 连接代码之前加载。镜像链接的 `example_preferred.<ext>` 以选择驱动程序——内存编写的连接会偏离规范 IAM 令牌刷新模式。规范入口点示例（加载 `language.md` 以获取完整的驱动程序列表 + 池/TLS/令牌刷新详细信息）：

- Python: `import aurora_dsql_psycopg as dsql` → `dsql.connect(host, region, user)`
- JS (node-postgres): `import { AuroraDSQLPool } from "@aws/aurora-dsql-node-postgres-connector"` → `new AuroraDSQLPool({ host, user })`
- JS (postgres.js): `import { auroraDSQLPostgres } from "@aws/aurora-dsql-postgresjs-connector"` → `auroraDSQLPostgres({ host, user })`
- Go (pgx): `import "github.com/awslabs/aurora-dsql-connectors/go/pgx/dsql"`
- Java (JDBC): `software.amazon.dsql:aurora-dsql-jdbc-connector:1.4.0` → `jdbc:aws-dsql:postgresql://...`

**包含：** 每种语言的规范 DSQL 连接器包、驱动程序选择、框架模式、IAM 认证令牌刷新和 TLS 配置，以及 Python / JavaScript / TypeScript / Go / Java / Rust 的连接代码示例。

### [troubleshooting.md](references/troubleshooting.md)

**何时：** 在调试错误或意外行为时加载。应始终查阅 OCC 错误、连接失败或意外查询结果。
**包含：** 常见陷阱、错误消息、解决方案

### [onboarding.md](references/onboarding.md)

**何时：** 用户明确请求“开始使用 DSQL”或类似短语
**包含：** 新用户的交互式分步指南

### [access-control.md](references/access-control.md)

**何时：** **必须** 在创建数据库角色、授予权限、为应用程序设置模式或处理敏感数据时加载。始终使用作用域角色为应用程序——使用 `dsql:DbConnect` 创建数据库角色。
**包含：** 作用域角色设置、IAM 到数据库角色映射、敏感数据的模式分离、角色设计模式

### 认证与操作：

#### [auth/authentication-guide.md](references/auth/authentication-guide.md)

**何时：** **必须** 在处理 IAM 认证令牌、密钥、SSL/TLS、连接池或审计日志时加载。
**包含：** 令牌生命周期、密钥存储模式、SSL/TLS 设置、连接池指导、审计日志集成。

#### [auth/connectivity-tools.md](references/auth/connectivity-tools.md)

**何时：** 在选择驱动程序/ORM/适配器或规划批量数据加载时加载。
**包含：** 指向规范 AWS DSQL 连接工具页面（驱动程序、ORM、适配器）和批量加载文档页面的指针。

#### [auth/scaling-guide.md](references/auth/scaling-guide.md)

**何时：** 在为扩展而设计时加载——连接池、批量优化、热键避免、标识符选择。
**包含：** 水平扩展策略、池大小、批量大小指导、IDENTITY/SEQUENCE 缓存权衡、序列缓存规则。

### 实现示例：

#### [workflow-patterns.md](references/workflow-patterns.md)

**何时：** 在查找常见多步骤 DSQL 工作流的示例（模式探索、CREATE+INDEX、安全迁移、批量插入、应用程序层外键检查）时加载。
**包含：** 五个规范模式，使用 `psql` / 驱动程序代码。

#### [dsql-examples.md](references/dsql-examples.md)

**何时：** 在查找特定实现示例时加载。
**包含：** `examples/*.md` 索引（连接、模式、数据操作、迁移、模式）。

### DDL 迁移（模块化）：

#### [ddl-migrations/overview.md](references/ddl-migrations/overview.md)

**何时：** **必须** 在执行 DROP COLUMN、RENAME COLUMN、ALTER COLUMN TYPE 或 DROP CONSTRAINT 时加载。
**包含：** 表重创建模式概述、事务规则、常见验证与交换模式

#### [ddl-migrations/column-operations.md](references/ddl-migrations/column-operations.md)

**何时：** 执行 DROP COLUMN、ALTER COLUMN TYPE、SET/DROP NOT NULL、SET/DROP DEFAULT 迁移时加载。
**包含：** 列级别更改的逐步迁移模式

#### [ddl-migrations/constraint-operations.md](references/ddl-migrations/constraint-operations.md)

**何时：** 执行 ADD/DROP CONSTRAINT、MODIFY PRIMARY KEY、列拆分/合并迁移时加载。
**包含：** 约束和结构更改的逐步迁移模式

#### [ddl-migrations/batched-migration.md](references/ddl-migrations/batched-migration.md)

**何时：** 迁移超过 3,000 行的表时加载。
**包含：** 基于 OFFSET 和游标的基础批量模式、进度跟踪、错误处理

### MySQL 迁移（模块化）：

#### [mysql-migrations/type-mapping.md](references/mysql-migrations/type-mapping.md)

**何时：** **必须** 在将 MySQL 模式迁移到 DSQL 时加载。
**包含：** MySQL 数据类型映射、功能替代方案、DDL 操作映射

#### [mysql-migrations/ddl-operations.md](references/mysql-migrations/ddl-operations.md)

**何时：** 在将 MySQL DDL 操作转换为 DSQL 等价物时加载。
**包含：** ALTER COLUMN、DROP COLUMN、AUTO_INCREMENT、ENUM、SET、外键迁移模式

#### [mysql-migrations/full-example.md](references/mysql-migrations/full-example.md)

**何时：** 在将完整的 MySQL 表迁移到 DSQL 时加载。
**包含：** 端到端 MySQL CREATE TABLE 迁移示例，包含决策摘要

### 查询计划可解释性（模块化）：

**何时：** **必须** 在 Workflow 8 阶段 0 加载所有四个——[query-plan/plan-interpretation.md](references/query-plan/plan-interpretation.md)，[query-plan/catalog-queries.md](references/query-plan/catalog-queries.md)，[query-plan/guc-experiments.md](references/query-plan/guc-experiments.md)，[query-plan/report-format.md](references/query-plan/report-format.md)
**包含：** DSQL 节点类型 + 节点持续时间数学 + 估计误差范围，pg_class/pg_stats/pg_indexes SQL + 相关谓词验证，GUC 实验程序 + 30 秒跳过协议，所需报告结构 + 元素清单 + 支持请求模板

---

## 查询执行

使用 `psql` 和新鲜生成的 IAM 认证令牌执行即席 DSQL 查询。捆绑的 [`scripts/psql-connect.sh`](scripts/psql-connect.sh) 包含令牌生成、TLS 配置和单语句保护——优先使用它而不是手工编写的 `psql` 调用。

**只读：**

```bash
./scripts/psql-connect.sh --cluster <cluster-id> --command "SELECT * FROM entities LIMIT 10"
```

**写入/DDL（需要 IAM 管理员认证令牌）：**

```bash
./scripts/psql-connect.sh --cluster <cluster-id> --admin --command "CREATE INDEX ASYNC ..."
```

**模式发现：** 没有特殊的 `list_tables` 辅助程序——使用 information_schema：

```sql
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';
```

参见 [database-tools.md](references/database-tools.md) 获取详细用法和示例。

### 通过 AWS MCP 服务器进行 AWS 知识查找（可选）

当连接到 [AWS MCP 服务器](https://docs.aws.amazon.com/aws-mcp/latest/userguide/mcp-server.html) 时，其 `aws___search_documentation` 和 `aws___read_documentation` 工具可以在建议用户之前验证 DSQL 服务限制。下表中的数值限制是默认值，可能会更改——当用户的决策取决于确切的限制时，请先验证它：

| 限制                                   | 默认       | 验证查询                       |
| --------------------------------------- | ------------- | ---------------------------------- |
| 每笔交易修改的最大行数                | 3,000         | `aurora dsql transaction limits`   |
| 每个写入交易修改的最大数据量          | 10 MiB        | `aurora dsql transaction limits`   |
| 最大事务持续时间                        | 5 分钟     | `aurora dsql transaction limits`   |
| 每个集群的最大连接数                  | 10,000        | `aurora dsql connection limits`    |
| IAM 认证令牌过期时间                  | 15 分钟    | `aurora dsql authentication token` |
| 最大连接持续时间                        | 60 分钟    | `aurora dsql connection limits`    |
| 每个表的最大索引数                    | 24            | `aurora dsql index limits`         |
| 每个索引的最大列数                    | 8             | `aurora dsql index limits`         |
| IDENTITY/SEQUENCE 缓存值              | 1 或 >= 65536 | `aurora dsql sequence cache`       |

**何时验证：** 在建议批量大小、连接池设置或模式设计时——如果达到限制会导致失败。不需要验证一般指导或当确切的数字不影响用户的决策。

**后备：** 如果 AWS MCP 服务器不可用，请使用上表中的默认值，并告知用户应将限制与 [DSQL 文档](https://docs.aws.amazon.com/aurora-dsql/latest/userguide/) 进行验证。

## 可用的 CLI 脚本

[scripts/](scripts/) 中的 Bash 脚本用于集群管理（创建、删除、列出、集群信息）和 `psql` 连接。参见 [references/scripts-guide.md](references/scripts-guide.md) 获取用法。对于批量数据加载，请参阅 [Loading data into Aurora DSQL](https://docs.aws.amazon.com/aurora-dsql/latest/userguide/loading-data.html)。

**始终** 优先使用 `scripts/create-cluster.sh`。该脚本发出一个 **单个原子** `CreateCluster` 调用，其中包含嵌入的标签——与 AWS DSQL API 形状匹配，输出可解释。

| 任务 | 脚本 | 示例 |
|---|---|---|
| 创建带标签的集群 | [`scripts/create-cluster.sh`](scripts/create-cluster.sh) | `./scripts/create-cluster.sh --created-by <model-id> --tags Environment=eval,Project=dsql-skill-eval` |
| 列出集群 | [`scripts/list-clusters.sh`](scripts/list-clusters.sh) | `./scripts/list-clusters.sh --region us-east-1` |
| 检查集群 | [`scripts/cluster-info.sh`](scripts/cluster-info.sh) | `./scripts/cluster-info.sh <cluster-id>` |
| 通过 psql 连接 | [`scripts/psql-connect.sh`](scripts/psql-connect.sh) | `./scripts/psql-connect.sh --cluster <id> --command "SELECT 1"` |

---

## 快速入门

### 1. 列出表并探索模式

```
./scripts/psql-connect.sh --cluster <id> --command "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
./scripts/psql-connect.sh --cluster <id> --command "SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_schema = 'public' AND table_name = '<table>' ORDER BY ordinal_position"
```

### 2. 查询数据

```
使用 psql-connect.sh（或应用程序代码中的语言连接器）进行 SELECT 查询
始终在 WHERE 子句中包含 `tenant_id` 对于多租户应用程序
**必须** 使用 `safe_query.build()` 构建 SQL——参见 references/input-validation.md
```

### 3. 执行模式更改

```
使用 ./scripts/psql-connect.sh --admin（或使用 IAM 管理员认证令牌的语言连接器）进行 DDL
遵循每笔交易一个 DDL 规则
始终在单独的语句中使用 `CREATE INDEX ASYNC`
ALTER COLUMN TYPE, DROP COLUMN, DROP CONSTRAINT → 表重创建模式（Workflow 6）
```

---

## 常见任务

### Workflow 0: 验证依赖项

检查所需工具，如果缺少任何工具，请警告用户。

**约束：**

- 您 **必须** 在继续之前验证以下工具可用性：`psql`（>=14 for SNI support）和 AWS CLI v2 with `aws dsql generate-db-connect-auth-token`（以及 `generate-db-connect-admin-auth-token` for DDL/role setup）
- 您 **应该** 确认 AWS MCP 服务器可用，当用户的决策取决于精确的服务限制时；如果缺失，使用上表中的默认值，并告知用户应将限制与 DSQL 文档进行验证
- 您 **必须** 使用清晰的消息告知用户缺少任何工具
- 您 **必须** 询问用户是否希望在缺少工具的情况下继续
- 您 **必须** 使用作用域（非管理员）IAM 认证令牌进行只读诊断，如果用户配置了作用域角色；保留 IAM 管理员认证令牌用于集群设置、角色授予和 DDL
- 对于集群生命周期（创建 / 检查 / 删除），请参阅 [Workflow 0a](#workflow-0a-cluster-lifecycle)
- 在编写应用程序代码之前，**还必须** 验证每种语言的特定 DSQL 连接器 per [Workflow 0b](#workflow-0b-verify-language-connector)

### Workflow 0a: 集群生命周期

**应该** 使用捆绑脚本进行集群创建和删除——它们发出原子的 `aws dsql` CLI 调用并处理输出。

**创建带标签的集群：**

```bash
./scripts/create-cluster.sh --created-by <model-id> --tags Environment=eval,Project=dsql-skill-eval
```

**检查集群（状态、标签、端点、删除保护）：**

```bash
./scripts/cluster-info.sh <cluster-id>
```

**删除集群：**

```bash
./scripts/delete-cluster.sh <cluster-id> [--force]   # --force 跳过非 TTY 中的确认提示
```

在仅 MCP 环境中（没有 Shell 访问），等效调用通过 AWS MCP 服务器的 `aws___call_aws` 工具进行。该工具接受 JSON 负载——使用与 AWS API 操作匹配的参数调用它：

```json
{"service": "dsql", "operation": "CreateCluster",
 "parameters": {"tags": {"created_by": "<model-id>", "Environment": "eval", "Project": "dsql-skill-eval"}, "deletionProtectionEnabled": true}
```

```json
{"service": "dsql", "operation": "GetCluster", "parameters": {"identifier": "<cluster-id>"}}
```

```json
{"service": "dsql", "operation": "DeleteCluster", "parameters": {"identifier": "<cluster-id>"}
```

`CreateCluster` 和 `DeleteCluster` 在 DSQL 端是异步的——API 立即返回集群的当前 `status` (`CREATING` / `DELETING`)。通过重新调用 `aws___call_aws` 使用 `dsql:GetCluster` 来轮询就绪状态，直到 `.status == "ACTIVE"`（创建）或调用返回 404（删除）。`aws___get_tasks` 用于轮询 MCP 端的长时间运行工具调用——不是 DSQL API。

参见 [AWS CLI `aws dsql` 参考](https://docs.aws.amazon.com/cli/latest/reference/dsql/) 以获取完整参数细节和调用上下文。

### Workflow 0b: 验证语言连接器

在编写应用程序代码之前，**必须** 根据 [language.md](references/language.md) 验证每种语言的特定 DSQL 连接器是否已安装。连接器是规范 IAM 令牌刷新路径；裸驱动程序 (`pg`, `psycopg`, `pgx`, `tokio-postgres`) 在第一个 15 分钟令牌过期之前有效，然后开始在新连接上返回认证错误——尝试裸形式的 DSQL 用户报告此为 DSQL 错误。**必须** 安装：

- Python: `aurora-dsql-python-connector` + 所选驱动程序轮
- Node.js: `@aws/aurora-dsql-node-postgres-connector` 或 `@aws/aurora-dsql-postgresjs-connector`
- Go: `github.com/awslabs/aurora-dsql-connectors/go/pgx`
- Java (JDBC): `software.amazon.dsql:aurora-dsql-jdbc-connector`
- Rust: `aurora-dsql-sqlx-connector`

如果为所选运行时不可用连接器，请记录手动令牌刷新策略，并安排与用户在编写代码之前进行交互。
