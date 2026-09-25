# Firecrawl 研究索引

查找回答研究查询的研究论文。有些问题只有一个答案；许多问题有多个答案——当不确定时，倾向于返回更完整的相关集（按相关性排序）而不是缩小到单一答案。读者看到相邻的方法和论文比无声地删除它们更有帮助。

## 索引中包含的内容

论文摘要，每篇论文都可以访问完整文本。语料库的大部分是**生物医学和生命科学**文献——**PubMed**期刊文章加上**bioRxiv**和**medRxiv**预印本——因此临床、药物、基因、疾病、流行病学和公共卫生问题都在范围内。**arXiv**预印本涵盖计算机科学、物理学和数学。那些来源之外的范围较薄：只有出版商付费墙或在小众场所存在的论文可能不会被索引，当这种情况发生时，下面的通用网络工具是备用方案。

没有**固定的公式**。阅读查询，决定它的类型，然后选择下面的方法。有些查询只需要一次搜索；其他查询需要重重的结构/语义扩展。不要运行查询不要求的机器。

## 工具及其独特优势

- MCP: **`firecrawl_research_search_papers(query, k?)`**
  CLI: **`firecrawl research search-papers <query> [--k <number>]`**
  基于摘要的语义搜索。对于几乎任何查询，这是自然的第一步。
  如果结果看起来很稀少或都相似，用不同的表述（兄弟领域、竞争方法、数据集/基准名称）重新运行，而不是放弃。

- MCP: **`firecrawl_research_related_papers(seed_ids, intent, mode?, k?)`**
  CLI: **`firecrawl research related-papers <seedIds...> --intent <intent> [--mode <similar|citers|references>] [--k <number>]`**
  语义和结构扩展，按您的`intent`排序。
  这触及语义搜索无法到达的论文，并且是将一个良好命中转变为完整集合的方法。
  `mode=similar` → 小众兄弟；`citers` → 谁使用/构建在种子上；`references` → 他们构建在/比较的对象。

- MCP: **`firecrawl_research_inspect_paper(id)`**
  CLI: **`firecrawl research inspect-paper <id>`**
  **单个**论文的规范元数据：标题、摘要、作者、类别、来源ID和日期。
  在`search_papers`或`related_papers`之后使用它，当您需要候选者的完整引用/元数据，或者当您从其他地方获得ID并需要确认它解析为哪篇论文时。
  这**不**读取论文正文；使用`read_paper`回答特定的全文问题。

- MCP: **`firecrawl_research_read_paper(id, question)`**
  CLI: **`firecrawl research read-paper <id> --question <question>`**
  **单个**论文的正文段落，以验证承重约束（实际使用的方法、实际报告的分数、隶属关系、论文比较的对象）。
  使用它来解决具体的疑问，而不是在所有内容上使用。

- MCP: **`firecrawl_search(query, categories: ["research"])`**
  CLI: **`firecrawl search <query> --categories research`**
  **不是这个索引**。这是一个_网站_过滤器：它将正常网络搜索限制到一组研究相关的域名——列表中包括`pubmed.ncbi.nlm.nih.gov`、`biorxiv.org`、`medrxiv.org`和`arxiv.org`以及出版商网站——并返回页面结果在`research`组旁边`web`，每个都有`url`、`title`、`description`（匹配的段落）、`position`和`category: "research"`——网络结果没有`category`，因此当合并时，该字段是关键。
  所以它触及那些网站的**网页**；它所做的不是查询它们的**论文记录**在这个索引中——没有对摘要的语义搜索，没有引文图或相关论文扩展，没有规范论文元数据，也没有正文段落。结果是普通的网络结果。
  当您**已经**运行网络搜索并希望这些网站在相同的调用中具有相同权重时使用它。对于任何实际上是查找论文的任务，使用`firecrawl_research_search_papers`及其上面的兄弟工具。

- MCP: **`firecrawl_search(query)` / `firecrawl_scrape(url)`**
  CLI: **`firecrawl search <query>` / `firecrawl scrape <url>`**
  通用**网络**搜索和页面获取，用于不在论文摘要中存在的事实：基准**排行榜**、排名，“谁得分最高/最大/最常用”。
  在网络上找到排名，然后使用`search_papers`将顶级条目映射回论文。
  只有当语料库无法自行回答问题时才使用这些。

## 将方法与查询匹配

- **单个_命名_论文**（“Qwen3报告”）→ 一个`search_papers`，完成。这是唯一真正需要单个论文的情况。
- **按描述/方法或技术查找论文**（“引入X的论文”、“训练无关的AI文本N-gram检测”）→ 找到最佳匹配，然后假设有一个_系列_：使用`related_papers`扩展，并**包括密切相关的方法/论文**。即使一个论文是确切的字面匹配，也要展示并保留它的邻居——不要缩小到单个最佳命中并推断其余部分。只有当查询命名特定论文时才将其视为一个答案。
- **列举/方法系列**（“执行X的论文”、“Adam的替代方案”、“Y的基准”）→ 答案是一个_集合_，这是`related_papers`发挥作用的地方：使用`mode=similar`扩展几个强锚点，重新从新的强命中重新播种。这里一次搜索永远不够。
- **展示**（“使用/展示属性P的论文”）→ 相关论文应用P，但它们的摘要可能不会描述它。通过`citers`/`references`从P的定义论文向外扩展，并使用`read_paper`确认候选者实际上使用P。
- **超级/排行榜**（“在基准X上表现最佳”、“最大”、“最受欢迎”）→ 排名存在于**排行榜/网络上**，而不是任何单个摘要中。使用`firecrawl_search` / `firecrawl_scrape`找到基准的排行榜或排名，读出顶级模型/论文，然后对每个使用`search_papers`获取其论文。作为备用方案，搜索基准并`read_paper`候选者以报告的数字。最难——广泛撒网。
- **组织/作者过滤**（“来自\<组织\>”、“由\<作者\>”）→ 主题匹配不够；在保留论文之前，验证隶属关系/作者身份（元数据或`read_paper`）。
- **比较对象**（“论文X基准针对/基于什么”）→ 答案在论文X内部：`read_paper(X, ...)`或`related_papers([X], ..., mode="references")`。

## 原则

- **两个不同的功能共享“研究”一词**。论文索引是`firecrawl_research_*` / `firecrawl research`。`firecrawl_search`上的`categories: ["research"]`选项是一个网站过滤器——它确实将网络搜索指向PubMed、bioRxiv、medRxiv、arXiv和出版商网站，但返回的是它们的网页，而不是论文记录。如果一个任务是关于查找论文的，那么这个技能中的工具是读取语料库的工具；选择`categories: ["research"]`将安静地回答一个不同的问题。
- **查询形状和主题字段是分开的**。临床试验问题和机器学习问题采用上述相同的形状；不同之处仅在于命中来自哪个来源。不要假设将生物医学或生命科学查询发送到开放网络，因为语料库仅限于arXiv——PubMed、bioRxiv和medRxiv是`search_papers`读取的最大部分。
- **当不确定时，包含**。对于任何主题/方法/比较问题，返回相关的_系列_，而不仅仅是单个最佳匹配——倾向于保留一个可能相关的论文而不是删除它。相邻的方法是良好答案的一部分；不要因为一个论文是最确切的匹配就推断其余部分。只有当查询命名特定论文时才将其视为一个答案。
- **遵循文献，并保留您找到的内容**。开创性来源、竞争方法、密切的邻居通常是一步之遥——使用`related_papers`，并_包含_它们，而不仅仅是第一个命中。停留在一个好结果是让读者只得到半个答案的最常见方式。
- **验证以排除，而不是以限制**。使用`read_paper`在硬约束明显失败时排除论文（错误的组织/作者、实际上没有报告分数）。当一个论文可能相关时，倾向于保留它而不是要求证明。
- **只排除明显不相关的**。不要用您确信无关的论文来填充——但这是一个高门槛；大多数可能相关的作品都应该入选。

## 参见

- [firecrawl-build-search](https://github.com/firecrawl/skills/tree/main/skills/build/firecrawl-build-search) — 将论文索引构建到应用程序中而不是在这里查询
