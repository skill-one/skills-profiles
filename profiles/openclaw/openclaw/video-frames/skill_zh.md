# 视频帧 (ffmpeg)

从视频中提取单帧，或创建快速缩略图用于检查。

## 快速入门

第一帧：

```bash
{baseDir}/scripts/frame.sh /path/to/video.mp4 --out /tmp/frame.jpg
```

在特定时间点：

```bash
{baseDir}/scripts/frame.sh /path/to/video.mp4 --time 00:00:10 --out /tmp/frame-10s.jpg
```

## 注意事项

- 对于"这里发生了什么？"的情况，优先使用 `--time`。
- 快速分享时使用 `.jpg`；清晰UI帧使用 `.png`。
