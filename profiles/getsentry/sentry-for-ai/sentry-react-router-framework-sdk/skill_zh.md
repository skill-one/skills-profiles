> [所有技能](../../SKILL_TREE.md) > [SDK 安装设置](../sentry-sdk-setup/SKILL.md) > React Router Framework SDK

# Sentry React Router Framework SDK

一个有主见的向导，它会扫描您的 React Router Framework 项目，并指导您完成在客户端和服务器入口点上的完整 Sentry 设置。

## 在何时调用此技能

- 用户询问“将 Sentry 添加到 React Router Framework”或“在 React Router v7 框架模式下设置 Sentry”
- 用户想要安装或配置 `@sentry/react-router`
- 用户使用 React Router 框架入口文件（`entry.client.tsx`，`entry.server.tsx`）并希望进行跟踪/错误捕获
- 用户询问关于 `reactRouterTracingIntegration`，`sentryOnError`，`createSentryHandleRequest` 或 React Router 向导设置

> **重要提示：** 此 SDK 目前处于 Beta 版本。
> 对于 React Router 非框架/数据/声明式模式（v5/v6/v7），请使用带有 `@sentry/react` 集成的 `sentry-react-sdk`。

---

## 第一阶段：检测

在提出任何建议之前，运行以下命令以了解项目：

```bash
# 检测 React Router Framework 指示器和版本
cat package.json | grep -E '"react-router"|"@react-router/"|"react-router-dev"|"react-router-serve"'

# 检测 Sentry 包选择
cat package.json | grep -E '"@sentry/react-router"|"@sentry/react"|"@sentry/profiling-node"'

# 检查入口点的可见性和服务器仪器文件
ls entry.client.tsx entry.server.tsx instrument.server.mjs react-router.config.ts vite.config.ts 2>/dev/null

# 检查 React Router 文件是否仍然隐藏（框架模式辅助命令可用）
cat package.json | grep -E '"reveal"|react-router'

# 检测运行时启动脚本和导入策略
cat package.json | grep -E '"dev"|"start"|NODE_OPTIONS|--import'

# 检测可选的日志/分析相关依赖
cat package.json | grep -E '"pino"|"winston"|"@sentry/profiling-node"'

# 检测配套后端目录
ls ../backend ../server ../api 2>/dev/null
cat ../go.mod ../requirements.txt ../Gemfile ../pom.xml 2>/dev/null | head -3
```

**需要确定的内容：**

| 问题 | 影响 |
|------|------|
| `@sentry/react-router` 已安装？ | 跳过安装并进入功能设置 |
| 框架入口文件是否暴露？ | 需要在手动配置之前运行 `npx react-router reveal` |
| 使用 `@sentry/react` 而不是？ | 这可能是非框架路由；重定向到 `sentry-react-sdk` |
| `react-router.config.ts` + Vite 配置存在？ | 源映射上传和构建末尾钩子设置路径 |
| `NODE_OPTIONS --import` 可用？ | 服务器仪器启动的首选路径 |
| `@sentry/profiling-node` 需要/可用？ | 启用服务器分析集成 |
| 发现后端目录？ | 触发第四阶段的跨链接建议 |

---

## 第二阶段：建议

根据您发现的内容，提出具体的建议，不要提出开放式问题——直接提出建议：

**建议（核心覆盖）：**
- ✅ **错误监控** — 总是；使用框架钩子捕获客户端和服务器错误
- ✅ **跟踪** — 推荐框架应用中的客户端/服务器请求流程的基线
- ✅ **会话回放** — 推荐用于面向用户的应用程序

**可选（增强的可观察性）：**
- ⚡ **分析** — 使用 `@sentry/profiling-node` 的服务器端分析
- ⚡ **日志** — 结构化的 `Sentry.logger.*` 摄入和关联
- ⚡ **用户反馈** — 应用内反馈小部件/报告流程

**建议逻辑：**

| 功能 | 当...推荐 |
|------|----------|
| 错误监控 | **总是** — 不可协商的基线 |
| 跟踪 | **通常是的** 在框架应用中；路由和请求时间具有高价值 |
| 会话回放 | 面向用户的产品或难以调试的 UX |
| 分析 | 需要服务器性能分析；验证 Node 运行时兼容性 |
| 日志 | 团队希望在 Sentry 中进行日志搜索和跟踪关联 |
| 用户反馈 | 产品/支持团队需要直接的应用内问题报告 |

建议：*"我建议首先启用错误监控 + 跟踪 + 会话回放。您还需要我启用分析、日志和用户反馈吗？"**

---

## 第三阶段：指导

### 选项 1：向导（推荐）

> **您需要自己运行** — 向导是交互式的，可能需要浏览器登录：
>
> ```bash
> npx @sentry/wizard@latest -i reactRouter
> ```
>
> 它安装 `@sentry/react-router`，暴露 React Router 入口文件，创建仪器文件，更新根错误处理，配置源映射上传，并添加验证示例。
>
> **完成后，继续到 [验证](#verification)。**

如果用户跳过向导设置，请继续执行以下手动设置。

---

### 选项 2：手动设置

#### 安装包

```bash
npm install @sentry/react-router --save
```

如果需要分析：

```bash
npm install @sentry/profiling-node --save
```

#### 暴露框架入口文件

```bash
npx react-router reveal
```

#### 在 `entry.client.tsx` 中配置客户端

```tsx
import * as Sentry from "@sentry/react-router";
import { startTransition, StrictMode } from "react";
import { hydrateRoot } from "react-dom/client";
import { HydratedRouter } from "react-router/dom";

Sentry.init({
  dsn: "___PUBLIC_DSN___",
  dataCollection: {
    // 要禁用发送用户数据和 HTTP 正文，请取消以下行的注释。更多信息请访问：
    // https://docs.sentry.io/platforms/javascript/guides/react-router/configuration/options/#dataCollection
    // userInfo: false,
    // httpBodies: [],
  },
  integrations: [
    Sentry.reactRouterTracingIntegration(),
    Sentry.replayIntegration(),
    Sentry.feedbackIntegration({ colorScheme: "system" }),
  ],
  enableLogs: true,
  tracesSampleRate: 1.0,
  tracePropagationTargets: [/^\//, /^https:\/\/yourserver\.io\/api/],
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
});

startTransition(() => {
  hydrateRoot(
    document,
    <StrictMode>
      <HydratedRouter onError={Sentry.sentryOnError} />
    </StrictMode>,
  );
});
```

#### 在 `instrument.server.mjs` 中配置服务器

```javascript
import * as Sentry from "@sentry/react-router";
import { nodeProfilingIntegration } from "@sentry/profiling-node";

Sentry.init({
  dsn: "___PUBLIC_DSN___",
  dataCollection: {
    // 要禁用发送用户数据和 HTTP 正文，请取消以下行的注释。更多信息请访问：
    // https://docs.sentry.io/platforms/javascript/guides/react-router/configuration/options/#dataCollection
    // userInfo: false,
    // httpBodies: [],
  },
  enableLogs: true,
  integrations: [nodeProfilingIntegration()],
  tracesSampleRate: 1.0,
  profileSessionSampleRate: 1.0,
});
```

#### 在 `entry.server.tsx` 中包装服务器处理程序

```tsx
import * as Sentry from "@sentry/react-router";
import { createReadableStreamFromReadable } from "@react-router/node";
import { renderToPipeableStream } from "react-dom/server";
import { ServerRouter } from "react-router";

const handleRequest = Sentry.createSentryHandleRequest({
  ServerRouter,
  renderToPipeableStream,
  createReadableStreamFromReadable,
});

export default handleRequest;

export const handleError = Sentry.createSentryHandleError({
  logErrors: false,
});
```

对于自定义服务器逻辑，使用 `wrapSentryHandleRequest`，`getMetaTagTransformer`，并在自定义 `handleError` 中手动 `Sentry.captureException`。

#### 在启动时加载服务器仪器

首选 `NODE_OPTIONS --import`：

```json
{
  "scripts": {
    "dev": "NODE_OPTIONS='--import ./instrument.server.mjs' react-router dev",
    "start": "NODE_OPTIONS='--import ./instrument.server.mjs' react-router-serve ./build/server/index.js"
  }
}
```

对于限制运行时标志的平台：

```tsx
import "./instrument.server.mjs";
```

此直接导入方法与 `--import` 相比可能导致自动仪器不完整。

#### 配置源映射

`vite.config.ts`：

```typescript
import { reactRouter } from "@react-router/dev/vite";
import {
  sentryReactRouter,
  type SentryReactRouterBuildOptions,
} from "@sentry/react-router";
import { defineConfig } from "vite";

const sentryConfig: SentryReactRouterBuildOptions = {
  org: "___ORG_SLUG___",
  project: "___PROJECT_SLUG___",
  authToken: process.env.SENTRY_AUTH_TOKEN,
};

export default defineConfig((config) => {
  return {
    plugins: [reactRouter(), sentryReactRouter(sentryConfig, config)],
  };
});
```

`react-router.config.ts`：

```typescript
import type { Config } from "@react-router/dev/config";
import { sentryOnBuildEnd } from "@sentry/react-router";

export default {
  ssr: true,
  buildEnd: async ({ viteConfig, reactRouterConfig, buildManifest }) => {
    await sentryOnBuildEnd({ viteConfig, reactRouterConfig, buildManifest });
  },
} satisfies Config;
```

---

对于每个同意的功能

逐个通过功能。加载参考文件，精确跟随步骤，并在继续之前进行验证：

| 功能 | 参考文件 | 加载时... |
|------|----------|----------|
| 错误监控 | `${SKILL_ROOT}/references/error-monitoring.md` | 总是 |
| 跟踪 | `${SKILL_ROOT}/references/tracing.md` | 需要路由/请求性能可见性 |
| 分析 | `${SKILL_ROOT}/references/profiling.md` | 需要服务器性能分析 |
| 会话回放 | `${SKILL_ROOT}/references/session-replay.md` | 面向用户的应用 |
| 日志 | `${SKILL_ROOT}/references/logging.md` | 需要结构化日志/关联 |
| 用户反馈 | `${SKILL_ROOT}/references/user-feedback.md` | 需要应用内反馈流程 |
| 框架功能 | `${SKILL_ROOT}/references/react-router-framework-features.md` | 入口文件、包装器、源映射、启动导入策略 |

对于每个功能：`读取 ${SKILL_ROOT}/references/<功能>.md`，精确跟随步骤，验证其是否正常工作。

---

## 配置参考

### `Sentry.init()` 的关键选项

| 选项 | 类型 | 默认值 | 备注 |
|------|------|--------|------|
| `dsn` | `string` | — | 必须的；为空时 SDK 禁用 |
| `dataCollection` | `object` | — | 控制收集的数据（userInfo、cookies、httpHeaders 等） |
| `dataCollection.userInfo` | `boolean` | `true` | 包括基于 IP 的用户上下文 |
| `dataCollection.cookies` | `CollectBehavior` | `true` | 控制 cookie 收集和过滤 |
| `dataCollection.httpHeaders` | `object` | `{ request: true, response: true }` | 控制 HTTP 标头收集 |
| `sendDefaultPii` | `boolean` | `false` | **已弃用：** 使用 `dataCollection` 代替；v11 中已移除 |
| `integrations` | `Integration[]` | SDK 默认值 | 添加跟踪/回放/反馈/分析集成 |
| `enableLogs` | `boolean` | `false` | 启用 `Sentry.logger.*` 摄入 |
| `tracesSampleRate` | `number` | — | 测试中通常是 `1.0`，生产中较低 |
| `tracePropagationTargets` | `(string|RegExp)[]` | SDK 默认值 | 接收跟踪标头的 URL |
| `replaysSessionSampleRate` | `number` | — | 记录所有会话的分数 |
| `replaysOnErrorSampleRate` | `number` | — | 记录错误会话的分数 |
| `profileSessionSampleRate` | `number` | — | 被分析的交易分数（服务器分析） |
| `tunnel` | `string` | — | 可选的绕过广告拦截器端点 |
| `debug` | `boolean` | `false` | SDK 详细诊断 |

### 框架特定 API

| API | 目的 |
|------|------|
| `reactRouterTracingIntegration()` | 框架模式的客户端跟踪集成 |
| `sentryOnError` | 钩入 React Router `HydratedRouter` 错误报告 |
| `createSentryHandleRequest(...)` | 框架入口服务器请求包装器 |
| `createSentryHandleError(...)` | 服务器错误处理包装器 |
| `wrapServerLoader(...)` / `wrapServerAction(...)` | 手动包装服务器加载器/动作 |
| `sentryReactRouter(...)` | Vite 插件，用于源映射/构建集成 |
| `sentryOnBuildEnd(...)` | React Router 构建末尾钩子，用于源映射处理 |

---

## 验证

### 向导生成的路径

如果生成了向导示例，请打开 `/sentry-example-page` 并触发测试操作。

### 手动错误测试

```tsx
export async function loader() {
  throw new Error("我的第一个 Sentry 错误！");
}
```

### 手动跟踪测试

```tsx
import * as Sentry from "@sentry/react-router";

export async function loader() {
  return Sentry.startSpan(
    { op: "test", name: "我的第一个测试交易" },
    () => {
      throw new Error("我的第一个 Sentry 错误！");
    },
  );
}
```

### 日志测试

```javascript
Sentry.logger.info("用户示例操作完成");
Sentry.logger.warn("检测到慢操作", { operation: "data_fetch", duration: 3500 });
Sentry.logger.error("验证失败", { field: "email", reason: "无效的电子邮件" });
```

在 Sentry 中确认：
- **问题**：错误出现
- **跟踪**：交易/跨度数据出现
- **分析**：启用分析时出现分析
- **回放**：启用时出现回放条目
- **日志**：`enableLogs: true` 时出现日志事件
- **用户反馈**：启用时出现提交

---

## 第四阶段：跨链接

完成 React Router Framework 设置后：

1. 检查应用程序是否实际上是非框架路由（v5/v6/v7 数据/声明式，使用 `@sentry/react`）。
2. 如果是，重定向到 `sentry-react-sdk` 以进行非框架路由集成。

然后检查配套后端覆盖范围：

```bash
ls ../backend ../server ../api ../go ../python 2>/dev/null
cat ../go.mod ../requirements.txt ../pyproject.toml ../Gemfile ../pom.xml 2>/dev/null | head -5
```

| 后端检测 | 建议技能 |
|----------|----------|
| Go | `sentry-go-sdk` |
| Python | `sentry-python-sdk` |
| Ruby | `sentry-ruby-sdk` |
| Node 后端服务 | `sentry-node-sdk` |
| Java 服务 | 使用 `@sentry/java` 文档 |

---

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| `entry.client.tsx` / `entry.server.tsx` 缺失 | 首先运行 `npx react-router reveal` |
| 客户端错误缺失 | 确保 `HydratedRouter` 包括 `onError={Sentry.sentryOnError}` |
| 服务器错误缺失 | 使用 `createSentryHandleRequest` 和 `createSentryHandleError` 包装器 |
| 自定义服务器处理程序绕过 Sentry | 使用 `wrapSentryHandleRequest` 和在自定义 `handleError` 中手动 `captureException` |
| 源映射未上传 | 验证 `sentryReactRouter` 插件配置和 `sentryOnBuildEnd` 钩子 |
| Vite 配置中 `SENTRY_AUTH_TOKEN` 未定义 | 在配置中加载环境变量或使用 `.env.sentry-build-plugin` |
| 服务器自动仪器不完整 | 首选 `NODE_OPTIONS='--import ./instrument.server.mjs'` 启动 |
| 分析数据缺失 | 确认 `@sentry/profiling-node` 已安装并启用 `nodeProfilingIntegration` |
| 运行不支持的 Node 自动仪器版本 | 使用文档中记录的仪器 API/手动包装器 |
| 使用 `@sentry/react-router` 配置非框架应用 | 切换到 `sentry-react-sdk` + `@sentry/react` 以进行 v5/v6/v7 非框架路由 |
