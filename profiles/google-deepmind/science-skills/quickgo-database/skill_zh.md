# QuickGO 数据库技能

GO（基因本体）注释是标记基因功能的主要方法之一。QuickGO 是一个快速、基于网络的 GO 和证据与结论本体（ECO）浏览器，由欧洲生物信息研究所（EMBL-EBI）的基因本体注释（GOA）小组维护。

它提供了一个中央资源来探索基因产物（蛋白质、RNA 和复合物）的功能属性。它是功能注释映射的主要工具，因为它允许您将基因（例如 USH2A）链接到其特定的生物学过程（例如光刺激的感知）、分子功能和细胞组分。

## 前置条件

1.  **`uv`**: 阅读 `uv` 技能并遵循其设置说明，确保已安装 `uv` 并在 PATH 环境变量中。
2.  **用户通知**: 如果工作区根目录中不存在 `.licenses/quickgo_database_LICENSE.txt` 文件，则 (1) 醒目地通知用户检查 https://www.ebi.ac.uk/QuickGO/ 和 https://www.ebi.ac.uk/QuickGO/api/index.html 上的条款，然后 (2) 创建记录通知文本和时间戳的文件。

## 使用方法

此技能提供了一个 Python CLI 包装器 `scripts/quickgo_tool.py`，用于查询 QuickGO REST API。它处理请求的格式化、尊重速率限制以及安全存储可能很大的 JSON 响应。

## 核心规则

-   **使用包装器**: 始终使用提供的辅助脚本来查询数据库，而不是直接访问数据库。脚本会自动优雅地执行所需的速率限制。
-   **分页和限制**: 使用 `--limit 100` 和 `--page` 参数将端点限制为每页最多 100 条结果，用于大型数据集。
-   **输出文件**: 始终使用 `--output` 标志将响应保存到文件，或通过 `jq` 解析。
-   **证据代码**: 优先考虑实验证据 (`ECO:0000269`) 而不是电子证据 (`ECO:0000501`)，以避免产生噪声的预测。
-   **分类单元过滤**: 使用 `--taxonId 9606` 将结果限制为人类，当分析临床或人类基因组数据时。
-   **通知**: 如果使用此技能，请确保在输出中提及。

该工具有四个主要子命令：

1.  **`go`**: 用于检索 GO 术语信息（例如定义、祖先、后代和 slims）。参见 [参考资料/go_terms.md](references/go_terms.md)。
2.  **`annotation`**: 用于查找将基因产物与 GO 术语链接的功能注释。这是您的主要功能映射器。参见 [参考资料/annotations.md](references/annotations.md)。
3.  **`geneproduct`**: 用于将基因符号（如 `PROC`）解析为其正式的数据库标识符。参见 [参考资料/gene_products.md](references/gene_products.md)。
4.  **`eco`**: 用于证据与结论本体术语（用于注释中以指示注释是如何得出的，例如实验性 vs 电子性）。参见 [参考资料/eco_terms.md](references/eco_terms.md)。

## 常见工作流

### 1. 将基因映射到其功能（注释）

要了解一个基因的作用，您必须首先将其符号解析为 UniProtKB ID，然后查询其注释。通常最好过滤实验证据（例如 `ECO:0000269` 用于 EXP，或其他如 IDA、IMP）以避免产生噪声的电子预测。

```bash
# 第一步：为人类（9606）基因 PROC 找到 UniProtKB ID
uv run scripts/quickgo_tool.py geneproduct search --query "PROC" --taxonId 9606 --limit 5 --output proc_id.json
# （查看 proc_id.json，观察 ID 为例如 UniProtKB:P04070）

# 第二步：为该 ID 查找实验性 GO 注释
uv run scripts/quickgo_tool.py annotation search --geneProductId "UniProtKB:P04070" --taxonId 9606 --evidenceCode "ECO:0000269" --limit 50 --output proc_annotations.json
```

### 2. 查找通路中的所有基因

要查找所有注释到特定 GO 术语（例如 GO:0003700 对于“转录因子活性”）的基因：

```bash
# 查找具有此特定分子功能的的人类基因
uv run scripts/quickgo_tool.py annotation search --goId "GO:0003700" --taxonId 9606 --limit 50 --output tf_genes.json
```

### 3. 探索 GO 层次结构

要检查特定 GO 术语是否是更广泛类别的后代，或获取其定义：

```bash
# 获取术语详细信息（定义、同义词）
uv run scripts/quickgo_tool.py go terms --ids "GO:0003150" --output term_details.json

# 检查祖先（例如，GO:0001917 是否是某个子类？）
uv run scripts/quickgo_tool.py go terms --ids "GO:0001917" --relation ancestors --output term_ancestors.json
```

### 4. 创建 GO Slim 摘要

如果您有一组候选基因并希望获得高级功能摘要，可以将它们映射到预定义的 GO Slim。首先，获取基因的注释以提取其 GO ID，然后将这些 ID 传递给 slim 端点：

```bash
# 第一步：为候选基因找到 GO ID（例如，通过它们的 UniProt ID，获取它们的注释）
# ...（输出产生例如 GO:0006915,GO:0008219）

# 第二步：从这些特定的 GO ID 创建 slim 摘要
uv run scripts/quickgo_tool.py go slim --slimsToIds "GO:0005575,GO:0008150,GO:0003674" --slimsFromIds "GO:0006915,GO:0008219" --output my_slim.json
```
