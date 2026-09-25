# ai-research-reproduction

## 目的

指导以README为主的深度学习复现，朝着最小可信运行进行，并提供可审计的证据。复现不是“通过改变任何东西让它运行”；忠实阅读README、环境、权重、数据集和记录的命令，然后记录结果和偏差。从`references/agent-operating-principles.md`开始；当科学意义或实验细节至关重要时，加载`references/research-rigor-principles.md`和`references/deep-learning-experiment-principles.md`。

对于首次使用的问题，使用目标Python运行`scripts/doctor.py`（只读；可选`--repo`和`--require-module`）。确定性入口点是带有自包含`_bundled/`运行时的`scripts/orchestrate_repro.py`，因此当单独安装时此技能有效；单独安装的辅助技能仍然是可选的可重用入口点。使用入口点和`--help`进行常规运行；当具体障碍或安全问题需要时，检查其实现。执行的命令持久化生命周期状态、仅追加事件，以及完整的流式stdout/stderr在`repro_outputs/_runtime/<run_id>/`下。在活动运行目录中创建`CANCEL`文件请求进程树取消。对于恢复，请阅读`references/runtime-and-model-adapter.md`中的队列或模型门；对于可选的模型/工具循环，请阅读`references/agent-runner.md`并使用`scripts/run_agent.py`。

## 适用范围

当所有条件都满足时，使用此技能：

- 目标是一个带有README、脚本、配置或记录命令的AI代码库。
- 请求涵盖多个可信阶段，如摄入、设置、执行、训练验证、分析、论文差距解决和报告。
- 期望的结果是一个小的可复现目标，而不是广泛的实验。

不要使用此技能进行论文摘要、通用环境设置、隔离仓库扫描、独立命令执行、开放式研究设计或明确的候选者仅探索。

## 可信目标选择

选择能够诚实展示基于仓库复现的最小目标：

1. 记录的推理
2. 记录的评估
3. 记录的训练启动或部分验证
4. 经明确用户确认后的完整训练

将README指导视为主要复现意图。使用仓库文件来澄清README，而不是无声地替换它。当README和论文冲突时，记录冲突，并仅使用`paper-context-resolver`来解决狭窄的复现关键差距。

## 工作流程

1. 阅读README和附近的仓库信号。
2. 运行捆绑的`repo-intake-and-plan`阶段以提取命令和目标。
3. 选择并说明最小可信目标。
4. 仅针对目标特定环境、检查点、数据集和缓存假设运行`env-and-assets-bootstrap`。
5. 仅当结构、插入点或可疑实现模式需要只读澄清时，运行`analyze-project`。
6. 使用`minimal-run-and-audit`进行记录的推理、评估、冒烟或健全性执行。保持直接执行为默认值；需要明确审查和授权的原生shell语法。
7. 当选定的可信目标是训练启动、短跑验证、完整启动或恢复时，使用`run-train`。
8. 在更完整的训练声明或任何可能改变数据集、分割、检查点、预处理、指标、损失、模型语义或结果解释的更改之前暂停人工审查。
9. 仅在记录的容差下比较明确预期指标时，才授予`result-match`；观察到的指标仅证明执行，不证明复现。然后在实际情况下，编写标准化的输出和简短的最终笔记（使用用户语言）。
10. 一旦请求的目标和证据检查完成，返回有界结果并停止。可选阶段和进一步的README命令不是自动后续工作。

## 补丁边界

优先不修改仓库。如果需要修改，请保持它们保守且可审计：

- 在代码更改之前，尝试命令行参数、环境变量、路径修复、依赖版本修复或依赖文件修复。
- 当需要时，允许复现修复，但它们必须不隐藏。说明更改了什么、为什么需要、是否改变科学意义、是否影响与论文、README或基线的可比性。
- 避免更改模型架构、核心推理语义、训练逻辑、损失函数或实验意义。
- 如果必须更改仓库文件，请创建名为`repro/YYYY-MM-DD-short-task`的分支，保持验证的补丁提交稀疏，并在`PATCHES.md`中记录README忠实度影响。

参见`references/patch-policy.md`。

## 输出

始终目标`repro_outputs/`：
```text
SUMMARY.md
COMMANDS.md
LOG.md
SCIENTIFIC_CHANGELOG.md
COMPARABILITY_REPORT.md
status.json
ANNOTATED_README.md   # 原始README + 带有按节agent-action注释的彩色
PATCHES.md   # 仅如果应用了补丁
```

使用`assets/`下的模板和`references/output-spec.md`中的字段规则。

- 将最短的摘要放在`SUMMARY.md`中。
- 将可复制的命令放在`COMMANDS.md`中。
- 将过程证据、假设、失败和决策放在`LOG.md`中。
- 将科学意义和变化影响放在`SCIENTIFIC_CHANGELOG.md`中。
- 将比较锚点和协议偏差放在`COMPARABILITY_REPORT.md`中。
- 将持久的机器可读状态放在`status.json`中。
- 在需要时，将分支、提交、验证和README忠实度影响放在`PATCHES.md`中。
- 将研究者的概览视图放在`ANNOTATED_README.md`中：重新播放README的字节级——包括其图像、GIF、视频和HTML标记——在每个标题块后精确地标记一个彩色注释。永远不要提取纯文本替代品。生成必须在文件保留之前通过内置的strip/check往返行程。
- 对于原始相对媒体/文件上下文，使用`--source-adjacent-readme`来在源README旁边写入`RIGORPILOT_README.md`；检查报告的路径/状态，永远不要替换不相关的现有文件。参见`references/output-spec.md`。
- 将已验证的事实与推断的猜测区分开来。

## 参考加载

- 写人类可读输出时，加载`references/language-policy.md`。
- 在做出可比性、贡献或研究结果声明之前，加载`references/research-rigor-principles.md`。
- 当数据集、分割、指标、检查点、训练或评估细节重要时，加载`references/deep-learning-experiment-principles.md`。
- 如果存在，在`references/continuous-learning-policy.md`下咨询`~/.rigorpilot/PERSONAL_RIGOR.md`（仅供参考；核心优先）。
- 失败和后续解决的运行通过`shared/scripts/lessons_store.py`自动记录为教训（`RIGORPILOT_LESSONS=0`禁用）。
- 在协议敏感决策之前，加载`references/research-safety-principles.md`。
- 在修改仓库文件之前，加载`references/patch-policy.md`。
- 将专业逻辑保留在子技能、脚本、模板或参考中，而不是扩展此入口点。
