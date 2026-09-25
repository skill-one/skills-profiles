Pinia 最佳实践、常见陷阱和状态管理模式。

### 存储库设置
- 启动时出现 "getActivePinia was called" 错误 → 查看 [pinia-no-active-pinia-error](reference/pinia-no-active-pinia-error.md)
- DevTools 或 SSR 中存储库缺少状态 → 查看 [pinia-setup-store-return-all-state](reference/pinia-setup-store-return-all-state.md)

### 响应式
- 存储库解构导致 UI 响应式更新停止 → 查看 [pinia-store-destructuring-breaks-reactivity](reference/pinia-store-destructuring-breaks-reactivity.md)
- 存储库方法在模板调用中丢失上下文 → 查看 [store-method-binding-parentheses](reference/store-method-binding-parentheses.md)

### 状态模式
- 过滤器在刷新时重置或无法共享 → 查看 [state-url-for-ephemeral-filters](reference/state-url-for-ephemeral-filters.md)
- 在没有 DevTools 或约定的情况下构建生产应用 → 查看 [state-use-pinia-for-large-apps](reference/state-use-pinia-for-large-apps.md)
