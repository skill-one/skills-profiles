# 通用视频

在依赖此工作流之前，请运行：

```bash
npx hyperframes skills update general-video
```

一次成功的无操作（no-op）即表示该技能已是最新版本。遇到更新失败时，应提示失败而非凭记忆继续。

## 1. 应用横切式源适配器

- **媒体：** 对于任何音频、图像、图标、Logo、语音、调色、LUT、处理/特效、字幕或媒体操作需求，加载 `/media-use`，并遵循 `../media-use/references/resolve.md`（解析、采用、复用）和 `../media-use/references/setup-providers.md`（服务商、认证）。编辑前，对模糊的素材反馈和具名风格，先使用 `../media-use/references/media-treatments.md`；不要凭 CSS/SVG/不透明度即兴发挥支持的媒体特效。在首次执行已认证服务商操作前，运行 `npx hyperframes auth status` 并原样传达其输出。若已登出，则应用 `../hyperframes/references/brief-contract.md` 中的门槛：协作状态等待登录或明确选择离线；自主状态说明状态后通过可用离线服务商继续。当没有离线服务商能满足所需能力时，提示阻碍。仅本地采用本身无需认证门槛。
- **Figma：** 若任何输入是 `figma.com` 链接，先运行 `/figma`。基于其导出的素材、令牌、组件或分镜帧进行构建。不要使用原始 Figma 连接器调用，因为它们会跳过 SVG 消毒、媒体溯源和品牌令牌绑定。

这些适配器不会改变 `/hyperframes` 选择的流程。

## 2. 从项目状态开始

应用首个匹配的行；不要评估更低层级的状态行：

| 状态                                                      | 操作                                                                                                         |
| ---------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| 特定编辑                                                  | 执行编辑，保留现有项目决策，然后重跑受影响检查。不要重新开启探索。                                           |
| `BRIEF.md` 存在                                          | 阅读它。若 `workflow` 指名了其他流程且 `flow` 不是 `companion`，则移交。不询问任何 brief 问题。               |
| 无 brief，但存在 `hyperframes.json` 或 `STORYBOARD.md`    | 从文件及记录的偏好中恢复。仅从已知事实回填 `BRIEF.md`。                                                 |
| 全新创建                                                  | 运行 `/hyperframes` 及其意图层。仅在此返回，当 `workflow: general-video` 或 `flow: companion` 时。            |

对于新项目，从 brief 中选择 kebab-case 目录名，并在编写 brief 前进行脚手架搭建：

```bash
npx hyperframes init "videos/<project>" --non-interactive --example=blank --skill=general-video
```

然后使用 `../hyperframes/references/brief-format.md` 在项目根目录编写 `BRIEF.md`。在现有项目中，根目录是包含 `hyperframes.json` 的目录。仅记录 brief 格式指明的、由确认偏好支撑的字段，使用 `node <MEDIA_DIR>/scripts/prefs.mjs record --hyperframes <PROJECT_ROOT>`；绝不记录推断出的默认值。此处 `<MEDIA_DIR>` 是已安装的 `/media-use` 技能目录，`<PROJECT_ROOT>` 是包含 `hyperframes.json` 的目录。若意图层采用了食谱，现在应用该食谱，使用 `node <MEDIA_DIR>/scripts/recipe.mjs use --hyperframes <PROJECT_ROOT> --name <name>`，且不再询问。

## 3. 解读运行形态

仅使用 `../hyperframes/references/brief-contract.md` 中的规范术语：

| 字段          | 含义                               | 效果                                                                              |
| -------------- | ------------------------------------- | ----------------------------------------------------------------------------------- |
| `flow`         | 驱动方                              | `automation`：选择并执行路线。`companion`：对话协作共创。                           |
| `storyboard`   | 构建前计划、草图与评审               | `yes`：运行计划与草图评审（`storyboard.html`）。`no`：不经过即构建。                |
| 派生 `mode`   | 检查点门槛如何行为                 | 遵循 brief 契约。绝不要求用户命名 mode。                                           |

不得为这些状态杜撰同义表述。持续的“直接构建”信号由意图层处理，并以 `flow: automation`、`storyboard: no` 的形式到达。

- 对于 `flow: automation`，选择路线并在首个进度更新中用一行说明。
- 对于特定编辑，直接执行编辑，不杜撰新路线。

对已有素材进行硬切、裁剪、拼接或重排序时，将相同视频源复制为多个片段元素。在每一份副本上，使用 `data-media-start` 加 `data-duration` 设置源范围，再用 `data-start` 设置已撰写的放置/顺序。独立撰写的音频遵循与匹配 `<audio>` 元素相同的片段范围与时间。`/hyperframes-core` 负责此时间编辑；仅使用 `/hyperframes-keyframes` 用于缩放、 punch、pan、裁剪、遮罩或内部包装器的 `clip-path` 等视觉属性动画。从 `../hyperframes-core/references/creator-editing-recipes.md` 复制完整契约。

### 协作流程

当 `flow: companion` 时：

- 阅读 `BRIEF.md`，将接受的 `## Assets` 与 `## Customizations` 与项目产物对齐。完成仍待完成的可接受工作；保持已完成工作不变；不要将可接受的能力当作新能力再次提供。
- **以导演身份到达，而非承包商身份。** 用户选择协作，即选择了参与与质量；诚实的回应是你能设计出的最佳版本，而非你能辩护的最小版本。首个计划即为天花板方案：故事弧（借用最近类型的镜头——菜单 § Genre lenses）、设计规范、每个场景的运动处理（以具名方式引用，§ 5 的计划纪律）、转场、音频身份（音乐与声音标记，或刻意静默）、用户素材的放置，以及设计的开场与结尾。用一句话说明每层贡献了什么；在命名时即标记昂贵项（渲染时间、登录、计费）。用户精简处理，绝不应被迫逐一审批一个方案。
- **天花板属于概念，而非工具箱。** 每一层都必须服务 brief 的信息——会以相同方式修饰任何视频的处理即属装饰。工艺达到天花板高度；内容绝不超出所要求范围（§ 6）。
- 检查点之间，`../hyperframes/references/capability-menu.md` 双向生效。作为触发列表：当用户提及输入或构建到达需求时，提供相关能力。作为每个环节的升级通道：计划、草图或构建检查点可携带一至两条指向用户正在查看材料的追踪性提议（“第 3 场景的统计数据需要倒计处理”）。提供前阅读；绝不一次性倾倒完整目录。
- 用户接受能力后，生成其产物，并在匹配的 `BRIEF.md` 正文中立即记录该决策。仅在用户明确变更时，重写 frontmatter 字段并记录确认偏好。
- 保持相同的草图、校验、最终预览与渲染审批门槛。协作改变的是谁来指引，而非质量要求是什么。

## 4. 在每阶段加载所需知识

当其条件满足时，以下阅读为必需：

| 条件                                                                                                         | 行动前阅读                                                                                                                                                                                                                     |
| ----------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 任何构图 HTML 或场景布局                                                                              | `/hyperframes-core`；使用 `references/determinism-rules.md` 处理其布局契约                                                                                                                                                     |
| 任何非平凡创建或视觉处理                                                                      | `/hyperframes-creative` → `references/house-style.md` 和 `references/video-composition.md`                                                                                                                                            |
| 任何运动、动画或场景过渡                                                                        | `/hyperframes-animation`；遵循其路由到匹配规则、适配器、蓝图或过渡引用                                                                                                                     |
| `storyboard: yes`                                                                                                 | `../hyperframes/references/storyboard-format.md` 和 `../hyperframes/references/review-loop.md`                                                                                                                                        |
| 任何媒体资源或操作，包括旁白、背景音乐、音效、字幕、调色或变换                                                   | `/media-use`；为框架播放与放置，也读 `/hyperframes-core` → `references/variables-and-media.md`                                                                                                                 |
| 多场景组装                                                                                              | `../hyperframes/references/production-loop.md`                                                                                                                                                                                         |
| `flow: companion`，首次计划前                                                                          | `/hyperframes-creative` → `references/story-spine.md` 和 `references/house-style.md`；最近类型镜头与完整 `../hyperframes/references/capability-menu.md` —— 天花板方案由此设计，而非回忆                                      |
| 协作能力提议、捕获、节拍网格、生成视频、映射、发布或跨流程能力                                              | `../hyperframes/references/capability-menu.md`                                                                                                                                                                                         |
| 存在设计规范，最终审批前                                                                       | `/hyperframes-creative` → `references/design-adherence.md`                                                                                                                                                                             |

不得用这些阅读取代回忆。渐进式披露仅当匹配的参考文档实际加载时，才节省上下文。

## 5. 执行构图

使用此依赖顺序。仅在输入缺失时跳过某阶段。

1. **计划。** 说明观看弧线、结构、节奏与时长驱动。对短的单一场景，用一个文件；对三个或以上硬场景切或任何复用场景，使用子构图。为叙述性弧线读 `/hyperframes-creative` → `references/story-spine.md`，为节奏读 `references/beat-direction.md`，为结构读 `/hyperframes-core` → `references/composition-patterns.md`。对开放式的多场景 brief，通过 `/hyperframes-creative` → `references/prompt-expansion.md` 扩展提示。多场景计划需引用每个场景的形状：当 `/hyperframes-animation` → `blueprints-index.md` 中有适用蓝图时，取该蓝图 id；否则取它组合自 `rules-index.md` 中具名规则 —— 运动名称来自这些索引，绝不杜撰。故事真实性决定哪些场景存在；引用为它们着装。**在自行构建任何具名造型前，先检索实时目录**：对 brief 指名的每一个造型、特效、处理或转场（"CRT 扫描线"、"glitch"、"film grain"、"shimmer sweep"、"confetti burst"）—— 运行 `npx hyperframes catalog --query "<the look, in plain English>" --json` 并阅读顶部结果，再在计划中说明该造型如何构建。该搜索**无需任何已安装内容**：无需项目、无需先前 `add`、无需账号。它从任意目录对整个托管注册表（约 400 个区块与组件）进行排序，因此也适用于用户在中途请求的造型。计划中命名的造型需在阶段 3 安装；仅在搜索结果中无可适配项时，才手工编写造型。多场景计划还作为派发产物记录：在 `STORYBOARD.md` 中，每个场景一个 `## Frame N` 区块 —— `status: outline`、声明的 `src:`、蓝图/规则引用及节拍文本 —— **即使 `storyboard: no`**。该区块是派发单元；分镜表仅作为评审表面。
2. **按请求评审计划。** 对于 `storyboard: yes`，对那些区块运行共享评审循环。对于 `storyboard: no`，不经过计划停顿或草图表即继续。即便计划停顿发生，也将子代理委派授权（代码x 在步骤 4 派发所需）合并进该停顿，而非稍后再停止。
3. **解析依赖。** 并行工作前安装注册表区块。阶段化用户素材、采用现有媒体，仅解析 brief 所需部分。当其时间驱动时长时，尽早启动音频。
4. **构建场景。** 对短的单一场景作品，先在最可见时刻实现场景，再添加运动（若存在已确认的线框图，该端态即线框图，不得重绘），然后从引用的蓝图或规则动画 —— 编写运动前，先读完整食谱正文（`/hyperframes-animation` → `blueprints/<id>.md`、`rules/<id>.md`）。

   **派发仅在规模下才物有所值。** 编写数据包与预热全新工作器上下文耗费真实的分钟与 token：一段约含 ~6 个短场景的电影，在此上下文中逐场景内联构建**更快**（实测：5 个短场景内联 ≈ 9 分钟，打包 ≈ 21 分钟）。仅当计划超出该范围时，才扇出派发 —— 场景更多，或各场景各自较重 —— 且给每个工作器 **2–3 个场景**，而非 1 个，并**在单波中生成所有工作器**（第二波几乎会使窗口减半）。派发时：

   `node <SKILL_DIR>/scripts/frame-packets.mjs --project "$PROJECT_DIR" --storyboard "$PROJECT_DIR/STORYBOARD.md"`

   构建者每个场景在 `.hyperframes/frame-packets/` 下写入一个有限数据包（场景的精确分镜区块 + 蓝图正文 + 每个引用规则食谱，内联）以及 `_role.md`（`../hyperframes/references/frame-worker-core.md` 与本技能 `sub-agents/frame-worker.md` 逐字拼接 —— 完整的工人物角色）。派发工作器 —— 每个 2–3 个场景数据包，全部单波（`../hyperframes/references/subagent-dispatch.md`）；每个工作器的提示包含 `_role.md` 及其数据包 —— 完整粘贴，或手工提供工作器先行读取的文件路径（二者等价）—— 外加含 `PROJECT_DIR`、其 `frame_id`s 与画布大小的派发上下文。**等待每个场景的 `compositions/<frame_id>.html` + `compositions/<frame_id>.motion.json`**。工作器仅读取其数据包与设计真相文件；从不打开 `STORYBOARD.md` 或技能文档。若无委派通道，回退为串行：在此上下文逐数据包处理，仍仅依据数据包工作。

5. **合并运动旁车。** 收集工作器的 `compositions/<frame_id>.motion.json` 文件，并将其时长与进出向量带入组装；当 `/motion-doctrine` 已安装时，在密封接缝前将其翻译为项目账册。
6. **组装。** 使用生产循环挂载场景、媒体、转场、字幕与音频。真实语音时长覆盖估算。当任何语音轨道下播放背景音乐时，在验证前切分背景：`/hyperframes-audio` → `scripts/carve.mjs --comp index.html`。仅有音量压缩不会完成混音。
7. **验证。** 首轮 HTML 通过与结构变更后，用 `npx hyperframes lint` 获取快速反馈。最终门槛运行 `npx hyperframes check`；其内部会重跑 lint，故不要在之前立即运行重复的独立 lint。对子构图，检查中点快照。对多场景工作，评审动画映射。
8. **最终审批。** 检查通过后，才打开最终 Studio 预览。询问是否渲染或修订。仅经审批后渲染。

## 6. 始终适用的门槛

### 保持范围精确

构建用户要求的内容。标题卡不是标题卡加三个场景、音乐与字幕。添加内容前先提出。

### 在 HTML 前建立设计

按以下顺序确定设计来源：`frame.md` → `design.md` → `DESIGN.md`。将找到的首个文件视为品牌真相。

当不存在设计规范时，在编写构图 HTML 前完成全部四项：

1. 以 `house-style.md` 与 `video-composition.md` 奠定视觉身份。
2. 为每个非平凡创作写一句命名其概念角度的句子。
3. 从 `/hyperframes-creative` → `references/typography.md` 选择可嵌入的字体配对；不假定云端渲染中存在未捆绑的展示字体。
4. 定义焦点元素、边缘锚点、支撑细节与背景处理。

匹配密度与请求的格式及信息。密度示例是对产出帧的指导，而非杜撰声明、场景或固定元素数量的许可。

对具名风格或情绪，读 `/hyperframes-creative` → `references/visual-styles.md`。当用户需视觉选择且无已发布预设符合时，读 `/hyperframes-creative` → `references/design-picker.md` 并在其中运行交互式设计选择。

### 保持构图契约

定时元素使用 `class="clip"`；根节点与相关祖先节点定尺寸；每个构图在 `window.__timelines` 上注册一个暂停、寻址安全的时间线；渲染确定。不使用渲染时网络获取、时钟或未播种的随机性。

### 安全借用流程

当作品类似已发布流程时，借用其类型参考作为示例。首先运行 `npx hyperframes skills update <workflow-name>`。借用其故事形态与品味，而非其私有脚本、流程状态或目录契约。通用构建仍由本技能所有。

## 7. 完成

当仅满足以下条件时，一次运行才完成：

- 所请求范围已实现；
- 对于 `flow: companion`，交付的是处理结果，而不仅是范围：每个场景的引用蓝图或规则均已实现，音频身份已呈现（或已选定静默并说明），开场与结尾已设计而非默认；
- `npx hyperframes check` 通过，含其内置 lint 阶段；
- 存在设计规范时，按 `/hyperframes-creative` → `references/design-adherence.md` 评审设计符合性；
- 对比发现已解决；
- 适用时检查子构图快照；
- 自主移交包含检查过的联系人或快照表；多场景表使用场景中点；
- 移交指明最终预览或渲染产物（如适用），并报告时间型交付物的实际时长；
- 对多场景工作，审查 `hyperframes-animation/scripts/animation-map.mjs`；
- 用户最终 Studio 预览获批后才渲染；
- 请求渲染时，已验证渲染文件。

最终审批后，可按 `../hyperframes/references/review-loop.md` § 4 提议一次将运行冻结为食谱。
