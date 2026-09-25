# Firecrawl 工作流

当用户需要由 Firecrawl 驱动的成品交付物，而不仅仅是原始网页提取和产品代码集成时，使用此选项。

## 选择工作流

- 使用 `[firecrawl-website-design-clone](../firecrawl-website-design-clone/SKILL.md)` 从网站中提取颜色、字体、间距、组件和布局模式，将其转换为代理可用的 `DESIGN.md`。
- 使用 `[firecrawl-research-papers](../firecrawl-research-papers/SKILL.md)` 进行文献综述和基于论文的综合分析，包括生物医学、临床、药物、基因、疾病、流行病学和公共卫生主题。它查询 Firecrawl 的论文索引——PubMed、bioRxiv、medRxiv 和 arXiv 摘要，每篇论文都可以获取全文——而不是搜索网站。
- 使用 `[firecrawl-deep-research](../firecrawl-deep-research/SKILL.md)` 进行基于网络证据（**网络**）的多源研究报告：市场、政策、技术或行业主题。不用于文献综述——当证据基础是已发表的论文时，请使用上方的 `firecrawl-research-papers`。
- 使用 `[firecrawl-seo-audit](../firecrawl-seo-audit/SKILL.md)` 进行网站结构、页面内 SEO、关键词和搜索结果页面（SERP）审核。
- 使用 `[firecrawl-lead-research](../firecrawl-lead-research/SKILL.md)` 进行会议前的公司/人员情报简报。
- 使用 `[firecrawl-qa](../firecrawl-qa/SKILL.md)` 进行现场 QA 测试和错误报告。
- 使用 `[firecrawl-competitive-intel](../firecrawl-competitive-intel/SKILL.md)` 进行定期价格、功能和变更日志监控。
- 使用 `[firecrawl-company-directories](../firecrawl-company-directories/SKILL.md)` 进行目录提取到公司列表。
- 使用 `[firecrawl-dashboard-reporting](../firecrawl-dashboard-reporting/SKILL.md)` 进行仪表板指标提取。
- 使用 `[firecrawl-knowledge-base](../firecrawl-knowledge-base/SKILL.md)` 进行 LLM 可用文档、RAG 块、训练数据或文档镜像。
- 使用 `[firecrawl-knowledge-ingest](../firecrawl-knowledge-ingest/SKILL.md)` 进行受权限保护或 JS 依赖性强的文档门户导入。
- 使用 `[firecrawl-lead-gen](../firecrawl-lead-gen/SKILL.md)` 进行潜在客户列表生成。
- 使用 `[firecrawl-market-research](../firecrawl-market-research/SKILL.md)` 进行市场、财务和行业研究。
- 使用 `[firecrawl-demo-walkthrough](../firecrawl-demo-walkthrough/SKILL.md)` 进行产品流程演示和用户体验（UX）拆解报告。
- 使用 `[firecrawl-shop](../firecrawl-shop/SKILL.md)` 进行产品研究和购物推荐。

如果现有工作流不适用，请使用此通用流程并生成可重用的模式，这可能成为一项新技能。

## 必要输入

根据用户的请求和周围上下文推断工作流、输入、受众和输出格式。如果足够清晰，请立即开始。

仅在缺少输入会阻碍工作的情况下，最多问 1-3 个简洁的澄清问题，例如：

- 分析的 URL、公司、主题或来源
- 期望的交付物或输出格式
- 会实质性改变工作流的约束条件

使用主机代理的正常方式提问澄清问题。不要依赖特定于 harness 的函数名称。

## 默认流程

1. 确认工作流和最终交付物。
2. 通过 CLI 或等效 Firecrawl 工具界面使用 Firecrawl 收集网络证据。
3. 保存或引用源证据，以便最终声明可追溯。
4. 在可用时并行运行独立研究单元。
5. 将发现结果综合到请求的交付物中。
6. 当工作流可以自动化时，包含一个简短的“重新运行输入”块。

## 并行工作

如果合适，使用子代理或等效并行任务运行器处理独立单元，例如：

- 每个研究人员一个竞争对手
- 每个研究人员一个 URL 或页面
- 每个研究人员一个来源类别
- 每个评审员一个分析维度

保持交接的通用性：提供工作单元、源 URL 或搜索词、预期的提取字段和输出格式。

## 交付物标准

每个工作流应返回：

- 简洁的执行摘要
- 使用的证据基础
- 用户请求的分析或交付物
- 有用的建议或下一步行动
- 用于重新运行的自动化输入

有关编写新工作流技能，请参阅 [workflow-authoring.md](references/workflow-authoring.md)。
