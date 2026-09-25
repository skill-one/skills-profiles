> **首先，保持此技能的新鲜度——运行前请与用户确认：** `npx hyperframes skills update music-to-video`。如果所有内容都已是最新，这是一个快速的无操作；否则，它在您依赖它之前会刷新此技能和其所依赖的核心领域技能。

# music-to-video — 一个音乐锚定、节拍同步的视频工作流

使用此技能将一个**音乐音轨**转化为节拍同步的 HyperFrames 视频。您分析音轨一次，规划帧布局，填写逐帧计划，并为每帧构建一个合成。输入是一个音乐音轨以及可选的用户图片或视频——**无旁白，无网站捕获**。排版和模板是基础（完整视频需要零资源）；用户提供的任何媒体都在同一节拍网格上裁剪。

您是**编排者**。在 `videos/<项目>/` 中工作。按顺序执行步骤，并在前往下一步前通过每个**关卡（Gate）**。需要用户参与的两个步骤是：**第 3 步**（计划批准）和 **第 6 步**（渲染批准）——两者均为 `../hyperframes/references/brief-contract.md`（在第 0 步之前阅读它）中的检查关卡：在自主模式下，以提醒形式发布摘要并继续，而不是等待。除 **第 4 步** 外，您亲自执行所有步骤，第 4 步中您为每帧派发**一个子代理**。将设计和运动规则保留在此文件中——它们位于 `references/` 和 `frame-worker` 子代理中。

`SKILL_DIR` = 此技能目录。`PROJECT_DIR` = `videos/<项目名称>/`。

工作流：第 0 步设置 → `hyperframes.json` + `assets/bgm.mp3`；第 1 步分析 → `audiomap.json`；第 2 步骨架 → `STORYBOARD.md`（帧，组 `TBD`）；第 3 步计划 → 完成 `STORYBOARD.md` + `frame.md`；第 4 步构建 → `compositions/frames/NN-*.html`；第 5 步组装 → `index.html`；第 6 步渲染 → `renders/video.mp4`。

## 塑造一切的两种思路

- **一个分析器，信任它。** `analyze-beatgrid.py` 是**唯一**的节拍分析器——永远不要用其他工具或凭耳朵重新测量节拍。它读取音轨一次并写入 `audiomap.json`：能量阶段（级别 / 密度 / 感觉）、 onset + `onset_rate`、rolls、silences、`hard_stops`、`key_moments`、phrases、tempo / grid，以及 `audio.duration_sec`。它是确定性的——相同的文件总是给出相同的地图。大多数字段在任何音乐上都是可靠的；`bpm` 和 `beats_sec` 只有在音乐确实有节奏时才可靠，判断此情况是第 2 步中的决定。
- **一帧 = 一个文件；组包含在内。** 第 2 步将音轨切割为**帧**，每帧变成一个由单个 frame-worker 构建的合成文件 `compositions/frames/NN-<frame_id>.html`。一帧可以细分为**组**（每个是模板或运动原语组合）。额外密度放入**组内部**，所以**帧数反映不同的处理，而非节拍**——快节奏不会增加子代理的数量。

---

## 第 0 步：设置、BGM 和输入

目标：建立音乐源，创建 HyperFrames 项目，并记录任何用户提供的媒体。

**简报从意图层开始。** 开头规则：**(1)** `BRIEF.md` 存在 → 阅读它，若其可回答的问题就无需再问——其 `flow`/`storyboard` 推导模式（简报契约 § 1）。**(2)** 没有 `BRIEF.md` 但项目存在 → 从磁盘上的内容恢复；永不重新询问。**(3)** 直接到达此处的全新创建请求 → 阅读 `/hyperframes` 并运行其意图层（`references/intent-interview.md`）：它确认此路由的必需项（音乐源、目的地 → 宽高比 — `../hyperframes/references/routes/music-to-video.md`）并宣布哪些内容保持延后——品牌和类型在第 3 步由设计选择。初始化后立即编写 `BRIEF.md`（永不之前——`init` 拒绝非空目录），并记录偏好答案（`brief-format.md`）。编辑请求跳过所有这些步骤。

**音乐是脊柱**——在任何东西之前先建立一条音轨。此技能为**快速、高能量 BGM** 调优：强节拍网格驱动切割（平静的音轨可用，但按短语而非节拍调速）。如果用户提供了音频——音乐文件，或从中提取音频的视频——使用它。否则根据请求选择情绪并通过 `/media-use`（`references/bgm.md`）生成音轨。在首次执行认证提供程序操作之前，运行 `npx hyperframes auth status` 并逐字传达其输出。如果未登录，应用一个分支：

- **协作式：** 等待登录或明确选择离线继续使用本地提供程序。
- **自主式：** 说明状态并通过可用本地提供程序继续。

如果没有离线提供程序能满足所需音乐能力，则指出阻塞问题。永不将密钥写入每个仓库的 `.env`。认证所有权和离线回退位于 `/media-use` `references/setup-providers.md` § 提供程序。 resulting track lands at `assets/bgm.mp3`。暂存提供的图片或视频，以便帧可在节拍网格上使用它们；否则由排版承载视频。

**歌词视频：** 对于与人声同步的歌词，通过 `/media-use` 转写音轨获取词/行 timing，或询问用户歌词文本并在节拍网格上放置行。

仅在 `hyperframes.json` 缺失时初始化。从简报中用 kebab-case 命名 `<项目>`，例如 `midnight-drive-loop`——永不使用时间戳。`init` 检查已安装的技能和 GitHub 上的最新版本，若有任何过时则更新全局集。

```bash
npx hyperframes init "videos/<项目>" --non-interactive --example=blank --skill=music-to-video
mkdir -p "$PROJECT_DIR/assets" "$PROJECT_DIR/renders"
cp "<用户音乐>" "$PROJECT_DIR/assets/bgm.mp3"   # 如果需要，先从视频中提取
# 仅当用户提供了图片/视频时：
node <SKILL_DIR>/scripts/stage-assets.mjs --from <dir> --hyperframes "$PROJECT_DIR" --into public
```

**品牌**（字体 + 调色板）在第 3 步选择，不在这里。不要预先选择类型或音轨类型——资产只是可选配料，类型从逐帧选择中涌现。

**关卡：** `hyperframes.json` + `assets/bgm.mp3` 存在；宽高比 / 长度 / fps 以及（如有）资产清单已记录。

---

## 第 1 步：分析音乐

目标：产生整个视频构建所依赖的单一规范 timing 分析。

`analyze-beatgrid.py` 是**唯一**的节拍分析器——永远不要用其他工具或凭耳朵重新测量节拍。它读取音轨一次并写入 `audiomap.json`：能量阶段（level / density / feel）、 onset + `onset_rate`、rolls、silences、`hard_stops`、`key_moments`、phrases、tempo / grid，以及 `audio.duration_sec`。它是确定性的——相同的文件总是给出相同的地图。大多数字段在任何音乐上都是可靠的；`bpm` 和 `beats_sec` 只有在音乐确实有节奏时才可靠，判断此情况是第 2 步中的决定。

前提：Python 3 有 `librosa`、`numpy` 和 `soundfile`。如果导入失败，在安装这些依赖到活动 Python 环境之前运行分析器：

```bash
python3 -m pip install librosa numpy soundfile
```

```bash
python3 <SKILL_DIR>/scripts/analyze-beatgrid.py "$PROJECT_DIR/assets/bgm.mp3" \
  -o "$PROJECT_DIR/audiomap.json" --print
```

**关卡：** `audiomap.json` 存在；`audio.duration_sec` 已知。

---

## 第 2 步：帧骨架（仅结构）

目标：阅读音乐并规划帧——`STORYBOARD.md` 的骨架。

阅读 [`references/frame-skeleton.md`](references/frame-skeleton.md)。自行将 `audiomap.json` 转为 `STORYBOARD.md` 的**骨架**——没有中间 JSON。在真实的音乐变化处将音轨切割为**帧**（`hard_stops`、SURGE / DROP `key_moments`、roll 的边界、无 onset 的拉伸、大的能量跳跃），将每个边界吸附到 audiomap 锚点。为每帧设置 `span_sec`、`pacing`（第 1 步信任判定的结果——当网格真实时为 `beat_cut`，当平静音乐上强加节拍器时为 `phrase_flow`）、`mood` 和一行 `feel`（第 3 步匹配模板时所对应的普通音乐情境）。此处仅进行分类和规划布局：保留每帧的 `### Groups` 为 `TBD (Step 3)` 和 frontmatter 的 `style` 留空——无模板、副本、颜色或字体。预期 ~1–6 帧。

**关卡：** 帧铺满音轨（首帧在 0，末帧在 `duration_s`）；每帧携带 `span_sec` + `pacing` + `mood` + `feel`；每个 `### Groups` 为 `TBD`；无内容。

---

## 第 3 步：填写计划（用户关卡）

目标：将骨架转化为经批准、完整的 `STORYBOARD.md`。

阅读 [`references/planning.md`](references/planning.md)、[`storyboard-format.md`](references/storyboard-format.md)、[`template-catalog.md`](references/template-catalog.md)、[`motion-primitive-catalog.md`](references/motion-primitive-catalog.md) 和 [`montage.md`](references/montage.md)（仅当用户提供了资产时）。原地编辑同一文件，做两件事：

1. **选择品牌。** 从 `../hyperframes-creative/frame-presets/` 使用 [`../hyperframes-creative/references/design-spec.md`](../hyperframes-creative/references/design-spec.md) 中的表格选择一个预设（匹配音轨情绪；**仅其字体和颜色重要**——模板拥有合成）。复制到 `frame.md` **原样**，并填写 frontmatter 的 `style`（字体 + 一个 ≤4–6 色板调色板）来自它。
2. **填写每帧。** 决定其组并给出每个的处理：匹配的目录模板（带受限参数和真实 audiomap 锚点）、来自原语目录的自由组合，或遵守 `pacing` 的资产处理。**在自由组合一个命名外观之前，搜索其实时目录：** 对于用户要求的所有外观、效果、处理或过渡——"CRT 扫描线"、"glitch"、"胶片颗粒"、"shimmer sweep"——运行 `npx hyperframes catalog --query "<该外观，用普通英语描述>" --json` 并阅读顶部结果。`template-catalog.md` 和 `motion-primitive-catalog.md` 仅列出本技能自身的本地材料；搜索排名整个托管注册表（~400 块和组件）且**无需安装任何东西**——无项目、无先前 `add`、无账户。仅在搜索返回不合适的材料后才自由组合外观。编写文案。您拥有 **WHAT**（模板 / 原语 + 内容 + 锚点）；frame-worker 拥有 **HOW**——**永不**在故事板上写入毫秒级补间。

```bash
node <SKILL_DIR>/scripts/validate-plan.mjs --storyboard "$PROJECT_DIR/STORYBOARD.md" \
  --audiomap "$PROJECT_DIR/audiomap.json" --templates <SKILL_DIR>/references/templates
```

修复每个 `✗`（硬错误：时长不匹配、帧未铺满音轨、缺失 `src`）；警告为尽力而为。然后向用户展示逐帧摘要并迭代，直到他们批准。在自主模式下这是检查关卡：以提醒形式发布摘要并继续（`validate-plan.mjs` 通过仍是质量关卡并会阻塞）。

**关卡：** `frame.md` 是预设的原样副本；`validate-plan.mjs` 退出 0；用户批准计划（自主：摘要作为提醒发布）。

---

## 第 4 步：从计划构建帧

目标：将每帧构建为自包含的合成文件。

创建 `compositions/frames/`。阅读 [`sub-agents/frame-worker.md`](sub-agents/frame-worker.md) 和 `../hyperframes/references/subagent-dispatch.md`。为每帧派发**一个 frame-worker**，在可能时并行（否则分批）。每个 worker 恰好接收一帧和此上下文：

```text
PROJECT_DIR: <绝对路径>
frame_id: <NN-frame_id>              # = 帧文件茎，如 02-f2；合成 id
Your block: PROJECT_DIR/STORYBOARD.md 中的 `## Frame N — <frame_id>` 块
audiomap: PROJECT_DIR/audiomap.json
frame.md: PROJECT_DIR/frame.md
Materials: 对每个组，<SKILL_DIR>/references/templates/<id>/index.html（模板）和
           <SKILL_DIR>/references/motion-primitives/<id>/（自由）；暂存的 assets/（资产组）
Contracts: ../hyperframes-core/references/sub-compositions.md + determinism-rules.md
Canvas: <w>×<h>   Pacing: <beat_cut|phrase_flow>
Write to: PROJECT_DIR/compositions/frames/<frame_id>.html
```

对应该帧的 worker fork 引用的材料，将所有锚点转换为帧本地秒（`local_t = track_t − span_sec[0]`），用 0ms 切割门控其组，并写入一个 seek 安全的帧文件。**worker 永不运行 `hyperframes` CLI**——那些命令在已组装的项目上操作，而该项目尚未存在，所以它们会报告错误的文件。worker 只写入契约并停止；您在组装（第 6 步）后验证。每个 worker 返回时，您可以确认其文件已落地。

**关卡：** 每个帧都有其 `compositions/frames/NN-*.html` 落地。

---

## 第 5 步：组装

目标：将构建的帧 + BGM 连接到可播放的 `index.html`。

`assemble-index.mjs` 是确定性的——无子代理，无判断。它引用每个帧文件以其累积的 `data-start`，将 `assets/bgm.mp3` 挂载在轨道 11 上，并硬切割帧 → 帧（帧铺满音轨无间隙，所以有**无转场注入器**）。

```bash
node <SKILL_DIR>/scripts/assemble-index.mjs --storyboard "$PROJECT_DIR/STORYBOARD.md" \
  --hyperframes "$PROJECT_DIR" --audiomap "$PROJECT_DIR/audiomap.json"
```

修复它报告的任何 `✗`——缺少或空白的帧文件意味着该 worker 写了部分文件；重新派发（第 4 步）并重新组装。

**关卡：** `index.html` 存在；总时长 == `audiomap.audio.duration_sec`。

---

## 第 6 步：验证和渲染

目标：验证已组装视频，获取用户批准，并渲染最终 MP4。

在**已组装项目**上运行 CLI——那是正确的单元（逐帧 worker 无法运行它）。`check` 在一次运行中执行结构 lint 和无头浏览器运行时、布局、运动、对比度关卡；`--snapshots` 还输出审查帧。

```bash
( cd "$PROJECT_DIR" && npx hyperframes check . --snapshots )
```

在 `t=0`、每个帧起始、最强的 DROP / SURGE、每个 `hard_stops[].t` 和末帧检查。失败时，自己进行**最廉价的稳妥修复**：编辑有问题的 `compositions/frames/NN-*.html`。永不通过更改时长或音频 timing 来掩盖同步问题。一旦关卡通过，暂停等待用户审查，然后仅在批准后渲染（自主模式：询问保留的一个问题——"先预览，还是渲染？"——然后交付含联系表的 MP4）：

```bash
( cd "$PROJECT_DIR" && npx hyperframes render . --skill=music-to-video -q draft -o renders/video.mp4 --fps 30 )
```

**关卡：** `check` 通过且快照已检查；用户批准（自主：检查通过且交付含联系表）；`renders/video.mp4` 存在且有音频，时长 == `audiomap.audio.duration_sec`。最终回复说明 MP4 路径和时长。

---

## 恢复表

| 您有                 | 继续从       |
| --------------------- | ------------- |
| 仅 `assets/bgm.mp3`  | 第 1 步       |
| `audiomap.json`      | 第 2 步       |
| `STORYBOARD.md`（骨架） | 第 3 步       |
| `STORYBOARD.md`（完整） | 第 4 步       |
| 所有帧文件             | 第 5 步       |
| `index.html`         | 第 6 步       |

## 快速参考

**格式：** 默认为横屏 `1920x1080`；竖屏 `1080x1920`；方屏 `1080x1080`。在故事板 frontmatter 中（`canvas: { w, h, fps }`）一次性设置画布。

`scripts/` 下的脚本：`analyze-beatgrid.py`（唯一分析器）、`validate-plan.mjs`（计划检查）、`assemble-index.mjs`（索引组装）、`stage-assets.mjs`（暂存用户媒体）、`lib/storyboard.mjs`（内置解析器）。其他均为 `hyperframes` CLI。

| 读取                                                                                         | 当                                       |
| ------------------------------------------------------------------------------------------- | ---------------------------------------- |
| [`references/frame-skeleton.md`](references/frame-skeleton.md)                                  | 第 2 步：读音乐，规划帧，设置 pacing |
| [`references/planning.md`](references/planning.md) · [`storyboard-format.md`](references/storyboard-format.md) | 第 3 步：选择品牌，填写每帧，编写计划 |
| [`references/template-catalog.md`](references/template-catalog.md)                                  | 第 3 步：为每组选择模板 |
| [`references/motion-primitive-catalog.md`](references/motion-primitive-catalog.md)                        | 第 3 步 / 第 4 步：自由组合的 L0 配方 |
| [`references/montage.md`](references/montage.md)                                                  | 第 3 步 / 第 4 步：资产处理（beat-cut / ken-burns） |
| [`sub-agents/frame-worker.md`](sub-agents/frame-worker.md)                                              | 第 4 步：派发 + 构建一帧 |
| `../hyperframes/references/subagent-dispatch.md`                                                      | 第 4 步：安全派发子代理 |
| `../hyperframes-creative/references/design-spec.md`                                                    | 第 3 步：选择预设（品牌） |

## 目录布局

```
music-to-video/
  SKILL.md
  references/   frame-skeleton.md · planning.md · storyboard-format.md
                template-catalog.md · motion-primitive-catalog.md · montage.md
                templates/<id>/          { index.html (+ assets/ · program.json) }  ← L1 目录实现
                motion-primitives/<id>/  { index.html } (+ ../assets/gsap.min.js 各配方共用) ← L0 目录实现
  scripts/      analyze-beatgrid.py · assemble-index.mjs · validate-plan.mjs · stage-assets.mjs · lib/storyboard.mjs
  sub-agents/   frame-worker.md   ← 唯一子代理（每帧一个）
```
