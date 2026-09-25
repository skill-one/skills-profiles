# PPTX操作技能

## 概述

该技能能够使用**python-pptx**库以编程方式创建、编辑和操作Microsoft PowerPoint (.pptx)演示文稿。无需手动编辑即可创建包含文本、形状、图像、图表和表格的专业幻灯片。

## 如何使用

1. 描述您想要创建或修改的演示文稿
2. 提供要包含的内容、数据或图像
3. 我将生成python-pptx代码并执行它

**示例提示：**
- "根据此大纲创建一个10张幻灯片的演示文稿"
- "在幻灯片3中添加一个图表，使用这些数据"
- "从此演示文稿中提取所有文本"
- "根据此Markdown内容生成幻灯片"

## 领域知识

### python-pptx基础

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN

# 创建新的演示文稿
prs = Presentation()

# 或打开现有演示文稿
prs = Presentation('existing.pptx')
```

### 演示文稿结构
```
演示文稿
├── slide_layouts (预定义布局)
├── slides (单个幻灯片)
│   ├── shapes (文本、图像、图表)
│   │   ├── text_frame (段落)
│   │   └── table (行、单元格)
│   └── placeholders (标题、内容)
└── slide_masters (模板)
```

### 幻灯片布局

```python
# 常用布局索引（可能因模板而异）
TITLE_SLIDE = 0
TITLE_CONTENT = 1
SECTION_HEADER = 2
TWO_CONTENT = 3
COMPARISON = 4
TITLE_ONLY = 5
BLANK = 6

# 使用布局添加幻灯片
slide_layout = prs.slide_layouts[TITLE_CONTENT]
slide = prs.slides.add_slide(slide_layout)
```

### 添加内容

#### 标题幻灯片

```python
slide_layout = prs.slide_layouts[0]  # 标题幻灯片
slide = prs.slides.add_slide(slide_layout)

title = slide.shapes.title
subtitle = slide.placeholders[1]

title.text = "季度报告"
subtitle.text = "2024年第四季度绩效回顾"
```

#### 文本内容

```python
# 使用占位符
body = slide.placeholders[1]
tf = body.text_frame
tf.text = "第一个项目符号"

# 添加更多段落
p = tf.add_paragraph()
p.text = "第二个项目符号"
p.level = 0

p = tf.add_paragraph()
p.text = "子项目符号"
p.level = 1
```

#### 文本框

```python
from pptx.util import Inches, Pt

left = Inches(1)
top = Inches(2)
width = Inches(4)
height = Inches(1)

txBox = slide.shapes.add_textbox(left, top, width, height)
tf = txBox.text_frame

p = tf.paragraphs[0]
p.text = "自定义文本框"
p.font.bold = True
p.font.size = Pt(18)
```

#### 形状

```python
from pptx.enum.shapes import MSO_SHAPE

# 矩形
shape = slide.shapes.add_shape(
    MSO_SHAPE.RECTANGLE,
    Inches(1), Inches(2),  # 左、上
    Inches(3), Inches(1.5), # 宽、高
)
shape.text = "带文本的矩形"

# 常用形状：
# MSO_SHAPE.RECTANGLE, ROUNDED_RECTANGLE
# MSO_SHAPE.OVAL, CHEVRON, ARROW_RIGHT
# MSO_SHAPE.CALLOUT_ROUNDED_RECTANGLE
```

#### 图像

```python
# 添加图像
slide.shapes.add_picture(
    'image.png',
    Inches(1), Inches(2),  # 位置
    width=Inches(4)        # 自动高度
)

# 或指定两个维度
slide.shapes.add_picture(
    'logo.png',
    Inches(8), Inches(0.5),
    Inches(1.5), Inches(0.75)
)
```

### 表格

```python
# 创建表格
rows, cols = 4, 3
left = Inches(1)
top = Inches(2)
width = Inches(8)
height = Inches(2)

table = slide.shapes.add_table(rows, cols, left, top, width, height).table

# 设置列宽
table.columns[0].width = Inches(2)
table.columns[1].width = Inches(3)
table.columns[2].width = Inches(3)

# 添加标题
headers = ['产品', '2023年第三季度销售额', '2024年第四季度销售额']
for i, header in enumerate(headers):
    cell = table.cell(0, i)
    cell.text = header
    cell.text_frame.paragraphs[0].font.bold = True

# 添加数据
data = [
    ['小部件A', '$10,000', '$12,500'],
    ['小部件B', '$8,000', '$9,200'],
    ['小部件C', '$15,000', '$18,000'],
]
for row_idx, row_data in enumerate(data, 1):
    for col_idx, value in enumerate(row_data):
        table.cell(row_idx, col_idx).text = value
```

### 图表

```python
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE

# 图表数据
chart_data = CategoryChartData()
chart_data.categories = ['第一季度', '第二季度', '第三季度', '第四季度']
chart_data.add_series('销售额', (19.2, 21.4, 16.7, 23.8))
chart_data.add_series('费用', (12.1, 15.3, 14.2, 18.1))

# 添加图表
x, y, cx, cy = Inches(1), Inches(2), Inches(8), Inches(4)
chart = slide.shapes.add_chart(
    XL_CHART_TYPE.COLUMN_CLUSTERED,
    x, y, cx, cy, chart_data
).chart

# 自定义
chart.has_legend = True
chart.legend.include_in_layout = False
```

### 格式化

#### 文本格式化

```python
from pptx.dml.color import RGBColor

run = p.runs[0]
run.font.name = 'Arial'
run.font.size = Pt(24)
run.font.bold = True
run.font.italic = True
run.font.color.rgb = RGBColor(0x00, 0x66, 0xCC)
```

#### 形状填充和线条

```python
from pptx.dml.color import RGBColor

shape.fill.solid()
shape.fill.fore_color.rgb = RGBColor(0x00, 0x80, 0x00)

shape.line.color.rgb = RGBColor(0x00, 0x00, 0x00)
shape.line.width = Pt(2)
```

#### 段落对齐

```python
from pptx.enum.text import PP_ALIGN

p.alignment = PP_ALIGN.CENTER  # LEFT, RIGHT, JUSTIFY
```

## 最佳实践

1. **使用模板**：从.pptx模板开始以保持一致的品牌
2. **先布局**：在编码前规划幻灯片结构
3. **重用幻灯片主母版**：保持演示文稿之间的一致性
4. **优化图像**：在添加前压缩图像
5. **测试输出**：始终验证生成的演示文稿

## 常见模式

### 幻灯片演示文稿生成器

```python
def create_deck(title, slides_content):
    prs = Presentation()
    
    # 标题幻灯片
    slide = prs.slides.add_slide(prs.slide_layouts[0])
    slide.shapes.title.text = title
    
    # 内容幻灯片
    for slide_data in slides_content:
        slide = prs.slides.add_slide(prs.slide_layouts[1])
        slide.shapes.title.text = slide_data['title']
        
        body = slide.placeholders[1]
        tf = body.text_frame
        for i, point in enumerate(slide_data['points']):
            if i == 0:
                tf.text = point
            else:
                p = tf.add_paragraph()
                p.text = point
    
    return prs
```

### 数据驱动图表

```python
def add_bar_chart(slide, title, categories, values):
    from pptx.chart.data import CategoryChartData
    from pptx.enum.chart import XL_CHART_TYPE
    
    chart_data = CategoryChartData()
    chart_data.categories = categories
    chart_data.add_series('值', values)
    
    chart = slide.shapes.add_chart(
        XL_CHART_TYPE.BAR_CLUSTERED,
        Inches(1), Inches(2),
        Inches(8), Inches(4),
        chart_data
    ).chart
    
    chart.chart_title.text_frame.text = title
    return chart
```

## 示例

### 示例1：创建演示文稿

```python
from pptx import Presentation
from pptx.util import Inches, Pt

prs = Presentation()

# 幻灯片1：标题
slide = prs.slides.add_slide(prs.slide_layouts[0])
slide.shapes.title.text = "StartupX"
slide.placeholders[1].text = "革新文档处理"

# 幻灯片2：问题
slide = prs.slides.add_slide(prs.slide_layouts[1])
slide.shapes.title.text = "问题"
body = slide.placeholders[1].text_frame
body.text = "手动文档处理每年使企业损失100亿美元"
p = body.add_paragraph()
p.text = "普通员工有20%的时间用于文档任务"
p.level = 1

# 幻灯片3：解决方案
slide = prs.slides.add_slide(prs.slide_layouts[1])
slide.shapes.title.text = "我们的解决方案"
body = slide.placeholders[1].text_frame
body.text = "AI驱动的文档自动化"
body.add_paragraph().text = "处理速度提升90%"
body.add_paragraph().text = "准确率99.5%"
body.add_paragraph().text = "兼容现有工具"

# 幻灯片4：市场
slide = prs.slides.add_slide(prs.slide_layouts[5])  # 仅标题
slide.shapes.title.text = "市场机会：2028年达500亿美元"

# 添加图表
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE

data = CategoryChartData()
data.categories = ['2024', '2025', '2026', '2027', '2028']
data.add_series('市场规模 ($B)', [30, 35, 40, 45, 50])

slide.shapes.add_chart(
    XL_CHART_TYPE.LINE,
    Inches(1), Inches(1.5),
    Inches(8), Inches(5),
    data
)

prs.save('pitch_deck.pptx')
```

### 示例2：带数据表格的报告

```python
from pptx import Presentation
from pptx.util import Inches, Pt

prs = Presentation()

# 标题幻灯片
slide = prs.slides.add_slide(prs.slide_layouts[0])
slide.shapes.title.text = "销售绩效报告"
slide.placeholders[1].text = "2024年第四季度"

# 数据幻灯片
slide = prs.slides.add_slide(prs.slide_layouts[5])
slide.shapes.title.text = "区域绩效"

# 创建表格
table = slide.shapes.add_table(5, 4, Inches(0.5), Inches(1.5), Inches(9), Inches(4)).table

# 标题
headers = ['区域', '收入', '增长率', '目标']
for i, h in enumerate(headers):
    table.cell(0, i).text = h
    table.cell(0, i).text_frame.paragraphs[0].font.bold = True

# 数据
data = [
    ['北美', '$5.2M', '+15%', '达标'],
    ['欧洲', '$3.8M', '+12%', '达标'],
    ['亚太', '$2.9M', '+28%', '超额完成'],
    ['拉丁美洲', '$1.1M', '+8%', '未达标'],
]
for row_idx, row_data in enumerate(data, 1):
    for col_idx, value in enumerate(row_data):
        table.cell(row_idx, col_idx).text = value

prs.save('sales_report.pptx')
```

## 限制

- 无法渲染复杂动画
- 智能图形支持有限
- 无法通过API嵌入视频
- 主母版编辑复杂
- 图表类型仅限于标准Office图表

## 安装

```bash
pip install python-pptx
```

## 资源

- [python-pptx文档](https://python-pptx.readthedocs.io/)
- [GitHub存储库](https://github.com/scanny/python-pptx)
- [幻灯片布局指南](https://python-pptx.readthedocs.io/en/latest/user/slides.html)
