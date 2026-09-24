> **首先，保持该技能为最新状态——在运行前与用户确认：** `npx hyperframes skills update product-launch-video`。若一切均为最新，此操作为快速空操作；否则，它会在你依赖该技能之前，刷新此技能及其依赖的核心领域技能。

> **media-use**：在获取音频、图片/标志之前，调用 `/media-use` 从 HeyGen 目录中解析 BGM/音效/图片，并从其官方来源获取品牌标志。首先运行 `--adopt` 以注册现有资源。参见 `/media-use` 技能。

> **figma source**：如果源是 figma.com 的 URL，先运行 `/figma`——如需资产导出、品牌令牌以及组件/分镜重建，则一并处理——然后基于其输出构建此工作流。不要直接通过原始 MCP 工具驱动 Figma：那会跳过 SVG 清理、`.media/manifest.jsonl` 来源追踪以及品牌令牌 `var()` 绑定，导致后续品牌变更无法传播，除非进行完整重新导入。

# Product Launch to HyperFrames

使用此技能来捕获产品、理解其品牌、规划发布视频，并在 HyperFrames 中逐帧构建。

> **入口是 `/hyperframes`。** 你负责统筹。依次执行每一步，验证各关卡通过后，再继续下一步。此技能适用于**正在推广、发布、宣传或揭晓的产品**，包括目的为推广的"为我们的网站制作推广"等请求。站点巡展 / 展示式请求也在此处处理：`BRIEF.md` 承载展示原貌的意图，而捕获的屏幕即为视频所呈现的资源。任何其他意图、单纯的"制作一个视频"，或任何不确定性 → 先阅读 `/hyperframes`——意图层决定所有路由决策，而一个未经 `BRIEF.md` 的新鲜创作到达此处时，也会经其处理（Setup 的开篇规则）。

你是统筹者。在 `videos/<project>/` 中工作。按顺序执行步骤，通过每个关卡后再继续。用户门控步骤为 Step 0、Step 3 和 Step 6。执行 Step 0 前，先阅读 `../hyperframes/references/brief-contract.md`——它定义了关卡类型，以及 `BRIEF.md` 的 `flow`/`storyboard` 如何推导出支配 Step 3/4/6 关卡的模式。除 Step 5 外，所有步骤均由你亲自执行，Step 5 中你按帧分派一个子代理。此处不涉及设计或运动规则；这些规则位于帧工作者子代理的 `../hyperframes-animation/rules/`、本技能的 `../hyperframes-animation/blueprints/` 以及 `hyperframes-creative` 中。

工作流：Step 0 设置 → `hyperframes.json`；Step 1 素材捕获 → `capture/`；Step 2 设计系统 → `frame.md`；Step 3 分镜与脚本 → `STORYBOARD.md` 和 `SCRIPT.md`；Step 3.1 音频 → `audio_meta.json`；Step 4 视觉设计 → 丰富的 `STORYBOARD.md`；Step 5 逐帧 → `compositions/frames/NN-*.html` 和 `index.html`；Step 6 最终渲染 → `renders/video.mp4`。

---

## Step 0: Setup

目标：以已确认的简报进入，创建 HyperFrames 项目，并将简报固化为可持久化的文件。

**简报由意图层确认，而非由此处提出的问题确认。** 开篇规则，按顺序如下：**(1)** `BRIEF.md` 存在 → 阅读它，无需提问——简报已定稿，且其 `flow`/`storyboard` 推导出行数模式（简报契约 § 1）。**(2)** 无 `BRIEF.md` 但项目已存在（磁盘上有 `hyperframes.json` / `STORYBOARD.md`）→ 依据分镜的 frontmatter 及已记录的偏好恢复；绝不重新询问一个半完成的项目。**(3)** 两者皆无——直接在此处收到的全新创作请求 → 阅读 `/hyperframes` 并运行其意图层（`references/intent-interview.md`）：它检查配方与记忆中的默认值，就本路线提出问题（`../hyperframes/references/routes/product-launch-video.md`），并返回锁定的简报。编辑请求跳过以上所有步骤——直接进行编辑。

仅在 `hyperframes.json` 缺失时初始化。项目名 `<project>` 取自品牌或领域，使用 kebab-case，例如 `acme-promo`；绝不使用工作区名或时间戳。

运行：`npx hyperframes init "videos/<project>" --non-interactive --example=blank --skill=product-launch-video`——`init` 会检查已安装的技能与 GitHub 上的最新版本，若有缺失则更新全局集。

初始化后，令 `<PROJECT_ROOT>` 为 `videos/<project>`，并以此目录为工作目录执行后续所有相对路径命令。以下命令中的 `.` 表示 `<PROJECT_ROOT>`；不得在调用者目录中写入 `.media`、`capture` 或输出文件。

**初始化后立即写入 `BRIEF.md`**（不得早于初始化——`init` 拒绝非空目录）：意图层锁定的简报，格式按 `../hyperframes/references/brief-format.md`。将 `<MEDIA_DIR>` 解析为已安装的 `/media-use` 技能目录。然后以 `node <MEDIA_DIR>/scripts/prefs.mjs record --hyperframes .` 记录每个基于偏好的答案（`brief-format.md` 指明了子集）。若意图层采纳了配方，运行 `node <MEDIA_DIR>/scripts/recipe.mjs use --hyperframes . --name <name>`；它会将 `frame.md` 复制到项目中（Step 2 因此跳过），并从 Step 3 草稿返回骨架。配方填充的是答案，而非批准；审查关卡仍会执行。

**在越过 Setup 之前，先显示登录状态**——运行 `npx hyperframes auth status` 并逐字传达其输出。它报告语音/BGM 将使用 HeyGen 还是本地引擎，以及未登录时如何登录。注意退出码约定：`auth status` **在未登录时退出码为 1**（以及当存储的凭据被拒绝时）——此非零退出码是正常的未登录状态，不是命令失败，因此不要将其视为错误，不要重试，也不要以会中断工作流的方式通过 `&&`/`set -e` 进行链式调用。应用分支：

- **协作模式**：等待用户登录或明确选择 `offline` / `go`。
- **自主模式**：说明状态，并在可用本地引擎范围内继续。

若不存在离线提供商，不得静默省略必需的能力；需表明阻碍。不得将此决策并入其他问题或写入每个仓库的 `.env` 中的密钥。认证所有权与离线回退：`/media-use` `references/setup-providers.md` § Providers。

**关卡**：`hyperframes.json` 和 `BRIEF.md` 存在；基于偏好的答案已记录（简报契约 § 2）；已显示登录状态（已登录，或继续离线）。

---

## Step 1: Capture assets

目标：收集视频所需的源素材、品牌信号和可用资源。

分类输入并选择路径。显式 URL → 捕获它并使用该网站进行旁白和素材。粘贴的脚本/简报 → 逐字保存为 `user_script.txt`；`VO_MODE`（逐字或重组）来自 `BRIEF.md`——意图层在收到脚本时要求该参数（若简报中某处缺少，此处仅询问一次）。然后确定捕获目标：文本中的 URL → 使用它；仅有品牌名 → 使用 `WebSearch` 确认 URL（一行），然后抓取；无 URL/网站（或简报要求不抓取）→ 无捕获路径。

使用以下命令运行捕获：`npx hyperframes capture "<URL>" -o ./capture --json`。保留默认的导航后预算，除非调用者拥有更小截止时间；然后传入一个正数的 `--capture-budget <milliseconds>`，为下游工作留出时间。`--timeout` 控制页面导航。仅在有意禁用可选图片说明时使用 `--skip-vision`。

立即检查命令结果与输出目录。非零退出码、JSON `ok: false`，或 `capture/BLOCKED.md` 均为**捕获路径的硬停止**：报告已记录的缘由，不要消费部分截图、DOM、令牌或资源。不要在生产不捕获的合成回退。仅在原始简报提供了源素材，或用户明确切换至提供的截图/简报后失败时，才通过无捕获路径继续。

警告如 `very little text content` 与空素材目录并不等同于页面可用。对于站点巡展或"展示原貌"的简报，要求可信任的捕获结构或提供的截图；若两者皆无，则停止。不得仅因捕获不可用而臆造或重建页面。

对于站点巡展或"展示原貌"简报，捕获的页面是视觉上的真实来源。使用真实截图而非在 HTML 中重建整个网站。若镜头需要内部运动，以截图为基底，在测得的位置叠加真实的捕获素材，或仅重建移动的组件。对于滚动镜头，在 `capture/screenshots/full-page.png`（整份文档的 1x 母版，1920 宽视口像素精确）上对视口进行动画——1x 的整份文档提供在 1:1 上下方的余量；超出 1:1 则需为该区域获取 2x 捕获。仅当用户明确要求风格化解读时，才重建整个页面；不可用的捕获本身不构成授权。

若存在 `GEMINI_API_KEY`、`GOOGLE_API_KEY`，或 OpenRouter 密钥，则捕获自动将素材说明生成至 `capture/extracted/asset-descriptions.md`。此非审查关卡。若无视觉密钥，使用 DOM 上下文并继续。

**无捕获路径**：手动创建 `capture/extracted/tokens.json`、`capture/extracted/visible-text.txt`、`capture/extracted/asset-descriptions.md`，以及 `capture/assets/`。`tokens.json` 应为 `{ "title": "", "description": "", "colors": [], "fonts": [] }`；尽可能从简报中填写 title/description。`visible-text.txt` 包含完整简报或脚本。`asset-descriptions.md` 应说明"未捕获到素材"，除非用户提供了素材说明。

**关卡**：捕获 JSON 报告 `ok: true`；不存在 `capture/BLOCKED.md`；`capture/extracted/tokens.json`、`capture/extracted/visible-text.txt`、`capture/extracted/asset-descriptions.md` 以及 `capture/assets/` 存在；且能用一句清晰的话说明品牌。将 `asset-descriptions.md` 视为主要素材清单。若捕获为真实捕获后仍缺失该文件，则停止并报告捕获不完整。对可选阶段降级的警告可接受，仅当此结构关卡仍通过时。

---

## Step 2: Design System

目标：选择一款已交付的帧预设；脚本将其转化为本视频的 `frame.md` + 字幕皮肤。

若 `BRIEF.md` 中命名了 `style_preset`——用户由意图层的展示中选择——则使用它；仅当简报未提及时有判断权。然后做出唯一选择——**选择哪款预设**：阅读 `../hyperframes-creative/references/design-spec.md`，并挑选最适合该品牌与简报的预设。然后运行：

```bash
node <SKILL_DIR>/scripts/build-frame.mjs --preset <name> --hyperframes .
```

脚本自动完成其余工作：将预设的 `FRAME.md` 复制为 `frame.md`，并**将其与 `capture/extracted/tokens.json` 中的品牌令牌混编**（品牌色彩按角色映射到预设的颜色键——墨色、画布、强调——保持键/结构/组件不变；预设的显示+正文字体替换为品牌的），将预设的字幕皮肤复制为 `.hyperframes/caption-skin.html`，并自校验（映射错误时退出码 1）。一旦退出码为 0，即可进入下一步，无需手动编辑规格。

`tokens.json` 无品牌色彩/字体（如未捕获）→ 脚本保留预设自身调色板，呈现一套可交付的设计。若简报命名了品牌色彩/字体而捕获遗漏，在运行前将它们添加到 `capture/extracted/tokens.json`（或使用用户的 `design.md` 填充）；仅在映射确实需要时，事后手动调整 `frame.md`。

**关卡**：`build-frame.mjs` 退出码 0——`frame.md` 已由命名的预设生成，且（若预设自带）`.hyperframes/caption-skin.html` 作为字幕皮肤源存在；所选预设已作为偏好记录（`--key style_preset --workflow <此工作流>`，简报契约 § 2）。

---

## Step 3: Storyboard and Script

目标：将简报和捕获素材转化为已批准的逐帧分镜计划。

阅读 `../hyperframes-creative/references/story-spine.md`（钩子语言、证据前价值、分镜作为提案、可溯源视觉）、`references/story-design.md`、`../hyperframes-animation/blueprints-index.md`、`../hyperframes/references/storyboard-format.md`，以及 `../hyperframes/references/script-format.md`。据此编写 `STORYBOARD.md`，并在需要旁白时编写 `SCRIPT.md`。设置 frontmatter 中的 `duration:` 为简报的 `length`——一个粗略预期；装配阶段会报告最终切割如何贴合该时长。

使用 `story-design.md` 进行故事蓝图、钩子、说服逻辑、节拍、`VO_MODE` 及素材选择。作为**软性指引**，参考 `../hyperframes-animation/blueprints-index.md` 中的角色→蓝图菜单：对每个节拍，标注一个适合的候选蓝图 id。故事真值仍决定存在哪些节拍——绝不强制某个节拍适配蓝图，也绝不仅因有成熟方案而臆造节拍。为每个视觉帧从 `capture/extracted/asset-descriptions.md`（规范清单）中选择 `asset_candidates`——不浏览原始的 `capture/assets/`。除非素材清单缺失或不可用，否则不向用户索要素材选择。使用分镜和脚本参考中要求的所有精确字段。

草稿完成后，运行计划通过环节——`../hyperframes/references/review-loop.md` § 1：以提案形式呈现计划，并提出两个问题——批准或修改，以及**先草图**（推荐）或跳过。反馈以聊天回复形式到达；循环直至批准。此为**检查关卡**（简报契约 § 1）：在自主模式下无需提问——以相同摘要作为提醒发布后继续；草图汇入构建，唯一的预览问题在 Step 6 提出。

**关卡**：`STORYBOARD.md` 存在，每个视觉帧均含 `asset_candidates`，需要旁白时 `SCRIPT.md` 存在，且用户批准了逐帧计划（自主：已以提醒发布摘要）。

---

## Step 3.1: Audio

目标：从已批准的脚本生成旁白、词时间点、音乐和音频元数据。

在 Step 3 批准后启动音频。在后台运行音频，然后继续 Step 4。

**在调用前，根据用户的要求选择旁白提供者和音色。** 以 Step 0 选择的提供商，通过 `--provider <provider>`（或设置 `HF_TTS_PROVIDER`）传入。若请求指定了音色、性别或语气，则挑选匹配的音色 id 并通过 `--voice <id>` 传入。管道默认为 **Marcia（女性）**（HeyGen）/ `am_michael`（Kokoro）——因此如"男性音色"的请求会被静默忽略，除非传入标志。音色 id 因提供商而异；根据 Step 0 登录状态所选提供商进行解析：**HeyGen**（已登录）通过 `node <MEDIA_DIR>/audio/scripts/heygen-tts.mjs --list`（或 `GET /v3/voices?engine=starfish`）执行；**Kokoro**（离线）通过 `<MEDIA_DIR>/audio/references/tts.md` 中的音色表（`am_`/`bm_` 为男性，`af_`/`bf_` 为女性）。当用户未表达偏好时，先回退到记忆中的音色（简报契约 § 2），并说明使用的音色；仅在两者均未指定时省略 `--voice`。当用户本次明确选择了音色时，记录之（`prefs.mjs record --key voice`）。

运行：`node <SKILL_DIR>/scripts/audio.mjs --script ./SCRIPT.md --storyboard ./STORYBOARD.md --hyperframes . --out ./audio_meta.json --provider <provider> --voice <voice-id> &`

音频脚本处理旁白、词时间点、HeyGen 音乐库中的 BGM 查找及时间元数据。BGM 情绪来自分镜的 `music:` 字段；**`music: none` 关闭 BGM**。此使用 HeyGen Audio API 进行获取，而非生成，并使用与 TTS 相同的 `~/.heygen` 凭据。详细资料参见 `../media-use/audio/references/tts.md`。

若无旁白且无 `SCRIPT.md`，则跳过语音生成。BGM 仍可运行，若分镜有音乐情绪。

**标准完全静默标记**：`music: none` 位于 `STORYBOARD.md` 顶部 YAML 块中**且**无 `SCRIPT.md`。该组合标记项目为静默——无旁白、无 BGM、无音效。`audio.mjs` 识别此组合并生成无内容（它移除任何过时 `audio_meta.json`；缺失的 `audio_meta.json` 是 assemble 视为静默的依据），因此 Step 3.1 可干净地跳过。当用户要求静音/无音乐视频时使用此——不得自创其他拼写。

**关卡**：音频任务已启动，或项目标记为静默（`music: none` + 无 `SCRIPT.md`）。

---

## Step 4: Frame Visual Design

目标：为每个分镜帧添加视觉方向、布局意图和运动选择。

**先绘制分镜表（仅协作模式）。** 计划批准后立即执行草图环节——`../hyperframes/references/review-loop.md` § 2（不等待 Step 3.1；草图不使用时间点）：以 `storyboard.html` 中单元格的形式自行绘制每个帧的线框（`../hyperframes-creative/references/storyboard-recipe.md` § 3），标记每个帧的 `built`，在所有帧标记为 `built` 后暂停一次布局问题，仅修订被命名的草图，直至分镜表确认。替代物：为捕获素材使用普通标注区块——真实文件在 Step 5 的工作者处到达。仅此时将视觉设计写入确认的布局中。在自主模式下，或用户在第 3 步选择跳过草图时，跳过此环节——帧从 `outline` 直接进入 Step 5 的 `animated`。

就地编辑 `STORYBOARD.md`。不要创建另一个分镜。以 `frame.md` 为色彩、字体、布局感觉和风格的唯一事实来源。

阅读 `references/visual-design.md`、`../hyperframes-animation/blueprints-index.md`、`references/motion-language.md`，以及 `../hyperframes-animation/rules-index.md`。使用 `visual-design.md` 作为方法（时间编码的镜头序列、内联 Layout 词汇表，以及必需的 `## Video direction` 块）。使用 `../hyperframes-animation/blueprints-index.md` 为每个帧选取镜头形状。使用 `motion-language.md`（运动词汇表 + 运动准则）和 `../hyperframes-animation/rules-index.md`（有效规则名称）作为运动——不得臆造运动名称。

**在设计任何命名的外观前，先搜索实时目录。** 对于简报命名的每个外观、效果、处理或转场——"CRT 扫描线"、"glitch"、"胶片颗粒"、"shimmer sweep"、"confetti burst"——运行 `npx hyperframes catalog --query "<用英文描述的该外观>" --json` 并在写入 `STORYBOARD.md` 前阅读顶部结果。搜索**无需任何安装**：无需项目、无需先前的 `add`、无需账号。它从任何目录按排名整个托管注册表（约 400 个区块和组件）。一个已完成工作的区块即成为帧的 `focal`——在此处命名，以便 Step 5 的工作者安装并定制它，而非重建它。仅在搜索返回无合适结果后，才手动编写该外观。

为每个视觉帧，按 `visual-design.md` 的方法，在 `STORYBOARD.md` 中写入**时间编码的镜头序列**：选取该帧的蓝图（或组合），用本产品内容实例化，并将每个 Scene 的展示节奏与旁白对齐，使帧在整个时长内逐步发展，而非前倾展示后冻结。按 Scene 内联陈述布局和运动（词汇表见 `visual-design.md` 和 `motion-language.md`）。添加一个全视频级 `## Video direction` 块。

当某元素在帧边界间明显持续时，向两个工作者提供 `STORYBOARD.md` 中相同的数值交接：在出帧添加 `handoff_out:`，在入帧添加匹配的 `handoff_in:`。命名元素及其确切 x/y 位置、缩放、不透明度和运动方向/速度——即使在未变化时也陈述每个字段，因为常数是 `opacity: 1`，而非省略。仅对有意干净的切割省略整个块。目标：并行工作者不得为同一条缝臆造两个不同版本。

不得更改故事、脚本、素材选择、`asset_candidates`、`transition_in` 或捕获源素材。此步骤不编写 HTML。

在视觉设计锁定后，分阶段命名素材：

`node <SKILL_DIR>/scripts/stage-assets.mjs --storyboard ./STORYBOARD.md --hyperframes .`

**关卡**：每个视觉帧均有节奏与旁白对齐的展示的、时间编码的镜头序列（无前倾展示）；存在 `## Video direction`；`assets/` 包含命名的素材。协作模式：草图表已在 Step 4 确认。

---

## Step 5: Build Frames

目标：将每个分镜帧构建为 HTML 组合并组装可播放视频。

若音频已启动，等待 Step 3.1 音频完成。然后同步时长并获取音效；若为静默则两者跳过。

`node <SKILL_DIR>/scripts/audio.mjs sync-durations --audio-meta ./audio_meta.json --storyboard ./STORYBOARD.md`

`node <SKILL_DIR>/scripts/audio.mjs fetch-sfx --storyboard ./STORYBOARD.md --hyperframes .`

时长同步是机械操作：真实语音时长优先；静默帧保留估计值；绝不手工编辑同步时长。

在组装前检查音乐与最终切割的匹配度。库曲目可能匹配所要求的情绪，但以安静的起始构建开始，会消耗短发布视频前几秒的节奏。将开头与之后的五秒片段比较；若后续片段有更强、更干净的音乐起始，则从那里修剪并保留短淡入加更长淡出。若帧或旁白时间点变化，则针对新最终时长重新检查此，确保音乐不会提前结束或在结尾留下静音。

在分派前，阅读 `../hyperframes/references/subagent-dispatch.md`。构建每帧数据包与工作者角色载荷：

`node <SKILL_DIR>/scripts/frame-packets.mjs --project "$PROJECT_DIR" --storyboard "$PROJECT_DIR/STORYBOARD.md"`

构建器在每个帧下生成一个有界数据包，位于 `.hyperframes/frame-packets/` 中（该帧分镜的完整块 + 蓝图正文 + 引用的每条规则配方内联），以及 `_role.md`（`../hyperframes/references/frame-worker-core.md` + 本技能的 `sub-agents/frame-worker.md`，逐字拼接——完整工作者角色）。按帧分派一个子代理，若可能则并行；否则分波运行工作者。每个工作者仅负责一帧：其提示包含 `_role.md` 和该帧的数据包——完整粘贴两者，或手工将两个文件路径交给工作者先读取（等效；工作者无论哪种方式都从这两份文档开始）——外加包含 `PROJECT_DIR`、`frame_id`、该帧是否在磁盘上有**已确认草图**（工作者据此着装该布局而非重绘——帧工作者核心 § 当存在已确认草图时）的调度上下文，画布尺寸，以及字幕状态与保留带（若启用了字幕）。

工作者仅读取其数据包和 `frame.md`；从不打开 `STORYBOARD.md` 或技能文档（数据包内联了上游选择的内容）。每个工作者仅写入 `compositions/frames/NN-*.html`。工作者绝不能编辑 `STORYBOARD.md`。

**全出血背景使用 `class="clip"` 层，绝不用 `#root`。** 帧的地面（颜色字段/渐变/网格）是其全时长的背景片段——在 `#root` / `data-composition-id` 元素上的 `background` 被限制在帧的窗口内，并非可靠的地面，因此深色内容可落在黑色的 `body` 宿主上且无法渲染。视频的基准地面由装配器从 `frame.md` 的 `canvas` 色彩在 index `#root` 上绘制。（完整规则 + 自检：`../hyperframes/references/frame-worker-core.md`。）

每个工作者返回后，统筹者将该帧在 `STORYBOARD.md` 中标记为 `animated`。

音频时间点存在后，在后台构建字幕并组装 index：

`node <SKILL_DIR>/scripts/captions.mjs build --storyboard ./STORYBOARD.md --audio-meta ./audio_meta.json --hyperframes . --out ./caption_groups.json &`

`node <SKILL_DIR>/scripts/assemble-index.mjs --storyboard ./STORYBOARD.md --hyperframes .`

`captions.mjs` 使用 Step 2 中复制的项目的 `.hyperframes/caption-skin.html` 作为字幕外观，并注入 `frame.md` 中的品牌令牌；若无皮肤存在，则渲染内置默认药丸。`captions: skipped (<reason>)` 有效。字幕明确跳过时继续，无需字幕。

**关卡**：每个帧均标记为 `animated`（协作：草图表在 Step 4 已确认）；`index.html` 存在；字幕已构建或明确跳过。

---

## Step 6: Finalize

目标：验证组装的视频、获取用户批准，并渲染最终 MP4。

注入转场，运行检查，暂停审查，然后渲染。

`node <SKILL_DIR>/scripts/transitions.mjs inject --storyboard ./STORYBOARD.md --hyperframes .`

`node <SKILL_DIR>/scripts/transitions.mjs verify --storyboard ./STORYBOARD.md --index ./index.html`

`npx hyperframes lint`

`npx hyperframes check`

`npx hyperframes snapshot --at <帧中点及每个切割前 0.1s 和后 0.2s>`

`snapshot` 将捕获帧拼接为一张接触表（`snapshots/contact-sheet.jpg`）。检查中点帧以排查布局失败，然后比较每个切割处的两张图像。持续元素必须保持承诺的位置、缩放、不透明度和方向；渲染前修复任何可见的跳变。

若命令失败，展示 stderr 并停止——不得堆叠恢复命令。自行修复：对 `compositions/frames/NN-*.html` 进行最便宜且安全的编辑，然后重跑失败检查。

检查通过后，暂停用户审查——审查环节的最后一步（`../hyperframes/references/review-loop.md` § 4）：一个问题，针对最终 Studio 预览——现在渲染，还是有哪些改动？（自主：预览或渲染的单一保留问题。）然后交付 MP4、接触表以及帧 id，以便修订可针对单个帧。

预览：`npx hyperframes preview --background`

仅在用户批准后（自主模式：预览或渲染问题后）渲染：

`npx hyperframes render --skill=product-launch-video --quality high --output renders/video.mp4`

渲染后除非用户要求，否则不重新运行 `lint`、`check` 或 `snapshot`。

**关卡**：`lint` 和 `check` 通过且快照在渲染前已检查；用户于审查暂停处批准（自主：检查通过且交付包含接触表）；`renders/video.mp4` 存在。最终回复说明 MP4 路径及最终时长。

---

## Quick Reference

**格式：** 横屏 `1920x1080`；竖屏 `1080x1920`；正方形 `1080x1080`——依据目标（简报契约 § 2）推导得出。在分镜的 frontmatter 中一次性设置格式。

**背景脚本**：本工作流在 `scripts/` 下仅包含以下脚本：`build-frame` 用于采用预设并将品牌混编至 `frame.md`（+ 字幕皮肤）；`audio` 用于 TTS、转录、BGM、音效和时长同步；`captions`；`transitions` 用于 inject 和 verify；`stage-assets` 用于将按帧命名的素材复制至 `assets/`；以及 `assemble-index`。其余由 `hyperframes` CLI 处理。

可复用、与产品无关的镜头形状位于 `../hyperframes-animation/blueprints/`（按 `../hyperframes-animation/blueprints-index.md` 索引）。

| 阅读                                                                                                                                                        | 何时                                                                                                     |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| `[../hyperframes/references/brief-contract.md](../hyperframes/references/brief-contract.md)`                                                                | 关卡类型、`BRIEF.md` 推导模式、字段语义。                                                            |
| `[../hyperframes-creative/references/story-spine.md](../hyperframes-creative/references/story-spine.md)`                                                    | Step 3：故事准则——钩子语言、证据前价值、提案形态、可溯源视觉。 |
| `[../hyperframes-creative/frame-presets/](../hyperframes-creative/frame-presets/)`                                                                          | Step 2：选择并采用帧预设。                                                                             |
| `[../hyperframes-creative/references/design-spec.md](../hyperframes-creative/references/design-spec.md)`                                                    | Step 2：正确应用品牌令牌。                                                                        |
| `[references/story-design.md](references/story-design.md)`                                                                                                  | Step 3：规划产品发布故事。                                                                           |
| `[../hyperframes-animation/blueprints-index.md](../hyperframes-animation/blueprints-index.md)`                                                              | Step 3：角色→蓝图菜单。Step 4：选取镜头形状。                                                            |
| `[../hyperframes/references/storyboard-format.md](../hyperframes/references/storyboard-format.md)`                                                          | Step 3：编写 `STORYBOARD.md`。                                                                           |
| `[../hyperframes/references/script-format.md](../hyperframes/references/script-format.md)`                                                                  | Step 3：编写 `SCRIPT.md`。                                                                               |
| `[../media-use/audio/references/tts.md](../media-use/audio/references/tts.md)`                                                                              | Step 3.1：选择或理解 TTS 提供商与音色。                                                            |
| `[references/visual-design.md](references/visual-design.md)`                                                                                                | Step 4：编写帧的镜头序列（+ Layout 词汇表）。                                                     |
| `[references/motion-language.md](references/motion-language.md)`                                                                                            | Step 4：运动词汇表 + 运动准则。                                                                       |
| `[references/cut-catalog.md](references/cut-catalog.md)`                                                                                                    | Step 4-5：切割目录（工作者构建帧内接缝）。                                                            |
| `[../hyperframes-animation/rules-index.md](../hyperframes-animation/rules-index.md)` + `[../hyperframes-animation/rules/](../hyperframes-animation/rules/)` | Step 5：引用的本地规则配方正文。                                                                   |
| `[../hyperframes/references/frame-worker-core.md](../hyperframes/references/frame-worker-core.md)`                                                          | Step 5：共享工作者契约（数据包构建器前置拼接）。                                                   |
| `[sub-agents/frame-worker.md](sub-agents/frame-worker.md)`                                                                                                  | Step 5：工作流的帧工作者增量。                                                                       |
| `[../hyperframes/references/subagent-dispatch.md](../hyperframes/references/subagent-dispatch.md)`                                                          | Step 5：安全分派子代理。                                                                              |
