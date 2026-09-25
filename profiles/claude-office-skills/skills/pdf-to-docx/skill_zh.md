# PDF转Word技能

## 概述

该技能能够使用**pdf2docx**（一个Python库）将PDF转换为可编辑的Word文档，该库能够保留布局、表格、图像和文本格式。与基于OCR的解决方案不同，pdf2docx提取原生PDF内容以实现精确转换。

## 使用方法

1. 提供您想要转换的PDF文件
2. 可选地指定页面或转换选项
3. 我将把它转换为可编辑的Word文档

**示例提示：**
- "将此PDF报告转换为可编辑的Word文档"
- "将此PDF的前5页转换为Word格式"
- "提取此扫描文档为可编辑文本"
- "将此PDF合同转换为Word以进行编辑"

## 领域知识

### pdf2docx基础

```python
from pdf2docx import Converter

# 基本转换
cv = Converter('input.pdf')
cv.convert('output.docx')
cv.close()

# 或使用上下文管理器
with Converter('input.pdf') as cv:
    cv.convert('output.docx')
```

### 转换选项

```python
from pdf2docx import Converter

cv = Converter('input.pdf')

# 整个文档
cv.convert('output.docx')

# 特定页面（0索引）
cv.convert('output.docx', start=0, end=5)

# 单页
cv.convert('output.docx', pages=[0])

# 多个特定页面
cv.convert('output.docx', pages=[0, 2, 4])

cv.close()
```

### 高级选项

```python
from pdf2docx import Converter

cv = Converter('input.pdf')

cv.convert(
    'output.docx',
    start=0,                    # 开始页（0索引）
    end=None,                   # 结束页（None = 最后一页）
    pages=None,                 # 特定页面列表
    password=None,              # 如果加密，则提供PDF密码
    min_section_height=20.0,    # 最小节高
    connected_border_tolerance=0.5,  # 边框检测容差
    line_overlap_threshold=0.9, # 线合并阈值
    line_break_width_ratio=0.5, # 行断开检测
    line_break_free_space_ratio=0.1,
    line_separate_threshold=5,  # 垂直线分离
    new_paragraph_free_space_ratio=0.85,
    float_image_ignorable_gap=5,
    page_margin_factor_top=0.5,
    page_margin_factor_bottom=0.5,
)

cv.close()
```

### 处理不同类型的PDF

#### 原生PDF（基于文本）
```python
# 原生PDF效果最佳
cv = Converter('native_pdf.pdf')
cv.convert('output.docx')
cv.close()
```

#### 扫描PDF（基于图像）
```python
# 对于扫描PDF，应先进行OCR处理
# pdf2docx最适合基于文本的原生PDF
# 考虑先使用pytesseract或PaddleOCR

import pytesseract
from pdf2image import convert_from_path

# 将PDF页面转换为图像
images = convert_from_path('scanned.pdf')

# 对每页进行OCR
text = ''
for img in images:
    text += pytesseract.image_to_string(img)

# 然后从文本创建Word文档
```

### Python集成

```python
from pdf2docx import Converter
import os

def pdf_to_word(pdf_path, output_path=None, pages=None):
    """将PDF转换为Word文档。"""
    if output_path is None:
        output_path = pdf_path.replace('.pdf', '.docx')
    
    cv = Converter(pdf_path)
    
    if pages:
        cv.convert(output_path, pages=pages)
    else:
        cv.convert(output_path)
    
    cv.close()
    
    return output_path

# 使用示例
result = pdf_to_word('document.pdf')
print(f"创建: {result}")
```

### 批量转换

```python
from pdf2docx import Converter
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

def convert_single(pdf_path, output_dir):
    """将单个PDF转换为Word。"""
    output_path = output_dir / pdf_path.with_suffix('.docx').name
    
    try:
        cv = Converter(str(pdf_path))
        cv.convert(str(output_path))
        cv.close()
        return f"成功: {pdf_path.name}"
    except Exception as e:
        return f"错误: {pdf_path.name} - {e}"

def batch_convert(input_dir, output_dir, max_workers=4):
    """转换目录中的所有PDF。"""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    pdf_files = list(input_path.glob('*.pdf'))
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(convert_single, pdf, output_path)
            for pdf in pdf_files
        ]
        
        for future in futures:
            print(future.result())

batch_convert('./pdfs', './word_docs')
```

### 解析PDF结构

```python
from pdf2docx import Converter

def analyze_pdf(pdf_path):
    """转换前分析PDF结构。"""
    cv = Converter(pdf_path)
    
    for i, page in enumerate(cv.pages):
        print(f"第{i+1}页:")
        print(f"  大小: {page.width} x {page.height}")
        print(f"  块数: {len(page.blocks)}")
        
        for block in page.blocks:
            if hasattr(block, 'text'):
                print(f"    文本块: {block.text[:50]}...")
            elif hasattr(block, 'image'):
                print(f"    图像块")
    
    cv.close()

analyze_pdf('document.pdf')
```

## 最佳实践

1. **检查PDF类型**：原生PDF比扫描PDF转换效果更好
2. **预览优先**：在完全转换前先测试几页
3. **处理表格**：复杂表格可能需要手动调整
4. **图像质量**：图像以原始分辨率提取
5. **字体处理**：某些字体可能替换为系统默认字体

## 常见模式

### 带进度转换
```python
from pdf2docx import Converter

def convert_with_progress(pdf_path, output_path):
    """带进度跟踪的转换。"""
    cv = Converter(pdf_path)
    
    总页数 = len(cv.pages)
    print(f"正在转换{总页数}页...")
    
    for i in range(总页数):
        cv.convert(output_path, start=i, end=i+1)
        进度 = (i + 1) / 总页数 * 100
        print(f"进度: {进度:.1f}%")
    
    cv.close()
    print("转换完成！")
```

### 仅提取表格
```python
from pdf2docx import Converter
from docx import Document

def extract_tables_to_word(pdf_path, output_path):
    """仅从PDF提取表格到Word。"""
    cv = Converter(pdf_path)
    
    # 先进行完整转换
    temp_path = 'temp_full.docx'
    cv.convert(temp_path)
    cv.close()
    
    # 打开并提取表格
    doc = Document(temp_path)
    new_doc = Document()
    
    for table in doc.tables:
        # 复制表格到新文档
        new_table = new_doc.add_table(rows=0, cols=len(table.columns))
        
        for row in table.rows:
            new_row = new_table.add_row()
            for i, cell in enumerate(row.cells):
                new_row.cells[i].text = cell.text
        
        new_doc.add_paragraph()  # 添加间距
    
    new_doc.save(output_path)
    os.remove(temp_path)
```

## 示例

### 示例1：合同转换
```python
from pdf2docx import Converter
import os

def convert_contract(pdf_path):
    """将合同PDF转换为可编辑的Word文档，并保留元数据。"""
    
    # 定义输出路径
    base_name = os.path.splitext(pdf_path)[0]
    output_path = f"{base_name}_editable.docx"
    
    # 转换
    cv = Converter(pdf_path)
    
    # 检查页数
    页数 = len(cv.pages)
    print(f"处理{页数}页...")
    
    # 转换所有页
    cv.convert(output_path)
    cv.close()
    
    print(f"创建: {output_path}")
    print(f"文件大小: {os.path.getsize(output_path) / 1024:.1f} KB")
    
    return output_path

# 使用示例
result = convert_contract('contract.pdf')
```

### 示例2：选择性页面转换
```python
from pdf2docx import Converter

def convert_selected_pages(pdf_path, page_ranges, output_path):
    """将特定页面范围转换为Word。
    
    page_ranges: 列表，如[(1, 3), (5, 7)]，表示第1-3页和第5-7页
    """
    cv = Converter(pdf_path)
    
    # 转换页面（内部为0索引）
    所有页 = []
    for start, end in page_ranges:
        所有页.extend(range(start - 1, end))  # 转换为0索引
    
    cv.convert(output_path, pages=所有页)
    cv.close()
    
    print(f"转换页面: {page_ranges}")
    return output_path

# 转换第1-5页和第10-15页
convert_selected_pages(
    'long_document.pdf',
    [(1, 5), (10, 15)],
    'selected_pages.docx'
)
```

### 示例3：PDF报告到可编辑模板
```python
from pdf2docx import Converter
from docx import Document

def pdf_to_template(pdf_path, output_path):
    """将PDF报告转换为Word模板，并添加占位符。"""
    
    # 将PDF转换为Word
    cv = Converter(pdf_path)
    cv.convert(output_path)
    cv.close()
    
    # 打开并添加占位符字段
    doc = Document(output_path)
    
    # 用占位符替换常见字段
    替换 = {
        '公司名称': '[COMPANY_NAME]',
        '日期:': '日期: [DATE]',
        '编制人:': '编制人: [AUTHOR]',
    }
    
    for 段落 in doc.paragraphs:
        for 旧, 新 in 替换.items():
            if 旧 in 段落.text:
                段落.text = 段落.text.replace(旧, 新)
    
    # 也检查表格
    for 表格 in doc.tables:
        for 行 in 表格.rows:
            for 单元格 in 行.cells:
                for 旧, 新 in 替换.items():
                    if 旧 in 单元格.text:
                        单元格.text = 单元格.text.replace(旧, 新)
    
    doc.save(output_path)
    print(f"模板创建: {output_path}")

pdf_to_template('annual_report.pdf', 'report_template.docx')
```

### 示例4：批量发票处理
```python
from pdf2docx import Converter
from pathlib import Path
import json

def process_invoices(input_folder, output_folder):
    """将PDF发票转换为可编辑的Word文档。"""
    
    input_path = Path(input_folder)
    output_path = Path(output_folder)
    output_path.mkdir(exist_ok=True)
    
    结果 = []
    
    for pdf_file in input_path.glob('*.pdf'):
        output_file = output_path / pdf_file.with_suffix('.docx').name
        
        try:
            cv = Converter(str(pdf_file))
            cv.convert(str(output_file))
            cv.close()
            
            结果.append({
                '文件': pdf_file.name,
                '状态': '成功',
                '输出': str(output_file)
            })
            
        except Exception as e:
            结果.append({
                '文件': pdf_file.name,
                '状态': '错误',
                '错误': str(e)
            })
    
    # 保存结果日志
    with open(output_path / 'conversion_log.json', 'w') as f:
        json.dump(结果, f, indent=2)
    
    # 摘要
    成功 = sum(1 for r in 结果 if r['状态'] == '成功')
    print(f"转换了{成功}/{len(结果)}个文件")
    
    return 结果

结果 = process_invoices('./invoices_pdf', './invoices_word')
```

## 限制

- 扫描PDF需要OCR预处理
- 复杂布局可能无法完美转换
- 某些字体可能不可用
- 水印会包含在转换结果中
- 受保护/加密的PDF需要密码

## 安装

```bash
pip install pdf2docx

# 用于图像处理
pip install Pillow
```

## 资源

- [GitHub仓库](https://github.com/dothinking/pdf2docx)
- [文档](https://pdf2docx.readthedocs.io/)
- [PyPI包](https://pypi.org/project/pdf2docx/)
