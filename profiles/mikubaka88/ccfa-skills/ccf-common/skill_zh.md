# CCF通用

## 家族文件合约

在编写前，确定每个任务/成果的规范输出和一个稳定的作业目录。重用明确的或已建立的作业路径；否则使用项目根目录 `ccfa-workfiles/<用途>/<成果ID>/`，仅在需要时使用 `source/`、`assets/`、`cache/` 和 `build/`。就地更新当前文件；不要分散中间文件或创建迭代副本。保留输入和所需证据；仅清理由此任务创建的已验证的可丢弃文件。使用UTF-8文本I/O，并在保存或渲染后检查中文文本。对于文件工作，应用 [artifact-contracts.md](references/artifact-contracts.md) 并在技能转换时重用相同的路径。

## 协作合约

在应用这些共享控制之前，除非其基线已激活，否则激活 [ccf-humanization](../ccf-humanization/SKILL.md)。应用此条目一次，然后继续专家工作；不要递归地重新进入任何预检。跨贡献者重用适用的规则。

保留一个集成负责人，并积极使用其他技能来解决缺失的先决条件或检查材料发现。重用适用的证据；不要跳过必要的准备工作以节省代币。在最终确定之前，集成贡献并验证受影响的结果。遵循条件 [合作路线](references/routing.md)；避免不相关的阶段和重复报告。

## 核心规则

这是在每次CCFA专家之前、在 `ccf-humanization` 之后激活的共享控制模块。它设置任务的范围、集成负责人、相关先决条件、证据边界和文件路径，而专家技能生成研究交付成果。应用这些控制不会运行维护工作流或需要治理报告。

## 调用控制

**CCFA交接模式：部分（推荐）。** 遵循 `metadata.ccf_skill_controls.handoff_question_mode` 和 `references/handoff-modes.md`。在直接调用时，确保Humanization的基线已被读取后再应用这些控制。不要递归地重新启动任何预检。跨贡献者重用适用的规则，并仅读取当前决策所需的共享参考。

## 家族预检

确定请求的结果、范围/权限、集成负责人以及缺失的或可重用的先决条件。使用 `references/routing.md` 进行协作，使用 `references/handoff-modes.md` 进行转换。在处理源或私有材料时应用证据/隐私规则，在文件工作前应用成果规则，在评估时应用审查标准。重用加载的规则和已知路径；不要仅仅为了激活此技能而创建摄入表或状态文件。一旦适用的控制建立，继续专家任务。将维护工作流保留在下方，以供实际的家族维护请求使用。

## 共享控制

仅加载当前预检决策或维护任务所需的参考：

- `references/routing.md`：用于确定哪个CCFA技能拥有请求，并避免触发重叠。
- `references/task-modes.md`：用于探索性/快速/标准深度、授权感知的继续、选择性上下文、主机支持的并行工作，以及GPT-6适应。
- `references/review-output-standards.md`：用于保持数值评分、多评审员小组、评分变更条件以及可见输出质量的一致性。
- `references/handoff-modes.md`：用于解释 `metadata.ccf_skill_controls.handoff_question_mode`。
- `references/privacy-and-evidence.md`：在处理手稿、评审、反驳、私有草稿、文献搜索或证据主张时使用。
- `references/source-registry.yaml`：用作共享源清单，用于场地规则、评审方法、示例记录和研究工作流参考。
- `references/ccf-a-venue-map.md`：当非写作技能需要场地-家族映射而不依赖于 `ccf-paper-writer` 时使用。
- `references/skill-trigger-registry.yaml`：用作规范触发器注册表；比较描述和代理提示与相同的所有权边界。
- `references/artifact-contracts.md`：每当技能创建或修订文件时使用；它定义所有权、规范路径、最小中间文件生成、就地覆盖默认值、任务范围清理和所需保留历史记录。
- `references/ccfa-yaml-contract.md`：用于共享 `ccfa.yaml` 项目状态模式。

## 维护工作流

1. 在默认值之前遵循当前用户范围和现有授权；对于无新文件维护，仅编辑现有表面。当编辑任何CCFA家族技能时，保留 `metadata.ccf_skill_controls` 块，并保持其键与 `references/handoff-modes.md` 对齐。
2. 在添加新的触发语言之前使用 `references/routing.md`，以防止所有权重叠。
3. 在更改清单严格性、快速抛光、标准评审或输出合约之前使用 `references/task-modes.md`。
4. 在更改评分卡、评审员小组、评分风险语言或最终输出自检规则之前使用 `references/review-output-standards.md`。
5. 在添加任何浏览、引用、新颖性、评分、实验结果、压缩或反驳指令之前使用 `references/privacy-and-evidence.md`。
6. 在更改生成的文件名、修订行为、报告文件夹、缓存、尝试存档或账本之前使用 `references/artifact-contracts.md`。默认为每个交付成果一个规范成果，每个任务/成果一个稳定的工作目录，并在交付前清理任务创建的可丢弃文件。保留所需证据和其他任务的文件。
7. 永不提交个人绝对路径、用户名、展开的 home 目录、私有本地技能根或机器特定命令示例。使用 `$CODEX_HOME`、`$HOME`、仓库相对路径或非识别占位符。
8. 将新的公共源放入 `references/source-registry.yaml`；不要在兄弟 `source-notes.md` 文件中重复长URL列表。本地参考必须使用仓库相对或非识别的 `local:`/`repo:` 标识符，而不是机器路径。
9. 在源注册表编辑后运行 `scripts/check_sources.py`。该脚本仅报告问题，绝不能重写注册表文件。
10. 运行 `scripts/check_v04.py` 进行家族元数据、注册表、脚本语法、引用资源以及回归检查；然后运行 `scripts/check_path_privacy.py` 在最终确定触及文档、示例、源记录、脚本、图表或发布文件的CCFA家族更改之前。

## 输出合约

对于普通预检，无需单独报告即可将控制权交还给专家。在审计或更新CCFA技能时，报告：

```text
路由影响：
交接模式影响：
私有材料安全：
源注册表变更：
评分风险语言变更：
验证结果：
```
