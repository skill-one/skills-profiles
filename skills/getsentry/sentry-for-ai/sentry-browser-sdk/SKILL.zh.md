---
name: sentry-browser-sdk
description: 浏览器 JavaScript 的完整 Sentry SDK 设置。当被要求“将 Sentry 添加到网站”、“安装 @sentry/browser”或为原生 JavaScript、jQuery、静态网站或 WordPress 配置错误监控、跟踪、会话回放或日志记录时使用。
---

> [所有技能](../../SKILL_TREE.md) > [SDK 安装](../sentry-sdk-setup/SKILL.md) > 浏览器 SDK

# Sentry 浏览器 SDK

一个有主见的向导，它会扫描你的项目，并指导你完成浏览器 JavaScript 的 Sentry 完整设置——包括原生 JS、jQuery、静态网站、WordPress，以及任何没有特定框架 SDK 的 JS 项目。

## 在何时使用此技能

- 用户询问“将 Sentry 添加到网站”或为原生 JavaScript 设置 Sentry
- 用户想要安装 `@sentry/browser` 或配置加载器脚本
- 用户拥有 WordPress、Shopify、Squarespace 或静态 HTML 网站
- 用户想要错误监控、跟踪、会话回放或日志记录，但没有特定框架
- 没有适用于特定框架的 SDK

> **注意：** 以下 SDK 版本和 API 反映 `@sentry/browser` ≥10.0.0。
> 在实施之前，请始终参考 [docs.sentry.io/platforms/javascript/](https://docs.sentry.io/platforms/javascript/) 进行验证。

---

## 第一阶段：检测

**关键——首先检查框架。** 框架特定的 SDK 提供显著更好的覆盖率，必须在继续使用 `@sentry/browser` 之前推荐。

### 第 1A 步：框架检测（如果发现则重定向）

```bash
# 检查 React
cat package.json 2>/dev/null | grep -E '"react"'

# 检查 Next.js
cat package.json 2>/dev/null | grep '"next"'

# 检查 Vue
cat package.json 2>/dev/null | grep '"vue"'

# 检查 Angular
cat package.json 2>/dev/null | grep '"@angular/core"'

# 检查 Svelte / SvelteKit
cat package.json 2>/dev/null | grep -E '"svelte"|"@sveltejs/kit"'

# 检查 Remix
cat package.json 2>/dev/null | grep -E '"@remix-run/react"|"@remix-run/node"'

# 检查 Nuxt
cat package.json 2>/dev/null | grep '"nuxt"'

# 检查 Astro
cat package.json 2>/dev/null | grep '"astro"'

# 检查 Ember
cat package.json 2>/dev/null | grep '"ember-source"'

# 检查 Node.js 服务器框架（完全是错误的 SDK）
cat package.json 2>/dev/null | grep -E '"express"|"fastify"|"@nestjs/core"|"koa"'
```

**如果检测到框架，停止并重定向：**

| 检测到的框架 | 重定向到 |
|-------------|---------|
| `next` | 加载 `sentry-nextjs-sdk` 技能——**不要在这里继续** |
| `react`（没有 Next.js） | 加载 `sentry-react-sdk` 技能——**不要在这里继续** |
| `vue` | 推荐 `@sentry/vue`——参见 [docs.sentry.io/platforms/javascript/guides/vue/](https://docs.sentry.io/platforms/javascript/guides/vue/) |
| `@angular/core` | 推荐 `@sentry/angular`——参见 [docs.sentry.io/platforms/javascript/guides/angular/](https://docs.sentry.io/platforms/javascript/guides/angular/) |
| `@sveltejs/kit` | 加载 `sentry-svelte-sdk` 技能——**不要在这里继续** |
| `svelte`（单页应用，没有 kit） | 推荐 `@sentry/svelte`——参见 [docs.sentry.io/platforms/javascript/guides/svelte/](https://docs.sentry.io/platforms/javascript/guides/svelte/) |
| `@remix-run` | 推荐 `@sentry/remix`——参见 [docs.sentry.io/platforms/javascript/guides/remix/](https://docs.sentry.io/platforms/javascript/guides/remix/) |
| `nuxt` | 推荐 `@sentry/nuxt`——参见 [docs.sentry.io/platforms/javascript/guides/nuxt/](https://docs.sentry.io/platforms/javascript/guides/nuxt/) |
| `astro` | 推荐 `@sentry/astro`——参见 [docs.sentry.io/platforms/javascript/guides/astro/](https://docs.sentry.io/platforms/javascript/guides/astro/) |
| `ember-source` | 推荐 `@sentry/ember`——参见 [docs.sentry.io/platforms/javascript/guides/ember/](https://docs.sentry.io/platforms/javascript/guides/ember/) |
| `express` / `fastify` / `@nestjs/core` | 这是一个 Node.js 服务器——加载 `sentry-node-sdk` 或 `sentry-nestjs-sdk` 技能 |

> **为什么重定向很重要：** 框架 SDK 添加了路由感知事务、错误边界、组件跟踪，并且通常支持服务器端渲染。在 React 或 Next.js 应用中直接使用 `@sentry/browser` 会丢失所有这些功能。

如果**没有检测到框架**，才继续使用 `@sentry/browser`。

### 第 1B 步：安装方法检测

```bash
# 检查是否存在 package.json（打包环境）
ls package.json 2>/dev/null

# 检查包管理器
ls package-lock.json yarn.lock pnpm-lock.yaml bun.lockb 2>/dev/null

# 检查构建工具
ls vite.config.ts vite.config.js webpack.config.js rollup.config.js esbuild.config.js 2>/dev/null
cat package.json 2>/dev/null | grep -E '"vite"|"webpack"|"rollup"|"esbuild"'

# 检查 CMS 或静态网站指标
ls wp-config.php wp-content/ 2>/dev/null   # WordPress
ls _config.yml _config.yaml 2>/dev/null    # Jekyll
ls config.toml 2>/dev/null                 # Hugo
ls .eleventy.js 2>/dev/null                # Eleventy

# 检查现有的 Sentry
cat package.json 2>/dev/null | grep '"@sentry/'
grep -r "sentry-cdn.com\|js.sentry-cdn.com" . --include="*.html" -l 2>/dev/null | head -3
```

**需要确定的内容：**

| 问题 | 影响 |
|------|------|
| `package.json` 存在 + 打包工具？ | → **路径 A：npm install** |
| WordPress、Shopify、静态 HTML、没有 npm？ | → **路径 B：加载器脚本** |
| 只有脚本标签，无法访问加载器脚本？ | → **路径 C：CDN 打包** |
| 已经有 `@sentry/browser`？ | 跳过安装，直接进行功能配置 |
| 构建工具是 Vite / webpack / Rollup / esbuild？ | 需要配置源映射插件 |

---

## 第二阶段：推荐

根据你的发现提出建议。以具体的建议开头，不要问开放式问题。

**推荐（核心覆盖）：**
- ✅ **错误监控** — 总是；捕获未处理的错误和 Promise 拒绝
- ✅ **跟踪** — 推荐用于任何交互式网站；跟踪页面加载和用户交互
- ✅ **会话回放** — 推荐用于面向用户的应用；记录错误周围的会话

**可选（增强的可观察性）：**
- ⚡ **用户反馈** — 直接从用户捕获错误报告
- ⚡ **日志记录** — 通过 `Sentry.logger.*` 结构化日志；需要 npm 或 CDN 日志打包（无法通过加载器脚本获取）
- ⚡ **性能分析** — JS 自我性能分析 API；测试版，仅限 Chromium，需要 `Document-Policy: js-profiling` 响应头

**功能推荐逻辑：**

| 功能 | 当...推荐 |
|------|----------|
| 错误监控 | **始终** — 不可协商的基线 |
| 跟踪 | **始终** 对于交互式页面——页面加载和导航跨度非常有价值 |
| 会话回放 | 面向用户的应⽤、支持流程或结账页面 |
| 用户反馈 | 支持导向的应用；想要带截图的本地应用错误报告 |
| 日志记录 | 需要结构化日志搜索或日志到跟踪关联；**仅 npm 路径** |
| 性能分析 | 性能关键、仅限 Chromium 的应用；需要 `Document-Policy: js-profiling` 响应头 |

**安装路径推荐：**

| 场景 | 推荐路径 |
|------|---------|
| 项目有 `package.json` + 打包工具 | **路径 A（npm）** — 完整功能，源映射，树摇动 |
| WordPress、Shopify、Squarespace、静态 HTML | **路径 B（加载器脚本）** — 无需构建工具，始终最新 |
| 没有加载器脚本访问的静态 HTML | **路径 C（CDN 打包）** — 手动 `<script>` 标签 |

建议：*"我建议使用路径 A（npm）设置错误监控 + 跟踪 + 会话回放。是否还需要添加日志记录或用户反馈？*"

---

## 第三阶段：指导

### 路径 A：npm / yarn / pnpm（推荐——打包项目）

#### 安装

```bash
npm install @sentry/browser --save
# 或
yarn add @sentry/browser
# 或
pnpm add @sentry/browser
```

#### 创建 `src/instrument.ts`

Sentry 必须在任何其他代码运行**之前**初始化。将 `Sentry.init()` 放在一个专门的侧边文件中：

```typescript
import * as Sentry from "@sentry/browser";

Sentry.init({
  dsn: import.meta.env.VITE_SENTRY_DSN, // 根据构建工具进行调整（见下表）
  environment: import.meta.env.MODE,
  release: import.meta.env.VITE_APP_VERSION, // 构建时注入

  dataCollection: {
    // 要禁用发送用户数据和 HTTP 正文，请取消以下行的注释。更多信息请访问：
    // https://docs.sentry.io/platforms/javascript/configuration/options/#dataCollection
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

  // 跟踪
  tracesSampleRate: 1.0, // 生产环境中降低到 0.1–0.2
  tracePropagationTargets: ["localhost", /^https:\/\/yourapi\.io/],

  // 会话回放
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,

  enableLogs: true,
});
```

**根据构建工具的 DSN 环境变量：**

| 构建工具 | 变量名 | 代码中访问 |
|----------|--------|-----------|
| Vite | `VITE_SENTRY_DSN` | `import.meta.env.VITE_SENTRY_DSN` |
| 自定义 webpack | `SENTRY_DSN` | `process.env.SENTRY_DSN` |
| esbuild | `SENTRY_DSN` | `process.env.SENTRY_DSN` |
| Rollup | `SENTRY_DSN` | `process.env.SENTRY_DSN` |

#### 入口点设置

将 `instrument.ts` 作为入口文件**第一个导入**：

```typescript
// src/main.ts 或 src/index.ts
import "./instrument";  // ← 必须是第一个

// ... 应用其余部分
```

#### 源映射设置（强烈推荐）

没有源映射，堆栈跟踪会显示压缩后的代码。设置构建插件自动上传源映射：

> **没有专门的浏览器向导：** 没有 `npx @sentry/wizard -i browser` 标志。最接近的是 `npx @sentry/wizard@latest -i sourcemaps`，它仅配置已初始化 SDK 的源映射上传。

**Vite (`vite.config.ts`):**

```typescript
import { defineConfig } from "vite";
import { sentryVitePlugin } from "@sentry/vite-plugin";

export default defineConfig({
  build: { sourcemap: "hidden" },
  plugins: [
    // sentryVitePlugin 必须是最后一个
    sentryVitePlugin({
      org: process.env.SENTRY_ORG,
      project: process.env.SENTRY_PROJECT,
      authToken: process.env.SENTRY_AUTH_TOKEN,
    }),
  ],
});
```

**webpack (`webpack.config.js`):**

```javascript
const { sentryWebpackPlugin } = require("@sentry/webpack-plugin");

module.exports = {
  devtool: "hidden-source-map",
  plugins: [
    sentryWebpackPlugin({
      org: process.env.SENTRY_ORG,
      project: process.env.SENTRY_PROJECT,
      authToken: process.env.SENTRY_AUTH_TOKEN,
    }),
  ],
};
```

**Rollup (`rollup.config.js`):**

```javascript
import { sentryRollupPlugin } from "@sentry/rollup-plugin";

export default {
  output: { sourcemap: "hidden" },
  plugins: [
    sentryRollupPlugin({
      org: process.env.SENTRY_ORG,
      project: process.env.SENTRY_PROJECT,
      authToken: process.env.SENTRY_AUTH_TOKEN,
    }),
  ],
};
```

**esbuild (`build.js`):**

```javascript
const { sentryEsbuildPlugin } = require("@sentry/esbuild-plugin");

require("esbuild").build({
  entryPoints: ["src/index.ts"],
  bundle: true,
  sourcemap: "hidden",
  plugins: [
    sentryEsbuildPlugin({
      org: process.env.SENTRY_ORG,
      project: process.env.SENTRY_PROJECT,
      authToken: process.env.SENTRY_AUTH_TOKEN,
    }),
  ],
});
```

> ⚠️ esbuild 插件**不支持** `splitting: true`。如果启用了代码拆分，请使用 `sentry-cli`。

**使用 `sentry-cli`（任何工具链 / CI）：**

```bash
# 构建步骤之后：
npx @sentry/cli sourcemaps inject ./dist
npx @sentry/cli sourcemaps upload ./dist
```

添加 `.env` 进行认证（切勿提交）：
```bash
SENTRY_AUTH_TOKEN=sntrys_...
SENTRY_ORG=my-org-slug
SENTRY_PROJECT=my-project-slug
```

---

### 路径 B：加载器脚本（WordPress、静态网站、Shopify、Squarespace）

**最佳用途：** 没有构建系统的网站。加载器脚本是一个单个的 `<script>` 标签，它惰性加载完整的 SDK，始终通过 Sentry 的 CDN 保持最新，并在 SDK 加载之前缓冲错误。

**获取加载器脚本：**
Sentry UI → **设置 → 项目 → （你的项目）→ SDK 设置 → 加载器脚本**

复制生成的标签，并将其放置在**每个页面的第一个脚本**：

```html
<!DOCTYPE html>
<html>
  <head>
    <!-- 在加载器标签之前配置 -->
    <script>
      window.sentryOnLoad = function () {
        Sentry.init({
          // DSN 已经在加载器 URL 中配置
          tracesSampleRate: 1.0,
          replaysSessionSampleRate: 0.1,
          replaysOnErrorSampleRate: 1.0,
        });
      };
    </script>

    <!-- 加载器脚本第一个——在所有其他脚本之前 -->
    <script
      src="https://js.sentry-cdn.com/YOUR_PUBLIC_KEY.min.js"
      crossorigin="anonymous"
    ></script>
  </head>
  ...
</html>
```

**加载器加载模式：**

| 模式 | 如何 | SDK 加载时 |
|------|------|------------|
| **惰性（默认）** | 什么额外操作都没有 | 在第一次错误或手动调用 Sentry 时 |
| **急切** | 在 `<script>` 中添加 `data-lazy="no"` | 在所有页面脚本完成后 |
| **手动** | 调用 `Sentry.forceLoad()` | 你调用它的任何时候 |

**安全在 SDK 加载之前调用（缓冲）：**
- `Sentry.captureException()`
- `Sentry.captureMessage()`
- `Sentry.captureEvent()`
- `Sentry.addBreadcrumb()`
- `Sentry.withScope()`

**其他方法使用 `Sentry.onLoad()`：**
```html
<script>
  window.Sentry && Sentry.onLoad(function () {
    Sentry.setUser({ id: "123" });
  });
</script>
```

**通过全局设置发布版本（可选）：**
```html
<script>
  window.SENTRY_RELEASE = { id: "my-app@1.0.0" };
</script>
```

**加载器脚本限制：**
- ❌ 没有 `Sentry.logger.*`（日志记录）——npm 路径仅限
- ❌ 没有特定框架功能（React ErrorBoundary、Vue Router 跟踪等）
- ❌ 仅在 SDK 加载后添加跟踪头到 fetch 调用
- ❌ 版本更改需要几分钟才能通过 CDN 缓存传播
- ⚠️ 使用加载器时，所有其他脚本使用 `defer`（而不是 `async`）

**CSP 要求：**
```
script-src: https://browser.sentry-cdn.com https://js.sentry-cdn.com
connect-src: *.sentry.io
```

---

### 路径 C：CDN 打包（手动脚本标签）

**最佳用途：** 无法使用加载器脚本但需要同步加载的页面。

选择与你的功能需求匹配的捆绑包，并将其放置在**所有其他脚本之前**：

**仅错误（最小占用空间）：**
```html
<script
  src="https://browser.sentry-cdn.com/10.42.0/bundle.min.js"
  integrity="sha384-L/HYBH2QCeLyXhcZ0hPTxWMnyMJburPJyVoBmRk4OoilqrOWq5kU4PNTLFYrCYPr"
  crossorigin="anonymous"
></script>
```

**错误 + 跟踪：**
```html
<script
  src="https://browser.sentry-cdn.com/10.42.0/bundle.tracing.min.js"
  integrity="sha384-DIqcfVcfIewrWiNWfVZcGWExO5v673hkkC5ixJnmAprAfJajpUDEAL35QgkOB5gw"
  crossorigin="anonymous"
></script>
```

**错误 + 会话回放：**
```html
<script
  src="https://browser.sentry-cdn.com/10.42.0/bundle.replay.min.js"
  integrity="sha384-sbojwIJFpv9duIzsI9FRm87g7pB15s4QwJS1m1xMSOdV1CF3pwgrPPEu38Em7M9+"
  crossorigin="anonymous"
></script>
```

**错误 + 跟踪 + 回放（推荐的完整设置）：**
```html
<script
  src="https://browser.sentry-cdn.com/10.42.0/bundle.tracing.replay.min.js"
  integrity="sha384-oo2U4zsTxaHSPXJEnXtaQPeS4Z/qbTqoBL9xFgGxvjJHKQjIrB+VRlu97/iXBtzw"
  crossorigin="anonymous"
></script>
```

**错误 + 跟踪 + 回放 + 用户反馈：**
```html
<script
  src="https://browser.sentry-cdn.com/10.42.0/bundle.tracing.replay.feedback.min.js"
  integrity="sha384-SmHU39Qs9cua0KLtq3A6gis1/cqM1nZ6fnGzlvWAPiwhBDO5SmwFQV65BBpJnB3n"
  crossorigin="anonymous"
></script>
```

**完整捆绑包（所有功能）：**
```html
<script
  src="https://browser.sentry-cdn.com/10.42.0/bundle.tracing.replay.feedback.logs.metrics.min.js"
  integrity="sha384-gOjSzRxwpXpy0FlT6lg/AVhagqrsUrOWUO7jm6TJwuZ9YVHtYK0MBA2hW2FGrIGl"
  crossorigin="anonymous"
></script>
```

**CDN 捆绑包变体总结：**

| 打包包 | 功能 | 使用场景 |
|--------|----------|-------------|
| `bundle.min.js` | 仅错误 | 绝对最小的代码体积 |
| `bundle.tracing.min.js` | + 跟踪 | 性能监控 |
| `bundle.replay.min.js` | + 回放 | 会话录制 |
| `bundle.tracing.replay.min.js` | + 跟踪 + 回放 | 完整的可观察性 |
| `bundle.tracing.replay.feedback.min.js` | + 用户反馈 | + 应用内反馈小部件 |
| `bundle.logs.metrics.min.js` | + 日志 + 指标 | 结构化日志 (CDN) |
| `bundle.tracing.replay.feedback.logs.metrics.min.js` | 全部 | 最大覆盖范围 |

**在脚本标签之后初始化：**
```html
<script>
  Sentry.init({
    dsn: "https://YOUR_KEY@o0.ingest.sentry.io/YOUR_PROJECT",
    environment: "production",
    release: "my-app@1.0.0",
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
  });
</script>
```

**CDN CSP要求：**
```
script-src: https://browser.sentry-cdn.com https://js.sentry-cdn.com
connect-src: *.sentry.io
```

---

### 每个约定的功能

逐个功能进行操作。加载参考文件，按照其步骤进行，验证后再继续：

| 功能 | 参考 | 当...加载时 |
|-------|-----------|-------------|
| 错误监控 | `${SKILL_ROOT}/references/error-monitoring.md` | 始终 (基准) |
| 跟踪 | `${SKILL_ROOT}/references/tracing.md` | 页面加载 / API调用跟踪 |
| 会话回放 | `${SKILL_ROOT}/references/session-replay.md` | 面向用户的程序 |
| 日志记录 | `${SKILL_ROOT}/references/logging.md` | 结构化日志搜索；npm或CDN日志打包 (非加载脚本) |
| 性能分析 | `${SKILL_ROOT}/references/profiling.md` | 性能关键，仅Chromium |
| 用户反馈 | `${SKILL_ROOT}/references/user-feedback.md` | 错误后捕获用户报告 |

对于每个功能：`读取 ${SKILL_ROOT}/references/<功能>.md`，精确跟随步骤，验证其是否正常工作。

---

## 配置参考

### `Sentry.init()` 的关键选项

| 选项 | 类型 | 默认值 | 备注 |
|--------|------|---------|-------|
| `dsn` | `string` | — | **必需。** 空时SDK禁用 |
| `environment` | `string` | `"production"` | 例如，`"staging"`，`"development"` |
| `release` | `string` | — | 例如，`"my-app@1.0.0"` 或 git SHA — 将错误链接到版本发布 |
| `sendDefaultPii` | `boolean` | `false` | 包括IP地址和请求头。**将在v11中弃用** — 使用 `dataCollection` 代替 |
| `dataCollection` | `object` | — | 对收集的数据进行细粒度控制 (v10.54+)。见下表 |
| `tracesSampleRate` | `number` | — | 0–1；开发时 `1.0`，生产时 `0.1–0.2` |
| `tracesSampler` | `function` | — | 每个交易的采样；覆盖比率 |
| `tracePropagationTargets` | `(string\|RegExp)[]` | same-origin | 接收分布式跟踪头的出站URL |
| `replaysSessionSampleRate` | `number` | — | 所有会话中记录的百分比 |
| `replaysOnErrorSampleRate` | `number` | — | 错误会话中记录的百分比 |
| `enableLogs` | `boolean` | `false` | 启用 `Sentry.logger.*` API (npm或CDN日志打包；非加载脚本) |
| `attachStackTrace` | `boolean` | `false` | `captureMessage()` 调用中的堆栈跟踪 |
| `maxBreadcrumbs` | `number` | `100` | 每个事件存储的面包屑数量 |
| `debug` | `boolean` | `false` | 控制台上的SDK详细输出 |
| `tunnel` | `string` | — | 跳过广告拦截器的代理URL |
| `ignoreErrors` | `(string\|RegExp)[]` | `[]` | 丢弃匹配这些模式的错误 |
| `denyUrls` | `(string\|RegExp)[]` | `[]` | 丢弃这些URL上的脚本错误 |
| `allowUrls` | `(string\|RegExp)[]` | `[]` | 仅捕获这些脚本URL的错误 |
| `spotlight` | `boolean\|string` | `false` | 将事件转发到Spotlight本地开发覆盖层 |

### 浏览器特定选项

| 选项 | 类型 | 默认值 | 备注 |
|--------|------|---------|-------|
| `cdnBaseUrl` | `string` | — | 懒加载集成的基本URL |
| `skipBrowserExtensionCheck` | `boolean` | `false` | 跳过浏览器扩展上下文检查 |

### `dataCollection` 选项 (v10.54+)

对SDK收集的数据进行细粒度控制。用更细致的设置替换简单的 `sendDefaultPii` 布尔值。省略时，回退到 `sendDefaultPii` 以保持向后兼容性。

| 字段 | 类型 | 默认值 | 备注 |
|-------|------|---------|-------|
| `userInfo` | `boolean` | `true` | 自动从仪器填充 `user.*` 字段 |
| `cookies` | `boolean \| { allow: string[] } \| { deny: string[] }` | `true` | Cookie收集；`true` = 所有 (过滤)，`false` = 无，`allow`/`deny` = 特定键 |
| `httpHeaders` | `{ request?, response? }` | `{ request: true, response: true }` | HTTP头收集；每个可以是 `boolean` 或 `allow`/`deny` 对象 |
| `httpBodies` | `string[]` | `["incomingRequest", "outgoingRequest", "incomingResponse", "outgoingResponse"]` | 要收集的HTTP体类型 (当 `dataCollection` 明确设置时) |
| `queryParams` | `boolean \| { allow: string[] } \| { deny: string[] }` | `true` | 带有敏感值过滤的查询参数收集 |
| `genAI` | `{ inputs?, outputs? }` | `{ inputs: true, outputs: true }` | 生成式AI输入/输出记录 |
| `stackFrameVariables` | `boolean` | `true` | 捕获堆栈帧中的局部变量值 |
| `frameContextLines` | `number` | `5` | 堆栈帧周围源代码上下文行数 |

**示例：**
```typescript
Sentry.init({
  dsn: "...",
  dataCollection: {
    userInfo: true,
    cookies: { deny: ["session_id", "auth_token"] },
    httpHeaders: {
      request: { deny: ["authorization", "cookie"] },
      response: true,
    },
    queryParams: { allow: ["utm_source", "utm_campaign"] },
  },
});
```

### `window.SENTRY_RELEASE` 全局 (CDN / 加载路径)

在SDK加载之前设置版本号：
```html
<script>
  window.SENTRY_RELEASE = { id: "my-app@1.0.0" };
</script>
```

---

## 验证

触发测试事件以确认Sentry是否接收数据：

**npm / CDN路径：**
```html
<!-- 暂时添加到您的页面 -->
<button onclick="throw new Error('Sentry Browser Test Error')">
  测试错误
</button>
```

**性能验证 (npm路径)：**
```javascript
import * as Sentry from "@sentry/browser";

Sentry.startSpan({ name: "Test Span", op: "test" }, () => {
  // 您的操作
});
```

**手动捕获：**
```javascript
Sentry.captureException(new Error("Manual test"));
Sentry.captureMessage("Manual test message", "info");
```

检查Sentry控制台：
- **问题** → 错误在几秒钟内出现
- **跟踪** → 页面加载事务可见
- **回放** → 页面交互后可见会话录制
- **日志** → 如果启用了日志记录 (npm或CDN日志打包)，则显示结构化日志条目

如果什么都没有出现，请在 `Sentry.init()` 中设置 `debug: true` 并检查浏览器控制台。

---

## 第4阶段：跨链接

完成浏览器设置后，检查是否有缺失Sentry覆盖的后端：

```bash
ls ../backend ../server ../api ../go ../python 2>/dev/null
cat ../go.mod 2>/dev/null | head -3
cat ../requirements.txt ../pyproject.toml 2>/dev/null | head -3
cat ../Gemfile 2>/dev/null | head -3
cat ../pom.xml 2>/dev/null | grep '<artifactId>' | head -3
cat ../composer.json 2>/dev/null | head -3
```

如果存在未配置Sentry的后端，建议匹配的技能：

| 后端检测 | 建议技能 |
|-----------------|--------------|
| Go (`go.mod`) | `sentry-go-sdk` |
| Python (`requirements.txt`, `pyproject.toml`) | `sentry-python-sdk` |
| Ruby (`Gemfile`) | `sentry-ruby-sdk` |
| PHP (`composer.json`) | `sentry-php-sdk` |
| .NET (`*.csproj`, `*.sln`) | `sentry-dotnet-sdk` |
| Java (`pom.xml`, `build.gradle`) | See [docs.sentry.io/platforms/java/](https://docs.sentry.io/platforms/java/) |
| Node.js (Express, Fastify) | `sentry-node-sdk` |
| NestJS (`@nestjs/core`) | `sentry-nestjs-sdk` |

---

## 故障排除

| 问题 | 解决方案 |
|-------|----------|
| 事件未出现 | 设置 `debug: true`，检查DSN，在浏览器控制台中查找SDK错误 |
| 源映射不工作 | 以生产模式构建 (`npm run build`)；验证 `SENTRY_AUTH_TOKEN` 是否设置 |
| 最小化堆栈跟踪 | 源映射未上传 — 检查构建插件配置；运行 `npx @sentry/wizard@latest -i sourcemaps` |
| CDN打包未找到 | 检查URL中的版本号；见 [browser.sentry-cdn.com](https://browser.sentry-cdn.com/) 获取最新版本 |
| SRI完整性错误 | 哈希不匹配 — 从此技能重新复制完整的 `<script>` 标签，包括 `integrity` 属性 |
| 加载脚本未触发 | 验证它是页面上的**第一个** `<script>`；在控制台中检查CSP错误 |
| 加载脚本与跟踪不兼容 | SDK加载之前的fetch调用不会被跟踪 — 将早期调用包裹在 `Sentry.onLoad()` 中 |
| `sentryOnLoad` 未调用 | 必须在加载 `<script>` 标签之前定义 `window.sentryOnLoad` |
| 日志记录不可用 | `Sentry.logger.*` 需要npm或带有 `.logs.` 的CDN打包 — 不支持通过加载脚本 |
| 性能分析不工作 | 验证文档响应上的 `Document-Policy: js-profiling` 标头；仅Chromium |
| 广告拦截器丢弃事件 | 设置 `tunnel: "/sentry-tunnel"` 并添加服务器端中继端点 |
| 会话回放未录制 | 确认 `replayIntegration()` 在初始化中；检查 `replaysSessionSampleRate` > 0 |
| 回放CSP错误 | 在您的CSP中添加 `worker-src 'self' blob:` 和 `child-src 'self' blob:` |
| `tracePropagationTargets` 不匹配 | 检查正则表达式转义；默认为同源 |
| 浏览器扩展阻止事件 | 添加 `denyUrls: [/chrome-extension:\/\//]` 以过滤扩展错误 |
| 高事件量 | 降低 `sampleRate` (错误) 和 `tracesSampleRate` 从生产中的 `1.0` |
| 部署后上传源映射 | 源映射必须在**错误发生之前**上传 — 集成到CI/CD |
| esbuild拆分冲突 | `sentryEsbuildPlugin` 不支持 `splitting: true` — 使用 `sentry-cli` 代替 |
