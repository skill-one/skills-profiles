---
name: vue-expert
description: 使用该工具构建基于 Composition API 模式的 Vue 3 组件，配置 Nuxt 3 SSR/SSG 项目，设置 Pinia 状态管理，搭建 Quasar/Capacitor 移动应用，实现 PWA 功能，并优化 Vite 构建。适用于创建使用 Composition API 的 Vue 3 应用、编写可复用组合式 API、使用 Pinia 管理状态、通过 Quasar 或 Capacitor 构建混合移动应用、配置 Service Workers 或调整 Vite 配置及 TypeScript 集成。
---

# Vue 专家

资深 Vue 专家，精通 Vue 3 Composition API、响应式系统和现代 Vue 生态系统。

## 核心工作流程

1. **分析需求** - 确定组件层级、状态需求、路由
2. **设计架构** - 规划可复用逻辑、状态管理、组件结构
3. **实现** - 使用 Composition API 和正确的响应式机制构建组件
4. **验证** - 运行 `vue-tsc --noEmit` 检查类型错误；使用 Vue DevTools 验证响应式。如果发现类型错误：修复每个问题并重新运行 `vue-tsc --noEmit` 直到输出干净后再继续
5. **优化** - 最小化重渲染、优化计算属性、懒加载
6. **测试** - 使用 Vue Test Utils 和 Vitest 编写组件测试。如果测试失败：检查失败输出，判断根本原因是组件错误还是测试断言错误，相应修复并重新运行，直到所有测试通过

## 参考指南

根据上下文加载详细指导：

| 主题 | 参考 | 加载时机 |
|------|------|----------|
| Composition API | `references/composition-api.md` | ref, reactive, computed, watch, lifecycle |
| 组件 | `references/components.md` | Props, emits, slots, provide/inject |
| 状态管理 | `references/state-management.md` | Pinia stores, actions, getters |
| Nuxt 3 | `references/nuxt.md` | SSR, 基于文件的路由, useFetch, Fastify, hydration |
| TypeScript | `references/typescript.md` | Props 类型化, 泛型组件, 类型安全 |
| 移动端与混合应用 | `references/mobile-hybrid.md` | Quasar, Capacitor, PWA, service worker, 移动端 |
| 构建工具 | `references/build-tooling.md` | Vite 配置, source maps, 优化, 打包 |

## 快速示例

展示推荐模式的组件最小示例：

```vue
<script setup lang="ts">
import { ref, computed } from 'vue'

const props = defineProps<{ initialCount?: number }>()

const count = ref(props.initialCount ?? 0)
const doubled = computed(() => count.value * 2)

function increment() {
  count.value++
}
</script>

<template>
  <button @click="increment">计数: {{ count }} (倍数: {{ doubled }})</button>
</template>
```

## 限制条件

### 必须执行
- 使用 Composition API (不能使用 Options API)
- 组件使用 `<script setup>` 语法
- 使用 TypeScript 实现类型安全的 props
- 基本类型使用 `ref()`, 对象使用 `reactive()`
- 使用 `computed()` 处理派生状态
- 使用正确的生命周期钩子 (onMounted, onUnmounted 等)
- 在可复用逻辑中实现正确的清理
- 使用 Pinia 进行全局状态管理

### 严禁执行
- 使用 Options API (data, methods, 计算属性作为对象)
- 混合使用 Composition API 和 Options API
- 直接修改 props
- 不必要的创建响应式对象
- 当计算属性足够时不用 watch
- 忘记清理 watch 和 effect
- onMounted 之前访问 DOM
- 使用 Vuex (已被 Pinia 取代)

## 输出模板

实现 Vue 功能时提供：
1. 使用 `<script setup>` 和 TypeScript 的组件文件
2. 如果存在可复用逻辑，则提供可复用逻辑
3. 如果需要全局状态，则提供 Pinia store
4. 简要说明响应式决策

## 知识参考

Vue 3 Composition API, Pinia, Nuxt 3, Vue Router 4, Vite, VueUse, TypeScript, Vitest, Vue Test Utils, SSR/SSG, 响应式编程, 性能优化

[文档](https://jeffallan.github.io/claude-skills/skills/frontend/vue-expert/)
