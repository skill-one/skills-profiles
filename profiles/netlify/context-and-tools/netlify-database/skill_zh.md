# Netlify 数据库

零配置管理的 Postgres。安装 `@netlify/database`，在 `netlify/database/migrations/` 下编写迁移文件，部署 — Netlify 会自动创建数据库并应用迁移。可从 Functions、Edge Functions、Builds 和 Agent Runners 中查询。

## 现代客户端（推荐使用）

```ts
import { getDatabase } from "@netlify/database";

const db = getDatabase();               // 自动选择运行时的连接
const userId = 42;
const users = await db.sql`SELECT * FROM users WHERE id = ${userId}`;  // 自动参数化
```

使用自己的驱动/ORM：
```ts
import { getConnectionString } from "@netlify/database";
const connectionString = getConnectionString();  // 正确的分支环境
```

**遗留 — 新代码请勿使用：** `import { neon } from "@netlify/neon"`。已被 `@netlify/database` 取代。用 Drizzle 的 `netlify-db` 适配器或通过 `getConnectionString()` 的 Postgres 驱动替换 `neon()` 调用。遗留环境变量 `NETLIFY_DATABASE_URL` 被 `NETLIFY_DB_URL` 取代。

## 文件存放位置

| 内容 | 位置 |
|------|----------|
| 迁移文件 | `netlify/database/migrations/` (SQL 文件或包含 `migration.sql` 的子目录) |
| 查询代码 | Functions (`netlify/functions/`), Edge Functions |
| Drizzle 模式 | `db/schema.ts` (约定) |
| Drizzle 客户端 | `db/index.ts` (约定) |
| 连接字符串 | `NETLIFY_DB_URL` 环境变量，或 `getConnectionString()` |

## 查询

`getDatabase(options?)` 返回一个具有 `sql` 和 `pool` 的客户端。`options.connectionString` 覆盖自动创建的连接；`options.debug` 启用日志记录。

```ts
const db = getDatabase();
const active = await db.sql`SELECT * FROM users WHERE active = ${true}`;
await db.sql`INSERT INTO users (name, email) VALUES (${"Ada"}, ${"ada@example.com"})`;
await db.sql`UPDATE users SET name = ${"Ada Lovelace"} WHERE id = ${1}`;
await db.sql`DELETE FROM users WHERE id = ${1}`;

// 类型化行
interface User { id: number; name: string; email: string; }
const typed = await db.sql<User>`SELECT * FROM users`;

// 流式处理
for await (const row of db.sql`SELECT * FROM users`.stream()) { /* ... */ }
for await (const chunk of db.sql`SELECT * FROM users`.chunked(100)) { /* ... */ }
```

`SQLTemplate` 方法：`execute()` → `Promise<T[]>`，`stream()` → `AsyncGenerator<T>`，`chunked(n)` → `AsyncGenerator<T[]>`，`toSQL()` → 原始 SQL + 参数（不执行）。

`sql` 辅助函数：
- `sql.identifier(value)` — 安全的表/列名。字符串、字符串数组或 `{ schema, table, column, as }`。
- `sql.values(rows)` — 从二维数组批量插入值列表。
- `sql.default` — SQL `DEFAULT` 关键字。
- `sql.raw(value)` — **注入未参数化的 SQL；绕过注入保护。仅用于可信常量（例如 `"DESC"`），永远不要用于用户输入。**
- `sql.unsafe(query, params?, { rowMode })` — 原始查询字符串与 `$1` 参数；`rowMode` 是 `"array"` 或 `"object"`。

### 事务 — 使用 `pool`

`db.pool` 是一个 [`pg.Pool`](https://node-postgres.com/apis/pool)。`BEGIN`/查询/`COMMIT` 必须在同一个连接上运行：
```ts
const client = await db.pool.connect();
try {
  await client.query("BEGIN");
  await client.query("INSERT INTO users (name, email) VALUES ($1, $2)", ["Ada", "ada@example.com"]);
  await client.query("INSERT INTO posts (author_id, title) VALUES ($1, $2)", [1, "First post"]);
  await client.query("COMMIT");
} catch (e) {
  await client.query("ROLLBACK");
  throw e;
} finally {
  client.release();
}
```

使用自己的驱动：
```ts
import { getConnectionString } from "@netlify/database";
import pg from "pg";
const pool = new pg.Pool({ connectionString: getConnectionString() });

// 或通过环境变量使用 `postgres` 驱动
import postgres from "postgres";
const sql = postgres(process.env.NETLIFY_DB_URL);
```

## Drizzle ORM

**必须从 `@beta` 安装这两个包 — 这是必需的。** `latest` 缺少 `drizzle-orm/netlify-db` 适配器，将失败。
```bash
npm install @netlify/database drizzle-orm@beta
npm install -D drizzle-kit@beta
```

`drizzle.config.ts` — 你 **必须** 将 `out` 设置为 Netlify 迁移目录，否则 Netlify 不会应用生成的迁移：
```ts title="drizzle.config.ts"
import { defineConfig } from "drizzle-kit";
export default defineConfig({
  dialect: "postgresql",
  schema: "./db/schema.ts",
  out: "netlify/database/migrations",   // 不是默认的 "drizzle"
});
```

```ts title="db/schema.ts"
import { pgTable, serial, text, timestamp } from "drizzle-orm/pg-core";
export const users = pgTable("users", {
  id: serial().primaryKey(),
  name: text().notNull(),
  email: text().notNull().unique(),
  createdAt: timestamp().defaultNow(),
});
```

```ts title="db/index.ts"
import { drizzle } from "drizzle-orm/netlify-db";  // 原生适配器，自动配置
import * as schema from "./schema";
export const db = drizzle({ schema });
```

```ts title="netlify/functions/api.ts"
import { desc } from "drizzle-orm";
import type { Config, Context } from "@netlify/functions";
import { db } from "../../db";
import { users } from "../../db/schema";

export default async (req: Request, context: Context) => {
  if (req.method === "GET") {
    const allUsers = await db.select().from(users).orderBy(desc(users.createdAt));
    return Response.json(allUsers);
  }
  if (req.method === "POST") {
    const { name, email } = await req.json();
    const [user] = await db.insert(users).values({ name, email }).returning();
    return Response.json(user, { status: 201 });
  }
  return new Response("Method not allowed", { status: 405 });
};

export const config: Config = { path: "/api/users" };
```

编辑模式后生成迁移：`npx drizzle-kit generate`。

**永远不要对 Netlify 托管的数据库运行 `drizzle-kit push`，也永远不要对 `NETLIFY_DB_URL` 运行 `drizzle-kit migrate`。** 模式仅作为提交的迁移文件通过部署应用到托管数据库。`generate` 写入文件；部署应用它们。

## 迁移文件

文件存放在 `netlify/database/migrations/`。两种格式：
```text
netlify/database/migrations/20260301143000_create_users.sql          # 单个 SQL 文件
netlify/database/migrations/20260318091500_add_posts/migration.sql   # 子目录形式
```

命名：`<数字>_<别名>` — `数字` 是数字（时间戳或 `0001`…）定义顺序；`别名` 是小写字母/数字/连字符/下划线。按**字典顺序**排序，按顺序应用。**使用时间戳前缀** (`netlify database migrations new` 处理此操作) 来避免顺序错误。

```sql title="netlify/database/migrations/20260425103000_create_comments.sql"
CREATE TABLE comments (
  id SERIAL PRIMARY KEY,
  post_id INTEGER NOT NULL REFERENCES posts(id),
  author_id INTEGER NOT NULL REFERENCES users(id),
  body TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);
```

**应用时：**
- 生产部署：在发布前立即应用；失败会阻止发布。自动发布关闭时，Netlify 会等待手动发布后再应用。
- 部署预览：在上线前每个部署都会应用；失败会导致部署失败。
- 本地：**不自动** — 自己运行 `netlify database migrations apply`。

**迁移的陷阱（所有都被检测为 drift / 拒绝）：**
- **永远不要编辑已应用的迁移** — 校验和漂移：`migration "<name>" 在应用后已被修改`。编写新的纠正迁移。
- **永远不要删除已应用的迁移** — `... 在应用后已被删除`。恢复它。
- **顺序错误：** 前缀 ≤ 最高已应用版本会被拒绝。时间戳可避免此问题。
- 优先使用向后兼容的迁移。破坏性更改（重命名/删除列）→ 跨多个部署扩展和收缩。新表/可空列 → 单个迁移即可。

自带迁移系统：选择一个**不是** `netlify/database/migrations` 的目录以避免自动检测，然后你拥有应用到预览分支和生产环境。

参见 `references/migrations.md`。

## 本地开发

本地是**一个**所有代码都指向的数据库 — 分支是部署时的概念，在本地不存在。它是一个真实的 Postgres 兼容引擎，镜像生产环境，但单进程（不适合负载测试）；自动扩展/睡眠设置不适用。

启动它 — 任何路径，状态都是可互换的：
```bash
netlify dev                                    # CLI 启动 + 销毁本地数据库
```
或 Vite 插件：
```ts title="vite.config.ts"
import { defineConfig } from "vite";
import netlify from "@netlify/vite-plugin";
export default defineConfig({ plugins: [netlify()] });
```

常见命令（本地数据库运行时）：
```bash
netlify database migrations apply                        # 本地应用待处理的迁移
netlify database migrations new -d "add users table"     # 框架迁移
netlify database migrations pull                          # 从远程覆盖本地迁移
netlify database status                                   # 启用？安装？已应用/待处理的迁移
netlify database connect                                  # 交互式 SQL REPL
netlify database connect --query "SELECT * FROM users LIMIT 10"
netlify database reset                                    # 删除所有模式/表 — 仅限本地
netlify database migrations reset                         # 删除未应用的本地迁移文件
```

外部工具（`netlify dev` 运行时工作）：
```bash
psql "$(netlify database connect --json | jq -r .connection_string)"
```

参见 `references/local-dev.md`。

## 配置

新项目：在 https://app.netlify.com/start 描述你的应用给 Agent Runners，或本地运行 `netlify create "<description>"`。

现有项目：
```bash
netlify database init      # 安装 @netlify/database，选择 Drizzle 或原始 SQL，框架迁移
netlify database init --yes # 非交互式（CI / 代理）
netlify dev
```
手动：`npm install @netlify/database`，在 `netlify/database/migrations/` 下编写迁移文件，编写函数，`netlify dev`，部署。

**如果 `@netlify/database` 未安装，Netlify 将不会自动创建数据库** — 你需要从 UI **Data & Storage** > **Database** 菜单手动创建一个。安装该包。

## CLI 参考 (`netlify database`)

先决条件：Node ≥ 20.12.2，Netlify CLI ≥ 26.0.0 (`npm install -g netlify-cli`)。所有命令支持 `--json`。

| 命令 | 目的 | 关键标志 |
|---------|---------|-----------|
| `init` | 在项目中设置数据库 | `-y, --yes` |
| `status` | 状态：启用、安装、连接字符串、已应用/待处理的迁移 | `-b, --branch`, `--show-credentials` |
| `connect` | SQL REPL，或 `--query` 一次性查询 | `-q, --query`, `--json` |
| `migrations apply` | 将待处理的迁移应用到本地数据库 | `--to <name>` |
| `migrations new` | 框架迁移 | `-d, --description`, `-s, --scheme sequential\|timestamp` |
| `migrations pull` | 从分支覆盖本地文件 | `-b, --branch`, `--force` |
| `migrations reset` | 删除未应用的本地迁移文件 | `-b, --branch` |
| `reset` | 删除所有数据/表 — **仅限本地** | — |

参见 `references/cli-commands.md`。

## REST API

针对单个站点，根目录为 `https://api.netlify.com/api/v1`，OAuth 2。完整参考：https://open-api.netlify.com。

| 方法 + 路径 | 目的 |
|---------------|---------|
| `POST /sites/{site_id}/database` | 创建数据库（如果存在则返回现有连接字符串）；`region` 可选 |
| `GET /sites/{site_id}/database` | 获取连接字符串 |
| `POST /sites/{site_id}/database/branch` | 创建分支；正文 `deploy_id` (必需)，`parent_branch_id` (可选，默认为生产) |
| `GET /sites/{site_id}/database/branch/{deploy_id}` | 获取分支连接字符串（如果没有则返回 404） |
| `DELETE /sites/{site_id}/database/branch/{deploy_id}` | 删除部署的分支 |
| `POST /sites/{site_id}/database/snapshot` | 快照分支（默认为生产） |
| `GET /sites/{site_id}/database/snapshots` | 列出快照 |
| `DELETE /sites/{site_id}/database/snapshot/{snapshot_id}` | 删除快照 |
| `POST /sites/{site_id}/database/snapshot/{snapshot_id}/restore` | 将快照恢复到分支（默认为生产） |

**分支删除和快照恢复是破坏性的，需要用户明确确认。** 快照恢复不是常规的生产回滚工具。

## 测试

纯 Postgres 用于单元/集成测试（不包含函数）：
```ts title="db.test.ts"
import { NetlifyDB } from "@netlify/database-dev";  // npm i -D @netlify/database-dev
import { Client } from "pg";
import { afterAll, beforeAll, expect, test } from "vitest";

let db: NetlifyDB, connectionString: string;
beforeAll(async () => {
  db = new NetlifyDB();
  connectionString = await db.start();
  await db.applyMigrations("./netlify/database/migrations");
});
afterAll(async () => { await db.stop(); });

test("inserts and reads a user", async () => {
  const client = new Client({ connectionString });
  await client.connect();
  await client.query("INSERT INTO users (name) VALUES ($1)", ["Ada"]);
  const { rows } = await client.query("SELECT name FROM users");
  expect(rows).toEqual([{ name: "Ada" }]);
  await client.end();
});
```
`NetlifyDB(options?)`：`directory`（持久化到磁盘；省略 = 内存），`port`（默认随机），`logger`。

完整 Netlify 环境（函数/边缘函数像生产环境一样读取 `NETLIFY_DB_URL`）：
```ts
import { NetlifyDev } from "@netlify/dev";  // npm i -D @netlify/dev
const netlifyDev = new NetlifyDev({ projectRoot: "./fixtures/my-project" });
await netlifyDev.start();  // 在运行时设置 NETLIFY_DB_URL
// ...测试...
await netlifyDev.stop();
```

## 数据库分支（部署时）

生产部署是唯一会接触生产数据库的部署。每个部署预览都有自己的分支，在预览创建时被生产数据的副本初始化；那里的模式/数据更改永远不会影响生产。自动配置，无需代码更改。

**预览分支可以包含生产数据，包括 PII — 并且预览部署链接是公开的。在分享预览链接前警告用户。**

## 运行时注意事项

- **`Environment not configured`** (`getDatabase()` 无法解析连接字符串)：在 Netlify 外运行，在 **Lambda 兼容模式的函数**中，或过时的 CLI。修复：显式传递 `connectionString`。
  ```ts
  const db = getDatabase({ connectionString: "postgres://..." });
  ```
  Lambda 兼容模式是唯一必须自己传递 `connectionString` 的场景。
- **`database feature not available for this account`** — 需要基于计费的计划。
- **`compute customization requires a Pro or higher plan`** — 自动扩展/睡眠设置需要 Pro+；Free/Personal 使用默认值。
- **`branch limit reached: maximum <N> branches...`** — 每个活动的部署预览都会消耗一个分支；删除不需要的分支或升级。
- **`database not found`** — 未创建数据库；运行 `netlify database init`。
- **`cannot reset the production branch`** — 重置仅限非生产环境。

## 限制

- **计划：** Netlify 数据库仅在计费计划上可用；活动数据库会消耗计算和带宽的计费。存储在 2026 年 7 月 1 日之前免费。
- **权限：** 只有团队所有者可以删除数据库；只有团队所有者和开发者可以查看连接字符串（`Access Denied` = 角色不足）。
- **密钥：** 连接字符串包含用户名和密码。永远不要提交它们；存储在密钥管理器/环境变量提供者中。

## 将现有的 Postgres 项目切换到 Netlify 数据库

三个阶段：配置（在分支上创建基线模式），排练（交换代码，将数据复制到预览分支，验证），切换（将数据导入生产，合并）。可以从任何 Postgres 源（Neon、Supabase、RDS、自管理、遗留 `@netlify/neon`）工作。使用 `pg_dump`/`pg_restore`（与源匹配的版本）。存在短暂的数据丢失窗口 — 在最终导出和生产部署之间的源写入不会跨越。

阶段 2/3 代码交换（Drizzle）：
```ts title="db/index.ts"
import { drizzle } from "drizzle-orm/netlify-db";
import * as schema from "./schema";
export const db = drizzle({ schema });
```

完整步骤（转储标志、回滚、清理）：`references/migration-from-extension.md` 和 `references/legacy-extension.md`。

<!-- 缺口：计划层级命名（计费 vs Free/Personal/Pro）未在源中协调；确切的计划限制、权限表和快照 UI 流程位于此分组之外的页面。 -->

<!-- system: agent-context/database/system.md — 人类拥有的，由 ctx-gen 合并；编辑 system.md，不要编辑此部分 -->
# Netlify 数据库规则

这些是组织约定，不是文档事实 — 由 ctx-gen 合并到渲染的技能中，并且永远不会生成。由技能维护者拥有。

1. 生产数据更改表示为 DML 迁移 — 代理永远不会直接编辑行（UI 行编辑供人类使用；它不是代理界面）。
2. 预览分支可以包含生产数据，包括 PII — 并且预览部署链接是公开的。在分享前警告用户。
3. 仅使用文档化界面：不针对内部端点进行原始 psql，不使用 `netlify api` 抓取，不从本地 CLI 配置文件读取令牌。
4. 深入指南存在于此技能中：`references/operational-footguns.md`、`references/migrations.md`、`references/local-dev.md`、`references/cli-commands.md`、`references/migration-from-extension.md`、`references/legacy-extension.md`。
5. 模式更改仅作为提交的迁移文件通过部署应用到托管数据库。永远不要以任何形式对 Netlify 托管的数据库运行 `drizzle-kit push`，永远不要对 `NETLIFY_DB_URL` 运行 `drizzle-kit migrate`，并且永远不要通过 `netlify database connect` 或任何直接连接应用 DDL。
6. 当 `netlify` 命令或部署失败时，向用户显示确切错误、部署日志链接和受影响的站点/分支，然后停止 — 不要编造恢复命令或升级到低级工具。
7. 首次部署 `401 Access Denied` on `createSiteDatabase`：如果它在 `--prod`-first 部署中发生，重试预览-首先 (`netlify deploy`，不带 `--prod`)；如果预览也失败，报告并停止。永远不要 curl `api.netlify.com`、运行 `netlify api createSiteDatabase` 或从本地 CLI 配置文件拉取令牌来绕过它。
8. 更改现有数据的请求在生产分支和预览分支之间是模糊的 — 如果提示没有说明，请询问。代表他人操作时，默认不更改生产。
9. 破坏性数据库操作 — REST 分支删除、快照恢复、任何重置 — 需要用户先明确确认。正文不应将快照恢复视为常规的生产回滚工具。
10. 固定：`drizzle-orm` 和 `drizzle-kit` 必须从 `@beta` 安装 — `latest` 缺少 `drizzle-orm/netlify-db` 适配器，将失败。正文不能将此软化为建议。
