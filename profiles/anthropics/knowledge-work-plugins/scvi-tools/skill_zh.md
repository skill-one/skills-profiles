# scvi-tools 深度学习技能

本技能提供使用 scvi-tools 进行单细胞分析的深度学习指导，scvi-tools 是单细胞基因组学中概率模型的首选框架。

## 如何使用此技能

1. 从下方的模型/工作流表中确定合适的工作流
2. 阅读相应的参考文件以获取详细步骤和代码
3. 使用 `scripts/` 中的脚本避免重写常用代码
4. 如遇安装或 GPU 问题，请参考 `references/environment_setup.md`
5. 如遇调试问题，请参考 `references/troubleshooting.md`

## 何时使用此技能

- 当提及 scvi-tools、scVI、scANVI 或相关模型时
- 当需要基于深度学习的批次校正或整合时
- 当处理多模态数据（CITE-seq、多组学）时
- 当需要参考映射或标签迁移时
- 当分析 ATAC-seq 或空间转录组学数据时
- 当学习单细胞数据的潜在表示时

## 模型选择指南

| 数据类型 | 模型 | 主要应用场景 |
|---------|------|------------|
| scRNA-seq | **scVI** | 无监督整合、差异表达、插补 |
| scRNA-seq + 标签 | **scANVI** | 标签迁移、半监督整合 |
| CITE-seq（RNA+蛋白） | **totalVI** | 多模态整合、蛋白去噪 |
| scATAC-seq | **PeakVI** | 染色质可及性分析 |
| 多组学（RNA+ATAC） | **MultiVI** | 联合模态分析 |
| 空间 + scRNA 参考数据 | **DestVI** | 细胞类型解卷积 |
| RNA 速度 | **veloVI** | 转录动态 |
| 跨技术 | **sysVI** | 系统级批次校正 |

## 工作流参考文件

| 工作流 | 参考文件 | 描述 |
|-------|---------|------|
| 环境设置 | `references/environment_setup.md` | 安装、GPU、版本信息 |
| 数据准备 | `references/data_preparation.md` | 为任何模型格式化数据 |
| scRNA 整合 | `references/scrna_integration.md` | scVI/scANVI 批次校正 |
| ATAC-seq 分析 | `references/atac_peakvi.md` | PeakVI 用于可及性分析 |
| CITE-seq 分析 | `references/citeseq_totalvi.md` | totalVI 用于蛋白+RNA |
| 多组学分析 | `references/multiome_multivi.md` | MultiVI 用于 RNA+ATAC |
| 空间解卷积 | `references/spatial_deconvolution.md` | DestVI 空间分析 |
| 标签迁移 | `references/label_transfer.md` | scANVI 参考映射 |
| scArches 映射 | `references/scarches_mapping.md` | 查询到参考数据的映射 |
| 批次校正 | `references/batch_correction_sysvi.md` | 高级批次方法 |
| RNA 速度 | `references/rna_velocity_velovi.md` | veloVI 动态 |
| 故障排除 | `references/troubleshooting.md` | 常见问题和解决方案 |

## CLI 脚本

常用工作流的模块化脚本。按需串联或修改。

### 管道脚本

| 脚本 | 目的 | 使用方法 |
|------|------|---------|
| `prepare_data.py` | QC、过滤、HVG 选择 | `python scripts/prepare_data.py raw.h5ad prepared.h5ad --batch-key batch` |
| `train_model.py` | 训练任何 scvi-tools 模型 | `python scripts/train_model.py prepared.h5ad results/ --model scvi` |
| `cluster_embed.py` | 邻居、UMAP、Leiden | `python scripts/cluster_embed.py adata.h5ad results/` |
| `differential_expression.py` | 差异表达分析 | `python scripts/differential_expression.py model/ adata.h5ad de.csv --groupby leiden` |
| `transfer_labels.py` | 使用 scANVI 进行标签迁移 | `python scripts/transfer_labels.py ref_model/ query.h5ad results/` |
| `integrate_datasets.py` | 多数据集整合 | `python scripts/integrate_datasets.py results/ data1.h5ad data2.h5ad` |
| `validate_adata.py` | 检查数据兼容性 | `python scripts/validate_adata.py data.h5ad --batch-key batch` |

### 示例工作流

```bash
# 1. 验证输入数据
python scripts/validate_adata.py raw.h5ad --batch-key batch --suggest

# 2. 准备数据（QC、HVG 选择）
python scripts/prepare_data.py raw.h5ad prepared.h5ad --batch-key batch --n-hvgs 2000

# 3. 训练模型
python scripts/train_model.py prepared.h5ad results/ --model scvi --batch-key batch

# 4. 聚类和可视化
python scripts/cluster_embed.py results/adata_trained.h5ad results/ --resolution 0.8

# 5. 差异表达
python scripts/differential_expression.py results/model results/adata_clustered.h5ad results/de.csv --groupby leiden
```

### Python 工具

`scripts/model_utils.py` 提供可导入的函数用于自定义工作流：

| 函数 | 目的 |
|------|------|
| `prepare_adata()` | 数据准备（QC、HVG、层设置） |
| `train_scvi()` | 训练 scVI 或 scANVI |
| `evaluate_integration()` | 计算整合指标 |
| `get_marker_genes()` | 提取差异表达基因 |
| `save_results()` | 保存模型、数据、图像 |
| `auto_select_model()` | 推荐最佳模型 |
| `quick_clustering()` | 邻居 + UMAP + Leiden |

## 关键要求

1. **需要原始计数数据**：scvi-tools 模型需要整数计数数据
   ```python
   adata.layers["counts"] = adata.X.copy()  # 在标准化之前
   scvi.model.SCVI.setup_anndata(adata, layer="counts")
   ```

2. **HVG 选择**：使用 2000-4000 个高变基因
   ```python
   sc.pp.highly_variable_genes(adata, n_top_genes=2000, batch_key="batch", layer="counts", flavor="seurat_v3")
   adata = adata[:, adata.var['highly_variable']].copy()
   ```

3. **批次信息**：指定 batch_key 用于整合
   ```python
   scvi.model.SCVI.setup_anndata(adata, layer="counts", batch_key="batch")
   ```

## 快速决策树

```
需要整合 scRNA-seq 数据？
├── 有细胞类型标签？→ scANVI (references/label_transfer.md)
└── 无标签？→ scVI (references/scrna_integration.md)

有跨模态数据？
├── CITE-seq（RNA + 蛋白）？→ totalVI (references/citeseq_totalvi.md)
├── 多组学（RNA + ATAC）？→ MultiVI (references/multiome_multivi.md)
└── 仅 scATAC-seq？→ PeakVI (references/atac_peakvi.md)

有空间数据？
└── 需要细胞类型解卷积？→ DestVI (references/spatial_deconvolution.md)

有预训练参考模型？
└── 映射查询到参考数据？→ scArches (references/scarches_mapping.md)

需要 RNA 速度？
└── veloVI (references/rna_velocity_velovi.md)

存在强跨技术批次效应？
└── sysVI (references/batch_correction_sysvi.md)
```

## 关键资源

- [scvi-tools 文档](https://docs.scvi-tools.org/)
- [scvi-tools 教程](https://docs.scvi-tools.org/en/stable/tutorials/index.html)
- [模型中心](https://huggingface.co/scvi-tools)
- [GitHub 问题](https://github.com/scverse/scvi-tools/issues)
