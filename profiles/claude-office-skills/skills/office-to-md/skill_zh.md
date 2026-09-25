# Office to Markdown 技能

## 概述

该技能能够使用 **markitdown**（微软的开源工具）将各种 Office 格式转换为 Markdown。非常适合使 Office 内容可搜索、可版本控制且对 AI 友好。

## 如何使用

1. 提供 Office 文件（Word、Excel、PowerPoint、PDF 等）
2. 可选地指定转换选项
3. 我将将其转换为干净的 Markdown

**示例提示：**
- "将这个 Word 文档转换为 Markdown"
- "将这个 PowerPoint 转换为 Markdown 笔记"
- "将这个 PDF 的内容提取为 Markdown"
- "将这个 Excel 文件转换为 Markdown 表格"

## 领域知识

### markitdown 基础

```python
from markitdown import MarkItDown

# 初始化转换器
md = MarkItDown()

# 转换文件
result = md.convert("document.docx")
print(result.text_content)

# 保存到文件
with open("output.md", "w") as f:
    f.write(result.text_content)
```

### 支持的格式

| 格式 | 扩展名 | 备注 |
|------|--------|------|
| Word | .docx | 完整文本、表格、基本格式 |
| Excel | .xlsx | 转换为 Markdown 表格 |
| PowerPoint | .pptx | 幻灯片作为章节 |
| PDF | .pdf | 文本提取 |
| HTML | .html | 干净的 Markdown |
| 图片 | .jpg, .png | 使用视觉模型进行 OCR |
| 音频 | .mp3, .wav | 转录 |
| ZIP | .zip | 处理包含的文件 |

### 基本使用

#### Python API

```python
from markitdown import MarkItDown

# 简单转换
md = MarkItDown()
result = md.convert("document.docx")

# 访问内容
markdown_text = result.text_content

# 带选项
md = MarkItDown(
    llm_client=None,      # 可选的 LLM 用于增强处理
    llm_model=None        # 如果使用 LLM，模型名称
)
```

#### 命令行

```bash
# 安装
pip install markitdown

# 转换文件
markitdown document.docx > output.md

# 或带输出文件
markitdown document.docx -o output.md
```

### Word 文档转换

```python
from markitdown import MarkItDown

md = MarkItDown()

# 转换 Word 文档
result = md.convert("report.docx")

# 输出保留：
# - 标题（作为 # 标题）
# - 粗体/斜体格式
# - 列表（项目符号和编号）
# - 表格（作为 Markdown 表格）
# - 链接

print(result.text_content)
```

**示例输出：**
```markdown
# 2024 年度报告

## 执行摘要

本报告总结了主要成就和挑战...

### 关键指标

| 指标 | 2023 | 2024 | 变化 |
|------|-----|-----|------|
| 收入 | $10M | $12M | +20% |
| 用户 | 50K | 75K | +50% |

## 详细分析

以下章节提供...

```

### Excel 转换

```python
from markitdown import MarkItDown

md = MarkItDown()
result = md.convert("data.xlsx")

# 每个工作表成为一个章节
# 数据转换为 Markdown 表格
print(result.text_content)
```

**示例输出：**
```markdown
## Sheet1

| 名称 | 部门 | 薪资 |
|------|------|------|
| John | 工程 | $80,000 |
| Jane | 市场 | $75,000 |

## Sheet2

| 产品 | Q1 | Q2 | Q3 | Q4 |
|------|----|----|----|----|
| Widget A | 100 | 120 | 150 | 180 |
```

### PowerPoint 转换

```python
from markitdown import MarkItDown

md = MarkItDown()
result = md.convert("presentation.pptx")

# 每个幻灯片成为一个章节
# 如果存在，包含演讲者笔记
print(result.text_content)
```

**示例输出：**
```markdown
# 幻灯片 1：公司概述

我们的使命是...

## 关键要点
- 首创精神
- 客户至上
- 全球覆盖

---

# 幻灯片 2：市场分析

市场机会非常重要...

**备注：** 在此处提及竞争对手分析
```

### PDF 转换

```python
from markitdown import MarkItDown

md = MarkItDown()
result = md.convert("document.pdf")

# 提取文本内容
# 检测到的表格转换为 Markdown
print(result.text_content)
```

### 图片转换（带视觉模型）

```python
from markitdown import MarkItDown
import anthropic

# 使用 Claude 进行图片描述
client = anthropic.Anthropic()

md = MarkItDown(
    llm_client=client,
    llm_model="claude-sonnet-4-20250514"
)

result = md.convert("diagram.png")
print(result.text_content)

# 输出：图片内容的描述
```

### 批量转换

```python
from markitdown import MarkItDown
from pathlib import Path

def batch_convert(input_dir, output_dir):
    """将所有 Office 文件转换为 Markdown."""
    md = MarkItDown()
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    extensions = ['.docx', '.xlsx', '.pptx', '.pdf']
    
    for ext in extensions:
        for file in input_path.glob(f'*{ext}'):
            try:
                result = md.convert(str(file))
                output_file = output_path / f"{file.stem}.md"
                
                with open(output_file, 'w') as f:
                    f.write(result.text_content)
                
                print(f"转换完成：{file.name}")
            except Exception as e:
                print(f"转换错误 {file.name}：{e}")

batch_convert('./documents', './markdown')
```

## 最佳实践

1. **检查输出质量**：检查转换后的 Markdown 准确性
2. **处理表格**：复杂的表格可能需要手动调整
3. **保留结构**：在源文档中使用一致的标题级别
4. **图片处理**：考虑使用视觉模型处理重要图片
5. **版本控制**：将转换后的 Markdown 存储在 Git 中进行跟踪

## 常见模式

### 文档归档

```python
import os
from datetime import datetime
from markitdown import MarkItDown

def archive_document(doc_path, archive_dir):
    """将 Office 文档转换为 Markdown 并归档."""
    md = MarkItDown()
    result = md.convert(doc_path)
    
    # 创建归档结构
    date_str = datetime.now().strftime('%Y-%m-%d')
    filename = os.path.basename(doc_path)
    base_name = os.path.splitext(filename)[0]
    
    # 带元数据保存
    output_content = f"""---
source: {filename}
converted: {date_str}
---

{result.text_content}
"""
    
    output_path = os.path.join(archive_dir, f"{base_name}.md")
    with open(output_path, 'w') as f:
        f.write(output_content)
    
    return output_path
```

### AI-准备语料库

```python
from markitdown import MarkItDown
from pathlib import Path
import json

def create_ai_corpus(doc_folder, output_file):
    """将文档转换为 JSON 语料库用于 AI 训练/RAG."""
    md = MarkItDown()
    corpus = []
    
    for doc in Path(doc_folder).glob('**/*'):
        if doc.suffix in ['.docx', '.pdf', '.pptx', '.xlsx']:
            try:
                result = md.convert(str(doc))
                corpus.append({
                    'source': str(doc),
                    'filename': doc.name,
                    'content': result.text_content,
                    'type': doc.suffix[1:]
                })
            except Exception as e:
                print(f"跳过 {doc.name}：{e}")
    
    with open(output_file, 'w') as f:
        json.dump(corpus, f, indent=2)
    
    print(f"创建语料库，包含 {len(corpus)} 个文档")
    return corpus
```

## 示例

### 示例 1：转换文档套件

```python
from markitdown import MarkItDown
from pathlib import Path

def convert_docs_to_wiki(docs_folder, wiki_folder):
    """将所有 Office 文档转换为 Markdown 维基结构."""
    md = MarkItDown()
    docs_path = Path(docs_folder)
    wiki_path = Path(wiki_folder)
    
    # 创建维基结构
    wiki_path.mkdir(exist_ok=True)
    
    # 创建索引
    index_content = "# 文档索引\n\n"
    
    for doc in sorted(docs_path.glob('**/*.docx')):
        try:
            result = md.convert(str(doc))
            
            # 在维基中创建相对路径
            rel_path = doc.relative_to(docs_path)
            output_file = wiki_path / rel_path.with_suffix('.md')
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 写入 Markdown
            with open(output_file, 'w') as f:
                f.write(result.text_content)
            
            # 添加到索引
            link = str(rel_path.with_suffix('.md')).replace('\\', '/')
            index_content += f"- [{doc.stem}]({link})\n"
            
            print(f"转换完成：{doc.name}")
            
        except Exception as e:
            print(f"错误：{doc.name} - {e}")
    
    # 写入索引
    with open(wiki_path / 'index.md', 'w') as f:
        f.write(index_content)

convert_docs_to_wiki('./company_docs', './wiki')
```

### 示例 2：会议笔记处理器

```python
from markitdown import MarkItDown
import re
from datetime import datetime

def process_meeting_notes(pptx_path):
    """从 PowerPoint 提取和结构化会议笔记."""
    md = MarkItDown()
    result = md.convert(pptx_path)
    
    # 解析 Markdown
    content = result.text_content
    
    # 提取章节
    sections = {
        'attendees': [],
        'agenda': [],
        'decisions': [],
        'action_items': []
    }
    
    current_section = None
    
    for line in content.split('\n'):
        line_lower = line.lower()
        
        if 'attendee' in line_lower or 'participant' in line_lower:
            current_section = 'attendees'
        elif 'agenda' in line_lower:
            current_section = 'agenda'
        elif 'decision' in line_lower:
            current_section = 'decisions'
        elif 'action' in line_lower:
            current_section = 'action_items'
        elif line.strip().startswith(('-', '*', '•')) and current_section:
            sections[current_section].append(line.strip()[1:].strip())
    
    # 生成结构化输出
    output = f"""# 会议笔记

**日期：** {datetime.now().strftime('%Y-%m-%d')}
**来源：** {pptx_path}

## 参会人员
{chr(10).join('- ' + a for a in sections['attendees'])}

## 议程
{chr(10).join('- ' + a for a in sections['agenda'])}

## 做出的决定
{chr(10).join('- ' + d for d in sections['decisions'])}

## 行动项
{chr(10).join('- [ ] ' + a for a in sections['action_items'])}
"""
    
    return output

notes = process_meeting_notes('team_meeting.pptx')
print(notes)
```

### 示例 3：Excel 到文档

```python
from markitdown import MarkItDown

def excel_to_data_dictionary(xlsx_path):
    """将 Excel 数据模型转换为数据字典文档."""
    md = MarkItDown()
    result = md.convert(xlsx_path)
    
    # 添加文档结构
    doc = f"""# 数据字典

生成自：`{xlsx_path}`

{result.text_content}

## 使用说明

- 所有表格都来自源 Excel 文件
- 在使用前检查数据类型和约束
- 联系数据团队获取澄清

## 更改日志

| 日期 | 更改 | 作者 |
|------|------|------|
| {datetime.now().strftime('%Y-%m-%d')} | 初始生成 | 自动 |
"""
    
    return doc

documentation = excel_to_data_dictionary('data_model.xlsx')
with open('data_dictionary.md', 'w') as f:
    f.write(documentation)
```

## 限制

- 复杂格式可能被简化
- 图片不嵌入（使用视觉模型进行描述）
- 一些表格结构可能无法完美转换
- Word 中的跟踪更改不会保留
- 注释可能无法提取

## 安装

```bash
pip install markitdown

# 用于图片/音频处理
pip install markitdown[all]

# 用于特定功能
pip install markitdown[images]  # 图片 OCR
pip install markitdown[audio]   # 音频转录
```

## 资源

- [GitHub 仓库](https://github.com/microsoft/markitdown)
- [PyPI 包](https://pypi.org/project/markitdown/)
- [支持的格式](https://github.com/microsoft/markitdown#supported-formats)
