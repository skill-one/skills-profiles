# 图形叠加

图形叠加（Graphic Overlays）处理一个本地视频，使其**完整播放**，并在其上叠加一系列**定时设计的图形卡片**，包括标题、下三分屏、数据调用、引言、侧面板、画中画等，与正在讲述的内容同步。代理设计卡片（时间+内容），**直接在对话中编写每个卡片的HTML**，然后组装成一个单一的组合HTML，并通过`hyperframes`渲染为MP4。没有固定的原型列表，也没有规定的卡片结构——叠加效果来自实际文本内容。

> **在构建前确认路线。** 此技能将一个**现有的说话头片段**与**设计的图形卡片**（标题、下三分屏、数据调用、引言、侧面板、PiP）打包。如果用户想要**纯文本字幕/字幕**（ spoken words as text）→ `/embedded-captions`；一个**单个短的无旁白**元素（一个logo sting / lower-third）→ `/motion-graphics`。**片段保持原样播放**——重新计时、重新着色、重新构图、重新排序或音频属于NLE编辑，**不在范围内**。从URL/主题/PR构建→创作工作流程。不确定叠加效果与字幕的区别？**先阅读 `/hyperframes`。**

> **`embedded-captions` 的图形包装兄弟。** 字幕将 spoken words 作为可读字幕添加；这会在播放的视频上添加 designed graphics。纯字幕 → `embedded-captions`。从零开始构建视频 → 创作工作流程 (`product-launch-video` / `faceless-explainer` / …)。

工作目录中的可检查中间文件：

- `metadata.json` — 时长 / 宽度 / 高度 / fps
- `audio.mp3` — 提取的音频
- `transcript.json` — 一个扁平的**单词数组** `[{ text, start, end }, …]` (Whisper; 没有 `segments`，没有 `words` 包装)
- `storyboard.json` — 轻量级卡片轮廓（代理的计划）
- `public/cards/card-XX.html` — 每个卡片一个HTML片段
- `public/index.html` — 最终组装的组合
- `output.mp4` — 渲染的视频

## CLI解析

```bash
# hyperframes — 转录（本地 Whisper）+ 渲染组装的HTML到MP4
npx hyperframes --help
```

此技能完全在**hyperframes** CLI上运行，并依赖系统`ffmpeg` / `ffprobe`。转录是通过`hyperframes transcribe`进行的本地**Whisper**——不需要第三方服务、API密钥或速率限制代理。

## 工作流程

### 1. 检查环境

```bash
npx hyperframes doctor          # ffmpeg, 无头浏览器, 渲染依赖
# 确认捆绑资源：
ls "<SKILL_DIR>/assets/fonts" "<SKILL_DIR>/assets/vendor/gsap.min.js"
```

必需：

- `ffmpeg` / `ffprobe` (系统)
- `<SKILL_DIR>/assets/fonts/*.woff2`, `<SKILL_DIR>/assets/vendor/gsap.min.js` (捆绑在此技能中，在步骤9中部署到工作目录)

转录不需要密钥——`hyperframes transcribe`在本地运行Whisper（步骤4）。

强烈建议在macOS上为`hyperframes render`：

```bash
export PRODUCER_BROWSER_GPU_MODE=hardware
```

### 2. 创建工作目录

所有工件都位于`videos/<项目名>/`下——与其他视频工作流程（`product-launch-video` / `faceless-explainer` / `pr-to-video`）采用相同的约定。保持cwd在工作区根目录；所有内容都在此子目录下写入。

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

输出：`metadata.json`（读取`width`/`height`/`duration`；fps = 组合级别的`r_frame_rate`分数评估，例如`30000/1001 → 29.97`）+ `audio.mp3`。

### 4. 转录

```bash
npx hyperframes transcribe "$WORK_DIR/audio.mp3" -d "$WORK_DIR" --json --model small.en
```

本地**Whisper**——没有API密钥，没有代理，没有速率限制。将一个单词级别的`transcript.json`写入工作目录（单词`text` + `start` / `end`时间戳）。用于步骤6中驱动卡片时间的单词/句子时间；如果需要分段级别的块，请自行将单词分组（在标点符号/停顿处）。

**限制在媒体时长内。** Whisper可能会返回最终单词的`end`略微超过实际片段长度——将每个卡片的`endSec`和`composition.durationSeconds`限制在`metadata.json`时长内，否则渲染会在视频之后显示黑色尾部。

### 5. 修正转录

`transcript.json`是一个**扁平的单词对象数组**——`[{ "text": "...", "start": s, "end": s }, …]`（没有`segments`数组，没有`words`包装；每个单词的键是**`text`**）。读取并修正明显的ASR错误：

- 同音异义词、产品名称、技术术语、标点符号
- 在原地编辑单词的`text`；**保留其`start` / `end`** 时间戳
- 没有预先分组的`segments`数组——**当您需要分段级别的块用于卡片时间时，请自行分组单词**

### 6. 轻量级故事板草稿（在聊天中）

**不涉及CLI。** 读取`transcript.json` + `metadata.json`并直接设计卡片。`storyboard.json`是代理内部的计划工件——没有CLI命令消耗它；它的存在是为了让您在编写每个卡片的HTML之前，可以清晰地考虑时间和内容。保持形状与下面的示例一致，以便相同的轮廓可以驱动您在步骤9中编写的组合：

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
      "intent": "用说话者的焦虑深夜问题作为钩子",
      "startSec": 0.5,
      "endSec": 13.0,
      "accentIndex": 0,
      "zone": "fullscreen",
      "contentHints": {
        "kicker": "一个诚实的提问",
        "title": "11点时灵魂深处的提问",
        "detail": "客户的60秒语音信息：'如果人民币升值，那我的美元政策是一个巨大的损失吗？'"
      }
    }
  ]
}
```

**必需卡片字段：**

| 字段                   | 类型                                       | 目的                                                                                               |
| ----------------------- | ------------------------------------------ | ----------------------------------------------------------------------------------------------------- |
| `id`                    | 字符串                                     | 在卡片HTML & GSAP选择器中使用的稳定id                                                          |
| `intent`                | 字符串                                     | 自然语言描述；输入到卡片合成                                                               |
| `startSec` / `endSec`   | 数字                                     | 秒级时间（endSec > startSec）                                                                  |
| `accentIndex`           | 0 \| 1 \| 2 \| 3 \| 4                      | 5个主题强调色中的哪一个被此卡片使用                                                    |
| `zone`                  | 枚举（见下文）                           | 卡片在画布上的位置                                                                    |
| `contentHints`          | 对象                                     | 自由形式包；代理将kicker/title/detail/data/quote放在这里                                         |
| `archetype` (可选)  | 字符串                                     | 您可以附加的自由形式标签，以记住卡片的模式；缺失 = 自由形式，这是默认值                         |
| `transition` (可选) | 枚举: `cut` \| `fade` \| `slide` \| `wipe` | 声明性的卡片到卡片的过渡                                                                   |

**五个`zone`值：**

| zone              | 解析边界                                | 何时使用                             |
| ----------------- | -------------------------------------- | --------------------------------------- |
| `fullscreen`      | 覆盖整个画布                            | 英雄时刻，大数字，口号              |
| `whiteboard-area` | 插入40px边距（或肖像高度的45%）          | 密集数据 / 注释内容                  |
| `lower-third`     | 底部30%带                                | 视频上方的注释                     |
| `side-panel`      | 右侧42%（横屏）或底部40%（竖屏）         | 数据侧，视频另一侧                 |
| `video-overlay`   | 全画布，期望半透明的卡片               | 全出血视频上的注释叠加             |

当您在步骤9中组装组合时，根据上表将每个卡片的`zone`解析为卡片宿主包装上的像素边界。视频边界在组合级别**一次性设置** (`videoTrack.bounds`)；要使视频在卡片之间“移动”，请在组合的`<script>`中编写针对`#video-wrap`的GSAP缓动（见步骤9）。

**没有规定的卡片角色，没有规定的叙事弧。** 卡片来自视频实际所说的话——可能是所有引言或所有数据，可能是以数字开头或以故事开头。让文本内容驱动节奏。

**多少要点？——根据时长+密度自动推断。** 没有固定的上限。从视频时长选择一个**基础节奏**，然后根据**信息密度**进行调整。只有**下限是固定的：至少5张卡片**，即使是短视频也有节奏。

**步骤1 — 基础节奏按时长**（中等密度下自然秒/卡片）：

| 视频时长     | 基础节奏（每张卡片的秒数） | 理由                                   |
| -------------- | ------------------------ | ------------------------------------------- |
| < 60s (短轮播) | **6–8s**                 | 观众期待短形式的快速剪辑                  |
| 60s – 3 min    | **8–12s**                | 正常社交节奏                          |
| 3 – 10 min     | **12–20s**               | 给予呼吸空间；每张卡片承载更多内容       |
| 10 – 30 min    | **20–35s**               | 长形式讲座 / 采访节奏                  |
| > 30 min       | **30–60s**               | 剧集感，接近章节感                     |

**步骤2 — 密度乘数**（乘以基础节奏）：

| 文本中的信号                                                                                                    | 乘数 | 效果                   |
| ---------------------------------------------------------------------------------------------------------------- | ---------- | ------------------------ |
| **高密度** — 许多数字，明确的声明，急促的节奏，列表式枚举，每1–2句就是一个新想法 | **× 0.7**  | 切片更快，更多卡片  |
| **中等密度** — 混合流，既有数据也有叙事                                                                | **× 1.0**  | 基础节奏                |
| **低密度** — 一个长故事，重复重构，缓慢的反思节奏，单一论点展开                 | **× 1.5**  | 切片更慢，较少卡片 |

**步骤3 — 计算：**

```
secPerCard = basePace × densityMultiplier
cardCount  = max(5, round(videoDurationSec / secPerCard))
```

示例（注意——**没有上限**；长视频自然产生更多卡片）：

- **30s轮播，单个要点（低密度）** → 7 × 1.5 = 10.5s/卡片 → round(30/10.5)=3 → 向下取整到 **5** 张卡片
- **60s反思独白（低密度）** → 10 × 1.5 = 15s/卡片 → **4** → 向下取整到 **5** 张卡片
- **121s说话头，丰富的数据（高密度）** → 10 × 0.7 = 7s/卡片 → **17** 张卡片
- **5分钟采访，混合密度** → 16 × 1.0 = 16s/卡片 → **19** 张卡片
- **10分钟深入探讨，高密度** → 16 × 0.7 = 11s/卡片 → **55** 张卡片
- **30分钟讲座，中等密度** → 28 × 1.0 = 28s/卡片 → **64** 张卡片
- **1小时播客，低密度** → 45 × 1.5 = 67.5s/卡片 → **53** 张卡片

当卡片持续时间超过~15s时，计划一个更丰富的卡片（数据块，多步骤揭示，几个子要点随 staggered 动画展开）——静态的一行文本在8秒后变得无聊。对于许多卡片超过30秒的长片段，考虑**将时间线分成子组合**（每个章节一个 .html，使用`data-composition-src`挂载）以使每个文件的GSAP时间线保持可管理——见`timeline_track_too_dense` HyperFrames lint警告。

`content` 可以是一个纯字符串 ("标题：年化5.69%\n笔记：...") 或任何捕获数据的JSON形状。代理决定每张卡片的形状。

**可选尾声。** 此技能不提供**固定的品牌尾声**。如果用户想要一个结束语，请自行设计一个中性的卡片（标志+一行标语，~1.5-2s，淡入 -> 短暂停留 -> 淡出），将其追加到`cards[]`，并将`composition.durationSeconds`扩展到其`endSec`。否则在最后一个内容卡片上结束。

### 7. 确定渲染策略

#### 与用户确认视觉方向（首先做这件事）

在开始设计卡片或决定边界之前，**要求用户选择输出比例、布局、风格和卡片密度预设**。帧将根据所选布局×风格组合自动选择（见下表“自动选择帧”）。在发送问题之前，**预先计算两件事**：

1. **`recommendedRatio`** 从源视频的宽高比 (`metadata.json` 宽度 / 高度)：
   - `sourceAspect = width / height`
   - `sourceAspect ≥ 1.5` (≥ ~3:2 宽) → 推荐 **`16:9`**
   - `sourceAspect ≤ 0.7` (≤ ~9:13 高) → 推荐 **`9:16`**
   - `0.7 < sourceAspect < 1.5` (接近方形) → 推荐 **`4:5`**

   将推荐选项的标签标记为"（推荐 · 匹配源视频 X:Y）"，以便用户知道为什么推荐。

2. **`autoCount`** 从步骤6 (`max(5, round(videoSec / (basePace × densityMultiplier)))`)，以便“自动”选项的标签可以显示具体数字。

**环境兼容性——选择最佳可用问题通道。** 不是每个运行时都暴露相同的结构化问题工具。应用此顺序：

1. **`AskUserQuestion`** (Claude Code, Anthropic Console) — 使用下面的结构化4个问题调用。
2. **其他原生澄清工具**（例如`ask_question`，`request_user_input`，IDE特定的提示）— 使用相同的4个问题文本和选项列表。保留推荐标记和预计算值。
3. **没有原生工具**（Codex CLI，纯文本运行时）— **在正常对话中直接提问**。使用本节末尾的纯文本模板。保持**一条消息，4个编号的问题**（全局限制是每轮2–5个问题；我们保持在范围内）。

适用于每个通道的规则：

- 一次最多**2–5个问题**。我们这里的4个符合。
- 即使缺少信息不会阻止渲染，**也要问一次以确认影响最终输出的参数**（比例，布局，风格，cardCount）。
- 如果用户已经预先批准默认值（“直接使用默认值”，“不需要提问”，“自动选择所有内容”）或要求您不要提问——**完全跳过问题**，并使用：`recommendedRatio`，`layout="stack"`（最安全的跨比例默认值），`style`从文本内容中最中性的组中选择（编辑/数据），`autoCount`。用一句话告诉用户您选择了什么，然后继续。

**通道A — 原生 `AskUserQuestion`：**

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
      // 重新排序，使推荐选项首先出现（根据 AskUserQuestion 的惯例）。
      // 在推荐选项的标签后附加 "（推荐 · 匹配源视频 W×H）"。
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
        { label: "上下（堆叠）",    description: "视频在上方（约 52%），卡片在下方。经典组合是说话者面部 + 摘要卡片；在竖屏中也适用。" },
        { label: "画中画（pip）", description: "卡片填满画布，视频缩小为圆角窗口。当内容是主要且说话者是次要时使用。" },
        { label: "全屏叠加（overlay）", description: "视频全屏播放，卡片作为玻璃层悬浮在上方。强烈的电影感 / 情感体验。" }
      ]
    },
    {
      question: "选择卡片视觉风格（style）：",
      header: "风格组",
      multiSelect: false,
      // 注意：这三个组有意与框架自动选择矩阵的行匹配
      // 下方，因此选择一个组即可同时解决 `style` 组和
      // 框架矩阵列。成员资格是互斥的。
      options: [
        { label: "暖纸（warm-paper）", description: "学术笔记本 · 编辑大号字体 · 白板手绘 · 小红书社交。最适合访谈反思、产品发布、生活方式、情感故事。" },
        { label: "临床 / 冷（clinical）",   description: "审计杂志 · 瑞士网格 · 终端 CLI · 现代极简。最适合财务分析、调查报告、技术教程、严肃演示。" },
        { label: "实验 / 前卫（experimental）", description: "几何色块几何 · 聚光灯暗背景。最适合短视频亮点、产品发布、强烈情感、电影感。" }
      ]
    },
    {
      question: "卡片数量（节奏）：剪多少张卡片？",
      header: "卡片数量",
      multiSelect: false,
      options: [
        { label: "自动（推荐）· 约 N 张卡片", description: "根据视频时长和信息密度（见步骤 6 规则）自动推断。此运行估计约 N 张卡片。将实际 N（你的 autoCount）代入标签。" },
        { label: "较少 · 约 round(N × 0.6) 张卡片", description: "稀疏剪辑，每张卡片承载更长时间 —— 适合反思 / 慢节奏内容。" },
        { label: "较多 · 约 round(N × 1.5) 张卡片", description: "紧密剪辑，节奏更快 —— 适合顿挫 / 数据密集 / 短视频亮点内容。" }
      ]
    }
  ]
})
```

**关于“其他”** — `AskUserQuestion` 自动在卡片数量问题中添加“其他”选项。用户可以直接输入数字（例如“8”、“20”）作为卡片数量目标。解析输入为整数：如果解析成功 → 使用该值（最小 5 作为下限）；如果解析失败 → 回退到“自动”。

**频道 B — 纯文本回退**（Codex CLI、没有原生问题工具的运行时）。发布为一条普通消息，然后等待回复。项目符号式 1/2/3/4 保持回复可解析：

```
我需要与你确认四个视觉决策，然后我才会开始剪辑卡片：

1) 输出长宽比（画布）：
   A. 16:9 横屏 (1920×1080) — 电视 / YouTube / 桌面播放
   B. 9:16 竖屏 (1080×1920) — TikTok / Reels / 短视频
   C. 4:5 近竖屏 (1080×1350) — Instagram 信息流 / 适用于两个平台
   ▸ 我的推荐： <recommendedRatio>  (匹配源视频 W×H = <sourceW>×<sourceH>)

2) 整体布局（视频与卡片如何共存）：
   A. split   并排 (50/50)
   B. stack   上下 (视频在上，卡片在下)
   C. pip     画中画 (卡片填满画布，视频为圆角窗口)
   D. overlay 全屏玻璃叠加 (视频全屏，卡片为玻璃层)

3) 卡片风格组（映射到框架自动选择矩阵，选 1 个中的 3 个）：
   A. 暖纸 (warm-paper)      (学术 / 编辑 / 白板 / 小红书)
   B. 临床 / 冷 (clinical)   (审计 / 瑞士 / 终端 / 极简)
   C. 实验 (experimental)  (几何 / 聚光灯)

4) 卡片数量（节奏）：
   A. 自动（推荐） — 约 <autoCount> 张
   B. 较少 — 约 round(<autoCount> × 0.6) 张
   C. 较多 — 约 round(<autoCount> × 1.5) 张
   D. 给我一个具体数字（例如“8”、“20”）

回复格式：“1A 2C 3B 4A” 或自然语言都可以。
如果你想要所有推荐默认值，回复“default” / “auto” / “使用所有推荐”。

```

解析纯文本回复：

- 接受松散格式：`"1A 2C 3B 4A"`，`"A C B A"`，`"16:9 / pip / data / auto"`，完整句子，或 `default`。
- 如果任何答案不明确 → 仅重新询问不明确的选项（仍然在 2–5 的限制内）。
- 如果用户说“default / auto / 使用所有推荐” → 跳过，不再询问。

用户回答后（任何频道）：

1. **从比例答案中解析输出画布** — 这些是 `storyboard.composition.width / height` 的确切值：

   | 用户选择 | composition.width × height | storyboard.layout 字段                                       |
   | ------- | -------------------------- | ------------------------------------------------------------- |
   | `16:9`  | **1920 × 1080**            | `"landscape"`                                                 |
   | `9:16`  | **1080 × 1920**            | `"portrait"`                                                  |
   | `4:5`   | **1080 × 1350**            | `"portrait"` (模式将 4:5 视为竖屏 — 高度 > 宽度) |

   对于 **4:5 边界在 `references/layouts/*.html` 内** — 这些文件
   仅记录横屏（1920×1080）和竖屏（1080×1920）。对于 4:5 (1080×1350)
   通过 **从竖屏按比例缩放** 推导边界：保持水平值，缩放垂直值
   为 `1350/1920 ≈ 0.703`。示例：`overlay` 竖屏卡片 =
   `{ x: 24, y: 1280, w: 1032, h: 564 }` → 4:5 卡片 =
   `{ x: 24, y: round(1280 × 0.703), w: 1032, h: round(564 × 0.703) }`
   = `{ x: 24, y: 900, w: 1032, h: 397 }`。

2. **通过查看文本稿语气将风格组映射到特定风格** — 选择最匹配的，但保持在用户选择的组内。如果你在组内的两个特定风格之间不确定，发送第二个 `AskUserQuestion`，包含 2–4 个特定风格选项。

3. **从密度答案中解析最终卡片数量**：

   | 用户选择             | final cardCount                           |
   | ----------------------- | ----------------------------------------- |
   | Auto (recommended)      | 你已经计算的 `autoCount`                  |
   | Fewer                   | `max(5, round(autoCount × 0.6))`          |
   | More                    | `round(autoCount × 1.5)` (无上限)         |
   | Other = "<n>" (整数) | `max(5, parseInt(n))`                     |
   | Other = 任何其他内容   | 回退到 `autoCount`                      |

4. **自动选择视频框架**（框架不询问用户 — 它们跟随布局 × 风格）：

   | 布局    | 暖纸风格（学术 / 白板 / 编辑 / 小红书） | 临床风格（审计 / 瑞士 / 终端 / 极简） | 实验风格（几何 / 聚光灯） |
   | --------- | ----------------------------------------------------------- | ---------------------------------------------------- | -------------------------------------- |
   | `split`   | `polaroid`                                                  | `hairline`                                           | `clean`                                |
   | `stack`   | `polaroid`                                                  | `hairline`                                           | `clean`                                |
   | `pip`     | `clean` (pip 药丸已有边框)                                 | `clean`                                              | `clean`                                |
   | `overlay` | `clean` (全屏禁止装饰框架)                                  | `clean`                                              | `clean`                                |

5. **告诉用户你选择了什么** — 长宽比（+ 画布大小）、布局、特定风格、框架和最终卡片数量 — 然后继续步骤 7 的其余部分（每张卡片的布局、运动模式）。
6. 在工作内存中记录五个值（长宽比 / 布局 / 风格 / 框架 / 卡片数量）
   （不需要模式字段）；你将在步骤 8 写每个卡片的 HTML 和读取匹配的
   `references/<dim>/<key>.html` 以获取标记和结构时参考它们。

如果用户通过“其他”选择一个不在 10 风格库中的自由文本风格名称，将其视为设计全新卡片视觉的提示，但仍然锚定在选择的布局的边界。

#### 渲染策略输入

在步骤 7.0 锁定了长宽比 / 布局 / 风格 / 卡片数量 / 框架后，剩余的每张卡片的决策是：

- **源视频在 GSAP 目标内的适配**：视频元素有 `object-fit: cover` 并被裁剪到 `#video-wrap` 的 tween 边界。如果你想要无裁剪（例如竖屏源视频在横屏画布上不应被裁剪顶部/底部），将 tween 目标指向匹配源视频长宽比的矩形，让周围的画布显示出来（或填充卡片 / 背景板）。
- **`card.zone` 每张卡片**：根据你选择的构图布局（split → 侧面板，stack → 下三分屏，pip → 全屏，overlay → 视频叠加），或为一次性变体选择不同的区域（全屏用于英雄 / 引语，白板区域用于密集数据）。
- **`accentIndex` 每张卡片**：每张卡片提取 5 个主题强调色之一。跨卡片变化以产生节奏；当两张卡片属于同一叙事节拍时重复相同的索引。
- **运动词汇**：从 `data-anim` 类型（见下表）中选择 2–3 个可重复的模式，并坚持使用它们，使构图感觉连贯。

从这些 `themeId` 调色板中选择（在构图 `<style>` 块中使用它们作为 `--accent-N` /
`--bg` / `--text` CSS 变量）：

| themeId | 强调调色板（5 种颜色）                 | 画布背景          | 文本      |
| ------- | ----------------------------------------- | ----------------- | --------- |
| classic | `#1971c2 #e03131 #2f9e44 #e8590c #9c36b5` | `#FFF9E3` (纸) | `#1e1e1e` |
| noir    | `#4cc9f0 #f72585 #4ade80 #fb923c #a78bfa` | `#1a1a1a`         | `#f1f1f1` |
| mint    | `#0077b6 #d62828 #2d6a4f #e76f51 #7209b7` | `#e8faf0`         | `#1b4332` |
| craft   | `#bf5700 #d62728 #6c757d #e9b54a #3d5a80` | `#f6efe1`         | `#2d2d2d` |
| slate   | `#0ea5e9 #ef4444 #22c55e #f97316 #a855f7` | `#1e293b`         | `#f1f5f9` |
| mono    | `#000 #555 #888 #aaa #ccc`                | `#fff`            | `#000`    |

可用字体（woff2 在 `<SKILL_DIR>/assets/fonts/` 中，在步骤 9 阶段到工作目录）：`Caveat` (手写),
`LXGW WenKai TC` (中文手写), `Inter` (现代无衬线), `Virgil`
（几何手写）。直接通过 `@font-face` 或 `font-family` 引用。

关于视觉模式的灵感，`<SKILL_DIR>/references/styles/`
提供 10 个自包含参考卡片（学术 / 编辑 / 极简 / 聚光灯 / 几何 / 白板 / 审计 / 终端 / 瑞士 / 小红书），你可以作为起点复制 — 但**不要感到受限于匹配任何这些**。每张卡片都是你自己的设计。

#### 视觉设计库（<SKILL_DIR>/references/）

除了构图级别的 `themeId`，技能还提供了更丰富的 **参考库** 在 `<SKILL_DIR>/references/`，涵盖三个**正交**的视觉维度，你可以自由混合：

```
风格  ×  布局  ×  视频框架
 (10)      (4)         (3)
```

| 维度  | keys                                                                                              | 它决定什么                                                          |
| ---------- | ------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| **风格**  | `academic` `editorial` `minimal` `spotlight` `geom` `whiteboard` `audit` `terminal` `swiss` `xhs` | 卡片的视觉语言 — 字体、颜色、装饰、卡片内的布局 |
| **布局** | `split` `stack` `pip` `overlay`                                                                   | 源视频和卡片如何在画布上共享                                      |
| **框架**  | `clean` `hairline` `polaroid`                                                                     | 视频元素的装饰性边框                                              |

阅读 `<SKILL_DIR>/references/DESIGN_INDEX.md`
以获取完整矩阵和松散决策指南（访谈 / 产品发布 / 数据分析 /
社交剪辑 / 技术教程 / 情感故事 …）。当你决定使用特定风格 / 布局 / 框架时，阅读相应的文件：

- `references/styles/<key>.html` — 自包含卡片片段，包含该风格
  的 CSS 标记（颜色、字体、填充、装饰）和占位符 takeaway。复制
  `.card[data-card-id="ref-<key>"]` 样式块，将 data-card-id 重命名为
  你的卡片 ID，将占位符内容替换为实际 takeaway，然后完成。
- `references/layouts/<key>.html` — 横屏和竖屏的确切 `videoBounds` +
  `cardBounds`，以及用于 `storyboard.json` 的每张卡片的 `layout` 字段的
  复制粘贴 JSON 摘要。
- `references/frames/<key>.html` — 作为 `#video-wrap` 的兄弟添加的装饰性 HTML，
  以及构图 CSS 的放置说明。

每张卡片选择 `风格 × 布局 × 框架` — 你可以在卡片之间改变所有三个，只要过渡读起来很流畅。一个常见的节奏：
打开 `editorial × overlay × clean`，切换到 `audit × split × hairline`
用于数据卡片，结束于 `whiteboard × pip × polaroid`。

10 种风格是技能端设计标记，**不是构图级别的主题** — 它们不需要在
`storyboard.composition` 中声明；它们存在于每张卡片的 HTML 中。`themeId` 字段
仍然可以选择构图级别的调色板（上表），以控制页面背景和视频边框铬。

模式不会存储每张卡的视频边界。`videoTrack.bounds` 在组合级别是**一次性**的（默认为全画布）。视频在卡之间“移动”纯粹是 GSAP 动画，在 `index.html` 中编写。没有 `card.layout` 字段——此文档的早期版本发明了它；实际模式只有 `card.zone`。

**4 组合布局**（来自 `references/layouts/`）—— 每个布局都是一个将 `zone` 与 `#video-wrap` 过渡目标配对的配方：

| 组合布局 | 推荐的 `card.zone` | GSAP 目标（横向 1920×1080） | GSAP 目标（竖向 1080×1920） | 使用场景 |
| ------- | ----------------- | -------------------------- | -------------------------- | -------- |
| `split` | `side-panel`      | `{ left: 960, top: 0, width: 960, height: 1080 }` | `{ left: 0, top: 960, width: 1080, height: 960 }`（下半部分） | 讲者 + 数据并排 / 50:50 权重 |
| `stack` | `lower-third`     | `{ left: 14, top: 14, width: 1892, height: 548 }`（顶部 52%） | `{ left: 0, top: 0, width: 1080, height: 844 }`（顶部 44%） | 讲者在上部 + 摘要卡在下部 |
| `pip`   | `fullscreen`      | `{ left: 1480, top: 760, width: 400, height: 300 }` + 添加 `.framed` 类 | `{ left: 690, top: 28, width: 360, height: 203 }` + 添加 `.framed` | 内容丰富的卡 + 角落画中画 |
| `overlay` | `video-overlay`   | `{ left: 0, top: 0, width: 1920, height: 1080 }`（全出血） | `{ left: 0, top: 0, width: 1080, height: 1920 }` | 电影感 / 戏剧性 / 玻璃卡在完整视频上 |

对于 4:5（1080×1350），将竖向 y/h 值按 `1350/1920 ≈ 0.703` 缩放（见步骤 7.0 通道 A / 通道 B `recommendedRatio` 分辨率表）。

**其他 `zone` 值用于一次性变体**（仍然使用 `card.zone`；没有假的“布局”字段）：

| `zone`       | 解析边界                                        | 常用场景                          |
| ------------ | --------------------------------------------- | -------------------------------- |
| `fullscreen` | 覆盖整个画布                                    | 英雄卡，视频过渡到隐藏/画中画     |
| `whiteboard-area` | 横向内嵌 40px 边距 或 竖向底部 45%             | 密集数据卡，自由边距             |
| `lower-third` | 底部 30% 带状区域                              | 讲头注释                         |
| `side-panel` | 横向右侧 42% 或 竖向底部 40%                   | 侧边栏 / “split”配方             |
| `video-overlay` | 全画布；期望透明卡根                          | 玻璃覆盖层在全出血视频上         |

你可以为每张卡混合配方——根据什么适合当前情况选择 `card.zone`，然后在卡之间编写 `#video-wrap` 的 GSAP 过渡。

#### 故事板渲染契约

`storyboard.json` 是代理内部的规划工件——没有 CLI 命令解析它。它的存在是为了在编写每张卡的 HTML 之前保持你的时间和内容决策明确。坚持以下 v3 风格的形状，以便相同的轮廓驱动你在步骤 9 组合的布局。

必需结构（见步骤 6 获取完整示例）：

- `schemaVersion: 3`
- `composition: { fps, width, height, durationSeconds, layout, themeId, seed }` — 注意 `durationSeconds`/`fps`/`themeId`/`layout` 位于**内部** `composition`，而不是顶层
- `videoTrack: { sourcePath, startSec, endSec, bounds? }` — 视频边界默认为全画布
- `subtitles: { enabled, ... }`
- `cards[]` — 每张卡都有 6 个必需字段：`id`, `intent`, `startSec`, `endSec`, `accentIndex`, `zone`, `contentHints`

规则：

- 卡时间位于 `composition.durationSeconds` 内，并且不应重叠，除非有意为之（使用 `data-track-index` 控制重叠时的 z-order）。
- 视觉细节位于卡 HTML 片段（步骤 8）中，**不**在 `contentHints` 中。`contentHints` 是你自己的结构化提示，用于设计卡；渲染外观是 HTML。
- 保持故事板的形状稳定——尽管没有东西解析它，但在编写步骤 8/9 时会阅读它，一致性可以保持卡 ID 和时间同步。
- 代理端的决策，如“我选择了覆盖层 × 几何形状 × 干净”，**不**属于 `storyboard.json`——将它们保留在工作内存中，并在编写卡 HTML + GSAP 过渡时使用它们。

**透明卡背景用于与视频共享画布的卡。**
当 GSAP 过渡使视频在卡后面或旁边可见（覆盖层配方、画中画配方或任何 `card.zone = 'lower-third' | 'video-overlay'` 瞬间）时，卡的 `.root` **必须**不绘制完全不透明的背景——否则它会遮挡视频。有两种模式：

```css
/* 模式 A：透明根，页面主体提供奶油背景 */
html,
body {
  background: var(--bg);
}
.card[data-card-id="card-X"] .root {
  background: transparent;
}

/* 模式 B：仅对全屏卡显式每张卡背景 */
.card[data-card-id="card-hero"] .root {
  background: var(--bg);
}
.card[data-card-id="card-overlay"] .root {
  background: transparent;
}
```

对于 `side-panel`-zone 卡（split 配方），卡宿主已经是画布的一半，所以不透明的卡背景是没问题的——它只覆盖它的一半。

### 8. 编写每张卡的 HTML

为每张卡创建 `$WORK_DIR/public/cards/{card-id}.html`。每个文件包含一个遵循此契约的单个根 HTML 片段：

#### 卡 HTML 契约

```html
<div class="card" data-card-id="{cardId}">
  <style>
    /* 必须：每个规则以 .card[data-card-id="{cardId}"] 开头 */
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

**硬规则**（`hyperframes` 检查器将拒绝违规）：

- 单个根 `<div class="card" data-card-id="{cardId}">`
- 内联 `<style>` 规则**必须**以上述作用域选择器开头
- **没有 `<script>` 标签**
- **没有外部 URL** 在 `src=` / `href=`（没有 CDN，没有远程字体）
- **没有内联事件处理程序**（`onclick=` 等）
- 所有资源通过相对路径到相同的 `public/` 目录
- 颜色通过 `var(--accent-N)` 等，以便跨主题移植

**动画是声明，不是编码。** 仅使用 `data-anim-*` 属性；永远不要编写 `<script>` 来动画。你将每个 `data-anim-*` 声明编译为步骤 9 中的单个主 GSAP 时间线。

#### 卡尺寸——竖向优先

10 个 `references/styles/*.html` 是为 **1920×1080 横向**预览尺寸的。当 `storyboard.layout = "portrait"`（1080×1920，社交/移动中的主要情况）时，**将每个视觉尺寸放大**——手机屏幕靠近，相同的像素数在横向电视式画布上读起来更小。

| token                  | 横向基线 | **竖向目标** | 缩放         |
| ---------------------- | -------- | ----------- | ------------ |
| 标题 (h1/h2 英雄)      | 64–96px  | **88–132px** | ×1.35        |
| 详情 / 正文            | 24–30px  | **30–40px**  | ×1.30        |
| 开头 / 芯片标签        | 14–16px  | **18–22px**  | ×1.30        |
| 时间码 / 元数据        | 12–14px  | **16–18px**  | ×1.30        |
| 数据块主数字            | 48–60px  | **64–88px**  | ×1.40        |
| 行高乘数               | 1.05–1.5 | 相同        | (不缩放)     |

**经验法则：** `portraitPx = round(landscapePx × 1.3)`，然后向下取整到附近的 4px 倍数以获得视觉节奏。英雄标题可能高达 ×1.4；小元数据文本保持在 ×1.2 以避免拥挤。

填充在竖向**略微缩小**——卡更窄，所以大的横向填充（40–64px）会占用太多宽度。竖向使用 24–36px 水平填充。

如果你正在制作必须适用于**两种**布局的单张卡，优先使用卡根上的 `@container` 查询，而不是硬编码尺寸：

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

但对于大多数卡，单一布局选择就足够了——只需选择与故事板 `layout` 字段匹配的尺寸表列。

#### 可用的 `data-anim` 类型

| 类型            | 用于             | 关键参数                                                                                   |
| --------------- | ---------------- | ------------------------------------------------------------------------------------------ |
| `fade-in`       | 进入             | `at`, `duration`, `ease?`                                                                    |
| `fade-out`      | 离开             | `at`, `duration`, `ease?`                                                                    |
| `slide-in`      | 滑动进入         | `at`, `duration`, `from=left\|right\|top\|bottom`, `distance`                                |
| `kinetic-chars` | 每个字符弹出     | `at`, `duration`, `stagger`, `pattern=pop\|fade` — 元素需要 `<span class="char">` 子元素     |
| `typewriter`    | 每个字符淡出     | 与 kinetic-chars 相同，但默认 stagger 更慢                                                    |
| `count-up`      | 动画数字         | `at`, `duration`, `from`, `to`, `format=.0f\|.1f\|.2f\|,d`                                  |
| `draw-path`     | SVG 路径揭示     | `at`, `duration` — 元素应该是 `<path>`                                                        |
| `grow-y`        | 条形高度         | `at`, `duration`, `target-h` (px) — 元素开始 `height:0`                                      |
| `grow-x`        | 条形宽度         | `at`, `duration`, `target-w` (px) — 元素开始 `width:0`                                       |
| `scale-pop`     | 弹出进入         | `at`, `duration`                                                                            |
| `blur-in`       | 无焦点 → 焦点   | `at`, `duration`                                                                            |
| `mask-reveal`   | 剪辑揭示         | `at`, `duration`, `direction=left\|right\|top\|bottom`                                        |
| `morph-to`      | 过渡任何 CSS     | `at`, `duration`, `props='{...JSON...}'`                                                    |

`data-anim-at` 是**相对于卡 startSec 的秒数**——当你在步骤 9 将每个声明编译到 GSAP 时间线时，添加卡的 `startSec` 以获得绝对时间并量化为 1/fps。

### 9. 组合布局 HTML

准备资源并编写 `$WORK_DIR/public/index.html`：

```bash
# SKILL_DIR 是由主机注入的（“此技能的基目录：…”）
SKILL_DIR="<SKILL_DIR>"

mkdir -p "$WORK_DIR/public/fonts" "$WORK_DIR/public/vendor" "$WORK_DIR/public/cards"
cp -n "$SKILL_DIR/assets/fonts/"*            "$WORK_DIR/public/fonts/"
cp -n "$SKILL_DIR/assets/vendor/gsap.min.js" "$WORK_DIR/public/vendor/"
# 准备输入视频——重新编码，使用密集关键帧。稀疏 GOP（关键帧间隔 > ~1s）在渲染器中搜索时冻结（在覆盖层下的冻结帧）；-g / -keyint_min 设置为你的组合 fps 使每个帧都可搜索。（将两者都设置为你的 fps — 显示 30；使用 24/25/60 以匹配。）
ffmpeg -y -i "$VIDEO_PATH" -c:v libx264 -crf 18 -g 30 -keyint_min 30 \
  -pix_fmt yuv420p -movflags +faststart -c:a aac "$WORK_DIR/public/input-video.mp4"
```

#### 组合模板

```html
<!doctype html>
<html lang="en">
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
        /* 从第 7 步的 themeId 色板表中选取 — 示例：classic */
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
      /* body 的 font-family 必须列出具体字体名称（不能仅写 var(--font-family)）—
   HyperFrames 渲染器的静态分析器在解析字体时不会展开 CSS 变量，
   因此仅使用 var 的链条会触发 `font_family_without_font_face`
   lint 警告并回退到通用字体。此处请使用具体的字体链；
   需要主题字体的卡片仍可在内部引用 var(--font-family)。 */
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

      /* video-wrapper 承载源视频。其位置/尺寸由主时间轴
   随时间进行动画驱动（每次布局切换对应一个补间动画）。 */
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

      /* 非全屏视频取景的微妙投影 + 圆角 */
      .video-wrapper.framed {
        border-radius: 16px;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.35);
      }
    </style>
  </head>
  <body>
    <div
      id="stage"
      data-composition-id="graphic-overlays"
      data-start="0"
      data-duration="121.2"
      data-fps="30"
      data-width="1920"
      data-height="1080"
    >
      <!-- 图层 1：源视频 — 初始位置与 card-01 的布局匹配 -->
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

      <!-- 图层 2：每个 card-host 位于其布局所规定的边界内。 -->
      <!-- 重要：每个 card-host 必须同时携带 "card-host" 和 "clip" 两个类。 -->
      <!--   - "card-host"  → 定位 + 指针事件样式                                     -->
      <!--   - "clip"       → HyperFrames 运行时使用该类来强制可见性，                 -->
      <!--                    仅在 data-start … data-start+data-duration 期间显示。      -->
      <!--                    缺少 "clip" 则宿主在整个视频期间保持可见，               -->
      <!--                    （lint：timed_element_missing_clip_class）。               -->
      <!-- 示例：card-01 的 zone="fullscreen" → card-host 覆盖 (0,0,1920,1080) -->
      <div
        class="card-host clip"
        data-card-id="card-01"
        data-start="1.0000"
        data-duration="6.5000"
        data-track-index="2"
        style="left:0;top:0;width:1920px;height:1080px;visibility:hidden;opacity:0;"
      >
        <!-- 在此处粘贴 public/cards/card-01.html 的内容 -->
      </div>

      <!-- 示例：card-02 的 zone="side-panel"（分屏组合布局）→ 卡片位于左半部分 -->
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

      <!-- …每张卡片对应一个 "card-host clip"，内联边界与 resolveZoneBounds(card.zone) 匹配… -->

      <script src="vendor/gsap.min.js"></script>
      <script>
        (function () {
          // 计数递增格式化器辅助函数
          window.__fmt = function (v, fmt) {
            if (typeof fmt === "string" && /^\.[0-9]+f$/.test(fmt)) {
              return Number(v).toFixed(Number(fmt.slice(1, -1)));
            }
            if (fmt === ",d") return Math.round(v).toLocaleString();
            return String(Math.round(v));
          };

          const tl = window.gsap.timeline({ paused: true });

          // ── 卡片生命周期（每张卡片一个代码块）──
          // card-01 [1.0, 7.5] 的示例，kinetic-chars 在 +0.3，grow-x 在 +0.65：

          // 入场（0.4s 淡入）
          tl.set('.card-host[data-card-id="card-01"]', { visibility: "visible" }, 1.0);
          tl.fromTo(
            '.card-host[data-card-id="card-01"]',
            { opacity: 0 },
            { opacity: 1, duration: 0.4, ease: "power2.out" },
            1.0,
          );

          // 卡片内部动画（在此处编译每个 data-anim-* 声明）
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

          // 退场（0.35s 淡出，在 endSec 结束）
          tl.to(
            '.card-host[data-card-id="card-01"]',
            { opacity: 0, duration: 0.35, ease: "power2.in" },
            7.15,
          );
          tl.set('.card-host[data-card-id="card-01"]', { visibility: "hidden" }, 7.5);

          // ── 视频取景切换 ──
          // 当下一个卡片使用不同的组合布局时，对 video-wrapper
          // 进行动画以过渡到其新边界。示例：card-01 = 全屏
          //（视频被隐藏在后方），card-02 = 分屏组合（zone="side-panel"
          // → 视频在右侧，卡片在左侧）。

          // Card-02 在 8.0s 以分屏组合布局入场。在 card-01 → card-02
          // 间隙（7.5 到 8.0s 之间）将视频动画到右半部分。
          tl.set("#video-wrap", { className: "video-wrapper framed" }, 7.5);
          tl.to(
            "#video-wrap",
            { left: 960, top: 0, width: 960, height: 1080, duration: 0.6, ease: "power2.inOut" },
            7.5,
          );

          // Card-02 入场 — 与 card-01 相同的模式
          tl.set('.card-host[data-card-id="card-02"]', { visibility: "visible" }, 8.0);
          tl.fromTo(
            '.card-host[data-card-id="card-02"]',
            { opacity: 0 },
            { opacity: 1, duration: 0.4, ease: "power2.out" },
            8.0,
          );
          // …card-02 内部动画…

          // ── 对每张卡片重复；如果下一张卡片的布局不同，
          //    在其入场前插入另一个 tl.to('#video-wrap', ...) 补间动画 ──

          window.__timelines = window.__timelines || {};
          window.__timelines["graphic-overlays"] = tl;
        })();
      </script>
    </div>
  </body>
</html>
```

#### GSAP 语句速查表

将每个 `data-anim` 属性编译为一条 GSAP 语句。时间为
**绝对秒数** = card.startSec + data-anim-at，按 1/fps 取整。
选择器为 `.card[data-card-id="X"] #elementId`。

| data-anim                       | GSAP 语句模板                                                                                                                                                                                            |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `fade-in`                       | `tl.fromTo(SEL, { opacity: 0 }, { opacity: 1, duration: D, ease: 'power2.out' }, T);`                                                                                                                              |
| `fade-out`                      | `tl.to(SEL, { opacity: 0, duration: D, ease: 'power2.in' }, T);`                                                                                                                                                   |
| `slide-in` (from=left, dist=80) | `tl.fromTo(SEL, { opacity: 0, x: -80 }, { opacity: 1, x: 0, duration: D, ease: 'power2.out' }, T);`                                                                                                                |
| `kinetic-chars` (pop)           | `tl.from(SEL + ' .char', { opacity: 0, y: 8, scale: 0.8, duration: D, ease: 'power2.out', stagger: S }, T);`                                                                                                       |
| `count-up`                      | `(function(){const o={v:FROM};tl.to(o,{v:TO,duration:D,ease:'power2.out',onUpdate:function(){const el=document.querySelector(SEL);if(el)el.textContent=__fmt(o.v,'FMT');}},T);})();`                               |
| `draw-path`                     | `(function(){const el=document.querySelector(SEL);if(el){const L=el.getTotalLength();tl.set(SEL,{strokeDasharray:L,strokeDashoffset:L},T);tl.to(SEL,{strokeDashoffset:0,duration:D,ease:'power2.inOut'},T);}})();` |
| `grow-x` (target-w=W)           | `tl.fromTo(SEL, { width: 0 }, { width: W, duration: D, ease: 'power2.out' }, T);`                                                                                                                                  |
| `grow-y` (target-h=H)           | `tl.fromTo(SEL, { height: 0 }, { height: H, duration: D, ease: 'power2.out' }, T);`                                                                                                                                |
| `scale-pop`                     | `tl.fromTo(SEL, { opacity: 0, scale: 0.6 }, { opacity: 1, scale: 1, duration: D, ease: 'back.out(1.6)' }, T);`                                                                                                     |
| `mask-reveal` (direction=left)  | `tl.fromTo(SEL, { clipPath: 'inset(0 100% 0 0)' }, { clipPath: 'inset(0 0 0 0)', duration: D, ease: 'power2.inOut' }, T);`                                                                                         |

取整规则：`T = Math.round(absSec * fps) / fps`。在 30fps 下最小步长为
`1/30 ≈ 0.0333s`；在 JS 字面量内部四舍五入到 4 位小数（`.toFixed(4)`）即可。

#### 视频取景参考（按 `layout` 值）

视频容器的选择器为 `#video-wrap`。使用 `tl.to('#video-wrap', { ...bounds }, T)`
在卡片之间对其边界进行动画。初始边界应通过内联样式设置在元素上，
以匹配 card-01 的布局。切换时长建议选择 0.5–0.7s，缓动使用 `ease: 'power2.inOut'`。

**装饰边框**（`clean` / `hairline` / `polaroid`）作为
`#video-wrap` 的**同级兄弟元素**放置，并跟随其经历布局切换。
参见
[`references/frames/`](references/frames/) 了解每种边框的放置
HTML、建议 CSS 以及适配的布局。快速规则：
`overlay` 布局会抑制装饰边框（全屏视频与边框效果冲突）；画中画布局已有
自身的小胶囊处理（圆角 + 白色描边 + 投影），因此仅在
`split` / `stack` 之上添加装饰边框。

**GSAP 目标查找表** — 各组合布局下 `#video-wrap` 的目标
（横屏 1920×1080 — 竖屏及 4:5 比例请参见 `references/layouts/*.html`，
其中列出了全部三种比例）：

| 组合布局                   | 典型 card.zone | `#video-wrap` GSAP 目标                                                 | 额外 CSS 类                            |
| ------------------------------------ | ----------------- | ------------------------------------------------------------------------- | ------------------------------------------ |
| `split`                              | `side-panel`      | `{ left: 960, top: 0, width: 960, height: 1080 }`                         | —                                          |
| `stack`                              | `lower-third`     | `{ left: 14, top: 14, width: 1892, height: 548 }`（上方 52%）               | —                                          |
| `pip`（右下角）                 | `fullscreen`      | `{ left: 1480, top: 760, width: 400, height: 300 }`                       | `pip-pill`（圆角 + 描边 + 投影） |
| `pip`（左上角）                     | `fullscreen`      | `{ left: 40, top: 40, width: 400, height: 300 }`                          | `pip-pill`                                 |
| `overlay`（视频全屏铺满）         | `video-overlay`   | `{ left: 0, top: 0, width: 1920, height: 1080 }`（与默认值无变化） | —                                          |
| **隐藏视频**（纯图形时刻） | `fullscreen`      | `{ opacity: 0 }`（或移出画布）                                     | —                                          |

在进入或离开画中画时刻时切换 pip-pill 边框效果（圆角 + 白色描边 + 投影）：

```js
// 进入画中画 — 添加边框效果
tl.set("#video-wrap", { className: "video-wrapper pip-pill" }, T);
tl.to(
  "#video-wrap",
  { left: 1480, top: 760, width: 400, height: 300, duration: 0.6, ease: "power2.inOut" },
  T,
);

// 离开画中画 — 回到干净的全屏铺满
tl.set("#video-wrap", { className: "video-wrapper" }, T_NEXT);
tl.to(
  "#video-wrap",
  { left: 0, top: 0, width: 1920, height: 1080, duration: 0.6, ease: "power2.inOut" },
  T_NEXT,
);
```

**Card-host 边界与 zone 匹配**。使用第 6 步顶部的表格将卡片的
`zone` 解析为像素边界，然后将其写入 card-host 的内联
`style="left:Xpx;top:Ypx;width:Wpx;
height:Hpx;..."`。对于 `video-overlay` zone（overlay 配方），
card-host 填满整个画布 — 你在 `.card .root` 内的 CSS
决定实际可见卡片的位置。

#### HyperFrames 布局 / 动画 QA 规则

- 首先构建每个卡片的静态英雄框架：卡片完全可见且可读的瞬间。
- 确认视频、卡片、字幕/标题和图表不会无意中重叠。
- 确认隐藏的视频区域被框架裁剪，且在预期边界之外不可见。
- 将一个暂停的主时间轴注册为 `window.__timelines["graphic-overlays"]`。
- 在页面加载时同步构建时间轴；不要使用 `async`、`setTimeout`、Promises 或媒体 `play()` 调用。
- 在渲染路径中不要使用 `Math.random()` 或 `Date.now()`。
- 不要使用 `repeat: -1`；根据视频时长计算有限重复次数。
- 对于运动，优先使用 GSAP 变换和透明度 (`x`、`y`、`scale`、`rotation`、`opacity`) 而不是布局属性 (`top`、`left`、`width`、`height`)。
- 动画化 `#video-wrap` 等包装器，而不是直接动画化视频元素的尺寸。
- 避免在相同元素上从多个时间轴同时动画化相同的属性。
- 使用 `data-track-index` 而不是 `data-layer`；使用 `data-duration` 而不是 `data-end`。
- 每个定时元素（`card-host`、子组合等）必须包含其自身类名之外的 `class="clip"` —— 例如 `class="card-host clip"`。HyperFrames 运行时使用 `.clip` 来控制可见性至 `data-start … data-start+data-duration` 窗口。没有它，元素会显示整个视频（警告：`timed_element_missing_clip_class`）。
- 对于全局 `font-family`，列出**具体的字体名称**（`'Inter'`、`'Caveat'`、…）—— 而不是 CSS 变量如 `var(--font-family)`。HyperFrames 字体解析器在静态分析期间不会展开 CSS 变量（警告：`font_family_without_font_face`）。卡片内部仍可使用 `var(--font-family)`，因为它们的 `@font-face` 声明已加载。

### 10. 渲染至 MP4

```bash
cd "$WORK_DIR"
PRODUCER_BROWSER_GPU_MODE=hardware npx hyperframes render public \
  --skill=graphic-overlays \
  -o output.mp4 \
  --fps 30
```

`hyperframes render <dir>` 读取 `<dir>/index.html` 并生成 MP4。
强烈推荐在 macOS 上使用标志 `PRODUCER_BROWSER_GPU_MODE=hardware`（或 `--browser-gpu`）—— 仅软件的 Chrome 渲染在大多数笔记本电脑上会超时。

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

**可选的实时预览（仅按请求）。** 剪片在 `public/index.html` 内保持不变并显示覆盖层，因此预览效果真实。**运行期间不要打开它。** 当用户请求时，在渲染后启动一个长时间运行的服务器并报告 URL：

```bash
(cd "$WORK_DIR/public" && npx hyperframes preview)   # 或 `npx hyperframes play` 用于可分享的链接
```

除非用户要求，否则不要删除工作目录。
