# Vercel React 最佳实践

由 Vercel 维护的 React 和 Next.js 应用程序性能优化综合指南。包含 8 个类别中的 70 条规则，按影响优先级排序，用于指导自动化重构和代码生成。

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
- `async-parallel` - 使用 Promise.all() 进行独立操作
- `async-dependencies` - 使用 better-all 进行部分依赖
- `async-api-routes` - 在 API 路由中尽早开始承诺，延迟等待
- `async-suspense-boundaries` - 使用 Suspense 流式传输内容

### 2. 打包大小优化 (CRITICAL)

- `bundle-barrel-imports` - 直接导入，避免使用包文件
- `bundle-analyzable-paths` - 优先使用静态可分析的导入和文件系统路径，避免广泛的打包和跟踪
- `bundle-dynamic-imports` - 使用 next/dynamic 进行重组件
- `bundle-defer-third-party` - 在 hydration 后加载分析/日志
- `bundle-conditional` - 仅在功能激活时加载模块
- `bundle-preload` - 在悬停/聚焦时预加载以提升感知速度

### 3. 服务器端性能 (HIGH)

- `server-auth-actions` - 认证服务器操作，如 API 路由
- `server-cache-react` - 使用 React.cache() 进行请求级重复
- `server-cache-lru` - 使用 LRU 缓存进行跨请求缓存
- `server-dedup-props` - 避免 RSC 属性中的重复序列化
- `server-hoist-static-io` - 将静态 I/O（字体、标志）提升到模块级别
- `server-no-shared-module-state` - 避免 RSC/SSR 中的模块级可变请求状态
- `server-serialization` - 最小化传递给客户端组件的数据
- `server-parallel-fetching` - 重构组件以并行化获取
- `server-parallel-nested-fetching` - 在 Promise.all 中按项目链式嵌套获取
- `server-after-nonblocking` - 使用 after() 进行非阻塞操作

### 4. 客户端数据获取 (MEDIUM-HIGH)

- `client-swr-dedup` - 使用 SWR 进行自动请求重复
- `client-event-listeners` - 重复全局事件监听器
- `client-passive-event-listeners` - 使用被动监听器进行滚动
- `client-localstorage-schema` - 版本和最小化 localStorage 数据

### 5. 重绘优化 (MEDIUM)

- `rerender-defer-reads` - 不要订阅仅在回调中使用的状态
- `rerender-memo` - 将昂贵的工作提取到记忆化组件中
- `rerender-memo-with-default-value` - 提升非原始类型的默认属性
- `rerender-dependencies` - 在效果中使用原始依赖
- `rerender-derived-state` - 订阅派生布尔值，而不是原始值
- `rerender-derived-state-no-effect` - 在渲染期间派生状态，而不是在效果中
- `rerender-functional-setstate` - 使用函数式 setState 进行稳定的回调
- `rerender-lazy-state-init` - 将函数传递给 useState 以获取昂贵值
- `rerender-simple-expression-in-memo` - 避免为简单原始类型使用记忆
- `rerender-split-combined-hooks` - 分割具有独立依赖的钩子
- `rerender-move-effect-to-event` - 将交互逻辑放在事件处理程序中
- `rerender-transitions` - 使用 startTransition 进行非紧急更新
- `rerender-use-deferred-value` - 将昂贵的渲染延迟以保持输入响应
- `rerender-use-ref-transient-values` - 使用 ref 存储临时频繁值
- `rerender-no-inline-components` - 不要在组件内部定义组件

### 6. 渲染性能 (MEDIUM)

- `rendering-animate-svg-wrapper` - 动画 div 包装器，而不是 SVG 元素
- `rendering-content-visibility` - 使用 content-visibility 进行长列表
- `rendering-hoist-jsx` - 将静态 JSX 提取到组件外部
- `rendering-svg-precision` - 减少SVG坐标精度
- `rendering-hydration-no-flicker` - 使用内联脚本进行客户端数据
- `rendering-hydration-suppress-warning` - 抑制预期的不匹配
- `rendering-activity` - 使用 Activity 组件进行显示/隐藏
- `rendering-conditional-render` - 使用三元运算符，而不是 && 进行条件渲染
- `rendering-usetransition-loading` - 优先使用 useTransition 进行加载状态
- `rendering-resource-hints` - 使用 React DOM 资源提示进行预加载
- `rendering-script-defer-async` - 在 script 标签上使用 defer 或 async

### 7. JavaScript 性能 (LOW-MEDIUM)

- `js-batch-dom-css` - 通过类或 cssText 组合 CSS 变更
- `js-index-maps` - 为重复查找构建 Map
- `js-cache-property-access` - 在循环中缓存对象属性
- `js-cache-function-results` - 在模块级 Map 中缓存函数结果
- `js-cache-storage` - 缓存 localStorage/sessionStorage 读取
- `js-combine-iterations` - 将多个 filter/map 合并为一个循环
- `js-length-check-first` - 在昂贵比较之前检查数组长度
- `js-early-exit` - 从函数中提前返回
- `js-hoist-regexp` - 将正则表达式创建提升到循环外部
- `js-min-max-loop` - 使用循环而不是排序进行 min/max
- `js-set-map-lookups` - 使用 Set/Map 进行 O(1) 查找
- `js-tosorted-immutable` - 使用 toSorted() 进行不可变性
- `js-flatmap-filter` - 使用 flatMap 在一次遍历中映射和过滤
- `js-request-idle-callback` - 将非关键工作延迟到浏览器空闲时间

### 8. 高级模式 (LOW)

- `advanced-effect-event-deps` - 不要将 useEffectEvent 结果放在效果依赖中
- `advanced-event-handler-refs` - 将事件处理程序存储在 ref 中
- `advanced-init-once` - 每次应用加载初始化一次
- `advanced-use-latest` - useLatest 用于稳定的回调引用

## 如何使用

阅读单个规则文件以获取详细解释和代码示例：

```
rules/async-parallel.md
rules/bundle-barrel-imports.md
```

每个规则文件包含：
- 为什么它重要的简要解释
- 带有解释的不正确代码示例
- 带有解释的正确代码示例
- 额外的上下文和参考

## 完整编译文档

包含所有规则扩展的完整指南：`AGENTS.md`
