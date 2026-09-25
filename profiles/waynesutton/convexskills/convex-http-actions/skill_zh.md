# 凸函数 HTTP 动作

为凸函数应用程序构建用于 webhook、外部 API 集成和自定义路由的 HTTP 端点。

## 文档来源

在实现之前，不要假设；获取最新文档：

- 主要：https://docs.convex.dev/functions/http-actions
- 动作概述：https://docs.convex.dev/functions/actions
- 身份验证：https://docs.convex.dev/auth
- 获取更广泛的背景：https://docs.convex.dev/llms.txt

## 说明

### HTTP 动作概述

HTTP 动作允许您在凸函数中定义 HTTP 端点，这些端点可以：

- 接收来自第三方服务的 webhook
- 创建自定义 API 路由
- 处理文件上传
- 与外部服务集成
- 提供动态内容

### 基本HTTP路由器设置

```typescript
// convex/http.ts
import { httpRouter } from "convex/server";
import { httpAction } from "./_generated/server";

const http = httpRouter();

// 简单的 GET 端点
http.route({
  path: "/health",
  method: "GET",
  handler: httpAction(async (ctx, request) => {
    return new Response(JSON.stringify({ status: "ok" }), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  }),
});

export default http;
```

### 请求处理

```typescript
// convex/http.ts
import { httpRouter } from "convex/server";
import { httpAction } from "./_generated/server";

const http = httpRouter();

// 处理 JSON 正文
http.route({
  path: "/api/data",
  method: "POST",
  handler: httpAction(async (ctx, request) => {
    // 解析 JSON 正文
    const body = await request.json();
    
    // 访问头部
    const authHeader = request.headers.get("Authorization");
    
    // 访问 URL 参数
    const url = new URL(request.url);
    const queryParam = url.searchParams.get("filter");

    return new Response(
      JSON.stringify({ received: body, filter: queryParam }),
      {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }
    );
  }),
});

// 处理表单数据
http.route({
  path: "/api/form",
  method: "POST",
  handler: httpAction(async (ctx, request) => {
    const formData = await request.formData();
    const name = formData.get("name");
    const email = formData.get("email");

    return new Response(
      JSON.stringify({ name, email }),
      {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }
    );
  }),
});

// 处理原始字节
http.route({
  path: "/api/upload",
  method: "POST",
  handler: httpAction(async (ctx, request) => {
    const bytes = await request.bytes();
    const contentType = request.headers.get("Content-Type") ?? "application/octet-stream";
    
    // 存储在凸函数存储中
    const blob = new Blob([bytes], { type: contentType });
    const storageId = await ctx.storage.store(blob);

    return new Response(
      JSON.stringify({ storageId }),
      {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }
    );
  }),
});

export default http;
```

### 路径参数

使用路径前缀匹配动态路由：

```typescript
// convex/http.ts
import { httpRouter } from "convex/server";
import { httpAction } from "./_generated/server";

const http = httpRouter();

// 匹配 /api/users/* 使用 pathPrefix
http.route({
  pathPrefix: "/api/users/",
  method: "GET",
  handler: httpAction(async (ctx, request) => {
    const url = new URL(request.url);
    // 从路径中提取用户 ID：/api/users/123 -> "123"
    const userId = url.pathname.replace("/api/users/", "");

    return new Response(
      JSON.stringify({ userId }),
      {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }
    );
  }),
});

export default http;
```

### CORS 配置

```typescript
// convex/http.ts
import { httpRouter } from "convex/server";
import { httpAction } from "./_generated/server";

const http = httpRouter();

// CORS 头部辅助函数
const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization",
  "Access-Control-Max-Age": "86400",
};

// 处理预检请求
http.route({
  path: "/api/data",
  method: "OPTIONS",
  handler: httpAction(async () => {
    return new Response(null, {
      status: 204,
      headers: corsHeaders,
    });
  }),
});

// 实际端点带 CORS
http.route({
  path: "/api/data",
  method: "POST",
  handler: httpAction(async (ctx, request) => {
    const body = await request.json();

    return new Response(
      JSON.stringify({ success: true, data: body }),
      {
        status: 200,
        headers: {
          "Content-Type": "application/json",
          ...corsHeaders,
        },
      }
    );
  }),
});

export default http;
```

### webhook 处理

```typescript
// convex/http.ts
import { httpRouter } from "convex/server";
import { httpAction } from "./_generated/server";
import { internal } from "./_generated/api";

const http = httpRouter();

// Stripe webhook
http.route({
  path: "/webhooks/stripe",
  method: "POST",
  handler: httpAction(async (ctx, request) => {
    const signature = request.headers.get("stripe-signature");
    if (!signature) {
      return new Response("Missing signature", { status: 400 });
    }

    const body = await request.text();

    // 验证 webhook 签名（在 Node.js 动作中）
    try {
      await ctx.runAction(internal.stripe.verifyAndProcessWebhook, {
        body,
        signature,
      });
      return new Response("OK", { status: 200 });
    } catch (error) {
      console.error("Webhook error:", error);
      return new Response("Webhook error", { status: 400 });
    }
  }),
});

// GitHub webhook
http.route({
  path: "/webhooks/github",
  method: "POST",
  handler: httpAction(async (ctx, request) => {
    const event = request.headers.get("X-GitHub-Event");
    const signature = request.headers.get("X-Hub-Signature-256");
    
    if (!signature) {
      return new Response("Missing signature", { status: 400 });
    }

    const body = await request.text();

    await ctx.runAction(internal.github.processWebhook, {
      event: event ?? "unknown",
      body,
      signature,
    });

    return new Response("OK", { status: 200 });
  }),
});

export default http;
```

### webhook 签名验证

```typescript
// convex/stripe.ts
"use node";

import { internalAction, internalMutation } from "./_generated/server";
import { internal } from "./_generated/api";
import { v } from "convex/values";
import Stripe from "stripe";

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!);

export const verifyAndProcessWebhook = internalAction({
  args: {
    body: v.string(),
    signature: v.string(),
  },
  returns: v.null(),
  handler: async (ctx, args) => {
    const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET!;

    // 验证签名
    const event = stripe.webhooks.constructEvent(
      args.body,
      args.signature,
      webhookSecret
    );

    // 基于事件类型处理
    switch (event.type) {
      case "checkout.session.completed":
        await ctx.runMutation(internal.payments.handleCheckoutComplete, {
          sessionId: event.data.object.id,
          customerId: event.data.object.customer as string,
        });
        break;

      case "customer.subscription.updated":
        await ctx.runMutation(internal.subscriptions.handleUpdate, {
          subscriptionId: event.data.object.id,
          status: event.data.object.status,
        });
        break;
    }

    return null;
  },
});
```

### HTTP 动作中的身份验证

```typescript
// convex/http.ts
import { httpRouter } from "convex/server";
import { httpAction } from "./_generated/server";
import { internal } from "./_generated/api";

const http = httpRouter();

// API 密钥身份验证
http.route({
  path: "/api/protected",
  method: "GET",
  handler: httpAction(async (ctx, request) => {
    const apiKey = request.headers.get("X-API-Key");
    
    if (!apiKey) {
      return new Response(
        JSON.stringify({ error: "Missing API key" }),
        { status: 401, headers: { "Content-Type": "application/json" } }
      );
    }

    // 验证 API 密钥
    const isValid = await ctx.runQuery(internal.auth.validateApiKey, {
      apiKey,
    });

    if (!isValid) {
      return new Response(
        JSON.stringify({ error: "Invalid API key" }),
        { status: 403, headers: { "Content-Type": "application/json" } }
      );
    }

    // 处理经过身份验证的请求
    const data = await ctx.runQuery(internal.data.getProtectedData, {});

    return new Response(
      JSON.stringify(data),
      { status: 200, headers: { "Content-Type": "application/json" } }
    );
  }),
});

// Bearer 令牌身份验证
http.route({
  path: "/api/user",
  method: "GET",
  handler: httpAction(async (ctx, request) => {
    const authHeader = request.headers.get("Authorization");
    
    if (!authHeader?.startsWith("Bearer ")) {
      return new Response(
        JSON.stringify({ error: "Missing or invalid Authorization header" }),
        { status: 401, headers: { "Content-Type": "application/json" } }
      );
    }

    const token = authHeader.slice(7);

    // 验证令牌并获取用户
    const user = await ctx.runQuery(internal.auth.validateToken, { token });

    if (!user) {
      return new Response(
        JSON.stringify({ error: "Invalid token" }),
        { status: 403, headers: { "Content-Type": "application/json" } }
      );
    }

    return new Response(
      JSON.stringify(user),
      { status: 200, headers: { "Content-Type": "application/json" } }
    );
  }),
});

export default http;
```

### 调用突变和查询

```typescript
// convex/http.ts
import { httpRouter } from "convex/server";
import { httpAction } from "./_generated/server";
import { api, internal } from "./_generated/api";

const http = httpRouter();

http.route({
  path: "/api/items",
  method: "POST",
  handler: httpAction(async (ctx, request) => {
    const body = await request.json();

    // 调用突变
    const itemId = await ctx.runMutation(internal.items.create, {
      name: body.name,
      description: body.description,
    });

    // 查询创建的项目
    const item = await ctx.runQuery(internal.items.get, { id: itemId });

    return new Response(
      JSON.stringify(item),
      { status: 201, headers: { "Content-Type": "application/json" } }
    );
  }),
});

http.route({
  path: "/api/items",
  method: "GET",
  handler: httpAction(async (ctx, request) => {
    const url = new URL(request.url);
    const limit = parseInt(url.searchParams.get("limit") ?? "10");

    const items = await ctx.runQuery(internal.items.list, { limit });

    return new Response(
      JSON.stringify(items),
      { status: 200, headers: { "Content-Type": "application/json" } }
    );
  }),
});

export default http;
```

### 错误处理

```typescript
// convex/http.ts
import { httpRouter } from "convex/server";
import { httpAction } from "./_generated/server";

const http = httpRouter();

// JSON 响应辅助函数
function jsonResponse(data: unknown, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

// 错误响应辅助函数
function errorResponse(message: string, status: number) {
  return jsonResponse({ error: message }, status);
}

http.route({
  path: "/api/process",
  method: "POST",
  handler: httpAction(async (ctx, request) => {
    try {
      // 验证内容类型
      const contentType = request.headers.get("Content-Type");
      if (!contentType?.includes("application/json")) {
        return errorResponse("Content-Type must be application/json", 415);
      }

      // 解析正文
      let body;
      try {
        body = await request.json();
      } catch {
        return errorResponse("Invalid JSON body", 400);
      }

      // 验证必需字段
      if (!body.data) {
        return errorResponse("Missing required field: data", 400);
      }

      // 处理请求
      const result = await ctx.runMutation(internal.process.handle, {
        data: body.data,
      });

      return jsonResponse({ success: true, result }, 200);
    } catch (error) {
      console.error("Processing error:", error);
      return errorResponse("Internal server error", 500);
    }
  }),
});

export default http;
```

### 文件下载

```typescript
// convex/http.ts
import { httpRouter } from "convex/server";
import { httpAction } from "./_generated/server";
import { Id } from "./_generated/dataModel";

const http = httpRouter();

http.route({
  pathPrefix: "/files/",
  method: "GET",
  handler: httpAction(async (ctx, request) => {
    const url = new URL(request.url);
    const fileId = url.pathname.replace("/files/", "") as Id<"_storage">;

    // 从存储中获取文件 URL
    const fileUrl = await ctx.storage.getUrl(fileId);

    if (!fileUrl) {
      return new Response("File not found", { status: 404 });
    }

    // 重定向到文件 URL
    return Response.redirect(fileUrl, 302);
  }),
});

export default http;
```

## 示例

### 完整的 webhook 集成

```typescript
// convex/http.ts
import { httpRouter } from "convex/server";
import { httpAction } from "./_generated/server";
import { internal } from "./_generated/api";

const http = httpRouter();

// Clerk webhook 用于用户同步
http.route({
  path: "/webhooks/clerk",
  method: "POST",
  handler: httpAction(async (ctx, request) => {
    const svixId = request.headers.get("svix-id");
    const svixTimestamp = request.headers.get("svix-timestamp");
    const svixSignature = request.headers.get("svix-signature");

    if (!svixId || !svixTimestamp || !svixSignature) {
      return new Response("Missing Svix headers", { status: 400 });
    }

    const body = await request.text();

    try {
      await ctx.runAction(internal.clerk.verifyAndProcess, {
        body,
        svixId,
        svixTimestamp,
        svixSignature,
      });
      return new Response("OK", { status: 200 });
    } catch (error) {
      console.error("Clerk webhook error:", error);
      return new Response("Webhook verification failed", { status: 400 });
    }
  }),
});

export default http;
```

```typescript
// convex/clerk.ts
"use node";

import { internalAction, internalMutation } from "./_generated/server";
import { internal } from "./_generated/api";
import { v } from "convex/values";
import { Webhook } from "svix";

export const verifyAndProcess = internalAction({
  args: {
    body: v.string(),
    svixId: v.string(),
    svixTimestamp: v.string(),
    svixSignature: v.string(),
  },
  returns: v.null(),
  handler: async (ctx, args) => {
    const webhookSecret = process.env.CLERK_WEBHOOK_SECRET!;
    const wh = new Webhook(webhookSecret);

    const event = wh.verify(args.body, {
      "svix-id": args.svixId,
      "svix-timestamp": args.svixTimestamp,
      "svix-signature": args.svixSignature,
    }) as { type: string; data: Record<string, unknown> };

    switch (event.type) {
      case "user.created":
        await ctx.runMutation(internal.users.create, {
          clerkId: event.data.id as string,
          email: (event.data.email_addresses as Array<{ email_address: string }>)[0]?.email_address,
          name: `${event.data.first_name} ${event.data.last_name}`,
        });
        break;

      case "user.updated":
        await ctx.runMutation(internal.users.update, {
          clerkId: event.data.id as string,
          email: (event.data.email_addresses as Array<{ email_address: string }>)[0]?.email_address,
          name: `${event.data.first_name} ${event.data.last_name}`,
        });
        break;

      case "user.deleted":
        await ctx.runMutation(internal.users.remove, {
          clerkId: event.data.id as string,
        });
        break;
    }

    return null;
  },
});
```

### HTTP API 的模式

```typescript
// convex/schema.ts
import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  apiKeys: defineTable({
    key: v.string(),
    userId: v.id("users"),
    name: v.string(),
    createdAt: v.number(),
    lastUsedAt: v.optional(v.number()),
    revokedAt: v.optional(v.number()),
  })
    .index("by_key", ["key"])
    .index("by_user", ["userId"]),

  webhookEvents: defineTable({
    source: v.string(),
    eventType: v.string(),
    payload: v.any(),
    processedAt: v.number(),
    status: v.union(
      v.literal("success"),
      v.literal("failed")
    ),
    error: v.optional(v.string()),
  })
    .index("by_source", ["source"])
    .index("by_status", ["status"]),

  users: defineTable({
    clerkId: v.string(),
    email: v.string(),
    name: v.string(),
  }).index("by_clerk_id", ["clerkId"]),
});
```

## 最佳实践

- 除非明确指示，否则永远不要运行 `npx convex deploy`
- 除非明确指示，否则永远不要运行任何 git 命令
- 始终验证和清理传入的请求数据
- 使用内部函数进行数据库操作
- 实现适当的错误处理和状态代码
- 为浏览器可访问的端点添加 CORS 头部
- 在处理之前验证 webhook 签名
- 为调试记录 webhook 事件
- 使用环境变量存储密钥
- 优雅地处理超时

## 常见陷阱

1. **缺少 CORS 预检处理器** - 浏览器首先发送 OPTIONS 请求
2. **未验证 webhook 签名** - 安全漏洞
3. **暴露内部函数** - 使用来自 HTTP 动作的内部函数
4. **忘记 Content-Type 头部** - 客户端可能无法正确解析响应
5. **未处理请求正文错误** - 无效的 JSON 将引发错误
6. **在长时间运行的操作上阻塞** - 使用计划函数进行重处理

## 参考

- Convex 文档：https://docs.convex.dev/
- Convex LLMs.txt：https://docs.convex.dev/llms.txt
- HTTP 动作：https://docs.convex.dev/functions/http-actions
- 动作：https://docs.convex.dev/functions/actions
- 身份验证：https://docs.convex.dev/auth
