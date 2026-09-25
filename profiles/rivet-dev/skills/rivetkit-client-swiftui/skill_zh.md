# RivetKit SwiftUI 客户端

在构建连接到 Rivet Actors 的 SwiftUI 应用程序时使用此技能，使用 `RivetKitSwiftUI`。

## 版本

RivetKit 版本：2.3.7

## 错误处理策略

- 默认情况下优先采用快速失败行为。
- 除非绝对必要，否则避免使用宽泛的 `do/catch`。
- 如果使用 `catch` 块，请显式处理错误，至少记录错误。

## 安装

添加 Swift 包依赖项并导入 `RivetKitSwiftUI`：

```swift
// Package.swift
dependencies: [
    .package(url: "https://github.com/rivet-dev/rivetkit-swift", from: "2.0.0")
]

targets: [
    .target(
        name: "MyApp",
        dependencies: [
            .product(name: "RivetKitSwiftUI", package: "rivetkit-swift")
        ]
    )
]
```

`RivetKitSwiftUI` 重新导出 `RivetKitClient` 和 `SwiftUI`，因此单个导入即可涵盖两者。

## 最小客户端

```swift HelloWorldApp.swift
import RivetKitSwiftUI
import SwiftUI

@main
struct HelloWorldApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
                .rivetKit(endpoint: "https://my-namespace:pk_...@api.rivet.dev")
        }
    }
}
```

```swift ContentView.swift
import RivetKitSwiftUI
import SwiftUI

struct ContentView: View {
    @Actor("counter", key: ["my-counter"]) private var counter
    @State private var count = 0

    var body: some View {
        VStack(spacing: 16) {
            Text("\(count)")
                .font(.system(size: 64, weight: .bold, design: .rounded))

            Button("Increment") {
                counter.send("increment", 1)
            }
            .disabled(!counter.isConnected)
        }
        .task {
            count = (try? await counter.action("getCount")) ?? 0
        }
        .onActorEvent(counter, "newCount") { (newCount: Int) in
            count = newCount
        }
    }
}
```

## Actor 选项

`@Actor` 属性包装器始终使用获取或创建语义，并接受：

- `name`（必需）
- `key` 作为 `String` 或 `[String]`（必需）
- `params`（可选连接参数）
- `createWithInput`（可选创建输入）
- `createInRegion`（可选创建提示）
- `enabled`（切换连接生命周期）

```swift
import RivetKitSwiftUI
import SwiftUI

struct ConnParams: Encodable {
    let authToken: String
}

struct ChatView: View {
    @Actor(
        "chatRoom",
        key: ["general"],
        params: ConnParams(authToken: "jwt-token"),
        enabled: true
    ) private var chat

    var body: some View {
        Text("Chat: \(chat.connStatus.rawValue)")
    }
}
```

## 动作

```swift
import RivetKitSwiftUI
import SwiftUI

struct CounterView: View {
    @Actor("counter", key: ["my-counter"]) private var counter
    @State private var count = 0
    @State private var name = ""

    var body: some View {
        VStack {
            Text("Count: \(count)")
            Text("Name: \(name)")

            Button("Fetch") {
                Task {
                    count = try await counter.action("getCount")
                    name = try await counter.action("rename", "new-name")
                }
            }

            Button("Increment") {
                counter.send("increment", 1)
            }
        }
    }
}
```

## 订阅事件

```swift
import RivetKitSwiftUI
import SwiftUI

struct GameView: View {
    @Actor("game", key: ["game-1"]) private var game
    @State private var count = 0
    @State private var isGameOver = false

    var body: some View {
        VStack {
            Text("Count: \(count)")
            if isGameOver {
                Text("Game Over!")
            }
        }
        .onActorEvent(game, "newCount") { (newCount: Int) in
            count = newCount
        }
        .onActorEvent(game, "gameOver") {
            isGameOver = true
        }
    }
}
```

## 异步事件流

```swift
import RivetKitSwiftUI
import SwiftUI

struct ChatView: View {
    @Actor("chatRoom", key: ["general"]) private var chat
    @State private var messages: [String] = []

    var body: some View {
        List(messages, id: \.self) { message in
            Text(message)
        }
        .task {
            for await message in chat.events("message", as: String.self) {
                messages.append(message)
            }
        }
    }
}
```

## 连接状态

```swift
import RivetKitSwiftUI
import SwiftUI

struct StatusView: View {
    @Actor("counter", key: ["my-counter"]) private var counter
    @State private var count = 0

    var body: some View {
        VStack {
            Text("Status: \(counter.connStatus.rawValue)")

            if counter.connStatus == .connected {
                Text("Connected!")
                    .foregroundStyle(.green)
            }

            Button("Fetch via Handle") {
                Task {
                    if let handle = counter.handle {
                        count = try await handle.action("getCount", as: Int.self)
                    }
                }
            }
            .disabled(!counter.isConnected)
        }
    }
}
```

## 错误处理

```swift
import RivetKitSwiftUI
import SwiftUI

struct UserView: View {
    @Actor("user", key: ["user-123"]) private var user
    @State private var errorMessage: String?
    @State private var username = ""

    var body: some View {
        VStack {
            TextField("Username", text: $username)

            Button("Update Username") {
                Task {
                    do {
                        let _: String = try await user.action("updateUsername", username)
                    } catch let error as ActorError {
                        errorMessage = "\(error.code): \(String(describing: error.metadata))"
                    }
                }
            }

            if let errorMessage {
                Text(errorMessage)
                    .foregroundStyle(.red)
            }
        }
        .onActorError(user) { error in
            errorMessage = "\(error.group).\(error.code): \(error.message)"
        }
    }
}
```

## 概念

### 键

键唯一标识 actor 实例。使用复合键（数组）进行分层寻址：

```swift
import RivetKitSwiftUI
import SwiftUI

struct OrgChatView: View {
    @Actor("chatRoom", key: ["org-acme", "general"]) private var room

    var body: some View {
        Text("Room: \(room.connStatus.rawValue)")
    }
}
```

不要使用字符串插值（如 `"org:\(userId)"`）构建键，当 `userId` 包含用户数据时。使用数组代替，以防止键注入攻击。

### 环境配置

在视图树的根处调用 `.rivetKit(endpoint:)` 或 `.rivetKit(client:)` 一次：

```swift
// 使用端点字符串（大多数应用程序推荐）
@main
struct MyApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
                .rivetKit(endpoint: "https://my-namespace:pk_...@api.rivet.dev")
        }
    }
}

// 使用自定义客户端（用于高级配置）
@main
struct MyApp: App {
    private let client = RivetKitClient(
        config: try! ClientConfig(endpoint: "https://api.rivet.dev", token: "pk_...")
    )

    var body: some Scene {
        WindowGroup {
            ContentView()
                .rivetKit(client: client)
        }
    }
}
```

使用 `.rivetKit(endpoint:)` 时，客户端会根据端点创建一次并缓存。使用 `.rivetKit(client:)` 时，将客户端作为 `App` 的属性存储（而不是在 `body` 内部），因为 SwiftUI 可以多次调用 `body`。

### 环境变量

`ClientConfig` 从环境变量读取可选值：

- `RIVET_NAMESPACE` - 命名空间（也可以在端点 URL 中）
- `RIVET_TOKEN` - 身份验证令牌（也可以在端点 URL 中）
- `RIVET_RUNNER` - 运行器名称（默认为 `"default"`）

端点始终是必需的。没有默认端点。

### 端点格式

端点支持 URL 认证语法：

```
https://namespace:token@api.rivet.dev
```

您也可以不提供认证的端点，并单独提供 `RIVET_NAMESPACE` 和 `RIVET_TOKEN`。对于无服务器部署，将端点设置为应用程序的 `/api/rivet` URL。有关详细信息，请参阅 [端点](/docs/general/endpoints#url-auth-syntax)。

## API 参考

### 属性包装器
- `@Actor(name, key:, params:, createWithInput:, createInRegion:, enabled:)` - 用于 actor 连接的 SwiftUI 属性包装器

### 视图修饰符
- `.rivetKit(endpoint:)` - 使用端点 URL 配置客户端（创建缓存的客户端）
- `.rivetKit(client:)` - 使用自定义实例配置客户端
- `.onActorEvent(actor, event) { ... }` - 订阅 actor 事件（支持 0–5 个类型参数）
- `.onActorError(actor) { error in ... }` - 处理 actor 错误

### ActorObservable
- `actor.action(name, args..., as:)` - 异步动作调用
- `actor.send(name, args...)` - 一次性动作
- `actor.events(name, as:)` - 类型化的异步事件流
- `actor.connStatus` - 当前连接状态
- `actor.isConnected` - 是否连接
- `actor.handle` - 底层的 `ActorHandle`（可选）
- `actor.connection` - 底层的 `ActorConnection`（可选）
- `actor.error` - 最新的错误（可选）

### 类型
- `ActorConnStatus` - 连接状态枚举（`.idle`, `.connecting`, `.connected`, `.disconnected`, `.disposed`）
- `ActorError` - 带有 `group`, `code`, `message`, `metadata` 的类型化 actor 错误

## 需要更多客户端以外的功能？

如果您需要更多关于 Rivet Actors、注册中心或服务器端 RivetKit 的信息，请添加主要技能：

```bash
npx skills add rivet-dev/skills
```

然后使用 `rivetkit` 技能获取后端指导。
