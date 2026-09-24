# 网站转 HyperFrames

捕获网站，从中制作专业视频。

用户可能会说：

- "捕获 https://...，制作一段25秒的产品发布视频"
- "将这个网站转换为15秒的Instagram社媒广告"
- "从 https://... 创建一段30秒的产品演示视频"

流程包含7个步骤，每个步骤产生一个工件，用于控制后续步骤。默认情况下是协作模式——标记为 💬 的关卡会停止并询问用户。如果用户发出自主模式信号（"由我决定"、"给我惊喜"），则 💬 用户偏好关卡会被跳过；请参阅 step-2-brief.md 了解该机制如何传播。

**自主模式并非"跳过所有关卡"。** 自动模式涵盖用户偏好问题（TTS提供方、音色、色彩强调、节拍数量、音乐是/否、字幕是/否——在这些情况下，代理代表用户做出决定）。它不涵盖质量验证关卡。以下内容在自动模式下仍不可跳过：

- Asset Audit（第3步）——查看拼版图并为每个资产说明使用（USE）/跳过（SKIP）的理由
- 逐节拍 HTML 阅读（第5步）——每个节拍的结构化证据区块
- DoD 检查清单（第6步）——包括动画图、逐警告项 WCAG 验证、音频/动态播放
- 诚实披露部分（第6步）——"我未验证的内容"必须出现在最终总结中

如果你发现自己这样推理——"自动模式意味着偏向行动，所以我跳过 X"——而 X 是验证关卡而非偏好问题——那么这种推理是错误的。偏向行动适用于决定 _构建什么_，而非决定 _是否验证_。

---

## 第 0 步：捕获并理解品牌

**阅读：** [references/step-0-capture.md](references/step-0-capture.md)

捕获网站，然后阅读提取的数据以理解 **品牌与产品**——它做什么，为谁服务，用什么语气，处于何种氛围。捕获的资产是后续使用的品牌工具包，而非视频的制作素材。

**关卡：** 打印网站摘要——以策略为先（产品功能、目标用户、品牌语气）在列出资产/色彩/字体清单之前。

---

## 第 1 步：品牌识别

**阅读：** [references/step-1-design.md](references/step-1-design.md)

编写 DESIGN.md——一份涵盖视觉识别的品牌速查表，包括颜色、排版、组件样式、布局原则。使用 `design-styles.json` 获取精确的已计算数值。

**速度选项：** 对于节奏快速（广告牌式逐节拍）的视频，DESIGN.md 可以是一份关于颜色、字体以及宜/忌的50行摘要——而非300行的文档。第5步的子代理提示词会直接粘贴品牌数值，因此 DESIGN.md 的深度仅对复杂构图重要。

**关卡：** `DESIGN.md` 已存在（长度不限）且至少包含：颜色调色板、字体选择，以及宜/忌。

---

## 第 2 步：策略与信息

**阅读：** [references/step-2-brief.md](references/step-2-brief.md)，[references/capabilities.md](references/capabilities.md)（扫描目录——仅在需要时深入探究特定章节）

在讨论视觉或素材之前，与用户就 **视频必须传达的内容** 达成一致。解析用户的提示词——用户可能已经提供了视频类型和风格。只询问缺失的内容：这段视频必须传达的核心内容、叙事弧线，以及目标受众。

**关卡：** 视频类型、时长、格式，以及——至关重要的是——消息与叙事弧线已锁定。没有这些内容，第3步无法编写以概念为先的分镜稿。

---

## 第 3 步：分镜 + 脚本 💬

**阅读：** [references/step-3-storyboard.md](references/step-3-storyboard.md)

先编写以概念为先的分镜稿：消息 → 叙事弧线 → 服务该弧线的节拍 → 每节拍的技术 → 结尾的品牌强调。然后编写与之一致的旁白脚本。将两者以逐节拍的摘要呈现给用户。迭代直至用户批准。

**关卡：** `STORYBOARD.md` + `SCRIPT.md` 已存在，且用户已批准该计划。

---

## 第 4 步：配音、节奏 + 字幕 💬

**阅读：** [references/step-4-vo.md](references/step-4-vo.md)

如果第2步表示无需旁白——则询问背景音乐，然后跳至第5步。否则：询问用户选择哪个TTS提供方（HeyGen TTS、ElevenLabs 或 Kokoro），生成音频，进行转写，将时间戳映射到节拍。然后询问关于字幕的问题。

**关卡：** 要么 (a) 用户未要求旁白且分镜稿包含手动节拍时间，要么 (b) `narration.wav` + `transcript.json` 已存在且节拍时间已根据实际时长更新。

---

## 第 5 步：构建构图

**阅读：** `hyperframes` 技能（加载它——每条规则都重要）
**阅读：** [references/step-5-build.md](references/step-5-build.md)

根据分镜稿（第3步）中选择的架构和节奏，构建 index.html 和构图。子代理在向回报告前，会对每个节拍运行 `hyperframes lint` 和 `hyperframes snapshot`。

**关卡：** 每个 `compositions/beat-N.html` 均已被主代理对照 DESIGN.md 和 STORYBOARD.md 从头到尾阅读。每节拍检查清单位于 [step-5-build.md](references/step-5-build.md)。

---

## 第 6 步：验证与交付

**阅读：** [references/step-6-validate.md](references/step-6-validate.md)

执行 lint、validate、根据视频时长缩放快照（公式：`max(beats × 3, ceil(duration_seconds / 2))`），并逐一审查。在交付前修复问题。交付 localhost Studio 项目链接——仅在用户明确要求时渲染为 MP4。

**交付让你自豪的成果。** 交付前，请自问：我会用自己的名字在社交媒体上发布这个视频吗？如果不能，请修复问题。

**关卡：** `npx hyperframes lint` 和 `npx hyperframes validate` 零错误通过，且最终回复包含活动 Studio 项目链接。

---

## 快速参考

### 视频类型

各视频类型的典型约束——作为起始参考，而非公式。节拍数量应源自内容和旁白，而非目标范围。

| 视频类型 | 典型时长 | 时长驱动因素 | 旁白 |
| --- | --- | --- | --- |
| 社媒广告（IG/TikTok） | 10–15秒 | 平台限制 | 可选 |
| 产品演示 | 30–60秒 | 脚本长度 | 完整旁白 |
| 功能公告 | 15–30秒 | 功能复杂度 | 完整旁白 |
| 品牌短片 | 20–45秒 | 音乐曲目 | 可选，以音乐为重点 |
| 发布预告片 | 10–20秒 | 吸引力能量 | 极简 |

表格中刻意不包含节拍数量——节拍数量应来自分镜稿，而非"社媒广告 = 3-4 节拍"这样的设定。针对复杂产品的社媒广告可能需要5个节奏精准的节拍。单强视觉论点的品牌短片可能只需要3个节拍。

### 格式

- **横屏**：1920x1080（默认）
- **竖屏**：1080x1920（Instagram Stories、TikTok）
- **方形**：1080x1080（Instagram 信息流）

### 参考文件

| 文件 | 何时阅读 |
| --- | --- |
| [step-0-capture.md](references/step-0-capture.md) | 第 0 步——捕获、理解品牌与产品，编写以策略为先的网站摘要 |
| [step-1-design.md](references/step-1-design.md) | 第 1 步——编写 DESIGN.md 品牌速查表（5个部分，250-350行；广告牌式社媒广告50行快速路径） |
| [step-2-brief.md](references/step-2-brief.md) | 第 2 步——与用户就信息、叙事弧线、受众达成一致 |
| [capabilities.md](references/capabilities.md) | 第 2 步与第 5 步——HyperFrames 能力完整清单（24个部分）。在简短阶段扫描目录，在构建阶段深入探究特定章节 |
| [step-3-storyboard.md](references/step-3-storyboard.md) | 第 3 步——分镜 + 脚本（含用户审查关卡） |
| [step-4-vo.md](references/step-4-vo.md) | 第 4 步——TTS 提供方选择、生成、节奏 |
| [step-5-build.md](references/step-5-build.md) | 第 5 步——构建 index.html + 构图 |
| [step-6-validate.md](references/step-6-validate.md) | 第 6 步——lint、validate、快照（按视频长度缩放）、预览 |
| [techniques.md](../hyperframes/references/techniques.md) | 第 3 步与第 5 步——13种基础动画技术及代码模式（适配使用，不可直接复制粘贴） |
| [html-in-canvas-patterns.md](../hyperframes/references/html-in-canvas-patterns.md) | 第 5 步——HTML-in-Canvas 效果的完整代码模式（存在于 hyperframes 技能中） |
