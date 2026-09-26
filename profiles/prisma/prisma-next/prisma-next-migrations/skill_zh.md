# Prisma Next — 迁移编写

> **编辑你的数据合约。Prisma Next 规划迁移。你需要填充任何数据转换。**

三步用户模型：

1. **你编辑你的数据合约。** (`prisma-next-contract`)
2. **Prisma Next 为你规划迁移。** ← 这个功能
3. **如果需要数据转换，你编辑 `migration.ts` 并自行触发。** ← 这个功能

一旦合约发生变化，你选择如何将更改应用到数据库。这个功能涵盖了两种路径（`db update` 和 `migration plan` + `migrate`）、迁移包合约、`migration.ts` 编写 API 以及你无需离开循环即可恢复的失败模式。

**目标。** 迁移编写对于 **Postgres** 和 **Mongo** 都是首选功能。CLI 从 `prisma-next.config.ts`（在 `prisma-next init --target …` 设置期间）读取目标。迁移命令不接受 `--target` 标志 — 使用针对所需目标的配置。以下示例调用会指出目标特定的导入、标记、工厂和事务行为，如果它们存在差异。

## 使用场景

- 用户编辑了合约并希望将更改应用到数据库。
- 用户希望编写包含数据转换的迁移。
- 用户希望针对本地数据库运行挂起的迁移。
- 用户遇到 `MIGRATION.HASH_MISMATCH`、`PN-MIG-2001`（未填充的占位符）或部分应用的迁移。
- 用户提到：*migrate, migration, db push, db update, `prisma migrate dev`, `prisma migrate deploy`, drift, hash mismatch, data backfill*。

## 不使用场景

- 用户想知道在部署/合并时 *将运行哪些迁移*，或者想要管理引用和不变量 → `prisma-next-migration-review`。
- 用户想要编辑合约 → `prisma-next-contract`。
- 用户想要深入了解单个结构化错误包 → `prisma-next-debug`。

## 关键概念

- **`db update` (快速路径)。** 读取发出的合约，与实时数据库进行比较，应用更改。可选 `--dry-run` 在不执行的情况下打印计划。交互式破坏性操作确认（或 `-y` 自动接受）。**不写入迁移目录。** 需要数据转换的操作不由此路径处理 — `db update` 排除了 `data` 操作类，并在需要数据转换的地方短路。仅针对没有与其他任何人共享历史的数据库（你的本地开发数据库）使用。

- **`migration plan` (正式路径)。** 读取发出的合约，与磁盘迁移图的头进行比较，在 `migrations/app/<YYYYMMDDTHHMM>_<snake_slug>/` 下写入新的迁移包。如果任何操作需要数据转换，则该包的 `migration.ts` 包含 `placeholder(...)` 调用，你需要填充。

- **迁移路径中的 `app/` 段是消费应用程序的合约空间 ID。** 你编写的每个迁移都位于 `migrations/app/` 下。你的合约依赖的扩展会获得自己的兄弟目录 (`migrations/<extension-space-id>/`) — 这些由扩展包管理，你不会写入它们。第一次运行 `migration plan` / `db init` 针对应用程序级配置时，`app/` 段会自动生成。

- **迁移包文件**（在每个 `migrations/app/<dir>/` 内）:
  - `migration.json` — 元数据（元数据 + `migrationHash`）。
  - `ops.json` — 标准操作列表。内容寻址；`migrationHash` 是基于此计算的。
  - `migration.ts` — TypeScript 编写源，**由框架渲染**（由 `migration plan` 或 `migration new` 渲染）。你编辑特定的孔（见下文 *填充占位符*），然后通过运行它来重新发出 `ops.json` / `migration.json`。

- **合约快照。** `migration.ts` 从共享的、内容寻址的存储 (`migrations/snapshots/<hex>/contract.json` + `contract.d.ts` (`<hex>` 是合约的 64 十六进制存储哈希)）导入其书端合约，而不是从迁移包内的文件导入。

- **自行触发。** 运行 `node migrations/app/<dir>/migration.ts` 重新生成 `ops.json` 和重新计算 `migration.json`（可能经过编辑的 TS 源）。这是更新现有迁移包的唯一支持方式。

- **`migration.ts` 结构。** 框架渲染。一个扩展 `Migration` 类（在 Mongo 上来自 `@prisma-next/family-mongo/migration`，在 Postgres 上通过 `@prisma-next/postgres/migration` 重新导出 — 见下文框架块），具有返回工厂调用值数组的 `operations` 获取器。文件以 `MigrationCLI.run(import.meta.url, M)` 结尾，执行它自行触发。

- **`placeholder(slot)`。** 规划器在渲染的 `migration.ts` 中（从 `@prisma-next/errors/migration` 在 Mongo 上，或在 Postgres 上的 `@prisma-next/postgres/migration` 导入）中，在需要数据转换的地方发出一个哨兵。在触发时调用 `placeholder(...)` 会抛出 `PN-MIG-2001` *未填充的迁移占位符*。用户将 `() => placeholder(...)` 箭头替换为真实的查询计划闭包（Postgres）或填充 `dataTransform({ check, run })` 源（Mongo — 见 *填充占位符*），然后自行触发。

- **`this.dataTransform(endContract, name, { check, run })`。** 数据转换工厂。`check` 是一个返回任何行存在的行集查询，表示“还有工作要做”；`run` 是一个或多个执行回填的突变查询。两者都是懒闭包，返回针对 `endContract` 构建的查询计划。运行器将 `check` 包装为 `EXISTS(...)` 进行预检查，包装为 `NOT EXISTS(...)` 进行后检查，因此相同的闭包断言“有工作”和“工作已完成”。

- **`pendingPlaceholders`。** `migration plan` JSON 结果上的一个布尔字段。`true` 表示包已写入但包含未填充的占位符 — `migrate` 在你编辑 `migration.ts` 并自行触发之前会抛出 `PN-MIG-2001`。

- **`migrationHash`。** 迁移包的内容寻址身份。当 `migration.json` 中的存储哈希与从磁盘文件重新计算的哈希不一致时（几乎总是：有人编辑了 `migration.ts` 而没有自行触发），会触发 `MIGRATION.HASH_MISMATCH`。

- **标记。** 记录“此数据库的合约哈希为 X，空间为 Y”。**Postgres:** `prisma_contract.marker` 表中的一行。**Mongo:** `_prisma_migrations` 集合中的一个文档（按空间键值）。每个成功的迁移都会在空间通过模式验证后向前推进一次。`db sign` 在成功验证模式后（它不会签署实时模式与合约不一致的数据库）从当前合约哈希写入标记。

- **原子性应用。** **Postgres:** 每个迁移都在 `BEGIN ... COMMIT` 内运行；如果失败，Postgres 回滚，标记保持在之前的迁移的 `to` 哈希。**Mongo:** DDL 操作 (`createCollection`, `createIndex`, `collMod`, `setValidation`, …) 没有被多文档事务包装；运行器应用操作，验证实时模式与目标合约，仅在验证通过时推进标记（跨空间可恢复 — 见 MongoDB 家族文档）。普通的 DDL + `dataTransform` 流保持一致；来自失败迁移的部分状态通过 `db verify` / `db schema` 诊断，而不是假设。

- **操作类。** 每个操作声明一个 `operationClass`：`additive`, `widening`, `data` 或 `destructive`。CLI 在计划预览和 JSON 输出中显示这些。没有 `long-running` 类，框架不会发出 `CREATE INDEX CONCURRENTLY` — 操作保持事务性。

## `migration.ts` 由框架渲染，不是手动编写

`migrations/<space-id>/<timestamp>/migration.ts`（对于你自己的应用程序，`<space-id>` 始终为 `app/`）下的文件由框架为你渲染 — `prisma-next migration plan` 在合约更改时写入填充的包，而 `prisma-next migration new` 在你想要直接编写操作时写入空脚手架。你不需要从零开始编写这些文件。你编辑框架留下的特定孔 — 主要替换 `placeholder("<slot>")` 哨兵（Postgres）或填充 `dataTransform({ check, run })` 管道槽（Mongo — 见 *填充占位符*），然后自行触发。

**Postgres** 渲染的导入指向 `@prisma-next/postgres/migration`（或 `@prisma-next/sqlite/migration` 对于 SQLite 项目）。

**Mongo** 渲染的导入使用 `@prisma-next/family-mongo/migration` 获取 `Migration` 基类，使用 `@prisma-next/target-mongo/migration` 获取操作工厂 (`createIndex`, `dataTransform`, …)。`MigrationCLI` 来自 `@prisma-next/cli/migration-cli`。

将渲染的导入行视为在两个目标上由框架管理的：

- 将它们保留在原位。不要将它们重写为不同的 `@prisma-next/<…>` 路径；框架的渲染器是权威形状，你手动做出的任何更改在下次重新渲染包或自行触发时都会被撤销（并且可能会触发 `MIGRATION.HASH_MISMATCH`)。
- 如果你需要额外的工厂符号，**将它们添加到现有的渲染导入行**（Postgres: `@prisma-next/postgres/migration`; Mongo: `@prisma-next/target-mongo/migration`），而不是从不同的 `@prisma-next/...` 子路径引入第二个导入。
- “用户代码仅从 `@prisma-next/<target>` 导入”的约定适用于 *你自己的* 模块（查询、运行时设置、合约编写）。渲染的 `migration.ts` 脚手架是框架的表面，不是你的；该规则适用于该文件。

## 你需要路由的诊断代码

| 代码 | 来源 | 移动 |
|---|---|---|
| `PN-MIG-2001` *未填充的迁移占位符* | 抛出 `placeholder(...)` 在触发时 | 打开 `migration.ts`，将命名的 `placeholder("<slot>")` 调用替换为真实的查询闭包，自行触发。 |
| `PN-MIG-2002` *migration.ts 未找到* | 读取迁移包 | 包是格式错误的。从版本控制中恢复，或者运行 `prisma-next migration new` 获取一个新的。 |
| `PN-MIG-2003` *无效的默认导出* | 加载 `migration.ts` | 文件的默认导出不是一个 `Migration` 子类或工厂函数。从版本控制中恢复规划器发出的脚手架或重新运行 `migration plan` 获取干净的包。 |
| `PN-MIG-2005` *dataTransform 合约不匹配* | 构建数据转换查询计划 | 查询构建器使用与传递给 `this.dataTransform(...)` 的 `endContract` 不同的合约引用。使用模块作用域导入的 `endContract` 进行两者。 |
| `MIGRATION.HASH_MISMATCH` *迁移包损坏* | `migrate`（或读取包的任何其他地方） | `ops.json` / `migration.json` 在未经自行触发的情况下被编辑。运行 `node migrations/app/<dir>/migration.ts` 重新发出，然后重新运行 `migrate`。 |
| `PN-RUN-3002` *哈希不匹配* | `db verify` | 标记与合约哈希不一致 (**Postgres:** `prisma_contract.marker`; **Mongo:** `_prisma_migrations`)。数据库的合约版本与代码认为的版本不一致。要么运行迁移前移，要么 — 如果数据库是正确的，并且标记在手动修复后已过时 — 运行 `db sign`。 |
| `PN-RUN-3001` *数据库未签名* | 需要标记的任何命令 | 数据库还没有标记。运行 `prisma-next db init --db <url>` 基线一个空数据库，或者 `db update --db <url>` 直接应用当前合约。 |

## 决策 — 你选择哪条路径？

| 情况 | 路径 | 原因 |
|---|---|---|
| 本地开发，模式在变化中 | `db update` | 快速、交互式、没有迁移文件。 |
| 与其他开发人员共享的分支 | `migration plan` + `migrate` | 可重放、可审查、内容哈希。 |
| 任何到达生产环境的内容 | `migration plan` + `migrate` | 生产必须运行经过审查、哈希的迁移。 |
| 添加需要回填的列 | `migration plan`（写入 `placeholder`），编辑 `migration.ts`, 自行触发, 然后运行 `migrate` | `db update` 不处理数据转换；正式路径可以。 |
| 从漂移中恢复 (数据库与合约分化) | 在手动修复后运行 `db sign`, 或者如果 PN 可以规划修复 | 取决于哪一方是正确的。见下文 *从漂移中恢复*。 |

## 开发 → 发货过渡 (`db` 引用模式)

示例 — 本地使用 `db update` 迭代，然后发布第一个真实迁移：

```bash
pnpm prisma-next db init --db $DATABASE_URL
pnpm prisma-next contract emit && pnpm prisma-next db update --db $DATABASE_URL
pnpm prisma-next contract emit && pnpm prisma-next migration plan --name add_feature
pnpm prisma-next migrate --db $DATABASE_URL
pnpm prisma-next db verify --db $DATABASE_URL
```

`db` 引用是一个名为 `migrations/app/refs/db.json` 的命名指针 — 它记录了项目开发数据库已提升到的合约哈希 — 离线规划器的替代方案，用于在没有连接计划时指示本地数据库的位置。它命名的合约通过共享内容寻址存储 (`migrations/snapshots/<hex>/contract.json`) 解析，与每个迁移图节点解析的方式相同。

**`db init` / `db update` 写入的内容。** 当针对项目的默认 `--db` URL 运行（没有显式的 `--db` 标志）时，这两个命令隐式地推进 `db` 引用：他们将命令后的合约 IR 写入快照存储，然后写入引用的指针。当你传递 `--db <non-default-url>` 时，除非显式使用 `--advance-ref <name>`，否则会抑制引用推进 — 调整不同数据库与该项目开发状态无关。磁盘布局只是一个指针：

```text
migrations/app/refs/
└── db.json                 # { "hash": "<hex>", "invariants": [] }
```

**第一次运行 `migration plan` 后的开发迭代。** `migration plan` 默认 `--from` 为 `db` 引用。当磁盘迁移图仍然为 **空** 且 `db` 引用指向一个非空的哈希，并且存储中存在条目时，规划器会发出 **两个** 包而不是一个：

1. 基线: `null → from-hash` (将 `from-hash` 引入为图节点)
2. 差异: `from-hash → current_contract`

两者都在一次调用中写入磁盘 — 预期 `git status` 中有两个新的目录。`migrate` 然后找到通过基线路径，并应用差异。这关闭了开发 → 发货陷阱，其中单个包的计划引用了一个尚未成为图节点的哈希，并生成了一个不可撤销的迁移 (`MIGRATION.PATH_UNREACHABLE` 在应用时)。

**忘记标记的陷阱。** 当图 **非空** 时，默认 `db` 引用可能指向 **图尖端之外**（在迭代期间每次 `db update` 都会推进标记，但你从未提交迁移）。下一个隐式默认 `migration plan` 拒绝使用 `MIGRATION.HASH_NOT_IN_GRAPH` 并命名指向图节点的可达引用。

在看到 `MIGRATION.HASH_NOT_IN_GRAPH` 时恢复：

```bash
# 选项 A — 明确从图节点计划
pnpm prisma-next migration plan --from production --name my_change

# 选项 B — 将 `db` 引用重新与图节点哈希对齐，然后使用默认值运行计划
pnpm prisma-next ref set db <graph-node-hash>
pnpm prisma-next migration plan --name my_change
```

如果 `db` 引用本身的指针丢失，并且哈希也不是图节点，则使用 `ref set db <hash>` 创建它，或者使用 `db update --advance-ref db` 推进它。

**运行 `migrate` 后。** `migrate` 不会隐式推进 `db` 引用（生产形状的命令保持显式）。实时标记在运行时推进，而引用可能滞后。使用 `db update`（在数据库已经当前时无操作）或同一调用中的 `migrate --advance-ref db` 刷新。

**何时切换路径。** 在模式在单人开发数据库上处于变化中时使用 `db update`。当更改需要可审查、可重放的迁移时切换到 `migration plan` + `migrate` — 通常在打开 PR 或触摸任何共享环境之前。
`db` 引用桥接了这两种路径：它捕获开发迭代状态到磁盘，以便第一次正式计划知道你停止的地方。

**计划时的图节点规则。** 任何用作 `from` 结点的哈希（显式 `--from`、默认 `db` 引用或引用名称）必须在图变为非空后已经是图中的一个节点。自动基线两个包的发射是例外：它在 **空** 图中，具有非空引用和可用存储条目时才会应用。

**应用时的补充。** `migrate` 在执行 DDL 之前读取实时标记。如果标记哈希不是图节点，命令会拒绝使用 `MIGRATION.MARKER_MISMATCH` — 捕获离线规划器无法看到的漂移。这与 `MIGRATION.MARKER_NOT_IN_HISTORY` 不同，后者在运行器的图遍历过程中稍后触发，标记位于遍历路径之外。见 `prisma-next-migration-review` 以获取完整的诊断目录。

`db` 是一个 **默认引用**，不是保留引用。框架在下一个开发周期中会覆盖它；你可以显式使用 `ref set db <hash>` 并接受后续的 `db update` 在默认 URL 运行时将其替换。

规范细节：[迁移系统 § 通过快照存储解析合约](../../docs/architecture%20docs/subsystems/7.%20Migration%20System.md#contract-resolution-through-the-snapshot-store), [§ `migration plan`](../../docs/architecture%20docs/subsystems/7.%20Migration%20System.md#migration-plan), [§ 恢复功能](../../docs/architecture%20docs/subsystems/7.%20Migration%20System.md#recovery-affordances), [ADR 218 — 具有配对合约快照和通用图节点不变量的引用](../../docs/architecture%20docs/adrs/ADR%20218%20-%20Refs%20with%20paired%20contract%20snapshots%20and%20universal%20graph-node%20invariant.md) (TML-2629, 其配对快照部分被取代 — 见 ADR 的状态说明), 以及 [ADR 240 — 合约快照存储在内容寻址存储中](../../docs/architecture%20docs/adrs/ADR%20240%20-%20Contract%20snapshots%20live%20in%20a%20content-addressed%20store.md).

## 工作流 — `db update` (快速路径)

概念：`db update` 解析目标 (`emitted contract`) 与实时数据库之间的差异并应用差异。使用 `--dry-run` 预览。破坏性操作提示交互式确认（或 `-y` 自动接受）。**不写入迁移目录。** 需要数据转换的操作不由此路径处理 — `db update` 排除了 `data` 操作类，并在需要数据转换的地方短路。仅针对没有与其他任何人共享历史的数据库（你的本地开发数据库）使用。

运行合约编辑后：

```bash
pnpm prisma-next contract emit
# Postgres: --db postgresql://...
# Mongo:    --db mongodb://...  (开发脚手架通常需要 ?replicaSet=rs0)
pnpm prisma-next db update --db $DATABASE_URL --dry-run
pnpm prisma-next db update --db $DATABASE_URL
```

`db update` 已经验证模式并在成功时推进标记 — 在快乐路径上不需要额外的 `db verify`。仅在需要独立诊断时使用 `db verify`。

检查 JSON 输出以驱动下一步操作：

```bash
pnpm prisma-next db update --db $DATABASE_URL --json
```

JSON 包含 `plan.operations[]`，其中包含每个 `operationClass`，以及在应用模式下包含 `execution.operationsExecuted` 和应用后的 `marker.storageHash`。如果命令因破坏性操作失败，错误包的 `meta.destructiveOperations[]` 列出了将如何被删除的内容。

## 工作流 — `migration plan` + `migrate` (正式路径)

概念：`migration plan` 在磁盘上写入新的迁移包。如果规划器需要任何数据转换，则该包是 **挂起的** — `migration.ts` 包含 `placeholder(...)` 调用，直到你填充它们。`migrate` 逐个运行挂起的包，事务性。

计划更改：

```bash
pnpm prisma-next contract emit
pnpm prisma-next migration plan --name <snake_slug>
```

读取结果。JSON 形状公开可查询的信号：

- `dir` — 新包的路径（例如 `migrations/app/20260515T1200_add_user_email/`）。
- `pendingPlaceholders` — `true` 如果 `migration.ts` 仍然包含 `placeholder(...)` 调用。
- `operations[].operationClass` — 用于识别 `destructive` 和 `data` 操作。
- `preview.statements` — 家族无关的文本预览。

检查包：

```bash
pnpm prisma-next migration show
pnpm prisma-next migration show <dirName-or-migrationHash-prefix>
```

`migration show` 显示单个迁移包。要查看将运行的迁移的有序列表（跨所有合约空间）使用 `migrate --show`：

```bash
# 在线: 读取实时数据库标记作为起源。
pnpm prisma-next migrate --show --db $DATABASE_URL

# 离线: 假设路径从任何引用或哈希开始。
pnpm prisma-next migrate --show --from <hash-or-ref> --to <hash-or-ref>
```

`migrate --show` 是只读的，永远不会写入数据库或迁移图。在应用之前使用它以确认执行顺序。

填充任何数据转换（见 *填充占位符*），如果你编辑了 `migration.ts`，则自行触发，然后：

```bash
pnpm prisma-next migrate --db $DATABASE_URL
```

`migrate` 无需提示运行 — 破坏性操作的确认保留在 `db update` 中，而不是这里。在应用之前审查破坏性操作，使用 `migration show` *在* `migrate` 之前。

## 工作流 — 填充占位符

概念：规划器可以检测到需要数据转换，但不能检测它应该做什么。它发出一个类型化的脚手架并停止；你填充转换，然后自行触发。

### Postgres

规划器可以检测到需要数据转换（例如，用默认值回填新的 `NOT NULL` 列），但不能检测它应该做什么。用户用针对 `endContract` 构建的查询计划填充 `check` 和 `run` 闭包。

规划器发出的脚手架看起来像：

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
      setNotNull('public', 'user', 'name'),
    ];
  }
}

MigrationCLI.run(import.meta.url, M);
```

用针对 `endContract` 构建的查询计划替换两个 `placeholder(...)` 调用。`check` 闭包必须返回一个 **行集查询，任何行的存在都表示“还有工作要做”** — 通常 `<table>.select('id').where(<violation>).limit(1)`。标量/聚合形状 (`count(*)`, `bool_and(...)`) 会无声地破坏合同：运行器将 `check` 两次包装为 `EXISTS(...)` 进行预检查，包装为 `NOT EXISTS(...)` 进行后检查，一个始终返回一行查询会使得 `EXISTS` 始终为真，`NOT EXISTS` 始终为假。

构建针对 `endContract` 的查询构建器，以便存储哈希对齐 — 使用不同的合约引用会引发 `PN-MIG-2005`。填充后的形状（渲染的脚手架，将 `placeholder(...)` 调用替换为真实的查询计划闭包；如果你需要额外的工厂，如 `setNotNull`, 添加到现有的 `@prisma-next/postgres/migration` 导入行，而不是引入新的导入路径）。见 `prisma-next-queries` 以获取周围的 `db` 设置：

```typescript
import endContract from '../../snapshots/93f07d1b…c9e1e5a2/contract.json' with { type: 'json' };
import { Migration, MigrationCLI, addColumn, setNotNull } from '@prisma-next/postgres/migration';
import { db } from './db'; // sql({ context: createExecutionContext({ contract: endContract, ... }) }

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

自行触发：

```bash
node migrations/app/20260515T1200_add_user_name/migration.ts
```

自行触发会重新生成 `ops.json` 并重新计算 `migration.json` 中的 `migrationHash`。下一个 `migrate` 将看到一个一致的包。

### Mongo

Mongo `dataTransform` 操作接受 `{ check, run }` 对象，其 `source` / `run` 返回 Mongo 查询计划形状（通常来自 `@prisma-next/mongo-query-ast/execution` 的 `RawAggregateCommand` / `RawUpdateManyCommand`）。规划器可能会在那些源中留下 `placeholder(...)`，直到你填充它们。每个渲染的 `migration.ts` 包括 `describe()` 书签（`from` / `to` 合约哈希）— 上面的 Postgres 示例为简洁起见省略了它们。从 `@prisma-next/target-mongo/migration` 导入工厂：

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
              { $match: { name: { $regex: '[A-Z]' } },
              { $limit: 1 },
            ]),
            meta: { target: 'mongo', storageHash: '…', lane: 'mongo-pipeline', paramDescriptors: [] },
          }),
        run: () => ({
          collection: 'users',
          command: new RawUpdateManyCommand(
            'users',
            { name: { $exists: true } },
            [{ $set: { name: { $toLower: '$name' } }],
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

以相同的方式自行触发（`node migrations/app/<dir>/migration.ts`）。

## 工作流 — 手动编写迁移

概念：相同的 `Migration` 类形状允许你在规划器没有任何可规划内容时直接编写操作。即使在这种情况下，你也不需要从零开始编写文件 — `migration new` 会为你渲染一个空的包，你编辑其中的 `operations` 获取器，然后自行触发。

```bash
pnpm prisma-next migration new --name <snake_slug>
```

添加目标特定工厂名称到框架渲染的导入行（Postgres: `@prisma-next/postgres/migration`; Mongo: `@prisma-next/target-mongo/migration`）。使用 `--help` 和渲染器发出的导入列表进行浏览。

**Postgres** 工厂（代表性集合）：

- 表: `createTable`, `dropTable`。
- 列: `addColumn`, `dropColumn`, `alterColumnType`, `setNotNull`, `dropNotNull`, `setDefault`, `dropDefault`。
- 约束: `addPrimaryKey`, `addForeignKey`, `addUnique`, `dropConstraint`。
- 索引: `createIndex`, `dropIndex`。
- 枚举: `createEnumType`, `addEnumValues`, `renameType`, `dropEnumType`。
- 依赖项: `createSchema`, `createExtension`, `installExtension`。
- 原生转义孔: `rawSql({ id, label, operationClass, target, precheck, execute, postcheck, ... })`。
- 数据转换: `this.dataTransform(endContract, name, { check, run })`（实例方法，不是自由工厂）。

**Mongo** 工厂（来自 `@prisma-next/target-mongo/migration`）：

- 集合: `createCollection`, `dropCollection`, `validatedCollection`, `setValidation`。
- 索引: `createIndex`, `dropIndex`。
- 集合选项: `collMod`。
- 数据转换: `dataTransform(name, { check, run })`（自由工厂；`check`/`run` 使用 Mongo 查询计划形状）。

自行触发（`node migrations/app/<dir>/migration.ts`）后进行每次编辑。

## 工作流 — 检查实时模式

概念：`db schema` 是只读的，永远不会写入文件。默认情况下以树形格式打印实时模式，或使用 `--json` 以 JSON 格式打印。在规划和验证期间使用它。

```bash
pnpm prisma-next db schema --db $DATABASE_URL
pnpm prisma-next db schema --db $DATABASE_URL --json > schema.json
```

没有内置过滤器标志 — 如果只想看到一个表，请将 JSON 通过 `jq`（或你喜欢的 JSON 工具）管道。

## 工作流 — 验证合约与数据库 (诊断)

概念：`db verify` 是一个 **独立的诊断** — 不是 `db update` 或 `migrate` 在快乐路径上的常规步骤（这些命令在成功时已经验证并推进了标记）。当你怀疑漂移或需要证明数据库与合约匹配时使用 `db verify`：

- 在 Prisma Next 外部手动 SQL 或 ad-hoc 编辑。
- 恢复从备份中恢复数据库。
- 如果 `migrate` 失败或部分应用（尤其是在 Mongo 上，DDL 是可重玩的，而不是事务包装的）。
- 当 `PN-RUN-3002` / `PN-RUN-3001` 在运行时或从另一个命令中出现时。

模式：

- 默认 — 完整验证（模式 + 标记）。
- `--marker-only` — 跳过模式验证，仅检查标记。
- `--schema-only` — 跳过标记验证，仅检查模式是否满足合约。
- `--strict` 添加：模式中不存在的元素是错误（默认是“数据库可能有多余的元素”）。

```bash
pnpm prisma-next db verify --db $DATABASE_URL
```

在不匹配的情况下，错误包会命名失败模式 (`PN-RUN-3002` 哈希不匹配, `PN-RUN-3001` 标记丢失, 目标不匹配, 模式问题与结构化路径相关)。

## 工作流 — 重新签署标记

概念：`db sign` 将标记重写为当前合约哈希。在手动修复后使用，此时数据库是真相，标记已过时。`db sign` 在签名之前执行模式验证 — 拒绝签署与合约模式不一致的数据库 — 因此成功的签名始终意味着模式匹配，标记现在正确。

```bash
pnpm prisma-next db sign --db $DATABASE_URL
```

## 工作流 — 从漂移中恢复

概念：漂移意味着 `db verify` 报告实时数据库模式与标记所述的应有状态不匹配。两种有效的操作，选择取决于哪一方是正确的。见下文 *从漂移中恢复*。

**从手动修复后运行 `db sign`**, 或者如果 PN 可以规划修复，则运行 `migration plan`。取决于哪一方是正确的。见下文 *从漂移中恢复*。

## 工作流 — 从部分应用的迁移中恢复

概念：在 **Postgres** 中，每个迁移都在 `BEGIN ... COMMIT` 内运行；如果失败，Postgres 会回滚，标记保持在之前的迁移的 `to` 哈希。**Mongo**：DDL 操作 (`createCollection`, `createIndex`, `collMod`, `setValidation`, …) 没有被多文档事务包装；运行器应用操作，验证实时模式与目标合约，仅在验证通过时推进标记（跨空间可恢复 — 见 MongoDB 家族文档）。普通的 DDL + `dataTransform` 流保持一致；来自失败迁移的部分状态通过 `db verify` / `db schema` 诊断，而不是假设。

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

如果失败是由于外部副作用（在 `run` 闭包中调用其他系统），请手动修复这些系统，然后再重新应用。

## 工作流 — 从 `MIGRATION.HASH_MISMATCH` 中恢复

概念：`migrationHash` 是内容寻址的。不匹配意味着 `migration.json` 中的存储哈希与从磁盘文件重新计算的哈希不一致（几乎总是：有人编辑了 `migration.ts` 而没有自行触发）。补救措施是自行触发有问题的包。

```bash
node migrations/app/<dir>/migration.ts
pnpm prisma-next migrate --db $DATABASE_URL
```

如果自行触发本身失败（例如，合约已经发生变化，操作不再适用于迁移的结束合约），则包已过时。要么从版本控制中恢复它，要么删除它并重新计划 `migration plan`。

## 工作流 — 解决破坏性操作提示 (`db update` 仅限)

概念：当 `db update` 会删除列或表时，它会停止并请求确认。提示是 `db update` 特有的 — `migrate` 不会提示，它会运行迁移包中的任何内容，所以请在 `migrate` 之前审查计划或调用 `migration show`。

当 `db update` 报告破坏性操作交互式地提示时，警告会列出它们。提示是：

> 应用破坏性更改？此操作无法撤销。

路由：

- 如果数据不再需要，则回答是。
- 如果回答否，则要么：
  - 通过 `migration plan` 重新塑造迁移，并手动编辑 `migration.ts` 以保留数据（例如，复制到新列，然后删除），要么
  - 通过重置合约更改来跳过破坏性操作。

在非交互式上下文中（CI、`--no-interactive`、`--json`），破坏性操作的响应作为结构化错误返回 — `meta.destructiveOperations[]` 列出了将被删除的内容。重新运行时使用 `-y` 自动接受，或者单独处理每个操作。

## 常见陷阱

1. **对共享或生产数据库使用 `db update`。** 绝对不要这样做。更改不会留下迁移历史。使用 `migration plan` + `migrate`。
2. **跳过数据转换。** 留下 `migration.ts` 中的 `placeholder(...)` 会使得下一个 `migrate` 抛出 `PN-MIG-2001`。填充每个占位符槽并自行触发。
3. **直接编辑 `ops.json`。** 它是规范 artifact，不是编写源。编辑 `migration.ts`，然后自行触发。
4. **编辑 `migration.ts` 后忘记自行触发。** 下一个 `migrate` 要么使用陈旧的 `ops.json`（如果你只添加了注释），要么在自行触发时失败并引发 `MIGRATION.HASH_MISMATCH`（如果你更改了操作）。始终自行触发。
5. **在成功 `db update` 或 `migrate` 后进行常规 `db verify`。** 在快乐路径上冗余 — 仅在诊断漂移时使用 `db verify`（例如，手动编辑、从备份中恢复数据库、`migrate` 失败或部分应用）。使用 `db verify` 仅当你需要独立诊断时。
6. **Postgres `this.dataTransform` 中的聚合 `check` 闭包。** 返回 `count(*)` 或 `bool_and(...)` 会无声地破坏合同 — 运行器将 `check` 两次包装为 `EXISTS(...)` 进行预检查，包装为 `NOT EXISTS(...)` 进行后检查，一个始终返回一行查询会使得 `EXISTS` 始终为真，`NOT EXISTS` 始终为假。
7. **一个迁移中使用两个合约引用。** 构建查询计划时使用与传递给 `this.dataTransform(endContract, ...)` 的 `endContract` 不同的合约引用会引发 `PN-MIG-2005`。始终使用模块作用域导入的 `endContract` 进行两者。
8. **重命名并期望规划器检测到它是重命名（Postgres）。** Prisma Next 目前没有合约中的重命名提示 — 规划器会发出破坏性删除+添加。手动编辑 `migration.ts` 将破坏性操作重写为 `rawSql({ ... })` 以发出 `ALTER TABLE ... RENAME COLUMN ...`（或者使用保留/回填/删除的两种迁移模式），然后自行触发。见 `prisma-next-contract` § *编辑字段 — 重命名*。
9. **从空白文件手动编写 `migration.ts` 或重写渲染的导入行。** 迁移文件由框架渲染 — 让 `prisma-next migration plan`（或 `migration new`）为你渲染包，然后你只编辑框架留下的特定孔。在 Postgres 中保留渲染的 `@prisma-next/postgres/migration`（或 `@prisma-next/sqlite/migration` 对于 SQLite 项目）导入路径；在 Mongo 中使用 `@prisma-next/family-mongo/migration` + `@prisma-next/target-mongo/migration` 作为渲染的导入。将符号添加到现有的工厂导入行，而不是引入来自不同 `@prisma-next/...` 子路径的第二个导入。
