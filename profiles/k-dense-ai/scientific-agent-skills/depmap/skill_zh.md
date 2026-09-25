# DepMap — 癌症依赖图谱

## 概述

癌症依赖图谱（DepMap）项目由布罗德研究所运营，通过全基因组CRISPR敲除筛选（DepMap CRISPR）、RNA干扰（RNAi）和化合物敏感性测定（PRISM）系统性地表征数百种癌症细胞系的遗传依赖性。DepMap数据对于以下方面至关重要：
- 确定哪些基因对特定癌症类型是必需的
- 发现癌症选择性依赖（治疗靶点）
- 验证肿瘤学药物靶点
- 发现合成致死相互作用

**关键资源：**
- DepMap门户：https://depmap.org/portal/
- DepMap数据下载：https://depmap.org/portal/download/all/
- Python包：`depmap`（或通过API/下载访问）
- API：https://depmap.org/portal/api/

## 何时使用此技能

使用DepMap时：
- **靶点验证**：基因是否在具有特定突变（例如，KRAS突变）的癌细胞系中对生存至关重要？
- **生物标志物发现**：哪些基因组特征可以预测基因敲除的敏感性？
- **合成致死**：当另一个基因发生突变/缺失时，哪些基因具有选择性依赖性
- **药物敏感性**：哪些细胞系特征可以预测对化合物的反应？
- **全癌症必需性**：基因是否在所有癌症类型中普遍必需（不良靶点）或选择性必需？
- **相关性分析**：哪些基因对依赖性谱相关（协同必需）？

## 核心概念

### 依赖性分数

| 分数 | 范围 | 含义 |
|------|------|------|
| **Chronos**（CRISPR） | ~ -3 至 0+ | 负值越低 = 越必需。常见必需阈值：-1。全必需基因 ~-1 至 -2 |
| **RNAi DEMETER2** | ~ -3 至 0+ | 与Chronos相似的尺度 |
| **基因效应** | 归一化 | 归一化Chronos；-1 = 常见必需基因的中位效应 |

**关键阈值：**
- Chronos ≤ -0.5：可能依赖
- Chronos ≤ -1：强依赖（常见必需范围）

### 细胞系注释

每个细胞系具有：
- `DepMap_ID`：唯一标识符（例如，`ACH-000001`）
- `cell_line_name`：人类可读名称
- `primary_disease`：癌症类型
- `lineage`：广义组织谱系
- `lineage_subtype`：特定亚型

## 核心功能

### 1. DepMap API

```python
import requests
import pandas as pd

BASE_URL = "https://depmap.org/portal/api"

def depmap_get(endpoint, params=None):
    url = f"{BASE_URL}/{endpoint}"
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()
```

### 2. 基因依赖性分数

```python
def get_gene_dependency(gene_symbol, dataset="Chronos_Combined"):
    """获取基因在所有细胞系中的CRISPR依赖性分数。"""
    url = f"{BASE_URL}/gene"
    params = {
        "gene_id": gene_symbol,
        "dataset": dataset
    }
    response = requests.get(url, params=params)
    return response.json()

# 或者，使用/data端点：
def get_dependencies_slice(gene_symbol, dataset_name="CRISPRGeneEffect"):
    """从数据集中获取基因的依赖性切片。"""
    url = f"{BASE_URL}/data/gene_dependency"
    params = {"gene_name": gene_symbol, "dataset_name": dataset_name}
    response = requests.get(url, params=params)
    data = response.json()
    return data
```

### 3. 基于下载的分析（推荐用于大规模查询）

对于大规模分析，下载DepMap数据文件并在本地进行分析：

```python
import pandas as pd
import requests, os

def download_depmap_data(url, output_path):
    """下载DepMap数据文件。"""
    response = requests.get(url, stream=True)
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

# DepMap 24Q4数据文件（按需更新版本）
FILES = {
    "crispr_gene_effect": "https://figshare.com/ndownloader/files/...",
    # 或者从：https://depmap.org/portal/download/all/下载
    # 可用文件：
    # CRISPRGeneEffect.csv - Chronos基因效应分数
    # OmicsExpressionProteinCodingGenesTPMLogp1.csv - mRNA表达
    # OmicsSomaticMutationsMatrixDamaging.csv - 突变二元矩阵
    # OmicsCNGene.csv - 复制数
    # sample_info.csv - 细胞系元数据
}

def load_depmap_gene_effect(filepath="CRISPRGeneEffect.csv"):
    """
    加载DepMap CRISPR基因效应矩阵。
    行 = 细胞系（DepMap_ID），列 = 基因（符号（EntrezID））
    """
    df = pd.read_csv(filepath, index_col=0)
    # 仅保留基因符号作为列名
    df.columns = [col.split(" ")[0] for col in df.columns]
    return df

def load_cell_line_info(filepath="sample_info.csv"):
    """加载细胞系元数据。"""
    return pd.read_csv(filepath)
```

### 4. 确定选择性依赖性

```python
import numpy as np
import pandas as pd

def find_selective_dependencies(gene_effect_df, cell_line_info, target_gene,
                                 cancer_type=None, threshold=-0.5):
    """查找对基因选择性依赖的细胞系。"""

    # 获取目标基因的分数
    if target_gene not in gene_effect_df.columns:
        return None

    scores = gene_effect_df[target_gene].dropna()
    dependent = scores[scores <= threshold]

    # 添加细胞系信息
    result = pd.DataFrame({
        "DepMap_ID": dependent.index,
        "gene_effect": dependent.values
    }).merge(cell_line_info[["DepMap_ID", "cell_line_name", "primary_disease", "lineage"]])

    if cancer_type:
        result = result[result["primary_disease"].str.contains(cancer_type, case=False, na=False)]

    return result.sort_values("gene_effect")

# 示例用法（加载数据后）
# df_effect = load_depmap_gene_effect("CRISPRGeneEffect.csv")
# cell_info = load_cell_line_info("sample_info.csv")
# deps = find_selective_dependencies(df_effect, cell_info, "KRAS", cancer_type="Lung")
```

### 5. 生物标志物分析（基因效应与突变）

```python
import pandas as pd
from scipy import stats

def biomarker_analysis(gene_effect_df, mutation_df, target_gene, biomarker_gene):
    """
    测试生物标志物基因中的突变是否预测对目标基因的依赖性。

    Args:
        gene_effect_df: CRISPR基因效应DataFrame
        mutation_df: 二元突变DataFrame（1 = 突变）
        target_gene: 评估依赖性的基因
        biomarker_gene: 突变可能预测依赖性的基因
    """
    if target_gene not in gene_effect_df.columns or biomarker_gene not in mutation_df.columns:
        return None

    # 对齐细胞系
    common_lines = gene_effect_df.index.intersection(mutation_df.index)
    scores = gene_effect_df.loc[common_lines, target_gene].dropna()
    mutations = mutation_df.loc[scores.index, biomarker_gene]

    mutated = scores[mutations == 1]
    wt = scores[mutations == 0]

    stat, pval = stats.mannwhitneyu(mutated, wt, alternative='less')

    return {
        "target_gene": target_gene,
        "biomarker_gene": biomarker_gene,
        "n_mutated": len(mutated),
        "n_wt": len(wt),
        "mean_effect_mutated": mutated.mean(),
        "mean_effect_wt": wt.mean(),
        "pval": pval,
        "significant": pval < 0.05
    }
```

### 6. 协同必需性分析

```python
import pandas as pd

def co_essentiality(gene_effect_df, target_gene, top_n=20):
    """查找依赖性谱最相关的基因（协同必需伙伴）。"""
    if target_gene not in gene_effect_df.columns:
        return None

    target_scores = gene_effect_df[target_gene].dropna()

    correlations = {}
    for gene in gene_effect_df.columns:
        if gene == target_gene:
            continue
        other_scores = gene_effect_df[gene].dropna()
        common = target_scores.index.intersection(other_scores.index)
        if len(common) < 50:
            continue
        r = target_scores[common].corr(other_scores[common])
        if not pd.isna(r):
            correlations[gene] = r

    corr_series = pd.Series(correlations).sort_values(ascending=False)
    return corr_series.head(top_n)

# 协同必需基因通常共享生物复合物或通路
```

## 查询工作流程

### 工作流程1：针对特定癌症类型的靶点验证

1. 下载`CRISPRGeneEffect.csv`和`sample_info.csv`
2. 按癌症类型筛选细胞系
3. 计算目标基因在癌症组与其他组的平均基因效应
4. 计算选择性：依赖性对您的癌症类型有多特定？
5. 与突变、表达或CNA数据作为生物标志物进行交叉参考

### 工作流程2：合成致死筛选

1. 确定具有目标基因突变/缺失的细胞系（例如，BRCA1突变型）
2. 计算突变型与野生型细胞系中所有基因的基因效应分数
3. 确定在突变型细胞系中显著更必需的基因（合成致死伙伴）
4. 按选择性效应大小筛选

### 工作流程3：化合物敏感性分析

1. 下载PRISM化合物敏感性数据（`primary-screen-replicate-treatment-info.csv`）
2. 将化合物AUC/对数2倍变化与基因组特征相关联
3. 确定化合物敏感性的预测生物标志物

## DepMap数据文件参考

| 文件 | 描述 |
|------|------|
| `CRISPRGeneEffect.csv` | CRISPR Chronos基因效应（主要依赖性数据） |
| `CRISPRGeneEffectUnscaled.csv` | 未缩放的CRISPR分数 |
| `RNAi_merged.csv` | DEMETER2 RNAi依赖性 |
| `sample_info.csv` | 细胞系元数据（谱系、疾病等） |
| `OmicsExpressionProteinCodingGenesTPMLogp1.csv` | mRNA表达 |
| `OmicsSomaticMutationsMatrixDamaging.csv` | 损伤体细胞突变（二元） |
| `OmicsCNGene.csv` | 每个基因的复制数 |
| `PRISM_Repurposing_Primary_Screens_Data.csv` | 药物敏感性（重新定位库） |

从：https://depmap.org/portal/download/all/下载所有文件

## 最佳实践

- **使用Chronos分数**（而不是DEMETER2）进行当前的CRISPR分析——切割效率控制更好
- **区分全必需与癌症选择性**：方差低（在所有细胞系中必需）的靶点不是好的药物靶点
- **与表达数据验证**：基因在细胞系中未表达，无论实际功能如何，都会被评分为非必需
- **使用DepMap ID**进行细胞系识别——`cell_line_name`可能存在歧义
- **考虑复制数**：扩增基因可能因复制数效应（垃圾DNA假说）而显得必需
- **多重检验校正**：当全基因组计算生物标志物关联时，应用FDR校正

## 额外资源

- **DepMap门户**：https://depmap.org/portal/
- **数据下载**：https://depmap.org/portal/download/all/
- **DepMap论文**：Behan FM等（2019）Nature。PMID: 30971826
- **Chronos论文**：Dempster JM等（2021）Nature Methods。PMID: 34349281
- **GitHub**：https://github.com/broadinstitute/depmap-portal
- **Figshare**：https://figshare.com/articles/dataset/DepMap_24Q4_Public/27993966
