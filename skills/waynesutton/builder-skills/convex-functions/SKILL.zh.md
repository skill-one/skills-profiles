---
name: convex-functions
description: 以对象形式编写凸查询、变异、操作和内部函数，包含参数和返回验证器、正确的 ctx 使用、运行时边界和错误处理。在添加或修改 convex/*.ts 中导出函数的任何内容时使用，或在决定使用查询、变异还是操作时使用。
---

# 凸函数

`convex/` 中的每个导出函数都使用带有 `args` 和 `returns` 验证器的对象形式。根据处理程序触及的内容选择类型：查询读取、变更写入、动作调用外部。

## 选择函数类型

| 类型 | 数据库 | 外部调用 | 可被调用 | 用于 |
| --- | --- | --- | --- | --- |
| `query` | 读取 | 否 | 客户端、其他函数 | 读取。缓存和响应式。 |
| `mutation` | 读取和写入 | 否 | 客户端、其他函数 | 写入。一个事务。 |
| `action` | 仅通过 `runQuery` 和 `runMutation` | 是 | 客户端、调度器、其他动作 | `fetch`、第三方 SDK、Node API |
| `internalQuery`、`internalMutation`、`internalAction` | 与公共形式相同 | 相同 | 仅其他 Convex 函数 | 定时工作、cron、特权写入 |
| `httpAction` | 仅通过 `runQuery` 和 `runMutation` | 是 | `convex/http.ts` 中的 HTTP 请求 | Webhooks、REST 端点 |

默认选择查询或变更。仅在处理程序必须与 Convex 外部通信时才选择动作。

## 对象形式

在每个函数上声明 `args` 和 `returns`。返回空的函数声明 `returns: v.null()` 并返回 `null`。当多个函数返回相同形状时，提升一个共享的文档验证器。

```typescript
// convex/tasks.ts
import { query, mutation } from "./_generated/server";
import { v } from "convex/values";

const taskValidator = v.object({
  _id: v.id("tasks"),
  _creationTime: v.number(),
  userId: v.id("users"),
  title: v.string(),
  completed: v.boolean(),
});

export const get = query({
  args: { taskId: v.id("tasks") },
  returns: v.union(taskValidator, v.null()),
  handler: async (ctx, args) => {
    return await ctx.db.get(args.taskId);
  },
});

export const remove = mutation({
  args: { taskId: v.id("tasks") },
  returns: v.null(),
  handler: async (ctx, args) => {
    await ctx.db.delete(args.taskId);
    return null;
  },
});
```

## 读取数据

使用 `ctx.db.get(id)` 通过 ID 获取一个文档。对于其他情况，使用 `withIndex` 对 `convex/schema.ts` 中定义的索引进行查询。永远不要在表查询上调用 `.filter()`；它会扫描整个表。

```typescript
export const listByUser = query({
  args: { userId: v.id("users") },
  returns: v.array(taskValidator),
  handler: async (ctx, args) => {
    return await ctx.db
      .query("tasks")
      .withIndex("by_user", (q) => q.eq("userId", args.userId))
      .order("desc")
      .take(50);
  },
});
```

根据您预期的文档数量选择终端方法：

| 方法 | 返回 | 使用时 |
| --- | --- | --- |
| `.unique()` | 一个文档或 null，多于一个时抛出 | 索引保证最多一个匹配 |
| `.first()` | 第一个文档或 null | 您想要最新或最旧的匹配 |
| `.take(n)` | 最多 n 个文档 | 有界的列表，如最近动态 |
| `.collect()` | 每个匹配 | 结果集很小且保持很小 |
| `.paginate(opts)` | 一页加上游标 | 表是无限的 |

分页查询接受 `paginationOpts: paginationOptsValidator`（来自 `convex/server`）作为参数。

## 写入数据

| 方法 | 它做什么 |
| --- | --- |
| `ctx.db.insert("tasks", doc)` | 插入并返回新的 ID |
| `ctx.db.patch(id, fields)` | 浅合并字段。如果文档不存在则抛出 |
| `ctx.db.replace(id, doc)` | 替换整个文档。如果不存在则抛出 |
| `ctx.db.delete(id)` | 删除文档 |

直接补丁，当您不需要旧值时。先读取会扩大写入冲突的窗口。使变更安全可重试。

```typescript
export const rename = mutation({
  args: { taskId: v.id("tasks"), title: v.string() },
  returns: v.null(),
  handler: async (ctx, args) => {
    await ctx.db.patch(args.taskId, { title: args.title });
    return null;
  },
});
```

## 内部函数和引用

`query`、`mutation` 和 `action` 是公共的。任何有部署 URL 的人都可以调用它们。使用 `internalQuery`、`internalMutation` 和 `internalAction` 为仅从其他 Convex 代码运行 的代码：定时工作、cron、webhook 处理程序、特权写入。

通过 `./_generated/api` 中的生成对象引用函数：

- `api.tasks.get` 指向 `convex/tasks.ts` 中的一个公共函数
- `internal.tasks.markPaid` 指向同一文件中的内部函数
- 文件夹映射到路径：`convex/billing/invoices.ts` 给出 `api.billing.invoices.list`

始终安排 `internal.*`。定时函数和 cron 在没有客户端的情况下运行，因此在此处使用公共引用会跳过客户端调用会遇到的认证检查。

```typescript
// convex/messages.ts
import { mutation, internalMutation } from "./_generated/server";
import { internal } from "./_generated/api";
import { v } from "convex/values";

export const send = mutation({
  args: { channelId: v.id("channels"), content: v.string() },
  returns: v.id("messages"),
  handler: async (ctx, args) => {
    const messageId = await ctx.db.insert("messages", args);
    await ctx.scheduler.runAfter(0, internal.messages.notifySubscribers, {
      channelId: args.channelId,
      messageId,
    });
    return messageId;
  },
});

export const notifySubscribers = internalMutation({
  args: { channelId: v.id("channels"), messageId: v.id("messages") },
  returns: v.null(),
  handler: async (ctx, args) => {
    const subs = await ctx.db
      .query("subscriptions")
      .withIndex("by_channel", (q) => q.eq("channelId", args.channelId))
      .collect();
    await Promise.all(
      subs.map((sub) =>
        ctx.db.insert("notifications", {
          userId: sub.userId,
          messageId: args.messageId,
          read: false,
        }),
      ),
    );
    return null;
  },
});
```

## 动作和运行时边界

动作没有 `ctx.db`。它们通过 `ctx.runQuery` 读取，通过 `ctx.runMutation` 写入。每个调用都是自己的事务，因此请保持数量低，并在一个变更内进行相关的读取和写入。

`fetch` 在默认运行时工作。仅在动作需要 Node 内建或 Node 仅 SDK 时，将 `"use node";` 作为文件的第一行。一个 `"use node"` 文件只能导出动作；查询和变更放在一个单独的文件中。

```typescript
// convex/orders.ts (默认运行时)
import { action } from "./_generated/server";
import { internal } from "./_generated/api";
import { v, ConvexError } from "convex/values";
import { Doc } from "./_generated/dataModel";

export const charge = action({
  args: { orderId: v.id("orders") },
  returns: v.null(),
  handler: async (ctx, args) => {
    // 同一文件调用：标注结果，以便 TypeScript 不会遇到循环类型
    const order: Doc<"orders"> | null = await ctx.runQuery(
      internal.orders.getForCharge,
      { orderId: args.orderId },
    );
    if (!order) {
      throw new ConvexError("Order not found");
    }
    const res = await fetch("https://api.payments.example/charge", {
      method: "POST",
      body: JSON.stringify({ amount: order.total }),
    });
    await ctx.runMutation(internal.orders.setStatus, {
      orderId: args.orderId,
      status: res.ok ? "paid" : "failed",
    });
    return null;
  },
});
```

`Doc` 和 `Id` 来自 `./_generated/dataModel`。该注释仅在调用的函数在同一文件中时需要。

## 错误

从 `convex/values` 中抛出 `ConvexError`，以便客户端可以读取任何内容。其 `data` 传递给客户端；在生产中，纯 `Error` 消息会被隐藏。对于预期的缺席（如查找为空的查询），返回 `null`。对于真实失败：未认证、未授权、无效输入，则抛出。

```typescript
import { ConvexError } from "convex/values";

throw new ConvexError({ code: "NOT_FOUND", message: "Task not found" });
```

## 薄包装器

保持处理程序简短。将认证查找、验证和业务逻辑放在首先接受 `ctx` 的普通异步函数中，然后从包装器中调用它们。普通帮助程序是可测试的，并且可以在查询和变更之间共享，而无需 `ctx.runQuery` 跳转。

```typescript
import { QueryCtx, MutationCtx } from "./_generated/server";
import { ConvexError } from "convex/values";

export async function getCurrentUser(ctx: QueryCtx | MutationCtx) {
  const identity = await ctx.auth.getUserIdentity();
  if (!identity) {
    throw new ConvexError("Not authenticated");
  }
  const user = await ctx.db
    .query("users")
    .withIndex("by_token", (q) =>
      q.eq("tokenIdentifier", identity.tokenIdentifier),
    )
    .unique();
  if (!user) {
    throw new ConvexError("User not found");
  }
  return user;
}
```

从查询或变更中直接调用帮助程序。`ctx.runQuery` 和 `ctx.runMutation` 是用于动作和组件边界的。

## 常见错误

| 错误 | 为什么它破坏 | 做替代 |
| --- | --- | --- |
| 没有 `returns` 验证器 | 返回形状漂移，客户端类型撒谎 | 声明 `returns`，使用 `v.null()` 表示无返回 |
| `.filter()` 在表查询上 | 完整表扫描 | 添加索引，使用 `withIndex` |
| `ctx.db` 在动作内 | 动作没有数据库句柄 | `ctx.runQuery` 和 `ctx.runMutation` |
| `fetch` 在查询或变更内 | 事务必须是确定的 | 移动到动作 |
| 安排 `api.*` | 运行公共代码而没有客户端，跳过认证 | 安排 `internal.*` |
| 文件中包含查询的 `"use node"` | 打包器拒绝文件 | 将动作拆分到它们自己的文件 |
| 查询中的 `Date.now()` | 破坏缓存和响应式 | 将时间作为参数传递或存储状态字段 |
| 一个动作中的多个 `runQuery` 调用 | 每个都是独立的事务，出现竞争 | 一个变更来完成相关工作 |
| 用于用户消息的普通 `Error` | 消息在生产中隐藏 | `ConvexError` |
| `ctx.db` 或调度器上缺少 `await` | 写入可能不会提交 | 等待每个 `ctx` 调用 |

## 检查清单

- [ ] 每个导出函数都有对象形式，带有 `args` 和 `returns`
- [ ] 无返回时，`returns: v.null()` 和 `return null`
- [ ] 读取使用 `ctx.db.get(id)` 或 `withIndex`，永远不会 `.filter()`
- [ ] 无限表使用 `.paginate()` 或 `.take(n)`，而不是 `.collect()`
- [ ] 变更直接补丁，并且可以安全重试
- [ ] 定时和 cron 目标是 `internal.*`
- [ ] 动作从不触及 `ctx.db`
- [ ] `"use node"` 仅在导出动作并需要 Node 的文件中
- [ ] 同一文件 `runQuery` 和 `runMutation` 结果有类型注释
- [ ] 客户端可见错误是 `ConvexError`
- [ ] 每个 `ctx.*` 承诺都被等待

## 文档

- https://docs.convex.dev/llms.txt
- https://docs.convex.dev/functions
- https://docs.convex.dev/functions/validation
- https://docs.convex.dev/functions/actions
- https://docs.convex.dev/functions/error-handling
