# Convex 安全审计

Convex 应用的全面安全审查模式，包括授权逻辑、数据访问边界、操作隔离、速率限制和保护敏感操作。

## 文档来源

在实施之前，不要假设；获取最新文档：

- 主要：https://docs.convex.dev/auth/functions-auth
- 生产安全：https://docs.convex.dev/production
- 更广泛的背景：https://docs.convex.dev/llms.txt

## 说明

### 安全审计领域

1. **授权逻辑** - 谁能做什么
2. **数据访问边界** - 用户能看到什么数据
3. **操作隔离** - 保护外部 API 调用
4. **速率限制** - 防止滥用
5. **敏感操作** - 保护关键功能

### 授权逻辑审计

#### 基于角色的访问控制 (RBAC)

```typescript
// convex/lib/auth.ts
import { QueryCtx, MutationCtx } from "./_generated/server";
import { ConvexError } from "convex/values";
import { Doc } from "./_generated/dataModel";

type UserRole = "user" | "moderator" | "admin" | "superadmin";

const roleHierarchy: Record<UserRole, number> = {
  user: 0,
  moderator: 1,
  admin: 2,
  superadmin: 3,
};

export async function getUser(ctx: QueryCtx | MutationCtx): Promise<Doc<"users"> | null> {
  const identity = await ctx.auth.getUserIdentity();
  if (!identity) return null;
  
  return await ctx.db
    .query("users")
    .withIndex("by_tokenIdentifier", (q) => 
      q.eq("tokenIdentifier", identity.tokenIdentifier)
    )
    .unique();
}

export async function requireRole(
  ctx: QueryCtx | MutationCtx, 
  minRole: UserRole
): Promise<Doc<"users">> {
  const user = await getUser(ctx);
  
  if (!user) {
    throw new ConvexError({
      code: "UNAUTHENTICATED",
      message: "需要身份验证",
    });
  }
  
  const userRoleLevel = roleHierarchy[user.role as UserRole] ?? 0;
  const requiredLevel = roleHierarchy[minRole];
  
  if (userRoleLevel < requiredLevel) {
    throw new ConvexError({
      code: "FORBIDDEN",
      message: `需要角色 '${minRole}' 或更高权限`,
    });
  }
  
  return user;
}

// 基于权限的检查
type Permission = "read:users" | "write:users" | "delete:users" | "admin:system";

const rolePermissions: Record<UserRole, Permission[]> = {
  user: ["read:users"],
  moderator: ["read:users", "write:users"],
  admin: ["read:users", "write:users", "delete:users"],
  superadmin: ["read:users", "write:users", "delete:users", "admin:system"],
};

export async function requirePermission(
  ctx: QueryCtx | MutationCtx,
  permission: Permission
): Promise<Doc<"users">> {
  const user = await getUser(ctx);
  
  if (!user) {
    throw new ConvexError({ code: "UNAUTHENTICATED", message: "需要身份验证" });
  }
  
  const userRole = user.role as UserRole;
  const permissions = rolePermissions[userRole] ?? [];
  
  if (!permissions.includes(permission)) {
    throw new ConvexError({
      code: "FORBIDDEN",
      message: `需要权限 '${permission}'`,
    });
  }
  
  return user;
}
```

### 数据访问边界审计

```typescript
// convex/data.ts
import { query, mutation } from "./_generated/server";
import { v } from "convex/values";
import { getUser, requireRole } from "./lib/auth";
import { ConvexError } from "convex/values";

// 审计：用户只能看到自己的数据
export const getMyData = query({
  args: {},
  returns: v.array(v.object({
    _id: v.id("userData"),
    content: v.string(),
  })),
  handler: async (ctx) => {
    const user = await getUser(ctx);
    if (!user) return [];
    
    // 安全：按 userId 过滤
    return await ctx.db
      .query("userData")
      .withIndex("by_user", (q) => q.eq("userId", user._id))
      .collect();
  },
});

// 审计：在返回敏感数据前验证所有权
export const getSensitiveItem = query({
  args: { itemId: v.id("sensitiveItems") },
  returns: v.union(v.object({
    _id: v.id("sensitiveItems"),
    secret: v.string(),
  }), v.null()),
  handler: async (ctx, args) => {
    const user = await getUser(ctx);
    if (!user) return null;
    
    const item = await ctx.db.get(args.itemId);
    
    // 安全：验证所有权
    if (!item || item.ownerId !== user._id) {
      return null; // 如果项目存在，则不透露
    }
    
    return item;
  },
});

// 审计：具有访问列表的共享资源
export const getSharedDocument = query({
  args: { docId: v.id("documents") },
  returns: v.union(v.object({
    _id: v.id("documents"),
    content: v.string(),
    accessLevel: v.string(),
  }), v.null()),
  handler: async (ctx, args) => {
    const user = await getUser(ctx);
    const doc = await ctx.db.get(args.docId);
    
    if (!doc) return null;
    
    // 公开文档
    if (doc.visibility === "public") {
      return { ...doc, accessLevel: "public" };
    }
    
    // 必须经过身份验证才能访问非公开文档
    if (!user) return null;
    
    // 所有人拥有完全访问权限
    if (doc.ownerId === user._id) {
      return { ...doc, accessLevel: "owner" };
    }
    
    // 检查共享访问权限
    const access = await ctx.db
      .query("documentAccess")
      .withIndex("by_doc_and_user", (q) => 
        q.eq("documentId", args.docId).eq("userId", user._id)
      )
      .unique();
    
    if (!access) return null;
    
    return { ...doc, accessLevel: access.level };
  },
});
```

### 操作隔离审计

```typescript
// convex/actions.ts
"use node";

import { action, internalAction } from "./_generated/server";
import { v } from "convex/values";
import { api, internal } from "./_generated/api";
import { ConvexError } from "convex/values";

// 安全：响应中永远不要暴露 API 密钥
export const callExternalAPI = action({
  args: { query: v.string() },
  returns: v.object({ result: v.string() }),
  handler: async (ctx, args) => {
    // 验证用户是否经过身份验证
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) {
      throw new ConvexError("需要身份验证");
    }
    
    // 从环境变量获取 API 密钥（不要硬编码）
    const apiKey = process.env.EXTERNAL_API_KEY;
    if (!apiKey) {
      throw new Error("未配置 API 密钥");
    }
    
    // 为审计记录日志
    await ctx.runMutation(internal.audit.logAPICall, {
      userId: identity.tokenIdentifier,
      endpoint: "external-api",
      timestamp: Date.now(),
    });
    
    const response = await fetch("https://api.example.com/query", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ query: args.query }),
    });
    
    if (!response.ok) {
      // 不要暴露外部 API 错误详情
      throw new ConvexError("外部服务不可用");
    }
    
    const data = await response.json();
    
    // 返回之前清理响应
    return { result: sanitizeResponse(data) };
  },
});

// 内部操作 - 不对客户端公开
export const _processPayment = internalAction({
  args: {
    userId: v.id("users"),
    amount: v.number(),
    paymentMethodId: v.string(),
  },
  returns: v.object({ success: v.boolean(), transactionId: v.optional(v.string()) }),
  handler: async (ctx, args) => {
    const stripeKey = process.env.STRIPE_SECRET_KEY;
    
    // 使用 Stripe 处理支付
    // 这绝对不应该作为公共操作公开
    
    return { success: true, transactionId: "txn_xxx" };
  },
});
```

### 速率限制审计

```typescript
// convex/rateLimit.ts
import { mutation, query } from "./_generated/server";
import { v } from "convex/values";
import { ConvexError } from "convex/values";

const RATE_LIMITS = {
  message: { requests: 10, windowMs: 60000 }, // 每分钟 10 次
  upload: { requests: 5, windowMs: 300000 },  // 每 5 分钟 5 次
  api: { requests: 100, windowMs: 3600000 },  // 每小时 100 次
};

export const checkRateLimit = mutation({
  args: {
    userId: v.string(),
    action: v.union(v.literal("message"), v.literal("upload"), v.literal("api")),
  },
  returns: v.object({ allowed: v.boolean(), retryAfter: v.optional(v.number()) }),
  handler: async (ctx, args) => {
    const limit = RATE_LIMITS[args.action];
    const now = Date.now();
    const windowStart = now - limit.windowMs;
    
    // 计算窗口内的请求次数
    const requests = await ctx.db
      .query("rateLimits")
      .withIndex("by_user_and_action", (q) => 
        q.eq("userId", args.userId).eq("action", args.action)
      )
      .filter((q) => q.gt(q.field("timestamp"), windowStart))
      .collect();
    
    if (requests.length >= limit.requests) {
      const oldestRequest = requests[0];
      const retryAfter = oldestRequest.timestamp + limit.windowMs - now;
      
      return { allowed: false, retryAfter };
    }
    
    // 记录此请求
    await ctx.db.insert("rateLimits", {
      userId: args.userId,
      action: args.action,
      timestamp: now,
    });
    
    return { allowed: true };
  },
});

// 在突变中使用
export const sendMessage = mutation({
  args: { content: v.string() },
  returns: v.id("messages"),
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) throw new ConvexError("需要身份验证");
    
    // 检查速率限制
    const rateCheck = await checkRateLimit(ctx, {
      userId: identity.tokenIdentifier,
      action: "message",
    });
    
    if (!rateCheck.allowed) {
      throw new ConvexError({
        code: "RATE_LIMITED",
        message: `请求过多。请 ${Math.ceil(rateCheck.retryAfter! / 1000)} 秒后重试`,
      });
    }
    
    return await ctx.db.insert("messages", {
      content: args.content,
      authorId: identity.tokenIdentifier,
      createdAt: Date.now(),
    });
  },
});
```

### 敏感操作保护

```typescript
// convex/admin.ts
import { mutation, internalMutation } from "./_generated/server";
import { v } from "convex/values";
import { requireRole, requirePermission } from "./lib/auth";
import { internal } from "./_generated/api";

// 双因素确认用于危险操作
export const deleteAllUserData = mutation({
  args: {
    userId: v.id("users"),
    confirmationCode: v.string(),
  },
  returns: v.null(),
  handler: async (ctx, args) => {
    // 需要超级管理员权限
    const admin = await requireRole(ctx, "superadmin");
    
    // 验证确认码
    const confirmation = await ctx.db
      .query("confirmations")
      .withIndex("by_admin_and_code", (q) => 
        q.eq("adminId", admin._id).eq("code", args.confirmationCode)
      )
      .filter((q) => q.gt(q.field("expiresAt"), Date.now()))
      .unique();
    
    if (!confirmation || confirmation.action !== "delete_user_data") {
      throw new ConvexError("无效或过期的确认码");
    }
    
    // 删除确认码以防止重复使用
    await ctx.db.delete(confirmation._id);
    
    // 安排删除（不要直接执行）
    await ctx.scheduler.runAfter(0, internal.admin._performDeletion, {
      userId: args.userId,
      requestedBy: admin._id,
    });
    
    // 审计日志
    await ctx.db.insert("auditLogs", {
      action: "delete_user_data",
      targetUserId: args.userId,
      performedBy: admin._id,
      timestamp: Date.now(),
    });
    
    return null;
  },
});

// 生成敏感操作的确认码
export const requestDeletionConfirmation = mutation({
  args: { userId: v.id("users") },
  returns: v.string(),
  handler: async (ctx, args) => {
    const admin = await requireRole(ctx, "superadmin");
    
    const code = generateSecureCode();
    
    await ctx.db.insert("confirmations", {
      adminId: admin._id,
      code,
      action: "delete_user_data",
      targetUserId: args.userId,
      expiresAt: Date.now() + 5 * 60 * 1000, // 5 分钟
    });
    
    // 在生产环境中，通过安全渠道（电子邮件、短信）发送代码
    return code;
  },
});
```

## 示例

### 完整的审计跟踪系统

```typescript
// convex/audit.ts
import { mutation, query, internalMutation } from "./_generated/server";
import { v } from "convex/values";
import { getUser, requireRole } from "./lib/auth";

const auditEventValidator = v.object({
  _id: v.id("auditLogs"),
  _creationTime: v.number(),
  action: v.string(),
  userId: v.optional(v.string()),
  resourceType: v.string(),
  resourceId: v.string(),
  details: v.optional(v.any()),
  ipAddress: v.optional(v.string()),
  timestamp: v.number(),
});

// 内部：记录审计事件
export const logEvent = internalMutation({
  args: {
    action: v.string(),
    userId: v.optional(v.string()),
    resourceType: v.string(),
    resourceId: v.string(),
    details: v.optional(v.any()),
  },
  returns: v.id("auditLogs"),
  handler: async (ctx, args) => {
    return await ctx.db.insert("auditLogs", {
      ...args,
      timestamp: Date.now(),
    });
  },
});

// 管理员：查看审计日志
export const getAuditLogs = query({
  args: {
    resourceType: v.optional(v.string()),
    userId: v.optional(v.string()),
    limit: v.optional(v.number()),
  },
  returns: v.array(auditEventValidator),
  handler: async (ctx, args) => {
    await requireRole(ctx, "admin");
    
    let query = ctx.db.query("auditLogs");
    
    if (args.resourceType) {
      query = query.withIndex("by_resource_type", (q) => 
        q.eq("resourceType", args.resourceType)
      );
    }
    
    return await query
      .order("desc")
      .take(args.limit ?? 100);
  },
});
```

## 最佳实践

- 除非明确指示，否则永远不要运行 `npx convex deploy`
- 除非明确指示，否则永远不要运行任何 git 命令
- 实施纵深防御（多层安全层）
- 记录所有敏感操作以用于审计跟踪
- 对破坏性操作使用确认码
- 对所有面向用户的端点实施速率限制
- 永远不要暴露内部 API 密钥或错误
- 定期审查访问模式

## 常见陷阱

1. **单点故障** - 实施多个身份验证检查
2. **缺少审计日志** - 记录所有敏感操作
3. **信任客户端数据** - 始终在服务器端验证
4. **暴露错误详情** - 清理错误消息
5. **没有速率限制** - 始终实施速率限制

## 参考

- Convex 文档：https://docs.convex.dev/
- Convex LLMs.txt：https://docs.convex.dev/llms.txt
- Functions Auth：https://docs.convex.dev/auth/functions-auth
- 生产安全：https://docs.convex.dev/production
