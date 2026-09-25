# Prisma Next — 查询

> **编辑你的数据合约。Prisma 会处理其余部分。**

一旦合约被发出且数据库已更新，这项技能涵盖了你对数据的所有操作：读取、写入、预加载关联、聚合，以及在 ORM 和低级查询通道之间的选择。

## 何时使用

- 用户想要读取、写入、更新或删除数据。
- 用户想要包含/预加载关联。
- 用户想要分页、排序、过滤、投影。
- 用户想要将操作包装在事务中 (`db.transaction(...)` — Postgres 和 SQLite)。
- 用户想要聚合 (`count`、`sum`、`avg`、…)。
- 用户询问关于查询通道的问题（ORM 与 SQL 构建器/查询构建器）。
- 用户提到：*查询、select、where、orderBy、take、skip、include、预加载、first、all、count、aggregate、create、update、delete、upsert、returning、drizzle-style、kysely-style、prisma client*。

## 何时不使用

- 用户想要添加/更改模型 → `prisma-next-contract`。
- 用户想要连接 `db.ts` 或添加中间件 → `prisma-next-runtime`。
- 用户通过 Supabase 角色绑定数据库进行查询 (`asUser` / `asAnon` / `asServiceRole`、RLS、`auth.*` admin 读取) → `prisma-next-supabase` 用于角色绑定表面；本技能中的所有内容都适用于返回的 `RoleBoundDb`。
- 用户想要调试查询失败（结构化错误包）→ `prisma-next-debug`。

## 选择你的目标

Prisma Next 在 `src/prisma/db.ts` 中为每个目标提供 **两个查询通道**，使用相同的 `db` 值。**在编写查询之前，请阅读 `db.ts` 并加载匹配的目标指南：**

| `db.ts` 中的运行时导入 | 加载 |
|---|---|
| `@prisma-next/postgres/runtime` | [`postgres.md`](./postgres.md) — `db.orm.<Model>` + `db.sql.<table>` |
| `@prisma-next/mongo/runtime` | [`mongo.md`](./mongo.md) — `db.orm.<root>` + `db.query.from(...)` |
| `@prisma-next/extension-supabase/runtime` | [`postgres.md`](./postgres.md) — Supabase `RoleBoundDb` 是一个 Postgres 表面 (`db.orm.<Model>` + `db.sql.<table>`); 首先通过 `prisma-next-supabase` 绑定角色 |

两个目标共享合约和连接在同一个 `db` 值上。首先使用 ORM；当 ORM 无法表达形状时，切换到低级通道。通道选择是局部的——一个查询函数选择一个通道，而不是整个应用程序。

**不要混合目标示例。** Postgres 使用帕斯卡大小写的模型根 (`db.orm.User`) 和 `db.sql.user`；Mongo 使用小写复数根 (`db.orm.users`) 和 `db.query.from('users')`。Mongo 没有 `db.sql`，Postgres 没有 `db.query` SQL 构建器等效项。

## 命名空间感知访问器

当合约声明多个命名空间（例如 `public` 和 `auth`）时，模型和表通过命名空间坐标进行引用：

- **ORM**：`db.orm.<namespace>.<Model>` — 例如 `db.orm.public.User`、`db.orm.auth.User`
- **SQL 构建器**：`db.sql.<namespace>.<table>` — 例如 `db.sql.public.users`、`db.sql.auth.users`

扁平的 `db.orm.User` / `db.sql.users` 形式仍然适用于单命名空间合约（或当所有表名在命名空间之间唯一时）。当相同的裸名出现在多个命名空间中时，你必须使用命名空间坐标。

有关示例，请参阅 [`postgres.md` § 命名空间感知访问器](./postgres.md#namespace-aware-accessors)。

## 消费结果：`await`、`.toArray()` 或 `for await`

关键在于早期正确处理——在 **Postgres 和 Mongo 上**，`.all()` 返回一个 **`AsyncIterableResult<Row>`**，它既是 `PromiseLike<Row[]>` 也是 `AsyncIterable<Row>`。这意味着三种消费形式都有效，最规范的是最短的：

```typescript
const users = await db.orm.User.select('id', 'email').all();
//    ^? Row[]   ← the Thenable resolves to a real array. This is the default idiom.
```

你**不需要** `collect()` / `toArray()` 辅助函数——`await` 足够。内部 `await` 调用结果的 `then(...)`，将行缓冲到数组中。两种等效的替代方案存在于它们读起来更好的情况下：

```typescript
// `.toArray()` 返回一个真正的 `Promise<Row[]>`。仅在需要真正的 `Promise` 而不仅仅是 thenable 时使用它：一个 `Promise<Row[]>` 类型的插槽（`AsyncIterableResult` 只有 `then`，没有 `catch` / `finally`，因此它不满足该注解），或运行时的 `instanceof Promise` 检查。请注意，`await` 和 `Promise.all` / `Promise.race` 组合器都接受 thenable 直接——那些不是调用 `.toArray()` 的原因。每当你在这里只是要 await 它时，使用 `await ...all()` 并跳过 `.toArray()`。
const rows: Promise<User[]> = db.orm.User.select('id', 'email').all().toArray();

// 流式传输——逐行处理，不缓冲整个结果。用于真正的大结果集（任何无法舒适地放入内存的内容）或可以在所有行到达之前开始工作的管道。
for await (const user of db.orm.User.select('id', 'email').all()) {
  process(user);
}
```

除了集合级别的 `.first()`（在 Postgres 上发出 `LIMIT 1`）之外，结果还提供了两个单行快捷方式：

```typescript
const user = await db.orm.User.where({ id }).all().first();
//    ^? Row | null   ← buffers, returns the first row or null. Issues no LIMIT.
const required = await db.orm.User.where({ id }).all().firstOrThrow();
//    ^? Row          ← buffers; throws `RUNTIME.NO_ROWS` if empty.
```

对于真正的单行读取，请优先使用集合级别的 `.first()`（在 Postgres 上向 SQL 添加 `LIMIT 1`）而不是 `.all().first()`（它获取所有行并丢弃其余部分）。结果级别的辅助函数用于你已经需要完整结果并希望在不进行额外往返的情况下获取第一行的情况。

**结果是单消费。** 每个 `AsyncIterableResult` 实例只能消费一次——通过 `await`、`.toArray()` 或 `for await`。尝试第二次消费它将抛出 **`RUNTIME.ITERATOR_CONSUMED`**。修复方法几乎总是将数组存储在第一次消费时的变量中并重用该变量：

```typescript
// 不良——第二次 await 抛出 RUNTIME.ITERATOR_CONSUMED。
const result = db.orm.User.select('id', 'email').all();
const a = await result;
const b = await result;

// 良好——一次缓冲，重用数组。
const users = await db.orm.User.select('id', 'email').all();
const a = users;
const b = users;
```

如果你在包装 `.all()` 的代码库中看到 `collect(...)` / `toArray(...)` 辅助函数，它们是遗留的——`await` 免费完成同样的事情。当你修改周围代码时，请删除它们。

## 从短脚本中运行查询

当用户运行一次性 `tsx my-script.ts`（不是长时间运行的服务）时，在末尾调用 `await db.close()` 以确保进程干净退出——在 Postgres 上， фасад拥有的池保持 Node 的事件循环活跃；在 Mongo 上，fasad 拥有的 `MongoClient` 也这样做。有关完整模式，包括 `await using`，请参阅 `prisma-next-runtime` § *作为脚本运行（清理）*。

```typescript
// src/scripts/seed.ts
import { db } from '../prisma/db';

// Postgres — 合约中的帕斯卡大小写模型根
for (const u of users) {
  await db.orm.User.create(u);
}

// Mongo — 合约中的小写复数根（例如 users，而不是 User）
// for (const u of users) {
//   await db.orm.users.create(u);
// }

console.log('Seeded.');
await db.close();
```

## 常见陷阱（跨目标）

1. **在 Mongo 项目上使用 Postgres 示例（反之亦然）。** 检查 `db.ts` 并加载正确的目标指南 ([`postgres.md`](./postgres.md) 或 [`mongo.md`](./mongo.md))。
2. **编写 `collect()` / `toArray()` 辅助函数将 `.all()` 转换为数组。** `.all()` 返回一个 `AsyncIterableResult<Row>`，它本身就是 `PromiseLike<Row[]>`——`await collection.all()` 直接生成 `Row[]`。见上文 *消费结果*。
3. **两次消费 `AsyncIterableResult`。** 每个结果是单用的。第二个消费者会抛出 `RUNTIME.ITERATOR_CONSUMED`。将数组缓冲到一个变量中并重用该变量。

特定目标的陷阱位于每个目标指南中。

## Prisma Next 尚未实现的功能

- **跨连接表的 N:M `.include()`。** 合约 IR 支持通过 `through` 连接表的多对多关系，并且 N:M 关系在 ORM 集合上显示为有效关系名称。然而，N:M 关系的 `.include()` 不会发出两步连接——查询计划构建器仅处理直接连接列 (`localColumn` / `targetColumn`) 并忽略 `through` 元数据。尝试它要么产生错误结果，要么产生错误。解决方法：通过 `db.sql.<table>` 以显式连接连接表表达 N:M 遍历。
- **N:M 嵌套突变。** `mutation-executor.ts` 明确抛出 `'N:M nested mutations are not supported yet'`，用于通过 N:M 关系嵌套创建/链接。
- **postgres фасад中的 `and` / `or` / `not` 组合器。** 组合器目前从 `@prisma-next/sql-orm-client`（一个内部包）导入。今天的解决方法：直接从 `@prisma-next/sql-orm-client` 导入它们，就像示例应用程序那样。如果你想在 `@prisma-next/postgres/runtime` 上获得它们，请通过 `prisma-next-feedback` 提交功能请求。
- **`.orderBy(...)` / `.take(...)` 在分组聚合上（Postgres）。** `db.orm.<Model>.groupBy(...).aggregate(...)` 材化一个 `Promise<Array<Group & Aggregates>>` 并在数据库层不暴露排序或行限制。结果：一个“按 SUM 顶 N 组”查询回退到 JS 端的排序 + 切片，在小基数下可以，在大规模下不好。解决方法：(a) 跳到 `db.sql.<table>` 并直接对聚合表编写 `GROUP BY` + `ORDER BY` + `LIMIT`；(b) 如果分组基数有界，则接受 JS 端的排序/切片。如果这影响了你的生产环境，请通过 `prisma-next-feedback` 提交功能请求。
- **原始 SQL 通道。** Prisma Next 目前没有为用户暴露原始 SQL 表面（没有 `db.sql.raw(...)`）。解决方法：通过 SQL 构建器建模查询——对于构建器尚不能表达的形状，通过 `prisma-next-feedback` 提交功能请求描述形状，以便团队决定是扩展构建器还是发布原始通道。
- **TypedSQL（`.sql` 文件编译为类型调用函数）。** 未实现。解决方法：坚持使用 SQL 构建器；对于重复查询，提取一个返回构建计划的函数，并在调用点调用 `db.runtime().execute(plan)`。如果你想要 `.sql` 文件编译路径，请通过 `prisma-next-feedback` 提交功能请求。
- **`EXPLAIN` / 查询计划检查。** Prisma Next 没有暴露 `.explain()` 方法。解决方法：通过运行时的 `pg:` 绑定（见 `prisma-next-runtime`）连接你控制的 `pg.Pool` 并通过它发出 `EXPLAIN ANALYZE`。如果你需要一个一流的计划检查表面，请通过 `prisma-next-feedback` 提交功能请求。
- **流式传输大结果集。** 今天没有 `.stream()` 光标。解决方法：对于中等大小，通过 `.skip(n).take(m)` 进行分页；对于非常大的集合，从运行时的 `pg:` 绑定保留一个 `pg.Client` 并直接通过它流式传输。如果你需要一个内置的流式传输表面，请通过 `prisma-next-feedback` 提交功能请求。
- **多语句批处理（Prisma-7 风格的 `db.$transaction([call1, call2])`）。** Prisma Next 逐个运行每个调用。解决方法：在 Postgres 上将原子相关的工作包装在 `db.transaction(async (tx) => { ... })` 中。如果你想要数组作为批处理语义，请通过 `prisma-next-feedback` 提交功能请求。
- **Mongo фасад事务。** `@prisma-next/mongo/runtime` 没有暴露 `db.transaction(...)`。多文档原子性尚未在 Prisma Next Mongo fasad 中包装。解决方法：如果你控制客户端绑定（`mongoClient:` 选项），请直接使用 MongoDB 驱动程序的会话 API。如果你需要一个一流的 fasad 表面，请通过 `prisma-next-feedback` 提交功能请求。
- **Mongo ORM 聚合。** 在 `db.orm.<root>` 上没有 `.aggregate(...)` / `.groupBy(...)`。解决方法：通过 `db.query.from(...).group(...).build()` 和 `runtime.execute(plan)` 表达聚合。
- **Mongo fasad 上的过滤器辅助函数。** 丰富的过滤器（`.in`、范围、布尔组合）目前从 `@prisma-next/mongo-query-ast/execution`（`MongoFieldFilter` 等）导入——尚未在 `@prisma-next/mongo/runtime` 上重新导出。解决方法：尽可能使用对象相等 `.where({ field: value })`；仅在必要时从内部包导入。与 fasad 完整性差距一起在 Linear `TML-2526` 中跟踪。
- **自动 N+1 检测。** Prisma Next 在缺少 `.include(...)` 时不会发出警告。解决方法：在代码审查中明确 `.include(...)`；`lints` 中间件（见 `prisma-next-runtime`）捕获更常见的编写错误（`DELETE` / `UPDATE` 上缺少 `WHERE`、`SELECT` 上缺少 `LIMIT`）。

## 参考文件

这项技能按需加载。特定目标的参考路径位于每个目标指南中：

- **Postgres** — [`postgres.md` § 参考文件](./postgres.md#reference-files)
- **Mongo** — [`mongo.md` § 参考文件](./mongo.md#reference-files)

## 检查清单

- [ ] 确认了从 `db.ts` 激活的目标并加载了匹配的指南 ([`postgres.md`](./postgres.md) 或 [`mongo.md`](./mongo.md))。
- [ ] 对于多命名空间合约，当相同的裸名存在于多个命名空间中时，使用了 `db.orm.<ns>.<Model>` / `db.sql.<ns>.<table>` 坐标。
- [ ] 选择了正确的通道（默认为 ORM；对于 ORM 无法表达的形状，使用低级构建器）。
- [ ] 使用 `.first()` / `.first({ pk })`（Postgres）或 `.where({ ... }).first()`（Mongo）进行单行读取——而不是 `.all()`。
- [ ] 使用纯 `await` 消费 `.all()`（不需要 `collect()` / `toArray()` 辅助函数）。仅在确实需要流式传输时使用 `for await`，并且永远不会两次迭代同一个结果。
- [ ] 未在 Mongo 项目上使用 `db.sql` 或在 Postgres SQL 构建器预期的地方使用 `db.query`。
- [ ] 完成了加载指南中特定目标的检查清单。
