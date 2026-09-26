# 科学可视化

## 概述

科学可视化将数据转化为清晰、准确的图形用于发表。使用多面板布局、误差线、显著性标记和色盲安全调色板创建适合期刊发表的图形。使用matplotlib、seaborn和plotly导出为PDF/EPS/TIFF格式用于文稿。

## 何时使用此技能

当需要使用此技能时：
- 为科学文稿创建图形或可视化
- 准备用于期刊投稿（自然、科学、细胞、PLOS等）的图形
- 确保图形对色盲友好且易于访问
- 创建具有一致样式的多面板图形
- 在正确的分辨率和格式下导出图形
- 遵循特定的发表指南
- 改进现有图形以满足发表标准
- 创建需要在彩色和灰度中都能正常工作的图形

## 快速入门指南

### 基础发表质量图形

```python
import matplotlib.pyplot as plt
import numpy as np

# 应用发表样式（从scripts/style_presets.py）
from style_presets import apply_publication_style
apply_publication_style('default')

# 创建适当大小的图形（单栏=3.5英寸）
fig, ax = plt.subplots(figsize=(3.5, 2.5))

# 绘制数据
x = np.linspace(0, 10, 100)
ax.plot(x, np.sin(x), label='sin(x)')
ax.plot(x, np.cos(x), label='cos(x)')

# 正确标注单位
ax.set_xlabel('时间 (秒)')
ax.set_ylabel('幅度 (mV)')
ax.legend(frameon=False)

# 移除不必要的刻度线
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# 以发表格式保存（从scripts/figure_export.py）
from figure_export import save_publication_figure
save_publication_figure(fig, 'figure1', formats=['pdf', 'png'], dpi=300)
```

### 使用预配置样式

使用`assets/`中的matplotlib样式文件应用期刊特定样式：

```python
import matplotlib.pyplot as plt

# 选项1：直接使用样式文件
plt.style.use('assets/nature.mplstyle')

# 选项2：使用style_presets.py辅助函数
from style_presets import configure_for_journal
configure_for_journal('nature', figure_width='single')

# 现在创建图形 - 它们将自动匹配Nature规范
fig, ax = plt.subplots()
# ... 你的绘图代码 ...
```

### 使用Seaborn快速入门

对于统计图形，使用带发表样式的seaborn：

```python
import seaborn as sns
import matplotlib.pyplot as plt
from style_presets import apply_publication_style

# 应用发表样式
apply_publication_style('default')
sns.set_theme(style='ticks', context='paper', font_scale=1.1)
sns.set_palette('colorblind')

# 创建统计比较图形
fig, ax = plt.subplots(figsize=(3.5, 3))
sns.boxplot(data=df, x='treatment', y='response', 
            order=['Control', 'Low', 'High'], palette='Set2', ax=ax)
sns.stripplot(data=df, x='treatment', y='response',
              order=['Control', 'Low', 'High'], 
              color='black', alpha=0.3, size=3, ax=ax)
ax.set_ylabel('响应 (μM)')
sns.despine()

# 保存图形
from figure_export import save_publication_figure
save_publication_figure(fig, 'treatment_comparison', formats=['pdf', 'png'], dpi=300)
```

## 核心原则和最佳实践

### 1. 分辨率和文件格式

**关键要求**（详细说明见`references/publication_guidelines.md`）：
- **位图图像**（照片、显微镜）：300-600 DPI
- **线形图**（图形、图表）：600-1200 DPI或矢量格式
- **矢量格式**（首选）：PDF、EPS、SVG
- **位图格式**：TIFF、PNG（科学数据永远不要使用JPEG）

**实现：**
```python
# 使用figure_export.py脚本设置正确参数
from figure_export import save_publication_figure

# 以多种格式保存，设置正确的DPI
save_publication_figure(fig, 'myfigure', formats=['pdf', 'png'], dpi=300)

# 或为特定期刊要求保存
from figure_export import save_for_journal
save_for_journal(fig, 'figure1', journal='nature', figure_type='combination')
```

### 2. 色彩选择 - 色盲可访问性

**始终使用色盲友好调色板**（详细说明见`references/color_palettes.md`）：

**推荐：Okabe-Ito调色板**（所有类型的色盲都可区分）：
```python
# 选项1：使用assets/color_palettes.py
from color_palettes import OKABE_ITO_LIST, apply_palette
apply_palette('okabe_ito')

# 选项2：手动指定
okabe_ito = ['#E69F00', '#56B4E9', '#009E73', '#F0E442',
             '#0072B2', '#D55E00', '#CC79A7', '#000000']
plt.rcParams['axes.prop_cycle'] = plt.cycler(color=okabe_ito)
```

**对于热图/连续数据：**
- 使用感知均匀的调色板：`viridis`、`plasma`、`cividis`
- 避免红绿分离图（使用`PuOr`、`RdBu`、`BrBG`代替）
- 永远不要使用`jet`或`rainbow`调色板

**始终在灰度中测试图形以确保可解释性。**

### 3. 字体和文本

**字体指南**（详细说明见`references/publication_guidelines.md`）：
- 无衬线字体：Arial、Helvetica、Calibri
- 最终打印尺寸的最小字号：
  - 轴标签：7-9 pt
  - 刻度标签：6-8 pt
  - 面板标签：8-12 pt（加粗）
- 标签使用句子大小： "时间 (小时)"而不是"TIME (HOURS)"
- 始终在括号中包含单位

**实现：**
```python
# 全局设置字体
import matplotlib as mpl
mpl.rcParams['font.family'] = 'sans-serif'
mpl.rcParams['font.sans-serif'] = ['Arial', 'Helvetica']
mpl.rcParams['font.size'] = 8
mpl.rcParams['axes.labelsize'] = 9
mpl.rcParams['xtick.labelsize'] = 7
mpl.rcParams['ytick.labelsize'] = 7
```

### 4. 图形尺寸

**期刊特定宽度**（详细说明见`references/journal_requirements.md`）：
- **自然**：单栏 89 mm，双栏 183 mm
- **科学**：单栏 55 mm，双栏 175 mm
- **细胞**：单栏 85 mm，双栏 178 mm

**检查图形尺寸合规性：**
```python
from figure_export import check_figure_size

fig = plt.figure(figsize=(3.5, 3))  # 89 mm适用于自然
check_figure_size(fig, journal='nature')
```

### 5. 多面板图形

**最佳实践：**
- 使用粗体字母标记面板：**A**、**B**、**C**（大多数期刊使用大写，自然使用小写）
- 在所有面板中保持一致的样式
- 尽可能沿边缘对齐面板
- 在面板之间使用适当的空间

**示例实现**（完整代码见`references/matplotlib_examples.md`）：
```python
from string import ascii_uppercase

fig = plt.figure(figsize=(7, 4))
gs = fig.add_gridspec(2, 2, hspace=0.4, wspace=0.4)

ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[0, 1])
# ... 创建其他面板 ...

# 添加面板标签
for i, ax in enumerate([ax1, ax2, ...]):
    ax.text(-0.15, 1.05, ascii_uppercase[i], transform=ax.transAxes,
            fontsize=10, fontweight='bold', va='top')
```

## 常见任务

### 任务1：创建可发表的线形图

见`references/matplotlib_examples.md`示例1的完整代码。

**关键步骤：**
1. 应用发表样式
2. 设置适合目标期刊的图形大小
3. 使用色盲友好颜色
4. 添加误差线，正确表示SEM、SD或CI
5. 标注轴并包含单位
6. 移除不必要的刻度线
7. 以矢量格式保存

**使用seaborn自动计算置信区间：**
```python
import seaborn as sns
fig, ax = plt.subplots(figsize=(5, 3))
sns.lineplot(data=timeseries, x='time', y='measurement',
             hue='treatment', errorbar=('ci', 95), 
             markers=True, ax=ax)
ax.set_xlabel('时间 (小时)')
ax.set_ylabel('测量值 (AU)')
sns.despine()
```

### 任务2：创建多面板图形

见`references/matplotlib_examples.md`示例2的完整代码。

**关键步骤：**
1. 使用`GridSpec`进行灵活布局
2. 确保所有面板样式一致
3. 添加粗体面板标签（A、B、C等）
4. 对齐相关面板
5. 确保所有文本在最终尺寸下可读

### 任务3：创建具有正确调色板的热图

见`references/matplotlib_examples.md`示例4的完整代码。

**关键步骤：**
1. 使用感知均匀调色板（`viridis`、`plasma`、`cividis`）
2. 包含标记的色条
3. 对于分离数据，使用色盲安全分离图（`RdBu_r`、`PuOr`）
4. 为分离图设置适当的中心值
5. 在灰度中测试外观

**使用seaborn创建相关矩阵：**
```python
import seaborn as sns
fig, ax = plt.subplots(figsize=(5, 4))
corr = df.corr()
mask = np.triu(np.ones_like(corr, dtype=bool))  # 只显示下三角
sns.heatmap(corr, mask=mask, annot=True, fmt='.2f',
            cmap='RdBu_r', center=0, square=True,
            linewidths=1, cbar_kws={'shrink': 0.8}, ax=ax)
plt.tight_layout()
```

### 任务4：为特定期刊准备图形

**工作流程：**
1. 检查期刊要求：`references/journal_requirements.md`
2. 配置matplotlib为期刊：
   ```python
   from style_presets import configure_for_journal
   configure_for_journal('nature', figure_width='single')
   ```
3. 创建图形（将自动调整大小）
4. 按期刊规范导出：
   ```python
   from figure_export import save_for_journal
   save_for_journal(fig, 'figure1', journal='nature', figure_type='line_art')
   ```

### 任务5：修复现有图形以满足发表标准

**清单方法**（完整清单见`references/publication_guidelines.md`）：

1. **检查分辨率**：验证DPI满足期刊要求
2. **检查文件格式**：图形使用矢量格式，TIFF用于图像
3. **检查颜色**：确保色盲友好
4. **检查字体**：最终打印尺寸最小6-7 pt，无衬线
5. **检查标签**：所有轴标注包含单位
6. **检查尺寸**：匹配期刊栏宽
7. **测试灰度**：确保图形无颜色即可理解
8. **移除图表垃圾**：无不必要的网格线、3D效果、阴影

### 任务6：创建色盲友好可视化

**策略：**
1. 使用`assets/color_palettes.py`中的批准调色板
2. 添加冗余编码（线型、标记、图案）
3. 使用色盲模拟器测试
4. 确保灰度兼容性

**示例：**
```python
from color_palettes import apply_palette
import matplotlib.pyplot as plt

apply_palette('okabe_ito')

# 超越颜色添加冗余编码
line_styles = ['-', '--', '-.', ':']
markers = ['o', 's', '^', 'v']

for i, (data, label) in enumerate(datasets):
    plt.plot(x, data, linestyle=line_styles[i % 4],
             marker=markers[i % 4], label=label)
```

## 统计严谨性

**始终包含：**
- 误差线（SD、SEM或CI - 在图例中说明）
- 样本量（n）在图形或图例中
- 统计显著性标记（*、**、***）
- 尽可能显示单个数据点（而不仅仅是汇总统计）

**示例带统计数据：**
```python
# 显示单个数据点与汇总统计
ax.scatter(x_jittered, individual_points, alpha=0.4, s=8)
ax.errorbar(x, means, yerr=sems, fmt='o', capsize=3)

# 标记显著性
ax.text(1.5, max_y * 1.1, '***', ha='center', fontsize=8)
```

## 使用不同绘图库

### Matplotlib

- 对发表细节有最大控制
- 适用于复杂的多面板图形
- 使用提供的样式文件进行一致格式化
- 见`references/matplotlib_examples.md`的示例

### Seaborn

Seaborn提供了一种高级的、面向数据集的统计图形界面，基于matplotlib。它擅长创建高质量的统计可视化，同时保持与matplotlib自定义的完全兼容性。

**科学可视化的主要优势：**
- 自动统计估计和置信区间
- 内置支持多面板图形（分面）
- 默认使用色盲友好调色板
- 使用pandas DataFrame的面向数据集API
- 将变量语义映射到视觉属性

#### 使用发表样式快速入门

始终先应用matplotlib发表样式，然后配置seaborn：

```python
import seaborn as sns
import matplotlib.pyplot as plt
from style_presets import apply_publication_style

# 应用发表样式
apply_publication_style('default')

# 配置seaborn为发表
sns.set_theme(style='ticks', context='paper', font_scale=1.1)
sns.set_palette('colorblind')  # 使用色盲安全调色板

# 创建图形
fig, ax = plt.subplots(figsize=(3.5, 2.5))
sns.scatterplot(data=df, x='x', y='y', hue='group', ax=ax)
sns.despine()  # 移除顶部和右侧刻度线
```

#### 常用于发表的绘图类型

**统计比较：**
```python
# 箱形图显示单个点以增加透明度
fig, ax = plt.subplots(figsize=(3.5, 3))
sns.boxplot(data=df, x='treatment', y='response', 
            order=['Control', 'Low', 'High'], palette='Set2', ax=ax)
sns.stripplot(data=df, x='treatment', y='response',
              order=['Control', 'Low', 'High'], 
              color='black', alpha=0.3, size=3, ax=ax)
ax.set_ylabel('响应 (μM)')
sns.despine()
```

**分布分析：**
```python
# 小提琴图比较分组
fig, ax = plt.subplots(figsize=(4, 3))
sns.violinplot(data=df, x='timepoint', y='expression',
               hue='treatment', split=True, inner='quartile', ax=ax)
ax.set_ylabel('基因表达 (AU)')
sns.despine()
```

**相关矩阵：**
```python
# 热图具有适当的色条和注释
fig, ax = plt.subplots(figsize=(5, 4))
corr = df.corr()
mask = np.triu(np.ones_like(corr, dtype=bool))  # 只显示下三角
sns.heatmap(corr, mask=mask, annot=True, fmt='.2f',
            cmap='RdBu_r', center=0, square=True,
            linewidths=1, cbar_kws={'shrink': 0.8}, ax=ax)
plt.tight_layout()
```

**时间序列带置信区间：**
```python
# 线形图自动计算置信区间
fig, ax = plt.subplots(figsize=(5, 3))
sns.lineplot(data=timeseries, x='time', y='measurement',
             hue='treatment', style='replicate',
             errorbar=('ci', 95), markers=True, dashes=False, ax=ax)
ax.set_xlabel('时间 (小时)')
ax.set_ylabel('测量值 (AU)')
sns.despine()
```

#### 使用Seaborn创建多面板图形

**使用FacetGrid进行自动分面：**
```python
# 创建分面图
g = sns.relplot(data=df, x='dose', y='response',
                hue='treatment', col='cell_line', row='timepoint',
                kind='line', height=2.5, aspect=1.2,
                errorbar=('ci', 95), markers=True)
g.set_axis_labels('剂量 (μM)', '响应 (AU)')
g.set_titles('{row_name} | {col_name}')
sns.despine()

# 以正确DPI保存
from figure_export import save_publication_figure
save_publication_figure(g.figure, 'figure_facets', 
                       formats=['pdf', 'png'], dpi=300)
```

**结合seaborn与matplotlib子图：**
```python
# 创建自定义多面板布局
fig, axes = plt.subplots(2, 2, figsize=(7, 6))

# 面板A：散点图与回归
sns.regplot(data=df, x='x', y='y', hue='group', ax=axes[0, 0])
axes[0, 0].text(-0.15, 1.05, 'A', transform=axes[0, 0].transAxes,
                fontsize=10, fontweight='bold')

# 面板B：分布比较
sns.violinplot(data=df, x='group', y='value', ax=axes[0, 1])
axes[0, 1].text(-0.15, 1.05, 'B', transform=axes[0, 1].transAxes,
                fontsize=10, fontweight='bold')

# 面板C：热图
sns.heatmap(correlation_data, cmap='viridis', ax=axes[1, 0])
axes[1, 0].text(-0.15, 1.05, 'C', transform=axes[1, 0].transAxes,
                fontsize=10, fontweight='bold')

# 面板D：时间序列
sns.lineplot(data=timeseries, x='time', y='signal', 
             hue='condition', ax=axes[1, 1])
axes[1, 1].text(-0.15, 1.05, 'D', transform=axes[1, 1].transAxes,
                fontsize=10, fontweight='bold')

plt.tight_layout()
sns.despine()
```

#### Seaborn的调色板

Seaborn包含多个色盲安全调色板：

```python
# 使用内置色盲调色板（推荐）
sns.set_palette('colorblind')

# 或指定自定义色盲安全颜色（Okabe-Ito）
okabe_ito = ['#E69F00', '#56B4E9', '#009E73', '#F0E442',
             '#0072B2', '#D55E00', '#CC79A7', '#000000']
sns.set_palette(okabe_ito)

# 对于热图和连续数据
sns.heatmap(data, cmap='viridis')  # 感知均匀
sns.heatmap(corr, cmap='RdBu_r', center=0)  # 分离图居中
```

#### 选择轴级和图形级函数

**轴级函数**（例如，`scatterplot`、`boxplot`、`heatmap`）：
- 当构建自定义多面板布局时使用
- 接受`ax=`参数进行精确放置
- 与matplotlib子图更好的集成
- 更好的图形组成控制

```python
fig, ax = plt.subplots(figsize=(3.5, 2.5))
sns.scatterplot(data=df, x='x', y='y', hue='group', ax=ax)
```

**图形级函数**（例如，`relplot`、`catplot`、`displot`）：
- 用于自动按分类变量分面
- 创建具有一致样式的完整图形
- 非常适合探索性分析
- 使用`height`和`aspect`进行尺寸调整

```python
g = sns.relplot(data=df, x='x', y='y', hue='treatment', kind='scatter',
                height=6, ratio=4, marginal_kws={'kde': True})
```

#### Seaborn的统计严谨性

Seaborn自动计算并显示不确定性：

```python
# 线形图：默认显示均值±95% CI
sns.lineplot(data=df, x='time', y='value', hue='treatment',
             errorbar=('ci', 95))  # 可以更改为'sd', 'se'等

# 条形图：显示均值带引导CI
sns.barplot(data=df, x='treatment', y='response',
            errorbar=('ci', 95), capsize=0.1)

# 始终在图例中指定误差类型：
# "误差线表示95%置信区间"
```

#### 发表准备Seaborn图形的最佳实践

1. **始终先设置发表主题：**
   ```python
   sns.set_context('paper', font_scale=1.2)  # 如有需要可增加
   ```

2. **使用色盲安全调色板：**
   ```python
   sns.set_palette('colorblind')
   ```

3. **移除不必要的元素：**
   ```python
   sns.despine()  # 移除顶部和右侧刻度线
   ```

4. **适当控制图形大小：**
   ```python
   # 轴级：使用matplotlib figsize
   fig, ax = plt.subplots(figsize=(3.5, 2.5))
   
   # 图形级：使用height和aspect
   g = sns.relplot(..., height=3, aspect=1.2)
   ```

5. **显示单个数据点（如果可能）：**
   ```python
   sns.boxplot(...)  # 汇总统计
   sns.stripplot(..., alpha=0.3)  # 单个点
   ```

6. **包含适当的标签和单位：**
   ```python
   ax.set_xlabel('时间 (小时)')
   ax.set_ylabel('表达 (AU)')
   ```

7. **以正确分辨率导出：**
   ```python
   from figure_export import save_publication_figure
   save_publication_figure(fig, 'figure_name', 
                          formats=['pdf', 'png'], dpi=300)
   ```

#### Seaborn的高级技术

**成对关系用于探索性分析：**
```python
# 快速查看所有关系
g = sns.pairplot(data=df, hue='condition', 
                 vars=['gene1', 'gene2', 'gene3'],
                 corner=True, diag_kind='kde', height=2)
```

**层次聚类热图：**
```python
# 对样本和特征进行聚类
g = sns.clustermap(expression_data, method='ward', 
                   metric='euclidean', z_score=0,
                   cmap='RdBu_r', center=0, 
                   figsize=(10, 8), 
                   row_colors=condition_colors,
                   cbar_kws={'label': 'Z-score'})
```

**联合分布带边缘：**
```python
# 双变量分布的上下文
g = sns.jointplot(data=df, x='gene1', y='gene2',
                  hue='treatment', kind='scatter',
                  height=6, ratio=4, marginal_kws={'kde': True})
```

#### Seaborn常见问题和解决方案

**问题：图例在图形区域外**
```python
g = sns.relplot(...)
g._legend.set_bbox_to_anchor((0.9, 0.5))
```

**问题：标签重叠**
```python
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
```

**问题：文本在最终尺寸下太小**
```python
sns.set_context('paper', font_scale=1.2)  # 如有需要可增加
```

#### 其他资源

有关更多seaborn详细信息，请参阅：
- `scientific-packages/seaborn/SKILL.md` - 全面seaborn文档
- `scientific-packages/seaborn/references/examples.md` - 实用用例
- `scientific-packages/seaborn/references/function_reference.md` - 完整API参考
- `scientific-packages/seaborn/references/objects_interface.md` - 现代声明式API

### Plotly

- 交互式图形用于探索
- 导出静态图像用于发表
- 配置为发表质量：
```python
fig.update_layout(
    font=dict(family='Arial, sans-serif', size=10),
    plot_bgcolor='white',
    # ... 见matplotlib_examples.md 示例8
)
fig.write_image('figure.png', scale=3)  # scale=3给出~300 DPI
```

## 资源

### 参考资料目录

**按需加载这些文件以获取详细信息：**

- **`publication_guidelines.md`**：全面最佳实践
  - 分辨率和文件格式要求
  - 字体指南
  - 布局和构图规则
  - 统计严谨性要求
  - 完整发表清单

- **`color_palettes.md`**：色彩使用指南
  - 色盲友好调色板规范（RGB值）
  - 顺序和分离色图建议
  - 可访问性测试程序
  - 领域特定调色板（基因组学、显微镜）

- **`journal_requirements.md`**：期刊特定规范
  - 出版商的技术要求
  - 文件格式和DPI规范
  - 图形尺寸要求
  - 快速参考表

- **`matplotlib_examples.md`**：实用代码示例
  - 10个完整工作示例
  - 线形图、条形图、热图、多面板图形
  - 期刊特定图形示例
  - 每个库的提示（matplotlib、seaborn、plotly）

### 脚本目录

**使用这些辅助脚本进行自动化：**

- **`figure_export.py`**：导出工具
  - `save_publication_figure()`：以正确的DPI导出多种格式
  - `save_for_journal()`：自动使用期刊特定要求
  - `check_figure_size()`：验证尺寸满足期刊规范
  - 直接运行：`python scripts/figure_export.py`查看示例

- **`style_presets.py`**：预配置样式
  - `apply_publication_style()`：应用预设样式（默认、nature、science、cell）
  - `set_color_palette()`：快速切换调色板
  - `configure_for_journal()`：一键配置期刊
  - 直接运行：`python scripts/style_presets.py`查看示例

### 资产目录

**在图形中使用这些文件：**

- **`color_palettes.py`**：可导入的颜色定义
  - 所有推荐调色板作为Python常量
  - `apply_palette()`辅助函数
  - 可以直接导入到笔记本/脚本中

- **Matplotlib样式文件**：使用`plt.style.use()`
  - `publication.mplstyle`：一般发表质量
  - `nature.mplstyle`：自然期刊规范
  - `presentation.mplstyle`：更大的字体用于海报/幻灯片

## 工作流程总结

**创建发表图形的推荐工作流程：**

1. **规划**：确定目标期刊、图形类型和内容
2. **配置**：应用适当的期刊样式
   ```python
   from style_presets import configure_for_journal
   configure_for_journal('nature', 'single')
   ```
3. **创建**：构建具有适当标签、颜色和统计的图形
4. **验证**：检查尺寸、字体、颜色、可访问性
   ```python
   from figure_export import check_figure_size
   check_figure_size(fig, journal='nature')
   ```
5. **导出**：以所需格式保存
   ```python
   from figure_export import save_for_journal
   save_for_journal(fig, 'figure1', 'nature', 'combination')
   ```
6. **审查**：在文稿环境中查看最终尺寸

## 常见错误

1. **字体太小**：文本在最终尺寸下无法阅读
2. **JPEG格式**：永远不要使用JPEG用于图形（会产生伪影）
3. **红绿颜色**：约8%的男性无法区分
4. **低分辨率**：发表中的图形像素化
5. **缺少单位**：始终标注轴的单位
6. **3D效果**：扭曲感知，完全避免
7. **图表垃圾**：移除不必要的网格线、装饰
8. **截断轴**：条形图从零开始除非有科学理由
9. **样式不一致**：同一文稿中不同图形的字体/颜色不一致
10. **没有误差线**：始终显示不确定性

## 最终清单

提交图形前请验证：

- [ ] 分辨率满足期刊要求（300+ DPI）
- [ ] 文件格式正确（矢量用于图形，TIFF用于图像）
- [ ] 图形尺寸符合期刊规范
- [ ] 所有文本在最终尺寸下可读（≥6 pt）
- [ ] 颜色色盲友好
- [ ] 图形在灰度中可理解
- [ ] 所有轴标注包含单位
- [ ] 误差线存在，图例中定义
- [ ] 面板标签存在且一致
- [ ] 无图表垃圾或3D效果
- [ ] 字体在所有图形中一致
- [ ] 清晰标记统计显著性
- [ ] 图例清晰完整

使用此技能确保科学图形符合最高的发表标准，同时保持对所有读者可访问性。
