# ElevenLabs 音效

根据文本描述生成音效 — 支持循环、自定义时长和提示词遵循控制。

> **设置：** 请参阅 [安装指南](references/installation.md)。对于 JavaScript，仅使用 `@elevenlabs/*` 包。

## 快速入门

### Python

```python
from elevenlabs import ElevenLabs

client = ElevenLabs()

audio = client.text_to_sound_effects.convert(
    text="远处雷声隆隆伴随小雨",
)

with open("thunder.mp3", "wb") as f:
    for chunk in audio:
        f.write(chunk)
```

### JavaScript

```javascript
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";
import { createWriteStream } from "fs";

const client = new ElevenLabsClient();
const audio = await client.textToSoundEffects.convert({
  text: "远处雷声隆隆伴随小雨",
});
audio.pipe(createWriteStream("thunder.mp3"));
```

### CLI

```bash
elevenlabs text-to-sound-effects convert \
  --text "远处雷声隆隆伴随小雨" \
  --output thunder.mp3
```

## 参数

| 参数 | 类型 | 默认值 | 描述 |
|-----------|------|---------|-------------|
| `text` | 字符串（必填） | — | 所需音效的描述 |
| `model_id` | 字符串 | `eleven_text_to_sound_v2` | 使用的模型 |
| `duration_seconds` | 数字 \| null | null（自动） | 时长 0.5–30s；若为 null 则自动计算 |
| `prompt_influence` | 数字 \| null | 0.3 | 提示词遵循程度（0–1） |
| `loop` | 布尔值 | false | 生成无缝循环的音效（仅限 v2 模型） |

## 带参数的示例

```python
# 循环环境音效，10 秒
audio = client.text_to_sound_effects.convert(
    text="轻柔的森林氛围伴随鸟鸣",
    duration_seconds=10.0,
    prompt_influence=0.5,
    loop=True,
)

# 短 UI 音效，高提示词遵循度
audio = client.text_to_sound_effects.convert(
    text="柔和的通知提示音",
    duration_seconds=1.0,
    prompt_influence=0.8,
)
```

## 输出格式

通过 `--output-format`（CLI）或作为 SDK 参数传递 `output_format`：

| 格式 | 描述 |
|--------|-------------|
| `mp3_44100_128` | MP3 44.1kHz 128kbps（默认） |
| `pcm_44100` | 未压缩的 CD 音质原始数据 |
| `opus_48000_128` | Opus 48kHz 128kbps — 高效压缩 |
| `ulaw_8000` | μ-law 8kHz — 电话音质 |

完整列表：`mp3_22050_32`, `mp3_24000_48`, `mp3_44100_32`, `mp3_44100_64`, `mp3_44100_96`, `mp3_44100_128`, `mp3_44100_192`, `pcm_8000`, `pcm_16000`, `pcm_22050`, `pcm_24000`, `pcm_32000`, `pcm_44100`, `pcm_48000`, `ulaw_8000`, `alaw_8000`, `opus_48000_32`, `opus_48000_64`, `opus_48000_96`, `opus_48000_128`, `opus_48000_192`。

## 提示词技巧

- 具体描述： "雨点敲击锡屋顶" > "雨"
- 组合元素： "碎石路上的脚步声伴随远处车流"
- 指定风格： "电影感 braam 音效，恐怖" 或 "8 位复古跳跃音"
- 提及情绪/背景： "荒废建筑中呼啸的诡异风声"

## 错误处理

```python
try:
    audio = client.text_to_sound_effects.convert(text="爆炸声")
except Exception as e:
    print(f"API 错误：{e}")
```

常见错误：
- **401**：无效的 API 密钥
- **422**：无效参数（检查时长范围、提示词遵循度范围）
- **429**：速率限制超出

## 参考

- [安装指南](references/installation.md)
