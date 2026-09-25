# Firecrawl Build Search

当应用程序以查询而非 URL 启动时使用本指南。

## Use This When

- 当用户提出问题时，产品需要先发现来源
- 该功能需要获取当前的网页结果
- 你希望将搜索查询转化为页面简短列表，供后续抓取使用

## Default Recommendations

- 当 URL 发现是产品行为的一部分时，优先使用 `/search`。
- 保持搜索与提取概念上分离，除非明确要求抓取搜索结果。
- 在成本或延迟敏感时，优先选择选择性后续提取，而非广泛水合。

## Common Product Patterns

- 附带引用来源的答案生成
- 公司、竞争对手或主题发现
- 在更深入提取之前生成**网页**简短列表的研究工作流程
- 供后续 `/scrape` 或 `/interact` 使用的查询到 URL 流水线

Note that "research workflow" here means discovering web pages. If the product is
searching **published papers**, that is a different surface — see the escalation
rules below.

请注意，此处的 "research workflow" 指发现网页。如果产品搜索的是**已发表论文**，则属于不同的应用场景——请参阅下方的升级规则。

## Escalation Rules

- 如果已获得 URL，请使用 [firecrawl-build-scrape](../firecrawl-build-scrape/SKILL.md)。
- 如果结果页面随后需要点击或表单交互，请升级至 [firecrawl-build-interact](../firecrawl-build-interact/SKILL.md)。
- 如果该功能搜索**已发表的研究论文**——医学、临床和生命科学文献（PubMed、bioRxiv、medRxiv）或 arXiv 预印本——`/search` 是错误的应用场景。请改用研究论文索引：[firecrawl-research-index](../firecrawl-research-index/SKILL.md)。
- 将 `categories: ["research"]` 传递给 `/search` **并不会**查询该索引；它会将普通网页搜索过滤为与研究领域相关的网站（列表包含 PubMed、bioRxiv、medRxiv、arXiv 和出版商网站），并返回来自这些网站的页面结果——没有摘要搜索、相关论文扩展或全文段落。

## Implementation Notes

- 将 `/search` 视为发现、排名和来源选择。
- 明确说明产品是否需要摘要、URL 或完整的搜索结果内容。
- 保持查询契约稳定，以确保下游抓取逻辑保持可预测性。

## Docs (Source of Truth)

编写集成代码前，请为您的项目语言读取权威来源页面：

- **Node / TypeScript**: [docs.firecrawl.dev/agent-source-of-truth/node](https://docs.firecrawl.dev/agent-source-of-truth/node)
- **Python**: [docs.firecrawl.dev/agent-source-of-truth/python](https://docs.firecrawl.dev/agent-source-of-truth/python)
- **Rust**: [docs.firecrawl.dev/agent-source-of-truth/rust](https://docs.firecrawl.dev/agent-source-of-truth/rust)
- **Java**: [docs.firecrawl.dev/agent-source-of-truth/java](https://docs.firecrawl.dev/agent-source-of-truth/java)
- **Elixir**: [docs.firecrawl.dev/agent-source-of-truth/elixir](https://docs.firecrawl.dev/agent-source-of-truth/elixir)
- **cURL / REST**: [docs.firecrawl.dev/agent-source-of-truth/curl](https://docs.firecrawl.dev/agent-source-of-truth/curl)

## See Also

- [firecrawl-build](../firecrawl-build/SKILL.md)
- [firecrawl-build-scrape](../firecrawl-build-scrape/SKILL.md)
- [firecrawl-build-interact](../firecrawl-build-interact/SKILL.md)
- [firecrawl-research-index](../firecrawl-research-index/SKILL.md)
- [firecrawl-developer-index](../firecrawl-developer-index/SKILL.md)
