# CSV 数据可视化工具

## 概述

该技能可对 CSV 文件进行全面的数据可视化和分析。它提供三大核心功能：(1) 使用 Plotly 创建单个交互式可视化图表，(2) 自动化数据剖析并生成统计摘要，(3) 生成多图仪表盘。该技能专为探索性数据分析、统计报告和创建演示用可视化图表而优化。

## 何时使用此技能

当用户请求以下内容时，可调用此技能：
- "可视化这些 CSV 数据"
- "根据这些数据创建直方图/散点图/箱线图"
- "显示 [列] 的分布情况"
- "为这个数据集生成仪表盘"
- "剖析这个 CSV 文件" 或 "分析这些数据"
- "创建相关性热力图"
- "显示随时间变化的趋势"
- "比较 [变量] 在 [类别] 中的情况"

## 核心功能

### 1. 单个可视化图表

使用 `visualize_csv.py` 脚本创建特定图表类型进行详细分析。

**可用图表类型：**

**统计图表：**
```bash
# 直方图 - 数值数据的分布
python3 scripts/visualize_csv.py data.csv --histogram column_name --bins 30

# 箱线图 - 显示四分位数和异常值
python3 scripts/visualize_csv.py data.csv --boxplot column_name

# 按类别分组的箱线图
python3 scripts/visualize_csv.py data.csv --boxplot salary --group-by department

# 小提琴图 - 带概率密度的分布
python3 scripts/visualize_csv.py data.csv --violin column_name --group-by category
```

**关系分析：**
```bash
# 带自动趋势线的散点图
python3 scripts/visualize_csv.py data.csv --scatter height weight

# 带颜色和大小编码的散点图
python3 scripts/visualize_csv.py data.csv --scatter x y --color category --size value

# 所有数值列的相关性热力图
python3 scripts/visualize_csv.py data.csv --correlation
```

**时间序列：**
```bash
# 单个变量的折线图
python3 scripts/visualize_csv.py data.csv --line date sales

# 同一图表上的多个变量
python3 scripts/visualize_csv.py data.csv --line date "sales,revenue,profit"
```

**分类数据：**
```bash
# 条形图（自动统计类别）
python3 scripts/visualize_csv.py data.csv --bar category

# 构成比例的饼图
python3 scripts/visualize_csv.py data.csv --pie region
```

**输出格式：**
指定所需格式的输出文件扩展名：
```bash
# 交互式 HTML（默认）
python3 scripts/visualize_csv.py data.csv --histogram age -o output.html

# 静态图像格式
python3 scripts/visualize_csv.py data.csv --scatter x y -o plot.png
python3 scripts/visualize_csv.py data.csv --correlation -o heatmap.pdf
python3 scripts/visualize_csv.py data.csv --bar category -o chart.svg
```

### 2. 自动化数据剖析

使用 `data_profile.py` 脚本生成全面的数据质量和统计报告。

**文本报告（默认）：**
```bash
python3 scripts/data_profile.py data.csv
```

**HTML 报告：**
```bash
python3 scripts/data_profile.py data.csv -f html -o report.html
```

**JSON 报告：**
```bash
python3 scripts/data_profile.py data.csv -f json -o profile.json
```

**剖析器提供的内容：**
- 文件信息（大小、维度）
- 数据集概览（形状、内存使用、重复项）
- 按列分析（类型、缺失数据、唯一值）
- 缺失数据模式和不完整性
- 数值列的统计摘要（均值、标准差、四分位数、偏度、峰度）
- 分类列分析（频率计数、最常见/最不常见值）
- 数据质量检查（高缺失数据、重复行、常数列、高基数）

**何时使用剖析：**
在以下情况下始终建议在创建可视化前运行数据剖析：
- 用户不熟悉数据集
- 数据质量未知
- 需要确定合适的可视化类型
- 首次探索新数据集

### 3. 多图仪表盘

使用 `create_dashboard.py` 脚本创建包含多个可视化的综合仪表盘。

**自动仪表盘：**
分析数据类型并自动创建适当的可视化图表：
```bash
python3 scripts/create_dashboard.py data.csv
```

自定义输出位置：
```bash
python3 scripts/create_dashboard.py data.csv -o my_dashboard.html
```

控制图表数量：
```bash
python3 scripts/create_dashboard.py data.csv --max-plots 9
```

**从配置文件创建自定义仪表盘：**
创建指定精确图表的 JSON 配置文件：
```bash
python3 scripts/create_dashboard.py data.csv --config config.json
```

**仪表盘配置格式：**
```json
{
  "title": "销售分析仪表盘",
  "plots": [
    {"type": "histogram", "column": "revenue"},
    {"type": "box", "column": "revenue", "group_by": "region"},
    {"type": "scatter", "column": "advertising", "group_by": "revenue"},
    {"type": "bar", "column": "product_category"},
    {"type": "correlation"}
  ]
}
```

**仪表盘图表类型：**
- `histogram`：数值列的分布
- `box`：箱线图，可选按类别分组
- `scatter`：两个数值列之间的关系
- `bar`：分类值的计数
- `correlation`：数值相关性热力图

## 工作流决策树

使用此决策树确定适当方法：

```
用户提供 CSV 文件
│
├─ "剖析这些数据" / "分析这些数据" / 不熟悉的数据集
│  └─> 首先运行 data_profile.py
│     然后根据分析结果提供可视化选项
│
├─ "创建仪表盘" / "数据概览" / 需要多个可视化
│  ├─ 用户知道所需的精确图表
│  │  └─> 创建 JSON 配置 → 运行 create_dashboard.py 带配置
│  └─ 用户需要自动仪表盘
│     └─> 运行 create_dashboard.py（自动模式）
│
└─ 特定可视化请求（"直方图"、"散点图"等）
   └─> 使用 visualize_csv.py 带相应标志
```

## 最佳实践

### 开始分析
1. **始终先进行数据剖析**：`python3 scripts/data_profile.py data.csv`
2. 审查剖析输出以了解：
   - 列数据类型和范围
   - 缺失数据模式
   - 数据质量问题
   - 统计分布

### 选择可视化图表
参考 `references/visualization_guide.md` 获取详细指导。快速参考：
- **分布**：直方图、箱线图、小提琴图
- **关系**：散点图、相关性热力图
- **时间序列**：折线图
- **分类**：条形图（首选）或饼图（谨慎使用）
- **比较**：按类别分组的箱线图

### 创建仪表盘
- **自动仪表盘**：适合初步探索
- **自定义仪表盘**：更适合演示或特定分析目标
- **限制图表数量**：最多保留 6-9 个图表以保证可读性
- **逻辑分组**：将相关可视化图表组合在一起

### 输出考虑
- **HTML**：最适合交互式探索（缩放、平移、悬停工具提示）
- **PNG/PDF**：最适合报告和演示
- **SVG**：最适合需要矢量图形的出版物

## 依赖项

脚本需要以下 Python 包：
```bash
pip install pandas plotly numpy
```

用于静态图像导出（PNG、PDF、SVG），还需安装：
```bash
pip install kaleido
```

## 示例工作流

### 探索性数据分析
```bash
# 1. 剖析数据
python3 scripts/data_profile.py sales_data.csv -f html -o profile.html

# 2. 创建自动仪表盘
python3 scripts/create_dashboard.py sales_data.csv -o dashboard.html

# 3. 深入分析特定图表
python3 scripts/visualize_csv.py sales_data.csv --scatter price sales --color region
python3 scripts/visualize_csv.py sales_data.csv --boxplot revenue --group-by product
```

### 报告生成
```bash
# 创建用于报告的特定可视化
python3 scripts/visualize_csv.py data.csv --histogram age -o fig1_distribution.png
python3 scripts/visualize_csv.py data.csv --scatter income age -o fig2_correlation.png
python3 scripts/visualize_csv.py data.csv --bar category -o fig3_categories.png

# 生成数据摘要
python3 scripts/data_profile.py data.csv -f html -o data_summary.html
```

### 交互式仪表盘
```bash
# 创建用于演示的自定义仪表盘
# 1. 首先创建包含所需图表的 config.json
# 2. 生成仪表盘
python3 scripts/create_dashboard.py data.csv --config config.json -o presentation_dashboard.html
```

## 故障排除

**"列未找到" 错误**：
- 运行数据剖析以查看确切列名
- CSV 列区分大小写
- 检查列名中的前导/尾随空格

**空或错误的可视化**：
- 验证数据类型（数值 vs 分类）
- 检查绘图列中的缺失数据
- 确保有足够的非空值

**脚本执行错误**：
- 验证依赖项已安装：`pip list | grep plotly`
- 检查 Python 版本：需要 Python 3.6+
- 对于图像导出问题，安装 kaleido：`pip install kaleido`

## 资源

### scripts/
- `visualize_csv.py`：包含所有图表类型的可视化主脚本
- `data_profile.py`：自动化数据剖析和质量分析
- `create_dashboard.py`：多图仪表盘生成器

### references/
- `visualization_guide.md`：关于选择适当图表类型、最佳实践和常见模式的全面指南
