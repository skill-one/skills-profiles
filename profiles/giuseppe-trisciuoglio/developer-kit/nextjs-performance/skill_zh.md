# Next.js 性能优化

提供针对 Next.js 应用的优化专家指导，重点关注核心网络生命体征、现代模式和实践最佳做法。

## 概述

本技能为 Next.js 应用优化提供全面指导。它涵盖了核心网络生命体征优化（LCP、INP、CLS）、现代 React 模式、服务器组件、缓存策略和捆绑包优化技术。专为已熟悉 React/Next.js 并希望实现生产级优化的开发者设计。

## 使用场景

在开发 Next.js 应用时，需要：

- 优化核心网络生命体征（LCP、INP、CLS）以提升性能和 SEO
- 使用 `next/image` 实现图像优化，加快加载速度
- 使用 `next/font` 配置字体优化，消除布局偏移
- 使用 `unstable_cache`、`revalidateTag` 或 ISR 设置缓存策略
- 将客户端组件转换为服务器组件以减小捆绑包大小
- 实现 Suspense 流式传输以实现渐进式页面加载
- 通过代码拆分和动态导入分析和减少捆绑包大小
- 配置元数据和 SEO 以提升搜索引擎可见性
- 优化 API 路由处理程序以提升性能
- 应用 Next.js 16 和 React 19 的现代模式

### 涵盖范围

- **核心网络生命体征优化**（LCP、INP、CLS）
- 使用 `next/image` 的**图像优化**
- 使用 `next/font` 的**字体优化**
- **缓存策略**（`unstable_cache`、`revalidateTag`、ISR）
- 服务器组件模式及客户端到服务器的转换
- 用于渐进式加载的**流式传输和 Suspense**
- **捆绑包优化**和代码拆分
- **元数据和 SEO**配置
- **路由处理程序**优化
- **Next.js 16 + React 19**模式

## 使用说明

### 开始前

1. 使用 Lighthouse **分析当前性能**
2. **识别瓶颈** - 在 Chrome 开发者工具或 PageSpeed Insights 中检查核心网络生命体征
3. **确定优化优先级**：
   - LCP 问题 → 重点关注图像、字体
   - INP 问题 → 减少 JS，使用服务器组件
   - CLS 问题 → 添加尺寸，使用 next/font

### 如何使用此技能

1. 根据您正在优化的领域**加载相关参考文件**：
   - 图像问题 → `references/image-optimization.md`
   - 字体/布局偏移 → `references/font-optimization.md`
   - 缓存 → `references/caching-strategies.md`
   - 组件架构 → `references/server-components.md`

2. **遵循快速模式**进行常见优化
3. **应用前后转换**以改进现有代码
4. 修改后使用 Lighthouse **验证改进**

### 核心原则

1. **优先使用服务器组件** - 仅在必要时使用 'use client'（浏览器 API、交互性）
2. **尽可能低地加载组件** - 将客户端组件保持在叶节点
3. **使用 Suspense 边界** - 启用流式传输和渐进式加载
4. **适当缓存** - 使用标签进行粒度化重新验证
5. **前后测量** - 始终使用真实指标验证改进

## 示例

### 示例 1：将客户端组件转换为服务器组件

**之前（带 useEffect 的客户端组件）：**
```tsx
'use client'
import { useEffect, useState } from 'react'

export default function ProductList() {
  const [products, setProducts] = useState([])

  useEffect(() => {
    fetch('/api/products').then(r => r.json()).then(setProducts)
  }, [])

  return <ul>{products.map(p => <li key={p.id}>{p.name}</li>)}</ul>
}
```

**之后（服务器组件直接访问数据）：**
```tsx
import { db } from '@/lib/db'

export default async function ProductList() {
  const products = await db.product.findMany()
  return <ul>{products.map(p => <li key={p.id}>{p.name}</li>)}</ul>
}
```

### 示例 2：为 LCP 优化图像

```tsx
import Image from 'next/image'

export function Hero() {
  return (
    <div className="relative w-full h-[600px]">
      <Image
        src="/hero.jpg"
        alt="Hero"
        fill
        priority          // 禁用懒加载以用于 LCP
        sizes="100vw"
        className="object-cover"
      />
    </div>
  )
}
```

### 示例 3：实现缓存策略

```tsx
import { unstable_cache, revalidateTag } from 'next/cache'

// 缓存数据函数
const getProducts = unstable_cache(
  async () => db.product.findMany(),
  ['products'],
  { revalidate: 3600, tags: ['products'] }
)

// 变动时重新验证
export async function createProduct(data: FormData) {
  'use server'
  await db.product.create({ data })
  revalidateTag('products')
}
```

### 示例 4：设置优化字体

```tsx
import { Inter } from 'next/font/google'

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
})

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={inter.variable}>
      <body className={`${inter.className} antialiased`}>
        {children}
      </body>
    </html>
  )
}
```

### 示例 5：实现 Suspense 流式传输

```tsx
import { Suspense } from 'react'

export default function Page() {
  return (
    <>
      <header>静态内容（立即加载）</header>

      <Suspense fallback={<ProductSkeleton />}>
        <ProductList />  {/* 准备好时流式传输 */}
      </Suspense>

      <Suspense fallback={<ReviewsSkeleton />}>
        <Reviews />      {/* 独立流式传输 */}
      </Suspense>
    </>
  )
}
```

## 参考文档

在处理特定领域时加载这些参考：

| 主题 | 参考文件 |
|------|----------|
| 核心网络生命体征 | `references/core-web-vitals.md` |
| 图像优化 | `references/image-optimization.md` |
| 字体优化 | `references/font-optimization.md` |
| 缓存策略 | `references/caching-strategies.md` |
| 服务器组件 | `references/server-components.md` |
| 流式传输/Suspense | `references/streaming-suspense.md` |
| 捆绑包优化 | `references/bundle-optimization.md` |
| 元数据/SEO | `references/metadata-seo.md` |
| API 路由 | `references/api-routes.md` |
| Next.js 16 模式 | `references/nextjs-16-patterns.md` |

## 常见转换

| 从 | 到 | 好处 |
|----|-----|------|
| `useEffect` + fetch | 服务器组件中的直接异步 | -70% JS，更快 TTFB |
| `useState` 用于数据 | 服务器组件直接访问数据库 | 代码更简单，无需重新激活 |
| 客户端端 fetch | `unstable_cache` 或 ISR | 更快的重复加载 |
| `img` 标签 | `next/image` | 优化格式，懒加载 |
| CSS 字体导入 | `next/font` | 零 CLS，自动优化 |
| 重型组件静态导入 | `dynamic()` | 减小初始捆绑包 |

## 最佳实践

### 图像

- 使用 `next/image` 加载所有图像
- 仅 LCP 图像添加 `priority`
- 提供 `width` 和 `height` 或 `fill` 与尺寸
- 使用 `placeholder="blur"` 以提升用户体验
- 在 next.config.js 中配置 remotePatterns

### 字体

- 使用 `next/font` 而不是 CSS 导入
- 指定 `subsets` 以减小大小
- 使用 `display: 'swap'` 以立即渲染文本
- 使用 `variable` 选项创建 CSS 变量
- 配置 Tailwind 使用 CSS 变量

### 缓存

- 使用 `unstable_cache` 缓存昂贵查询
- 使用有意义的缓存标签进行粒度化控制
- 实现按需重新验证以用于动态内容
- 根据数据变更频率设置 TTL
- 使用 revalidatePath 进行路由级失效

### 组件

- 尽可能将客户端组件转换为服务器组件
- 将客户端组件保持在叶节点
- 使用 Suspense 边界进行渐进式加载
- 实现适当的加载状态
- 使用 dynamic() 加载折叠下方的重型组件

### 捆绑包

- 使用 `dynamic()` 懒加载重型组件
- 使用命名导出以实现更好的树摇
- 定期使用 `@`next/bundle-analyzer 分析捆绑包
- 优先使用 ESM 包而不是 CommonJS
- 使用 modularizeImports 处理大型库

## 限制和警告

### 服务器组件限制

- 不能使用浏览器 API（window、localStorage、document）
- 不能使用 React 钩子（useState、useEffect、useContext）
- 不能使用事件处理程序（onClick、onSubmit）
- 不能使用带 ssr: false 的动态导入

### 图像优化限制

- `priority` 仅用于折叠上方图像
- 外部图像需要在 next.config.js 中配置
- 除非使用 `fill`，否则必须提供 `width` 和 `height`
- 默认情况下不优化动画 GIF

### 缓存注意事项

- 缓存标签必须手动失效
- 开发环境中的数据缓存是按请求的
- 边缘运行时具有不同的缓存行为
- 小心缓存用户特定数据

### 捆绑包大小警告

- 动态导入如果包含关键内容可能影响 SEO
- 树摇需要正确的 ES 模块使用
- 某些库无法树摇（避免使用列 barrel 导出）
- 客户端组件增加捆绑包大小 - 谨慎使用

## Next.js 16 + React 19 特定内容

### Async Params

```tsx
// Next.js 15+ params 是 Promise
export default async function Page({
  params,
}: {
  params: Promise<{ slug: string }>
}) {
  const { slug } = await params
  const post = await fetchPost(slug)
  return <article>{post.content}</article>
}
```

### use() 钩子用于 Promise

```tsx
'use client'
import { use, Suspense } from 'react'

function Comments({ promise }: { promise: Promise<Comment[]> }) {
  const comments = use(promise)  // 挂起直到解决
  return <ul>{comments.map(c => <li key={c.id}>{c.text}</li>)}</ul>
}
```

### useOptimistic 用于 UI 更新

```tsx
'use client'
import { useOptimistic } from 'react'

export function TodoList({ todos }: { todos: Todo[] }) {
  const [optimisticTodos, addOptimisticTodo] = useOptimistic(
    todos,
    (state, newTodo: Todo) => [...state, newTodo]
  )

  async function addTodo(formData: FormData) {
    const text = formData.get('text') as string
    addOptimisticTodo({ id: crypto.randomUUID(), text, completed: false })
    await createTodo(text)
  }

  return (
    <form action={addTodo}>
      <input name="text" />
      {optimisticTodos.map(todo => <div key={todo.id}>{todo.text}</div>)}
    </form>
  )
}
```

## 捆绑包分析

```bash
# 安装分析器
npm install --save-dev @next/bundle-analyzer

# 运行分析
ANALYZE=true npm run build
```

```javascript
// next.config.js
const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
})

module.exports = withBundleAnalyzer({
  modularizeImports: {
    'lodash': { transform: 'lodash/{{member}}' },
  },
})
```

## 性能检查清单

- [ ] 所有图像使用 `next/image` 并提供正确尺寸
- [ ] LCP 图像具有 `priority` 属性
- [ ] 字体使用 `next/font` 并包含子集
- [ ] 服务器组件尽可能使用
- [ ] 客户端组件仅位于叶节点
- [ ] 使用 Suspense 边界进行数据获取
- [ ] 配置缓存以优化昂贵操作
- [ ] 分析捆绑包以查找重复项
- [ ] 重型组件懒加载
- [ ] 验证修改前后的 Lighthouse 分数

## 常见错误

```tsx
// ❌ 不要：在 useEffect 中 fetch
'use client'
useEffect(() => { fetch('/api/data').then(...) }, [])

// ✅ 要：服务器组件中直接 fetch
const data = await fetch('/api/data')

// ❌ 不要：忘记图像尺寸
<Image src="/photo.jpg" />

// ✅ 要：始终提供尺寸
<Image src="/photo.jpg" width={800} height={600} />

// ❌ 不要：对所有图像使用 priority
<Image src="/photo1.jpg" priority />
<Image src="/photo2.jpg" priority />

// ✅ 要：仅 LCP 使用 priority
<Image src="/hero.jpg" priority />
<Image src="/photo.jpg" loading="lazy" />

// ❌ 不要：使用相同 TTL 缓存所有内容
{ revalidate: 3600 }

// ✅ 要：匹配 TTL 与数据变更频率
{ revalidate: 86400 } // 分类很少变更
{ revalidate: 60 }     // 评论经常变更
```

## 外部资源

- [Next.js 性能文档](https://nextjs.org/docs/app/building-your-application/optimizing)
- [核心网络生命体征](https://web.dev/vitals/)
- [React 服务器组件](https://react.dev/reference/react/server-components)
