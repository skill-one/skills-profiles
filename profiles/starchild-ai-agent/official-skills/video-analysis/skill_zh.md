# 视频分析

使用**原生模型理解**或**帧提取+转录**来分析视频文件。

⚠️ **URL输入（YouTube / TikTok / IG / Apple Podcasts / Spotify / 任何链接）？**
这项技能需要**本地文件路径**。对于链接，请**不要下载媒体**。
根据输入类型顺序路由，并在第一个产生文本的级别停止：

1. **播客节目链接或节目名称**（Apple Podcasts、Spotify、Overcast、发布者网站，或只是“关于X的a16z节目”）→ 使用`web_search`搜索发布者的节目页面/节目笔记/文本页面，然后使用`web-crawler.scrape_markdown(url)`读取。大多数主要节目都会发布文本。
2. **视频URL** → `web-crawler.youtube_video(url)` / `youtube_transcript(url)`（云端字幕，~1秒，无需下载；TikTok有`tiktok_transcript`）。
3. **`web_fetch`返回空**（`empty_extraction`，JS渲染页面）→ 使用`web-crawler.scrape_markdown`重试相同的URL——它渲染JS。永远不要从空的普通获取得出“没有字幕”的结论。
4. **未找到任何内容** → 直接报告并询问。本地下载+`analyze_video()`仅在用户明确要求下载媒体或交给你文件时运行。这不是后备方案：数据中心IP会触发机器人检查，100MB的音频拉取需要几分钟，通常失败。

转录文本仅包含语音——仅凭它无法命名说话者（参见web-crawler的元数据优先规则）。

## 工作原理
```
analyze_video(path, question)
      │
      ├─ file_size ≤ threshold (默认20MB)
      │     → 将视频发送到支持视频的模型（默认Gemini 3.1 Flash Lite）
      │     → 模型原生查看完整视频（最佳质量）
      │
      └─ file_size > threshold
            → ffmpeg提取关键帧（长视频的场景检测）
            → Whisper转录音频轨道
            → 返回帧图像路径+转录文本
            → 代理将这些输入当前聊天模型
```

## 快速入门
⚠️ **调用——不要使用点式导入。** 目录名包含连字符（`video-analysis`），所以`from skills.video-analysis.exports import ...`是**Python语法错误**（`-`被解析为减号）。这对每个带连字符的技能都适用，而不仅仅是这个。使用以下两种模式之一。

**模式A——从工作区根目录（推荐用于脚本）：**
```bash
cd /data/workspace/skills/video-analysis && \
  python3 -c "from exports import analyze_video; \
    import json; \
    print(json.dumps(analyze_video('output/videos/clip.mp4', \
      question='What happens in this video?'), ensure_ascii=False))"
```
注意：传递视频路径**工作区相对路径**（analyze.py将其与`WORKSPACE_DIR`解析），即使你cd到技能目录。

**模式B——在starchild-clawd脚本内：**
```python
from core.skill_tools import video_analysis
result = video_analysis.analyze_video("output/videos/clip.mp4",
                                      question="What happens in this video?")
```

❌ **不要** `exec(open('skills/video-analysis/analyze.py').read())`——analyze.py在导入时使用`__file__`，在`exec`下未定义，所以它崩溃。如果你必须避免上述两种模式，请使用`importlib.util.spec_from_file_location`按文件路径加载。

```python
# result键（两种模式相同）：
# 分析视频——自动选择原生模式或提取模式
# result = analyze_video("output/videos/clip.mp4", question="What happens in this video?")

# result键：
#   success: bool
#   mode: "native" | "extraction"
#
# 如果mode == "native":
#   analysis: str (模型的文本响应)
#   model: str (使用的模型)
#   tokens: {input, output, video, audio}
#
# 如果mode == "extraction":
#   frame_paths: list[str] (工作区相对路径到关键帧JPEG)
#   transcript: str | None (Whisper转录文本)
#   frame_count: int
#   duration_sec: float
```

## 使用导出
```python
from core.skill_tools import video_analysis

# 全部分析（自动选择模式）
result = video_analysis.analyze_video("output/videos/my_video.mp4", question="描述这个视频")

# 检查当前配置
config = video_analysis.get_config()

# 获取视频元数据而不分析
info = video_analysis.get_video_info("output/videos/my_video.mp4")
# → {"duration": 45.2, "size": 12345678, "width": 1920, "height": 1080, "has_audio": true}
```

## 原生模式（小视频）
对于小于大小阈值的视频，该技能将完整视频发送到支持原生视频输入的模型。模型查看每一帧并听到音频。

**默认模型：** `google/gemini-3.1-flash-lite`——视频的最佳性价比。

**模型基准**（6MB片段，与`gemini-3.1-pro-preview`基线对比）：

| 模型                       | 等级   | 成本     | 时间  | 准确性 | 备注                          |
|-----------------------------|--------|----------|-------|----------|--------------------------------|
| google/gemini-3.1-flash-lite | 经济型 | ~$0.0014 | 8.1s  | ~88%     | ⭐ 默认——最便宜+最快 |
| google/gemini-3.5-flash     | 标准   | ~$0.0152 | 11.8s | ~85%     | 更详细，成本更高       |
| qwen/qwen3.6-plus           | 经济型 | ~$0.0058 | 44.2s | ~95%     | 准确但慢              |
| qwen/qwen3.6-flash          | 经济型 | ~$0.0027 | 16.6s | ~80%     | 有时误读主体            |
| google/gemini-3.1-pro-preview | 标准  | ~$0.0199 | 19.7s | 100%     | 基线（最好，最贵）|

flash-lite正确识别完整场景、动作序列和过渡，成本比Pro基线低约14倍。对于最大准确度（精确角色名称、细节），将`default_model`更改为`gemini-3.1-pro-preview`或`gemini-3.5-flash`在`config/video-analysis.yaml`中。

## 提取模式（大视频）
对于大于大小阈值的视频，该技能提取关键帧并转录音频：

- **短视频（≤60秒）：** 每 N 秒一帧（默认：2秒）
- **长视频（>60秒）：** 场景变化检测选择视觉上不同的帧
- **音频：** 提取并发送到Whisper进行转录
- **最大帧数：** 限制在30（可配置）以控制成本

代理接收帧图像路径和转录文本，然后将它们作为图像附件+上下文文本输入当前聊天模型。

## 配置
编辑**`config/video-analysis.yaml`**（在工作区中）进行自定义。此文件在首次使用时自动创建，只需覆盖您想要修改的键，并且**在技能更新时保留**。

> 不要编辑`skills/video-analysis/config.yaml`——那是工厂默认值，并且在每次技能自动更新时被覆盖。用户文件覆盖它。

独立的技能和聊天“发送视频”流程都读取此相同的配置，因此一次编辑会更改所有地方的模型。可用键：

```yaml
# 用于原生视频理解的模型
default_model: google/gemini-3.1-flash-lite

# 大小阈值：原生（≤）vs 提取（>
# 设置为0 → 始终提取。设置为100 → 始终原生。
native_size_limit_mb: 20

# 帧提取设置
extraction:
  max_frames: 30                  # 最大关键帧数
  short_video_interval_sec: 2     # ≤60秒视频的帧间隔
  scene_threshold: 0.3            # 场景检测灵敏度（0.0-1.0）
  transcribe_audio: true          # 是否Whisper转录音频
```

### 可用的视频模型

| 模型                         | 别名    | 等级     | 备注              |
|-------------------------------|----------|----------|--------------------|
| google/gemini-3.1-flash-lite  | flash31  | 经济型   | ⭐ 默认，最佳性价比 |
| google/gemini-3.5-flash       | gemini35 | 标准     | 更详细，成本更高 |
| google/gemini-3.1-flash-lite  | flash31  | 经济型   | 最便宜选项    |
| google/gemini-3.1-pro-preview | gemini   | 标准     | 最高质量    |
| qwen/qwen3.6-flash            | qwenf    | 经济型   | 良好替代方案   |
| qwen/qwen3.6-plus             | qwen     | 经济型   | —                  |
| minimax/minimax-m3             | mm3      | 标准     | —                  |
| meta-llama/llama-4-maverick    | maverick | 标准     | —                  |
| meta-llama/llama-4-scout       | scout    | 经济型   | —                  |
| xiaomi/mimo-v2.5               | mimo     | 标准     | —                  |
| z-ai/glm-5v-turbo             | glm5v    | 标准     | —                  |
| minimax/minimax-m2.7           | mm27     | 经济型   | 仅音频，无图像 |

## 代理行为
当用户提供视频文件（通过上传或文件路径），并且当前聊天模型不支持视频时：

1. 调用`analyze_video(path, question)`。
2. 如果结果模式是`"native"` → 直接返回`result["analysis"]`。
3. 如果结果模式是`"extraction"` → 使用`result["frame_paths"]`作为图像引用，并使用`result["transcript"]`作为上下文，然后要求当前模型根据帧+转录进行分析。

当当前模型支持视频时，后端通过Phase 1（base64内容块注入）原生处理——无需此技能。

## 故障排除
| 问题       | 解决方法 |
|---------|-----|
| "文件未找到" | 检查路径是工作区相对路径（例如`output/videos/x.mp4`） |
| 原生模式返回错误 | 检查`config/video-analysis.yaml`中的`default_model`是否有效 |
| 无音频转录 | 视频可能没有音频轨道；检查结果中的`has_audio` |
| 提取的帧太少 | 在`config/video-analysis.yaml`中降低`scene_threshold`（例如0.15） |
| 帧太多/成本过高 | 减少`max_frames`或提高`scene_threshold` |
