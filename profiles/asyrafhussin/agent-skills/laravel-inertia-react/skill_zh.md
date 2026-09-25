# Laravel + Inertia.js + React

使用 Laravel、Inertia.js 和 React 构建现代单体应用的全面模式。包含 30 多条规则，实现无缝全栈开发。

## 应用场景

在以下情况下参考这些指南：
- 创建 Inertia 页面组件
- 使用 useForm 钩子处理表单
- 管理共享数据和认证
- 实现持久化布局
- 页面间导航

## 按优先级分类的规则类别

| 优先级 | 类别 | 影响 | 前缀 |
|--------|------|------|------|
| 1 | 页面组件 | 关键 | `page-` |
| 2 | 表单与验证 | 关键 | `form-` |
| 3 | 导航与链接 | 高 | `nav-` |
| 4 | 共享数据 | 高 | `shared-` |
| 5 | 布局 | 中 | `layout-` |
| 6 | 文件上传 | 中 | `upload-` |
| 7 | 高级模式 | 低 | `advanced-` |

## 快速参考

### 1. 页面组件 (关键)

- `page-props-typing` - 从 Laravel 类型化页面属性
- `page-component-structure` - 标准页面组件模式
- `page-head-management` - 使用 Head 管理标题和元标签
- `page-default-layout` - 为页面分配布局

### 2. 表单与验证 (关键)

- `form-useform-basic` - 基本用法 of useForm
- `form-validation-errors` - 显示 Laravel 验证错误
- `form-processing-state` - 处理表单提交状态
- `form-reset-preserve` - 重置与保留表单数据
- `form-nested-data` - 处理嵌套表单数据
- `form-transform` - 提交前转换数据

### 3. 导航与链接 (高)

- `nav-link-component` - 使用 Link 进行导航
- `nav-preserve-state` - 保留滚动和状态
- `nav-partial-reloads` - 仅重新加载已更改的部分
- `nav-replace-history` - 替换与推入历史记录

### 4. 共享数据 (高)

- `shared-auth-user` - 访问认证用户
- `shared-flash-messages` - 处理闪现消息
- `shared-global-props` - 访问全局属性
- `shared-typescript` - 类型化共享数据

### 5. 布局 (中)

- `layout-persistent` - 持久化布局模式
- `layout-nested` - 嵌套布局
- `layout-default` - 默认布局分配
- `layout-conditional` - 条件布局

### 6. 文件上传 (中)

- `upload-basic` - 基本文件上传
- `upload-progress` - 上传进度跟踪
- `upload-multiple` - 多文件上传

### 7. 高级模式 (低)

- `advanced-polling` - 实时轮询
- `advanced-prefetch` - 预取页面
- `advanced-modal-pages` - 模态作为页面
- `advanced-infinite-scroll` - 无限滚动

## 基本模式

### 使用 TypeScript 的页面组件

```tsx
// resources/js/Pages/Posts/Index.tsx
import { Head, Link } from '@inertiajs/react'

interface Post {
  id: number
  title: string
  excerpt: string
  created_at: string
  author: {
    id: number
    name: string
  }
}

interface Props {
  posts: {
    data: Post[]
    links: { url: string | null; label: string; active: boolean }[]
  }
  filters: {
    search?: string
  }
}

export default function Index({ posts, filters }: Props) {
  return (
    <>
      <Head title="Posts" />

      <div className="container mx-auto py-8">
        <h1 className="text-2xl font-bold mb-6">Posts</h1>

        <div className="space-y-4">
          {posts.data.map((post) => (
            <article key={post.id} className="p-4 bg-white rounded-lg shadow">
              <Link href={route('posts.show', post.id)}>
                <h2 className="text-xl font-semibold hover:text-blue-600">
                  {post.title}
                </h2>
              </Link>
              <p className="text-gray-600 mt-2">{post.excerpt}</p>
              <p className="text-sm text-gray-400 mt-2">
                By {post.author.name}
              </p>
            </article>
          ))}
        </div>
      </div>
    </>
  )
}
```

### 使用 useForm 的表单

```tsx
// resources/js/Pages/Posts/Create.tsx
import { Head, useForm, Link } from '@inertiajs/react'
import { FormEvent } from 'react'

interface Category {
  id: number
  name: string
}

interface Props {
  categories: Category[]
}

export default function Create({ categories }: Props) {
  const { data, setData, post, processing, errors, reset } = useForm({
    title: '',
    body: '',
    category_id: '',
  })

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    post(route('posts.store'), {
      onSuccess: () => reset(),
    })
  }

  return (
    <>
      <Head title="Create Post" />

      <form onSubmit={handleSubmit} className="max-w-2xl mx-auto py-8">
        <div className="mb-4">
          <label htmlFor="title" className="block font-medium mb-1">
            Title
          </label>
          <input
            id="title"
            type="text"
            value={data.title}
            onChange={(e) => setData('title', e.target.value)}
            className="w-full border rounded px-3 py-2"
          />
          {errors.title && (
            <p className="text-red-500 text-sm mt-1">{errors.title}</p>
          )}
        </div>

        <div className="mb-4">
          <label htmlFor="category" className="block font-medium mb-1">
            Category
          </label>
          <select
            id="category"
            value={data.category_id}
            onChange={(e) => setData('category_id', e.target.value)}
            className="w-full border rounded px-3 py-2"
          >
            <option value="">Select a category</option>
            {categories.map((category) => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </select>
          {errors.category_id && (
            <p className="text-red-500 text-sm mt-1">{errors.category_id}</p>
          )}
        </div>

        <div className="mb-4">
          <label htmlFor="body" className="block font-medium mb-1">
            Content
          </label>
          <textarea
            id="body"
            value={data.body}
            onChange={(e) => setData('body', e.target.value)}
            rows={10}
            className="w-full border rounded px-3 py-2"
          />
          {errors.body && (
            <p className="text-red-500 text-sm mt-1">{errors.body}</p>
          )}
        </div>

        <div className="flex gap-4">
          <button
            type="submit"
            disabled={processing}
            className="px-4 py-2 bg-blue-600 text-white rounded disabled:opacity-50"
          >
            {processing ? 'Creating...' : 'Create Post'}
          </button>

          <Link
            href={route('posts.index')}
            className="px-4 py-2 border rounded"
          >
            Cancel
          </Link>
        </div>
      </form>
    </>
  )
}
```

### 持久化布局

```tsx
// resources/js/Layouts/AppLayout.tsx
import { Link, usePage } from '@inertiajs/react'
import { ReactNode } from 'react'

interface Props {
  children: ReactNode
}

export default function AppLayout({ children }: Props) {
  const { auth } = usePage().props as { auth: { user: { name: string } } }

  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-white shadow">
        <div className="container mx-auto px-4 py-3 flex justify-between">
          <Link href="/" className="font-bold">
            My App
          </Link>
          <span>Welcome, {auth.user.name}</span>
        </div>
      </nav>

      <main className="container mx-auto px-4 py-8">
        {children}
      </main>
    </div>
  )
}

// resources/js/Pages/Dashboard.tsx
import AppLayout from '@/Layouts/AppLayout'

export default function Dashboard() {
  return <h1>Dashboard</h1>
}

// 分配持久化布局
Dashboard.layout = (page: ReactNode) => <AppLayout>{page}</AppLayout>
```

### Laravel 控制器

```php
<?php

namespace App\Http\Controllers;

use App\Http\Requests\StorePostRequest;
use App\Models\Post;
use App\Models\Category;
use Illuminate\Http\RedirectResponse;
use Inertia\Inertia;
use Inertia\Response;

class PostController extends Controller
{
    public function index(): Response
    {
        return Inertia::render('Posts/Index', [
            'posts' => Post::with('author:id,name')
                ->latest()
                ->paginate(10),
            'filters' => request()->only('search'),
        ]);
    }

    public function create(): Response
    {
        return Inertia::render('Posts/Create', [
            'categories' => Category::all(['id', 'name']),
        ]);
    }

    public function store(StorePostRequest $request): RedirectResponse
    {
        $post = Post::create([
            ...$request->validated(),
            'user_id' => auth()->id(),
        ]);

        return redirect()
            ->route('posts.show', $post)
            ->with('success', 'Post created successfully.');
    }

    public function show(Post $post): Response
    {
        return Inertia::render('Posts/Show', [
            'post' => $post->load('author', 'category'),
        ]);
    }
}
```

### 共享数据 (HandleInertiaRequests)

```php
<?php

namespace App\Http\Middleware;

use Illuminate\Http\Request;
use Inertia\Middleware;

class HandleInertiaRequests extends Middleware
{
    public function share(Request $request): array
    {
        return array_merge(parent::share($request), [
            'auth' => [
                'user' => $request->user() ? [
                    'id' => $request->user()->id,
                    'name' => $request->user()->name,
                    'email' => $request->user()->email,
                ] : null,
            ],
            'flash' => [
                'success' => $request->session()->get('success'),
                'error' => $request->session()->get('error'),
            ],
        ]);
    }
}
```

### 闪现消息组件

```tsx
// resources/js/Components/FlashMessages.tsx
import { usePage } from '@inertiajs/react'
import { useEffect, useState } from 'react'

export default function FlashMessages() {
  const { flash } = usePage().props as {
    flash: { success?: string; error?: string }
  }
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    if (flash.success || flash.error) {
      setVisible(true)
      const timer = setTimeout(() => setVisible(false), 3000)
      return () => clearTimeout(timer)
    }
  }, [flash])

  if (!visible) return null

  return (
    <div className="fixed top-4 right-4 z-50">
      {flash.success && (
        <div className="bg-green-500 text-white px-4 py-2 rounded shadow">
          {flash.success}
        </div>
      )}
      {flash.error && (
        <div className="bg-red-500 text-white px-4 py-2 rounded shadow">
          {flash.error}
        </div>
      )}
    </div>
  )
}
```

## 使用方法

阅读单个规则文件获取详细说明和代码示例：

```
rules/form-useform-basic.md
rules/page-props-typing.md
rules/layout-persistent.md
```

## 项目结构

```
laravel-inertia-react/
├── SKILL.md                 # 本文件 - 概述和示例
├── README.md                # 快速参考指南
├── AGENTS.md                # AI 代理集成指南
├── metadata.json            # 技能元数据和引用
└── rules/
    ├── _sections.md         # 规则类别和优先级
    ├── _template.md         # 新规则的模板
    ├── page-*.md            # 页面组件模式 (6 条规则)
    ├── form-*.md            # 表单处理模式 (8 条规则)
    ├── nav-*.md             # 导航模式 (5 条规则)
    ├── shared-*.md          # 共享数据模式 (4 条规则)
    └── layout-*.md          # 布局模式 (1 条规则)
```

## 参考

- [Inertia.js 文档](https://inertiajs.com/) - 官方 Inertia.js 文档
- [Laravel 文档](https://laravel.com/docs) - Laravel 框架文档
- [React 文档](https://react.dev/) - 官方 React 文档
- [Ziggy](https://github.com/tighten/ziggy) - Laravel JavaScript 路由助手

## 许可证

MIT 许可证。本技能按原样提供，用于教育和开发目的。

## 元数据

- **版本**: 1.0.1
- **最后更新**: 2026-01-17
- **维护者**: Asyraf Hussin
- **规则数量**: 6 类别中的 24 条规则
- **技术栈**: Laravel 10+、Inertia.js 1.0+、React 18+、TypeScript 5+
