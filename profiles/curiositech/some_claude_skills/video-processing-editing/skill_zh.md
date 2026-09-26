# 视频处理与编辑

精通基于FFmpeg的视频编辑、处理自动化和导出优化，适用于现代内容创作工作流程。

## 使用场景

✅ **适用场景**：
- 自动化视频编辑流程（脚本到视频）
- 剪辑、裁剪、拼接片段
- 添加转场、特效、叠加层
- 音频混音和标准化
- 字幕/标题处理
- 平台导出优化
- 批量视频处理
- 色彩分级和校正

❌ **不适用场景**：
- 实时视频编辑界面（使用达芬奇 Resolve/Premiere）
- 3D合成（使用After Effects/Blender）
- 运动图形动画（使用After Effects）
- 基础屏幕录制（使用OBS）

---

## 技术选择

### 视频编辑工具

| 工具 | 速度 | 功能 | 应用场景 |
|------|-------|----------|----------|
| FFmpeg | 非常快 | 命令行自动化 | 生产流程 |
| MoviePy | 中等 | Python API | 程序化编辑 |
| PyAV | 快速 | 低级控制 | 自定义处理 |
| DaVinci Resolve | 慢 | 完整非线性编辑 | 手动编辑 |

**决策树**：
```
需要自动化？→ FFmpeg
需要Python API？→ MoviePy
需要帧级控制？→ PyAV
需要手动编辑？→ DaVinci Resolve
```

---

## 常见反模式

### 反模式1：未使用关键帧对齐的剪辑

**新手想法**： "随便在任意时间戳剪辑视频"

**问题**： 导致出现伪影、黑帧和播放问题。

**错误方法**：
```bash
# ❌ 随机时间戳剪辑（未对齐关键帧）
ffmpeg -i input.mp4 -ss 00:01:23.456 -to 00:02:45.678 -c copy output.mp4

# 结果：黑帧、伪影、同步问题
```

**为什么错误**：
- 视频编码器每2-10秒使用关键帧（I帧）
- 非关键帧剪辑需要重新编码
- 使用 `-c copy`（流复制）而未对齐关键帧会破坏播放
- GOP（图像组）结构依赖于关键帧

**正确方法1**： 重新编码以实现精确剪辑
```bash
# ✅ 重新编码进行帧精确剪辑
ffmpeg -i input.mp4 -ss 00:01:23.456 -to 00:02:45.678 \
  -c:v libx264 -crf 18 -preset medium \
  -c:a aac -b:a 192k \
  output.mp4

# 帧精确，但速度较慢（重新编码）
```

**正确方法2**： 关键帧对齐的流复制
```bash
# ✅ 快速剪辑（关键帧对齐）
# 第1步：查找剪辑点附近的关键帧
ffprobe -select_streams v -show_frames -show_entries frame=pkt_pts_time,key_frame \
  -of csv input.mp4 | grep ",1$" | awk -F',' '{print $2}'

# 第2步：在最近的关键帧处剪辑（快速，无需重新编码）
ffmpeg -i input.mp4 -ss 00:01:22.000 -to 00:02:46.000 -c copy output.mp4

# 极速，无质量损失，但非帧精确
```

**正确方法3**： 双路处理兼顾速度和精确度
```bash
# ✅ 快速定位+精确剪辑
ffmpeg -ss 00:01:20.000 -i input.mp4 \
  -ss 00:00:03.456 -to 00:01:25.678 \
  -c:v libx264 -crf 18 -preset medium \
  -c:a aac -b:a 192k \
  output.mp4

# -ss 在 -i 之前：快速定位到关键帧（无需解码）
# -ss 在 -i 之后：精确修剪（仅解码所需部分）
```

**性能对比**：
| 方法 | 1小时视频耗时 | 精确度 | 质量 |
|--------|---------------------|----------|---------|
| 流复制（任意） | 2秒 | ❌ 破坏 | ❌ 伪影 |
| 流复制（关键帧） | 2秒 | ±2秒 | ✅ 完美 |
| 重新编码（简单） | 15分钟 | ✅ 帧精确 | ⚠️ 质量损失 |
| 双路（最优） | 3分钟 | ✅ 帧精确 | ✅ 完美 |

**时间线背景**：
- 2010年：FFmpeg需要完整重新编码进行剪辑
- 2015年：添加 `-c copy` 用于流复制
- 2020年：双路剪辑成为最佳实践
- 2024年：硬件加速（NVENC）使重新编码可行

---

### 反模式2：不必要的重新编码

**新手想法**： "在一个FFmpeg命令中应用所有编辑"

**问题**： 多次重新编码导致累积质量损失。

**错误方法**：
```bash
# ❌ 每次操作重新编码（质量退化）
# 操作1：裁剪
ffmpeg -i input.mp4 -ss 00:01:00 -to 00:05:00 \
  -c:v libx264 -crf 23 temp1.mp4

# 操作2：添加音频
ffmpeg -i temp1.mp4 -i audio.mp3 -c:v libx264 -crf 23 \
  -map 0:v -map 1:a temp2.mp4

# 操作3：添加字幕
ffmpeg -i temp2.mp4 -vf subtitles=subs.srt \
  -c:v libx264 -crf 23 output.mp4

# 结果：3次重新编码 = 显著质量损失
```

**为什么错误**：
- 每次重新编码都是有损的（即使使用高CRF）
- 累积质量损失（代数损失）
- 3倍编码时间
- 浪费磁盘I/O

**正确方法1**： 单命令链式操作
```bash
# ✅ 单次编码包含所有操作
ffmpeg -ss 00:01:00 -i input.mp4 -i audio.mp3 \
  -to 00:04:00 \
  -vf "subtitles=subs.srt" \
  -map 0:v -map 1:a \
  -c:v libx264 -crf 18 -preset medium \
  -c:a aac -b:a 192k \
  output.mp4

# 单次重新编码，一次性应用所有操作
```

**正确方法2**： 尽可能使用流复制
```bash
# ✅ 流复制操作（无损）
# 裁剪（流复制）
ffmpeg -i input.mp4 -ss 00:01:00 -to 00:05:00 -c copy temp.mp4

# 添加音频（流复制视频，编码音频）
ffmpeg -i temp.mp4 -i audio.mp3 \
  -map 0:v -map 1:a \
  -c:v copy -c:a aac -b:a 192k \
  temp2.mp4

# 烧录字幕（必须重新编码视频）
ffmpeg -i temp2.mp4 -vf subtitles=subs.srt \
  -c:v libx264 -crf 18 -preset medium \
  -c:a copy \
  output.mp4

# 仅1次视频重新编码（用于字幕）
```

**质量对比**：
| 方法 | 编码次数 | 质量（VMAF） | 时间 |
|--------|-----------------|----------------|------|
| 3次重新编码（CRF 23） | 3 | 82/100 | 45分钟 |
| 单次编码（CRF 23） | 1 | 91/100 | 15分钟 |
| 流复制+1次编码 | 1 | 95/100 | 18分钟 |
| 全流复制 | 0 | 100/100 | 30秒 |

---

### 反模式3：忽略色彩空间转换

**新手想法**： "直接拼接视频"

**问题**： 色彩偏移、亮度不匹配、播放损坏。

**错误方法**：
```bash
# ❌ 色彩空间不同的视频拼接
# clip1.mp4: BT.709（高清），yuv420p
# clip2.mp4: BT.601（标清），yuvj420p（全范围）
# clip3.mp4: BT.2020（超高清），yuv420p10le

# 创建拼接列表
echo "file 'clip1.mp4'" > list.txt
echo "file 'clip2.mp4'" >> list.txt
echo "file 'clip3.mp4'" >> list.txt

# 无色彩归一化拼接
ffmpeg -f concat -safe 0 -i list.txt -c copy output.mp4

# 结果：片段间色彩偏移，HDR元数据损坏
```

**为什么错误**：
- 不同的色彩空间（BT.601 vs BT.709 vs BT.2020）
- 不同的像素格式（yuv420p vs yuvj420p）
- 不同的色彩范围（有限 vs 全范围）
- 元数据冲突

**正确方法**：
```bash
# ✅ 拼接前归一化色彩空间

# 第1步：分析每个片段的色彩空间
ffprobe -v error -select_streams v:0 \
  -show_entries stream=color_space,color_transfer,color_primaries,pix_fmt \
  -of default=noprint_wrappers=1 clip1.mp4

# 第2步：将所有片段归一化到通用色彩空间
# 目标：BT.709（高清），yuv420p，有限范围

# 归一化clip1（已为BT.709）
ffmpeg -i clip1.mp4 -c copy clip1_normalized.mp4

# 归一化clip2（BT.601标清 → BT.709高清）
ffmpeg -i clip2.mp4 \
  -vf "scale=in_range=full:out_range=limited,colorspace=bt709:iall=bt601:fast=1" \
  -color_primaries bt709 \
  -color_trc bt709 \
  -colorspace bt709 \
  -c:v libx264 -crf 18 -preset medium \
  -c:a copy \
  clip2_normalized.mp4

# 归一化clip3（BT.2020 HDR → BT.709 SDR）
ffmpeg -i clip3.mp4 \
  -vf "zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=limited,format=yuv420p" \
  -color_primaries bt709 \
  -color_trc bt709 \
  -colorspace bt709 \
  -c:v libx264 -crf 18 -preset medium \
  -c:a copy \
  clip3_normalized.mp4

# 第3步：拼接归一化片段
echo "file 'clip1_normalized.mp4'" > list.txt
echo "file 'clip2_normalized.mp4'" >> list.txt
echo "file 'clip3_normalized.mp4'" >> list.txt

ffmpeg -f concat -safe 0 -i list.txt -c copy output.mp4
```

**色彩空间指南**：
| 标准 | 色彩空间 | 转换 | 主色 | 应用场景 |
|----------|-------------|----------|-----------|----------|
| BT.601 | 标清 | bt470bg | bt470bg | 旧标清内容 |
| BT.709 | 高清 | bt709 | bt709 | 现代高清/FHD |
| BT.2020 | 超高清/HDR | smpte2084 | bt2020 | 4K HDR |
| sRGB | 网络 | iec61966-2-1 | bt709 | 网络交付 |

---

### 反模式4：音频同步差

**新手想法**： "视频和音频是分开的，直接叠加即可"

**问题**： 嘴唇同步问题、音频漂移、播放损坏。

**错误方法**：
```bash
# ❌ 替换音频不考虑同步
ffmpeg -i video.mp4 -i audio.mp3 \
  -map 0:v -map 1:a \
  -c:v copy -c:a copy \
  output.mp4

# 问题：
# - 音频时长 ≠ 视频时长
# - 无音频拉伸/压缩
# - 随时间漂移
```

**为什么错误**：
- 音频和视频时长不同
- 无时间基准同步
- 无漂移校正
- 忽略原始音频同步

**正确方法1**： 调整音频速度匹配视频
```bash
# ✅ 调整音频速度匹配视频时长

# 获取时长
VIDEO_DUR=$(ffprobe -v error -show_entries format=duration \
  -of default=noprint_wrappers=1:nokey=1 video.mp4)
AUDIO_DUR=$(ffprobe -v error -show_entries format=duration \
  -of default=noprint_wrappers=1:nokey=1 audio.mp3)

# 计算速度比
RATIO=$(echo "$VIDEO_DUR / $AUDIO_DUR" | bc -l)

# 拉伸音频匹配视频（带音高校正）
ffmpeg -i video.mp4 -i audio.mp3 \
  -filter_complex "[1:a]atempo=${RATIO}[a]" \
  -map 0:v -map "[a]" \
  -c:v copy -c:a aac -b:a 192k \
  output.mp4
```

**正确方法2**： 精确偏移和修剪
```bash
# ✅ 音频偏移与修剪同步

# 音频延迟0.5秒，修剪匹配视频
ffmpeg -i video.mp4 -itsoffset 0.5 -i audio.mp3 \
  -map 0:v -map 1:a \
  -shortest \
  -c:v copy -c:a aac -b:a 192k \
  output.mp4

# -itsoffset: 音频延迟0.5秒
# -shortest: 修剪到最短流
```

**正确方法3**： 精确时间混合多音频轨道
```bash
# ✅ 精确时间混合对话、音乐、音效

ffmpeg -i video.mp4 -i dialogue.wav -i music.mp3 -i sfx.wav \
  -filter_complex "
    [1:a]adelay=0|0[dlg];
    [2:a]volume=0.3,adelay=500|500[mus];
    [3:a]adelay=1200|1200[sfx];
    [dlg][mus][sfx]amix=inputs=3:duration=first[a]
  " \
  -map 0:v -map "[a]" \
  -c:v copy -c:a aac -b:a 256k \
  output.mp4

# adelay: 精确毫秒级时间
# amix: 混合多个音频流
# volume: 归一化音量
```

**音频同步检查清单**：
```
□ 验证视频和音频时长匹配
□ 使用 -shortest 防止多余音频
□ 应用 adelay 精确时间偏移
□ 使用 atempo 调整速度（保持音高）
□ 适当设置音频比特率（128k-256k）
□ 在开头、中间、结尾测试唇同步
```

---

### 反模式5：平台不合适的编码/比特率

**新手想法**： "所有平台使用同一导出设置"

**问题**： 浪费带宽、质量差、上传被拒、兼容性问题。

**错误方法**：
```bash
# ❌ 所有内容导出为4K 50 Mbps
ffmpeg -i input.mp4 \
  -c:v libx264 -b:v 50M -s 3840x2160 \
  -c:a aac -b:a 320k \
  output.mp4

# 对于Instagram故事：2GB文件被拒（最大100MB）
# 对于YouTube：可用10 Mbps且外观相同
# 对于Twitter：超出比特率限制
```

**为什么错误**：
- 平台特定的文件大小/比特率限制
- 过度编码浪费带宽
- 错误分辨率不适用于平台
- 不兼容编码器

**正确方法**： 平台优化导出

**YouTube（推荐设置）**：
```bash
# ✅ YouTube 1080p上传
ffmpeg -i input.mp4 \
  -c:v libx264 -preset slow -crf 18 \
  -s 1920x1080 -r 30 \
  -pix_fmt yuv420p \
  -color_primaries bt709 -color_trc bt709 -colorspace bt709 \
  -movflags +faststart \
  -c:a aac -b:a 192k -ar 48000 \
  youtube_1080p.mp4

# YouTube 4K上传
ffmpeg -i input.mp4 \
  -c:v libx264 -preset slow -crf 18 \
  -s 3840x2160 -r 60 \
  -pix_fmt yuv420p \
  -movflags +faststart \
  -c:a aac -b:a 256k -ar 48000 \
  youtube_4k.mp4
```

**Instagram（故事、Reels、Feed）**：
```bash
# ✅ Instagram故事（9:16，最大100MB，15秒）
ffmpeg -i input.mp4 \
  -c:v libx264 -preset medium -crf 23 \
  -s 1080x1920 -r 30 -t 15 \
  -pix_fmt yuv420p \
  -movflags +faststart \
  -c:a aac -b:a 128k \
  instagram_story.mp4

# ✅ Instagram Reels（9:16，最大90秒）
ffmpeg -i input.mp4 \
  -c:v libx264 -preset medium -crf 23 \
  -s 1080x1920 -r 30 -t 90 \
  -pix_fmt yuv420p \
  -movflags +faststart \
  -c:a aac -b:a 128k \
  instagram_reel.mp4

# ✅ Instagram Feed（1:1或4:5）
ffmpeg -i input.mp4 \
  -c:v libx264 -preset medium -crf 23 \
  -s 1080x1080 -r 30 \
  -pix_fmt yuv420p \
  -movflags +faststart \
  -c:a aac -b:a 128k \
  instagram_feed.mp4
```

**Twitter/X**:
```bash
# ✅ Twitter视频（最大512MB，2:20）
ffmpeg -i input.mp4 \
  -c:v libx264 -preset medium -crf 23 \
  -s 1280x720 -r 30 -t 140 \
  -maxrate 5000k -bufsize 10000k \
  -pix_fmt yuv420p \
  -movflags +faststart \
  -c:a aac -b:a 128k \
  twitter.mp4
```

**TikTok**:
```bash
# ✅ TikTok（9:16，最大287MB，10分钟）
ffmpeg -i input.mp4 \
  -c:v libx264 -preset medium -crf 23 \
  -s 1080x1920 -r 30 -t 600 \
  -pix_fmt yuv420p \
  -movflags +faststart \
  -c:a aac -b:a 128k \
  tiktok.mp4
```

**网络（HTML5视频）**：
```bash
# ✅ 网络优化（快速加载，广泛兼容）
ffmpeg -i input.mp4 \
  -c:v libx264 -preset medium -crf 23 \
  -s 1920x1080 -r 30 \
  -pix_fmt yuv420p \
  -profile:v baseline -level 3.0 \
  -movflags +faststart \
  -c:a aac -b:a 128k -ar 48000 \
  web.mp4
```

**平台规格表**：
| 平台 | 最大大小 | 最大时长 | 分辨率 | FPS | 比特率 | 编码器 |
|----------|----------|----------|--------|-----|---------|-------|
| YouTube | 无限 | 无限 | 8K | 60 | 自动 | H.264/VP9 |
| Instagram Story | 100 MB | 15秒 | 1080x1920 | 30 | ~5 Mbps | H.264 |
| Instagram Reel | 1 GB | 90秒 | 1080x1920 | 30 | ~8 Mbps | H.264 |
| Twitter | 512 MB | 2:20 | 1920x1080 | 60 | 5 Mbps | H.264 |
| TikTok | 287 MB | 10分钟 | 1080x1920 | 30 | ~4 Mbps | H.264 |
| LinkedIn | 5 GB | 10分钟 | 1920x1080 | 30 | 5 Mbps | H.264 |
| 网络 | 变化 | 变化 | 1920x1080 | 30 | 2-5 Mbps | H.264 |

**导出优化检查清单**：
```
□ 使用 -movflags +faststart 为网络（渐进式下载）
□ 使用 -pix_fmt yuv420p 以确保广泛兼容
□ 设置 -r 30（避免可变帧率）
□ 使用 -preset slow 进行最终导出（更好质量）
□ 使用 -preset ultrafast 进行草稿
□ 应用 -maxrate 和 -bufsize 用于流式传输
□ 在批量导出前在目标平台测试播放
```

---

## 生产检查清单

```
□ 对齐剪辑到关键帧（或双路定位）
□ 单FFmpeg命令链式操作
□ 拼接前归一化色彩空间
□ 验证音频/视频同步（多点测试）
□ 使用平台特定导出预设
□ 应用 -movflags +faststart 用于网络交付
□ 设置正确的色彩元数据（高清使用bt709）
□ 在目标平台测试输出文件
□ 保留无损中间文件（ProRes, FFV1）
□ 批量作业使用硬件加速（NVENC, VideoToolbox）
```

---

## 使用场景与避免

| 场景 | 适用？ |
|----------|--------|
| 自动化视频流程（脚本到视频） | ✅ 是 - FFmpeg自动化 |
| 批量处理100个视频 | ✅ 是 - 并行FFmpeg作业 |
| 程序化剪辑/裁剪片段 | ✅ 是 - 精确剪辑 |
| 为视频添加字幕 | ✅ 是 - 烧录或软字幕 |
| 色彩分级素材 | ⚠️ 有限 - 仅基础操作 |
| 多机位编辑 | ❌ 否 - 使用DaVinci Resolve |
| 运动图形 | ❌ 否 - 使用After Effects |
| 实时预览编辑 | ❌ 否 - 使用Premiere/Resolve |

---

## 参考文献

- `/references/ffmpeg-guide.md` - 完整FFmpeg命令参考
- `/references/timeline-editing.md` - 时间线概念，多轨道编辑
- `/references/export-optimization.md` - 平台特定导出设置

## 脚本

- `scripts/video_editor.py` - 剪辑、裁剪、拼接、转场、特效
- `scripts/batch_processor.py` - 并行批量视频处理

---

**此技能涵盖**： 视频编辑 | FFmpeg | 时间线编辑 | 转场 | 导出优化 | 音频混音 | 色彩分级 | 自动化视频生产
