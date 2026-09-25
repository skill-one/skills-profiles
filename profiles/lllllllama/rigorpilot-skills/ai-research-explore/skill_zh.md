# ai-research-explore

## 目的

在研究员明确授权在持久性 `current_research` 锚点之上进行候选工作之后，使用此作为 Rigor Explore 兼容的技能别名。安装的别名保持为 `ai-research-explore` 以确保兼容性。Rigor Explore 用于有意义且可能具有新颖性的深度学习研究候选，同时保持科学严谨性、可比性、可复现性和可审计的合作。新颖性和重要性在文献对比、消融证据和公平比较之前仍然是假设。该技能不承诺自主发现、全局基准完整性、新颖性证明或可信赖的复现成功。

从 `../ai-research-reproduction/references/agent-operating-principles.md` 中的共享操作原则开始，然后加载 `../ai-research-reproduction/references/research-rigor-principles.md` 以进行研究声明，并在实验细节影响可比性或可复现性时加载 `../ai-research-reproduction/references/deep-learning-experiment-principles.md`。

## 适用范围

仅在使用请求同时具有以下内容时使用此技能：

- 明确的探索授权，例如候选工作、隔离分支或工作树、扫描、多个变体或探索性排序。
- 持久的 `current_research` 上下文，例如分支、提交、检查点、运行记录或已训练的本地模型状态。

将狭义的代码请求保留在 `explore-code` 上。将狭义运行请求保留在 `explore-run` 上。将被动仓库分析保留在 `analyze-project` 上。将 README 优先的复现保留在 `ai-research-reproduction` 上。

## 研究节奏

使用双循环节奏：

- 外循环：理解仓库、冻结任务/数据集/评估/预算、保留用户想法、映射来源、筛选想法，并决定下一个实验是否值得运行。
- 内循环：进行一次有边界的候选更改或运行、进行冒烟测试、收集证据、将其与当前锚点进行比较，并要么停止，要么带着新证据返回外循环。

这种节奏是一个指导，而不是一个严格的自主循环。在明确的障碍、不明确的科学意义、预算耗尽、缺少锚点/评估或人类检查点时停止。

## 工作流程

1. 确认 `current_research` 和明确的探索车道授权。
2. 接受 legacy `variant_spec` 或更高级别的 `research_campaign`。
3. 在战役模式下，在候选工作之前冻结任务、数据集、基准、评估来源、SOTA 参考和预算。
4. 仅构建当前战役所需的仓库理解工件，通常通过 `analyze-project` 完成。
5. 当来源支持重要时，运行有边界的、缓存优先的来源查找；如果可用，优先选择本地整理的文献，如 Zotero，然后是种子来源、仓库本地定位器、公共定位器或可选的网页查找。将查找视为来源解析，而不是开放式文献搜索。
6. 保留研究员提供的思想，可选地添加一小部分单变量种子思想，并使用明确的筛选器和分数明细对思想进行排名。
7. 一次优先考虑一个清晰候选。使用 `explore-code` 进行有边界的代码适应，使用 `explore-run` 进行短周期试验或扫描。
8. 仅在探索性计划需要实际执行证据时使用 `minimal-run-and-audit` 或 `run-train`。
9. 将候选输出到 `analysis_outputs/`、`sources/` 和 `explore_outputs/`，视情况而定；永远不要将探索性收益呈现为可信赖的复现成功。包括 `SCIENTIFIC_CHANGELOG.md` 和 `COMPARABILITY_REPORT.md` 以说明候选的科学意义和比较边界。

## 排名和证据

- 在执行之前，按预期收益、成本、成功可能性、补丁表面、依赖拖拽、评估风险和回滚易用性对候选进行优先级排序。
- 在执行之后，首先按真实证据排名：命令状态、观察到的指标、工件、更改路径、冒烟结果和可复现性笔记。
- 保持研究员提供的 `evaluation_source` 和 `sota_reference` 在战役期间冻结；不要声称它们是全局完整的。
- 如果顶级想法过于接近或实现无法分解为可审计单元，则停止进行检查点，而不是无声地选择。

## 战役输入

`research_campaign` 是 Rigor Explore 战役的首选，但它应保持最小化。持久核心是：

- `current_research`
- `task_family`
- `dataset`
- `benchmark`
- `evaluation_source`
- `sota_reference`
- `compute_budget`

使用 `candidate_ideas`、`variant_spec`、`research_lookup`、`idea_policy`、`idea_generation`、`source_constraints`、`feasibility_policy`、`baseline_gate` 和 `execution_policy` 作为可选指导，而不是代理必须为每个战役填写字段。有关高级模式和工作件期望，请参阅 `references/research-campaign-spec.md`。

## 参考加载

- 加载 `references/ai-research-explore-policy.md` 以确保车道安全和候选语义。
- 仅在存在战役文件或用户要求 Rigor Explore 战役治理时加载 `references/research-campaign-spec.md`。
- 加载 `../ai-research-reproduction/references/explore-variant-spec.md` 以获取运行级变体矩阵详细信息。
- 在提出或排名候选更改之前加载 `../ai-research-reproduction/references/research-thinking-loop.md`；这是必需的贪婪观察-设计-比较循环。
- 在做出新颖性、贡献、SOTA 或可比性声明之前加载 `../ai-research-reproduction/references/research-rigor-principles.md`。
- 如果存在，则咨询 `~/.rigorpilot/PERSONAL_RIGOR.md`，位于 `../ai-research-reproduction/references/continuous-learning-policy.md` 下（仅供参考；核心优先）。
- 当训练、评估、基线、消融、指标、检查点或数据集详细信息重要时加载 `../ai-research-reproduction/references/deep-learning-experiment-principles.md`。
- 使用 `scripts/orchestrate_explore.py` 和 `scripts/write_outputs.py` 以用于现有的确定性工件工作流程。
