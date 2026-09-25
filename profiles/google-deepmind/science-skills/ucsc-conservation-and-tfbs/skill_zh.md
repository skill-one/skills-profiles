# 保守评分与TFBS查询（UCSC）

此技能可访问UCSC基因组浏览器提供的进化约束评分和保守元素。它从PHAST软件包中检索评分，具体包括`phastCons`（识别功能区块）和`phyloP`（测量单个位点约束），这些评分是基于多重比对计算得出的。

使用此技能来确定非编码变异是否命中自共同祖先以来未发生变化的位点（这是一个致病性的强信号），或用于在调控元件上查找保守峰值。

## 前置条件

1.  **`uv`**：阅读`uv`技能并遵循其设置说明，确保已安装`uv`并将其添加到PATH中。
2.  **用户通知**：如果工作区根目录中不存在`.licenses/ucsc_conservation_and_tfbs_LICENSE.txt`文件，则（1）向用户显著通知检查条款，网址为https://genome.ucsc.edu/conditions.html和https://genome.ucsc.edu/goldenPath/help/api.html，然后（2）创建记录通知文本和时间戳的文件。

## 核心规则

-   **使用包装器**：始终使用提供的辅助脚本来查询数据库，而不是直接访问数据库。脚本会自动优雅地执行所需的速率限制。
-   **处理大量输出**：始终使用`--output`将输出重定向到文件。单独解析（使用jq或您自己的代码）。
-   **通知**：如果使用此技能，请确保在输出中提及这一点。

## 实用脚本

此技能包含用于从UCSC查询不同类型基因组数据的脚本：

1.  **`scripts/get_conservation.py`**：用于进化保守评分（phyloP、phastCons）。
2.  **`scripts/get_tfbs.py`**：用于转录因子结合位点（TFBS）。
3.  **`scripts/list_tracks.py`**：用于根据搜索或组约束列出可用轨道。

默认情况下始终使用`hg38`基因组组装，除非用户另有指定。

### 为特定变异获取保守性

获取单个碱基或特定碱基列表的进化约束。这对于单核苷酸变异（SNV）最理想。`phyloP`是单个碱基的最佳指标。

```bash
uv run scripts/get_conservation.py --coordinates "chr1:215867804" "chr1:215867823" --output /tmp/cons_output.json
```

### 获取区域和保守元素

识别非编码调控元件（如增强子）上的“保守峰值”，以查看ISM预测的重要性峰值是否与进化历史一致。由于HMM平滑，`phastCons`最适合功能窗口。`--conserved-elements`标志还将检索极端约束下的预定义区块。

```bash
uv run scripts/get_conservation.py --coordinates "chr8:11748914-11749085" --conserved-elements --output /tmp/region_cons.json
```

### 特定谱系约束

您可以使用`--collection`标志控制进化深度。默认值（`vertebrate`）使用**100-脊椎动物Multiz比对**，适用于hg38和hg19，与UCSC基因组浏览器的默认比较基因组学轨道匹配。

#### hg38集合

-   **`vertebrate`**（默认）：UCSC 100-脊椎动物Multiz比对。phyloP：`phyloP100way`，phastCons：`phastCons100way`。
-   **`mammal`**：Hiller实验室470路哺乳动物比对。phyloP：`phyloP470wayBW`，phastCons：`phastCons470way`。
-   **`primate`**：UCSC 30-灵长类Multiz比对。phyloP：`phyloP30way`，phastCons：`phastCons30way`。

#### hg19集合

-   **`vertebrate`**（默认）：UCSC 100-脊椎动物Multiz比对。phyloP：`phyloP100way`，phastCons：`phastCons100way`。
-   **`vertebrate46`**：UCSC 46-脊椎动物Multiz比对（遗留）。phyloP：`phyloP46wayAll`，phastCons：`phastCons46way`。
-   **`mammal`**：46路胎盘哺乳动物子集。phyloP：`phyloP46wayPlacental`，phastCons：`phastCons46wayPlacental`。
-   **`primate`**：46路灵长类子集。phyloP：`phyloP46wayPrimates`，phastCons：`phastCons46wayPrimates`。

```bash
# hg38哺乳动物（Hiller 470路）
uv run scripts/get_conservation.py --coordinates "chr5:1045330-1046172" --collection mammal --output /tmp/mammal_cons.json

# hg19使用遗留的46-脊椎动物比对
uv run scripts/get_conservation.py --coordinates "chr5:1045330-1046172" --genome hg19 --collection vertebrate46 --output /tmp/vert46_cons.json
```

### 分析进化加速

要分析特定位点是否正在经历进化加速（即比中性漂移基线进化得更快），请使用`--analyze`。这将计算`phyloP`评分的标量统计量（均值、最小值、最大值），并提供启发式布尔值`is_accelerated`以简化您的评估。

```bash
uv run scripts/get_conservation.py --coordinates "chr5:1045330-1046172" --analyze --output /tmp/accelerated_cons.json
```

### 获取转录因子结合位点（TFBS）

识别给定基因组区间内的转录因子结合位点。这对于解释可能破坏转录因子结合的非编码变异很有用。

使用`scripts/get_tfbs.py`并使用`--coordinates`和`--tracks`。您可以一次查询多个轨道。

```bash
uv run scripts/get_tfbs.py --coordinates "chr11:1001000-1010000" --tracks encRegTfbsClustered --output /tmp/tfbs_encode.json
```

JASPAR轨道可能会返回非常大的结果集。使用`--tf-filter`仅保留`TFName`字段包含给定子字符串（不区分大小写）的项目：

```bash
uv run scripts/get_tfbs.py --coordinates "chr6:36670000-36690000" --tracks jaspar2024 --tf-filter TP53 --output /tmp/tp53_sites.json
```

#### 常见验证轨道（hg38）

-   **ENCODE**：`encRegTfbsClustered`（转录因子簇）
-   **JASPAR**：`jaspar2026`，`jaspar2024`（预测的TFBS）
-   **ReMap**：`ReMapTFs`（ChIP-seq图谱）

> [!CAUTION] 像`jaspar`或`ReMap`这样的轨道如果没有年份，通常是“容器”轨道，并且会以400错误失败。始终使用特定的子轨道名称（例如，`jaspar2026`）。

### 列出可用轨道

列出可用轨道（例如不同版本的JASPAR，或纯粹是为了发现特定基因组组装存在哪些轨道）：

```bash
uv run scripts/list_tracks.py --search "jaspar" --output /tmp/jaspar_tracks.json
```

您还可以按功能组过滤：

```bash
uv run scripts/list_tracks.py --group "regulation" --output /tmp/regulation_tracks.json
```

## 反模式

*   **不要**查询哺乳动物（`--collection mammal`）约束，如果您正在显式寻找跨越所有脊椎动物的深层进化根源。使用默认的`vertebrate`集合。
*   **不要**使用此技能来确定核苷酸的祖先状态重建（此技能提供的是位点变化程度，而不是祖先核苷酸是什么）。
*   **不要**假设低保守性严格意味着中性/无用的序列；这也可能反映高局部突变率，而保守评分本身无法区分。
*   **不要**将输出打印到标准输出，或将cat运行在输出文件上。输出太大。使用jq或编写您自己的代码来解析输出文件。
*   **不要**使用hg19，除非用户明确要求。默认值应该是始终使用hg38。
