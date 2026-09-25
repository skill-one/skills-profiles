> [所有技能](../../SKILL_TREE.md) > [SDK 安装](../sentry-sdk-setup/SKILL.md) > TanStack Start React SDK

# Sentry TanStack Start React SDK

一个有倾向性的向导，它会扫描您的 TanStack Start React 项目，并指导您完成浏览器和服务器运行时的完整 Sentry 设置。

## 在何时调用此技能

- 用户询问在 TanStack Start React 应用中“添加 Sentry”或“设置 Sentry”
- 用户想要安装或配置 `@sentry/tanstackstart-react`
- 用户想要为 TanStack Start React 添加错误监控、跟踪、会话回放、日志或用户反馈
- 用户询问关于 `sentryTanstackStart`、`wrapFetchWithSentry`、`instrument.server.mjs` 或 TanStack Start 中间件仪器化的问题

> **注意：** 此 SDK 目前处于 alpha 版本，并文档化为与 TanStack Start `1.0 RC` 兼容。
> 在实施之前，请始终参考 [docs.sentry.io/platforms/javascript/guides/tanstackstart-react/](https://docs.sentry.io/platforms/javascript/guides/tanstackstart-react/) 进行验证。

---

## 第一阶段：检测

在提出任何建议之前，运行这些命令以了解项目：

```bash
# 检测 TanStack Start / Router 和现有的 Sentry
cat package.json | grep -E '"@tanstack/react-start"|"@tanstack/react-router"|"@sentry/tanstackstart-react"'

# 检查 Sentry 是否已经存在
cat package.json | grep '"@sentry/'

# 检测 TanStack Start 设置使用的关键文件
ls src/router.tsx src/start.ts src/server.ts instrument.server.mjs vite.config.ts vite.config.js 2>/dev/null

# 检查是否配置了源映射上传凭证
cat .env .env.local .env.sentry-build-plugin 2>/dev/null | grep "SENTRY_AUTH_TOKEN"

# 检测脚本中的部署提示
cat package.json | grep -E '"dev"|"build"|"start"|NODE_OPTIONS|--import'

# 检测日志库
cat package.json | grep -E '"pino"|"winston"|"loglevel"'

# 检测配套后端目录
ls ../backend ../server ../api 2>/dev/null
cat ../go.mod ../requirements.txt ../Gemfile ../pom.xml 2>/dev/null | head -3
```

**需要确定的内容：**

| 问题 | 影响 |
|----------|--------|
| `@tanstack/react-start` 存在？ | 确认此技能是正确的设置路径 |
| `@sentry/tanstackstart-react` 已经安装？ | 跳过安装并进入功能微调 |
| `src/router.tsx` 存在？ | 客户端 `Sentry.init` 位置 |
| `src/start.ts` 存在？ | 服务器端错误的全局中间件设置 |
| `src/server.ts` 存在？ | 服务器入口仪器化位置 |
| `instrument.server.mjs` 存在？ | 运行时启动仪器化路径 |
| `vite.config.ts` 存在？ | 添加 `sentryTanstackStart` 插件和源映射 |
| `SENTRY_AUTH_TOKEN` 配置？ | 源映射上传准备就绪 |
| 后端目录找到？ | 触发第四阶段跨链接建议 |

---

## 第二阶段：建议

根据您发现的内容提出具体的建议。不要提出开放式问题——直接提出建议：

**建议（核心覆盖）：**
- ✅ **错误监控** — 总是；捕获未处理的客户端和服务器错误
- ✅ **跟踪** — 对浏览器和服务器请求和路由时间的高价值
- ✅ **会话回放** — 推荐用于面向用户的应用程序

**可选（增强可观察性）：**
- ⚡ **日志** — 当需要结构化日志搜索和日志到跟踪关联时推荐
- ⚡ **用户反馈** — 当产品团队想要应用内问题报告时推荐

**建议逻辑：**

| 功能 | 当...建议 |
|---------|------------------|
| 错误监控 | **总是** — 不可协商的基线 |
| 跟踪 | **通常是的** 对于 TanStack Start；路由 + fetch 仪器化立即提供价值 |
| 会话回放 | 面向用户的应用程序、登录流程、结账流程或难以复制的 UX 错误 |
| 日志 | 现有的日志策略、支持工作流或跟踪/日志关联需求 |
| 用户反馈 | 团队希望在不离开应用程序的情况下直接获取用户报告 |

建议：*"我建议 Error Monitoring + Tracing + Session Replay。您希望我同时启用 Logs 和 User Feedback 吗？*"

---

## 第三阶段：指导

### 安装

```bash
npm install @sentry/tanstackstart-react --save
```

### 在 `src/router.tsx` 中配置客户端 Sentry

在路由工厂内部初始化 Sentry，并将其限制在浏览器中：

```tsx
import * as Sentry from "@sentry/tanstackstart-react";
import { createRouter } from "@tanstack/react-router";

export const getRouter = () => {
  const router = createRouter();

  if (!router.isServer) {
    Sentry.init({
      dsn: "___PUBLIC_DSN___",
      dataCollection: {
        // userInfo: false,
        // httpBodies: [],
      },

      integrations: [
        Sentry.tanstackRouterBrowserTracingIntegration(router),
        Sentry.replayIntegration(),
        Sentry.feedbackIntegration({
          colorScheme: "system",
        }),
      ],

      enableLogs: true,
      tracesSampleRate: 1.0,
      replaysSessionSampleRate: 0.1,
      replaysOnErrorSampleRate: 1.0,
    });
  }

  return router;
};
```

### 在 `instrument.server.mjs` 中配置服务器端 Sentry

在项目根目录创建 `instrument.server.mjs`：

```javascript
import * as Sentry from "@sentry/tanstackstart-react";

Sentry.init({
  dsn: "___PUBLIC_DSN___",
  dataCollection: {
    // 要禁用发送用户数据和 HTTP 正文，请取消以下行的注释。更多信息请访问：
    // https://docs.sentry.io/platforms/javascript/guides/tanstackstart-react/configuration/options/#dataCollection
    // userInfo: false,
    // httpBodies: [],
  },
  enableLogs: true,
  tracesSampleRate: 1.0,
});
```

### 在 `vite.config.ts` 中配置 Vite 插件

`sentryTanstackStart` 应该是最后一个插件：

```typescript
import { defineConfig } from "vite";
import { sentryTanstackStart } from "@sentry/tanstackstart-react/vite";
import { tanstackStart } from "@tanstack/react-start/plugin/vite";

export default defineConfig({
  plugins: [
    tanstackStart(),
    sentryTanstackStart({
      org: "___ORG_SLUG___",
      project: "___PROJECT_SLUG___",
      authToken: process.env.SENTRY_AUTH_TOKEN,
    }),
  ],
});
```

如果令牌存储在 `.env` 中，请在 Vite 配置中使用 `loadEnv` 在将其传递给插件之前加载它。

### 在 `src/server.ts` 中仪器化服务器入口点

用 `wrapFetchWithSentry` 包裹 fetch 处理程序：

```typescript
import { wrapFetchWithSentry } from "@sentry/tanstackstart-react";
import handler, { createServerEntry } from "@tanstack/react-start/server-entry";

export default createServerEntry(
  wrapFetchWithSentry({
    fetch(request: Request) {
      return handler.fetch(request);
    },
  }),
);
```

### 在 `src/start.ts` 中添加全局服务器中间件

这些中间件捕获服务器端请求和函数错误：

```tsx
import {
  sentryGlobalFunctionMiddleware,
  sentryGlobalRequestMiddleware,
} from "@sentry/tanstackstart-react";
import { createStart } from "@tanstack/react-start";

export const startInstance = createStart(() => {
  return {
    requestMiddleware: [sentryGlobalRequestMiddleware],
    functionMiddleware: [sentryGlobalFunctionMiddleware],
  };
});
```

Sentry 中间件应在每个数组中首先出现。

### 运行时启动模式

选择一种运行时方法：

| 运行时模式 | 当...使用 | 备注 |
|---|---|---|
| `--import` 标志 | 您可以控制 Node 启动标志 | 生产监控的首选 |
| 在 `src/server.ts` 中直接导入 | 主机限制启动标志（例如无服务器主机） | 限制仪器化到原生 Node API |

`--import` 示例：

```json
{
  "scripts": {
    "dev": "NODE_OPTIONS='--import ./instrument.server.mjs' vite dev --port 3000",
    "build": "vite build && cp instrument.server.mjs .output/server",
    "start": "node --import ./.output/server/instrument.server.mjs .output/server/index.mjs"
  }
}
```

直接导入回退（`src/server.ts` 的顶部）：

```typescript
import "../instrument.server.mjs";
```

### 对于每个同意的功能

逐个介绍功能。加载参考文件，按步骤操作，并在继续之前进行验证：

| 功能 | 参考 | 加载时... |
|---------|-----------|-------------|
| 错误监控 | `${SKILL_ROOT}/references/error-monitoring.md` | 总是 |
| 跟踪 | `${SKILL_ROOT}/references/tracing.md` | 需要路由/API 性能可见性 |
| 会话回放 | `${SKILL_ROOT}/references/session-replay.md` | 面向用户的应用程序 |
| 日志 | `${SKILL_ROOT}/references/logging.md` | 需要结构化日志和关联 |
| 用户反馈 | `${SKILL_ROOT}/references/user-feedback.md` | 需要在应用程序内收集反馈 |
| TanStack Start 功能 | `${SKILL_ROOT}/references/tanstackstart-features.md` | 服务器入口、Vite 插件、源映射、运行时启动 |

对于每个功能：`读取 ${SKILL_ROOT}/references/<功能>.md`，按步骤操作，验证其是否正常工作。

---

## 配置参考

### `Sentry.init()` 的关键选项

| 选项 | 类型 | 默认值 | 备注 |
|--------|------|---------|-------|
| `dsn` | `string` | — | 必须的；当为空时，SDK 被禁用 |
| `dataCollection` | `object` | 保守，除非设置 | 对自动收集的类别（`userInfo`、`cookies`、`httpHeaders`、`httpBodies`、`queryParams`、`genAI`）进行细粒度控制。省略对象时，SDK 会回退到 `sendDefaultPii`（默认 `false`）。传递对象——即使 `{}`——会将未设置的类别切换到它们的允许默认值；按类别选择退出。 |
| `integrations` | `Integration[]` | SDK 默认 | 根据需要包含 TanStack Router 跟踪、回放、反馈 |
| `enableLogs` | `boolean` | `false` | 启用 `Sentry.logger.*` API |
| `tracesSampleRate` | `number` | — | 开发中为 `1.0`，生产中为较低值 |
| `replaysSessionSampleRate` | `number` | — | 记录所有会话的分数 |
| `replaysOnErrorSampleRate` | `number` | — | 记录错误会话的分数 |
| `tunnel` | `string` | — | 可选的 ad-blocker 跳过端点 |
| `debug` | `boolean` | `false` | SDK 诊断日志 |

### TanStack Start 特定 API

| API | 目的 |
|-----|---------|
| `tanstackRouterBrowserTracingIntegration(router)` | 浏览器导航跟踪 |
| `wrapFetchWithSentry(...)` | 服务器请求跟踪 + fetch 处理程序上的错误捕获 |
| `sentryGlobalRequestMiddleware` | 捕获请求级服务器错误 |
| `sentryGlobalFunctionMiddleware` | 捕获服务器函数错误 |
| `sentryTanstackStart({...})` | 用于源映射和中间件仪器化的 Vite 插件 |

---

## 验证

触发测试事件以确认 Sentry 接收数据。

### 问题测试（前端）

```tsx
<button
  type="button"
  onClick={() => {
    throw new Error("Sentry Test Error");
  }}
>
  破坏世界
</button>
```

### 跟踪测试（前端 + API 路由）

```tsx
<button
  type="button"
  onClick={async () => {
    await Sentry.startSpan({ name: "Example Frontend Span", op: "test" }, async () => {
      const res = await fetch("/api/sentry-example");
      if (!res.ok) {
        throw new Error("Sentry Example Frontend Error");
      }
    });
  }}
>
  破坏世界
</button>
```

### 日志测试

```javascript
Sentry.logger.info("User example action completed");
Sentry.logger.warn("Slow operation detected", { operation: "data_fetch", duration: 3500 });
Sentry.logger.error("Validation failed", { field: "email", reason: "Invalid email" });
```

在 Sentry 中确认：
- **问题**：前端/服务器错误出现
- **跟踪**：浏览器和服务器跨度出现
- **回放**：启用时出现会话回放
- **日志**：当 `enableLogs: true` 时出现日志行
- **用户反馈**：当反馈集成启用时出现提交

---

## 第四阶段：跨链接

完成 TanStack Start 设置后，检查是否存在未配置 Sentry 的配套后端：

```bash
ls ../backend ../server ../api ../go ../python 2>/dev/null
cat ../go.mod ../requirements.txt ../pyproject.toml ../Gemfile ../pom.xml 2>/dev/null | head -5
```

如果后端未配置 Sentry，建议匹配的技能：

| 后端检测 | 建议技能 |
|------------------|--------------|
| Go (`go.mod`) | `sentry-go-sdk` |
| Python (`requirements.txt`, `pyproject.toml`) | `sentry-python-sdk` |
| Ruby (`Gemfile`) | `sentry-ruby-sdk` |
| Java (`pom.xml`, `build.gradle`) | 使用 `@sentry/java` 文档 |
| Node.js 后端服务 | `sentry-node-sdk` |

---

## 故障排除

| 问题 | 解决方案 |
|-------|----------|
| 事件未出现 | 设置 `debug: true`，验证 DSN，并确保客户端/服务器初始化文件都运行 |
| 没有服务器跟踪 | 确认 `src/server.ts` 使用 `wrapFetchWithSentry` 并运行时加载 `instrument.server.mjs` |
| 路由处理程序中缺少服务器错误 | 确保 `sentryGlobalRequestMiddleware` 和 `sentryGlobalFunctionMiddleware` 在数组中首先出现 |
| 源映射无法解析 | 验证 `sentryTanstackStart` 配置中的 `SENTRY_AUTH_TOKEN`、`org` 和 `project` |
| Vite 配置中 `SENTRY_AUTH_TOKEN` 未定义 | 使用 `loadEnv(mode, process.cwd(), "")` 或 `.env.sentry-build-plugin` |
| 回放未记录 | 确保 `replayIntegration()` 在 `integrations` 中，且样本率非零 |
| 反馈小部件不可见 | 确认 `feedbackIntegration()` 已配置并检查 CSS z-index 冲突 |
| Sentry 中缺少日志 | 设置 `enableLogs: true` 并使用 `Sentry.logger.*` API |
| 直接导入设置遗漏库跨度 | 尽可能使用 `--import` 启动；直接导入仅支持原生 Node 仪器化 |
| SSR 渲染异常未自动捕获 | 使用 `Sentry.captureException` 在错误边界/回退处理程序中手动捕获 |
