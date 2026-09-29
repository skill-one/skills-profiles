---
name: general-video
description: '在没有任何专业工作流程适用，或BRIEF.md设置flow: companion时，可创建或编辑自定义HyperFrames组合。适用于较长的多场景作品、品牌和花絮短片、蒙太奇、静态循环、静态标题卡、素材混剪以及自由形式构建。对于包含动画标题的短篇无旁白动态优先单元，则应使用动态图形。在使用此技能前，请将新创作内容通过HyperFrames进行路由处理。'
---

**插件安装：** 在设置或新鲜命令之前，当此技能位于 HyperFrames 插件内时，请遵循 [插件执行规则](../hyperframes/references/plugin-installation.md)。独立安装保留下方的更新说明。

# 一般视频

在依赖此工作流之前，运行：

```bash
npx hyperframes skills update general-video
```

成功的 no-op 表示技能是当前的。显示更新失败，而不是从记忆中继续。

## 1. 应用跨领域源适配器

- **媒体：** 对于任何音频、图像、图标、标志、语音、等级、LUT、处理/效果、字幕或媒体操作需求，加载 `/media-use` 并遵循 `../media-use/references/resolve.md`（解析、采用、重用）和 `../media-use/references/setup-providers.md`（提供者、认证）。模糊的镜头反馈和命名样式在编辑前使用 `../media-use/references/media-treatments.md`；不要用 CSS/SVG/不透明度即兴创作支持的视频效果。在第一个经过认证的提供者操作之前，运行 `npx hyperframes auth status` 并原封不动地传递其输出。如果已登出，应用 `../hyperframes/references/brief-contract.md` 中的门禁：协作等待登录或显式的离线选择；自主状态并继续通过可用的离线提供者。当没有离线提供者能满足所需功能时，显示阻止器。仅本地采用不需要认证门禁。
- **Figma：** 如果任何输入是 `figma.com` URL，请先运行 `/figma`。从其导出的资源、标记、组件或故事板帧构建。不要使用原始 Figma 连接器调用，因为它们会跳过 SVG 清理、媒体来源和品牌标记绑定。

这些适配器不会更改 `/hyperframes` 选择的工作流。

## 2. 从项目状态开始

应用第一个匹配的行；不要评估较低状态行：

| 状态                                                      | 操作                                                                                                         |
| ---------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| 具体编辑                                                  | 进行编辑，保留现有的项目决策，然后重新运行受影响的检查。不要重新打开发现。                                       |
| `BRIEF.md` 存在                                            | 读取它。如果 `workflow` 指向另一个工作流且 `flow` 不是 `companion`，则移交。不要询问简要问题。                     |
| 无简要，但 `hyperframes.json` 或 `STORYBOARD.md` 存在      | 从文件和记录的偏好中恢复。仅从已知事实填充 `BRIEF.md`。                                                         |
| 新鲜创建                                                  | 运行 `/hyperframes` 及其意图层。仅当 `workflow: general-video` 或 `flow: companion` 时才返回这里。                |

对于新项目，从简要中选择一个 kebab-case 目录名并在编写简要之前创建脚手架：

```bash
npx hyperframes init "videos/<项目>" --non-interactive --example=blank --skill=general-video
```

然后在项目根目录下使用 `../hyperframes/references/brief-format.md` 编写 `BRIEF.md`。在现有项目中，根是包含 `hyperframes.json` 的目录。仅记录简要格式命名的经确认偏好支持的字段，使用 `node <MEDIA_DIR>/scripts/prefs.mjs record --hyperframes <PROJECT_ROOT>`；永远不要记录推断的默认值。这里 `<MEDIA_DIR>` 是安装的 `/media-use` 技能目录，`<PROJECT_ROOT>` 是包含 `hyperframes.json` 的目录。如果意图层采用了配方，现在使用 `node <MEDIA_DIR>/scripts/recipe.mjs use --hyperframes <PROJECT_ROOT> --name <name>` 应用它，并且不要再询问。

## 3. 解释运行形状

仅使用 `../hyperframes/references/brief-contract.md` 中的规范术语：

| 字段          | 含义                               | 效果                                                                              |
| -------------- | ------------------------------------- | ----------------------------------------------------------------------------------- |
| `flow`         | 谁驱动                            | `automation`：选择并执行路线。`companion`：在对话中共同创建。                         |
| `storyboard`   | 在构建前计划、绘制和审查           | `yes`：运行计划和绘制审查 (`storyboard.html`)。`no`：无计划构建。                   |
| derived `mode` | 检查点门禁如何行为               | 遵循简要合同。永远不要要求用户命名模式。                                             |

不要为这些状态发明同义词。持续的“直接构建”信号由意图层处理，并作为 `flow: automation`、`storyboard: no` 到达。

- 对于 `flow: automation`，选择路线并在第一条进度更新中用一行状态声明它。
- 对于具体编辑，进行编辑而不发明新路线。

对于现有镜头的硬切、修剪、拼接或重新排序，将相同的视频源复制到多个剪辑元素中。在每个副本上，使用 `data-media-start` 加 `data-duration` 设置源范围，然后使用 `data-start` 设置授权的放置/顺序。独立的音频遵循相同的剪辑范围和匹配的 `<audio>` 元素上的时间。`/hyperframes-core` 拥有此时间编辑；仅使用 `/hyperframes-keyframes` 进行视觉属性动画，如缩放、冲击、平移、裁剪、遮罩或内包装上的 `clip-path`。
复制完整的合同来自 `../hyperframes-core/references/creator-editing-recipes.md`。

### 伙伴流程

当 `flow: companion` 时：

- 读取 `BRIEF.md` 并与项目工件协调接受的 `## 资产` 和 `## 自定义`。完成待处理的接受工作；保留已完成的工作；不要再次提供已接受的 capability，好像它是新的。
- **作为导演而不是承包商到达。** 选择伙伴的用户选择了参与和质量；诚实的回应是你能设计的最佳版本，而不是你能辩护的最小版本。第一个计划是天花板处理：故事弧（借用最近的类型镜头——菜单 § 类型镜头）、设计规范、每个场景的运动处理（§ 5 的计划纪律）、过渡、音频身份——音乐和声音标记，或故意的沉默——用户提供的材料放置，以及设计的开头和结尾。用一句话说明每一层添加的内容；当你命名它们时，将昂贵的层（渲染时间、登录、计费）标记为阻止器。用户会缩减处理；他们永远不需要逐个批准地组装一个批准。
- **天花板属于概念，而不是工具箱。** 每一层都必须服务于简要的信息——任何视频都会以相同方式穿着的处理是装饰。工艺上升到天花板；内容永远不会超过所要求的内容（§ 6）。
- 在检查点之间，`../hyperframes/references/capability-menu.md` 有两种工作方式。作为触发列表：当用户提到其输入或构建达到其需求时提供相关 capability。作为每次迭代的升级通道：一个计划、绘制或构建检查点可能包含一个或两个指向用户正在查看的材料（“场景 3 的 stat 需要计数上升处理”）的跟踪提议。在提供之前读取它；永远不要倾倒完整目录。
- 用户接受 capability 后，立即在其匹配的 `BRIEF.md` 正文部分生成其工件并记录决策。仅当用户明确更改它时，才重写前文字段并记录经确认的偏好。
- 保持相同的故事板、验证、最终预览和渲染批准门禁。伙伴改变的是谁驾驶，而不是质量要求什么。

## 4. 在每个阶段之前加载所需知识

当其条件匹配时，这些读取是强制性的：

| 条件                                                                                                         | 在行动前读取                                                                                                                                                                                                                     |
| ----------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 任何组合 HTML 或场景布局                                                                              | `/hyperframes-core`；使用 `references/determinism-rules.md` 用于其布局合同                                                                                                                                                     |
| 任何非平凡的创建或视觉处理                                                                      | `/hyperframes-creative` → `references/house-style.md` 和 `references/video-composition.md`                                                                                                                                            |
| 任何运动、动画或场景过渡                                                                        | `/hyperframes-animation`；遵循其路由到匹配的规则、适配器、蓝图或过渡参考                                                                                                                                                     |
| `storyboard: yes`                                                                                                 | `../hyperframes/references/storyboard-format.md` 和 `../hyperframes/references/review-loop.md`                                                                                                                                        |
| 任何媒体资产或操作，包括旁白、BGM、SFX、字幕、调色或转换                     | `/media-use`；对于框架播放和放置还读取 `/hyperframes-core` → `references/variables-and-media.md`                                                                                                                 |
| 多场景组装                                                                                              | `../hyperframes/references/production-loop.md`                                                                                                                                                                                         |
| `flow: companion`，在第一个计划之前                                                              | `/hyperframes-creative` → `references/story-spine.md` 和 `references/house-style.md`；最近的类型镜头和完整的 `../hyperframes/references/capability-menu.md` — 天花板处理是从这些设计的，而不是回忆的 |
| 一个伙伴 capability 提供方案、捕获、节拍网格、生成视频、地图、发布或跨工作流 capability | `../hyperframes/references/capability-menu.md`                                                                                                                                                                                         |
| 一个设计规范存在，在最终批准之前                                                                       | `/hyperframes-creative` → `references/design-adherence.md`                                                                                                                                                                             |

不要用回忆替换这些读取。渐进式披露仅在匹配的参考实际加载时才保存上下文。

## 5. 执行组合

使用此依赖顺序。仅在其输入不存在时才跳过阶段。

1. **计划。** 声明观众弧、结构、节奏和持续时间驱动器。对于短单一场景使用一个文件；对于三个或更多硬场景切或任何重用的场景使用子组合。读取 `/hyperframes-creative` → `references/story-spine.md` 用于旁白弧，`references/beat-direction.md` 用于节奏，和 `/hyperframes-core` → `references/composition-patterns.md` 用于结构。对于开放式多场景简要，通过 `/hyperframes-creative` → `references/prompt-expansion.md` 扩展提示。多场景计划引用每个场景的形状：当有一个匹配时，引用 `/hyperframes-animation` → `blueprints-index.md` 中的蓝图 id，否则引用 `rules-index.md` 中它组合的命名规则——运动名称来自这些索引，永远不要发明。故事真相决定哪些场景存在；引用为它们增添。**在构建任何命名外观之前搜索实时目录**：对于简要命名的每个外观、效果、处理或过渡——"CRT 扫描线"、"故障"、"胶片颗粒"、"闪烁扫描"、"五彩纸屑爆发"——运行 `npx hyperframes catalog --query "<外观，用普通英语>" --json` 并在计划命名如何构建该外观之前阅读顶部结果。搜索需要**不需要安装任何东西**：没有项目，没有先前的 `add`，没有账户。它从任何目录对整个托管注册表（~400 个块和组件）进行排名，因此也适用于用户在构建中途要求的外观。计划名称的块在阶段 3 安装；仅当搜索该外观返回了不匹配的结果后，才手写外观。多场景计划也记录为调度工件：每个场景一个 `## 帧 N` 块在 `STORYBOARD.md` 中——`status: 概要`，声明的 `src:`，蓝图/规则引用，和节拍文本——**即使 `storyboard: no`**。块是调度单元；故事板表只是审查表面。
2. **在请求时审查计划。** 对于 `storyboard: yes`，运行共享审查循环。对于 `storyboard: no`，继续而不计划暂停或绘制表。当计划暂停无论如何发生时，将子代理委托授权（由 codex 在步骤 4 的调度需要）合并到该暂停中，而不是稍后再次停止。
3. **解析依赖项。** 在并行工作之前安装注册表块。阶段用户资产，采用现有媒体，并仅解析简要要求的内容。当音频时间驱动持续时间时，尽早开始音频。
4. **构建场景。** 对于短单一场景作品，在其最可见时刻实现场景（当存在时，确认的线框是那个最终状态，并且必须不被重绘），然后从其引用的蓝图或规则进行动画——在编写运动之前读取完整的配方正文 (`/hyperframes-animation` → `blueprints/<id>.md`，`rules/<id>.md`)。

   **调度仅在规模上自我支付。** 编写数据包和预热新鲜工作上下文会消耗真实的分钟和标记：最多 6 个短场景的电影在线此上下文中比包化更快，一个接一个地构建（测量：5 个短场景 ≈ 9 分钟在线 vs ≈ 21 分钟包化）。仅当计划超过该值时才发散——更多场景，或单独的重场景——并给每个工人 **2–3 个场景**，而不是一个，并在单个波次中生成**所有工人**（第二个波次几乎将窗口翻倍）。当调度时：

   `node <SKILL_DIR>/scripts/frame-packets.mjs --project "$PROJECT_DIR" --storyboard "$PROJECT_DIR/STORYBOARD.md"`

构建器在每个场景下向 `.hyperframes/frame-packets/` 目录写入一个有界数据包（包含场景的精确故事板区块、蓝图主体以及所有引用的规则配方，内联），以及 `_role.md`（`../hyperframes/references/frame-worker-core.md` + 此技能的 `sub-agents/frame-worker.md`，逐字连接——完整的工人角色）。派遣工人——每个工人分配 2-3 个场景数据包，全部一次性派遣（`../hyperframes/references/subagent-dispatch.md`）；每个工人的提示包含 `_role.md` 及其数据包——可以完整粘贴，或让工人先读取文件路径（两种方式等效）——以及包含 `PROJECT_DIR`、其 `frame_id` 和画布尺寸的派遣上下文。等待每个场景的 `compositions/<frame_id>.html` + `compositions/<frame_id>.motion.json`。工人仅读取其数据包和设计真理文件；他们从不打开 `STORYBOARD.md` 或技能文档。在没有委派通道的情况下，串行回退：在此上下文中逐个处理数据包，仍然仅从数据包本身工作。

5. **合并运动副产物**。收集工人的 `compositions/<frame_id>.motion.json` 文件，并将它们的持续时间和进出向量带入装配；在安装了教义链（`/motion-doctrine`）的地方，在打上接缝之前将它们翻译成项目账本。
6. **组装**。使用生产循环挂载场景、媒体、过渡、字幕和音频。真实语音时长覆盖估计值。当任何语音轨道下方播放音乐床时，在验证前切割床：`/hyperframes-audio` → `scripts/carve.mjs --comp index.html`。仅有的音量压低并不能完成混音。
7. **验证**。在第一次 HTML 遍历和结构变更后，使用 `npx hyperframes lint` 获取快速反馈。对于最终关卡，运行 `npx hyperframes check`；它会内部重新运行 lint，因此不要在它之前立即运行冗余的独立 lint。对于子组合，检查中点快照。对于多场景工作，审查动画图。
8. **最终批准**。检查通过后，仅打开最终 Studio 预览。询问是否渲染或修改。仅经批准后渲染。

## 6. 始终适用的关卡

### 保持范围精确

构建用户要求的内容。标题卡不是标题卡加三个场景、音乐和字幕。在添加之前提供补充。

### 在 HTML 之前建立设计

按以下顺序解决设计源：`frame.md` → `design.md` → `DESIGN.md`。将找到的第一个文件视为品牌真理。

当不存在设计规范时，在编写组合 HTML 之前完成所有四项：

1. 在 `house-style.md` 和 `video-composition.md` 中为视觉身份奠定基础。
2. 为每个非平凡的创建编写一句命名概念角度。
3. 从 `/hyperframes-creative` → `references/typography.md` 选择一个可嵌入的字体搭配；不要假设云渲染中存在未打包的显示字体。
4. 定义焦点元素、边缘锚点、支撑细节和背景处理。

根据请求的格式和消息匹配密度。密度示例是为生成的帧提供指导，不是创造声明、场景或固定数量元素的许可。

对于命名风格或情绪，阅读 `/hyperframes-creative` → `references/visual-styles.md`。当用户需要视觉选择且没有合适的已发布预设时，阅读 `/hyperframes-creative` → `references/design-picker.md` 并在那里运行交互式设计选择。

### 保留组合契约

定时元素使用 `class="clip"`；根和相关的祖先被调整大小；每个组合在 `window.__timelines` 上注册一个暂停的、安全可搜索的时间线；渲染是确定性的。不要使用渲染时网络获取、时钟或未播种的随机性。

### 安全借用工作流

当作品类似于已发布的工作流时，将其类型参考作为示例借用。首先运行 `npx hyperframes skills update <workflow-name>`。借用其故事形状和品味，而不是其私有脚本、管道状态或目录契约。通用构建仍由此技能拥有。

## 7. 完成

运行仅在以下情况下完成：

- 请求的范围已实现；
- 对于 `flow: companion`，交付的是处理而非范围：每个场景引用的蓝图或规则已实现，音频身份存在（或选择了沉默并说明），开闭设计而非默认；
- `npx hyperframes check` 通过，包括其内置的 lint 阶段；
- 当存在设计规范时，根据 `/hyperframes-creative` → `references/design-adherence.md` 审查设计遵循性；
- 对比发现已解决；
- 在适用情况下检查子组合快照；
- 自主交接包括检查的联系人或快照表；多场景表使用场景中点；
- 交接命名最终预览或渲染工件（如适用），并报告基于时间的交付的实际时长；
- 对于多场景工作，审查 `hyperframes-animation/scripts/animation-map.mjs`；
- 用户在渲染前批准最终 Studio 预览；
- 当请求渲染时，验证渲染文件。

最终批准后，根据 `../hyperframes/references/review-loop.md` § 4. 一次性提供冻结运行作为配方。
