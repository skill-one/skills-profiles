# ElevenLabs 文本转语音

从文本生成自然语音 - 支持 70 多种语言，提供多种模型以在音质和延迟之间进行权衡。

> **设置：** 请参阅 [安装指南](references/installation.md)。对于 JavaScript，仅使用 `@elevenlabs/*` 包。

## 快速入门

### Python

```python
from elevenlabs import ElevenLabs

client = ElevenLabs()

audio = client.text_to_speech.convert(
    text="你好，欢迎来到 ElevenLabs！",
    voice_id="JBFqnCBsd6RMkjVDRZzb",  # George
    model_id="eleven_multilingual_v2"
)

with open("output.mp3", "wb") as f:
    for chunk in audio:
        f.write(chunk)
```

### JavaScript

```javascript
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";
import { createWriteStream } from "fs";
import { Readable } from "stream";

const client = new ElevenLabsClient();
const audio = await client.textToSpeech.convert("JBFqnCBsd6RMkjVDRZzb", {
  text: "你好，欢迎来到 ElevenLabs！",
  modelId: "eleven_multilingual_v2",
});
// convert() 返回一个 web ReadableStream — 将其桥接到 Node 流以写入磁盘
Readable.fromWeb(audio).pipe(createWriteStream("output.mp3"));
```

### 命令行

使用 `say` 立即播放文本，并使用默认语音和 `eleven_v3` 模型：

```bash
elevenlabs say "你好！"
```

当另一个命令生成输入时，将文本管道输入到 `say`：

```bash
echo "构建成功完成。" | elevenlabs say
```

当您需要直接设置请求参数时，使用 API 命令：

```bash
elevenlabs text-to-speech convert --voice-id JBFqnCBsd6RMkjVDRZzb \
  --text "你好！" --model-id eleven_multilingual_v2 --output output.mp3
```

命令行会自动从环境变量中读取 `ELEVENLABS_API_KEY`。

## 模型

| 模型 ID | 语言 | 延迟 | 适用于 |
|----------|-----------|---------|----------|
| `eleven_v3` | 70+ | 标准 | 最高音质，情感范围 |
| `eleven_multilingual_v2` | 29 | 标准 | 高音质，长文本内容 |
| `eleven_flash_v2_5` | 32 | ~75ms | 超低延迟，实时 |
| `eleven_flash_v2` | 英语 | ~75ms | 仅英语，最快 |
| `eleven_turbo_v2_5` | 32 | ~250-300ms | 音质/速度平衡 |
| `eleven_turbo_v2` | 英语 | ~250-300ms | 仅英语，平衡 |

## 语音 ID

使用预制的语音或在控制面板中创建自定义语音。

**热门语音：**
- `JBFqnCBsd6RMkjVDRZzb` - George（男性，叙事）
- `EXAVITQu4vr4xnSDxMaL` - Sarah（女性，柔和）
- `onwK4e9ZLuTAKqWW03F9` - Daniel（男性，权威）
- `XB0fDUnXU5powFXDhCwa` - Charlotte（女性，对话）

```python
voices = client.voices.get_all()
for voice in voices.voices:
    print(f"{voice.voice_id}: {voice.name}")
```

## 语音设置

微调语音的音效：

- **稳定性**：语音保持一致的程度。较低值 = 更多的情感范围和变化，但可能听起来不稳定。较高值 = 稳定、可预测的输出。
- **相似度增强**：与原始语音样本匹配的紧密程度。较高值听起来更像原始语音，但可能会放大音频伪影。
- **风格**：夸张语音的独特风格特征（仅适用于 v2+ 模型）。
- **说话者增强**：后处理，增强清晰度和语音相似度。

```python
from elevenlabs import VoiceSettings

audio = client.text_to_speech.convert(
    text="自定义我的语音设置。",
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    voice_settings=VoiceSettings(
        stability=0.5,
        similarity_boost=0.75,
        style=0.5,
        speed=1.0,             # 0.25 到 4.0（默认 1.0）
        use_speaker_boost=True
    )
)
```

## 语言选择

使用 `language_code` 与支持语言强制的模型一起使用，以指导发音和文本规范化。不支持的语言代码将被忽略，并且 `eleven_multilingual_v2` 不支持 `language_code`。

```python
audio = client.text_to_speech.convert(
    text="Bonjour, comment allez-vous?",
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    model_id="eleven_v3",
    language_code="fr"  # ISO 639-1 代码
)
```

## 文本规范化

控制数字、日期和缩写的转换方式，例如 "01/15/2026" 变成 "January fifteenth, twenty twenty-six"：

- `"auto"`（默认）：模型根据上下文决定
- `"on"`：始终规范化（当您希望自然语音时使用）
- `"off"`：逐字发音（当您希望 "zero one slash one five..." 时使用）

```python
audio = client.text_to_speech.convert(
    text="Call 1-800-555-0123 on 01/15/2026",
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    apply_text_normalization="on"
)
```

## 请求拼接

当在多个请求中生成长音频时，音频在边界处可能会有爆音、不自然的停顿或音调变化。请求拼接通过让每个请求知道它之前/之后的内容来解决这个问题：

```python
# 第一个请求
audio1 = client.text_to_speech.convert(
    text="这是第一部分。",
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    next_text="这继续了故事。"
)

# 使用先前上下文的第二个请求
audio2 = client.text_to_speech.convert(
    text="这继续了故事。",
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    previous_text="这是第一部分。"
)
```

## 输出格式

| 格式 | 描述 |
|--------|-------------|
| `mp3_44100_128` | MP3 44.1kHz 128kbps（默认）- 压缩，适用于网络/应用程序 |
| `mp3_44100_192` | MP3 44.1kHz 192kbps（Creator+）- 更高质量的压缩 |
| `mp3_44100_64` | MP3 44.1kHz 64kbps - 较低质量，文件较小 |
| `mp3_22050_32` | MP3 22.05kHz 32kbps - 最小的 MP3 文件 |
| `pcm_16000` | 原始 PCM 16kHz - 用于实时处理 |
| `pcm_22050` | 原始 PCM 22.05kHz |
| `pcm_24000` | 原始 PCM 24kHz - 适用于流媒体的良好平衡 |
| `pcm_44100` | 原始 PCM 44.1kHz（Pro+）- CD 质量 |
| `pcm_48000` | 原始 PCM 48kHz（Pro+）- 最高质量 |
| `ulaw_8000` | μ-law 8kHz - 电话系统标准（Twilio，电话） |
| `alaw_8000` | A-law 8kHz - 电话（μ-law 的替代方案） |
| `opus_48000_64` | Opus 48kHz 64kbps - 高效流媒体编解码器 |
| `wav_44100` | WAV 44.1kHz - 带头部的未压缩 |

## 流式传输

对于实时应用程序，使用 `stream` 方法（返回生成的音频块）：

```python
audio_stream = client.text_to_speech.stream(
    text="这段文本将作为音频流式传输。",
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    model_id="eleven_flash_v2_5"  # 超低延迟
)

for chunk in audio_stream:
    play_audio(chunk)
```

有关 WebSocket 流式传输，请参阅 [references/streaming.md](references/streaming.md)。

## 错误处理

```python
try:
    audio = client.text_to_speech.convert(
        text="生成语音",
        voice_id="无效的语音 ID"
    )
except Exception as e:
    print(f"API 错误：{e}")
```

常见错误：
- **401**：无效的 API 密钥
- **422**：无效参数（检查 voice_id, model_id）
- **429**：速率限制超出

## 跟踪成本

通过响应头 (`x-character-count`, `request-id`) 监控字符使用情况：

```python
response = client.text_to_speech.convert.with_raw_response(
    text="你好！", voice_id="JBFqnCBsd6RMkjVDRZzb", model_id="eleven_multilingual_v2"
)
audio = response.parse()
print(f"使用的字符数：{response.headers.get('x-character-count')}")
```

## 参考

- [安装指南](references/installation.md)
- [流式音频](references/streaming.md)
- [语音设置](references/voice-settings.md)
