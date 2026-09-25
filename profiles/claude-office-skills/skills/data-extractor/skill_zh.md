# 数据提取技能

## 概述

该技能能够使用 **非结构化**（一个用于处理 PDF、Word 文档、电子邮件、HTML 等的统一库）从任何文档格式中提取结构化数据。无论输入格式如何，都能获得一致的结构化输出。

## 如何使用

1. 提供要处理的文档
2. 可选地指定提取选项
3. 我将提取带有元数据的结构化元素

**示例提示：**
- "从该 PDF 中提取所有文本和表格"
- "解析此电子邮件并获取正文、附件和元数据"
- "将此 HTML 页面转换为结构化元素"
- "从这些混合格式文档中提取数据"

## 领域知识

### unstructured 基础知识

```python
from unstructured.partition.auto import partition

# 自动检测和处理任何文档
elements = partition("document.pdf")

# 访问提取的元素
for element in elements:
    print(f"类型: {type(element).__name__}")
    print(f"文本: {element.text}")
    print(f"元数据: {element.metadata}")
```

### 支持的格式

| 格式 | 功能 | 备注 |
|------|------|------|
| PDF | `partition_pdf` | 原生 + 扫描 |
| Word | `partition_docx` | 完整结构 |
| PowerPoint | `partition_pptx` | 幻灯片 & 笔记 |
| Excel | `partition_xlsx` | 工作表 & 表格 |
| 电子邮件 | `partition_email` | 正文 & 附件 |
| HTML | `partition_html` | 保留标签 |
| Markdown | `partition_md` | 保留结构 |
| 纯文本 | `partition_text` | 基本解析 |
| 图像 | `partition_image` | OCR 提取 |

### 元素类型

```python
from unstructured.documents.elements import (
    Title,
    NarrativeText,
    Text,
    ListItem,
    Table,
    Image,
    Header,
    Footer,
    PageBreak,
    Address,
    EmailAddress,
)

# 元素具有一致的结构
element.text           # 原始文本内容
element.metadata       # 丰富的元数据
element.category       # 元素类型
element.id            # 唯一标识符
```

### 自动分区

```python
from unstructured.partition.auto import partition

# 处理任何文件类型
elements = partition(
    filename="document.pdf",
    strategy="auto",          # 或 "fast", "hi_res", "ocr_only"
    include_metadata=True,
    include_page_breaks=True,
)

# 按类型过滤
titles = [e for e in elements if isinstance(e, Title)]
tables = [e for e in elements if isinstance(e, Table)]
```

### 格式特定分区

```python
# PDF 带选项
from unstructured.partition.pdf import partition_pdf

elements = partition_pdf(
    filename="document.pdf",
    strategy="hi_res",              # 高质量提取
    infer_table_structure=True,     # 检测表格
    include_page_breaks=True,
    languages=["en"],               # OCR 语言
)

# Word 文档
from unstructured.partition.docx import partition_docx

elements = partition_docx(
    filename="document.docx",
    include_metadata=True,
)

# HTML
from unstructured.partition.html import partition_html

elements = partition_html(
    filename="page.html",
    include_metadata=True,
)
```

### 处理表格

```python
from unstructured.partition.auto import partition

elements = partition("report.pdf", infer_table_structure=True)

# 提取表格
for element in elements:
    if element.category == "Table":
        print("找到表格:")
        print(element.text)
        
        # 访问结构化表格数据
        if hasattr(element, 'metadata') and element.metadata.text_as_html:
            print("HTML:", element.metadata.text_as_html)
```

### 元数据访问

```python
from unstructured.partition.auto import partition

elements = partition("document.pdf")

for element in elements:
    meta = element.metadata
    
    # 常见元数据字段
    print(f"页码: {meta.page_number}")
    print(f"文件名: {meta.filename}")
    print(f"文件类型: {meta.filetype}")
    print(f"坐标: {meta.coordinates}")
    print(f"语言: {meta.languages}")
```

### 用于 AI/RAG 的分块

```python
from unstructured.partition.auto import partition
from unstructured.chunking.title import chunk_by_title
from unstructured.chunking.basic import chunk_elements

# 分区文档
elements = partition("document.pdf")

# 按标题分块（语义块）
chunks = chunk_by_title(
    elements,
    max_characters=1000,
    combine_text_under_n_chars=200,
)

# 或基本分块
chunks = chunk_elements(
    elements,
    max_characters=500,
    overlap=50,
)

for chunk in chunks:
    print(f"块 ({len(chunk.text)} 字符):")
    print(chunk.text[:100] + "...")
```

### 批量处理

```python
from unstructured.partition.auto import partition
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

def process_document(file_path):
    """处理单个文档."""
    try:
        elements = partition(str(file_path))
        return {
            '文件': str(file_path),
            '状态': '成功',
            '元素数量': len(elements),
            '文本': '\n\n'.join([e.text for e in elements])
        }
    except Exception as e:
        return {
            '文件': str(file_path),
            '状态': '错误',
            '错误': str(e)
        }

def batch_process(input_dir, max_workers=4):
    """处理目录中的所有文档."""
    input_path = Path(input_dir)
    files = list(input_path.glob('*'))
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(process_document, files))
    
    return results
```

### 导出格式

```python
from unstructured.partition.auto import partition
from unstructured.staging.base import elements_to_json, elements_to_dicts

elements = partition("document.pdf")

# 导出为 JSON 字符串
json_str = elements_to_json(elements)

# 导出为字典列表
dicts = elements_to_dicts(elements)

# 导出为 DataFrame
import pandas as pd
df = pd.DataFrame(dicts)
```

## 最佳实践

1. **明智选择策略**： "fast" 用于速度，"hi_res" 用于准确性
2. **启用表格检测**： 对于包含表格的文档
3. **指定语言**： 对于非英文文档的更好 OCR
4. **分块用于 RAG**： 使用语义分块用于 AI 应用
5. **处理错误**： 某些格式可能优雅地失败

## 常见模式

### 文档转换为 JSON

```python
def document_to_json(file_path, output_path=None):
    """将文档转换为结构化 JSON."""
    from unstructured.partition.auto import partition
    from unstructured.staging.base import elements_to_json
    import json
    
    elements = partition(file_path)
    
    # 创建结构化输出
    output = {
        '来源': file_path,
        '元素': []
    }
    
    for element in elements:
        output['元素'].append({
            '类型': type(element).__name__,
            '文本': element.text,
            '元数据': {
                '页码': element.metadata.page_number,
                '坐标': element.metadata.coordinates.to_dict() if element.metadata.coordinates else None
            }
        })
    
    if output_path:
        with open(output_path, 'w') as f:
            json.dump(output, f, indent=2)
    
    return output
```

### 电子邮件解析器

```python
from unstructured.partition.email import partition_email

def parse_email(email_path):
    """从电子邮件中提取结构化数据."""
    
    elements = partition_email(email_path)
    
    email_data = {
        '主题': None,
        '发件人': None,
        '收件人': [],
        '日期': None,
        '正文': [],
        '附件': []
    }
    
    for element in elements:
        meta = element.metadata
        
        # 从元数据中提取标题
        if meta.subject:
            email_data['主题'] = meta.subject
        if meta.sent_from:
            email_data['发件人'] = meta.sent_from
        if meta.sent_to:
            email_data['收件人'] = meta.sent_to
        
        # 正文内容
        email_data['正文'].append({
            '类型': type(element).__name__,
            '文本': element.text
        })
    
    return email_data
```

## 示例

### 示例 1：研究论文提取

```python
from unstructured.partition.pdf import partition_pdf
from unstructured.chunking.title import chunk_by_title

def extract_paper(pdf_path):
    """从研究论文中提取结构化数据."""
    
    elements = partition_pdf(
        filename=pdf_path,
        strategy="hi_res",
        infer_table_structure=True,
        include_page_breaks=True
    )
    
    paper = {
        '标题': None,
        '摘要': None,
        '章节': [],
        '表格': [],
        '参考文献': []
    }
    
    # 找到标题（通常是第一个 Title 元素）
    for element in elements:
        if element.category == "Title" and not paper['标题']:
            paper['标题'] = element.text
            break
    
    # 提取表格
    for element in elements:
        if element.category == "Table":
            paper['表格'].append({
                '页码': element.metadata.page_number,
                '内容': element.text,
                'html': element.metadata.text_as_html if hasattr(element.metadata, 'text_as_html') else None
            })
    
    # 分块为章节
    chunks = chunk_by_title(elements, max_characters=2000)
    
    current_section = None
    for chunk in chunks:
        if chunk.category == "Title":
            paper['章节'].append({
                '标题': chunk.text,
                '内容': ''
            })
        elif paper['章节']:
            paper['章节'][-1]['内容'] += chunk.text + '\n'
    
    return paper

paper = extract_paper('research_paper.pdf')
print(f"标题: {paper['标题']}")
print(f"表格数量: {len(paper['表格'])}")
print(f"章节数量: {len(paper['章节'])}")
```

### 示例 2：发票数据提取

```python
from unstructured.partition.auto import partition
import re

def extract_invoice_data(file_path):
    """从发票中提取关键数据."""
    
    elements = partition(file_path, strategy="hi_res")
    
    # 合并所有文本
    full_text = '\n'.join([e.text for e in elements])
    
    invoice = {
        '发票编号': None,
        '日期': None,
        '总计': None,
        '供应商': None,
        '明细项': [],
        '表格': []
    }
    
    # 提取模式
    inv_match = re.search(r'Invoice\s*#?\s*:?\s*(\w+[-\w]*)', full_text, re.I)
    if inv_match:
        invoice['发票编号'] = inv_match.group(1)
    
    date_match = re.search(r'Date\s*:?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})', full_text, re.I)
    if date_match:
        invoice['日期'] = date_match.group(1)
    
    total_match = re.search(r'Total\s*:?\s*\$?([\d,]+\.?\d*)', full_text, re.I)
    if total_match:
        invoice['总计'] = float(total_match.group(1).replace(',', ''))
    
    # 提取表格
    for element in elements:
        if element.category == "Table":
            invoice['表格'].append(element.text)
    
    return invoice

invoice = extract_invoice_data('invoice.pdf')
print(f"发票编号: {invoice['发票编号']}")
print(f"总计: ${invoice['总计']}")
```

### 示例 3：文档语料库构建器

```python
from unstructured.partition.auto import partition
from unstructured.chunking.title import chunk_by_title
from pathlib import Path
import json

def build_corpus(input_dir, output_path):
    """从文档集合构建可搜索语料库."""
    
    input_path = Path(input_dir)
    corpus = []
    
    # 支持多种格式
    patterns = ['*.pdf', '*.docx', '*.html', '*.txt', '*.md']
    files = []
    for pattern in patterns:
        files.extend(input_path.glob(pattern))
    
    for file in files:
        print(f"处理: {file.name}")
        
        try:
            elements = partition(str(file))
            chunks = chunk_by_title(elements, max_characters=1000)
            
            for i, chunk in enumerate(chunks):
                corpus.append({
                    'id': f"{file.stem}_{i}",
                    '来源': str(file),
                    '类型': type(chunk).__name__,
                    '文本': chunk.text,
                    '页码': chunk.metadata.page_number if chunk.metadata.page_number else None
                })
        
        except Exception as e:
            print(f"  错误: {e}")
    
    # 保存语料库
    with open(output_path, 'w') as f:
        json.dump(corpus, f, indent=2)
    
    print(f"语料库构建: 从 {len(files)} 个文件中提取 {len(corpus)} 个块")
    return corpus

corpus = build_corpus('./documents', 'corpus.json')
```

## 限制

- 复杂布局可能需要人工审核
- OCR 质量取决于图像质量
- 大文件可能需要分块
- 某些专有格式不受支持
- 云处理 API 的速率限制

## 安装

```bash
# 基本安装
pip install unstructured

# 带所有依赖
pip install "unstructured[all-docs]"

# 用于 PDF 处理
pip install "unstructured[pdf]"

# 用于特定格式
pip install "unstructured[docx,pptx,xlsx]"
```

## 资源

- [unstructured GitHub](https://github.com/Unstructured-IO/unstructured)
- [文档](https://unstructured-io.github.io/unstructured/)
- [Unstructured API](https://unstructured.io/api-key)
