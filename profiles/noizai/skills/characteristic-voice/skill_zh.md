# 特色语音

让你的 AI 代理听起来像一个真正的伙伴——一个会叹息、大笑、犹豫，并用真诚的情感说话的人。

## 凭证

| 变量 | 必填 | 描述 |
|---|---|---|
| `NOIZ_API_KEY` | **是**（如果使用 Noiz 后端） | 来自 [developers.noiz.ai](https://developers.noiz.ai/api-keys) 的 API 密钥。如果使用本地 Kokoro 后端则不需要。 |

脚本会为了方便将密钥的规范化副本保存到 `~/.noiz_api_key`（模式 600）。设置方法：

```bash
bash skills/characteristic-voice/scripts/speak.sh config --set-api-key YOUR_KEY
```

## 前置条件

包含的 `speak.sh` 脚本在运行时需要 **curl** 和 **python3**。根据你使用的后端和功能，你可能还需要：

| 工具 | 需要时 | 安装提示 |
|---|---|---|
| `curl`, `python3` | 总是（核心脚本） | 通常预装 |
| `kokoro-tts` | Kokoro（本地/离线）后端 | `uv tool install kokoro-tts` |
| `yt-dlp` | 下载用于语音克隆的参考音频 | [github.com/yt-dlp/yt-dlp](https://github.com/yt-dlp/yt-dlp) |
| `ffmpeg` | 剪辑参考音频片段 | [ffmpeg.org](https://ffmpeg.org) |
| `rg` (ripgrep) | 搜索字幕文件 | [github.com/BurntSushi/ripgrep](https://github.com/BurntSushi/ripgrep) |

这些都不是由技能本身安装的——请手动在你的环境中配置它们。

## 隐私与数据传输

- **Noiz 后端**：使用 Noiz 后端时，你所说的文本以及你提供的任何参考音频都会发送到 `https://noiz.ai/v1`。如果你提供 `--ref-audio`，该音频文件将被上传用于语音克隆。
- **Kokoro 后端**：完全在本地运行——没有数据离开你的机器。
- 如果你想进行完全离线处理，请选择 Kokoro 后端 (`--backend kokoro`)。

## 触发词

- say like
- talk like
- speak like 
- companion voice
- comfort me
- cheer me up
- sound more human

## 两个技巧

1. **非词汇填充词**——在自然的停顿点加入一些人类的声音（嗯，哈哈，啊，嘿嘿）让演讲感觉生动
2. **情绪调谐**——调整温暖、喜悦、悲伤、温柔以匹配时刻

## 填充音调色板

| 声音 | 感觉 | 用于 |
|-------|---------|---------|
| hmm... | 思考，温和的确认 | 安慰，思考 |
| ah... | 意识到，柔和的惊讶 | 发现，过渡 |
| uh... | 犹豫，共情 | 小心时刻 |
| heh / hehe | 俏皮，淘气 | 取笑，轻松时刻 |
| haha | 笑声 | 喜悦，幽默 |
| aww | 温柔，同情 | 深度安慰 |
| oh? / oh! | 惊讶，注意力 | 对新闻做出反应 |
| pfft | 抑制的笑声 | 俏皮的怀疑 |
| whew | 解除 | 紧张之后 |
| ~ (波浪号) | 拉长，旋律结尾 | 温暖，俏皮 |

**规则**：每条短消息最多 2-4 个填充词。放在自然的停顿处——句子开始，思路转变。在填充词后使用 `...` 表示沉默，在单词结尾使用 `~` 表示温暖。

## 预设

### Good Night

温柔，温暖，略带困倦。慢节奏。

### Good Morning

温暖，愉快但不令人不知所措。

### Comfort

柔和，理解，不匆忙。留出空间。不要急于“解决问题”。

### Celebration

兴奋，自豪，真诚的快乐。

### Just Chatting

放松，俏皮，自然。

## 使用角色的声音

当用户说类似 *"用赫敏的声音说话"* 或 *"听起来像托尼·斯塔克"* 时，首先检查 `skills/characteristic-voice/` 中是否已存在参考音频文件。如果有，直接使用 `--ref-audio` 与其配合。

如果没有参考音频，你可以创建一个——但**首先阅读下面的警告**。

### 准备参考音频（一次性设置）

你需要目标声音的 10-30 秒 WAV 录音片段。可能的来源：

1. **用户提供的音频**——最安全的选择。要求用户提供自己的录音。
2. **公共领域 / CC 授权片段**——搜索免费授权材料。
3. **从在线视频中提取**——像 `yt-dlp` 和 `ffmpeg` 这样的工具可以下载和剪辑音频。示例工作流程：

```bash
yt-dlp "URL" --write-auto-sub --sub-lang en --skip-download -o tmp/clip
rg -n "目标行" tmp/clip.en.vtt
yt-dlp "URL" -x --audio-format wav --download-sections "*00:00:00-00:00:25" -o tmp/clip
ffmpeg -i tmp/clip.wav -ss 00:00:02 -to 00:00:20 skills/characteristic-voice/character.wav
```

> **版权与隐私警告**：从受版权保护媒体（电影、电视、YouTube）下载并重用某人的声音可能违反版权或人格权法律，具体取决于你的司法管辖区。**不要上传私人录音或你没有使用权限的材料。** 使用 Noiz 后端时，参考音频会发送到 `https://noiz.ai/v1` 用于语音克隆。如果这是你的担忧，请考虑使用本地 Kokoro 后端。

### 使用参考音频

```bash
bash skills/characteristic-voice/scripts/speak.sh \
  --preset goodnight -t "Hmm... rest well~ Sweet dreams." \
  --ref-audio skills/characteristic-voice/character.wav -o night.wav
```

`--ref-audio` 标志会将文件上传到 Noiz 后端用于语音克隆（需要 `NOIZ_API_KEY`）。

---

## 使用方法

此技能提供 `speak.sh`，它是 `tts` 技能的包装器，带有适合伙伴的预设。

```bash
# 使用预设（自动设置情绪 + 速度）
bash skills/characteristic-voice/scripts/speak.sh \
  --preset goodnight -t "Hmm... rest well~ Sweet dreams." -o night.wav

# 自定义情绪覆盖
bash skills/characteristic-voice/scripts/speak.sh \
  -t "Aww... I'm right here." --emo '{"Tenderness":0.9}' --speed 0.75 -o comfort.wav

# 使用特定后端和声音
bash skills/characteristic-voice/scripts/speak.sh \
  --preset morning -t "Good morning~" --voice-id voice_abc --backend noiz -o morning.mp3 --format mp3
```

运行 `bash skills/characteristic-voice/scripts/speak.sh --help` 获取所有选项。

## 代理的写作指南

1. **开始柔和**——以填充词（"嗯..."，"哦~"）开头，而不是内容
2. **镜像能量**——他们低落时温柔，他们高涨时匹配
3. **保持简短**——1-3 句话，像朋友发来的语音消息
4. **温暖结束**——以连接结束（"我在这里"，"明天见~"）
5. **不要说教**——倾听并保持在场；不要不请自来的建议
