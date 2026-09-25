# React Router 框架模式

框架模式是 React Router 提供的全栈开发体验，具有基于文件的路由、服务器端、客户端和静态渲染策略，数据加载和变更，以及类型安全的路由模块 API。

## 何时使用

- 配置新路由 (`app/routes.ts`)
- 使用 `loader` 或 `clientLoader` 加载数据
- 使用 `action` 或 `clientAction` 处理变更
- 使用 `<Link>`, `<NavLink>`, `<Form>`, `redirect` 和 `useNavigate` 进行导航
- 实现挂起/加载的 UI 状态
- 配置 SSR、SPA 模式或预渲染 (`react-router.config.ts`)
- 实现身份验证

## 参考

加载相关参考以获取特定 API/概念的详细指导：

| 参考                          | 使用场景                                      |
| ----------------------------- | -------------------------------------------- |
| `references/routing.md`       | 配置路由、嵌套路由、动态片段                 |
| `references/route-modules.md` | 理解所有路由模块导出                         |
| `references/special-files.md` | 自定义 root.tsx、添加全局导航/页脚、字体     |
| `references/data-loading.md`  | 使用加载器、流式传输、缓存加载数据           |
| `references/actions.md`       | 处理表单、变更、验证                         |
| `references/navigation.md`    | 链接、程序化导航、重定向                     |
| `references/pending-ui.md`    | 加载状态、乐观 UI                           |
| `references/error-handling.md` | 错误边界、错误报告                           |
| `references/rendering-strategies.md` | SSR 与 SPA 与预渲染配置                     |
| `references/middleware.md`    | 添加中间件（需要 v7.9.0+）                   |
| `references/sessions.md`      | Cookie 会话、身份验证、受保护路由             |
| `references/type-safety.md`   | 自动生成的路由类型、类型导入、类型安全       |

## 版本兼容性

某些功能需要特定版本的 React Router。**实施前务必验证：**

```bash
npm list react-router
```

| 功能                 | 最低版本 | 备注                         |
| --------------------- | -------- | ---------------------------- |
| 中间件               | 7.9.0+   | 需要 `v8_middleware` 标志   |
| 核心框架功能         | 7.0.0+   | 加载器、动作、Form 等       |

## 关键模式

这些是最重要的模式。加载相关参考以获取完整细节。

### 表单与变更

**搜索表单** - 使用 `<Form method="get">`，而不是 `onSubmit` 与 `setSearchParams`：

```tsx
// ✅ 正确
<Form method="get">
  <input name="q" />
</Form>

// ❌ 错误 - 不要手动处理搜索参数
<form onSubmit={(e) => { e.preventDefault(); setSearchParams(...) }}>
```

**内联变更** - 使用 `useFetcher`，而不是 `<Form>`（后者会导致页面导航）：

```tsx
const fetcher = useFetcher();
const optimistic = fetcher.formData?.get("favorite") === "true" ?? isFavorite;

<fetcher.Form method="post" action={`/favorites/${id}`}>
  <button>{optimistic ? "★" : "☆"}</button>
</fetcher.Form>;
```

参考 `references/actions.md` 获取完整模式。

### 布局

**全局 UI 属于 `root.tsx`** - 不要为导航/页脚创建单独的布局文件：

```tsx
// app/root.tsx - 在此处添加导航、页脚、提供者
export default function App() {
  return (
    <div>
      <nav>...</nav>
      <Outlet />
      <footer>...</footer>
    </div>
  );
}
```

**使用嵌套路由** 实现特定区域的布局。参考 `references/routing.md`。

### 路由模块导出

**`meta` 使用 `loaderData`**，而不是已弃用的 `data`：

```tsx
// ✅ 正确
export function meta({ loaderData }: Route.MetaArgs) { ... }

// ❌ 错误 - `data` 已弃用
export function meta({ data }: Route.MetaArgs) { ... }
```

参考 `references/route-modules.md` 获取所有导出。

## 更多文档

如果与 React Router 相关的内容未包含在这些参考中，您可以在官方文档中搜索：

https://reactrouter.com/docs
