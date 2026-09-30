---
name: tts
description: 当用户希望将文本转换为语音、从文本生成音频或制作旁白时，请使用此技能。触发条件包括：提及“TTS”、“文本转语音”、“说话”、“说出”、“语音”、“朗读”、“音频旁白”、“配音”、“配音”或要求将书面内容转换为语音音频的请求。此外，在将EPUB/PDF/SRT/文章转换为音频、从参考音频克隆声音、控制语音的情感或速度、将语音与字幕时间轴对齐或生成分段映射音频时，也请使用此技能。
---

# 语音合成

将任意文本转换为语音音频。支持两种后端（Kokoro 本地，Noiz 云端），两种模式（简单或时间轴精确），以及每段语音的独立控制。

## 触发词

- 文本转语音 / tts / 说话 / 讲
- 语音克隆 / 配音
- 电子书转音频 / 字幕转音频 / 转换为音频
- 语音 / 说 / 讲 / 说话

## 简易模式 — 文本转音频

`speak` 是默认命令 — 子命令可以省略：

```bash
# 基本用法（speak 是隐含的）
python3 skills/tts/scripts/tts.py -t "Hello world"          # 添加 -o 路径保存
python3 skills/tts/scripts/tts.py -f article.txt -o out.mp3

# 语音克隆 — 本地文件路径或 URL
python3 skills/tts/scripts/tts.py -t "Hello" --ref-audio ./ref.wav
python3 skills/tts/scripts/tts.py -t "Hello" --ref-audio https://example.com/my_voice.wav -o clone.wav

# 语音消息格式
python3 skills/tts/scripts/tts.py -t "Hello" --format opus -o voice.opus
python3 skills/tts/scripts/tts.py -t "Hello" --format ogg -o voice.ogg
```

第三方集成（飞书/Telegram/Discord）的文档请参考 [ref_3rd_party.md](ref_3rd_party.md)。

## 时间轴模式 — 字幕转时间对齐音频

用于精确的每段语音时间控制（配音、字幕、视频旁白）。

### 第一步：获取或创建字幕文件

如果用户没有字幕文件，可以从文本生成：

```bash
python3 skills/tts/scripts/tts.py to-srt -i article.txt -o article.srt
python3 skills/tts/scripts/tts.py to-srt -i article.txt -o article.srt --cps 15 --gap 500
```

`--cps` = 每秒字符数（默认 4，适合中文；~15 适合英文）。代理也可以手动编写字幕。

### 第二步：创建语音映射文件

JSON 文件控制默认及每段语音的设置。`segments` 键支持单个索引 `"3"` 或范围 `"5-8"`。

Kokoro 语音映射文件：

```json
{
  "default": { "voice": "zf_xiaoni", "lang": "cmn" },
  "segments": {
    "1": { "voice": "zm_yunxi" },
    "5-8": { "voice": "af_sarah", "lang": "en-us", "speed": 0.9 }
  }
}
```

Noiz 语音映射文件（支持 `emo`，`reference_audio`）。`reference_audio` 可以是本地路径或 URL（仅用户自己的音频；Noiz 支持）：

```json
{
  "default": { "voice_id": "voice_123", "target_lang": "zh" },
  "segments": {
    "1": { "voice_id": "voice_host", "emo": { "Joy": 0.6 } },
    "2-4": { "reference_audio": "./refs/guest.wav" }
  }
}
```

**动态参考音频切片**：
如果你在翻译或配音视频时，希望每句话自动使用与参考音频完全相同时间戳的原视频音频，请使用 `--ref-audio-track` 参数代替在映射中设置 `reference_audio`：
```bash
python3 skills/tts/scripts/tts.py render --srt input.srt --voice-map vm.json --ref-audio-track original_video.mp4 -o output.wav
```

完整示例请参考 `examples/` 文件夹。

### 第三步：渲染

```bash
python3 skills/tts/scripts/tts.py render --srt input.srt --voice-map vm.json -o output.wav
python3 skills/tts/scripts/tts.py render --srt input.srt --voice-map vm.json --backend noiz --auto-emotion -o output.wav
```

## 何时选择哪种后端

| 需求 | 推荐 |
|------|-------------|
| 仅朗读文本，无需复杂操作 | Kokoro (默认) |
| 电子书/PDF 有章节的音频书 | Kokoro (原生支持) |
| 语音混合 (`"v1:60,v2:40"`) | Kokoro |
| 从参考音频克隆语音 | Noiz |
| 情感控制 (`emo` 参数) | Noiz |
| 每段语音的精确服务器端时长 | Noiz |

> 当用户需要情感控制 + 语音克隆 + 精确时长时，Noiz 是唯一支持所有这三个功能的后端。

## 访客模式（无需 API 密钥）

当未配置 API 密钥时，`tts.py` 会自动切换到 **访客模式** — 这是一个需要无需认证的 Noiz 端点。访客模式仅支持 `--voice-id`，`--speed` 和 `--format`；语音克隆、情感、时长和时间轴渲染均不可用。

```bash
# 访客模式（未设置 API 密钥时自动检测）
python3 skills/tts/scripts/tts.py -t "Hello" --voice-id 883b6b7c -o hello.wav

# 显式覆盖后端使用 kokoro
python3 skills/tts/scripts/tts.py -t "Hello" --backend kokoro
```

可用的访客语音（15 个内置）：

| voice_id | name | lang | gender | tone |
|---|---|---|---|---|
| `063a4491` | 販売員（なおみ） | ja | F | 喜び |
| `4252b9c8` | 落ち着いた女性 | ja | F | 穏やか |
| `578b4be2` | 熱血漢（たける） | ja | M | 怒り |
| `a9249ce7` | 安らぎ（みなと） | ja | M | 穏やか |
| `f00e45a1` | 旅人（かいと） | ja | M | 穏やか |
| `b4775100` | 悦悦｜社交分享 | zh | F | Joyful |
| `77e15f2c` | 婉青｜情绪抚慰 | zh | F | Calm |
| `ac09aeb4` | 阿豪｜磁性主持 | zh | M | Calm |
| `87cb2405` | 建国｜知识科普 | zh | M | Calm |
| `3b9f1e27` | 小明｜科技达人 | zh | M | Joyful |
| `95814add` | Science Narration | en | M | Calm |
| `883b6b7c` | The Mentor (Alex) | en | M | Joyful |
| `a845c7de` | The Naturalist (Silas) | en | M | Calm |
| `5a68d66b` | The Healer (Serena) | en | F | Calm |
| `0e4ab6ec` | The Mentor (Maya) | en | F | Calm |

## 安全与数据披露

此技能在运行时执行以下文件和网络操作：

- **凭证存储**：当你运行 `config --set-api-key` 时，密钥会保存到 `~/.config/noiz/api_key`（权限 `0600`）。`NOIZ_API_KEY` 环境变量也作为替代方案支持。
- **旧密钥迁移**：如果 `~/.noiz_api_key` 存在而 `~/.config/noiz/api_key` 不存在，密钥会被**复制**（不会删除）到新位置。会打印一条消息；旧文件会保留供你手动删除。
- **网络请求（Noiz 后端）**：文本和可选的参考音频会上传到 `https://noiz.ai/v1/` 进行合成。除非你调用 Noiz 命令，否则不会发送任何数据。
- **参考音频下载**：当 `--ref-audio` 是 URL 时，文件会下载到临时文件，用于 API 调用，然后删除。如果未提供 voice-id 或 ref-audio，会从 `storage.googleapis.com` 或 `noiz.ai` 下载默认参考音频。
- **临时文件**：在合成过程中可能会创建临时音频/文本文件，并在使用后清理。
- **ffmpeg**：仅在时间轴 `render` 模式下调用，用于组装最终音频。

除了输出路径和 `~/.config/noiz/` 之外，不会修改任何文件。Kokoro 后端完全离线运行，无需网络访问。

## 依赖项

- `ffmpeg` 在 PATH 中（时间轴模式仅需要）
- `requests` 包：`uv pip install requests`（Noiz 后端需要）
- 在 [Noiz 开发者](https://developers.noiz.ai/api-keys) 获取你的 API 密钥，然后运行 `python3 skills/tts/scripts/tts.py config --set-api-key YOUR_KEY`（访客模式无需密钥但功能有限）
- Kokoro：如果已安装，传递 `--backend kokoro` 以使用本地后端

### Noiz API 认证

仅使用 base64 编码的 API 密钥作为 `Authorization` — 无需前缀（例如，不要 `APIKEY ` 或 `Bearer `）。任何前缀都会导致 401。

后端详细信息和完整参数参考请见 [reference.md](reference.md)。
