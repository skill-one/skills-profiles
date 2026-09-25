# 网站到 HyperFrames

捕获一个网站，然后从它制作一个专业的视频。

用户会说这样的话：

- "捕获 https://... 并为我制作一个 25 秒的产品发布视频"
- "把这个网站变成一个 15 秒的 Instagram 社交广告"
- "从 https://... 创建一个 30 秒的产品巡游"

工作流程有 7 个步骤。每个步骤都会产生一个工件，用于触发下一个步骤。默认情况下它是协作式的——标记为 💬 的关卡会停止并询问用户。如果用户指示自动模式（“为我决定”，“让我惊喜”），💬 用户偏好关卡会被跳过；有关如何传播的详细信息，请参阅 step-2-brief.md。

**自动模式不是“跳过所有关卡。”** 自动模式涵盖用户偏好问题（TTS 提供商、声音、颜色强调、节拍数、音乐是/否、字幕是/否——代理会代表用户做出决定）。它不包括质量验证关卡。以下在自动模式下仍然不可跳过：

- 资产审计（第 3 步）——查看接触片并说明每个资产的 USE/SKIP
- 每个节拍的 HTML 读取（第 5 步）——每个节拍的结构化证据块
- DoD 检查清单（第 6 步）——包括动画图、每个警告的 WCAG 验证、音频/动画播放
- 诚实披露部分（第 6 步）——"我未验证的内容"必须在您的最终摘要中显示

如果你发现自己推理“自动模式倾向于行动，所以我将跳过 X”——而 X 是一个验证关卡，不是一个偏好问题——这种推理是错误的。倾向于行动适用于决定要构建什么，而不是决定是否验证。

---

## 第 0 步：捕获和理解品牌

**阅读：** [references/step-0-capture.md](references/step-0-capture.md)

捕获网站，然后阅读提取的数据以了解 **品牌和产品**——它做什么，为谁，使用什么声音，处于什么情绪中。捕获的资产是稍后使用的品牌工具包，而不是视频的构建块。

**关卡：** 打印网站摘要——先策略后（产品做什么，为谁，品牌声音）再资产/颜色/字体清单。

---

## 第 1 步：品牌标识

**阅读：** [references/step-1-design.md](references/step-1-design.md)

编写 DESIGN.md——一个涵盖视觉标识的品牌速查表：颜色、字体、组件样式、布局原则。使用 `design-styles.json` 获取确切的计算值。

**快速选项：** 对于快节奏视频（每节拍一个广告牌），DESIGN.md 可以是颜色+字体+可做/不可做的 50 行摘要——不是 300 行文档。第 5 步中的子代理提示会直接粘贴品牌价值，因此 DESIGN.md 的深度仅适用于复杂构图。

**关卡：** `DESIGN.md` 存在（任何长度）且至少包含：调色板、字体选择和可做/不可做。

---

## 第 2 步：策略和消息

**阅读：** [references/step-2-brief.md](references/step-2-brief.md)、[references/capabilities.md](references/capabilities.md)（扫描目录——仅当需要时深入探讨）

在讨论视觉或资产之前，与用户就 **视频必须传达的内容** 保持一致。解析用户的提示——他们可能已经给出了视频类型和风格。只问缺失的内容：这个视频必须说的唯一事情、叙事弧和受众。

**关卡：** 视频类型、时长、格式和——关键地——消息和叙事弧已锁定。没有这些，第 3 步无法编写以概念为先的故事板。

---

## 第 3 步：故事板+脚本 💬

**阅读：** [references/step-3-storyboard.md](references/step-3-storyboard.md)

以概念为先编写故事板：消息→叙事弧→服务于弧的节拍→每个节拍的技巧→在最后传递品牌点缀。然后编写与匹配的旁白脚本。向用户展示两者，并提供按节拍总结。迭代直到他们批准。

**关卡：** `STORYBOARD.md` + `SCRIPT.md` 存在且用户已批准计划。

---

## 第 4 步：旁白、时间+字幕 💬

**阅读：** [references/step-4-vo.md](references/step-4-vo.md)

如果第 2 步说不需要旁白——询问背景音乐，然后跳到第 5 步。否则：询问用户哪个 TTS 提供商（HeyGen TTS、ElevenLabs 或 Kokoro），生成音频，转录，将时间戳映射到节拍。然后询问字幕。

**关卡：** 要么 (a) 没有请求旁白且故事板有手动节拍时间，要么 (b) `narration.wav` + `transcript.json` 存在且节拍时间已更新为实际持续时间。

---

## 第 5 步：构建构图

**阅读：** `hyperframes` 技能（加载它——每条规则都很重要）
**阅读：** [references/step-5-build.md](references/step-5-build.md)

按照故事板（第 3 步）中选择的架构和节奏构建 index.html 和构图。子代理在每个节拍上运行 `hyperframes lint` 和 `hyperframes snapshot`，然后报告回主代理。

**关卡：** 每个主代理都按顺序阅读 `compositions/beat-N.html` 并对照 DESIGN.md 和 STORYBOARD.md。每个节拍的检查清单位于 [step-5-build.md](references/step-5-build.md)。

---

## 第 6 步：验证和交付

**阅读：** [references/step-6-validate.md](references/step-6-validate.md)

检查、验证、按视频长度缩放快照（公式：`max(beats × 3, ceil(duration_seconds / 2))`），并审查每个快照。在交付前修复问题。交付本地 Studio 项目 URL——仅在用户明确请求时才渲染为 MP4。

**交付您引以为傲的内容。** 在交接之前，问问自己：我会把带有我名字的社交媒体上发布这个吗？如果不是，修复所有问题。

**关卡：** `npx hyperframes lint` 和 `npx hyperframes validate` 通过且无错误，并且最终响应包含活动 Studio 项目 URL。

---

## 快速参考

### 视频类型

按视频类型划分的典型约束——用作起点，而不是公式。节拍数应根据内容和旁白来确定，而不是目标范围。

| 类型                  | 典型时长 | 时长驱动    | 旁白             |
| --------------------- | ---------------- | ------------------ | --------------------- |
| 社交广告（IG/TikTok） | 10–15s           | 平台限制     | 可选              |
| 产品演示          | 30–60s           | 脚本长度      | 全旁白        |
| 功能公告  | 15–30s           | 功能复杂性 | 全旁白        |
| 品牌轮播            | 20–45s           | 音乐曲目        | 可选，音乐重点 |
| 发布预告         | 10–20s           | 钩子能量        | 最小               |

节拍数故意不在此表中——它应来自故事板，而不是“社交广告 = 3-4 节拍。” 复杂产品的社交广告可能需要 5 个精心安排的节拍。有一个强视觉主题的品牌轮播可能需要 3 个。

### 格式

- **横屏：** 1920x1080（默认）
- **竖屏：** 1080x1920（Instagram 故事，TikTok）
- **方形：** 1080x1080（Instagram 信息流）

### 参考文件

| 文件                                                                               | 何时阅读                                                                                                                                   |
| ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| [step-0-capture.md](references/step-0-capture.md)                                  | 第 0 步——捕获，理解品牌和产品，编写先策略后网站摘要                                                          |
| [step-1-design.md](references/step-1-design.md)                                    | 第 1 步——编写 DESIGN.md 品牌速查表（5 个部分，250-350 行；50 行快速路径用于广告牌风格的社交广告）                       |
| [step-2-brief.md](references/step-2-brief.md)                                      | 第 2 步——与用户就消息、叙事弧、受众保持一致                                                                                   |
| [capabilities.md](references/capabilities.md)                                      | 第 2 步和第 5 步——HyperFrames 能做什么的完整清单（24 个部分）。在简报期间扫描目录，在构建期间深入特定部分                 |
| [step-3-storyboard.md](references/step-3-storyboard.md)                            | 第 3 步——故事板+脚本（组合）与用户审查关卡                                                                                  |
| [step-4-vo.md](references/step-4-vo.md)                                            | 第 4 步——TTS 提供商选择、生成、时间                                                                                               |
| [step-5-build.md](references/step-5-build.md)                                      | 第 5 步——构建 index.html + 构图                                                                                                       |
| [step-6-validate.md](references/step-6-validate.md)                                | 第 6 步——检查、验证、按视频长度缩放快照、预览                                                                           |
| [techniques.md](../hyperframes/references/techniques.md)                           | 第 3 步和第 5 步——13 个原始动画技巧与代码模式（改编，不要复制粘贴）                                                   |
| [html-in-canvas-patterns.md](../hyperframes/references/html-in-canvas-patterns.md) | 第 5 步——HTML-in-Canvas 效果的完整代码模式（存在于 hyperframes 技能中）                                                    |
