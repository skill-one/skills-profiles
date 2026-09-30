---
name: vercel-react-best-practices
description: Vercel 工程团队提供的 React 和 Next.js 性能优化指南。在编写、审查或重构 React/Next.js 代码时，应使用此技能以确保最佳性能模式。适用于涉及 React 组件、Next.js 页面、数据获取、打包优化或性能提升的任务。
---

# Vercel React 最佳实践

Vercel 维护的 React 和 Next.js 应用程序性能优化综合指南。包含 8 个类别下的 70 条规则，按影响程度排序，用于指导自动化重构和代码生成。

## 应用时机

在以下情况参考这些指南：
- 编写新的 React 组件或 Next.js 页面
- 实现数据获取（客户端或服务器端）
- 审查代码以发现性能问题
- 重构现有的 React/Next.js 代码
- 优化打包大小或加载时间

## 按优先级排序的规则类别

| 优先级 | 类别 | 影响 | 前缀 |
|--------|------|------|------|
| 1 | 消除级联 | CRITICAL | `async-` |
| 2 | 打包大小优化 | CRITICAL | `bundle-` |
| 3 | 服务器端性能 | HIGH | `server-` |
| 4 | 客户端数据获取 | MEDIUM-HIGH | `client-` |
| 5 | 重绘优化 | MEDIUM | `rerender-` |
| 6 | 渲染性能 | MEDIUM | `rendering-` |
| 7 | JavaScript 性能 | LOW-MEDIUM | `js-` |
| 8 | 高级模式 | LOW | `advanced-` |

## 快速参考

### 1. 消除级联 (CRITICAL)

- `async-cheap-condition-before-await` - 在等待标志或远程值之前检查廉价的同步条件
- `async-defer-await` - 将 await 移入实际使用的分支中
- `async-parallel` - 使用 Promise.all() 处理独立操作
- `async-dependencies` - 使用 better-all 处理部分依赖
- `async-api-routes` - 在 API 路由中尽早启动 Promise，延迟等待
- `async-suspense-boundaries` - 使用 Suspense 流式传输内容

### 2. 打包大小优化 (CRITICAL)

- `bundle-barrel-imports` - 直接导入，避免使用包文件
- `bundle-analyzable-paths` - 优先使用静态可分析的导入和文件系统路径，避免生成宽泛的打包和跟踪
- `bundle-dynamic-imports` - 使用 next/dynamic 处理重量级组件
- `bundle-defer-third-party` - 在 hydration 后加载分析/日志
- `bundle-conditional` - 仅在功能激活时加载模块
- `bundle-preload` - 在鼠标悬停/聚焦时预加载以提升感知速度

### 3. 服务器端性能 (HIGH)

- `server-auth-actions` - 对服务器端操作（如 API 路由）进行身份验证
- `server-cache-react` - 使用 React.cache() 进行请求级去重
- `server-cache-lru` - 使用 LRU 缓存进行跨请求缓存
- `server-dedup-props` - 避免 RSC 属性中的重复序列化
- `server-hoist-static-io` - 将静态 I/O（字体、标志）提升到模块级别
- `server-no-shared-module-state` - 避免 RSC/SSR 中的模块级可变请求状态
- `server-serialization` - 最小化传递给客户端组件的数据
- `server-parallel-fetching` - 重构组件以并行化获取操作
- `server-parallel-nested-fetching` - 在 Promise.all 中为每个项目链式嵌套获取
- `server-after-nonblocking` - 使用 after() 处理非阻塞操作

### 4. 客户端数据获取 (MEDIUM-HIGH)

- `client-swr-dedup` - 使用 SWR 自动去重请求
- `client-event-listeners` - 去重全局事件监听器
- `client-passive-event-listeners` - 使用被动监听器处理滚动
- `client-localstorage-schema` - 版本化并最小化 localStorage 数据

### 5. 重绘优化 (MEDIUM)

- `rerender-defer-reads` - 不要订阅仅在回调中使用的状态
- `rerender-memo` - 将昂贵操作提取到记忆化组件中
- `rerender-memo-with-default-value` - 提升非原始类型的默认属性
- `rerender-dependencies` - 在副作用中使用原始依赖
- `rerender-derived-state` - 订阅派生布尔值，而不是原始值
- `rerender-derived-state-no-effect` - 在渲染时派生状态，而不是在副作用中
- `rerender-functional-setstate` - 使用函数式 setState 处理稳定的回调
- `rerender-lazy-state-init` - 将函数传递给 useState 处理昂贵值
- `rerender-simple-expression-in-memo` - 避免对简单原始类型使用记忆化
- `rerender-split-combined-hooks` - 分离具有独立依赖的钩子
- `rerender-move-effect-to-event` - 将交互逻辑放入事件处理程序
- `rerender-transitions` - 使用 startTransition 处理非紧急更新
- `rerender-use-deferred-value` - 延迟昂贵渲染以保持输入响应
- `rerender-use-ref-transient-values` - 使用 ref 处理频繁的临时值
- `rerender-no-inline-components` - 不要在组件内部定义组件

### 6. 渲染性能 (MEDIUM)

- `rendering-animate-svg-wrapper` - 动画化 div 包装器，而不是 SVG 元素
- `rendering-content-visibility` - 使用 content-visibility 处理长列表
- `rendering-hoist-jsx` - 将静态 JSX 提取到组件外部
- `rendering-svg-precision` - 降低 SVG 坐标精度
- `rendering-hydration-no-flicker` - 使用内联脚本处理客户端独有数据
- `rendering-hydration-suppress-warning` - 忽略预期的不匹配
- `rendering-activity` - 使用 Activity 组件处理显示/隐藏
- `rendering-conditional-render` - 使用三元运算符，而不是 && 处理条件渲染
- `rendering-usetransition-loading` - 优先使用 useTransition 处理加载状态
- `rendering-resource-hints` - 使用 React DOM 资源提示预加载
- `rendering-script-defer-async` - 在 script 标签上使用 defer 或 async

### 7. JavaScript 性能 (LOW-MEDIUM)

- `js-batch-dom-css` - 通过类或 cssText 分组 CSS 变更
- `js-index-maps` - 为重复查找构建 Map
- `js-cache-property-access` - 在循环中缓存对象属性
- `js-cache-function-results` - 在模块级 Map 中缓存函数结果
- `js-cache-storage` - 缓存 localStorage/sessionStorage 读取
- `js-combine-iterations` - 将多个 filter/map 合并为一个循环
- `js-length-check-first` - 在昂贵比较前检查数组长度
- `js-early-exit` - 从函数中提前返回
- `js-hoist-regexp` - 将正则表达式创建提升到循环外部
- `js-min-max-loop` - 使用循环处理最小/最大值，而不是排序
- `js-set-map-lookups` - 使用 Set/Map 处理 O(1) 查找
- `js-tosorted-immutable` - 使用 toSorted() 处理不可变
- `js-flatmap-filter` - 使用 flatMap 在一次遍历中映射和过滤
- `js-request-idle-callback` - 将非关键工作延迟到浏览器空闲时间

### 8. 高级模式 (LOW)

- `advanced-effect-event-deps` - 不要将 useEffectEvent 结果放入副作用依赖中
- `advanced-event-handler-refs` - 将事件处理程序存储在 ref 中
- `advanced-init-once` - 每次应用加载时初始化一次
- `advanced-use-latest` - 使用 useLatest 处理稳定的回调引用

## 如何使用

阅读单个规则文件以获取详细解释和代码示例：

```
rules/async-parallel.md
rules/bundle-barrel-imports.md
```

每个规则文件包含：
- 规则重要性的简要说明
- 带说明的错误代码示例
- 带说明的正确代码示例
- 额外的上下文和参考

## 完整编译文档

获取包含所有规则扩展的完整指南：`AGENTS.md`
