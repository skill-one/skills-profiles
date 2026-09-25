# Swift MCP Server Generator

使用官方 Swift SDK 包生成完整的、可生产使用的 MCP 服务器。

## 项目生成

当被要求创建一个 Swift MCP 服务器时，生成一个具有以下结构的完整项目：

```
my-mcp-server/
├── Package.swift
├── Sources/
│   └── MyMCPServer/
│       ├── main.swift
│       ├── Server.swift
│       ├── Tools/
│       │   ├── ToolDefinitions.swift
│       │   └── ToolHandlers.swift
│       ├── Resources/
│       │   ├── ResourceDefinitions.swift
│       │   └── ResourceHandlers.swift
│       └── Prompts/
│           ├── PromptDefinitions.swift
│           └── PromptHandlers.swift
├── Tests/
│   └── MyMCPServerTests/
│       └── ServerTests.swift
└── README.md
```

## Package.swift 模板

```swift
// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "MyMCPServer",
    platforms: [
        .macOS(.v13),
        .iOS(.v16),
        .watchOS(.v9),
        .tvOS(.v16),
        .visionOS(.v1)
    ],
    dependencies: [
        .package(
            url: "https://github.com/modelcontextprotocol/swift-sdk.git",
            from: "0.10.0"
        ),
        .package(
            url: "https://github.com/apple/swift-log.git",
            from: "1.5.0"
        ),
        .package(
            url: "https://github.com/swift-server/swift-service-lifecycle.git",
            from: "2.0.0"
        )
    ],
    targets: [
        .executableTarget(
            name: "MyMCPServer",
            dependencies: [
                .product(name: "MCP", package: "swift-sdk"),
                .product(name: "Logging", package: "swift-log"),
                .product(name: "ServiceLifecycle", package: "swift-service-lifecycle")
            ]
        ),
        .testTarget(
            name: "MyMCPServerTests",
            dependencies: ["MyMCPServer"]
        )
    ]
)
```

## main.swift 模板

```swift
import MCP
import Logging
import ServiceLifecycle

struct MCPService: Service {
    let server: Server
    let transport: Transport
    
    func run() async throws {
        try await server.start(transport: transport) { clientInfo, capabilities in
            logger.info("Client connected", metadata: [
                "name": .string(clientInfo.name),
                "version": .string(clientInfo.version)
            ])
        }
        
        // 保持服务运行
        try await Task.sleep(for: .days(365 * 100))
    }
    
    func shutdown() async throws {
        logger.info("Shutting down MCP server")
        await server.stop()
    }
}

var logger = Logger(label: "com.example.mcp-server")
logger.logLevel = .info

do {
    let server = await createServer()
    let transport = StdioTransport(logger: logger)
    let service = MCPService(server: server, transport: transport)
    
    let serviceGroup = ServiceGroup(
        services: [service],
        configuration: .init(
            gracefulShutdownSignals: [.sigterm, .sigint]
        ),
        logger: logger
    )
    
    try await serviceGroup.run()
} catch {
    logger.error("Fatal error", metadata: ["error": .string("\(error)")])
    throw error
}
```

## Server.swift 模板

```swift
import MCP
import Logging

func createServer() async -> Server {
    let server = Server(
        name: "MyMCPServer",
        version: "1.0.0",
        capabilities: .init(
            prompts: .init(listChanged: true),
            resources: .init(subscribe: true, listChanged: true),
            tools: .init(listChanged: true)
        )
    )
    
    // 注册工具处理器
    await registerToolHandlers(server: server)
    
    // 注册资源处理器
    await registerResourceHandlers(server: server)
    
    // 注册提示处理器
    await registerPromptHandlers(server: server)
    
    return server
}
```

## ToolDefinitions.swift 模板

```swift
import MCP

func getToolDefinitions() -> [Tool] {
    [
        Tool(
            name: "greet",
            description: "生成问候消息",
            inputSchema: .object([
                "type": .string("object"),
                "properties": .object([
                    "name": .object([
                        "type": .string("string"),
                        "description": .string("要问候的名称")
                    ])
                ]),
                "required": .array([.string("name")])
            ])
        ),
        Tool(
            name: "calculate",
            description: "执行数学计算",
            inputSchema: .object([
                "type": .string("object"),
                "properties": .object([
                    "operation": .object([
                        "type": .string("string"),
                        "enum": .array([
                            .string("add"),
                            .string("subtract"),
                            .string("multiply"),
                            .string("divide")
                        ]),
                        "description": .string("要执行的操作")
                    ]),
                    "a": .object([
                        "type": .string("number"),
                        "description": .string("第一个操作数")
                    ]),
                    "b": .object([
                        "type": .string("number"),
                        "description": .string("第二个操作数")
                    ])
                ]),
                "required": .array([
                    .string("operation"),
                    .string("a"),
                    .string("b")
                ])
            ])
        )
    ]
}
```

## ToolHandlers.swift 模板

```swift
import MCP
import Logging

private let logger = Logger(label: "com.example.mcp-server.tools")

func registerToolHandlers(server: Server) async {
    await server.withMethodHandler(ListTools.self) { _ in
        logger.debug("列出可用工具")
        return .init(tools: getToolDefinitions())
    }
    
    await server.withMethodHandler(CallTool.self) { params in
        logger.info("调用工具", metadata: ["name": .string(params.name)])
        
        switch params.name {
        case "greet":
            return handleGreet(params: params)
            
        case "calculate":
            return handleCalculate(params: params)
            
        default:
            logger.warning("请求未知工具", metadata: ["name": .string(params.name)])
            return .init(
                content: [.text("未知工具: \(params.name)")],
                isError: true
            )
        }
    }
}

private func handleGreet(params: CallTool.Params) -> CallTool.Result {
    guard let name = params.arguments?["name"]?.stringValue else {
        return .init(
            content: [.text("缺少 'name' 参数")],
            isError: true
        )
    }
    
    let greeting = "你好，\(name)! 欢迎使用 MCP。"
    logger.debug("生成问候消息", metadata: ["name": .string(name)])
    
    return .init(
        content: [.text(greeting)],
        isError: false
    )
}

private func handleCalculate(params: CallTool.Params) -> CallTool.Result {
    guard let operation = params.arguments?["operation"]?.stringValue,
          let a = params.arguments?["a"]?.doubleValue,
          let b = params.arguments?["b"]?.doubleValue else {
        return .init(
            content: [.text("缺少或无效的参数")],
            isError: true
        )
    }
    
    let result: Double
    switch operation {
    case "add":
        result = a + b
    case "subtract":
        result = a - b
    case "multiply":
        result = a * b
    case "divide":
        guard b != 0 else {
            return .init(
                content: [.text("除以零")],
                isError: true
            )
        }
        result = a / b
    default:
        return .init(
            content: [.text("未知操作: \(operation)")],
            isError: true
        )
    }
    
    logger.debug("执行计算", metadata: [
        "operation": .string(operation),
        "result": .string("\(result)")
    ])
    
    return .init(
        content: [.text("结果: \(result)")],
        isError: false
    )
}
```

## ResourceDefinitions.swift 模板

```swift
import MCP

func getResourceDefinitions() -> [Resource] {
    [
        Resource(
            name: "示例数据",
            uri: "resource://data/example",
            description: "示例资源数据",
            mimeType: "application/json"
        ),
        Resource(
            name: "配置",
            uri: "resource://config",
            description: "服务器配置",
            mimeType: "application/json"
        )
    ]
}
```

## ResourceHandlers.swift 模板

```swift
import MCP
import Logging
import Foundation

private let logger = Logger(label: "com.example.mcp-server.resources")

actor ResourceState {
    private var subscriptions: Set<String> = []
    
    func addSubscription(_ uri: String) {
        subscriptions.insert(uri)
    }
    
    func removeSubscription(_ uri: String) {
        subscriptions.remove(uri)
    }
    
    func isSubscribed(_ uri: String) -> Bool {
        subscriptions.contains(uri)
    }
}

private let state = ResourceState()

func registerResourceHandlers(server: Server) async {
    await server.withMethodHandler(ListResources.self) { params in
        logger.debug("列出可用资源")
        return .init(resources: getResourceDefinitions(), nextCursor: nil)
    }
    
    await server.withMethodHandler(ReadResource.self) { params in
        logger.info("读取资源", metadata: ["uri": .string(params.uri)])
        
        switch params.uri {
        case "resource://data/example":
            let jsonData = """
            {
                "message": "示例资源数据",
                "timestamp": "\(Date())"
            }
            """
            return .init(contents: [
                .text(jsonData, uri: params.uri, mimeType: "application/json")
            ])
            
        case "resource://config":
            let config = """
            {
                "serverName": "MyMCPServer",
                "version": "1.0.0"
            }
            """
            return .init(contents: [
                .text(config, uri: params.uri, mimeType: "application/json")
            ])
            
        default:
            logger.warning("请求未知资源", metadata: ["uri": .string(params.uri)])
            throw MCPError.invalidParams("未知资源 URI: \(params.uri)")
        }
    }
    
    await server.withMethodHandler(ResourceSubscribe.self) { params in
        logger.info("客户端订阅了资源", metadata: ["uri": .string(params.uri)])
        await state.addSubscription(params.uri)
        return .init()
    }
    
    await server.withMethodHandler(ResourceUnsubscribe.self) { params in
        logger.info("客户端取消订阅了资源", metadata: ["uri": .string(params.uri)])
        await state.removeSubscription(params.uri)
        return .init()
    }
}
```

## PromptDefinitions.swift 模板

```swift
import MCP

func getPromptDefinitions() -> [Prompt] {
    [
        Prompt(
            name: "code-review",
            description: "生成代码审查提示",
            arguments: [
                .init(name: "language", description: "编程语言", required: true),
                .init(name: "focus", description: "审查重点区域", required: false)
            ]
        )
    ]
}
```

## PromptHandlers.swift 模板

```swift
import MCP
import Logging

private let logger = Logger(label: "com.example.mcp-server.prompts")

func registerPromptHandlers(server: Server) async {
    await server.withMethodHandler(ListPrompts.self) { params in
        logger.debug("列出可用提示")
        return .init(prompts: getPromptDefinitions(), nextCursor: nil)
    }
    
    await server.withMethodHandler(GetPrompt.self) { params in
        logger.info("获取提示", metadata: ["name": .string(params.name)])
        
        switch params.name {
        case "code-review":
            return handleCodeReviewPrompt(params: params)
            
        default:
            logger.warning("请求未知提示", metadata: ["name": .string(params.name)])
            throw MCPError.invalidParams("未知提示: \(params.name)")
        }
    }
}

private func handleCodeReviewPrompt(params: GetPrompt.Params) -> GetPrompt.Result {
    guard let language = params.arguments?["language"]?.stringValue else {
        return .init(
            description: "缺少语言参数",
            messages: []
        )
    }
    
    let focus = params.arguments?["focus"]?.stringValue ?? "general quality"
    
    let description = "针对 \(language) 的代码审查，重点关注 \(focus)"
    let messages: [Prompt.Message] = [
        .user("请审查这段 \(language) 代码，重点关注 \(focus)。"),
        .assistant("我会专注于 \(focus) 审查代码。请分享代码。"),
        .user("这是要审查的代码: [在此处粘贴代码]")
    ]
    
    logger.debug("生成代码审查提示", metadata: [
        "language": .string(language),
        "focus": .string(focus)
    ])
    
    return .init(description: description, messages: messages)
}
```

## ServerTests.swift 模板

```swift
import XCTest
@testable import MyMCPServer

final class ServerTests: XCTestCase {
    func testGreetTool() async throws {
        let params = CallTool.Params(
            name: "greet",
            arguments: ["name": .string("Swift")]
        )
        
        let result = handleGreet(params: params)
        
        XCTAssertFalse(result.isError ?? true)
        XCTAssertEqual(result.content.count, 1)
        
        if case .text(let message) = result.content[0] {
            XCTAssertTrue(message.contains("Swift"))
        } else {
            XCTFail("预期文本内容")
        }
    }
    
    func testCalculateTool() async throws {
        let params = CallTool.Params(
            name: "calculate",
            arguments: [
                "operation": .string("add"),
                "a": .number(5),
                "b": .number(3)
            ]
        )
        
        let result = handleCalculate(params: params)
        
        XCTAssertFalse(result.isError ?? true)
        XCTAssertEqual(result.content.count, 1)
        
        if case .text(let message) = result.content[0] {
            XCTAssertTrue(message.contains("8"))
        } else {
            XCTFail("预期文本内容")
        }
    }
    
    func testDivideByZero() async throws {
        let params = CallTool.Params(
            name: "calculate",
            arguments: [
                "operation": .string("divide"),
                "a": .number(10),
                "b": .number(0)
            ]
        )
        
        let result = handleCalculate(params: params)
        
        XCTAssertTrue(result.isError ?? false)
    }
}
```

## README.md 模板

```markdown
# MyMCPServer

一个使用 Swift 构建的 Model Context Protocol 服务器。

## 功能

- ✅ 工具：greet, calculate
- ✅ 资源：示例数据、配置
- ✅ 提示：code-review
- ✅ 使用 ServiceLifecycle 实现优雅关闭
- ✅ 使用 swift-log 实现结构化日志记录
- ✅ 完整的测试覆盖

## 要求

- Swift 6.0+
- macOS 13+, iOS 16+ 或 Linux

## 安装

```bash
swift build -c release
```

## 使用

运行服务器：

```bash
swift run
```

或者带日志记录：

```bash
LOG_LEVEL=debug swift run
```

## 测试

```bash
swift test
```

## 开发

服务器使用：
- [MCP Swift SDK](https://github.com/modelcontextprotocol/swift-sdk) - MCP 协议实现
- [swift-log](https://github.com/apple/swift-log) - 结构化日志记录
- [swift-service-lifecycle](https://github.com/swift-server/swift-service-lifecycle) - 优雅关闭

## 项目结构

- `Sources/MyMCPServer/main.swift` - 使用 ServiceLifecycle 的入口点
- `Sources/MyMCPServer/Server.swift` - 服务器配置
- `Sources/MyMCPServer/Tools/` - 工具定义和处理器
- `Sources/MyMCPServer/Resources/` - 资源定义和处理器
- `Sources/MyMCPServer/Prompts/` - 提示定义和处理器
- `Tests/` - 单元测试

## 许可证

MIT
```

## 生成说明

1. **询问项目名称和描述**
2. **生成所有文件**，使用正确的命名
3. **使用基于 actor 的状态** 实现线程安全
4. **包含全面的日志记录**，使用 swift-log
5. **实现优雅关闭**，使用 ServiceLifecycle
6. **为所有处理器添加测试**
7. **使用现代 Swift 并发**（async/await）
8. **遵循 Swift 命名规范**（camelCase、PascalCase）
9. **使用正确的 MCPError 处理错误**
10. **使用 doc 注释记录公共 API**

## 构建和运行

```bash
# 构建
swift build

# 运行
swift run

# 测试
swift test

# 发布构建
swift build -c release

# 安装
swift build -c release
cp .build/release/MyMCPServer /usr/local/bin/
```

## 与 Claude Desktop 集成

添加到 `claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "my-mcp-server": {
      "command": "/path/to/MyMCPServer"
    }
  }
}
```
