# OpenSEO 关键词研究

## 目标

使用 OpenSEO MCP 数据将种子主题转化为优先级关键词机会集。输出结果应帮助用户决定要瞄准什么、要保存什么以及下一步要研究什么。

## 必须的输入

- `projectId`
- 一个或多个种子主题、产品、页面、竞争对手或受众问题
- 可选的市场/位置/语言

如果缺少 `projectId`，请先使用 `list_projects`。如果目标市场/位置/语言不明确且会实质性影响关键词指标，请询问用户；否则使用 MCP 工具的默认设置。

## 项目上下文

项目上下文工具是免费的，并与应用程序和其他代理共享。

1. 首先调用 `get_project_context` 并将其作为研究的基础——业务、目标、市场以及已保存的竞争对手和关键页面。
2. 此技能需要 `business_overview` 和 `current_goal`。如果其中任何一个为空，请运行最小的内联设置：询问用户，或从网站中推断并确认，仅足够填充它们，然后使用 `update_project_context` 将它们写回，然后继续研究。永远不要预先加载完整的访谈；建议在最后使用 `seo-project-setup` 进行其余部分。
3. 在花费积分之前，请检查研究日志。如果相同的研究在过去 30 天内运行过，请重用该结果并说明，而不是重新购买。
4. 完成后，写回持久化的内容——一个更清晰的 `business_overview` 或 `current_goal`，通过 `addCompetitors` 持续出现在搜索结果页面中的竞争对手，以及关键词应该落地的页面通过 `addKeyPages`——并追加一个研究日志条目：`{ appendResearchLog: { summary: "关键词研究: <seeds/market>. 结论: <conclusion>" } }`。

## 以报告形式交付

通过 `seo-report` 技能交付，并使用 `skill: "keyword-research"` 保存。如果该技能不可用，请说明并在写入 HTML 之前停止。

## OpenSEO MCP 工具

- `research_keywords`：主要发现工具。每次调用使用 1-5 个种子，并优先选择 150 个结果，除非用户要求进行彻底研究。
- `get_keyword_metrics`：一次调用最多为 700 个已知关键词提供搜索量、关键词难度 (KD)、搜索意图、CPC 和月度趋势。使用它来评分候选词或已知术语——包括步骤 1 中的 Search Console 可触及查询。
- `get_ranked_keywords`：当目标域名或页面是研究简报的一部分时，拉取确切的排名关键词行。
- `get_search_console_performance`：当连接 Search Console 时，从项目的真实第一方需求开始——已经获得印象并接近排名的查询（“可触及”术语）。传递 `minPosition: 5, maxPosition: 20, minImpressions: 50` 以便服务器为您过滤可触及的行（Google 按点击排序，无法自行过滤位置）。然后使用 `get_keyword_metrics` 为这些可触及查询添加难度和意图。
- `get_serp_results`：检查候选词的搜索结果页面，尤其是在意图不明确时。
- `search_local_businesses`、`get_local_serp_results` 和 `get_google_business_questions`：用于本地 SEO 主题，当业务/位置半径很重要时。
- `list_saved_keywords`：避免重复已保存的工作或使用现有标签作为上下文。
- `save_keywords`：仅在明确用户确认后保存选定的关键词。

## 工作流程

1. 将种子主题标准化为一个小型的独特研究角度集。如果项目连接了 Search Console，首先使用 `get_search_console_performance` 与 `minPosition: 5, maxPosition: 20, minImpressions: 50`（默认回顾期）拉取查询，并使用 `get_keyword_metrics` 为这些查询添加 KD 和意图。该排名和加水的列表是您最快的机遇集——在广泛发现之前先处理它。
2. 如果请求是本地 SEO，请确定业务、位置/坐标或服务区域以及本地类别。使用 `search_local_businesses` 和 `get_local_serp_results` 为最重要的位置/关键词集提供数据，而不是仅依赖全国性关键词/搜索结果数据。
3. 调用 `research_keywords` 进行探索性种子。在可能的情况下使用批量调用。
4. 使用 `get_keyword_metrics` 在优先级排序之前为固定关键词列表——或步骤 1 中的可触及查询——添加搜索量、KD 和意图。
5. 当用户提供域名/页面并希望基于当前排名、接近失误或竞争对手拥有的术语获得机遇时，使用 `get_ranked_keywords`。
6. 移除不相关、重复、仅品牌和意图不匹配的术语。
7. 按实际机遇而非仅按搜索量进行优先级排序：
   - 与用户的 产品/页面/主题 强匹配
   - 明确的搜索意图
   - 合理的难度
   - 有用的搜索量/CPC 信号
   - 用户可能竞争的搜索结果页面
   - 对于本地 SEO，本地包/地图可见性和邻近度匹配
8. 使用 `get_serp_results` 对高潜力或意图不明确的词进行检查，当搜索结果页面意图会改变推荐时；保持默认检查量小。
9. 提供一个短名单和一个更长的机遇表。
10. 在保存关键词之前询问。保存时，建议使用简洁的标签，如 `topic:<topic>`、`intent:<intent>` 或 `page:<slug>`。

## 输出格式

`h1`：网站或主题。

如果适用报告模板（见 `seo-report`），其部分和语气将替换此列表。

按以下顺序排列的部分：

1. **机遇**——一到两句话命名最佳主题以及为什么网站现在可以赢得它。
2. **立即瞄准这些**——一个包含关键词、意图、搜索量、KD、CPC 和要创建的页面的表格。添加一个比较短名单搜索量的条形图。
3. **为什么这些**——每个关键词需要一个解释：搜索结果页面或指标证据，然后是构建的页面。
4. **更长的机遇列表**——第二个表格，相同列。
5. **风险和注意事项**——笔记：会改变推荐的搜索结果页面意图，缺失的指标写为 `unknown`，近义词量是一个桶而不是几个。
6. **下一步做什么**——一个有序列表，包括是否运行关键词聚类、编写内容摘要或保存选定的关键词。
7. **如何生成此报告**——以 `seo-report` 的技能链接行开头，指向 `https://openseo.so/docs/skills/keyword-research`（“OpenSEO 关键词研究技能”），然后是哪些工具返回了什么。

## 防护措施

- 不要编造指标。如果 OpenSEO 没有返回值，请写 `unknown`。
- 不要在未经明确确认的情况下调用 `save_keywords`。
- 优先考虑业务匹配和意图匹配，而不是追逐最大搜索量的术语。
