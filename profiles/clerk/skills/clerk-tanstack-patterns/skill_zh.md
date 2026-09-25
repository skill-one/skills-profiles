# TanStack React 启动模式

## 需要什么？

| 任务 | 参考 |
|------|-----------|
| 使用 beforeLoad 保护路由 | references/router-guards.md |
| 在 createServerFn 中进行认证 | references/server-functions.md |
| 将认证传递给 loaders | references/loaders.md |
| 配置 Vinxi + clerkMiddleware | references/vinxi-server.md |

## 参考

| 参考 | 描述 |
|-----------|-------------|
| `references/router-guards.md` | beforeLoad 认证重定向 |
| `references/server-functions.md` | 带有 auth() 的 createServerFn |
| `references/loaders.md` | loaders 中的 Auth 上下文 |
| `references/vinxi-server.md` | clerkMiddleware() 设置 |

## 设置

```
npm install @clerk/tanstack-react-start
```

`.env`:
```
CLERK_PUBLISHABLE_KEY=pk_...
CLERK_SECRET_KEY=sk_...
```

`src/start.ts` (Vinxi 入口):
```typescript
import { clerkMiddleware } from '@clerk/tanstack-react-start/server'
import { createStart } from '@tanstack/react-start'

export const startInstance = createStart(() => {
  return {
    requestMiddleware: [clerkMiddleware()],
  }
})
```

`src/routes/__root.tsx` — 用 `<ClerkProvider>` 包裹:
```tsx
import { ClerkProvider } from '@clerk/tanstack-react-start'

function RootDocument({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <ClerkProvider>
          {children}
        </ClerkProvider>
      </body>
    </html>
  )
}
```

## 思维模型

TanStack Start 在 Vinxi 上运行。认证流程通过两层进行：

1. **服务器层** — `createServerFn` + 来自 `@clerk/tanstack-react-start/server` 的 `auth()` 
2. **路由层** — 路由定义上的 `beforeLoad`，对未认证用户抛出 `redirect`

两层都是服务器执行的。客户端钩子 (`useAuth`, `useUser`) 是用于浏览器端的 React 钩子。

## 最小模式

```typescript
import { createFileRoute, redirect } from '@tanstack/react-router'
import { createServerFn } from '@tanstack/react-start'
import { auth } from '@clerk/tanstack-react-start/server'

const authStateFn = createServerFn().handler(async () => {
  const { isAuthenticated, userId } = await auth()
  if (!isAuthenticated) {
    throw redirect({ to: '/sign-in' })
  }
  return { userId }
})

export const Route = createFileRoute('/dashboard')({
  beforeLoad: async () => await authStateFn(),
})
```

## 常见陷阱

| 症状 | 原因 | 解决方法 |
|---------|-------|-----|
| `auth()` 返回空 | start.ts 中缺少 `clerkMiddleware` | 添加到 `requestMiddleware` 数组 |
| `redirect` 未抛出 | 使用 `return` 而不是 `throw` | 在 TanStack 中使用 `throw redirect(...)` |
| `auth` 导入错误 | 混合客户端/服务器导入 | 服务器: `@clerk/tanstack-react-start/server` |
| Loader 上下文缺少 userId | 未从 beforeLoad 传递 | 从 beforeLoad 返回，通过 `context` 访问 |
| `ClerkProvider` 缺失 | 遗忘了根包裹 | 添加到 `__root.tsx` 容器组件 |

## 参见

- `clerk-setup` - 初始 Clerk 安装
- `clerk-custom-ui` - 自定义流程和外观
- `clerk-orgs` - B2B 组织

## 文档

[TanStack React Start SDK](https://clerk.com/docs/tanstack-react-start/getting-started/quickstart)
