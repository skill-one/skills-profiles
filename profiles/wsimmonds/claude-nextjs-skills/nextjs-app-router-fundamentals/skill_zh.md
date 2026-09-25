# Next.js 应用路由基础

## 概述

为 Next.js 应用路由（Next.js 13+）提供全面指导，涵盖从页面路由迁移、基于文件的路线约定、布局、元数据处理以及现代 Next.js 模式。

## TypeScript：永远不要使用 `any` 类型

**关键规则**：此代码库启用了 `@typescript-eslint/no-explicit-any`。使用 `any` 将导致构建失败。

**❌ 错误：**
```typescript
function handleSubmit(e: any) { ... }
const data: any[] = [];
```

**✅ 正确：**
```typescript
function handleSubmit(e: React.FormEvent<HTMLFormElement>) { ... }
const data: string[] = [];
```

### 常见的 Next.js 类型模式

```typescript
// 页面属性
function Page({ params }: { params: { slug: string } }) { ... }
function Page({ searchParams }: { searchParams: { [key: string]: string | string[] | undefined } }) { ... }

// 表单事件
const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => { ... }
const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => { ... }

// 服务器操作
async function myAction(formData: FormData) { ... }
```

## 何时使用此技能

使用此技能时：
- 从页面路由（`pages/` 目录）迁移到应用路由（`app/` 目录）
- 从头开始创建 Next.js 13+ 应用
- 使用布局、模板和嵌套路由
- 实现元数据和 SEO 优化
- 使用应用路由路线约定构建
- 处理路线组、并行路由或拦截路由基础

## 核心概念

### 应用路由与页面路由

**页面路由（遗留 - Next.js 12 及更早版本）：**
```
pages/
├── index.tsx              # 路径：/
├── about.tsx              # 路径：/about
├── _app.tsx               # 自定义 App 组件
├── _document.tsx          # 自定义 Document 组件
└── api/                   # API 路由
    └── hello.ts           # API 端点：/api/hello
```

**应用路由（现代 - Next.js 13+）：**
```
app/
├── layout.tsx             # 根布局（必需）
├── page.tsx               # 路径：/
├── about/                 # 路径：/about
│   └── page.tsx
├── blog/
│   ├── layout.tsx         # 嵌套布局
│   └── [slug]/
│       └── page.tsx       # 动态路由：/blog/:slug
└── api/                   # 路由处理程序
    └── hello/
        └── route.ts       # API 端点：/api/hello
```

### 文件约定

**应用路由中的特殊文件：**
- `layout.tsx` - 分段及其子组件的共享 UI（保留状态，不会重新渲染）
- `page.tsx` - 路径的唯一 UI，使路径公开访问
- `loading.tsx` - 使用 React Suspense 的加载 UI
- `error.tsx` - 使用错误边界（Error Boundaries）的错误 UI
- `not-found.tsx` - 404 UI
- `template.tsx` - 类似于布局，但在导航时重新渲染
- `route.ts` - API 端点（路由处理程序）

**文件共置：**
- 组件、测试和其他文件可以共置在 `app/`
- 只有 `page.tsx` 和 `route.ts` 文件创建公共路径
- 其他文件（组件、工具、测试）不可路由

## 从页面路由迁移到应用路由的指南

### 第 1 步：理解当前结构

检查现有的页面路由设置：
- 阅读 `pages/` 目录结构
- 确定 `_app.tsx` - 处理全局状态、布局、提供程序
- 确定 `_document.tsx` - 自定义 HTML 结构
- 注意元数据处理（`next/head`，`<Head>` 组件）
- 列出所有路径和动态段

### 第 2 步：创建根布局

创建 `app/layout.tsx` - 所有应用路由应用程序**必需**：

```typescript
// app/layout.tsx
export const metadata = {
  title: '我的应用',
  description: '应用描述',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
```

**迁移说明：**
- 将 `_document.tsx` 的 HTML 结构移动到 `layout.tsx`
- 将 `_app.tsx` 的全局提供程序/包装器移动到 `layout.tsx`
- 将 `<Head>` 元数据转换为 `metadata` 导出
- 根布局**必须**包含 `<html>` 和 `<body>` 标签

### 第 3 步：将页面迁移为路径

**简单页面迁移：**
```typescript
// 之前：pages/index.tsx
import Head from 'next/head';

export default function Home() {
  return (
    <>
      <Head>
        <title>主页</title>
      </Head>
      <main>
        <h1>欢迎</h1>
      </main>
    </>
  );
}
```

```typescript
// 之后：app/page.tsx
export default function Home() {
  return (
    <main>
      <h1>欢迎</h1>
    </main>
  );
}

// 元数据移动到 layout.tsx 或在此处导出
export const metadata = {
  title: '主页',
};
```

**嵌套路径迁移：**
```typescript
// 之前：pages/blog/[slug].tsx
export default function BlogPost() { ... }
```

```typescript
// 之后：app/blog/[slug]/page.tsx
export default function BlogPost() { ... }
```

### 第 4 步：更新导航

用 Next.js Link 替换锚标签：

```typescript
// 之前（在应用路由中不正确）
<a href="/about">关于</a>

// 之后（正确）
import Link from 'next/link';
<Link href="/about">关于</Link>
```

### 第 5 步：清理页面目录

迁移后：
- 从 `pages/` 目录中删除所有页面文件
- 如果你还没有迁移 API 路由，请保留 `pages/api/`
- 删除 `_app.tsx` 和 `_document.tsx`（功能已移动到布局）
- 可选：删除空的 `pages/` 目录

## 元数据处理

### 静态元数据

```typescript
// app/page.tsx 或 app/layout.tsx
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: '我的页面',
  description: '页面描述',
  keywords: ['nextjs', 'react'],
  openGraph: {
    title: '我的页面',
    description: '页面描述',
    images: ['/og-image.jpg'],
  },
};
```

### 动态元数据

```typescript
// app/blog/[slug]/page.tsx
export async function generateMetadata({
  params
}: {
  params: { slug: string }
}): Promise<Metadata> {
  const post = await getPost(params.slug);

  return {
    title: post.title,
    description: post.excerpt,
  };
}
```

## 布局和嵌套

### 创建嵌套布局

```typescript
// app/layout.tsx - 根布局
export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        <Header />
        {children}
        <Footer />
      </body>
    </html>
  );
}

// app/blog/layout.tsx - 博客布局
export default function BlogLayout({ children }) {
  return (
    <div>
      <BlogSidebar />
      <main>{children}</main>
    </div>
  );
}
```

**布局行为：**
- 布局在导航时保留状态
- 布局在路径更改时不会重新渲染
- 父布局包装子布局
- 根布局是必需的，并包装整个应用

## 路由模式

### 动态路由

```typescript
// app/blog/[slug]/page.tsx
export default function BlogPost({
  params
}: {
  params: { slug: string }
}) {
  return <article>文章：{params.slug}</article>;
}
```

### 捕获所有路由

```typescript
// app/shop/[...slug]/page.tsx - 匹配 /shop/a、/shop/a/b 等
export default function Shop({
  params
}: {
  params: { slug: string[] }
}) {
  return <div>路径：{params.slug.join('/')}</div>;
}
```

### 可选捕获所有

```typescript
// app/shop/[[...slug]]/page.tsx - 匹配 /shop 和 /shop/a、/shop/a/b
```

### 路径组

在不影响 URL 的情况下分组路径：

```
app/
├── (marketing)/
│   ├── about/
│   │   └── page.tsx      # /about
│   └── contact/
│       └── page.tsx      # /contact
└── (shop)/
    └── products/
        └── page.tsx      # /products
```

## 常见迁移陷阱

### 陷阱 1：忘记根布局 HTML 标签

**错误：**
```typescript
export default function RootLayout({ children }) {
  return <div>{children}</div>; // 缺少 <html> 和 <body>
}
```

**正确：**
```typescript
export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
```

### 陷阱 2：在应用路由中使用 `next/head`

**错误：**
```typescript
import Head from 'next/head';

export default function Page() {
  return (
    <>
      <Head><title>标题</title></Head>
      <main>内容</main>
    </>
  );
}
```

**正确：**
```typescript
export const metadata = { title: '标题' };

export default function Page() {
  return <main>内容</main>;
}
```

### 陷阱 3：未删除页面目录

迁移路径后，删除旧的 `pages/` 目录文件以避免混淆。如果存在冲突路径，构建将失败。

### 陷阱 4：缺少 `page.tsx` 文件

没有 `page.tsx` 文件，路径将无法访问。仅布局不会创建路径。

```
app/
├── blog/
│   ├── layout.tsx   # 不是路径
│   └── page.tsx     # 这使 /blog 可访问
```

### 陷阱 5：链接使用不正确

**错误：**
```typescript
<a href="/about">关于</a>  // 可以工作，但会导致整个页面重新加载
```

**正确：**
```typescript
import Link from 'next/link';
<Link href="/about">关于</Link>  // 客户端导航
```

## 服务器组件与客户端组件

### 默认：服务器组件

`app/` 中的所有组件默认都是服务器组件：

```typescript
// app/page.tsx - 服务器组件（默认）
export default async function Page() {
  const data = await fetch('https://api.example.com/data');
  const json = await data.json();

  return <div>{json.title}</div>;
}
```

**优点：**
- 可以直接使用 async/await
- 可以直接访问数据库/API
- 零客户端 JavaScript
- 自动代码拆分

### 客户端组件

当您需要时使用 `'use client'` 指令：
- 交互式元素（onClick、onChange 等）
- React 钩子（useState、useEffect、useContext 等）
- 浏览器 API（window、localStorage 等）
- 事件监听器

```typescript
// app/components/Counter.tsx
'use client';

import { useState } from 'react';

export default function Counter() {
  const [count, setCount] = useState(0);

  return (
    <button onClick={() => setCount(count + 1)}>
      计数：{count}
    </button>
  );
}
```

## 数据获取模式

### 服务器组件数据获取

```typescript
// app/posts/page.tsx
async function getPosts() {
  const res = await fetch('https://api.example.com/posts', {
    next: { revalidate: 3600 } // 每小时重新验证
  });
  return res.json();
}

export default async function PostsPage() {
  const posts = await getPosts();

  return (
    <ul>
      {posts.map(post => (
        <li key={post.id}>{post.title}</li>
      ))}
    </ul>
  );
}
```

### 并行数据获取

```typescript
export default async function Page() {
  // 并行获取
  const [posts, users] = await Promise.all([
    fetch('https://api.example.com/posts').then(r => r.json()),
    fetch('https://api.example.com/users').then(r => r.json()),
  ]);

  return (/* 渲染 */);
}
```

## 使用 generateStaticParams 进行静态站点生成

### 概述

`generateStaticParams` 是应用路由中 `getStaticPaths`（页面路由）的等效功能。它生成静态页面以在构建时为动态路由生成。

### 基本用法

```typescript
// app/blog/[id]/page.tsx
export async function generateStaticParams() {
  // 返回要预渲染的参数数组
  return [
    { id: '1' },
    { id: '2' },
    { id: '3' },
  ];
}

export default function BlogPost({
  params
}: {
  params: { id: string }
}) {
  return <article>博客文章 {params.id}</article>;
}
```

**关键点：**
- 返回一个包含路由参数键的对象数组
- 每个对象代表一个要在构建时预渲染的页面
- 函数必须导出并命名为 `generateStaticParams`
- 仅在服务器组件中工作（没有 `'use client'` 指令）
- 仅适用于页面路由的 `getStaticPaths` 替代

### 为静态参数获取数据

```typescript
// app/blog/[slug]/page.tsx
export async function generateStaticParams() {
  const posts = await fetch('https://api.example.com/posts').then(r => r.json());

  return posts.map((post: { slug: string }) => ({
    slug: post.slug,
  }));
}

export default async function BlogPost({
  params
}: {
  params: { slug: string }
}) {
  const post = await fetch(`https://api.example.com/posts/${params.slug}`).then(r => r.json());

  return (
    <article>
      <h1>{post.title}</h1>
      <p>{post.content}</p>
    </article>
  );
}
```

### 多个动态段

```typescript
// app/products/[category]/[id]/page.tsx
export async function generateStaticParams() {
  const categories = await getCategories();

  const params = [];
  for (const category of categories) {
    const products = await getProducts(category.slug);
    for (const product of products) {
      params.push({
        category: category.slug,
        id: product.id,
      });
    }
  }

  return params;
}

export default function ProductPage({
  params
}: {
  params: { category: string; id: string }
}) {
  return <div>分类：{params.category}，产品：{params.id}</div>;
}
```

### 动态行为配置

```typescript
// app/blog/[id]/page.tsx
export async function generateStaticParams() {
  return [{ id: '1' }, { id: '2' }];
}

// 控制未预渲染路径的行为
export const dynamicParams = true; // 默认 - 允许实时生成
// export const dynamicParams = false; // 返回 404 对于未预渲染的路径

export default function BlogPost({
  params
}: {
  params: { id: string }
}) {
  return <div>文章 {params.id}</div>;
}
```

**选项：**
- `dynamicParams = true`（默认）：非预渲染路径按需生成
- `dynamicParams = false`：非预渲染路径返回 404

### 常见模式

**模式 1：基于 ID 的路由**
```typescript
export async function generateStaticParams() {
  return [
    { id: '1' },
    { id: '2' },
    { id: '3' },
  ];
}
```

**模式 2：从 API 获取**
```typescript
export async function generateStaticParams() {
  const items = await fetch('https://api.example.com/items').then(r => r.json());
  return items.map(item => ({ id: item.id }));
}
```

**模式 3：数据库查询**
```typescript
export async function generateStaticParams() {
  const posts = await db.post.findMany();
  return posts.map(post => ({ slug: post.slug }));
}
```

### 从页面路由迁移

**之前（页面路由）：**
```typescript
// pages/blog/[id].tsx
export async function getStaticPaths() {
  return {
    paths: [
      { params: { id: '1' } },
      { params: { id: '2' } },
    ],
    fallback: false,
  };
}

export async function getStaticProps({ params }) {
  return { props: { id: params.id } };
}
```

**之后（应用路由）：**
```typescript
// app/blog/[id]/page.tsx
export async function generateStaticParams() {
  return [
    { id: '1' },
    { id: '2' },
  ];
}

export const dynamicParams = false; // 等效于 fallback: false

export default function BlogPost({ params }: { params: { id: string } }) {
  return <div>文章 {params.id}</div>;
}
```

### 常见错误

**❌ 错误：使用 `'use client'`**
```typescript
'use client'; // 错误！generateStaticParams 仅适用于服务器组件

export async function generateStaticParams() {
  return [{ id: '1' }];
}
```

**❌ 错误：使用页面路由模式**
```typescript
export async function getStaticPaths() { // 错误的 API!
  return { paths: [...], fallback: false };
}
```

**❌ 错误：缺少导出关键字**
```typescript
async function generateStaticParams() { // 必须导出！
  return [{ id: '1' }];
}
```

**✅ 正确：干净的 Server Component**
```typescript
// app/blog/[id]/page.tsx
// 没有 'use client' 指令

export async function generateStaticParams() {
  return [{ id: '1' }, { id: '2' }];
}

export default function Page({ params }: { params: { id: string } }) {
  return <div>文章 {params.id}</div>;
}
```

**关键实施说明：**

当要求“编写”或“实现” `generateStaticParams` 时：
- **要**使用编辑或写入工具修改实际文件
- **要**将函数添加到现有的 page.tsx 文件
- **要**删除任何关于 generateStaticParams 的 TODO 评论
- **不要**只是以 Markdown 形式输出代码 - 实际实现它
- **不要**在不写入文件的情况下显示代码

## 测试和验证

在使用应用路由迁移或构建时，请验证：

1. **结构：**
   - 存在 `app/` 目录
   - 根 `layout.tsx` 存在并包含 `<html>` 和 `<body>`
   - 每个路径都有一个 `page.tsx` 文件

2. **元数据：**
   - 在应用路由中不导入 `next/head`
   - 从页面或布局导出元数据
   - 使用 `Metadata` 类型正确类型化元数据

3. **导航：**
   - 使用 `next/link` 组件
   - 不使用 `<a>` 标签进行内部导航

4. **清理：**
   - 从 `pages/` 目录中删除所有剩余的页面文件
   - 删除 `_app.tsx` 和 `_document.tsx`
   - 删除旧元数据模式

## 快速参考

### 文件结构映射

| 页面路由 | 应用路由 | 目的 |
|-------------|-----------|---------|
| `pages/index.tsx` | `app/page.tsx` | 主页 |
| `pages/about.tsx` | `app/about/page.tsx` | 关于 |
| `pages/[id].tsx` | `app/[id]/page.tsx` | 动态 |
| `pages/_app.tsx` | `app/layout.tsx` | 全局布局 |
| `pages/_document.tsx` | `app/layout.tsx` | HTML 结构 |
| `pages/api/hello.ts` | `app/api/hello/route.ts` | API 路由 |

### 常用命令

```bash
# 创建带有应用路由的新 Next.js 应用
npx create-next-app@latest my-app

# 运行开发服务器
npm run dev

# 构建生产版本
npm run build

# 启动生产服务器
npm start
```

## 其他资源

有关更高级的路由模式（并行路由、拦截路由、路由处理程序），请参阅 `nextjs-advanced-routing` 技能。

有关服务器与客户端组件的最佳实践和反模式，请参阅 `nextjs-server-client-components` 和 `nextjs-anti-patterns` 技能。
