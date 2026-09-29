---
name: run-train
description: 用于深度学习研究仓库的严谨训练技能。当需要保守地运行文档化或选定的训练命令以进行启动验证、短程验证、全面启动或恢复时使用，并将命令、配置、种子、日志、检查点、状态和指标证据写入标准化的 `train_outputs/` 目录。不应用于环境设置、探索性扫描、推测性想法实现或端到端编排。
---

# run-train

将此用作 Rigor Train 技能。安装的 slug 保持为 `run-train` 以确保兼容性。

使用 `../ai-research-reproduction/references/agent-operating-principles.md` 中的共享操作原则；此技能应将训练证据保持受限，同时将特定于存储库的监控细节留给模型。

## 适用场景

- 当训练命令已选定且应谨慎执行时。
- 当研究人员需要启动验证、短程验证、完整训练启动或恢复处理时。
- 当运行需要结构化的训练状态、检查点和指标报告时。

## 不适用场景

- 当主要任务是环境设置或资产下载时。
- 当研究人员希望仅进行推理或仅进行评估的执行时。
- 当任务涉及推测性探索、多变量扫描或自主想法实现时。
- 当用户仍需存储库摄入或论文差距解决时。

## 明确边界

- 此技能执行选定的训练命令并规范化产生的证据。
- 它不会自行选择整体研究目标。
- 它不拥有探索性分支或推测性代码适配。
- 它应清晰记录部分、阻塞、恢复和启动状态。
- 当可用时，它应保留可复现性上下文，如配置、种子、检查点、日志、指标和运行时假设。

## 输入预期

- 选定的训练目标
- 可运行的训练命令
- 环境和资产假设
- 运行模式，如启动验证、短程验证、完整启动或恢复

## 输出预期

- `train_outputs/SUMMARY.md`
- `train_outputs/COMMANDS.md`
- `train_outputs/LOG.md`
- `train_outputs/SCIENTIFIC_CHANGELOG.md`
- `train_outputs/COMPARABILITY_REPORT.md`
- `train_outputs/status.json`

## 注意事项

使用 `references/training-policy.md`、`../ai-research-reproduction/references/deep-learning-experiment-principles.md`、`scripts/run_training.py` 和 `scripts/write_outputs.py`。
