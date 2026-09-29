---
name: faceless-explainer
description: 将任意文本——文章、笔记、主题、简短内容——转化为无具体形象的解说视频：无需捕捉网站或素材，因此每场画面都是根据场景创作（字体排版、抽象图形、图表、数据可视化）。适用于主题解说、概念拆解、操作指南、清单类内容。非基于网站构建的视频（/产品发布视频——促销或导览）。不明确时→/超帧。
---

**插件安装：** 在设置或新鲜命令之前，当此技能位于 HyperFrames 插件内时，请遵循 [插件执行规则](../hyperframes/references/plugin-installation.md)。独立安装则保留以下更新说明。

> **首先，保持此技能新鲜——在运行前与用户确认：** `npx hyperframes skills update faceless-explainer`。当一切都是最新时，这是一个快速的无操作；否则，它将在您依赖它们之前刷新此技能及其依赖的核心域技能。

> **media-use**：在获取音频/图像/标志之前，调用 `/media-use` 从 HeyGen 目录解析 BGM/SFX/图像，并从其官方来源获取品牌标志。首先运行 `--adopt` 以注册现有资源。参见 `/media-use` 技能。

# 无脸解说员到 HyperFrames

使用此技能将文本内容转换为解说视频：选择设计系统，规划教学故事，并在 HyperFrames 中逐帧构建。**无脸**意味着所有视觉都是在下游创作的——没有捕获步骤，也没有真实的资产清单。

> **正门是 `/hyperframes`。** 您是协调者。运行每个步骤，验证其门控，然后才能继续。此技能用于从文本解释主题，没有产品和网站需要捕获。任何其他意图，一个简单的“制作视频”，或任何不确定性 → 首先阅读 `/hyperframes` — 意图层拥有每条路线的决策，一个没有 `BRIEF.md` 的新创建到达这里仍然会通过它（设置的开启规则）。

您是协调者。在 `videos/<project>/` 中工作。按顺序运行步骤，并在继续之前通过每个门控。用户门控步骤是步骤 0、步骤 3 和步骤 6。在步骤 0 之前阅读 `../hyperframes/references/brief-contract.md` — 它定义了门控类型以及 `BRIEF.md` 的 `flow`/`storyboard` 如何导出控制步骤 3/4/6 门控的模式。除了步骤 5，您自己完成所有步骤，在步骤 5 中，您为每帧派遣一个子代理。不要在这里放置设计或运动规则；那些存在于帧工作子代理、此技能的本地 `../hyperframes-animation/rules/` + `../hyperframes-animation/blueprints/` 和 `hyperframes-creative`。

工作流程：步骤 0 设置 → `hyperframes.json`；步骤 1 简报 → `capture/extracted/`；步骤 2 设计系统 → `frame.md`；步骤 3 故事板/脚本 → `STORYBOARD.md` 和 `SCRIPT.md`；步骤 3.1 音频 → `audio_meta.json`；步骤 4 视觉设计 → 丰富 `STORYBOARD.md`；步骤 5 帧→ `compositions/frames/NN-*.html` 和 `index.html`；步骤 6 最终渲染 → `renders/video.mp4`。

---

## 步骤 0：设置

目标：带确认的简报进入，创建 HyperFrames 项目，并使简报持久化。

**简报由意图层确认，而不是在此处提出问题。** 开启规则，按顺序：**(1)** `BRIEF.md` 存在 → 读取它并不要提问——简报已确定，其 `flow`/`storyboard` 导出模式（简报合同 § 1）。**(2)** 没有 `BRIEF.md` 但项目存在（`hyperframes.json` / 磁盘上的 `STORYBOARD.md`）→ 从故事板的 frontmatter 和记录的偏好中恢复；永远不要重新审问一个半建成的项目。**(3)** 都没有——一个直接到达此处的全新创建请求 → 阅读 `/hyperframes` 并运行其意图层（`references/intent-interview.md`）：它检查配方和记忆的默认值，进行此路线的问题（`../hyperframes/references/routes/faceless-explainer.md`），并返回锁定简报。编辑请求跳过所有这些——去进行编辑。

如果 `hyperframes.json` 缺失，则仅初始化。从主题中命名 `<project>`，例如 `compound-interest-explained`；永远不要使用工作区名称或时间戳。

`npx hyperframes init "videos/<project>" --non-interactive --example=blank --skill=faceless-explainer` — `init` 检查已安装的技能与 GitHub 上的最新版本，如果任何技能过时，则更新全局集。

初始化后，让 `<PROJECT_ROOT>` 为 `videos/<project>`，并运行后续所有相对路径命令时将其作为工作目录。在以下命令中，`.` 表示 `<PROJECT_ROOT>`；永远不要在调用目录中写入 `.media`、`capture` 或输出文件。

**立即在初始化后编写 `BRIEF.md`**（永远不要在之前——`init` 拒绝非空目录）：意图层的锁定简报，形状按 `../hyperframes/references/brief-format.md`。解析 `<MEDIA_DIR>` 为已安装的 `/media-use` 技能目录。然后使用 `node <MEDIA_DIR>/scripts/prefs.mjs record --hyperframes .` 记录每个偏好支持的答案（`brief-format.md` 命名子集）。如果意图层采用了配方，运行 `node <MEDIA_DIR>/scripts/recipe.mjs use --hyperframes . --name <name>`；它将其 `frame.md` 复制到项目中（然后步骤 2 被跳过），并返回步骤 3 草稿的骨架。配方填充答案，而不是批准；审查门控仍然运行。

**在继续步骤之前显示登录状态** — 运行 `npx hyperframes auth status` 并原封不动地传递其输出。它报告语音/BGM 将使用 HeyGen 还是本地引擎，并且在注销时如何登录。应用一个分支：

- **协作式**：等待用户登录或显式选择 `offline` / `go`。
- **自主式**：声明状态并继续使用可用的本地引擎。

当没有离线提供者时，不要无声地省略所需功能；显示阻止器。不要将此决策折叠到另一个问题中，或写入到每个存储库的 `.env` 中。Auth 所有权和离线回退：`/media-use` `references/setup-providers.md` § 提供者。

**门控**：`hyperframes.json` 和 `BRIEF.md` 存在；偏好支持的答案被记录（简报合同 § 2）；登录状态被显示（已登录，或继续离线）。

---

## 步骤 1：简报（无捕获）

目标：将用户的文本作为信息来源折叠到项目中。这里**没有网站捕获和没有真实资产**——这是一个无脸解说员。

逐字保存用户的完整输入，然后手动创建合成捕获包：

- `capture/extracted/visible-text.txt` — 完整文章 / 笔记 / 主题 / 简报，逐字。这是**信息**来源，而不是故事模板（步骤 3 重新塑造它）。
- `capture/extracted/tokens.json` — `{ "title": "", "description": "", "colors": [], "fonts": [] }`。从简报填充 `title`/`description`。除非用户明确给出了品牌颜色/字体，否则留空 `colors`/`fonts`——然后添加它们（设计预设提供完整的调色板）。

如果用户粘贴了脚本或希望保留他们的措辞，逐字保存为 `user_script.txt`；`VO_MODE`（逐字或重组）来自 `BRIEF.md` — 意图层在脚本到达时询问它。在此处只询问一次，如果简报以某种方式缺少它，并存储答案以供步骤 3 使用。

**不要**运行 `npx hyperframes capture`（没有 URL）。不要创建 `asset-descriptions.md` 或填充 `capture/assets/`——无脸视觉是在步骤 4-5 中创作的，而不是捕获的。一个例外：如果用户提供了一个真实图像，将其放在 `public/<basename>` 下并记下它以供步骤 3 使用。

**门控**：`capture/extracted/visible-text.txt` 和 `capture/extracted/tokens.json` 存在；您可以一句话清晰地说明解说的主题和受众。

---

## 步骤 2：设计系统

目标：选择一个已安装的帧预设；脚本将其转换为此视频的 `frame.md` + 标题皮肤。

当 `BRIEF.md` 命名 `style_preset` — 用户通过意图层的展示挑选了它——使用它；只有当简报是沉默的时，判断才由您做出。然后您只做一次调用——**哪个预设**：阅读 `../hyperframes-creative/references/design-spec.md` 并浏览 `../hyperframes-creative/frame-presets/`；选择最适合主题、语气和受众的预设。然后运行：

```bash
node <SKILL_DIR>/scripts/build-frame.mjs --preset <name> --hyperframes .
```

脚本会确定性地完成其余工作：复制预设的 `FRAME.md` → `frame.md`，并**重新混合**它到 `capture/extracted/tokens.json` 中的任何品牌标记上（品牌颜色映射到预设的颜色键上，预设的显示 + 正文字体被替换为品牌的），复制预设的标题皮肤到 `.hyperframes/caption-skin.html`，并自我验证（在映射损坏时退出 1）。一旦它退出 0 就继续——不要手动编辑规范。

无脸解说员通常**没有品牌颜色/字体**（`tokens.json` 颜色/字体为空）→ 脚本保留预设自己的调色板，一个可发布的完整设计。只有当用户在运行之前将品牌颜色/字体添加到 `tokens.json` 中，并且只有在手动调整 `frame.md` 后如果映射确实需要它。

**门控**：`build-frame.mjs` 退出 0 — 从命名预设存在 `frame.md`，并且（当预设提供时）`.hyperframes/caption-skin.html` 存在作为标题皮肤源；选择的预设被记录为偏好（`--key style_preset --workflow <this workflow>`，简报合同 § 2）。

---

## 步骤 3：故事板和脚本

目标：将文本转换为批准的逐帧教学计划。

阅读 `../hyperframes-creative/references/story-spine.md`（钩语言、证据前价值、故事板作为提案、来源可追溯的视觉）、`references/story-design.md`、`../hyperframes-animation/blueprints-index.md`、`../hyperframes/references/storyboard-format.md` 和 `../hyperframes/references/script-format.md`。使用它们来编写 `STORYBOARD.md`，并在需要旁白时编写 `SCRIPT.md`。从简报的 `length` 设置 frontmatter `duration:` — 一个粗略预期；组装报告在哪里切割它。

使用 `story-design.md` 来编写解说结构（概念 / 如何做 / 列表 / 故事）、钩策略、清晰技术、情感节拍、类型枚举映射和 `VO_MODE`。视频的序列来自**叙事设计，而不是输入文本的段落顺序**——重新排序、合并、省略、压缩。作为**软指南**，参考 `../hyperframes-animation/blueprints-index.md` 中的角色→蓝图菜单：对于每个节拍，根据候选蓝图暗示的形状编写旁白，并在适合时标记该候选 `blueprint:` id。教学真理仍然决定哪些节拍存在——永远不要强迫节拍适合蓝图，也永远不要因为一个被证明的形状可用而发明节拍。无脸视觉是在下游创作的，所以帧**不**携带资产清单：除非用户提供了一个真实的 `public/<basename>` 图像，否则将 `asset_candidates` 留空。使用故事板和脚本参考中的确切所需字段。

起草后，运行审查循环的计划步骤——`../hyperframes/references/review-loop.md` § 1：将计划作为提案提出，并提出两个问题——批准或更改，以及**首先绘制草图**（推荐）或跳过。反馈作为聊天回复到达；循环直到批准。这是一个**检查门控**（简报合同 § 1）：在自主模式下没有要询问的——发布相同的摘要作为提示并继续；草图合并到构建中，并且一个预览问题在步骤 6 来到。

**门控**：`STORYBOARD.md` 存在，每个帧都有所需的叙事字段，当需要旁白时 `SCRIPT.md` 存在，并且用户批准了逐帧计划（自主：摘要被作为提示发布）。

---

## 步骤 3.1：音频

目标：从批准的脚本生成旁白、单词时间、音乐和音频元数据。

在步骤 3 批准后开始音频。在后台运行它，然后继续步骤 4。（登录状态已在步骤 0 显示；引擎会自动回退。）

**从用户在调用之前询问选择旁白声音。** 如果请求命名了声音、性别或语调，选择匹配的声音 id 并将其与 `--voice <id>` 一起传递。管道默认是否则 **Marcia（女性）** 在 HeyGen / `am_michael` 在 Kokoro — 所以像“一个男性声音”这样的请求会被无声忽略，除非您传递标志。声音 id 是提供者特定的；针对步骤 0 的登录状态选择的提供者解析：**HeyGen**（已登录）通过 `node <MEDIA_DIR>/audio/scripts/heygen-tts.mjs --list`（或 `GET /v3/voices?engine=starfish`）；**Kokoro**（离线）通过 `<MEDIA_DIR>/audio/references/tts.md` 中的声音表（前缀 `am_`/`bm_` 男性，`af_`/`bf_` 女性）。当用户没有表达偏好时，在管道默认之前回退到记住的声音（简报合同 § 2），并说明您使用了哪个；仅当两者都没有命名时才省略 `--voice`。当用户在此运行中明确选择了一个声音时，记录它（`prefs.mjs record --key voice`）。

`node <SKILL_DIR>/scripts/audio.mjs --script ./SCRIPT.md --storyboard ./STORYBOARD.md --hyperframes . --out ./audio_meta.json --voice <voice-id> &`

音频脚本处理旁白、单词时间、从 HeyGen 的音乐库获取 BGM，以及时间元数据。BGM 情绪来自故事板的 `music:` 字段。这使用 HeyGen 音频 API 进行检索，而不是生成，并且与 TTS 使用相同的 `~/.heygen` 凭证。有关提供者详细信息，请阅读 `../media-use/audio/references/tts.md`。

如果没有旁白并且没有 `SCRIPT.md`，则跳过声音生成。如果故事板有音乐情绪，BGM 可能仍然运行。

**标准的完全静音标记**（跨重用此音频模型的流程共享）：`STORYBOARD.md` 顶部 YAML 块中的 `music: none` **并且**没有 `SCRIPT.md`。这种组合将项目标记为静音——没有旁白，没有 BGM，没有 SFX。`audio.mjs` 识别它并生成 nothing（它删除任何过时的 `audio_meta.json`；一个缺失的 `audio_meta.json` 是组装视为静音的），所以这个步骤是一个干净的跳过。`music: none` 与旁白一起保留 TTS 并关闭 BGM。使用确切的拼写——不要即兴创作其他标记。

**门控**：音频作业已开始，或者项目被标记为静音（`music: none` + 没有 `SCRIPT.md`）。

**在您创建任何命名视觉元素之前，请先搜索实时目录。** 一个无名的解释者发明了每一个视觉元素，这正是在最有可能对现有模块进行手工重写的时刻。对于每一种外观、效果、处理或过渡，简要中文名称——"CRT扫描线"、"故障"、"胶片颗粒"、"闪烁扫描"、"五彩纸屑爆发"——运行 `npx hyperframes catalog --query "<用普通英语描述的外观>" --json` 并在将这种外观写入 `STORYBOARD.md` 之前阅读顶部结果。此搜索**无需安装任何东西**：无需项目、无需先前的 `add`、无需账户。它从任何目录中排名整个托管注册表（约400个模块和组件）。一个已经完成工作的模块成为帧的 `focal`——在此处命名，以便第5步的工人可以安装和定制它。只有在搜索结果为空时才发明视觉元素。

对于每个帧，根据 `visual-design.md` 的方法，在 `STORYBOARD.md` 中编写一个**带时间编码的拍摄序列**：选择帧的蓝图（或创作），用此帧的**发明**内容实例化它，并调整每个场景的揭示速度以适应旁白，以便帧在其完整持续时间中发展，而不是前加载然后冻结。因为解释者是无名的，`focal`/`roles` 命名**发明的视觉元素**（一个英雄词、一个图表节点、一个数据可视化系列）——您正在设计它们，而不是选择捕获的资产。按场景**内联**声明布局和运动（词汇表在 `visual-design.md` 和 `motion-language.md` 中）。添加一个视频范围的 `## 视频指导` 块。

不要更改故事、脚本、`transition_in` 或源文本。在此步骤中不要编写HTML。没有**资产准备步骤**——无名的视觉元素由第5步的工人构建。如果用户提供了一个真实的 `public/<basename>` 图像，请在相关帧的 `focal`/`roles` 中通过路径引用它；否则无需准备。

**关卡：** 每个帧都有一个带时间编码的拍摄序列，其揭示速度与旁白同步（没有前加载）；每个帧都命名其发明的 `focal` 和/或 `roles`；`## 视频指导` 存在。协作：草图表已确认。

---

## 第5步：构建帧

目标：将每个故事板帧构建为HTML组合，并组装可播放视频。

如果已启动音频，请等待第3.1步音频完成。然后同步持续时间并获取SFX；如果无声，则跳过两者。

`node <SKILL_DIR>/scripts/audio.mjs sync-durations --audio-meta ./audio_meta.json --storyboard ./STORYBOARD.md`

`node <SKILL_DIR>/scripts/audio.mjs fetch-sfx --storyboard ./STORYBOARD.md --hyperframes .`

持续时间同步是机械的：真实旁白持续时间获胜；静音帧保持估计；永远不要手工编辑同步后的持续时间。

在调度之前，阅读 `../hyperframes/references/subagent-dispatch.md`。构建每个帧的数据包和工人角色有效负载：

`node <SKILL_DIR>/scripts/frame-packets.mjs --project "$PROJECT_DIR" --storyboard "$PROJECT_DIR/STORYBOARD.md"`

构建者在每个帧下（`.hyperframes/frame-packets/`）写入一个有界的数据包（帧的精确故事板块 + 蓝图主体 + 每个引用的规则配方，内联）和 `_role.md` (`../hyperframes/references/frame-worker-core.md` + 此技能的 `sub-agents/frame-worker.md`，逐字连接——完整的工人角色）。并行调度每个子代理（如果可能）；否则分波次运行工人。每个工人只得到一个帧：其提示包含 `_role.md` 和该帧的数据包——将两者全部粘贴，或交给工人先读取这两个文件路径（等效；工人从这两个文档开始）——加上调度上下文，包含 `PROJECT_DIR`、`frame_id`、帧是否在磁盘上有**确认的草图**（工人应用该布局而不是重绘它——帧工人核心 § 当存在确认的草图时）、画布大小、字幕状态+如果启用字幕则保留带）。

工人只读取其数据包和 `frame.md`；他们永远不会打开 `STORYBOARD.md` 或技能文档（数据包内联了上游选择的内容）。每个工人只写入 `compositions/frames/NN-*.html`。工人必须永远不要编辑 `STORYBOARD.md`。

**全出血背景骑在 `class="clip"` 层上，永远不会在 `#root` 上。** 帧的地面（颜色字段/渐变/网格）是其自己的全持续时间背景剪辑——在 `#root` / `data-composition-id` 元素上设置的 `background` 被剪辑门控到帧的窗口，并且是不可靠的地面，因此深色内容可能会落在黑色的主机 `body` 上并渲染不可见。视频的基础地面由汇编器从 `frame.md` 的 `canvas` 颜色绘制到索引 `#root`。（完整规则+自我检查：`../hyperframes/references/frame-worker-core.md`。）

每当一个工人返回时，协调器在 `STORYBOARD.md` 中将该帧标记为 `animated`。

在音频时间存在后，在后台构建字幕并组装索引：

`node <SKILL_DIR>/scripts/captions.mjs build --storyboard ./STORYBOARD.md --audio-meta ./audio_meta.json --hyperframes . --out ./caption_groups.json &`

`node <SKILL_DIR>/scripts/assemble-index.mjs --storyboard ./STORYBOARD.md --hyperframes .`

`captions.mjs` 使用项目的 `.hyperframes/caption-skin.html`（在第2步中复制）作为字幕外观，注入来自 `frame.md` 的品牌标记；如果没有皮肤，则渲染内置默认药丸。`captions: skipped (<reason>)` 是有效的。在明确跳过时不要字幕。

**关卡：** 每个帧都被标记为 `animated`（协作：草图表在第4步已确认），`index.html` 存在，并且字幕已构建或明确跳过。

---

## 第6步：最终确认

目标：验证组装的视频，获取用户批准，并渲染最终MP4。

注入过渡，运行检查，暂停以供审查，然后渲染。

`node <SKILL_DIR>/scripts/transitions.mjs inject --storyboard ./STORYBOARD.md --hyperframes .`

`node <SKILL_DIR>/scripts/transitions.mjs verify --storyboard ./STORYBOARD.md --index ./index.html`

`npx hyperframes lint`

`npx hyperframes check`

`npx hyperframes snapshot --at <frame-midpoints>`

`snapshot` 将捕获的帧拼接成一个接触表 (`snapshots/contact-sheet.jpg`)。快速查看它；如果没有什么明显出问题，继续前进——不要在此处停留。

如果命令失败，显示 `stderr` 并停止——不要堆叠恢复命令。自己修复它：对 `compositions/frames/NN-*.html` 进行最安全的编辑，然后重新运行失败的检查。

**已知的误报——不要追查它。** `check` 可能会报告一些 `text_box_overflow` 找到的结果，约1-4px在**字幕**高亮词上（选择器 `#caption-word-*` / `.caption-line`）。字幕药丸使用故意紧凑的 `line-height`（在 `scripts/captions.mjs` 中一次设置）并且**没有 `overflow:hidden`**，因此一个重型显示字形的墨水会溢出几px到药丸自己的填充中——实际上没有剪切。将这些视为预期行为并继续。**不要**增加字幕的 `line-height`（它会使药丸膨胀，这更糟）。只有在 `text_box_overflow` 命名一个**帧**元素（`#el-NN-*`）时才采取行动，而不是字幕词。

检查通过后，暂停以供用户审查——审查循环的最终外观（`../hyperframes/references/review-loop.md` § 4）：一个问题，在最终 Studio 预览上——现在渲染，还是有什么变化？（自主：保留的问题，预览优先还是渲染。）然后交付MP4、接触表和帧ID，以便修订可以针对单个帧。

预览：`npx hyperframes preview --background`

只有在用户批准后（自主模式：在预览或渲染问题之后）才渲染：

`npx hyperframes render --skill=faceless-explainer --quality high --output renders/video.mp4`

渲染后不要重新运行 `lint`、`check` 或 `snapshot`，除非用户要求。

**关卡：** `lint` 和 `check` 通过，并且在渲染前检查了快照；用户在审查暂停时批准（自主：检查通过并且交付包括接触表）；`renders/video.mp4` 存在。最终回复声明MP4路径和最终持续时间。

---

## 快速参考

**格式：** 横屏 `1920x1080`；竖屏 `1080x1920`；方形 `1080x1080`——根据目的地（简要合同 § 2）导出。在故事板frontmatter中一次性设置格式。

**无名的增量与捕获资产工作流：** 没有第1步捕获（合成的 `tokens.json` + `visible-text.txt`）；没有 `asset-descriptions.md` 和没有 `capture/assets/`；第4步中没有资产准备；`asset_candidates` 默认为空；每个视觉元素都是由第5步的工人发明的（字体/抽象图形/图表/数据可视化）。用户提供的 `public/<basename>` 图像是唯一的真实资产路径。

**背景脚本：** 工作流仅在 `scripts/` 下提供这些：`build-frame` 用于采用+品牌混合帧预设到 `frame.md`（+字幕皮肤）；`audio` 用于TTS、转录、BGM、SFX和持续时间同步；`captions`；`transitions` 用于注入和验证；以及 `assemble-index`。其他一切都是 `hyperframes` CLI。

可重用、领域无关的拍摄形状位于 `../hyperframes-animation/blueprints/`（由 `../hyperframes-animation/blueprints-index.md` 索引）。

| 阅读                                                                                                                                                        | 时间                                                                                                     |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| `[../hyperframes/references/brief-contract.md](../hyperframes/references/brief-contract.md)`                                                                | 关卡类型，从 `BRIEF.md` 派生的模式，字段语义。                                                        |
| `[../hyperframes-creative/references/story-spine.md](../hyperframes-creative/references/story-spine.md)`                                                    | 第3步：故事教条——钩子语言、价值先于证据、提案形状、源可追溯的视觉元素。                                |
| `[../hyperframes-creative/frame-presets/](../hyperframes-creative/frame-presets/)`                                                                          | 第2步：选择并采用一个帧预设。                                                                          |
| `[../hyperframes-creative/references/design-spec.md](../hyperframes-creative/references/design-spec.md)`                                                    | 第2步：正确应用品牌标记。                                                                              |
| `[references/story-design.md](references/story-design.md)`                                                                                                  | 第3步：规划解释者的故事。                                                                              |
| `[../hyperframes-animation/blueprints-index.md](../hyperframes-animation/blueprints-index.md)`                                                              | 第3步：角色→蓝图菜单。第4步：选择拍摄形状。                                                            |
| `[../hyperframes/references/storyboard-format.md](../hyperframes/references/storyboard-format.md)`                                                          | 第3步：编写 `STORYBOARD.md`。                                                                          |
| `[../hyperframes/references/script-format.md](../hyperframes/references/script-format.md)`                                                                  | 第3步：编写 `SCRIPT.md`。                                                                               |
| `[../media-use/audio/references/tts.md](../media-use/audio/references/tts.md)`                                                                              | 第3.1步：选择或理解TTS提供者和声音。                                                                  |
| `[references/visual-design.md](references/visual-design.md)`                                                                                                | 第4步：编写帧的拍摄序列（+布局词汇表）。                                                                |
| `[references/motion-language.md](references/motion-language.md)`                                                                                            | 第4步：运动词汇表+运动教条。                                                                          |
| `[references/cut-catalog.md](references/cut-catalog.md)`                                                                                                    | 第4-5步：切割目录（工人构建帧内接缝）。                                                                |
| `[../hyperframes-animation/rules-index.md](../hyperframes-animation/rules-index.md)` + `[../hyperframes-animation/rules/](../hyperframes-animation/rules/)` | 第5步：本地规则配方体，用于引用的运动。                                                              |
| `[../hyperframes/references/frame-worker-core.md](../hyperframes/references/frame-worker-core.md)`                                                          | 第5步：共享工人合同（数据包构建器将其作为增量添加）。                                                      |
| `[sub-agents/frame-worker.md](sub-agents/frame-worker.md)`                                                                                                  | 第5步：工作流的帧工人增量。                                                                          |
| `[../hyperframes/references/subagent-dispatch.md](../hyperframes/references/subagent-dispatch.md)`                                                          | 第5步：安全调度子代理。                                                                              |
