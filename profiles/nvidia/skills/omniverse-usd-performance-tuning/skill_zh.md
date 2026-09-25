# Omniverse USD 性能调优

## 范围

用于广泛的 USD 性能工作：加载缓慢、低 FPS/交互性、高 GPU 或系统内存、GPU崩溃/设备丢失、验证失败、CAD/转换质量筛选、分析、或请求优化场景。此技能拥有面向用户的流程；设置、认证、分析、验证、变异和报告在达到时由阶段引用执行。

Frontmatter 将 `version` 和 `tools` 保持在顶层以兼容 agentskills.io；NVCARPS 字段位于 `metadata` 下。

## 强制会话启动门

在除静态分类答案外的任何调优输出之前，请遵循 `skills/omniverse-usd-performance-tuning/references/setup-usd-performance-tuning/references/runtime-context-header.md`。该引用拥有 `output_path`、`setup-preflight.json`、格式 A/格式 B，并禁止静默的临时探测。

所需行为：

- 缺失或不可读的预检：调用 `setup-usd-performance-tuning`。
- 存在预检：打印格式 A 并等待用户的答案。该引用拥有选项集；此处不要重述或发明选项。
- 本会话中已确认的运行时：使用紧凑格式 B：

```text
[套件：{runtime_context.kit.application} {runtime_context.kit.version}  |  SO：{runtime_context.usdOptimize.version}  |  AV：{runtime_context.assetValidator.version}]
```

对于独立/usd-optimize 包，运行时证据必须包括包/哨兵检查以及共享库或导入/加载验证，而不仅仅是 Python 可执行文件/版本。对于 `omniverse://` 资产，在设置、筛选或首次打开之前，通过 `omniverse-authentication` 路由。

## 入口技能和决策规则

- 每当验证任何运行时路径时（套件、独立或部分堆栈，例如 usd-validation-nvidia 仅），将 `omniverse-usd-performance-tuning` 作为入口技能命名。如果请求的工具或操作缺失，请返回具体的阻止代码，例如 `blocked_missing_usd_optimize` 或 `blocked_missing_usd_optimize_operation`；不要替换不同的流程。
- 仅当未验证运行时路径且运行时选择/设置是第一个未解决的问题时，将 `setup-usd-performance-tuning` 作为入口命名。
- 这是所有权，不是阶段顺序：认证、设置和筛选仍按其正常顺序运行。

规划决策——根据响应的形状导出 `decision`，而不是根据请求是否命名了破坏性操作（套件强制执行形状不变量）：

- `ready_to_plan`——此响应中没有任何内容等待用户；`committed_milestones` 等于 `planned_phases`。这是通用优化的默认值：无损规范链，加上主动的 `auto-within-tolerance` 有界损失传递（一个视觉容差的目标减少在其保守的每个目标带，使用一行通知而不是提示）。
- `approval_required`——此响应在当前阶段停止；`committed_milestones` 是 `planned_phases` 的严格前缀，`approval_required_reason` 指出阶段。触发器是代理必须在此计划操作之前展示的未解决决策，而不是操作破坏的事实。默认的拟合操作在拟合候选场景（例如 BIM/CAD 管道和风管运行，使用默认参数的 `fitPrimitives`）是标准预期胜利并保持 `ready_to_plan`，在执行时受阶段限制。有界损失操作（`decimateMeshes`、`fitPrimitives`）仅在它将在保守带之上运行时、在功能精度目标（`articulated`/物理/模拟准备/计量/变体）上或在使用明确保留意图（用户请求保留 UVs/displayColors/subsets）时变为 **内联触发**——其容差或数据保留参数必须立即回答——对于 `decimateMeshes` 请求没有声明的容差，通过其一个前置 `mm_tolerance` 问题内联触发。响应当前展示的 `restructure-decision` 是 `approval_required`，原因相同。有关应用权威类的信息，请参阅 `usd-optimize-run-operations/references/operation-safety.md`。
- `blocked`——适用 `blocked_code`。
- 以后真正触发的未来阶段——尚未达到的下游 `restructure-decision`、为阶段 7 选入菜单收集的身份验证操作——应属于 `gates_observed`，而不是 `decision`。

## 规范计划合同

对于广泛优化，结构化计划/状态摘要必须：

- 以 `omniverse-usd-performance-tuning` 开始里程碑列表；仅在相关时将 `setup-usd-performance-tuning` 作为阶段 0 上下文包含。
- 将顶层 `decision` 设置为 `ready_to_plan` 以进行通用优化。
- 在 `committed_milestones` 和 `planned_phases` 中都包含到 `optimization-report` 的链。
- 使用确切的配置文件标签 `profile-stage:baseline` 和 `profile-stage:after`；永远不要发出裸 `profile-stage`。
- 精确保留此子序列，仅在它不会重新排序它时插入可选分析：

`omniverse-usd-performance-tuning` -> `profile-stage:baseline` -> `usd-structure-assessment` -> `usd-validation-runner` -> `restructure-decision` -> `apply-restructure` -> `usd-optimize-run-validators` -> `usd-optimize-interpret-validators` -> `usd-optimize-run-operations` -> `profile-stage:after` -> `compare-profiles` -> `optimization-report`

两个里程碑是 **有条件必需的**——当触发器有效时，它们必须作为已提交的里程碑出现在此位置，而不仅仅是路由到：

- `usd-hierarchy-dedupe-candidates`——在 `usd-structure-assessment` 之后、`restructure-decision` 之前，每当阶段显示重复的复制层次结构、高网格计数而几乎没有实例化，或单体根时。在没有它的情况下不要得出 `hierarchy_dedupe.recommended: false`。
- `usd-edit-target-planner`——在 `apply-restructure` 之后、Usd Optimize 验证器/操作链之前，每当阶段由（引用或有效负载）组成，并且每个目标都必须作为其自己的根层进行优化时。

在广泛优化的里程碑摘要中不要列出 `usd-optimize-run-validators` 或 `usd-optimize-interpret-validators` 在 `restructure-decision` 之前。阶段感知验证路由仍在 `usd-validation-runner` 内发生。

默认广泛优化为三个范围迭代，除非用户选择退出、请求快速传递或适用停止标准。每次迭代都会写入一个中期报告/更新；后续传递会重用先前的证据而不是重新启动完整工作流。

## 执行规范

- 在端到端执行之前加载 `references/workflow.md`；它拥有阶段 0-7 流程、套件/独立分支、验证器路由、操作排序、终止标准、持续时间提示和默认三传递模式。
- 不要将嵌套阶段名称视为清单标签。在执行阶段之前，加载该阶段的嵌套 `README.md` 或引用并遵循它。仅在达到其阶段时才调用下游技能主体。
- 如果提供本地工作区指令或辅助命令，请检查它们并使用它们来创建、验证或渲染所需工件。如果文件/工具不可用，请报告观察到的阻止因素，而不是编造完成。
- 对于二进制或大型资产，不要打印原始内容。使用有界元数据、校验和、大小、验证/配置文件摘要、紧凑事实或工具报告。
- 在读取套件日志、usd-validation-nvidia CSV、Usd Optimize 日志、Tracy CSV 或其他运行时输出之前，请遵循 `references/runtime-artifact-token-budget.md`：将原始工件保留在磁盘上，首先读取摘要 JSON，并使用有界快照而不是完整转储或实时流。

收集的最小上下文：目标阶段、问题/目标、本地/挂载/远程位置、运行时、已知的工作负载类型、诊断与变异、写入的权限/输出目标。除非明确允许，否则不要覆盖源；优先为变异创建单独的优化输出。不要编造阈值、百分比胜利、指标或运行时证据。

## 路由图

- 组成、结构、层健康、实例化准备：`usd-structure-assessment`。
- 验证/内容问题：`usd-validation-runner`，它根据需要路由到 validate-* 或 Usd Optimize 验证器。
- 编辑目标、变体、有效负载和输出决策：`usd-edit-target-planner`。
- 重复复制的层次结构/高网格计数且无实例化：`usd-hierarchy-dedupe-candidates`。
- 单体阶段或资产边界材料化：`restructure-decision` 然后在批准时 `apply-restructure`。
- CAD 转换器设置：`references/cad-conversion/README.md`。
- Usd Optimize 执行：`usd-optimize-run-validators`、`usd-optimize-interpret-validators`、`usd-optimize-run-operations`。
- 完整套件运行时分析，如 FPS、帧时间、Hydra/RTX 指标：外部 NVIDIA/omniperf 分析技能。

在路由广泛工作之前，请阅读 `usd-structure-assessment` 权衡引用，以在相关决策时考虑管道阶段和工厂级结构。

## 变异和操作规则

遵循 `references/workflow.md#operation-ordering-invariants`。高级不变量：原型优先 -> 每个资产验证 -> 阶段级操作最后。

始终：

- 在变异之前运行组成审计。
- 在处理器执行之前和之后进行验证。
- 在每个资产验证之前优化原型。
- 在对非常大的 CAD 场景进行整个阶段的网格去重之前检查层次级重用。
- 基于瓶颈证据提出建议；不要在没有发现的情况下推荐固定堆栈。
- 当写入不被允许时，不要授权变异。

Usd Optimize 管理：

- 当多个操作可以解决相同发现时，优先选择 `references/operations/operations.json` 中的 `canonical` 操作。
- 顶点焊接：优先选择具有显式标志的规范 `meshCleanup` 而不是独立的 `mergeVertices`；在变异之前遵循上游 `usd-optimize` 机制和本地批准策略。
- 层次结构去重：对于阶段 2 下降，优先选择 `usd-hierarchy-dedupe-candidates` 加上 `apply-restructure`（它拥有清单/身份合同）；一个独立的批准链去重运行直接驱动 `deduplicateHierarchies`，按前沿区域（`paths` + 每个区域的 `maxDepth`）调用。
- 每个网格去重：优先选择规范 `deduplicateGeometry`；`findCoincidingGeometry` 仅用于分析和报告。
- 不要代理发起 `documentary` 操作，例如 `boxClip`、`deletePrims`、`removeAttributes`、`removeUntypedPrims`，或在非实例化情况下广泛的 `merge`，除非明确请求。
- 当验证器证据将它们连接到 `usd-optimize-interpret-validators` 或下游上下文需要它们时，允许 `specialty` 操作，例如 `sparseMeshes`、`optimizePrimvars`、`primitivesToMeshes`、`utilityFunction` 或 `pythonScript` 配方。

## 交付成果和最终响应

端到端优化必须在变异运行时产生优化的 USD 阶段和 `optimization-report` 报告。仅诊断工作仍需以报告或摘要结束，说明未写入优化的阶段。

报告要求：

- 结构化 JSON 必须符合 `optimization-report` 的 `scripts/optimization-report.schema.json`。
- 保存生成的 Markdown 摘要。
- 通过 `render_preview.py` 从 `references/report-templates/optimization-report.html.template` 渲染 HTML；永远不要手写 HTML。
- 不要用临时的摘要文件或仅聊天回顾替换报告工件。

最终运行时响应必须明确命名：

- 选定的入口技能和选定的运行时/预检状态，包括适用时的独立包哨兵/加载证据；
- 写入的优化 USD 输出路径，或未运行变异；
- 源未覆盖/原位变异状态；
- 执行的确切操作链，特别是当声称安全/无损链时；
- 可用的验证前/后和配置文件指标；
- 验证的报告 JSON、生成的 Markdown、渲染的 HTML、规范/验证裁决、分数（如果存在），以及 `workflow_mode`。

如果预检缺失、验证/渲染失败、报告工件缺失或未运行变异，请明确说明，不要用聊天回顾替换缺失工件。

## 限制和引用

此技能不会安装运行时、替换下游引用指令、本身认证远程资产、批准未请求的破坏性写入，或在没有证据的情况下保证性能提升。如果运行时状态不明确，请返回设置门；如果变异出现在证据之前，请先返回基线分析和组成审计。

主要引用：

- `references/workflow.md`
- `references/briefing-the-skill.md` — 请求应说明的内容，以及原因。当简报薄弱时阅读它：它命名了决定策略的四个因素，以及沉默地影响质量的措辞（一个声明的三角形计数，一个声明的网格计数）。
- `references/runtime-artifact-token-budget.md`
- `references/skill-map.md`
- `skills/omniverse-usd-performance-tuning/references/setup-usd-performance-tuning/references/runtime-context-header.md`
- `skills/omniverse-usd-performance-tuning/references/usd-structure-assessment/references/optimization-tradeoffs.md`
- `skills/omniverse-usd-performance-tuning/references/usd-structure-assessment/references/factory-level-structuring.md`
- `skills/omniverse-usd-performance-tuning/references/usd-structure-assessment/references/composition-audit.md`
- `skills/omniverse-usd-performance-tuning/references/usd-validation-runner/README.md`
- `skills/omniverse-usd-performance-tuning/references/optimization-report/references/optimization-report-template.md`
- `references/upstreams/usd-optimize.md`

当网络访问可用且当前上游行为重要时，使用参考文件中注明的实时 URL。
