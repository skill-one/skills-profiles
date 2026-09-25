# 批量转换技能

## 概述

该技能能够使用统一的工作流在多种格式之间批量转换文档。通过一致的设置、自动格式检测和并行处理，您可以一次性转换数百个文件，实现最大效率。

## 使用方法

1. 指定源文件夹或文件
2. 选择目标格式
3. 可选配置转换选项
4. 我将处理所有文件并跟踪进度

**示例提示：**
- "将此文件夹中的所有PDF转换为Word文档"
- "批量将这些Markdown文件转换为PDF和HTML"
- "处理所有Office文件并转换为Markdown"
- "将此文件夹中的图像转换为单个PDF"

## 领域知识

### 支持的格式矩阵

| 从 | 到: DOCX | 到: PDF | 到: MD | 到: HTML | 到: PPTX |
|------|----------|---------|--------|----------|----------|
| DOCX | - | ✅ | ✅ | ✅ | - |
| PDF | ✅ | - | ✅ | ✅ | - |
| MD | ✅ | ✅ | - | ✅ | ✅ |
| HTML | ✅ | ✅ | ✅ | - | - |
| XLSX | - | ✅ | ✅ | ✅ | - |
| PPTX | - | ✅ | ✅ | ✅ | - |

### 核心工作流

```python
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess
import os

class DocumentConverter:
    """统一文档转换工作流。"""
    
    def __init__(self, max_workers=4):
        self.max_workers = max_workers
        self.converters = {
            ('md', 'docx'): self._md_to_docx,
            ('md', 'pdf'): self._md_to_pdf,
            ('md', 'html'): self._md_to_html,
            ('md', 'pptx'): self._md_to_pptx,
            ('docx', 'pdf'): self._docx_to_pdf,
            ('docx', 'md'): self._docx_to_md,
            ('pdf', 'docx'): self._pdf_to_docx,
            ('pdf', 'md'): self._pdf_to_md,
            ('xlsx', 'pdf'): self._xlsx_to_pdf,
            ('xlsx', 'md'): self._xlsx_to_md,
            ('pptx', 'pdf'): self._pptx_to_pdf,
            ('pptx', 'md'): self._pptx_to_md,
            ('html', 'md'): self._html_to_md,
            ('html', 'pdf'): self._html_to_pdf,
        }
    
    def convert(self, input_path, output_format, output_dir=None):
        """将单个文件转换为目标格式。"""
        input_path = Path(input_path)
        input_format = input_path.suffix[1:].lower()
        
        if output_dir:
            output_path = Path(output_dir) / f"{input_path.stem}.{output_format}"
        else:
            output_path = input_path.with_suffix(f".{output_format}")
        
        converter_key = (input_format, output_format)
        if converter_key not in self.converters:
            raise ValueError(f"不支持转换: {input_format} -> {output_format}")
        
        converter = self.converters[converter_key]
        return converter(input_path, output_path)
    
    def batch_convert(self, input_dir, output_format, output_dir=None, 
                      file_pattern="*", recursive=False):
        """批量转换所有匹配的文件。"""
        input_path = Path(input_dir)
        output_path = Path(output_dir) if output_dir else input_path / "converted"
        output_path.mkdir(exist_ok=True)
        
        # 查找文件
        if recursive:
            files = list(input_path.rglob(file_pattern))
        else:
            files = list(input_path.glob(file_pattern))
        
        # 筛选支持的格式
        supported_ext = ['.md', '.docx', '.pdf', '.xlsx', '.pptx', '.html']
        files = [f for f in files if f.suffix.lower() in supported_ext]
        
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {
                executor.submit(self.convert, f, output_format, output_path): f
                for f in files
            }
            
            for future in as_completed(future_to_file):
                file = future_to_file[future]
                try:
                    result = future.result()
                    results.append({'file': str(file), 'status': 'success', 'output': str(result)})
                except Exception as e:
                    results.append({'file': str(file), 'status': 'error', 'error': str(e)})
        
        return results
```

### 转换实现

```python
# Markdown转换（使用Pandoc）
def _md_to_docx(self, input_path, output_path):
    subprocess.run(['pandoc', str(input_path), '-o', str(output_path)], check=True)
    return output_path

def _md_to_pdf(self, input_path, output_path):
    subprocess.run(['pandoc', str(input_path), '-o', str(output_path)], check=True)
    return output_path

def _md_to_html(self, input_path, output_path):
    subprocess.run(['pandoc', str(input_path), '-s', '-o', str(output_path)], check=True)
    return output_path

def _md_to_pptx(self, input_path, output_path):
    subprocess.run(['marp', str(input_path), '-o', str(output_path)], check=True)
    return output_path

# Office到Markdown（使用markitdown）
def _docx_to_md(self, input_path, output_path):
    from markitdown import MarkItDown
    md = MarkItDown()
    result = md.convert(str(input_path))
    with open(output_path, 'w') as f:
        f.write(result.text_content)
    return output_path

def _xlsx_to_md(self, input_path, output_path):
    from markitdown import MarkItDown
    md = MarkItDown()
    result = md.convert(str(input_path))
    with open(output_path, 'w') as f:
        f.write(result.text_content)
    return output_path

def _pptx_to_md(self, input_path, output_path):
    from markitdown import MarkItDown
    md = MarkItDown()
    result = md.convert(str(input_path))
    with open(output_path, 'w') as f:
        f.write(result.text_content)
    return output_path

# PDF转换
def _pdf_to_docx(self, input_path, output_path):
    from pdf2docx import Converter
    cv = Converter(str(input_path))
    cv.convert(str(output_path))
    cv.close()
    return output_path

def _pdf_to_md(self, input_path, output_path):
    from markitdown import MarkItDown
    md = MarkItDown()
    result = md.convert(str(input_path))
    with open(output_path, 'w') as f:
        f.write(result.text_content)
    return output_path

# Office到PDF（使用LibreOffice）
def _docx_to_pdf(self, input_path, output_path):
    subprocess.run([
        'soffice', '--headless', '--convert-to', 'pdf',
        '--outdir', str(output_path.parent), str(input_path)
    ], check=True)
    return output_path

def _xlsx_to_pdf(self, input_path, output_path):
    subprocess.run([
        'soffice', '--headless', '--convert-to', 'pdf',
        '--outdir', str(output_path.parent), str(input_path)
    ], check=True)
    return output_path

def _pptx_to_pdf(self, input_path, output_path):
    subprocess.run([
        'soffice', '--headless', '--convert-to', 'pdf',
        '--outdir', str(output_path.parent), str(input_path)
    ], check=True)
    return output_path
```

### 进度跟踪

```python
from tqdm import tqdm

def batch_convert_with_progress(converter, input_dir, output_format, output_dir=None):
    """带进度条的批量转换。"""
    input_path = Path(input_dir)
    files = list(input_path.glob('*'))
    
    results = []
    for file in tqdm(files, desc=f"转换为 {output_format}"):
        try:
            result = converter.convert(file, output_format, output_dir)
            results.append({'file': str(file), 'status': 'success'})
        except Exception as e:
            results.append({'file': str(file), 'status': 'error', 'error': str(e)})
    
    return results
```

## 最佳实践

1. **先测试样本**：批量处理前先转换几个文件
2. **检查磁盘空间**：确保有足够的输出空间
3. **使用并行处理**：通过多个工作线程加速
4. **优雅处理错误**：记录失败日志，继续处理
5. **验证输出**：抽查转换后的文件

## 常见模式

### 格式检测工作流
```python
def detect_and_convert(file_path, target_format):
    """自动检测格式并转换。"""
    import mimetypes
    
    mime_type, _ = mimetypes.guess_type(str(file_path))
    
    format_map = {
        'application/pdf': 'pdf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'xlsx',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'pptx',
        'text/markdown': 'md',
        'text/html': 'html',
    }
    
    source_format = format_map.get(mime_type, Path(file_path).suffix[1:])
    
    converter = DocumentConverter()
    return converter.convert(file_path, target_format)
```

### 多格式输出
```python
def convert_to_multiple_formats(input_file, output_formats, output_dir):
    """将单个文件转换为多种格式。"""
    converter = DocumentConverter()
    results = {}
    
    for fmt in output_formats:
        try:
            output = converter.convert(input_file, fmt, output_dir)
            results[fmt] = {'status': 'success', 'path': str(output)}
        except Exception as e:
            results[fmt] = {'status': 'error', 'error': str(e)}
    
    return results

# 将README转换为多种格式
results = convert_to_multiple_formats(
    'README.md',
    ['docx', 'pdf', 'html'],
    './exports'
)
```

## 示例

### 示例1：文档导出
```python
from pathlib import Path
import json

def export_documentation(docs_dir, export_dir):
    """将所有文档导出到多种格式。"""
    
    converter = DocumentConverter(max_workers=8)
    docs_path = Path(docs_dir)
    export_path = Path(export_dir)
    
    # 创建格式目录
    for fmt in ['pdf', 'docx', 'html']:
        (export_path / fmt).mkdir(parents=True, exist_ok=True)
    
    all_results = {}
    
    # 查找所有Markdown文件
    md_files = list(docs_path.rglob('*.md'))
    
    for md_file in md_files:
        file_results = {}
        
        for fmt in ['pdf', 'docx', 'html']:
            output_dir = export_path / fmt
            try:
                output = converter.convert(md_file, fmt, output_dir)
                file_results[fmt] = 'success'
            except Exception as e:
                file_results[fmt] = f'error: {e}'
        
        all_results[str(md_file)] = file_results
        print(f"处理: {md_file.name}")
    
    # 保存报告
    with open(export_path / 'export_report.json', 'w') as f:
        json.dump(all_results, f, indent=2)
    
    return all_results

results = export_documentation('./docs', './exports')
```

### 示例2：遗留文档迁移
```python
def migrate_legacy_docs(source_dir, target_dir):
    """将遗留文档迁移到现代格式。"""
    
    converter = DocumentConverter(max_workers=4)
    
    # 迁移规则
    migrations = [
        ('*.doc', 'docx'),   # 旧版Word到新版
        ('*.xls', 'xlsx'),   # 旧版Excel到新版
        ('*.ppt', 'pptx'),   # 旧版PowerPoint到新版
        ('*.rtf', 'docx'),   # RTF到Word
    ]
    
    source_path = Path(source_dir)
    target_path = Path(target_dir)
    target_path.mkdir(exist_ok=True)
    
    total_migrated = 0
    errors = []
    
    for pattern, target_format in migrations:
        files = list(source_path.glob(pattern))
        
        for file in files:
            try:
                # 使用LibreOffice处理遗留格式
                subprocess.run([
                    'soffice', '--headless',
                    '--convert-to', target_format,
                    '--outdir', str(target_path),
                    str(file)
                ], check=True)
                
                total_migrated += 1
                print(f"迁移: {file.name}")
                
            except Exception as e:
                errors.append({'file': str(file), 'error': str(e)})
    
    print(f"\n迁移完成: {total_migrated}个文件")
    print(f"错误: {len(errors)}")
    
    return {'migrated': total_migrated, 'errors': errors}
```

### 示例3：报告生成工作流
```python
def generate_reports_pipeline(data_files, template_dir, output_dir):
    """使用模板从数据文件生成报告。"""
    
    from datetime import datetime
    
    converter = DocumentConverter()
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    reports = []
    
    for data_file in data_files:
        # 加载数据
        data_path = Path(data_file)
        
        # 生成Markdown报告
        md_content = f"""---
title: 报告 - {data_path.stem}
date: {datetime.now().strftime('%Y-%m-%d')}
---

# {data_path.stem} 报告

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 数据摘要

"""
        
        # 添加数据内容（简化版）
        if data_path.suffix == '.xlsx':
            from markitdown import MarkItDown
            md = MarkItDown()
            result = md.convert(str(data_path))
            md_content += result.text_content
        
        # 保存Markdown
        md_file = output_path / f"{data_path.stem}_{timestamp}.md"
        with open(md_file, 'w') as f:
            f.write(md_content)
        
        # 转换为PDF和DOCX
        for fmt in ['pdf', 'docx']:
            try:
                output = converter.convert(md_file, fmt, output_path)
                reports.append({'source': str(data_file), 'output': str(output), 'format': fmt})
            except Exception as e:
                print(f"错误：将 {data_file} 转换为 {fmt}: {e}")
    
    return reports
```

## 限制

- 部分格式组合不支持
- 复杂格式可能在转换中丢失
- 大文件可能需要更多时间
- 某些转换需要外部工具（LibreOffice、Pandoc）
- 质量因源文档复杂度而异

## 安装

```bash
# 核心依赖
pip install pdf2docx markitdown python-docx openpyxl

# Pandoc（用于MD转换）
brew install pandoc  # macOS
apt install pandoc   # Ubuntu

# Marp（用于PPTX）
npm install -g @marp-team/marp-cli

# LibreOffice（用于Office格式）
brew install libreoffice  # macOS
apt install libreoffice   # Ubuntu
```

## 资源

- [Pandoc文档](https://pandoc.org/MANUAL.html)
- [markitdown GitHub](https://github.com/microsoft/markitdown)
- [pdf2docx文档](https://pdf2docx.readthedocs.io/)
- [LibreOffice CLI](https://help.libreoffice.org/latest/en-US/text/shared/guide/start_parameters.html)
