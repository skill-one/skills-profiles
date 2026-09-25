# 设备完整性

验证请求是否来自真实苹果设备上的合法应用实例。DeviceCheck 提供每个设备的位来设置简单标志（例如，“已申领促销优惠”）。App Attest 使用 Secure Enclave 密钥和苹果验证来在敏感请求上加密证明应用合法性。

## 内容

- [DCDevice (DeviceCheck 令牌)](#dcdevice-devicecheck-tokens)
- [DCAppAttestService (App Attest)](#dcappattestservice-app-attest)
- [App Attest 密钥生成](#app-attest-key-generation)
- [App Attest 验证流程](#app-attest-attestation-flow)
- [App Attest 断言流程](#app-attest-assertion-flow)
- [服务器验证指南](#server-verification-guidance)
- [错误处理](#error-handling)
- [常见模式](#common-patterns)
- [常见错误](#common-mistakes)
- [审查清单](#review-checklist)
- [参考资料](#references)

## DCDevice (DeviceCheck 令牌)

[`DCDevice`](https://sosumi.ai/documentation/devicecheck/dcdevice) 生成一个唯一、短暂的令牌来标识设备。将每个令牌视为单次使用：为每个服务器操作生成新令牌，而不是缓存或重用。将令牌发送到您的服务器，然后服务器与苹果的服务器通信来读取或设置每个设备的两个位。iOS 11+ 可用。

### 令牌生成

```swift
import DeviceCheck

func generateDeviceToken() async throws -> Data {
    guard DCDevice.current.isSupported else {
        throw DeviceIntegrityError.deviceCheckUnsupported
    }

    return try await DCDevice.current.generateToken()
}
```

### 将令牌发送到您的服务器

```swift
func sendTokenToServer(_ token: Data) async throws {
    let tokenString = token.base64EncodedString()

    var request = URLRequest(url: serverURL.appending(path: "verify-device"))
    request.httpMethod = "POST"
    request.setValue("application/json", forHTTPHeaderField: "Content-Type")
    request.httpBody = try JSONEncoder().encode(["device_token": tokenString])

    let (_, response) = try await URLSession.shared.data(for: request)
    guard let httpResponse = response as? HTTPURLResponse,
          httpResponse.statusCode == 200 else {
        throw DeviceIntegrityError.serverVerificationFailed
    }
}
```

### 服务器端概述

服务器将每个新鲜令牌与苹果的认证 DeviceCheck API 交换。加载 [DeviceCheck 服务器端点](references/device-integrity-patterns.md#devicecheck-server-endpoints) 获取端点和环境详细信息。

### 两个位的作用是什么

苹果为每个开发团队存储每个设备的两个布尔值。您决定它们的意义。常见用途：

- **位 0**：设备已申领促销优惠。
- **位 1**：设备已被标记为欺诈。

位在应用重新安装时仍然存在。您通过服务器 API 控制何时重置它们。

## DCAppAttestService (App Attest)

[`DCAppAttestService`](https://sosumi.ai/documentation/devicecheck/dcappattestservice) 验证特定设备上的特定应用实例是否合法。它使用 Secure Enclave 中的硬件后钥来创建加密验证和断言。iOS 14+ 可用。

流程分为三个阶段：
1. **密钥生成** -- 在 Secure Enclave 中创建密钥对。
2. **验证** -- 苹果验证密钥属于真实苹果设备上的您的应用。
3. **断言** -- 使用验证的密钥签名服务器请求，以证明持续合法性。

### 检查支持

```swift
import DeviceCheck

let attestService = DCAppAttestService.shared

guard attestService.isSupported else {
    // 回退到 DCDevice 令牌或其他风险评估。
    // App Attest 在模拟器或所有设备型号上不可用。
    return
}
```

对于应用扩展，App Attest 仅在 Action、可扩展 SSO 和 watchOS 扩展中受支持。即使 `isSupported` 返回 `true`，也要将其他扩展类型视为不受支持。

## App Attest 密钥生成

为每个设备上的每个用户帐户生成一个加密密钥对。私钥保留在 Secure Enclave 中。返回的 `keyId` 是您的应用后来访问密钥的唯一标识符，因此记录并重用帐户/设备范围的 `keyId`；不要在用户之间共享一个密钥。避免不必要的重新生成，因为每个新密钥都会影响 App Attest 密钥计数风险指标。只有在您的服务器验证验证后，才将 `keyId` 视为可用。如果服务器验证失败，请丢弃 `keyId` 并在重试之前生成新密钥。

```swift
import DeviceCheck

actor AppAttestManager {
    private let service = DCAppAttestService.shared
    private var keyId: String?

    /// 为 App Attest 生成并记录密钥对。
    func generateKeyIfNeeded() async throws -> String {
        if let existingKeyId = loadKeyIdFromKeychain() {
            self.keyId = existingKeyId
            return existingKeyId
        }

        let newKeyId = try await service.generateKey()
        saveKeyIdToKeychain(newKeyId)
        self.keyId = newKeyId
        return newKeyId
    }

    // MARK: - Keychain 辅助函数（简化）

    private func saveKeyIdToKeychain(_ keyId: String) {
        let data = Data(keyId.utf8)
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: "app-attest-key-id-\(currentAccountID)",
            kSecAttrService as String: Bundle.main.bundleIdentifier ?? "",
            kSecValueData as String: data,
            kSecAttrAccessible as String: kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly
        ]
        SecItemDelete(query as CFDictionary) // 如果存在则删除旧值
        SecItemAdd(query as CFDictionary, nil)
    }

    private func loadKeyIdFromKeychain() -> String? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: "app-attest-key-id-\(currentAccountID)",
            kSecAttrService as String: Bundle.main.bundleIdentifier ?? "",
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne
        ]
        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)
        guard status == errSecSuccess, let data = result as? Data else { return nil }
        return String(data: data, encoding: .utf8)
    }
}
```

## App Attest 验证流程

验证证明密钥是在真实苹果设备上的合法应用实例上生成的。您对每个密钥执行一次验证，然后将验证的公钥和收据存储在您的服务器上。应用在服务器接受验证后将 `keyId` 存储起来以供以后断言。

### 客户端验证

```swift
import DeviceCheck
import CryptoKit

extension AppAttestManager {
    /// 向苹果验证密钥。将验证对象发送到您的服务器。
    func attestKey() async throws -> Data {
        guard let keyId else {
            throw DeviceIntegrityError.keyNotGenerated
        }

        // 1. 从您的服务器请求一次性挑战
        let challenge = try await fetchServerChallenge()

        // 2. 哈希挑战（苹果要求 SHA-256 哈希）
        let challengeHash = Data(SHA256.hash(data: challenge))

        // 3. 请求苹果验证密钥
        let attestation = try await service.attestKey(keyId, clientDataHash: challengeHash)

        // 4. 将验证对象发送到您的服务器以进行验证
        try await sendAttestationToServer(
            keyId: keyId,
            attestation: attestation,
            challenge: challenge
        )

        return attestation
    }

    private func fetchServerChallenge() async throws -> Data {
        let url = serverURL.appending(path: "attest/challenge")
        let (data, _) = try await URLSession.shared.data(from: url)
        return data
    }

    private func sendAttestationToServer(
        keyId: String,
        attestation: Data,
        challenge: Data
    ) async throws {
        var request = URLRequest(url: serverURL.appending(path: "attest/verify"))
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let payload: [String: String] = [
            "key_id": keyId,
            "attestation": attestation.base64EncodedString(),
            "challenge": challenge.base64EncodedString()
        ]
        request.httpBody = try JSONEncoder().encode(payload)

        let (_, response) = try await URLSession.shared.data(for: request)
        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else {
            throw DeviceIntegrityError.attestationVerificationFailed
        }
    }
}
```

### 服务器端验证

服务器必须在客户端将 `keyId` 视为可用之前验证验证，然后存储验证的公钥和收据。加载 [服务器端验证](references/device-integrity-patterns.md#server-side-attestation-verification) 获取证书、App ID、环境、计数器、凭证和随机数的检查。

## App Attest 断言流程

验证后，使用断言对敏感请求进行签名。每个断言都证明请求来自验证的应用实例，并包含服务器颁发的一次性挑战以防止重放。

### 客户端断言

```swift
import DeviceCheck
import CryptoKit

extension AppAttestManager {
    /// 为编码的客户端数据生成断言。
    /// 客户端数据应包括一次性服务器挑战和请求上下文。
    func generateAssertion(for clientData: Data) async throws -> Data {
        guard let keyId else {
            throw DeviceIntegrityError.keyNotGenerated
        }

        let clientDataHash = Data(SHA256.hash(data: clientData))

        return try await service.generateAssertion(keyId, clientDataHash: clientDataHash)
    }
}
```

### 在网络请求中使用断言

```swift
struct AppAttestClientData: Encodable {
    let challenge: String
    let method: String
    let path: String
    let bodySHA256: String
}

extension AppAttestManager {
    /// 执行验证的 API 请求。
    func makeAttestedRequest(
        to url: URL,
        method: String = "POST",
        body: Data
    ) async throws -> (Data, URLResponse) {
        let challenge = try await fetchAssertionChallenge()
        let bodyHash = Data(SHA256.hash(data: body)).base64EncodedString()
        let clientData = try JSONEncoder().encode(
            AppAttestClientData(
                challenge: challenge,
                method: method,
                path: url.path,
                bodySHA256: bodyHash
            )
        )
        let assertion = try await generateAssertion(for: clientData)

        var request = URLRequest(url: url)
        request.httpMethod = method
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue(assertion.base64EncodedString(), forHTTPHeaderField: "X-App-Attest-Assertion")
        request.setValue(clientData.base64EncodedString(), forHTTPHeaderField: "X-App-Attest-Client-Data")
        request.httpBody = body

        return try await URLSession.shared.data(for: request)
    }

    private func fetchAssertionChallenge() async throws -> String {
        let url = serverURL.appending(path: "assert/challenge")
        let (data, _) = try await URLSession.shared.data(from: url)
        return String(decoding: data, as: UTF8.self)
    }
}
```

### 服务器端断言验证

服务器必须验证每个断言的签名、RP ID、计数器、一次性挑战和请求绑定，然后才能授权请求。加载 [服务器端断言验证](references/device-integrity-patterns.md#server-side-assertion-verification) 获取完整算法。

## 服务器验证指南

查看 [参考资料/device-integrity-patterns.md](references/device-integrity-patterns.md) 获取完整服务器架构指南，包括验证与断言比较、推荐端点设计和风险评估。

### 安全边界

App Attest 证明应用实例完整性，适用于选定请求。它不会取代用户认证、OAuth/JWT/会话处理、API 令牌设计、权限或订阅授权、TLS、证书锁定或一般网络安全性。将它们视为回退到认证、网络或更广泛的安全指南，并且在 App Attest 通过后仍然执行正常认证和授权。

## 错误处理

处理 DeviceCheck 操作的 `DCError` 代码。关键案例：

- `.serverUnavailable` — 使用指数退避重试
- `.invalidKey` — 密钥已验证，断言使用了未验证的密钥，或服务拒绝了密钥
- `.featureUnsupported` — 回退到 `DCDevice` 令牌
- `.invalidInput` — `clientDataHash` 或 `keyId` 格式错误

对于 `attestKey`，稍后使用相同的 `keyId` 和相同的 `clientDataHash` 重试 `.serverUnavailable`。对于其他验证错误，丢弃密钥标识符并在重试之前生成新密钥。查看 [参考资料/device-integrity-patterns.md](references/device-integrity-patterns.md) 获取完整错误处理代码、重试策略和拒绝密钥恢复。

## 常见模式

### 环境权限

在您的权限文件中设置 App Attest 环境。在测试期间使用 `development`，对于 App Store 构建使用 `production`。加载 [环境权限](references/device-integrity-patterns.md#environment-entitlement) 获取 XML、默认沙盒行为、分发行为和扩展限制。

查看 [参考资料/device-integrity-patterns.md](references/device-integrity-patterns.md) 获取完整集成管理器模式、渐进式推出指南和错误类型定义。

## 常见错误

1. **每次启动都生成新密钥。** 在设备上为每个用户帐户生成一次，持久化 `keyId`，并保持密钥计数较低。
2. **重用 `DCDevice` 令牌。** 将生成的令牌视为单次使用。为每个服务器操作生成新令牌。
3. **跳过对不支持设备或扩展的回退。** 并非所有设备和扩展类型都支持 App Attest。使用 `DCDevice` 令牌或其他风险评估作为回退。
4. **在客户端信任验证。** 所有验证都必须在您的服务器上执行。
5. **仅签名原始请求正文。** 断言客户端数据必须包含一次性服务器挑战和足够请求上下文，以便服务器将断言绑定到请求。
6. **验证错误的验证随机数。** 将证书扩展与 `SHA256(authData || SHA256(challenge))` 比较，而不是单独比较 `SHA256(challenge)`。
7. **未实现重放保护。** 服务器必须验证一次性挑战并跟踪断言计数器。
8. **混合开发和生产环境。** 沙盒密钥和收据在生产中不起作用，生产密钥和收据在沙盒中不起作用。
9. **未处理 `DCError.invalidKey`。** 检查重复验证、未验证的断言密钥或服务拒绝；仅在状态已知为错误时才重新生成。

## 审查清单

- [ ] `DCDevice` 令牌为每个服务器操作生成，并且从不缓存以重用
- [ ] 在使用前检查 `DCAppAttestService.isSupported`；不支持设备和扩展类型有回退
- [ ] 在每个设备上为每个用户帐户生成一次密钥，并且 `keyId` 仅持久化给该应用帐户/设备
- [ ] 对每个密钥执行一次验证；服务器存储验证的公钥和收据
- [ ] 服务器验证验证证书链、App ID 哈希、环境 `aaguid`、凭证 ID 和 `SHA256(authData || SHA256(challenge))`
- [ ] 断言包括一次性挑战加上请求上下文；服务器验证签名、RP ID、计数器、挑战和请求绑定
- [ ] 受保护端点在 App Attest 通过后仍然执行正常用户认证和权限授权
- [ ] 处理 `DCError` 案例的 `.serverUnavailable` 重试验证使用相同的密钥/哈希；丢弃坏密钥并重新生成
- [ ] App Attest 环境权限和沙盒/生产服务器路由一致
- [ ] 考虑渐进式推出；启用/禁用功能的功能标志

## 参考资料

- 扩展模式：[参考资料/device-integrity-patterns.md](references/device-integrity-patterns.md)
- [DeviceCheck 框架](https://sosumi.ai/documentation/devicecheck)
- [DCDevice](https://sosumi.ai/documentation/devicecheck/dcdevice)
- [DCAppAttestService](https://sosumi.ai/documentation/devicecheck/dcappattestservice)
- [建立您的应用完整性](https://sosumi.ai/documentation/devicecheck/establishing-your-app-s-integrity)
- [验证连接到您服务器的应用](https://sosumi.ai/documentation/devicecheck/validating-apps-that-connect-to-your-server)
- [验证对象验证指南](https://sosumi.ai/documentation/devicecheck/attestation-object-validation-guide)
- [App Attest 环境](https://sosumi.ai/documentation/bundleresources/entitlements/com.apple.developer.devicecheck.appattest-environment)
