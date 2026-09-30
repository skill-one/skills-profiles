---
name: baseball-trend
description: 当用户请求棒球相关内容或符合以下示例的任务时，请使用此功能：生成一段病毒式传播的虚假“ESPN本垒后方特写镜头”——模拟广播风格的静态画面，并附加一段15秒的Kling-omni动态片段，其中包含两位解说的原声解说，并明确提及用户的姓名。固定主题：扬基队对垒红袜队的美职联冠军系列赛（ALCS）第三场，比赛地点为芬威球场，视角为贵宾席，画面中包含显示用户姓名的比分板和下滚字幕。触发关键词：“让我出现在本垒后方特写镜头里”、“伪造一段有我的MLB广播”、“AI生成的ESPN棒球观众镜头”、“病毒式MLB广播趋势”、“让我出现在扬基对红袜的特写镜头里”。需要提供用户的姓名及一张参考照片。
---

# baseball-trend

15秒ESPN风格的广播剪辑，展示用户坐在假洋基队对阵红袜队的ALCS第3场比赛的芬威球场主垒后方，两位解说员在广播中称呼他们。

固定配方技能——以下提示已校准。替换用户名并保持标记的锚点完整。

## 成本透明门

在支付任何MCP调用之前，调用一次 `identity_balance({verbose: true})`。显示当前余额、近期消耗率和剩余运行时间，然后用以下确切消息锁定运行：

> 预计成本：约3,000-5,500积分（~$30-$55）用于GPT-image-2广播静态图像，一个或两个Kling v3-omni pro 15秒渲染（包含一个带有更改负载的步骤2纠正重试），以及飞行后analyze_media QA。这超过$5，所以回复 `proceed` 继续或 `cancel` 停止。

在用户回复 `proceed` 之前，不要调用任何付费MCP工具。如果用户回复 `cancel`，则不生成。这是唯一的“是/否”门；在 `proceed` 之后，管道端到端运行。

## 语音选择说明

此技能使用Kling-omni的原生广播评论：两位男性解说员，匹配MLB广播惯例。`identity_voice` 设置不被消耗，因为此固定配方不使用代理端TTS或自定义语音ID。

如果用户想要女性编码的解说员或任何自定义语音，baseball-trend是错误的技能。将他们路由到 `/pika:podcast` 并使用棒球框架，它具有代理端语音路径并可以尊重明确的语音选择。

## 阶段 0 — 摄入

如果使用空参数且没有可用的先验上下文，则打印此菜单并停止：

> **谁应该在假MLB广播剪辑中出现？** 必须提供：
>
> - **姓名** — 恰好如其在 chyron 和解说员对话中显示
> - **参考照片** — 一张正面或3/4肖像，本地路径或HTTPS URL

如果只缺少一个字段，则只询问该字段。否则，一次一个地询问以下两个问题。

**1. 用户名** *(必需)* — 用于广播 chyron 和解说员评论中，例如 `"Jane Doe"`。保存为 `state.username`。这替换了提示中每个字面量 `${username}`。

**2. 参考图像** *(必需)* — 一张正面3/4肖像，光线良好，一张脸。解析为CDN URL并保存为 `state.reference_image_url`：

- **`https://…` URL** → 保持原样使用。
- **本地路径** → 使用 `upload_asset` 上传文件，然后使用返回的公共URL。
- **Claude Desktop，照片内联粘贴** → 内联粘贴尚未到达MCP工具（Anthropic限制）。回复：

  > 注意——粘贴的图像在Claude Desktop上尚未到达MCP工具。两个选项：
  > - **粘贴URL** 如果它已经在某个地方托管——最快。
  > - **附加图像文件** 让我可以在上传之前使用它。

  当本地文件到达时：使用 `upload_asset` 将其转换为公共URL，并使用 `public_url`。

回答两个问题后，运行成本透明门，然后回显一条简短的确认信息（“正在生成主垒后方剪辑，用户为 **{username}**…”），然后开始管道。**成本门之后不再有“是/否”门** — 管道端到端运行。

### 阶段 0.5 — 参考图像的Avatar-type探测

在任何付费 `generate_image_edit` 或 `generate_reference_video` 调用之前，在 `state.reference_image_url` 上运行此Avatar-type探测。baseball-trend配方将主题变成假广播嘉宾，因此基于IP的化身和名人/公众人物参考特别可能无法通过审核。

调用一次 `analyze_media`：

```
query: "对付费视频生成进行分类。这是一张真实人脸的照片，AI生成的逼真肖像，风格化/插画角色，还是像蝙蝠侠、皮卡丘或米奇这样的可识别的商标/版权角色？仅返回严格的JSON：{ \"avatar_type\": \"real_human\" | \"ai_realistic\" | \"stylized_illustrated\" | \"recognized_ip\", \"recognized_character\": string | null, \"moderation_risk\": \"low\" | \"medium\" | \"high\", \"recommendation\": \"proceed\" | \"warn\" | \"reject\" }。当没有特定角色被识别时，使用null for `recognized_character`；在`moderation_risk`字段中永远不要写 \"none\"、\"unknown\" 或解释性文字。"
```

根据结果路由：
- **已识别的IP / 版权风险** -> **仅在** `avatar_type` 为 `"recognized_ip"`，或 `recognized_character` 称呼特定角色（例如 `"Batman"`），或当 `moderation_risk` 为 `"high"` 且 `recommendation` 为 `"reject"` 时停止。将 `recognized_character: null`、空字符串、`"none"`、`"unknown"`、`"n/a"` 和低/中 `moderation_risk` 视为单独不足以停止。在此检查之前运行此检查。即使 `avatar_type` 为风格化/插画，chibi蝙蝠侠仍然是蝙蝠侠。
- **真实人类 / AI生成的逼真** -> 正常进行。
- **风格化/插画** -> 带可见警告进行，风格化化身可能会降低相似度质量，并且可能会被图像/视频审核阻止。
- **商标/版权** -> **在生成前停止**。显示此确切用户界面消息：`您的身份化身似乎是一个商标化角色（[X]）。大多数视频提供商会审核并拒绝生成。传递 --avatar <真实照片URL> 来覆盖，或在 pika.me 首先更新您的身份化身。` 对于此技能，如果用户没有传递 `--avatar <真实照片URL>` 风格的覆盖，请要求用户提供替换的参考照片URL或路径。

## 管道

两个Pika MCP阶段，顺序执行。主要引擎锁定：`gpt-image-2` 用于静态图像，`kling-v3-omni` 用于视频。静态阶段唯一的回退是在OpenAI拒绝广播静态图像并返回 `moderation_blocked` 时的 `seedream` 过程。

## 长任务_status轮询

当任何长时间运行的生成调用返回带有或没有 `task_id` 的 `status`（包括 `{task_id}`、`{task_id, status: "queued"}` 或初始 `queued`、`running` 或 `processing` 状态），立即记录任务ID和开始时间。

- 在状态为 `queued`、`running` 或 `processing` 时，每60秒调用一次 `task_status({task_id})`，直到终端（`completed | failed | cancelled`）。不要手动睡眠和不要使用Bash轮询；工作进程保持每个状态调用打开。
- 在 `completed` 时，解开返回的结果URL并继续。
- 在 `failed` 或 `cancelled` 时，向用户显示失败，包括 `task_id`、状态和最后的状态消息。
- 在原始提交15分钟后，如果任务仍然非终端，调用 `task_cancel({task_id})`，然后向用户显示失败。如果取消报告任务已经终端，再次调用状态一次并报告终端结果。
- 在原始任务仍然为 `queued`、`running` 或 `processing` 时，不要提交重复请求。

### 步骤 1 — 广播静态图像 (`generate_image_edit`)

 chyron + scorebug 在帧0（承重 — 当Kling被要求在剪辑中途“弹出”chyron时，它在第4-5秒出现，有可见的闪烁并破坏趋势；将其烘焙到第一帧使Kling将其视为像素锁定烧入的UI）。

使用以下参数调用 `generate_image_edit`：

- `provider`: `gpt-image-2`
- `images`: `[state.reference_image_url]`
- `aspect_ratio`: `16:9`
- `quality`: `medium`（默认速度；`high` 现在已公开，但 ~2分钟/调用 — 仅在保真度重要时使用）
- `output_format`: `png`
- `prompt`（逐字，`${username}` 替换）：

```
来自ESPN的现场MLB游戏电视广播的截图。摄像机切换到观众——我们的参考图像人物，坐在芬威球场主垒后方的高级场级别座位上，自然微笑，不知道自己正在被拍摄。硬锁：不要改变他们的面部结构并保持他们的相似度。主题必须与参考人物匹配。

图像看起来就像真实的电视截图——广播色彩分级、轻微的压缩伪影、交错颗粒、广角广播摄像机感觉。这是纽约洋基队对阵波士顿红袜队，MLB美国联盟冠军系列赛（ALCS），第3场比赛，波士顿主场（芬威球场）。洋基队在ALCS到目前为止以2-0领先。

关键——必须在图像中显示的广播图形：
1. 一个真实的ESPN风格底部scorebug，显示洋基队对阵红袜队，带有球队标志、局数、出局、球/球数计数和得分（带有一个小跑者基地菱形），看起来像真实的现场广播scorebug。
2. 直接在scorebug上方，一个干净的广播风格下三分之二姓名图形/ chyron，恰好读取：`${username}` — 使用经典的ESPN无衬线字体，使用网络的颜色处理。chyron位于左下区域，在scorebug上方，像真实的广播标识符，用于现场嘉宾。
3. ESPN网络标志水印在一个角落。

所有三个图形必须看起来像真实的烧入广播UI——不是Photoshop叠加层。16:9宽高比。
```

将返回的URL保存为 `state.broadcast_still_url`。

重试预算：步骤1静态图像生成最多获得3次总尝试，包括主要静态图像、自我检查重试、无效图像重试、`quality` 降级和下面的一个 `seedream` 回退。在每次付费静态调用之前跟踪 `state.step1_attempt_count`。

**OpenAI审核回退**：如果步骤1的 `gpt-image-2` 调用返回 `moderation_blocked`，将其视为“真实人物 + ESPN品牌实时源 + 真实MLB球队背景”的已知政策表面。不要保持重新滚动相同的OpenAI调用。尝试一次 `seedream`，使用相同的 `images`、`aspect_ratio` 和提示文本，省略 `quality` 和 `output_format`，因为这些是 `gpt-image-2` 仅有的字段。

- 如果 `seedream` 成功，将那个URL保存为 `state.broadcast_still_url`，设置 `state.broadcast_still_provider = "seedream_fallback"`，然后继续到自我检查下面。回退是一次性的：不要再次调用 `gpt-image-2`，不要在此次运行中调用 `seedream` 第二次。
- 如果 `seedream` 也失败或返回政策/安全块，停止并显示此确切用户界面消息：

  > OpenAI拒绝了此图像。尝试使用一个新鲜的AI生成的头像而不是个人照片，或者选择一个非MLB体育变体。

**在步骤2之前的代理端自我检查**：chyron必须正确拼写用户名，scorebug必须看起来像真实的广播UI。如果主要 `gpt-image-2` 静态图像后两者看起来不对，则在步骤1的尝试剩余时，重新滚动步骤1一次（下游所有像素都锁定到这个帧）。如果 `state.broadcast_still_provider = "seedream_fallback"` 后两者看起来不对，则不要重新滚动步骤1；停止并使用上面的相同消息要求用户提供一个新鲜的AI生成的头像或一个非MLB体育变体。这是代理自己的检查——除非已经失败的回退路径通过QA，否则不要询问用户。在任一限制用尽后，停止并要求提供更好的参考照片或允许交付最佳尝试；包括最佳静态/视频URL和失败的检查。

### 步骤 2 — 15秒广播视频 (`generate_reference_video`)

`image_types: ["first_frame"]` 将 `state.broadcast_still_url` 锁定为Kling的精确帧0，保持chyron + scorebug在整个15秒内像素静态。

使用以下参数调用 `generate_reference_video`：

- `provider`: `kling`
- `kling_model`: `kling-v3-omni`
- `duration`: `15`
- `aspect_ratio`: `16:9`
- `quality_mode`: `pro`
- `reference_images`: `[state.broadcast_still_url]`
- `image_types`: `["first_frame"]`
- `sound`: `true`
- `prompt_adherence`: `strict` *(承重 — 没有它，scorebug会动画，身份会在剪辑后期漂移)*
- `negative_prompt` *(逐字，承重 — 没有这些条目，Kling偶尔会变形scorebug或淡出chyron)*：

```
场景切换，摄像机角度改变，scorebug动画，chyron弹出，chyron淡入，chyron文本更改，图形动画，夸张表演，直接对准摄像机，模糊的脸，身份漂移，扭曲的解剖
单个解说员，一个解说员，单一叙述者，解说员独白
```

- `prompt`（逐字，`${username}` 在所有地方替换；预修剪以适应Kling的2500字符限制；在顶部锁定帧0的chyron）：

```
第一帧是提供的参考图像。ESPN scorebug 和 "${username}" 下三分之二 chyron 已经在帧0上屏幕——保持可见，不变，跨所有15秒像素锁定。不要动画它们，不要改变它们的文本。

真实的MLB现场广播剪辑，主题坐在洋基队对阵红袜队ALCS第3场在芬威球场主垒后方的高级场级别座位上。感觉就像广播摄像机在局间发现了一个值得注意的嘉宾。

主题保持坐着，自然微笑，不夸张，不锁定在眼神交流上。偶尔看向球场，然后看向摄像机，然后回到球场。一个连续的拍摄。没有剪辑。没有角度变化。

行动时间线：
0-4s：在摄像机落在他身上时，在座位上自然地微笑；自然地环顾四周，没有注意摄像机。
4-7s：放松自然地向摄像机挥手（当第一次挥手时，观众欢呼）；抬头看头顶的Jumbotron，然后回到摄像机。
7-11s：简要欢呼，表现出明显的兴奋，对季后赛氛围做出反应；转向左边的朋友，交换话语，笑（我们听不到他说的话）。
11-15s：自然地微笑时鼓掌。

保持所有动作微妙、可信、人性化。没有夸张的表演。没有直接对准摄像机说话。

广播风格：现场体育电视外观，广角广播摄像机，自然球场照明，轻微的压缩/交错颗粒，真实的观众运动，逼真的场级别构图。

音频：两个不同的男性声音，不是一个单一叙述者。解说员A是比赛解说；解说员B是彩色评论员。自然广播手交接A/B行，以便两个声音都清晰听到：
解说员A：`${username} 今晚在芬威，观看这场巨大的季后赛对决。`
解说员B：`你可以看到他在主垒后方享受第3场比赛。`
解说员A：`今晚气氛很好。`
解说员B：`${username} 正在得到观众的很多喜爱。`
解说员是离屏的；主题不会对口型或对准摄像机说话。

约束：强烈保留身份。始终坐在主垒后方。不要与摄像机保持眼神交流。不要对准摄像机说话。不要夸张手势。不要场景剪辑。scorebug + chyron在任何时候都不改变。真实的MLB电视广播观众剪辑感觉。
```

将返回的视频URL保存为 `state.broadcast_video_url`。如果生成完成异步，则遵循MCP工具返回的状态处理程序，直到视频达到终端状态。

步骤2 Kling视频生成最多获得2次总尝试（初始渲染 + 一个纠正重试，用于漂移、scorebug/chyron运动或解说员误读）。kling-v3-omni没有种子，相同的Kling负载可以解析为相同的作业/资产。不要提交相同的Kling负载只是为了寻求变化。在纠正重试之前，通过使用更新的 `state.broadcast_still_url`、恢复缺失的严格参数/ `negative_prompt` 条目或缩短/澄清A/B解说员块来实质性更改负载。跟踪 `state.step2_attempt_count`。在任一限制用尽后，停止并要求提供更好的参考照片或允许交付最佳尝试；包括最佳静态/视频URL和失败的检查。

### 步骤 3 — 交付

返回两个Pika CDN URL：静态图像URL和最终视频URL。如果主机客户端需要本地媒体标记，请在确认两个CDN URL都可访问后在此技能之外创建本地预览。

单行摘要：*"为 {username} 制作的本垒板后切出画面 — 15秒，16:9，1080p，Kling v3-omni，原生双解说员评论。"*  

## 飞行后质量门禁

在宣布成功之前，对 `state.broadcast_video_url` 调用 `analyze_media` 并请求结构化判断：

```
仅返回 JSON：{
  "verdict": "clean" | "degraded" | "catastrophic",
  "announcer_count": 0 | 1 | 2,
  "observations": string[],
  "audio_warning": string | null,
  "quality_warning": string | null,
  "re_roll_suggestion": string | null
}
检查 chyron 仍显示准确的用户名，主体的身份在整个过程中保持稳定，比分虫保持稳定，最终片段没有黑帧或错误体育场景，音频包含两个不同的男性解说员声音 — 不仅仅是单一叙述者。
```

- 如果 `announcer_count < 2`，将结果视为至少 `degraded`，包含 `audio_warning`，并在更改 A/B 音频负载后仅使用步骤 2 的纠正重试。不要提交相同的 Kling 负载。
- 如果 `verdict` 为 `clean`，正常返回静态 URL 和最终视频 URL。
- 如果 `verdict` 为 `degraded`，返回 URL 以及 `quality_warning` 和 `audio_warning`，以便用户在发布前进行审查。
- 如果 `verdict` 为 `catastrophic`，不要调用运行完成；而是显示判断和 `re_roll_suggestion`，而不是宣布成功。

## 承重短语（不要移除这些）

这些是经验行为依赖关系，而非写作风格 — 移除它们会破坏配方：

- 在 **静态提示** 中：`Hardlock: 不要改变他们的面部结构并保持他们的相似度` + `主体必须与参考人物匹配`（没有这些，身份在第一帧上会漂移，下游所有内容都会继承漂移）。
- 在 **视频提示** 中：`强烈保留身份` + `ESPN 比分虫和 "${username}" 下三分 chyron 在帧 0 时已经显示在屏幕上 — 保持可见、未更改、像素锁定`（没有这些，Kling 在片段中途重新动画 chyron）。
- 完整的 **negative_prompt** 列表 — 列表中的每个条目都来自先前运行中的特定失败模式。
- `prompt_adherence: "strict"` 和 `image_types: ["first_frame"]` — 见上述内联注释。

## 引擎选择：仅 Kling（有一个例外）

Seedance 有一个在重复 NBA 兄弟运行中观察到的两阶段 `partner_validation_failed` 422 门禁：

- **输入端** (`body.image_urls`)：如果参考包含可识别的真实人物，则拒绝。
- **输出端** (`body.generated_video`)：生成后拒绝，如果生成的片段包含可识别的面孔 — 并且每个广播切出画面都有满是面孔的观众。

输出端门禁对于这种趋势无论如何都不可避免，因此 Seedance 在这里实际上无法使用。Kling 是适用于普通用户照片的引擎。

**Kling 例外 — 可识别的名人也会被阻止。** Kling 有自己的内容审核门禁，会在名人参考上触发。名人参考提示加上匹配的广播 chyron 可能会在提交时失败，`task_status: failed, task_status_msg: "未能通过风险控制系统"`。这是正确的行为 — 趋势错觉只有在非公众人物参考中才有效，其中 chyron 名称 + 面孔是连贯的。如果用户提供名人照片，向他们显示门禁并要求提供非名人参考。

**Kling 交易**：2500 字符 `prompt` 限制（上述配方已预修剪）。kling-v3-omni 没有种子；相同的 Kling 负载可能会折叠到同一作业/资产，因此纠正重试必须实质性地改变第一帧静态、提示、negative_prompt 或音频措辞。不要提交相同的 Kling 负载以进行变化。

## 运行预期

典型运行时间为 4-7 分钟：

| 步骤 | 墙上时钟 | 备注 |
|---|---:|---|
| 参考上传 | 5-30s | 用户提供 HTTPS 时跳过 |
| 广播静态 | 60-120s | 如果 chyron 或比分虫错误，在视频之前重新录制，受步骤 1 重试预算限制 |
| Kling 视频 | 3-5 min | 一个 15 秒的专业渲染，带原生评论 |
| 交付检查 | <30s | 验证最终 URL 和明显的身份/chyron 连续性 |

## 失败模式

| 症状 | 原因 | 修复 |
|---|---|---|
| chyron 在片段中途弹出（约 4-5 秒闪烁） | chyron 未嵌入静态 | 在步骤 1 重试预算内重新运行步骤 1；在步骤 2 之前验证 `state.broadcast_still_url` 中 chyron 是否可见 |
| 比分虫在片段中途动画/变形 | `prompt_adherence` 不是 `strict`，或 `negative_prompt` 被修剪 | 恢复严格遵循和完整的 negative_prompt |
| 片段后期身份漂移（约 10 秒后脸部变化） | 参考图像太小 / Kling 丢失脸部 | 仅在实质性地更改负载后使用一次步骤 2 纠正重试，通常通过在步骤 1 预算剩余的情况下重新运行步骤 1 并对静态进行更紧密的脸部裁剪 |
| 只听到一个解说员声音 | Kling 将 A/B 评论合并为一个原生叙述者 | 在一次步骤 2 纠正重试之前缩短或澄清 A/B 解说员行；在用尽上限后，显示音频警告并询问是否交付最佳尝试 |
| 解说员误读用户名 | 原生音频是单次录制 | 在一次步骤 2 纠正重试之前添加发音提示或缩短解说员行；否则显示音频警告 |
| OpenAI `moderation_blocked` 在步骤 1 | `gpt-image-2` 安全门禁在真实人物 + ESPN 品牌直播源 + 真实 MLB 球队上下文 | 在步骤 1 预算剩余的情况下，尝试一次 `seedream` 并使用相同的参考图像和提示。如果它也阻止，告诉用户："OpenAI 拒绝了这张图片。尝试使用新鲜的人工智能生成的头像而不是个人照片，或者选择一个非 MLB 体育变体。" |
| Seedance `partner_validation_failed` 422 | 尝试使用 Seedance 而不是 Kling | 仅使用 Kling — 见引擎选择部分 |
| Kling `task_status: failed` with `task_status_msg: "未能通过风险控制系统"` | 参考照片是可识别的名人/公众人物 | 向用户请求非名人参考。Kling 正确阻止模仿模式（名人面孔 + 虚假事件 chyron） |
| `generate_image_edit` 400 `invalid_image_file` from `openai v1/images/edits` | 参考是 iPhone HEIC 衍生的 JPEG，带有沉重的 EXIF 和/或极端宽高比（例如 2316×3088） | 在上传前重新编码参考：`convert in.jpg -strip -auto-orient -resize 1536x1536\> out.png`，然后上传清理后的 PNG |
| `quality: "high"` 运行感觉缓慢（约 2 分钟/调用） | gpt-image-2 高是故意较慢的保真度层级，不是错误 — 上游典型值约为每分钟两分钟，如清单所示 | 耐心等待 — 大多数运行正常返回。如果特定运行失败，在步骤 1 重试预算内重试一次；仅在持续存在时才回退到 `quality: "medium"` |

## 不要做的事情

- 不要进行体育交换。NBA / NFL / 足球变体 → 分叉这个技能；不要参数化这个。
- 不要在 chyron 后添加后缀（例如 " - AI Creator"）。Chyron 仅是用户名 — 趋势错觉取决于它看起来像真实的广播标识符。
- 不要添加后期编辑 — 没有 `add_captions`，`generate_music`，`edit_*`。Kling 直接烧录比分虫 + chyron + 原生评论；任何后续添加的内容都会破坏广播错觉。
