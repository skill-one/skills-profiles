---
name: prisma-next-migrations
description: 作者 Prisma Next 迁移——选择数据库更新或迁移计划，编辑框架生成的 migration.ts（将占位符哨兵替换为 dataTransform 闭包），从 MIGRATION.HASH_MISMATCH 或 PN-MIG-2001 未填写的占位符中恢复。用于 prisma migrate dev、prisma migrate deploy、prisma db push、数据库更新、数据库更新 --dry-run、迁移计划、migrate、migration new、migration show、数据库验证、数据库签名、数据迁移、this.dataTransform、dataTransform、占位符、生成的 migration.ts、编辑 migration.ts、MIGRATION.HASH_MISMATCH、模式漂移。
---

# Prisma Next — 迁移编写

> **编辑你的数据合约。Prisma Next 规划迁移。你负责填写任何数据转换。**

三步用户模型：

1. **你编辑你的数据合约。** (`prisma-next-contract`)
2. **Prisma Next 为你规划迁移。** ← 这个功能
3. **如果需要数据转换，你编辑 `migration.ts` 并自行触发。** ← 这个功能

一旦合约发生变化，你选择如何将变更应用到数据库。这个功能涵盖了两种路径（`db update` 和 `migration plan` + `migrate`）、迁移包合约、`migration.ts` 编写 API 以及你在不离开循环的情况下恢复的失败模式。

**目标。** 迁移编写对 **Postgres** 和 **Mongo** 都是首选功能。CLI 从 `prisma-next.config.ts` 读取目标（在 `prisma-next init --target …` 时设置）。迁移命令不接受 `--target` 标志 — 使用针对你需要的目标的配置。下文中的示例会指出在它们出现分歧时目标特定的导入、标记、工厂和事务行为。

## 何时使用

- 用户编辑了合约并希望将变更应用到数据库。
- 用户希望编写包含数据转换的迁移。
- 用户希望对本地数据库运行待处理的迁移。
- 用户遇到 `MIGRATION.HASH_MISMATCH`、`PN-MIG-2001`（未填充的占位符）或部分应用的迁移。
- 用户提到：*migrate, migration, db push, db update, `prisma migrate dev`, `prisma migrate deploy`, drift, hash mismatch, data backfill*。

## 何时不用

- 用户想知道在部署/合并时将运行哪些迁移，或管理引用和不变量 → `prisma-next-migration-review`。
- 用户希望编辑合约 → `prisma-next-contract`。
- 用户希望深入了解单个结构化错误包 → `prisma-next-debug`。

## 关键概念

- **`db update` (快速路径)。** 读取已触发的合约，与实时数据库进行差异比较，应用变更。可选 `--dry-run` 在不执行的情况下打印计划。交互式破坏操作确认（或 `-y` 自动接受）。**不写入迁移目录。** 需要数据转换的操作不由此路径处理 — `db update` 完全排除了 `data` 操作类，并在需要数据转换时短路。仅用于没有与其他任何人共享历史的数据库（你的本地开发数据库）。
- **`migration plan` (正式路径)。** 读取已触发的合约，与磁盘上的迁移图头部进行差异比较，在 `migrations/app/<YYYYMMDDTHHMM>_<snake_slug>/` 下写入新的迁移包。如果任何操作需要数据转换，该包的 `migration.ts` 包含 `placeholder(...)` 调用供你填充。
- **迁移路径中的 `app/` 段是消费应用程序的合约空间 ID。** 你编写的每个迁移都位于 `migrations/app/` 下。你的合约依赖的扩展会获得自己的兄弟目录（`migrations/<extension-space-id>/`），这些目录由扩展包管理，你不会写入它们。第一次对应用级配置运行 `migration plan` / `db init` 时，`app/` 段会自动生成。
- **迁移包文件**（在每个 `migrations/app/<dir>/` 内）：
  - `migration.json` — 元数据（元数据 + `migrationHash`）。
  - `ops.json` — 标准操作列表。内容寻址；`migrationHash` 是基于此计算的。
  - `migration.ts` — TypeScript 编写源，**由框架渲染**的 `migration plan`（或 `migration new`）。你编辑其中的特定占位符（见下文 *填充占位符*），并通过运行它来重新触发 `ops.json` / `migration.json`。
- **合约快照。** `migration.ts` 从共享的、内容寻址的存储 `migrations/snapshots/<hex>/contract.json` + `contract.d.ts`（`<hex>` 是合约的 64-hex 存储哈希）导入其书端合约 — 不是从迁移包内的文件导入。
- **自行触发。** 运行 `node migrations/app/<dir>/migration.ts` 从（可能编辑过的）TS 源重新生成 `ops.json` 和 `migration.json`。这是更新现有迁移包的唯一支持方式。
- **`migration.ts` 结构。** 由框架渲染。一个扩展 `Migration`（在 Mongo 上来自 `@prisma-next/family-mongo/migration`，或在 Postgres 上通过 `@prisma-next/postgres/migration` 重新导出 — 见下文框架块），其 `operations` 获取器返回工厂调用值的数组。文件以 `MigrationCLI.run(import.meta.url, M)` 结尾，执行它将自行触发。
- **`placeholder(slot)`。** 规划器在渲染的 `migration.ts` 中发出的哨兵（在 Mongo 上来自 `@prisma-next/errors/migration`，或在 Postgres 上来自 `@prisma-next/postgres/migration` 导入）的任何需要数据转换的地方。在触发时调用 `placeholder(...)` 会抛出 `PN-MIG-2001` *未填充的迁移占位符*。用户将 `() => placeholder(...)` 箭头替换为真实的查询计划闭包（Postgres）或填充 `dataTransform({ check, run })` 源（Mongo — 见 *填充占位符*），然后自行触发。
- **`this.dataTransform(endContract, name, { check, run })`。** 数据转换工厂。`check` 是一个行集查询，任何行的存在都表示“仍有工作要做”；`run` 是一个或多个执行回填的变异查询。两者都是针对 `endContract` 构建的查询计划构建的惰性闭包。执行者将 `check` 包装为 `EXISTS(...)` 进行预检查和 `NOT EXISTS(...)` 进行后检查，因此相同的闭包断言“有工作”和“工作已完成”。
- **`pendingPlaceholders`。** `migration plan` JSON 结果上的布尔字段。`true` 表示包已写入但包含未填充的占位符 — `migrate` 会抛出 `PN-MIG-2001`，直到你编辑 `migration.ts` 并自行触发。
- **`migrationHash`。** 迁移包的内容寻址身份。当 `migration.json` 中存储的哈希与从磁盘文件重新计算的哈希不一致时（几乎总是：有人编辑了 `migration.ts` 而没有自行触发），会触发 `MIGRATION.HASH_MISMATCH`。
- **标记。** 记录“此数据库在合约哈希 X 时处于空间 Y”。**Postgres：** `prisma_contract.marker` 表中的一行。**Mongo：** `_prisma_migrations` 集合中的一个文档（按空间键值）。每个成功的迁移在空间通过模式验证后都会推进标记一次。`db sign` 从当前合约哈希写入标记，但只有在模式验证成功后才会写入（它不会对实时模式与合约不一致的数据库进行签名）。
- **应用原子性。** **Postgres：** 每个迁移都在 `BEGIN ... COMMIT` 内运行；失败时，Postgres 回滚，标记保持在先前迁移的 `to` 哈希。**Mongo：** DDL 操作（`createCollection`、`createIndex`、`collMod`、`setValidation`、…）没有包裹在多文档事务中；执行者应用操作，验证实时模式与目标合约，只有在验证通过时才推进标记（跨空间可恢复 — 见 MongoDB 家族文档）。普通的 DDL + `dataTransform` 流保持一致；失败迁移的部分状态通过 `db verify` / `db schema` 诊断，而不是假设不存在。
- **操作类。** 每个操作声明一个 `operationClass`：`additive`、`widening`、`data` 或 `destructive`。CLI 在计划预览和 JSON 输出中显示这些。没有 `long-running` 类，框架不会触发 `CREATE INDEX CONCURRENTLY` — 操作保持事务性。

## `migration.ts` 由框架渲染，而非手写

`migrations/<space-id>/<timestamp>/migration.ts`（对于你自己的应用，`<space-id>` 总是 `app/`）下的文件由框架为你渲染 — `prisma-next migration plan` 在合约变化时写入填充的包，而 `prisma-next migration new` 在你希望直接编写操作时写入空的骨架。你不从零开始编写这些文件。你编辑框架留下的特定占位符 — 主要替换 `placeholder("<slot>")` 哨兵（Postgres）或填充 `dataTransform({ check, run })` 管道槽（Mongo）— 然后自行触发。

**Postgres** 渲染的导入指向 `@prisma-next/postgres/migration`（对于 SQLite 项目是 `@prisma-next/sqlite/migration`）。

**Mongo** 渲染的导入使用 `@prisma-next/family-mongo/migration` 作为 `Migration` 基类，使用 `@prisma-next/target-mongo/migration` 作为操作工厂（`createIndex`、`dataTransform`、…）。`MigrationCLI` 来自 `@prisma-next/cli/migration-cli`。

将渲染的导入行视为两个目标上的框架管理：

- 将它们留在原地。不要重写它们到不同的 `@prisma-next/<…>` 路径；框架的渲染器是权威形状，你手动做的任何更改在下一次重新渲染或自行触发时都会被撤销（并且可能会触发 `MIGRATION.HASH_MISMATCH`）。
- 如果你需要额外的工厂符号，**将它添加到现有的渲染导入行**（Postgres：`@prisma-next/postgres/migration`；Mongo：`@prisma-next/target-mongo/migration`），而不是从不同的 `@prisma-next/...` 子路径引入第二个导入。
- “用户代码仅从 `@prisma-next/<target>` 导入”的约定适用于你自己的模块（查询、运行时设置、合约编写）。框架渲染的 `migration.ts` 框架是框架的表面，不是你的；该规则对此文件暂停。

## 你路由的诊断代码

| 代码 | 来源 | 操作 |
|---|---|---|
| `PN-MIG-2001` *未填充的迁移占位符* | 抛出 `placeholder(...)` 时 | 打开 `migration.ts`，将命名的 `placeholder("<slot>")` 调用替换为真实的查询闭包，自行触发。 |
| `PN-MIG-2002` *找不到 migration.ts* | 读取迁移包时 | 包格式不正确。从版本控制中恢复，或运行 `prisma-next migration new` 获取一个干净的。 |
| `PN-MIG-2003` *无效的默认导出* | 加载 `migration.ts` 时 | 文件的默认导出不是一个 `Migration` 子类或工厂函数。从版本控制中恢复规划器发出的骨架或重新运行 `migration plan` 获取干净的包。 |
| `PN-MIG-2005` *dataTransform 合约不匹配* | 构建数据转换查询计划时 | 查询构建器使用与传递给 `this.dataTransform(...)` 的 `endContract` 不同的合约引用。使用模块作用域导入的 `endContract` 进行两者。 |
| `MIGRATION.HASH_MISMATCH` *迁移包已损坏* | `migrate`（或任何读取包的操作） | `ops.json` / `migration.json` 被编辑而没有自行触发。运行 `node migrations/app/<dir>/migration.ts` 重新触发，然后重新运行 `migrate`。 |
| `PN-RUN-3002` *哈希不匹配* | `db verify` | 标记与合约哈希不一致（**Postgres：** `prisma_contract.marker`；**Mongo：** `_prisma_migrations`）。数据库处于与代码认为不同的合约版本。要么运行迁移向前，要么 — 如果数据库正确且标记在手动修复后已过时 — 运行 `db sign`。 |
| `PN-RUN-3001` *数据库未签名* | 任何需要标记的命令 | 数据库还没有标记。运行 `prisma-next db init --db <url>` 基线一个空数据库，或 `db update --db <url>` 直接应用当前合约。 |

## 决策 — 你选择哪条路径？

| 情况 | 路径 | 原因 |
|---|---|---|
| 本地开发，模式在变化中 | `db update` | 快速、交互式、没有迁移文件。 |
| 与其他开发人员共享分支 | `migration plan` + `migrate` | 可重放、可审查、内容哈希。 |
| 任何到达生产环境 | `migration plan` + `migrate` | 生产必须运行经过审查的、哈希的迁移。 |
| 添加需要回填的列 | `migration plan`（写入 `placeholder`），编辑 `migration.ts`，自行触发，然后 `migrate` | `db update` 不编写数据转换；正式路径会。 |
| 从漂移中恢复（数据库与合约偏离） | 在手动修复后运行 `db sign`，*或* 如果 PN 可以规划修复的 `migration plan` | 取决于哪一方是正确的。见下文 *从漂移中恢复*。 |

## 开发 → 发送过渡（`db` 引用模式）

示例 — 本地使用 `db update` 迭代，然后发布第一个真实迁移：

```bash
pnpm prisma-next db init --db $DATABASE_URL
pnpm prisma-next contract emit && pnpm prisma-next db update --db $DATABASE_URL
pnpm prisma-next contract emit && pnpm prisma-next migration plan --name add_feature
pnpm prisma-next migrate --db $DATABASE_URL
pnpm prisma-next db verify --db $DATABASE_URL
```

`db` 引用是一个在 `migrations/app/refs/db.json` 中的命名指针 — `{ hash, invariants }`。它记录了项目开发数据库已提升到的合约哈希 — 离线规划器的替代方案，用于在计划时无需连接即可“我的本地数据库在哪里？”。它命名的合约通过 `migrations/snapshots/<hex>/contract.json` 中的哈希解析通过共享的内容寻址存储，每个迁移图节点都通过该存储解析。

**`db init` / `db update` 写入的内容。** 当针对项目的默认 `--db` URL 运行时（没有显式 `--db` 标志），这两个命令隐式地推进 `db` 引用：它们将命令后的合约 IR 写入快照存储，然后写入引用的指针。使用 `--advance-ref <name>` 覆盖引用名称。当你传递 `--db <非默认 URL>` 时，除非显式指定 `--advance-ref`，否则会抑制引用推进 — 调整不同数据库与此项目的开发状态检查点不同。

磁盘布局只是一个指针：

```text
migrations/app/refs/
└── db.json                 # { "hash": "<hex>", "invariants": [] }
```

**开发迭代后的第一个 `migration plan`。** `migration plan` 默认 `--from` 为 `db` 引用。当磁盘上的迁移图仍然 **为空** 且 `db` 引用指向一个非空的哈希，并且存储中有条目（在 `db update` 循环后通常是这种情况）时，规划器会发出 **两个** 套件而不是一个：

1. 基线：`null → from-hash`（引入 `from-hash` 作为图节点）
2. 差异：`from-hash → current_contract`

两者在一次调用中写入磁盘 — 预期在 `git status` 中看到两个新的目录。`migrate` 然后找到一条通过基线的路径并应用差异。这关闭了开发 → 发送陷阱，其中单个包计划引用了一个尚未成为图节点的哈希，并生成了一个不可撤销的迁移（`MIGRATION.PATH_UNREACHABLE` 在应用时）。

**忘记标志的陷阱。** 当图 **非空** 时，默认 `db` 引用可能指向 **图尖端之后**（在迭代时每次 `db update` 都会推进引用，但你从未提交迁移）。下一个隐式默认 `migration plan` 会拒绝 `MIGRATION.HASH_NOT_IN_GRAPH` 并命名可到达的引用，这些引用指向图节点。

在看到 `MIGRATION.HASH_NOT_IN_GRAPH` 时恢复：

```bash
# 选项 A — 明确从图节点计划
pnpm prisma-next migration plan --from production --name my_change

# 选项 B — 将 db 引用对齐到图节点哈希，然后使用默认值计划
pnpm prisma-next ref set db <graph-node-hash>
pnpm prisma-next migration plan --name my_change
```

如果 `db` 引用的指针本身丢失，且哈希也不是图节点（`MIGRATION.SNAPSHOT_MISSING`），使用 `ref set db <hash>` 创建它，或使用 `db update --advance-ref db` 推进它。

**在 `plain migrate` 之后。** `migrate` 不会隐式推进 `db` 引用（生产形状的命令保持显式）。实时标记会推进，而引用可能滞后。使用 `db update`（在数据库已经当前时无操作）或同一调用中的 `migrate --advance-ref db` 刷新。

**何时切换路径。** 在独占开发数据库的模式在变化时使用 `db update`。当变更需要可审查、可重放的迁移时切换到 `migration plan` + `migrate` — 通常在打开 PR 或触摸任何共享环境之前。`db` 引用桥接这两种路径：它将开发迭代状态捕获到磁盘上，以便第一个正式计划知道你从哪里开始。

**图节点规则（计划时间）。** 任何用作 `from` 端的哈希（显式 `--from`、默认 `db` 引用或引用名称）在图非空时必须已经是在磁盘上的迁移图中的节点。自动基线双束发射是唯一的例外：它仅适用于**空**的图，具有非空的引用解析 `from` 和可用的存储条目。如果引用的指针丢失且哈希不是图节点，计划将拒绝并返回 `MIGRATION.SNAPSHOT_MISSING`。

**应用时间补充。** `migrate` 在 DDL 之前读取活动标记。如果标记哈希不是图节点，命令将拒绝并返回 `MIGRATION.MARKER_MISMATCH` — 捕获离线规划器无法看到的漂移。这与 `MIGRATION.MARKER_NOT_IN_HISTORY` 不同，后者在运行器图遍历过程中较晚触发，当时标记不在正在遍历的路径上。有关完整诊断目录，请参阅 `prisma-next-migration-review`。

`db` 是一个**默认引用名称**，不是保留名称。框架在下一个开发周期中会覆盖它；你可以显式地 `ref set db <hash>` 并接受在针对默认 URL 运行时后续的 `db update` 会替换它。

规范细节：[迁移系统 § 通过快照存储解析契约](../../docs/architecture%20docs/subsystems/7.%20Migration%20System.md#contract-resolution-through-the-snapshot-store)、[§ `migration plan`](../../docs/architecture%20docs/subsystems/7.%20Migration%20System.md#migration-plan)、[§ 恢复功能](../../docs/architecture%20docs/subsystems/7.%20Migration%20System.md#recovery-affordances)、[ADR 218 — 具有配对契约快照和通用图节点不变性的引用](../../docs/architecture%20docs/adrs/ADR%20218%20-%20Refs%20with%20paired%20contract%20snapshots%20and%20universal%20graph-node%20invariant.md) (TML-2629，其配对快照部分已被取代 — 请参阅 ADR 的状态说明)，以及 [ADR 240 — 契约快照存储在内容寻址存储中](../../docs/architecture%20docs/adrs/ADR%20240%20-%20Contract%20snapshots%20live%20in%20a%20content-addressed%20store.md)。

## 工作流 — `db update`（快速路径）

概念：`db update` 将目标（发射的契约）与实时数据库解析，并应用差异。使用 `--dry-run` 预览。破坏性操作会提示交互式确认，除非你传递 `-y` 或 `--no-interactive`。路径不包括 `data` 类型的操作 — 如果差异需要数据转换，`db update` 会因规划错误而失败，你需要切换到 `migration plan` 来编写转换。

在契约编辑后运行：

```bash
pnpm prisma-next contract emit
# Postgres: --db postgresql://...
# Mongo:    --db mongodb://...  (开发脚手架通常需要 ?replicaSet=rs0)
pnpm prisma-next db update --db $DATABASE_URL --dry-run
pnpm prisma-next db update --db $DATABASE_URL
```

`db update` 已经验证了模式并在成功时推进标记 — 在顺利路径上，后续的 `db verify` 是多余的。仅在需要独立的诊断时使用 `db verify`（见 *Verify contract vs DB*）。

检查 JSON 输出来驱动下一步行动：

```bash
pnpm prisma-next db update --db $DATABASE_URL --json
```

JSON 包含 `plan.operations[]`，其中每个 `operationClass`，以及在应用模式下 `execution.operationsExecuted` 和应用后的 `marker.storageHash`。如果命令因破坏性操作失败，错误包的 `meta.destructiveOperations[]` 会列出将要被删除的确切内容。

## 工作流 — `migration plan` + `migrate`（正式路径）

概念：`migration plan` 在磁盘上写入一个新的迁移包。如果规划器需要任何数据转换，该包将是*挂起的* — `migration.ts` 包含 `placeholder(...)` 调用，直到你填充它们。`migrate` 依图顺序运行每个挂起的包，事务性地。

计划更改：

```bash
pnpm prisma-next contract emit
pnpm prisma-next migration plan --name <snake_slug>
```

读取结果。JSON 结构暴露了可查询的信号：

- `dir` — 新包的路径（例如 `migrations/app/20260515T1200_add_user_email/`）。
- `pendingPlaceholders` — 如果 `migration.ts` 仍然包含 `placeholder(...)` 调用，则为 `true`。
- `operations[].operationClass` — 用于识别 `destructive` 和 `data` 操作。
- `preview.statements` — 与家族无关的文本预览。

检查包：

```bash
pnpm prisma-next migration show
pnpm prisma-next migration show <dirName-or-migrationHash-prefix>
```

`migration show` 显示单个迁移包。要查看将运行的迁移有序列表（跨所有契约空间），请使用 `migrate --show`：

```bash
# 在线：读取实时数据库标记作为起点。
pnpm prisma-next migrate --show --db $DATABASE_URL

# 离线：从任何引用或哈希的假设路径。
pnpm prisma-next migrate --show --from <hash-or-ref> --to <hash-or-ref>
```

`migrate --show` 是只读的，永远不会写入数据库或迁移图。在应用之前使用它以确认执行顺序。

填充任何数据转换（见 *Fill a placeholder*），如果你编辑了 `migration.ts`，则自发射，然后：

```bash
pnpm prisma-next migrate --db $DATABASE_URL
```

`migrate` 无需提示运行 — 破坏性操作的确认存在于 `db update` 中，而不是在这里。在应用之前，在计划输出或 `migration show` 中审查破坏性操作。

## 工作流 — 填充占位符

概念：规划器可以检测到需要*数据转换*，但不能检测到它应该*做什么*。它会写入一个类型化的脚手架并停止；你填充转换，然后自发射。

### Postgres

规划器可以检测到需要数据转换（例如用无默认值的 `NOT NULL` 列进行回填），但不能检测到它应该做什么。你用针对 `endContract` 构建的查询计划填充 `check` 和 `run` 闭包。

规划器发射的脚手架看起来像：

```typescript
// migrations/app/20260515T1200_add_user_name/migration.ts
import endContract from '../../snapshots/93f07d1b…c9e1e5a2/contract.json' with { type: 'json' };
import { Migration, MigrationCLI, addColumn, placeholder } from '@prisma-next/postgres/migration';

export default class M extends Migration {
  override get operations() {
    return [
      addColumn('public', 'user', {
        name: 'name',
        typeSql: 'text',
        defaultSql: '',
        nullable: true,
      }),
      this.dataTransform(endContract, 'backfill user.name', {
        check: () => placeholder('backfill user.name:check'),
        run:   () => placeholder('backfill user.name:run'),
      }),
    ];
  }
}

MigrationCLI.run(import.meta.url, M);
```

用从 `endContract` 构建的查询计划闭包替换两个 `placeholder(...)` 调用。`check` 闭包必须返回一个**行集查询，其任何行的存在都表示“仍有工作要做”** — 通常 `<table>.select('id').where(<violation predicate>).limit(1)`。标量/聚合形状 (`count(*)`、`bool_and(...)`) 默默地破坏契约：运行器两次包装 `check` (`EXISTS(...)` 用于预检查，`NOT EXISTS(...)` 用于后检查)，并且始终返回一行数据的查询使 `EXISTS` 始终为真，`NOT EXISTS` 始终为假。

使用 `endContract` 构建查询构建器，以便存储哈希对齐 — 使用不同的契约引用会引发 `PN-MIG-2005`。填充后的形状（上面渲染的脚手架，其中 `placeholder(...)` 调用被替换；如果你需要一个额外的工厂，如 `setNotNull`，请将其添加到现有的 `@prisma-next/postgres/migration` 导入行，而不是编写第二个导入）。有关周围的 `db` 设置，请参阅 `prisma-next-queries`：

```typescript
import endContract from '../../snapshots/93f07d1b…c9e1e5a2/contract.json' with { type: 'json' };
import { Migration, MigrationCLI, addColumn, setNotNull } from '@prisma-next/postgres/migration';
import { db } from './db'; // sql({ context: createExecutionContext({ contract: endContract, ... }) })

export default class M extends Migration {
  override get operations() {
    return [
      addColumn('public', 'user', {
        name: 'name',
        typeSql: 'text',
        defaultSql: '',
        nullable: true,
      }),
      this.dataTransform(endContract, 'backfill user.name', {
        check: () => db.users.select('id').where((f, fns) => fns.eq(f.name, null)).limit(1),
        run:   () => db.users.update({ name: '' }).where((f, fns) => fns.eq(f.name, null)),
      }),
      setNotNull('public', 'user', 'name'),
    ];
  }
}

MigrationCLI.run(import.meta.url, M);
```

自发射：

```bash
node migrations/app/20260515T1200_add_user_name/migration.ts
```

自发射会重新生成 `ops.json` 并重新计算 `migrationHash` 在 `migration.json` 中。下一个 `migrate` 将看到一个一致的包。

### Mongo

Mongo `dataTransform` 操作使用 `{ check, run }` 对象，其 `source` / `run` 返回 Mongo 查询计划形状（通常来自 `@prisma-next/mongo-query-ast/execution` 的 `RawAggregateCommand` / `RawUpdateManyCommand`）。规划器可能会在这些源中保留 `placeholder(...)`，直到你填充它们。每个渲染的 `migration.ts` 包括 `describe()` 书签（`from` / `to` 契约哈希）— 上面 Postgres 示例为简洁起见省略了它们。从 `@prisma-next/target-mongo/migration` 导入工厂：

```typescript
import { MigrationCLI } from '@prisma-next/cli/migration-cli';
import { Migration } from '@prisma-next/family-mongo/migration';
import { createIndex, dataTransform } from '@prisma-next/target-mongo/migration';
import { RawAggregateCommand, RawUpdateManyCommand } from '@prisma-next/mongo-query-ast/execution';

class M extends Migration {
  override describe() {
    return { from: '<hex>', to: '<hex>', labels: ['normalize-names'] };
  }

  override get operations() {
    return [
      createIndex('users', [{ field: 'name', direction: 1 }]),
      dataTransform('lowercase-user-name', {
        check: {
          source: () => ({
            collection: 'users',
            command: new RawAggregateCommand('users', [
              { $match: { name: { $regex: '[A-Z]' } } },
              { $limit: 1 },
            ]),
            meta: { target: 'mongo', storageHash: '…', lane: 'mongo-pipeline', paramDescriptors: [] },
          }),
        },
        run: () => ({
          collection: 'users',
          command: new RawUpdateManyCommand(
            'users',
            { name: { $exists: true } },
            [{ $set: { name: { $toLower: '$name' } } }],
          ),
          meta: { target: 'mongo', storageHash: '…', lane: 'mongo-raw', paramDescriptors: [] },
        }),
      }),
    ];
  }
}

export default M;
MigrationCLI.run(import.meta.url, M);
```

同样方式自发射：`node migrations/app/<dir>/migration.ts`。

## 工作流 — 手动编写迁移

概念：相同的 `Migration` 类形状允许你在规划器无计划可做时直接编写操作（自定义数据修复、扩展安装、基线）。即使在这种情况下，你也不需要从头开始编写文件 — `migration new` 会为你渲染一个空包，你编辑其中的 `operations` 获取器，然后自发射。

```bash
pnpm prisma-next migration new --name <snake_slug>
```

将目标工厂名称添加到框架渲染的导入行中（Postgres: `@prisma-next/postgres/migration`；Mongo: `@prisma-next/target-mongo/migration`）。使用 `--help` 和渲染器发射的导入列表进行浏览。

**Postgres** 工厂（代表性集合）：

- 表：`createTable`、`dropTable`。
- 列：`addColumn`、`dropColumn`、`alterColumnType`、`setNotNull`、`dropNotNull`、`setDefault`、`dropDefault`。
- 约束：`addPrimaryKey`、`addForeignKey`、`addUnique`、`dropConstraint`。
- 索引：`createIndex`、`dropIndex`。
- 枚举：`createEnumType`、`addEnumValues`、`renameType`、`dropEnumType`。
- 依赖：`createSchema`、`createExtension`、`installExtension`。
- 原始逃逸通道：`rawSql({ id, label, operationClass, target, precheck, execute, postcheck, ... })`。
- 数据转换：`this.dataTransform(endContract, name, { check, run })`（实例方法，不是自由工厂）。

**Mongo** 工厂（来自 `@prisma-next/target-mongo/migration`）：

- 集合：`createCollection`、`dropCollection`、`validatedCollection`、`setValidation`。
- 索引：`createIndex`、`dropIndex`。
- 集合选项：`collMod`。
- 数据转换：`dataTransform(name, { check, run })`（自由工厂；`check`/`run` 使用 Mongo 查询计划形状）。

每次编辑后自发射 (`node migrations/app/<dir>/migration.ts`)。

## 工作流 — 检查实时模式

概念：`db schema` 是只读的，永远不会写入文件。默认情况下，它按树形打印实时模式，或使用 `--json` 作为 JSON。在规划和作为验证的一部分时使用它。

```bash
pnpm prisma-next db schema --db $DATABASE_URL
pnpm prisma-next db schema --db $DATABASE_URL --json > schema.json
```

没有内置的过滤标志 — 如果只想要一个表，请将 JSON 通过 `jq`（或你喜欢的 JSON 工具）。

## 工作流 — 验证契约与数据库（诊断）

概念：`db verify` 是一个**独立的诊断** — 不是在 `db update` 或 `migrate` 在顺利路径上的常规步骤（这些命令在成功时已经验证并推进了标记）。当你怀疑漂移或需要证明数据库与契约匹配时，请使用 `db verify`：

- 跟随手动 SQL 或 ad-hoc 编辑，这些编辑在 Prisma Next 外部。
- 恢复数据库备份时。
- 如果 `migrate` 失败或部分应用（尤其是在 Mongo 上，DDL 是可恢复的，而不是事务包装的）。
- 当 `PN-RUN-3002` / `PN-RUN-3001` 在运行时或从另一个命令中出现时。

模式：

- 默认 — 完全验证（模式 + 标记）。
- `--marker-only` — 跳过模式验证，仅检查标记。
- `--schema-only` — 跳过标记验证，仅检查模式满足契约。
- `--strict` 添加：契约中不存在的模式元素是错误（默认是“数据库可能有额外内容”）。

```bash
pnpm prisma-next db verify --db $DATABASE_URL
```

在不匹配的情况下，错误包会命名失败模式（`PN-RUN-3002` 哈希不匹配、`PN-RUN-3001` 标记丢失、目标不匹配、与结构化路径相关的模式问题）。

## 工作流 — 重新签名标记

概念：`db sign` 将标记重写为当前契约哈希。在手动修复后使用，此时数据库是真相来源，而标记已过时。`db sign` 首先执行模式验证，并拒绝签署与契约不一致的数据库 — 因此成功的签名始终意味着模式匹配，并且标记现在是正确的。

```bash
pnpm prisma-next db sign --db $DATABASE_URL
```

## 工作流 — 从漂移中恢复

概念：漂移意味着 `db verify` 报告实时数据库模式与标记所说的它应该是什么不匹配。有两种有效操作，选择哪一方正确：

- **契约正确；数据库错误** → 运行迁移。`db update`（快速路径，仅限开发数据库）或 `migration plan` + `migrate`（其他所有地方）。
- **数据库正确；契约或标记错误** → 编辑契约以匹配数据库（见 `prisma-next-contract`），发射，然后 `db sign` 刷新标记。

揭示哪一方正确的诊断：

```bash
pnpm prisma-next db schema --db $DATABASE_URL --json
pnpm prisma-next db verify --db $DATABASE_URL --json
```

使用 `db verify` 确认哪一方错误，然后在任何分支后重新运行它，直到它返回 `ok` 且没有诊断。

## 工作流 — 从部分应用的迁移中恢复

概念：在 **Postgres** 上，每个迁移都在事务内应用 — 中间迁移失败会回滚，并且标记保持在先前迁移的 `to` 哈希。在 **Mongo** 上，DDL 可恢复，通过验证门控标记推进；使用 `db verify` / `db schema` 诊断，修复失败的包的 `migration.ts`，自发射，然后重新运行 `migrate`。

能够导致部分状态泄露的失败包括：Postgres `rawSql(...)` 步骤在事务包装器外部、Mongo DDL 部分应用在验证失败之前，或外部副作用（从 `run` 闭包调用其他系统）。

诊断：

```bash
pnpm prisma-next db verify --db $DATABASE_URL --json
pnpm prisma-next db schema --db $DATABASE_URL --json
```

修复并重新运行 `migrate`：

```bash
node migrations/app/<dir>/migration.ts
pnpm prisma-next migrate --db $DATABASE_URL
```

如果失败是由于外部系统部分更改的带外副作用，请在重新应用之前手动修复这些系统。

## 工作流 — 从 `MIGRATION.HASH_MISMATCH` 恢复

概念：`migrationHash` 是内容寻址的。不匹配意味着 `migration.json` 存储的哈希与从 `ops.json`（以及元数据）重新计算的哈希不一致。原因几乎总是：有人编辑了 `migration.ts` 但忘记自我发出。补救措施是自我发出有问题的包。

```bash
node migrations/app/<dir>/migration.ts
pnpm prisma-next migrate --db $DATABASE_URL
```

如果自我发出本身失败（例如，合约已经变更，操作不再适用于迁移的最终合约），则该包已过时。要么从版本控制中恢复它，要么删除它并使用 `migration plan` 重新规划。

## 工作流 — 解决破坏性操作提示（仅 `db update`）

概念：当 `db update` 将删除列或表时，它会停止并询问是否应用。提示是 `db update` 特有的——`migrate` 不提示并运行迁移包中包含的内容，因此请在 `migrate` 之前查看计划或调用 `migration show`。

当 `db update` 交互式报告破坏性操作时，警告会列出它们。提示是：

> 应用破坏性更改？此操作无法撤销。

路由：

- 如果数据不再需要，请回答是。
- 回答否，然后：
  - 通过 `migration plan` 重新塑造迁移，并手动编辑 `migration.ts` 以保留数据（例如，复制到新列，然后删除），或
  - 通过回滚合约更改来跳过破坏性操作。

在非交互式上下文（CI、`--no-interactive`、`--json`）中，破坏性操作的响应作为结构化错误返回——`meta.destructiveOperations[]` 列出将要被删除的内容。使用 `-y` 重新运行以自动接受，或单独处理每个操作。

## 常见陷阱

1. **对共享或生产数据库使用 `db update`。** 绝对不要。更改不会留下迁移历史记录。使用 `migration plan` + `migrate`。
2. **跳过数据转换。** 在 `migration.ts` 中保留 `placeholder(...)` 会导致下一个 `migrate` 抛出 `PN-MIG-2001`。填写所有占位符槽并自我发出。
3. **直接编辑 `ops.json`。** 它是规范工件，不是编写源。编辑 `migration.ts`，然后自我发出。
4. **编辑 `migration.ts` 后忘记自我发出。** 下一个 `migrate` 要么使用过时的 `ops.json`（如果你只添加了注释），要么因操作更改而失败，报 `MIGRATION.HASH_MISMATCH`。始终自我发出。
5. **在成功的 `db update` 或 `migrate` 后进行常规 `db verify`。** 在顺利路径上冗余——保留 `db verify` 用于漂移诊断（手动编辑、恢复、失败的 `migrate`）。
6. **Postgres `this.dataTransform` 中的聚合 `check` 闭包。** 返回 `count(*)` 或 `bool_and(...)` 会破坏预检查/后检查契约——两边都解析为常量。使用行集形状：`select('id').where(<violation>).limit(1)`。
7. **一个迁移中有两个合约引用。** 对与传递给 `this.dataTransform(endContract, ...)` 的合约不同的查询计划会引发 `PN-MIG-2005`。始终在模块作用域中导入 `endContract` 一次并使用相同的引用。
8. **重命名并期望规划器检测到它（Postgres）。** Prisma Next 目前没有合约内重命名提示；规划器会发出破坏性删除+添加。手动编辑 `migration.ts` 以将破坏性操作重写为 `rawSql({ ... })`，发出 `ALTER TABLE ... RENAME COLUMN ...`（或使用两个迁移的保留/回填/删除模式），然后自我发出。参见 `prisma-next-contract` § *编辑字段 — 重命名*。
9. **从空白文件手动编写 `migration.ts`，或重写渲染的导入行。** 迁移文件是框架渲染的——让 `prisma-next migration plan`（或 `migration new`）渲染包，然后仅编辑框架为你留下的空白。在 Postgres 中保留渲染的 `@prisma-next/postgres/migration`（或 `@prisma-next/sqlite/migration`）导入路径；在 Mongo 中使用 `@prisma-next/family-mongo/migration` + `@prisma-next/target-mongo/migration` 作为渲染的。在现有的工厂导入行中添加符号，而不是引入新的导入路径。

## Prisma Next 尚未实现的功能

- **运行时应用迁移。** Prisma Next 不会从你的应用的启动代码中应用挂起的迁移（“Drizzle 模式”用于无服务器/边缘）。解决方法：在应用启动前从你的部署管道中运行 `prisma-next migrate`。如果你需要内置的运行时应用，请通过 `prisma-next-feedback` 技能提交功能请求。
- **种子作为一等公民。** Prisma Next 没有提供 `prisma db seed` 等价物。解决方法：编写一个 TypeScript 脚本，导入你的 `db` 实例并运行你的设置查询；从 `package.json` 的脚本中调用它。如果你需要一等种子功能，请通过 `prisma-next-feedback` 技能提交功能请求。
- **迁移合并。** Prisma Next 不会将旧迁移合并到基线。它们会累积；对于非常大的历史记录，手动基线和截断是路径。如果你需要内置合并，请通过 `prisma-next-feedback` 技能提交功能请求。
- **合约内重命名提示。** 规划器无法检测字段重命名是重命名而不是删除+添加。解决方法：手动编辑 `migration.ts` 以通过 `rawSql(...)` 发出 `RENAME COLUMN`，或使用两个迁移的保留/回填/删除模式。如果你需要合约级别的重命名提示，请通过 `prisma-next-feedback` 技能提交功能请求。

## 图和历史命令

在规划或应用后，你可以离线检查迁移图：

- `pnpm prisma-next migration list` — 列出所有磁盘上的迁移，渲染为图树。支持 `--legend`（打印符号键）、`--ascii`（管道安全符号）和 `--json`。
- `pnpm prisma-next migration log --db $DATABASE_URL` — 已应用迁移的平面时间表，从实时数据库读取。支持 `--ascii` 和 `--json`。

对于完整的图拓扑：`pnpm prisma-next migration graph`（也支持 `--legend`、`--ascii`、`--dot`、`--json`）。

## `@@control` 和 DDL 范围

`@@control` 策略排除 Prisma Next 的管理表面的对象会被省略出规划的 DDL。有四种策略：`managed`（Prisma 规划和应用 DDL）、`tolerated`（对象可能存在，不发出 DDL）、`external`（对象预期存在，不发出 DDL）、`observed`（Prisma 读取但从不写入）。在模式中声明 `@@control(managed|tolerated|external|observed)`；参见 `prisma-next-contract` 和 [`packages/2-sql/2-authoring/contract-psl/README.md`](../../packages/2-sql/2-authoring/contract-psl/README.md) 了解编写语法。

## 远程监控

CLI 默认收集匿名使用数据。要退出，请在环境中设置 `PRISMA_NEXT_DISABLE_TELEMETRY=1` 或 `DO_NOT_TRACK=1`。参见 [`docs/Telemetry.md`](../../docs/Telemetry.md) 了解完整的退出参考。

## 检查清单

- [ ] 合约已发出（`contract.json` + `contract.d.ts` 当前）。
- [ ] 选择正确的路径：`db update`（本地开发）vs `migration plan` + `migrate`（任何共享内容）。
- [ ] 对于 `migration plan`：在 `migrate` 之前运行 `migration show` 进行审查。
- [ ] 填写了 `migration.ts` 中的所有 `placeholder(...)`（如果有），基于 `endContract` 构建。
- [ ] `check` 闭包是行集查询，不是标量聚合。
- [ ] 编辑 TS 后自我发出（`node migrations/app/<dir>/migration.ts`）。
- [ ] 运行 `migrate`（或 `db update`）并看到它完成。
- [ ] 仅在诊断漂移时使用 `db verify`——不作为常规的后续步骤。
- [ ] 未对共享或生产数据库使用 `db update`。
- [ ] 未直接编辑 `ops.json`。
- [ ] 未在未检查 `meta.destructiveOperations[]` 的情况下跳过破坏性操作提示。
