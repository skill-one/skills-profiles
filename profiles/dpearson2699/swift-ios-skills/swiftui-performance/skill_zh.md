# SwiftUI 性能

从可复现的症状到测量的修复方案，审计 SwiftUI 视图性能。将动画设计路由到 `swiftui-animation`，生产遥测数据路由到 `metrickit`，所有权/内存泄漏分析路由到 `ios-memgraph-analysis`，导航行为路由到 `swiftui-navigation`，状态架构路由到 `swiftui-patterns`，布局构建路由到 `swiftui-layout-components`。

## 目录

- [工作流决策树](#workflow-decision-tree)
- [1. 代码优先审查](#1-code-first-review)
- [2. 引导用户到配置文件](#2-guide-the-user-to-profile)
- [3. 分析和诊断](#3-analyze-and-diagnose)
- [4. 修复](#4-remediate)
- [常见代码异味（及修复）](#common-code-smells-and-fixes)
- [5. 验证](#5-verify)
- [输出](#outputs)
- [Instruments 性能分析](#instruments-profiling)
- [身份和生命周期](#identity-and-lifetime)
- [惰性加载模式](#lazy-loading-patterns)
- [状态和观察优化](#state-and-observation-optimization)
- [常见错误](#common-mistakes)
- [审查清单](#review-checklist)
- [参考资料](#references)

## 工作流决策树

- 提供代码：首先审查它，并将发现的结果标记为假设。
- 只有症状：收集最小的相关视图、数据流、可复现性、设备、操作系统和构建配置。
- 审查结果不明确：在建议广泛的重构之前，收集跟踪或车道截图。

使用此分诊列表进行代码和跟踪分析：

- 广泛的状态依赖或无效化风暴
- 不稳定的列表身份或根条件交换
- 在 `body` 中进行格式化、排序、解码或同步 I/O
- 布局/几何反馈循环和过大的图像
- 将隐式动画应用于大型层次结构

## 1. 代码优先审查

将分诊列表中的每个可疑项映射到确切代码。使用代码引用报告可能的原因，但在跟踪确认成本之前，将它们标记为代码支持的假设。当证据缺失时，建议最小可复现性或测量方案。

## 2. 引导用户到配置文件

在可能的情况下，使用 SwiftUI Instruments 模板在 **发布构建** 和真实设备上进行。重现精确的交互，捕获 SwiftUI 车道、时间分析器和挂起/卡顿。要求提供跟踪或车道和调用树的截图。

## 3. 分析和诊断

将相同的分诊列表应用于跟踪证据。将长时间或频繁的 SwiftUI 更新与时间分析器调用树和复现的交互相关联。将基于跟踪的发现与代码支持的假设分开，并命名将解决剩余不确定性的下一个测量方案。

## 4. 修复

应用有针对性的修复：

- 缩小状态范围（`@State`/`@Observable` 更靠近叶视图）。
- 为 `ForEach` 和列表稳定身份。
- 将繁重的工作从 `body` 移到模型层的预计算、显式派生值（在其输入更改时更新）、记忆化辅助函数或后台处理。仅在视图拥有值及其更新生命周期时使用 `@State`；它不是通用的任意计算缓存。
- 仅在相等性比重新计算子树更便宜且比较的输入具有稳定值语义时使用 `equatable()`。
- 在渲染之前对图像进行下采样。
- 减少布局复杂性或在可能的情况下使用固定尺寸。

## 常见代码异味（及修复）

| 异味 | 寻找的证据 | 针对性修复 |
|---|---|---|
| 在 `body` 中进行格式化、排序、过滤或解码 | 长时间/频繁的 `body` 更新与匹配的调用树成本 | 输入更改时重新计算；在主线程之外下采样/解码 |
| `UUID()` 或不稳定的 `id: \.self` | 重新创建的行、丢失的状态、过多的更新 | 使用稳定的模型身份 |
| 根 `if`/`else` 交换 | 切换时状态重置或更新峰值 | 在语义允许时将条件内容/修饰符局部化 |
| 广泛的模型读取 | 许多不相关的视图一起更新 | 传递狭窄的值或将读取移入聚焦的子视图 |
| 布局期间的几何写入 | 重复的布局/更新循环 | 阈值更改或用稳定布局替换反馈路径 |

## 5. 验证

要求用户重新运行相同的捕获并与基线指标进行比较。如果提供，请总结差异（CPU、帧丢失、内存峰值）。

## 输出

提供：

- 短暂的指标表（如果可用，则提供前后）。
- 顶级问题（按影响排序）。
- 建议的修复方案及估计工作量。

## Instruments 性能分析

使用 Instruments 中的 **SwiftUI 模板**（使用 Cmd+I 进行性能分析）。当前的 SwiftUI 车道包括更新组、长时间视图 `body` 更新、长时间可表示更新 / 可表示更新、其他长时间更新 / 其他更新以及因果关系图。将这些与时间分析器和挂起/卡顿相关联。

在调试构建中添加 `Self._printChanges()` 以记录触发视图更新的属性：

```swift
var body: some View {
    #if DEBUG
    let _ = Self._printChanges()  // "MyView: @self, _count changed."
    #endif
    Text("Count: \(count)")
}
```

有关完整性能分析工作流的详细信息，请参阅 [参考资料/优化 SwiftUI 性能 Instruments.md](references/optimizing-swiftui-performance-instruments.md)。

## 身份和生命周期

身份控制视图生命周期和状态。在重复内容中使用稳定的模型 ID，并为有意重置保留 `.id(_:)` 更改。优先使用 `@ViewBuilder` 或通用组合而不是 `AnyView` 在分析的行中。当证据显示状态波动或昂贵重建时，将根条件分支视为可疑对象——而不是自动缺陷。

```swift
Text(title)
    .foregroundStyle(isHighlighted ? .yellow : .primary)

ForEach(items) { item in
    Row(item: item).id(item.stableID)
}
```

## 惰性加载模式

当分析显示急切构建、布局或更新工作是实质性的；没有通用的项目计数阈值时，使用惰性容器。将网格/列表构建选择路由到 `swiftui-layout-components`。

护栏：

- 屏幕外的视图从惰性堆栈中移除。SwiftUI 可能会暂时保留它们，然后删除视图及其视图本地状态。
- 如果必须保留滚动外的行状态，请将其持久化到行视图之外。
- 由于预取，`onAppear` 之前可以进行 `body` 和布局工作。不要使 `onAppear` 成为行需要渲染数据的唯一设置点。
- 将 `onAppear` 和 `onDisappear` 视为可见性信号，而不是生命周期保证。
- 在 `ForEach` 之前过滤数据；避免使每个元素产生零行或一行 `if` 分支。
- 保持每个 `ForEach` 元素到常数的顶级子视图数。如果需要，请将行内容包装在稳定容器中。在调试列表/表格慢路径时使用 `-LogForEachSlowPath YES`。
- 避免绝对内容尺寸或内容偏移假设；惰性堆栈估计屏幕外尺寸。
- 避免惰性行中的几何反馈循环。优先使用稳定尺寸、布局原语或自定义 `Layout`，然后再将几何更改反馈到行状态。

## 状态和观察优化

观察跟踪在视图评估期间读取的属性。通过传递狭窄的派生值或将读取移入聚焦的子视图来减少扇出。

```swift
// 将读取拆分为子视图，以便每个视图仅跟踪它渲染的内容。
struct ProfileView: View {
    let model: ProfileModel
    var body: some View {
        VStack {
            NameRow(model: model)      // 仅跟踪名称
            EmailRow(model: model)     // 仅跟踪电子邮件
            AvatarView(model: model)   // 仅跟踪头像
            SettingsForm(model: model) // 仅跟踪设置
        }
    }
}
```

廉价的计算值可以保持派生状态；昂贵的转换需要一个显式的所有者、输入集和刷新触发器。不要将视图模型作为性能仪式添加——首先测量，并将通用状态设计路由到 `swiftui-patterns`。

## 常见错误

1. **在调试构建上进行性能分析。** 调试构建包括额外的运行时检查并禁用优化，生成的性能数据具有误导性。在真实设备上分析发布构建。
2. **观察整个模型，而只需要一个属性。** 将大型 `@Observable` 模型拆分为聚焦的模型，或使用计算属性/闭包来缩小观察范围。
3. **在 `ScrollView` 项内使用几何反馈。** 几何读取器或嘈杂的几何状态可以强制重复布局。优先使用稳定尺寸、自定义布局或狭窄范围的 `.onGeometryChange`（iOS 16+）并设置阈值。
4. **在 `body` 内调用 `DateFormatter()` 或 `NumberFormatter()`。** 这些创建起来很昂贵。使它们成为静态的或将它们移出视图。
5. **对非等价状态进行动画。** 如果 SwiftUI 无法确定相等性，它将每帧重绘。使状态符合 `Equatable`，然后使用 `.animation(_:value:)` 进行简单的值绑定更改或 `.animation(_:body:)` 进行更狭窄的修饰符作用域隐式动画。
6. **没有标识符的大型扁平 `List`。** 使用 `id:` 或使项目 `Identifiable`，以便 SwiftUI 可以有效地进行差异比较，而不是重建整个列表。
7. **不必要的 `@State` 包装对象。** 将简单值类型包装在类中以用于 `@State` 会破坏值语义。使用结构体的 `@State`。
8. **使用同步 I/O 阻塞 `MainActor`。** 文件读取、大型有效载荷的 JSON 解析和图像解码应在主线程之外进行。优先使用非隔离的异步辅助函数或专用演员；保留 `Task.detached` 用于您有意打破演员继承并自行处理取消的情况。

## 审查清单

- [ ] `body` 内没有 `DateFormatter`/`NumberFormatter` 分配
- [ ] 大型列表使用 `Identifiable` 项目或显式 `id:`
- [ ] `@Observable` 模型仅暴露视图实际读取的属性
- [ ] 繁重计算在 `MainActor` 之外（图像处理、解析）
- [ ] 惰性行具有稳定身份、常数的顶级行形状和预过滤数据
- [ ] 滚动行中的几何更改被阈值化，并且不会将广泛的反馈传递到状态
- [ ] 行渲染不依赖于 `onAppear` 作为唯一的设置点
- [ ] 隐式动画使用 `.animation(_:value:)` 进行值绑定更改或 `.animation(_:body:)` 进行更狭窄的修饰符作用域
- [ ] 主线程上没有同步网络/文件 I/O
- [ ] 性能分析在发布构建、真实设备上进行
- [ ] `@State` 不用作未指定的缓存；每个派生值都有显式的所有者和刷新触发器
- [ ] `equatable()` 仅在比较比重新计算更便宜且输入具有稳定值语义时使用
- [ ] 发现区分代码支持的假设和跟踪支持的证据
- [ ] `@Observable` 视图模型是 `@MainActor`-隔离的；跨越并发边界的类型是 `Sendable`

## 参考资料

- 神秘的 SwiftUI 性能解密（WWDC23）：[参考资料/解密 SwiftUI 性能 WWDC23.md](references/demystify-swiftui-performance-wwdc23.md)
- 使用 Instruments 优化 SwiftUI 性能：[参考资料/优化 SwiftUI 性能 Instruments.md](references/optimizing-swiftui-performance-instruments.md)
- 了解应用程序中的挂起：[参考资料/了解应用程序中的挂起.md](references/understanding-hangs-in-your-app.md)
- 了解和改进 SwiftUI 性能：[参考资料/了解改进 SwiftUI 性能.md](references/understanding-improving-swiftui-performance.md)
- WWDC 文本来源：[参考资料/wwdc 会话来源.md](references/wwdc-session-sources.md)
