# 单细胞 RNA 测序质量控制

遵循 scverse 最佳实践的单细胞 RNA 测序数据自动化质量控制工作流。

## 何时使用此技能

当用户：
- 请求对单细胞 RNA 测序数据进行质量控制 (QC)
- 想要过滤低质量细胞或评估数据质量
- 需要质量控制可视化或指标
- 要求遵循 scverse/scanpy 最佳实践
- 请求基于 MAD 的过滤或异常值检测

**支持的输入格式：**
- `.h5ad` 文件（scanpy/Python 工作流的 AnnData 格式）
- `.h5` 文件（10X Genomics Cell Ranger 输出）

**默认推荐**：除非用户有特定的自定义需求或明确要求非标准过滤逻辑，否则使用方法 1（完整工作流）。

## 方法 1：完整 QC 工作流（推荐用于标准工作流）

对于遵循 scverse 最佳实践的标准 QC，使用便利脚本 `scripts/qc_analysis.py`：

```bash
python3 scripts/qc_analysis.py input.h5ad
# 或对于 10X Genomics .h5 文件：
python3 scripts/qc_analysis.py raw_feature_bc_matrix.h5
```

该脚本会自动检测文件格式并进行适当加载。

**何时使用此方法：**
- 标准QC工作流，具有可调整的阈值（所有细胞以相同方式过滤）
- 批量处理多个数据集
- 快速探索性分析
- 用户想要“开箱即用”的解决方案

**要求：** anndata, scanpy, scipy, matplotlib, seaborn, numpy

**参数：**

使用命令行参数自定义过滤阈值和基因模式：
- `--output-dir` - 输出目录
- `--mad-counts`, `--mad-genes`, `--mad-mt` - 计数/基因/MT% 的 MAD 阈值
- `--mt-threshold` - 硬性线粒体 % 截止值
- `--min-cells` - 基因过滤阈值
- `--mt-pattern`, `--ribo-pattern`, `--hb-pattern` - 不同物种的基因名称模式

使用 `--help` 查看当前默认值。

**输出：**

默认情况下，所有文件都会保存到 `<input_basename>_qc_results/` 目录（或由 `--output-dir` 指定的目录）：
- `qc_metrics_before_filtering.png` - 过滤前的可视化
- `qc_filtering_thresholds.png` - 基于 MAD 的阈值叠加
- `qc_metrics_after_filtering.png` - 过滤后的质量指标
- `<input_basename>_filtered.h5ad` - 准备好进行下游分析的清洁、过滤数据集
- `<input_basename>_with_qc.h5ad` - 保留 QC 注释的原始数据

如果需要将输出复制给用户访问，请复制单个文件（而不是整个目录），以便用户可以直接预览。

### 工作流步骤

该脚本执行以下步骤：

1. **计算 QC 指标** - 计数深度、基因检测、线粒体/核糖体/血红蛋白含量
2. **应用基于 MAD 的过滤** - 使用计数/基因/MT% 的 MAD 阈值进行宽松的异常值检测
3. **过滤基因** - 移除在少量细胞中检测到的基因
4. **生成可视化** - 具有阈值叠加的综合前后图

## 方法 2：模块化构建块（用于自定义工作流）

对于自定义分析工作流或非标准需求，使用 `scripts/qc_core.py` 和 `scripts/qc_plotting.py` 中的模块化实用函数：

```python
# 从 scripts/ 目录运行，或者如果需要，将 scripts/ 添加到 sys.path
import anndata as ad
from qc_core import calculate_qc_metrics, detect_outliers_mad, filter_cells
from qc_plotting import plot_qc_distributions  # 仅当需要可视化时使用

adata = ad.read_h5ad('input.h5ad')
calculate_qc_metrics(adata, inplace=True)
# ... 在此处添加自定义分析逻辑
```

**何时使用此方法：**
- 需要不同工作流（跳过步骤、改变顺序、对子集应用不同阈值）
- 条件逻辑（例如，神经元与其他细胞过滤方式不同）
- 部分执行（仅指标/可视化，无过滤）
- 与更大工作流中的其他分析步骤集成
- 命令行参数无法支持的定制过滤标准

**可用的实用函数：**

从 `qc_core.py`（核心 QC 操作）：
- `calculate_qc_metrics(adata, mt_pattern, ribo_pattern, hb_pattern, inplace=True)` - 计算 QC 指标并注释 adata
- `detect_outliers_mad(adata, metric, n_mads, verbose=True)` - 基于 MAD 的异常值检测，返回布尔掩码
- `apply_hard_threshold(adata, metric, threshold, operator='>', verbose=True)` - 应用硬性截止值，返回布尔掩码
- `filter_cells(adata, mask, inplace=False)` - 应用布尔掩码过滤细胞
- `filter_genes(adata, min_cells=20, min_counts=None, inplace=True)` - 按检测过滤基因
- `print_qc_summary(adata, label='')` - 打印汇总统计数据

从 `qc_plotting.py`（可视化）：
- `plot_qc_distributions(adata, output_path, title)` - 生成综合 QC 图
- `plot_filtering_thresholds(adata, outlier_masks, thresholds, output_path)` - 可视化过滤阈值
- `plot_qc_after_filtering(adata, output_path)` - 生成过滤后图

**自定义工作流示例：**

**示例 1：仅计算指标和可视化，尚未过滤**
```python
adata = ad.read_h5ad('input.h5ad')
calculate_qc_metrics(adata, inplace=True)
plot_qc_distributions(adata, 'qc_before.png', title='初始 QC')
print_qc_summary(adata, label='过滤前')
```

**示例 2：仅应用 MT% 过滤，保留其他指标宽松**
```python
adata = ad.read_h5ad('input.h5ad')
calculate_qc_metrics(adata, inplace=True)

# 仅过滤高 MT% 细胞
high_mt = apply_hard_threshold(adata, 'pct_counts_mt', 10, operator='>')
adata_filtered = filter_cells(adata, ~high_mt)
adata_filtered.write('filtered.h5ad')
```

**示例 3：不同子集使用不同阈值**
```python
adata = ad.read_h5ad('input.h5ad')
calculate_qc_metrics(adata, inplace=True)

# 应用类型特定 QC（假设存在细胞类型元数据）
neurons = adata.obs['cell_type'] == 'neuron'
other_cells = ~neurons

# 神经元容忍更高 MT%，其他细胞使用更严格阈值
neuron_qc = apply_hard_threshold(adata[neurons], 'pct_counts_mt', 15, operator='>')
other_qc = apply_hard_threshold(adata[other_cells], 'pct_counts_mt', 8, operator='>')
```

## 最佳实践

1. **过滤要宽松** - 默认阈值有意保留大多数细胞，以避免丢失稀有群体
2. **检查可视化** - 始终在过滤前后查看，确保过滤符合生物学意义
3. **考虑数据集特定因素** - 某些组织自然具有更高的线粒体含量（例如，神经元、心肌细胞）
4. **检查基因注释** - 线粒体基因前缀因物种而异（小鼠为 mt-，人类为 MT-）
5. **如有必要，迭代** - QC 参数可能需要根据具体实验或组织类型进行调整

## 参考资料

有关详细的 QC 方法、参数合理性以及故障排除指南，请参阅 `references/scverse_qc_guidelines.md`。此参考资料提供：
- 每个QC指标的详细解释及其重要性
- 基于 MAD 的阈值的合理性以及为什么它们比固定截止值更好
- 解释 QC 可视化（直方图、小提琴图、散点图）的指南
- 物种特定的基因注释考虑
- 调整过滤参数的时机和方法
- 高级 QC 考虑（环境 RNA 校正、双细胞检测）

当用户需要更深入理解方法或需要解决 QC问题时，加载此参考资料。

## QC 后的下一步

典型的下游分析步骤：
- 环境RNA校正（SoupX, CellBender）
- 双细胞检测（scDblFinder）
- 归一化（对数归一化，scran）
- 特征选择和降维
- 聚类和细胞类型注释
