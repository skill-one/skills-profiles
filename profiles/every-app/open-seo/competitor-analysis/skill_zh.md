# OpenSEO 竞争对手分析

## 目标

深入分析一个竞争对手，以便决定要从中学习什么、避免什么、进行差异化竞争或超越它。

用于指定名称的竞争对手。若要首先识别市场领导者，请使用 `competitive-landscape`。

## 必需输入

- `projectId`
- 竞争对手域名
- 当请求比较时用户域名
- 可选的主题/类别/位置/语言

## 项目上下文

项目上下文工具免费，并与应用程序和其他代理共享。

1. 首先调用 `get_project_context` 并将其作为分析的基础——保存的竞争对手会说明该域名是否已知以及之前得出的结论。
2. 此技能需要竞争对手。如果保存中没有竞争对手，请运行最小的内联设置：保存正在分析的竞争对手，并询问用户（或从 `find_serp_competitors` 推断并确认）是否有其他竞争对手，使用 `update_project_context` (`addCompetitors`) 将它们写回，然后继续分析。切勿预先加载完整访谈；建议在最后使用 `seo-project-setup` 进行其余部分。
3. 在花费积分之前，请检查研究日志。如果过去30天内运行了相同的研究，请重用该结果并说明，而不是重新购买。
4. 完成后，使用 `update_project_context` 写回持久内容——对该域名的 `addCompetitors` 更新操作，附带其优势和脆弱点的简短说明——并追加一个研究日志条目：`{ appendResearchLog: { summary: "Competitor analysis: <domain>. Verdict: <conclusion>" } }`。

## 以报告形式交付

通过 `seo-report` 技能交付，并使用 `skill: "competitor-analysis"` 保存。如果该技能不可用，请在写入 HTML 之前说明并停止。

## OpenSEO MCP 工具

- `get_domain_overview`: 基线有机流量和关键词数量。
- `get_search_console_performance`: 当与用户自己的域名进行比较且已连接 Search Console 时，将其用作第一方基线（真实点击量/展示量/CTR/排名）而不是从第三方数据估计用户自己的性能。
- `get_ranked_keywords`: 竞争对手域名或页面的精确关键词、URL、排名、意图、流量、CPC 和 SERP 类型行。
- `get_backlinks_overview`: 反向链接/来源域名资料。
- `find_serp_competitors`: 验证指定竞争对手是否在目标关键词集中是真正的搜索竞争对手。
- `search_local_businesses`, `get_local_serp_results`, 和 `get_google_business_questions`: 用于本地 SEO 竞争对手，当地图/本地包可见性、附近商家、类别或 Google Q&A 有关时使用。
- `get_serp_results`: 验证重要关键词的直接头对头 SERPs。
- `research_keywords`: 在需要时扩展差距或类别术语。

## 工作流程

1. 对竞争对手调用 `get_domain_overview`，在支持时传递提供的位置/语言。
2. 如果与用户比较，也对用户的域名调用 `get_domain_overview`——如果已连接 Search Console，则为用户调用 `get_search_console_performance` 以获取真实基线。
3. 对竞争对手调用 `get_ranked_keywords`。使用 `maxRank`、`minSearchVolume`、`excludeBrandTerms` 和 `resultTypes` 等过滤器以保持行相关。
4. 如果与用户比较，也对用户的域名/页面调用 `get_ranked_keywords`，或者当轻量级检查足够时使用 `get_serp_results` 对共享术语进行。
5. 对于本地 SEO，在得出本地包结论之前，使用 `search_local_businesses` 和 `get_local_serp_results` 围绕相关商业位置。仅在问答证据重要时添加 `get_google_business_questions`。
6. 当用户提供了竞争对手但其搜索重叠不明确时，使用 `find_serp_competitors`。
7. 将竞争对手关键词按主题分组：
   - 产品/类别术语
   - 替代品/比较
   - 模板/工具/计算器
   - 教育指南
   - 品牌需求
   - 当相关时本地/社区术语
8. 对竞争对手调用 `get_backlinks_overview`，特别是如果权威性似乎可以解释排名。如果无法获得反向链接证据，则继续分析。
9. 使用 `get_serp_results` 对重要共享或目标关键词进行比较，在支持时传递提供的位置/语言。
10. 制定可执行计划：
    - 他们做得好的地方
    - 他们的脆弱点
    - 要追求的页面/关键词
    - 要避免复制的内容

## 输出格式

`h1`: 竞争对手域名。

如果适用报告模板（见 `seo-report`），其部分和语气将替换此列表。

按顺序包含以下部分：

1. **快照**——一到两句话开头，然后是竞争对手有机足迹的表格（流量估计、关键词数量、来源域名）。在比较时将用户域名作为第二行添加。
2. **最大的教训**——一个发现。
3. **他们的脆弱点**——每个开头一个发现，按可取胜程度排序。
4. **关键词主题**——一个包含主题、示例关键词、流量以及用户是否竞争该主题的表格。当少数主题主导足迹时显示条形图。
5. **内容模式和权威**——散文，对从关键词行推断而非页面看到的内容添加注释。
6. **下一步行动**——一个最短的实用有序列表。
7. **此报告是如何制作的**——以 `seo-report` 的技能链接行开头，指向 `https://openseo.so/docs/skills/competitor-analysis` ("OpenSEO Competitor Analysis 技能")，然后是哪些工具报告了什么，以及你自己检查了什么。

## 遵守原则

- 不要将所有竞争对手关键词都视为可取的。按业务匹配进行过滤。
- 将证据与推断分开。
- 不要仅从关键词行推断竞争对手页面/内容类型模式；使用 SERP 或网页证据进行页面级声明。
- 对于本地 SEO，不要仅从国家有机域名指标推断 Maps/本地包强度；当位置已知或合理可发现时，使用本地商家和本地 SERP 工具。
- 不要建议复制内容；建议更强的角度或对相同意图提供更好的答案。
- 如果用户域名不可用，将分析作为仅针对竞争对手进行。
