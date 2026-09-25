# 报表生成技能

## 概述

该技能可自动生成专业的数据报表。使用图表、表格和数据分析洞察，创建仪表盘、KPI摘要和分析报告。

## 如何使用

1. 提供数据（CSV、Excel、JSON或描述数据）
2. 指定所需的报表类型
3. 我将生成格式化的报表并包含可视化内容

**示例提示：**
- "根据这些数据生成销售报表"
- "创建月度KPI仪表盘"
- "构建带图表的执行摘要"
- "生成数据分析报告"

## 领域知识

### 报表组件

```python
# 报表结构
report = {
    'title': '月度销售报表',
    'period': '2024年1月',
    'sections': [
        '执行摘要',
        'KPI仪表盘',
        '详细分析',
        '图表',
        '建议'
    ]
}
```

### 使用Python生成报表

```python
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def generate_report(data, output_path):
    # 加载数据
    df = pd.read_csv(data)
    
    # 计算KPI
    total_revenue = df['revenue'].sum()
    avg_order = df['revenue'].mean()
    growth = df['revenue'].pct_change().mean()
    
    # 创建图表
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    df.plot(kind='bar', ax=axes[0,0], title='按月收入')
    df.plot(kind='line', ax=axes[0,1], title='趋势')
    plt.savefig('charts.png')
    
    # 生成PDF
    # ... PDF生成代码
    
    return output_path
```

### HTML报表模板

```python
def generate_html_report(data, title):
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>{title}</title>
        <style>
            body {{ font-family: Arial; margin: 40px; }}
            .kpi {{ display: flex; gap: 20px; }}
            .kpi-card {{ background: #f5f5f5; padding: 20px; border-radius: 8px; }}
            .metric {{ font-size: 2em; font-weight: bold; color: #2563eb; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        </style>
    </head>
    <body>
        <h1>{title}</h1>
        <div class="kpi">
            <div class="kpi-card">
                <div class="metric">${data['revenue']:,.0f}</div>
                <div>总收入</div>
            </div>
            <div class="kpi-card">
                <div class="metric">{data['growth']:.1%}</div>
                <div>增长率</div>
            </div>
        </div>
        <!-- 更多内容 -->
    </body>
    </html>
    '''
    return html
```

## 示例：销售报表

```python
import pandas as pd
import matplotlib.pyplot as plt

def create_sales_report(csv_path, output_path):
    # 读取数据
    df = pd.read_csv(csv_path)
    
    # 计算指标
    metrics = {
        'total_revenue': df['amount'].sum(),
        'total_orders': len(df),
        'avg_order': df['amount'].mean(),
        'top_product': df.groupby('product')['amount'].sum().idxmax()
    }
    
    # 创建可视化
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 按产品收入
    df.groupby('product')['amount'].sum().plot(
        kind='bar', ax=axes[0,0], title='按产品收入'
    )
    
    # 月度趋势
    df.groupby('month')['amount'].sum().plot(
        kind='line', ax=axes[0,1], title='月度收入'
    )
    
    plt.tight_layout()
    plt.savefig(output_path.replace('.html', '_charts.png'))
    
    # 生成HTML报表
    html = generate_html_report(metrics, '销售报表')
    
    with open(output_path, 'w') as f:
        f.write(html)
    
    return output_path

create_sales_report('sales_data.csv', 'sales_report.html')
```

## 资源

- [Matplotlib](https://matplotlib.org/)
- [Plotly](https://plotly.com/)
- [ReportLab](https://www.reportlab.com/)
