## 何时使用

- 用户希望将音频文件转录为文本
- 用户提供音频文件路径并要求转录
- 用户说“转录”、“识别”、“transcribe”、“语音转文字”

## 何时不应使用

- 用户希望从文本合成语音（请使用 `/tts`）
- 用户希望创建播客或解说（请使用 `/podcast` 或 `/explainer`）

## 目的

使用 `coli asr` 将音频文件转录为文本，该工具通过本地语音识别模型完全离线运行。无需 API 密钥。支持中文、英文、日语、韩语和粤语（sensevoice 模型）或仅英文（whisper 模型）。

运行 `coli asr --help` 获取当前 CLI 选项和受支持的标志。

## 严格约束

- 不得使用 shell 脚本。仅使用直接命令。
- 在任何交互之前，始终按照 `shared/config-pattern.md` 读取配置
- 按照 `shared/cli-patterns.md` 进行交互模式
- 一次只问一个问题

<HARD-GATE>
对于每个多选题步骤，使用 `AskUserQuestion` 工具——不要以纯文本形式打印选项。一次问一个问题。等待用户回答后再继续。在运行任何转录之前，收集所有参数后总结并要求用户确认。

</HARD-GATE>

## 交互流程

### 第 0 步：前提条件检查

在配置设置之前，静默检查环境：

```bash
COLI_OK=$(which coli 2>/dev/null && echo yes || echo no)
FFMPEG_OK=$(which ffmpeg 2>/dev/null && echo yes || echo no)
MODELS_DIR="$HOME/.coli/models"
MODELS_OK=$([ -d "$MODELS_DIR" ] && ls "$MODELS_DIR" | grep -q sherpa && echo yes || echo no)
```

| 问题 | 操作 |
|------|------|
| `coli` 未找到 | 阻止。提示用户先运行 `npm install -g @marswave/coli` |
| `ffmpeg` 未找到 | 警告（WAV 文件仍然可用）。建议 `brew install ffmpeg` / `sudo apt install ffmpeg` |
| 模型未下载 | 通知用户：首次转录将自动下载模型（约 60MB）到 `~/.coli/models/` |

如果 `coli` 缺失，则停止此处，不要继续。

### 第 0 步：配置设置

遵循 `shared/config-pattern.md` 第 0 步（零问题启动）。

**如果文件不存在**——静默创建默认值并继续：
```bash
mkdir -p ".listenhub/asr"
echo '{"model":"sensevoice","polish":true}' > ".listenhub/asr/config.json"
CONFIG_PATH=".listenhub/asr/config.json"
CONFIG=$(cat "$CONFIG_PATH")
```
**不要询问任何设置问题。** 直接进入交互流程，使用合理的默认值（sensevoice 模型，启用润色）。

**如果文件存在**——静默读取配置并继续：
```bash
CONFIG_PATH=".listenhub/asr/config.json"
[ ! -f "$CONFIG_PATH" ] && CONFIG_PATH="$HOME/.listenhub/asr/config.json"
CONFIG=$(cat "$CONFIG_PATH")
```

### 设置流程（仅用户主动重新配置时运行）

仅在用户明确要求重新配置时运行。显示当前设置：
```
当前配置 (asr)：
  模型：sensevoice / whisper-tiny.en
  润色：开启 / 关闭
```

按顺序询问：

1. **model**: "默认使用哪个语音识别模型？"
   - "sensevoice（推荐）" — 支持中英日韩粤，可检测语言、情绪、音频事件
   - "whisper-tiny.en" — 仅英文

3. **polish**: "转录后由 AI 润色文本？（修正标点、去语气词、提升可读性）"
   - "是（推荐）" → `polish: true`
   - "否，保留原始转录" → `polish: false`

收集所有答案后一次性保存。

### 第 1 步：获取音频文件

如果用户未提供文件路径，询问：

> "请提供要转录的音频文件路径。"

在继续之前验证文件是否存在。

### 第 2 步：确认

```
准备转录：

  文件：{filename}
  模型：{model}
  润色：{是 / 否}

继续？
```

### 第 3 步：转录

使用 JSON 输出运行 `coli asr`（以获取元数据）：

```bash
coli asr -j --model {model} "{file}"
```

首次运行时，`coli` 将自动下载所需的模型。这可能需要一些时间——如果模型尚未下载，请通知用户。

解析 JSON 结果以提取 `text`、`lang`、`emotion`、`event`、`duration`。

### 第 4 步：润色（如果启用）

如果 `polish` 为 `true`，则从转录结果中获取原始 `text` 并重写它以修正标点、去除填充词并提高可读性。保留原始含义和说话者意图。不要总结或释义。

### 第 5 步：展示结果

直接在对话中显示转录内容：

```
转录完成

{transcript text}

─────────────────
语言：{lang} · 情绪：{emotion} · 时长：{duration}s
```

如果已润色，请显示润色版本并注明其为 AI 优化。如有请求，可显示原始原始版本。

### 第 6 步：导出为 Markdown（可选）

展示结果后，询问：

```
Question: "保存为 Markdown 文件到当前目录？"
Options:
  - "是" — 保存到当前目录
  - "否" — 完成
```

如果同意，将 `{audio-filename}-transcript.md` 写入**当前工作目录**（用户运行 Claude Code 的位置）。文件应包含转录文本（如果启用了润色，则为润色版本），并带有前导标题：

```markdown
---
source: {original audio filename}
date: {YYYY-MM-DD}
model: {model used}
duration: {duration}s
lang: {detected language}
---

{transcript text}
```

## 可组合性

- **被调用**：需要转录录制音频的未来技能
- **调用**：无

## 示例

> "帮我转录这个文件 meeting.m4a"

1. 检查前提条件
2. 读取配置
3. 确认：meeting.m4a、sensevoice、润色开启
4. 运行 `coli asr -j --model sensevoice "meeting.m4a"`
5. 润色原始文本
6. 直接展示

> "transcribe interview.wav, no polish"

1. 检查前提条件
2. 读取配置
3. 为本次会话将润色设置为 false
4. 运行 `coli asr -j --model sensevoice "interview.wav"`
5. 直接展示原始转录
