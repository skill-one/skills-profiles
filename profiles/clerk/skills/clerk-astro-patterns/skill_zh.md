# Astro 模式

SDK: `@clerk/astro` v3+。需要 Astro 4.15+。

## 你需要什么？

| 任务 | 参考 |
|------|-----------|
| 配置中间件 | references/middleware.md |
| 保护 SSR 页面 | references/ssr-pages.md |
| 在岛组件中使用 Clerk | references/island-components.md |
| API 路由中的认证 | references/api-routes.md |
| 在 Astro 中使用 React 和 Clerk | references/astro-react.md |

## 思维模型

每个页面在 Astro 中有两种渲染模式：**SSR** 和 **静态预渲染**。Clerk 在每种模式下的工作方式不同：

- **SSR 页面** — 使用 `Astro.locals.auth()`，该值由中间件填充
- **静态页面** (`export const prerender = true`) — Clerk 中间件会跳过它们；在岛中使用客户端钩子
- **岛** — React/Vue/Svelte 组件；使用 `useAuth()` 和其他来自 `@clerk/astro/react` 的钩子

```
请求 → clerkMiddleware() → SSR 页面 → Astro.locals.auth()
                                ↓
                         岛 (.client) → useAuth() 钩子
```

## 设置

### astro.config.mjs

```ts
import { defineConfig } from 'astro/config'
import clerk from '@clerk/astro'

export default defineConfig({
  integrations: [clerk()],
  output: 'server',
})
```

### src/middleware.ts

```ts
import { clerkMiddleware, createRouteMatcher } from '@clerk/astro/server'

const isProtectedRoute = createRouteMatcher(['/dashboard(.*)'])

export const onRequest = clerkMiddleware((auth, context, next) => {
  if (isProtectedRoute(context.request) && !auth().userId) {
    return auth().redirectToSignIn()
  }
  return next()
})
```

## SSR 页面认证

```astro
---
const { userId, orgId } = Astro.locals.auth()
if (!userId) return Astro.redirect('/sign-in')
---

<h1>仪表盘</h1>
```

## 常见陷阱

| 症状 | 原因 | 解决方法 |
|---------|-------|-----|
| `Astro.locals.auth` 未定义 | 缺少中间件 | 在 `src/middleware.ts` 中添加 `clerkMiddleware` |
| 开发环境中认证正常，但生产环境中不正常 | 全局 `output: 'static'` | 将 `output` 设置为 `'server'` 或 `'hybrid'` 用于受保护的页面 |
| 静态页面没有认证 | 预渲染页面会跳过中间件 | 使用 `export const prerender = false` 或移动到岛 |
| 岛对登录没有响应 | 缺少 `client:load` 指令 | 在岛组件中添加 `client:load` |

## 导入映射

| 内容 | 导入自 |
|------|-------------|
| `clerkMiddleware`, `createRouteMatcher` | `@clerk/astro/server` |
| `useAuth`, `useUser`, `UserButton` | `@clerk/astro/react` |
| Astro 组件 (`<SignIn>`, 等.) | `@clerk/astro/components` |

## 环境变量

```
# .env
PUBLIC_CLERK_PUBLISHABLE_KEY=pk_...
CLERK_SECRET_KEY=sk_...
```

Astro 使用 `PUBLIC_` 前缀用于客户端暴露的变量（不是 `NEXT_PUBLIC_`）。

## 参考文档

- `clerk-setup` - 初始 Clerk 安装
- `clerk-custom-ui` - 自定义流程和外观
- `clerk-orgs` - B2B 组织

## 文档

[Astro SDK](https://clerk.com/docs/astro/getting-started/quickstart)
