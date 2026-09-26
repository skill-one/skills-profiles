# YouTube 下载器

## 概述

使用 yt-dlp 和 ffmpeg 从 YouTube 和 HLS 流媒体平台（Mux、Vimeo 等）进行可靠的视频和音频下载。此技能提供以下工作流程：
- 使用 PO token 提供商或浏览器 cookie 进行 YouTube 下载（最高 4K）
- 使用认证头下载 HLS 流
- 处理受保护内容和解决常见的下载失败问题

## 非技术用户体验（默认）

假设用户是非技术用户。不要让他们运行命令。由您自己执行所有操作，并使用普通语言报告进度。除非用户询问，否则避免提及工具。

**默认流程：**
1. 如果未提供，请询问 URL。
2. 获取视频元数据（标题/上传者/时长/缩略图），并确认是否与用户的意图匹配。
   - 如果 yt-dlp 被“确认您不是机器人”阻止，则回退到 YouTube oEmbed 以获取标题/上传者/缩略图（时长可能未知）。
3. 提供简单的选择（视频与仅音频、质量、字幕、保存位置）。
4. 如果用户未指定，则使用合理的默认值继续：
   - 最佳质量视频下载
   - 合并输出 MP4
   - 仅单个视频（不下载播放列表）
5. 下载并报告最终文件路径、文件大小和分辨率（如果为视频）。

**使用用户友好的术语提供选择：**
- “以最佳质量下载视频（默认）”
- “仅下载音频（MP3）”
- “选择质量：1080p / 720p / 480p / 360p”
- “包含字幕（如果可用）”
- “保存到下载文件夹（默认）或告诉我另一个文件夹”

**始终在可用时渲染缩略图：**
- 如果元数据包含缩略图 URL，请使用 Markdown 图片语法包含它：`![缩略图](URL)`。

**在执行额外工作之前询问：**
- 确认播放列表下载（可能很大）。
- 确认安装/升级缺失的依赖项。
- 询问是否提取浏览器 cookie。
- 如果使用 cookie，则绝不在用户界面响应中提及 cookie 数量或原始 cookie 详细信息。请说“使用了您的 Chrome 登录会话”。
- 如果需要验证，则自动设置本地 PO Token 助手（无需用户操作）。如果 Docker 缺失或失败，则**不要**尝试安装 Docker——改用基于浏览器的 PO Token 提供商。

**法律/安全提示（简短）：**
- 仅在用户有权或有权下载内容时继续。

**响应模板（使用普通语言，无命令）：**
```
![缩略图](THUMBNAIL_URL)

标题：…
频道：…
时长：…

我可以帮助您：
1) 下载视频（最佳质量，MP4）
2) 仅下载音频（MP3）
3) 选择特定质量（1080p/720p/480p/360p）
4) 包含字幕（如果可用）

应该保存到哪里？（默认：下载文件夹）
```

**如果用户说“直接下载”：**
- 使用默认值继续，并在下载完成后确认。
  - 如果被 403 阻止，则自动设置验证助手并重试。

## 可靠下载 SOP（内部）

遵循此 SOP 以避免常见失败和混淆：

1. 在 shell 命令中引用 URL（zsh 将 `?` 视为通配符）。示例：`'https://www.youtube.com/watch?v=VIDEO_ID'`。
2. 确保为 yt-dlp 和 PO Token 提供商启用代理（HTTP_PROXY/HTTPS_PROXY/ALL_PROXY）。
3. 如果看到“确认您不是机器人”，请请求权限并使用浏览器 cookie。如果没有 cookie，则不要继续。
4. 在下载前启动 PO Token 提供商（如果无法启动，则快速失败）。
   - 当可用时，使用 Docker bgutil 提供商。
   - 如果 Docker 缺失或失败，则切换到基于浏览器的 WPC 提供商。
5. 如果使用 cookie，则优先使用 `web_safari` 播放器客户端。否则优先使用 `mweb` 用于 PO token。
6. 在 WPC 生成 token 时保持浏览器窗口打开。确保 Chrome 可以通过相同的代理访问 YouTube。
7. 如果您收到“仅图像可用”或“请求的格式不可用”，将其视为 PO Token 失败，并在修复 token 提供商/浏览器状态后重试。
8. 如果您收到 SSL EOF 或片段错误，将其视为代理/网络问题。使用渐进式格式和/或更好的代理重试。

## 代理执行清单（内部）

- 运行 `scripts/download_video.py URL --info`（如果获得权限，则添加 `--cookies-from-browser chrome`）以获取元数据和缩略图。
- 如果 yt-dlp 元数据失败，则依赖脚本的 oEmbed 回退以获取标题/上传者/缩略图，并注意时长可能不可用。
- 如果存在缩略图 URL，则使用 Markdown 图片语法在响应中渲染它。
- 询问用户选择视频与仅音频（可选）质量预设。
- 使用友好的默认保存位置（下载文件夹），除非用户指定文件夹。
- 对于字幕，运行 `--subtitles` 和请求的 `--sub-lang`。
- 下载后，以普通语言报告文件名、大小和分辨率（如果为视频）。
- 如果下载因 403/片段错误失败，则重试一次使用非 m3u8 渐进式格式。
- 如果出现“确认您不是机器人”，则请求 cookie 访问，并使用 cookie + `web_safari` 重试。
- 如果出现“仅图像可用”，则将其视为 PO Token 失败，并在修复提供者/浏览器状态后重试。
- 在下载前启动 PO Token 提供商（默认 `--auto-po-token`）。如果无法启动，则快速失败。
- 如果基于 Docker 的提供者失败（在中国很常见），则自动回退到基于浏览器的 WPC 提供商（它可能会短暂打开浏览器窗口）。
- 如果使用 WPC 提供商，则保持浏览器窗口打开，直到下载开始。如果浏览器失败启动，则显式设置 Chrome 路径。
- 如果 PO Token 提供者超时，则重新启动一次并重试。
- 如果系统代理已配置，则将其传递到提供者容器中。如果代理指向 127.0.0.1/localhost，则将其重写为 `host.docker.internal` 用于 Docker。

## 何时使用此技能

当用户：
- 请求下载 YouTube 视频或播放列表
- 想从 YouTube 视频中提取音频
- 遇到 yt-dlp 下载失败或格式可用性有限
- 需要帮助选择格式或质量选项
- 报告仅低质量（360p）格式可用
- 询问以特定质量（1080p、4K 等）下载 YouTube 内容
- 需要将下载的 WebM 视频转换为 MP4 格式以实现更广泛的兼容性
- 请求从 Mux、Vimeo 或其他流媒体服务下载 HLS 流（m3u8）
- 需要下载需要认证头的受保护流

## 前提条件

### 1. 验证 yt-dlp 安装（自己运行）

```bash
which yt-dlp
yt-dlp --version
```

如果未安装或过时（< 2025.10.22）：

```bash
brew upgrade yt-dlp  # macOS
# 或
pip install --upgrade yt-dlp  # 跨平台
```

**关键**：过时的 yt-dlp 版本会导致 nsig 提取失败和缺失格式。

### 2. 检查当前质量访问（自己运行）

在下载前检查可用格式：

```bash
yt-dlp -F "https://youtu.be/VIDEO_ID"
```

**如果仅出现格式 18（360p）**：需要 PO token 提供商设置以获取高质量访问。

## 高质量下载工作流程

### 第 1 步：安装 PO Token 提供商（一次性设置）

对于 1080p/1440p/4K 访问，将 PO token 提供商插件安装到 yt-dlp 的 Python 环境中：

```bash
# 找到 yt-dlp 的 Python 路径（yt-dlp 使用的解释器）
head -1 $(which yt-dlp)

# 使用上述行中的解释器安装插件
<YTDLP_PYTHON> -m pip install bgutil-ytdlp-pot-provider
```

**验证**：再次运行 `yt-dlp -F "VIDEO_URL"`。查找格式 137（1080p）、271（1440p）或 313（4K）。

有关详细设置说明和故障排除，请参阅 `references/po-token-setup.md`。

### 第 2 步：以最佳质量下载

安装 PO token 提供商后：

```bash
# 下载最高 1080p 的最佳质量
yt-dlp -f "bestvideo[height<=1080]+bestaudio/best" "VIDEO_URL"

# 下载最佳可用质量（如果可用，则为 4K）
yt-dlp -f "bestvideo+bestaudio/best" "VIDEO_URL"
```

### 第 3 步：验证下载质量

```bash
# 检查视频分辨率
ffprobe -v error -select_streams v:0 -show_entries stream=width,height,codec_name -of default=noprint_wrappers=1 video.mp4
```

1080p 的预期输出：
```
codec_name=vp9
width=1920
height=1080
```

## 备选方案：浏览器 Cookie 方法

如果 PO token 提供商设置有问题，请使用浏览器 cookie：

```bash
# Firefox
yt-dlp --cookies-from-browser firefox -f "bestvideo[height<=1080]+bestaudio/best" "VIDEO_URL"

# Chrome
yt-dlp --cookies-from-browser chrome -f "bestvideo[height<=1080]+bestaudio/best" "VIDEO_URL"
```

**优点**：可以访问年龄限制和会员专享内容。
**要求**：
- 必须在指定浏览器中登录 YouTube。
- 浏览器和 yt-dlp 必须使用相同的 IP/代理。
- 不要使用 Android 客户端与 cookie（Android 客户端不支持 cookie）。

## 常见任务

### 仅音频下载（自己运行）

提取 MP3：

```bash
yt-dlp -x --audio-format mp3 "VIDEO_URL"
```

### 自定义输出目录（自己运行）

```bash
yt-dlp -P ~/Downloads/YouTube "VIDEO_URL"
```

### 带字幕下载（自己运行）

```bash
yt-dlp --write-subs --sub-lang en "VIDEO_URL"
```

### 播放列表下载（自己运行）

```bash
yt-dlp -f "bestvideo[height<=1080]+bestaudio/best" "PLAYLIST_URL"
```

### WebM 转换为 MP4（自己运行）

YouTube 高质量下载通常使用 WebM 格式（VP9 编码）。转换为 MP4 以实现更广泛的兼容性：

```bash
# 检查是否安装了 ffmpeg
which ffmpeg || brew install ffmpeg  # macOS

# 使用良好的质量设置将 WebM 转换为 MP4
ffmpeg -i "video.webm" -c:v libx264 -preset medium -crf 23 -c:a aac -b:a 128k "video.mp4"
```

**参数说明：**
- `-c:v libx264`：使用 H.264 视频编码（广泛兼容）
- `-preset medium`：平衡编码速度和文件大小
- `-crf 23`：恒定速率因子（质量）（18-28 范围，较低 = 更高质量）
- `-c:a aac`：使用 AAC 音频编码
- `-b:a 128k`：音频比特率 128 kbps

**提示**：转换保留 1080p 分辨率，并在现代硬件上提供约 6 倍编码速度。

## 故障排除快速参考

### 仅 360p 可用（格式 18）

**原因**：缺少 PO token 提供商或 yt-dlp 过时。

**解决方案**：
1. 更新 yt-dlp：`brew upgrade yt-dlp`
2. 安装 PO token 提供商（见上述步骤 1）
3. 或使用浏览器 cookie 方法

### 确认您不是机器人

**原因**：YouTube 要求进行身份验证才能继续。

**解决方案**：
1. 请求权限并使用浏览器 cookie (`--cookies-from-browser chrome`)。
2. 确保浏览器和 yt-dlp 使用相同的 IP/代理。
3. 如有必要，使用 `web_safari` 客户端重试。

### 仅图像可用 / 请求的格式不可用

**原因**：PO token 未应用或提供者/浏览器验证失败。

**解决方案**：
1. 在下载前验证 PO Token 提供商是否正在运行。
2. 如果使用 WPC，请保持浏览器窗口打开。
3. 如果使用 cookie，请优先使用 `web_safari` 客户端并重试。

### nsig 提取失败

**症状**：
```
WARNING: [youtube] nsig 提取失败：某些格式可能缺失
```

**解决方案**：
1. 更新 yt-dlp 到最新版本
2. 安装 PO token 提供商
3. 如果仍然失败且 PO token 被禁用，请使用 Android 客户端：`yt-dlp --extractor-args "youtube:player_client=android" "VIDEO_URL"`

### SSL EOF / 片段错误

**原因**：代理或网络不稳定。

**解决方案**：
1. 使用渐进式格式（非 m3u8）重试。
2. 切换到更稳定的代理/节点。
3. 在下载期间避免关闭 PO token 浏览器窗口。

### 缓慢下载或网络错误

对于中国用户或受限制代理：
- 由于网络条件，下载可能很慢
- 允许足够的时间完成
- yt-dlp 自动重试临时故障

### PO Token 警告（无害）

```
WARNING: android client https formats require a GVS PO Token
```

**操作**：如果下载成功，请忽略。这表示 Android 客户端在没有 PO token 的情况下具有有限的格式访问权限。

## 嵌套脚本参考

### scripts/download_video.py

使用此便利包装器默认自动启动 PO Token 提供商以进行高质量下载。自己使用它并报告结果给用户，而无需让他们运行命令。

**基本用法：**
```bash
scripts/download_video.py "VIDEO_URL"
```

**参数：**
- `url` - YouTube 视频链接（必需）
- `-o, --output-dir` - 输出目录
- `--output-template` - 输出文件名模板（yt-dlp 语法）
- `-f, --format` - 格式规范
- `-q, --quality` - 质量预设（best、1080p、720p、480p、360p、worst）。默认：best（对于 `--audio-only` 被跳过）
- `-a, --audio-only` - 提取 MP3 作为音频
- `--subtitles` - 如果可用，则下载字幕
- `--sub-lang` - 字幕语言（逗号分隔，默认：en）
- `--cookies-from-browser` - 从浏览器加载 cookie（例如，chrome、firefox）
- `--cookies-file` - 从 cookies.txt 文件加载 cookie
- `--player-client` - 使用特定的 YouTube 播放器客户端（例如，web_safari）
- `--auto-po-token` - 自动启动 PO Token 提供商（默认；如果可用，则使用 Docker，否则切换到基于浏览器的提供者）
- `--no-auto-po-token` - 禁用自动 PO Token 设置
- `--proxy` - 为 yt-dlp 和 PO Token 提供商设置代理 URL（例如，http://127.0.0.1:1082）
- `--wpc-browser-path` - WPC 提供者的浏览器可执行路径
- `-F, --list-formats` - 列出可用格式
- `--merge-format` - 合并输出容器（例如，mp4、mkv）。默认：mp4
- `--playlist` - 允许播放列表下载（默认：仅单个视频）
- `--info` - 打印标题/上传者/时长/缩略图并退出
- `--no-android-client` - 禁用 Android 客户端回退

**注意**：仅在 PO token 被禁用时使用 Android 客户端。保持 PO token 启用以获得高质量。

## 质量预期

| 设置 | 360p | 720p | 1080p | 1440p | 4K |
|------|------|------|-------|-------|-----|
| **自动 PO token（默认）** | ✓ | ✓ | ✓ | ✓ | ✓ |
| Android 客户端仅 | ✓ | ✗ | ✗ | ✗ | ✗ |
| 手动 PO token 提供商 | ✓ | ✓ | ✓ | ✓ | ✓ |
| 浏览器 cookie | ✓ | ✓ | ✓ | ✓ | ✓ |

## HLS 流下载（m3u8）

对于 Mux、Vimeo 和其他基于 HLS 的流媒体平台，使用 ffmpeg 作为主要工具。这些流通常需要 yt-dlp 可能无法正确处理的认证头。

### 识别 HLS 流

HLS 流使用 `.m3u8` 播放列表文件：
- 主播放列表：列出多个质量选项
- 渲染播放列表：包含实际视频/音频段 URL

### 下载工作流程

#### 第 1 步：获取流 URL

从视频源获取 m3u8 URL。对于受保护的流：
1. 打开浏览器开发者工具 → 网络选项卡
2. 播放视频
3. 过滤“m3u8”以找到播放列表 URL
4. 复制渲染 URL（通常包含质量信息，如“rendition.m3u8”）

#### 第 2 步：识别所需头

许多 CDN 需要认证头：
- **Referer**：源网站（例如，`https://maven.com/`）
- **Origin**：与 Referer 相同的 CORS
- **User-Agent**：浏览器识别

检查网络选项卡以查看浏览器发送哪些头。

#### 第 3 步：使用 ffmpeg 下载

使用 `-headers` 标志为受保护流使用 ffmpeg：

```bash
ffmpeg -headers "Referer: https://example.com/" \
  -protocol_whitelist file,http,https,tcp,tls,crypto,httpproxy \
  -i "https://cdn.example.com/path/rendition.m3u8?params" \
  -c copy -bsf:a aac_adtstoasc \
  output.mp4
```

**关键参数：**
- `-headers`：设置 HTTP 头（对于认证至关重要）
- `-protocol_whitelist`：启用 HLS 所需协议
- `-c copy`：流复制（不重新编码，更快）
- `-bsf:a aac_adtstoasc`：修复 AAC 音频兼容性

**常见头模式：**
```bash
# 单个头
-headers "Referer: https://example.com/"

# 多个头
-headers "Referer: https://example.com/" \
-headers "User-Agent: Mozilla/5.0..."

# 替代语法
-headers $'Referer: https://example.com/\r\nUser-Agent: Mozilla/5.0...'
```

### 处理单独的音频/视频流

某些平台（如 Mux）提供单独的音频和视频流：

1. **下载音频流：**
```bash
ffmpeg -headers "Referer: https://example.com/" \
  -protocol_whitelist file,http,https,tcp,tls,crypto,httpproxy \
  -i "https://cdn.example.com/audio/rendition.m3u8" \
  -c copy audio.m4a
```

2. **下载视频流：**
```bash
ffmpeg -headers "Referer: https://example.com/" \
  -protocol_whitelist file,http,https,tcp,tls,crypto,httpproxy \
  -i "https://cdn.example.com/video/rendition.m3u8" \
  -c copy video.mp4
```

3. **合并流：**
```bash
ffmpeg -i video.mp4 -i audio.m4a -c copy merged.mp4
```

### HLS 下载故障排除

#### 403 禁止错误

**原因**：缺少或认证头不正确。

**解决方案**：
1. 验证 Referer 头是否与视频源网站匹配
2. 检查是否需要额外的头（Origin、User-Agent）
3. 确保播放列表 URL 包含来自浏览器的所有查询参数

#### yt-dlp 卡在 Cookie 提取

**症状**：`Extracting cookies from chrome` 无限期挂起。

**解决方案**：直接使用 ffmpeg 而不是 yt-dlp 进行 HLS 流下载。

#### 协议未在白名单中

**错误**：`Protocol 'https' not on whitelist 'file,crypto,data'`

**解决方案**：添加 `-protocol_whitelist file,http,https,tcp,tls,crypto,httpproxy`

#### 空片段或无流

**原因**：m3u8 URL 中的签名已过期。

**解决方案**：
1. 从浏览器开发者工具获取最新 URL
2. 获取 URL 后立即下载
3. 查找带有更新签名参数的渲染 URL

### 性能提示

- HLS 下载通常以 10-15 倍实时速度运行
- 使用 `-c copy`（无重新编码，最快）
- 使用实时进度显示监控下载
- 使用绝对输出路径以避免目录混乱

## 进一步阅读

- **PO Token 设置**：请参阅 `references/po-token-setup.md` 以获取详细的安装和故障排除说明
- **内部 SOP**：`references/internal-sop.md` — 短列表的 yt-dlp 失败，看起来像其他东西（zsh 中未引用的 URL，代理无法到达 PO Token 提供商）。当下载失败且没有明显原因时，首先阅读它
- **yt-dlp 文档**：https://github.com/yt-dlp/yt-dlp
- **格式选择指南**：https://github.com/yt-dlp/yt-dlp#format-selection

## 下一步：转录下载的音频/视频

下载后，如果用户的目标涉及从视频中获取文本（转录、字幕、会议笔记），则主动建议：

```
下载完成：[filename]

如果您需要语音内容作为文本，我可以为您转录。

选项：
A) 使用 /daymade-audio:asr-transcribe-to-text 进行转录（推荐用于语音识别）
B) 不用了——我只需要视频文件
```
