# Asta MCP — 学术论文搜索

Asta是Ai2的科学语料库工具，通过MCP（流式HTTP传输）暴露了Semantic Scholar学术图谱。这项技能告诉代理**应该为哪个意图调用哪个Asta工具**，以及如何将它们组合成有用的工作流。

- **MCP端点**：`https://asta-tools.allen.ai/mcp/v1`
- **认证**：`x-api-key`请求头（请求密钥位于 <https://share.hsforms.com/1L4hUh20oT3mu8iXJQMV77w3ioxm>）
- **传输**：流式HTTP

## 前置条件检查

在调用任何工具之前，请验证Asta MCP服务器是否已在主机代理中注册。工具名称将以安装时选择的MCP服务器名称为前缀（通常为 `asta__<工具>` 或 `mcp__asta__<工具>`）。

如果没有可见的Asta工具，请**不要**进行原始HTTP调用或编造结果。请告知用户将 `https://asta-tools.allen.ai/mcp/v1` 注册为流式HTTP MCP服务器，并带有 `x-api-key` 请求头，然后重新启动/重新加载主机。最小化设置提示：

- Codex CLI：将 `[mcp_servers.asta] url = "https://asta-tools.allen.ai/mcp/v1"` 和 `env_http_headers = { "x-api-key" = "ASTA_API_KEY" }` 添加到 `~/.codex/config.toml`。
- Claude Code：运行 `claude mcp add -t http -s user asta https://asta-tools.allen.ai/mcp/v1 -H "x-api-key: $ASTA_API_KEY"`。
- 通用MCP客户端：配置服务器URL `https://asta-tools.allen.ai/mcp/v1` 并带有请求头 `{ "x-api-key": "<YOUR_API_KEY>" }`。

## 工具映射 — 意图 → Asta工具

| 用户意图 | Asta工具 | 备注 |
| --- | --- | --- |
| 广泛主题搜索 | `search_papers_by_relevance` | 支持场馆+日期过滤器 |
| 已知论文标题 | `search_paper_by_title` | 可选 `venues` + `publication_date_range` 过滤器 |
| 已知DOI / arXiv / PMID / CorpusId / MAG / ACL / SHA / URL | `get_paper` | 单篇论文查询 |
| 同时查询多个已知ID | `get_paper_batch` | 批量查询 — 将 `ids` 作为 **JSON数组** 传递（不是逗号分隔的字符串，与 `snippet_search` 的 `paper_ids` 不同）；优先于N个连续的 `get_paper` 调用；无法解析的ID将静默丢弃（不返回null/错误），因此请将返回的 `paperId` 与您的输入进行核对 |
| 论文X被谁引用 | `get_citations` | 前向引用，分页；接受 `publication_date_range` 但**不**接受 `venues`；`limit` 默认为 100 |
| 通过姓名查找作者 | `search_authors_by_name` | 默认 `fields="name"` 仅返回 `name` + `authorId` — **明确请求** `affiliations,paperCount,citationCount,hIndex,externalIds` 以获取可排序的内容；`externalIds` 包含 ORCID/DBLP (`url`/`homepage` 也可选择) |
| 作者的出版物 | `get_author_papers` | 传递作者ID；字段参数是 **`paper_fields`**（不是 `fields`）；`limit` 默认为 **1000** — 请明确设置它 |
| 查找提及X的段落 | `snippet_search` | 约500字的摘录（标题/摘要/正文，不包括标题和参考文献）；见下文的片段特定参数 |

大多数搜索/引用工具接受 **`publication_date_range`**（格式 `YYYY-MM-DD:YYYY-MM-DD`；年份简写如 `"2021:"`，`":2015-01"`，`"2015:2020"` 也被接受），**`venues`**，以及 **`fields`** 用于字段选择 — 当用户的意图限制范围时（例如，“最近的”、“自2022年以来”、“在NeurIPS”），请传递它们。`venues` 匹配Semantic Scholar的**精确**场馆字符串（逗号分隔，例如 `"Nature,N. Engl. J. Med."`）；像“NeurIPS”这样的非正式名称可能无法匹配，因此当场馆查询返回空时，请回退到日期/关键字过滤器。

**每个工具的参数例外**（与实时服务器验证 — 错误的参数会导致格式错误或静默忽略的参数）：

- `get_author_papers` 将其字段选择参数命名为 **`paper_fields`**，而不是 `fields`（传递 `fields=` 会被静默忽略 — 您将只获得标题），并接受 `publication_date_range` 但**不**接受 `venues` 过滤器。其日期过滤器在分页后应用，可能会丢弃有效范围内的论文（一个知名作者的 `2024:2024` 返回 `[]`），因此请在工作流程中通过主题/场馆**和日期**进行客户端过滤以获得可靠结果。
- `get_citations` 接受 `publication_date_range` 但**不**接受 `venues`。
- `snippet_search` 接受**既** `fields` 也**不** `publication_date_range`。相反，它有：**`inserted_before`**（日期过滤器，`YYYY-MM-DD`/`YYYY-MM`/`YYYY`），**`paper_ids`**（最多100个ID的逗号分隔列表，以限制摘录到特定论文），以及 `venues`。

### ⚠️ `fields` 参数 — 避免上下文爆炸

`get_paper` / `get_paper_batch` 接受一个 `fields` 字符串。**切勿通过 `fields` 请求 `citations` 或 `references`** — 一个高度引用的论文（例如 *Attention Is All You Need*）将返回 200k+ 字符，并会溢出代理的上下文窗口。使用专用的 `get_citations` 工具获取前向引用（它分页）。Asta不提供专用的 `get_references` 工具 — 要检索论文的参考文献列表，请仅对您知道具有较小参考文献列表的论文（通常 < 100）使用 `get_paper` 并设置 `fields=references`。

**也要注意行数**，而不仅仅是每行的大小：默认 `limit` 很大 — `get_author_papers` 返回最多 **1000**，`get_citations` **100**，`search_papers_by_relevance` **50**，而 `snippet_search` **20**（每个摘录约500字，使其成为每行最重的工具）。传递一个明确的较小 `limit` — 例如，20–50用于论文/引用列表，~5–10用于摘录 — 除非用户要求完整列表。

使用特定任务的字段预设：

元数据查找：

```
title,year,authors,venue,tldr,url,abstract
```

搜索/排名/结果表格：

```
title,year,authors,venue,tldr,url,abstract,citationCount,influentialCitationCount
```

DOI/导出交接：

```
title,year,authors,venue,tldr,url,externalIds
```

仅在需要时添加 `journal`, `publicationDate`, `fieldsOfStudy`, `isOpenAccess`。如果未来响应中缺少传递性字段（如 `citationCount`），请优雅降级：按相关性/时效性排序并省略基于引用的声明。

**示例调用**（主题搜索，按引用排名，DOI暴露以供下游获取）：

```
search_papers_by_relevance(
  keyword="mixture of experts routing",
  publication_date_range="2023:",
  fields="title,year,authors,venue,tldr,url,externalIds,citationCount",
  limit=20,
)
```

### 获取DOI / 外部ID（未记录但受支持）

Asta的官方 `fields` 列表**不包括** `externalIds`，但该字段会透明地传递给底层的Semantic Scholar API，并且在实践中有效。将 `externalIds` 添加到 `fields` 以检索 `DOI`，`PubMed`，`PubMedCentral`，`ArXiv`，`MAG`，`DBLP`，`CorpusId`。相同的传递机制适用于 **`citationCount`** 和 **`influentialCitationCount`**（它们也未被官方列表包含，但经验证会返回）— 当按引用排名结果时请求它们。注意事项：

- 并非所有论文都有DOI — 纯粹的arXiv预印本通常只返回 `ArXiv` + `CorpusId`。
- `get_paper("DOI:...")` 查询并不总是可靠；一些有效的DOI返回 `not found`。最好先通过标题搜索，然后从结果中读取 `externalIds`。
- 由于这是未记录的，请将其视为尽力而为，如果未来的Asta版本删除它，请优雅降级。

## 工作流模式

### 模式1 — 主题发现

1. `search_papers_by_relevance(keyword, publication_date_range="<current_year-5>:", venues=?, fields="title,year,authors,venue,tldr,url,abstract,citationCount,influentialCitationCount", limit=20)` → 初始命中（从今天的日期计算下限 — 例如，在2026年传递 `publication_date_range="2021:"`；如果用户要求旧工作，请调整或删除过滤器）
2. 按引用数+时效性对前N名进行排名/展示
3. 提供后续操作：对最有影响力的 `get_citations`，或 `snippet_search` 用于特定主张

### 模式2 — 种子论文扩展

1. `get_paper(DOI|arXiv|...)` → 验证种子
2. `get_citations(paperId)` → 前向扩展
3. 可选地使用种子标题术语运行 `search_papers_by_relevance` 以进行横向发现
4. 在展示前按 `paperId` 去重

### 模式3 — 作者深入挖掘

1. `search_authors_by_name(name, fields="name,affiliations,paperCount,citationCount,hIndex,externalIds")` → 选择正确的个人资料。**你必须请求这些字段** — 默认的 `fields="name"` 仅返回 `name` + `authorId`，留下无内容可供排序。当存在时，通过 `externalIds.ORCID` 消歧（最强信号），然后是 `paperCount`/`citationCount`/`hIndex`；`affiliations` 即使请求也可能为空，因此仅将其用作平局判据
2. `get_author_papers(authorId, limit=50, paper_fields="title,year,authors,venue,tldr,url,abstract,citationCount")` → 一个有界的首页；如果用户要求完整列表，请仅在此之后扩展
3. 客户端通过主题关键字或日期进行过滤

### 模式4 — 证据检索

1. `snippet_search(claim_query)` → 查找支持主张的段落
2. 要在特定论文**内**验证主张，请传递 `paper_ids="<id1>,<id2>,…"`（≤100），以便摘录仅从该集合中获取
3. 对于每个命中，可选地 `get_paper(id)` 获取完整元数据

## 输出与交互规则

- 始终报告**使用的工具**。仅在工具暴露总数时才报告总数；否则报告返回计数/页面大小，不要暗示语料库范围的总数。
- 最多展示10个结果作为表格（标题、年份、场馆、引用数（如果获取）），然后展示最相关的详细信息。
- 如果用户使用中文，请用中文展示摘要；保持标题为原始语言。
- 结果后，提供：**详情 / 精炼 / 引用 / 摘录 / 导出 / 完成**。

## 关键规则

- **优先批量意图而非 ping-pong**。如果用户的问题需要两个独立的查询，请在一个回合中并行发出MCP工具调用，而不是顺序发出。
- **切勿猜测ID**。如果用户给出模糊的标题，请先使用 `search_paper_by_title` 再使用 `get_paper`。
- **尊重速率限制**。API密钥可购买更高的限制，但不是无限制的 — 停止扩展引用图，超出用户要求的内容。
- **不要编造字段**。如果Asta返回 null `abstract` 或 `venue`，请说明情况，而不是编造。

## 处理Asta响应

| 情况 | 应该做什么 |
| --- | --- |
| 空的 `abstract` | 并非所有语料库论文都有全文 — 使用 `snippet_search`，或回退到标题 + TLDR |
| 作者消歧不确定 | 预先请求排名字段（见模式3 — 它们**不是**默认返回的）；优先 `externalIds.ORCID`，然后 `paperCount`/`citationCount`/`hIndex`，`affiliations` 仅作为平局判据 |
| 日期过滤结果 | `publication_date_range` 过滤器可能返回 `publicationDate` 为 `null` 的记录（只有 `year` 是保证的），并且未知日期的论文被视为在其年份的1月1日发表 — 因此边界年份过滤是近似的 |
| `429 Too Many Requests` | 后退；使用 `get_paper_batch` 而不是顺序的 `get_paper` 调用进行批量处理 |
| 需要 DOI / PubMed ID / arXiv ID | 将 `externalIds` 添加到 `fields`（见上文的“获取DOI”）；当 `DOI` 缺失时回退到 `ArXiv` ID |
