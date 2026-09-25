# 发票模板技能

## 概述

该技能可从结构化数据和模板生成专业的PDF发票。创建具有公司品牌、明细列表、税务计算和付款详情的发票。

## 使用方法

1. 描述您想要完成的目标
2. 提供任何所需的输入数据或文件
3. 我将执行相应的操作

**示例提示：**
- "从订单数据生成发票"
- "创建周期性发票"
- "批量生成月度发票"
- "根据客户定制发票模板"

## 领域知识


### 发票数据结构

```python
invoice_data = {
    "invoice_number": "INV-2026-001",
    "date": "2026-01-30",
    "due_date": "2026-02-28",
    
    "from": {
        "name": "您的公司",
        "address": "123 商业街",
        "email": "billing@company.com"
    },
    
    "to": {
        "name": "客户名称",
        "address": "456 客户大道",
        "email": "client@example.com"
    },
    
    "items": [
        {"description": "咨询", "quantity": 10, "rate": 150.00},
        {"description": "开发", "quantity": 20, "rate": 100.00}
    ],
    
    "tax_rate": 0.08,
    "notes": "付款期限为30天"
}
```

### 使用ReportLab生成PDF

```python
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

def create_invoice(data: dict, output_path: str):
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter
    
    # 页眉
    c.setFont("Helvetica-Bold", 24)
    c.drawString(1*inch, height - 1*inch, "发票")
    
    # 发票详情
    c.setFont("Helvetica", 12)
    c.drawString(1*inch, height - 1.5*inch, f"发票编号: {data['invoice_number']}")
    c.drawString(1*inch, height - 1.75*inch, f"日期: {data['date']}")
    
    # 发票来源/接收方
    y = height - 2.5*inch
    c.drawString(1*inch, y, f"来源: {data['from']['name']}")
    c.drawString(4*inch, y, f"接收方: {data['to']['name']}")
    
    # 项目表格
    y = height - 4*inch
    c.setFont("Helvetica-Bold", 10)
    c.drawString(1*inch, y, "描述")
    c.drawString(4*inch, y, "数量")
    c.drawString(5*inch, y, "单价")
    c.drawString(6*inch, y, "金额")
    
    c.setFont("Helvetica", 10)
    subtotal = 0
    for item in data['items']:
        y -= 0.3*inch
        amount = item['quantity'] * item['rate']
        subtotal += amount
        c.drawString(1*inch, y, item['description'])
        c.drawString(4*inch, y, str(item['quantity']))
        c.drawString(5*inch, y, f"${item['rate']:.2f}")
        c.drawString(6*inch, y, f"${amount:.2f}")
    
    # 总计
    tax = subtotal * data['tax_rate']
    total = subtotal + tax
    
    y -= 0.5*inch
    c.drawString(5*inch, y, f"小计: ${subtotal:.2f}")
    y -= 0.25*inch
    c.drawString(5*inch, y, f"税额 ({data['tax_rate']*100}%): ${tax:.2f}")
    y -= 0.25*inch
    c.setFont("Helvetica-Bold", 12)
    c.drawString(5*inch, y, f"总计: ${total:.2f}")
    
    c.save()
    return output_path
```

### HTML模板方法

```python
from weasyprint import HTML
from jinja2 import Template

invoice_template = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial; margin: 40px; }
        .header { display: flex; justify-content: space-between; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
        .total { font-weight: bold; font-size: 18px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>发票</h1>
        <div>
            <p>发票编号: {{ invoice_number }}</p>
            <p>日期: {{ date }}</p>
        </div>
    </div>
    <table>
        <tr><th>描述</th><th>数量</th><th>单价</th><th>金额</th></tr>
        {% for item in items %}
        <tr>
            <td>{{ item.description }}</td>
            <td>{{ item.quantity }}</td>
            <td>${{ "%.2f"|format(item.rate) }}</td>
            <td>${{ "%.2f"|format(item.quantity * item.rate) }}</td>
        </tr>
        {% endfor %}
    </table>
    <p class="total">总计: ${{ "%.2f"|format(total) }}</p>
</body>
</html>
"""

def create_invoice_html(data: dict, output_path: str):
    template = Template(invoice_template)
    
    # 计算总计
    total = sum(i['quantity'] * i['rate'] for i in data['items'])
    total *= (1 + data.get('tax_rate', 0))
    data['total'] = total
    
    html = template.render(**data)
    HTML(string=html).write_pdf(output_path)
    return output_path
```


## 最佳实践

1. **生成前验证必填字段**
2. **使用模板保持品牌一致性**
3. **自动计算总计（不要信任输入数据）**
4. **包含付款说明和条款**

## 安装

```bash
# 安装所需依赖
pip install python-docx openpyxl python-pptx reportlab jinja2
```

## 资源

- [easy-invoice-pdf 仓库](https://github.com/nickmitchko/easy-invoice-pdf)
- [Claude Office Skills Hub](https://github.com/claude-office-skills/skills)
