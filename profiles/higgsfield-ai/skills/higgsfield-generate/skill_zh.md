# Higgsfield Generate

向任意 Higgsfield 模型提交任务。封装了 `higgsfield` CLI。覆盖通用图像/视频/3D/音频生成、Marketing Studio（品牌广告、头像、产品、钩子、设置），以及次要的 Virality Predictor 视频评分。

## 第 0 步 — 初始化

在任何其他命令之前：

1. 如果 `higgsfield` 不在 `$PATH` 中，则安装它：
   ```bash
   curl -fsSL https://raw.githubusercontent.com/higgsfield-ai/cli/main/install.sh | sh
   ```
2. 如果 `higgsfield account status` 以 `Session expired` / `Not authenticated` 失败，请询问用户运行交互式 `higgsfield auth login`，并等待确认。

## UX 规则

1. 简洁。不在聊天中输出原始 ID，不输出 JSON 数据。打印生成的媒体 URL，或 Virality Predictor 的文本摘要。
2. 不使用内部术语。不要描述"调用 higgsfield 成本"、"轮询任务"等。
3. 从第一条消息检测用户语言，并以相应语言回复。技术参数（`--aspect_ratio 16:9`）保持英文。
4. 不要批量提问。选择一个合理的默认模型，仅在确实缺失时才询问一项。
5. 除非用户要求，否则不预先预估成本或优化更便宜的模型。优先选择高质量默认。
6. 向 `generate create` 传入 `--wait`，使命令阻塞直至完成并直接打印结果 URL。避免 `create` → `wait` 两步模式。

## 发现护栏

查找 Higgsfield 功能/模型时，不要仅依赖语义搜索或 CLI 的 `--help`。首先运行未过滤的模型列表，然后检查可能的 `job_set_type` 名称。如果用户说某个模型存在但搜索无结果，则信任该信号，在回答前先用完整模型列表进行验证。

工作流与模型是分开的。通过 `higgsfield workflow list` 发现工作流，并通过 `higgsfield workflow get <workflow_name>` 检查参数。

Virality Predictor 的暴露方式为：

- 面向客户的名称：Virality Predictor
- 技术 `job_set_type`：`brain_activity`
- 类别/输出：文本报告。这是视频输入/文本输出分析，不是文本/聊天生成模型。
- 输入：上传的视频
- 用途：已发布视频的钩子、注意力、留存率及病毒性分析

如果用户说"分析这段视频"、"给这个广告打分"、"评估钩子"等，即使它出现在文本/分析模型中，也应路由到 `brain_activity`。按任务意图和所需输入进行分类，而非仅按输出类别。

## 工作流 — 通用生成

1. **选择模型。** 除非需求明确需要专业模型，否则从核心默认开始：

   - **GPT Image 2.5** → 高精度通用生成、平面设计、UI、横幅、排版、图片内文字的默认图像模型。
   - **Seedance 2.5**（`seedance_2_5`）→ SOTA 默认视频模型，适用于严肃动态内容、电影感片段、多镜头工作及图像转视频。支持 4–30 秒输出，最高 1080p；如需原生 4K，使用 Seedance 2.0。
   - **Nano Banana 2/Lite/Pro** → 角色、卡通、风格化及基于参考的图像工作的默认选择；Lite 用于速度/成本，Pro 用于更复杂的需求。
   - **Marketing Studio** → 广告、UGC、产品演示、开箱、电视广告、 presenter 视频及品牌/产品工作流的默认选择。
   - **Seed Audio 1.0** → 默认音频模型，用于文本转音频、语音、音效、环境音、拟音及类音乐音频，除非用户指定 Sonilo/Mirelo。

   **图像：**
   - 完整品牌身份、logo 系统、色彩体系、字体、品牌手册、包装体系、标识，或协调的品牌素材组合 → 使用 `higgsfield-brandkit` 代替。
   - YouTube 缩略图、Shorts 封面或 Instagram 视频封面 → 使用 `higgsfield-youtube-thumbnail` 代替。
   - 品牌产品视觉（Pinterest 图钉、生活方式、主视觉横幅、广告组合、虚拟试穿）→ 使用 `higgsfield-product-photoshoot` 代替。不是本技能。
   - 带品牌名或标签文字的生成产品概念/包装/罐/瓶 → GPT Image 2.5。
   - 带头像 + 产品的品牌广告图像（Marketing Studio 形态）→ Marketing Studio 图像（见下文 Marketing Studio）
   - 美学 UGC / 时尚编辑 / 生活方式角色 → Soul 2.0
   - 电影感静态帧 → Soul Cinema
   - 极具角色感、仅文本且独特的创意人格 → Soul Cast
   - 地点/环境/无人场景 → Soul Location（最佳水平）
   - Logo、图标、矢量风格插画、品牌标志、受控色系图形 → Recraft V4.1（`recraft_v4_1`，常配合 `--model_type vector`）
   - 人脸编辑 + 复杂场景替换 → Seedream 4.5
   - Soul Character（来自 `higgsfield-soul-id` 的参考 ID）→ 静态图像用 Soul 2.0，电影感用 Soul Cinema
   - 角色或卡通风格工作 → Nano Banana 2；快速/简单参考编辑使用 Nano Banana 2 Lite（`nano_banana_2_lite`），复杂情况升级到 Nano Banana Pro
   - 快速且低成本迭代 → Z Image
   - **其他一切默认 → GPT Image 2.5。** 平面设计、UI、横幅、排版及高精度通用生成。

   **视频：**
   - 从主题、故事或文档完成讲解性解说视频 → 使用 `higgsfield-video-explainer`，而非通用视频生成。
   - 所有广告/商业/品牌广告视频 → Marketing Studio（见下文 Marketing Studio）
   - 从草图/时间戳编辑现有视频，或重新调整为其他宽高比 → 工作流（`draw_to_video` 或 `reframe`），而非模型。见 `references/workflows.md`。
   - **所有用途的严肃视频默认（多镜头、一致身份、动态强、图像转视频、4–30 秒请求）→ Seedance 2.5。** SOTA。不要仅因 Seedance 1.5 的时长枚举更易读取就降级；先验证 Seedance 2.5。
   - 无强动态的单平面场景、低成本选项 → Kling 3.0；若用户明确要求 Turbo、更快或更低成本的 Kling 输出 → Kling 3.0 Turbo（`kling3_0_turbo`）
   - 仅当用户要求更便宜/预算输出时，使用无剪辑的干净镜头 → Seedance 1.5 Pro
   - 电影级最高保真 → Cinema Studio Video 3.0
   - 物理效果强且无需音频的便宜方案 → Minimax Hailuo
   - 快速批量/大量生成 → Veo 3.1 Lite
   - 由必需起始图出发的 bold/风格化图像转视频 → Grok Video 1.5（`grok_video_v15`）。需一个 `--start-image` 或 `--image`，时长 2–15 秒，分辨率 `480p` 或 `720p`。
   - 最多 7 张图像或一个视频参考的多模态参考转视频 → Gemini Omni Flash（`gemini_omni`）。将 Seedance 2.5 保留为严肃视频的默认选择。
   - 基于参考的生成、编辑现有视频或扩展现有视频 → **Seedance 2.5**（`seedance_2_5`），其模式为 `t2v` / `omni_reference` / `video_edit` / `video_extension`，并接受图像/视频/音频参考数组。用 `omni_reference` 处理参考输入，包括起始/结束帧；`t2v` 不接受媒体。支持最高 **1080p**；如需原生 4K 使用 Seedance 2.0。

   **视频分析：**
   - 为已发布视频的钩子、病毒性潜力、注意力、留存率或分心风险打分 → Virality Predictor（`brain_activity`）。这是返回文本评分/报告的视频分析模型，而非生成的媒体资产。

   **3D：**
   - 游戏或游戏整体资产系统中的 3D 资产 → 使用 `higgsfield-game-generation`。
   - 从一个或多个对象/产品参考图像创建实际的 3D 网格/模型/GLB → 多图像转 3D（`multi_image_to_3d`）。传入 1–4 张图像，使用重复的 `--image`；当资产需要纹理时使用 `--should_texture true`。若用户仅要求 3D 渲染的图像，则使用图像模型代替。

   **音频：**
   - **音频生成的默认 → Seed Audio 1.0（`seed_audio`）。** 用于文本转音频、音效、环境音、拟音、冲击、环境音频、语音风格生成及类音乐音频。需要 `--prompt`；仅当用户提供参考时使用可选 `--audio-references`/`--image-references`。
   - 仅当用户明确要求 Sonilo 或需要该专业音乐模型时，使用 Sonilo Music（`sonilo_music`）。需 `--prompt` 和 `--duration`，并返回音频。
   - 仅当用户明确要求 Mirelo 或需要该旧版音效模型时，使用 Mirelo Text to Audio（`mirelo_text_to_audio`）。需 `--prompt` 和 `--duration`，并返回音频。

   要获取传递给 `higgsfield generate create` 的实际 `--model` ID，运行 `higgsfield model list --json | jq` 将显示名称映射为 ID。完整表格见 `references/model-catalog.md`。

2. **将媒体输入直接传给参数。** 媒体参数接受本地文件路径**或** UUID。CLI 会自动上传路径，并自动检测 UUID 是任务还是上传。无需预先上传。每个模型声明接受的媒体角色或 `*_references` 参数 — 见 `references/media-inputs.md`。
3. **快速验证。** 若不确定参数，运行一次 `higgsfield model get <jst> --json` 并只传递所需内容。在回退到较旧模型之前先验证首选模型。其他情况使用 schema 默认值。服务器对非致命强制转换返回 `adjustments`（例如 `aspect_ratio=99:99` → 最近匹配），对无效声明的参数值返回结构化错误。
4. **一次性提交并等待。** `higgsfield generate create <jst> [--prompt "..."] [media flags] [param flags] --wait`。阻塞直至终端状态，并在标准输出打印结果。可调参数：`--wait-timeout 20m`（默认 10m），`--wait-interval 5s`（默认 3s）。Virality Predictor 不需要 prompt；传入 `--video`。
5. **交付。** 对于生成的媒体和 3D 资产，发送主要结果 URL 及一行摘要（模型、视频时长；3D 的 GLB/资产 URL）。对于 Virality Predictor，交付评分、业务解读及 Open 报告链接。不要在正常聊天输出中暴露 Virality Predictor 的 `.glb`、`.bin` 或区域表内部信息。

后续检查或重跑，可使用 `higgsfield generate list --json` 和 `higgsfield generate get <id> --json`。若曾用未带 `--wait` 的方式启动任务，仍可使用 `higgsfield generate wait <id>` 重新加入任务。

对于工作流任务，使用 `higgsfield generate workflow <workflow_name> ... --wait`。成本语法为 `higgsfield generate cost workflow <workflow_name> ...`。见 `references/workflows.md`。

## 媒体参数

| 参数 | 用途 | 接受该参数的模型 |
|---|---|---|
| `--image <path-or-id>` | 参考图像 | 大多数图像模型、`grok_video_v15`、`multi_image_to_3d`、`seedance_2_0`、`seedance_2_5`、`veo3`、`marketing_studio_video` |
| `--start-image <path-or-id>` | 图像转视频的起始帧 | `grok_video_v15`、`kling3_0`、`kling3_0_turbo`、`kling2_6`、`veo3_1`、`seedance_2_0`、`seedance_2_5`、`marketing_studio_video` |
| `--end-image <path-or-id>` | 过渡的最后一帧 | `kling3_0`、`seedance_2_0`、`seedance_2_5`、`marketing_studio_video` |
| `--video <path-or-id>` | 参考或分析视频 | `seedance_2_0`、`seedance_2_5`、`brain_activity` |
| `--audio <path-or-id>` | 参考音频（唇形同步、配乐匹配） | `seedance_2_0`、`seedance_2_5`（参考输入；区别于生成输出音频） |

对于参考数组模型，显式参数为 `--image-references`、`--video-references` 和 `--audio-references`；当 schema 暴露这些参数时，`--image`、`--video` 和 `--audio` 是简写别名。

每个参数接受本地文件路径（自动上传）或 UUID（来自 `higgsfield upload create` 的上传 ID，或先前任务 ID）。每个模型声明自己的媒体角色或 `*_references` 参数。完整表格见 `references/media-inputs.md`。

## 通用参数

参数透传至模型 schema。使用 `higgsfield model get <jst>` 来发现。

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

对于机器可读输出（链式管道、代理上下文），添加 `--json`。配合 `--wait --json`，可获取最终任务对象数组。不带 `--wait` 时，获取任务 ID 数组。Virality Predictor 将原始分析和渲染产物存储在任务参数中，但默认文本输出应保持为评分及 Open 报告。

标准输入 prompt：`echo "..." | higgsfield generate create z_image --wait`。

Soul 图像质量：对于 `text2image_soul_v2` 和 `soul_cinematic`，传入 `--quality 1.5k` 或 `--quality 2k`。这些是面向 UI 的层级；后端将其映射为 `720p`/`1080p` 以及所选 `--aspect_ratio` 下的模型特定尺寸。`soul_location` 没有质量选择器；它按宽高比使用固定尺寸。

## Marketing Studio

品牌图像/视频生成：头像 + 产品 + 可选设置钩子/设置 + 广告形态模式。使用模型 `marketing_studio_video` 和 `marketing_studio_image`。

### 概念

- **头像** — presenter 面部。精选 `preset`（浏览 `higgsfield marketing-studio avatars list`）或 `custom`（通过 `higgsfield marketing-studio avatars create` 上传的照片）。对于 UGC 模式，若需求明确提及人物，头像可省略；后端可自动创建 Soul Character。当用户需要特定 presenter 时，传入头像。
- **产品** — 带有标题 + 参考图像的品牌物品。从 URL 导入（`higgsfield marketing-studio products fetch --url ...`）或从上传图像创建（`higgsfield marketing-studio products create`）。
- **Webproduct** — App Store / 网页版本。获取 App Store URL 时自动路由。
- **钩子** — 可复用的开场角度 / 广告钩子。使用 `higgsfield marketing-studio hooks list` 浏览。钩子文本会前置到用户 prompt 中；它不会替换 `--prompt`。
- **设置** — 可复用的环境 / 场景上下文。使用 `higgsfield marketing-studio settings list` 浏览。
- **广告参考** — 可复用的灵感视频，可与头像及/或产品绑定。从上传视频（`--video-input <upload_id>`）或先前生成任务（`--job <job_id>`）创建。使用 `higgsfield marketing-studio ad-references list` 浏览。见 `references/marketing-ad-references.md`。
- **品牌套装** — 捕获品牌身份（名称、logo、主视觉图像、颜色、字体、语气），用于跨图像生成复用。通过提交网站 URL 创建（`higgsfield marketing-studio brand-kits fetch --url https://… --wait`）。见 `references/marketing-brand-kits.md`。
- **广告格式** — 驱动生成图像视觉结构的预设（`headline`、`bullet-points` 等）。只读，使用 `higgsfield marketing-studio ad-formats list` 浏览。`dtc-ads generate` 的必需输入。

### 发现命令

当用户询问已有内容时，使用以下精确的列表命令：

```bash
higgsfield marketing-studio avatars list --json
higgsfield marketing-studio products list --json
higgsfield marketing-studio hooks list --json
higgsfield marketing-studio settings list --json
higgsfield marketing-studio ad-references list --json
higgsfield marketing-studio brand-kits list --json
higgsfield marketing-studio ad-formats list --json
```

`--hook_id` 和 `--setting_id` 仅受 `marketing_studio_video` 支持；不要将其传给 `marketing_studio_image`。

### UX 规则（额外）

- 每个阶段一个问题。不要在前期同时询问产品 + 头像 + 模式。
- **两种广告方式互斥。** 要么用户提供广告参考视频（参考驱动），要么选择钩子/设置块（组合式）——两者不可兼得。若用户已选择广告参考，则不提供钩子/设置；若选择了钩子/设置，则不提供附加广告参考。
- **广告参考来源。** 唯一有效输入是本地视频文件（通过 `higgsfield upload create ... --video` 上传）或先前视频任务。若用户提供其他内容，请要求提供本地文件。
- **`dtc-ads` 广告格式为必需。** 始终询问用户从 `ad-formats list` 中选择。CLI 和服务器均拒绝未带 `--format-id` 的调用。
- **`dtc-ads` 可选输入。** 当需求需要时，建议头像、产品和参考媒体；仅附加用户选择的项。

### 工作流 — 快速广告视频

1. **获取产品。**
   - 已有产品 → `higgsfield marketing-studio products list --json`
   - URL → `higgsfield marketing-studio products fetch --url <url> --wait`（轮询直至导入完成）
   - 本地图像 → `higgsfield upload create <photo>...` 然后 `higgsfield marketing-studio products create --title "..." --image <id>...`
   - 捕获产品 ID。使用 `--hook_id` 时，强烈建议传入 `--product_ids`；钩子是为转入产品而设计的，缺乏产品上下文时效果差。
2. **如需则选择头像。**
   - 默认：`higgsfield marketing-studio avatars list`，选择一个符合品牌语气的预设。
   - 自定义：`higgsfield marketing-studio avatars create --name "..." --image <upload_id>`。
   - 对于 UGC 模式，若需求未要求特定 presenter 且提到人物，可省略 `--avatars`；后端可合成 Soul Character。
3. **可选选择设置项。**
   - 钩子：`higgsfield marketing-studio hooks list --json`
   - 设置：`higgsfield marketing-studio settings list --json`
   - 将所选 ID 作为 `--hook_id <hook_id>` 和 `--setting_id <setting_id>` 传入，仅用于 `marketing_studio_video`。除非用户明确希望强化相同措辞，否则不要将钩子的 prompt 复制到 `--prompt`。
4. **如需则选择模式。** 默认是 `ugc`；有 `--hook_id` 存在并不强制要求 `--mode`。其他当前 slug：`ugc_how_to`、`ugc_unboxing`、`product_showcase`、`product_review`、`tv_spot`、`wild_card`、`ugc_virtual_try_on`、`virtual_try_on`。**钩子/设置仅对 `ugc`、`ugc_how_to`、`ugc_unboxing`、`product_review`、`ugc_virtual_try_on` 有效** — 不要在其他模式下传入 `--hook_id` / `--setting_id`。见 `references/marketing-modes.md`。
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
   - 当选择了设置钩子/设置时，添加 `--hook_id <hook_id>` 和/或 `--setting_id <setting_id>`。
   - `product_ids` 和 `avatars` 为 JSON 数组；通过 `@/path/to/file.json` 传入。不要向 `--product_ids` 传入裸 UUID。
   - 分辨率为 `480p` 或 `720p`。宽高比为 `auto`/`21:9`/`16:9`/`4:3`/`1:1`/`3:4`/`9:16` 之一。支持 `--generate-audio true`（`seedance_2_0` 不支持）。`--wait` 阻塞至完成；运行时间较长时，提升 `--wait-timeout 30m`。
6. **交付。** URL + 一行摘要（模式、时长）。

### 点击式广告快捷方式（URL 驱动）

当用户给出产品 URL 并希望一步生成营销视频时：

```bash
# 1. 触发抓取（返回产品 ID，导入在后台运行）
higgsfield marketing-studio products fetch --url https://shop.example.com/sneakers --wait

# 2. 针对相同 URL 生成营销视频 — 后端复用该实体
higgsfield generate create marketing_studio_video \
  --url https://shop.example.com/sneakers \
  --mode ugc \
  --duration 15 \
  --aspect_ratio 9:16 \
  --wait
```

后端按 URL 去重，因此重复运行会复用现有实体，而非重新抓取。

### 工作流 — 营销图像

与上述相同，但使用 `marketing_studio_image` 模型：

```bash
higgsfield generate create marketing_studio_image \
  --prompt "..." \
  --aspect_ratio 1:1 \
  --resolution 2k \
  --wait
```

## Virality Predictor 视频评分

当用户希望将已发布视频作为商业创意进行评估时，使用 Virality Predictor（`brain_activity`）：钩子强度、病毒性潜力、注意力、留存率，或内容/产品如何保持焦点并最小化分心。将"Virality Predictor"视为面向客户的特性名称；`brain_activity` 仅为 CLI/`job_set_type`。

```bash
higgsfield generate create brain_activity --video ./creative.mp4 --wait
```

结果为文本，而非生成的图像/视频。报告总体评分、峰值钩子秒数、持续评分、最强/最弱区域，以及若有则报告 URL。将其解释为创意测试中客观的注意力代理：视觉/听觉/语言/注意力评分较高表明刺激更强、注意力更集中；默认模式（Default Mode）较低更好，表明心不在焉程度较低。

CLI 会打印类似 `https://<app-domain>/apps/virality-predictor?resultJobId=<job_id>` 的 Open 报告 URL。发送该 URL 用于可视化报告。`brain_example_url`、`vertexMapBinaryUrl` 和 `vertexMapUrl` 等原始产物 URL 是实现细节；仅在用户要求原始数据或实现细节时提及。

良好的最终输出形态：

```text
Overall score: 44/100
Peak hook: 49% at 1s
Sustain: 89%
Strongest region: Visual Cortex
Risk: Default Mode is high, which can indicate mind-wandering.

Open report: <report_url>
```

## 错误

- `Missing required params: prompt` → 用户未提供 prompt；请要求提供。
- `brain_activity` / Virality Predictor 上的 `Missing required params: medias` → 通过 `--video <path-or-id>` 精确传入一个视频。
- `Invalid values: aspect_ratio=99:99 (allowed: ...)` → 枚举值错误；从允许项中选择。
- `Unknown params: foo` → schema 不接受该参数；检查 `higgsfield model get <jst>`。若对 `hook_id` 或 `setting_id` 出现此错误，说明所选模型/`job_set_type` 不支持 Marketing Studio 设置项。
- `Session expired` → 运行 `higgsfield auth login`。

更多内容见 `references/troubleshooting.md`。

## 参考文档

按需加载：

- `references/model-catalog.md` — 为任务选择正确的模型
- `references/workflows.md` — `draw_to_video` 和 `reframe` 工作流生成
- `references/prompt-engineering.md` — 编写可用提示词
- `references/media-inputs.md` — 图像/视频/音频参考流程及 Virality Predictor 视频分析
- `references/troubleshooting.md` — 常见错误及修复
- `references/marketing-avatars.md` — 预设与自定义头像
- `references/marketing-products.md` — URL 抓取与手动产品创建
- `references/marketing-setup-items.md` — 钩子/设置发现与使用
- `references/marketing-ad-references.md` — 广告参考视频（创建/列表/获取）
- `references/marketing-brand-kits.md` — 品牌套装（从 URL 抓取、列表、获取）
- `references/marketing-dtc-ads.md` — DTC Ads Engine（`dtc-ads generate`）
- `references/marketing-modes.md` — Marketing Studio 的每种模式
