# CCF 可视化构建器

## 家族文件合约

在编写前，确定每个任务/产物的规范输出和一个稳定的 working directory。重用明确的或已建立的任务路径；否则使用项目根目录 `ccfa-workfiles/<用途>/<产物ID>/`，仅在需要时使用 `source/`、`assets/`、`cache/` 和 `build/`。就地更新当前文件；不要分散中间文件或创建迭代副本。保留输入和所需证据；仅清理由此任务创建的已验证的可丢弃文件。使用 UTF-8 文本 I/O，并在保存或渲染后检查中文文本。对于文件工作，应用 [artifact-contracts.md](../ccf-common/references/artifact-contracts.md) 并在技能转换时重用相同的路径。

## 协作合约

在专家执行前，首先阅读并应用 [ccf-humanization](../ccf-humanization/SKILL.md)，然后应用 [ccf-common](../ccf-common/SKILL.md)。在每次交接时，重用适用的活跃规则或刷新缺失/更改的规则。即使没有文字，这两个预检也是必需的；详细的编辑、实验和维护模式仅在相关时运行。

保留一个集成的负责人，并积极使用其他技能来解决缺失的先决条件或检查材料发现。重用适用的证据；不要跳过必要的准备工作以节省 token。在最终确定前，集成贡献并验证受影响的成果。遵循条件性的 [合作路线](../ccf-common/references/routing.md)；避免不相关的阶段和重复报告。

## 调用控制

**CCFA 交接模式：PARTIAL（推荐）。** 遵循 `metadata.ccf_skill_controls.handoff_question_mode`、`../ccf-common/references/handoff-modes.md` 和 `../ccf-common/references/task-modes.md`。重用上下文中已有的共享规则。

对于新的科学方法或架构概念，除非用户请求纯 SVG/代码优先输出或选择退出，否则 GPT Image 2 保持为默认的首选渲染器。使用验证的主机功能及其隐私/图像说明。不要将未知的后端标记为 GPT Image 2。现有的授权涵盖必要的生成和请求的重建；仅在请求之外时才提供额外格式。

## 核心规则

从提供的內容创建可读的视觉。保留值、单位、不确定性、精确标签、方法模块和类型连接。定量图使用可重复的代码。缺失的数据或拓扑需要相关证据负责人；不要编造它来完成一个组合。保留科学术语和规范的大写缩写；普通标签使用自然大小写。

将目的地分类为论文机制图、演示/海报或 README/宣传。论文图显示表示和计算。从方法中选择视觉语法，而不是固定的阶段卡模板。

对于新的组合，使用 `references/visual-contract.md`：紧凑的内容适配画布、共享的对齐锚点、缩放的间隙，以及最终尺寸检查的排版。不要默认为方形或强制固定宽高比。Times New Roman 是默认值；Comic Sans MS 用于请求的漫画处理，取决于用户/场所的排版。对于新的视觉方向，从 `references/adaptive-architecture-style.md` 选择一个功能预设。检查提供的参考，根据解释的重要性分配空间，并保留仅必要的标签/数字。

## 模式和选择性参考

仅阅读下文的相关部分。本地编辑从现有源和适用 QA 开始；它不会重新加载完整的生成工作流。

| 模式 | 使用和参考 |
| --- | --- |
| `visual-contract` | 非平凡的內容/证据/输出决策：`references/visual-contract.md`。 |
| `figure-design`, `python-plotting` | 数值图：从 `references/python-plot-recipes.md` 选择，然后从 `resources/python/ccfa_plot_recipes.py` 导入需要的配方；仅当调试或修改它时才阅读实现。`references/plot-inspiration-map.md` 是可选的，用于未解决的图表选择。 |
| `architecture-generation` | 新概念：`references/architecture-diagram-generation.md`；仅论文特定的语法来自 `references/paper-vs-presentation-diagrams.md`。 |
| `pure-svg-generation` | 显式的确定性路线：直接使用支持的网络拓扑和矢量创作源。 |
| `editable-reconstruction` | `references/architecture-diagram-generation.md` 中的语义重建部分；仅当 PPTX 时加载 `references/editable-pptx.md`。 |
| `reference-layout-blueprint` | 提供的参考组合：`references/reference-layout-blueprint.md`；当需要提示细化时使用 `references/adaptive-architecture-style.md`。 |
| `icon-system` | 原生基元、可重用的许可图标或必要的自定义资产：`references/icon-system.md`。 |
| `table-design`, `layout-integration` | 提供的值、面板/浮动/标题放置：`references/figure-table-layout.md`。 |
| `render-qa` | 使用 `references/render-qa.md` 中的相关检查检查请求的格式。 |

仅在选择或更改颜色语义时使用 `references/palette-and-accessibility.md`。当它们仍然适用时，重用已建立的调色板和图标家族。

## 工作流

1. 确定请求的产物、现有源、最终尺寸、目的地、格式和科学要点。对于文件工作，一次读取 `../ccf-common/references/artifact-contracts.md` 并在渲染前确定规范输出和工作路径。将不相关的图保留在单独的稳定工作目录中；尊重现有的项目路径。
2. 在渲染依赖内容前解决科学先决条件：源值、单位、度量意义、拓扑和预期信息。使用 `ccf-experiment-designer` 处理未解决的结果语义，使用方法的负责人处理拓扑，或使用 `ccf-integrity-auditor` 处理源冲突；集成他们的证据，不要编造缺失的内容。拓扑、标签、数据位置、布局、样式和来源重用一个规范。不要保存重叠的合约、提示草稿、线框图或 QA 日志。一个小的编辑重用未更改的先决条件，并仅检查受影响的依赖项。
3. 选择完成任务的渲染路线中最小的路线。新的架构概念使用默认的图像工作流。对于现有的 SVG、PPTX 或图脚本，直接编辑该创作源并导出受影响的请求格式；不要为标签、颜色、间距、数据或导出更改运行新的光栅概念传递。光栅编辑遵循主机图像编辑工作流，并使用现有的图像作为参考。
4. 保留详细的用户提示，并在一次添加缺失的约束。对于全面重新设计，包括参考角色、布局几何、文本清单、排版和调色板，以使其具体化；不要将这些截断为任意字数限制。重用批准的拓扑、布局 token 和资产。从完整的候选者开始，除非请求了替代方案。仅当解决特定的未满足需求时，搜索或生成资产。
5. 检查草稿是否符合布局和科学合约。在请求的重建期间纠正矢量/原生文本和几何；对于光栅交付，使用有针对性的图像编辑来修复文本、间距或插图缺陷，并保留接受的区域。如果两次尝试无法修复相同的缺陷，诊断原因并更改相关策略。在可行的更正仍然存在时，不要仅仅因为尝试次数而停止。
6. 作为语义组、活文本、形状和类型连接构建请求的可编辑输出。不要嵌入整个光栅并声称可编辑。将不可避免的图像资产保留为单独的，并描述它们的实际可编辑性。从规范创作源生成下游 PDF/PPTX，无损失往返；仅保留必要的可重用源和资产。
7. 检查更改的输出，包括数据/拓扑、整个图的紧凑性、共享边缘/基线、最终尺寸文本、裁剪、对比度和请求的可编辑性。本地编辑还检查附加的连接器和受保护的区域。首先渲染受影响的页面/幻灯片；仅在更改的共享样式/布局影响它们时才扩展。在工作构建目录下保存一个当前预览；重用满意的检查。
8. 完成请求的可交付成果，并检查文件位置、当前导出和可丢弃的临时文件。新的数据/协议决策属于 `ccf-experiment-designer`，手稿文字属于 `ccf-paper-writer`，声明不匹配属于 `ccf-integrity-auditor`；保持未受影响的授权工作继续。

## 输出合约

首先交付请求的视觉和必要的可编辑源/格式。仅需要规范的请求不需要渲染。返回规范路径、有用的来源、实际的 QA 结果和材料可编辑性限制。仅在需要或请求时，将完整的提示、规范和清单保留在一个可重用的源记录中；不要在最终答案中也重复它们。保留明确的精确输出请求。
