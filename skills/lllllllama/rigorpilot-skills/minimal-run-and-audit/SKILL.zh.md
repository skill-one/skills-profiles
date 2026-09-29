---
name: minimal-run-and-audit
description: 用于README优先的深度学习仓库复现的Rigor Run技能。当任务明确要求捕获或规范化从选定的冒烟测试或已记录的推理或评估命令中获取的证据，并编写标准化的`repro_outputs/`文件时使用，包括当仓库文件发生变化时的版本更新说明。不应用于训练执行、初始仓库采集、通用环境设置、论文查找、目标选择、隐藏的科学意义变更，或单独的端到端编排。
---

# minimal-run-and-audit

将此用作严谨运行技能。安装的slug保持为`minimal-run-and-audit`以保持兼容性。

使用`../ai-research-reproduction/references/agent-operating-principles.md`中的共享操作原则；该技能应使运行证据可审计，而无需将每个命令都转换为僵化的协议。

## 何时应用

- 在存在复现目标和设置计划之后。
- 当主要技能需要执行证据和标准化输出时。
- 当适用冒烟测试、已记录的推理运行、已记录的评估运行或其他短时非训练验证时。
- 当用户已经知道应尝试的命令，并且只需要执行和报告时。

## 何时不应用

- 在初始仓库扫描期间。
- 当环境或资产仍足够不确定，以至于执行变得毫无意义时。
- 当任务是一项文献查找，而不是仓库执行时。
- 当用户仍在决定哪个复现目标应计为主要运行时。

## 清晰的边界

- 此技能拥有尝试命令的标准化报告。
- 它可能从主要技能或一个薄的辅助技能接收执行证据。
- 它不会自行选择整体目标。
- 它不会执行广泛的论文分析。
- 它不拥有训练启动、恢复或长时间运行训练状态。
- 它不应将风险代码修改标准化为可接受的实践。
- 它必须不隐藏改变评估、预处理、检查点、指标或其他科学意义的变更。

## 输入预期

- 选择的复现目标
- 可运行的命令或冒烟命令
- 环境和资产假设
- 可选的补丁元数据

## 输出预期

- 执行结果摘要
- 标准化的`repro_outputs/`文件
- `SCIENTIFIC_CHANGELOG.md`用于改变的科学研究意义和证据状态
- `COMPARABILITY_REPORT.md`用于README/论文/基线可比性
- 明确区分已验证、部分和阻塞状态
- 当仓库文件变更时，`PATCHES.md`

## 注意事项

使用`references/reporting-policy.md`、`../ai-research-reproduction/references/research-rigor-principles.md`、`scripts/run_command.py`和`scripts/write_outputs.py`。
