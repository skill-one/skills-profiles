**首先**：使用父级 `neon` 技能获取 Neon 概览、开始使用 Neon、Neon 开发最佳实践等。

如果未安装 `neon` 技能，请从 https://neon.com/docs/ai/skills/neon/SKILL.md 获取或使用以下命令安装：

```bash
neon skills -s neon -y
```

# Neon 函数

目前可在 `aws-us-east-2`、`aws-us-east-1`、`aws-eu-central-1` 和 `aws-ap-southeast-1` 中使用。

Neon 函数是部署在 Neon 分支上的长运行 Node.js HTTP 处理程序。每个函数都获得一个公共 HTTPS URL，在您的数据库所在的区域运行，如果该分支有 Postgres，则自动注入 `DATABASE_URL`。您通过相同的 Neon CLI、`neon.ts` 和 API 部署和管理它们。

使用此技能帮助用户定义、本地运行、部署和管理其数据库旁边的函数。交付部署的函数及其调用 URL、工作本地 `neon dev` 循环或来自官方 Neon 文档的精确答案。

## 使用场景

当工作负载是请求/响应处理程序，并且受益于保持活动状态并靠近数据时，请使用 Neon 函数：

- **长时间运行的请求/响应流，超出 lambda 风格限制。** 每个请求执行多个 LLM 调用和工具调用，或图像/视频生成，通常会超过传统的无服务器函数的 ~10-60 秒执行限制和短流窗口。Neon 函数是长运行的：处理程序只需要在 15 分钟内开始响应，打开的流只要字节持续流动就会保持活动状态。这足以应对真实的代理工作负载。
- **无状态流，无需附加 Redis。** 由于函数跨请求保持活动状态，因此它可以托管 SSE 端点或 WebSocket 服务器，并在进程内保持连接打开——无需外部状态存储（Redis 等）即可保持流的一致性。模块范围状态（`pg` 池、内存计数器）在相同的隔离器上跨请求持久化。
- **必须靠近 Postgres 的计算。** 函数在分支的数据库所在的区域运行，因此每个查询都没有跨区域往返。为您自动注入 `DATABASE_URL`。
- **与您的数据分支的后端。** 每个分支在其自己的 URL 上运行自己的函数版本，针对其自己的隔离状态。预览部署、CI 和开发环境每个都获得一个自包含的后端——将子分支部署到父分支永远不会影响父分支。
- **从函数（或现有框架处理程序）查询 Postgres。** 优先于数据 API。当应用程序已经使用 PostgREST 或 Supabase-js 数据库调用，或者正在迁移该客户端时，请使用数据 API。
- **Webhooks、机器人和响应后工作。** Webhook 处理程序扩展到多个数据库写入、Discord/WebSocket 机器人，以及通过 `waitUntil` 进行的“发射并忘记”后续操作（分析、审计日志）都适用。
- **定期 HTTP 工作。** 函数触发器在 cron（`type: "schedule"`）或当对象在对象存储中创建时（`type: "storage_object_created"`）向函数 POST。相同的 `fetch` 处理程序，相同的 15 分钟首次字节限制。请参阅 [Function Triggers](#function-triggers)。

如果工作负载是纯静态网站，或者必须运行在当前不受支持的区域（`aws-us-east-2`、`aws-us-east-1`、`aws-eu-central-1` 和 `aws-ap-southeast-1`）之外，则此工具尚不适用（请参阅 [Timeouts and Runtime Limits](#timeouts-and-runtime-limits) 和 [Availability](#availability)）。

## 功能

- **长运行 & 无服务器** — 专为 WebSocket 服务器（请参阅 [WebSocket Servers](#websocket-servers）、SSE 端点（请参阅 [Server-Sent Events (SSE)](#server-sent-events-sse）、长时间代理 HTTP 流和 API。仍然可以扩展到零（空闲时）。
- **Web 标准处理程序** — 任何具有 `fetch(request)` 方法的默认导出，返回 `Response`（Workers/WinterTC 兼容）。Hono 应用程序导出确切的形状，因此 `export default app` 直接工作。运行在 Node.js 24 上，因此所有 Node API 都可用。
- **靠近您的数据库** — 在分支的区域运行；当分支有 Postgres 时，自动注入 `DATABASE_URL`。
- **分支化** — 每个分支在其自己的 URL 上针对其自己的隔离状态运行自己的函数版本。
- **相同的 CLI/API** — 通过 `neon`、`neon.ts` 或 Neon API 部署和管理。
- **Function Triggers** — Neon 在 cron 或对象存储中创建时（`storage_object_created`）向函数 POST。请参阅 [Function Triggers](#function-triggers)。

## 可用性

在使用任何东西之前检查此先决条件：Neon 函数目前可在 `aws-us-east-2`、`aws-us-east-1`、`aws-eu-central-1` 和 `aws-ap-southeast-1` 中使用。确认用户的 Neon 项目位于这些区域之一。

## 架构：函数的适用位置

Neon（包括函数）是 **后端原语，而不是全栈应用托管**。在 **Vercel**（或 Netlify，或其他前端/应用托管平台）上托管您的应用程序；函数是您数据旁边长时间运行、有状态的后端切片。它们通过以下两种方式与该平台组合：

- **将函数添加到全栈应用程序中。** 您在 Vercel（或 Netlify）上的 Next.js / TanStack Start 应用程序拥有 UI、身份验证（Managed Auth、Better Auth、Clerk 或另一个 IdP），并直接与 Lakebase Postgres 和对象存储通信。将函数作为 Web 应用程序和其他客户端的 Hono API 层添加，或用于数据旁边的一个作业：对象存储上传、AI 代理、Discord 机器人、WebSocket 或 SSE 服务器。（请参阅 [Functions as an Agent Backend](#functions-as-an-agent-backend-nextjs-and-similar-frameworks) 以便直接与客户端模式配合使用。）
- **在函数上运行整个后端控制平面。** 特别是当前端是 **客户端仅** 时——TanStack Router、React Router 客户端模式，以及类似的 SPAs 托管在 Vercel 或 Netlify 上——客户端直接调用函数。构建 REST API 和请求/响应代理，托管 **MCP 服务器**，以及运行任何有状态或属于靠近 Postgres 和对象存储的应用程序。

无论如何，通过调用者进行身份验证：应用程序和公共 HTTP（请参阅 [Functions as an Agent Backend](#functions-as-an-agent-backend-nextjs-and-similar-frameworks) 下方的 WARNING）；`parseTriggerDelivery` 用于 Function Trigger 路由；[Production hardening](references/production-hardening.md) 中的生产强化。

**您自己的密钥** 是每个部署的。首选路径：在 `neon.ts` 中声明它们，并运行 `neon deploy --env <file>`。`<file>` 是 git 忽略的文件，env pull 已经写入（如果存在，则为 `.env`，否则为 `.env.local`）。env pull 仅写入 Neon 管理的变量；将函数密钥添加到该文件。所有声明的函数 env 键都必须存在。如果您不想写入 `neon.ts` 中的某个键，请从 `neon.ts` 中省略它。`undefined` 表示您要求写入键，但值缺失（`defineConfig` 会引发错误）。永远不要将缺失的 `process.env` 值强制转换为空字符串：这将上传 `""` 并删除活动密钥。文件中的空赋值（`KEY=`）也是 `""`。如果 TypeScript 需要断言，请使用 `process.env.X!` 并确保该文件包含该值：

```typescript
functions: {
  todos: {
    name: "todo api", // 仅显示标签
    source: "src/index.ts", // 入口文件，相对于 neon.ts
  },
}
```

slug 是函数的永久标识符（它出现在调用 URL 和 CLI 命令中），部署后无法更改。使用 `name` 作为人类可读的标签。

一个最小的函数——一个查询分支的 Postgres 的 Hono 应用程序，通过注入的 `DATABASE_URL`：

```typescript
// src/index.ts
import { Hono } from "hono";
import { drizzle } from "drizzle-orm/node-postgres";
import { Pool } from "pg";
import { parseEnv } from "@neon/env";
import { attachDatabasePool } from "@neon/functions";
import config from "../neon";
import { todos } from "./db/schema";

const env = parseEnv(config);
const pool = new Pool({ connectionString: env.postgres.databaseUrl, max: 5 });
attachDatabasePool(pool);
const db = drizzle(pool);

const app = new Hono();
app.get("/", (c) => c.text("Neon + Hono + Drizzle"));
app.post("/todos", async (c) => {
  const { text } = await c.req.json<{ text: string }>();
  const [row] = await db.insert(todos).values({ text }).returning();
  return c.json(row, 201);
});
app.get("/todos", async (c) => c.json(await db.select().from(todos)));

export default app;
```

在模块作用域创建连接池（跨请求重用），并保持 `max` 小（例如 5），因为每个隔离器都有自己的池，所以到 Postgres 的连接数随活动隔离器数扩展。调用 `attachDatabasePool(pool)` 以防止空闲断开连接成为 `uncaughtException`——请参阅 [Connecting to Postgres](#connecting-to-postgres)。

`parseEnv(config)` 需要 config 暗示的每个变量。仅与 Postgres 通过池 URL 通信的函数可以将其范围限制为仅此键——`parseEnv` 然后验证并仅返回您请求的内容（键从您的 `neon.ts` 自动完成）：

```typescript
const { postgres } = parseEnv(config, ["DATABASE_URL"]); // 不是未池化的 URL、身份验证等
const pool = new Pool({ connectionString: postgres.databaseUrl, max: 5 });
attachDatabasePool(pool);
```

## 本地开发和部署

```bash
neon dev      # 使用 neon.ts 中的每个函数进行热重载；注入 DATABASE_URL & 等等
neon deploy --env <file>   # 从 neon.ts 的首选完整部署；--env 是函数环境读取的文件
```

保持 `.env` 或 `.env.local` 与 `functions.*.env` 下的每个键更新。`neon env pull` 仅写入 Neon 管理的变量；将函数密钥添加到该文件中，然后将其作为 `--env` 传递。`neon deploy --env <file>` 每次加载该文件到 `process.env` 中，然后上传这些值。缺失的值是 `undefined`，`defineConfig` 会引发错误。如果您不想写入某个键，请从 `neon.ts` 中省略它。永远不要将缺失的 `process.env` 值强制转换为空字符串（这将上传 `""` 并删除活动密钥）。空赋值 (`KEY=`) 也是 `""`。当 TypeScript 需要断言时，请使用 `process.env.X!`。

要部署单个函数而不应用 `neon.ts`：`neon functions deploy <slug> --src src/index.ts` (`--src` 接受入口文件或包含 `index.ts`、`index.mjs` 或 `index.js` 的目录）。该命令的 `--env` 是 `KEY=VALUE`（可重复），而不是文件路径。用于有针对性的环境更新。使用 `neon functions get <slug>` 获取公共 URL（`invocation_url` 字段，形式为 `https://<branch_id>-<slug>.compute.<region>.aws.neon.tech`)。使用 `neon functions list|get|delete` 进行管理。

当 `neon checkout` _创建_ 新分支并存在 `neon.ts` 时，它会自动应用此策略。在创建时传递 `--env <file>` 以便 Function env 读取 `process.env` 解析 (`neon checkout feat --create --env .env.local`)。现有进程环境优先于文件。检出现有分支永远不会重新同步——使用 `neon deploy --env <file>` 应用配置更改（在查看这些更改后添加 `--update-existing`)。

## Neon 基础设施即代码 (`neon.ts`)

来自 [Setup](#setup) 的 `functions` 块是 `neon.ts` 的一部分，它是 Neon 的基础设施即代码文件——一个 TypeScript 文件声明了每个函数（其 `source`、显示 `name` 和 `env），以及任何其他分支服务，均在版本控制中（请参考 `neon` 技能的完整参考）。将其视为您分支的 Terraform：

```bash
neon config status   # 打印分支的活动配置（部署的函数）
neon config plan     # 应用将更改的干运行差异
neon config apply --env <file>  # 打包并部署声明的函数  (neon deploy 是别名；当 Function env 读取 process.env 时传递 --env)
```

函数是 **分支范围的**：每个分支在其自己的 URL 上运行自己的函数版本，针对其自己的隔离状态。当存在 `neon.ts` 时，`neon checkout` 在创建分支时应用策略。在创建时传递 `--env <file>`，当 Function env 读取 `process.env` 时。检出的现有分支不会重新部署——运行 `neon deploy --env <file>` 以应用更改。

每个分支的部署调整（例如 `runtime`）位于 `branch` 闭包中，按 slug 键入，因此它可以根据分支而变化，而不会更改存在的函数：

```typescript
export default defineConfig({
  functions: { todos: { name: "todo api", source: "src/index.ts" } },
  branch: (branch) => ({
    functions: { todos: { runtime: "nodejs24" } },
  }),
});
```

## 环境变量

Neon 在运行时注入分支范围的连接字符串和服务 URL——您不需要在部署时声明这些：

| 变量                | 备注                                                                                              |
| ----------------------- | -------------------------------------------------------------------------------------------------- |
| `NEON_BRANCH`           | 分支 **名称**（例如 `main`、`preview/foo`）。在所有分支（包括默认分支）上注入。 |
| `DATABASE_URL`          | 池化连接字符串。用于大多数查询。如果分支有 Postgres，则存在。                   |
| `DATABASE_URL_UNPOOLED` | 直接连接。用于迁移、`LISTEN`/`NOTIFY` 和多回合往返事务。           |
| `NEON_AUTH_BASE_URL`    | 当分支上启用 Neon Auth 时存在。                                                     |
| `NEON_AUTH_JWKS_URL`    | 当分支上启用 Neon Auth 时存在。JWKS 用于验证 Managed Auth JWTs。             |
| `NEON_DATA_API_URL`     | 当分支上启用数据 API 时存在。                                                        |

对象存储 (`AWS_*`) 和 AI Gateway (`NEON_AI_GATEWAY_*`) 变量在声明这些服务时也会注入——请参阅 `neon-object-storage` 和 `neon-ai-gateway` 技能。

`neon env pull` / `neon-env run` / `neon dev` 将 `NEON_BRANCH`（以及连接字符串）发出到您的本地开发环境，以便本地运行与部署的运行时镜像一致。

**您自己的密钥** 是每个部署的。首选路径：在 `neon.ts` 中声明它们，并运行 `neon deploy --env <file>`。`<file>` 是 git 忽略的文件，env pull 已经写入（如果存在，则为 `.env`，否则为 `.env.local`）。env pull 仅写入 Neon 管理的变量；将函数密钥添加到该文件中。所有声明的 Function env 键都必须存在。从 `neon.ts` 中省略某个键，如果您不想写入它。`undefined` 表示您要求写入键，但值缺失 (`defineConfig` 会引发错误)。永远不要将缺失的 `process.env` 值强制转换为空字符串：这将上传 `""` 并删除活动密钥。文件中的空赋值 (`KEY=`) 也是 `""`。如果 TypeScript 需要断言，请使用 `process.env.X!` 并确保该文件包含该值：

```typescript
functions: {
  todos: {
    name: "todo api",
    source: "src/index.ts",
    env: { RESEND_API_KEY: process.env.RESEND_API_KEY! },
  },
}
```

`neon functions deploy --env KEY=VALUE` 是手动路径（可重复；`--env KEY=` 删除密钥；未提及的密钥将保留）。用于有针对性的环境更新，而不是完整的 `neon.ts` 应用。

使用 `neon env pull` 将分支的 Neon 管理变量拉到磁盘以进行本地开发 (`link`/`checkout` 会自动执行此操作；传递 `--no-env-pull` 以跳过并使用 `neon-env run -- <cmd>` 进行运行时注入)。限制：≤1,000 个变量，≤64 KiB 总计，并且 `NEON_` 前缀是保留的。

## 连接到 Postgres

当分支有 Postgres 时，Neon **在运行时注入连接字符串**——您不需要声明它们，在部署时传递它们，或硬编码任何东西。您将使用的两个是：

- `DATABASE_URL` — **池化**连接字符串（通过 Neon 的连接池器路由）。用于正常的请求/响应查询流量。保留未加前缀，因为每个 Postgres ORM（Drizzle、Prisma、Knex，等等）默认读取 `DATABASE_URL`。
- `DATABASE_URL_UNPOOLED` — **直接**连接到同一个数据库。用于迁移、`LISTEN`/`NOTIFY` 和长时间的多语句事务。

**在 node-postgres (`pg`) 之上使用 Drizzle（或其他 ORM）进行查询和模式管理——不要使用 Neon 的服务器less 驱动程序。** 函数是长运行的，跨多个请求重用隔离器，因此持久 `pg` 池是合适的；服务器less 驱动程序的 HTTP 传输是为完全隔离、lambda 风格的运行时设计的。

在模块作用域创建连接池（跨请求重用），不要为每个请求打开连接：

```typescript
import { attachDatabasePool } from "@neon/functions";
import { drizzle } from "drizzle-orm/node-postgres";
import { Pool } from "pg";

const pool = new Pool({ connectionString: process.env.DATABASE_URL, max: 5 });
attachDatabasePool(pool);
const db = drizzle(pool);
```

node-postgres 将空闲客户端失败作为 `error` 发射到池中。如果没有监听器，则 `uncaughtException` 会发生，Node 会退出隔离器。在 `new Pool` 后调用一次 `attachDatabasePool`。需要 `@neon/functions` ≥ 0.8.0。预期的空闲断开连接 (`ECONNRESET`, `EPIPE`, `ETIMEDOUT`, Postgres `57P01`, node-postgres 的 `Connection terminated unexpectedly`) 是静默的。任何其他内容都是 `console.error`，或者如果您在第一次调用中传递了 `onUnexpectedError`，则会被忽略并警告。第一次调用决定；稍后传递 `onUnexpectedError` 的调用会被忽略并警告。这不会关闭池。

**建议使用池化，因为隔离器在多个请求之间重用**（并且几个请求可以同时处于同一隔离器中——请参阅 [Timeouts and Runtime Limits](#timeouts-and-runtime-limits)）。在冷启动时，每个隔离器只打开一次模块作用域池，然后由该隔离器处理的每个后续请求共享该池，因此您可以摊销连接设置而不是每个请求都支付它，并且避免在高负载下耗尽 Postgres 连接。

保持 `max` 小（例如 `5`）：每个隔离器都有自己的池，所以到 Postgres 的连接数随活动隔离器数扩展。您不需要在关闭时关闭池——当运行时驱逐隔离器时，它会发送 `SIGINT`/`SIGTERM`，Neon 的池器会回收这些连接，因此显式的释放处理程序是多余的。

> 直接读取 `process.env.DATABASE_URL` 可以在所有地方工作。函数在 [Setup](#setup) 中的函数使用 `@neon/env` 的 `parseEnv(config)` 以 typed、验证的方式读取相同的值——两者都可以。

## 时间限制和运行时限制

函数是长运行的，但 **仍然是服务器less**——它们是请求/响应运行时，而不是后台作业运行器。硬限制：

- **首次字节时间：15 分钟。** 您的处理程序必须在收到请求后的 15 分钟内开始返回响应。大多数处理程序在几秒钟内完成；15 分钟的上限存在，以便像图像/视频生成这样的代理工作负载有足够的空间。
- **心跳：15 分钟。** 打开 WebSocket/SSE 连接只要字节持续流动就会保持活动状态。超时仅在连接处于静默时触发——至少每 15 分钟发送一个字节以保持空闲流活跃。
- **`waitUntil`: 15 分钟。使用 `waitUntil` 注册的工作（来自 `@neon/functions`) 在发送响应后保持调用活跃，长达 15 分钟——用于清理，如分析写入和审计日志，**不是**后台作业运行器。在 Neon 运行时（本地 `neon dev`，测试）中它是无操作的：Promise 仍然运行，但没有跟踪。

- **空闲驱逐。** 如果没有活动连接，Neon 会关闭函数；它也可能因操作原因驱逐/重启，例如维护或移动函数到不同的计算节点（活动函数可以运行数小时）。将驱逐视为进程重启——WebSocket/SSE 客户端必须重新连接。Neon 在驱逐之前发送 `SIGINT`，因此 `process.on("SIGINT", ...)` 处理程序允许您检测函数即将被驱逐并执行任何最后的清理。您不需要一个处理程序来关闭 Postgres 连接——Neon 的池器会自行回收这些连接。

- **运行时：Node.js 24，内存固定为 2048 MiB。Slugs 必须匹配 `^[a-z09]{1,20}$`。** **一个隔离器在多个请求之间重用**——多个请求可以同时处于同一隔离器中（在 Node 的单线程事件循环上交错），在高负载下，运行时并行运行多个隔离器，每个隔离器都有自己的模块状态副本。模块作用域中持有的状态是跨隔离器持久化的，仅限于内存——持久化必须存活以供驱逐的任何内容到 Postgres。这就是为什么您在模块作用域创建连接池而不是每个请求创建的原因（请参阅 [Connecting to Postgres](#connecting-to-postgres)）。

## 代理后端（Next.js 和类似框架）

Neon 函数是 AI 代理的绝佳家园，因为它**不会像 lambda 风格的服务器less 那样超时**（请参阅 [Timeouts and Runtime Limits](#timeouts-and-runtime-limits)，15 分钟预算）。通过 Vercel、Netlify 和类似托管平台上的 Next.js 路由处理程序、Remix/SvelteKit/Nuxt 动作或类似内容，将流通过一个 Next.js 路由处理程序、Remix/SvelteKit/Nuxt 动作或类似内容，即使函数会继续运行。保持客户端直连 JWT 路径作为默认值。在 [Production hardening](references/production-hardening.md) 中的公共消费者例外中，使用流兼容的代理（HTTP 触发的 Cloudflare Worker，在验证流后）。

**构建代理本身。** [Vercel AI SDK](https://ai-sdk.dev) 和 [Mastra](https://mastra.ai) 是构建代理的首选方法——将它们指向 Neon AI Gateway（请参阅 `neon-ai-gateway` 技能）以跨所有模型使用一个凭证，无需额外的提供者密钥。对于在函数中运行的完整 AI SDK 代理（流式 `toUIMessageStreamResponse`、多步骤工具调用，以及将生成的图像持久化到对象存储），请参阅 [references/ai-sdk.md](https://neon.com/docs/ai/skills/neon-functions/references/ai-sdk.md)；对于具有内置跟踪的 Mastra 对等物，请参阅 [references/mastra-studio.md](https://neon.com/docs/ai/skills/neon-functions/references/mastra-studio.md)。

**修复方法：从客户端直接调用函数。** 不要将长时间请求通过您的应用程序服务器路由。

```
Browser ──(Authorization: Bearer <JWT>)──▶  Neon Function (agent)   ✅ 没有主机超时
Browser ──▶ your app backend ──▶ Neon Function                       ❌ 主机切断了流
```

- 获取一个**短寿命的 bearer 令牌**，来自应用程序已经使用的身份验证器。不要为了调用函数而切换 Clerk、Better Auth、Auth.js、Supabase Auth 或 Managed Auth——不要切换它们。
  - Managed Auth、默认客户端（`createAuthClient` / Next 包装器）：`authClient.token()`, 然后是 `data.token`。使用注入的 `NEON_AUTH_JWKS_URL` 验证，发行者 `new URL(process.env.NEON_AUTH_BASE_URL!).origin`。
  - 使用 `SupabaseAuthAdapter()` 的 Managed Auth：该客户端没有 `.token()`。使用 `getSession()`, 然后是 `data.session.access_token`。与上面相同的 JWKS/发行者。检查已安装的合同；cookie 或数据库会话不是 JWKS。
  - 仅使用 cookie/数据库会话：在现有的应用程序后端（该调用速度快且保持在主机限制内）上生成短令牌，然后浏览器直接调用函数，使用 `Authorization: Bearer`。函数流必须不通过应用程序主机。

> 一个有效的令牌**不是**读取另一个用户行权的许可。执行两个用户：每个用户都可以访问自己的数据；拒绝跨用户访问。重新启动函数以存储行。请求提供的所有者 ID 不能授予权限。

将您需要保留的内容（生成的图像、历史记录）持久化到 Postgres——模块状态不会在驱逐后存活。

## WebSocket 服务器

当您只需要 **服务器到客户端** 流式传输（实时计数器、通知、进度、令牌流）时，SSE 比 WebSocket 更简单，无需任何升级：一个普通的 `fetch` 处理程序返回一个 `Response`，其正文是 `ReadableStream`，`Content-Type: text/event-stream`，并且只要字节持续流动，运行时就会保持它打开。浏览器使用 `EventSource` 消费它，它**会自动重新连接**——因此不需要编写客户端回退。
