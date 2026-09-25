# SwiftUI 性能审计

## 快速入门

使用此技能从代码层面首先诊断 SwiftUI 性能问题，然后在代码审查无法解释症状时请求性能分析证据。

## 工作流程

1. 识别症状：渲染缓慢、滚动卡顿、CPU 占用率高、内存增长、卡死或视图更新过度。
2. 如果代码可用，使用 `references/code-smells.md` 进行代码优先级审查。
3. 如果代码不可用，请求最小的有用代码片段：目标视图、数据流、复现步骤和部署目标。
4. 如果代码审查结果不明确或需要运行时证据，引导用户使用 `references/profiling-intake.md` 进行性能分析。
5. 使用 `references/report-template.md` 总结可能的原因、证据、修复方案和验证步骤。

## 1. 信息收集

收集：
- 目标视图或功能代码。
- 症状和精确的复现步骤。
- 数据流：`@State`、`@Binding`、环境依赖和可观察模型。
- 问题是否在设备或模拟器上出现，以及是否在 Debug 或 Release 模式下观察到。

如果可能，请用户对问题进行分类：
- CPU 峰值或电池消耗
- 滚动卡顿或帧丢失
- 内存过高或图像压力过大
- 卡死或无响应交互
- 视图更新过度或范围异常广泛

有关完整的性能分析信息收集清单，请阅读 `references/profiling-intake.md`。

## 2. 代码优先级审查

重点关注：
- 由广泛观察或环境读取引发的无效化风暴。
- 列表和 `ForEach` 中不稳定的身份。
- `body` 或视图构建器中的大量派生工作。
- 复杂层次结构、`GeometryReader` 或偏好链引起的布局混乱。
- 主线程上的大图像解码或缩放工作。
- 过度泛用的动画或过渡工作。

使用 `references/code-smells.md` 获取详细的气味目录和修复指南。

提供：
- 带代码引用的可能根本原因。
- 建议的修复和重构方案。
- 如有必要，提供最小化复现或测量建议。

## 3. 引导用户进行性能分析

如果代码审查无法解释问题，请求运行时证据：
- SwiftUI 时间线和时间分析器调用树的跟踪导出或截图。
- 设备/OS/构建配置。
- 正在分析的精确交互。
- 如果用户正在比较变更，提供前后指标。

使用 `references/profiling-intake.md` 获取精确清单和收集步骤。

## 4. 分析和诊断

- 将证据映射到最可能的类别：无效化、身份周转、布局混乱、主线程工作、图像成本或动画成本。
- 按影响优先级排序问题，而不是按解释难度排序。
- 区分代码级怀疑和有跟踪证据的情况。
- 指出何时性能分析仍不足以及哪些额外证据可以减少不确定性。

## 5. 修复

应用针对性修复：
- 缩小状态范围并减少广泛观察的传播范围。
- 稳定 `ForEach` 和列表的身份。
- 将大量工作从 `body` 移到从输入、模型层预计算、记忆化辅助函数或后台预处理更新的派生状态中。仅将 `@State` 用于视图拥有的状态，而不是作为任意计算的临时缓存。
- 仅在等价性比重新计算子树更便宜且输入确实是值语义时使用 `equatable()`。
- 渲染前对图像进行下采样。
- 减少布局复杂性或在可能的情况下使用固定尺寸。

使用 `references/code-smells.md` 获取示例、特定观察的传播范围指南和修复模式。

## 6. 验证

请求用户重新运行相同的捕获并与基线指标进行比较。
如果提供，总结差异（CPU、帧丢失、内存峰值）。

## 输出

提供：
- 短暂的指标表（如有可用，则提供前后对比）。
- 主要问题（按影响排序）。
- 建议的修复方案及预估工作量。

使用 `references/report-template.md` 格式化最终审计报告。

## 参考资料

- 性能分析信息收集清单：`references/profiling-intake.md`
- 常见代码气味和修复模式：`references/code-smells.md`
- 审计输出模板：`references/report-template.md`
- 用户提供的 `references/` 下添加 Apple 文档和 WWDC 资源。
- 使用 Instruments 优化 SwiftUI 性能：`references/optimizing-swiftui-performance-instruments.md`
- 理解和改进 SwiftUI 性能：`references/understanding-improving-swiftui-performance.md`
- 理解应用中的卡死：`references/understanding-hangs-in-your-app.md`
- SwiftUI 性能揭秘（WWDC23）：`references/demystify-swiftui-performance-wwdc23.md`
