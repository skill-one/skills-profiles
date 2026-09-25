# RCSB 蛋白质数据库技能

## 前置条件

1.  **`uv`**: 阅读 `uv` 技能并遵循其安装说明，确保 `uv` 已安装并在 PATH 路径中。
2.  **用户通知**: 如果工作区根目录中不存在 `.licenses/pdb_database_LICENSE.txt` 文件，则 (1) 显著通知用户检查 https://www.rcsb.org/pages/usage-policy 上的条款，然后 (2) 创建一个记录通知文本和时间戳的文件。

## 核心规则

-   **始终优先使用提供的脚本**。仅在最后手段时使用 `curl`、`urllib`、原始 HTTP 请求或任何其他方法来访问 PDB API。脚本会自动执行所需的速率限制。
-   **始终将输出重定向到文件**。使用 `jq`、`grep` 或简短的 Python 代码片段解析输出。不要将大型 API 响应打印到 stdout，以避免截断。
-   **通知**: 如果使用此技能，请确保在输出中提及。
-   **解释你的查询** 在完成使用 PDB JSON/GraphQL 查询的任务后，用清晰的语言解释你的查询做了什么，以便用户可以纠正任何错误的假设。

## 基于属性的搜索工作流

1.  **获取相关模式** 以发现可搜索的属性名称。对于结构属性：`uv run scripts/fetch_schema.py --api search_structure --output schema_structure.txt` 对于化学属性：`uv run scripts/fetch_schema.py --api search_chemical --output schema_chemical.txt`

2.  **使用 Grep 搜索模式** 以找到相关属性。一次 Grep 一个关键词，并检查多行——有很多相似的属性，你必须为用户的意图选择**最佳匹配**。

3.  **使用发现的属性组成并运行 JSON 搜索查询**：`uv run scripts/search_pdb.py --query '<JSON>' --return_type <RETURN_TYPE> --output results.json` 使用 `--count_only` 标志获取匹配条目的数量。

### 对于步骤 2：一些基本的 PDB 概念（有助于属性选择）

-   **实体**: 结构中发现的唯一分子。
-   **实例 / 链**: 实体的特定副本。例如，如果一个结构包含两个具有相同序列的蛋白质链，它们是相同的实体，但不同的实例 / 链。
-   **组装**: 生物相关的实例 / 链集合。这可能等于已提交的结构、子集或多个副本。
-   **标签 vs 作者**: 聚合物实例获得字母标签（"A"、"B"、"AA"）及其单体编号。存在作者分配（"auth"）和 PDB 内部（"label"）的方案。标签方案更一致，并且始终在脚本和 API 中使用。但是，用户和论文可能会引用作者方案（如有必要，请澄清使用哪种方案）。
-   **化学组分**: 小分子 / 单体，其 ID 匹配 `[A-Z]{1,3}`。
-   **主要引用**: 关于结构的主要出版物。优先使用 `primary_citation` 属性而不是 `citation` 属性。
-   **分辨率**: 结构质量常用的衡量指标（越低越好）。通常优先使用 `rcsb_entry_info.resolution_combined`，它考虑了不同的实验方法。

### 对于步骤 3：示例查询

```bash
# 非人类蛋白质发表在 Nature 上，按最新排序
uv run scripts/search_pdb.py --query '{ "type": "group", "logical_operator": "and", "nodes": [ { "type": "terminal", "service": "text", "parameters": { "operator": "exact_match", "negation": true, "value": "Homo sapiens", "attribute": "rcsb_entity_source_organism.taxonomy_lineage.name" } }, { "type": "terminal", "service": "text", "parameters": { "operator": "exact_match", "value": "Nature", "attribute": "rcsb_primary_citation.rcsb_journal_abbrev" } } ] }' --return_type entry --sort_by rcsb_accession_info.initial_release_date --sort_direction desc --page_start 0 --rows 100 --output results.json
```

```bash
# 包含化学组分 CA（Ca2+ 离子）的结构
uv run scripts/search_pdb.py --query '{ "type": "terminal", "service": "text_chem", "parameters": { "operator": "exact_match", "value": "CA", "attribute": "rcsb_chem_comp_container_identifiers.comp_id" } }' --return_type entry --output results.json
```

```bash
# 具有二硫键的条目数量
uv run scripts/search_pdb.py --query '{ "type": "terminal", "service": "text", "parameters": { "operator": "exact_match", "value": "disulfide bridge", "attribute": "rcsb_polymer_struct_conn.connect_type" } }' --return_type entry --count-only --output count.json
```

常用操作符：`exact_match`、`equals`、`exists`、`contains_phrase`、`contains_words`、`in`、`greater`、`less`

## 基于相似性的搜索工作流

相似性搜索不需要获取模式。基本示例：

```bash
# 序列相似性
uv run scripts/search_pdb.py --query '{ "query": { "type": "terminal", "service": "sequence", "parameters": { "evalue_cutoff": 1, "identity_cutoff": 0.9, "sequence_type": "protein", "value": "MTEYKLVVVGAGGVGKSALTIQLIQNHFVDEYDPTIEDSYRKQ" } }, "request_options": { "scoring_strategy": "sequence" } }' --return_type polymer_entity --output results.json
```

```bash
# 结构相似性
uv run scripts/search_pdb.py --query '{ "type": "terminal", "service": "structure", "parameters": { "value": {"entry_id": "6LU7", "asym_id": "A"}, "number_of_candidates": 2000 } }' --return_type polymer_entity --output results.json
```

```bash
# 序列基序匹配
uv run scripts/search_pdb.py --query '{ "type": "terminal", "service": "seqmotif", "parameters": { "value": "C-x(2,4)-C-x(3)-[LIVMFYWC]-x(8)-H-x(3,5)-H.", "pattern_type": "prosite", "sequence_type": "protein" } }' --return_type polymer_entity --output results.json
```

```bash
# 化学描述符匹配
uv run scripts/search_pdb.py --query '{ "type": "terminal", "service": "chemical", "parameters": { "value": "InChI=1S/C8H9NO2/c1-6(10)9-7-2-4-8(11)5-3-7/h2-5,11H,1H3,(H,9,10)", "type": "descriptor", "descriptor_type": "InChI", "match_type": "graph-strict" } }' --return_type mol_definition --output results.json
```

更多详情请参阅 https://search.rcsb.org/#search-services。

## 全文搜索工作流

搜索与条目关联的**所有**文本。示例：

```bash
uv run scripts/search_pdb.py --query '{ "type": "terminal", "service": "full_text", "parameters": { "value": "isopeptide + ( collagen | fibrinogen )" } }' --return_type entry --output results.json
```

> **重要**：仅在无法使用更精确的属性搜索时，才使用 `full_text` 搜索。考虑使用 `struct.title` 或 `rcsb_pubmed_abstract_text` 属性。

## 文件下载工作流

要下载完整的 PDB 条目，请使用 `download_coordinate_files.py` 脚本。在需要访问原子坐标、被要求提供 pdb / mmcif 文件或被非特定地要求获取 PDB 代码时使用。示例：

```bash
uv run scripts/download_coordinate_files.py --ids "4HHB,6BEA" --format "mmcif" --output_dir <OUTPUT_DIR>
```

## 元数据查询工作流

当您只需要每个条目 / 实体的几条元数据时，此流程比下载完整坐标文件更高效。

1.  **获取相关对象类型的模式**。例如：`uv run scripts/fetch_schema.py --api data_entry --output schema_entry.txt`

2.  **使用 Grep 搜索相关字段**（一次一个关键词，多行）。

3.  **组成并运行 GraphQL 元数据查询**：`uv run scripts/fetch_pdb_metadata.py --query '<GraphQL>' --output results.json`

### 对于步骤 3：示例查询

```bash
# 获取结构标题和实验方法
uv run scripts/fetch_pdb_metadata.py --query '{ entries(entry_ids: ["1STP", "2JEF", "1CDG"]) { rcsb_id struct { title } exptl { method } } }' --output results.json
```

```bash
# 获取聚合物实体分类学和集群成员资格
uv run scripts/fetch_pdb_metadata.py --query '{ polymer_entities(entity_ids:["2CPK_1","3WHM_1","2D5Z_1"]) { rcsb_id rcsb_entity_source_organism { ncbi_taxonomy_id ncbi_scientific_name } rcsb_cluster_membership { cluster_id identity } } }' --output results.json
```

```bash
# 获取聚合物实体外部序列数据库访问号
uv run scripts/fetch_pdb_metadata.py --query '{ entries(entry_ids:["7NHM", "5L2G"]){ polymer_entities { rcsb_id rcsb_polymer_entity_container_identifiers { reference_sequence_identifiers { database_accession database_name } } } } }' --output results.json
```
