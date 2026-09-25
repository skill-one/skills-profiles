> [所有技能](../../SKILL_TREE.md) > [SDK 安装](../sentry-sdk-setup/SKILL.md) > React SDK

# Sentry React SDK

一个有主见的向导，它会扫描你的 React 项目并指导你完成 Sentry 的完整设置。

## 在以下情况下调用此技能

- 用户询问在 React 应用中“添加 Sentry”或“设置 Sentry”
- 用户希望在 React 中实现错误监控、跟踪、会话回放、性能分析或日志记录
- 用户提到 `@sentry/react`、React Sentry SDK 或 Sentry 错误边界
- 用户希望监控 React Router v5/v6/v7 非框架导航、Redux 状态或组件性能

如果项目使用 `@sentry/react-router` 的 **框架模式**，请使用 `sentry-react-router-framework-sdk` 而不是此技能。

> **注意：** 以下 SDK 版本和 API 反映了编写文档时 Sentry 文档的当前状态（`@sentry/react` ≥8.0.0）。
> 在实施之前，请始终参考 [docs.sentry.io/platforms/javascript/guides/react/](https://docs.sentry.io/platforms/javascript/guides/react/) 进行验证。

---

## 第一阶段：检测

在提出任何建议之前，运行这些命令以了解项目：

```bash
# 检测 React 版本
cat package.json | grep -E '"react"|"react-dom"'

# 检查现有的 Sentry
cat package.json | grep '"@sentry/'

# 检测路由和框架模式提示
cat package.json | grep -E '"react-router-dom"|"react-router"|"@react-router/"|"@tanstack/react-router"|"@sentry/react-router"'

# 检测状态管理
cat package.json | grep -E '"redux"|"@reduxjs/toolkit"'

# 检测构建工具
ls vite.config.ts vite.config.js webpack.config.js craco.config.js 2>/dev/null
cat package.json | grep -E '"vite"|"react-scripts"|"webpack"'

# 检测日志库
cat package.json | grep -E '"pino"|"winston"|"loglevel"'

# 检查相邻目录中的配套后端
ls ../backend ../server ../api 2>/dev/null
cat ../go.mod ../requirements.txt ../Gemfile ../pom.xml 2>/dev/null | head -3
```

**需要确定的内容：**

| 问题 | 影响 |
|------|------|
| React 19+? | 使用 `reactErrorHandler()` 钩子模式 |
| React <19? | 使用 `Sentry.ErrorBoundary` |
| `@sentry/react` 已存在？ | 跳过安装，直接进行功能配置 |
| React Router Framework 模式指示器（`@sentry/react-router`，`@react-router/*`）？ | 使用 `sentry-react-router-framework-sdk` |
| `react-router-dom` v5 / v6 / v7? | 确定要使用的路由集成 |
| `@tanstack/react-router`? | 使用 `tanstackRouterBrowserTracingIntegration()` |
| 使用 Redux？ | 推荐 `createReduxEnhancer()` |
| 检测到 Vite？ | 通过 `sentryVitePlugin` 提供源映射 |
| CRA (`react-scripts`)? | 通过 CRACO 中的 `@sentry/webpack-plugin` 提供源映射 |
| 找到后端目录？ | 触发第四阶段的跨链接建议 |

---

## 第二阶段：建议

根据你发现的内容提出具体的建议，不要提出开放式问题——直接提出建议：

**推荐（核心覆盖）：**
- ✅ **错误监控** — 总是；捕获未处理的错误、React 错误边界、React 19 钩子
- ✅ **跟踪** — React SPAs 从页面加载、导航和 API 调用跟踪中受益
- ✅ **会话回放** — 建议用于面向用户的应用程序；记录错误周围的会话

**可选（增强可观察性）：**
- ⚡ **日志记录** — 通过 `Sentry.logger.*` 提供结构化日志；当需要结构化日志搜索时推荐
- ⚡ **性能分析** — JS 自我性能分析 API（⚠️ 实验性；需要跨域隔离标头）

**建议逻辑：**

| 功能 | 当...推荐 |
|------|----------|
| 错误监控 | **始终** — 不可协商的基线 |
| 跟踪 | **始终用于 React SPAs** — 页面加载和导航跨度非常有价值 |
| 会话回放 | 面向用户的应用程序、登录流程或结账页面 |
| 日志记录 | 应用程序需要结构化日志搜索或日志到跟踪关联 |
| 性能分析 | 性能关键的应用程序；服务器发送 `Document-Policy: js-profiling` 标头 |

**React 特定扩展：**
- 检测到 React 19 → 在 `createRoot` 上设置 `reactErrorHandler()`
- 检测到 React Router v5/v6/v7 非框架 → 配置匹配的路由集成（见第三阶段）
- 检测到 React Router Framework 模式 → 切换到 `sentry-react-router-framework-sdk`
- 检测到 Redux → 向 Redux 存储添加 `createReduxEnhancer()`
- 检测到 Vite → 配置 `sentryVitePlugin` 以提供源映射（对可读堆栈跟踪至关重要）

建议：*"我建议设置错误监控 + 跟踪 + 会话回放。是否还需要添加日志记录或性能分析？*"

---

## 第三阶段：指导

### 安装

```bash
npm install @sentry/react --save
```

### 创建 `src/instrument.ts`

Sentry 必须在任何其他代码运行之前初始化。将 `Sentry.init()` 放在一个专门的侧车文件中：

```typescript
import * as Sentry from "@sentry/react";

Sentry.init({
  dsn: import.meta.env.VITE_SENTRY_DSN, // 根据构建工具进行调整（见下表）
  environment: import.meta.env.MODE,
  release: import.meta.env.VITE_APP_VERSION, // 在构建时注入

  dataCollection: {
    // 要禁用发送用户数据和 HTTP 正文，请取消以下行。更多信息请访问：
    // https://docs.sentry.io/platforms/javascript/guides/react/configuration/options/#dataCollection
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
  tracesSampleRate: 1.0, // 在生产环境中降低到 0.1–0.2
  tracePropagationTargets: ["localhost", /^https:\/\/yourapi\.io/],

  // 会话回放
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,

  enableLogs: true,
});
```

**根据构建工具的 DSN 环境变量：**

| 构建工具 | 变量名 | 代码中的访问方式 |
|----------|--------|------------------|
| Vite | `VITE_SENTRY_DSN` | `import.meta.env.VITE_SENTRY_DSN` |
| Create React App | `REACT_APP_SENTRY_DSN` | `process.env.REACT_APP_SENTRY_DSN` |
| 自定义 webpack | `SENTRY_DSN` | `process.env.SENTRY_DSN` |

### 入口点设置

在入口文件中作为**第一个导入**导入 `instrument.ts`：

```tsx
// src/main.tsx (Vite) 或 src/index.tsx (CRA/webpack)
import "./instrument";              // ← 必须是第一个

import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>
);
```

### React 版本特定的错误处理

**React 19+** — 在 `createRoot` 上使用 `reactErrorHandler()`：

```tsx
import { reactErrorHandler } from "@sentry/react";

createRoot(document.getElementById("root")!, {
  onUncaughtError: reactErrorHandler(),
  onCaughtError: reactErrorHandler(),
  onRecoverableError: reactErrorHandler(),
}).render(<App />);
```

**React <19** — 将你的应用程序包装在 `Sentry.ErrorBoundary` 中：

```tsx
import * as Sentry from "@sentry/react";

createRoot(document.getElementById("root")!).render(
  <Sentry.ErrorBoundary fallback={<p>出错了</p>} showDialog>
    <App />
  </Sentry.ErrorBoundary>
);
```

对于任何应该独立捕获错误的子树（路由部分、小部件等），使用 `<Sentry.ErrorBoundary>`。

### 路由集成

为你的路由配置匹配的集成（非框架模式）：

| 路由 | 集成 | 备注 |
|------|------|------|
| React Router v7 | `reactRouterV7BrowserTracingIntegration` | `useEffect`，`useLocation`，`useNavigationType`，`createRoutesFromChildren`，`matchRoutes` 来自 `react-router` |
| React Router v6 | `reactRouterV6BrowserTracingIntegration` | `useEffect`，`useLocation`，`useNavigationType`，`createRoutesFromChildren`，`matchRoutes` 来自 `react-router-dom` |
| React Router v5 | `reactRouterV5BrowserTracingIntegration` | 将路由包装在 `withSentryRouting(Route)` 中 |
| TanStack Router | `tanstackRouterBrowserTracingIntegration(router)` | 传递路由实例——不需要钩子 |
| 无路由/自定义 | `browserTracingIntegration()` | 通过 URL 路径名称事务 |

**React Router v6/v7 设置：**

```typescript
// 在 integrations 数组中：
import React from "react";
import {
  createRoutesFromChildren, matchRoutes,
  useLocation, useNavigationType,
} from "react-router-dom"; // 或 "react-router" 用于 v7
import * as Sentry from "@sentry/react";
import { reactRouterV6BrowserTracingIntegration } from "@sentry/react";
import { createBrowserRouter } from "react-router-dom";

// 选项 A — createBrowserRouter（推荐用于 v6.4+）：
const sentryCreateBrowserRouter = Sentry.wrapCreateBrowserRouterV6(createBrowserRouter);
const router = sentryCreateBrowserRouter([...routes]);

// 选项 B — createBrowserRouter 用于 React Router v7：
// const sentryCreateBrowserRouter = Sentry.wrapCreateBrowserRouterV7(createBrowserRouter);

// 选项 C — 钩子集成（v6 不使用数据 API）：
Sentry.init({
  integrations: [
    reactRouterV6BrowserTracingIntegration({
      useEffect: React.useEffect,
      useLocation,
      useNavigationType,
      matchRoutes,
      createRoutesFromChildren,
    }),
  ],
});
```

**TanStack Router 设置：**

```typescript
import { tanstackRouterBrowserTracingIntegration } from "@sentry/react";

// 传递你的 TanStack router 实例：
Sentry.init({
  integrations: [tanstackRouterBrowserTracingIntegration(router)],
});
```

### Redux 集成（当检测到时）

```typescript
import * as Sentry from "@sentry/react";
import { configureStore } from "@reduxjs/toolkit";

const store = configureStore({
  reducer: rootReducer,
  enhancers: (getDefaultEnhancers) =>
    getDefaultEnhancers().concat(Sentry.createReduxEnhancer()),
});
```

### 源映射设置（强烈推荐）

没有源映射，堆栈跟踪将显示压缩的代码。设置构建插件自动上传源映射：

**Vite (`vite.config.ts`)：**

```typescript
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { sentryVitePlugin } from "@sentry/vite-plugin";

export default defineConfig({
  build: { sourcemap: "hidden" },
  plugins: [
    react(),
    sentryVitePlugin({
      org: process.env.SENTRY_ORG,
      project: process.env.SENTRY_PROJECT,
      authToken: process.env.SENTRY_AUTH_TOKEN,
    }),
  ],
});
```

**Create React App（通过 CRACO）：**

```bash
npm install @craco/craco @sentry/webpack-plugin --save-dev
```

```javascript
// craco.config.js
const { sentryWebpackPlugin } = require("@sentry/webpack-plugin");

module.exports = {
  webpack: {
    plugins: {
      add: [
        sentryWebpackPlugin({
          org: process.env.SENTRY_ORG,
          project: process.env.SENTRY_PROJECT,
          authToken: process.env.SENTRY_AUTH_TOKEN,
        }),
      ],
    },
  },
};
```

`SENTRY_ORG` / `SENTRY_PROJECT` / `SENTRY_AUTH_TOKEN` 是构建时值；认证标头是秘密（永远不要提交它）。有关创建标头并将其连接到 CI 的信息，请参阅 [`sentry-source-maps`](../sentry-source-maps/SKILL.md)。

### 对于每个同意的功能

逐个功能进行操作。加载参考文件，按照其步骤操作，验证后再继续：

| 功能 | 参考 | 加载时... |
|------|------|----------|
| 错误监控 | `${SKILL_ROOT}/references/error-monitoring.md` | 始终（基线） |
| 跟踪 | `${SKILL_ROOT}/references/tracing.md` | SPA 导航 / API 调用跟踪 |
| 会话回放 | `${SKILL_ROOT}/references/session-replay.md` | 面向用户的应用程序 |
| 日志记录 | `${SKILL_ROOT}/references/logging.md` | 结构化日志搜索 / 日志到跟踪 |
| 性能分析 | `${SKILL_ROOT}/references/profiling.md` | 性能关键的应用程序 |
| React 功能 | `${SKILL_ROOT}/references/react-features.md` | Redux，组件跟踪，源映射，集成目录 |

对于每个功能：`读取 ${SKILL_ROOT}/references/<功能>.md`，精确跟随步骤，验证其是否正常工作。

---

## 配置参考

### `Sentry.init()` 的关键选项

| 选项 | 类型 | 默认值 | 备注 |
|------|------|--------|------|
| `dsn` | `string` | — | **必需。** SDK 在为空时禁用 |
| `environment` | `string` | `"production"` | 例如，`"staging"`，`"development"` |
| `release` | `string` | — | 例如，`"my-app@1.0.0"` 或 git SHA — 将错误链接到发布版本 |
| `dataCollection` | `object` | 保守，除非设置 | 对自动收集的类别进行细粒度控制（`userInfo`，`cookies`，`httpHeaders`，`httpBodies`，`queryParams`，`genAI`）。当省略时，SDK 回退到 `sendDefaultPii`（默认 `false`）。传递对象——即使 `{}`——会将未设置的类别切换到它们的宽松默认值；按类别选择退出。 |
| `tracesSampleRate` | `number` | — | 0–1；`1.0` 在开发中，`0.1–0.2` 在生产中 |
| `tracesSampler` | `function` | — | 按交易采样；覆盖比率 |
| `tracePropagationTargets` | `(string\|RegExp)[]` | — | 接收分布式跟踪标头的出站 URL |
| `replaysSessionSampleRate` | `number` | — | 记录所有会话的分数 |
| `replaysOnErrorSampleRate` | `number` | — | 记录错误会话的分数 |
| `enableLogs` | `boolean` | `false` | 启用 `Sentry.logger.*` API |
| `attachStacktrace` | `boolean` | `false` | 在 `captureMessage()` 调用上附加堆栈跟踪 |
| `maxBreadcrumbs` | `number` | `100` | 每个事件存储的面包屑数量 |
| `debug` | `boolean` | `false` | 控制台上的 SDK 详细输出 |
| `tunnel` | `string` | — | 跳过广告拦截器的代理 URL |

### `dataCollection` 选项（SDK ≥10.57.0）

对 SDK 收集的数据进行细粒度控制。收集默认为开启（带敏感值清理）；按类别选择退出：

| 字段 | 类型 | 默认值 | 备注 |
|------|------|--------|------|
| `userInfo` | `boolean` | `true` | 收集用户 ID、电子邮件和 IP |
| `cookies` | `boolean \| { allow: string[] } \| { deny: string[] }` | `true` | Cookie 收集和过滤；`true` = 所有 Cookie（敏感密钥被过滤） |
| `httpHeaders.request` | `boolean \| { allow: string[] } \| { deny: string[] }` | `true` | HTTP 请求标头收集 |
| `httpHeaders.response` | `boolean \| { allow: string[] } \| { deny: string[] }` | `true` | HTTP 响应标头收集 |
| `queryParams` | `boolean \| { allow: string[] } \| { deny: string[] }` | `true` | 查询参数收集和过滤 |
| `httpBodies` | `HttpBodyCollectionTarget[]` | `["incomingRequest", "outgoingRequest", "incomingResponse", "outgoingResponse"]` | 收集请求/响应对正文；选项：`'incomingRequest'`，`'outgoingRequest'`，`'incomingResponse'`，`'outgoingResponse'` |
| `genAI.inputs` | `boolean` | `true` | 记录 AI 模型输入（用于 AI 监控） |
| `genAI.outputs` | `boolean` | `true` | 记录 AI 模型输出（用于 AI 监控） |
| `stackFrameVariables` | `boolean` | `true` | 捕获堆栈帧中的局部变量值 |
| `frameContextLines` | `number` | `5` | 堆栈帧周围源代码上下文行数 |

**示例：** 仅允许特定 Cookie 和标头：

```typescript
Sentry.init({
  dataCollection: {
    cookies: { allow: ['session', 'user_id'] },
    httpHeaders: {
      request: { allow: ['authorization', 'x-request-id'] },
      response: { deny: ['set-cookie'] },
    },
  },
});
```

### React 兼容性矩阵

| React 版本 | 错误处理方法 | SDK 最小版本 |
|------------|--------------|---------------|
| React 19+ | `reactErrorHandler()` on `createRoot` | `@sentry/react` ≥8.0.0 |
| React 16–18 | `Sentry.ErrorBoundary` 组件 | `@sentry/react` ≥7.0.0 |
| React 16 | `componentDidCatch` 类边界 | `@sentry/react` ≥6.0.0 |

---

## 验证

触发测试事件以确认 Sentry 是否接收数据：

```tsx
// 在应用程序的任何地方添加一个临时的测试按钮
import * as Sentry from "@sentry/react";

function SentryTest() {
  return (
    <>
      <button onClick={() => { throw new Error("Sentry React 测试错误"); }}>
        测试错误
      </button>
      <button onClick={() => Sentry.captureMessage("Sentry 测试消息", "info")}>
        测试消息
      </button>
    </>
  );
}
```

检查 Sentry 仪表板：
- **问题** → 错误在几秒钟内出现
- **跟踪** → 页面加载和导航事务可见
- **回放** → 页面交互后可见会话记录
- **日志** → 如果启用了日志记录，则可见结构化日志条目

在 `Sentry.init()` 中设置 `debug: true` 并检查浏览器控制台，如果没有任何内容出现。

---

## 第四阶段：跨链接

完成 React 设置后，检查是否缺少 Sentry 覆盖的配套后端：

```bash
ls ../backend ../server ../api ../go ../python 2>/dev/null
cat ../go.mod 2>/dev/null | head -3
cat ../requirements.txt ../pyproject.toml 2>/dev/null | head -3
cat ../Gemfile 2>/dev/null | head -3
cat ../pom.xml 2>/dev/null | grep '<artifactId>' | head -3
```

如果存在未配置 Sentry 的后端，建议匹配的技能：

| 后端检测到 | 建议技能 |
|------------|----------|
| Go (`go.mod`) | `sentry-go-sdk` |
| Python (`requirements.txt`，`pyproject.toml`) | `sentry-python-sdk` |
| Ruby (`Gemfile`) | `sentry-ruby-sdk` |
| Java (`pom.xml`，`build.gradle`) | 使用 `@sentry/java` — 见 [docs.sentry.io/platforms/java/](https://docs.sentry.io/platforms/java/) |
| Node.js (Express, Fastify) | 使用 `@sentry/node` — 见 [docs.sentry.io/platforms/javascript/guides/express/](https://docs.sentry.io/platforms/javascript/guides/express/) |

---

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| 事件未出现 | 设置 `debug: true`，检查 DSN，检查浏览器控制台中的 SDK 错误 |
| 源映射不工作 | 在生产模式下构建（`npm run build`）；验证 `SENTRY_AUTH_TOKEN` 是否设置 |
| 压缩的堆栈跟踪 | 源映射未上传——检查插件配置和认证标头 |
| `instrument.ts` 未首先运行 | 验证它是在入口文件中 React/应用程序导入之前的第一行导入 |
| React 19 错误未捕获 | 确认 `reactErrorHandler()` 传递给所有三个 `createRoot` 选项 |
| React <19 错误未捕获 | 确保 `<Sentry.ErrorBoundary>` 包裹组件树 |
| 路由事务命名为 `<unknown>` | 添加匹配你的路由版本的路由集成 |
| `tracePropagationTargets` 不匹配 | 检查正则表达式转义；默认是 `localhost` 和你的 DSN 起源仅 |
| 会话回放未记录 | 确认 `replayIntegration()` 在 init 中；检查 `replaysSessionSampleRate` |
| Redux 操作未在面包屑中 | 向存储增强器添加 `Sentry.createReduxEnhancer()` |
| 广告拦截器丢弃事件 | 设置 `tunnel: "/sentry-tunnel"` 并添加服务器端中继端点 |
| 高回放存储成本 | 降低 `replaysSessionSampleRate`；保持 `replaysOnErrorSampleRate: 1.0` |
| 性能分析未工作 | 验证 `Document-Policy: js-profiling` 标头是否在文档响应中设置 |
