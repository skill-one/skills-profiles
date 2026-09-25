> **必须：首先加载 Remotion 最佳实践**
>
> 此技能依赖于 `remotion-best-practices`。
>
> - **Pi**: 在可用的技能列表中读取 `remotion-best-practices` 加载的技能。
> - **Claude Code**: 在继续之前调用 `remotion-best-practices` 技能/工具。
>
> 未安装？从 [remotion-dev/skills](https://github.com/remotion-dev/skills) 获取（文档：[remotion.dev/docs/ai/skills](https://www.remotion.dev/docs/ai/skills)）。
>
> 如果未安装 `remotion-best-practices`，则最低要求：必须提供 chromium，始终用 `<Scale4K>` 包裹 4K 内容，使用 `<TransitionSeries>` 并带有 `linearTiming`，并将音频视为主时钟。

# 视频播客制作器

从主题自动生成 **4K Bilibili 水平知识视频** 的自动化流程。编码代理 + TTS 后端 + Remotion + FFmpeg。

## 内容

- [引导](#bootstrap) — 前置条件（在步骤 1 之前运行）
- [执行模式](#execution-modes) — 自动 vs 交互式 → [references/workflow-script.md](references/workflow-script.md)
- [重新生成现有视频](#regenerating-an-existing-video) — 对已完成的视频进行迭代
- [工作流](#workflow) — 11 步骤的管道 + 阶段文件指针 + 强制停止点
- [硬规则](#hard-rules) — 不可协商的生产约束
- [音频主时钟与同步](#audio-master-clock--sync)
- [每个视频的布局](#per-video-layout)
- [附加资源](#additional-resources) — 何时加载每个 `references/` 文件
- [用户偏好](#user-preferences)
- [故障排除](#troubleshooting)

---

## 引导

将 `SKILL_DIR` 解析为包含此 `SKILL.md` 的目录：

- **Pi**: 代理从加载的技能列表中知道技能路径 — 在运行命令之前将 `SKILL_DIR` 设置为该目录。
- **Claude Code**: `${CLAUDE_SKILL_DIR}` 会自动填充。

```bash
SKILL_DIR="${SKILL_DIR:-${CLAUDE_SKILL_DIR}}"

# 前置条件 (CLIs + 后端环境变量)
python3 "${SKILL_DIR}/scripts/check_prereqs.py"
```

更新通过插件市场 (`/plugin update`) 流动；直接 git-clone 安装使用 README 中的 `git pull`。此技能不执行更新检查。

**前置条件失败** — 请参阅 README.md 进行设置。检查是后端感知的（解析 `TTS_BACKEND` 环境变量 → `user_prefs.json` `global.tts.backend` → `edge` 默认），因此仅验证活动后端所需的环境变量。

**新项目中第一个视频？** 优先重用现有的 Remotion 项目，其中 `node_modules/` 已安装 — 创建一个新项目会下载 ~2.2 GB 的 npm 包和 90 MB 的 Chrome 无头 Shell（每个项目一次性）。如果用户有来自先前视频的项目，请使用它。如果必须创建一个新项目，请在执行步骤 1-4（主题研究和脚本编写）的同时在后台运行 `npm install`。

**所有渲染都进入 `videos/{name}/`** — 每个 `output.mp4`、`final_video.mp4` 和 `thumbnail_*.png` 都直接进入每个视频目录。永远不要渲染到 `out/` 或 `dist/` 目录；`--public-dir videos/{name}/` 的约定使一切保持自包含。

**TTS 引擎** — 所有 11 个后端 (`TTS_BACKEND=edge|azure|cosyvoice|doubao|tencent|baidu|minimax|xunfei|elevenlabs|openai|google`) 都通过 **ttscn 组件技能** 合成，该技能是**必需的**：在 `~/.claude/skills/ttscn` 下安装它或指向其根目录 ([Agents365-ai/ttsCN](https://github.com/Agents365-ai/ttsCN))。每个后端仍然只需要自己的 API 密钥（Edge 无需）；`check_prereqs.py` 验证安装和密钥。

> **Pi 用户**：`ttscn` 没有与 Pi捆绑 — 将 `Agents365-ai/ttsCN` 作为 Pi 技能安装（其 `skills/ttscn/` 布局会自动检测）或设置 `TTSCN_HOME`；`check_prereqs.py` 在 TTS 之前验证安装。

> **设计学习快捷方式**：如果用户提供参考视频/图像或要求保存/列出/删除样式配置文件，请参阅 [references/design-learning.md](references/design-learning.md)，而不是运行以下工作流。

---

## 执行模式

在工作流启动时检测自动模式（默认）与交互式模式 — 自动默认的决策表和每个请求的覆盖在 [references/workflow-script.md](references/workflow-script.md#execution-modes) 中。

---

## 重新生成现有视频

如果 `videos/{name}/` **已存在** 且用户正在迭代一个已完成或进行中的视频，**重用该目录**。不要开始一个新项目或一个新的 `videos/{newname}/`。

选择实际更改的**最小**重新运行：

| 更改 | 重新运行 | 重用（不要重做） |
| --------- | -------- | --------------------- |
| 叙述脚本 (`podcast.txt`) | 步骤 7 (TTS) → 步骤 8 预览 → 渲染+混合 | 主题研究 + 章节设计 |
| 仅视觉效果（组件、布局、颜色） | 步骤 8 预览 → 渲染+混合 | 音频 (`podcast_audio.wav` / `timing.json`) |
| 仅背景音乐 | 重新混合 BGM | `output.mp4`（不重新渲染） |
| 仅字幕 | 步骤 10.1 最终化 | `output.mp4` / `video_with_bgm.mp4` |

任何更改观众**看到或听到**的内容的重新运行都会重新进入步骤 8 的门：应用更改，让 Studio 热重载，并等待用户明确的“渲染 4K”——之前的确认**不会**转移。包含调整请求的回复**不是**确认 — 应用更改，热重载，再次询问。每次调整都需要在步骤 9 之前进行新的确认。

**脚本**更改会移动所有下游时间戳，因此始终通过 TTS 重新生成 `timing.json` — 永远不要手动编辑它。任何重新运行后，重新验证：

```bash
python3 ${SKILL_DIR}/scripts/verify_output.py videos/{name}/
```

---

## 工作流

> **迭代一个已完成的视频？** 如果 `videos/{name}/` 已存在，请参阅上面 [重新生成现有视频](#regenerating-an-existing-video) 的最小重新运行 — 不要从步骤 1 开始。

在步骤 1 启动时，在代理的跟踪器中为每个步骤创建一个任务。开始时标记 `in_progress`，完成时标记 `completed`。`videos/{name}/` 中的文件是持久的记录 — 如果中断，请检查目录以确定从哪里恢复。

| # | 步骤 | 输出 | 阶段文件 |
| --- | ------ | -------- | ----------- |
| 1 | 定义主题方向 | `topic_definition.md` | [workflow-script.md](references/workflow-script.md) |
| 2 | 研究主题 | `topic_research.md` | [workflow-script.md](references/workflow-script.md) |
| 3 | 设计 5-7 个章节 | (内存中) | [workflow-script.md](references/workflow-script.md) |
| 4 | 编写叙述脚本 | `podcast.txt` | [workflow-script.md](references/workflow-script.md) |
| 4.5 | 拼音预飞行 (zh-CN) | `phonemes.json` | [workflow-script.md](references/workflow-script.md) |
| 5 | 资产计划与解析 | `assets/manifest.json` | [workflow-assets.md](references/workflow-assets.md) |
| 6 | 生成缩略图 (16:9 + 4:3) | `thumbnail_*.png` | [workflow-production.md](references/workflow-production.md) |
| 7 | 生成 TTS 音频 | `podcast_audio.wav`, `timing.json` | [workflow-production.md](references/workflow-production.md) |
| **8** | **Remotion 合成 + Studio 预览** | — | [workflow-production.md](references/workflow-production.md) |
| 9 | 渲染 4K + 混合 BGM | `output.mp4`, `video_with_bgm.mp4` | [workflow-production.md](references/workflow-production.md) |
| **10** | **发布信息 + 验证输出** | `publish_info.md`, `final_video.mp4` | [workflow-publish.md](references/workflow-publish.md) |
| 11 | 生成垂直短片（可选） | `shorts/` | [workflow-publish.md](references/workflow-publish.md) |

**强制停止**（上面粗体行）：

- **步骤 8 — Studio 审查。** 必须启动 `npx remotion studio` 并等待用户反馈，然后才能渲染。永远不要渲染 4K，直到用户明确确认（“渲染 4K” / “渲染最终”）。包含调整请求的回复**不是**确认 — 应用更改，热重载，再次询问。每次调整都需要在步骤 9 之前进行新的确认。
- **步骤 10 — `verify_output.py`。** 必须通过才能宣布视频完成。退出 0 = 绿色；退出 2 = 可发布的警告。自动修复常见的遗漏（如果缺少，则创建 `final_video.mp4`）。验证发布信息（标题、描述、标签、章节）与平台矩阵 — 在步骤 5.5 和 10.2 中生成它。为机器可读输出添加 `--format json`。

**预渲染审核（推荐）** — 在步骤 8 之前：

```bash
python3 ${SKILL_DIR}/scripts/audit_beat_sync.py <Video.tsx> <timing.json>
```

标记与叙述漂移 > 1.5 秒的节拍。

**自动模式：视觉自我审查。** 在自动模式下运行时（没有用户观看 Studio），在请求渲染确认之前渲染 3-5 个关键帧静态图像：

```bash
npx remotion still src/remotion/index.ts <CompositionId> videos/{name}/_review_001.png --public-dir videos/{name}/ --frame=<midpoint_frame>
```

选择帧：英雄标题（约 10% 在内），一个密集章节的中点，和结尾。将静态图像读回为图像，并运行 [design-guide.md](references/design-guide.md) 和 [visual-taste.md](references/visual-taste.md) 检查表与实际渲染输出进行对比。在 4K 渲染之前捕获溢出、对比度和布局回归。审查后删除 `_review_*.png`。

### 验证检查点

| 步骤后 | 检查 |
| ----------- | ------- |
| 7 (TTS) | `podcast_audio.wav` 播放 · `timing.json` 覆盖所有章节 · SRT 是 UTF-8 |
| 9 (渲染) | `output.mp4` 是 3840×2160 · 音频-视频同步 · 没有黑帧 |
| 10 (验证) | `verify_output.py` 退出 0（或 2 带有审查的警告） |

---

## 硬规则

| 规则 | 要求 |
| ------ | ------------- |
| **单个项目** | 用户 Remotion 项目中 `videos/{name}/` 下所有视频。永远不要为每个视频创建一个新项目。 |
| **4K 输出** | 3840×2160（或 2160×3840 垂直），使用 `scale(2)` 包装 1920×1080 设计空间 |
| **音频同步** | 音频 (`podcast_audio.wav` + `podcast_audio.srt`) 是主时钟。`timing.json` 必须从真实的 TTS 输出生成，永远不要手动估计。在渲染之前，最终视频的持续时间必须与音频在 ±0.5 秒内匹配。参见 [Audio-Master Clock & Sync](#audio-master-clock--sync)。 |
| **缩略图** | 必须生成 16:9（1920×1080）和 4:3（1200×900） — 参见 [design-guide.md](references/design-guide.md) |
| **Studio 在渲染之前** | 必须启动 `remotion studio` 进行审查。永远不要渲染 4K，直到用户明确确认。调整反馈≠确认 — 应用更改，热重载，再次询问。每次调整都需要在步骤 9 之前进行新的确认。 |
| **`--public-dir`** | 每个 Remotion 命令使用 `--public-dir videos/{name}/`。所有输出文件（output.mp4、final_video.mp4、缩略图）直接进入 `videos/{name}/` — 永远不要进入 `out/` 或 `dist/` 目录。 |

视觉效果最低要求（文本大小、内容宽度、安全区域、动画安全）位于 [references/design-guide.md](references/design-guide.md)。**必须在步骤 8 之前加载。**

## 音频主时钟与同步

### 金科玉律

1. **音频是主时钟。** 每个幻灯片开始、字幕、章节和动画节拍都来自 `podcast_audio.wav` 和 `podcast_audio.srt`。
2. **从 TTS 生成时间，而不是从文本估计。** 流程：`podcast.txt` → `generate_tts.py` → `podcast_audio.wav` + `podcast_audio.srt` + `timing.json` → 合成 → 渲染。
3. **在音频存在之前，永远不要手动编写 `timing.json`。** 如果您已经有了定制的幻灯片，请运行 `align_timing_from_srt.py` 将它们锚定到真实的 SRT。
4. **补偿 TransitionSeries 重叠。** `TransitionSeries` 渲染 `sum(section.duration_frames) - (N-1) * transitionFrames` 帧。按比例缩放每个章节，以保持渲染长度等于 `timing.total_frames`。**不要**将所有重叠帧塞进第一个章节。修正模式位于 `templates/Video.tsx`。

### 强制同步检查点

| 当... | 检查 |
| ------ | ------- |
| 步骤 7 (TTS) 后 | `timing.json.total_duration` 与 `podcast_audio.wav` 在 ±0.5 秒内匹配 |
| 渲染之前 | `Video.tsx` 按比例缩放所有章节以补偿过渡重叠 |
| 渲染后 | `final_video.mp4` 持续时间与 `podcast_audio.wav` 在 ±0.5 秒内匹配 |
| 步骤 10 (验证) | `verify_output.py` 退出 0 并报告音频/时间绿色 |

如果任何检查点失败，请停止。不要发布。

### 输出规格

| 参数 | 水平 (16:9) | 垂直 (9:16) |
| ----------- | ------------------- | ----------------- |
| 分辨率 | 3840×2160 (4K) | 2160×3840 (4K) |
| 帧率 | 30 fps | 30 fps |
| 编码 | H.264, 16Mbps | H.264, 16Mbps |
| 音频 | AAC, 192kbps | AAC, 192kbps |
| 持续时间 | 1-15 分钟 | 60-90 秒（高亮） |

## 每个视频的布局

```
project-root/                           # Remotion 项目根目录
├── src/remotion/                       # Remotion 源 (Root.tsx, 合成, index.ts)
├── videos/{video-name}/                # 每个视频目录
│   ├── topic_definition.md             # 步骤 1
│   ├── topic_research.md               # 步骤 2
│   ├── podcast.txt                     # 步骤 4: 叙述脚本
│   ├── phonemes.json                   # 步骤 4.5: zh-CN 拼音覆盖
│   ├── assets/manifest.json            # 步骤 5: 每个章节的资产注册表
│   ├── publish_info.md                 # 步骤 10: 标题/描述/标签
│   ├── podcast_audio.wav               # 步骤 7: TTS 音频
│   ├── podcast_audio.srt               # 步骤 7: 字幕
│   ├── timing.json                     # 步骤 7: 时间线（驱动动画）
│   ├── thumbnail_*.png                 # 步骤 6
│   ├── output.mp4                      # 步骤 9: 4K 渲染
│   ├── video_with_bgm.mp4              # 步骤 9: 带有 BGM
│   ├── final_video.mp4                 # 步骤 10: 最终输出
│   └── bgm.mp3                         # 背景音乐
└── remotion.config.ts
```

### 每个视频的 `--public-dir`

每个 Remotion 命令使用 `--public-dir videos/{name}/` — 每个视频的资产都保留在其自己的目录中，以启用并行渲染：

```bash
npx remotion studio src/remotion/index.ts --public-dir videos/{name}/
npx remotion render ... videos/{name}/output.mp4 --public-dir videos/{name}/ --video-bitrate 16M
npx remotion still ... videos/{name}/thumbnail.png --public-dir videos/{name}/
```

### 命名

- **视频名称 `{video-name}`**: 小写英文，连字符分隔（例如 `reference-manager-comparison`）
- **章节名称 `{section}`**: 小写英文，下划线分隔，匹配 `[SECTION:xxx]`
- **缩略图**（16:9 和 4:3 都需要）：`thumbnail_remotion_16x9.png` + `thumbnail_remotion_4x3.png`（或 `_ai_` 前缀用于 AI 生成的）

---

## 附加资源

按需加载 — **不要一次加载所有**：

| 文件 | 加载时 |
| ------ | ----------- |
| [references/workflow-script.md](references/workflow-script.md) | 步骤 1-4（主题 → 脚本）+ 执行模式（自动 vs 交互式） |
| [references/natural-narration.md](references/natural-narration.md) | **加载在步骤 4 脚本编写之前** — 语音叙述的反滑规则（淘汰名单、结构指示、检查表） |
| [references/script-polish.md](references/script-polish.md) | **加载在步骤 4 草稿编写之后** — 深度编辑工具包，带有 24 个 EN+ZH 的前后模式，证据边界，质量标准 |
| [references/workflow-assets.md](references/workflow-assets.md) | 步骤 5，或当用户提供图像/片段或想要库存/AI 媒体时 |
| [references/workflow-assets.md](references/workflow-assets.md#transparent-overlays-via-hyperframes-free-needs-node-22) | 需要数据图表/信息图表动画（透明覆盖 via Hyperframes）的一个部分 |
| [references/workflow-production.md](references/workflow-production.md) | 步骤 5.5-9.5（发布信息草稿 → 缩略图 → TTS → Remotion → 渲染 → 混合 BGM） |
| [references/workflow-publish.md](references/workflow-publish.md) | 步骤 10-11（发布信息，验证，短片） |
| [references/platform-matrix.md](references/platform-matrix.md) | 平台特定行为（缩略图，章节，结尾，发布信息，短片） |
| [references/design-guide.md](references/design-guide.md) | **必须在步骤 8 之前加载** — 视觉最低要求，排版，动画安全 |
| [references/visual-taste.md](references/visual-taste.md) | **加载在步骤 8 之前** 与设计指南一起 — 设计旋钮，反默认规则，视觉模式，章节节奏 |
| [references/design-learning.md](references/design-learning.md) | 用户提供参考视频/图像，或管理样式配置文件 |
| [references/troubleshooting.md](references/troubleshooting.md#azure-tts-deep-dive) | 选择 Azure 语音/样式，调试嘶哑/有故障的音频 |
| [references/troubleshooting.md](references/troubleshooting.md) | 出错时，脚本/CLI 发现，或用户询问关于偏好/BGM |
| [templates/presets/kinetic-typography/](templates/presets/kinetic-typography/) | 粗体类型驱动的预设（意见 / 论证 / 声明视频） |

所有脚本都可通过一个调度器访问 — 开始使用 `python3 ${SKILL_DIR}/scripts/cli.py --help`；完整路线和包封错误代码：[references/troubleshooting.md](references/troubleshooting.md#discovery-when-youre-not-sure-which-script-to-run).

---

## 用户偏好

可变状态 (`user_prefs.json`, `phonemes.json`) 存在于 `~/.video-podcast-maker/` — 安全不受技能更新影响。在首次运行时从技能目录自动迁移。运行“显示偏好”查看，或“设置 X Y”更改。完整命令：[references/troubleshooting.md](references/troubleshooting.md).

---

## 故障排除

参见 [references/troubleshooting.md](references/troubleshooting.md) 中的错误、BGM 选项、偏好学习、设计学习问题。
