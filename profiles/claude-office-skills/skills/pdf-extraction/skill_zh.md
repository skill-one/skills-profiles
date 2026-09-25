# PDF提取技能

## 概述

该技能能够使用**pdfplumber**从PDF文档中精确提取文本、表格和元数据——这是PDF数据提取的首选库。与基本的PDF阅读器不同，pdfplumber提供字符级别的定位、精确的表格检测和可视化调试功能。

## 使用方法

1. 提供您想要从中提取的PDF文件
2. 指定您的需求：文本、表格、图像或元数据
3. 我将生成pdfplumber代码并执行它

**示例提示：**
- "从这份财务报告中提取所有表格"
- "获取这份文档第5-10页的文本"
- "从这份PDF中查找并提取发票总额"
- "将这份PDF表格转换为CSV/Excel"

## 领域知识

### pdfplumber基础

```python
import pdfplumber

# 打开PDF
with pdfplumber.open('document.pdf') as pdf:
    # 访问页面
    first_page = pdf.pages[0]
    
    # 文档元数据
    print(pdf.metadata)
    
    # 页面数量
    print(len(pdf.pages))
```

### PDF结构
```
PDF文档
├── metadata (标题、作者、创建日期)
├── pages[]
│   ├── chars (单个字符及其位置)
│   ├── words (字符分组)
│   ├── lines (水平/垂直线)
│   ├── rects (矩形)
│   ├── curves (贝塞尔曲线)
│   └── images (嵌入图像)
└── outline (书签/目录)
```

### 文本提取

#### 基本文本
```python
with pdfplumber.open('document.pdf') as pdf:
    # 单页
    text = pdf.pages[0].extract_text()
    
    # 所有页面
    full_text = ''
    for page in pdf.pages:
        full_text += page.extract_text() or ''
```

#### 高级文本选项
```python
# 带布局保留
text = page.extract_text(
    x_tolerance=3,      # 水平容差用于分组
    y_tolerance=3,      # 垂直容差
    layout=True,        # 保留布局
    x_density=7.25,     # 单位宽度字符数
    y_density=13        # 单位高度字符数
)

# 提取带位置的单词
words = page.extract_words(
    x_tolerance=3,
    y_tolerance=3,
    keep_blank_chars=False,
    use_text_flow=False
)

# 每个单词包括：文本、x0、top、x1、bottom等
for word in words:
    print(f"{word['text']} at ({word['x0']}, {word['top']})")
```

#### 字符级访问
```python
# 获取所有字符
chars = page.chars

for char in chars:
    print(f"'{char['text']}' at ({char['x0']}, {char['top']})")
    print(f"  字体: {char['fontname']}, 大小: {char['size']}")
```

### 表格提取

#### 基本表格提取
```python
with pdfplumber.open('report.pdf') as pdf:
    page = pdf.pages[0]
    
    # 提取所有表格
    tables = page.extract_tables()
    
    for i, table in enumerate(tables):
        print(f"表格 {i+1}:")
        for row in table:
            print(row)
```

#### 高级表格设置
```python
# 自定义表格检测
table_settings = {
    "vertical_strategy": "lines",      # 或 "text", "explicit"
    "horizontal_strategy": "lines",
    "explicit_vertical_lines": [],     # 自定义线位置
    "explicit_horizontal_lines": [],
    "snap_tolerance": 3,
    "snap_x_tolerance": 3,
    "snap_y_tolerance": 3,
    "join_tolerance": 3,
    "edge_min_length": 3,
    "min_words_vertical": 3,
    "min_words_horizontal": 1,
    "intersection_tolerance": 3,
    "text_tolerance": 3,
    "text_x_tolerance": 3,
    "text_y_tolerance": 3,
}

tables = page.extract_tables(table_settings)
```

#### 表格查找
```python
# 查找表格（不提取）
table_finder = page.find_tables()

for table in table_finder:
    print(f"表格位置: {table.bbox}")  # (x0, top, x1, bottom)
    
    # 提取特定表格
    data = table.extract()
```

### 可视化调试

```python
# 创建可视化调试图像
im = page.to_image(resolution=150)

# 绘制检测到的对象
im.draw_rects(page.chars)        # 字符边界框
im.draw_rects(page.words)        # 单词边界框
im.draw_lines(page.lines)        # 线条
im.draw_rects(page.rects)        # 矩形

# 保存调试图像
im.save('debug.png')

# 调试表格
im.reset()
im.debug_tablefinder()
im.save('table_debug.png')
```

### 裁剪和过滤

#### 裁剪到区域
```python
# 定义边界框 (x0, top, x1, bottom)
bbox = (0, 0, 300, 200)

# 裁剪页面
cropped = page.crop(bbox)

# 从裁剪区域提取
text = cropped.extract_text()
tables = cropped.extract_tables()
```

#### 按位置过滤
```python
# 按区域过滤字符
def within_bbox(obj, bbox):
    x0, top, x1, bottom = bbox
    return (obj['x0'] >= x0 and obj['x1'] <= x1 and
            obj['top'] >= top and obj['bottom'] <= bottom)

bbox = (100, 100, 400, 300)
filtered_chars = [c for c in page.chars if within_bbox(c, bbox)]
```

#### 按字体过滤
```python
# 按字体获取文本
def extract_by_font(page, font_name):
    chars = [c for c in page.chars if font_name in c['fontname']]
    return ''.join(c['text'] for c in chars)

# 提取粗体文本（通常字体名中包含"Bold"）
bold_text = extract_by_font(page, 'Bold')

# 按大小提取
large_chars = [c for c in page.chars if c['size'] > 14]
```

### 元数据和结构

```python
with pdfplumber.open('document.pdf') as pdf:
    # 文档元数据
    meta = pdf.metadata
    print(f"标题: {meta.get('Title')}")
    print(f"作者: {meta.get('Author')}")
    print(f"创建: {meta.get('CreationDate')}")
    
    # 页面信息
    for i, page in enumerate(pdf.pages):
        print(f"页面 {i+1}: {page.width} x {page.height}")
        print(f"  旋转: {page.rotation}")
```

## 最佳实践

1. **可视化调试**：使用`to_image()`理解PDF结构
2. **调整表格设置**：根据您的PDF调整容差值
3. **处理扫描PDF**：先使用OCR（这项技能用于原生文本）
4. **逐页处理**：对于大PDF，避免一次性加载所有页面
5. **检查文本**：某些PDF是图像——验证是否存在文本

## 常见模式

### 将所有表格提取到DataFrame
```python
import pandas as pd

def pdf_tables_to_dataframes(pdf_path):
    """从PDF提取所有表格为pandas DataFrame。"""
    dfs = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            
            for j, table in enumerate(tables):
                if table and len(table) > 1:
                    # 第一行作为标题
                    df = pd.DataFrame(table[1:], columns=table[0])
                    df['_page'] = i + 1
                    df['_table'] = j + 1
                    dfs.append(df)
    
    return dfs
```

### 提取特定区域
```python
def extract_invoice_amount(pdf_path):
    """从典型发票布局中提取金额。"""
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        
        # 搜索"Total"并获取附近数字
        words = page.extract_words()
        
        for i, word in enumerate(words):
            if 'total' in word['text'].lower():
                # 查看接下来的几个词
                for next_word in words[i+1:i+5]:
                    text = next_word['text'].replace(',', '').replace('$', '')
                    try:
                        return float(text)
                    except ValueError:
                        continue
    
    return None
```

### 多列布局
```python
def extract_columns(page, num_columns=2):
    """从多列布局中提取文本。"""
    width = page.width
    col_width = width / num_columns
    
    columns = []
    for i in range(num_columns):
        x0 = i * col_width
        x1 = (i + 1) * col_width
        
        cropped = page.crop((x0, 0, x1, page.height))
        columns.append(cropped.extract_text())
    
    return columns
```

## 示例

### 示例1：财务报告表格提取
```python
import pdfplumber
import pandas as pd

def extract_financial_tables(pdf_path):
    """从财务报告中提取表格并保存到Excel。"""
    
    with pdfplumber.open(pdf_path) as pdf:
        all_tables = []
        
        for page_num, page in enumerate(pdf.pages):
            # 调试：保存表格可视化
            im = page.to_image()
            im.debug_tablefinder()
            im.save(f'debug_page_{page_num+1}.png')
            
            # 提取表格
            tables = page.extract_tables({
                "vertical_strategy": "lines",
                "horizontal_strategy": "lines",
                "snap_tolerance": 5,
            })
            
            for table in tables:
                if table and len(table) > 1:
                    # 清理数据
                    clean_table = []
                    for row in table:
                        clean_row = [cell.strip() if cell else '' for cell in row]
                        clean_table.append(clean_row)
                    
                    df = pd.DataFrame(clean_table[1:], columns=clean_table[0])
                    df['Source Page'] = page_num + 1
                    all_tables.append(df)
        
        # 保存到Excel，使用多个工作表
        with pd.ExcelWriter('extracted_tables.xlsx') as writer:
            for i, df in enumerate(all_tables):
                df.to_excel(writer, sheet_name=f'Table_{i+1}', index=False)
        
        return all_tables

tables = extract_financial_tables('annual_report.pdf')
print(f"提取了 {len(tables)} 个表格")
```

### 示例2：发票数据提取
```python
import pdfplumber
import re
from datetime import datetime

def extract_invoice_data(pdf_path):
    """从发票PDF中提取结构化数据。"""
    
    data = {
        'invoice_number': None,
        'date': None,
        'total': None,
        'line_items': []
    }
    
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        text = page.extract_text()
        
        # 提取发票号
        inv_match = re.search(r'Invoice\s*#?\s*:?\s*(\w+)', text, re.IGNORECASE)
        if inv_match:
            data['invoice_number'] = inv_match.group(1)
        
        # 提取日期
        date_match = re.search(r'Date\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', text)
        if date_match:
            data['date'] = date_match.group(1)
        
        # 提取总额
        total_match = re.search(r'Total\s*:?\s*\$?([\d,]+\.?\d*)', text, re.IGNORECASE)
        if total_match:
            data['total'] = float(total_match.group(1).replace(',', ''))
        
        # 从表格中提取行项目
        tables = page.extract_tables()
        for table in tables:
            if table and any('description' in str(row).lower() for row in table[:2]):
                # 找到行项目表格
                for row in table[1:]:  # 跳过标题
                    if row and len(row) >= 3:
                        data['line_items'].append({
                            'description': row[0],
                            'quantity': row[1] if len(row) > 1 else None,
                            'amount': row[-1]
                        })
    
    return data

invoice = extract_invoice_data('invoice.pdf')
print(f"发票 #{invoice['invoice_number']}")
print(f"总额: ${invoice['total']}")
```

### 示例3：简历/履历解析器
```python
import pdfplumber

def parse_resume(pdf_path):
    """从简历中提取结构化部分。"""
    
    with pdfplumber.open(pdf_path) as pdf:
        full_text = ''
        for page in pdf.pages:
            full_text += (page.extract_text() or '') + '\n'
        
        # 常见简历部分
        sections = {
            'contact': '',
            'summary': '',
            'experience': '',
            'education': '',
            'skills': ''
        }
        
        # 按常见标题分割
        import re
        section_patterns = {
            'summary': r'(summary|objective|profile)',
            'experience': r'(experience|employment|work history)',
            'education': r'(education|academic)',
            'skills': r'(skills|competencies|technical)'
        }
        
        lines = full_text.split('\n')
        current_section = 'contact'
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # 检查是否为部分标题行
            for section, pattern in section_patterns.items():
                if re.match(pattern, line_lower):
                    current_section = section
                    break
            
            sections[current_section] += line + '\n'
        
        return sections

resume = parse_resume('resume.pdf')
print("技能:", resume['skills'])
```

## 限制

- 无法从扫描/图像PDF中提取（需先使用OCR）
- 复杂布局可能需要手动调整
- 某些PDF加密类型不支持
- 嵌入字体可能影响文本提取
- 没有直接PDF编辑功能

## 安装

```bash
pip install pdfplumber

# 用于图像调试（可选）
pip install Pillow
```

## 资源

- [pdfplumber文档](https://github.com/jsvine/pdfplumber)
- [表格提取指南](https://github.com/jsvine/pdfplumber#extracting-tables)
- [可视化调试](https://github.com/jsvine/pdfplumber#visual-debugging)
