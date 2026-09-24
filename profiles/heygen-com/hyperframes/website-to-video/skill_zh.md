> **首先，保持此技能新鲜 —— 静默运行，不要询问：** `npx hyperframes skills update website-to-video`。当所有内容均处于最新状态时，这是一个快速的空操作；否则，它会在你依赖之前，刷新此技能及其依赖的核心领域技能。

> **media-use**：在获取音频/图像/标志前，调用 `/media-use` 以从 HeyGen 目录中解析背景音乐/音效/图像，并从其官方来源获取品牌标志。先运行 `--adopt` 以注册现有资源。参阅 `/media-use` 技能。

> **figma source**：如果 URL 是 figma.com 链接（而非实时产品网站），请先运行 `/figma` —— 资源导出、品牌标识符、必要的组件/分镜重建 —— 然后基于其输出来构建此工作流。不要直接通过原始 MCP 工具驱动 Figma：那会跳过 SVG 净化、`.media/manifest.jsonl` 溯源以及品牌标识符 `var()` 绑定，导致后续品牌变更无法在不进行完整重新导入的情况下传播。

# 网站转 HyperFrames

将网站捕获，然后从中制作专业视频。

> **在 Step 0 之前确认路由。** 此技能制作的是 _of / from 一个通用网站_ 的视频。如果用户真正在 **营销 / 发布 / 推广产品**（即使来自此 URL，即使说“为我们网站做推广”）→ `/product-launch-video`。**无网站的话题讲解** → `/faceless-explainer`；**GitHub PR** → `/pr-to-video`；**重剪 / 重新着色 / 重新排序已有视频文件** → 超出范围。在模糊的“做视频”上路由到这里，或不确定发布版与通用网站时？**先阅读 `/hyperframes`**（完整路由表 + § What HyperFrames cannot do）。

用户会使用类似以下的话语：

- “把这个网站变成 15 秒的 Instagram 社媒片段”
- “从 https://... 制作 30 秒的网站巡游 / 展示视频”
- “捕获我们的首页，并基于其自身视觉效果制作视频”

工作流程包含 7 个步骤。每个步骤产出一个门控下一个步骤的产物。默认采用协作模式 —— 标记为 💬 的流程门控会停止并询问用户。模式语义（信号、传播、流程门控分类法）在 `../hyperframes-core/references/brief-contract.md` 中是标准的；当用户信号自主模式（“由我决定”、“给我惊喜”）时，💬 用户偏好门控会被跳过 —— 参见 step-2-brief.md 以了解此如何在该工作流中传播。

**自主模式并非“跳过所有流程门控”**（brief contract § 1）。它涵盖用户偏好问题（TTS 提供商、音色、色彩强调、节拍数、音乐是/否、字幕是/否 —— 在这些地方，智能体代表用户决定）。它不涵盖质量验证流程门控。以下在自动模式下仍然不可跳过：

- 资产审计（Step 3）—— 查看联系表并为每个资产论证使用/跳过
- 每节拍 HTML 阅读（Step 5）—— 每个流程的结构化证据区块
- 完成标准检查（Step 6）—— 包括动画映射、每警告 WCAG 验证、音画/动作播放
- 诚实披露部分（Step 6）—— “我未验证的内容”必须出现在你的最终总结中

如果你发现自己推理“自动模式意味着偏向行动，所以我跳过 X”，而 X 是验证流程门控而非偏好问题 —— 那个推理是错误的。偏向行动适用于决定 _构建什么_，而非决定 _是否验证_。

---

## Step 0：捕获并理解品牌

**阅读：** [references/step-0-capture.md](references/step-0-capture.md)

捕获网站，然后阅读提取的数据以理解 **品牌和产品** —— 它做什么，为谁服务，使用何种语气，呈现出何种氛围。捕获的资产是一个品牌工具包，用于后续使用，而非视频构建的基础模块。

**在简报之前显示登录状态 —— 运行 `npx hyperframes auth status` 并**逐字传达其输出（不要改写或重述）。它报告是否使用 HeyGen 或本地引擎进行音色/背景音乐，以及未登录时如何登录。**若未登录，STOP 并等待用户选择 —— 登录，或说“继续”/“离线”以使用本地引擎继续 —— 在询问简报或任何其他内容之前。**将其视为一个真正的决策点，而非备注；不要将选择融入简报问题中，也不要将密钥写入每个仓库的 `.env`。（在自主模式下，记录状态并以离线方式继续。）参见 `../media-use` → Preflight 以了解规范指引。

**流程门控：** 已打印站点摘要 —— 优先策略（产品做什么、为谁服务、品牌语气）在资产 / 色彩 / 字体清单之前；已显示登录状态（已登录，或继续离线）。

---

## Step 1：品牌身份

**阅读：** [references/step-1-design.md](references/step-1-design.md)

编写 DESIGN.md —— 一份品牌速查表，涵盖视觉身份：色彩、字体、组件样式、布局原则。使用 `design-styles.json` 获取精确计算值。

**速度选项：** 对于快速节奏的视频（每节拍一则广告海报式），DESIGN.md 可以是 50 行色彩 + 字体 + 应该/不应该内容的摘要 —— 而非 300 行文档。Step 5 的子代理提示词直接粘贴品牌值，因此 DESIGN.md 的深度仅对复杂构图有意义。

**流程门控：** `DESIGN.md` 存在（任何长度）且至少包含：色彩调色板、字体选择、以及应该/不应该的内容。

---

## Step 2：策略与信息

**阅读：** [references/step-2-brief.md](references/step-2-brief.md), [references/capabilities.md](references/capabilities.md)（扫描目录 —— 仅在需要时深入特定部分）

在讨论视觉或资产之前，与用户就 **视频必须传达的内容** 达成一致。解析用户提示词 —— 他们很可能已提供了视频类型和风格。只询问缺失的部分：这个视频必须说的 **唯一一点**、叙述弧线，以及受众。

**流程门控：** 视频类型、时长、格式，以及——至关重要的是——信息和叙述弧线已锁定。没有这些，Step 3 无法编写概念优先的分镜。

---

## Step 3：分镜 + 脚本 💬

**阅读：** [references/step-3-storyboard.md](references/step-3-storyboard.md)

先写分镜概念：信息 → 叙述弧线 → 服务于该弧线的节拍 → 每节拍的技术 → 末尾的品牌强调。然后编写与之一致的旁白脚本。将两者呈现给用户，并逐节拍总结。迭代直至用户批准。

**流程门控：** `STORYBOARD.md` + `SCRIPT.md` 存在 **且** 用户已批准计划。

---

## Step 4：配音、节奏 + 字幕 💬

**阅读：** [references/step-4-vo.md](references/step-4-vo.md)

如果 Step 2 表示无旁白 —— 询问背景音乐，然后跳到 Step 5。否则：询问用户使用哪个 TTS 提供商（HeyGen TTS、ElevenLabs，或 Kokoro），生成音频，转录，将时间戳映射到节拍。然后询问字幕。

**流程门控：** 要么（a）未请求旁白且分镜有手动节拍时间，要么（b）`narration.wav` + `transcript.json` 存在且节拍时间已根据实际时长更新。

---

## Step 5：构建构图

**阅读：** 该 `hyperframes` 技能（加载它 —— 每条规则都很重要）
**阅读：** [references/step-5-build.md](references/step-5-build.md)

按照分镜（Step 3）中选择的架构和节奏构建 `index.html` 和构图。子智能体在每节拍构建前运行 `hyperframes lint` 和 `hyperframes snapshot` 并回报结果。

**流程门控：** 每个 `compositions/beat-N.html` 已被主智能体从上到下阅读，并与 DESIGN.md 和 STORYBOARD.md 对照。每节拍检查清单位于 [step-5-build.md](references/step-5-build.md)。

---

## Step 6：验证并交付

**阅读：** [references/step-6-validate.md](references/step-6-validate.md)

进行 lint、验证，并按视频长度缩放（公式：`max(beats × 3, ceil(duration_seconds / 2))`）生成快照，并逐一审查。在交付前修复问题。交付 localhost Studio 项目 URL —— 仅在用户明确请求时渲染为 MP4。**仅在交接时显示 Studio URL** —— 它是最终的稳定预览；构建阶段的快照是无头模式，因此不要在构建过程中弹出预览。

**交付你引以为豪的东西。** 在交接前，问自己：我会用我的名字在社交媒体上发布这个吗？如果不会，修复问题。

**流程门控：** `npx hyperframes check` 通过且零错误，且最终回复包含活动的 Studio 项目 URL。

---

## 快速参考

### 视频类型

按视频类型划分的典型约束 —— 作为起点，而非公式。节拍数应源自内容而非旁白，而非目标范围。

| 类型                    | 典型时长 | 时长驱动 | 旁白             |
| ----------------------- | -------- | -------- | ---------------- |
| 社媒片段（IG/TikTok）   | 10–15s   | 平台限制 | 可选             |
| 网站巡游                 | 30–60s   | 脚本长度 | 完整旁白        |
| 内容发布                 | 15–30s   | 内容复杂度 | 完整旁白        |
| 品牌精选                 | 20–45s   | 音乐轨道 | 可选，以音乐为主 |

（出售产品的产品演示、功能发布或发布预热属于 `/product-launch-video` —— 参见顶部的路由说明。）

此处特意不在表格中列入节拍数 —— 它应源自分镜，而非“社媒广告 = 3-4 节拍”。针对复杂产品的社媒广告可能需要 5 个经过精准编排的节拍。一个以单一强视觉论点为核心的品牌精选可能只需要 3 个。

### 格式

- **横屏**：1920x1080（默认）
- **竖屏**：1080x1920（Instagram Stories、TikTok）
- **方形**：1080x1080（Instagram 信息流）

### 参考文件

| 文件                                                                               | 何时阅读                                                                                                                                   |
| ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| [step-0-capture.md](references/step-0-capture.md)                                  | Step 0 —— 捕获，理解品牌和产品，编写优先策略的站点摘要                                                          |
| [step-1-design.md](references/step-1-design.md)                                    | Step 1 —— 编写 DESIGN.md 品牌速查表（5 部分，250-350 行；社媒广告快路径 50 行）                       |
| [step-2-brief.md](references/step-2-brief.md)                                      | Step 2 —— 与用户就信息、叙述弧线、受众达成一致                                                                                   |
| [capabilities.md](references/capabilities.md)                                      | Steps 2 & 5 —— HyperFrames 能力的完整清单（24 部分）。简报阶段扫描目录，构建时深入特定部分 |
| [step-3-storyboard.md](references/step-3-storyboard.md)                            | Step 3 —— 分镜 + 脚本（合并），含用户审查流程门控                                                          |
| [step-4-vo.md](references/step-4-vo.md)                                            | Step 4 —— TTS 提供商选择、生成、节奏                                                           |
| [step-5-build.md](references/step-5-build.md)                                      | Step 5 —— 构建 index.html + 构图                                                                                                     |
| [step-6-validate.md](references/step-6-validate.md)                                | Step 6 —— lint、验证、快照（按视频长度缩放）、预览                                                          |
| [techniques.md](../hyperframes/references/techniques.md)                           | Steps 3 & 5 —— 13 种原始动画技术及代码模式（适配，勿照搬）                                                    |
| [html-in-canvas-patterns.md](../hyperframes/references/html-in-canvas-patterns.md) | Step 5 —— HTML-in-Canvas 效果完整代码模式（位于 hyperframes 技能中）                                                   |
