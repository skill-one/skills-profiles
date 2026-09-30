---
name: neon-functions
description: 长时间运行的服务器less Node.js HTTP函数部署到您的Neon分支上，自动注入DATABASE_URL，计算资源与您的数据相邻。适用于用户希望托管API、具有长时间流式响应的AI代理、WebSocket或服务器发送事件（SSE）服务器、webhook处理器、Discord机器人、MCP服务器，或任何在短lambda式服务器less函数中容易超时的请求/响应工作负载——并希望其与数据库分支。也适用于函数触发器：如cron或对象存储事件向函数POST请求。触发器包括"服务器less函数"、"部署API"、"长时间运行函数"、"流式代理"、"SSE服务器"、"WebSocket服务器"、"webhook处理器"、"MCP服务器"、"cron"、"函数触发器"、"计划函数"、"cron作业"、"对象存储触发器"、"上传时触发"、"在数据库旁边运行代码"、"不会超时的函数"、"函数日志"、"Neon函数"、"Neon计算"、"DDoS防护"、"速率限制"和"生产环境加固"。
---

**首先**：使用父级 `neon` 技能获取 Neon 概览、开始使用 Neon、Neon 开发最佳实践等内容。

如果未安装 `neon` 技能，请从 https://neon.com/docs/ai/skills/neon/SKILL.md 获取或使用以下命令安装：

```bash
neon skills -s neon -y
```

# Neon 函数

目前可在 `aws-us-east-2`、`aws-us-east-1`、`aws-eu-central-1` 和 `aws-ap-southeast-1` 区域使用。

Neon 函数是长时间运行的 Node.js HTTP 处理程序，部署在 Neon 分支上。每个函数都获得一个公共 HTTPS URL，在您的数据库所在的同一区域运行，如果分支有 Postgres，则会自动注入 `DATABASE_URL`。您可以通过相同的 Neon CLI、`neon.ts` 和 API 部署和管理它们。

使用此技能帮助用户定义、本地运行、部署和管理其数据库旁边的函数。提供已部署函数的调用 URL、可工作的本地 `neon dev` 循环，或来自官方 Neon 文档的精确答案。

## 使用场景

当工作负载是请求/响应处理程序，并且从保持活动状态和靠近数据中受益时，请使用 Neon 函数：

- **长时间运行的请求/响应流程，超出 lambda 风格限制**。 每个请求执行多个 LLM 调用和工具调用，或图像/视频生成，通常会超过传统无服务器函数的约 10–60 秒执行限制和短流窗口。Neon 函数是长时间运行的：处理程序只需在 15 分钟内开始响应，打开的流只要字节持续流动就会保持活动状态。这足以应对真实的代理工作负载。
- **无需附加 Redis 的状态流**。 由于函数跨请求保持活动状态，因此可以在进程内托管 SSE 端点或 WebSocket 服务器并保持连接打开——无需外部状态存储（Redis 等）来保持流的一致性。模块范围状态（一个 `pg` 池、一个内存计数器）在相同隔离的请求之间持续存在。
- **必须靠近 Postgres 的计算**。 函数在分支的数据库所在的同一区域运行，因此每个查询都没有跨区域往返。为您自动注入 `DATABASE_URL`。
- **与您的数据分支的后端**。 每个分支在其自己的 URL 上运行自己的函数版本，针对其自己的隔离状态（数据库和存储、网关）。预览部署、CI 和开发环境各自获得一个自包含的后端——将部署到子分支永远不会影响父分支。
- **从函数（或现有框架处理程序）查询 Postgres**。 优先选择 Data API。当应用程序已经使用 PostgREST 或 Supabase-js 数据库调用，或正在迁移该客户端时，使用 Data API。
- **Webhooks、机器人、响应后工作**。 分散到多个数据库写入的 Webhook 处理程序、Discord/WebSocket 机器人，以及通过 `waitUntil`（分析、审计日志）的“发射并遗忘”后续工作都适用。
- **定期 HTTP 工作**。 函数触发器按 cron（`type: "schedule"`）或在 Object Storage 中创建对象时（`type: "storage_object_created"`）向函数 POST。相同的 `fetch` 处理程序，相同的 15 分钟首次字节时间限制。参见 [函数触发器](#function-triggers)。

如果工作负载是纯静态网站，或必须运行在当前不受支持的区域（`aws-us-east-2`、`aws-us-east-1`、`aws-eu-central-1` 和 `aws-ap-southeast-1`）之外，则此工具尚不适用（参见 [超时和运行时限制](#timeouts-and-runtime-limits) 和 [可用性](#availability)）。

## 功能

- **长时间运行 & 无服务器** — 专为 WebSocket 服务器（参见 [WebSocket 服务器](#websocket-servers)）、SSE 端点（参见 [服务器发送事件 (SSE)](#server-sent-events-sse)）、长时间代理 HTTP 流和 API。空闲时仍可扩展到零。
- **Web 标准处理程序** — 任何具有 `fetch(request)` 方法的默认导出，返回 `Response`（兼容 Workers/WinterTC）。Hono 应用程序导出确切的形状，因此 `export default app` 直接适用。在 Node.js 24 上运行，因此所有 Node API 都可用。
- **靠近您的数据库** — 在分支的区域运行；当分支有 Postgres 时，自动注入 `DATABASE_URL`。
- **分支化** — 每个分支在其自己的 URL 上运行自己的函数版本，针对其自己的隔离状态。
- **相同的 CLI/API** — 通过 `neon`、`neon.ts` 或 Neon API 部署和管理。
- **函数触发器** — Neon 按 cron 或对象存储上传向函数 POST。参见 [函数触发器](#function-triggers)。

## 可用性

在设置任何内容之前，请检查此前提条件：Neon 函数目前可在 `aws-us-east-2`、`aws-us-east-1`、`aws-eu-central-1` 和 `aws-ap-southeast-1` 区域使用。确认用户的 Neon 项目位于这些区域之一。

## 架构：函数的适用位置

Neon（包括函数）是**后端原语，而不是全栈应用托管**。在 **Vercel**（或 Netlify 或其他前端/应用主机）上托管您的应用；函数是您的数据旁边长时间运行、有状态的后端切片。它们以两种方式与该平台组合：

- **将函数添加到全栈应用**。 您在 Vercel（或 Netlify）上的 Next.js / TanStack Start 应用拥有 UI、认证（Managed Auth、Better Auth、Clerk 或其他 IdP），并直接与 Lakebase Postgres 和 Object Storage 通信。将函数作为 Hono API 层添加为 Web 应用和其他客户端，或用于靠近数据的一个作业：Object Storage 上传、AI 代理、Discord 机器人、WebSocket 或 SSE 服务器。（参见 [函数作为代理后端](#functions-as-an-agent-backend-nextjs-and-similar-frameworks) 的客户端直接模式。）
- **在函数上运行整个后端控制平面**。 特别是当前端是**客户端仅**——TanStack Router、React Router 客户端模式、类似 SPAs 在 Vercel 或 Netlify 上托管——客户端直接调用函数。构建 REST API 和请求/响应代理，托管 **MCP 服务器**，以及运行任何有状态或靠近 Postgres 和 Object Storage 的内容。

无论如何，通过调用者进行身份验证：应用程序和公共 HTTP 使用 JWT 或 API 密钥（参见 [函数作为代理后端](#functions-as-an-agent-backend-nextjs-and-similar-frameworks) 下面的警告）；`parseTriggerDelivery` 用于函数触发器路由；生产硬化在 [生产硬化](references/production-hardening.md) 中。因为函数只是您的后端，所以您可以将组件在主机和 Neon 之间移动——当需要更多运行时将代理或有状态 WebSocket 服务器迁移到函数上，如果需要则可以移回。

优先选择查询 Postgres 的函数，或现有框架处理程序。当应用程序已经使用 PostgREST/Supabase-js 数据库调用或正在迁移该客户端时，使用 Data API。

## 生产硬化

在公开生产路由之前，请阅读 [生产硬化](references/production-hardening.md)。

按调用者选择：受信任的应用服务器、函数触发器或公共消费者。除非需要经过验证的流式传输兼容代理，否则请保持在客户端直接 JWT 路径上保持长时间浏览器流。身份验证拒绝应用程序工作；对原生 URL 的请求仍然会到达函数。

## 设置

函数在 `neon.ts` 中声明（参见 `neon` 技能的分支优先工作流和 `neon.ts` 基础知识）。添加 `@neon/config` 并在 `functions` 下声明函数，按 **slug** 键入：

```typescript
// neon.ts
import { defineConfig } from "@neon/config/v1";

export default defineConfig({
  functions: {
    todos: {
      // slug: ^[a-z0-9]{1,20}$ — 小写字母/数字，无连字符
      name: "todo api", // 仅显示标签
      source: "src/index.ts", // 入口文件，相对于 neon.ts
    },
  },
});
```

slug 是函数的永久身份（它出现在调用 URL 和 CLI 命令中），部署后不能更改。使用 `name` 用于人类可读的标签。

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

在模块作用域创建 `pg` 池（在相同隔离的请求之间重用），并将 `max` 保持较小（例如 5），因为每个隔离保持自己的池。调用 `attachDatabasePool(pool)` 以防止空闲断开连接成为 `uncaughtException`——参见 [连接到 Postgres](#connecting-to-postgres)。

`parseEnv(config)` 需要 config 暗示的**每个**变量。仅与通过池 URL 与 Postgres 通信的函数可以将其限制到此键——`parseEnv` 然后验证并只返回您请求的内容（键从您的 `neon.ts` 自动完成）：

```typescript
const { postgres } = parseEnv(config, ["DATABASE_URL"]); // 不是未池化的 URL、认证等
const pool = new Pool({ connectionString: postgres.databaseUrl, max: 5 });
attachDatabasePool(pool);
```

## 本地开发和部署

```bash
neon dev      # 使用热重载为 neon.ts 中的每个函数提供服务；注入 DATABASE_URL & 朋友
neon deploy --env <file>   # 从 neon.ts 的首选完整部署；--env 是函数环境读取的文件
```

将 `.env` 或 `.env.local` 更新为 `functions.*.env` 下**每个**键。`neon env pull` 仅写入 Neon 管理的变量；将函数密钥添加到此文件，然后将其作为 `--env` 传递。`neon deploy --env <file>` 每次加载该文件到 `process.env`，然后上传这些值。缺失的值是 `undefined` 并且 `defineConfig` 会抛出错误。如果您不想写入该键，请从 `neon.ts` 中省略该键。永远不要将缺失的 `process.env` 值强制转换为空字符串（这将上传 `""` 并删除活动键）。空赋值（`KEY=`）也是 `""`。当 TypeScript 需要断言时，使用 `process.env.X!` 并确保文件包含该值：

```typescript
functions: {
  todos: {
    name: "todo api",
    source: "src/index.ts",
    env: { RESEND_API_KEY: process.env.RESEND_API_KEY! },
  },
}
```

`neon functions deploy --env KEY=VALUE` 是手动路径（可重复；`--env KEY=` 删除键；未提及的键会保留）。用于有针对性的环境更新，而不是完整的 `neon.ts` 应用。

将函数密钥加载到 `neon env pull` 写入的同一文件中，然后 `neon deploy --env <file>`。使用 `neon env pull` 将分支的 Neon 管理的变量拉到磁盘上，用于本地开发（`link`/`checkout` 会自动执行此操作；传递 `--no-env-pull` 以跳过并使用 `neon-env run -- <cmd>` 进行运行时注入）。限制：≤1,000 个变量，≤64 KiB 总计，并且 `NEON_` 前缀是保留的。

## 连接到 Postgres

当分支包含 Postgres 时，Neon **在运行时注入连接字符串** — 你不需要声明它们，在部署时传递它们，或硬编码任何内容。你会使用的两个：

- `DATABASE_URL` — **连接池**连接字符串（通过 Neon 的连接池器路由）。用于常规的请求/响应查询流量。保持无前缀，因为每个 Postgres ORM（Drizzle、Prisma、Knex、…）默认读取 `DATABASE_URL`。
- `DATABASE_URL_UNPOOLED` — 到同一数据库的**直接**连接字符串。用于迁移、`LISTEN`/`NOTIFY` 和长时间的多语句事务。

**在 node-postgres (`pg`) 之上使用 Drizzle（或其他 ORM）进行查询和模式管理** — 而不是 Neon 的无服务器驱动程序。函数是长时间运行的，并在许多请求之间重用隔离，因此持久的 `pg` 池是合适的；无服务器驱动程序的 HTTP 传输是为完全隔离的 lambda 风格运行时设计的。

**在模块作用域中一次创建连接池，并在请求之间重用它** — 不要为每个请求打开一个连接：

```typescript
import { attachDatabasePool } from "@neon/functions";
import { drizzle } from "drizzle-orm/node-postgres";
import { Pool } from "pg";

const pool = new Pool({ connectionString: process.env.DATABASE_URL, max: 5 });
attachDatabasePool(pool);
const db = drizzle(pool);
```

node-postgres 将空闲客户端失败作为 `error` 发送到池。如果没有监听器，则会抛出 `uncaughtException`，并且 Node 退出隔离。在 `new Pool` 之后调用一次 `attachDatabasePool(pool)`。需要 `@neon/functions` ≥ 0.8.0。预期的空闲断开连接（`ECONNRESET`、`EPIPE`、`ETIMEDOUT`、Postgres `57P01`、node-postgres 的 `Connection terminated unexpectedly`）是静默的。其他任何内容都是 `console.error`，或者如果你在第一次调用中传递 `onUnexpectedError`，则是 `onUnexpectedError`。第一次调用决定；稍后传递 `onUnexpectedError` 的调用被忽略并发出警告。这不会关闭池。

**建议使用连接池，因为隔离在许多请求之间重用**（并且多个请求可以同时处于同一隔离中 — 见 [超时和运行时限制](#timeouts-and-runtime-limits)）。模块作用域的池在冷启动时打开一次，然后由隔离服务的每个后续请求共享，因此你可以摊销连接设置，而不是在每次请求上支付它，并且避免在高负载下耗尽 Postgres 连接。

保持 `max` 小（例如 `5`）：每个隔离保留自己的池，因此到 Postgres 的总连接数随活动隔离数扩展。你不需要在关闭时关闭池 — 当运行时驱逐隔离时，它会发送 `SIGINT`/`SIGTERM`，并且 Neon 的池器会为你回收这些连接，因此显式的排空处理程序是多余的。

> 直接读取 `process.env.DATABASE_URL` 在任何地方都有效。[设置](#setup) 中的函数使用 `@neon/env` 的 `parseEnv(config)` 以类型化、验证的方式读取相同的值 — 两者都可以。

## 超时和运行时限制

函数是长时间运行的，但**仍然是无服务器的** — 它们是请求/响应运行时，而不是后台作业运行器。硬限制：

- **首次字节时间：15 分钟。** 你的处理程序必须在接收到请求后的 15 分钟内**开始返回响应**。大多数处理程序在几秒钟内完成；15 分钟的上限是为了让代理工作负载（如图像/视频生成）有空间。
- **心跳：15 分钟。** 打开的 WebSocket/SSE 连接只要数据流动就会保持活动状态。超时仅在连接处于静默状态时触发 — 每隔 15 分钟至少发送一个字节以保持安静的流保持活动状态。
- **`waitUntil`：15 分钟。** 使用 `waitUntil`（来自 `@neon/functions`）注册的工作在发送响应后最多保持 15 分钟的调用活动 — 用于清理，如分析写入和审计日志，**不是**后台作业运行器。在 Neon 运行时之外（本地 `neon dev`、测试）它是无操作的：Promise 仍然运行，但不会被跟踪。
- **空闲驱逐。** 如果没有活动连接，Neon 会关闭函数；它还可能因操作原因驱逐/重启 — 例如维护，或移动函数到不同的计算节点（活动函数可以先运行数小时）。将驱逐视为进程重启 — WebSocket/SSE 客户端必须重新连接。Neon 在驱逐之前发送 `SIGINT`，因此 `process.on("SIGINT", ...)` 处理程序允许你检测函数即将被驱逐并运行任何最后时刻的清理。你不需要一个只是为了关闭 Postgres 连接 — Neon 的池器会自行回收这些连接。
- **运行时：Node.js 24，内存固定为 2048 MiB。** Slugs 必须匹配 `^[a-z0-9]{1,20}$`。**隔离在许多请求之间重用** — 多个请求可以同时处于同一隔离中（在 Node 的单线程事件循环上交错），并且在高负载下运行时并行运行多个隔离，每个隔离都有自己的模块状态副本。因此，模块作用域中持有的状态是按隔离（由隔离处理的每个请求共享）的，并且仅在内存中 — 持久化任何必须存活以度过驱逐的 Postgres 中的内容。这种重用正是为什么你在模块作用域中一次创建连接池而不是按请求创建（见 [连接到 Postgres](#connecting-to-postgres)）。

## 函数作为代理后端（Next.js 和类似框架）

Neon 函数是 AI 代理的绝佳家园，正是因为它**不会像 lambda 风格的无服务器那样超时**（15 分钟预算，见 [超时和运行时限制](#timeouts-and-runtime-limits)）。通过 Next.js 路由处理程序、Remix/SvelteKit/Nuxt 动作或类似托管在 Vercel、Netlify 等上的代理**在超出主机配置的持续时间或传输限制时切断流**，即使函数会继续运行。保持客户端直连 JWT 路径作为默认值。一个流兼容的代理（HTTP 触发的 Cloudflare Worker，在验证流之后）是 [生产硬化](references/production-hardening.md) 中的公共消费者例外。

**构建代理本身。** [Vercel AI SDK](https://ai-sdk.dev) 和 [Mastra](https://mastra.ai) 是构建代理的推荐方法 — 将它们指向 Neon AI Gateway（见 `neon-ai-gateway` 技能）以跨每个模型使用一个凭证，无需额外的提供者密钥。对于作为函数运行的完整 AI SDK 代理（流式传输 `toUIMessageStreamResponse`、多步骤工具调用紧邻 Postgres，并将生成的图像持久化到对象存储），见 [references/ai-sdk.md](https://neon.com/docs/ai/skills/neon-functions/references/ai-sdk.md)；对于具有内置跟踪的 Mastra 对等物，见 [references/mastra-studio.md](https://neon.com/docs/ai/skills/neon-functions/references/mastra-studio.md)。

**修复方法：从客户端直接调用函数。** 不要将长请求路由到你的应用服务器。

```
Browser ──(Authorization: Bearer <JWT>)──▶  Neon Function (agent)   ✅ 无主机超时
Browser ──▶ 你的应用后端 ──▶ Neon Function                       ❌ 主机切断流
```

- 从应用已经使用的身份获取**短寿命的 bearer 令牌**。不要为了调用函数而切换 Clerk、Better Auth、Auth.js、Supabase Auth 或 Managed Auth。
  - Managed Auth、默认客户端（`createAuthClient` / Next 包装器）：`authClient.token()`，然后 `data.token`。使用注入的 `NEON_AUTH_JWKS_URL` 和发行者 `new URL(process.env.NEON_AUTH_BASE_URL!).origin` 进行验证。
  - Managed Auth 使用 `SupabaseAuthAdapter()`：该客户端没有 `.token()`。使用 `getSession()`，然后 `data.session.access_token`。与上面相同的 JWKS/发行者。
  - 现有的 Better Auth / Auth.js / 其他已发布 JWKS 的签名者：使用该 JWKS URL、发行者和受众。检查安装的合同；cookie 或数据库会话不是 JWKS。
  - 仅 cookie/数据库会话：在现有的应用后端（该调用速度快且保持在主机限制内）铸造一个短令牌，然后浏览器直接调用函数，使用 `Authorization: Bearer`。函数流必须不通过应用主机。
- 将令牌交给客户端，例如使用 Vercel AI SDK：`new DefaultChatTransport({ api: NEON_FUNCTION_URL, fetch })`，其中 `fetch` 附加 `Authorization: Bearer <token>`。你的应用服务器永远不会处于长流的路径上。
- 添加 **CORS** 以便浏览器可以到达它（处理 `OPTIONS`，设置 `Access-Control-Allow-Origin`/`-Headers`）。

> [!WARNING]
> Neon 函数有一个**公共 HTTPS URL — 它可以被任何人访问。** 直接客户端→函数调用意味着没有应用后端在它前面来控制访问，所以**你必须自己验证函数**。验证 JWT 对调用者的 JWKS 进行验证，检查共享密钥 / API 密钥，或拒绝请求。永远不要部署未验证的代理。浏览器调用者使用短寿命的用户令牌。服务器或代理起源密钥（`X-Secret`）保留在服务器端；见 [生产硬化](references/production-hardening.md)。

```typescript
// src/index.ts — 在执行任何工作之前验证调用者
import { createRemoteJWKSet, jwtVerify } from "jose";

const jwks = createRemoteJWKSet(new URL(process.env.NEON_AUTH_JWKS_URL!));
const issuer = new URL(process.env.NEON_AUTH_BASE_URL!).origin;

export default {
  async fetch(request: Request) {
    if (request.method === "OPTIONS")
      return new Response(null, { status: 204, headers: cors(request) });

    const auth = request.headers.get("authorization");
    if (!auth?.toLowerCase().startsWith("bearer ")) {
      return new Response("Unauthorized", {
        status: 401,
        headers: cors(request),
      });
    }
    let userId: string;
    try {
      const { payload } = await jwtVerify(auth.slice(7), jwks, { issuer });
      if (!payload.sub) {
        return new Response("Unauthorized", {
          status: 401,
          headers: cors(request),
        });
      }
      userId = payload.sub;
    } catch {
      return new Response("Unauthorized", {
        status: 401,
        headers: cors(request),
      });
    }
    // 通过 userId 授权资源访问，然后在为该用户范围运行代理。
    // ... return result.toUIMessageStreamResponse({ headers: cors(request) })
  },
};
```

这段代码是 Managed Auth 验证。使用默认客户端的 `.token()`（`data.token`）铸造 bearer 令牌，或使用 `SupabaseAuthAdapter()` 的 `getSession()` 然后是 `data.session.access_token`。对于另一个身份，通过函数 `env` 传递该应用的 JWKS URL 和发行者（见 [环境变量](#environment-variables)），并且仅在令牌合同需要时才包含 `audience`。https://neon.com/docs/compute/functions/authentication.md

有效的令牌不是读取另一个用户行的权限。练习两个用户：每个用户都可以访问自己的数据；跨用户访问被拒绝。在重新启动函数以存储行后重复。请求提供的所有者 ID 不能授予权限。

将你需要保留的任何内容（生成的图像、历史记录）持久化到 Postgres — 模块状态不会在驱逐后存活。

## WebSocket 服务器

WebSocket 服务器是 Functions 工作负载的规范：一个长时间运行的处理程序在进程中保持连接打开，不需要外部状态存储来保持流一致。只要字节流动，连接就会保持活动状态（15 分钟心跳，见 [超时](#timeouts-and-runtime-limits)）。

**在 `fetch` 内部升级。** 从 [`@neon/functions`](https://www.npmjs.com/package/@neon/functions) 调用 `upgradeWebSocket(request)` 并返回它给出的响应。Hono 应用程序使用相同的原语通过 `@neon/functions/hono`（见 [Hono](#hono) 下面）。有一个入口点，并且没有 WebSocket 依赖项需要安装：

```typescript
import { upgradeWebSocket } from "@neon/functions";

export default {
  async fetch(req: Request): Promise<Response> {
    if (req.headers.get("upgrade")?.toLowerCase() !== "websocket") {
      return new Response("WebSocket 端点 — 使用 ?token=<jwt>连接", { status: 426 });
    }

    const { socket, response } = upgradeWebSocket(req);
    socket.addEventListener("message", (event) => socket.send(event.data));
    return response;
  },
};
```

`socket` 是标准的 [`WebSocket`](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)，所以 `addEventListener` 和 `onopen`/`onmessage`/`onclose`/`onerror` 属性都有效。当你得到它时，它仍然是 `CONNECTING` — 运行时只有在你的处理程序返回 `response` 后才会写入 `101`，并且连接才会打开。

三个重要的规则：

- **返回 `response` 不变。** `101` 不能作为普通的 `Response` 构建（fetch 规范限制构造的响应为 200–599），所以运行时会返回一个对象来携带挂起的升级。`clone()`，或者使用 `new Response(res.body, res)` 作为响应重写中间件重建它，会丢弃升级并失败请求。
- **通过返回普通的 `Response` 拒绝握手。** 在升级之前从 `fetch` 返回 `401`、`403` 或 `404` 来控制套接字。浏览器客户端无法读取握手被拒绝的原因；它只看到一个通用的连接失败，而不是你的状态或正文。拒绝让客户端出去，但通过单独的认证请求发送任何客户端需要的信息。
- **`binaryType` 默认为 `"arraybuffer"`**，而不是浏览器的 `"blob"`。`event.data` 对于文本帧是 `string`，对于二进制帧是 `ArrayBuffer`，所以根据 `typeof` 分支。

**带认证。** 浏览器不能在 WebSocket 上设置标头，所以使用 `?token=` 查询参数进行认证（与 [代理后端](#functions-as-an-agent-backend-nextjs-and-similar-frameworks) 相同方式验证：`jwtVerify` 对你的 JWKS）并在升级之前拒绝：

```typescript
// src/index.ts
import { upgradeWebSocket } from "@neon/functions";

const clients = new Set<WebSocket>();

export default {
  async fetch(request: Request): Promise<Response> {
    if (request.headers.get("upgrade")?.toLowerCase() !== "websocket") {
      return new Response("WebSocket 端点 — 使用 ?token=<jwt>连接");
    }

    const url = new URL(request.url);
    const identity = await verifyToken(url.searchParams.get("token"));
    if (!identity) return new Response("unauthorized", { status: 401 });

    const { socket, response } = upgradeWebSocket(request);
    clients.add(socket);
    socket.addEventListener("close", () => clients.delete(socket));
    socket.addEventListener("message", (event) => {
      if (typeof event.data !== "string") return;
      persist(identity.id, event.data); // 分发到每个隔离 — 见下面
    });
    return response;
  },
};
```

**子协议。** 将 `{ protocol }` 传递给客户端提供的协议之一；它在 `Sec-WebSocket-Protocol` 中回显，并作为 `socket.protocol` 暴露。选择客户端未提供的协议会抛出 `TypeError`。省略它则不会协商协议。也没有协商扩展 — `socket.extensions` 始终为 `""`，并且 `permessage-deflate` 不可用。

**Hono。** 使用 `@neon/functions/hono` 的 `upgradeWebSocket` — 与 Hono 自己的 WebSocket 辅助程序相同的原语，没有 `ws` 依赖项，也不是过时的 `@hono/node-ws`。认证是普通中间件；在 `next()` 之前控制升级请求：

```typescript
// src/index.ts
import { Hono } from "hono";
import { upgradeWebSocket } from "@neon/functions/hono";

const clients = new Set<WebSocket>();

const app = new Hono<{ Variables: { userId: string } }>();

app.use("/ws", async (c, next) => {
  const identity = await verifyToken(c.req.query("token"));
  if (!identity) return c.text("Unauthorized", 401);
  c.set("userId", identity.id);
  await next();
});

app.get(
  "/ws",
  upgradeWebSocket((c) => ({
    onOpen(_event, ws) {
      clients.add(ws.raw);
      ws.send("welcome");
    },
    onClose(_event, ws) {
      clients.delete(ws.raw);
    },
    onMessage(event, ws) {
      ws.send(`echo: ${event.data}`);
    },
  })),
);

export default app;
```

通过浏览器的 `wss://` URL 连接（来自 `neon functions get <slug>`），例如 `new WebSocket("wss://<branch>-<slug>.compute.<region>.aws.neon.tech/ws?token=<jwt>")`。在关闭时重新连接——隔离体是可被驱逐的，空闲连接可能在 15 分钟后被终止。

不要在升级路由上放置 `cors()`，并且在 `await next()` 之前不要读取 `c.res`，在它之后不要调用 `c.header()`——两者都会重建 `101` 并中断升级。参见 `@neon/functions` README 以获取完整中间件表。

### 心跳（保持套接字活跃）

连接仅在**字节流动时**保持打开：Neon 在 15 分钟后驱逐沉默的流（[超时和运行时限制](#timeouts-and-runtime-limits)），并且中间代理/负载均衡器通常要严格得多（通常为几十秒）。不要依赖应用程序足够多话——从服务器发送周期性保持活动状态的消息，以便套接字永远不会处于安静状态。

标准的 `WebSocket` 接口没有 `ping()`，因此发送客户端可以过滤掉的应用程序级消息：

```typescript
const HEARTBEAT_MS = 25_000; // 舒适地低于代理空闲超时

const beat = setInterval(() => {
  for (const socket of clients) {
    if (socket.readyState === socket.OPEN) socket.send('{"type":"ping"}');
  }
}, HEARTBEAT_MS);
beat.unref?.();
```

客户端在处理消息时跳过这些。这里没有协议级快捷方式：来自 `upgradeWebSocket` 的标准 `WebSocket` 没有 `ping()`，并且浏览器无法从 JavaScript 发送 ping 帧因此应用程序级消息是浏览器客户端唯一可用的保持活动状态方式。（Node `ws` 客户端可以发送 ping 帧，并且服务器自动回复 pong，但浏览器不能。）

### 在隔离体之间同步客户端（不要跳过此部分）

在负载下，运行时并行运行**多个隔离体，每个隔离体都有自己的模块状态副本**——因此每个隔离体都有自己的 `clients` 集合。仅向该本地集合广播意味着隔离体 A 上的客户端永远不会看到隔离体 B 产生的事件，并且信息流会无声地分裂。很容易错过：`neon dev` 运行单个进程（一个隔离体），因此进程内广播在本地始终看起来很好，但在生产环境中会中断，其中并发连接分布在多个隔离体上。

模块状态无论如何都不会在驱逐后存活，因此**Postgres 是共享的真相来源**。选择一个分发的策略。在下面的每个片段中，`pool` 是一个池化的 `pg` 客户端，`clients` 是此隔离体的活跃连接的 `Set`。

**1. 投票 Postgres——默认的，并且是保持 Scale to Zero 的唯一选项。** 每个隔离体在短间隔内重新读取共享状态（或游标后的行）并将更改推送到它自己的客户端。每个隔离体每滴答一次（不是每个客户端）一个查询，当隔离体没有客户端时则不发送查询——因此空闲计算仍然暂停。

```typescript
let lastId = "0"; // 大整数 ID，因此是字符串
let polling = false;

async function poll() {
  if (polling || clients.size === 0) return; // 防止重叠；没有客户端→没有查询→计算可以缩放到零
  polling = true;
  try {
    const { rows } = await pool.query(
      "SELECT id, payload FROM events WHERE id > $1 ORDER BY id",
      [lastId],
    );
    for (const { id, payload } of rows) {
      lastId = id;
      for (const socket of clients) {
        if (socket.readyState === socket.OPEN) socket.send(payload);
      }
    }
  } catch (err) {
    console.error("[poll]", err);
  } finally {
    polling = false;
  }
}

// 从最新的 ID 开始，以便新的隔离体只发送新行，而不是整个表，然后投票。
pool
  .query("SELECT coalesce(max(id), 0)::text AS id FROM events")
  .then((seed) => {
    lastId = seed.rows[0].id;
  })
  .catch((err) => console.error("[seed]", err))
  .finally(() => setInterval(poll, 1000).unref?.());
```

- **延迟**：最多为间隔（~1s）——适用于计数器、聊天和仪表板。
- **扩展**：数据库负载随着活跃隔离体的数量增长，而不是客户端。保持游标在索引的 `serial`/`bigserial` PK 上，并且间隔合理。
- **缩放到零**：✅ 保留——当没有客户端连接时投票停止，因此计算在其正常计时器上暂停。
- **顺序**：`WHERE id > cursor` 可以跳过序列中提交顺序的行：一个事务使用了较低的 ID 但在较高的一个之后提交，该事务已经在游标之后，因此投票永远不会返回它。对于广播信息流，偶尔丢失通常是没问题的；当你需要每一行时，使用 `LISTEN`/`NOTIFY` 或按 `created_at` 投票，并使用小的重叠窗口并按 ID 去重。

**2. `LISTEN`/`NOTIFY`——最低延迟，但需要禁用 Scale to Zero。** 每个隔离体在一个专用的**非池化**连接上 `LISTEN` 一个通道；广播是 `NOTIFY`，因此每个隔离体（包括发送者）都重新推送其套接字。近实时——但监听器持有一个空闲连接，该连接**不被视为活跃**，因此 [Scale to Zero](https://neon.com/docs/introduction/scale-to-zero) 暂停计算并丢弃它，无声地杀死信息流。仅在**始终开启**的计算上使用它（Scale to Zero 禁用——付费计划设置）。

```typescript
import { attachDatabasePool } from "@neon/functions";
import { Pool, Client } from "pg";

const pool = new Pool({ connectionString: process.env.DATABASE_URL, max: 5 });
attachDatabasePool(pool);
const CHANNEL = "chat_events";

// 每个隔离体一个专用的 DIRECT 连接，只是为了接收事件。
// 使用 DATABASE_URL_UNPOOLED——LISTEN 需要一个真实的会话，而不是池化的一个。
// 不要在这里调用 attachDatabasePool：它会静音杀死信息流的空闲丢弃。
// 错误监听器保持进程活跃；在生产中（这里省略）在错误时重新连接客户端。
const listener = new Client({
  connectionString: process.env.DATABASE_URL_UNPOOLED,
});
listener.on("error", (err) => {
  console.error(err);
});
listener.connect().then(() => listener.query(`LISTEN ${CHANNEL}`));
listener.on("notification", (msg) => {
  if (!msg.payload) return;
  for (const socket of clients) {
    if (socket.readyState === socket.OPEN) socket.send(msg.payload);
  }
});

// 通过池发送 NOTIFY 进行广播——每个隔离体的监听器都会触发。
function broadcast(event: unknown) {
  return pool.query("SELECT pg_notify($1, $2)", [
    CHANNEL,
    JSON.stringify(event),
  ]);
}
```

**3. 外部 pub/sub（例如 [Upstash](https://upstash.com) Redis）——在扩展方面最佳。** 对于高分发，大量连接数下的亚秒级延迟，或跨区域，通过专用代理发布/订阅。最高吞吐量，并且它不会触及 Postgres 或阻塞 Scale to Zero——代价是运行另一个服务。

**经验法则**：从**投票**开始（与 Scale to Zero 兼容，无需额外基础设施）；仅在始终开启的计算上需要亚秒级延迟时切换到 `LISTEN`/`NOTIFY`；当分发超出 Postgres 时转向 Redis。

### 客户端必须重新连接

空闲函数被驱逐（并且为操作原因隔离体重新启动），因此客户端的套接字**会**掉落——将重新连接视为正常，而不是异常。使用指数退避重新连接，限制，并且**在每次尝试时重新生成一个新鲜令牌**（令牌是短命的，因此过时的令牌会失败 `upgrade` 认证检查）：

```typescript
let closed = false,
  retry = 0,
  timer: ReturnType<typeof setTimeout>;

async function connect() {
  if (closed) return;
  const token = await getToken(); // 每次尝试重新生成；短命
  const ws = new WebSocket(`${WS_URL}?token=${encodeURIComponent(token)}`);
  ws.onopen = () => {
    retry = 0; // 成功时重置退避
  };
  ws.onmessage = (e) => {
    /* 应用事件 */
  };
  ws.onclose = () => {
    if (!closed)
      timer = setTimeout(connect, Math.min(1000 * 2 ** retry++, 15000));
  };
  ws.onerror = () => ws.close(); // 让 onclose 驱动重试
}
connect();
```

一起——`fetch` 内部的 `upgradeWebSocket`，`?token=` 上的 JWT 认证，跨隔离体分发，以及客户端退避——这些组合成一个完整的实时聊天后端在单个函数上。

## 服务器发送事件 (SSE)

当您只需要**服务器→客户端**流（实时计数器、通知、进度、令牌流）时，SSE 比 WebSocket 更简单，并且无需升级：一个普通的 `fetch` 处理器返回一个 `Response`，其正文是一个 `ReadableStream`，`Content-Type: text/event-stream`，并且运行时在字节流动时保持其打开。浏览器使用 `EventSource` 消费它，它**自行重新连接**——因此无需编写客户端退避。

```typescript
// src/index.ts — 最小的 SSE 端点
const encoder = new TextEncoder();
export default {
  fetch: () => {
    let t: ReturnType<typeof setInterval>;
    return new Response(
      new ReadableStream<Uint8Array>({
        start(controller) {
          controller.enqueue(encoder.encode("data: hello\n\n"));
          t = setInterval(
            () => controller.enqueue(encoder.encode(": ping\n\n")),
            25_000,
          );
        },
        cancel() {
          clearInterval(t); // 客户端断开连接时触发
        },
      }),
      {
        headers: {
          "Content-Type": "text/event-stream",
          "Cache-Control": "no-cache, no-transform",
        },
      },
    );
  },
};
```

WebSocket 的相同规则适用。**心跳**：流仅在字节流动时保持打开——Neon 的窗口是 15 分钟（[超时和运行时限制](#timeouts-and-runtime-limits)），但代理通常要严格得多，因此每隔 ~25–30 秒（如上所示）发出 `: ping\n\n` 注释以保持空闲流不被丢弃。在 Postgres 中保持状态，并使用 [同步策略](#keeping-clients-in-sync-across-isolates-do-not-skip-this)（持有一个流控制器的 `Set` 并向每个 `enqueue`）跨隔离体分发。`EventSource` 是 GET-only 并且不能设置标头，因此使用 `?token=` 查询参数或 cookie 进行认证，就像 WebSocket 情况一样。[references/sse.md](https://neon.com/docs/ai/skills/neon-functions/references/sse.md) 有完整模式——Hono 变体，跨隔离体分发，线格式，客户端和注意事项。

## 函数触发器

函数触发器在 cron（`schedule`）或当对象在对象存储中创建时（`storage_object_created`）向您的函数 POST JSON。在 `neon.ts` 中声明它，使用 `neon deploy` 应用，并使用 `parseTriggerDelivery`（`@neon/functions/triggers`）对交付进行认证。`parseTrigger`（Hono）和 `parseTriggerInvocation` 保持仅限计划。优先选择 `neon.ts`；CLI 和 Neon MCP 触发器工具（`list_triggers`，`create_trigger`，…）是备用。

触发器路由不得需要用户 JWT 或 `X-Secret`；Neon 未经这些直接 POST 到原生 URL。生产调用者形状：[references/production-hardening.md](references/production-hardening.md)。完整字段列表，CLI，MCP，负载，继承以及两种处理形状：[references/function-triggers.md](references/function-triggers.md)。

## MCP 服务器

MCP（模型上下文协议）服务器是函数的自然工作负载：一个长时间运行的 HTTP 处理器，它向 AI 客户端（Cursor，Claude，ChatGPT，代理）公开工具，这些工具紧挨着计算读取和写入分支的 Postgres。MCP 的**流式 HTTP 传输**是一个单一的端点（通常为 `/mcp`）上的普通 `POST`/`GET`，因此它映射到函数的 `fetch` 处理器，无需 `upgrade` 方法或额外协议。

最简单的托管是一个使用官方 [`@modelcontextprotocol/sdk`](https://github.com/modelcontextprotocol/typescript-sdk) 和 [`@hono/mcp`](https://github.com/honojs/middleware/tree/main/packages/mcp) 的 Hono 应用，它将传输桥接到路由。构建服务器，注册其工具，并在模块作用域一次创建传输，然后将每个 `/mcp` 请求交给它：

```typescript
const transport = new StreamableHTTPTransport();
app.all("/mcp", async (c) => {
  if (!mcpServer.isConnected()) await mcpServer.connect(transport);
  return transport.handleRequest(c);
});
```

因为函数的 URL 是公开的，**在连接传输之前进行认证**——[更好的认证](https://better-auth.com) 涵盖 OAuth（其 MCP 插件使您的应用程序成为授权服务器，因此第三方客户端根据 MCP 规范自我认证）和更简单的 API-key/会话-JWT 检查用于您自己的调用者。公共消费者边缘保护：[references/production-hardening.md](references/production-hardening.md)。[references/mcp.md](https://neon.com/docs/ai/skills/neon-functions/references/mcp.md) 有完整模式——具有 Postgres 支持的工具的服务器，两种 Better Auth 认证选项，以及使用 `mcporter` / `add-mcp` 进行测试。
