# Inngest 步骤

使用 Inngest 的步骤方法构建健壮、持久的流程。每个步骤是一个独立的 HTTP 请求，可以独立重试和监控。

> **这些技能主要针对 TypeScript。** 对于 Python 或 Go，请参考 [Inngest 文档](https://www.inngest.com/llms.txt) 获取特定语言的指导。核心概念适用于所有语言。

## 核心概念

**🔄 关键：每个步骤都会从头开始重新运行你的函数。** 将所有非确定性代码（API 调用、数据库查询、随机性）全部放在步骤内部，切勿放在外部。

**📊 步骤限制：** 每个函数最多有 1,000 个步骤和 4MB 的总步骤数据。

```typescript
// ❌ 错误 - 将运行 4 次
export default inngest.createFunction(
  { id: "bad-example", triggers: [{ event: "test" }] },
  async ({ step }) => {
    console.log("This logs 4 times!"); // 位于步骤外部 = 错误
    await step.run("a", () => console.log("a"));
    await step.run("b", () => console.log("b"));
    await step.run("c", () => console.log("c"));
  }
);

// ✅ 正确 - 每个步骤只打印一次
export default inngest.createFunction(
  { id: "good-example", triggers: [{ event: "test" }] },
  async ({ step }) => {
    await step.run("log-hello", () => console.log("hello"));
    await step.run("a", () => console.log("a"));
    await step.run("b", () => console.log("b"));
    await step.run("c", () => console.log("c"));
  }
);
```

## step.run()

执行可重试的代码作为步骤。**每个步骤 ID 都可以重复使用** - Inngest 会自动处理计数器。

```typescript
// 基本用法
const result = await step.run("fetch-user", async () => {
  const user = await db.user.findById(userId);
  return user; // 始终返回有用数据
});

// 同步代码同样适用
const transformed = await step.run("transform-data", () => {
  return processData(result);
});

// 产生副作用（无需返回值）
await step.run("send-notification", async () => {
  await sendEmail(user.email, "Welcome!");
});
```

**✅ 应该：**

- 将所有非确定性逻辑放在步骤内部
- 为后续步骤返回有用数据
- 在循环中重复使用步骤 ID（计数器自动处理）

**❌ 不应该：**

- 不必要地将确定性逻辑放在步骤中
- 忘记每个步骤 = 独立的 HTTP 请求

## step.sleep()

暂停执行而不使用计算时间。

```typescript
// 持续时间字符串
await step.sleep("wait-24h", "24h");
await step.sleep("short-delay", "30s");
await step.sleep("weekly-pause", "7d");

// 在工作流中使用
await step.run("send-welcome", () => sendEmail(email));
await step.sleep("wait-for-engagement", "3d");
await step.run("send-followup", () => sendFollowupEmail(email));
```

## step.sleepUntil()

在特定日期时间暂停。

```typescript
const reminderDate = new Date("2024-12-25T09:00:00Z");
await step.sleepUntil("wait-for-christmas", reminderDate);

// 从事件数据中获取
const scheduledTime = new Date(event.data.remind_at);
await step.sleepUntil("wait-for-scheduled-time", scheduledTime);
```

## step.waitForEvent()

**🚨 关键：waitForEvent 仅捕获在此步骤执行后发送的事件。**

- ❌ 事件在 waitForEvent 运行之前发送 → 将不会被捕获
- ✅ 事件在 waitForEvent 运行之后发送 → 将会被捕获
- 始终检查 `null` 返回值（表示超时，事件未到达）

```typescript
// 带超时的事件等待
const approval = await step.waitForEvent("wait-for-approval", {
  event: "app/invoice.approved",
  timeout: "7d",
  match: "data.invoiceId" // 简单匹配
});

// 表达式匹配（CEL 语法）
const subscription = await step.waitForEvent("wait-for-subscription", {
  event: "app/subscription.created",
  timeout: "30d",
  if: "event.data.userId == async.data.userId && async.data.plan == 'pro'"
});

// 处理超时
if (!approval) {
  await step.run("handle-timeout", () => {
    // 审批未到达
    return notifyAccountingTeam();
  });
}
```

**✅ 应该：**

- 使用唯一的 ID 进行匹配（userId、sessionId、requestId）
- 始终设置合理的超时
- 处理 `null` 返回值（超时情况）
- 与 Realtime 结合使用，实现人机交互流程

**❌ 不应该：**

- 期待在此步骤之前发送的事件被处理
- 在生产环境中不使用超时

### 表达式语法

在表达式中，`event` = **原始**触发事件，`async` = **新**被匹配的事件。有关完整语法、运算符和模式，请参阅 [表达式语法参考](../references/expressions.md)。

## step.waitForSignal()

等待唯一的信号（不是事件）。更适合 1:1 匹配。

```typescript
const taskId = "task-" + crypto.randomUUID();

const signal = await step.waitForSignal("wait-for-task-completion", {
  signal: taskId,
  timeout: "1h",
  onConflict: "replace" // 必须设置："replace" 覆盖待处理的信号，"fail" 抛出错误
});

// 通过 Inngest API 或 SDK 在其他地方发送信号
// POST /v1/events，信号匹配 taskId
```

**何时使用：**

- **waitForEvent**：多个函数可能处理相同的事件
- **waitForSignal**：精确的 1:1 信号到特定函数运行

## step.sendEvent()

无需等待结果即可分发给其他函数。

```typescript
// 触发其他函数
await step.sendEvent("notify-systems", {
  name: "user/profile.updated",
  data: { userId: user.id, changes: profileChanges }
});

// 同时发送多个事件
await step.sendEvent("batch-notifications", [
  { name: "billing/invoice.created", data: { invoiceId } },
  { name: "email/invoice.send", data: { email: user.email, invoiceId } }
]);
```

**使用场景：** 你想触发其他函数，但不需要它们的结果。

## step.invoke()

调用其他函数并处理其结果。非常适合组合。

```typescript
const computeSquare = inngest.createFunction(
  { id: "compute-square", triggers: [{ event: "calculate/square" }] },
  async ({ event }) => {
    return { result: event.data.number * event.data.number };
  }
);

// 调用并使用结果
const square = await step.invoke("get-square", {
  function: computeSquare,
  data: { number: 4 }
});

console.log(square.result); // 16，完全类型化！

// 用于跨应用调用（当无法直接导入函数时）：
import { referenceFunction } from "inngest";

const externalFn = referenceFunction({
  appId: "other-app",
  functionId: "other-fn"
});

const result = await step.invoke("call-external", {
  function: externalFn,
  data: { key: "value" }
});
```

**警告：v4 版本破坏性变更：** 字符串函数 ID（例如 `function: "my-app-other-fn"`）不再支持在 `step.invoke()` 中。使用导入的函数引用或 `referenceFunction()` 进行跨应用调用。

**非常适合：**

- 将复杂工作流分解为可组合的函数
- 在多个工作流中重用逻辑
- Map-reduce 模式

## 模式

### 使用步骤的循环

重复使用步骤 ID - Inngest 自动处理计数器。

```typescript
const allProducts = [];
let cursor = null;
let hasMore = true;

while (hasMore) {
  // 相同的 ID "fetch-page" 被重复使用 - 计数器自动处理
  const page = await step.run("fetch-page", async () => {
    return shopify.products.list({ cursor, limit: 50 });
  });

  allProducts.push(...page.products);

  if (page.products.length < 50) {
    hasMore = false;
  } else {
    cursor = page.products[49].id;
  }
}

await step.run("process-products", () => {
  return processAllProducts(allProducts);
});
```

### 并行执行

使用 Promise.all 进行并行步骤。**在 v4 中，并行步骤执行默认优化**

```typescript
// 创建步骤但不等待
const sendEmail = step.run("send-email", async () => {
  return await sendWelcomeEmail(user.email);
});

const updateCRM = step.run("update-crm", async () => {
  return await crmService.addUser(user);
});

const createSubscription = step.run("create-subscription", async () => {
  return await subscriptionService.create(user.id);
});

// 并行执行所有步骤
const [emailId, crmRecord, subscription] = await Promise.all([
  sendEmail,
  updateCRM,
  createSubscription
]);

// v4 默认优化并行步骤
export default inngest.createFunction(
  {
    id: "parallel-heavy-function",
    triggers: [{ event: "process/batch" }]
  },
  async ({ event, step }) => {
    const results = await Promise.all(
      event.data.items.map((item, i) =>
        step.run(`process-item-${i}`, () => processItem(item))
      )
    );
  }
);

// ⚠️ v4 优化并行性中的 Promise.race() 行为：
// 所有 Promise 都会解决后再由 race 返回。使用 group.parallel() 进行真正的 race：
const winner = await group.parallel(async () => {
  return Promise.race([
    step.run("fast-service", () => callFastService()),
    step.run("slow-service", () => callSlowService())
  ]);
});

// 如果需要禁用优化并行性：
// 在客户端级别：new Inngest({ id: "app", optimizeParallelism: false })
// 在函数级别：{ id: "fn", optimizeParallelism: false, triggers: [...] }
```

有关并发和限流选项，请参阅 **inngest-flow-control**。

### 分块处理任务

非常适合带并行步骤的批量处理。

```typescript
export default inngest.createFunction(
  { id: "process-large-dataset", triggers: [{ event: "data/process.large" }] },
  async ({ event, step }) => {
    const chunks = chunkArray(event.data.items, 10);

    // 并行处理块
    const results = await Promise.all(
      chunks.map((chunk, index) =>
        step.run(`process-chunk-${index}`, () => processChunk(chunk))
      )
    );

    // 合并结果
    await step.run("combine-results", () => {
      return aggregateResults(results);
    });
  }
);
```

## 关键注意事项

**🔄 函数重执行：** 步骤外部的代码在每个步骤执行时都会运行
**⏰ 事件时间：** waitForEvent 仅捕获步骤运行后发送的事件
**🔢 步骤限制：** 每个函数最多 1,000 个步骤，每个步骤输出最多 4MB，每个函数运行总大小最多 32MB
**📨 HTTP 请求：** v4 默认启用检查点，减少 HTTP 开销。对于无服务器平台，请在客户端配置 `maxRuntime`
**🔁 步骤 ID：** 可以在循环中重复使用 - Inngest 自动处理计数器
**⚡ 并行性：** 使用 Promise.all 进行并行步骤（v4 默认优化）。注意 Promise.race() 等待所有 Promise 解决 — 使用 `group.parallel()` 进行真正的 race 语义

## 常见用例

- **人机交互：** waitForEvent + Realtime UI
- **多步骤引导：** 步骤间使用 sleep，waitForEvent 等待用户操作
- **数据处理：** 并行步骤进行分块工作
- **外部集成：** step.run 进行可靠的 API 调用
- **AI 工作流：** step.ai 进行持久的 LLM 组合
- **函数组合：** step.invoke 构建复杂工作流

记住：步骤使你的函数变得持久、可观察和可调试。拥抱它们！
