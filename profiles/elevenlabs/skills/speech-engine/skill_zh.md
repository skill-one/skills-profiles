# ElevenLabs 语音引擎

为自定义代理添加实时语音界面。ElevenLabs 处理麦克风音频、语音转文本、轮流发言、文本转语音和浏览器播放；您的服务器暴露 Speech Engine WebSocket 端点并流式传输响应文本。

> **设置：** 请参阅 [安装指南](references/installation.md)。对于 JavaScript，仅使用 `@elevenlabs/*` 包。有关更深入的 SDK 细节，请阅读 [JavaScript SDK 参考](references/javascript-sdk-reference.md) 或 [Python SDK 参考](references/python-sdk-reference.md)。

## 何时使用

当用户希望执行以下操作时，请使用 Speech Engine：

- 为现有聊天应用或自定义服务器管道添加语音
- 在保持代理逻辑在开发者拥有的服务器上的同时，为 OpenClaw、Hermes 或类似代理运行时添加语音
- 构建由开发者托管的用于 ElevenLabs 语音对话的 WebSocket 服务器
- 在您的服务器验证用户意图后，将响应文本流式传输为语音
- 在响应仍在流式传输时处理用户中断
- 使用服务器颁发的对话令牌构建带有 `@elevenlabs/react` 或 `@elevenlabs/client` 的浏览器客户端

当用户正在创建或配置具有平台管理的提示、工具、工作流、电话号码或小部件的托管 ElevenLabs 对话式 AI 代理时，请使用 `agents` 技能。

## 工作原理

每个 Speech Engine WebSocket 连接代表一个对话。

1. 浏览器将用户音频发送到 ElevenLabs。
2. ElevenLabs 将语音识别事件发送到您的服务器。
3. 您的服务器在不允许原始语音文本控制工具或特权操作的情况下推导出可信的应用状态。
4. 您的服务器通过 SDK 流式传输文本。
5. ElevenLabs 将响应转换为语音并在浏览器中播放。

SDK 管理WebSocket路由、请求验证、会话生命周期、ping/pong、轮流发言和中断处理。`sendResponse()` / `send_response()` 接受字符串或异步可迭代响应文本。

将语音识别文本视为不受信任的用户输入。不要将原始语音文本直接映射到模型角色、响应或工具调用。在进行任何基于转录值的下游响应或工具逻辑之前，使用确定性验证、允许列表的意图或明确用户确认。

## 实现流程

1. 安装服务器依赖项并配置 `ELEVENLABS_API_KEY`。
2. 通过公共 HTTPS URL 暴露您的 Speech Engine 服务器，例如使用 `ngrok http 3001` 进行本地开发。
3. 创建 Speech Engine 资源，`ws_url` / `wsUrl` 指向公共 WebSocket URL，通常是 `wss://.../ws`。
4. 将返回的 Speech Engine ID 存储在 `ELEVENLABS_SPEECH_ENGINE_ID` 中，例如。
5. 使用 Python 中的 `engine.serve(...)` 或 TypeScript 中的 `speechEngine.attach(...)` 启动 Speech Engine 服务器。
6. 从服务器端点发出浏览器对话令牌。永远不要在浏览器代码中放置 `ELEVENLABS_API_KEY`。
7. 使用 `conversationToken` 启动客户端会话；如果代理应首先问候，请在 Speech Engine 资源上启用首次消息覆盖，然后在客户端设置 `overrides.agent.firstMessage`。

## 创建 Speech Engine

### Python

```python
import asyncio
import os

from dotenv import load_dotenv
from elevenlabs import AsyncElevenLabs

load_dotenv()

elevenlabs = AsyncElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

async def main():
    engine = await elevenlabs.speech_engine.create(
        name="My Speech Engine",
        speech_engine={"ws_url": os.environ["PUBLIC_WS_URL"]},
        overrides={"first_message": True},
    )
    print(engine.engine_id)

asyncio.run(main())
```

### TypeScript

```typescript
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";
import "dotenv/config";

const elevenlabs = new ElevenLabsClient({
  apiKey: process.env.ELEVENLABS_API_KEY,
});

const engine = await elevenlabs.speechEngine.create({
  name: "My Speech Engine",
  speechEngine: { wsUrl: process.env.PUBLIC_WS_URL! },
  overrides: { firstMessage: true },
});

console.log(engine.engineId);
```

`PUBLIC_WS_URL` 应类似于本地 `wss://example.ngrok.app/ws` 或部署中的生产 WebSocket 路由。

创建请求还可以配置 `tts`、`asr`、`turn`、`speech_engine.request_headers` / `speechEngine.requestHeaders`、`overrides` 和 `privacy`，用于自定义语音、转录关键字、轮流发言、服务器认证标头、客户端提供的首次消息和录制行为。请参阅 SDK 参考文件以获取扩展示例。

## 服务器模式

在资源上配置的 `ws_url` / `wsUrl` 处运行 Speech Engine 服务器。将响应生成保留在您自己的验证边界之后：原始语音识别文本不应直接控制响应、工具、密钥或其他特权操作。

### Python

```python
engine = await elevenlabs.speech_engine.get(os.environ["ELEVENLABS_SPEECH_ENGINE_ID"])
await engine.serve(port=3001, path="/ws", debug=True, callbacks=validated_callbacks)
```

### TypeScript

```typescript
const engine = await elevenlabs.speechEngine.get(process.env.ELEVENLABS_SPEECH_ENGINE_ID!);
engine.attach(httpServer, "/ws", { debug: true, ...validatedCallbacks });
```

在 TypeScript 中，当下游异步工作支持取消时，将中断信号传递给下游异步工作，以便中断的响应能够快速停止。在 Python 中，SDK 在接收到新的轮次时取消先前的轮次处理程序。

服务器回调可以区分干净关闭和断开连接：使用 `onClose` / `on_close` 用于干净断开连接，使用 `onDisconnect` / `on_disconnect` 用于意外的 WebSocket 断开连接。

安全提示：语音识别文本可能包含来自用户语音或播放音频的提示注入尝试。将其视为不受信任的输入。在调用响应生成、工具或特权工作流之前，将其转换为受信任的应用状态。

### 禁用身份验证（高级、危险）

`engine.attach()`（TypeScript）和 `engine.serve()` / `SpeechEngineServer`（Python）默认情况下会对每个传入的 WebSocket 验证 JWT。这是证明连接确实来自 ElevenLabs 而不是攻击者猜测 URL 的方法。**不要关闭此功能。**

存在一个逃生通道——回调选项中的 `disableAuth: true`（TypeScript）或 `serve()` / `SpeechEngineServer(...)` 上的 `disable_auth=True`（Python）——用于狭窄的情况，其中已经存在补偿性网络级控制。如果没有这种控制，禁用身份验证意味着**互联网上任何找到您 URL 的客户端都可以打开会话**。具体来说，攻击者可以：

- 打开无限对话以耗尽您的 ElevenLabs 配额和下游 LLM 预算
- 将精心制作的转录文本输入您的响应管道，实际上模仿用户
- 使用您的服务器作为探查后端状态、工具或提示的预言机

仅在用户已经实现了**至少一个**以下情况时才建议 `disableAuth` / `disable_auth`：

- **IP 允许列表**——服务器（或上游防火墙 / 负载均衡器 / API 网关）仅接受来自 [ElevenLabs 文档的出站范围](https://elevenlabs.io/docs/overview/capabilities/speech-engine#ip-allowlisting) 的入站流量。
- **自定义共享密钥标头**——在创建时通过 `speech_engine.request_headers` / `speechEngine.requestHeaders` 配置在 Speech Engine 资源上的密钥标头，由上游代理（或开发者在 `attach()` / `serve()` 前面的自己的中间件）在请求到达 SDK 之前进行验证。

如果用户无法确认以上任一情况已到位，请保持默认身份验证开启。在没有缓解措施的情况下跳过 JWT 验证不是优化或便利——它是未经验证的全公开计算。

## 浏览器客户端

创建服务器端令牌端点，并在开始麦克风会话之前让浏览器请求令牌。将 Speech Engine ID 和 API 密钥保留在服务器上。如果客户端传递 `overrides.agent.firstMessage`，则 Speech Engine 资源必须启用首次消息覆盖。

```typescript
import express from "express";
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";
import "dotenv/config";

const app = express();
const elevenlabs = new ElevenLabsClient();

app.get("/api/token", async (_req, res) => {
  const response = await elevenlabs.conversationalAi.conversations.getWebrtcToken({
    agentId: process.env.ELEVENLABS_SPEECH_ENGINE_ID!,
  });
  res.json({ token: response.token });
});
```

React 客户端可以使用 `@elevenlabs/react`：

```tsx
import { useConversation } from "@elevenlabs/react";

export function VoiceControls() {
  const conversation = useConversation({
    onConnect: () => console.log("connected"),
    onDisconnect: () => console.log("disconnected"),
    onError: (error) => console.error(error),
  });

  async function startConversation() {
    await navigator.mediaDevices.getUserMedia({ audio: true });
    const { token } = await fetch("/api/token").then((res) => res.json());

    await conversation.startSession({
      conversationToken: token,
      overrides: {
        agent: { firstMessage: "Hello! How can I help you today?" },
      },
    });
  }

  return <button onClick={startConversation}>Start conversation</button>;
}
```

## 参考

- [安装指南](references/installation.md)
- [JavaScript SDK 参考](references/javascript-sdk-reference.md)
- [Python SDK 参考](references/python-sdk-reference.md)
