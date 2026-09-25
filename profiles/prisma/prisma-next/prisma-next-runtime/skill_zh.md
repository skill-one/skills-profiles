# Prisma Next — 运行时 (`db.ts` 配置)

> **编辑你的数据合约。Prisma 将处理其余部分。**

本技巧涵盖了**运行时入口点**——`db.ts**——以及如何将数据库客户端与扩展、中间件和环境配置组合起来。

## 使用场景

- 用户首次配置 `db.ts`（初始化后）。
- 用户想要添加中间件（遥测、校验、预算、自定义）。
- 用户需要按环境配置（开发与生产、多区域）。
- 用户需要在 Postgres、SQLite 和 Mongo 界面之间切换。
- 用户需要使用 `db.transaction(...)`（Postgres 和 SQLite）包装操作。
- 用户正在运行一次性脚本（`tsx my-script.ts`、Node CLI、CI 任务），进程在查询完成后不会退出，或者需要脚本清理（`db.close()`、`await using`）。
- 用户提到：*db.ts、postgres()、mongo()、中间件、遥测、校验、预算、DATABASE_URL、.env、连接池、poolOptions、开发与生产、事务、读副本、多数据库、脚本不会退出、挂起、db.close、db.end、关闭连接、pool.end、await using*。

## 不适用场景

- 用户想要编写查询 → `prisma-next-queries`。
- 用户使用 Supabase —— `supabase()` 角色优先工厂，`asUser(jwt)` / `asAnon()` / `asServiceRole()`，JWT 配置，RLS → `prisma-next-supabase`。
- 用户需要编辑合约 → `prisma-next-contract`。
- 用户需要将 Prisma Next 集成到构建工具（Vite 插件、Next.js、…）→ `prisma-next-build`。
- 用户需要调试连接/运行时错误 → `prisma-next-debug`。
- 用户需要提交 Bug 或功能请求 → `prisma-next-feedback`。

## 关键概念

- **`db.ts` 是运行时入口点。** 导入来自 `@prisma-next/<target>` 界面（`@prisma-next/postgres/runtime`、`@prisma-next/sqlite/runtime` 或 `@prisma-next/mongo/runtime`）的运行时工厂、合约工件（`contract.json` + 来自 `contract.d.ts` 的 `Contract` 类型），以及任何中间件。导出一个 `db` 值供应用程序其余部分导入。
- **界面的运行时工厂是用户自定义 `db.ts` 仅导入的表面。** 每个工厂都是 *默认* 导出。对于 Postgres：`import postgres from '@prisma-next/postgres/runtime'`；SQLite：`import sqlite from '@prisma-next/sqlite/runtime'`；Mongo：`import mongo from '@prisma-next/mongo/runtime'`。工厂签名是 `<Target><Contract>(options)` —— 一个类型参数（来自 `contract.d.ts` 的 `Contract` 类型），和一个选项对象。
- **懒连接。** 工厂不会同步连接到数据库。静态查询表面（`db.sql`、`db.orm`）立即可用；驱动程序/池在第一次需要运行时（或当你显式调用 `await db.connect({ url })`）实例化。这就是为什么 `db.ts` 可以在环境准备就绪之前导入到模块中。
- **中间件按顺序组合。** `middleware: [...]` 数组中的第一个中间件运行 *最外层* —— 它在操作进入时和退出时最先看到操作。遥测首先意味着预算/校验失败会显示在遥测跨度内部。
- **`prisma-next.config.ts` 与 `.env` 的区别。** 配置（`defineConfig({ contract, db, extensions, migrations })`）用于静态项目结构：合约路径、安装的扩展、迁移目录、默认连接字符串。`.env` 用于按环境值（`DATABASE_URL`、密钥）。配置自动通过 `dotenv/config` 读取 `.env`。在配置文件中硬编码 `DATABASE_URL` 会导致凭证泄露并绕过按环境覆盖。
- **构建系统/开发服务器集成是单独的技巧。** `vite dev` 自动发射功能位于 `prisma-next-build` 中。运行时侧（本技巧）无论它们如何出现在磁盘上，都会读取 `contract.json` / `contract.d.ts`，因此这两个技巧可以干净地组合。

## 工作流 — 基本的 `db.ts`

概念：`db.ts` 是已发射合约工件（目标形状）和执行查询的运行时的接口。三个导入是承重的——运行时工厂、`Contract` 类型（以便静态查询表面具有类型），以及 JSON 工件（以便运行时在构造时验证结构）。

`init` 模板了类似以下内容（对于 `--target postgres`）：

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

（目前 `init` 在 `prisma/db.ts` 中模板——参见 `prisma-next-quickstart` 中的 TML-2532。规范路径是 `src/prisma/db.ts`；其余 `src/` 从 `./prisma/db` 或 `../prisma/db` 导入，具体取决于深度。）

需要了解的三件事：

- **`<Contract>` 类型参数是承重的。** 没有它，静态表面会折叠成通用形状，并且你将失去模型名称的自动完成。始终从发射的 `./contract.d.ts` 中导入 `Contract`。
- **`with { type: 'json' }` 是必需的。** Node 的 ESM JSON 导入属性规范。没有它，导入会出错。
- **构造时 `url` 是可选的。** 如果 `DATABASE_URL` 在 `db.ts` 加载时未设置，工厂仍然返回一个客户端；你可以稍后调用 `await db.connect({ url })`。工厂懒惰地抛出异常——只有在实际需要运行时时才会。

Mongo 界面具有相同的构造形状——`import mongo from '@prisma-next/mongo/runtime'`——以及相同的 `db.connect(...)` / `db.close()` 生命周期方法。**Mongo 界面不暴露 `db.transaction(...)`。** 参见 *Prisma Next 尚未实现的功能* 获取解决方案。**ORM 表面在一点上不同：键。** 在 Mongo 上，`db.orm` 按集合的存储名称（来自 `@@map(...)`，或如果没有 `@@map` 则按小写的模型名称）键，而不是按 PSL 模型名称——所以 `model User { … @@map("users") }` 在 `db.orm.users` 中访问，而不是 `db.orm.User`。SQL 构建车道（`db.sql.<table>`）在 Mongo 上根本不存在（`db.sql` 是 `undefined`）。参见 `prisma-next-queries` § *MongoDB ORM 地址* 获取完整规则和 SQL 目标示例的重写配方。

## 工作流 — 作为脚本运行（清理）

概念：短脚本连接、查询，然后期望进程退出会在 Postgres 上**挂起**，因为界面拥有的 `pg.Pool` 保持 Node 的事件循环活跃。数据往返成功；脚本永远不会退出。在脚本返回之前调用 `await db.close()`（或使用 `await using` **在脚本模块顶部**，以便在模块退出时运行清理——参见下面的块作用域警告，了解为什么这很重要）。

**基本形状**——从 `db.ts` 导出 `db`，在脚本中导入它，在末尾关闭：

```typescript
// src/scripts/hello.ts
import { db } from '../prisma/db';

const created = await db.orm.User.create({ email: 'alice@example.com', name: 'Alice' });
const read = await db.orm.User.first();
console.log({ created, read });

await db.close();
```

**TS 5.2+ 习惯用法形状**——在脚本模块顶部构造客户端，并让 `[Symbol.asyncDispose]` 在模块退出时调用 `close()`：

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

这是本节最重要的规则。`await using db = postgres(...)` 在*外围块*退出时进行清理。在脚本模块中，该块是模块正文，清理在进程退出时触发——可以。在请求处理程序中，外围块是处理程序函数，因此清理在**每个请求之后**触发——每次调用都有一个新鲜的 `pg.Pool`，TCP 连接风暴，连接上下波动。

```typescript
// 不要这样做——每次请求后关闭连接池。
app.get('/users', async (req, res) => {
  await using db = postgres<Contract>({ contractJson, url: process.env.DATABASE_URL! });
  const users = await db.orm.User.all();
  res.json(users);
});
```

正确的服务器模式是在 `db.ts` 中使用**模块级单例**，由处理程序导入，在进程生命周期内永不关闭：

```typescript
// src/prisma/db.ts — 一次性构造，持续整个进程
export const db = postgres<Contract>({ contractJson, url: process.env.DATABASE_URL });

// src/routes/users.ts
import { db } from '../prisma/db';

app.get('/users', async (req, res) => {
  const users = await db.orm.User.all();
  res.json(users);
});
```

服务器（HTTP 处理程序、请求循环中的工作者）在稳定状态下**根本不调用 `db.close()`**。池保持进程生命周期内打开。`db.close()` 和 `await using` 用于短生命周期脚本——`tsx my-script.ts`、Node CLI 命令、CI 任务、一次性种子运行——而不是在请求循环内运行的代码。

**语义：**

- **`close()` 是幂等的。** 调用它两次是无操作的。
- **`close()` 是终止的。** 关闭的 `db` 没有重新连接——如果你需要另一个连接，请构造一个新的客户端。关闭后，`db.runtime()`、`db.connect(...)`、`db.transaction(...)` 和 `db.prepare(...)` 会以 `Error('<target> 客户端已关闭')`（例如 `'Postgres 客户端已关闭'`、`'SQLite 客户端已关闭'`、`'Mongo 客户端已关闭'`）拒绝。
- **`close()` 不会中止正在进行的查询。** 在调用 `close()` 之前完成 `await` 中的工作。来自 `db.runtime().execute(plan)` 的异步迭代器和 `close()` 后持有的 `PreparedStatement` 在下次调用时失败。
- **所有权。** `close()` 仅释放界面构造的内容（来自 `{ url }` 的 `pg.Pool`；来自 `{ url }` / `{ uri, dbName }` 的 `mongodb.MongoClient`；来自 `{ path }` 的 SQLite 套接字）。如果你提供了自己的 `pg.Pool` / `pg.Client`（Postgres `pg:` 选项）、`mongodb.MongoClient`（Mongo `mongoClient:` 选项）或预构建的 `binding`，`db.close()` **不会**接触它们——你拥有它们的生命周期。

**`db.end()` 不存在。** 通用 `node-postgres` 名称是 `pg.Pool` 上的 `pool.end()`；Prisma Next 运行时客户端不是 `pg.Pool`。正确的调用是 `await db.close()`。

## 工作流 — 遥测中间件

概念：遥测中间件看到每个操作，并为每个操作（开始、成功、错误）发出一个结构化事件。将事件与你的可观察性堆栈的收集器配对。

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
        // 发送到你的收集器、记录等。
      },
    }),
  ],
});
```

`createTelemetryMiddleware` 作为单独的用户可安装包（`@prisma-next/middleware-telemetry`）提供，而不是作为 postgres 界面的 `/middleware` 子路径。直接安装它。运行 `pnpm ls @prisma-next/middleware-telemetry` 以确认它位于锁定文件中。

## 工作流 — 校验和预算中间件

概念：校验会捕获在类型检查后仍然存在的编写错误（例如没有 `WHERE` 的 `DELETE`、大型表上没有 `LIMIT` 的 `SELECT`）；预算在运行时强制行数和延迟上限。两者都通过结构化错误信封暴露，以便代理可以基于代码分支。

这些包含在底层 SQL 运行时包（`@prisma-next/sql-runtime`）中，并且目前**尚未**从 postgres 界面重新导出——参见 *Prisma Next 尚未实现的功能*。`examples/prisma-next-demo/src/prisma/db.ts` 下的示例应用程序展示了规范导入。

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

完整选项表面，请查看源代码：`packages/2-sql/5-runtime/src/middleware/lints.ts` 和 `.../budgets.ts`。`severities` 键（校验的 `selectStar`、`noLimit`、`deleteWithoutWhere`、`updateWithoutWhere`、`readOnlyMutation`；预算的 `rowCount`、`latency`）是事实依据；不要推断一个 `grep` 找不到的键。

## 工作流 — 组合多个中间件

```typescript
middleware: [
  createTelemetryMiddleware({ onEvent }),  // 最外层——它看到所有子失败作为内部错误
  lints({ severities: { noLimit: 'error' } }),
  budgets({ maxLatencyMs: 5_000 }),         // 最内层——它最接近驱动程序运行
],
```

顺序很重要：外层包装。遥测首先意味着预算/校验失败会被捕获为跨度（代理可以将校验代码与同一跟踪中的操作相关联）。

## 工作流 — 配置连接

概念：运行时采用三种绑定形状之一——`url`、`pg`（预构建的 `pg.Pool` 或 `pg.Client`）、或 `binding`（显式的类型标签）。它们是互斥的。`pg` 形式用于已经管理自己的池的项目（例如 Lambda 层）；`url` 是默认值。池调优是 `poolOptions.connectionTimeoutMillis` / `poolOptions.idleTimeoutMillis` —— *不是* `driverOptions`。

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

// BYO 池——传递你已经创建的 pg.Pool。
import { Pool } from 'pg';
const pool = new Pool({ connectionString: process.env['DATABASE_URL'] });
postgres<Contract>({ contractJson, pg: pool });
```

`url` 和 `pg` 键在类型级别是互斥的；传递两者会出错。

`DATABASE_URL` 位于 `.env` 中。CLI 用于发射/验证/迁移命令读取它；运行时通过 `process.env` 在 `db.ts` 加载时读取它。

## 工作流 — 按环境配置（开发与生产）

概念：每个环境一个 `DATABASE_URL`；`db.ts` 的其余形状相同。对于中间件分歧（例如仅在开发中严格校验），在 `db.ts` 中根据 `process.env['NODE_ENV']` 分支。

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

概念适用于**Postgres 和 SQLite**。`db.transaction(fn)` 打开一个事务，给回调一个具有与 `db` 相同的 `sql` / `orm` 表面的 `tx` 上下文，并在成功返回时提交/在任何抛出错误时回滚。在回调内，使用 `tx.sql` 和 `tx.orm` 而不是 `db.sql` / `db.orm`，以便写入事务。Mongo 界面不暴露 `db.transaction(...)`。

```typescript
await db.transaction(async (tx) => {
  const user = await tx.orm.User.create({ email: 'alice@example.com' });
  await tx.orm.Post.create({ userId: user.id, title: 'hello' });
  // 如果任何调用抛出错误，两个插入都会回滚。
});
```

回调返回你返回的内容——事务包装器会传递它。`tx` 对象在事务内暴露 `execute(plan)`，用于 SQL 构建计划。

## 工作流 — 在 Postgres、SQLite 和 Mongo 之间切换

概念：界面选择嵌入在 `db.ts`（`@prisma-next/postgres`、`@prisma-next/sqlite` 或 `@prisma-next/mongo`）和 `prisma-next.config.ts`（你导入的 `defineConfig`）中。要切换项目的目标，在同一目录中重新运行 `prisma-next init` 并选择其他目标——初始化流程检测现有脚手架并提示重新初始化（`--force` 跳过提示）。PN 重新脚手架 `prisma-next.config.ts` 和 `db.ts` 以适应新的界面。合约源需要为新的目标 idioms 重新编写（Mongo 表达嵌套文档；Postgres/SQLite 表达关系）。

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

`path` 在构造时是可选的（你可以稍后调用 `db.connect({ path })`）；省略它，界面仍然返回一个客户端。SQLite 界面暴露与 Postgres 相同的 `db.sql`、`db.orm`、`db.transaction(...)`、`db.close()` 和 `[Symbol.asyncDispose]` 表面。Mongo 界面共享 `db.orm`、`db.close()` 和 `[Symbol.asyncDispose]`，但没有 `db.sql` 和没有 `db.transaction(...)`。

`db.sql` / `db.orm` 表面在名称上保持不变；每个操作表面暴露的运算符是目标形状的（Mongo 没有连接）。

## 工作流 — 构建系统/开发服务器集成

如果你希望合约工件在开发服务器运行时自动重新发射（而不是每次合约源更改时手动运行 `prisma-next contract emit`），请使用 `prisma-next-build` 中的构建工具插件：

- **Vite**: 安装 `@prisma-next/vite-plugin-contract-emit` 并在 `vite.config.ts` 中注册 `prismaVitePlugin('prisma-next.config.ts')`。
- **Next.js、Webpack、esbuild、Rollup、Turbopack**: 目前没有第一方插件——解决方法是一个 `prebuild` 脚本运行 `prisma-next contract emit`。参见 `prisma-next-build` 获取演练。

运行时侧（本技巧）是相同的：`db.ts` 从磁盘读取 `contract.json` + `contract.d.ts`。构建系统插件的工 作是开发期间保持这些文件最新。

## 常见陷阱

1. **在 `prisma-next.config.ts` 中硬编码 `DATABASE_URL`。** 泄露凭证；绕过按环境覆盖。使用 `.env`。
2. **在 `postgres<Contract>(...)` 中省略 `<Contract>` 类型参数。** 没有它，静态表面会折叠成通用形状，并且你将失去模型名称的自动完成。没有第二个类型参数——旧的二参数签名（`postgres<Contract, TypeMaps>`）已过时。
3. **忘记在合约导入中添加 `with { type: 'json' }`。** Node 的 ESM JSON 导入属性规范要求。
4. **中间件顺序很重要。** 外层包装。如果你想要遥测捕获内部中间件错误，请将其放在最外层。
5. **从不存在的界面子路径导入中间件。** `@prisma-next/postgres/middleware` 不存在。遥测来自 `@prisma-next/middleware-telemetry`；校验/预算来自 `@prisma-next/sql-runtime`（参见 *Prisma Next 尚未实现的功能*）。
6. **编造校验/预算选项名称。** 校验使用 `severities`（具有上述五个键），而不是 `requireWhere` / `maxRowsWithoutLimit`。预算使用 `maxLatencyMs`（不是 `maxDurationMs`）加上 `maxRows` / `defaultTableRows` / `tableRows`。如有疑问，请查看源代码。
7. **切换目标时不重新发射。** 合约工件是目标形状的；切换后重新发射。
8. **Postgres 脚本在查询完成后挂起。** `pg.Pool` 保持 Node 的事件循环活跃。解决方案：在脚本返回之前调用 `await db.close()`，或在脚本模块顶部使用 `await using db = postgres<Contract>(...)`。不要将 `await using db = postgres(...)` 放在请求处理程序内——它是块作用域的，并且会在每次请求后关闭池。正确的服务器模式是在 `db.ts` 中使用模块级单例，在进程生命周期内持续存在。

## Prisma Next 尚未实现的功能

- **`@prisma-next/postgres/middleware` 子路径。** Postgres 界面重新导出运行时工厂（`./runtime`）、配置（`./config`）、合约构建器（`./contract-builder`）、控制（`./control`）、家族（`./family`）、目标（`./target`）和服务器less（`./serverless`），但**不**重新导出中间件。目前的解决方案：从 `@prisma-next/sql-runtime` 导入 `lints` 和 `budgets`，从 `@prisma-next/middleware-telemetry` 导入 `createTelemetryMiddleware`。通过 `prisma-next-feedback` 报告你遇到的额外差距。
- **多数据库路由/读副本。** Prisma Next 没有内置的主/副本路由器或分片感知客户端。解决方案：为每个数据存储配置单独的 `db.ts` 实例，并在应用程序代码中调用正确的实例。如果你需要第一类多数据库路由，请通过 `prisma-next-feedback` 技巧提交功能请求。
- **连接池作为第一类配置字段。** `poolOptions.connectionTimeoutMillis` 和 `poolOptions.idleTimeoutMillis` 已连接，但 `pg.Pool` 的其余调优表面（最大连接数、`allowExitOnIdle`、ssl 选项等）没有通过界面命名暴露。解决方案：自己构造 `pg.Pool` 并通过 `pg:` 传递。如果你需要更多池字段通过界面暴露，请通过 `prisma-next-feedback` 技巧提交功能请求。
- **查询日志中间件作为内置。** Prisma Next 没有内置“记录每个查询”的中间件。解决方案：编写一个小型自定义中间件包装每个操作并记录；或使用 `createTelemetryMiddleware` 并在 `onEvent` 回调中记录。如果你需要一个内置查询日志，请通过 `prisma-next-feedback` 技巧提交功能请求。

## 参考

本技巧有意只包含正文；`prisma-next init --help`、`packages/3-extensions/postgres/src/config/define-config.ts` 中的 `defineConfig` 工厂、`packages/3-extensions/postgres/src/runtime/postgres.ts` 中的 `postgres()` 工厂，以及 `packages/2-sql/5-runtime/src/middleware/{lints,budgets}.ts` 中的中间件源都是选项级详细信息的权威表面。如有疑问，请查看源代码。

## 检查清单

- [ ] `db.ts` 从 `@prisma-next/<target>/runtime` 导入运行时工厂（`postgres`、`sqlite` 或 `mongo`）和 `Contract` 类型从 `./contract.d`.
- [ ] 合约 JSON 导入中添加 `with { type: 'json' }`.
- [ ] `<Contract>` 是 `postgres<Contract>(...)` 上的唯一类型参数（没有第二个参数）。
- [ ] `DATABASE_URL` 位于 `.env` 中，而不是在 `prisma-next.config.ts` 中。
- [ ] 中间件按预期顺序排列（遥测通常最外层）。
- [ ] `lints` / `budgets` 使用验证的选项键（`severities`、`maxLatencyMs`、`maxRows`、`tableRows`）。
- [ ] 任何环境分歧（如有）由 `NODE_ENV` 或类似控制。
- [ ] 未在任何已提交文件中硬编码凭证。
- [ ] 未编造 `@prisma-next/postgres/middleware` 子路径、`@prisma-next/postgres-extension-audit` 包或 `postgres<...>` 上的第二个类型参数。
- [ ] 未声称 Mongo 界面存在 `db.transaction(...)`——只有 Postgres 和 SQLite 暴露它。
- [ ] 未编造读副本/多数据库/额外池配置——指向 *Prisma Next 尚未实现的功能* 并路由到 `prisma-next-feedback`。
- [ ] 对于构建系统/开发服务器提示（Vite 插件、Next.js 插件、…）路由到 `prisma-next-build`.
