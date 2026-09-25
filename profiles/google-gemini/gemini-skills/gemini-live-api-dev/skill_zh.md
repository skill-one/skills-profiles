# Gemini Live API 开发技能

## 概述

Live API 能够通过 WebSockets 与 Gemini 进行低延迟、实时的语音和视频交互。它处理连续的音频、视频或文本流，以提供即时、类人的语音响应和背景推理。

主要功能：
- **双向音频流** — 实时麦克风到扬声器的对话
- **背景推理（扩展思考）** — 带有语音对话填充的多步骤背景推理
- **实时流字幕** — 实时语音转文本，带有中间和最终流
- **视频流** — 随音频发送相机/屏幕帧
- **文本输入/输出** — 在实时会话中发送和接收文本
- **音频字幕** — 获取输入和输出音频的文本字幕
- **语音活动检测 (VAD)** — 服务器端自动 VAD，客户端混合 VAD 和手动 Push-to-Talk
- **异步函数调用** — 音频继续流式传输时非阻塞工具执行
- **全会话客户端内容** — 在流中注入和更新对话回合
- **会话管理** — 上下文压缩、会话恢复、GoAway 信号
- **临时令牌** — 客户端端认证

> [!NOTE]
> Live API 通过 **WebSockets** 直接连接。如需 WebRTC 支持或简化集成，请使用 [合作伙伴集成](#partner-integrations)。

## 模型

### 当前模型（使用这些）

- `gemini-3.8-live` — 适用于大多数低延迟语音代理体验和实时对话（无推理延迟）。支持交错推理、默认异步函数调用（`behavior: NON_BLOCKING`）和全会话客户端内容更新。
- `gemini-3.8-live-extended-thinking` — 当实时交互需要更高背景推理时推荐的高推理音频到音频模型。在流式传输连续语音对话填充时处理背景推理和异步工具调用（需要 `behavior: NON_BLOCKING`）；通过 `interaction_status` (`IN_PROGRESS` vs `IDLE`) 管理生命周期。
- `gemini-3.5-transcribe-live` — 实时流语音转文本，带有中间假设、最终字幕、智能格式化和混合 VAD。
- `gemini-3.5-live-translate-preview` — 实时语音到语音流式传输翻译，支持 70 多种语言。

> [!WARNING]
> **旧版模型** (`gemini-3.1-flash-live-preview`, `gemini-2.5-flash-native-audio-*`, `gemini-live-2.5-flash-preview`, `gemini-2.0-flash-live-001`)：请参阅 [`references/migration.md`](references/migration.md) 了解协议变更（`behavior: "NON_BLOCKING"`, `thinking_level`, `interaction_status`, `send_client_content`）。

## SDKs

- **Python**: `google-genai` >= `2.3.0` — `pip install -U google-genai`
- **JavaScript/TypeScript**: `@google/genai` >= `2.3.0` — `npm install @google/genai`

> [!WARNING]
> 旧版 SDK `google-generativeai` (Python) 和 `@google/generative-ai` (JS) 已**弃用**。切勿使用它们。

## 合作伙伴集成

为简化实时音频/视频应用开发，使用支持 Gemini Live API 的第三方集成，通过 **WebRTC** 或 **WebSockets**：

- [LiveKit](https://docs.livekit.io/agents/models/realtime/plugins/gemini/) — 使用 LiveKit Agents 与 Gemini Live API 集成。
- [Pipecat by Daily](https://docs.pipecat.ai/guides/features/gemini-live) — 使用 Gemini Live 和 Pipecat 创建实时 AI 聊天机器人。
- [Fishjam by Software Mansion](https://docs.fishjam.io/tutorials/gemini-live-integration) — 使用 Fishjam 创建实时视频和音频流应用。
- [Vision Agents by Stream](https://visionagents.ai/integrations/gemini) — 使用 Vision Agents 构建实时语音和视频 AI 应用。
- [Voximplant](https://voximplant.com/products/gemini-client) — 使用 Voximplant 将入站和出站呼叫连接到 Live API。
- [Firebase AI SDK](https://firebase.google.com/docs/ai-logic/live-api?api=dev) — 使用 Firebase AI Logic 开始使用 Gemini Live API。

## 音频格式

- **输入**：原始 PCM，小端，16 位，单声道。原生 16kHz（将重采样其他频率）。MIME 类型：`audio/pcm;rate=16000`
- **输出**：原始 PCM，小端，16 位，单声道。24kHz 采样率。

> [!IMPORTANT]
> 使用 `send_realtime_input` / `sendRealtimeInput` 发送所有实时流式传输的用户输入（音频、视频、**和文本**）。在 Gemini 3.8 模型中，`send_client_content` / `sendClientContent` 支持全会话生命周期，带有显式角色（`user` 或 `model`）以注入对话上下文（`turn_complete=true` 无条件中断活动生成）。

> [!WARNING]
> **不要**在 `sendRealtimeInput` 中使用 `media`。使用特定键：`audio` 用于音频数据，`video` 用于图像/视频帧，`text` 用于文本输入。

---

## 快速入门

### 认证

#### Python

```python
from google import genai

client = genai.Client(api_key="YOUR_API_KEY")
```

#### JavaScript

```js
import { GoogleGenAI } from '@google/genai';

const ai = new GoogleGenAI({ apiKey: 'YOUR_API_KEY' });
```

### 连接到 Live API

#### Python
```python
from google.genai import types

config = types.LiveConnectConfig(
    response_modalities=[types.Modality.AUDIO],
    system_instruction=types.Content(
        parts=[types.Part(text="You are a helpful assistant.")]
    )
)

async with client.aio.live.connect(model="gemini-3.8-live", config=config) as session:
    pass  # 会话处于活动状态
```

#### JavaScript
```js
const session = await ai.live.connect({
  model: 'gemini-3.8-live',
  config: {
    responseModalities: ['audio'],
    systemInstruction: { parts: [{ text: 'You are a helpful assistant.' }] }
  },
  callbacks: {
    onopen: () => console.log('Connected'),
    onmessage: (response) => console.log('Message:', response),
    onerror: (error) => console.error('Error:', error),
    onclose: () => console.log('Closed')
  }
});
```

### 发送文本

#### Python
```python
await session.send_realtime_input(text="Hello, how are you?")
```

#### JavaScript
```js
session.sendRealtimeInput({ text: 'Hello, how are you?' });
```

### 发送音频

#### Python
```python
await session.send_realtime_input(
    audio=types.Blob(data=chunk, mime_type="audio/pcm;rate=16000")
)
```

#### JavaScript
```js
session.sendRealtimeInput({
  audio: { data: chunk.toString('base64'), mimeType: 'audio/pcm;rate=16000' }
});
```

### 发送视频

#### Python
```python
# frame: 原始 JPEG 编码的字节
await session.send_realtime_input(
    video=types.Blob(data=frame, mime_type="image/jpeg")
)
```

#### JavaScript
```js
session.sendRealtimeInput({
  video: { data: frame.toString('base64'), mimeType: 'image/jpeg' }
});
```

### 接收音频和文本

> [!IMPORTANT]
> 单个服务器事件可以同时包含**多个内容部分**（例如，音频块和字幕）。始终处理每个事件中的**所有**部分，以避免遗漏内容。

#### Python
```python
async for response in session.receive():
    content = response.server_content
    if content:
        # 音频 — 处理每个事件中的所有部分
        if content.model_turn:
            for part in content.model_turn.parts:
                if part.inline_data:
                    audio_data = part.inline_data.data
        # 字幕
        if content.input_transcription:
            print(f"用户: {content.input_transcription.text}")
        if content.output_transcription:
            print(f"Gemini: {content.output_transcription.text}")
        # 中断
        if content.interrupted is True:
            pass  # 停止播放，清空音频队列
```

#### JavaScript
```js
// 在 onmessage 回调中
const content = response.serverContent;
if (content?.modelTurn?.parts) {
  for (const part of content.modelTurn.parts) {
    if (part.inlineData) {
      const audioData = part.inlineData.data; // Base64 编码
    }
  }
}
if (content?.inputTranscription) console.log('用户:', content.inputTranscription.text);
if (content?.outputTranscription) console.log('Gemini:', content.outputTranscription.text);
if (content?.interrupted) { /* 停止播放，清空音频队列 */ }
```

---

## 背景推理（扩展思考）

当您的语音代理必须评估复杂数据、计划多步骤或处理长时间运行的工具时，使用 `gemini-3.8-live-extended-thinking`。模型在后台执行异步工具时说话自然对话填充（例如 *"正在检查航班选项..."*）。

主要要求：
- **思考配置**：设置 `thinking_config=types.ThinkingConfig(thinking_level="low")` (`"minimal"` | `"low"` | `"medium"` | `"high"`).
- **非阻塞工具**：所有函数声明**必须**设置 `behavior="NON_BLOCKING"`。同步阻塞模式不受支持，将返回错误。
- **生命周期跟踪 (`interaction_status`)**：不要仅依赖 `turn_complete=True` 来检测回合完成。监控 `message.interaction_status` (Python) / `message.interactionStatus` (JS):
  - `"IN_PROGRESS"`：服务器正在推理、说话对话填充或等待异步工具响应。
  - `"IDLE"`：服务器已完成所有背景推理和工具调用；会话准备好接收用户输入。

请参阅 [`references/migration.md`](references/migration.md) 和 [Live API 思考指南](https://ai.google.dev/gemini-api/docs/live-api/thinking.md.txt) 获取完整的 Python 和 JavaScript 实现示例。

---

## Live Translation (Gemini Live Translate)

Live API 支持跨 70 多种语言的实时、低延迟语音（音频）流式翻译。有关选项和功能的完整详细信息，请参阅 [Live Translation Guide](https://ai.google.dev/gemini-api/docs/live-api/live-translate.md.txt)。

### 模型
- `gemini-3.5-live-translate-preview` — 推荐的 Live Translation 翻译模型。

### 配置 (`TranslationConfig`)

要启用翻译，请在您的实时会话设置中指定 `TranslationConfig` 对象：

- **Python SDK**：使用 `LiveConnectConfig` 上的 `translation_config` 配置连接：
  ```python
  config = types.LiveConnectConfig(
      response_modalities=[types.Modality.AUDIO],
      translation_config=types.TranslationConfig(
          target_language_code="es",  # 目标语言代码（例如 es, fr, pl）
          echo_target_language=True,
      ),
      input_audio_transcription=types.AudioTranscriptionConfig(),
      output_audio_transcription=types.AudioTranscriptionConfig(),
  )
  ```
- **原始 WebSockets**：将 `translationConfig` 放在 `generationConfig` 中：
  ```json
  {
    "setup": {
      "model": "models/gemini-3.5-live-translate-preview",
      "generationConfig": {
        "responseModalities": ["AUDIO"],
        "translationConfig": {
          "targetLanguageCode": "es",
          "echoTargetLanguage": true
        }
      }
    }
  }
  ```

---

## Live Streaming Transcription (Gemini Live Transcribe)

Live API 支持通过 WebSockets 进行实时流式语音转文本，具有低延迟的中间假设、最终字幕和混合 VAD。有关完整详细信息，请参阅 [Live Transcription Guide](https://ai.google.dev/gemini-api/docs/live-api/live-transcribe.md.txt) 和 [Colab Cookbook](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started_transcribe.ipynb)。

### 模型
- `gemini-3.5-transcribe-live`

### 模式
- `smart`：清理填充词，解决内联自我纠正，并结构化格式。
- `verbatim`（默认）：逐字精确字幕。

### Python
```python
config = types.LiveConnectConfig(
    response_modalities=["TEXT"],
    input_audio_transcription=types.AudioTranscriptionConfig(),
)

async with client.aio.live.connect(model="gemini-3.5-transcribe-live", config=config) as session:
    # 流式传输音频
    await session.send_realtime_input(audio=types.Blob(data=chunk, mime_type="audio/pcm;rate=16000"))
    # 混合 VAD：在客户端检测到的静音时通知回合结束以实现零延迟
    await session.send_realtime_input(audio_stream_end=True)
```

### JavaScript
```javascript
const session = await ai.live.connect({
  model: 'gemini-3.5-transcribe-live',
  config: {
    responseModalities: ['text'],
    inputAudioTranscription: { mode: 'smart' }
  },
  callbacks: {
    onmessage: (msg) => {
      if (msg.serverContent?.interimInputTranscription) {
        console.log('Interim:', msg.serverContent.interimInputTranscription.text);
      }
      if (msg.serverContent?.inputTranscription) {
        console.log('Final:', msg.serverContent.inputTranscription.text);
      }
    }
  }
});

session.sendRealtimeInput({ audio: { data: chunkBase64, mimeType: 'audio/pcm;rate=16000' } });
session.sendRealtimeInput({ audioStreamEnd: true }); // 混合 VAD
```

### 原始 WebSockets
```json
{
  "setup": {
    "model": "models/gemini-3.5-transcribe-live",
    "generationConfig": {
      "responseModalities": ["TEXT"],
      "speechConfig": {
        "voiceConfig": {}
      }
    },
    "inputAudioTranscription": {
      "mode": "smart"
    }
  }
}
```

---

## 限制

- **响应模态** — 每个会话仅支持 `TEXT` **或** `AUDIO`，不支持两者。原生音频模型输出音频 (`response_modalities=["AUDIO"]`)；如需文本字幕，请启用 `output_audio_transcription`。
- **纯音频会话** — 无压缩 15 分钟
- **音频+视频会话** — 无压缩 2 分钟
- **连接生命周期** — ~10 分钟（使用会话恢复）
- **上下文窗口** — 128k 输入令牌 / 64k 输出令牌
- **代码执行 / URL 上下文** — 不支持

## 升级与迁移

从 `gemini-3.1-flash-live-preview`, `gemini-2.5-flash-native-audio-*` 或 `gemini-2.0-flash-live-001` 升级到 **Gemini 3.8 Live** 或 **Gemini 3.8 Live Extended Thinking** 的步骤迁移清单和协议差异，请参阅 [`references/migration.md`](references/migration.md)。

## 最佳实践

1. **测试麦克风音频时使用耳机**以防止回声/自我中断
2. **为超过 15 分钟的会话启用上下文窗口压缩**
3. **实现会话恢复**以优雅处理连接重置
4. **在客户端部署中使用临时令牌** — 不要在浏览器中暴露 API 密钥
5. **使用 `send_realtime_input`** 发送实时用户输入（音频、视频、文本）。使用 `send_client_content` 带有显式 `user`/`model` 角色，在流中注入上下文回合
6. **在麦克风暂停或用户完成说话时发送 `audioStreamEnd` / `audio_stream_end`**（混合 VAD）
7. **在收到中断信号时 (`interrupted: true`) 清空音频播放队列**
8. **处理每个服务器事件中的所有部分** — 事件可以包含多个内容部分
9. **使用 `gemini-3.8-live-extended-thinking` 时监控 `interaction_status`** (`IN_PROGRESS` vs `IDLE`)，而不是仅依赖 `turn_complete`

## 文档查找

### 当 MCP 安装时（首选）

如果 **`search_docs`** 工具（来自 Google MCP 服务器）可用，请将其作为您的**唯一**文档来源：

1. 使用您的查询调用 `search_docs`
2. 阅读返回的文档
3. **将 MCP 结果视为 API 详细信息的来源** — 它们始终是最新的。

> [!IMPORTANT]
> 当 MCP 工具存在时，**切勿**手动获取 URL。MCP 提供最新、索引的文档，比 URL 获取更准确、更高效。

### 当 MCP 未安装时（仅作为回退）

如果未提供 MCP 文档工具，则从官方文档索引获取：

**llms.txt URL**: `https://ai.google.dev/gemini-api/docs/llms.txt`

此索引包含所有 `.md.txt` 格式文档页面的链接。使用网络获取工具：

1. 获取 `llms.txt` 以发现可用的文档页面
2. 获取特定页面（例如，`https://ai.google.dev/gemini-api/docs/live-session.md.txt`）

### 关键文档页面

> [!IMPORTANT]
> 这些不是所有文档页面。使用 `llms.txt` 索引发现可用的文档页面

- [Live API 概述](https://ai.google.dev/gemini-api/docs/live.md.txt) — 入门、原始 WebSocket 使用
- [Live API 中的思考](https://ai.google.dev/gemini-api/docs/live-api/thinking.md.txt) — 背景推理、对话填充、`interaction_status`、非阻塞工具
- [Gemini 3.8 Live 模型卡](https://ai.google.dev/gemini-api/docs/models/gemini-3.8-live) — 默认低延迟语音代理模型 & 迁移指南
- [Gemini 3.8 Live Extended Thinking 模型卡](https://ai.google.dev/gemini-api/docs/models/gemini-3.8-live-extended-thinking) — 高推理语音模型 & 升级指南
- [Live Transcription](https://ai.google.dev/gemini-api/docs/live-api/live-transcribe.md.txt) — 实时语音转文本、中间假设、智能格式化、混合 VAD
- [Live Translate](https://ai.google.dev/gemini-api/docs/live-api/live-translate.md.txt) — 翻译配置选项和能力
- [Live API 功能指南](https://ai.google.dev/gemini-api/docs/live-guide.md.txt) — 语音配置、字幕配置、VAD 配置、媒体分辨率
- [Live API 工具使用](https://ai.google.dev/gemini-api/docs/live-tools.md.txt) — 同步和异步函数调用、Google 搜索接地
- [会话管理](https://ai.google.dev/gemini-api/docs/live-session.md.txt) — 上下文窗口压缩、会话恢复、GoAway 信号
- [临时令牌](https://ai.google.dev/gemini-api/docs/ephemeral-tokens.md.txt) — 浏览器/移动端的客户端端安全认证
- [WebSockets API 参考](https://ai.google.dev/api/live.md.txt) — 原始 WebSocket 协议详细信息
- [迁移与升级指南](references/migration.md) — Gemini 3.8 Live 和 Extended Thinking 的逐步检查清单和代码示例

## 支持的语言

Live API 支持 70 种语言，包括：英语、西班牙语、法语、德语、意大利语、葡萄牙语、中文、日语、韩语、印地语、阿拉伯语、俄语，以及更多。原生音频模型自动检测和切换语言。
