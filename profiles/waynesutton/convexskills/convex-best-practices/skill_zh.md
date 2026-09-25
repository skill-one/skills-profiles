# 凸函数最佳实践

遵循已建立的函数组织、查询优化、验证、TypeScript 使用和错误处理模式，构建生产就绪的凸函数应用程序。

## 代码质量

本技能中的所有模式均符合 `@convex-dev/eslint-plugin`。安装它以进行构建时验证：

```bash
npm i @convex-dev/eslint-plugin --save-dev
```

```js
// eslint.config.js
import { defineConfig } from "eslint/config";
import convexPlugin from "@convex-dev/eslint-plugin";

export default defineConfig([
  ...convexPlugin.configs.recommended,
]);
```

该插件强制执行四条规则：

| 规则                                | 它强制执行的内容                  |
| ----------------------------------- | --------------------------------- |
| `no-old-registered-function-syntax` | 使用 `handler` 的对象语法      |
| `require-argument-validators`       | 所有函数上的 `args: {}`       |
| `explicit-table-ids`                | 数据库操作中的表名             |
| `import-wrong-runtime`              | 凸函数运行时中不要 Node 导入 |

文档：https://docs.convex.dev/eslint

## 文档来源

在实现之前，不要假设；获取最新文档：

- 主要：https://docs.convex.dev/understanding/best-practices/
- 错误处理：https://docs.convex.dev/functions/error-handling
- 写入冲突：https://docs.convex.dev/error#1
- 更广泛的背景：https://docs.convex.dev/llms.txt

## 说明

### 凸函数的禅意

1. **凸函数管理难题** - 让凸函数处理缓存、实时同步和一致性**
2. **函数是 API** - 将你的函数设计为应用程序的接口**
3. **模式是真理** - 在 schema.ts 中显式定义你的数据模型**
4. **到处使用 TypeScript** - 利用端到端类型安全**
5. **查询是响应式的** - 用订阅而不是请求来思考**

### 函数组织

按领域组织你的凸函数：

```typescript
// convex/users.ts - 与用户相关的函数
import { query, mutation } from "./_generated/server";
import { v } from "convex/values";

export const get = query({
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
```

### 参数和返回验证

始终为参数和返回类型定义验证器：

```typescript
export const createTask = mutation({
  args: {
    title: v.string(),
    description: v.optional(v.string()),
    priority: v.union(v.literal("low"), v.literal("medium"), v.literal("high")),
  },
  returns: v.id("tasks"),
  handler: async (ctx, args) => {
    return await ctx.db.insert("tasks", {
      title: args.title,
      description: args.description,
      priority: args.priority,
      completed: false,
      createdAt: Date.now(),
    });
  },
});
```

### 查询模式

使用索引而不是过滤器进行高效查询：

```typescript
// 模式中的索引
export default defineSchema({
  tasks: defineTable({
    userId: v.id("users"),
    status: v.string(),
    createdAt: v.number(),
  })
    .index("by_user", ["userId"])
    .index("by_user_and_status", ["userId", "status"]),
});

// 使用索引的查询
export const getTasksByUser = query({
  args: { userId: v.id("users") },
  returns: v.array(
    v.object({
      _id: v.id("tasks"),
      _creationTime: v.number(),
      userId: v.id("users"),
      status: v.string(),
      createdAt: v.number(),
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

### 错误处理

使用 ConvexError 进行用户面错误：

```typescript
import { ConvexError } from "convex/values";

export const updateTask = mutation({
  args: {
    taskId: v.id("tasks"),
    title: v.string(),
  },
  returns: v.null(),
  handler: async (ctx, args) => {
    const task = await ctx.db.get("tasks", args.taskId);

    if (!task) {
      throw new ConvexError({
        code: "NOT_FOUND",
        message: "Task not found",
      });
    }

    await ctx.db.patch("tasks", args.taskId, { title: args.title });
    return null;
  },
});
```

### 避免写入冲突（乐观并发控制）

凸函数使用 OCC。遵循这些模式以最大程度地减少冲突：

```typescript
// 良好：使突变幂等
export const completeTask = mutation({
  args: { taskId: v.id("tasks") },
  returns: v.null(),
  handler: async (ctx, args) => {
    const task = await ctx.db.get("tasks", args.taskId);

    // 如果已经完成，则提前返回（幂等）
    if (!task || task.status === "completed") {
      return null;
    }

    await ctx.db.patch("tasks", args.taskId, {
      status: "completed",
      completedAt: Date.now(),
    });
    return null;
  },
});

// 良好：在可能的情况下直接修补，而无需先读取
export const updateNote = mutation({
  args: { id: v.id("notes"), content: v.string() },
  returns: v.null(),
  handler: async (ctx, args) => {
    // 直接修补 - ctx.db.patch 如果文档不存在会抛出错误
    await ctx.db.patch("notes", args.id, { content: args.content });
    return null;
  },
});

// 良好：使用 Promise.all 进行并行独立更新
export const reorderItems = mutation({
  args: { itemIds: v.array(v.id("items")) },
  returns: v.null(),
  handler: async (ctx, args) => {
    const updates = args.itemIds.map((id, index) =>
      ctx.db.patch("items", id, { order: index }),
    );
    await Promise.all(updates);
    return null;
  },
});
```

### TypeScript 最佳实践

```typescript
import { Id, Doc } from "./_generated/dataModel";

// 使用 Id 类型进行文档引用
type UserId = Id<"users">;

// 使用 Doc 类型进行完整文档
type User = Doc<"users">;

// 正确定义 Record 类型
const userScores: Record<Id<"users">, number> = {};
```

### 内部函数与公共函数

```typescript
// 公共函数 - 暴露给客户端
export const getUser = query({
  args: { userId: v.id("users") },
  returns: v.union(
    v.null(),
    v.object({
      /* ... */
    }),
  ),
  handler: async (ctx, args) => {
    // ...
  },
});

// 内部函数 - 仅可从其他凸函数调用
export const _updateUserStats = internalMutation({
  args: { userId: v.id("users") },
  returns: v.null(),
  handler: async (ctx, args) => {
    // ...
  },
});
```

## 示例

### 完整的 CRUD 模式

```typescript
// convex/tasks.ts
import { query, mutation } from "./_generated/server";
import { v } from "convex/values";
import { ConvexError } from "convex/values";

const taskValidator = v.object({
  _id: v.id("tasks"),
  _creationTime: v.number(),
  title: v.string(),
  completed: v.boolean(),
  userId: v.id("users"),
});

export const list = query({
  args: { userId: v.id("users") },
  returns: v.array(taskValidator),
  handler: async (ctx, args) => {
    return await ctx.db
      .query("tasks")
      .withIndex("by_user", (q) => q.eq("userId", args.userId))
      .collect();
  },
});

export const create = mutation({
  args: {
    title: v.string(),
    userId: v.id("users"),
  },
  returns: v.id("tasks"),
  handler: async (ctx, args) => {
    return await ctx.db.insert("tasks", {
      title: args.title,
      completed: false,
      userId: args.userId,
    });
  },
});

export const update = mutation({
  args: {
    taskId: v.id("tasks"),
    title: v.optional(v.string()),
    completed: v.optional(v.boolean()),
  },
  returns: v.null(),
  handler: async (ctx, args) => {
    const { taskId, ...updates } = args;

    // 移除未定义的值
    const cleanUpdates = Object.fromEntries(
      Object.entries(updates).filter(([_, v]) => v !== undefined),
    );

    if (Object.keys(cleanUpdates).length > 0) {
      await ctx.db.patch("tasks", taskId, cleanUpdates);
    }
    return null;
  },
});

export const remove = mutation({
  args: { taskId: v.id("tasks") },
  returns: v.null(),
  handler: async (ctx, args) => {
    await ctx.db.delete("tasks", args.taskId);
    return null;
  },
});
```

## 最佳实践

- 除非明确指示，否则永远不要运行 `npx convex deploy`
- 除非明确指示，否则永远不要运行任何 git 命令
- 始终为函数定义返回验证器
- 对所有过滤数据的查询使用索引
- 使突变幂等以优雅地处理重试
- 使用 ConvexError 进行用户面错误消息
- 按领域组织函数（users.ts、tasks.ts 等）
- 使用内部函数进行敏感操作
- 利用 TypeScript 的 Id 和 Doc 类型

## 常见陷阱

1. **使用 filter 而不是 withIndex** - 始终定义索引并使用 withIndex
2. **缺少返回验证器** - 始终指定 returns 字段
3. **非幂等突变** - 更新前检查当前状态
4. **不必要地读取后再修补** - 在可能的情况下直接修补
5. **不处理 null 返回** - 文档 ID 可能不存在

## 参考

- 凸函数文档：https://docs.convex.dev/
- 凸函数 LLMs.txt：https://docs.convex.dev/llms.txt
- 最佳实践：https://docs.convex.dev/understanding/best-practices/
- 错误处理：https://docs.convex.dev/functions/error-handling
- 写入冲突：https://docs.convex.dev/error#1
