---
name: sentry-node-sdk
description: Node.js、Bun 和 Deno 的完整 Sentry SDK 配置。当被要求“为 Node.js 添加 Sentry”、“为 Bun 添加 Sentry”、“为 Deno 添加 Sentry”、“安装 @sentry/node”、“@sentry/bun”或“@sentry/deno”时使用，或为服务器端 JavaScript/TypeScript 运行时配置错误监控、追踪、日志记录、性能分析、指标、定时任务或 AI 监控。
---

> [所有技能](../../SKILL_TREE.md) > [SDK 安装](../sentry-sdk-setup/SKILL.md) > Node.js / Bun / Deno SDK

# Sentry Node.js / Bun / Deno SDK

一个有主见的向导，它会扫描你的项目，并指导你完成 Sentry 在服务器端 JavaScript 和 TypeScript 运行时（Node.js、Bun 和 Deno）的完整设置。

## 何时调用此技能

- 用户询问如何将 Sentry 添加到 Node.js、Bun 或 Deno
- 用户想要安装或配置 `@sentry/node`、`@sentry/bun` 或 `@sentry/deno`
- 用户想要为后端 JS/TS 应用添加错误监控、追踪、日志记录、性能分析、计划任务、指标或 AI 监控
- 用户询问关于 `instrument.js`、`--import ./instrument.mjs`、`bun --preload` 或 `npm:@sentry/deno`
- 用户想要监控 Express、Fastify、Koa、Hapi、Connect、Bun.serve() 或 Deno.serve()

> **NestJS？** 使用 [`sentry-nestjs-sdk`](../sentry-nestjs-sdk/SKILL.md) 而不是它 — 它使用 `@sentry/nestjs` 与 NestJS 原生装饰器和过滤器。
> **Next.js？** 使用 [`sentry-nextjs-sdk`](../sentry-nextjs-sdk/SKILL.md) 而不是它 — 它处理三运行时架构（浏览器、服务器、边缘）。

> **注意：** SDK 版本反映的是编写文档时当前的 Sentry 文档（`@sentry/node` ≥10.42.0、`@sentry/bun` ≥10.42.0、`@sentry/deno` ≥10.42.0）。
> 在实施之前，请始终参考 [docs.sentry.io/platforms/javascript/guides/node/](https://docs.sentry.io/platforms/javascript/guides/node/)。

---

## 第一阶段：检测

运行以下命令以识别运行时、框架和现有的 Sentry 设置：

```bash
# 检测运行时
bun --version 2>/dev/null && echo "Bun 检测到"
deno --version 2>/dev/null && echo "Deno 检测到"
node --version 2>/dev/null && echo "Node.js 检测到"

# 检测现有的 Sentry 包
cat package.json 2>/dev/null | grep -E '"@sentry/'
cat deno.json deno.jsonc 2>/dev/null | grep -i sentry

# 检测 Node.js 框架
cat package.json 2>/dev/null | grep -E '"express"|"fastify"|"@hapi/hapi"|"koa"|"@nestjs/core"|"connect"'

# 检测 Bun 特定框架
cat package.json 2>/dev/null | grep -E '"elysia"|"hono"'

# 检测 Deno 框架（deno.json 导入）
cat deno.json deno.jsonc 2>/dev/null | grep -E '"oak"|"hono"|"fresh"'

# 检测模块系统（Node.js）
cat package.json 2>/dev/null | grep '"type"'
ls *.mjs *.cjs 2>/dev/null | head -5

# 检测现有的 instrument 文件
ls instrument.js instrument.mjs instrument.ts instrument.cjs 2>/dev/null

# 检测日志库
cat package.json 2>/dev/null | grep -E '"winston"|"pino"|"bunyan"'

# 检测计划任务/调度
cat package.json 2>/dev/null | grep -E '"node-cron"|"cron"|"agenda"|"bull"|"bullmq"'

# 检测 AI / LLM 使用
cat package.json 2>/dev/null | grep -E '"openai"|"@anthropic-ai"|"@langchain"|"@vercel/ai"|"@google/generative-ai"'

# 检测 OpenTelemetry 追踪
cat package.json 2>/dev/null | grep -E '"@opentelemetry/sdk-node"|"@opentelemetry/sdk-trace-node"|"@opentelemetry/sdk-trace-base"'
grep -rn "NodeTracerProvider\|trace\.getTracer\|startActiveSpan" \
  --include="*.ts" --include="*.js" --include="*.mjs" 2>/dev/null | head -5

# 检查配套前端
ls frontend/ web/ client/ ui/ 2>/dev/null
cat package.json 2>/dev/null | grep -E '"react"|"vue"|"svelte"|"next"'
```

**需要确定的内容：**

| 问题 | 影响 |
|----------|--------|
| 哪个运行时？（Node.js / Bun / Deno） | 确定包、初始化模式和预加载标志 |
| Node.js：ESM 还是 CJS？ | ESM 需要 `--import ./instrument.mjs`；CJS 使用 `require("./instrument")` |
| 检测到框架吗？ | 确定注册哪个错误处理器 |
| 已经安装 `@sentry/*` 吗？ | 跳过安装，直接进行功能配置 |
| `instrument.js` / `instrument.mjs` 已经存在吗？ | 合并到它而不是覆盖 |
| 检测到日志库吗？ | 推荐 Sentry 日志 |
| 检测到计划任务/调度器吗？ | 推荐 Crons 监控 |
| 检测到 AI 库吗？ | 推荐 AI 监控 |
| 检测到 OpenTelemetry 追踪吗？ | 使用 OTLP 路径而不是原生追踪 |
| 检测到配套前端吗？ | 触发第四阶段的跨链接 |

---

## 第二阶段：推荐

根据你发现的内容提出具体的建议，不要问开放式问题 — 直接提出建议：

**从 OTel 检测路由：**
- **检测到 OTel 追踪**（`package.json` 中的 `@opentelemetry/sdk-node` 或 `@opentelemetry/sdk-trace-node`，或源代码中的 `NodeTracerProvider`）→ 使用 OTLP 路径：通过 `@sentry/node-core/light` 的 `otlpIntegration()`；不要设置 `tracesSampleRate`；Sentry 会自动将错误链接到 OTel 追踪

**推荐（核心覆盖）：**
- ✅ **错误监控** — 总是；捕获未处理的异常、Promise 拒绝和框架错误
- ✅ **追踪** — 通过 OpenTelemetry 自动化 HTTP、数据库和队列追踪

**可选（增强可观察性）：**
- ⚡ **日志记录** — 通过 `Sentry.logger.*` 的结构化日志；当需要 `winston`/`pino`/`bunyan` 或日志搜索时推荐
- ⚡ **性能分析** — 持续 CPU 性能分析（仅 Node.js；Bun 或 Deno 上不可用）；**使用 OTLP 路径时不可用**
- ⚡ **AI 监控** — OpenAI、Anthropic、LangChain、Vercel AI SDK；当检测到 AI/LLM 调用时推荐
- ⚡ **计划任务** — 检测遗漏或失败的定时任务；当检测到 node-cron、Bull 或 Agenda 时推荐
- ⚡ **指标** — 自定义计数器、指标、分布；当需要自定义 KPI 时推荐
- ⚡ **运行时指标** — 自动收集内存、CPU 和事件循环指标；`nodeRuntimeMetricsIntegration()`（Node.js）/ `bunRuntimeMetricsIntegration()`（Bun）

**推荐逻辑：**

| 功能 | 当...推荐 |
|---------|------------------|
| 错误监控 | **始终** — 不可协商的基线 |
| OTLP 集成 | 检测到 OTel 追踪 — **替换** 原生追踪 |
| 追踪 | **始终用于服务器应用** — HTTP 跨度和数据库跨度非常有价值；**如果检测到 OTel 追踪则跳过** |
| 日志记录 | 应用使用 winston、pino、bunyan 或需要日志到追踪的关联 |
| 性能分析 | **仅 Node.js** — 性能关键服务；原生插件兼容；**使用 OTLP 追踪时跳过**（需要 `tracesSampleRate`，与 OTLP 不兼容） |
| AI 监控 | 应用调用 OpenAI、Anthropic、LangChain、Vercel AI 或 Google GenAI |
| 计划任务 | 应用使用 node-cron、Bull、BullMQ、Agenda 或任何定时任务模式 |
| 指标 | 应用需要自定义计数器、指标或直方图 |
| 运行时指标 | 任何想要自动内存/CPU/事件循环可见性的 Node.js 或 Bun 服务 |

**检测到 OTel 追踪：***"我在项目中看到 OpenTelemetry 追踪。我推荐 Sentry 的 OTLP 集成用于追踪（通过您现有的 OTel 设置）+ 错误监控 + Sentry 日志 [如果适用，则添加指标/计划任务/AI 监控]。要继续吗？*"

**未检测到 OTel：***"我推荐设置错误监控 + 追踪。您想要我添加日志记录或性能分析吗？*"

---

## 第三阶段：指导

### 运行时：Node.js

#### 选项 1：向导（推荐用于 Node.js）

> **您需要自己运行** — 向导会打开浏览器进行登录，并需要交互式输入，代理无法处理。将以下内容复制粘贴到您的终端：
>
> ```
> npx @sentry/wizard@latest -i node
> ```
>
> 它处理登录、组织/项目选择、SDK 安装、`instrument.js` 创建和 `package.json` 脚本更新。
>
> **完成后，回来并跳转到 [验证](#verification)。**

如果用户跳过向导，请继续执行下面（手动设置）。

---

#### 选项 2：手动设置 — Node.js

##### 安装

```bash
npm install @sentry/node --save
# 或
yarn add @sentry/node
# 或
pnpm add @sentry/node
```

##### 创建 Instrument 文件

**CommonJS (`instrument.js`):**

```javascript
// instrument.js — 必须在所有其他模块之前加载
const Sentry = require("@sentry/node");

Sentry.init({
  dsn: process.env.SENTRY_DSN ?? "___DSN___",

  dataCollection: {
    // 要禁用发送用户数据和 HTTP 正文，请取消以下行的注释。更多信息请访问：
    // https://docs.sentry.io/platforms/javascript/guides/node/configuration/options/#dataCollection
    // userInfo: false,
    // httpBodies: [],
  },

  // 开发环境 100%，生产环境较低
  tracesSampleRate: process.env.NODE_ENV === "development" ? 1.0 : 0.1,

  // 在堆栈帧中捕获局部变量的值
  includeLocalVariables: true,

  enableLogs: true,
});
```

**ESM (`instrument.mjs`):**

```javascript
// instrument.mjs — 在加载任何其他模块之前加载
import * as Sentry from "@sentry/node";

Sentry.init({
  dsn: process.env.SENTRY_DSN ?? "___DSN___",

  dataCollection: {
    // 要禁用发送用户数据和 HTTP 正文，请取消以下行的注释。更多信息请访问：
    // https://docs.sentry.io/platforms/javascript/guides/node/configuration/options/#dataCollection
    // userInfo: false,
    // httpBodies: [],
  },
  tracesSampleRate: process.env.NODE_ENV === "development" ? 1.0 : 0.1,
  includeLocalVariables: true,
  enableLogs: true,
});
```

##### 使用 Sentry 首先加载启动您的应用

**CommonJS** — 将 `require("./instrument")` 作为您的入口文件的第一行添加：

```javascript
// app.js
require("./instrument"); // 必须是第一行

const express = require("express");
// ... 应用其余部分
```

**ESM** — 使用 `--import` 标志，以便 Sentry 在所有其他模块之前加载（需要 Node.js 18.19.0+）：

```bash
node --import ./instrument.mjs app.mjs
```

添加到 `package.json` 脚本：

```json
{
  "scripts": {
    "start": "node --import ./instrument.mjs server.mjs",
    "dev": "node --import ./instrument.mjs --watch server.mjs"
  }
}
```

或通过环境变量（用于包装现有的启动命令）：

```bash
NODE_OPTIONS="--import ./instrument.mjs" npm start
```

##### 框架错误处理器

在所有路由之后注册 Sentry 错误处理器，以便它可以捕获框架错误：

**Express:**

```javascript
const express = require("express");
const Sentry = require("@sentry/node");

const app = express();

// ... 您的路由

// 添加到所有路由之后 — 默认捕获 5xx 错误
Sentry.setupExpressErrorHandler(app);

// 可选：捕获 4xx 错误
// Sentry.setupExpressErrorHandler(app, {
//   shouldHandleError(error) { return error.status >= 400; },
// });

app.listen(3000);
```

**Fastify:**

```javascript
const Fastify = require("fastify");
const Sentry = require("@sentry/node");

const fastify = Fastify();

// 添加到路由之前（与 Express 不同！）
Sentry.setupFastifyErrorHandler(fastify);

// ... 您的路由

await fastify.listen({ port: 3000 });
```

**Koa:**

```javascript
const Koa = require("koa");
const Sentry = require("@sentry/node");

const app = new Koa();

// 作为第一个中间件添加（捕获后续中间件抛出的错误）
Sentry.setupKoaErrorHandler(app);

// ... 您的其他中间件和路由

app.listen(3000);
```

**Hapi（异步 — 必须等待）:**

```javascript
const Hapi = require("@hapi/hapi");
const Sentry = require("@sentry/node");

const server = Hapi.server({ port: 3000 });

// ... 您的路由

// 必须等待 — Hapi 注册是异步的
await Sentry.setupHapiErrorHandler(server);

await server.start();
```

**Connect:**

```javascript
const connect = require("connect");
const Sentry = require("@sentry/node");

const app = connect();

// 添加到路由之前（与 Fastify 和 Koa 类似）
Sentry.setupConnectErrorHandler(app);

// ... 您的中间件和路由

require("http").createServer(app).listen(3000);
```

**NestJS** — 它有自己的专用技能，提供完整覆盖：

> **使用 [`sentry-nestjs-sdk`](../sentry-nestjs-sdk/SKILL.md) 技能。**
> NestJS 使用单独的包 (`@sentry/nestjs`) 与 NestJS 原生结构：
> `SentryModule.forRoot()`、`SentryGlobalFilter`、`@SentryTraced`、`@SentryCron` 装饰器，
> 以及 GraphQL/微服务支持。加载该技能以完成 NestJS 设置。

**Vanilla Node.js `http` 模块** — 手动包装请求处理器：

```javascript
const http = require("http");
const Sentry = require("@sentry/node");

const server = http.createServer((req, res) => {
  Sentry.withIsolationScope(() => {
    try {
      // 您的处理器
      res.end("OK");
    } catch (err) {
      Sentry.captureException(err);
      res.writeHead(500);
      res.end("Internal Server Error");
    }
  });
});

server.listen(3000);
```

**框架错误处理器摘要：**

| 框架 | 函数 | 位置 | 异步？ |
|-----------|----------|-----------|--------|
| Express | `setupExpressErrorHandler(app)` | **之后**所有路由 | No |
| Fastify | `setupFastifyErrorHandler(fastify)` | **之前**路由 | No |
| Koa | `setupKoaErrorHandler(app)` | **第一个**中间件 | No |
| Hapi | `setupHapiErrorHandler(server)` | 在 `server.start()` 之前 | **Yes** |
| Connect | `setupConnectErrorHandler(app)` | **之前**路由 | No |
| NestJS | → 使用 [`sentry-nestjs-sdk`](../sentry-nestjs-sdk/SKILL.md) | 专用技能 | — |

---

### 运行时：Bun

> **Bun 没有向导可用。** 仅支持手动设置。

#### 安装

```bash
bun add @sentry/bun
```

#### 创建 `instrument.ts`（或 `instrument.js`）

```typescript
// instrument.ts
import * as Sentry from "@sentry/bun";

Sentry.init({
  dsn: process.env.SENTRY_DSN ?? "___DSN___",

  dataCollection: {
    // 要禁用发送用户数据和 HTTP 正文，请取消以下行的注释。更多信息请访问：
    // https://docs.sentry.io/platforms/javascript/guides/node/configuration/options/#dataCollection
    // userInfo: false,
    // httpBodies: [],
  },
  tracesSampleRate: process.env.NODE_ENV === "development" ? 1.0 : 0.1,
  enableLogs: true,
});
```

#### 使用 `--preload` 启动您的应用

```bash
bun --preload ./instrument.ts server.ts
```

添加到 `package.json`：

```json
{
  "scripts": {
    "start": "bun --preload ./instrument.ts server.ts",
    "dev": "bun --watch --preload ./instrument.ts server.ts"
  }
}
```

#### Bun.serve() — 自动追踪

`@sentry/bun` 通过 JavaScript Proxy 自动追踪 `Bun.serve()`。不需要额外的设置 — 只需使用 `--preload` 并初始化，您的 `Bun.serve()` 调用就会被追踪：

```typescript
// server.ts
const server = Bun.serve({
  port: 3000,
  fetch(req) {
    return new Response("Hello from Bun!");
  },
});
```

#### Bun 上的框架错误处理器

Bun 可以运行 Express、Fastify、Hono 和 Elysia。使用相同的 `@sentry/bun` 导入和 `@sentry/node` 错误处理器函数（由 `@sentry/bun` 重导出）：

```typescript
import * as Sentry from "@sentry/bun";
import express from "express";

const app = express();
// ... 路由
Sentry.setupExpressErrorHandler(app);
app.listen(3000);
```

#### Bun 功能支持

| 功能 | Bun 支持 | 备注 |
|---------|-------------|-------|
| 错误监控 | ✅ 完整 | 与 Node 相同的 API |
| 追踪 | ✅ 通过 `@sentry/node` OTel | 大多数自动追踪工作正常 |
| 日志记录 | ✅ 完整 | `enableLogs: true` + `Sentry.logger.*` |
| 性能分析 | ❌ 不支持 | `@sentry/profiling-node` 使用原生插件，与 Bun 不兼容 |
| 指标 | ✅ 完整 | `Sentry.metrics.*` |
| 运行时指标 | ✅ 完整 | `bunRuntimeMetricsIntegration()` — 内存、CPU、事件循环（没有事件循环延迟百分比） |
| 计划任务 | ✅ 完整 | `Sentry.withMonitor()` |
| AI 监控 | ✅ 完整 | OpenAI、Anthropic 集成工作正常 |

---

### 运行时：Deno

> **Deno 没有向导可用。** 仅支持手动设置。
> **需要 Deno 2.0+。** Deno 1.x 不受支持。
> **使用 `npm:` 指定符。** `deno.land/x/sentry` 仓库已弃用。

#### 通过 `deno.json` 安装（推荐）

```json
{
  "imports": {
    "@sentry/deno": "npm:@sentry/deno@10.42.0"
  }
}
```

或直接使用 `npm:` 指定符导入：

```typescript
import * as Sentry from "npm:@sentry/deno";
```

#### 初始化 — 添加到入口文件

```typescript
// main.ts — Sentry.init() 必须在任何其他代码之前调用
import * as Sentry from "@sentry/deno";

Sentry.init({
  dsn: Deno.env.get("SENTRY_DSN") ?? "___DSN___",

  dataCollection: {
    // 如需禁用发送用户数据和 HTTP 请求体，请取消注释下面的行。更多信息请访问：
    // https://docs.sentry.io/platforms/javascript/guides/node/configuration/options/#dataCollection
    // userInfo: false,
    // httpBodies: [],
  },
  tracesSampleRate: Deno.env.get("DENO_ENV") === "development" ? 1.0 : 0.1,
  enableLogs: true,
});

// 你的应用程序代码如下
Deno.serve({ port: 8000 }, (req) => {
  return new Response("Hello from Deno!");
});
```

> 与 Node.js 和 Bun 不同，Deno 没有 `--preload` 或 `--import` 标志。Sentry 必须是入口文件中的第一个 `import`。

#### 必需的 Deno 权限

SDK 需要网络访问权限以连接到你的 Sentry 摄入域名：

```bash
deno run \
  --allow-net=o<ORG_ID>.ingest.sentry.io \
  --allow-read=./src \
  --allow-env=SENTRY_DSN,SENTRY_RELEASE \
  main.ts
```

在开发环境中，`--allow-all` 可以使用，但不推荐在生产环境中使用。

#### Deno 定时任务集成

Deno 提供原生的定时任务调度功能。使用 `denoCronIntegration` 实现自动监控：

```typescript
import * as Sentry from "@sentry/deno";
import { denoCronIntegration } from "@sentry/deno";

Sentry.init({
  dsn: Deno.env.get("SENTRY_DSN") ?? "___DSN___",
  integrations: [denoCronIntegration()],
});

// 定时任务会自动被监控
Deno.cron("daily-cleanup", "0 0 * * *", () => {
  // 清理逻辑
});
```

#### Deno 功能支持

| 功能 | Deno 支持情况 | 备注 |
|---------|-------------|-------|
| 错误监控 | ✅ 完整支持 | 未处理的异常 + `captureException` |
| 链路追踪 | ✅ 自定义 OTel | 为 `Deno.serve()` 和 `fetch` 自动创建跨度 |
| 日志记录 | ✅ 完整支持 | `enableLogs: true` + `Sentry.logger.*` |
| 性能分析 | ❌ 不可用 | Deno 没有性能分析插件 |
| 指标 | ✅ 完整支持 | `Sentry.metrics.*` |
| 运行时指标 | ❌ 不可用 | Deno 没有运行时指标集成 |
| 定时任务 | ✅ 完整支持 | `denoCronIntegration()` + `Sentry.withMonitor()` |
| AI 监控 | ✅ 部分支持 | Vercel AI SDK 集成可用；OpenAI/Anthropic 通过 `npm:` 实现 |

---

### OTLP 集成（OTel 优先项目 — 仅限 Node.js）

> 仅当第一阶段**检测到 OpenTelemetry 链路追踪**时，才使用此路径
> （例如 `package.json` 中存在 `@opentelemetry/sdk-node` 或 `@opentelemetry/sdk-trace-node`）。
> 对于没有现有 OTel 配置的项目，请使用上述标准的 `@sentry/node` 路径。

OTLP 集成使用 `@sentry/node-core/light` — 一个轻量级的 Sentry SDK，它不捆绑自己的 OpenTelemetry。相反，它挂钩到用户现有的 OTel `TracerProvider` 并通过 OTLP 将跨度导出到 Sentry。

#### 何时使用

| 场景 | 推荐路径 |
|----------|-----------------|
| 新项目，没有现有的 OTel | 标准的 `@sentry/node`（如上所示） — 包含内置的 OTel |
| 现有 OTel 配置，希望使用 Sentry 链路追踪 | `@sentry/node-core/light` + `otlpIntegration()` |
| 现有 OTel 配置，发送到自己的收集器 | `@sentry/node-core/light` + `otlpIntegration({ collectorUrl })` |

#### 安装

```bash
npm install @sentry/node-core @opentelemetry/api @opentelemetry/sdk-trace-node @opentelemetry/sdk-trace-base
# 或
yarn add @sentry/node-core @opentelemetry/api @opentelemetry/sdk-trace-node @opentelemetry/sdk-trace-base
# 或
pnpm add @sentry/node-core @opentelemetry/api @opentelemetry/sdk-trace-node @opentelemetry/sdk-trace-base
```

> `@opentelemetry/*` 包是同级依赖。如果项目已经安装了这些包，请跳过重复安装。

#### 初始化

```javascript
// instrument.mjs — 通过 --import 标志在任何其他模块之前加载
import { NodeTracerProvider } from '@opentelemetry/sdk-trace-node';
import * as Sentry from '@sentry/node-core/light';
import { otlpIntegration } from '@sentry/node-core/light/otlp';

// 首先注册用户的 OTel TracerProvider
const provider = new NodeTracerProvider();
provider.register();

Sentry.init({
  dsn: process.env.SENTRY_DSN ?? '___DSN___',

  dataCollection: {
    // 如需禁用发送用户数据和 HTTP 请求体，请取消注释下面的行。更多信息请访问：
    // https://docs.sentry.io/platforms/javascript/guides/node/configuration/options/#dataCollection
    // userInfo: false,
    // httpBodies: [],
  },
  enableLogs: true,

  // 不要设置 tracesSampleRate — OTel 控制采样
  integrations: [
    otlpIntegration({
      // 通过 OTLP 将 OTel 跨度导出到 Sentry（默认：true）
      setupOtlpTracesExporter: true,
    }),
  ],
});
```

**使用自定义收集器端点：**

```javascript
Sentry.init({
  dsn: process.env.SENTRY_DSN ?? '___DSN___',
  integrations: [
    otlpIntegration({
      collectorUrl: 'http://localhost:4318/v1/traces',
    }),
  ],
});
```

#### 启动你的应用

与标准 Node.js 配置相同的 `--import` 模式：

```bash
node --import ./instrument.mjs app.mjs
```

#### 与标准 `@sentry/node` 的主要区别

| 方面 | `@sentry/node`（标准） | `@sentry/node-core/light`（OTLP） |
|--------|--------------------------|----------------------------------|
| OTel 捆绑 | ✅ 是 — 内置 TracerProvider | ❌ 否 — 使用你现有的 provider |
| 链路追踪控制 | `Sentry.init()` 中的 `tracesSampleRate` | OTel SDK 控制采样 |
| 自动插桩 | ✅ 内置（HTTP、数据库等） | ❌ 你管理 OTel 插桩 |
| 性能分析 | ✅ 可用 | ❌ 不兼容 |
| 错误 ↔ 链路追踪关联 | ✅ 自动 | ✅ 自动（通过 `otlpIntegration`） |
| 包大小 | 较大（包含 OTel） | 较小（轻量模式） |

---

### 针对每个已同意的功能

加载相应的参考文件并遵循其步骤：

| 功能 | 参考文件 | 加载条件... |
|---------|---------------|-------------|
| 错误监控 | `references/error-monitoring.md` | 始终（基线） — 捕获、作用域、丰富化、beforeSend |
| OTLP 集成 | 参见上文 [OTLP 集成](#otlp-integration-otel-first-projects--nodejs-only) | 检测到 OTel 链路追踪 — **替代** 原生链路追踪 |
| 链路追踪 | `references/tracing.md` | OTel 自动插桩、自定义跨度、分布式链路追踪、采样；**如果检测到 OTel 链路追踪则跳过** |
| 日志记录 | `references/logging.md` | 结构化日志、`Sentry.logger.*`、日志到链路追踪的关联 |
| 性能分析 | `references/profiling.md` | 仅限 Node.js — CPU 性能分析，已记录 Bun/Deno 的缺失功能；**如果检测到 OTel 链路追踪则跳过** |
| 指标 | `references/metrics.md` | 自定义计数器、量表、分布 |
| 运行时指标 | 参见下文内联内容 | Node.js 和 Bun 的自动内存、CPU 和事件循环指标 |
| 定时任务 | `references/crons.md` | 定时作业监控、node-cron、Bull、Agenda、Deno.cron |
| AI 监控 | 加载 `sentry-setup-ai-monitoring` 技能 | OpenAI、Anthropic、LangChain、Vercel AI、Google GenAI |

对于每个功能：阅读参考文件，严格遵循其步骤，并在继续之前进行验证。

### 运行时指标

以可配置的间隔自动收集 Node.js 和 Bun 运行时健康指标（内存、CPU 利用率、事件循环延迟/利用率、运行时间）。这些指标会显示在 Sentry 的指标产品中的 `node.runtime.*` / `bun.runtime.*` 命名空间下。

**Node.js** — 在你的 `instrument.js` 中添加 `nodeRuntimeMetricsIntegration()`：

```javascript
const Sentry = require("@sentry/node");

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  integrations: [
    Sentry.nodeRuntimeMetricsIntegration(),
    // 可选：更改收集间隔（默认 30 000 毫秒）
    // Sentry.nodeRuntimeMetricsIntegration({ collectionIntervalMs: 60_000 }),
  ],
});
```

默认收集的指标：`node.runtime.mem.rss`、`node.runtime.mem.heap_used`、`node.runtime.mem.heap_total`、`node.runtime.cpu.utilization`、`node.runtime.event_loop.delay.p50`、`node.runtime.event_loop.delay.p99`、`node.runtime.event_loop.utilization`、`node.runtime.process.uptime`。

**Bun** — 在你的 `instrument.ts` 中添加 `bunRuntimeMetricsIntegration()`：

```typescript
import * as Sentry from "@sentry/bun";
import { bunRuntimeMetricsIntegration } from "@sentry/bun";

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  integrations: [
    bunRuntimeMetricsIntegration(),
    // 可选：更改收集间隔（默认 30 000 毫秒）
    // bunRuntimeMetricsIntegration({ collectionIntervalMs: 60_000 }),
  ],
});
```

收集的指标：与 Node.js 相同，但没有事件循环延迟百分位数（在 Bun 中不可用）。前缀为 `bun.runtime.*`。

---

## 配置参考

### `Sentry.init()` 核心选项

| 选项 | 类型 | 默认值 | 备注 |
|--------|------|---------|-------|
| `dsn` | `string` | — | 必需。也可从环境变量 `SENTRY_DSN` 获取 |
| `tracesSampleRate` | `number` | — | 0–1；启用链路追踪所必需；**使用 OTLP 路径时不要设置** |
| `dataCollection` | `object` | 除非设置，否则保守 | 对自动收集类别（`userInfo`、`cookies`、`httpHeaders`、`httpBodies`、`queryParams`、`genAI`）的细粒度控制。省略时，SDK 回退到 `sendDefaultPii`（默认 `false`）。传递对象 — 即使是 `{}` — 会将未设置的类别翻转为其宽松默认值；可按类别选择退出。 |
| `includeLocalVariables` | `boolean` | `false` | 在堆栈帧中添加局部变量值（Node.js） |
| `enableLogs` | `boolean` | `false` | 启用 Sentry 日志产品（v9.41.0+） |
| `environment` | `string` | `"production"` | 也可从环境变量 `SENTRY_ENVIRONMENT` 获取 |
| `release` | `string` | — | 也可从环境变量 `SENTRY_RELEASE` 获取 |
| `debug` | `boolean` | `false` | 将 SDK 活动记录到控制台 |
| `enabled` | `boolean` | `true` | 在测试中设置为 `false` 以禁用发送 |
| `sampleRate` | `number` | `1.0` | 要发送的错误事件的比例（0–1） |
| `shutdownTimeout` | `number` | `2000` | 进程退出前刷新事件的毫秒数 |

### `nativeNodeFetchIntegration()` 选项

配置出站 `fetch`/`undici` 跨度捕获。自 `@opentelemetry/instrumentation-undici@0.22.0` 起，像 `content-length` 这样的响应头不再自动捕获 — 请使用 `headersToSpanAttributes` 选择加入：

```javascript
Sentry.init({
  integrations: [
    Sentry.nativeNodeFetchIntegration({
      headersToSpanAttributes: {
        requestHeaders: ["x-request-id"],
        responseHeaders: ["content-length", "content-type"],
      },
    }),
  ],
});
```

| 选项 | 类型 | 默认值 | 备注 |
|--------|------|---------|-------|
| `breadcrumbs` | `boolean` | `true` | 为出站 fetch 请求记录面包屑 |
| `headersToSpanAttributes.requestHeaders` | `string[]` | — | 捕获为跨度属性的请求头名称 |
| `headersToSpanAttributes.responseHeaders` | `string[]` | — | 捕获为跨度属性的响应头名称 |

### `otlpIntegration()` 选项（`@sentry/node-core/light/otlp`）

适用于使用 `@sentry/node-core/light` 的 OTel 优先项目。导入：`import { otlpIntegration } from '@sentry/node-core/light/otlp'`。

| 选项 | 类型 | 默认值 | 用途 |
|--------|------|---------|---------|
| `setupOtlpTracesExporter` | `boolean` | `true` | 自动配置 OTLP 导出器以将跨度发送到 Sentry；如果你已经导出到自己的收集器，请设置为 `false` |
| `collectorUrl` | `string` | `undefined` | OTel 收集器的 OTLP HTTP 端点（例如，`http://localhost:4318/v1/traces`）；设置后，跨度将发送到收集器而不是 DSN 派生的 Sentry 端点 |

### 优雅关闭

在进程退出前刷新缓冲的事件 — 这对短命脚本和无服务器应用很重要：

```javascript
process.on("SIGTERM", async () => {
  await Sentry.close(2000); // 带 2 秒超时的刷新
  process.exit(0);
});
```

### 环境变量

| 变量 | 用途 | 运行时 |
|----------|---------|---------|
| `SENTRY_DSN` | DSN（作为在 `init()` 中硬编码的替代方案） | 所有 |
| `SENTRY_ENVIRONMENT` | 部署环境 | 所有 |
| `SENTRY_RELEASE` | 发布版本字符串（从 git 自动检测） | 所有 |
| `SENTRY_AUTH_TOKEN` | 源映射上传令牌 | 构建时 |
| `SENTRY_ORG` | 用于源映射上传的组织别名 | 构建时 |
| `SENTRY_PROJECT` | 用于源映射上传的项目别名 | 构建时 |
| `NODE_OPTIONS` | 为 ESM 设置 `--import ./instrument.mjs` | Node.js |

### 源映射（Node.js）

在生产环境中获得可读的堆栈跟踪需要使用 `@sentry/cli` 或 webpack/esbuild/rollup 插件上传源映射 — 例如，在你的构建中添加注入和上传步骤：

```json
{
  "scripts": {
    "build": "tsc && sentry-cli sourcemaps inject ./dist && sentry-cli sourcemaps upload ./dist"
  }
}
```

上传需要 `SENTRY_AUTH_TOKEN`（一个构建时秘密）。关于创建令牌并将其接入 CI，请参阅 [`sentry-source-maps`](../sentry-source-maps/SKILL.md)。

---

## 验证

设置完成后，验证 Sentry 是否正在接收事件：

```javascript
// 暂时添加到你的入口文件或测试路由，然后移除
import * as Sentry from "@sentry/node"; // 或 @sentry/bun / @sentry/deno

Sentry.captureException(new Error("Sentry test error — delete me"));
```

或者触发一个未处理的异常：

```javascript
// 在路由处理程序或启动时 — 将被自动捕获
throw new Error("Sentry test error — delete me");
```

然后检查你的 [Sentry 问题仪表板](https://sentry.io/issues/) — 错误应该在 ~30 秒内出现。

**验证清单：**

| 检查项 | 方法 |
|-------|-----|
| 错误已捕获 | 在处理程序中抛出，在 Sentry 问题中验证 |
| 链路追踪正常工作 | 检查性能选项卡 — 应显示 HTTP 跨度 |
| `includeLocalVariables` 正常工作 | Sentry 中的堆栈帧应显示变量值 |
| 源映射正常工作 | 堆栈跟踪显示可读的文件名，而不是压缩后的 |

---

## 阶段 4：交叉链接

完成后端设置后，检查配套服务：

```bash
# 前端配套
ls frontend/ web/ client/ ui/ 2>/dev/null
cat package.json 2>/dev/null | grep -E '"react"|"vue"|"svelte"|"next"'

# 其他后端服务
ls ../go.mod ../requirements.txt ../Gemfile 2>/dev/null
```

如果发现前端、特定于框架的 SDK 或其他后端，建议匹配的技能：

**专用 JavaScript 框架技能（优先于通用 node-sdk）：**

| 检测到的 | 优先技能 | 原因 |
|----------|-------------|-----|
| NestJS（`package.json` 中的 `@nestjs/core`） | [`sentry-nestjs-sdk`](../sentry-nestjs-sdk/SKILL.md) | 使用 `@sentry/nestjs`，具有 NestJS 原生装饰器、过滤器和 GraphQL 支持 |
| Next.js（`package.json` 中的 `next`） | [`sentry-nextjs-sdk`](../sentry-nextjs-sdk/SKILL.md) | 三种运行时架构（浏览器、服务器、边缘）、`withSentryConfig`、源映射上传 |

**前端配套：**

| 检测到的 | 建议 |
|---------|---------|
| React 应用（`package.json` 中的 `react`） | [`sentry-react-sdk`](../sentry-react-sdk/SKILL.md) |
| Svelte/SvelteKit | [`sentry-svelte-sdk`](../sentry-svelte-sdk/SKILL.md) |

**其他后端配套：**

| 检测到的 | 建议 |
|---------|---------|
| Go 后端（`go.mod`） | [`sentry-go-sdk`](../sentry-go-sdk/SKILL.md) |
| Python 后端（`requirements.txt`、`pyproject.toml`） | [`sentry-python-sdk`](../sentry-python-sdk/SKILL.md) |
| Ruby 后端（`Gemfile`） | [`sentry-ruby-sdk`](../sentry-ruby-sdk/SKILL.md) |

将前端和后端使用相同的 DSN 或链接项目进行连接，可以启用**分布式链路追踪** — 在单个链路追踪视图中跨越你的浏览器、API 服务器和数据库的堆栈跟踪。

---

## 故障排除

| 问题 | 原因 | 解决方案 |
|-------|-------|----------|
| 事件未出现 | `instrument.js` 加载过晚 | 确保它是第一个 `require()` / 通过 `--import` 或 `--preload` 加载 |
| 跟踪的跨度丢失 | 未设置 `tracesSampleRate` | 在 `Sentry.init()` 中添加 `tracesSampleRate: 1.0` |
| ESM 仪器化不工作 | 缺少 `--import` 标志 | 使用 `node --import ./instrument.mjs` 运行；`import "./instrument.mjs"` 在应用程序中不充分 |
| `@sentry/profiling-node` 在 Bun 上安装失败 | 本地插件不兼容 | Bun 不支持分析功能 — 移除 `@sentry/profiling-node` |
| Deno: 事件未发送 | 缺少 `--allow-net` 权限 | 使用 `--allow-net=o<ORG_ID>.ingest.sentry.io` 运行 |
| Deno: `deno.land/x/sentry` 不工作 | 已弃用且在 v8.55.0 时冻结 | 切换到 `npm:@sentry/deno` 指定符 |
| `includeLocalVariables` 未显示值 | 集成未激活或代码已压缩 | 确保 `includeLocalVariables: true` 在初始化中；检查源映射 |
| NestJS: 错误未被捕获 | 错误 SDK 或缺少过滤器 | 使用 [`sentry-nestjs-sdk`](../sentry-nestjs-sdk/SKILL.md) — NestJS 需要 `@sentry/nestjs`，而不是 `@sentry/node` |
| Hapi: `setupHapiErrorHandler` 时间问题 | 未等待 | 必须在 `server.start()` 之前 `await Sentry.setupHapiErrorHandler(server)` |
| 关闭时: 事件丢失 | 进程在刷新前退出 | 在 SIGTERM/SIGINT 处理器中添加 `await Sentry.close(2000)` |
| 堆栈跟踪显示压缩代码 | 未上传源映射 | 在构建步骤中配置 `@sentry/cli` 源映射上传 |
| 无跟踪出现 (OTLP) | 缺少 `@opentelemetry/*` 包或未添加 `otlpIntegration` | 验证 `@opentelemetry/sdk-trace-node` 是否已安装；将 `otlpIntegration()` 添加到 `integrations`；**不要**设置 `tracesSampleRate` |
| OTLP: 错误未链接到跟踪 | 未注册 `otlpIntegration` | 确保 `otlpIntegration()` 在 `integrations` 数组中 — 它注册了链接错误到 OTel 跟踪的传播上下文 |
| OTLP: 分析未启动 | 分析需要 `tracesSampleRate` | 分析与 OTLP 路径**不兼容**；使用标准的 `@sentry/node` 设置替代 |
