# yt-dlp 视频下载技能

该技能提供使用 yt-dlp 下载视频和从各种平台提取音频的工具。

## 功能

- 支持从多个平台下载视频（YouTube、Twitter/X、Vimeo、TikTok、Instagram、Facebook 等）
- 支持从视频中提取音频
- 自动检测对话中的视频链接
- 支持不同的质量设置和格式

## 使用场景

### 1. 基于命令的下载

当用户明确要求下载视频时：
```
用户：下载这个视频 https://youtube.com/watch?v=...
```

**操作**：提取链接并调用下载脚本

### 2. 对话中的自动检测

当对话中包含视频链接时：
```
用户：看看这个视频 https://twitter.com/... 并告诉我你的想法
```

**操作**：检测视频链接，询问用户是否要下载

### 3. 音频提取

当用户只想提取音频时：
```
用户：提取 https://youtu.be/... 中的音频
```

**操作**：使用音频提取脚本

## 可用脚本

注意：脚本位于 `scripts/` 目录

### download_video.py

主要视频下载器，支持质量和格式选项。

**用法**：
```bash
# 下载视频
scripts/download_video.py <url> -o <输出目录>

# 指定质量下载
scripts/download_video.py <url> --quality 720p
scripts/download_video.py <url> --quality audio  # 仅音频

# 自定义格式选择
scripts/download_video.py <url> --format "bestvideo[height<=1080]+bestaudio/best"

# 仅提取信息
scripts/download_video.py <url> --info-only
```

**质量选项**：`best`、`1080p`、`720p`、`480p`、`audio`

### extract_audio.py

从各种格式的视频中提取音频。

**用法**：
```bash
# 作为 MP3 提取（默认）
/scripts/extract_audio.py <url> -o <输出目录>

# 作为 M4A 提取
/scripts/extract_audio.py <url> --format m4a

# 自定义质量
/scripts/extract_audio.py <url> --quality 320
```

**格式**：`mp3`、`m4a`、`opus`、`flac`、`wav`

### extract_urls.py

从文本或文件中提取视频链接。

**用法**：
```bash
# 从文本参数提取
/scripts/extract_urls.py "检查 https://youtube.com/watch?v=..."

# 从文件提取
/scripts/extract_urls.py <文件路径>

# 从标准输入读取
cat file.txt | /scripts/extract_urls.py
```

## 视频平台支持

该技能识别以下平台的链接：
- YouTube (youtube.com, youtu.be)
- Twitter/X (twitter.com, x.com)
- Vimeo (vimeo.com)
- TikTok (tiktok.com)
- Instagram (instagram.com)
- Facebook (facebook.com, fb.watch)
- Twitch (twitch.tv, clips.twitch.tv)
- Dailymotion (dailymotion.com)
- Reddit (reddit.com)
- Streamable (streamable.com)
- 以及 yt-dlp 支持的其他许多平台

## 工作流程

### 当用户提供视频链接时

1. 使用 `extract_urls.py` 从用户的输入中提取链接
2. 确认用户要执行的操作：
   - 下载视频
   - 提取音频
   - 显示视频信息
3. 根据用户的选择执行相应的脚本
4. 通知用户成功/失败以及文件位置

### 当自动检测链接时

1. 使用 `extract_urls.py` 扫描对话文本（可以处理标准输入）
2. 如果发现视频链接，询问用户："我在这个对话中发现了视频链接。您希望我下载吗？"
3. 如果是，继续下载工作流程
4. 如果不是，继续对话

### 处理多个链接

- 对于单个链接：直接下载
- 对于多个链接：询问用户是否要下载所有或选择特定链接
- 如果链接来自同一来源，提供作为播放列表下载的选项

## 质量和格式选择

当用户未指定偏好时：
- 默认使用最佳可用质量
- 对于音频：默认使用 192kbps 的 MP3

当需要选项时：
```bash
# 如果未指定质量，询问用户质量偏好
# 选项：best（默认）、1080p、720p、480p、audio

# 提取音频时询问格式
# 选项：mp3（默认）、m4a、opus、flac、wav
```

## 错误处理

常见问题和解决方案：

1. **yt-dlp 未安装**：
   - 使用 `yt-dlp --version` 检查
   - 使用 `pip install yt-dlp` 或 `brew install yt-dlp` 安装

2. **ffmpeg 未安装**（格式转换需要）
   - 使用 `brew install ffmpeg`（macOS）安装
   - 或 `apt install ffmpeg`（Linux）

3. **视频不可用**：
   - 检查链接是否可访问
   - 某些视频可能需要认证
   - 限制内容可能需要 Cookie

4. **网络错误**：
   - 重试下载
   - 检查网络连接

## 依赖项

- `yt-dlp`：主要视频下载器
- `ffmpeg`：音频/视频处理（格式转换需要）
- `python3` 及标准库

所有脚本都是自包含的，仅使用内置的 Python 模块。
