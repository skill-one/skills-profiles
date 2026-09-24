# ai-research-explore

## 目的

在研究人员明确授权在持久化 `current_research` 锚点之上开展仅针对候选的工作后，将其用作兼容 Rigor Explore 的 skill slug。安装时保留的 slug 为 `ai-research-explore`，以保证兼容性。Rigor Explore 用于有意义且可能具有新颖性的深度学习研究候选，同时保持科学严谨性、可比性、可重复性和可审计的协作。新颖性和重要性在文献对比、消融证据和公平对比之前仍属于假设。该技能不承诺自主发现、全球基准的完整性、新颖性证明，或可信的复现成功。

从 `../ai-research-reproduction/references/agent-operating-principles.md` 中的共享操作原则开始，然后为研究声明加载 `../ai-research-reproduction/references/research-rigor-principles.md`，并在实验细节影响可比性或可重复性时加载 `../ai-research-reproduction/references/deep-learning-experiment-principles.md`。

## 适配条件

仅在请求同时满足以下条件时使用该技能：

- 明确的探索授权，例如仅针对候选的工作、独立的分支或工作区、遍历（sweep）、多种变体或探索性排序。
- 持久的 `current_research` 上下文，例如分支、提交、检查点、运行记录，或已训练的本地模型状态。

将仅涉及代码的狭窄请求保留在 `explore-code`。将仅涉及运行的狭窄请求保留在 `explore-run`。将被动式仓库分析保留在 `analyze-project`。将 README 优先的复现保留在 `ai-research-reproduction`。

## 研究节奏

采用双重循环节奏：

- 外层循环：理解仓库、冻结任务/数据集/评估/预算、保留用户想法、梳理来源、对想法进行把关，并决定下一个实验是否值得运行。
- 内层循环：完成一次有边界的候选修改或运行，进行冒烟检查，收集证据，将其与当前锚点进行对比排名，然后停止或带着新的证据返回外层循环。

该节奏是指导，而非严格的自主循环。遇到明确的阻塞、不明确的研究意义、预算耗尽、缺失锚点/评估，或需要人工检查点时停止。

## 工作流程

1. 确认 `current_research` 及明确的探索通道授权。
2. 接受传统的 `variant_spec` 或更高层级的 `research_campaign`。
3. 在活动（campaign）模式下，在进行候选工作前冻结任务、数据集、基准、评估来源、SOTA 参考和预算。
4. 仅通过 `analyze-project` 构建当前活动所需的仓库理解产物。
5. 在来源支持相关时，运行有边界且优先使用缓存的源码检索；优先在可用时使用本地精选文献，如 Zotero，然后使用种子来源、仓库本地定位器、公共定位器或可选的网络检索。将检索视为来源解析，而非开放式的文献搜索。
6. 保留研究者提供的想法，可选地添加一小组有边界的单变量种子想法，并使用明确的把关和评分分解对想法进行排名。
7. 优先每次只选择一个清晰的候选。使用 `explore-code` 进行有边界的代码适配，使用 `explore-run` 进行短期周期试验或遍历（sweep）。
8. 仅在探索性计划需要实际执行证据时，使用 `minimal-run-and-audit` 或 `run-train`。
9. 根据适当性将仅针对候选的输出写入 `analysis_outputs/`、`sources/` 和 `explore_outputs/`；切勿将探索性收益呈现为可信的复现成功。包含 `SCIENTIFIC_CHANGELOG.md` 和 `COMPARABILITY_REPORT.md`，用于记录候选的科学意义与比较边界。

## 排序与证据

- 执行前，按预期收益、成本、成功可能性、补丁范围、依赖拖拽、评估风险和回滚便捷度对候选进行优先排序。
- 执行后，首先依据真实证据进行排名：命令状态、观测到的指标、产物、变更路径、冒烟结果和可重复性说明。
- 保持研究者提供的 `evaluation_source` 和 `sota_reference` 在整个活动周期内冻结，不得声称它们是全局完备的。
- 如果顶层想法过于接近，或实现无法分解为可审计的单位，则停止并进入检查点，而非静默选择。

## 活动输入

`research_campaign` 是 Rigor Explore 活动的首选，但应保持最小化。持久的核心要素为：

- `current_research`
- `task_family`
- `dataset`
- `benchmark`
- `evaluation_source`
- `sota_reference`
- `compute_budget`

将 `candidate_ideas`、`variant_spec`、`research_lookup`、`idea_policy`、`idea_generation`、`source_constraints`、`feasibility_policy`、`baseline_gate` 和 `execution_policy` 作为可选指导，而非代理必须为每个活动填写的字段。参见 `references/research-campaign-spec.md` 了解高级模式与产物预期。

## 参考加载

- 加载 `references/ai-research-explore-policy.md` 以了解通道安全与候选语义。
- 仅当存在活动文件或用户要求 Rigor Explore 活动治理时，加载 `references/research-campaign-spec.md`。
- 加载 `../ai-research-reproduction/references/explore-variant-spec.md` 以了解运行级别变体矩阵详情。
- 在提出或排名候选修改之前加载 `../ai-research-reproduction/references/research-thinking-loop.md`；这是必要的贪心观察-定位-设计-比较循环。
- 在作出新颖性、贡献、SOTA 或可比性声明之前，加载 `../ai-research-reproduction/references/research-rigor-principles.md`。
- 如果存在 `~/.rigorpilot/PERSONAL_RIGOR.md`，则在 `../ai-research-reproduction/references/continuous-learning-policy.md` 下查阅（仅作建议；核心原则优先）。
- 当训练、评估、基线、消融、指标、检查点或数据集详情相关时，加载 `../ai-research-reproduction/references/deep-learning-experiment-principles.md`。
- 使用 `scripts/orchestrate_explore.py` 和 `scripts/write_outputs.py` 执行现有的确定性产物工作流。
