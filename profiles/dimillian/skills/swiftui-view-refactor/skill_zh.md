# SwiftUI 视图重构

## 概述
重构 SwiftUI 视图，使其趋向于小型、明确、稳定的视图类型。默认使用纯 SwiftUI：视图中的本地状态，环境中的共享依赖项，服务/模型中的业务逻辑，以及在请求或现有代码明确需要时才使用视图模型。

## 核心指南

### 1) 视图顺序（从上到下）
- 除非现有文件有必须保留的更强的本地约定，否则强制执行此顺序。
- 环境
- `private`/`public` `let`
- `@State` / 其他存储属性
- 非视图计算 `var`
- `init`
- `body`
- 计算视图构建器 / 其他视图辅助工具
- 辅助函数 / 异步函数

### 2) 默认使用 MV 而不是 MVVM
- 视图应该是轻量级的状态表达式和编排点，而不是业务逻辑的容器。
- 优先使用 `@State`、`@Environment`、`@Query`、`.task`、`.task(id:)` 和 `onChange`，然后再考虑视图模型。
- 通过 `@Environment` 注入服务和共享模型；将领域逻辑保留在服务/模型中，而不是在视图体中。
- 不要仅仅为了镜像本地视图状态或包装环境依赖项而引入视图模型。
- 如果一个屏幕变得很大，请在发明新的视图模型层之前将 UI 分割成子视图。

### 3) 强烈优先使用专用子视图类型，而不是计算 `some View` 辅助工具
- 标记 `body` 属性，如果它们比大约一个屏幕更长或包含多个逻辑部分。
- 优先提取专用的 `View` 类型用于非平凡部分，特别是当它们有状态、异步工作、分支或值得它们自己的预览时。
- 保持计算 `some View` 辅助工具罕见且小型。不要使用 `private var header: some View` 风格的片段构建整个屏幕。
- 将小型、明确的输入（数据、绑定、回调）传递到提取的子视图，而不是传递整个父状态。
- 如果提取的子视图变得可重用或具有独立意义，将其移动到它自己的文件中。

优先：

```swift
var body: some View {
    List {
        HeaderSection(title: title, subtitle: subtitle)
        FilterSection(
            filterOptions: filterOptions,
            selectedFilter: $selectedFilter
        )
        ResultsSection(items: filteredItems)
        FooterSection()
    }
}

private struct HeaderSection: View {
    let title: String
    let subtitle: String

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(title).font(.title2)
            Text(subtitle).font(.subheadline)
        }
    }
}

private struct FilterSection: View {
    let filterOptions: [FilterOption]
    @Binding var selectedFilter: FilterOption

    var body: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack {
                ForEach(filterOptions, id: \.self) { option in
                    FilterChip(option: option, isSelected: option == selectedFilter)
                        .onTapGesture { selectedFilter = option }
                }
            }
        }
    }
}
```

避免：

```swift
var body: some View {
    List {
        header
        filters
        results
        footer
    }
}

private var header: some View {
    VStack(alignment: .leading, spacing: 6) {
        Text(title).font(.title2)
        Text(subtitle).font(.subheadline)
    }
}
```

### 3b) 将动作和副作用从 `body` 中提取出来
- 不要在视图体中将非平凡的按钮动作内联。
- 不要将业务逻辑隐藏在 `.task`、`.onAppear`、`.onChange` 或 `.refreshable` 中。
- 优先从视图中调用小型私有方法，并将真正的业务逻辑移动到服务/模型中。
- 视图体应该像 UI，而不是像视图控制器。

```swift
Button("Save", action: save)
    .disabled(isSaving)

.task(id: searchText) {
    await reload(for: searchText)
}

private func save() {
    Task { await saveAsync() }
}

private func reload(for searchText: String) async {
    guard !searchText.isEmpty else {
        results = []
        return
    }
    await searchService.search(searchText)
}
```

### 4) 保持稳定的视图树（避免顶层条件视图交换）
- 避免通过 `if/else` 返回完全不同根分支的 `body` 或计算视图。
- 优先使用单个稳定的基视图，并在部分/修饰符中（`overlay`、`opacity`、`disabled`、`toolbar` 等）中添加条件。
- 根级分支交换会导致身份更替、更广泛的无效化以及额外的重新计算。

优先：

```swift
var body: some View {
    List {
        documentsListContent
    }
    .toolbar {
        if canEdit {
            editToolbar
        }
    }
}
```

避免：

```swift
var documentsListView: some View {
    if canEdit {
        editableDocumentsList
    } else {
        readOnlyDocumentsList
    }
}
```

### 5) 视图模型处理（仅在已存在或明确请求时）
- 将视图模型视为遗留模式或显式需求模式，而不是默认模式。
- 除非请求或现有代码明确需要，否则不要引入视图模型。
- 如果视图模型存在，尽可能使其非可选。
- 通过 `init` 将依赖项传递给视图，然后在视图的 `init` 中创建视图模型。
- 避免 `bootstrapIfNeeded` 模式和其他延迟设置工作绕过。

示例（基于观察）：

```swift
@State private var viewModel: SomeViewModel

init(dependency: Dependency) {
    _viewModel = State(initialValue: SomeViewModel(dependency: dependency))
}
```

### 6) 观察使用
- 对于 iOS 17+ 上的 `@Observable` 引用类型，在拥有视图中将它们存储为 `@State`。
- 明确传递观察者；避免可选状态，除非 UI 真正需要它。
- 如果发布目标包括 iOS 16 或更早版本，请在拥有者处使用 `@StateObject`，并在注入遗留观察模型时使用 `@ObservedObject`。

## 工作流程

1. 按照顺序规则重新排序视图。
2. 从 `body` 中移除内联动作和副作用；将业务逻辑移动到服务/模型中，并在视图中仅保留薄编排。
3. 通过提取专用子视图类型缩短长视图体；避免使用许多计算 `some View` 辅助工具重建屏幕。
4. 确保稳定的视图结构：避免基于 `if` 的顶层分支交换；将条件移动到本地部分/修饰符中。
5. 如果视图模型存在或明确需要，用在 `init` 中初始化的非可选 `@State` 视图模型替换可选视图模型。
6. 确认观察使用：iOS 17+ 上的根 `@Observable` 模型使用 `@State`，仅在发布目标需要时使用遗留包装器。
7. 保持行为完整：除非请求，否则不要更改布局或业务逻辑。

## 注意事项

- 优先使用小型、明确的视图类型，而不是大型条件块和大型计算 `some View` 属性。
- 保持计算视图构建器在 `body` 下方，非视图计算 `var` 在 `init` 上方。
- 好的 SwiftUI 重构应使视图从上到下读取为数据流加布局，而不是混合布局和命令式逻辑。
- 对于 MV 首次指导及理由，参见 `references/mv-patterns.md`。

## 处理大型视图

当 SwiftUI 视图文件超过 ~300 行时，应积极分割。将有意义部分提取为专用的 `View` 类型，而不是将复杂性隐藏在许多计算属性中。使用带 `// MARK: -` 注释的 `private` 扩展来处理动作和辅助工具，但不要将扩展视为将巨大屏幕分割为较小视图类型的替代方案。如果提取的子视图可重用或具有独立意义，将其移动到它自己的文件中。
