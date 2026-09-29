---
name: swiftui-patterns
description: 构建和审查符合现代 MV 架构、状态、组合、独立预览和迁移指南的 SwiftUI 视图。涵盖 @Observable 所有权、@State/@Bindable/@Environment 连接、视图分解、ViewModifiers、环境值、.task 加载、iOS 26+ 的手柄、写作工具、剪贴板可用性以及性能。适用于构建 SwiftUI 状态、管理 @Observable、组合视图、预览有意义的 UI 状态或修正 SwiftUI 模式时使用。
---

# SwiftUI 模式

面向 iOS 26+ 和 Swift 6.3 的现代 SwiftUI 模式。涵盖架构、状态管理、视图组合、环境配置、异步加载、设计润色和平台/共享集成。导航、布局、动画和 Liquid Glass 模式位于专门的后代技能中。除非另有说明，否则模式向后兼容 iOS 17。

## 目录

- [架构：模型-视图 (MV) 模式](#架构-模型-视图-mv-模式)
- [工作流](#工作流)
- [状态管理](#状态管理)
- [视图排序约定](#视图排序约定)
- [视图组合](#视图组合)
- [环境](#环境)
- [异步数据加载](#异步数据加载)
- [iOS 26+ 新 API](#ios-26新-api)
- [性能指南](#性能指南)
- [HIG 对齐](#hig对齐)
- [编写工具 (iOS 18+)](#编写工具ios-18)
- [常见错误](#常见错误)
- [审查清单](#审查清单)
- [参考资料](#参考资料)

**范围边界**：此技能涵盖架构、状态所有权、组合、环境配置、异步加载和相关 SwiftUI 应用程序结构模式。详细的导航模式在 `swiftui-navigation` 技能中涵盖，包括 `NavigationStack`、`NavigationSplitView`、弹出窗口、标签和深度链接模式。详细的布局、容器和组件模式在 `swiftui-layout-components` 技能中涵盖，包括堆栈、网格、列表、滚动视图模式、表单、控件、带有 `.searchable` 的搜索 UI、覆盖和相关的布局组件。详细的动画编排在 `swiftui-animation` 中涵盖。Liquid Glass 采用、自定义玻璃控件、滚动边缘效果、`.scrollEdgeEffectStyle` 和 `.backgroundExtensionEffect` 在 `swiftui-liquid-glass` 中涵盖。

## 工作流

1.  记录当前状态所有权、操作、副作用、导航和生命周期行为。
2.  选择最小的 MV/状态/组合更改，以保留该契约。
3.  在每个结构步骤后构建；在继续之前修复编译器和隔离错误。
4.  根据适用情况渲染确定性预览，包括加载、加载中、空和错误状态，以及所需的环境依赖项。
5.  练习重要的交互和副作用。如果行为发生变化，请恢复固定装置，修复最小的边界，并重新运行相同的构建、预览和交互检查。

加载 [行为保留视图重构](references/view-refactoring.md) 以重构现有视图，并加载 [隔离预览构建](references/preview-isolation.md) 以获取固定装置和依赖项模式。

## 架构：模型-视图 (MV) 模式

默认使用 MV -- 视图是轻量级状态表达式；模型和服务拥有业务逻辑。除非现有代码已经使用它们，否则不要引入视图模型。

**核心原则：**
- 优先使用 `@State`、`@Environment`、`@Query`、`.task` 和 `.onChange` 进行编排
- 通过 `@Environment` 注入服务和共享模型；保持视图小而可组合
- 将大型视图拆分为较小的子视图，而不是引入视图模型
- 测试模型、服务和业务逻辑；保持视图简单和声明式

```swift
struct FeedView: View {
    @Environment(FeedClient.self) private var client

    enum ViewState {
        case loading, error(String), loaded([Post])
    }

    @State private var viewState: ViewState = .loading

    var body: some View {
        List {
            switch viewState {
            case .loading:
                ProgressView()
            case .error(let message):
                ContentUnavailableView("Error", systemImage: "exclamationmark.triangle",
                                       description: Text(message))
            case .loaded(let posts):
                ForEach(posts) { post in
                    PostRow(post: post)
                }
            }
        }
        .task { await loadFeed() }
        .refreshable { await loadFeed() }
    }

    private func loadFeed() async {
        do {
            let posts = try await client.getFeed()
            viewState = .loaded(posts)
        } catch {
            viewState = .error(error.localizedDescription)
        }
    }
}
```

有关 MV 模式原理、应用程序连接和轻量级客户端示例，请参阅 [references/architecture-patterns.md](references/architecture-patterns.md)。

## 状态管理

### `@Observable` 所有权规则

**重要提示**：当 SwiftUI 视图拥有、修改或绑定到 `@Observable` 存储和视图模型时，在 `@MainActor` 上隔离 UI 绑定的 `@Observable` 存储和视图模型。观察跟踪更改；它不会使共享可变状态线程安全。不接触 UI 状态的领域模型可以使用自己的隔离策略。

| 包装器 | 使用场景 |
|---------|-------------|
| `@State` | 视图拥有对象或值。创建和管理生命周期。 |
| `let` | 视图接收 `@Observable` 对象。只读观察 -- 不需要包装器。 |
| `@Bindable` | 视图接收 `@Observable` 对象并需要双向绑定 (`$property`)。 |
| `@Environment(Type.self)` | 从环境中访问共享 `@Observable` 对象。 |
| `@State` (值类型) | 视图本地简单状态：切换、计数器、文本字段值。始终 `private`。 |
| `@Binding` | 与父级的 `@State` 或 `@Bindable` 属性建立双向连接。 |

### 所有权模式

```swift
// UI 绑定的 @Observable 存储一一主线程隔离
@MainActor
@Observable final class ItemStore {
    var title = ""
    var items: [Item] = []
}

// 拥有模型的视图
struct ParentView: View {
    @State private var viewModel = ItemStore()

    var body: some View {
        ChildView(store: viewModel)
            .environment(viewModel)
    }
}

// 读取（不需要 @Observable 包装器）
struct ChildView: View {
    let store: ItemStore

    var body: some View { Text(store.title) }
}

// 绑定（需要双向访问）
struct EditView: View {
    @Bindable var store: ItemStore

    var body: some View {
        TextField("Title", text: $store.title)
    }
}

// 从环境中读取
struct DeepView: View {
    @Environment(ItemStore.self) private var store

    var body: some View {
        @Bindable var s = store
        TextField("Title", text: $s.title)
    }
}
```

**粒度跟踪**：SwiftUI 仅重新渲染读取了已更改属性的视图。如果视图读取 `items` 但不读取 `isLoading`，更改 `isLoading` 不会触发重新渲染。这是相对于 `ObservableObject` 的主要性能优势。

### 遗留的 ObservableObject

仅在使用支持 iOS 16 或更早版本时使用。`@StateObject` → `@State`，`@ObservedObject` → `let`，`@EnvironmentObject` → `@Environment(Type.self)`。

## 视图排序约定

从上到下按顺序排列成员：1) `@Environment` 2) `let` 属性 3) `@State` / 存储属性 4) 计算的 `var` 5) `init` 6) `body` 7) 视图构建器 / 辅助函数 8) 异步函数

## 视图组合

### 提取子视图

将视图拆分为专注的子视图。每个视图应具有单一职责。
当重构现有视图时，加载 [行为保留视图重构](references/view-refactoring.md)
以获取操作/副作用边界，并构建/预览证明。

```swift
var body: some View {
    VStack {
        HeaderSection(title: title, isPinned: isPinned)
        DetailsSection(details: details)
        ActionsSection(onSave: onSave, onCancel: onCancel)
    }
}
```

### 计算视图属性

为小型、无状态片段保留计算的 `some View` 属性。当片段具有以下任何信号时，将其提取为专用的 `View` 类型：

- 有意义的分支或大量布局
- 自己的状态或异步生命周期
- 比父级更窄的观察依赖项
- 有用的独立预览
- 复杂度足以掩盖父级的数据流

当缩小依赖项时，仅传递子视图需要的值、绑定和操作。如果它们形成一个庞大但连贯的接口，请传递一个功能范围的 `@Observable` 模型。观察将无效化限制为子视图读取的属性，但应用程序范围的存储仍然创建一个广泛的接口；将其保留给确实需要该连贯状态的子视图。

重用是一个有用的结果，而不是分解的先决条件。

扩展和 `// MARK: -` 组织大型文件；它们不会创建视图边界或替换提取。

### 视图构建器函数

用于不需要单独结构的条件逻辑：

```swift
@ViewBuilder
private func statusBadge(for status: Status) -> some View {
    switch status {
    case .active: Text("Active").foregroundStyle(.green)
    case .inactive: Text("Inactive").foregroundStyle(.secondary)
    }
}
```

### 自定义视图修改器

将重复的样式提取到 `ViewModifier`：

```swift
struct CardStyle: ViewModifier {
    func body(content: Content) -> some View {
        content
            .padding()
            .background(.background)
            .clipShape(.rect(cornerRadius: 12))
            .shadow(radius: 2)
    }
}
extension View { func cardStyle() -> some View { modifier(CardStyle()) } }
```

### 稳定的视图树

避免顶级条件视图交换。优先使用具有条件内部的单个稳定基本视图。

当提取的视图需要独立的状

14. 在每个栈上硬编码 `spacing:` -- 省略它以获得自适应的平台间距；仅当该值是有意指定时才使用
15. 将 `.copyable`、`.cuttable` 或基于命令的 `.pasteDestination(for:action:validator:)` 视为 iOS 16/iOS 26 API -- 根据当前 Apple 文档，它们是 macOS 13+ 以及 iOS/iPadOS/Mac Catalyst 27 beta 版本中的 API。对于 iOS 26 目标，请使用 `UIPasteboard`、拖放或 `ShareLink`。
16. 将现代默认行为视为正式弃用 -- `#Preview` 是现代预览默认值，但 `PreviewProvider` 是旧版而非编译器弃用。`EditButton`、`.onDelete` 和 `.onMove` 对于编辑模式的列表工作流程仍然有效；对于上下文行操作请使用 `.swipeActions`。
17. 为了让预览崩溃而将必需依赖项设为可选 -- 改为安装确定性的预览依赖项，不要使用实时网络、身份验证、生产数据库或全局单例

## 审查清单

- [ ] 在共享状态模型中使用 `@Observable`（在 iOS 17+ 上不使用 `ObservableObject`）
- [ ] `@State` 拥有对象；`let`/`@Bindable` 接收它们
- [ ] 检查和确认迁移及可用性声明是否符合当前平台支持，特别是剪贴板和共享 API
- [ ] 使用 `NavigationStack`（而不是 `NavigationView`）
- [ ] 使用 `.task` 修饰符进行异步数据加载
- [ ] 对大型集合使用 `LazyVStack`/`LazyHStack`
- [ ] 稳定的 `Identifiable` ID（不使用数组索引）
- [ ] 提取使用分支/布局、生命周期、依赖、预览或父级流程信号；小型无状态片段保持为计算属性
- [ ] 扩展和 `// MARK:` 仅用于组织文件
- [ ] 仅涉及结构的重构保留行为；使用薄的操作/生命周期方法，将可复用逻辑保留在 services/models 中，然后构建和渲染有用的预览
- [ ] 预览覆盖有意义的已加载/加载中/空/错误状态，使用确定性测试数据和每个必需的环境依赖项
- [ ] 视图 `body` 中没有重型计算
- [ ] 对环境使用深度共享状态
- [ ] 当语义样式优于固定颜色时使用 `foregroundStyle(_:)`
- [ ] 为重复样式使用自定义 `ViewModifier`
- [ ] 优先使用 `.sheet(item:)` 而不是 `.sheet(isPresented:)`
- [ ] 工作表拥有自己的操作并在内部调用 `dismiss()`
- [ ] 遵循 MV 模式 -- 没有不必要的视图模型
- [ ] UI 绑定的 `@Observable` 存储和视图模型是 `@MainActor` 隔离的
- [ ] 跨并发边界传递的模型类型是 `Sendable`
- [ ] 栈 `spacing:` 省略，除非需要特定值（优先使用自适应默认值）

## 参考

- 架构、应用程序接线和轻量级客户端：[references/architecture-patterns.md](references/architecture-patterns.md)
- 设计润色（HIG、主题、触觉反馈、过渡、加载、焦点）：[references/design-polish.md](references/design-polish.md)
- 弃用 API 迁移：[references/deprecated-migration.md](references/deprecated-migration.md)
- 平台和共享模式（Transferable、剪贴板可用性、媒体、菜单、macOS 设置）：[references/platform-and-sharing.md](references/platform-and-sharing.md)
- 隔离预览构建（状态覆盖、测试数据和环境依赖项）：[references/preview-isolation.md](references/preview-isolation.md)
- 现有视图重构（行为契约、操作/副作用边界和验证）：[references/view-refactoring.md](references/view-refactoring.md)
