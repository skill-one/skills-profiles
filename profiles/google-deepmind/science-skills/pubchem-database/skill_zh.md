# PubChem 数据库

## 前置条件

1.  **`uv`**: 阅读 `uv` 技能并遵循其 Setup 指南，确保 `uv` 已安装并在 PATH 中。
2.  **用户通知**: 如果工作区根目录中不存在 `.licenses/pubchem_database_LICENSE.txt`，则 (1) 显著通知用户检查条款，位于 https://pubchem.ncbi.nlm.nih.gov/docs/citation-guidelines 和 https://pubchem.ncbi.nlm.nih.gov/docs/pug-rest，然后 (2) 创建记录通知文本和时间戳的文件。

## 快速入门

PubChem 查询通过一个强大的 Python 包装脚本执行，以尊重服务条款并处理复杂的 JSON 解析。此脚本允许安全的多代理使用 API。

示例：将化学名称解析为其化合物 ID (CID)

```bash
uv run scripts/pubchem_api.py resolve --name "aspirin" --output result.json
```

## 核心规则

-   **使用包装脚本**: 始终使用提供的辅助脚本来查询数据库，而不是直接访问数据库。脚本会自动优雅地执行所需的速率限制。
-   读取生成的 JSON 输出文件，并使用 jq 或代码进行处理。
-   **验证事实**: 如果用户询问 PubChem 中可以检查的特定事实，始终使用数据库查询来验证从内存中检索到的信息。不要仅依赖内部知识。
-   **通知**: 如果使用此技能，请确保在输出中提及。

## 核心功能

**1. 化合物解析（名称或 InChI 到标识符）** 将化学/商品名称或 InChI 字符串转换为 PubChem CID、SMILES 和 InChIKeys。

```bash
uv run scripts/pubchem_api.py resolve --name "ibuprofen" --output result.json
# 或者
uv run scripts/pubchem_api.py resolve --inchi "InChI=1S/C3/c1-3-2/i1+1" --output result.json
```

**2. 物理和化学性质检索** 获取计算性质（例如，MolecularWeight、XLogP、TPSA）。

```bash
uv run scripts/pubchem_api.py properties --cid 2244 --output result.json
```

**3. 同义词和商品名** 查找替代名称和品牌名称。

```bash
uv run scripts/pubchem_api.py synonyms --cid 2244 --output result.json
```

## 高级上下文

**4. 安全和危害信息（GHS）** 获取全球统一制度危害声明和处理预防措施（使用 PUG-View）。

```bash
uv run scripts/pubchem_api.py safety --cid 2244 --output result.json
```

**5. 药物和药物信息** 获取 FDA 药理学数据、作用机制和治疗效果（使用 PUG-View）。

```bash
uv run scripts/pubchem_api.py pharmacology --cid 2244 --output result.json
```

**6. 自定义标题（PUG-View）** 从 PUG-View 系统中检索任何特定标题（例如，'Geometry'、'Crystal Structures'）。

```bash
uv run scripts/pubchem_api.py view --cid 3939 --heading "Crystal Structures" --output result.json
```

**7. 图像生成** 检索 2D 化学结构图像。脚本返回一个 Markdown 格式的图像链接。

```bash
uv run scripts/pubchem_api.py image --cid 2244 --output result.json
```

## 复杂搜索和生物学

**8. 基于结构的搜索（相似性和子结构）** 查找与 SMILES 字符串相似的分子或包含特定子结构的分子。

```bash
uv run scripts/pubchem_api.py similarity --smiles "CC(=O)OC1=CC=CC=C1C(=O)O" --output result.json
```

以及

```bash
uv run scripts/pubchem_api.py substructure --smiles "C1=CC=CC=C1" --output result.json
```

**9. 生物实验和靶点相互作用** 确定化学物质与基因或蛋白质的相互作用。

```bash
uv run scripts/pubchem_api.py assays --cid 2244 --output result.json
```

## 高级用法和工作流程

**10. 参考文献交叉引用（Xrefs）** 获取与 CID 交叉引用的标识符（例如，PatentID、PubMedID）。

```bash
uv run scripts/pubchem_api.py xrefs --cid 2244 --type "PatentID" --output result.json
```

**11. 属性范围搜索** 查找特定属性范围内的 CID。支持的功能包括：`molecular_weight`、`heavy_atom_count`、`xlogp`、`tpsa`、`h_bond_donor_count`、`h_bond_acceptor_count`、`rotatable_bond_count`、`exact_mass`、`monoisotopic_mass` 和 `complexity`。

```bash
uv run scripts/pubchem_api.py range --feature molecular_weight --min 400.0 --max 400.05 --output result.json
```

**12. 自定义 PUG-REST 查询** 对 PUG-REST API 执行原始路径。

```bash
uv run scripts/pubchem_api.py query --path "compound/cid/2244/xrefs/PatentID/JSON" --output result.json
```

## 备用搜索策略

如果按名称或公式直接解析失败（例如，对于复杂化合物或特定离子）：

-   **搜索父/中性分子**: 如果搜索离子或盐，尝试搜索中性父化合物。
-   **分解复杂公式**: 如果复杂公式返回无结果，尝试搜索主要成分或配体。
-   **使用子结构或相似性搜索**: 如果您有 SMILES 字符串或可以为其生成一个，使用它来查找相关化合物。

## 复杂查询和多步骤任务

*   **自定义/复杂查询**: 更多详情，请阅读 [references/endpoints.md](references/endpoints.md) 以构建原始 PUG-REST URL。
*   **多步骤任务**: 对于复杂的任务（如药物发现工作流程），请遵循 [references/workflows.md](references/workflows.md) 中的检查清单。
