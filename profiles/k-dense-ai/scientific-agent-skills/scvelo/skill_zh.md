# scVelo — RNA 速度分析

## 概述

scVelo 是用于单细胞 RNA 测序数据中 RNA 速度分析的领先 Python 包。它通过模拟 mRNA 剪接的动力学来推断细胞状态转换——使用未剪接（前体 mRNA）与剪接（成熟 mRNA）丰度的比率来确定每个细胞中基因是否被上调或下调。这使得无需时间序列数据即可重建发育轨迹和识别细胞命运决定。

**安装：** `uv pip install scvelo`

**关键资源：**
- 文档：https://scvelo.readthedocs.io/
- GitHub：https://github.com/theislab/scvelo
- 论文：Bergen 等人 (2020) Nature Biotechnology. PMID: 32747759

## 何时使用此技能

使用 scVelo 时：

- **从快照数据推断轨迹**：确定细胞分化的方向
- **细胞命运预测**：识别祖细胞及其下游命运
- **驱动基因鉴定**：找到其动态最能解释观察到的轨迹的基因
- **发育生物学**：模拟造血、神经发生、上皮-间质转化
- **潜在时间估计**：沿剪接动力学衍生的伪时间对细胞进行排序
- **Scanpy 的补充**：向 UMAP 嵌入添加方向信息

## 前提条件

scVelo 需要 **未剪接** 和 **剪接** RNA 的计数矩阵。这些由以下方式生成：
1. **STARsolo** 或 **kallisto|bustools** 使用 `lamanno` 模式
2. **velocyto** 命令行界面：`velocyto run10x` / `velocyto run`
3. **alevin-fry** / **simpleaf** 使用剪接/未剪接输出

数据存储在具有 `layers["spliced"]` 和 `layers["unspliced"]` 的 `AnnData` 对象中。

## 标准RNA速度工作流程

### 1. 设置和数据加载

```python
import scvelo as scv
import scanpy as sc
import numpy as np
import matplotlib.pyplot as plt

# 配置设置
scv.settings.verbosity = 3       # 显示计算步骤
scv.settings.presenter_view = True
scv.settings.set_figure_params('scvelo')

# 加载数据（具有剪接/未剪接层的 AnnData）
# 选项 A：从 loom 加载（velocyto 输出）
adata = scv.read("cellranger_output.loom", cache=True)

# 选项 B：合并 velocyto loom 与 Scanpy 处理的 AnnData
adata_processed = sc.read_h5ad("processed.h5ad")  # 具有 UMAP、聚类
adata_velocity = scv.read("velocyto.loom")
adata = scv.utils.merge(adata_processed, adata_velocity)

# 验证层
print(adata)
# obs × var: N × G
# layers: 'spliced', 'unspliced'（必需）
# obsm['X_umap']（必需用于可视化）
```

### 2. 预处理

```python
# 过滤和标准化。自 scVelo 0.3 起，filter_and_normalize() 仅过滤基因并按细胞进行标准化——它不再接受 n_top_genes 且不再进行对数转换，因此对数步骤和 HVG 选择来自 Scanpy。
scv.pp.filter_and_normalize(
    adata,
    min_shared_counts=20    # 剪接+未剪接中的最小计数
)
sc.pp.log1p(adata)
sc.pp.highly_variable_genes(adata, n_top_genes=2000, subset=True)

# 计算一阶和二阶矩（均值和方差）
# knn_connectivities 必须首先计算
sc.pp.neighbors(adata, n_neighbors=30, n_pcs=30)
scv.pp.moments(
    adata,
    n_pcs=30,
    n_neighbors=30
)
```

### 3. 速度估计——随机模型

随机模型速度快，适合探索性分析：

```python
# 随机速度（更快，精度较低）
scv.tl.velocity(adata, mode='stochastic')
scv.tl.velocity_graph(adata)

# 可视化
scv.pl.velocity_embedding_stream(
    adata,
    basis='umap',
    color='leiden',
    title="RNA 速度（随机）"
)
```

### 4. 速度估计——动态模型（推荐）

动态模型拟合完整的剪接动力学，更准确：

```python
# 恢复动力学（计算密集；10K 细胞约需 10-30 分钟）
scv.tl.recover_dynamics(adata, n_jobs=4)

# 从动态模型计算速度
scv.tl.velocity(adata, mode='dynamical')
scv.tl.velocity_graph(adata)
```

### 5. 潜在时间

动态模型能够计算共享的潜在时间（伪时间）：

```python
# 计算潜在时间
scv.tl.latent_time(adata)

# 在 UMAP 上可视化潜在时间
scv.pl.scatter(
    adata,
    color='latent_time',
    color_map='gnuplot',
    size=80,
    title='潜在时间'
)

# 按潜在时间排序的顶部基因
top_genes = adata.var['fit_likelihood'].sort_values(ascending=False).index[:300]
scv.pl.heatmap(
    adata,
    var_names=top_genes,
    sortby='latent_time',
    col_color='leiden',
    n_convolve=100
)
```

### 6. 驱动基因分析

```python
# 识别速度拟合最高的基因
scv.tl.rank_velocity_genes(adata, groupby='leiden', min_corr=0.3)
df = scv.DataFrame(adata.uns['rank_velocity_genes']['names'])
print(df.head(10))

# 速度和一致性
scv.tl.velocity_confidence(adata)
scv.pl.scatter(
    adata,
    c=['velocity_length', 'velocity_confidence'],
    cmap='coolwarm',
    perc=[5, 95]
)

# 特定基因的相空间图
scv.pl.velocity(adata, ['Cpe', 'Gnao1', 'Ins2'],
               ncols=3, figsize=(16, 4))
```

### 7. 速度箭头和伪时间

```python
# UMAP 上的箭头图
scv.pl.velocity_embedding(
    adata,
    arrow_length=3,
    arrow_size=2,
    color='leiden',
    basis='umap'
)

# 流图（更清晰的可视化）
scv.pl.velocity_embedding_stream(
    adata,
    basis='umap',
    color='leiden',
    smooth=0.8,
    min_mass=4
)

# 速度伪时间（潜在时间的替代方案）
scv.tl.velocity_pseudotime(adata)
scv.pl.scatter(adata, color='velocity_pseudotime', cmap='gnuplot')
```

### 8. PAGA 轨迹图

```python
# 基于速度的转换的 PAGA 图
scv.tl.paga(adata, groups='leiden')
df = scv.get_df(adata, 'paga/transitions_confidence', precision=2).T
df.style.background_gradient(cmap='Blues').format('{:.2g}')

# 带速度的 PAGA 绘制
scv.pl.paga(
    adata,
    basis='umap',
    size=50,
    alpha=0.1,
    min_edge_width=2,
    node_size_scale=1.5
)
```

## 完整工作流程脚本

```python
import scvelo as scv
import scanpy as sc

def run_rna_velocity(adata, n_top_genes=2000, mode='dynamical', n_jobs=4):
    """
    完整 RNA 速度工作流程。

    Args:
        adata: 具有 'spliced' 和 'unspliced' 层、UMAP 在 obsm 中的 AnnData
        n_top_genes: 用于速度的顶部 HVG 数量
        mode: 'stochastic'（快速）或 'dynamical'（准确）
        n_jobs: 动态模型的并行作业

    Returns:
        具有速度信息的处理后的 AnnData
    """
    scv.settings.verbosity = 2

    # 1. 预处理（scVelo 0.3 从 filter_and_normalize 中移除了对数/HVG）
    scv.pp.filter_and_normalize(adata, min_shared_counts=20)
    sc.pp.log1p(adata)
    sc.pp.highly_variable_genes(adata, n_top_genes=n_top_genes, subset=True)

    if 'neighbors' not in adata.uns:
        sc.pp.neighbors(adata, n_neighbors=30)

    scv.pp.moments(adata, n_pcs=30, n_neighbors=30)

    # 2. 速度估计
    if mode == 'dynamical':
        scv.tl.recover_dynamics(adata, n_jobs=n_jobs)

    scv.tl.velocity(adata, mode=mode)
    scv.tl.velocity_graph(adata)

    # 3. 下游分析
    if mode == 'dynamical':
        scv.tl.latent_time(adata)
        scv.tl.rank_velocity_genes(adata, groupby='leiden', min_corr=0.3)

    scv.tl.velocity_confidence(adata)
    scv.tl.velocity_pseudotime(adata)

    return adata
```

## AnnData 中的关键输出字段

运行工作流程后，将添加以下字段：

| 位置 | 键 | 描述 |
|------|----|------|
| `adata.layers` | `velocity` | 每个基因每个细胞的 RNA 速度 |
| `adata.layers` | `fit_t` | 每个基因每个细胞的拟合潜在时间 |
| `adata.obsm` | `velocity_umap` | UMAP 上的 2D 速度向量 |
| `adata.obs` | `velocity_pseudotime` | 从速度计算的伪时间 |
| `adata.obs` | `latent_time` | 动态模型的潜在时间 |
| `adata.obs` | `velocity_length` | 每个细胞的速度 |
| `adata.obs` | `velocity_confidence` | 每个细胞的置信度分数 |
| `adata.var` | `fit_likelihood` | 基因级别的模型拟合质量 |
| `adata.var` | `fit_alpha` | 转录速率 |
| `adata.var` | `fit_beta` | 剪接速率 |
| `adata.var` | `fit_gamma` | 降解速率 |
| `adata.uns` | `velocity_graph` | 细胞间转换概率矩阵 |

## 速度模型比较

| 模型 | 速度 | 准确性 | 何时使用 |
|------|------|--------|----------|
| `stochastic` | 快速 | 中等 | 探索性；大型数据集 |
| `deterministic` | 中等 | 中等 | 简单线性动力学 |
| `dynamical` | 慢速 | 高 | 发表质量；识别驱动基因 |

## 最佳实践

- **先用随机模式进行探索**；最终分析时切换到动态模式
- **需要良好的未剪接读数覆盖率**：短读数（< 100 bp）可能无法覆盖内含子
- **至少 2,000 个细胞**：RNA 速度在细胞较少时噪声较大
- **速度应具有一致性**：箭头应遵循已知生物学；随机性表明存在问题
- **k-NN 带宽很重要**：邻居太少 → 速度噪声；太多 → 过度平滑
- **合理性检查**：祖细胞（干细胞）对于标记基因应具有高未剪接/剪接比率
- **动态模型需要不同的动力学状态**：最适合清晰的分化过程

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| 缺失未剪接层 | 重新运行 velocyto 或使用 STARsolo 与 `--soloFeatures Gene Velocyto` |
| 速度基因非常少 | 降低 `min_shared_counts`；检查测序深度 |
| 随机-looking 箭头 | 尝试不同的 `n_neighbors` 或速度模型 |
| 动态时内存错误 | 设置 `n_jobs=1`；减少 `n_top_genes` |
| 每处都有负速度 | 检查剪接/未剪接层是否未交换 |

## 额外资源

- **scVelo 文档**：https://scvelo.readthedocs.io/
- **教程笔记本**：https://scvelo.readthedocs.io/tutorials/
- **GitHub**：https://github.com/theislab/scvelo
- **论文**：Bergen V 等人 (2020) Nature Biotechnology. PMID: 32747759
- **velocyto**（预处理）：http://velocyto.org/
- **CellRank**（命运预测，扩展 scVelo）：https://cellrank.readthedocs.io/
- **dynamo**（代谢标记替代方案）：https://dynamo-release.readthedocs.io/
