# CCF 文献监控

## 家庭文件合同

在编写前，确定每个任务/成果的规范输出和一个稳定的作业目录。重用明确的或已建立的作业路径；否则使用项目根目录 `ccfa-workfiles/<用途>/<成果ID>/`，仅在需要时使用 `source/`、`assets/`、`cache/` 和 `build/`。就地更新当前文件；不要分散中间文件或创建迭代副本。保留输入和所需证据；仅清理由该任务创建的已验证的可丢弃文件。使用 UTF-8 文本 I/O，并在保存或渲染后检查中文文本。对于文件工作，应用 [artifact-contracts.md](../ccf-common/references/artifact-contracts.md) 并在技能转换时重用相同的路径。

## 协作合同

在专家执行前，首先阅读并应用 [ccf-humanization](../ccf-humanization/SKILL.md)，然后应用 [ccf-common](../ccf-common/SKILL.md)。在每个交接时，重用适用的活跃规则或刷新缺失/更改的规则。即使没有文本，这两个预检也是必需的；详细的编辑、实验和维护模式仅在相关时运行。

保留一个集成的负责人，并积极使用其他技能来解决缺失的先决条件或检查材料发现。重用适用的证据；不要跳过必要的准备工作以节省代币。在最终确定前，集成贡献并验证受影响的成果。遵循条件性 [合作路线](../ccf-common/references/routing.md)；避免无关的阶段和重复报告。

## 核心规则

监控 arXiv、OpenReview、会议/论文集信息流、项目页面、实验室和指定竞争对手，以发现可能与其用户想法或论文重叠的新论文。如实报告发现。不要夸大新颖性威胁，忽视真实重叠，或从薄弱证据中推断优先权。提供可操作的信号：RELAX、RESEARCH、FOLLOW-UP。

## 模式

- `arxiv-watch`：扫描目标类别或关键词簇中的近期论文。
- `venue-watch`：扫描 OpenReview、论文集、已接受论文列表或官方会议页面。
- `novelty-check`：将给定想法与近期论文进行比较并标记重叠。
- `trend-scouting`：总结新兴方向、拥挤领域和未经充分测试的空白。
- `competitor-tracking`：监控指定的研究组、实验室、存储库、数据集、基准或作者。
- `paper-alert-digest`：生成适合保存到项目文件夹的周期性监控报告。

## 技能链接

- @READS `ccfa.yaml` 以获取想法状态。
- @SHARES 发现结果给 `ccf-literature-searcher`。
- @SHARES 新颖性影响给 `ccf-idea-reviewer`。
- @SHARES 救援或区分机会给 `ccf-idea-optimizer`。
- @SHARES 引用和定位候选者给 `ccf-paper-writer`。
- @FLAGS 冲突论文给 `ccf-integrity-auditor`。

## 调用控制

**CCFA 交接模式：PARTIAL（推荐）。** 遵循 `metadata.ccf_skill_controls.handoff_question_mode` 和 `../ccf-common/references/handoff-modes.md`。

在决定探索性、快速或标准模式之前，加载 `../ccf-common/references/task-modes.md`。

将未发表的论文、草稿摘要、方法和结果视为私人材料。在使用查询中的私人文本之前，加载 `../ccf-common/references/privacy-and-evidence.md`。使用公共安全的关键词、公共方法名、会议名称和用户批准的查询文本。

当监控结果提供想法评分、论文评审或评分风险语言时，加载 `../ccf-common/references/review-output-standards.md`。

## 工作流

1. 加载 `references/monitoring-workflow.md`。
2. 如果项目状态可用 (`ccfa.yaml`)，读取当前想法、目标会议、主张和跟踪的竞争对手。
3. 选择模式和时间段。如果用户说“最新”、“近期”、“新”、“本周”或“今天”，请验证当前日期并使用明确的日期范围。
4. 使用共享策略中的公共安全查询和源质量排除，执行请求的监控模式。
5. 按问题、机制、证据、基准、数据集、主张和会议定位对重叠进行分类。
6. 报告新或实质性变化的发现，并为请求的研究决策提供精确的影响。使用现有的报告历史记录以避免将同一篇论文作为新论文呈现。
7. 通过其负责人执行已请求的下游工作；否则，提供可选交接给 `ccf-literature-searcher` 以进行深度检索，`ccf-idea-reviewer` 以评估影响，`ccf-idea-optimizer` 以进行区分，或 `ccf-paper-writer` 以整合相关工作。

## 输出合同

对于每次监控执行，按此结构报告：

```markdown
## 文献监控报告：[模式] - [主题/会议]

**自：** [YYYY-MM-DD]
**时间范围：** [从] 到 [到]
**扫描来源：** [arXiv 类别 / 会议 / 实验室 / API]
**扫描论文数：** [数量]
**高相关论文数：** [数量]
**总体信号：** RELAX / RESEARCH / FOLLOW-UP

| 标题 | 来源 | 重叠级别 | 重叠类型 | 证据基础 | 行动 |
|:---|:---|:---:|:---|:---|:---:|
| [标题] | [arXiv/OpenReview/会议] | 无/低/中/高 | 问题/方法/证据/基准 | [摘要/引言/结果] | RELAX/RESEARCH/FOLLOW-UP |

**可操作信号：**
- RELAX：在扫描窗口中未发现实质性重叠；继续，但不要声称完全新颖性证明。
- RESEARCH：部分重叠或可能接近的工作；通过 `ccf-literature-searcher` 进行深度检索。
- FOLLOW-UP：在问题、机制和证据方面存在显著重叠；在撰写更强的新颖性主张之前，路由到 `ccf-idea-reviewer` 或 `ccf-idea-optimizer`。

**交接信号：**
- `ccf-literature-searcher`：[需要深度检索的论文或簇]
- `ccf-idea-reviewer`：[新颖性或评分影响]
- `ccf-idea-optimizer`：[区分或救援方向]
- `ccf-paper-writer`：[相关工作或定位更新]
- `ccf-integrity-auditor`：[引用/归属冲突]

**输出自检：** [日期范围明确，来源基础说明，表格有效，无不支持的新颖性结论]
```

## 参考文献

- `references/monitoring-workflow.md` — 工作流、api-key-management、搜索策略。
- `references/report-template.md` — 输出模板和格式。
- `../ccf-common/references/source-registry.yaml` — 竞争对手和 arxiv 链接。

## 执行与持久化

区分单次扫描和周期性监控。周期性报告格式不是调度器：只有在实际授权的调度作业存在后，才声称持续监控。记录时间窗口和覆盖范围；空扫描不是新颖性的证明。按稳定论文身份和版本去重，将首次发表与修订分开。在支持时批量独立信息流；在 `../ccf-common/references/artifact-contracts.md` 下保留真实的监控历史。遵循无新文件和现有项目状态授权。
