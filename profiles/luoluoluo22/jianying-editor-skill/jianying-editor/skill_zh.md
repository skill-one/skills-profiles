# 剪映编辑器技能

当用户希望自动化视频剪辑、生成草稿或操作剪映专业版中的媒体素材时，使用此技能。

代理执行剧本：[docs/agent-playbook.md](docs/agent-playbook.md)
最小命令标准操作程序：[docs/minimal-command-sop.md](docs/minimal-command-sop.md)
自然语言使用指南：[usage.md](usage.md)
草稿检查器 CLI：
`python <SKILL_ROOT>/scripts/draft_inspector.py list --limit 20`
`python <SKILL_ROOT>/scripts/draft_inspector.py summary --name "DraftName"`
`python <SKILL_ROOT>/scripts/draft_inspector.py show --name "DraftName" --kind content --json`
对于通用编辑请求，始终遵循剧本中的“快速编辑运行模板”和“验收清单”。

## 🚨 重要开发原则 (CRITICAL DEVELOPER RULES)
1.  **脚本位置**：**禁止在 Skill 内部目录创建剪辑脚本**。所有剪辑逻辑实现代码（`.py` 脚本）必须存放在用户当前项目的**根目录**（或子目录，如 `scripts/`），以保持技能库的纯净和可移植性。
2.  **版本与架构**：
    - **双平台适配**：已全面支持 MacOS (路径探测/录屏) 与 Windows。
    - **Auto-healing**：支持 v5.9+ (`draft_info.json`)。若草稿损坏或版本冲突，使用 `overwrite=True` 初始化 `JyProject` 可触发自动修复。
3.  **配乐选择**：
    - **简单演示使用默认音乐**。实际项目，应优先检索并推荐 `data/cloud_music_library.csv` 中的相关曲目，或根据视频主题（如“科技”、“温暖”）进行关键词过滤。
    - 询问用户：“我发现了几首符合主题的云端音乐，要不要试试？（如：`Illuminate` - 科技感）”。

##  规则指南 (Rules)

阅读单个规则文件以了解特定任务和约束：

- [rules/setup.md](rules/setup.md) - **必须**的初始化代码，适用于所有脚本。
- [rules/core.md](rules/core.md) - 核心操作：保存、导出和草稿管理。
- [rules/cli.md](rules/cli.md) - CLI 合同和机器可读输出约定。
- [rules/media.md](rules/media.md) - 导入素材 & **AI 视频分析优化 (30m/360p)**。
- [rules/text.md](rules/text.md) - 添加字幕、文本和标题。
- [rules/keyframes.md](rules/keyframes.md) - **高级**：添加关键帧动画。
- [rules/effects.md](rules/effects.md) - 搜索和应用滤镜、效果和转场。
- [rules/recording.md](rules/recording.md) - **新**：屏幕录制与智能变焦自动化。
- [rules/web-vfx.md](rules/web-vfx.md) - 高级：网页到视频生成。
- [rules/generative.md](rules/generative.md) - 思维链用于生成式编辑。
- [rules/audio-voice.md](rules/audio-voice.md) - **新**：TTS 配音与背景音乐获取。

## 🎯 Agent 快速路由

- 云端视频 + 云端音乐：`rules/media.md` + `rules/audio-voice.md` -> `examples/cloud_video_music_tts_demo.py`
- 智能配音与字幕 (Script-to-Video)：`rules/text.md` + `rules/audio-voice.md` -> 核心 API `add_narrated_subtitles`
- 旁白与字幕对齐：`rules/text.md` + `rules/audio-voice.md` -> `examples/cloud_video_music_tts_demo.py`
- 录屏与智能变焦：`rules/recording.md` -> `tools/recording/recorder.py`
- 批量导出/无头导出：`rules/core.md` + `rules/cli.md` -> `examples/robust_auto_export.py`
- 影视解说生成：`rules/generative.md` -> `scripts/movie_commentary_builder.py`

## 📖 经典示例 (Examples)

参考这些以了解完整工作流：
- [examples/my_first_vlog.py](examples/my_first_vlog.py) - 带背景音乐和动画文本的完整 Vlog 创建演示。
- [examples/simple_clip_demo.py](examples/simple_clip_demo.py) - 基础剪辑和轨道管理的快速入门教程。
- [examples/compound_clip_demo.py](examples/compound_clip_demo.py) - **新**：专业嵌套项目（复合剪辑）自动化。
- [examples/cloud_video_music_tts_demo.py](examples/cloud_video_music_tts_demo.py) - 云端视频 + 云端 BGM + TTS/字幕对齐。
- [examples/web_to_video_intro_demo.py](examples/web_to_video_intro_demo.py) - 网页到视频介绍演示（HTML 动画 -> 时间轴剪辑）。
- [examples/robust_auto_export.py](examples/robust_auto_export.py) - 稳定导出工作流和错误处理。
- [examples/auto_exposure_align_demo.py](examples/auto_exposure_align_demo.py) - CV 辅助曝光对齐工作流。
- [examples/video_transcribe_and_match.py](examples/video_transcribe_and_match.py) - **高级**：AI 驱动工作流（转录视频 -> 通过 AI 语义匹配 B-Roll -> 组合草稿）。

## 🧠 提示词与集成工具 (Prompts & Integrated Tools)

使用这些模板和脚本处理复杂任务：
- **素材搜索**：通过中英文名称查找滤镜、转场和动画：
  ```bash
  python <SKILL_ROOT>/scripts/asset_search.py "复古" -c filters
  ```
- **影视解说生成器**：从故事板 JSON 生成 60 秒解说视频：
  ```bash
  python <SKILL_ROOT>/scripts/movie_commentary_builder.py --video "video.mp4" --json "storyboard.json"
  ```
- **同步原生素材**：将剪映 App 中的喜爱/播放过的 BGM/风格导入技能：
  ```bash
  python <SKILL_ROOT>/scripts/sync_jy_assets.py
  # 从现有草稿索引云端素材
  python <SKILL_ROOT>/scripts/build_cloud_music_library.py
  python <SKILL_ROOT>/scripts/build_cloud_text_styles_library.py
  ```
- **README 到教程**：将项目的 README.md 转换为完整安装教程视频脚本：
  - 读取提示：`prompts/readme_to_tutorial.md`
  - 将内容注入 `{{README_CONTENT}}` 变量
- **屏幕录制与智能变焦**：录制屏幕并自动应用缩放关键帧：
  ```bash
  python <SKILL_ROOT>/tools/recording/recorder.py
  # Web 预览捕获（高性能）
  python <SKILL_ROOT>/scripts/web_recorder.py --url "http://localhost:3000" --duration 5
  # 或对现有视频应用缩放：
  python <SKILL_ROOT>/scripts/jy_wrapper.py apply-zoom --name "Project" --video "v.mp4" --json "e.json"
  ```
- **草稿检查器**：检查草稿结构和元数据（v5.9+ 支持）：
  ```bash
  python <SKILL_ROOT>/scripts/draft_inspector.py list --limit 20
  python <SKILL_ROOT>/scripts/draft_inspector.py summary --name "DraftName"
  ```
- **自动导出器**：草稿的无头导出到 MP4/SRT：
  ```bash
  python <SKILL_ROOT>/scripts/auto_exporter.py "DraftName" "output.mp4" --res 1080 --fps 60
  # 仅用于 SRT：
  python <SKILL_ROOT>/scripts/jy_wrapper.py export-srt --name "DraftName"
  ```
  注意：MP4 自动导出使用 Windows UI 自动化。在 macOS 上，生成草稿后手动从剪映导出。
- **模板克隆与替换器**：安全克隆模板并批量替换素材（防止损坏原模板）:
  ```bash
  # 克隆模板生成新项目
  python <SKILL_ROOT>/scripts/jy_wrapper.py clone --template "酒店模板" --name "客户A_副本"
  ```
- **API 验证器**：快速诊断您的环境：
  ```bash
  python <SKILL_ROOT>/scripts/api_validator.py
  ```

## 🚀 快速开始示例

```python
import os
import sys

# 1. 环境初始化 (必须同步到脚本开头，支持 Win/Mac)
current_dir = os.path.dirname(os.path.abspath(__file__))
env_root = os.getenv("JY_SKILL_ROOT", "").strip()
# 探测技能路径 (支持 Antigravity, Trae, Claude 等)
skill_root = next((p for p in [
    env_root,
    os.path.join(current_dir, ".agents", "skills", "jianying-editor"),
    os.path.join(current_dir, ".agent", "skills", "jianying-editor"),
    os.path.join(current_dir, ".trae", "skills", "jianying-editor"),
    os.path.join(current_dir, ".claude", "skills", "jianying-editor"),
    os.path.join(current_dir, "skills", "jianying-editor"),
    os.path.abspath(".agents/skills/jianying-editor"),
    os.path.abspath(".agent/skills/jianying-editor"),
    os.path.abspath(".trae/skills/jianying-editor"),
    os.path.abspath(".claude/skills/jianying-editor"),
    os.path.abspath("skills/jianying-editor"),
    os.path.dirname(current_dir)
] if p and os.path.exists(os.path.join(p, "scripts", "jy_wrapper.py"))), None)

if not skill_root: raise ImportError("Could not find jianying-editor skill root.")
sys.path.insert(0, os.path.join(skill_root, "scripts"))
from jy_wrapper import JyProject

if __name__ == "__main__":
    # 2. 初始化工程 (支持 v5.9+ 及自修复)
    project = JyProject("New AI Video", overwrite=True)
    assets_dir = os.path.join(skill_root, "assets")

    # 3. 智能配音与字幕 (One-click Script-to-Video)
    project.add_narrated_subtitles(
        text="欢迎使用剪映自动化 Skill。这是一个全面适配 MacOS 的进阶版本。",
        speaker="zh_female_xiaopengyou"
    )

    # 4. 导入额外素材
    project.add_media_safe(os.path.join(assets_dir, "video.mp4"), "0s")
    project.add_media_safe(os.path.join(assets_dir, "audio.mp3"), "0s", track_name="Audio")

    # 5. 添加带动画的标题
    project.add_text_simple("剪映自动化开启", start_time="1s", duration="3s", anim_in="复古打字机")

    project.save()
```

## 🛠️ 初始化与项目规范 (Initialization & Project Rules)

在初始化 `JyProject` 时，请务必根据主视频素材的比例设置分辨率。**默认值为横屏 (1920x1080)**。

### 🚨 脚本存放位置规范
**禁止在 Skill 安装目录下创建您的业务剪辑脚本**。
- **正确做法**：将您的剪辑 Python 脚本放在项目的根目录。
- **原因**：Skill 目录应该只包含工具集源码，便于后续 `git pull` 升级。业务代码混入会导致版本管理混乱。
