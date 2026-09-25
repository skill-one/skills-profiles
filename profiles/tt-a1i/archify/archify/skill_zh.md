# Archify

从一份小型带类型的 JSON 规范创建自包含、交互式的 HTML 图。静态输出是默认情况；仅在用户要求演示或演示文稿时才启用动画。

## 快速作者路径

使用此受限路径进行普通生成。除非用户询问相关功能，否则不要阅读可选的查看器运行时参考文档。

1. 从问题中选取 `architecture`、`workflow`、`sequence`、`dataflow` 或 `lifecycle`。
2. 在 `schemas/`、`schemas/common.schema.json` 中读取一个匹配的 schema，在 `examples/` 中读取一个匹配的 JSON 示例。仅读取这些文件。新作者的创作意味着使用新的稳定 ID、领域措辞和布局；使用示例来理解字段结构，而非事实内容。新的工作流源使用 `schema_version: 2` 及其可读的布局契约；仅在保留现有工作流固定的几何形状时，才使用 `schema_version: 1`。当真实产品身份至关重要时，查询 `node bin/archify.mjs brands "<name>" --json`；仅当用户提供了未知品牌的官方 URL 时，才阅读 `references/brand-marks.md`。
3. 优先生成产物：下一个工具操作必须写入候选方案。在检查渲染器内部机制之前写入候选方案。不要以文字形式规划精确的坐标。从一条清晰的主路径开始，辅以简短的旁支、稀疏的标签，且主要节点不超过 12 个。除非用户明确请求密集的 `standard` 地图，否则将 `meta.quality_profile` 设置为 `"showcase"`。从自动路由和标签开始。在诊断需要之前，不要添加 `via`、`channelX`、`channelY` 或 `labelAt`；每次修复最多应用一个经诊断的几何控制。
4. 每次修改候选方案后进行验证，并在移交前立即验证：

   ```bash
   node bin/archify.mjs validate <type> <candidate.json> --quality showcase --json
   ```

   仅包含 4 个产物检查的回执仅为基础验证，绝不代表展示通过。展示通过必须报告所有 9 项产物检查，且组合错误和警告均为 0。如果候选方案遗漏或拼写错误 `meta.quality_profile` 字段，必须在几何设置前修正它。对于工作流 v2 几何诊断，运行 `node bin/archify.mjs validate workflow <candidate.json> --layout-json` 并使用稳定的编译器回执；求解器内部机制不是作者控制项。通过的最终验证会冻结候选方案：之后切勿修改它。
5. 对于交付的 HTML，`deliver` 是最终验收命令：

   ```bash
   node bin/archify.mjs deliver <type> <candidate.json> <output.html> --quality showcase --json
   ```

   非零退出码绝不视为成功。失败的交付会保留任何先前输出，因此不要在失败路径上运行 `visual-check`：它检查的是过时的上一次良好产物，而非失败的候选方案。如果验证失败，仅修改经诊断的 `subject`，验证 `evidence`，从 `supportedFixes` 中选择，然后重新运行。在客观错误计数达到新的最小值的过程中，继续聚焦修正。如果连续两轮未使该最佳计数有所改善，则停止并如实报告未解决的诊断情况。

## 更新感知

在第一个候选方案存在后，使用打包的校验器 `scripts/check-update.mjs` 配合 Node 运行一次，然后继续请求的工作流。如果命令无法运行，在不提及该检查的情况下继续。

- 对于 `silent`，继续且无需提及更新检查。
- 对于 `update_available`，在用户的对话语言中显示一条简洁提示，包含已安装版本、最新版本、校验器的固定本地摘要和官方发布说明链接。当 `severity` 为 `security` 时，明确标注为安全更新，并使用克制的警告标记；这仅改变强调，绝不改变用户自主性。明确说明已安装的 Skill 未发生变化，由用户自行决定何时更新。你可以翻译那条固定的本地句子，但绝不引用、总结或翻译远程清单的摘要。提示可见后，通过以 `--ack "<eventKey>"` 运行相同校验器的方式确认其精确的 `eventKey`，然后继续用户 original 任务。

该提示是信息，而非许可。保持已安装版本不变；此 v0.1 工作流从不下载、安装或执行更新，且静默绝非同意。

在第一个候选方案存在之前，不要阅读 `renderers/shared/geometry.mjs`、渲染器源码、校验器源码、测试或基准测试。仅在遇到不支持的内部诊断或两次聚焦修复失败后，才检查实现。

工作流说明：使用 schema v2 创建新工作流；当现有源需要固定的旧版几何形状时，保留 schema v1。保留语义边标签，并针对编译器诊断采取行动。规范布局、固定、迁移和回执契约见 [`renderers/workflow/README.md`](renderers/workflow/README.md#layout-contracts)。

生命周期说明：相位列 `0..4` 占据主轨道；事件/终端列 `N` 在 `0..2` 中与主列 `N + 2` 完全对齐。可恢复状态使用 `type: "failure"` 加上回到活动状态的真实转换。

## 类型路由器

| 类型 | 用途 |
|---|---|
| `architecture` | 组件、服务、云/安全边界、基础设施 |
| `workflow` | 流程、审批关卡、工具调用、运维手册、CI/CD |
| `sequence` | API 调用链、请求生命周期、异步跟踪、返回 |
| `dataflow` | 管道、ETL/ELT、血缘、治理、消费者 |
| `lifecycle` | 状态/状态转换、重试、等待和终端状态 |

当存在歧义时，运行 `node bin/archify.mjs guide "<scenario>" --json`。场景证明示例是结构性引用，而非需复制的事实。

## Mermaid 输入

阅读 Mermaid 以理解拓扑和含义，然后编写全新的 Archify JSON；不要机械渲染 Mermaid 样式。

- `flowchart` / `graph` → `workflow`，或为组件映射使用 `architecture`。
- `sequenceDiagram` → `sequence`；参与者变为语义参与者，箭头变为消息。
- `stateDiagram` → `lifecycle`；状态和转换保留含义，而非 Mermaid 样式。

## 作者不变性

- 一条明显的核心路径；旁支路径从其最近的路径节点离开。在添加路由控制之前，移除低价值边。
- 默认省略 `meta.visual_preset`，确保无论其解析的颜色模式是浅色还是深色，所有图表均以 `classic` 打开。颜色模式和视觉预设相互独立：切换浅色/深色必须保留当前预设。仅当用户明确请求该视觉风格时，才设置 `signal-flow`、`blueprint` 或 `editorial`。
- 默认省略 `meta.subtitle`。绝不编造重复标题、节点或卡片内容的副标题；仅在用户明确要求时才包含一行简短的补充内容。
- 将独立桌面查看器视为首屏产物，而非浅显的条带。为笔记本和外部显示器生成一个响应式产物——切勿生成设备特定 HTML 或替代拓扑。查看器仅能从实时视口高度调整外部阅读宽度；必须保留已编写的 SVG/viewBox、比例、语义几何和正常文档流。在宽屏或大屏桌面，使用足够的已编写垂直节奏，使图表面板及其必要结论卡片构成平衡的整体；运行时缩放无法修复过度压缩的 Y 布局或过小的显式 `meta.viewBox`。移交前，在 1440×900、1600×1000 和 1920×1080 下实际打开 HTML；若构图旨在用于大屏桌面显示，额外检查 2048×1320。在每个检查尺寸下，要求 `document.documentElement.scrollWidth <= window.innerWidth` 且 `scrollHeight <= window.innerHeight`，同时在视觉上检查图表在最大检查视口中保持舒适可读且垂直平衡。通过仅移除真正冗余的内容或精简间距来修复溢出；在缩小节点、标签或主面板前。若最大视口在查看器宽度限制下仍存在明显的空底部区域，重新分配已编写的 Y 位置并成比例增加 viewBox 高度；切勿添加填充文字或装饰卡片。切勿通过 `overflow: hidden`、裁剪内容、内部图表滚动条、拉伸 SVG 高度或更小字号来虚假通过验证。窄屏/移动布局在需要时可垂直滚动。
- 对于真实的 `auto` 默认值，省略 `meta.legend`。需要时，仅使用 `mode: auto|all|hidden` 和渲染器支持的 `entries.<kind>.label|visible`；标签绝不改变语义。
- 从用户明确选择中选取一个主要编写语言；否则遵循请求或对话的主导语言。`meta.locale` 仅控制渲染器自有的查看器 UI：对对应的支持主要语言使用 `"en"` 或 `"zh-CN"`。对于其他所有语言，省略 `meta.locale`，并明确说明固定的查看器 UI 和 `<html lang>` 回退至英文。渲染器从不翻译编写内容。详见 `references/authoring-contract.md`。
- 保留确切的产品名称、代码标识符、命令、协议、API 路径和环境名称。它们在本地化文案中可保留英文，但绝不因此使周围解释性文本为其他语言。
- 品牌身份是可选且明确的。当节点名称代表真实产品时，在 `brand` 中放入规范内置 ID。若无预设匹配且用户提供了官方 HTTP(S) URL，首先运行 `node bin/archify.mjs brands capture "<url>" --json`，然后编写返回的摘要固定的 `brand` 对象。渲染和验证从不执行未固定捕获。否则省略 `brand`。切勿从“数据库”等模糊角色推断品牌，也绝不让徽章取代语义 `type`、标签或关系事实。
- 对于序列图，对于稳定的 `fixed` 布局省略 `meta.column_fit`。当 viewBox 较宽会导致水平空间未被使用，或有意义参与者标签无法放入固定框时，将其设置为 `"spread"`；在尝试 `spread` 之前，切勿缩短语义标签。
- 组件类型为 `frontend`、`backend`、`database`、`cloud`、`security`、`messagebus` 和 `external`；变体为 `default`、`emphasis`、`security` 和 `dashed`。
- 关系标签是语义数据。当发生冲突时，移动标签，调整路由或间距，然后缩短措辞同时保留含义。仅省略已被两端完全隐含且不含协议、动作、方向、同步/异步行为或跨边界机制的措辞。保留所有有意义的标签；删除标签并非几何修复。若某关系因端点完全隐含而初始无标签，解释措辞冗余的原因；这是语义作者选择，而非几何修复。
- 默认省略 `meta.engineering_profile`。区域、集群和安全边界措辞本身不使其启用。仅在用户明确要求生产部署拓扑、所有权移交或故障关闭部署审查，且源事实已知时，才启用 `deployment-ownership`。一旦启用，仅为了通过验证而移除工程配置文件的行为是不允许的；需修正事实或如实报告诊断情况。
- 间距指清晰间隙，而非中心距离。对于关系标签，清晰间隙必须超过其测量的掩码宽度；遵循保留标签的修复顺序。
- 自动路由拥有其端点侧。侧是方向契约：第一段和最后一段必须垂直于该侧离开或进入。
- 自动端口展开是架构、工作流、数据流和生命周期上默认的渲染器行为。它跳过单一关系以及显式 `via`、`channelX`、`channelY`、`labelAt` 或非常规路由。近平行端口使用外部桥梁，以便自动路由无法创建小于 8px 的线段或小于 16px 的内部转弯。架构在端口偏移小于 16px 且两端均保留角落余量时，将相互面对的自动端口（`left`/`right` 或 `top`/`bottom`）保持在同一共享轴上，确保它们不受阻碍。若恰好一个端点被展开，仅共享端点外的端点可移入该轴；若两端均被展开，保留外部桥梁，使竞争端口保持独立。
- 切勿接受边穿过无关的不透明节点、模糊的共享走廊，或关系标签遮挡其他路由的情况。

仅在需要字段枚举、间距计算、几何修复规则、仓库证据或特定模式放置时，阅读 `references/authoring-contract.md`。

## 交付

在修复过程中使用 `validate`，最终验收使用 `deliver` 一次。交付将精确规范字节冻结为私有同目录快照，渲染并检查该快照，原子提交 HTML，并为规范和产物报告 SHA-256 及字节数。这是确定性的产物证据；它不通过浏览器执行查看器。

交付后，在不修改或重新渲染可信 HTML 的情况下，收集有界的桌面证据：

```bash
node bin/archify.mjs visual-check <output.html> --json
```

`visual-check` 从精确交付的 HTML 收集自动化浏览器证据，且不修改或重新渲染它。其机器可读测量和截图不认可视觉精细度。遵循 `references/delivery-contract.md` 了解规范的回执字段、覆盖范围、辅助文件、退出行为和补充手动记录要求。

将三项声明分开：`deliver` 证明确定性产物检查，`visual-check` 证明真实浏览器中的有界行为，而感知视觉评审需要实际人工或具备图像识别能力的评审者。独立报告浏览器证据和感知评审。不受约束的粗略查看仅支持感知评审；在记录补充手动浏览器工作或处理环境故障时，使用规范交付契约。

仅在用户需要立即本地预览时添加 `--open`。对于活跃的桌面作者循环，可选命令为：

```bash
node bin/archify.mjs preview <type> <input>.json <output>.html --quality showcase
```

切勿默认启动预览。使用预览、仓库证据、导出回执、视觉评审或提交后打开时，阅读 `references/delivery-contract.md`。

## 可选查看器功能

生成的 HTML 已包含主题切换、平移/缩放、搜索、聚焦、关系追踪、语义视图、演示和真实导出功能。这些是读者功能，而非额外作者工作。`meta.animation: "trace"` 为可选；`meta.views` 为可选，且应包含最多五个精选章节。

仅当用户明确询问 Share Cards、Route/Reach 卡片、动画、引导故事、深层链接、演示、搜索/聚焦或查看器运行时其他功能时，才阅读 `references/viewer-runtime.md`。

## 设置与回退

无需在 Skill 包中安装。通过以下命令验证：

```bash
node bin/archify.mjs doctor
node bin/archify.mjs demo <output-directory>
```

当无法访问 Shell 时，将架构 SVG 手动放入 `assets/template.html`，使用 CSS 语义类而非内联颜色，并遵循 `references/delivery-contract.md` 中的视觉评审契约。

## 输出

返回检查后的 HTML 路径、图表类型、验证摘要、规范/产物回执、浏览器证据状态及真实的视觉评审状态。对于非零命令，切勿声称成功；切勿声称进行了未执行的视觉检查。
