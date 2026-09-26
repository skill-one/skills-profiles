# CCF 论文撰写工具

## 家庭文件合同

在撰写前，确定每个任务/成果的规范输出和一个稳定的 working directory。重用明确的或已建立的路径；否则使用项目根目录 `ccfa-workfiles/<用途>/<成果ID>/`，仅在需要时使用 `source/`、`assets/`、`cache/` 和 `build/`。就地更新当前文件；不要分散中间文件或创建迭代副本。保留输入和所需证据；仅清理此任务创建的已验证的可丢弃文件。使用 UTF-8 文本 I/O，并在保存或渲染后检查中文文本。对于文件工作，应用 [artifact-contracts.md](../ccf-common/references/artifact-contracts.md) 并在技能转换时重用相同的路径。

## 协作合同

在专家执行前，首先阅读并应用 [ccf-humanization](../ccf-humanization/SKILL.md)，然后应用 [ccf-common](../ccf-common/SKILL.md)。在每次交接时，重用适用的活跃规则或刷新缺失/更改的规则。即使没有文本，这两个预检也是必需的；详细的编辑、实验和维护模式仅在相关时运行。

保留一个集成的负责人，并积极使用其他技能来解决缺失的先决条件或检查材料发现。重用适用的证据；不要为了节省 token 而跳过必要的准备工作。在最终确定前，集成贡献并验证受影响的成果。遵循条件性 [合作路线](../ccf-common/references/routing.md)；避免不相关的阶段和重复报告。

## 调用控制

**CCFA 交接模式：PARTIAL（推荐）。** 遵循 `metadata.ccf_skill_controls.handoff_question_mode`、`../ccf-common/references/handoff-modes.md` 和 `../ccf-common/references/task-modes.md`。用户范围和现有授权控制执行；保留仅计划、不浏览、精确输出和不创建新文件请求。

此技能拥有手稿文本、压缩和演示文本。保留提供的题目、方法机制、实验设置、数字、引用键和结论，除非授权进行研究更改。请求的修订授权进行常规的准确措辞编辑和必要的本地检查。

将 `ccf-humanization` 作为面向手稿的第一步预检。阅读 `../ccf-humanization/references/humanization-policy.md` 和 `references/prose-quality-guardrails.md`。这些指导直接的科学写作；它们不会启动单独的审查或确认循环。

## 撰写标准

从贡献出发撰写：什么问题重要，为什么机制解决它，证据确立了什么，以及接下来会发生什么。用其科学内容替换面向审稿人的安慰性陈述、道歉性新颖性声明、重复的警告、以否认为导向的定位和堆叠的模糊语。删除没有内容的句子。不要习惯性地在每个段落、摘要、标题或结论中添加限制性句子。

保留有意义的不确定性、已知的负面结果、必要的假设、公平比较限制和强制披露，使用直接的学术文本。不要写方法已被确认、批准或适合发表。解释实际方法和相关配置。缺失的结果仍然是缺失的；建议的研究不是完成的实验。永远不要猜测引用或插入虚构的测量值来完成草稿。

使用人类化政策作为标点符号和模式阈值的单一来源。自然写作是一个语义编辑任务；通过短语检查器并不代表质量。即使启发式方法标记它们，也要保留科学上必要的术语、否定和模糊语。

## 模式和参考加载

| 模式 | 交付物 | 超出共享文本政策的参考 |
| --- | --- | --- |
| `polish` | 修订的段落或其源格式中的本地段落 | 除非事实、引用或明确的风格问题需要，否则无需。 |
| `draft` 部分 | 具有连贯科学论证的请求部分 | 相关的 `references/section-modules.md` 部分；仅在需要文献支持时才进行引用工作流。 |
| `draft` 手稿 | 完整的证据绑定手稿 | 场所指南、`references/length-budget-policy.md`、`references/storyline-blueprint.md` 和相关的部分/清单参考。 |
| `compress` | 保留意义和数字的缩短源文本 | `references/compression-rules.md`。 |
| `presentation` | 从提供的研究中提取的幻灯片/海报/演讲/Q&A 文本 | `references/section-modules.md` 中适用的演示指导以及源论文。 |

摘要、标题、概要、段落编辑或精确的 JSON 响应默认情况下不需要场所指南、完整示例、审稿人小组或长度规划。仅当请求风格调整或受益于它们的全手稿时，从 `references/exemplars/index.md` 加载匹配的示例卡片。永远不要复制示例措辞或技术内容。

## 工作流程

1. 从对话和提供的文件中识别请求的模式、输出格式、证据和目标长度。推断常规选择；仅请求缺失的决定，该决定会改变研究声明、交付物或可行性。在等待该决定时，继续独立工作。
2. 对于对现有手稿的授权编辑，就地修订该文件并保留 Markdown/LaTeX 部分、命令、引用、标签、方程式和浮动环境，除非请求重新结构。遵循 `../ccf-common/references/artifact-contracts.md`；对于普通迭代，不创建日期或 `v2` 副本。仅提供文件进行检查并不授权重写它。
3. 对于完整提交手稿，阅读 `references/venue-guides/index.md` 和匹配的指南，然后使用 `references/length-budget-policy.md` 建立部分预算。如果没有场所或指南可用，使用现有的 NeurIPS 指南/模板作为公开的起草假设。`references/output-style-policy.md` 控制模糊的格式选择。当前的最终政策要求官方验证；本地指南可以支持临时草稿。
4. 组织科学论证。对于重要的引言或完整手稿，使用 `references/storyline-blueprint.md`；对于有边界的文本，直接连接问题、见解、机制、证据和启示。在解释变化的地方保留材料范围。不要为普通写作生成审稿人风险登记册或多专家锦标赛。
5. 在断言依赖声明之前解决证据先决条件。当需要文献时，加载 `references/citation-workflow.md`，使用 `ccf-literature-searcher` 查找缺失的来源，并更新参考书目而不更改无关的键。使用 `ccf-integrity-auditor` 处理未解决的引用支持或数值冲突。重用适用的已验证证据。对于仅提供证据或无浏览任务，保留提供的引用，并将不受支持的声明保留为临时状态，而不要编造条目。
6. 撰写请求的成果。仅对于实质性写作，使用 `references/research-writing-patterns.md`、相关的 `references/section-modules.md` 段落和适用的 `references/writing-checklists.md` 检查。完整论文包括所有科学上相关且场所要求的部分，带有明确的 `TBD` 占位符，表示不可用的证据。保留方法、设置和分析实质性；永远不要用通用的谨慎、假设模块或虚构结果来填充。
7. 对于报告的实验比较，当方法身份或协议重要时，咨询 `../ccf-humanization/references/experiment-discipline.md`。使用提供的建议方法设计规范，并使用引用的证据；不要要求可运行的检查点或完整的实验确认来执行文本编辑。
8. 对于具有可用引擎的完整 LaTeX 手稿，编译并检查页数、错误、引用和受影响的布局。修复具体问题，扩展实际解释性差距，并压缩多余内容。将辅助文件、构建日志和当前预览放在建立的构建目录或选择的任务 working directory 下；仅在成功构建后，将请求的 PDF 导出到其规范路径。保留现有的相对包含和构建配置。在相关更改后重新编译；如果另一轮没有实质性进展，请修订方法或报告确切的剩余问题。不要循环填充页面或追逐无害的警告。在请求或必要时，将最终场所合规性留给 `ccf-submission-checker`。
9. 使用 Humanization 的句子决策一次性检查结果文本。对于完整部分或论文，当可用时运行 `scripts/check_prose_quality.py`。在上下文中检查防御性语言的候选者；修复真实问题并保留合理的科学语言。仅在请求严格的报告时使用 `--strict`，而不是作为通用的出版门。仅针对更改的内容或未解决的发现重新运行。
10. 对于重要的草稿或对论证/证据的更改，使用 `ccf-paper-reviewer` 检查受影响的声明-证据链接、连贯性和未解决的审稿人发现，除非这些检查已经涵盖当前文本。在授权的写作范围内集成更正并验证它们；不需要单独的完整审查报告或接受分数。本地措辞编辑使用本地检查。如果缺失的证据需要新的研究决策，请保留受影响的声明未解决，并继续支持的工作。在满足适用先决条件和检查后交付，而不要启动不相关的下游输出。

## 输出合同

首先以用户的格式返回实际修订的文本、手稿、压缩段落或演示文本。普通的本地编辑不需要模式/状态/下一技能块。对于完整手稿文件，报告它们的路径、实质性更改、相关验证和具体的未解决证据。精确模式保持精确。

完整的草稿包含适当深度的请求科学部分；它可能仍然是证据不完整的。区分草稿完成与提交准备。不要将未知结果标记为观察结果，或从文本修订中声称测量分数改进。

## 参考文献

根据上述模式选择性地加载：

- `references/output-style-policy.md`、`references/length-budget-policy.md`：源格式保留和手稿预算。
- `references/venue-guides/index.md`、`references/exemplars/index.md`：目标场所和选定的风格移动。
- `references/storyline-blueprint.md`、`references/section-modules.md`、`references/research-writing-patterns.md`：科学组织和部分写作。
- `references/citation-workflow.md`：验证的引用插入。
- `references/prose-quality-guardrails.md`、`references/writing-checklists.md`、`scripts/check_prose_quality.py`：语义文本审查和支持诊断。
- `references/compression-rules.md`：保留证据的压缩。
- `references/table-style-guide.md`：现有的 LaTeX 表格源指导；视觉重新设计属于 `ccf-visual-composer`。
- `references/score-lifting-loop.md`、`references/expert-review-loop.md`：在请求时应用实际审稿人扣除。
- `../ccf-common/references/review-output-standards.md`：条件分数和冻结的审查标准，仅用于请求的与审查相关的输出。
