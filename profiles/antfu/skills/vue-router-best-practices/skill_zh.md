Vue Router 最佳实践、常见陷阱和导航模式。

### 导航守卫
- 在相同路由之间使用不同参数导航 → 查看 [router-beforeenter-no-param-trigger](reference/router-beforeenter-no-param-trigger.md)
- 在 `beforeRouteEnter` 守卫中访问组件实例 → 查看 [router-beforerouteenter-no-this](reference/router-beforerouteenter-no-this.md)
- 导航守卫在未等待 API 调用时 → 查看 [router-guard-async-await-pattern](reference/router-guard-async-await-pattern.md)
- 用户陷入无限重定向循环 → 查看 [router-navigation-guard-infinite-loop](reference/router-navigation-guard-infinite-loop.md)
- 使用已弃用的 `next()` 函数的导航守卫 → 查看 [router-navigation-guard-next-deprecated](reference/router-navigation-guard-next-deprecated.md)

### 路由生命周期
- 在相同路由之间导航时出现陈旧数据 → 查看 [router-param-change-no-lifecycle](reference/router-param-change-no-lifecycle.md)
- 组件卸载后事件监听器仍然存在 → 查看 [router-simple-routing-cleanup](reference/router-simple-routing-cleanup.md)

### 配置
- 构建 production 单页面应用程序 → 查看 [router-use-vue-router-for-production](reference/router-use-vue-router-for-production.md)
