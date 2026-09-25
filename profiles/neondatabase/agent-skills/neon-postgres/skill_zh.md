**FIRST**：使用 `neon` 技能获取 Neon 概览、Neon 入门、Neon 开发最佳实践等更多内容。

如果未安装 `neon` 技能，请从 https://neon.com/docs/ai/skills/neon/SKILL.md 获取，或使用以下命令安装：

```bash
neon skills -s neon -y
```

# Lakebase Postgres

Lakebase Postgres 是 Neon 的核心数据库。它运行在 lakebase 架构之上——直接在云端对象存储上构建的 OLTP——这种架构将存储与计算解耦，从而提供自动扩展、分支、即时恢复和缩容至零的能力。它与 Postgres 完全兼容，可与任何支持 Postgres 的语言、框架或 ORM 配合使用。

无论通过 Neon 还是通过 Databricks 访问，它都是同一个数据库；本技能覆盖 Neon 访问路径。

登录、用户、会话和 `@neondatabase/auth` 相关内容属于 `neon-auth`。

## 设置流程

### 1. 选择组织和项目

如果已有 `DATABASE_URL` 提供（提示、环境变量或仓库），或 `.neon` 文件指向某个项目，则使用它。不要列出组织或为模式（schema）工作创建第二个项目。

否则使用 CLI（默认）或 MCP 服务器列出组织和项目，让用户选择已有项目或创建新项目。

### 2. 获取连接字符串

如果已有 `DATABASE_URL`，直接使用它。不要通过 CLI 或 MCP 获取其他连接字符串。

否则使用 CLI（默认）、`neon env pull` 或 MCP 服务器获取连接字符串。将其存储在 `.env` 文件中，命名为 `DATABASE_URL`。修改文件前先读取，以避免覆盖已有值。

#### 何时使用池化连接与直连

| 使用场景 | 连接类型 |
| ------------------------ | ---------------- |
|  Web 应用、无服务器函数 | Pooled（-pooler） |
|  模式迁移 |  直连 |
|  pg_dump / pg_restore |  直连 |
|  逻辑复制 |  直连 |
|  使用临时表的长期分析 |  直连 |
|  需要 SET 或会话状态的管理任务 |  直连 |
|  LISTEN / NOTIFY |  直连 |

### 3. 选择连接方式与驱动

保留现有的 ORM 和驱动。对于没有既定选择的新 TypeScript 模式工作，建议使用 Drizzle：https://neon.com/docs/guides/drizzle.md。参考连接方式指南，根据运行时如何对待你的代码来选择正确的驱动：https://neon.com/docs/connect/choose-connection.md。

驱动说明：

- 在 Vercel 上，使用 `node-postgres`（`npm install pg`），配合 Vercel Fluid compute 和 `import { attachDatabasePool } from "@vercel/functions";`
- 在 Cloudflare 上，使用 `node-postgres` 配合 Cloudflare Hyperdrive
- 在 Neon Functions 上，使用 `node-postgres`，因为函数是长期运行的，会在请求间复用连接池。
- 在 serverless 和边缘环境（例如使用 Netlify）中，使用 `@neondatabase/serverless` 驱动——一次性查询使用 HTTP 传输，事务支持使用 WebSocket。链接：https://neon.com/docs/serverless/serverless-driver.md

### 4. 设置模式（Schema）

将模式和迁移以代码形式管理。避免直接对数据库执行即席（临时）模式迁移，因为它们难以管理。

如果你正在使用 ORM，请遵循该 ORM 的最佳实践来管理模式和迁移。例如，如果使用 Drizzle，除非另有指示，否则仅使用 Drizzle 进行模式与迁移管理。

## 分支

在用户规划独立环境、模式迁移测试、预览部署或分支生命周期自动化时使用本部分。

要点：

- 分支是即时的、采用 copy-on-write 的克隆（无完整数据拷贝）。
- 每个分支都有独立的计算端点。
- 使用 neon CLI 或 MCP 服务器创建、检查并比较分支。

链接：https://neon.com/docs/introduction/branching.md

详细的分支创建工作流程（普通分支与仅模式分支、reset-from-parent、CLI/MCP 选择），使用 `neon-postgres-branches` 技能。如果未安装，请从 https://neon.com/docs/ai/skills/neon-postgres-branches/SKILL.md 获取，或使用以下命令安装：

```bash
neon skills -s neon-postgres-branches -y
```

## 迁移

在将迁移应用到生产环境之前，先在生产的分支上、针对类生产数据上测试迁移。

运行迁移时使用**直连（非池化）**连接字符串，而非池化连接字符串。`neon connection-string` 默认返回直连字符串；请确保主机名不包含 `-pooler` 后缀。

## 故障排除与 Neon 特定性能

在手动编写目录查询之前，先使用 Neon 预定义的只读诊断工具。Neon CLI 的 `neon inspect db` 子命令与 Neon MCP 服务器的 `inspect_database` 工具执行相同的检查。

本部分涵盖 Neon 特定的诊断工具、计算缓存行为以及平台信号。当证据表明问题属于通用 Postgres 工作（如重写查询、选择索引、修改模式或解释计划节点）时，加载 [`postgres-best-practices`](https://github.com/neondatabase/postgres-skills/tree/main/skills/postgres-best-practices) 技能，并将诊断证据带入该工作流。

文档：

- CLI：https://neon.com/docs/cli/inspect.md
- 查询性能：https://neon.com/docs/postgresql/query-performance.md
- `pg_stat_statements`：https://neon.com/docs/extensions/pg_stat_statements.md
- Neon Local File Cache：https://neon.com/docs/extensions/neon.md

### 选择 CLI 或 MCP

在终端访问和认证可用时，优先使用 Neon CLI：

```bash
neon inspect db <check>
```

CLI 根据当前的 Neon 上下文解析项目和分支。使用 `--project-id`、`--branch` 和 `--database-name` 覆盖它。省略 `--database-name` 以检查分支上的每个数据库。仅在直接检查 Postgres 数据库而非通过 Neon API 解析时使用 `--db-url`。

使用 Neon MCP 时，调用 `inspect_database`，传入 `projectId` 和一项检查。仅在需要时传入 `branchId`、`databaseName` 或 `computeId`。省略 `databaseName` 以检查分支上的所有数据库。仅在结果表明被截断时，才增加 `limit`。

### 选择诊断项

| 症状或问题 | 检查项 |
| ---------------------------------------------- | ------------------------------------ |
|  哪些关系消耗存储？ | `table-sizes`、`index-sizes` |
|  索引是否未使用或表被大量扫描？ | `unused-indexes`、`seq-scans` |
|  有哪些查询运行了 5 分钟以上或持锁？ | `long-running-queries`、`locks` |
|  哪些查询消耗的总时间最多？ | `outliers` |
|  哪些查询执行最频繁？ | `calls` |
|  活动数据是否适合计算缓存？ | `lfc-hit-rate`、`working-set` |
|  自动 vacuum 是否落后或空间是否浪费？ | `vacuum-stats`、`bloat` |
|  逻辑复制是否健康？ | `replication-slots`、`subscriptions` |

不要混淆这些检查：

- `long-running-queries` 报告**正在运行**超过五分钟的语句。
- `outliers` 按自统计信息重置以来的累计执行时间为各查询排序，而非按平均延迟排序。
- `calls` 按同一统计历史记录中的执行次数排序。

`outliers` 和 `calls` 需要 `pg_stat_statements`。`lfc-hit-rate` 和 `working-set` 需要 `neon` 扩展。如果某项检查报告缺少扩展，在运行建议的 `CREATE EXTENSION` 语句前先征得同意，因为安装扩展会修改数据库。

### 安全解读结果

- 将 `unused-indexes` 视为候选列表，而非删除索引的权限。删除前确认观察窗口、约束和工作负载。
- 顺序扫描对于小表或读取大部分表的数据的查询可能是正确的。在添加索引前，检查表大小、选择性和查询计划。
- `bloat` 是统计估算值。在执行 `VACUUM FULL`、`REINDEX` 等修复操作前，确认其影响并规划锁或维护。
- 计算重启时会重置缓存和 Postgres 统计信息，包括缩容至零暂停。在解读全新的 `lfc-hit-rate`、`working-set`、`vacuum-stats` 或 `pg_stat_statements` 结果之前，先运行代表性工作负载。
- 计算范围检查（`lfc-hit-rate`、`working-set` 和 `replication-slots`）即使检查所有数据库时也只需运行一次。
- 一个失败的数据库可能导致全部数据库检查失败；使用明确的 `databaseName` 重试相关检查以隔离问题。

### 按查询检查 Neon 缓存行为

标准的 `EXPLAIN (ANALYZE, BUFFERS)` 报告 Postgres 共享缓冲区的活动，但不显示 Neon 的 Local File Cache（LFC）或页预取。对于安全的只读查询，添加 Neon 的 `FILECACHE` 和 `PREFETCH` 选项：

```sql
EXPLAIN (ANALYZE, BUFFERS, PREFETCH, FILECACHE)
SELECT ...;
```

- `File cache: hits` 统计在计算资源的 LFC 中找到的页面数量。
- `File cache: misses` 统计未在 LFC 中找到、从数据库存储中获取的页面数量。
- `Prefetch: hits`、`misses`、`expired` 和 `duplicates` 显示 Neon 在执行器请求之前如何有效地获取页面。

`FILECACHE` 和 `PREFETCH` 为本次查询提供指标，不需要 `neon` 扩展。相比之下，`neon inspect db lfc-hit-rate` 和 `working-set` 提供计算范围的统计信息，且需要该扩展。

MCP 的 `explain_sql_statement` 工具可以生成标准计划，但不暴露 `FILECACHE` 或 `PREFETCH` 选项。要通过 MCP 收集这些 Neon 特定指标，使用上述明确的只读 `EXPLAIN` 语句配合 `run_sql`。

由于 `ANALYZE` 会执行语句，仅在执行安全时使用它；不要为变更性 SQL 自主执行。仔细比较冷缓存与热缓存的运行，因为首次执行可能填充缓存并显著改变后续结果。

### 性能工作流程

1.  复现症状并记录其时间窗口。
2.  从上面的表格中运行最小相关的 `inspect` 检查。
3.  在修改模式或计算之前，先识别具体的查询。使用 MCP `explain_sql_statement` 获取标准计划，或在 LFC 或预取行为重要时使用上述 Neon 特定 `EXPLAIN`。
4.  如果瓶颈是查询形状、索引、模式、锁或 vacuum 行为，加载 `postgres-best-practices` 并携带检查结果与查询计划前进。保持 Neon 计算、缓存、连接和平台决策在本技能中。
5.  重跑相同的检查和工作负载以验证更改。

当用户特别需要按平均执行时间排序并带有自定义阈值和限制查询时，使用 MCP `list_slow_queries`，而非 `inspect_database`。在上述明确的 `EXPLAIN` 情况之外，仅在预定义检查无法回答问题时，使用 `run_sql` 执行只读诊断 SQL。

## 自动扩展

当用户需要计算根据工作负载自动扩展，并需要 CU 规模与运行时行为指导时，使用本部分。

链接：https://neon.com/docs/introduction/autoscaling.md

## 缩容至零

当需要优化空闲成本并讨论暂停/恢复行为，包括冷启动权衡时，使用本部分。

要点：

- 空闲计算资源在默认 5 分钟后自动暂停；超时参数可配置，且暂停只能在 Launch 和 Scale 套餐上禁用。
- 暂停后的首次查询通常存在冷启动惩罚（约数百毫秒）。
- 计算暂停时，存储保持活跃。

链接：https://neon.com/docs/introduction/scale-to-zero.md

## 即时恢复

当用户需要时间点恢复或希望在传统备份恢复工作流之外恢复数据状态时，使用本部分。

要点：

- 即时恢复的历史窗口取决于套餐限制。
- 用户可以从历史时间点创建分支。
- 时间旅行查询可用于历史检查工作流。

链接：https://neon.com/docs/introduction/branch-restore.md

## 只读副本

当用户需要针对重读负载提供专用的只读计算，且不复制存储时，使用本部分。

要点：

- 副本是共享同一存储的只读计算端点。
- 创建快速，扩展独立于主计算。
- 典型用途：分析、报表和重读负载繁重的 API。

链接：https://neon.com/docs/introduction/read-replicas.md

## 连接池化

当用户处于无服务器或高并发环境，需要安全、可扩展的 Postgres 连接管理时，使用本部分。

要点：

- Neon 池化使用 PgBouncer。
- 在端点主机名中添加 `-pooler` 以使用池化连接。
- 池化在无服务器运行时的高突发并发场景中尤为重要。

链接：https://neon.com/docs/connect/connection-pooling.md

## IP 白名单

当用户需要通过可信网络、IP 或 CIDR 范围限制数据库访问时，使用本部分。

链接：https://neon.com/docs/introduction/ip-allow.md

## 逻辑复制

当集成 CDC 管道、外部 Postgres 同步或基于复制的数据传输时，使用本部分。

要点：

- Neon 支持原生的逻辑复制工作流。
- 适用于复制到/自外部 Postgres 系统。

链接：https://neon.com/docs/guides/logical-replication-guide.md

## Lakebase Search

使用 Lakebase Search 进行语义、全文和混合搜索：

- 对于语义搜索，阅读 [Vector search](references/vector-search.md)。
- 对于带 BM25 排名的全文搜索，阅读 [Full-text search](references/full-text-search.md)。
- 对于结合语义与词汇结果的混合搜索，阅读 [Hybrid search](references/hybrid-search.md)。

链接：

- [Lakebase Search 入门](https://neon.com/docs/ai/lakebase-search-get-started)
- [`lakebase_vector` 参考](https://neon.com/docs/extensions/lakebase-vector)
- [`lakebase_text` 参考](https://neon.com/docs/extensions/lakebase-text)

## 注意事项

### 池化连接与直连：迁移、转储和复制使用直连 URL

Neon 为你提供同一数据库的两个连接字符串：**池化**一个（主机名带 `-pooler` 后缀）和**直连/非池化**一个（不带 `-pooler` 后缀）。`neon env pull` 将它们分别写入 `DATABASE_URL` 和 `DATABASE_URL_UNPOOLED`。池化连接通过 PgBouncer 的事务模式路由，该模式不支持会话级操作。请选择正确的连接：

- **池化（`DATABASE_URL`）** — 应用的常规查询流量，尤其是无服务器和按请求连接的工作负载。
- **直连（`DATABASE_URL_UNPOOLED`）** — 模式迁移（Prisma Migrate、Drizzle Kit、Alembic 等）、`pg_dump` / `pg_restore`、逻辑复制、`LISTEN`/`NOTIFY`，以及任何依赖 `SET` 或其他会话状态的操作。

在池化连接上执行迁移、转储或复制可能会失败，且失败方式永远不会指向池化问题：Prisma Migrate 的 `prepared statement "s0" already exists`、一个因 `SET search_path` 未在自身事务后延续而导致后续查询报告 `relation "mytable" does not exist` 的情况，或写入间歇性地命中来自先前客户端继承的只读事务（`SQLSTATE 25006`）。迁移工具通常会同时接收两个字符串——Prisma 的 `directUrl` 与 `url`——因此请将其指向直连的那个，而不是交换 `DATABASE_URL` 而丢失应用的池化支持。详见 https://neon.com/docs/connect/connection-pooling.md。
