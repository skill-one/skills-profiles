# Inngest 持久函数

掌握 Inngest 的持久执行模型，用于构建容错、长时间运行的流程。这项技能涵盖了从触发器到错误处理的完整生命周期。

> **这些技能专注于 TypeScript。** 对于 Python 或 Go，请参考 Inngest 文档 [Inngest documentation](https://www.inngest.com/llms.txt) 获取语言特定的指导。核心概念适用于所有语言。

## 需要了解的核心概念

### **持久执行模型**

- **每个步骤** 应该封装副作用和非确定性代码
- **缓存** 防止重新执行已完成的步骤
- **状态持久化** 在基础设施故障时仍然存在
- **自动重试** 具有可配置的重试次数

### **步骤执行流程**

```typescript
// ❌ BAD: 步骤外部的非确定性逻辑
async ({ event, step }) => {
  const timestamp = Date.now(); // 这会在多次运行！

  const result = await step.run("process-data", () => {
    return processData(event.data);
  });
};

// ✅ GOOD: 所有非确定性逻辑都在步骤内
async ({ event, step }) => {
  const result = await step.run("process-with-timestamp", () => {
    const timestamp = Date.now(); // 只运行一次
    return processData(event.data, timestamp);
  });
};
```

## 函数限制

**每个 Inngest 函数都有以下硬限制：**

- **最多 1,000 步** 每个函数运行
- **每步最多 4MB** 返回数据
- **最多 32MB** 组合函数运行状态，包括事件数据、步骤输出和函数输出
- 每个步骤 = 独立的 HTTP 请求 (~50-100ms 开销)

如果你遇到了这些限制，请将你的函数拆分成更小的函数，并通过 `step.invoke()` 或 `step.sendEvent()` 连接它们。

## 何时使用步骤

**始终用 `step.run()` 封装：**

- API 调用和网络请求
- 数据库读写
- 文件 I/O 操作
- 任何非确定性操作
- 任何希望在失败时独立重试的操作

**永远不要用 `step.run()` 封装：**

- 纯计算和数据处理转换
- 简单的验证逻辑
- 没有副作用的确定性操作
- 日志记录（在步骤外部使用）

## 函数创建

### 基本函数结构

```typescript
const processOrder = inngest.createFunction(
  {
    id: "process-order", // 唯一，永远不要更改
    triggers: [{ event: "order/created" }],
    retries: 4, // 默认：每步 4 次重试
    concurrency: 10 // 最大并发执行数
  },
  async ({ event, step }) => {
    // 你的持久化工作流
  }
);
```

### **步骤 ID 和缓存**

```typescript
// 步骤 ID 可以重复使用 - Inngest 会自动处理计数器
const data = await step.run("fetch-data", () => fetchUserData());
const more = await step.run("fetch-data", () => fetchOrderData()); // 不同的执行

// 使用描述性 ID 以提高清晰度
await step.run("validate-payment", () => validatePayment(event.data.paymentId));
await step.run("charge-customer", () => chargeCustomer(event.data));
await step.run("send-confirmation", () => sendEmail(event.data.email));
```

## 触发器和事件

### **事件触发器**

触发器定义在 `createFunction` 的第一个参数中的 `triggers` 数组中：

```typescript
// 单个事件触发器
inngest.createFunction(
  { id: "my-fn", triggers: [{ event: "user/signup" }] },
  async ({ event }) => { /* ... */ }
);

// 带条件过滤的事件
inngest.createFunction(
  { id: "my-fn", triggers: [{ event: "user/action", if: 'event.data.action == "purchase" && event.data.amount > 100' }] },
  async ({ event }) => { /* ... */ }
);

// 多个触发器（最多 10 个）
inngest.createFunction(
  {
    id: "my-fn",
    triggers: [
      { event: "user/signup" },
      { event: "user/login", if: 'event.data.firstLogin == true' },
      { cron: "0 9 * * *" } // 每天早上 9 点
  ],
  async ({ event }) => { /* ... */ }
);
```

### **Cron 触发器**

```typescript
// 基本 Cron
inngest.createFunction(
  { id: "my-fn", triggers: [{ cron: "0 */6 * * *" }] }, // 每 6 小时
  async ({ step }) => { /* ... */ }
);

// 带时区
inngest.createFunction(
  { id: "my-fn", triggers: [{ cron: "TZ=Europe/Paris 0 12 * * 5" }] }, // 巴黎时间周五中午
  async ({ step }) => { /* ... */ }
);

// 与事件结合
inngest.createFunction(
  {
    id: "my-fn",
    triggers: [
      { event: "manual/report.requested" },
      { cron: "0 0 * * 0" } // 每周日
  ],
  async ({ event, step }) => { /* ... */ }
);
```

### **函数调用**

```typescript
// 作为步骤调用另一个函数
const result = await step.invoke("generate-report", {
  function: generateReportFunction,
  data: { userId: event.data.userId }
});

// 使用返回数据
await step.run("process-report", () => {
  return processReport(result);
});
```

## 幂等性策略

### **事件级幂等性（生产者端）**

```typescript
// 防止重复事件，使用自定义 ID
await inngest.send({
  id: `checkout-completed-${cartId}`, // 24 小时去重
  name: "cart/checkout.completed",
  data: { cartId, email: "user@example.com" }
});
```

### **函数级幂等性（消费者端）**

```typescript
const sendEmail = inngest.createFunction(
  {
    id: "send-checkout-email",
    triggers: [{ event: "cart/checkout.completed" }],
    // 每 24 小时每个 cartId 只运行一次
    idempotency: "event.data.cartId"
  },
  async ({ event, step }) => {
    // 对于相同的 cartId，这个函数不会运行两次
  }
);

// 复杂的幂等性键
const processUserAction = inngest.createFunction(
  {
    id: "process-user-action",
    triggers: [{ event: "user/action.performed" }],
    // 唯一，针对每个用户和组织的组合
    idempotency: 'event.data.userId + "-" + event.data.organizationId'
  },
  async ({ event, step }) => {
    /* ... */
  }
);
```

## 取消模式

### **事件取消**

在表达式中，`event` = **原始** 触发事件，`async` = **新** 被匹配的事件。有关完整详细信息，请参阅 [表达式语法参考](../references/expressions.md)。

```typescript
const processOrder = inngest.createFunction(
  {
    id: "process-order",
    triggers: [{ event: "order/created" }],
    cancelOn: [
      {
        event: "order/cancelled",
        if: 'event.data.orderId == async.data.orderId'
      }
    ]
  },
  async ({ event, step }) => {
    await step.sleepUntil("wait-for-payment", event.data.paymentDue);
    // 如果收到 order/cancelled 事件，将被取消
    await step.run("charge-payment", () => processPayment(event.data));
  }
);
```

### **超时取消**

```typescript
const processWithTimeout = inngest.createFunction(
  {
    id: "process-with-timeout",
    triggers: [{ event: "long/process.requested" }],
    timeouts: {
      start: "5m", // 如果 5 分钟内未启动，则取消
      finish: "30m" // 如果 30 分钟内未完成，则取消
    }
  },
  async ({ event, step }) => {
    /* ... */
  }
);
```

### **处理取消清理**

```typescript
// 监听取消事件
const cleanupCancelled = inngest.createFunction(
  { id: "cleanup-cancelled-process", triggers: [{ event: "inngest/function.cancelled" }] },
  async ({ event, step }) => {
    if (event.data.function_id === "process-order") {
      await step.run("cleanup-resources", () => {
        return cleanupOrderResources(event.data.run_id);
      });
    }
  }
);
```

## 错误处理和重试

### **默认重试行为**

- **每步 5 次尝试**（1 次初始 + 4 次重试）
- **指数退避** 带抖动
- **每步独立的重试计数器**

### **自定义重试配置**

```typescript
const reliableFunction = inngest.createFunction(
  {
    id: "reliable-function",
    triggers: [{ event: "critical/task" }],
    retries: 10 // 每步最多 10 次重试
  },
  async ({ event, step, attempt }) => {
    // `attempt` 是函数级别的尝试计数器（0 索引）
    // 它跟踪当前正在执行的步骤的重试，而不是整个函数
    if (attempt > 5) {
      // 后续尝试的逻辑不同
    }
  }
);
```

### **不可重试错误**

防止重试那些重试后不会成功的代码。

```typescript
import { NonRetriableError } from "inngest";

const processUser = inngest.createFunction(
  { id: "process-user", triggers: [{ event: "user/process.requested" }] },
  async ({ event, step }) => {
    const user = await step.run("fetch-user", async () => {
      const user = await db.users.findOne(event.data.userId);

      if (!user) {
        // 不要重试 - 用户不存在
        throw new NonRetriableError("User not found, stopping execution");
      }

      return user;
    });

    // 继续处理...
  }
);
```

### **自定义重试时间**

```typescript
import { RetryAfterError } from "inngest";

const respectRateLimit = inngest.createFunction(
  { id: "api-call", triggers: [{ event: "api/call.requested" }] },
  async ({ event, step }) => {
    await step.run("call-api", async () => {
      const response = await externalAPI.call(event.data);

      if (response.status === 429) {
        // 根据 API 指定时间重试
        const retryAfter = response.headers["retry-after"];
        throw new RetryAfterError("Rate limited", `${retryAfter}s`);
      }

      return response.data;
    });
  }
);
```

## 日志最佳实践

### **正确的日志设置**

```typescript
import winston from "winston";

// 配置日志器
const logger = winston.createLogger({
  level: "info",
  format: winston.format.json(),
  transports: [new winston.transports.Console()]
});

const inngest = new Inngest({
  id: "my-app",
  logger // 将日志器传递给客户端
});

// 或使用内置的 ConsoleLogger 进行简单的日志级别控制
import { ConsoleLogger, Inngest } from "inngest";

const inngest = new Inngest({
  id: "my-app",
  logger: new ConsoleLogger({ level: "debug" }) // "debug" | "info" | "warn" | "error"
});
```

**⚠️ v4 不兼容变更：** `logLevel` 选项已被移除。使用 `logger` 选项与 `ConsoleLogger` 或自定义日志器。

### **函数日志模式**

```typescript
const processData = inngest.createFunction(
  { id: "process-data", triggers: [{ event: "data/process.requested" }] },
  async ({ event, step, logger }) => {
    // ✅ GOOD: 步骤内日志以避免重复
    const result = await step.run("fetch-data", async () => {
      logger.info("Fetching data for user", { userId: event.data.userId });
      return await fetchUserData(event.data.userId);
    });

    // ❌ AVOID: 步骤外日志可能导致重复
    // logger.info("Processing complete"); // 这可能运行多次！

    await step.run("log-completion", async () => {
      logger.info("Processing complete", { resultCount: result.length });
    });
  }
);
```

## 性能优化

### **检查点**

检查点在 **v4 中默认启用**。它允许函数在执行过程中定期持久化状态，减少步骤之间的延迟。

```typescript
// v4 中检查点默认启用
// 配置 maxRuntime 以适用于无服务器平台（设置为平台超时的 60-80%）
const realTimeFunction = inngest.createFunction(
  {
    id: "real-time-function",
    triggers: [{ event: "realtime/process" }],
    checkpointing: {
      maxRuntime: "50s", // 对于 60s 超时的无服务器平台
    }
  },
  async ({ event, step }) => {
    // 步骤立即执行，并带有定期检查点
    const result1 = await step.run("step-1", () => process1(event.data));
    const result2 = await step.run("step-2", () => process2(result1));
    return { result2 };
  }
);

// 如果需要禁用检查点
const legacyFunction = inngest.createFunction(
  {
    id: "legacy-function",
    triggers: [{ event: "legacy/process" }],
    checkpointing: false
  },
  async ({ event, step }) => { /* ... */ }
);
```

## 高级模式

### **条件步骤执行**

```typescript
const conditionalProcess = inngest.createFunction(
  { id: "conditional-process", triggers: [{ event: "process/conditional" }] },
  async ({ event, step }) => {
    const userData = await step.run("fetch-user", () => {
      return getUserData(event.data.userId);
    });

    // 条件步骤执行
    if (userData.isPremium) {
      await step.run("premium-processing", () => {
        return processPremiumFeatures(userData);
      });
    }

    // 总是运行
    await step.run("standard-processing", () => {
      return processStandardFeatures(userData);
    });
  }
);
```

### **错误恢复模式**

```typescript
const robustProcess = inngest.createFunction(
  { id: "robust-process", triggers: [{ event: "process/robust" }] },
  async ({ event, step }) => {
    let primaryResult;

    try {
      primaryResult = await step.run("primary-service", () => {
        return callPrimaryService(event.data);
      });
    } catch (error) {
      // 回退到次要服务
      primaryResult = await step.run("fallback-service", () => {
        return callSecondaryService(event.data);
      });
    }

    return { result: primaryResult };
  }
);
```

## 常见错误

1. **❌ 步骤外部的非确定性代码**
2. **❌ 步骤外部的数据库调用**
3. **❌ 步骤外部的日志记录（导致重复）**
4. **❌ 部署后更改步骤 ID**
5. **❌ 不处理 NonRetriableError 情况**
6. **❌ 忽略关键函数的幂等性**

## 下一步

- 查看 **inngest-steps** 获取详细的步骤方法参考
- 查看 [references/step-execution.md](references/step-execution.md) 获取详细的步骤模式
- 查看 [references/error-handling.md](references/error-handling.md) 获取全面的错误策略
- 查看 [references/observability.md](references/observability.md) 获取监控和跟踪设置
- 查看 [references/checkpointing.md](references/checkpointing.md) 获取性能优化细节

---

这项技能涵盖了 Inngest 的持久函数模式。有关事件发送和 webhook 处理，请参阅 `inngest-events` 技能。
