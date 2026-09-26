> **首先，保持此技能的时效性——在运行前与用户确认：** `npx hyperframes skills update talking-head-recut`。当一切都是最新时，这是一个快速的无操作；否则，它将在您依赖它们之前刷新此技能及其依赖的核心域技能。

# Talking Head Recut

Talking Head Recut 会对本地视频进行全屏播放，并在其上叠加一系列定时设计的**图形卡片**——标题、下三分之二、数据调用、引言、侧面板、画中画——与正在说的话同步。代理设计卡片（时间 + 内容），并将每个卡片的 HTML 直接**在对话中编写**，然后通过 `hyperframes` 组装成一个单一的合成 HTML 并渲染为 MP4。没有固定的原型列表，也没有规定的卡片结构——覆盖层来自实际转录内容。

> **正门是 `/hyperframes`。** 此技能将一个**现有的 talking-head 影片**与**设计的图形卡片**（标题、下三分之二、数据调用、引言、侧面板、PiP）打包在一起——不是纯字幕（作为文本的 spoken words）。**影片未经修改地播放。** 任何其他意图——纯字幕、独立图形、从头开始的视频——或任何不确定性 → 首先阅读 `/hyperframes`：意图层拥有每个路由决策。

> **`embedded-captions` 的图形包装兄弟。** 字幕将 _spoken words_ 添加为可读的副标题；这将在播放的视频上添加 _设计的图形_。纯字幕 → `embedded-captions`。从头开始构建视频 → 创建工作流程 (`product-launch-video` / `faceless-explainer` / …)。

通过 `/hyperframes` 路由，意图层仅确认输入（哪个影片）并**宣布**渲染策略问题作为延迟询问——宽高比、布局、样式组、卡片数量保持在第 7 步，其中探测到的影片和转录内容为建议提供基础；层的运行形状问题不适用。当存在 `BRIEF.md` 时，它会携带确认的输入和任何用户注释——首先阅读它。

工作目录中的可检查中间文件：

- `metadata.json` — 时长 / 宽度 / 高度 / fps
- `audio.mp3` — 提取的音频
- `transcript.json` — 一个扁平的**单词数组** `[{ text, start, end }, …]` (Whisper；没有 `segments`，没有 `words` 包装)
- `storyboard.json` — 轻量级卡片轮廓（代理的计划）
- `public/cards/card-XX.html` — 每个卡片一个 HTML 片段
- `public/index.html` — 最终组装的合成
- `output.mp4` — 渲染的视频

## CLI 解析

```bash
# hyperframes — 转录（本地 Whisper）+ 将组装的 HTML 渲染为 MP4
npx hyperframes --help
```

此技能完全在 **hyperframes** CLI 以及系统 `ffmpeg` / `ffprobe` 上运行。
转录是通过 `hyperframes transcribe` 进行的本地 **Whisper**——没有第三方服务、API 密钥或速率限制代理。

## 工作流程

### 1. 检查环境

```bash
npx hyperframes doctor          # ffmpeg, 无头浏览器, 渲染依赖
# 确认捆绑的资产：
ls "<SKILL_DIR>/assets/fonts" "<SKILL_DIR>/assets/vendor/gsap.min.js"
```

必需：

- `ffmpeg` / `ffprobe` (系统)
- `<SKILL_DIR>/assets/fonts/*.woff2`, `<SKILL_DIR>/assets/vendor/gsap.min.js` (捆绑在此技能中，在第 9 步到工作目录中)

转录不需要密钥——`hyperframes transcribe` 在本地运行 Whisper（第 4 步）。

强烈建议在 macOS 上为 `hyperframes render`：

```bash
export PRODUCER_BROWSER_GPU_MODE=hardware
```

### 2. 创建一个工作目录

所有工件都位于 `videos/<project-name>/` 下——与其他视频工作流程（`product-launch-video` / `faceless-explainer` / `pr-to-video`）相同的约定。保持 cwd 在工作区根目录；所有以下内容都在此一个子目录下写入。

```bash
VIDEO_PATH="/绝对路径输入.mp4"
WORK_DIR="videos/$(basename "$VIDEO_PATH" | sed 's/\.[^.]*$//')"
mkdir -p "$WORK_DIR"
```

### 3. 提取音频和元数据

```bash
# metadata — 时长 / 宽度 / 高度 / fps
ffprobe -v error -select_streams v:0 \
  -show_entries stream=width,height,r_frame_rate \
  -show_entries format=duration -of json "$VIDEO_PATH" > "$WORK_DIR/metadata.json"
# audio
ffmpeg -y -i "$VIDEO_PATH" -vn -acodec libmp3lame -q:a 2 "$WORK_DIR/audio.mp3"
```

输出：`metadata.json`（读取 `width`/`height`/`duration`；fps = 评估的 `r_frame_rate` 分数，例如 `30000/1001 → 29.97`) + `audio.mp3`。

### 4. 转录

```bash
npx hyperframes transcribe "$WORK_DIR/audio.mp3" -d "$WORK_DIR" --json --model small.en
```

本地 **Whisper**——没有 API 密钥，没有代理，没有速率限制。将一个单词级别的 `transcript.json` 写入工作目录（单词 `text` + `start` / `end` 时间戳）。
阅读它以获取驱动卡片时间（第 6 步）的单词/句子时间。如果需要段落级别的块，请自行将单词分组为句子（在标点符号/停顿处）。

**限制在媒体时长内。** Whisper 可能会返回最终单词的 `end` 略微超过实际剪辑长度——将每个卡片的 `endSec` 和 `composition.durationSeconds` 限制为 `metadata.json` 时长，否则渲染将在视频之后显示黑色尾部。

### 5. 修正转录

`transcript.json` 是一个**扁平的单词对象数组**——`[{ "text": "...", "start": s, "end": s }, …]`（没有 `segments` 数组，没有 `words` 包装；每个单词的键是**`text`**）。阅读并修正明显的 ASR 错误：

- 同音异义词、产品名称、技术术语、标点符号
- 在原地编辑单词的 `text`；**保留其 `start` / `end`** 时间戳
- 没有预先分组的 `segments` 数组——**当您需要段落级别的块以用于卡片时间时，请自行分组单词**（在终端标点符号/停顿处）

### 6. 轻量级故事板（在聊天中）

**不涉及 CLI。** 阅读 `transcript.json` + `metadata.json` 并直接设计卡片。`storyboard.json` 是代理内部的计划工件——没有 CLI 命令消耗它；它的存在是为了让您在编写每个卡片的 HTML 之前，可以清晰地思考时间和内容。保持形状与下面的示例一致，以便相同的轮廓可以驱动您在第 9 步编写的合成：

```json
{
  "schemaVersion": 3,
  "composition": {
    "fps": 30,
    "width": 1080,
    "height": 1920,
    "durationSeconds": 121.2,
    "layout": "portrait",
    "themeId": "noir",
    "seed": 42
  },
  "videoTrack": {
    "sourcePath": "input-video.mp4",
    "startSec": 0,
    "endSec": 121.2,
    "bounds": { "x": 0, "y": 0, "width": 1080, "height": 1920 }
  },
  "subtitles": { "enabled": false },
  "cards": [
    {
      "id": "card-01",
      "intent": "用演讲者焦虑的午夜问题作为钩子",
      "startSec": 0.5,
      "endSec": 13.0,
      "accentIndex": 0,
      "zone": "fullscreen",
      "contentHints": {
        "kicker": "一个诚实的提问",
        "title": "11 点钟的灵魂搜索问题",
        "detail": "客户的 60 秒语音信息：'如果人民币升值，那我的美元政策是否是一个巨大的损失？'"
      }
    }
  ]
}
```

**必需的卡片字段：**

| 字段                   | 类型                                       | 目的                                                                                               |
| ----------------------- | ------------------------------------------ | ----------------------------------------------------------------------------------------------------- |
| `id`                    | 字符串                                     | 在卡片 HTML & GSAP 选择器中使用的稳定 ID                                                          |
| `intent`                | 字符串                                     | 自然语言描述；输入到卡片合成                                                   |
| `startSec` / `endSec`   | 数字                                     | 秒级时间（endSec > startSec）                                                                  |
| `accentIndex`           | 0 \| 1 \| 2 \| 3 \| 4                      | 从 5 个主题强调色中选择哪个颜色用于此卡片                                                    |
| `zone`                  | 枚举（见下文）                           | 卡片在画布上的位置                                                                    |
| `contentHints`          | 对象                                     | 自由形式包；代理将 kicker/title/detail/data/quote 放在这里                                         |
| `archetype` (可选)  | 字符串                                     | 您可以附加的自由形式标签，以记住卡片的模式；缺失 = 自由形式，这是默认值 |
| `transition` (可选) | 枚举: `cut` \| `fade` \| `slide` \| `wipe` | 声明卡片之间的过渡                                                                   |

**五个 `zone` 值：**

| zone              | 解析边界                                | 使用时机                             |
| ----------------- | -------------------------------------- | --------------------------------------- |
| `fullscreen`      | 覆盖整个画布                            | 英雄时刻，大数字，口号              |
| `whiteboard-area` | 插入 40px 边距（或 45% 的肖像高度）  | 密集数据 / 注释内容                  |
| `lower-third`     | 底部 30% 带状                          | 视频上方的注释                     |
| `side-panel`      | 右侧 42%（横屏）或底部 40%（竖屏） | 数据侧，视频另一侧                 |
| `video-overlay`   | 全画布，期望大部分透明的卡片   | 全出血视频上的注释覆盖             |

当您在第 9 步组装合成时，根据上表将每个卡片的 `zone` 解析为卡片宿主包装上的像素边界。
视频边界在合成级别（`videoTrack.bounds`）**一次性设置**；要使视频在卡片之间“移动”，请在合成的 `<script>` 中针对 `#video-wrap` 编写 GSAP 缩放（见第 9 步）。

**没有规定的卡片角色，没有规定的叙事弧。** 卡片来自视频实际说什么——可能是所有引言或所有数据，可能是以数字开头或以故事开头。让转录驱动节奏。

**有多少要点？——根据时长 + 密度自动推断。** 没有固定的上限。从视频时长选择**基础速度**，然后根据**信息密度**进行调整。
**下限是固定的：至少 5 张卡片**，即使短视频也有节奏。

**第 1 步——基于时长的基本速度**（中等密度下的自然秒/卡片）：

| 视频时长     | 基本速度（每张卡片的秒数） | 理由                                   |
| ------------ | ------------------------ | ------------------------------------------- |
| < 60s (短轮播) | **6–8s**                 | 观众期待短形式的快速剪辑                  |
| 60s – 3 分钟  | **8–12s**                | 正常社交节奏                          |
| 3 – 10 分钟  | **12–20s**               | 给呼吸空间；每张卡片承载更多信息         |
| 10 – 30 分钟  | **20–35s**               | 长形式讲座 / 采访节奏                  |
| > 30 分钟    | **30–60s**               | 剧集，接近章节的感觉                 |

**第 2 步——密度乘数**（乘以基本速度）：

| 转录中的信号                                                                                                    | 乘数 | 效果                   |
| ---------------------------------------------------------------------------------------------------------------- | ---------- | ------------------------ |
| **高密度** — 许多数字、明确的声明、急促的节奏、列表式枚举、每 1–2 句话就是一个新想法 | **× 0.7**  | 切片更快，更多卡片  |
| **中等密度** — 混合流，既有数据也有叙事                                                                | **× 1.0**  | 基本速度                |
| **低密度** — 一个扩展的故事、重复的重新框架、缓慢的反思节奏、单一论点展开                 | **× 1.5**  | 切片更慢，较少卡片 |

**第 3 步——计算：**

```
secPerCard = basePace × densityMultiplier
cardCount  = max(5, round(videoDurationSec / secPerCard))
```

示例（注意——**没有上限**；长视频自然产生更多卡片）：

- **30 秒轮播，单个要点（低密度）** → 7 × 1.5 = 10.5s/卡片 → round(30/10.5)=3 → 向下取整到 **5** 张卡片
- **60 秒反思独白（低密度）** → 10 × 1.5 = 15s/卡片 → **4** → 向下取整到 **5** 张卡片
- **121 秒 talking-head，丰富的数据（高密度）** → 10 × 0.7 = 7s/卡片 → **17** 张卡片
- **5 分钟采访，混合密度** → 16 × 1.0 = 16s/卡片 → **19** 张卡片
- **10 分钟深入探讨，高密度** → 16 × 0.7 = 11s/卡片 → **55** 张卡片
- **30 分钟讲座，中等密度** → 28 × 1.0 = 28s/卡片 → **64** 张卡片
- **1 小时播客，低密度** → 45 × 1.5 = 67.5s/卡片 → **53** 张卡片

当卡片持续超过 ~15 秒时，计划一个更丰富的卡片（数据块、多步骤揭示、几个子要点随着错开的动画展开）——静态的单行文本在 8 秒后变得无聊。对于许多卡片超过 30 秒的长片段，考虑将时间线**分成子合成**（每个章节一个 .html，使用 `data-composition-src` 挂载）以便每个文件中的 GSAP 时间线保持可管理——见 `timeline_track_too_dense` HyperFrames lint 警告。

`content` 可以是纯字符串（"标题：年化 5.69%\n笔记：..."）或任何捕获数据的 JSON 形状。代理决定每张卡片的形状。

**可选的尾声。** 此技能不提供**固定的品牌尾声**。如果用户想要一个结束语，请自行设计一个中性的卡片（标志 + 一行标语，~1.5-2 秒，淡入 -> 短暂停留 -> 淡出），将其追加到 `cards[]`，并将 `composition.durationSeconds` 扩展到其 `endSec`。否则在最后一张内容卡片上结束。

### 7. 决定渲染策略

#### 与用户确认视觉方向（首先做这件事）

在您开始设计卡片或决定边界之前，**要求用户选择输出比例、布局、样式和卡片密度预设**。帧会根据选择的布局 × 样式组合自动选择（见下文“自动选择帧”表）。在发送问题之前，**预先计算两件事**：

1. **`recommendedRatio`** 从源视频的宽高比（`metadata.json` 宽度 / 高度）：
   - `sourceAspect = width / height`
   - `sourceAspect ≥ 1.5`（≥ ~3:2 宽）→ 推荐 **`16:9`**
   - `sourceAspect ≤ 0.7`（≤ ~9:13 高）→ 推荐 **`9:16`**
   - `0.7 < sourceAspect < 1.5`（接近方形）→ 推荐 **`4:5`**

   将推荐选项的标签标记为 "（推荐 · 匹配源视频 X:Y）" 以便用户知道为什么推荐它。

2. **`autoCount`** 从第 6 步（`max(5, round(videoSec / (basePace × densityMultiplier)))`）以便“自动”选项的标签可以显示具体数字。

**环境兼容性——选择最佳可用的问题通道。**
不是每个运行时都暴露相同的结构化问题工具。应用此顺序：

1. **本地澄清工具** — 使用下面的结构化 4 个问题调用。
2. **其他本地澄清工具**（例如 `ask_question`、`request_user_input`、IDE 特定的提示）— 使用相同的 4 个问题文本和选项列表。保留推荐标记和预计算值。
3. **没有本地工具**（Codex CLI、纯文本运行时）— **在正常对话中直接询问**。使用本节末尾的纯文本模板。保持它为**一条消息，4 个编号的问题**（全局限制是每轮 2–5 个问题；我们保持在其中）。

适用于每个通道的规则：

- 每轮最多**问 2-5 个问题**。我们这里的 4 个问题符合要求。
- 即使缺少信息不会阻止渲染，**也要问一次以确认那些对最终输出有实质性影响的参数**（比例、布局、风格、卡片数量）。
- 如果用户已经预先批准了默认值（“直接使用默认值”、“不需要询问”、“自动选择所有内容”），或者你被要求不要提问，或者运行中带有持续的自主信号（“让我惊喜”/“由我决定”——`../hyperframes/references/brief-contract.md` § 1），则**完全跳过问题**，并使用：`recommendedRatio`、`layout="stack"`（最安全的跨比例默认值）、从最中性的组（编辑/数据）中选择的 `style`、`autoCount`。用一句话告诉用户你选择了什么，然后继续。

**渠道 A — 原生 `AskUserQuestion`：**

```
// 在调用之前预先计算：
//   recommendedRatio = "16:9" | "9:16" | "4:5"
//   autoCount        = 整数（来自步骤 6）

AskUserQuestion({
  questions: [
    {
      question: "输出视频长宽比（画布）：",
      header: "长宽比",
      multiSelect: false,
      // 按照AskUserQuestion的惯例，将推荐选项排在最前面。
      // 在推荐选项的标签后添加"(推荐 · 匹配源视频 W×H)"。
      options: [
        { label: "16:9 (1920×1080) 横屏", description: "电视 / YouTube / 桌面播放。当源视频已经是横屏时最自然；最宽的画布。" },
        { label: "9:16 (1080×1920) 竖屏", description: "TikTok / Reels / 短视频。对于竖屏源视频最自然；原生移动体验。" },
        { label: "4:5 (1080×1350) 近竖屏", description: "Instagram 信息流 / 微信朋友圈。当源视频接近方形或你想覆盖两个平台时最佳。" }
      ]
    },
    {
      question: "选择整体布局：视频和卡片如何在画布上共存？",
      header: "布局",
      multiSelect: false,
      options: [
        { label: "并排（分割）",  description: "视频和卡片各占画布的一半。对于访谈 / 数据并排最稳定；视觉分离清晰。" },
        { label: "上下（堆叠）",    description: "视频在上方（约 52%），卡片在下方。经典组合：说话者面部 + 摘要卡片；在竖屏中也适用。" },
        { label: "画中画 (pip)", description: "卡片填满画布，视频缩小成一个圆角窗口。当内容是主要时使用，说话者是次要的。" },
        { label: "全屏覆盖 (overlay)", description: "视频全屏播放，卡片作为玻璃层悬浮在上方。强烈的电影感 / 情感体验。" }
      ]
    },
    {
      question: "选择卡片视觉风格（style）：",
      header: "风格组",
      multiSelect: false,
      // 注意：这三个组有意与下面的框架自动选择矩阵行匹配，
      // 这样选择一个组就能同时确定 `style` 组和框架矩阵列。成员资格是互斥的。
      options: [
        { label: "暖纸 (warm-paper)", description: "学术笔记本 · 编辑大号字体 · 白板手绘 · xhs 社交。最适合访谈反思、产品发布、生活方式、情感故事。" },
        { label: "临床 / 冷 (clinical)",   description: "审计杂志 · 瑞士网格 · 终端 CLI · 现代极简。最适合财务分析、调查报告、技术教程、严肃演示。" },
        { label: "实验 / 前卫 (experimental)", description: "几何色块几何 · 聚光灯暗背景。最适合短视频高亮、产品发布、强烈情感、电影感。" }
      ]
    },
    {
      question: "卡片数量（取走节奏）：剪多少张卡片？",
      header: "卡片数量",
      multiSelect: false,
      options: [
        { label: "自动（推荐）· 约 N 张卡片", description: "根据视频时长和信息密度（见步骤 6 规则）自动推断。本次运行估计约 N 张卡片。将实际 N（你的 autoCount）代入标签。" },
        { label: "较少 · 约 round(N × 0.6) 张卡片", description: "稀疏剪辑，每张卡片包含更长时间——适合反思性 / 慢节奏内容。" },
        { label: "更多 · 约 round(N × 1.5) 张卡片", description: "紧密剪辑，节奏更快——适合顿挫性 / 数据密集型 / 短视频高亮内容。" }
      ]
    }
  ]
})
```

**关于“其他”** — `AskUserQuestion` 会自动在卡片数量问题中添加“其他”选项。用户可以直接输入数字（例如“8”、“20”）作为卡片数量目标。将输入解析为整数：如果解析成功 → 使用该值（最小值 5）；如果解析失败 → 回退到“自动”。

**渠道 B — 纯文本回退**（Codex CLI、没有原生提问工具的运行时）。将以下内容作为一条普通消息发布，然后等待回复。使用项目符号样式 1/2/3/4 以保持回复可解析：

```
在开始剪辑卡片之前，我需要与你确认四个视觉决策：

1) 输出长宽比（画布）：
   A. 16:9 横屏 (1920×1080) — 电视 / YouTube / 桌面播放
   B. 9:16 竖屏 (1080×1920) — TikTok / Reels / 短视频
   C. 4:5 近竖屏 (1080×1350) — Instagram 信息流 / 适用于两个平台
   ▸ 我的推荐： <recommendedRatio>  (匹配源视频 W×H = <sourceW>×<sourceH>)

2) 整体布局（视频与卡片如何共存）：
   A. split   并排 (50/50)
   B. stack   上下 (视频在上方，卡片在下方)
   C. pip     画中画 (卡片填满画布，视频圆角窗口)
   D. overlay 全屏玻璃覆盖 (视频全屏，卡片玻璃层)

3) 卡片风格组（映射到框架自动选择矩阵，选 1 个中的 3 个）：
   A. 暖纸 (warm-paper)      (学术 / 编辑 / 白板 / xhs)
   B. 临床 / 冷 (clinical)   (审计 / 瑞士 / 终端 / 极简)
   C. 实验 (experimental)  (几何 / 聚光灯)

4) 卡片数量（取走节奏）：
   A. 自动（推荐） — 约 <autoCount> 张
   B. 较少 — 约 round(<autoCount> × 0.6) 张
   C. 更多 — 约 round(<autoCount> × 1.5) 张
   D. 给我一个具体数字（例如“8”、“20”）

回复格式：“1A 2C 3B 4A” 或自然语言都可以。
如果你希望所有推荐默认值，回复“默认”/“自动”/“使用所有推荐”。

```

解析纯文本回复：

- 接受松散格式：`"1A 2C 3B 4A"`、`"A C B A"`、`"16:9 / pip / data / auto"`、完整句子或 `default`。
- 如果任何答案不明确 → 重新询问不明确的选项（仍然在 2-5 个问题的限制内）。
- 如果用户说“默认 / 自动 / 使用所有推荐” → 直接跳过，不重新提问。

用户回答后（任何渠道）：

1. **根据比例答案解析输出画布** — 这些是 `storyboard.composition.width / height` 的确切值：

   | 用户选择 | composition.width × height | storyboard.layout 字段                                       |
   | ------- | -------------------------- | ------------------------------------------------------------- |
   | `16:9`  | **1920 × 1080**            | `"landscape"`                                                 |
   | `9:16`  | **1080 × 1920**            | `"portrait"`                                                  |
   | `4:5`   | **1080 × 1350**            | `"portrait"` (模式将 4:5 视为竖屏——高度 > 宽度) |

   对于 **4:5 边界在 `references/layouts/*.html` 中** — 这些文件只记录横屏（1920×1080）和竖屏（1080×1920）。对于 4:5（1080×1350），通过**从竖屏按比例缩放**来推导边界：保持水平值，垂直值按 `1350/1920 ≈ 0.703` 缩放。示例：`overlay` 竖屏卡片 = `{ x: 24, y: 1280, w: 1032, h: 564 }` → 4:5 卡片 =
   `{ x: 24, y: round(1280 × 0.703), w: 1032, h: round(564 × 0.703) }`
   = `{ x: 24, y: 900, w: 1032, h: 397 }`。

2. **通过查看转录文本的语气将风格组映射到特定风格** — 选择最匹配的，但保持在用户选择的组内。如果你在组内的两个特定风格之间不确定，发送第二个 `AskUserQuestion`，包含 2-4 个特定风格选项。

3. **根据密度答案解析最终卡片数量**：

   | 用户选择             | final cardCount                           |
   | ----------------------- | ----------------------------------------- |
   | Auto (recommended)      | 你已经计算的 `autoCount`                  |
   | Fewer                   | `max(5, round(autoCount × 0.6))`          |
   | More                    | `round(autoCount × 1.5)` (无上限)         |
   | Other = "<n>" (整数) | `max(5, parseInt(n))`                     |
   | Other = 任何其他内容   | 回退到 `autoCount`                  |

4. **从这张表中自动选择视频框架**（框架不询问用户——它们跟随布局 × 风格）：

   | 布局    | 暖纸风格（学术 / 白板 / 编辑 / xhs） | 临床风格（审计 / 瑞士 / 终端 / 极简） | 实验风格（几何 / 聚光灯） |
   | --------- | ------------------------------------- | ------------------------------------ | -------------------------- |
   | `split`   | `polaroid`                            | `hairline`                           | `clean`                    |
   | `stack`   | `polaroid`                            | `hairline`                           | `clean`                    |
   | `pip`     | `clean` (pip pill 已经有边框)        | `clean`                              | `clean`                    |
   | `overlay` | `clean` (全屏禁止装饰框架)            | `clean`                              | `clean`                    |

5. **用一句话告诉用户你选择了什么**——比例（+画布大小）、布局、特定风格、框架和最终卡片数量——然后继续执行步骤 7 的其余部分（每张卡片的布局、运动模式）。
6. 在工作记忆中记录这五个值（比例 / 布局 / 风格 / 框架 / 卡片数量）（不需要模式字段）；你将在步骤 8 写每个卡片的 HTML 时以及读取匹配的 `references/<dim>/<key>.html` 以获取标记和结构时参考它们。

如果用户通过“其他”选择了一个不在 10 风格库中的自由文本风格名称，将其视为设计新卡片视觉的提示，但仍然以选择的布局的边界为基础。

#### 渲染策略输入

在步骤 7.0 锁定了比例 / 布局 / 风格 / 卡片数量 / 框架后，剩余的每张卡片的决策是：

- **源视频在 GSAP 目标中的适配**：视频元素有 `object-fit: cover` 并被裁剪到 `#video-wrap` 的 tween 边界。如果你想要**不裁剪**（例如竖屏源视频在横屏画布上不应被裁剪顶部/底部），将 tween 对准一个匹配源视频比例的矩形，让周围的画布显示出来（或填充卡片 / 背景）。
- **`card.zone` 每张卡片**：根据你选择的布局（split → 侧面板，stack → 下三分屏，pip → 全屏，overlay → 视频覆盖层），或者为一次性变体选择不同的区域（全屏用于英雄/引言，白板区域用于密集数据）。
- **`accentIndex` 每张卡片**：每张卡片提取 5 个主题强调色之一。在卡片间变化以产生节奏；当两张卡片属于同一叙事节拍时，重复相同的索引。
- **运动词汇**：从 `data-anim` 类型（见后面的表格）中选择 2-3 个可重复的模式，并坚持使用它们，使构图感觉连贯。

从这些 `themeId` 调色板中选择（在构图 `<style>` 块中使用它们作为 `--accent-N` / `--bg` / `--text` CSS 变量）：

| themeId | 强调调色板（5 种颜色）                 | 画布背景          | 文本      |
| ------- | ------------------------------------- | ----------------- | --------- |
| classic | `#1971c2 #e03131 #2f9e44 #e8590c #9c36b5` | `#FFF9E3` (纸)    | `#1e1e1e` |
| noir    | `#4cc9f0 #f72585 #4ade80 #fb923c #a78bfa` | `#1a1a1a`         | `#f1f1f1` |
| mint    | `#0077b6 #d62828 #2d6a4f #e76f51 #7209b7` | `#e8faf0`         | `#1b4332` |
| craft   | `#bf5700 #d62728 #6c757d #e9b54a #3d5a80` | `#f6efe1`         | `#2d2d2d` |
| slate   | `#0ea5e9 #ef4444 #22c55e #f97316 #a855f7` | `#1e293b`         | `#f1f5f9` |
| mono    | `#000 #555 #888 #aaa #ccc`                | `#fff`            | `#000`    |

可用字体（woff2 在 `<SKILL_DIR>/assets/fonts/` 中，在步骤 9 阶段到工作目录）：`Caveat`（手写）、`LXGW WenKai TC`（中文手写）、`Inter`（现代无衬线）、`Virgil`（几何手写）。直接通过 `@font-face` 或 `font-family` 引用。

关于视觉模式的灵感，`<SKILL_DIR>/references/styles/` 包含 10 张自包含的参考卡片（学术 / 编辑 / 极简 / 聚光灯 / 几何 / 白板 / 审计 / 终端 / 瑞士 / xhs），你可以将它们作为起点复制——但**不要感到受限于匹配其中任何一张**。每张卡片都是你自己的设计。

#### 视觉设计库（<SKILL_DIR>/references/）

除了构图级别的 `themeId`，技能还提供了更丰富的**参考库**在 `<SKILL_DIR>/references/`，涵盖三个**正交**的视觉维度，你可以自由混合：

```
风格  ×  布局  ×  视频框架
 (10)      (4)         (3)
```

| 维度  | 键                                                                                              | 它决定什么                                                          |
| ---------- | ------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| **风格**  | `academic` `editorial` `minimal` `spotlight` `geom` `whiteboard` `audit` `terminal` `swiss` `xhs` | 卡片的视觉语言——字体、颜色、装饰、卡片内的布局 |
| **布局** | `split` `stack` `pip` `overlay`                                                                   | 源视频和卡片如何在画布上共享空间                       |
| **框架** | `clean` `hairline` `polaroid`                                                                     | 视频元素的装饰性边框                                           |

阅读 `<SKILL_DIR>/references/DESIGN_INDEX.md`
以获取完整矩阵和松散决策指南（访谈 / 产品发布 / 数据分析 /
社交剪辑 / 技术教程 / 情感故事 …）。当你决定使用特定风格 / 布局 / 框架时，阅读相应的文件：

- `references/styles/<key>.html` — 包含该风格 CSS 标记（颜色、字体、填充、装饰）和占位符取走的自包含卡片片段。复制 `.card[data-card-id="ref-<key>"]` 的样式块，将 data-card-id 重命名为你卡片的 ID，将占位符内容替换为实际取走内容，然后完成。
- `references/layouts/<key>.html` — 横屏和竖屏的精确 `videoBounds` + `cardBounds`，以及用于 `storyboard.json` 的每张卡片的 `layout` 字段的复制粘贴 JSON 段落。
- `references/frames/<key>.html` — 作为 `#video-wrap` 的兄弟添加的装饰性 HTML，以及构图 CSS 的放置说明。

为每张卡片选择 `风格 × 布局 × 框架` — 你可以在卡片之间改变所有三个，只要过渡读起来很流畅。一个常见的节奏：打开 `editorial × overlay × clean`，切换到 `audit × split × hairline` 用于数据卡片，结束于 `whiteboard × pip × polaroid`。

10种样式是技能端的样式设计令牌，**不是组合级的主题**——
它们不需要在`storyboard.composition`中声明；它们存在于每个卡片的HTML内部。`themeId`字段仍然可以选择组合级的调色板（上表），该调色板控制页面主体背景和视频边框装饰。

#### 布局组合（卡片 + 视频）

每张卡片有两个协调的决策定义它如何与源视频共享画布：

- **`card.zone`**（在`storyboard.json`中声明）—— 5个模式值之一；在步骤9中编写卡片宿主包装器的内联`style`时，将其解析为像素边界（根据步骤6中的表格）。
- **`#video-wrap`在当前卡片的播放时间窗口内的边界**（在组合的GSAP时间轴中强制声明）——代理将`#video-wrap`每个布局过渡到目标矩形。

模式**不**存储每张卡片的视频边界。`videoTrack.bounds`在组合级别是**一次性**的（默认为全画布）。视频“在卡片之间移动”纯粹是在`index.html`中编写的GSAP动画。没有`card.layout`字段——此文档的早期版本发明了一个；真实的模式只有`card.zone`。

**4种组合布局**（来自`references/layouts/`）—— 每个布局都是一个将`zone`与`#video-wrap`动画目标配对的配方：

| 组合布局   | 推荐的`card.zone` | GSAP目标`#video-wrap`（横向 1920×1080）                               | GSAP目标`#video-wrap`（竖向 1080×1920）                | 使用时机                                   |
| ---------- | ----------------- | --------------------------------------------------------------------- | ----------------------------------------------------------------- | ----------------------------------------- |
| `split`    | `side-panel`      | `{ left: 960, top: 0, width: 960, height: 1080 }`                     | `{ left: 0, top: 960, width: 1080, height: 960 }`（下半部分） | 讲者 + 数据并排 / 50:50权重              |
| `stack`    | `lower-third`     | `{ left: 14, top: 14, width: 1892, height: 548 }`（顶部52%）             | `{ left: 0, top: 0, width: 1080, height: 844 }`（顶部44%） | 讲者位于顶部 + 摘要卡片位于下方             |
| `pip`      | `fullscreen`      | `{ left: 1480, top: 760, width: 400, height: 300 }` + 添加`.framed`类 | `{ left: 690, top: 28, width: 360, height: 203 }` + 添加`.framed` | 内容密集型卡片 + 角落pip                 |
| `overlay`  | `video-overlay`   | `{ left: 0, top: 0, width: 1920, height: 1080 }`（全出血）             | `{ left: 0, top: 0, width: 1080, height: 1920 }`                  | 电影感 / 戏剧性 / 玻璃卡片全视频上         |

对于4:5（1080×1350），将竖向y/h值按`1350/1920 ≈ 0.703`缩放（见步骤7.0频道A / 频道B`recommendedRatio`分辨率表）。

**其他`zone`值用于一次性变体**（仍然使用`card.zone`；没有假的“布局”字段）：

| `zone`       | 解析边界                                        | 常用场景                          |
| ------------ | ------------------------------------------------------ | ------------------------------------- |
| `fullscreen` | 覆盖整个画布                                    | 英雄卡片，视频过渡到隐藏/pip         |
| `whiteboard-area` | 横向内边距40px或竖向底部45%                     | 紧密数据卡片，自由边距         |
| `lower-third`     | 底部30%带                                        | 讲头注释                         |
| `side-panel`      | 横向右42%或竖向底部40%                          | 侧边栏 / “split”配方              |
| `video-overlay`   | 全画布；期望透明卡片根                          | 玻璃覆盖全出血视频             |

你可以为每张卡片混合配方——根据什么适合当前情况选择`card.zone`，然后在卡片之间编写`#video-wrap`的GSAP过渡。

#### 故事板渲染契约

`storyboard.json`是代理内部的规划工件——没有CLI命令解析它。它的存在是为了在编写每张卡片的HTML之前保持你的时间和内容决策明确。坚持以下v3风格的形状，以便相同的轮廓驱动你在步骤9中组装的组合。

必要结构（见步骤6的完整示例）：

- `schemaVersion: 3`
- `composition: { fps, width, height, durationSeconds, layout, themeId, seed }` — 注意`durationSeconds`/`fps`/`themeId`/`layout`存在于**内部**`composition`，**不是**顶层
- `videoTrack: { sourcePath, startSec, endSec, bounds? }` — 视频边界默认为全画布
- `subtitles: { enabled, ... }`
- `cards[]` — 每张卡片有6个必要字段：`id`, `intent`, `startSec`, `endSec`, `accentIndex`, `zone`, `contentHints`

规则：

- 卡片时间保持在`composition.durationSeconds`内部，并且不应重叠，除非有意为之（使用`data-track-index`在它们这样做时控制z-order）。
- 视觉细节存在于卡片HTML片段（步骤8）中，**不**在`contentHints`。`contentHints`是你自己的结构化提示，用于设计卡片；渲染的外观是HTML。
- 保持故事板的形状稳定——尽管没有任何东西解析它，但在编写步骤8/9时你会阅读它，一致性保持了卡片ID和时间同步。
- 代理端决策，如“我选择了覆盖 × 几何 × 干净”，**不**属于`storyboard.json`——将它们保留在工作内存中，并在编写卡片HTML + GSAP过渡时使用它们。

**透明卡片背景用于与视频共享画布的卡片。**
当GSAP过渡使视频在卡片后面或旁边可见时（覆盖配方、pip配方或任何`card.zone = 'lower-third' | 'video-overlay'`时刻），卡片的`.root`**必须**不绘制完全不透明的背景——否则它会遮挡视频。有两种模式：

```css
/* 模式A：透明根，页面主体提供奶油背景 */
html,
body {
  background: var(--bg);
}
.card[data-card-id="card-X"] .root {
  background: transparent;
}

/* 模式B：显式每张卡片的背景仅用于全屏卡片 */
.card[data-card-id="card-hero"] .root {
  background: var(--bg);
}
.card[data-card-id="card-overlay"] .root {
  background: transparent;
}
```

对于`side-panel`-zone卡片（split配方），卡片宿主已经是画布的一半，所以不透明的卡片背景是没问题的——它只覆盖它的一半。

### 8. 编写每张卡片的HTML

为每张卡片创建`$WORK_DIR/public/cards/{card-id}.html`。每个文件包含一个遵循此契约的单个根HTML片段：

#### 卡片HTML契约

```html
<div class="card" data-card-id="{cardId}">
  <style>
    /* 必须：每个规则以`.card[data-card-id="{cardId}"]`开头 */
    .card[data-card-id="card-01"] .root {
      width: 100%; height: 100%;
      display: flex; ...;
      font-family: 'Caveat', 'LXGW WenKai TC', serif;
      color: var(--text);
      background: var(--bg);
    }
    .card[data-card-id="card-01"] .title { font-size: 84px; ... }
  </style>

  <div class="root">
    <h1
      id="card-01-title"
      data-anim="kinetic-chars"
      data-anim-at="0.3"
      data-anim-duration="0.5"
      data-anim-stagger="0.04"
      data-anim-pattern="pop"
    >
      <span class="char">S</span>
      <span class="char">u</span>
    </h1>
    <div
      id="card-01-line"
      data-anim="grow-x"
      data-anim-at="0.65"
      data-anim-duration="0.5"
      data-anim-target-w="420"
      style="width:0;height:8px;background:var(--accent-0);border-radius:4px;"
    ></div>
  </div>
</div>
```

**硬规则**（`hyperframes`检查器将拒绝违规）：

- 单个根`<div class="card" data-card-id="{cardId}">`
- 内联`<style>`规则**必须**以上述作用域选择器开头
- **没有`<script>`标签**
- **没有外部URL**在`src=` / `href=`（没有CDN，没有远程字体）
- **没有内联事件处理程序**（`onclick=`等）
- 所有资源通过相对路径到相同的`public/`目录
- 颜色通过`var(--accent-N)`等跨主题移植

**动画是声明，不是编码。** 仅使用`data-anim-*`属性；永远不要编写`<script>`来动画。你将每个`data-anim-*`声明编译成步骤9中的单个主GSAP时间轴。

#### 卡片尺寸——竖向优先于移动端

10个`references/styles/*.html`是为**1920×1080横向**预览尺寸的。当`storyboard.layout = "portrait"`（1080×1920，社交/移动的主要情况）时，**将每个视觉尺寸放大**——手机靠近屏幕，相同的像素数在横向电视风格画布上读起来更小。

| 令牌                     | 横向基线 | **竖向目标** | 缩放         |
| ------------------------- | ------------------ | ------------------- | ------------- |
| 标题（h1/h2 英雄）        | 64–96px            | **88–132px**        | ×1.35         |
| 详情 / 正文             | 24–30px            | **30–40px**         | ×1.30         |
| 开头 / 芯片标签           | 14–16px            | **18–22px**         | ×1.30         |
| 时间码 / 元数据           | 12–14px            | **16–18px**         | ×1.30         |
| 数据块主数字             | 48–60px            | **64–88px**         | ×1.40         |
| 行高乘数                  | 1.05–1.5           | 相同                | (不缩放)     |

**经验法则：** `portraitPx = round(landscapePx × 1.3)`，然后向下舍入到附近的4px倍数以获得视觉节奏。英雄标题可能高达×1.4；小元数据文本保持在×1.2以避免拥挤。

填充在竖向时**略微缩小**——卡片更窄，所以大的横向填充（40–64px）会占用太多宽度。在竖向使用24–36px水平填充。

如果你正在制作一个必须适用于**两种**布局的单张卡片，优先选择卡片根的`@container`查询而不是硬编码尺寸：

```css
.card[data-card-id="X"] .root {
  container-type: inline-size;
}
.card[data-card-id="X"] .title {
  font-size: clamp(64px, 8.5cqi, 132px);
}
.card[data-card-id="X"] .detail {
  font-size: clamp(24px, 3.2cqi, 40px);
}
```

但对于大多数卡片，单一布局选择就足够了——只需选择与故事板的`layout`字段匹配的尺寸表列。

#### 可用的`data-anim`类型

此列表是封闭的，并且故意如此：卡片是一个HTML片段，其运动此技能在步骤9中编译到共享的覆盖时间轴（见那里的GSAP映射表）。这就是为什么此工作流程不搜索HyperFrames组件注册表的方式——`npx hyperframes catalog`返回独立的组合，它们携带自己的时间轴，而卡片没有地方挂载一个。使用以下类型无法表达的外观，使用纯CSS在卡片的范围`<style>`内。

| 类型            | 用于             | 关键参数                                                                                      |
| --------------- | ------------------- | ----------------------------------------------------------------------------------------------- |
| `fade-in`       | 进入               | `at`, `duration`, `ease?`                                                                       |
| `fade-out`      | 退出                | `at`, `duration`, `ease?`                                                                       |
| `slide-in`      | 滑动进入         | `at`, `duration`, `from=left\|right\|top\|bottom`, `distance`                                   |
| `kinetic-chars` | 每个字符弹出        | `at`, `duration`, `stagger`, `pattern=pop\|fade` — 元素需要`<span class="char">`子元素 |
| `typewriter`    | 每个字符淡出       | 与kinetic-chars相同但默认stagger更慢                                                            |
| `count-up`      | 动画数字            | `at`, `duration`, `from`, `to`, `format=.0f\|.1f\|.2f\|,d`                                      |
| `draw-path`     | SVG路径揭示     | `at`, `duration` — 元素应该是`<path>`                                                         |
| `grow-y`        | 条形高度          | `at`, `duration`, `target-h` (px) — 元素开始`height:0`                                   |
| `grow-x`        | 条形宽度           | `at`, `duration`, `target-w` (px) — 元素开始`width:0`                                    |
| `scale-pop`     | 弹出入口        | `at`, `duration`                                                                                |
| `blur-in`       | 无焦点 → 焦点      | `at`, `duration`                                                                                |
| `mask-reveal`   | 剪辑揭示         | `at`, `duration`, `direction=left\|right\|top\|bottom`                                          |
| `morph-to`      | 任何CSS过渡        | `at`, `duration`, `props='{...JSON...}'`                                                        |

`data-anim-at`是**相对于卡片`startSec`的秒数**——当你在步骤9中将每个声明编译到GSAP时间轴时，添加卡片的`startSec`以获得绝对时间并量化为1/fps。

```html
<!doctype html>
<html lang="zh">
  <head>
    <meta charset="utf-8" />
    <style>
      @font-face {
        font-family: "Caveat";
        src: url("fonts/Caveat-400-latin.woff2") format("woff2");
        font-weight: 400;
        font-display: block;
      }
      @font-face {
        font-family: "Caveat";
        src: url("fonts/Caveat-700-latin.woff2") format("woff2");
        font-weight: 700;
        font-display: block;
      }
      @font-face {
        font-family: "LXGW WenKai TC";
        src: url("fonts/LXGWWenKaiTC-400-latin.woff2") format("woff2");
        font-weight: 400;
        font-display: block;
      }
      @font-face {
        font-family: "Inter";
        src: url("fonts/Inter-400-latin.woff2") format("woff2");
        font-weight: 400;
        font-display: block;
      }
      @font-face {
        font-family: "Inter";
        src: url("fonts/Inter-700-latin.woff2") format("woff2");
        font-weight: 700;
        font-display: block;
      }
      @font-face {
        font-family: "Virgil";
        src: url("fonts/Virgil.woff2") format("woff2");
        font-display: block;
      }

      :root {
        /* 从步骤7中的主题Id调色板表中选择——例如：经典 */
        --bg: #fff9e3;
        --text: #1e1e1e;
        --accent-0: #1971c2;
        --accent-1: #e03131;
        --accent-2: #2f9e44;
        --accent-3: #e8590c;
        --accent-4: #9c36b5;
        --font-family: "Caveat", "LXGW WenKai TC", serif;
      }
      * {
        box-sizing: border-box;
      }
      /* Body font-family 必须列出具体字体名称（不只是 var(--font-family)) —
   HyperFrames 渲染器的静态分析器在解析字体时不会展开CSS变量，因此只有var的链会触发
   `font_family_without_font_face` lint并回退到通用字体。在这里使用具体链；想要主题字体的卡片
   仍然可以内部引用 var(--font-family)。 */
      html,
      body {
        margin: 0;
        padding: 0;
        width: 100%;
        height: 100%;
        overflow: hidden;
        background: #000;
        font-family: "Inter", "Caveat", "LXGW WenKai TC", ui-sans-serif, system-ui, sans-serif;
      }
      #stage {
        position: relative;
        width: 100%;
        height: 100%;
        overflow: hidden;
      }

      /* video-wrapper 包含源视频。它的位置/大小由主时间轴随时间动画化
   （每个布局转换一个tween）。 */
      .video-wrapper {
        position: absolute;
        left: 0;
        top: 0;
        width: 1920px;
        height: 1080px;
        overflow: hidden;
        border-radius: 0;
        box-shadow: none;
      }
      .video-wrapper video {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }

      .card-host {
        position: absolute;
        pointer-events: none;
        overflow: hidden;
      }
      .card-host .card {
        position: relative;
        width: 100%;
        height: 100%;
        overflow: hidden;
      }
      .card-host .char {
        display: inline-block;
        visibility: visible;
      }

      /* 微妙的阴影+圆角用于非全屏视频框架 */
      .video-wrapper.framed {
        border-radius: 16px;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.35);
      }
    </style>
  </head>
  <body>
    <div
      id="stage"
      data-composition-id="talking-head-recut"
      data-start="0"
      data-duration="121.2"
      data-fps="30"
      data-width="1920"
      data-height="1080"
    >
      <!-- 层1：源视频——初始位置与card-01的布局匹配 -->
      <div class="video-wrapper" id="video-wrap">
        <video
          id="bg-video"
          src="input-video.mp4"
          muted
          playsinline
          data-start="0"
          data-duration="121.2"
          data-track-index="1"
        ></video>
      </div>
      <!-- 在视觉视频静音时保留源程序音频。 -->
      <audio
        id="source-audio"
        src="input-video.mp4"
        data-start="0"
        data-duration="121.2"
        data-track-index="10"
        data-volume="1"
      ></audio>

      <!-- 层2：每个card-host位于其布局规定的边界处。 -->
      <!-- 重要提示：每个card-host必须同时包含"card-host"和"clip"类。 -->
      <!--   - "card-host"  → 我们的定位+pointer-events样式                 -->
      <!--   - "clip"       → Studio和linter用来识别剪辑的标记。可见性本身来自
      data-start / data-duration，运行时无论是否包含此类都会尊重这些值
      (lint: timed_element_missing_clip_class, 警告)。 -->
      <!-- 示例：card-01 with zone="fullscreen" → card-host覆盖(0,0,1920,1080) -->
      <div
        class="card-host clip"
        data-card-id="card-01"
        data-start="1.0000"
        data-duration="6.5000"
        data-track-index="2"
        style="left:0;top:0;width:1920px;height:1080px;visibility:hidden;opacity:0;"
      >
        <!-- 在这里粘贴public/cards/card-01.html的内容 -->
      </div>

      <!-- 示例：card-02 with zone="side-panel"（分割组合布局）→ 卡片在左半部分 -->
      <div
        class="card-host clip"
        data-card-id="card-02"
        data-start="8.0000"
        data-duration="12.0000"
        data-track-index="2"
        style="left:0;top:0;width:960px;height:1080px;visibility:hidden;opacity:0;"
      >
        <!-- card-02 HTML -->
      </div>

      <!-- ...每个具有匹配resolveZoneBounds(card.zone)...的inline bounds的"card-host clip" -->

      <script src="vendor/gsap.min.js"></script>
      <script>
        (function () {
          // count-up格式化辅助函数
          window.__fmt = function (v, fmt) {
            if (typeof fmt === "string" && /^\.[0-9]+f$/.test(fmt)) {
              return Number(v).toFixed(Number(fmt.slice(1, -1)));
            }
            if (fmt === ",d") return Math.round(v).toLocaleString();
            return String(Math.round(v));
          };

          const tl = window.gsap.timeline({ paused: true });

          // ── 卡片生命周期（每张卡片一个块） ──
          // 示例：card-01 [1.0, 7.5] with kinetic-chars at +0.3, grow-x at +0.65:

          // 进入（0.4秒内淡入）
          tl.set('.card-host[data-card-id="card-01"]', { visibility: "visible" }, 1.0);
          tl.fromTo(
            '.card-host[data-card-id="card-01"]',
            { opacity: 0 },
            { opacity: 1, duration: 0.4, ease: "power2.out" },
            1.0,
          );

          // 卡片内部动画（在这里编译每个data-anim-*声明）
          tl.from(
            '.card[data-card-id="card-01"] #card-01-title .char',
            { opacity: 0, y: 8, scale: 0.8, duration: 0.5, ease: "power2.out", stagger: 0.04 },
            1.3,
          );
          tl.fromTo(
            '.card[data-card-id="card-01"] #card-01-line',
            { width: 0 },
            { width: 420, duration: 0.5, ease: "power2.out" },
            1.65,
          );

          // 退出（0.35秒内淡出，结束于endSec）
          tl.to(
            '.card-host[data-card-id="card-01"]',
            { opacity: 0, duration: 0.35, ease: "power2.in" },
            7.15,
          );
          tl.set('.card-host[data-card-id="card-01"]', { visibility: "hidden" }, 7.5);

          // ── 视频框架转换 ──
          // 当下一张卡片使用不同的组合布局时，将video-wrapper动画化到其新边界。示例：card-01 = 全屏
          // （视频隐藏在后面），card-02 = 分割组合（zone="side-panel" → 视频在右侧，卡片在左侧）。

          // card-02在8.0秒时进入分割组合。在card-01→card-02的间隙（7.5和8.0秒之间）动画化视频到
          // 右半部分。
          tl.set("#video-wrap", { className: "video-wrapper framed" }, 7.5);
          tl.to(
            "#video-wrap",
            { left: 960, top: 0, width: 960, height: 1080, duration: 0.6, ease: "power2.inOut" },
            7.5,
          );

          // card-02进入——与card-01相同模式
          tl.set('.card-host[data-card-id="card-02"]', { visibility: "visible" }, 8.0);
          tl.fromTo(
            '.card-host[data-card-id="card-02"]',
            { opacity: 0 },
            { opacity: 1, duration: 0.4, ease: "power2.out" },
            8.0,
          );
          // ...card-02内部动画...

          // ── 对每张卡片重复；如果下一张卡片的布局不同，
          //    在其进入之前插入另一个tl.to('#video-wrap', ...) tween ──

          window.__timelines = window.__timelines || {};
          window.__timelines["talking-head-recut"] = tl;
        })();
      </script>
    </div>
  </body>
</html>
```

#### GSAP语句速查表

将每个`data-anim`属性编译为GSAP语句。时间是**绝对秒** = card.startSec + data-anim-at，量化为1/fps。选择器是`.card[data-card-id="X"] #elementId`。

| data-anim                | GSAP语句模板                                                                                                                                                                                            |
| ------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `fade-in`                | `tl.fromTo(SEL, { opacity: 0 }, { opacity: 1, duration: D, ease: 'power2.out' }, T);`                                                                                                                    |
| `fade-out`               | `tl.to(SEL, { opacity: 0, duration: D, ease: 'power2.in' }, T);`                                                                                                                                              |
| `slide-in`（从左侧，距离=80） | `tl.fromTo(SEL, { opacity: 0, x: -80 }, { opacity: 1, x: 0, duration: D, ease: 'power2.out' }, T);`                                                                                                          |
| `kinetic-chars`（弹出）   | `tl.from(SEL + ' .char', { opacity: 0, y: 8, scale: 0.8, duration: D, ease: 'power2.out', stagger: S }, T);`                                                                                                  |
| `count-up`               | `(function(){const o={v:FROM};tl.to(o,{v:TO,duration:D,ease:'power2.out',onUpdate:function(){const el=document.querySelector(SEL);if(el)el.textContent=__fmt(o.v,'FMT');}},T);})();`                             |
| `draw-path`              | `(function(){const el=document.querySelector(SEL);if(el){const L=el.getTotalLength();tl.set(SEL,{strokeDasharray:L,strokeDashoffset:L},T);tl.to(SEL,{strokeDashoffset:0,duration:D,ease:'power2.inOut'},T);}})();` |
| `grow-x`（目标宽=W）     | `tl.fromTo(SEL, { width: 0 }, { width: W, duration: D, ease: 'power2.out' }, T);`                                                                                                                          |
| `grow-y`（目标高=H）     | `tl.fromTo(SEL, { height: 0 }, { height: H, duration: D, ease: 'power2.out' }, T);`                                                                                                                          |
| `scale-pop`              | `tl.fromTo(SEL, { opacity: 0, scale: 0.6 }, { opacity: 1, scale: 1, duration: D, ease: 'back.out(1.6)' }, T);`                                                                                                  |
| `mask-reveal`（方向=左）  | `tl.fromTo(SEL, { clipPath: 'inset(0 100% 0 0)' }, { clipPath: 'inset(0 0 0 0)', duration: D, ease: 'power2.inOut' }, T);`                                                                                       |

量化：`T = Math.round(absSec * fps) / fps`。在30fps时最小步长是`1/30 ≈ 0.0333s`；在JS字面量内部将四舍五入到4位小数（`.toFixed(4)`）即可。

#### 视频框架参考（每个`layout`值）

视频容器的选择器是`#video-wrap`。使用`tl.to('#video-wrap', { ...bounds }, T)`在卡片之间动画化其边界。初始边界应在元素的内联样式中设置以匹配card-01的布局。选择0.5-0.7秒的过渡持续时间，`ease: 'power2.inOut'`。

**装饰性框架**（`clean` / `hairline` / `polaroid`）作为`#video-wrap`的**兄弟**，随其通过布局转换。参见
[`references/frames/`](references/frames/)以获取每个框架的放置HTML、建议CSS以及它配对哪些布局。快速规则：
`overlay`布局会抑制装饰性框架（全屏视频与界面冲突）；PiP布局已经有自己的药丸处理（边框半径+白色环+阴影），因此仅在`split` / `stack`顶部添加装饰性框架。

**GSAP目标查找表**为`#video-wrap`按组合布局（横向1920×1080——对于纵向&4:5请参阅`references/layouts/*.html`，其中列出了所有三种比例）：

| 组合布局                   | 典型card.zone | `#video-wrap` GSAP目标                                                 | 额外css类                            |
| -------------------------- | ------------- | --------------------------------------------------------------------- | ------------------------------------ |
| `split`                    | `side-panel`  | `{ left: 960, top: 0, width: 960, height: 1080 }`                     | —                                    |
| `stack`                    | `lower-third` | `{ left: 14, top: 14, width: 1892, height: 548 }`（顶部52%）         | —                                    |
| `pip`（右下角）            | `fullscreen`  | `{ left: 1480, top: 760, width: 400, height: 300 }`                   | `pip-pill`（边框半径+环+阴影）       |
| `pip`（左上角）            | `fullscreen`  | `{ left: 40, top: 40, width: 400, height: 300 }`                      | `pip-pill`                          |
| `overlay`（视频全屏）      | `video-overlay` | `{ left: 0, top: 0, width: 1920, height: 1080 }`（与默认值无变化） | —                                    |
| **隐藏视频**（纯图形时刻） | `fullscreen`  | `{ opacity: 0 }`（或移出画布）                                        | —                                    |

进入或离开pip时刻时切换pip-pill界面（边框半径+白色环+阴影）：

```js
// 进入pip — 添加界面
tl.set("#video-wrap", { className: "video-wrapper pip-pill" }, T);
tl.to(
  "#video-wrap",
  { left: 1480, top: 760, width: 400, height: 300, duration: 0.6, ease: "power2.inOut" },
  T,
);

// 离开pip — 回到干净全屏
tl.set("#video-wrap", { className: "video-wrapper" }, T_NEXT);
tl.to(
  "#video-wrap",
  { left: 0, top: 0, width: 1920, height: 1080, duration: 0.6, ease: "power2.inOut" },
  T_NEXT,
);
```

**卡片宿主边界匹配zone**。使用步骤6顶部表格将卡片`zone`解析为像素边界，然后将这些值写入卡片宿主的内联`style="left:Xpx;top:Ypx;width:Wpx;height:Hpx;..."`。对于`video-overlay` zone（叠加配方），卡片宿主填满整个画布——你的CSS在`.card .root`内部决定实际可见卡片的位置。

#### HyperFrames布局/动画QA规则

- 首先构建每个卡片的静态英雄框架：卡片完全可见且可读的瞬间。
- 确认视频、卡片、字幕/标题和图表不会无意中重叠。
- 确认隐藏的视频区域被框架裁剪，且不会在预期边界外可见。
- 将一个暂停的主时间轴注册为 `window.__timelines["talking-head-recut"]`。
- 在页面加载时同步构建时间轴；不要使用 `async`、`setTimeout`、Promises 或媒体 `play()` 调用。
- 在渲染路径中不要使用 `Math.random()` 或 `Date.now()`。
- 不要使用 `repeat: -1`；根据视频时长计算有限重复次数。
- 优先使用 GSAP 变换和透明度 (`x`、`y`、`scale`、`rotation`、`opacity`) 而不是布局属性 (`top`、`left`、`width`、`height`) 进行动画。
- 动画 `#video-wrap` 等包装器，而不是直接动画视频元素尺寸。
- 避免在相同元素上从多个时间轴同时动画相同属性。
- 使用 `data-track-index` 而不是 `data-layer`；使用 `data-duration` 而不是 `data-end`。
- 每个定时元素 (`card-host`、子组合等) 应包含 `class="clip"` 以及其自身类名——例如 `class="card-host clip"`。可见性本身由 `data-start` / `data-duration` 驱动：运行时将 `[data-start]` 元素门禁到其窗口，无论是否存在此类。`.clip` 是 Studio 和 GSAP clip-所有权规则识别剪辑的标记，因此省略它会使元素更难编辑和进行代码检查（代码检查：`timed_element_missing_clip_class`，警告）。
- 对于全局 `font-family`，列出具体的字体名称（`'Inter'`、`'Caveat'`、…）——而不是 CSS 变量如 `var(--font-family)`。HyperFrames 字体解析器在静态分析期间不会展开 CSS 变量（代码检查：`font_family_without_font_face`）。卡片内部仍可使用 `var(--font-family)`，因为它们的 `@font-face` 声明已加载。

### 10. 渲染到 MP4

```bash
cd "$WORK_DIR"
PRODUCER_BROWSER_GPU_MODE=hardware npx hyperframes render public \
  --skill=talking-head-recut \
  -o output.mp4 \
  --fps 30
```

`hyperframes render <dir>` 读取 `<dir>/index.html` 并生成 MP4。
规范组合保持视觉 `<video>` 静音，并挂载与根 `#source-audio` 轨道相同的源，因此渲染的 MP4 保留了 talking-head 音频，无需手动重新封装。这使用单独的音频轨道而不是 `data-has-audio="true"`，因此其音量和静音效果可以在时间轴上独立控制。
强烈建议在 macOS 上使用标志 `PRODUCER_BROWSER_GPU_MODE=hardware`（或 `--browser-gpu`）——纯软件的 Chrome 渲染在大多数笔记本电脑上会超时。

在完整渲染之前，在特定时间戳捕获单个帧进行检查：

```bash
npx hyperframes snapshot public --at 5    # → public/snapshots/frame-00-at-5s.png (单个 --at 会忽略 --out)
```

### 11. 报告结果

告知用户：

- 工作目录路径
- `storyboard.json`（您设计的卡片轮廓）
- `public/cards/*.html`（每张卡片一个 HTML）
- `public/index.html`（组装的组合）
- `output.mp4`（最终视频）
- 使用的 ASR 提供商
- 卡片数量及选择方式（一句话说明）
- 任何缺失的键或质量注意事项

**可选的实时预览（仅限请求）。** 剪辑在 `public/index.html` 内部不变，并带有覆盖层，因此预览效果忠实。**在运行期间不要打开它。** 当用户请求时，渲染后启动长时间运行的服务并报告 URL：

```bash
(cd "$WORK_DIR/public" && npx hyperframes preview --background)   # 或 `npx hyperframes play` 用于可分享链接
```

除非用户请求，否则不要删除工作目录。
