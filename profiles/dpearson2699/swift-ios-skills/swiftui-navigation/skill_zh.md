# SwiftUI 导航

针对 iOS 26+ 和 Swift 6.3 的 SwiftUI 应用导航模式。涵盖推送导航、多列布局、页面呈现、标签架构和深度链接。除非另有说明，否则模式向后兼容至 iOS 17。

## 目录

- [NavigationStack (推送导航)](#navigationstack-push-navigation)
- [NavigationSplitView (多列)](#navigationsplitview-multi-column)
- [页面呈现](#sheet-presentation)
- [基于标签的导航](#tab-based-navigation)
- [深度链接](#deep-links)
- [常见错误](#common-mistakes)
- [审查清单](#review-checklist)
- [参考资料](#references)

## NavigationStack (推送导航)

使用带类型 `[Route]` 绑定的 `NavigationStack` 进行程序化推送导航。将路由定义为 `Hashable` 枚举，并使用 `.navigationDestination(for:)` 映射它们；这可以保持路径在编译时检查。仅在必须使用异构路由值类型的单个堆栈时使用 `NavigationPath`。

```swift
enum Route: Hashable {
    case item(id: Item.ID)
}

struct ContentView: View {
    @State private var path: [Route] = []
    let items: [Item]

    var body: some View {
        NavigationStack(path: $path) {
            List(items) { item in
                NavigationLink(value: Route.item(id: item.id)) {
                    ItemRow(item: item)
                }
            }
            .navigationDestination(for: Route.self) { route in
                switch route {
                case .item(let id):
                    DetailView(itemID: id)
                }
            }
            .navigationTitle("项目")
        }
    }
}
```

**程序化导航：**

```swift
path.append(.item(id: item.id))  // 推送
path.removeLast()                // 弹出一个
path = []                        // 弹出到根
```

**路由模式：** 对于具有复杂导航的应用，使用拥有路径和页面状态的路由对象。每个标签都通过 `.environment()` 注入自己的路由实例。使用单个 `.navigationDestination(for:)` 块或共享 `withAppRouter()` 修饰符集中目的地映射。

参见 [参考资料/navigationstack.md](references/navigationstack.md) 获取完整的路由示例，包括每个标签的堆栈、集中式目的地映射和通用标签路由。

## NavigationSplitView (多列)

使用 `NavigationSplitView` 在 iPad 和 Mac 上进行侧边栏-详情布局。在 iPhone 上回退到堆栈导航。

```swift
struct MasterDetailView: View {
    @State private var selectedItem: Item?

    var body: some View {
        NavigationSplitView {
            List(items, selection: $selectedItem) { item in
                NavigationLink(value: item) { ItemRow(item: item) }
            }
            .navigationTitle("项目")
        } detail: {
            if let item = selectedItem {
                ItemDetailView(item: item)
            } else {
                ContentUnavailableView("选择一个项目", systemImage: "sidebar.leading")
            }
        }
    }
}
```

### 自定义分割列（手动 HStack）

对于自定义多列布局（例如，独立于选择的专用通知列），使用带 `horizontalSizeClass` 检查的手动 `HStack` 分割：

```swift
@MainActor
struct AppView: View {
  @Environment(\.horizontalSizeClass) private var horizontalSizeClass
  @AppStorage("showSecondaryColumn") private var showSecondaryColumn = true

  var body: some View {
    HStack(spacing: 0) {
      primaryColumn
      if shouldShowSecondaryColumn {
        Divider().edgesIgnoringSafeArea(.all)
        secondaryColumn
      }
    }
  }

  private var shouldShowSecondaryColumn: Bool {
    horizontalSizeClass == .regular
      && showSecondaryColumn
  }

  private var primaryColumn: some View {
    TabView { /* 标签 */ }
  }

  private var secondaryColumn: some View {
    NotificationsTab()
      .environment(\.isSecondaryColumn, true)
      .frame(maxWidth: .secondaryColumnWidth)
  }
}
```

当您需要完全控制或非标准次要列时，使用手动 HStack 分割。当您想要标准系统布局和最小化自定义时，使用 `NavigationSplitView`。

## Sheet Presentation

优先使用 `.sheet(item:)` 而不是 `.sheet(isPresented:)`，当状态表示选定的模型时。页面应拥有自己的操作并在内部调用 `dismiss()`。

```swift
@State private var selectedItem: Item?

.sheet(item: $selectedItem) { item in
    EditItemSheet(item: item)
}
```

**呈现尺寸（iOS 18+）：** 使用 `.presentationSizing` 控制页面尺寸：

```swift
.sheet(item: $selectedItem) { item in
    EditItemSheet(item: item)
        .presentationSizing(.form)  // .form, .page, .fitted, .automatic
}
```

`PresentationSizing` 值：
- `.automatic` -- 平台默认
- `.page` -- 大约纸张尺寸，用于信息内容
- `.form` -- 略窄于页面，用于表单式 UI
- `.fitted` -- 由内容理想尺寸决定

微调：`.fitted(horizontal:vertical:)` 限制适配轴；`.sticky(horizontal:vertical:)` 在指定维度内增长但不缩小。

**取消呈现保护：** 在 iOS/iPadOS 上，使用 `.interactiveDismissDisabled(hasUnsavedChanges)` 并在页面内提供明确的保存/放弃操作。在 macOS 15+ 上，使用 `.dismissalConfirmationDialog("放弃？", shouldPresent: hasUnsavedChanges)` 进行窗口取消确认。
通过相同的保存/验证/放弃门路处理所有程序化关闭；
`interactiveDismissDisabled` 仅保护交互式取消。

**枚举驱动页面路由：** 定义一个 `SheetDestination` 枚举，它是 `Identifiable`，将其存储在路由器上，并使用共享视图修饰符映射它。这允许任何子视图呈现页面，而无需属性钻取。参见 [参考资料/sheets.md](references/sheets.md) 获取完整的集中式页面路由模式。

## Tab-Based Navigation

使用带选择绑定的 `Tab` API 进行可扩展的标签架构。每个标签应将其内容包装在独立的 `NavigationStack` 中。

```swift
struct MainTabView: View {
    @State private var selectedTab: AppTab = .home

    var body: some View {
        TabView(selection: $selectedTab) {
            Tab("首页", systemImage: "house", value: .home) {
                NavigationStack { HomeView() }
            }
            Tab("搜索", systemImage: "magnifyingglass", value: .search) {
                NavigationStack { SearchView() }
            }
            Tab("个人资料", systemImage: "person", value: .profile) {
                NavigationStack { ProfileView() }
            }
        }
    }
}
```

**自定义绑定带副作用：** 通过函数路由选择更改以拦截特殊标签（例如， compose），这些标签应触发操作而不是更改选择。

### iOS 26 标签新增功能

- **`Tab(value:role:)` with `.search`** -- 标记专用搜索标签，带有系统默认搜索标题、图标和固定行为
- **`.tabViewSearchActivation(_:)`** -- 控制搜索标签激活和停用行为
- **`.tabBarMinimizeBehavior(_:)`** -- `.onScrollDown`, `.onScrollUp`, `.never` (iPhone 仅限)
- **`.tabViewSidebarHeader/Footer`** -- 在 iPadOS/macOS 上自定义侧边栏部分
- **`.tabViewBottomAccessory { }`** -- 在标签栏下方附加内容（例如，正在播放栏）
- **`TabSection`** -- 使用 `.tabPlacement(.sidebarOnly)` 将标签分组到侧边栏部分

参见 [参考资料/tabview.md](references/tabview.md) 获取完整的 TabView 模式，包括自定义绑定、动态标签和侧边栏自定义。

## Deep Links

使用解析→验证→提交。解析为带类型的路由而不修改导航；验证方案/主机/路径、标识符形状、授权和目的地存在；然后原子性地更新标签/路径。无效链接必须保持当前导航不变。

### Universal Links

通用链接允许 iOS 为标准 HTTPS URL 打开您的应用。它们需要：
1. 一个位于 `/.well-known/apple-app-site-association` 的 Apple App Site Association (AASA) 文件
2. 一个 Associated Domains 授权 (`applinks:example.com`)

使用 `.onOpenURL` 在 SwiftUI 中处理通用链接和自定义 URL 方案：

```swift
@main
struct MyApp: App {
    @State private var router = Router()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environment(router)
                .onOpenURL { url in router.handle(url: url) }
        }
    }
}
```

### Custom URL Schemes

在 `Info.plist` 中注册方案，位于 `CFBundleURLTypes` 下。使用 `.onOpenURL` 处理。优先使用通用链接而不是自定义方案，用于公开共享的链接——它们提供网络回退和域名验证。

### Handoff (NSUserActivity)

使用 `.userActivity()` 广告活动，并使用 `.onContinueUserActivity()` 接收 Handoff 或其他用户活动。在 `Info.plist` 中声明活动类型，位于 `NSUserActivityTypes` 下。设置 `isEligibleForHandoff = true` 并提供 `webpageURL` 作为回退。

参见 [参考资料/deeplinks.md](references/deeplinks.md) 获取完整的 AASA 配置、路由器 URL 处理、自定义 URL 方案和 NSUserActivity 继续示例。

## Common Mistakes

1. 使用已弃用的 `NavigationView` -- 使用 `NavigationStack` 或 `NavigationSplitView`
2. 在所有标签之间共享一个导航路径或路由器——每个标签都需要自己的路径
3. 当状态表示模型时使用 `.sheet(isPresented:)`——使用 `.sheet(item:)` 代替
4. 在导航路径中存储视图实例——存储轻量级的 `Hashable` 路由数据
5. 在其他 `@Observable` 对象内嵌套 `@Observable` 路由器对象
6. 优先使用 `Tab(value:)` with `TabView(selection:)` 而不是旧的 `.tabItem { }` API
7. 假设 `tabBarMinimizeBehavior` 在 iPad 上工作——它仅适用于 iPhone
8. 在多个地方处理深度链接——在路由器中集中 URL 解析
9. 硬编码页面尺寸——使用 `.presentationSizing(.form)` 代替
10. 路由器类缺少 `@MainActor`——Swift 6 并发安全要求

## Review Checklist

- [ ] 使用 `NavigationStack`（不是 `NavigationView`）
- [ ] 每个标签都有自己的 `NavigationStack` 和独立路径
- [ ] 路由枚举是 `Hashable` 并具有稳定的标识符
- [ ] `.navigationDestination(for:)` 映射所有路由类型
- [ ] `.sheet(item:)` 优先于 `.sheet(isPresented:)`
- [ ] 页面拥有自己的内部取消逻辑
- [ ] 路由器对象是 `@MainActor` 和 `@Observable`
- [ ] 深度链接 URL 在导航之前解析和验证
- [ ] 通用链接配置了 AASA 和 Associated Domains
- [ ] 标签选择使用 `Tab(value:)` with binding

## References

- NavigationStack 和路由模式：[参考资料/navigationstack.md](references/navigationstack.md)
- 页面呈现和路由：[参考资料/sheets.md](references/sheets.md)
- TabView 模式和 iOS 26 API：[参考资料/tabview.md](references/tabview.md)
- 深度链接、通用链接和 Handoff：[参考资料/deeplinks.md](references/deeplinks.md)
- 架构和状态管理：参见 `swiftui-patterns` 技能
- 布局和组件：参见 `swiftui-layout-components` 技能
