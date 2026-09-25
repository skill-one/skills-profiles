# ElevenLabs 音频隔离器

从音频中去除背景噪音并隔离人声/语音——适用于清理嘈杂录音、为转录准备音频或从混音轨道中提取对话。

> **设置：** 请参阅 [安装指南](references/installation.md)。对于 JavaScript，仅使用 `@elevenlabs/*` 包。

## 快速入门

### Python

```python
from elevenlabs import ElevenLabs

client = ElevenLabs()

with open("noisy.mp3", "rb") as audio_file:
    audio_stream = client.audio_isolation.convert(audio=audio_file)

with open("clean.mp3", "wb") as f:
    for chunk in audio_stream:
        f.write(chunk)
```

### JavaScript

```javascript
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";
import { createReadStream, createWriteStream } from "fs";

const client = new ElevenLabsClient();

const audioStream = await client.audioIsolation.convert({
  audio: createReadStream("noisy.mp3"),
});

audioStream.pipe(createWriteStream("clean.mp3"));
```

### CLI

```bash
elevenlabs audio-isolation convert --audio noisy.mp3 --output clean.mp3
```

## 参数

| 参数 | 类型 | 默认值 | 描述 |
|-----------|------|---------|-------------|
| `audio` | 文件 (必填) | — | 包含人声/语音的音频文件，用于隔离 |
| `file_format` | 字符串 | `other` | `other` 用于任何编码的音频，或 `pcm_s16le_16` 用于 16 位 PCM 单声道 @ 16kHz 小端序 (低延迟) |

## 从 URL 隔离

```python
import requests
from io import BytesIO
from elevenlabs import ElevenLabs

client = ElevenLabs()

audio_url = "https://example.com/noisy.mp3"
response = requests.get(audio_url)
audio_data = BytesIO(response.content)

audio_stream = client.audio_isolation.convert(audio=audio_data)

with open("clean.mp3", "wb") as f:
    for chunk in audio_stream:
        f.write(chunk)
```

## 低延迟 PCM 输入

如果你已经有原始 16 位 PCM 单声道 @ 16kHz，传递 `file_format="pcm_s16le_16"` 可以跳过解码并减少延迟：

```python
audio_stream = client.audio_isolation.convert(
    audio=pcm_bytes,
    file_format="pcm_s16le_16",
)
```

## 支持的格式

任何常见的编码音频/视频容器都可以作为输入 (MP3, WAV, M4A, FLAC, OGG, WebM, MP4 等)。默认响应为流式 MP3。

## 常见工作流程

- **清理采访/播客录音** — 编辑前去除房间噪音、暖通空调噪音、交通噪音。
- **为语音转文本准备嘈杂音频** — 首先隔离人声，然后通过 `speech_to_text.convert()` 以获得更好的转录准确性。
- **从混音轨道中提取对话** — 从包含音乐/SFX 的轨道中提取人声。
- **语音转换预处理** — 在应用语音转换之前隔离源语音。

## 错误处理

```python
try:
    audio_stream = client.audio_isolation.convert(audio=audio_file)
except Exception as e:
    print(f"语音隔离失败: {e}")
```

常见错误：
- **401**: 无效的 API 密钥
- **422**: 无效的参数 (例如，提供的音频的 `file_format` 错误)
- **429**: 超出速率限制

## 参考

- [安装指南](references/installation.md)
