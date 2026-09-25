# Next.js 最佳实践

在编写或审查 Next.js 代码时，请遵循这些规则。

## 文件约定

参见 [file-conventions.md](./file-conventions.md) 了解：
- 项目结构和特殊文件
- 路由片段（动态、捕获所有、分组）
- 并行和拦截路由
- v16 中的中间件重命名（middleware → proxy）

## RSC 边界

检测无效的 React Server 组件模式。

参见 [rsc-boundaries.md](./rsc-boundaries.md) 了解：
- 异步客户端组件检测（无效）
- 非序列化属性检测
- Server Action 异常

## 异步模式

Next.js 15+ 异步 API 变更。

参见 [async-patterns.md](./async-patterns.md) 了解：
- 异步 `params` 和 `searchParams`
- 异步 `cookies()` 和 `headers()`
- 迁移 codemod

## 运行时选择

参见 [runtime-selection.md](./runtime-selection.md) 了解：
- 默认使用 Node.js 运行时
- 何时适合使用 Edge 运行时

## 指令

参见 [directives.md](./directives.md) 了解：
- `'use client'`，`'use server'`（React）
- `'use cache'`（Next.js）

## 函数

参见 [functions.md](./functions.md) 了解：
- 导航钩子：`useRouter`，`usePathname`，`useSearchParams`，`useParams`
- 服务器函数：`cookies`，`headers`，`draftMode`，`after`
- 生成函数：`generateStaticParams`，`generateMetadata`

## 错误处理

参见 [error-handling.md](./error-handling.md) 了解：
- `error.tsx`，`global-error.tsx`，`not-found.tsx`
- `redirect`，`permanentRedirect`，`notFound`
- `forbidden`，`unauthorized`（认证错误）
- `unstable_rethrow` 用于 catch 块

## 数据模式

参见 [data-patterns.md](./data-patterns.md) 了解：
- 服务器组件 vs 服务器动作 vs 路由处理器
- 避免 数据级联（`Promise.all`，Suspense，preload）
- 客户端组件数据获取

## 路由处理器

参见 [route-handlers.md](./route-handlers.md) 了解：
- `route.ts` 基础
- GET 处理器与 `page.tsx` 冲突
- 环境行为（无 React DOM）
- 何时使用 vs 服务器动作

## 元数据和 OG 图片

参见 [metadata.md](./metadata.md) 了解：
- 静态和动态元数据
- `generateMetadata` 函数
- 使用 `next/og` 生成 OG 图片
- 基于文件的元数据约定

## 图片优化

参见 [image.md](./image.md) 了解：
- 始终使用 `next/image` 而不是 `<img>`
- 远程图片配置
- 响应式 `sizes` 属性
- 模糊占位符
- LCP 的优先加载

## 字体优化

参见 [font.md](./font.md) 了解：
- `next/font` 设置
- Google Fonts，本地字体
- Tailwind CSS 集成
- 预加载子集

## 打包

参见 [bundling.md](./bundling.md) 了解：
- 服务器不兼容的包
- CSS 导入（非 link 标签）
- Polyfills（已包含）
- ESM/CommonJS 问题
- 打包分析

## 脚本

参见 [scripts.md](./scripts.md) 了解：
- `next/script` vs 原生脚本标签
- 内联脚本需要 `id`
- 加载策略
- 使用 `@next/third-parties` 的 Google Analytics

## 水合错误

参见 [hydration-error.md](./hydration-error.md) 了解：
- 常见原因（浏览器 API，日期，无效 HTML）
- 使用错误覆盖层进行调试
- 每个原因的修复方法

## Suspense 边界

参见 [suspense-boundaries.md](./suspense-boundaries.md) 了解：
- 使用 `useSearchParams` 和 `usePathname` 的 CSR 回退
- 需要 Suspense 边界的钩子

## 并行和拦截路由

参见 [parallel-routes.md](./parallel-routes.md) 了解：
- 使用 `@slot` 和 `(.)` 拦截器的模态模式
- `default.tsx` 用于回退
- 使用 `router.back()` 正确关闭模态

## 自托管

参见 [self-hosting.md](./self-hosting.md) 了解：
- Docker 的 `output: 'standalone'`
- 多实例 ISR 的缓存处理器
- 什么可行 vs 需要额外设置

## 调试技巧

参见 [debug-tricks.md](./debug-tricks.md) 了解：
- 用于 AI 辅助调试的 MCP 端点
- 使用 `--debug-build-paths` 重建特定路由
