> [所有技能](../../SKILL_TREE.md) > [SDK 安装](../sentry-sdk-setup/SKILL.md) > Next.js SDK

# Sentry Next.js SDK

一个有主见的向导，它会扫描您的 Next.js 项目，并指导您在所有三个运行时（浏览器、Node.js 服务器和 Edge）中完成 Sentry 的完整设置。

## 在何时调用此技能

- 用户询问在 Next.js 应用中“添加 Sentry”或“设置 Sentry”
- 用户想要安装或配置 `@sentry/nextjs`
- 用户想要为 Next.js 添加错误监控、跟踪、会话回放、日志记录或性能分析
- 用户询问关于 `instrumentation.ts`、`withSentryConfig()` 或 `global-error.tsx`
- 用户想要捕获服务器操作、服务器组件错误或 Edge 运行时错误

> **注意：** 以下 SDK 版本和 API 反映了编写本文时 Sentry 文档的当前状态（`@sentry/nextjs` ≥8.28.0）。
> 在实施之前，请始终参考 [docs.sentry.io/platforms/javascript/guides/nextjs/](https://docs.sentry.io/platforms/javascript/guides/nextjs/) 进行验证。

---

## 第一阶段：检测

在提出任何建议之前，运行这些命令以了解项目：

```bash
# 检测 Next.js 版本和现有的 Sentry
cat package.json | grep -E '"next"|"@sentry/'

# 检测路由类型（应用路由器 vs 页面路由器）
ls src/app app src/pages pages 2>/dev/null

# 检查现有的 Sentry 配置文件
ls instrumentation.ts instrumentation-client.ts sentry.server.config.ts sentry.edge.config.ts 2>/dev/null
ls src/instrumentation.ts src/instrumentation-client.ts 2>/dev/null

# 检查 next.config
ls next.config.ts next.config.js next.config.mjs 2>/dev/null

# 检查现有的错误边界
find . -name "global-error.tsx" -o -name "_error.tsx" 2>/dev/null | grep -v node_modules

# 检查构建工具
cat package.json | grep -E '"turbopack"|"webpack"'

# 检查日志记录库
cat package.json | grep -E '"pino"|"winston"|"bunyan"'

# 检查配套后端
ls ../backend ../server ../api 2>/dev/null
cat ../go.mod ../requirements.txt ../Gemfile 2>/dev/null | head -3
```

**需要确定的内容：**

| 问题 | 影响 |
|----------|--------|
| Next.js 版本？ | 需要 13+；15+ 需要 Turbopack 支持 |
| 应用路由器或页面路由器？ | 确定需要的错误边界文件（`global-error.tsx` vs `_error.tsx`） |
| `@sentry/nextjs` 已存在？ | 跳过安装，进入功能配置 |
| 现有的 `instrumentation.ts`？ | 将 Sentry 合并到其中，而不是替换 |
| 使用 Turbopack？ | 树形拆解仅在 `withSentryConfig` 中是 webpack 专属 |
| 检测到日志记录库？ | 推荐 Sentry 日志集成 |
| 找到后端目录？ | 触发第四阶段跨链接建议 |

---

## 第二阶段：建议

根据您发现的内容提出具体的建议，不要提出开放式问题——直接提出建议：

**推荐（核心覆盖）：**
- ✅ **错误监控** — 总是；捕获服务器错误、客户端错误、服务器操作和未处理的 Promise 拒绝
- ✅ **跟踪** — 服务器端请求跟踪 + 客户端导航跨所有运行时的跨度
- ✅ **会话回放** — 推荐用于面向用户的 App；记录错误周围的会话

**可选（增强可观察性）：**
- ⚡ **日志记录** — 通过 `Sentry.logger.*` 的结构化日志；当需要 `pino`/`winston` 或日志搜索时推荐
- ⚡ **性能分析** — 持续性能分析；需要 `Document-Policy: js-profiling` 标头
- ⚡ **AI 监控** — OpenAI、Vercel AI SDK、Anthropic；当检测到 AI/LLM 调用时推荐
- ⚡ **Crons** — 检测遗漏/失败的计划任务；当检测到 cron 模式时推荐
- ⚡ **指标** — 通过 `Sentry.metrics.*` 的自定义指标；当需要自定义 KPI 或业务指标时推荐

**建议逻辑：**

| 功能 | 当...推荐 |
|---------|------------------|
| 错误监控 | **始终** — 不可协商的基线 |
| 跟踪 | **始终用于 Next.js** — 服务器路由跟踪 + 客户端导航具有高价值 |
| 会话回放 | 面向用户的 App、登录流程或结账页面 |
| 日志记录 | App 使用结构化日志或需要日志到跟踪关联 |
| 性能分析 | 性能关键 App；客户端设置 `Document-Policy: js-profiling` |
| AI 监控 | App 调用 OpenAI、Vercel AI SDK 或 Anthropic |
| Crons | App 有 Vercel Cron 任务、计划 API 路由或 `node-cron` 使用 |
| 指标 | App 需要自定义计数器、仪表或通过 `Sentry.metrics.*` 的直方图 |

建议："我建议设置 Error Monitoring + Tracing + Session Replay。您想要我添加 Logging 或 Profiling 吗？"

---

## 第三阶段：指导

### 选项 1：向导（推荐）

> **您需要自己运行** — 向导会打开浏览器进行登录，并需要交互式输入，代理无法处理。将以下内容复制粘贴到您的终端：
>
> ```
> npx @sentry/wizard@latest -i nextjs
> ```
>
> 它会处理登录、组织/项目选择、SDK 安装、配置文件（`instrumentation-client.ts`、`sentry.server.config.ts`、`sentry.edge.config.ts`、`instrumentation.ts`）、`next.config.ts` 包装、源映射上传，并添加一个 `/sentry-example-page`。
>
> **完成它后，回来并跳转到 [验证](#verification)。**

如果用户跳过向导，请继续执行下面的选项 2（手动设置）。

---

### 选项 2：手动设置

#### 安装

```bash
npm install @sentry/nextjs --save
```

#### 创建 `instrumentation-client.ts` — 浏览器 / 客户端运行时

> 旧版文档使用 `sentry.client.config.ts` — 当前模式是 `instrumentation-client.ts`。

```typescript
import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN ?? "___PUBLIC_DSN___",

  dataCollection: {
    // 要禁用发送用户数据和 HTTP 正文，请取消注释以下行。更多信息请访问：
    // https://docs.sentry.io/platforms/javascript/guides/nextjs/configuration/options/#dataCollection
    // userInfo: false,
    // httpBodies: [],
  },

  // 开发环境 100%，生产环境 10%
  tracesSampleRate: process.env.NODE_ENV === "development" ? 1.0 : 0.1,

  // 会话回放：所有会话的 10%，有错误的会话的 100%
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,

  enableLogs: true,

  integrations: [
    Sentry.replayIntegration(),
    // 可选：用户反馈组件
    // Sentry.feedbackIntegration({ colorScheme: "system" }),
  ],
});

// 钩入 App Router 导航转换（仅 App Router）
export const onRouterTransitionStart = Sentry.captureRouterTransitionStart;
```

#### 创建 `sentry.server.config.ts` — Node.js 服务器运行时

```typescript
import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: process.env.SENTRY_DSN ?? "___DSN___",

  dataCollection: {
    // 要禁用发送用户数据和 HTTP 正文，请取消注释以下行。更多信息请访问：
    // https://docs.sentry.io/platforms/javascript/guides/nextjs/configuration/options/#dataCollection
    // userInfo: false,
    // httpBodies: [],
  },
  tracesSampleRate: process.env.NODE_ENV === "development" ? 1.0 : 0.1,

  // 将局部变量值附加到堆栈帧
  includeLocalVariables: true,

  enableLogs: true,
});
```

#### 创建 `sentry.edge.config.ts` — Edge 运行时

```typescript
import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: process.env.SENTRY_DSN ?? "___DSN___",

  dataCollection: {
    // 要禁用发送用户数据和 HTTP 正文，请取消注释以下行。更多信息请访问：
    // https://docs.sentry.io/platforms/javascript/guides/nextjs/configuration/options/#dataCollection
    // userInfo: false,
    // httpBodies: [],
  },
  tracesSampleRate: process.env.NODE_ENV === "development" ? 1.0 : 0.1,

  enableLogs: true,
});
```

#### 创建 `instrumentation.ts` — 服务器端注册钩子

> 需要 `experimental.instrumentationHook: true` 在 `next.config` 中（Next.js < 14.0.4）。它在 14.0.4+ 中是稳定的。

```typescript
import * as Sentry from "@sentry/nextjs";

export async function register() {
  if (process.env.NEXT_RUNTIME === "nodejs") {
    await import("./sentry.server.config");
  }

  if (process.env.NEXT_RUNTIME === "edge") {
    await import("./sentry.edge.config");
  }
}

// 自动捕获所有未处理的服务器端请求错误
// 需要 @sentry/nextjs >= 8.28.0
export const onRequestError = Sentry.captureRequestError;
```

**运行时分发：**

| `NEXT_RUNTIME` | 加载配置文件 |
|---|---|
| `"nodejs"` | `sentry.server.config.ts` |
| `"edge"` | `sentry.edge.config.ts` |
| *(客户端捆绑包)* | `instrumentation-client.ts` (Next.js 直接处理) |

#### App Router：创建 `app/global-error.tsx`

这会捕获根布局中的错误和 React 渲染错误：

```tsx
"use client";

import * as Sentry from "@sentry/nextjs";
import NextError from "next/error";
import { useEffect } from "react";

export default function GlobalError({
  error,
}: {
  error: Error & { digest?: string };
}) {
  useEffect(() => {
    Sentry.captureException(error);
  }, [error]);

  return (
    <html>
      <body>
        <NextError statusCode={0} />
      </body>
    </html>
  );
}
```

#### Pages Router：更新 `pages/_error.tsx`

```tsx
import * as Sentry from "@sentry/nextjs";
import type { NextPageContext } from "next";
import NextErrorComponent from "next/error";

type ErrorProps = { statusCode: number };

export default function CustomError({ statusCode }: ErrorProps) {
  return <NextErrorComponent statusCode={statusCode} />;
}

CustomError.getInitialProps = async (ctx: NextPageContext) => {
  await Sentry.captureUnderscoreErrorException(ctx);
  return NextErrorComponent.getInitialProps(ctx);
};
```

#### 使用 `withSentryConfig()` 包装 `next.config.ts`

```typescript
import type { NextConfig } from "next";
import { withSentryConfig } from "@sentry/nextjs";

const nextConfig: NextConfig = {
  // 你现有的 Next.js 配置
};

export default withSentryConfig(nextConfig, {
  org: "___ORG_SLUG___",
  project: "___PROJECT_SLUG___",

  // 源映射上传认证令牌（见下文源映射部分）
  authToken: process.env.SENTRY_AUTH_TOKEN,

  // 上传更广泛的客户端源文件以获得更好的堆栈跟踪解析
  widenClientFileUpload: true,

  // 创建一个代理 API 路由以绕过广告拦截器
  tunnelRoute: "/monitoring",

  // 抑制非 CI 输出
  silent: !process.env.CI,
});
```

#### 从中间件中排除隧道路由

如果你有 `middleware.ts`，请从认证或重定向逻辑中排除隧道路径：

```typescript
// middleware.ts
export const config = {
  matcher: [
    // 排除监控路由、Next.js 内部文件和静态文件
    "/((?!monitoring|_next/static|_next/image|favicon.ico).*)",
  ],
};
```

---

### 源映射设置

`withSentryConfig` 在生产构建中上传源映射，以便堆栈跟踪显示您的原始代码而不是压缩输出。SDK 特定的连接是在 `next.config.ts` 中的 `authToken`（以及 `widenClientFileUpload`，它提高了客户端堆栈跟踪）：

```typescript
withSentryConfig(nextConfig, {
  org: "my-org",
  project: "my-project",
  authToken: process.env.SENTRY_AUTH_TOKEN, // 从 CI 环境或 git 忽略的 .env.sentry-build-plugin 获取
  widenClientFileUpload: true,
});
```

`SENTRY_AUTH_TOKEN` 是构建时密钥，与 DSN 不同。有关创建令牌、将其连接到 CI 以及解决压缩跟踪的更多信息，请参阅 [`sentry-source-maps`](../sentry-source-maps/SKILL.md)。

源映射会在每次 `next build` 时自动上传。

---

### 对于每个同意的功能

加载相应的参考文件并按照其步骤操作：

| 功能 | 参考文件 | 加载时... |
|---------|---------------|-------------|
| 错误监控 | `references/error-monitoring.md` | 始终（基线）— App Router 错误边界，Pages Router `_error.tsx`，服务器操作包装 |
| 跟踪 | `references/tracing.md` | 服务器端请求跟踪，客户端导航，分布式跟踪，`tracePropagationTargets` |
| 会话回放 | `references/session-replay.md` | 面向用户的 App；隐私掩码，画布记录，网络捕获 |
| 日志记录 | `references/logging.md` | 结构化日志，`Sentry.logger.*`，日志到跟踪关联 |
| 性能分析 | `references/profiling.md` | 持续性能分析，`Document-Policy` 标头，`nodeProfilingIntegration` |
| AI 监控 | `references/ai-monitoring.md` | App 使用 OpenAI、Vercel AI SDK 或 Anthropic |
| Crons | `references/crons.md` | Vercel Cron，计划 API 路由，`node-cron` |
| 指标 | `references/metrics.md` | 自定义计数器，仪表，通过 `Sentry.metrics.*` 的分布 |

对于每个功能：阅读参考文件，精确跟随其步骤，并在继续之前进行验证。

---

## 配置参考

### `Sentry.init()` 选项

| 选项 | 类型 | 默认 | 备注 |
|--------|------|---------|-------|
| `dsn` | `string` | — | 需要。客户端使用 `NEXT_PUBLIC_SENTRY_DSN`，服务器/Edge 使用 `SENTRY_DSN` |
| `tracesSampleRate` | `number` | — | 0–1；开发环境 1.0，生产环境 0.1 推荐值 |
| `replaysSessionSampleRate` | `number` | `0.1` | 记录所有会话的分数 |
| `replaysOnErrorSampleRate` | `number` | `1.0` | 记录有错误会话的分数 |
| `dataCollection` | `object` | 保守，除非设置 | 对自动收集类别（`userInfo`、`cookies`、`httpHeaders`、`httpBodies`、`queryParams`、`genAI`）进行细粒度控制。省略时，SDK 会回退到 `sendDefaultPii`（默认 `false`）。传递对象——即使 `{}`——会将未设置的类别切换到它们的宽松默认值；按类别选择退出。 |
| `includeLocalVariables` | `boolean` | `false` | 将局部变量值附加到堆栈帧（仅服务器） |
| `enableLogs` | `boolean` | `false` | 启用 Sentry Logs 产品 |
| `environment` | `string` | 自动 | `"production"`、`"staging"` 等 |
| `release` | `string` | 自动 | 设置为提交 SHA 或版本标签 |
| `debug` | `boolean` | `false` | 将 SDK 活动记录到控制台 |

### `withSentryConfig()` 选项

| 选项 | 类型 | 备注 |
|--------|------|-------|
| `org` | `string` | Sentry 组织代码 |
| `project` | `string` | Sentry 项目代码 |
| `authToken` | `string` | 源映射上传令牌（`SENTRY_AUTH_TOKEN`） |
| `widenClientFileUpload` | `boolean` | 上传更多客户端文件以获得更好的堆栈跟踪 |
| `tunnelRoute` | `string` | 用于绕过广告拦截器的 API 路由路径（例如 `"/monitoring"`） |
| `silent` | `boolean` | 抑制构建输出（推荐 `!process.env.CI`） |
| `webpack.treeshake.*` | `object` | 树形拆解 SDK 功能（仅 webpack，不支持 Turbopack） |

### 环境变量

| 变量 | 运行时 | 目的 |
|----------|---------|---------|
| `NEXT_PUBLIC_SENTRY_DSN` | 客户端 | 浏览器 Sentry 初始化的 DSN（公开） |
| `SENTRY_DSN` | 服务器 / Edge | 服务器/Edge Sentry 初始化的 DSN |
| `SENTRY_AUTH_TOKEN` | 构建 | 源映射上传认证令牌（密钥） |
| `SENTRY_ORG` | 构建 | 组织代码（配置中的 `org` 替代） |
| `SENTRY_PROJECT` | 构建 | 项目代码（配置中的 `project` 替代） |
| `SENTRY_RELEASE` | 服务器 | 发布版本字符串（从 git 自动检测） |
| `NEXT_RUNTIME` | 服务器 / Edge | `"nodejs"` 或 `"edge"`（由 Next.js 内部设置） |

---

## 验证

完成向导或手动设置后，验证 Sentry 是否正常工作：

```typescript
// 暂时添加到服务器操作或 API 路由，然后删除
import * as Sentry from "@sentry/nextjs";

throw new Error("Sentry 测试错误 — 删除我");
// 或
Sentry.captureException(new Error("Sentry 测试错误 — 删除我"));
```

然后检查您的 [Sentry 问题面板](https://sentry.io/issues/) — 错误应在约 30 秒内出现。

**验证清单：**

| 检查 | 如何 |
|-------|-----|
| 客户端错误捕获 | 在客户端组件中抛出，验证在 Sentry 中 |
| 服务器错误捕获 | 在服务器操作或 API 路由中抛出 |
| Edge 错误捕获 | 在中间件或 Edge 路由处理程序中抛出 |
| 源映射正常工作 | 检查堆栈跟踪显示可读的文件名 |
| 会话回放正常工作 | 检查 Sentry 控制面板中的回放选项卡 |

---

## 第四阶段：跨链接

完成 Next.js 设置后，检查配套服务：

```bash
# 检查相邻目录中的后端服务
ls ../backend ../server ../api ../services 2>/dev/null

# 检查后端语言指示器
cat ../go.mod 2>/dev/null | head -3
cat ../requirements.txt ../pyproject.toml 2>/dev/null | head -3
cat ../Gemfile 2>/dev/null | head -3
cat ../pom.xml ../build.gradle 2>/dev/null | head -3
```

如果发现后端，请建议匹配的 SDK 技能：

| 后端检测 | 建议技能 |
|-----------------|--------------|
| Go (`go.mod`) | `sentry-go-sdk` |
| Python (`requirements.txt`，`pyproject.toml`) | `sentry-python-sdk` |
| Ruby (`Gemfile`) | `sentry-ruby-sdk` |
| Java/Kotlin (`pom.xml`，`build.gradle`) | 查看 [docs.sentry.io/platforms/java/](https://docs.sentry.io/platforms/java/) |
| Node.js (Express，Fastify，Hapi) | `@sentry/node` — 查看 [docs.sentry.io/platforms/javascript/guides/express/](https://docs.sentry.io/platforms/javascript/guides/express/) |

使用相同 DSN 或链接项目连接前端和后端可以启用**分布式跟踪**——跨越浏览器、Next.js 服务器和后端 API 的单次跟踪视图。

---

## 故障排除

| 问题 | 原因 | 解决方案 |
|-------|-------|----------|
| 事件未出现 | DSN 配置错误或 `debug: false` 隐藏错误 | 暂时设置 `debug: true`；检查浏览器网络选项卡中的对 `sentry.io` 的请求 |
| 堆栈跟踪显示压缩代码 | 源映射未上传 | 检查 `SENTRY_AUTH_TOKEN` 是否设置；运行 `next build` 并在构建输出中查找 "Source Maps" |
| `onRequestError` 未触发 | SDK 版本 < 8.28.0 | 升级：`npm install @sentry/nextjs@latest` |
| Edge 运行时错误缺失 | 未加载 `sentry.edge.config.ts` | 验证 `instrumentation.ts` 在 `NEXT_RUNTIME === "edge"` 时导入它 |
| 隧道路由返回 404 | 设置了 `tunnelRoute` 但 Next.js 路由缺失 | 插件会自动创建它；检查您在添加 `tunnelRoute` 后是否运行了 `next build` |
| `withSentryConfig` 树形拆解破坏构建 | 使用 Turbopack | 树形拆解选项仅适用于 webpack；使用 Turbopack 时移除 `webpack.treeshake` 选项 |
| `global-error.tsx` 未捕获错误 | 缺少 `"use client"` 指令 | 在 `global-error.tsx` 的第一行添加 `"use client"` |
| 会话回放未记录 | 客户端初始化中缺少 `replayIntegration()` | 在 `instrumentation-client.ts` 中的 `integrations` 中添加 `Sentry.replayIntegration()` |
