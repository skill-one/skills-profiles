# Markdown to Office 技能

## 概述

该技能使用 **Pandoc**（通用文档转换器）将 Markdown 转换为多种 Office 格式。将您的 Markdown 文件转换为专业的 Word 文档、PowerPoint 演示文稿、PDF 以及更多格式，同时保留格式和结构。

## 使用方法

1. 提供Markdown内容或文件
2. 指定目标格式（docx、pptx、pdf等）
3. 可选地提供用于样式的参考模板
4. 我将使用 Pandoc 以最佳设置进行转换

**示例提示：**
- "将这个 README.md 转换为专业的 Word 文档"
- "将我的 Markdown 笔记转换为 PowerPoint 演示文稿"
- "使用自定义样式从这个 Markdown 生成 PDF"
- "使用公司模板从这个 Markdown 创建 Word 文档"

## 领域知识

### Pandoc 基础知识

```bash
# 基本转换
pandoc input.md -o output.docx
pandoc input.md -o output.pdf
pandoc input.md -o output.pptx

# 使用模板
pandoc input.md --reference-doc=template.docx -o output.docx

# 多个输入
pandoc ch1.md ch2.md ch3.md -o book.docx
```

### 支持的转换

| 从 | 到 | 命令 |
|------|-----|---------|
| Markdown | Word | `pandoc in.md -o out.docx` |
| Markdown | PDF | `pandoc in.md -o out.pdf` |
| Markdown | PowerPoint | `pandoc in.md -o out.pptx` |
| Markdown | HTML | `pandoc in.md -o out.html` |
| Markdown | LaTeX | `pandoc in.md -o out.tex` |
| Markdown | EPUB | `pandoc in.md -o out.epub` |

### Markdown 到 Word (.docx)

#### 基本转换
```bash
pandoc document.md -o document.docx
```

#### 使用模板（参考文档）
```bash
# 首先通过转换示例创建模板
pandoc sample.md -o reference.docx

# 在 Word 中编辑 reference.docx 样式，然后使用它
pandoc input.md --reference-doc=reference.docx -o output.docx
```

#### 使用目录
```bash
pandoc document.md --toc --toc-depth=3 -o document.docx
```

#### 使用元数据
```bash
pandoc document.md \
  --metadata title="我的报告" \
  --metadata author="约翰·多伊" \
  --metadata date="2024-01-15" \
  -o document.docx
```

### Markdown 到 PDF

#### 通过 LaTeX（最佳质量）
```bash
# 需要安装 LaTeX
pandoc document.md -o document.pdf

# 使用自定义设置
pandoc document.md \
  --pdf-engine=xelatex \
  -V geometry:margin=1in \
  -V fontsize=12pt \
  -o document.pdf
```

#### 通过 HTML/wkhtmltopdf
```bash
pandoc document.md \
  --pdf-engine=wkhtmltopdf \
  --css=style.css \
  -o document.pdf
```

#### PDF 选项
```bash
pandoc document.md \
  -V papersize:a4 \
  -V geometry:margin=2cm \
  -V fontfamily:libertinus \
  -V colorlinks:true \
  --toc \
  -o document.pdf
```

### Markdown 到 PowerPoint (.pptx)

#### 基本转换
```bash
pandoc slides.md -o presentation.pptx
```

#### Markdown 结构用于幻灯片
```markdown
---
title: 演示文稿标题
author: 作者姓名
date: 2024年1月
---

# 章节标题（创建章节分隔符）

## 幻灯片标题

- 项目符号点 1
- 项目符号点 2
  - 子项目符号

## 另一个幻灯片

内容在此

::: notes
演讲者笔记在此处（幻灯片中不可见）
:::

## 带图片的幻灯片

![描述](image.png){width=80%}

## 两列幻灯片

:::::::::::::: {.columns}
::: {.column width="50%"}
左列内容
:::

::: {.column width="50%"}
右列内容
:::
::::::::::::::
```

#### 使用模板
```bash
# 使用公司 PowerPoint 模板
pandoc slides.md --reference-doc=template.pptx -o presentation.pptx
```

### YAML 前置内容

在 Markdown 顶部添加元数据：

```yaml
---
title: "文档标题"
author: "作者姓名"
date: "2024-01-15"
abstract: "简要描述"
toc: true
toc-depth: 2
numbersections: true
geometry: margin=1in
fontsize: 11pt
documentclass: report
---

# 第一章
...
```

### Python 集成

```python
import subprocess
import os

def md_to_docx(input_path, output_path, template=None):
    """将 Markdown 转换为 Word 文档."""
    cmd = ['pandoc', input_path, '-o', output_path]
    
    if template:
        cmd.extend(['--reference-doc', template])
    
    subprocess.run(cmd, check=True)
    return output_path

def md_to_pdf(input_path, output_path, **options):
    """使用选项将 Markdown 转换为 PDF."""
    cmd = ['pandoc', input_path, '-o', output_path]
    
    if options.get('toc'):
        cmd.append('--toc')
    
    if options.get('margin'):
        cmd.extend(['-V', f"geometry:margin={options['margin']}"])
    
    subprocess.run(cmd, check=True)
    return output_path

def md_to_pptx(input_path, output_path, template=None):
    """将 Markdown 转换为 PowerPoint."""
    cmd = ['pandoc', input_path, '-o', output_path]
    
    if template:
        cmd.extend(['--reference-doc', template])
    
    subprocess.run(cmd, check=True)
    return output_path
```

### pypandoc（Python 封装器）

```python
import pypandoc

# 简单转换
output = pypandoc.convert_file('input.md', 'docx', outputfile='output.docx')

# 使用选项
output = pypandoc.convert_file(
    'input.md', 
    'docx',
    outputfile='output.docx',
    extra_args=['--toc', '--reference-doc=template.docx']
)

# 从字符串
md_content = "# Hello\n\nThis is markdown."
output = pypandoc.convert_text(md_content, 'docx', format='md', outputfile='output.docx')
```

## 最佳实践

1. **使用模板**：创建参考文档以保持品牌一致性
2. **结构化标题**：使用一致的标题级别（## 用于幻灯片，# 用于章节）
3. **逐步测试**：先转换小部分以验证格式
4. **包含元数据**：使用 YAML 前置内容设置文档属性
5. **处理图片**：使用相对路径并指定尺寸

## 常见模式

### 批量转换
```python
import subprocess
from pathlib import Path

def batch_convert(input_dir, output_format, output_dir=None):
    """转换目录中的所有 Markdown 文件."""
    input_path = Path(input_dir)
    output_path = Path(output_dir) if output_dir else input_path
    
    for md_file in input_path.glob('*.md'):
        output_file = output_path / md_file.with_suffix(f'.{output_format}').name
        subprocess.run([
            'pandoc', str(md_file), '-o', str(output_file)
        ], check=True)
        print(f"转换：{md_file.name} -> {output_file.name}")

batch_convert('./docs', 'docx', './output')
```

### 报告生成器
```python
def generate_report(title, sections, output_path, template=None):
    """从结构化数据生成 Word 报告."""
    
    # 构建Markdown
    md_content = f"""---
title: "{title}"
date: "{datetime.now().strftime('%B %d, %Y')}"
---

"""
    for section_title, content in sections.items():
        md_content += f"# {section_title}\n\n{content}\n\n"
    
    # 写临时文件
    with open('temp_report.md', 'w') as f:
        f.write(md_content)
    
    # 转换
    cmd = ['pandoc', 'temp_report.md', '-o', output_path, '--toc']
    if template:
        cmd.extend(['--reference-doc', template])
    
    subprocess.run(cmd, check=True)
    os.remove('temp_report.md')
```

## 示例

### 示例 1：技术文档
```python
import subprocess

# 创建综合 Markdown
doc = """---
title: "API 文档"
author: "开发团队"
date: "2024-01-15"
toc: true
toc-depth: 2
---

# 简介

本文档描述了我们的服务 REST API。

## 认证

所有 API 请求都需要在头部包含 API 密钥：

```
Authorization: Bearer YOUR_API_KEY
```

## 端点

### GET /users

检索所有用户。

**响应：**

| 字段 | 类型 | 描述 |
|-------|------|-------------|
| id | integer | 用户 ID |
| name | string | 全名 |
| email | string | 电子邮件地址 |

### POST /users

创建新用户。

**请求正文：**

```json
{
  "name": "约翰·多伊",
  "email": "john@example.com"
}
```

## 错误代码

| 代码 | 含义 |
|------|---------|
| 400 | 错误请求 |
| 401 | 未授权 |
| 404 | 未找到 |
| 500 | 服务器错误 |
"""

# 保存 Markdown
with open('api_docs.md', 'w') as f:
    f.write(doc)

# 转换为 Word
subprocess.run([
    'pandoc', 'api_docs.md',
    '-o', 'api_documentation.docx',
    '--toc',
    '--reference-doc', 'company_template.docx'
], check=True)

# 转换为 PDF
subprocess.run([
    'pandoc', 'api_docs.md',
    '-o', 'api_documentation.pdf',
    '--toc',
    '-V', 'geometry:margin=1in',
    '-V', 'fontsize=11pt'
], check=True)
```

### 示例 2：从 Markdown 创建演示文稿
```python
slides_md = """---
title: "2024年第四季度业务回顾"
author: "销售团队"
date: "2024年1月"
---

# 概述

## 议程

- 第四季度表现总结
- 区域亮点
- 2024年展望
- 问答

# 第四季度表现

## 关键指标

- 收入：$12.5M（同比增长15%）
- 新客户：250
- 保留率：94%

## 区域表现

:::::::::::::: {.columns}
::: {.column width="50%"}
**北美**

- 收入：$6.2M
- 增长：+18%
:::

::: {.column width="50%"}
**欧洲**

- 收入：$4.1M
- 增长：+12%
:::
::::::::::::::

# 2024年展望

## 战略优先事项

1. 扩大亚太地区业务
2. 推出新产品线
3. 改进客户入职流程

## 收入目标

| 季度 | 目标 |
|---------|--------|
| Q1 | $13M |
| Q2 | $14M |
| Q3 | $15M |
| Q4 | $16M |

# 感谢

## 问答？

联系方式：sales@company.com
"""

with open('presentation.md', 'w') as f:
    f.write(slides_md)

subprocess.run([
    'pandoc', 'presentation.md',
    '-o', 'q4_review.pptx',
    '--reference-doc', 'company_slides.pptx'
], check=True)
```

## 限制

- 复杂 Word 格式可能无法完美转换
- PDF 转换需要 LaTeX 或 wkhtmltopdf
- PowerPoint 动画不支持
- 一些高级表格需要手动调整
- 图片定位可能比较复杂

## 安装

```bash
# macOS
brew install pandoc

# Ubuntu/Debian
sudo apt-get install pandoc

# Windows
choco install pandoc

# Python 封装器
pip install pypandoc
```

## 资源

- [Pandoc 用户指南](https://pandoc.org/MANUAL.html)
- [GitHub 仓库](https://github.com/jgm/pandoc)
- [Pandoc 模板](https://github.com/jgm/pandoc-templates)
- [pypandoc 文档](https://github.com/JessicaTegworthy/pypandoc)
