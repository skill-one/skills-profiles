# arXiv 搜索与检索

## 前置条件

1.  **`uv`**: 阅读 `uv` 技能并遵循其安装说明，确保 `uv` 已安装且在 PATH 路径中。
2.  **用户通知**: 如果工作区根目录中不存在 `.licenses/literature_search_arxiv_LICENSE.txt` 文件，则 (1) 显著通知用户检查 https://info.arxiv.org/help/api/index.html 上的条款，并始终检查技能检索到的论文的许可证以获取任何限制，然后 (2) 创建一个记录通知文本和时间戳的文件。

## 核心规则

-   **使用条款**: 您必须尊重 arXiv 的使用条款。
    -   每隔 3 秒最多 1 次请求。
    -   提供的实用脚本会自动处理速率限制。始终使用这些脚本，而不是编写自己的 curl/Python 请求。
-   如果使用此技能，请确保在输出中提及这一点，并列出用于生成输出的所有论文的 URL。

## 实用脚本

**1. 搜索和提取元数据**

搜索 arXiv 并返回匹配论文的干净 JSON 数组。

```bash
uv run scripts/search_arxiv.py --query "au:einstein AND ti:relativity" \
  --max_results 5 2>/dev/null > /tmp/arxiv_search_results.json
```

> **重要**: 工具将大型 JSON 结果输出到标准输出。请求 100+ 结果将产生一个巨大的 JSON，可能会超过您的上下文长度。限制 `--max_results`（例如，5-10）或使用 `--start` 小心地分页。始终将输出重定向到文件并单独解析，否则终端输出将被截断。

*返回的元数据*: JSON 结果包括 `id`、`title`、`summary`、`published`、`authors`、`pdf_url`、`primary_category`、`doi`、`journal_ref` 和 `comment`。注意：`doi` 字段仅包含 DOI 信息，仅当论文有外部 DOI 时才包含，如果仅存在 arXiv 发布的 DOI，则不返回此 DOI。

*选项*:

-   `--query`: 搜索字符串。有关高级语法，请参阅 [references/query_syntax.md](references/query_syntax.md)。
-   `--id_list`: 要直接获取的 arXiv ID 的逗号分隔列表（例如，`1706.03762v5`）。
-   `--start`: 分页偏移量（默认为 0）。
-   `--max_results`: 要返回的结果数量（默认为 10）。
-   `--sort_by`: `relevance`、`lastUpdatedDate` 或 `submittedDate`。（使用 `--sort_by submittedDate --sort_order descending` 获取最新论文）。
-   `--sort_order`: `ascending` 或 `descending`。

**2. 下载论文（PDF 或 HTML）**

将论文全文下载到本地工作区以供阅读。

```bash
uv run scripts/download_paper.py --id 1706.03762 --format pdf --output attention.pdf
```

*选项*:

-   `--id`: arXiv ID（例如，`1706.03762` 或 `1706.03762v5`）。
-   `--format`: `pdf` 或 `html`。注意：HTML 仅适用于较新的论文。
-   `--output`: 保存下载文档的文件路径。

> **重要**: 下载论文时，请确保将它们下载到不会覆盖其他文件且不会杂乱现有目录结构的位置。

**3. 下载论文源（tar.gz）**

将论文的 LaTeX 源文件下载到本地工作区。注意并非所有论文都有源文件可用。

```bash
uv run scripts/download_paper_source.py --id 2010.11645 --output source.tar.gz
```

*选项*:

-   `--id`: arXiv ID（例如，`2010.11645`）。
-   `--output`: 保存下载的 tar.gz 文件的文件路径。

> **注意**: 在解压缩下载的文件时要小心，以确保安全并避免杂乱您的文件系统，因为存档可能包含许多文件或意外的目录结构。

> **安全解压要求**: 绝对不要直接解压到您的工作目录！始终解压到一个专用的新目录：`bash mkdir paper_source && tar -xzf source.tar.gz -C paper_source`

## 参考

-   **高级查询语法**: 有关前缀（au、ti、abs）、布尔值和日期过滤，请参阅 [references/query_syntax.md](references/query_syntax.md)。

## 工作流程

1.  使用 `search_arxiv.py` 搜索论文。查看 JSON 摘要。
2.  如果需要全文，使用 `download_paper.py` 获取 PDF 或 HTML。
3.  如果下载 PDF，请验证 PDF 是否为空或损坏。
4.  使用标准文件读取工具阅读下载的文件。
