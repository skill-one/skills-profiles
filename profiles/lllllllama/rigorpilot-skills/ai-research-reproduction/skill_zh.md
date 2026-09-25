# ai-research-reproduction

## 目的

指导以README为主的深度学习复现，以最小的可信运行和可审计证据为目标。保留文档中的含义；记录假设、偏差和障碍，而不是改变语义来制造成功。仅在具体不确定性存在时加载专业参考。

## 快速路径

对于常规的有限运行，保持控制路径简短：

1. 读取目标README，并仅读取理解文档命令所需的测试/配置/源文件。
2. 使用 `scripts/orchestrate_repro.py --repo <repo> --plan-only --agent-output` 运行，并已提供任何明确用户超时限制（`--timeout` 或 `--train-timeout`）；检查 `command_candidates`、选定的 `cmd-XX`、副作用契约、选择指纹和返回的 `reviewed_run_args`。如果没有 `--output-dir`，后续证据将发送到 `<repo>/repro_outputs`，无论调用者的当前工作目录如何。
3. 使用 `--run-selected --command-id <cmd-XX> --plan-fingerprint <fingerprint> --agent-output` 加上请求的超时/指标/源相邻选项运行选定的候选者或另一个已审查的候选者。保留明确的用户命令超时限制，而不是在常规可信运行中默默地使其更严格。`--timeout` 限制目标命令；**不要**将整个编排器包装在相等或更短的外部超时中，因为它仍然需要时间终止子进程和写入终端证据。命令集更改会导致失败；设置/下载命令永远不会是目标候选者。
4. 运行 `--verify-output --agent-output`；仅在验证失败或结果为部分/阻塞时才检查详细证据文件。
5. 提供有限的结果并停止。

对于具有短工具调用截止时间的宿主机，使用 `--include-agent-handoff` 重新运行规划并遵循 `references/agent-job.md`；否则保持上述直接路径。作业完成不是任务接受，不确定状态永远不会是自动重播的理由。

在正常成功路径上**不要**检查 `orchestrate_repro.py`、`annotate_readme.py`、`_bundled/`、写入器或运行时内部。仅在存在具体障碍、意外副作用、捆绑完整性失败或未解决的安全问题时才检查实现。使用 `scripts/doctor.py` 进行首次使用的环境/安装诊断。执行的命令在 `repro_outputs/_runtime/<run_id>/` 下保留完整生命周期/日志证据。

## 适用范围

用于以仓库为基础的多阶段可信复现，目标是可复现的小目标。不要用于论文摘要、通用设置、独立扫描、独立命令、开放式研究设计或明确授权的候选者探索。

## 可信目标选择

选择可以诚实展示基于仓库复现的最小目标：

1. 文档中的推理
2. 文档中的评估
3. 文档中的训练启动或部分验证
4. 经明确用户确认后的完整训练

将README指导视为主要复现意图。使用仓库文件来澄清README，而不是默默地替换它。当README和论文冲突时，记录冲突，并仅使用 `paper-context-resolver` 来填补狭窄的复现关键差距。

## 工作流程

1. 将README指导视为主要；提取并选择最小可信目标。
2. 仅在需要结构澄清时使用设置/资产，仅用于目标特定先决条件。
3. 使用 `minimal-run-and-audit` 进行推理/评估/冒烟测试，使用 `run-train` 进行训练启动、启动或恢复；直接执行是默认值。
4. 在进行更完整的训练或更改数据集、分割、检查点、预处理、指标、损失、模型语义或解释之前暂停。
5. 仅针对明确预期指标和容差授予 `result-match`；单独处理成功不是复现成功。
6. 编写证据捆绑包，返回请求的有限结果并停止；可选阶段不是自动后续工作。

## 补丁边界

优先不进行仓库编辑。如果需要编辑，请保持它们保守且可审计：

- 在代码更改之前尝试命令行参数、环境变量、路径修复、依赖版本修复或依赖文件修复。
- 当需要时允许复现修复，但它们必须不隐藏。说明更改了什么、为什么需要、是否改变科学含义、是否影响与论文、README或基线的可比性。
- 避免更改模型架构、核心推理语义、训练逻辑、损失函数或实验含义。
- 如果必须更改仓库文件，请创建名为 `repro/YYYY-MM-DD-short-task` 的分支，保持已验证补丁提交稀疏，并在 `PATCHES.md` 中记录README保真度影响。

参见 `references/patch-policy.md`。

## 输出

始终目标 `repro_outputs/`：
```text
SUMMARY.md
COMMANDS.md
LOG.md
SCIENTIFIC_CHANGELOG.md
COMPARABILITY_REPORT.md
status.json
ANNOTATED_README.md   # 原始README + 带有彩色按节代理操作注释
PATCHES.md   # 仅如果已应用补丁
```

使用 `assets/` 下和 `references/output-spec.md` 中的模板。保持摘要简短、命令可复制、机器状态稳定、科学/可比性更改明确。`ANNOTATED_README.md` 必须在插入证据块外保留源README的字节对字节，并通过其剥离/检查轮次。仅对于拥有的 `RIGORPILOT_README.md` 使用 `--source-adjacent-readme`；永远不会替换无关文件。区分已验证的事实和推理。

## 参考加载

- 工作流判断：`references/agent-operating-principles.md`。
- 人类可读输出：`references/language-policy.md`。
- 科学/可比性判断：`references/research-rigor-principles.md` 和，当实验细节重要时，`references/deep-learning-experiment-principles.md`。
- 协议敏感更改：`references/research-safety-principles.md` 和 `references/patch-policy.md`。
- 个人严谨性和经验教训仅供参考；将专业细节保留在参考/脚本中，而不是扩展此入口点。
