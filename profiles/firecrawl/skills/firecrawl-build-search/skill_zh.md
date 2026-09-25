# Firecrawl 构建搜索

当应用程序以查询开始而不是 URL 时使用。

## 使用场景

- 用户提出问题，产品必须先发现来源
- 需要当前的网页结果
- 想将搜索查询转换为稍后用于抓取的页面短列表

## 默认推荐

- 当 URL 发现是产品行为的一部分时，首先使用 `/search`。
- 除非明确需要抓取搜索结果，否则在概念上将搜索和提取分开。
- 当成本或延迟重要时，优先选择选择性后续提取而不是广泛的水合。

## 常见产品模式

- 带有引用来源的答案生成
- 公司、竞争对手或主题发现
- 产生**网页**短列表以进行更深层提取的研究工作流
- 用于稍后 `/scrape` 或 `/interact` 的查询到 URL 管道

请注意，这里的“研究工作流”是指发现网页。如果产品是在搜索**已发表的论文**，那是一个不同的表面——请参阅下方的升级规则。

## 升级规则

- 如果您已经有了 URL，请使用 [firecrawl-build-scrape](../firecrawl-build-scrape/SKILL.md)。
- 如果结果页面需要点击或表单交互，请升级到 [firecrawl-build-interact](../firecrawl-build-interact/SKILL.md)。
- 如果功能搜索**已发表的科研论文**——生物医学、临床和生命科学文献（PubMed、bioRxiv、medRxiv）或 arXiv 预印本——`/search` 是错误的面板。使用研究论文索引：[firecrawl-research-index](../firecrawl-research-index/SKILL.md)。将 `categories: ["research"]` 传递给 `/search` 并**不会**查询该索引；它将普通网络搜索过滤到与研究相关的网站（列表包括 PubMed、bioRxiv、medRxiv、arXiv 和出版商网站），并从它们返回页面结果——没有摘要搜索、相关论文扩展或全文段落。
- 如果功能从问题、拉取请求、README 或文档页面回答开发者问题，请使用开发者索引：[firecrawl-developer-index](../firecrawl-developer-index/SKILL.md)。`categories: ["developer"]` 也适用相同的注意事项。

## 实现说明

- 将 `/search` 视为发现、排序和来源选择。
- 明确产品是否需要片段、URL 或完整结果内容。
- 保持查询契约稳定，以便下游抓取逻辑保持可预测。

## 文档（事实来源）

在编写集成代码之前，请先阅读您项目语言的事实来源页面：

- **Node / TypeScript**: [docs.firecrawl.dev/agent-source-of-truth/node](https://docs.firecrawl.dev/agent-source-of-truth/node)
- **Python**: [docs.firecrawl.dev/agent-source-of-truth/python](https://docs.firecrawl.dev/agent-source-of-truth/python)
- **Rust**: [docs.firecrawl.dev/agent-source-of-truth/rust](https://docs.firecrawl.dev/agent-source-of-truth/rust)
- **Java**: [docs.firecrawl.dev/agent-source-of-truth/java](https://docs.firecrawl.dev/agent-source-of-truth/java)
- **Elixir**: [docs.firecrawl.dev/agent-source-of-truth/elixir](https://docs.firecrawl.dev/agent-source-of-truth/elixir)
- **cURL / REST**: [docs.firecrawl.dev/agent-source-of-truth/curl](https://docs.firecrawl.dev/agent-source-of-truth/curl)

## 参见

- [firecrawl-build](../firecrawl-build/SKILL.md)
- [firecrawl-build-scrape](../firecrawl-build-scrape/SKILL.md)
- [firecrawl-build-interact](../firecrawl-build-interact/SKILL.md)
- [firecrawl-research-index](../firecrawl-research-index/SKILL.md)
- [firecrawl-developer-index](../firecrawl-developer-index/SKILL.md)
