# minimal-run-and-audit

使用此作为 Rigor Run 技能。已安装的 slug 保持
`minimal-run-and-audit` 以确保兼容性。

使用 `../ai-research-reproduction/references/agent-operating-principles.md` 中的共享操作原则；本技能应使运行证据可审计，而不将每条命令转化为严格的协议。

## 何时应用

- 存在复现目标和设置计划之后。
- 主技能需要执行证据和规范化输出时。
- 当进行冒烟测试、已记录的推理运行、已记录的评估运行或其他短时非训练验证时是合适的。
- 当用户已经知道应尝试的命令，且仅需要执行和报告时。

## 何时不应用

- 在初始仓库扫描期间。
- 当环境或资源仍定义不足，以致执行无意义时。
- 当任务是文献查询而非仓库执行时。
- 当用户仍在决定哪个复现目标应作为主运行时。

## 明确边界

- 本技能负责对已尝试命令的规范化报告。
- 它可能从主技能或薄辅助工具接收执行证据。
- 它不自行选择总体目标。
- 它不进行广泛的论文分析。
- 它不拥有训练启动、恢复或长时间运行的训练状态。
- 它不应将风险代码修改规范化为可接受实践。
- 它不得隐瞒会改变评估、预处理、检查点、
  指标或其他科学含义的修改。

## 输入期望

- 选定的复现目标
- 可运行的命令或冒烟命令
- 环境与资源假设
- 可选的补丁元数据

## 输出期望

- 执行结果摘要
- 标准化的 `repro_outputs/` 文件
- 用于改变科学含义与证据状态的 `SCIENTIFIC_CHANGELOG.md`
- 用于 README/论文/基线可比性的 `COMPARABILITY_REPORT.md`
- 清晰区分已验证、部分和受阻状态
- 当仓库文件被更改时，提供 `PATCHES.md`

## 说明

使用 `references/reporting-policy.md`、`../ai-research-reproduction/references/research-rigor-principles.md`、`scripts/run_command.py` 和 `scripts/write_outputs.py`。
