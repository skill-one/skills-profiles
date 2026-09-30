---
name: fullstack-dev
description: '全栈后端架构与前后端集成指南。

  触发条件：构建全栈应用、创建带前端的后端REST API、搭建后端服务、构建待办事项应用、构建CRUD应用、构建实时应用、构建聊天应用、Express + React、Next.js API、Node.js后端、Python后端、Go后端、设计服务层、实现错误处理、管理配置/认证、设置API客户端、实现认证流程、处理文件上传、添加实时功能（SSE/WebSocket）、为生产环境加固。

  不触发条件：纯前端UI工作、纯CSS/样式、仅数据库模式。'
---

# 全栈开发实践

## 强制工作流程 — 按顺序执行以下步骤

**当此技能被触发时，您必须在编写任何代码之前遵循此工作流程。**

### 第 0 步：收集需求

在搭建任何东西之前，要求用户澄清（或从上下文中推断）：

1. **技术栈**：后端和前端的语言/框架（例如，Express + React，Django + Vue，Go + HTMX）
2. **服务类型**：仅 API、全栈单体还是微服务？
3. **数据库**：SQL（PostgreSQL、SQLite、MySQL）还是 NoSQL（MongoDB、Redis）？
4. **集成方式**：REST、GraphQL、tRPC 还是 gRPC？
5. **实时功能**：需要吗？如果需要——SSE、WebSocket 或轮询？
6. **认证**：需要吗？如果需要——JWT、会话、OAuth 或第三方（Clerk、Auth.js）？

如果用户已经在请求中指定了这些，则跳过询问并继续。

### 第 1 步：架构决策

在编码之前，根据需求做出并声明以下决策：

| 决策 | 选项 | 参考 |
|------|------|------|
| 项目结构 | 特性优先（推荐） vs 层次优先 | [第 1 节](#1-项目结构--层次化关键) |
| API 客户端方法 | 类型化请求 / React Query / tRPC / OpenAPI 代码生成 | [第 5 节](#5-api客户端模式中等) |
| 认证策略 | JWT + 刷新 / 会话 / 第三方 | [第 6 节](#6-认证--中间件高) |
| 实时方法 | 轮询 / SSE / WebSocket | [第 11 节](#11-实时模式中等) |
| 错误处理 | 类型化错误层次 + 全局处理器 | [第 3 节](#3-错误处理--弹性高) |

简要解释每个选择（每个决策 1 句话）。

### 第 2 步：使用清单搭建

使用以下适当的清单。确保所有勾选的项目都已实现——不要跳过任何项目。

### 第 3 步：实现以下模式

按照本文件中的模式编写代码。在实现每个部分时参考具体章节。

### 第 4 步：测试和验证

在实现后，运行以下检查，然后再声称完成：

1. **构建检查**：确保后端和前端都能无错误地编译
   ```bash
   # 后端
   cd server && npm run build
   # 前端
   cd client && npm run build
   ```
2. **启动和冒烟测试**：启动服务器，验证关键端点返回预期响应
   ```bash
   # 启动服务器，然后测试
   curl http://localhost:3000/health
   curl http://localhost:3000/api/<资源>
   ```
3. **集成检查**：验证前端可以连接到后端（CORS、API 基础 URL、认证流程）
4. **实时检查**（如果适用）：打开两个浏览器标签页，验证更改是否同步

如果任何检查失败，在继续之前修复问题。

### 第 5 步：交接摘要

向用户提供简要摘要：

- **已构建内容**：已实现功能和端点列表
- **如何运行**：启动后端和前端的精确命令
- **缺失内容 / 下一步**：任何推迟的项目、已知限制或建议的改进
- **关键文件**：用户应了解的最重要文件列表

---

## 范围

**使用此技能的情况：**
- 构建全栈应用程序（后端 + 前端）
- 搭建新的后端服务或 API
- 设计服务层和模块边界
- 实现数据库访问、缓存或后台作业
- 编写错误处理、日志记录或配置管理
- 审查后端代码以发现架构问题
- 生产环境加固
- 设置 API 客户端、认证流程、文件上传或实时功能

**不适用情况：**
- 纯前端/UI 问题（使用您的前端框架文档）
- 没有后端上下文的纯数据库模式设计

---

## 快速入门 — 新后端服务清单

- [ ] 使用 **特性优先** 结构搭建项目
- [ ] 配置 **集中化**，环境变量在启动时 **验证**（快速失败）
- [ ] 定义 **类型化错误层次**（不是通用 `Error`）
- [ ] **全局错误处理器** 中间件
- [ ] **结构化 JSON 日志**，带有请求 ID 传播
- [ ] 数据库：**迁移** 设置，**连接池** 配置
- [ ] 所有端点上的 **输入验证**（Zod / Pydantic / Go 验证器）
- [ ] **认证中间件** 已就位
- [ ] **健康检查** 端点 (`/health`, `/ready`)
- [ ] **优雅关闭** 处理（SIGTERM）
- [ ] **CORS** 配置（明确来源，不是 `*`）
- [ ] **安全头部**（helmet 或等效）
- [ ] 提交 `.env.example`（无真实密钥）

## 快速入门 — 前端-后端集成清单

- [ ] **API 客户端** 配置（类型化请求包装器、React Query、tRPC 或 OpenAPI 生成的）
- [ ] **基础 URL** 从环境变量（不是硬编码）
- [ ] **认证令牌** 自动附加到请求（拦截器 / 中间件）
- [ ] **错误处理** — API 错误映射到用户界面消息
- [ ] **加载状态** 处理（骨架屏/加载器，不是空白屏幕）
- [ ] **类型安全** 跨边界（共享类型、OpenAPI 或 tRPC）
- [ ] **CORS** 配置，明确来源（生产中不是 `*`）
- [ ] **刷新令牌** 流程实现（httpOnly cookie + 透明 401 重试）

---

## 快速导航

| 需要执行… | 跳转到 |
|----------|-------|
| 组织项目文件夹 | [1. 项目结构](#1-项目结构--层次化关键) |
| 管理 config + 密钥 | [2. 配置](#2-配置--环境关键) |
| 正确处理错误 | [3. 错误处理](#3-错误处理--弹性高) |
| 编写数据库代码 | [4. 数据库访问模式](#4-数据库访问模式高) |
| 从前端设置 API 客户端 | [5. API 客户端模式](#5-api客户端模式中等) |
| 添加认证中间件 | [6. 认证 & 中间件](#6-认证--中间件高) |
| 设置日志记录 | [7. 日志记录 & 可观察性](#7-日志记录--可观察性中等高) |
| 添加后台作业 | [8. 后台作业](#8-后台作业--异步中等) |
| 实现缓存 | [9. 缓存](#9-缓存模式中等) |
| 文件上传（预签名 URL、multipart） | [10. 文件上传模式](#10-文件上传模式中等) |
| 添加实时功能（SSE、WebSocket） | [11. 实时模式](#11-实时模式中等) |
| 在前端 UI 中处理 API 错误 | [12. 跨边界错误处理](#12-跨边界错误处理中等) |
| 生产环境加固 | [13. 生产环境加固](#13-生产环境加固中等) |
| 设计 API 端点 | [API 设计](references/api-design.md) |
| 设计数据库模式 | [数据库模式](references/db-schema.md) |
| 认证流程（JWT、刷新、Next.js SSR、RBAC） | [references/auth-flow.md](references/auth-flow.md) |
| CORS、环境变量、环境管理 | [references/environment-management.md](references/environment-management.md) |

---

## 核心原则（7 条铁律）

```
1. ✅ 按特性组织，而不是按技术层次
2. ✅ 控制器不包含业务逻辑
3. ✅ 服务不导入 HTTP 请求/响应类型
4. ✅ 所有配置来自环境变量，在启动时验证，快速失败
5. ✅ 每个错误都是类型化的，记录的，并返回一致的格式
6. ✅ 所有输入在边界处验证——不要信任来自客户端的任何内容
7. ✅ 结构化 JSON 日志，带有请求 ID——不是 `console.log`
```

---

## 1. 项目结构 & 层次（关键）

### 特性优先组织

```
✅ 特性优先                    ❌ 层次优先
src/                                src/
  orders/                             控制器/
    order.controller.ts                 order.controller.ts
    order.service.ts                    user.controller.ts
    order.repository.ts               服务/
    order.dto.ts                        order.service.ts
    order.test.ts                       user.service.ts
  users/                              仓库/
    user.controller.ts                  ...
    user.service.ts
  shared/
    database/
    中间件/
```

### 三层架构

```
控制器 (HTTP) → 服务 (业务逻辑) → 仓库 (数据访问)
```

| 层级 | 责任 | ❌ 从不 |
|-------|------|---------|
| 控制器 | 解析请求、验证、调用服务、格式化响应 | 业务逻辑、DB 查询 |
| 服务 | 业务规则、编排、事务管理 | HTTP 类型（请求/响应）、直接 DB |
| 仓库 | 数据库查询、外部 API 调用 | 业务逻辑、HTTP 类型 |

### 依赖注入（所有语言）

**TypeScript:**
```typescript
class OrderService {
  constructor(
    private readonly orderRepo: OrderRepository,    // ✅ 注入接口
    private readonly emailService: EmailService,
  ) {}
}
```

**Python:**
```python
class OrderService:
    def __init__(self, order_repo: OrderRepository, email_service: EmailService):
        self.order_repo = order_repo                 # ✅ 注入
        self.email_service = email_service
```

**Go:**
```go
type OrderService struct {
    orderRepo    OrderRepository                      // ✅ 接口
    emailService EmailService
}

func NewOrderService(repo OrderRepository, email EmailService) *OrderService {
    return &OrderService{orderRepo: repo, emailService: email}
}
```

---

## 2. 配置 & 环境（关键）

### 集中化、类型化、快速失败

**TypeScript:**
```typescript
const config = {
  port: parseInt(process.env.PORT || '3000', 10),
  database: { url: requiredEnv('DATABASE_URL'), poolSize: intEnv('DB_POOL_SIZE', 10) },
  auth: { jwtSecret: requiredEnv('JWT_SECRET'), expiresIn: process.env.JWT_EXPIRES_IN || '1h' },
} as const;

function requiredEnv(name: string): string {
  const value = process.env[name];
  if (!value) throw new Error(`Missing required env var: ${name}`);  // 快速失败
  return value;
}
```

**Python:**
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str                        # 必须的——没有它应用程序不会启动
    jwt_secret: str                          # 必须的
    port: int = 3000                         # 可选的，带默认值
    db_pool_size: int = 10
    class Config:
        env_file = ".env"

settings = Settings()                        # 如果 DATABASE_URL 缺失，会快速失败
```

### 规则

```
✅ 所有配置通过环境变量（十二因素）
✅ 在启动时验证必需的变量——快速失败
✅ 在配置层进行类型转换，而不是在用法位置
✅ 提交 .env.example 带有虚拟值

❌ 从不硬编码密钥、URL 或凭证
❌ 从不提交 .env 文件
❌ 从不将 process.env / os.environ 散布在整个代码中
```

---

## 3. 错误处理 & 弹性（高）

### 类型化错误层次

```typescript
// 基础（TypeScript）
class AppError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly statusCode: number,
    public readonly isOperational: boolean = true,
  ) { super(message); }
}
class NotFoundError extends AppError {
  constructor(resource: string, id: string) {
    super(`${resource} not found: ${id}`, 'NOT_FOUND', 404);
  }
}
class ValidationError extends AppError {
  constructor(public readonly errors: FieldError[]) {
    super('Validation failed', 'VALIDATION_ERROR', 422);
  }
}
```

```python
# 基础（Python）
class AppError(Exception):
    def __init__(self, message: str, code: str, status_code: int):
        self.message, self.code, self.status_code = message, code, status_code

class NotFoundError(AppError):
    def __init__(self, resource: str, id: str):
        super().__init__(f"{resource} not found: {id}", "NOT_FOUND", 404)
```

### 全局错误处理器

```typescript
// TypeScript (Express)
app.use((err, req, res, next) => {
  if (err instanceof AppError && err.isOperational) {
    return res.status(err.statusCode).json({
      title: err.code, status: err.statusCode,
      detail: err.message, request_id: req.id,
    });
  }
  logger.error('Unexpected error', { error: err.message, stack: err.stack, request_id: req.id });
  res.status(500).json({ title: 'Internal Error', status: 500, request_id: req.id });
});
```

### 规则

```
✅ 类型化、特定领域的错误类
✅ 全局错误处理器捕获所有内容
✅ 操作性错误→结构化响应
✅ 编程错误→记录+通用 500
✅ 使用指数退避重试临时失败

❌ 从不无声地捕获并忽略错误
❌ 从不向客户端返回堆栈跟踪
❌ 从不抛出通用 Error('something')
```

---

## 4. 数据库访问模式（高）

### 永远使用迁移

```bash
# TypeScript (Prisma)           # Python (Alembic)              # Go (golang-migrate)
npx prisma migrate dev          alembic revision --autogenerate  migrate -source file://migrations
npx prisma migrate deploy       alembic upgrade head             migrate -database $DB up
```

```
✅ 通过迁移更改模式，永远不手动 SQL
✅ 迁移必须是可逆的
✅ 在生产前审查迁移 SQL
❌ 从不手动修改生产模式
```

### 防止 N+1 问题

```typescript
// ❌ N+1: 1 查询 + N 查询
const orders = await db.order.findMany();
for (const o of orders) { o.items = await db.item.findMany({ where: { orderId: o.id } }); }

// ✅ 单个 JOIN 查询
const orders = await db.order.findMany({ include: { items: true } });
```

### 事务用于多步骤写入

```typescript
await db.$transaction(async (tx) => {
  const order = await tx.order.create({ data: orderData });
  await tx.inventory.decrement({ productId, quantity });
  await tx.payment.create({ orderId: order.id, amount });
});
```

### 连接池

池大小 = `(CPU 核心数 × 2) + 磁盘数量`（从 10-20 开始）。始终设置连接超时。使用 PgBouncer 用于无服务器环境。

---

## 5. API 客户端模式（中等）

前端和后端之间的“粘合层”。选择适合您团队和栈的方法。

### 选项 A：类型化请求包装器（简单，无依赖）

```typescript
// lib/api-client.ts
const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001';

class ApiError extends Error {
  constructor(public status: number, public body: any) {
    super(body?.detail || body?.message || `API error ${status}`);
  }
}

async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getAuthToken();  // 从 cookie / 内存 / 上下文

  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });

  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new ApiError(res.status, body);
  }

  if (res.status === 204) return undefined as T;
  return res.json();
}

export const apiClient = {
  get: <T>(path: string) => api<T>(path),
  post: <T>(path: string, data: unknown) => api<T>(path, { method: 'POST', body: JSON.stringify(data) }),
  put: <T>(path: string, data: unknown) => api<T>(path, { method: 'PUT', body: JSON.stringify(data) }),
  patch: <T>(path: string, data: unknown) => api<T>(path, { method: 'PATCH', body: JSON.stringify(data) }),
  delete: <T>(path: string) => api<T>(path, { method: 'DELETE' }),
};
```

### 选项 B：React Query + 类型化客户端（React 推荐使用）

```typescript
// hooks/use-orders.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';

interface Order { id: string; total: number; status: string; }
interface CreateOrderInput { items: { productId: string; quantity: number }[] }

export function useOrders() {
  return useQuery({
    queryKey: ['orders'],
    queryFn: () => apiClient.get<{ data: Order[] }>('/api/orders'),
    staleTime: 1000 * 60,  // 1 min
  });
}

export function useCreateOrder() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: CreateOrderInput) =>
      apiClient.post<{ data: Order }>('/api/orders', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['orders'] });
    },
  });
}

// Usage in component:
function OrdersPage() {
  const { data, isLoading, error } = useOrders();
  const createOrder = useCreateOrder();
  if (isLoading) return <Skeleton />;
  if (error) return <ErrorBanner error={error} />;
  // ...
}
```

### Option C: tRPC (Same Team Owns Both Sides)

```typescript
// server: trpc/router.ts
export const appRouter = router({
  orders: router({
    list: publicProcedure.query(async () => {
      return db.order.findMany({ include: { items: true } });
    }),
    create: protectedProcedure
      .input(z.object({ items: z.array(orderItemSchema) }))
      .mutation(async ({ input, ctx }) => {
        return orderService.create(ctx.user.id, input);
      }),
  }),
});
export type AppRouter = typeof appRouter;

// client: automatic type safety, no code generation
const { data } = trpc.orders.list.useQuery();
const createOrder = trpc.orders.create.useMutation();
```

### Option D: OpenAPI Generated Client (Public / Multi-Consumer APIs)

```bash
npx openapi-typescript-codegen \
  --input http://localhost:3001/api/openapi.json \
  --output src/generated/api \
  --client axios
```

### Decision: Which API Client?

| Approach | When | Type Safety | Effort |
|----------|------|-------------|--------|
| Typed fetch wrapper | Simple apps, small teams | Manual types | Low |
| React Query + fetch | React apps, server state | Manual types | Medium |
| tRPC | Same team, TypeScript both sides | Automatic | Low |
| OpenAPI generated | Public API, multi-consumer | Automatic | Medium |
| GraphQL codegen | GraphQL APIs | Automatic | Medium |

---

## 6. Authentication & Middleware (HIGH)

> **Full reference:** [references/auth-flow.md](references/auth-flow.md) — JWT bearer flow, automatic token refresh, Next.js server-side auth, RBAC pattern, backend middleware order.

### Standard Middleware Order

```
Request → 1.RequestID → 2.Logging → 3.CORS → 4.RateLimit → 5.BodyParse
       → 6.Auth → 7.Authz → 8.Validation → 9.Handler → 10.ErrorHandler → Response
```

### JWT Rules

```
✅ Short expiry access token (15min) + refresh token (server-stored)
✅ Minimal claims: userId, roles (not entire user object)
✅ Rotate signing keys periodically

❌ Never store tokens in localStorage (XSS risk)
❌ Never pass tokens in URL query params
```

### RBAC Pattern

```typescript
function authorize(...roles: Role[]) {
  return (req, res, next) => {
    if (!req.user) throw new UnauthorizedError();
    if (!roles.some(r => req.user.roles.includes(r))) throw new ForbiddenError();
    next();
  };
}
router.delete('/users/:id', authenticate, authorize('admin'), deleteUser);
```

### Auth Token Automatic Refresh

```typescript
// lib/api-client.ts — transparent refresh on 401
async function apiWithRefresh<T>(path: string, options: RequestInit = {}): Promise<T> {
  try {
    return await api<T>(path, options);
  } catch (err) {
    if (err instanceof ApiError && err.status === 401) {
      const refreshed = await api<{ accessToken: string }>('/api/auth/refresh', {
        method: 'POST',
        credentials: 'include',  // send httpOnly cookie
      });
      setAuthToken(refreshed.accessToken);
      return api<T>(path, options);  // retry
    }
    throw err;
  }
}
```

---

## 7. Logging & Observability (MEDIUM-HIGH)

### Structured JSON Logging

```typescript
// ✅ Structured — parseable, filterable, alertable
logger.info('Order created', {
  orderId: order.id, userId: user.id, total: order.total,
  items: order.items.length, duration_ms: Date.now() - startTime,
});
// Output: {"level":"info","msg":"Order created","orderId":"ord_123",...}

// ❌ Unstructured — useless at scale
console.log(`Order created for user ${user.id} with total ${order.total}`);
```

### Log Levels

| Level | When | Production? |
|-------|------|------------|
| error | Requires immediate attention | ✅ Always |
| warn | Unexpected but handled | ✅ Always |
| info | Normal operations, audit trail | ✅ Always |
| debug | Dev troubleshooting | ❌ Dev only |

### Rules

```
✅ Request ID in every log entry (propagated via middleware)
✅ Log at layer boundaries (request in, response out, external call)
❌ Never log passwords, tokens, PII, or secrets
❌ Never use console.log in production code
```

---

## 8. Background Jobs & Async (MEDIUM)

### Rules

```
✅ All jobs must be IDEMPOTENT (same job running twice = same result)
✅ Failed jobs → retry (max 3) → dead letter queue → alert
✅ Workers run as SEPARATE processes (not threads in API server)

❌ Never put long-running tasks in request handlers
❌ Never assume job runs exactly once
```

### Idempotent Job Pattern

```typescript
async function processPayment(data: { orderId: string }) {
  const order = await orderRepo.findById(data.orderId);
  if (order.paymentStatus === 'completed') return;  // already processed
  await paymentGateway.charge(order);
  await orderRepo.updatePaymentStatus(order.id, 'completed');
}
```

---

## 9. Caching Patterns (MEDIUM)

### Cache-Aside (Lazy Loading)

```typescript
async function getUser(id: string): Promise<User> {
  const cached = await redis.get(`user:${id}`);
  if (cached) return JSON.parse(cached);

  const user = await userRepo.findById(id);
  if (!user) throw new NotFoundError('User', id);

  await redis.set(`user:${id}`, JSON.stringify(user), 'EX', 900);  // 15min TTL
  return user;
}
```

### Rules

```
✅ ALWAYS set TTL — never cache without expiry
✅ Invalidate on write (delete cache key after update)
✅ Use cache for reads, never for authoritative state

❌ Never cache without TTL (stale data is worse than slow data)
```

| Data Type | Suggested TTL |
|-----------|---------------|
| User profile | 5-15 min |
| Product catalog | 1-5 min |
| Config / feature flags | 30-60 sec |
| Session | Match session duration |

---

## 10. File Upload Patterns (MEDIUM)

### Option A: Presigned URL (Recommended for Large Files)

```
Client → GET /api/uploads/presign?filename=photo.jpg&type=image/jpeg
Server → { uploadUrl: "https://s3.../presigned", fileKey: "uploads/abc123.jpg" }
Client → PUT uploadUrl (direct to S3, bypasses your server)
Client → POST /api/photos { fileKey: "uploads/abc123.jpg" }  (save reference)
```

**Backend:**
```typescript
app.get('/api/uploads/presign', authenticate, async (req, res) => {
  const { filename, type } = req.query;
  const key = `uploads/${crypto.randomUUID()}-${filename}`;
  const url = await s3.getSignedUrl('putObject', {
    Bucket: process.env.S3_BUCKET, Key: key,
    ContentType: type, Expires: 300,  // 5 min
  });
  res.json({ uploadUrl: url, fileKey: key });
});
```

**Frontend:**
```typescript
async function uploadFile(file: File) {
  const { uploadUrl, fileKey } = await apiClient.get<PresignResponse>(
    `/api/uploads/presign?filename=${file.name}&type=${file.type}`
  );
  await fetch(uploadUrl, { method: 'PUT', body: file, headers: { 'Content-Type': file.type } });
  return apiClient.post('/api/photos', { fileKey });
}
```

### Option B: Multipart (Small Files < 10MB)

```typescript
// Frontend
const formData = new FormData();
formData.append('file', file);
formData.append('description', 'Profile photo');
const res = await fetch('/api/upload', { method: 'POST', body: formData });
// Note: do NOT set Content-Type header — browser sets boundary automatically
```

### Decision

| Method | File Size | Server Load | Complexity |
|--------|-----------|-------------|------------|
| Presigned URL | Any (recommended > 5MB) | None (direct to storage) | Medium |
| Multipart | < 10MB | High (streams through server) | Low |
| Chunked / Resumable | > 100MB | Medium | High |

---

## 11. Real-Time Patterns (MEDIUM)

### Option A: Server-Sent Events (SSE) — One-Way Server → Client

Best for: notifications, live feeds, streaming AI responses.

**Backend (Express):**
```typescript
app.get('/api/events', authenticate, (req, res) => {
  res.writeHead(200, {
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    Connection: 'keep-alive',
  });
  const send = (event: string, data: unknown) => {
    res.write(`event: ${event}\ndata: ${JSON.stringify(data)}\n\n`);
  };
  const unsubscribe = eventBus.subscribe(req.user.id, (event) => {
    send(event.type, event.payload);
  });
  req.on('close', () => unsubscribe());
});
```

**Frontend:**
```typescript
function useServerEvents(userId: string) {
  useEffect(() => {
    const source = new EventSource(`/api/events?userId=${userId}`);
    source.addEventListener('notification', (e) => {
      showToast(JSON.parse(e.data).message);
    });
    source.onerror = () => { source.close(); setTimeout(() => /* reconnect */, 3000); };
    return () => source.close();
  }, [userId]);
}
```

### Option B: WebSocket — Bidirectional

Best for: chat, collaborative editing, gaming.

**Backend (ws library):**
```typescript
import { WebSocketServer } from 'ws';
const wss = new WebSocketServer({ server: httpServer, path: '/ws' });
wss.on('connection', (ws, req) => {
  const userId = authenticateWs(req);
  if (!userId) { ws.close(4001, 'Unauthorized'); return; }
  ws.on('message', (raw) => handleMessage(userId, JSON.parse(raw.toString())));
  ws.on('close', () => cleanupUser(userId));
  const interval = setInterval(() => ws.ping(), 30000);
  ws.on('pong', () => { /* alive */ });
  ws.on('close', () => clearInterval(interval));
});
```

**Frontend:**
```typescript
function useWebSocket(url: string) {
  const [ws, setWs] = useState<WebSocket | null>(null);
  useEffect(() => {
    const socket = new WebSocket(url);
    socket.onopen = () => setWs(socket);
    socket.onclose = () => setTimeout(() => /* reconnect */, 3000);
    return () => socket.close();
  }, [url]);
  const send = useCallback((data: unknown) => ws?.send(JSON.stringify(data)), [ws]);
  return { ws, send };
}
```

### Option C: Polling (Simplest, No Infrastructure)

```typescript
function useOrderStatus(orderId: string) {
  return useQuery({
    queryKey: ['order-status', orderId],
    queryFn: () => apiClient.get<Order>(`/api/orders/${orderId}`),
    refetchInterval: (query) => {
      if (query.state.data?.status === 'completed') return false;
      return 5000;
    },
  });
}
```

### Decision

| Method | Direction | Complexity | When |
|--------|-----------|------------|------|
| Polling | Client → Server | Low | Simple status checks, < 10 clients |
| SSE | Server → Client | Medium | Notifications, feeds, AI streaming |
| WebSocket | Bidirectional | High | Chat, collaboration, gaming |

---

## 12. Cross-Boundary Error Handling (MEDIUM)

### API Error → User-Facing Message

```typescript
// lib/error-handler.ts
export function getErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    switch (error.status) {
      case 401: return 'Please log in to continue.';
      case 403: return 'You don\'t have permission to do this.';
      case 404: return 'The item you\'re looking for doesn\'t exist.';
      case 409: return 'This conflicts with an existing item.';
      case 422:
        const fields = error.body?.errors;
        if (fields?.length) return fields.map((f: any) => f.message).join('. ');
        return 'Please check your input.';
      case 429: return 'Too many requests. Please wait a moment.';
      default: return 'Something went wrong. Please try again.';
    }
  }
  if (error instanceof TypeError && error.message === 'Failed to fetch') {
    return 'Cannot connect to server. Check your internet connection.';
  }
  return 'An unexpected error occurred.';
}
```

### React Query Global Error Handler

```typescript
const queryClient = new QueryClient({
  defaultOptions: {
    mutations: { onError: (error) => toast.error(getErrorMessage(error)) },
    queries: {
      retry: (failureCount, error) => {
        if (error instanceof ApiError && error.status < 500) return false;
        return failureCount < 3;
      },
    },
  },
});
```

### Rules

```
✅ Map every API error code to a human-readable message
✅ Show field-level validation errors next to form inputs
✅ Auto-retry on 5xx (max 3, with backoff), never on 4xx
✅ Redirect to login on 401 (after refresh attempt fails)
✅ Show "offline" banner when fetch fails with TypeError

❌ Never show raw API error messages to users ("NullPointerException")
❌ Never silently swallow errors (show toast or log)
❌ Never retry 4xx errors (client is wrong, retrying won't help)
```

### Integration Decision Tree

```
Same team owns frontend + backend?
│
├─ YES, both TypeScript
│   └─ tRPC (end-to-end type safety, zero codegen)
│
├─ YES, different languages
│   └─ OpenAPI spec → generated client (type safety via codegen)
│
├─ NO, public API
│   └─ REST + OpenAPI → generated SDKs for consumers
│
└─ Complex data needs, multiple frontends
    └─ GraphQL + codegen (flexible queries per client)

Real-time needed?
│
├─ Server → Client only (notifications, feeds, AI streaming)
│   └─ SSE (simplest, auto-reconnect, works through proxies)
│
├─ Bidirectional (chat, collaboration)
│   └─ WebSocket (need heartbeat + reconnection logic)
│
└─ Simple status polling (< 10 clients)
    └─ React Query refetchInterval (no infrastructure needed)
```

---

## 13. Production Hardening (MEDIUM)

### Health Checks

```typescript
app.get('/health', (req, res) => res.json({ status: 'ok' }));           // liveness
app.get('/ready', async (req, res) => {                                   // readiness
  const checks = {
    database: await checkDb(), redis: await checkRedis(), 
  };
  const ok = Object.values(checks).every(c => c.status === 'ok');
  res.status(ok ? 200 : 503).json({ status: ok ? 'ok' : 'degraded', checks });
});
```

### Graceful Shutdown

```typescript
process.on('SIGTERM', async () => {
  logger.info('SIGTERM received');
  server.close();              // stop new connections
  await drainConnections();    // finish in-flight
  await closeDatabase();
  process.exit(0);
});
```

### Security Checklist

```
✅ CORS: explicit origins (never '*' in production)
✅ Security headers (helmet / equivalent)
✅ Rate limiting on public endpoints
✅ Input validation on ALL endpoints (trust nothing)
✅ HTTPS enforced
❌ Never expose internal errors to clients
```

---

## Anti-Patterns
```

| # | ❌ 不要 | ✅ 应该这样做 |
|---|---------|--------------|
| 1 | 在路由/控制器中写业务逻辑 | 移动到服务层 |
| 2 | `process.env` 滥用 | 集中化类型化配置 |
| 3 | 用 `console.log` 做日志记录 | 结构化 JSON 日志记录器 |
| 4 | 通用 `Error('oops')` | 类型化错误层级 |
| 5 | 在控制器中直接调用数据库 | 仓库模式 |
| 6 | 没有输入验证 | 在边界处验证（Zod/Pydantic） |
| 7 | 沉默地捕获错误 | 记录并重新抛出或返回错误 |
| 8 | 没有健康检查端点 | `/health` + `/ready` |
| 9 | 硬编码配置/密钥 | 环境变量 |
| 10 | 没有优雅的关闭 | 正确处理 SIGTERM |
| 11 | 在前端硬编码 API URL | 环境变量 (`NEXT_PUBLIC_API_URL`) |
| 12 | 将 JWT 存储在 localStorage 中 | 内存 + httpOnly 刷新 cookie |
| 13 | 向用户展示原始 API 错误 | 映射为人类可读的消息 |
| 14 | 重试 4xx 错误 | 仅重试 5xx（服务器错误） |
| 15 | 跳过加载状态 | 获取时显示骨架屏/加载动画 |
| 16 | 通过 API 服务器上传大文件 | 预签名 URL → 直接指向 S3 |
| 17 | 轮询实时数据 | SSE 或 WebSocket |
| 18 | 前端和后端重复类型定义 | 共享类型，tRPC 或 OpenAPI 代码生成 |

---

## 常见问题

### 问题 1: "这个业务规则应该放在哪里？"

**规则：** 如果它涉及 HTTP（请求解析、状态码、头部）→ 控制器。如果它涉及业务决策（定价、权限、规则）→ 服务。如果它触及数据库 → 仓库。

### 问题 2: "服务变得太大"

**症状：** 一个服务文件 > 500 行，包含 20+ 方法。

**解决方法：** 按子域拆分。`OrderService` → `OrderCreationService` + `OrderFulfillmentService` + `OrderQueryService`。每个专注于一个工作流。

### 问题 3: "测试因为访问数据库而变慢"

**解决方法：** 单元测试模拟仓库层（快速）。集成测试使用测试容器或事务回滚（真实数据库，仍然快速）。永远不要在集成测试中模拟服务层。

---

## 参考文档

这项技能包括针对专业主题的深入参考。当你需要详细指导时，请阅读相关参考文档。

| 需要… | 参考文档 |
|----------|-----------|
| 编写后端测试（单元、集成、端到端、契约、性能） | [references/testing-strategy.md](references/testing-strategy.md) |
| 部署前验证发布（6-门禁清单） | [references/release-checklist.md](references/release-checklist.md) |
| 选择技术栈（语言、框架、数据库、基础设施） | [references/technology-selection.md](references/technology-selection.md) |
| 使用 Django / DRF 构建（模型、视图、序列化器、管理后台） | [references/django-best-practices.md](references/django-best-practices.md) |
| 设计 REST/GraphQL/gRPC 端点（URL、状态码、分页） | [references/api-design.md](references/api-design.md) |
| 设计数据库模式、索引、迁移、多租户 | [references/db-schema.md](references/db-schema.md) |
| 认证流程（JWT 带宽、令牌刷新、Next.js SSR、RBAC、中间件顺序） | [references/auth-flow.md](references/auth-flow.md) |
| CORS 配置、按环境设置环境变量、常见 CORS 问题 | [references/environment-management.md](references/environment-management.md) |
