> [所有技能](../../SKILL_TREE.md) > [SDK 设置](../sentry-sdk-setup/SKILL.md) > NestJS SDK

# Sentry NestJS SDK

一个有主见的向导，扫描您的 NestJS 项目并指导您完成完整的 Sentry 设置。

## 何时调用此技能

- 用户询问在 NestJS 应用中“添加 Sentry 到 NestJS”或“设置 Sentry”
- 用户希望在 NestJS 中实现错误监控、跟踪、分析、日志记录、指标或定时任务
- 用户提到 `@sentry/nestjs` 或 Sentry + NestJS
- 用户希望监控 NestJS 控制器、服务、守卫、微服务或后台作业

> **注意：** 以下 SDK 版本和 API 反映 `@sentry/nestjs` 10.x（支持 NestJS 8–11）。
> 在实施之前，始终在 [docs.sentry.io/platforms/node/guides/nestjs/](https://docs.sentry.io/platforms/node/guides/nestjs/) 进行验证。

---

## 第一阶段：检测

运行这些命令以了解项目，然后进行建议：

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

# 检查基于配置类的初始化（与基于环境变量的对比）
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
- **检测到 Sentry DI 包装器？** → 项目在依赖注入令牌（例如 `SENTRY_PROXY_TOKEN`）后面包装 Sentry 以便测试。在控制器、服务和处理程序中，使用注入的代理进行所有运行时 Sentry 调用（`startSpan`、`captureException`、`withIsolationScope`），而不是直接导入 `@sentry/nestjs`。只有 `instrument.ts` 应直接导入 `@sentry/nestjs`。
- **检测到配置类？** → 项目使用类型化的配置类来配置 `Sentry.init()` 选项（例如从 YAML 或 `@nestjs/config` 加载）。任何新的 SDK 选项都必须添加到配置类型中——不要为每个环境硬编码值。
- **`SentryModule.forRoot()` 是否已注册？** → 如果它在共享模块中（例如一个 Sentry 代理模块），则不要在 `AppModule` 中再次添加它——这会导致重复拦截器注册。
- Express（默认）或 Fastify 适配器？Express 完全支持；Fastify 可以工作，但有已知的边缘情况。
- GraphQL 检测到？→ `SentryGlobalFilter` 原生处理。
- 微服务检测到？→ 建议使用 RPC 异常过滤器。
- 任务队列/`@nestjs/schedule`？→ 建议使用定时任务。
- AI 库？→ 自动注入，无需配置。
- Prisma？→ 需要手动 `prismaIntegration()`。
- 配套前端？→ 触发阶段 4 的跨链接。

---

## 第二阶段：建议

根据您发现的内容，提出具体的建议。不要提出开放式问题——直接以建议开头：

**始终推荐（核心覆盖）：**

- ✅ **错误监控** — 捕获跨 HTTP、GraphQL、RPC 和 WebSocket 上下文的未处理异常
- ✅ **跟踪** — 自动注入中间件、守卫、管道、拦截器、过滤器和路由处理程序

**检测到时推荐：**

- ✅ **分析** — 生产应用程序中 CPU 性能很重要 (`@sentry/profiling-node`)
- ✅ **日志记录** — 结构化 Sentry 日志 + 可选控制台捕获
- ✅ **定时任务** — 检测到 `@nestjs/schedule`、Bull 或 BullMQ
- ✅ **指标** — 业务 KPI 或 SLO 跟踪
- ✅ **AI 监控** — 检测到 OpenAI/Anthropic/LangChain 等（自动注入，无需配置）

**建议矩阵：**

| 功能          | 检测到时...                                  | 参考                                      |
| ------------- | ------------------------------------------ | ---------------------------------------- |
| 错误监控      | **始终** — 不可协商的基线                   | `${SKILL_ROOT}/references/error-monitoring.md` |
| 跟踪          | **始终** — NestJS 生命周期自动注入          | `${SKILL_ROOT}/references/tracing.md`          |
| 分析          | 生产 + CPU 敏感工作负载                     | `${SKILL_ROOT}/references/profiling.md`        |
| 日志记录      | **始终**；增强用于结构化日志聚合            | `${SKILL_ROOT}/references/logging.md`          |
| 指标          | 自定义业务 KPI 或 SLO 跟踪                 | `${SKILL_ROOT}/references/metrics.md`          |
| 定时任务      | 检测到 `@nestjs/schedule`、Bull 或 BullMQ | `${SKILL_ROOT}/references/crons.md`            |
| AI 监控      | 检测到 OpenAI/Anthropic/LangChain 等        | `${SKILL_ROOT}/references/ai-monitoring.md`    |

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

NestJS 需要特定的三文件初始化模式，因为 Sentry SDK 必须在 NestJS 加载它们之前修补 Node.js 模块（通过 OpenTelemetry）。

> **在创建新文件之前**，检查阶段 1 的结果：
>
> - 如果 `instrument.ts` 已存在 → 修改它，不要创建新的。
> - 如果配置类驱动 `Sentry.init()` → 从配置类中读取选项，而不是硬编码环境变量。
> - 如果存在 Sentry DI 包装器 → 在服务/控制器中不要直接导入 `@sentry/nestjs`，而要使用它。

#### 第 1 步：创建 `src/instrument.ts`

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
    // 要禁用发送用户数据和 HTTP 正文，请取消以下行。更多信息请访问：
    // https://docs.sentry.io/platforms/javascript/guides/nestjs/configuration/options/#dataCollection
    // userInfo: false,
    // httpBodies: [],
  },

  // 跟踪 — 在高流量生产环境中降低到 0.1–0.2
  tracesSampleRate: 1.0,

  // 分析（需要 @sentry/profiling-node）
  // integrations: [nodeProfilingIntegration()],
  // profileSessionSampleRate: 1.0,
  // profileLifecycle: "trace",

  // 结构化日志（SDK ≥ 9.41.0）
  enableLogs: true,
});
```

**配置驱动的 `Sentry.init()`：** 如果阶段 1 检测到类型化的配置类（例如 `SentryConfig`），请从它读取选项，而不是使用原始 `process.env`。这在使用 `@nestjs/config` 或自定义配置加载器的 NestJS 应用中很常见：

```typescript
import * as Sentry from "@sentry/nestjs";
import { loadConfiguration } from "./config";

const config = loadConfiguration();

Sentry.init({
  dsn: config.sentry.dsn,
  environment: config.sentry.environment ?? "production",
  release: config.sentry.release,
  dataCollection: config.sentry.dataCollection ?? {
    // 要禁用发送用户数据和 HTTP 正文，请取消以下行。更多信息请访问：
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

当添加新的 SDK 选项（例如 `dataCollection`、`profileSessionSampleRate`）时，请将它们添加到配置类型中，以便它们可以按环境配置。

#### 第 2 步：在 `src/main.ts` 中**首先**导入 `instrument.ts`

```typescript
// instrument.ts 必须是绝对的第一行导入 — 在 NestJS 或任何其他模块之前
import "./instrument";

import { NestFactory } from "@nestjs/core";
import { AppModule } from "./app.module";

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  // 启用优雅关闭 — 在 SIGTERM/SIGINT 上发送 Sentry 事件
  app.enableShutdownHooks();

  await app.listen(3000);
}
bootstrap();
```

> **为什么首先？** OpenTelemetry 必须在加载之前修补 `http`、`express`、数据库驱动程序和其他模块。任何在 `instrument.ts` 之前加载的模块都不会被自动注入。

#### 第 3 步：在 `src/app.module.ts` 中注册 `SentryModule` 和 `SentryGlobalFilter`

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

> ⚠️ **不要重复注册 `SentryModule.forRoot()`。** 如果阶段 1 发现它在共享库模块中已导入（例如 `SentryProxyModule` 或 `AnalyticsModule`），则不要在 `AppModule` 中再次添加它。重复注册会导致每个跟踪数据被拦截两次，导致跟踪数据膨胀。

> ⚠️ **两个入口点，不同的导入：**
>
> - `@sentry/nestjs` → SDK 初始化、捕获 API、装饰器（`SentryTraced`、`SentryCron`、`SentryExceptionCaptured`）
> - `@sentry/nestjs/setup` → NestJS DI 构造（`SentryModule`、`SentryGlobalFilter`）
>
> 永远不要从 `@sentry/nestjs`（主入口点）导入 `SentryModule`（它加载 `@nestjs/common` 之前，会破坏自动注入）。

### ESM 设置（Node ≥ 18.19.0）

对于 ESM 应用程序，使用 `--import` 而不是文件导入：

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

#### `@SentryTraced(op?)` — 任何方法注入

```typescript
import { Injectable } from "@nestjs/common";
import { SentryTraced } from "@sentry/nestjs";

@Injectable()
export class OrderService {
  @SentryTraced("order.process")
  async processOrder(orderId: string): Promise<void> {
    // 自动包装在 Sentry 跟踪中
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
    // 自动发送检查请求
  }
}
```

#### 后台任务作用域隔离

后台任务共享默认隔离作用域——用 `Sentry.withIsolationScope()` 包装以防止交叉污染：

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

将 `withIsolationScope` 应用于：`@Cron()`、`@Interval()`、`@OnEvent()`、`@Processor()` 以及任何请求生命周期之外的代码。

### 与 Sentry DI 包装器一起使用

一些 NestJS 项目在依赖注入令牌（例如 `SENTRY_PROXY_TOKEN`）后面包装 Sentry 以便测试和解耦。如果阶段 1 检测到此模式，**请使用注入的服务进行所有运行时 Sentry 调用** — 不要在控制器、服务或处理程序中直接导入 `@sentry/nestjs`。

```typescript
import { Controller, Inject } from "@nestjs/common";
import { SENTRY_PROXY_TOKEN, type SentryProxyService } from "./sentry-proxy";

@Controller("orders")
export class OrderController {
  constructor(
    @Inject(SENTRY_PROXY_TOKEN) private readonly sentry: SentryProxyService,
    private readonly orderService: OrderService,
  ) {}
}

@Post()
async createOrder(@Body() dto: CreateOrderDto) {
  return this.sentry.startSpan(
    { name: "createOrder", op: "http" },
    async () => this.orderService.create(dto),
  );
}
```

**直接 `@sentry/nestjs` 导入仍然正确的地方：**

- `instrument.ts` — 总是使用 `import * as Sentry from "@sentry/nestjs"` 进行 `Sentry.init()`
- 独立脚本和异常过滤器，它们在 DI 容器之外运行

### 验证

添加一个测试端点以确认事件已到达 Sentry：

```typescript
// 添加一个测试端点（生产前删除）
@Get("/debug-sentry")
getError() {
  throw new Error("我的第一个 Sentry 错误！");
}
```

或者发送测试消息而不会崩溃：

```typescript
import * as Sentry from "@sentry/nestjs";
Sentry.captureMessage("NestJS Sentry SDK 测试");
```

如果什么都没有出现：

1. 在 `Sentry.init()` 中设置 `debug: true` — 在 stdout 中打印 SDK 内部信息
2. 验证运行进程中的 `SENTRY_DSN` 环境变量已设置
3. 确认 `import "./instrument"` 是 `main.ts` 中的**第一行**
4. 确认在 `AppModule` 中导入了 `SentryModule`
5. 检查 DSN 格式：`https://<key>@o<org>.ingest.sentry.io/<project>`

---

## 第四阶段：跨链接

完成 NestJS 设置后，检查是否有缺少 Sentry 的配套前端：

```bash
ls -d ../frontend ../web ../client ../ui 2>/dev/null
cat ../frontend/package.json ../web/package.json 2>/dev/null \
  | grep -E '"react"|"svelte"|"vue"|"next"|"nuxt"'
```

如果存在没有 Sentry 的前端，建议匹配的技能：

| 检测到的前端   | 建议技能                                                                                                                      |
| --------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| Next.js         | `sentry-nextjs-sdk`                                                                                                                |
| React           | `sentry-react-sdk`                                                                                                                 |
| Svelte / SvelteKit  | `sentry-svelte-sdk`                                                                                                                |
| Vue / Nuxt          | 使用 `@sentry/vue` — 请参阅 [docs.sentry.io/platforms/javascript/guides/vue/](https://docs.sentry.io/platforms/javascript/guides/vue/) |
| React Native / Expo | `sentry-react-native-sdk`                                                                                                          |

---

## 故障排除

| 问题                                              | 解决方案                                                                                                                                                      |
| -------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 事件未出现                                       | 设置 `debug: true`，验证 `SENTRY_DSN`，检查 `instrument.ts` 是否首先导入                                                                                             |
| DSN 格式错误                                      | 格式：`https://<key>@o<org>.ingest.sentry.io/<project>`                                                                                                     |
| 异常未被捕获                                    | 确保 `SentryGlobalFilter` 通过 `APP_FILTER` 在 `AppModule` 中注册                                                                                             |
| 自动注入不工作                                 | `instrument.ts` 必须是 `main.ts` 中的**第一行导入** — 在所有 NestJS 导入之前                                                                                   |
| 分析未启动                                       | 需要 `tracesSampleRate > 0` + `profileSessionSampleRate > 0` + `@sentry/profiling-node` 安装                                                                 |
| `enableLogs` 不工作                             | 需要 SDK ≥ 9.41.0                                                                                                                                         |
| 没有跟踪出现                                    | 验证 `tracesSampleRate` 已设置（不是 `undefined`）                                                                                                            |
| 事务过多                                       | 降低 `tracesSampleRate` 或使用 `tracesSampler` 拖掉健康检查                                                                                             |
| Fastify + GraphQL 问题                           | 已知的边缘情况 — 请参阅 [GitHub #13388](https://github.com/getsentry/sentry-javascript/issues/13388)；优先使用 Express for GraphQL                               |
| 后台任务事件混合                                | 在任务主体中包装 `Sentry.withIsolationScope(() => { ... })`                                                                                                   |
| Prisma 跟踪丢失                                 | 在 `Sentry.init()` 中添加 `integrations: [Sentry.prismaIntegration()]`                                                                                           |
| ESM 语法错误                                  | 设置 `registerEsmLoaderHooks: false`（禁用 ESM 钩子；也禁用 ESM 模块的自动注入）                                                                 |
| `SentryModule` 破坏自动注入                      | 必须从 `@sentry/nestjs/setup` 导入，绝不能从 `@sentry/nestjs` 导入                                                                                          |
| RPC 异常未被捕获                                | 添加专用的 `SentryRpcExceptionFilter`（见异常过滤器部分中的选项 D）                                                                           |
| WebSocket 异常未被捕获                          | 在网关 `handleConnection`/`handleDisconnect` 上使用 `@SentryExceptionCaptured()`                                                                             |
| `@SentryCron` 未触发                           | 装饰器的顺序很重要 — `@SentryCron` 必须在 `@Cron` 之后                                                                                               |
| TypeScript 路径别名问题                         | 确保 `tsconfig.json` `paths` 配置正确，以便 `instrument` 从 `main.ts` 位置解析                                                                                   |
| `import * as Sentry` ESLint 错误                  | 许多项目禁止命名空间导入。使用命名导入 (`import { startSpan, captureException } from "@sentry/nestjs"`) 或使用项目中的 DI 代理代替                                                                 |
| `profilesSampleRate` vs `profileSessionSampleRate` | `profilesSampleRate` 在 SDK 10.x 中已弃用。使用 `profileSessionSampleRate` + `profileLifecycle: "trace"` 代替                                                                 |
| 每个请求都有重复的跟踪                             | `SentryModule.forRoot()` 在多个模块中注册。确保它只被调用一次 — 检查共享/库模块                                                                                   |
| 配置属性在 `instrument.ts` 中未识别                 | 当使用类型化的配置类时，新的 SDK 选项必须添加到配置类型定义中，然后重新构建项目，以便 TypeScript 能够识别它们                                                                   |

### 版本要求

| 功能                            | 最小 SDK 版本 |
| ---------------------------------- | --------------- |
| `@sentry/nestjs` 包             | 8.0.0               |
| `@SentryTraced` 装饰器          | 8.15.0              |
| `@SentryCron` 装饰器            | 8.16.0              |
| 事件发射器自动注入               | 8.39.0              |
| `SentryGlobalFilter` (统一)     | 8.40.0              |
| `Sentry.logger` API (`enableLogs`) | 9.41.0              |
| `profileSessionSampleRate`         | 10.27.0             |
| Node.js 要求                    | ≥ 18                |
| Node.js for ESM `--import`         | ≥ 18.19.0           |
| NestJS 兼容性                   | 8.x – 11.x          |
