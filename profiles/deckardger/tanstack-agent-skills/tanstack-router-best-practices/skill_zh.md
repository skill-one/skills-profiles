# TanStack Router 最佳实践

React 应用中实现 TanStack Router 模式的全面指南。这些规则优化了类型安全、数据加载、导航和代码组织。

## 应用场景

- 设置应用路由
- 创建新路由和布局
- 实现搜索参数处理
- 配置数据加载器
- 设置代码拆分
- 与 TanStack Query 集成
- 重构导航模式

## 按优先级分类的规则

| 优先级 | 类别 | 规则 | 影响 |
|--------|------|------|------|
| CRITICAL | 类型安全 | 4 条规则 | 防止运行时错误并支持重构 |
| CRITICAL | 路由组织 | 5 条规则 | 确保可维护的路由结构 |
| HIGH | 路由器配置 | 1 条规则 | 全局路由默认设置 |
| HIGH | 数据加载 | 6 条规则 | 优化数据获取和缓存 |
| HIGH | 搜索参数 | 5 条规则 | 实现类型安全的 URL 状态 |
| HIGH | 错误处理 | 1 条规则 | 优雅处理 404 和错误 |
| MEDIUM | 导航 | 5 条规则 | 提升用户体验和可访问性 |
| MEDIUM | 代码拆分 | 3 条规则 | 减少包体积 |
| MEDIUM | 预加载 | 3 条规则 | 提升感知性能 |
| LOW | 路由上下文 | 3 条规则 | 支持依赖注入 |

## 快速参考

### 类型安全（前缀：`ts-`）

- `ts-register-router` — 为全局推断注册路由类型
- `ts-use-from-param` — 使用 `from` 参数进行类型窄化
- `ts-route-context-typing` — 使用 createRootRouteWithContext 类型化路由上下文
- `ts-query-options-loader` — 在加载器中使用 queryOptions 进行类型推断

### 路由器配置（前缀：`router-`）

- `router-default-options` — 配置路由默认设置（scrollRestoration、defaultErrorComponent 等）

### 路由组织（前缀：`org-`）

- `org-file-based-routing` — 优先使用基于文件的路由以符合规范
- `org-route-tree-structure` — 遵循分层路由树模式
- `org-pathless-layouts` — 使用无路径路由实现共享布局
- `org-index-routes` — 理解索引路由与布局路由的区别
- `org-virtual-routes` — 理解虚拟文件路由

### 数据加载（前缀：`load-`）

- `load-use-loaders` — 使用路由加载器进行数据获取
- `load-loader-deps` — 定义 loaderDeps 以控制缓存
- `load-ensure-query-data` — 使用 ensureQueryData 与 TanStack Query
- `load-deferred-data` — 分离关键和非关键数据
- `load-error-handling` — 合理处理加载器错误
- `load-parallel` — 利用并行路由加载

### 搜索参数（前缀：`search-`）

- `search-validation` — 始终验证搜索参数
- `search-type-inheritance` — 利用父级搜索参数类型
- `search-middleware` — 使用搜索参数中间件
- `search-defaults` — 提供合理的默认值
- `search-custom-serializer` — 配置自定义搜索参数序列化器

### 错误处理（前缀：`err-`）

- `err-not-found` — 正确处理未找到的路由

### 导航（前缀：`nav-`）

- `nav-link-component` — 优先使用 Link 组件进行导航
- `nav-active-states` — 配置活动链接状态
- `nav-use-navigate` — 使用 useNavigate 进行程序化导航
- `nav-relative-paths` — 理解相对路径导航
- `nav-route-masks` — 使用路由掩码处理模态 URL

### 代码拆分（前缀：`split-`）

- `split-lazy-routes` — 使用 .lazy.tsx 进行代码拆分
- `split-critical-path` — 将关键配置保留在主路由文件中
- `split-auto-splitting` — 在可能的情况下启用 autoCodeSplitting

### 预加载（前缀：`preload-`）

- `preload-intent` — 启用基于意图的预加载
- `preload-stale-time` — 配置预加载过期时间
- `preload-manual` — 策略性地使用手动预加载

### 路由上下文（前缀：`ctx-`）

- `ctx-root-context` — 在根路由中定义上下文
- `ctx-before-load` — 在 beforeLoad 中扩展上下文
- `ctx-dependency-injection` — 使用上下文进行依赖注入

## 使用方法

`rules/` 目录中的每个规则文件包含：

1. **说明** — 为什么这个模式很重要
2. **不良示例** — 需要避免的反模式
3. **良好示例** — 推荐的实现方式
4. **上下文** — 何时应用或跳过此规则

## 完整参考

有关详细指南和代码示例，请参阅 `rules/` 目录中的各个规则文件。
