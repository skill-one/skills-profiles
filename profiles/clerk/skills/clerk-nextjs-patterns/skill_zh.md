# Next.js 模式

> **版本**：检查 `package.json` 中的 SDK 版本——参见 `clerk` 技能中的版本表。Core 2 的差异会在 `>` **Core 2 ONLY (skip if current SDK):**` 提示中直接标注。

基础设置请参见 `clerk-setup` 技能。

## 你需要什么？

| 任务 | 参考 |
|------|-----------|
| 服务端与客户端认证（`auth()` vs hooks） | references/server-vs-client.md |
| 配置中间件（public-first 与 protected-first） | references/middleware-strategies.md |
| 保护 Server Actions | references/server-actions.md |
| API 路由认证（401 vs 403） | references/api-routes.md |
| 缓存认证数据（用户范围缓存） | references/caching-auth.md |

## 参考

| 参考 | 描述 |
|-----------|-------------|
| `references/server-vs-client.md` | `await auth()` vs hooks |
| `references/middleware-strategies.md` | Public-first vs protected-first, `proxy.ts` (Next.js <=15: `middleware.ts`) |
| `references/server-actions.md` | 保护变更 |
| `references/api-routes.md` | 401 vs 403 |
| `references/caching-auth.md` | 用户范围缓存 |

## 心智模型

服务端与客户端 = 不同的认证 API：
- **服务端**：从 `@clerk/nextjs/server` 导入 `await auth()`（异步！）
- **客户端**：使用 `@clerk/nextjs` 中的 `useAuth()` hook（同步）

切勿混用。Server Components 使用服务端导入，Client Components 使用 hook。

`auth()` 中的关键属性：
- `isAuthenticated` — 布尔值，替代 `!!userId` 模式
- `sessionStatus` — `'active'` | `'pending'`，用于检测不完整的会话任务
- `userId`, `orgId`, `orgSlug`, `has()`, `protect()` — 保持不变

> **Core 2 ONLY (skip if current SDK):** `isAuthenticated` 和 `sessionStatus` 不可用。请改用 `!!userId`。

## 最小模式

```typescript
// Server Component
import { auth } from '@clerk/nextjs/server'

export default async function Page() {
  const { isAuthenticated, userId } = await auth()  // MUST await!
  if (!isAuthenticated) return <p>Not signed in</p>
  return <p>Hello {userId}</p>
}
```

> **Core 2 ONLY (skip if current SDK):** `isAuthenticated` 不可用。请改用 `if (!userId)`。

### 使用 `<Show>` 的条件渲染

基于认证状态的客户端条件渲染。`<Show>` 可在同一组件中覆盖认证检查和授权（功能、套餐、角色、权限）。

**认证检查：**

```tsx
import { Show } from '@clerk/nextjs'

<Show when="signed-in" fallback={<p>Please sign in</p>}>
  <Dashboard />
</Show>
```

**授权检查（B2B）：**

```tsx
// 基于功能（推荐——功能可在套餐间迁移而无需重新部署）
<Show when={{ feature: 'analytics' }} fallback={<UpgradePrompt />}>
  <AnalyticsDashboard />
</Show>

// 基于权限（推荐用于细粒度访问，优于基于角色）
<Show when={{ permission: 'org:invoices:create' }}>
  <NewInvoiceButton />
</Show>

// 基于套餐（层级级控制）
<Show when={{ plan: 'pro' }}>
  <ProFeatures />
</Show>

// 基于角色（少量使用——优先使用权限）
<Show when={{ role: 'org:admin' }}>
  <AdminPanel />
</Show>
```

**复杂逻辑的回调：**

```tsx
<Show when={(has) => has({ role: 'org:admin' }) || has({ role: 'org:billing_manager' })}>
  <BillingActions />
</Show>
```

> **Core 2 ONLY (skip if current SDK):** `<Show>` 不存在。认证请使用 `<SignedIn>` 和 `<SignedOut>`。授权（角色 / 权限）请使用 `<Protect>`，并保留相同的属性名（`role`、`permission`、`condition`）。基于功能和套餐的变体需要 Core 3。参见 `clerk-custom-ui` 技能、`core-3/show-component.md` 以获取完整的迁移表。

## 常见陷阱

| 症状 | 原因 | 修复 |
|---------|-------|-----|
| Server Component 中 `undefined` userId | 缺少 `await` | `await auth()` 而非 `auth()` |
| API 路由上认证不工作 | 缺少 matcher | 在 `proxy.ts`（Next.js <=15：`middleware.ts`）中添加 `'/(api\(trpc\)(.*)'` |
| 缓存返回了错误用户的数据 | 键中缺少 userId | 在 `unstable_cache` 键中包含 `userId` |
| 变更绕过认证 | 未受保护的 Server Action | 在操作开始时检查 `auth()` |
| 错误的 HTTP 错误码 | 混淆了 401/403 | 401 = 未登录，403 = 无权限 |

## 会话令牌与自定义 JWT

### 为外部 API 使用 `getToken()`

使用 Clerk 仪表板中定义的 JWT 模板，向第三方服务（Hasura、Supabase 等）传递自定义 JWT。

**服务端（Server Component 或 Route Handler）：**

```typescript
import { auth } from '@clerk/nextjs/server'

export default async function Page() {
  const { getToken } = await auth()
  const token = await getToken({ template: 'hasura' })
  if (!token) return <p>Not authenticated</p>

  const res = await fetch('https://api.example.com/graphql', {
    headers: { Authorization: `Bearer ${token}` },
  })
  const data = await res.json()
  return <pre>{JSON.stringify(data)}</pre>
}
```

**客户端（Client Component）：**

```tsx
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

  return <button onClick={fetchData}>Fetch</button>
}
```

`getToken()` 在用户未认证时返回 `null`——使用时务必进行 null 检查。

### 为会话数据使用 `useSession()`

在客户端组件中访问会话元数据：

```tsx
'use client'
import { useSession } from '@clerk/nextjs'

export function SessionInfo() {
  const { session } = useSession()
  if (!session) return null

  return (
    <p>
      Session {session.id} — last active: {session.lastActiveAt.toISOString()}
    </p>
  )
}
```

### 手动 JWT 验证（无 Clerk 中间件）

对于独立 API 服务器，需要接收来自 `Authorization` 请求头或 `__session` cookie（同源）的 Clerk 会话令牌。

**使用 `@clerk/backend` 的 `verifyToken`**（推荐）：

```typescript
import { verifyToken } from '@clerk/backend'

const token = req.headers.authorization?.replace('Bearer ', '')
if (!token) return res.status(401).json({ error: 'No token' })

try {
  const claims = await verifyToken(token, {
    jwtKey: process.env.CLERK_JWT_KEY,
  })
  // claims.sub = userId
} catch {
  return res.status(401).json({ error: 'Invalid token' })
}
```

**使用 `jsonwebtoken`**（当无法使用 `@clerk/backend` 时）：

```typescript
import jwt from 'jsonwebtoken'

const publicKey = process.env.CLERK_PEM_PUBLIC_KEY!.replace(/\\n/g, '\n')
const token = req.headers.authorization?.replace('Bearer ', '')
if (!token) return res.status(401).json({ error: 'No token' })

try {
  const claims = jwt.verify(token, publicKey, { algorithms: ['RS256'] }) as jwt.JwtPayload
  // 手动检查 exp 和 nbf（jsonwebtoken 会自动处理此操作，但如果需要可验证 azp）
  // claims.sub = userId
} catch {
  return res.status(401).json({ error: 'Invalid or expired token' })
}
```

令牌来源：
- **同源请求**：`__session` cookie（Clerk 会自动设置）
- **跨域 / 移动端 / API 间调用**：`Authorization: Bearer <token>` 请求头

> **重要**：始终检查 `exp` 和 `nbf` 声明。`@clerk/backend` 的 `verifyToken` 会自动处理此操作；使用原始 `jsonwebtoken` 时，设置 `ignoreExpiration: false`（默认值）并确保 `clockTolerance` 最小。

## 另请参见

- `clerk-setup` - 初始 Clerk 安装
- `clerk-orgs` - B2B 模式（活动组织、角色/权限控制）
- `clerk-billing` - 使用 `has()` 的套餐和功能授权
- `clerk-webhooks` - 将用户/组织事件同步到您的数据库
- `clerk-custom-ui` - 内置组件的主题化和定制

## 文档

[Next.js SDK](https://clerk.com/docs/reference/nextjs/overview)
