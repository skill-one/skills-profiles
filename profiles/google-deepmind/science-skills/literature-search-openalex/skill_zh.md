# OpenAlex技能

## 前置条件

1.  **`uv`**: 阅读`uv`技能并遵循其安装说明，确保`uv`已安装并在PATH路径中。
2.  **用户通知**: 如果工作区根目录中不存在`.licenses/literature_search_openalex_LICENSE.txt`文件，则 (1) 醒目地通知用户检查[https://developers.openalex.org/](https://developers.openalex.org/)处的条款，并始终检查技能检索的论文的许可证以了解任何限制，然后 (2) 创建记录通知文本和时间戳的文件。
3.  **`.env`文件**: 确保您的家目录中存在`.env`文件。如果不存在，请创建它。
4.  **`OPENALEX_API_KEY`** (可选但推荐): 启用具有更高速率限制的OpenAlex高级API。该技能无需它即可工作（使用“礼貌池”的免费版本）。您可以在OpenAlex.org → 账户设置中获取密钥。如果此技能与用户的请求相关，您**必须**在`credentials`技能中使用安全凭证协议来检查并请求此密钥，以帮助用户将其添加到其`.env`文件中。

## 核心规则

1.  **列出来源**。如果使用此技能，请确保在输出中提及，并列出在生成输出时使用的所有论文的URL。
2.  **解析优先于过滤**。永远不要按名称过滤。首先将名称解析为ID，然后使用该ID在`--filter`中使用。
3.  **仅使用CLI**。永远不要通过`curl`/`urllib`调用API。CLI处理重试和速率限制。
4.  **不伪造**。永远不要编造OpenAlex ID或DOI。使用`resolve`/`get`来查找它们。准确报告空结果。
5.  **API密钥**。如果命令返回401/429或您需要高容量查询，您**必须**在`credentials`技能中使用安全凭证协议来检查并请求`OPENALEX_API_KEY`，以帮助用户将其添加到其`.env`文件中。
6.  **保持输出较小**。对于概览查询，始终使用`--select`和`--per-page 5–10`。将`filter`输出重定向到文件（`> results.json`），然后使用`jq`进行精简，然后再将其读入上下文中。

## 速率限制

-   **使用密钥**: 约10个请求/秒，每天1美元免费预算。
-   **不使用密钥**: 限制非常严格，每天预算0.01美元。

操作              | 成本
---------------------- | -------
单个`get`        | 免费
`filter`               | 0.0001
`--search` / `resolve` | 0.001
`download-pdf`         | 0.01

## CLI参考

```
uv run scripts/openalex_cli.py [--api-key KEY] <command> [flags]
```

实体类型（跨命令共享）：`works`，`authors`，`sources`，`institutions`，`topics`，`domains`，`fields`，`subfields`，`sdgs`，`countries`，`continents`，`languages`，`keywords`，`publishers`，`funders`，`work-types`，`source-types`，`institution-types`，`licenses`

### 命令

**resolve** `<entity> <query>` — 名称 → ID候选。返回`id`，`display_name`，`hint`。使用`--per-page N`获取更多候选。

**get** `<entity> <id>` — 一个实体的完整元数据。接受短ID（`W2741809807`），完整URL或DOI URL。使用`--select`限制字段。

**filter** `<entity>` — 搜索/过滤实体。主要标志是：

-   `--search <query>`：全文搜索（`--filter`成本的10倍）
-   `--filter <expr>`：过滤表达式。使用`,`表示AND，使用`|`表示OR。
-   `--sort <field:dir>`：排序结果（例如，`cited_by_count:desc`）
-   `--select <fields>`：限制输出中返回的字段。
-   `--group-by <field>`：按特定字段聚合结果。
-   `--per-page <N>`：每页结果数量（默认25，最大100）。
-   `--page <N>`：指定要检索的页码。
-   `--sample <N>`：获取最多10,000个结果的随机样本。
-   `--seed <N>`：可重复采样的种子。

**download-pdf** `<work-id> <output-path>` — 下载PDF（需要API密钥）。如果主要位置失败，则回退到替代`pdf_url`位置。每次下载PDF时，请验证它是否为空或已损坏。

**rate-limit** — 检查当前速率限制状态（需要API密钥）。

### 搜索技巧

-   如果`resolve`没有返回匹配项，请尝试替代拼写或缩写。
-   如果`--search`返回0个结果，请尝试更广泛的术语（最多3次重试）。
-   如果`resolve`返回多个候选，请使用`display_name`和`hint`向用户展示，以便手动选择。

## 实体参考

查阅`references/`以获取每个实体的有效过滤、排序和按组字段：

-   [Works](references/works.md) — [Authors](references/authors.md) —
    [Sources](references/sources.md)
-   [Institutions](references/institutions.md) — [Topics](references/topics.md)
    — [Taxonomy](references/taxonomy.md)
-   [Geo & Language](references/geo_and_language.md) —
    [Publishers & Funders](references/publishers_funders.md)
-   [Type Values](references/type_values.md)

## 常见工作流

```bash
# 作者的论文（解析 → 过滤）
uv run scripts/openalex_cli.py resolve authors "Geoffrey Hinton"
uv run scripts/openalex_cli.py filter works \
  --filter "authorships.author.id:A5108093963" \
  --sort "cited_by_count:desc" --per-page 10 > papers.json
cat papers.json | jq '[.results[] | {id, title: .display_name, year: .publication_year, citations: .cited_by_count}]'

# DOI查找
uv run scripts/openalex_cli.py get works "https://doi.org/10.1038/s41586-021-03819-2"

# 批量DOI查找（最多100）
uv run scripts/openalex_cli.py filter works \
  --filter "doi:10.1234/a|10.1234/b|10.1234/c" --per-page 100 > results.json

# 按年份的机构影响力
uv run scripts/openalex_cli.py resolve institutions "MIT"
uv run scripts/openalex_cli.py filter works \
  --filter "authorships.institutions.id:I63966007" \
  --group-by "publication_year" > mit_by_year.json

# 随机样本
uv run scripts/openalex_cli.py filter works \
  --filter "publication_year:2023,is_oa:true" \
  --sample 100 --seed 42 > results.json
```

## 错误处理

| 代码 | 含义             | 操作                        |
| ---- | ------------------- | ----------------------------- |
| 401  | 未授权        | 您**必须**在credentials技能中使用安全凭证协议 |
:      :                     : 来帮助用户将API密钥添加到   :
:      :                     : `.env`                        :
| 403  | 需要升级套餐 | 通知用户；参见              |
:      :                     : https\://openalex.org/pricing :
| 404  | 未找到           | 验证ID；首先尝试`resolve`      |
:      :                     :                              :
| 429  | 速率限制        | 等待并重试；您**必须**使用  |
:      :                     : credentials技能中的安全凭证协议 :
:      :                     : 来帮助用户将API密钥添加到 `.env` :

已知的仅限高级过滤：`from_updated_date`，`to_updated_date`。

在空响应上永远不要编造结果 — 准确报告并建议替代搜索术语。
