# Archify

从一个小的 JSON 规范创建一个自包含的、交互式的 HTML 图表。静态输出是默认设置；仅在用户要求演示或演示文稿时启用动画。

## 快速创建路径

使用此受限路径进行常规生成。除非用户询问有关这些功能，否则不要阅读可选的 Viewer Runtime 参考。

1. 从问题中选择 `architecture`（架构）、`workflow`（工作流）、`sequence`（序列）、`dataflow`（数据流）或 `lifecycle`（生命周期）。
2. 在 `schemas/`、`schemas/common.schema.json` 中读取一个匹配的架构，并在 `examples/` 中读取一个匹配的 JSON 示例。只读取这些文件。新的创作意味着新的稳定 ID、领域措辞和布局；使用示例来表示字段形状，而不是事实。新的工作流源使用 `schema_version: 2` 和其可读的布局契约；仅在保留现有工作流的固定几何形状时保留 `schema_version: 1`。当实际产品标识很重要时，查询 `node bin/archify.mjs brands "<name>" --json`；仅当为未知品牌提供 URL 时，才读取 `references/brand-marks.md`。
3. 首先创建工件：下一个工具操作必须写入候选者。在检查渲染器内部之前写入候选者。不要在散文中计划精确的坐标。从一个清晰的主路径开始，短侧分支，稀疏标签，最多 12 个主要节点。将 `meta.quality_profile` 设置为 `"showcase"`，除非用户明确要求密集的 `standard` 地图。从自动路由和标签开始。在诊断调用之前不要添加 `via`、`channelX`、`channelY` 或 `labelAt`；每项修复最多应用一个诊断的几何控制。
4. 在每次候选者编辑后和移交前立即验证：

   ```bash
   node bin/archify.mjs validate <type> <candidate.json> --quality showcase --json
   ```

   仅包含 4 个工件检查的基本验证，永远不会是展示接受。展示通过必须报告所有 9 个工件检查，0 个组合错误和 0 个警告。如果候选者遗漏或拼写错误 `meta.quality_profile` 字段，则在几何形状之前修复它。对于工作流 v2 几何诊断，运行 `node bin/archify.mjs validate workflow <candidate.json> --layout-json` 并使用稳定的编译收据；求解器内部不是创作控制。通过最终验证冻结候选者：之后永远不要编辑它。
5. 对于交付的 HTML，`deliver` 是最终的接受命令：

   ```bash
   node bin/archify.mjs deliver <type> <candidate.json> <output.html> --quality showcase --json
   ```

   非零退出永远不能描述为成功。失败的交付保留任何先前的输出，因此不要在该路径上运行 `visual-check`：它将检查过时的最后一个良好工件，而不是失败的候选者。如果验证失败，仅更改诊断的 `subject`，验证 `evidence`，从 `supportedFixes` 中选择，并重新运行。在目标错误计数达到新最小值时继续专注修复。如果连续两轮没有改善该最佳计数，则停止并如实报告未解决的诊断。

## 更新意识

在第一个候选者存在后，使用 Node 运行打包的检查器 `scripts/check-update.mjs` 一次，然后继续请求的工作流。如果命令无法运行，则继续而不提及检查。

- 对于 `silent`，继续而不提及更新检查。
- 对于 `update_available`，在用户对话语言中显示一个紧凑的通知，其中包含安装版本、最新版本、检查器的固定本地摘要和官方发布说明链接。当 `severity` 为 `security` 时，将其明确标记为安全更新，并使用受约束的警告标记；这仅改变重点，永远不会改变用户自主权。明确说明已安装的技能保持不变，用户决定是否以及何时更新。您可以翻译该固定的本地句子，但永远不要引用、总结或翻译远程清单的摘要。在通知可见后，通过运行相同的检查器并使用 `--ack "<eventKey>"` 来确认其确切的 `eventKey`，然后继续用户的原始任务。

通知是信息，不是许可。保持安装版本不变；此 v0.1 工作流永远不会下载、安装或执行更新，沉默永远不是同意。

在第一个候选者之前，不要读取 `renderers/shared/geometry.mjs`、渲染器源代码、验证器源代码、测试或基准。仅当遇到不支持的内部诊断或两次专注修复失败后，才检查实现。

工作流说明：为新工作流使用架构 v2；当现有源需要固定遗留几何形状时保留架构 v1。保持语义边缘标签并针对编译器诊断采取行动。规范布局、固定、迁移和收据契约在 [`renderers/workflow/README.md`](renderers/workflow/README.md#layout-contracts) 中。

生命周期说明：阶段列 `0..4` 占据主轨道；事件/终端列 `N` 在 `0..2` 中与主列 `N + 2` 精确对齐。可恢复状态使用 `type: "failure"` 加上返回活动状态的实际转换。

## 类型路由

| 类型 | 用于 |
|---|---|
| `architecture` | 组件、服务、云/安全边界、基础设施 |
| `workflow` | 流程、审批门、工具调用、运行簿、CI/CD |
| `sequence` | API 调用链、请求生命周期、异步跟踪、返回 |
| `dataflow` | 管道、ETL/ELT、谱系、治理、消费者 |
| `lifecycle` | 状态/状态转换、重试、等待和终端状态 |

当存在歧义时，运行 `node bin/archify.mjs guide "<scenario>" --json`。场景证明示例是结构参考，不是要复制的事实。

## Mermaid 输入

读取 Mermaid 以了解拓扑和含义，然后创作新的 Archify JSON；不要机械地渲染 Mermaid 样式。

- `flowchart` / `graph` → `workflow`，或 `architecture` 用于组件地图。
- `sequenceDiagram` → `sequence`；参与者成为语义参与者，箭头成为消息。
- `stateDiagram` → `lifecycle`；状态和转换保留含义，而不是 Mermaid 样式。

## 创作不变量

- 一个明显的主路径；侧分支离开最近的主路径节点。在添加路由控制之前删除低价值边。
- 默认情况下省略 `meta.visual_preset`，因此每个图表都以 `classic` 打开，无论其解析的颜色模式是浅色还是深色。颜色模式和视觉预设是独立的：切换亮色/暗色必须保留当前预设。仅在用户明确请求该视觉样式时，才设置 `signal-flow`、`blueprint` 或 `editorial`。
- 默认情况下省略 `meta.subtitle`。永远不要编造一个重述标题、节点或卡片的副标题；仅在用户明确要求时，才包括一条简短的支持性行。
- 默认情况下将独立的桌面查看器视为第一屏工件，而不是浅条。为笔记本电脑和外部显示器生成一个响应式工件——永远不要设备特定的 HTML 或替代拓扑。查看器只能从实时视口高度调整外部的阅读宽度；它必须保留创作的 SVG/viewBox、比例、语义几何和正常文档流。在宽或高的桌面上，使用足够的创作垂直节奏，使图表面板及其必要的结论卡以平衡的整体方式占据屏幕；运行时缩放无法修复过度压缩的 Y 布局或尺寸不足的显式 `meta.viewBox`。在移交之前，在 1440×900、1600×1000 和 1920×1080 打开真实的 HTML；如果组合旨在用于大型桌面显示器，则额外检查 2048×1320。要求 `document.documentElement.scrollWidth <= window.innerWidth` 和 `scrollHeight <= window.innerHeight` 在每个检查的尺寸下，同时视觉检查图表在最大的检查视口下保持舒适可读和垂直平衡。通过删除真正冗余的内容或压缩间距来修复溢出，然后缩小节点、标签或主面板。如果最大的视口在查看器宽度上限处仍有明显的空下带，则重新分配创作的 Y 位置并按比例增加 viewBox 高度；不要添加填充文本或装饰卡。永远不要用 `overflow: hidden`、剪切内容、内部图表滚动器、拉伸 SVG 高度或更小的字体大小来伪造通过。窄/移动布局在需要时可以垂直滚动。
- 默认情况下省略 `meta.legend` 以获得真实的 `auto` 默认。当需要时，仅使用 `mode: auto|all|hidden` 和渲染器支持的 `entries.<kind>.label|visible`；标签永远不会改变语义。
- 从明确用户选择中选择一个主要创作的语言；否则，遵循请求或对话的主导语言。`meta.locale` 仅控制渲染器拥有的 Viewer UI：使用 `"en"` 或 `"zh-CN"` 对应支持的主要语言。对于其他每种语言，省略 `meta.locale` 并明确说明固定的 Viewer UI 和 `<html lang>` 回退到英语。渲染器永远不会翻译创作的內容。有关详细信息，请参阅 `references/authoring-contract.md`。
- 保留确切的产品名称、代码标识符、命令、协议、API 路径和环境名称。它们可以保留在本地化文本中为英语，但永远不要以保留周围解释性散文为理由而使用另一种语言。
- 品牌标识是可选的，并且是明确的。当节点名称是实际产品时，在 `brand` 中放置一个规范内置 ID。如果没有预设匹配，并且用户提供了官方的 HTTP(S) URL，首先运行 `node bin/archify.mjs brands capture "<url>" --json"`，然后创作返回的摘要固定 `brand` 对象。渲染和验证永远不会执行未固定的捕获。否则省略 `brand`。永远不要从模糊的角色（如“数据库”）推断品牌，并且永远不要让徽章取代语义 `type`、标签或关系事实。
- 对于序列图表，默认情况下省略 `meta.column_fit` 以获得稳定的 `fixed` 布局。当宽 viewBox 会留下未使用的水平空间或有意义参与者标签不适合固定框时，将其设置为 `"spread"`；在尝试 `spread` 之前不要缩短语义标签。
- 组件类型是 `frontend`、`backend`、`database`、`cloud`、`security`、`messagebus` 和 `external`；变体是 `default`、`emphasis`、`security` 和 `dashed`。
- 关系标签是语义数据。当一个发生冲突时，移动标签，调整路由或间距，然后缩短措辞，同时保留含义。仅省略已经完全由两个端点隐含且不包含协议、动作、方向、同步/异步行为或跨边界机制的措辞。保留每个有意义的标签；删除它不是几何修复。如果一个关系因为其端点完全隐含而未标记，解释为什么措辞是冗余的；这是一个语义创作选择，而不是几何修复。
- 默认情况下省略 `meta.engineering_profile`。区域、集群和安全边界措辞本身并不能启用它。仅在用户明确要求生产部署拓扑、所有权移交或故障关闭部署审查，并且源事实已知时，才启用 `deployment-ownership`。一旦启用，就不得仅为了通过验证而移除工程配置文件；修复事实或如实报告诊断。
- 间距意味着清晰的间隙，而不是中心距离。对于关系标签，清晰的间隙必须超过其测量的掩码宽度；遵循标签保留修复顺序。
- 自动路由拥有其端点侧。一侧是一个方向合同：第一个和最后一个段必须垂直于该侧离开/进入。
- 自动端口扩展是架构、工作流、数据流和生命周期的默认渲染器行为。它跳过单个关系和显式的 `via`、`channelX`、`channelY`、`labelAt` 或非 `auto` 路由。靠近平行端口使用外部桥接，以便自动路由无法创建小于 8px 的段或小于 16px 的内部转弯。架构单独保留未受阻碍的面对自动端口（`left`/`right` 或 `top`/`bottom`）在共享轴上，当它们的偏移量小于 16 像素，并且两个端口都保留角落间隙时。如果恰好有一个端点被扩展，则只有未共享的端点可以移动到该轴上；如果两个端点都被扩展，则保留外部桥接，以便竞争端口保持区分。
- 永远不接受跨越无关的完全不透明节点、模糊的共享走廊或关系标签掩盖其他路由的边。

仅在需要字段枚举、间距数学、几何修复规则、仓库证据或特定模式放置时，才读取 `references/authoring-contract.md`。

## 交付

在修复期间使用 `validate`，一次使用 `deliver` 进行最终接受。交付将确切的规范字节冻结为同一目录下的私有快照，渲染并检查该快照，原子性地提交 HTML，并报告 SHA-256 以及规范和工件的字节数。这是一个确定性工件证据；它不会在浏览器中执行 Viewer。

交付后，收集有界桌面证据而不修改或重新渲染受信任的 HTML：

```bash
node bin/archify.mjs visual-check <output.html> --json
```

`visual-check` 从确切的交付 HTML 收集自动的浏览器证据而不修改或重新渲染它。其机器可读的测量值和屏幕截图不会批准感知上的完善。遵循 `references/delivery-contract.md` 以获取规范收据字段、覆盖范围、副产物、退出行为和补充手动记录要求。

将三个声明分开：`deliver` 证明确定性工件检查，`visual-check` 证明在真实浏览器中的有界行为，感知视觉审查需要一个实际的人类或图像功能的审查者。独立报告浏览器证据和感知审查。无约束的扫视只能支持感知审查；在记录补充手动浏览器工作或处理环境故障时，使用规范交付契约。

仅在用户希望立即本地预览时才添加 `--open`。对于活动的桌面创作循环，可选命令是：

```bash
node bin/archify.mjs preview <type> <input>.json <output>.html --quality showcase
```

默认情况下永不开始预览。使用预览、仓库证据、导出收据、视觉审查或提交后打开时，请读取 `references/delivery-contract.md`。

## 可选的查看器功能

生成的 HTML 已经包含主题切换、平移/缩放、搜索、聚焦、关系跟踪、语义视图、演示和真实导出。这些是读者功能，不是额外的创作工作。`meta.animation: "trace"` 是可选的；`meta.views` 是可选的，应最多包含五个策划章节。

仅在用户明确要求分享卡、路线/可达卡、动画、引导故事、深度链接、演示、搜索/聚焦或另一个 Viewer Runtime 功能时，才读取 `references/viewer-runtime.md`。

## 设置和回退

技能包内不需要安装。通过以下命令验证：

```bash
node bin/archify.mjs doctor
node bin/archify.mjs demo <output-directory>
```

当无法访问 Shell 时，将架构 SVG 放置到 `assets/template.html` 中，使用 CSS 语义类而不是内联颜色，并遵循 `references/delivery-contract.md` 中的视觉审查契约。

## 输出

返回检查的 HTML 路径、图表类型、验证摘要、规范/工件收据、浏览器证据状态和真实的视觉审查状态。不要因为非零命令或声称执行了未执行的视觉检查而声称成功。
