---
name: higgsfield-video-explainer
description: 从有序的10秒块中构建一个完整的非照片级真人解说或故事视频：每个块包含一名解说员、一个通用风格键、一个Seed音频片段和一个Gemini Omni片段，然后使用explainer_video进行服务器端组装。使用场景包括："制作解说视频"、"用视频解释这个"、"将这个主题或文档转换为解说视频"、"把这个故事做成动画视频"、"制作无脸解说视频"或"展示解说风格"。支持实时CMS预设、自定义风格引用、吉祥物/无脸模式、双重视角和可选的烧录字幕。不适用于：照片级电影、广告/UGC、访谈片段、播客、动态文字转场、无解说的一时性片段或编辑完成的视频。
---

# Higgsfield 视频解释说明

通过 Higgsfield CLI 运行 MCP 视频解释说明工作流程。锁定一个视觉风格键，每 10 秒块写一条旁白和一条匹配的视觉提示，先生成所有语音，再生成所有片段，然后立即使用 `explainer_video` 组合有序对。

在此技能中永远不要使用整体的 `video_explainer` 任务。

## MCP 到 CLI 映射

| MCP 工作流程操作 | CLI 等价物 |
|---|---|
| `get_explainer_presets` | `higgsfield preset list video-explainer --json` |
| `resolve_explainer_preset` | `higgsfield preset resolve video-explainer <preset_id> --json` |
| `generate_image` / `nano_banana_pro` | `higgsfield generate create nano_banana_2 ...` |
| `list_voices` | `higgsfield voices list --json` |
| `generate_audio` / `seed_audio` | `higgsfield generate create seed_audio ...` |
| `generate_video` / `gemini_omni` | `higgsfield generate create gemini_omni ...` |
| `job_status` | `--wait --json` 或 `higgsfield generate wait <job_id> --json` |
| `explainer_video` | `higgsfield generate create explainer_video ...` |

`nano_banana_2` 是 MCP 工作流程使用的 Nano Banana Pro 风格键模型的公共 CLI ID。

## 引导

1. 如果 `higgsfield` 不可用，请安装它：

   ```bash
   curl -fsSL https://raw.githubusercontent.com/higgsfield-ai/cli/main/install.sh | sh
   ```

2. 如果 `higgsfield account status` 失败，请让用户运行 `higgsfield auth login`，然后等待。
3. 在第一次提交前检查实时合约：

   ```bash
   higgsfield model get nano_banana_2
   higgsfield model get seed_audio
   higgsfield model get gemini_omni
   higgsfield model get explainer_video
   ```

## 阶段 0 — 询问第一次

收集选择，分两个独立回合，按此顺序。永远不要合并它们。

### 回合 1 — 仅风格

始终加载实时 CMS 目录：

```bash
higgsfield preset list video-explainer --json
```

显示预设名称及其缩略图/视频预览 URL。说一句简短的话，让用户选择预设、描述自定义风格或附加风格参考图像，然后结束回合。不要在同一回合中询问生产问题。选择风格是强制性的；除非用户明确说“你选择”，否则永远不要无声选择。

仅当请求中已包含 `explainer preset id: <uuid>` 时才跳过此回合。确认 UUID 存在于实时目录中并保留它以供阶段 1 使用。

### 回合 2 — 生产设置

仅在选择风格后，收集所有未解决设置：

- 时长：一到十分钟。`N = duration_minutes × 6` 固定的 10 秒块。
- 旁白语言：默认为英语，但仍然提供选择。
- 角色：重复的吉祥物或无脸的风格化场景。始终询问。
- 画幅：默认为 `16:9` 或垂直 `9:16`。
- 字幕：默认关闭。解释字幕每段旁白成本为 0.05 信用。如果启用，让用户选择 `patrick`、`caveat`、`marker` 或 `anton`；永远不要无声选择。

除非用户明确授权，否则每个选择都属于用户。

## 输入

- 主题或个人/哲学故事。
- 可选的本地源文档；在脚本前读取/提取它们。它们是事实输入，不是生成媒体。
- 可选的预设 UUID，与自定义风格参考图像互斥。
- 可选的风格参考图像。仅使用它们的渲染风格和色彩分级；除非要求，否则不要复制它们的人物、文本、标志或对象。
- 阶段 0 中的时长、语言、角色模式、画幅和字幕选择。

对于本地风格提供者，用重复的 `--image` 传递每个路径。对于网络图像，先下载到本地或使用现有的上传媒体 ID。

## 严格规则

- 保持每个视觉严格非照片写实。在每个片段提示中重复相同的 STYLE 描述和非写实负面。
- 保持所有语音内容排除视频生成。片段音频仅是环境音或音乐；没有对话、口型同步或烘焙的旁白。
- 使用恰好一个旁白和一段片段每标记块。块 N 音频始终映射到块 N 视频。
- 将相同的风格键图像附加到每个片段。
- 将所有图像/视频提示用英语写。仅旁白使用选定语言。
- 脚本前研究真实主题。不要编造引言、日期、数字或事件。
- 自动组合。返回松散片段是失败。

## 管道

| 阶段 | 输出 | CLI |
|---|---|---|
| 0 询问 | 首先风格；然后时长、语言、角色、画幅、字幕 | `preset list` + 用户问题 |
| R 研究 | 已验证的事实和来源 | 可用研究工具 |
| 1 风格键 | 一个通用风格图像 | `preset resolve` 或 `nano_banana_2` |
| 2 旁白 | N 标记的旁白行 | 推理 |
| 3 块提示 | N 标记的视频提示 | 推理 |
| 4 语音 | 用户选择一个语音；生成 N 次尝试 | `voices list` + `seed_audio` |
| 5 片段 | 生成 N 个 10 秒片段 | `gemini_omni` |
| 6 组合 | 一个最终 MP4 | `explainer_video` |

在阶段 1–3 之前阅读 `references/prompts.md`。

## 阶段 R — 研究

对于真实主题，使用可用的网络研究工具和权威来源验证每个块足够的事实。保留一个简短的来源列表。永远不要仅凭记忆编写事实性解释。

对于个人故事，跳过网络研究，仅使用用户提供的信息。不要编造事实。

## 阶段 1 — 创建或解析风格键

写一个可重用的 STYLE 描述：中等、调色板、线/填充行为、纹理/完成，然后 `非照片写实、插图、不是照片、无真人动作、无写实`。

### 选定的 CMS 预设

将隐藏的风格图像解析到活动工作区：

```bash
higgsfield preset resolve video-explainer "<preset UUID>" --json
```

将返回的 `media_id` 作为 `STYLE_KEY_ID`。跳过图像生成：导入的媒体是风格键。根据返回的预设名称加上强制性的非写实规则构建 STYLE 描述。不要从其名称重新创建预设。

预设参考控制构图。如果它与阶段 0 中请求的画幅冲突，请停止并让用户选择，而不是无声地对抗参考。

### 自定义风格或参考图像

生成恰好一个键图像。使用 `references/prompts.md` 中的抽象色板模板，或在启用角色模式时使用其吉祥物变体。对每个风格提供者重复 `--image`：

```bash
higgsfield generate create nano_banana_2 \
  --prompt "<style-key prompt>" \
  --aspect_ratio 16:9 \
  --resolution 2k \
  --wait \
  --json
```

选择垂直时使用 `9:16`。将完成的图像作业 UUID 作为 `STYLE_KEY_ID`；后续 CLI 生成可以重用完成的作业 UUID 作为图像参考。

## 阶段 2 — 写旁白

用选定语言写恰好 `N` 个标记的旁白块：

```text
块 1
<块 1 旁白>
块 2
<块 2 旁白>
```

- 每块一行，通常 20–24 个词，约 8–9 秒。
- 保持每个尝试在约 9.5 秒以内。
- 仅使用纯语音文本：没有时间码、情绪提示、括号注释或舞台指示。
- 数字用文字拼写。
- 使用具体语气，永远不要说“在这个视频中”。
- 对于主题，从钩子到收尾构建。对于个人故事，保留用户的细节和主人公。

## 阶段 3 — 写匹配的视频提示

用 `references/prompts.md` 中的模板写恰好 `N` 个标记的英语提示：

```text
块 N
STYLE REFERENCE: 精确匹配附加的参考图像。 <相同的 STYLE 描述>
SCENE: <匹配块 N 旁白的场景和动作>
MOTION: <摄像机移动和动画行为>
AUDIO: <环境音效或音乐仅；没有语音、对话或旁白>
NEGATIVE: <风格漂移和写实禁止；没有口型同步、字幕、文本、标志或水印>
```

对于吉祥物模式，块 1 用闭着嘴的姿势打招呼，最后一块挥手告别，中间块仅在必要时使用一致的出镜。对于无脸模式，仅使用风格化场景。每块保持一个清晰的动作。

## 阶段 4 — 先生成所有语音尝试

列出实时语音，展示选择，等待用户选择一个叙述者：

```bash
higgsfield voices list --json
```

保留选定语音的精确 `id` 和 `type` (`preset` 或 `element`)。除非用户明确授权，否则永远不要编造或自动选择语音。

为每个旁白块生成一个完成的 `seed_audio` 作业，始终使用相同的语音：

```bash
higgsfield generate create seed_audio \
  --prompt "<块 N 旁白仅>" \
  --voice_type "<preset|element>" \
  --voice_id "<语音 UUID>" \
  --wait \
  --json
```

按块顺序记录每个音频作业 UUID。仅重新生成失败的或过长的尝试。当需要时，缩短该块或适度调整 `--speech_rate`。在所有 `N` 音频作业完成前，不要开始阶段 5。

## 阶段 5 — 每秒生成所有片段

为每个块生成一个完成的 10 秒 `gemini_omni` 片段。将相同的风格键附加到每个调用：

```bash
higgsfield generate create gemini_omni \
  --prompt "<块 N 视频提示>" \
  --image "<STYLE_KEY_ID>" \
  --duration 10 \
  --resolution 720p \
  --aspect_ratio 16:9 \
  --wait \
  --json
```

选择垂直时使用 `9:16`。按块顺序记录每个视频作业 UUID。在此阶段内，独立作业可以并发运行，但音频阶段屏障是严格的。仅重新提交失败的块。永远不要无声替换 `gemini_omni`；如果模型不可用，请检查实时视频目录。

## 阶段 6 — 立即组合

创建 `blocks.json`，至少包含两个有序块对。CLI 模型合同要求类型化参考，因此使用通用的完成作业类型：

```json
[
  {
    "video": {"id": "<片段 1 作业 UUID>", "type": "video_job"},
    "audio": {"id": "<语音 1 作业 UUID>", "type": "audio_job"}
  },
  {
    "video": {"id": "<片段 2 作业 UUID>", "type": "video_job"},
    "audio": {"id": "<语音 2 作业 UUID>", "type": "audio_job"}
  }
]
```

立即提交服务器端组合器：

```bash
higgsfield generate create explainer_video \
  --items @blocks.json \
  --width 1280 \
  --height 720 \
  --wait \
  --json
```

使用 `--width 720 --height 1280` 选择垂直。当字幕启用时，添加选定的字体：

```bash
--subtitles '{"font":"patrick"}'
```

组合器将每个块保持在恰好 10 秒：它居中短语音尝试，安全地加速小的超时，永远不会拉伸视频，按顺序连接块，并可选地烧入定时字幕。总时长恰好为 `N × 10` 秒。

不要使用本地 ffmpeg、遗留组合脚本或整体的 `video_explainer` 作业。

## 检查点和恢复

- 在阶段 5 之前：要求一个风格键、恰好 `N` 个旁白行和提示、一个选定的语音、`N` 个完成的音频作业。
- 在阶段 6 之前：要求 `N` 个完成的视频作业和精确的一对一块配对，没有缺失或重复的 ID。
- 预设缺失：刷新 `preset list`；永远不要重用或编造一个 ID。
- 预设解析失败：验证工作区选择并重试一次。
- 风格漂移或写实：加强共享的 STYLE 和 NEGATIVE 文本，然后仅重新生成该片段。
- 超时：使用 `higgsfield generate wait <job_id> --json` 重新加入；永远不要重复正在运行的作业。
- 两次相同的失败意味着提示或参数必须改变。

## 交付

返回最终组合视频 URL、精确时长、画幅、旁白语言、选定风格、叙述者、字幕状态和研究主题的来源列表。除非要求，否则保留中间作业 ID 和松散资产 URL 为内部。
