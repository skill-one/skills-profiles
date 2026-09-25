# Next.js 数据获取

## 概述

为 Next.js 应用路由器中的数据获取提供模式：服务器端获取、SWR/React Query 集成、ISR、重新验证、错误边界和加载状态。

## 何时使用

- 在 Next.js 应用路由器中实现数据获取
- 在服务器组件和客户端组件之间进行选择
- 设置客户端缓存以使用 SWR 或 React Query
- 配置 ISR、基于时间的或按需重新验证
- 处理加载和错误状态
- 使用服务器动作构建表单

## 说明

### 服务器组件获取

在异步服务器组件中直接获取：

```tsx
async function getPosts() {
  const res = await fetch('https://api.example.com/posts');
  if (!res.ok) throw new Error('获取帖子失败');
  return res.json();
}

export default async function PostsPage() {
  const posts = await getPosts();
  return (
    <ul>
      {posts.map((post) => (
        <li key={post.id}>{post.title}</li>
      ))}
    </ul>
  );
}
```

### 并行数据获取

使用 `Promise.all()` 进行独立请求：

```tsx
async function getDashboardData() {
  const [user, posts, analytics] = await Promise.all([
    fetch('/api/user').then(r => r.json()),
    fetch('/api/posts').then(r => r.json()),
    fetch('/api/analytics').then(r => r.json()),
  ]);
  return { user, posts, analytics };
}

export default async function DashboardPage() {
  const { user, posts, analytics } = await getDashboardData();
  // 渲染仪表盘
}
```

### 顺序数据获取（当存在依赖关系时）

```tsx
async function getUserPosts(userId: string) {
  const user = await fetch(`/api/users/${userId}`).then(r => r.json());
  const posts = await fetch(`/api/users/${userId}/posts`).then(r => r.json());
  return { user, posts };
}
```

### 基于时间的重新验证（ISR）

```tsx
async function getPosts() {
  const res = await fetch('https://api.example.com/posts', {
    next: { revalidate: 60 } // 每60秒重新验证一次
  });
  return res.json();
}
```

### 按需重新验证

```tsx
// app/api/revalidate/route.ts
import { revalidateTag } from 'next/cache';
import { NextRequest } from 'next/server';

export async function POST(request: NextRequest) {
  const tag = request.nextUrl.searchParams.get('tag');
  if (tag) {
    revalidateTag(tag);
    return Response.json({ revalidated: true });
  }
  return Response.json({ revalidated: false }, { status: 400 });
}
```

为选择性重新验证标记数据：

```tsx
async function getPosts() {
  const res = await fetch('https://api.example.com/posts', {
    next: { tags: ['posts'], revalidate: 3600 }
  });
  return res.json();
}
```

### 跳过缓存

```tsx
async function getRealTimeData() {
  const res = await fetch('https://api.example.com/data', {
    cache: 'no-store'
  });
  return res.json();
}

// 或者：
export const dynamic = 'force-dynamic';
```

## 客户端数据获取

### SWR 集成

安装：`npm install swr`

```tsx
'use client';

import useSWR from 'swr';

const fetcher = (url: string) => fetch(url).then(r => r.json());

export function Posts() {
  const { data, error, isLoading } = useSWR('/api/posts', fetcher, {
    refreshInterval: 5000,
    revalidateOnFocus: true,
  });

  if (isLoading) return <div>加载中...</div>;
  if (error) return <div>加载帖子失败</div>;

  return (
    <ul>
      {data.map((post: any) => (
        <li key={post.id}>{post.title}</li>
      ))}
    </ul>
  );
}
```

### React Query 集成

安装：`npm install @tanstack/react-query`

```tsx
// app/providers.tsx
'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState } from 'react';

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 60 * 1000,
        refetchOnWindowFocus: false,
      },
    },
  }));

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
}
```

有关突变、乐观更新、无限查询和高级模式的更多信息，请参阅 [react-query.md](references/react-query.md)。

## 错误边界

将客户端数据获取包装在错误边界中，以便优雅地处理失败：

有关完整的 `ErrorBoundary` 实现示例（基本、带重置回调）和与数据获取的错误处理示例，请参阅 [error-boundaries.md](references/error-boundaries.md)。

## 服务器动作

使用服务器动作进行带缓存重新验证的突变：

有关包括使用 `useActionState` 进行表单验证、错误处理和缓存失效的完整示例，请参阅 [server-actions.md](references/server-actions.md)。

## 加载状态

### loading.tsx 模式

```tsx
// app/posts/loading.tsx
export default function PostsLoading() {
  return (
    <div className="space-y-4">
      {[...Array(5)].map((_, i) => (
        <div key={i} className="h-16 bg-gray-200 animate-pulse rounded" />
      ))}
    </div>
  );
}
```

### Suspense 边界

```tsx
// app/posts/page.tsx
import { Suspense } from 'react';
import { PostsList } from './PostsList';
import { PostsSkeleton } from './PostsSkeleton';

export default function PostsPage() {
  return (
    <div>
      <h1>帖子</h1>
      <Suspense fallback={<PostsSkeleton />}>
        <PostsList />
      </Suspense>
    </div>
  );
}
```

## 最佳实践

1. **默认使用服务器组件** — 在服务器组件中获取以提高性能
2. **使用并行获取** — `Promise.all()` 用于独立请求以减少延迟
3. **选择适当的缓存**：
   - 静态数据：较长的重新验证间隔
   - 动态数据：较短的重新验证或 `cache: 'no-store'`
   - 用户特定数据：使用动态渲染
4. **优雅地处理错误** — 将客户端数据获取包装在错误边界中
5. **实现加载状态** — 使用 `loading.tsx` 或 Suspense 边界
6. **优先使用 SWR/React Query**：用于实时数据、用户交互、后台更新
7. **使用服务器动作**：用于表单提交、需要缓存重新验证的突变

## 限制和警告

### 关键限制

- 服务器组件不能使用钩子（`useState`、`useEffect`）或客户端数据获取库
- 客户端组件必须包含 `'use client'` 指令
- Next.js 中的 `fetch` API 扩展了标准 Web fetch，增加了 Next.js 特定的缓存选项
- 服务器动作需要 `'use server'`，并且只能从客户端组件或表单动作调用

### 常见陷阱

1. **在循环中获取** — 避免在服务器组件中顺序获取；使用并行获取
2. **缓存中毒** — 不要使用 `force-cache` 用于用户特定或个性化数据
3. **内存泄漏** — 在客户端组件中使用实时数据时清理订阅
4. **水合不匹配** — 确保服务器和客户端以相同的初始状态渲染，使用 React Query 水合

## 示例

### 示例 1：带 ISR 的博客

**输入**：创建一个获取帖子并每小时更新的博客页面。

```tsx
// app/blog/page.tsx
async function getPosts() {
  const res = await fetch('https://api.example.com/posts', {
    next: { revalidate: 3600 }
  });
  return res.json();
}

export default async function BlogPage() {
  const posts = await getPosts();
  return (
    <main>
      <h1>博客帖子</h1>
      {posts.map(post => (
        <article key={post.id}>
          <h2>{post.title}</h2>
          <p>{post.excerpt}</p>
        </article>
      ))}
    </main>
  );
}
```

**输出**：页面在构建时静态生成，每小时重新验证一次。

### 示例 2：带并行获取的仪表盘

**输入**：构建一个并行显示用户资料、统计数据和最近活动的仪表盘。

```tsx
// app/dashboard/page.tsx
async function getDashboardData() {
  const [user, stats, activity] = await Promise.all([
    fetch('/api/user').then(r => r.json()),
    fetch('/api/stats').then(r => r.json()),
    fetch('/api/activity').then(r => r.json()),
  ]);
  return { user, stats, activity };
}

export default async function DashboardPage() {
  const { user, stats, activity } = await getDashboardData();
  return (
    <div className="dashboard">
      <UserProfile user={user} />
      <StatsCards stats={stats} />
      <ActivityFeed activity={activity} />
    </div>
  );
}
```

**输出**：所有三个请求同时执行，最小化总加载时间。
