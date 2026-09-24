# explore-run

将其用作 Rigor Improve / Rigor Explore 的运行叶子技能。已安装的 slug
仍为 `explore-run` 以确保兼容性。

参考
`../ai-research-reproduction/references/agent-operating-principles.md` 中的共享操作原则；本技能应指导候选运行规划，同时保留模型对当前仓库的判断。

## 何时适用

- 当研究者明确授权进行探索性运行时。
- 当任务为小子集验证、短周期训练探测、批处理扫描、闲置 GPU 搜索或快速迁移学习试验。
- 当输出应排序候选运行，而非认证可信的成功。

## 何时应不适用

- 当用户需要可信的训练执行或保守验证时。
- 当没有明确的探索性授权时。
- 当任务为仓库设置、录入或调试时。

## 明确边界

- 本技能仅负责探索性执行规划与总结。
- 当任务同时涉及当前研究协调与探索性代码变更时，应改用 `ai-research-explore`。
- 它可将实际命令执行移交至 `minimal-run-and-audit` 或 `run-train`。
- 它应将实验状态与可信基线隔离。
- 在更重的探索性运行之前，应优先采用小子集与短周期检查。
- 它应将运行结果标注为有界证据，并在比较不直接公正时进行说明。

## 排序语义

- 执行前的候选选择使用三个因素：`cost`、`success_rate` 和 `expected_gain`。
- 默认权重应保持保守，除非研究者明确提供 `selection_weights`。
- 通过 `max_variants` 和 `max_short_cycle_runs` 评分后，预算修剪仍适用。
- 如果运行稍后执行，下游排序应切换到真实执行证据，而非仅依赖纯启发式方法。

## 变体规格提示

- 使用 `variant_axes` 定义候选维度网格。
- 使用 `subset_sizes` 和 `short_run_steps` 表达探索性运行规模。
- 使用 `selection_weights` 重新平衡 `cost`、`success_rate` 和 `expected_gain`。
- 使用 `primary_metric` 和 `metric_goal`，以便下游排序能一致地排序已执行的候选。

## 输出预期

- `explore_outputs/CHANGESET.md`
- `explore_outputs/SCIENTIFIC_CHANGELOG.md`
- `explore_outputs/COMPARABILITY_REPORT.md`
- `explore_outputs/TOP_RUNS.md`
- `explore_outputs/status.json`

## 说明

参考 `references/execution-policy.md`、`../ai-research-reproduction/references/explore-variant-spec.md`、`../ai-research-reproduction/references/deep-learning-experiment-principles.md`、`scripts/plan_variants.py` 和 `scripts/write_outputs.py`。
