# TanStack Start 技能入门

## 概述

TanStack Start 是基于 TanStack Router 构建的全栈 React 框架，由 Vite 和 Nitro（通过 Vinxi）提供支持。它提供服务器端渲染、流式传输、服务器函数（RPC）、中间件、API 路由，并通过 Nitro 预设部署到任何平台。

**包:** `@tanstack/react-start`
**路由插件:** `@tanstack/router-plugin`
**构建工具:** Vinxi (Vite + Nitro)
**状态:** RC (候选发布版本)
**RSC 支持:** React 服务器组件支持正在积极开发中，并将作为非破坏性 v1.x 版本发布

## 安装与项目设置

```bash
npx @tanstack/cli create my-app
# 或者手动:
npm install @tanstack/react-start @tanstack/react-router react react-dom
npm install -D @tanstack/router-plugin typescript vite vite-tsconfig-paths
```

### 项目结构

```
my-app/
  app/
    routes/
      __root.tsx          # 根布局
      index.tsx           # / 路由
      posts.$postId.tsx   # /posts/:postId
      api/
        users.ts          # /api/users API 路由
    client.tsx            # 客户端入口
    router.tsx            # 路由创建
    ssr.tsx               # SSR 入口
    routeTree.gen.ts      # 自动生成的路由树
  app.config.ts           # TanStack Start 配置
  tsconfig.json
  package.json
```

### 配置 (`app.config.ts`)

```typescript
import { defineConfig } from '@tanstack/react-start/config'
import viteTsConfigPaths from 'vite-tsconfig-paths'

export default defineConfig({
  vite: {
    plugins: [
      viteTsConfigPaths({ projects: ['./tsconfig.json'] }),
    ],
  },
  server: {
    preset: 'node-server', // 'vercel' | 'netlify' | 'cloudflare-pages' | 等
  },
  tsr: {
    appDirectory: './app',
    routesDirectory: './app/routes',
    generatedRouteTree: './app/routeTree.gen.ts',
  },
})
```

## 服务器函数 (`createServerFn`)

服务器函数提供客户端与服务器之间的类型安全 RPC 调用。

### 基本服务器函数

```typescript
import { createServerFn } from '@tanstack/react-start'

// GET (数据获取，可缓存)
const getUsers = createServerFn()
  .handler(async () => {
    const users = await db.query.users.findMany()
    return users
  })

// POST (变异操作，副作用)
const createUser = createServerFn({ method: 'POST' })
  .validator((data: { name: string; email: string }) => data)
  .handler(async ({ data }) => {
    const user = await db.insert(users).values(data).returning()
    return user
  })
```

### 使用 Zod 验证

```typescript
import { z } from 'zod'

const updateUser = createServerFn({ method: 'POST' })
  .validator(
    z.object({
      id: z.string(),
      name: z.string().min(1),
      email: z.string().email(),
    })
  )
  .handler(async ({ data }) => {
    // data 完全类型化: { id: string; name: string; email: string }
    return await db.update(users).set(data).where(eq(users.id, data.id))
  })
```

## 中间件

### 创建中间件

```typescript
import { createMiddleware } from '@tanstack/react-start'

const loggingMiddleware = createMiddleware().handler(async ({ next }) => {
  console.log('请求开始')
  const result = await next()
  console.log('请求完成')
  return result
})
```

### 带上下文的认证中间件

```typescript
const authMiddleware = createMiddleware().handler(async ({ next }) => {
  const request = getWebRequest()
  const session = await getSession(request)

  if (!session?.user) {
    throw redirect({ to: '/login' })
  }

  // 向处理器传递类型化的上下文
  return next({ context: { user: session.user } })
})
```

### 链式中间件

```typescript
const adminMiddleware = createMiddleware()
  .middleware([authMiddleware])
  .handler(async ({ next, context }) => {
    // context.user 来自 authMiddleware 的类型化
    if (context.user.role !== 'admin') {
      throw redirect({ to: '/unauthorized' })
    }
    return next({ context: { isAdmin: true } })
  })

// 使用
const adminAction = createServerFn({ method: 'POST' })
  .middleware([adminMiddleware])
  .handler(async ({ context }) => {
    // context: { user: User; isAdmin: boolean }
    return { success: true }
  })
```

## API 路由（服务器路由）

```typescript
// app/routes/api/users.ts
import { createAPIFileRoute } from '@tanstack/react-start/api'

export const APIRoute = createAPIFileRoute('/api/users')({
  GET: async ({ request }) => {
    const users = await db.query.users.findMany()
    return Response.json(users)
  },
  POST: async ({ request }) => {
    const body = await request.json()
    const user = await db.insert(users).values(body).returning()
    return new Response(JSON.stringify(user), { status: 201 })
  },
})
```

## SSR 策略

### 流式 SSR（默认）

```typescript
export const Route = createFileRoute('/dashboard')({
  loader: async () => ({
    criticalData: await fetchCriticalData(),
    deferredData: defer(fetchSlowData()),
  }),
  component: Dashboard,
})

function Dashboard() {
  const { criticalData, deferredData } = Route.useLoaderData()
  return (
    <div>
      <CriticalSection data={criticalData} />
      <Suspense fallback={<Loading />}>
        <Await promise={deferredData}>
          {(data) => <SlowSection data={data} />}
        </Await>
      </Suspense>
    </div>
  )
}
```

## 部署

### 支持的平台（Nitro 预设）

```typescript
// app.config.ts
export default defineConfig({
  server: {
    preset: 'node-server',        // 自托管 Node.js
    // preset: 'vercel',          // Vercel
    // preset: 'netlify',         // Netlify
    // preset: 'cloudflare-pages', // Cloudflare Pages
    // preset: 'aws-lambda',      // AWS Lambda
    // preset: 'deno-server',     // Deno Deploy
    // preset: 'bun',             // Bun
  },
})
```

## 最佳实践

1. **对所有服务器函数输入使用验证器** - 运行时安全性和 TypeScript 推断
2. **组合中间件** 用于跨切关注点（认证、日志记录、速率限制）
3. **使用 `createServerFn` GET** 进行数据获取（可缓存、可预加载）
4. **使用 `createServerFn` POST** 进行变异操作和副作用
5. **使用 `beforeLoad`** 进行路由级认证守卫
6. **使用 `defer()`** 对非关键数据进行流式传输以改善 TTFB
7. **在路由上设置 `defaultPreload: 'intent'`** 以实现即时导航
8. **将服务器函数与使用它们的路由放在一起**

## 常见陷阱

- 服务器函数不能捕获客户端变量（它们被提取到单独的包中）
- 从服务器函数返回的数据必须是可序列化的
- 在加载器中忘记 `await` 导致流式传输问题
- 在客户端包中导入服务器端代码导致构建错误
- 缺少 `declare module '@tanstack/react-router'` 会导致所有类型安全丢失
