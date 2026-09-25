## 概述

TanStack Router 是一个适用于 React（以及 Solid）应用的完全类型安全的路由器。它提供基于文件的路由、一流的搜索参数管理、内置的数据加载、代码拆分和深度 TypeScript 集成。它是 TanStack Start（全栈框架）的路由基础。

**包：** `@tanstack/react-router`
**CLI：** `@tanstack/router-cli` 或 `@tanstack/router-plugin`（Vite/Rspack/Webpack）
**开发者工具：** `@tanstack/react-router-devtools`

## 安装

```bash
npm install @tanstack/react-router
# 用于基于文件的 Vite 路由：
npm install -D @tanstack/router-plugin
# 或独立的 CLI：
npm install -D @tanstack/router-cli
```

## 核心概念

### 路由树

路由以树状结构组织。根路由是顶层布局，子路由嵌套在其下方。

```tsx
import { createRootRoute, createRoute, createRouter } from '@tanstack/react-router'

const rootRoute = createRootRoute({
  component: RootLayout,
})

const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/',
  component: HomePage,
})

const aboutRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/about',
  component: AboutPage,
})

const routeTree = rootRoute.addChildren([indexRoute, aboutRoute])
const router = createRouter({ routeTree })
```

### 基于文件的路由

基于文件的路由会自动根据您的文件结构生成路由树。使用 Vite 插件配置：

```ts
// vite.config.ts
import { defineConfig } from 'vite'
import { TanStackRouterVite } from '@tanstack/router-plugin/vite'

export default defineConfig({
  plugins: [
    TanStackRouterVite(),
    // ... 其他插件
  ],
})
```

#### 文件命名约定

| 文件模式 | 路由类型 | 示例路径 |
|---|---|---|
| `__root.tsx` | 根布局 | N/A（包含所有） |
| `index.tsx` | 索引路由 | `/` |
| `about.tsx` | 静态路由 | `/about` |
| `$postId.tsx` | 动态参数 | `/posts/$postId` |
| `posts.tsx` | 布局路由 | `/posts/*`（布局） |
| `posts/index.tsx` | 嵌套索引 | `/posts` |
| `posts/$postId.tsx` | 嵌套动态 | `/posts/123` |
| `posts_.$postId.tsx` | 无路径布局 | `/posts/123`（不同布局） |
| `_layout.tsx` | 无路径布局 | N/A（分组路由） |
| `_layout/dashboard.tsx` | 分组路由 | `/dashboard` |
| `$.tsx` | Splat/捕获所有 | `/*` |
| `posts.$postId.edit.tsx` | 点表示法 | `/posts/123/edit` |

#### 特殊前缀
- `_` 前缀：无路径路由（无 URL 段的布局组）
- `$` 前缀：动态路径参数
- `(文件夹)` 括号：路由组（组织性，无 URL 影响）

### 路由配置

每个路由可以定义：

```tsx
// routes/posts.$postId.tsx
import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/posts/$postId')({
  // 路径参数验证
  params: {
    parse: (params) => ({ postId: Number(params.postId) }),
    stringify: (params) => ({ postId: String(params.postId) }),
  },

  // 搜索参数验证
  validateSearch: (search: Record<string, unknown>) => {
    return {
      page: Number(search.page ?? 1),
      filter: (search.filter as string) || '',
    }
  },

  // 数据加载
  loader: async ({ params, context, abortController }) => {
    return fetchPost(params.postId)
  },

  // 加载器依赖（当这些变化时重新运行加载器）
  loaderDeps: ({ search }) => ({ page: search.page }),

  // 缓存加载器数据的过期时间
  staleTime: 5_000,

  // 预加载过期时间
  preloadStaleTime: 30_000,

  // 错误组件
  errorComponent: PostErrorComponent,

  // 等待/加载中组件
  pendingComponent: PostLoadingComponent,

  // 404 组件
  notFoundComponent: PostNotFoundComponent,

  // 加载前钩子（认证、重定向）
  beforeLoad: async ({ context, location }) => {
    if (!context.auth.isAuthenticated) {
      throw redirect({
        to: '/login',
        search: { redirect: location.href },
      })
    }
  },

  // 头部/元数据管理
  head: () => ({
    meta: [{ title: '帖子详情' }],
  }),

  // 组件
  component: PostComponent,
})

function PostComponent() {
  const { postId } = Route.useParams()
  const post = Route.useLoaderData()
  const { page, filter } = Route.useSearch()

  return <div>{post.title}</div>
}
```

## 数据加载

### 路由加载器

```tsx
export const Route = createFileRoute('/posts')({
  loader: async ({ context }) => {
    // 访问路由上下文（例如，queryClient）
    const posts = await context.queryClient.ensureQueryData({
      queryKey: ['posts'],
      queryFn: fetchPosts,
    })
    return { posts }
  },
  component: PostsComponent,
})

function PostsComponent() {
  const { posts } = Route.useLoaderData()
  // ...
}
```

### 加载器依赖

控制何时重新执行加载器：

```tsx
export const Route = createFileRoute('/posts')({
  loaderDeps: ({ search: { page, filter } }) => ({ page, filter }),
  loader: async ({ deps: { page, filter } }) => {
    return fetchPosts({ page, filter })
  },
})
```

### 延迟数据加载

流式传输非关键数据：

```tsx
import { Await, defer } from '@tanstack/react-router'

export const Route = createFileRoute('/dashboard')({
  loader: async () => {
    const criticalData = await fetchCriticalData()
    const deferredData = defer(fetchSlowData())
    return { criticalData, deferredData }
  },
  component: DashboardComponent,
})

function DashboardComponent() {
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

### 基于上下文的数据加载

通过路由上下文提供共享依赖：

```tsx
// 创建带上下文的路由
const router = createRouter({
  routeTree,
  context: {
    queryClient,
    auth: undefined!, // 将由 RouterProvider 提供
  },
})

// 在根/应用组件中
function App() {
  const auth = useAuth()
  return <RouterProvider router={router} context={{ auth }} />
}

// 在路由中
export const Route = createFileRoute('/protected')({
  beforeLoad: ({ context }) => {
    if (!context.auth.user) throw redirect({ to: '/login' })
  },
  loader: ({ context }) => {
    return context.queryClient.ensureQueryData(userQueryOptions())
  },
})
```

## 搜索参数

### 验证

```tsx
import { z } from 'zod'

const postSearchSchema = z.object({
  page: z.number().default(1),
  filter: z.string().default(''),
  sort: z.enum(['date', 'title']).default('date'),
})

export const Route = createFileRoute('/posts')({
  validateSearch: postSearchSchema,
  // 或手动验证：
  // validateSearch: (search) => postSearchSchema.parse(search),
})
```

### 读取搜索参数

```tsx
function PostsComponent() {
  // 从路由
  const { page, filter, sort } = Route.useSearch()

  // 或从任何使用 useSearch 钩子的组件
  const search = useSearch({ from: '/posts' })
}
```

### 更新搜索参数

```tsx
import { useNavigate } from '@tanstack/react-router'

function Pagination() {
  const navigate = useNavigate()
  const { page } = Route.useSearch()

  return (
    <button
      onClick={() =>
        navigate({
          search: (prev) => ({ ...prev, page: prev.page + 1 }),
        })
      }
    >
      下一页
    </button>
  )
}

// 或通过 Link 组件
<Link
  to="/posts"
  search={(prev) => ({ ...prev, page: 2 })}
>
  第 2 页
</Link>
```

### 搜索参数选项

```tsx
const router = createRouter({
  routeTree,
  // 自定义序列化
  search: {
    strict: true, // 拒绝未知参数
  },
  // 默认搜索参数序列化器
  stringifySearch: defaultStringifySearch,
  parseSearch: defaultParseSearch,
})
```

## 导航

### Link 组件

```tsx
import { Link } from '@tanstack/react-router'

// 静态路由
<Link to="/about">关于</Link>

// 带参数的动态路由
<Link to="/posts/$postId" params={{ postId: '123' }}>
  帖子 123
</Link>

// 带搜索参数
<Link to="/posts" search={{ page: 2, filter: 'react' }}>
  第 2 页
</Link>

// 活跃链接样式
<Link
  to="/posts"
  activeProps={{ className: 'active' }}
  inactiveProps={{ className: 'inactive' }}
  activeOptions={{ exact: true }}
>
  帖子
</Link>

// 预加载
<Link to="/posts" preload="intent">帖子</Link>
<Link to="/dashboard" preload="viewport">仪表盘</Link>

// Hash
<Link to="/docs" hash="api-reference">API 参考</Link>
```

### 程序化导航

```tsx
import { useNavigate, useRouter } from '@tanstack/react-router'

function MyComponent() {
  const navigate = useNavigate()
  const router = useRouter()

  // 导航到路由
  navigate({ to: '/posts', search: { page: 1 } })

  // 使用 replace 导航
  navigate({ to: '/posts', replace: true })

  // 相对导航
  navigate({ to: '.', search: (prev) => ({ ...prev, page: 2 }) })

  // 返回/前进
  router.history.back()
  router.history.forward()

  // 使当前路由失效并重新加载
  router.invalidate()
}
```

### 重定向

```tsx
import { redirect } from '@tanstack/react-router'

// 在 beforeLoad 或 loader 中
throw redirect({
  to: '/login',
  search: { redirect: location.href },
  // 可选状态码
  statusCode: 301, // 永久重定向（SSR）
})
```

### 导航阻止

```tsx
import { useBlocker } from '@tanstack/react-router'

function FormComponent() {
  const [isDirty, setIsDirty] = useState(false)

  useBlocker({
    shouldBlockFn: () => isDirty,
    withResolver: true, // 显示确认对话框
  })

  // 或使用自定义 UI
  const { proceed, reset, status } = useBlocker({
    shouldBlockFn: () => isDirty,
  })

  if (status === 'blocked') {
    return (
      <div>
        <p>您确定要离开吗？</p>
        <button onClick={proceed}>离开</button>
        <button onClick={reset}>留下</button>
      </div>
    )
  }
}
```

## 代码拆分

### 自动（基于文件的路由）

使用基于文件的路由时，创建一个懒加载文件：

```
routes/
  posts.tsx          # 关键：loader, beforeLoad, meta
  posts.lazy.tsx     # 懒加载：component, pendingComponent, errorComponent
```

```tsx
// posts.tsx（立即加载）
export const Route = createFileRoute('/posts')({
  loader: () => fetchPosts(),
})

// posts.lazy.tsx（懒加载）
import { createLazyFileRoute } from '@tanstack/react-router'

export const Route = createLazyFileRoute('/posts')({
  component: PostsComponent,
  pendingComponent: PostsLoading,
  errorComponent: PostsError,
})
```

### 手动代码拆分

```tsx
const postsRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/posts',
  loader: () => fetchPosts(),
}).lazy(() => import('./posts.lazy').then((d) => d.Route))
```

## 预加载

```tsx
// 路由级默认值
const router = createRouter({
  routeTree,
  defaultPreload: 'intent', // 'intent' | 'viewport' | 'render' | false
  defaultPreloadStaleTime: 30_000, // 30 秒
})

// 路由级
export const Route = createFileRoute('/posts/$postId')({
  // 加载器数据的过期时间
  staleTime: 5_000,
  // 预加载数据保持新鲜的时间
  preloadStaleTime: 30_000,
})

// Link 级
<Link to="/posts" preload="intent" preloadDelay={100}>
  帖子
</Link>
```

## 类型安全

### 注册路由类型

```tsx
// 声明模块以进行类型推断
declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router
  }
}
```

### 类型安全的钩子

所有钩子都基于路由树完全类型化：

```tsx
// useParams - 类型化为路由的 params
const { postId } = useParams({ from: '/posts/$postId' })

// useSearch - 类型化为路由的搜索模式
const { page } = useSearch({ from: '/posts' })

// useLoaderData - 类型化为加载器返回
const data = useLoaderData({ from: '/posts/$postId' })

// useRouteContext - 类型化为路由上下文
const { auth } = useRouteContext({ from: '/protected' })
```

### 路由泛型

```tsx
import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/posts/$postId')({
  // TypeScript 推断：
  // params: { postId: string }
  // search: 验证的搜索模式类型
  // loaderData: 加载器返回类型
  // context: 路由上下文类型
})
```

## 认证路由

```tsx
// __root.tsx
export const Route = createRootRouteWithContext<{
  auth: AuthContext
}>()({
  component: RootComponent,
})

// _authenticated.tsx（无路径布局用于认证）
export const Route = createFileRoute('/_authenticated')({
  beforeLoad: ({ context, location }) => {
    if (!context.auth.isAuthenticated) {
      throw redirect({
        to: '/login',
        search: { redirect: location.href },
      })
    }
  },
})

// _authenticated/dashboard.tsx
export const Route = createFileRoute('/_authenticated/dashboard')({
  component: Dashboard, // 只有在认证时才可访问
})
```

## 滚动恢复

```tsx
const router = createRouter({
  routeTree,
  // 启用滚动恢复
  defaultScrollRestoration: true,
})

// 或每条路由
export const Route = createFileRoute('/posts')({
  // 导航时滚动到顶部
  scrollRestoration: true,
})

// 自定义滚动恢复键
<ScrollRestoration
  getKey={(location) => location.pathname}
/>
```

## 路由掩码

显示与实际路由不同的 URL：

```tsx
<Link
  to="/photos/$photoId"
  params={{ photoId: photo.id }}
  mask={{ to: '/photos', search: { photoId: photo.id } }}
>
  查看照片
</Link>

// 或程序化
navigate({
  to: '/photos/$photoId',
  params: { photoId: photo.id },
  mask: { to: '/photos', search: { photoId: photo.id } },
})
```

## 未找到处理

```tsx
// 全局 404
const router = createRouter({
  routeTree,
  defaultNotFoundComponent: () => <div>页面未找到</div>,
})

// 路由级 404
export const Route = createFileRoute('/posts/$postId')({
  loader: async ({ params }) => {
    const post = await fetchPost(params.postId)
    if (!post) throw notFound()
    return post
  },
  notFoundComponent: () => <div>帖子未找到</div>,
})
```

## 头部管理

```tsx
export const Route = createFileRoute('/posts/$postId')({
  head: ({ loaderData }) => ({
    meta: [
      { title: loaderData.title },
      { name: 'description', content: loaderData.excerpt },
      { property: 'og:title', content: loaderData.title },
    ],
    links: [
      { rel: 'canonical', href: `https://example.com/posts/${loaderData.id}` },
    ],
  }),
})
```

## 与 TanStack Query 集成

```tsx
import { queryOptions } from '@tanstack/react-query'

const postsQueryOptions = queryOptions({
  queryKey: ['posts'],
  queryFn: fetchPosts,
})

export const Route = createFileRoute('/posts')({
  loader: ({ context: { queryClient } }) => {
    // 确保数据在缓存中，如果新鲜则不会重新获取
    return queryClient.ensureQueryData(postsQueryOptions)
  },
  component: PostsComponent,
})

function PostsComponent() {
  // 使用相同的查询选项进行响应式更新
  const { data: posts } = useSuspenseQuery(postsQueryOptions)
  return <PostsList posts={posts} />
}
```

## 路由钩子参考

| 钩子 | 目的 |
|------|---------|
| `useRouter()` | 访问路由实例 |
| `useRouterState()` | 订阅路由状态 |
| `useParams()` | 获取路由路径参数 |
| `useSearch()` | 获取验证后的搜索参数 |
| `useLoaderData()` | 获取路由加载器数据 |
| `useRouteContext()` | 获取路由上下文 |
| `useNavigate()` | 获取导航函数 |
| `useLocation()` | 获取当前位置 |
| `useMatches()` | 获取所有匹配的路由 |
| `useMatch()` | 获取特定路由匹配 |
| `useBlocker()` | 阻止导航 |
| `useLinkProps()` | 获取自定义组件的链接属性 |
| `useMatchRoute()` | 检查路由是否匹配 |

## 最佳实践

1. **使用基于文件的路由**（对于大多数应用程序）- 它更简单且自动生成路由树
2. **使用 Zod 或自定义验证器验证搜索参数**以实现类型安全
3. **使用 `loaderDeps`** 控制基于搜索参数变化时加载器何时重新执行
4. **利用上下文**进行依赖注入（QueryClient、认证状态）
5. **使用 `beforeLoad`** 进行认证保护，而不是在组件中
6. **分离关键与懒加载代码** - 将加载器放在主文件中，组件放在 `.lazy.tsx` 中
7. **使用 `preload="intent"`** 在链接上以获得感知性能
8. **使用 `staleTime`** 防止在导航期间不必要的重新获取
9. **注册路由类型**以在整个应用程序中实现完整的 TypeScript 推断
10. **使用 `notFound()`** 而不是条件渲染来处理 404 状态
11. **将搜索参数逻辑与拥有它们的路由放在一起**
12. **使用无路径布局**（`_authenticated`）用于共享认证/布局逻辑而无需 URL 段

## 常见陷阱

- 忘记注册路由类型（`declare module`）
- 加载器依赖于搜索参数时未使用 `loaderDeps`（导致数据陈旧）
- 在组件中放置认证检查而不是 `beforeLoad`（受保护的页面闪烁）
- 未使用 `pendingComponent` 处理加载状态
- 使用 `useEffect` 进行数据获取而不是路由加载器
- 直接修改搜索参数而不是使用 navigate/Link
- 忘记将应用程序包装在 `RouterProvider` 中
- 在基于代码的路由定义中忘记 `getParentRoute`
