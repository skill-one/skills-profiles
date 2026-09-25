# 全栈开发实践

## 强制工作流程 — 按顺序遵循以下步骤

**当此技能被触发时，你必须在此编写任何代码之前遵循此工作流程。**

### 步骤 0：收集需求

在搭建任何东西之前，要求用户澄清（或从上下文中推断）：

1. **技术栈**：后端和前端的语言/框架（例如，Express + React，Django + Vue，Go + HTMX）
2. **服务类型**：仅 API、全栈单体还是微服务？
3. **数据库**：SQL（PostgreSQL、SQLite、MySQL）还是 NoSQL（MongoDB、Redis）？
4. **集成**：REST、GraphQL、tRPC 还是 gRPC？
5. **实时**：需要吗？如果是，— SSE、WebSocket 或轮询？
6. **认证**：需要吗？如果是，— JWT、会话、OAuth 或第三方（Clerk、Auth.js）？

如果用户已经在他们的请求中指定了这些，请跳过询问并继续。

### 步骤 1：架构决策

在编码之前，根据需求做出并声明这些决策：

| 决策 | 选项 | 参考 |
|------|------|------|
| 项目结构 | 特性优先（推荐）vs 层次优先 | [第 1 节](#1-project-structure--layering-critical) |
| API 客户端方法 | 类型化获取 / React Query / tRPC / OpenAPI 代码生成 | [第 5 节](#5-api-client-patterns-medium) |
| 认证策略 | JWT + 刷新 / 会话 / 第三方 | [第 6 节](#6-authentication--middleware-high) |
| 实时方法 | 轮询 / SSE / WebSocket | [第 11 节](#11-real-time-patterns-medium) |
| 错误处理 | 类型化错误层次结构 + 全局处理程序 | [第 3 节](#3-error-handling--resilience-high) |

简要解释每个选择（每个决策 1 句话）。

### 步骤 2：使用清单搭建

使用以下适当的清单。确保所有勾选的项目都已实现 — 不要跳过任何。

### 步骤 3：实现以下模式

按照本文档中的模式编写代码。在实现每个部分时，引用特定部分。

### 步骤 4：测试和验证

实现后，在声称完成之前运行这些检查：

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
   curl http://localhost:3000/api/<resource>
   ```
3. **集成检查**：验证前端可以连接到后端（CORS、API 基 URL、认证流程）
4. **实时检查**（如果适用）：打开两个浏览器标签页，验证更改同步

如果任何检查失败，请在继续之前修复问题。

### 步骤 5：交接摘要

向用户提供简要摘要：

- **构建了什么**：实现的功能和端点列表
- **如何运行**：启动后端和前端的精确命令
- **缺失的/下一步**：任何推迟的项目、已知限制或建议的改进
- **关键文件**：用户应该知道的最重要的文件列表

---

## 范围

**使用此技能当：**
- 构建全栈应用程序（后端 + 前端）
- 搭建新的后端服务或 API
- 设计服务层和模块边界
- 实现数据库访问、缓存或后台作业
- 编写错误处理、日志记录或配置管理
- 审查后端代码以发现架构问题
- 生产环境加固
- 设置 API 客户端、认证流程、文件上传或实时功能

**不适用于：**
- 纯前端/UI 问题（使用你的前端框架文档）
- 没有后端上下文的纯数据库模式设计

---

## 快速入门 — 新后端服务清单

- [ ] 使用 **特性优先** 结构搭建项目
- [ ] 配置 **集中化**，环境变量在启动时 **验证**（快速失败）
- [ ] **类型化错误层次结构** 定义（不是通用 `Error`）
- [ ] **全局错误处理** 中间件
- [ ] **结构化 JSON 日志**，带有请求 ID 传播
- [ ] 数据库：**迁移** 设置，**连接池** 配置
- [ ] 所有端点上的 **输入验证**（Zod / Pydantic / Go 验证器）
- [ ] **认证中间件** 已就位
- [ ] **健康检查** 端点 (`/health`, `/ready`)
- [ ] **优雅关闭** 处理（SIGTERM）
- [ ] **CORS** 配置（明确来源，不是 `*`）
- [ ] **安全头**（helmet 或等效）
- [ ] `.env.example` 提交（没有真实密钥）

## 快速入门 — 前端-后端集成清单

- [ ] **API 客户端** 配置（类型化获取包装器、React Query、tRPC 或 OpenAPI 生成）
- [ ] **基本 URL** 从环境变量（不是硬编码）
- [ ] **认证令牌** 自动附加到请求（拦截器 / 中间件）
- [ ] **错误处理** — API 错误映射到用户界面消息
- [ ] **加载状态** 处理（骨架/旋转器，不是空白屏幕）
- [ ] **类型安全** 跨边界（共享类型、OpenAPI 或 tRPC）
- [ ] **CORS** 配置具有明确来源（生产中不是 `*`）
- [ ] **刷新令牌** 流程实现（httpOnly cookie + 401 透明重试）

---

## 快速导航

| 需要执行… | 跳转到 |
|----------|--------|
| 组织项目文件夹 | [第 1 节](#1-project-structure--layering-critical) |
| 管理 config + secrets | [第 2 节](#2-configuration--environment-critical) |
| 正确处理错误 | [第 3 节](#3-error-handling--resilience-high) |
| 编写数据库代码 | [第 4 节](#4-database-access-patterns-high) |
| 从前端设置 API 客户端 | [第 5 节](#5-api-client-patterns-medium) |
| 添加认证中间件 | [第 6 节](#6-authentication--middleware-high) |
| 设置日志记录 | [第 7 节](#7-logging--observability-medium-high) |
| 添加后台作业 | [第 8 节](#8-background-jobs--async-medium) |
| 实现缓存 | [第 9 节](#9-caching-patterns-medium) |
| 上传文件（预签名 URL、multipart） | [第 10 节](#10-file-upload-patterns-medium) |
| 添加实时功能（SSE、WebSocket） | [第 11 节](#11-real-time-patterns-medium) |
| 在前端 UI 中处理 API 错误 | [第 12 节](#12-cross-boundary-error-handling-medium) |
| 生产环境加固 | [第 13 节](#13-production-hardening-medium) |
| 设计 API 端点 | [API 设计](references/api-design.md) |
| 设计数据库模式 | [数据库模式](references/db-schema.md) |
| 认证流程（JWT、刷新、Next.js SSR、RBAC） | [references/auth-flow.md](references/auth-flow.md) |
| CORS、环境变量、环境管理 | [references/environment-management.md](references/environment-management.md) |

---

## 核心原则（7 条铁律）

```
1. ✅ 按特性组织，而不是按技术层
2. ✅ 控制器从不包含业务逻辑
3. ✅ 服务从不导入 HTTP 请求/响应类型
4. ✅ 所有配置来自环境变量，在启动时验证，快速失败
5. ✅ 每个错误都是类型化的，记录的，并返回一致的格式
6. ✅ 所有输入在边界处验证 — 不要相信来自客户端的任何内容
7. ✅ 结构化 JSON 日志，带有请求 ID — 不是 `console.log`
```

---

## 1. 项目结构 & 层次结构（关键）

### 特性优先组织

```
✅ 特性优先                    ❌ 层次优先
src/                                src/
  orders/                             controllers/
    order.controller.ts                 order.controller.ts
    order.service.ts                    user.controller.ts
    order.repository.ts               services/
    order.dto.ts                        order.test.ts
  users/                              repositories/
    user.controller.ts                 user.service.ts
  shared/
    database/
    middleware/
```

### 三层架构

```
控制器 (HTTP) → 服务 (业务逻辑) → 仓库 (数据访问)
```

| 层级 | 责任 | ❌ 不应 |
|------|------|-------|
| 控制器 | 解析请求、验证、调用服务、格式化响应 | 业务逻辑、数据库查询 |
| 服务 | 业务规则、编排、事务管理 | HTTP 类型（请求/响应）、直接数据库 |
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
    database_url: str                        # required — 应用程序没有它不会启动
    jwt_secret: str                          # required
    port: int = 3000                         # optional with default
    db_pool_size: int = 10
    class Config:
        env_file = ".env"

settings = Settings()                        # 缺少 DATABASE_URL 会快速失败
```

### 规则

```
✅ 所有配置通过环境变量（Twelve-Factor）
✅ 在启动时验证必需的变量 — 快速失败
✅ 在配置层进行类型转换，而不是在用法位置
✅ 提交 .env.example 带有虚拟值

❌ 从不硬编码密钥、URL 或凭证
❌ 从不提交 .env 文件
❌ 从不将 process.env / os.environ 散布在代码中
```

---

## 3. 错误处理 & 弹性（高）

### 类型化错误层次结构

```typescript
// 基础 (TypeScript)
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
# 基础 (Python)
class AppError(Exception):
    def __init__(self, message: str, code: str, status_code: int):
        self.message, self.code, self.status_code = message, code, status_code

class NotFoundError(AppError):
    def __init__(self, resource: str, id: str):
        super().__init__(f"{resource} not found: {id}", "NOT_FOUND", 404)
```

### 全局错误处理程序

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
✅ 类型化、特定于领域的错误类
✅ 全局错误处理程序捕获所有内容
✅ 操作错误 → 结构化响应
✅ 编程错误 → 记录 + 通用 500
✅ 使用指数退避重试瞬态故障

❌ 从不捕获并静默忽略错误
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
✅ 通过迁移进行模式更改，永远不要手动 SQL
✅ 迁移必须是可逆的
✅ 在生产之前审查迁移 SQL
❌ 从不手动修改生产模式
```

### 防止 N+1

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

池大小 = `(CPU 核 × 2) + 磁盘数量`（从 10-20 开始）。始终设置连接超时。使用 PgBouncer 进行无服务器环境。

---

## 5. API 客户端模式（中）

“前端和后端之间的粘合层”。选择适合您的团队和堆栈的方法。

### 选项 A：类型化获取包装器（简单，无依赖项）

```typescript
// lib/api-client.ts
const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001';

class ApiError extends Error {
  constructor(public status: number, public body: any) {
    super(body?.detail || body?.message || `API 错误 ${status}`);
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
    staleTime: 1000 * 60,  // 1 分钟
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

// 在组件中使用：
function OrdersPage() {
  const { data, isLoading, error } = useOrders();
  const createOrder = useCreateOrder();
  if (isLoading) return <Skeleton />;
  if (error) return <ErrorBanner error={error} />;
  // ...
}
```

### 选项 C：tRPC（两边都由 TypeScript 拥有）

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

// 客户端：自动类型安全，无需代码生成
const { data } = trpc.orders.list.useQuery();
const createOrder = trpc.orders.create.useMutation();
```

### 选项 D：OpenAPI 生成客户端（公共 / 多消费者 API）

```bash
npx openapi-typescript-codegen \
  --input http://localhost:3001/api/openapi.json \
  --output src/generated/api \
  --client axios
```

### 决策：选择哪个 API 客户端？

| 方法 | 当... | 类型安全 | 努力程度 |
|------|------|----------|----------|
| 类型化获取包装器 | 简单应用程序，小团队 | 手动类型 | 低 |
| React Query + 获取 | React 应用程序，服务器状态 | 手动类型 | 中等 |
| tRPC | 两边都由 TypeScript 拥有 | 自动 | 低 |
| OpenAPI 生成客户端 | 公共 API，多消费者 | 自动 | 中等 |
| GraphQL 代码生成 | GraphQL API | 自动 | 中等 |

---

## 6. 认证 & 中间件（高）

> **完整参考：** [references/auth-flow.md](references/auth-flow.md) — JWT 带令牌流程，自动令牌刷新，Next.js 服务器端认证，RBAC 模式，后端中间件顺序。

### 标准中间件顺序

```
请求 → 1.请求 ID → 2.日志记录 → 3.CORS → 4.速率限制 → 5.请求体解析
       → 6.认证 → 7.授权 → 8.验证 → 9.处理程序 → 10.错误处理 → 响应
```

### JWT 规则

```
✅ 短期过期访问令牌（15 分钟）+ 刷新令牌（服务器存储）
✅ 最小声明：userId、roles（不是整个用户对象）
✅ 定期轮换签名密钥

❌ 从不将令牌存储在 localStorage（XSS 风险）
❌ 从不将令牌传递在 URL 查询参数中
```

### RBAC 模式

```typescript
function authorize(...roles: Role[]) {
  return (req, res, next) => {
    if (!req.user) throw new UnauthorizedError();
    if (!roles.some(r => req.user.roles.includes(r)) throw new ForbiddenError();
    next();
  };
}
router.delete('/users/:id', authenticate, authorize('admin'), deleteUser);
```

### 认证令牌自动刷新

```typescript
// lib/api-client.ts — 401 透明重试
async function apiWithRefresh<T>(path: string, options: RequestInit = {}): Promise<T> {
  try {
    return await api<T>(path, options);
  } catch (err) {
    if (err instanceof ApiError && err.status === 401) {
      const refreshed = await api<{ accessToken: string }>('/api/auth/refresh', {
        method: 'POST',
        credentials: 'include',  // 发送 httpOnly cookie
      });
      setAuthToken(refreshed.accessToken);
      return api<T>(path, options);  // 重试
    }
    throw err;
  }
}
```

---

## 7. 日志记录 & 可观察性（中高）

### 结构化 JSON 日志记录

```typescript
// ✅ 结构化 — 可解析的，可过滤的，可告警的
logger.info('Order created', {
  orderId: order.id, userId: user.id, total: order.total,
  items: order.items.length, duration_ms: Date.now() - startTime,
});
// 输出: {"level":"info","msg":"Order created","orderId":"ord_123",...}

// ❌ 非结构化 — 在规模上无用的
console.log(`Order created for user ${user.id} with total ${order.total}`);
```

### 日志级别

| 级别 | 当... | 生产环境？ |
|------|------|------------|
| error | 需要立即注意 | ✅ 总是 |
| warn | 预期之外但已处理 | ✅ 总是 |
| info | 正常操作，审计跟踪 | ✅ 总是 |
| debug | 开发故障排除 | ❌ 仅限开发 |

### 规则

```
✅ 每个日志条目中都包含请求 ID（通过中间件传播）
✅ 在层边界处记录日志（请求输入，响应输出，外部调用）
❌ 从不记录密码、令牌、PII 或密钥
❌ 从不使用 `console.log` 在生产代码中
```

---

## 8. 后台作业 & 异步（中）

### 规则

```
✅ 所有作业都必须是幂等的（两次运行相同的作业 = 相同的结果）
✅ 失败的作业 → 重试（最多 3 次）→ 死信队列 → 告警
✅ 工作进程作为单独的进程运行（不是 API 服务器中的线程）

❌ 从不将长时间运行的任务放在请求处理程序中
❌ 不假设作业运行正好一次
```

### 幂等作业模式

```typescript
async function processPayment(data: { orderId: string }) {
  const order = await orderRepo.findById(data.orderId);
  if (order.paymentStatus === 'completed') return;  // 已经处理
  await paymentGateway.charge(order);
  await orderRepo.updatePaymentStatus(order.id, 'completed');
}
```

---

## 9. 缓存模式（中）

### 缓存分离（惰性加载）

```typescript
async function getUser(id: string): Promise<User> {
  const cached = await redis.get(`user:${id}`);
  if (cached) return JSON.parse(cached);

  const user = await userRepo.findById(id);
  if (!user) throw new NotFoundError('User', id);

  await redis.set(`user:${id}`, JSON.stringify(user), 'EX', 900);  // 15 分钟 TTL
  return user;
}
```

### 规则

```
✅ 总是设置 TTL — 没有TTL的缓存（过时的数据比慢数据更糟）
✅ 写入时使缓存失效（删除缓存键）
✅ 使用缓存进行读取，永远不要用于权威状态

❌ 从不缓存而没有 TTL（过时的数据比慢数据更糟）
```

| 数据类型 | 建议的 TTL |
|----------|------------|
| 用户配置文件 | 5-15 分钟 |
| 产品目录 | 1-5 分钟 |
| 配置 / 功能标志 | 30-60 秒 |
| 会话 | 匹配会话持续时间 |

---

## 10. 文件上传模式（中）

### 选项 A：预签名 URL（推荐用于大文件）

```
客户端 → GET /api/uploads/presign?filename=photo.jpg&type=image/jpeg
服务器 → { uploadUrl: "https://s3.../presigned", fileKey: "uploads/abc123.jpg" }
客户端 → PUT uploadUrl (直接上传到 S3，绕过你的服务器)
客户端 → POST /api/photos { fileKey: "uploads/abc123.jpg" }  (保存引用)
```

**后端:**
```typescript
app.get('/api/uploads/presign', authenticate, async (req, res) => {
  const { filename, type } = req.query;
  const key = `uploads/${crypto.randomUUID()}-${filename}`;
  const url = await s3.getSignedUrl('putObject', {
    Bucket: process.env.S3_BUCKET, Key: key,
    ContentType: type, Expires: 300,  // 5 分钟
  });
  res.json({ uploadUrl: url, fileKey: key });
});
```

**前端:**
```typescript
async function uploadFile(file: File) {
  const { uploadUrl, fileKey } = await apiClient.get<PresignResponse>(
    `/api/uploads/presign?filename=${file.name}&type=${file.type}`
  );
  await fetch(uploadUrl, { method: 'PUT', body: file, headers: { 'Content-Type': file.type } });
  return apiClient.post('/api/photos', { fileKey });
}
```

### 决策

| 方法 | 文件大小 | 服务器负载 | 复杂性 |
|------|----------|-------------|--------|
| 预签名 URL | 任何 (推荐 > 5MB) | 无 (直接到存储)
| Multipart | < 10MB | 高 (通过服务器流式传输)
| 分块 / 可恢复 | > 100MB | 中等 |
