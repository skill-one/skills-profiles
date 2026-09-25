Vue.js 测试最佳实践、模式和常见陷阱。

### 测试
- 为 Vue 3 项目设置测试基础设施 → 查看 [testing-vitest-recommended-for-vue](reference/testing-vitest-recommended-for-vue.md)
- 重构组件内部时测试不断失败 → 查看 [testing-component-blackbox-approach](reference/testing-component-blackbox-approach.md)
- 由于竞态条件测试间歇性失败 → 查看 [testing-async-await-flushpromises](reference/testing-async-await-flushpromises.md)
- 使用生命周期钩子或注入的 Composables 无法测试 → 查看 [testing-composables-helper-wrapper](reference/testing-composables-helper-wrapper.md)
- 测试中遇到 "注入 Symbol(pinia) 未找到" 错误 → 查看 [testing-pinia-store-setup](reference/testing-pinia-store-setup.md)
- 具有异步设置的组件在测试中无法渲染 → 查看 [testing-suspense-async-components](reference/testing-suspense-async-components.md)
- 快照测试尽管功能损坏仍通过 → 查看 [testing-no-snapshot-only](reference/testing-no-snapshot-only.md)
- 为 Vue 应用选择端到端测试框架 → 查看 [testing-e2e-playwright-recommended](reference/testing-e2e-playwright-recommended.md)
- 测试需要验证计算样式或真实 DOM 事件 → 查看 [testing-browser-vs-node-runners](reference/testing-browser-vs-node-runners.md)
- 使用 defineAsyncComponent 创建的组件测试失败 → 查看 [async-component-testing](reference/async-component-testing.md)
- 传送的模态内容在包装器查询中找不到 → 查看 [teleport-testing-complexity](reference/teleport-testing-complexity.md)

## 参考

- [Vue.js 测试指南](https://vuejs.org/guide/scaling-up/testing)
- [Vue Test Utils](https://test-utils.vuejs.org/)
- [Vitest 文档](https://vitest.dev/)
- [Playwright 文档](https://playwright.dev/)
