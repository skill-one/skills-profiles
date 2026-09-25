# 文档解析技能

## 概述

该技能使用 IBM 的最先进的文档理解库 **docling** 实现高级文档解析。解析复杂的 PDF 文件、Word 文档和图像，同时保留结构、提取表格、图表，并处理多列布局。

## 使用方法

1. 提供要解析的文档
2. 指定要提取的内容（文本、表格、图表等）
3. 我将解析文档并返回结构化数据

**示例提示：**
- "解析此 PDF 并提取所有表格"
- "将此学术论文转换为结构化 Markdown"
- "从此文档中提取图表和标题"
- "解析此报告并保留文档结构"

## 领域知识

### docling 基础知识

```python
from docling.document_converter import DocumentConverter

# 初始化转换器
converter = DocumentConverter()

# 转换文档
result = converter.convert("document.pdf")

# 访问解析内容
doc = result.document
print(doc.export_to_markdown())
```

### 支持的格式

| 格式 | 扩展名 | 备注 |
|------|--------|------|
| PDF | .pdf | 原生和扫描 |
| Word | .docx | 保留完整结构 |
| PowerPoint | .pptx | 幻灯片作为章节 |
| 图像 | .png, .jpg | OCR + 布局分析 |
| HTML | .html | 保留结构 |

### 基本用法

```python
from docling.document_converter import DocumentConverter

# 创建转换器
converter = DocumentConverter()

# 转换单个文档
result = converter.convert("report.pdf")

# 访问文档
doc = result.document

# 导出选项
markdown = doc.export_to_markdown()
text = doc.export_to_text()
json_doc = doc.export_to_dict()
```

### 高级配置

```python
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions

# 配置管道
pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = True
pipeline_options.do_table_structure = True
pipeline_options.table_structure_options.do_cell_matching = True

# 使用选项创建转换器
converter = DocumentConverter(
    allowed_formats=[InputFormat.PDF, InputFormat.DOCX],
    pdf_backend_options=pipeline_options
)

result = converter.convert("document.pdf")
```

### 文档结构

```python
# 文档层次结构
doc = result.document

# 访问元数据
print(doc.name)
print(doc.origin)

# 遍历内容
for element in doc.iterate_items():
    print(f"类型: {element.type}")
    print(f"文本: {element.text}")
    
    if element.type == "table":
        print(f"行数: {len(element.data.table_cells)}")
```

### 提取表格

```python
from docling.document_converter import DocumentConverter
import pandas as pd

def extract_tables(doc_path):
    """从文档中提取所有表格."""
    converter = DocumentConverter()
    result = converter.convert(doc_path)
    doc = result.document
    
    tables = []
    
    for element in doc.iterate_items():
        if element.type == "table":
            # 获取表格数据
            table_data = element.export_to_dataframe()
            tables.append({
                '页码': element.prov[0].page_no if element.prov else None,
                '数据': table_data
            })
    
    return tables

# 使用示例
tables = extract_tables("report.pdf")
for i, table in enumerate(tables):
    print(f"表格 {i+1} 在第 {table['页码']} 页:")
    print(table['数据'])
```

### 提取图表

```python
def extract_figures(doc_path, output_dir):
    """提取带标题的图表."""
    import os
    
    converter = DocumentConverter()
    result = converter.convert(doc_path)
    doc = result.document
    
    figures = []
    os.makedirs(output_dir, exist_ok=True)
    
    for element in doc.iterate_items():
        if element.type == "picture":
            figure_info = {
                '标题': element.caption if hasattr(element, 'caption') else None,
                '页码': element.prov[0].page_no if element.prov else None,
            }
            
            # 如果有图像则保存
            if hasattr(element, 'image'):
                img_path = os.path.join(output_dir, f"figure_{len(figures)+1}.png")
                element.image.save(img_path)
                figure_info['路径'] = img_path
            
            figures.append(figure_info)
    
    return figures
```

### 处理多列布局

```python
from docling.document_converter import DocumentConverter

def parse_multicolumn(doc_path):
    """解析具有多列布局的文档."""
    
    converter = DocumentConverter()
    result = converter.convert(doc_path)
    doc = result.document
    
    # docling 自动处理列检测
    # 文本按阅读顺序返回
    
    structured_content = []
    
    for element in doc.iterate_items():
        content_item = {
            '类型': element.type,
            '文本': element.text if hasattr(element, 'text') else None,
            '级别': element.level if hasattr(element, 'level') else None,
        }
        
        # 如果有边界框则添加
        if element.prov:
            content_item['bbox'] = element.prov[0].bbox
            content_item['页码'] = element.prov[0].page_no
        
        structured_content.append(content_item)
    
    return structured_content
```

### 导出格式

```python
from docling.document_converter import DocumentConverter

converter = DocumentConverter()
result = converter.convert("document.pdf")
doc = result.document

# Markdown 导出
markdown = doc.export_to_markdown()
with open("output.md", "w") as f:
    f.write(markdown)

# 纯文本
text = doc.export_to_text()

# JSON/字典格式
json_doc = doc.export_to_dict()

# HTML 格式（如果支持）
# html = doc.export_to_html()
```

### 批量处理

```python
from docling.document_converter import DocumentConverter
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

def batch_parse(input_dir, output_dir, max_workers=4):
    """并行解析多个文档."""
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    converter = DocumentConverter()
    
    def process_single(doc_path):
        try:
            result = converter.convert(str(doc_path))
            md = result.document.export_to_markdown()
            
            out_file = output_path / f"{doc_path.stem}.md"
            with open(out_file, 'w') as f:
                f.write(md)
            
            return {'文件': str(doc_path), '状态': '成功'}
        except Exception as e:
            return {'文件': str(doc_path), '状态': '失败', '错误': str(e)}
    
    docs = list(input_path.glob('*.pdf')) + list(input_path.glob('*.docx'))
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(process_single, docs))
    
    return results
```

## 最佳实践

1. **使用适当的管道**：根据文档类型进行配置
2. **处理大型文档**：如有需要可分块处理
3. **验证表格提取**：复杂表格可能需要人工检查
4. **检查 OCR 质量**：对扫描文档启用 OCR
5. **缓存结果**：存储解析文档以供重复使用

## 常见模式

### 学术论文解析器

```python
def parse_academic_paper(pdf_path):
    """解析学术论文结构."""
    
    converter = DocumentConverter()
    result = converter.convert(pdf_path)
    doc = result.document
    
    paper = {
        '标题': None,
        '摘要': None,
        '章节': [],
        '参考文献': [],
        '表格': [],
        '图表': []
    }
    
    current_section = None
    
    for element in doc.iterate_items():
        text = element.text if hasattr(element, 'text') else ''
        
        if element.type == 'title':
            paper['标题'] = text
        
        elif element.type == 'heading':
            if 'abstract' in text.lower():
                current_section = 'abstract'
            elif 'reference' in text.lower():
                current_section = 'references'
            else:
                paper['章节'].append({
                    '标题': text,
                    '内容': ''
                })
                current_section = '章节'
        
        elif element.type == 'paragraph':
            if current_section == 'abstract':
                paper['摘要'] = text
            elif current_section == '章节' and paper['章节']:
                paper['章节'][-1]['内容'] += text + '\n'
        
        elif element.type == 'table':
            paper['表格'].append({
                '标题': element.caption if hasattr(element, 'caption') else None,
                '数据': element.export_to_dataframe() if hasattr(element, 'export_to_dataframe') else None
            })
    
    return paper
```

### 报告到结构化数据

```python
def parse_business_report(doc_path):
    """将商业报告解析为结构化格式."""
    
    converter = DocumentConverter()
    result = converter.convert(doc_path)
    doc = result.document
    
    report = {
        '元数据': {
            '标题': None,
            '日期': None,
            '作者': None
        },
        '执行摘要': None,
        '章节': [],
        '关键指标': [],
        '建议': []
    }
    
    # 解析文档结构
    for element in doc.iterate_items():
        # 根据文档结构实现解析逻辑
        pass
    
    return report
```

## 示例

### 示例 1：解析财务报告

```python
from docling.document_converter import DocumentConverter

def parse_financial_report(pdf_path):
    """从财务报告中提取结构化数据."""
    
    converter = DocumentConverter()
    result = converter.convert(pdf_path)
    doc = result.document
    
    financial_data = {
        '损益表': None,
        '资产负债表': None,
        '现金流量表': None,
        '注释': []
    }
    
    # 提取表格
    tables = []
    for element in doc.iterate_items():
        if element.type == 'table':
            table_df = element.export_to_dataframe()
            
            # 识别表格类型
            if 'revenue' in str(table_df).lower() or 'income' in str(table_df).lower():
                financial_data['损益表'] = table_df
            elif 'asset' in str(table_df).lower() or 'liabilities' in str(table_df).lower():
                financial_data['资产负债表'] = table_df
            elif 'cash' in str(table_df).lower():
                financial_data['现金流量表'] = table_df
            else:
                tables.append(table_df)
    
    # 提取 Markdown 格式的注释
    financial_data['markdown'] = doc.export_to_markdown()
    
    return financial_data

report = parse_financial_report('annual_report.pdf')
print("损益表:")
print(report['损益表'])
```

### 示例 2：技术文档解析器

```python
from docling.document_converter import DocumentConverter

def parse_technical_docs(doc_path):
    """解析技术文档."""
    
    converter = DocumentConverter()
    result = converter.convert(doc_path)
    doc = result.document
    
    documentation = {
        '标题': None,
        '版本': None,
        '章节': [],
        '代码块': [],
        '图表': []
    }
    
    current_section = None
    
    for element in doc.iterate_items():
        if element.type == 'title':
            documentation['标题'] = element.text
        
        elif element.type == 'heading':
            current_section = {
                '标题': element.text,
                '级别': element.level if hasattr(element, 'level') else 1,
                '内容': []
            }
            documentation['章节'].append(current_section)
        
        elif element.type == 'code':
            if current_section:
                current_section['内容'].append({
                    '类型': 'code',
                    '内容': element.text
                })
            documentation['代码块'].append(element.text)
        
        elif element.type == 'picture':
            documentation['图表'].append({
                '页码': element.prov[0].page_no if element.prov else None,
                '标题': element.caption if hasattr(element, 'caption') else None
            })
    
    return documentation

docs = parse_technical_docs('api_documentation.pdf')
print(f"标题: {docs['标题']}")
print(f"章节: {len(docs['章节'])}")
```

### 示例 3：合同分析

```python
from docling.document_converter import DocumentConverter

def analyze_contract(pdf_path):
    """解析合同文档以提取关键条款."""
    
    converter = DocumentConverter()
    result = converter.convert(pdf_path)
    doc = result.document
    
    contract = {
        '当事人': [],
        '条款': [],
        '日期': [],
        '金额': [],
        '全文': doc.export_to_text()
    }
    
    import re
    
    # 提取日期
    date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b'
    contract['日期'] = re.findall(date_pattern, contract['全文'], re.IGNORECASE)
    
    # 提取金额
    amount_pattern = r'\$[\d,]+(?:\.\d{2})?|\b\d+(?:,\d{3})*(?:\.\d{2})?\s*(?:USD|dollars)\b'
    contract['金额'] = re.findall(amount_pattern, contract['全文'], re.IGNORECASE)
    
    # 将章节解析为条款
    for element in doc.iterate_items():
        if element.type == 'heading':
            contract['条款'].append({
                '标题': element.text,
                '内容': ''
            })
        elif element.type == 'paragraph' and contract['条款']:
            contract['条款'][-1]['内容'] += element.text + '\n'
    
    return contract

contract_data = analyze_contract('agreement.pdf')
print(f"关键日期: {contract_data['日期']}")
print(f"金额: {contract_data['金额']}")
```

## 限制

- 非常大的文档可能需要分块处理
- 手写内容需要 OCR 预处理
- 复杂嵌套表格可能需要人工检查
- 某些 PDF 类型（加密）不支持
- 推荐使用 GPU 以获得最佳性能

## 安装

```bash
pip install docling

# 用于完整功能
pip install docling[all]

# 用于 OCR 支持
pip install docling[ocr]
```

## 资源

- [docling GitHub](https://github.com/DS4SD/docling)
- [文档](https://ds4sd.github.io/docling/)
- [IBM 研究博客](https://research.ibm.com/)
