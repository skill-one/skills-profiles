# CryptoKit

Apple CryptoKit 提供了用于加密操作的 Swift 原生 API：
哈希、消息认证、对称加密、公钥签名、密钥协商、HPKE、量子安全密钥封装/签名以及 Secure Enclave 支持的密钥。大多数核心原语在 iOS 13+ 上可用；检查 HPKE（iOS 17+）和 SHA-3 / 后量子 API（iOS 26+）的可用性。对于面向 Swift 6.3+ 的新加密原语代码，请优先选择 CryptoKit 而不是 CommonCrypto 或原始 Security 框架 API。

## 目录

- [哈希](#哈希)
- [HMAC](#hmac)
- [对称加密](#对称加密)
- [公钥签名](#公钥签名)
- [密钥协商](#密钥协商)
- [HPKE](#hpke)
- [后量子 CryptoKit](#后量子-cryptokit)
- [Secure Enclave](#secure-enclave)
- [常见错误](#常见错误)
- [审查清单](#审查清单)
- [参考资料](#参考资料)

## 哈希

在 iOS 13+ 上使用 SHA256/SHA384/SHA512；SHA3_256/SHA3_384/SHA3_512 需要 iOS 26+。所有这些都遵循 `HashFunction`。

### 单次哈希

```swift
import CryptoKit

let data = Data("Hello, world!".utf8)
let digest = SHA256.hash(data: data)
let hex = digest.compactMap { String(format: "%02x", $0) }.joined()
```

### SHA-3 可用性

除非部署目标是 iOS 26+，否则仅在通过可用性检查后才使用 SHA-3：

```swift
if #available(iOS 26.0, *) {
    let digest = SHA3_256.hash(data: data)
}
```

### 增量哈希

对于大数据或流式输入，增量哈希：

```swift
var hasher = SHA256()
hasher.update(data: chunk1)
hasher.update(data: chunk2)
let digest = hasher.finalize()
```

### 摘要比较

直接比较 CryptoKit 摘要值。不要将摘要转换为字符串或数组进行安全敏感的相等性检查。

```swift
let expected = SHA256.hash(data: reference)
let actual = SHA256.hash(data: received)
if expected == actual {
    // 数据完整性已验证
}
```

## HMAC

当协议需要带密钥的消息认证时使用 HMAC；使用 `isValidAuthenticationCode` 而不是自己比较序列化值进行验证。

### 计算认证码

```swift
let key = SymmetricKey(size: .bits256)
let data = Data("message".utf8)

let mac = HMAC<SHA256>.authenticationCode(for: data, using: key)
```

### 验证认证码

```swift
let isValid = HMAC<SHA256>.isValidAuthenticationCode(
    mac, authenticating: data, using: key
)
```

### 增量 HMAC

```swift
var hmac = HMAC<SHA256>(key: key)
hmac.update(data: chunk1)
hmac.update(data: chunk2)
let mac = hmac.finalize()
```

## 对称加密

CryptoKit 提供两种认证加密密码：AES-GCM 和 ChaChaPoly。两者都生成一个包含 nonce、密文和认证标签的密封盒子。

### AES-GCM

对称加密的默认选择。在 Apple 硅上硬件加速。

```swift
let key = SymmetricKey(size: .bits256)
let plaintext = Data("Secret message".utf8)

// 加密
let sealedBox = try AES.GCM.seal(plaintext, using: key)
let ciphertext = sealedBox.combined!  // nonce + 密文 + 标签

// 解密
let box = try AES.GCM.SealedBox(combined: ciphertext)
let decrypted = try AES.GCM.open(box, using: key)
```

### ChaChaPoly

当 AES 硬件加速不可用时或需要与要求 ChaCha20-Poly1305 的协议互操作时（例如 TLS、WireGuard）使用 ChaChaPoly。

```swift
let sealedBox = try ChaChaPoly.seal(plaintext, using: key)
let combined = sealedBox.combined  // ChaChaPoly 的 `combined` 始终为非可选

let box = try ChaChaPoly.SealedBox(combined: combined)
let decrypted = try ChaChaPoly.open(box, using: key)
```

### 认证数据

两种密码都支持附加认证数据 (AAD)。AAD 被认证但未被加密——适用于必须保持透明但防篡改的元数据。

```swift
let header = Data("v1".utf8)
let sealedBox = try AES.GCM.seal(
    plaintext, using: key, authenticating: header
)
let decrypted = try AES.GCM.open(
    sealedBox, using: key, authenticating: header
)
```

对于 AES-256-GCM 或 ChaChaPoly，将 `.bits256` 作为默认的 `SymmetricKey` 大小。要从现有数据创建密钥：

```swift
let key = SymmetricKey(data: existingKeyData)
```

## 公钥签名

CryptoKit 支持使用 NIST 曲线进行 ECDSA 签名，以及通过 Curve25519 进行 Ed25519 签名。

### NIST 曲线：P256、P384、P521

```swift
let signingKey = P256.Signing.PrivateKey()
let publicKey = signingKey.publicKey

// 签名
let signature = try signingKey.signature(for: data)

// 验证
let isValid = publicKey.isValidSignature(signature, for: data)
```

P384 和 P521 使用相同的 API——只需替换曲线名称。

NIST 密钥支持 DER、PEM、X9.63 和原始表示形式。有关序列化示例，请参阅 [参考资料/cryptokit-patterns.md](references/cryptokit-patterns.md)。

### Curve25519 / Ed25519

```swift
let signingKey = Curve25519.Signing.PrivateKey()
let publicKey = signingKey.publicKey

// 签名
let signature = try signingKey.signature(for: data)

// 验证
let isValid = publicKey.isValidSignature(signature, for: data)
```

Curve25519 密钥仅使用 `rawRepresentation`（无 DER/PEM/X9.63）。

### 选择曲线

| 曲线 | 签名方案 | 密钥大小 | 典型用途 |
|---|---|---|---|
| P256 | ECDSA | 256 位 | 通用；Secure Enclave 支持 |
| P384 | ECDSA | 384 位 | 更高的安全要求 |
| P521 | ECDSA | 521 位 | 最大的 NIST 安全级别 |
| Curve25519 | Ed25519 | 256 位 | 快速；简单 API；无 Secure Enclave |

默认使用 P256。当与基于 Ed25519 的协议互操作时使用 Curve25519。

## 密钥协商

密钥协商允许双方使用 ECDH 从他们的公钥/私钥对中派生一个共享的对称密钥。

### 使用 P256 的 ECDH

```swift
// Alice
let aliceKey = P256.KeyAgreement.PrivateKey()

// Bob
let bobKey = P256.KeyAgreement.PrivateKey()

// Alice 计算共享密钥
let sharedSecret = try aliceKey.sharedSecretFromKeyAgreement(
    with: bobKey.publicKey
)

// 使用 HKDF 派生对称密钥
let symmetricKey = sharedSecret.hkdfDerivedSymmetricKey(
    using: SHA256.self,
    salt: Data("salt".utf8),
    sharedInfo: Data("my-app-v1".utf8),
    outputByteCount: 32
)
```

Bob 使用他的私钥和 Alice 的公钥计算相同的 `sharedSecret`。双方都派生出相同的 `symmetricKey`。

### 使用 Curve25519 的 ECDH

```swift
let aliceKey = Curve25519.KeyAgreement.PrivateKey()
let bobKey = Curve25519.KeyAgreement.PrivateKey()

let sharedSecret = try aliceKey.sharedSecretFromKeyAgreement(
    with: bobKey.publicKey
)

let symmetricKey = sharedSecret.hkdfDerivedSymmetricKey(
    using: SHA256.self,
    salt: Data(),
    sharedInfo: Data("context".utf8),
    outputByteCount: 32
)
```

### 密钥派生函数

`SharedSecret` 不能直接用作 `SymmetricKey`。始终使用以下之一派生密钥：

| 方法 | 标准 | 用途 |
|---|---|---|
| `hkdfDerivedSymmetricKey` | HKDF (RFC 5869) | 推荐的默认值 |
| `x963DerivedSymmetricKey` | ANSI X9.63 | 与 X9.63 系统互操作 |

始终提供一个非空的 `sharedInfo` 字符串，以将派生的密钥绑定到特定的协议上下文。

## HPKE

HPKE 在 iOS 17+ 上用于公钥加密工作流。在加密到接收者公钥时，优先选择它而不是手写的 ECDH + HKDF + AEAD 协议。

```swift
let info = Data("my-protocol-v1".utf8)
let recipientKey = Curve25519.KeyAgreement.PrivateKey()
var sender = try HPKE.Sender(
    recipientKey: recipientKey.publicKey,
    ciphersuite: .Curve25519_SHA256_ChachaPoly,
    info: info
)
let encapsulatedKey = sender.encapsulatedKey
let ciphertext = try sender.seal(
    plaintext,
    authenticating: Data("metadata".utf8)
)

var recipient = try HPKE.Recipient(
    privateKey: recipientKey,
    ciphersuite: .Curve25519_SHA256_ChachaPoly,
    info: info,
    encapsulatedKey: encapsulatedKey
)
```

`HPKE.Sender` 和 `HPKE.Recipient` 是有状态的；将它们作为 `var` 保留，将 `encapsulatedKey` 与密文一起发送，并按密封的顺序打开消息。有关 ciphersuite 选择和后量子 HPKE，请参阅 [参考资料/cryptokit-patterns.md](references/cryptokit-patterns.md)。

## 后量子 CryptoKit

iOS 26+ 添加了量子安全 API：

- 密钥封装：`MLKEM768`、`MLKEM1024`
- 混合 HPKE：`XWingMLKEM768X25519` 与 `.XWingMLKEM768X25519_SHA256_AES_GCM_256`
- 数字签名：`MLDSA65`、`MLDSA87`
- Secure Enclave 变体：`SecureEnclave.MLKEM768`、`SecureEnclave.MLKEM1024`、`SecureEnclave.MLDSA65`、`SecureEnclave.MLDSA87`

当经典和量子安全都重要时，使用混合机制进行迁移。考虑到 P256 或 Curve25519 比较大的公钥、密文和签名。

## Secure Enclave

Secure Enclave 提供硬件支持的密钥存储。私钥永远不会离开硬件。对于经典的椭圆曲线 CryptoKit，Secure Enclave 支持使用 P256 签名和密钥协商。在支持硬件的 iOS 26+ 上，CryptoKit 还暴露了 Secure Enclave ML-KEM 密钥封装和 ML-DSA 签名类型。

### 可用性检查

```swift
guard SecureEnclave.isAvailable else {
    // 回退到软件密钥
    return
}
```

### 创建 Secure Enclave 签名密钥

```swift
let privateKey = try SecureEnclave.P256.Signing.PrivateKey()
let publicKey = privateKey.publicKey  // 标准 P256.Signing.PublicKey

let signature = try privateKey.signature(for: data)
let isValid = publicKey.isValidSignature(signature, for: data)
```

### 访问控制

使用 `SecAccessControl` 与 `.privateKeyUsage`，当密钥需要生物识别或密码保护使用时。在 `swift-security` 域中保留详细的 Keychain 策略决策。

### 持久化 Secure Enclave 密钥

`dataRepresentation` 是一个加密的 blob，只有同一设备的 Secure Enclave 才能恢复。将其存储在 Keychain 中。

```swift
// 导出
let blob = privateKey.dataRepresentation

// 恢复
let restored = try SecureEnclave.P256.Signing.PrivateKey(
    dataRepresentation: blob
)
```

### Secure Enclave 密钥协商

```swift
let seKey = try SecureEnclave.P256.KeyAgreement.PrivateKey()
let peerPublicKey: P256.KeyAgreement.PublicKey = // 来自对端

let sharedSecret = try seKey.sharedSecretFromKeyAgreement(
    with: peerPublicKey
)
```

## 常见错误

### 1. 直接将共享密钥用作密钥

```swift
// 不要
let badKey = sharedSecret.withUnsafeBytes { bytes in
    SymmetricKey(data: Data(bytes))
}

// 要——使用 HKDF 派生
let goodKey = sharedSecret.hkdfDerivedSymmetricKey(
    using: SHA256.self,
    salt: salt,
    sharedInfo: info,
    outputByteCount: 32
)
```

### 2. 重用 nonce

```swift
// 不要——硬编码 nonce
let nonce = try AES.GCM.Nonce(data: Data(repeating: 0, count: 12))
let box = try AES.GCM.seal(data, using: key, nonce: nonce)

// 要——让 CryptoKit 生成随机 nonce（默认行为）
let box = try AES.GCM.seal(data, using: key)
```

### 3. 忽略认证标签验证

```swift
// 不要——手动剥离标签并解密
// 要——始终使用 AES.GCM.open() 或 ChaChaPoly.open()
// 这些会自动验证标签
```

### 4. 使用不安全的哈希进行安全

```swift
// 不要——MD5/SHA1 用于完整性或安全性
import CryptoKit
let bad = Insecure.MD5.hash(data: data)

// 要——使用 SHA256 或更强的
let good = SHA256.hash(data: data)
```

`Insecure.MD5` 和 `Insecure.SHA1` 仅用于向后兼容（校验和验证、协议互操作）。永远不要将它们用于新的安全敏感操作。

### 5. 将对称密钥存储在 UserDefaults 中

```swift
// 不要
UserDefaults.standard.set(rawKeyData, forKey: "encryptionKey")

// 要——存储在 Keychain 中
// 请参阅参考资料/cryptokit-patterns.md 以获取 Keychain 存储模式
```

### 6. 不检查 Secure Enclave 可用性

```swift
// 不要——在模拟器或不支持的硬件上崩溃
let key = try SecureEnclave.P256.Signing.PrivateKey()

// 要
guard SecureEnclave.isAvailable else { /* 回退 */ }
let key = try SecureEnclave.P256.Signing.PrivateKey()
```

## 审查清单

- [ ] 使用 CryptoKit，而不是 CommonCrypto 或原始 Security 框架
- [ ] 哈希使用 SHA256+；出于安全目的不使用 MD5/SHA1
- [ ] HMAC 验证使用 `isValidAuthenticationCode`（常时）
- [ ] 对称加密使用 AES-GCM 或 ChaChaPoly；256 位密钥
- [ ] Nonces 是随机的（默认）——不是硬编码或重用
- [ ] 使用认证数据 (AAD)，当元数据需要完整性时
- [ ] SharedSecret 通过 HKDF 派生，而不是直接使用
- [ ] sharedInfo 参数是非空的且上下文特定的
- [ ] 在 iOS 17+ 上，使用 HPKE 而不是自定义 ECDH+HKDF+AEAD 进行接收者公钥加密
- [ ] SHA-3 和后量子 API 受 iOS 26+ 可用性保护
- [ ] 在使用 Secure Enclave 之前检查其可用性
- [ ] Secure Enclave 密钥 `dataRepresentation` 存储在 Keychain 中
- [ ] 私钥不会不必要地记录、打印或序列化
- [ ] 对称密钥存储在 Keychain 中，而不是 UserDefaults 或文件
- [ ] 考虑加密导出合规性 (`ITSAppUsesNonExemptEncryption`)

## 参考资料

- 扩展模式（密钥序列化、Insecure 模块、Keychain 集成、AES 密钥封装、HPKE）：[参考资料/cryptokit-patterns.md](references/cryptokit-patterns.md)
- Apple 文档：[CryptoKit](https://sosumi.ai/documentation/cryptokit)
- Apple 文档：[HPKE](https://sosumi.ai/documentation/cryptokit/hpke)
- Apple 文档：[量子安全工作流](https://sosumi.ai/documentation/cryptokit/enhancing-your-app-s-privacy-and-security-with-quantum-secure-workflows)
- Apple 示例：[执行常见加密操作](https://sosumi.ai/documentation/cryptokit/performing-common-cryptographic-operations)
- Apple 示例：[在 Keychain 中存储 CryptoKit 密钥](https://sosumi.ai/documentation/cryptokit/storing-cryptokit-keys-in-the-keychain)
