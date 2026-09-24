# Vercel React 最佳实践

由 Vercel 维护的 React 和 Next.js 应用的全面性能优化指南。涵盖 8 个类别的 70 条规则，按影响程度进行优先级排序，以指导自动化重构和代码生成。

## 何时应用

参考以下指南，当：
- 编写新的 React 组件或 Next.js 页面
- 实现（客户端或服务端）数据获取
- 审查代码以排查性能问题
- 重构现有的 React/Next.js 代码
- 优化打包体积或加载时间

## 按优先级排列的规则类别

| Priority | Category | Impact | Prefix |
|----------|----------|--------|--------|
| 1 | 消除瀑布流 | CRITICAL | `async-` |
| 2 | 打包体积优化 | CRITICAL | `bundle-` |
| 3 | 服务端性能 | HIGH | `server-` |
| 4 | 客户端数据获取 | MEDIUM-HIGH | `client-` |
| 5 | 重渲染优化 | MEDIUM | `rerender-` |
| 6 | 渲染性能 | MEDIUM | `rendering-` |
| 7 | JavaScript 性能 | LOW-MEDIUM | `js-` |
| 8 | 高级模式 | LOW | `advanced-` |

## 快速参考

### 1. 消除瀑布流 (CRITICAL)

- `async-cheap-condition-before-await` - 在 await 标志或远程值时，检查廉价同步条件
- `async-defer-await` - 将 await 移动到实际使用的分支中
- `async-parallel` - 使用 Promise.all() 处理独立操作
- `async-dependencies` - 使用 better-all 处理部分依赖
- `async-api-routes` - 在 API 路由中尽早启动 Promise，稍后 await
- `async-suspense-boundaries` - 使用 Suspense 实现内容流式传输

### 2. 打包体积优化 (CRITICAL)

- `bundle-barrel-imports` - 直接导入，避免使用 barrel 文件
- `bundle-analyzable-paths` - 优先使用静态可分析的导入和文件系统路径，以避免过宽的打包体积和调用栈
- `bundle-dynamic-imports` - 为重型组件使用 next/dynamic
- `bundle-defer-third-party` - 在 hydration 后加载分析/日志
- `bundle-conditional` - 仅在功能激活时加载模块
- `bundle-preload` - 在悬停/聚焦时预加载，提升感知速度

### 3. 服务端性能 (HIGH)

- `server-auth-actions` - 以 API 路由的方式认证服务端操作
- `server-cache-react` - 使用 React.cache() 实现按请求去重
- `server-cache-lru` - 使用 LRU 缓存实现跨请求缓存
- `server-dedup-props` - 避免 RSC props 中的重复序列化
- `server-hoist-static-io` - 将静态 I/O（字体、Logo）提升到模块层级
- `server-no-shared-module-state` - 避免 RSC/SSR 中的模块级可变请求状态
- `server-serialization` - 最小化传递给客户端组件的数据
- `server-parallel-fetching` - 重构组件以并行化获取数据
- `server-parallel-nested-fetching` - 使用 Promise.all 按项串联嵌套获取
- `server-after-nonblocking` - 使用 after() 处理非阻塞操作

### 4. 客户端数据获取 (MEDIUM-HIGH)

- `client-swr-dedup` - 使用 SWR 实现自动请求去重
- `client-event-listeners` - 去重全局事件监听器
- `client-passive-event-listeners` - 滚动时使用 passive 监听器
- `client-localstorage-schema` - 对 localStorage 数据进行版本管理并最小化数据量

### 5. 重渲染优化 (MEDIUM)

- `rerender-defer-reads` - 不要订阅仅在回调中使用的状态
- `rerender-memo` - 将昂贵操作提取到记忆化组件中
- `rerender-memo-with-default-value` - 提升默认非基本类型的 props
- `rerender-dependencies` - 在 effect 中使用基本类型依赖
- `rerender-derived-state` - 订阅派生布尔值，而非原始值
- `rerender-derived-state-no-effect` - 在渲染过程中派生状态，而非在 effect 中
- `rerender-functional-setstate` - 为稳定回调使用函数式 setState
- `rerender-lazy-state-init` - 为昂贵值向 useState 传入函数
- `rerender-simple-expression-in-memo` - 避免对简单原始值使用 memo
- `rerender-split-combined-hooks` - 将具有独立依赖的 hook 拆分
- `rerender-move-effect-to-event` - 将交互逻辑放入事件处理函数中
- `rerender-transitions` - 使用 startTransition 处理非紧急更新
- `rerender-use-deferred-value` - 将昂贵的渲染推迟，以保持输入响应灵敏
- `rerender-use-ref-transient-values` - 使用 ref 处理瞬态且频繁的值
- `rerender-no-inline-components` - 不要在内层组件中定义组件

### 6. 渲染性能 (MEDIUM)

- `rendering-animate-svg-wrapper` - 对 div 包装器进行动画，而非 SVG 元素
- `rendering-content-visibility` - 为长列表使用 content-visibility
- `rendering-hoist-jsx` - 将静态 JSX 提取到组件外部
- `rendering-svg-precision` - 减少 SVG 坐标精度
- `rendering-hydration-no-flicker` - 使用内联脚本加载仅客户端的数据
- `rendering-hydration-suppress-warning` - 抑制预期的不匹配警告
- `rendering-activity` - 使用 Activity 组件实现显隐效果
- `rendering-conditional-render` - 使用三元运算符，而非 && 进行条件渲染
- `rendering-usetransition-loading` - 加载状态优先使用 useTransition
- `rendering-resource-hints` - 使用 React DOM 资源提示进行预加载
- `rendering-script-defer-async` - 在 script 标签上使用 defer 或 async

### 7. JavaScript 性能 (LOW-MEDIUM)

- `js-batch-dom-css` - 通过类或 cssText 分组 CSS 变更
- `js-index-maps` - 为重复查找构建 Map
- `js-cache-property-access` - 在循环中缓存对象属性
- `js-cache-function-results` - 将函数结果缓存到模块级别的 Map 中
- `js-cache-storage` - 缓存 localStorage/sessionStorage 的读取结果
- `js-combine-iterations` - 将多个 filter/map 合并到一个循环中
- `js-length-check-first` - 在昂贵的比较之前检查数组长度
- `js-early-exit` - 在函数中提前返回
- `js-hoist-regexp` - 将 RegExp 创建提升到循环外部
- `js-min-max-loop` - 使用循环计算 min/max，而非 sort
- `js-set-map-lookups` - 使用 Set/Map 实现 O(1) 查找
- `js-tosorted-immutable` - 使用 toSorted() 保证不可变性
- `js-flatmap-filter` - 使用 flatMap 在一次遍历中完成映射与过滤
- `js-request-idle-callback` - 将非关键工作推迟到浏览器空闲时间

### 8. 高级模式 (LOW)

- `advanced-effect-event-deps` - 不要将 `useEffectEvent` 的结果放入 effect 依赖中
- `advanced-event-handler-refs` - 将事件处理函数存储在 ref 中
- `advanced-init-once` - 每次应用加载时仅初始化应用一次
- `advanced-use-latest` - 为稳定回调引用使用 useLatest

## 如何使用

阅读单独的规则文件以获取详细解释和代码示例：

```
rules/async-parallel.md
rules/bundle-barrel-imports.md
```

每个规则文件包含：
- 简要说明其重要性
- 附带解释的错误代码示例
- 附带解释的正确代码示例
- 附加上下文与参考资料

## 完整编译文档

获取包含所有规则展开的完整指南：`AGENTS.md`
