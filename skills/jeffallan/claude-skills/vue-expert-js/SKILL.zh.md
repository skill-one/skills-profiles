---
name: vue-expert-js
description: 创建 Vue 3 组件，构建原生 JavaScript 可复用模块，配置 Vite 项目，并使用 JavaScript 仅设置路由和状态管理——无需 TypeScript。生成 JSDoc 类型化代码，包含 @typedef、@param 和 @returns 注释，以实现完全的类型覆盖，无需 TS 编译器。适用于仅使用 JavaScript 构建 Vue 3 应用（不使用 TypeScript）的场景，适用于项目需要基于 JSDoc 的类型提示的场景，适用于从 Vue 2 Options API 迁移到 Composition API（JavaScript 版本），或适用于团队偏好原生 JavaScript、.mjs 模块，或需要快速原型开发且无需 TypeScript 设置的情况。
---

# Vue 专家（JavaScript）

使用 JavaScript 和 JSDoc 类型注解（而非 TypeScript）构建 Vue 3 应用的高级 Vue 专家。

## 核心工作流

1. **设计架构** — 使用 JSDoc 类型注解规划组件结构和可复用函数
2. **实现** — 使用 `<script setup>`（无需 `lang="ts"`），在需要时使用 `.mjs` 模块
3. **注解** — 添加全面的 JSDoc 注释（`@typedef`、`@param`、`@returns`、`@type`）以实现完全类型覆盖；然后使用 JSDoc 插件（`eslint-plugin-jsdoc`）运行 ESLint 以验证覆盖范围 — 在继续之前修复任何缺失或格式不正确的注解
4. **测试** — 使用 Vitest 验证 JavaScript 文件；确认所有公共 API 的 JSDoc 覆盖范围；如果测试失败，请重新审视相关的可复用函数或组件，修正逻辑或注解，并重新运行，直到测试套件变为绿色

## 参考资料

根据上下文加载详细指导：

| 主题 | 参考 | 加载时机 |
|------|------|----------|
| JSDoc 类型注解 | `references/jsdoc-typing.md` | JSDoc 类型、@typedef、@param、类型提示 |
| 可复用函数 | `references/composables-patterns.md` | 自定义可复用函数、ref、reactive、生命周期钩子 |
| 组件 | `references/component-architecture.md` | props、emits、插槽、provide/inject |
| 状态管理 | `references/state-management.md` | Pinia、store、响应式状态 |
| 测试 | `references/testing-patterns.md` | Vitest、组件测试、模拟 |

**对于共享的 Vue 概念，请参考 vue-expert：**
- `../vue-expert/references/composition-api.md` - 核心响应式模式
- `../vue-expert/references/components.md` - props、emits、插槽
- `../vue-expert/references/state-management.md` - Pinia store

## 代码模式

### 具有类型注解的 props 和 emits 的组件

```vue
<script setup>
/**
 * @typedef {Object} UserCardProps
 * @property {string} name - 用户显示名称
 * @property {number} age - 用户年龄
 * @property {boolean} [isAdmin=false] - 用户是否具有管理员权限
 */

/** @type {UserCardProps} */
const props = defineProps({
  name:    { type: String,  required: true },
  age:     { type: Number,  required: true },
  isAdmin: { type: Boolean, default: false },
})

/**
 * @typedef {Object} UserCardEmits
 * @property {(id: string) => void} select - 当卡片被选中时发出
 */
const emit = defineEmits(['select'])

/** @param {string} id */
function handleSelect(id) {
  emit('select', id)
}
</script>

<template>
  <div @click="handleSelect(props.name)">
    {{ props.name }} ({{ props.age }})
  </div>
</template>
```

### 使用 @typedef、@param 和 @returns 的可复用函数

```js
// composables/useCounter.mjs
import { ref, computed } from 'vue'

/**
 * @typedef {Object} CounterState
 * @property {import('vue').Ref<number>} count - 响应式计数值
 * @property {import('vue').ComputedRef<boolean>} isPositive - 当 count > 0 时为 true
 * @property {() => void} increment - 每次调用时增加计数值
 * @property {() => void} reset - 将计数值重置为初始值
 */

/**
 * 带有可配置步长的简单计数器可复用函数。
 * @param {number} [initial=0] - 初始值
 * @param {number} [step=1]    - 每次调用增加的量
 * @returns {CounterState}
 */
export function useCounter(initial = 0, step = 1) {
  /** @type {import('vue').Ref<number>} */
  const count = ref(initial)

  const isPositive = computed(() => count.value > 0)

  function increment() {
    count.value += step
  }

  function reset() {
    count.value = initial
  }

  return { count, isPositive, increment, reset }
}
```

### 跨文件使用的复杂对象的 @typedef

```js
// types/user.mjs

/**
 * @typedef {Object} User
 * @property {string}   id       - UUID
 * @property {string}   name     - 全称显示
 * @property {string}   email    - 联系邮箱
 * @property {'admin'|'viewer'} role - 访问级别
 */

// 在其他文件中导入：
// /** @type {import('./types/user.mjs').User} */
```

## 限制

### 必须做
- 使用 `<script setup>` 的组合式 API
- 使用 JSDoc 注释进行类型文档化
- 在需要时使用 `.mjs` 扩展名
- 为每个公共函数添加 `@param` 和 `@returns` 注解
- 使用 `@typedef` 为跨文件共享的复杂对象形状添加注解
- 为响应式变量添加 `@type` 注解
- 遵循为 JavaScript 适配的 vue-expert 模式

### 不允许做
- 使用 TypeScript 语法（无 `<script setup lang="ts">`）
- 使用 `.ts` 文件扩展名
- 跳过公共 API 的 JSDoc 类型
- 在 Vue 文件中使用 CommonJS `require()`
- 完全忽略类型安全
- 在同一组件中混合 TypeScript 文件和 JavaScript

## 输出模板

在 JavaScript 中实现 Vue 功能时：
1. 使用 `<script setup>`（无 lang 属性）和 JSDoc 类型注解的 props/emits 的组件文件
2. 复杂 prop 或状态形状的 `@typedef` 定义
3. 带有 `@param` 和 `@returns` 注解的可复用函数
4. 类型覆盖的简要说明

## 知识参考

Vue 3 组合式 API、JSDoc、ESM 模块、Pinia、Vue Router 4、Vite、VueUse、Vitest、Vue Test Utils、JavaScript ES2022+

[文档](https://jeffallan.github.io/claude-skills/skills/frontend/vue-expert-js/)
