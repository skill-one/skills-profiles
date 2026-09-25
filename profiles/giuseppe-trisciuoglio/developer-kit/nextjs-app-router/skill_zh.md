# Next.js 应用路由器（Next.js 16+）

使用 Next.js 16+ 的应用路由器架构构建现代 React 应用。

## 概述

此技能提供以下模式的指导：
- 服务器组件（默认）和客户端组件（"use client"）
- 服务器操作用于突变和表单处理
- 路由处理器用于 API 端点
- 使用 "use cache" 指令的显式缓存
- 并行和拦截路由
- Next.js 16 异步 API 和 proxy.ts

## 何时使用

当用户请求涉及以下内容时激活：
- "创建 Next.js 16 项目"、"设置应用路由器"
- "服务器组件"、"客户端组件"、"use client"
- "服务器操作"、"表单提交"、"突变"
- "路由处理器"、"API 端点"、"route.ts"
- "use cache"、"cacheLife"、"cacheTag"、"revalidation"
- "并行路由"、"@slot"、"拦截路由"
- "proxy.ts"、"从 middleware.ts 迁移"
- "layout.tsx"、"page.tsx"、"loading.tsx"、"error.tsx"、"not-found.tsx"
- "generateMetadata"、"next/image"、"next/font"

## 快速参考

| 文件 | 目的 | 指令 | 目的 |
|------|---------|-----------|---------|
| `page.tsx` | 路由页面 | `"use server"` | 服务器操作函数 |
| `layout.tsx` | 共享布局 | `"use client"` | 客户端组件边界 |
| `loading.tsx` | Suspense 加载 | `"use cache"` | 显式缓存（Next.js 16） |
| `error.tsx` | 错误边界 | | |
| `not-found.tsx` | 404 页面 | | |
| `route.ts` | API 路由处理器 | | |
| `proxy.ts` | 路由边界 | | |

## 说明

### 创建新项目

```bash
npx create-next-app@latest my-app --typescript --tailwind --app --turbopack
```

### 服务器组件

服务器组件是应用路由器的默认选项。它们在服务器上运行，并可以使用 async/await。

```tsx
// app/users/page.tsx
async function getUsers() {
  const apiUrl = process.env.API_URL;
  const res = await fetch(`${apiUrl}/users`);
  return res.json();
}

export default async function UsersPage() {
  const users = await getUsers();
  return <main>{users.map(user => <UserCard key={user.id} user={user} />)}</main>;
}
```

### 客户端组件

在使用钩子、浏览器 API 或事件处理器时添加 `"use client"`。

```tsx
"use client";

import { useState } from "react";

export default function Counter() {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount(c => c + 1)}>Count: {count}</button>;
}
```

### 服务器操作

在单独的文件中定义操作，并使用 `"use server"` 指令。

```tsx
// app/actions.ts
"use server";

import { revalidatePath } from "next/cache";

export async function createUser(formData: FormData) {
  const name = formData.get("name") as string;
  const email = formData.get("email") as string;
  await db.user.create({ data: { name, email } });
  revalidatePath("/users");
}
```

在客户端组件中的表单中使用：

```tsx
"use client";

import { useActionState } from "react";
import { createUser } from "./actions";

export default function UserForm() {
  const [state, formAction, pending] = useActionState(createUser, {});
  return (
    <form action={formAction}>
      <input name="name" />
      <input name="email" type="email" />
      <button type="submit" disabled={pending}>{pending ? "Creating..." : "Create"}</button>
    </form>
  );
}
```

有关 Zod 验证、乐观更新和高级模式的更多信息，请参阅 [references/server-actions.md](references/server-actions.md)。

### 配置缓存

使用 `"use cache"` 指令进行显式缓存（Next.js 16+）。

```tsx
"use cache";

import { cacheLife, cacheTag } from "next/cache";

export default async function ProductPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  cacheTag(`product-${id}`);
  cacheLife("hours");
  const product = await fetchProduct(id);
  return <ProductDetail product={product} />;
}
```

有关缓存配置文件、按需重新验证和高级模式的更多信息，请参阅 [references/caching-strategies.md](references/caching-strategies.md)。

### 路由处理器

```ts
// app/api/users/route.ts
import { NextRequest, NextResponse } from "next/server";

export async function GET(request: NextRequest) {
  return NextResponse.json(await db.user.findMany());
}

export async function POST(request: NextRequest) {
  const body = await request.json();
  return NextResponse.json(await db.user.create({ data: body }), { status: 201 });
}
```

动态段使用 `[param]`：

```ts
// app/api/users/[id]/route.ts
export async function GET(request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const user = await db.user.findUnique({ where: { id } });
  if (!user) return NextResponse.json({ error: "Not found" }, { status: 404 });
  return NextResponse.json(user);
}
```

### Next.js 16 异步 API

在版本 16 中，所有 Next.js API 都是异步的。

```tsx
import { cookies, headers } from "next/headers";

export default async function Page() {
  const cookieStore = await cookies();
  const headersList = await headers();
  const session = cookieStore.get("session")?.value;
  const userAgent = headersList.get("user-agent");
  return <div>...</div>;
}
```

Params 和 searchParams 也是基于 Promise 的：

```tsx
export default async function Page({
  params,
  searchParams,
}: {
  params: Promise<{ slug: string }>;
  searchParams: Promise<{ sort?: string }>;
}) {
  const { slug } = await params;
  const { sort } = await searchParams;
  // ...
}
```

有关迁移指南和 proxy.ts 配置的更多信息，请参阅 [references/nextjs16-migration.md](references/nextjs16-migration.md)。

### 并行路由

使用 `@folder` 约定为并行路由插槽。

```tsx
// app/dashboard/layout.tsx
export default function DashboardLayout({ children, team, analytics }: Record<string, React.ReactNode>) {
  return (
    <div>
      {children}
      <div className="grid grid-cols-2">{team}{analytics}</div>
    </div>
  );
}
```

```tsx
// app/dashboard/@team/page.tsx
export default function TeamPage() { return <div>Team Section</div>; }

// app/dashboard/@analytics/page.tsx
export default function AnalyticsPage() { return <div>Analytics Section</div>; }
```

有关拦截路由、路由组和动态路由的更多信息，请参阅 [references/routing-patterns.md](references/routing-patterns.md)。

## 最佳实践

**服务器与客户端决策：**
- 从服务器组件（默认）开始
- 仅在以下情况下使用客户端组件：React 钩子（useState、useEffect）、浏览器 API（window、document）、事件处理器（onClick、onSubmit）或客户端库

**数据获取：**
- 尽可能地在服务器组件中获取数据
- 使用 React 的 `cache()` 进行去重
- 并行化独立的获取操作
- 使用 `loading.tsx` 添加 Suspense 边界

**性能检查清单：**
- 使用 `loading.tsx` for Suspense 边界
- 使用 `next/image` for 优化图像
- 使用 `next/font` for 字体优化
- 添加 `error.tsx` 和 `not-found.tsx` for 错误处理

## 示例

### 示例 1：带服务器操作的博客文章表单

**输入：** 创建一个带有 Zod 验证的博客文章提交表单

**输出：**
```tsx
// app/blog/actions.ts
"use server";

import { z } from "zod";
import { revalidatePath } from "next/cache";

const schema = z.object({ title: z.string().min(5), content: z.string().min(10) });

export async function createPost(formData: FormData) {
  const parsed = schema.safeParse({ title: formData.get("title"), content: formData.get("content") });
  if (!parsed.success) return { errors: parsed.error.flatten().fieldErrors };
  await db.post.create({ data: parsed.data });
  revalidatePath("/blog");
  return { success: true };
}
```

```tsx
// app/blog/new/page.tsx
"use client";

import { useActionState } from "react";
import { createPost } from "../actions";

export default function NewPostPage() {
  const [state, formAction, pending] = useActionState(createPost, {});
  return (
    <form action={formAction}>
      <input name="title" placeholder="Title" />
      {state.errors?.title && <span>{state.errors.title[0]}</span>}
      <textarea name="content" placeholder="Content" />
      {state.errors?.content && <span>{state.errors.content[0]}</span>}
      <button type="submit" disabled={pending}>{pending ? "Publishing..." : "Publish"}</button>
    </form>
  );
}
```

### 示例 2：缓存产品页面

**输入：** 创建一个带按需重新验证的缓存产品页面

**输出：**
```tsx
// app/products/[id]/page.tsx
"use cache";

import { cacheLife, cacheTag } from "next/cache";

export default async function ProductPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  cacheTag(`product-${id}`, "products");
  cacheLife("hours");
  const product = await db.product.findUnique({ where: { id } });
  if (!product) notFound();
  return <article><h1>{product.name}</h1><p>{product.description}</p></article>;
}
```

```ts
// app/api/revalidate/route.ts
import { revalidateTag } from "next/cache";
import { NextResponse } from "next/server";

export async function POST(request: Request) {
  const { tag } = await request.json();
  revalidateTag(tag);
  return NextResponse.json({ revalidated: true });
}
```

### 示例 3：带并行路由的仪表板

**输入：** 创建一个带有侧边栏和统计区域的仪表板

**输出：**
```tsx
// app/dashboard/layout.tsx
export default function DashboardLayout({ children, sidebar, stats }: Record<string, React.ReactNode>) {
  return (
    <div className="flex">
      <aside className="w-64">{sidebar}</aside>
      <main className="flex-1"><div className="grid grid-cols-3">{stats}</div>{children}</main>
    </div>
  );
}
```

```tsx
// app/dashboard/@sidebar/page.tsx
export default function Sidebar() { return <nav>{/* 导航链接 */}</nav>; }

// app/dashboard/@stats/page.tsx
export default async function Stats() {
  const stats = await fetchStats();
  return <><div>Users: {stats.users}</div><div>Orders: {stats.orders}</div></>;
}
```

## 限制和警告

**限制：**
- 服务器组件不能使用浏览器 API 或 React 钩子
- 客户端组件不能是异步的（不能直接获取数据）
- `cookies()`、`headers()`、`draftMode()` 在 Next.js 16 中是异步的
- `params` 和 `searchParams` 在 Next.js 16 中是基于 Promise 的
- 服务器操作必须使用 `"use server"` 指令定义

**警告：**
- 在客户端组件中使用 `await` 会导致构建错误
- 在服务器组件中访问 `window` 或 `document` 会引发错误
- 在 Next.js 16 中忘记 `await` cookies() 或 headers() 会返回 Promise 而不是值
- 没有适当验证的服务器操作可能会使数据库暴露于未经授权的访问
- **外部数据获取**：在服务器组件中 `fetch()` 第三方 URL 会处理不受信任的内容——始终验证、清理和类型检查响应；使用环境变量而不是硬编码 API URL
