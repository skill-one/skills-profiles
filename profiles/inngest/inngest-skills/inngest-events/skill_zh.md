# Inngest 事件

掌握 Inngest 事件设计和交付模式。事件是 Inngest 的基础 - 学习设计健壮的事件模式、实现幂等性、利用扇出模式以及有效处理系统事件。

> **这些技能主要针对 TypeScript。** 对于 Python 或 Go，请参考 Inngest 文档 [Inngest documentation](https://www.inngest.com/llms.txt) 获取语言特定的指导。核心概念适用于所有语言。

## 事件负载格式

每个 Inngest 事件都是一个具有必需和可选属性的 JSON 对象：

### 必需属性

```typescript
type Event = {
  name: string; // 事件类型（触发函数）
  data: object; // 负载数据（任何嵌套的 JSON）
};
```

### 完整模式

```typescript
type EventPayload = {
  name: string; // 必需：事件类型
  data: Record<string, any>; // 必需：事件数据
  id?: string; // 可选：去重 ID
  ts?: number; // 可选：时间戳（Unix ms）
  v?: string; // 可选：模式版本
};
```

### 基本事件示例

```typescript
await inngest.send({
  name: "billing/invoice.paid",
  data: {
    customerId: "cus_NffrFeUfNV2Hib",
    invoiceId: "in_1J5g2n2eZvKYlo2C0Z1Z2Z3Z",
    userId: "user_03028hf09j2d02",
    amount: 1000,
    metadata: {
      accountId: "acct_1J5g2n2eZvKYlo2C0Z1Z2Z3Z",
      accountName: "Acme.ai"
    }
  }
});
```

## 事件命名规范

**使用对象-动作模式：** `域名/名词.动词`

### 推荐模式

```typescript
// ✅ 良好：清晰的对象-动作模式
"billing/invoice.paid";
"user/profile.updated";
"order/item.shipped";
"ai/summary.completed";

// ✅ 良好：使用域名前缀进行组织
"stripe/customer.created";
"intercom/conversation.assigned";
"slack/message.posted";

// ❌ 避免：不明确或不一致
"payment"; // 发生了什么？
"user_update"; // 使用点号，而不是下划线
"invoiceWasPaid"; // 太冗长
```

### 命名指南

- **过去式：** 事件描述发生了什么（`created`、`updated`、`failed`）
- **点表示法：** 使用点表示层级（`billing/invoice.paid`）
- **前缀：** 对相关事件进行分组（`api/user.created`、`webhook/stripe.received`）
- **一致性：** 建立模式并坚持使用

## 事件 ID 和幂等性

**何时使用 ID：** 防止重复处理，当事件可能被多次发送时。

### 基本去重

```typescript
await inngest.send({
  id: "cart-checkout-completed-ed12c8bde", // 每个事件类型唯一
  name: "storefront/cart.checkout.completed",
  data: {
    cartId: "ed12c8bde",
    items: ["item1", "item2"]
  }
});
```

### ID 最佳实践

```typescript
// ✅ 良好：针对事件类型和实例
id: `invoice-paid-${invoiceId}`;
id: `user-signup-${userId}-${timestamp}`;
id: `order-shipped-${orderId}-${trackingNumber}`;

// ❌ 坏：跨事件类型共享的通用 ID
id: invoiceId; // 可能与其他事件冲突
id: "user-action"; // 太通用
id: customerId; // 同一客户，不同事件
```

**去重窗口：** 接收第一个事件后的 24 小时

参考 **inngest-durable-functions** 获取幂等性配置。

## `ts` 参数用于延迟交付

**何时使用：** 调度事件进行未来处理或保持事件顺序。

### 未来调度

```typescript
const oneHourFromNow = Date.now() + 60 * 60 * 1000;

await inngest.send({
  name: "trial/reminder.send",
  ts: oneHourFromNow, // 1 小时后交付
  data: {
    userId: "user_123",
    trialExpiresAt: "2024-02-15T12:00:00Z"
  }
});
```

### 保持事件顺序

```typescript
// 带时间戳的事件按时间顺序处理
const events = [
  {
    name: "user/action.performed",
    ts: 1640995200000, // 较早
    data: { action: "login" }
  },
  {
    name: "user/action.performed",
    ts: 1640995260000, // 较晚
    data: { action: "purchase" }
  }
];

await inngest.send(events);
```

## 扇出模式

**用例：** 一个事件触发多个独立的函数，以提高可靠性和并行处理。

### 基本扇出实现

```typescript
// 发送单个事件
await inngest.send({
  name: "user/signup.completed",
  data: {
    userId: "user_123",
    email: "user@example.com",
    plan: "pro"
  }
});

// 多个函数响应相同事件
const sendWelcomeEmail = inngest.createFunction(
  { id: "send-welcome-email", triggers: [{ event: "user/signup.completed" }] },
  async ({ event, step }) => {
    await step.run("send-email", async () => {
      return sendEmail({
        to: event.data.email,
        template: "welcome"
      });
    });
  }
);

const createTrialSubscription = inngest.createFunction(
  { id: "create-trial", triggers: [{ event: "user/signup.completed" }] },
  async ({ event, step }) => {
    await step.run("create-subscription", async () => {
      return stripe.subscriptions.create({
        customer: event.data.stripeCustomerId,
        trial_period_days: 14
      });
    });
  }
);

const addToCrm = inngest.createFunction(
  { id: "add-to-crm", triggers: [{ event: "user/signup.completed" }] },
  async ({ event, step }) => {
    await step.run("crm-sync", async () => {
      return crm.contacts.create({
        email: event.data.email,
        plan: event.data.plan
      });
    });
  }
);
```

### 扇出优势

- **独立性：** 函数独立运行；一个失败不会影响其他函数
- **并行执行：** 所有函数同时运行
- **选择性重放：** 仅重放失败的函数
- **跨服务：** 触发不同代码库/语言的函数

### 高级扇出使用 `waitForEvent`

在表达式中，`event` = **原始** 触发事件，`async` = **新** 被匹配的事件。参考 [表达式语法参考](../references/expressions.md) 获取完整详细信息。

```typescript
const orchestrateOnboarding = inngest.createFunction(
  { id: "orchestrate-onboarding", triggers: [{ event: "user/signup.completed" }] },
  async ({ event, step }) => {
    // 扇出到多个服务
    await step.sendEvent("fan-out", [
      { name: "email/welcome.send", data: event.data },
      { name: "subscription/trial.create", data: event.data },
      { name: "crm/contact.add", data: event.data }
    ]);

    // 等待全部完成
    const [emailResult, subResult, crmResult] = await Promise.all([
      step.waitForEvent("email-sent", {
        event: "email/welcome.sent",
        timeout: "5m",
        if: `event.data.userId == async.data.userId`
      }),
      step.waitForEvent("subscription-created", {
        event: "subscription/trial.created",
        timeout: "5m",
        if: `event.data.userId == async.data.userId`
      }),
      step.waitForEvent("crm-synced", {
        event: "crm/contact.added",
        timeout: "5m",
        if: `event.data.userId == async.data.userId`
      })
    ]);

    // 完成入职
    await step.run("complete-onboarding", async () => {
      return completeUserOnboarding(event.data.userId);
    });
  }
);
```

参考 **inngest-steps** 获取更多模式，包括 `step.invoke`。

## 系统事件

Inngest 发送系统事件用于函数生命周期监控：

### 可用系统事件

```typescript
// 函数执行事件
"inngest/function.failed"; // 函数重试后失败
"inngest/function.finished"; // 函数完成 - 成功或失败
"inngest/function.cancelled"; // 函数完成前取消
```

### 处理失败函数

```typescript
const handleFailures = inngest.createFunction(
  { id: "handle-failed-functions", triggers: [{ event: "inngest/function.failed" }] },
  async ({ event, step }) => {
    const { function_id, run_id, error } = event.data;

    await step.run("log-failure", async () => {
      logger.error("Function failed", {
        functionId: function_id,
        runId: run_id,
        error: error.message,
        stack: error.stack
      });
    });

    // 关键函数失败时发送警报
    if (function_id.includes("critical")) {
      await step.run("send-alert", async () => {
        return alerting.sendAlert({
          title: `Critical function failed: ${function_id}`,
          severity: "high",
          runId: run_id
        });
      });
    }

    // 自动重试某些失败
    if (error.code === "RATE_LIMIT_EXCEEDED") {
      await step.run("schedule-retry", async () => {
        return inngest.send({
          name: "retry/function.requested",
          ts: Date.now() + 5 * 60 * 1000, // 5 分钟后重试
          data: { originalRunId: run_id }
        });
      });
    }
  }
);
```

## 发送事件

### 客户端设置

```typescript
// inngest/client.ts
import { Inngest } from "inngest";

export const inngest = new Inngest({
  id: "my-app"
});
// 生产环境中必须设置 INNGEST_EVENT_KEY 环境变量
```

### 单个事件

```typescript
const result = await inngest.send({
  name: "order/placed",
  data: {
    orderId: "ord_123",
    customerId: "cus_456",
    amount: 2500,
    items: [
      { id: "item_1", quantity: 2 },
      { id: "item_2", quantity: 1 }
    ]
  }
});

// 返回用于跟踪的事件 ID
console.log(result.ids); // ["01HQ8PTAESBZPBDS8JTRZZYY3S"]
```

### 批量事件

```typescript
const orderItems = await getOrderItems(orderId);

// 转换为事件
const events = orderItems.map((item) => ({
  name: "inventory/item.reserved",
  data: {
    itemId: item.id,
    orderId: orderId,
    quantity: item.quantity,
    warehouseId: item.warehouseId
  }
}));

// 一次性发送所有事件（最多 512kb）
await inngest.send(events);
```

### 从函数发送

```typescript
inngest.createFunction(
  { id: "process-order", triggers: [{ event: "order/placed" }] },
  async ({ event, step }) => {
    // 在函数中使用 step.sendEvent() 而不是 inngest.send()，以提高可靠性和去重
    await step.sendEvent("trigger-fulfillment", {
      name: "fulfillment/order.received",
      data: {
        orderId: event.data.orderId,
        priority: event.data.customerTier === "premium" ? "high" : "normal"
      }
    });
  }
);
```

## 事件设计最佳实践

### 模式版本控制

```typescript
// 使用版本字段跟踪模式变化
await inngest.send({
  name: "user/profile.updated",
  v: "2024-01-15.1", // 模式版本
  data: {
    userId: "user_123",
    changes: {
      email: "new@example.com",
      preferences: { theme: "dark" }
    },
    // v2 模式中的新字段
    auditInfo: {
      changedBy: "user_456",
      reason: "user_requested"
    }
  }
});
```

### 丰富上下文数据

```typescript
// 包含所有消费者所需的足够上下文
await inngest.send({
  name: "payment/charge.succeeded",
  data: {
    // 主要标识符
    chargeId: "ch_123",
    customerId: "cus_456",

    // 金额详情
    amount: 2500,
    currency: "usd",

    // 不同消费者的上下文
    subscription: {
      id: "sub_789",
      plan: "pro_monthly"
    },
    invoice: {
      id: "inv_012",
      number: "INV-2024-001"
    },

    // 用于调试的元数据
    paymentMethod: {
      type: "card",
      last4: "4242",
      brand: "visa"
    },
    metadata: {
      source: "stripe_webhook",
      environment: "production"
    }
  }
});
```

**事件设计原则：**

1. **自包含：** 包含所有消费者需要的数据
2. **不可变：** 发送后永不修改事件模式
3. **可追溯：** 包含关联 ID 和审计跟踪
4. **可操作：** 提供足够的上下文用于业务逻辑
5. **可调试：** 包含元数据用于故障排除
