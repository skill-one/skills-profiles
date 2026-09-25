# Inngest 设置

本指南将指导您从零开始在一个 TypeScript 项目中设置 Inngest，涵盖安装、客户端配置、连接模式和本地开发。

> **这些指南专注于 TypeScript。** 对于 Python 或 Go，请参考 Inngest 文档 ([Inngest documentation](https://www.inngest.com/llms.txt)) 获取特定语言的指导。核心概念适用于所有语言。

## 前置条件

- Node.js 18+（推荐使用 Node.js 22.4+ 以支持 WebSocket）
- TypeScript 项目
- 包管理器（npm、yarn、pnpm 或 bun）

## 第 1 步：安装 Inngest SDK

在您的项目中安装 `inngest` npm 包：

```bash
npm install inngest
# 或
yarn add inngest
# 或
pnpm add inngest
# 或
bun add inngest
```

## 第 2 步：创建 Inngest 客户端

创建一个共享的客户端文件，您将在整个代码库中导入它：

```typescript
// src/inngest/client.ts
import { Inngest } from "inngest";

export const inngest = new Inngest({
  id: "my-app" // 您应用程序的唯一标识符（连字符分隔的 slug）
});
// 重要提示：v4 默认为 Cloud 模式。本地开发时，请设置环境变量 INNGEST_DEV=1。
// 如果不设置，您的 serve 端点将返回 500 错误（"In cloud mode but no signing key"）。
// 在生产环境中，请设置 INNGEST_SIGNING_KEY（Cloud 模式需要）。
```

### 关键配置选项

- **`id`**（必需）：您的应用程序的唯一标识符。使用连字符分隔的 slug，例如 `"my-app"` 或 `"user-service"`
- **`eventKey`**：发送事件的事件键（推荐使用环境变量 INNGEST_EVENT_KEY）
- **`env`**：分支环境的环境名称
- **`isDev`**：强制 Dev 模式（`true`）或 Cloud 模式（`false`）。**v4 默认为 Cloud 模式**，因此本地开发时请设置 `INNGEST_DEV=1` 环境变量。**切勿在源代码中硬编码 `isDev: true`** —— 这将在生产环境中导致静默错误。始终使用环境变量。
- **`signingKey`**：生产的签名密钥（推荐使用环境变量 INNGEST_SIGNING_KEY）。v4 中从 `serve()` 移动到客户端
- **`signingKeyFallback`**：密钥轮换的备用签名密钥（推荐使用环境变量 INNGEST_SIGNING_KEY_FALLBACK）
- **`baseUrl`**：自定义 Inngest API 基础 URL（推荐使用环境变量 INNGEST_BASE_URL）
- **`logger`**：自定义日志记录器实例（例如 winston、pino）—— 启用函数上下文中的 `logger`
- **`middleware`**：中间件数组（参见 **inngest-middleware** 指南）

### 使用 eventType() 发送带类型的 Event

```typescript
import { Inngest, eventType } from "inngest";
import { z } from "zod";

const signupCompleted = eventType("user/signup.completed", {
  schema: z.object({
    userId: z.string(),
    email: z.string(),
    plan: z.enum(["free", "pro"])
  })
});

const orderPlaced = eventType("order/placed", {
  schema: z.object({
    orderId: z.string(),
    amount: z.number()
  })
});

export const inngest = new Inngest({ id: "my-app" });

// 使用事件类型作为触发器，实现完全的类型安全：
inngest.createFunction(
  { id: "handle-signup", triggers: [signupCompleted] },
  async ({ event }) => {
    event.data.userId; /* 类型为 string */
  }
);

// 发送事件时使用事件类型：
await inngest.send(
  signupCompleted.create({
    userId: "user_123",
    email: "user@example.com",
    plan: "pro"
  })
);
```

### 环境变量设置

在您的 `.env` 文件或部署环境中设置以下环境变量：

```env
# 生产必需
INNGEST_EVENT_KEY=your-event-key-here
INNGEST_SIGNING_KEY=your-signing-key-here

# 本地开发时强制 Dev 模式
INNGEST_DEV=1

# 可选 - 自定义开发服务器 URL（默认：http://localhost:8288）
INNGEST_BASE_URL=http://localhost:8288
```

**⚠️ 常见问题**：切勿在源代码中硬编码密钥。始终使用环境变量 `INNGEST_EVENT_KEY` 和 `INNGEST_SIGNING_KEY`。

## 关键：为本地开发启用 Dev 模式

**在创建 serve 端点或连接工作器之前，确保已启用 Dev 模式。** 如果不启用，Inngest 将默认为 Cloud 模式，并且您的端点将返回 500 错误。

在 `.env` 文件（或 package.json 中的开发脚本）中添加：

```env
INNGEST_DEV=1
```

或在 `package.json` 脚本中：

```json
{
  "scripts": {
    "dev": "INNGEST_DEV=1 tsx --watch src/server.ts"
  }
}
```

**缺少 INNGEST_DEV 的症状**：
- GET `/api/inngest` 返回 `{"code":"internal_server_error"}`
- 服务器日志："In cloud mode but no signing key found"
- 开发服务器无法与您的应用程序同步

## 第 3 步：选择您的连接模式

Inngest 支持两种连接模式：

### 模式 A：Serve 端点（HTTP）

适用于无服务器平台（Vercel、Lambda 等）和现有 API。

### 模式 B：Connect（WebSocket）

适用于容器运行时（Kubernetes、Docker）和长时间运行的进程。

## 第 4A 步：提供端点（HTTP 模式）

创建一个 API 端点，将您的函数暴露给 Inngest：

```typescript
// 对于 Next.js App Router: src/app/api/inngest/route.ts
import { serve } from "inngest/next";
import { inngest } from "../../../inngest/client";
import { myFunction } from "../../../inngest/functions";

export const { GET, POST, PUT } = serve({
  client: inngest,
  functions: [myFunction]
});
```

```typescript
// 对于 Next.js Pages Router: pages/api/inngest.ts
import { serve } from "inngest/next";
import { inngest } from "../../inngest/client";
import { myFunction } from "../../inngest/functions";

export default serve({
  client: inngest,
  functions: [myFunction]
});
```

```typescript
// 对于 Express.js
import express from "express";
import { serve } from "inngest/express";
import { inngest } from "./inngest/client";
import { myFunction } from "./inngest/functions";

const app = express();
app.use(express.json({ limit: "10mb" })); // Inngest 需要，增加限制以支持更大的函数状态

app.use(
  "/api/inngest",
  serve({
    client: inngest,
    functions: [myFunction]
  })
);
```

**🔧 框架特定说明**：

- **Express**：必须使用 `express.json({ limit: "10mb" })` 中间件以支持更大的函数状态。
- **Fastify**：使用 `inngest/fastify` 中的 `fastifyPlugin`
- **Cloudflare Workers**：使用 `inngest/cloudflare`
- **AWS Lambda**：使用 `inngest/lambda`
- 对于所有其他框架，请查看此处 `serve` 的参考：https://www.inngest.com/docs-markdown/learn/serving-inngest-functions

**⚠️ v4 变更**：`signingKey`、`signingKeyFallback` 和 `baseUrl` 等选项现在在 `Inngest` 客户端构造函数中配置，而不是在 `serve()` 中。`serve()` 函数仅接受 `client`、`functions` 和 `streaming`。

**⚠️ 常见问题**：始终使用 `/api/inngest` 作为您的端点路径。这启用了自动发现。如果您必须使用不同的路径，您需要使用 `-u` 标志手动配置发现。

## 第 4B 步：作为工作器连接（WebSocket 模式）

适用于长时间运行的应用程序，这些应用程序维护持久连接：

```typescript
// src/worker.ts
import { connect } from "inngest/connect";
import { inngest } from "./inngest/client";
import { myFunction } from "./inngest/functions";

(async () => {
  const connection = await connect({
    apps: [{ client: inngest, functions: [myFunction] }],
    instanceId: process.env.HOSTNAME, // 工作器的唯一标识符
    maxWorkerConcurrency: 10 // 最大并发步骤
  });

  console.log("Worker connected:", connection.state);

  // 平稳关闭处理
  await connection.closed;
  console.log("Worker shut down");
})();
```

**Connect 模式的要求**：

- Node.js 22.4+（或 Deno 1.4+、Bun 1.1+）以支持 WebSocket
- 长时间运行的服务器环境（非无服务器）
- 生产环境需要 `INNGEST_SIGNING_KEY` 和 `INNGEST_EVENT_KEY`
- 在生产环境中设置 `Inngest` 客户端的 `appVersion` 参数以支持滚动部署

**v4 Connect 变更**：

- **工作线程隔离** 默认启用——WebSocket 连接在工作者线程中执行，以防止事件循环饥饿。设置 `isolateExecution: false` 以使用单个进程（或 `INNGEST_CONNECT_ISOLATE_EXECUTION=false`）
- **`rewriteGatewayEndpoint`** 回调已被 `gatewayUrl` 字符串选项（或 `INNGEST_CONNECT_GATEWAY_URL` 环境变量）取代

## 第 5 步：使用 Apps 组织

随着系统的增长，将函数组织到逻辑应用中：

```typescript
// 用户服务
const userService = new Inngest({ id: "user-service" });

// 支付服务
const paymentService = new Inngest({ id: "payment-service" });

// 邮件服务
const emailService = new Inngest({ id: "email-service" });
```

每个应用在 Inngest 仪表板中都有自己的部分，并且可以独立部署。使用描述性、连字符分隔的 ID，这些 ID 与您的服务架构匹配。

**⚠️ 常见问题**：更改应用的 `id` 将在 Inngest 中创建一个新的应用。在部署中保持 ID 一致。

## 第 6 步：使用 inngest-cli 进行本地开发

启动 Inngest Dev Server 进行本地开发：

```bash
# 自动发现您的应用在常见端口/端点
npx --ignore-scripts=false inngest-cli@latest dev

# 手动指定您的应用的 URL
npx --ignore-scripts=false inngest-cli@latest dev -u http://localhost:3000/api/inngest

# 开发服务器的自定义端口
npx --ignore-scripts=false inngest-cli@latest dev -p 9999

# 禁用自动发现
npx --ignore-scripts=false inngest-cli@latest dev --no-discovery -u http://localhost:3000/api/inngest

# 多个应用
npx --ignore-scripts=false inngest-cli@latest dev -u http://localhost:3000/api/inngest -u http://localhost:4000/api/inngest
```

默认情况下，开发服务器将在 `http://localhost:8288` 上可用。

### 配置文件（可选）

为复杂设置创建 `inngest.json`：

```json
{
  "sdk-url": [
    "http://localhost:3000/api/inngest",
    "http://localhost:4000/api/inngest"
  ],
  "port": 8289,
  "no-discovery": true
}
```

## 环境特定设置

### 本地开发

```env
INNGEST_DEV=1
# 开发模式下不需要密钥
```

### 生产

```env
INNGEST_EVENT_KEY=evt_your_production_event_key
INNGEST_SIGNING_KEY=signkey_your_production_signing_key
```

### 自定义开发服务器端口

```env
INNGEST_DEV=1
INNGEST_BASE_URL=http://localhost:9999
```

如果您的应用程序运行在非标准端口（不是 3000），请确保开发服务器可以到达它，通过使用 `-u` 标志指定 URL。

## 常见问题及解决方案

**端口冲突**：如果端口 8288 正在使用中，请指定不同的端口：`-p 9999`

**自动发现不工作**：使用手动 URL 指定：`-u http://localhost:YOUR_PORT/api/inngest`。如果使用 `--no-discovery` 标志，`-u` 标志是**必需的**——如果没有它，开发服务器将无法找到您的应用程序。

**函数未在开发服务器中显示**：您的应用程序必须注册到开发服务器。当开发服务器从开发服务器接收到第一个请求时，这会自动发生。如果注册没有发生： (1) 验证 `INNGEST_DEV=1` 是否设置，(2) 验证开发服务器是否可以到达您的应用 URL，(3) 尝试在开发服务器运行时重启您的应用程序。

**签名验证错误**：确保在生产环境中正确设置 `INNGEST_SIGNING_KEY`

**WebSocket 连接问题**：验证 Connect 模式需要 Node.js 版本 22.4+

**Docker 开发**：在 Docker 中运行开发服务器时，使用 `host.docker.internal` 作为应用 URL

## 下一步

1. 使用 `inngest.createFunction()` 创建您的第一个 Inngest 函数
2. 使用开发服务器的“Invoke”按钮测试函数
3. 使用 `inngest.send()` 发送事件以触发函数
4. 使用正确的环境变量部署到生产环境
5. 查看 **inngest-middleware** 以添加日志记录、错误跟踪和其他横切关注点
6. 在 Inngest 仪表板中监控函数

当您更改函数时，开发服务器会自动重新加载，使开发快速且迭代。
