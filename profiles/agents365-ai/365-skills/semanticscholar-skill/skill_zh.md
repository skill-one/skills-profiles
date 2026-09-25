# Semantic Scholar 搜索工作流

使用 Semantic Scholar API 通过结构化的四阶段工作流搜索学术论文。

**关键规则：** 绝对不要对 API 请求进行多个连续的 Bash 调用。始终编写一个 Python 脚本，该脚本运行所有搜索，然后执行一次。所有速率限制都在 `s2.py` 内部自动处理。

## 第一阶段：理解与规划

解析用户的意图并选择搜索策略：

### 决策树

> **默认使用 `search_bulk()`。** 根据 Semantic Scholar 自己的文档，对于大多数情况，批量搜索优先于相关性搜索，因为相关性搜索更耗费资源。仅在您需要 TLDR 字段或内联作者/引用详细信息时使用 `search_relevance()`。

| 用户想要... | 策略 | 函数 |
| --------------- | ---------- | ---------- |
| 广泛的主题探索 | 批量搜索（首选） | `search_bulk()` 与 `build_bool_query()` |
| 需要 TLDR / 内联作者详细信息 | 相关性搜索 | `search_relevance()` |
| 精确的技术术语、确切短语 | 批量搜索使用布尔运算符 | `search_bulk()` 与 `build_bool_query()` |
| 特定段落或方法 | 段落搜索 | `search_snippets()` |
| 通过标题了解的论文 | 标题匹配 | `match_title()` |
| 通过 DOI/PMID/ArXiv 了解的论文 | 直接查找 | `get_paper()` |
| 引用已知作品的论文 | 引用遍历 | `get_citations()` |
| 与一篇论文相关 | 单一种子推荐 | `find_similar()` |
| 与多篇论文相关 | 多种子推荐 | `recommend()` |
| 查找研究人员 | 作者搜索 | `search_authors()` |
| 研究人员的个人资料 | 作者详细信息 | `get_author()` |
| 研究人员的出版物 | 作者论文 | `get_author_papers()` |

### 查询构造规则

- **模糊术语**（例如，“干细胞”可能意味着间充质或干细胞样 T 细胞）：使用 `build_bool_query()` 与确切短语和排除项
  - 示例：`build_bool_query(phrases=["干细胞样 T 细胞"], required=["CD4", "TCF7"], excluded=["间充质", "造血干细胞"])`
- **多上下文查询**（例如，“癌症中的主题 X 与自身免疫性疾病”）：规划单独的搜索，使用 `deduplicate()` 进行去重
- **广泛主题**：使用 `search_relevance()` 并带过滤器（年份、会议、研究领域、最小引用计数）

### 规划过滤器

| 过滤器 | 使用场景 |
| -------- | ---------- |
| `year="2020-"` | 仅限近期工作 |
| `publication_date="2024-01-01:2024-06-30"` | 精确日期范围 (YYYY-MM-DD) |
| `fields_of_study="医学"` | 限制到领域 |
| `min_citations=10` | 仅限知名论文 |
| `pub_types="综述"` | 查找综述/元分析 |
| `pub_types="临床试验"` | 仅限临床试验 |
| `open_access=True` | 仅限开放获取论文 |

**检查点：** 在继续之前，请验证：(1) 搜索策略与用户意图匹配，(2) 过滤器适当，(3) 查询足够具体以避免不相关结果。

## 第二阶段：执行搜索

编写一个 Python 脚本，该脚本以**标准前导程序**开头，然后运行所有搜索：

```python
# --- 标准前导程序（每个脚本使用） ---
import sys, os, glob
_candidates = [
    os.path.expanduser("~/.claude/skills/semanticscholar-skill"),
    os.path.expanduser("~/.openclaw/skills/semanticscholar-skill"),
    *glob.glob(os.path.expanduser("~/.claude/plugins/**/semanticscholar-skill"), recursive=True),
    *glob.glob(os.path.expanduser("~/.codex/skills/semanticscholar-skill")),
    ".",
]
SKILL_DIR = next((p for p in _candidates if os.path.isfile(os.path.join(p, "s2.py"))), None)
if SKILL_DIR is None:
    raise RuntimeError("无法定位 semanticallycholar-skill (未找到 s2.py)")
sys.path.insert(0, SKILL_DIR)
from s2 import *
# --- 前导程序结束 ---

# 构建精确查询
q = build_bool_query(
    phrases=["干细胞样 T 细胞"],
    required=["CD4", "IBD"],
    excluded=["间充质"]
)
papers = search_bulk(q, max_results=30, year="2018-", fields_of_study="医学")
papers = deduplicate(papers)

print(format_results(papers, "干细胞样 CD4 T 细胞在 IBD 中"))
```

保存到 `/tmp/s2_search.py`，然后在单个 Bash 调用中使用 `python3 /tmp/s2_search.py` 运行。速率限制、重试和退避都在 `s2.py` 内部自动处理。

**没有 API 密钥：** 该技能在没有 `S2_API_KEY` 的情况下也能工作。当密钥不存在或无效时，`s2.py` 会自动切换到未身份验证模式（没有 `x-api-key` 头），并将请求间隔放宽到 5 秒。根据 S2 文档，匿名调用共享所有未身份验证用户的全局 1000 req/s 池，并且在高峰使用期间可能会“进一步限制” — 因此保守的 5 秒间隔可以防止高峰使用限制，即使稳态池很慷慨。如果您仍然看到持续的 429 错误，请将 `_MIN_GAP` 提高到 10 秒。保持 `max_results` ≤ 30 每次搜索，并在脚本中组合较少的搜索。S2 建议在每次请求中包含 API 密钥 — 您可以在 <https://www.semanticscholar.org/product/api#api-key-form> 获取密钥。

**检查点：** 验证脚本是否成功运行（没有异常）并返回了结果。如果结果为 0，请放宽查询或放宽过滤器，然后再呈现。

### 示例

以下每个示例都假设脚本顶部有第二阶段的**标准前导程序**。

**示例 1：作者工作流** — “查找 Yann LeCun 关于自监督学习的论文”

```python
authors = search_authors("Yann LeCun", max_results=5)
print(format_authors(authors))

# 使用第一个匹配的 ID 获取他们的论文
author_id = authors[0]["authorId"]
papers = get_author_papers(author_id, max_results=50)
# 本地过滤以查找主题
ssl_papers = [p for p in papers if "自监督" in (p.get("title") or "").lower()]
print(format_results(ssl_papers, "Yann LeCun - 自监督学习"))
```

**示例 2：带意图的引用链** — “谁引用了 Transformer 论文以及他们如何使用它？”

```python
paper = get_paper("DOI:10.48550/arXiv.1706.03762")
print(f"标题: {paper['title']}, 引用次数: {paper['citationCount']}")

# 引用信封包含上下文意图 — 保留它们，不要展平。
citing = get_citations(paper["paperId"], max_results=50)
citing.sort(key=lambda c: (c.get("citingPaper") or {}).get("citationCount", 0), reverse=True)
print(format_citations(citing, max_items=10))  # 渲染意图标签 + 上下文片段
```

**示例 3：多种子推荐与 BibTeX 导出** — “查找这两篇论文类似的论文，但不是关于 NLP 的”

```python
recs = recommend(
    positive_ids=["DOI:10.1038/nature14539", "ARXIV:2010.11929"],
    negative_ids=["ARXIV:1706.03762"],
    limit=20
)
print(format_results(recs, "视觉论文类似于深度学习 & ViT，排除 NLP"))

# 导出 BibTeX 以供前 10 个结果
bib_data = batch_papers([r["paperId"] for r in recs[:10]], fields="title,citationStyles")
print(export_bibtex(bib_data))
```

## 第三阶段：总结与呈现

- 使用 `format_results()` 以一致的输出（摘要表格 + 前 10 个详细信息）
- 如果用户的语言是中文，请用中文呈现摘要
- 始终注明总结果计数和使用的搜索策略
- 根据用户的具体问题突出显示最相关的论文

## 第四阶段：用户交互循环

呈现结果后，**始终提供以下选项：**

1. **翻译** — 标题/摘要翻译成中文（或其他语言）
2. **详细信息** — 特定论文的完整摘要
3. **优化** — 使用不同的术语/过滤器缩小或扩展搜索
4. **类似** — 查找与特定结果相似的论文 (`find_similar()`)
5. **引用** — 查找引用特定论文的人以及他们如何使用 (`get_citations()` + `format_citations()` 用于意图标签)
6. **导出** — 通过 `export_bibtex()`、`export_markdown()` 或 `export_json()` 保存结果
7. **完成** — 结束搜索会话

循环直到用户说完成。每个后续操作都使用相同的单脚本模式。

---

## 其他资源

- **S2folks GitHub** — 官方 Semantic Scholar 代码示例：<https://github.com/allenai/s2-folks>
- **Postman 集合** — 无代码 API 测试：来自 <https://www.semanticscholar.org/product/api/tutorial> 的链接
- **API 文档** — 完整端点参考：<https://api.semanticscholar.org/>

---

## API 快速参考

### 辅助模块 (`s2.py`)

在每個脚本顶部使用第二阶段的**标准前导程序**。然后调用以下任一函数 — 该模块的文档字符串 (`help(s2)` 或阅读 `s2.py`) 列出了每个按阶段分类的简短摘要。

### 论文搜索函数

| 函数 | 目的 | 最大结果 |
| ---------- | --------- | ------------- |
| `search_relevance(query, **filters)` | 简单的广泛搜索 | 1,000 |
| `search_bulk(query, sort=..., **filters)` | 布尔精确搜索 | 10,000,000 |
| `search_snippets(query, paper_ids=, authors=, inserted_before=, **filters)` | 全文段落搜索 | 1,000 |
| `match_title(title)` | 精确标题匹配 | 1 |
| `paper_autocomplete(query)` | 查询完成建议 | — |
| `get_paper(paper_id)` | 单篇论文详细信息 | — |
| `get_citations(paper_id, max_results, publication_date=)` | 谁引用了这篇论文 | 10,000 |
| `get_references(paper_id, max_results)` | 这篇论文引用了什么 | 10,000 |
| `find_similar(paper_id, limit, pool)` | 单种子推荐 | 500 |
| `recommend(positive_ids, negative_ids, limit)` | 多种子推荐 | 500 |
| `batch_papers(ids, fields)` | 批量查找（≤500） | — |

### 作者函数

| 函数 | 目的 | 最大结果 |
| ---------- | --------- | ------------- |
| `search_authors(query, max_results)` | 通过姓名查找研究人员 | 1,000 |
| `get_author(author_id)` | 作者个人资料（隶属关系、h-index） | — |
| `get_author_papers(author_id, max_results, publication_date=)` | 作者的出版物 | 10,000 |
| `get_paper_authors(paper_id, max_results)` | 论文的作者列表 | 1,000 |
| `batch_authors(ids, fields)` | 批量作者查找（≤1000） | — |

### 过滤器参数 (kwargs)

snake_case kwargs 会自动转换为 S2 camelCase 参数 (`fields_of_study` → `fieldsOfStudy`，`min_citations` → `minCitationCount`，`publication_date` → `publicationDateOrYear`，`pub_types` → `publicationTypes`，`open_access` → `openAccessPdf`)。在这里使用 snake_case。

`year`，`publication_date`，`venue`，`fields_of_study`，`min_citations`，`pub_types`，`open_access`

- `year`: `"2020-"`，`"-2019"`，`"2016-2020"`
- `publication_date`: `"2024-01-01:2024-06-30"`（YYYY-MM-DD 范围，开区间 OK）
- `pub_types`: `Review`，`JournalArticle`，`Conference`，`ClinicalTrial`，`MetaAnalysis`，`Dataset`，`Book`，`CaseReport`，`Editorial`，`LettersAndComments`，`News`，`Study`，`BookSection`

### 布尔查询语法（仅限批量搜索）

| 语法 | 示例 | 含义 |
| -------- | --------- | --------- |
| `"..."` | `"深度学习"` | 精确短语 |
| `+` | `+transformer` | 必须包含 |
| `-` | `-survey` | 排除 |
| `\|` | `CNN \| RNN` | 或 |
| `*` | `neuro*` | 前缀通配符 |
| `()` | `(CNN \| RNN) +attention` | 分组 |
| `term~N` | `bugs~3` | 模糊：匹配 N 次编辑内的单词（例如 buggy，buns） |
| `"phrase"~N` | `"blue lake"~3` | 临近：最多 N 个词之间的距离 |
| `fuzzy`: list of `(term, edit_distance)` tuples |
| `proximity`: list of `(phrase, word_distance)` tuples |

使用 `build_bool_query(phrases, required, excluded, or_terms, fuzzy, proximity)` 安全构建。

### 输出函数

| 函数 | 目的 |
| ---------- | --------- |
| `format_table(papers, max_rows=30)` | Markdown 摘要表格 |
| `format_details(papers, max_papers=10)` | 详细条目，带 TLDR/摘要 |
| `format_citations(citations, max_items=10)` | 引用信封，带意图标签 + 上下文片段 |
| `format_results(papers, query_desc)` | 组合：摘要 + 表格 + 详细信息 |
| `format_authors(authors, max_rows=20)` | 作者表格（姓名、隶属关系、h-index） |
| `export_bibtex(papers)` | BibTeX 条目（需要 `citationStyles` 字段） |
| `export_markdown(papers, query_desc)` | 全部 Markdown 报告保存到文件 |
| `export_json(papers, path)` | JSON 导出保存到文件 |
| `deduplicate(papers)` | 通过 paperId 移除重复 |

### 支持的 ID 格式

`DOI:10.1038/...`，`ARXIV:2106.15928`，`PMID:19872477`，`PMCID:PMC2323569`，`CorpusId:215416146`，`ACL:2020.acl-main.447`，`DBLP:conf/acl/...`，`MAG:3015453090`，`URL:https://...`

### 论文字段

默认：`title,year,citationCount,authors,venue,externalIds,tldr`

附加：`corpusId`（整数，S2 次要 ID），`url`（S2 论文页面链接），`abstract`，`references`，`citations`，`openAccessPdf`，`publicationDate`，`publicationVenue`，`fieldsOfStudy`，`s2FieldsOfStudy`，`journal`，`isOpenAccess`，`referenceCount`，`influentialCitationCount`（仅限有影响力的引用），`citationStyles`，`embedding`，`textAvailability`

`externalIds` 对象包含：`ArXiv`，`MAG`，`ACL`，`PubMed`，`Medline`，`PubMedCentral`，`DBLP`，`DOI`

作者字段：`name`，`affiliations`，`paperCount`，`citationCount`，`hIndex`，`homepage`，`externalIds`，`papers`

> **最小化字段。** 根据 S2 官方教程：*"避免包含比您需要的更多的字段，因为那会降低响应速率。"* 仅在用户明确需要时添加 `abstract`，`references` 或 `citations`。

### `sort` 参数值（仅限批量搜索）

`sort` kwarg 仅接受以下三个值：

| 值 | 含义 |
| ------- | --------- |
| `citationCount:desc` | 引用次数最多优先（默认） |
| `publicationDate:desc` | 最新优先 |
| `paperId:asc` | 稳定的确定性顺序（用于分页） |

### 推荐限制

`find_similar()` 和 `recommend()` 每次调用最多返回 **500** 篇论文 (`limit` 最大 = 500)。

### 数据集 API 函数

用于批量下载完整 S2 数据集（论文、作者、摘要、嵌入等）：

| 函数 | 目的 | 是否需要密钥 |
| ---------- | --------- | -------------- |
| `list_releases()` | 列出所有可用的发布日期字符串 | 否 |
| `list_datasets(release_id="latest")` | 列出发布中的数据集 | 否 |
| `get_dataset_links(release_id, dataset_name)` | 数据集的预签名下载 URL | **是** |
| `get_dataset_diffs(start, end, dataset_name)` | 两个发布之间的增量差异 | **是** |

**可用数据集名称**（作为 `dataset_name` 传递）：

| 名称 | 描述 | 大约大小 |
| ------ | ------------- | ------------- |
| `papers` | 核心论文属性（标题、作者、日期等） | ~200M 记录，30 × 1.5 GB |
| `abstracts` | 论文摘要文本（如果可用） | ~100M 记录，30 × 1.8 GB |
| `authors` | 作者核心属性（姓名、隶属关系、论文计数） | — |
| `citations` | 论文之间的引用关系 | — |
| `embeddings-specter_v1` | 论文的密集 SPECTER 向量嵌入 | ~120M 记录，30 × 28 GB |
| `publication-venues` | 会议元数据 | — |
| `s2orc` | 来自开放获取 PDF 的全文 | — |
| `tldrs` | 短自然语言摘要 | ~100M 记录，30 × 200 MB |

所有数据集都以 **JSON Lines**（每行一条记录）交付。差异响应包含 `update_files`（通过主键插入/替换）和 `delete_files`（从数据集中删除）。

### 速率限制

`s2.py` 根据是否设置了 `S2_API_KEY` 自动调整：

| 模式 | 间隔 | 官方限制 | 重试 |
|------|-----|-----|-----|
| 认证（有效密钥） | 1.1 s | **入门级 1 req/s** 每个密钥，专用配额，跨所有端点累积（可按请求提高） | 5× 指数退避（2s→60s） |
| 未认证（无密钥或无效密钥） | 5.0 s | **1000 req/s 共享** 在所有匿名用户之间；在高峰使用期间“可能会进一步限制” | 5× 指数退避（2s→60s） |

> S2 建议在每次请求中包含 API 密钥，即使对于可以匿名工作的端点也是如此 — 它为您提供专用配额、在负载下更平滑的体验以及如果需要帮助时更好的支持。入门级 1 req/s 密钥可以按请求提高。在 <https://www.semanticscholar.org/product/api#api-key-form> 获取密钥。
>
> 匿名 1000 req/s 池在稳态下很慷慨，但在文档中明确警告说在高峰使用期间可能会被严格限制 — 这就是为什么没有密钥时 `_MIN_GAP` 默认为 5 秒，而不是 1 ms 一个 1000 req/s 预算技术上允许的。如果您的负载仍然遇到持续的 429 错误，请在 `s2.py` 中将 `_MIN_GAP = 10.0` 或获取密钥。1 req/s 密钥预算跨所有端点累积，因此串联调用（例如 `get_paper` → `get_citations`）分别计算。

### 批量搜索响应结构

`search_bulk()` 返回一个已取消分页的论文列表。内部原始响应具有：

| 字段 | 类型 | 含义 |
| ------- | ------ | --------- |
| `total` | integer | 估计匹配的论文总数（不精确） |
| `token` | string | 存在更多页面时显示；在下一个请求中传递 |
| `data` | array | 此页面的论文 |

`s2.py` 自动处理标记分页 — 您只看到最终的扁平列表。

### 故障排除

| 错误 | 原因 | 修复 |
| ------- | ------- | ----- |
| `HTTPError 403` | `S2_API_KEY` 设置但无效/过期 | `s2.py` 自动回退到未身份验证；或者 `unset S2_API_KEY`，或者 <https://www.semanticscholar.org/product/api#api-key-form> 获取新密钥 |
| `HTTPError 404` | 坏的论文/作者 ID | 检查 ID 格式 — S2 返回 `{"error": "Paper/Author/Object not found"}` 或 `"...with id ### not found"` |
| `HTTPError 429` after 5 retries | 持续匿名速率限制命中 | 等待 60 秒，将 `_MIN_GAP` 在 `s2.py` 中从 5.0 → 10.0，保持 `max_results` ≤ 30，或者获取 API 密钥 |
| `ModuleNotFoundError: s2` | 技能目录不在路径上 | 验证技能安装在 `~/.claude/skills/`，`~/.openclaw/skills/`，或作为 Claude 代码插件在 `~/.claude/plugins/` 下 |
| `ModuleNotFoundError: requests` | `requests` 未安装 | `pip install requests` 或 `uv pip install requests` |
| 0 结果返回 | 查询太具体或过滤器太窄 | 放宽查询，删除过滤器，尝试 `search_relevance()` 而不是 `search_bulk()` |
| `KeyError: 'data'` | 端点返回了错误对象 | 检查 `r.get("message")` 以获取 API 错误详细信息 |
| `tldr` 字段为空 | 不是所有论文都有 TLDR；批量搜索从不返回它 | 回退到 `abstract` 字段 |
