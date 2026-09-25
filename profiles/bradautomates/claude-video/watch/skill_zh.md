# /watch

您没有视频输入；这个技能将为您提供。一个 Python 脚本首先获取字幕，然后根据需要下载视频，将帧提取为 JPEG（场景感知，或以 `efficient` 的细节进行快速关键帧），获取带时间戳的文本（首先使用原生字幕，然后使用 Whisper API 作为后备），并打印帧路径。然后您 `Read` 每个帧路径以查看图像，并将它们与文本结合起来回答用户。

## 解析 `SKILL_DIR`（在任何命令之前执行）

以下每个 `python3 ...` 命令都在 `SKILL_DIR/scripts/` 下运行捆绑的脚本。将 `SKILL_DIR` 设置为包含此 `SKILL.md` 文件的**绝对路径**——您的 harness 在 `Read` 结果中告诉了您该路径。脚本始终是此文件的直接同级文件（`SKILL_DIR/scripts/watch.py`），在每个安装布局中：

```
Read ~/.claude/plugins/cache/claude-video/watch/<ver>/skills/watch/SKILL.md → SKILL_DIR=…/skills/watch
Read ~/.codex/skills/watch/SKILL.md                                          → SKILL_DIR=~/.codex/skills/watch
Read ~/.agents/skills/watch/SKILL.md                                         → SKILL_DIR=~/.agents/skills/watch
```

将这个字面路径替换为命令中的 `${SKILL_DIR}`。这在每个 harness（Claude Code、Codex、Cursor、Gemini CLI、…）上都能工作，而无需依赖任何 harness 特定的环境变量。在运行开始时保护一次：

```bash
SKILL_DIR="<包含您所读的 SKILL.md 文件的目录的绝对路径>"
if [ ! -f "$SKILL_DIR/scripts/watch.py" ]; then
  echo "ERROR: scripts/watch.py 未在 SKILL_DIR=$SKILL_DIR 下找到" >&2
  echo "重新检查您所读的 SKILL.md 文件的目录并将其作为 SKILL_DIR 替换。" >&2
  exit 1
fi
```

## 第 0 步 — 预设设置（每次 `/watch` 调用都会运行，成功时静默）

**Python 解释器：** 此技能中的每个 `python3 ...` 命令都适用于 macOS/Linux。在 **Windows** 上，请将 `python` 替换为 `python3` 命令——Windows 上的 `python3` 命令是 Microsoft Store 的存根，不会运行脚本。

在会话中的第一次 `/watch` 调用时，使用结构化预设，以便您可以检测首次运行设置：

```bash
python3 "${SKILL_DIR}/scripts/setup.py" --json
```

根据两个字段进行分支：

- **`can_proceed: true` 和 `first_run: false`** → 设置已完成（用户可能故意跳过了 Whisper 密钥——这是允许的）。无需评论直接继续到第 1 步。
- **`first_run: true`** → 真正的首次设置。按顺序执行以下操作：
  1. 如果 `missing_binaries` 非空，请先运行安装程序（它在 macOS 上自动安装 / 在其他地方打印命令——见下文），并确认二进制文件已安装。**不要跳过此步骤并跳转到偏好设置。**
  2. 如果需要，再次运行安装程序，以便它构建 `~/.config/watch/.env`（它仅在文件不存在时写入模板，因此请在您向其写入任何值之前让它创建该文件）。
  3. 鼓励一个 Whisper API 密钥，并询问下文中的 `watch-preference` 问题，然后将所选值写入 `~/.config/watch/.env` 并设置 `SETUP_COMPLETE=true`。
- **`can_proceed: false` 和 `first_run: false`** → 设置之前已完成，但环境已回归（例如，OS 更改后的 `missing_binaries`）。运行安装程序以修复，然后继续。不要重新询问偏好设置。

缺少 Whisper 密钥是*鼓励修复而不是必需的*：在真正的首次运行中，即使二进制文件存在，`status` 也会读取 `needs_key`——这是您鼓励密钥的提示，而不是阻止。

在同一会话中的后续 `/watch` 调用中，使用静默检查：

```bash
python3 "${SKILL_DIR}/scripts/setup.py" --check
```

这是一个小于 100 毫秒的查找。退出 0 表示 `/watch` 可以运行——这**包括没有 Whisper 密钥完成设置的用戶**（无密钥是允许的）。退出 0 时，脚本不会输出**任何内容**——无需评论直接继续到第 1 步。**不要向用户宣布“设置已完成”**——他们不需要在每次回合中都有一个状态消息。第 0 步的唯一可接受的用户可见输出是在需要修复时。

在非零退出时，请遵循表格：

| 退出 | 含义 | 操作 |
|------|------|------|
| `2` | 缺少二进制文件 (`ffmpeg` / `ffprobe` / `yt-dlp`) | 运行安装程序 |
| `3` | 真正的首次运行且没有 Whisper API 密钥 | 运行安装程序以构建 `.env`，然后鼓励一个密钥（用户可能会拒绝——继续使用 `--no-whisper`） |
| `4` | 两者都缺少 | 运行安装程序，然后鼓励一个密钥 |

退出 `3` 仅在用户完成设置之前触发。一旦 `SETUP_COMPLETE=true` 被写入，无密钥安装将返回退出 0，并且永远不会再次提示。

安装程序是幂等的——可以重新运行：

```bash
python3 "${SKILL_DIR}/scripts/setup.py"
```

在 macOS 使用 Homebrew 时，它会自动安装 `ffmpeg` 和 `yt-dlp`。在 Linux/Windows 上，它会打印用户需要运行的精确安装命令。它使用带注释的占位符和默认的 `watch` 设置在 `0600` 权限下构建 `~/.config/watch/.env`。

**如果安装后仍然缺少 API 密钥：** 使用 `AskUserQuestion` 询问用户他们是否有 Groq API 密钥（首选——更便宜、更快）或 OpenAI 密钥。然后将其写入 `~/.config/watch/.env`——设置匹配的 `GROQ_API_KEY=...` 或 `OPENAI_API_KEY=...` 行。如果他们不想设置 Whisper，继续使用 `--no-whisper` 并告诉他们没有原生字幕的视频将只返回帧。

**首次运行的 `watch` 偏好设置：** 在安装程序构建 `~/.config/watch/.env` 后，使用 `AskUserQuestion` 询问一个问题：

- 默认细节（一个旋钮）。按此确切顺序呈现 `AskUserQuestion` 选项——从最轻到最重——并保持 `(推荐)` 在 `balanced` 上，即使它不是第一个（**不要**重新排序以将推荐选项放在第一位）：
  - `transcript` — 不返回任何帧，仅返回文本（当字幕存在时跳过视频下载）。
  - `efficient` — 快速关键帧遍历（最多 50 帧）。
  - `balanced`（推荐）— 场景感知帧（最多 100 帧，默认）。
  - `token-burner` — 场景感知，无限制（最高保真度；高 token 成本）。

直接将答案写入 `~/.config/watch/.env`，在其自己的行上设置裸键——**没有尾随的行内注释**（值后的 `# note` 会破坏解析）：

```bash
WATCH_DETAIL=balanced
```

使用用户选择的值。如果他们跳过此问题，请保持推荐的默认值。一旦处理了依赖项、API 密钥选择和此偏好设置，就在同一文件中写入或更新 `SETUP_COMPLETE=true`。当 `SETUP_COMPLETE=true` 时，**不要**再次询问此偏好设置问题。

**结构化模式（可选）：** `python3 "${SKILL_DIR}/scripts/setup.py" --json` 会发出 `{status, can_proceed, first_run, setup_complete, missing_binaries, whisper_backend, has_api_key, config_file, watch_detail, platform}`，其中 `status` 是 `ready | needs_install | needs_key | needs_install_and_key` 之一。`status` 描述了*理想*状态（鼓励密钥，因此无密钥的首次运行会读取 `needs_key`）；`can_proceed` 是操作门（二进制文件存在 AND 密钥已设置 OR 设置已完成）。根据 `can_proceed`/`first_run` 进行分支以决定是否运行；使用 `status` 来决定鼓励什么。

在单个会话内，您可以在后续的 `/watch` 调用中跳过第 0 步——一旦 `--check` 返回 0，回合之间环境不会发生变化。

## 使用场景

- 用户粘贴了视频 URL（YouTube、Vimeo、X、TikTok、Twitch 片段、大多数 yt-dlp 支持的网站），并询问关于它的信息。
- 用户指向本地视频文件（`.mp4`、`.mov`、`.mkv`、`.webm` 等），并询问关于它的信息。
- 用户输入 `/watch <url-or-path> [question]`。

## 推荐限制

- **最佳准确性：** 10 分钟以下的视频。帧覆盖率与持续时间成反比。
- **通用速率限制：** 2 fps。脚本永远不会比 2 fps 采样更快，即使预算或 `--fps` 会暗示更多。
- **帧上限由细节模式设置**（`~/.config/watch/.env` 中的 `WATCH_DETAIL`，或 `--detail`），而不是单个全局限制：
  - `transcript` → 不返回任何帧
  - `efficient` → 最多 **50**（关键帧）
  - `balanced`（默认）→ 最多 **100**（场景感知）
  - `token-burner` → **无限制**（场景感知；超过 250 帧会打印一个软警告）
  - `--max-frames N` 会覆盖模式原本使用的限制（例如，`--max-frames 40`）
  - `--resolution W` 会更改帧宽度（以像素为单位）（默认 512；仅在用户需要读取屏幕上的文本时增加到 1024）
  - `--fps F` 会覆盖自动 fps（最大限制为 2 fps）
  - `--out-dir DIR` 会将工作文件保存在特定位置（默认：自动生成的 tmp 目录）
  - `--whisper groq|openai` 会强制使用特定的 Whisper 后端（默认：如果两者都存在，则优先使用 Groq）
  - `--no-whisper` 会完全禁用 Whisper 后备（如果没有字幕，则仅返回帧）
  - `--no-dedup` 会保留近乎重复的帧。默认情况下，帧差分遍历会丢弃与之前保留的帧视觉上近乎相同的帧（静态幻灯片、静态屏幕录制、暂停的视频），以便帧预算用于独特内容；报告的 **Frames** 行会注明已丢弃多少帧。仅当用户需要每个采样帧时（例如，判断帧与帧之间的细微运动）才传递此参数。

### 聚焦于某一部分（更高的帧率）

当用户询问特定时刻时——"2 分钟标记处发生了什么？"、"将 0:45 放大到 1:00"、"前 10 秒"——请传递 `--start` 和/或 `--end`。脚本会切换到聚焦模式预算，这些预算比全视频预算更密集（仍然限制在 2 fps，并且仍然受细节模式限制——以下计数假设默认的 `balanced` 限制为 100；`efficient` 最高为 50）：

- ≤5s → 2 fps（最多 10 帧）
- 5-15s → 2 fps（最多 30 帧）
- 15-30s → ~2 fps（最多 60 帧）
- 30-60s → ~1.3 fps（最多 80 帧）
- 60-180s → ~0.6 fps（100 帧，限制）

聚焦模式适用于：
- 任何用户明确命名的时刻/范围（"在 2:30 附近"、"引言"、"最后 30 秒"）。
- 任何视频长度超过 ~10 分钟，而用户的询问是关于特定部分的情况——在相关部分上运行聚焦比在整个东西上进行稀疏扫描更有用。
- 全扫描后重新运行没有在某个区域提供足够细节的情况。

文本会自动过滤到相同的范围。帧时间戳是绝对的（真实视频时间线，而不是相对于开始的偏移量）。

示例：
```bash
# 1 分钟视频的最后 10 秒
python3 "${SKILL_DIR}/scripts/watch.py" video.mp4 --start 50 --end 60

# 放大到 2:15 → 2:45，以 2 fps（60 帧）
python3 "${SKILL_DIR}/scripts/watch.py" "$URL" --start 2:15 --end 2:45 --fps 2

# 从 1h12m 到视频结束
python3 "${SKILL_DIR}/scripts/watch.py" "$URL" --start 1:12:00
```

**第 3 步 — 读取脚本列出的每个帧路径。** `Read` 工具会直接将 JPEG 渲染为图像。在单个消息中读取所有帧（并行工具调用），以便您可以看到它们一起。帧按时间戳顺序排列，带有 `t=MM:SS` 时间戳，以便您可以将它们与文本对齐。

**第 4 步 — 回答用户。** 您现在有两个证据流：
- **Frames** — 每个时间戳时屏幕上的内容
- **Transcript** — 每个时间戳时说的话。报告的标题显示了来源（`captions` = yt-dlp 拉取原生字幕；`whisper (groq)` 或 `whisper (openai)` = 由 API 转录）。

如果用户提出了特定问题，请直接引用时间戳回答。如果他们没有提出任何问题，请总结视频中的内容——结构、关键时刻、值得注意的视觉效果、口语内容。

这对 `transcript` 细节也是如此：即使没有帧，也要产生**总结**，就像其他模式一样——不要将完整文本粘贴到聊天中。结合结构、关键时刻和口语内容以及时间戳进行综合；仅引用重要的行。如果用户明确要求，才提供原始文本。

**第 5 步 — 清理。** 脚本在末尾打印工作目录。如果用户不会就这个视频提出后续问题，请使用 `rm -rf <dir>` 删除它。如果他们可能会，请保留它。

## 细节和帧

默认行为来自 `~/.config/watch/.env`：

- `WATCH_DETAIL=transcript|efficient|balanced|token-burner`（默认：`balanced`）

在 `transcript` 细节下，字幕足以在不下载视频的情况下返回报告。如果字幕缺失，脚本仅下载音频并尝试 Whisper。如果无法生成文本，它会清楚地报告此限制；使用 `--detail balanced` 返回帧。

在 `efficient` 细节下，脚本下载视频并提取**仅关键帧**（`ffmpeg -skip_frame nokey`）——一个近乎即时的遍历，在场景切换处生成帧。如果片段的关键帧少于 4 个，它会回退到均匀采样。

在 `balanced` / `token-burner` 细节下，脚本提取**场景感知**帧：首先使用 ffmpeg 场景变化选择，仅在视频实际上静态时才回退到均匀采样。`balanced` 限制为 100 帧；`token-burner` 无限制。帧报告行包括时间戳和选择原因。提取的图像在 1998px 高度上被限制，以与 Claude Read 兼容。

## 文本提示帧

视觉帧选择（场景/关键帧）可能会遗漏演讲者明确标记的时刻——"看这里"、"你可以看到"、"注意这个"、"注意发生什么"——因为指向幻灯片通常是*低*视觉变化。`--timestamps` 允许您在这些确切时刻强制一个帧。**您**决定哪些时刻很重要，通过读取文本：

1. 在 `--detail transcript`（或任何细节）下运行一次以获取带时间戳的文本。
2. 扫描文本以查找指示性提示——说话者将注意力引导到屏幕上的某物的短语。这是一个判断（忽略修辞的"看，重点是…"）；这就是为什么由您而不是正则表达式完成的原因。
3. 使用 `--timestamps 4:32,7:10,9:55`（绝对源时间）重新运行。对于 URL，在工作目录中指向下载的本地文件，以便它不会重新下载。

行为：
- **默认为累加。** 提示帧（`reason=transcript-cue`）会按时间顺序合并到 `--detail` 已经选择的任何内容中。
- **首先固定和计数。** 提示帧在细节引擎运行之前被预留，因此它们永远不会被均匀采样甚至移除。
- **尊重聚焦模式。** 使用 `--start/--end`，任何在窗口外的提示时间戳都会被丢弃（在总结中报告）。坐标始终是绝对源时间。
- **仅提示帧。** `--detail transcript --timestamps …` 会跳过场景/关键帧采样并返回*仅*提示帧（它将下载视频以这样做，因为帧需要像素）。

## 转录

脚本以两种方式之一获取带时间戳的文本：

1. **原生字幕（免费，首选）。** yt-dlp 从源平台（如果可用）拉取手动或自动生成的字幕。
2. **Whisper API 后备。** 如果没有返回字幕（或源是本地文件），脚本提取音频（`ffmpeg -vn -ac 1 -ar 16000 -b:a 64k`，约 0.5 MB/分钟）并将其上传到配置了密钥的 Whisper API：
   - **Groq** — `whisper-large-v3`。首选默认：更便宜、更快。在 console.groq.com/keys 获取密钥。
   - **OpenAI** — `whisper-1`。后备。在 platform.openai.com/api-keys 获取密钥。

这两个密钥都位于 `~/.config/watch/.env`。脚本在设置两个密钥时优先使用 Groq；使用 `--whisper openai` 强制 OpenAI。使用 `--no-whisper` 跳过后备。

## 失败模式和处理

- **预设设置失败** → 运行 `python3 "${SKILL_DIR}/scripts/setup.py"`（在 macOS 上通过 brew 自动安装 ffmpeg/yt-dlp，构建 `.env`）。对于 API 密钥，通过 `AskUserQuestion` 询问用户并将其写入 `~/.config/watch/.env`。
- **没有文本可用** → 字幕缺失 AND（没有 Whisper 密钥 OR Whisper API 失败）。脚本会打印一个提示，指向设置。继续仅使用帧并告诉用户。
- **打印了长视频警告** → 在您的回答中确认它。提供通过 `--start`/`--end` 重新运行聚焦于特定部分的机会，而不是稀疏的全视频扫描。
- **下载失败** → yt-dlp 的错误会输出到 stderr。如果是需要登录或区域锁定的视频，请直接告诉用户；不要重复尝试。
- **Whisper 请求失败** → 错误会打印到 stderr（可能：无效密钥或速率限制）。通过 API 的 25 MB 上传上限分割音频并自动转录，因此长度本身不会失败它；如果某些块失败，文本将不完整，并且丢弃的块会在 stderr 中注明。报告将说“无可用”仅当每个块都失败时。如果 Groq 失败（或反之），可以尝试使用 `--whisper openai`。

## Token 效率

此技能主要在帧上消耗 token。数量级：
- 80 个 512 像素宽的帧大约是 50-80k 图像 token，具体取决于宽高比。
- 文本很便宜（最多几千 token，对于 10 分钟的视频）。
- 将 `--resolution` 增加到 1024 会使每帧图像 token 大约四倍。仅在必要时这样做。

如果您已经在当前会话中观看了一个视频，而用户提出了后续问题，请**不要**重新运行脚本——您已经有了上下文中的帧和文本。只需根据您拥有的内容回答。

## 安全与权限

**此技能执行的操作：**
- 在本地运行 `yt-dlp` 以下载视频并拉取原生字幕（公共数据；请求直接发送到 URL 指向的主机）
- 在本地运行 `ffmpeg` / `ffprobe` 以将帧提取为 JPEG，并在需要 Whisper 时提取单声道 16 kHz 音频片段
- 当 `GROQ_API_KEY` 设置时，将提取的音频片段发送到 Groq 的 Whisper API (`api.groq.com/openai/v1/audio/transcriptions`)（首选——更便宜、更快）
- 当 Groq 未设置时，或当 `--whisper openai` 被强制时，将提取的音频片段发送到 OpenAI 的音频转录 API (`api.openai.com/v1/audio/transcriptions`)
- 将下载的视频、帧、音频和中间文本写入系统临时目录下的工作目录（或 `--out-dir` 如果指定）以便 Claude 可以 `Read` 它们
- 读取/创建 `~/.config/watch/.env`（模式 `0600`）以存储 Whisper API 密钥和 `SETUP_COMPLETE` 标记。作为后备，也会读取当前工作目录中的 `.env`

**此技能不执行的操作：**
- 不上传视频本身到任何 API——只有提取的音频会发送出去，并且仅当原生字幕缺失且未使用 `--no-whisper` 禁用 Whisper 时才会发送
- 不访问任何平台账户（没有登录、没有会话 cookie、没有发布）——yt-dlp 仅请求公共数据
- 不在提供者之间共享 API 密钥（Groq 密钥仅发送到 `api.groq.com`，OpenAI 密钥仅发送到 `api.openai.com`)
- 不记录、缓存或写入 API 密钥到 stdout、stderr 或输出文件
- 不在工作目录和 `~/.config/watch/.env` 之外持久化任何内容——完成时清理工作目录（第 5 步）

**捆绑脚本：** `scripts/watch.py`（入口点）、`scripts/download.py`（yt-dlp 包装器）、`scripts/frames.py`（ffmpeg 帧提取）、`scripts/transcribe.py`（字幕选择 + Whisper 协调）、`scripts/whisper.py`（Groq / OpenAI 客户端）、`scripts/setup.py`（预设 + 安装程序）

首次使用前检查脚本以验证行为。
