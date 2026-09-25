# TanStack Query 最佳实践

React 应用中实现 TanStack Query (React Query) 模式的全面指南。这些规则优化了数据获取、缓存、变异和服务器状态同步。

## 应用场景

- 创建新的数据获取逻辑
- 设置查询配置
- 实现变异和乐观更新
- 配置缓存策略
- 集成 SSR/SSG
- 重构现有的数据获取代码

## 按优先级分类的规则类别

| 优先级 | 类别 | 规则数量 | 影响 |
|--------|------|----------|------|
| CRITICAL | 查询键 | 5 条规则 | 防止缓存错误和数据不一致 |
| CRITICAL | 缓存 | 5 条规则 | 优化性能和数据新鲜度 |
| HIGH | 变异 | 6 条规则 | 确保数据完整性和 UI 一致性 |
| HIGH | 错误处理 | 3 条规则 | 防止糟糕的用户体验 |
| MEDIUM | 预取 | 4 条规则 | 提高感知性能 |
| MEDIUM | 并行查询 | 2 条规则 | 实现动态并行获取 |
| MEDIUM | 无限查询 | 3 条规则 | 防止分页错误 |
| MEDIUM | SSR 集成 | 4 条规则 | 实现正确的 hydration |
| LOW | 性能 | 4 条规则 | 减少不必要的重新渲染 |
| LOW | 离线支持 | 2 条规则 | 支持离线优先模式 |

## 快速参考

### 查询键 (前缀: `qk-`)

- `qk-array-structure` — 始终使用数组作为查询键
- `qk-include-dependencies` — 包含查询依赖的所有变量
- `qk-hierarchical-organization` — 按层级组织键 (实体 → id → 筛选条件)
- `qk-factory-pattern` — 在复杂应用中使用查询键工厂
- `qk-serializable` — 确保所有键部分都是 JSON-可序列化的

### 缓存 (前缀: `cache-`)

- `cache-stale-time` — 根据数据波动性设置合适的 staleTime
- `cache-gc-time` — 配置 gcTime 用于非活动查询保留
- `cache-defaults` — 在 QueryClient 层级设置合理的默认值
- `cache-invalidation` — 使用目标化失效而非广泛模式
- `cache-placeholder-vs-initial` — 理解占位符与初始数据的不同

### 变异 (前缀: `mut-`)

- `mut-invalidate-queries` — 变异后始终失效相关查询
- `mut-optimistic-updates` — 实现乐观更新以提供响应式 UI
- `mut-rollback-context` — 从 onMutate 提供回滚上下文
- `mut-error-handling` — 优雅处理变异错误
- `mut-loading-states` — 使用 isPending 表示变异加载状态
- `mut-mutation-state` — 使用 useMutationState 进行跨组件跟踪

### 错误处理 (前缀: `err-`)

- `err-error-boundaries` — 使用 useQueryErrorResetBoundary 配合错误边界
- `err-retry-config` — 合理配置重试逻辑
- `err-fallback-data` — 在适当情况下提供回退数据

### 预取 (前缀: `pf-`)

- `pf-intent-prefetch` — 在用户意图时预取 (悬停、聚焦)
- `pf-route-prefetch` — 在路由转换期间预取数据
- `pf-stale-time-config` — 预取时设置 staleTime
- `pf-ensure-query-data` — 使用 ensureQueryData 进行条件预取

### 无限查询 (前缀: `inf-`)

- `inf-page-params` — 始终提供 getNextPageParam
- `inf-loading-guards` — 在获取更多数据前检查 isFetchingNextPage
- `inf-max-pages` — 考虑 maxPages 用于大型数据集

### SSR 集成 (前缀: `ssr-`)

- `ssr-dehydration` — 使用 dehydrate/hydrate 模式进行 SSR
- `ssr-client-per-request` — 每个请求创建 QueryClient
- `ssr-stale-time-server` — 在服务器设置更高的 staleTime
- `ssr-hydration-boundary` — 使用 HydrationBoundary 包裹

### 并行查询 (前缀: `parallel-`)

- `parallel-use-queries` — 使用 useQueries 实现动态并行查询
- `query-cancellation` — 正确实现查询取消

### 性能 (前缀: `perf-`)

- `perf-select-transform` — 使用 select 转换/过滤数据
- `perf-structural-sharing` — 利用结构共享
- `perf-notify-change-props` — 使用 notifyOnChangeProps 限制重新渲染
- `perf-placeholder-data` — 使用 placeholderData 实现即时 UI

### 离线支持 (前缀: `offline-`)

- `network-mode` — 配置网络模式支持离线
- `persist-queries` — 配置查询持久化支持离线

## 如何使用

`rules/` 目录中的每个规则文件包含：
1. **说明** — 为什么这个模式很重要
2. **不良示例** — 要避免的反模式
3. **良好示例** — 推荐的实现方式
4. **上下文** — 何时应用或跳过此规则

## 完整参考

有关详细指导和代码示例，请参阅 `rules/` 目录中的各个规则文件。
