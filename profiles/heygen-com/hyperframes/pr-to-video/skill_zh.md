> **首先保持此技能新鲜——在运行前与用户确认：** `npx hyperframes skills update pr-to-video`。当一切都是最新时，这是一个快速的无操作；否则，在您依赖它们之前，将刷新此技能及其依赖的核心域技能。

> **media-use**：在获取音频/图像/标志之前，调用 `/media-use` 来从 HeyGen 目录解析背景音乐/SFX/图像，并从其官方来源获取品牌标志。首先运行 `--adopt` 以注册现有资产。参见 `/media-use` 技能。

# PR 到 HyperFrames

使用此技能来摄取 GitHub 拉取请求，理解更改，计划代码更改解释，并在 HyperFrames 中逐帧构建。输入是一个**代码更改**（通过 `gh` 读取），而不是一个网站——没有**捕获步骤**和**实际资产**，除了贡献者的头像。

> **正门是 `/hyperframes`。** 您是协调者。运行每个步骤，验证其门控，然后才能继续。此技能适用于**GitHub 拉取请求**（代码更改）。任何其他意图、一个简单的“制作视频”，或任何不确定性 → 首先阅读 `/hyperframes` — 意图层拥有每条路线的决策，一个没有 `BRIEF.md` 的新创建也会通过它（Setup 的开篇规则）。

您是协调者。在解析的外部 `PROJECT_DIR` 中工作，默认情况下不在调用存储库中。按顺序运行步骤，并在继续之前通过每个门控。用户门控步骤是 Step 0、Step 3 和 Step 6。在 Step 0 之前阅读 `../hyperframes/references/brief-contract.md` — 它定义了门控类型以及 `BRIEF.md` 的 `flow`/`storyboard` 如何导出管理 Step 3/4/6 门控的模式。除了 Step 5，您自己执行所有步骤，在 Step 5 中，您调度一个有界的帧工作者池。不要在这里放置设计或运动规则；那些存在于帧工作者子代理、此技能的本地 `../hyperframes-animation/rules/` + `../hyperframes-animation/blueprints/` 和 `hyperframes-creative`。

工作流：Step 0 设置 → `hyperframes.json`；Step 1 摄取 → `capture/extracted/` + `assets/<login>.png`；Step 2 设计系统 → `frame.md`；Step 3 故事板/脚本 → `STORYBOARD.md` 和 `SCRIPT.md`；Step 3.1 音频 → `audio_meta.json`；Step 4 视觉设计 → 丰富的 `STORYBOARD.md`；Step 5 帧 → `compositions/frames/NN-*.html` 和 `index.html`；Step 6 最终渲染 → `renders/video.mp4`。

---

## Step 0: 设置

目标：带有确认的简报进入——包括**PR 参考**（完整的 URL、`<owner>/<repo>#<N>` 引用，或在签出存储库中为“此 PR”）——创建 HyperFrames 项目，并使简报持久化。风格始终是**代码编辑**（在 Step 2 中固定，永不询问）。

**简报由意图层确认，而不是在此处提出问题。** 开篇规则，按顺序：**(1)** `BRIEF.md` 存在 → 读取它并不要任何东西——简报已确定，其 `flow`/`storyboard` 导出模式（简报合同 § 1）。**(2)** 没有 `BRIEF.md` 但项目存在 (`hyperframes.json` / 磁盘上的 `STORYBOARD.md`) → 从故事板的 frontmatter 和记录的偏好中恢复；永不重新询问一个半建成的项目。**(3)** 既不是——一个直接到达此处的全新创建请求 → 阅读 `/hyperframes` 并运行其意图层 (`references/intent-interview.md`)：它检查配方和记住的默认值，并执行此路线的问题——包括 PR 大小→长度原则，它完整地存在于 `../hyperframes/references/routes/pr-to-video.md` 中——然后返回锁定简报。编辑请求跳过所有这些——去执行编辑。

在执行任何其他工作之前解决项目目录。保留用户提供的项目目录；否则使用持久的外部缓存位置，由解析器打印。在调用存储库中永不创建 `videos/`：

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

能力预检在获取、故事工作、音频或帧调度之前运行。如果安装的 CLI 无法运行此技能所需的验证命令，则与其升级说明一起停止，而不是首先花费运行上下文。

仅在 `$PROJECT_DIR/hyperframes.json` 缺失时初始化。其基本名来自 PR，例如 `acme-sdk-pr-1842`；永不使用工作区名称或时间戳。

`npx hyperframes init "$PROJECT_DIR" --non-interactive --example=blank --skill=pr-to-video` — `init` 检查安装的技能与 GitHub 上的最新版本，如果任何技能过时，则更新全局集。

下面的每个相对路径命令都以 `$PROJECT_DIR` 作为其工作目录。没有明确子壳的示例意味着 `(cd "$PROJECT_DIR" && …)`；永不更改调用存储库的工作树。

**立即在 init 后编写 `BRIEF.md`**（永不提前——`init` 拒绝非空目录）：意图层的锁定简报，形状按 `../hyperframes/references/brief-format.md`。解析 `<MEDIA_DIR>` 作为安装的 `/media-use` 技能目录。然后使用 `node <MEDIA_DIR>/scripts/prefs.mjs record --hyperframes .` 记录每个偏好支持的答案（`brief-format.md` 指定子集）。如果意图层采用了配方，运行 `node <MEDIA_DIR>/scripts/recipe.mjs use --hyperframes . --name <name>`；它将其 `frame.md` 复制到项目中（Step 2 然后被跳过），并返回其 Step 3 草稿的骨架。配方填充答案，而不是批准；审查门控仍然运行。

**在继续 Setup 之前显示登录状态** — 运行 `npx hyperframes auth status` 并逐字转发其输出。它报告语音/BGM 将使用 HeyGen 还是本地引擎，并且在注销时，如何登录。应用一个分支：

- **协作式**：等待用户登录或明确选择 `offline` / `go`。
- **自主式**：声明状态并继续使用可用的本地引擎。

当没有离线提供者时，不要无声地省略所需的能力；显示阻止器。不要将此决策合并到另一个问题中，或写入到每个存储库的 `.env` 中。Auth 所有权和离线回退：`/media-use` `references/setup-providers.md` § 提供者。

**门控**：`hyperframes.json` 和 `BRIEF.md` 存在；PR 引用在简报中捕获；偏好支持的答案被记录（简报合同 § 2）；显示登录状态（已登录，或继续离线）。

---

## Step 1: 摄取 PR（无捕获）

目标：获取 PR 的事实并将其作为信息来源折叠到项目中。没有**网站捕获**。`fetch-pr.mjs` 运行 `gh` 确定性地——通过分页的 `gh api` 完成文件列表，以便大型 PR 不会在 ~100 个文件处截断，并且仅写入 `capture/pr.json` + `capture/diff.patch`（没有临时目录）。对于已合并的 PR，它还解析一个最佳尝试的 `shipped_version` (+ `version_source`) 到 `pr.json`，以便结束卡片可以引用一个真实版本，而不是编造一个。然后 `ingest.mjs` 在离线状态下将那折叠到合成捕获包中。

```bash
PR="<url | owner/repo#N | N>"

# 确定性地获取 PR：运行 gh，通过分页 gh api 完成文件列表（因此大型 PR 不会在 ~100 个文件处截断），仅写入 capture/pr.json + capture/diff.patch — 没有临时目录。gh auth / not-found / private 错误在此处退出 1。
(cd "$PROJECT_DIR" && node <SKILL_DIR>/scripts/fetch-pr.mjs --pr "$PR" --out-dir ./capture)

# 离线转换 → capture/extracted/{tokens.json (colors:[] → 代码编辑调色板), visible-text.txt (简报), people.json (贡献者，机器人过滤，姓名+登录，avatarFile=assets/<login>.png)}.
(cd "$PROJECT_DIR" && node <SKILL_DIR>/scripts/ingest.mjs \
  --pr-json ./capture/pr.json --diff ./capture/diff.patch --out-dir ./capture/extracted)

# 人员的 front 的一个网络步骤——下载每个贡献者的 GitHub 头像到 assets/<login>.png 以供 credits close。尽力而为；始终退出 0。
(cd "$PROJECT_DIR" && node <SKILL_DIR>/scripts/fetch-people-avatars.mjs \
  --people ./capture/extracted/people.json)
```

如果 `fetch-pr.mjs` 退出 1（gh auth / not found / private），报告其 stderr 并停止——**不要编造 PR 内容**。如果 `ingest.mjs` 退出 1，读取其 stderr（通常是格式错误的 `pr.json`），修复，然后重新运行（确定性地）。`fetch-people-avatars.mjs` 始终退出 0；缺少头像意味着没有 credits close 到作者。

`people.json` 携带 `gh` 已经命名的贡献者的 `name`（PR 作者、提交作者、`mergedBy`）——其余的 `null`（审查者/评论者/分配者，`gh pr view` 只会给出一个简单的 `login`）。在 Step 3 写入 credits close 之前，您自己解决任何 `null` 名称，为实际出现在该帧中的 1-6 个人：`gh api users/<login> --jq .name`（您已经有了 `gh` —— 无需脚本化此内容）。如果 GitHub 没有为该用户提供公共名称，则回退到屏幕上的登录名，并从口头行中删除该人员（参见 story-design.md 的 credits 部分——旁白必须说名称，而不是原始句柄）。

**门控**：`capture/pr.json`、`capture/diff.patch`、`capture/extracted/tokens.json`、`capture/extracted/visible-text.txt` 和 `capture/extracted/people.json` 存在；您可以一句话清晰地陈述 PR 的更改。`assets/<login>.png` 是尽力而为——其缺失不是失败。

---

## Step 2: 设计系统

目标：采用代码编辑帧预设；一个脚本将其转换为此视频的 `frame.md` + 标题皮肤。

风格是固定的——**代码编辑**（温暖的编辑；为差异构建的海军代码表面）。运行：

```bash
node <SKILL_DIR>/scripts/build-frame.mjs --preset code-editorial --hyperframes .
```

风格是固定的——**代码编辑**（温暖的编辑；为差异构建的海军代码表面）。运行：

```bash
node <SKILL_DIR>/scripts/build-frame.mjs --preset code-editorial --hyperframes .
```

脚本复制代码编辑预设的 `FRAME.md` → `frame.md`，将其与 `capture/extracted/tokens.json` 中的任何品牌标记混合（PR 没有这些 → `colors:[]`/`fonts:[]` 保持代码编辑自己的调色板，一个完整的设计），将预设的标题皮肤复制到 `.hyperframes/caption-skin.html`，并自我验证（在映射损坏时退出 1）。一旦它退出 0 就继续——无需手动编辑。

**门控**：`build-frame.mjs` 退出 0 — `frame.md` 存在于代码编辑预设中，并且 `.hyperframes/caption-skin.html` 作为标题皮肤源存在。

---

## Step 3: 故事板和脚本

目标：将 PR 转换为批准的逐帧解释计划。

阅读 `../hyperframes-creative/references/story-spine.md`（钩语言、价值优先于证据、故事板作为提案、来源可追溯的视觉效果）、`references/story-design.md`、`../hyperframes-animation/blueprints-index.md`、`../hyperframes/references/storyboard-format.md` 和 `../hyperframes/references/script-format.md`。使用它们来编写 `STORYBOARD.md`，当需要旁白时，编写 `SCRIPT.md`。从简报的 `length` 设置 frontmatter `duration:`——一个粗略的预期；组装报告将切割与它的位置。

使用 `story-design.md` 来获取 PR 架构（变更日志 / 功能揭示 / 修复解释 / 重构演练），PR 本地帧类型，钩子，说服力，节拍，每个帧的字预算，以及 credits close。序列来自**叙事设计，而不是差异的文件顺序**——解释更改，不要朗读差异。作为一个**软指南**，参考 `../hyperframes-animation/blueprints-index.md` 中的角色→蓝图菜单：对于每个节拍，编写其候选蓝图暗示的旁白，并标记该候选 `blueprint:` ID 当它适用时（故事真相仍然决定哪些节拍存在——永不强迫节拍适应形状）。功能 2–4 个真实的差异 hunks（来自 `capture/diff.patch`），每个都是一个可读的小片段；为每个帧的 `scene` 指定每个想要在帧中的 `code-*` 块。帧不携带 `asset_candidates`，除了 `credits` close（1–6 `assets/<login>.png` 头像）。使用故事板和脚本参考中要求的精确字段。

起草后，运行审查循环的计划通过——`../hyperframes/references/review-loop.md` § 1：将计划作为提案呈现，并提出两个问题——批准或更改，以及**草图优先**（推荐）或跳过。反馈作为聊天回复到达；循环直到批准。这是一个**检查点门控**（简报合同 § 1）：在自主模式下没有要询问的——发布相同的摘要作为提示并继续；草图折叠到构建中，并且一个预览问题在 Step 6 来。

**门控**：`STORYBOARD.md` 存在，每个帧都有所需的叙事字段，`SCRIPT.md` 存在当需要旁白时，并且用户批准了计划（自主：检查通过并且交付包括接触表单）。

---

## Step 3.1: 音频

目标：从批准的脚本生成旁白、字计时、音乐和音频元数据。

在 Step 3 批准后开始音频。在后台运行它，然后继续到 Step 4。

**从用户在调用之前选择旁白声音。** 如果请求命名了一个声音，性别或语调，选择一个匹配的声音 ID 并将其与 `--voice <id>` 一起传递。管道默认是否则 **Marcia (女性)** 在 HeyGen / `am_michael` 在 Kokoro — 因此像“一个男性声音”这样的请求在没有传递标志的情况下会被无声忽略。声音 ID 是提供者特定的；根据 Step 0 的登录状态选择的提供者：**HeyGen**（已登录）通过 `node <MEDIA_DIR>/audio/scripts/heygen-tts.mjs --list`（或 `GET /v3/voices?engine=starfish`）；**Kokoro**（离线）通过 `<MEDIA_DIR>/audio/references/tts.md` 中的声音表（前缀 `am_`/`bm_` 男性，`af_`/`bf_` 女性）。当用户没有表达偏好时，在管道默认之前回退到记住的声音（简报合同 § 2），并说明您使用了哪个；仅当两者都没有命名一个声音时才省略 `--voice`。当用户在此运行中明确选择了一个声音时，记录它 (`prefs.mjs record --key voice`)。

`node <SKILL_DIR>/scripts/audio.mjs --script ./SCRIPT.md --storyboard ./STORYBOARD.md --hyperframes . --out ./audio_meta.json --voice <voice-id> &`

音频脚本处理旁白、字计时、从 HeyGen 的音乐库获取 BGM，以及时间计时元数据。BGM 情绪来自故事板的 `music:` 字段。这使用 HeyGen 音频 API 进行检索，而不是生成，并且使用与 TTS 相同的 `~/.heygen` 凭证。对于提供者详细信息，请阅读 `../media-use/audio/references/tts.md`。

如果没有旁白且没有 `SCRIPT.md`，则跳过声音生成。BGM 可能仍然运行如果故事板有一个音乐情绪。

**标准的完全静音标记**（跨重用此音频模型的多个工作流共享）：`music: none` 在 STORYBOARD.md 顶部 YAML 块 **并且** 没有 `SCRIPT.md`。这种组合将项目标记为静音——没有旁白，没有 BGM，没有 SFX。`audio.mjs` 认识它并生成 nothing（它删除任何陈旧的 `audio_meta.json`；缺少 `audio_meta.json` 是组装将其视为静音的方式），因此此步骤是一个干净的跳过。`music: none` 与旁白一起保留 TTS 并关闭 BGM。使用确切的拼写——不要即兴其他标记。

**门控**：音频作业已开始，或者项目被标记为静音 (`music: none` + 没有 `SCRIPT.md`)。

---

## Step 4: 帧视觉设计

目标：为每个故事板帧添加视觉方向、布局意图和运动选择。

**首先绘制故事板表单（仅限协作式）。** 一旦计划被批准，运行草图通过——`../hyperframes/references/review-loop.md` § 2（不要等待 Step 3.1；草图不使用计时）：将每个帧作为 `storyboard.html` 的单元格（`../hyperframes-creative/references/storyboard-recipe.md` § 3）自己绘制，标记每个 `built`，在所有帧都是 `built` 时暂停一个布局问题，并修订仅被命名的草图。替身：对于**代码节拍**，一个普通的代码面板，带有文件名和一些真实的差异行作为文本——`code-*` 块的接线属于工作者。立即在代码帧的字段之后添加一个 `### Source excerpt` 分隔的 `diff` 块，其中仅包含工作者必须渲染的确切真实 hunks（最多 12 行）。从 `capture/diff.patch` 选择它；工作者被禁止重新打开完整的 diff。按场景**直接**添加布局和运动（词汇表在 `visual-design.md` 和 `motion-language.md`）。添加一个视频范围的 `## Video direction` 块。

不要更改故事、脚本、`transition_in`、`asset_candidates` 或 PR 来源。不要在此步骤中编写 HTML。没有**资产暂存步骤**——唯一的真实资产是 credits 头像，已经在 `assets/` 中。

**门控**：每个帧都有一个时间编码的拍摄序列，其揭示与旁白同步（没有前加载）；代码帧将 `code-*` 块命名为 `focal`；`## Video direction` 存在。协作式：草图表单在 Step 4 被确认。

---

## Step 5: 构建帧

目标：将每个故事板帧构建为 HTML 组合，并组装可播放的视频。

如果启动了音频，则等待 Step 3.1 音频完成。然后同步持续时间并获取 SFX；如果静音，则跳过两者。

`node <SKILL_DIR>/scripts/audio.mjs sync-durations --audio-meta ./audio_meta.json --storyboard ./STORYBOARD.md`

`node <SKILL_DIR>/scripts/audio.mjs fetch-sfx --storyboard ./STORYBOARD.md --hyperframes .`

持续时间同步是机械的：真实语音持续时间获胜；静音帧保留估计；永不手动编辑同步持续时间。

**预安装注册表块** 一次，在调度之前，以便并行工作者不会在注册表中竞争：

`for b in <故事板中命名的每个注册表块>; do npx hyperframes add "$b"; done`

在调度之前，阅读 `../hyperframes/references/subagent-dispatch.md`。构建有界的数据包和工作者角色有效负载：

```bash
node <SKILL_DIR>/scripts/frame-packets.mjs --project "$PROJECT_DIR" --storyboard "$PROJECT_DIR/STORYBOARD.md"
```

数据包构建器在没有上游选择的 `### Source excerpt` 的代码帧时硬失败，并且硬限制数据包字节数。它还写入 `_role.md` (`../hyperframes/references/frame-worker-core.md` + 此技能的 `sub-agents/frame-worker.md`, 逐字连接——完整的工人角色)。最多调度**三个工作者**，在数据包路径之间平衡；每个工作者的提示都携带 `_role.md` 和其分配的数据包路径——完整地粘贴角色或手动粘贴其路径（等效；工作者从完全相同的文档开始）。工作者只读取其数据包(s) 和 `frame.md`。它们永远不会打开完整的 `STORYBOARD.md`、`capture/diff.patch` 或 `capture/extracted/visible-text.txt`。每个工作者只写入其分配的 `compositions/frames/NN-*.html`；工作者永远不会编辑 `STORYBOARD.md`。当帧在磁盘上有一个**确认的草图**（协作运行——审查循环 § 3），在该工作者的调度上下文中说明这一点：草图是现有的 `compositions/frames/NN-*.html`，并且工作者为该布局添加样式而不是重新绘制它（frame-worker core § 当存在确认的草图时）。

在失败的帧中，仅重新调度**该帧**，将其现有数据包加上确切的验证/检查找到。最多重试一次。不要重播整个批次，并且不要在没有具体找到的情况下重试。

**全出血背景依赖于 `class="clip"` 层，而不是 `#root`。** 帧的地面（颜色字段 / 渐变 / 网格）是其自己的全持续时间背景剪辑——在 `#root` / `data-composition-id` 元素上设置的 `background` 被限制在帧的窗口中，因此深色内容可以落在黑色主机 `body` 上并渲染不可见。视频的基础地面由组装从 `frame.md` 的 `canvas` 颜色绘制到索引 `#root`。 （完整规则 + 自检：`../hyperframes/references/frame-worker-core.md`。）

每个工作者返回后，在 `STORYBOARD.md` 中将该帧标记为 `animated`。

在音频计时存在后，在后台构建标题，并组装索引：

`node <SKILL_DIR>/scripts/captions.mjs build --storyboard ./STORYBOARD.md --audio-meta ./audio_meta.json --hyperframes . --out ./caption_groups.json &`

`node <SKILL_DIR>/scripts/assemble-index.mjs --storyboard ./STORYBOARD.md --hyperframes .`

`captions.mjs` 使用项目的 `.hyperframes/caption-skin.html`（代码编辑的，在 Step 2 中复制），注入品牌标记来自 `frame.md`；`captions: skipped (<reason>)` 是有效的。`assemble-index.mjs` 将 credits 头像从 `assets/` 作为 idempotent 后备进行暂存。

**门控**：每个帧都被标记为 `animated`（协作式：在 Step 4 中确认了草图表单），`index.html` 存在，标题已构建或明确跳过。

---

## Step 6: 最终化

目标：验证组装的视频，获取用户批准，并渲染最终的 MP4。

注入过渡，运行检查，暂停审查，然后渲染。

`node <SKILL_DIR>/scripts/transitions.mjs inject --storyboard ./STORYBOARD.md --hyperframes .`

`node <SKILL_DIR>/scripts/transitions.mjs verify --storyboard ./STORYBOARD.md --index ./index.html`

`npx hyperframes lint`

`npx hyperframes check`

`npx hyperframes snapshot --at <frame-midpoints>`

`snapshot` 将捕获的帧拼接成一个接触表 (`snapshots/contact-sheet.jpg`)。快速查看它；如果没有什么明显损坏的，继续——不要在这里停留。

如果命令失败，显示 stderr 并停止——不要堆叠恢复命令。自己修复它：对 `compositions/frames/NN-*.html` 的最安全的编辑，然后重新运行失败的检查。

**已知的误报——不要追逐它。** `check` 可能报告一些 `text_box_overflow` 错误，大约 1–4px 在**标题**高亮单词上（选择器 `#caption-word-*` / `.caption-line`）。标题药丸使用故意紧凑的 `line-height`（在 `scripts/captions.mjs` 中设置一次）并且**没有 `overflow:hidden`**，因此一个沉重的显示字体的墨水会溢出到药丸自己的填充中——实际上没有剪切。将这些视为预期并继续。**不要**增加标题的 `line-height`（它会使药丸膨胀，这更糟）。仅在 `text_box_overflow` 指定一个**帧**元素 (`#el-NN-*`)，而不是标题单词时才采取行动。

检查通过后，暂停用户审查——审查循环的最终外观 (`../hyperframes/references/review-loop.md` § 4)：一个问题，在最终 Studio 预览上——现在渲染，或者需要哪些更改？（自主：一个问题，预览优先还是渲染——在“是”的情况下打开预览）。然后交付 MP4 与接触表单和帧 ID，以便修订可以针对单个帧。

预览：`npx hyperframes preview "$PROJECT_DIR" --background`

仅在使用用户批准后（自主模式：在预览或渲染问题后）渲染：

`npx hyperframes render --skill=pr-to-video --quality high --output renders/video.mp4`

渲染后不要重新运行 `lint`、`check` 或 `snapshot` 除非用户要求。

在用户完成审查后（或渲染后如果没有更多实时编辑预期），仅停止此项目的后台服务器：`npx hyperframes preview "$PROJECT_DIR" --stop`。在等待审查时，永不拆除它。

**门控**：`lint` 和 `check` 通过，并且在渲染之前检查了快照；用户在审查暂停时批准（自主：检查通过并且交付包括接触表单）；`renders/video.mp4` 存在。最终回复声明 MP4 路径和最终持续时间。

---

## 快速参考

**格式**：横向 `1920x1080`；纵向 `1080x1920`；方形 `1080x1080` — 源自目标（简报合同 § 2）。在故事板的 frontmatter 中设置一次。

**PR 差异与捕获资产工作流对比**：没有 Step 1 捕获（`gh` CLI 将 PR 摄取到合成 `capture/extracted/` 包中——`tokens.json` + `visible-text.txt` + `people.json`）；唯一的真实资产是贡献者的 `assets/<login>.png` 头像（credits close）；没有 `asset-descriptions.md`，没有资产暂存步骤。代码节拍由 `code-*` 注册表块在代码编辑的海军代码表面上渲染；风格始终是**代码编辑**。

**后台脚本**：工作流在 `scripts/` 下提供这些：`fetch-pr`（PR → `capture/pr.json` + `diff.patch` 通过 `gh`；安全的大 PR，没有临时目录），`ingest`（→ 合成捕获包；离线），和 `fetch-people-avatars`（贡献者头像 → `assets/`）；以及共享引擎——`build-frame`（采用 + 品牌混合预设到 `frame.md` + 标题皮肤），`audio`（TTS、BGM、SFX、持续时间同步），`captions`，`transitions`（注入 + 验证），和 `assemble-index`。其他所有内容都是 `hyperframes` CLI。代码块通过 `npx hyperframes add <name>` 安装。

可重用、与域无关的拍摄形状存在于 `../hyperframes-animation/blueprints/`（通过 `../hyperframes-animation/blueprints-index.md` 索引）；`code-*` 注册表块是代码节拍词汇（`references/code-vocabulary.md`）。
