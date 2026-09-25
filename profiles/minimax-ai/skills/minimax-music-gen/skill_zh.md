# MiniMax 音乐生成技能

使用 MiniMax 音乐 API 生成歌曲（带歌词或纯音乐）。支持两种创作模式：**基础**（一句话输入，一首歌输出）和**高级控制**（编辑歌词，优化提示词，生成前规划）。

## 前置条件

- **mmx CLI**（必需）：音乐生成使用 `mmx` 命令行工具。
  **检查是否安装：**
  ```bash
  command -v mmx && mmx --version || echo "mmx 未找到"
  ```
  **安装（需要 Node.js）：**
  ```bash
  npm install -g mmx-cli
  ```
  **认证（仅首次需要）：**
  ```bash
  mmx auth login --api-key <your-minimax-api-key>
  ```
  API 密钥可以从 [MiniMax 平台](https://platform.minimaxi.com/) 获取。
  凭据保存到 `~/.mmx/credentials.json`，并在会话之间保持持久。
  **验证：**
  ```bash
  mmx quota show
  ```

- **音频播放器**（推荐）：`mpv`、`ffplay` 或 `afplay`（macOS 内置）用于本地播放。`mpv` 因其交互式控制而更受青睐。

## 命令行工具

此技能使用 `mmx` 命令行工具进行所有音乐生成：

- **音乐生成**：`mmx music generate` — 模型：`music-2.6-free`
  - 支持 `--lyrics-optimizer` 自动从提示词生成歌词
  - 支持 `--instrumental` 用于纯音乐曲目
  - 支持 `--lyrics` 用于用户提供的歌词
  - 结构化参数：`--genre`、`--mood`、`--vocals`、`--instruments`、`--bpm`、`--key`、`--tempo`、`--structure`、`--references`
  
- **翻唱**：`mmx music cover` — 模型：`music-cover-free`
  - 通过 `--audio-file <path>` 或 `--audio <url>` 提供参考音频
  - `--prompt` 描述目标翻唱风格

**代理标志**：从代理调用 `mmx` 时始终添加 `--quiet --non-interactive`。

**流程**：
- 带歌词：`用户描述 -> mmx music generate --lyrics-optimizer -> MP3`
- 纯音乐：`用户描述 -> mmx music generate --instrumental -> MP3`
- 翻唱：`源音频 + 风格 -> mmx music cover -> MP3`

## 存储

所有生成的音乐都保存到 `~/Music/minimax-gen/`。如果目录不存在，请创建它。文件名称由时间戳和从提示词派生的短标识符组成：`YYYYMMDD_HHMMSS_<slug>.mp3`

---

## 语言与交互

从用户的第一条消息中检测用户的语言，并在整个会话中用该语言回复。这适用于所有交互文本、问题、确认和反馈提示。

**面向用户的文本本地化规则**：
- 所有显示给用户的文本——包括预览标签、字段名称、确认、状态消息、播放信息、反馈提示、**以及提示词/描述预览**——必须完全翻译成用户的语言。
- 发送到模型的 API 提示词应始终使用英语编写，以获得最佳生成质量。但是，在向用户预览提示词时，应显示用户语言的本地化描述，而不是原始英语提示词。英语提示词是内部实现细节——用户不需要看到它。
- 以下模板用英语编写，仅作参考。在运行时，将每个标签和消息翻译成用户的检测语言。

**歌词语言规则**：
- 默认歌词语言 = 用户的语言。说中文的用户获得中文歌词；说英语的用户获得英语歌词。
- 只有在用户**明确**要求时才生成不同语言的歌词。
- 当需要不同语言的歌词时，将其自然地嵌入到提示词中的声乐或流派描述中。例如，不要追加“带有韩语歌词”，而是使用“ featuring 韩语女歌手”或指定暗示语言的流派（例如，“K-pop”、“J-rock”、“Mandopop”、“拉丁流行”）。

---

## 工作流程

### 第 0 步：检测意图

解析用户的消息以确定：

1. **歌曲类别**：带歌词的声乐、无歌词的纯音乐或翻唱
2. **创作模式偏好**：他们是否提供了详细的要求（高级）还是随意的简短描述（基础）？

如果模糊不清，请使用此决策树提问：

```
Q1: 音乐类型是什么？
  - 带歌词的声乐
  - 无歌词的纯音乐
  - 翻唱

Q2: 创作模式？
  - 基础——一句话描述，自动生成
  - 高级——编辑歌词，优化提示词，规划
```

如果用户给出清晰的简短描述，如“给我做一个悲伤的钢琴曲”，则跳过问题——推断纯音乐 + 基础模式并继续。

---

### 第 1 步：基础模式

**目标**：用户提供简短描述，技能自动生成所有内容，然后调用 API。

1. **将描述扩展为提示词**：将用户的简短描述扩展为丰富的音乐提示词。参考文档末尾的 **提示词编写指南** 以获取风格词汇、流派/乐器参考和提示词结构。
   **API 提示词应始终使用英语编写**，以获得最佳生成质量，无论用户的语言是什么。
   
   遵循此模式：
   ```
   一首 [心情] [BPM 可选] [流派] 歌曲，由 [声乐描述] 表现，
   关于 [叙事/主题]，[氛围]，[关键乐器和制作]。
   ```

2. **在生成之前向用户显示预览**。将所有标签和提示词描述翻译成用户的语言。英语提示词仅在调用 API 时使用——用户不应看到它。示例模板（英语参考——在运行时本地化所有内容）：

   ```
   即将生成：
   类型：声乐 / 纯音乐
   描述：独立民谣，忧郁，原声吉他，温柔女声
   歌词：自动生成 (--lyrics-optimizer)
   
   确认？（按回车确认，或告诉我如何修改）
   ```

3. **调用 mmx**：直接生成音乐。

---

### 第 2 步：高级控制模式

**目标**：用户在生成之前可以完全控制每个参数。

1. **歌词阶段**：
   - 如果用户提供了歌词：使用段落标记格式化显示，询问是否需要编辑。
     最终歌词将通过 `--lyrics` 传递给 mmx。
   - 如果用户有主题但没有歌词：将使用 `--lyrics-optimizer` 自动生成。
   - 支持迭代编辑："修改第二段副歌" -> 仅重写该部分。
   - 用户也可以自己编写歌词并通过 `--lyrics` 传递。

2. **提示词阶段**：
   - 根据歌词的心情和内容生成推荐的提示词。
   - 将其作为用户可以添加/删除/修改的可编辑标签呈现。
   - 参考 **提示词编写指南** 获取完整词汇。

3. **高级规划**（可选，但不要强制）：
   - 歌曲结构：主歌-副歌-主歌-副歌-桥段-副歌 或自定义
   - BPM 建议（在提示词中作为速度描述编码）
   - 参考风格："类似 X 风格" -> 映射到提示词标签
   - 声乐角色描述

4. **最终确认**：显示完整的参数摘要，然后生成。

---

### 第 3 步：调用 mmx

使用 `mmx` 命令行工具生成音乐：

**带自动生成歌词的声乐：**
```bash
mmx music generate \
  --prompt "<prompt>" \
  --lyrics-optimizer \
  --genre "<genre>" --mood "<mood>" --vocals "<vocal style>" \
  --instruments "<instruments>" --bpm <bpm> \
  --out ~/Music/minimax-gen/<filename>.mp3 \
  --quiet --non-interactive
```

**带用户提供的歌词的声乐：**
```bash
mmx music generate \
  --prompt "<prompt>" \
  --lyrics "<带段落标记的歌词>" \
  --genre "<genre>" --mood "<mood>" --vocals "<vocal style>" \
  --out ~/Music/minimax-gen/<filename>.mp3 \
  --quiet --non-interactive
```

**纯音乐（无声乐）：**
```bash
mmx music generate \
  --prompt "<prompt>" \
  --instrumental \
  --genre "<genre>" --mood "<mood>" --instruments "<instruments>" \
  --out ~/Music/minimax-gen/<filename>.mp3 \
  --quiet --non-interactive
```

使用结构化标志（`--genre`、`--mood`、`--vocals`、`--instruments`、`--bpm`、`--key`、`--tempo`、`--structure`、`--references`、`--avoid`、`--use-case`）来为 API 提供细粒度控制，而不是将所有内容都嵌入到 `--prompt` 中。

等待时显示进度指示器。典型生成时间需要 30-120 秒。

---

### 第 4 步：播放

生成后，检测可用的音频播放器并播放文件。

**检测播放器：**
```bash
command -v mpv || command -v ffplay || command -v afplay
```

**根据检测到的播放器播放（优先级顺序）：**

| 播放器 | 命令 | 控制 |
|--------|------|------|
| `mpv`（首选） | `mpv --no-video ~/Music/minimax-gen/<filename>.mp3` | 空格 = 暂停/继续，q = 退出，左右 = 跳转 |
| `ffplay` | `ffplay -nodisp -autoexit ~/Music/minimax-gen/<filename>.mp3` | q = 退出 |
| `afplay`（macOS） | `afplay ~/Music/minimax-gen/<filename>.mp3` | Ctrl+C = 停止 |
| 未找到 | 不尝试播放 | 仅显示文件路径 |

开始播放后，向用户说明（本地化所有文本）：

```
正在播放：<filename>.mp3
保存到：~/Music/minimax-gen/<filename>.mp3
```

**不要显示播放控制（例如键盘快捷键）**——它们在这个环境中不起作用，因为播放器在后台运行。

如果未检测到播放器（本地化所有文本）：

```
未检测到音频播放器。
文件保存到：~/Music/minimax-gen/<filename>.mp3
提示：安装 mpv 以获得最佳播放体验（brew install mpv）。
```

---

### 第 5 步：反馈与迭代

播放后，询问反馈：

```
这首歌怎么样？
  1. 很喜欢，保留
  2. 不太满意，调整后重新生成
  3. 微调歌词/风格后重新生成
  4. 不想要，重新开始
```

根据反馈：
- **满意**：完成。再次提及文件路径。
- **调整后重新生成**：询问要更改什么（提示词？歌词？风格？），应用编辑，重新运行生成。保留旧文件并添加 `_v1` 后缀以供比较。
- **微调**：进入高级控制模式，预填充当前参数。
- **删除并重新开始**：删除文件，返回第 0 步。

---

## 翻唱模式

根据参考音频生成歌曲的翻唱版本。模型：`music-cover-free`。

**参考音频要求**：mp3、wav、flac——时长 6 秒至 6 分钟，最大 50MB。
如果没有提供歌词，将通过 ASR 自动提取原始歌词。

### 工作流程

当用户选择翻唱模式时：
1. 询问源音频——本地文件路径或 URL
2. 询问目标翻唱风格（例如，“原声翻唱，简化版，亲密声乐”）
3. 可选地询问自定义歌词或歌词文件

### 命令

**从本地文件翻唱：**
```bash
mmx music cover \
  --prompt "<翻唱风格描述>" \
  --audio-file <source.mp3> \
  --out ~/Music/minimax-gen/<filename>.mp3 \
  --quiet --non-interactive
```

**从 URL 翻唱：**
```bash
mmx music cover \
  --prompt "<风格描述>" \
  --audio <source_url> \
  --out ~/Music/minimax-gen/<filename>.mp3 \
  --quiet --non-interactive
```

**带自定义歌词（文本）：**
```bash
mmx music cover \
  --prompt "<风格>" \
  --audio-file <source.mp3> \
  --lyrics "<自定义歌词>" \
  --out ~/Music/minimax-gen/<filename>.mp3 \
  --quiet --non-interactive
```

**带自定义歌词（文件）：**
```bash
mmx music cover \
  --prompt "<风格>" \
  --audio-file <source.mp3> \
  --lyrics-file <lyrics.txt> \
  --out ~/Music/minimax-gen/<filename>.mp3 \
  --quiet --non-interactive
```

### 可选标志

| 标志 | 描述 |
|------|------|
| `--seed <number>` | 随机种子 0-1000000 以获得可重复结果 |
| `--channel <n>` | `1`（单声道）或 `2`（立体声，默认） |
| `--format <fmt>` | `mp3`（默认），`wav`，`pcm` |
| `--sample-rate <hz>` | 采样率（默认：44100） |
| `--bitrate <bps>` | 比特率（默认：256000） |

### 生成后
执行正常的播放和反馈流程（第 4 步 & 5 步）。

---

## 错误处理

| 错误 | 操作 |
|------|------|
| mmx 未找到 | `npm install -g mmx-cli` |
| mmx 认证错误（退出码 3） | `mmx auth login` |
| 配额超出（退出码 4） | 报告配额限制，建议等待或升级 |
| API 超时（退出码 5） | 重试一次，然后报告失败 |
| 内容过滤器（退出码 10） | 调整提示词以避免过滤内容 |
| 歌词格式无效 | 自动修复段落标记，警告用户 |
| 未找到音频播放器 | 保存文件并告知用户路径，建议安装 mpv |
| 网络错误 | 显示错误详情，建议检查连接 |

---

## 重要提示

- **切勿重复受版权保护的歌词。** 在进行翻唱时，始终根据歌曲主题创作原创歌词。向用户解释这一点。
- **提示词语言**：API 提示词使用英语标签效果最佳。中文标签也接受。混合使用是允许的。
- **歌词中的段落标记**：API 识别 `[verse]`、`[chorus]`、`[bridge]`、`[outro]`、`[intro]`。提供 `--lyrics` 时始终包含它们。
- **文件管理**：如果 `~/Music/minimax-gen/` 中文件超过 50 个，在开始新会话时建议清理。
- **结构化参数**：优先使用 `--genre`、`--mood`、`--vocals`、`--instruments`、`--bpm` 等，而不是将所有内容嵌入到 `--prompt` 中。这为 API 提供了更好的控制。
- **通过风格指定歌词语言**：当用户希望特定语言的歌词时，通过声乐描述或流派表达（例如，“日语女歌手”、“Mandopop 球谣”）而不是在提示词中追加语言指令。

---

## 附录：提示词编写指南

参考 [references/prompt_guide.md](references/prompt_guide.md) 获取完整的提示词编写指南，包括流派/声乐/乐器参考和 BPM 表格。
