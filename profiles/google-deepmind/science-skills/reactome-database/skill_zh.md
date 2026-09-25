# Reactome 分析与内容服务

## 前置条件

1.  **`uv`**: 阅读 `uv` 技能并遵循其设置说明，确保已安装 `uv` 并将其添加到 PATH 环境变量中。
2.  **用户通知**: 如果工作区根目录中不存在 `.licenses/reactome_database_LICENSE.txt` 文件，则 (1) 显著通知用户检查 https://reactome.org/license 和 https://reactome.org/cite 上的条款，然后 (2) 创建记录通知文本和时间戳的文件。

## 概述

Reactome 是一个免费、开源、经过编辑的通路数据库。该技能封装了 **分析服务** (`https://reactome.org/AnalysisService/`) 和 **内容服务** (`https://reactome.org/ContentService/`)，提供通路富集分析、标识符映射、反应详情、通路层次结构导航、图例导出、交叉引用映射和搜索功能。

## 何时使用此技能

-   对基因/蛋白质列表进行通路富集（过表达）分析
-   使用来自先前富集的令牌检索分析结果
-   识别通路分析中未找到的哪些基因或蛋白质
-   对基因表达数据与通路注释进行分析
-   在物种间映射标识符到 Reactome 实体
-   检索反应参与者（输入、输出、催化剂、调节因子）
-   导航通路层次结构并列出顶级通路
-   查找哪些复合物或集合包含特定蛋白质
-   导出通路/反应图例（PNG/SVG），并高亮显示基因
-   在不同数据库（UniProt、Ensembl 等）间交叉引用标识符
-   搜索 Reactome 知识库
-   下载分析报告（PDF、CSV、JSON）
-   比较不同物种间的通路

## 常见物种 ID

常见研究生物体的参考列表：

-   *Homo sapiens* (人类)
    -   ID: 9606
-   *Mus musculus* (小鼠)
    -   ID: 48892
-   *Rattus norvegicus* (大鼠)
    -   ID: 48895

## 常见通路 ID

常用 Reactome 通路稳定 ID 的参考列表：

-   细胞周期
    -   稳定 ID: R-HSA-1640170
    -   备注：顶级通路（广泛）
-   细胞周期，有丝分裂
    -   稳定 ID: R-HSA-69278
    -   备注：特定子通路 — 用于图例和下钻
-   免疫系统
    -   稳定 ID: R-HSA-168256
    -   备注：顶级通路
-   信号转导
    -   稳定 ID: R-HSA-162582
    -   备注：顶级通路
-   基因表达
    -   稳定 ID: R-HSA-74160
    -   备注：顶级通路
-   程序性细胞死亡
    -   稳定 ID: R-HSA-5357801
    -   备注：顶级通路

> **重要提示**: 当用户请求“细胞周期”图例或分析时，优先选择特定的 **细胞周期，有丝分裂** 通路 (`R-HSA-69278`)，除非用户明确要求顶级概述。本文档中的示例均使用 `R-HSA-69278`。

## 核心规则

1.  **始终使用 `--output`**: 每个子命令都需要 `--output <file>` 将结果写入文件。切勿依赖标准输出（stdout）来处理大量结果。
2.  **默认物种为 *Homo sapiens***: 使用 `--species` 覆盖默认值。
3.  **令牌 7 天后过期**: 将分析结果中的令牌存储起来，以便稍后无需重新提交数据即可检索。
4.  **使用 `--fdr` 和 `--pvalue` 过滤**: 富集结果可能非常庞大。使用 `--fdr 0.05` 或 `--pvalue 0.01` 过滤，以专注于具有统计学意义的通路。
5.  **标识符格式**: Reactome 自动检测包括基因符号（TP53）、UniProt（P04637）、Ensembl（ENSG00000141510）、ChEBI、OMIM、EntrezGene 以及更多标识符。
6.  **处理大量输出**: 对于返回大量数据的命令（如 `species-comparison`），使用 `--summary` 标志截断列表，以避免超出工作区文件大小限制（1MB）。
7.  **通知**: 如果使用此技能，请确保在输出中提及。

## 工具执行

CLI 工具位于 `scripts/reactome_analysis.py`。使用 `uv` 运行：

```bash
uv run scripts/reactome_analysis.py <command> [options] --output /tmp/out.json
```

**要列出所有可用的子命令和标志**，运行：

```bash
uv run scripts/reactome_analysis.py --help
```

在执行不熟悉的命令之前，使用 `--help` 验证可用的子命令或标志。

## 功能领域

### 1. 数据库信息

```bash
uv run scripts/reactome_analysis.py db-version --output /tmp/version.json
uv run scripts/reactome_analysis.py db-name --output /tmp/name.json
```

### 2. 单个标识符分析

```bash
uv run scripts/reactome_analysis.py identifier --id TP53 --output /tmp/tp53.json
uv run scripts/reactome_analysis.py identifier-projection --id TP53 --output /tmp/tp53_proj.json
```

### 3. 批量分析（富集）

提交标识符列表进行过表达或表达分析：

```bash
uv run scripts/reactome_analysis.py analyze --data "TP53,BRCA1,EGFR" --output /tmp/enrich.json
uv run scripts/reactome_analysis.py analyze --file genes.txt --output /tmp/enrich.json
uv run scripts/reactome_analysis.py analyze-projection --data "TP53,BRCA1" --output /tmp/proj.json
uv run scripts/reactome_analysis.py analyze --data "TP53,BRCA1" --fdr 0.05 --output /tmp/sig.json
```

常见选项：`--page-size`（别名 `--limit`）、`--page`（别名 `--offset`）、`--sort-by`、`--order`、`--resource`、`--species`、`--fdr`、`--pvalue`。

### 4. 基于令牌的结果检索

```bash
uv run scripts/reactome_analysis.py token-result --token TOKEN --output /tmp/result.json
uv run scripts/reactome_analysis.py token-not-found --token TOKEN --output /tmp/notfound.json
uv run scripts/reactome_analysis.py token-resources --token TOKEN --output /tmp/resources.json
uv run scripts/reactome_analysis.py token-found-entities --token TOKEN --pathway R-HSA-69278 --output /tmp/found.json
uv run scripts/reactome_analysis.py token-filter-species --token TOKEN --species-filter 9606 --output /tmp/filtered.json
uv run scripts/reactome_analysis.py token-reactions-pathway --token TOKEN --pathway R-HSA-69278 --output /tmp/rxns.json
```

### 5. 下载结果

```bash
uv run scripts/reactome_analysis.py download-result --token TOKEN --output /tmp/full.json
uv run scripts/reactome_analysis.py download-pathways --token TOKEN --output /tmp/pathways.csv
uv run scripts/reactome_analysis.py download-found --token TOKEN --output /tmp/found.csv
uv run scripts/reactome_analysis.py download-not-found --token TOKEN --output /tmp/notfound.csv
```

### 6. 标识符映射

```bash
uv run scripts/reactome_analysis.py mapping --data "TP53,BRCA1" --output /tmp/mapped.json
uv run scripts/reactome_analysis.py mapping-projection --data "TP53" --output /tmp/mapped_proj.json
```

### 7. 反应参与者与作用机制

检索反应的分子参与者（输入、输出、催化剂）：

```bash
uv run scripts/reactome_analysis.py participants --id R-HSA-6804194 --output /tmp/participants.json
uv run scripts/reactome_analysis.py participating-entities --id R-HSA-6804194 --output /tmp/entities.json
```

### 8. 复合物与集合成员

查找包含给定实体的复合物或集合：

```bash
uv run scripts/reactome_analysis.py component-of --id R-HSA-69488 --output /tmp/complexes.json
```

### 9. 通路层次结构导航

向上（祖先）或向下（包含事件）移动通路层次结构：

```bash
uv run scripts/reactome_analysis.py event-ancestors --id R-HSA-69278 --output /tmp/ancestors.json
uv run scripts/reactome_analysis.py contained-events --id R-HSA-69278 --output /tmp/steps.json
uv run scripts/reactome_analysis.py top-pathways --output /tmp/top.json
uv run scripts/reactome_analysis.py low-pathways --id R-HSA-69488 --output /tmp/low.json
```

### 10. 图例导出

导出通路或反应图例为 PNG/SVG，可选高亮显示基因：

```bash
uv run scripts/reactome_analysis.py diagram --id R-HSA-69278 --output /tmp/diagram.png
uv run scripts/reactome_analysis.py diagram --id R-HSA-69278 --highlight TP53 --output /tmp/highlighted.png
uv run scripts/reactome_analysis.py diagram --id R-HSA-69278 --format svg --output /tmp/diagram.svg
uv run scripts/reactome_analysis.py reaction-diagram --id R-HSA-6804194 --output /tmp/rxn.png
```

### 11. 交叉引用映射

解析标识符到 Reactome 内部 ID 和交叉引用：

```bash
uv run scripts/reactome_analysis.py xref-mapping --id TP53 --output /tmp/xref.json
uv run scripts/reactome_analysis.py xref-mapping-batch --data "TP53,BRCA1" --output /tmp/xrefs.json
```

### 12. 搜索

```bash
uv run scripts/reactome_analysis.py search --query "TP53 细胞凋亡" --output /tmp/results.json
```

### 13. 通过 ID 查询条目

```bash
uv run scripts/reactome_analysis.py query --id R-HSA-69278 --output /tmp/entry.json
```

### 14. 报告与物种比较

```bash
uv run scripts/reactome_analysis.py report --token TOKEN --output /tmp/report.pdf
uv run scripts/reactome_analysis.py species-comparison --species-id 48892 --output /tmp/species.json
# 使用 --summary 截断大量输出并避免超出工作区文件大小限制
uv run scripts/reactome_analysis.py species-comparison --species-id 48892 --summary --output /tmp/species.json
```

## 方案：解释基因集富集

解释基因集富集结果的逐步工作流：

1.  **提交基因列表** 并投影到人类通路：`bash uv run scripts/reactome_analysis.py analyze-projection \ --data "TP53,BRCA1,EGFR,MYC,PTEN" --fdr 0.05 --output /tmp/enrichment.json`

2.  **检查顶级通路** — 检查输出中的 `pathwaysFound`、顶级通路名称、p 值和 FDR 值。

3.  **下钻到通路** — 获取其子事件和反应详情：`bash uv run scripts/reactome_analysis.py contained-events --id R-HSA-69278 --output /tmp/steps.json uv run scripts/reactome_analysis.py participants --id <reaction_id> --output /tmp/parts.json`

4.  **可视化** — 导出带有您基因高亮显示的图例：`bash uv run scripts/reactome_analysis.py diagram --id R-HSA-69278 \ --highlight "TP53,BRCA1" --output /tmp/diagram.png`

5.  **检查层次结构** — 向上导航以查看更广泛的生物学背景：`bash uv run scripts/reactome_analysis.py event-ancestors --id R-HSA-69278 --output /tmp/ancestors.json`

6.  **交叉引用** — 映射标识符到其他数据库：`bash uv run scripts/reactome_analysis.py xref-mapping --id TP53 --output /tmp/xrefs.json`

## 参考

有关详细的 API 端点文档，请参阅 [references/api_reference.md](references/api_reference.md)。
