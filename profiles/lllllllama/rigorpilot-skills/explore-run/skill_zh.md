# explore-run

将此用作 Rigor Improve / Rigor Explore 运行子技能。安装的 slug 保持为 `explore-run` 以确保兼容性。

使用 `../ai-research-reproduction/references/agent-operating-principles.md` 中的共享操作原则；此技能应指导候选运行规划，同时保留对活动仓库的模型判断。

## 何时应用

- 当研究人员明确授权探索性运行时。
- 当任务是小子集验证、短周期训练探测、批量扫描、空闲 GPU 搜索或快速迁移学习试验时。
- 当输出应按候选运行排序而不是认证可信成功时。

## 何时不应用

- 当用户希望可信训练执行或保守验证时。
- 当没有明确的探索性授权时。
- 当任务是仓库设置、摄入或调试时。

## 清晰边界

- 此技能仅拥有探索性执行规划和总结。
- 当任务跨越当前_research 协调和探索性代码更改时，请使用 `ai-research-explore`。
- 它可以将实际命令执行移交给 `minimal-run-and-audit` 或 `run-train`。
- 它应将实验状态与可信基线隔离。
- 它应在更重的探索性运行之前优先进行小子集和短周期检查。
- 它应将运行结果标记为有界证据，并解释何时比较不直接公平。

## 排序语义

- 预执行候选选择使用三个因素：`cost`、`success_rate` 和 `expected_gain`。
- 默认权重应保持保守，除非研究人员明确提供 `selection_weights`。
- 预算修剪在通过 `max_variants` 和 `max_short_cycle_runs` 评分后仍然适用。
- 如果运行稍后执行，下游排序应切换到实际执行证据，而不是保持纯粹启发式。

## 变体规范提示

- 使用 `variant_axes` 定义候选维度网格。
- 使用 `subset_sizes` 和 `short_run_steps` 表达探索性运行规模。
- 使用 `selection_weights` 重新平衡 `cost`、`success_rate` 和 `expected_gain`。
- 使用 `primary_metric` 和 `metric_goal` 以便下游排序可以一致地排序已执行的候选。

## 输出预期

- `explore_outputs/CHANGESET.md`
- `explore_outputs/SCIENTIFIC_CHANGELOG.md`
- `explore_outputs/COMPARABILITY_REPORT.md`
- `explore_outputs/TOP_RUNS.md`
- `explore_outputs/status.json`

## 注意事项

使用 `references/execution-policy.md`、`../ai-research-reproduction/references/explore-variant-spec.md`、`../ai-research-reproduction/references/deep-learning-experiment-principles.md`、`scripts/plan_variants.py` 和 `scripts/write_outputs.py`。
