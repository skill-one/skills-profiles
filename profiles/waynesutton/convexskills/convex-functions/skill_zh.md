# 凸函数

掌握凸函数，包括查询、变异、操作和 HTTP 端点，并确保具有适当的验证、错误处理和运行时考虑。

## 代码质量

本技能中的所有示例都符合 @convex-dev/eslint-plugin 规则：

- 使用 `handler` 属性的对象语法
- 所有函数上的参数验证器
- 数据库操作中显式的表名

有关代码质量部分的代码检查设置，请参阅 [convex-best-practices](../convex-best-practices/SKILL.md) 中的代码质量部分。

## 文档来源

在实现之前，不要假设；获取最新文档：

- 主要：https://docs.convex.dev/functions
- 查询函数：https://docs.convex.dev/functions/query-functions
- 变异函数：https://docs.convex.dev/functions/mutation-functions
- 操作：https://docs.convex.dev/functions/actions
- HTTP 操作：https://docs.convex.dev/functions/http-actions
- 更广泛的上下文：https://docs.convex.dev/llms.txt

## 说明

### 函数类型概述

| 类型        | 数据库访问          | 外部 API | 缓存       | 用例              |
| ----------- | ------------------------ | ------------- | ------------- | --------------------- |
| 查询       | 只读                | 否            | 是，响应式 | 获取数据         |
| 变异    | 读写               | 否            | 否            | 修改数据        |
| 操作      | 通过 runQuery/runMutation | 是           | 否            | 外部集成         |
| HTTP 操作 | 通过 runQuery/runMutation | 是           | 否            | Webhooks，API        |

### 查询

查询是响应式的、缓存的，并且是只读的：

```typescript
import { query } from "./_generated/server";
import { v } from "convex/values";

export const getUser = query({
  args: { userId: v.id("users") },
  returns: v.union(
    v.object({
      _id: v.id("users"),
      _creationTime: v.number(),
      name: v.string(),
      email: v.string(),
    }),
    v.null(),
  ),
  handler: async (ctx, args) => {
    return await ctx.db.get("users", args.userId);
  },
});

// 带索引的查询
export const listUserTasks = query({
  args: { userId: v.id("users") },
  returns: v.array(
    v.object({
      _id: v.id("tasks"),
      _creationTime: v.number(),
      title: v.string(),
      completed: v.boolean(),
    }),
  ),
  handler: async (ctx, args) => {
    return await ctx.db
      .query("tasks")
      .withIndex("by_user", (q) => q.eq("userId", args.userId))
      .order("desc")
      .collect();
  },
});
```

### 变异

变异修改数据库，并且是事务性的：

```typescript
import { mutation } from "./_generated/server";
import { v } from "convex/values";
import { ConvexError } from "convex/values";

export const createTask = mutation({
  args: {
    title: v.string(),
    userId: v.id("users"),
  },
  returns: v.id("tasks"),
  handler: async (ctx, args) => {
    // 验证用户是否存在
    const user = await ctx.db.get("users", args.userId);
    if (!user) {
      throw new ConvexError("用户未找到");
    }

    return await ctx.db.insert("tasks", {
      title: args.title,
      userId: args.userId,
      completed: false,
      createdAt: Date.now(),
    });
  },
});

export const deleteTask = mutation({
  args: { taskId: v.id("tasks") },
  returns: v.null(),
  handler: async (ctx, args) => {
    await ctx.db.delete("tasks", args.taskId);
    return null;
  },
});
```

### 操作

操作可以调用外部 API，但没有直接访问数据库：

```typescript
"use node";

import { action } from "./_generated/server";
import { v } from "convex/values";
import { api, internal } from "./_generated/api";

export const sendEmail = action({
  args: {
    to: v.string(),
    subject: v.string(),
    body: v.string(),
  },
  returns: v.object({ success: v.boolean() }),
  handler: async (ctx, args) => {
    // 调用外部 API
    const response = await fetch("https://api.email.com/send", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(args),
    });

    return { success: response.ok };
  },
});

// 调用查询和变异的操作
export const processOrder = action({
  args: { orderId: v.id("orders") },
  returns: v.null(),
  handler: async (ctx, args) => {
    // 通过查询读取数据
    const order = await ctx.runQuery(api.orders.get, { orderId: args.orderId });

    if (!order) {
      throw new Error("订单未找到");
    }

    // 调用外部支付 API
    const paymentResult = await processPayment(order);

    // 通过变异更新数据库
    await ctx.runMutation(internal.orders.updateStatus, {
      orderId: args.orderId,
      status: paymentResult.success ? "paid" : "failed",
    });

    return null;
  },
});
```

### HTTP 操作

HTTP 操作处理 webhooks 和外部请求：

```typescript
// convex/http.ts
import { httpRouter } from "convex/server";
import { httpAction } from "./_generated/server";
import { api, internal } from "./_generated/api";

const http = httpRouter();

// Webhook 端点
http.route({
  path: "/webhooks/stripe",
  method: "POST",
  handler: httpAction(async (ctx, request) => {
    const signature = request.headers.get("stripe-signature");
    const body = await request.text();

    // 验证 webhook 签名
    if (!verifyStripeSignature(body, signature)) {
      return new Response("Invalid signature", { status: 401 });
    }

    const event = JSON.parse(body);

    // 处理 webhook
    await ctx.runMutation(internal.payments.handleWebhook, {
      eventType: event.type,
      data: event.data,
    });

    return new Response("OK", { status: 200 });
  }),
});

// API 端点
http.route({
  path: "/api/users/:userId",
  method: "GET",
  handler: httpAction(async (ctx, request) => {
    const url = new URL(request.url);
    const userId = url.pathname.split("/").pop();

    const user = await ctx.runQuery(api.users.get, {
      userId: userId as Id<"users">,
    });

    if (!user) {
      return new Response("Not found", { status: 404 });
    }

    return Response.json(user);
  }),
});

export default http;
```

### 内部函数

使用内部函数进行敏感操作：

```typescript
import {
  internalMutation,
  internalQuery,
  internalAction,
} from "./_generated/server";
import { v } from "convex/values";

// 只能从其他 Convex 函数调用
export const _updateUserCredits = internalMutation({
  args: {
    userId: v.id("users"),
    amount: v.number(),
  },
  returns: v.null(),
  handler: async (ctx, args) => {
    const user = await ctx.db.get("users", args.userId);
    if (!user) return null;

    await ctx.db.patch("users", args.userId, {
      credits: (user.credits || 0) + args.amount,
    });
    return null;
  },
});

// 从操作调用内部函数
export const purchaseCredits = action({
  args: { userId: v.id("users"), amount: v.number() },
  returns: v.null(),
  handler: async (ctx, args) => {
    // 外部处理支付
    await processPayment(args.amount);

    // 通过内部变异更新积分
    await ctx.runMutation(internal.users._updateUserCredits, {
      userId: args.userId,
      amount: args.amount,
    });

    return null;
  },
});
```

### 调度函数

调度函数以稍后运行：

```typescript
import { mutation, internalMutation } from "./_generated/server";
import { v } from "convex/values";
import { internal } from "./_generated/api";

export const scheduleReminder = mutation({
  args: {
    userId: v.id("users"),
    message: v.string(),
    delayMs: v.number(),
  },
  returns: v.id("_scheduled_functions"),
  handler: async (ctx, args) => {
    return await ctx.scheduler.runAfter(
      args.delayMs,
      internal.notifications.sendReminder,
      { userId: args.userId, message: args.message },
    );
  },
});

export const sendReminder = internalMutation({
  args: {
    userId: v.id("users"),
    message: v.string(),
  },
  returns: v.null(),
  handler: async (ctx, args) => {
    await ctx.db.insert("notifications", {
      userId: args.userId,
      message: args.message,
      sentAt: Date.now(),
    });
    return null;
  },
});
```

## 示例

### 完整函数文件

```typescript
// convex/messages.ts
import { query, mutation, internalMutation } from "./_generated/server";
import { v } from "convex/values";
import { ConvexError } from "convex/values";
import { internal } from "./_generated/api";

const messageValidator = v.object({
  _id: v.id("messages"),
  _creationTime: v.number(),
  channelId: v.id("channels"),
  authorId: v.id("users"),
  content: v.string(),
  editedAt: v.optional(v.number()),
});

// 公共查询
export const list = query({
  args: {
    channelId: v.id("channels"),
    limit: v.optional(v.number()),
  },
  returns: v.array(messageValidator),
  handler: async (ctx, args) => {
    const limit = args.limit ?? 50;
    return await ctx.db
      .query("messages")
      .withIndex("by_channel", (q) => q.eq("channelId", args.channelId))
      .order("desc")
      .take(limit);
  },
});

// 公共变异
export const send = mutation({
  args: {
    channelId: v.id("channels"),
    authorId: v.id("users"),
    content: v.string(),
  },
  returns: v.id("messages"),
  handler: async (ctx, args) => {
    if (args.content.trim().length === 0) {
      throw new ConvexError("消息不能为空");
    }

    const messageId = await ctx.db.insert("messages", {
      channelId: args.channelId,
      authorId: args.authorId,
      content: args.content.trim(),
    });

    // 调度通知
    await ctx.scheduler.runAfter(0, internal.messages.notifySubscribers, {
      channelId: args.channelId,
      messageId,
    });

    return messageId;
  },
});

// 内部变异
export const notifySubscribers = internalMutation({
  args: {
    channelId: v.id("channels"),
    messageId: v.id("messages"),
  },
  returns: v.null(),
  handler: async (ctx, args) => {
    // 获取频道订阅者并通知他们
    const subscribers = await ctx.db
      .query("subscriptions")
      .withIndex("by_channel", (q) => q.eq("channelId", args.channelId))
      .collect();

    for (const sub of subscribers) {
      await ctx.db.insert("notifications", {
        userId: sub.userId,
        messageId: args.messageId,
        read: false,
      });
    }
    return null;
  },
});
```

## 最佳实践

- 除非明确指示，否则不要运行 `npx convex deploy`
- 除非明确指示，否则不要运行任何 git 命令
- 始终定义 args 和 returns 验证器
- 使用查询进行读取操作（它们是缓存的和响应式的）
- 使用变异进行写入操作（它们是事务性的）
- 仅在调用外部 API 时使用操作
- 仅对敏感操作使用内部函数
- 在使用 Node.js API 的操作文件顶部添加 `"use node";`
- 使用 ConvexError 处理用户面消息的错误

## 常见陷阱

1. **使用操作进行数据库操作** - 使用查询/变异代替
2. **从查询/变异调用外部 API** - 使用操作
3. **忘记添加 "use node"** - 对于 Node.js API 在操作中是必需的
4. **缺少返回验证器** - 始终指定返回
5. **不使用内部函数进行敏感逻辑** - 使用 internalMutation 保护

## 参考

- Convex 文档：https://docs.convex.dev/
- Convex LLMs.txt：https://docs.convex.dev/llms.txt
- 函数概述：https://docs.convex.dev/functions
- 查询函数：https://docs.convex.dev/functions/query-functions
- 变异函数：https://docs.convex.dev/functions/mutation-functions
- 操作：https://docs.convex.dev/functions/actions
