# 凸形迁移

安全地进化您的 Convex 数据库模式，添加字段、回填数据、移除已弃用的字段以及维护零停机部署的模式。

## 文档来源

在实施之前，不要假设；获取最新文档：

- 主要：https://docs.convex.dev/database/schemas
- 模式概述：https://docs.convex.dev/database
- 迁移模式：https://stack.convex.dev/migrate-data-postgres-to-convex
- 更广泛的背景：https://docs.convex.dev/llms.txt

## 说明

### 迁移理念

Convex 处理模式进化与传统数据库不同：

- 无需显式迁移文件或命令
- 模式变更使用 `npx convex dev` 立即部署
- 现有数据不会自动转换
- 使用可选字段和回填突变进行安全迁移

### 添加新字段

从可选字段开始，然后回填：

```typescript
// 第 1 步：向模式添加可选字段
// convex/schema.ts
import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  users: defineTable({
    name: v.string(),
    email: v.string(),
    // 新字段 - 开始为可选
    avatarUrl: v.optional(v.string()),
  }),
});
```

```typescript
// 第 2 步：更新代码以处理两种情况
// convex/users.ts
import { query } from "./_generated/server";
import { v } from "convex/values";

export const getUser = query({
  args: { userId: v.id("users") },
  returns: v.union(
    v.object({
      _id: v.id("users"),
      name: v.string(),
      email: v.string(),
      avatarUrl: v.union(v.string(), v.null()),
    }),
    v.null()
  ),
  handler: async (ctx, args) => {
    const user = await ctx.db.get(args.userId);
    if (!user) return null;

    return {
      _id: user._id,
      name: user.name,
      email: user.email,
      // 优雅地处理缺失字段
      avatarUrl: user.avatarUrl ?? null,
    };
  },
});
```

```typescript
// 第 3 步：回填现有文档
// convex/migrations.ts
import { internalMutation } from "./_generated/server";
import { internal } from "./_generated/api";
import { v } from "convex/values";

const BATCH_SIZE = 100;

export const backfillAvatarUrl = internalMutation({
  args: {
    cursor: v.optional(v.string()),
  },
  returns: v.object({
    processed: v.number(),
    hasMore: v.boolean(),
  }),
  handler: async (ctx, args) => {
    const result = await ctx.db
      .query("users")
      .paginate({ numItems: BATCH_SIZE, cursor: args.cursor ?? null });

    let processed = 0;
    for (const user of result.page) {
      // 仅在字段缺失时更新
      if (user.avatarUrl === undefined) {
        await ctx.db.patch(user._id, {
          avatarUrl: generateDefaultAvatar(user.name),
        });
        processed++;
      }
    }

    // 如果需要，安排下一批
    if (!result.isDone) {
      await ctx.scheduler.runAfter(0, internal.migrations.backfillAvatarUrl, {
        cursor: result.continueCursor,
      });
    }

    return {
      processed,
      hasMore: !result.isDone,
    };
  },
});

function generateDefaultAvatar(name: string): string {
  return `https://api.dicebear.com/7.x/initials/svg?seed=${encodeURIComponent(name)}`;
}
```

```typescript
// 第 4 步：回填完成后，将字段设为必需
// convex/schema.ts
export default defineSchema({
  users: defineTable({
    name: v.string(),
    email: v.string(),
    avatarUrl: v.string(), // 现在为必需
  }),
});
```

### 移除字段

在从模式中移除字段之前停止使用字段：

```typescript
// 第 1 步：在查询和突变中停止使用字段
// 在代码注释中标记为已弃用

// 第 2 步：从模式中移除字段（如果需要，先将其设为可选）
// convex/schema.ts
export default defineSchema({
  posts: defineTable({
    title: v.string(),
    content: v.string(),
    authorId: v.id("users"),
    // legacyField: v.optional(v.string()), // 移除此行
  }),
});

// 第 3 步：可选地清理现有数据
// convex/migrations.ts
export const removeDeprecatedField = internalMutation({
  args: {
    cursor: v.optional(v.string()),
  },
  returns: v.null(),
  handler: async (ctx, args) => {
    const result = await ctx.db
      .query("posts")
      .paginate({ numItems: 100, cursor: args.cursor ?? null });

    for (const post of result.page) {
      // 使用 replace 完全移除字段
      const { legacyField, ...rest } = post as typeof post & { legacyField?: string };
      if (legacyField !== undefined) {
        await ctx.db.replace(post._id, rest);
      }
    }

    if (!result.isDone) {
      await ctx.scheduler.runAfter(0, internal.migrations.removeDeprecatedField, {
        cursor: result.continueCursor,
      });
    }

    return null;
  },
});
```

### 重命名字段

重命名需要将数据复制到新字段，然后移除旧字段：

```typescript
// 第 1 步：将新字段设为可选
// convex/schema.ts
export default defineSchema({
  users: defineTable({
    userName: v.string(), // 旧字段
    displayName: v.optional(v.string()), // 新字段
  }),
});

// 第 2 步：更新代码以从新字段读取，带回退
export const getUser = query({
  args: { userId: v.id("users") },
  returns: v.object({
    _id: v.id("users"),
    displayName: v.string(),
  }),
  handler: async (ctx, args) => {
    const user = await ctx.db.get(args.userId);
    if (!user) throw new Error("User not found");

    return {
      _id: user._id,
      // 从新字段读取，回退到旧字段
      displayName: user.displayName ?? user.userName,
    };
  },
});

// 第 3 步：回填以复制数据
export const backfillDisplayName = internalMutation({
  args: { cursor: v.optional(v.string()) },
  returns: v.null(),
  handler: async (ctx, args) => {
    const result = await ctx.db
      .query("users")
      .paginate({ numItems: 100, cursor: args.cursor ?? null });

    for (const user of result.page) {
      if (user.displayName === undefined) {
        await ctx.db.patch(user._id, {
          displayName: user.userName,
        });
      }
    }

    if (!result.isDone) {
      await ctx.scheduler.runAfter(0, internal.migrations.backfillDisplayName, {
        cursor: result.continueCursor,
      });
    }

    return null;
  },
});

// 第 4 步：回填完成后，更新模式将新字段设为必需
// 并移除旧字段
export default defineSchema({
  users: defineTable({
    // userName 移除
    displayName: v.string(),
  }),
});
```

### 添加索引

在查询中使用它们之前添加索引：

```typescript
// 第 1 步：向模式添加索引
// convex/schema.ts
export default defineSchema({
  posts: defineTable({
    title: v.string(),
    authorId: v.id("users"),
    publishedAt: v.optional(v.number()),
    status: v.string(),
  })
    .index("by_author", ["authorId"])
    // 新索引
    .index("by_status_and_published", ["status", "publishedAt"]),
});

// 第 2 步：部署模式变更
// 运行：npx convex dev

// 第 3 步：现在在查询中使用索引
export const getPublishedPosts = query({
  args: {},
  returns: v.array(v.object({
    _id: v.id("posts"),
    title: v.string(),
    publishedAt: v.number(),
  })),
  handler: async (ctx) => {
    const posts = await ctx.db
      .query("posts")
      .withIndex("by_status_and_published", (q) =>
        q.eq("status", "published")
      )
      .order("desc")
      .take(10);

    return posts
      .filter((p) => p.publishedAt !== undefined)
      .map((p) => ({
        _id: p._id,
        title: p.title,
        publishedAt: p.publishedAt!,
      }));
  },
});
```

### 更改字段类型

类型变更需要谨慎迁移：

```typescript
// 示例：将 "priority" 字段从 string 改为 number

// 第 1 步：添加新字段与新类型
// convex/schema.ts
export default defineSchema({
  tasks: defineTable({
    title: v.string(),
    priority: v.string(), // 旧： "low", "medium", "high"
    priorityLevel: v.optional(v.number()), // 新： 1, 2, 3
  }),
});

// 第 2 步：回填类型转换
export const migratePriorityToNumber = internalMutation({
  args: { cursor: v.optional(v.string()) },
  returns: v.null(),
  handler: async (ctx, args) => {
    const result = await ctx.db
      .query("tasks")
      .paginate({ numItems: 100, cursor: args.cursor ?? null });

    const priorityMap: Record<string, number> = {
      low: 1,
      medium: 2,
      high: 3,
    };

    for (const task of result.page) {
      if (task.priorityLevel === undefined) {
        await ctx.db.patch(task._id, {
          priorityLevel: priorityMap[task.priority] ?? 1,
        });
      }
    }

    if (!result.isDone) {
      await ctx.scheduler.runAfter(0, internal.migrations.migratePriorityToNumber, {
        cursor: result.continueCursor,
      });
    }

    return null;
  },
});

// 第 3 步：更新代码使用新字段
export const getTask = query({
  args: { taskId: v.id("tasks") },
  returns: v.object({
    _id: v.id("tasks"),
    title: v.string(),
    priorityLevel: v.number(),
  }),
  handler: async (ctx, args) => {
    const task = await ctx.db.get(args.taskId);
    if (!task) throw new Error("Task not found");

    const priorityMap: Record<string, number> = {
      low: 1,
      medium: 2,
      high: 3,
    };

    return {
      _id: task._id,
      title: task.title,
      priorityLevel: task.priorityLevel ?? priorityMap[task.priority] ?? 1,
    };
  },
});

// 第 4 步：回填完成后，更新模式
export default defineSchema({
  tasks: defineTable({
    title: v.string(),
    // priority 字段移除
    priorityLevel: v.number(),
  }),
});
```

### 迁移运行器模式

创建可重用的迁移系统：

```typescript
// convex/schema.ts
import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  migrations: defineTable({
    name: v.string(),
    startedAt: v.number(),
    completedAt: v.optional(v.number()),
    status: v.union(
      v.literal("running"),
      v.literal("completed"),
      v.literal("failed")
    ),
    error: v.optional(v.string()),
    processed: v.number(),
  }).index("by_name", ["name"]),

  // 您的其他表...
});
```

```typescript
// convex/migrations.ts
import { internalMutation, internalQuery } from "./_generated/server";
import { internal } from "./_generated/api";
import { v } from "convex/values";

// 检查是否已运行迁移
export const hasMigrationRun = internalQuery({
  args: { name: v.string() },
  returns: v.boolean(),
  handler: async (ctx, args) => {
    const migration = await ctx.db
      .query("migrations")
      .withIndex("by_name", (q) => q.eq("name", args.name))
      .first();
    return migration?.status === "completed";
  },
});

// 开始迁移
export const startMigration = internalMutation({
  args: { name: v.string() },
  returns: v.id("migrations"),
  handler: async (ctx, args) => {
    // 检查是否已存在
    const existing = await ctx.db
      .query("migrations")
      .withIndex("by_name", (q) => q.eq("name", args.name))
      .first();

    if (existing) {
      if (existing.status === "completed") {
        throw new Error(`Migration ${args.name} already completed`);
      }
      if (existing.status === "running") {
        throw new Error(`Migration ${args.name} already running`);
      }
      // 重置失败的迁移
      await ctx.db.patch(existing._id, {
        status: "running",
        startedAt: Date.now(),
        error: undefined,
        processed: 0,
      });
      return existing._id;
    }

    return await ctx.db.insert("migrations", {
      name: args.name,
      startedAt: Date.now(),
      status: "running",
      processed: 0,
    });
  },
});

// 更新迁移进度
export const updateMigrationProgress = internalMutation({
  args: {
    migrationId: v.id("migrations"),
    processed: v.number(),
  },
  returns: v.null(),
  handler: async (ctx, args) => {
    const migration = await ctx.db.get(args.migrationId);
    if (!migration) return null;

    await ctx.db.patch(args.migrationId, {
      processed: migration.processed + args.processed,
    });

    return null;
  },
});

// 完成迁移
export const completeMigration = internalMutation({
  args: { migrationId: v.id("migrations") },
  returns: v.null(),
  handler: async (ctx, args) => {
    await ctx.db.patch(args.migrationId, {
      status: "completed",
      completedAt: Date.now(),
    });
    return null;
  },
});

// 失败迁移
export const failMigration = internalMutation({
  args: {
    migrationId: v.id("migrations"),
    error: v.string(),
  },
  returns: v.null(),
  handler: async (ctx, args) => {
    await ctx.db.patch(args.migrationId, {
      status: "failed",
      error: args.error,
    });
    return null;
  },
});
```

```typescript
// convex/migrations/addUserTimestamps.ts
import { internalMutation } from "../_generated/server";
import { internal } from "../_generated/api";
import { v } from "convex/values";

const MIGRATION_NAME = "add_user_timestamps_v1";
const BATCH_SIZE = 100;

export const run = internalMutation({
  args: {
    migrationId: v.optional(v.id("migrations")),
    cursor: v.optional(v.string()),
  },
  returns: v.null(),
  handler: async (ctx, args) => {
    // 首次运行时初始化迁移
    let migrationId = args.migrationId;
    if (!migrationId) {
      const hasRun = await ctx.runQuery(internal.migrations.hasMigrationRun, {
        name: MIGRATION_NAME,
      });
      if (hasRun) {
        console.log(`Migration ${MIGRATION_NAME} already completed`);
        return null;
      }
      migrationId = await ctx.runMutation(internal.migrations.startMigration, {
        name: MIGRATION_NAME,
      });
    }

    try {
      const result = await ctx.db
        .query("users")
        .paginate({ numItems: BATCH_SIZE, cursor: args.cursor ?? null });

      let processed = 0;
      for (const user of result.page) {
        if (user.createdAt === undefined) {
          await ctx.db.patch(user._id, {
            createdAt: user._creationTime,
            updatedAt: user._creationTime,
          });
          processed++;
        }
      }

      // 更新进度
      await ctx.runMutation(internal.migrations.updateMigrationProgress, {
        migrationId,
        processed,
      });

      // 继续 或 完成
      if (!result.isDone) {
        await ctx.scheduler.runAfter(0, internal.migrations.addUserTimestamps.run, {
          migrationId,
          cursor: result.continueCursor,
        });
      } else {
        await ctx.runMutation(internal.migrations.completeMigration, {
          migrationId,
        });
        console.log(`Migration ${MIGRATION_NAME} completed`);
      }
    } catch (error) {
      await ctx.runMutation(internal.migrations.failMigration, {
        migrationId,
        error: String(error),
      });
      throw error;
    }

    return null;
  },
});
```

## 示例

### 支持迁移的模式

```typescript
// convex/schema.ts
import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  // 迁移跟踪
  migrations: defineTable({
    name: v.string(),
    startedAt: v.number(),
    completedAt: v.optional(v.number()),
    status: v.union(
      v.literal("running"),
      v.literal("completed"),
      v.literal("failed")
    ),
    error: v.optional(v.string()),
    processed: v.number(),
  }).index("by_name", ["name"]),

  // 用户表带进化模式
  users: defineTable({
    // 原始字段
    name: v.string(),
    email: v.string(),
    
    // 迁移 v1 添加
    createdAt: v.optional(v.number()),
    updatedAt: v.optional(v.number()),
    
    // 迁移 v2 添加
    avatarUrl: v.optional(v.string()),
    
    // 迁移 v3 添加
    settings: v.optional(v.object({
      theme: v.string(),
      notifications: v.boolean(),
    })),
  })
    .index("by_email", ["email"])
    .index("by_createdAt", ["createdAt"]),

  // 帖子表带常见查询的索引
  posts: defineTable({
    title: v.string(),
    content: v.string(),
    authorId: v.id("users"),
    status: v.union(
      v.literal("draft"),
      v.literal("published"),
      v.literal("archived")
    ),
    publishedAt: v.optional(v.number()),
    createdAt: v.number(),
    updatedAt: v.number(),
  })
    .index("by_author", ["authorId"])
    .index("by_status", ["status"])
    .index("by_author_and_status", ["authorId", "status"])
    .index("by_publishedAt", ["publishedAt"]),
});
```

## 最佳实践

- 除非明确指示，否则不要运行 `npx convex deploy`
- 除非明确指示，否则不要运行任何 git 命令
- 添加新数据时始终从可选字段开始
- 分批回填数据以避免超时
- 在生产之前在开发环境中测试迁移
- 跟踪已完成的迁移以避免重新运行
- 在过渡期间更新代码以处理旧数据和新数据
- 仅在所有代码停止使用后移除已弃用的字段
- 对大数据集使用分页
- 在运行新字段的查询之前添加适当的索引

## 常见陷阱

1. **立即将新字段设为必需** - 破坏现有文档
2. **不处理未定义值** - 导致运行时错误
3. **大批量** - 导致函数超时
4. **忘记更新索引** - 查询失败或性能差
5. **未跟踪就运行迁移** - 可能多次运行
6. **在代码更新前移除字段** - 破坏现有功能
7. **不在开发环境中测试** - 生产数据问题

## 参考

- Convex 文档：https://docs.convex.dev/
- Convex LLMs.txt：https://docs.convex.dev/llms.txt
- 模式：https://docs.convex.dev/database/schemas
- 数据库概述：https://docs.convex.dev/database
- 迁移模式：https://stack.convex.dev/migrate-data-postgres-to-convex
