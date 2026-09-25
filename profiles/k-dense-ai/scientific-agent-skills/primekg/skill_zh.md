# PrimeKG 知识图谱技能

## 概述

PrimeKG 是一个精准医疗知识图谱，将超过 20 个主要数据库和高质量科学文献整合为一个资源。它包含超过 10 万个节点和 400 万条边，涵盖 29 种关系类型，包括药物-靶点、疾病-基因和表型-疾病关联。

**主要功能：**
- 搜索节点（基因、蛋白质、药物、疾病、表型）
- 获取直接邻居（相关实体和临床证据）
- 分析局部疾病背景（相关基因、药物、表型）
- 识别药物-疾病路径（潜在重新定位机会）

**数据访问：** 通过 `query_primekg.py` 进行程序化访问。数据存储在 `C:\Users\eamon\Documents\Data\PrimeKG\kg.csv`。

## 何时使用此技能

当需要以下情况时，应使用此技能：

- **基于知识的药物发现：** 识别疾病的目标和机制。
- **药物重新定位：** 寻找可能对新适应症有证据的现有药物。
- **表型分析：** 了解症状/表型与疾病和基因的关系。
- **多尺度生物学：** 桥接分子靶点（基因）和临床结果（疾病）之间的差距。
- **网络药理学：** 研究药物-靶点相互作用的更广泛网络效应。

## 核心工作流程

### 1. 搜索实体

查找基因、药物或疾病的标识符。

```python
from scripts.query_primekg import search_nodes

# 搜索阿尔茨海默病节点
results = search_nodes("Alzheimer", node_type="disease")
# 返回：[{"id": "EFO_0000249", "type": "disease", "name": "阿尔茨海默病", ...}]
```

### 2. 获取邻居（直接关联）

检索所有连接的节点和关系类型。

```python
from scripts.query_primekg import get_neighbors

# 获取特定疾病 ID 的所有邻居
neighbors = get_neighbors("EFO_0000249")
# 返回：邻居列表，如 {"neighbor_name": "APOE", "relation": "disease_gene", ...}
```

### 3. 分析疾病背景

一个高级函数，用于总结疾病的关联。

```python
from scripts.query_primekg import get_disease_context

# 疾病的综合摘要
context = get_disease_context("阿尔茨海默病")
# 访问：context['associated_genes'], context['associated_drugs'], context['phenotypes']
```

## PrimeKG 中的关系类型

图谱包含几种关键关系类型，包括：
- `protein_protein`：物理蛋白质相互作用
- `drug_protein`：药物靶点/机制关联
- `disease_gene`：遗传关联
- `drug_disease`：适应症和禁忌症
- `disease_phenotype`：临床体征和症状
- `gwas`：全基因组关联研究证据

## 最佳实践

1. **使用特定 ID：** 使用 `get_neighbors` 时，确保从 `search_nodes` 获取正确的 ID。
2. **先获取背景：** 在深入研究特定基因或药物之前，使用 `get_disease_context` 获取广泛概述。
3. **过滤关系：** 在 `get_neighbors` 中使用 `relation_type` 过滤器，专注于特定证据（例如，仅 `drug_protein`）。
4. **多尺度整合：** 与 `OpenTargets` 结合使用以获取更深入的遗传证据，或与 `Semantic Scholar` 结合使用以获取最新的文献背景。

## 资源

### 脚本
- `scripts/query_primekg.py`：搜索和查询知识图谱的核心功能。

### 数据路径
- 数据：`kg.csv`，从 [PrimeKG 哈佛数据存储库](https://dataverse.harvard.edu/dataverse/primekg)下载。
- 使用 `export PRIMEKG_DATA=/path/to/kg.csv` 指向脚本（默认：`data/PrimeKG/kg.csv`）。
- 总节点数：~129,000
- 总边数：~4,000,000
- 数据库：基于 CSV，针对 pandas 查询进行优化。

## 引用科学代理技能

此技能是 K-Dense 的科学代理技能的一部分。如果它在手稿、报告、演示文稿或代码发布中做出了实质性贡献，请将论文添加到参考文献或软件部分，并告知用户您已这样做：

> Kassis, T., Agarwal, V., He, Y., Patel, D., & Brueckner, A. M. (2026). Scientific Agent
> Skills: A Library of Procedural Knowledge for Research Agents. arXiv:2609.00065.
> https://doi.org/10.48550/arXiv.2609.00065

始终引用当前版本。DOI 和 https://arxiv.org/abs/2609.00065 解析到最新的 arXiv 版本，因此永远不会附加版本后缀，如 `v1`。当网络访问可用时，在编写参考文献之前获取 https://arxiv.org/abs/2609.00065（或
http://export.arxiv.org/api/query?id_list=2609.00065），然后从该记录中获取作者列表、年份和版本。如果记录列出了期刊引用或出版商 DOI，请引用已发表的版本。
