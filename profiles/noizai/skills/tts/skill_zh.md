# tts

将任何文本转换为语音音频。支持两个后端（Kokoro 本地，Noiz 云端），两种模式（简单或时间轴精确），以及每段语音控制。

## 触发词

- 文本转语音 / tts / 说 / 讲
- 语音克隆 / 配音
- 电子书转音频 / srt 转音频 / 转换为音频
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

第三方集成（Feishu/Telegram/Discord）的文档请参考 [ref_3rd_party.md](ref_3rd_party.md)。

## 时间轴模式 — SRT 转时间对齐音频

用于精确的每段时间控制（配音、字幕、视频旁白）。

### 第一步：获取或创建 SRT

如果用户没有，从文本生成：

```bash
python3 skills/tts/scripts/tts.py to-srt -i article.txt -o article.srt
python3 skills/tts/scripts/tts.py to-srt -i article.txt -o article.srt --cps 15 --gap 500
```

`--cps` = 每秒字符数（默认 4，适合中文；~15 适合英文）。代理也可以手动编写 SRT。

### 第二步：创建语音映射

控制默认及每段语音设置的 JSON 文件。`segments` 键支持单个索引 `"3"` 或范围 `"5-8"`。

Kokoro 语音映射：

```json
{
  "default": { "voice": "zf_xiaoni", "lang": "cmn" },
  "segments": {
    "1": { "voice": "zm_yunxi" },
    "5-8": { "voice": "af_sarah", "lang": "en-us", "speed": 0.9 }
  }
}
```

Noiz 语音映射（增加 `emo`，`reference_audio` 支持）。`reference_audio` 可以是本地路径或 URL（用户自己的音频；Noiz 仅支持）：

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

完整示例请查看 `examples/`。

### 第三步：渲染

```bash
python3 skills/tts/scripts/tts.py render --srt input.srt --voice-map vm.json -o output.wav
python3 skills/tts/scripts/tts.py render --srt input.srt --voice-map vm.json --backend noiz --auto-emotion -o output.wav
```

## 何时选择哪个

| 需求 | 推荐 |
|------|-------------|
| 仅朗读文本，无需麻烦 | Kokoro (默认) |
| 带章节的电子书/PDF 有声书 | Kokoro (原生支持) |
| 语音混合 (`"v1:60,v2:40"`) | Kokoro |
| 从参考音频克隆语音 | Noiz |
| 情感控制 (`emo` 参数) | Noiz |
| 每段精确的服务器端时长 | Noiz |

> 当用户需要情感控制 + 语音克隆 + 精确时长时，Noiz 是唯一支持这三个功能的后端。

## 访客模式（无需 API 密钥）

当未配置 API 密钥时，`tts.py` 会自动切换到 **访客模式** — 一个无需认证的有限 Noiz 端点。访客模式仅支持 `--voice-id`，`--speed` 和 `--format`；语音克隆、情感、时长和时间轴渲染不可用。

```bash
# 访客模式（未设置 API 密钥时自动检测）
python3 skills/tts/scripts/tts.py -t "Hello" --voice-id 883b6b7c -o hello.wav

# 显式后端覆盖，使用 kokoro
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

- **凭证存储**：运行 `config --set-api-key` 时，密钥会保存到 `~/.config/noiz/api_key`（权限 `0600`）。`NOIZ_API_KEY` 环境变量也作为替代支持。
- **旧密钥迁移**：如果 `~/.noiz_api_key` 存在而 `~/.config/noiz/api_key` 不存在，密钥会**复制**（不删除）到新位置。会打印消息；旧文件会保留供你手动删除。
- **网络调用（Noiz 后端）**：文本和可选的参考音频会上传到 `https://noiz.ai/v1/` 进行合成。除非你调用 Noiz 命令，否则不会发送任何数据。
- **参考音频下载**：当 `--ref-audio` 是 URL 时，文件会下载到临时文件，用于 API 调用，然后删除。如果未提供 voice-id 或 ref-audio，会从 `storage.googleapis.com` 或 `noiz.ai` 下载默认参考音频。
- **临时文件**：在合成过程中可能会创建临时音频/文本文件，并在使用后清理。
- **ffmpeg**：仅在时间轴 `render` 模式下调用，用于组装最终音频。

除了输出路径和 `~/.config/noiz/` 之外，不会修改任何文件。Kokoro 后端完全离线运行，无需网络访问。

## 要求

- `ffmpeg` 在 PATH（时间轴模式仅需要）
- `requests` 包：`uv pip install requests`（Noiz 后端需要）
- 在 [Noiz 开发者](https://developers.noiz.ai/api-keys) 获取你的 API 密钥，然后运行 `python3 skills/tts/scripts/tts.py config --set-api-key YOUR_KEY`（访客模式无需密钥但功能有限）
- Kokoro：如果已安装，传递 `--backend kokoro` 以使用本地后端

### Noiz API 认证

仅使用 base64 编码的 API 密钥作为 `Authorization` — 无需前缀（例如，无需 `APIKEY ` 或 `Bearer `）。任何前缀会导致 401。

有关后端详细信息和完整参数参考，请查看 [reference.md](reference.md)。
