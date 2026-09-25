**首先**：使用父级 `neon` 技能获取 Neon 概览、Neon 入门指南、Neon 开发最佳实践等内容。

如果未安装 `neon` 技能，请从 https://neon.com/docs/ai/skills/neon/SKILL.md 获取或使用以下命令安装：

```bash
neon skills -s neon -y
```

# Lakebase Postgres

Lakebase Postgres 是 Neon 的核心数据库。它基于 lakebase 架构（直接在云对象存储上构建的 OLTP），将存储与计算解耦，提供自动扩展、分支、即时恢复和零扩展功能。它与 Postgres 完全兼容，并支持任何支持 Postgres 的语言、框架或 ORM。

无论您是通过 Neon 还是 Databricks 访问该数据库，它都是相同的数据库；本技能涵盖 Neon 的访问路径。

登录、用户、会话和 `@neondatabase/auth` 属于 `neon-auth`。

## 设置流程

### 1. 选择组织和项目

如果已经提供 `DATABASE_URL`（提示、环境或代码库），或者 `.neon` 文件指向了项目，请使用它们。不要列出组织或为模式工作创建第二个项目。

否则，使用 CLI（默认）或 MCP 服务器列出组织和项目。让用户选择现有项目或创建新项目。

### 2. 获取连接字符串

如果已经提供 `DATABASE_URL`，请使用它。不要通过 CLI 或 MCP 获取另一个连接字符串。

否则，使用 CLI（默认）、`neon env pull` 或 MCP 服务器获取连接字符串。将其存储在 `.env` 文件中作为 `DATABASE_URL`。在修改文件之前先读取文件，以避免覆盖现有值。

#### 使用池化连接与直接连接的场景

| 使用场景                                 | 连接类型  |
| ---------------------------------------- | ---------------- |
| Web 应用程序、无服务器函数   | 池化 (-pooler) |
| 模式迁移                        | 直接           |
| pg_dump / pg_restore                     | 直接           |
| 逻辑复制                      | 直接           |
| 长时间运行的带临时表的分析  | 直接           |
| 需要使用 SET 或会话状态的行政任务 | 直接           |
| LISTEN / NOTIFY                          | 直接           |

### 3. 选择连接方法和驱动程序

保留现有的 ORM 和驱动程序。对于没有既定选择的新的 TypeScript 模式工作，建议使用 Drizzle：https://neon.com/docs/guides/drizzle.md。参考连接方法指南根据运行时如何处理代码选择正确的驱动程序：https://neon.com/docs/connect/choose-connection.md。

驱动程序说明：

- 在 Vercel 上，使用 `node-postgres` (`npm install pg`) 并配合 Vercel Fluid 计算，并使用 `import { attachDatabasePool } from "@vercel/functions";`。
- 在 Cloudflare 上，使用 `node-postgres` 并配合 Cloudflare Hyperdrive。
- 在 Neon Functions 上，使用 `node-postgres`，因为函数是长时间运行的，并在请求之间重用连接池。
- 在无服务器和边缘环境中（例如使用 Netlify 时），使用 `@neondatabase/serverless` 驱动程序 — HTTP 传输用于一次性查询，WebSocket 用于事务支持。链接：https://neon.com/docs/serverless/serverless-driver.md

### 4. 设置模式

将模式和迁移作为代码进行管理。避免直接对数据库运行 ad hoc 模式迁移，因为它们难以管理。

如果您使用 ORM，请遵循 ORM 的最佳实践来管理模式和迁移。例如，如果使用 Drizzle，除非另有说明，否则仅使用 Drizzle 进行模式和迁移管理。

## 分支

当用户计划隔离环境、模式迁移测试、预览部署或分支生命周期自动化时使用此功能。

要点：

- 分支是即时、写时复制克隆（无需完整数据复制）。
- 每个分支都有自己的计算端点。
- 使用 neon CLI 或 MCP 服务器创建、检查和比较分支。

链接：https://neon.com/docs/introduction/branching.md

对于详细的分支创建工作流（正常分支与仅模式分支、从父分支重置、CLI/MCP 选择），使用 `neon-postgres-branches` 技能。如果未安装，请从 https://neon.com/docs/ai/skills/neon-postgres-branches/SKILL.md 获取或使用以下命令安装：

```bash
neon skills -s neon-postgres-branches -y
```

## 迁移

在将迁移应用到生产环境之前，先在生产环境的分支上使用生产类似的数据进行测试。

运行迁移时，使用**直接（非池化）**连接字符串，而不是池化连接字符串。`neon connection-string` 默认返回直接字符串；确保主机名不包含 `-pooler` 后缀。

## 故障排除和 Neon 特定性能

在手动编写目录查询之前，使用 Neon 的预定义只读诊断工具。Neon CLI 的 `neon inspect db` 子命令和 Neon MCP 服务器的 `inspect_database` 工具运行相同的检查。

本节涵盖 Neon 特定的诊断工具、计算缓存行为和平台信号。当证据指向通用 Postgres 工作时（例如重写查询、选择索引、更改模式或解释计划节点），加载 [`postgres-best-practices`](https://github.com/neondatabase/postgres-skills/tree/main/skills/postgres-best-practices) 技能，并将诊断证据带入该工作流。

文档：

- CLI: https://neon.com/docs/cli/inspect.md
- 查询性能: https://neon.com/docs/postgresql/query-performance.md
- `pg_stat_statements`: https://neon.com/docs/extensions/pg_stat_statements.md
- Neon Local File Cache: https://neon.com/docs/extensions/neon.md

### 选择 CLI 或 MCP

当终端访问和身份验证可用时，优先使用 Neon CLI：

```bash
neon inspect db <check>
```

CLI 会根据当前的 Neon 上下文解析项目和分支。使用 `--project-id`、`--branch` 和 `--database-name` 覆盖它。省略 `--database-name` 以检查分支上的所有数据库。仅在直接检查 Postgres 数据库而不是通过 Neon API 解析时使用 `--db-url`。

当使用 Neon MCP 时，调用 `inspect_database` 并传入 `projectId` 和一个 `check`。仅在需要时传递 `branchId`、`databaseName` 或 `computeId`。省略 `databaseName` 以检查分支上的所有数据库。仅在结果提示被截断时增加 `limit`。

### 选择诊断工具

| 症状或问题                            | 检查                               |
| ---------------------------------------------- | ------------------------------------ |
| 哪些关系消耗存储空间？               | `table-sizes`，`index-sizes`         |
| 索引是否未使用或表被大量扫描？ | `unused-indexes`，`seq-scans`        |
| 什么运行了 5 分钟以上或持有锁？    | `long-running-queries`，`locks`      |
| 哪些查询消耗了最多的总时间？     | `outliers`                           |
| 哪些查询运行最频繁？                  | `calls`                              |
| 活动数据是否适合计算缓存？     | `lfc-hit-rate`，`working-set`        |
| 自动清理是否落后或空间被浪费？       | `vacuum-stats`，`bloat`              |
| 逻辑复制是否健康？                | `replication-slots`，`subscriptions` |

不要混淆这些检查：

- `long-running-queries` 报告当前运行超过五分钟的语句。
- `outliers` 按累积执行时间对查询进行排名，自统计重置以来。它不按平均延迟排名。
- `calls` 按执行次数对相同统计历史进行排名。

`outliers` 和 `calls` 需要 `pg_stat_statements`。`lfc-hit-rate` 和 `working-set` 需要 `neon` 扩展。如果检查报告缺少扩展，请在运行建议的 `CREATE EXTENSION` 语句之前询问，因为安装扩展会修改数据库。

### 安全地解释结果

- 将 `unused-indexes` 视为候选列表，而不是删除索引的权限。在删除之前，确认观察窗口、约束和工作负载。
- 对于小型表或读取表的大部分数据的查询，顺序扫描可能是正确的。在添加索引之前，检查表大小、选择性和查询计划。
- `bloat` 是一个统计估计。在 `VACUUM FULL`、`REINDEX` 或类似修复之前，确认影响并计划锁或维护。
- 缓存和 Postgres 统计信息在计算重新启动时（包括零扩展暂停）会重置。在解释新鲜的 `lfc-hit-rate`、`working-set`、`vacuum-stats` 或 `pg_stat_statements` 结果之前，运行代表性工作负载。
- 计算范围检查（`lfc-hit-rate`、`working-set` 和 `replication-slots`）即使在检查每个数据库时也只运行一次。
- 一个失败的数据库可能导致所有数据库检查失败；使用显式的 `databaseName` 重试相关检查以隔离它。

### 按查询检查 Neon 缓存行为

标准的 `EXPLAIN (ANALYZE, BUFFERS)` 报告 Postgres 共享缓冲区活动，但它不显示 Neon 的本地文件缓存 (LFC) 或页面预取。对于安全的只读查询，添加 Neon 的 `FILECACHE` 和 `PREFETCH` 选项：

```sql
EXPLAIN (ANALYZE, BUFFERS, PREFETCH, FILECACHE)
SELECT ...;
```

- `File cache: hits` 计算在计算 LFC 中找到的页面。
- `File cache: misses` 计算未在 LFC 中找到并从数据库存储中获取的页面。
- `Prefetch: hits`、`misses`、`expired` 和 `duplicates` 显示 Neon 在执行器请求页面之前获取页面的有效性。

`FILECACHE` 和 `PREFETCH` 为此查询提供指标，并且不需要 `neon` 扩展。相比之下，`neon inspect db lfc-hit-rate` 和 `working-set` 提供计算范围统计信息，并且需要该扩展。

MCP 的 `explain_sql_statement` 工具可以生成标准计划，但不暴露 `FILECACHE` 或 `PREFETCH` 选项。要通过 MCP 收集这些 Neon 特定指标，请使用上面明确的只读 `EXPLAIN` 语句与 `run_sql`。

由于 `ANALYZE` 会执行语句，因此仅在执行安全时使用它；不要自行运行可变 SQL。仔细比较冷缓存和热缓存运行，因为第一次执行可以填充缓存并实质性地改变后续结果。

### 性能工作流

1. 复现症状并记录其时间窗口。
2. 运行上述表格中最相关的 `inspect` 检查。
3. 在更改模式或计算之前，识别特定查询。使用 MCP `explain_sql_statement` 获取标准计划，或在 LFC 或预取行为重要时的 Neon 特定 `EXPLAIN`。
4. 如果瓶颈是查询形状、索引、模式、锁定或清理行为，加载 `postgres-best-practices` 并将检查结果和查询计划传递下去。在此技能中保留 Neon 计算、缓存、连接和平台决策。
5. 重新运行相同的检查和工作负载以验证更改。

当用户需要按平均执行时间对查询进行排名并具有自定义阈值和限制时，使用 MCP `list_slow_queries` 而不是 `inspect_database`。在上述显式 `EXPLAIN` 案例之外，仅在预定义检查无法回答问题时，使用 `run_sql` 仅用于只读诊断 SQL。

## 自动扩展

当用户需要计算随工作负载自动扩展并希望获得 CU 大小和运行时行为的指导时使用此功能。

链接：https://neon.com/docs/introduction/autoscaling.md

## 零扩展

当优化空闲成本并讨论暂停/恢复行为（包括冷启动权衡）时使用此功能。

要点：

- 空闲计算在默认 5 分钟后自动暂停；超时是可配置的，并且仅在 Launch 和 Scale 计划上可以禁用暂停。
- 暂停后的第一个查询通常有冷启动惩罚（约几百毫秒）
- 计算暂停时，存储保持活动状态。

链接：https://neon.com/docs/introduction/scale-to-zero.md

## 即时恢复

当用户需要时间点恢复或希望在不使用传统备份恢复工作流的情况下恢复数据状态时使用此功能。

要点：

- 即时恢复的历史窗口取决于计划限制。
- 用户可以从历史时间点创建分支。
- 时间旅行查询可用于历史检查工作流。

链接：https://neon.com/docs/introduction/branch-restore.md

## 读副本

当用户需要为读密集型工作负载提供专用的只读计算端点而不复制存储时使用此功能。

要点：

- 读副本是共享相同存储的只读计算端点。
- 创建速度快，扩展独立于主计算。
- 典型用例：分析、报告和读密集型 API。

链接：https://neon.com/docs/introduction/read-replicas.md

## 连接池化

当用户处于无服务器或高并发环境并需要安全的可扩展 Postgres 连接管理时使用此功能。

要点：

- Neon 池化使用 PgBouncer。
- 向端点主机名添加 `-pooler` 以使用池化连接。
- 池化在高并发无服务器运行时尤其重要。

链接：https://neon.com/docs/connect/connection-pooling.md

## IP 允许列表

当用户需要通过可信网络、IP 或 CIDR 范围限制数据库访问时使用此功能。

链接：https://neon.com/docs/introduction/ip-allow.md

## 逻辑复制

当集成 CDC 管道、外部 Postgres 同步或基于复制的数
