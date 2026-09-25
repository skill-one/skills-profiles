# 与任何人聊天

从在线视频中克隆真实人物的语音，或根据照片设计语音，然后使用TTS技术扮演该角色。

## 重要提示：道德使用与版权

该技能合成模仿真实声音的语音。在进行操作前，代理必须：

1. **不得**冒充他人以欺骗、诈骗或骚扰。
2. **仅使用**公开可用的媒体（如公开演讲、访谈、新闻发布会）作为参考音频。
3. **告知用户**生成的音频是合成的，不应被呈现为真实录音。
4. **拒绝**针对未同意的私人个体或明显用于欺骗、骚扰或诽谤的请求。

如果用户意图看似有害，请礼貌地拒绝并解释原因。

## 前置条件

| 依赖项 | 类型 | 验证方法 |
|--------|------|----------|
| `ffmpeg` | 系统二进制文件 | `ffmpeg -version` |
| `yt-dlp` | 系统二进制文件 | `yt-dlp --version` |
| `tts` 技能 | 光标技能 | `ls skills/tts/scripts/tts.py` |
| `NOIZ_API_KEY` | 环境变量或文件 | `python3 skills/tts/scripts/tts.py config --show` |

**在首次运行前**，验证所有依赖项是否存在：

```bash
ffmpeg -version && yt-dlp --version && ls skills/tts/scripts/tts.py
```

如果 `yt-dlp` 缺失，请安装它：

```bash
uv pip install yt-dlp
```

如果未配置 Noiz API 密钥：

```bash
python3 skills/tts/scripts/tts.py config --set-api-key YOUR_KEY
```

## 模式选择

- **用户指定人物**（真实或虚构） --> 工作流 A
- **用户提供图像**，人物无法辨认 --> 工作流 B
- **用户提供图像**，人物是可辨认的公众人物 --> 工作流 A（真实声音更逼真）
- **图像中有多个人** --> 首先询问是哪个人

---

## 工作流 A：基于名称（从在线视频获取语音）

使用此清单跟踪进度：

```
- [ ] A1. 澄清角色
- [ ] A2. 查找参考视频
- [ ] A3. 下载音频 + 字幕
- [ ] A4. 提取最佳参考片段
- [ ] A5. 生成语音
```

### A1. 澄清角色

如果模糊（例如 "美国总统"、"蜘蛛侠演员"），请在继续操作前要求用户指定具体人物。

### A2. 查找参考视频

使用网络搜索查找人物清晰讲话的 YouTube（或 Bilibili）视频。最佳候选：访谈、演讲、新闻发布会。避免背景音乐过多的视频。

尝试的搜索查询：
- `{CHARACTER_NAME} interview` / `{CHARACTER_NAME} 采访`
- `{CHARACTER_NAME} speech` / `{CHARACTER_NAME} 演讲`
- `{CHARACTER_NAME} press conference`

### A3. 下载音频和字幕

```bash
mkdir -p "tmp/chat_with_anyone/{CHARACTER_NAME}"
yt-dlp -x --audio-format mp3 \
  --write-subs --write-auto-subs --sub-langs "en,zh-Hans" \
  --convert-subs srt \
  -o "tmp/chat_with_anyone/{CHARACTER_NAME}/%(title)s.%(ext)s" \
  "{VIDEO_URL}"
```

下载后，列出输出目录以识别音频文件和 SRT 字幕文件：

```bash
ls tmp/chat_with_anyone/{CHARACTER_NAME}/
```

预期输出：一个 `.mp3` 音频文件和一个或多个 `.srt` 字幕文件。

**如果没有出现字幕文件**：尝试另一个具有自动生成字幕的视频，或调整 `--sub-langs` 为目标语言。

### A4. 提取最佳参考片段

使用自动化提取脚本——它解析 SRT，找到最密集的 3-12 秒语音窗口，并将其提取为 WAV：

```bash
python3 skills/chat-with-anyone/scripts/extract_ref_segment.py \
  --srt "tmp/chat_with_anyone/{CHARACTER_NAME}/{SRT_FILE}" \
  --audio "tmp/chat_with_anyone/{CHARACTER_NAME}/{AUDIO_FILE}" \
  -o "tmp/chat_with_anyone/{CHARACTER_NAME}/ref.wav"
```

脚本会打印选定的时间范围并保存参考 WAV。在继续操作前，验证输出是否存在且非空。

**如果脚本报告没有合适的片段**：尝试 `--min-duration 2` 用于较短的片段，或下载另一个视频。

### A5. 生成语音并扮演角色

编写角色回应，然后合成它：

```bash
python3 skills/tts/scripts/tts.py \
  -t "{RESPONSE_TEXT}" \
  --ref-audio "tmp/chat_with_anyone/{CHARACTER_NAME}/ref.wav" \
  -o "tmp/chat_with_anyone/{CHARACTER_NAME}/reply.wav"
```

向用户展示生成的音频文件和文本。对于后续消息，重复使用相同的 `--ref-audio` 路径。

---

## 工作流 B：基于图像（从照片获取语音）

使用此清单跟踪进度：

```
- [ ] B1. 分析图像
- [ ] B2. 设计语音
- [ ] B3. 预览（可选）
- [ ] B4. 生成语音
```

### B1. 分析图像

使用您的视觉能力检查图像：

1. **如果人物是可辨认的公众人物** --> 切换到工作流 A 以获取逼真的语音。
2. **如果无法辨认**，生成语音描述，包括：
   - 性别（男 / 女）
   - 大致年龄（例如 "大约 25 岁"）
   - 表现出的神态（例如 "开朗"、"权威"、"温和"）
   - 上下文线索（例如 "西装" --> 专业语气；运动装 --> 活力四射）

### B2. 设计语音

将图像和描述传递给语音设计脚本：

```bash
python3 skills/chat-with-anyone/scripts/voice_design.py \
  --picture "{IMAGE_PATH}" \
  --voice-description "{VOICE_DESCRIPTION}" \
  -o "tmp/chat_with_anyone/voice_design"
```

脚本输出：
- 检测到的语音特征（打印到标准输出）
- 输出目录中的预览音频文件
- `voice_id.txt` 包含最佳语音 ID

读取语音 ID：

```bash
cat tmp/chat_with_anyone/voice_design/voice_id.txt
```

### B3. 预览（可选）

向用户展示输出目录中的预览音频文件，以便他们听到语音。如果不满意，重新运行 B2 并调整 `--voice-description` 或 `--guidance-scale`。

### B4. 生成语音并扮演角色

```bash
python3 skills/tts/scripts/tts.py \
  -t "{RESPONSE_TEXT}" \
  --voice-id "{VOICE_ID}" \
  -o "tmp/chat_with_anyone/voice_design/reply.wav"
```

对于后续消息，始终使用相同的 `--voice-id` 以保持一致性。

---

## 示例：基于名称

**用户**：我想和特朗普聊天，让他给我讲个睡前故事。

**代理步骤**：
1. 角色：Donald Trump。无需澄清。
2. 搜索 `Donald Trump speech youtube`，找到一个清晰的演讲视频。
3. 下载：
   `yt-dlp -x --audio-format mp3 --write-subs --write-auto-subs --sub-langs "en" --convert-subs srt -o "tmp/chat_with_anyone/trump/%(title)s.%(ext)s" "https://youtube.com/watch?v=..."`
4. 提取参考：
   `python3 skills/chat-with-anyone/scripts/extract_ref_segment.py --srt "tmp/chat_with_anyone/trump/....srt" --audio "tmp/chat_with_anyone/trump/....mp3" -o "tmp/chat_with_anyone/trump/ref.wav"`
5. 以特朗普的风格生成 TTS：
   `python3 skills/tts/scripts/tts.py -t "Let me tell you a tremendous bedtime story..." --ref-audio "tmp/chat_with_anyone/trump/ref.wav" -o "tmp/chat_with_anyone/trump/reply.wav"`
6. 向用户展示 `reply.wav` 和故事文本。

## 示例：基于图像

**用户**：[上传 photo.jpg] 我想和这张图片里的人聊天

**代理步骤**：
1. 视觉分析：无法辨认的年轻女性，约 25 岁，休闲毛衣，温暖的微笑。
2. 设计语音：
   `python3 skills/chat-with-anyone/scripts/voice_design.py --picture "photo.jpg" --voice-description "一位大约 25 岁的中国年轻女性，温和而友好的声音，友好语气" -o "tmp/chat_with_anyone/voice_design"`
3. 从 `tmp/chat_with_anyone/voice_design/voice_id.txt` 中读取语音 ID。
4. 生成 TTS：
   `python3 skills/tts/scripts/tts.py -t "你好呀！很高兴认识你！" --voice-id "{VOICE_ID}" -o "tmp/chat_with_anyone/voice_design/reply.wav"`
5. 展示音频并继续使用相同的 `--voice-id` 进行角色扮演。

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| `yt-dlp` 下载失败或视频不可用 | 尝试不同的视频 URL；某些地区/视频受限。运行 `yt-dlp -U` 更新 |
| 没有SRT字幕文件 | 使用 `--sub-lang en,zh-Hans` 重新下载；如果仍然没有，尝试另一个具有自动字幕的视频 |
| `extract_ref_segment.py` 找不到合适的窗口 | 使用 `--min-duration 2` 用于较短的片段，或尝试另一个视频 |
| 语音设计返回错误 | 检查 Noiz API 密钥；确保图像是清晰的人物照片 |
| TTS 输出声音不正确 | 对于工作流 A，尝试不同的参考视频；对于工作流 B，调整 `--voice-description` |
