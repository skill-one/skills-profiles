---
name: swiftui-uikit-interop
description: 通过 `UIViewRepresentable`、`UIViewControllerRepresentable`、`UIHostingController`、`UIHostingConfiguration`、协调器代理以及 UIKit 自动观察跟踪共享的 `@Observable` 状态，实现 UIKit 和 SwiftUI 的桥接。适用于将 UIKit 唯一或第三方 UIKit 视图/控制器包装在 SwiftUI 中、将 SwiftUI 嵌入 UIKit、集成邮件/分享/文档/PDF/文本视图界面，或逐步将 UIKit 应用迁移到 SwiftUI。
---

# SwiftUI-UIKit 互操作

在两个方向上桥接 UIKit 和 SwiftUI：包装 UIKit 视图和控制器，在 UIKit 屏幕中嵌入 SwiftUI，并同步状态而无需重复生命周期所有权。

有关完整的包装配方，请参阅 [references/representable-recipes.md](references/representable-recipes.md)，有关 UIKit 到 SwiftUI 迁移模式的请参阅 [references/hosting-migration.md](references/hosting-migration.md)。

## 目录

- [UIViewRepresentable 协议](#uiviewrepresentable-protocol)
- [UIViewControllerRepresentable 协议](#uiviewcontrollerrepresentable-protocol)
- [协调者模式](#the-coordinator-pattern)
- [UIHostingController](#uihostingcontroller)
- [尺寸和布局](#sizing-and-layout)
- [状态同步模式](#state-synchronization-patterns)
- [UIKit 自动观察跟踪](#uikit-automatic-observation-tracking)
- [Sendable 考虑](#sendable-considerations)
- [常见错误](#common-mistakes)
- [审查清单](#review-checklist)
- [参考资料](#references)

## UIViewRepresentable 协议

使用 `UIViewRepresentable` 来包装任何 `UIView` 子类以用于 SwiftUI。

### 必要方法

```swift
struct WrappedTextView: UIViewRepresentable {
    @Binding var text: String

    func makeUIView(context: Context) -> UITextView {
        // 当 SwiftUI 将此视图插入层次结构时调用一次。
        // 创建并返回 UIKit 视图。一次性设置在这里。
        let textView = UITextView()
        textView.delegate = context.coordinator
        textView.font = .preferredFont(forTextStyle: .body)
        return textView
    }

    func updateUIView(_ uiView: UITextView, context: Context) {
        // 每次 SwiftUI 状态变化影响此视图时调用。
        // 将 SwiftUI 状态同步到 UIKit 视图。
        // 防止冗余更新以避免循环。
        if uiView.text != text {
            uiView.text = text
        }
    }
}
```

### 生命周期时机

| 方法 | 调用时 | 目的 |
|--------|-----------|---------|
| `makeCoordinator()` | 在 `makeUIView` 之前。每个可表示生命周期的实例。 | 创建委托/数据源引用类型。 |
| `makeUIView(context:)` | 一次，当可表示进入视图树时。 | 分配和配置 UIKit 视图。 |
| `updateUIView(_:context:)` | 立即调用 `makeUIView` 后，然后在每个相关状态变化时调用。 | 将 SwiftUI 状态推送到 UIKit 视图。 |
| `dismantleUIView(_:coordinator:)` | 当可表示从视图树中移除时。 | 清理观察者、计时器、订阅。 |
| `sizeThatFits(_:uiView:context:)` | 在布局期间，当 SwiftUI 需要视图的理想尺寸时。iOS 16+. | 返回自定义尺寸建议。 |

**为什么 `updateUIView` 是最重要的方法：** SwiftUI 每次读取可表示的任何 `@Binding`、`@State`、`@Environment` 或 `@Observable` 属性发生变化时都会调用它。所有从 SwiftUI 到 UIKit 的状态同步都发生在这里。如果你跳过某个属性，UIKit 视图将失去同步。

### 可选：dismantleUIView

```swift
static func dismantleUIView(_ uiView: UITextView, coordinator: Coordinator) {
    // 移除观察者、使计时器失效、取消订阅。
    // 传入协调者，以便你可以访问它上面存储的状态。
    coordinator.cancellables.removeAll()
}
```

### 可选：sizeThatFits (iOS 16+)

```swift
@available(iOS 16.0, *)
func sizeThatFits(
    _ proposal: ProposedViewSize,
    uiView: UITextView,
    context: Context
) -> CGSize? {
    // 返回 nil 以回退到 UIKit 的 intrinsicContentSize。
    // 返回一个 CGSize 以覆盖 SwiftUI 的此视图的尺寸。
    let width = proposal.width ?? UIView.layoutFittingExpandedSize.width
    let size = uiView.sizeThatFits(CGSize(width: width, height: .greatestFiniteMagnitude))
    return size
}
```

## UIViewControllerRepresentable 协议

使用 `UIViewControllerRepresentable` 来包装一个 `UIViewController` 子类——通常用于系统选择器、文档扫描仪、邮件撰写或任何模态呈现的控制器。

```swift
struct DocumentScannerView: UIViewControllerRepresentable {
    @Binding var scannedImages: [UIImage]
    @Environment(\.dismiss) private var dismiss

    func makeUIViewController(context: Context) -> VNDocumentCameraViewController {
        let scanner = VNDocumentCameraViewController()
        scanner.delegate = context.coordinator
        return scanner
    }

    func updateUIViewController(_ uiViewController: VNDocumentCameraViewController, context: Context) {
        // 对于模态控制器通常为空——没有需要从 SwiftUI 推送的内容。
    }

    func makeCoordinator() -> Coordinator { Coordinator(self) }
}
```

### 处理从呈现控制器返回的结果

协调者捕获委托回调，并通过父级的 `@Binding` 或闭包将结果路由回 SwiftUI：

```swift
extension DocumentScannerView {
    final class Coordinator: NSObject, VNDocumentCameraViewControllerDelegate {
        let parent: DocumentScannerView

        init(_ parent: DocumentScannerView) { self.parent = parent }

        func documentCameraViewController(
            _ controller: VNDocumentCameraViewController,
            didFinishWith scan: VNDocumentCameraScan
        ) {
            parent.scannedImages = (0..<scan.pageCount).map { scan.imageOfPage(at: $0) }
            parent.dismiss()
        }

        func documentCameraViewControllerDidCancel(_ controller: VNDocumentCameraViewController) {
            parent.dismiss()
        }

        func documentCameraViewController(
            _ controller: VNDocumentCameraViewController,
            didFailWithError error: Error
        ) {
            parent.dismiss()
        }
    }
}
```

## 协调者模式

### 协调者存在的原因

UIKit 委托、数据源和目标-动作模式需要引用类型 (`class`)。SwiftUI 可表示的结构是值类型，不能作为委托。协调者是一个 `class` 实例，由 SwiftUI 创建和管理——它的生命周期与可表示视图相同。

### 结构

始终将协调者嵌套在可表示中或在扩展中。存储对 `parent`（可表示的结构）的引用，以便协调者可以写回 `@Binding` 属性。

```swift
struct SearchBarView: UIViewRepresentable {
    @Binding var text: String
    var onSearch: (String) -> Void

    func makeCoordinator() -> Coordinator { Coordinator(self) }

    func makeUIView(context: Context) -> UISearchBar {
        let bar = UISearchBar()
        bar.delegate = context.coordinator  // 在这里设置委托，而不是在 updateUIView 中
        return bar
    }

    func updateUIView(_ uiView: UISearchBar, context: Context) {
        context.coordinator.parent = self

        if uiView.text != text {
            uiView.text = text
        }
    }

    final class Coordinator: NSObject, UISearchBarDelegate {
        var parent: SearchBarView

        init(_ parent: SearchBarView) { self.parent = parent }

        func searchBar(_ searchBar: UISearchBar, textDidChange searchText: String) {
            parent.text = searchText
        }

        func searchBarSearchButtonClicked(_ searchBar: UISearchBar) {
            parent.onSearch(parent.text)
            searchBar.resignFirstResponder()
        }
    }
}
```

### 关键规则

1. **在 `makeUIView`/`makeUIViewController` 中设置委托，绝不在 `updateUIView` 中。** 更新方法可以多次运行以响应影响所表示视图的状态变化——在更新方法中设置委托会导致冗余分配并可能触发意外的副作用。

2. **自己刷新复制的父状态。** 如果协调者在 `var parent` 中存储了可表示，在 `updateUIView` 或 `updateUIViewController` 的开始处分配 `context.coordinator.parent = self`。绑定仍然指向其真实来源，但闭包和非绑定值被复制到协调者中。

3. **在闭包中使用 `[weak coordinator]`** 以避免协调者和捕获它的 UIKit 对象之间的保留循环。

## UIHostingController

使用 `UIHostingController` 将 SwiftUI 视图嵌入 UIKit 视图控制器中。

### 基本嵌入

```swift
final class ProfileViewController: UIViewController {
    private let hostingController = UIHostingController(rootView: ProfileView())

    override func viewDidLoad() {
        super.viewDidLoad()

        // 1. 添加为子视图
        addChild(hostingController)

        // 2. 添加并约束视图
        hostingController.view.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(hostingController.view)
        NSLayoutConstraint.activate([
            hostingController.view.topAnchor.constraint(equalTo: view.topAnchor),
            hostingController.view.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            hostingController.view.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            hostingController.view.bottomAnchor.constraint(equalTo: view.bottomAnchor),
        ])

        // 3. 通知子视图
        hostingController.didMove(toParent: self)
    }
}
```

这三个步骤（addChild、添加视图、didMove）是强制性的。跳过任何步骤都会导致包含回调错误，这将破坏外观过渡和特征传播。

### 尺寸选项 (iOS 16+)

```swift
@available(iOS 16.0, *)
hostingController.sizingOptions = [.intrinsicContentSize]
```

| 选项 | 效果 |
|--------|--------|
| `.intrinsicContentSize` | 包含控制器的视图将其 SwiftUI 内容尺寸报告为 `intrinsicContentSize`。在 Auto Layout 中使用时，如果托管视图应自行调整大小，请使用。 |
| `.preferredContentSize` | 更新 `preferredContentSize` 以匹配 SwiftUI 内容。在作为弹出窗口或表单表单呈现时使用。 |

### 更新根视图

当 UIKit 中的数据发生变化时，将新状态推送到托管 SwiftUI 视图：

```swift
func updateProfile(_ profile: Profile) {
    hostingController.rootView = ProfileView(profile: profile)
}
```

对于可观察模型，传递一个 `@Observable` 对象，SwiftUI 将自动跟踪更改——无需重新分配 `rootView`。

### UIHostingConfiguration (iOS 16+)

直接在 `UICollectionViewCell` 或 `UITableViewCell` 中渲染 SwiftUI 内容，而无需管理子级包含控制器：

```swift
@available(iOS 16.0, *)
func collectionView(
    _ collectionView: UICollectionView,
    cellForItemAt indexPath: IndexPath
) -> UICollectionViewCell {
    let cell = collectionView.dequeueReusableCell(withReuseIdentifier: "cell", for: indexPath)
    cell.contentConfiguration = UIHostingConfiguration {
        ItemRow(item: items[indexPath.item])
    }
    return cell
}
```

## 尺寸和布局

### intrinsicContentSize 桥接

在 `UIViewRepresentable` 中包装的 UIKit 视图通过 `intrinsicContentSize` 向 SwiftUI 传达其自然尺寸。除非被 `frame()` 或 `fixedSize()` 覆盖，否则 SwiftUI 在布局期间会尊重此值。

### SwiftUI拥有的几何形状

SwiftUI拥有所表示视图的 `center`、`bounds`、`frame` 和 `transform`。不要在 `makeUIView` 或 `updateUIView` 中直接在 `uiView` 上设置这些属性。使用 `sizeThatFits`、内在内容尺寸、SwiftUI布局修饰符或自定义 UIKit 子视图中的布局代码来处理内部子图层。

### fixedSize() 和 frame() 交互

| SwiftUI 修饰符 | 对可表示的影响 |
|-----------------|-----------------|
| 无修饰符 | SwiftUI 使用 `intrinsicContentSize` 作为理想尺寸；视图是灵活的。 |
| `.fixedSize()` | 强制可表示在两个轴上均为其理想（内在）尺寸。 |
| `.fixedSize(horizontal: true, vertical: false)` | 宽度固定为内在；高度保持灵活。 |
| `.frame(width:height:)` | 覆盖建议尺寸；UIKit 视图接收此尺寸。 |

### Auto Layout with UIHostingController

当将 `UIHostingController` 作为子视图嵌入时，使用约束固定其视图。使用 `.sizingOptions = [.intrinsicContentSize]`，以便 Auto Layout 可以查询 SwiftUI 内容的自然尺寸，以用于自定尺寸的单元格或可变高度的章节。

## 状态同步模式

### `@Binding`：双向同步 (SwiftUI <-> UIKit)

当双方都读取和写入相同值时，请使用 `@Binding`。协调者在委托回调中写入 `parent.bindingProperty`；`updateUIView` 读取绑定并将其推送到 UIKit 视图。

```swift
// SwiftUI -> UIKit: 在 updateUIView 中
if uiView.text != text { uiView.text = text }

// UIKit -> SwiftUI: 在 Coordinator 委托方法中
func textViewDidChange(_ textView: UITextView) {
    parent.text = textView.text
}
```

### 闭包：单向事件 (UIKit -> SwiftUI)

对于一次性事件（按钮点击、搜索提交、扫描完成），传递闭包而不是绑定：

```swift
struct WebViewWrapper: UIViewRepresentable {
    let url: URL
    var onNavigationFinished: ((URL) -> Void)?
}
```

### 环境值

通过 `context.environment` 在可表示方法中访问 SwiftUI 环境值：

```swift
func updateUIView(_ uiView: UITextView, context: Context) {
    let isEnabled = context.environment.isEnabled
    uiView.isEditable = isEnabled

    // 响应配色方案变化
    let colorScheme = context.environment.colorScheme
    uiView.backgroundColor = colorScheme == .dark ? .systemGray6 : .white
}
```

### 避免更新循环

`updateUIView` 在 SwiftUI 有新状态时被调用——包括由协调者写入 `@Binding` 触发的更改。使用守卫防止冗余更新以防止无限循环：

```swift
func updateUIView(_ uiView: UITextView, context: Context) {
    // 守卫：只有值实际不同时才更新
    if uiView.text != text {
        uiView.text = text
    }
}
```

如果没有守卫，设置 `uiView.text` 可能会触发委托的 `textViewDidChange`，这会写入 `parent.text`，这会再次触发 `updateUIView`。

## UIKit 自动观察跟踪

对于共享 `@Observable` 模型的 UIKit 屏幕，保持 UIKit 屏幕，并从 UIKit 的跟踪更新钩子中读取观察状态：

- iOS 26+: 使用 `updateProperties()` 为标签、颜色、可见性、启用状态和其他非布局 UI；使用布局钩子为几何形状；使用单元格配置更新处理程序为单元格。
- iOS 18: 自动 UIKit 跟踪需要在 `Info.plist` 中设置 `UIObservationTrackingEnabled`。
- iOS 17: `@Observable` 存在，但 UIKit 自动观察跟踪不可用。手动 `withObservationTracking` 是一次性；不要围绕它构建轮询循环。
- iOS 15-16 或现有的 `ObservableObject`：使用 Combine `objectWillChange`、委托、通知或显式回调。

有关迁移模式的详细信息，请参阅 [references/hosting-migration.md](references/hosting-migration.md#automatic-observation-tracking-in-uikit)。

## Sendable 考虑

UIKit 委托协议不是 `Sendable`。当协调者符合 UIKit 委托时，它会从 UIKit 继承主线程隔离。将协调者标记为 `@MainActor` 或仅对确实不接触 UIKit 状态的方法使用 `nonisolated`。在 Swift 6 严格并发中：

```swift
@MainActor
final class Coordinator: NSObject, UISearchBarDelegate {
    var parent: SearchBarView
    init(_ parent: SearchBarView) { self.parent = parent }
    // 委托方法是主线程隔离的——可以安全地访问 UIKit 和 @Binding。
}
```

如果跨隔离边界传递闭包，请确保它们是 `@Sendable` 或在正确的线程上捕获。

| 错误 | 修复 |
|---|---|
| UIKit 对象或代理在 `update*` 中被重新创建 | 在 `make*` 中创建一次；仅更新改变的 state。 |
| 代表的 frame/bounds/transform 直接被修改 | 让 SwiftUI 控制尺寸；使用内置尺寸、`sizeThatFits`、修饰符或内部布局。 |
| UIKit 闭包保留 Coordinator | 弱引用捕获它，并保持一个生命周期所有者。 |
| Picker/控制器退出路径缺少撤销或完成 | 通过一个 Coordinator 清理路径路由每个委托退出。 |
| 观察者、计时器或订阅比视图存活时间更长 | 在 `dismantle*` 中移除/取消它们。 |
| Hosting controller 使用手动 frame 而没有包含 | 使用 Auto Layout 和 `addChild`/`didMove(toParent:)`。 |
| `@State` 在 Coordinator 内部使用 | 使用存储属性并通过绑定/回调进行通信。 |
| `withObservationTracking` 被手动轮询 | 在可用的情况下使用 UIKit 自动观察钩子，或在较旧的版本上显式无效化。 |

## 审查清单

- [ ] 视图/控制器在 `make*` 中创建，而不是 `update*`
- [ ] Coordinator 在 `make*` 中作为委托设置，而不是 `update*`
- [ ] 使用 `@Binding` 进行双向状态同步
- [ ] `updateUIView` 处理所有 SwiftUI 状态变化并带有冗余保护
- [ ] `dismantleUIView` 如果需要则清理观察者/计时器
- [ ] Coordinator 和闭包之间没有 retain 循环 (`[weak coordinator]`)
- [ ] `UIHostingController` 正确添加为子视图 (`addChild` + `didMove(toParent:)`)
- [ ] 选择尺寸策略 (`intrinsicContentSize` vs 固定 `frame` vs `sizeThatFits`)
- [ ] 代表的视图几何形状留给 SwiftUI (`frame`, `bounds`, `center`, `transform` 不直接被修改)
- [ ] 在需要的地方通过 `context.environment` 在 `updateUIView` 中读取环境值
- [ ] UIKit `@Observable` 在 iOS 18+/26+ 上使用自动跟踪钩子，而不是轮询；iOS 17 仅手动单次
- [ ] Coordinator 标记为 `@MainActor` 以确保并发严格性
- [ ] 模态控制器在所有委托退出路径中撤销（成功、取消、错误）
- [ ] 使用 `UIHostingConfiguration` 为集合/表格视图单元格提供托管，而不是手动托管（iOS 16+）

## 参考

- 包装配方：[references/representable-recipes.md](references/representable-recipes.md)
- 迁移模式：[references/hosting-migration.md](references/hosting-migration.md)
- Apple 文档：[UIViewRepresentable](https://sosumi.ai/documentation/swiftui/UIViewRepresentable)
- Apple 文档：[UIViewControllerRepresentable](https://sosumi.ai/documentation/swiftui/UIViewControllerRepresentable)
- Apple 文档：[UIHostingController](https://sosumi.ai/documentation/swiftui/UIHostingController)
