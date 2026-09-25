# Next.js 代码审查

## 概述

评估 Next.js 应用程序路由器代码是否符合服务器组件、客户端组件、服务器操作、缓存策略和生产就绪标准等最佳实践。生成按严重程度分类的可操作发现结果，并附带具体的代码示例。将架构分析委托给 `typescript-software-architect-review` 代理。

## 使用场景

- 合并前审查 Next.js 页面、布局和路由段
- 验证服务器组件与客户端组件的边界
- 检查服务器操作的安全性和正确性
- 审查数据获取模式（fetch、缓存、重新验证）
- 评估缓存策略（静态生成、ISR、动态渲染）
- 评估中间件实现（身份验证、重定向、重写）
- 审查 API 路由处理程序的正确请求/响应处理
- 验证 SEO 元数据配置
- 检查加载、错误和未找到页面的实现
- 实施新的 Next.js 功能或从 Pages 路由器迁移后

## 说明

1. **确定范围**：确定正在审查的 Next.js 路由段和组件。使用 `glob` 发现 `page.tsx`、`layout.tsx`、`loading.tsx`、`error.tsx`、`route.ts` 和 `middleware.ts` 文件。

2. **分析组件边界**：验证服务器组件/客户端组件分离是否正确。检查 `'use client'` 是否仅放置在必要的地方，并且尽可能深地放置在组件树中。确保服务器组件不导入仅客户端模块。

3. **审查数据获取**：验证获取模式——检查 `cache` 和 `revalidate` 选项是否正确，使用 `Promise.all` 进行并行数据获取，并避免请求瀑布。验证服务器端数据获取是否不会将敏感数据暴露给客户端。

4. **评估缓存策略**：审查静态与动态渲染决策。检查 `generateStaticParams` 的使用情况以进行静态生成，`revalidatePath`/`revalidateTag` 的使用情况以进行按需重新验证，以及 API 路由的正确缓存头。

5. **评估服务器操作**：审查表单操作的正确验证（客户端和服务器端）、错误处理、使用 `useOptimistic` 的乐观更新，以及安全性（确保操作在未经授权的情况下不会暴露敏感操作）。

6. **检查中间件**：审查中间件是否正确匹配请求、身份验证/授权逻辑、响应修改和性能影响。验证它是否仅在必要的路由上运行。

7. **审查元数据和 SEO**：检查 `generateMetadata` 函数、Open Graph 标签、结构化数据、`robots.txt` 和 `sitemap.xml` 配置。验证动态元数据是否正确地为具有可变内容的页面实现。

8. **验证发现结果**：在最终确定之前，通过检查实际代码上下文来验证每个问题。确认模式违规存在，确保建议的修复适用于代码库，并删除任何误报。

9. **生成审查报告**：生成一个结构化报告，包含按严重程度分类的发现结果（关键、警告、建议）、积极观察结果和带有代码示例的优先级建议。

## 示例

### 示例 1：服务器/客户端组件边界

```tsx
// ❌ 不良：整个页面标记为客户端，而仅按钮需要交互
'use client';

export default async function ProductPage({ params }: { params: { id: string } }) {
  const product = await fetch(`/api/products/${params.id}`);
  return (
    <div>
      <h1>{product.name}</h1>
      <p>{product.description}</p>
      <button onClick={() => addToCart(product.id)}>添加到购物车</button>
    </div>
  );
}

// ✅ 良好：服务器组件与隔离的客户端组件
// app/products/[id]/page.tsx（服务器组件）
import { AddToCartButton } from './add-to-cart-button';

export default async function ProductPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const product = await getProduct(id);

  return (
    <div>
      <h1>{product.name}</h1>
      <p>{product.description}</p>
      <AddToCartButton productId={product.id} />
    </div>
  );
}

// app/products/[id]/add-to-cart-button.tsx（客户端组件）
'use client';

export function AddToCartButton({ productId }: { productId: string }) {
  return <button onClick={() => addToCart(productId)}>添加到购物车</button>;
}
```

### 示例 2：数据获取模式

```tsx
// ❌ 不良：顺序数据获取创建瀑布
export default async function DashboardPage() {
  const user = await getUser();
  const orders = await getOrders(user.id);
  const analytics = await getAnalytics(user.id);
  return <Dashboard user={user} orders={orders} analytics={analytics} />;
}

// ✅ 良好：使用适当的 Suspense 边界进行并行数据获取
export default async function DashboardPage() {
  const user = await getUser();
  const [orders, analytics] = await Promise.all([
    getOrders(user.id),
    getAnalytics(user.id),
  ]);
  return <Dashboard user={user} orders={orders} analytics={analytics} />;
}

// ✅ 甚至更好：使用 Suspense 进行流式传输以实现独立的区域
export default async function DashboardPage() {
  const user = await getUser();
  return (
    <div>
      <UserHeader user={user} />
      <Suspense fallback={<OrdersSkeleton />}>
        <OrdersSection userId={user.id} />
      </Suspense>
      <Suspense fallback={<AnalyticsSkeleton />}>
        <AnalyticsSection userId={user.id} />
      </Suspense>
    </div>
  );
}
```

### 示例 3：服务器操作安全性

```tsx
// ❌ 不良：没有验证或授权的服务器操作
'use server';

export async function deleteUser(id: string) {
  await db.user.delete({ where: { id } });
}

// ✅ 良好：带有验证、授权和错误处理的服务器操作
'use server';

import { z } from 'zod';
import { auth } from '@/lib/auth';
import { revalidatePath } from 'next/cache';

const deleteUserSchema = z.object({ id: z.string().uuid() });

export async function deleteUser(rawData: { id: string }) {
  const session = await auth();
  if (!session || session.user.role !== 'admin') {
    throw new Error('未授权');
  }

  const { id } = deleteUserSchema.parse(rawData);
  await db.user.delete({ where: { id } });
  revalidatePath('/admin/users');
}
```

### 示例 4：缓存和重新验证

```tsx
// ❌ 不良：没有缓存控制，每次请求都获取
export default async function BlogPage() {
  const posts = await fetch('https://api.example.com/posts').then(r => r.json());
  return <PostList posts={posts} />;
}

// ✅ 良好：使用基于时间的重新验证的显式缓存
export default async function BlogPage() {
  const posts = await fetch('https://api.example.com/posts', {
    next: { revalidate: 3600, tags: ['blog-posts'] },
  }).then(r => r.json());
  return <PostList posts={posts} />;
}

// 服务器操作中的重新验证
'use server';
export async function publishPost(data: FormData) {
  await db.post.create({ data: parseFormData(data) });
  revalidateTag('blog-posts');
}
```

### 示例 5：中间件审查

```typescript
// ❌ 不良：中间件在包括静态资源在内的所有路由上运行
import { NextResponse } from 'next/server';

export function middleware(request: NextRequest) {
  const session = request.cookies.get('session');
  if (!session) {
    return NextResponse.redirect(new URL('/login', request.url));
  }
}
// 缺少 config.matcher

// ✅ 良好：具有正确匹配器的范围中间件
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const session = request.cookies.get('session');
  if (!session) {
    return NextResponse.redirect(new URL('/login', request.url));
  }
  return NextResponse.next();
}

export const config = {
  matcher: ['/dashboard/:path*', '/api/protected/:path*'],
};
```

## 审查输出格式

按照以下结构组织所有代码审查发现结果：

### 1. 摘要
简要概述，包括整体质量评分（1-10）和关键观察结果。

### 2. 关键问题（必须修复）
导致安全漏洞、数据暴露或功能损坏的问题。

### 3. 警告（应修复）
违反最佳实践、导致性能问题或降低可维护性的问题。

### 4. 建议（考虑改进）
代码组织、性能或开发者体验的改进建议。

### 5. 积极观察结果
良好实现的模式和良好实践，值得认可。

### 6. 建议
按优先级排列的下一步操作，附带代码示例，以实现最有影响力的改进。

## 最佳实践

- 将 `'use client'` 边界尽可能深地放置在树中
- 在服务器组件中获取数据——避免在客户端获取初始数据
- 使用并行数据获取（`Promise.all`）以避免请求瀑布
- 为每个路由段实现适当的加载、错误和未找到状态
- 使用 Zod 或类似库验证所有服务器操作输入
- 在可能的情况下使用 `revalidatePath`/`revalidateTag` 而不是基于时间的重新验证
- 使用 `config.matcher` 将中间件限制为特定路由
- 为具有可变内容的动态页面实现 `generateMetadata`
- 使用 `generateStaticParams` 为具有已知参数的静态页面
- 避免在客户端组件中导入服务器端代码——使用 `server-only` 包

## 限制和警告

- 此技能针对 Next.js 应用程序路由器——Pages 路由器模式可能差异很大
- 尊重项目的 Next.js 版本——某些功能是版本特定的
- 除非明确要求，否则不要建议从 Pages 路由器迁移到应用程序路由器
- 开发和生产环境中的缓存行为不同——在生产构建中验证
- 服务器操作必须始终在未经适当身份验证检查的情况下不暴露敏感操作
- 专注于高置信度问题——避免对样式偏好产生误报

## 参考

有关详细的审查清单和模式文档，请参阅 `references/` 目录：
- `references/app-router-patterns.md` — 应用程序路由器最佳实践和模式
- `references/server-components.md` — 服务器组件和客户端组件边界指南
- `references/performance.md` — Next.js 性能优化清单
