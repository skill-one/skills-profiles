# ElevenLabs 语音转文本

使用 Scribe v2 将音频转录为文本 - 支持 90 多种语言、说话人分割和单词级时间戳。

> **设置：** 请参阅 [安装指南](references/installation.md)。对于 JavaScript，仅使用 `@elevenlabs/*` 包。

## 快速入门

### Python

```python
from elevenlabs import ElevenLabs

client = ElevenLabs()

with open("audio.mp3", "rb") as audio_file:
    result = client.speech_to_text.convert(file=audio_file, model_id="scribe_v2")

print(result.text)
```

### JavaScript

```javascript
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";
import { createReadStream } from "fs";

const client = new ElevenLabsClient();
const result = await client.speechToText.convert({
  file: createReadStream("audio.mp3"),
  modelId: "scribe_v2",
});
console.log(result.text);
```

### 命令行

```bash
elevenlabs speech-to-text convert --file audio.mp3 --model-id scribe_v2
```

## 模型

| 模型 ID | 描述 | 适用于 |
|----------|-------------|----------|
| `scribe_v2` | 最先进的准确性，90 多种语言 | 批量转录、字幕、长格式音频 |
| `scribe_v2_realtime` | 低延迟 (~150ms) | 实时转录、语音代理 |
| `scribe_v2_realtime_turbo` | 实时转录变体 | 实时转录 |
| `scribe_v2_realtime_lite` | 实时转录变体 | 实时转录 |

## 带时间戳的转录

单词级时间戳包括类型分类和说话人识别：

```python
result = client.speech_to_text.convert(
    file=audio_file, model_id="scribe_v2", timestamps_granularity="word"
)

for word in result.words:
    print(f"{word.text}: {word.start}s - {word.end}s (类型: {word.type})")

```

## 说话人分割

识别谁说了什么 - 模型为每个单词标记说话人 ID，适用于会议、采访或任何多说话人音频：

```python
result = client.speech_to_text.convert(
    file=audio_file,
    model_id="scribe_v2",
    diarize=True
)

for word in result.words:
    print(f"[{word.speaker_id}] {word.text}")
```

对于通话录音，批量 API 可以通过设置 `detect_speaker_roles=true`（同时设置 `diarize=true`）将分割的说话人标记为 `agent` 和 `customer`。此选项与 `use_multi_channel=true` 不兼容。

如果您的工具有注册的说话人配置文件，请使用 `use_speaker_library=true`（同时设置 `diarize=true`）将检测到的说话人与说话人库进行匹配。

```bash
elevenlabs speech-to-text convert \
  --file call.mp3 \
  --model-id scribe_v2 \
  --diarize true \
  --detect-speaker-roles true \
  --use-speaker-library true
```

## 多通道音频

当每个说话人隔离在单独的音频通道上时，使用 `use_multi_channel=true`。默认情况下，API 按通道返回一个转录文本（在 `transcripts` 下）；设置 `multichannel_output_style="combined"` 以接收按时间戳合并的一个转录文本，并在每个单词上显示 `channel_index`。

```python
result = client.speech_to_text.convert(
    file=audio_file,
    model_id="scribe_v2",
    use_multi_channel=True,
    multichannel_output_style="combined",
)
```

## 关键词提示

帮助模型识别它可能误听的具体单词 - 产品名称、技术术语或不寻常的拼写（最多 100 个术语）：

```python
result = client.speech_to_text.convert(
    file=audio_file,
    model_id="scribe_v2",
    keyterms=["ElevenLabs", "Scribe", "API"]
)
```

## 语言检测

自动检测，可选语言提示：

```python
result = client.speech_to_text.convert(
    file=audio_file,
    model_id="scribe_v2",
    language_code="eng"  # ISO 639-1 或 ISO 639-3 代码
)

print(f"检测到: {result.language_code} ({result.language_probability:.0%})")
```

## 支持的格式

**音频：** MP3、WAV、M4A、FLAC、OGG、WebM、AAC、AIFF、Opus
**视频：** MP4、AVI、MKV、MOV、WMV、FLV、WebM、MPEG、3GPP

**限制：** 文件大小最多 5.0GB，持续时间最长 10 小时

## 响应格式

```json
{
  "text": "完整的转录文本",
  "language_code": "eng",
  "language_probability": 0.98,
  "words": [
    {"text": "The", "start": 0.0, "end": 0.15, "type": "word", "speaker_id": "speaker_0"},
    {"text": " ", "start": 0.15, "end": 0.16, "type": "spacing", "speaker_id": "speaker_0"}
  ]
}
```

**单词类型：**
- `word` - 实际说出的单词
- `spacing` - 单词之间的空白（用于精确计时）
- `audio_event` - 模型检测到的非语音声音（笑声、掌声、音乐等）

## 错误处理

```python
try:
    result = client.speech_to_text.convert(file=audio_file, model_id="scribe_v2")
except Exception as e:
    print(f"转录失败: {e}")
```

常见错误：
- **401**：无效的 API 密钥
- **422**：无效的参数
- **429**：超出速率限制

## 跟踪成本

通过 `request-id` 响应头监控使用情况：

```python
response = client.speech_to_text.with_raw_response.convert(file=audio_file, model_id="scribe_v2")
result = response.data
print(f"请求 ID: {response.headers.get('request-id')}")
```

## 实时流式传输

对于超低延迟 (~150ms) 的实时转录，请使用实时 API。实时 API 生成两种类型的转录：

- **部分转录**：音频处理过程中频繁更新的中间结果 - 用于实时反馈（例如，在用户说话时显示文本）
- **已提交转录**：在您“提交”后稳定的最终结果 - 作为应用程序的真相来源使用

“提交”告诉模型最终当前片段。您可以手动提交（例如，当用户暂停时）或使用语音活动检测 (VAD) 在静音时自动提交。

### Python（服务器端）

```python
import asyncio
from elevenlabs import ElevenLabs

client = ElevenLabs()

async def transcribe_realtime():
    async with client.speech_to_text.realtime.connect(
        model_id="scribe_v2_realtime",
        include_timestamps=True,
        keyterms=["ElevenLabs", "Scribe"],
        no_verbatim=True,
    ) as connection:
        await connection.stream_url("https://example.com/audio.mp3")

        async for event in connection:
            if event.type == "partial_transcript":
                print(f"部分: {event.text}")
            elif event.type == "committed_transcript":
                print(f"最终: {event.text}")

asyncio.run(transcribe_realtime())
```

### JavaScript（客户端，使用 React）

```typescript
import { useScribe, CommitStrategy } from "@elevenlabs/react";

function TranscriptionComponent() {
  const [transcript, setTranscript] = useState("");

  const scribe = useScribe({
    modelId: "scribe_v2_realtime",
    commitStrategy: CommitStrategy.VAD, // 在麦克风输入时自动提交
    keyterms: ["ElevenLabs", "Scribe"],
    noVerbatim: true,
    includeLanguageDetection: true,
    onPartialTranscript: (data) => console.log("部分:", data.text),
    onCommittedTranscript: (data) => setTranscript((prev) => prev + data.text),
  });

  const start = async () => {
    // 从后端获取 token（切勿将 API 密钥暴露给客户端）
    const { token } = await fetch("/scribe-token").then((r) => r.json());

    await scribe.connect({
      token,
      microphone: { echoCancellation: true, noiseSuppression: true },
    });
  };

  return <button onClick={start}>开始录音</button>;
}
```

### 提交策略

| 策略 | 描述 |
|----------|-------------|
| **手动** | 当您准备好时调用 `commit()` - 用于文件处理或当您控制音频片段时 |
| **VAD** | 语音活动检测在检测到静音时自动提交 - 用于实时麦克风输入 |

设置 `includeLanguageDetection: true` 以在延迟的最终转录事件中接收检测到的语言代码。

```typescript
// React: 在钩子上设置 commitStrategy（推荐用于麦克风输入）
import { useScribe, CommitStrategy } from "@elevenlabs/react";

const scribe = useScribe({
  modelId: "scribe_v2_realtime",
  commitStrategy: CommitStrategy.VAD,
  keyterms: ["ElevenLabs", "Scribe"],
  noVerbatim: true,
  // 可选的 VAD 调整：
  vadSilenceThresholdSecs: 1.5,
  vadThreshold: 0.4,
});
```

```javascript
// JavaScript 客户端：在连接时传递 VAD 配置
const connection = await client.speechToText.realtime.connect({
  modelId: "scribe_v2_realtime",
  keyterms: ["ElevenLabs", "Scribe"],
  noVerbatim: true,
  vad: {
    silenceThresholdSecs: 1.5,
    threshold: 0.4,
  },
});
```

### 事件类型

| 事件 | 描述 |
|-------|-------------|
| `partial_transcript` | 实时中间结果 |
| `final_transcript` | 在片段提交之前发送的稳定片段结果 |
| `final_transcript_with_timestamps` | 延迟的最终结果，带时间戳和/或检测到的语言 |
| `committed_transcript` | 提交后的最终结果 |
| `committed_transcript_with_timestamps` | 带单词计时的最终结果 |
| `committed_transcript_entities` | 已提交片段中检测到的实体 |
| `invalid_request` | 连接参数被拒绝，会话关闭 |
| `error` | 发生错误 |

请参阅实时参考文档以获取完整信息。

## 参考

- [安装指南](references/installation.md)
- [转录选项](references/transcription-options.md)
- [实时客户端流式传输](references/realtime-client-side.md)
- [实时服务器端流式传输](references/realtime-server-side.md)
- [提交策略](references/realtime-commit-strategies.md)
- [实时事件参考](references/realtime-events.md)
