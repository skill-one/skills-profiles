---
name: prisma-next-debug
description: 读取 Prisma Next 结构化的错误信封，并根据代码、域、严重程度、原因、修复方案和元数据路由到正确的恢复路径。适用于错误、异常、我的发射失败、我的查询无法类型检查、我的查询崩溃、我的迁移无法应用、MIGRATION.HASH_MISMATCH、BUDGET.ROWS_EXCEEDED、BUDGET.TIME_EXCEEDED、RUNTIME.ABORTED、PLAN.HASH_MISMATCH、CONTRACT.MARKER_MISSING、PN-RUN-3001、PN-RUN-3002、PN-RUN-3030、PN-MIG-2001、PN-CLI-4011、PN-SCHEMA-0001、漂移、功能缺失、规划器冲突、Prisma Studio、EXPLAIN、查询日志、db.end、db.close、脚本无法退出、卡死、关闭连接、pool.end、客户端已关闭。
---

# Prisma Next — 调试

> **编辑你的数据合约。Prisma 处理其余部分。**

当 Prisma Next 调用失败时，框架会返回一个**结构化信封**。代理的任务是读取信封，根据 `code` 进行路由，并链接到正确的创作技能以进行实际修复。这个技能教授信封的形状和路由——它不会重复兄弟技能的工作流程。

## 何时使用

- 用户粘贴了错误信封（CLI 失败、运行时异常、`--json` 输出）。
- 用户说 *"我的查询不会类型检查"*、"我的迁移不会应用"*、"我的 emit 失败"*、"运行时崩溃"*。
- 用户提到稳定的代码（`PN-CLI-*`、`PN-MIG-*`、`PN-RUN-*`、`PN-SCHEMA-*`、`MIGRATION.*`、`CONTRACT.*`、`LINT.*`、`BUDGET.*`、`PLAN.*`、`RUNTIME.*`）。
- 用户提到：*Studio、EXPLAIN、查询日志、预处理语句、drift、哈希不匹配、功能、规划器*。

## 何时不使用

- 用户想要创作查询 / 模型 / 迁移 → 对应的创作技能。
- 用户想要*预防*错误（lints、budgets、类型级别守卫）→ `prisma-next-runtime`。
- 用户想要改变框架，因为表面本身就是问题（没有信封可以路由，功能确实缺失）→ `prisma-next-feedback`。

## 关键概念

### 两种信封形状

Prisma Next 根据哪个接口抛出异常发出**两种不同的信封**。在路由之前，请先阅读你拥有的是哪一种。

**1. CLI 信封** — 由 `prisma-next ...` 命令产生（emit、db init/update/verify/sign/schema、migration plan/apply/show/status、init）。形状（参见 `CliErrorEnvelope` 在 `packages/1-framework/1-core/errors/src/control.ts`）：

```json
{
  "ok": false,
  "code": "PN-MIG-2001",
  "domain": "MIG",
  "severity": "error",
  "summary": "未填写的迁移占位符",
  "why": "...",
  "fix": "...",
  "where": { "path": "...", "line": 42 },
  "meta": { "slot": "..." },
  "docsUrl": "https://prisma-next.dev/..."
}
```

完整代码是 `PN-<domain>-<NNNN>`。使用的域：`CLI`、`MIG`、`RUN`、`CON`、`SCHEMA`。严重性是 `error | warn | info` — `migration status` 在其诊断是 `warn` 时退出 0，因此请根据**严重性 + 代码一起**进行路由，而不是仅根据退出代码。

**2. 运行时信封** — 在执行查询时由进程内运行时抛出（参见 `RuntimeErrorEnvelope` 在 `packages/1-framework/1-core/framework-components/src/execution/runtime-error.ts`）：

```ts
{ name: 'RuntimeError', code: 'BUDGET.TIME_EXCEEDED', category: 'BUDGET', severity: 'error', message: '...', details: { ... } }
```

`category` 是 `PLAN | CONTRACT | LINT | BUDGET | RUNTIME`（`code` 的前缀）。`details` 包含结构化上下文（`details` 是运行时信封的 CLI 信封 `meta` 的等效项）。

**3. SQL 驱动程序错误** — 表现为 `SqlQueryError` / `SqlConnectionError`（参见 `packages/2-sql/1-core/errors/`）。`SqlQueryError` 上的字段：`kind: 'sql_query'`，`sqlState`（Postgres SQLSTATE，例如 `'23505'`），`constraint`，`table`，`column`，`detail`，`cause`。这些不是 `PN-*` 代码——根据 `sqlState` 和约束元数据进行路由。SQL 驱动程序错误通常在到达用户之前由中间件包装，但原始 SQL 路径可以直接显示它们。

### 包装错误和 `meta.code`

某些命令将下游错误重新包装为 `PN-RUN-3000`（`errorRuntime`）信封，并将原始代码存储在 `meta.code` 上。最重要的案例：`migrate` 通过 `mapMigrationToolsError` 包装 `MigrationToolsError`（它具有如 `MIGRATION.HASH_MISMATCH`、`MIGRATION.STALE_CONTRACT_BOOKENDS`、`MIGRATION.AMBIGUOUS_TARGET` 等代码）。你看到的信封是 `code: 'PN-RUN-3000'` 且 `meta.code: 'MIGRATION.HASH_MISMATCH'`。**当 `code` 是 `PN-RUN-3000` 时，始终检查 `meta.code`**——那里是路由质量信息所在的地方。

### 如何请求完整信封

如果用户只粘贴了人类摘要，请请求 `--json` 输出（机器信封）或使用 `-v` 重新运行（CLI 打印完整结构化字段）。`--json` 和 `-v` 是每个 CLI 命令的全局标志。

## 路由 — 脚本拆除和关闭客户端

这些症状不是 `PN-*` 信封——根据消息文本进行路由，并链接到 `prisma-next-runtime` § *作为脚本运行（拆除）*。

| 症状 | 下一步操作 |
|---|---|
| `TypeError: db.end is not a function` | 运行时客户端不暴露 `db.end()`——那是 `node-postgres` 池 API (`pool.end()`)。正确的调用是 `await db.close()`。参见 `prisma-next-runtime` § *作为脚本运行（拆除）*。 |
| 查询打印后脚本挂起 / 处理不会退出 | 在 Postgres 上， фасад 所拥有的 `pg.Pool` 保持事件循环活跃。在脚本返回之前调用 `await db.close()`，或者在脚本模块顶部使用 `await using db = postgres<Contract>(...)`（不要在请求处理程序内部放置 `await using`——块作用域，会按请求关闭）。参见 `prisma-next-runtime` § *作为脚本运行（拆除）*。 |
| `Error('Postgres client is closed')` / `Error('SQLite client is closed')` / `Error('Mongo client is closed')` | 客户端通过 `db.close()` 关闭（终端状态）。移除早期的 `close()`，重新排序以便 `close()` 在所有查询后运行，或者如果打算重新连接，则构造一个新的 `db`。参见 `prisma-next-runtime` § *作为脚本运行（拆除）*。 |

## 路由 — 症状和代码 → 下一步操作

单一事实来源：读取信封，通过 `code`（对于包装错误，通过 `meta.code`）找到行，遵循下一步操作。

| 代码 | 出现位置 | 下一步操作 |
|---|---|---|
| `PN-CLI-4001` *配置文件未找到* | 大多数 `prisma-next` 命令 | 运行 `prisma-next init`，或传递 `--config <path>`。 |
| `PN-CLI-4002` *合约配置缺失* | `contract emit`、`db *` | 在 `prisma-next.config.ts` 中添加 `contract: { ... }`。参见 `prisma-next-contract`。 |
| `PN-CLI-4003` *合约验证失败* | `contract emit`、`db *` | 在修复 `where.path` 中命名的合约源后重新运行 `pnpm prisma-next contract emit`。参见 `prisma-next-contract`。 |
| `PN-CLI-4005` *需要数据库连接* | `db *`、`migrate`、`migration status` | 传递 `--db <url>` 或在 `prisma-next.config.ts` 中设置 `db.connection`。 |
| `PN-CLI-4011` *配置中缺少扩展包* | `contract emit`（例如，合约使用 `pgvector.Vector(...)` 但配置未列出 pgvector 包） | 将 `meta.missingExtensions` 中命名的描述符添加到 `prisma-next.config.ts` 中的 `extensions`。参见 `prisma-next-contract`。 |
| `PN-CLI-4020` *迁移规划失败* | `db init`、`db update` | 检查 `meta.conflicts`。恢复是针对每个冲突的——链接到 `prisma-next-migrations`。 |
| `PN-CLI-5002/5003/5004/…` *初始化错误* | `prisma-next init` | 使用 `meta.missingFlags` 或 `meta.allowed` 中列出的缺失/无效标志重新运行。 |
| `PN-MIG-2001` *未填写的迁移占位符* | `node migrations/app/<dir>/migration.ts`（自我 emit）或 `migrate` | 编辑 `migration.ts`，将命名的 `placeholder("<slot>")` 替换为实际的查询闭包，自我 emit。参见 `prisma-next-migrations`。 |
| `PN-MIG-2002` *未找到 migration.ts* | 读取迁移包 | 从版本控制中恢复或使用 `migration plan` 构建一个全新的包。 |
| `PN-MIG-2003` *无效的默认导出* | 加载 `migration.ts` | 使用 `export default class extends Migration { ... }`（或工厂 `() => ({ ... })`）。参见 `prisma-next-migrations`。 |
| `PN-MIG-2005` *dataTransform 合约不匹配* | 构建数据转换查询计划 | 将相同的 `endContract` 引用传递给 `dataTransform(endContract, …)` 和查询构建器上下文。 |
| `PN-RUN-3001` *数据库未签名* | `db verify`、运行时启动 | 数据库还没有标记。运行 `prisma-next db init --db <url>`（基线空数据库）或 `db update --db <url>`（直接应用合约）。 |
| `PN-RUN-3002` *哈希不匹配* | `db verify`、运行时启动 | 标记与合约哈希不一致。要么向前迁移（`migrate` / `db update`），要么——如果数据库在手动修复后是正确的——`db sign`。参见 `prisma-next-migrations`。 |
| `PN-RUN-3003` *目标不匹配* | 运行时启动 | 合约目标 ≠ 配置目标；对齐它们（参见 `meta.expected` / `meta.actual`）。 |
| `PN-RUN-3004` *模式验证失败* | `db verify`（完整模式） | 检查 `meta.verificationResult`。运行 `db update` 以协调，或调整合约。 |
| `PN-RUN-3010` *模式验证失败（CLI 表面）* | `db verify` 模式仅 | 与 3004 相同。 |
| `PN-RUN-3020` *迁移运行器失败* | `migrate`、`db update`、`db init` | 检查 `meta` 以获取冲突；协调模式漂移，然后重新运行。之前应用的迁移将保留。 |
| `PN-RUN-3030` *需要确认的破坏性更改* | `db update`（交互式提示符触发；非交互式返回此代码） | 使用 `-y`（或 `--yes`）应用，或 `--dry-run` 预览。**只有 `db update` 有此流程**——`migrate` 不在标志上阻塞破坏性操作。 |
| `PN-RUN-3000` *(包装器)* | `migrate`、其他包装 `MigrationToolsError` 的命令 | 读取 `meta.code`。案例：`MIGRATION.HASH_MISMATCH`（重新 emit：`node migrations/app/<dir>/migration.ts`）；`MIGRATION.AMBIGUOUS_TARGET`（并发迁移——`prisma-next-migration-review`）；`MIGRATION.STALE_CONTRACT_BOOKENDS`（重新运行 `migration plan`）；`MIGRATION.NO_INVARIANT_PATH` / `MIGRATION.UNKNOWN_INVARIANT`（`prisma-next-migration-review`）；`MIGRATION.PATH_UNREACHABLE` / `MIGRATION.MARKER_MISMATCH`（运行 `migrate --show --db $URL` 以检查路径，然后 `migration plan --from <from> --to <target>` 或 `migration list` 以审计图——参见 `prisma-next-migration-review`）。 |
| `PN-SCHEMA-0001` | `db verify` 模式检查 | 活模式不满足合约。`meta.verificationResult` 包含差异。运行 `db update` 或调整合约。 |
| `MIGRATION.UP_TO_DATE` / `.DATABASE_BEHIND` | `migration status` `info` 诊断 | 信息性；退出 0。参见 `prisma-next-migration-review`。 |
| `MIGRATION.MISSING_INVARIANTS` | `migration status` `info` 诊断 | 活标记在结构上到达目标哈希，但没有携带目标引用所需的所有不变式。运行 `migrate --to <name> --db $URL` 以获取涵盖缺失不变式的路径。参见 `prisma-next-migration-review`。 |
| `MIGRATION.NO_MARKER` / `.MARKER_NOT_IN_HISTORY` / `.DIVERGED` / `CONTRACT.AHEAD` / `CONTRACT.UNREADABLE` | `migration status` `warn` 诊断（退出 0；CI 管道解析 `--json`） | 阅读 `severity` *和* `code`。`prisma-next-migration-review` 涵盖菱形/分歧/标记超出历史的流程。 |
| `BUDGET.ROWS_EXCEEDED` / `BUDGET.TIME_EXCEEDED` | 运行时，当 `budgets` 中间件激活时 | 调整 `budgets({ maxRows, maxLatencyMs, ... })` 或重写查询。参见 `prisma-next-runtime`。 |
| `LINT.SELECT_STAR` / `LINT.NO_LIMIT` / `LINT.DELETE_WITHOUT_WHERE` / `LINT.UPDATE_WITHOUT_WHERE` / `LINT.READ_ONLY_MUTATION` | 运行时，当 `lints` 中间件激活时 | 修复查询（添加 `WHERE` / `LIMIT` / 显式列），或放宽 lint 配置。参见 `prisma-next-runtime`。 |
| `PLAN.HASH_MISMATCH` | 运行时，执行预编译计划 | 构建计划的合约与运行时合约不匹配。重新 emit、重新构建、重新部署。 |
| `CONTRACT.MARKER_MISSING` / `CONTRACT.MARKER_MISMATCH` | 运行时，执行前标记检查 | 与 `PN-RUN-3001` / `PN-RUN-3002` 相同的系列，但在进程内由运行时而不是 CLI 抛出。恢复相同。 |
| `RUNTIME.ABORTED` (`details.phase` = `encode\|decode\|stream\|beforeExecute\|afterExecute\|onRow`) | 运行时，当 `AbortSignal` 在执行中途触发时 | 取消操作，不是错误；显示给调用者。 |
| `SqlQueryError`（无 `PN-` 代码） | 原始 SQL 路径显示驱动程序错误 | 检查 `sqlState` + `constraint` + `table` + `column`。Postgres `23505` = 唯一违反，`23503` = 外键违反，等等。修复数据或模式。 |
| TypeScript 错误提及功能（例如 `returning()` 未在类型上、`include` 的多关系不在多加载上） | 创作时，在任何信封触发之前 | 功能门控在合约中声明（`capabilities` 块，按目标/家族命名空间），而不是在 `prisma-next.config.ts` 中。路由到 `prisma-next-contract` 进行功能声明，并路由到 `prisma-next-queries` 以了解哪些方法门控哪些功能。启用后重新 emit（`pnpm prisma-next contract emit`）。 |
| TypeScript 错误提及 `db.orm.<Model>` 上缺失的字段/方法或陈旧的 `Contract` 形状 | 创作时 | 重新 emit（`pnpm prisma-next contract emit`）；确认 `db.ts` 使用 `postgres<Contract, TypeMaps>(...)` 实例化（类型参数传播合约类型）。参见 `prisma-next-runtime` 和 `prisma-next-contract`。 |

如果信封的 `code` 不在此表中，请按照信封的 `fix` 字段字面意思进行操作——那是框架的第一方下一步操作。如果 `fix` 为空或无帮助，通过 `prisma-next-feedback` 升级。

## 常见陷阱

1. **只读取 `summary`，不读取信封的其余部分。** `code`、`severity`、`why`、`fix`、`meta`/`details`，以及（对于 CLI 错误）`where` 都是承重部分。代理根据 `code` 路由；用户看到 `summary`。
2. **忽略 `severity`。** `migration status` 发出警告级别的诊断并**退出 0**。只检查退出代码的代理会错过所有并发迁移警告。
3. **在 `PN-RUN-3000` 上跳过 `meta.code`。** 该信封是包装器——真实代码在 `meta.code` 上。
4. **将漂移视为可以用 `db sign` 来抑制的东西。** `db sign` 从当前合约哈希写入标记，但它需要模式验证通过才能首先运行。在达到 `db sign` 之前运行 `db verify`。
5. **在部分失败后重新运行 `migrate` 而不检查状态。** `db schema --db <url>` 显示活形状；`migration status --db <url> --json` 显示标记实际所在的位置。

## Prisma Next 尚未实现的功能

- **Studio / GUI 数据库浏览器。** 没有第一方 Studio。替代方案：`prisma-next db schema` 以获取 CLI 活模式的树状结构，或使用第三方工具（TablePlus、DataGrip、`psql`）针对你的 `DATABASE_URL`。如果你需要一个内置 GUI，通过 `prisma-next-feedback` 提交功能请求。
- **第一类查询日志中间件。** 没有与框架一起提供的第一方“记录每个查询”中间件。替代方案：编写一个小型自定义中间件来包装每个操作（参见 `prisma-next-runtime` 以了解中间件组合）。如果你需要一个内置查询日志，通过 `prisma-next-feedback` 提交功能请求。
- **`EXPLAIN` 集成。** 没有 `.explain()` 在计划上。替代方案：将 EXPLAIN 作为原始查询编写（`db.sql.raw\`EXPLAIN ANALYZE ...\``；参见 `prisma-next-queries`）。如果你需要一个第一类 EXPLAIN，通过 `prisma-next-feedback` 提交功能请求。
- **作为用户界面表面的预处理语句缓存。** 适配器在幕后为参数化查询准备，但你不能预先准备并重新执行一个以名称命名的语句。替代方案：使用 TypedSQL（参见 `prisma-next-queries`）。如果你需要一个第一类预处理语句 API，通过 `prisma-next-feedback` 提交功能请求。

## 当信封无法路由时请求帮助

1. 使用 `-v` 重新运行（或 `--json` 以获取机器输出）以获取完整信封。
2. 如果信封确实无信息——空 `fix`、缺失 `meta`、通用 `summary`——那是框架功能差距；通过 `prisma-next-feedback` 提供信封、合约源（清理）和重现步骤。

## 检查清单

- [ ] 确定了信封形状（`CliErrorEnvelope`、`RuntimeErrorEnvelope`、`SqlQueryError`）。
- [ ] 读取了每个字段 — `code`、`severity`、`why`、`fix`、`meta`（或`details`）、如果存在则读取`where`。
- [ ] 如果`code`是`PN-RUN-3000`，则也读取`meta.code`。
- [ ] 根据`code`路由到下一步（并根据表格说明与匹配的创作技能链式调用）。
- [ ] 使用相关的CLI命令重新验证（`db verify`、`migration status --json`、`contract emit`、`migrate`）。
- [ ] 未创建Studio / EXPLAIN / 查询日志API — 使用了文档中的替代方案，并将未满足的功能缺口路由到`prisma-next-feedback`。
