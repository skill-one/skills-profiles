# RivetKit Swift 客户端

在构建连接到 Rivet Actors 的 Swift 客户端时使用此技能，使用 `RivetKitClient`。

## 版本

RivetKit 版本：2.3.7

## 错误处理策略

- 默认情况下优先采用快速失败行为。
- 除非绝对必要，否则避免使用宽泛的 `do/catch`。
- 如果使用 `catch` 块，应显式处理错误，至少记录错误。

## 安装

添加 Swift 包依赖并导入 `RivetKitClient`：

```swift
// Package.swift
dependencies: [
    .package(url: "https://github.com/rivet-dev/rivetkit-swift", from: "2.0.0")
]

targets: [
    .target(
        name: "MyApp",
        dependencies: [
            .product(name: "RivetKitClient", package: "rivetkit-swift")
        ]
    )
]
```

## 最小客户端

### 端点 URL

```swift
import RivetKitClient

let config = try ClientConfig(
    endpoint: "https://my-namespace:pk_...@api.rivet.dev"
)
let client = RivetKitClient(config: config)

let handle = client.getOrCreate("counter", ["my-counter"])
let count: Int = try await handle.action("increment", 1, as: Int.self)
```

### 显式字段

```swift
import RivetKitClient

let config = try ClientConfig(
    endpoint: "https://api.rivet.dev",
    namespace: "my-namespace",
    token: "pk_..."
)
let client = RivetKitClient(config: config)

let handle = client.getOrCreate("counter", ["my-counter"])
let count: Int = try await handle.action("increment", 1, as: Int.self)
```

## 无状态与有状态

```swift
import RivetKitClient

let config = try ClientConfig(endpoint: "http://localhost:6420")
let client = RivetKitClient(config: config)

let handle = client.getOrCreate("counter", ["my-counter"])

// 无状态：每次调用都是独立的
let current: Int = try await handle.action("getCount", as: Int.self)
print("当前计数：\(current)")

// 有状态：保持连接打开以接收实时事件
let conn = handle.connect()

// 使用 AsyncStream 订阅事件
let eventTask = Task {
    for await count in await conn.events("count", as: Int.self) {
        print("事件：\(count)")
    }
}

_ = try await conn.action("increment", 1, as: Int.self)

eventTask.cancel()
await conn.dispose()
await client.dispose()
```

## 获取 Actors

```swift
import RivetKitClient

struct GameInput: Encodable {
    let mode: String
}

let config = try ClientConfig(endpoint: "http://localhost:6420")
let client = RivetKitClient(config: config)

// 获取或创建 Actor
let room = client.getOrCreate("chatRoom", ["room-42"])

// 获取现有 Actor（如果不存在则失败）
let existing = client.get("chatRoom", ["room-42"])

// 使用输入创建新 Actor
let created = try await client.create(
    "game",
    ["game-1"],
    options: CreateOptions(input: GameInput(mode: "ranked"))
)

// 通过 ID 获取 Actor
let byId = client.getForId("chatRoom", "actor-id")

// 解析 Actor ID
let resolvedId = try await room.resolve()
print("解析 ID：\(resolvedId)")

await client.dispose()
```

动作支持 0-5 个参数的位置重载：

```swift
import RivetKitClient

let config = try ClientConfig(endpoint: "http://localhost:6420")
let client = RivetKitClient(config: config)
let handle = client.getOrCreate("counter", ["my-counter"])

let count: Int = try await handle.action("getCount")
let updated: String = try await handle.action("rename", "new-name")
let ok: Bool = try await handle.action("setScore", "user-1", 42)

print("计数：\(count), 更新：\(updated), 成功：\(ok)")
await client.dispose()
```

如果您需要超过 5 个参数，可以使用原始 JSON 落回方法：

```swift
import RivetKitClient

let config = try ClientConfig(endpoint: "http://localhost:6420")
let client = RivetKitClient(config: config)
let handle = client.getOrCreate("counter", ["my-counter"])

let args: [JSONValue] = [
    .string("user-1"),
    .number(.int(42)),
    .string("extra"),
    .string("more"),
    .string("args"),
    .string("here")
]
let ok: Bool = try await handle.action("setScore", args: args, as: Bool.self)
print("成功：\(ok)")

await client.dispose()
```

## 连接参数

```swift
import RivetKitClient

struct ConnParams: Encodable {
    let authToken: String
}

let config = try ClientConfig(endpoint: "http://localhost:6420")
let client = RivetKitClient(config: config)

let chat = client.getOrCreate(
    "chatRoom",
    ["general"],
    options: GetOrCreateOptions(params: ConnParams(authToken: "jwt-token-here"))
)

let conn = chat.connect()

// 使用连接...
for await status in await conn.statusChanges() {
    print("状态：\(status.rawValue)")
    if status == .connected {
        break
    }
}

await conn.dispose()
await client.dispose()
```

## 订阅事件

```swift
import RivetKitClient

let config = try ClientConfig(endpoint: "http://localhost:6420")
let client = RivetKitClient(config: config)
let conn = client.getOrCreate("chatRoom", ["general"]).connect()

// 使用 AsyncStream 订阅事件
let messageTask = Task {
    for await (from, body) in await conn.events("message", as: (String, String).self) {
        print("\(from): \(body)")
    }
}

// 对于一次性事件，接收后中断
let gameOverTask = Task {
    for await _ in await conn.events("gameOver", as: Void.self) {
        print("完成")
        break
    }
}

// 运行一段时间
try await Task.sleep(for: .seconds(5))

// 完成时取消
messageTask.cancel()
gameOverTask.cancel()
await conn.dispose()
await client.dispose()
```

事件流支持 0-5 个类型参数。如果您需要原始值或超过 5 个参数，可以使用 `JSONValue`：

```swift
import RivetKitClient

let config = try ClientConfig(endpoint: "http://localhost:6420")
let client = RivetKitClient(config: config)
let conn = client.getOrCreate("chatRoom", ["general"]).connect()

let rawTask = Task {
    for await args in await conn.events("message") {
        print(args)
    }
}

try await Task.sleep(for: .seconds(5))
rawTask.cancel()
await conn.dispose()
await client.dispose()
```

## 连接生命周期

```swift
import RivetKitClient

let config = try ClientConfig(endpoint: "http://localhost:6420")
let client = RivetKitClient(config: config)
let conn = client.getOrCreate("chatRoom", ["general"]).connect()

// 监控状态变化（立即返回当前状态）
let statusTask = Task {
    for await status in await conn.statusChanges() {
        print("状态：\(status.rawValue)")
    }
}

// 监控错误
let errorTask = Task {
    for await error in await conn.errors() {
        print("错误：\(error.group).\(error.code)")
    }
}

// 监控打开/关闭事件
let openTask = Task {
    for await _ in await conn.opens() {
        print("已连接")
    }
}

let closeTask = Task {
    for await _ in await conn.closes() {
        print("已断开")
    }
}

// 检查当前状态
let current = await conn.currentStatus
print("当前状态：\(current.rawValue)")

// 运行一段时间
try await Task.sleep(for: .seconds(5))

// 清理
statusTask.cancel()
errorTask.cancel()
openTask.cancel()
closeTask.cancel()
await conn.dispose()
await client.dispose()
```

## 低级 HTTP & WebSocket

对于实现 `onRequest` 或 `onWebSocket` 的 Actors，您可以直接调用它们：

```swift
import RivetKitClient

let config = try ClientConfig(endpoint: "http://localhost:6420")
let client = RivetKitClient(config: config)
let handle = client.getOrCreate("chatRoom", ["general"])

// 原始 HTTP 请求
let response = try await handle.fetch("history")
let history: [String] = try response.json([String].self)
print("历史记录：\(history)")

// 原始 WebSocket 连接
let websocket = try await handle.websocket(path: "stream")
try await websocket.send(text: "hello")
let message = try await websocket.receive()
print("接收：\(message)")

await client.dispose()
```

## 从后端调用

在服务器端 Swift（Vapor、Hummingbird 等）中使用相同的客户端：

```swift
import RivetKitClient

let config = try ClientConfig(endpoint: "http://localhost:6420")
let client = RivetKitClient(config: config)

let handle = client.getOrCreate("counter", ["server-counter"])
let count: Int = try await handle.action("increment", 1, as: Int.self)
print("计数：\(count)")

await client.dispose()
```

## 错误处理

```swift
import RivetKitClient

let config = try ClientConfig(endpoint: "http://localhost:6420")
let client = RivetKitClient(config: config)

do {
    _ = try await client.getOrCreate("user", ["user-123"])
        .action("updateUsername", "ab", as: String.self)
} catch let error as ActorError {
    print("错误代码：\(error.code)")
    print("元数据：\(String(describing: error.metadata))")
}

await client.dispose()
```

如果您需要一个无类型的响应，可以解码到 `JSONValue`：

```swift
import RivetKitClient

let config = try ClientConfig(endpoint: "http://localhost:6420")
let client = RivetKitClient(config: config)
let handle = client.getOrCreate("data", ["raw"])

let value: JSONValue = try await handle.action("getRawPayload")
print("原始值：\(value)")

await client.dispose()
```

## 概念

### 键

键唯一标识 Actor 实例。使用复合键（数组）进行分层寻址：

```swift
import RivetKitClient

let config = try ClientConfig(endpoint: "http://localhost:6420")
let client = RivetKitClient(config: config)

// 使用复合键进行分层寻址
let room = client.getOrCreate("chatRoom", ["org-acme", "general"])
let actorId = try await room.resolve()
print("Actor ID：\(actorId)")

await client.dispose()
```

不要使用字符串插值（如 `"org:\(userId)"`）构建键，当 `userId` 包含用户数据时。使用数组来防止键注入攻击。

### 环境变量

`ClientConfig` 从环境变量读取可选值：

- `RIVET_NAMESPACE` - 命名空间（也可以在端点 URL 中）
- `RIVET_TOKEN` - 认证令牌（也可以在端点 URL 中）
- `RIVET_RUNNER` - 运行器名称（默认为 `"default"`）

`endpoint` 参数始终是必需的。没有默认端点。

### 端点格式

端点支持 URL 认证语法：

```
https://namespace:token@api.rivet.dev
```

您也可以不传递认证的端点，并单独提供 `RIVET_NAMESPACE` 和 `RIVET_TOKEN`。对于无服务器部署，将端点设置为您的应用程序的 `/api/rivet` URL。有关详细信息，请参阅 [端点](/docs/general/endpoints#url-auth-syntax)。

## API 参考

### 客户端

- `RivetKitClient(config:)` - 使用配置创建客户端
- `ClientConfig` - 配置端点、命名空间和令牌
- `client.get()` / `getOrCreate()` / `getForId()` / `create()` - 获取 Actor 处理
- `client.dispose()` - 释放客户端和所有连接

### ActorHandle

- `handle.action(name, args..., as:)` - 无状态动作调用
- `handle.connect()` - 创建有状态连接
- `handle.resolve()` - 获取 Actor ID
- `handle.getGatewayUrl()` - 获取原始网关 URL
- `handle.fetch(path, request:)` - 原始 HTTP 请求
- `handle.websocket(path:)` - 原始 WebSocket 连接

### ActorConnection

- `conn.action(name, args..., as:)` - 通过 WebSocket 调用动作
- `conn.events(name, as:)` - 类型化事件的 AsyncStream
- `conn.statusChanges()` - 状态变化的 AsyncStream
- `conn.errors()` - 连接错误的 AsyncStream
- `conn.opens()` - 在连接打开时产生事件的 AsyncStream
- `conn.closes()` - 在连接关闭时产生事件的 AsyncStream
- `conn.currentStatus` - 当前连接状态
- `conn.dispose()` - 关闭连接

### 类型

- `ActorConnStatus` - 连接状态枚举（`.idle`, `.connecting`, `.connected`, `.disconnected`, `.disposed`）
- `ActorError` - 带有 `group`, `code`, `message`, `metadata` 的类型化 Actor 错误
- `JSONValue` - 用于无类型响应的原始 JSON 值

## 需要客户端以外的功能？

如果您需要更多关于 Rivet Actors、注册中心或服务器端 RivetKit 的信息，请添加主技能：

```bash
npx skills add rivet-dev/skills
```

然后使用 `rivetkit` 技能获取后端指导。
