# YouTube 转录文本

从 YouTube 视频下载转录文本（字幕/旁白）。支持手动创建和自动生成的转录文本。无需 API 密钥或浏览器 — 直接使用 YouTube 的 InnerTube API，并在 YouTube 阻止直接 API 路径时自动回退到 `yt-dlp`。

首次运行时获取视频元数据和封面图片，缓存原始数据以快速重新格式化。

## 脚本目录

位于 `scripts/` 子目录中。`{baseDir}` = 此 SKILL.md 的目录路径。解析 `${BUN_X}` 运行时：如果安装了 `bun` → `bun`；如果可用 `npx` → `npx -y bun`；否则建议安装 bun。将 `{baseDir}` 和 `${BUN_X}` 替换为实际值。

| 脚本 | 目的 |
|------|------|
| `scripts/main.ts` | 转录文本下载 CLI |

## 使用方法

```bash
# 默认：带时间戳的 markdown（英文）
${BUN_X} {baseDir}/scripts/main.ts <youtube-url-or-id>

# 指定语言（优先顺序）
${BUN_X} {baseDir}/scripts/main.ts <url> --languages zh,en,ja

# 无时间戳
${BUN_X} {baseDir}/scripts/main.ts <url> --no-timestamps

# 带章节划分
${BUN_X} {baseDir}/scripts/main.ts <url> --chapters

# 带发言人识别（需要 AI 后处理）
${BUN_X} {baseDir}/scripts/main.ts <url> --speakers

# SRT 字幕文件
${BUN_X} {baseDir}/scripts/main.ts <url> --format srt

# 翻译转录文本
${BUN_X} {baseDir}/scripts/main.ts <url> --translate zh-Hans

# 列出可用转录文本
${BUN_X} {baseDir}/scripts/main.ts <url> --list

# 强制重新获取（忽略缓存）
${BUN_X} {baseDir}/scripts/main.ts <url> --refresh
```

## 选项

| 选项 | 描述 | 默认值 |
|------|------|--------|
| `<url-or-id>` | YouTube URL 或视频 ID（允许多个） | 必填 |
| `--languages <codes>` | 语言代码，逗号分隔，按优先顺序排列 | `en` |
| `--format <fmt>` | 输出格式：`text`，`srt` | `text` |
| `--translate <code>` | 翻译到指定语言代码 | 无 |
| `--list` | 列出可用转录文本而不是获取 | 无 |
| `--timestamps` | 包含 `[HH:MM:SS → HH:MM:SS]` 每段的时间戳 | 开启 |
| `--no-timestamps` | 禁用时间戳 | 无 |
| `--chapters` | 从视频描述中划分章节 | 无 |
| `--speakers` | 带元数据的原始转录文本用于发言人识别 | 无 |
| `--exclude-generated` | 跳过自动生成的转录文本 | 无 |
| `--exclude-manually-created` | 跳过手动创建的转录文本 | 无 |
| `--refresh` | 强制重新获取，忽略缓存数据 | 无 |
| `-o, --output <path>` | 保存到特定文件路径 | 自动生成 |
| `--output-dir <dir>` | 基础输出目录 | `youtube-transcript` |

## 可选环境变量

| 变量 | 描述 |
|------|------|
| `YOUTUBE_TRANSCRIPT_COOKIES_FROM_BROWSER` | 传递给 `yt-dlp --cookies-from-browser` 在回退时使用，例如 `chrome`，`safari`，`firefox`，或 `chrome:Profile 1` |

## 输入格式

接受以下任何一种作为视频输入：
- 完整 URL：`https://www.youtube.com/watch?v=dQw4w9WgXcQ`
- 短 URL：`https://youtu.be/dQw4w9WgXcQ`
- 嵌入 URL：`https://www.youtube.com/embed/dQw4w9WgXcQ`
- Shorts URL：`https://www.youtube.com/shorts/dQw4w9WgXcQ`
- 视频ID：`dQw4w9WgXcQ`

## 输出格式

| 格式 | 扩展名 | 描述 |
|------|--------|------|
| `text` | `.md` | 带 frontmatter（包括 `description`），标题标题，摘要，可选的 TOC/封面/时间戳/章节/发言人识别的 Markdown |
| `srt` | `.srt` | 视频播放器使用的 SubRip 字幕格式 |

## 输出目录

```
youtube-transcript/
├── .index.json                          # 视频ID → 目录路径映射（用于缓存查找）
└── {channel-slug}/{title-full-slug}/
    ├── meta.json                        # 视频元数据（标题，频道，描述，时长，章节等）
    ├── transcript-raw.json              # 来自 YouTube API 的原始转录片段（缓存）
    ├── transcript-sentences.json        # 句子分割的转录文本（按标点符号分割，跨片段合并）
    ├── imgs/
    │   └── cover.jpg                    # 视频缩略图
    ├── transcript.md                    # Markdown 转录文本（从句子生成）
    └── transcript.srt                   # SRT 字幕（从原始片段生成，如果 `--format srt`） |
```

- `{channel-slug}`：频道名（短横线命名）
- `{title-full-slug}`：完整视频标题（短横线命名）

`--list` 模式仅输出到标准输出（不保存文件）。

## 缓存

首次获取时，脚本保存：
- `meta.json` — 视频元数据，章节，封面图片路径，语言信息
- `transcript-raw.json` — 来自 YouTube API 的原始转录片段（`{ text, start, duration }[]`）
- `transcript-sentences.json` — 句子分割的转录文本（`{ text, start: "HH:mm:ss", end: "HH:mm:ss" }[]`），按句子结束标点符号（`.?!…。？！` 等）分割，时间戳按字符长度比例分配，支持 CJK 文本合并
- `imgs/cover.jpg` — 视频缩略图

后续运行相同视频时使用缓存数据（无网络调用）。使用 `--refresh` 强制重新获取。如果请求不同语言，缓存会自动刷新。

当 YouTube 在直接 InnerTube 路径返回反爬虫/阻止响应时，脚本会尝试使用备用客户端身份，如果可用则回退到 `yt-dlp`。如果需要回退但 `yt-dlp` 不可用，代理应自行决定如何使 `yt-dlp` 可用并继续，而不是将安装决策推给用户。

SRT 输出（`--format srt`）从 `transcript-raw.json` 生成。文本/Markdown 输出使用 `transcript-sentences.json` 以实现自然句子边界。

## 工作流程

当用户提供 YouTube URL 并希望获取转录文本时：

1. 如果用户未指定语言，首先使用 `--list` 运行脚本，以显示可用选项
2. **运行脚本时始终使用单引号包裹 URL** — zsh 将 `?` 视为通配符，因此未引用的 YouTube URL 会导致“未找到匹配项”：使用 `'https://www.youtube.com/watch?v=ID'`
3. 默认：使用 `--chapters --speakers` 运行以获取最丰富的输出（章节 + 发言人识别）
4. 脚本自动保存缓存数据 + 输出文件并打印文件路径
5. 对于 `--speakers` 模式：脚本保存原始文件后，请按照以下发言人识别工作流程进行后处理，添加发言人标签

当用户只想获取封面图片或元数据时，运行脚本（带任何选项）也会缓存 `meta.json` 和 `imgs/cover.jpg`。

重新格式化相同视频（例如，先文本后 SRT）时，会复用缓存数据 — 无需重新获取。

## 章节与发言人工作流程

### 章节 (`--chapters`)

脚本从视频描述中解析章节时间戳（例如，`0:00 简介`），按章节边界分割转录文本，将片段分组为可读段落，并保存为 `.md` 文件带目录。无需进一步处理。

如果描述中没有章节时间戳，转录文本将按分组段落输出，无章节标题。

### 发言人识别 (`--speakers`)

发言人识别需要 AI 处理。脚本输出包含以下内容的原始 `.md` 文件：
- 带有视频元数据的 YAML frontmatter（标题，频道，日期，封面，描述，语言）
- 视频描述（用于提取发言人姓名）
- 描述中的章节列表（如果可用）
- 原始 SRT 格式的转录文本（预计算的起始/结束时间戳，高效的标记）

脚本保存原始文件后，启动子代理（使用更便宜的模型如 Sonnet 以提高成本效率）进行发言人识别：

1. 读取保存的 `.md` 文件
2. 读取 `{baseDir}/prompts/speaker-transcript.md` 中的提示模板
3. 按照提示处理原始转录文本：
   - 使用视频元数据（标题 → 嘉宾，频道 → 主持人，描述 → 名称）识别发言人
   - 从对话流程、问答模式和环境线索中检测发言人转换
   - 划分章节（使用描述章节，如果可用，否则从主题转变创建）
   - 使用 `**发言人姓名：**` 标签格式化，段落分组（2-4 句话），带 `[HH:MM:SS → HH:MM:SS]` 时间戳
4. 使用 YAML frontmatter 保留原始文件，覆盖为处理后的转录文本

使用 `--speakers` 时，`--chapters` 被隐含 — 处理后的输出始终包含章节划分。

## 错误情况

| 错误 | 含义 |
|------|------|
| 转录文本禁用 | 视频完全没有字幕 |
| 未找到转录文本 | 请求的语言不可用 |
| 视频不可用 | 视频被删除，私密或区域锁定 |
| IP 被阻止 | 请求过多，稍后再试 |
| 年龄限制 | 视频需要登录进行年龄验证 |
| 检测到机器人 | 脚本尝试备用客户端，然后 `yt-dlp`；如果回退工具缺失，代理应自行解决，否则如果仍然失败，尝试 `YOUTUBE_TRANSCRIPT_COOKIES_FROM_BROWSER=safari`（或您的浏览器） |
