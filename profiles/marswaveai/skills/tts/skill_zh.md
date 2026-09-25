## 使用场景

- 用户希望将文本转换为语音音频
- 用户询问“朗读”、“TTS”、“文本转语音”、“语音旁白”
- 用户说“朗读”、“配音”、“语音合成”
- 用户希望获得多角色脚本音频或对话

## 不适用场景

- 用户希望进行播客风格的讨论并探索主题（使用 `/podcast`）
- 用户希望生成带视觉效果的解说视频（使用 `/explainer`）
- 用户希望生成图像（使用 `/image-gen`）

## 目的

将文本转换为自然语音音频。两种路径：

1. **快速模式** (`--mode direct`)：单语音、低延迟、同步。适用于休闲聊天、阅读片段、即时音频。
2. **脚本模式** (`--mode smart`)：多角色、分段语音分配。适用于对话、有声读物、脚本内容。

## 严格限制

- 始终在 `shared/cli-authentication.md` 后检查 CLI 认证
- 按照 `shared/cli-patterns.md` 执行 CLI、错误和交互模式
- 在 CLI 调用中永不硬编码说话人 ID —— 仅作为后备使用内置默认值；当用户想要更改声音时从说话人 CLI 获取
- 在任何交互之前始终读取 `shared/config-pattern.md` 中的配置
- 始终按照 `shared/speaker-selection.md` 进行说话人选择（文本表格 + 自由文本输入）
- 永不将文件保存到 `~/Downloads/` 或 `/tmp/` 作为主要输出 —— 将工件保存到当前工作目录，使用友好的基于主题的名称（参见 `shared/config-pattern.md` § 工件命名）

<HARD-GATE>
对每个多选步骤使用 AskUserQuestion 工具 —— 不要将选项作为纯文本打印。一次问一个问题。等待用户回答后再进行下一步。在收集所有参数后，总结选择并询问用户确认。在用户明确确认之前，不要调用任何生成 CLI 命令。

</HARD-GATE>

## 模式检测

在使用任何问题之前自动从用户输入中确定模式：

| 信号        | 模式   |
|------------|--------|
| "多角色", "脚本", "对话", "script", "dialogue", "multi-speaker" | 脚本   |
| 提及名称或角色的多个角色 | 脚本   |
| 输入包含结构化段落（A: ..., B: ...） | 脚本   |
| 单个段落文本，无角色标记 | 快速   |
| "读一下", "read this", "TTS", "朗读" 与纯文本 | 快速   |
| 模糊不清    | 快速（默认） |

## 交互流程

### 步骤 -1：CLI 认证检查

遵循 `shared/cli-authentication.md`。如果 CLI 未安装或用户未登录，自动安装和自动登录 —— 不要要求用户手动运行命令。

然后遵循 `shared/cli-authentication.md` § 认证模式检测来确定 `AUTH_MODE` 并设置：

```bash
if [ "$AUTH_MODE" = "openapi" ]; then
  CMD_PREFIX="listenhub openapi tts"
else
  CMD_PREFIX="listenhub tts"
fi
```

所有后续 CLI 调用使用 `$CMD_PREFIX` 而不是硬编码 `listenhub tts`。

### 步骤 0：配置设置

遵循 `shared/config-pattern.md` 步骤 0（零问题启动）。

**如果文件不存在** —— 静默创建默认值并继续：
```bash
mkdir -p ".listenhub/tts"
echo '{"outputMode":"inline","language":null,"defaultSpeakers":{}}' > ".listenhub/tts/config.json"
CONFIG_PATH=".listenhub/tts/config.json"
CONFIG=$(cat "$CONFIG_PATH")
```
**不要询问任何设置问题。** 直接进入交互流程。

**如果文件存在** —— 静默读取配置并继续：
```bash
CONFIG_PATH=".listenhub/tts/config.json"
[ ! -f "$CONFIG_PATH" ] && CONFIG_PATH="$HOME/.listenhub/tts/config.json"
CONFIG=$(cat "$CONFIG_PATH")
```

### 设置流程（仅用户主动重新配置）

仅在用户明确要求重新配置时运行。显示当前设置：
```
当前配置 (tts)：
  输出方式：{inline / download / both}
  语言偏好：{zh / en / 未设置}
  默认主播：{speakerName / 使用内置默认}
```

然后询问：

1. **outputMode**: 遵循 `shared/output-mode.md` § 设置流程问题。

2. **语言**（可选）: "默认语言？"
   - "中文 (zh)"
   - "English (en)"
   - "每次手动选择" → 保持 `null`

收集答案后立即保存：
```bash
NEW_CONFIG=$(echo "$CONFIG" | jq --arg m "$OUTPUT_MODE" '. + {"outputMode": $m}')
# 如果用户选择了语言（不是 "每次手动选择"）
if [ "$LANGUAGE" != "null" ]; then
  NEW_CONFIG=$(echo "$NEW_CONFIG" | jq --arg lang "$LANGUAGE" '. + {"language": $lang}')
fi
echo "$NEW_CONFIG" > "$CONFIG_PATH"
CONFIG=$(cat "$CONFIG_PATH")
```

### 生成速度

**默认：1.0x（原始速度）。永不询问速度。**

仅在用户明确要求更快或更慢的朗读时传递 `--speed` ——
"慢一点"、"快一点"、"1.25 倍速"、"read it faster"。否则省略标志。

- 范围：任何从 `0.5` 到 `2.0` 的值，最多两位小数 —— 连续范围，不是固定步长。
- 常见值：`0.5`, `0.75`, `1`（默认）, `1.25`, `1.5`, `2`；中间值，如 `0.85` 或 `1.35` 也有效。
- 含义：生成音频的说话速率，不是播放器播放速率。
- 保守映射模糊措辞："慢一点" → `0.85`, "快一点" → `1.25`, "慢很多" → `0.5`, "快很多" → `1.75`。用户命名的数字将原样传递。

仅在速度不是 `1` 时在确认摘要中显示速度。

### 快速模式 — `$CMD_PREFIX create --mode direct`

**步骤 1：提取文本**

获取要转换的文本。如果用户未提供，询问：

> "您希望我朗读哪些文本？"

**步骤 2：确定语音**

- 如果 `config.defaultSpeakers.{language}[0]` 已设置 → 静默使用（跳至步骤 4）
- 如果未设置 → 使用检测语言的内置默认值（跳至步骤 4）
- 仅在用户明确要求更改语音时显示说话人选择

**步骤 3：保存偏好**

在用户明确选择新语音后（使用默认值时除外）：

```
问题: "将 {voice name} 保存为 {language} 的默认语音？"
选项：
  - "是" — 更新 .listenhub/tts/config.json
  - "否" — 仅本次会话使用
```

**步骤 4：确认**

```
准备生成：

  文本："{前 80 个字符}..."
  语音：{voice name}
  速度：{speed}x        # 当速度为 1 时省略此行

继续？
```

**步骤 5：生成**

对于短文本，直接传递：
```bash
RESULT=$($CMD_PREFIX create --text "{text}" --mode direct --speaker "{name}" --lang {lang} [--speed {0.5-2.0}] --json 2>/tmp/lh-err)
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
  ERROR=$(cat /tmp/lh-err)
  case $EXIT_CODE in
    2) echo "认证错误：运行 'listenhub auth login'" ;;
    3) echo "超时：尝试 --no-wait" ;;
    *) echo "错误：$ERROR" ;;
  esac
  rm -f /tmp/lh-err
fi
rm -f /tmp/lh-err

AUDIO_URL=$(echo "$RESULT" | jq -r '.audioUrl')
```

对于长文本，首先写入临时文件（参见 `shared/cli-patterns.md` § 长文本输入）：
```bash
cat > /tmp/lh-content.txt << 'ENDCONTENT'
长文本内容放在这里...
ENDCONTENT

RESULT=$($CMD_PREFIX create --text "$(cat /tmp/lh-content.txt)" --mode direct --speaker "{name}" --lang {lang} [--speed {0.5-2.0}] --json)
AUDIO_URL=$(echo "$RESULT" | jq -r '.audioUrl')

rm -f /tmp/lh-content.txt
```

**步骤 6：展示结果**

从配置中读取 `OUTPUT_MODE`。遵循 `shared/output-mode.md` 进行行为。

**`inline` 或 `both`**：将 `audioUrl` 显示为可点击链接。

展示：
```
音频已生成！

在线收听：{audioUrl}
```

**`download` 或 `both`**：也下载文件。根据文本内容生成主题 slug，遵循 `shared/config-pattern.md` § 工件命名。
```bash
SLUG="{topic-slug}"  # 例如 "server-maintenance-notice"
NAME="${SLUG}.mp3"
# 去重：如果文件存在，追加 -2, -3, 等。
BASE="${NAME%.*}"; EXT="${NAME##*.}"; i=2
while [ -e "$NAME" ]; do NAME="${BASE}-${i}.${EXT}"; i=$((i+1)); done
curl -sS -o "$NAME" "$AUDIO_URL"
```
展示：
```
已保存到当前目录：
  {NAME}
```

---

### 脚本模式 — `$CMD_PREFIX create --mode smart`

**步骤 1：获取脚本**

确定用户是否已提供脚本数组：

- **已提供**（JSON 或清晰段落）：解析并确认显示
- **尚未提供**：帮助用户结构化段落。询问：

  > "请提供带有说话人分配的脚本。格式：每行作为 `SpeakerName: 文本内容`。我将将其转换。"

  一旦用户提供脚本，将其解析为带说话人注释的文本。

**步骤 2：按角色分配语音**

对于脚本中的每个唯一角色：

- 如果 `config.defaultSpeakers.{language}` 已保存语音 → 静默自动分配（每个角色按顺序一个）
- 如果未设置 → 使用内置默认值（主要角色为第一个，次要角色为第二个）
- 仅在用户明确要求更改语音时显示说话人选择

**步骤 3：保存偏好**

在分配所有语音后（如果有新语音）：

```
问题: "保存这些语音分配以供未来会话使用？"
选项：
  - "是" — 更新 .listenhub/tts/config.json 中的 defaultSpeakers
  - "否" — 仅本次会话使用
```

**步骤 4：确认**

```
准备生成：

  角色：
    {name}: {voice}
    {name}: {voice}
  段落：{count}
  速度：{speed}x        # 当速度为 1 时省略此行
  标题：自动生成

继续？
```

**步骤 5：生成**

使用说话人标记格式化脚本文本并提交。对于多角色脚本，将说话人名称内联在文本中。由于脚本模式可能需要更长时间，使用 `run_in_background: true` 运行。

**前台提交** 使用 `--no-wait`：
```bash
RESULT=$($CMD_PREFIX create --text "{formatted script with speaker markers}" --mode smart --speaker "{name1}" --speaker "{name2}" --lang {lang} [--speed {0.5-2.0}] --no-wait --json)
ID=$(echo "$RESULT" | jq -r '.id')
echo "已提交：$ID"
```

对于长脚本，首先写入临时文件：
```bash
cat > /tmp/lh-content.txt << 'ENDCONTENT'
SpeakerA: 第一行对话
SpeakerB: 第二行对话
...
ENDCONTENT

RESULT=$($CMD_PREFIX create --text "$(cat /tmp/lh-content.txt)" --mode smart --speaker "{name1}" --speaker "{name2}" --lang {lang} [--speed {0.5-2.0}] --no-wait --json)
ID=$(echo "$RESULT" | jq -r '.id')

rm -f /tmp/lh-content.txt
```

**后台轮询** 使用 `run_in_background: true` 和 `timeout: 600000`：
```bash
ID="<id-from-above>"
for i in $(seq 1 60); do
  RESULT=$(listenhub creation get "$ID" --json 2>/dev/null)
  STATUS=$(echo "$RESULT" | jq -r '.status // "processing"')

  case "$STATUS" in
    completed) echo "$RESULT"; exit 0 ;;
    failed) echo "FAILED: $RESULT" >&2; exit 1 ;;
    *) sleep 10 ;;
  esac
done
echo "TIMEOUT" >&2; exit 2
```

**步骤 6：展示结果**

当后台任务完成时，解析结果：
```bash
AUDIO_URL=$(echo "$RESULT" | jq -r '.audioUrl')
SUBTITLES_URL=$(echo "$RESULT" | jq -r '.subtitlesUrl // empty')
DURATION=$(echo "$RESULT" | jq -r '.audioDuration // empty')
CREDITS=$(echo "$RESULT" | jq -r '.credits // empty')
```

从配置中读取 `OUTPUT_MODE`。遵循 `shared/output-mode.md` 进行行为。

**`inline` 或 `both`**：显示 `audioUrl` 和 `subtitlesUrl` 作为可点击链接。

展示：
```
音频已生成！

在线收听：{audioUrl}
字幕：{subtitlesUrl}
时长：{audioDuration / 1000}s
消耗积分：{credits}
```

**`download` 或 `both`**：也下载文件。根据 `shared/config-pattern.md` § 工件命名生成主题 slug。
```bash
SLUG="{topic-slug}"  # 例如 "welcome-dialogue"
NAME="${SLUG}.mp3"
# 去重：如果文件存在，追加 -2, -3, 等。
BASE="${NAME%.*}"; EXT="${NAME##*.}"; i=2
while [ -e "$NAME" ]; do NAME="${BASE}-${i}.${EXT}"; i=$((i+1)); done
curl -sS -o "$NAME" "$AUDIO_URL"
```
展示：
```
已保存到当前目录：
  {NAME}
```

---

## 更新配置

在保存偏好时，合并到 `.listenhub/tts/config.json` —— 不要覆盖未更改的键。

- 快速语音：将 `defaultSpeakers.{language}[0]` 设置为选择的 `speakerId`
- 脚本语音：将 `defaultSpeakers.{language}` 设置为本次会话分配的完整数组
- 语言：如果用户明确指定，则设置 `language`

## API 参考

- CLI 执行模式：`shared/cli-patterns.md`
- CLI 认证：`shared/cli-authentication.md`
- 说话人列表：`shared/cli-speakers.md`
- 说话人选择指南：`shared/speaker-selection.md`
- 配置模式：`shared/config-pattern.md`
- 输出模式：`shared/output-mode.md`

## 组合性

- **调用**：说话人 CLI（用于说话人选择）
- **被调用**：解说（用于旁白）

## 示例

**快速模式：**

> "TTS 这个：服务器将在午夜进行维护。"

1. 检测：快速模式（纯文本，“TTS 这个”）
2. 读取配置：`defaultSpeakers.en` 为空
3. 使用内置默认值：Mars (`cozy-man-english`)
4. 确认 → 用户批准
5. 生成：
   ```bash
   RESULT=$($CMD_PREFIX create --text "The server will be down for maintenance at midnight." --mode direct --speaker "Mars" --lang en --json)
   AUDIO_URL=$(echo "$RESULT" | jq -r '.audioUrl')
   ```
6. 展示：显示 `audioUrl` 作为链接（inline 模式）

**脚本模式：**

> "帮我做一段双人对话配音，A 说：欢迎大家，B 说：谢谢邀请"

1. 检测：脚本模式（“双人对话”）
2. 解析段落：A -> "欢迎大家", B -> "谢谢邀请"
3. 读取配置：`defaultSpeakers.zh` 为空
4. 使用内置默认值：原野（主要）+ 高晴（次要）
5. 确认 → 用户批准
6. 生成：
   ```bash
   RESULT=$($CMD_PREFIX create --text "A: 欢迎大家
   B: 谢谢邀请" --mode smart --speaker "原野" --speaker "高晴" --lang zh --no-wait --json)
   ID=$(echo "$RESULT" | jq -r '.id')
   ```
7. 后台轮询直至完成
8. 展示：`audioUrl`, `subtitlesUrl`, 时长
