---
name: gemini-omni-flash-api
description: 使用此技能进行生成式视频编辑、文本转视频、图像参考视频生成、首帧转视频、首尾帧过渡以及使用 Gemini Omni 1.1 Flash (gemini-omni-1.1-flash) 通过官方 google-genai SDK 进行视频扩展。包含使用 ffmpeg 对高分辨率或长源视频进行预处理/优化的工作流程、音频剥离以实现完整声音再生，以及处理逐帧视频编辑和并行执行。
---

# Gemini Omni Flash 功能

该功能使用 Gemini Omni 1.1 Flash 模型 (`gemini-omni-1.1-flash`) 进行文本转视频生成、图像转视频生成（首帧和尾帧过渡）、视频扩展（最长40秒）以及视频编辑。

> [!WARNING]
> **重要区域限制**：在 EEA、瑞士、英国以及美国部分州上传视频用于视频编辑或扩展是**不可用**的。如果视频到视频编辑快速完成且输出为空（`total_output_tokens: 0` 或无视频内容），这可能是由于此限制。

## 核心功能

1. **文本转视频**：根据文本提示生成视频。
2. **首帧转视频**：根据起始图像生成视频 (`--first-frame`)。
3. **首帧和尾帧过渡**：在起始图像和最终图像之间生成视频（`--first-frame` 和 `--last-frame`；注意：`--last-frame` 必须与 `--first-frame` 一起使用）。
4. **视频扩展**：每次最多扩展10秒，总时长最长40秒（`--extend` 或 `--previous-interaction-id`）。
5. **视频编辑和细化**：编辑现有视频（最长10秒），应用风格变化，或执行修复/扩展。
6. **图像和视频参考生成**：使用图像或视频中的风格、角色或对象参考来指导视频生成。

## 工作流程

1. **分析请求**：确定目标任务（例如，首帧转视频、首尾帧过渡、视频扩展、参考引导编辑）并识别任何输入媒体资源。
2. **运行 SDK 脚本**：

   * 直接运行相应的工具 (`scripts/video/generate_video.py` 或 `scripts/upload_file.py`)。
   * 配置设置，如 `--aspect-ratio`（例如 `16:9`、`9:16`）、`--resolution`（`360p`、`720p`、`1080p`、`4k`；默认：`720p`）和 `--duration`（任何介于 `3` 和 `10` 秒之间的整数，例如 `3`、`5`、`10`）。*注意：`4k` 请求生成时间更长。*

3. **获取和处理输出**：输出保存到本地文件系统（例如 `media/`）。向用户报告完成的媒体路径。

## 参考文档

* **交互 API**：Gemini Omni 1.1 Flash 模型 (`gemini-omni-1.1-flash`) 的所有操作和状态管理均通过 [交互 API](https://ai.google.dev/gemini-api/docs/interactions-overview) 处理。
* **文件 API**：输入媒体文件（如参考图像和视频）必须先通过 [文件 API](https://ai.google.dev/gemini-api/docs/files) 上传，然后才能在生成中引用。然后，将上传的文件 URI 和 MIME 类型包含在 `interactions.create` 输入部分数组中。
* **[Gemini API 功能参考](https://github.com/google-gemini/gemini-skills/blob/main/skills/gemini-api-dev/SKILL.md)**：平台级指南、当前模型规范和 Gemini API SDK 使用规则。

## 依赖项和前提条件

* **Python SDK (`google-genai`)**：需要 `google-genai >= 2.19.0`（Python）以支持 `interactions` 客户端和完整视频输出分辨率配置（`360p`、`720p`、`1080p`、`4k`）。使用以下命令安装或升级：
  ```bash
  pip install -U google-genai
  ```
* **Python 运行时**：需要 **Python >= 3.10**（以兼容现代 `google-genai` SDK 类型和方法）。
* **ffmpeg & ffprobe**：`prep_video.py`、`inspect_video.py` 和 `generate_video.py`（在通过 `--strip-audio` 剥离音频时）需要安装 `ffmpeg` 和 `ffprobe` 二进制文件并在系统 `PATH` 中可用。
* **API 密钥**：设置 `GEMINI_API_KEY` 环境变量：
  ```bash
  export GEMINI_API_KEY="your-api-key"
  ```

## 可用脚本

使用以下 Python 脚本上传媒体（使用 Files API）、使用 ffmpeg 准备输入视频以及使用交互 API 生成视频输出。

1. **[upload_file.py](scripts/upload_file.py)**：将本地媒体（图像和视频）上传到 Files API 并轮询直到 `ACTIVE`。如果上传的视频大于 25MB，它将打印一条信息性警告/提示，突出显示 Gemini Omni Flash 专为编辑 10 秒 720p/24fps 视频而优化，并建议首先使用 `prep_video.py` 进行预处理以加快上传速度。

   ```bash
   ./scripts/upload_file.py path/to/image.png
   ```

2. **[generate_video.py](scripts/video/generate_video.py)**：执行端到端视频生成并下载输出视频。它检测并上传本地媒体引用（图像或视频）然后再调用交互 API。大型视频资产（>25MB）将触发信息性预处理建议，而不会阻止上传。

   * **文本转视频**：

     ```bash
     ./scripts/video/generate_video.py "一只猫在阳光下窗台上喝茶的特写" --output media/cat_tea.mp4
     ```

   * **输出分辨率选项 (`--resolution`)**：

     Gemini Omni 1.1 Flash 原生支持四种输出分辨率，适用于横屏（`16:9`）和竖屏（`9:16`）两种长宽比：
     - `360p`：`640x360`（16:9）或 `360x640`（9:16）
     - `720p`：`1280x720`（16:9）或 `720x1280`（9:16） — *(默认)*
     - `1080p`：`1920x1080`（16:9）或 `1080x1920`（9:16）
     - `4k`：`3840x2160`（16:9）或 `2160x3840`（9:16）

     ```bash
     # 高清（1080p）
     ./scripts/video/generate_video.py "日出时雾蒙蒙的山上航拍电影镜头" --resolution 1080p --output media/mountains_1080p.mp4

     # 超高清 4K（注意：4K 请求生成时间更长；如需，可传递 --timeout）
     ./scripts/video/generate_video.py "金色阳光下花瓣上的露珠宏观拍摄" --resolution 4k --timeout 900 --output media/flower_4k.mp4
     ```

   * **可配置请求超时 (`--timeout`)**：

     默认 HTTP 超时为 `600` 秒（10 分钟）。对于计算密集型请求——例如，在 4K 中将 30 秒视频扩展 10 秒（总时长最长 40 秒）——生成可能需要几分钟。使用 `--timeout 900`（或 `1200`）以提供更长的执行预算。

   * **首帧转视频**：

     ```bash
     ./scripts/video/generate_video.py "海浪拍打海岸。" --first-frame start.png --output media/waves.mp4
     ```

   * **首尾帧过渡**：

     提供起始帧和结束帧以生成它们之间的平滑过渡（注意：`--last-frame` **必须**与 `--first-frame` 一起使用）：

     ```bash
     ./scripts/video/generate_video.py "从日出到日落的平滑延时摄影" --first-frame start.png --last-frame end.png --output media/interpolation.mp4
     ```

   * **循环视频（起始帧和结束帧相同）**：

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
     ./scripts/video/generate_video.py "一个演奏大提琴的音乐家，风格为 <VIDEO_REF_0>" --video-reference ref_dance.mp4 --output media/cello.mp4
     ```

   * **视频扩展（扩展现有视频）**：

     将现有视频扩展最多 10 秒（总时长最长 40 秒）：

     ```bash
     ./scripts/video/generate_video.py "场景随着太阳落在地平线上继续" --extend media/sunset.mp4 --output media/sunset_extended.mp4
     ```

   * **带参考图像和参考视频的视频扩展**：

     基于提示的扩展允许同时传递参考图像和参考视频：

     ```bash
     ./scripts/video/generate_video.py "扩展这个视频。角色在 <IMAGE_REF_0> 中进入跳舞，像 <VIDEO_REF_0> 中的舞者一样。" --extend media/sunset.mp4 --image character.png --video-reference dance_ref.mp4 --output media/sunset_extended_with_refs.mp4
     ```

   * **视频编辑（保留原始音频）**：

     ```bash
     ./scripts/video/generate_video.py "将风格转换为日本动漫" --video input.mp4 --output media/anime_style.mp4
     ```

   * **视频编辑（从头开始重新生成所有音频）**：

     ```bash
     ./scripts/video/generate_video.py "将风格转换为日本动漫" --video input.mp4 --strip-audio --output media/anime_style_new_audio.mp4
     ```

   * **逐帧视频编辑（编辑先前的交互）**：

     通过传递交互 ID 而无需重新上传资产来编辑先前的视频生成：

     ```bash
     ./scripts/video/generate_video.py "将场景改为一个雪中的仙境。" --previous-interaction-id "v1_..." --output media/winter_wonderland.mp4
     ```

   * **逐帧视频扩展（扩展先前的交互）**：

     通过传递先前的交互 ID 来扩展先前的视频生成：

     ```bash
     ./scripts/video/generate_video.py "扩展这个视频。角色转身开始跑步。" --previous-interaction-id "v1_..." --output media/extended_turn.mp4
     ```

   * **并行批处理执行（提示文件）**：从行文本文件中并发运行多个提示：

     ```bash
     ./scripts/video/generate_video.py --prompts-file prompts.txt --concurrency 3
     ```

   * **并行批处理执行（JSON 配置）**：并行执行完全配置的、不同的生成和编辑作业：

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
         "prompt": "扩展这个视频。场景继续，角色在 <IMAGE_REF_0> 中跳舞，像 <VIDEO_REF_0> 中的舞者。",
         "extend": "media/sunset.mp4",
         "image": "character.png",
         "video_reference": "dance_ref.mp4",
         "output": "media/extended_with_refs.mp4"
       },
       {
         "prompt": "一个水晶球折射宇宙星云颜色的宏观拍摄。",
         "resolution": "4k",
         "output": "media/nebula_orb_4k.mp4"
       },
       {
         "prompt": "一个演奏大提琴的音乐家，风格为 <VIDEO_REF_0>。",
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

3. **[inspect_video.py](scripts/video/inspect_video.py)**：使用 `ffprobe` 检查本地视频文件，以检查其时长、分辨率、帧率（FPS）、音频流存在以及格式详细信息。

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

4. **[prep_video.py](scripts/video/prep_video.py)**：规范化、修剪和格式化任何视频文件以适应 Gemini Omni Flash 生成和编辑的标准限制。它处理基于时间码的修剪、可选帧率转换以及大型视频的按比例缩放（横屏最大 1280x720，竖屏最大 720x1280），以优化上传时间而不拉伸。如果视频时长超过 10 秒并且脚本以交互方式运行（在 TTY 中），它将提示用户选择前 10 秒、后 10 秒或输入自定义时间码（默认为前 10 秒）。

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

* **保留原始音频**：默认情况下，Gemini Omni Flash 保留现有音频层（尽管它在生成过程中可能会对其进行修改或调整）。当原始背景音乐、对话或音效需要时使用此选项。
* **从头开始重新生成所有音频**：如果您希望 Gemini Omni Flash 重新创建一个针对新视觉风格或提示量身定制的全新音频层，您**必须**上传剥离了音频流的视频。如果存在任何音频流，Gemini Omni Flash 将尝试保留/修改它而不是从头开始。

  * 在使用 `scripts/video/prep_video.py` 或执行 `scripts/video/generate_video.py` 进行预处理时使用 `--strip-audio`（或 `-a`）。
  * 这将强制 Gemini Omni Flash 执行完整音频生成。

## 提示 Gemini Omni Flash

### 单个场景

默认情况下 Gemini Omni Flash 将尝试创建一个包含几个不同镜头的视频。它将尝试根据提示制作一个有趣的叙事。

如果您需要输出视频包含单个场景，您必须提示：

* 在单个连续场景中
* 在单个连续镜头中
* 无场景剪辑

例如：

```
手持连续镜头的毛茸茸的虎斑猫坐在阳光明媚的窗台上，凝视着叶茂的花园。猫的尾巴慢慢抽动，耳朵稍微转向环境噪音。阳光照亮了空气中的尘埃颗粒。音效设计：轻柔的风声，远处的鸟鸣声。无对话。
```

### 移除不需要的元素

如果生成的视频包含您不想要的元素，请包括简单的负面提示来避免它们：

* 无对话
* 无装饰
* 无额外音效

### 编辑提示

简单的提示最适合视频编辑。过于描述性的提示可能导致意外变化。

以下是一些简单的编辑提示示例：

* 将此视频制作成动漫
* 给这个人戴一顶时尚的帽子
* 将灯光改为更具戏剧性
* 将标志上的文字改为“Omni Flash”

当编辑视频的特定方面时，包括 `"保持其他一切不变"` 以保持视觉一致性。

以下是一些示例，说明如何应用此技术：

* **避免：** 在视频中，请添加一只小黑猫，它从屏幕右侧跑来，跳到沙发上，然后他开始抚摸它的头，同时低头看着。`
  * **简化：** 添加一只跳到他腿上的猫，他开始抚摸它。保持其他内容不变。`
* **避免：** 请移除那个人手中拿着的手机，并填充背景，使其看起来像他只是空着手。`
  * **简化：** 使手机隐形。保持其他内容不变。`

### 提示音频

默认情况下，模型会尝试为视频生成合适的音频轨道。但这并不总是你想要的结果。你可以使用你的提示来描述你想要的音频类型。如果你想在视频中添加音乐，这一点尤其重要：

* 包含舒缓的背景音乐
* 视频具有高能量的电子节拍
* 音频是背景中播放歌曲的低沉的收音机广播

### 时间事件

你可以提示在视频的特定时间发生事情，不需要精确的语法，你可以使用自然语言。这在创建你自己的场景剪辑、节奏或快速连续序列时特别有用。以下是一些示例：

* 3秒后，一名女性进入场景。
* 在5秒时，背景音频开始播放副歌。
* 每2秒切换到一个新画面。
* 在快速连续序列中，每半秒（24fps的12帧）切换到新的场景。

你也可以使用时间码语法：

```
[0-3s] 一个人正在行走
[3-6s] 他们停下并转身
[6-10s] 他们开始跑步
```

### 元提示

你可以要求Gemini Omni Flash关注视频生成的整体质量或原则：

* 考虑微观细节、表情和时机，以创建一个非常丰富、详细但完全自然的场景。
* 在角色和环境描述中极其详细。将服装设计原则应用于角色。对场景中的人、物品和对象非常具体。
* 在背景元素中包含大量适当的细节，使场景感觉真实自然。
* 制作一个快速连续的视频，每1秒展示一个不同的稀有 `[事物]`，欢快的音乐，包括文本来标记这个事物。

### 视频中的文本

你可以提示在视频中包含文本，Gemini Omni将以正确且可读的方式渲染。如果你的视频中有自然出现的文本，即使是在背景元素中，它也有助于定义它应该说什么。

* 屏幕上一次出现一个单词：“did, you, know, that, Omni, can, do, awesome, text?” 每个单词出现1秒，并使用不同的动画风格。没有对话。
* 有一块路牌写着：“这是由Omni生成的AI”，有一家店铺写着：“你需要AI”，还有一辆车牌为：“OMNI1.1”的车。

### 用于扩展视频的提示

使用Gemini Omni 1.1 Flash，你可以通过提示如`“扩展此视频”`或`“场景继续”`来扩展视频。你可以通过10秒扩展视频，最长可达40秒。

Omni通过使用你原始视频的最后10秒作为上下文来创建扩展，以保持视频、动作、角色和音频的一致性。你输入视频的最后一帧将被编辑，以使过渡无缝。

> [!提示]
> **使用参考扩展视频**：视频扩展可以通过提示（例如，`“扩展此视频”`，`“场景继续”`）完成，而无需设置API的`task="extend"`参数。省略`task`参数允许在视频扩展期间传递参考图像（`--image`）和参考视频（`--video-reference`），以将新角色、对象或风格无缝地引入扩展场景。如果显式设置`task="extend"`，则无法传递多模态参考。

扩展时，本指南中的所有Omni提示技巧仍然适用：

* 描述你扩展场景中的音频，特别是如果你需要它改变，`“音乐继续进入副歌”`
* 描述场景是否继续，或者是否有镜头切换到新场景（也许使用相同的人物），`“显示下一个场景中的相同人物”`
* 扩展时包含图像和视频作为参考，以帮助保持你的输出准确，或引入新角色，`“参考图像中显示的人进入场景”`，`“参考视频中的狗<VIDEO_REF_0>跳到沙发上”`
* 如果使用时间戳或时间码语法，0s指的是扩展视频部分的开始。如果你扩展一个10秒的视频，这个提示中的场景切换将在12秒后发生：`“2秒后切换到具有相同人物的新场景”`

### 视频扩展限制和指南

* **时长限制**：用于扩展的上传视频必须为10秒或更短（除非使用多轮）。
* **上传视频中的对话**：目前，你不能扩展一个有人说话的上传视频以添加额外对话（如果角色保持沉默或提示不添加对话则支持）。
* **多轮语音扩展**：在通过多轮（`previous_interaction_id`）扩展先前生成的视频时，生成语音对话或语音受支持。
* **任务参数建议**：我们建议主要依赖提示，仅在提示单独使用不起作用时使用`task="extend"`参数，以帮助模型理解它应该使用的模式，因为设置`task`字段会添加限制（例如禁用多模态参考输入）。

### 使用标签在提示中设置图像和视频角色

你可以使用标签将上传的媒体绑定到特定的生成角色。这让你可以指定每个图像或视频是起始帧、最终帧还是参考。

#### 简单标签（推荐）

对于媒体角色从提示中就很明确的简单情况，你可以直接将图像和视频绑定到角色：

* **`<FIRST_FRAME>`**：将图像用作视频的起始帧，例如：`<FIRST_FRAME> 一名女性正在行走`
* **`<LAST_FRAME>`**：将图像用作视频的最终帧以进行过渡。必须与`<FIRST_FRAME>`一起使用，例如：`<FIRST_FRAME> <LAST_FRAME> 一名女性正在行走`
* **`<IMAGE_REF_N>`**：将图像用作参考，例如：`在<IMAGE_REF_0>风格的背景下，一名女性<IMAGE_REF_1>正在行走`（结合了第一张图像的风格参考和第二张图像的主题参考）。图像参考从0开始。
* **`<VIDEO_REF_N>`**：将视频用作角色或对象参考，例如：`<VIDEO_REF_0>中的人正在拉小提琴`。视频参考也从0开始。

> [!注意]
> **参考视频指南**：
> * **时长**：理想的参考视频是**~3秒**，虽然更长的视频也可以。如果你想要将更长的源文件修剪到参考长度，可以使用`prep_video.py --duration 3`。
> * **数量**：最多**3个参考视频**是理想的，虽然也可以使用更多。

以下是一个包含6个参考图像的示例：

```
[0-3s] 一个工作室时尚序列。从<IMAGE_REF_0>中的女性开始，她正在拿着<IMAGE_REF_1>
[3-6s] 然后我们看到<IMAGE_REF_2>中的男性拿着<IMAGE_REF_3>
[6-10s] 最后是另一个<IMAGE_REF_4>中的女性，她正在拿着<IMAGE_REF_5>边走边走。
```

#### 声明来源和参考

对于具有多个媒体输入和多个角色的更复杂的情况，你可以使用明确的前缀标签与自然语言说明配对。你应该在提示的开头声明这些来源和参考。

  * `[# Sources <FIRST_FRAME>@Image1]` 将使用第一张图像作为起始帧。
  * `[# Sources <FIRST_FRAME>@Image1 <LAST_FRAME>@Image2]` 将使用第一张图像作为起始帧，第二张图像作为最终帧。
  * `[# Sources <FIRST_FRAME>@Image1 <LAST_FRAME>@Image1]` 将使用第一张图像作为起始帧和最终帧，创建一个循环的视频。
  * `[# Sources <FIRST_FRAME>@Image1] [# References <IMAGE_REF_0>@Image2]` 将使用第一张图像作为起始帧，第二张图像作为参考。
  * `[# Sources <VIDEO_0>@Video1]` 将使用视频作为主要源视频进行编辑或修改。
  * `[# Sources <PREVIOUS_VIDEO>@Video1]` 将使用上一轮的视频来扩展。
  * `[# References <IMAGE_REF_0>@Image1]` 将使用第一张图像作为参考。
  * `[# References <IMAGE_REF_1>@Image2]` 将使用第二张图像作为参考。
  * `[# References <IMAGE_REF_0>@Image1 <IMAGE_REF_1>@Image2]` 将使用两张图像作为参考。
  * `[# References <VIDEO_REF_0>@Video1]` 将使用第一段视频作为参考。
  * `[# References <IMAGE_REF_0>@Image1 <VIDEO_REF_0>@Video1]` 将使用图像和视频作为参考。

在提示的末尾添加指导说明：

  * 对于起始帧：`“使用此图像作为起始帧。”`
  * 对于通过起始和结束帧创建的循环视频：`“使用此图像作为第一帧和最后一帧。”`
  * 对于参考图像：`“使用给定的图像作为视频生成的参考。图像不应作为字面意义上的初始帧使用。”`
  * 对于参考视频：`“使用给定的视频作为参考。不要将它们用作视频编辑的来源。”`

一些包含来源和参考声明的提示示例：

```
[# Sources <FIRST_FRAME>@Image1] [# References <IMAGE_REF_0>@Image2] 一名女性<IMAGE_REF_0>正在行走。使用Image1作为起始帧。使用Image2作为视频生成的参考。
```

```
[# References <IMAGE_REF_0>@Image1 <VIDEO_REF_0>@Video1] <VIDEO_REF_0>中的女性正在拉小提琴，显示在<IMAGE_REF_0>中。使用Video1作为角色参考，Image1作为对象参考。
```
