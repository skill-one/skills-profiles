Vue.js 选项 API 最佳实践、TypeScript 集成以及常见陷阱。

### TypeScript
- 需要对组件属性启用 TypeScript 类型推断 → 查看 [ts-options-api-use-definecomponent](reference/ts-options-api-use-definecomponent.md)
- 在此上下文中为 Options API 启用类型安全 → 查看 [ts-strict-mode-options-api](reference/ts-strict-mode-options-api.md)
- 使用旧版 TypeScript 与 prop 验证器 → 查看 [ts-options-api-arrow-functions-validators](reference/ts-options-api-arrow-functions-validators.md)
- 事件处理器参数需要适当的类型安全 → 查看 [ts-options-api-type-event-handlers](reference/ts-options-api-type-event-handlers.md)
- 需要用接口类型化对象或数组 prop → 查看 [ts-options-api-proptype-complex-types](reference/ts-options-api-proptype-complex-types.md)
- 注入的属性完全缺少 TypeScript 类型 → 查看 [ts-options-api-provide-inject-limitations](reference/ts-options-api-provide-inject-limitations.md)
- 复杂的计算属性缺乏清晰的类型文档 → 查看 [ts-options-api-computed-return-types](reference/ts-options-api-computed-return-types.md)

### 方法与生命周期
- 方法未绑定到组件实例上下文 → 查看 [no-arrow-functions-in-methods](reference/no-arrow-functions-in-methods.md)
- 生命周期钩子失去对组件数据的访问 → 查看 [no-arrow-functions-in-lifecycle-hooks](reference/no-arrow-functions-in-lifecycle-hooks.md)
- 被缓动的函数在组件实例之间共享状态 → 查看 [stateful-methods-lifecycle](reference/stateful-methods-lifecycle.md)
