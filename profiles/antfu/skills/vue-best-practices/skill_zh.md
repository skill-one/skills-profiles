# Vue 最佳实践工作流

将此技能作为指令集使用。除非用户明确要求不同顺序，否则请按顺序遵循此工作流。

## 核心原则
- **保持状态可预测：**单一事实来源，派生其他所有内容。
- **使数据流显式化：**大多数情况下，属性向下传递，事件向上触发。
- **优先使用小型、专注的组件：**更易于测试、重用和维护。
- **避免不必要的重新渲染：**明智地使用计算属性和观察者。
- **可读性很重要：**编写清晰、自文档化的代码。

## 1) 编码前确认架构（必需）

- 默认技术栈：Vue 3 + Composition API + `<script setup lang="ts">`。
- 如果项目明确使用 Options API，如果可用，则加载 `vue-options-api-best-practices` 技能。
- 如果项目明确使用 JSX，如果可用，则加载 `vue-jsx-best-practices` 技能。

### 1.1 必读的核心参考（必需）

- 在实现任何 Vue 任务之前，请确保阅读并应用这些核心参考：
  - `references/reactivity.md`
  - `references/sfc.md`
  - `references/component-data-flow.md`
  - `references/composables.md`
- 在整个任务期间，将这些参考保留在活跃的工作上下文中，而不仅仅是在出现特定问题时。

### 1.2 编码前规划组件边界（必需）

在实现任何非平凡功能之前，创建一个简短的组件图。

- 用一句话定义每个组件的单一职责。
- 默认情况下，将入口/根和路由级视图组件作为组合表面。
- 除非任务有意作为一个微型的单文件演示，否则将功能 UI 和功能逻辑从入口/根/视图组件中移出。
- 在图中为每个子组件定义 props/emits 合约。
- 添加多个组件时，优先选择功能文件夹布局（`components/<feature>/...`，`composables/use<Feature>.ts`）。

## 2) 应用基本的 Vue 基础（必需）

这些都是基本、必须掌握的基础知识。在 `1.1` 节中已加载的核心参考中，在所有 Vue 任务中应用它们。

### Reactivity

- 来自 `1.1` 的必读参考：[reactivity](references/reactivity.md)
- 保持源状态最小（`ref`/`reactive`），尽可能使用 `computed` 派生其他内容。
- 如有必要，使用观察者处理副作用。
- 避免在模板中重新计算昂贵的逻辑。

### SFC 结构和模板安全性

- 来自 `1.1` 的必读参考：[sfc](references/sfc.md)
- 保持 SFC 部分按此顺序：`<script>` → `<template>` → `<style>`。
- 保持 SFC 职责集中；拆分大型组件。
- 保持模板声明式；将分支/派生移至脚本。
- 应用 Vue 模板安全性规则（`v-html`，列表渲染，条件渲染选择）。

### 保持组件专注

当组件具有**多个明确的职责**时（例如，数据编排 + UI，或多个独立的 UI 部分）拆分组件。

- 优先选择**更小的组件 + 可组合性**而不是一个“巨型组件”
- 将**UI 部分**移入子组件（输入 props，输出事件）。
- 将**状态/副作用**移入可组合性（`useXxx()`）。

应用客观拆分触发器。如果**任何**条件为真，则拆分组件：

- 它同时拥有编排/状态和多个部分的大量展示性标记。
- 它有 3+ 个独立的 UI 部分（例如：表单，过滤器，列表，页脚/状态）。
- 模板块重复或可能变得可重用（项目行，卡片，列表条目）。

入口/根和路由视图规则：

- 保持入口/根和路由视图组件精简：应用壳/布局，提供器接线，功能组合。
- 当这些功能包含独立部分时，不要在入口/根/视图组件中放置完整的功能实现。
- 对于 CRUD/列表功能（待办事项，表格，目录，收件箱），至少拆分为：
  - 功能容器组件
  - 输入/表单组件
  - 列表（和/或项目）组件
  - 页脚/操作或过滤器/状态组件
- 仅允许非常小的抛弃型演示使用单文件实现；如果选择，请明确说明为什么拆分是不必要的。

### 组件数据流

- 来自 `1.1` 的必读参考：[component-data-flow](references/component-data-flow.md)
- 使用属性向下传递，事件向上触发作为主要模型。
- 仅在真正的双向组件合约中使用 `v-model`。
- 仅在深度树依赖或共享上下文中使用 provide/inject。
- 使用 `defineProps`，`defineEmits` 和 `InjectionKey`（如有必要）保持合约显式和类型化。

### Composables

- 来自 `1.1` 的必读参考：[composables](references/composables.md)
- 当逻辑可重用、有状态或副作用密集时，将其提取到可组合性中。
- 保持可组合性 API 小型、类型化且可预测。
- 将功能逻辑与展示性组件分离。

## 3) 仅在需求要求时考虑可选功能

### 3.1 标准可选功能

默认情况下不要添加这些。仅在需求存在时加载匹配的参考。

- 插槽：父组件需要控制子组件内容/布局 -> [component-slots](references/component-slots.md)
- 跌代属性：包装器/基础组件必须安全地转发 attrs/事件 -> [component-fallthrough-attrs](references/component-fallthrough-attrs.md)
- 内置组件 `<KeepAlive>` 用于有状态视图缓存 -> [component-keep-alive](references/component-keep-alive.md)
- 内置组件 `<Teleport>` 用于覆盖/端口 -> [component-teleport](references/component-teleport.md)
- 内置组件 `<Suspense>` 用于异步子树回退边界 -> [component-suspense](references/component-suspense.md)
- 动画相关功能：选择与所需运动行为最匹配的最简单方法。
  - 内置组件 `<Transition>` 用于进入/离开效果 -> [transition](references/component-transition.md)
  - 内置组件 `<TransitionGroup>` 用于动画列表变更 -> [transition-group](references/component-transition-group.md)
  - 基于类的动画用于非进入/离开效果 -> [animation-class-based-technique](references/animation-class-based-technique.md)
  - 基于状态的动画用于用户输入驱动的动画 -> [animation-state-driven-technique](references/animation-state-driven-technique.md)

### 3.2 较少使用的可选功能

仅在存在明确的产品或技术需求时使用这些。

- 指令：行为是 DOM 特定的，不适合可组合性/组件 -> [directives](references/directives.md)
- 异步组件：重型/很少使用的 UI 应该懒加载 -> [component-async](references/component-async.md)
- 仅当模板无法表达需求时使用渲染函数 -> [render-functions](references/render-functions.md)
- 插件：当行为必须全局安装时 -> [plugins](references/plugins.md)
- 状态管理模式：应用范围共享状态跨越功能边界 -> [state-management](references/state-management.md)

## 4) 行为正确后再进行性能优化

性能工作是一个功能后处理步骤。在核心行为实现并验证之前不要进行优化。

- 大型列表渲染瓶颈 -> [perf-virtualize-large-lists](references/perf-virtualize-large-lists.md)
- 静态子树不必要地重新渲染 -> [perf-v-once-v-memo-directives](references/perf-v-once-v-memo-directives.md)
- 热路径中过度抽象 -> [perf-avoid-component-abstraction-in-lists](references/perf-avoid-component-abstraction-in-lists.md)
- 过于频繁触发昂贵的更新 -> [updated-hook-performance](references/updated-hook-performance.md)

## 5) 完成前的最终自检

- 核心行为工作且符合需求。
- 所有必读参考都已阅读并应用。
- Reactivity 模型最小且可预测。
- 遵循 SFC 结构和模板规则。
- 组件专注且结构良好，需要时拆分。
- 入口/根和路由视图组件保持为组合表面，除非存在明确的单文件演示例外。
- 组件拆分决策明确且有说服力（职责边界清晰）。
- 数据流合约显式且类型化。
- 仅在重用/复杂性证明它们时使用可组合性。
- 如适用，将状态/副作用移入可组合性
- 仅在需求要求时使用可选功能。
- 仅在功能完成后才应用性能更改。
