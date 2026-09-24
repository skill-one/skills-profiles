# ai-research-reproduction

## 目的

以 README 优先的深度学习复现，引导完成最小化、可信的可靠运行，并提供可审计的证据。复现不是"通过修改任何内容来让它运行起来"；应忠实阅读 README、环境、权重、数据集和已记录命令，然后记录结果和偏差。从 `references/agent-operating-principles.md` 开始；当科学含义或实验细节存在风险时，加载 `references/research-rigor-principles.md` 和 `references/deep-learning-experiment-principles.md`。

对于首次使用的相关问题，使用指定的 Python 运行 `scripts/doctor.py`（只读；可选 `--repo` 和 `--require-module`）。确定性入口为 `scripts/orchestrate_repro.py`，内置自包含的 `_bundled/` 运行时，因此该技能在安装后即可单独使用；单独安装的配套技能作为可选的复用入口。使用入口点和 `--help` 进行常规运行；当遇到具体阻碍或安全问题需要时，检查其实现。

执行的命令会持久化生命周期状态、追加式事件，以及完整的流式 stdout/stderr，保存在 `repro_outputs/_runtime/<run_id>/` 下。在活动运行目录中的 `CANCEL` 文件会请求进程树的取消。

为恢复，如果涉及队列或模型门控，读取 `references/runtime-and-model-adapter.md`；对于可选的模型/工具循环，读取 `references/agent-runner.md` 并使用 `scripts/run_agent.py`。

## 适用场景

当以下条件同时满足时使用本技能：

- 目标是包含 README、脚本、配置或已记录命令的 AI 代码仓库。
- 请求涵盖从接收、设置、执行、训练验证、分析、论文差距解决到报告等多个可信阶段。
- 期望结果为小型可复现的目标，而非广泛的实验。

不使用本技能处理论文摘要、通用环境设置、隔离仓库扫描、独立命令执行、开放式研究设计，或仅针对候选方案明确的探索。

## 可信目标选择

选择能够诚实展示基于仓库的复现的最小目标：

1. 已记录的推理
2. 已记录的评估
3. 已记录的训练启动或部分验证
4. 仅在明确获得用户确认后进行完整训练

将 README 指导作为主要复现意图。使用仓库文件澄清 README，而非静默替换它。当 README 与论文冲突时，记录冲突，仅使用 `paper-context-resolver` 用于狭窄的、与复现相关的差距。

## 工作流

1. 阅读 README 和仓库附近的相关信号。
2. 运行捆绑的 `repo-intake-and-plan` 阶段，提取命令和目标。
3. 选择并论证最小的可信目标。
4. 仅针对目标特定的环境、检查点、数据集和缓存假设运行 `env-and-assets-bootstrap`。
5. 仅在结构、插入点或可疑实现模式需要只读澄清时，运行 `analyze-project`。
6. 使用 `minimal-run-and-audit` 执行已记录的推理、评估、冒烟或完整性检查。保持直接执行为默认；原生 shell 语法需明确审查和授权。
7. 当所选可信目标为训练启动、短时验证、完整启动或恢复时，使用 `run-train`。
8. 在完整训练声明或任何可能改变数据集、划分、检查点、预处理、指标、损失、模型语义或结果解释的修改之前，暂停供人类审查。
9. 仅在已记录的容差条件下比较明确预期的指标时，授予 `result-match`；仅观察到的指标仅证明执行，而非复现。然后在实际可行时，以用户的语言编写标准输出和简洁的最终说明。
10. 一旦请求的目标和证据检查完成，返回有界结果并停止。可选阶段和进一步的 README 命令不是自动的后续工作。

## 补丁边界

优先不进行仓库修改。如果需要修改，保持修改保守且可审计：

- 优先使用命令行参数、环境变量、路径修复、依赖版本修复或依赖文件修复，而非代码更改。
- 必要时允许进行复现修复，但必须不隐瞒。说明变更内容、必要原因、是否改变科学含义、是否影响与论文、README 或基线的可比性。
- 避免更改模型架构、核心推理语义、训练逻辑、损失函数或实验含义。
- 如果必须修改仓库文件，创建名为 `repro/YYYY-MM-DD-short-task` 的分支，保持已验证的补丁提交精简，并在 `PATCHES.md` 中记录 README 保真度影响。

参见 `references/patch-policy.md`。

## 输出

始终面向 `repro_outputs/`：
```
SUMMARY.md
COMMANDS.md
LOG.md
SCIENTIFIC_CHANGELOG.md
COMPARABILITY_REPORT.md
status.json
ANNOTATED_README.md   # 原始 README + 按章节设置的着色代理 agent 动作标注
PATCHES.md   # 仅在应用了补丁时
```

使用 `assets/` 下的模板和 `references/output-spec.md` 中的字段规则。

- 在 `SUMMARY.md` 中放置最短且高价值的摘要。
- 在 `COMMANDS.md` 中放置可复制的命令。
- 在 `LOG.md` 中放置过程证据、假设、失败和决策。
- 在 `SCIENTIFIC_CHANGELOG.md` 中放置科学含义和变更影响。
- 在 `COMPARABILITY_REPORT.md` 中放置比较锚点和协议偏差。
- 在 `status.json` 中放置持久化机器可读状态。
- 在需要时，在 `PATCHES.md` 中放置分支、提交、验证和 README 保真度影响。
- 在 `ANNOTATED_README.md` 中放置研究人员的一目了然视角：按字节逐字回放原始 README——包括其图片、GIF、视频和 HTML 标记——在每一标题块之后恰好标记一次颜色标注。绝不提取纯文本替代方案。生成必须经过内置的去除/检查往返测试，文件方可保存。
- 对于原始相对媒体/文件上下文，使用 `--source-adjacent-readme` 在源 README 旁边同时写入 `RIGORPILOT_README.md`；检查报告的路径/状态，且绝不替换不相关的现有文件。参见 `references/output-spec.md`。
- 区分已验证事实与推断猜测。

## 引用加载

- 编写人类可读输出时加载 `references/language-policy.md`。
- 在做出可比性、贡献或研究结果声明之前，加载 `references/research-rigor-principles.md`。
- 当数据集、划分、指标、检查点、训练或评估细节相关时，加载 `references/deep-learning-experiment-principles.md`。
- 如果存在 `~/.rigorpilot/PERSONAL_RIGOR.md`，在 `references/continuous-learning-policy.md` 下加载（仅建议性；核心原则优先）。
- 失败及后续已解决的运行通过 `shared/scripts/lessons_store.py` 自动记录为经验教训（`RIGORPILOT_LESSONS=0` 禁用）。
- 在涉及协议敏感决策之前，加载 `references/research-safety-principles.md`。
- 在修改仓库文件之前，加载 `references/patch-policy.md`。
- 将专门逻辑保留在子技能、脚本、模板或引用中，而非扩展此入口点。
