# EAS Observe

EAS Observe 用于跟踪生产环境中 Expo 应用的启动、导航和自定义事件性能。

> **权威来源:** https://docs.expo.dev/eas/observe/ — 当 API 细节至关重要时，尤其是入门指南、配置、集成和指标参考时，请始终查阅官方文档。EAS Observe 正在不断发展；本技能的参考文档会力求保持准确，但可能存在与文档更新不同步的情况。

## 应该阅读哪个参考文件

`./references/` 中的三个参考文件涵盖了人们通常需要这个技能的三种情况：

- **将 EAS Observe 添加到项目中** → [`./references/setup.md`](./references/setup.md)。安装、包裹根布局（SDK 55 上为 `AppMetricsRoot`，SDK 56 及以上版本上为 `ObserveRoot`），调用 `markInteractive()`（SDK 55 上为全局调用，SDK 56 及以上版本上通过 `useObserve()` 钩子调用），通过 Expo Router / React Navigation 集成实现可选的每路由导航指标，以及通过 `Observe.logEvent`（SDK 56 及以上版本）记录用户定义的事件。
- **从终端查询指标** → [`./references/queries.md`](./references/queries.md)。五个 `eas observe:*` 命令——`metrics-summary`、`metrics`、`routes`、`events`、`versions`——以及它们的标志、表格布局、JSON 结构和常见工作流。
- **阅读仪表板或 CLI 输出** → [`./references/metrics.md`](./references/metrics.md)。针对每个指标的阈值目标、TTI `frameRate.*` 参数的含义，以及区分缓慢但平稳的启动与主线程争用或硬阻塞的诊断模式。

## 快速链接到文档

- 入门指南: https://docs.expo.dev/eas/observe/get-started/
- 仪表板指南: https://docs.expo.dev/eas/observe/dashboard/
- 指标参考: https://docs.expo.dev/eas/observe/reference/metrics/
- Expo Router 集成: https://docs.expo.dev/eas/observe/integrations/expo-router/
- React Navigation 集成: https://docs.expo.dev/eas/observe/integrations/react-navigation/
- 用户定义的事件: https://docs.expo.dev/eas/observe/events/
- 配置: https://docs.expo.dev/eas/observe/configuration/
