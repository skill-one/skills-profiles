---
name: sentry-cloudflare-sdk
description: 为 Cloudflare Workers 和 Pages 完整设置 Sentry SDK。当被要求“将 Sentry 添加到 Cloudflare Workers”、“安装 @sentry/cloudflare”或为 Cloudflare Workers、Pages、Durable Objects、Queues、Workflows 或 Cloudflare 上的 Hono 配置错误监控、跟踪、日志记录、计划任务或 AI 监控时使用。
---

> [所有技能](../../SKILL_TREE.md) > [SDK 设置](../sentry-sdk-setup/SKILL.md) > Cloudflare SDK

# Sentry Cloudflare SDK

一个有倾向性的向导，它会扫描您的 Cloudflare 项目，并指导您完成 Sentry Workers、Pages、Durable Objects、Queues、Workflows 和 Hono 的完整设置。

## 在何时调用此技能

- 用户询问在 Cloudflare 项目中“将 Sentry 添加到 Cloudflare Workers”或“设置 Sentry”
- 用户想要安装或配置 `@sentry/cloudflare`
- 用户想要为 Cloudflare Workers 或 Pages 添加错误监控、跟踪、日志记录、计划任务或 AI 监控
- 用户询问关于 `withSentry`、`sentryPagesPlugin`、`instrumentDurableObjectWithSentry` 或 `instrumentD1WithSentry`
- 用户想要监控 Cloudflare 上的 Durable Objects、Queues、Workflows、计划处理程序或电子邮件处理程序

> **注意：** 以下 SDK 版本和 API 反映了编写时 Sentry 文档的当前状态（`@sentry/cloudflare` v10.61.0）。
> 在实施之前，请始终参考 [docs.sentry.io/platforms/javascript/guides/cloudflare/](https://docs.sentry.io/platforms/javascript/guides/cloudflare/)。

---

## 第一阶段：检测

在提出任何建议之前，运行这些命令以了解项目：

```bash
# 检测 Cloudflare 项目
ls wrangler.toml wrangler.jsonc wrangler.json 2>/dev/null

# 检测现有 Sentry
cat package.json 2>/dev/null | grep -E '"@sentry/'

# 检测项目类型（Workers vs Pages）
ls functions/ functions/_middleware.js functions/_middleware.ts 2>/dev/null && echo "检测到 Pages"
cat wrangler.toml 2>/dev/null | grep -E 'main|pages_build_output_dir'

# 检测框架
cat package.json 2>/dev/null | grep -E '"hono"|"remix"|"astro"|"svelte"'

# 检测 Durable Objects
cat wrangler.toml 2>/dev/null | grep -i 'durable_objects'

# 检测 D1 数据库
cat wrangler.toml 2>/dev/null | grep -i 'd1_databases'

# 检测 Queues
cat wrangler.toml 2>/dev/null | grep -i 'queues'

# 检测 Workflows
cat wrangler.toml 2>/dev/null | grep -i 'workflows'

# 检测计划处理程序（cron 触发器）
cat wrangler.toml 2>/dev/null | grep -i 'crons\|triggers'

# 检测兼容性标志
cat wrangler.toml 2>/dev/null | grep -i 'compatibility_flags'
cat wrangler.jsonc 2>/dev/null | grep -i 'compatibility_flags'

# 检测 AI/LLM 库
cat package.json 2>/dev/null | grep -E '"openai"|"@anthropic-ai"|"ai"|"@google/generative-ai"|"@langchain"'

# 检测日志记录库
cat package.json 2>/dev/null | grep -E '"pino"|"winston"'

# 检查配套前端
ls frontend/ web/ client/ 2>/dev/null
cat package.json 2>/dev/null | grep -E '"react"|"vue"|"svelte"|"next"'
```

**需要确定的内容：**

| 问题 | 影响 |
|----------|--------|
| Workers 或 Pages？ | 确定包装器：`withSentry` vs `sentryPagesPlugin` |
| Hono 框架？ | 推荐使用独立的 `@sentry/hono` 包（v10.55.0+）以实现更干净的集成 |
| `@sentry/cloudflare` 已安装？ | 跳过安装，进入功能配置 |
| Durable Objects 已配置？ | 推荐使用 `instrumentDurableObjectWithSentry` |
| D1 数据库已绑定？ | `withSentry` 自动对 D1 绑定进行跟踪（v10.57.0+）；无需手动包装 |
| Queues 已配置？ | `withSentry` 自动对队列处理程序进行跟踪 |
| Workflows 已配置？ | 推荐使用 `instrumentWorkflowWithSentry` |
| Cron 触发器已配置？ | `withSentry` 自动对计划处理程序进行跟踪；推荐使用 Crons 监控 |
| `nodejs_als` 或 `nodejs_compat` 标志已设置？ | **必需** — SDK 需要 `AsyncLocalStorage` |
| AI/LLM 库？ | 推荐使用 AI 监控集成 |
| 配套前端？ | 触发 Phase 4 跨链接 |

---

## 第二阶段：推荐

根据您发现的内容，提出具体的建议。不要提出开放式问题 — 直接提出建议：

**核心覆盖推荐：**
- ✅ **错误监控** — 始终；捕获 fetch、scheduled、queue、email 和 Durable Object 处理程序中的未处理异常
- ✅ **跟踪** — 自动 HTTP 请求跨度、出站 fetch 跟踪、D1 查询跨度

**可选（增强的可观察性）：**
- ⚡ **日志记录** — 通过 `Sentry.logger.*` 进行结构化日志；当需要日志搜索时推荐
- ⚡ **Crons** — 检测丢失/失败的计划任务；当配置了 cron 触发器时推荐
- ⚡ **D1 Instrumentation** — 自动查询跨度和面包屑；当 D1 已绑定时推荐
- ⚡ **Durable Objects** — 自动捕获 DO 方法的错误和跨度；当配置了 DO 时推荐
- ⚡ **Workflows** — 自动为工作流步骤创建跨度；当配置了 Workflows 时推荐
- ⚡ **AI Monitoring** — Vercel AI SDK、OpenAI、Anthropic、LangChain；当检测到 AI 库时推荐

**推荐逻辑：**

| 功能 | 当...推荐 |
|---------|------------------|
| 错误监控 | **始终** — 不可协商的基线 |
| 跟踪 | **始终** — HTTP 请求跟踪和出站 fetch 具有高价值 |
| 日志记录 | 应用需要结构化日志搜索或日志到跟踪关联 |
| Crons | 在 `wrangler.toml` 中配置了 cron 触发器 |
| D1 Instrumentation | 存在 D1 数据库绑定 |
| Durable Objects | 配置了 Durable Object 绑定 |
| Workflows | 配置了 Workflow 绑定 |
| AI Monitoring | 应用使用 Vercel AI SDK、OpenAI、Anthropic 或 LangChain |
| Metrics | 应用需要自定义计数器、计量器或分布 |

提议：*"我建议设置错误监控 + 跟踪。您还需要我添加 D1 instrumentations 和 Crons 监控吗？*"

---

## 第三阶段：指导

### 选项 1：Source Maps 向导

> **您需要自行运行此向导** — 向导会打开浏览器进行登录，并需要交互式输入，而代理无法处理。将以下内容复制粘贴到终端：
>
> ```
> npx @sentry/wizard@latest -i sourcemaps
> ```
>
> 这将设置源映射上传，以便您的生产堆栈跟踪显示可读的代码。它**不会**设置 SDK 初始化 — 您仍然需要按照下面的选项 2 执行实际的 SDK 设置。
>
> **完成之后，继续执行选项 2 进行 SDK 设置。**

> **注意：** 与框架 SDK（Next.js、SvelteKit）不同，没有 Cloudflare 特定的向导集成。`sourcemaps` 向导仅处理源映射上传配置。

---

### 选项 2：手动设置

#### 前提条件：兼容性标志

SDK 需要 `AsyncLocalStorage`。将以下**一个**标志添加到您的 Wrangler 配置中：

**wrangler.toml:**
```toml
compatibility_flags = ["nodejs_als"]
# 或: compatibility_flags = ["nodejs_compat"]
```

**wrangler.jsonc:**
```jsonc
{
  "compatibility_flags": ["nodejs_als"]
}
```

> `nodejs_als` 更轻量级 — 它仅启用 `AsyncLocalStorage`。如果您的代码还需要其他 Node.js API，请使用 `nodejs_compat`。

#### 安装

```bash
npm install @sentry/cloudflare
```

#### Workers 设置

使用 `withSentry` 包裹您的处理程序。这会自动对 `fetch`、`scheduled`、`queue`、`email` 和 `tail` 处理程序进行跟踪：

```typescript
import * as Sentry from "@sentry/cloudflare";

export default Sentry.withSentry(
  (env: Env) => ({
    dsn: env.SENTRY_DSN,
    tracesSampleRate: 1.0,
    enableLogs: true,
    dataCollection: {
      // 要禁用发送用户数据和 HTTP 正文，请取消注释以下行。更多信息请访问：
      // https://docs.sentry.io/platforms/javascript/guides/cloudflare/configuration/options/#dataCollection
      // userInfo: false,
      // httpBodies: [],
    },
  }),
  {
    async fetch(request, env, ctx) {
      return new Response("Hello World!");
    },
  } satisfies ExportedHandler<Env>,
);
```

**关键点：**
- 第一个参数是一个回调，它接收 `env` — 使用此参数读取密钥，如 `SENTRY_DSN`
- SDK 会自动从 `env` 读取 DSN、环境、版本、调试、隧道和跟踪采样率（见 [环境变量](#环境变量)）
- `withSentry` 会包装所有导出的处理程序 — 您不需要为 `scheduled`、`queue` 等单独包装

#### Pages 设置

使用 `sentryPagesPlugin` 作为中间件：

```typescript
// functions/_middleware.ts
import * as Sentry from "@sentry/cloudflare";

export const onRequest = Sentry.sentryPagesPlugin((context) => ({
  dsn: context.env.SENTRY_DSN,
  tracesSampleRate: 1.0,
  enableLogs: true,
  dataCollection: {
    // 要禁用发送用户数据和 HTTP 正文，请取消注释以下行。更多信息请访问：
    // https://docs.sentry.io/platforms/javascript/guides/cloudflare/configuration/options/#dataCollection
    // userInfo: false,
    // httpBodies: [],
  },
}));
```

**链式多个中间件：**

```typescript
import * as Sentry from "@sentry/cloudflare";

export const onRequest = [
  // Sentry 必须是第一个
  Sentry.sentryPagesPlugin((context) => ({
    dsn: context.env.SENTRY_DSN,
    tracesSampleRate: 1.0,
  })),
  // 在此处添加更多中间件
];
```

**直接使用 `wrapRequestHandler`**（适用于 Cloudflare Pages 上的 SvelteKit 等框架）：

```typescript
import * as Sentry from "@sentry/cloudflare";

export const handle = ({ event, resolve }) => {
  return Sentry.wrapRequestHandler(
    {
      options: {
        dsn: event.platform.env.SENTRY_DSN,
        tracesSampleRate: 1.0,
      },
      request: event.request,
      context: event.platform.ctx,
    },
    () => resolve(event),
  );
};
```

#### Hono on Cloudflare Workers

**推荐（v10.55.0+）：** 使用独立的 `@sentry/hono` 包为 Hono 应用：

```bash
npm install @sentry/hono @sentry/cloudflare
```

`@sentry/cloudflare` 包是依赖项，必须与 `@sentry/hono` 保持同步。

```typescript
import { Hono } from "hono";
import { sentry } from "@sentry/hono/cloudflare";

type Bindings = { SENTRY_DSN: string };

const app = new Hono<{ Bindings: Bindings }>();

// 尽早初始化 Sentry 中间件
app.use(
  sentry(app, (env) => ({
    dsn: env.SENTRY_DSN,
    tracesSampleRate: 1.0,
  })),
);

app.get("/", (ctx) => ctx.json({ message: "Hello" }));

app.get("/error", () => {
  throw new Error("Test error");
});

export default app;
```

`sentry()` 中间件会自动捕获错误并创建带有路由模式的交易跨度。

**遗留方法（已弃用）：** 使用 `@sentry/cloudflare` 与 `withSentry` 仍然有效，但 `honoIntegration` 已弃用：

```typescript
import { Hono } from "hono";
import * as Sentry from "@sentry/cloudflare";

const app = new Hono();

app.get("/", (ctx) => ctx.json({ message: "Hello" }));

export default Sentry.withSentry(
  (env: Env) => ({
    dsn: env.SENTRY_DSN,
    tracesSampleRate: 1.0,
  }),
  app,
);
```

#### 设置 SENTRY_DSN 密钥

将您的 DSN 存为 Cloudflare 密钥 — 不要硬编码它：

```bash
# 本地开发：添加到 .dev.vars
echo 'SENTRY_DSN="https://examplePublicKey@o0.ingest.sentry.io/0"' >> .dev.vars

# 生产：设置为密钥
npx wrangler secret put SENTRY_DSN
```

将绑定添加到您的 `Env` 类型：

```typescript
interface Env {
  SENTRY_DSN: string;
  // ... 其他绑定
}
```

#### Source Maps 设置

源映射使生产堆栈跟踪可读。大多数 Cloudflare 项目通过 Wrangler 使用 Vite 构建 — 将 Sentry Vite 插件连接起来，以便在构建时上传映射：

```bash
npm install @sentry/vite-plugin --save-dev
```

```typescript
import { defineConfig } from "vite";
import { sentryVitePlugin } from "@sentry/vite-plugin";

export default defineConfig({
  build: {
    sourcemap: true,
  },
  plugins: [
    sentryVitePlugin({
      org: "___ORG_SLUG___",
      project: "___PROJECT_SLUG___",
      authToken: process.env.SENTRY_AUTH_TOKEN,
    }),
  ],
});
```

`SENTRY_AUTH_TOKEN` 是构建时密钥。有关创建密钥并将其连接到 CI 的更多信息，请参考 [`sentry-source-maps`](../sentry-source-maps/SKILL.md)。上面提到的 `npx @sentry/wizard@latest -i sourcemaps` 快捷方式可自动执行此设置。

---

### 自动发布检测

SDK 可以通过 Cloudflare 的版本元数据绑定自动检测发布版本：

**wrangler.toml:**
```toml
[version_metadata]
binding = "CF_VERSION_METADATA"
```

发布优先级（从高到低）：
1. 传递给 `Sentry.init()` 的 `release` 选项
2. `SENTRY_RELEASE` 环境变量
3. `CF_VERSION_METADATA.id` 绑定

---

### 对每个同意的功能

加载相应的参考文件并按照其步骤操作：

| 功能 | 参考文件 | 在...加载时 |
|---------|---------------|-------------|
| 错误监控 | `references/error-monitoring.md` | 始终（基线）— 未处理异常、手动捕获、作用域、丰富 |
| 跟踪 | `references/tracing.md` | HTTP 请求跟踪、出站 fetch 跨度、D1 查询跨度、分布式跟踪 |
| 日志记录 | `references/logging.md` | 通过 `Sentry.logger.*` 进行结构化日志、日志到跟踪关联 |
| Crons | `references/crons.md` | 计划处理程序监控、`withMonitor`、检查点 API |
| Durable Objects | `references/durable-objects.md` | 为错误捕获和跨度对 Durable Object 类进行跟踪 |

对于每个功能：阅读参考文件，完全按照其步骤操作，并在继续之前进行验证。

---

## 配置参考

### `Sentry.init()` 选项

| 选项 | 类型 | 默认值 | 备注 |
|--------|------|---------|-------|
| `dsn` | `string` | — | 必需。如果未设置，会自动从 `env.SENTRY_DSN` 读取 |
| `tracesSampleRate` | `number` | — | 0–1；开发时为 1.0，生产时建议较低值 |
| `tracesSampler` | `function` | — | 动态采样函数；与 `tracesSampleRate` 互斥 |
| `dataCollection` | `object` | 保守，除非设置 | 控制 SDK 捕获的数据（`userInfo`、`httpBodies` 等）。省略时回退到 `sendDefaultPii`（默认 `false`）；传递对象 — 即使是 `{}` — 也会启用允许的默认值。见 [数据收集参考](#数据收集参考) |
| `sendDefaultPii` | `boolean` | `false` | 遗留。优先使用 `dataCollection` 以控制捕获的数据 |
| `enableLogs` | `boolean` | `false` | 启用 Sentry Logs 产品 |
| `environment` | `string` | 自动 | 如果未设置，会从 `env.SENTRY_ENVIRONMENT` 读取 |
| `release` | `string` | 自动 | 从 `CF_VERSION_METADATA.id` 或 `SENTRY_RELEASE` 检测 |
| `debug` | `boolean` | `false` | 如果未设置，会从 `env.SENTRY_DEBUG` 读取。将 SDK 活动记录到控制台 |
| `tunnel` | `string` | — | 如果未设置，会从 `env.SENTRY_TUNNEL` 读取 |
| `beforeSend` | `function` | — | 在发送错误事件之前过滤/修改错误事件 |
| `beforeSendTransaction` | `function` | — | 在发送交易事件之前过滤/修改交易事件 |
| `beforeSendLog` | `function` | — | 在发送日志条目之前过滤/修改日志条目 |
| `tracePropagationTargets` | `(string\|RegExp)[]` | 所有 URL | 控制哪些出站请求会接收跟踪头 |
| `skipOpenTelemetrySetup` | `boolean` | `false` | 选择退出 OpenTelemetry 兼容性跟踪器 |
| `instrumentPrototypeMethods` | `boolean \| string[]` | `false` | Durable Object：为 RPC 跨度跟踪原型方法 |

### 数据收集参考

```typescript
dataCollection: {
  // 要禁用发送用户数据和 HTTP 正文，请取消注释以下行。更多信息请访问：
  // https://docs.sentry.io/platforms/javascript/configuration/options/#dataCollection
  // userInfo: false,
  // httpBodies: [],
},
```

### 环境变量（从 `env` 读取）

SDK 会自动从 Cloudflare `env` 对象读取这些内容：

| 变量 | 目的 |
|----------|--------|
| `SENTRY_DSN` | Sentry 初始化的 DSN |
| `SENTRY_RELEASE` | 发布版本字符串 |
| `SENTRY_ENVIRONMENT` | 环境名称（`production`、`staging`） |
| `SENTRY_TRACES_SAMPLE_RATE` | 跟踪采样率（解析为浮点数） |
| `SENTRY_DEBUG` | 启用调试模式（`"true"` / `"1"`） |
| `SENTRY_TUNNEL` | 用于事件代理的隧道 URL |
| `CF_VERSION_METADATA` | Cloudflare 版本元数据绑定（自动检测发布） |

### 默认集成

这些由 `getDefaultIntegrations()` 自动注册：

| 集成 | 目的 |
|-------|---------|
| `dedupeIntegration` | 防止重复事件（Workflows中禁用） |
| `inboundFiltersIntegration` | 按类型、消息、URL过滤事件 |
| `functionToStringIntegration` | 保留原始函数名称 |
| `linkedErrorsIntegration` | 跟踪错误中的`cause`链 |
| `fetchIntegration` | 追踪外发`fetch()`调用，创建面包屑 |
| `honoIntegration` | **在v10.55.0中已弃用** — 请使用`@sentry/hono`包替代。自动捕获Hono `onError`异常 |
| `requestDataIntegration` | 将请求数据附加到事件 |
| `consoleIntegration` | 将`console.*`调用捕获为面包屑 |

---

## 验证

设置完成后，验证Sentry是否正常工作：

```typescript
// 暂时添加到您的fetch处理器中，然后移除
export default Sentry.withSentry(
  (env: Env) => ({
    dsn: env.SENTRY_DSN,
    tracesSampleRate: 1.0,
  }),
  {
    async fetch(request, env, ctx) {
      throw new Error("Sentry测试错误 — 删除我");
    },
  } satisfies ExportedHandler<Env>,
);
```

部署并触发该路由，然后检查您的[Sentry问题面板](https://sentry.io/issues/) — 错误应在约30秒内出现。

**验证清单：**

| 检查项 | 方法 |
|-------|-----|
| 捕获到错误 | 在fetch处理器中抛出错误，在Sentry中验证 |
| 跟踪正常工作 | 检查性能标签中的HTTP跨度 |
| 源映射正常工作 | 检查堆栈跟踪是否显示可读的文件/行名 |
| D1跨度（如果配置） | 运行D1查询，检查是否存在`db.query`跨度 |
| 定时监控（如果配置） | 触发cron，检查Crons面板 |

---

## 第4阶段：跨链接

完成Cloudflare设置后，检查是否有配套服务：

```bash
# 检查配套前端
ls frontend/ web/ client/ ui/ 2>/dev/null
cat package.json 2>/dev/null | grep -E '"react"|"vue"|"svelte"|"next"|"astro"'

# 检查相邻目录中的配套后端
ls ../backend ../server ../api 2>/dev/null
cat ../go.mod ../requirements.txt ../Gemfile 2>/dev/null | head -3
```

如果发现前端，建议匹配的SDK技能：

| 检测到的前端 | 建议技能 |
|------------------|--------------|
| React | `sentry-react-sdk` |
| Next.js | `sentry-nextjs-sdk` |
| Svelte/SvelteKit | `sentry-svelte-sdk` |
| Vue/Nuxt | 参考[docs.sentry.io/platforms/javascript/guides/vue/](https://docs.sentry.io/platforms/javascript/guides/vue/) |

如果在不同目录中发现后端：

| 检测到的后端 | 建议技能 |
|-----------------|--------------|
| Go (`go.mod`) | `sentry-go-sdk` |
| Python (`requirements.txt`, `pyproject.toml`) | `sentry-python-sdk` |
| Ruby (`Gemfile`) | `sentry-ruby-sdk` |
| Node.js (Express, Fastify) | `sentry-node-sdk` |

通过链接Sentry项目连接前端和后端，可以启用**分布式跟踪** — 在单个跟踪视图中显示跨越您的浏览器、Cloudflare Worker和后端API的堆栈跟踪。

---

## 故障排除

| 问题 | 原因 | 解决方案 |
|-------|-------|----------|
| 事件未出现 | DSN未设置或`debug: false`隐藏错误 | 在初始化选项中临时设置`debug: true`；验证`SENTRY_DSN`密钥是否通过`wrangler secret list`设置 |
| `AsyncLocalStorage is not defined` | 缺少兼容性标志 | 在`wrangler.toml`中将`nodejs_als`或`nodejs_compat`添加到`compatibility_flags` |
| 堆栈跟踪显示压缩代码 | 未上传源映射 | 配置`@sentry/vite-plugin`或运行`npx @sentry/wizard -i sourcemaps`；验证CI中的`SENTRY_AUTH_TOKEN` |
| 短暂请求中事件丢失 | SDK在worker终止前未刷新 | 确保`withSentry`或`sentryPagesPlugin`包装了您的处理器 — 它们使用`ctx.waitUntil()`来刷新 |
| Hono错误未捕获 | Hono应用未进行instrumentation | 使用`@sentry/hono/cloudflare` — 导入`sentry`中间件并调用`app.use(sentry(app, options))` |
| Durable Object错误丢失 | DO类未进行instrumentation | 使用`Sentry.instrumentDurableObjectWithSentry()`包装类 — 参考`references/durable-objects.md` |
| D1查询未创建跨度 | 处理器未用`withSentry`包装，或查询非`env`绑定 | `withSentry`自动instrument `env`上的D1绑定（v10.57.0+） — 无需手动包装（`instrumentD1WithSentry`已弃用）。v10.61.0+的所有查询方法（`prepare`, `batch`, `exec`, `withSession`）都会被跟踪 |
| 定时处理器未监控 | `withSentry`未包装处理器 | 确保`export default Sentry.withSentry(...)`包装了您的整个导出处理器对象 |
| 发布版本未自动检测 | 未配置`CF_VERSION_METADATA`绑定 | 在`wrangler.toml`中添加`[version_metadata]`并设置`binding = "CF_VERSION_METADATA"` |
| Workflows中存在重复事件 | Dedupe集成过滤步骤失败 | SDK自动为Workflows禁用dedupe；验证您使用`instrumentWorkflowWithSentry` |
