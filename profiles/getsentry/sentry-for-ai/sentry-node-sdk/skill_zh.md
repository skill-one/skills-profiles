> [所有技能](../../SKILL_TREE.md) > [SDK 设置](../sentry-sdk-setup/SKILL.md) > Node.js / Bun / Deno SDK

# Sentry Node.js / Bun / Deno SDK

一个有主见的向导，扫描您的项目并引导您完成 Sentry 在服务器端 JavaScript 和 TypeScript 运行时（Node.js、Bun 和 Deno）的完整设置。

## 在何时调用此技能

- 用户询问“将 Sentry 添加到 Node.js”、“Bun”或“Deno”
- 用户想要安装或配置 `@sentry/node`、`@sentry/bun` 或 `@sentry/deno`
- 用户想要为后端 JS/TS 应用程序添加错误监控、跟踪、日志记录、分析、计划任务、指标或 AI 监控
- 用户询问 `instrument.js`、`--import ./instrument.mjs`、`bun --preload` 或 `npm:@sentry/deno`
- 用户想要监控 Express、Fastify、Koa、Hapi、Connect、Bun.serve() 或 Deno.serve()

> **NestJS？** 使用 [`sentry-nestjs-sdk`](../sentry-nestjs-sdk/SKILL.md) 而不是它——它使用 `@sentry/nestjs` 与 NestJS 本地装饰器和过滤器。
> **Next.js？** 使用 [`sentry-nextjs-sdk`](../sentry-nextjs-sdk/SKILL.md) 而不是它——它处理三运行时架构（浏览器、服务器、边缘）。

> **注意：** SDK 版本反映编写时当前的 Sentry 文档（`@sentry/node` ≥10.42.0, `@sentry/bun` ≥10.42.0, `@sentry/deno` ≥10.42.0）。
> 在实施之前，始终在 [docs.sentry.io/platforms/javascript/guides/node/](https://docs.sentry.io/platforms/javascript/guides/node/) 进行验证。

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

# 检测计划任务 / 调度
cat package.json 2>/dev/null | grep -E '"node-cron"|"cron"|"agenda"|"bull"|"bullmq"'

# 检测 AI / LLM 使用
cat package.json 2>/dev/null | grep -E '"openai"|"@anthropic-ai"|"@langchain"|"@vercel/ai"|"@google/generative-ai"'

# 检测 OpenTelemetry 跟踪
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
| 检测到框架？ | 确定要注册哪个错误处理器 |
| `@sentry/*` 已经安装？ | 跳过安装，直接进行功能配置 |
| `instrument.js` / `instrument.mjs` 已经存在？ | 合并到它而不是覆盖 |
| 检测到日志库？ | 推荐 Sentry 日志 |
| 计划任务 / 调度检测到？ | 推荐 Crons 监控 |
| 检测到 AI 库？ | 推荐 AI 监控 |
| 检测到 OpenTelemetry 跟踪？ | 使用 OTLP 路径而不是原生跟踪 |
| 检测到配套前端？ | 触发 Phase 4 跨链接 |

---

## 第二阶段：推荐

根据您发现的内容，提出具体的建议。不要提出开放式问题——直接提出建议：

**从 OTel 检测路线：**
- **OTel 跟踪检测到**（`package.json` 中的 `@opentelemetry/sdk-node` 或 `@opentelemetry/sdk-trace-node`，或源代码中的 `NodeTracerProvider`）→ 使用 OTLP 路径：`otlpIntegration()` 通过 `@sentry/node-core/light`；**不要**设置 `tracesSampleRate`；Sentry 自动将错误链接到 OTel 跟踪

**推荐的（核心覆盖）：**
- ✅ **错误监控**——始终；捕获未处理的异常、Promise 拒绝和框架错误
- ✅ **跟踪**——通过 OpenTelemetry 自动进行 HTTP、数据库和队列的 instrumentation

**可选的（增强的可观察性）：**
- ⚡ **日志记录**——通过 `Sentry.logger.*` 的结构化日志；当需要 `winston`/`pino`/`bunyan` 或日志搜索时推荐
- ⚡ **分析**——持续 CPU 分析（仅限 Node.js；Bun 或 Deno 上不可用）；**使用 OTLP 路径时不可用**
- ⚡ **AI 监控**——OpenAI、Anthropic、LangChain、Vercel AI SDK；当检测到 AI/LLM 调用时推荐
- ⚡ **计划任务**——检测错过或失败的计划任务；当检测到 node-cron、Bull 或 Agenda 时推荐
- ⚡ **指标**——自定义计数器、指标、分布；当需要自定义 KPI 时推荐
- ⚡ **运行时指标**——自动收集内存、CPU 和事件循环指标；`nodeRuntimeMetricsIntegration()`（Node.js） / `bunRuntimeMetricsIntegration()`（Bun）

**推荐逻辑：**

| 功能 | 推荐当... |
|---------|------------------|
| 错误监控 | **始终**——不可协商的基线 |
| OTLP 集成 | OTel 跟踪检测到——**替换**原生跟踪 |
| 跟踪 | **始终用于服务器应用程序**——HTTP 跨度和数据库跨度具有高价值；**如果检测到 OTel 跟踪，则跳过** |
| 日志记录 | 应用程序使用 winston、pino、bunyan 或需要日志到跟踪的关联 |
| 分析 | **仅限 Node.js**——性能关键的服务；兼容原生插件；**使用 OTLP 路径时不可用**（需要 `tracesSampleRate`，与 OTLP 不兼容） |
| AI 监控 | 应用程序调用 OpenAI、Anthropic、LangChain、Vercel AI 或 Google GenAI |
| 计划任务 | 应用程序使用 node-cron、Bull、BullMQ、Agenda 或任何计划任务模式 |
| 指标 | 应用程序需要自定义计数器、指标或直方图 |
| 运行时指标 | 任何想要自动内存/CPU/事件循环可见性的 Node.js 或 Bun 服务 |

**OTel 跟踪检测到：***"我看到项目中存在 OpenTelemetry 跟踪。我推荐 Sentry 的 OTLP 集成用于跟踪（通过您现有的 OTel 设置）+ 错误监控 + Sentry 日志 [如果适用]。是否继续？*"

**没有 OTel：***"我推荐设置错误监控 + 跟踪。想要我添加日志记录或分析吗？**

---

## 第三阶段：指导

### 运行时：Node.js

#### 选项 1：向导（推荐用于 Node.js）

> **您需要自己运行**——向导会打开浏览器进行登录，需要交互输入，代理无法处理。将以下内容复制粘贴到您的终端：
>
> ```
> npx @sentry/wizard@latest -i node
> ```
>
> 它处理登录、组织/项目选择、SDK 安装、`instrument.js` 创建和 `package.json` 脚本更新。
>
> **完成后，回来并跳到 [验证](#verification)。**

如果用户跳过向导，请继续执行下面的 Option 2（手动设置）。

---

#### 选项 2：手动设置——Node.js

##### 安装

```bash
npm install @sentry/node --save
# or
yarn add @sentry/node
# or
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

  // 开发环境为 100%，生产环境降低
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

##### 使用 Sentry 首先加载您的应用程序

**CommonJS**——将 `require("./instrument")` 作为您入口文件的非常第一行：

```javascript
// app.js
require("./instrument"); // 必须是第一个

const express = require("express");
// ... 您的应用程序的其他部分
```

**ESM**——使用 `--import` 标志，以便 Sentry 在所有其他模块之前加载（需要 Node.js 18.19.0+）：

```bash
node --import ./instrument.mjs app.mjs
```

将内容添加到 `package.json` 脚本：

```json
{
  "scripts": {
    "start": "node --import ./instrument.mjs server.mjs",
    "dev": "node --import ./instrument.mjs --watch server.mjs"
  }
}
```

或者通过环境变量（用于包装现有的启动命令）：

```bash
NODE_OPTIONS="--import ./instrument.mjs" npm start
```

##### 框架错误处理器

在所有路由之后注册 Sentry 错误处理器，以便它能够捕获框架错误：

**Express:**

```javascript
const express = require("express");
const Sentry = require("@sentry/node");

const app = express();

// ... 您的路由

// 添加到所有路由之后——默认捕获 5xx 错误
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

// 添加为第一个中间件（捕获后续中间件抛出的错误）
Sentry.setupKoaErrorHandler(app);

// ... 您的其他中间件和路由

app.listen(3000);
```

**Hapi (异步——必须等待):**

```javascript
const Hapi = require("@hapi/hapi");
const Sentry = require("@sentry/node");

const server = Hapi.server({ port: 3000 });

// ... 您的路由

// 必须 `await`——Hapi 注册是异步的
await Sentry.setupHapiErrorHandler(server);

await server.start();
```

**Connect:**

```javascript
const connect = require("connect");
const Sentry = require("@sentry/node");

const app = connect();

// 添加到路由之前（像 Fastify 和 Koa 一样）
Sentry.setupConnectErrorHandler(app);

// ... 您的中间件和路由

require("http").createServer(app).listen(3000);
```

**NestJS**——它有自己的专用技能，提供完整覆盖：

> **使用 [`sentry-nestjs-sdk`](../sentry-nestjs-sdk/SKILL.md) 技能。**
> NestJS 使用单独的包 (`@sentry/nestjs`) 与 NestJS 本地构造：
> `SentryModule.forRoot()`, `SentryGlobalFilter`, `@SentryTraced`, `@SentryCron` 装饰器，
> 以及 GraphQL/微服务支持。加载该技能以完成 NestJS 设置。

**Vanilla Node.js `http` 模块**——手动包装请求处理器：

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
| Hapi | `setupHapiErrorHandler(server)` | 在 `server.start()` 之前 | Yes |
| Connect | `setupConnectErrorHandler(app)` | **之前**路由 | No |
| NestJS | → 使用 [`sentry-nestjs-sdk`](../sentry-nestjs-sdk/SKILL.md) | 专用技能 | — |

---

### 运行时：Bun

> **Bun 没有向导可用。** 仅限手动设置。

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

#### 使用 `--preload` 启动您的应用程序

```bash
bun --preload ./instrument.ts server.ts
```

将内容添加到 `package.json`：

```json
{
  "scripts": {
    "start": "bun --preload ./instrument.ts server.ts",
    "dev": "bun --watch --preload ./instrument.ts server.ts"
  }
}
```

#### Bun.serve() — 自动 Instrumentation

`@sentry/bun` 通过 JavaScript Proxy 自动 instrumentation `Bun.serve()`。不需要额外的设置——只需使用 `--preload`，您的 `Bun.serve()` 调用就会被跟踪：

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

Bun 可以运行 Express、Fastify、Hono 和 Elysia。使用相同的 `@sentry/bun` 导入和 `@sentry/node` 错误处理器函数（由 `@sentry/bun` 重新导出）：

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
| 错误监控 | ✅ 完整支持 | 与 Node.js 相同的 API |
| 跟踪 | ✅ 通过 `@sentry/node` OTel | 大多数自动 instrumentation 都有效 |
| 日志记录 | ✅ 完整支持 | `enableLogs: true` + `Sentry.logger.*` |
| 分析 | ❌ 不支持 | `@sentry/profiling-node` 使用原生插件与 Bun 不兼容 |
| 指标 | ✅ 完整支持 | `Sentry.metrics.*` |
| 运行时指标 | ✅ 完整支持 | `bunRuntimeMetricsIntegration()`——内存、CPU 和事件循环指标（没有事件循环延迟百分比） |
| 计划任务 | ✅ 完整支持 | `Sentry.withMonitor()` |
| AI 监控 | ✅ 完整支持 | OpenAI、Anthropic 集成有效 |

---

### 运行时：Deno

> **Deno 没有向导可用。** 仅限手动设置。
> **需要 Deno 2.0+。** Deno 1.x 不受支持。
> **使用 `npm:` 指定。** `deno.land/x/sentry` 仓库已弃用。

#### 通过 `deno.json` 安装（推荐）

```json
{
  "imports": {
    "@sentry/deno": "npm:@sentry/deno@10.42.0"
  }
}
```

或者直接导入：

```typescript
import * as Sentry from "npm:@sentry/deno";
```

#### 初始化——添加到入口文件

```typescript
// main.ts — Sentry.init() 必须在任何其他代码之前调用
import * as Sentry from "@sentry/deno";

Sentry.init({
  dsn: Deno.env.get("SENTRY_DSN") ?? "___DSN___",

  dataCollection: {
    // 要禁用发送用户数据和 HTTP 正文，请取消以下行的注释。更多信息请访问：
    // https://docs.sentry.io/platforms/javascript/guides/node/configuration/options/#dataCollection
    // userInfo: false,
    // httpBodies: [],
  },
  tracesSampleRate: Deno.env.get("DENO_ENV") === "development" ?  ```
