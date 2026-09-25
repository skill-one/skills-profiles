# @json-render/next

一个将 JSON 规范转换为完整 Next.js 应用的渲染器，包含路由、页面、布局、元数据和 SSR 支持。

## 快速入门

```bash
npm install @json-render/core @json-render/react @json-render/next
```

### 1. 定义你的规范

```typescript
// lib/spec.ts
import type { NextAppSpec } from "@json-render/next";

export const spec: NextAppSpec = {
  metadata: {
    title: { default: "My App", template: "%s | My App" },
    description: "一个 json-render Next.js 应用",
  },
  layouts: {
    main: {
      root: "shell",
      elements: {
        shell: { type: "Container", props: {}, children: ["nav", "slot"] },
        nav: { type: "NavBar", props: { links: [
          { href: "/", label: "Home" },
          { href: "/about", label: "About" },
        ]}, children: [] },
        slot: { type: "Slot", props: {}, children: [] },
      },
    },
  },
  routes: {
    "/": {
      layout: "main",
      metadata: { title: "Home" },
      page: {
        root: "hero",
        elements: {
          hero: { type: "Card", props: { title: "Welcome" }, children: [] },
        },
      },
    },
    "/about": {
      layout: "main",
      metadata: { title: "About" },
      page: {
        root: "content",
        elements: {
          content: { type: "Card", props: { title: "About Us" }, children: [] },
        },
      },
    },
  },
};
```

### 2. 创建应用

```typescript
// lib/app.ts
import { createNextApp } from "@json-render/next/server";
import { spec } from "./spec";

export const { Page, generateMetadata, generateStaticParams } = createNextApp({
  spec,
  loaders: {
    // 服务器端数据加载器（可选）
    loadPost: async ({ slug }) => {
      const post = await getPost(slug as string);
      return { post };
    },
  },
});
```

### 3. 连接路由文件

```tsx
// app/[[...slug]]/page.tsx
export { Page as default, generateMetadata, generateStaticParams } from "@/lib/app";
```

```tsx
// app/[[...slug]]/layout.tsx
import { NextAppProvider } from "@json-render/next";
import { registry, handlers } from "@/lib/registry";

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <NextAppProvider registry={registry} handlers={handlers}>
          {children}
        </NextAppProvider>
      </body>
    </html>
  );
}
```

## 关键概念

### NextAppSpec

顶层的规范定义了一个完整的 Next.js 应用：

- **metadata**: 根级 SEO 元数据（标题模板、描述、OpenGraph）
- **layouts**: 可重用的布局元素树（每个都必须包含一个 `Slot` 组件）
- **routes**: 路由定义，按 URL 模式键值对
- **state**: 全局初始状态，跨所有路由共享

### 路由模式

路由使用 Next.js URL  conventions：

- `"/"` -- 首页
- `"/about"` -- 静态路由
- `"/blog/[slug]"` -- 动态片段
- `"/docs/[...path]"` -- 捕获所有片段
- `"/settings/[[...path]]"` -- 可选捕获所有片段

### 布局

布局包裹页面内容。每个布局必须包含一个 `Slot` 组件，页面内容将在此渲染。布局在 `spec.layouts` 中定义一次，并通过 `layout` 字段在路由中引用。

### 内置组件

- **Slot**: 布局中的占位符，用于渲染页面内容
- **Link**: 客户端导航链接（包裹 `next/link`）

### 内置操作

- **setState**: 更新状态值。参数：`{ statePath, value }`
- **pushState**: 向数组追加。参数：`{ statePath, value, clearStatePath? }`
- **removeState**: 按索引从数组中移除。参数：`{ statePath, index }`
- **navigate**: 客户端导航。参数：`{ href }`

### 数据加载器

在渲染服务器组件之前运行的异步函数。结果将合并到页面的初始状态中。

```typescript
createNextApp({
  spec,
  loaders: {
    loadPost: async ({ slug }) => {
      const post = await db.post.findUnique({ where: { slug } });
      return { post };
    },
  },
});
```

### SSR

页面会自动服务器渲染。`createNextApp` 的 `Page` 组件是一个异步服务器组件，它：

1. 匹配规范中的路由
2. 运行服务器端数据加载器
3. 生成元数据
4. 将解析的规范传递给客户端渲染器进行挂载

### 入口点

- `@json-render/next` -- 客户端组件（NextAppProvider、PageRenderer、Link）
- `@json-render/next/server` -- 服务器工具（createNextApp、matchRoute、schema）

## API 参考

### 服务器导出 (`@json-render/next/server`)

- `createNextApp(options)` -- 创建 Page、generateMetadata、generateStaticParams
- `schema` -- Next.js 应用的自定义 schema（用于 AI 目录生成）
- `matchRoute(spec, pathname)` -- 将 URL 匹配到路由规范
- `resolveMetadata(spec, route)` -- 解析路由的元数据
- `slugToPath(slug)` -- 将捕获所有 slug 数组转换为路径名
- `collectStaticParams(spec)` -- 收集所有路由的静态参数

### 客户端导出 (`@json-render/next`)

- `NextAppProvider` -- 提供上下文，包含 registry 和 handlers
- `PageRenderer` -- 渲染带有可选布局的页面规范
- `NextErrorBoundary` -- 错误边界组件
- `NextLoading` -- 加载状态组件
- `NextNotFound` -- 未找到组件
- `Link` -- 内置导航组件（包裹 next/link）
