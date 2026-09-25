# sag

使用 `sag` 命令进行 ElevenLabs TTS 并本地播放。

API 密钥（必需）

- `ELEVENLABS_API_KEY`（首选）
- `SAG_API_KEY` CLI 也支持
- 通过 `--api-key-file`、`ELEVENLABS_API_KEY_FILE` 或 `SAG_API_KEY_FILE` 指定密钥文件

快速入门

- `sag "你好"`
- `sag speak -v "罗杰" "你好"`
- `sag voices`
- `sag prompting`（特定模型的提示）

模型说明

- 默认：`eleven_v3`（富有表现力）
- 稳定：`eleven_multilingual_v2`
- 快速：`eleven_flash_v2_5`

发音 + 播报规则

- 首次修正：重新拼写（例如 "key-note"），添加连字符，调整大小写。
- 数字/单位/URL：`--normalize auto`（如果它损害名称，则使用 `off`）。
- 语言偏好：`--lang en|de|fr|...` 指导规范化。
- v3：不支持 SSML `<break>`；使用 `[停顿]`、`[短停顿]`、`[长停顿]`。
- v2/v2.5：支持 SSML `<break time="1.5s" />`；`<phoneme>` 在 `sag` 中未暴露。

v3 音频标签（放在行的开头）

- `[低语]`、`[呐喊]`、`[歌唱]`
- `[笑声]`、`[开始笑]`、`[叹息]`、`[呼气]`
- `[讽刺]`、`[好奇]`、`[兴奋]`、`[哭泣]`、`[恶作剧]`
- 示例：`sag "[低语]保持安静。[短停顿]好吧?"`

声音默认值

- `ELEVENLABS_VOICE_ID` 或 `SAG_VOICE_ID`

在长输出前确认声音 + 说话者。

## 聊天声音回复

当用户要求“声音”回复（例如，“疯狂科学家声音”、“用声音解释”）时，生成音频并发送：

```bash
# 生成音频文件
sag -v Clawd -o /tmp/voice-reply.mp3 "你的消息"

# 然后在回复中包含：
# MEDIA:/tmp/voice-reply.mp3
```

声音角色提示：

- 疯狂科学家：使用 `[兴奋]` 标签，戏剧性停顿 `[短停顿]`，变化强度
- 冷静：使用 `[低语]` 或更慢的节奏
- 戏剧性：少量使用 `[歌唱]` 或 `[呐喊]`

Clawd 的默认声音：`lj2rcrvANS3gaWWnczSX`（或直接 `-v Clawd`）
