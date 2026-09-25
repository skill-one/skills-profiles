# CallKit

使用 CallKit 和 PushKit 构建 VoIP 通话功能，使其与原生 iOS 通话 UI 集成。涵盖传入/传出通话流程、VoIP 推送注册、音频会话协调和通话目录扩展。

## 目录

- [设置](#设置)
- [提供者配置](#提供者配置)
- [传入通话流程](#传入通话流程)
- [传出通话流程](#传出通话流程)
- [PushKit VoIP 注册](#pushkit-voip 注册)
- [音频会话协调](#音频会话协调)
- [通话目录扩展和经理](#通话目录扩展和经理)
- [常见错误](#常见错误)
- [审查清单](#审查清单)
- [参考资料](#参考资料)

## 设置

### 项目配置

1. 在“签名与能力”中启用 **VoIP** 后台模式
2. 添加 **推送通知** 能力
3. 对于通话目录扩展，添加一个 **通话目录扩展** 目标

### 关键类型

| 类型 | 角色 |
|---|---|
| `CXProvider` | 向系统报告通话，接收通话操作 |
| `CXCallController` | 请求通话操作（开始、结束、保持、静音） |
| `CXCallUpdate` | 描述通话元数据（来电者姓名、视频、处理方式） |
| `CXProviderDelegate` | 处理系统通话操作和音频会话事件 |
| `PKPushRegistry` | 注册并接收 VoIP 推送通知 |
| `PKVoIPPushMetadata` | iOS 26.4+ 元数据，说明是否必须报告 VoIP 推送 |

## 提供者配置

在应用启动时创建一个 `CXProvider` 并在整个应用生命周期中保持其活跃。使用 `CXProviderConfiguration` 配置您的通话功能。

```swift
import CallKit

/// CXProvider 将所有委托调用分派到传递给 `setDelegate(_:queue:)` 的队列中。
/// `let` 属性初始化一次且永不修改，因此尽管有 @unchecked Sendable，此类型可以跨并发域安全共享。
final class CallManager: NSObject, @unchecked Sendable {
    static let shared = CallManager()

    let provider: CXProvider
    let callController = CXCallController()

    private override init() {
        let config = CXProviderConfiguration()
        config.localizedName = "我的 VoIP 应用"
        config.supportsVideo = true
        config.maximumCallsPerCallGroup = 1
        config.maximumCallGroups = 2
        config.supportedHandleTypes = [.phoneNumber, .emailAddress]
        config.includesCallsInRecents = true

        provider = CXProvider(configuration: config)
        super.init()
        provider.setDelegate(self, queue: nil)
    }
}
```

## 传入通话流程

当接收到必要的 VoIP 通话推送时，立即向 CallKit 报告传入通话。系统显示原生通话 UI。您必须在 PushKit 完成处理之前报告必要的通话——否则会导致系统终止您的应用。

```swift
func reportIncomingCall(
    uuid: UUID,
    handle: String,
    hasVideo: Bool
) async throws {
    let update = CXCallUpdate()
    update.remoteHandle = CXHandle(type: .phoneNumber, value: handle)
    update.hasVideo = hasVideo
    update.localizedCallerName = "Jane Doe"

    try await withCheckedThrowingContinuation {
        (continuation: CheckedContinuation<Void, Error>) in
        provider.reportNewIncomingCall(
            with: uuid,
            update: update
        ) { error in
            if let error {
                continuation.resume(throwing: error)
            } else {
                continuation.resume()
            }
        }
    }
}
```

### 处理应答操作

实现 `CXProviderDelegate` 以在用户应答时响应：

```swift
extension CallManager: CXProviderDelegate {
    func providerDidReset(_ provider: CXProvider) {
        // 结束所有通话，重置音频
    }

    func provider(_ provider: CXProvider, perform action: CXAnswerCallAction) {
        // 准备音频，然后在通话实际准备好后仅完成
        configureAudioSession()
        connectToCallServer(callUUID: action.callUUID) { success in
            if success {
                action.fulfill()
            } else {
                provider.reportCall(
                    with: action.callUUID,
                    endedAt: Date(),
                    reason: .failed
                )
                action.fail()
            }
        }
    }

    func provider(_ provider: CXProvider, perform action: CXEndCallAction) {
        disconnectFromCallServer(callUUID: action.callUUID)
        action.fulfill()
    }
}
```

## 传出通话流程

使用 `CXCallController` 请求传出通话。系统将请求通过您的 `CXProviderDelegate` 路由。

```swift
func startOutgoingCall(handle: String, hasVideo: Bool) {
    let uuid = UUID()
    let handle = CXHandle(type: .phoneNumber, value: handle)
    let startAction = CXStartCallAction(call: uuid, handle: handle)
    startAction.isVideo = hasVideo

    let transaction = CXTransaction(action: startAction)
    callController.request(transaction) { error in
        if let error {
            print("启动通话失败: \(error)")
        }
    }
}
```

### 传出通话的委托方法

```swift
extension CallManager {
    func provider(_ provider: CXProvider, perform action: CXStartCallAction) {
        configureAudioSession()
        // 开始连接到服务器
        provider.reportOutgoingCall(
            with: action.callUUID,
            startedConnectingAt: Date()
        )

        connectToServer(callUUID: action.callUUID) {
            provider.reportOutgoingCall(
                with: action.callUUID,
                connectedAt: Date()
            )
        }
        action.fulfill()
    }
}
```

## PushKit VoIP 注册

在每次应用启动时注册 VoIP 推送，并将令牌更改发送到您的服务器。对于 iOS 13 SDK+ 应用，每个需要报告的 VoIP 通话推送都必须在使用 CallKit 或 LiveCommunicationKit（对于基于该框架构建的应用）之前报告。在 iOS 26.4+ 中，`PKVoIPPushMetadata.mustReport` 是关键：`true` 表示在完成前报告；`false` 表示不需要 CallKit 或 LiveCommunicationKit 报告。在完成前遗漏必要的报告可能会导致应用终止，重复失败可能会停止 VoIP 交付。

| 路径 | 报告决策 | 完成时间 |
|---|---|---|
| iOS 26.4+ `mustReport == true` | 使用 CallKit 或 LiveCommunicationKit 报告 | 报告回调后 |
| iOS 26.4+ `mustReport == false` | 不需要 CallKit/LiveCommunicationKit 报告 | 本地处理后 |
| 旧委托 | iOS 13 SDK+ 将 VoIP 通话推送视为需要报告 | 报告回调后 |

```swift
import PushKit

final class PushManager: NSObject, PKPushRegistryDelegate {
    let registry: PKPushRegistry

    override init() {
        registry = PKPushRegistry(queue: .main)
        super.init()
        registry.delegate = self
        registry.desiredPushTypes = [.voIP]
    }

    func pushRegistry(
        _ registry: PKPushRegistry,
        didUpdate pushCredentials: PKPushCredentials,
        for type: PKPushType
    ) {
        let token = pushCredentials.token
            .map { String(format: "%02x", $0) }
            .joined()
        // 将令牌发送到您的服务器
        sendTokenToServer(token)
    }

    @available(iOS 26.4, *)
    func pushRegistry(
        _ registry: PKPushRegistry,
        didReceiveIncomingVoIPPushWith payload: PKPushPayload,
        metadata: PKVoIPPushMetadata,
        withCompletionHandler completion: @escaping @Sendable () -> Void
    ) {
        guard metadata.mustReport else {
            completion()
            return
        }
        handleIncomingVoIPPush(payload, completion: completion)
    }

    // 为 iOS 26.0-26.3 和旧部署目标保留旧回调。
    func pushRegistry(
        _ registry: PKPushRegistry,
        didReceiveIncomingPushWith payload: PKPushPayload,
        for type: PKPushType,
        completion: @escaping () -> Void
    ) {
        guard type == .voIP else {
            completion()
            return
        }

        handleIncomingVoIPPush(payload, completion: completion)
    }

    private func handleIncomingVoIPPush(
        _ payload: PKPushPayload,
        completion: @escaping () -> Void
    ) {
        let callUUID = UUID()
        let handle = payload.dictionaryPayload["handle"] as? String ?? "未知"

        Task {
            do {
                try await CallManager.shared.reportIncomingCall(
                    uuid: callUUID,
                    handle: handle,
                    hasVideo: false
                )
            } catch {
                // 通话被 DND 或阻止列表过滤
            }
            completion()
        }
    }
}
```

服务器端的 VoIP 推送应使用短生命周期：将 `apns-expiration` 设置为 `0` 或仅几秒钟。在初始推送唤醒应用后，通过应用-服务器连接发送挂断和通话详情更改，而不是发送更多 VoIP 推送。

## 音频会话协调

CallKit 拥有音频激活边界：仅在 `provider(_:didActivate:)` 中开始媒体，并在 `provider(_:didDeactivate:)` 和重置路径中停止或拆除。

```swift
extension CallManager {
    func provider(_ provider: CXProvider, didActivate audioSession: AVAudioSession) {
        // 音频会话现在处于活动状态——启动音频引擎 / WebRTC
        startAudioEngine()
    }

    func provider(_ provider: CXProvider, didDeactivate audioSession: AVAudioSession) {
        // 音频会话停用——停止音频引擎
        stopAudioEngine()
    }

    func configureAudioSession() {
        let session = AVAudioSession.sharedInstance()
        do {
            try session.setCategory(
                .playAndRecord,
                mode: .voiceChat,
                options: [.allowBluetooth, .allowBluetoothA2DP]
            )
        } catch {
            print("音频会话配置失败: \(error)")
        }
    }
}
```

## 通话目录扩展和经理

使用通话目录进行预加载来电者 ID/阻止，而不是每次通话的 API 查找。扩展在 `beginRequest(with:)` 中加载排序的批量数据；主应用使用 `CXCallDirectoryManager` 检查启用状态，在禁用时打开通话阻止和识别设置，并在数据更改后重新加载。将 `CXCallDirectoryPhoneNumber` 存储为国家代码加数字，按升序排序（例如 `18005551234`），而不是格式化字符串。

```swift
import CallKit

final class CallDirectoryHandler: CXCallDirectoryProvider {
    override func beginRequest(
        with context: CXCallDirectoryExtensionContext
    ) {
        if context.isIncremental {
            addOrRemoveIncrementalEntries(to: context)
        } else {
            addAllEntries(to: context)
        }
        context.completeRequest()
    }

    private func addAllEntries(
        to context: CXCallDirectoryExtensionContext
    ) {
        // 国家代码加数字，按升序排序
        let blockedNumbers: [CXCallDirectoryPhoneNumber] = [
            18005551234, 18005555678
        ]
        for number in blockedNumbers {
            context.addBlockingEntry(
                withNextSequentialPhoneNumber: number
            )
        }

        let identifiedNumbers: [(CXCallDirectoryPhoneNumber, String)] = [
            (18005551111, "本地披萨店"),
            (18005552222, "牙科诊所")
        ]
        for (number, label) in identifiedNumbers {
            context.addIdentificationEntry(
                withNextSequentialPhoneNumber: number,
                label: label
            )
        }
    }
}
```

### 主应用经理：状态、设置、重新加载

```swift
let manager = CXCallDirectoryManager.sharedInstance
manager.getEnabledStatusForExtension(withIdentifier: extensionID) { status, _ in
    guard status == .enabled else {
        manager.openSettings { _ in } // 通话阻止和识别
        return
    }
    manager.reloadExtension(withIdentifier: extensionID) { _ in }
}
```

在假设扩展处于活动状态之前检查 `getEnabledStatusForExtension(...)`，在禁用时使用 `openSettings(...)` 进行通话阻止和识别，并在数据更改后调用 `reloadExtension(...)`。将 APNs 认证密钥轮换和正常远程通知设置路由到推送通知。

## 常见错误

| 错误 | 修复 |
|---|---|
| 必要的 VoIP 推送被视为仅数据 | 应用特定版本的报告规则，在完成前报告，然后调用 PushKit 完成处理。 |
| 应答操作在媒体/服务器就绪前完成 | 保持挂起状态直到连接完成；就绪时完成或在失败时报告 `.failed`。 |
| 媒体在 `provider(_:didActivate:)` 前启动 | 如果需要，提前准备，但仅在激活后启动，并在停用/重置时停止。 |
| 某个操作路径从未调用 `fulfill()` 或 `fail()` | 为成功、取消、超时和网络错误路径提供终端操作。 |
| 令牌刷新被忽略 | 将每个 `didUpdate pushCredentials` 令牌发送到服务器。 |
| 通话目录执行每次通话的网络 | 预加载排序的条目并重新加载扩展。 |

## 审查清单

- [ ] 能力中启用 VoIP 后台模式
- [ ] 在应用启动时创建单个 `CXProvider` 实例并保持其活跃
- [ ] 在报告任何通话之前设置 `CXProviderDelegate`
- [ ] iOS 26.4+ PushKit 路径在 `mustReport` 为 true 时报告，在为 false 时可能跳过
- [ ] iOS 13 SDK+ PushKit VoIP 通话推送在完成前报告给 CallKit
- [ ] VoIP APNs 请求使用 `apns-expiration` 为 `0` 或仅几秒钟
- [ ] 挂断和详情更新在初始推送后使用应用-服务器连接
- [ ] 每个提供者委托操作都调用了 `action.fulfill()` 或 `action.fail()` 
- [ ] 仅在通话服务器/媒体连接就绪后完成 `CXAnswerCallAction`
- [ ] 仅在 `provider(_:didActivate:)` 回调后启动音频引擎
- [ ] 在 `provider(_:didDeactivate:)` 回调中停止音频引擎
- [ ] 音频会话类别设置为 `.playAndRecord` 并使用 `.voiceChat` 模式
- [ ] 每个 `didUpdate pushCredentials` 回调都将 VoIP 推送令牌发送到服务器
- [ ] 在每次应用启动时创建 `PKPushRegistry`（不是懒加载）
- [ ] 通话目录数据预加载，而不是每次传入通话时获取
- [ ] 文档中 `CXCallDirectoryPhoneNumber` 为国家代码加数字
- [ ] `CXCallDirectoryManager` 命名状态检查、重新加载和设置打开 API
- [ ] `CXCallUpdate` 使用 `localizedCallerName` 和 `remoteHandle` 填充
- [ ] 传出通话报告 `startedConnectingAt` 和 `connectedAt` 时间戳
- [ ] iOS 26 通话翻译在静音期间保持上游音频活动
- [ ] 加密元数据过滤提及通知服务扩展权限

## 参考资料

- 扩展模式（保持、静音、组通话、委托生命周期）：[references/callkit-patterns.md](references/callkit-patterns.md)
- [CallKit 框架](https://sosumi.ai/documentation/callkit)
- [CXProvider](https://sosumi.ai/documentation/callkit/cxprovider)
- [CXCallController](https://sosumi.ai/documentation/callkit/cxcallcontroller)
- [CXCallAction](https://sosumi.ai/documentation/callkit/cxcallaction)
- [CXCallUpdate](https://sosumi.ai/documentation/callkit/cxcallupdate)
- [CXProviderConfiguration](https://sosumi.ai/documentation/callkit/cxproviderconfiguration)
- [CXProviderDelegate](https://sosumi.ai/documentation/callkit/cxproviderdelegate)
- [PKPushRegistry](https://sosumi.ai/documentation/pushkit/pkpushregistry)
- [PKPushRegistryDelegate](https://sosumi.ai/documentation/pushkit/pkpushregistrydelegate)
- [PKVoIPPushMetadata](https://sosumi.ai/documentation/pushkit/pkvoippushmetadata)
- [CXCallDirectoryProvider](https://sosumi.ai/documentation/callkit/cxcalldirectoryprovider)
- [CXCallDirectoryPhoneNumber](https://sosumi.ai/documentation/callkit/cxcalldirectoryphonenumber)
- [CXCallDirectoryManager](https://sosumi.ai/documentation/callkit/cxcalldirectorymanager)
- [CXSetTranslatingCallAction](https://sosumi.ai/documentation/callkit/cxsettranslatingcallaction)
- [reportNewIncomingVoIPPushPayload(_:completion:)](https://sosumi.ai/documentation/callkit/cxprovider/reportnewincomingvoippushpayload(_:completion:))
- [发起和接收 VoIP 通话](https://sosumi.ai/documentation/callkit/making-and-receiving-voip-calls)
- [响应来自 PushKit 的 VoIP 通知](https://sosumi.ai/documentation/pushkit/responding-to-voip-notifications-from-pushkit)
