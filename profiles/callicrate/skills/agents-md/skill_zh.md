# 管理 AGENTS.md

`AGENTS.md` 为代码代理提供范围限定、当前、仓库特定的指令。它不是 README、运行手册、架构文档、变更日志、教程或证据日志。良好的指导应基于证据、简洁、限定于文件目录树，并具有行为性：它告诉代理在这个仓库中应该如何不同地操作。

## 使用时机

- 创建、更新、审查、拆分、移动或修复仓库的 `AGENTS.md`。
- 捕获经过验证的本地命令、仓库契约、路径所有权或重复出现的代理错误。
- 将仓库证据转换为未来代理可以遵循的规则。

## 不使用时机

- 独立技能、提示、全局指令、README、架构文档、变更日志或运行手册。
- 广泛的文档重写，其中 `AGENTS.md` 不是明确的交付成果。
- 不受当前仓库证据支持的理想化流程指导。

## 模式

- **patch**：小的文本修复、拼写错误、过时的路径或狭窄的规则变更。仅检查受影响的部分和证据。
- **create**：不存在合适的 `AGENTS.md`。运行分析器，采样源/配置/文档，然后起草最小的有用文件。
- **update**：现有文件需要新的或修正的指导。保留有效的规则，删除过时或重复的内容，并仅添加有证据支持的变化。
- **split/move**：范围边界正在变化。检查现有的根文件和嵌套文件，然后使用 [references/topology-and-handoff-guidance.md](references/topology-and-handoff-guidance.md)。
- **review**：除非被要求，否则不要编辑。按严重程度返回发现，附带证据和残余风险。
- **exhaustive**：单体仓库、契约密集型仓库、安全敏感的指导、操作交接、主要的拓扑变更或证据不明确。

## 工作流程

1. 选择模式和目标范围。阅读最近的现有 `AGENTS.md`、可能重叠的嵌套 `AGENTS.md` 文件，以及当可用时的 `git status --short`。
2. 对于 create、update、split/move 或 exhaustive 模式，运行 `python <skill-root>/scripts/analyze_project.py --repo-root <target-repo> --format json`。将其视为采样指南，而不是权威。
3. 对于常规编写细节，使用 [references/normal-authoring.md](references/normal-authoring.md)。仅检查您将要提出的声明所需的源。
4. 从 [references/template-selection.md](references/template-selection.md) 中的最小适用模板起草。除非仓库明显需要专门的模板，否则优先使用 [assets/agentsmd-minimal.md](assets/agentsmd-minimal.md)。
5. 将证据保存在工作笔记或最终摘要中。仅在仓库已经拥有一个或用户要求时才添加证据文件。
6. 使用 `python <skill-root>/scripts/validate_agentsmd.py --repo-root <target-repo> --agents-file <target-agents-file> --mode <quick|standard|exhaustive>` 和 `python <skill-root>/scripts/semantic_check_agentsmd.py --repo-root <target-repo> --agents-file <target-agents-file>` 进行验证。

## 规则质量评估标准

仅保留以下情况的规则：

- **specific**：命名实际路径、命令、契约或本地约定。
- **current**：由活动文件或用户提供的当前事实支持。
- **scoped**：适用于此 `AGENTS.md` 目录树。
- **behavioral**：改变代理应该做什么。
- **evidence-backed**：可追溯到检查的仓库证据。
- **safe**：避免秘密、未经授权的访问、破坏性命令和生产执行。
- **non-duplicative**：不重述全局指令、语言基础或 README 内容。
- **concise**：足够简短，可以在正常编码工作中扫描。

## 升级矩阵

仅在任务需要时加载额外参考：

| 触发器 | 阅读 |
|---------|------|
| 工具、CLI、MCP、API、生成文件、迁移、模式或公共契约指导 | [references/contract-bearing-agentsmd.md](references/contract-bearing-agentsmd.md) |
| 拆分、移动、嵌套范围、过时的拓扑或所有权交接 | [references/topology-and-handoff-guidance.md](references/topology-and-handoff-guidance.md) |
| 活动操作、降级工具、手动调度、停止状态或环境重置 | [references/degraded-tool-surface.md](references/degraded-tool-surface.md), [references/evidence-invalidation.md](references/evidence-invalidation.md) |
| 子代理或委托审查工作流 | [references/subagent-coordination-patterns.md](references/subagent-coordination-patterns.md) |
| Python、TypeScript、其他栈、Databricks/Spark 或 ML特定证据提示 | [references/language-specific/python-guidance.md](references/language-specific/python-guidance.md), [references/language-specific/typescript-guidance.md](references/language-specific/typescript-guidance.md), [references/language-specific/other-stack-guidance.md](references/language-specific/other-stack-guidance.md), [references/domain-specific/databricks-spark.md](references/domain-specific/databricks-spark.md), [references/domain-specific/ml-projects.md](references/domain-specific/ml-projects.md) |
| 仅审查或判断密集型审计 | [references/manual-audit.md](references/manual-audit.md) |

## 最终响应

对于编辑模式，包括更改的文件、添加/更改/删除的规则、采样的证据来源、验证命令和结果，以及残余风险。

对于审查模式，首先按严重程度列出发现。每个发现需要受影响的 `AGENTS.md` 部分或行、支持仓库证据、为什么重要以及建议的修复。然后列出开放问题、测试/验证差距，并在发现之后提供简要总结。

## 确定性工具

| 工具 | 使用 |
|------|-----|
| [scripts/analyze_project.py](scripts/analyze_project.py) | 栈、配置、测试、路径和建议清单 |
| [scripts/validate_agentsmd.py](scripts/validate_agentsmd.py) | 结构验证 |
| [scripts/semantic_check_agentsmd.py](scripts/semantic_check_agentsmd.py) | 路径、命令、链接和示例验证 |
| [scripts/check_agentsmd_templates.py](scripts/check_agentsmd_templates.py) | 技能模板和指导卫生 |
| [scripts/run_agentsmd_fixture_checks.py](scripts/run_agentsmd_fixture_checks.py) | 已知固定行为，用于验证器变更 |

## 参考

- [references/tool-contracts.md](references/tool-contracts.md) 和 [references/template-selection.md](references/template-selection.md) - 辅助 CLI 契约、模式和模板
- [assets/agentsmd-minimal.md](assets/agentsmd-minimal.md), [assets/agentsmd-contract-bearing.md](assets/agentsmd-contract-bearing.md), [assets/agentsmd-operational.md](assets/agentsmd-operational.md), [assets/agentsmd-full.md](assets/agentsmd-full.md) - 启动模板
- [assets/example-validated-agentsmd.md](assets/example-validated-agentsmd.md), [assets/example-contract-bearing-agentsmd.md](assets/example-contract-bearing-agentsmd.md), [assets/example-operational-agentsmd.md](assets/example-operational-agentsmd.md), [assets/writing-tips.md](assets/writing-tips.md) - 紧凑示例
