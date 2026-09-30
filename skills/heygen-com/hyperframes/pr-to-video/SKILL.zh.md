---
name: pr-to-video
description: 将一个 GitHub 拉取请求（一个 PR URL、所有者/仓库#N，或已检出的仓库中的“这个 PR”）转换成一个代码变更解释视频——基于 diff、提交记录和文件构建的版本日志、功能展示、修复或重构过程：输入的是一个代码变更，而不是一个网站。不是产品推广（/product-launch-video）或无 PR 主题解释（/faceless-explainer）。不明确的情况→/hyperframes。
---

**插件安装：** 在设置或新鲜命令之前，当此技能位于 HyperFrames 插件内时，请遵循 [插件执行规则](../hyperframes/references/plugin-installation.md)。独立安装则保留以下更新说明。

> **首先，保持此技能新鲜——在运行前与用户确认：** `npx hyperframes skills update pr-to-video`。当一切正常时，这是一个快速的无操作；否则，它将在您依赖它们之前刷新此技能及其依赖的核心域技能。

> **media-use：** 在获取音频/图像/标志之前，调用 `/media-use` 来从 HeyGen 目录解析 BGM/SFX/图像，并从其官方来源获取品牌标志。首先运行 `--adopt` 以注册现有资源。参见 `/media-use` 技能。

# PR 到 HyperFrames

使用此技能摄取 GitHub 拉取请求，理解变更，规划代码变更解释，并在 HyperFrames 中逐帧构建。输入是一个 **代码变更**（通过 `gh` 读取），而不是一个网站——没有 **捕获步骤**，也没有除贡献者头像之外的**实际资源**。

> **入口点是 `/hyperframes`。** 您是协调者。运行每个步骤，验证其门控，然后才能继续。此技能用于一个 **GitHub 拉取请求**（代码变更）。任何其他意图，一个简单的“制作视频”，或任何不确定性 → 首先读取 `/hyperframes` — 意图层控制每条路线的决策，一个没有 `BRIEF.md` 的新鲜创建也会通过它（设置的开启规则）。

您是协调者。在解析的外部 `PROJECT_DIR` 中工作，默认情况下不在调用者的存储库中。按顺序运行步骤，并在继续之前通过每个门控。用户门控步骤是步骤 0、步骤 3 和步骤 6。在步骤 0 之前阅读 `../hyperframes/references/brief-contract.md` — 它定义了门控类型以及 `BRIEF.md` 的 `flow`/`storyboard` 如何导出控制步骤 3/4/6 门控的模式。除了步骤 5，您自己执行所有步骤，在步骤 5 中，您调度一个有界池的帧工作者。不要在这里放置设计或运动规则；那些存在于帧工作者子代理、此技能的本地 `../hyperframes-animation/rules/` + `../hyperframes-animation/blueprints/` 和 `hyperframes-creative`。

工作流：步骤 0 设置 → `hyperframes.json`；步骤 1 摄取 → `capture/extracted/` + `assets/<login>.png`；步骤 2 设计系统 → `frame.md`；步骤 3 故事板/脚本 → `STORYBOARD.md` 和 `SCRIPT.md`；步骤 3.1 音频 → `audio_meta.json`；步骤 4 视觉设计 → 丰富的 `STORYBOARD.md`；步骤 5 帧生成 → `compositions/frames/NN-*.html` 和 `index.html`；步骤 6 最终渲染 → `renders/video.mp4`。

---

## 步骤 0：设置

目标：带确认的简报进入——包括 **PR 参考**（完整的 URL、`<owner>/<repo>#<N>` 引用，或在签出存储库中为“此 PR”）——创建 HyperFrames 项目，并使简报持久化。风格始终是 **代码编辑**（在步骤 2 中固定，从不询问）。

**简报由意图层确认，而不是在此处提出问题。** 开启规则，按顺序：**(1)** `BRIEF.md` 存在 → 读取它并不要提问——简报已确定，其 `flow`/`storyboard` 导出模式（简报合同 § 1）。**(2)** 没有 `BRIEF.md` 但项目存在（`hyperframes.json` / 磁盘上的 `STORYBOARD.md`）→ 从故事板的 frontmatter 和记录的偏好中恢复；从不重新询问一个半构建的项目。**(3)** 都没有——一个直接到达此处的全新创建请求 → 读取 `/hyperframes` 并运行其意图层（`references/intent-interview.md`）：它检查配方和记忆的默认值，并执行此路线的问题——包括 PR 大小→长度原则，它完整地存在于 `../hyperframes/references/routes/pr-to-video.md` 中——然后返回锁定简报。编辑请求跳过所有这些——去执行编辑。

在执行任何其他工作之前解析项目目录。保留用户提供的项目目录；否则使用解析器打印的持久外部缓存位置。在调用者的存储库中**永不创建 `videos/`**：

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

能力预检在获取、故事工作、音频或帧调度之前运行。如果安装的 CLI 无法运行此技能所需的验证命令，请使用其升级说明停止，而不是首先花费运行上下文。

仅在 `$PROJECT_DIR/hyperframes.json` 缺失时初始化。其基本名称来自 PR，例如 `acme-sdk-pr-1842`；**永不使用工作区名称或时间戳**。

`npx hyperframes init "$PROJECT_DIR" --non-interactive --example=blank --skill=pr-to-video` — `init` 检查安装的技能与 GitHub 上的最新版本，如果任何技能过时，则更新全局集。

以下每个相对路径命令都以 `$PROJECT_DIR` 作为其工作目录。没有显式子壳的示例意味着 `(cd "$PROJECT_DIR" && …)`；**永不更改调用者的存储库的工作树**。

**立即在初始化后编写 `BRIEF.md`**（永远不会在之前——`init` 拒绝非空目录）：意图层的锁定简报，形状按 `../hyperframes/references/brief-format.md`。解析 `<MEDIA_DIR>` 作为安装的 `/media-use` 技能目录。然后使用 `node <MEDIA_DIR>/scripts/prefs.mjs record --hyperframes .` 记录每个偏好支持的答案（`brief-format.md` 命名了子集）。如果意图层采用了配方，运行 `node <MEDIA_DIR>/scripts/recipe.mjs use --hyperframes . --name <name>`；它将其 `frame.md` 复制到项目中（步骤 2 然后被跳过），并返回 Step 3 草稿的骨架。配方填充答案，而不是批准；审查门控仍然运行。

**在继续步骤 0 之后显示登录状态** — 运行 `npx hyperframes auth status` 并逐字转述其输出。它报告语音/BGM 将使用 HeyGen 还是本地引擎，并且在签出时，如何登录。应用一个分支：

- **协作式：** 等待用户登录或显式选择 `offline` / `go`。
- **自主式：** 报告状态并继续使用可用的本地引擎。

当没有离线提供者时，不要无声地省略所需功能；暴露阻止器。不要将此决策合并到其他问题或写入到每个存储库的 `.env` 中。Auth 所有权和离线回退：`/media-use` `references/setup-providers.md` § Providers。

**门控：** `hyperframes.json` 和 `BRIEF.md` 存在；PR 引用已捕获在简报中；偏好支持的答案已记录（简报合同 § 2）；已显示登录状态（已登录，或继续离线）。

---

## 步骤 1：摄取 PR（无捕获）

目标：获取 PR 的事实并将其作为信息来源折叠到项目中。**没有网站捕获**。`fetch-pr.mjs` 运行 `gh` 确定性地——通过分页 `gh api` 完成文件列表（因此大 PR 不会在 ~100 个文件处截断），并仅写入 `capture/pr.json` + `capture/diff.patch`（没有临时目录）。对于合并的 PR，它还解析一个最佳尝试的 `shipped_version` (+ `version_source`) 到 `pr.json`，以便结束卡片可以引用一个真实版本，而不是编造一个。然后 `ingest.mjs` 在离线状态下将它们折叠到合成捕获包中。

```bash
PR="<url | owner/repo#N | N>"

# 确定性地获取 PR：运行 gh，通过分页 gh api 完成文件列表（因此大 PR 不会在 ~100 个文件处截断），仅写入 capture/pr.json +
# capture/diff.patch — 没有临时目录。gh auth / not-found / private 错误在此处退出 1。
(cd "$PROJECT_DIR" && node <SKILL_DIR>/scripts/fetch-pr.mjs --pr "$PR" --out-dir ./capture)

# 离线转换 → capture/extracted/{tokens.json (colors:[] → 代码编辑调色板),
# visible-text.txt (简报), people.json (贡献者，机器人过滤，姓名+登录，
# avatarFile=assets/<login>.png)}。
(cd "$PROJECT_DIR" && node <SKILL_DIR>/scripts/ingest.mjs \
  --pr-json ./capture/pr.json --diff ./capture/diff.patch --out-dir ./capture/extracted)

# 人员的 front 的一个网络步骤——下载每个贡献者的 GitHub 头像到
# assets/<login>.png 以用于结束的信用。尽力而为；始终退出 0。
(cd "$PROJECT_DIR" && node <SKILL_DIR>/scripts/fetch-people-avatars.mjs \
  --people ./capture/extracted/people.json)
```

如果 `fetch-pr.mjs` 退出 1（gh auth / 未找到 / 私有），报告其 stderr 并停止——**不要编造 PR 内容**。如果 `ingest.mjs` 退出 1，读取其 stderr（通常是格式错误的 `pr.json`），修复，然后重新运行（确定性地）。`fetch-people-avatars.mjs` 始终退出 0；缺少头像意味着没有作者信用。

`people.json` 携带 `gh` 已经命名的贡献者的 `name`（PR 作者、提交作者、`mergedBy`）——`null` 对于其余的（审查者/评论者/分配者，`gh pr view` 只会给出一个简陋的 `login`）。在步骤 3 中写入信用关闭之前，您自己解析任何 `null` 名称，为实际出现在该帧中的 1-6 个人：`gh api users/<login> --jq .name`（您已经有了 `gh` — 无需脚本此操作）。如果 GitHub 对该用户没有公开名称，则回退到屏幕上的登录名，并从语音行中删除那个人（参见 story-design.md 的信用部分——旁白必须说出名称，永远不会说原始句柄）。

**门控：** `capture/pr.json`、`capture/diff.patch`、`capture/extracted/tokens.json`、`capture/extracted/visible-text.txt` 和 `capture/extracted/people.json` 存在；您可以一句话清晰地陈述 PR 的变更。`assets/<login>.png` 是尽力而为的——它的缺失不是失败。

---

## 步骤 2：设计系统

目标：采用代码编辑的帧预设；一个脚本将其转换为此视频的 `frame.md` + 标题皮肤。

风格是固定的——**代码编辑**（温暖的编辑；为差异构建的海军代码表面）。运行：

```bash
node <SKILL_DIR>/scripts/build-frame.mjs --preset code-editorial --hyperframes .
```

脚本复制代码编辑的预设的 `FRAME.md` → `frame.md`，将其与 `capture/extracted/tokens.json` 中的任何品牌标记混合（PR 没有标记 → `colors:[]`/`fonts:[]` 保持代码编辑自己的调色板，一个完整的设计），将预设的标题皮肤复制到 `.hyperframes/caption-skin.html`，并自我验证（在映射损坏时退出 1）。一旦它退出 0 就继续——无需手动编辑。

**门控：** `build-frame.mjs` 退出 0 — `frame.md` 存在于代码编辑的预设中，并且 `.hyperframes/caption-skin.html` 存在作为标题皮肤源。

---

## 步骤 3：Storyboard 和 Script

目标：将 PR 转换为批准的逐帧解释计划。

阅读 `../hyperframes-creative/references/story-spine.md`（钩语言、证据先于价值、Storyboard 作为提案、来源可追溯的视觉效果）、`references/story-design.md`、`../hyperframes-animation/blueprints-index.md`、`../hyperframes/references/storyboard-format.md` 和 `../hyperframes/references/script-format.md`。使用它们来编写 `STORYBOARD.md`，并在需要旁白时编写 `SCRIPT.md`。从简报的 `length` 设置 frontmatter `duration:` — 一个粗略的预期；组装报告将剪辑位置与它对比。

使用 `story-design.md` 来处理 PR 架构（变更日志 / 功能揭示 / 修复解释 / 重构逐步指南），PR 本地帧类型、钩子、说服力、节拍、每帧的单词预算，以及信用关闭。序列来自 **叙事设计，而不是差异的文件顺序**——解释变更，而不是大声朗读差异。作为一个 **软指南**，参考 `../hyperframes-animation/blueprints-index.md` 中的角色→蓝图菜单：对于每个节拍，根据其候选蓝图暗示的形状编写旁白，并在适合时标记候选 `blueprint:` id（故事真相仍然决定哪些节拍存在——永远不要强迫节拍适应形状）。功能 2–4 个真实的差异 hunks（来自 `capture/diff.patch`），每个都是一个可读的小片段；命名每个 `code-*` 块每个都希望在帧的 `scene` 中。帧不携带 `asset_candidates`，除了 `credits` 关闭（1–6 `assets/<login>.png` 头像）。使用来自 storyboard 和 script 参考的精确所需字段。

起草后，运行审查循环的计划通过——`../hyperframes/references/review-loop.md` § 1：将计划作为提案提出，并询问两个问题——批准或更改，以及 **草图优先**（推荐）或跳过。反馈作为聊天回复到达；循环直到批准。这是一个 **检查点门控**（简报合同 § 1）：在自主模式下没有要询问的——发布相同的摘要作为通知并继续；草图合并到构建中，并且一个预览问题在步骤 6 来。

**门控：** `STORYBOARD.md` 存在，每个帧都有所需的叙事字段，`SCRIPT.md` 存在当需要旁白时，并且用户批准了计划（自主：摘要被发布为通知）。

---

## 步骤 3.1：音频

目标：从批准的脚本生成旁白、单词时间、音乐和音频元数据。

在步骤 3 批准后开始音频。在后台运行它，然后继续到步骤 4。

**从用户在调用之前选择旁白声音。** 如果请求命名了一个声音、性别或语调，选择一个匹配的声音 id 并与 `--voice <id>` 一起传递。管道默认是否则 **Marcia（女性）** 在 HeyGen / `am_michael` 在 Kokoro 上——因此像“男性声音”这样的请求在没有传递标志的情况下会被无声忽略。声音 id 是提供者特定的；针对步骤 0 的登录状态选择的提供者解析：**HeyGen**（已登录）通过 `node <MEDIA_DIR>/audio/scripts/heygen-tts.mjs --list`（或 `GET /v3/voices?engine=starfish`）；**Kokoro**（离线）通过 `<MEDIA_DIR>/audio/references/tts.md` 中的声音表（前缀 `am_`/`bm_` 男性，`af_`/`bf_` 女性）。当用户没有表达偏好时，回退到记忆中的声音（简报合同 § 2）然后是管道默认值，并说明您使用了哪个；仅在两者都没有命名时才省略 `--voice`。当用户在此运行中明确选择了一个声音时，记录它（`prefs.mjs record --key voice`）。

`node <SKILL_DIR>/scripts/audio.mjs --script ./SCRIPT.md --storyboard ./STORYBOARD.md --hyperframes . --out ./audio_meta.json --voice <voice-id> &`

音频脚本处理旁白、单词时间、从 HeyGen 的音乐库中查找 BGM，以及时间元数据。BGM 情绪来自故事板的 `music:` 字段。这使用 HeyGen 音频 API 进行检索，而不是生成，并使用与 TTS 相同的 `~/.heygen` 凭证。有关提供者详细信息，请阅读 `../media-use/audio/references/tts.md`。

如果没有旁白且没有 `SCRIPT.md`，则跳过语音生成。如果故事板有音乐情绪，BGM 可能仍然运行。

**标准的完全静音标记**（跨重用此音频模型的流程共享）：STORYBOARD.md 顶部 YAML 块中的 `music: none` **和**没有 `SCRIPT.md`。这种组合将项目标记为静音——没有旁白，没有 BGM，没有 SFX。`audio.mjs` 识别它并生成 nothing（它删除任何陈旧的 `audio_meta.json`；缺席的 `audio_meta.json` 是组装将其视为静音的东西），因此此步骤是一个干净的跳过。`music: none` 与旁白一起保留 TTS 并关闭 BGM。使用确切的拼写——不要即兴其他标记。

**门控：** 音频作业已开始，或者项目被标记为静音（`music: none` + 没有 `SCRIPT.md`）。

---

## 步骤 4：帧视觉设计

目标：为每个故事板帧添加视觉方向、布局意图和运动选择。

**首先绘制故事板页面（仅限协作）。** 一旦计划获得批准，立即进行草图绘制流程——`../hyperframes/references/review-loop.md` § 2（不要等待步骤 3.1；草图不使用时间轴）：将每个帧作为 `storyboard.html` 的单元格（`../hyperframes-creative/references/storyboard-recipe.md` § 3）自己绘制线框图，标记每个 `built`，在每帧标记为 `built` 时暂停一个布局问题，并仅修订命名为确认的故事板页面。替身：对于**代码片段**，一个纯代码面板，包含文件名和一些真实的 diff 行作为文本——`code-*` 块的接线属于工作人员。只有在确认的布局下方才绘制视觉设计。在自主模式下，或当用户选择在步骤 3 跳过草图时，跳过此流程——帧直接从 `outline` 到 `animated` 在步骤 5。

就地编辑 `STORYBOARD.md`。不要创建另一个故事板。使用 `frame.md` 作为颜色、类型、布局感觉和样式的真实来源。

阅读 `references/visual-design.md`、`../hyperframes-animation/blueprints-index.md`、`references/motion-language.md`、`references/code-vocabulary.md` 和 `../hyperframes-animation/rules-index.md`。使用 `visual-design.md` 作为方法（时间编码的镜头序列、内联布局词汇和代码片段处理），以及所需的 `## 视频方向` 块。使用 `../hyperframes-animation/blueprints-index.md` 选择每个帧的镜头形状。使用 `code-vocabulary.md` 选择每个代码片段的正确 `code-*` 块（diff = `code-diff`，重构 = `code-morph`，新代码 = `code-typing`，…）。使用 `motion-language.md`（运动词汇 + 运动准则）和 `../hyperframes-animation/rules-index.md`（有效规则名称）用于运动——不要发明运动或块/蓝图名称。

**在您设计任何命名外观之前，先搜索实时目录。** `code-vocabulary.md` 涵盖代码片段；它不涵盖其他内容。对于其他外观、效果、处理或过渡，简要命名——"CRT 扫描线"、"故障"、"胶片颗粒"、"闪烁扫描"、"五彩纸屑爆炸"——运行 `npx hyperframes catalog --query "<用普通英语描述的外观>" --json` 并在将此外观写入 `STORYBOARD.md` 之前阅读顶部结果。搜索不需要**安装任何内容**：没有项目、没有先前的 `add`、没有账户。它从任何目录对托管注册表（~400 个块和组件）进行排名。在此处命名您找到的块；步骤 5 预装故事板命名的每个块。只有在搜索返回不匹配的内容后，才手动编写外观。

对于每个帧，根据 `visual-design.md` 的方法在 `STORYBOARD.md` 中编写**时间编码的镜头序列**：选择帧的蓝图（或组合），用此帧的内容实例化它，并调整每个场景的揭示速度以匹配旁白，以便帧在其完整持续时间中发展，而不是前加载然后冻结。**对于代码片段，`code-*` 块是帧的 `focal`**，场景编排周围的代码编辑器界面（文件的入口/头部、相机对准代码块、着陆行）——**不是**代码动画本身，该动画属于块。在每个代码帧的字段后立即添加一个 `### 源代码片段` 围栏 `diff` 块，其中只包含工作人员必须渲染的确切代码块（最多 12 行）。从 `capture/diff.patch` 中选择它；工作人员被禁止重新打开完整的 diff。按场景**内联**声明布局和运动（`visual-design.md` 和 `motion-language.md` 中的词汇表）。添加一个视频范围的 `## 视频方向` 块。

不要更改故事、脚本、`transition_in`、`asset_candidates` 或 PR 源。在此步骤中不要编写 HTML。没有**资产预装步骤**——唯一的真实资产是已存在于 `assets/` 中的信用头像。

**门禁：** 每个帧都有一个时间编码的镜头序列，其揭示速度与旁白匹配（没有前加载）；代码帧将 `code-*` 块命名为 `focal`；存在 `## 视频方向` 块。协作：草图页面已确认。

---

## 步骤 5：构建帧

目标：将每个故事板帧作为 HTML 组合构建，并组装可播放视频。

如果已启动音频，则等待步骤 3.1 音频完成。然后同步持续时间并获取 SFX；如果无声则跳过两者。

```bash
node <SKILL_DIR>/scripts/audio.mjs sync-durations --audio-meta ./audio_meta.json --storyboard ./STORYBOARD.md
```

```bash
node <SKILL_DIR>/scripts/audio.mjs fetch-sfx --storyboard ./STORYBOARD.md --hyperframes .
```

持续时间同步是机械的：实际旁白持续时间获胜；静音帧保持估计；永远不要手动编辑同步后的持续时间。

**预装注册表块**，在分发前一次性命名 `STORYBOARD.md` 中的块，以便并行工作人员不会在注册表中竞争：

```bash
for b in <storyboard 中命名的每个注册表块>; do npx hyperframes add "$b"; done
```

分发前，阅读 `../hyperframes/references/subagent-dispatch.md`。构建有界数据包和工作者角色有效负载：

```bash
node <SKILL_DIR>/scripts/frame-packets.mjs --project "$PROJECT_DIR" --storyboard "$PROJECT_DIR/STORYBOARD.md"
```

数据包构建器在没有上游选择的 `### 源代码片段` 的代码帧时会硬失败，并硬限制数据包字节数。它还写入 `_role.md`（`../hyperframes/references/frame-worker-core.md` + 此技能的 `sub-agents/frame-worker.md`，按原样连接——完整的工人角色）。最多分发**三个工作者**，在数据包路径上平衡；每个工作者的提示包含 `_role.md` 和其分配的数据包路径——完整粘贴角色或手动粘贴其路径（等效；工作者从完全相同的文档开始）——每个工作者可以按顺序构建分配的多个帧，只读取一次角色。工作者只读取其数据包和 `frame.md`。他们永远不会打开完整的 `STORYBOARD.md`、`capture/diff.patch` 或 `capture/extracted/visible-text.txt`。每个工作者只写入其分配的 `compositions/frames/NN-*.html`；工作者永远不会编辑 `STORYBOARD.md`。当帧在磁盘上具有**确认的草图**（协作运行——审查循环 § 3）时，在工作者分发上下文中说明：草图是现有的 `compositions/frames/NN-*.html`，工作者装饰该布局而不是重新绘制它（frame-worker 核心 § 当存在确认的草图时）。

对于失败的帧，重新分发**该帧**，加上其现有数据包以及确切的验证器/检查查找。最多重试一次。不要重播整个批次，也不要在没有具体查找的情况下重试。

**全出血背景始终位于 `class="clip"` 层上，而不是 `#root`。** 帧的地面（颜色字段/渐变/网格）是其自己的全持续时间背景剪辑——在 `#root` / `data-composition-id` 元素上设置的 `background` 被剪辑限制在帧的窗口中，并且不是可靠的地面，因此深色内容可以落在黑色主机 `body` 上并渲染不可见。视频的基础地面由组装器从 `frame.md` 的 `canvas` 颜色绘制到索引 `#root`。（完整规则 + 自检：`../hyperframes/references/frame-worker-core.md`。）

每当一个工作者返回时，在 `STORYBOARD.md` 中将该帧标记为 `animated`。

在音频时间存在后，在背景中构建字幕并组装索引：

```bash
node <SKILL_DIR>/scripts/captions.mjs build --storyboard ./STORYBOARD.md --audio-meta ./audio_meta.json --hyperframes . --out ./caption_groups.json &
```

```bash
node <SKILL_DIR>/scripts/assemble-index.mjs --storyboard ./STORYBOARD.md --hyperframes .
```

`captions.mjs` 使用项目的 `.hyperframes/caption-skin.html`（代码编辑器的，在步骤 2 中复制），注入来自 `frame.md` 的品牌标记；`captions: skipped (<reason>)` 是有效的。`assemble-index.mjs` 将信用头像从 `assets/` 预装为 idempotent 的后备。

**门禁：** 每个帧都被标记为 `animated`（协作：步骤 4 中确认了草图），`index.html` 存在，并且字幕已构建或明确跳过。

---

## 步骤 6：最终确认

目标：验证组装的视频，获取用户批准，并渲染最终 MP4。

注入过渡，运行检查，暂停审查，然后渲染。

```bash
node <SKILL_DIR>/scripts/transitions.mjs inject --storyboard ./STORYBOARD.md --hyperframes .
```

```bash
node <SKILL_DIR>/scripts/transitions.mjs verify --storyboard ./STORYBOARD.md --index ./index.html
```

```bash
npx hyperframes lint
```

```bash
npx hyperframes check
```

```bash
npx hyperframes snapshot --at <frame-midpoints>
```

`snapshot` 将捕获的帧拼接成一个接触片 (`snapshots/contact-sheet.jpg`)。快速查看它；如果没有什么明显损坏，继续前进——不要在此处停留。

如果命令失败，显示 stderr 并停止——不要堆叠恢复命令。自己修复它：对 `compositions/frames/NN-*.html` 进行最安全的编辑，然后重新运行失败的检查。

**已知的误报——不要追查它。** `check` 可能会报告一些 `text_box_overflow` 错误，约 1–4px 在**字幕**高亮单词上（选择器 `#caption-word-*` / `.caption-line`）。字幕药丸使用故意紧凑的 `line-height`（在 `scripts/captions.mjs` 中设置一次）并且**没有 `overflow:hidden`**，因此重型显示字形的墨水会溢出几 px 到药丸自己的填充中——实际上没有剪切。将这些视为预期值并继续。**不要**增加字幕的 `line-height`（它会使药丸膨胀，这更糟）。只有在 `text_box_overflow` 命名**帧**元素（`#el-NN-*`）时才采取行动，而不是字幕单词。

检查通过后，暂停用户审查——审查循环的最终外观（`../hyperframes/references/review-loop.md` § 4）：一个问题，在最终 Studio 预览上——现在渲染，还是有什么变化？（自主：保留的问题，预览优先还是渲染——使用以下命令在“是”的情况下预览预览。）然后交付 MP4、接触片和帧 ID，以便修订可以针对单个帧。

预览：`npx hyperframes preview "$PROJECT_DIR" --background`

只有在用户批准后（自主模式：在预览或渲染问题后）才渲染：

```bash
npx hyperframes render --skill=pr-to-video --quality high --output renders/video.mp4
```

渲染后不要重新运行 `lint`、`check` 或 `snapshot`，除非用户要求。

在用户审查完成（或渲染后，如果没有更多实时编辑预期）后，停止**仅此项目**的背景服务器：`npx hyperframes preview "$PROJECT_DIR" --stop`。在等待审查期间**永远不要**将其拆除。

**门禁：** `lint` 和 `check` 通过，并且在渲染前检查了快照；用户在审查暂停时批准（自主：检查通过，交付包括接触片）；`renders/video.mp4` 存在。最终回复声明 MP4 路径和最终持续时间。

---

## 快速参考

**格式：** 横屏 `1920x1080`；竖屏 `1080x1920`；方形 `1080x1080`——源自目的地（简要合同 § 2）。在故事板 frontmatter 中一次性设置格式。

**PR 差异与捕获资产工作流：** 没有 Step 1 捕获（`gh` CLI 将 PR 消化到合成 `capture/extracted/` 包中——`tokens.json` + `visible-text.txt` + `people.json`）；唯一的真实资产是贡献者的 `assets/<login>.png` 头像（信用结束）；没有 `asset-descriptions.md`，没有资产预装步骤。代码片段由 `code-*` 注册表块在代码编辑器的海军代码表面渲染；风格始终是**代码编辑器**。

**背景脚本：** 工作流在 `scripts/` 下提供这些：`fetch-pr`（PR → `capture/pr.json` + `diff.patch` 通过 `gh`；安全的大 PR，无草稿）、`ingest`（→ 合成捕获包；离线）、`fetch-people-avatars`（贡献者头像 → `assets/`）；以及共享引擎——`build-frame`（采用 + 品牌混合预设到 `frame.md` + 字幕皮肤）、`audio`（TTS、BGM、SFX、持续时间同步）、`captions`、`transitions`（注入 + 验证）、`assemble-index`。其他所有内容都是 `hyperframes` CLI。代码块通过 `npx hyperframes add <name>` 安装。

可重用、领域无关的镜头形状位于 `../hyperframes-animation/blueprints/`（由 `../hyperframes-animation/blueprints-index.md` 索引）；`code-*` 注册表块是代码片段词汇（`references/code-vocabulary.md`）。

| 阅读                                                                                                                                                        | 时间                                                                                                     |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| `[../hyperframes/references/brief-contract.md](../hyperframes/references/brief-contract.md)`                                                                | 门类型、从 `BRIEF.md` 推导模式、字段语义。                                            |
| `[../hyperframes-creative/references/story-spine.md](../hyperframes-creative/references/story-spine.md)`                                                    | 第 3 步：故事教义 — 钩子语言、证据前置、提案形状、可追溯来源的视觉效果。 |
| `[references/story-design.md](references/story-design.md)`                                                                                                  | 第 3 步：规划 PR 解释。                                                                         |
| `[../hyperframes-animation/blueprints-index.md](../hyperframes-animation/blueprints-index.md)`                                                              | 第 3 步：角色→蓝图菜单。第 4 步：选择镜头形状。                                                |
| `[../hyperframes/references/storyboard-format.md](../hyperframes/references/storyboard-format.md)`                                                          | 第 3 步：编写 `STORYBOARD.md`。                                                                           |
| `[../hyperframes/references/script-format.md](../hyperframes/references/script-format.md)`                                                                  | 第 3 步：编写 `SCRIPT.md`。                                                                               |
| `[../media-use/audio/references/tts.md](../media-use/audio/references/tts.md)`                                                                              | 第 3.1 步：选择或理解 TTS 提供商。                                                            |
| `[references/visual-design.md](references/visual-design.md)`                                                                                                | 第 4 步：编写帧的镜头序列 (+ 布局词汇)。                                           |
| `[references/code-vocabulary.md](references/code-vocabulary.md)`                                                                                            | 第 4 + 5 步：选择并填充 `code-*` 块以用于代码片段。                                              |
| `[references/motion-language.md](references/motion-language.md)`                                                                                            | 第 4 步：运动词汇 + 运动教义。                                                     |
| `[references/cut-catalog.md](references/cut-catalog.md)`                                                                                                    | 第 4-5 步：剪辑目录（工作者在帧内构建接缝）。                                            |
| `[../hyperframes-animation/rules-index.md](../hyperframes-animation/rules-index.md)` + `[../hyperframes-animation/rules/](../hyperframes-animation/rules/)` | 第 5 步：引用运动的本地规则配方主体。                                                  |
| `[../hyperframes/references/frame-worker-core.md](../hyperframes/references/frame-worker-core.md)`                                                          | 第 5 步：共享工作合同（数据包构建器将其添加到增量之前）。                            |
| `[sub-agents/frame-worker.md](sub-agents/frame-worker.md)`                                                                                                  | 第 5 步：工作流的帧工作增量。                                                               |
| `[../hyperframes/references/subagent-dispatch.md](../hyperframes/references/subagent-dispatch.md)`                                                          | 第 5 步：安全地调度子代理。                                                                      |
| `[../hyperframes-creative/frame-presets/code-editorial/FRAME.md](../hyperframes-creative/frame-presets/code-editorial/FRAME.md)`                            | 第 2 步：代码编辑预设（固定样式）。                                                         |
