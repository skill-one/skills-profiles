---
name: sentry-nestjs-sdk
description: NestJS 完整的 Sentry SDK 配置。当被要求“将 Sentry 添加到 NestJS”、“安装 @sentry/nestjs”、“在 NestJS 中配置 Sentry”，或为 NestJS 应用配置错误监控、追踪、性能分析、日志记录、指标、定时任务或 AI 监控时使用。支持 Express 和 Fastify 适配器、GraphQL、微服务、WebSocket 和后台任务。
---

> [所有技能](../../SKILL_TREE.md) > [SDK 安装](../sentry-sdk-setup/SKILL.md) > NestJS SDK

# Sentry NestJS SDK

一个有主见的向导，扫描您的 NestJS 项目并指导您完成完整的 Sentry 设置。

## 何时调用此技能

- 用户询问在 NestJS 应用中“添加 Sentry 到 NestJS”或“设置 Sentry”
- 用户希望在 NestJS 中实现错误监控、追踪、分析、日志记录、指标或定时任务
- 用户提到 `@sentry/nestjs` 或 Sentry + NestJS
- 用户希望监控 NestJS 控制器、服务、守卫、微服务或后台任务

> **注意：** 以下 SDK 版本和 API 反映的是 `@sentry/nestjs` 10.x 版本（支持 NestJS 8–11）。
> 在实施之前，请务必参考 [docs.sentry.io/platforms/node/guides/nestjs/](https://docs.sentry.io/platforms/node/guides/nestjs/) 进行验证。

---

## 第一阶段：检测

运行这些命令以在提供建议之前了解项目：

```bash
# 确认 NestJS 项目
grep -E '"@nestjs/core"' package.json 2>/dev/null

# 检查 NestJS 版本
node -e "console.log(require('./node_modules/@nestjs/core/package.json').version)" 2>/dev/null

# 检查现有 Sentry
grep -i sentry package.json 2>/dev/null
ls src/instrument.ts 2>/dev/null
grep -r "Sentry.init\|@sentry" src/main.ts src/instrument.ts 2>/dev/null

# 检查现有的 Sentry DI 包装器（在企业级 NestJS 中常见）
grep -rE "SENTRY.*TOKEN|SentryProxy|SentryService" src/ libs/ 2>/dev/null

# 检查基于配置类的初始化（与基于环境变量的初始化对比）
grep -rE "class SentryConfig|SentryConfig" src/ libs/ 2>/dev/null

# 检查 SentryModule.forRoot() 是否已在共享模块中注册
grep -rE "SentryModule\.forRoot|SentryProxyModule" src/ libs/ 2>/dev/null

# 检测 HTTP 适配器（默认为 Express）
grep -E "FastifyAdapter|@nestjs/platform-fastify" package.json src/main.ts 2>/dev/null

# 检测 GraphQL
grep -E '"@nestjs/graphql"|"apollo-server"' package.json 2>/dev/null

# 检测微服务
grep '"@nestjs/microservices"' package.json 2>/dev/null

# 检测 WebSockets
grep -E '"@nestjs/websockets"|"socket.io"' package.json 2>/dev/null

# 检测任务队列/定时任务
grep -E '"@nestjs/bull"|"@nestjs/bullmq"|"@nestjs/schedule"|"bullmq"|"bull"' package.json 2>/dev/null

# 检测数据库
grep -E '"@prisma/client"|"typeorm"|"mongoose"|"pg"|"mysql2"' package.json 2>/dev/null

# 检测 AI 库
grep -E '"openai"|"@anthropic-ai"|"langchain"|"@langchain"|"@google/generative-ai"|"ai"' package.json 2>/dev/null

# 检查配套前端
ls -d ../frontend ../web ../client ../ui 2>/dev/null
```

**需要注意的事项：**

- `@sentry/nestjs` 是否已安装？如果是，请检查是否存在 `instrument.ts` 并调用 `Sentry.init()` — 可能只需要配置功能。
- **检测到 Sentry DI 包装器？** → 项目在依赖注入令牌（例如 `SENTRY_PROXY_TOKEN`）后面包装了 Sentry 以便测试。使用注入的代理进行所有运行时 Sentry 调用（`startSpan`、`captureException`、`withIsolationScope`），而不是在控制器、服务和处理程序中直接导入 `@sentry/nestjs`。只有 `instrument.ts` 应直接导入 `@sentry/nestjs`。
- **检测到配置类？** → 项目使用一个类型化的配置类来配置 `Sentry.init()` 选项（例如从 YAML 或 `@nestjs/config` 加载）。任何新的 SDK 选项都必须添加到配置类型中 — 不要硬编码应在每个环境中配置的值。
- **`SentryModule.forRoot()` 是否已注册？** → 如果它在共享模块中（例如一个 Sentry 代理模块），请不要在 `AppModule` 中再次添加它 — 这会导致重复拦截器注册。
- Express（默认）或 Fastify 适配器？Express 完全支持；Fastify 可以工作但有已知的边缘情况。
- 检测到 GraphQL？→ `SentryGlobalFilter` 原生处理。
- 检测到微服务？→ 建议使用 RPC 异常过滤器。
- 任务队列/`@nestjs/schedule`？→ 建议使用定时任务。
- AI 库？→ 自动注入，无需配置。
- Prisma？→ 需要手动调用 `prismaIntegration()`。
- 配套前端？→ 触发第四阶段跨链接。

---

## 第二阶段：建议

根据您的发现，提出具体的建议。不要提出开放式问题 — 直接给出建议：

**始终推荐（核心覆盖）：**

- ✅ **错误监控** — 捕获 HTTP、GraphQL、RPC 和 WebSocket 上下文中的未处理异常
- ✅ **追踪** — 自动注入中间件、守卫、管道、拦截器、过滤器和路由处理器

**检测到时推荐：**

- ✅ **分析** — CPU 性能重要的生产应用（`@sentry/profiling-node`）
- ✅ **日志记录** — 结构化的 Sentry 日志 + 可选的控制台捕获
- ✅ **定时任务** — 检测到 `@nestjs/schedule`、Bull 或 BullMQ
- ✅ **指标** — 业务 KPI 或 SLO 跟踪
- ✅ **AI 监控** — 检测到 OpenAI/Anthropic/LangChain 等（自动注入，无需配置）

**建议矩阵：**

| 功能          | 检测到时...                                  | 参考                                      |
| ------------- | ------------------------------------------ | ---------------------------------------- |
| 错误监控      | **始终** — 不可协商的基线                   | `${SKILL_ROOT}/references/error-monitoring.md` |
| 追踪          | **始终** — NestJS 生命周期自动注入          | `${SKILL_ROOT}/references/tracing.md`          |
| 分析          | 生产 + CPU 敏感工作负载                     | `${SKILL_ROOT}/references/profiling.md`        |
| 日志记录      | 始终；增强的结构化日志聚合                | `${SKILL_ROOT}/references/logging.md`          |
| 指标          | 自定义业务 KPI 或 SLO 跟踪               | `${SKILL_ROOT}/references/metrics.md`          |
| 定时任务      | 检测到 `@nestjs/schedule`、Bull 或 BullMQ | `${SKILL_ROOT}/references/crons.md`            |
| AI 监控      | 检测到 OpenAI/Anthropic/LangChain 等       | `${SKILL_ROOT}/references/ai-monitoring.md`    |

建议：_"我建议 Error Monitoring + Tracing + Logging。还需要 Profiling、Crons 或 AI Monitoring 吗？"_

---

## 第三阶段：指导

### 安装

```bash
# 核心 SDK（始终需要 — 包括 @sentry/node）
npm install @sentry/nestjs

# 带有分析支持（可选）
npm install @sentry/nestjs @sentry/profiling-node
```

> ⚠️ **不要将 `@sentry/node` 与 `@sentry/nestjs` 一起安装** — `@sentry/nestjs` 重新导出 `@sentry/node` 中的所有内容。安装两者会导致重复注册。

### 三文件设置（必需）

NestJS 需要特定的三文件初始化模式，因为 Sentry SDK 必须在 NestJS 加载它们之前通过 OpenTelemetry 修补 Node.js 模块。

> **在创建新文件之前**，检查第一阶段的结果：
>
> - 如果 `instrument.ts` 已存在 → 修改它，不要创建新的。
> - 如果配置类驱动 `Sentry.init()` → 从配置中读取选项，而不是硬编码环境变量。
> - 如果存在 Sentry DI 包装器 → 使用它进行运行时调用，而不是在服务/控制器中直接导入 `@sentry/nestjs`。

#### 第一步：创建 `src/instrument.ts`

```typescript
import * as Sentry from "@sentry/nestjs";
// 可选：添加分析
// import { nodeProfilingIntegration } from "@sentry/profiling-node";

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.SENTRY_ENVIRONMENT ?? "production",
  release: process.env.SENTRY_RELEASE,

  // 数据收集（SDK ≥ 10.57.0 — 替代已弃用的 sendDefaultPii）
  dataCollection: {
    // 要禁用发送用户数据和 HTTP 正文，请取消注释以下行。更多信息请访问：
    // https://docs.sentry.io/platforms/javascript/guides/nestjs/configuration/options/#dataCollection
    // userInfo: false,
    // httpBodies: [],
  },

  // 追踪 — 在高流量生产环境中将 `tracesSampleRate` 降低到 0.1–0.2
  tracesSampleRate: 1.0,

  // 分析（需要 @sentry/profiling-node）
  // integrations: [nodeProfilingIntegration()],
  // profileSessionSampleRate: 1.0,
  // profileLifecycle: "trace",

  // 结构化日志（SDK ≥ 9.41.0）
  enableLogs: true,
});
```

**配置驱动的 `Sentry.init()`：** 如果第一阶段发现一个类型化的配置类（例如 `SentryConfig`），请从它读取选项，而不是使用原始 `process.env`。这在使用 `@nestjs/config` 或自定义配置加载器的 NestJS 应用中很常见：

```typescript
import * as Sentry from "@sentry/nestjs";
import { loadConfiguration } from "./config";

const config = loadConfiguration();

Sentry.init({
  dsn: config.sentry.dsn,
  environment: config.sentry.environment ?? "production",
  release: config.sentry.release,
  dataCollection: config.sentry.dataCollection ?? {
    // 要禁用发送用户数据和 HTTP 正文，请取消注释以下行。更多信息请访问：
    // https://docs.sentry.io/platforms/javascript/guides/nestjs/configuration/options/#dataCollection
    // userInfo: false,
    // httpBodies: [],
  },
  tracesSampleRate: config.sentry.tracesSampleRate ?? 1.0,
  profileSessionSampleRate: config.sentry.profilesSampleRate ?? 1.0,
  profileLifecycle: "trace",
  enableLogs: true,
});
```

当添加新的 SDK 选项（例如 `dataCollection`、`profileSessionSampleRate`）时，请将它们添加到配置类型中，以便可以按环境配置。

#### 第二步：在 `src/main.ts` 中**首先**导入 `instrument.ts`

```typescript
// instrument.ts 必须是第一个导入 — 在 NestJS 或任何其他模块之前
import "./instrument";

import { NestFactory } from "@nestjs/core";
import { AppModule } from "./app.module";

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  // 启用优雅关闭 — 在 SIGTERM/SIGINT 上刷新 Sentry 事件
  app.enableShutdownHooks();

  await app.listen(3000);
}
bootstrap();
```

> **为什么第一个？** OpenTelemetry 必须在加载之前修补 `http`、`express`、数据库驱动程序和其他模块。任何在 `instrument.ts` 之前加载的模块都不会被自动注入。

#### 第三步：在 `src/app.module.ts` 中注册 `SentryModule` 和 `SentryGlobalFilter`

```typescript
import { Module } from "@nestjs/common";
import { APP_FILTER } from "@nestjs/core";
import { SentryModule, SentryGlobalFilter } from "@sentry/nestjs/setup";
import { AppController } from "./app.controller";
import { AppService } from "./app.service";

@Module({
  imports: [
    SentryModule.forRoot(), // 全局注册 SentryTracingInterceptor
  ],
  controllers: [AppController],
  providers: [
    AppService,
    {
      provide: APP_FILTER,
      useClass: SentryGlobalFilter, // 捕获所有未处理的异常
    },
  ],
})
export class AppModule {}
```

**每个部分的作用：**

- `SentryModule.forRoot()` — 将 `SentryTracingInterceptor` 注册为全局 `APP_INTERCEPTOR`，启用 HTTP 事务命名
- `SentryGlobalFilter` — 扩展 `BaseExceptionFilter`；跨 HTTP、GraphQL（重新抛出 `HttpException` 而不报告）和 RPC 上下文捕获异常

> ⚠️ **不要重复注册 `SentryModule.forRoot()`。** 如果第一阶段发现它在共享库模块中已导入（例如 `SentryProxyModule` 或 `AnalyticsModule`），请不要在 `AppModule` 中再次添加它。重复注册会导致每个跨度被拦截两次，使跟踪数据膨胀。

> ⚠️ **两个入口点，不同的导入：**
>
> - `@sentry/nestjs` → SDK 初始化、捕获 API、装饰器（`SentryTraced`、`SentryCron`、`SentryExceptionCaptured`）
> - `@sentry/nestjs/setup` → NestJS DI 构造（`SentryModule`、`SentryGlobalFilter`）
>
> 永远不要从 `@sentry/nestjs`（主入口点）导入 `SentryModule` — 它在 OpenTelemetry 修补它之前加载 `@nestjs/common`，破坏自动注入。

### ESM 设置（Node ≥ 18.19.0）

对于 ESM 应用程序，请使用 `--import` 而不是文件导入：

```javascript
// instrument.mjs
import * as Sentry from "@sentry/nestjs";

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  tracesSampleRate: 1.0,
});
```

```json
// package.json
{
  "scripts": {
    "start": "node --import ./instrument.mjs -r ts-node/register src/main.ts"
  }
}
```

或通过环境：

```bash
NODE_OPTIONS="--import ./instrument.mjs" npm run start
```

### 异常过滤器选项

选择适合您现有架构的方法：

#### 选项 A：没有现有的全局过滤器 — 使用 `SentryGlobalFilter`（推荐）

已在上述步骤 3 中涵盖。这是最简单的选项。

#### 选项 B：现有的自定义全局过滤器 — 添加 `@SentryExceptionCaptured()` 装饰器

```typescript
import { Catch, ExceptionFilter, ArgumentsHost } from "@nestjs/common";
import { SentryExceptionCaptured } from "@sentry/nestjs";

@Catch()
export class YourExistingFilter implements ExceptionFilter {
  @SentryExceptionCaptured() // 包装 catch() 以自动报告异常
  catch(exception: unknown, host: ArgumentsHost): void {
    // 您现有的错误处理保持不变
  }
}
```

#### 选项 C：特定异常类型 — 手动捕获

```typescript
import { ArgumentsHost, Catch } from "@nestjs/common";
import { BaseExceptionFilter } from "@nestjs/core";
import * as Sentry from "@sentry/nestjs";

@Catch(ExampleException)
export class ExampleExceptionFilter extends BaseExceptionFilter {
  catch(exception: ExampleException, host: ArgumentsHost) {
    Sentry.captureException(exception);
    super.catch(exception, host);
  }
}
```

#### 选项 D：微服务 RPC 异常

```typescript
import { Catch, RpcExceptionFilter, ArgumentsHost } from "@nestjs/common";
import { Observable, throwError } from "rxjs";
import { RpcException } from "@nestjs/microservices";
import * as Sentry from "@sentry/nestjs";

@Catch(RpcException)
export class SentryRpcFilter implements RpcExceptionFilter<RpcException> {
  catch(exception: RpcException, host: ArgumentsHost): Observable<any> {
    Sentry.captureException(exception);
    return throwError(() => exception.getError());
  }
}
```

### 装饰器

#### `@SentryTraced(op?)` — 任何方法都可以注入

```typescript
import { Injectable } from "@nestjs/common";
import { SentryTraced } from "@sentry/nestjs";

@Injectable()
export class OrderService {
  @SentryTraced("order.process")
  async processOrder(orderId: string): Promise<void> {
    // 自动包装在 Sentry 跨度中
  }

  @SentryTraced()  // 默认为 op: "function"
  async fetchInventory() { ... }
}
```

#### `@SentryCron(slug, config?)` — 监控定时任务

```typescript
import { Injectable } from "@nestjs/common";
import { Cron } from "@nestjs/schedule";
import { SentryCron } from "@sentry/nestjs";

@Injectable()
export class ReportService {
  @Cron("0 * * * *")
  @SentryCron("hourly-report", {
    // @SentryCron 必须在 @Cron 之后
    schedule: { type: "crontab", value: "0 * * * *" },
    checkinMargin: 2, // 分钟前标记错过
    maxRuntime: 10, // 最大运行时间（分钟）
    timezone: "UTC",
  })
  async generateReport() {
    // 自动发送签到在启动/成功/失败时
  }
}
```

#### 后台任务范围隔离

后台任务共享默认隔离范围 — 使用 `Sentry.withIsolationScope()` 包装以防止交叉污染：

```typescript
import * as Sentry from "@sentry/nestjs";
import { Injectable } from "@nestjs/common";
import { Cron, CronExpression } from "@nestjs/schedule";

@Injectable()
export class JobService {
  @Cron(CronExpression.EVERY_HOUR)
  handleCron() {
    Sentry.withIsolationScope(() => {
      Sentry.setTag("job", "hourly-sync");
      this.doWork();
    });
  }
}
```

将 `withIsolationScope` 应用于：`@Cron()`、`@Interval()`、`@OnEvent()`、`@Processor()`，以及请求生命周期之外的任何代码。

### 与 Sentry DI 包装器一起工作

一些 NestJS 项目在依赖注入令牌（例如 `SENTRY_PROXY_TOKEN`）后面包装 Sentry 以便测试和解耦。如果第一阶段检测到此模式，**请使用注入的服务进行所有运行时 Sentry 调用** — 不要在控制器、服务或处理程序中直接导入 `@sentry/nestjs`。

```typescript
import { Controller, Inject } from "@nestjs/common";
import { SENTRY_PROXY_TOKEN, type SentryProxyService } from "./sentry-proxy";

@Controller("orders")
export class OrderController {
  constructor(
    @Inject(SENTRY_PROXY_TOKEN) private readonly sentry: SentryProxyService,
    private readonly orderService: OrderService,
  ) {}

  @Post()
  async createOrder(@Body() dto: CreateOrderDto) {
    return this.sentry.startSpan(
      { name: "createOrder", op: "http" },
      async () => this.orderService.create(dto),
    );
  }
}
```

**直接使用 `@sentry/nestjs` 导入仍然正确：**

- `instrument.ts` — 始终使用 `import * as Sentry from "@sentry/nestjs"` 用于 `Sentry.init()`
- 独立脚本和异常过滤器（在依赖注入容器外运行）

### 验证

添加一个测试端点以确认事件已到达 Sentry：

```typescript
import { Controller, Get } from "@nestjs/common";
import * as Sentry from "@sentry/nestjs";

@Controller()
export class DebugController {
  @Get("/debug-sentry")
  triggerError() {
    throw new Error("我的第一个 Sentry 错误来自 NestJS！");
  }

  @Get("/debug-sentry-span")
  triggerSpan() {
    return Sentry.startSpan({ op: "test", name: "NestJS 测试跨度" }, () => {
      return { status: "跨度已创建" };
    });
  }
}
```

访问 `GET /debug-sentry` 并在几秒钟内检查 Sentry 问题面板。

### 每个约定的功能

逐个功能进行操作。加载参考文件，按照其步骤操作，验证后再继续：

| 功能          | 参考文件                                 | 加载时...                           |
| ------------- | ---------------------------------------- | ---------------------------------- |
| 错误监控      | `${SKILL_ROOT}/references/error-monitoring.md` | 始终（基准线）                      |
| 跟踪          | `${SKILL_ROOT}/references/tracing.md`          | 始终（NestJS 路由自动跟踪）          |
| 分析          | `${SKILL_ROOT}/references/profiling.md`        | CPU 密集型生产应用                  |
| 日志记录      | `${SKILL_ROOT}/references/logging.md`          | 需要结构化日志聚合                  |
| 指标          | `${SKILL_ROOT}/references/metrics.md`          | 自定义 KPIs / SLO 追踪             |
| 定时任务      | `${SKILL_ROOT}/references/crons.md`            | 定时任务或任务队列                  |
| AI 监控      | `${SKILL_ROOT}/references/ai-monitoring.md`    | 检测到 OpenAI/Anthropic/LangChain    |

对于每个功能：`读取 ${SKILL_ROOT}/references/<功能>.md`，精确遵循步骤，验证其是否正常工作。

---

## 配置参考

### `Sentry.init()` 的关键选项

| 选项                       | 类型                    | 默认值        | 目的                                                                                              |
| -------------------------- | ----------------------- | ------------- | ------------------------------------------------------------------------------------------------ |
| `dsn`                      | `string`                | —              | 如果为空，则禁用 SDK；环境变量：`SENTRY_DSN`                                                         |
| `environment`              | `string`                | `"production"` | 例如：`"staging"`；环境变量：`SENTRY_ENVIRONMENT`                                                     |
| `release`                  | `string`                | —              | 例如：`"myapp@1.0.0"`；环境变量：`SENTRY_RELEASE`                                                     |
| `dataCollection`           | `object`                | 见下文      | 控制 SDK 收集的数据（SDK ≥ 10.57.0）                                                              |
| `dataCollection.userInfo`    | `boolean`               | `true`        | 包括 IP 地址和用户上下文                                                            |
| `dataCollection.httpHeaders` | `object`                | 见下文      | 捕获请求/响应的 HTTP 头部                                                          |
| `dataCollection.cookies`     | `boolean\|object`       | `true`         | 捕获 cookies；使用 `{allow: [...]}` 或 `{deny: [...]}` 进行过滤                           |
| `dataCollection.queryParams` | `boolean\|object`       | `true`         | 捕获 URL 查询参数；使用 `{allow: [...]}` 或 `{deny: [...]}` 进行过滤              |
| `dataCollection.genAI`       | `object`                | 见下文      | 控制 AI 输入/输出的记录                                                                |
| `sendDefaultPii`             | `boolean`               | `false`        | **已弃用** — 使用 `dataCollection.userInfo` 代替                                           |
| `tracesSampleRate`           | `number`                | —              | 事务采样率；`undefined` 禁用跟踪                                                    |
| `tracesSampler`              | `function`              | —              | 自定义每笔交易的采样（覆盖采样率）                                                 |
| `tracePropagationTargets`    | `Array<string\|RegExp>` | —              | 要传播 `sentry-trace`/`baggage` 头部的 URL                                                |
| `profileSessionSampleRate`   | `number`                | —              | 持续分析会话率（SDK ≥ 10.27.0）                                                |
| `profileLifecycle`           | `"trace"\|"manual"`     | `"trace"`      | `"trace"` = 自动启动与跨度关联的分析器；`"manual"` = 调用 `startProfiler()`/`stopProfiler()` |
| `enableLogs`                 | `boolean`               | `false`        | 将结构化日志发送到 Sentry (SDK ≥ 9.41.0)                                                    |
| `ignoreErrors`               | `Array<string\|RegExp>` | `[]`           | 要抑制的错误消息模式                                                               |
| `ignoreTransactions`         | `Array<string\|RegExp>` | `[]`           | 要抑制的事务名称模式                                                                |
| `beforeSend`                 | `function`              | —              | 钩子，用于修改或丢弃错误事件                                                              |
| `beforeSendTransaction`      | `function`              | —              | 钩子，用于修改或丢弃事务事件                                                            |
| `beforeSendLog`              | `function`              | —              | 钩子，用于修改或丢弃日志事件                                                                |
| `debug`                      | `boolean`               | `false`        | SDK 详细调试输出                                                                         |
| `maxBreadcrumbs`             | `number`                | `100`          | 每个事件的最大面包屑数量                                                                        |

**`dataCollection` 默认值：**
- `httpHeaders: { request: true, response: true }`
- `httpBodies: ["incomingRequest", "outgoingRequest", "incomingResponse", "outgoingResponse"]`
- `userInfo: true`
- `genAI: { inputs: true, outputs: true }`

### 环境变量

| 变量             | 映射到         | 备注                                             |
| ---------------- | -------------- | ------------------------------------------------ |
| `SENTRY_DSN`         | `dsn`           | 如果未向 `init()` 传递 `dsn`，则使用此变量          |
| `SENTRY_RELEASE`     | `release`       | 也自动从 git SHA、Heroku、CircleCI 检测到        |
| `SENTRY_ENVIRONMENT` | `environment`   | 如果未设置，则回退到 `"production"`                      |
| `SENTRY_AUTH_TOKEN`  | CLI/source maps | 用于 `npx @sentry/wizard@latest -i sourcemaps`     |
| `SENTRY_ORG`         | CLI/source maps | 组织代码                                           |
| `SENTRY_PROJECT`     | CLI/source maps | 项目代码                                      |

### 自动启用的集成

当检测到其包时，这些集成会自动激活 — 无需 `integrations: [...]`：

| 自动启用                      | 备注                                                                |
| ----------------------------- | ------------------------------------------------------------------ |
| `httpIntegration`                 | 通过 `http`/`https`/`fetch` 发出的 HTTP 调用                       |
| `expressIntegration`              | Express 适配器（默认 NestJS）                                     |
| `nestIntegration`                 | NestJS 生命周期（中间件、守卫、管道、拦截器、处理器）                 |
| `onUncaughtExceptionIntegration`  | 未捕获的异常                                                  |
| `onUnhandledRejectionIntegration` | 未处理的 Promise 拒绝                                         |
| `openAIIntegration`               | OpenAI SDK (当安装时)                                          |
| `anthropicAIIntegration`          | Anthropic SDK (当安装时)                                       |
| `langchainIntegration`            | LangChain (当安装时)                                           |
| `graphqlIntegration`              | GraphQL (当存在 `graphql` 包时)                             |
| `postgresIntegration`             | `pg` 驱动                                                          |
| `mysqlIntegration`                | `mysql` / `mysql2`                                                   |
| `mongoIntegration`                | MongoDB / Mongoose                                                   |
| `redisIntegration`                | `ioredis` / `redis`                                                  |

### 需要手动设置的集成

| 集成                 | 添加时                        | 代码                                                                |
| --------------------- | ---------------------------- | ------------------------------------------------------------------- |
| `nodeProfilingIntegration`  | 需要分析时                  | `import { nodeProfilingIntegration } from "@sentry/profiling-node"` |
| `prismaIntegration`         | 使用 Prisma ORM 时            | `integrations: [Sentry.prismaIntegration()]`                        |
| `consoleLoggingIntegration` | 捕获控制台输出             | `integrations: [Sentry.consoleLoggingIntegration()]`                |
| `localVariablesIntegration` | 捕获错误中的局部变量值     | `integrations: [Sentry.localVariablesIntegration()]`                |

---

## 验证

测试 Sentry 是否接收事件：

```typescript
// 添加测试端点（生产前移除）
@Get("/debug-sentry")
getError() {
  throw new Error("我的第一个 Sentry 错误！");
}
```

或者在不崩溃的情况下发送测试消息：

```typescript
import * as Sentry from "@sentry/nestjs";
Sentry.captureMessage("NestJS Sentry SDK 测试");
```

如果没有任何内容显示：

1. 在 `Sentry.init()` 中设置 `debug: true` — 将 SDK 内部信息打印到 stdout
2. 验证运行进程中的 `SENTRY_DSN` 环境变量是否已设置
3. 确认 `import "./instrument"` 是 `main.ts` 中的**第一行**
4. 确认 `SentryModule.forRoot()` 已在 `AppModule` 中导入
5. 检查 DSN 格式：`https://<key>@o<org>.ingest.sentry.io/<project>`

---

## 第 4 步：跨链接

完成 NestJS 设置后，检查是否有缺失 Sentry 的前端：

```bash
ls -d ../frontend ../web ../client ../ui 2>/dev/null
cat ../frontend/package.json ../web/package.json 2>/dev/null \
  | grep -E '"react"|"svelte"|"vue"|"next"|"nuxt"'
```

如果存在没有 Sentry 的前端，建议匹配的技能：

| 前端检测到   | 建议技能                                                                                                                      |
| ------------ | ---------------------------------------------------------------------------------------------------------------------------------- |
| Next.js             | `sentry-nextjs-sdk`                                                                                                                |
| React               | `sentry-react-sdk`                                                                                                                 |
| Svelte / SvelteKit  | `sentry-svelte-sdk`                                                                                                                |
| Vue / Nuxt          | 使用 `@sentry/vue` — 参考 [docs.sentry.io/platforms/javascript/guides/vue/](https://docs.sentry.io/platforms/javascript/guides/vue/) |
| React Native / Expo | `sentry-react-native-sdk`                                                                                                          |

---

## 故障排除

| 问题                                               | 解决方案                                                                                                                                                          |
| -------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 事件未显示                                           | 设置 `debug: true`，验证 `SENTRY_DSN`，检查 `instrument.ts` 是否首先导入                                                                                              |
| DSN 格式错误                                        | 格式：`https://<key>@o<org>.ingest.sentry.io/<project>`                                                                                                              |
| 异常未被捕获                                         | 确保 `SentryGlobalFilter` 通过 `APP_FILTER` 在 `AppModule` 中注册                                                                                                   |
| 自动instrumentation无法工作                         | `instrument.ts` 必须是 `main.ts` 中的**第一个导入** — 在所有 NestJS 导入之前                                                                                              |
| 性能分析未启动                                       | 需要 `tracesSampleRate > 0` + `profileSessionSampleRate > 0` + 安装 `@sentry/profiling-node`                                                                                   |
| `enableLogs`无法工作                                 | 需要 SDK ≥ 9.41.0                                                                                                                                                    |
| 没有跟踪信息显示                                      | 验证 `tracesSampleRate` 是否已设置（不是 `undefined`）                                                                                                                  |
| 交易过多                                           | 降低 `tracesSampleRate` 或使用 `tracesSampler` 来丢弃健康检查                                                                                                         |
| Fastify + GraphQL问题                               | 已知的边缘情况 — 查看 [GitHub #13388](https://github.com/getsentry/sentry-javascript/issues/13388)；优先使用 Express 进行 GraphQL                                                                 |
| 后台作业事件混合                                     | 将作业体包裹在 `Sentry.withIsolationScope(() => { ... })` 中                                                                                                       |
| Prisma 跨度缺失                                      | 在 `Sentry.init()` 中添加 `integrations: [Sentry.prismaIntegration()]`                                                                                              |
| ESM 语法错误                                        | 设置 `registerEsmLoaderHooks: false`（禁用 ESM 钩子；也会禁用 ESM 模块的自动instrumentation）                                                                          |
| `SentryModule`破坏instrumentation                     | 必须从 `@sentry/nestjs/setup` 导入，绝不能从 `@sentry/nestjs` 导入                                                                                              |
| RPC异常未被捕获                                      | 添加专用的 `SentryRpcExceptionFilter`（查看异常过滤器部分的选项 D）                                                                                                   |
| WebSocket异常未被捕获                                | 在网关的 `handleConnection`/`handleDisconnect` 上使用 `@SentryExceptionCaptured()`                                                                                       |
| `@SentryCron`未触发                                 | 装饰器顺序很重要 — `@SentryCron` 必须在 `@Cron` 之后                                                                                                               |
| TypeScript 路径别名问题                             | 确保 `tsconfig.json` 的 `paths` 配置正确，以便 `instrument` 从 `main.ts` 的位置解析                                                                                   |
| `import * as Sentry` ESLint错误                      | 许多项目禁止命名空间导入。使用命名导入（`import { startSpan, captureException } from "@sentry/nestjs"`）或使用项目的 DI 代理替代                                                                 |
| `profilesSampleRate` vs `profileSessionSampleRate` | `profilesSampleRate` 在 SDK 10.x 中已弃用。使用 `profileSessionSampleRate` + `profileLifecycle: "trace"` 代替                                                                 |
| 每次请求重复的跨度                                  | 在多个模块中注册了 `SentryModule.forRoot()`。确保只调用一次 — 检查共享/库模块                                                                                          |
| `instrument.ts`中未识别的配置属性                   | 当使用带类型的配置类时，新的 SDK 选项必须添加到配置类型定义中，并在重新构建项目后 TypeScript 才能识别它们                                                                    |

### 版本要求

| 功能                          | 最小 SDK 版本 |
| ---------------------------- | ------------ |
| `@sentry/nestjs` 包          | 8.0.0        |
| `@SentryTraced` 装饰器      | 8.15.0       |
| `@SentryCron` 装饰器        | 8.16.0       |
| 事件发射器自动instrumentation | 8.39.0       |
| `SentryGlobalFilter`（统一） | 8.40.0       |
| `Sentry.logger` API (`enableLogs`) | 9.41.0       |
| `profileSessionSampleRate`    | 10.27.0      |
| Node.js 要求                  | ≥ 18         |
| Node.js for ESM `--import`    | ≥ 18.19.0    |
| NestJS 兼容性                | 8.x – 11.x   |
