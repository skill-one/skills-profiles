# 技能：视频转 GIF

将视频文件转换为多个具有不同参数的 GIF 变体，以便用户可以直观地比较并选择最佳效果。

> **前提条件**：必须安装 FFmpeg 和 uv。gifsicle 为可选（启用有损压缩变体）。

---

## 使用场景

用户想从视频片段中创建 GIF，但不确定合适的参数。GIF 质量涉及以下权衡：
- **文件大小** — 越小越好，便于分享/嵌入
- **颜色精度** — 颜色越少文件越小，但可能导致色带现象
- **平滑度** — FPS 越高越平滑，但文件越大
- **分辨率** — 越宽细节越清晰，但文件越大

与其猜测，此技能会生成多个变体供用户选择。

---

## 默认工作流程

当用户提供视频文件时：

```bash
uv run --python 3.12 /path/to/skills/video-to-gif/scripts/video_to_gif.py <input.mp4>
```

这将在 `<input>_gifs/` 目录中生成 GIF，使用 **完整** 预设（18 个变体）：
- 3 个 FPS 选项：10、15、20
- 3 个宽度：480px、640px、800px
- 2 个颜色数量：128、256

输出包括一个排序后的比较表格，显示每个变体的文件大小、FPS、宽度和颜色数量。

---

## 预设

| 预设 | 变体数量 | 适用场景 |
|------|----------|----------|
| `full` | ~18 | 通用使用 — 广泛探索参数空间 |
| `minimal` | ~4 | 快速比较 — 仅几个关键权衡点 |
| `lossy` | ~12 | 最小文件 — 包含 gifsicle 有损压缩级别 |
| `quality` | ~12 | 最佳视觉效果 — 更高分辨率，包含 Bayer 滤波器抖动 |

```bash
# 使用较少变体进行快速比较
uv run --python 3.12 .../video_to_gif.py input.mp4 --presets minimal

# 包含有损压缩（需要 gifsicle）
uv run --python 3.12 .../video_to_gif.py input.mp4 --presets lossy

# 侧重高质量
uv run --python 3.12 .../video_to_gif.py input.mp4 --presets quality
```

---

## 常用选项

| 标志 | 默认值 | 描述 |
|------|---------|-------------|
| `-o`, `--output-dir` | `<input>_gifs/` | 所有 GIF 变体的输出目录 |
| `--start` | 无 | 开始时间（秒）（裁剪源视频） |
| `--end` | 无 | 结束时间（秒）（裁剪源视频） |
| `--presets` | `full` | 预设配置：full、minimal、lossy、quality |
| `--fps` | 预设 | 覆盖 FPS 值（例如，`--fps 10 15 20`） |
| `--width` | 预设 | 覆盖宽度值（例如，`--width 480 640`） |
| `--colors` | 预设 | 覆盖颜色数量（例如，`--colors 128 256`） |
| `--lossy` | 预设 | gifsicle 有损级别（例如，`--lossy 0 30 80`） |

---

## 示例

```bash
# 转换视频的前 10 秒
uv run --python 3.12 .../video_to_gif.py demo.mp4 --end 10

# 提取特定片段
uv run --python 3.12 .../video_to_gif.py demo.mp4 --start 5 --end 15

# 自定义参数扫描
uv run --python 3.12 .../video_to_gif.py demo.mp4 --fps 12 15 --width 480 800 --colors 256

# 有损压缩比较（需要 gifsicle）
uv run --python 3.12 .../video_to_gif.py demo.mp4 --lossy 0 30 60 100
```

---

## 如何选择

运行后，打开输出目录进行比较：

1. **从最小文件开始** — 检查质量是否可接受
2. **检查色带现象** — 如果可见，尝试 256 颜色或 Bayer 滤波器抖动（quality 预设）
3. **检查平滑度** — 如果太卡顿，提高至 15 或 20 FPS
4. **检查清晰度** — 如果文字无法辨认，提高至 640 或 800px 宽度

大多数屏幕录制视频的最佳效果通常在 **640px、15fps、256颜色** 左右。

---

## 重要提示

- 宽度大于源视频分辨率的将被自动跳过。
- 脚本使用 FFmpeg 的双通道调色板生成，效果优于单通道。
- gifsicle 有损压缩可在 30-60 级别下将文件大小减少 30-70%，且视觉效果影响极小。
- 对于非常长的片段，建议先使用 `--start`/`--end` 裁剪 — 超过 10 秒的 GIF 可能会变得非常大。
