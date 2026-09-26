# React 模式

适用于 React 19 + Vite + Cloudflare Workers 项目的性能和组合模式。在编写新组件时用作检查清单，在审计现有代码时用作审查指南，或在感觉缓慢或混乱时用作重构手册。

规则按影响程度排序。先修复 CRITICAL 级别的问题，再处理 MEDIUM 级别的问题。

## 何时应用

- 编写新的 React 组件或页面
- 审查存在性能问题的代码
- 重构具有过多属性或重渲染过多的组件
- 调试“为什么这么慢？”或“为什么这个会重渲染？”
- 构建可重用的组件库
- 合并前的代码审查

## 1. 消除瀑布流（CRITICAL）

可以并行执行但顺序调用的异步调用。性能杀手榜第一位。

| 模式 | 问题 | 解决方案 |
|------|------|----------|
| **按顺序等待** | `const a = await getA(); const b = await getB();` | `const [a, b] = await Promise.all([getA(), getB()]);` |
| **子组件中获取** | 父组件渲染，然后子组件获取，然后孙组件获取 | 将获取操作提升到最高公共祖先，向下传递数据 |
| **Suspense 瀑布** | 多个依次解析的 Suspense 边界 | 一个 Suspense 边界包裹所有异步兄弟组件 |
| **分支前等待** | `const data = await fetch(); if (condition) { use(data); }` | 将等待移到分支内部——不要获取可能不需要的数据 |
| **导入后渲染** | `const Component = await import('./Heavy'); return <Component />` | 使用 `React.lazy()` + `<Suspense>` — 立即渲染回退内容 |

**如何发现它们**：在组件中搜索 `await`。每个 `await` 都可能是瀑布流。如果两个 `await` 是独立的，它们应该是并行的。

## 2. 打包大小（CRITICAL）

用户下载的每一 KB 都是他们需要等待的每一 KB。

| 模式 | 问题 | 解决方案 |
|------|------|----------|
| **共用导入** | `import { Button } from '@/components'` 拉取整个共用文件 | `import { Button } from '@/components/ui/button'` — 直接导入 |
| **无代码拆分** | 重型组件在每一页都加载 | `React.lazy(() => import('./HeavyComponent'))` + `<Suspense>` |
| **第三方预加载** | 分析/跟踪在应用程序渲染前加载 | 在水合后加载：`useEffect(() => { import('./analytics') }, [])` |
| **完整库导入** | `import _ from 'lodash'` (70KB) | `import debounce from 'lodash/debounce'` (1KB) |
| **Lucide 树摇** | `import * as Icons from 'lucide-react'` (所有图标) | 显式映射：`import { Home, Settings } from 'lucide-react'` |
| **重复 React** | 库捆绑了自己的 React → "Cannot read properties of null" | `resolve.dedupe: ['react', 'react-dom']` 在 vite.config.ts 中 |

**如何发现它们**：`npx vite-bundle-visualizer` — 显示你的打包内容。

## 3. 组合架构（HIGH）

组件的结构比如何优化它们更重要。

| 模式 | 问题 | 解决方案 |
|------|------|----------|
| **布尔属性爆炸** | `<Card isCompact isClickable showBorder hasIcon isLoading>` | 显式变体：`<CompactCard>`, `<ClickableCard>` |
| **复合组件** | 具有 15 个属性的复杂组件 | 分割为 `<Dialog>`, `<Dialog.Trigger>`, `<Dialog.Content>` 并使用共享上下文 |
| **renderX 属性** | `<Layout renderSidebar={...} renderHeader={...} renderFooter={...}>` | 使用 children + 命名插槽：`<Layout><Sidebar /><Header /></Layout>` |
| **提升状态** | 兄弟组件无法共享状态 | 将状态移到父组件或上下文提供者 |
| **提供者实现** | 消费者代码知道状态管理的内部实现 | 提供者暴露接口 `{ state, actions, meta }` — 隐藏实现细节 |
| **内联组件** | `function Parent() { function Child() { ... } return <Child /> }` | 在父组件外定义 Child — 内联组件在每次渲染时都会重新挂载 |

**测试**：如果组件有超过 5 个布尔属性，它需要组合，而不是更多属性。

## 4. 防止重渲染（MEDIUM）

并非所有重渲染都是坏的。只修复导致可见卡顿或浪费计算的重渲染。

| 模式 | 问题 | 解决方案 |
|------|------|----------|
| **默认对象/数组属性** | `function Foo({ items = [] })` → 每次渲染都创建新的数组引用 | 提升：`const DEFAULT = []; function Foo({ items = DEFAULT })` |
| **效果中的派生状态** | `useEffect(() => setFiltered(items.filter(...)), [items])` | 在渲染时派生：`const filtered = useMemo(() => items.filter(...), [items])` |
| **对象依赖** | `useEffect(() => {...}, [config])` 如果 config 是 `{}` 每次渲染都会触发 | 使用原始依赖：`useEffect(() => {...}, [config.id, config.type])` |
| **订阅未使用的状态** | 组件读取 `{ user, theme, settings }` 但只使用 `user` | 分割上下文或使用选择器：`useSyncExternalStore` |
| **用于瞬时值的状体** | `const [mouseX, setMouseX] = useState(0)` 在鼠标移动时 | 使用 `useRef` 对于频繁变化但不需要重渲染的值 |
| **内联回调属性** | `<Button onClick={() => doThing(id)} />` — 每次渲染都创建新的函数 | `useCallback` 或函数式 setState：`<Button onClick={handleClick} />` |

**如何发现它们**：React DevTools Profiler → “为什么这个会渲染？” 或 `<React.StrictMode>` 在开发中的双倍渲染。

## 5. React 19 特定（MEDIUM）

React 19 中更改或新增的模式。

| 模式 | 旧版 (React 18) | 新版 (React 19) |
|------|---------------|----------------|
| **表单状态** | `useFormState` | `useActionState` — 重命名 |
| **引用转发** | `forwardRef((props, ref) => ...)` | `function Component({ ref, ...props })` — 引用是一个普通属性 |
| **上下文** | `useContext(MyContext)` | `use(MyContext)` — 在条件语句和循环中有效 |
| **挂起 UI** | 手动加载状态 | `useTransition` + `startTransition` 用于非紧急更新 |
| **路由级懒加载** | 仅与 `createBrowserRouter` 一起工作 | 仍然有效 — `<Route lazy={...}>` 在 `<BrowserRouter>` 中被静默忽略 |
| **乐观更新** | 手动状态管理 | `useOptimistic` 钩子 |
| **元数据** | Helmet 或手动 `<head>` 管理 | `<title>`, `<meta>`, `<link>` 在组件 JSX 中 — 自动提升到 `<head>` |

## 6. 渲染性能（MEDIUM）

| 模式 | 问题 | 解决方案 |
|------|------|----------|
| **加载时的布局偏移** | 异步数据到达时内容跳跃 | 匹配最终布局尺寸的骨架屏 |
| **直接动画 SVG** | 卡顿的 SVG 动画 | 包裹在 `<div>` 中，而不是动画 div |
| **大量列表渲染** | 表格/列表中有 1000+ 项 | `@tanstack/react-virtual` 用于虚拟化渲染 |
| **content-visibility** | 长滚动内容预先渲染所有内容 | 在离屏部分上使用 `content-visibility: auto` |
| **使用 && 的条件渲染** | `{count && <Items />}` 当 count 为 0 时渲染 `0` | 使用三元运算符：`{count > 0 ? <Items /> : null}` |

## 7. 数据获取（MEDIUM）

| 模式 | 问题 | 解决方案 |
|------|------|----------|
| **无去重** | 3 个组件获取相同数据 | TanStack Query 或 SWR — 自动去重 + 缓存 |
| **挂载时获取** | `useEffect(() => { fetch(...) }, [])` — 瀑布流，无缓存，无去重 | TanStack Query: `useQuery({ queryKey: ['users'], queryFn: fetchUsers })` |
| **无乐观更新** | 用户点击保存，等待 2 秒，然后看到变化 | `useMutation` 与 `onMutate` 用于即时视觉反馈 |
| **过时的闭包** | `setInterval` 捕获过时的状态 | 使用 `useRef` 对于频繁变化但不需要重渲染的值 |
| **无清理的轮询** | `useEffect` 中的 `setInterval` 而没有 `clearInterval` | 返回清理：`useEffect(() => { const id = setInterval(...); return () => clearInterval(id); })` |

## 8. Vite + Cloudflare 特定（MEDIUM）

| 模式 | 问题 | 解决方案 |
|------|------|----------|
| **Node 脚本中的 `import.meta.env`** | 未定义 — 仅在 Vite 处理的文件中工作 | 使用 vite 的 `loadEnv()` |
| **React 重复实例** | 库捆绑了自己的 React | `resolve.dedupe` + `optimizeDeps.include` 在 vite.config.ts 中 |
| **Radix Select 空字符串** | `<SelectItem value="">` 抛出异常 | 使用哨兵：`<SelectItem value="__any__">` |
| **React Hook Form null** | `{...field}` 将 null 传递给 Input | 手动展开：`value={field.value ?? ''}` |
| **边缘环境变量** | `process.env` 在 Workers 中不存在 | 使用 `c.env` (Hono 上下文) 或 `import.meta.env` (Vite 构建时) |

## 作为审查检查清单使用

在审查代码时，对每个 PR 逐一检查 1-3 类（CRITICAL + HIGH）。4-8 类仅在性能成为问题时检查。

```
/react-patterns [文件或组件路径]
```

阅读文件，按优先级顺序检查规则，报告发现的问题作为：
```
文件:行 — [规则] 问题描述
```
