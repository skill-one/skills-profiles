# explore-code

将此作为 Rigor Improve 实现的叶级技能使用。安装后的别名
remains `explore-code` 以保持兼容性。

使用
`../ai-research-reproduction/references/agent-operating-principles.md` 中的共享操作原则；该技能应指导有限的候选代码工作，而不过度规定实现细节。

## 适用场景

- 当研究者在隔离分支或工作区上明确授权探索性代码变更时。
- 当任务为源锚定模块移植、主干适配、LoRA 或适配器插入，或低风险模块组合时。
- 当仅需要摘要级记录即可满足要求，且结果为候选而非可信结论时。

## 不适用场景

- 当请求为可信基线工作、保守调试或正常训练执行时。
- 当用户未明确授权探索性修改时。
- 当任务为广泛重构或从零开始实现想法时。

## 明确边界

- 本技能仅拥有探索性代码修改的职责。
- 必须将工作与可信基线保持隔离。
- 当任务同时涵盖 `current_research` 协调与探索性运行范围时，应改用 `ai-research-explore`。
- 可以将其执行交由 `minimal-run-and-audit` 或 `run-train`。
- 应优先选择源锚定的复制和最小化适配，而非自由改写。
- 应记录候选变更的意义、如何回滚，以及为何其仍为候选而非已验证的贡献。

## 输出预期

- `explore_outputs/CHANGESET.md`
- `explore_outputs/SCIENTIFIC_CHANGELOG.md`
- `explore_outputs/COMPARABILITY_REPORT.md`
- `explore_outputs/TOP_RUNS.md`
- `explore_outputs/status.json`

## 说明

使用 `references/explore-policy.md`、`../ai-research-reproduction/references/research-rigor-principles.md`、`scripts/plan_code_changes.py` 以及 `scripts/write_outputs.py`。
