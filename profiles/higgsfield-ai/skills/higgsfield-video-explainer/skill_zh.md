# Higgsfield Video Explainer

通过 Higgsfield CLI 运行 MCP 视频说明工作流。锁定一个视觉风格键，为每个 10 秒片段撰写一行旁白和一条匹配的视觉提示，先生成所有声音片段，再生成所有视频片段，然后立即使用 `explainer_video` 组装有序配对。

切勿在本技能中使用整体的 `video_explainer` 任务。

## MCP-to-CLI 映射

| MCP 工作流操作 | CLI 等价命令 |
|---|---|
| `get_explainer_presets` | `higgsfield preset list video-explainer --json` |
| `resolve_explainer_preset` | `higgsfield preset resolve video-explainer <preset_id>` --json |
| `generate_image` / `nano_banana_pro` | `higgsfield generate create nano_banana_2 ...` |
| `list_voices` | `higgsfield voices list --json` |
| `generate_audio` / `seed_audio` | `higgsfield generate create seed_audio ...` |
| `generate_video` / `gemini_omni` | `higgsfield generate create gemini_omni ...` |
| `job_status` | `--wait --json` 或 `higgsfield generate wait <job_id>` --json |
| `explainer_video` | `higgsfield generate create explainer_video ...` |

`nano_banana_2` 是 MCP 工作流所使用的 Nano Banana Pro 风格键模型的公共 CLI 标识。

## 启动（Bootstrap）

1. 如果 `higgsfield` 不可用，则进行安装：

```bash
curl -fsSL https://raw.githubusercontent.com/higgsfield-ai/cli/main/install.sh | sh
```

2. 如果 `higgsfield account status` 失败，请询问用户运行 `higgsfield auth login`，然后等待。
3. 在首次提交前检查实时契约：

```bash
higgsfield model get nano_banana_2
higgsfield model get seed_audio
higgsfield model get gemini_omni
higgsfield model get explainer_video
```

## 阶段 0 — 先询问

分两次独立回合收集选项，顺序如下。切勿合并它们。

### 第 1 回合 — 仅风格

始终加载实时 CMS 目录：

```bash
higgsfield preset list video-explainer --json
```

展示预设名称及其缩略图/视频预览 URL。用一句简短的话询问用户选择预设、描述自定义风格或附上风格参考图片，然后结束该回合。在同一回合不要询问生产相关的问题。选择风格为必须项；除非用户明确表示“由你选择”，否则不得静默选择。

仅当请求已包含 `explainer preset id: <uuid>` 时才跳过本回合。确认该 UUID 在实时目录中存在，并保留至阶段 1。

### 第 2 回合 — 生产设置

在风格选择之后，收集所有未决设置：

- 时长：1 至 10 个完整分钟。`N = duration_minutes × 6`，为固定的 10 秒片段。
- 旁白语言：默认英语，但仍需提供选择。
- 角色：循环吉祥物或无脸风格场景。始终询问。
- 宽高比：默认 `16:9` 或 `9:16` 竖屏。
- 字幕：默认关闭。说明字幕每个有声音的片段收费 0.05 信用点。如果启用，请让用户选择 `patrick`、`caveat`、`marker` 或 `anton`；切勿静默选择。

除非用户明确委托，否则每个选择都属于用户。

## 输入

- 主题或个人/哲学故事。
- 可选本地源文档；在撰写脚本前读取/提取它们。它们是事实性输入，不是生成媒体。
- 可选预设 UUID，与自定义风格参考图片互斥。
- 可选风格参考图片。仅使用其渲染风格和色彩校正；除非用户要求，否则不得复制其中的人物、文本、 Logo 或物体。
- 来自阶段 0 的时长、语言、角色模式、宽高比和字幕选择。

对于本地风格提供方，每个路径都需重复 `--image` 参数。对于网络图片，需先将其下载到本地，或使用已有的上传媒体 ID。

## 硬性规则

- 始终保持所有视觉效果严格非写实。在每个剪辑提示中重复相同的 STYLE 描述和非写实否定项。
- 将所有口述内容排除在视频生成之外。剪辑音频仅限环境音效或音乐；不得包含对白、唇形同步或烘焙旁白。
- 每个带标签的片段严格使用一个旁白片段和一条剪辑。Block N 的音频始终对应 Block N 的视频。
- 每个剪辑都附上相同的风格键图片。
- 所有图像/视频提示均使用英文撰写。仅旁白使用所选语言。
- 在撰写脚本前研究真实主题。不得凭记忆编造引语、日期、数字或事件。
- 在同一运行中自动组装。返回零散剪辑即为失败。

## 流程

| 阶段 | 输出 | CLI |
|---|---|---|
| 0 询问 | 先确定风格；然后确定时长、语言、角色、宽高比、字幕 | `preset list` + 用户问题 |
| R 研究 | 已核实的事实和来源 | 可用研究工具 |
| 1 风格键 | 一张通用风格图片 | `preset resolve` 或 `nano_banana_2` |
| 2 旁白 | N 行带标签的旁白 | 推理 |
| 3 片段提示 | N 个带标签的视频提示 | 推理 |
| 4 声音 | 用户选择一个声音；生成 N 个片段 | `voices list` + `seed_audio` |
| 5 片段 | 生成 N 个 10 秒片段 | `gemini_omni` |
| 6 组装 | 一个最终 MP4 | `explainer_video` |

在阶段 1–3 之前读取 `references/prompts.md`。

## 阶段 R — 研究

对于真实主题，使用可用的网络研究工具及权威来源，核实每个片段所需足够的事实。保留简短的 Sources 列表。切勿仅凭记忆独立撰写事实性说明。

对于个人故事，跳过网络研究，仅使用用户提供的细节。不得编造任何事实性内容。

## 阶段 1 — 创建或确定风格键

撰写一条可重复使用的 STYLE 描述：包含中等、调色板、线条/填充行为、纹理/完成度，然后加上 `non-photorealistic, illustrated, not a photo, no live-action, no realism`。

### 选定 CMS 预设

将隐藏的风格图片解析到活动工作区中：

```bash
higgsfield preset resolve video-explainer "<preset UUID>" --json
```

将返回的 `media_id` 作为 `STYLE_KEY_ID` 保留。跳过图像生成：导入的媒体即为风格键。根据返回的预设名称以及必要的非写实规则构建 STYLE 描述。不得仅凭预设名称重新创建预设。

预设参考控制构图。若与阶段 0 请求的宽高比冲突，请停止并让用户选择，而非静默对抗参考。

### 自定义风格或参考图片

生成恰好一张关键图片。使用 `references/prompts.md` 中的抽象色块模板，或在角色模式启用时使用其吉祥物变体。为每个风格提供方重复 `--image`：

```bash
higgsfield generate create nano_banana_2 \
  --prompt "<style-key prompt>" \
  --aspect_ratio 16:9 \
  --resolution 2k \
  --wait \
  --json
```

竖屏使用 `9:16`。将完成的图像任务 UUID 保留为 `STYLE_KEY_ID`；后续 CLI 生成可使用完成的任务 UUID 作为图片引用。

## 阶段 2 — 撰写旁白

在所选语言中撰写恰好 `N` 个带标签的旁白片段：

```text
Block 1
<Narration line spoken over clip 1>`
```

- 每个片段一行，通常为 20–24 词，时长约 8–9 秒。
- 每个旁白片段时长控制在约 9.5 秒以内。
- 仅使用纯口述文本：不得包含计时码、情感提示、括号注释或舞台指示。
- 数字需以文字形式拼写。
- 采用具体语气，切勿说“在本视频中”。
- 对于主题，从钩子到收尾构建。对于个人故事，保留用户细节和主角。

## 阶段 3 — 撰写匹配的视觉提示

使用 `references/prompts.md` 中的模板，撰写恰好 `N` 个带标签的英文提示：

```text
Block N
STYLE REFERENCE: Match the attached reference image EXACTLY. <same STYLE descriptor>`
```

对于吉祥物模式，Block 1 以手势致意且闭嘴，最后一片段挥手告别，中间片段仅在有必要时使用一致的客串出场。对于无脸模式，仅使用风格化场景。每个片段保持一个清晰的动作。

## 阶段 4 — 先生成所有声音片段

列出实时声音，呈现选项，并等待用户选择一名旁白：

```bash
higgsfield voices list --json
```

保留所选声音的精确 `id` 和 `type`（`preset` 或 `element`）。除非用户明确委托，否则不得编造或自动选择声音。

为每个旁白片段生成一个完成的 `seed_audio` 任务，始终使用相同的声音：

```bash
higgsfield generate create seed_audio \
  --prompt "<Block N narration only>" \
  --voice_type "<preset | element>" \
  --voice_id "<voice UUID>" \
  --wait \
  --json
```

按块顺序记录每个音频任务 UUID。仅重新生成失败或过长的片段。如有需要，缩短该片段或适度调整 `--speech_rate`。在所有 `N` 个音频任务完成前，不得进入阶段 5。

## 阶段 5 — 逐片生成每个视频片段

为每个片段生成一个完成的 10 秒 `gemini_omni` 剪辑。每次调用都附上相同的风格键：

```bash
higgsfield generate create gemini_omni \
  --prompt "<Block N video prompt>" \
  --image "<STYLE_KEY_ID>" \
  --duration 10 \
  --resolution 720p \
  --aspect_ratio 16:9 \
  --wait \
  --json
```

选择竖屏时使用 `9:16`。按块顺序记录每个视频任务 UUID。本阶段内独立任务可并行运行，但音频阶段的屏障是严格的。仅重新提交失败的片段。切勿静默替换 `gemini_omni`；若模型不可用，请检查实时视频目录。

## 阶段 6 — 立即组装

使用至少两个有序块对的 `blocks.json`。CLI 模型契约要求类型化引用，因此使用通用的已完成任务类型：

```json
[
  {
    "video": {"id": "<clip 1 job UUID>", "type": "video_job"},
    "audio": {"id": "<voice 1 job UUID>", "type": "audio_job"}
  },
  {
    "video": {"id": "<clip 2 job UUID>", "type": "video_job"},
    "audio": {"id": "<voice 2 job UUID>", "type": "audio_job"}
  }
]
```

立即提交服务器端组装器：

```bash
higgsfield generate create explainer_video \
  --items @blocks.json \
  --width 1280 \
  --height 720 \
  --wait \
  --json
```

竖屏使用 `--width 720 --height 1280`。启用字幕时，添加所选字体：

```bash
--subtitles '{"font":"patrick"}'
```

组装器将每个片段保持恰好 10 秒：它将缩短的旁白片段居中，安全地升调以处理小幅超出，从不拉伸视频，按顺序拼接片段，并可选地烧录定时字幕。总时长恰好为 `N × 10` 秒。

不得使用本地 ffmpeg、旧版组装脚本，或整体的 `video_explainer` 任务。

## 检查点与恢复

- 阶段 5 之前：需要一张风格键、恰好 `N` 行旁白和提示、一个已选声音，以及 `N` 个完成的音频任务。
- 阶段 6 之前：需要 `N` 个完成的视频任务，以及精确的一对一块配对，无缺失或重复 ID。
- 预设缺失：刷新 `preset list`；不得重用或编造 ID。
- 预设解析失败：核实工作区选择并重试一次。
- 风格漂移或写实性问题：加强共享的 STYLE 和 NEGATIVE 文本，然后仅重新生成该片段。
- 超时：使用 `higgsfield generate wait <job_id>` --json 重新加入；切勿重复正在运行的任务。
- 两次相同失败意味着提示或参数必须变更。

## 交付

返回最终组装的视频 URL、确切时长、宽高比、旁白语言、所选风格、旁白者、字幕状态，以及研究主题的 Sources 列表。除非用户要求，否则保持中间任务 ID 和零散资源 URL 内部处理。
