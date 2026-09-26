# Gemini Omni 闪光技能

此技能使用 Gemini Omni 1.1 闪光模型 (`gemini-omni-1.1-flash`) 来执行文本到视频生成、图像到视频生成（首帧和尾帧过渡）、视频扩展（最长40秒）以及视频编辑。

> [!WARNING]
> **重要区域限制**：在 EEA、瑞士、英国以及美国某些州上传视频以用于视频编辑或扩展是**不可用**的。如果视频到视频编辑快速完成且输出为空（`total_output_tokens: 0` 或无视频内容），则可能是由于此限制。

## 核心功能

1. **文本到视频**：根据文本提示生成视频。
2. **首帧到视频**：根据起始图像生成视频（`--first-frame`）。
3. **首帧和尾帧过渡**：在起始图像和最终图像之间生成视频插值（`--first-frame` 和 `--last-frame`；注意：`--last-frame` 必须与 `--first-frame` 一起使用）。
4. **视频扩展**：通过每次最多10秒的回合扩展现有视频，总长度最多为40秒（`--extend` 或 `--previous-interaction-id`）。
5. **视频编辑和细化**：编辑现有视频（最大时长10秒），应用风格变化或执行修复/扩展。
6. **图像和视频参考生成**：使用来自图像或视频的风格、角色或对象参考来指导视频生成。

## 工作流程

1. **分析请求**：确定目标任务（例如，首帧到视频、首帧和尾帧过渡、视频扩展、参考引导编辑）并识别任何输入媒体资源。
2. **运行 SDK 脚本**：

   * 直接运行相应的工具（`scripts/video/generate_video.py` 或 `scripts/upload_file.py`）。
   * 配置设置，如 `--aspect-ratio`（例如 `16:9`、`9:16`）、`--resolution`（`360p`、`720p`、`1080p`、`4k`；默认：`720p`）和 `--duration`（任何介于 `3` 和 `10` 秒之间的整数，例如 `3`、`5`、`10`）。*注意：`4k` 请求生成时间更长。*

3. **检索和处理输出**：输出保存到本地文件系统（例如 `media/`）。向用户报告完成的媒体路径。

## 参考文档

* **交互 API**：所有 Gemini Omni 1.1 闪光模型 (`gemini-omni-1.1-flash`) 的操作和状态管理通过 [交互 API](https://ai.google.dev/gemini-api/docs/interactions-overview) 处理。
* **文件 API**：输入媒体文件（如参考图像和视频）必须先通过 [文件 API](https://ai.google.dev/gemini-api/docs/files) 上传，然后才能在生成中引用。然后，上传的文件 URI 和 MIME 类型包含在 `interactions.create` 输入部分数组中。
* **[Gemini API 技能参考](https://github.com/google-gemini/gemini-skills/blob/main/skills/gemini-api-dev/SKILL.md)**：平台级指南、当前模型规范和 Gemini API SDK 使用规则。

## 依赖项和先决条件

* **Python SDK (`google-genai`)**：需要 `google-genai >= 2.19.0`（Python）以支持 `interactions` 客户端和完整视频输出分辨率配置（`360p`、`720p`、`1080p`、`4k`）。使用以下命令安装或升级：
  ```bash
  pip install -U google-genai
  ```
* **Python 运行时**：需要 **Python >= 3.10**（以兼容现代 `google-genai` SDK 类型和方法）。
* **ffmpeg & ffprobe**：`prep_video.py`、`inspect_video.py` 和 `generate_video.py`（在通过 `--strip-audio` 剥离音频时）需要安装 `ffmpeg` 和 `ffprobe` 二进制文件，并在系统 `PATH` 中可用。
* **API 密钥**：设置 `GEMINI_API_KEY` 环境变量：
  ```bash
  export GEMINI_API_KEY="your-api-key"
  ```

## 可用脚本

使用以下 Python 脚本上传媒体（使用 Files API）、使用 ffmpeg 准备输入视频以及使用交互 API 生成视频输出。

1. **[upload_file.py](scripts/upload_file.py)**：将本地媒体（图像和视频）上传到 Files API 并轮询直到 `ACTIVE`。如果上传大于 25MB 的视频，它会打印一个信息性警告/提示，突出 Gemini Omni Flash 优化于编辑 10 秒 720p/24fps 视频，并建议首先使用 `prep_video.py` 进行预处理以加快上传速度。

   ```bash
   ./scripts/upload_file.py path/to/image.png
   ```

2. **[generate_video.py](scripts/video/generate_video.py)**：执行端到端视频生成并下载输出视频。它检测并上传本地媒体引用（图像或视频），然后调用交互 API。大于 25MB 的视频资产将触发信息性预处理建议，而不会阻止上传。

   * **文本到视频**：

     ```bash
     ./scripts/video/generate_video.py "一只猫正在喝茶的特写" --output media/cat_tea.mp4
     ```

   * **输出分辨率选项（`--resolution`）**：

     Gemini Omni 1.1 闪光原生支持四种输出分辨率，涵盖横屏（`16:9`）和竖屏（`9:16`）两种宽高比：
     - `360p`：`640x360`（16:9）或 `360x640`（9:16）
     - `720p`：`1280x720`（16:9）或 `720x1280`（9:16）—— *(默认)*
     - `1080p`：`1920x1080`（16:9）或 `1080x1920`（9:16）
     - `4k`：`3840x2160`（16:9）或 `2160x3840`（9:16）

     ```bash
     # 高清（1080p）
     ./scripts/video/generate_video.py "日出时分，无人机飞越薄雾笼罩的山脉的航拍镜头" --resolution 1080p --output media/mountains_1080p.mp4

     # 超高清 4K（注意：4K 请求生成时间更长；如有需要，可传递 --timeout）
     ./scripts/video/generate_video.py "金色阳光下，花蕾上露珠的微距拍摄" --resolution 4k --timeout 900 --output media/flower_4k.mp4
     ```

   * **可配置请求超时（`--timeout`）**：

     默认 HTTP 超时为 `600` 秒（10 分钟）。对于计算密集型请求——例如，通过 `--extend` 或 `--previous-interaction-id` 将 30 秒视频扩展到 4K（总时长最多 40 秒）——生成可能需要几分钟。使用 `--timeout 900`（或 `1200`）以提供更长的执行预算。

   * **首帧到视频**：

     ```bash
     ./scripts/video/generate_video.py "海浪拍打海岸。" --first-frame start.png --output media/waves.mp4
     ```

   * **首帧和尾帧过渡**：

     提供起始帧和结束帧以生成它们之间的平滑过渡（注意：`--last-frame` **必须**与 `--first-frame` 一起使用）：

     ```bash
     ./scripts/video/generate_video.py "从日出到日落的平滑延时摄影" --first-frame start.png --last-frame end.png --output media/interpolation.mp4
     ```

   * **循环视频（相同的起始和结束帧）**：

     ```bash
     ./scripts/video/generate_video.py "一个水晶球持续原地旋转" --first-frame orb.png --last-frame orb.png --output media/loop.mp4
     ```

   * **图像参考视频生成**：

     ```bash
     ./scripts/video/generate_video.py "一个赛博战士，风格为 <IMAGE_REF_0>" --image reference.png --output media/warrior.mp4
     ```

   * **视频参考视频生成**：

     提供一个或多个参考视频（`--video-reference` / `-vr`）来指导角色、对象或运动风格（理想时长约为 3 秒，最多 3 个参考视频推荐）：

     ```bash
     ./scripts/video/generate_video.py "一个音乐家正在拉小提琴，风格为 <VIDEO_REF_0>" --video-reference ref_dance.mp4 --output media/cello.mp4
     ```

   * **视频扩展（扩展现有视频）**：

     通过每次最多 10 秒扩展现有视频（总时长最多 40 秒）：

     ```bash
     ./scripts/video/generate_video.py "场景随着太阳落在地平线上继续" --extend media/sunset.mp4 --output media/sunset_extended.mp4
     ```

   * **带参考图像和参考视频的视频扩展**：

     基于提示的扩展允许同时传递参考图像和参考视频：

     ```bash
     ./scripts/video/generate_video.py "扩展此视频。角色 <IMAGE_REF_0> 进入跳舞，像 <VIDEO_REF_0> 中的舞者一样。" --extend media/sunset.mp4 --image character.png --video-reference dance_ref.mp4 --output media/sunset_extended_with_refs.mp4
     ```

   * **视频编辑（保留原始音频）**：

     ```bash
     ./scripts/video/generate_video.py "将风格转换为日本动漫" --video input.mp4 --output media/anime_style.mp4
     ```

   * **视频编辑（从头开始重新生成所有音频）**：

     ```bash
     ./scripts/video/generate_video.py "将风格转换为日本动漫" --video input.mp4 --strip-audio --output media/anime_style_new_audio.mp4
     ```

   * **回合制视频编辑（编辑先前的交互）**：

     通过传递交互 ID 而无需重新上传资产来编辑先前的视频生成：

     ```bash
     ./scripts/video/generate_video.py "将场景改为一个雪中的仙境。" --previous-interaction-id "v1_..." --output media/winter_wonderland.mp4
     ```

   * **回合制视频扩展（扩展先前的交互）**：

     通过传递先前的交互 ID 扩展先前的视频生成：

     ```bash
     ./scripts/video/generate_video.py "扩展此视频。角色转身开始跑步。" --previous-interaction-id "v1_..." --output media/extended_turn.mp4
     ```

   * **并行批处理执行（提示文件）**：从行文本文件并发运行多个提示：

     ```bash
     ./scripts/video/generate_video.py --prompts-file prompts.txt --concurrency 3
     ```

   * **并行批处理执行（JSON 配置）**：并行执行完全配置的独立生成和编辑作业：

     ```bash
     ./scripts/video/generate_video.py --batch jobs.json --concurrency 3
     ```

     *示例 `jobs.json`：*

     ```json
     [
       {
         "prompt": "从日出到日落的平滑延时摄影。",
         "first_frame": "start.png",
         "last_frame": "end.png",
         "resolution": "1080p",
         "output": "media/interpolation.mp4"
       },
       {
         "prompt": "扩展此视频。场景随着角色 <IMAGE_REF_0> 跳舞，像 <VIDEO_REF_0> 中的舞者一样。",
         "extend": "media/sunset.mp4",
         "image": "character.png",
         "video_reference": "dance_ref.mp4",
         "output": "media/extended_with_refs.mp4"
       },
       {
         "prompt": "一个水晶球折射宇宙星云颜色的微距拍摄。",
         "resolution": "4k",
         "output": "media/nebula_orb_4k.mp4"
       },
       {
         "prompt": "一个音乐家正在拉小提琴，风格为 <VIDEO_REF_0>。",
         "video_reference": "cello_ref.mp4",
         "output": "media/cello.mp4"
       },
       {
         "prompt": "将风格转换为日本动漫。",
         "video": "input.mp4",
         "output": "media/anime_style.mp4",
         "strip_audio": false,
         "aspect_ratio": "16:9"
       }
     ]
     ```

3. **[inspect_video.py](scripts/video/inspect_video.py)**：检查本地视频文件（使用 `ffprobe`）以检查其时长、分辨率、帧率（FPS）、音频流存在以及格式详细信息。

   ```bash
   ./scripts/video/inspect_video.py media/output.mp4
   ```

   * 获取预解析的、结构化的 JSON 摘要：

     ```bash
     ./scripts/video/inspect_video.py media/output.mp4 --json
     ```

   * 获取完整的、未修改的 `ffprobe` 原始 JSON 倾倒：

     ```bash
     ./scripts/video/inspect_video.py media/output.mp4 --raw
     ```

4. **[prep_video.py](scripts/video/prep_video.py)**：规范化、修剪和格式化任何视频文件以适应标准 Gemini Omni Flash 生成和编辑限制。它处理基于时间码的修剪、可选帧率转换以及大型视频的比例缩放（横屏最大 1280x720，竖屏最大 720x1280），以优化上传时间而不拉伸。如果视频时长超过 10 秒并且脚本以交互方式运行（在 TTY 中），它会提示用户选择前 10 秒、后 10 秒或输入自定义时间码（默认为前 10 秒）。

   * **修剪前 10 秒（默认）**：

    ```bash
     ./scripts/video/prep_video.py path/to/source.mp4
     ```

     或显式指定起始点和持续时间：

     ```bash
     ./scripts/video/prep_video.py path/to/source.mp4 --start 0 --duration 10
     ```

   * **修剪后 10 秒**（自动根据源长度计算起始点）：

     ```bash
     ./scripts/video/prep_video.py path/to/source.mp4 --start last
     ```

   * **从特定时间码修剪 10 秒**（MM:SS 或 HH:MM:SS）：

     ```bash
     ./scripts/video/prep_video.py path/to/source.mp4 --start 00:03 --output media/custom.mp4
     ```

   * **自定义帧率和分辨率**：

     ```bash
     ./scripts/video/prep_video.py path/to/source.mp4 --fps 30 --resolution 1920x1080
     ```

   * **剥离音频以重新生成音频**：

     ```bash
     ./scripts/video/prep_video.py path/to/source.mp4 --strip-audio --output media/video_with_no_audio.mp4
     ```

## 视频编辑中的音频处理

当编辑包含音频的源视频时，您必须在保留原始音频或从头开始重新生成所有音频之间进行选择。

* **保留原始音频**：默认情况下，Gemini Omni Flash 保留现有音频层（尽管它在生成过程中可能会对其进行修改或调整）。当您希望保留原始背景音乐、对话或音效时，请使用此选项。
* **从头开始重新生成所有音频**：如果您希望 Gemini Omni Flash 重新创建一个针对新视觉风格或提示量身定制的新音频层，则**必须**上传剥离了音频流的视频。如果存在任何音频流，Gemini Omni Flash 将尝试保留/修改它，而不是从头开始。

  * 在使用 `scripts/video/prep_video.py` 或执行 `scripts/video/generate_video.py` 时使用 `--strip-audio`（或 `-a`）进行预处理。
  * 这会强制 Gemini Omni Flash 执行完整音频生成。

## 提示 Gemini Omni Flash

### 单场景

默认情况下 Gemini Omni Flash 将尝试创建一个包含几个不同镜头的视频。它将尝试根据提示制作一个有趣的叙事。

如果您需要输出视频包含单个场景，则必须在提示中明确要求：

* 在单个不间断场景中
* 在单个连续镜头中
* 无场景剪辑

例如：

```
手持连续镜头拍摄一只蓬松的虎斑猫坐在阳光明媚的窗台上，凝视着叶茂的花园。猫的尾巴缓慢地抽动，耳朵稍微转向环境噪音。阳光照亮了空气中的尘埃。音效设计：轻柔的风声，远处的鸟鸣。无对话。
```

### 移除不需要的元素

如果生成的视频包含您不想要的元素，请包括简单的负面提示以避免它们：

* 无对话
* 无装饰
* 无额外音效

### 编辑提示

简单的提示最适合视频编辑。过于描述性的提示可能导致意外变化。

以下是一些简单的编辑提示示例：

* 将此视频制作成动漫
* 给这个人戴上一顶时尚的帽子
* 将标志上的文字改为“Omni Flash”

当编辑视频的特定方面时，包括 `"保持其他所有内容不变"` 以保持视觉一致性。

以下是一些示例，说明如何应用此技术：

* **避免**：`在沙发上坐着的人的视频中，请添加一个小黑猫从屏幕右侧跑来，跳到他的膝盖上，然后他开始抚摸它的头，同时低头看。`
  * **简化**：`添加一只跳到他的膝盖上，他开始抚摸它。保持其他所有内容不变。`
* **避免**：`请移除这个人手中拿着的手机，并填充背景，使其看起来像他只是空着手。`
  * **简化**：`使手机不可见。保持其他所有内容不变。`

### 提示音频

默认情况下，模型将尝试为视频生成适当的音频轨道。这可能不是您想要的结果。您可以使用提示来描述您想要的音频类型。这在您希望在视频中包含音乐时尤其重要：

* 包含平静的背景音乐
* 视频具有高能量的电子节拍
* 音频是背景中播放歌曲的低沉的收音机广播

### 时间事件

您可以提示在视频的特定时间发生事情，不需要精确的语法，可以使用自然语言。这在创建您自己的场景剪辑、节奏或快速连续序列时特别有用。以下是一些示例：

* 3 秒后，一名女性进入场景。
* 5 秒时，背景音频中的副歌开始。
* 每 2 秒切换到新帧。
* 在快速连续序列中，每半秒（24fps 的 12 帧）切换到新的场景。

您也可以使用时间码语法：

```
[0-3s] 一个人正在走路
[3-6s] 他们停下来转身
[6-10s] 他们开始跑步
```

### 元提示

您可以要求 Gemini Omni Flash 专注于视频生成的通用质量或原则：

* 考虑微观细节、表情和时机，以创建一个非常丰富、详细但完全自然的场景。
* 在角色和环境描述中极其详细。将服装设计原则应用于角色。非常具体地描述场景中的人、物品和对象。
* 在背景元素中包含大量适当的细节，以使场景感觉真实自然。
* 制作一个快速连续的视频，每 1 秒显示一个不同的稀有 `[事物]`，欢快的音乐，包括标签文本。

### 视频中的文本

您可以提示在视频中包含文本，Gemini 将以正确且可读的方式渲染。如果您的视频中会自然出现文本，即使是在背景元素中，它也有助于定义它应该说什么。

* 一次一个词显示在屏幕上：`did, you, know, that, Omni, can, do, awesome, text?` 每个词显示 1 秒，使用不同的动画风格。无对话。
* 有一块路牌写着：`这是由 Omni 生成的 AI 生成内容`，有一家商店写着：`所有你需要 AI`，有一辆车车牌为：`OMNI1.1`

### 扩展视频的提示

使用 Gemini Omni 1.1 Flash，您可以使用提示，如 `"扩展此视频"` 或 `"场景继续"`，最多扩展 10 秒，总时长最多为 40 秒。

Omni 通过使用您原始视频的最后 10 秒作为上下文来创建一个扩展，以保持视频、运动、角色和音频的连贯性。您输入视频中的一些最终帧将被编辑，以使过渡无缝。

> [!TIP]
> **带参考的扩展**：视频扩展可以使用提示（例如，`"扩展此视频"`，`"场景继续"`）而不设置 API 的 `task="extend"` 参数。省略 `task` 参数允许在视频扩展期间传递参考图像（`--image`）和参考视频（`--video-reference`），以将新的角色、对象或风格无缝地引入扩展场景。如果显式设置 `task="extend"`，则无法传递多模态参考。

扩展时，本指南中所有 Omni 提示技巧仍然适用：

* 描述扩展场景中的音频，特别是如果您需要它改变，`"音乐继续进入副歌"`
* 描述场景是否继续，或者是否有镜头切换到新场景（可能使用相同的人物），`"显示相同的人物在下一个场景"`
* 扩展时包括图像和视频作为参考，以帮助保持输出准确，或引入新角色，`"参考图像中显示的人物进入场景"`，`"参考视频 <VIDEO_REF_0> 中的狗跳到沙发上"`
* 如果使用时间码或时间码语法，0s 指的是扩展视频部分的开始。如果扩展 10 秒视频，则此提示中的场景切换将在 12 秒发生： `"2 秒后切换到具有相同人物的新场景"`

### 视频扩展限制和指南

* **时长限制**：用于扩展的输入视频在上传时必须为 10 秒或更短（除非使用多回合）。
* **上传视频中的人声**：目前，您无法扩展上传的视频，其中有人正在说话以添加额外对话（如果角色保持沉默或提示不添加对话则支持）。
* **多回合语音扩展**：生成语音对话或语音支持通过多回合 (`previous_interaction_id`) 扩展先前生成的视频。
* **任务参数建议**：我们建议主要依赖提示，仅在提示不起作用且您需要帮助模型理解它应使用哪种模式时才使用 `task="extend"` 字段，因为设置 `task` 字段会添加约束（例如禁用多模态参考输入）。

### 使用标签在提示中设置图像和视频角色

您可以使用标签将上传的媒体绑定到特定的生成角色。这允许您指定每个图像或视频是起始帧、最终帧还是参考。

#### 简单标签（推荐）

对于媒体角色从提示中清晰的情况，您可以直接将图像和视频绑定到角色：

* **`<FIRST_FRAME>`**：将图像用作视频的起始帧，例如：`<FIRST_FRAME> 一位女性正在走路`
* **`<LAST_FRAME>`**：将图像用作视频的最终帧以进行过渡。必须与 `<FIRST_FRAME>` 一起使用，例如：`<FIRST_FRAME> <LAST_FRAME> 一位女性正在走路`
* **`<IMAGE_REF_N>`**：将图像用作参考，例如：`在 <IMAGE_REF_0> 风格中，一位女性 <IMAGE_REF_1> 正在走路`（结合了来自第一个图像的风格参考和来自第二个图像的主题参考）。图像参考从 0 开始。
* **`<VIDEO_REF_N>`**：将视频用作角色或对象参考，例如：`<VIDEO_REF_0> 中的那个人正在拉小提琴`。视频参考也从 0 开始。

> [!NOTE]
> **参考视频指南**：
> * **时长**：理想的参考视频是 **~3 秒**，虽然更长的视频也可以。如果您想将更长的源文件修剪为参考长度，请使用 `prep_video.py --duration 3`。
> * **数量**：最多 **3 个参考视频** 是理想的，虽然也可以使用更多。

以下是包含 6 个参考图像的示例：

```
[0-3s] 一个工作室时尚序列。从 <FIRST_FRAME>@Image1 开始，她拿着 <IMAGE_REF_1>
[3-6s] 然后我们看到 <IMAGE_REF_2> 拿着 <IMAGE_REF_3>
[6-10s] 最后，另一位女性 <IMAGE_REF_4> 拿着 <IMAGE_REF_5> 走路。
```

#### 声明源和参考

对于具有多个媒体输入和多个角色的更复杂的情况，您可以使用明确的前缀标签与自然语言指令配对。您应该在提示的开头声明这些源和参考。

  * `[# Sources <FIRST_FRAME>@Image1]` 将使用第一个图像作为起始帧。
  * `[# Sources <FIRST_FRAME>@Image1 <LAST_FRAME>@Image2]` 将使用第一个图像作为起始帧，第二个图像作为最终帧。
  * `[# Sources <FIRST_FRAME>@Image1 <LAST_FRAME>@Image1]` 将使用第一个图像作为起始帧和最终帧，创建一个循环视频。
  * `[# Sources <FIRST_FRAME>@Image1] [# References <IMAGE_REF_0>@Image2]` 将使用第一个图像作为起始帧，第二个图像作为参考。
  * `[# Sources <VIDEO_0>@Video1]` 将使用视频作为主要源视频进行编辑或修改。
  * `[# Sources <PREVIOUS_VIDEO>@Video1]` 将使用上一回合的视频。
  * `[# References <IMAGE_REF_0>@Image1]` 将使用第一个图像作为参考。
  * `[# References <IMAGE_REF_1>@Image2]` 将使用第二个图像作为参考。
  * `[# References <IMAGE_REF_0>@Image1 <IMAGE_REF_1>@Image2]` 将使用两个图像作为参考。
  * `[# References <VIDEO_REF_0>@Video1]` 将使用第一个视频作为参考。
  * `[# References <IMAGE_REF_0>@Image1 <VIDEO_REF_0>@Video1]` 将使用图像和视频作为参考。

在提示的末尾添加指导说明：

  * 对于起始帧：`使用此图像作为起始帧。`
  * 对于通过起始和结束帧创建循环视频：`使用此图像作为第一帧和最后一帧。`
  * 对于参考图像：`使用给定的图像作为视频生成的参考。图像不应作为字面初始帧使用。`
  * 对于参考视频：`使用给定的视频作为参考。不要将它们用作视频编辑的源。`

以下是一些包含源和参考的提示示例：

```
[# Sources <FIRST_FRAME>@Image1] [# References <IMAGE_REF_0>@Image2] 一位女性 <IMAGE_REF_0> 正在走路。使用 Image1 作为起始帧。使用 Image2 作为视频生成的参考。
```

```
[# References <IMAGE_REF_0>@Image1 <VIDEO_REF_0>@Video1] <VIDEO_REF_0> 中的女性正在拉小提琴，显示在 <IMAGE_REF_0> 中。使用 Video1 作为角色参考，Image1 作为对象参考。
```
