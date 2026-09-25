# 表格提取技能

## 概述

该技能能够使用 **camelot** 精确地从 PDF 文档中提取表格 - PDF 表格提取的黄金标准。处理具有合并单元格、无边框表格和多页布局的复杂表格，具有高精度。

## 使用方法

1. 提供包含表格的 PDF 文件
2. 可选地指定页面或表格检测方法
3. 我将表格提取为 pandas DataFrame

**示例提示：**
- "从该 PDF 中提取所有表格"
- "获取该报告第 5 页的表格"
- "从该文档中提取无边框表格"
- "将 PDF 表格转换为 Excel 格式"

## 领域知识

### camelot 基础知识

```python
import camelot

# 从 PDF 中提取表格
tables = camelot.read_pdf('document.pdf')

# 访问结果
print(f"找到 {len(tables)} 个表格")

# 获取第一个表格作为 DataFrame
df = tables[0].df
print(df)
```

### 提取方法

| 方法 | 用例 | 描述 |
|------|------|------|
| `lattice` | 带边框的表格 | 通过线条/边框检测表格 |
| `stream` | 无边框表格 | 使用文本位置 |

```python
# Lattice 方法（默认）- 用于带可见边框的表格
tables = camelot.read_pdf('document.pdf', flavor='lattice')

# Stream 方法 - 用于无边框表格
tables = camelot.read_pdf('document.pdf', flavor='stream')
```

### 页面选择

```python
# 单页
tables = camelot.read_pdf('document.pdf', pages='1')

# 多页
tables = camelot.read_pdf('document.pdf', pages='1,3,5')

# 页面范围
tables = camelot.read_pdf('document.pdf', pages='1-5')

# 所有页面
tables = camelot.read_pdf('document.pdf', pages='all')
```

### 高级选项

#### Lattice 选项
```python
tables = camelot.read_pdf(
    'document.pdf',
    flavor='lattice',
    line_scale=40,              # 线条检测灵敏度
    copy_text=['h', 'v'],       # 复制跨越合并单元格的文本
    shift_text=['l', 't'],      # 移动文本对齐
    split_text=True,            # 在换行处分割文本
    flag_size=True,             # 标记超/下标
    strip_text='\n',            # 要删除的字符
    process_background=False,   # 处理背景线条
)
```

#### Stream 选项
```python
tables = camelot.read_pdf(
    'document.pdf',
    flavor='stream',
    edge_tol=500,               # 边缘容差
    row_tol=10,                 # 行容差
    column_tol=0,               # 列容差
    strip_text='\n',            # 要删除的字符
)
```

### 表格区域指定

```python
# 从特定区域提取（x1, y1, x2, y2）
# 坐标从左下角开始，以 PDF 点为单位（72 点 = 1 英寸）
tables = camelot.read_pdf(
    'document.pdf',
    table_areas=['72,720,540,400'],  # 一个区域
)

# 多个区域
tables = camelot.read_pdf(
    'document.pdf',
    table_areas=['72,720,540,400', '72,380,540,200'],
)
```

### 列指定

```python
# 手动指定列位置（用于 stream 方法）
tables = camelot.read_pdf(
    'document.pdf',
    flavor='stream',
    columns=['100,200,300,400'],  # 列分隔符的 X 位置
)
```

### 处理结果

```python
import camelot

tables = camelot.read_pdf('document.pdf')

for i, table in enumerate(tables):
    # 访问 DataFrame
    df = table.df
    
    # 表格元数据
    print(f"表格 {i+1}:")
    print(f"  页面: {table.page}")
    print(f"  准确率: {table.accuracy}")
    print(f"  空白: {table.whitespace}")
    print(f"  顺序: {table.order}")
    print(f"  形状: {df.shape}")
    
    # 解析报告
    report = table.parsing_report
    print(f"  报告: {report}")
```

### 导出选项

```python
import camelot

tables = camelot.read_pdf('document.pdf')

# 导出为 CSV
tables[0].to_csv('table.csv')

# 导出为 Excel
tables[0].to_excel('table.xlsx')

# 导出为 JSON
tables[0].to_json('table.json')

# 导出为 HTML
tables[0].to_html('table.html')

# 导出所有表格
for i, table in enumerate(tables):
    table.to_excel(f'table_{i+1}.xlsx')
```

### 可视化调试

```python
import camelot

# 启用可视化调试
tables = camelot.read_pdf('document.pdf')

# 绘制检测到的表格区域
camelot.plot(tables[0], kind='contour').show()

# 绘制表格上的文本
camelot.plot(tables[0], kind='text').show()

# 绘制检测到的线条（仅 lattice）
camelot.plot(tables[0], kind='joint').show()
camelot.plot(tables[0], kind='line').show()

# 保存图表
fig = camelot.plot(tables[0])
fig.savefig('debug.png')
```

### 处理多页表格

```python
import camelot
import pandas as pd

def extract_multipage_table(pdf_path, pages='all'):
    """提取并组合跨越多页的表格。"""
    
    tables = camelot.read_pdf(pdf_path, pages=pages)
    
    # 按相似结构（列）分组表格
    table_groups = {}
    
    for table in tables:
        cols = tuple(table.df.columns)
        if cols not in table_groups:
            table_groups[cols] = []
        table_groups[cols].append(table.df)
    
    # 合并相似表格
    combined = []
    for cols, dfs in table_groups.items():
        if len(dfs) > 1:
            # 合并并去重标题行
            combined_df = pd.concat(dfs, ignore_index=True)
            combined.append(combined_df)
        else:
            combined.append(dfs[0])
    
    return combined
```

## 最佳实践

1. **尝试两种方法**：Lattice 用于带边框的，stream 用于无边框的
2. **检查准确率分数**：通常 90% 以上就是好的
3. **使用可视化调试**：了解提取结果
4. **指定区域**：对于具有多种表格类型的 PDF
5. **处理标题**：第一行通常需要特殊处理

## 常见模式

### 批量表格提取
```python
import camelot
from pathlib import Path
import pandas as pd

def batch_extract_tables(input_dir, output_dir):
    """从目录中的所有 PDF 中提取表格。"""
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    results = []
    
    for pdf_file in input_path.glob('*.pdf'):
        try:
            tables = camelot.read_pdf(str(pdf_file), pages='all')
            
            for i, table in enumerate(tables):
                # 跳过低准确率的表格
                if table.accuracy < 80:
                    continue
                
                output_file = output_path / f"{pdf_file.stem}_table_{i+1}.xlsx"
                table.to_excel(str(output_file))
                
                results.append({
                    'source': str(pdf_file),
                    'table': i + 1,
                    'page': table.page,
                    'accuracy': table.accuracy,
                    'output': str(output_file)
                })
        
        except Exception as e:
            results.append({
                'source': str(pdf_file),
                'error': str(e)
            })
    
    return results
```

### 自动检测表格方法
```python
import camelot

def smart_extract_tables(pdf_path, pages='1'):
    """尝试两种方法并返回最佳结果。"""
    
    # 首先尝试 lattice
    lattice_tables = camelot.read_pdf(pdf_path, pages=pages, flavor='lattice')
    
    # 然后尝试 stream
    stream_tables = camelot.read_pdf(pdf_path, pages=pages, flavor='stream')
    
    # 比较并返回最佳结果
    results = []
    
    if lattice_tables and lattice_tables[0].accuracy > 70:
        results.extend(lattice_tables)
    elif stream_tables:
        results.extend(stream_tables)
    
    return results
```

## 示例

### 示例 1：财务报表提取
```python
import camelot
import pandas as pd

def extract_financial_tables(pdf_path):
    """从年报中提取财务表格。"""
    
    # 提取所有表格
    tables = camelot.read_pdf(pdf_path, pages='all', flavor='lattice')
    
    financial_data = {
        'income_statement': None,
        'balance_sheet': None,
        'cash_flow': None,
        'other_tables': []
    }
    
    for table in tables:
        df = table.df
        text = df.to_string().lower()
        
        # 识别表格类型
        if 'revenue' in text or 'sales' in text:
            if 'operating income' in text or 'net income' in text:
                financial_data['income_statement'] = df
        elif 'asset' in text and 'liabilities' in text:
            financial_data['balance_sheet'] = df
        elif 'cash flow' in text or 'operating activities' in text:
            financial_data['cash_flow'] = df
        else:
            financial_data['other_tables'].append({
                'page': table.page,
                'data': df,
                'accuracy': table.accuracy
            })
    
    return financial_data

financials = extract_financial_tables('annual_report.pdf')
if financials['income_statement'] is not None:
    print("Income Statement found:")
    print(financials['income_statement'])
```

### 示例 2：科学数据提取
```python
import camelot
import pandas as pd

def extract_research_data(pdf_path, pages='all'):
    """从研究论文中提取数据表格。"""
    
    # 尝试 lattice 用于带边框的表格
    tables = camelot.read_pdf(pdf_path, pages=pages, flavor='lattice')
    
    if not tables or all(t.accuracy < 70 for t in tables):
        # 如果 lattice 不成功，则使用 stream 降级
        tables = camelot.read_pdf(pdf_path, pages=pages, flavor='stream')
    
    extracted_data = []
    
    for table in tables:
        df = table.df
        
        # 清理 DataFrame
        # 如果第一行看起来像标题行，则将其设置为标题
        if not df.iloc[0].str.contains(r'\d').any():
            df.columns = df.iloc[0]
            df = df[1:]
            df = df.reset_index(drop=True)
        
        extracted_data.append({
            'page': table.page,
            'accuracy': table.accuracy,
            'data': df
        })
    
    return extracted_data

data = extract_research_data('research_paper.pdf')
for i, item in enumerate(data):
    print(f"表格 {i+1}（页面 {item['page']}，准确率: {item['accuracy']}%）：")
    print(item['data'].head())
```

### 示例 3：发票行项目
```python
import camelot

def extract_invoice_items(pdf_path):
    """从发票中提取行项目。"""
    
    # 通常发票具有带边框的表格
    tables = camelot.read_pdf(pdf_path, flavor='lattice')
    
    line_items = []
    
    for table in tables:
        df = table.df
        
        # 查找具有典型发票列的表格
        header_text = ' '.join(df.iloc[0].astype(str)).lower()
        
        if any(term in header_text for term in ['quantity', 'qty', 'amount', 'price', 'description']):
            # 这看起来像是一个行项目表格
            df.columns = df.iloc[0]
            df = df[1:]
            
            for _, row in df.iterrows():
                item = {}
                for col in df.columns:
                    col_lower = str(col).lower()
                    value = row[col]
                    
                    if 'desc' in col_lower or 'item' in col_lower:
                        item['description'] = value
                    elif 'qty' in col_lower or 'quantity' in col_lower:
                        item['quantity'] = value
                    elif 'price' in col_lower or 'rate' in col_lower:
                        item['unit_price'] = value
                    elif 'amount' in col_lower or 'total' in col_lower:
                        item['amount'] = value
                
                if item:
                    line_items.append(item)
    
    return line_items

items = extract_invoice_items('invoice.pdf')
for item in items:
    print(item)
```

### 示例 4：表格比较
```python
import camelot
import pandas as pd

def compare_pdf_tables(pdf1_path, pdf2_path):
    """比较两个 PDF 版本之间的表格。"""
    
    tables1 = camelot.read_pdf(pdf1_path)
    tables2 = camelot.read_pdf(pdf2_path)
    
    comparisons = []
    
    # 通过形状和位置匹配表格
    for t1 in tables1:
        best_match = None
        best_score = 0
        
        for t2 in tables2:
            if t1.df.shape == t2.df.shape:
                # 计算相似度
                try:
                    similarity = (t1.df == t2.df).mean().mean()
                    if similarity > best_score:
                        best_score = similarity
                        best_match = t2
                except:
                    pass
        
        if best_match:
            comparisons.append({
                'page1': t1.page,
                'page2': best_match.page,
                'similarity': best_score,
                'identical': best_score == 1.0,
                'diff': pd.DataFrame(t1.df != best_match.df)
            })
    
    return comparisons

comparison = compare_pdf_tables('report_v1.pdf', 'report_v2.pdf')
```

## 限制

- 不支持加密 PDF
- 基于图像的 PDF 需要预先进行 OCR 处理
- 非常复杂的合并单元格可能需要调整
- 旋转表格需要预先处理
- 大型 PDF 可能需要逐页处理

## 安装

```bash
pip install camelot-py[cv]

# 额外依赖
# macOS
brew install ghostscript tcl-tk

# Ubuntu
apt-get install ghostscript python3-tk
```

## 资源

- [camelot 文档](https://camelot-py.readthedocs.io/)
- [GitHub 仓库](https://github.com/camelot-dev/camelot)
- [与其他工具的比较](https://camelot-py.readthedocs.io/en/master/user/intro.html#why-camelot)
