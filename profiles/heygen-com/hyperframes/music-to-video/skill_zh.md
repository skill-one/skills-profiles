> **首先，保持这项技能的新鲜感——在运行前与用户确认：** `npx hyperframes skills update music-to-video`。当一切都是最新时，这是一个快速的空操作；否则，它会在您依赖它们之前刷新这项技能及其依赖的核心领域技能。

# music-to-video — 一种基于音乐的、节拍同步的视频工作流程

使用这项技能将**音乐曲目**转换为节拍同步的 HyperFrames 视频。您只需分析一次曲目，布置帧，为每帧制定计划，并将每个帧作为 compositions 构建。输入是一个音乐曲目以及可选的用户图像或视频——**没有旁白和网站捕获**。排版和模板是底线（一个完整的视频需要零资源）；用户提供的任何媒体都将按照相同的节拍网格剪辑。

您是**指挥家**。在 `videos/<项目>/` 中工作。按顺序运行步骤，并在继续之前通过每个**门**。两个步骤需要用户：**步骤 3**（计划批准）和**步骤 6**（渲染批准）——两者都是根据 `../hyperframes/references/brief-contract.md`（在步骤 0 之前阅读）：在自主模式下，发布摘要作为提醒，然后继续而不是等待。除了**步骤 4**，您自己完成所有步骤，其中您为每帧派遣**一个子代理**。将设计和运动规则从该文件中排除——它们存在于 `references/` 和 `frame-worker` 子代理中。

`SKILL_DIR` = 这项技能目录。`PROJECT_DIR` = `videos/<项目名>/`。

工作流程：步骤 0 设置 → `hyperframes.json` + `assets/bgm.mp3`；步骤 1 分析 → `audiomap.json`；步骤 2 骨架 → `STORYBOARD.md`（帧、组 `TBD`）；步骤 3 计划 → 完成 `STORYBOARD.md` + `frame.md`；步骤 4 构建 → `compositions/frames/NN-*.html`；步骤 5 组装 → `index.html`；步骤 6 渲染 → `renders/video.mp4`。

## 两个塑造一切的想法

- **一个分析器，您信任它。** `analyze-beatgrid.py` 是唯一节拍分析器——永远不要用其他工具或凭听觉重新测量节拍。它的能量 / 密度 / 卷轴 / 起始 / 沉默始终可靠。它的 `bpm` 和 `beats_sec` 只有在音乐真正有节奏时才可靠；在平静的音乐中，网格是追踪者强加的节拍器，因此按短语和能量而不是硬切到它来调整节奏。决定您处于哪种情况是每帧的 `pacing`（步骤 2）。
- **一个帧 = 一个文件；组存在于内部。** 步骤 2 将曲目切割成**帧**，每帧成为一个 compositions 文件 `compositions/frames/NN-<frame_id>.html`，由一个帧-worker 构建。一个帧可以细分为**组**（每个都是一个模板或运动原语组合）。额外的密度进入组内部，因此**帧数跟踪不同的处理，而不是节拍**——一个快速的曲目不会增加子代理的数量。

---

## 步骤 0：设置、BGM 和输入

目标：建立音乐来源，创建 HyperFrames 项目，并记录任何用户提供的媒体。

**简要从意图层开始。** 开启规则，按顺序：**(1)** `BRIEF.md` 存在 → 阅读它并不要它回答的问题——它的 `flow`/`storyboard` 推导模式（简要合同 § 1）。**(2)** 没有 `BRIEF.md` 但项目存在 → 从磁盘上的内容恢复；永远不要重新询问。**(3)** 一个直接到达这里的全新创建请求 → 阅读 `/hyperframes` 并运行其意图层（`references/intent-interview.md`）：它确认此路线的必备条件（音乐来源、目的地 → 方面——`../hyperframes/references/routes/music-to-video.md`）并宣布什么被推迟——品牌和类型在步骤 3 由设计选择。初始化后立即编写 `BRIEF.md`（永远不在之前——`init` 拒绝非空目录）并记录偏好支持的答案（`brief-format.md`）。编辑请求跳过所有这些。

**音乐是脊柱**——在 anything 之前建立一条曲目。这项技能针对**快速、高能量的 BGM**：一个强节拍网格驱动切割（平静的曲目有效，但按短语而不是节拍来调整节奏）。如果用户提供了音频——一个音乐文件，或从中提取音频的视频——使用它。否则从请求中选择情绪并通过 `/media-use` 生成曲目（`references/bgm.md`）。在第一个经过身份验证的提供者操作之前，运行 `npx hyperframes auth status` 并逐字传递其输出。如果已注销，应用一个分支：

- **协作式：** 等待登录或选择明确继续离线使用本地提供者。
- **自主式：** 陈述状态并通过可用的本地提供者继续。

如果没有任何离线提供者能满足所需的音乐能力，显示障碍。永远不要将密钥写入每个存储库的 `.env`。身份验证所有权和离线回退存在于 `/media-use` `references/setup-providers.md` § 提供者。生成的曲目位于 `assets/bgm.mp3`。将提供的图像或视频暂存，以便帧可以在节拍网格上使用它们；否则排版承载视频。

**歌词视频：** 对于与声乐同步的歌词，通过 `/media-use` 转录曲目以获取单词/行时间，或向用户索取歌词文本并将行放置在节拍网格上。

如果 `hyperframes.json` 缺失，则仅初始化。从简要中命名 `<项目>` 为连字符形式，例如 `midnight-drive-loop`——永远不要使用时间戳。`init` 检查已安装的技能与 GitHub 上的最新版本，如果任何技能过时，则更新全局集。

```bash
npx hyperframes init "videos/<项目>" --non-interactive --example=blank --skill=music-to-video
mkdir -p "$PROJECT_DIR/assets" "$PROJECT_DIR/renders"
cp "<用户音乐>" "$PROJECT_DIR/assets/bgm.mp3"   # 如果需要，首先从视频中提取
# 只有如果用户给了您图像/视频：
node <SKILL_DIR>/scripts/stage-assets.mjs --from <目录> --hyperframes "$PROJECT_DIR" --into public
```

**品牌**（字体 + 调色板）在步骤 3 选择，而不是在这里。不要提前选择一个类型或曲目类型——资源只是一个可选成分，类型从每帧的选择中产生。

**门：** `hyperframes.json` + `assets/bgm.mp3` 存在；方面 / 长度 / fps 以及（如果有）资源清单被记录。

---

## 步骤 1：分析音乐

目标：生成整个视频构建的单一规范时间分析。

`analyze-beatgrid.py` 是**唯一的**节拍分析器——永远不要用其他工具或凭听觉重新测量节拍。它读取曲目一次并写入 `audiomap.json`：能量阶段（级别 / 密度 / 感觉），起始 + `onset_rate`，卷轴，沉默，`hard_stops`，`key_moments`，短语，速度 / 网格，和 `audio.duration_sec`。它是确定性的——相同的文件始终给出相同的地图。大多数字段在任何音乐上都可靠；`bpm` 和 `beats_sec` 只有在音乐真正有节奏时才可靠，而判断这一点是您在步骤 2 做出的决定。

先决条件：Python 3 并具有 `librosa`，`numpy`，和 `soundfile` 可用。如果导入失败，请在运行分析器之前将它们安装到活动的 Python 环境中：

```bash
python3 -m pip install librosa numpy soundfile
```

```bash
python3 <SKILL_DIR>/scripts/analyze-beatgrid.py "$PROJECT_DIR/assets/bgm.mp3" \
  -o "$PROJECT_DIR/audiomap.json" --print
```

**门：** `audiomap.json` 存在；`audio.duration_sec` 已知。

---

## 步骤 2：帧骨架（仅结构）

目标：读取音乐并布置帧——`STORYBOARD.md` 的骨架。

阅读 [`references/frame-skeleton.md`](references/frame-skeleton.md)。自己将 `audiomap.json` 转换为 `STORYBOARD.md` 的**骨架**——没有中间的 JSON。在真实的音乐变化处（`hard_stops`，SURGE / DROP `key_moments`，卷轴的边缘，没有起始的拉伸，大的能量跳跃）切割曲目为**帧**，并将每个边界对齐到 audiomap 锚点。对于每个帧设置 `span_sec`，`pacing`（步骤 1 的信任调用的裁决——`beat_cut` 当网格真实时，`phrase_flow` 当它是平静音乐强加的节拍器时），`mood`，和一个一行的 `feel`（步骤 3 匹配模板的纯音乐情况）。仅在此时分类和布置：将每个帧的 `### Groups` 作为 `TBD (步骤 3)`，并将前文 `style` 留空——没有模板，复制，颜色或字体。预期 ~1–6 帧。

**门：** 帧平铺曲目（第一个在 0，最后一个在 `duration_s`）；每个都带有 `span_sec` + `pacing` + `mood` + `feel`；每个 `### Groups` 都是 `TBD`；任何地方都没有内容。

---

## 步骤 3：填充计划（用户门控）

目标：将骨架转换为经批准的完整 `STORYBOARD.md`。

阅读 [`references/planning.md`](references/planning.md)，[`storyboard-format.md`](references/storyboard-format.md)，[`template-catalog.md`](references/template-catalog.md)，[`motion-primitive-catalog.md`](references/motion-primitive-catalog.md)，和 [`montage.md`](references/montage.md)（如果用户提供了资源）。原地编辑同一文件，做两件事：

1. **选择品牌。** 使用 `../hyperframes-creative/frame-presets/` 中的一个预设（使用 `../hyperframes-creative/references/design-spec.md` 中的表格）（匹配曲目的情绪；**只有它的字体和颜色重要**——模板拥有 compositions）。将其未修改地复制到 `frame.md` 并从它填充前文 `style`（字体 + ≤4–6 种色板调色板）。
2. **填充每个帧。** 决定其组并给每个组一个处理：来自目录的匹配模板（具有绑定参数和真实的 audiomap 锚点），来自原语目录的自由组合，或遵守 `pacing` 的资源处理。**在您自由组合一个命名的样式之前，在实时目录中搜索它**：对于每个样式，效果，处理或过渡，用户要求的——"CRT 扫描线"，"故障"，"胶片颗粒"，"闪烁扫描"——运行 `npx hyperframes catalog --query "<样式，用普通英语>" --json` 并阅读顶部结果。`template-catalog.md` 和 `motion-primitive-catalog.md` 仅列出这项技能自己的本地材料；搜索排名整个托管注册表（~400 块和组件）并**不需要安装**——没有项目，没有先前的 `add`，没有账户。只有在搜索返回了不匹配的样式之后才自由组合样式。编写副本。您拥有 WHAT（模板 / 原语 + 内容 + 锚点）；帧-worker 拥有 HOW——**永远不要将毫秒级 tweens 写入故事板**。

```bash
node <SKILL_DIR>/scripts/validate-plan.mjs --storyboard "$PROJECT_DIR/STORYBOARD.md" \
  --audiomap "$PROJECT_DIR/audiomap.json" --templates <SKILL_DIR>/references/templates
```

修复它报告的每个 `✗`（硬错误：持续时间不匹配，帧未平铺曲目，缺少 `src`）；警告是尽力而为的。然后向用户显示逐帧摘要并迭代，直到他们批准。在自主模式下这是一个检查点门：发布摘要作为提醒并继续（`validate-plan.mjs` 的传递是一个质量门，仍然会阻止）。

**门：** `frame.md` 是一个字面量预设副本；`validate-plan.mjs` 退出 0；用户批准了计划（自主：摘要被作为提醒发布）。

---

## 步骤 4：根据计划构建帧

目标：将每个帧构建为自包含的 compositions 文件。

创建 `compositions/frames/`。阅读 [`sub-agents/frame-worker.md`](sub-agents/frame-worker.md) 和 `../hyperframes/references/subagent-dispatch.md`。派遣**每个帧一个帧-worker**，尽可能并行（否则按波浪式）。每个工人得到恰好一个帧和此上下文：

```text
PROJECT_DIR: <绝对路径>
frame_id: <NN-frame_id>              # = 帧文件茎，例如 02-f2；compositions id
您的块：PROJECT_DIR/STORYBOARD.md 中的 `## Frame N — <frame_id>` 块
audiomap: PROJECT_DIR/audiomap.json
frame.md: PROJECT_DIR/frame.md
材料：对于每个组，<SKILL_DIR>/references/templates/<id>/index.html（模板）和
           <SKILL_DIR>/references/motion-primitives/<id>/（自由）；暂存的资源/（资源组）
合同：../hyperframes-core/references/sub-compositions.md + determinism-rules.md
画布：<w>×<h>   Pacing: <beat_cut|phrase_flow>
写入：PROJECT_DIR/compositions/frames/<frame_id>.html
```

工人分支引用的材料，将每个锚点转换为帧本地秒（`local_t = track_t − span_sec[0]`），用 0ms 切割门控其组，并写入一个安全的帧文件。**工人永远不会运行 `hyperframes` CLI**——这些命令在组装项目上运行，而组装项目尚不存在，因此它们会报告错误的文件。工人只是写入合同并停止；您在组装后（步骤 6）验证。每当一个工人返回时，您可以确认其文件已落在磁盘上。

**门：** 每个帧都有其 `compositions/frames/NN-*.html` 存在于磁盘上。

---

## 步骤 5：组装

目标：将构建的帧 + BGM 组装到可播放的 `index.html` 中。

`assemble-index.mjs` 是确定性的——没有子代理，没有判断。它引用每个帧文件在其累积 `data-start`，在轨道 11 上挂载 `assets/bgm.mp3`，并硬切帧 → 帧（帧按曲目平铺且没有间隙，因此**没有过渡注入器**）。

```bash
node <SKILL_DIR>/scripts/assemble-index.mjs --storyboard "$PROJECT_DIR/STORYBOARD.md" \
  --hyperframes "$PROJECT_DIR" --audiomap "$PROJECT_DIR/audiomap.json"
```

修复它报告的任何 `✗`——一个缺失或空的帧文件意味着该工人写了一个部分文件；重新派遣它（步骤 4）并重新组装。

**门：** `index.html` 存在；总持续时间 == `audiomap.audio.duration_sec`。

---

## 步骤 6：验证和渲染

目标：验证组装的视频，获取用户批准，并渲染最终的 MP4。

在**组装的项目**上运行 CLI——这是正确的单元（每帧的工人无法运行它）。`check` 运行结构 lint 和无头浏览器运行时，布局，运动，和对比度门控一次通过；`--snapshots` 还会发出审查帧。

```bash
( cd "$PROJECT_DIR" && npx hyperframes check . --snapshots )
```

在 `t=0`，每个帧开始，最强的 DROP / SURGE，每个 `hard_stops[].t`，和最终帧处检查。失败时，自己做出**最安全的修复**：编辑有问题的 `compositions/frames/NN-*.html`。永远不要更改持续时间或音频时间来隐藏同步问题。一旦门控通过，暂停用户审查，然后在批准后仅渲染（自主模式：询问一个保留的问题——"预览首先，还是渲染？"——然后交付带有联系表的 MP4）：

```bash
( cd "$PROJECT_DIR" && npx hyperframes render . --skill=music-to-video -q draft -o renders/video.mp4 --fps 30 )
```

**门：** `check` 通过并且快照已被检查；用户批准（自主：检查通过并且交付包括联系表）；`renders/video.mp4` 存在，有音频，持续时间 == `audiomap.audio.duration_sec`。最终回复声明 MP4 路径和持续时间。

---

## 继续表

| 您有                   | 继续从 |
| -------------------------- | ------------- |
| `assets/bgm.mp3` 仅      | 步骤 1        |
| `audiomap.json`            | 步骤 2        |
| `STORYBOARD.md`（骨架） | 步骤 3        |
| `STORYBOARD.md`（完整） | 步骤 4        |
| 所有帧文件            | 步骤 5        |
| `index.html`               | 步骤 6        |

## 快速参考

**格式：** 默认为横向 `1920x1080`；纵向 `1080x1920`；方形 `1080x1080`。在故事板前文一次设置画布（`canvas: { w, h, fps }`）。

**脚本** 在 `scripts/` 下：`analyze-beatgrid.py`（唯一的分析器），`validate-plan.mjs`（计划检查），`assemble-index.mjs`（索引组装），`stage-assets.mjs`（暂存用户媒体），`lib/storyboard.mjs`（托管的解析器）。其他所有的是 `hyperframes` CLI。

| 阅读                                                                                                           | 当                                                                 |
| -------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------- |
| [`references/frame-skeleton.md`](references/frame-skeleton.md)                                                 | 步骤 2：读取音乐，布置帧，设置 pacing                  |
| [`references/planning.md`](references/planning.md) · [`storyboard-format.md`](references/storyboard-format.md) | 步骤 3：选择品牌，填充每帧，写入计划                   |
| [`references/template-catalog.md`](references/template-catalog.md)                                             | 步骤 3：为每组选择模板                               |
| [`references/motion-primitive-catalog.md`](references/motion-primitive-catalog.md)                             | 步骤 3/4：自由组合的 L0 配方                         |
| [`references/montage.md`](references/montage.md)                                                               | 步骤 3/4：资源处理（节拍切 / ken-burns）               |
| [`sub-agents/frame-worker.md`](sub-agents/frame-worker.md)                                                     | 步骤 4：派遣 + 构建一个帧                              |
| `../hyperframes/references/subagent-dispatch.md`                                                               | 步骤 4：安全地派遣子代理                              |
| `../hyperframes-creative/references/design-spec.md`                                                            | 步骤 3：选择预设（品牌）                              |

## 目录布局

```
music-to-video/
  SKILL.md
  references/   frame-skeleton.md · planning.md · storyboard-format.md
                template-catalog.md · motion-primitive-catalog.md · montage.md
                templates/<id>/          { index.html (+ assets/ · program.json) }  ← L1 目录实现
                motion-primitives/<id>/  { index.html } (+ ../assets/gsap.min.js 共享的配方) ← L0 目录实现
  scripts/      analyze-beatgrid.py · assemble-index.mjs · validate-plan.mjs · stage-assets.mjs · lib/storyboard.mjs
  sub-agents/   frame-worker.md   ← 唯一的子代理（每帧一个）
```
