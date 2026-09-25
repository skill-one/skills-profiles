# ElevenLabs 语音转换器

将音频录音中的语音转换为不同的目标语音。语音转换器（以前称为语音到语音——API 端点和 SDK 方法仍然使用 `speech_to_speech` / `speechToSpeech` 名称）保留原始表现——情感、节奏、语调、呼吸、耳语、笑声、哭泣——仅交换说话者。

> **设置**：请参阅 [安装指南](references/installation.md)。对于 JavaScript，仅使用 `@elevenlabs/*` 包。

## 关键信息

- **最大输入长度**：每次请求 5 分钟——将较长的录音拆分为块并拼接输出。
- **最大文件大小**：每次请求 50 MB——如果源文件较大，请将其压缩为 MP3。
- **定价**：每分钟处理 1,000 个字符的音频（基于时长，而非文本）。
- **推荐模型**：`eleven_multilingual_sts_v2`——即使对于纯英文内容，通常也优于 `eleven_english_sts_v2`。

## 快速入门

### Python

```python
from elevenlabs import ElevenLabs

client = ElevenLabs()

with open("source.mp3", "rb") as audio_file:
    audio_stream = client.speech_to_speech.convert(
        voice_id="JBFqnCBsd6RMkjVDRZzb",  # George
        audio=audio_file,
        model_id="eleven_multilingual_sts_v2",
        output_format="mp3_44100_128",
    )

with open("converted.mp3", "wb") as f:
    for chunk in audio_stream:
        f.write(chunk)
```

### JavaScript

```javascript
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";
import { createReadStream, createWriteStream } from "fs";

const client = new ElevenLabsClient();

const audioStream = await client.speechToSpeech.convert("JBFqnCBsd6RMkjVDRZzb", {
  audio: createReadStream("source.mp3"),
  modelId: "eleven_multilingual_sts_v2",
  outputFormat: "mp3_44100_128",
});

audioStream.pipe(createWriteStream("converted.mp3"));
```

### CLI

```bash
elevenlabs speech-to-speech convert \
  --voice-id JBFqnCBsd6RMkjVDRZzb \
  --audio source.mp3 \
  --model-id eleven_multilingual_sts_v2 \
  --output-format mp3_44100_128 \
  --output converted.mp3
```

## 参数

| 参数 | 类型 | 默认值 | 描述 |
|-------|------|---------|-------------|
| `voice_id` | 字符串（必需） | — | 要使用的目标语音。使用预制的语音 ID、克隆的语音或库中的语音 |
| `audio` | 文件（必需） | — | 源音频，其表现（情感、时间、表达方式）将被保留 |
| `model_id` | 字符串 | `eleven_english_sts_v2` | `eleven_multilingual_sts_v2` 用于 29 种语言，`eleven_english_sts_v2` 用于纯英文 |
| `output_format` | 字符串 | `mp3_44100_128` | 下方输出格式表 |
| `voice_settings` | JSON 字符串 | — | 仅为此请求覆盖存储的语音设置 |
| `seed` | 整数 | — | 最佳努力确定性采样（0 – 4294967295） |
| `remove_background_noise` | 布尔值 | `false` | 在转换前对输入运行隔离模型 |
| `file_format` | 字符串 | `other` | `other` 用于任何编码的音频，或 `pcm_s16le_16` 用于 16 位 PCM 单声道 @ 16kHz 小端（低延迟） |
| `optimize_streaming_latency` | 整数（查询） | — | 0–4。以质量换取延迟。`4` 速度最快，但禁用文本标准化器 |
| `enable_logging` | 布尔值（查询） | `true` | 设置为 `false` 以实现零保留模式（仅限企业——禁用历史记录/拼接） |

## 模型

| 模型 ID | 语言 | 适用场景 |
|----------|-----------|----------|
| `eleven_multilingual_sts_v2` | 29 | 推荐用于所有场景——即使对于英文音频，通常也优于英文模型 |
| `eleven_english_sts_v2` | 英文 | API 默认——英文仅回退 |

仅当 `can_do_voice_conversion` 属性为 true 时才能使用这些模型。语音转换器目前没有低延迟的“快速/加速”层级——如果您需要，请保持 `pcm_s16le_16` 输入，`opus_*` / 低比特率 `mp3_*` 输出，并提高 `optimize_streaming_latency`。

### 语言 (`eleven_multilingual_sts_v2`)

英语（美国、英国、澳大利亚、加拿大）、日语、中文、德语、印地语、法语（法国、加拿大）、韩语、葡萄牙语（巴西、葡萄牙）、意大利语、西班牙语（西班牙、墨西哥）、印度尼西亚语、荷兰语、土耳其语、菲律宾语、波兰语、瑞典语、保加利亚语、罗马尼亚语、阿拉伯语（沙特阿拉伯、阿联酋）、捷克语、希腊语、芬兰语、克罗地亚语、马来语、斯洛伐克语、丹麦语、泰米尔语、乌克兰语、俄语。

## 目标语音

使用预制语音、您的克隆语音或语音库中的任何语音 ID。

**热门语音：**
- `JBFqnCBsd6RMkjVDRZzb` — George（男性，叙事）
- `EXAVITQu4vr4xnSDxMaL` — Sarah（女性，柔和）
- `onwK4e9ZLuTAKqWW03F9` — Daniel（男性，权威）
- `XB0fDUnXU5powFXDhCwa` — Charlotte（女性，对话）

```python
voices = client.voices.get_all()
for voice in voices.voices:
    print(f"{voice.voice_id}: {voice.name}")
```

## 从 URL 转换

```python
import requests
from io import BytesIO
from elevenlabs import ElevenLabs

client = ElevenLabs()

audio_url = "https://storage.googleapis.com/eleven-public-cdn/audio/marketing/nicole.mp3"
response = requests.get(audio_url)
audio_data = BytesIO(response.content)

audio_stream = client.speech_to_speech.convert(
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    audio=audio_data,
    model_id="eleven_multilingual_sts_v2",
    output_format="mp3_44100_128",
)

with open("converted.mp3", "wb") as f:
    for chunk in audio_stream:
        f.write(chunk)
```

## 语音设置覆盖

在不更改其存储默认值的情况下，对单个请求的目标语音进行微调：

```python
from elevenlabs import VoiceSettings

audio_stream = client.speech_to_speech.convert(
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    audio=audio_file,
    model_id="eleven_multilingual_sts_v2",
    voice_settings=VoiceSettings(
        stability=0.5,
        similarity_boost=0.75,
        style=0.0,
        use_speaker_boost=True,
    ),
)
```

- **稳定性**：较低 = 更多的情感范围（更自由地跟随源），较高 = 更稳定的表达。
- **相似度提升**：较高 = 更接近目标语音的音色，可能会放大源音频伪影。
- **风格**：夸张目标语音的独特特征（v2+ 模型）。
- **说话者增强**：后处理以增强目标语音的清晰度。

## 清理嘈杂的源音频

如果输入录音嘈杂，请使用语音隔离技能预处理，或在单个调用中传递 `remove_background_noise=True`：

```python
audio_stream = client.speech_to_speech.convert(
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    audio=audio_file,
    model_id="eleven_multilingual_sts_v2",
    remove_background_noise=True,
)
```

更干净的输入几乎总是能产生更好的转换——模型试图匹配音素和韵律，而背景噪音会干扰。

## 低延迟 PCM 输入

如果您已有原始 16 位 PCM 单声道 @ 16kHz，传递 `file_format="pcm_s16le_16"` 可跳过解码并减少延迟：

```python
audio_stream = client.speech_to_speech.convert(
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    audio=pcm_bytes,
    model_id="eleven_multilingual_sts_v2",
    file_format="pcm_s16le_16",
)
```

将此与 `optimize_streaming_latency`（0–4）作为查询参数结合使用，以进一步降低延迟，但会牺牲一些质量。

## 输出格式

| 格式 | 描述 |
|--------|-------------|
| `mp3_44100_128` | MP3 44.1kHz 128kbps（默认）——适用于网页/应用 |
| `mp3_44100_192` | MP3 44.1kHz 192kbps（创作者+）——更高质量 |
| `mp3_44100_64` | MP3 44.1kHz 64kbps——更小的文件 |
| `mp3_22050_32` | MP3 22.05kHz 32kbps——最小的 MP3 |
| `pcm_16000` | 原始 PCM 16kHz——实时管道 |
| `pcm_24000` | 原始 PCM 24kHz——良好的流媒体平衡 |
| `pcm_44100` | 原始 PCM 44.1kHz（专业+）——CD 质量 |
| `pcm_48000` | 原始 PCM 48kHz（专业+）——最高质量 |
| `ulaw_8000` | μ-law 8kHz——Twilio / 电信 |
| `alaw_8000` | A-law 8kHz——电信 |
| `opus_48000_64` | Opus 48kHz 64kbps——高效的流媒体 |

## 确定性输出

传递一个 `seed` 以使相同输入的重复转换返回（最佳努力）相同的音频——适用于测试和 A/B 比较。

```python
audio_stream = client.speech_to_speech.convert(
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    audio=audio_file,
    model_id="eleven_multilingual_sts_v2",
    seed=12345,
)
```

## 输入音频最佳实践

转换质量受限于输入录音——模型只能交换音色，无法挽救糟糕的源。一些实用规则：

- **表达要丰富。** 耳语、喊叫、大笑、哭泣——模型保留所有这些。平淡的输入会得到平淡的输出。
- **注意麦克风增益。** 太安静会导致模型无法检测音素；太响会导致削波混入转换中。目标是健康的峰值，无削波。
- **口音和节奏从源而非目标转移。** 如果您用美国口音朗读并目标“George”语音，您会得到 George 的音色和美国的口音。要为不同的口音或语言配音，请让目标口音/语言的人说话，然后转换为克隆/库语音。
- **先清理噪音。** 要么传递 `remove_background_noise=True`，要么在转换前将源通过语音隔离技能处理。噪音在这里比在 TTS 中影响更大。
- **拆分长录音。** 任何超过 5 分钟的录音都必须分块。在自然停顿处剪切，转换每一部分，然后连接生成的音频。

## 常见工作流程

- **重新配音旁白**——保留草稿录音的表现，替换为不同的解说员语音。
- **本地化/配音**——将配音转换为同一解说员克隆语音的另一种语言（使用 `eleven_multilingual_sts_v2`）。
- **创建角色语音**——自己表演一句话，转换为独特的角色语音用于游戏或动画。
- **匿名化说话者**——用中性的预制语音替换可识别的语音，同时保留所说内容和表达方式。
- **与语音隔离器配合使用**——在转换前先隔离源语音（或设置 `remove_background_noise=True）用于嘈杂的现场录音。
- **与语音克隆配合使用**——从短样本克隆目标语音，然后在此处使用其 `voice_id` 作为转换目标。

## 错误处理

```python
try:
    audio_stream = client.speech_to_speech.convert(
        voice_id="JBFqnCBsd6RMkjVDRZzb",
        audio=audio_file,
        model_id="eleven_multilingual_sts_v2",
    )
except Exception as e:
    print(f"语音转换失败：{e}")
```

常见错误：
- **401**：无效的 API 密钥
- **422**：无效参数（检查 `voice_id`、`model_id` 或 `file_format` 与提供的音频）
- **429**：速率限制超出

## 参考

- [安装指南](references/installation.md)
