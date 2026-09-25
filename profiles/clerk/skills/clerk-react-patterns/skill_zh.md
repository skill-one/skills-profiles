# React 单页应用模式

> 本技能涵盖 `@clerk/react` 用于 Vite/CRA 单页应用。对于 Next.js 使用 `clerk-nextjs-patterns`。对于 TanStack Start 使用 `clerk-tanstack-patterns`。

## 需要什么？

| 任务 | 参考 |
|------|-----------|
| useAuth / useUser / useClerk 钩子 | references/hooks.md |
| 使用 React Router 的受保护路由 | references/protected-routes.md |
| 自定义登录/注册表单 | references/custom-flows.md |
| React Router v6/v7 集成 | references/router-integration.md |

## 参考

| 参考 | 描述 |
|-----------|-------------|
| `references/hooks.md` | useAuth, isLoaded 守卫 |
| `references/protected-routes.md` | 受保护路由模式 |
| `references/custom-flows.md` | useSignIn, useSignUp 流程 |
| `references/router-integration.md` | React Router v6/v7 设置 |

## 设置

```
npm install @clerk/react
```

`.env`:
```
VITE_CLERK_PUBLISHABLE_KEY=pk_...
```

`src/main.tsx`:
```tsx
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { ClerkProvider } from '@clerk/react'
import App from './App.tsx'

const PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ClerkProvider publishableKey={PUBLISHABLE_KEY}>
      <App />
    </ClerkProvider>
  </StrictMode>,
)
```

## 思维模型

`@clerk/react` 仅客户端使用——没有服务器端的 `auth()`。所有认证状态都来自钩子。

- 在信任 `isSignedIn` 之前 `isLoaded` 必须为 `true`——始终在 `isLoaded` 上守卫
- `useClerk()` 提供对 `signOut`, `openSignIn`, `openUserProfile` 等方法的访问
- `useAuth()` 的 `getToken()` 获取用于 API 调用的会话 JWT

## 最小模式

```tsx
import { useAuth } from '@clerk/react'

export function Dashboard() {
  const { isLoaded, isSignedIn, userId } = useAuth()

  if (!isLoaded) return <div>Loading...</div>
  if (!isSignedIn) return <div>Please sign in</div>

  return <div>Hello {userId}</div>
}
```

## 受保护路由 (React Router v6/v7)

```tsx
import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '@clerk/react'

export function ProtectedRoute() {
  const { isLoaded, isSignedIn } = useAuth()

  if (!isLoaded) return <div>Loading...</div>
  if (!isSignedIn) return <Navigate to="/sign-in" replace />

  return <Outlet />
}
```

```tsx
<Routes>
  <Route element={<ProtectedRoute />}>
    <Route path="/dashboard" element={<Dashboard />} />
    <Route path="/settings" element={<Settings />} />
  </Route>
  <Route path="/sign-in" element={<SignIn />} />
</Routes>
```

## API 调用的 Token

```tsx
import { useAuth } from '@clerk/react'

export function DataFetcher() {
  const { getToken } = useAuth()

  async function fetchData() {
    const token = await getToken()
    if (!token) return

    const res = await fetch('/api/data', {
      headers: { Authorization: `Bearer ${token}` },
    })
    return res.json()
  }

  return <button onClick={fetchData}>Load</button>
}
```

## 常见陷阱

| 症状 | 原因 | 解决方法 |
|---------|-------|-----|
| `isSignedIn` 为 `undefined` | `isLoaded` 仍为 `false` | 始终先检查 `isLoaded` |
| `ClerkProvider` 缺失 | 提供者不在根节点 | 将 `<App>` 包裹在 `main.tsx` 中 |
| 环境变量未定义 | Vite 前缀错误 | 使用 `VITE_CLERK_PUBLISHABLE_KEY`，通过 `import.meta.env` 访问 |
| Token 为 `null` | 用户未登录 | 检查 `getToken()` 结果是否为空 |
| 登录组件显示空白 | 提供者没有 `publishableKey` | 显式传递 `publishableKey` |

## 参考资料链接

- `clerk-setup` - 初始 Clerk 安装
- `clerk-custom-ui` - 自定义流程和外观
- `clerk-orgs` - B2B 组织

## 文档

[React SDK](https://clerk.com/docs/react/getting-started/quickstart)
