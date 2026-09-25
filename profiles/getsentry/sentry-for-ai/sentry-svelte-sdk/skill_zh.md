> [所有技能](../../SKILL_TREE.md) > [SDK 安装](../sentry-sdk-setup/SKILL.md) > Svelte SDK

# Sentry Svelte SDK

一个有主见的向导，它会扫描你的项目并指导你完成 Svelte 和 SvelteKit 的 Sentry 完整设置。

## 在何时调用此技能

- 用户询问在 Svelte/SvelteKit 应用中“添加 Sentry”或“设置 Sentry”
- 用户希望在 Svelte 或 SvelteKit 中实现错误监控、追踪、会话回放或日志记录
- 用户提到 `@sentry/svelte`、`@sentry/sveltekit` 或 Sentry Svelte SDK

> **注意：** 以下 SDK 版本和 API 反映了编写本文时 Sentry 文档的当前状态 (`@sentry/sveltekit` ≥10.8.0, SvelteKit ≥2.31.0)。
> 在实施之前，请始终参考 [docs.sentry.io/platforms/javascript/guides/sveltekit/](https://docs.sentry.io/platforms/javascript/guides/sveltekit/)。

---

## 第一阶段：检测

在提出任何建议之前，运行这些命令以了解项目：

```bash
# 检测框架类型
cat package.json | grep -E '"svelte"|"@sveltejs/kit"|"@sentry/svelte"|"@sentry/sveltekit"'

# 检查 SvelteKit 指示器
ls svelte.config.js svelte.config.ts vite.config.ts vite.config.js 2>/dev/null

# 检查 SvelteKit 版本（决定使用哪种设置模式）
cat package.json | grep '"@sveltejs/kit"'

# 检查 Sentry 是否已安装
cat package.json | grep '"@sentry/'

# 检查现有的钩子文件
ls src/hooks.client.ts src/hooks.client.js src/hooks.server.ts src/hooks.server.js \
   src/instrumentation.server.ts 2>/dev/null

# 检测日志库（Node 端）
cat package.json | grep -E '"pino"|"winston"|"consola"'

# 检测相邻目录中是否存在后端（Go、Python、Ruby 等）
ls ../backend ../server ../api 2>/dev/null
cat ../go.mod ../requirements.txt ../Gemfile 2>/dev/null | head -3
```

**需要确定的内容：**

| 问题 | 影响 |
|----------|--------|
| `package.json` 中是否存在 `@sveltejs/kit`？ | SvelteKit 路径与纯 Svelte 路径 |
| 是否为 SvelteKit ≥2.31.0？ | 现代（`instrumentation.server.ts`）与遗留设置 |
| 是否已存在 `@sentry/sveltekit`？ | 跳过安装，直接进行功能配置 |
| 是否存在 `vite.config.ts`？ | 可通过 Vite 插件上传源映射 |
| 是否找到后端目录？ | 触发第四阶段的跨链接建议 |

---

## 第二阶段：推荐

根据你发现的内容，提出具体的建议。不要提出开放式问题——直接提出建议：

**推荐（核心覆盖）：**
- ✅ **错误监控** — 总是；自动捕获客户端和服务器上的未处理错误
- ✅ **追踪** — SvelteKit 具有客户端导航段和服务器端请求段；总是推荐
- ✅ **会话回放** — 推荐用于面向用户的 SvelteKit 应用（仅客户端）

**可选（增强可观察性）：**
- ⚡ **日志记录** — 通过 `Sentry.logger.*` 的结构化日志；当应用使用服务器端日志记录或需要日志到追踪关联时推荐

**推荐逻辑：**

| 功能 | 当...推荐 |
|---------|------------------|
| 错误监控 | **始终** — 不可协商的基线 |
| 追踪 | **始终用于 SvelteKit**（客户端 + 服务器）；当纯 Svelte 调用 API 时 |
| 会话回放 | 存在面向用户的应用、登录流程或结账页面 |
| 日志记录 | 应用已使用服务器端日志记录，或需要结构化日志搜索 |

提议：*"我推荐设置 Error Monitoring + Tracing + Session Replay。是否还需要添加结构化 Logging？"*

---

## 第三阶段：指导

### 确定设置路径

| 你的项目 | 包 | 设置复杂度 |
|-------------|---------|-----------------|
| SvelteKit (≥2.31.0) | `@sentry/sveltekit` | 需要创建/修改 5 个文件 |
| SvelteKit (<2.31.0) | `@sentry/sveltekit` | 3 个文件（在 `hooks.server.ts` 中初始化） |
| 纯 Svelte（没有 `@sveltejs/kit`） | `@sentry/svelte` | 单一入口点 |

---

### 路径 A：SvelteKit（推荐 — 现代，≥2.31.0）

#### 选项 1：向导（推荐）

> **你需要自己运行** — 向导会打开浏览器进行登录，并需要交互式输入，代理无法处理。将以下内容复制粘贴到你的终端：
>
> ```
> npx @sentry/wizard@latest -i sveltekit
> ```
>
> 它会处理登录、组织/项目选择、SDK 安装、客户端/服务器钩子、Vite 插件配置、源映射上传，并添加一个 `/sentry-example-page`。
>
> **完成后，回来并跳转到 [验证](#verification)。**

如果用户跳过向导，请继续执行下面的手动设置。

#### 选项 2：手动设置

**步骤 1 — 安装**

```bash
npm install @sentry/sveltekit --save
```

**步骤 2 — `svelte.config.js`** — 启用 instrumentation

```javascript
import adapter from "@sveltejs/adapter-auto";

const config = {
  kit: {
    adapter: adapter(),
    experimental: {
      instrumentation: { server: true },
      tracing: { server: true },
    },
  },
};

export default config;
```

**步骤 3 — `src/instrumentation.server.ts`** — 服务器端初始化（启动时运行一次）

```typescript
import * as Sentry from "@sentry/sveltekit";

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.SENTRY_ENVIRONMENT,
  release: process.env.SENTRY_RELEASE,

  dataCollection: {
    // 要禁用发送用户数据和 HTTP 正文，请取消以下行的注释。更多信息请访问：
    // https://docs.sentry.io/platforms/javascript/guides/sveltekit/configuration/options/#dataCollection
    // userInfo: false,
    // httpBodies: [],
  },
  tracesSampleRate: 1.0,    // 在生产环境中降低到 0.1–0.2
  enableLogs: true,
});
```

**步骤 4 — `src/hooks.client.ts`** — 客户端初始化

```typescript
import * as Sentry from "@sentry/sveltekit";

Sentry.init({
  dsn: import.meta.env.PUBLIC_SENTRY_DSN ?? import.meta.env.VITE_SENTRY_DSN,
  environment: import.meta.env.MODE,

  dataCollection: {
    // 要禁用发送用户数据和 HTTP 正文，请取消以下行的注释。更多信息请访问：
    // https://docs.sentry.io/platforms/javascript/guides/sveltekit/configuration/options/#dataCollection
    // userInfo: false,
    // httpBodies: [],
  },
  tracesSampleRate: 1.0,

  integrations: [
    Sentry.replayIntegration({
      maskAllText: true,
      blockAllMedia: true,
    }),
  ],

  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
  enableLogs: true,
});

export const handleError = Sentry.handleErrorWithSentry();
```

**步骤 5 — `src/hooks.server.ts`** — 服务器钩子（现代设置中此处无需初始化）

```typescript
import * as Sentry from "@sentry/sveltekit";
import { sequence } from "@sveltejs/kit/hooks";

export const handleError = Sentry.handleErrorWithSentry();

// sentryHandle() 会对传入的请求进行 instrumentation 并创建根 span
export const handle = Sentry.sentryHandle();

// 如果你还有其他 handle 函数，请使用 sequence() 组合它们：
// export const handle = sequence(Sentry.sentryHandle(), myAuthHandle);
```

**步骤 6 — `vite.config.ts`** — 源映射（需要 `SENTRY_AUTH_TOKEN`）

```typescript
import { sveltekit } from "@sveltejs/kit/vite";
import { sentrySvelteKit } from "@sentry/sveltekit";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [
    // sentrySvelteKit 必须在 sveltekit() 之前
    sentrySvelteKit({
      org: process.env.SENTRY_ORG,
      project: process.env.SENTRY_PROJECT,
      authToken: process.env.SENTRY_AUTH_TOKEN,
    }),
    sveltekit(),
  ],
});
```

添加到 `.env`（切勿提交）：
```bash
SENTRY_AUTH_TOKEN=sntrys_...
SENTRY_ORG=my-org-slug
SENTRY_PROJECT=my-project-slug
```

---

### 路径 B：SvelteKit 遗留版（<2.31.0 或 `@sentry/sveltekit` <10.8.0）

跳过 `instrumentation.server.ts` 和 `svelte.config.js` 的更改。相反，将 `Sentry.init()` 直接放在 `hooks.server.ts` 中：

```typescript
// src/hooks.server.ts（遗留 — 初始化在这里）
import * as Sentry from "@sentry/sveltekit";

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  tracesSampleRate: 1.0,
  enableLogs: true,
});

export const handleError = Sentry.handleErrorWithSentry();
export const handle = Sentry.sentryHandle();
```

`hooks.client.ts` 和 `vite.config.ts` 与现代路径相同。

---

### 路径 C：纯 Svelte（没有 SvelteKit）

**安装：**

```bash
npm install @sentry/svelte --save
```

**在入口点配置**（`src/main.ts` 或 `src/main.js`）**在挂载应用之前**：

```typescript
import * as Sentry from "@sentry/svelte";
import App from "./App.svelte";

Sentry.init({
  dsn: import.meta.env.VITE_SENTRY_DSN,
  environment: import.meta.env.MODE,

  dataCollection: {
    // 要禁用发送用户数据和 HTTP 正文，请取消以下行的注释。更多信息请访问：
    // https://docs.sentry.io/platforms/javascript/guides/sveltekit/configuration/options/#dataCollection
    // userInfo: false,
    // httpBodies: [],
  },

  integrations: [
    Sentry.browserTracingIntegration(),
    Sentry.replayIntegration({
      maskAllText: true,
      blockAllMedia: true,
    }),
  ],

  tracesSampleRate: 1.0,
  tracePropagationTargets: ["localhost", /^https:\/\/yourapi\.io/],
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
  enableLogs: true,
});

const app = new App({ target: document.getElementById("app")! });
export default app;
```

**可选：Svelte 组件追踪**（自动向所有组件注入追踪）：

```javascript
// svelte.config.js
import { withSentryConfig } from "@sentry/svelte";

export default withSentryConfig(
  { compilerOptions: {} },
  { componentTracking: { trackComponents: true } }
);
```

---

### 对于每个同意的功能

逐个功能进行操作。加载参考文件，按照其步骤操作，然后验证后再继续：

| 功能 | 参考文件 | 加载时... |
|---------|-----------|-------------|
| 错误监控 | `${SKILL_ROOT}/references/error-monitoring.md` | 始终（基线） |
| 追踪 | `${SKILL_ROOT}/references/tracing.md` | 需要调用 API / 分布式追踪 |
| 会话回放 | `${SKILL_ROOT}/references/session-replay.md` | 面向用户的应用 |
| 日志记录 | `${SKILL_ROOT}/references/logging.md` | 结构化日志 / 日志到追踪关联 |

对于每个功能：`读取 ${SKILL_ROOT}/references/<功能>.md`，完全按照步骤操作，验证其是否正常工作。

---

## 配置参考

### `Sentry.init()` 的关键选项

| 选项 | 类型 | 默认值 | 备注 |
|--------|------|---------|-------|
| `dsn` | `string` | — | **必需。** 使用环境变量；当为空时 SDK 被禁用 |
| `environment` | `string` | `"production"` | 例如，`"staging"`，`"development"` |
| `release` | `string` | — | 例如，`"my-app@1.2.3"` 或 git SHA |
| `dataCollection` | `object` | — | 控制收集哪些数据（userInfo、cookies、headers 等） |
| `dataCollection.userInfo` | `boolean` | `true` | 从 instrumentation 自动填充 `user.*` 字段 |
| `dataCollection.cookies` | `boolean\|object` | `true` | Cookie 收集和过滤 |
| `dataCollection.httpHeaders` | `object` | `{request: true, response: true}` | 请求/响应的 HTTP 头收集 |
| `dataCollection.httpBodies` | `string[]` | `["incomingRequest", "outgoingRequest", "incomingResponse", "outgoingResponse"]` | 要收集的 HTTP 正文类型 |
| `dataCollection.queryParams` | `boolean\|object` | `true` | 查询参数收集和过滤 |
| `tracesSampleRate` | `number` | — | 0–1；开发中使用 `1.0`，生产中使用 `0.1–0.2` |
| `tracesSampler` | `function` | — | 每个交易的采样；覆盖 `tracesSampleRate` |
| `tracePropagationTargets` | `(string\|RegExp)[]` | — | 接收分布式追踪头的 URL |
| `replaysSessionSampleRate` | `number` | — | 所有会话记录的分数（仅客户端） |
| `replaysOnErrorSampleRate` | `number` | — | 错误会话记录的分数（仅客户端） |
| `enableLogs` | `boolean` | `false` | 启用 `Sentry.logger.*` API |
| `beforeSendLog` | `function` | — | 在发送前过滤/修改日志 |
| `debug` | `boolean` | `false` | 控制台上的 SDK 详细输出 |

### 仅服务器端选项 (`instrumentation.server.ts` / `hooks.server.ts`)

| 选项 | 类型 | 备注 |
|--------|------|-------|
| `serverName` | `string` | 服务器事件上的主机名标签 |
| `includeLocalVariables` | `boolean` | 将局部变量附加到堆栈帧 |
| `shutdownTimeout` | `number` | ms 内刷新事件，然后退出进程（默认：2000） |

### 适配器兼容性

| 适配器 | 支持 |
|---------|---------|
| `@sveltejs/adapter-auto` / adapter-vercel (Node) | ✅ 完全支持 |
| `@sveltejs/adapter-node` | ✅ 完全支持 |
| `@sveltejs/adapter-cloudflare` | ⚠️ 部分支持 — 需要额外设置 |
| Vercel Edge Runtime | ❌ 不支持 |

### SvelteKit 文件总结

| 文件 | 目的 | 现代 | 遗留 |
|------|------|--------|--------|
| `src/instrumentation.server.ts` | 服务器 `Sentry.init()` — 启动时运行一次 | ✅ 必需 | ❌ |
| `src/hooks.client.ts` | 客户端 `Sentry.init()` + `handleError` | ✅ 必需 | ✅ 必需 |
| `src/hooks.server.ts` | `handleError` + `sentryHandle()`（无需初始化） | ✅ 必需 | ✅ 初始化在这里 |
| `svelte.config.js` | 启用 `experimental.instrumentation.server` | ✅ 必需 | ❌ |
| `vite.config.ts` | `sentrySvelteKit()` 插件用于源映射 | ✅ 推荐 | ✅ 推荐 |
| `.env` | `SENTRY_AUTH_TOKEN`、`SENTRY_ORG`、`SENTRY_PROJECT` | ✅ 用于源映射 | ✅ 用于源映射 |

---

## 验证

设置完成后，触发测试事件以确认 Sentry 正在接收数据：

```svelte
<!-- src/routes/sentry-test/+page.svelte -->
<script>
  import * as Sentry from "@sentry/sveltekit";
</script>

<button onclick={() => { throw new Error("Sentry client test"); }}>
  测试客户端错误
</button>

<button onclick={() => Sentry.captureMessage("Sentry test message", "info")}>
  测试消息
</button>
```

```typescript
// src/routes/sentry-test/+server.ts
export const GET = () => {
  throw new Error("Sentry server test");
};
```

检查 Sentry 仪表板：
- **问题** → 两个错误应在几秒钟内出现
- **追踪** → 查找基于路由的交易
- **回放** → 页面交互后可见会话记录
- **日志** → 结构化日志条目（如果启用了日志记录）

如果没有任何内容出现，请在 `Sentry.init()` 中设置 `debug: true`，并检查浏览器/服务器控制台中的 SDK 输出。

---

## 第四阶段：跨链接

完成 Svelte/SvelteKit 设置后，检查是否有缺少 Sentry 覆盖的配套后端：

```bash
# 查找相邻目录中的后端
ls ../backend ../server ../api ../go ../python 2>/dev/null
cat ../go.mod 2>/dev/null | head -3
cat ../requirements.txt ../pyproject.toml 2>/dev/null | head -3
cat ../Gemfile 2>/dev/null | head -3
```

如果存在未配置 Sentry 的后端，建议匹配的技能：

| 检测到的后端 | 建议技能 |
|-----------------|--------------|
| Go (`go.mod`) | `sentry-go-sdk` |
| Python (`requirements.txt`, `pyproject.toml`) | `sentry-python-sdk` |
| Ruby (`Gemfile`) | `sentry-ruby-sdk` |
| Node.js (Express, Fastify 等) | 使用 `@sentry/node` — 参考 [docs.sentry.io/platforms/javascript/guides/express/](https://docs.sentry.io/platforms/javascript/guides/express/) |

---

## 故障排除

| 问题 | 解决方案 |
|-------|----------|
| 事件未出现 | 设置 `debug: true`，检查 DSN，打开浏览器控制台查看 SDK 错误 |
| 源映射不工作 | 运行 `npm run build`（不是 `dev`），验证 `SENTRY_AUTH_TOKEN` 是否已设置 |
| 服务器错误未捕获 | 确保 `handleErrorWithSentry()` 从 `hooks.server.ts` 导出 |
| 客户端错误未捕获 | 确保 `handleErrorWithSentry()` 从 `hooks.client.ts` 导出 |
| 会话回放未记录 | 确认 `replayIntegration()` 仅在客户端初始化中（服务器中绝不能有） |
| `sentryHandle()` + 其他钩子未组合 | 使用 `sequence(Sentry.sentryHandle(), myHandle)` 包装 |
| 广告拦截器阻止事件 | 设置 `tunnel: "/sentry-tunnel"` 并添加一个服务器端中继端点 |
| SvelteKit instrumentation 未激活 | 确认 `experimental.instrumentation.server: true` 在 `svelte.config.js` 中 |
| Cloudflare 适配器问题 | 参考 [docs.sentry.io/platforms/javascript/guides/sveltekit/](https://docs.sentry.io/platforms/javascript/guides/sveltekit/) 获取适配器特定说明 |
| `wrapLoadWithSentry` / `wrapServerLoadWithSentry` 错误 | 这些是遗留包装器 — 移除它们；`sentryHandle()` 在 ≥10.8.0 中自动 instrumentation load 函数 |
