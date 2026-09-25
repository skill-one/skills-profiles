# 凸显安全检查

凸显应用的快速安全审计清单，涵盖身份验证、函数暴露、参数验证、行级访问控制和环境变量处理。

## 文档来源

在实施之前，不要假设；获取最新文档：

- 主要：https://docs.convex.dev/auth
- 生产安全：https://docs.convex.dev/production
- 函数认证：https://docs.convex.dev/auth/functions-auth
- 更广泛的背景：https://docs.convex.dev/llms.txt

## 说明

### 安全清单

使用此清单快速审计您的凸显应用的安全性：

#### 1. 身份验证

- [ ] 配置了身份验证提供者（Clerk、Auth0 等）
- [ ] 所有敏感查询检查 `ctx.auth.getUserIdentity()`
- [ ] 明确允许在预期的地方进行未身份验证访问
- [ ] 会话令牌正确验证

#### 2. 函数暴露

- [ ] 审查了公共函数（`query`、`mutation`、`action`）
- [ ] 内部函数使用 `internalQuery`、`internalMutation`、`internalAction`
- [ ] 不将敏感操作暴露为公共函数
- [ ] HTTP 动作验证来源/身份验证

#### 3. 参数验证

- [ ] 所有函数都有明确的 `args` 验证器
- [ ] 所有函数都有明确的 `returns` 验证器
- [ ] 不对敏感数据使用 `v.any()`
- [ ] ID 验证器使用正确的表名

#### 4. 行级访问控制

- [ ] 用户只能访问自己的数据
- [ ] 管理函数检查用户角色
- [ ] 共享资源有适当的访问检查
- [ ] 删除函数验证所有权

#### 5. 环境变量

- [ ] API 密钥存储在环境变量中
- [ ] 代码或模式中不包含密钥
- [ ] 开发/生产环境使用不同的密钥
- [ ] 仅在动作中访问环境变量

### 身份验证检查

```typescript
// convex/auth.ts
import { query, mutation } from "./_generated/server";
import { v } from "convex/values";
import { ConvexError } from "convex/values";

// 需要身份验证的辅助函数
async function requireAuth(ctx: QueryCtx | MutationCtx) {
  const identity = await ctx.auth.getUserIdentity();
  if (!identity) {
    throw new ConvexError("需要身份验证");
  }
  return identity;
}

// 安全查询模式
export const getMyProfile = query({
  args: {},
  returns: v.union(v.object({
    _id: v.id("users"),
    name: v.string(),
    email: v.string(),
  }), v.null()),
  handler: async (ctx) => {
    const identity = await requireAuth(ctx);
    
    return await ctx.db
      .query("users")
      .withIndex("by_tokenIdentifier", (q) => 
        q.eq("tokenIdentifier", identity.tokenIdentifier)
      )
      .unique();
  },
});
```

### 函数暴露检查

```typescript
// 公开 - 暴露给客户端（仔细审查！）
export const listPublicPosts = query({
  args: {},
  returns: v.array(v.object({ /* ... */ })),
  handler: async (ctx) => {
    // 任何人都可以调用此函数 - 故意公开
    return await ctx.db
      .query("posts")
      .withIndex("by_public", (q) => q.eq("isPublic", true))
      .collect();
  },
});

// 内部 - 仅可从其他凸显函数调用
export const _updateUserCredits = internalMutation({
  args: { userId: v.id("users"), amount: v.number() },
  returns: v.null(),
  handler: async (ctx, args) => {
    // 不能直接从客户端调用此函数
    await ctx.db.patch(args.userId, {
      credits: args.amount,
    });
    return null;
  },
});
```

### 参数验证检查

```typescript
// 良好：严格验证
export const createPost = mutation({
  args: {
    title: v.string(),
    content: v.string(),
    category: v.union(
      v.literal("tech"),
      v.literal("news"),
      v.literal("other")
    ),
  },
  returns: v.id("posts"),
  handler: async (ctx, args) => {
    const identity = await requireAuth(ctx);
    return await ctx.db.insert("posts", {
      ...args,
      authorId: identity.tokenIdentifier,
    });
  },
});

// 不良：弱验证
export const createPostUnsafe = mutation({
  args: {
    data: v.any(), // 危险：允许任何数据
  },
  returns: v.id("posts"),
  handler: async (ctx, args) => {
    return await ctx.db.insert("posts", args.data);
  },
});
```

### 行级访问控制检查

```typescript
// 更新前验证所有权
export const updateTask = mutation({
  args: {
    taskId: v.id("tasks"),
    title: v.string(),
  },
  returns: v.null(),
  handler: async (ctx, args) => {
    const identity = await requireAuth(ctx);
    
    const task = await ctx.db.get(args.taskId);
    
    // 检查所有权
    if (!task || task.userId !== identity.tokenIdentifier) {
      throw new ConvexError("无权更新此任务");
    }
    
    await ctx.db.patch(args.taskId, { title: args.title });
    return null;
  },
});

// 删除前验证所有权
export const deleteTask = mutation({
  args: { taskId: v.id("tasks") },
  returns: v.null(),
  handler: async (ctx, args) => {
    const identity = await requireAuth(ctx);
    
    const task = await ctx.db.get(args.taskId);
    
    if (!task || task.userId !== identity.tokenIdentifier) {
      throw new ConvexError("无权删除此任务");
    }
    
    await ctx.db.delete(args.taskId);
    return null;
  },
});
```

### 环境变量检查

```typescript
// convex/actions.ts
"use node";

import { action } from "./_generated/server";
import { v } from "convex/values";

export const sendEmail = action({
  args: {
    to: v.string(),
    subject: v.string(),
    body: v.string(),
  },
  returns: v.object({ success: v.boolean() }),
  handler: async (ctx, args) => {
    // 从环境变量访问 API 密钥
    const apiKey = process.env.RESEND_API_KEY;
    
    if (!apiKey) {
      throw new Error("未配置 RESEND_API_KEY");
    }
    
    const response = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        from: "noreply@example.com",
        to: args.to,
        subject: args.subject,
        html: args.body,
      }),
    });
    
    return { success: response.ok };
  },
});
```

## 示例

### 完整安全模式

```typescript
// convex/secure.ts
import { query, mutation, internalMutation } from "./_generated/server";
import { v } from "convex/values";
import { ConvexError } from "convex/values";

// 身份验证辅助函数
async function getAuthenticatedUser(ctx: QueryCtx | MutationCtx) {
  const identity = await ctx.auth.getUserIdentity();
  if (!identity) {
    throw new ConvexError({
      code: "UNAUTHENTICATED",
      message: "您必须登录",
    });
  }
  
  const user = await ctx.db
    .query("users")
    .withIndex("by_tokenIdentifier", (q) => 
      q.eq("tokenIdentifier", identity.tokenIdentifier)
    )
    .unique();
    
  if (!user) {
    throw new ConvexError({
      code: "USER_NOT_FOUND",
      message: "用户资料未找到",
    });
  }
  
  return user;
}

// 检查管理员角色
async function requireAdmin(ctx: QueryCtx | MutationCtx) {
  const user = await getAuthenticatedUser(ctx);
  
  if (user.role !== "admin") {
    throw new ConvexError({
      code: "FORBIDDEN",
      message: "需要管理员访问权限",
    });
  }
  
  return user;
}

// 公开：列出自己的任务
export const listMyTasks = query({
  args: {},
  returns: v.array(v.object({
    _id: v.id("tasks"),
    title: v.string(),
    completed: v.boolean(),
  })),
  handler: async (ctx) => {
    const user = await getAuthenticatedUser(ctx);
    
    return await ctx.db
      .query("tasks")
      .withIndex("by_user", (q) => q.eq("userId", user._id))
      .collect();
  },
});

// 管理员专有：列出所有用户
export const listAllUsers = query({
  args: {},
  returns: v.array(v.object({
    _id: v.id("users"),
    name: v.string(),
    role: v.string(),
  })),
  handler: async (ctx) => {
    await requireAdmin(ctx);
    
    return await ctx.db.query("users").collect();
  },
});

// 内部：更新用户角色（从不暴露）
export const _setUserRole = internalMutation({
  args: {
    userId: v.id("users"),
    role: v.union(v.literal("user"), v.literal("admin")),
  },
  returns: v.null(),
  handler: async (ctx, args) => {
    await ctx.db.patch(args.userId, { role: args.role });
    return null;
  },
});
```

## 最佳实践

- 除非明确指示，否则不要运行 `npx convex deploy`
- 除非明确指示，否则不要运行任何 git 命令
- 返回敏感数据前始终验证用户身份
- 对敏感操作使用内部函数
- 使用严格的验证器验证所有参数
- 在更新/删除操作前检查所有权
- 将 API 密钥存储在环境变量中
- 审查所有公共函数的安全影响

## 常见陷阱

1. **缺少身份验证检查** - 始终验证身份
2. **暴露内部操作** - 使用 `internalMutation/Query`
3. **信任客户端提供的 ID** - 验证所有权
4. **对参数使用 v.any()** - 使用特定验证器
5. **硬编码密钥** - 使用环境变量

## 参考

- 凸显文档：https://docs.convex.dev/
- 凸显 LLMs.txt：https://docs.convex.dev/llms.txt
- 身份验证：https://docs.convex.dev/auth
- 生产安全：https://docs.convex.dev/production
- 函数认证：https://docs.convex.dev/auth/functions-auth
