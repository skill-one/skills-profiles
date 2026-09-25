# 文档处理技能

## 概述

该技能能够使用 **python-docx** 库以编程方式创建、编辑和操作 Microsoft Word (.docx) 文档。无需手动编辑即可创建具有正确格式、样式、表格和图像的专业文档。

## 使用方法

1. 描述您希望在 Word 文档中创建或修改的内容
2. 提供任何源内容（文本、数据、图像）
3. 我将生成 python-docx 代码并执行它

**示例提示：**
- "创建一个具有标题、标题和表格的专业报告"
- "为该文档添加页眉和页脚"
- "生成一个带有占位符的合同文档"
- "将此 Markdown 内容转换为带样式的 Word 文档"

## 领域知识

### python-docx 基础知识

```python
from docx import Document
from docx.shared import Inches, Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE

# 创建新文档
doc = Document()

# 或打开现有文档
doc = Document('existing.docx')
```

### 文档结构
```
Document
├── sections (页边距、方向、大小)
├── paragraphs (带格式的文本)
├── tables (行、单元格、合并单元格)
├── pictures (内联图像)
└── styles (预定义格式)
```

### 添加内容

#### 段落和标题

```python
# 添加标题（级别 0-9）
doc.add_heading('主标题', level=0)
doc.add_heading('章节标题', level=1)

# 添加段落
para = doc.add_paragraph('普通文本')

# 添加带样式的段落
doc.add_paragraph('注意：重要!', style='Intense Quote')

# 带内联格式添加
para = doc.add_paragraph()
para.add_run('粗体文本').bold = True
para.add_run(' 和 ')
para.add_run('斜体文本').italic = True
```

#### 表格

```python
# 创建表格
table = doc.add_table(rows=3, cols=3)
table.style = 'Table Grid'

# 添加内容
table.cell(0, 0).text = '标题 1'
table.rows[0].cells[1].text = '标题 2'

# 动态添加行
row = table.add_row()
row.cells[0].text = '新数据'

# 合并单元格
a = table.cell(0, 0)
b = table.cell(0, 2)
a.merge(b)
```

#### 图像

```python
# 添加带尺寸的图像
doc.add_picture('image.png', width=Inches(4))

# 添加到特定段落
para = doc.add_paragraph()
run = para.add_run()
run.add_picture('logo.png', width=Inches(1.5))
```

### 格式化

#### 段落格式化

```python
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, Inches

para = doc.add_paragraph('格式化文本')
para.alignment = WD_ALIGN_PARAGRAPH.CENTER
para.paragraph_format.line_spacing = 1.5
para.paragraph_format.space_after = Pt(12)
para.paragraph_format.first_line_indent = Inches(0.5)
```

#### 字符格式化

```python
run = para.add_run('带样式的文本')
run.bold = True
run.italic = True
run.underline = True
run.font.name = 'Arial'
run.font.size = Pt(14)
run.font.color.rgb = RGBColor(0x00, 0x00, 0xFF)  # 蓝色
```

#### 页面设置

```python
from docx.enum.section import WD_ORIENT
from docx.shared import Inches

section = doc.sections[0]
section.page_width = Inches(11)
section.page_height = Inches(8.5)
section.orientation = WD_ORIENT.LANDSCAPE
section.left_margin = Inches(1)
section.right_margin = Inches(1)
```

### 页眉和页脚

```python
section = doc.sections[0]

# 页眉
header = section.header
header.paragraphs[0].text = "公司名称"
header.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

# 带页码的页脚
footer = section.footer
para = footer.paragraphs[0]
para.text = "第 "
# 添加页码字段
run = para.add_run()
fldChar1 = OxmlElement('w:fldChar')
fldChar1.set(qn('w:fldCharType'), 'begin')
run._r.append(fldChar1)
# ... (页码字段代码)
```

### 样式

```python
# 使用内置样式
doc.add_paragraph('标题', style='Heading 1')
doc.add_paragraph('引用', style='Quote')
doc.add_paragraph('列表项', style='List Bullet')

# 常用样式：
# - 'Normal', 'Heading 1-9', 'Title', 'Subtitle'
# - 'Quote', 'Intense Quote', 'List Bullet', 'List Number'
# - 'Table Grid', 'Light Shading', 'Medium Grid 1'
```

## 最佳实践

1. **先结构化**：在编码前规划文档层次结构
2. **使用样式**：通过样式而非手动格式化实现一致格式
3. **频繁保存**：对大型文档定期调用 `doc.save()`
4. **处理错误**：在打开文件前检查文件是否存在
5. **清理**：填充模板占位符后删除

## 常见模式

### 报告模板

```python
def create_report(title, sections):
    doc = Document()
    doc.add_heading(title, 0)
    doc.add_paragraph(f'生成时间: {datetime.now()}')
    
    for section_title, content in sections.items():
        doc.add_heading(section_title, 1)
        doc.add_paragraph(content)
    
    return doc
```

### 从数据创建表格

```python
def add_data_table(doc, headers, rows):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = 'Table Grid'
    
    # 标题
    for i, header in enumerate(headers):
        table.rows[0].cells[i].text = header
        table.rows[0].cells[i].paragraphs[0].runs[0].bold = True
    
    # 数据行
    for row_data in rows:
        row = table.add_row()
        for i, value in enumerate(row_data):
            row.cells[i].text = str(value)
    
    return table
```

### 邮件合并模式

```python
def fill_template(template_path, replacements):
    doc = Document(template_path)
    
    for para in doc.paragraphs:
        for key, value in replacements.items():
            if f'{{{key}}}' in para.text:
                para.text = para.text.replace(f'{{{key}}}', value)
    
    return doc
```

## 示例

### 示例 1：创建商业信函

```python
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import datetime

doc = Document()

# 信头
doc.add_paragraph('ACME 公司')
doc.add_paragraph('123 商业大道，100 套房')
doc.add_paragraph('纽约，纽约 10001')
doc.add_paragraph()

# 日期
doc.add_paragraph(datetime.now().strftime('%B %d, %Y'))
doc.add_paragraph()

# 收件人
doc.add_paragraph('约翰·史密斯先生')
doc.add_paragraph('XYZ 公司')
doc.add_paragraph('456 行业大道')
doc.add_paragraph('芝加哥，伊利诺伊 60601')
doc.add_paragraph()

# 称呼
doc.add_paragraph('尊敬的史密斯先生，')
doc.add_paragraph()

# 正文
body = """我们很高兴通知您，您的提案已被接受...

[信函正文继续...]

感谢您一直以来的合作。"""

for para_text in body.split('\n\n'):
    doc.add_paragraph(para_text)

doc.add_paragraph()
doc.add_paragraph('此致，')
doc.add_paragraph()
doc.add_paragraph()
doc.add_paragraph()
doc.add_paragraph('简·多伊')
doc.add_paragraph('ACME 公司首席执行官')

doc.save('商业信函.docx')
```

### 示例 2：创建带表格的报告

```python
from docx import Document
from docx.shared import Inches

doc = Document()
doc.add_heading('2024 年第四季度销售报告', 0)

# 执行摘要
doc.add_heading('执行摘要', 1)
doc.add_paragraph('2024 年第四季度在所有地区都显示出强劲的增长...')

# 销售表格
doc.add_heading('区域表现', 1)

table = doc.add_table(rows=1, cols=4)
table.style = 'Medium Grid 1 Accent 1'

headers = ['区域', '2023 年销售额', '2024 年销售额', '增长率']
for i, header in enumerate(headers):
    table.rows[0].cells[i].text = header

data = [
    ['北美', '$1.2M', '$1.5M', '+25%'],
    ['欧洲', '$800K', '$950K', '+18%'],
    ['亚太地区', '$600K', '$750K', '+25%'],
]

for row_data in data:
    row = table.add_row()
    for i, value in enumerate(row_data):
        row.cells[i].text = value

doc.save('销售报告.docx')
```

## 限制

- 无法执行宏或 VBA 代码
- 复杂模板可能丢失部分格式
- 对高级功能（SmartArt、图表）支持有限
- 无直接 PDF 转换（使用单独工具）
- 跟踪更改阅读功能有限

## 安装

```bash
pip install python-docx
```

## 资源

- [python-docx 文档](https://python-docx.readthedocs.io/)
- [GitHub 仓库](https://github.com/python-openxml/python-docx)
- [Office Open XML 规范](https://docs.microsoft.com/en-us/office/open-xml/open-xml-sdk)
