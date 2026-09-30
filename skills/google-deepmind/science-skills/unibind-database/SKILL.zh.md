---
name: unibind-database
description: 查询UniBind数据库中实验验证的转录因子（TF）结合位点。在检索直接TF-DNA相互作用数据集、下载结合位点坐标（BED/FASTA）进行本地分析，或按物种、细胞系或TF名称列出可用数据集时使用。不要用于查询特定区间、位置、基因、基序模型或表达数据。
---

# UniBind 数据库技能

UniBind 是一个包含 9 个物种直接 TF-DNA 相互作用的数据库，通过 DAMO 框架将 ChIP-seq 峰与 JASPAR TF 结合谱整合在一起。

## 前置条件

1.  **`uv`**: 阅读 `uv` 技能并按照其 Setup 指南进行操作，确保已安装 `uv` 并将其添加到 PATH 中。
2.  **用户通知**: 如果工作区根目录中不存在 `.licenses/unibind_database_LICENSE.txt`，则 (1) 醒目地通知用户检查条款，网址为 https://unibind.uio.no/ 和 https://unibind.uio.no/api/overview，然后 (2) 创建一个记录通知文本和时间戳的文件。

## 快速入门

查询命令默认将 JSON 打印到标准输出。大多数输出足够小，可以直接读取。对于大型输出 (`list_cell_lines`, `list_tfs`)，请通过 `jq` 管道提取您需要的字段。

```bash
uv run <SKILL DIR>/scripts/unibind_api.py list_species
```

`download_tfbs` 命令将 BED/FASTA 文件写入 `--output-dir`。您可以在任何查询命令中使用 `--output <path>` 可选地保存结果到文件（如果需要）。

## 核心规则

-   **使用包装器**: 始终使用提供的辅助脚本来查询数据库，而不是直接访问数据库。脚本会自动优雅地强制执行所需的速率限制。
-   **输出**: 查询命令将 JSON 打印到标准输出。大多数响应都很紧凑，可以直接读取。
-   **大型结果**: `list_cell_lines` 和 `list_tfs` 产生大型输出。请通过 `jq` 管道提取特定字段，而不是将完整输出读入上下文中。
-   **保存到文件**: 当您需要稍后引用数据或使用 `jq` 处理非常大的结果时，请使用 `--output <path>`。
-   **分页**: 使用 `--page` 和 `--page-size`（最大 1000）来分块大型结果集。
-   **排序**: 在任何列表命令上使用 `--order field_name`（用 `-` 前缀表示降序）。
-   **通知**: 如果使用此技能，请确保在输出中提及这一点。

## 实用脚本

*将 `<SKILL DIR>` 替换为此技能目录的绝对路径。*

### 1. 列出物种

```bash
uv run <SKILL DIR>/scripts/unibind_api.py list_species
```

### 2. 列出集合

```bash
uv run <SKILL DIR>/scripts/unibind_api.py list_collections
```

### 3. 列出细胞系和 TF（大型输出 — 使用 `jp`）

这些命令返回大型数据集。使用 `uvx --from jmespath jp` 仅提取您需要的字段。

```bash
uv run <SKILL DIR>/scripts/unibind_api.py list_cell_lines | uvx --from jmespath jp "results[].name"
uv run <SKILL DIR>/scripts/unibind_api.py list_tfs | uvx --from jmespath jp "results[].tf_name"
```

### 4. 列出和过滤数据集（以及特定于配置文件的数据集）

使用以下参数过滤数据集：

-   `--species`（例如，"Homo sapiens"）
-   `--tf-name`（例如，"CTCF"）
-   `--cell-line`（例如，"mESC"）
-   `--collection`（例如，Permissive, Robust）
-   `--search`（搜索词）
-   `--biological-condition`（生物条件或来源）
-   `--data-source`（数据来源，例如，"ENCODE"）
-   `--has-pvalue`（"true" 或 "false"）
-   `--identifier`（例如，"GSE60130"）
-   `--jaspar-id`（JASPAR 数据库配置文件矩阵 ID）
-   `--model`（预测模型）
-   `--summary`（摘要过滤器）
-   `--threshold-pvalue`（p 值阈值）

使用 `list_datasets` 获取标准数据集，或使用 `list_specific_datasets` 进行特定于配置文件的查询。

```bash
uv run <SKILL DIR>/scripts/unibind_api.py list_datasets --species "Homo sapiens" --tf-name "CTCF" --data-source "ENCODE"
uv run <SKILL DIR>/scripts/unibind_api.py list_specific_datasets --species "Mus musculus" --cell-line "mESC"
```

### 5. 获取数据集详情

```bash
uv run <SKILL DIR>/scripts/unibind_api.py get_dataset "EXP047889.HMLE-Twist-ER_breast_cancer.SMAD3"
```

### 6. 下载 TFBS 文件（BED / FASTA）

将数据集的所有 TFBS 文件下载到本地目录。使用 `--format bed`（默认）或 `--format fasta`。

```bash
uv run <SKILL DIR>/scripts/unibind_api.py download_tfbs "EXP047889.HMLE-Twist-ER_breast_cancer.SMAD3" --output-dir /tmp/tfbs --format bed
```

## 反模式

-   **不要**尝试使用 UniBind API 查询特定的基因组区间、位置或基因。
-   **不要**猜测或凭空想象基因组坐标。如果您正在为离线 bedtools 交集拉取本地 BED 轨迹，请始终使用 `ensembl-database` 作为外部检查。
-   **不要**用于基序模型（PFMs）。请使用 **jaspar-database** 技能。
-   **不要**用于基因表达数据。UniBind 仅存储结合事件。
-   **不要**仅从数据集列表中假设组织特异性表达。
-   **不要**使用 `cat` 将大型 JSON 输出文件读入上下文中。输出太大。请使用 `jq` 或编写自己的代码来解析输出文件。
