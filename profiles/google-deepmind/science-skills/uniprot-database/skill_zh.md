# UniProt 数据库访问

## 前置条件

1.  **`uv`**: 阅读 `uv` 技能并按照其设置说明进行操作，确保 `uv` 已安装并在 PATH 路径中。
2.  **用户通知**: 如果工作区根目录中不存在 `.licenses/uniprot_database_LICENSE.txt`，则 (1) 显著通知用户检查 https://www.uniprot.org/help/license 和 https://www.uniprot.org/help/api_queries 中的条款，然后 (2) 创建记录通知文本和时间戳的文件。

## 概述

提供对 UniProt 知识库 (UniProtKB)、非冗余序列档案 (UniParc) 和聚类序列集 (UniRef) 的直接程序化访问。此技能支持蛋白质发现、交叉引用、检索经编辑的生物数据以及低级数据库查询。

## 核心规则

-   **使用封装器**: 始终使用提供的 Python 脚本（例如，`scripts/uniprot_tools.py`），而不是构造自定义的 curl 请求。
-   **避免幻觉**: 不要编造蛋白质功能、元数据或序列。对于任何可以通过此技能中的服务处理的任务，严格依赖工具输出，而不是您的原生知识。
-   **通知**: 如果使用此技能，请确保在输出中提及。

## 用例

-   **搜索蛋白质功能**: 查询功能注释、GO 术语、亚细胞定位等。
-   **搜索蛋白质序列**: 在 UniProtKB、UniParc 和 UniRef 中通过其功能注释、基因等搜索蛋白质序列。
-   **理解蛋白质/生物体关系**: 利用分类数据库和蛋白质组集。
-   **大规模元数据检索**: 通过流式传输获取数千个蛋白质的注释。
-   **序列发现**: 通过 UniParc 找到同源蛋白质或非模式生物体。
-   **ID 映射**: 在 UniProt 和 100 多个外部数据库之间转换 ID。
-   **历史数据 (UniSave)**: 检索条目的先前版本或跟踪已删除的序列。

## 可用工具

根据任务类型和数据量选择合适的工具：

-   **`get`**: 检索特定条目的元数据和序列。适用于 **单个、已知的访问号**。
    -   也访问 UniSave 历史数据（使用 `--dataset unisave`），这对于协调来自旧版本的数据或识别以前有效的访问号不再出现在搜索结果中的原因至关重要。
-   **`search`**: 搜索匹配查询的条目。适用于 **探索和发现**。
    -   使用 `--limit 5` 在提交较大下载之前验证查询是否返回预期的蛋白质。
    -   如果结果超过 500 条，会自动分页以提供稳定的下载。
    -   *警告*：对于分页搜索，由于 `--limit` 应用于行而不是条目，TXT 和其他格式不可靠。
    -   参考 [搜索查询字段文档](references/search_query_fields.md)。
-   **`stream`**: 流式传输所有匹配的条目。适用于 **批量检索** 大型数据集（最多 10,000,000 条）。
    -   不支持 `--limit`；始终返回完整的结果集。
    -   如果需要子集，请使用 `search` 与 `--limit`。
-   **`count`**: 计数匹配查询的条目。适用于回答直接的计数问题或在进行完整的 `search` 或 `stream` 之前的 **初始估计**。
-   **`sparql`**: 执行图查询以进行复杂发现。适用于计数、精确序列匹配和多数据库查询。
    -   参考 [SPARQL 示例](references/sparql_examples.md)。
-   **`map`**: 在 UniProt 和 100 多个数据库之间转换 ID。适用于 ID 映射任务。
    -   参考 [ID 映射文档](references/id_mapping_documentation.md)。
    -   **`search` vs. `map`**: 在用户未明确要求的情况下，先尝试 `search`，然后再使用 `map`。例如，外部 ID 可能在 UniParc 中可搜索，但无法映射到 UniProtKB。

## 工作流

### 典型的蛋白质研究工作流

复制此清单并跟踪进度：

-   [ ] 第 1 步：确定目标蛋白质和生物体。
-   [ ] 第 2 步：在 UniProtKB 中搜索已审核的条目 (`reviewed:true`)。
-   [ ] 第 3 步：如果没有已审核的条目，搜索未审核的或使用 UniParc 进行序列发现。
-   [ ] 第 4 步：如有必要，将外部 ID（例如，Ensembl、PDB）映射到 UniProt 访问号。
-   [ ] 第 5 步：以所需格式（JSON、FASTA）检索功能元数据或序列。

### 处理搜索失败（例如，非模式生物体的基因搜索）

如果直接查询（例如，`gene:SYMBOL`）失败：

1.  **转向蛋白质名称**: 搜索常见的蛋白质名称（例如，`protein_name:Alpha-crystallin A`）。
2.  **使用 UniParc**: 搜索 UniParc 数据集，该数据集集成了来自所有生命形式的序列，即使它们在 UniProtKB 中未完全注释。
3.  **检查同源/规范**: 首先解决人类/小鼠同源体，以找到正确的命名/助记符。

### 批量检索优先级

> [!IMPORTANT] 始终优先选择 **`stream`** 或 **`sparql`** 进行批量数据。
> `search` 适用于探索；如果结果超过 500 条，它会自动分页以提供稳定的下载。

-   **优先级 0: `count`**: **始终**在运行 `search` 或 `stream` 之前检查结果计数。
-   **优先级 1: `stream`**: 批量数据检索的主要方法（最多 10M 条）。不支持 `--limit`；始终返回所有结果。
-   **优先级 2: `sparql`**: 适用于检索期间的复杂过滤和精确匹配。

### 基于序列的搜索（精确匹配）

> [!IMPORTANT] 通过其完整氨基酸序列搜索蛋白质时使用 **SPARQL**。REST API `/search` 端点不支持直接序列字符串查找。对于任何非精确匹配，请使用专门的序列相似性搜索技能。如果无法在 UniProt 中找到查询，请使用 UniParc。

**SPARQL 查询模式（UniProt）:**

```text
PREFIX up: <http://purl.uniprot.org/core/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT ?protein ?name WHERE {
  ?protein a up:Protein ;
           up:sequence/rdf:value "SEQUENCE_HERE" .
  OPTIONAL {
    ?protein up:recommendedName/up:fullName ?name .
  }
}
```

**SPARQL 查询模式（UniParc）:**

```text
PREFIX up: <http://purl.uniprot.org/core/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?uniparc ?val WHERE {
  GRAPH <http://sparql.uniprot.org/uniparc> {
    ?uniparc a up:Sequence ;
             rdf:value ?val .
    FILTER (?val = "SEQUENCE_HERE")
  }
}
```

### 高效计数条目

> [!IMPORTANT] 使用 **`count`** 或 **`SPARQL`** 进行条目计数（例如，“人类中有多少蛋白质？”）。

**计数模式（每个生物体的蛋白质）:**

```text
PREFIX up: <http://purl.uniprot.org/core/>
PREFIX taxon: <http://purl.uniprot.org/taxonomy/>
SELECT (COUNT(?protein) AS ?count) WHERE {
  ?protein a up:Protein ;
           up:reviewed true ;
           up:organism taxon:9606 .
}
```

### REST 搜索语法

-   **列表中无逗号**: 逗号被视为文字。使用大写的 `OR` 分隔项目。
    *   分组：`accession:(P12345 OR P67890)`
    *   重复：`accession:P12345 OR accession:P67890`
-   **空格 = AND**: 例如，`gene:p53 human` 搜索 `gene:p53` 和 `human`。

## 示例命令

以下是 `uniprot_tools.py` 每种模式的示例命令。

计算给定查询的总条目数。

```bash
uv run scripts/uniprot_tools.py count "taxonomy_id:9606"
```

搜索条目。

```bash
uv run scripts/uniprot_tools.py search "gene:p53 AND reviewed:true" --limit 5
```

通过访问号检索单个条目。

```bash
uv run scripts/uniprot_tools.py get P04637
```

检索历史/已删除条目（UniSave）。

```bash
uv run scripts/uniprot_tools.py get P04637 --dataset unisave
```

流式传输大型结果集以进行批量检索（返回所有匹配的条目，不支持 `--limit`）。

```bash
uv run scripts/uniprot_tools.py stream "taxonomy_id:9606 AND reviewed:true" --format tsv --fields accession,gene_names > human_reviewed.tsv
```

将 ID 从一个数据库映射到另一个数据库。

```bash
uv run scripts/uniprot_tools.py map "P04637" --from_db UniProtKB_AC-ID --to_db Gene_Name
```

使用 SPARQL 执行图查询。

```bash
uv run scripts/uniprot_tools.py sparql 'PREFIX up: <http://purl.uniprot.org/core/> SELECT ?protein WHERE { ?protein a up:Protein ; up:reviewed true . } LIMIT 5'
```

## 常见错误

-   **使用 `name:` 而不是 `protein_name:`**: `name:` 不是支持的查询术语，请使用 `protein_name:`。
-   **忽略 UniParc**: 非模式生物体可能仅存在于 UniParc 中。
-   **混淆访问号与 UPI**: UniProtKB 访问号（例如，`P04637`）链接到功能元数据；UniParc ID（`UPI...`）仅用于序列。您可以使用 ID 映射工具从 UniParc ID 找到到 UniProtKB 访问号的交叉引用。
-   **在 ID 映射中使用 UniProtKB-AC 作为目标**: 使用 `UniProtKB`。
-   **放弃复杂查询**: 如果复杂搜索查询失败，请尝试使用 SPARQL 而不是放弃。
-   **未经验证使用 ID**: **永远**不要假设您知道 ID 的含义（例如，关键词、GO 术语、Pfam ID 等）。**始终**在搜索之前在 UniProt 中查找 ID 的自然语言描述/含义，以确保它匹配您的预期搜索词。
-   **忽略广泛搜索中的引用噪音**: 广泛文本搜索（`search "term"`）经常返回误报（例如，常见的维护蛋白质），因为 UniProt 搜索完整的元数据，包括出版物标题。**始终**优先选择字段特定过滤器，如 `cc_function:` 或 `protein_name:` 进行功能发现。
-   **忘记为短搜索词加引号**: 短、未加引号的术语（例如，`lanM`）可以匹配生物体名称中的子字符串（例如，*Lan*cefieldella）或其他字段。使用引号和字段前缀（例如，`gene:lanM`）以隔离真实命中。
-   **直接操作蛋白质序列**: 始终使用代码和工具进行基于序列的操作。不要尝试手动编辑、截断或修改蛋白质序列。
-   **过度使用搜索进行批量数据**: 如果 `stream` 或 `sparql` 可以完成工作，**不要**使用 `search` 来检索数百万条条目。流式传输对于非常大的数据集更高效。请注意，`stream` 有 10,000,000 个输出的硬限制，并且**不支持** `--limit`。
-   **忘记检查数据量**: **始终**在运行不带 `--limit` 的 `search` 或使用 `stream` 之前执行 `count`。无限制查询可能需要很长时间，并且如果返回数百万条条目，将消耗大量资源。
-   **在 `stream` 中使用 `--limit`**: `stream` 命令**不支持** `--limit`。如果您需要有限数量的结果，请使用 `search` 与 `--limit`。
-   **忘记许可证通知**: 在**第一次**呈现包含 UniProt 数据的结果时，不要忽视声明使用了 UniProt 数据库并建议用户查看许可条款。即使任务简洁，此归属也是必需的。
