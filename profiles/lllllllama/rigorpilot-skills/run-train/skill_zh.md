# run-train

将此作为 Rigor Train 技能使用。为保持兼容性，已安装的 slug 仍为 `run-train`。

使用 `../ai-research-reproduction/references/agent-operating-principles.md` 中的共享操作原则；本技能应将训练证据控制在合理范围内，并将仓库特定的监控细节留给模型。

## 何时适用

- 当训练命令已选定且应保守执行时。
- 当研究人员需要启动验证、短时验证、完整训练启动或恢复处理时。
- 当该运行需要结构化的训练状态、检查点与指标上报时。

## 不适用场景

- 当主要任务是环境配置或资源下载时。
- 当研究人员需要仅推理执行或仅评估执行时。
- 当任务是推测性探索、多变量扫描或自主想法实现时。
- 当用户仍需要仓库导入或论文缺口解决时。

## 明确边界

- 本技能执行已选择的训练命令，并对结果证据进行规范化处理。
- 它不能自行确定总体研究目标。
- 它不负责探索性分支或推测性代码适配。
- 应清晰记录部分执行、被阻塞、恢复以及已启动状态。
- 在可用时，应保留可复现性上下文，如配置文件、种子、检查点、日志、指标和运行假设。

## 输入预期

- 已选择的训练目标
- 可运行的训练命令
- 环境与资源假设
- 运行模式，例如启动验证、短时验证、完整启动或恢复

## 输出预期

- `train_outputs/SUMMARY.md`
- `train_outputs/COMMANDS.md`
- `train_outputs/LOG.md`
- `train_outputs/SCIENTIFIC_CHANGELOG.md`
- `train_outputs/COMPARABILITY_REPORT.md`
- `train_outputs/status.json`

## 备注

使用 `references/training-policy.md`、`../ai-research-reproduction/references/deep-learning-experiment-principles.md`、`scripts/run_training.py` 以及 `scripts/write_outputs.py`。
