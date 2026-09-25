# PDFKit

使用 `PDFView`、`PDFDocument`、`PDFPage`、`PDFAnnotation` 和 `PDFSelection` 来显示、导航、搜索、注释和操作 PDF 文档。

## 内容

- [设置](#设置)
- [显示 PDF](#显示-pdf)
- [加载文档](#加载文档)
- [页面导航](#页面导航)
- [文本搜索和选择](#文本搜索和选择)
- [注释](#注释)
- [缩略图](#缩略图)
- [SwiftUI 集成](#swiftui集成)
- [常见错误](#常见错误)
- [审查清单](#审查清单)
- [参考资料](#参考资料)

## 设置

PDFKit 不需要任何权限或 Info.plist 条目。

```swift
import PDFKit
```

| API | 可用性 |
|---|---|
| PDFKit 框架 | iOS/iPadOS/tvOS 11+、Mac Catalyst 13.1+、macOS 10.4+、visionOS 1.0+ |
| 查找交互和页面覆盖 | iOS/iPadOS 16+ |

## 显示 PDF

`PDFView` 渲染 PDF 内容并处理缩放、滚动、文本选择和页面导航。

```swift
import PDFKit
import UIKit

class PDFViewController: UIViewController {
    let pdfView = PDFView()

    override func viewDidLoad() {
        super.viewDidLoad()
        pdfView.frame = view.bounds
        pdfView.autoresizingMask = [.flexibleWidth, .flexibleHeight]
        view.addSubview(pdfView)

        pdfView.autoScales = true
        pdfView.displayMode = .singlePageContinuous
        pdfView.displayDirection = .vertical

        if let url = Bundle.main.url(forResource: "sample", withExtension: "pdf") {
            pdfView.document = PDFDocument(url: url)
        }
    }
}
```

### 显示模式

| 模式 | 行为 |
|---|---|
| `.singlePage` | 一次显示一页 |
| `.singlePageContinuous` | 页面垂直堆叠，可滚动 |
| `.twoUp` | 两页并排显示 |
| `.twoUpContinuous` | 两页并排，连续滚动 |

### 缩放和外观

```swift
pdfView.autoScales = true
pdfView.minScaleFactor = pdfView.scaleFactorForSizeToFit
pdfView.maxScaleFactor = 4.0

pdfView.displaysPageBreaks = true
pdfView.pageShadowsEnabled = true
pdfView.interpolationQuality = .high
```

## 加载文档

`PDFDocument` 可以从 URL、`Data` 加载，或者可以创建空白的。

```swift
let fileDoc = PDFDocument(url: fileURL)
let dataDoc = PDFDocument(data: pdfData)
let emptyDoc = PDFDocument()
```

### 密码保护的 PDF

```swift
guard let document = PDFDocument(url: url) else { return }
if document.isLocked {
    if !document.unlock(withPassword: userPassword) {
        // 显示密码提示
    }
}
```

### 保存和页面操作

```swift
document.write(to: outputURL)
document.write(to: outputURL, withOptions: [
    .ownerPasswordOption: "ownerPass", .userPasswordOption: "userPass"
])
let data = document.dataRepresentation()

// 页面是从 0 开始的。验证索引；超出范围的调用会引发异常。
let count = document.pageCount
document.insert(PDFPage(), at: count)
if document.pageCount > 2 {
    document.removePage(at: 2)
}
if document.pageCount > 3 {
    document.exchangePage(at: 0, withPageAt: 3)
}
```

## 页面导航

`PDFView` 提供内置导航并跟踪历史记录。

```swift
// 跳转到特定页面
let pageIndex = 5
if let document = pdfView.document,
   pageIndex >= 0,
   pageIndex < document.pageCount,
   let page = document.page(at: pageIndex) {
    pdfView.go(to: page)
}

// 顺序导航
pdfView.goToNextPage(nil)
pdfView.goToPreviousPage(nil)
pdfView.goToFirstPage(nil)
pdfView.goToLastPage(nil)

// 检查导航状态
if pdfView.canGoToNextPage { /* ... */ }

// 历史导航
if pdfView.canGoBack { pdfView.goBack(nil) }

// 跳转到当前页面的特定位置
if let page = pdfView.currentPage {
    let destination = PDFDestination(page: page, at: CGPoint(x: 0, y: 500))
    pdfView.go(to: destination)
}
```

### 观察页面变化

```swift
NotificationCenter.default.addObserver(
    self, selector: #selector(pageChanged),
    name: .PDFViewPageChanged, object: pdfView
)

@objc func pageChanged(_ notification: Notification) {
    guard let page = pdfView.currentPage,
          let doc = pdfView.document else { return }
    let index = doc.index(for: page)
    pageLabel.text = "Page \(index + 1) of \(doc.pageCount)"
}
```

## 文本搜索和选择

### 同步搜索

```swift
let results: [PDFSelection] = document.findString(
    "search term", withOptions: [.caseInsensitive]
)
```

### 异步搜索

使用 `PDFDocumentDelegate` 在大文档上进行后台搜索。
实现 `didMatchString(_:)` 以接收每个匹配项，并实现 `documentDidEndDocumentFind(_:)` 以接收完成通知。

### 增量搜索和查找交互

```swift
// 从当前选择查找下一个匹配项
let next = document.findString("term", fromSelection: current, withOptions: [.caseInsensitive])

// 系统查找栏；应用设置中的可用性门控
pdfView.isFindInteractionEnabled = true
```

### 文本提取

```swift
let fullText = document.string                          // 整个文档
let firstPage = document.pageCount > 0 ? document.page(at: 0) : nil
let pageText = firstPage?.string                        // 单页
let attributed = firstPage?.attributedString            // 带格式

// 基于区域的提取
if let page = firstPage {
    let selection = page.selection(for: CGRect(x: 50, y: 50, width: 400, height: 200))
    let text = selection?.string
}
```

### 高亮搜索结果

```swift
let results = document.findString("important", withOptions: [.caseInsensitive])
for selection in results { selection.color = .yellow }
pdfView.highlightedSelections = results

if let first = results.first {
    pdfView.setCurrentSelection(first, animate: true)
    pdfView.go(to: first)
}
```

## 注释

注释使用 `PDFAnnotation(bounds:forType:withProperties:)` 创建，并添加到 `PDFPage`。

### 高亮注释

```swift
func addHighlight(to page: PDFPage, selection: PDFSelection) {
    let highlight = PDFAnnotation(
        bounds: selection.bounds(for: page),
        forType: .highlight, withProperties: nil
    )
    highlight.color = UIColor.yellow.withAlphaComponent(0.5)
    page.addAnnotation(highlight)
}
```

### 文本注释

```swift
let note = PDFAnnotation(
    bounds: CGRect(x: 100, y: 700, width: 30, height: 30),
    forType: .text, withProperties: nil
)
note.contents = "这是一个便签。"
note.color = .systemYellow
note.iconType = .comment
page.addAnnotation(note)
```

### 自由文本注释

```swift
let freeText = PDFAnnotation(
    bounds: CGRect(x: 50, y: 600, width: 300, height: 40),
    forType: .freeText, withProperties: nil
)
freeText.contents = "添加评论"
freeText.font = UIFont.systemFont(ofSize: 14)
freeText.fontColor = .darkGray
page.addAnnotation(freeText)
```

### 链接注释

```swift
let link = PDFAnnotation(
    bounds: CGRect(x: 50, y: 500, width: 200, height: 20),
    forType: .link, withProperties: nil
)
link.url = URL(string: "https://example.com")!
page.addAnnotation(link)

// 内部页面链接
link.destination = PDFDestination(page: targetPage, at: .zero)
```

### 删除注释

```swift
for annotation in page.annotations {
    page.removeAnnotation(annotation)
}
```

常见的子类型包括 `.highlight`、`.underline`、`.strikeOut`、`.text`、`.freeText`、`.ink`、`.link`、`.line`、`.square`、`.circle`、`.stamp` 和 `.widget`。

## 缩略图

### PDFThumbnailView

`PDFThumbnailView` 显示一排页面缩略图，并与 `PDFView` 链接。

```swift
let thumbnailView = PDFThumbnailView()
thumbnailView.pdfView = pdfView
thumbnailView.thumbnailSize = CGSize(width: 60, height: 80)
thumbnailView.layoutMode = .vertical
thumbnailView.translatesAutoresizingMaskIntoConstraints = false
view.addSubview(thumbnailView)
```

### 生成缩略图

```swift
let thumbnail = page.thumbnail(of: CGSize(width: 120, height: 160), for: .mediaBox)

// 所有页面
let thumbnails = (0..<document.pageCount).compactMap {
    document.page(at: $0)?.thumbnail(of: CGSize(width: 120, height: 160), for: .mediaBox)
}
```

## SwiftUI 集成

将 `PDFView` 包裹在 `UIViewRepresentable` 中以用于 SwiftUI。PDF 特定的包装器（配置 `PDFView`、页面、注释、搜索、缩略图或覆盖）属于此技能；仅将通用可表示生命周期、布局或 SwiftUI 状态架构问题路由到 SwiftUI/UIKit 互操作指南。

```swift
import SwiftUI
import PDFKit

struct PDFKitView: UIViewRepresentable {
    let document: PDFDocument

    func makeUIView(context: Context) -> PDFView {
        let pdfView = PDFView()
        pdfView.autoScales = true
        pdfView.displayMode = .singlePageContinuous
        pdfView.document = document
        return pdfView
    }

    func updateUIView(_ pdfView: PDFView, context: Context) {
        if pdfView.document !== document {
            pdfView.document = document
        }
    }
}
```

### 使用

```swift
struct DocumentScreen: View {
    let url: URL

    var body: some View {
        if let document = PDFDocument(url: url) {
            PDFKitView(document: document)
                .ignoresSafeArea()
        } else {
            ContentUnavailableView("无法加载 PDF", systemImage: "doc.questionmark")
        }
    }
}
```

对于具有页面跟踪、注释命中检测和协调器模式的交互式包装器，请参阅 [参考资料/pdfkit-patterns.md](references/pdfkit-patterns.md)。

### 页面覆盖

`PDFPageOverlayViewProvider` 将 UIKit 视图放置在单个页面的顶部，用于交互式控件或标准注释之外的定制渲染。

```swift
class OverlayProvider: NSObject, PDFPageOverlayViewProvider {
    func pdfView(_ view: PDFView, overlayViewFor page: PDFPage) -> UIView? {
        let overlay = UIView()
        // 添加自定义子视图
        return overlay
    }
}

class PDFOverlayController: UIViewController {
    let pdfView = PDFView()
    private let overlayProvider = OverlayProvider()

    override func viewDidLoad() {
        super.viewDidLoad()
        pdfView.pageOverlayViewProvider = overlayProvider
    }
}
```

`pageOverlayViewProvider` 是弱引用的，因此请保持提供者强引用。有关覆盖生命周期和保存处理，请参阅 [参考资料/pdfkit-patterns.md](references/pdfkit-patterns.md)。

## 常见错误

### 不要：强制解包 PDFDocument 初始化

`PDFDocument(url:)` 和 `PDFDocument(data:)` 是可失败初始化器。

```swift
// 错误
let document = PDFDocument(url: url)!

// 正确
guard let document = PDFDocument(url: url) else { return }
```

### 不要：忘记 PDFView 的 autoScales

如果没有 `autoScales`，PDF 将以其原生分辨率渲染。

```swift
// 错误
pdfView.document = document

// 正确
pdfView.autoScales = true
pdfView.document = document
```

### 不要：忽略注释中的 PDF 坐标系统

PDF 页面坐标的原点在左下角，Y 轴向上增加——与 UIKit 相反。

```swift
// 错误：UIKit 坐标
let bounds = CGRect(x: 50, y: 50, width: 200, height: 30)

// 正确：PDF 坐标（原点在左下角）
let pageBounds = page.bounds(for: .mediaBox)
let pdfY = pageBounds.height - 50 - 30
let bounds = CGRect(x: 50, y: pdfY, width: 200, height: 30)
```

### 不要：在后台线程上修改注释

PDFKit 类不是线程安全的。

```swift
// 错误
DispatchQueue.global().async { page.addAnnotation(annotation) }

// 正确
DispatchQueue.main.async { page.addAnnotation(annotation) }
```

### 不要：在 UIViewRepresentable 中使用 == 比较 PDFDocument

`PDFDocument` 是引用类型。使用身份 (`!==`)。

```swift
// 错误：总是替换文档
func updateUIView(_ pdfView: PDFView, context: Context) {
    pdfView.document = document
}

// 正确
func updateUIView(_ pdfView: PDFView, context: Context) {
    if pdfView.document !== document {
        pdfView.document = document
    }
}
```

## 审查清单

- [ ] `PDFDocument` 初始化使用可选绑定，而不是强制解包
- [ ] `pdfView.autoScales = true` 设置以正确显示初始内容
- [ ] 在访问之前检查页面索引是否与 `pageCount` 匹配
- [ ] `displayMode` 和 `displayDirection` 配置以匹配设计
- [ ] 注释使用 PDF 坐标空间（原点在左下角，Y 轴向上）
- [ ] 所有 PDFKit 变化都在主线程上发生
- [ ] 处理密码保护的 PDF 使用 `isLocked` / `unlock(withPassword:)`
- [ ] SwiftUI 包装器在 `updateUIView` 中使用 `!==` 身份检查
- [ ] 观察 `PDFViewPageChanged` 通知以进行页面跟踪
- [ ] `PDFThumbnailView.pdfView` 与主 `PDFView` 链接
- [ ] 大文档搜索使用异步 `beginFindString` 并使用代理
- [ ] 保存文档在需要加密时使用 `write(to:withOptions:)`

## 参考资料

- 扩展模式（表单、水印、合并、打印、覆盖、大纲、自定义绘制）：[参考资料/pdfkit-patterns.md](references/pdfkit-patterns.md)
- [PDFKit 框架](https://sosumi.ai/documentation/pdfkit)
- [PDFView](https://sosumi.ai/documentation/pdfkit/pdfview)
- [PDFDocument](https://sosumi.ai/documentation/pdfkit/pdfdocument)
- [PDFPage](https://sosumi.ai/documentation/pdfkit/pdfpage)、[PDFAnnotation](https://sosumi.ai/documentation/pdfkit/pdfannotation)、[PDFSelection](https://sosumi.ai/documentation/pdfkit/pdfselection)、[PDFThumbnailView](https://sosumi.ai/documentation/pdfkit/pdfthumbnailview)
- [PDFPageOverlayViewProvider](https://sosumi.ai/documentation/pdfkit/pdfpageoverlayviewprovider)
- [向 PDF 文档添加 Widget](https://sosumi.ai/documentation/pdfkit/adding-widgets-to-a-pdf-document)
- [向 PDF 添加自定义图形](https://sosumi.ai/documentation/pdfkit/adding-custom-graphics-to-a-pdf)
