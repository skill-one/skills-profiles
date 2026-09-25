# Higgsfield 生成

向任何 Higgsfield 模型提交任务。封装了 `higgsfield` 命令行界面。涵盖通用图像/视频/3D/音频生成、营销工作室（品牌广告、头像、产品、钩子、设置）以及次要的病毒性预测器视频评分。

## 第 0 步 — 引导

在执行任何其他命令之前：

1. 如果 `higgsfield` 不在 `$PATH` 中，请安装它：
   ```bash
   curl -fsSL https://raw.githubusercontent.com/higgsfield-ai/cli/main/install.sh | sh
   ```
2. 如果 `higgsfield account status` 出现 `Session expired` / `Not authenticated` 错误，请提示用户运行 `higgsfield auth login`（交互式）并等待确认。

## 用户体验规则

1. 保持简洁。聊天中不要显示原始 ID，不要输出 JSON。为生成的资源打印媒体 URL，或为病毒性预测器打印文本摘要。
2. 不要使用内部术语。不要描述“调用 higgsfield 成本”、“轮询任务”。
3. 从第一条消息中检测用户语言并使用该语言回复。技术参数（`--aspect_ratio 16:9`）保持英文。
4. 不要批量询问。选择一个合理的默认模型，并且仅在确实缺失的情况下才一次询问一件事。
5. 除非用户询问，否则不要预先估计成本或优化以使用更便宜的模型。优先选择质量默认值。
6. 在 `generate create` 中传递 `--wait`，以便命令在完成前阻塞并自行打印结果 URL。避免 `create` → `wait` 的两步模式。

## 发现护栏

在查找 Higgsfield 功能/模型时，不要仅依赖语义搜索或 CLI `--help`。首先运行未过滤的模型列表，然后检查可能的 `job_set_type` 名称。如果用户说某个模型存在但搜索无结果，请相信该信号，并在回答前使用完整模型列表进行验证。

工作流与模型是分开的。使用 `higgsfield workflow list` 发现它们，并使用 `higgsfield workflow get <workflow_name>` 检查参数。

病毒性预测器作为以下内容公开：

- 客户端名称：病毒性预测器
- 技术 `job_set_type`：`brain_activity`
- 类别/输出：文本报告。这是一个视频输入/文本输出分析模型，而不是文本/聊天生成模型。
- 输入：上传的视频
- 目的：成品视频钩子、注意力、留存和病毒性分析

如果用户说“分析此视频”、“评分此广告”、“评估此钩子”或类似内容，即使它出现在文本/分析模型下，也路由到 `brain_activity`。根据任务意图和所需输入进行分类，而不是仅根据输出类别。

## 工作流 — 通用生成

1. **选择模型。** 除非简报明确需要专家，否则从核心默认值开始：

   - **GPT Image 2.5** → 高保真度通用生成、图形设计、UI、横幅、排版和图像内文本的默认图像模型。
   - **Seedance 2.5** (`seedance_2_5`) → SOTA 默认视频模型，适用于严肃运动、电影片段、多镜头工作和图像到视频。支持 4–30 秒输出，最高 1080p；当需要原生 4K 时使用 Seedance 2.0。
   - **Nano Banana 2/Lite/Pro** → 默认用于角色、卡通、风格化和参考驱动图像工作；使用 Lite 以提高速度/成本，使用 Pro 处理更复杂的简报。
   - **Marketing Studio** → 默认用于广告、UGC、产品演示、开箱、电视广告、主持人视频和品牌/产品工作流。
   - **Seed Audio 1.0** → 默认音频模型，用于文本到音频、语音、音效、氛围、拟音和类似音乐的音频，除非用户指定 Sonilo/Mirelo。

   **图像：**
   - 完整的品牌标识、标志系统、调色板、排版、品牌手册、包装系统、标识或协调的品牌资产套件 → 使用 `higgsfield-brandkit`。
   - YouTube 缩略图、Shorts 封面或 Instagram 视频封面 → 使用 `higgsfield-youtube-thumbnail`。
   - 品牌产品视觉（Pinterest 钉、生活方式、英雄横幅、广告包、虚拟试穿）→ 使用 `higgsfield-product-photoshoot`。不是此技能。
   - 生成的产品概念/包装/罐子/瓶子带有品牌名称或标签文本 → GPT Image 2.5。
   - 品牌广告图像带有头像 + 产品（Marketing Studio 形状）→ Marketing Studio Image（见下文 Marketing Studio）
   - 美学 UGC / 时尚编辑 / 生活方式角色 → Soul 2.0
   - 电影级静态帧 → Soul Cinema
   - 具有强烈角色特征的创意形象（纯文本、独特）→ Soul Cast
   - 地点/环境/无人物场景 → Soul Location（同类最佳）
   - 标志、图标、矢量样式插图、品牌标记、受控调色板图形 → Recraft V4.1 (`recraft_v4_1`，通常与 `--model_type vector` 一起使用）
   - 脸部编辑 + 复杂场景交换 → Seedream 4.5
   - Soul Character（来自 `higgsfield-soul-id` 的参考 ID）→ Soul 2.0 用于静态图像，Soul Cinema 用于电影
   - 角色或卡通风格工作 → Nano Banana 2；使用 Nano Banana 2 Lite (`nano_banana_2_lite`) 进行快速/简单参考编辑，在复杂情况下升级到 Nano Banana Pro
   - 快速且便宜的迭代 → Z Image
   - **其他所有内容的默认值 → GPT Image 2.5。** 图形设计、UI、横幅、排版和高保真度通用生成。

   **视频：**
   - 从主题、故事或文档创建的完整旁白式解释视频 → 使用 `higgsfield-video-explainer`，而不是通用视频生成。
   - 所有广告/商业/品牌广告视频 → Marketing Studio（见下文 Marketing Studio）
   - 从草图/时间戳编辑现有视频，或重新调整到另一个宽高比 → 工作流 (`draw_to_video` 或 `reframe`)，而不是模型。参见 `references/workflows.md`。
   - **默认所有用途的严肃视频（多镜头、一致身份、运动密集型、图像到视频、4–30 秒请求）→ Seedance 2.5。** SOTA。不要因为其持续时间枚举更容易阅读就降级到 Seedance 1.5；首先验证 Seedance 2.5。
   - 单平面场景，无强动态，低成本选项 → Kling 3.0；如果用户明确要求 Turbo、更快或更低成本的 Kling 输出 → Kling 3.0 Turbo (`kling3_0_turbo`)
   - 干净的简单拍摄，仅在用户要求更便宜/预算输出时使用 → Seedance 1.5 Pro
   - 电影级最高保真度 → Cinema Studio Video 3.0
   - 带强物理效果，无需音频 → Minimax Hailuo
   - 快速批量/大量 → Veo 3.1 Lite
   - 从所需起始图像生成的粗犷/风格化图像到视频 → Grok Video 1.5 (`grok_video_v15`)。需要一个 `--start-image` 或 `--image`，持续时间 2–15 秒，分辨率 `480p` 或 `720p`。
   - 多模态参考到视频，最多 7 张图像或一个视频参考 → Gemini Omni Flash (`gemini_omni`)；保持 Seedance 2.5 作为默认严肃视频选择。
   - 参考驱动生成、编辑现有视频或扩展 → **Seedance 2.5** (`seedance_2_5`)，其模式为 `t2v` / `omni_reference` / `video_edit` / `video_extension`，并接受图像/视频/音频参考数组。使用 `omni_reference` 用于参考输入，包括起始/结束帧；`t2v` 不接受媒体。支持最高 **1080p**；当需要原生 4K 时使用 Seedance 2.0。

   **视频分析：**
   - 评估成品视频的钩子、病毒性潜力、注意力、留存或分心风险 → Virality Predictor (`brain_activity`)。这是一个返回文本分数/报告的视频分析模型，而不是生成的媒体资源。

   **3D：**
   - 可玩游戏中或游戏全局资产系统中的 3D 资产 → 使用 `higgsfield-game-generation`。
   - 从一个或多个对象/产品参考图像创建实际的 3D 网格/模型/GLB → Multi-Image to 3D (`multi_image_to_3d`)。使用重复的 `--image` 传递 1–4 张图像；当资产需要纹理时使用 `--should_texture true`。如果用户仅要求 3D 渲染的图片，请使用图像模型。

   **音频：**
   - **音频生成的默认值 → Seed Audio 1.0 (`seed_audio`)。** 用于文本到音频、音效、氛围、拟音、冲击、环境音频、语音风格生成和类似音乐的音频。它需要 `--prompt`；仅在用户提供参考时使用可选的 `--audio-references`/`--image-references`。
   - 仅在用户明确要求 Sonilo 或您需要该专业音乐模型时使用 Sonilo Music (`sonilo_music`)。它需要 `--prompt` 和 `--duration`，并返回音频。
   - 仅在用户明确要求 Mirelo 或您需要该遗留 SFX 模型时使用 Mirelo Text to Audio (`mirelo_text_to_audio`)。它需要 `--prompt` 和 `--duration`，并返回音频。

   要获取传递给 `higgsfield generate create` 的实际 `--model` ID，请运行 `higgsfield model list --json | jq` 以将显示名称映射到 ID。参见 `references/model-catalog.md` 以获取完整表格。

2. **直接将媒体输入传递给标志。** 媒体标志接受本地文件路径 **或** UUID。CLI 自动上传路径并自动检测 UUID 的任务与上传。无需预上传。每个模型声明接受的媒体角色或 `*_references` 参数 — 参见 `references/media-inputs.md`。
3. **快速验证。** 如果不确定参数，请运行一次 `higgsfield model get <jst> --json` 并仅传递所需内容。在降级到旧模型之前验证首选模型。否则使用模式默认值。服务器返回 `adjustments` 以处理非致命强制转换（例如 `aspect_ratio=99:99` → 最接近的匹配）和结构化错误以处理无效声明的参数值。
4. **一次性提交并等待。** `higgsfield generate create <jst> [--prompt "..."] [媒体标志] [参数标志] --wait`。阻塞直到终端状态并打印结果到标准输出。可调参数：`--wait-timeout 20m`（默认 10m），`--wait-interval 5s`（默认 3s）。病毒性预测器不需要提示；传递 `--video`。
5. **交付。** 对于生成的媒体和 3D 资产，发送主要结果 URL 加上一行摘要（模型，视频的持续时间；3D 的 GLB/资产 URL）。对于病毒性预测器，交付分数、业务解释和 Open 报告链接。不要在正常聊天输出中显示病毒性预测器 `.glb`、`.bin` 或区域表内部细节。

要检查或稍后重跑，`higgsfield generate list --json` 和 `higgsfield generate get <id> --json` 用于回顾。如果需要重新加入未使用 `--wait` 启动的任务，`higgsfield generate wait <id>` 仍然可用。

对于工作流任务，使用 `higgsfield generate workflow <workflow_name> ... --wait`。成本语法是 `higgsfield generate cost workflow <workflow_name> ...`。参见 `references/workflows.md`。

## 媒体标志

| 标志 | 目的 | 接受该标志的模型 |
|---|---|---|
| `--image <path-or-id>` | 参考图像 | 大多数图像模型、`grok_video_v15`、`seedance_2_0`、`seedance_2_5`、`veo3`、`marketing_studio_video` |
| `--start-image <path-or-id>` | 图像到视频转换的第一帧 | `grok_video_v15`、`kling3_0`、`kling3_0_turbo`、`kling2_6`、`veo3_1`、`seedance_2_0`、`seedance_2_5`、`marketing_studio_video` |
| `--end-image <path-or-id>` | 转换的最后一帧 | `kling3_0`、`seedance_2_0`、`seedance_2_5`、`marketing_studio_video` |
| `--video <path-or-id>` | 参考或分析视频 | `seedance_2_0`、`seedance_2_5`、`brain_activity` |
| `--audio <path-or-id>` | 参考音频（口型同步、配乐匹配） | `seedance_2_0`、`seedance_2_5`（参考输入；与生成输出音频不同） |

对于参考数组模型，显式标志是 `--image-references`、`--video-references` 和 `--audio-references`；`--image`、`--video` 和 `--audio` 是当模式暴露这些参数时的简写。

每个标志接受本地文件路径（自动上传）或 UUID（来自 `higgsfield upload create ... --video` 的上传 ID 或先前视频任务 ID）。每个模型声明自己的媒体角色或 `*_references` 参数。参见 `references/media-inputs.md` 以获取完整表格。

## 常见参数

标志传递到模型模式。使用 `higgsfield model get <jst>` 发现。

```bash
higgsfield generate create gpt_image_2_5 --prompt "neon city at dusk" --aspect_ratio 16:9 --resolution 2k --wait
higgsfield generate create nano_banana_2 --prompt "anime character concept, expressive pose" --image ./ref.png --wait
higgsfield generate create seedance_2_5 --prompt "camera dollies in" --mode omni_reference --start-image ./first.png --duration 12 --resolution 1080p --wait
higgsfield generate create grok_video_v15 --prompt "cinematic handheld shot, neon rainy street" --start-image ./image.png --duration 5 --resolution 720p --wait
higgsfield generate create text2image_soul_v2 --prompt "..." --soul-id <soul_ref_id> --quality 2k --wait
higgsfield generate create multi_image_to_3d --image ./front.png --image ./side.png --should_texture true --wait
higgsfield generate create seed_audio --prompt "cinematic rain ambience with distant thunder" --wait
higgsfield generate create sonilo_music --prompt "cinematic synthwave track" --duration 12 --wait
higgsfield generate create mirelo_text_to_audio --prompt "glass breaking in a large hall" --duration 4 --wait
higgsfield generate create brain_activity --video ./ad.mp4 --wait
```

对于机器可读输出（链接管道、代理上下文），添加 `--json`。使用 `--wait --json` 您将获得最终的作业对象数组。不使用 `--wait`，您将获得作业 ID。病毒性预测器将原始分析和渲染工件存储在作业参数中，但默认文本输出应保持为分数和 Open 报告。

标准输入提示：`echo "..." | higgsfield generate create z_image --wait`。

Soul 图像质量：对于 `text2image_soul_v2` 和 `soul_cinematic`，传递 `--quality 1.5k` 或 `--quality 2k`。这些是面向 UI 的层级；后端将它们映射到 `720p`/`1080p` 和选定的 `--aspect_ratio` 的模型特定维度。`soul_location` 没有质量选择器；它根据宽高比使用固定尺寸。

## 营销工作室

品牌图像/视频生成：头像 + 产品 + 可选设置钩子/设置 + 广告风格模式。使用模型 `marketing_studio_video` 和 `marketing_studio_image`。

### 概念

- **头像** — 主持人面部。精选 `preset`（浏览 `higgsfield marketing-studio avatars list`）或 `custom`（通过 `higgsfield marketing-studio avatars create` 上传照片）。对于 UGC 模式，如果简报明确提到人物，头像是可选的；后端可以自动创建 Soul Character。当用户想要特定主持人时传递头像。
- **产品** — 品牌项目，带有标题 + 参考图像。从 URL 导入 (`higgsfield marketing-studio products fetch --url ...`) 或从上传的图像创建 (`higgsfield marketing-studio products create`)。
- **Webproduct** — App Store / 网页版本。在获取 App Store URL 时自动路由。
- **钩子** — 可重复使用的开场角度 / 广告钩子。使用 `higgsfield marketing-studio hooks list` 浏览。钩子文本附加到用户的提示；它不会替换 `--prompt`。
- **设置** — 可重复使用的环境 / 场景上下文。使用 `higgsfield marketing-studio settings list` 浏览。
- **广告参考** — 可重复使用的灵感视频，可以绑定到头像和/或产品。从上传的视频创建 (`--video-input <upload_id>`) 或从先前的生成任务创建 (`--job <job_id>`)。使用 `higgsfield marketing-studio ad-references list` 浏览。参见 `references/marketing-ad-references.md`。
- **品牌套件** — 捕获品牌的标识（名称、标志、英雄图像、颜色、字体、语气）以在图像生成中重复使用。通过提交网站 URL 创建 (`higgsfield marketing-studio brand-kits fetch --url https://… --wait`)。参见 `references/marketing-brand-kits.md`。
- **广告格式** — 驱动生成图像视觉结构的预设 (`headline`、`bullet-points` 等）。只读，使用 `higgsfield marketing-studio ad-formats list` 浏览。是 `dtc-ads generate` 的必需输入。

### 发现命令

当用户询问已存在的内容时，使用这些确切的列表命令：

```bash
higgsfield marketing-studio avatars list --json
higgsfield marketing-studio products list --json
higgsfield marketing-studio hooks list --json
higgsfield marketing-studio settings list --json
higgsfield marketing-studio ad-references list --json
higgsfield marketing-studio brand-kits list --json
higgsfield marketing-studio ad-formats list --json
```

`--hook_id` 和 `--setting_id` 仅由 `marketing_studio_video` 支持；不要将它们传递给 `marketing_studio_image`。

### 用户体验规则（附加）

- 每个阶段一个问题。不要一开始就询问产品+头像+模式。
- **两种广告方法是互斥的。** 要么用户提供广告参考视频（参考驱动）**要么**选择钩子/设置块（块组合） — 永远不要两者同时使用。如果用户选择了广告参考，不要提供钩子/设置；如果选择了钩子/设置，不要提供附加广告参考。
- **广告参考来源。** 唯一有效的输入是一个本地视频文件（通过 `higgsfield upload create ... --video` 上传）或先前的视频任务。如果用户提供任何其他内容，请要求本地文件。
- **`dtc-ads` 广告格式是强制的。** 始终要求用户从 `ad-formats list` 选择。没有自动默认值 — CLI 和服务器都拒绝没有 `--format-id` 的调用。
- **`dtc-ads` 可选输入。** 当简报要求时，建议头像、产品和参考媒体；仅附加用户选择的内容。

### 工作流 — 快速广告视频

1. **获取产品。**
   - 现有产品 → `higgsfield marketing-studio products list --json`
   - URL → `higgsfield marketing-studio products fetch --url <url> --wait`（轮询直到导入完成）
   - 本地图像 → `higgsfield upload create <photo>...` 然后 `higgsfield marketing-studio products create --title "..." --image <id>...`
   捕获产品 ID。在使用 `--hook_id` 时，强烈建议传递 `--product_ids`；钩子设计为在产品上下文中旋转，在没有产品上下文的情况下工作不佳。
2. **如果需要，选择头像。**
   - 默认：`higgsfield marketing-studio avatars list` 并选择与品牌声音匹配的预设。
   - 自定义：`higgsfield marketing-studio avatars create --name "..." --image <upload_id>`。
   对于 UGC 模式，当不需要特定主持人且简报提到人物时，您可以省略 `--avatars`；后端可以合成 Soul Character。
3. **可选地选择设置项。**
   - 钩子：`higgsfield marketing-studio hooks list --json`
   - 设置：`higgsfield marketing-studio settings list --json`
   将选定的 ID 作为 `--hook_id <hook_id>` 和 `--setting_id <setting_id>` 传递给 `marketing_studio_video`（仅限此模型）。不要将钩子的提示复制到 `--prompt`，除非用户明确希望强化相同的措辞。
4. **如果需要，选择模式。** 默认是 `ugc`；仅因为 `--hook_id` 存在而无需 `--mode`。其他当前 slugs：`ugc_how_to`、`ugc_unboxing`、`product_showcase`、`product_review`、`tv_spot`、`wild_card`、`ugc_virtual_try_on`、`virtual_try_on`。**钩子/设置仅对 `ugc`、`ugc_how_to`、`ugc_unboxing`、`product_review`、`ugc_virtual_try_on` 有效** — 不要在与其他模式一起使用时传递 `--hook_id` / `--setting_id`。参见 `references/marketing-modes.md`。
5. **生成（一次性）。**
   ```bash
   PRODUCT_IDS_JSON=$(mktemp)
   AVATARS_JSON=$(mktemp)
   printf '["<product_id>"]' > "$PRODUCT_IDS_JSON"
   printf '[{"id":"<avatar_id>","type":"preset"}]' > "$AVATARS_JSON"

   higgsfield generate create marketing_studio_video \
     --prompt "..." \
     --avatars @"$AVATARS_JSON" \
     --product_ids @"$PRODUCT_IDS_JSON" \
     --mode ugc \
     --duration 15 \
     --resolution 720p \
     --aspect_ratio 9:16 \
     --wait
   ```
   当选择了设置钩子/设置时，添加 `--hook_id <hook_id>` 和/或 `--setting_id <setting_id>`。
   `product_ids` 和 `avatars` 是 JSON 数组；通过 `@/path/to/file.json` 传递它们。不要将裸 UUID 传递给 `--product_ids`。
   分辨率是 `480p` 或 `720p`。宽高比是 `auto`/`21:9`/`16:9`/`4:3`/`1:1`/`3:4`/`9:16`。`--generate-audio true` 在这里受支持（与 `seedance_2_0` 不同）。`--wait` 阻塞直到完成；对于较长的广告运行，增加 `--wait-timeout 30m`。
6. **交付。** URL + 一行摘要（模式，持续时间）。

### 点击广告快捷方式（URL 驱动）

当用户提供产品 URL 并希望一次性获得营销视频时：

```bash
# 1. 触发获取（返回产品 ID，导入在后台运行）
higgsfield marketing-studio products fetch --url https://shop.example.com/sneakers --wait

# 2. 对同一 URL 生成营销视频 — 后端重用实体
higgsfield generate create marketing_studio_video \
  --url https://shop.example.com/sneakers \
  --mode ugc \
  --duration 15 \
  --aspect_ratio 9:16 \
  --wait
```

后端通过 URL 去重，因此重复运行会重用现有实体，而不是重新获取。

### 工作流 — 营销图像

与上述内容相同，但使用 `marketing_studio_image` 模型：

```bash
higgsfield generate create marketing_studio_image \
  --prompt "..." \
  --aspect_ratio 1:1 \
  --resolution 2k \
  --wait
```

## 病毒性预测器视频评分

当用户希望评估成品视频作为商业创意时使用 Virality Predictor (`brain_activity`)：钩子强度、病毒性潜力、注意力、留存或内容/产品如何保持焦点并最小化分心。将“病毒性预测器”视为面向客户的特性名称；`brain_activity` 仅是 CLI/`job_set_type`。

```bash
higgsfield generate create brain_activity --video ./creative.mp4 --wait
```

结果是文本，而不是生成的图像/视频。报告总体分数、峰值钩子秒数、持续分数、最强/最弱区域，如果有的话，报告 URL。将其解释为创意测试的客观注意力代理：更高的视觉/听觉/语言/注意力分数表明更强的刺激和焦点；较低的 Default Mode 更好，因为它表明较少的分心。

CLI 打印一个 Open 报告 URL，例如 `https://<app-domain>/apps/virality-predictor?resultJobId=<job_id>`。发送该 URL 以获取视觉报告。例如 `brain_example_url`、`vertexMapBinaryUrl` 和 `vertexMapUrl` 是实现细节；仅在用户要求原始数据或实现细节时才提及它们。

良好的最终形状：

```text
Overall score: 44/100
Peak hook: 49% at 1s
Sustain: 89%
Strongest region: Visual Cortex
Risk: Default Mode is high, which can indicate mind-wandering.

Open report: <report_url>
```

## 错误

- `Missing required params: prompt` → 用户未提供提示；要求提供提示。
- `Missing required params: medias` on `brain_activity` / Virality Predictor → 通过 `--video <path-or-id>` 传递恰好一个视频。
- `Invalid values: aspect_ratio=99:99 (allowed: ...)` → 枚举无效；从允许的值中选择。
- `Unknown params: foo` → 模式不接受该标志；检查 `higgsfield model get <jst>`。如果这发生在 `hook_id` 或 `setting_id` 上，则选择的模型/`job_set_type` 不支持营销工作室设置项。
- `Session expired` → `higgsfield auth login`。

参见 `references/troubleshooting.md` 以获取更多。

## 参考文档

按需加载：

- `references/model-catalog.md` — 为任务选择正确的模型
- `references/workflows.md` — `draw_to_video` 和 `reframe` 工作流生成
- `references/prompt-engineering.md` — 编写有效的提示
- `references/media-inputs.md` — 图像/视频/音频参考流和病毒性预测器视频分析
- `references/troubleshooting.md` — 常见错误和修复
- `references/marketing-avatars.md` — 预设与自定义头像
- `references/marketing-products.md` — URL 获取与手动创建产品
- `references/marketing-setup-items.md` — 钩子/设置发现和使用
- `references/marketing-ad-references.md` — 广告参考视频（创建/列表/获取）
- `references/marketing-brand-kits.md` — 品牌套件（从 URL 获取、列表、获取）
- `references/marketing-dtc-ads.md` — DTC 广告引擎 (`dtc-ads generate`)
- `references/marketing-modes.md` — 每个营销工作室模式
