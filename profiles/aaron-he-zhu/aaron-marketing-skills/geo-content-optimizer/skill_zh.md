# GEO内容优化器

优化内容以供AI生成答案和引用表面，如ChatGPT、Perplexity、Gemini、Claude和AI概述使用。

## 此技能的作用

改进结构、权威信号、事实密度、可引用的陈述、来源归因以及整体的GEO准备情况。

## 快速入门

```text
为GEO/AI引用优化此内容：[内容或URL]
使这篇文章更有可能被AI系统引用
撰写关于[主题]的内容，优化SEO和GEO
审计此内容以进行GEO准备并建议改进
AI概述正在消耗12个头部查询的点击量——制定恢复计划
```

有关针对恢复场景（与通用GEO优化相反）量身定制的4阶段剧本（衡量→诊断→重写→监控）的详细信息，请参阅[AI概述恢复](references/ai-overview-recovery.md)。

## 技能合约

**预期输出**：一个可立即使用的资产或可实施的转换，以及一个准备好用于`memory/content/`的简短交接摘要。

- **读取**：简报、目标关键词、实体输入和质量约束。**规范实体配置文件**：如果内容提到了品牌/人物/产品，此技能必须咨询`memory/entities/<slug>.md`（根据[实体-geo交接模式](../../../references/entity-geo-handoff-schema.md)），以填充`display_name`、`description_short`、`ai_resolution_status`并决定是否需要歧义样板。如果配置文件缺失或过时（>90天），则声明`DONE_WITH_CONCERNS`并建议`entity-registry`作为开放循环。
- **写入**：面向用户的内容、元数据或模式交付，以及可以存储在`memory/content/`下的可重用摘要。
- **推广**：批准的角度、信息选择、缺失的证据和发布障碍到`memory/hot-cache.md`和`memory/open-loops.md`；将持久性决策作为待定决策项提出。
- **完成时**：每个目标AI查询都有一个独立的、可引用的答案块；报告了GEO分数和AI查询覆盖率；CORE-EEAT GEO自我检查（C02、O03、O05、E01）没有未解决的失败。
- **主要下一步技能**：当资产准备好审查或部署时，使用下面的`Next Best Skill`。

### 交接摘要

> 从[skill-contract.md §交接摘要格式](../../../references/skill-contract.md)发出标准形状。

## 数据源

连接时使用`~~AI monitor`和`~~SEO tool`；否则，请询问目标查询、内容、引擎、竞争对手示例和已知的AI引用差距。参见[CONNECTORS.md](../../../CONNECTORS.md)。

**衡量GEO工作是否有效**：此技能所做的更改（可提取、可引用、答案形状的内容）使**可引用性**——可通过将URL交给实时获取引擎并询问目标查询在几分钟内进行测试。这是一个*代理*。一个引擎是否未经提示引用你（显示）受其爬取/索引刷新的限制——以周为单位且相互混淆，而不是以分钟为单位。不要混淆两者或承诺快速显示。每个信号的延迟以及为什么结果差异需要一个控制组，在[references/measurement-protocol.md](../../../references/measurement-protocol.md)中定义。

**无密钥AI引用探测（Tavily）**：`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/connectors/tavily.py" search "<目标查询>" --answer --limit 10` 运行该可引用性测试，针对真实的AI答案引擎，无需密钥——检查合成的答案是否引用了你的URL/域，以及该页面在评分来源中的排名。这对于Tavily自己的层是**测量**的，对于ChatGPT/Perplexity/Google AI概述是**估计代理**（不同的索引，不同的检索）。在发布更改后重新运行，以进行分钟级可引用性读取；根据上面的段落，未经提示的显示仍然是周级的。参见[scripts/connectors/README.md](../../../scripts/connectors/README.md)。

## 说明

当用户请求GEO优化时，执行以下五个步骤：

1. **加载CORE-EEAT GEO-First目标** — 优先考虑C02、C09、O03、O05、E01、O02加上特定引擎的偏好。
2. **分析当前内容** — 评分清晰的定义、可引用的陈述、事实密度、来源引用、问答格式、权威信号、新鲜度和结构清晰度。
3. **应用GEO技术** — 添加独立的25-50字定义、来源可引用的陈述、专家/来源信号、问答/表格/列表、特定数据以及可见内容匹配的FAQ模式。
4. **生成GEO输出** — 报告所做的更改、GEO分数（前后）和AI查询覆盖率。
5. **CORE-EEAT GEO自我检查** — 验证C02、C04、C09、O02、O03、O05、O06、R01、R02、R04、R07、E01、Exp10、Ept08，并使用Pass/Warn/Fail。然后运行[slop自我检查](../../../references/humanizer-slop.md)，在资产发布前删除AI告诉性措辞。

将每个指标标记为**测量**（工具/导出）、**用户提供**或**估计**（模型推理）；永远不要将估计呈现为测量；如果必需的指标不可用，请将其标记为N/A——不要编造它。

> **参考**：有关完整的CORE-EEAT GEO目标表、AI引擎偏好、分析模板、优化报告模板、自我检查矩阵和示例，请参阅[说明详情](references/instructions-detail.md)。

## 示例

**用户**："优化此段落以供GEO使用：'电子邮件营销是接触客户的好方法。它已经存在一段时间了，许多企业都在使用它。'"

**输出**添加了清晰的定义、日期/来源支持的事实、结构化列表、可引用的陈述和前后GEO分数。有关完整模式，请参阅[说明详情 — 示例](references/instructions-detail.md#example)。

## GEO优化清单

> **参考**：有关涵盖定义、可引用内容、权威、结构和技术元素的完整清单，请参阅[GEO优化技术](references/geo-optimization-techniques.md)中的GEO准备清单。

## 保存结果

在用户确认后，保存到`memory/content/YYYY-MM-DD-<主题>.md`——参见[技能合约](../../../references/skill-contract.md) §保存结果模板。

## 参考材料

- [说明详情](references/instructions-detail.md) - 完整的5步工作流、CORE-EEAT GEO目标、自我检查矩阵、示例、提示
- [GEO优化技术](references/geo-optimization-techniques.md) - 每种技术的详细前后示例、模板和清单
- [AI引用模式](references/ai-citation-patterns.md) - Google AI功能、ChatGPT搜索、Perplexity、Claude、Gemini基础、Copilot Studio和Brave Search的证据限制发现、检索和引用控制
- [可引用内容示例](references/quotable-content-examples.md) - 优化AI引用的内容的前后示例
- [Medium / GitHub AI引用表面](references/medium-github-surfaces.md) - 引擎引用的站外表面（Medium文章、GitHub存储库/README）
- [Slop自我检查](../../../references/humanizer-slop.md) - 发布前检查，以删除内容发布前的AI告诉性措辞
- [Agent可读文件堆栈（llms.txt / OKF）](../../../references/llms-txt-okf.md) - 机器可读文件，以便代理和引擎可以解析您的网站
- [Grokipedia策略](../../../references/platforms/grokipedia.md) - Grok / Grokipedia的AI引用策略
- **GEO分布表面** — 引擎从中获取的平台引用：[X](../../../references/platforms/x.md)、[LinkedIn](../../../references/platforms/linkedin.md)、[YouTube](../../../references/platforms/youtube.md)、[Reddit](../../../references/platforms/reddit.md)

## 下一步最佳技能

- **主要**：[content-quality-auditor](../../tune/content-quality-auditor/SKILL.md) — 验证优化后的内容足够强大，可以发布并引用。

**终止说明**：保持此会话的访问集；如果推荐的技能已经调用，则停止并报告链完成，而不是重新运行它。尊重最大交接深度为3，以避免循环（根据[skill-contract.md §终止规则](../../../references/skill-contract.md)）。
