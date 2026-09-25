# explore-code

将此用作 Rigor Improve 实现的叶子技能。安装的 slug 保持为 `explore-code` 以确保兼容性。

使用 `../ai-research-reproduction/references/agent-operating-principles.md` 中的共享操作原则；该技能应指导有边界的候选代码工作，而不会过度规定实现细节。

## 何时应用

- 当研究人员明确授权在隔离分支或工作集中进行探索性代码更改时。
- 当任务是基于源模块移植、骨干适应、LoRA 或适配器插入，或低风险模块组合时。
- 当摘要级别的记录就足够，且结果是候选方案，而非可信结论时。

## 何时不应用

- 当请求是用于可信基线工作、保守调试或正常训练执行时。
- 当用户未明确授权探索性修改时。
- 当任务是一个广泛的重构或从头开始的实现时。

## 明确边界

- 该技能仅拥有探索性代码修改。
- 它必须将工作与可信基线隔离。
- 当任务跨越当前_research 协调和探索性运行时，应使用 `ai-research-explore`。
- 它可以将执行移交给 `minimal-run-and-audit` 或 `run-train`。
- 它应优先选择基于源的复制和最小化适配，而非自由形式的重写。
- 它应记录候选更改为何有意义、如何回滚，以及为何它保持为候选方案而非已验证的贡献。

## 输出预期

- `explore_outputs/CHANGESET.md`
- `explore_outputs/SCIENTIFIC_CHANGELOG.md`
- `explore_outputs/COMPARABILITY_REPORT.md`
- `explore_outputs/TOP_RUNS.md`
- `explore_outputs/status.json`

## 备注

使用 `references/explore-policy.md`、`../ai-research-reproduction/references/research-rigor-principles.md`、`scripts/plan_code_changes.py` 和 `scripts/write_outputs.py`。
