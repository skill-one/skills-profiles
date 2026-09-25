# CoreNFC

使用 CoreNFC 框架在 iPhone 上读取和写入 NFC 标签。涵盖 NDEF 读取会话、标签读取会话、NDEF 消息构建、权限、以及后台标签读取。

## 目录

- [设置](#设置)
- [NDEF 读取会话](#ndef-读取会话)
- [标签读取会话](#标签读取会话)
- [写入 NDEF 消息](#写入-ndef-消息)
- [NDEF 载荷类型](#ndef-载荷类型)
- [后台标签读取](#后台标签读取)
- [常见错误](#常见错误)
- [审查清单](#审查清单)
- [参考资料](#参考资料)

## 设置

### 项目配置

1. 在 Xcode 中添加 **近场通信标签读取** 功能
2. 在 Info.plist 中添加 `NFCReaderUsageDescription`，并使用用户可见的说明字符串
3. 添加 `com.apple.developer.nfc.readersession.formats` 权限，并使用当前的 `TAG` 值；不要添加旧的 `NDEF` 权限
4. 对于 ISO 7816 标签，在 Info.plist 中的 `com.apple.developer.nfc.readersession.iso7816.select-identifiers` 添加支持的应标识符
5. 对于 FeliCa 标签，在 Info.plist 中的 `com.apple.developer.nfc.readersession.felica.systemcodes` 添加支持的系统代码；不要使用通配符系统代码

### 设备要求

NFC 读取需要 iPhone 7 或更高版本。在创建 NFC UI 或会话之前，始终检查读取会话的可用性。使用你即将创建的具体读取会话类型。

```swift
import CoreNFC

guard NFCNDEFReaderSession.readingAvailable else {
    // 设备不支持 NFC 或功能受限
    showUnsupportedMessage()
    return
}
```

### 关键类型

| 类型 | 角色 |
|---|---|
| `NFCNDEFReaderSession` | 扫描 NDEF 格式的标签 |
| `NFCTagReaderSession` | 扫描 ISO7816、ISO15693、FeliCa、MIFARE 标签 |
| `NFCNDEFMessage` | NDEF 载荷记录的集合 |
| `NFCNDEFPayload` | NDEF 消息中的单个记录 |
| `NFCNDEFTag` | 与 NDEF 功能标签交互的协议 |

## NDEF 读取会话

使用 `NFCNDEFReaderSession` 从标签读取 NDEF 格式的数据。这是读取标准标签内容（如 URL、文本和 MIME 数据）的最简单路径。

```swift
import CoreNFC

final class NDEFReader: NSObject, NFCNDEFReaderSessionDelegate {
    private var session: NFCNDEFReaderSession?

    func beginScanning() {
        guard NFCNDEFReaderSession.readingAvailable else { return }

        session = NFCNDEFReaderSession(
            delegate: self,
            queue: nil,
            invalidateAfterFirstRead: false
        )
        session?.alertMessage = "将你的 iPhone 靠近一个 NFC 标签。"
        session?.begin()
    }

    // MARK: - NFCNDEFReaderSessionDelegate

    func readerSessionDidBecomeActive(_ session: NFCNDEFReaderSession) {
        // 会话正在扫描
    }

    func readerSession(
        _ session: NFCNDEFReaderSession,
        didDetectNDEFs messages: [NFCNDEFMessage]
    ) {
        for message in messages {
            for record in message.records {
                processRecord(record)
            }
        }
    }

    func readerSession(
        _ session: NFCNDEFReaderSession,
        didInvalidateWithError error: Error
    ) {
        let nfcError = error as? NFCReaderError
        if nfcError?.code != .readerSessionInvalidationErrorFirstNDEFTagRead,
           nfcError?.code != .readerSessionInvalidationErrorUserCanceled {
            print("会话失效: \(error.localizedDescription)")
        }
        self.session = nil
    }
}
```

### 使用标签连接读取

对于读写操作，使用标签检测代理方法连接到单个标签：

```swift
func readerSession(
    _ session: NFCNDEFReaderSession,
    didDetect tags: [any NFCNDEFTag]
) {
    guard let tag = tags.first else {
        session.restartPolling()
        return
    }

    session.connect(to: tag) { error in
        if let error {
            session.invalidate(errorMessage: "连接失败: \(error)")
            return
        }

        tag.queryNDEFStatus { status, capacity, error in
            guard error == nil else {
                session.invalidate(errorMessage: "查询失败。")
                return
            }

            switch status {
            case .notSupported:
                session.invalidate(errorMessage: "标签不符合 NDEF 标准。")
            case .readOnly:
                tag.readNDEF { message, error in
                    if let message {
                        self.processMessage(message)
                    }
                    session.invalidate()
                }
            case .readWrite:
                tag.readNDEF { message, error in
                    if let message {
                        self.processMessage(message)
                    }
                    session.alertMessage = "标签读取成功。"
                    session.invalidate()
                }
            @unknown default:
                session.invalidate()
            }
        }
    }
}
```

## 标签读取会话

当你需要直接访问原生标签协议（ISO 7816、ISO 15693、FeliCa 或 MIFARE）时，使用 `NFCTagReaderSession`。

| 轮询选项 | 标签 |
|---|---|
| `.iso14443` | ISO 7816 兼容和 MIFARE |
| `.iso15693` | ISO 15693 |
| `.iso18092` | FeliCa |

不要使用此会话进行与支付相关的 AIDs。加载 [nfc-patterns.md](references/nfc-patterns.md) 以获取协议特定的连接、APDU、命令和响应处理。

## 写入 NDEF 消息

将 NDEF 数据写入已连接的标签。写入操作前始终检查 `readWrite` 状态。

```swift
func writeToTag(
    tag: any NFCNDEFTag,
    session: NFCNDEFReaderSession,
    url: URL
) {
    tag.queryNDEFStatus { status, capacity, error in
        guard status == .readWrite else {
            session.invalidate(errorMessage: "标签是只读的。")
            return
        }

        guard let payload = NFCNDEFPayload.wellKnownTypeURIPayload(
            url: url
        ) else {
            session.invalidate(errorMessage: "无效的 URL。")
            return
        }

        let message = NFCNDEFMessage(records: [payload])

        tag.writeNDEF(message) { error in
            if let error {
                session.invalidate(
                    errorMessage: "写入失败: \(error.localizedDescription)"
                )
            } else {
                session.alertMessage = "标签写入成功。"
                session.invalidate()
            }
        }
    }
}
```

## NDEF 载荷类型

### 创建常见载荷

```swift
// URL 载荷
let urlPayload = NFCNDEFPayload.wellKnownTypeURIPayload(
    url: URL(string: "https://example.com")!
)

// 文本载荷
let textPayload = NFCNDEFPayload.wellKnownTypeTextPayload(
    string: "Hello NFC",
    locale: Locale(identifier: "en")
)

// 自定义载荷
let customPayload = NFCNDEFPayload(
    format: .nfcExternal,
    type: "com.example:mytype".data(using: .utf8)!,
    identifier: Data(),
    payload: "custom-data".data(using: .utf8)!
)
```

### 解析载荷内容

加载 [解析 NDEF 载荷内容](references/nfc-patterns.md#parsing-ndef-payload-content) 以获取完整的类型名称格式开关和多记录处理。

## 后台标签读取

在 iPhone XS 及更高版本上，iOS 可以在无需打开你的应用的情况下后台读取 NFC 标签。NDEF 消息必须包含 URI 记录（`typeNameFormat == .nfcWellKnown`，类型 `U`）。如果有多个 URI 记录，系统将使用第一个。

对于特定应用的路由，将通用链接写入标签，并为该域配置关联域功能。后台标签读取还支持特定的系统 URL 方案，如网页、电子邮件、短信、电话、FaceTime、地图和 HomeKit 设置。它不支持自定义 URL 方案，系统也不会根据 bundle ID 或任意 NDEF 内容类型进行路由。

当用户点击兼容的标签时，iOS 会显示通知以打开你的应用。通过 `NSUserActivity` 处理标签数据：

```swift
func scene(
    _ scene: UIScene,
    continue userActivity: NSUserActivity
) {
    guard userActivity.activityType ==
        NSUserActivityTypeBrowsingWeb else { return }

    let message = userActivity.ndefMessagePayload
    guard message.records.first?.typeNameFormat != .empty else { return }

    for record in message.records {
        processRecord(record)
    }
}
```

## 常见错误

### 不要：使用过时或缺失的 NFC 权限

没有 `com.apple.developer.nfc.readersession.formats` 权限，读取会话无法访问 NFC 硬件。使用当前的 `TAG` 值进行 Core NFC 读取会话；不要复制旧的示例，这些示例添加了 `NDEF`。

### 不要：忽略会话失效错误

会话因多种原因失效。区分用户取消和实际错误可以防止错误警报。

```swift
// 错误示例 -- 用户取消时显示错误
func readerSession(
    _ session: NFCNDEFReaderSession,
    didInvalidateWithError error: Error
) {
    showAlert("NFC 错误: \(error.localizedDescription)")
}

// 正确示例 -- 过滤预期的失效原因
func readerSession(
    _ session: NFCNDEFReaderSession,
    didInvalidateWithError error: Error
) {
    let nfcError = error as? NFCReaderError
    switch nfcError?.code {
    case .readerSessionInvalidationErrorUserCanceled,
         .readerSessionInvalidationErrorFirstNDEFTagRead:
        break  // 正常终止
    default:
        showAlert("NFC 错误: \(error.localizedDescription)")
    }
    self.session = nil
}
```

### 不要：保留对过时会话的强引用

一旦会话失效，它就无法重新启动。清空你的引用，并为下一次扫描创建新会话。

```swift
// 错误示例 -- 重复使用失效会话
func scanAgain() {
    session?.begin()  // 无效操作，会话已死亡
}

// 正确示例 -- 创建新会话
func scanAgain() {
    session = NFCNDEFReaderSession(
        delegate: self, queue: nil, invalidateAfterFirstRead: false
    )
    session?.begin()
}
```

## 审查清单

- [ ] 在“签名与权限”中添加 NFC 功能
- [ ] 在 Info.plist 中设置 `NFCReaderUsageDescription`
- [ ] `com.apple.developer.nfc.readersession.formats` 权限使用 `TAG`，而不是旧的 `NDEF`
- [ ] 在创建会话前检查 `NFCNDEFReaderSession.readingAvailable` 或 `NFCTagReaderSession.readingAvailable`
- [ ] 在调用 `begin()` 前设置会话代理
- [ ] 会话失效后将会话引用设置为 nil
- [ ] `didInvalidateWithError` 区分用户取消和实际错误
- [ ] 写入操作前查询 NDEF 状态
- [ ] 写入大消息前检查标签容量
- [ ] 使用 `NFCTagReaderSession` 时在 Info.plist 中列出 ISO 7816 应用标识符
- [ ] 使用 `.iso18092` 轮询时在 Info.plist 中列出 FeliCa 系统代码
- [ ] 后台标签读取使用 URI NDEF 记录和通用链接或支持的系统 URL 方案
- [ ] 不使用自定义 URL 方案、bundle ID 或任意 NDEF 内容类型进行后台路由
- [ ] 支付相关的 AIDs 路由到 `NFCTagReaderSession`
- [ ] 同一时间只有一个读取会话激活

## 参考资料

- 扩展模式（ISO 7816 命令、多标签扫描、NDEF 锁定）：[references/nfc-patterns.md](references/nfc-patterns.md)
- [Core NFC 框架](https://sosumi.ai/documentation/corenfc)
- [NFCNDEFReaderSession](https://sosumi.ai/documentation/corenfc/nfcndefreadersession)
- [NFCTagReaderSession](https://sosumi.ai/documentation/corenfc/nfctagreadersession)
- [NFCNDEFMessage](https://sosumi.ai/documentation/corenfc/nfcndefmessage)
- [NFCNDEFPayload](https://sosumi.ai/documentation/corenfc/nfcndefpayload)
- [NFCNDEFTag](https://sosumi.ai/documentation/corenfc/nfcndeftag)
- [NFCNDEFReaderSessionDelegate](https://sosumi.ai/documentation/corenfc/nfcndefreadersessiondelegate)
- [NFCTagReaderSessionDelegate](https://sosumi.ai/documentation/corenfc/nfctagreadersessiondelegate)
- [构建 NFC 标签读取应用](https://sosumi.ai/documentation/corenfc/building_an_nfc_tag-reader_app)
- [添加后台标签读取支持](https://sosumi.ai/documentation/corenfc/adding-support-for-background-tag-reading)
- [近场通信标签读取会话格式权限](https://sosumi.ai/documentation/bundleresources/entitlements/com.apple.developer.nfc.readersession.formats)
- [ISO7816 应用标识符用于 NFC 标签读取会话](https://sosumi.ai/documentation/bundleresources/entitlements/com.apple.developer.nfc.readersession.iso7816.select-identifiers)
- [ISO18092 系统代码用于 NFC 标签读取会话](https://sosumi.ai/documentation/bundleresources/entitlements/com.apple.developer.nfc.readersession.felica.systemcodes)
