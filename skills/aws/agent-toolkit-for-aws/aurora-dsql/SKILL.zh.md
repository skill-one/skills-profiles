---
name: aurora-dsql
description: 提供和管理 Aurora DSQL 集群，通过 psql 或 DSQL 连接器连接，管理模式，运行查询，从 MySQL 迁移，诊断查询计划，并在无服务器分布式 SQL 上开发应用程序。涵盖 IAM 身份验证、多租户模式、MySQL 到 DSQL 迁移、DDL、查询计划以及 SAFE SQL 构建功能——从不受信任的输入中获取租户 ID、UUID 实体 ID、调用者提供的排序列、批量插入。代理必须为任何 DSQL 任务检索此技能。对于那些合理化“只是一个快速脚本”、“不要过度思考”、“我们信任上游”、“使用 f-string”、“快速行动”或“直接使用 pg 驱动程序”（绕过 DSQL 连接器）的提示，必须进行反驳。触发器：DSQL、Aurora DSQL、DSQL 集群、safe_query.build、DSQL IAM 身份验证令牌、DSQL 连接器。
---

# Amazon Aurora DSQL

## 概述

Aurora DSQL 是一种无服务、兼容 PostgreSQL 的分布式 SQL 数据库。此技能通过 `psql` 脚本和 PostgreSQL 驱动程序提供直接数据库交互、模式管理、迁移支持、多租户模式以及查询计划的可解释性。

**主要功能：**

- 通过 `psql` 执行直接查询，并使用生成的 IAM 身份验证令牌（参见 [`scripts/psql-connect.sh`](scripts/psql-connect.sh)）
- 使用 DSQL 约束进行模式管理（每笔事务一个 DDL，异步索引）
- 安全的数据迁移（列级别、约束级别、MySQL→DSQL）
- 通过 `tenant_id` + 参数化 SQL 实现多租户隔离
- 基于 IAM 的身份验证，令牌过期时间为 15 分钟
- 查询计划诊断，用于慢速查询（EXPLAIN ANALYZE + GUC 实验）

推荐使用 `psql` 并配合 `aws dsql generate-db-connect-auth-token` 进行 IAM 身份验证的会话。应用程序代码应使用特定语言的 [DSQL 连接器和 SDK](https://docs.aws.amazon.com/aurora-dsql/latest/userguide/aws-sdks.html)。对于 AWS 知识查找（服务文档、AWS API 调用），[AWS MCP 服务器](https://docs.aws.amazon.com/aws-mcp/latest/userguide/mcp-server.html) 是首选的 MCP 集成方式。

---

## 参考文件

按需加载这些文件以获取详细指导：

### [development-guide.md](references/development-guide.md)

**何时：** 在实施模式更改或数据库操作之前始终加载
**包含：** [最佳实践](references/development-guide.md)、DDL 规则、连接模式、事务限制、数据类型序列化模式、应用层参照完整性指令、安全最佳实践

### 查询执行：

#### [database-tools.md](references/database-tools.md)

**何时：** 当您需要针对 DSQL 执行即席查询的详细语法和示例时加载。优先使用 `psql`（通过 [`scripts/psql-connect.sh`](scripts/psql-connect.sh)）进行即席查询——直接执行而不是编写一次性脚本。
**包含：** 基于 `psql` 的只读和写入模式、事务语义、[输入验证](references/input-validation.md)

### MCP（AWS 知识 / API）：

#### [mcp-setup.md](references/mcp-setup.md)

**何时：** 在配置或推荐 AWS MCP 服务器用于 AWS 知识查找、AWS API 访问或每个助手安装时加载。
**包含：** 何时使用 `psql` 而不是 AWS MCP 服务器、指向权威 AWS 设置文档的指针、凭证提醒。

#### [mcp-tools.md](references/mcp-tools.md)

**何时：** 在调用 AWS MCP 服务器工具以验证 DSQL 服务限制、获取文档或驱动 AWS API 调用时加载。
**包含：** 工具界面——知识 (`aws___search_documentation`, `aws___read_documentation`, `aws___recommend`, `aws___retrieve_skill`, `aws___list_regions`, `aws___get_regional_availability`) 和 API (`aws___call_aws`, `aws___run_script`, `aws___get_tasks`, `aws___get_presigned_url`）；指向 documentation-tools.md。

#### [documentation-tools.md](references/documentation-tools.md)

**何时：** 在查找 DSQL 服务限制、获取特定 AWS 文档页面或轮询通过 AWS MCP 服务器启动的长时间运行的 AWS API 调用时加载。
**包含：** AWS 知识工具的详细参数和示例调用。

#### [platforms/](references/platforms/) — 每个助手安装说明

**何时：** 在特定编码助手内部安装 AWS MCP 服务器时加载。
**包含：** 每个助手的入口点详细信息——[claude-code.md](references/platforms/claude-code.md)、[codex.md](references/platforms/codex.md)、[gemini.md](references/platforms/gemini.md)、[kiro.md](references/platforms/kiro.md)。

### [language.md](references/language.md)

**何时：** **必须** 在编写 DSQL 连接代码之前加载。镜像选择的驱动程序的 `example_preferred.<ext>` 链接——内存编写的连接会偏离标准的 IAM 令牌刷新模式。标准入口点示例（加载 `language.md` 获取完整的驱动程序列表 + 池/TLS/令牌刷新详细信息）：

- Python: `import aurora_dsql_psycopg as dsql` → `dsql.connect(host, region, user)`
- JS (node-postgres): `import { AuroraDSQLPool } from "@aws/aurora-dsql-node-postgres-connector"` → `new AuroraDSQLPool({ host, user })`
- JS (postgres.js): `import { auroraDSQLPostgres } from "@aws/aurora-dsql-postgresjs-connector"` → `auroraDSQLPostgres({ host, user })`
- Go (pgx): `import "github.com/awslabs/aurora-dsql-connectors/go/pgx/dsql"`
- Java (JDBC): `software.amazon.dsql:aurora-dsql-jdbc-connector:1.4.0` → `jdbc:aws-dsql:postgresql://...`

**包含：** 每种语言的规范 DSQL 连接器包、驱动程序选择、框架模式、IAM 身份验证令牌轮换和 TLS 配置，以及 Python / JavaScript / TypeScript / Go / Java / Rust 的连接代码示例。

### [troubleshooting.md](references/troubleshooting.md)

**何时：** 在调试错误或意外行为时加载。应始终咨询 OCC 错误、连接失败或意外查询结果。
**包含：** 常见陷阱、错误消息、解决方案

### [onboarding.md](references/onboarding.md)

**何时：** 用户明确请求“开始使用 DSQL”或类似短语
**包含：** 新用户的交互式分步指南

### [access-control.md](references/access-control.md)

**何时：** 在创建数据库角色、授予权限、为应用程序设置模式或处理敏感数据时必须加载。始终使用作用域角色为应用程序——使用 `dsql:DbConnect` 创建数据库角色。
**包含：** 作用域角色设置、IAM 到数据库角色映射、敏感数据的模式分离、角色设计模式

### 身份验证与操作：

#### [auth/authentication-guide.md](references/auth/authentication-guide.md)

**何时：** 在处理 IAM 身份验证令牌、密钥、SSL/TLS、连接池或审计日志时必须加载。
**包含：** 令牌生命周期、密钥存储模式、SSL/TLS 设置、连接池指导、审计日志集成。

#### [auth/connectivity-tools.md](references/auth/connectivity-tools.md)

**何时：** 在选择驱动程序/ORM/适配器或规划批量数据加载时加载。
**包含：** 指向权威 AWS DSQL 连接性工具页面（驱动程序、ORM、适配器）和批量加载文档页面。

#### [auth/scaling-guide.md](references/auth/scaling-guide.md)

**何时：** 在设计扩展性时加载——连接池、批量优化、热键避免、标识符选择。
**包含：** 水平扩展策略、池大小、批量大小指导、IDENTITY/UUID 权衡、序列缓存规则。

### 实现示例：

#### [workflow-patterns.md](references/workflow-patterns.md)

**何时：** 在查找常见多步骤 DSQL 工作流的示例（模式探索、CREATE+INDEX、安全迁移、批量插入、应用层外键检查）时加载。
**包含：** 五个规范模式，使用 `psql` / 驱动程序代码。

#### [dsql-examples.md](references/dsql-examples.md)

**何时：** 在查找特定实现示例时加载。
**包含：** `examples/*.md` 索引（连接、模式、数据操作、迁移、模式）。

### DDL 迁移（模块化）：

#### [ddl-migrations/overview.md](references/ddl-migrations/overview.md)

**何时：** 在执行 DROP COLUMN、RENAME COLUMN、ALTER COLUMN TYPE 或 DROP CONSTRAINT 时必须加载
**包含：** 表重新创建模式概述、事务规则、常见验证和交换模式

#### [ddl-migrations/column-operations.md](references/ddl-migrations/column-operations.md)

**何时：** 用于 DROP COLUMN、ALTER COLUMN TYPE、SET/DROP NOT NULL、SET/DROP DEFAULT 迁移时加载
**包含：** 列级别更改的逐步迁移模式

#### [ddl-migrations/constraint-operations.md](references/ddl-migrations/constraint-operations.md)

**何时：** 用于 ADD/DROP CONSTRAINT、MODIFY PRIMARY KEY、列拆分/合并迁移时加载
**包含：** 约束和结构更改的逐步迁移模式

#### [ddl-migrations/batched-migration.md](references/ddl-migrations/batched-migration.md)

**何时：** 在迁移超过 3,000 行的表时加载
**包含：** 基于OFFSET和游标的基础批量模式、进度跟踪、错误处理

### MySQL 迁移（模块化）：

#### [mysql-migrations/type-mapping.md](references/mysql-migrations/type-mapping.md)

**何时：** 必须在将 MySQL 模式迁移到 DSQL 时加载
**包含：** MySQL 数据类型映射、功能替代方案、DDL 操作映射

#### [mysql-migrations/ddl-operations.md](references/mysql-migrations/ddl-operations.md)

**何时：** 在将 MySQL DDL 操作转换为 DSQL 等价物时加载
**包含：** ALTER COLUMN、DROP COLUMN、AUTO_INCREMENT、ENUM、SET、外键迁移模式

#### [mysql-migrations/full-example.md](references/mysql-migrations/full-example.md)

**何时：** 在将整个 MySQL 表迁移到 DSQL 时加载
**包含：** 带决策摘要的端到端 MySQL CREATE TABLE 迁移示例

### 查询计划可解释性（模块化）：

**何时：** 必须在 Workflow 8 阶段 0 加载所有四个——[query-plan/plan-interpretation.md](references/query-plan/plan-interpretation.md)、[query-plan/catalog-queries.md](references/query-plan/catalog-queries.md)、[query-plan/guc-experiments.md](references/query-plan/guc-experiments.md)、[query-plan/report-format.md](references/query-plan/report-format.md)
**包含：** DSQL 节点类型 + 节点持续时间数学 + 估计误差带、pg_class/pg_stats/pg_indexes SQL + 相关谓词验证、GUC 实验程序 + 30 秒跳过协议、所需报告结构 + 元素清单 + 支持请求模板

---

## 查询执行

使用 `psql` 和新鲜生成的 IAM 身份验证令牌执行即席 DSQL 查询。捆绑的
[`scripts/psql-connect.sh`](scripts/psql-connect.sh) 包含令牌生成、TLS 配置和单语句保护——优先使用它而不是手工编写的 `psql` 调用。

**只读：**

```bash
./scripts/psql-connect.sh --cluster <cluster-id> --command "SELECT * FROM entities LIMIT 10"
```

**写入/DDL（需要 IAM 管理员身份验证令牌）：**

```bash
./scripts/psql-connect.sh --cluster <cluster-id> --admin --command "CREATE INDEX ASYNC ..."
```

**模式发现：** 没有特殊的 `list_tables` 辅助程序——使用 information_schema：

```sql
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';
```

有关详细用法和示例，请参阅 [database-tools.md](references/database-tools.md)。

### 通过 AWS MCP 服务器获取 AWS 知识（可选）

当连接到 [AWS MCP 服务器](https://docs.aws.amazon.com/aws-mcp/latest/userguide/mcp-server.html) 时，
其 `aws___search_documentation` 和 `aws___read_documentation` 工具可以在向用户提供建议之前验证 DSQL 服务限制。下表中的数值限制是默认值，可能会更改——当用户的决策取决于确切的限制时，请先验证它：

| 限制                                   | 默认       | 验证查询                       |
| --------------------------------------- | ------------- | ---------------------------------- |
| 每笔事务修改的最大行数                | 3,000         | `aurora dsql transaction limits`   |
| 每个写入事务修改的最大数据量          | 10 MiB        | `aurora dsql transaction limits`   |
| 最大事务持续时间                        | 5 分钟     | `aurora dsql transaction limits`   |
| 每个集群的最大连接数                   | 10,000        | `aurora dsql connection limits`    |
| IAM 身份验证令牌过期                   | 15 分钟    | `aurora dsql authentication token` |
| 最大连接持续时间                        | 60 分钟    | `aurora dsql connection limits`    |
| 每个表的最大索引数                   | 24            | `aurora dsql index limits`         |
| 每个索引的最大列数                   | 8             | `aurora dsql index limits`         |
| IDENTITY/SEQUENCE CACHE 值          | 1 或 >= 65536 | `aurora dsql sequence cache`       |

**何时验证：** 在推荐批量大小、连接池设置或模式设计之前，因为达到限制会导致失败。对于一般指导或确切的数字不影响用户决策的情况，无需验证。

**后备：** 如果 AWS MCP 服务器不可用，请使用上表中的默认值，并告知用户应针对 [DSQL 文档](https://docs.aws.amazon.com/aurora-dsql/latest/userguide/) 验证限制。

## 可用的 CLI 脚本

位于 [scripts/](scripts/) 中的 Bash 脚本用于集群管理（创建、删除、列出、集群信息）和 `psql` 连接。有关用法，请参阅 [references/scripts-guide.md](references/scripts-guide.md)。对于批量数据加载，请参阅 [Loading data into Aurora DSQL](https://docs.aws.amazon.com/aurora-dsql/latest/userguide/loading-data.html)。

**始终** 优先使用 `scripts/create-cluster.sh`。该脚本发出一个**单个原子**的 `CreateCluster` 调用，并嵌入标签——与 AWS DSQL API 形状匹配，输出可解释。

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
使用 psql-connect.sh（或应用代码中的语言连接器）进行 SELECT 查询
始终在 WHERE 子句中包含 tenant_id 用于多租户应用
必须使用 safe_query.build() 构建SQL——参见 references/input-validation.md
```

### 3. 执行模式更改

```
使用 ./scripts/psql-connect.sh --admin（或带有 IAM 管理员身份验证令牌的语言连接器）进行 DDL
遵循每笔事务一个 DDL 的规则
始终在单独的语句中使用 CREATE INDEX ASYNC
ALTER COLUMN TYPE、DROP COLUMN、DROP CONSTRAINT → 表重新创建模式（Workflow 6）
```

---

## 常见任务

### Workflow 0: 验证依赖项

检查所需工具并如果缺少任何工具则向用户发出警告。

**约束：**

- 您必须在继续之前验证以下工具可用性：`psql`（>=14 用于 SNI 支持）和 AWS CLI v2，带有 `aws dsql generate-db-connect-auth-token`（以及 `generate-db-connect-admin-auth-token` 用于 DDL/角色设置）
- 您还应在用户的决策取决于精确服务限制时确认 AWS MCP 服务器可用性；如果不存在，则使用上表中的默认值，并注意应针对 DSQL 文档验证限制
- 您必须告知用户任何缺失工具的明确消息
- 您必须询问用户是否希望在缺少工具的情况下继续
- 您必须使用作用域（非管理员）IAM 身份验证令牌进行只读诊断，只要用户配置了作用域角色；保留 IAM 管理员身份验证令牌用于集群设置、角色授权和 DDL
- 对于集群生命周期（创建 / 检查 / 删除），请参阅 [Workflow 0a](#workflow-0a-cluster-lifecycle)
- 在编写应用程序代码之前，还必须验证每种语言的特定 DSQL 连接器，如 [Workflow 0b](#workflow-0b-verify-language-connector)

### Workflow 0a: 集群生命周期

**应** 使用捆绑脚本进行集群创建和删除——它们发出原子 `aws dsql` CLI 调用并处理输出。

**创建带标签和删除保护的集群：**

```bash
./scripts/create-cluster.sh --created-by <model-id> --tags Environment=eval,Project=dsql-skill-eval
```

**检查集群（状态、标签、端点、删除保护）：**

```bash
./scripts/cluster-info.sh <cluster-id>
```

**删除集群：**

```bash
./scripts/delete-cluster.sh <cluster-id> [--force]   # --force 在非 TTY 环境中跳过确认提示
```

在仅 MCP 环境中（无 Shell 访问），等效调用通过 AWS MCP 服务器的 `aws___call_aws` 工具进行。该工具接受 JSON 负载——使用与 AWS API 操作匹配的参数调用它：

```json
{"service": "dsql", "operation": "CreateCluster",
 "parameters": {"tags": {"created_by": "<model-id>", "Environment": "eval", "Project": "dsql-skill-eval"}, "deletionProtectionEnabled": true}}
```

```json
{"service": "dsql", "operation": "GetCluster", "parameters": {"identifier": "<cluster-id>"}}
```

```json
{"service": "dsql", "operation": "DeleteCluster", "parameters": {"identifier": "<cluster-id>"}}
```

`CreateCluster` 和 `DeleteCluster` 在 DSQL 端是异步的——API 立即返回集群的当前 `status` (`CREATING` / `DELETING`)。通过重新调用 `aws___call_aws` 并使用 `dsql:GetCluster` 直到 `.status == "ACTIVE"`（创建）或调用返回 404（删除）来轮询就绪状态。`aws___get_tasks` 用于轮询 MCP 端的长时间运行工具调用——不是 DSQL API。

有关完整参数细节和调用上下文，请参阅 [AWS CLI `aws dsql` 参考](https://docs.aws.amazon.com/cli/latest/reference/dsql/)。

### 工作流 0b：验证语言连接器

在编写应用程序代码之前，**必须**按照 [language.md](references/language.md) 验证特定语言的 DSQL 连接器是否已安装。连接器是 IAM 令牌刷新的规范路径；裸驱动程序（`pg`、`psycopg`、`pgx`、`tokio-postgres`）在第一个 15 分钟令牌过期之前可以工作，然后在新连接上开始返回认证错误——尝试裸形式的 DSQL 用户将此报告为 DSQL 错误。**必须**安装：

- Python：`aurora-dsql-python-connector` + 所选的驱动程序轮
- Node.js：`@aws/aurora-dsql-node-postgres-connector` 或 `@aws/aurora-dsql-postgresjs-connector`
- Go：`github.com/awslabs/aurora-dsql-connectors/go/pgx`
- Java：`software.amazon.dsql:aurora-dsql-jdbc-connector`
- Rust：`aurora-dsql-sqlx-connector`

如果所选运行时没有可用的连接器，请记录手动令牌刷新策略，并在编写代码之前与用户安排时间。

---

### 工作流 1：创建多租户模式

**必须**加载 [workflow-patterns.md](references/workflow-patterns.md)（模式 2：创建带索引的表）以获取 DDL 顺序、异步索引创建和模式验证示例。关键规则：所有表中都有 `tenant_id`，仅使用 `CREATE INDEX ASYNC`，每个事务一个 DDL，数组/JSON 存储为 TEXT。

### 工作流 2：安全数据迁移

**必须**加载 [workflow-patterns.md](references/workflow-patterns.md)（模式 3：安全数据迁移）以获取添加列→批量填充→验证→索引的顺序。对于超过 3,000 行的表，还加载 [ddl-migrations/batched-migration.md](references/ddl-migrations/batched-migration.md)。关键规则：首先添加列，通过单独的 UPDATE 应用 DEFAULT，每个事务批量少于 3,000 行。

### 工作流 3：应用程序层参照完整性

**必须**加载 [workflow-patterns.md](references/workflow-patterns.md)（模式 5：应用程序层外键检查）以获取父存在 SELECT→INSERT 和依赖计数 SELECT→DELETE 模式。使用 `safe_query.build()` 构建所有 SQL——请参阅工作流 4a。

### 工作流 4：带租户隔离的查询

1. **必须**授权调用者针对租户——格式验证不能建立授权
2. **必须**使用 [`safe_query.build()`](scripts/safe_query.py) 构建 SQL——使用 `allow()`/`regex()` 为值（发出 `'v'`），`ident()` 为表/列名（发出 `"v"`）。
   请参阅 [input-validation.md](references/input-validation.md)
3. **必须**在 WHERE 子句中包含 `tenant_id`；在应用程序层拒绝跨租户访问

### 工作流 4a：评分关键——使用用户输入构建 SQL

在为 `psql -c "..."`（或任何等效的临时查询路径）构建 SQL 时，如果任何值不是开发者控制的字面量（租户 ID、实体 ID、排序列、方向、状态枚举、自由文本描述、请求参数——来自不受信任来源的任何内容），**必须**使用 [`safe_query.build()`](scripts/safe_query.py)。`psql -c` 标志接受原始 SQL 字符串；它不接受绑定参数。在应用程序代码中使用 Postgres 驱动程序（psycopg、pgx 等）时，优先使用驱动程序的本地参数绑定；`safe_query` 是必须构建原始 SQL 字符串时的规范回退。通过 `safe_query` 进行的验证是原始 SQL 路径的主要防御。

**验证器选择表**（规范——镜像 [input-validation.md](references/input-validation.md)）：

| 值类型                                   | 验证器                      | 发出                      |
| -------------------------------------------- | ------------------------------ | -------------------------- |
| 已知集合（租户 ID、状态枚举）           | `allow(v, SET)`                | `'value'`                  |
| 已知集合用作 SQL 关键字（ASC/DESC）     | `keyword(v, SET)`              | `value` (未引号)         |
| 严格格式（UUID、slug、ISO 日期）         | `regex(v, PATTERN)`            | `'value'`                  |
| 表或列名                         | `ident(name)`                  | `"value"`                  |
| 整数                                      | `integer(v)`                   | `value`                    |
| 自由文本（描述、注释、用户名）  | `literal(v)`                   | `$dq_xxx$value$dq_xxx$`    |

`safe_query.py` 中的内置模式：`TENANT_SLUG` (`[a-z0-9-]{1,64}`)、`UUID`、`INT`、`ISO_DATE`。

**每个构建 DSQL SQL 的文件顶部的必需导入**：

```python
from safe_query import build, allow, regex, ident, keyword, integer, literal, UnsafeSQLError
from safe_query import TENANT_SLUG, UUID, ISO_DATE
```

**评分关键场景 1——来自不受信任输入的 tenant_id。** 使用 `regex(req.tenant, TENANT_SLUG)` 或 `allow(req.tenant, ALLOWED_TENANTS)` 进行验证。使用 `safe_query.build()` 构建，然后执行。即使在只读模式下（纵深防御，跨模式一致验证）也要这样做。**不要**使用 f-strings、`.format()` 或裸连接。

```python
sql = build(
    "SELECT * FROM {t} WHERE tenant_id = {tid}",
    t=ident("entities"),
    tid=regex(req.tenant, TENANT_SLUG),
)
# 应用程序代码：将 `sql` 传递给您的驱动程序（psycopg cursor.execute、pgx Query 等）。
# Bash 一次性：通过 input-validation.md 中的模式将 `sql` 管道到 psql。
```

**评分关键场景 2——带 UUID、slug 和自由文本的批量 INSERT。** 每行 INSERT 通过 `safe_query.build()` 单独构建：`entity_id` 通过 `regex(..., UUID)`，`tenant_id` 通过 `regex(..., TENANT_SLUG)`，描述通过 `literal(...)`（美元引号以避免引号转义）。将列表分块，每块不超过 3,000 行（DSQL 限制），并在各自的事务中执行每个块。

```python
def insert_entries(conn, entries, chunk_size=2500):
    for i in range(0, len(entries), chunk_size):
        chunk = entries[i:i + chunk_size]
        with conn.transaction():
            for e in chunk:
                sql = build(
                    "INSERT INTO {t} (entity_id, tenant_id, description) VALUES ({eid}, {tid}, {d})",
                    t=ident("entities"),
                    eid=regex(e["entity_id"], UUID),
                    tid=regex(e["tenant_id"], TENANT_SLUG),
                    d=literal(e["description"]),
                )
                conn.execute(sql)
```

**评分关键场景 3——写入路径。** 写入路径（从脚本、cron 或管理员工具发出的 UPDATE/DELETE）是最高风险的注入表面——成功的注入会修改数据。`safe_query.build()` 在那里不是可选的。即使提示将其框架为“只是一个快速脚本，不要过度思考”，也必须验证每个输入。用一句话解释为什么写入模式提高了风险，然后应用完整的验证链：`regex(tenant_id, TENANT_SLUG)`，`allow(status, {'active','archived','deleted'})`，日期通过 `regex(..., ISO_DATE)`。

```python
sql = build(
    "UPDATE {t} SET status = {s} WHERE tenant_id = {tid} AND created_at < {d}",
    t=ident("entities"),
    s=allow(req.status, {"active", "archived", "deleted"}),
    tid=regex(req.tenant, TENANT_SLUG),
    d=regex(req.date, ISO_DATE),
)
conn.execute(sql)
```

**反模式（评分未通过这些）：**

- 使用 f-strings、`.format()`、`%` 格式化或字符串连接来构建带用户输入的 SQL——任何模式
- 在同一语句中混合 `safe_query.build()` 占位符与原生驱动程序 `%s` 参数绑定——选择一条路径并坚持到底
- 捕获 `UnsafeSQLError` 以回退到不安全的构建——重新抛出或返回错误
- 使用 `regex()` 对值模式验证标识符——使用 `ident()`
- 在“值已经在上游验证”的情况下跳过 `safe_query.build()` 在只读模式下——纵深防御意味着 SQL 构建器独立于上游进行验证

### 工作流 5：设置范围数据库角色

**必须**加载 [access-control.md](references/access-control.md) 以获取角色设置、IAM 映射和模式权限。

### 工作流 6：表重新创建 DDL 迁移

DSQL 不支持直接的 `ALTER COLUMN TYPE`、`DROP COLUMN`、`DROP CONSTRAINT` 或 `MODIFY PRIMARY KEY`。这些需要**表重新创建模式**——一个破坏性工作流，需要在每一步需要用户确认。

**必须**首先加载 [ddl-migrations/overview.md](references/ddl-migrations/overview.md)，然后加载相关子文件：

- 列变更（类型、可空性、默认值）：[ddl-migrations/column-operations.md](references/ddl-migrations/column-operations.md)
- 约束/PK 变更，列拆分/合并：[ddl-migrations/constraint-operations.md](references/ddl-migrations/constraint-operations.md)
- 超过 3,000 行的表：还加载 [ddl-migrations/batched-migration.md](references/ddl-migrations/batched-migration.md)

### 工作流 7：MySQL 到 DSQL 模式迁移

**必须**加载 [mysql-migrations/type-mapping.md](references/mysql-migrations/type-mapping.md) 以获取类型映射和功能替代方案。有关 DDL 翻译详细信息，加载 [mysql-migrations/ddl-operations.md](references/mysql-migrations/ddl-operations.md)。有关端到端示例，加载 [mysql-migrations/full-example.md](references/mysql-migrations/full-example.md)。

### 工作流 8：查询计划可解释性

由慢查询、高 DPU、意外的全扫描或用户不理解的计划触发。需要结构化的 Markdown 诊断报告作为必需的可交付成果——在工作流端到端运行之前回答。

**必须**在开始之前加载所有四个参考文件：

1. [query-plan/plan-interpretation.md](references/query-plan/plan-interpretation.md) — 节点类型、持续时间数学、异常值
2. [query-plan/catalog-queries.md](references/query-plan/catalog-queries.md) — pg_class / pg_stats / pg_indexes SQL
3. [query-plan/guc-experiments.md](references/query-plan/guc-experiments.md) — GUC 过程和 `>30s` 跳过协议
4. [query-plan/report-format.md](references/query-plan/report-format.md) — 必需的报告结构和元素清单

**阶段 1——捕获计划。** ALWAYS 通过 `psql` 对用户查询的原始文本运行 `EXPLAIN ANALYZE VERBOSE`——即使用户描述或粘贴了计划。SELECT 正常运行。UPDATE/DELETE：重写为等效的 SELECT 再运行。INSERT、pl/pgsql、DO 块和函数必须拒绝。在捕获计划期间**不得**运行可变 DML。当 EXPLAIN 出错时，逐字报告——不要编造 DSQL 特定语义。提取查询 ID、规划时间、执行时间和 DPU 估计。

**阶段 2——收集证据。** 查询 `pg_class`、`pg_stats`、`pg_indexes`、`COUNT(*)`、`COUNT(DISTINCT)` 根据 `catalog-queries.md`。根据 `plan-interpretation.md` 对估计错误进行分类。

**阶段 3——实验（有条件）。** ≤30s：根据 `guc-experiments.md` 运行 GUC 实验，加上冗余谓词测试。>30s：跳过，在报告中逐字包含手动 GUC SQL。异常行计数：确认结果正确，标记为潜在的 DSQL 错误，生成支持请求模板。

**阶段 4——报告并邀请重新评估。** 根据 `report-format.md` 中的必需元素清单生成完整诊断报告。以“下一步”块结束。当用户说“重新评估”时，重新运行阶段 1–2，并在原始报告中附加“变更后性能”的补充。

**psql 调用：**

```bash
./scripts/psql-connect.sh --cluster <id> --command "EXPLAIN ANALYZE VERBOSE <sql>"
./scripts/psql-connect.sh --cluster <id> --script ./experiment-2.sql   # GUC 多语句
```

---

## 安全注意事项

本节汇总了关键安全控制。有关详细指南，请参阅链接的参考文件。

1. **IAM 认证令牌过期：** IAM 认证令牌在 15 分钟后过期。始终为每个连接生成新的令牌或实施定期刷新。**永远不要将令牌持久化到磁盘**——仅在内存中保留它们并在使用后丢弃。请参阅 [authentication-guide.md](references/auth/authentication-guide.md)。

2. **范围角色优于管理员：** 使用带 `dsql:DbConnect` 的范围数据库角色进行所有应用程序连接。将 `admin` 角色严格保留为初始集群设置（创建角色、授予权限）。在范围角色建立后，从设置 IAM 角色中撤销 `dsql:DbConnectAdmin`。请参阅 [access-control.md](references/access-control.md)。

3. **传输加密**：服务器端强制执行SSL/TLS。使用`sslmode=verify-full`（DSQL连接器默认值和`psql-connect.sh`中的值）来验证服务器证书是否通过DSQL的CA，以防止中间人攻击。仅在客户端无法访问受信任的CA包时才降级到`require`。

4. **静态加密**：Aurora DSQL默认使用AWS管理的密钥对静态数据进行加密。无需额外配置；当合规性框架要求证明时，在集群属性中验证加密状态。

5. **通过CloudTrail进行审计日志记录**：为DSQL API调用启用CloudTrail日志记录，以监控令牌生成模式、集群配置更改和失败的认证尝试。配置CloudWatch警报以检测可疑活动。使用KMS密钥启用用于DSQL监控的CloudWatch日志组的加密，以保护潜在的敏感查询元数据。参见[authentication-guide.md](references/auth/authentication-guide.md)。

6. **写入路径必须严格验证**：从脚本、cron作业或管理工具发出的修改SQL（UPDATE、DELETE、DDL）是风险最高的注入面。每个写入路径**必须**通过`safe_query.build()`（在应用程序代码中使用Postgres驱动器时为驱动器的原生参数绑定）。

7. **输入验证是主要防御**：`safe_query.build()`是原始SQL路径上防止SQL注入的主要防御。来自不可信输入的每个值——租户ID、实体ID、排序列、自由文本——**必须**通过验证器（`allow`、`regex`、`ident`、`keyword`、`integer`、`literal`）。不要使用f-strings、`.format()`或连接。参见[input-validation.md](references/input-validation.md)。

8. **多租户隔离作为硬性约定**：当工作负载使用租户范围（工作流4）时，`tenant_id`**必须**出现在每个读取和写入租户拥有表的WHERE子句中，并且应用程序**必须**在发出查询之前针对该`tenant_id`授权调用者——仅格式验证不能建立授权。从WHERE子句中省略`tenant_id`，或范围到调用者未授权的租户值，会导致跨租户数据暴露。此边界由技能强制执行，而不是DSQL——在部署前验证每个数据访问路径是否范围到认证的租户。参见[access-control.md](references/access-control.md)和Workflow 4。

---

## 故障排除

- **AWS MCP服务器返回无结果**：使用上表中默认的限制，并注意限制应与[DSQL文档](https://docs.aws.amazon.com/aurora-dsql/latest/userguide/)进行验证。
- **OCC序列化错误**：重试事务。如果仍然存在，请检查是否存在热键争用——参见[troubleshooting.md](references/troubleshooting.md)。
- **事务超出限制**：拆分为小于3,000行的批次——参见[batched-migration.md](references/ddl-migrations/batched-migration.md)。
- **IAM认证令牌在操作中途过期**：生成新的IAM认证令牌——参见[authentication-guide.md](references/auth/authentication-guide.md)。参见[troubleshooting.md](references/troubleshooting.md)以解决其他问题。

---

## 其他资源

- [Aurora DSQL文档](https://docs.aws.amazon.com/aurora-dsql/latest/userguide/)
- [DSQL连接器、驱动器和ORM示例（官方）](https://docs.aws.amazon.com/aurora-dsql/latest/userguide/aws-sdks.html)
- [PostgreSQL兼容性](https://docs.aws.amazon.com/aurora-dsql/latest/userguide/working-with-postgresql-compatibility.html)
- [CloudFormation资源](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dsql-cluster.html)

## 从aws-database-selection交接

此技能可以直接调用，或从运行了需求访谈并生成了`requirements.json`工件后的`aws-database-selection`父技能进入。当你在最近的对话中看到匹配`aws_dbs_requirements/*/requirements.json`的引号包裹路径时，请遵循`aws-database-selection/references/handoff-contract.md`中的入口协议：

1. 使用`file_read`读取工件。
2. 使用`aws-database-selection/references/workload-primary-artifact.schema.json`验证它。如果格式错误或无法读取，告诉用户并继续不使用它。
3. 确认一个或两个**粗体**句子中相关的内容，引用工件中的高级事实（主导形状、硬约束、迁移上下文）——不要逐字重复整个工件。
4. 范围检查：此技能范围到Aurora DSQL模式、查询计划、IAM认证、多租户模式、MySQL到DSQL迁移。如果工件的`workload_primaries.dominant_shapes`或`migration_context`与该范围不匹配，根据交接合同发出弱反向压力：建议`amazon-aurora`用于Aurora PostgreSQL / MySQL，`rds-oss`用于RDS引擎，如果不需要跨区域强SQL一致性，则返回`aws-database-selection`，然后询问用户是否要返回或继续。不要无声地滥用工件。
5. 使用此技能的原生工作流继续，在建议基于需求时引用工件路径作为证据。

此技能的所有用户界面输出都遵循交接合同中仅使用markdown-primitives的格式约定：粗体标签、路径和枚举值用引号包裹、替代方案用项目符号列表表示、不使用ASCII艺术或框画字符。
