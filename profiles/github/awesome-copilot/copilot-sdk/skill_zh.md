# GitHub Copilot SDK

使用 Python、TypeScript、Go 或 .NET 将 Copilot 的智能代理工作流程嵌入到任何应用程序中。

## 概述

GitHub Copilot SDK 暴露了与 Copilot CLI 相同的引擎：一个经过生产环境测试的代理运行时，您可以程序性地调用它。无需构建自己的编排 - 您定义代理行为，Copilot 处理计划、工具调用、文件编辑等。

## 前置条件

1. **GitHub Copilot 访问权限** 和一个经过身份验证的环境
2. **语言运行时**：Node.js ^20.19.0 或 >=22.12.0、Python 3.11+、Go 1.24+ 或 .NET Standard 2.0 兼容实现
3. **Go**：已安装并身份验证 GitHub Copilot CLI（[安装指南](https://docs.github.com/en/copilot/how-tos/set-up/install-copilot-cli)）

TypeScript、Python 和 .NET 包默认使用捆绑的 Copilot 运行时，因此它们不需要单独的 CLI 安装。

## 安装

### Node.js/TypeScript
```bash
mkdir copilot-demo && cd copilot-demo
npm init -y --init-type module
npm install @github/copilot-sdk tsx
```

### Python
```bash
pip install github-copilot-sdk

# 可选：预先下载捆绑的运行时，而不是在第一次使用时下载
python -m copilot download-runtime
```

发布的 Python 轮包包含一个固定的运行时版本。预下载命令将运行时缓存在本地；如果跳过，SDK 将在第一次使用时自动尝试下载它。

### Go
```bash
mkdir copilot-demo && cd copilot-demo
go mod init copilot-demo
go get github.com/github/copilot-sdk/go
```

### .NET
```bash
dotnet new console -n CopilotDemo && cd CopilotDemo
dotnet add package GitHub.Copilot.SDK
```

## 快速入门

### TypeScript
```typescript
import { CopilotClient, approveAll } from "@github/copilot-sdk";

const client = new CopilotClient();
const session = await client.createSession({
    onPermissionRequest: approveAll,
    model: "gpt-4.1",
});

const response = await session.sendAndWait({ prompt: "What is 2 + 2?" });
console.log(response?.data.content);

await client.stop();
process.exit(0);
```

运行：`npx tsx index.ts`

### Python
```python
import asyncio
from copilot import CopilotClient, PermissionHandler

async def main():
    async with CopilotClient() as client:
        async with await client.create_session(
            on_permission_request=PermissionHandler.approve_all,
            model="gpt-4.1",
        ) as session:
            response = await session.send_and_wait("What is 2 + 2?")
            print(response.data.content)

asyncio.run(main())
```

### Go
```go
package main

import (
    "fmt"
    "log"
    "os"
    copilot "github.com/github/copilot-sdk/go"
)

func main() {
    client := copilot.NewClient(nil)
    if err := client.Start(); err != nil {
        log.Fatal(err)
    }
    defer client.Stop()

    session, err := client.CreateSession(&copilot.SessionConfig{
        OnPermissionRequest: copilot.PermissionHandler.ApproveAll,
        Model:               "gpt-4.1",
    })
    if err != nil {
        log.Fatal(err)
    }

    response, err := session.SendAndWait(copilot.MessageOptions{Prompt: "What is 2 + 2?"}, 0)
    if err != nil {
        log.Fatal(err)
    }

    fmt.Println(*response.Data.Content)
    os.Exit(0)
}
```

### .NET (C#)
```csharp
using GitHub.Copilot.SDK;

await using var client = new CopilotClient();
await using var session = await client.CreateSessionAsync(new SessionConfig
{
    OnPermissionRequest = PermissionHandler.ApproveAll,
    Model = "gpt-4.1",
});

var response = await session.SendAndWaitAsync(new MessageOptions { Prompt = "What is 2 + 2?" });
Console.WriteLine(response?.Data.Content);
```

运行：`dotnet run`

## 流式传输响应

启用实时输出以获得更好的用户体验：

### TypeScript
```typescript
import { CopilotClient, approveAll, SessionEvent } from "@github/copilot-sdk";

const client = new CopilotClient();
const session = await client.createSession({
    onPermissionRequest: approveAll,
    model: "gpt-4.1",
    streaming: true,
});

session.on((event: SessionEvent) => {
    if (event.type === "assistant.message_delta") {
        process.stdout.write(event.data.deltaContent);
    }
    if (event.type === "session.idle") {
        console.log(); // 新行当完成时
    }
});

await session.sendAndWait({ prompt: "Tell me a short joke" });

await client.stop();
process.exit(0);
```

### Python
```python
import asyncio
import sys
from copilot import CopilotClient, PermissionHandler
from copilot.generated.session_events import SessionEventType

async def main():
    async with CopilotClient() as client:
        async with await client.create_session(
            on_permission_request=PermissionHandler.approve_all,
            model="gpt-4.1",
            streaming=True,
        ) as session:
            def handle_event(event):
                if event.type == SessionEventType.ASSISTANT_MESSAGE_DELTA:
                    sys.stdout.write(event.data.delta_content)
                    sys.stdout.flush()
                if event.type == SessionEventType.SESSION_IDLE:
                    print()

            session.on(handle_event)
            await session.send_and_wait("Tell me a short joke")

asyncio.run(main())
```

### Go
```go
session, err := client.CreateSession(&copilot.SessionConfig{
    OnPermissionRequest: copilot.PermissionHandler.ApproveAll,
    Model:     "gpt-4.1",
    Streaming: true,
})

session.On(func(event copilot.SessionEvent) {
    if event.Type == "assistant.message_delta" {
        fmt.Print(*event.Data.DeltaContent)
    }
    if event.Type == "session.idle" {
        fmt.Println()
    }
})

_, err = session.SendAndWait(copilot.MessageOptions{Prompt: "Tell me a short joke"}, 0)
```

### .NET
```csharp
await using var session = await client.CreateSessionAsync(new SessionConfig
{
    OnPermissionRequest = PermissionHandler.ApproveAll,
    Model = "gpt-4.1",
    Streaming = true,
});

session.On(ev =>
{
    if (ev is AssistantMessageDeltaEvent deltaEvent)
        Console.Write(deltaEvent.Data.DeltaContent);
    if (ev is SessionIdleEvent)
        Console.WriteLine();
});

await session.SendAndWaitAsync(new MessageOptions { Prompt = "Tell me a short joke" });
```

## 自定义工具

定义 Copilot 在推理过程中可以调用的工具。当您定义一个工具时，您告诉 Copilot：
1. **工具的作用是什么**（描述）
2. **它需要哪些参数**（模式）
3. **要运行什么代码**（处理程序）

### TypeScript (JSON Schema)
```typescript
import { CopilotClient, approveAll, defineTool, SessionEvent } from "@github/copilot-sdk";

const getWeather = defineTool("get_weather", {
    description: "获取一个城市的当前天气",
    parameters: {
        type: "object",
        properties: {
            city: { type: "string", description: "城市名称" },
        },
        required: ["city"],
    },
    handler: async (args: { city: string }) => {
        const { city } = args;
        // 在实际应用中，在这里调用天气 API
        const conditions = ["sunny", "cloudy", "rainy", "partly cloudy"];
        const temp = Math.floor(Math.random() * 30) + 50;
        const condition = conditions[Math.floor(Math.random() * conditions.length)];
        return { city, temperature: `${temp}°F`, condition };
    },
});

const client = new CopilotClient();
const session = await client.createSession({
    onPermissionRequest: approveAll,
    model: "gpt-4.1",
    streaming: true,
    tools: [getWeather],
});

session.on((event: SessionEvent) => {
    if (event.type === "assistant.message_delta") {
        process.stdout.write(event.data.deltaContent);
    }
});

await session.sendAndWait({
    prompt: "What's the weather like in Seattle and Tokyo?",
});

await client.stop();
process.exit(0);
```

### Python (Pydantic)
```python
import asyncio
import random
import sys
from copilot import CopilotClient, PermissionHandler
from copilot.tools import define_tool
from copilot.generated.session_events import SessionEventType
from pydantic import BaseModel, Field

class GetWeatherParams(BaseModel):
    city: str = Field(description="要获取天气的城市名称")

@define_tool(description="获取一个城市的当前天气")
async def get_weather(params: GetWeatherParams) -> dict:
    city = params.city
    conditions = ["sunny", "cloudy", "rainy", "partly cloudy"]
    temp = random.randint(50, 80)
    condition = random.choice(conditions)
    return {"city": city, "temperature": f"{temp}°F", "condition": condition}

async def main():
    async with CopilotClient() as client:
        async with await client.create_session(
            on_permission_request=PermissionHandler.approve_all,
            model="gpt-4.1",
            streaming=True,
            tools=[get_weather],
        ) as session:
            def handle_event(event):
                if event.type == SessionEventType.ASSISTANT_MESSAGE_DELTA:
                    sys.stdout.write(event.data.delta_content)
                    sys.stdout.flush()

            session.on(handle_event)
            await session.send_and_wait(
                "What's the weather like in Seattle and Tokyo?"
            )

asyncio.run(main())
```

### Go
```go
type WeatherParams struct {
    City string `json:"city" jsonschema:"城市名称"`
}

type WeatherResult struct {
    City        string `json:"city"`
    Temperature string `json:"temperature"`
    Condition   string `json:"condition"`
}

getWeather := copilot.DefineTool(
    "get_weather",
    "获取一个城市的当前天气",
    func(params WeatherParams, inv copilot.ToolInvocation) (WeatherResult, error) {
        conditions := []string{"sunny", "cloudy", "rainy", "partly cloudy"}
        temp := rand.Intn(30) + 50
        condition := conditions[rand.Intn(len(conditions))]
        return WeatherResult{
            City:        params.City,
            Temperature: fmt.Sprintf("%d°F", temp),
            Condition:   condition,
        }, nil
    },
)

session, _ := client.CreateSession(&copilot.SessionConfig{
    OnPermissionRequest: copilot.PermissionHandler.ApproveAll,
    Model: "gpt-4.1",
    Streaming: true,
    Tools:     []copilot.Tool{getWeather},
})
```

### .NET (Microsoft.Extensions.AI)
```csharp
using GitHub.Copilot.SDK;
using Microsoft.Extensions.AI;
using System.ComponentModel;

var getWeather = AIFunctionFactory.Create(
    ([Description("城市名称")] string city) =>
    {
        var conditions = new[] { "sunny", "cloudy", "rainy", "partly cloudy" };
        var temp = Random.Shared.Next(50, 80);
        var condition = conditions[Random.Shared.Next(conditions.Length)];
        return new { city, temperature = $"{temp}°F", condition };
    },
    "get_weather",
    "获取一个城市的当前天气"
);

await using var session = await client.CreateSessionAsync(new SessionConfig
{
    OnPermissionRequest = PermissionHandler.ApproveAll,
    Model = "gpt-4.1",
    Streaming = true,
    Tools = [getWeather],
});
```

## 工具的工作原理

当 Copilot 决定调用您的工具时：
1. Copilot 发送带有参数的工具调用请求
2. SDK 运行您的处理程序函数
3. 结果发送回 Copilot
4. Copilot 将结果合并到其响应中

Copilot 根据用户的问题和您的工具描述决定何时调用您的工具。

## 交互式 CLI 助手

构建一个完整的交互式助手：

### TypeScript
```typescript
import { CopilotClient, approveAll, defineTool, SessionEvent } from "@github/copilot-sdk";
import * as readline from "readline";

const getWeather = defineTool("get_weather", {
    description: "获取一个城市的当前天气",
    parameters: {
        type: "object",
        properties: {
            city: { type: "string", description: "城市名称" },
        },
        required: ["city"],
    },
    handler: async ({ city }) => {
        const conditions = ["sunny", "cloudy", "rainy", "partly cloudy"];
        const temp = Math.floor(Math.random() * 30) + 50;
        const condition = conditions[Math.floor(Math.random() * conditions.length)];
        return { city, temperature: `${temp}°F`, condition };
    },
});

const client = new CopilotClient();
const session = await client.createSession({
    onPermissionRequest: approveAll,
    model: "gpt-4.1",
    streaming: true,
    tools: [getWeather],
});

session.on((event: SessionEvent) => {
    if (event.type === "assistant.message_delta") {
        process.stdout.write(event.data.deltaContent);
    }
});

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
});

console.log("Weather Assistant (type 'exit' to quit)");
console.log("Try: 'What's the weather in Paris?'\n");

const prompt = () => {
    rl.question("You: ", async (input) => {
        if (input.toLowerCase() === "exit") {
            await client.stop();
            rl.close();
            return;
        }

        process.stdout.write("Assistant: ");
        await session.sendAndWait({ prompt: input });
        console.log("\n");
        prompt();
    });
};

prompt();
```

### Python
```python
import asyncio
import random
import sys
from copilot import CopilotClient, PermissionHandler
from copilot.tools import define_tool
from copilot.generated.session_events import SessionEventType
from pydantic import BaseModel, Field

class GetWeatherParams(BaseModel):
    city: str = Field(description="要获取天气的城市名称")

@define_tool(description="获取一个城市的当前天气")
async def get_weather(params: GetWeatherParams) -> dict:
    conditions = ["sunny", "cloudy", "rainy", "partly cloudy"]
    temp = random.randint(50, 80)
    condition = random.choice(conditions)
    return {"city": params.city, "temperature": f"{temp}°F", "condition": condition}

async def main():
    async with CopilotClient() as client:
        async with await client.create_session(
            on_permission_request=PermissionHandler.approve_all,
            model="gpt-4.1",
            streaming=True,
            tools=[get_weather],
        ) as session:
            def handle_event(event):
                if event.type == SessionEventType.ASSISTANT_MESSAGE_DELTA:
                    sys.stdout.write(event.data.delta_content)
                    sys.stdout.flush()

            session.on(handle_event)

            print("Weather Assistant (type 'exit' to quit)")
            print("Try: 'What's the weather in Paris?'\n")

            while True:
                try:
                    user_input = input("You: ")
                except EOFError:
                    break

                if user_input.lower() == "exit":
                    break

                sys.stdout.write("Assistant: ")
                await session.send_and_wait(user_input)
                print("\n")

asyncio.run(main())
```

## MCP 服务器集成

连接到 MCP（模型上下文协议）服务器以获取预构建的工具。连接到 GitHub 的 MCP 服务器以获取存储库、问题和拉取请求的访问权限：

### TypeScript
```typescript
const session = await client.createSession({
    onPermissionRequest: approveAll,
    model: "gpt-4.1",
    mcpServers: {
        github: {
            type: "http",
            url: "https://api.githubcopilot.com/mcp/",
        },
    },
});
```

### Python
```python
async with await client.create_session(
    on_permission_request=PermissionHandler.approve_all,
    model="gpt-4.1",
    mcp_servers={
        "github": {
            "type": "http",
            "url": "https://api.githubcopilot.com/mcp/",
        },
    },
) as session:
    ...
```

### Go
```go
session, _ := client.CreateSession(&copilot.SessionConfig{
    OnPermissionRequest: copilot.PermissionHandler.ApproveAll,
    Model: "gpt-4.1",
    MCPServers: map[string]copilot.MCPServerConfig{
        "github": {
            "type": "http",
            "url": "https://api.githubcopilot.com/mcp/",
        },
    },
})
```

### .NET
```csharp
await using var session = await client.CreateSessionAsync(new SessionConfig
{
    OnPermissionRequest = PermissionHandler.ApproveAll,
    Model = "gpt-4.1",
    McpServers = new Dictionary<string, McpServerConfig>
    {
        ["github"] = new McpServerConfig
        {
            Type = "http",
            Url = "https://api.githubcopilot.com/mcp/",
        },
    },
});
```

## 自定义代理

定义用于特定任务的专用 AI 人格：

### TypeScript
```typescript
const session = await client.createSession({
    onPermissionRequest: approveAll,
    model: "gpt-4.1",
    customAgents: [{
        name: "pr-reviewer",
        displayName: "PR Reviewer",
        description: "审查拉取请求的最佳实践",
        prompt: "You are an expert code reviewer. Focus on security, performance, and maintainability.",
    }],
});
```

### Python
```python
async with await client.create_session(
    on_permission_request=PermissionHandler.approve_all,
    model="gpt-4.1",
    custom_agents=[{
        "name": "pr-reviewer",
        "display_name": "PR Reviewer",
        "description": "审查拉取请求的最佳实践",
        "prompt": "You are an expert code reviewer. Focus on security, performance, and maintainability.",
    }],
) as session:
    ...
```

## 系统消息

自定义 AI 的行为和个性：

### TypeScript
```typescript
const session = await client.createSession({
    onPermissionRequest: approveAll,
    model: "gpt-4.1",
    systemMessage: {
        content: "You are a helpful assistant for our engineering team. Always be concise.",
    },
});
```

### Python
```python
async with await client.create_session(
    on_permission_request=PermissionHandler.approve_all,
    model="gpt-4.1",
    system_message={
        "content": "You are a helpful assistant for our engineering team. Always be concise.",
    },
) as session:
    ...
```

## 外部 CLI 服务器

单独以服务器模式运行 CLI，并将 SDK 连接到它。适用于调试、资源共享或自定义环境。

### 以服务器模式启动 CLI
```bash
copilot --server --port 4321
```

### 将 SDK 连接到外部服务器

#### TypeScript
```typescript
const client = new CopilotClient({
    cliUrl: "localhost:4321"
});

const session = await client.createSession({
    onPermissionRequest: approveAll,
    model: "gpt-4.1",
});
```

#### Python
```python
from copilot import CopilotClient, PermissionHandler, RuntimeConnection

async with CopilotClient(
    connection=RuntimeConnection.for_uri("localhost:4321")
) as client:
    async with await client.create_session(
        on_permission_request=PermissionHandler.approve_all,
        model="gpt-4.1",
    ) as session:
        ...
```

#### Go
```go
client := copilot.NewClient(&copilot.ClientOptions{
    CLIUrl: "localhost:4321",
})

if err := client.Start(); err != nil {
    log.Fatal(err)
}

session, _ := client.CreateSession(&copilot.SessionConfig{
    OnPermissionRequest: copilot.PermissionHandler.ApproveAll,
    Model:               "gpt-4.1",
})
```

#### .NET
```csharp
using var client = new CopilotClient(new CopilotClientOptions
{
    CliUrl = "localhost:4321"
});

await using var session = await client.CreateSessionAsync(new SessionConfig
{
    OnPermissionRequest = PermissionHandler.ApproveAll,
    Model = "gpt-4.1",
});
```

**注意**：配置为使用外部服务器时，SDK 仅管理其连接，不管理外部进程。

## 事件类型

| 事件 | 描述 |
|-------|-------------|
| `user.message` | 用户输入添加 |
| `assistant.message` | 完整模型响应 |
| `assistant.message_delta` | 流式传输响应块 |
| `assistant.reasoning` | 模型推理（取决于模型） |
| `assistant.reasoning_delta` | 流式传输推理块 |
| `tool.execution_start` | 工具调用开始 |
| `tool.execution_complete` | 工具执行完成 |
| `session.idle` | 没有活动处理 |
| `session.error` | 发生错误 |

## 客户端配置

| 选项 | 描述 | 默认 |
|--------|-------------|---------|
| `cliPath` | Copilot CLI 可执行文件的路径 | 系统PATH |
| `cliUrl` | 连接到现有服务器（例如，"localhost:4321"） | 无 |
| `port` | 服务器通信端口 | 随机 |
| `useStdio` | 使用 stdio 传输而不是 TCP | true |
| `logLevel` | 日志详细程度 | "info" |
| `autoStart` | 自动启动服务器 | true |
| `autoRestart` | 故障时重启 | true |
| `cwd` | CLI 进程的工作目录 | 继承 |

## 会话配置

| 选项 | 描述 |
|--------|-------------|
| `model` | 要使用的 LLM（"gpt-4.1", "claude-sonnet-4.5" 等） |
| `sessionId` | 自定义会话标识符 |
| `tools` | 自定义工具定义 |
| `mcpServers` | MCP 服务器连接 |
| `customAgents` | 自定义代理人格 |
| `systemMessage` | 覆盖默认系统提示 |
| `streaming` | 启用增量响应块 |
| `availableTools` | 允许的工具白名单 |
| `excludedTools` | 禁用工具黑名单 |

## 会话持久化

跨重启保存和恢复对话：

### 使用自定义 ID 创建
```typescript
const session = await client.createSession({
    onPermissionRequest: approveAll,
    sessionId: "user-123-conversation",
    model: "gpt-4.1"
});
```

### 恢复会话
```typescript
const session = await client.resumeSession("user-123-conversation", { onPermissionRequest: approveAll });
await session.send({ prompt: "What did we discuss earlier?" });
```

### 列出和删除会话
```typescript
const sessions = await client.listSessions();
await client.deleteSession("old-session-id");
```

## 错误处理

```typescript
try {
    const client = new CopilotClient();
    const session = await client.createSession({
        onPermissionRequest: approveAll,
        model: "gpt-4.1",
    });
    const response = await session.sendAndWait(
        { prompt: "Hello!" },
        30000 // 超时以毫秒计
    );
} catch (error) {
    if (error.code === "ENOENT") {
        console.error("Copilot CLI not installed");
    } else if (error.code === "ECONNREFUSED") {
        console.error("Cannot connect to Copilot server");
    } else {
        console.error("Error:", error.message);
    }
} finally {
    await client.stop();
}
```

## 平稳关闭

```typescript
process.on("SIGINT", async () => {
    console.log("Shutting down...");
    await client.stop();
    process.exit(0);
});
```

## 常见模式

### 多轮对话
```typescript
const session = await client.createSession({
    onPermissionRequest: approveAll,
    model: "gpt-4.1",
});

await session.sendAndWait({ prompt: "My name is Alice" });
await session.sendAndWait({ prompt: "What's my name?" });
// 响应: "Your name is Alice"
```

### 文件附件
```typescript
await session.send({
    prompt: "Analyze this file",
    attachments: [{
        type: "file",
        path: "./data.csv",
        displayName: "Sales Data"
    }]
});
```

### 中断长时间操作
```typescript
const timeoutId = setTimeout(() => {
    session.abort();
}, 60000);

session.on((event) => {
    if (event.type === "session.idle") {
        clearTimeout(timeoutId);
    }
});
```

## 可用模型

在运行时查询可用模型：

```typescript
const models = await client.getModels();
// 返回: ["gpt-4.1", "gpt-4o", "claude-sonnet-4.5", ...]
```

## 最佳实践

1. **始终清理**：使用语言原生上下文管理器或释放，或显式断开会话并停止客户端
2. **设置超时**：使用 `sendAndWait` 带超时进行长时间操作
3. **处理事件**：订阅错误事件以进行健壮的错误处理
4. **使用流式传输**：启用流式传输以在长响应上获得更好的用户体验
5. **持久化会话**：使用自定义会话 ID 进行多轮对话
6. **定义清晰的工具**：编写描述性工具名称和描述

## 架构

```
您的应用程序
       |
  SDK Client
       | JSON-RPC
  Copilot CLI (服务器模式)
       |
  GitHub (模型, 认证)
```

SDK 自动管理 CLI 进程生命周期。所有通信都通过 JSON-RPC 通过 stdio 或 TCP 进行。
