# YouTube 视频下载器

可完全控制视频质量和格式设置的 YouTube 视频下载工具。

## 快速入门

下载视频最简单的方法：

```bash
python scripts/download_video.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

这将在最佳可用质量下将视频下载为 MP4 格式到 `/mnt/user-data/outputs/` 目录。

## 选项

### 质量设置

使用 `-q` 或 `--quality` 指定视频质量：

- `best`（默认）：最高可用质量
- `1080p`：全高清
- `720p`：高清
- `480p`：标清
- `360p`：较低质量
- `worst`：最低可用质量

示例：
```bash
python scripts/download_video.py "URL" -q 720p
```

### 格式选项

使用 `-f` 或 `--format` 指定输出格式（仅限视频下载）：

- `mp4`（默认）：最兼容
- `webm`：现代格式
- `mkv`：Matroska 容器

示例：
```bash
python scripts/download_video.py "URL" -f webm
```

### 仅音频

使用 `-a` 或 `--audio-only` 仅下载音频为 MP3 格式：

```bash
python scripts/download_video.py "URL" -a
```

### 自定义输出目录

使用 `-o` 或 `--output` 指定不同的输出目录：

```bash
python scripts/download_video.py "URL" -o /path/to/directory
```

## 完整示例

1. 以 1080p 质量下载为 MP4：
```bash
python scripts/download_video.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" -q 1080p
```

2. 仅下载音频为 MP3：
```bash
python scripts/download_video.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" -a
```

3. 以 720p 质量下载为 WebM 到自定义目录：
```bash
python scripts/download_video.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" -q 720p -f webm -o /custom/path
```

## 工作原理

该工具使用 `yt-dlp`，一个强大的 YouTube 下载器，它：
- 如果未安装则自动安装自身
- 在下载前获取视频信息
- 选择符合您标准的最佳可用流
- 需要时合并视频和音频流
- 支持广泛的 YouTube 视频格式

## 重要提示

- 默认下载到 `/mnt/user-data/outputs/` 目录
- 视频文件名自动根据视频标题生成
- 脚本会自动处理 `yt-dlp` 的安装
- 默认仅下载单个视频（播放列表默认被跳过）
- 更高质量的视频下载时间可能更长，且占用更多磁盘空间
