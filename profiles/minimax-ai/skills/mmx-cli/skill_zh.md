# MiniMax CLI — Agent Skill Guide

使用 `mmx` 通过 MiniMax AI 平台生成文本、图像、视频、语音、音乐，并执行网络搜索。

## 前置条件

```bash
# 安装
npm install -g mmx-cli

# 认证（持久化到 ~/.mmx/credentials.json）
mmx auth login --api-key sk-xxxxx

# 或者每次调用时传递
mmx text chat --api-key sk-xxxxx --message "Hello"
```

区域自动检测。使用 `--region global` 或 `--region cn` 覆盖。

---

## Agent 标志

在非交互式（agent/CI）上下文中始终使用这些标志：

| 标志 | 目的 |
|---|---|
| `--non-interactive` | 缺少参数时快速失败，而不是提示 |
| `--quiet` | 抑制旋转器/进度条；stdout 是纯数据 |
| `--output json` | 机器可读的 JSON 输出 |
| `--async` | 返回任务 ID（视频生成） |
| `--dry-run` | 预览 API 请求而不执行 |
| `--yes` | 跳过确认提示 |

---

## 命令

### text chat

聊天补全。默认模型：`MiniMax-M2.7`。

```bash
mmx text chat --message <text> [flags]
```

| 标志 | 类型 | 描述 |
|---|---|---|
| `--message <text>` | 字符串，**必需**，可重复 | 消息文本。使用 `role:` 前缀设置角色（例如 `"system:You are helpful"`，`"user:Hello"`） |
| `--messages-file <path>` | 字符串 | 包含消息数组的 JSON 文件。使用 `-` 表示 stdin |
| `--system <text>` | 字符串 | 系统提示 |
| `--model <model>` | 字符串 | 模型 ID（默认：`MiniMax-M2.7`） |
| `--max-tokens <n>` | 数字 | 最大 token 数（默认：4096） |
| `--temperature <n>` | 数字 | 采样温度（0.0，1.0] |
| `--top-p <n>` | 数字 | 核心采样阈值 |
| `--stream` | 布尔值 | 流 token（TTY 中默认开启） |
| `--tool <json-or-path>` | 字符串，可重复 | 工具定义 JSON 或文件路径 |

```bash
# 单条消息
mmx text chat --message "user:What is MiniMax?" --output json --quiet

# 多轮对话
mmx text chat \
  --system "You are a coding assistant." \
  --message "user:Write fizzbuzz in Python" \
  --output json

# 从文件
cat conversation.json | mmx text chat --messages-file - --output json
```

**stdout**: 响应文本（文本模式）或完整响应对象（json 模式）。

---

### image generate

生成图像。模型：`image-01`。

```bash
mmx image generate --prompt <text> [flags]
```

| 标志 | 类型 | 描述 |
|---|---|---|
| `--prompt <text>` | 字符串，**必需** | 图像描述 |
| `--aspect-ratio <ratio>` | 字符串 | 例如 `16:9`，`1:1` |
| `--n <count>` | 数字 | 图像数量（默认：1） |
| `--subject-ref <params>` | 字符串 | 主体参考：`type=character,image=path-or-url` |
| `--out-dir <dir>` | 字符串 | 下载图像到目录 |
| `--out-prefix <prefix>` | 字符串 | 文件名前缀（默认：`image`） |

```bash
mmx image generate --prompt "A cat in a spacesuit" --output json --quiet
# stdout: 图像 URL（安静模式下每行一个）

mmx image generate --prompt "Logo" --n 3 --out-dir ./gen/ --quiet
# stdout: 保存的文件路径（每行一个）
```

---

### video generate

生成视频。默认模型：`MiniMax-Hailuo-2.3`。这是一个异步任务——默认情况下它会轮询直到完成。

```bash
mmx video generate --prompt <text> [flags]
```

| 标志 | 类型 | 描述 |
|---|---|---|
| `--prompt <text>` | 字符串，**必需** | 视频描述 |
| `--model <model>` | 字符串 | `MiniMax-Hailuo-2.3`（默认）或 `MiniMax-Hailuo-2.3-Fast` |
| `--first-frame <path-or-url>` | 字符串 | 第一帧图像 |
| `--callback-url <url>` | 字符串 | 完成时的 webhook URL |
| `--download <path>` | 字符串 | 保存视频到特定文件 |
| `--async` | 布尔值 | 立即返回任务 ID |
| `--no-wait` | 布尔值 | 与 `--async` 相同 |
| `--poll-interval <seconds>` | 数字 | 轮询间隔（默认：5） |

```bash
# 非阻塞：获取任务 ID
mmx video generate --prompt "A robot." --async --quiet
# stdout: {"taskId":"..."}

# 阻塞：等待并获取文件路径
mmx video generate --prompt "Ocean waves." --download ocean.mp4 --quiet
# stdout: ocean.mp4
```

### video task get

查询视频生成任务的状态。

```bash
mmx video task get --task-id <id> [--output json]
```

### video download

通过任务 ID 下载完成的视频。

```bash
mmx video download --file-id <id> [--out <path>]
```

---

### speech synthesize

文本转语音。默认模型：`speech-2.8-hd`。最多 10k 字符。

```bash
mmx speech synthesize --text <text> [flags]
```

| 标志 | 类型 | 描述 |
|---|---|---|
| `--text <text>` | 字符串 | 要合成的文本 |
| `--text-file <path>` | 字符串 | 从文件读取文本。使用 `-` 表示 stdin |
| `--model <model>` | 字符串 | `speech-2.8-hd`（默认），`speech-2.6`，`speech-02` |
| `--voice <id>` | 字符串 | 语音 ID（默认：`English_expressive_narrator`） |
| `--speed <n>` | 数字 | 速度倍数 |
| `--volume <n>` | 数字 | 音量级别 |
| `--pitch <n>` | 数字 | 音调调整 |
| `--format <fmt>` | 字符串 | 音频格式（默认：`mp3`） |
| `--sample-rate <hz>` | 数字 | 采样率（默认：32000） |
| `--bitrate <bps>` | 数字 | 比特率（默认：128000） |
| `--channels <n>` | 数字 | 音频通道（默认：1） |
| `--language <code>` | 字符串 | 语言增强 |
| `--subtitles` | 布尔值 | 包含字幕时间数据 |
| `--pronunciation <from/to>` | 字符串，可重复 | 自定义发音 |
| `--sound-effect <effect>` | 字符串 | 添加音效 |
| `--out <path>` | 字符串 | 保存音频到文件 |
| `--stream` | 布尔值 | 将原始音频流到 stdout |

```bash
mmx speech synthesize --text "Hello world" --out hello.mp3 --quiet
# stdout: hello.mp3

echo "Breaking news." | mmx speech synthesize --text-file - --out news.mp3
```

---

### music generate

生成音乐。模型：`music-2.5`。对丰富、结构化的描述反应良好。

```bash
mmx music generate --prompt <text> [--lyrics <text>] [flags]
```

| 标志 | 类型 | 描述 |
|---|---|---|
| `--prompt <text>` | 字符串 | 音乐风格描述（可以详细） |
| `--lyrics <text>` | 字符串 | 带有结构标签的歌曲歌词。使用 `"\u65e0\u6b4c\u8bcd"` 表示纯音乐。不能与 `--instrumental` 一起使用 |
| `--lyrics-file <path>` | 字符串 | 从文件读取歌词。使用 `-` 表示 stdin |
| `--vocals <text>` | 字符串 | 人声风格，例如 `"warm male baritone"`，`"bright female soprano"`，`"duet with harmonies"` |
| `--genre <text>` | 字符串 | 音乐流派，例如 folk，pop，jazz |
| `--mood <text>` | 字符串 | 情绪或心情，例如 warm，melancholic，uplifting |
| `--instruments <text>` | 字符串 | 要包含的乐器，例如 `"acoustic guitar, piano"` |
| `--tempo <text>` | 字符串 | 速度描述，例如 fast，slow，moderate |
| `--bpm <number>` | 数字 | 每分钟的节拍数 |
| `--key <text>` | 字符串 | 音乐调性，例如 C major，A minor，G sharp |
| `--avoid <text>` | 字符串 | 生成的音乐中要避免的元素 |
| `--use-case <text>` | 字符串 | 用例上下文，例如 `"background music for video"`，`"theme song"` |
| `--structure <text>` | 字符串 | 歌曲结构，例如 `"verse-chorus-verse-bridge-chorus"` |
| `--references <text>` | 字符串 | 参考曲目或艺术家，例如 `"similar to Ed Sheeran"` |
| `--extra <text>` | 字符串 | 额外的细粒度要求 |
| `--instrumental` | 布尔值 | 生成纯音乐（无人声）。不能与 `--lyrics` 或 `--lyrics-file` 一起使用 |
| `--aigc-watermark` | 布尔值 | 嵌入 AI 生成内容水印 |
| `--format <fmt>` | 字符串 | 音频格式（默认：`mp3`） |
| `--sample-rate <hz>` | 数字 | 采样率（默认：44100） |
| `--bitrate <bps>` | 数字 | 比特率（默认：256000） |
| `--out <path>` | 字符串 | 保存音频到文件 |
| `--stream` | 布尔值 | 将原始音频流到 stdout |

至少需要 `--prompt` 或 `--lyrics` 中的一个。

```bash
# 简单用法
mmx music generate --prompt "Upbeat pop" --lyrics "La la la..." --out song.mp3 --quiet

# 带人声特征的详细提示
mmx music generate --prompt "Warm morning folk" \
  --vocals "male and female duet, harmonies in chorus" \
  --instruments "acoustic guitar, piano" \
  --bpm 95 \
  --lyrics-file song.txt \
  --out duet.mp3

# 纯音乐（使用 --instrumental 标志）
mmx music generate --prompt "Cinematic orchestral, building tension" --instrumental --out bgm.mp3
```

---

### vision describe

通过 VLM 进行图像理解。提供 `--image` 或 `--file-id`，不能同时提供。

```bash
mmx vision describe (--image <path-or-url> | --file-id <id>) [flags]
```

| 标志 | 类型 | 描述 |
|---|---|---|
| `--image <path-or-url>` | 字符串 | 本地路径或 URL（自动 base64 编码） |
| `--file-id <id>` | 字符串 | 预上传文件 ID（跳过 base64） |
| `--prompt <text>` | 字符串 | 关于图像的问题（默认：`"Describe the image."`） |

```bash
mmx vision describe --image photo.jpg --prompt "What breed?" --output json
```

**stdout**: 描述文本（文本模式）或完整响应（json 模式）。

---

### search query

通过 MiniMax 进行网络搜索。

```bash
mmx search query --q <query>
```

| 标志 | 类型 | 描述 |
|---|---|---|
| `--q <query>` | 字符串，**必需** | 搜索查询 |

```bash
mmx search query --q "MiniMax AI" --output json --quiet
```

---

### quota show

显示 Token 计划使用情况和剩余配额。

```bash
mmx quota show [--output json]
```

---

## Tool Schema 导出

导出所有命令为 Anthropic/OpenAI 兼容的 JSON 工具模式：

```bash
# 所有值得导出的命令（排除 auth/config/update）
mmx config export-schema

# 单个命令
mmx config export-schema --command "video generate"
```

使用此功能将 mmx 命令动态注册为 agent 框架中的工具。

---

## 退出代码

| 代码 | 含义 |
|---|---|
| 0 | 成功 |
| 1 | 一般错误 |
| 2 | 使用错误（错误的标志，缺少参数） |
| 3 | 认证错误 |
| 4 | 配额超出 |
| 5 | 超时 |
| 10 | 内容过滤器触发 |

---

## 管道模式

```bash
# stdout 始终是干净的数据——可以安全地管道
mmx text chat --message "Hi" --output json | jq '.content'

# stderr 包含进度/旋转器——如果需要则丢弃
mmx video generate --prompt "Waves" 2>/dev/null

# 链接：生成图像 → 描述它
URL=$(mmx image generate --prompt "A sunset" --quiet)
mmx vision describe --image "$URL" --quiet

# 异步视频工作流
TASK=$(mmx video generate --prompt "A robot" --async --quiet | jq -r '.taskId')
mmx video task get --task-id "$TASK" --output json
mmx video download --task-id "$TASK" --out robot.mp4
```

---

## 配置优先级

CLI 标志 → 环境变量 → `~/.mmx/config.json` → 默认值。

```bash
# 持久化配置
mmx config set --key region --value cn
mmx config show

# 环境变量
export MINIMAX_API_KEY=sk-xxxxx
export MINIMAX_REGION=cn
```
