# Next.js 模式

> **版本**: 请查看 `package.json` 获取 SDK 版本 — 参考文档中的 `clerk` 技能获取版本表。核心 2 版本的不同之处将在 `> **Core 2 ONLY (skip if current SDK):**` 标注中内联说明。

基本设置请参考 `clerk-setup` 技能。

## 你需要什么？

| 任务 | 参考 |
|------|-----------|
| 服务器与客户端认证 (`auth()` 与钩子) | references/server-vs-client.md |
| 配置中间件（公开优先与保护优先） | references/middleware-strategies.md |
| 保护服务器操作 | references/server-actions.md |
| API 路由认证 (401 与 403) | references/api-routes.md |
| 缓存认证数据 (用户范围缓存) | references/caching-auth.md |

## 参考

| 参考 | 描述 |
|-----------|-------------|
| `references/server-vs-client.md` | `await auth()` 与钩子 |
| `references/middleware-strategies.md` | 公开优先与保护优先，`proxy.ts` (Next.js <=15: `middleware.ts`) |
| `references/server-actions.md` | 保护变更 |
| `references/api-routes.md` | 401 与 403 |
| `references/caching-auth.md` | 用户范围缓存 |

## 思维模型

服务器与客户端 = 不同的认证 API：
- **服务器**: 从 `@clerk/nextjs/server` 导入的 `await auth()` (异步!)
- **客户端**: 从 `@clerk/nextjs` 导入的 `useAuth()` 钩子 (同步)

永远不要混用它们。服务器组件使用服务器导入，客户端组件使用钩子。

`auth()` 的关键属性：
- `isAuthenticated` — 布尔值，替代 `!!userId` 模式
- `sessionStatus` — `'active'` | `'pending'`，用于检测未完成的会话任务
- `userId`, `orgId`, `orgSlug`, `has()`, `protect()` — 无变化

> **Core 2 ONLY (skip if current SDK):** `isAuthenticated` 和 `sessionStatus` 不可用。请检查 `!!userId`。

## 最小模式

```typescript
// 服务器组件
import { auth } from '@clerk/nextjs/server'

export default async function Page() {
  const { isAuthenticated, userId } = await auth()  // 必须使用 await!
  if (!isAuthenticated) return <p>未登录</p>
  return <p>Hello {userId}</p>
}
```

> **Core 2 ONLY (skip if current SDK):** `isAuthenticated` 不可用。使用 `if (!userId)`。

### 使用 `<Show>` 进行条件渲染

基于认证状态进行客户端条件渲染。`<Show>` 组件在一个组件中涵盖了认证检查和授权（功能、计划、角色、权限）。

**认证检查:**

```tsx
import { Show } from '@clerk/nextjs'

<Show when="signed-in" fallback={<p>请登录</p>}>
  <Dashboard />
</Show>
```

**授权检查 (B2B):**

```tsx
// 基于功能 (推荐 — 功能可以在计划间移动而无需重新部署)
<Show when={{ feature: 'analytics' }} fallback={<UpgradePrompt />}>
  <AnalyticsDashboard />
</Show>

// 基于权限 (推荐于基于角色的权限，用于更细粒度的访问)
<Show when={{ permission: 'org:invoices:create' }}>
  <NewInvoiceButton />
</Show>

// 基于计划 (层级门控)
<Show when={{ plan: 'pro' }}>
  <ProFeatures />
</Show>

// 基于角色 (谨慎使用 — 优先使用权限)
<Show when={{ role: 'org:admin' }}>
  <AdminPanel />
</Show>
```

**复杂逻辑的回调:**

```tsx
<Show when={(has) => has({ role: 'org:admin' }) || has({ role: 'org:billing_manager' })}>
  <BillingActions />
</Show>
```

> **Core 2 ONLY (skip if current SDK):** `<Show>` 不存在。用于认证，请使用 `<SignedIn>` 和 `<SignedOut>`。用于授权（角色 / 权限），请使用 `<Protect>` 并使用相同的属性名 (`role`, `permission`, `condition`)。基于功能和基于计划的变体需要核心 3。参考 `clerk-custom-ui` 技能，`core-3/show-component.md` 获取完整的迁移表。

## 常见陷阱

| 症状 | 原因 | 解决方法 |
|---------|-------|-----|
| 服务器组件中的 `undefined` userId | 缺少 `await` | `await auth()` 而不是 `auth()` |
| API 路由认证失败 | 缺少匹配器 | 将 `'/(api|trpc)(.*)'` 添加到 `proxy.ts` (Next.js <=15: `middleware.ts`) |
| 缓存返回错误用户的数据 | 缺少 userId 在键中 | 在 `unstable_cache` 键中包含 `userId` |
| 变更绕过认证 | 未保护的服务器操作 | 在操作开始时检查 `auth()` |
| 错误的 HTTP 错误代码 | 混淆 401/403 | 401 = 未登录，403 = 无权限 |

## 会话令牌与自定义 JWT

### getToken() 用于外部 API

使用 Clerk 控制面板中定义的 JWT 模板向第三方服务（Hasura、Supabase 等）传递自定义 JWT。

**服务器端 (服务器组件或路由处理器)**:

```typescript
import { auth } from '@clerk/nextjs/server'

export default async function Page() {
  const { getToken } = await auth()
  const token = await getToken({ template: 'hasura' })
  if (!token) return <p>未认证</p>

  const res = await fetch('https://api.example.com/graphql', {
    headers: { Authorization: `Bearer ${token}` },
  })
  const data = await res.json()
  return <pre>{JSON.stringify(data)}</pre>
}
```

**客户端 (客户端组件)**:

```typescript
'use client'
import { useAuth } from '@clerk/nextjs'

export function DataFetcher() {
  const { getToken } = useAuth()

  async function fetchData() {
    const token = await getToken({ template: 'supabase' })
    if (!token) return

    const res = await fetch('https://api.example.com/data', {
      headers: { Authorization: `Bearer ${token}` },
    })
    return res.json()
  }

  return <button onClick={fetchData}>获取</button>
}
```

`getToken()` 在用户未认证时返回 `null` — 使用前始终进行 null 检查。

### useSession() 用于会话数据

在客户端组件中访问会话元数据:

```typescript
'use client'
import { useSession } from '@clerk/nextjs'

export function SessionInfo() {
  const { session } = useSession()
  if (!session) return null

  return (
    <p>
      会话 {session.id} — 最后活跃时间: {session.lastActiveAt.toISOString()}
    </p>
  )
}
```

### 手动 JWT 验证 (无 Clerk 中间件)

用于独立 API 服务器，该服务器从 `Authorization` 头或 `__session` cookie (同源) 接收 Clerk 会话令牌。

**使用 `@clerk/backend` `verifyToken`** (推荐):

```typescript
import { verifyToken } from '@clerk/backend'

const token = req.headers.authorization?.replace('Bearer ', '')
if (!token) return res.status(401).json({ error: '无令牌' })

try {
  const claims = await verifyToken(token, {
    jwtKey: process.env.CLERK_JWT_KEY,
  })
  // claims.sub = userId
} catch {
  return res.status(401).json({ error: '无效令牌' })
}
```

**使用 `jsonwebtoken`** (当无法使用 `@clerk/backend`):

```typescript
import jwt from 'jsonwebtoken'

const publicKey = process.env.CLERK_PEM_PUBLIC_KEY!.replace(/\\n/g, '\n')
const token = req.headers.authorization?.replace('Bearer ', '')
if (!token) return res.status(401).json({ error: '无令牌' })

try {
  const claims = jwt.verify(token, publicKey, { algorithms: ['RS256'] }) as jwt.JwtPayload
  // 手动检查 exp 和 nbf (jsonwebtoken 会自动处理，但需要验证 azp)
  // claims.sub = userId
} catch {
  return res.status(401).json({ error: '无效或过期令牌' })
}
```

令牌来源：
- **同源请求**: `__session` cookie (Clerk 自动设置)
- **跨源 / 移动 / API 到 API**: `Authorization: Bearer <token>` 头

> **关键**: 始终检查 `exp` 和 `nbf` 声明。`@clerk/backend` 的 `verifyToken` 自动处理此问题；使用原始 `jsonwebtoken` 时，设置 `ignoreExpiration: false` (默认) 并确保 `clockTolerance` 最小。

## 参考文档

- `clerk-setup` - 初始 Clerk 安装
- `clerk-orgs` - B2B 模式 (活跃组织，角色/权限门控)
- `clerk-billing` - 计划和功能授权与 `has()`
- `clerk-webhooks` - 将用户/组织事件同步到您的数据库
- `clerk-custom-ui` - 内置组件的主题和定制

## 文档

[Next.js SDK](https://clerk.com/docs/reference/nextjs/overview)
