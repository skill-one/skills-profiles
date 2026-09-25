# EAS Hosting

> **EAS服务 - 适用费用。** EAS Hosting是一个付费的Expo应用服务产品，具有免费层级限制；生产部署使用您计划的请求和带宽配额。请参阅https://expo.dev/pricing。API路由的创建和Web包的导出是免费且开源的，您可以选择托管导出的服务器输出而不是使用EAS Hosting。

EAS Hosting将您的Expo **Web应用和API路由**部署到Expo管理的边缘（Cloudflare Workers）。使用`npx expo export -p web`导出Web包，并使用`eas deploy`发送它——同一个命令会部署与之捆绑的任何Expo Router API路由。本技能涵盖了部署网站、创建API路由和托管运行时；请参阅下方的部署部分了解部署工作流程。

## 何时使用API路由

当您需要时使用API路由：

- **服务器端密钥** — API密钥、数据库凭证或永远不会到达客户端的令牌
- **数据库操作** — 不应公开的直接数据库查询
- **第三方API代理** — 调用外部服务时隐藏API密钥（OpenAI、Stripe等）
- **服务器端验证** — 在数据库写入之前验证数据
- **Webhook端点** — 接收来自Stripe或GitHub等服务的回调
- **速率限制** — 在服务器级别控制访问
- **重型计算** — 将在移动设备上缓慢的处理过程卸载

## 何时不使用API路由

避免使用API路由：

- **数据已经是公开的** — 使用直接fetch公共API
- **不需要密钥** — 静态数据或客户端安全的操作
- **需要实时更新** — 使用WebSockets或Supabase Realtime等服务
- **简单的CRUD** — 考虑使用Firebase、Supabase或Convex进行托管后端
- **文件上传** — 使用直接到存储的上传（S3预签名URL、Cloudflare R2）
- **仅身份验证** — 使用Clerk、Auth0或Firebase Auth

## 文件结构

API路由位于`app`目录下，以`+api.ts`后缀：

```
app/
  api/
    hello+api.ts          → GET /api/hello
    users+api.ts          → /api/users
    users/[id]+api.ts     → /api/users/:id
  (tabs)/
    index.tsx
```

## 基本API路由

```ts
// app/api/hello+api.ts
export function GET(request: Request) {
  return Response.json({ message: "来自Expo的问候！" });
}
```

## HTTP方法

为每个HTTP方法导出命名函数：

```ts
// app/api/items+api.ts
export function GET(request: Request) {
  return Response.json({ items: [] });
}

export async function POST(request: Request) {
  const body = await request.json();
  return Response.json({ created: body }, { status: 201 });
}

export async function PUT(request: Request) {
  const body = await request.json();
  return Response.json({ updated: body });
}

export async function DELETE(request: Request) {
  return new Response(null, { status: 204 });
}
```

## 动态路由

```ts
// app/api/users/[id]+api.ts
export function GET(request: Request, { id }: { id: string }) {
  return Response.json({ userId: id });
}
```

## 请求处理

### 查询参数

```ts
export function GET(request: Request) {
  const url = new URL(request.url);
  const page = url.searchParams.get("page") ?? "1";
  const limit = url.searchParams.get("limit") ?? "10";

  return Response.json({ page, limit });
}
```

### 标头

```ts
export function GET(request: Request) {
  const auth = request.headers.get("Authorization");

  if (!auth) {
    return Response.json({ error: "未授权" }, { status: 401 });
  }

  return Response.json({ authenticated: true });
}
```

### JSON正文

```ts
export async function POST(request: Request) {
  const { email, password } = await request.json();

  if (!email || !password) {
    return Response.json({ error: "缺少字段" }, { status: 400 });
  }

  return Response.json({ success: true });
}
```

## 环境变量

使用`process.env`用于服务器端密钥：

```ts
// app/api/ai+api.ts
export async function POST(request: Request) {
  const { prompt } = await request.json();

  const response = await fetch("https://api.openai.com/v1/chat/completions", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${process.env.OPENAI_API_KEY}`,
    },
    body: JSON.stringify({
      model: "gpt-4",
      messages: [{ role: "user", content: prompt }],
    }),
  });

  const data = await response.json();
  return Response.json(data);
}
```

设置环境变量：

- **本地**：创建`.env`文件（切勿提交）
- **EAS Hosting**：使用`eas env:create`或Expo控制面板

## CORS标头

为Web客户端添加CORS：

```ts
const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization",
};

export function OPTIONS() {
  return new Response(null, { headers: corsHeaders });
}

export function GET() {
  return Response.json({ data: "value" }, { headers: corsHeaders });
}
```

## 错误处理

```ts
export async function POST(request: Request) {
  try {
    const body = await request.json();
    // 处理...
    return Response.json({ success: true });
  } catch (error) {
    console.error("API错误:", error);
    return Response.json({ error: "内部服务器错误" }, { status: 500 });
  }
}
```

## 本地测试

使用API路由启动开发服务器：

```bash
npx expo serve
```

这将在`http://localhost:8081`启动一个本地服务器，并支持完整的API路由。

使用curl测试：

```bash
curl http://localhost:8081/api/hello
curl -X POST http://localhost:8081/api/users -H "Content-Type: application/json" -d '{"name":"Test"}'
```

## 部署到EAS Hosting

### 前置条件

```bash
npm install -g eas-cli
eas login
```

### 部署

部署会发送您的Web包和任何Expo Router API路由——`eas deploy`会处理两者。导出会根据您是否有完整的网站、仅API路由的后端或两者而运行。

```bash
# 导出Web包（包括任何API路由）
npx expo export -p web

# 部署预览（PR风格的URL）
npx eas-cli@latest deploy

# 部署到生产
npx eas-cli@latest deploy --prod
```

所有内容都会部署到EAS Hosting（Cloudflare Workers）。

### 生产环境变量

```bash
# 创建一个密钥
eas env:create --name OPENAI_API_KEY --value sk-xxx --environment production

# 或者使用Expo控制面板
```

### 自定义域名

在`eas.json`中配置或使用Expo控制面板。

### 使用EAS Workflows自动部署

使用`type: deploy`工作流程在每次推送到main时部署网站（和API路由）：

`.eas/workflows/deploy.yml`

```yaml
name: Deploy

on:
  push:
    branches:
      - main

# https://docs.expo.dev/eas/workflows/syntax/#deploy
jobs:
  deploy_web:
    type: deploy
    params:
      prod: true
```

用于拉取请求预览的部署使用相同的工作流程类型，但`prod: false`：

```yaml
name: Web PR Preview

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  preview:
    type: deploy
    params:
      prod: false
```

要编写或验证工作流程YAML，请使用`eas-workflows`技能。

## EAS Hosting运行时（Cloudflare Workers）

API路由在Cloudflare Workers上运行。主要限制：

### 缺失/有限API

- **没有Node.js文件系统** — `fs`模块不可用
- **没有原生Node模块** — 使用Web API或polyfills
- **执行时间有限** — CPU密集型任务30秒超时
- **没有持久连接** — WebSocket需要Durable Objects
- **fetch可用** — 使用标准fetch进行HTTP请求

### 使用Web API替代

```ts
// 使用Web Crypto替代Node crypto
const hash = await crypto.subtle.digest(
  "SHA-256",
  new TextEncoder().encode("data")
);

// 使用fetch替代node-fetch
const response = await fetch("https://api.example.com");

// 使用Response/Request（已经可用）
return new Response(JSON.stringify(data), {
  headers: { "Content-Type": "application/json" },
});
```

### 数据库选项

由于文件系统不可用，请使用云数据库：

- **Cloudflare D1** — 边缘SQLite
- **Turso** — 分布式SQLite
- **PlanetScale** — 无服务器MySQL
- **Supabase** — 带REST API的Postgres
- **Neon** — 无服务器Postgres

使用Turso的示例：

```ts
// app/api/users+api.ts
import { createClient } from "@libsql/client/web";

const db = createClient({
  url: process.env.TURSO_URL!,
  authToken: process.env.TURSO_AUTH_TOKEN!,
});

export async function GET() {
  const result = await db.execute("SELECT * FROM users");
  return Response.json(result.rows);
}
```

## 从客户端调用API路由

```ts
// 从React Native组件
const response = await fetch("/api/hello");
const data = await response.json();

// 带正文
const response = await fetch("/api/users", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ name: "John" }),
});
```

## 常见模式

### 身份验证中间件

```ts
// utils/auth.ts
export async function requireAuth(request: Request) {
  const token = request.headers.get("Authorization")?.replace("Bearer ", "");

  if (!token) {
    throw new Response(JSON.stringify({ error: "未授权" }), {
      status: 401,
      headers: { "Content-Type": "application/json" },
    });
  }

  // 验证令牌...
  return { userId: "123" };
}

// app/api/protected+api.ts
import { requireAuth } from "../../utils/auth";

export async function GET(request: Request) {
  const { userId } = await requireAuth(request);
  return Response.json({ userId });
}
```

### 代理外部API

```ts
// app/api/weather+api.ts
export async function GET(request: Request) {
  const url = new URL(request.url);
  const city = url.searchParams.get("city");

  const response = await fetch(
    `https://api.weather.com/v1/current?city=${city}&key=${process.env.WEATHER_API_KEY}`
  );

  return Response.json(await response.json());
}
```

## 规则

- 永远不要在客户端代码中暴露API密钥或密钥
- 始终验证和清理用户输入
- 使用正确的HTTP状态码（200、201、400、401、404、500）
- 使用try/catch优雅地处理错误
- 保持API路由专注——每个端点一个职责
- 使用TypeScript进行类型安全
- 在服务器端记录错误以进行调试

## 提交反馈
如果您在本技能中遇到错误、误导性或过时的信息，请报告给Expo以改进：
```bash
npx --yes submit-expo-feedback@latest --category skills --subject "eas-hosting" "<可操作的反馈>"
```
仅在您有具体且可操作的内容时才提交。尽可能提供相关上下文。
如果AI代理反复失败或用户不得不接管Expo任务，加载expo-skill-feedback技能并遵循其eval-candidate工作流程，而不是重复使用上面的命令。
