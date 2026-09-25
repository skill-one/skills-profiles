# PubMed API

## 前置条件

1.  **`uv`**: 阅读 `uv` 技能并遵循其设置说明，确保已安装 `uv` 并在 PATH 路径中。
2.  **用户通知**: 如果工作区根目录中不存在 `.licenses/pubmed_database_LICENSE.txt` 文件，则 (1) 显著通知用户检查 https://pubmed.ncbi.nlm.nih.gov/disclaimer/ 和 https://www.ncbi.nlm.nih.gov/home/about/policies/ 上的条款，并始终检查通过技能检索的论文的许可证以了解任何限制，然后 (2) 创建记录通知文本和时间戳的文件。
3.  **`.env` 文件**: 确保您的家目录中存在 `.env` 文件。如果不存在，请创建它。
4.  **`NCBI_API_KEY`** (可选): 将 NCBI E-utilities 的速率限制从 3 提高到每秒 10 个请求。该技能无需此密钥即可工作，但如果用户计划进行大量查询或遇到 429 错误，则建议使用密钥。您可以在 https://www.ncbi.nlm.nih.gov/account/settings/ 免费注册密钥。如果此技能与用户的请求相关，您 **必须** 在 `credentials` 技能中使用安全凭证协议来检查并请求此密钥。
5.  **`USER_EMAIL`** (可选): 用于向 NCBI 标识调用者（根据其使用条款推荐）。如果此技能与用户的请求相关，您 **必须** 在 `credentials` 技能中使用安全凭证协议来检查并请求此凭证。

此技能通过 `scripts/pubmed_api.py` 提供对 NCBI PubMed 和 PubMed Central API 的 CLI 访问——一个包含 10 个功能的单一 CLI，涵盖搜索、获取、链接、全文、拼写、发现、引文匹配和缓存。

## 核心规则

-   **API 使用**: 始终使用提供的包装器 `scripts/pubmed_api.py`，该包装器自动管理速率限制并防止 API 滥用。设置 `NCBI_API_KEY` 环境变量将速率限制从每秒 3 个请求提高到 10 个请求。以任何其他方式（例如通过 curl、wget 或手写代码）查询 API 是严格禁止的。
-   **JSON 处理**: 使用 `jq` 过滤和转换 JSON 输出（如果 `jq` 不可用，则使用 Python 等效程序），以防止幻觉和上下文溢出。
-   **临时文件**: 为避免将 JSON 文件污染工作目录，在当前目录内使用临时目录。在并行运行多个代理或任务时，确保每个使用唯一的子目录名称（例如 `tmp_$TASK_ID/`）以避免文件冲突。
-   **通知**: 如果使用此技能，请确保在输出中提及这一点，并列出所有用于生成输出的论文的 URL。

## 技能文件夹的结构

-   `SKILL.md` - 此文件
-   `scripts/pubmed_api.py` - 技能 CLI
-   `references/` - 包含详细功能规范的目录
    -   `advanced-linking.md`
    -   `advanced-search.md`
    -   `bulk-workflows.md`
    -   `citation-matching.md`
    -   `cross-database-linking.md`
    -   `fetch-and-resolve.md`
    -   `search-and-discovery.md`
    -   `utilities.md`

## CLI 使用

```bash
uv run scripts/pubmed_api.py <output_file> <function_name> <required_args> [--flag value ...]
```

-   **位置参数**: 参数是位置性的；列表参数作为不带空格的逗号分隔字符串传递（例如 `"35113657,31234568"`）。
-   **标志选项**: 可选参数可以作为 `--flag value` 而不是位置参数传递。
-   **输出处理**: 成功时，JSON 写入 `output_file`。出错时，进程退出并带有非零代码且不写入输出文件。

### 示例用法

```bash
uv run scripts/pubmed_api.py ./search_results.json search_pubmed "BRCA1" --max_results 5
cat ./search_results.json | jq '.[]' -r
uv run scripts/pubmed_api.py ./abstracts.json fetch_article_abstracts "35113657"
cat ./abstracts.json | jq '.[0].title' -r
```

## 基本配方

**为下一次调用连接 PMIDs（最常见的链式模式）：**

```bash
cat ./search_results.json | jq -r 'join(",")'
```

**将摘要缩减为基本字段并截断长摘要：**

```bash
cat ./abstracts.json | jq '[.[] | {pmid, title, snippet: (.abstract // "")[:500]}]'
```

**按关键词过滤（空值安全）：**

```bash
cat ./abstracts.json | jq '[.[] | select((.title // "") | contains("Review"))]'
```

### 上下文管理与准确性

在处理大于 10 个摘要的结果集时：

1.  **早期过滤**: 使用 `jq` 在将完整 JSON 读取到上下文中之前验证摘要中的关键词。
2.  **缩减**: 除非明确指示否则仅提取 `title` 和 `abstract` 字段。作者列表和元数据会增加噪声。
3.  **批量操作 (N > 10)**: 避免逐个获取或处理 ID。API 和 History Server 设计用于批量检索。在单个回合中获取所有数据，并使用 shell 管道在读取到上下文之前缩减结果。这可防止回合耗尽和上下文溢出。
4.  **事实核查**: 如果未找到结果，切勿使用内部知识提供特定标识符（PMIDs、CIDs、基因 ID）。准确报告工具的输出，以确保结果基于当前数据库状态。
5.  **搜索终止**: 当被要求查找可能不存在的论文时，将探索限制为 3-5 个高质量、多样化的搜索查询。在这些尝试后如果没有结果匹配，则得出没有论文符合标准的结论，而不是继续迭代——除非明确指示要彻底进行。

## 功能

> **⚠️ 强制性**: 您 **必须** 在调用任何功能之前阅读相关参考文件。下表仅描述每个功能做什么——不描述如何调用它。参数名称、参数顺序、标志和输出模式 **仅** 在参考文件中记录。**不要** 根据功能名称猜测或推断参数。如果您在阅读参考之前调用功能，您 **将** 生成不正确的调用。

### [搜索](references/search-and-discovery.md)

-   `search_pubmed`: 查找与自由文本或结构化 NCBI 查询匹配的 PMIDs。
-   `global_database_discovery`: 统计跨所有 NCBI 数据库匹配查询的记录数。

### [获取与解析](references/fetch-and-resolve.md)

-   `fetch_article_abstracts`: 获取一批 PMIDs 的元数据和摘要。
-   `get_full_text_pmc`: 从 PMC 获取开放获取的全文。
-   `fetch_database_summary`: 将来自任何 NCBI 数据库的不透明 UID 解析为人类可读的元数据。

### [跨数据库链接](references/cross-database-linking.md)

-   `find_linked_biological_data`: 查找与源记录链接的其他 NCBI 数据库中的记录。
-   `discover_available_links`: 列出给定记录的所有可用 ELink 链接名称。

### [批量工作流](references/bulk-workflows.md)

在处理 **超过 ~10 个 PMIDs** 时，避免逐个处理 ID。通过 `cache_results_history` 将它们上传到 NCBI History Server 以获取会话句柄（`webenv` + `query_key`），然后将该句柄传递给 `fetch_article_abstracts` 或 `find_linked_biological_data` 进行单个批量调用。使用 `jq` shell 管道在读取到上下文之前缩减结果。这可防止回合耗尽和上下文溢出。参考中提供了完整的工作流配方（搜索→获取、跨数据库探索、引文解析和带数据缩减的批量检索）。

-   `cache_results_history`: 将 PMIDs 上传到 NCBI History Server 以进行批量检索。

### [工具](references/utilities.md)

-   `verify_medical_spelling`: 在搜索之前检查生物医学术语的拼写。
-   `match_raw_citations`: 将不完整的书目引文解析为 PMIDs。
