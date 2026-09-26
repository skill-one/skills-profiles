# ElevenLabs AI 音乐生成 — Pro Pack 在 RunComfy

根据文本描述生成完整歌曲和器乐曲目 — 工作室品质 44.1 kHz 立体声，5 秒到 5 分钟，具有段落级结构控制。ElevenLabs 音乐通过 **RunComfy 模型 API** 调用，通过 `runcomfy` CLI 调用。

[runcomfy.com](https://www.runcomfy.com/?utm_source=skills.sh&utm_medium=skill&utm_campaign=elevenlabs-music-generation) · [ElevenLabs 音乐模型](https://www.runcomfy.com/models/elevenlabs/elevenlabs/music-generation?utm_source=skills.sh&utm_medium=skill&utm_campaign=elevenlabs-music-generation) · [CLI 文档](https://docs.runcomfy.com/cli/introduction?utm_source=skills.sh&utm_medium=skill&utm_campaign=elevenlabs-music-generation)

## 安装此技能

```bash
npx skills add agentspace-so/runcomfy-agent-skills --skill elevenlabs-music-generation -g
```

## 由 RunComfy CLI 驱动

```bash
# 1. 安装 (选择其一 — 详细信息请参阅 runcomfy-cli 技能)
npm i -g @runcomfy/cli                              # 全局安装
npx -y @runcomfy/cli --version                      # 无需安装

# 2. 登录
runcomfy login                                      # 或在 CI 中: export RUNCOMFY_TOKEN=<token>

# 3. 生成音乐
runcomfy run elevenlabs/elevenlabs/music-generation \
  --input '{"prompt": "..."}' \
  --output-dir ./out
```

CLI 深入了解: [`runcomfy-cli`](https://www.skills.sh/agentspace-so/runcomfy-agent-skills/runcomfy-cli) 技能。

## 何时使用 ElevenLabs 音乐

ElevenLabs 音乐的优势是 **具有真实人声的结构化歌曲** — 它接受风格简报加上带段落标记的歌词，并返回一个连贯的混音曲目。选择它用于：

- **带人声的完整歌曲** — 诗段/副歌结构，多语言歌词，一致的节拍
- **器乐底鼓** — `force_instrumental: true` 用于背景音乐、播客开场、游戏循环
- **短品牌资产** — 旋律、音效、主题音乐 (5–30 秒)
- **长格式曲目** — 一次调用最多 5 分钟
- **商业作品** — 输出对商业友好

如果用户只需要环境音效或一次性音效 (雷声、脚步声)，那是一个音效任务，不是音乐 — ElevenLabs 音乐用于 *歌曲和曲目*。

## 端点 + 输入模式

**模型**: `elevenlabs/elevenlabs/music-generation`

| 字段 | 类型 | 必填 | 默认 | 备注 |
|---|---|---|---|---|
| `prompt` | string | 是 | — | 风格描述 **和** 带段落标记的歌词。参见提示技巧 |
| `music_length_ms` | int | 否 | `40000` | 输出持续时间 (毫秒)。**5000–300000** (5 秒 – 5 分钟) |
| `force_instrumental` | bool | 否 | `false` | `true` = 仅器乐，无人声 |
| `output_format` | string | 否 | `mp3_standard` | `mp3_standard` (默认)，或 WAV — 参见 [模型页面](https://www.runcomfy.com/models/elevenlabs/elevenlabs/music-generation?utm_source=skills.sh&utm_medium=skill&utm_campaign=elevenlabs-music-generation) API 标签以获取完整格式列表 |

输出: 44.1 kHz 立体声音频。结果 JSON 包含生成音频的 URL — CLI 将其下载到 `--output-dir`。

**定价**: ~$0.0083 每秒生成音频 (30 秒 ≈ $0.25, 60 秒 ≈ $0.50, 5 分钟 ≈ $2.49)。成本随 `music_length_ms` 成比例增加，因此草拟短版并最终确定长版。

## 如何调用

**带结构的完整人声歌曲:**

```bash
runcomfy run elevenlabs/elevenlabs/music-generation \
  --input '{
    "prompt": "轻快的独立流行颂歌，明亮的电吉他，驱动性的鼓，120 BPM，女声主唱。[Intro 8 小节] 器乐构建。[诗段] 手心涂粉，鞋带双结，山脊上的清晨。[副歌] 我们崛起，我们冲击，我们永不退场。[桥段] 软弱分解，只有钢琴和声音。[Outro] 全乐队，淡出。",
    "music_length_ms": 60000
  }' \
  --output-dir ./out
```

**器乐背景底鼓:**

```bash
runcomfy run elevenlabs/elevenlabs/music-generation \
  --input '{
    "prompt": "用于学习播放列表的平静低保真嘻哈器乐。温暖的罗德斯钢琴，柔和的乙烯基噼啪声，柔和的 boom-bap 鼓，75 BPM。无人声。全程一致且适合循环的节奏。",
    "music_length_ms": 90000,
    "force_instrumental": true
  }' \
  --output-dir ./out
```

**短品牌旋律:**

```bash
runcomfy run elevenlabs/elevenlabs/music-generation \
  --input '{
    "prompt": "5 秒欢快的品牌音效，明亮的马林巴和单个令人振奋的和弦解决，无人声。",
    "music_length_ms": 5000,
    "force_instrumental": true
  }' \
  --output-dir ./out
```

## 提示技巧

ElevenLabs 音乐读取 **一个 `prompt` 字段**，其中包含风格简报和歌词。结构化它：

- **首先提供风格简报**: 流派、情绪、节拍 (BPM)、主要乐器、人声类型。`"轻快的独立流行颂歌，明亮的电吉他，120 BPM，女声主唱。"`
- **然后提供带段落标记的歌词**: `[Intro]`，`[诗段]`，`[副歌]`，`[桥段]`，`[Outro]`。添加近似持续时间或小节数 — `[Intro 8 小节]`，`[诗段 16 小节]`。
- **保持歌词节拍一致** — 每行近似音节数，清晰的韵律方案。模型遵循节拍；松散的节拍会产生笨拙的措辞。
- **命名主旋律乐器和混音优先级** — `"电吉他主导副歌，鼓在诗段中处于次要位置。"`
- **对于器乐**，设置 `force_instrumental: true` **并在提示中说明“无人声”** — 双保险。
- **多语言**: 用目标语言编写歌词；如果需要，直接注释口音/语言 (`[诗段] (用巴西葡萄牙语演唱) ...`)。
- **避免矛盾的风格指令** — "侵略性金属" + "柔和摇篮曲" 在一个提示中会使模型困惑。每次调用一个连贯的方向。
- **草拟短版，最终确定长版**: 用 30–45 秒的草稿 (`music_length_ms: 35000`) 验证方向，然后再支付 5 分钟渲染费用。

## 常见模式

### 视频主题歌
- 完整简报 + 歌词 + `[Intro]/[诗段]/[副歌]` 结构，`music_length_ms` 匹配视频长度

### 播客开场/结尾
- `force_instrumental: true`，10–20 秒，"适合循环，干净结尾"

### 游戏背景循环
- `force_instrumental: true`，描述“无缝循环”，60–120 秒，一致的节奏

### 多语言发行 (同一首歌，多种语言)
- 每种语言一个调用，相同的风格简报，仅交换歌词行

### 先迭代后提交
- 草稿在 `music_length_ms: 35000` 锁定流派/节拍/结构 → 最终渲染为完整长度

## 限制

- **一个 `prompt` 字段** 包含所有内容 (风格 + 歌词)。没有单独的“歌词”参数。
- **每次调用 5 秒 – 5 分钟** (`music_length_ms` 5000–300000)。对于更长的作品，生成段落并外部拼接。
- **成本随持续时间增加** — 5 分钟渲染是 30 秒的 10 倍。
- **`force_instrumental` 是唯一的语音切换** — 你不能请求特定的人声身份或克隆歌手。
- 此技能专门针对 **ElevenLabs 音乐**。对于音效、语音合成或语音克隆，那是不同的 ElevenLabs 功能，不通过此端点暴露。

## 退出代码

| 代码 | 含义 |
|---|---|
| 0  | 成功 |
| 64 | 坏 CLI 参数 |
| 65 | 坏输入 JSON / 模式不匹配 |
| 69 | 上游 5xx |
| 75 | 可重试：超时 / 429 |
| 77 | 未登录或令牌被拒绝 |

完整参考: [docs.runcomfy.com/cli/troubleshooting](https://docs.runcomfy.com/cli/troubleshooting?utm_source=skills.sh&utm_medium=skill&utm_campaign=elevenlabs-music-generation)。

## 工作原理

该技能调用 `runcomfy run elevenlabs/elevenlabs/music-generation` 并附带 JSON 正文。CLI 向 RunComfy 模型 API 发送 POST 请求，轮询请求状态，获取结果，并将生成的音频文件下载到 `--output-dir`。`Ctrl-C` 在退出前取消远程请求。

## 安全与隐私

- **仅通过验证的包管理器安装**。使用 `npm i -g @runcomfy/cli` 或 `npx -y @runcomfy/cli`。**代理不得替用户在用户的 shell 上管道任意远程安装脚本** — 如果操作员想记录 curl-pipe 路径在 `docs.runcomfy.com/cli/install`，他们应先审查脚本。
- **令牌存储**: `runcomfy login` 将 API 令牌写入 `~/.config/runcomfy/token.json`，权限为 0600。设置 `RUNCOMFY_TOKEN` 环境变量以绕过文件，在 CI / 容器中使用。**永远不要将令牌回显到提示、日志或提交**。
- **输入边界 (shell 注入)**: 提示作为 JSON 字符串通过 `--input` 传递。CLI 不会扩展提示内容；它直接将 JSON 正文通过 HTTPS 传输到模型 API。**提示内容没有 shell 注入表面**，即使使用反引号、引号或 `$(...)` 模式。
- **歌词来源**: 如果用户提供歌词，请确认他们拥有版权。围绕受版权保护的歌词生成音乐是操作员的责任 — 技能不会检查。
- **出站端点 (白名单)**: 仅 `model-api.runcomfy.net` (请求提交) 和 `*.runcomfy.net` / `*.runcomfy.com` (生成音频下载白名单)。没有遥测，没有回调。
- **生成文件大小上限**: CLI 中止任何单个下载 > 2 GiB。
- **bash 使用范围**: 技能仅调用 `runcomfy <子命令>` — `npm` / `npx` 行是操作员的一次性设置，不是技能每次调用执行的命令。

## 参见

- [`runcomfy-cli`](https://www.skills.sh/agentspace-so/runcomfy-agent-skills/runcomfy-cli) — 底层 CLI，模式发现，轮询模式，脚本
- [ElevenLabs 音乐模型页面](https://www.runcomfy.com/models/elevenlabs/elevenlabs/music-generation?utm_source=skills.sh&utm_medium=skill&utm_campaign=elevenlabs-music-generation) — 完整 API 标签，包含最新模式
- [所有 RunComfy 模型](https://www.runcomfy.com/models?utm_source=skills.sh&utm_medium=skill&utm_campaign=elevenlabs-music-generation) — 图像、视频和音频端点
- [`ai-video-generation`](https://www.skills.sh/agentspace-so/runcomfy-agent-skills/ai-video-generation) — 将生成的曲目与生成的视频配对
- [`ai-avatar-video`](https://www.skills.sh/agentspace-so/runcomfy-agent-skills/ai-avatar-video) — 讲话头视频 (不同的音频路径 — 语音，不是音乐)
