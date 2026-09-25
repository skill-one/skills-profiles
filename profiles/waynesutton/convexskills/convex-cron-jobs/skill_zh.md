# 凸显定时任务

为凸显应用程序中的后台任务、清理任务、数据同步和自动化工作流安排周期性函数。

## 文档来源

在实施之前，不要假设；获取最新文档：

- 主要：https://docs.convex.dev/scheduling/cron-jobs
- 调度概述：https://docs.convex.dev/scheduling
- 定时函数：https://docs.convex.dev/scheduling/scheduled-functions
- 获取更广泛的背景：https://docs.convex.dev/llms.txt

## 说明

### 定时任务概述

凸显定时任务允许您安排函数在固定间隔或特定时间运行。主要功能：

- 在固定时间运行函数
- 支持基于间隔和cron表达式的时间调度
- 失败时自动重试
- 通过凸显控制面板进行监控

### 基本定时任务设置

```typescript
// convex/crons.ts
import { cronJobs } from "convex/server";
import { internal } from "./_generated/api";

const crons = cronJobs();

// 每小时运行一次
crons.interval(
  "清理过期会话",
  { hours: 1 },
  internal.tasks.cleanupExpiredSessions,
  {}
);

// 每天午夜UTC时间运行一次
crons.cron(
  "每日报告",
  "0 0 * * *",
  internal.reports.generateDailyReport,
  {}
);

export default crons;
```

### 基于间隔的调度

使用 `crons.interval` 进行简单的周期性任务：

```typescript
// convex/crons.ts
import { cronJobs } from "convex/server";
import { internal } from "./_generated/api";

const crons = cronJobs();

// 每5分钟
crons.interval(
  "同步外部数据",
  { minutes: 5 },
  internal.sync.fetchExternalData,
  {}
);

// 每2小时
crons.interval(
  "清理临时文件",
  { hours: 2 },
  internal.files.cleanupTempFiles,
  {}
);

// 每30秒（最小间隔）
crons.interval(
  "健康检查",
  { seconds: 30 },
  internal.monitoring.healthCheck,
  {}
);

export default crons;
```

### Cron表达式调度

使用 `crons.cron` 进行精确的cron表达式调度：

```typescript
// convex/crons.ts
import { cronJobs } from "convex/server";
import { internal } from "./_generated/api";

const crons = cronJobs();

// 每天上午9点UTC时间
crons.cron(
  "早晨通知",
  "0 9 * * *",
  internal.notifications.sendMorningDigest,
  {}
);

// 每周一上午8点UTC时间
crons.cron(
  "每周总结",
  "0 8 * * 1",
  internal.reports.generateWeeklySummary,
  {}
);

// 每月第一天午夜
crons.cron(
  "月度账单",
  "0 0 1 * *",
  internal.billing.processMonthlyBilling,
  {}
);

// 每15分钟
crons.cron(
  "频繁同步",
  "*/15 * * * *",
  internal.sync.syncData,
  {}
);

export default crons;
```

### Cron表达式参考

```
┌───────────── 分钟 (0-59)
│ ┌───────────── 小时 (0-23)
│ │ ┌───────────── 月内日期 (1-31)
│ │ │ ┌───────────── 月份 (1-12)
│ │ │ │ ┌───────────── 周内日期 (0-6, 星期日=0)
│ │ │ │ │
* * * * *
```

常见模式：

- `* * * * *` - 每分钟
- `0 * * * *` - 每小时
- `0 0 * * *` - 每天午夜
- `0 0 * * 0` - 每周日午夜
- `0 0 1 * *` - 每月第一天
- `*/5 * * * *` - 每5分钟
- `0 9-17 * * 1-5` - 每小时从上午9点到下午5点，周一至周五

### 用于定时任务的内部函数

定时任务应调用内部函数以确保安全：

```typescript
// convex/tasks.ts
import { internalMutation, internalQuery } from "./_generated/server";
import { v } from "convex/values";

// 清理过期会话
export const cleanupExpiredSessions = internalMutation({
  args: {},
  returns: v.number(),
  handler: async (ctx) => {
    const oneHourAgo = Date.now() - 60 * 60 * 1000;
    
    const expiredSessions = await ctx.db
      .query("sessions")
      .withIndex("by_lastActive")
      .filter((q) => q.lt(q.field("lastActive"), oneHourAgo))
      .collect();

    for (const session of expiredSessions) {
      await ctx.db.delete(session._id);
    }

    return expiredSessions.length;
  },
});

// 处理挂起任务
export const processPendingTasks = internalMutation({
  args: {},
  returns: v.null(),
  handler: async (ctx) => {
    const pendingTasks = await ctx.db
      .query("tasks")
      .withIndex("by_status", (q) => q.eq("status", "pending"))
      .take(100);

    for (const task of pendingTasks) {
      await ctx.db.patch(task._id, {
        status: "processing",
        startedAt: Date.now(),
      });
      
      // 安排实际处理
      await ctx.scheduler.runAfter(0, internal.tasks.processTask, {
        taskId: task._id,
      });
    }

    return null;
  },
});
```

### 带参数的定时任务

向定时任务传递静态参数：

```typescript
// convex/crons.ts
import { cronJobs } from "convex/server";
import { internal } from "./_generated/api";

const crons = cronJobs();

// 不同的清理间隔用于不同类型
crons.interval(
  "清理临时文件",
  { hours: 1 },
  internal.cleanup.cleanupByType,
  { fileType: "temp", maxAge: 3600000 }
);

crons.interval(
  "清理缓存文件",
  { hours: 24 },
  internal.cleanup.cleanupByType,
  { fileType: "cache", maxAge: 86400000 }
);

export default crons;
```

```typescript
// convex/cleanup.ts
import { internalMutation } from "./_generated/server";
import { v } from "convex/values";

export const cleanupByType = internalMutation({
  args: {
    fileType: v.string(),
    maxAge: v.number(),
  },
  returns: v.number(),
  handler: async (ctx, args) => {
    const cutoff = Date.now() - args.maxAge;
    
    const oldFiles = await ctx.db
      .query("files")
      .withIndex("by_type_and_created", (q) => 
        q.eq("type", args.fileType).lt("createdAt", cutoff)
      )
      .collect();

    for (const file of oldFiles) {
      await ctx.storage.delete(file.storageId);
      await ctx.db.delete(file._id);
    }

    return oldFiles.length;
  },
});
```

### 监控和日志记录

添加日志以跟踪定时任务执行：

```typescript
// convex/tasks.ts
import { internalMutation } from "./_generated/server";
import { v } from "convex/values";

export const cleanupWithLogging = internalMutation({
  args: {},
  returns: v.null(),
  handler: async (ctx) => {
    const startTime = Date.now();
    let processedCount = 0;
    let errorCount = 0;

    try {
      const expiredItems = await ctx.db
        .query("items")
        .withIndex("by_expiresAt")
        .filter((q) => q.lt(q.field("expiresAt"), Date.now()))
        .collect();

      for (const item of expiredItems) {
        try {
          await ctx.db.delete(item._id);
          processedCount++;
        } catch (error) {
          errorCount++;
          console.error(`Failed to delete item ${item._id}:`, error);
        }
      }

      // 记录任务完成
      await ctx.db.insert("cronLogs", {
        jobName: "cleanup",
        startTime,
        endTime: Date.now(),
        duration: Date.now() - startTime,
        processedCount,
        errorCount,
        status: errorCount === 0 ? "success" : "partial",
      });
    } catch (error) {
      // 记录任务失败
      await ctx.db.insert("cronLogs", {
        jobName: "cleanup",
        startTime,
        endTime: Date.now(),
        duration: Date.now() - startTime,
        processedCount,
        errorCount,
        status: "failed",
        error: String(error),
      });
      throw error;
    }

    return null;
  },
});
```

### 批处理用于大型数据集

分批处理大型数据集以避免超时：

```typescript
// convex/tasks.ts
import { internalMutation } from "./_generated/server";
import { internal } from "./_generated/api";
import { v } from "convex/values";

const BATCH_SIZE = 100;

export const processBatch = internalMutation({
  args: {
    cursor: v.optional(v.string()),
  },
  returns: v.null(),
  handler: async (ctx, args) => {
    const result = await ctx.db
      .query("items")
      .withIndex("by_status", (q) => q.eq("status", "pending"))
      .paginate({ numItems: BATCH_SIZE, cursor: args.cursor ?? null });

    for (const item of result.page) {
      await ctx.db.patch(item._id, {
        status: "processed",
        processedAt: Date.now(),
      });
    }

    // 如果还有更多项，安排下一个批次
    if (!result.isDone) {
      await ctx.scheduler.runAfter(0, internal.tasks.processBatch, {
        cursor: result.continueCursor,
      });
    }

    return null;
  },
});
```

### 定时任务中的外部API调用

使用操作进行外部API调用：

```typescript
// convex/sync.ts
"use node";

import { internalAction } from "./_generated/server";
import { internal } from "./_generated/api";
import { v } from "convex/values";

export const syncExternalData = internalAction({
  args: {},
  returns: v.null(),
  handler: async (ctx) => {
    // 从外部API获取数据
    const response = await fetch("https://api.example.com/data", {
      headers: {
        Authorization: `Bearer ${process.env.API_KEY}`,
      },
    });

    if (!response.ok) {
      throw new Error(`API请求失败: ${response.status}`);
    }

    const data = await response.json();

    // 使用突变存储数据
    await ctx.runMutation(internal.sync.storeExternalData, {
      data,
      syncedAt: Date.now(),
    });

    return null;
  },
});

export const storeExternalData = internalMutation({
  args: {
    data: v.any(),
    syncedAt: v.number(),
  },
  returns: v.null(),
  handler: async (ctx, args) => {
    await ctx.db.insert("externalData", {
      data: args.data,
      syncedAt: args.syncedAt,
    });
    return null;
  },
});
```

```typescript
// convex/crons.ts
import { cronJobs } from "convex/server";
import { internal } from "./_generated/api";

const crons = cronJobs();

crons.interval(
  "同步外部数据",
  { minutes: 15 },
  internal.sync.syncExternalData,
  {}
);

export default crons;
```

## 示例

### 定时任务日志模式

```typescript
// convex/schema.ts
import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  cronLogs: defineTable({
    jobName: v.string(),
    startTime: v.number(),
    endTime: v.number(),
    duration: v.number(),
    processedCount: v.number(),
    errorCount: v.number(),
    status: v.union(
      v.literal("success"),
      v.literal("partial"),
      v.literal("failed")
    ),
    error: v.optional(v.string()),
  })
    .index("by_job", ["jobName"])
    .index("by_status", ["status"])
    .index("by_startTime", ["startTime"]),

  sessions: defineTable({
    userId: v.id("users"),
    token: v.string(),
    lastActive: v.number(),
    expiresAt: v.number(),
  })
    .index("by_user", ["userId"])
    .index("by_lastActive", ["lastActive"])
    .index("by_expiresAt", ["expiresAt"]),

  tasks: defineTable({
    type: v.string(),
    status: v.union(
      v.literal("pending"),
      v.literal("processing"),
      v.literal("completed"),
      v.literal("failed")
    ),
    data: v.any(),
    createdAt: v.number(),
    startedAt: v.optional(v.number()),
    completedAt: v.optional(v.number()),
  })
    .index("by_status", ["status"])
    .index("by_type_and_status", ["type", "status"]),
});
```

### 完整的定时任务配置示例

```typescript
// convex/crons.ts
import { cronJobs } from "convex/server";
import { internal } from "./_generated/api";

const crons = cronJobs();

// 清理任务
crons.interval(
  "清理过期会话",
  { hours: 1 },
  internal.cleanup.expiredSessions,
  {}
);

crons.interval(
  "清理旧日志",
  { hours: 24 },
  internal.cleanup.oldLogs,
  { maxAgeDays: 30 }
);

// 同步任务
crons.interval(
  "同步用户数据",
  { minutes: 15 },
  internal.sync.userData,
  {}
);

// 报告任务
crons.cron(
  "每日分析",
  "0 1 * * *",
  internal.reports.dailyAnalytics,
  {}
);

crons.cron(
  "每周总结",
  "0 9 * * 1",
  internal.reports.weeklySummary,
  {}
);

// 健康检查
crons.interval(
  "服务健康检查",
  { minutes: 5 },
  internal.monitoring.healthCheck,
  {}
);

export default crons;
```

## 最佳实践

- 除非明确指示，否则不要运行 `npx convex deploy`
- 除非明确指示，否则不要运行任何git命令
- 仅使用 `crons.interval` 或 `crons.cron` 方法，不要使用已弃用的辅助方法
- 从定时任务中始终调用内部函数以确保安全
- 即使对于同一文件中的函数，也要从 `_generated/api` 中导入 `internal`
- 为生产定时任务添加日志和监控
- 对于处理大型数据集的操作，使用批处理
- 优雅地处理错误以防止任务失败
- 使用有意义的任务名称以便在控制面板中查看
- 在使用cron表达式时考虑时区（凸显使用UTC）

## 常见陷阱

1. **使用公共函数** - 定时任务应仅调用内部函数
2. **长时间运行的突变** - 将大型操作拆分为批次
3. **缺少错误处理** - 未处理的错误将导致整个任务失败
4. **忘记时区** - 所有cron表达式使用UTC
5. **使用已弃用的辅助方法** - 避免 `crons.hourly`、`crons.daily` 等
6. **不记录执行** - 使调试生产问题变得困难

## 参考

- 凸显文档：https://docs.convex.dev/
- 凸显 LLMs.txt：https://docs.convex.dev/llms.txt
- 定时任务：https://docs.convex.dev/scheduling/cron-jobs
- 调度概述：https://docs.convex.dev/scheduling
- 定时函数：https://docs.convex.dev/scheduling/scheduled-functions
