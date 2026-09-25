# PencilKit

使用 `PKCanvasView` 捕获 Apple Pencil 和手指输入，使用 `PKToolPicker` 管理绘图工具，使用 `PKDrawing` 序列化绘图，并将 PencilKit 封装在 SwiftUI 中。

## 目录

- [设置](#设置)
- [捕获到导出工作流](#捕获到导出工作流)
- [PKCanvasView 基础](#pkcanvasview-basics)
- [PKToolPicker](#pktoolpicker)
- [PKDrawing 序列化](#pkdrawing-serialization)
- [内容版本兼容性](#内容版本兼容性)
- [导出到图像](#导出到图像)
- [笔迹检查](#笔迹检查)
- [SwiftUI 集成](#swiftui-integration)
- [PaperKit 关系](#paperkit-关系)
- [常见错误](#常见错误)
- [审查清单](#审查清单)
- [参考资料](#参考资料)

## 设置

PencilKit 不需要任何权限或 Info.plist 条目。导入 `PencilKit` 并创建一个 `PKCanvasView`。

```swift
import PencilKit
```

**平台可用性：** iOS 13+、iPadOS 13+、Mac Catalyst 13.1+、visionOS 1.0+。

## 捕获到导出工作流

1. **捕获：** 从 `canvasView.drawing` 读取，`canvasViewDrawingDidChange(_:)`；保留先前的持久化版本，直到新版本完成剩余检查点。
2. **序列化：** 创建 `dataRepresentation()`，原子写入，并运行 [解码验证/修复/重试循环](#解码验证修复重试循环)。当 `PKDrawing(data:)` 仍然抛出时，不要标记字节有效。
3. **版本门控：** 在可编辑同步之前应用 [内容版本兼容性](#内容版本兼容性)。如果接收者无法加载绘图，保留完整保真度的源，并使用现有的兼容回退或只读预览。
4. **同步：** 仅发送验证的、兼容的数据，并在确认后标记版本已同步。在传输或冲突失败时，保留待处理的版本，解决原因，并重试而不丢弃最后一个好的副本。
5. **导出：** 在调用 `image(from:scale:)` 之前验证非空绘图区域和预期比例；在无效边界上跳过导出而不更改序列化绘图。

## PKCanvasView 基础

`PKCanvasView` 是一个 `UIScrollView` 子类，捕获 Apple Pencil 和手指输入并渲染笔迹。

```swift
import PencilKit
import UIKit

class DrawingViewController: UIViewController, PKCanvasViewDelegate {
    let canvasView = PKCanvasView()

    override func viewDidLoad() {
        super.viewDidLoad()
        canvasView.delegate = self
        canvasView.drawingPolicy = .anyInput
        canvasView.tool = PKInkingTool(.pen, color: .black, width: 5)
        canvasView.frame = view.bounds
        canvasView.autoresizingMask = [.flexibleWidth, .flexibleHeight]
        view.addSubview(canvasView)
    }

    func canvasViewDrawingDidChange(_ canvasView: PKCanvasView) {
        // 绘图已更改 -- 保存或处理
    }
}
```

### 绘图策略

| 策略 | 行为 |
|---|---|
| `.default` | 当工具选择器可见时，尊重 `UIPencilInteraction.prefersPencilOnlyDrawing`；否则仅铅笔 |
| `.anyInput` | 铅笔和手指都绘图 |
| `.pencilOnly` | 仅 Apple Pencil 触摸在画布上绘图 |

```swift
canvasView.drawingPolicy = .pencilOnly
```

当工具选择器的绘图策略控制应遵循用户的铅笔偏好时，使用 `.default` 用于系统标准的铅笔优先画布。使用 `.anyInput` 用于签名垫、白板或显式的手指绘图模式。使用 `.pencilOnly` 当手指输入永远不会创建笔迹时。

### 配置画布

```swift
// 设置大型绘图区域（可滚动）
canvasView.contentSize = CGSize(width: 2000, height: 3000)

// 启用/禁用标尺
canvasView.isRulerActive = true

// 逐行编程设置当前工具
canvasView.tool = PKInkingTool(.pencil, color: .blue, width: 3)
canvasView.tool = PKEraserTool(.vector)
```

## PKToolPicker

`PKToolPicker` 显示一个浮动的绘图工具面板。画布自动采用选定的工具。

```swift
class DrawingViewController: UIViewController {
    let canvasView = PKCanvasView()
    let toolPicker = PKToolPicker()

    override func viewDidAppear(_ animated: Bool) {
        super.viewDidAppear(animated)
        toolPicker.addObserver(canvasView)
        toolPicker.setVisible(true, forFirstResponder: canvasView)
        canvasView.becomeFirstResponder()
    }
}
```

### 自定义工具选择器项

使用特定工具创建工具选择器。`PKToolPicker(toolItems:)` 和自定义工具选择器项类需要 iOS/iPadOS 18+、Mac Catalyst 18+ 和 visionOS 2+；这些项类从 macOS 26 开始在 macOS 上可用。

```swift
let toolPicker = PKToolPicker(toolItems: [
    PKToolPickerInkingItem(type: .pen, color: .black, width: 5),
    PKToolPickerInkingItem(type: .pencil, color: .gray, width: 5),
    PKToolPickerInkingItem(type: .marker, color: .yellow, width: 12),
    PKToolPickerEraserItem(type: .vector),
    PKToolPickerLassoItem(),
    PKToolPickerRulerItem()
])
```

### 墨水类型

| 类型 | 描述 |
|---|---|
| `.pen` | 平滑、压力敏感的笔 |
| `.pencil` | 带有倾斜阴影的纹理铅笔 |
| `.marker` | 半透明的荧光笔 |
| `.monoline` | 统一宽度的笔 |
| `.fountainPen` | 可变宽度的书法笔 |
| `.watercolor` | 可混合的水彩笔刷 |
| `.crayon` | 纹理蜡笔 |
| `.reed` | 竹笔（iOS/iPadOS/macOS/visionOS 26+） |

### 内容版本

使用 [内容版本兼容性](#内容版本兼容性) 作为画布和工具选择器的单一版本映射和兼容性门控。

## PKDrawing 序列化

`PKDrawing` 是一个值类型（结构体），包含所有笔迹数据。将其序列化为 `Data` 以进行持久化。

```swift
// 保存
func saveDrawing(_ drawing: PKDrawing) throws {
    let data = drawing.dataRepresentation()
    try data.write(to: fileURL, options: .atomic)
}

// 加载
func loadDrawing() throws -> PKDrawing {
    let data = try Data(contentsOf: fileURL)
    return try PKDrawing(data: data)
}
```

### 解码验证/修复/重试循环

对于同步或用户提供的数据：**验证** 使用 `PKDrawing(data:)`；在失败时保留原始字节并**修复**原因，通过重新获取完整版本或选择先前生成的兼容副本；然后**重试**解码。仅在成功重试后分配绘图。如果恢复仍然失败，保留源不变，并显示错误或可用的只读预览，而不是使用 `try?` 抑制失败。

```swift
do {
    canvasView.drawing = try PKDrawing(data: correctedData) // 重试
} catch {
    showReadOnlyPreview(for: document, loadError: error)
}
```

### 组合绘图

```swift
var drawing1 = PKDrawing()
let drawing2 = PKDrawing()
drawing1.append(drawing2)

// 非突变
let combined = drawing1.appending(drawing2)
```

### 变换绘图

```swift
let scaled = drawing.transformed(using: CGAffineTransform(scaleX: 2, y: 2))
let translated = drawing.transformed(using: CGAffineTransform(translationX: 100, y: 0))
```

## 内容版本兼容性

对于同步、迁移、降级或跨设备编辑任务，使用 `requiredContentVersion` 作为兼容性门控，并在旧客户端必须继续编辑时选择显式的 `maximumSupportedContentVersion`。

```swift
let targetVersion: PKContentVersion = .version1
canvasView.maximumSupportedContentVersion = targetVersion
toolPicker.maximumSupportedContentVersion = targetVersion

switch drawing.requiredContentVersion {
case .version1:
    // 较旧的标记、笔和铅笔墨水集
    syncEditable(drawing)
case .version2:
    // iPadOS 17 时代的墨水：monoline、fountain pen、watercolor、crayon
    syncIfRecipientsSupportVersion2(drawing)
case .version3, .version4:
    // 后续功能，如桶滚动数据和 Reed Pen
    syncEditableOnlyToCurrentClients(drawing)
@unknown default:
    showReadOnlyPreview(for: drawing)
}
```

如果绘图需要的新版本比接收者无法加载的版本更新，保留完整保真度的 `PKDrawing` 以供能够加载的客户端使用，并提供只读预览或单独的回退，而不是静默覆盖它。有关更深的兼容性表，请参阅 [参考资料/pencilkit-patterns.md](references/pencilkit-patterns.md)。

## 导出到图像

从绘图生成 `UIImage`。

```swift
func exportImage(from drawing: PKDrawing, scale: CGFloat = 2.0) -> UIImage {
    drawing.image(from: drawing.bounds, scale: scale)
}

// 导出特定区域
let region = CGRect(x: 0, y: 0, width: 500, height: 500)
let scale = UITraitCollection.current.displayScale
let croppedImage = drawing.image(from: region, scale: scale)
```

## 笔迹检查

访问单个笔迹、它们的墨水和控制点。

```swift
for stroke in drawing.strokes {
    let ink = stroke.ink
    print("墨水类型: \(ink.inkType), 颜色: \(ink.color)")
    print("边界: \(stroke.renderBounds)")

    // 访问路径点
    let path = stroke.path
    print("点数: \(path.count), 创建时间: \(path.creationDate)")

    // 沿路径插值
    for point in path.interpolatedPoints(by: .distance(10)) {
        print("位置: \(point.location), 力度: \(point.force)")
    }
}
```

### 逐行编程构建笔迹

仅用于生成的墨水路径；普通绘图和检查不需要高级构造器。

## SwiftUI 集成

将 `PKCanvasView` 封装在 SwiftUI 的 `UIViewRepresentable` 中。

```swift
import SwiftUI
import PencilKit

struct CanvasView: UIViewRepresentable {
    @Binding var drawing: PKDrawing
    @Binding var toolPickerVisible: Bool

    func makeUIView(context: Context) -> PKCanvasView {
        let canvas = PKCanvasView()
        canvas.delegate = context.coordinator
        canvas.drawingPolicy = .anyInput
        canvas.drawing = drawing
        context.coordinator.toolPicker.addObserver(canvas)
        return canvas
    }

    func updateUIView(_ canvas: PKCanvasView, context: Context) {
        if canvas.drawing != drawing {
            canvas.drawing = drawing
        }
        let toolPicker = context.coordinator.toolPicker
        toolPicker.setVisible(toolPickerVisible, forFirstResponder: canvas)
        if toolPickerVisible { canvas.becomeFirstResponder() }
    }

    func makeCoordinator() -> Coordinator { Coordinator(self) }

    class Coordinator: NSObject, PKCanvasViewDelegate {
        let parent: CanvasView
        let toolPicker = PKToolPicker()

        init(_ parent: CanvasView) {
            self.parent = parent
            super.init()
        }

        func canvasViewDrawingDidChange(_ canvasView: PKCanvasView) {
            parent.drawing = canvasView.drawing
        }
    }
}
```

对于 SwiftUI 封装器，使用标准的 [绘图策略](#绘图策略) 表设置输入策略。

### SwiftUI 中的使用

```swift
struct DrawingScreen: View {
    @State private var drawing = PKDrawing()
    @State private var showToolPicker = true

    var body: some View {
        CanvasView(drawing: $drawing, toolPickerVisible: $showToolPicker)
            .ignoresSafeArea()
    }
}
```

## PaperKit 关系

PaperKit (iOS 26+) 通过形状、文本框、图像、贴纸和放大镜扩展 PencilKit，提供完整的标记体验。当您需要结构化标记而不是仅自由形式绘图时，使用兄弟 `paperkit` 技能。

| 功能 | PencilKit | PaperKit |
|---|---|---|
| 自由形式绘图 | 是 | 是 |
| 形状和线条 | 否 | 是 |
| 文本框 | 否 | 是 |
| 图像和贴纸 | 否 | 是 |
| 放大镜 | 否 | 是 |
| 标记工具栏 | 否 | 是 |
| 标记插入 UI | 否 | `MarkupEditViewController`、`MarkupToolbarViewController` |
| 数据模型 | `PKDrawing` | `PaperMarkup` |

PaperKit 在底层使用 PencilKit：`PaperMarkupViewController` 接受 `PKTool` 作为其 `drawingTool` 属性，`PaperMarkup` 可以追加 `PKDrawing`。

## 常见错误

### 不要：忘记调用 becomeFirstResponder 为工具选择器

工具选择器仅在关联的响应者是第一响应者时才显示。

```swift
// 错误：工具选择器永远不会显示
toolPicker.setVisible(true, forFirstResponder: canvasView)

// 正确：也 become first responder
toolPicker.setVisible(true, forFirstResponder: canvasView)
canvasView.becomeFirstResponder()
```

### 不要：为同一画布创建多个工具选择器

每个画布一个 `PKToolPicker`。创建多余的会导致视觉冲突。

```swift
// 错误
func viewDidAppear(_ animated: Bool) {
    let picker = PKToolPicker()  // 每次显示时创建新选择器
    picker.setVisible(true, forFirstResponder: canvasView)
}

// 正确：将选择器作为属性存储
let toolPicker = PKToolPicker()
```

### 不要：忽略内容版本以向后兼容

在同步可编辑绘图之前，应用 [内容版本兼容性](#内容版本兼容性) 门控。

### 不要：通过数据表示比较绘图

`dataRepresentation()` 用于持久化和交换，而不是比较。使用 `PKDrawing` 等于性进行精确值检查，并检查笔迹或渲染图像进行视觉/近似比较。

```swift
// 错误
if drawing1.dataRepresentation() == drawing2.dataRepresentation() { }

// 正确
if drawing1 == drawing2 { }
```

## 审查清单

- [ ] `PKCanvasView.drawingPolicy` 遵循标准策略表
- [ ] `PKToolPicker` 存储为属性，而不是每次显示时重新创建
- [ ] `canvasView.becomeFirstResponder()` 调用以显示工具选择器
- [ ] 在显示选择器之前将画布添加为 `PKToolPicker` 观察者
- [ ] 绘图通过 `dataRepresentation()` 序列化并通过 `PKDrawing(data:)` 加载
- [ ] 使用 `canvasViewDrawingDidChange` 委托方法跟踪更改
- [ ] 如果需要向后兼容，在画布和工具选择器上设置 `maximumSupportedContentVersion`
- [ ] 自定义工具选择器项代码受 iOS/iPadOS 18+ 和 visionOS 2+ 保护
- [ ] 导出的图像使用适当的设备比例因子
- [ ] SwiftUI 封装器通过检查 `drawing != binding` 避免无限更新循环
- [ ] 在图像导出之前检查绘图边界（空绘图具有 `.zero` 边界）

## 参考资料

- 扩展 PencilKit 模式（高级笔迹、内容版本、委托）：[参考资料/pencilkit-patterns.md](references/pencilkit-patterns.md)
- [PencilKit 框架](https://sosumi.ai/documentation/pencilkit)
- [PKCanvasView](https://sosumi.ai/documentation/pencilkit/pkcanvasview)
- [PKDrawing](https://sosumi.ai/documentation/pencilkit/pkdrawing-swift.struct)
- [PKToolPicker](https://sosumi.ai/documentation/pencilkit/pktoolpicker)
- [PKInkingTool](https://sosumi.ai/documentation/pencilkit/pkinkingtool-swift.struct)
- [PKStroke](https://sosumi.ai/documentation/pencilkit/pkstroke-swift.struct)
- [使用 PencilKit 绘图](https://sosumi.ai/documentation/pencilkit/drawing-with-pencilkit)
- [配置 PencilKit 工具选择器](https://sosumi.ai/documentation/pencilkit/configuring-the-pencilkit-tool-picker)
