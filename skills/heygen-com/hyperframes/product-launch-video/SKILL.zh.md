---
name: product-launch-video
description: 将产品或营销链接、粘贴的脚本或简短内容转换为产品发布/促销视频——SaaS促销、功能揭晓、产品演示、应用和公司发布。当用户希望营销、发布、推广或揭晓产品时使用；任何商业链接的默认选项。网站路线的游览/展示也在此处——简短内容包含“按原样展示”的意图。不明确 → /hyperframes。
---

**插件安装：** 在设置或新鲜命令之前，当此技能位于 HyperFrames 插件内时，请遵循 [插件执行规则](../hyperframes/references/plugin-installation.md)。独立安装则保留以下更新说明。

> **首先，保持此技能的新鲜状态——在运行前与用户确认：** `npx hyperframes skills update product-launch-video`。当一切正常时，这是一个快速的无操作；否则，它将在您依赖它们之前刷新此技能及其依赖的核心域技能。

> **media-use**：在获取音频/图像/标志之前，调用 `/media-use` 从 HeyGen 目录解析 BGM/SFX/图像，并从其官方来源获取品牌标志。首先运行 `--adopt` 以注册现有资源。参见 `/media-use` 技能。

> **figma source**：如果源是 figma.com URL，请先运行 `/figma`——资产导出、品牌令牌以及如果需要的话组件/故事板重建——然后从其输出构建此工作流。不要通过原始 MCP 工具直接驱动 Figma：那样会跳过 SVG 清理、`.media/manifest.jsonl` 起源和品牌令牌 `var()` 绑定，因此后续品牌更改无法在不完全重新导入的情况下传播。

# 产品发布到 HyperFrames

使用此技能捕获产品、理解其品牌、规划发布视频，并在 HyperFrames 中逐帧构建它。

> **入口是 `/hyperframes`。** 您是协调者。运行每个步骤，验证其门控，然后才能继续下一步。此技能适用于正在营销、发布、推广或揭晓的产品，包括当目的是促销时的请求，例如“我们网站的促销”。站点巡游/展示请求也保留在此处：`BRIEF.md` 传达了按原样展示的意图，捕获的屏幕成为视频使用的资产。任何其他意图、简单的“制作视频”或任何不确定性 → 首先阅读 `/hyperframes`——意图层拥有每条路线的决策权，并且没有 `BRIEF.md` 的新创建内容也会通过它（Setup 的开篇规则）。

您是协调者。在 `videos/<project>/` 中工作。按顺序运行步骤，并在继续前通过每个门控。用户门控步骤是步骤 0、步骤 3 和步骤 6。在步骤 0 之前阅读 `../hyperframes/references/brief-contract.md`——它定义了门控类型以及 `BRIEF.md` 的 `flow`/`storyboard` 如何导出控制步骤 3/4/6 门控的模式。除了步骤 5，您自己执行所有步骤，在步骤 5 中，您为每个帧派遣一个子代理。不要在此处放置设计或运动规则；那些存在于帧工作器子代理、此技能的本地 `../hyperframes-animation/rules/` + `../hyperframes-animation/blueprints/` 和 `hyperframes-creative`。

工作流：步骤 0 设置 -> `hyperframes.json`；步骤 1 捕获 -> `capture/`；步骤 2 设计系统 -> `frame.md`；步骤 3 故事板/脚本 -> `STORYBOARD.md` 和 `SCRIPT.md`；步骤 3.1 音频 -> `audio_meta.json`；步骤 4 视觉设计 -> 丰富的 `STORYBOARD.md`；步骤 5 帧 -> `compositions/frames/NN-*.html` 和 `index.html`；步骤 6 最终渲染 -> `renders/video.mp4`。

---

## 步骤 0：设置

目标：带确认的简报进入，创建 HyperFrames 项目，并使简报持久化。

**简报由意图层确认，而不是在此处提出问题。** 开启规则，按顺序：**(1)** `BRIEF.md` 存在 → 读取它并不要提问——简报已确定，其 `flow`/`storyboard` 导出模式（简报合同 § 1）。**(2)** 没有 `BRIEF.md` 但项目存在（`hyperframes.json` / 磁盘上的 `STORYBOARD.md`）→ 从故事板的 frontmatter 和记录的偏好中恢复；永远不要重新审问一个半建成的项目。**(3)** 都没有——一个直接到达此处的全新创建请求 → 阅读 `/hyperframes` 并运行其意图层（`references/intent-interview.md`）：它检查配方和记忆的默认值，进行此路线的问题（`../hyperframes/references/routes/product-launch-video.md`），并返回锁定简报。编辑请求跳过所有这些——去执行编辑。

仅在 `hyperframes.json` 缺失时初始化。从品牌或域在短横线命名法中命名 `<project>`，例如 `acme-promo`；永远不要使用工作区名称或时间戳。

`npx hyperframes init "videos/<project>" --non-interactive --example=blank --skill=product-launch-video`——`init` 检查已安装的技能与 GitHub 上的最新版本，如果任何技能过时，则更新全局集。

初始化后，让 `<PROJECT_ROOT>` 为 `videos/<project>`，并运行后续所有相对路径命令时将其作为工作目录。在以下命令中，`.` 表示 `<PROJECT_ROOT>`；永远不要在调用者目录中写入 `.media`、`capture` 或输出文件。

**立即在初始化后编写 `BRIEF.md`**（永远不要提前——`init` 拒绝非空目录）：意图层的锁定简报，形状按 `../hyperframes/references/brief-format.md`。解析 `<MEDIA_DIR>` 为已安装的 `/media-use` 技能目录。然后使用 `node <MEDIA_DIR>/scripts/prefs.mjs record --hyperframes .` 记录每个偏好支持的答案（`brief-format.md` 命名了子集）。如果意图层采用了配方，运行 `node <MEDIA_DIR>/scripts/recipe.mjs use --hyperframes . --name <name>`；它将其 `frame.md` 复制到项目中（步骤 2 然后被跳过），并返回步骤 3 草稿的骨架。配方填充答案，而不是批准；审查门控仍然运行。

**在继续 Setup 之前显示登录状态**——运行 `npx hyperframes auth status` 并逐字转述其输出。它报告语音/BGM 将使用 HeyGen 还是本地引擎，并且在注销时，如何登录。注意退出代码合同：`auth status` **在未登录时退出 1**（并且在存储的凭证被拒绝时）——这个非零退出是正常的注销状态，而不是命令失败，所以不要将其视为错误，不要重试它，并且不要以会导致中止工作流的方式将其与 `&&`/`set -e` 链接。应用一个分支：

- **协作式**：等待用户登录或显式选择 `offline` / `go`。
- **自主式**：声明状态并继续使用可用的本地引擎。

当没有离线提供者时，不要无声地省略所需功能；暴露障碍。不要将此决策折叠到另一个问题中，或写入到每个存储库的 `.env` 中。Auth 所有权和离线回退：`/media-use` `references/setup-providers.md` § Providers。

**门控**：`hyperframes.json` 和 `BRIEF.md` 存在；偏好支持的答案被记录（简报合同 § 2）；显示登录状态（已登录，或继续离线）。

---

## 步骤 1：捕获资产

目标：收集视频的源材料、品牌信号和可用资产。

分类输入并选择路径。显式 URL -> 捕获它并使用该站点进行叙述和资产。粘贴的脚本/简报 -> 原文保存为 `user_script.txt`；`VO_MODE`（原文或重构）来自 `BRIEF.md`——当脚本到达时，意图层会询问它（如果简报以某种方式缺少它，仅在此时询问一次）。然后解析捕获目标：文本中的 URL -> 使用它；仅品牌名称 -> `WebSearch`，确认一行中的 URL，然后爬取；没有 URL/站点（或简报说不抓取）-> 无捕获路径。

使用捕获：`npx hyperframes capture "<URL>" -o ./capture --json`。保持默认的导航预算，除非调用者拥有更小的截止日期；然后传递一个正的 `--capture-budget <milliseconds>` 留下下游工作的时间。`--timeout` 仅控制页面导航。仅在可选图像标题被有意禁用时使用 `--skip-vision`。

立即检查命令结果和输出目录。非零退出、JSON `ok: false` 或 `capture/BLOCKED.md` 是捕获路径的**硬停止**：报告记录的原因，不要消耗部分屏幕截图、DOM、令牌或资产。在 URL 捕获失败后，不要制造一个合成无捕获回退。仅在原始简报提供了源材料，或用户在失败后显式切换到提供的屏幕截图或简报时，才继续无捕获路径。

警告，例如 `very little text content` 与空资产目录一起，并不是可用页面的证明。对于站点巡游或按原样简报，需要可信捕获结构或提供的屏幕截图；如果都不存在，则停止。不要仅仅因为捕获不可用而发明或重建页面。

对于站点巡游或按原样简报，捕获的页面是视觉事实依据。使用真实屏幕截图而不是在 HTML 中重建整个网站。如果截图需要内部运动，将屏幕截图保留为基线，并在测量位置覆盖真实捕获的资产，或者仅重建移动的组件。对于滚动截图，在 `capture/screenshots/full-page.png` 上动画视口——整个文档的 1x 膜，对于 1920 宽视口的视口向下移动，像素精确。当页面太高无法一次性捕获时，会缺少；回退到同一目录中的重叠滚动位置截图。超过 1:1 的推入需要该区域的 2x 捕获，因为膜在 1x 以上没有头空间。仅在用户明确要求风格化解释时才重新创建整个页面；单独的不可用捕获不是授权。

如果存在 `GEMINI_API_KEY`、`GOOGLE_API_KEY` 或 OpenRouter 密钥，捕获自动标题资产到 `capture/extracted/asset-descriptions.md`。这不是一个审查门控。没有视觉密钥，使用 DOM 上下文并继续。

无捕获路径：手动创建 `capture/extracted/tokens.json`、`capture/extracted/visible-text.txt`、`capture/extracted/asset-descriptions.md` 和 `capture/assets/`。`tokens.json` 应该是 `{ "title": "", "description": "", "colors": [], "fonts": [] }`；尽可能从简报中填充标题/描述。`visible-text.txt` 包含完整的简报或脚本。`asset-descriptions.md` 应该说没有捕获资产，除非用户提供了资产注释。

**门控**：捕获 JSON 报告 `ok: true`；`capture/BLOCKED.md` 不存在；`capture/extracted/tokens.json`、`capture/extracted/visible-text.txt`、`capture/extracted/asset-descriptions.md` 和 `capture/assets/` 存在；并且您可以清晰地声明品牌。将 `asset-descriptions.md` 视为主资产清单。如果捕获后它缺失，停止并报告捕获不完整。仅在结构性门控仍然通过时，才接受关于退化可选阶段的警告。

---

## 步骤 2：设计系统

目标：选择一个已发布的帧预设；脚本将其转换为此视频的 `frame.md` + 标题皮肤。

当 `BRIEF.md` 指定 `style_preset`——用户通过意图层中的展示挑选了它——使用它；判断权只有当简报是沉默时才属于你。然后你只做一次调用——**哪个预设**：读取 `../hyperframes-creative/references/design-spec.md` 并选择最适合品牌和简报的预设。然后运行：

```bash
node <SKILL_DIR>/scripts/build-frame.mjs --preset <name> --hyperframes .
```

脚本会确定性地完成其余工作：复制预设的 `FRAME.md` → `frame.md` 并**重新混合**它到 `capture/extracted/tokens.json` 中的品牌令牌（品牌颜色映射到预设的颜色键，按角色——墨水、画布、强调——保持键/结构/组件；预设的显示 + 正文字体被品牌的替换），复制预设的标题皮肤到 `.hyperframes/caption-skin.html`，并自我验证（在映射损坏时退出 1）。一旦它退出 0，立即进入下一步——不要手动编辑规范。

`tokens.json` 没有品牌颜色/字体（例如没有捕获）→ 脚本保留预设自己的调色板，一个可完全发布的完整设计。如果简报命名了捕获遗漏的品牌颜色/字体，在运行之前将它们添加到 `capture/extracted/tokens.json` 中（或使用用户的 `design.md` 来填充它）；只有在映射确实需要的情况下，才手动调整 `frame.md`。

**门控**：`build-frame.mjs` 退出 0——`frame.md` 存在来自命名预设，并且（当预设提供时）`.hyperframes/caption-skin.html` 存在作为标题皮肤源；选择的预设被记录为偏好（`--key style_preset --workflow <this workflow>`，简报合同 § 2）。

---

## 步骤 3：Storyboard 和 Script

目标：将简报和捕获的材料转换为批准的逐帧故事计划。

阅读 `../hyperframes-creative/references/story-spine.md`（钩语言、价值先于证据、Storyboard 作为提案、来源可追溯的视觉）、`references/story-design.md`、`../hyperframes-animation/blueprints-index.md`、`../hyperframes/references/storyboard-format.md` 和 `../hyperframes/references/script-format.md`。使用它们来编写 `STORYBOARD.md`，当需要叙述时，编写 `SCRIPT.md`。从简报的 `length` 设置 frontmatter `duration:`——一个粗略预期；组装报告将切割与它的对齐情况。

使用 `story-design.md` 进行故事蓝图、钩、说服逻辑、节拍、`VO_MODE` 和资产选择。作为**软指南**，参考 `../hyperframes-animation/blueprints-index.md` 中的角色→蓝图菜单：对于每个节拍，当有一个适合的蓝图时，记下一个候选蓝图 ID。故事真相仍然决定哪些节拍存在——永远不要强迫节拍适应蓝图，也永远不要仅仅因为一个可证明的形状可用而发明节拍。从 `capture/extracted/asset-descriptions.md`（规范清单）选择每个视觉帧的 `asset_candidates`——不要浏览原始 `capture/assets/`。除非该清单缺失或不可用，否则不要要求用户选择资产。使用来自故事板和脚本参考的精确所需字段。

起草后，运行审查循环的计划通过——`../hyperframes/references/review-loop.md` § 1：将计划作为提案提出，并询问两个问题——批准或更改，以及**草图优先**（推荐）或跳过。反馈作为聊天回复到达；循环直到批准。这是一个**检查点门控**（简报合同 § 1）：在自主模式下没有要询问的——将相同的摘要作为提示发布并继续；草图合并到构建中，并且一个预览问题在步骤 6 来临。

**门控**：`STORYBOARD.md` 存在，每个视觉帧都有 `asset_candidates`，当需要叙述时 `SCRIPT.md` 存在，并且用户批准了逐帧计划（自主：摘要被作为提示发布）。

---

## 步骤 3.1：Audio

目标：从批准的脚本生成叙述、单词时间、音乐和音频元数据。

在步骤 3 批准后开始音频。在后台运行它，然后继续步骤 4。

**在调用之前选择叙述提供者和声音来自用户的询问。** 使用在步骤 0 中选择的提供者在 `--provider <provider>`（或设置 `HF_TTS_PROVIDER`）中传递提供者。如果请求命名了声音、性别或语调，选择匹配的声音 ID 并使用 `--voice <id>` 传递它。管道默认是否则 **Marcia（女性）** 在 HeyGen / `am_michael` 在 Kokoro 上——所以像“男性声音”这样的请求被无声忽略，除非你传递标志。声音 ID 是提供者特定的；针对步骤 0 的登录状态选择的提供者解析：**HeyGen**（已登录）通过 `node <MEDIA_DIR>/audio/scripts/heygen-tts.mjs --list`（或 `GET /v3/voices?engine=starfish`）；**Kokoro**（离线）通过 `<MEDIA_DIR>/audio/references/tts.md` 中的声音表（前缀 `am_`/`bm_` 男性，`af_`/`bf_` 女性）。当用户表达了没有偏好时，在管道默认之前回退到记住的声音（简报合同 § 2），并说明您使用了哪个；仅在两者都没有命名一个时才省略 `--voice`。当用户在此运行中明确选择了一个声音时，记录它（`prefs.mjs record --key voice`）。

`node <SKILL_DIR>/scripts/audio.mjs --script ./SCRIPT.md --storyboard ./STORYBOARD.md --hyperframes . --out ./audio_meta.json --provider <provider> --voice <voice-id> &`

音频脚本处理旁白、字词时间、从HeyGen音乐库中查找背景音乐（BGM）以及时间元数据。BGM情绪来自故事板的`music:`字段；**`music: none`会关闭BGM**。这使用HeyGen音频API进行检索，而不是生成，并使用与TTS相同的`~/.heygen`凭证。有关提供者详细信息，请阅读`../media-use/audio/references/tts.md`。

如果没有旁白且没有`SCRIPT.md`，则跳过语音生成。即使故事板有音乐情绪，BGM仍可能运行。

**标准的完全静音标记**：`STORYBOARD.md`顶部YAML块中的`music: none` **并且**没有`SCRIPT.md`。这种组合将项目标记为静音——没有旁白，没有BGM，没有音效。`audio.mjs`识别它并生成空白（它删除任何过时的`audio_meta.json`；`assemble`将不存在的`audio_meta.json`视为静音），因此第3.1步可以干净地跳过。当用户要求制作无声/无音乐的视频时使用它——不要自行编造其他拼写。

**门禁**：音频任务已开始，或者项目被标记为静音（`music: none` + 没有`SCRIPT.md`）。

---

## 第4步：帧视觉设计

目标：为每个故事板帧添加视觉方向、布局意图和运动选择。

**首先绘制故事板页面（仅限协作）。** 一旦计划获得批准，立即运行绘制流程——`../hyperframes/references/review-loop.md` § 2（不要等待第3.1步；绘制不使用时间）：将每个帧作为`storyboard.html`（`../hyperframes-creative/references/storyboard-recipe.md` § 3）的单元格自行绘制，标记每个`built`，在所有帧都`built`时暂停一个布局问题，并仅修订命名为确认的草图，直到页面确认。替身：用于捕获资产的普通标记块——实际文件将在第5步的工作人员中到达。只有在视觉设计锁定后，才在确认的布局下方编写视觉设计。在自主模式下，或者当用户选择在第3步跳过绘制时，跳过此步骤——帧直接从`outline`跳到第5步的`animated`。

就地编辑`STORYBOARD.md`。不要创建另一个故事板。使用`frame.md`作为颜色、类型、布局感觉和样式的真实来源。

阅读`references/visual-design.md`、`../hyperframes-animation/blueprints-index.md`、`references/motion-language.md`和`../hyperframes-animation/rules-index.md`。使用`visual-design.md`作为方法（时间编码的镜头序列、内联布局词汇表以及必需的`## 视频方向`块）。使用`../hyperframes-animation/blueprints-index.md`选择每个帧的镜头形状。使用`motion-language.md`（运动词汇表+运动准则）和`../hyperframes-animation/rules-index.md`（有效规则名称）进行运动——不要编造运动名称。

**在您设计任何命名外观之前，先搜索实时目录。** 对于每个外观、效果、处理或过渡，简要命名——"CRT扫描线"、"故障"、"胶片颗粒"、"闪烁扫描"、"五彩纸屑爆炸"——运行`npx hyperframes catalog --query "<用普通英语描述的外观>" --json`并阅读顶部结果，然后再将此外观写入`STORYBOARD.md`。搜索不需要**安装任何东西**：没有项目，没有先前的`add`，没有账户。它从任何目录对托管注册表（~400个模块和组件）进行排名。已经完成工作的模块成为帧的`focal`——在这里命名它，以便第5步的工作人员安装和自定义它，而不是重新构建它。只有在搜索结果为空时，才手动编写外观。

对于每个视觉帧，根据`visual-design.md`的方法，在`STORYBOARD.md`中编写**时间编码的镜头序列**：选择帧的蓝图（或组合），用此产品的内容实例化它，并调整每个场景的揭示速度，以便帧在其完整持续时间中发展，而不是前加载然后冻结。按场景**内联**声明布局和运动（词汇表在`visual-design.md`和`motion-language.md`中）。添加一个视频范围的`## 视频方向`块。

当元素在帧边界处可见地继续时，在`STORYBOARD.md`中给两个工作人员相同的数字交接：在出帧中添加`handoff_out:`，并在入帧中添加匹配的`handoff_in:`。命名元素及其确切的x/y位置、缩放、不透明度和切割时的运动方向/速度——即使它没有改变，也要声明每个字段，因为常量是`opacity: 1`，而不是省略。仅当存在故意干净的切割时才省略整个块。目标是简单的：并行工作的工作人员不应编造相同接缝的两个不同版本。

不要更改故事、脚本、资产选择、`asset_candidates`、`transition_in`或捕获的源材料。在此步骤中不要编写HTML。

在视觉设计锁定后，阶段命名资产：

`node <SKILL_DIR>/scripts/stage-assets.mjs --storyboard ./STORYBOARD.md --hyperframes .`

**门禁**：每个视觉帧都有一个时间编码的镜头序列，其揭示速度与旁白同步（没有前加载）；`## 视频方向`存在；`assets/`包含命名资产。协作：草图页面已确认。

---

## 第5步：构建帧

目标：将每个故事板帧作为HTML组合构建，并组装可播放视频。

如果音频已开始，等待第3.1步音频完成。然后同步持续时间并获取音效；如果静音则跳过两者。

`node <SKILL_DIR>/scripts/audio.mjs sync-durations --audio-meta ./audio_meta.json --storyboard ./STORYBOARD.md`

`node <SKILL_DIR>/scripts/audio.mjs fetch-sfx --storyboard ./STORYBOARD.md --hyperframes .`

持续时间同步是机械的：实际语音持续时间获胜；静音帧保持估计；永远不要手动编辑同步后的持续时间。

在组装前检查音乐与最终剪辑。库曲目可以匹配请求的情绪，但在安静构建时可能打开，导致在短启动视频的前几秒钟耗尽。比较开头与后面的五秒部分；当后面的部分有更强的、音乐上干净的开始时，从那里剪切并保留一个短淡入和一个长淡出。如果帧或旁白时间发生变化，请根据新的最终持续时间重新进行此检查，以确保音乐永远不会过早结束或在尾部留下沉默。

在派遣前，阅读`../hyperframes/references/subagent-dispatch.md`。构建每个帧的数据包和工作人员角色负载：

`node <SKILL_DIR>/scripts/frame-packets.mjs --project "$PROJECT_DIR" --storyboard "$PROJECT_DIR/STORYBOARD.md"`

构建者在每个帧下写入一个有界数据包（`.hyperframes/frame-packets/`）（帧的确切故事板块+蓝图正文+每个引用的规则配方，内联）和`_role.md`（`../hyperframes/references/frame-worker-core.md` + 此技能的`sub-agents/frame-worker.md`，逐字连接——完整的工人角色）。并行派遣每个子代理；否则分波运行。每个工人得到一个帧：其提示包含`_role.md`和该帧的数据包——将两者全部粘贴，或者将两个文件路径交给工人首先读取（等效；工人无论如何都是从这两个文档开始）——加上一个派遣上下文，包含`PROJECT_DIR`、`frame_id`、该帧在磁盘上是否有**确认的草图**（工人使用该布局而不是重新绘制它——帧工人核心 § 当存在确认的草图时）、画布大小和字幕状态+如果启用字幕则保留带）。

工人只读取其数据包和`frame.md`；他们永远不会打开`STORYBOARD.md`或技能文档（数据包内联了上游选择的内容）。每个工人只写入`compositions/frames/NN-*.html`。工人必须永远不会编辑`STORYBOARD.md`。

**全出血背景骑在`class="clip"`层上，而不是`#root`。** 帧的地面（颜色字段/渐变/网格）是其自己的全持续时间背景剪辑——在`#root` / `data-composition-id`元素上设置的`background`被剪辑门控到帧的窗口，并且不是一个可靠的地面，因此深色内容可能会落在黑色的主机`body`上并渲染不可见。视频的基础地面由组装器从`frame.md`的`canvas`颜色绘制到索引`#root`。（完整规则+自我检查：`../hyperframes/references/frame-worker-core.md`。）

每当一个工人返回时，协调器在`STORYBOARD.md`中将该帧标记为`animated`。

在音频时间存在后，在后台构建字幕并组装索引：

`node <SKILL_DIR>/scripts/captions.mjs build --storyboard ./STORYBOARD.md --audio-meta ./audio_meta.json --hyperframes . --out ./caption_groups.json &`

`node <SKILL_DIR>/scripts/assemble-index.mjs --storyboard ./STORYBOARD.md --hyperframes .`

`captions.mjs`使用项目的`.hyperframes/caption-skin.html`（在第2步中复制）作为字幕外观，注入来自`frame.md`的品牌标记；如果没有皮肤，则渲染内置默认药丸。`captions: skipped (<reason>)`是有效的。在明确跳过时继续不字幕。

**门禁**：每个帧都被标记为`animated`（协作：在第4步确认了草图），`index.html`存在，并且字幕已构建或明确跳过。

---

## 第6步：最终确认

目标：验证组装的视频，获取用户批准，并渲染最终MP4。

注入过渡，运行检查，暂停审查，然后渲染。

`node <SKILL_DIR>/scripts/transitions.mjs inject --storyboard ./STORYBOARD.md --hyperframes .`

`node <SKILL_DIR>/scripts/transitions.mjs verify --storyboard ./STORYBOARD.md --index ./index.html`

`npx hyperframes lint`

`npx hyperframes check`

`npx hyperframes snapshot --at <frame-midpoints-and-each-cut-minus-0.1s-and-plus-0.2s>`

`snapshot`将捕获的帧拼接成一个接触表（`snapshots/contact-sheet.jpg`）。检查中点帧是否有布局故障，然后比较每个切割周围的两个图像。继续的元素必须保持承诺的位置、缩放、不透明度和方向；修复任何可见的弹出，然后再渲染。

如果命令失败，显示`stderr`并停止——不要堆叠恢复命令。自己修复它：对`compositions/frames/NN-*.html`进行最安全的编辑，然后重新运行失败的检查。

检查通过后，暂停用户审查——审查循环的最终外观（`../hyperframes/references/review-loop.md` § 4）：一个问题，在最终Studio预览上——现在渲染，还是有什么变化？（自主：一个问题，预览优先还是渲染。）然后交付MP4、接触表和帧ID，以便修订可以针对单个帧。

预览：`npx hyperframes preview --background`

只有在用户批准后（自主模式：在预览或渲染问题后）才渲染：

`npx hyperframes render --skill=product-launch-video --quality high --output renders/video.mp4`

渲染后不要重新运行`lint`、`check`或`snapshot`，除非用户要求。

**门禁**：`lint`和`check`通过，并且在渲染前检查了快照；用户在审查暂停时批准（自主：检查通过并且交付包括接触表）；`renders/video.mp4`存在。最终回复声明MP4路径和最终持续时间。

---

## 快速参考

**格式**：横向`1920x1080`；纵向`1080x1920`；方形`1080x1080`——源自目的地（简要合同 § 2）。在故事板frontmatter中设置一次格式。

**背景脚本**：工作流仅在`scripts/`下发送这些脚本：`build-frame`用于采用+品牌混合帧预设到`frame.md`（+字幕皮肤）；`audio`用于TTS、转录、BGM、音效和持续时间同步；`captions`；`transitions`用于注入和验证；`stage-assets`用于将命名帧资产复制到`assets/`；和`assemble`。其他所有内容均由`hyperframes` CLI处理。

可重用、产品无关的镜头形状位于`../hyperframes-animation/blueprints/`（由`../hyperframes-animation/blueprints-index.md`索引）。

| 阅读                                                                                                                                                        | 时间                                                                                                     |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| `[../hyperframes/references/brief-contract.md](../hyperframes/references/brief-contract.md)`                                                                | 门类型、从 `BRIEF.md` 推导模式、字段语义。                                            |
| `[../hyperframes-creative/references/story-spine.md](../hyperframes-creative/references/story-spine.md)`                                                    | 第 3 步：故事准则 — 钩子语言、先价值后证据、提案形状、可追溯来源的视觉效果。 |
| `[../hyperframes-creative/frame-presets/](../hyperframes-creative/frame-presets/)`                                                                          | 第 2 步：选择并采用一个框架预设。                                                                 |
| `[../hyperframes-creative/references/design-spec.md](../hyperframes-creative/references/design-spec.md)`                                                    | 第 2 步：正确应用品牌令牌。                                                                    |
| `[references/story-design.md](references/story-design.md)`                                                                                                  | 第 3 步：规划产品发布故事。                                                                   |
| `[../hyperframes-animation/blueprints-index.md](../hyperframes-animation/blueprints-index.md)`                                                              | 第 3 步：角色→蓝图菜单。第 4 步：选择镜头形状。                                                |
| `[../hyperframes/references/storyboard-format.md](../hyperframes/references/storyboard-format.md)`                                                          | 第 3 步：编写 `STORYBOARD.md`。                                                                           |
| `[../hyperframes/references/script-format.md](../hyperframes/references/script-format.md)`                                                                  | 第 3 步：编写 `SCRIPT.md`。                                                                               |
| `[../media-use/audio/references/tts.md](../media-use/audio/references/tts.md)`                                                                              | 第 3.1 步：选择或理解 TTS 提供商和声音。                                                 |
| `[references/visual-design.md](references/visual-design.md)`                                                                                                | 第 4 步：编写框架的镜头序列 (+ 布局词汇)。                                           |
| `[references/motion-language.md](references/motion-language.md)`                                                                                            | 第 4 步：运动词汇 + 运动准则。                                                     |
| `[references/cut-catalog.md](references/cut-catalog.md)`                                                                                                    | 第 4-5 步：剪辑目录（工作者在框架内构建接缝）。                                            |
| `[../hyperframes-animation/rules-index.md](../hyperframes-animation/rules-index.md)` + `[../hyperframes-animation/rules/](../hyperframes-animation/rules/)` | 第 5 步：引用运动的本地规则配方正文。                                                  |
| `[../hyperframes/references/frame-worker-core.md](../hyperframes/references/frame-worker-core.md)`                                                          | 第 5 步：共享的工作者合同（数据包构建器将其添加到增量之前）。                            |
| `[sub-agents/frame-worker.md](sub-agents/frame-worker.md)`                                                                                                  | 第 5 步：工作流的框架工作者增量。                                                               |
| `[../hyperframes/references/subagent-dispatch.md](../hyperframes/references/subagent-dispatch.md)`                                                          | 第 5 步：安全地调度子代理。                                                                      |
