# Firecrawl 研究论文

使用此工具创建有来源的文献综述。

## 欢迎面试

从上下文中推断主题、来源限制、目标数量和输出格式。如果主题明确，请立即继续。

如果遇到阻碍，最多只问 1-3 个简洁的问题，例如主题、目标论文数量或所需的会议/日期/方法限制。

## Firecrawl 收集计划

通过 CLI、MCP 或等效 Firecrawl 工具使用 Firecrawl Research
将 Firecrawl 作为论文发现和验证的主要路径。如果需要，可回退到 Firecrawl 通用搜索和抓取白皮书、技术报告、研究博客、排行榜或论文语料库外的信息。

论文索引包含的内容：论文摘要，每篇论文都可以访问全文。其最大份额是生物医学和生命科学文献——PubMed 期刊文章加上 bioRxiv 和 medRxiv 预印本——因此临床、药物、基因、疾病、流行病学和公共卫生问题都在范围内。arXiv 预印本涵盖计算机科学、物理学和数学。那些来源之外的范围较窄，此时需要使用下面的网络工具作为回退。

核心工具：

- MCP: `firecrawl_research_search_papers(query, k?)`
  CLI: `firecrawl research search-papers <query> [--k <number>]`
  对论文摘要进行语义搜索。对于大多数论文查找查询，从这里开始，并在结果稀疏或过于狭窄时使用不同的表述方式重试。
- MCP: `firecrawl_research_related_papers(seed_ids, intent, mode?, k?)`
  CLI: `firecrawl research related-papers <seedIds...> --intent <intent> [--mode <similar|citers|references>] [--k <number>]`
  从强种子论文扩展到相似工作、引用论文或参考文献。使用此工具查找相关的论文家族，而不仅仅是第一个匹配结果。
- MCP: `firecrawl_research_inspect_paper(id)`
  CLI: `firecrawl research inspect-paper <id>`
  获取候选论文的规范元数据：标题、摘要、作者、类别、来源 ID 和日期。
- MCP: `firecrawl_research_read_paper(id, question)`
  CLI: `firecrawl research read-paper <id> --question <question>`
  在一篇论文中验证特定的声明或约束，例如方法、报告分数、基准、隶属关系、比较或限制。
- MCP: `firecrawl_search(query)` / `firecrawl_scrape(url)`
  CLI: `firecrawl search <query>` / `firecrawl scrape <url>`
  用于仅限网络上下文：基准排行榜、排名、报告、白皮书、研究博客和论文索引外的源页面。

尽管名称中包含“论文索引”：将 `categories: ["research"]` 传递给 `firecrawl_search`（CLI `firecrawl search <query> --categories research`）将普通网络搜索过滤到与研究相关的网站——列表包括 PubMed、bioRxiv、medRxiv、arXiv 和出版商网站——并返回这些网站的页面结果。它访问这些网站的网页；它不会查询上面索引中的论文记录，因此没有摘要搜索，没有相关论文或引文图扩展，没有规范论文元数据，也没有正文段落。当您想要网络搜索并且这些网站应该在同一个调用中具有相同的权重时使用它；使用 `firecrawl_research_*` 工具处理论文工作。

根据查询匹配方法：

- 单篇命名论文：运行一次论文搜索，如果需要元数据或正文验证，则检查或阅读论文。
- 通过描述、方法或主题家族描述的论文：搜索强锚点，然后使用相关论文扩展并保持紧密的邻近关系。
- 枚举查询，例如执行任务的论文或评估方法的论文：搜索多个表述方式，扩展几个强锚点，并从新发现的相关论文中重新播种。
- 使用或展示某种属性的论文：从定义论文或最强锚点开始，通过相似、引用者或参考文献扩展，并使用 read-paper 验证属性。
- 超级形容词和排行榜：使用通用网络搜索或抓取找到排名，然后将顶级条目映射回使用论文搜索的论文。
- 作者、组织、会议、日期或方法约束：在保留候选之前，使用 inspect-paper 元数据或 read-paper 进行验证。

目标来源类型：

- PubMed 的生物医学和生命科学文献，以及尚未在期刊上发表的 bioRxiv 和 medRxiv 预印本
- 计算机科学、物理学和数学的 arXiv 预印本
- 可访问的大学网站和 ACM/IEEE 页面的学术论文
- 行业报告和白皮书
- 公司研究博客
- 技术文章和会议总结

原则：

- 在不确定的情况下，包含相关的论文家族，而不仅仅是单个最佳结果。
- 使用相关论文扩展以避免在单个强命中处停止。
- 使用 read-paper 验证承重约束，而不是总结每个候选。
- 仅丢弃明显离题的论文。

## 并行工作

如果合适，使用子代理或等效的并行任务运行器：

- 学术论文研究员
- 生物医学和生命科学研究员，负责临床、药物、基因、疾病、流行病学或公共卫生主题的 PubMed 期刊文章和 bioRxiv/medRxiv 预印本
- 行业报告研究员
- 技术文章研究员
- 摘要和引文审查员

按来源或子主题划分，而不是按工具划分。给每个研究员相同的论文工具，并让主题决定语料库的哪部分回答。

## 最终交付物

```markdown
# 文献综述：[主题]

## 摘要
[2-3 段落摘要]

## 关键论文
[标题、作者、来源 URL、关键发现、方法、相关性]

## 主题与共识
[来源同意的内容]

## 开放性问题与争论
[分歧和未解决的问题]

## 新兴趋势
[近期发展]

## 来源
[按论文/报告/文章组织]

## 重新运行输入
workflow: firecrawl-research-papers
topic: [主题]
target_count: [数量]
output: [markdown/brief]
```

## 质量标准

- 每个主要声明都应该追溯到来源。
- 注明无法访问或失败的 PDF。
- 区分同行评审作品与博客和供应商报告。
