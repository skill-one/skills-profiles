# Swift 安全

用于客户端 Apple 平台安全工作的技能：Keychain Services、访问控制、生物识别门禁密钥、CryptoKit、Secure Enclave 密钥、凭证存储、证书信任、Keychain 共享、遗留密钥迁移、安全测试和 OWASP 移动合规性映射。

当部署目标未知时，默认使用 iOS 17+ 和 Swift 并发示例。当用户要求较旧目标时，保留 iOS 13+ 兼容性说明。将 iOS 26 CryptoKit 后量子 API 视为可用性门禁。

## 目录

- [工作流](#工作流)
- [参考加载](#参考加载)
- [安全不变量](#安全不变量)
- [同级边界](#同级边界)
- [审查清单](#审查清单)
- [常见错误](#常见错误)
- [输出规则](#输出规则)
- [参考文献](#参考文献)

## 工作流

加载参考之前对请求进行分类。

1. 审查现有代码：运行 [审查清单](#审查清单)，然后加载 [common-anti-patterns.md](references/common-anti-patterns.md) 以及每个失败领域的域参考。报告严重性、证据和修正后的模式。
2. 改进或迁移代码：识别迁移类型，加载迁移和目标域参考，保留现有数据，验证新项，然后在成功后才删除遗留存储。
3. 实现新的安全代码：加载最小域参考，使用提供的正确模式，包含 OSStatus 处理和测试，然后运行相关清单。

默认情况下不要加载每个参考文件。此技能有意拆分为渐进式披露；仅加载用户任务所需的文件。

### 最小安全 Keychain 写入

使用单独的添加、身份和更新字典；处理每个 `OSStatus`：

```swift
func saveSecret(_ data: Data, account: String) throws {
    let identity: [CFString: Any] = [
        kSecClass: kSecClassGenericPassword,
        kSecAttrService: "com.example.app",
        kSecAttrAccount: account,
    ]
    var add = identity
    add[kSecValueData] = data
    add[kSecAttrAccessible] = kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly

    switch SecItemAdd(add as CFDictionary, nil) {
    case errSecSuccess:
        return
    case errSecDuplicateItem:
        let status = SecItemUpdate(
            identity as CFDictionary,
            [kSecValueData: data] as CFDictionary
        )
        guard status == errSecSuccess else { throw KeychainError(status: status) }
    case let status:
        throw KeychainError(status: status)
    }
}
```

加载 [keychain-fundamentals.md](references/keychain-fundamentals.md) 以获取读取、删除、访问控制、锁定设备和测试模式。

## 参考加载

| 如果任务涉及 | 加载 |
| --- | --- |
| 通用 Keychain CRUD 或 OSStatus 处理 | [keychain-fundamentals.md](references/keychain-fundamentals.md) |
| 选择 `kSecClass` 或项身份 | [keychain-item-classes.md](references/keychain-item-classes.md) |
| 可访问性类或 `SecAccessControl` | [keychain-access-control.md](references/keychain-access-control.md) |
| Face ID、Touch ID 或生物识别门禁密钥 | [biometric-authentication.md](references/biometric-authentication.md) |
| Secure Enclave 密钥 | [secure-enclave.md](references/secure-enclave.md) |
| 哈希、HMAC、AES-GCM、ChaChaPoly、HKDF、PBKDF2 | [cryptokit-symmetric.md](references/cryptokit-symmetric.md) |
| 签名、ECDH、HPKE、ML-KEM、ML-DSA | [cryptokit-public-key.md](references/cryptokit-public-key.md) |
| OAuth 令牌、API 密钥、注销、刷新旋转 | [credential-storage-patterns.md](references/credential-storage-patterns.md) |
| App/扩展 Keychain 共享 | [keychain-sharing.md](references/keychain-sharing.md) |
| 证书信任、SPKI 签名、mTLS | [certificate-trust.md](references/certificate-trust.md) |
| UserDefaults/plist/NSCoding 迁移 | [migration-legacy-stores.md](references/migration-legacy-stores.md) |
| 单元、集成、模拟器、设备或 CI 测试 | [testing-security-code.md](references/testing-security-code.md) |
| OWASP MASVS/MASTG 或企业审计映射 | [compliance-owasp-mapping.md](references/compliance-owasp-mapping.md) |
| 全面的安全审查 | [common-anti-patterns.md](references/common-anti-patterns.md)，然后是每个触及的域参考 |

## 安全不变量

仅用于以下安全不变量和 [common-anti-patterns.md](references/common-anti-patterns.md) 中的匹配反模式。对于此列表之外的架构选择，使用建议性语言。

- 永远不要在 `UserDefaults`、plists、源代码、日志、文件或 `NSCoding` 存档中存储令牌、密码、API 密钥、签名密钥或刷新令牌。使用 Keychain 或在运行时获取密钥。
- 永远不要忽略 `OSStatus`。每个 `SecItemAdd`、`SecItemCopyMatching`、`SecItemUpdate` 和 `SecItemDelete` 路径都必须检查成功并处理预期错误，例如 `errSecDuplicateItem`、`errSecItemNotFound` 和 `errSecInteractionNotAllowed`。
- 永远不要将 `LAContext.evaluatePolicy()` 仅用作密钥的唯一门禁。使用 `SecAccessControl` 将受保护的密钥绑定到 Keychain 项，然后让 Keychain 访问触发 LocalAuthentication。
- 添加 Keychain 项时始终显式设置 `kSecAttrAccessible` 或 `kSecAttrAccessControl`。
- 永远使用添加或更新进行持久化 Keychain 写入。不要作为正常更新路径删除然后添加。
- 将 `SecItem*` 工作从主线程移开。使用 actor 或串行队列进行 Keychain 访问。
- 在 macOS AppKit 目标上，除非故意使用遗留基于文件的 Keychain 项，否则使用 `kSecUseDataProtectionKeychain: true` 目标数据保护 Keychain。
- 永远不要使用相同的 AES-GCM 非确定性。
- 永远不要将原始 ECDH `SharedSecret` 字节用作对称密钥。使用 HKDF 或 X9.63 衍生。
- 永远不要使用 `Insecure.MD5` 或 `Insecure.SHA1` 用于安全目的。

## 同级边界

此技能拥有客户端存储、密码学原语、硬件后盾密钥和信任评估。有意地路由相邻工作：

- 使用 `authentication` 进行 Apple Sign in、passkeys、OAuth UI 流程、`ASAuthorizationController`、凭证状态和账户登录 UX。
- 使用 `cryptokit` 进行 CryptoKit API 语法和示例，当存储、密钥生命周期、协议/信任设计、Secure Enclave 策略、证书信任、误用审查或合规性不是任务的一部分时。
- 当工作涉及密钥所有权、衍生、存储、旋转/恢复、Secure Enclave、HPKE/PQC 迁移、协议信任边界或误用分析时，在此处保留应用程序级端到端加密安全审查。
- 使用 `device-integrity` 进行 DeviceCheck 和 App Attest 证明/断言流程。
- 使用 `ios-networking` 进行 URLSession、请求管道、ATS 配置、重试、缓存、可达性和传输架构。
- 使用 `app-store-review` 进行隐私清单、ATT、App Review 指南合规性和提交准备就绪。

此技能可能仅提及这些领域以识别安全交接。

## 审查清单

用于代码审查和迁移计划。标记每个项目通过、失败或不适用；对于每个失败，引用参考文件和严重性。

- 密钥不存储在 `UserDefaults`、plists、源代码、日志、文件或存档中。
- 每个 `SecItem*` 调用检查 `OSStatus` 并处理常见可恢复错误。
- 生物识别访问密钥通过 `SecAccessControl` 与 Keychain 绑定，而不是来自 `LAContext.evaluatePolicy()` 的独立 `Bool`。
- Keychain 添加字典设置显式的可访问性策略。
- Keychain 写入使用添加或更新，而不是删除然后添加。
- Keychain 工作与 UI/主线程代码隔离。
- 选择的 `kSecClass` 与项类型和主键属性匹配。
- CryptoKit 代码避免非确定性重用、原始共享密钥使用、弱哈希和硬编码密钥。
- 自定义加密设计识别密钥所有权、衍生、存储、旋转/恢复、可用性门禁和协议/信任边界。
- Secure Enclave 代码检查可用性，处理模拟器/设备差异，仅持久化 `dataRepresentation`，并设计用于设备绑定密钥。
- App/扩展共享使用完整的 Team ID 访问组并在每个目标上匹配的权限。
- 证书信任使用当前的 `SecTrust` API，验证主机名/策略，并在需要时使用 SPKI 或 CA 签名。
- macOS Keychain 代码有意选择数据保护或基于文件的 Keychain 行为。
- 测试涵盖成功、重复、缺失项、锁定设备、模拟器/设备和适用迁移路径。
- 当请求合规性时，包含 OWASP MASVS/MASTG 映射。

## 常见错误

- 生成没有重复处理或 `errSecItemNotFound` 处理的 Keychain 示例。
- 添加生物识别 UI 但不通过 Keychain 访问控制使密钥可读。
- 通过省略属性隐式选择 `kSecAttrAccessibleWhenUnlocked`。
- 使用 `kSecAttrAccessibleAlways` 或 `kSecAttrAccessibleAlwaysThisDeviceOnly`，两者都已弃用。
- 在同一添加查询中混合 `kSecAttrAccessible` 和 `kSecAttrAccessControl`。
- 将 Secure Enclave 密钥视为可导入、可导出、可同步或适用于对称加密。
- 声称 SHA-3、ML-KEM、ML-DSA 或 X-Wing CryptoKit API 在 iOS 26 之前可用。
- 将 HPKE 视为在 iOS 17 之前可用。
- 通过仅哈希原始密钥字节而不是正确的 SPKI 表示来实现证书签名。
- 将此技能扩展为账户登录、网络、App Attest 或 App Store 审查指南，而不是将工作交接给同级技能。

## 输出规则

- 对于安全发现，声明严重性：可利用的密钥或密码学失败为 CRITICAL，静默安全边界/数据丢失问题为 HIGH，脆弱或不完整的硬化为 MEDIUM。
- 当存在具体的反模式时，在实施审查时包含错误和修正后的代码示例。
- 推荐版本 API 时包含最低 iOS/macOS 可用性。
- 引用支持每个实质性安全模式的参考文件。
- 对于 Keychain 代码，在示例中包含 `OSStatus` 处理和显式可访问性。
- 对于实施或迁移答案，以 `## Reference Files` 结尾并列出加载的参考及其一行目的。
- 不要编造 WWDC 会议编号或来源引用。如果声明未在加载的参考或官方 Apple 文档中，请说明需要验证。

## 参考文献

- [keychain-fundamentals.md](references/keychain-fundamentals.md) - SecItem CRUD、OSStatus 处理、添加或更新、macOS 数据保护 Keychain。
- [keychain-item-classes.md](references/keychain-item-classes.md) - `kSecClass` 选择、主键、证书、身份。
- [keychain-access-control.md](references/keychain-access-control.md) - 可访问性常量、`SecAccessControl`、后台访问、数据保护。
- [biometric-authentication.md](references/biometric-authentication.md) - Keychain 绑定的生物识别、`LAContext`、注册更改处理。
- [secure-enclave.md](references/secure-enclave.md) - Secure Enclave 限制、持久化、生物识别密钥、iOS 26 PQ API。
- [cryptokit-symmetric.md](references/cryptokit-symmetric.md) - SHA、HMAC、AES-GCM、ChaChaPoly、HKDF、PBKDF2。
- [cryptokit-public-key.md](references/cryptokit-public-key.md) - 签名、密钥协商、HPKE、ML-KEM、ML-DSA、密钥格式。
- [credential-storage-patterns.md](references/credential-storage-patterns.md) - OAuth 令牌、API 密钥、旋转、注销清理。
- [keychain-sharing.md](references/keychain-sharing.md) - 访问组、扩展、iCloud 同步、macOS 访问组。
- [certificate-trust.md](references/certificate-trust.md) - SecTrust、SPKI/CA 签名、`NSPinnedDomains`、客户端证书。
- [migration-legacy-stores.md](references/migration-legacy-stores.md) - UserDefaults/plist/NSCoding 迁移和清理。
- [common-anti-patterns.md](references/common-anti-patterns.md) - 不安全生成代码的审查骨干。
- [testing-security-code.md](references/testing-security-code.md) - 协议模拟、真实 Keychain 测试、CI/设备分割。
- [compliance-owasp-mapping.md](references/compliance-owasp-mapping.md) - OWASP 移动前 10 名、MASVS、MASTG 证据映射。
