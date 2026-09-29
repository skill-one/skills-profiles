---
name: talking-head-recut
description: 将现有的真人出镜/访谈/播客视频包装，配上定时设计的图形叠加卡——动态标题、字幕条、数据标注、引言、侧边栏、画中画等，与文稿同步，在您选择的16:9/9:16/4:5画布上播放；视频内容保持原样。触发方式为“图形叠加”、“屏幕图形”、“包装/美化我的视频”。不提供纯字幕（/嵌入式字幕）。不明确时→/超帧。
---

**插件安装：** 在设置或新鲜命令之前，当此技能位于 HyperFrames 插件内时，请遵循 [插件执行规则](../hyperframes/references/plugin-installation.md)。独立安装则保留以下更新说明。

> **首先，保持此技能新鲜 — 在运行前与用户确认：** `npx hyperframes skills update talking-head-recut`。当一切正常时，这是一个快速的无操作；否则，它将在您依赖它们之前刷新此技能及其依赖的核心域技能。

# Talking Head Recut

Talking Head Recut 会对一个本地视频（**完整播放**）进行操作，在其上叠加一系列**定时设计的图形卡片**，包括标题、下三分屏、数据调用、引言、侧面板、画中画等，与正在说话的内容同步。代理设计卡片（时间 + 内容），并将每个卡片的 HTML 直接**写在对话中**，然后通过 `hyperframes` 组装成一个单一的组合 HTML 并渲染为 MP4。没有固定的原型列表，也没有规定的卡片结构——覆盖层来自实际转录的内容。

> **入口点是 `/hyperframes`。** 此技能将一个**现有的 talking-head 影片**与**设计的图形卡片**（标题、下三分屏、数据调用、引言、侧面板、PiP）打包——不是纯字幕（即口语文字）。**影片保持原样播放。** 任何其他意图——纯字幕、独立图形、从头开始制作视频——或任何不确定性 → 首先阅读 `/hyperframes`：意图层拥有所有路由决策。

> **`embedded-captions` 的图形包装兄弟。** 字幕将 _口语文字_ 作为可读字幕添加；这在此播放的视频上添加 _设计图形_。纯字幕 → `embedded-captions`。从头开始制作视频 → 创建工作流 (`product-launch-video` / `faceless-explainer` / …)。

通过 `/hyperframes` 路由，意图层仅确认输入（即哪个影片）并**宣布**渲染策略问题作为延迟询问——宽高比、布局、样式组、卡片数量保持在第 7 步，其中探测到的影片和转录内容为建议提供基础；层的运行形状问题不适用。当存在 `BRIEF.md` 时，它会包含确认的输入和任何用户注释——首先阅读它。

工作目录中的可检查中间文件：

- `metadata.json` — 时长 / 宽度 / 高度 / fps
- `audio.mp3` — 提取的音频
- `transcript.json` — 一个扁平的**单词数组** `[{ text, start, end }, …]` (Whisper；没有 `segments`，没有 `words` 包装)
- `storyboard.json` — 轻量级卡片轮廓（代理的计划）
- `public/cards/card-XX.html` — 每个卡片一个 HTML 片段
- `public/index.html` — 最终组装的组合
- `output.mp4` — 渲染的视频

## CLI 渲染

```bash
# hyperframes — 转录（本地 Whisper）+ 将组装的 HTML 渲染为 MP4
npx hyperframes --help
```

此技能完全在 **hyperframes** CLI 和系统 `ffmpeg` / `ffprobe` 上运行。转录是通过 `hyperframes transcribe` 进行的本地 **Whisper**——没有第三方服务、API 密钥或速率限制代理。

## 工作流

### 1. 检查环境

```bash
npx hyperframes doctor          # ffmpeg, 无头浏览器, 渲染依赖
# 确认捆绑资源：
ls "<SKILL_DIR>/assets/fonts" "<SKILL_DIR>/assets/vendor/gsap.min.js"
```

必需：

- `ffmpeg` / `ffprobe` (系统)
- `<SKILL_DIR>/assets/fonts/*.woff2`, `<SKILL_DIR>/assets/vendor/gsap.min.js` (捆绑在此技能中，在第 9 步部署到工作目录)

转录不需要密钥——`hyperframes transcribe` 在本地运行 Whisper（第 4 步）。

强烈推荐在 macOS 上为 `hyperframes render`：

```bash
export PRODUCER_BROWSER_GPU_MODE=hardware
```

### 2. 创建工作目录

所有工件都位于 `videos/<项目名称>/` 下——与其他视频工作流（`product-launch-video` / `faceless-explainer` / `pr-to-video`）采用相同的约定。保持 cwd 在工作区根目录；所有以下内容都写入此一个子目录下。

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

输出：`metadata.json`（读取 `width`/`height`/`duration`；fps = 评估的 `r_frame_rate` 分数，例如 `30000/1001 → 29.97`）+ `audio.mp3`。

### 4. 转录

```bash
npx hyperframes transcribe "$WORK_DIR/audio.mp3" -d "$WORK_DIR" --json --model small.en
```

本地 **Whisper**——没有 API 密钥，没有代理，没有速率限制。将一个单词级的 `transcript.json` 写入工作目录（单词 `text` + `start` / `end` 时间戳）。读取它以获取驱动卡片时间（第 6 步）的单词/句子时间；如果需要段落级块，请自行将单词分组（在标点符号/停顿处）。

**限制在媒体时长内。** Whisper 可能会返回最终单词的 `end` 略微超过实际剪辑长度——将每个卡片的 `endSec` 和 `composition.durationSeconds` 限制为 `metadata.json` 时长，否则渲染会在视频之后显示黑色尾部。

### 5. 修正转录

`transcript.json` 是一个**扁平的单词对象数组**——`[{ "text": "...", "start": s, "end": s }, …]`（没有 `segments` 数组，没有 `words` 包装；每个单词的键是**`text`**）。读取并修正明显的 ASR 错误：

- 同音异义词、产品名称、技术术语、标点符号
- 在原地编辑单词的 `text`；**保留其 `start` / `end`** 时间戳
- 没有预先分组的 `segments` 数组——**当您需要段落级块以用于卡片时间时，自行将单词分组**（在终端标点符号/停顿处）

### 6. 轻量级故事板草稿（在聊天中）

**不涉及 CLI。** 阅读 `transcript.json` + `metadata.json` 并直接设计卡片。`storyboard.json` 是代理内部的计划工件——没有 CLI 命令消耗它；它的存在是为了让您在编写每个卡片的 HTML 之前，可以清晰地思考时间和内容。保持形状与以下示例一致，以便相同的轮廓可以驱动您在第 9 步编写的组合：

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
        "title": "11 点钟的灵魂拷问",
        "detail": "客户的 60 秒语音信息：'如果人民币升值，那我的美元政策是否是一个巨大的损失？'"
      }
    }
  ]
}
```

**必需的卡片字段：**

| 字段                   | 类型                                       | 目的                                                                                               |
| ----------------------- | ------------------------------------------ | ----------------------------------------------------------------------------------------------------- |
| `id`                    | string                                     | 在卡片 HTML & GSAP 选择器中使用的稳定 ID                                                          |
| `intent`                | string                                     | 自然语言描述；输入到卡片合成                                                   |
| `startSec` / `endSec`   | number                                     | 秒级时间（endSec > startSec）                                                                  |
| `accentIndex`           | 0 \| 1 \| 2 \| 3 \| 4                      | 从 5 个主题强调色中选择哪个颜色                                                        |
| `zone`                  | 枚举（见下文）                           | 卡片在画布上的位置                                                                    |
| `contentHints`          | object                                     | 自由形式包；代理将标题/详情/数据/引言放在这里                                         |
| `archetype` (可选)  | string                                     | 您可以附加的自由形式标签，用于记住卡片的模式；缺失 = 自由形式，这是默认值 |
| `transition` (可选) | 枚举: `cut` \| `fade` \| `slide` \| `wipe` | 声明卡片之间的过渡                                                                   |

**五个 `zone` 值：**

| zone              | 解析边界                                | 使用场景                             |
| ----------------- | -------------------------------------- | --------------------------------------- |
| `fullscreen`      | 覆盖整个画布                            | 英雄时刻，大数字，口号              |
| `whiteboard-area` | 插入 40px 边距（或 45% 的肖像高度）  | 密集数据 / 注释内容                  |
| `lower-third`     | 底部 30% 带状                        | 视频上方的注释                     |
| `side-panel`      | 右侧 42%（横屏）或底部 40%（竖屏） | 数据侧，视频另一侧                 |
| `video-overlay`   | 全画布，期望半透明卡片               | 全出血视频上的注释覆盖层           |

当您在第 9 步组装组合时，根据上表将每个卡片的 `zone` 解析为卡片宿主包装上的像素边界。视频边界在组合级别（`videoTrack.bounds`）**设置一次**；要使视频在卡片之间“移动”，请在组合的 `<script>` 中编写针对 `#video-wrap` 的 GSAP 缩放（见第 9 步）。

**没有规定的卡片角色，没有规定的叙事弧。** 卡片来自视频实际说什么——可能是所有引言或所有数据，可能是以数字开头或以故事开头。让转录驱动节奏。

**多少要点？——根据时长 + 密度自动推断。** 没有固定的上限。从视频时长选择一个**基础节奏**，然后根据**信息密度**进行调整。只有**下限是固定的：至少 5 张卡片**，即使是短视频也有节奏。

**第 1 步 — 基础节奏由时长**（中等密度下的自然秒/卡片）：

| 视频时长     | 基础节奏（每张卡片的秒数） | 理由                                   |
| ------------ | ------------------------ | ------------------------------------------- |
| < 60s（短轮播） | **6–8s**                 | 观众期待短形式的快速剪辑                  |
| 60s – 3 min  | **8–12s**                | 正常社交节奏                          |
| 3 – 10 min   | **12–20s**               | 给呼吸空间；每张卡片承载更多内容         |
| 10 – 30 min  | **20–35s**               | 长形式讲座 / 采访节奏                  |
| > 30 min     | **30–60s**               | 剧集，接近章节的感觉                 |

**第 2 步 — 密度乘数**（乘以基础节奏）：

| 转录中的信号                                                                                                    | 乘数 | 效果                   |
| --------------------------------------------------------------------------------------------------------------------------- | ---------- | ------------------------ |
| **高密度** — 许多数字，明确的声明，急促的节奏，列表式枚举，每 1–2 句话就是一个新想法 | **× 0.7**  | 切片更快，更多卡片  |
| **中等密度** — 混合流，既有数据也有叙事                                                                | **× 1.0**  | 基础节奏                |
| **低密度** — 一个长故事，重复的重新框架，慢节奏的反思，单一论点展开                 | **× 1.5**  | 切片更慢，较少卡片 |

**第 3 步 — 计算：**

```
secPerCard = basePace × densityMultiplier
cardCount  = max(5, round(videoDurationSec / secPerCard))
```

示例（注意——**没有上限**；长视频自然产生更多卡片）：

- **30s 轮播，单个要点（低密度）** → 7 × 1.5 = 10.5s/卡片 → round(30/10.5)=3 → 向下取整到 **5** 张卡片
- **60s 反思独白（低密度）** → 10 × 1.5 = 15s/卡片 → **4** → 向下取整到 **5** 张卡片
- **121s talking-head，丰富的数据（高密度）** → 10 × 0.7 = 7s/卡片 → **17** 张卡片
- **5 分钟采访，混合密度** → 16 × 1.0 = 16s/卡片 → **19** 张卡片
- **10 分钟深入探讨，高密度** → 16 × 0.7 = 11s/卡片 → **55** 张卡片
- **30 分钟讲座，中等密度** → 28 × 1.0 = 28s/卡片 → **64** 张卡片
- **1 小时播客，低密度** → 45 × 1.5 = 67.5s/卡片 → **53** 张卡片

当卡片持续超过 ~15s 时，计划一个更丰富的卡片（数据块，多步骤揭示，几个子要点随 staggered 动画展开）——静态的单行文本在 8s 后会变得无聊。对于许多卡片超过 30s 的长片段，考虑将时间线**拆分为子组合**（每个章节一个 .html，使用 `data-composition-src` 挂载）以便每个文件上的 GSAP 时间线保持可管理——见 `timeline_track_too_dense` HyperFrames lint 警告。

`content` 可以是纯字符串（"标题：年化 5.69%\n笔记：..."）或任何捕获数据的 JSON 形状。代理决定每张卡片的形状。

**可选的尾声。** 此技能不提供**固定的品牌尾声**。如果用户想要一个结束语，请自行设计一个中性的卡片（标志 + 一行标语，~1.5-2s，淡入 -> 短暂停留 -> 淡出），将其追加到 `cards[]`，并将 `composition.durationSeconds` 扩展到其 `endSec`。否则在最后一个内容卡片上结束。

### 7. 确定渲染策略

#### 与用户确认视觉方向（首先执行此操作）

在您开始设计卡片或决定边界之前，**要求用户选择输出比例、布局、样式和卡片密度预设**。帧会根据选择的布局 × 样式组合自动选择（见下文“自动选择帧”表）。在发送问题之前，**预先计算两件事**：

1. **`recommendedRatio`** 从源视频的宽高比（`metadata.json` 宽度 / 高度）：
   - `sourceAspect = width / height`
   - `sourceAspect ≥ 1.5`（≥ ~3:2 宽）→ 推荐 **`16:9`**
   - `sourceAspect ≤ 0.7`（≤ ~9:13 高）→ 推荐 **`9:16`**
   - `0.7 < sourceAspect < 1.5`（接近方形）→ 推荐 **`4:5`**

   将推荐选项的标签标记为 "（推荐 · 匹配源视频 X:Y）" 以便用户知道为什么推荐它。

2. **`autoCount`** 从第 6 步（`max(5, round(videoSec / (basePace × densityMultiplier)))`）以便“自动”选项的标签可以显示具体数字。

**环境兼容性——选择最佳可用问题通道。** 不是每个运行时都暴露相同的结构化问题工具。应用此顺序：

1. **原生澄清工具** — 使用下面的结构化 4 个问题调用。
2. **其他原生澄清工具**（例如 `ask_question`，`request_user_input`，IDE 特定的提示）— 使用与相同 4 个问题文本和选项列表相同的工具。保留推荐标记和预计算值。
3. **没有原生工具**（Codex CLI，纯文本运行时）— **在正常对话中直接询问**。使用本节末尾的纯文本模板。保持它为**一条消息，4 个编号的问题**（全局限制为每轮 2–5 个问题；我们保持在范围内）。

适用于每个通道的规则：

- 每轮最多**問 2–5 個問題**。我們這裡的 4 個符合要求。
- 即使缺少信息不會阻礙渲染，也**問一次以確認影響最終輸出的關鍵參數**（比例、佈局、風格、卡片數量）。
- 如果用戶已經預先批准默認值（“直接使用默認值”、“不需要問”、“自動選擇所有項”），要求您不要問，或者運行帶有持續自動信號（“讓我驚喜”/“由我決定”——`../hyperframes/references/brief-contract.md` § 1），則**完全跳過問題**，並使用：`recommendedRatio`，`layout="stack"`（最安全的跨比例默認值），`style`從轉文本風格中最中性的組（編輯/數據）中選擇，`autoCount`。用一句話告訴用戶您選擇了什麼，然後繼續。

**頻道 A — 原生 `AskUserQuestion`：**

```
// 在調用之前預計算：
//   recommendedRatio = "16:9" | "9:16" | "4:5"
//   autoCount        = 整數（來自步驟 6）

AskUserQuestion({
  questions: [
    {
      question: "輸出視頻長寬比（畫布）：",
      header: "長寬比",
      multiSelect: false,
      // 重新排序，以便建議選項出現在第一個（根據 AskUserQuestion 惯例）。
      // 將 "（建議 · 匹配源視頻 W×H）" 添加到建議選項的標籤中。
      options: [
        { label: "16:9 (1920×1080) 横向", description: "電視 / YouTube / 桌面播放。當源視頻已是橫向時最自然；最寬的畫布。" },
        { label: "9:16 (1080×1920) 縱向", description: "TikTok / Reels / 短形式移動設備。當源視頻是縱向時最自然；原生的移動設備體驗。" },
        { label: "4:5 (1080×1350) 近縱向", description: "Instagram 信息流 / 微信朋友圈。當源視頻是近方形或您想涵蓋兩個平台時最佳。" }
      ]
    },
    {
      question: "選擇整體佈局：視頻和卡片應該如何在畫布上共存？",
      header: "佈局",
      multiSelect: false,
      options: [
        { label: "並列（分割）",  description: "視頻和卡片各佔一半的畫布。最穩定，適合採訪 / 數據並列；清晰的視覺分離。" },
        { label: "上下（堆疊）",    description: "視頻在上方（約 52%），卡片在下方。經典組合：講者臉部 + 摘要卡片；在縱向也很適用。" },
        { label: "圖像內圖像（pip）", description: "卡片填滿畫布，視頻縮小為帶有圓角的窗口。當內容是主要時，講者是次要時使用。" },
        { label: "全屏覆蓋（覆蓋）", description: "視頻全屏播放，卡片作為玻璃層浮在上方。強烈的電影感 / 情感體驗。" }
      ]
    },
    {
      question: "選擇卡片視覺風格（風格）：",
      header: "風格組",
      multiSelect: false,
      // 注意：這 3 個組有意識地匹配了框架自動選擇矩陣
      // 下方行，因此選擇一個組可以同時解決 `風格` 組和
      // 框架矩陣列。成員關係是互斥的。
      options: [
        { label: "溫暖紙張 (warm-paper)", description: "學術筆記本 · 編輯大字體 · 白板手繪 · xhs 社交。最適合採訪反思、產品發布、生活方式、情感故事。" },
        { label: "臨床 / 冷冽 (clinical)",   description: "審計雜誌 · 瑞士網格 · 終端 CLI · 現代極簡。最適合財務分析、調查報告、技術教程、嚴肅演講。" },
        { label: "實驗 / 先鋒 (experimental)", description: "幾何色塊幾何 · 聚焦暗背景。最適合短形式高亮、產品發布、強烈情感、電影感。" }
      ]
    },
    {
      question: "卡片數量（取走節奏）：剪多少張卡片？",
      header: "卡片數量",
      multiSelect: false,
      options: [
        { label: "自動（建議） · 大約 N 張卡片", description: "根據視頻持續時間和信息密度（見步驟 6 規則）自動推斷。此運行估計大約 N 張卡片。將實際 N（您的 autoCount）替換到標籤中。" },
        { label: "較少 · 大約 round(N × 0.6) 張卡片", description: "稀疏剪輯，每張卡片持續時間更長——適合反思性 / 慢節奏內容。" },
        { label: "較多 · 大約 round(N × 1.5) 張卡片", description: "緊湊剪輯，節奏更快——適合短促 / 數據密集 / 短形式高亮內容。" }
      ]
    }
  ]
})
```

**關於“其他”** — `AskUserQuestion` 自動在卡片數量問題中添加“其他”選項。用戶可以直接輸入一個數字（例如“8”、“20”）作為卡片Count目標。將輸入解析為整數：如果解析成功 → 使用該值（最小值為 5）；如果解析失敗 → 落實到“自動”。

**頻道 B — 純文本備用**（Codex CLI、沒有原生問題工具的運行時）。作為一條正常消息發送，然後等待回覆。項目式 1/2/3/4 保持回覆可解析：

```
我需要在開始剪卡片之前與您確認四個視覺決定：

1) 輸出長寬比（畫布）：
   A. 16:9 橫向 (1920×1080) — 電視 / YouTube / 桌面播放
   B. 9:16 縱向 (1080×1920) — TikTok / Reels / 短形式移動設備
   C. 4:5 近縱向 (1080×1350) — Instagram 信息流 / 適用於兩個平台
   ▸ 我的建議： <recommendedRatio>  (匹配源視頻 W×H = <sourceW>×<sourceH>)

2) 整體佈局（視頻與卡片如何共存）：
   A. 分割   並列 (50/50)
   B. 堆疊   上下 (視頻在上方，卡片在下方)
   C. pip     圖像內圖像 (卡片填滿畫布，視頻為帶有圓角的窗口)
   D. 覆蓋   全屏玻璃覆蓋 (視頻全屏，卡片為玻璃層)

3) 卡片風格組（映射到框架自動選擇矩陣，選擇 1 個中的 3 個）：
   A. 溫暖紙張 (warm-paper)      (學術 / 編輯 / 白板 / xhs)
   B. 臨床 / 冷冽 (clinical)   (審計 / 瑞士 / 終端 / 極簡)
   C. 實驗 (experimental)  (幾何 / 聚焦)

4) 卡片數量（取走節奏）：
   A. 自動（建議） — 大約 <autoCount> 張
   B. 較少 — 大約 round(<autoCount> × 0.6) 張
   C. 較多 — 大約 round(<autoCount> × 1.5) 張
   D. 给我一個具體數字（例如“8”、“20”）

回覆格式：“1A 2C 3B 4A”或自然語言都可以。
如果您想使用所有建議的默認值，回覆“default” / “auto” / “使用所有建議”。
```

解析純文本回覆：

- 接受鬆散格式：`"1A 2C 3B 4A"`，`"A C B A"`，`"16:9 / pip /
數據 / 自動"`，完整句子，或 `default`。
- 如果任何答案不清晰 → 只重新問不清晰的（仍然在 2–5 的限制內）。
- 如果用戶說“default / auto / 使用所有建議” → 不重新問。

用戶回答後（任何頻道）：

1. **從比例答案解析輸出畫布** — 這些是寫入 `storyboard.composition.width / height` 的確切值：

   | 用戶選擇 | composition.width × height | storyboard.layout 字段                                       |
   | ------- | -------------------------- | ------------------------------------------------------------- |
   | `16:9`  | **1920 × 1080**            | `"landscape"`                                                 |
   | `9:16`  | **1080 × 1920**            | `"portrait"`                                                  |
   | `4:5`   | **1080 × 1350**            | `"portrait"` (模式將 4:5 作為縱向——高度 > 寬度) |

   對於 **4:5 界限在 `references/layouts/*.html` 內** — 這些文件只記錄橫向（1920×1080）和縱向（1080×1920）。對於 4:5 (1080×1350) 通過**比例縮放從縱向推導界限**：保持水平值，縮放垂直值為 `1350/1920 ≈ 0.703`。示例：`overlay` 縱向卡片 =
   `{ x: 24, y: 1280, w: 1032, h: 564 }` → 4:5 卡片 =
   `{ x: 24, y: round(1280 × 0.703), w: 1032, h: round(564 × 0.703) }`
   = `{ x: 24, y: 900, w: 1032, h: 397 }`。

2. **將風格組映射到特定風格**，通過查看轉文本風格——選擇最匹配的，但保持在用戶選擇的組內。如果您在組內兩個特定風格之間猶豫不決，發送第二個 `AskUserQuestion`，其中包含那 2–4 個特定風格選項。

3. **從密度答案解析最終卡片Count**：

   | 用戶選擇             | final cardCount                           |
   | ----------------------- | ----------------------------------------- |
   | Auto (建議)      | the `autoCount` 你已經計算的              |
   | Fewer                   | `max(5, round(autoCount × 0.6))`          |
   | More                    | `round(autoCount × 1.5)` (沒有上限) |
   | Other = "<n>" (整數) | `max(5, parseInt(n))`                     |
   | Other = 任何其他     | 落實到 `autoCount`                  |

4. **從這個表中自動選擇視頻框架**（框架不問用戶——它們遵循佈局 × 風格）：

   | layout    | warm-paper 風格（學術 / 白板 / 編輯 / xhs） | clinical 風格（審計 / 瑞士 / 終端 / 極簡） | experimental 風格（幾何 / 聚焦） |
   | --------- | ----------------------------------------------------------- | ---------------------------------------------------- | -------------------------------------- |
   | `split`   | `polaroid`                                                  | `hairline`                                           | `clean`                                |
   | `stack`   | `polaroid`                                                  | `hairline`                                           | `clean`                                |
   | `pip`     | `clean` (pip pill 已經有邊框)                       | `clean`                                              | `clean`                                |
   | `overlay` | `clean` (全屏禁止裝飾框架)                    | `clean`                                              | `clean`                                |

5. **用一句話告訴用戶您選擇了什麼**——比例（+畫布大小）、佈局、特定風格、框架和最終卡片Count——然後繼續執行 Step 7 的剩餘部分（每張卡片的佈局、運動模式）。
6. 在工作記憶中記錄五個值（比例 / 佈局 / 風格 / 框架 / 卡片Count）（不需要模式字段）；您將在 Step 8 撰寫每張卡片的 HTML 時以及閱讀匹配的 `references/<dim>/<key>.html` 時參考它們。

如果用戶通過“其他”選擇一個不在 10 風格庫中的自由文本風格名稱，將其視為設計新卡片視覺的提示，但仍然以選擇的佈局的界限為基礎。

#### 渲染策略輸入

在比例 / 佈局 / 風格 / 卡片Count / 框架從 Step 7.0 鎖定後，剩餘的每張卡片的決定是：

- **源視頻在 GSAP 目標內的適應**：視頻元素有 `object-fit: cover`，並被裁剪到 `#video-wrap` 的動畫界限內。如果您想**不裁剪**（例如縱向源視頻在橫向畫布上不應該剪掉頂部/底部），將動畫指向一個匹配源視頻比例的矩形，讓周圍的畫布顯示出來（或填充卡片 / 背景板）。
- **`card.zone` 每張卡片**：從您選擇的組成佈局推導（分割 → 側面板，堆疊 → 下三分之二，pip → 全屏，覆蓋 → 視頻覆蓋），或者為一次性變體選擇不同的區域（全屏為英雄 / 引用，白板區域為密集數據）。
- **`accentIndex` 每張卡片**：每張卡片拉取 5 個主題色調色板中的一個。在卡片間變化以獲得節奏；當兩張卡片屬於同一敘事節拍時，重用相同的索引。
- **運動詞彙**：從 `data-anim` 類型（見後面的表格）中選擇 2–3 個可重複的模式，並堅持它們，以便組成體感一致。

從這些 `themeId` 色板中選擇（在您的組成 `<style>` 块中使用它們作為 `--accent-N` /
`--bg` / `--text` CSS 變量）：

| themeId | accent 色板（5 個顏色）                 | board bg          | text      |
| ------- | ----------------------------------------- | ----------------- | --------- |
| classic | `#1971c2 #e03131 #2f9e44 #e8590c #9c36b5` | `#FFF9E3` (紙張) | `#1e1e1e` |
| noir    | `#4cc9f0 #f72585 #4ade80 #fb923c #a78bfa` | `#1a1a1a`         | `#f1f1f1` |
| mint    | `#0077b6 #d62828 #2d6a4f #e76f51 #7209b7` | `#e8faf0`         | `#1b4332` |
| craft   | `#bf5700 #d62728 #6c757d #e9b54a #3d5a80` | `#f6efe1`         | `#2d2d2d` |
| slate   | `#0ea5e9 #ef4444 #22c55e #f97316 #a855f7` | `#1e293b`         | `#f1f5f9` |
| mono    | `#000 #555 #888 #aaa #ccc`                | `#fff`            | `#000`    |

可用的字體（woff2 在 `<SKILL_DIR>/assets/fonts/` 中，在 Step 9 中到工作目錄）：`Caveat`（手寫）,
`LXGW WenKai TC`（中文手寫）, `Inter`（現代無襯線）, `Virgil`
（幾何手寫）。直接通過 `@font-face` 或 `font-family` 參考。

關於視覺模式靈感，`<SKILL_DIR>/references/styles/`
隨附 10 個自包含的參考卡片（學術 / 編輯 / 極簡 / 聚焦 / 幾何 / 白板 / 審計 / 終端 / 瑞士 / xhs），您可以將其作為起點複製——但**不要感到受限制於匹配其中任何一個**。每張卡片都是您自己的設計。

#### 視覺設計庫（<SKILL_DIR>/references/）

除了組成級別的 `themeId`，該技能還在 `<SKILL_DIR>/references/` 中提供更豐富的**參考庫**，涵蓋三個**正交**的視覺維度，您可以自由混合：

```
風格  ×  佈局  ×  視頻框架
 (10)      (4)         (3)
```

| 維度  | keys                                                                                              | 它決定了什麼                                                          |
| ---------- | ------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| **風格**  | `academic` `editorial` `minimal` `spotlight` `geom` `whiteboard` `audit` `terminal` `swiss` `xhs` | 卡片的視覺語言 — 字體、顏色、裝飾、卡片內的佈局 |
| **佈局** | `split` `stack` `pip` `overlay`                                                                   | 源視頻和卡片如何在畫布上共享                                       |
| **框架**  | `clean` `hairline` `polaroid`                                                                     | 視頻元素周圍的裝飾性邊框                                       |

閱讀 `<SKILL_DIR>/references/DESIGN_INDEX.md`
以獲得完整的矩陣和鬆散的決策指南（採訪 / 產品發布 / 數據分析 /
社交片段 / 技術教程 / 情感故事 …）。當您決定使用特定風格 / 佈局 / 框架時，閱讀對應的文件：

- `references/styles/<key>.html` — 自包含的卡片片段，包含該風格的 CSS 代碼（顏色、字體、填充、裝飾）和一個占位符取走。複製 `.card[data-card-id="ref-<key>"]` 風格塊，將 data-card-id 更名為您卡片的名稱，將占位符內容替換為實際取走，您就完成了。
- `references/layouts/<key>.html` — 橫向和縱向的確切 `videoBounds` + `cardBounds`，以及為 `storyboard.json` 的每張卡片的 `layout` 字段準備的複製貼上 JSON 碼。
- `references/frames/<key>.html` — 作為 `#video-wrap` 的兄弟添加的裝飾性 HTML，以及組成 CSS 的放置說明。

每張卡片選擇 `風格 × 佈局 × 框架` — 只要過渡讀起來順暢，您可以在卡片間更改所有三個。常見節奏：
開啟 `editorial × overlay × clean`，切換到 `audit × split × hairline` 為數據卡片，結束於 `whiteboard × pip × polaroid`。

10种样式是技能侧面的设计令牌，**不是组合级别的主题**——
它们不需要在`storyboard.composition`中声明；它们存在于每张卡片的HTML内部。`themeId`字段仍然可以选择组合级别的调色板（上表），该调色板控制页面主体背景和视频边框装饰。

#### 布局组合（卡片 + 视频）

每张卡片有两个协调的决策定义它如何与源视频共享画布：

- **`card.zone`**（在`storyboard.json`中声明）—— 5个模式值之一；在您在步骤9中编写卡片宿主包装器的内联`style`时，将其解析为像素边界（根据步骤6中的表格）。
- **`#video-wrap`在此卡的时间窗口内的边界**（在组合的GSAP时间轴中强制声明）——代理将`#video-wrap`缓动到每个布局转换的目标矩形。

模式**不**存储每张卡片的视频边界。`videoTrack.bounds`在组合级别是**一次性**的（默认为全画布）。视频“在卡片之间移动”纯粹是在`index.html`中编写的GSAP动画。没有`card.layout`字段——此文档的早期版本发明了一个；真实的模式只有`card.zone`。

**4种组合布局**（来自`references/layouts/`）—— 每个布局都是一个将`zone`与`#video-wrap`缓动目标配对的配方：

| 组合布局   | 推荐的`card.zone` | GSAP目标`#video-wrap`（横向 1920×1080）                               | GSAP目标`#video-wrap`（竖向 1080×1920）                | 使用时机                                   |
| ---------- | ----------------- | --------------------------------------------------------------------- | ----------------------------------------------------------------- | ----------------------------------------- |
| `split`    | `side-panel`      | `{ left: 960, top: 0, width: 960, height: 1080 }`                     | `{ left: 0, top: 960, width: 1080, height: 960 }`（下半部分） | 讲者 + 数据并排 / 50:50权重              |
| `stack`    | `lower-third`     | `{ left: 14, top: 14, width: 1892, height: 548 }`（顶部52%）             | `{ left: 0, top: 0, width: 1080, height: 844 }`（顶部44%） | 讲者在上部 + 摘要卡片在下部             |
| `pip`      | `fullscreen`      | `{ left: 1480, top: 760, width: 400, height: 300 }` + 添加`.framed`类 | `{ left: 690, top: 28, width: 360, height: 203 }` + 添加`.framed` | 内容密集型卡片 + 角落pip                 |
| `overlay`  | `video-overlay`   | `{ left: 0, top: 0, width: 1920, height: 1080 }`（全出血）             | `{ left: 0, top: 0, width: 1080, height: 1920 }`                  | 电影感 / 戏剧性 / 玻璃卡片在完整视频上     |

对于4:5（1080×1350），将竖向y/h值按`1350/1920 ≈ 0.703`缩放（见步骤7.0频道A / 频道B`recommendedRatio`分辨率表格）。

**其他用于一次性变体的区域值**（仍然使用`card.zone`；没有假的“布局”字段）：

| `zone`            | 解析边界                                        | 常见用途                            |
| ----------------- | ------------------------------------------------------ | ------------------------------------- |
| `fullscreen`      | 覆盖整个画布                                    | 英雄卡片，视频缓动到隐藏/pip         |
| `whiteboard-area` | 插入40像素边距（横向）或底部45%（竖向）             | 紧密数据卡片，自由边距             |
| `lower-third`     | 底部30%带                                        | 讲头注释                           |
| `side-panel`      | 右侧42%（横向）或底部40%（竖向）                 | 侧边栏 / “split”配方              |
| `video-overlay`   | 全画布；期望透明卡片根                          | 玻璃覆盖层在全出血视频上           |

您可以为每张卡片混合配方——根据什么适合当前时刻选择`card.zone`，然后在卡片之间编写`#video-wrap`的GSAP缓动。

#### 故事板渲染契约

`storyboard.json`是代理内部的规划工件——没有CLI命令解析它。它的存在是为了在您编写每张卡片的HTML之前保持您的时机和内容决策明确。坚持以下v3风格的形状，以便相同的轮廓驱动您在步骤9中组装的组合。

必需结构（见步骤6获取完整示例）：

- `schemaVersion: 3`
- `composition: { fps, width, height, durationSeconds, layout, themeId, seed }` — 注意`durationSeconds`/`fps`/`themeId`/`layout`存在于**内部**`composition`，**不是**在顶层
- `videoTrack: { sourcePath, startSec, endSec, bounds? }` — 视频边界默认为全画布
- `subtitles: { enabled, ... }`
- `cards[]` — 每张卡片有6个必需字段：`id`, `intent`, `startSec`, `endSec`, `accentIndex`, `zone`, `contentHints`

规则：

- 卡片时间保持在`composition.durationSeconds`内部，并且不应重叠，除非有意为之（当它们确实重叠时，使用`data-track-index`控制z-order）。
- 视觉细节存在于卡片HTML片段（步骤8）中，**不**在`contentHints`中。`contentHints`是您自己的结构化提示，用于设计卡片；渲染的外观是HTML。
- 保持故事板的形状稳定——尽管没有任何东西解析它，但在编写步骤8/9时您会阅读它，一致性可以保持卡片ID和时间同步。
- 代理侧决策，如“我选择了覆盖层 × 几何形状 × 干净”，**不属于**`storyboard.json`——将它们保留在工作内存中，并在编写卡片HTML + GSAP缓动时使用它们。

**透明卡片背景用于与视频共享画布的卡片。**
当GSAP缓动将视频留在卡片后面/旁边可见时（覆盖层配方、pip配方或任何`card.zone = 'lower-third' | 'video-overlay'`时刻），卡片的`.root`**必须**不绘制完全不透明的背景——否则它会遮挡视频。有两种模式：

```css
/* 模式A：透明根，页面主体提供奶油背景 */
html,
body {
  background: var(--bg);
}
.card[data-card-id="card-X"] .root {
  background: transparent;
}

/* 模式B：仅对全屏卡片指定每张卡片的背景 */
.card[data-card-id="card-hero"] .root {
  background: var(--bg);
}
.card[data-card-id="card-overlay"] .root {
  background: transparent;
}
```

对于`side-panel`-区域卡片（split配方），卡片宿主已经是画布的一半，所以不透明的卡片背景是没问题的——它只覆盖它的一半。

### 8. 编写每张卡片的HTML

为每张卡片创建`$WORK_DIR/public/cards/{card-id}.html`。每个文件包含一个遵循此契约的单个根HTML片段：

#### 卡片HTML契约

```html
<div class="card" data-card-id="{cardId}">
  <style>
    /* 必须的：每个规则都以`.card[data-card-id="{cardId}"]`开头 */
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
- 所有资源通过相对路径进入相同的`public/`目录
- 颜色通过`var(--accent-N)`等跨主题便携

**动画是声明的，不是编码的。** 仅使用`data-anim-*`属性；永远不要编写`<script>`来动画。您将每个`data-anim-*`声明编译为步骤9中的单个主GSAP时间轴。

#### 卡片尺寸——竖向优先于移动端

10个`references/styles/*.html`是为**横向 1920×1080** 预览尺寸的。当`storyboard.layout = "portrait"`（1080×1920，社交/移动的主要情况）时，**将每个视觉尺寸放大**——手机靠近屏幕，相同的像素数在横向电视风格画布上读起来更小。

| 令牌                     | 横向基线 | **竖向目标** | 缩放         |
| ------------------------- | ------------------ | ------------------- | ------------- |
| 标题（h1/h2 英雄）        | 64–96px            | **88–132px**        | ×1.35         |
| 详情 / 正文             | 24–30px            | **30–40px**         | ×1.30         |
| 开头 / 芯片标签           | 14–16px            | **18–22px**         | ×1.30         |
| 时间码 / 元数据           | 12–14px            | **16–18px**         | ×1.30         |
| 数据块主数字             | 48–60px            | **64–88px**         | ×1.40         |
| 行高乘数                 | 1.05–1.5           | 相同                | (不缩放)      |

**经验法则：** `portraitPx = round(landscapePx × 1.3)`，然后向下舍入到附近的4像素倍数以获得视觉节奏。英雄标题可能高达×1.4；小元数据文本保持在×1.2以避免拥挤。

填充在竖向时**略微缩小**——卡片更窄，因此大的横向填充（40–64px）会占用太多宽度。在竖向使用24–36像素的水平填充。

如果您正在制作必须适用于**两种**布局的单张卡片，则优先选择卡片根上的`@container`查询，而不是硬编码尺寸：

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

但对于大多数卡片，一个单一的布局选择就足够了——只需选择与故事板`layout`字段匹配的尺寸表列。

#### 可用的`data-anim`种类

此列表是封闭的，并且故意如此：卡片是一个HTML片段，其运动由此技能在步骤9中编译到共享的覆盖层时间轴（见那里的GSAP映射表）。这就是为什么此工作流不会像组合工作流那样搜索HyperFrames组件注册表——`npx hyperframes catalog`返回独立的组合，它们携带自己的时间轴，而卡片没有挂载的地方。使用以下种类无法表达的外观，请使用卡片作用域内的`<style>`中的纯CSS。

| 种类            | 用于             | 关键参数                                                                                      |
| --------------- | ------------------- | ----------------------------------------------------------------------------------------------- |
| `fade-in`       | 进入               | `at`, `duration`, `ease?`                                                                       |
| `fade-out`      | 退出                | `at`, `duration`, `ease?`                                                                       |
| `slide-in`      | 滑动进入         | `at`, `duration`, `from=left\|right\|top\|bottom`, `distance`                                   |
| `kinetic-chars` | 每个字符弹出        | `at`, `duration`, `stagger`, `pattern=pop\|fade` — 元素需要`<span class="char">`子元素             |
| `typewriter`    | 每个字符淡出       | 与kinetic-chars相同，但默认stagger更慢                                                            |
| `count-up`      | 动画数字           | `at`, `duration`, `from`, `to`, `format=.0f\|.1f\|.2f\|,d`                                      |
| `draw-path`     | SVG路径揭示     | `at`, `duration` — 元素应该是`<path>`                                                             |
| `grow-y`        | 条形高度          | `at`, `duration`, `target-h` (px) — 元素开始`height:0`                                          |
| `grow-x`        | 条形宽度           | `at`, `duration`, `target-w` (px) — 元素开始`width:0`                                            |
| `scale-pop`     | 弹出入口        | `at`, `duration`                                                                                |
| `blur-in`       | 无焦点 → 焦点      | `at`, `duration`                                                                                |
| `mask-reveal`   | 剪辑揭示         | `at`, `duration`, `direction=left\|right\|top\|bottom`                                          |
| `morph-to`      | 缓动任何CSS       | `at`, `duration`, `props='{...JSON...}'`                                                        |

`data-anim-at`是**相对于卡片`startSec`的秒数**——当您在步骤9中将每个声明编译到GSAP时间轴时，添加卡片的`startSec`以获得绝对时间并量化为1/fps。

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
   `font_family_without_font_face` lint并回退到通用字体。在这里使用具体链；想要使用主题字体的卡片
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

      /* video-wrapper 持有源视频。它的位置/大小由主时间轴随时间动画化
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
      <!-- 重要：每个card-host必须同时包含"card-host"和"clip"类。 -->
      <!--   - "card-host"  → 我们的定位+pointer-events样式                 -->
      <!--   - "clip"       → Studio和linter用来识别剪辑的标记。可见性本身来自
      data-start / data-duration，运行时无论是否使用此类都会尊重它们
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

      <!-- ...每个具有与resolveZoneBounds(card.zone)匹配的内部边界
      的"card-host clip"... -->

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
          // 当下一张卡片使用不同的组合布局时，将视频-wrapper动画化到其新边界。示例：card-01 = 全屏
          // （视频隐藏在后面），card-02 = 分割组合（zone="side-panel" → 视频在右侧，卡片在左侧）。

          // card-02在8.0秒时进入分割组合。在card-01→card-02的间隙（7.5到8.0秒之间）动画化视频到右侧。
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
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `fade-in`                | `tl.fromTo(SEL, { opacity: 0 }, { opacity: 1, duration: D, ease: 'power2.out' }, T);`                                                                                                                    |
| `fade-out`               | `tl.to(SEL, { opacity: 0, duration: D, ease: 'power2.in' }, T);`                                                                                                                                          |
| `slide-in`（从左侧，距离=80） | `tl.fromTo(SEL, { opacity: 0, x: -80 }, { opacity: 1, x: 0, duration: D, ease: 'power2.out' }, T);`                                                                                                      |
| `kinetic-chars`（弹出）   | `tl.from(SEL + ' .char', { opacity: 0, y: 8, scale: 0.8, duration: D, ease: 'power2.out', stagger: S }, T);`                                                                                              |
| `count-up`               | `(function(){const o={v:FROM};tl.to(o,{v:TO,duration:D,ease:'power2.out',onUpdate:function(){const el=document.querySelector(SEL);if(el)el.textContent=__fmt(o.v,'FMT');}},T);})();`                               |
| `draw-path`              | `(function(){const el=document.querySelector(SEL);if(el){const L=el.getTotalLength();tl.set(SEL,{strokeDasharray:L,strokeDashoffset:L},T);tl.to(SEL,{strokeDashoffset:0,duration:D,ease:'power2.inOut'},T);}})();` |
| `grow-x`（目标宽=W）     | `tl.fromTo(SEL, { width: 0 }, { width: W, duration: D, ease: 'power2.out' }, T);`                                                                                                                        |
| `grow-y`（目标高=H）     | `tl.fromTo(SEL, { height: 0 }, { height: H, duration: D, ease: 'power2.out' }, T);`                                                                                                                        |
| `scale-pop`              | `tl.fromTo(SEL, { opacity: 0, scale: 0.6 }, { opacity: 1, scale: 1, duration: D, ease: 'back.out(1.6)' }, T);`                                                                                              |
| `mask-reveal`（方向=左）  | `tl.fromTo(SEL, { clipPath: 'inset(0 100% 0 0)' }, { clipPath: 'inset(0 0 0 0)', duration: D, ease: 'power2.inOut' }, T);`                                                                                     |

量化：`T = Math.round(absSec * fps) / fps`。在30fps时最小步长是`1/30 ≈ 0.0333s`；在JS字面量中四舍五入到4位小数（`.toFixed(4)`）即可。

#### 视频框架参考（每个`layout`值）

视频容器的选择器是`#video-wrap`。使用`tl.to('#video-wrap', { ...bounds }, T)`在卡片之间动画化其边界。初始边界应在元素的内联样式中设置以匹配card-01的布局。选择0.5-0.7秒的过渡持续时间，`ease: 'power2.inOut'`。

**装饰性框架**（`clean` / `hairline` / `polaroid`）作为`#video-wrap`的**兄弟**，随其通过布局转换。查看
[`references/frames/`](references/frames/)以获取每个框架的放置HTML、建议CSS以及它配对的布局。快速规则：
`overlay`布局抑制装饰性框架（全屏视频与界面冲突）；PiP布局已有自己的药丸处理（边框半径+白色环+阴影），因此仅在`split` / `stack`上添加装饰性框架。

**GSAP目标查找表**为`#video-wrap`按组合布局（横向1920×1080——对于纵向&4:5请查看`references/layouts/*.html`，其中列出了所有三种比例）：

| 组合布局                   | 典型card.zone | `#video-wrap` GSAP目标                                                 | 额外css类                            |
| -------------------------- | ------------- | -------------------------------------------------------------------- | ------------------------------------ |
| `split`                    | `side-panel`  | `{ left: 960, top: 0, width: 960, height: 1080 }`                     | —                                    |
| `stack`                    | `lower-third` | `{ left: 14, top: 14, width: 1892, height: 548 }`（顶部52%）         | —                                    |
| `pip`（右下）             | `fullscreen`  | `{ left: 1480, top: 760, width: 400, height: 300 }`                   | `pip-pill`（边框半径+环+阴影）       |
| `pip`（左上）             | `fullscreen`  | `{ left: 40, top: 40, width: 400, height: 300 }`                      | `pip-pill`                          |
| `overlay`（视频全屏）     | `video-overlay` | `{ left: 0, top: 0, width: 1920, height: 1080 }`（与默认无变化）     | —                                    |
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

**卡片宿主边界匹配zone**。使用步骤6顶部表格将卡片`zone`解析为像素边界，然后将这些写入卡片宿主的内联`style="left:Xpx;top:Ypx;width:Wpx;height:Hpx;..."`。对于`video-overlay` zone（叠加配方），卡片宿主填满整个画布——你的CSS在`.card .root`中决定实际可见卡片的位置。

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
- 每个定时元素（如 `card-host`、子组合等）应包含其自身类名之外的 `class="clip"` —— 例如 `class="card-host clip"`。可见性本身由 `data-start` / `data-duration` 驱动：运行时无论是否存在此类，都会将 `[data-start]` 元素门禁到其窗口中。`.clip` 是 Studio 和 GSAP clip-所有权规则识别剪辑的标记，因此省略它会使元素更难编辑和进行代码检查（代码检查：`timed_element_missing_clip_class`，警告）。
- 对于全局 `font-family`，列出具体的字体名称（如 `'Inter'`、`'Caveat'`、…）—— 而不是 CSS 变量（如 `var(--font-family)`）。HyperFrames 字体解析器在静态分析期间不会展开 CSS 变量（代码检查：`font_family_without_font_face`）。卡片内部仍可使用 `var(--font-family)`，因为它们的 `@font-face` 声明已加载。

### 10. 渲染为 MP4

```bash
cd "$WORK_DIR"
PRODUCER_BROWSER_GPU_MODE=hardware npx hyperframes render public \
  --skill=talking-head-recut \
  -o output.mp4 \
  --fps 30
```

`hyperframes render <dir>` 读取 `<dir>/index.html` 并生成 MP4。
规范化的组合保持视觉 `<video>` 静音，并挂载与根 `#source-audio` 轨道相同的源，因此渲染的 MP4 保留了说话人音频，无需手动重新封装。它使用单独的音频轨道而不是 `data-has-audio="true"`，因此其音量和静音效果可以在时间轴上独立控制。
强烈建议在 macOS 上使用标志 `PRODUCER_BROWSER_GPU_MODE=hardware`（或 `--browser-gpu`）—— 仅软件的 Chrome 渲染在大多数笔记本电脑上会超时。

在完整渲染之前，在特定时间戳捕获单个帧进行合理性检查：

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

**可选的实时预览（仅按请求提供）。** 剪辑在 `public/index.html` 内部不变，并带有覆盖层，因此预览效果忠实。**在运行期间不要打开它。** 当用户请求时，在渲染后启动长时间运行的服务器并报告 URL：

```bash
(cd "$WORK_DIR/public" && npx hyperframes preview --background)   # 或 `npx hyperframes play` 用于可分享链接
```

除非用户要求，否则不要删除工作目录。
