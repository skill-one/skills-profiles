# React 最佳实践

## 概述

React 性能和质量的路由和优先级指南，包含 9 个类别中的 26 条规则。规则文件包含详细的解释、示例、审查气味和影响指标。

## 应用时机

在以下情况下参考这些指南：

- 编写新的 React 组件
- 实现数据获取
- 审查存在性能问题的代码
- 重构现有的 React 代码
- 优化包大小或加载时间

## 优先级排序指南

规则按影响优先级排序：

| 优先级 | 类别                  | 影响                        |
| ------ | --------------------- | --------------------------- |
| 1      | 消除瀑布流            | CRITICAL                    |
| 2      | 包大小优化            | CRITICAL                    |
| 3      | 客户端数据获取        | MEDIUM-HIGH                 |
| 4      | 重新渲染优化          | MEDIUM                      |
| 5      | 渲染性能              | MEDIUM                      |
| 6      | JavaScript 性能        | LOW-MEDIUM                  |
| 7      | 组件结构              | MEDIUM-HIGH (可维护性)      |
| 8      | 测试                  | MEDIUM-HIGH (正确性)        |
| 9      | 类型安全              | HIGH                        |

## 快速参考

### 关键模式（优先应用）

**消除瀑布流：**

- 使用 `Promise.all()` 处理独立的异步操作 (`async-parallel`)

**减少包大小：**

- 避免使用模块合并文件导入，直接从源导入 (`bundle-barrel-imports`)
- 延迟加载非关键的第三方库 (`bundle-defer-third-party`)

### 中等影响模式

**客户端数据获取：**

- 使用 Tanstack Query 实现自动请求去重 (`client-request-dedupe`)
- 依赖查询参数值为 `undefined` 或 `null`，而不是 `| null` 或伪造的回退值；在调用者处缩小范围以保持钩子严格，或在钩子必须接受可选参数时使用 `skipToken` (`client-request-dedupe`)

**重新渲染优化：**

- 对昂贵的值使用懒加载状态初始化 (`rerender-lazy-state-init`)
- 使用 `startTransition` 处理非紧急更新 (`rerender-transitions`)
- 保持 UI 处理器简单；仅使用 Effect Events 处理触发逻辑 (`rerender-useffect-function-calls`)
- 不要使用 `useEffect` 重置状态；提升判别条件并重新挂载分支 (`rerender-no-useeffect-state-reset`)
- 不要添加 `useMemo` 或 `useCallback`；将记忆化决策留给开发者，并提供性能分析证据 (`rerender-no-usememo-usecallback`)
- 不要在渲染或 `useEffect` 内部调用 `setState`；在渲染时派生或移至中间组件的状态所有权 (`rerender-no-setstate-in-render-or-effect`)

**组件结构：**

- 每个文件一个领域组件/钩子，每个文件一个职责 — 分割臃肿的组件 (`structure-single-responsibility`)
- 保持组件、钩子、函数和工具 API 窄小：将过大的属性、参数和返回对象拆分为组件级别的聚焦单元；将相同的值包装在一个对象中不是解决方案 (`structure-narrow-apis`)
- 使用 PascalCase 组件命名 JSX 返回的辅助函数；保持小写命名非 JSX 值 (`structure-component-naming`)
- 从其他参数派生属性/参数，而不是接受可从另一个参数计算出的值 (`structure-derive-dont-duplicate`)
- 将复杂的派生逻辑提取到命名局部变量和谓词或纯辅助函数中，带早期返回：过大的条件、嵌套三元运算符、计算而非选择的三元运算符（多行分支，或 `as` 类型断言重新断言条件测试的内容）、回退链，以及基于 `let` 的渲染准备都是代码气味，在渲染准备和钩子选项、请求构建器、配置映射和 reducer 中都如此 (`structure-complex-derived-logic`)
- 使用早期 `if` 守卫选择视图，但保持布局包装器在一个地方 — 分支体组件，不要三元运算符或重复外壳 (`structure-early-return-render-branches`)
- 对于固定项集，为每个项编写一个组件，具有明确的属性并拥有其数据和加载 — 不要将配置对象数组映射到组件形状 (`structure-composition-over-config`)

**测试：**

- 驱动真实的 `@mastra/client-js` + React Query 堆栈的 BDD 测试，仅模拟网络；不要 `vi.mock` 我们自己的钩子/服务/auth 网关或 SDK (`testing-bdd-no-mocks`)
- 避免使用类名断言进行视觉行为测试；优先使用计算样式、用户可见行为或浏览器验证，并优先选择无测试而不是仅类名实现的镜像 (`testing-no-classname-assertions`)

**类型安全：**

- 任何地方都不使用 `as` 类型断言 — 生产环境**或测试**；使用真实的类型守卫、查询泛型 (`querySelector<T>`，`getByRole<T>`)、类型化的 fixture 工厂，或在模拟上使用 `implements`。`as const` 是唯一允许的形式。不要用领域类型谓词替换类型断言，该谓词仅检查 `typeof value === 'object'`；调用 `isRecord` 辅助函数或验证使用的字段 (`types-no-type-assertions`)
- 使用 `undefined` 和可选 `?` 表示缺失，而不是 `null`；在边界处转换外部 `null`，并保持叶属性严格，以便调用者拥有缺失和回退渲染 (`types-no-null`)

### 渲染模式

- 动画 SVG 包装器，而不是直接动画 SVG 元素 (`rendering-animate-svg-wrapper`)
- 对长列表使用 `content-visibility: auto` (`rendering-content-visibility`)

### JavaScript 模式

- 使用 Set/Map 进行重复查找 (`js-set-map-lookups`)
- 使用 `toSorted()` 而不是 `sort()` 以实现不可变性 (`js-tosorted-immutable`)
- 数组比较时先进行长度检查 (`js-length-check-first`)

## 参考文献

规则文件是详细指导和示例的权威来源：

- `references/react-best-practices-reference.md` - 包含类别顺序和规则文件路径的规则目录
- `references/rules/` - 按类别组织的规范单个规则文件

实施或审查特定模式时，仅加载相关的规则文件。使用目录选择正确的规则，而无需加载每个示例。

要查找特定模式，在规则目录中执行 grep：

```
grep -l "Promise.all" references/rules/
grep -l "barrel" references/rules/
grep -l "Tanstack" references/rules/
```

## `references/rules/` 中的规则类别

- `async-*` - 消除瀑布流 (1 条规则)
- `bundle-*` - 包大小优化 (2 条规则)
- `client-*` - 客户端数据获取 (1 条规则)
- `rerender-*` - 重新渲染优化 (6 条规则)
- `rendering-*` - DOM 渲染性能 (2 条规则)
- `js-*` - JavaScript 微优化 (3 条规则)
- `types-*` - 类型安全 / 无 `as` 断言和无 `null` 规则 (2 条规则)
- `structure-*` - 组件/钩子/函数/工具结构 (7 条规则)
- `testing-*` - BDD 测试 + 仅模拟网络策略 + 无类名实现镜像断言 (2 条规则)
