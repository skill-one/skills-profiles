# Swift Codable

使用 `Codable` (`Encodable & Decodable`) 与 `JSONEncoder`、`JSONDecoder` 及相关 API 对 Swift 类型进行编码和解码。目标 Swift 6.3 / iOS 26+。

## 目录

- [解码和验证工作流](#decode-and-verify-workflow)
- [基本符合性](#basic-conformance)
- [自定义 CodingKeys](#custom-codingkeys)
- [自定义解码和编码](#custom-decoding-and-encoding)
- [嵌套和平铺容器](#nested-and-flattened-containers)
- [异构数组](#heterogeneous-arrays)
- [日期解码策略](#date-decoding-strategies)
- [数据和键策略](#data-and-key-strategies)
- [有损数组解码](#lossy-array-decoding)
- [单值容器](#single-value-containers)
- [缺失键的默认值](#default-values-for-missing-keys)
- [编码器和解码器配置](#encoder-and-decoder-configuration)
- [Codable 与 URLSession](#codable-with-urlsession)
- [Codable 与 SwiftData](#codable-with-swiftdata)
- [Codable 与 UserDefaults](#codable-with-userdefaults)
- [常见错误](#common-mistakes)
- [审查清单](#review-checklist)
- [参考资料](#references)

## 解码和验证工作流

1. 解码代表性的成功、缺失、null、格式错误、缩写键和日期样本。
2. 失败时，检查 `DecodingError`、其 `codingPath` 和原始负载。
3. 仅修正不匹配的模型、键、容器或策略；不要用有损解码隐藏契约失败。
4. 重新运行样本并执行编码/解码往返，其中两个方向都是契约的一部分。

## 基本符合性

当所有存储属性本身都是 `Codable` 时，编译器会自动合成符合性：

```swift
struct User: Codable {
    let id: Int
    let name: String
    let email: String
    let isVerified: Bool
}

let user = try JSONDecoder().decode(User.self, from: jsonData)
let encoded = try JSONEncoder().encode(user)
```

对于只读 API 响应优先使用 `Decodable`，对于只写优先使用 `Encodable`。只有当两个方向都需要时才使用 `Codable`。

## 自定义 CodingKeys

通过声明 `CodingKeys` 枚举来重命名 JSON 键，而无需编写自定义解码器：

```swift
struct Product: Codable {
    let id: Int
    let displayName: String
    let imageURL: URL
    let priceInCents: Int

    enum CodingKeys: String, CodingKey {
        case id
        case displayName = "display_name"
        case imageURL = "image_url"
        case priceInCents = "price_in_cents"
    }
}
```

每个存储属性都必须出现在枚举中。从 `CodingKeys` 中省略属性会将其排除在编码/解码之外——提供默认值或单独计算。

## 自定义解码和编码

对于合成符合性无法处理的转换，重写 `init(from:)` 和 `encode(to:)`：

```swift
struct Event: Codable {
    let name: String
    let timestamp: Date
    let tags: [String]

    enum CodingKeys: String, CodingKey {
        case name, timestamp, tags
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        name = try container.decode(String.self, forKey: .name)
        // 解码 Unix 时间戳为 Double，转换为 Date
        let epoch = try container.decode(Double.self, forKey: .timestamp)
        timestamp = Date(timeIntervalSince1970: epoch)
        // 键缺失时默认为空数组
        tags = try container.decodeIfPresent([String].self, forKey: .tags) ?? []
    }

    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(name, forKey: .name)
        try container.encode(timestamp.timeIntervalSince1970, forKey: .timestamp)
        try container.encode(tags, forKey: .tags)
    }
}
```

## 嵌套和平铺容器

使用 `nestedContainer(keyedBy:forKey:)` 导航并平铺嵌套 JSON：

```swift
// JSON: { "id": 1, "location": { "lat": 37.7749, "lng": -122.4194 } }
struct Place: Decodable {
    let id: Int
    let latitude: Double
    let longitude: Double

    enum CodingKeys: String, CodingKey { case id, location }
    enum LocationKeys: String, CodingKey { case lat, lng }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        id = try container.decode(Int.self, forKey: .id)
        let location = try container.nestedContainer(
            keyedBy: LocationKeys.self, forKey: .location)
        latitude = try location.decode(Double.self, forKey: .lat)
        longitude = try location.decode(Double.self, forKey: .lng)
    }
}
```

链式调用多个 `nestedContainer` 调用来平铺深度嵌套结构。也使用 `nestedUnkeyedContainer(forKey:)` 来处理嵌套数组。

## 异构数组

加载 [高级 Codable 模式](references/codable-advanced-patterns.md#heterogeneous-arrays) 以处理基于区分器的混合数组。

## 日期解码策略

配置 `JSONDecoder.dateDecodingStrategy` 以匹配您的 API：

```swift
let decoder = JSONDecoder()

// ISO 8601 (例如，"2024-03-15T10:30:00Z")
decoder.dateDecodingStrategy = .iso8601

// Unix 时间戳（秒）（例如，1710499800）
decoder.dateDecodingStrategy = .secondsSince1970

// 自定义 DateFormatter
let formatter = DateFormatter()
formatter.dateFormat = "yyyy-MM-dd"
formatter.locale = Locale(identifier: "en_US_POSIX")
formatter.timeZone = TimeZone(secondsFromGMT: 0)
decoder.dateDecodingStrategy = .formatted(formatter)

// 自定义闭包处理多种格式
decoder.dateDecodingStrategy = .custom { decoder in
    let container = try decoder.singleValueContainer()
    let string = try container.decode(String.self)
    if let date = ISO8601DateFormatter().date(from: string) { return date }
    throw DecodingError.dataCorruptedError(
        in: container, debugDescription: "Cannot decode date: \(string)")
}
```

在 `JSONEncoder` 上设置匹配策略：
`encoder.dateEncodingStrategy = .iso8601`

## 数据和键策略

```swift
let decoder = JSONDecoder()
decoder.dataDecodingStrategy = .base64           // Base64 编码的 Data 字段
decoder.keyDecodingStrategy = .convertFromSnakeCase  // 仅简单键；不包括 URL/ID 拼写
// {"user_name": "Alice"} 映射到 `var userName: String` —— 无需 CodingKeys

let encoder = JSONEncoder()
encoder.dataEncodingStrategy = .base64
encoder.keyEncodingStrategy = .convertToSnakeCase
```

仅用于机械的 snake_case 到 camelCase 映射。`convertFromSnakeCase` 按拼写映射，而不是 Swift 缩写/首字母缩略词政策：
`image_url`、`base_uri` 和 `user_id` 仅匹配 `imageUrl`、`baseUri` 和 `userId`。如果 Swift 模型使用 `imageURL`、`baseURI` 或 `userID`，声明显式的 `CodingKeys`；策略不会合成这些名称。

## 有损数组解码

仅在部分成功是产品契约的一部分时才使用有损数组；加载 [有损数组](references/codable-advanced-patterns.md#lossy-arrays)。

## 单值容器

使用 `singleValueContainer()` 进行类型安全的原始值包装；参见
[单值包装器](references/codable-advanced-patterns.md#single-value-wrappers)。

## 缺失键的默认值

存储默认值不会使合成解码容忍缺失的非可选键。当契约为缺失或 null 值分配显式回退行为时，加载
[缺失键默认值](references/codable-advanced-patterns.md#missing-key-defaults)。

## 编码器和解码器配置

在传输/文件格式边界处保持匹配策略。加载
[编码器配置](references/codable-advanced-patterns.md#encoder-configuration) 以处理非符合浮点数和属性列表指导。

## Codable 与 URLSession

```swift
func fetchUser(id: Int) async throws -> User {
    let url = URL(string: "https://api.example.com/users/\(id)")!
    let (data, response) = try await URLSession.shared.data(from: url)
    guard let http = response as? HTTPURLResponse,
          (200...299).contains(http.statusCode) else {
        throw APIError.invalidResponse
    }
    let decoder = JSONDecoder()
    decoder.keyDecodingStrategy = .convertFromSnakeCase
    decoder.dateDecodingStrategy = .iso8601
    return try decoder.decode(User.self, from: data)
}

// 通用 API 封装。在辅助函数内部配置解码器，因为 fetchUser 的解码器不在作用域内。
struct APIResponse<T: Decodable>: Decodable {
    let data: T
    let meta: Meta?
    struct Meta: Decodable { let page: Int; let totalPages: Int }
}

func decodeUsersEnvelope(from data: Data) throws -> [User] {
    let decoder = JSONDecoder()
    decoder.keyDecodingStrategy = .convertFromSnakeCase
    decoder.dateDecodingStrategy = .iso8601
    return try decoder.decode(APIResponse<[User]>.self, from: data).data
}
```

## Codable 与 SwiftData

保持模式值类型化并将持久化设计路由到 `swiftdata`；参见
[持久化边界](references/codable-advanced-patterns.md#persistence-boundaries)。

## Codable 与 UserDefaults

使用原始值进行小偏好设置。加载
[持久化边界](references/codable-advanced-patterns.md#persistence-boundaries) 以处理小的 `Codable` `RawRepresentable`/`@AppStorage` 传递；使用真实持久化层处理较大或持久数据。

## 常见错误

**1. 未处理缺失的默认字段：**
```swift
// 不要——如果键缺失会崩溃
let value = try container.decode(String.self, forKey: .bio)
// 要——键缺失或 null 时会回退
let value = try container.decodeIfPresent(String.self, forKey: .bio) ?? ""
```

**2. 当一个元素无效时整个数组失败：**
```swift
// 不要——一个坏元素会导致整个解码失败
let items = try container.decode([Item].self, forKey: .items)
// 要——仅当允许部分成功时才单独解码元素
```

**3. 日期策略不匹配：**
```swift
// 不要——默认策略期望 Double，但 API 发送 ISO 字符串
let decoder = JSONDecoder()  // dateDecodingStrategy 默认为 .deferredToDate
// 要——设置策略以匹配 API 格式
decoder.dateDecodingStrategy = .iso8601
```

**4. 强制解包解码的可选值：**
```swift
// 不要
let user = try? decoder.decode(User.self, from: data)
print(user!.name)
// 要
guard let user = try? decoder.decode(User.self, from: data) else { return }
```

**5. 当只需要 Decodable 时使用 Codable：**
```swift
// 不要——不必要地限制类型也必须是 Encodable
struct APIResponse: Codable { let id: Int; let message: String }
// 要——对于只读 API 响应使用 Decodable
struct APIResponse: Decodable { let id: Int; let message: String }
```

**6. 简单 snake_case API 的手动 CodingKeys：**
```swift
// 不要——每个模型都冗长的样板代码
enum CodingKeys: String, CodingKey {
    case userName = "user_name"
    case avatarUrl = "avatar_url"
}
// 要——对于简单情况在解码器上配置一次
decoder.keyDecodingStrategy = .convertFromSnakeCase
// 保持 CodingKeys 用于 `imageURL`、`baseURI`、`userID` 和类似名称。
```

## 审查清单

- [ ] 类型仅在编码不需要时符合 `Decodable`
- [ ] 使用 `decodeIfPresent` 为可选或缺失键提供默认值
- [ ] `keyDecodingStrategy = .convertFromSnakeCase` 用于简单 snake_case API，保留 CodingKeys 以处理缩写拼写
- [ ] `dateDecodingStrategy` 匹配 API 日期格式
- [ ] 可靠性不高的数据数组使用有损解码跳过无效元素
- [ ] 自定义 `init(from:)` 验证和转换数据，而不是解码后修复
- [ ] `JSONEncoder.outputFormatting` 包括 `.sortedKeys` 以生成确定的测试输出
- [ ] 包装类型（UserID 等）使用 `singleValueContainer` 以获得干净的 JSON
- [ ] 使用通用 `APIResponse<T>` 包装器以处理一致的 API 封装
- [ ] 不要强制解包解码的值
- [ ] 持久化边界明确：仅使用 SwiftData 兼容的非计算模型属性，`@AppStorage`/UserDefaults 仅用于小的原始值或 `RawRepresentable` 偏好

## 参考资料

- [高级 Codable 模式](references/codable-advanced-patterns.md) -- 混合数组、有损解码、包装器、默认值、配置和持久化边界
- [Codable](https://sosumi.ai/documentation/swift/codable/) -- 结合 Encodable 和 Decodable 的协议
- [JSONDecoder](https://sosumi.ai/documentation/foundation/jsondecoder/) -- 将 JSON 数据解码为 Codable 类型
- [JSONEncoder](https://sosumi.ai/documentation/foundation/jsonencoder/) -- 将 Codable 类型编码为 JSON 数据
- [CodingKey](https://sosumi.ai/documentation/swift/codingkey/) -- 用于编码/解码键的协议
- [JSONDecoder.KeyDecodingStrategy.convertFromSnakeCase](https://sosumi.ai/documentation/foundation/jsondecoder/keydecodingstrategy-swift.enum/convertfromsnakecase) -- snake-case 转换行为和限制
- [编码和解码自定义类型](https://sosumi.ai/documentation/foundation/encoding-and-decoding-custom-types/) -- Apple 关于自定义 Codable 符合性的指南
- [使用 JSON 与自定义类型](https://sosumi.ai/documentation/foundation/archives_and_serialization/using_json_with_custom_types/) -- Apple 示例代码，用于 JSON 模式
- [跨启动保留应用模型数据](https://sosumi.ai/documentation/swiftdata/preserving-your-apps-model-data-across-launches) -- SwiftData 模型属性兼容性
