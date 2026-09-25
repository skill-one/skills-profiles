# Next.js 应用路由模式

Next.js 14+ 应用路由架构、服务器组件和现代全栈 React 开发的全面模式。

## 何时使用此技能

- 使用应用路由构建新的 Next.js 应用
- 从页面路由迁移到应用路由
- 实现服务器组件和流式传输
- 设置并行和拦截路由
- 优化数据获取和缓存
- 使用服务器操作构建全栈功能

## 核心概念

### 1. 渲染模式

| 模式                  | 位置        | 使用场景                               |
| --------------------- | ------------ | ----------------------------------------- |
| **服务器组件**        | 仅服务器    | 数据获取、复杂计算、密钥               |
| **客户端组件**        | 浏览器      | 交互、钩子、浏览器 API                |
| **静态**              | 构建时     | 很少变化的内容                         |
| **动态**              | 请求时     | 个性化或实时数据                      |
| **流式传输**          | 渐进式     | 大页面、慢速数据源                    |

### 2. 文件约定

```
app/
├── layout.tsx       # 共享 UI 包装器
├── page.tsx         # 路由 UI
├── loading.tsx      # 加载 UI (Suspense)
├── error.tsx        # 错误边界
├── not-found.tsx    # 404 UI
├── route.ts         # API 端点
├── template.tsx     # 重新挂载的布局
├── default.tsx      # 并行路由回退
└── opengraph-image.tsx  # OG 图片生成
```

## 快速入门

```typescript
// app/layout.tsx
import { Inter } from 'next/font/google'
import { Providers } from './providers'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: { default: '我的应用', template: '%s | 我的应用' },
  description: '使用 Next.js 应用路由构建',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}

// app/page.tsx - 默认为服务器组件
async function getProducts() {
  const res = await fetch('https://api.example.com/products', {
    next: { revalidate: 3600 }, // ISR: 每小时重新验证
  })
  return res.json()
}

export default async function HomePage() {
  const products = await getProducts()

  return (
    <main>
      <h1>产品</h1>
      <ProductGrid products={products} />
    </main>
  )
}
```

## 详细模式和实例

详细模式文档位于 `references/details.md`。当上层导航层级不足时，请阅读该文件。

## 最佳实践

### 应该做

- **从服务器组件开始** - 仅在需要时添加 'use client'
- **集中数据获取** - 在使用数据的地方获取数据
- **使用 Suspense 边界** - 为慢速数据启用流式传输
- **利用并行路由** - 独立的加载状态
- **使用服务器操作** - 用于具有渐进增强的突变

### 不应该做

- **不要传递可序列化数据** - 服务器→客户端边界限制
- **不要在服务器组件中使用钩子** - 没有 useState、useEffect
- **不要在客户端组件中获取数据** - 使用服务器组件或 React Query
- **不要过度嵌套布局** - 每个布局都会增加组件树
- **不要忽略加载状态** - 始终提供 loading.tsx 或 Suspense
