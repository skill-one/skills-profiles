# AlphaFold 数据库：获取与分析

## 前置条件

1.  **`uv`**：阅读 `uv` 技能并遵循其安装说明，确保 `uv` 已安装且位于 PATH 路径中。
2.  **用户通知**：如果工作区根目录中不存在 `.licenses/alphafold_database_fetch_and_analyze_LICENSE.txt` 文件，则 (1) 醒目地通知用户检查 https://alphafold.ebi.ac.uk/ 上的条款，然后 (2) 创建记录通知文本和时间戳的文件。

## 概述

从 AlphaFold 数据库下载给定 UniProt ID 的 AlphaFold 预测结构 (mmCIF) 和预测对齐误差 (PAE) 矩阵，然后对结构置信度 (pLDDT)、内在无序区域、刚性结构域边界和结构域间柔性进行自动启发式分析。

**禁止使用场景**：

-   用户仅拥有蛋白质名称、基因名称或氨基酸序列（没有 UniProt ID）——请指导他们在 [UniProt](https://www.uniprot.org) 上查找 ID。
-   用户想要搜索结构同源物（使用 **Foldseek**）。
-   用户想要在自定义序列上运行 AlphaFold 预测。
-   用户需要实验性 PDB 结构（使用 **RCSB PDB**）。

## 核心规则

-   **使用封装器**：始终使用提供的辅助脚本来查询数据库，而不是直接访问数据库。脚本会自动优雅地执行所需的速率限制。
-   不要尝试自行计算结构域边界或评估结构无序性；始终依赖脚本提供的输出。
-   如果使用此技能，请确保在输出中提及。

## 实用脚本

**1. 获取结构文件**

下载 `.cif` 结构文件、`_predicted_aligned_error.json` 和 API 元数据 JSON (`-metadata.json`)。处理非常大的蛋白质的片段回退。

示例：

```bash
uv run scripts/fetch_structure.py P00520 -o /path/to/output/
uv run scripts/fetch_structure.py P04637 -o /path/to/custom_results/
```

始终使用绝对路径或相对于用户项目根目录的路径指定 `-o`，绝不能使用相对于技能目录的路径。

**2. 分析 pLDDT 置信度**

从 `fetch_structure.py` 生成的保存的 AFDB 元数据 JSON 文件中读取 pLDDT 置信度指标，并打印启发式置信度评估（结构化、无序、混合）。

示例：

```bash
uv run scripts/analyze_plddt.py ./data/AF-P00520-F1-metadata.json
```

**3. 分析 PAE / 结构域边界**

读取下载的 PAE JSON 文件，并使用滑动窗口 PAE 启发式方法检测刚性结构域边界。

示例：

```bash
uv run scripts/analyze_pae.py ./data/AF-P00520-F1-predicted_aligned_error_v6.json
```

## 解释输出

脚本将分析结果打印到标准输出。仔细阅读并综合结果供用户使用：

1.  **异构体/大蛋白质警告（强制）**：检查脚本输出中的任何 `[!] WARNING` 行。如果脚本报告未找到规范条目并使用了异构体，或者如果蛋白质非常大（>2700 个氨基酸），您 **必须** 醒目地告知用户此警告。不要遗漏此警告。
2.  **综合结构分析**：将“pLDDT 结论”和“PAE 结构结论”合并为单个连贯的总体摘要。描述蛋白质的整体折叠置信度、无序区域的存在及其刚性结构域布局。
3.  突出显示支持指标：
    -   总体全局 pLDDT 及置信度分数的分解（尤其是极低与极高）。
    -   结构域边界分析（不同全局结构域的数量及其特定残基范围）。
4.  **明确无序警告**：如果分析得出蛋白质高度内在无序（例如，高比例的 <50 pLDDT 或缺乏刚性结构域），请发布单独的醒目警告。建议用户不要进行全蛋白质下游结构分析（如 Foldseek 或对接）。如果无序中存在小有序结构域，建议用户将任何未来分析严格限制在那些特定残基边界内。
5.  提醒用户，每个残基的 pLDDT 嵌入在下载的 mmCIF 文件的 B-factor 列中。
