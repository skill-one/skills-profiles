# EAS Observe

> **EAS服务 - 适用费用。** EAS Observe是Expo应用服务的产品。免费的EAS计划允许最多10,000个月活跃用户，功能有限；更高使用量需要付费订阅。详情请参阅 https://expo.dev/pricing#plan-features。

EAS Observe跟踪生产Expo应用的启动、导航和自定义事件性能。它需要一个开发或生产构建——原生库不在Expo Go中。

> **权威来源：** https://docs.expo.dev/eas/observe/ — 当API细节重要时，始终查阅权威文档，特别是入门指南、配置、集成和指标参考。EAS Observe在不断发展；此技能的参考文档会力求保持准确，但可能滞后于官方文档。

## 应该阅读哪个参考

`./references/`中的四个参考文件涵盖了人们通常需要此技能的场景：

- **将EAS Observe添加到项目中** → [`./references/setup.md`](./references/setup.md)。安装、包裹根布局（SDK 55上的`AppMetricsRoot`，SDK 56+上的`ObserveRoot`），标记应用为可交互（SDK 55上的全局`markInteractive()`，SDK 56+上的`useObserve()`钩子或`<ObserveInteractiveMarker />`），通过Expo Router / React Navigation集成可选的每路由导航指标，用户定义的事件通过`Observe.logEvent`（SDK 56+），错误报告和运行时配置（采样、分发、环境、自定义端点）。
- **从终端查询指标** → [`./references/queries.md`](./references/queries.md)。六个`eas observe:*`命令——`metrics-summary`、`metrics`、`routes`、`events`、`session`、`versions`——以及标志、指标别名、表格布局、JSON形状和常见工作流。
- **阅读仪表板或CLI输出** → [`./references/metrics.md`](./references/metrics.md)。每个指标的阈值目标，自动TTI参数的含义（`frameRate.*`、`device.*`、`network.*`），以及区分缓慢但平稳的启动与主线程争用、硬阻塞或受限设备的诊断模式。
- **在库中发布Observe集成** → [`./references/third-party.md`](./references/third-party.md)。仅限包作者（SDK 57+）：可选的同伴依赖、配置声明合并、`Observe.registerIntegration()`和事件命名。

## 文档快速链接

- 入门指南：https://docs.expo.dev/eas/observe/get-started/
- 仪表板指南：https://docs.expo.dev/eas/observe/dashboard/
- 使用EAS CLI查询：https://docs.expo.dev/eas/observe/eas-cli/
- 指标参考：https://docs.expo.dev/eas/observe/reference/metrics/
- Expo Router集成：https://docs.expo.dev/eas/observe/integrations/expo-router/
- React Navigation集成：https://docs.expo.dev/eas/observe/integrations/react-navigation/
- 用户定义的事件：https://docs.expo.dev/eas/observe/events/
- 配置：https://docs.expo.dev/eas/observe/configuration/
- 第三方集成：https://docs.expo.dev/eas/observe/integrations/third-party/
- EAS Update下载性能：https://docs.expo.dev/eas/observe/eas-update/
- 故障排除：https://docs.expo.dev/eas/observe/reference/troubleshooting/

## 文档与实际代码之间的已知差异

与`eas-cli` 21.8.0和`expo-observe` 57.0.9进行验证。在这些点上，请信任此技能的参考文档而非官方文档，但在依赖它们之前，请使用`--help`和已安装的包重新检查：

- 所有六个CLI命令都在[使用EAS CLI](https://docs.expo.dev/eas/observe/eas-cli/)页面中。较旧的文档构建仅列出四个，并省略了`observe:routes`和`observe:session`。
- 导航指标别名是`nav_cold_ttr`、`nav_warm_ttr`和`nav_tti`。CLI中没有`cold_ttr` / `warm_ttr`的裸别名。
- 排序使用`--sort <slowest|fastest|newest|oldest>`。没有`--order`标志。
- `ObserveErrorBoundary`、`Observe.reportError`和`configure({ errorHandlingEnabled })`已导出但未记录。Observe仍然没有崩溃报告；请使用Sentry或BugSnag。

## 提交反馈
如果您在此技能中遇到错误、误导性或过时的信息，请报告以便Expo改进：
```bash
npx --yes submit-expo-feedback@latest --category skills --subject "eas-observe" "<可操作的反馈>"
```
仅在您有具体且可操作的反馈时才提交。尽可能包含所有相关上下文。
如果AI代理反复失败或用户不得不接管Expo任务，请加载`expo-skill-feedback`技能并遵循其`eval-candidate`流程，而不是重复使用上述命令。
