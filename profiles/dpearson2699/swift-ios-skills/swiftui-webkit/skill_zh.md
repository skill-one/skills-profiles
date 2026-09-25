# SwiftUI WebKit

使用为 iOS 26、iPadOS 26、macOS 26 和 visionOS 26 引入的原生 WebKit-for-SwiftUI API 在 SwiftUI 中嵌入和管理网页内容。当应用程序需要集成网页界面、应用程序拥有的 HTML 内容、JavaScript 支持的页面交互或自定义导航策略控制时，使用此技能。

## 目录

- [选择合适的 Web 容器](#选择合适的-web容器)
- [显示网页内容](#显示网页内容)
- [使用 WebPage 加载和观察](#使用-webpage加载和观察)
- [导航策略](#导航策略)
- [JavaScript 集成](#javascript集成)
- [本地内容和自定义 URL 方案](#本地内容和自定义-url方案)
- [WebView 自定义](#webview自定义)
- [常见错误](#常见错误)
- [审查清单](#审查清单)
- [参考资料](#参考资料)

## 选择合适的 Web 容器

使用与任务匹配的最窄工具。

| 需求 | 默认选择 |
|---|---|
| 在 SwiftUI 中嵌入应用程序拥有的网页内容 | `WebView` + `WebPage` |
| iOS/iPadOS 带有 Safari 行为的模态浏览 | `SFSafariViewController` |
| macOS 或 visionOS 浏览外行为 | `openURL` / 默认浏览器 |
| OAuth 或第三方登录 | `ASWebAuthenticationSession` |
| 低于 iOS 26 的回退部署或使用仅限遗留的 WebKit 功能 | `WKWebView` 回退 |

当新的 API 表面涵盖功能时，优先为面向 iOS 26+ 的现代 SwiftUI 应用程序使用 `WebView` 和 `WebPage`。苹果的 WWDC25 指导方针将现有的 UIKit/AppKit WebKit 包装器在 SwiftUI 应用程序中视为迁移的良好候选者，而不是删除每个回退的全面命令。

不要使用嵌入式 WebView 进行 OAuth。那仍然是 `ASWebAuthenticationSession` 流程。

## 显示网页内容

当应用程序只需要渲染 URL 且 SwiftUI 状态驱动导航时，使用简单的 `WebView(url:)` 形式。

```swift
import SwiftUI
import WebKit

struct ArticleView: View {
    let url: URL

    var body: some View {
        WebView(url: url)
    }
}
```

当应用程序需要直接加载请求、观察状态、调用 JavaScript 或自定义导航行为时，创建一个 `WebPage`。

一个 `WebPage` 只能与一个 `WebView` 同时关联。为多个可见的 WebView 创建单独的 `WebPage` 实例。

```swift
@Observable
@MainActor
final class ArticleModel {
    let page = WebPage()

    func load(_ url: URL) async throws {
        for try await _ in page.load(URLRequest(url: url)) {
        }
    }
}

struct ArticleDetailView: View {
    @State private var model = ArticleModel()
    let url: URL

    var body: some View {
        WebView(model.page)
            .task {
                try? await model.load(url)
            }
    }
}
```

有关完整示例，请参阅 [references/loading-and-observation.md](references/loading-and-observation.md)。

## 使用 WebPage 加载和观察

`WebPage` 是一个 `@MainActor` 可观察类型。当您需要在 SwiftUI 中需要页面状态时使用它。

常见的加载入口点：
- `load(URLRequest)`
- `load(URL)`
- `load(html:baseURL:)`
- `load(_:mimeType:characterEncoding:baseURL:)`

常见的可观察属性：
- `title`
- `url`
- `isLoading`
- `estimatedProgress`
- `currentNavigationEvent`
- `backForwardList`

```swift
struct ReaderView: View {
    @State private var page = WebPage()

    var body: some View {
        WebView(page)
            .navigationTitle(page.title ?? "加载中")
            .overlay {
                if page.isLoading {
                    ProgressView(value: page.estimatedProgress)
                }
            }
            .task {
                do {
                    for try await _ in page.load(URLRequest(url: URL(string: "https://example.com")!)) {
                    }
                } catch {
                    // 处理加载失败。
                }
            }
    }
}
```

当您需要响应每次导航时，观察导航序列而不是只检查单个属性。

```swift
Task {
    do {
        for try await event in page.navigations {
            // 处理开始、重定向、提交或完成事件。
        }
    } catch {
        // 处理 WebPage.NavigationError 或取消。
    }
}
```

有关更强的模式和加载序列示例，请参阅 [references/loading-and-observation.md](references/loading-and-observation.md)。

## 导航策略

使用 `WebPage.NavigationDeciding` 允许、取消或根据请求或响应自定义导航。

典型用法：
- 保持应用程序拥有的域在嵌入式 WebView 内部
- 取消外部域并将它们交给 `openURL`
- 截获特殊回调 URL
- 调整 `NavigationPreferences`

```swift
@MainActor
final class ArticleNavigationDecider: WebPage.NavigationDeciding {
    var urlToOpenExternally: URL?

    func decidePolicy(
        for action: WebPage.NavigationAction,
        preferences: inout WebPage.NavigationPreferences
    ) async -> WKNavigationActionPolicy {
        guard let url = action.request.url else { return .allow }

        if url.host == "example.com" {
            return .allow
        }

        urlToOpenExternally = url
        return .cancel
    }
}
```

在导航技能中保持应用程序级别的深度链接路由。此技能拥有在嵌入式网页内容中发生的导航。

有关完整模式，请参阅 [references/navigation-and-javascript.md](references/navigation-and-javascript.md)。

## JavaScript 集成

使用 `callJavaScript(_:arguments:in:contentWorld:)` 对页面上的 JavaScript 函数进行求值。

传递 JavaScript 函数体，而不是包装的函数声明或调用表达式。优先使用 `arguments` 传递 Swift 提供的值，而不是将不受信任的字符串插入脚本。

```swift
let script = """
const headings = [...document.querySelectorAll('h1, h2')];
return headings.map(node => ({
    id: node.id,
    text: node.textContent?.trim()
}));
"""

let result = try await page.callJavaScript(script)
let headings = result as? [[String: Any]] ?? []
```

您可以通过 `arguments` 字典传递值，并将返回的 `Any` 转换为您实际需要的 Swift 类型。

```swift
let result = try await page.callJavaScript(
    "return document.getElementById(sectionID)?.getBoundingClientRect().top ?? null;",
    arguments: ["sectionID": selectedSectionID]
)
```

故意处理空和 JavaScript `null` 结果：没有显式返回会产生 `nil`，而显式的 JavaScript `null` 返回 `NSNull`。

重要边界：原生 SwiftUI WebKit API 明确支持 Swift-to-JavaScript 调用，但它没有公开直接替代 `WKScriptMessageHandler` 的方法。如果您需要粗粒度的 JS-to-native 信号，自定义导航或回调 URL 模式可以工作，但请将其记录为一种替代模式，而不是保证的一对一替换。

有关详细信息，请参阅 [references/navigation-and-javascript.md](references/navigation-and-javascript.md)。

## 本地内容和自定义 URL 方案

当应用程序需要捆绑的 HTML、离线文档或应用程序提供的自定义方案下的资源时，使用 `WebPage.Configuration` 和 `URLSchemeHandler`。

```swift
var configuration = WebPage.Configuration()
configuration.urlSchemeHandlers[URLScheme("docs")!] = DocsSchemeHandler(bundle: .main)

let page = WebPage(configuration: configuration)
for try await _ in page.load(URL(string: "docs://article/welcome")!) {
}

```

用于：
- 捆绑的文档或文章内容
- 离线 HTML/CSS/JS 资产
- 在自定义方案下加载应用程序拥有的资源

不要过度使用自定义方案进行普通远程内容。优先使用标准 HTTPS 加载服务器托管页面。

有关详细信息，请参阅 [references/local-content-and-custom-schemes.md](references/local-content-and-custom-schemes.md)。

## WebView 自定义

使用 WebView 修饰符以匹配预期的浏览体验。

有用的修饰符和相关 API：
- `webViewBackForwardNavigationGestures(_:)`
- `findNavigator(isPresented:)`
- `webViewScrollPosition(_:)`
- `webViewOnScrollGeometryChange(...)`

仅在用户体验需要时应用它们。

- 当人们可能会访问多个页面时，启用后退/前进手势。
- 当内容像文档时，添加页面内查找。
- 仅当应用程序有侧边栏、目录或其他明确导航功能时，同步滚动位置。

苹果的 HIG 也适用于此：在适当的情况下支持后退/前进导航，但不要将应用程序 WebView 转换为通用浏览器。

## 常见错误

- 在 iOS 26+ 的 SwiftUI 应用程序中默认使用 `WKWebView` 包装器，而不是从 `WebView` 和 `WebPage` 开始
- 使用嵌入式 WebView 进行 OAuth，而不是 `ASWebAuthenticationSession`
- 在构建一个现在需要状态、JS 或导航控制的简单 `WebView(url:)` 路径后，才使用 `WebPage`
- 将 `callJavaScript` 视为 `WKScriptMessageHandler` 的直接替代品
- 将可调用的 JavaScript 包装器传递给 `callJavaScript`，而不是只传递函数体
- 即使导航失败会终止序列并抛出，也迭代 `page.navigations` 而不使用 `try`/`catch`
- 将相同的 `WebPage` 绑定到多个可见的 `WebView` 值
- 将所有链接保留在应用程序中，而外部域应在嵌入式表面外打开
- 将 `SFSafariViewController` 视为 macOS 或 visionOS 上的跨平台浏览外答案，而不是使用默认浏览器/openURL 行为
- 在 WebView 周围构建浏览器式应用外壳，而不是专注的嵌入式体验
- 使用自定义 URL 方案加载应该只是通过 HTTPS 加载的内容
- 忘记 `WebPage` 是主线程隔离的

## 审查清单

- [ ] `WebView` 和 `WebPage` 是 iOS 26+ SwiftUI 网页内容的默认路径
- [ ] `ASWebAuthenticationSession` 用于 auth 流程，而不是嵌入式 WebView
- [ ] 只要应用程序需要状态观察、JS 调用或策略控制，就使用 `WebPage`
- [ ] 导航策略仅拦截应用程序实际拥有或需要重新路由的 URL
- [ ] 外部域在适当的时候外部打开
- [ ] JavaScript 返回值防御性地转换为具体的 Swift 类型
- [ ] `callJavaScript` 使用函数体并通过 `arguments` 传递 Swift 值
- [ ] `page.navigations` 循环使用 `for try await` 并处理抛出的导航错误
- [ ] 每个可见的 `WebView(page)` 拥有一个独立的 `WebPage`
- [ ] 仅用于真正的应用程序拥有的资源使用自定义 URL 方案
- [ ] 当预期多页面浏览时，启用后退/前进手势或控件
- [] `SFSafariViewController` 仅限于 iOS/iPadOS Safari 式模态浏览；macOS 和 visionOS 浏览外流程使用平台默认浏览器行为
- [] 网页体验增加了专注的原生价值，而不是表现得像浏览器外壳
- [] 回退到 `WKWebView` 是由部署目标或缺少 API 需要证明的

## 参考资料

- 加载和观察：[references/loading-and-observation.md](references/loading-and-observation.md)
- 导航和 JavaScript：[references/navigation-and-javascript.md](references/navigation-and-javascript.md)
- 本地内容和自定义方案：[references/local-content-and-custom-schemes.md](references/local-content-and-custom-schemes.md)
- 迁移和回退：[references/migration-and-fallbacks.md](references/migration-and-fallbacks.md)
