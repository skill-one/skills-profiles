## 何时使用 API 路由

当您需要以下功能时，请使用 API 路由：

- **服务器端密钥** — API 密钥、数据库凭证或必须永不到达客户端的令牌
- **数据库操作** — 不应公开的直接数据库查询
- **第三方 API 代理** — 调用外部服务（如 OpenAI、Stripe 等）时隐藏 API 密钥
- **服务器端验证** — 在写入数据库之前验证数据
- **Webhook 端点** — 接收来自 Stripe 或 GitHub 等服务的回调
- **速率限制** — 在服务器级别控制访问
- **重型计算** — 将在移动设备上运行缓慢的处理卸载

## 何时不应使用 API 路由

当您不需要以下功能时，请避免使用 API 路由：

- **数据已经是公开的** — 直接使用公共 API 而不是
- **不需要密钥** — 静态数据或客户端安全的操作
- **需要实时更新** — 使用 WebSocket 或 Supabase Realtime 等服务
- **简单的 CRUD** — 考虑使用 Firebase、Supabase 或 Convex 管理后端
- **文件上传** — 使用直接存储上传（S3 预签名 URL、Cloudflare R2）
- **仅认证** — 使用 Clerk、Auth0 或 Firebase Auth

## 文件结构

API 路由位于 `app` 目录下，以 `+api.ts` 后缀：

```
app/
  api/
    hello+api.ts          → GET /api/hello
    users+api.ts          → /api/users
    users/[id]+api.ts     → /api/users/:id
  (tabs)/
    index.tsx
```

## 基本 API 路由

```ts
// app/api/hello+api.ts
export function GET(request: Request) {
  return Response.json({ message: "来自 Expo 的问候！" });
}
```

## HTTP 方法

为每个 HTTP 方法导出命名函数：

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

### JSON 正文

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

使用 `process.env` 存储服务器端密钥：

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

- **本地**：创建 `.env` 文件（切勿提交）
- **EAS Hosting**：使用 `eas env:create` 或 Expo 仪表板

## CORS 标头

为 Web 客户端添加 CORS：

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
  return Response.json({ data: "值" }, { headers: corsHeaders });
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
    console.error("API 错误:", error);
    return Response.json({ error: "内部服务器错误" }, { status: 500 });
  }
}
```

## 本地测试

使用 API 路由启动开发服务器：

```bash
npx expo serve
```

这将在 `http://localhost:8081` 启动本地服务器，并支持完整的 API 路由。

使用 curl 测试：

```bash
curl http://localhost:8081/api/hello
curl -X POST http://localhost:8081/api/users -H "Content-Type: application/json" -d '{"name":"Test"}'
```

## 部署到 EAS Hosting

### 前置条件

```bash
npm install -g eas-cli
eas login
```

### 部署

```bash
eas deploy
```

这将构建并部署您的 API 路由到 EAS Hosting（Cloudflare Workers）。

### 生产环境变量

```bash
# 创建密钥
eas env:create --name OPENAI_API_KEY --value sk-xxx --environment production

# 或使用 Expo 仪表板
```

### 自定义域名

在 `eas.json` 中配置或使用 Expo 仪表板。

## EAS Hosting 运行时（Cloudflare Workers）

API 路由在 Cloudflare Workers 上运行。关键限制：

### 缺失/有限 API

- **没有 Node.js 文件系统** — `fs` 模块不可用
- **没有原生 Node 模块** — 使用 Web API 或 polyfills
- **有限执行时间** — CPU 密集型任务 30 秒超时
- **没有持久连接** — WebSocket 需要持久对象
- **fetch 是可用的** — 使用标准 fetch 进行 HTTP 请求

### 使用 Web API 替代

```ts
// 使用 Web Crypto 替代 Node crypto
const hash = await crypto.subtle.digest(
  "SHA-256",
  new TextEncoder().encode("data")
);

// 使用 fetch 替代 node-fetch
const response = await fetch("https://api.example.com");

// 使用 Response/Request（已经可用）
return new Response(JSON.stringify(data), {
  headers: { "Content-Type": "application/json" },
});
```

### 数据库选项

由于文件系统不可用，请使用云数据库：

- **Cloudflare D1** — 边缘 SQLite
- **Turso** — 分布式 SQLite
- **PlanetScale** — 无服务器 MySQL
- **Supabase** — 带有 REST API 的 Postgres
- **Neon** — 无服务器 Postgres

使用 Turso 的示例：

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

## 从客户端调用 API 路由

```ts
// 从 React Native 组件
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

### 认证中间件

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

### 代理外部 API

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

- 绝对不要在客户端代码中暴露 API 密钥或密钥
- 始终验证和清理用户输入
- 使用正确的 HTTP 状态码（200、201、400、401、404、500）
- 使用 try/catch 优雅地处理错误
- 保持 API 路由专注 — 每个端点一个职责
- 使用 TypeScript 进行类型安全
- 在服务器端记录错误以进行调试
