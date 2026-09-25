# Inngest 中间件

掌握 Inngest 中间件，以处理日志记录、错误追踪、依赖注入和数据转换等横切关注点。中间件在函数生命周期的关键点运行，为可观察性和共享功能提供强大的模式。

> **这些技能主要针对 TypeScript。** 对于 Python 或 Go，请参考 [Inngest 文档](https://www.inngest.com/llms.txt) 获取语言特定的指导。核心概念适用于所有语言。

> **注意：** 中间件系统在 v4 中进行了重大重写。此处记录的生命周期钩子反映了 v4 API。如果从 v3 迁移，请查阅 [迁移指南](https://www.inngest.com/docs-markdown/reference/typescript/v4/migrations/v3-to-v4) 了解破坏性变更的详细信息。

> **⚠ 用于 Realtime 的请使用 `inngest-realtime` 技能，不要使用这个。** Inngest v3 使用 `@inngest/realtime` 中的 `realtimeMiddleware()` 将 `publish` 参数注入函数处理程序。**v4 原生支持实时功能** — `step.realtime.publish` 是内置的，不需要中间件。**v4 项目中不要安装 `@inngest/realtime`**（这是一个 v3 时代的包，在运行时会产生 `TypeError: Cls is not a constructor`）。请参阅 `inngest-realtime` 技能了解 v4 模式。

## 什么是中间件？

中间件允许代码在 Inngest 客户端生命周期的各个点运行——在函数执行期间、事件发送期间等。可以将中间件视为 Inngest 执行管道的钩子。

**何时使用中间件：**

- **可观察性：** 添加日志记录、跟踪或指标
- **依赖注入：** 在函数之间共享客户端实例
- **数据转换：** 加密/解密、验证或丰富数据
- **错误处理：** 自定义错误追踪和告警
- **身份验证：** 验证用户上下文或权限

## 中间件生命周期

中间件可以在 **客户端级别**（影响所有函数）或 **函数级别**（影响特定函数）进行注册。

### 执行顺序

```typescript
const inngest = new Inngest({
  id: "my-app",
  middleware: [
    loggingMiddleware, // 第一个执行
    errorMiddleware // 第二个执行
  ]
});

inngest.createFunction(
  {
    id: "example",
    middleware: [
      authMiddleware, // 第三个执行
      metricsMiddleware // 第四个执行
    ],
    triggers: [{ event: "test" }]
  },
  async () => {
    /* 函数代码 */
  }
);
```

**顺序很重要：** 客户端中间件首先执行，然后是函数中间件，按指定顺序执行。

## 创建自定义中间件

### 基本中间件结构

```typescript
import { InngestMiddleware } from "inngest";

const loggingMiddleware = new InngestMiddleware({
  name: "日志记录中间件",
  init() {
    // 初始化阶段 - 当客户端初始化时运行
    const logger = setupLogger();

    return {
      // 函数执行生命周期
      // 注意：`fn` 在中间件泛型中是弱类型的；`fn.id` 在运行时有效
      onFunctionRun({ ctx, fn }) {
        return {
          beforeExecution() {
            logger.info("函数开始", {
              functionId: fn.id,
              eventName: ctx.event.name,
              runId: ctx.runId
            });
          },

          afterExecution() {
            logger.info("函数完成", {
              functionId: fn.id,
              runId: ctx.runId
            });
          },

          transformOutput({ result }) {
            // 记录函数输出
            logger.debug("函数输出", {
              functionId: fn.id,
              output: result.data
            });

            // 返回未修改的结果
            return { result };
          }
        };
      },

      // 事件发送生命周期
      onSendEvent() {
        return {
          transformInput({ payloads }) {
            logger.info("发送事件", {
              count: payloads.length,
              events: payloads.map((p) => p.name)
            });

            // 展开以将只读数组转换为可变数组
            return { payloads: [...payloads] };
          }
        };
      }
    };
  }
});
```

### Python 实现

Python 中间件遵循类似的模式。请参阅 [依赖注入参考](./references/dependency-injection.md) 获取完整的 Python 示例。

````

## 依赖注入

在所有函数之间共享昂贵的或具有状态的客户端。**请参阅 [依赖注入参考](./references/dependency-injection.md) 获取详细模式。**

### 快速示例 - 内置 DI

```typescript
import { dependencyInjectionMiddleware } from "inngest";

const inngest = new Inngest({
  id: 'my-app',
  middleware: [
    dependencyInjectionMiddleware({
      openai: new OpenAI(),
      db: new PrismaClient(),
    }),
  ],
});

// 函数自动获取注入的依赖项
inngest.createFunction(
  { id: "ai-summary", triggers: [{ event: "document/uploaded" }] },
  async ({ event, openai, db }) => {
    // 依赖项在函数上下文中可用
    const summary = await openai.chat.completions.create({
      messages: [{ role: "user", content: event.data.content }],
      model: "gpt-4",
    });

    await db.document.update({
      where: { id: event.data.documentId },
      data: { summary: summary.choices[0].message.content }
    });
  }
);
````

## 中间件包

除了 `dependencyInjectionMiddleware`（内置的，如上所示），Inngest 还提供作为**单独包**的官方中间件。**请参阅 [中间件参考](./references/built-in-middleware.md) 获取完整详细信息。**

### 加密中间件

```bash
npm install @inngest/middleware-encryption
```

```typescript
import { encryptionMiddleware } from "@inngest/middleware-encryption";

const inngest = new Inngest({
  id: "my-app",
  middleware: [
    encryptionMiddleware({
      key: process.env.ENCRYPTION_KEY
    })
  ]
});
```

自动加密所有步骤数据、函数输出和事件 `data.encrypted` 字段。支持通过 `fallbackDecryptionKeys` 进行密钥轮换。

### Sentry 错误追踪

```bash
npm install @inngest/middleware-sentry
```

```typescript
import * as Sentry from "@sentry/node";
import { sentryMiddleware } from "@inngest/middleware-sentry";

Sentry.init({
  /* 你的 Sentry 配置 */
});

const inngest = new Inngest({
  id: "my-app",
  middleware: [sentryMiddleware()]
});
```

捕获异常，为每个函数运行添加跟踪，并将函数 ID 和事件名称作为上下文包含。需要 `@sentry/*@>=8.0.0`。

## 常见中间件模式

### 指标和性能追踪

```typescript
const metricsMiddleware = new InngestMiddleware({
  name: "指标追踪",
  init() {
    return {
      onFunctionRun({ ctx, fn }) {
        let startTime: number;

        return {
          beforeExecution() {
            startTime = Date.now();
            metrics.increment("inngest.step.started", {
              function: fn.id,
              event: ctx.event.name
            });
          },

          afterExecution() {
            const duration = Date.now() - startTime;
            metrics.histogram("inngest.step.duration", duration, {
              function: fn.id,
              event: ctx.event.name
            });
          },

          transformOutput({ result }) {
            const status = result.error ? "error" : "success";
            metrics.increment("inngest.step.completed", {
              function: fn.id,
              status: status
            });

            return { result };
          }
        };
      }
    };
  }
});
```

### 高级模式

**身份验证：** 验证令牌并注入用户上下文
**条件逻辑：** 根据事件类型或函数应用中间件
**断路器：** 防止外部服务导致级联故障

### 基于配置的中间件

创建可重用的中间件，为不同的环境和用例提供配置选项。请参阅参考文档获取完整示例。

## 最佳实践

### 设计原则

1. **保持中间件专注：** 每个中间件处理一个关注点
2. **优雅地处理错误：** 不要让中间件崩溃函数
3. **考虑性能：** 中间件在每次执行时运行
4. **使用正确的类型：** 让 TypeScript 推断中间件类型
5. **彻底测试：** 中间件影响所有使用它的函数

### 常见用例

- **重试逻辑** 用于瞬态故障
- **断路器** 用于外部服务调用
- **请求/响应日志记录** 用于调试
- **用户上下文丰富** 来自外部源
- **功能标志** 用于逐步发布
- **自定义身份验证** 和授权检查

### 中间件中的错误处理

```typescript
const robustMiddleware = new InngestMiddleware({
  name: "健壮中间件",
  init() {
    return {
      onFunctionRun({ ctx, fn }) {
        return {
          transformOutput({ result }) {
            try {
              // 你的中间件逻辑
              return performTransformation(result);
            } catch (middlewareError) {
              // 记录错误但不要崩溃函数
              console.error("中间件错误:", middlewareError);

              // 中间件失败时返回原始结果
              return { result };
            }
          }
        };
      }
    };
  }
});
```

### 测试中间件

使用 Inngest 的测试工具（`createMockContext`、`createMockFunction`）来单元测试中间件行为。

**有关完整的实现示例和高级模式，请参阅：**

- [依赖注入参考](./references/dependency-injection.md)
- [内置中间件参考](./references/built-in-middleware.md)
