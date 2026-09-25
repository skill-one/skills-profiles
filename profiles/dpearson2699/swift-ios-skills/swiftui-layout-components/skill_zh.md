# SwiftUI 布局与组件

面向 iOS 26+ 和 Swift 6.3 的 SwiftUI 应用布局与组件模式。涵盖堆叠和网格布局、列表模式、滚动视图、表单、控件、搜索和覆盖层。除非另有说明，否则模式向后兼容至 iOS 17。

## 目录

- [布局基础](#布局基础)
- [网格布局](#网格布局)
- [列表模式](#列表模式)
- [ScrollView](#scrollview)
- [表单和控件](#表单和控件)
- [Searchable](#searchable)
- [覆盖和呈现](#覆盖和呈现)
- [常见错误](#常见错误)
- [审查清单](#审查清单)
- [参考资料](#参考资料)

## 布局基础

### 标准堆叠

使用 `VStack`、`HStack` 和 `ZStack` 处理小型固定尺寸内容。它们会立即渲染所有子视图。

```swift
VStack(alignment: .leading) {
    Text(title).font(.headline)
    Text(subtitle).font(.subheadline).foregroundStyle(.secondary)
}
```

### 懒加载堆叠

在 `ScrollView` 中使用 `LazyVStack` 和 `LazyHStack` 处理大型或动态集合。它们会在滚动到视图中时按需创建子视图。

```swift
ScrollView {
    LazyVStack {
        ForEach(items) { item in
            ItemRow(item: item)
        }
    }
    .padding(.horizontal)
}
```

**何时使用哪种：**
- **非懒加载堆叠：** 小型固定内容（标题、工具栏、字段较少的表单）
- **懒加载堆叠：** 大型或未知尺寸的集合、信息流、聊天消息

## 网格布局

使用 `LazyVGrid` 处理图标选择器、媒体画廊和密集视觉选择。使用 `.adaptive` 列来适应不同设备尺寸的布局，或使用 `.flexible` 列来保持固定列数。

```swift
// 自适应网格 -- 列会自动调整以适应
let columns = [GridItem(.adaptive(minimum: 120, maximum: 1024))]

LazyVGrid(columns: columns) {
    ForEach(items) { item in
        ThumbnailView(item: item)
            .aspectRatio(1, contentMode: .fit)
    }
}
```

```swift
// 固定 3 列网格
let columns = Array(repeating: GridItem(.flexible(minimum: 100), spacing: 4), count: 3)

LazyVGrid(columns: columns, spacing: 4) {
    ForEach(items) { item in
        ThumbnailView(item: item)
    }
}
```

使用 `.aspectRatio` 来设置单元格尺寸。不要在懒加载容器内放置 `GeometryReader` —— 这会强制立即测量并破坏懒加载。如果需要读取尺寸，请使用 `.onGeometryChange`（iOS 16+）。

查看 [references/grids.md](references/grids.md) 获取完整的网格模式和设计选择。

## 列表模式

使用 `List` 处理信息流式内容和设置行，其中内置行重用、选择和可访问性很重要。

```swift
List {
    Section("常规") {
        NavigationLink("显示") { DisplaySettingsView() }
        NavigationLink("触觉反馈") { HapticsSettingsView() }
    }
    Section("账户") {
        Button("退出登录", role: .destructive) { }
    }
}
.listStyle(.insetGrouped)
```

**关键模式：**
- `.listStyle(.plain)` 用于信息流布局，`.insetGrouped` 用于设置
- `.scrollContentBackground(.hidden)` + 自定义背景用于主题化表面
- `.listRowInsets(...)` 和 `.listRowSeparator(.hidden)` 用于间距和分隔符控制
- **边缘滚动：** 使用 `List` + `ScrollPosition` 并带有 `.scrollPosition($scrollPosition)` 来实现顶部/底部滚动操作
- **项目或部分跳转：** 使用 `ScrollView` + 懒加载堆叠，并带有 `.scrollTargetLayout()` 和稳定目标来实现可靠的跳转到 ID 行为
- 使用 `.refreshable { }` 处理下拉刷新信息流
- 在需要可点击的行上使用 `.contentShape(Rectangle())`
- 对于布局审查或迁移指导，优先考虑容器选择和约束；保持代码片段简短，并将弹簧、过渡和时序选择推迟到 `swiftui-animation`

**iOS 26：** 使用 `.scrollEdgeEffectStyle(.soft, for: .top)` 来实现现代滚动边缘效果。

查看 [references/list.md](references/list.md) 获取完整的列表模式，包括带有滚动到顶部的信息流列表。

## ScrollView

当需要自定义布局、混合内容或水平滚动时，使用 `ScrollView` 与懒加载堆叠。

```swift
ScrollView(.horizontal, showsIndicators: false) {
    LazyHStack {
        ForEach(chips) { chip in
            ChipView(chip: chip)
        }
    }
}
```

**ScrollPosition：** 启用声明式、双向滚动位置跟踪和程序化滚动。

```swift
@State private var scrollPosition = ScrollPosition(edge: .bottom)

ScrollView {
    LazyVStack {
        ForEach(messages) { message in
            MessageRow(message: message)
        }
    }
    .scrollTargetLayout()
}
.scrollPosition($scrollPosition)
.onChange(of: messages.last?.id) {
    withAnimation { scrollPosition.scrollTo(edge: .bottom) }
}
```

**`safeAreaInset(edge:)`** 将内容（输入栏、工具栏）固定在键盘上方，而不会影响滚动布局。

**iOS 26 新增：**
- `.scrollEdgeEffectStyle(.soft, for: .top)` -- 淡入边缘效果
- `.backgroundExtensionEffect()` -- 在安全区域边缘镜像/模糊（谨慎使用，每屏一个）
- `.safeAreaBar(edge:)` -- 将与滚动效果集成的栏视图附加到边缘

查看 [references/scrollview.md](references/scrollview.md) 获取完整的 `ScrollPosition`、分页显示、缩放/裁剪冲突和 iOS 26 边缘效果模式。

## 表单和控件

### 表单

使用 `Form` 处理结构化设置和输入屏幕。将相关控件分组到 `Section` 块中。

```swift
Form {
    Section("通知") {
        Toggle("提及", isOn: $prefs.mentions)
        Toggle("关注", isOn: $prefs.follows)
    }
    Section("外观") {
        Picker("主题", selection: $theme) {
            ForEach(Theme.allCases, id: \.self) { Text($0.title).tag($0) }
        }
        Slider(value: $fontScale, in: 0.5...1.5, step: 0.1)
    }
}
.formStyle(.grouped)
.scrollContentBackground(.hidden)
```

使用 `@FocusState` 在输入密集型表单中管理键盘焦点。仅在独立呈现或使用 `NavigationStack` 时将其包装在表单中。

### 控件

| 控件 | 使用场景 |
|-------|-------|
| `Toggle` | 布尔值偏好设置 |
| `Picker` | 离散选择；`.segmented` 用于 2-4 个选项 |
| `Slider` | 带可见值标签的数值范围 |
| `DatePicker` | 日期/时间选择 |
| `TextField` | 带有 `.keyboardType`、`.textInputAutocapitalization` 的文本输入 |

直接将控件绑定到 `@State`、`@Binding` 或 `@AppStorage`。将相关控件分组到 `Form` 的部分中。使用 `.disabled(...)` 来反映锁定或继承的设置。在切换中嵌套 `Label` 来组合图标 + 文本，以增加清晰度。

避免使用 `.pickerStyle(.segmented)` 处理大型选项集；使用菜单或内联样式。不要隐藏滑块的标签；始终显示上下文。

查看 [references/form.md](references/form.md) 获取完整的表单示例。

## Searchable

使用 `.searchable` 添加原生搜索 UI。使用 `.searchScopes` 处理多个模式，并使用 `.task(id:)` 处理防抖异步结果。

```swift
@MainActor
struct ExploreView: View {
  @State private var searchQuery = ""
  @State private var searchScope: SearchScope = .all
  @State private var isSearching = false
  @State private var results: [SearchResult] = []

  var body: some View {
    List {
      if isSearching {
        ProgressView()
      } else {
        ForEach(results) { result in
          SearchRow(result: result)
        }
      }
    }
    .searchable(
      text: $searchQuery,
      placement: .navigationBarDrawer(displayMode: .always),
      prompt: Text("搜索")
    )
    .searchScopes($searchScope) {
      ForEach(SearchScope.allCases, id: \.self) { scope in
        Text(scope.title)
      }
    }
    .task(id: searchQuery) {
      await runSearch()
    }
  }

  private func runSearch() async {
    guard !searchQuery.isEmpty else {
      results = []
      return
    }
    isSearching = true
    defer { isSearching = false }
    try? await Task.sleep(for: .milliseconds(250))
    results = await fetchResults(query: searchQuery, scope: searchScope)
  }
}
```

在搜索为空时显示占位符。防抖输入以避免过度获取。保持搜索状态在视图内部。避免为空字符串运行搜索。

## 覆盖和呈现

使用 `.overlay(alignment:)` 处理短暂 UI（提示、横幅），而不会影响布局。

```swift
struct AppRootView: View {
  @State private var toast: Toast?

  var body: some View {
    content
      .overlay(alignment: .top) {
        if let toast {
          ToastView(toast: toast)
            .transition(.move(edge: .top).combined(with: .opacity))
            .onAppear {
              Task {
                try? await Task.sleep(for: .seconds(2))
                withAnimation { self.toast = nil }
              }
            }
        }
      }
  }
}
```

优先使用覆盖来处理短暂 UI，而不是嵌入布局堆叠中。使用过渡和短自动消失计时器。保持覆盖层对齐到清晰的边缘（`.top` 或 `.bottom`）。除非明确需要，否则避免使用会阻塞所有交互的覆盖层。不要堆叠许多覆盖层；使用队列或替换当前提示。

对于模态路由、表单分页和全屏呈现策略，请转交给 `swiftui-navigation` 技能。

## 常见错误

1. 在懒加载容器内放置 `GeometryReader` 会破坏懒加载；使用 `.onGeometryChange` 当需要尺寸时。
2. 数组索引会导致不稳定的 `ForEach` ID 并产生错误的 diffing。
3. 同轴嵌套滚动视图会导致手势冲突。
4. 重型自定义或扩展的 `List` 行应属于 `ScrollView` + `LazyVStack`。
5. 大型选项集应使用菜单或内联选择器样式，而不是 `.segmented`。
6. 除非特定间隙是故意的，否则不要省略堆叠/网格的 `spacing:` 以实现平台自适应默认值。
7. 从一个标准化的进度值驱动滚动显示，而不是并行布尔值或重复的拖动手势。
8. 保持每帧滚动几何为本地，并避免更改用于计算进度的几何。

## 审查清单

- [ ] 使用 `LazyVStack`/`LazyHStack` 处理大型或动态集合
- [ ] 所有 `ForEach` 项都有稳定的 `Identifiable` ID（不是数组索引）
- [ ] 懒加载容器内没有 `GeometryReader`
- [ ] `List` 样式与上下文匹配（`.plain` 用于信息流，`.insetGrouped` 用于设置）
- [ ] 使用 `Form` 处理结构化输入屏幕（而不是自定义堆叠）
- [ ] `.searchable` 使用 `.task(id:)` 防抖输入
- [ ] `.refreshable` 添加到支持下拉刷新的数据源
- [ ] 覆盖层使用过渡和自动消失计时器
- [ ] 可点击行使用 `.contentShape(Rectangle())`
- [ ] `@FocusState` 管理表单中的键盘焦点
- [ ] 堆叠/网格 `spacing:` 除非需要特定值，否则省略
- [ ] 滚动驱动的显示使用一个标准化的进度值，并保持几何更新在一个狭窄的子树中
- [ ] 冲突的缩放/裁剪交互会禁用滚动，离散的可见性效果不会驱动连续动画

## 参考资料

- 网格模式：[references/grids.md](references/grids.md)
- 列表和部分模式：[references/list.md](references/list.md)
- `ScrollView` 和懒加载堆叠：[references/scrollview.md](references/scrollview.md)
- 表单模式：[references/form.md](references/form.md)
- 架构和状态管理：参见 `swiftui-patterns` 技能
- 导航模式：参见 `swiftui-navigation` 技能
