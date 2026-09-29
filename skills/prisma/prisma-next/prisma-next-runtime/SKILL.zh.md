---
name: prisma-next-runtime
description: 配置 Prisma Next 运行时——使用 `@prisma-next/postgres/runtime` 中的 `postgres<Contract>(...)`、`@prisma-next/sqlite/runtime` 中的 `sqlite<Contract>(...)` 或 `@prisma-next/mongo/runtime` 中的 `mongo<Contract>(...)` 来设置 `db.ts`；中间件组合（来自 `@prisma-next/middleware-telemetry` 的遥测数据；检查和预算），`DATABASE_URL` 配置，按环境分支，在 Postgres、SQLite 和 Mongo 界面之间切换。用于 `db.ts`、`postgres()`、`sqlite()`、`mongo()`、中间件、遥测数据、检查、预算、`DATABASE_URL`、`.env`、连接池、`poolOptions`、开发与生产配置、事务、`db.transaction`、读副本、多数据库、脚本无法退出、卡顿、关闭连接、`db.end`、`db.close`、`pool.end`、`[Symbol.asyncDispose]`、`await using`。
---

# Prisma Next — 运行时 (`db.ts` 连接)

> **编辑你的数据合约。Prisma 处理其余部分。**

本技巧涵盖了**运行时入口点**——`db.ts**——以及如何将数据库客户端与扩展、中间件和环境配置组合在一起。

## 何时使用

- 用户首次连接 `db.ts`（初始化后）。
- 用户想要添加中间件（遥测、警告、预算、自定义）。
- 用户想要按环境配置（开发与生产、多区域）。
- 用户想要在 Postgres、SQLite 和 Mongo 界面之间切换。
- 用户想要将操作包装在 `db.transaction(...)` 中（Postgres 和 SQLite）。
- 用户正在运行一次性脚本（`tsx my-script.ts`、Node CLI、CI 任务），进程在查询完成后不会退出，或者需要脚本清理（`db.close()`、`await using`）。
- 用户提到：*db.ts、postgres()、mongo()、中间件、遥测、警告、预算、DATABASE_URL、.env、连接池、poolOptions、开发与生产、事务、只读副本、多数据库、脚本不会退出、挂起、db.close、db.end、关闭连接、pool.end、await using*。

## 何时不使用

- 用户想要编写查询 → `prisma-next-queries`。
- 用户使用 Supabase — `supabase()` 角色优先工厂，`asUser(jwt)` / `asAnon()` / `asServiceRole()`，JWT 配置，RLS → `prisma-next-supabase`。
- 用户想要编辑合约 → `prisma-next-contract`。
- 用户想要将 Prisma Next 连接到构建工具（Vite 插件、Next.js、…）→ `prisma-next-build`。
- 用户想要调试连接/运行时错误 → `prisma-next-debug`。
- 用户想要提交 Bug 或功能请求 → `prisma-next-feedback`。

## 关键概念

- **`db.ts` 是运行时入口点。** 从 `@prisma-next/<target>` 界面（`@prisma-next/postgres/runtime`、`@prisma-next/sqlite/runtime` 或 `@prisma-next/mongo/runtime`）导入运行时工厂，合约工件（`contract.json` + 来自 `contract.d.ts` 的 `Contract` 类型），以及任何中间件。导出一个 `db` 值供应用程序其余部分导入。
- **界面运行时工厂是用户自定义 `db.ts` 仅导入的表面。** 每个工厂都是 *默认* 导出。对于 Postgres：`import postgres from '@prisma-next/postgres/runtime'`；SQLite：`import sqlite from '@prisma-next/sqlite/runtime'`；Mongo：`import mongo from '@prisma-next/mongo/runtime'`。工厂签名是 `<Target><Contract>(options)` — 一个类型参数（来自 `contract.d.ts` 的 `Contract` 类型），和一个选项对象。
- **懒连接。** 工厂不会同步连接到数据库。静态查询表面（`db.sql`、`db.orm`）立即可用；驱动程序/池在首次需要运行时实例化（或在显式调用 `await db.connect({ url })` 时）。这就是为什么 `db.ts` 可以在环境准备就绪之前导入到模块中。
- **中间件按顺序组合。** `middleware: [...]` 数组中的第一个中间件运行 *最外层* — 它在操作进入时首先看到，在退出时最后看到。遥测首先意味着预算/警告失败会显示在遥测跨度内。
- **`prisma-next.config.ts` vs `.env`。** 配置（`defineConfig({ contract, db, extensions, migrations })`）用于静态项目结构：合约路径、安装的扩展、迁移目录、默认连接字符串。`.env` 用于按环境值（`DATABASE_URL`、密钥）。配置自动通过 `dotenv/config` 读取 `.env`。在配置文件中硬编码 `DATABASE_URL` 会导致凭证泄露并绕过按环境覆盖。
- **构建系统/开发服务器集成是单独的技巧。** `vite dev` 自动发射在 `prisma-next-build` 中。运行时侧（本技巧）无论合约文件/合约.d.ts 如何出现在磁盘上，都会读取它们，因此这两个技巧可以干净地组合。

## 工作流 — 基本的 `db.ts`

概念：`db.ts` 是发出合约工件（目标形状）和执行查询的运行时的接口之间的接口。三个导入是承重的——运行时工厂、`Contract` 类型（以便静态查询表面被类型化），以及 JSON 工件（以便运行时在构造时验证结构）。

`init` 框架了类似的东西（对于 `--target postgres`）：

```typescript
// src/prisma/db.ts
import postgres from '@prisma-next/postgres/runtime';
import type { Contract } from './contract.d';
import contractJson from './contract.json' with { type: 'json' };

export const db = postgres<Contract>({
  contractJson,
  url: process.env['DATABASE_URL'],
});
```

(`init` 目前在 `prisma/db.ts` 中框架——见 `prisma-next-quickstart` 中的 TML-2532。规范路径是 `src/prisma/db.ts`；其余 `src/` 从 `./prisma/db` 或 `../prisma/db` 导入，具体取决于深度。）

需要了解的三件事：

- **`<Contract>` 类型参数是承重的。** 没有它，静态表面会折叠成通用形状，并且您会失去模型名称的自动完成。始终从发出的 `./contract.d.ts` 导入 `Contract`。
- **`with { type: 'json' }` 是必需的。** Node 的 ESM JSON 导入属性规范。没有它，导入会出错。
- **`url` 在构造时是可选的。** 如果在 `db.ts` 加载时未设置 `DATABASE_URL`，工厂仍然会返回客户端；您可以稍后调用 `await db.connect({ url })`。工厂懒惰地抛出错误——只有在实际需要运行时时才会抛出。

Mongo 界面具有相同的构造形状——`import mongo from '@prisma-next/mongo/runtime'`——以及相同的 `db.connect(...)` / `db.close()` 生命周期方法。**Mongo 界面不暴露 `db.transaction(...)`。** 见 *Prisma Next 尚未实现的功能* 获取解决方案。**ORM 表面在一点上有所不同：键。** 在 Mongo 中，`db.orm` 按集合的存储名称键（来自 `@@map(...)`，或如果没有 `@@map` 则按小写的模型名称），而不是按 PSL 模型名称——所以 `model User { … @@map("users") }` 在 `db.orm.users` 中访问，而不是 `db.orm.User`。SQL 构建车道（`db.sql.<table>`）在 Mongo 中根本不存在（`db.sql` 是 `undefined`）。见 `prisma-next-queries` § *MongoDB ORM 地址* 获取完整规则和 SQL 目标示例的重写配方。

## 工作流 — 作为脚本运行（清理）

概念：短脚本连接、查询，然后期望进程退出会在 Postgres 上**挂起**，因为界面拥有的 `pg.Pool` 会保持 Node 的事件循环活跃。数据往返成功；脚本永远不会退出。在脚本返回之前调用 `await db.close()`（或使用 `await using` **在脚本模块顶部**，以便在模块退出时运行清理——见下面的块作用域警告，了解为什么这很重要）。

**基本形状**——从 `db.ts` 导出 `db`，在脚本中导入它，在末尾关闭：

```typescript
// src/scripts/hello.ts
import { db } from '../prisma/db';

const created = await db.orm.User.create({ email: 'alice@example.com', name: 'Alice' });
const read = await db.orm.User.first();
console.log({ created, read });

await db.close();
```

**TS 5.2+ 习语形状**——在脚本模块顶部构造客户端，并让 `[Symbol.asyncDispose]` 在模块退出时调用 `close()`：

```typescript
// src/scripts/hello.ts — 脚本模块中的顶层 await
import postgres from '@prisma-next/postgres/runtime';
import type { Contract } from '../prisma/contract.d';
import contractJson from '../prisma/contract.json' with { type: 'json' };

await using db = postgres<Contract>({ contractJson, url: process.env.DATABASE_URL! });

const user = await db.orm.User.first();
console.log(user);
// db.close() 在脚本模块退出时自动运行。
```

### `await using` 是 **块作用域**——不要将其放在请求处理程序内

这是本节最重要的规则。`await using db = postgres(...)` 在*外围块*退出时释放。在脚本模块中，该块是模块正文，清理在进程退出时触发——可以。在请求处理程序中，外围块是处理程序函数，因此清理在**每个请求之后**触发——每次调用都有一个新鲜的 `pg.Pool`，TCP 连接风暴，热循环上下拆分连接。

```typescript
// 不要这样做——每次请求后关闭连接池。
app.get('/users', async (req, res) => {
  await using db = postgres<Contract>({ contractJson, url: process.env.DATABASE_URL! });
  const users = await db.orm.User.all();
  res.json(users);
});
```

正确的服务器模式是在 `db.ts` 中使用**模块级单例**，由处理程序导入，在进程生命周期内永远不会关闭：

```typescript
// src/prisma/db.ts — 一次构造，持续整个进程
export const db = postgres<Contract>({ contractJson, url: process.env.DATABASE_URL });

// src/routes/users.ts
import { db } from '../prisma/db';

app.get('/users', async (req, res) => {
  const users = await db.orm.User.all();
  res.json(users);
});
```

服务器（HTTP 处理程序、请求循环中的工作程序）在稳定状态下**根本不调用 `db.close()`**。池保持打开状态以供进程使用。`db.close()` 和 `await using` 是用于短生命周期脚本——`tsx my-script.ts`、Node CLI 命令、CI 任务、一次性种子运行——而不是在请求循环内运行的代码。

**语义：**

- **`close()` 是幂等的。** 调用它两次是无操作的。
- **`close()` 是终止的。** 关闭 `db` 后不会重新连接——如果需要另一个连接，请构造一个新的客户端。关闭后，`db.runtime()`、`db.connect(...)`、`db.transaction(...)` 和 `db.prepare(...)` 会以 `Error('<target> 客户端已关闭')`（例如 `'Postgres 客户端已关闭'`、`'SQLite 客户端已关闭'`、`'Mongo 客户端已关闭'`）拒绝。
- **`close()` 不会中止正在进行的查询。** 在调用 `close()` 之前 `await` 未完成的任务。`db.runtime().execute(plan)` 的异步迭代器和 `close()` 后持有的 `PreparedStatement` 处理程序在下次调用时失败。
- **所有权。** `close()` 仅释放界面构造的内容（来自 `{ url }` 的 `pg.Pool`，来自 `{ url }` / `{ uri, dbName }` 的 `mongodb.MongoClient`，来自 `{ path }` 的 SQLite 手柄）。如果您提供了自己的 `pg.Pool` / `pg.Client`（Postgres `pg:` 选项）、`mongodb.MongoClient`（Mongo `mongoClient:` 选项）或预构建的 `binding`，`db.close()` 不会**接触这些**——您拥有它们的生命周期。

**`db.end()` 不存在。** 通用 `node-postgres` 名称是 `pool.end()` 在 `pg.Pool` 上；Prisma Next 运行时客户端不是 `pg.Pool`。正确的调用是 `await db.close()`。

## 工作流 — 遥测中间件

概念：遥测中间件看到每个操作，并为每个操作（开始、成功、错误）发出一个结构化事件。将事件与您的可观察性堆栈的收集器配对。

```typescript
import postgres from '@prisma-next/postgres/runtime';
import { createTelemetryMiddleware } from '@prisma-next/middleware-telemetry';
import type { Contract } from './contract.d';
import contractJson from './contract.json' with { type: 'json' };

export const db = postgres<Contract>({
  contractJson,
  url: process.env['DATABASE_URL'],
  middleware: [
    createTelemetryMiddleware({
      onEvent: (event) => {
        // 转发到您的收集器、记录等。
      },
    }),
  ],
});
```

`createTelemetryMiddleware` 作为单独的用户可安装包（`@prisma-next/middleware-telemetry`）提供，而不是作为 postgres 界面的 `/middleware` 子路径。直接安装它。运行 `pnpm ls @prisma-next/middleware-telemetry` 以确认它在锁定文件中。

## 工作流 — 警告和预算中间件

概念：警告捕获在类型检查后幸存的编写错误（例如没有 `WHERE` 的 `DELETE`，没有 `LIMIT` 的大型表上的 `SELECT`）；预算在运行时强制行数和延迟上限。两者都通过结构化错误信封显示结果，以便代理可以基于代码分支。

这些包含在底层 SQL 运行时包（`@prisma-next/sql-runtime`）中，并且目前尚未从 postgres 界面重新导出——见 *Prisma Next 尚未实现的功能*。`examples/prisma-next-demo/src/prisma/db.ts` 下的示例应用程序展示了规范导入。

```typescript
import postgres from '@prisma-next/postgres/runtime';
import { budgets, lints } from '@prisma-next/sql-runtime';
import type { Contract } from './contract.d';
import contractJson from './contract.json' with { type: 'json' };

export const db = postgres<Contract>({
  contractJson,
  url: process.env['DATABASE_URL'],
  middleware: [
    lints({
      severities: {
        selectStar: 'warn',
        noLimit: 'error',
        deleteWithoutWhere: 'error',
        updateWithoutWhere: 'error',
        readOnlyMutation: 'error',
      },
    }),
    budgets({
      maxRows: 10_000,
      defaultTableRows: 10_000,
      tableRows: { user: 10_000, post: 50_000 },
      maxLatencyMs: 1_000,
      severities: { rowCount: 'error', latency: 'warn' },
    }),
  ],
});
```

完整选项表面，请查看源代码：`packages/2-sql/5-runtime/src/middleware/lints.ts` 和 `.../budgets.ts`。`severities` 键（`selectStar`、`noLimit`、`deleteWithoutWhere`、`updateWithoutWhere`、`readOnlyMutation` 对于警告；`rowCount`、`latency` 对于预算）是权威来源；不要推测一个 `grep` 找不到的键。

## 工作流 — 组合多个中间件

```typescript
middleware: [
  createTelemetryMiddleware({ onEvent }),  // 最外层——看到所有子失败作为内部错误
  lints({ severities: { noLimit: 'error' } }),
  budgets({ maxLatencyMs: 5_000 }),         // 最内层——最接近驱动程序运行
],
```

顺序很重要：外层包装。遥测首先意味着预算/警告失败会作为跨度捕获（代理可以将警告代码与同一跟踪中的操作相关联）。

## 工作流 — 配置连接

概念：运行时采用三种绑定形状之一——`url`、`pg`（预构造的 `pg.Pool` 或 `pg.Client`），或 `binding`（显式的类型标签）。它们是互斥的。`pg` 形式用于已经管理自己的池的项目（例如 Lambda 层）；`url` 是默认值。池调优是 `poolOptions.connectionTimeoutMillis` / `poolOptions.idleTimeoutMillis` —— *不是* `driverOptions`。

```typescript
// 默认——URL 字符串，工厂构造池。
postgres<Contract>({
  contractJson,
  url: process.env['DATABASE_URL'],
  poolOptions: {
    connectionTimeoutMillis: 20_000,
    idleTimeoutMillis: 30_000,
  },
});

// BYO pool — 传递您已经创建的 pg.Pool。
import { Pool } from 'pg';
const pool = new Pool({ connectionString: process.env['DATABASE_URL'] });
postgres<Contract>({ contractJson, pg: pool });
```

`url` 和 `pg` 键在类型级别是互斥的；传递两者会出错。

`DATABASE_URL` 存在 `.env` 中。CLI 为发射/验证/迁移命令读取它；运行时在 `db.ts` 加载时通过 `process.env` 读取它。

## 工作流 — 按环境配置（开发与生产）

概念：每个环境一个 `DATABASE_URL`；`db.ts` 的其余形状相同。对于中间件分歧（例如仅在开发中严格警告），在 `db.ts` 中根据 `process.env['NODE_ENV']` 分支。

```typescript
const isProd = process.env['NODE_ENV'] === 'production';

export const db = postgres<Contract>({
  contractJson,
  url: process.env['DATABASE_URL'],
  middleware: isProd
    ? [createTelemetryMiddleware({ onEvent })]
    : [
        createTelemetryMiddleware({ onEvent }),
        lints({ severities: { noLimit: 'error', deleteWithoutWhere: 'error' } }),
      ],
});
```

`.env` 用于本地；部署平台的密钥用于生产。永远不要提交 `.env`。

## 工作流 — 事务

概念适用于 **Postgres 和 SQLite**。`db.transaction(fn)` 打开一个事务，将回调传递给具有与 `db` 相同的 `sql` / `orm` 表面的 `tx` 上下文，并在成功返回时提交/在任何抛出错误时回滚。在回调内，使用 `tx.sql` 和 `tx.orm` 而不是 `db.sql` / `db.orm`，以便写入在事务中运行。Mongo 界面不暴露 `db.transaction(...)`。

```typescript
await db.transaction(async (tx) => {
  const user = await tx.orm.User.create({ email: 'alice@example.com' });
  await tx.orm.Post.create({ userId: user.id, title: 'hello' });
  // 如果其中任何一个调用抛出异常，两个插入操作都会回滚。
});
```

回调函数会返回它返回的内容 — 事务包装器会将其传递。`tx` 对象为事务内的 SQL-builder 计划暴露了 `execute(plan)`。

## 工作流程 — 在 Postgres、SQLite 和 Mongo 之间切换

概念：前端选择被嵌入到 `db.ts` (`@prisma-next/postgres`、`@prisma-next/sqlite` 或 `@prisma-next/mongo`) 和 `prisma-next.config.ts`（你从其中导入的 `defineConfig`）。要切换项目的目标，请在同一目录中重新运行 `prisma-next init` 并选择其他目标 — 初始化流程会检测现有的脚手架并提示重新初始化（`--force` 会跳过提示）。PN 会为新的前端重新生成 `prisma-next.config.ts` 和 `db.ts`。合同源需要为新的目标 idioms 重新编写（Mongo 表达嵌套文档；Postgres/SQLite 表达关系）。

切换后（Mongo）：

```typescript
// src/prisma/db.ts (Mongo)
import mongo from '@prisma-next/mongo/runtime';
import type { Contract } from './contract.d';
import contractJson from './contract.json' with { type: 'json' };

export const db = mongo<Contract>({ contractJson, url: process.env['DATABASE_URL'] });
```

SQLite：

```typescript
// src/prisma/db.ts (SQLite)
import sqlite from '@prisma-next/sqlite/runtime';
import type { Contract } from './contract.d';
import contractJson from './contract.json' with { type: 'json' };

export const db = sqlite<Contract>({ contractJson, path: 'app.db' });
```

`path` 在构造时是可选的（你可以稍后调用 `db.connect({ path })`）；省略它，前端仍然会返回一个客户端。SQLite 前端暴露了与 Postgres 相同的 `db.sql`、`db.orm`、`db.transaction(...)`、`db.close()` 和 `[Symbol.asyncDispose]` 接口。Mongo 前端共享 `db.orm`、`db.close()` 和 `[Symbol.asyncDispose]`，但没有 `db.sql` 和 `db.transaction(...)`。

`db.sql` / `db.orm` 接口在名称上保持不变；每个接口暴露的操作都是目标形状的（Mongo 没有 `JOIN`）。

## 工作流程 — 构建系统 / 开发服务器集成

如果你希望在开发服务器运行时自动重新发出合同工件（而不是每次合同源更改时手动运行 `prisma-next contract emit`），请使用 `prisma-next-build` 中的构建工具插件：

- **Vite**：安装 `@prisma-next/vite-plugin-contract-emit` 并在 `vite.config.ts` 中注册 `prismaVitePlugin('prisma-next.config.ts')`。
- **Next.js、Webpack、esbuild、Rollup、Turbopack**：目前还没有第一方插件 — 解决方案是一个 `prebuild` 脚本，它运行 `prisma-next contract emit`。请参阅 `prisma-next-build` 获取详细步骤。

运行时方面（这项技能）是相同的：`db.ts` 从磁盘读取 `contract.json` + `contract.d.ts`。构建系统插件的职责是在开发过程中保持这些文件是最新的。

## 常见陷阱

1. **在 `prisma-next.config.ts` 中硬编码 `DATABASE_URL`。** 泄露凭证；绕过每个环境的覆盖。使用 `.env`。
2. **在 `postgres<Contract>(...)` 中省略 `<Contract>` 类型参数**。没有它，静态接口会折叠成通用形状，并且你会失去模型的自动完成。没有第二个类型参数 — 旧的二参数签名 (`postgres<Contract, TypeMaps>`) 已被移除。
3. **忘记在合同导入上使用 `with { type: 'json' }`。** Node 的 ESM JSON 导入属性规范要求。
4. **中间件顺序很重要。** 最外层的包裹。如果你希望它捕获内部中间件的错误，请首先放置遥测。
5. **从不存在的前端子路径导入中间件。** `@prisma-next/postgres/middleware` 不存在。遥测来自 `@prisma-next/middleware-telemetry`；今天的警告/预算来自 `@prisma-next/sql-runtime`（见 *Prisma Next 还未实现的功能*）。
6. **编造警告/预算选项名称。** 警告使用 `severities`（上述五个键），而不是 `requireWhere` / `maxRowsWithoutLimit`。预算使用 `maxLatencyMs`（不是 `maxDurationMs`）加上 `maxRows` / `defaultTableRows` / `tableRows`。如有疑问，请查看源代码。
7. **切换目标而不重新发出。** 合同工件是目标形状的；在目标更改后发出。
8. **Postgres 查询完成后脚本挂起。** `pg.Pool` 保持 Node 的事件循环活跃。解决方案：在脚本返回之前 `await db.close()`，或在脚本模块顶部使用 `await using db = postgres<Contract>(...)`。不要在请求处理程序内部放置 `await using db = postgres(...)` — 它是块作用域的，并且会在每个请求后关闭连接池。正确的服务器模式是在 `db.ts` 中使用模块级单例，它在整个进程生命周期中存在。

## Prisma Next 还未实现的功能

- **`@prisma-next/postgres/middleware` 子路径。** Postgres 前端重新导出了运行时工厂 (`./runtime`)、配置 (`./config`)、合同构建器 (`./contract-builder`)、控制 (`./control`)、家族 (`./family`)、目标 (`./target`) 和无服务器 (`./serverless`) — 但不包括中间件。今天的解决方案：从 `@prisma-next/sql-runtime` 导入 `lints` 和 `budgets`，从 `@prisma-next/middleware-telemetry` 导入 `createTelemetryMiddleware`。通过 `prisma-next-feedback` 提交你遇到的额外空白。
- **多数据库路由/读取副本。** Prisma Next 没有内置的主/副本路由器或分片感知客户端。解决方案：为每个数据存储配置单独的 `db.ts` 实例，并在应用程序代码中调用正确的实例。如果你需要第一类的多数据库路由，请通过 `prisma-next-feedback` 提交功能请求。
- **连接池作为第一类配置字段。** `poolOptions.connectionTimeoutMillis` 和 `poolOptions.idleTimeoutMillis` 已连接，但 `pg.Pool` 的其余调谐表面（最大连接数、`allowExitOnIdle`、ssl 选项等）没有被命名暴露。解决方案：自己构造 `pg.Pool` 并通过 `pg:` 传递。如果你需要更多池字段在前端暴露，请通过 `prisma-next-feedback` 提交功能请求。
- **查询日志中间件作为内置。** Prisma Next 没有内置的“记录每个查询”中间件。解决方案：编写一个小型自定义中间件，它包装每个操作并记录；或使用 `createTelemetryMiddleware` 并在 `onEvent` 回调中记录。如果你需要一个内置的查询日志，请通过 `prisma-next-feedback` 提交功能请求。

## 参考文件

这项技能有意只包含正文；`prisma-next init --help`、`packages/3-extensions/postgres/src/config/define-config.ts` 中的 `defineConfig` 工厂、`packages/3-extensions/postgres/src/runtime/postgres.ts` 中的 `postgres()` 工厂，以及 `packages/2-sql/5-runtime/src/middleware/{lints,budgets}.ts` 中的中间件源是选项级详细信息的权威表面。如有疑问，请查看源代码。

## 检查清单

- [ ] `db.ts` 从 `@prisma-next/<target>/runtime` (`postgres`、`sqlite` 或 `mongo`) 导入运行时工厂，并从 `./contract.d` 导入 `<Contract>` 类型。
- [ ] 合同 JSON 导入上使用 `with { type: 'json' }`。
- [ ] `<Contract>` 是 `postgres<Contract>(...)` 的唯一类型参数（没有第二个参数）。
- [ ] `DATABASE_URL` 存在于 `.env` 中，而不是在 `prisma-next.config.ts` 中。
- [ ] 中间件顺序有意设置（通常遥测在最外层）。
- [ ] `lints` / `budgets` 使用验证的选项键 (`severities`、`maxLatencyMs`、`maxRows`、`tableRows`)。
- [ ] 每个环境的差异（如果有）由 `NODE_ENV` 或类似条件控制。
- [ ] 没有在提交的任何文件中硬编码凭证。
- [ ] 没有编造 `@prisma-next/postgres/middleware` 子路径、`@prisma-next/postgres-extension-audit` 包或 `postgres<...>` 的第二个类型参数。
- [ ] 没有声称 Mongo 前端存在 `db.transaction(...)` — 只有 Postgres 和 SQLite 暴露它。
- [ ] 没有编造读取副本/多数据库/额外池配置 — 指向 *Prisma Next 还未实现的功能* 并路由到 `prisma-next-feedback`。
- [ ] 构建系统/开发服务器提示（Vite 插件、Next.js 插件等）路由到 `prisma-next-build`。
