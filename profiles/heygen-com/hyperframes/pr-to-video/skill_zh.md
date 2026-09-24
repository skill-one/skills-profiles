> **首先，保持此技能保持新鲜——在运行前与用户确认：** `npx hyperframes skills update pr-to-video`。当所有内容都更新时，这是一个快速的无操作；否则，它会在您依赖之前刷新此技能及其依赖的核心领域技能。

> **media-use**：在获取音频/图像/标志之前，调用 `/media-use` 以从 HeyGen 目录解析 BGM/音效和品牌标志。首先运行 `--adopt` 以注册现有资源。参见 `/media-use` 技能。

# PR to HyperFrames

使用此技能将 GitHub 拉取请求（pull request）导入，理解变更，规划代码变更讲解，并在 HyperFrames 中逐帧构建。输入是**代码变更**（通过 `gh` 读取），而非网站——**没有捕获步骤，也没有真实资源**，仅有的资源是贡献者的头像。

> **入门入口是 `/hyperframes`。** 您是编排者。依次执行每个步骤，验证其关卡，然后才继续。此技能用于**GitHub 拉取请求**（代码变更）。任何其他意图、单纯的“制作视频”，或任何不确定性 → 先阅读 `/hyperframes` ——意图层拥有所有路由决策，且未经 `BRIEF.md` 的新创建在此到达时也会经过它（Setup 的开头规则）。

您是编排者。在已解析的外部 `PROJECT_DIR` 中工作，默认不在调用者的代码库中进行。按顺序执行步骤，在继续前通过每个关卡。用户控制的步骤是 Step 0、Step 3 和 Step 6。在 Step 0 之前读取 `../hyperframes/references/brief-contract.md` ——它定义了关卡类型，以及 `BRIEF.md` 的 `flow`/`storyboard` 如何推导出规范 Step 3/4/6 的模式的依据。除 Step 5 外，您亲自执行每个步骤；Step 5 中，您派发一个有界的工作池帧工人。不要在此处放置设计或运动规则；这些位于帧工人子代理的 `../hyperframes-animation/rules/` + `../hyperframes-animation/blueprints/` 以及 `hyperframes-creative` 中。

工作流：Step 0 设置 → `hyperframes.json`；Step 1 导入 → `capture/extracted/` + `assets/<login>.png`；Step 2 设计系统 → `frame.md`；Step 3 分镜/脚本 → `STORYBOARD.md` 和 `SCRIPT.md`；Step 3.1 音频 → `audio_meta.json`；Step 4 视觉设计 → 丰富的 `STORYBOARD.md`；Step 5 帧 → `compositions/frames/NN-*.html` 和 `index.html`；Step 6 最终渲染 → `renders/video.mp4`。

---

## Step 0: Setup

目标：以确认的简报进入——包括**PR 引用**（完整 URL、`<owner>/<repo>#<N>` 引用，或已检出的代码库中的“此 PR”）——创建 HyperFrames 项目，并使简报持久化。风格始终为**代码编辑型**（在 Step 2 中固定，从不询问）。

**简报由意图层确认，而非在此询问问题。** 开头规则，按顺序：**(1)** `BRIEF.md` 存在 → 阅读它，不问任何问题——简报已确定，其 `flow`/`storyboard` 推导出模式（简报契约 § 1）。**(2)** 无 `BRIEF.md`，但项目存在（磁盘上的 `hyperframes.json` / `STORYBOARD.md`）→ 从分镜的前置元数据记录和记录的偏好继续；永远不重新询问半完成的项目。**(3)** 两者皆无 → 这是直接到达此处的全新创建请求 → 阅读 `/hyperframes` 并运行其意图层（`references/intent-interview.md`）：它检查配方和回忆中的默认值，并针对此路由进行提问——包括 PR 规模 → 长度教义，完整地位于 `../hyperframes/references/routes/pr-to-video.md` ——然后返回锁定的简报。编辑请求跳过所有这些——去执行编辑。

在做任何其他工作之前，解析项目目录。保留用户提供的项目目录；否则使用解析器打印的持久外部缓存位置。永远不在调用者的代码库中创建 `videos/`：

```bash
PR="<url | owner/repo#N>"
if [ -n "${EXPLICIT_PROJECT_DIR:-}" ]; then
  PROJECT_DIR="$(node <SKILL_DIR>/scripts/project-dir.mjs --pr "$PR" --project-dir "$EXPLICIT_PROJECT_DIR")"
else
  PROJECT_DIR="$(node <SKILL_DIR>/scripts/project-dir.mjs --pr "$PR")"
fi
echo "PR-to-video project: $PROJECT_DIR"
node <SKILL_DIR>/scripts/preflight.mjs
```

能力预检在获取、故事工作、音频或帧派发之前运行。如果安装的程序化 CLI 无法运行此技能所需的验证命令，请停止并给出其升级说明，而不是先消耗本次运行的上下文。

仅当 `$PROJECT_DIR/hyperframes.json` 缺失时才初始化。其基名来自 PR，例如 `acme-sdk-pr-1842`；永远不使用工作区名称或时间戳。

`npx hyperframes init "$PROJECT_DIR" --non-interactive --example=blank --skill=pr-to-video` — `init` 检查已安装的技能与 GitHub 上的最新版本，并在任何过期时更新全局设置。

以下所有相对路径命令均在 `$PROJECT_DIR` 作为其工作目录下运行。无显式子shell的示例意为 `(cd "$PROJECT_DIR" && …)`；永远不改变调用者代码库的工作树。

初始化后立即写入 `BRIEF.md`（永远不提前——`init` 拒绝非空目录）：按 `../hyperframes/references/brief-format.md` 的形状，意图层锁定的简报。将 `<MEDIA_DIR>` 解析为安装的 `/media-use` 技能目录。然后以 `node <MEDIA_DIR>/scripts/prefs.mjs record --hyperframes .` 记录每个基于偏好的答案（`brief-format.md` 指定了子集）。如果意图层采纳了配方，运行 `node <MEDIA_DIR>/scripts/recipe.mjs use --hyperframes . --name <name>`；它将配方的 `frame.md` 复制到项目中（Step 2 然后跳过）并从 Step 3 草稿返回骨架。配方填充答案，而非批准；审查关卡仍会运行。

在继续 Setup 之前，展示登录状态——运行 `npx hyperframes auth status` 并逐字传达其输出。它报告语音/BGM 是否使用 HeyGen 或本地引擎，以及未登录时如何登录。应用一个分支：

- **协作模式：** 等待用户登录或明确选择 `offline` / `go`。
- **自主模式：** 说明状态并继续使用可用的本地引擎。

当不存在离线提供者时，不要静默省略必需的能力；突出显示阻塞问题。不要将此决策合并为另一个问题，也不要将密钥写入每个代码库的 `.env`。Auth 所有权和离线回退：`/media-use` `references/setup-providers.md` § Providers。

**关卡：** `hyperframes.json` 和 `BRIEF.md` 存在；PR 引用已捕获在简报中；基于偏好的答案已记录（简报契约 § 2）；已展示登录状态（已登录，或继续离线）。

---

## Step 1: Ingest the PR (no capture)

目标：获取 PR 的事实并将其折叠进项目作为信息来源。**没有网站捕获**。`fetch-pr.mjs` 确定性地运行 `gh`——通过分页 `gh api` 完成文件列表，使大型 PR 不会在约 100 个文件处截断，并只写入 `capture/pr.json` + `capture/diff.patch`（无临时目录）。对于 MERGED PR，它还尽力将 `shipped_version`（+ `version_source`）解析到 `pr.json` 中，以便结束卡片能引用真实版本而非虚构一个。然后 `ingest.mjs` 将其离线折叠进合成的捕获包。

```bash
PR="<url | owner/repo#N | N>"

# 确定性地获取 PR：运行 gh，通过分页 gh api 完成文件列表（使大型 PR 不会在约 100 个文件处截断），仅写入 capture/pr.json +
# capture/diff.patch — 无临时目录。gh 认证/未找到/私有错误在此以退出码 1 退出。
(cd "$PROJECT_DIR" && node <SKILL_DIR>/scripts/fetch-pr.mjs --pr "$PR" --out-dir ./capture)

# 离线转换 → capture/extracted/{tokens.json (颜色:[] → 代码编辑型调色板),
# visible-text.txt (简报), people.json (贡献者，过滤机器人，名称+登录，avatarFile=assets/<login>.png)}。
(cd "$PROJECT_DIR" && node <SKILL_DIR>/scripts/ingest.mjs \
  --pr-json ./capture/pr.json --diff ./capture/diff.patch --out-dir ./capture/extracted)

# 人群界面的一个网络步骤——下载每个贡献者的 GitHub 头像到 assets/<login>.png，用于 credits 结尾。
# 尽力而为；始终以退出码 0 退出。
(cd "$PROJECT_DIR" && node <SKILL_DIR>/scripts/fetch-people-avatars.mjs \
  --people ./capture/extracted/people.json)
```

如果 `fetch-pr.mjs` 以退出码 1 退出（gh 认证/未找到/私有），报告其 stderr 并停止——**不要伪造 PR 内容**。如果 `ingest.mjs` 以退出码 1 退出，读取其 stderr（通常是格式错误的 `pr.json`），修复后重跑（确定性的）。`fetch-people-avatars.mjs` 始终以退出码 0 退出；头像缺失仅意味着作者处没有 credits 结尾。

`people.json` 携带 `gh` 已为哪些贡献者命名的 `name`（PR 作者、提交作者、`mergedBy`）——其余为 `null`（审查者/评论者/负责人，`gh pr view` 仅始终给一个裸 `login`）。在 Step 3 写 credits 结尾之前，为实际会出现在该帧上的 1-6 个人物解析任何 `null` 名称：`gh api users/<login> --jq .name`（您已有 `gh`——无需为此编写脚本）。如果 GitHub 对该用户也没有公开名称，回退到屏幕上的 `login`，并从说出的行中移除该人（参见 story-design.md 的 credits 部分——配音仍需说出名字，而非原始句柄）。

**关卡：** `capture/pr.json`、`capture/diff.patch`、`capture/extracted/tokens.json`、`capture/extracted/visible-text.txt` 和 `capture/extracted/people.json` 存在；您可以用一句话陈述 PR 的变更。`assets/<login>.png` 是尽力而为——其缺失不是失败。

---

## Step 2: Design System

目标：采纳代码编辑型帧预设；一个脚本将其转为此视频的 `frame.md` + 字幕皮肤。

风格固定为**代码编辑型**（暖编辑风格；为差异构建的海军蓝代码表面）。运行：

```bash
node <SKILL_DIR>/scripts/build-frame.mjs --preset code-editorial --hyperframes .
```

脚本复制代码编辑型预设的 `FRAME.md` → `frame.md`，将其重新混音到 `capture/extracted/tokens.json` 中的任何品牌令牌上（PR 没有 → `colors:[]`/`fonts:[]` 保持代码编辑型自身的调色板和字体，完整的设计），复制预设的字幕皮肤到 `.hyperframes/caption-skin.html`，并自验证（映射错误以退出码 1 退出）。它以退出码 0 退出后立即继续——不手动编辑。

**关卡：** `build-frame.mjs` 以退出码 0 退出——`frame.md` 由代码编辑型预设生成，且 `.hyperframes/caption-skin.html` 作为字幕皮肤源存在。

---

## Step 3: Storyboard and Script

目标：将 PR 转为经过批准的逐帧解释计划。

阅读 `../hyperframes-creative/references/story-spine.md`（钩子语言、先价值后证据、分镜作为提案、可溯源视觉）、`references/story-design.md`、`../hyperframes-animation/blueprints-index.md`、`../hyperframes/references/storyboard-format.md` 和 `../hyperframes/references/script-format.md`。使用它们编写 `STORYBOARD.md`，以及当需要叙述时编写 `SCRIPT.md`。从简报的 `length` 设置分镜前置元数据 `duration:`——粗略预期；组装报告其切点落在何处。

使用 `story-design.md` 作为 PR 原型（changelog / feature-reveal / fix-explainer / refactor-walkthrough）、PR 原生命帧类型、钩子、说服力、节拍、每帧字数预算和 credits 结尾。序列来自**叙事设计**，而非 diff 的文件顺序——解释变更，而非朗读 diff。作为**软指导**，参考 `../hyperframes-animation/blueprints-index.md` 中的角色→蓝图菜单：为每个节拍，按其候选蓝图暗示的形状撰写配音，并在适合的候选处标记 `blueprint:` id（故事真实决定了哪些节拍存在——永远不强制节拍适应形状）。Feature 2–4 个真实 diff 片段（来自 `capture/diff.patch`），每个是一个小且可读的代码片段；为每个想要帧内 `code-*` 块的节拍命名它。帧不携带除 credits 结尾（1–6 个 `assets/<login>.png` 头像）外的 `asset_candidates`。使用 storyboard 和脚本参考中要求的精确字段。

起草后，运行审查循环的计划通过——`../hyperframes/references/review-loop.md` § 1：以提案形式呈现计划，并询问两个问题——批准或变更，以及**草图优先**（推荐）或跳过。反馈以聊天回复到达；循环直到批准。这是**检查关卡**（简报契约 § 1）：在自主模式下没有要问的——发布相同的摘要作为提示，然后继续；草图坍缩为构建，唯一的一次预览问题在 Step 6。

**关卡：** `STORYBOARD.md` 存在，每个帧都有所需的叙事字段，`SCRIPT.md` 在需要叙述时存在，且用户批准了计划（自主模式：摘要已作为提示发布）。

---

## Step 3.1: Audio

目标：从批准的脚本生成叙述、词语计时、音乐和音频元数据。

在 Step 3 批准后开始音频。在后台运行它，然后继续 Step 4。

**在调用前从用户的请求中选择叙述声音。** 如果请求命名了声音、性别或语调，选择一个匹配的声音 id 并通过 `--voice <id>` 传递。否则，流水线默认为 **Marcia（女性）** 在 HeyGen / `am_michael` 在 Kokoro——因此，“男声”的请求除非传递标志会被静默忽略。声音 id 是提供商特定的；根据 Step 0 登录状态所选的提供商进行解析：**HeyGen**（已登录）通过 `node <MEDIA_DIR>/audio/scripts/heygen-tts.mjs --list`（或 `GET /v3/voices?engine=starfish`）；**Kokoro**（离线）通过 `<MEDIA_DIR>/audio/references/tts.md` 中的声音表（前缀 `am_`/`bm_` 为男声，`af_`/`bf_` 为女声）。当用户未表达偏好时，回退到简报契约 § 2 中的回忆声音，然后为流水线默认值，并说明使用了哪一个；仅当两者均未命名时才省略 `--voice`。当用户本次显式选择了声音时，记录它（`prefs.mjs record --key voice`）。

`node <SKILL_DIR>/scripts/audio.mjs --script ./SCRIPT.md --storyboard ./STORYBOARD.md --hyperframes . --out ./audio_meta.json --voice <voice-id> &`

音频脚本处理叙述、词语计时、从 HeyGen 音乐库查找 BGM 以及计时元数据。BGM 情绪来自分镜的 `music:` 字段。此使用 HeyGen 音频 API 进行检索，而非生成，并使用与 TTS 相同的 `~/.heygen` 凭证。对于提供商详情，阅读 `../media-use/audio/references/tts.md`。

如果没有叙述且无 `SCRIPT.md`，跳过语音生成。如果分镜有音乐情绪，BGM 仍可运行。

**标准的完全静音标记**（共享于重用此音频模型的工作流）：`music: none` 在 STORYBOARD.md 顶部 YAML 代码块中**且**无 `SCRIPT.md`。该组合标记项目静音——无叙述，无 BGM，无音效。`audio.mjs` 识别它并生成任何内容（它移除任何陈旧的 `audio_meta.json`；缺少 `audio_meta.json` 是 assemble 视为静音的），因此此步骤是干净的跳过。`music: none` 配合叙述保留 TTS 并仅关闭 BGM。使用完全相同的拼写——不要即兴其他标记。

**关卡：** 音频任务已开始，或项目标记为静音（`music: none` + 无 `SCRIPT.md`）。

---

## Step 4: Frame Visual Design

目标：为每个分镜帧添加视觉方向、布局意图和运动选择。

**首先绘制分镜图（仅协作模式）。** 计划获批的瞬间，运行草图通过——`../hyperframes/references/review-loop.md` § 2（不要等待 Step 3.1；草图不使用计时）：自行将每个帧作为 `storyboard.html` 中单元格的一个连接线框绘制（`../hyperframes-creative/references/storyboard-recipe.md` § 3），标记每个 `built`，当所有帧均为 `built` 时停顿于唯一布局问题，并仅修订命名的草图，直到分镜确认。替代物：对**代码节拍**，一个普通代码面板，包含文件名和少量真实 diff 行作为文本——`code-*` 块的连接线工作属于工人。然后才在确认的布局上撰写下方的视觉设计。在自主模式下，或当用户在 Step 3 选择跳过草图时，跳过此通过——帧在 Step 5 直接从 `outline` 到 `animated`。

在原地编辑 `STORYBOARD.md`。不要创建另一个分镜。使用 `frame.md` 作为颜色、类型、布局感觉和风格的真理来源。

阅读 `references/visual-design.md`、`../hyperframes-animation/blueprints-index.md`、`references/motion-language.md`、`references/code-vocabulary.md` 和 `../hyperframes-animation/rules-index.md`。使用 `visual-design.md` 作为方法（编码时间镜头序列、行内 Layout 词汇，以及代码节拍处理），外加所需的 `## Video direction` 块。使用 `../hyperframes-animation/blueprints-index.md` 为每个帧选择镜头形状。使用 `code-vocabulary.md` 为每个代码节拍选择正确的 `code-*` 块（diff = `code-diff`，refactor = `code-morph`，new code = `code-typing`，…）。使用 `motion-language.md`（运动词汇 + 运动教条）和 `../hyperframes-animation/rules-index.md`（有效规则名称）作为运动——不要发明运动或块/蓝图名称。

**在设计任何命名外观之前搜索实时目录。** `code-vocabulary.md` 覆盖代码节拍；它不覆盖其余部分。对于简报命名的每个其他外观、效果、处理或过渡——"CRT 扫描线"、"故障"、"胶片颗粒"、"闪烁扫光"、"彩带爆发"——运行 `npx hyperframes catalog --query "<the look, in plain English>" --json` 并在写入该外观到 `STORYBOARD.md` 之前阅读顶部结果。搜索无需任何安装：无项目、无先前 `add`、无账户。它从任何目录对整个托管注册表（约 400 个块和组件）进行排名。在此处命名您找到的块；Step 5 预安装分镜中提到的每个块。仅在搜索返回不合适的项后手工编写外观。

为每个帧，按 `visual-design.md` 的方法写入一个**带时间编码的镜头序列**到 `STORYBOARD.md`：为帧选择蓝图（或合成），用此帧的内容实例化它，并使每个 Scene 的显现节奏与配音一致，使帧在其整个持续时间内发展，而非先预加载再冻结。对**代码节拍**，`code-*` 块是帧的 `focal`，Scenes 编排代码编辑型代码表面周围的代码（文件/头部的进入、对 hunk 的镜头、落地行）——**而非**代码动画本身，后者由块拥有。在每个代码帧的字段之后立即添加一个 `### Source excerpt` 围栏 `diff` 块，仅包含工人必须渲染的确切真实 hunk（最大 12 行）。从 `capture/diff.patch` 此处选择它；工人被禁止重新打开该完整 diff。在此处声明布局和运动**内联**每个 Scene（词汇在 `visual-design.md` 和 `motion-language.md` 中）。添加一个全视频范围的 `## Video direction` 块。

不改变故事、脚本、`transition_in`、`asset_candidates` 或 PR 来源。此步骤不写 HTML。没有资产暂存步骤——唯一真实资源是 credits 头像，已在 `assets/` 中。

**关卡：** 每个帧都有一个时间编码镜头序列，其显现节奏与配音同步（无预加载）；代码帧命名 `code-*` 块作为 `focal`；`## Video direction` 存在。协作模式：草图表已确认。

---

## Step 5: Build Frames

目标：将每个分镜帧构建为 HTML 组合并组装可播放视频。

等待 Step 3.1 音频完成（如果音频已开始）。然后同步持续时间并获取音效；如果静音则两者都跳过。

`node <SKILL_DIR>/scripts/audio.mjs sync-durations --audio-meta ./audio_meta.json --storyboard ./STORYBOARD.md`

`node <SKILL_DIR>/scripts/audio.mjs fetch-sfx --storyboard ./STORYBOARD.md --hyperframes .`

持续时间同步是机械的：真实语音持续时间获胜；静音帧保持估计；永不手动编辑同步持续时间。

**在派发之前一次预安装注册表中的块**，分镜中提到的所有块，以便并行工人不在注册表上竞争：

`for b in <storyboard 中每个注册表块名>; do npx hyperframes add "$b"; done`

派发前，阅读 `../hyperframes/references/subagent-dispatch.md`。构建有界包和工人角色负载：

```bash
node <SKILL_DIR>/scripts/frame-packets.mjs --project "$PROJECT_DIR" --storyboard "$PROJECT_DIR/STORYBOARD.md"
```

包构建器在没有上游选择的 `### Source excerpt` 的代码帧上硬失败，并硬限制包字节。它还写入 `_role.md`（`../hyperframes/references/frame-worker-core.md` + 此技能的 `sub-agents/frame-worker.md`，逐字拼接——工人角色的完整文档）。在**最多三个工人总数**上派发，平衡于包路径；每个工人的提示携带 `_role.md` 及其分配的包路径——粘贴完整角色或手递其路径（等效；工人从这些文档开始）——每个工人可顺序构建多个分配帧，仅读取一次角色。工人只读取其包（），从不打开完整的 `STORYBOARD.md`、`capture/diff.patch` 或 `capture/extracted/visible-text.txt`。每个工人只写入其分配的 `compositions/frames/NN-*.html`；工人从不编辑 `STORYBOARD.md`。当帧有磁盘上的**确认草图**时（协作运行——审查循环 § 3），在派发上下文中说明：草图是现有的 `compositions/frames/NN-*.html`，工人为该布局打扮而非重绘它（frame-worker 核心 § When a confirmed sketch exists）。

对失败帧，**只重新派发该帧**，携带其现有包以及确切的验证器/规范发现。一次最大重试。不要重播整个批次，也绝不无具体发现而重试。

全屏背景使用 `class="clip"` 层，**从不**使用 `#root`。帧的地面（颜色字段/渐变/网格）是其自身全持续时间的背景剪辑——设置在 `#root` / `data-composition-id` 元素上的 `background` 被剪辑限制在帧窗口，并非可靠的地面，因此暗内容可以落在黑色宿主 `body` 上并渲染为不可见。视频的基础地面由组装器从 `frame.md` 的 `canvas` 颜色在索引 `#root` 上绘制。（完整规则 + 自检：`../hyperframes/references/frame-worker-core.md`。）

每个工人返回后，在 `STORYBOARD.md` 中将该帧标记为 `animated`。

在音频计时存在后，在后台构建字幕并组装索引：

`node <SKILL_DIR>/scripts/captions.mjs build --storyboard ./STORYBOARD.md --audio-meta ./audio_meta.json --hyperframes . --out ./caption_groups.json &`

`node <SKILL_DIR>/scripts/assemble-index.mjs --storyboard ./STORYBOARD.md --hyperframes .`

`captions.mjs` 使用项目的 `.hyperframes/caption-skin.html`（Step 2 中复制的代码编辑型的），从 `frame.md` 注入品牌令牌；`captions: skipped (<reason>)` 有效。`assemble-index.mjs` 将 `assets/` 中的 credits 头像作为幂等后备暂存。

**关卡：** 每个帧标记为 `animated`（协作模式：草图表在 Step 4 确认），`index.html` 存在，且字幕已构建或明确跳过。

---

## Step 6: Finalize

目标：验证组装的视频，获得用户批准，并渲染最终 MP4。

注入过渡，运行检查，暂停审查，然后渲染。

`node <SKILL_DIR>/scripts/transitions.mjs inject --storyboard ./STORYBOARD.md --hyperframes .`

`node <SKILL_DIR>/scripts/transitions.mjs verify --storyboard ./STORYBOARD.md --index ./index.html`

`npx hyperframes lint`

`npx hyperframes check`

`npx hyperframes snapshot --at <frame-midpoints>`

`snapshot` 将捕获的帧拼接为一个联系表（`snapshots/contact-sheet.jpg`）。浏览它；如果没有明显损坏，继续——不要在此停留。

如果命令失败，展示 stderr 并停止——不要堆叠恢复命令。自行修复：对 `compositions/frames/NN-*.html` 的最便宜安全编辑，然后重跑失败的检查。

**已知假阳性——不要追逐它。** `check` 可能在**字幕**高亮字上报告少量 `text_box_overflow` 错误，约 1-4px（选择器 `#caption-word-*` / `.caption-line`）。字幕药丸使用刻意紧致的 `line-height`（在 `scripts/captions.mjs` 中设置一次）且**无 `overflow:hidden`**，因此重显示字形的墨会溢出几 px 进入药丸自身的内边距——没有实际被裁剪。将其视为预期并继续。**不要**增大字幕 `line-height`（它会增大药丸，这更糟）。仅当 `text_box_overflow` 命名**帧**元素（`#el-NN-*`）时，才对 `text_box_overflow` 采取行动。

检查通过后，暂停用户审查——审查循环的最终查看（`../hyperframes/references/review-loop.md` § 4）：一个问题，关于最终 Studio 预览——现在渲染，还是有什么变化？（自主模式：预览或渲染后保持的那一个问题）：然后用以下命令打开预览。）然后在用户批准后交付 MP4 连同联系表和帧 id，以便修订可定位到单个帧。

预览：`npx hyperframes preview "$PROJECT_DIR" --background`

仅在用户批准后渲染（自主模式：预览或渲染问题后）：

`npx hyperframes render --skill=pr-to-video --quality high --output renders/video.mp4`

渲染后除非用户要求，否则不要重跑 `lint`、`check` 或 `snapshot`。

用户完成审查后（或在渲染且预期无更多实时编辑后），仅在此项目后台服务器上停止：`npx hyperframes preview "$PROJECT_DIR" --stop`。在等待审查时永远不要拆除它。

**关卡：** `lint` 和 `check` 通过，且快照在渲染前已被检查；用户在审查暂停处批准（自主模式：检查通过，且交付包含联系表）；`renders/video.mp4` 存在。最终回复陈述 MP4 路径和最终持续时间。

---

## Quick Reference

**格式：** 横屏 `1920x1080`；竖屏 `1080x1920`；方屏 `1080x1080`——从目标推导（简报契约 § 2）。在分镜前置元数据中一次设置格式。

**PR 增量 vs 捕获资产工作流：** 无 Step 1 捕获（`gh` CLI 将 PR 导入合成 `capture/extracted/` 包——`tokens.json` + `visible-text.txt` + `people.json`）；唯一真实资源是贡献者的 `assets/<login>.png` 头像（credits 结尾）；无 `asset-descriptions.md`，无资产暂存步骤。代码节拍由代码编辑型海军代码表面上的 `code-*` 注册表块渲染；风格始终为**代码编辑型**。

**背景脚本：** 该工作流在 `scripts/` 下携带这些：`fetch-pr`（PR → `capture/pr.json` + `diff.patch` 通过 `gh`；大型 PR 安全，无临时目录）、`ingest`（→ 合成捕获包；离线）、`fetch-people-avatars`（贡献者头像 → `assets/`）；外加共享引擎——`build-frame`（采纳 + 品牌重混预设为 `frame.md` + 字幕皮肤）、`audio`（TTS，BGM，SFX，持续时间同步）、`captions`、`transitions`（注入 + 验证），和 `assemble-index`。其余均为 `hyperframes` CLI。代码块通过 `npx hyperframes add <name>` 安装。

可复用、领域无关的镜头形状位于 `../hyperframes-animation/blueprints/`（索引于 `../hyperframes-animation/blueprints-index.md`）；`code-*` 注册表块是代码节拍词汇（`references/code-vocabulary.md`）。

| 阅读                                                                                                                                                        | 何时                                                                                                     |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| `[../hyperframes/references/brief-contract.md](../hyperframes/references/brief-contract.md)`                                                                | 关卡类型，从 `BRIEF.md` 推导模式，字段语义。                                            |
| `[../hyperframes-creative/references/story-spine.md](../hyperframes-creative/references/story-spine.md)`                                                    | Step 3：故事教义——钩子语言、先价值后证据、提案形状、可溯源视觉。 |
| `[references/story-design.md](references/story-design.md)`                                                                                                  | Step 3：规划 PR 解释。                                                                         |
| `[../hyperframes-animation/blueprints-index.md](../hyperframes-animation/blueprints-index.md)`                                                              | Step 3：角色→蓝图菜单。 Step 4：选择镜头形状。                                                |
| `[../hyperframes/references/storyboard-format.md](../hyperframes/references/storyboard-format.md)`                                                          | Step 3：编写 `STORYBOARD.md`。                                                                           |
| `[../hyperframes/references/script-format.md](../hyperframes/references/script-format.md)`                                                                  | Step 3：编写 `SCRIPT.md`。                                                                               |
| `[../media-use/audio/references/tts.md](../media-use/audio/references/tts.md)`                                                                              | Step 3.1：选择或理解 TTS 提供商。                                                            |
| `[references/visual-design.md](references/visual-design.md)`                                                                                                | Step 4：编写帧的镜头序列（+ Layout 词汇）。                                           |
| `[references/code-vocabulary.md](references/code-vocabulary.md)`                                                                                            | Step 4 + 5：为代码节拍选择并填充 `code-*` 块。                                              |
| `[references/motion-language.md](references/motion-language.md)`                                                                                             | Step 4：运动词汇 + 运动教条。                                                     |
| `[references/cut-catalog.md](references/cut-catalog.md)`                                                                                                    | Step 4-5：剪辑目录（工人构建帧内接缝）。                                                  |
| `[../hyperframes-animation/rules-index.md](../hyperframes-animation/rules-index.md)` + `[../hyperframes-animation/rules/](../hyperframes-animation/rules/)` | Step 5：所引用运动的本地规则配方正文。                                                  |
| `[../hyperframes/references/frame-worker-core.md](../hyperframes/references/frame-worker-core.md)`                                                          | Step 5：共享工人契约（包构建器将其前置到 delta）。                            |
| `[sub-agents/frame-worker.md](sub-agents/frame-worker.md)`                                                                                                  | Step 5：工作流的帧工人 delta。                                                               |
| `[../hyperframes/references/subagent-dispatch.md](../hyperframes/references/subagent-dispatch.md)`                                                          | Step 5：安全派发子代理。                                                                      |
| `[../hyperframes-creative/frame-presets/code-editorial/FRAME.md](../hyperframes-creative/frame-presets/code-editorial/FRAME.md)`                            | Step 2：代码编辑型预设（固定风格）。                                                         |
