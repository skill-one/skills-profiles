# EMBL-EBI本体查找服务（OLS）

## 前置条件

1.  **`uv`**: 阅读 `uv` 技能并遵循其设置说明，确保 `uv` 已安装并在 PATH 路径中。
2.  **用户通知**: 如果工作区根目录中不存在 `.licenses/embl_ebi_ols_LICENSE.txt`，则 (1) 显著通知用户检查 https://www.ebi.ac.uk/ols4/api-docs 上的条款，然后 (2) 创建记录通知文本和时间戳的文件。

## 核心规则

-   [!IMPORTANT] **使用工具脚本**: 您必须始终使用 `scripts/` 下提供的工具脚本进行所有 API 交互，包括检查状态。绝对不要使用 `curl` 或自定义 Python 请求直接查询 API。
-   **速率限制与弹性**: 您必须遵守 EBI 的使用条款，每秒最多 5 个请求。提供的工具脚本会自动执行此限制。
-   **通知**: 如果使用此技能，请确保在输出中提及。

## 使用场景 — 快速配方

当用户查询匹配以下模式时，使用此技能：

-   **疾病、表型或术语的定义** → `get_term.py --obo_id <ID> --summary`
-   **术语的子类型或子项** → `get_term.py --obo_id <ID> --relations children`
-   **术语的父项** → `get_term.py --obo_id <ID> --relations parents`
-   **祖先 / 疾病类别 / 分类于** → `get_term.py --obo_id <ID> --relations ancestors`
-   **本体的根术语** → `get_term.py --ontology <id> --roots`
-   **分层父项（is-a + part-of）** → `get_term.py --obo_id <ID> --relations hierarchicalParents`
-   **构成部分 / 分层子项** → `get_term.py --obo_id <ID> --relations hierarchicalChildren`
-   **比较直接与分层父项** → `get_term.py --obo_id <ID> --relations parents,hierarchicalParents`
-   搜索术语（例如，GO 中的 "apoptosis"）→ `search_ols.py --query "..." --ontology <id>`
-   找到与功能匹配的 **GO 术语** → `search_ols.py --query "..." --ontology go --exact`
-   在 **MONDO**、**CHEBI**、**CL**、**UBERON** 中搜索 → `search_ols.py --query "..." --ontology <id> --defining`
-   **分页** 搜索结果 / 下一页 → `search_ols.py --query "..." --rows N --start <offset>`
-   自动补全部分名称 → `suggest_ols.py --query "..."`
-   本体元数据（例如，EFO 信息）→ `get_ontology.py --id <id>`
-   OLS 索引统计 → `get_stats.py`

> **多步查询**（例如，“心肌梗塞的父项是什么？”）：
> 当用户命名一个术语但您不知道其 OBO ID 时，必须精确地分两步完成——不要跨多个本体搜索：
>
> 1.  **搜索** 在最合适的单个本体中：`search_ols.py --query "myocardial infarction" --ontology doid --exact --rows 1 --output /tmp/step1.json`
> 2.  使用步骤 1 中的 OBO ID **获取关系**：`get_term.py --obo_id DOID:5844 --relations parents --output /tmp/step2.json`
>
> **本体选择规则**：始终使用 `doid` 用于常见的人类疾病（例如，糖尿病、癌症），`hp` 用于表型，`go` 用于基因功能，`chebi` 用于化学物质，`uberon` 用于解剖学，`cl` 用于细胞类型。仅在明确提及或需要跨物种上下文时使用 `mondo`。

## 工具脚本

**1. 跨本体搜索术语**

通过关键字搜索本体术语并返回干净的 JSON。

```bash
uv run scripts/search_ols.py --query "diabetes" \
  --rows 5 --output /tmp/ols_search_results.json 2>/dev/null
```

> **重要**：`--output` 对所有脚本都是必需的。结果始终写入指定的文件。对于较大的输出，您可以限制 `--rows`（例如，5-10）或使用 `--start` 进行分页。

*返回字段*：JSON 结果包括 `iri`、`label`、`description`、`ontology_name`、`ontology_prefix`、`obo_id`、`short_form`、`type`、`is_defining_ontology` 和 `exact_synonyms`。

*分页*：输出包括一个 `pagination` 块，包含 `start`、`rows` 和 `has_more`，以便您决定是否获取更多结果。

*选项*：

-   `--query`：搜索字符串（必需）。搜索标签、同义词、描述和标识符。
-   `--ontology`：按本体 ID 过滤（例如，`go`、`doid`、`efo`、`hp`）。**推荐** 在您知道要搜索哪个本体时使用——避免来自 250 多个本体的噪音。
-   `--type`：按实体类型过滤：`class`、`property`、`individual` 或 `ontology`。
-   `--exact`：仅标记精确标签匹配。**用于实体解析**，当将用户的字符串映射到特定的本体术语 ID 时。
-   `--defining`：仅返回来自其定义（权威）本体的术语。例如，`GO:0005634` 仅来自 GO，而不是交叉引用的副本。
-   `--obsolete`：标记以包含过时的术语在结果中。
-   `--local`：仅返回定义本体内的术语。
-   `--childrenOf`：限制为给定术语 IRI（用逗号分隔）的子项。
-   `--allChildrenOf`：限制为所有子项，包括传递关系（例如，“part of”、“develops from”），用逗号分隔的 IRIs。
-   `--queryFields`：逗号分隔的要在其中搜索的字段（例如，`label,synonym,description`）。
-   `--fieldList`：逗号分隔的要返回的字段。
-   `--groupField`：按唯一 IRI 对结果进行分组。
-   `--isLeaf`：仅返回叶术语（没有子项）。
-   `--rows`：要返回的结果数量（默认 10）。
-   `--start`：分页偏移量（默认 0）。
-   `--output`：保存结果的文件路径（**必需**）。

**2. 自动补全 / 建议**

获取部分术语名称的自动补全建议。

```bash
uv run scripts/suggest_ols.py --query "diabet" --rows 5 \
  --output /tmp/ols_suggest.json 2>/dev/null
```

*选项*：

-   `--query`：要自动补全的部分术语（必需）。
-   `--ontology`：按本体 ID（用逗号分隔）过滤。
-   `--rows`：建议数量（默认 10）。
-   `--start`：分页偏移量（默认 0）。
-   `--output`：保存结果的文件路径（默认：stdout）。

**3. 获取术语详细信息**

通过其 OBO ID 或 IRI 获取特定本体术语的完整详细信息。

```bash
uv run scripts/get_term.py --obo_id "GO:0005634" \
  --output /tmp/ols_term.json 2>/dev/null
```

*返回字段*：JSON 包括 `iri`、`label`、`description`、`obo_id`、`synonyms`、`ontology_name`、`is_obsolete`、`is_defining_ontology`、`has_children`、`is_root`、`annotation`、`in_subset` 以及任何请求的关系。

*摘要模式*：使用 `--summary` 获取干净的、人类可读的块在 stdout 上（标签、OBO ID、本体、定义、同义词）。完整的 JSON 始终保存到 `--output` 文件中。

```bash
uv run scripts/get_term.py --obo_id "GO:0005634" --summary \
  --output /tmp/nucleus_full.json
```

*选项*：

-   `--obo_id`：OBO 风格标识符（例如，`GO:0005634`、`DOID:9351`）。与 `--iri` 互斥。自动将双编码转换为 IRI。
-   `--iri`：术语的完整 IRI。与 `--obo_id` 互斥。
-   `--ontology`：本体 ID（如果未提供，则自动从 `--obo_id` 推导）。
-   `--relations`：要获取的逗号分隔的关系列表。

    -   **直接（仅 is-a）**：`parents`、`children`、`ancestors`、`descendants`
    -   **分层（is-a + 传递关系，如 "part of"、"develops from"）**：`hierarchicalParents`、`hierarchicalChildren`、`hierarchicalAncestors`、`hierarchicalDescendants`
    -   **图**：`graph`——术语的完整图 JSON

    > **注意**：对于解剖学/发育本体（UBERON、CL），使用分层变体，其中传递关系（如“part of”和“develops from”）对于导航层次结构至关重要。

-   `--roots`：列出本体的根术语（需要 `--ontology`）。

-   `--preferred_roots`：列出首选根术语（需要 `--ontology`）。

-   `--summary`：在 stdout 上显示人类可读的摘要，完整 JSON 保存到 `--output`。

-   `--output`：保存结果的文件路径（默认：stdout）。

**4. 获取属性详细信息**

获取具有层次结构的本体属性（关系类型）的详细信息。

```bash
uv run scripts/get_property.py --obo_id "BFO:0000051" --ontology go \
  --output /tmp/ols_property.json 2>/dev/null
```

*选项*：

-   `--obo_id`：属性的 OBO 风格 ID。与 `--iri` 互斥。
-   `--iri`：属性的完整 IRI。与 `--obo_id` 互斥。
-   `--ontology`：本体 ID（与 `--iri` 一起使用时必需）。
-   `--relations`：逗号分隔：`parents`、`children`、`ancestors`、`descendants`。
-   `--roots`：列出本体的根属性（需要 `--ontology`）。
-   `--output`：保存结果的文件路径（默认：stdout）。

**5. 获取个体详细信息**

获取本体个体的详细信息（实例）。

```bash
uv run scripts/get_individual.py --obo_id "IAO:0000103" --ontology iao --types \
  --output /tmp/ols_individual.json 2>/dev/null
```

*选项*：

-   `--obo_id`：OBO 风格 ID。与 `--iri` 互斥。
-   `--iri`：完整 IRI。与 `--obo_id` 互斥。
-   `--ontology`：本体 ID（与 `--iri` 一起使用时必需）。
-   `--types`：获取此个体的直接类型（类）。
-   `--alltypes`：获取所有类型，包括祖先类。
-   `--output`：保存结果的文件路径（默认：stdout）。

**6. 获取本体信息**

列出可用本体或检索特定本体的详细信息。

```bash
uv run scripts/get_ontology.py --id go \
  --output /tmp/ols_ontology.json 2>/dev/null
```

*选项*：

-   `--id`：特定本体 ID（例如，`go`、`efo`、`doid`）。如果省略，则列出所有本体。
-   `--page`：分页的页码（默认 0）。
-   `--size`：每页的本体数量（默认 20）。
-   `--output`：保存结果的文件路径（默认：stdout）。

**7. 获取 OLS 统计信息**

检索索引统计信息（总本体、类、属性、个体）。

```bash
uv run scripts/get_stats.py --output /tmp/ols_stats.json 2>/dev/null
```

*选项*：

-   `--output`：保存结果的文件路径（默认：stdout）。

## 参考

-   **API 参考**：有关常见本体 ID、OBO ID 格式和关键 API 端点的参考，请参阅
    [references/api_reference.md](references/api_reference.md)。
