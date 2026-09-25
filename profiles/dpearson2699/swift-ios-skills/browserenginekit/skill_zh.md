# BrowserEngineKit

用于在 iOS 和 iPadOS 上构建具有替代（非 WebKit）渲染引擎的浏览器的框架。为自行实现 HTML/CSS/JavaScript 引擎的浏览器应用提供进程隔离、XPC 通信、能力管理和系统集成。示例目标为 Swift 6.3 和当前 Apple SDK。

BrowserEngineKit 是一个专业框架。替代浏览器引擎只能通过 Apple 批准的授权配置文件和支持区域的设备资格获得。欧盟支持适用于 iOS 17.4+ 和 iPadOS 18+ 的合格用户；日本支持从 iOS 26.2 开始，并为浏览器应用添加了显式的 PAC/MIE 安全要求。开发和使用可以在任何地方进行。配套框架 BrowserEngineCore（低级原语）和 BrowserKit（资格检查、数据传输）支持整体工作流程。

## 内容
- [概述和资格](#概述和资格)
- [授权](#授权)
- [架构](#架构)
- [进程管理](#进程管理)
- [扩展类型](#扩展类型)
- [能力](#能力)
- [层宿主和视图协调](#层宿主和视图协调)
- [文本交互](#文本交互)
- [沙盒和安全](#沙盒和安全)
- [下载](#下载)
- [常见错误](#常见错误)
- [审查清单](#审查清单)
- [参考资料](#参考资料)

## 概述和资格

### 资格检查

使用 BrowserKit 框架中的 `BEAvailability` 检查设备是否有资格使用替代浏览器引擎。`BEAvailability` 在 iOS/iPadOS 18.4+ 上可用：

```swift
import BrowserKit

do {
    let eligible = try await BEAvailability.isEligible(for: .webBrowser)
    guard eligible else { return /* 回退或解释 */ }
    // 设备支持替代浏览器引擎
} catch {
    // 处理资格查找失败
}
```

资格取决于设备区域和操作系统版本。不要硬编码区域检查；依赖系统 API。

可用性锚点：进程 API 为 iOS/iPadOS 17.4+，`BEDownloadMonitor` 为 iOS 18.2+，`.revision2` 限制沙盒为 iOS 26+，`RenderingExtensionFeature.coreML` 为 iOS 26.2+。

## 授权

### 浏览器应用（宿主）

宿主应用需要两个授权：

| 授权 | 目的 |
|---|---|
| `com.apple.developer.web-browser` | 启用默认浏览器候选资格 |
| `com.apple.developer.web-browser-engine.host` | 启用替代引擎扩展 |

两者都必须向 Apple 申请。申请过程因地区而异。

### 扩展授权

每个扩展目标都需要将其类型特定的授权设置为 `true`：

| 扩展类型 | 授权 |
|---|---|
| Web 内容 | `com.apple.developer.web-browser-engine.webcontent` |
| 网络连接 | `com.apple.developer.web-browser-engine.networking` |
| 渲染 | `com.apple.developer.web-browser-engine.rendering` |

### 可选授权

| 授权 | 扩展 | 目的 |
|---|---|---|
| `com.apple.security.cs.allow-jit` | Web 内容 | 脚本的 JIT 编译 |
| `com.apple.developer.kernel.extended-virtual-addressing` | Web 内容 | 与 JIT 一起使用 |
| `com.apple.developer.memory.transfer_send` | 渲染 | 发送内存归属；值为宿主应用捆绑包 ID |
| `com.apple.developer.memory.transfer_accept` | Web 内容 | 接受内存归属；值为宿主应用捆绑包 ID |
| `com.apple.developer.web-browser-engine.restrict.notifyd` | Web 内容 | 限制通知守护进程访问 |

### 嵌入式浏览器引擎（非浏览器应用）

不是浏览器但嵌入替代引擎用于应用内浏览的应用使用不同的授权：

| 授权 | 目的 |
|---|---|
| `com.apple.developer.embedded-web-browser-engine` | 启用嵌入式引擎 |
| `com.apple.developer.embedded-web-browser-engine.engine-association` | 声明引擎所有权 |

`engine-association` 从 iOS/iPadOS/Mac Catalyst 26.2 开始可用，当您拥有引擎时设置为 `first-party`，当其他开发者拥有它时设置为 `third-party`。嵌入式引擎仅使用 `arm64`（不使用 `arm64e`），不能包含浏览器扩展，也不能使用 JIT 编译。

### 日本特定要求

在日本发布的浏览器应用支持 iOS 26.2+，并且必须采用 Apple 为日本列出的当前安全缓解措施，包括相关分配器和扩展进程的指针认证码和内存完整性强制执行。使用 `com.apple.security.hardened-process.checked-allocations` 启用硬件内存标记；Apple 强烈建议在欧盟也启用它。

## 架构

使用 BrowserEngineKit 构建的浏览器由四个在单独进程中运行的组件组成：

```
宿主应用（UI，协调）
  |
  |-- XPC --> Web 内容扩展（HTML 解析，JS，DOM）
  |-- XPC --> 网络连接扩展（URLSession，套接字）
  |-- XPC --> 渲染扩展（Metal，GPU，媒体）
```

宿主应用启动和管理所有扩展。扩展不能启动其他扩展。扩展通过宿主应用中介的匿名 XPC 端点相互通信。

### 引导序列

1. 宿主启动 Web 内容、网络和渲染扩展
2. 宿主为每个扩展创建 XPC 连接
3. 宿主从网络和渲染扩展请求匿名 XPC 端点
4. 宿主通过引导消息将两个端点发送到 Web 内容扩展
5. Web 内容扩展直接连接到网络和渲染

这种架构遵循最小权限原则：Web 内容扩展处理不受信任的数据，但没有直接访问 OS 资源。

## 进程管理

### 启动扩展

每种扩展类型在宿主应用中都有一个相应的进程类：

```swift
import BrowserEngineKit

// Web 内容（每个选项卡或 iframe 一个）
let contentProcess = try await WebContentProcess(
    bundleIdentifier: nil,
    onInterruption: {
        // 处理崩溃或 OS 中断
    }
)

// 网络连接（通常一个实例）
let networkProcess = try await NetworkingProcess(
    bundleIdentifier: nil,
    onInterruption: {
        // 处理中断
    }
)

// 渲染 / GPU（通常一个实例）
let renderingProcess = try await RenderingProcess(
    bundleIdentifier: nil,
    onInterruption: {
        // 处理中断
    }
)
```

将 `bundleIdentifier` 传递为 `nil` 以使用默认扩展目标。如果扩展崩溃或被 OS 终止，中断处理程序会触发。

### 创建 XPC 连接

```swift
let connection = try contentProcess.makeLibXPCConnection()
// 使用连接进行进程间消息传递
```

每种进程类型都提供 `makeLibXPCConnection()` 来创建用于通信的 `xpc_connection_t`。

### 停止扩展

```swift
contentProcess.invalidate()
```

调用 `invalidate()` 后，进程对象上的任何进一步方法调用都不再有效。

## 扩展类型

### Web 内容扩展

宿主浏览器引擎的 HTML 解析器、CSS 引擎、JavaScript 解释器和 DOM。实现 `WebContentExtension` 以处理传入的 XPC 连接：

```swift
import BrowserEngineKit

@main
struct MyWebContentExtension: WebContentExtension {
    func handle(xpcConnection: xpc_connection_t) {
        // 在连接上设置消息处理程序
    }
}
```

通过扩展的 `EXAppExtensionAttributes` 中的 `WebContentExtensionConfiguration` 进行配置。

### 网络连接扩展

使用 `URLSession` 或套接字 API 处理所有网络请求。一个实例服务于所有选项卡：

```swift
import BrowserEngineKit

@main
struct MyNetworkingExtension: NetworkingExtension {
    func handle(xpcConnection: xpc_connection_t) {
        // 处理网络请求消息
    }
}
```

通过 `NetworkingExtensionConfiguration` 进行配置。

### 渲染扩展

通过 Metal 访问 GPU 进行视频解码、合成和复杂渲染。一个实例通常服务于整个浏览器：

```swift
import BrowserEngineKit

@main
struct MyRenderingExtension: RenderingExtension {
    init() {
        if #available(iOS 26.2, macOS 26.2, *) {
            enableFeature(.coreML)
        }
    }

    func handle(xpcConnection: xpc_connection_t) {
        // 处理渲染命令
    }
}
```

通过 `RenderingExtensionConfiguration` 进行配置。

## 能力

向扩展授予能力，以便 OS 适当地调度它们：

```swift
// 向扩展授予前台优先级
let grant = try contentProcess.grantCapability(.foreground)

// ... 扩展执行前台工作 ...

// 完成时释放
grant.invalidate()
```

### 可用能力

| 能力 | 用例 |
|---|---|
| `.foreground` | 活动选项卡渲染，可见内容 |
| `.background` | 背景任务，预取 |
| `.suspended` | 最小活动，待清理 |
| `.mediaPlaybackAndCapture(environment:)` | 音频/视频播放，相机/麦克风捕获 |

### 媒体环境

对于媒体能力，创建一个与页面 URL 关联的 `MediaEnvironment`。环境支持 `AVCaptureSession` 用于相机/麦克风访问，并且是 XPC-可序列化的，用于跨进程传输：

```swift
let mediaEnv = MediaEnvironment(webPage: pageURL)
let grant = try contentProcess.grantCapability(
    .mediaPlaybackAndCapture(environment: mediaEnv)
)
try mediaEnv.activate()
let captureSession = try mediaEnv.makeCaptureSession()
```

### 可见性传播

将可见性传播交互附加到浏览器视图，以便扩展知道内容何时在屏幕上。`WebContentProcess` 和 `RenderingProcess` 都提供 `createVisibilityPropagationInteraction()`。

## 层宿主和视图协调

渲染扩展绘制到 `LayerHierarchy`，宿主应用通过 `LayerHierarchyHostingView` 显示其内容。通过 XPC 传递句柄。使用 `LayerHierarchyHostingTransactionCoordinator` 在进程之间同步层更新原子操作。

有关详细的层宿主示例和事务协调，请参阅 [references/browserenginekit-patterns.md](references/browserenginekit-patterns.md)。

## 文本交互

在自定义文本视图上采用 `BETextInput` 以集成 UIKit 的文本系统。这启用了标准文本选择、自动更正、听写和键盘交互。

关键集成点：

- `asyncInputDelegate` 用于向系统传达文本更改
- `handleKeyEntry(_:completionHandler:)` 用于键盘事件
- `BETextInteraction` 用于选择手势、编辑菜单和上下文菜单
- `BEScrollView` 和 `BEScrollViewDelegate` 用于自定义滚动处理

有关详细的文本交互实现，请参阅 [references/browserenginekit-patterns.md](references/browserenginekit-patterns.md)。

## 沙盒和安全

### 限制沙盒

初始化后，使用限制沙盒锁定内容扩展：

```swift
// 在 Web 内容扩展中，设置后：
if #available(iOS 26.0, macOS 26.0, *) {
    applyRestrictedSandbox(revision: .revision2)
} else {
    applyRestrictedSandbox(revision: .revision1)
}
```

这将移除扩展在启动时使用但在不再需要的资源访问。使用最新可用的修订版以获得最严格的限制。

### JIT 编译

JIT 编译 JavaScript 的 Web 内容扩展必须使用 BrowserEngineKit 的见证 API 过渡页面：

```swift
import BrowserEngineCore

be_memory_inline_jit_restrict_rwx_to_rw_with_witness(...)
// 写入生成的代码
be_memory_inline_jit_restrict_rwx_to_rx_with_witness(...)
```

需要在 Web 内容扩展上仅具有 `com.apple.security.cs.allow-jit` 和 `com.apple.developer.kernel.extended-virtual-addressing` 授权。如果实现改用 `pthread_jit_write_with_callback_np`，它还需要 JIT 写入允许列表授权；不要单独呈现 `BE_JIT_WRITE_PROTECT_TAG` 作为完整的保护策略。

### arm64e 要求

发布构建必须满足当前替代浏览器授权配置文件中的设备架构、PAC 和 MIE 要求。保持宿主和扩展配置一致，包含所需的设备切片，并在合格设备上测试签名的存档。嵌入式引擎不同：它们仅使用 arm64，不能使用 JIT。不要在模拟器构建上强制 `arm64e`，也不要复制一行 `ARCHS` 覆盖指令以丢弃所需切片。

## 下载

使用 `BEDownloadMonitor` 向系统报告下载进度。创建访问令牌，使用源/目标 URL 和 `Progress` 对象初始化监视器，然后调用 `beginMonitoring()` 以显示系统下载 UI。使用 `resumeMonitoring(placeholderURL:)` 恢复中断的下载。`BEDownloadMonitor` 在 iOS 18.2+ 上可用。

有关完整的下载管理示例，请参阅 [references/browserenginekit-patterns.md](references/browserenginekit-patterns.md)。

## 常见错误

### 不要：跳过引导序列

```swift
// 错误 - 内容扩展没有路径到其他扩展
let contentProcess = try await WebContentProcess(
    bundleIdentifier: nil, onInterruption: {}
)
// 立即开始发送工作而不连接到网络和渲染

// 正确 - 通过宿主应用中介连接
let networkEndpoint = try await networkProxy.getEndpoint()
let renderEndpoint = try await renderProxy.getEndpoint()
try await contentProxy.bootstrap(
    renderingExtension: renderEndpoint,
    networkExtension: networkEndpoint
)
```

### 不要：从其他扩展启动扩展

```swift
// 错误 - 扩展不能启动其他扩展
// (在 WebContentExtension 内部)
let network = try await NetworkingProcess(...)

// 正确 - 只有宿主应用启动扩展
// 宿主应用创建所有进程，然后中介连接
```

### 不要：在无效化后使用扩展进程对象

```swift
// 错误
contentProcess.invalidate()
let conn = try contentProcess.makeLibXPCConnection()  // 错误

// 正确 - 如需，创建新进程
let newProcess = try await WebContentProcess(
    bundleIdentifier: nil, onInterruption: {}
)
```

### 不要：将 JIT 授权应用于非内容扩展

JIT 编译授权 (`com.apple.security.cs.allow-jit`) 仅在 Web 内容扩展上有效。将它们添加到宿主应用、渲染扩展或网络连接扩展会导致 App Store 拒绝。

### 不要：硬编码区域资格

```swift
// 错误
if Locale.current.region?.identifier == "DE" {
    useAlternativeEngine()
}

// 正确 - 使用系统资格 API
let eligible = try await BEAvailability.isEligible(for: .webBrowser)
if eligible {
    useAlternativeEngine()
}
```

### 不要：忘记设置 UIRequiredDeviceCapabilities

没有 `web-browser-engine` 在 `UIRequiredDeviceCapabilities` 中，不支持设备的用户可以下载应用并遇到运行时失败。

## 审查清单

- [ ] 宿主应用具有 `com.apple.developer.web-browser-engine.host` 授权
- [ ] 每个扩展具有其类型特定的授权
- [ ] `UIRequiredDeviceCapabilities` 包括 `web-browser-engine`
- [ ] 所有 iOS 设备目标配置为 `arm64e` 指令集
- [ ] 模拟器目标不设置 `arm64e`
- [ ] 使用 `iOSPackagesShouldBuildARM64e` 工作区设置构建 Swift 包
- [ ] 每个扩展的 Info.plist 中正确设置扩展点标识符
- [ ] 所有进程类型实现了中断处理程序
- [ ] 引导序列将内容扩展连接到网络和渲染
- [ ] 在开始工作前授予能力，并在完成后释放
- [ ] 将可见性传播交互添加到浏览器内容视图
- [ ] 内容扩展初始化后应用限制沙盒
- [ ] 使用 `BEAvailability` 进行资格检查而不是手动区域逻辑
- [ ] 内存归属授权值使用宿主应用捆绑包 ID
- [ ] iOS 18.2+ 上通过 `BEDownloadMonitor` 报告活动下载的进度
- [ ] 在 iOS 26.2+ 上为日本分发启用内存标记（建议在欧盟启用）

## 参考资料
- 扩展模式（文本交互、层宿主、滚动视图、文件书签、XPC 通信、内容过滤）：[references/browserenginekit-patterns.md](references/browserenginekit-patterns.md)
- [BrowserEngineKit 框架](https://sosumi.ai/documentation/browserenginekit)
- [设计您的浏览器架构](https://sosumi.ai/documentation/browserenginekit/designing-your-browser-architecture)
- [在 Xcode 中创建浏览器扩展](https://sosumi.ai/documentation/browserenginekit/creating-browser-extensions-in-xcode)
- [管理浏览器扩展生命周期](https://sosumi.ai/documentation/browserenginekit/managing-the-browser-extension-lifecycle)
- [使用 XPC 与浏览器扩展通信](https://sosumi.ai/documentation/browserenginekit/using-xpc-to-communicate-with-browser-extensions)
- [Web 浏览器引擎授权](https://sosumi.ai/documentation/bundleresources/entitlements/com.apple.developer.web-browser-engine.host)
- [BrowserKit 框架](https://sosumi.ai/documentation/browserkit)
- [BrowserEngineCore 框架](https://sosumi.ai/documentation/browserenginecore)
- [示例：使用替代引擎开发浏览器应用](https://sosumi.ai/documentation/browserenginekit/developing-a-browser-app-that-uses-an-alternative-browser-engine)
