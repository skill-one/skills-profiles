<!-- GENERATED from convex-agents content/capabilities/optimize.json — do not edit by hand. -->

# 审计和优化现有的 Convex 应用

现有应用的修复 WORKFLOW：以评分评估开始，然后根据评估结果采取行动 — 升级过时的组件并设置可观察性 — 计划-确认-应用。评估本身委托给 launch-readiness（findings-bus 评分器）；优化的独特价值在于其对评估结果的行动。

## WORKFLOW

1. 检测应用：一个 `convex/` 目录、模式，以及它是匿名部署还是云部署。
2. 通过 `launch-readiness` 进行评估 — 一个评分的、去重的报告，跨越 authz/reviewer/advisor/insights，并带有排序的修复计划。不要手动重新运行这些步骤；optimize 消费 launch-readiness 的报告，而不是重新实现审计。
3. UPGRADE：对固定的 `@convex-dev/*` 组件运行 `check-updates`，并将过时组件（过时类别）的发现结果合并到同一计划中。
4. OBSERVABILITY：如果就绪报告标记了可观察性差距（没有生产错误捕获），则提供安装 `sentinel` 的选项。
5. 展示合并的优先计划 — launch-readiness 评分 + 修复计划 + 升级 + 可观察性，安全/数据丢失优先 — 仅在明确确认后应用，并将每个修复任务分派到其 fixCapability。
6. 应用后，重新运行 launch-readiness 评估并显示评分差异。

## 规则

- 首先只读。展示计划并 CONFIRM 后才更改任何文件。
- 将审计委托给 launch-readiness（findings-bus 评分器）；不要内联重新实现 reviewer/advisor/insights — optimize 的工作是对报告采取行动（升级 + 可观察性），而不是重新评分。
- 优先考虑安全和数据丢失风险，而不是样式，遵循 launch-readiness 的排序。
- 不要自动将更改部署到某人的现有生产应用上；应用后重新评估并显示评分有所变化。
