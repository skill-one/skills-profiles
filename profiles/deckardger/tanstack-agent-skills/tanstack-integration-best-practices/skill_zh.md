# TanStack 集成最佳实践

有效集成 TanStack Query、Router 和 Start 的指南。这些模式确保了整个栈中的数据流、缓存协调和类型安全达到最佳效果。

## 应用场景

- 设置新的 TanStack Start 项目
- 将 TanStack Query 与 TanStack Router 集成
- 配置带查询预加载的 SSR
- 协调路由和查询之间的缓存
- 设置类型安全的请求数据模式

## 按优先级分类的规则类别

| 优先级 | 类别 | 规则数量 | 影响 |
|--------|------|----------|------|
| CRITICAL | 设置 | 3 条规则 | 基础配置 |
| CRITICAL | SSR 集成 | 1 条规则 | 路由 + 查询 SSR 设置 |
| HIGH | 数据流 | 4 条规则 | 正确的请求数据模式 |
| MEDIUM | 缓存 | 3 条规则 | 性能优化 |
| MEDIUM | SSR | 2 条规则 | 额外的 SSR 模式 |

## 快速参考

### 设置 (前缀: `setup-`)

- `setup-query-client-context` — 通过路由上下文传递 QueryClient
- `setup-provider-wrapping` — 正确使用 QueryClientProvider 包裹
- `setup-stale-time-coordination` — 协调路由和查询之间的 staleTime

### 数据流 (前缀: `flow-`)

- `flow-loader-query-pattern` — 使用 ensureQueryData 与 loaders
- `flow-suspense-query-component` — 在组件中使用 useSuspenseQuery
- `flow-mutations-invalidation` — 协调突变与查询失效
- `flow-server-functions-queries` — 使用服务器函数处理查询

### 缓存 (前缀: `cache-`)

- `cache-single-source` — 让 TanStack Query 管理缓存
- `cache-preload-coordination` — 协调路由和查询之间的预加载
- `cache-invalidation-patterns` — 统一失效模式

### SSR 集成 (前缀: `ssr-`)

- `ssr-dehydrate-hydrate` — 使用 setupRouterSsrQueryIntegration 实现自动 SSR

### 额外的 SSR (前缀: `ssr-`)

- `ssr-per-request-client` — 每个请求创建 QueryClient
- `ssr-streaming-queries` — 处理查询流

## 使用方法

`rules/` 目录中的每个规则文件包含：
1. **说明** — 为什么这个模式很重要
2. **不良示例** — 需要避免的反模式
3. **良好示例** — 推荐的实现方式
4. **适用场景** — 何时应用或跳过此规则

## 完整参考

详细指南和代码示例请参阅 `rules/` 目录中的各个规则文件。
