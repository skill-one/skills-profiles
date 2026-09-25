# Hono API 框架生成器

为现有的 Cloudflare Workers 项目添加结构化的 API 路由。此功能在项目外壳创建完成后运行（通过 cloudflare-worker-builder 或 vite-flare-starter），并生成路由文件、中间件和端点文档。

## 工作流程

### 第 1 步：收集端点

确定 API 需要什么。可以询问用户或从项目描述中推断。按资源分组端点：

```
用户：    GET /api/users, GET /api/users/:id, POST /api/users, PUT /api/users/:id, DELETE /api/users/:id
帖子：    GET /api/posts, GET /api/posts/:id, POST /api/posts, PUT /api/posts/:id
认证：    POST /api/auth/login, POST /api/auth/logout, GET /api/auth/me
```

### 第 2 步：创建路由文件

每个资源组一个文件。使用来自 [assets/route-template.ts](assets/route-template.ts) 的模板：

```typescript
// src/routes/users.ts
import { Hono } from 'hono'
import { zValidator } from '@hono/zod-validator'
import { z } from 'zod'
import type { Env } from '../types'

const app = new Hono<{ Bindings: Env }>()

// GET /api/users
app.get('/', async (c) => {
  const db = c.env.DB
  const { results } = await db.prepare('SELECT * FROM users').all()
  return c.json({ users: results })
})

// GET /api/users/:id
app.get('/:id', async (c) => {
  const id = c.req.param('id')
  const user = await db.prepare('SELECT * FROM users WHERE id = ?').bind(id).first()
  if (!user) return c.json({ error: 'Not found' }, 404)
  return c.json({ user })
})

// POST /api/users
const createUserSchema = z.object({
  name: z.string().min(1),
  email: z.string().email(),
})

app.post('/', zValidator('json', createUserSchema), async (c) => {
  const body = c.req.valid('json')
  // ... 插入逻辑
  return c.json({ user }, 201)
})

export default app
```

### 第 3 步：添加中间件

根据项目需求，添加来自 [assets/middleware-template.ts](assets/middleware-template.ts) 的中间件：

**认证中间件** — 保护需要认证的路由：
```typescript
import { createMiddleware } from 'hono/factory'
import type { Env } from '../types'

export const requireAuth = createMiddleware<{ Bindings: Env }>(async (c, next) => {
  const token = c.req.header('Authorization')?.replace('Bearer ', '')
  if (!token) return c.json({ error: 'Unauthorized' }, 401)
  // 验证 token...
  await next()
})
```

**CORS** — 使用 Hono 的内置功能：
```typescript
import { cors } from 'hono/cors'
app.use('/api/*', cors({ origin: ['https://example.com'] }))
```

### 第 4 步：连接路由

在主入口点挂载所有路由组：

```typescript
// src/index.ts
import { Hono } from 'hono'
import type { Env } from './types'
import users from './routes/users'
import posts from './routes/posts'
import auth from './routes/auth'
import { errorHandler } from './middleware/error-handler'

const app = new Hono<{ Bindings: Env }>()

// 全局错误处理器
app.onError(errorHandler)

// 挂载路由
app.route('/api/users', users)
app.route('/api/posts', posts)
app.route('/api/auth', auth)

// 健康检查
app.get('/api/health', (c) => c.json({ status: 'ok' }))

export default app
```

### 第 5 步：创建类型

```typescript
// src/types.ts
export interface Env {
  DB: D1Database
  KV: KVNamespace      // 如有需要
  R2: R2Bucket         // 如有需要
  API_SECRET: string   // 密钥
}
```

### 第 6 步：生成 API_ENDPOINTS.md

记录所有端点。参考 [references/endpoint-docs-template.md](references/endpoint-docs-template.md) 的格式：

```markdown
## POST /api/users
创建新用户。
- **认证**：必需（Bearer token）
- **请求体**：`{ name: string, email: string }`
- **响应 201**：`{ user: User }`
- **响应 400**：`{ error: string, details: ZodError }`
```

## 关键模式

### Zod 验证

始终使用 `@hono/zod-validator` 验证请求体：

```typescript
import { zValidator } from '@hono/zod-validator'
app.post('/', zValidator('json', schema), async (c) => {
  const body = c.req.valid('json')  // 完全类型化
})
```

安装：`pnpm add @hono/zod-validator zod`

### 错误处理

使用来自 [assets/error-handler.ts](assets/error-handler.ts) 的标准错误处理器：

```typescript
export const errorHandler = (err: Error, c: Context) => {
  console.error(err)
  return c.json({ error: err.message }, 500)
}
```

**API 路由必须返回 JSON 错误，而不是重定向。** `fetch()` 默默跟随重定向，然后客户端尝试将 HTML 解析为 JSON。

### RPC 类型安全

为 Worker 和客户端之间的端到端类型安全：

```typescript
// Worker: 导出应用类型
export type AppType = typeof app

// Client: 使用 hc (Hono Client)
import { hc } from 'hono/client'
import type { AppType } from '../worker/src/index'

const client = hc<AppType>('https://api.example.com')
const res = await client.api.users.$get()  // 完全类型化
```

### 路由组与单个文件

| 项目规模 | 结构 |
|-------------|-----------|
| < 10 端点 | 单个 `index.ts` 包含所有路由 |
| 10-30 端点 | 每个资源一个路由文件 (`routes/users.ts`) |
| 30+ 端点 | 路由文件 + 共享中间件 + 类型化上下文 |

## 参考文件

| 当... | 阅读 |
|------|------|
| Hono 模式、中间件、RPC | [references/hono-patterns.md](references/hono-patterns.md) |
| API_ENDPOINTS.md 格式 | [references/endpoint-docs-template.md](references/endpoint-docs-template.md) |

## 资产

| 文件 | 目的 |
|------|------|
| [assets/route-template.ts](assets/route-template.ts) | 带有 CRUD + Zod 的起始路由文件 |
| [assets/middleware-template.ts](assets/middleware-template.ts) | 认证中间件模板 |
| [assets/error-handler.ts](assets/error-handler.ts) | 标准 JSON 错误处理器 |
