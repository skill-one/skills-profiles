---
name: nuqs
description: nuqs（类型安全的URL查询状态）在Next.js和其他React框架中的最佳实践。当编写、审查或重构使用nuqs进行URL状态管理的代码时，应使用此技能。它会在涉及useQueryState、useQueryStates、搜索参数、URL状态、查询参数、nuqs解析器、limitUrlUpdates、标准模式、NuqsAdapter或带状态的Next.js路由的任务中触发。
---

# 社区 nuqs Next.js & React 最佳实践

全面指南，使用 nuqs 在 Next.js、React Router、TanStack Router、Remix 和纯 React 中进行类型安全的 URL 查询状态管理。涵盖 nuqs v2.5–v2.9 的功能。包含 8 个类别中的 39 条规则，按影响优先级排序，以指导代码生成、重构和代码审查。

## 何时应用

在以下情况下参考这些指南：
- 使用 nuqs 实现基于 URL 的状态
- 在 Next.js 或 React Router 项目中设置 nuqs
- 配置 URL 参数的解析器
- 将 URL 状态与服务器组件集成
- 优化 URL 更新性能（`limitUrlUpdates`、键隔离）
- 通过标准模式与 tRPC / TanStack Router / 表单共享解析器定义
- 调试与 nuqs 相关的问题

## 按优先级划分的规则类别

| 优先级 | 类别 | 影响 | 前缀 |
|--------|------|------|------|
| 1 | 解析器配置 | 关键 | `parser-` |
| 2 | 适配器与设置 | 关键 | `setup-` |
| 3 | 状态管理 | 高 | `state-` |
| 4 | 服务器集成 | 高 | `server-` |
| 5 | 性能优化 | 中 | `perf-` |
| 6 | 历史记录与导航 | 中 | `history-` |
| 7 | 调试与测试 | 低-中 | `debug-` |
| 8 | 高级模式 | 低 | `advanced-` |

## 快速参考

### 1. 解析器配置 (关键)

- [`parser-use-typed-parsers`](references/parser-use-typed-parsers.md) — 为非字符串值使用类型化解析器
- [`parser-with-default`](references/parser-with-default.md) — 用于非空状态使用 withDefault
- [`parser-enum-validation`](references/parser-enum-validation.md) — 为受约束值使用枚举解析器
- [`parser-array-format`](references/parser-array-format.md) — 选择正确的数组解析器格式
- [`parser-json-validation`](references/parser-json-validation.md) — 验证 JSON 解析器输入
- [`parser-date-format`](references/parser-date-format.md) — 选择合适的日期解析器
- [`parser-index-offset`](references/parser-index-offset.md) — 使用 parseAsIndex 进行基于 1 的 URL 显示

### 2. 适配器与设置 (关键)

- [`setup-nuqs-adapter`](references/setup-nuqs-adapter.md) — 用 NuqsAdapter 包装应用
- [`setup-use-client`](references/setup-use-client.md) — 为钩子添加 'use client' 指令
- [`setup-import-server`](references/setup-import-server.md) — 从 nuqs/server 导入服务器工具
- [`setup-nextjs-version`](references/setup-nextjs-version.md) — 确保兼容的 Next.js 版本
- [`setup-shared-parsers`](references/setup-shared-parsers.md) — 在专用文件中定义共享解析器
- [`setup-default-options`](references/setup-default-options.md) — 在 NuqsAdapter 上配置应用范围的默认值（v2.5+）

### 3. 状态管理 (高)

- [`state-use-query-states`](references/state-use-query-states.md) — 为相关参数使用 useQueryStates
- [`state-clear-with-null`](references/state-clear-with-null.md) — 使用 null 清除 URL 参数
- [`state-avoid-derived`](references/state-avoid-derived.md) — 避免从 URL 参数派生的状态
- [`state-options-inheritance`](references/state-options-inheritance.md) — 使用 withOptions 进行解析器级别的配置
- [`state-setter-return`](references/state-setter-return.md) — 使用设置器返回值进行 URL 访问
- [`state-standard-schema`](references/state-standard-schema.md) — 使用标准模式进行跨库验证（v2.5+）

### 4. 服务器集成 (高)

- [`server-search-params-cache`](references/server-search-params-cache.md) — 使用 createSearchParamsCache（或 createLoader）为服务器组件
- [`server-shallow-false`](references/server-shallow-false.md) — 使用 shallow:false 触发服务器重新渲染
- [`server-use-transition`](references/server-use-transition.md) — 集成 useTransition 进行加载状态
- [`server-parse-before-get`](references/server-parse-before-get.md) — 在服务器组件中在 get() 之前调用 parse()
- [`server-next15-async`](references/server-next15-async.md) — 处理 Next.js 15+ 中的异步 searchParams

### 5. 性能优化 (中)

- [`perf-throttle-updates`](references/perf-throttle-updates.md) — 使用 `limitUrlUpdates` 减缓快速 URL 更新
- [`perf-debounce-search`](references/perf-debounce-search.md) — 使用内置的 `limitUrlUpdates` 进行搜索输入防抖
- [`perf-clear-on-default`](references/perf-clear-on-default.md) — 使用 clearOnDefault 进行干净的 URL
- [`perf-avoid-rerender`](references/perf-avoid-rerender.md) — 使用 URL 状态（Next.js）记忆化组件
- [`perf-key-isolation`](references/perf-key-isolation.md) — 在 Next.js 外依赖键隔离（v2.5+）
- [`perf-serialize-utility`](references/perf-serialize-utility.md) — 使用 createSerializer 为链接 URL

### 6. 历史记录与导航 (中)

- [`history-push-navigation`](references/history-push-navigation.md) — 选择 history:push 与 history:replace
- [`history-scroll-behavior`](references/history-scroll-behavior.md) — 控制 URL 更改时的滚动行为

### 7. 调试与测试 (低-中)

- [`debug-enable-logging`](references/debug-enable-logging.md) — 启用调试日志进行故障排除
- [`debug-testing`](references/debug-testing.md) — 使用 URL 状态测试组件

### 8. 高级模式 (低)

- [`advanced-custom-parsers`](references/advanced-custom-parsers.md) — 为复杂类型创建自定义解析器
- [`advanced-url-keys`](references/advanced-url-keys.md) — 使用 urlKeys 进行更短的 URL
- [`advanced-eq-function`](references/advanced-eq-function.md) — 为对象解析器实现 eq 函数
- [`advanced-framework-adapters`](references/advanced-framework-adapters.md) — 使用框架特定的适配器
- [`advanced-process-url-search-params`](references/advanced-process-url-search-params.md) — 使用 `processUrlSearchParams`（v2.6+）规范化 URL 形状

## 如何使用

阅读单个参考文件以获取详细说明和代码示例：

- [部分定义](references/_sections.md) — 类别结构和影响级别
- [规则模板](assets/templates/_template.md) — 添加新规则的模板

## 参考文件

| 文件 | 描述 |
|------|------|
| [AGENTS.md](AGENTS.md) | 包含所有规则的完整编译指南 |
| [references/_sections.md](references/_sections.md) | 类别定义和排序 |
| [assets/templates/_template.md](assets/templates/_template.md) | 新规则的模板 |
| [metadata.json](metadata.json) | 版本和参考信息 |
