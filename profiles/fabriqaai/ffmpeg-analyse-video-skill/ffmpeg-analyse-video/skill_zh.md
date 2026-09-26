# FFmpeg 视频分析

使用 ffmpeg 从视频文件中提取帧。将帧读取工作委托给子代理以保留主上下文窗口。从纯文本子代理报告中综合生成结构化的带时间戳的摘要。

## 架构：上下文高效的子代理管道

**问题**：将数十张图像读入主对话上下文会占用大部分上下文窗口，几乎没有空间用于综合和后续处理。

**解决方案**：一个三阶段管道：

```
主代理                          子代理（可丢弃上下文）
──────────                          ──────────────────────────────
1. ffprobe 元数据        ───►
2. ffmpeg 帧提取 ───►
3. 将帧分批 ──►   4. 读取图像（视觉）
                                      将文本描述写入 batch_N_analysis.md
5. 仅读取文本文件    ◄───    (上下文被丢弃)
6. 综合最终输出
```

图像仅存在于子代理的上下文中。主代理仅读取轻量级文本文件。这使上下文使用量减少了约 90%。

## 1. 前置条件

```bash
which ffmpeg && which ffprobe
```

如果缺少任一程序，请显示平台特定的安装说明并停止：
- **macOS**：`brew install ffmpeg`
- **Ubuntu/Debian**：`sudo apt install ffmpeg`
- **Windows**：`choco install ffmpeg` 或 `winget install ffmpeg`

## 2. 设置临时目录

```bash
# macOS/Linux
TMPDIR="/tmp/video-analysis-$(date +%s)"
mkdir -p "$TMPDIR"

# Windows (PowerShell)
# $TMPDIR = "$env:TEMP\video-analysis-$(Get-Date -UFormat %s)"
# New-Item -ItemType Directory -Path $TMPDIR
```

## 3. 提取视频元数据

```bash
ffprobe -v quiet -print_format json -show_format -show_streams "VIDEO_PATH"
```

提取并报告：时长、分辨率（宽度 x 高度）、帧率、编解码器、文件大小、是否包含音频。

如果没有找到视频流，则报告“仅音频文件”并停止。
如果文件大小 > 2GB，则警告用户并建议使用 `-ss START -to END` 分析时间范围。

## 4. 提取帧

根据时长选择策略：

| 时长     | 策略         | 命令                                                                 |
|----------|--------------|----------------------------------------------------------------------|
| 0-60s    | 每 2 秒 1 帧 | `ffmpeg -hide_banner -y -i INPUT -vf "fps=1/2,scale='min(1280,iw)':-2" -q:v 5 DIR/frame_%04d.jpg` |
| 1-10min  | 场景检测（阈值 0.3） | `ffmpeg -hide_banner -y -i INPUT -vf "select='gt(scene,0.3)',scale='min(1280,iw)':-2" -vsync vfr -q:v 5 DIR/scene_%04d.jpg` |
| 10-30min | 关键帧提取   | `ffmpeg -hide_banner -y -skip_frame nokey -i INPUT -vf "scale='min(1280,iw)':-2" -vsync vfr -q:v 5 DIR/key_%04d.jpg` |
| 30min+   | 缩略图过滤器 | `ffmpeg -hide_banner -y -i INPUT -vf "thumbnail=SEGMENT_FRAMES,scale='min(1280,iw)':-2" -vsync vfr -q:v 5 DIR/thumb_%04d.jpg` |

对于缩略图过滤器，计算 `SEGMENT_FRAMES = total_frames / 60` 以将输出限制在约 60 帧。

**备用方案**：
- 场景检测产生 0 帧 → 使用 1 帧/5 秒的间隔重试
- 提取的帧超过 100 帧 → 均匀抽样到 80 帧
- 帧提取失败 → 尝试下一个更简单的策略（场景 → 间隔，关键帧 → 间隔）

**时间范围分析**：当用户指定范围时，在 `-i` 之前添加 `-ss START -to END`。
**更高细节模式**：如果请求，将帧率加倍并将场景阈值降低到 0.2。

提取后，列出所有帧文件并从其序列号和提取速率计算每个帧的时间戳。

## 5. 将帧分析委托给子代理

**这是节省上下文的关键步骤。** 不要在主对话中读取帧图像。相反，将帧分批并委托每个批次给一个子代理。

### 5a. 准备批次清单

将提取的帧文件列表分成每批 8-10 帧的批次。对于每个批次，记录：
- 批次编号（1、2、3、...）
- 帧文件路径（绝对路径）
- 帧时间戳（从序列号计算）
- 输出文件路径：`TMPDIR/batch_N_analysis.md`

### 5b. 启动子代理

为每个批次使用以下提示启动一个子代理。**如果工具支持，并行启动所有批次** — 它们是完全独立的。

#### 子代理提示模板

使用此提示的原文，替换占位符：

```
你正在分析从视频文件提取的帧。

VIDEO: {filename}
DURATION: {duration}
BATCH: {batch_number} of {total_batches}

使用 Read 工具（或支持图像的等效文件读取工具）读取下面列出的每个帧图像。对于每个帧，编写结构化的描述。

FRAMES:
{对于批次中的每个帧}
- {绝对路径到帧} (timestamp: {MM:SS})
{结束 for}

对于每个帧，描述：
1. SCENE：可见内容（布局、UI 元素、环境）
2. CONTENT：屏幕上可见的文本、代码、标签、菜单或对话
3. ACTION：自可能的前一帧发生或改变的内容
4. DETAILS：任何值得注意的细节（错误消息、URL、文件名、按钮状态）

描述所有帧后，添加 BATCH SUMMARY 部分，包含：
- 内容类型（之一：屏幕录制、演示文稿、教程、素材、动画）
- 此批次时间范围内的关键事件
- 用户输入的任何文本/提示/命令（精确引用）

将完整分析写入：{TMPDIR}/batch_{N}_analysis.md

格式化输出文件为：

# Batch {N} Analysis ({start_timestamp} - {end_timestamp})

## Frame-by-Frame

### Frame {sequence} ({timestamp})
- **Scene**: ...
- **Content**: ...
- **Action**: ...
- **Details**: ...

（对每个帧重复）

## Batch Summary
- **Content Type**: ...
- **Key Events**: ...
- **Quoted Text/Prompts**: ...
```

#### 如何启动

使用你提供的子代理、后台任务或独立代理机制。要求很简单 — 每个子代理需要：

1. **读取图像文件**（帧 JPEG）
2. **写入文本文件**（批次分析 markdown）

如果工具支持，并行启动所有批次 — 它们是完全独立的，没有共享状态。

**如果你的工具没有子代理机制**，则回退到在主上下文中直接读取帧，但最多限制为 **20 帧**，并警告用户关于上下文使用。

### 5c. 收集结果

所有子代理完成后，读取文本分析文件。这些是轻量级的 markdown — 没有图像进入主上下文。

```bash
ls TMPDIR/batch_*_analysis.md
```

按顺序读取每个 `batch_N_analysis.md` 文件。这些文件只包含文本描述 — 与读取原始图像相比，上下文成本最小。

## 6. 综合输出

仅使用批次分析文件的文本，在主上下文中执行综合：

1. 将所有帧描述合并为一个按时间顺序排列的时间线
2. 将帧分组为自然段（相同场景、幻灯片或屏幕）
3. 检测所有批次中的主要内容类型
4. 确定 3-7 个关键时刻
5. 提取用户输入的所有引用文本、提示或命令
6. 编写 2-5 句的叙述性摘要

格式化输出为：

```markdown
# 视频分析：[filename]

## 元数据
| 属性     | 值       |
|----------|----------|
| 时长     | M:SS     |
| 分辨率   | WxH      |
| 帧率     | N        |
| 内容类型 | [检测到]  |
| 分析帧数 | N        |

## 时间线
### [段标题] (M:SS - M:SS)
此段中发生的内容描述。

### [段标题] (M:SS - M:SS)
此段中发生的内容描述。

## 关键时刻
1. **[M:SS] 标题**：描述
2. **[M:SS] 标题**：描述
3. **[M:SS] 标题**：描述

## 摘要
[2-5 句总结整个视频的叙述性段落]
```

## 7. 清理

输出完成后删除临时目录：

```bash
# macOS/Linux
rm -rf "$TMPDIR"

# Windows (PowerShell)
# Remove-Item -Recurse -Force $TMPDIR
```

如果用户要求保留帧，则跳过清理。

## 高级选项

- **时间范围**： "分析视频.mp4 的 2:00 到 5:00" → 使用 `-ss 120 -to 300`
- **更高细节**： "以高细节分析" → 将帧率加倍并将场景阈值降低到 0.2
- **关注区域**： "关注显示的代码" → 在子代理提示中优先提取文本/代码
- **精灵表**： 为视觉概览，生成联系表：
  ```bash
  ffmpeg -hide_banner -y -i INPUT -vf "select='not(mod(n,EVERY_N))',scale='min(320,iw)':-2,tile=5xROWS" -frames:v 1 DIR/sprite.jpg
  ```

## 错误处理

- ffmpeg 未找到 → 按平台提供安装说明，停止
- 没有视频流 → 报告仅音频，停止
- 场景检测产生 0 帧 → 回退到间隔
- 帧过多（>100）→ 均匀抽样到 80
- 文件过大（>2GB）→ 警告，建议时间范围
- 子代理失败或超时 → 直接读取该批次的帧作为备用，警告关于上下文使用
- 子代理中帧读取失败 → 跳过帧，在批次分析文件中注明间隙
