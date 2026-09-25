# SwiftUI UI 模式

## 快速入门

根据您的目标选择一个轨道：

### 现有项目

- 确定功能或屏幕以及主要交互模型（列表、详情、编辑器、设置、标签页）。
- 在仓库中查找与 `rg "TabView("` 或类似的示例，然后阅读最接近的 SwiftUI 视图。
- 应用本地规范：优先使用 SwiftUI 原生状态，尽可能保持状态本地化，并使用环境注入来处理共享依赖。
- 从 `references/components-index.md` 中选择相关的组件参考，并遵循其指导。
- 如果交互通过拖动或滚动主要内容来揭示次要内容，请在手动实现手势之前阅读 `references/scroll-reveal.md`。
- 使用小型、专注的子视图和 SwiftUI 原生的数据流构建视图。

### 新项目脚手架

- 从 `references/app-wiring.md` 开始，以连接 TabView + NavigationStack + sheets。
- 基于提供的骨架添加最小的 `AppTab` 和 `RouterPath`。
- 根据您首先需要的 UI 选择下一个组件参考（TabView、NavigationStack、Sheets）。
- 随着新屏幕的添加，扩展路由和 sheet 枚举。

## 需要遵循的通用规则

- 使用现代 SwiftUI 状态（`@State`、`@Binding`、`@Observable`、`@Environment`），避免不必要的视图模型。
- 如果部署目标包括 iOS 16 或更早版本且无法使用 iOS 17 中引入的观察 API，则回退到使用 `ObservableObject` 和 `@StateObject` 进行根所有权，`@ObservedObject` 进行注入观察，以及仅在真正共享的应用级状态时使用 `@EnvironmentObject`。
- 优先使用组合；保持视图小型化和专注。
- 使用 async/await 与 `.task` 和显式的加载/错误状态。有关重启、取消和防抖的指导，请阅读 `references/async-state.md`。
- 将共享的应用服务放在 `@Environment` 中，但对于功能本地依赖和模型，优先使用显式初始化器注入。有关根连接模式，请阅读 `references/app-wiring.md`。
- 优先使用符合部署目标的最新 SwiftUI API，并在模式依赖于它时指明最低操作系统版本。
- 仅在编辑遗留文件时维护现有的遗留模式。
- 遵循项目的格式化器和样式指南。
- **Sheet**：当状态表示选定的模型时，优先使用 `.sheet(item:)` 而不是 `.sheet(isPresented:)`。避免在 sheet 身体内部使用 `if let`。Sheet 应该拥有自己的操作，并在内部调用 `dismiss()` 而不是转发 `onCancel`/`onConfirm` 闭包。
- **滚动驱动的揭示**：优先从滚动偏移量派生标准化的进度值，并从该单一事实来源驱动视觉状态。除非滚动本身无法表达交互，否则避免并行手势状态机。

## 状态所有权总结

使用与所有权模型最匹配的最窄状态工具：

| 场景 | 优先模式 |
| --- | --- |
| 由一个视图拥有的本地 UI 状态 | `@State` |
| 子视图修改父视图拥有的值状态 | `@Binding` |
| 在 iOS 17+ 上的根拥有的引用模型 | `@State` 与 `@Observable` 类型 |
| 在 iOS 17+ 上，子视图读取或修改注入的 `@Observable` 模型 | 明确地将其作为存储属性传递 |
| 共享的应用服务或配置 | `@Environment(Type.self)` |
| 在 iOS 16 及更早版本上的遗留引用模型 | 根处的 `@StateObject`，注入时使用 `@ObservedObject` |

首先选择所有权位置，然后选择包装器。如果使用纯值状态就足够，则不要引入引用模型。

## 跨领域参考

- `references/navigationstack.md`：导航所有权、每个标签页的历史记录和枚举路由。
- `references/sheets.md`：集中式模态呈现和枚举驱动的 sheets。
- `references/deeplinks.md`：URL 处理和将外部链接路由到应用目的地。
- `references/app-wiring.md`：根依赖图、环境使用和应用程序外壳连接。
- `references/async-state.md`：`.task`、`.task(id:)`、取消、防抖和异步 UI 状态。
- `references/previews.md`：`#Preview`、固定装置、模拟环境以及隔离式预览设置。
- `references/performance.md`：稳定身份、观察范围、懒容器和渲染成本防护措施。

## 反模式

- 在一个文件中混合布局、业务逻辑、网络、路由和格式的大型视图。
- 用于互斥 sheets、警报或导航目的地的多个布尔标志。
- 在视图生命周期钩子或注入的模型/服务中直接进行实时服务调用，而不是在 `body` 驱动的代码路径中。
- 为了解决应该通过更好的组合解决的类型不匹配问题而使用 `AnyView`。
- 默认将每个共享依赖设置为 `@EnvironmentObject` 或没有明确所有权理由的全局路由。

## 新 SwiftUI 视图的 workflow

1. 在编写 UI 代码之前，定义视图的状态、所有权位置和最低操作系统假设。
2. 确定哪些依赖属于 `@Environment`，哪些应该作为显式初始化器输入保留。
3. 绘制视图层次结构、路由模型和呈现点；将重复的部分提取为子视图。对于复杂的导航，请阅读 `references/navigationstack.md`、`references/sheets.md` 或 `references/deeplinks.md`。**在继续之前，构建并验证没有编译错误。**
4. 使用 `.task` 或 `.task(id:)` 实现异步加载，并在需要时添加显式的加载和错误状态。当工作依赖于变化的输入或取消时，请阅读 `references/async-state.md`。
5. 为主要和次要状态添加预览，然后在 UI 交互时添加可访问性标签或标识符。当视图需要固定装置或注入的模拟依赖时，请阅读 `references/previews.md`。
6. 通过构建进行验证：确认没有编译错误，检查预览是否在崩溃的情况下渲染，确保状态变化正确传播，并检查列表身份和观察范围不会导致不必要的重新渲染。如果屏幕较大、滚动密集或频繁更新，请阅读 `references/performance.md`。对于常见的 SwiftUI 编译错误——缺少 `@State` 注解、模糊的 `ViewBuilder` 闭包或不匹配的泛型类型——在更新调用点之前解决它们。**如果构建失败：**仔细阅读错误消息，修复已识别的问题，然后重建，再继续下一步。如果预览崩溃，隔离有问题的子视图，确认其状态初始化有效，并重新运行预览再继续。

## 组件参考

使用 `references/components-index.md` 作为入口点。每个组件参考应包括：
- 意图和最佳适用场景。
- 最小使用模式与本地规范。
- 陷阱和性能注意事项。
- 当前仓库中现有示例的路径。

## 添加新的组件参考

- 创建 `references/<component>.md`。
- 保持简短且可操作；链接到当前仓库中的具体文件。
- 更新 `references/components-index.md` 以包含新条目。
