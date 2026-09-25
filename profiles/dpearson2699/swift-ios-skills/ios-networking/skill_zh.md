# iOS 网络编程

使用 URLSession 与 async/await 和结构化并发处理普通的 HTTP、REST、上传、下载和流式传输。使用 Network.framework 处理低级协议，并使用委托/任务 API 进行持久的后台传输。

## 目录

- [核心 URLSession async/await](#核心-urlsession-asyncawait)
- [API 客户端架构](#api-client-architecture)
- [错误处理](#error-handling)
- [分页](#pagination)
- [网络可达性](#network-reachability)
- [配置 URLSession](#configuring-urlsession)
- [应用传输安全 (ATS)](#app-transport-security-ats)
- [常见错误](#common-mistakes)
- [审查清单](#review-checklist)
- [参考资料](#references)

## 核心 URLSession async/await

URLSession 在 iOS 15 中获得了原生的 async/await 重载。对于前台数据、上传、下载和流式传输工作，请优先使用这些功能。后台 URLSession 传输是主要例外：它们仍然使用任务/委托 API，以便系统可以在挂起或重新启动后传递事件。

使用 `URLProtocol` 测试用例在本地验证网络策略，以验证有效的 2xx、格式错误的 2xx、一次性 401 刷新、有界的 429/5xx 重试、超时/离线、取消和非重试的 4xx。检查标头、状态和错误分类；修复策略并重新运行。仅重试安全/幂等的或显式可重播的请求，并且永远不要循环令牌刷新。

### 数据请求

```swift
// 基本的 GET
let (data, response) = try await URLSession.shared.data(from: url)

// 使用配置的 URLRequest
var request = URLRequest(url: url)
request.httpMethod = "POST"
request.setValue("application/json", forHTTPHeaderField: "Content-Type")
request.httpBody = try JSONEncoder().encode(payload)
request.timeoutInterval = 30
request.cachePolicy = .reloadIgnoringLocalCacheData

let (data, response) = try await URLSession.shared.data(for: request)
```

### 响应验证

在解码之前始终验证 HTTP 状态码。URLSession 不会因 4xx/5xx 响应而抛出异常——它仅在传输级故障时抛出异常。

```swift
guard let httpResponse = response as? HTTPURLResponse else {
    throw NetworkError.invalidResponse
}

guard (200..<300).contains(httpResponse.statusCode) else {
    throw NetworkError.httpError(
        statusCode: httpResponse.statusCode,
        data: data
    )
}
```

### 使用 Codable 进行 JSON 解码

```swift
func fetch<T: Decodable>(_ type: T.Type, from url: URL) async throws -> T {
    let (data, response) = try await URLSession.shared.data(from: url)

    guard let httpResponse = response as? HTTPURLResponse,
          (200..<300).contains(httpResponse.statusCode) else {
        throw NetworkError.invalidResponse
    }

    let decoder = JSONDecoder()
    decoder.dateDecodingStrategy = .iso8601
    decoder.keyDecodingStrategy = .convertFromSnakeCase
    return try decoder.decode(T.self, from: data)
}
```

### 下载和上传

使用 `download(for:)` 处理大文件——它将数据流式传输到磁盘，而不是将整个有效负载加载到内存中。

```swift
// 下载到临时文件
let (localURL, response) = try await URLSession.shared.download(for: request)

// 及时移动或复制返回的临时文件。
let destination = documentsDirectory.appendingPathComponent("file.zip")
try FileManager.default.moveItem(at: localURL, to: destination)
```

对于基于委托的 `URLSessionDownloadDelegate`，在 `urlSession(_:downloadTask:didFinishDownloadingTo:)` 返回之前移动或打开临时文件。

后台会话是委托驱动的传输队列。使用任务创建 API，如 `downloadTask(with:)` 和文件背书的 `uploadTask(with:fromFile:)`，然后处理 `URLSessionDelegate` / 任务委托回调。不要使用异步便利 API，如 `data(for:)`、`download(for:)` 或 `upload(for:)`，因为它们不是持久的后台会话模式。

```swift
// 上传数据
let (data, response) = try await URLSession.shared.upload(for: request, from: bodyData)

// 从文件上传
let (data, response) = try await URLSession.shared.upload(for: request, fromFile: fileURL)
```

### 使用 AsyncBytes 进行流式传输

使用 `bytes(for:)` 处理响应流、进度跟踪或行分隔数据（例如，服务器发送事件）。

```swift
let (bytes, response) = try await URLSession.shared.bytes(for: request)

for try await line in bytes.lines {
    // 每当收到一行时处理（例如，SSE 流）
    handleEvent(line)
}
```

## API 客户端架构

### 基于协议的客户端

定义一个协议以进行可测试性。这允许你在测试中交换实现，而无需直接模拟 URLSession。

```swift
protocol APIClientProtocol: Sendable {
    func fetch<T: Decodable & Sendable>(
        _ type: T.Type,
        endpoint: Endpoint
    ) async throws -> T

    func send<T: Decodable & Sendable>(
        _ type: T.Type,
        endpoint: Endpoint,
        body: some Encodable & Sendable
    ) async throws -> T
}
```

```swift
struct Endpoint: Sendable {
    let path: String
    var method: String = "GET"
    var queryItems: [URLQueryItem] = []
    var headers: [String: String] = [:]

    func url(relativeTo baseURL: URL) -> URL {
        guard let components = URLComponents(
            url: baseURL.appendingPathComponent(path),
            resolvingAgainstBaseURL: true
        ) else {
            preconditionFailure("Invalid URL components for path: \(path)")
        }
        var mutableComponents = components
        if !queryItems.isEmpty {
            mutableComponents.queryItems = queryItems
        }
        guard let url = mutableComponents.url else {
            preconditionFailure("Failed to construct URL from components")
        }
        return url
    }
}
```

客户端接受一个 `baseURL`、可选的自定义 `URLSession`、`JSONDecoder` 和一个 `RequestMiddleware` 中间件拦截器数组。每个方法从端点构建 `URLRequest`，应用中间件，执行请求，验证状态码并解码结果。有关完整的 `APIClient` 实现和便利方法、请求构建器和测试设置的详细信息，请参阅 [参考资料/urlsession-patterns.md](references/urlsession-patterns.md)。

生产客户端应接收注入的、配置的 `URLSession`，而不是在内部调用 `URLSession.shared`。配置 `URLSessionConfiguration` 以包含请求/资源超时、缓存策略或 `URLCache`、`waitsForConnectivity`、数据成本策略以及在身份验证挑战、重定向、指标、固定或后台传输处理方面重要时的委托。

### 轻量级闭包客户端

对于使用 MV 模式的应用程序，使用闭包客户端进行可测试性和 SwiftUI 预览支持。有关完整模式（通过 init 注入的异步闭包结构）的详细信息，请参阅 [参考资料/lightweight-clients.md](references/lightweight-clients.md)。

### 请求中间件 / 拦截器

中间件在发送请求之前转换请求。使用此功能进行身份验证、日志记录、分析标头和类似的跨领域关注点。

```swift
protocol RequestMiddleware: Sendable {
    func prepare(_ request: URLRequest) async throws -> URLRequest
}
```

```swift
struct AuthMiddleware: RequestMiddleware {
    let tokenProvider: @Sendable () async throws -> String

    func prepare(_ request: URLRequest) async throws -> URLRequest {
        var request = request
        let token = try await tokenProvider()
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        return request
    }
}
```

### 令牌刷新流程

通过刷新令牌并重试一次来处理 401 响应。

```swift
func fetchWithTokenRefresh<T: Decodable & Sendable>(
    _ type: T.Type,
    endpoint: Endpoint,
    tokenStore: TokenStore
) async throws -> T {
    do {
        return try await fetch(type, endpoint: endpoint)
    } catch NetworkError.httpError(statusCode: 401, _) {
        try await tokenStore.refreshToken()
        return try await fetch(type, endpoint: endpoint)
    }
}
```

## 错误处理

### 结构化错误类型

```swift
enum NetworkError: Error, Sendable {
    case invalidResponse
    case httpError(statusCode: Int, data: Data)
    case decodingFailed(Error)
    case noConnection
    case timedOut
    case cancelled

    /// 将 URLError 映射为类型的 NetworkError
    static func from(_ urlError: URLError) -> NetworkError {
        switch urlError.code {
        case .notConnectedToInternet, .networkConnectionLost:
            return .noConnection
        case .timedOut:
            return .timedOut
        case .cancelled:
            return .cancelled
        default:
            return .httpError(statusCode: -1, data: Data())
        }
    }
}
```

### 关键 URLError 案例表

| URLError 代码 | 含义 | 操作 |
|---|---|---|
| `.notConnectedToInternet` | 设备离线 | 显示离线 UI，排队重试 |
| `.networkConnectionLost` | 请求中途断开连接 | 带退避重试 |
| `.timedOut` | 服务器未在规定时间内响应 | 重试一次，然后显示错误 |
| `.cancelled` | 任务被取消 | 无需操作；不要显示错误 |
| `.cannotFindHost` | DNS 失败 | 检查 URL，显示错误 |
| `.secureConnectionFailed` | TLS 握手失败 | 检查证书固定，ATS 配置 |
| `.userAuthenticationRequired` | 访问资源需要身份验证 | 触发身份验证流程 |

### 解码服务器错误正文

```swift
struct APIErrorResponse: Decodable, Sendable {
    let code: String
    let message: String
}

func decodeAPIError(from data: Data) -> APIErrorResponse? {
    try? JSONDecoder().decode(APIErrorResponse.self, from: data)
}

// 在 catch 块中使用
catch NetworkError.httpError(let statusCode, let data) {
    if let apiError = decodeAPIError(from: data) {
        showError("服务器错误：\(apiError.message)")
    } else {
        showError("HTTP \(statusCode)")
    }
}
```

### 带指数退避的重试

使用结构化并发进行重试。在尝试之间尊重任务取消。对于取消和 4xx 客户端错误（除 429 外）跳过重试。

```swift
func withRetry<T: Sendable>(
    maxAttempts: Int = 3,
    initialDelay: Duration = .seconds(1),
    operation: @Sendable () async throws -> T
) async throws -> T {
    var lastError: Error?
    for attempt in 0..<maxAttempts {
        do {
            return try await operation()
        } catch {
            lastError = error
            if error is CancellationError { throw error }
            if case NetworkError.httpError(let code, _) = error,
               (400..<500).contains(code), code != 429 { throw error }
            if attempt < maxAttempts - 1 {
                try await Task.sleep(for: initialDelay * Int(pow(2.0, Double(attempt))))
            }
        }
    }
    throw lastError!
}
```

## 分页

使用 `AsyncSequence` 构建 cursor-based 或 offset-based 分页。在页面之间始终检查 `Task.isCancelled`。有关完整的 `CursorPaginator` 和基于 offset 的实现，请参阅 [参考资料/urlsession-patterns.md](references/urlsession-patterns.md)。

## 网络可达性

使用 Network.framework 的 `NWPathMonitor`——而不是第三方 Reachability 库。在当前 OS 目标上，它符合 `AsyncSequence`；仅将 `pathUpdateHandler` 包装以兼容或自定义投影。

```swift
import Network

func observeNetworkStatus() async {
    let monitor = NWPathMonitor()

    for await path in monitor {
        handle(path.status)
    }
}
```

检查 `path.isExpensive`（蜂窝）和 `path.isConstrained`（低数据模式）以调整行为（降低图像质量，跳过预取）。

使用 Network.framework 处理低级 TCP、UDP、监听器、Bonjour、路径监控或 WebSocket 协议工作——而不是普通的 REST API。对于 iOS 26，`NetworkConnection<QUIC>`、`openStream(...)` 和 `inboundStreams(...)` 是异步抛出 API；请参阅 [参考资料/network-framework.md#quic-multiplexed-streams](references/network-framework.md#quic-multiplexed-streams)。

## 配置 URLSession

当生产代码需要超时、缓存、连接等待、数据成本策略、身份验证挑战、重定向、指标或后台委托时，注入配置的会话。仅使用 `URLSession.shared` 进行简单的单次工作。有关完整配置和测试设置，请参阅 [URLSession 模式](references/urlsession-patterns.md)。

## 应用传输安全 (ATS)

ATS 使 HTTPS 成为 URL 加载系统的默认值。不要启用无差别的任意加载；使用最窄的合理域/本地网络例外。为 Network.framework 显式配置 TLS。在 `swift-security` 中保留深度信任和 SPKI 固定设计。

## 常见错误

**不要**：使用动态输入强制解包 `URL(string:)`。
**要**：使用适当的错误处理使用 `URL(string:)`。仅当字符串为编译时常量时，强制解包才是可接受的。

**不要**：在主线程上对大型有效负载进行 JSON 解码。
**要**：保持解码在 URLSession 调用的调用上下文中，默认情况下为非主线程。仅当更新 UI 状态时才跳转到 `@MainActor`。

**不要**：忽略长时间运行的网络任务中的取消。
**要**：在循环（分页、流式传输、重试）中检查 `Task.isCancelled` 或调用 `try Task.checkCancellation()`。在 SwiftUI 中使用 `.task` 以自动取消。

**不要**：当 URLSession async/await 处理需求时使用 Alamofire 或 Moya。
**要**：直接使用 URLSession。使用 async/await 时，第三方库的便利性差距不再存在。将第三方库保留为确实缺少的功能（例如，图像缓存）。

**不要**：在测试中直接模拟 URLSession。
**要**：使用 `URLProtocol` 子类进行传输级模拟，或使用接受测试替身的基于协议的客户端。

**不要**：从 `body` 或视图初始化器触发网络请求。
**要**：使用 `.task` 或 `.task(id:)` 触发网络调用。

## 审查清单

- [ ] 前台传输使用 async/await；后台会话使用委托/任务 API
- [ ] 错误处理涵盖 URLError 案例(.notConnectedToInternet, .timedOut, .cancelled)
- [ ] 请求是可取消的（通过 `.task` 修饰符或存储的任务引用尊重任务取消）
- [ ] 身份验证令牌通过中间件注入，而不是硬编码
- [ ] 在解码之前验证响应的 HTTP 状态码
- [ ] 大型下载使用 `download(for:)` 而不是 `data(for:)`
- [ ] 网络调用发生在 `@MainActor` 之外（仅在主线程上更新 UI）
- [ ] URLSession 配置了适当的超时和缓存
- [ ] 生产客户端注入配置的会话，而不是使用 `URLSession.shared`
- [ ] 后台传输使用任务/委托 API，而不是异步便利 API
- [ ] 重试逻辑排除取消和 4xx 客户端错误
- [ ] 分页在页面之间检查 `Task.isCancelled`
- [ ] 敏感令牌存储在 Keychain 中（不是 UserDefaults 或纯文件）
- [ ] 不要从动态输入强制解包 URL
- [ ] 解码服务器错误响应并显示给用户
- [ ] Network.framework 代码显式配置 TLS/信任，并将深度固定工作保留在 `swift-security` 中
- [ ] `NetworkConnection<QUIC>` 流 API 被视为异步抛出
- [ ] 确保网络响应模型类型符合 Sendable；使用 @MainActor 用于更新 UI 的完成路径

## 参考资料

- 有关完整的 API 客户端实现、多部分上传、下载进度、URLProtocol 模拟、重试/退避、证书固定、请求日志记录和分页实现的详细信息，请参阅 [参考资料/urlsession-patterns.md](references/urlsession-patterns.md)。
- 有关后台 URLSession 配置、后台下载/上传、具有结构化并发的 WebSocket 模式和重连策略的详细信息，请参阅 [参考资料/background-websocket.md](references/background-websocket.md)。
- 有关轻量级闭包客户端模式（通过 init 注入的异步闭包结构）的详细信息，请参阅 [参考资料/lightweight-clients.md](references/lightweight-clients.md)。
- 有关 Network.framework（NWConnection、NWListener、NWBrowser、NWPathMonitor）和低级 TCP/UDP/WebSocket 模式的详细信息，请参阅 [参考资料/network-framework.md](references/network-framework.md)。
- 有关文件系统目录选择、FileProtectionType、备份排除和存储压力处理的详细信息，请参阅 [参考资料/file-storage-patterns.md](references/file-storage-patterns.md)。
