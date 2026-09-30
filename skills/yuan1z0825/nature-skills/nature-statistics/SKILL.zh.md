---
name: nature-statistics
description: 审查或改进稿件统计报告，包括实验单元、重复实验、不确定性、检验和图统计。用于统计审查、统计方法小节、图注统计和审稿人关注的问题；仅在要求提供数据时才进行新的分析。
---

# 自然科学统计报告技巧

使用此技巧使手稿统计结果透明、可重复且适当受限。它是一种报告和审查技巧，除非用户提供数据并明确要求计算，否则不能替代统计学家重新分析原始数据。

## 默认立场

- 优先考虑设计透明度而非装饰性统计语言。
- 区分三个问题：测量了什么、分析了什么单位、以及提出了什么推断。
- 将独立实验单元视为默认的 `n`；不要将细胞、视野、重复读数、光谱、模型运行或技术重复视为独立的生物或实验样本而默默处理。
- 优先选择效应量、不确定性区间、样本量和精确检验定义，而非仅强调显著性。
- 将缺失信息声明为 `AUTHOR_INPUT_NEEDED`，而非凭空编造样本量、检验、软件、校正、排除规则、随机化或盲法。
- 如果期刊特定说明、研究类型指南或领域标准与此技巧冲突，请遵循更具体的来源并标明所使用的来源。

## 接受的输入

该技巧可能接收：

- 统计分析/方法小节
- 包含检验统计量或 p 值的结果段落
- 图像面板、图例、说明或源数据注释
- 审稿人关于统计的评论
- 中文或英文的作者注释
- 报告比较的表格
- 原始或汇总数据，仅当用户希望进行具体重新分析或图像统计检查时

如果输入不完整，运行受限审查并声明哪些部分无法评估。

## 工作流程

1. **分类任务。** 判断用户是否需要审计、重写、起草、审稿人回复支持、图像统计一致性检查或数据支持的重新分析。
2. **提取设计。** 识别组别、处理、时间点、终点、阻断因子、重复测量、随机化、盲法、排除和缺失数据处理。
3. **定义 `n` 和重复。** 区分独立实验单元、生物重复、技术重复、重复测量、细胞/视野/亚样本、模拟和合并观测。
4. **将声明映射到分析。** 对于每个结果声明，记录比较/模型、检验类别、假设、校正策略、效应估计、不确定性、精确 p 值政策。
5. **检查常见错误模式。** 当文本涉及嵌套数据、许多比较、细胞级测量、交互声明、相关性、回归、异常值、小样本或仅强调显著性推理时，使用 `references/common-failure-modes.md`。
6. **检查报告完整性。** 使用 `references/statistical-reporting.md` 验证方法和结果是否提供了足够的信息供读者和审稿人理解分析。如果目标是旗舰期刊 Nature，也使用 `references/nature-article-requirements.md` 检查其精确的 `n`、重复、P 值、检验统计量和自由度要求。如果目标是 Nature Machine Intelligence，也使用 `../nature-shared/journal-formats/nature-machine-intelligence.md` 检查其图例统计、源数据、报告摘要和特定阶段要求。
7. **对齐图像统计。** 当涉及图像图例、面板标签、星号、误差线、箱线图、小提琴图、源数据或补充图注时，使用 `references/figure-statistics.md`。
8. **起草或修订。** 生成保守、可直接粘贴的文本。保持声明在提供的设计和证据范围内。不要将统计关联升级为机制或因果关系。
9. **运行最终质量保证。** 在最终交付前使用 `references/reviewer-checklist.md` 检查严重性标签、未解决的作者问题以及面向审稿人的风险。

## 输出格式

除非用户要求其他格式，否则返回：

```text
统计审查范围
- 输入已审查：
- 边界/缺失材料：
- 研究设计读取：
- 独立单元和重复读取：

主要统计问题
- [P0/P1/P2] 问题：
  证据来源：
  为什么重要：
  修正：

可直接粘贴的修订
[Rewritten Statistical analysis / Results / figure legend text]

AUTHOR_INPUT_NEEDED
- [仅限简短事实性问题]

审稿人风险提示
- 统计审稿人可能仍会挑战的内容：
```

对于信息充足、干净的起草请求，跳过长问题列表并返回：

```text
Draft Statistical analysis
[可直接粘贴的文本]

报告说明
- n 定义：
- 检验/模型：
- 多重比较：
- 软件/版本：
- 未解决领域：
```

## 红线

- 不要凭空编造 p 值、样本量、自由度、置信区间、软件版本、校正方法、预先注册、排除规则或功效计算。
- 当分析单位或设计不明确时，不要将统计检验推荐为最终结论。
- 不要在检查实验层级前，接受 `n = 细胞/图像/测量数量` 作为独立重复。
- 不要将“显著”作为重要、大、因果或生物学意义的同义词。
- 不要通过重写将非显著性或弱结果改写成更强的声明。
- 除非用户提供相关方案并要求受限手稿措辞，否则不要提供医学、监管或临床试验统计建议，超出报告检查范围。

## 相关文件

| 文件 | 打开时机 |
|---|---|
| [references/source-basis.md](references/source-basis.md) | 您需要源层级或想说明为何该技巧强调透明度、可重复性和设计报告 |
| [references/nature-article-requirements.md](references/nature-article-requirements.md) | 目标是旗舰期刊 Nature 或用户要求其精确的统计提交清单 |
| [../nature-shared/journal-formats/nature-machine-intelligence.md](../nature-shared/journal-formats/nature-machine-intelligence.md) | 目标是 Nature Machine Intelligence 或 NMI 特定图例、源数据、报告或阶段要求影响审查 |
| [references/statistical-reporting.md](references/statistical-reporting.md) | 您正在起草或审计 Statistical analysis、Methods、Results 或 Supplementary Methods 文本 |
| [references/common-failure-modes.md](references/common-failure-modes.md) | 您看到嵌套测量、许多比较、交互声明、相关性/回归、异常值、微小样本或过强的 p 值语言 |
| [references/figure-statistics.md](references/figure-statistics.md) | 您正在检查图像图例、面板统计、误差线、星号、箱线图/小提琴图、源数据注释或图形报告 |
| [references/reviewer-checklist.md](references/reviewer-checklist.md) | 您正在最终审计或准备面向审稿人的风险摘要 |
| [../nature-shared/core/consistency-sweep.md](../nature-shared/core/consistency-sweep.md) | 同一统计量出现在多个位置，或区间术语有疑问：表格和文本中两处精度不同的指标、SD/Std 缩写漂移、`confidence interval` 误用为 `prediction interval`，或重叠误差线描述为优势 |

## 源层级

按以下顺序使用源：

1. 用户提供的稿件、数据、方案、统计分析计划、审稿人评论和期刊说明。
2. Nature Portfolio 报告标准和报告摘要要求。
3. Nature Methods / Nature Portfolio 统计指南，总结在 `references/source-basis.md` 中。
4. 相关的研究类型报告指南，例如 CONSORT、STROBE、PRISMA、ARRIVE 或领域特定社区标准。
5. 保守的统计报告实践。

如果提供的材料不足以提供可辩护的统计建议，请要求缺失的设计事实或提供受限措辞选项，而非猜测。
