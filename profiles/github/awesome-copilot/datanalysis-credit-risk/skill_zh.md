# 数据清洗与变量筛选

## 快速入门

```bash
# 运行完整的数据清洗流程
python ".github/skills/datanalysis-credit-risk/scripts/example.py"
```

## 完整流程描述

数据清洗流程包含以下11个步骤，每个步骤独立执行且不删除原始数据：

1. **获取数据** - 加载并格式化原始数据
2. **组织样本分析** - 每个组织的样本数量和坏样本率统计
3. **分离OOS数据** - 将建模样本外的样本（OOS）分离
4. **过滤异常月份** - 移除坏样本数量不足或总样本数量不足的月份
5. **计算缺失率** - 计算每个特征的总体和按组织划分的缺失率
6. **移除高缺失率特征** - 移除总体缺失率超过阈值的特征
7. **移除低IV特征** - 移除总体IV过低或多个组织IV过低的特征
8. **移除高PSI特征** - 移除PSI不稳定的特征
9. **空值重要性降噪** - 使用标签置换法移除噪声特征
10. **移除高相关特征** - 基于原始增益移除高相关特征
11. **导出报告** - 生成包含所有步骤细节和统计信息的Excel报告

## 核心功能

| 功能 | 目的 | 模块 |
|------|------|----------|
| `get_dataset()` | 加载和格式化数据 | references.func |
| `org_analysis()` | 组织样本分析 | references.func |
| `missing_check()` | 计算缺失率 | references.func |
| `drop_abnormal_ym()` | 过滤异常月份 | references.analysis |
| `drop_highmiss_features()` | 移除高缺失率特征 | references.analysis |
| `drop_lowiv_features()` | 移除低IV特征 | references.analysis |
| `drop_highpsi_features()` | 移除高PSI特征 | references.analysis |
| `drop_highnoise_features()` | 空值重要性降噪 | references.analysis |
| `drop_highcorr_features()` | 移除高相关特征 | references.analysis |
| `iv_distribution_by_org()` | IV分布统计 | references.analysis |
| `psi_distribution_by_org()` | PSI分布统计 | references.analysis |
| `value_ratio_distribution_by_org()` | 值率分布统计 | references.analysis |
| `export_cleaning_report()` | 导出清洗报告 | references.analysis |

## 参数描述

### 数据加载参数
- `DATA_PATH`: 数据文件路径（最佳为parquet格式）
- `DATE_COL`: 日期列名称
- `Y_COL`: 标签列名称
- `ORG_COL`: 组织列名称
- `KEY_COLS`: 主键列名称列表

### OOS组织配置
- `OOS_ORGS`: 建模样本外的组织列表

### 异常月份过滤参数
- `min_ym_bad_sample`: 每月最小坏样本数量（默认10）
- `min_ym_sample`: 每月最小总样本数量（默认500）

### 缺失率参数
- `missing_ratio`: 总体缺失率阈值（默认0.6）

### IV参数
- `overall_iv_threshold`: 总体IV阈值（默认0.1）
- `org_iv_threshold`: 单个组织IV阈值（默认0.1）
- `max_org_threshold`: 最大允许的低IV组织数量（默认2）

### PSI参数
- `psi_threshold`: PSI阈值（默认0.1）
- `max_months_ratio`: 最大不稳定月份比例（默认1/3）
- `max_orgs`: 最大不稳定组织数量（默认6）

### 空值重要性参数
- `n_estimators`: 树的数量（默认100）
- `max_depth`: 最大树深度（默认5）
- `gain_threshold`: 增益差异阈值（默认50）

### 高相关参数
- `max_corr`: 相关性阈值（默认0.9）
- `top_n_keep`: 按原始增益排名保留的顶部N个特征（默认20）

## 输出报告

生成的Excel报告包含以下工作表：

1. **汇总** - 所有步骤的汇总信息，包括操作结果和条件
2. **机构样本统计** - 每个组织的样本数量和坏样本率
3. **分离OOS数据** - OOS样本和建模样本数量
4. **Step4-异常月份处理** - 被移除的异常月份
5. **缺失率明细** - 每个特征的总体和按组织划分的缺失率
6. **Step5-有值率分布统计** - 不同值率范围内的特征分布
7. **Step6-高缺失率处理** - 被移除的高缺失率特征
8. **Step7-IV明细** - 每个组织每个特征的IV值和总体IV值
9. **Step7-IV处理** - 不满足IV条件的特征和低IV组织
10. **Step7-IV分布统计** - 不同IV范围内的特征分布
11. **Step8-PSI明细** - 每个组织每月特征的PSI值
12. **Step8-PSI处理** - 不满足PSI条件的特征和不稳定组织
13. **Step8-PSI分布统计** - 不同PSI范围内的特征分布
14. **Step9-null importance处理** - 被移除的噪声特征
15. **Step10-高相关性剔除** - 被移除的高相关特征

## 功能特性

- **交互式输入**：每个步骤执行前可输入参数，支持默认值
- **独立执行**：每个步骤独立执行且不删除原始数据，便于对比分析
- **完整报告**：生成包含细节、统计和分布的完整Excel报告
- **多进程支持**：IV和PSI计算支持多进程加速
- **组织级分析**：支持组织级统计和建模/OOS区分
