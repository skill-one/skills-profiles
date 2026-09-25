# FFmpeg 用于视频制作

FFmpeg 是视频/音频处理的基本工具。这项技能涵盖了 Remotion 视频项目中的常见操作。

## 快速参考

### GIF 转换为 MP4 (Remotion 兼容)

```bash
ffmpeg -i input.gif -movflags faststart -pix_fmt yuv420p \
  -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" output.mp4
```

**这些标志的原因：**
- `-movflags faststart` - 将元数据移动到开头用于网络流式传输
- `-pix_fmt yuv420p` - 确保与大多数播放器兼容
- `scale=trunc(...)` - 强制偶数尺寸（大多数编解码器需要）

### 调整视频大小

```bash
# 调整为 1920x1080（保持宽高比，添加黑边）
ffmpeg -i input.mp4 -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2" output.mp4

# 调整为 1920x1080（裁剪填充）
ffmpeg -i input.mp4 -vf "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080" output.mp4

# 按宽度缩放，自动高度
ffmpeg -i input.mp4 -vf "scale=1280:-2" output.mp4
```

### 视频压缩

```bash
# 良好质量，较小文件（CRF 23 是默认值，越低质量越好）
ffmpeg -i input.mp4 -c:v libx264 -crf 23 -preset medium -c:a aac -b:a 128k output.mp4

# 适用于网络预览的激进压缩
ffmpeg -i input.mp4 -c:v libx264 -crf 28 -preset fast -c:a aac -b:a 96k output.mp4

# 目标文件大小（例如，60 秒视频约为 10MB = ~1.3Mbps）
ffmpeg -i input.mp4 -c:v libx264 -b:v 1300k -c:a aac -b:a 128k output.mp4
```

### 提取音频

```bash
# 提取为 MP3
ffmpeg -i input.mp4 -vn -acodec libmp3lame -q:a 2 output.mp3

# 提取为 AAC
ffmpeg -i input.mp4 -vn -acodec aac -b:a 192k output.m4a

# 提取为 WAV（无损压缩）
ffmpeg -i input.mp4 -vn output.wav
```

### 转换音频格式

```bash
# M4A 转换为 MP3（用于 ElevenLabs 语音样本）
ffmpeg -i input.m4a -codec:a libmp3lame -qscale:a 2 output.mp3

# WAV 转换为 MP3
ffmpeg -i input.wav -codec:a libmp3lame -b:a 192k output.mp3

# 调整音量
ffmpeg -i input.mp3 -filter:a "volume=1.5" output.mp3
```

### 剪辑/裁剪视频

```bash
# 从时间戳剪辑到持续时间（推荐 - 可靠）
ffmpeg -i input.mp4 -ss 00:00:30 -t 00:00:15 -c:v libx264 -c:a aac output.mp4

# 从时间戳剪辑到时间戳
ffmpeg -i input.mp4 -ss 00:00:30 -to 00:00:45 -c:v libx264 -c:a aac output.mp4

# 流复制（更快，但在裁剪点可能丢失帧）
# 仅在源文件频繁包含关键帧时使用
ffmpeg -i input.mp4 -ss 00:00:30 -t 00:00:15 -c copy output.mp4
```

**注意：** 剪辑建议重新编码。流复制 (`-c copy`) 可能会无声地丢失视频，如果查找点与关键帧不匹配。

### 加速/减速

```bash
# 2x 速度（视频和音频）
ffmpeg -i input.mp4 -filter_complex "[0:v]setpts=0.5*PTS[v];[0:a]atempo=2.0[a]" -map "[v]" -map "[a]" output.mp4

# 0.5x 速度（慢动作）
ffmpeg -i input.mp4 -filter_complex "[0:v]setpts=2.0*PTS[v];[0:a]atempo=0.5[a]" -map "[v]" -map "[a]" output.mp4

# 仅视频（无音频）
ffmpeg -i input.mp4 -filter:v "setpts=0.5*PTS" -an output.mp4
```

### 视频拼接

```bash
# 创建文件列表
echo "file 'clip1.mp4'" > list.txt
echo "file 'clip2.mp4'" >> list.txt
echo "file 'clip3.mp4'" >> list.txt

# 拼接（相同编解码器/分辨率）
ffmpeg -f concat -safe 0 -i list.txt -c copy output.mp4

# 拼接并重新编码（不同来源）
ffmpeg -f concat -safe 0 -i list.txt -c:v libx264 -c:a aac output.mp4
```

### 添加淡入/淡出

```bash
# 前 1 秒淡入，最后 1 秒淡出（30fps 视频）
ffmpeg -i input.mp4 -vf "fade=t=in:st=0:d=1,fade=t=out:st=9:d=1" -c:a copy output.mp4

# 音频淡入淡出
ffmpeg -i input.mp4 -af "afade=t=in:st=0:d=1,afade=t=out:st=9:d=1" -c:v copy output.mp4
```

### 获取视频信息

```bash
# 持续时间、分辨率、编解码器信息
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 input.mp4

# 完整信息
ffprobe -v quiet -print_format json -show_format -show_streams input.mp4
```

## Remotion 特定模式

### Remotion 视频速度调整

**何时使用 FFmpeg 与 Remotion `playbackRate`：**

| 情景 | 使用 FFmpeg | 使用 Remotion |
|------|------------|--------------|
| 恒定速度 (1.5x, 2x) | 两者皆可 | ✅ 更简单 |
| 极端速度 (>4x 或 <0.25x) | ✅ 更可靠 | 可能存在问题 |
| 变化速度（随时间加速） | ✅ 预处理 | 需要复杂的解决方案 |
| 需要完美音频同步 | ✅ 保证 | 通常足够 |
| 演示需要匹配旁白时间 | ✅ 预先计算 | 运行时调整 |

**Remotion 限制：** `playbackRate` 必须是恒定的。动态插值如 `playbackRate={interpolate(frame, [0, 100], [1, 5])}` 不会正常工作，因为 Remotion 独立评估每一帧。

```bash
# 加速演示以适应场景（例如，60 秒演示压缩到 20 秒 = 3x 速度）
ffmpeg -i demo-raw.mp4 \
  -filter_complex "[0:v]setpts=0.333*PTS[v];[0:a]atempo=3.0[a]" \
  -map "[v]" -map "[a]" \
  public/demos/demo-fast.mp4

# 慢动作强调（0.5x 速度）
ffmpeg -i action.mp4 \
  -filter_complex "[0:v]setpts=2.0*PTS[v];[0:a]atempo=0.5[a]" \
  -map "[v]" -map "[a]" \
  public/demos/action-slow.mp4

# 无音频加速（屏幕录制常见）
ffmpeg -i demo.mp4 -filter:v "setpts=0.5*PTS" -an public/demos/demo-2x.mp4

# 时间流逝效果（10x 速度，丢弃音频）
ffmpeg -i long-demo.mp4 -filter:v "setpts=0.1*PTS" -an public/demos/timelapse.mp4
```

**计算速度因子：**
- 要将 X 秒视频压缩到 Y 秒场景：`speed = X / Y`
- setpts 乘数 = `1 / speed`（例如，3x 速度 = setpts=0.333*PTS）
- atempo 值 = `speed`（例如，3x 速度 = atempo=3.0）

**极端速度 (>2x 音频）：** 链接 atempo 滤镜（每个滤镜限制在 0.5-2.0 范围内）：
```bash
# 4x 速度音频
-filter_complex "[0:a]atempo=2.0,atempo=2.0[a]"

# 8x 速度音频
-filter_complex "[0:a]atempo=2.0,atempo=2.0,atempo=2.0[a]"
```

### 准备 Remotion 演示录制

```bash
# 标准 1080p，30fps，Remotion 准备
ffmpeg -i raw-recording.mp4 \
  -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,fps=30" \
  -c:v libx264 -crf 18 -preset slow \
  -c:a aac -b:a 192k \
  -movflags faststart \
  public/demos/demo.mp4
```

### 屏幕录制转换为 Remotion 资产

```bash
# 从 iPhone/iPad 录制（通常 60fps，可变分辨率）
ffmpeg -i iphone-recording.mov \
  -vf "scale=1920:-2,fps=30" \
  -c:v libx264 -crf 20 \
  -an \
  public/demos/mobile-demo.mp4
```

### 批量转换 GIF

```bash
for f in assets/*.gif; do
  ffmpeg -i "$f" -movflags faststart -pix_fmt yuv420p \
    -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" \
    "public/demos/$(basename "$f" .gif).mp4"
done
```

## 常见问题

### "高度不能被 2 整除"
添加缩放滤镜：`-vf "scale=trunc(iw/2)*2:trunc(ih/2)*2"`

### 视频无法在浏览器中播放
使用：`-movflags faststart -pix_fmt yuv420p -c:v libx264`

### 音频在速度变化后不同步
使用滤镜复杂结构 with atempo: `-filter_complex "[0:v]setpts=0.5*PTS[v];[0:a]atempo=2.0[a]"`

### 文件过大
增加 CRF（23→28）或降低分辨率

## 质量指南

| 使用场景 | CRF | 预设 | 备注 |
|----------|-----|------|-------|
| 归档/主文件 | 18 | slow | 最佳质量，大文件 |
| 制作 | 20-22 | medium | 良好平衡 |
| 网络/预览 | 23-25 | fast | 较小文件 |
| 草稿/快速 | 28+ | veryfast | 快速编码 |

## 平台特定输出优化

Remotion 渲染视频后（通常为 `out/video.mp4`），使用 FFmpeg 优化每个分发平台。

### 工作流集成

```
Remotion 渲染（主文件）     FFmpeg 优化      平台上传
       ↓                            ↓                       ↓
   out/video.mp4  ────────→  out/video-youtube.mp4  ───→  YouTube
                  ────────→  out/video-twitter.mp4  ───→  Twitter/X
                  ────────→  out/video-linkedin.mp4 ───→  LinkedIn
                  ────────→  out/video-web.mp4      ───→  网站嵌入
```

### YouTube（推荐设置）

YouTube 会重新编码所有内容，因此上传高质量：

```bash
# YouTube 优化（1080p）
ffmpeg -i out/video.mp4 \
  -c:v libx264 -preset slow -crf 18 \
  -profile:v high -level 4.0 \
  -bf 2 -g 30 \
  -c:a aac -b:a 192k -ar 48000 \
  -movflags +faststart \
  out/video-youtube.mp4

# YouTube Shorts（垂直 1080x1920）
ffmpeg -i out/video.mp4 \
  -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" \
  -c:v libx264 -crf 18 -c:a aac -b:a 192k \
  out/video-shorts.mp4
```

### Twitter/X

Twitter 严格限制：最大 140 秒，512MB，1920x1200：

```bash
# Twitter 优化（目标 15MB 快速上传）
ffmpeg -i out/video.mp4 \
  -c:v libx264 -preset medium -crf 24 \
  -profile:v main -level 3.1 \
  -vf "scale='min(1280,iw)':'min(720,ih)':force_original_aspect_ratio=decrease" \
  -c:a aac -b:a 128k -ar 44100 \
  -movflags +faststart \
  -fs 15M \
  out/video-twitter.mp4

# 检查文件大小和持续时间
ffprobe -v error -show_entries format=duration,size -of csv=p=0 out/video-twitter.mp4
```

### LinkedIn

LinkedIn 偏好 MP4 格式，AAC 音频，最大 10 分钟：

```bash
# LinkedIn 优化
ffmpeg -i out/video.mp4 \
  -c:v libx264 -preset medium -crf 22 \
  -profile:v main \
  -vf "scale='min(1920,iw)':'min(1080,ih)':force_original_aspect_ratio=decrease" \
  -c:a aac -b:a 192k -ar 48000 \
  -movflags +faststart \
  out/video-linkedin.mp4
```

### 网站/嵌入（优化快速加载）

```bash
# 网站优化 MP4（小文件，渐进式加载）
ffmpeg -i out/video.mp4 \
  -c:v libx264 -preset medium -crf 26 \
  -profile:v baseline -level 3.0 \
  -vf "scale=1280:720" \
  -c:a aac -b:a 128k \
  -movflags +faststart \
  out/video-web.mp4

# WebM 替代方案（更好压缩，更广泛的浏览器支持）
ffmpeg -i out/video.mp4 \
  -c:v libvpx-vp9 -crf 30 -b:v 0 \
  -vf "scale=1280:720" \
  -c:a libopus -b:a 128k \
  -deadline good \
  out/video-web.webm
```

### GIF（用于预览/缩略图）

```bash
# 高质量 GIF（前 5 秒）
ffmpeg -i out/video.mp4 -t 5 \
  -vf "fps=15,scale=480:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" \
  out/preview.gif

# 较小文件 GIF
ffmpeg -i out/video.mp4 -t 3 \
  -vf "fps=10,scale=320:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" \
  out/preview-small.gif
```

### 平台要求快速参考

| 平台 | 最大分辨率 | 最大大小 | 最大持续时间 | 音频 |
|------|-----------|----------|--------------|-------|
| YouTube | 8K | 256GB | 12 小时 | AAC 48kHz |
| Twitter/X | 1920x1200 | 512MB | 140 秒 | AAC 44.1kHz |
| LinkedIn | 4096x2304 | 5GB | 10 分钟 | AAC 48kHz |
| Instagram Feed | 1080x1350 | 4GB | 60 秒 | AAC 48kHz |
| Instagram Reels | 1080x1920 | 4GB | 90 秒 | AAC 48kHz |
| TikTok | 1080x1920 | 287MB | 10 分钟 | AAC |

### 批量导出所有平台

```bash
#!/bin/bash
# 保存为：export-all-platforms.sh
INPUT="out/video.mp4"

# YouTube（高质量）
ffmpeg -i "$INPUT" -c:v libx264 -preset slow -crf 18 \
  -c:a aac -b:a 192k -movflags +faststart \
  out/video-youtube.mp4

# Twitter（压缩）
ffmpeg -i "$INPUT" -c:v libx264 -crf 24 \
  -vf "scale='min(1280,iw)':'-2'" \
  -c:a aac -b:a 128k -movflags +faststart \
  out/video-twitter.mp4

# LinkedIn
ffmpeg -i "$INPUT" -c:v libx264 -crf 22 \
  -c:a aac -b:a 192k -movflags +faststart \
  out/video-linkedin.mp4

# 网站嵌入（小文件）
ffmpeg -i "$INPUT" -c:v libx264 -crf 26 \
  -vf "scale=1280:720" \
  -c:a aac -b:a 128k \
  -movflags +faststart \
  out/video-web.mp4

echo "导出："
ls -lh out/video-*.mp4
```

## 错误处理

处理视频时常见的错误和修复方法：

```bash
# 检查 FFmpeg 是否成功
ffmpeg -i input.mp4 -c:v libx264 output.mp4 && echo "成功" || echo "失败：检查输入文件"

# 验证输出文件是否可播放
ffprobe -v error -select_streams v:0 -show_entries stream=codec_name -of csv=p=0 output.mp4

# 获取详细错误信息
ffmpeg -v error -i input.mp4 -f null - 2>&1 | head -20
```

### 处理常见错误

| 错误 | 原因 | 修复 |
|------|------|------|
| "找不到文件" | 输入路径错误 | 检查路径，使用引号包含空格 |
| "无效数据" | 输入损坏 | 重新下载或重新录制源文件 |
| "高度不能被 2 整除" | 奇数尺寸 | 添加带 trunc 的缩放滤镜 |
| "找不到编码器" | 缺少编解码器 | 安装带完整编解码器的 FFmpeg |
| 输出 0 字节 | 无声失败 | 检查完整的 ffmpeg 输出以查找错误 |

---

## 反馈与贡献

如果这项技能缺少信息或可以改进：

- **缺少命令？** 描述你需要什么
- **发现错误？** 告诉我哪里有问题
- **想要贡献？** 我可以帮助你：
  1. 使用改进更新这项技能
  2. 创建 PR 到 github.com/digitalsamba/claude-code-video-toolkit

只需说 "改进这项技能"，我会指导你更新 `.claude/skills/ffmpeg/SKILL.md`。
