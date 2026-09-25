# OpenSEO 竞争格局

## 目标

回答： "这个 SEO 市场谁在赢，他们哪些内容有效，以及有哪些机会？"

在用户需要跨多个竞争对手获取市场级视图时使用。对于单个域的深入分析，请使用 `competitor-analysis`。

## 必填输入

- `projectId`
- 主题、种子关键词、市场/类别或用户域
- 可选的已知竞争对手
- 可选的位置/语言

## 项目上下文

项目上下文工具免费，并与应用程序和其他代理共享。

1. 首先调用 `get_project_context` 并将其作为市场阅读的基础——保存的竞争对手是初始阵容，而业务和定位决定了谁被视为竞争对手。
2. 这个技能需要竞争对手。如果没有保存，请运行最小的内联设置：询问用户他们与谁竞争，或从 `find_serp_competitors` 和网站中推断出简短清单并确认，使用 `update_project_context` (`addCompetitors`) 将其写回，然后继续竞争格局工作。永远不要提前加载完整的访谈；建议在最后使用 `seo-project-setup` 来完成其余部分。
3. 在花费积分之前，请检查研究日志。如果相同的研究在最近 30 天内运行过，请重用该结果并说明，而不是重新购买。
4. 完成后，使用 `update_project_context` 写回持久内容——通过 `addCompetitors` 确认每个竞争对手并附上简短说明他们为什么重要，以及 `removeCompetitors` 删除那些最终无关的条目（保留用户添加的行）——并附加一个研究日志条目：`{ appendResearchLog: { summary: "Competitive landscape: <market/query set>. Verdict: <conclusion>" } }`。

## 以报告形式交付

通过 `seo-report` 技能交付，并使用 `skill: "competitive-landscape"` 保存。如果该技能不可用，请在写入 HTML 之前说明并停止。

## OpenSEO MCP 工具

- `research_keywords`：发现代表性市场查询。
- `get_keyword_metrics`：使用量、难度、意图和趋势验证已知查询集。
- `get_serp_results`：识别目标查询中反复出现的排名域名。
- `find_serp_competitors`：比较在提供的关键词中竞争的域名；当关键词集可用时，在手动 SERP 计数之前使用此工具。
- `get_domain_overview`：为候选领导者估算有机足迹。
- `get_search_console_performance`：当用户的域在比较中并且已连接 Search Console 时，使用第一方点击/印象/CTR 而不是第三方估计来锚定他们的位置。
- `get_ranked_keywords`：为领导者找到确切的排名关键词、URL、排名、意图和 SERP 结果类型。
- `get_backlinks_overview`：在相关时比较反向链接/引用域的强度。
- `search_local_businesses`、`get_local_serp_results` 和 `get_google_business_questions`：用于本地 SEO 市场，其中邻近性、地图排名、业务类别、评论或 Google Q&A 影响谁在赢。

## 工作流程

1. 定义市场查询集：
   - 使用提供的关键词，或调用 `research_keywords` 构建代表 5-10 个查询。
   - 包含混合意图：当适用时，包括信息性、商业性、比较性和工具/软件术语。
   - 对于本地 SEO，包括社区/城市/服务区域查询，并确定优先位置或坐标。
2. 如果查询集已知，使用 `get_keyword_metrics` 验证相对需求和难度，并使用 `find_serp_competitors` 大规模识别重复出现的域名。
3. 对于本地 SEO，在综合获胜者之前，为最高优先级的位置调用 `search_local_businesses` 和 `get_local_serp_results`。使用 `get_serp_results` 作为有机页面的补充，而不是唯一的本地证据。
4. 当需要检查实时 SERP 组成、排名 URL 或 SERP 功能时，调用 `get_serp_results`。每次调用最多发送 10 个查询。
5. 识别重复出现的域名并按类型分组：
   - 直接产品竞争对手
   - 出版商/媒体
   - 市场营销/目录
   - 社区/论坛
   - 文档/资源
6. 对于最强的重复出现的域名，调用 `get_domain_overview`；默认为前 3-5 个域名，然后扩展。
7. 对于直接竞争对手和相关出版商，调用 `get_ranked_keywords`。
8. 当反向链接权威性看起来重要或用户询问某个域名为什么在赢时，使用 `get_backlinks_overview`。如果账户未启用该数据，反向链接可能不可用；如果失败，请继续使用 SERP/域名证据。
9. 综合模式：内容类型、主题、SERP 格式、本地包信号、权威优势以及未满足的方面。

## 输出格式

`h1`：市场或类别。

如果适用报告模板（见 `seo-report`），其部分和语气将替换此列表。

按顺序排列的部分：

1. **市场阅读**——一个或两个开篇句子，命名领导者、最可赢的区域和最大的障碍。
2. **谁在赢**——一个表格，显示域名、类型、有机足迹、获胜主题和差距。明确标记域名类型。
3. **他们为什么赢**——每个模式一个发现，Fix 指向用户应该做什么。
4. **差距和机会**——一个表格，显示主题、需求和当前拥有者，以及当少数主题承载需求时出现的条形图。
5. **下一步做什么**——一个有序列表，以下一个工作流程结束：竞争对手分析、关键词聚类或内容摘要。
6. **如何生成此报告**——以 `seo-report` 的技能链接行开头，指向 `https://openseo.so/docs/skills/competitive-landscape` ("OpenSEO Competitive Landscape 技能")，然后是使用的查询集，并备注当查询集较小时，该阅读具有方向性。

## 遵守规则

- 区分 SEO 竞争对手和商业竞争对手。
- 当 OpenSEO 返回估计时，不要夸大确切流量。
- 如果使用较小的查询集，请称结果为方向性。
- 不要假设出版商是产品竞争对手；明确标记域名类型。
- 对于本地市场，区分有机页面获胜者和地图/本地包获胜者。
