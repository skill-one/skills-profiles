# Europe PMC 数据库

一个用于搜索、下载和探索 Europe PMC（https://europepmc.org/）上开放获取论文的技能——这是一个包含超过 4300 万篇摘要和 900 万篇全文文章的综合性免费生命科学文献数据库。

## 前置条件

1.  **`uv`**：阅读 `uv` 技能并按照其设置说明进行操作，确保 `uv` 已安装并在 PATH 环境变量中。
2.  **用户通知**：如果工作区根目录中不存在 `.licenses/literature_search_europepmc_LICENSE.txt` 文件，则（1）向用户显著通知其检查 https://europepmc.org/ 上的条款，并始终检查该技能检索到的论文的许可限制，然后（2）创建一个记录通知文本和时间戳的文件。

## 核心规则

-   **仅开放获取**：此技能仅搜索开放获取内容。脚本会自动在每个搜索查询中追加 `OPEN_ACCESS:y`。**不要**移除或覆盖此过滤器。
-   **绝对不要直接运行 `python3` 或 `python3 -c`**：系统 Python 不一定包含所有关键依赖项。不要尝试使用 pip 安装或创建新的虚拟环境。
-   **使用包装器**：**始终**使用提供的脚本，而不是直接调用 API。脚本会处理速率限制（1 请求/秒）和错误。
-   **输出文件**：所有子命令都需要 `--output` 参数将结果写入文件。单独读取输出文件以避免上下文溢出。
-   **列出来源**。如果使用此技能，请确保在输出中提及这一点，并列出所有用于生成输出的论文的 URL。

## 实用脚本

所有命令都是 `scripts/europepmc_api.py` 的子命令。速率限制和重试会自动处理。

### 1. 搜索 (`search`)

通过查询搜索 Europe PMC。支持 DOI 查找、关键词搜索、作者搜索、PMID 查找，并支持完整的 [Europe PMC 搜索语法](https://europepmc.org/searchsyntax)。

```bash
# 通过 DOI 查找论文
uv run scripts/europepmc_api.py search "DOI:10.1038/s41586-021-03819-2" --output result.json

# 关键词搜索
uv run scripts/europepmc_api.py search "CRISPR cancer" --max_results 5 --output results.json

# 作者搜索
uv run scripts/europepmc_api.py search "AUTH:Jumper J" --max_results 10 --output results.json

# PMID 查找
uv run scripts/europepmc_api.py search "EXT_ID:34265844 AND SRC:MED" --output result.json

# 按引用次数排序
uv run scripts/europepmc_api.py search "machine learning" \
  --sort "CITED desc" --max_results 20 --output results.json
```

**参数：**

-   `query` (str, 必填) — 使用 Europe PMC 语法进行搜索的查询
-   `--output` (str, 必填) — 输出 JSON 文件路径
-   `--max_results` (int, 默认 10) — 每页的最大结果数（最大 1000）
-   `--result_type` (str, 默认 `core`) — `core`（完整元数据）或 `lite`
-   `--cursor` (str, 默认 `*`) — 分页的游标标记；传递来自先前响应的 `nextCursorMark` 值以获取下一页
-   `--sort` (str) — 排序顺序，例如 `CITED desc`、`P_PDATE_D desc`（出版日期降序）、`P_PDATE_D asc`

**输出：** 包含三个字段的 JSON 文件：

-   `hitCount` (int) — 匹配文章的总数
-   `nextCursorMark` (str) — 下一页的游标；如果没有更多页面则为空字符串
-   `results` (list) — 文章元数据对象数组

**搜索语法快速参考：**

-   `DOI:10.xxxx/yyyy` — 通过 DOI 查找
-   `EXT_ID:12345678 AND SRC:MED` — 通过 PMID 查找
-   `AUTH:surname initials` — 作者搜索
-   `TITLE:keyword` — 仅在标题中搜索
-   `JOURNAL:name` — 通过期刊搜索
-   `PUB_YEAR:2024` 或 `(FIRST_PDATE:[2023-01-01 TO 2023-12-31])` — 日期过滤
-   `HAS_FT:y` — 限制为 Europe PMC 中包含全文的文章
-   布尔运算符：`AND`、`OR`、`NOT`

> **注意**：`OPEN_ACCESS:y` 会自动追加到所有查询中。您不需要手动添加它。

### 2. 下载 PDF (`download_pdf`)

通过 PMCID 从 Europe PMC 下载开放获取的 PDF。

```bash
uv run scripts/europepmc_api.py download_pdf PMC8371605 --output alphafold.pdf
```

**参数：**

-   `pmcid` (str, 必填) — PubMed Central ID（例如 `PMC8371605`）
-   `--output` (str, 必填) — 保存 PDF 的文件路径

**输出：** 将 PDF 保存到指定文件。如果 PMCID 未找到或响应不是有效的 PDF，则退出并报错。每次下载 PDF 时，请检查下载的 PDF 是否为空或损坏。

### 3. 获取全文 (`get_fulltext`)

检索开放获取文章的全文并保存到文件。默认情况下返回纯文本（已移除 XML 标签），或使用 `--format xml` 返回原始 XML。

```bash
# 获取纯文本（默认）
uv run scripts/europepmc_api.py get_fulltext PMC8371605 --output fulltext.txt

# 获取原始 XML
uv run scripts/europepmc_api.py get_fulltext PMC8371605 --format xml --output fulltext.xml
```

**参数：**

-   `pmcid` (str, 必填) — PubMed Central ID
-   `--output` (str, 必填) — 输出文件路径
-   `--format` (str, 默认 `text`) — `text`（纯文本）或 `xml`（原始 JATS XML）

**输出：** 将全文写入指定文件。如果文章不在 Europe PMC 开放获取子集中，则退出并报错。

> **重要**：只有 PMC 开放获取子集中的文章才提供全文。如果检索失败，请使用 `search` 检查 `isOpenAccess` 字段，然后回退到摘要。

### 4. 获取引用 (`get_citations`)

检索引用给定论文的文章。

```bash
# 获取 AlphaFold 论文（PMID 34265844）的引用
uv run scripts/europepmc_api.py get_citations MED 34265844 \
  --page_size 25 --output citations.json
```

**参数：**

-   `source` (str, 必填) — 源数据库：`MED`（PubMed）、`PMC`、`PPR`（预印本）、`PAT`（专利）
-   `article_id` (str, 必填) — 源数据库中的文章 ID
-   `--output` (str, 必填) — 输出 JSON 文件路径
-   `--page` (int, 默认 1) — 页码
-   `--page_size` (int, 默认 25) — 每页结果数

**输出：** 包含 `hitCount` 和 `citations` 数组的 JSON 文件。

### 5. 获取参考文献 (`get_references`)

检索给定文章的参考文献列表（书目）。

```bash
# 从 AlphaFold 论文获取参考文献
uv run scripts/europepmc_api.py get_references MED 34265844 \
  --page_size 100 --output references.json
```

**参数：**

-   `source` (str, 必填) — 源数据库：`MED`、`PMC`、`PPR`、`PAT`
-   `article_id` (str, 必填) — 源数据库中的文章 ID
-   `--output` (str, 必填) — 输出 JSON 文件路径
-   `--page` (int, 默认 1) — 页码
-   `--page_size` (int, 默认 25) — 每页结果数

**输出：** 包含 `hitCount` 和 `references` 数组的 JSON 文件。

## 常见工作流程

### DOI 到 PDF

```bash
# 第一步：搜索 PMCID
uv run scripts/europepmc_api.py search "DOI:10.1038/s41586-021-03819-2" --output result.json
PMCID=$(jq -r '.results[0].pmcid // empty' result.json)

# 第二步：下载 PDF
uv run scripts/europepmc_api.py download_pdf "$PMCID" --output paper.pdf
```

### PMID 到全文

```bash
# 第一步：从 PMID 找到 PMCID
uv run scripts/europepmc_api.py search "EXT_ID:34265844 AND SRC:MED" --output result.json
PMCID=$(jq -r '.results[0].pmcid // empty' result.json)

# 第二步：获取全文
uv run scripts/europepmc_api.py get_fulltext "$PMCID" --output fulltext.txt
```

### 引用图遍历

```bash
# 查找引用了里程碑研究的论文，然后检查它们的参考文献
uv run scripts/europepmc_api.py get_citations MED 34265844 --page_size 50 --output citing.json
# 解析引用论文的 PMID 并探索其参考文献
uv run scripts/europepmc_api.py get_references MED <CITING_PMID> --output refs.json
```

### 带分页的搜索

```bash
# 第一页
uv run scripts/europepmc_api.py search "CRISPR" --max_results 100 --output page1.json
# 提取下一页的游标
CURSOR=$(jq -r '.nextCursorMark // empty' page1.json)
# 下一页
uv run scripts/europepmc_api.py search "CRISPR" --max_results 100 --cursor "$CURSOR" --output page2.json
```
