# CryptoTokenKit

使用 CryptoTokenKit 进行令牌驱动程序扩展、智能卡通信、令牌会话、令牌支持的密钥串集成以及 Swift 6.3 应用中的基于证书的认证。

**平台可用性**：CryptoTokenKit 类跨 Apple 平台可用，但能力取决于扩展点、权限、硬件和 OS 版本。macOS 的登录/密钥串解锁使用智能卡应用扩展流程。`TKSmartCardSlotManager.default` 是可选的，除非启用智能卡访问，否则返回 `nil`。iOS/iPadOS 26+ 添加 NFC 智能卡插槽和注册。

## 目录

- [架构概述](#架构概述)
- [令牌扩展](#令牌扩展)
- [令牌会话](#令牌会话)
- [智能卡通信](#智能卡通信)
- [密钥串集成](#密钥串集成)
- [证书认证](#证书认证)
- [令牌监控](#令牌监控)
- [错误处理](#错误处理)
- [常见错误](#常见错误)
- [审查清单](#审查清单)
- [参考资料](#参考资料)

## 架构概述

CryptoTokenKit 桥接硬件安全令牌（智能卡、USB 令牌）与认证和密钥串服务。该框架有三种主要使用模式：

**智能卡令牌扩展** -- macOS 应用扩展，使硬件令牌的加密项可用于系统登录和密钥串解锁。驱动程序处理令牌生命周期、会话管理和加密操作。

**客户端侧令牌访问** -- 应用查询密钥串以查找由令牌支持的项。当令牌存在时，CryptoTokenKit 将令牌项暴露为标准密钥串条目。

**NFC 智能卡访问** -- iOS/iPadOS 26+ 应用创建临时 NFC 智能卡插槽，并通过 `TKSmartCard` 与呈现的无接触卡通信。

**边界路由**：拥有令牌/智能卡会话、令牌支持的密钥串项和基于证书的智能卡认证。将 passkeys/WebAuthn 和账户登录路由到 `authentication`；将 Secure Enclave、CryptoKit 原语、密钥串架构、证书锁定和信任策略路由到 `swift-security`。

### 关键类型

| 类型 | 角色 | 平台 |
|---|---|---|
| `TKTokenDriver` / `TKToken` / `TKTokenSession` | 令牌驱动程序、令牌和会话原语 | iOS 10+、macOS 10.12+ |
| `TKSmartCardTokenDriver` | 智能卡令牌扩展的入口点 | iOS 10+、macOS 10.12+；macOS 扩展流程 |
| `TKSmartCard` / `TKSmartCardSlotManager` | 低级 APDU 通信和插槽发现 | iOS 9+、macOS 10.10+；`default` 是可选的 |
| `TKTokenWatcher` | 观察令牌插入和移除 | iOS 10+、macOS 10.12+ |
| `TKSmartCardSlotNFCSession` | NFC 支持的智能卡插槽会话 | iOS/iPadOS 26+ |
| `TKSmartCardTokenRegistrationManager` | 注册 NFC 智能卡以供后续密钥串使用 | iOS/iPadOS 26+ |

## 令牌扩展

在 macOS 上进行系统登录和密钥串解锁时，令牌驱动程序是一个应用扩展，它使硬件令牌的加密功能可用于系统。主机应用仅作为扩展的交付机制存在。

智能卡令牌扩展有三个核心类：

1. **TokenDriver**（`TKSmartCardTokenDriver` 的子类）-- 入口点
2. **Token**（`TKSmartCardToken` 的子类）-- 表示令牌
3. **TokenSession**（`TKSmartCardTokenSession` 的子类）-- 处理操作

### 驱动程序类

```swift
import CryptoTokenKit

final class TokenDriver: TKSmartCardTokenDriver, TKSmartCardTokenDriverDelegate {
    func tokenDriver(
        _ driver: TKSmartCardTokenDriver,
        createTokenFor smartCard: TKSmartCard,
        aid: Data?
    ) throws -> TKSmartCardToken {
        return try Token(
            smartCard: smartCard,
            aid: aid,
            instanceID: "com.example.token:\(smartCard.slot.name)",
            tokenDriver: driver
        )
    }
}
```

### 令牌类

令牌从硬件读取证书和密钥，并填充其密钥串内容：

```swift
final class Token: TKSmartCardToken, TKTokenDelegate {
    init(
        smartCard: TKSmartCard, aid: Data?,
        instanceID: String, tokenDriver: TKSmartCardTokenDriver
    ) throws {
        try super.init(
            smartCard: smartCard, aid: aid,
            instanceID: instanceID, tokenDriver: tokenDriver
        )
        self.delegate = self

        let certData = try readCertificate(from: smartCard)
        guard let cert = SecCertificateCreateWithData(nil, certData as CFData) else {
            throw TKError(.corruptedData)
        }

        let certItem = TKTokenKeychainCertificate(certificate: cert, objectID: "cert-auth")
        let keyItem = TKTokenKeychainKey(certificate: cert, objectID: "key-auth")
        keyItem?.canSign = true
        keyItem?.canDecrypt = false
        keyItem?.isSuitableForLogin = true

        self.keychainContents?.fill(with: [certItem!, keyItem!])
    }

    func createSession(_ token: TKToken) throws -> TKTokenSession {
        TokenSession(token: token)
    }
}
```

### Info.plist 和注册

扩展的 `Info.plist` 必须命名驱动程序类：

```
NSExtension
  NSExtensionAttributes
    com.apple.ctk.driver-class = $(PRODUCT_MODULE_NAME).TokenDriver
  NSExtensionPointIdentifier = com.apple.ctk-tokens
```

通过以 `_securityagent` 启动主机应用来注册扩展一次：

```shell
sudo -u _securityagent /Applications/TokenHost.app/Contents/MacOS/TokenHost
```

## 令牌会话

`TKTokenSession` 管理认证状态并通过其代理执行加密操作。

```swift
final class TokenSession: TKSmartCardTokenSession, TKTokenSessionDelegate {
    func tokenSession(
        _ session: TKTokenSession,
        supports operation: TKTokenOperation,
        keyObjectID: TKToken.ObjectID,
        algorithm: TKTokenKeyAlgorithm
    ) -> Bool {
        switch operation {
        case .signData:
            return algorithm.isAlgorithm(.rsaSignatureDigestPKCS1v15SHA256)
                || algorithm.isAlgorithm(.ecdsaSignatureDigestX962SHA256)
        case .decryptData:
            return algorithm.isAlgorithm(.rsaEncryptionOAEPSHA256)
        case .performKeyExchange:
            return algorithm.isAlgorithm(.ecdhKeyExchangeStandard)
        default:
            return false
        }
    }

    func tokenSession(
        _ session: TKTokenSession,
        sign dataToSign: Data,
        keyObjectID: TKToken.ObjectID,
        algorithm: TKTokenKeyAlgorithm
    ) throws -> Data {
        let smartCard = try getSmartCard()
        return try smartCard.withSession {
            try performCardSign(smartCard: smartCard, data: dataToSign, keyID: keyObjectID)
        }
    }

    func tokenSession(
        _ session: TKTokenSession,
        decrypt ciphertext: Data,
        keyObjectID: TKToken.ObjectID,
        algorithm: TKTokenKeyAlgorithm
    ) throws -> Data {
        let smartCard = try getSmartCard()
        return try smartCard.withSession {
            try performCardDecrypt(smartCard: smartCard, data: ciphertext, keyID: keyObjectID)
        }
    }
}
```

### PIN 认证

从 `beginAuthFor:` 返回 `TKTokenAuthOperation` 以在加密操作之前提示用户输入 PIN：

```swift
func tokenSession(
    _ session: TKTokenSession,
    beginAuthFor operation: TKTokenOperation,
    constraint: Any
) throws -> TKTokenAuthOperation {
    let pinAuth = TKTokenSmartCardPINAuthOperation()
    pinAuth.pinFormat.charset = .numeric
    pinAuth.pinFormat.minPINLength = 4
    pinAuth.pinFormat.maxPINLength = 8
    pinAuth.smartCard = (session as? TKSmartCardTokenSession)?.smartCard
    pinAuth.apduTemplate = buildVerifyAPDU()
    pinAuth.pinByteOffset = 5
    return pinAuth
}
```

## 智能卡通信

`TKSmartCard` 提供与智能卡的低级 APDU 通信。`TKSmartCardSlotManager.default` 是可选的；将 `nil` 视为不可用硬件、缺失权限/访问或不受支持运行时功能。

### 发现读卡器

```swift
import CryptoTokenKit

func discoverSmartCards() {
    guard let slotManager = TKSmartCardSlotManager.default else {
        print("智能卡服务不可用")
        return
    }

    for slotName in slotManager.slotNames {
        slotManager.getSlot(withName: slotName) { slot in
            guard let slot else { return }
            if slot.state == .validCard, let card = slot.makeSmartCard() {
                communicateWith(card: card)
            }
        }
    }
}
```

### 发送 APDU 命令

使用 `send(ins:p1:p2:data:le:)` 进行结构化 APDU 通信。始终将调用包装在 `withSession` 中：

```swift
func selectApplication(card: TKSmartCard, aid: Data) throws {
    try card.withSession {
        let (sw, response) = try card.send(
            ins: 0xA4, p1: 0x04, p2: 0x00, data: aid, le: nil
        )
        guard sw == 0x9000 else {
            throw TKError(.communicationError)
        }
    }
}
```

对于原始 APDU 字节或非标准格式，使用 `transmit(_:reply:)` 并手动管理 `beginSession`/`endSession` 生命周期。

### NFC 智能卡会话（iOS/iPadOS 26+）

在 iOS/iPadOS 26+ 上，在调用 `createNFCSlot(message:completion:)` 以与无接触卡通信之前，先检查 `isNFCSupported()`：

```swift
@available(iOS 26.0, iPadOS 26.0, *)
func readNFCSmartCard() {
    guard let slotManager = TKSmartCardSlotManager.default,
          slotManager.isNFCSupported() else { return }

    slotManager.createNFCSlot(message: "将卡靠近 iPhone") { session, error in
        guard let session else {
            handleNFCError(error)
            return
        }
        defer { session.end() }

        guard let slotName = session.slotName,
              let slot = slotManager.slotNamed(slotName),
              let card = slot.makeSmartCard() else { return }
        // 使用 card.send(...) 与 NFC 卡通信
    }
}
```

## 密钥串集成

当令牌存在时，CryptoTokenKit 将其项暴露为标准密钥串条目。使用 `kSecAttrTokenID` 属性查询它们：

```swift
import Security

func findTokenKey(tokenID: String) throws -> SecKey {
    let query: [String: Any] = [
        kSecClass as String: kSecClassKey,
        kSecAttrTokenID as String: tokenID,
        kSecReturnRef as String: true
    ]
    var result: CFTypeRef?
    let status = SecItemCopyMatching(query as CFDictionary, &result)
    guard status == errSecSuccess, let key = result else {
        throw TKError(.objectNotFound)
    }
    return key as! SecKey
}
```

使用 `kSecReturnPersistentRef` 而不是 `kSecReturnRef` 以获取跨应用启动持久的引用。当令牌移除时，引用失效 -- 处理 `errSecItemNotFound` 通过提示用户重新插入令牌。

以相同方式查询证书，使用 `kSecClass: kSecClassCertificate`。

## 证书认证

### 令牌密钥要求

对于用户登录，令牌必须至少包含一个能够使用以下之一进行签名的密钥：EC 签名摘要 X962、RSA 签名摘要 PSS 或 RSA 签名摘要 PKCS1v15。

对于密钥串解锁，令牌需要：
- 支持 `ecdhKeyExchangeStandard` 的 256 位 EC 密钥 (`kSecAttrKeyTypeECSECPrimeRandom`)，或
- 支持 `rsaEncryptionOAEPSHA256` 解密的 2048/3072/4096 位 RSA 密钥 (`kSecAttrKeyTypeRSA`)

### macOS 智能卡认证首选项

在 `com.apple.security.smartcard` 域（MDM 或系统范围）中配置：

| 键 | 默认值 | 描述 |
|---|---|---|
| `allowSmartCard` | `true` | 启用智能卡认证 |
| `checkCertificateTrust` | `0` | 证书信任级别（0-3） |
| `oneCardPerUser` | `false` | 将单个智能卡与账户配对 |
| `enforceSmartCard` | `false` | 要求使用智能卡登录 |

信任级别：`0` = 信任所有，`1` = 有效性 + 发行人，`2` = + 软撤销，`3` = + 硬撤销。

## 令牌监控

`TKTokenWatcher` 监控令牌插入和移除。在 iOS 10+ 和 macOS 10.12+ 上可用。枚举 `tokenIDs`，安装插入处理程序，然后为每个观察到的令牌添加移除处理程序。只要需要监控，就保持监控器活跃。对于插槽级读卡器状态，请使用 [智能卡插槽监控](references/cryptotokenkit-patterns.md#smart-card-slot-monitoring)。

## 错误处理

CryptoTokenKit 操作抛出 `TKError`。关键错误代码：

| 代码 | 含义 |
|---|---|
| `.notImplemented` | 操作未由此令牌支持 |
| `.communicationError` | 与令牌通信失败 |
| `.corruptedData` | 令牌数据损坏 |
| `.canceledByUser` | 用户取消了操作 |
| `.authenticationFailed` | PIN 或密码错误 |
| `.objectNotFound` | 未找到请求的密钥或证书 |
| `.tokenNotFound` | 令牌不再存在 |
| `.authenticationNeeded` | 操作之前需要认证 |

## 常见错误

### 不要：在未检查令牌存在的情况下查询令牌密钥串项

```swift
// 错误 -- 如果令牌被移除，查询可能会失败
let key = try findTokenKey(tokenID: savedTokenID)

// 正确 -- 首先验证令牌是否仍然存在
let watcher = TKTokenWatcher()
guard watcher.tokenIDs.contains(savedTokenID) else {
    promptUserToInsertToken()
    return
}
let key = try findTokenKey(tokenID: savedTokenID)
```

### 不要：将 API 可用性视为访问保证

```swift
// 错误 -- 可能在没有权限、硬件或运行时支持的情况下为 nil
let manager = TKSmartCardSlotManager.default!  // 不可用时崩溃

// 正确 -- 在使用智能卡插槽之前，先检查可用性/访问权限
guard let manager = TKSmartCardSlotManager.default else {
    print("智能卡服务不可用")
    return
}
```

### 不要：跳过卡片通信的会话管理

```swift
// 错误 -- 没有会话发送命令
card.transmit(apdu) { response, error in /* 可能会失败 */ }

// 正确 -- 使用 withSession 或 beginSession/endSession
try card.withSession {
    let (sw, response) = try card.send(
        ins: 0xCA, p1: 0x00, p2: 0x6E, data: nil, le: 0
    )
}
```

### 不要：忽略 APDU 响应中的状态字

```swift
// 错误 -- 假设成功
let (_, response) = try card.send(ins: 0xA4, p1: 0x04, p2: 0x00, data: aid, le: nil)

// 正确 -- 检查状态字
let (sw, response) = try card.send(ins: 0xA4, p1: 0x04, p2: 0x00, data: aid, le: nil)
guard sw == 0x9000 else {
    throw SmartCardError.commandFailed(statusWord: sw)
}
```

### 不要：硬编码通用的算法支持

`supports` 委托方法必须反映硬件实际实现的内容。无条件返回 `true` 会导致系统尝试不支持的操作时出现运行时错误。

## 审查清单

- [ ] 验证了确切的令牌能力可用性（`TKTokenWatcher` iOS 10+、NFC 智能卡会话 iOS/iPadOS 26+）
- [ ] `TKSmartCardSlotManager.default` 防御了缺失权限、硬件或运行时支持
- [ ] macOS 令牌扩展目标使用 `NSExtensionPointIdentifier` = `com.apple.ctk-tokens`
- [] `com.apple.ctk.driver-class` 在 Info.plist 中设置为正确的驱动程序类
- [] 扩展通过安装期间以 `_securityagent` 启动注册
- [] `TKTokenSessionDelegate` 检查特定算法，而不是通用的 `true`
- [] 智能卡会话打开和关闭（`withSession` 或 `beginSession`/`endSession`）
- [] 每个 `send` 调用后检查 APDU 状态字
- [] 在密钥串查询之前通过 `TKTokenWatcher` 验证令牌存在
- [] 处理 `TKError` 案例并提供适当的用户反馈
- [] 密钥串内容填充了正确的 `objectID` 值
- [] `TKTokenKeychainKey` 功能 (`canSign`, `canDecrypt`) 与硬件匹配
- [] 部署环境中配置适当的证书信任级别
- [] 令牌移除时处理 `errSecItemNotFound` 以提示用户重新插入令牌
- [] iOS 26+ NFC 会话使用 `TKSmartCardSlotNFCSession.end()` 结束

## 参考资料

- 扩展模式（PIV 命令、TLV 解析、通用令牌驱动程序、APDU 辅助程序、安全 PIN）：[references/cryptotokenkit-patterns.md](references/cryptotokenkit-patterns.md)
- [TKTokenDriver](https://sosumi.ai/documentation/cryptotokenkit/tktokendriver)
- [TKToken](https://sosumi.ai/documentation/cryptotokenkit/tktoken)
- [TKTokenSession](https://sosumi.ai/documentation/cryptotokenkit/tktokensession)
- [TKSmartCard](https://sosumi.ai/documentation/cryptotokenkit/tksmartcard)
- [TKSmartCardSlotManager](https://sosumi.ai/documentation/cryptotokenkit/tksmartcardslotmanager)
- [com.apple.security.smartcard 权限](https://sosumi.ai/documentation/BundleResources/Entitlements/com.apple.security.smartcard)
- [TKSmartCardSlotNFCSession](https://sosumi.ai/documentation/cryptotokenkit/tksmartcardslotnfcsession)
- [TKSmartCardTokenRegistrationManager](https://sosumi.ai/documentation/cryptotokenkit/tksmartcardtokenregistrationmanager)
- [TKTokenWatcher](https://sosumi.ai/documentation/cryptotokenkit/tktokenwatcher)
- [使用加密令牌验证用户](https://sosumi.ai/documentation/cryptotokenkit/authenticating-users-with-a-cryptographic-token)
- [使用存储在智能卡上的加密资产](https://sosumi.ai/documentation/cryptotokenkit/using-cryptographic-assets-stored-on-a-smart-card)
- [配置智能卡认证](https://sosumi.ai/documentation/cryptotokenkit/configuring-smart-card-authentication)
