---
name: youtube-transcript
description: 从 YouTube 视频中提取文本。当用户要求获取 YouTube 视频的文本、字幕或标题，并提供了 YouTube URL（如 youtube.com/watch?v=、youtu.be/ 或类似格式）时使用。支持带时间戳或不带时间戳的输出。
---

# YouTube 文本转录

使用 youtube-transcript-api 从 YouTube 视频中提取文本转录。

## 使用方法

使用 YouTube URL 或视频 ID 运行脚本：

```bash
uv run scripts/get_transcript.py "VIDEO_URL_OR_ID"
```

带时间戳：

```bash
uv run scripts/get_transcript.py "VIDEO_URL_OR_ID" --timestamps
```

## 默认设置

- **不带时间戳**（默认）：纯文本格式，每个字幕片段占一行
- **带时间戳**：`[分:秒] 文本` 格式（或 `[时:分:秒]` 格式用于较长的视频）

## 支持的 URL 格式

- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://youtube.com/embed/VIDEO_ID`
- 原始视频 ID（11 个字符）

## 输出

- **重要**：你绝对不能修改返回的文本转录
- 如果文本转录不带时间戳，你应该整理它，使其按完整段落排列，并且行不会在句子中间截断
- 如果你被要求将文本转录保存到特定文件，请保存到请求的文件
- 如果没有指定输出文件，请使用 YouTube 视频ID，并添加 `-transcript.txt` 后缀

## 注意事项

- 获取自动生成或手动添加的字幕（以可用的为准）
- 需要视频已开启字幕功能
- 如果没有手动字幕，则回退到自动生成的字幕
