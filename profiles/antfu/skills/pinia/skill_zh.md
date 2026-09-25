# Pinia

Pinia 是 Vue 官方的状态管理库，旨在直观且类型安全。它支持 Options API 和 Composition API 两种风格，具有一流的 TypeScript 支持和 devtools 集成。

> 本技能基于 Pinia v3.0.4，生成于 2026-01-28。

## 核心参考

| 主题 | 描述 | 参考 |
|------|------|------|
| Stores | 定义 store、状态、获取器、动作、storeToRefs、订阅 | [core-stores](references/core-stores.md) |

## 功能

### 扩展性

| 主题 | 描述 | 参考 |
|------|------|------|
| Plugins | 使用自定义属性、状态和行为扩展 store | [features-plugins](references/features-plugins.md) |

### 组合性

| 主题 | 描述 | 参考 |
|------|------|------|
| Composables | 在 store 中使用 Vue 组合式 API (VueUse 等) | [features-composables](references/features-composables.md) |
| Composing Stores | store 之间的通信，避免循环依赖 | [features-composing-stores](references/features-composing-stores.md) |

## 最佳实践

| 主题 | 描述 | 参考 |
|------|------|------|
| Testing | 使用 @pinia/testing 进行单元测试、模拟、存根 | [best-practices-testing](references/best-practices-testing.md) |
| Outside Components | 在导航守卫、插件、中间件中使用 store | [best-practices-outside-component](references/best-practices-outside-component.md) |

## 高级

| 主题 | 描述 | 参考 |
|------|------|------|
| SSR | 服务器端渲染、状态水合 | [advanced-ssr](references/advanced-ssr.md) |
| Nuxt | Nuxt 集成、自动导入、SSR 最佳实践 | [advanced-nuxt](references/advanced-nuxt.md) |
| HMR | 开发中的热模块替换 | [advanced-hmr](references/advanced-hmr.md) |

## 关键建议

- **对于复杂逻辑、组合式 API 和观察者，优先使用 Setup Store**
- **解构状态/获取器时使用 `storeToRefs()` 以保持响应性**
- **可以直接解构动作 - 它们已绑定到 store**
- **在函数内部调用 store，而不是模块作用域，尤其是在 SSR 中**
- **为每个 store 添加 HMR 支持，以获得更好的开发体验**
- **使用 `@pinia/testing` 进行带模拟 store 的组件测试**
