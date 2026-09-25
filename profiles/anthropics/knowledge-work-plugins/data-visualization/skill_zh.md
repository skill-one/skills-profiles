# 数据可视化技能

图表选择指南、Python 可视化代码模式、设计原则以及无障碍考虑，用于创建有效的数据可视化。

## 图表选择指南

### 按数据关系选择

| 你要展示的内容 | 最佳图表 | 替代方案 |
|---|---|---|
| **随时间变化趋势** | 折线图 | 面积图（如果展示累计或构成） |
| **类别间比较** | 垂直条形图 | 水平条形图（类别较多时）、吸管图 |
| **排名** | 水平条形图 | 点图、斜率图（比较两个时期） |
| **部分到整体构成** | 堆叠条形图 | 树状图（层次结构）、瓦片图 |
| **随时间变化的构成** | 堆叠面积图 | 100% 堆叠条形图（用于关注比例） |
| **分布** | 直方图 | 箱线图（比较组）、小提琴图、条形图 |
| **相关性（两个变量）** | 散点图 | 气泡图（添加第三个变量作为大小） |
| **相关性（多个变量）** | 热力图（相关矩阵） | 配对图 |
| **地理模式** | 颜色填充地图 | 气泡地图、六边形地图 |
| **流程/过程** |桑基图 | 漏斗图（顺序阶段） |
| **关系网络** | 网络图 | 和弦图 |
| **性能与目标对比** | 子弹图 | 指针图（仅单个 KPI） |
| **同时展示多个 KPI** | 小 multiples 图 | 带有单独图表的仪表盘 |

### 某些图表不适用的情况

- **饼图**：除非类别少于 6 个且精确比例不如粗略比较重要。人类在比较角度方面表现不佳。使用条形图代替。
- **3D 图表**：绝对不要使用。它们会扭曲感知且不提供任何信息。
- **双轴图表**：谨慎使用。它们可能通过暗示相关性而产生误导。如果使用，请清晰标注两个轴。
- **堆叠条形图（类别较多）**：难以比较中间部分。使用小 multiples 图或分组条形图代替。
- **环形图**：比饼图稍好，但存在相同的基本问题。最多用于单个 KPI 展示。

## Python 可视化代码模式

### 设置和样式

```python
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import pandas as pd
import numpy as np

# 专业风格设置
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({
    'figure.figsize': (10, 6),
    'figure.dpi': 150,
    'font.size': 11,
    'axes.titlesize': 14,
    'axes.titleweight': 'bold',
    'axes.labelsize': 11,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'figure.titlesize': 16,
})

# 色盲友好调色板
PALETTE_CATEGORICAL = ['#4C72B0', '#DD8452', '#55A868', '#C44E52', '#8172B3', '#937860']
PALETTE_SEQUENTIAL = 'YlOrRd'
PALETTE_DIVERGING = 'RdBu_r'
```

### 折线图（时间序列）

```python
fig, ax = plt.subplots(figsize=(10, 6))

for label, group in df.groupby('category'):
    ax.plot(group['date'], group['value'], label=label, linewidth=2)

ax.set_title('按类别展示指标趋势', fontweight='bold')
ax.set_xlabel('日期')
ax.set_ylabel('值')
ax.legend(loc='upper left', frameon=True)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# 格式化 x 轴上的日期
fig.autofmt_xdate()

plt.tight_layout()
plt.savefig('trend_chart.png', dpi=150, bbox_inches='tight')
```

### 条形图（比较）

```python
fig, ax = plt.subplots(figsize=(10, 6))

# 按值排序以便阅读
df_sorted = df.sort_values('metric', ascending=True)

bars = ax.barh(df_sorted['category'], df_sorted['metric'], color=PALETTE_CATEGORICAL[0])

# 添加值标签
for bar in bars:
    width = bar.get_width()
    ax.text(width + 0.5, bar.get_y() + bar.get_height()/2,
            f'{width:,.0f}', ha='left', va='center', fontsize=10)

ax.set_title('按类别展示指标（排序）', fontweight='bold')
ax.set_xlabel('指标值')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig('bar_chart.png', dpi=150, bbox_inches='tight')
```

### 直方图（分布）

```python
fig, ax = plt.subplots(figsize=(10, 6))

ax.hist(df['value'], bins=30, color=PALETTE_CATEGORICAL[0], edgecolor='white', alpha=0.8)

# 添加均值和中位数线
mean_val = df['value'].mean()
median_val = df['value'].median()
ax.axvline(mean_val, color='red', linestyle='--', linewidth=1.5, label=f'均值: {mean_val:,.1f}')
ax.axvline(median_val, color='green', linestyle='--', linewidth=1.5, label=f'中位数: {median_val:,.1f}')

ax.set_title('值的分布', fontweight='bold')
ax.set_xlabel('值')
ax.set_ylabel('频率')
ax.legend()
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig('histogram.png', dpi=150, bbox_inches='tight')
```

### 热力图

```python
fig, ax = plt.subplots(figsize=(10, 8))

# 转换数据为热力图格式
pivot = df.pivot_table(index='row_dim', columns='col_dim', values='metric', aggfunc='sum')

sns.heatmap(pivot, annot=True, fmt=',.0f', cmap='YlOrRd',
            linewidths=0.5, ax=ax, cbar_kws={'label': '指标值'})

ax.set_title('按行维度和列维度展示指标', fontweight='bold')
ax.set_xlabel('列维度')
ax.set_ylabel('行维度')

plt.tight_layout()
plt.savefig('heatmap.png', dpi=150, bbox_inches='tight')
```

### 小 multiples 图

```python
categories = df['category'].unique()
n_cats = len(categories)
n_cols = min(3, n_cats)
n_rows = (n_cats + n_cols - 1) // n_cols

fig, axes = plt.subplots(n_rows, n_cols, figsize=(5*n_cols, 4*n_rows), sharex=True, sharey=True)
axes = axes.flatten() if n_cats > 1 else [axes]

for i, cat in enumerate(categories):
    ax = axes[i]
    subset = df[df['category'] == cat]
    ax.plot(subset['date'], subset['value'], color=PALETTE_CATEGORICAL[i % len(PALETTE_CATEGORICAL)])
    ax.set_title(cat, fontsize=12)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

# 隐藏空的子图
for j in range(i+1, len(axes)):
    axes[j].set_visible(False)

fig.suptitle('按类别展示趋势', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('small_multiples.png', dpi=150, bbox_inches='tight')
```

### 数字格式化辅助函数

```python
def format_number(val, format_type='number'):
    """为图表标签格式化数字。"""
    if format_type == 'currency':
        if abs(val) >= 1e9:
            return f'${val/1e9:.1f}B'
        elif abs(val) >= 1e6:
            return f'${val/1e6:.1f}M'
        elif abs(val) >= 1e3:
            return f'${val/1e3:.1f}K'
        else:
            return f'${val:,.0f}'
    elif format_type == 'percent':
        return f'{val:.1f}%'
    elif format_type == 'number':
        if abs(val) >= 1e9:
            return f'{val/1e9:.1f}B'
        elif abs(val) >= 1e6:
            return f'{val/1e6:.1f}M'
        elif abs(val) >= 1e3:
            return f'{val/1e3:.1f}K'
        else:
            return f'{val:,.0f}'
    return str(val)

# 使用轴格式化器
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: format_number(x, 'currency')))
```

### 使用 Plotly 创建交互式图表

```python
import plotly.express as px
import plotly.graph_objects as go

# 简单的交互式折线图
fig = px.line(df, x='date', y='value', color='category',
              title='交互式指标趋势',
              labels={'value': '指标值', 'date': '日期'})
fig.update_layout(hovermode='x unified')
fig.write_html('interactive_chart.html')
fig.show()

# 交互式散点图，带悬停数据
fig = px.scatter(df, x='metric_a', y='metric_b', color='category',
                 size='size_metric', hover_data=['name', 'detail_field'],
                 title='相关性分析')
fig.show()
```

## 设计原则

### 颜色

- **有目的地使用颜色**：颜色应编码数据，而非装饰
- **突出故事**：使用明亮的强调色突出关键洞察；其余部分用灰色表示
- **顺序数据**：使用单色调渐变（从浅到深）表示有序值
- **发散数据**：使用双色调渐变，中间为中性色，表示具有有意义中心的数
- **分类数据**：使用不同的色调，最多 6-8 个类别前不会混淆
- **避免仅使用红/绿**：8% 的男性是红绿色盲。使用蓝/橙作为主要配对

### 字体

- **标题陈述洞察**："年收入同比增长 23%" 比 "按月展示收入" 更好
- **副标题添加上下文**：日期范围、应用的筛选、数据来源
- **轴标签易于阅读**：如果可以避免，不要将轴标签旋转 90 度。缩短或换行
- **数据标签增加精确度**：仅在关键点上使用，而不是每个条形图都使用
- **注释突出显示**：用文本注释标出特定点

### 布局

- **减少图表垃圾**：移除不携带信息的网格线、边框、背景
- **有意义地排序**：类别按值排序（不是按字母顺序），除非有自然顺序（月份、阶段）
- **适当的纵横比**：时间序列比高宽（3:1 到 2:1）；比较可以更正方形
- **留白是好的**：不要将图表挤在一起。给每个可视化留出空间

### 准确性

- **条形图从零开始**：始终如此。从 95 到 100 的条形图会夸大 5% 的差异
- **折线图可以有非零基线**：当变化范围有意义时
- **多个面板使用一致的比例**：当比较多个图表时，使用相同的轴范围
- **显示不确定性**：当数据不确定时，使用误差线、置信区间或范围
- **标注你的轴**：不要让读者猜测数字的含义

## 无障碍考虑

### 色盲

- 永远不要仅依赖颜色来区分数据系列
- 添加图案填充、不同的线型（实线、虚线、点线）或直接标签
- 使用色盲模拟器（例如 Coblis、Sim Daltonism）进行测试
- 使用色盲友好调色板：`sns.color_palette("colorblind")`

### 屏幕阅读器

- 包含描述图表关键发现的 alt 文本
- 提供与可视化一起的数据表替代方案
- 使用语义标题和标签

### 一般无障碍

- 数据元素与背景之间有足够的对比度
- 标签文字大小至少 10pt，标题至少 12pt
- 避免仅通过空间位置传达信息（添加标签）
- 考虑打印：图表在黑白情况下是否适用？

### 无障碍检查清单

在分享可视化之前：
- [ ] 图表无需颜色即可工作（图案、标签或线型区分系列）
- [ ] 文字在标准缩放级别下可读
- [ ] 标题描述洞察，而不仅仅是数据
- [ ] 轴标注了单位
- [ ] 图例清晰且位置不会遮挡数据
- [ ] 注明了数据来源和日期范围
