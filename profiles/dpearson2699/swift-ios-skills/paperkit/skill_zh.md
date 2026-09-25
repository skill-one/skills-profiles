# PaperKit

> **Beta-sensitive。** PaperKit 是 iOS/iPadOS 26、macOS 26 和 visionOS 26 中的新功能。API 表面可能发生变化。在发布前，请参考当前的 Apple 文档进行核实。

PaperKit 将 PencilKit 绘图与结构化的标记元素（如形状、文本、图像和线条）结合，并在由 `PaperMarkupViewController` 管理的画布上呈现。

## 内容

- [设置](#设置)
- [工作流](#工作流)
- [PaperMarkupViewController](#papermarkupviewcontroller)
- [PaperMarkup 数据模型](#papermarkup-data-model)
- [插入控制器](#插入控制器)
- [FeatureSet 配置](#featureset-configuration)
- [与 PencilKit 集成](#integration-with-pencilkit)
- [SwiftUI 集成](#swiftui-integration)
- [常见错误](#common-mistakes)
- [审查清单](#review-checklist)
- [参考资料](#references)

## 工作流

1.  在构建 UI 之前，选择文档边界、支持的 `FeatureSet` 和持久化版本。
2.  创建 `PaperMarkup`，嵌入 `PaperMarkupViewController`，并保持控制器、工具选择器和插入控制器在视图生命周期内保持活跃。
3.  使用平台适当的插入表面，并将 PencilKit 绘图保持在 PaperKit 文档边界内。
4.  在主线程外保存，为向前不兼容的内容保留缩略图，并使用相同的特征集测试往返加载。
5.  在失败时，恢复原始文档字节，修复特征集/版本/控制器不匹配，并重新运行编辑、保存、重新启动、加载、缩略图回退和撤销检查。

加载 [参考资料/paperkit-patterns.md](references/paperkit-patterns.md) 获取完整平台设置、工具选择器连接、持久化、缩略图、自定义特征集、程序化构建和迁移。

## 设置

PaperKit 不需要任何权限或特殊的 Info.plist 条目。

```swift
import PaperKit
```

**平台可用性：** iOS 26.0+、iPadOS 26.0+、Mac Catalyst 26.0+、macOS 26.0+、visionOS 26.0+。

三个核心组件：

| 组件 | 角色 |
|---|---|
| `PaperMarkupViewController` | 用于创建和显示标记和绘图的交互式画布 |
| `PaperMarkup` | 用于序列化所有标记元素和 PencilKit 绘图的数据模型 |
| `MarkupEditViewController` / `MarkupToolbarViewController` | 用于添加标记元素的插入 UI |

## PaperMarkupViewController

交互式标记的主要视图控制器。提供一个可滚动的画布，用于自由形式的 PencilKit 绘图和结构化的标记元素。遵循 `Observable` 和 `PKToolPickerObserver`。

### 基本 UIKit 设置

```swift
import PaperKit
import PencilKit
import UIKit

class MarkupViewController: UIViewController, PaperMarkupViewController.Delegate {
    var paperVC: PaperMarkupViewController!
    var toolPicker: PKToolPicker!

    override func viewDidLoad() {
        super.viewDidLoad()

        let pageBounds = CGRect(origin: .zero, size: CGSize(width: 612, height: 792))
        let markup = PaperMarkup(bounds: pageBounds)
        let features = FeatureSet.latest

        paperVC = PaperMarkupViewController(
            markup: markup,
            supportedFeatureSet: features
        )
        paperVC.delegate = self

        addChild(paperVC)
        paperVC.view.frame = view.bounds
        paperVC.view.autoresizingMask = [.flexibleWidth, .flexibleHeight]
        view.addSubview(paperVC.view)
        paperVC.didMove(toParent: self)

        toolPicker = PKToolPicker()
        toolPicker.addObserver(paperVC)
        paperVC.pencilKitResponderState.activeToolPicker = toolPicker
        paperVC.pencilKitResponderState.toolPickerVisibility = .visible
    }

    func paperMarkupViewControllerDidChangeMarkup(
        _ controller: PaperMarkupViewController
    ) {
        guard let markup = controller.markup else { return }
        Task { try await save(markup) }
    }
}
```

### 关键属性

| 属性 | 类型 | 描述 |
|---|---|---|
| `markup` | `PaperMarkup?` | 当前数据模型 |
| `selectedMarkup` | `PaperMarkup` | 当前选中的内容 |
| `isEditable` | `Bool` | 画布是否接受输入 |
| `isRulerActive` | `Bool` | 是否显示标尺覆盖层 |
| `drawingTool` | `any PKTool` | 活动的 PencilKit 绘图工具 |
| `contentView` | `UIView?` / `NSView?` | 在标记下方渲染的背景视图 |
| `zoomRange` | `ClosedRange<CGFloat>` | 最小/最大缩放比例 |
| `supportedFeatureSet` | `FeatureSet` | 启用的 PaperKit 功能 |

### 触摸模式

`PaperMarkupViewController.TouchMode` 有两个情况：`.drawing` 和 `.selection`。

```swift
paperVC.directTouchMode = .drawing    // 指尖绘制
paperVC.directTouchMode = .selection  // 指尖选择元素
paperVC.directTouchAutomaticallyDraws = true  // 系统根据 Pencil 状态决定
```

### 内容背景

为模板、文档页面或待注释的图像设置任何视图在标记层下方。保持 `PaperMarkup(bounds:)` 坐标空间与背景内容（如 PDF 页面或渲染图像大小）对齐，以便保存的注释在正确位置恢复：

```swift
let pageBounds = CGRect(origin: .zero, size: pageImage.size)
let imageView = UIImageView(image: pageImage)
imageView.frame = pageBounds

let markup = PaperMarkup(bounds: pageBounds)
paperVC = PaperMarkupViewController(markup: markup, supportedFeatureSet: features)
paperVC.contentView = imageView
```

### Delegate 回调

| 方法 | 调用时 |
|---|---|
| `paperMarkupViewControllerDidChangeMarkup(_:)` | 标记内容发生变化 |
| `paperMarkupViewControllerDidBeginDrawing(_:)` | 用户开始绘图 |
| `paperMarkupViewControllerDidChangeSelection(_:)` | 选择发生变化 |
| `paperMarkupViewControllerDidChangeContentVisibleFrame(_:)` | 可见帧发生变化 |

## PaperMarkup 数据模型

`PaperMarkup` 是一个 `Sendable` 结构体，存储所有标记元素和 PencilKit 绘图数据。

### 创建和持久化

```swift
// 新的空模型。边界定义了保存文档的坐标空间。
let markup = PaperMarkup(bounds: CGRect(x: 0, y: 0, width: 612, height: 792))

// 从保存的数据加载
let markup = try PaperMarkup(dataRepresentation: savedData)

// 保存 — dataRepresentation() 是异步的
func save(_ markup: PaperMarkup) async throws {
    let data = try await markup.dataRepresentation()
    try data.write(to: fileURL)
}
```

### 程序化插入内容

```swift
// 文本框
markup.insertNewTextbox(
    attributedText: AttributedString("注释"),
    frame: CGRect(x: 50, y: 100, width: 200, height: 40),
    rotation: 0
)

// 图像
markup.insertNewImage(cgImage, frame: CGRect(x: 50, y: 200, width: 300, height: 200), rotation: 0)

// 形状
let shapeConfig = ShapeConfiguration(
    type: .rectangle,
    fillColor: UIColor.systemBlue.withAlphaComponent(0.2).cgColor,
    strokeColor: UIColor.systemBlue.cgColor,
    lineWidth: 2
)
markup.insertNewShape(configuration: shapeConfig, frame: CGRect(x: 50, y: 420, width: 200, height: 100), rotation: 0)

// 带箭头端标记的线条
let lineConfig = ShapeConfiguration(type: .line, fillColor: nil, strokeColor: UIColor.red.cgColor, lineWidth: 3)
markup.insertNewLine(
    configuration: lineConfig,
    from: CGPoint(x: 50, y: 550), to: CGPoint(x: 250, y: 550),
    startMarker: false, endMarker: true
)
```

形状类型：`.rectangle`、`.roundedRectangle`、`.ellipse`、`.line`、`.arrowShape`、`.star`、`.chatBubble`、`.regularPolygon`。

### 其他操作

```swift
markup.append(contentsOf: otherMarkup)       // 合并另一个 PaperMarkup
markup.append(contentsOf: pkDrawing)          // 合并一个 PKDrawing
markup.transformContent(CGAffineTransform(...)) // 应用仿射变换
markup.removeContentUnsupported(by: featureSet) // 移除不支持的元素
```

| 属性 | 描述 |
|---|---|
| `bounds` | 标记的坐标空间 |
| `contentsRenderFrame` | 所有内容的最小边界框 |
| `featureSet` | 此数据模型内容使用的功能 |
| `indexableContent` | 可提取的文本，用于搜索索引 |

使用视图控制器的 `suggestedFrameForInserting(contentInFrame:)` 获取一个避免与现有内容重叠的帧。

## 插入控制器

### MarkupEditViewController (iOS、iPadOS、Mac Catalyst、visionOS)

显示一个弹出菜单，用于插入形状、文本框、线条和其他元素。

```swift
func showInsertionMenu(from barButtonItem: UIBarButtonItem) {
    let editVC = MarkupEditViewController(
        supportedFeatureSet: paperVC.supportedFeatureSet,
        additionalActions: []
    )
    editVC.delegate = paperVC  // PaperMarkupViewController 遵循委托
    editVC.modalPresentationStyle = .popover
    editVC.popoverPresentationController?.barButtonItem = barButtonItem
    present(editVC, animated: true)
}
```

### MarkupToolbarViewController (macOS、Mac Catalyst)

提供一个包含绘图工具和插入按钮的工具栏。用于原生 macOS 和 Mac Catalyst 工具栏式 UI；希望使用 UIKit 弹出菜单的 Catalyst 应用可以使用 `MarkupEditViewController`。

```swift
let toolbar = MarkupToolbarViewController(supportedFeatureSet: paperVC.supportedFeatureSet)
toolbar.delegate = paperVC
addChild(toolbar)
toolbar.view.frame = toolbarContainerView.bounds
toolbarContainerView.addSubview(toolbar.view)
toolbar.didMove(toParent: self)
```

两个控制器必须使用与 `PaperMarkupViewController` 相同的 `FeatureSet`。

## FeatureSet 配置

`FeatureSet` 控制哪些标记功能可用。

| 预设 | 描述 |
|---|---|
| `.latest` | 所有当前功能 — 推荐的起始点 |
| `.version1` | 版本 1 的功能 |
| `.empty` | 未启用任何功能 |

### 自定义

```swift
var features = FeatureSet.latest
features.remove(.stickers)
features.remove(.images)

// 或者从空构建
var features = FeatureSet.empty
features.insert(.drawing)
features.insert(.text)
features.insert(.shapeStrokes)
```

### 可用功能

| 功能 | 描述 |
|---|---|
| `.drawing` | 自由形式的 PencilKit 绘图 |
| `.text` | 文本框插入 |
| `.images` | 图像插入 |
| `.stickers` | 贴纸插入 |
| `.links` | 链接注释 |
| `.loupes` | loupe/放大镜元素 |
| `.shapeStrokes` | 形状轮廓 |
| `.shapeFills` | 形状填充 |
| `.shapeOpacity` | 形状不透明度控制 |

### HDR 支持

在 `FeatureSet` 和 `PKToolPicker` 上将 `colorMaximumLinearExposure` 设置为 `1.0` 以上：

```swift
var features = FeatureSet.latest
features.colorMaximumLinearExposure = 4.0
toolPicker.colorMaximumLinearExposure = features.colorMaximumLinearExposure
```

使用 `view.window?.windowScene?.screen.potentialEDRHeadroom` 匹配设备屏幕的能力。使用 `1.0` 仅用于 SDR。

### 形状、墨水和线条标记

```swift
features.shapes = [.rectangle, .ellipse, .arrowShape, .line]
features.inks = [.pen, .pencil, .marker]
features.lineMarkerPositions = .all  // .single、.double、.plain 或 .all
```

## 与 PencilKit 集成

PaperKit 接受 `PKTool` 用于绘图，并可以追加 `PKDrawing` 内容。

PaperKit 不是一个低级别的 `PKCanvasView` 的即插即用替代品，当应用程序依赖于自定义笔刷行为、原始 `PKDrawing` / `PKStroke` 分析或以套索为中心的自定义编辑时。保留那些由 PencilKit 拥有的工作流，并在它们旁边添加 PaperKit 以用于结构化的审查标记，如标注、箭头、文本框、标签、图像戳和系统标准的插入 UI。仅在低级别编辑路径不再需要拥有该内容时，才将现有绘图迁移或复制到 PaperKit 注释层，使用 `PaperMarkup.append(contentsOf: PKDrawing)`。

```swift
import PencilKit

// 设置绘图工具
paperVC.drawingTool = PKInkingTool(.pen, color: .black, width: 3)

// 合并现有的 PKDrawing 到标记
markup.append(contentsOf: existingPKDrawing)
```

### 工具选择器设置

```swift
let toolPicker = PKToolPicker()
toolPicker.addObserver(paperVC)
paperVC.pencilKitResponderState.activeToolPicker = toolPicker
paperVC.pencilKitResponderState.toolPickerVisibility = .visible
```

将 `toolPickerVisibility` 设置为 `.hidden` 可以保持选择器的功能（响应 Pencil 手势）但不显示，从而启用迷你工具选择器体验。

### 内容版本兼容性

`FeatureSet.ContentVersion` 映射到 `PKContentVersion`：

```swift
let pkVersion = features.contentVersion.pencilKitContentVersion
```

## SwiftUI 集成

将 `PaperMarkupViewController` 包裹在 `UIViewControllerRepresentable` 中：

```swift
struct MarkupView: UIViewControllerRepresentable {
    @Binding var markup: PaperMarkup
    let features: FeatureSet

    func makeUIViewController(context: Context) -> PaperMarkupViewController {
        let vc = PaperMarkupViewController(markup: markup, supportedFeatureSet: features)
        vc.delegate = context.coordinator
        let toolPicker = PKToolPicker()
        toolPicker.addObserver(vc)
        vc.pencilKitResponderState.activeToolPicker = toolPicker
        vc.pencilKitResponderState.toolPickerVisibility = .visible
        context.coordinator.toolPicker = toolPicker
        return vc
    }

    func updateUIViewController(_ vc: PaperMarkupViewController, context: Context) {
        if vc.markup != markup { vc.markup = markup }
    }

    func makeCoordinator() -> Coordinator { Coordinator(parent: self) }

    class Coordinator: NSObject, PaperMarkupViewController.Delegate {
        let parent: MarkupView
        var toolPicker: PKToolPicker?
        init(parent: MarkupView) { self.parent = parent }

        func paperMarkupViewControllerDidChangeMarkup(
            _ controller: PaperMarkupViewController
        ) {
            if let markup = controller.markup { parent.markup = markup }
        }
    }
}
```

在创建 SwiftUI 桥接之前，从文档或页面大小初始化绑定的 `PaperMarkup`：

```swift
struct DocumentMarkupScreen: View {
    let pageSize: CGSize
    @State private var markup: PaperMarkup
    private let features = FeatureSet.latest

    init(pageSize: CGSize) {
        self.pageSize = pageSize
        _markup = State(
            initialValue: PaperMarkup(
                bounds: CGRect(origin: .zero, size: pageSize)
            )
        )
    }

    var body: some View {
        MarkupView(markup: $markup, features: features)
    }
}
```

## 常见错误

| 错误 | 修复 |
|---|---|
| 视图、插入 UI 和保存的文档使用不匹配的特征集 | 选择一个支持的 `FeatureSet` 并在整个编辑会话中使用它。 |
| 加载的内容未进行版本检查就分配 | 验证 `markup.featureSet.isSubset(of: supportedFeatureSet)` 或显示保存的缩略图/回退。 |
| 序列化阻塞 UI 或不安全重叠 | 在交互路径外异步调用 `dataRepresentation()` 并防抖自动保存。 |
| 工具选择器是局部变量 | 为控制器/视图生命周期保留它。 |
| 平台不正确的插入表面 | 在 macOS 上使用 `MarkupToolbarViewController`；在 UIKit 上使用 `MarkupEditViewController`，Catalyst 支持任一呈现方式。 |

## 审查清单

- [ ] `import PaperKit` 存在；部署目标是 iOS 26+ / macOS 26+ / visionOS 26+
- [ ] `PaperMarkup` 使用与内容大小匹配的边界初始化
- [ ] `PaperMarkupViewController` 和插入控制器使用相同的 `FeatureSet`
- [ ] 在异步上下文中调用 `dataRepresentation()`
- [ ] 将 `PKToolPicker` 作为存储属性保留
- [ ] 在 `PaperMarkupViewController` 上设置委托以接收更改回调
- [ ] 加载保存的数据时检查内容版本
- [ ] 根据平台使用正确的插入控制器（`MarkupToolbarViewController` 用于 macOS/Catalyst 工具栏 UI；`MarkupEditViewController` 用于 UIKit/Catalyst 弹出菜单）
- [ ] `MarkupError` 情况在反序列化时处理
- [ ] HDR：在 `FeatureSet` 和 `PKToolPicker.colorMaximumLinearExposure` 上设置 `colorMaximumLinearExposure` 为 `1.0` 以上

## 参考资料

- [PaperKit 文档](https://sosumi.ai/documentation/paperkit)
- [将 PaperKit 集成到您的应用程序中](https://sosumi.ai/documentation/paperkit/getting-started-with-paperkit)
- [认识 PaperKit — WWDC25](https://sosumi.ai/videos/play/wwdc2025/285/)
- `pencilkit` 技能涵盖 PencilKit 绘图、工具选择器和 PKDrawing 序列化
- [参考资料/paperkit-patterns.md](references/paperkit-patterns.md) — 数据持久化、渲染、多平台设置、自定义特征集
