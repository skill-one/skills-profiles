# React Router 模式

SDK: `@clerk/react-router` v3.5+，支持 React Router v7.9+ 和 v8。

## 你需要什么？

| 任务 | 参考 |
|------|-----------|
| 认证在加载器和操作中 | references/loaders-actions.md |
| 受保护的路由和重定向 | references/protected-routes.md |
| SSR 用户数据和会话 | references/ssr-auth.md |

## React Router v7 与 v8 的比较

在搭建脚手架之前检查已安装的 `react-router` 主版本号——配置不同：

| | v7.9+ | v8+ |
|--|--|--|
| 中间件 API | 选择性启用：在 `react-router.config.ts` 中设置 `future: { v8_middleware: true }` | 始终启用——不要设置标志（v8 已移除它） |
| `ssr.noExternal` 工作方式（下文） | 不需要 | **必需** |

## 最小化设置

### 1. vite.config.ts（仅 v8——必需）

React Router v8 提供开发/生产条件导出。在 `react-router dev` 中，
Vite 将 `@clerk/react-router` 外部化以用于 SSR，因此 Node 解析
react-router 的生产构建，而应用程序代码获得开发构建——两个模块实例，两个
Router 上下文。然后每次请求在 SSR 时都会失败，错误信息如下：

```
Error: useNavigate() may be used only in the context of a <Router> component.
```

**`npm ls react-router` 显示单个副本——这不排除这种情况。** 复制是按导出条件而不是按安装副本进行的。不要追查重复安装；添加工作方式（上游问题：
https://github.com/remix-run/react-router/issues/15232）：

```ts
import { reactRouter } from '@react-router/dev/vite'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [reactRouter()],
  ssr: {
    noExternal: ['@clerk/react-router'],
  },
})
```

### 2. root.tsx

```tsx
import { Outlet } from 'react-router'
import { rootAuthLoader, clerkMiddleware } from '@clerk/react-router/server'
import { ClerkProvider } from '@clerk/react-router'
import type { Route } from './+types/root'

export const middleware: Route.MiddlewareFunction[] = [clerkMiddleware()]

export async function loader(args: Route.LoaderArgs) {
  return rootAuthLoader(args)
}

export default function App({ loaderData }: Route.ComponentProps) {
  return (
    <ClerkProvider loaderData={loaderData}>
      <Outlet />
    </ClerkProvider>
  )
}
```

在 `@clerk/react-router` 中没有 `ClerkApp` HOC（那曾是 `@clerk/remix` API）。
在默认导出内部渲染 `<ClerkProvider loaderData={loaderData}>` 并将其传递给根路由的 `loaderData`。

### 3. react-router.config.ts（仅 v7）

```ts
import type { Config } from '@react-router/dev/config'

export default {
  future: {
    v8_middleware: true,
  },
} satisfies Config
```

在 v8 上，完全省略 `future` 块——该标志不再存在。

> **必需**：必须在 `root.tsx` 的加载器中调用 `rootAuthLoader`。如果没有它，`getAuth` 在嵌套加载器中会抛出错误。

## 思维模型

React Router v7/v8 使用中间件 + 加载器管道。Clerk 插入到两个层中：

- **中间件** (`clerkMiddleware()`) — 每次请求运行，将认证附加到上下文
- **`rootAuthLoader`** — 在 `root.tsx` 中必需，以将 Clerk 状态传递给客户端
- **`getAuth(args)`** — 在任何加载器/操作内部调用以获取当前用户

```
请求 → clerkMiddleware() → rootAuthLoader → 页面加载器 → 组件
                 ↓                   ↓               ↓
           附加认证      注入状态     获取当前用户
           到上下文         到响应       读取上下文
```

## 加载器中的认证

```tsx
import { getAuth } from '@clerk/react-router/server'
import type { Route } from './+types/dashboard'

export async function loader(args: Route.LoaderArgs) {
  const { userId } = await getAuth(args)
  if (!userId) throw redirect('/sign-in')

  const data = await fetchUserData(userId)
  return { data }
}
```

## 操作中的认证

```tsx
import { getAuth } from '@clerk/react-router/server'

export async function action(args: Route.ActionArgs) {
  const { userId, orgId } = await getAuth(args)
  if (!userId) throw new Response('Unauthorized', { status: 401 })

  const formData = await args.request.formData()
  await saveData(userId, orgId, formData)
  return redirect('/dashboard')
}
```

## 客户端组件

```tsx
import { useAuth, useUser } from '@clerk/react-router'

export function Profile() {
  const { userId, isSignedIn } = useAuth()
  const { user } = useUser()
  if (!isSignedIn) return null
  return <p>{user?.firstName}</p>
}
```

## 组织切换

```tsx
import { OrganizationSwitcher } from '@clerk/react-router'

export function Nav() {
  return <OrganizationSwitcher afterSelectOrganizationUrl="/dashboard" />
}
```

```tsx
export async function loader(args: Route.LoaderArgs) {
  const { userId, orgId } = await getAuth(args)
  if (!userId) throw redirect('/sign-in')
  if (!orgId) throw redirect('/select-org')

  return { data: await fetchOrgData(orgId) }
}
```

## 常见陷阱

| 症状 | 原因 | 修复 |
|---------|-------|-----|
| `useNavigate() may be used only in the context of a <Router>` 从 ClerkProvider 在开发（v8）期间 SSR 抛出 | Vite 开发 SSR 外部化 `@clerk/react-router`，然后加载 react-router 的生产构建，而应用程序使用开发构建——两个 Router 上下文。`npm ls` 中的单个副本并不排除这种情况。 | 在 `vite.config.ts` 中添加 `ssr: { noExternal: ['@clerk/react-router'] }`。不要降级到 v7 |
| 构建错误：`ClerkApp` 未导出 | `ClerkApp` 在 `@clerk/react-router` 中不存在 | 在 `root.tsx` 的默认导出中使用 `<ClerkProvider loaderData={loaderData}>` |
| `clerkMiddleware() not detected` | 缺少中间件（或在 v7 上，缺少 `v8_middleware` 未来标志） | 从根路由导出 `middleware = [clerkMiddleware()]`；在 v7 上还设置 `future: { v8_middleware: true }` |
| 未知未来标志错误/警告（v8） | 升级后 `react-router.config.ts` 中保留 `v8_middleware` 标志 | 删除 `future.v8_middleware` 条目——v8 中中间件始终启用 |
| `getAuth` 返回空 userId | 未调用 `rootAuthLoader` | 在 `root.tsx` 加载器中调用 `rootAuthLoader(args)` |
| 无限重定向循环 | 重定向目标是受保护的 | 从保护检查中排除 `/sign-in` |
| `redirect` 在操作中不起作用 | 使用 `Response` 而不是 `throw redirect()` | 使用 `throw redirect('/path')` 从 `react-router` |

## 导入映射

| 内容 | 从...导入 |
|------|-------------|
| `getAuth` | `@clerk/react-router/server` |
| `rootAuthLoader` | `@clerk/react-router/server` |
| `clerkMiddleware` | `@clerk/react-router/server` |
| `ClerkProvider` | `@clerk/react-router` |
| `useAuth`, `useUser` | `@clerk/react-router` |
| `OrganizationSwitcher` | `@clerk/react-router` |

## 参考资料链接

- `clerk-setup` - 初始 Clerk 安装
- `clerk-custom-ui` - 自定义流程和外观
- `clerk-orgs` - B2B 组织

## 文档

[React Router SDK](https://clerk.com/docs/react-router/getting-started/quickstart)
