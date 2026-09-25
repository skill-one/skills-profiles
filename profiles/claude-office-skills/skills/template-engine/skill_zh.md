# 模板引擎技能

## 概述

该技能支持基于模板的文档生成 - 定义包含占位符的模板，然后自动用数据填充它们。支持 Word、Excel、PowerPoint 等多种文档格式。

## 使用方法

1. 描述您希望完成的目标
2. 提供所需的输入数据或文件
3. 我将执行相应的操作

**示例提示：**
- "批量合并邮件/合同"
- "根据数据生成个性化报告"
- "从模板创建证书"
- "用用户数据自动填写表单"

## 领域知识


### 模板语法（基于 Jinja2）

```
{{ variable }}           - 简单替换
{% for item in list %}   - 循环
{% if condition %}       - 条件判断
{{ date | format_date }} - 过滤器
```

### Word 模板示例

```python
from docxtpl import DocxTemplate

# 创建包含占位符的模板：
# 尊敬的 {{ name }},
# 感谢您的订单 #{{ order_id }}...

def fill_template(template_path: str, data: dict, output_path: str):
    doc = DocxTemplate(template_path)
    doc.render(data)
    doc.save(output_path)
    return output_path

# 使用示例
fill_template(
    "templates/order_confirmation.docx",
    {
        "name": "John Smith",
        "order_id": "ORD-12345",
        "items": [
            {"name": "产品A", "qty": 2, "price": 29.99},
            {"name": "产品B", "qty": 1, "price": 49.99}
        ],
        "total": 109.97
    },
    "output/confirmation_john.docx"
)
```

### Excel 模板

```python
from openpyxl import load_workbook
import re

def fill_excel_template(template_path: str, data: dict, output_path: str):
    wb = load_workbook(template_path)
    ws = wb.active
    
    # 查找并替换类似 {{name}} 的占位符
    for row in ws.iter_rows():
        for cell in row:
            if cell.value and isinstance(cell.value, str):
                for key, value in data.items():
                    placeholder = "{{" + key + "}}"
                    if placeholder in cell.value:
                        cell.value = cell.value.replace(placeholder, str(value))
    
    wb.save(output_path)
    return output_path
```

### 批量生成（邮件合并）

```python
import csv
from pathlib import Path

def mail_merge(template_path: str, data_csv: str, output_dir: str):
    """为 CSV 中的每一行生成文档。"""
    
    Path(output_dir).mkdir(exist_ok=True)
    
    with open(data_csv) as f:
        reader = csv.DictReader(f)
        
        for i, row in enumerate(reader):
            output_path = f"{output_dir}/document_{i+1}.docx"
            fill_template(template_path, row, output_path)
            print(f"已生成: {output_path}")

# 使用 contacts.csv 示例：
# name,email,company
# John,john@example.com,Acme
# Jane,jane@example.com,Corp

mail_merge(
    "templates/welcome_letter.docx",
    "data/contacts.csv",
    "output/letters"
)
```

### 高级：条件内容

```python
from docxtpl import DocxTemplate

# 包含条件判断的模板：
# {% if vip %}
# 感谢您成为 VIP 会员！
# {% else %}
# 感谢您的购买。
# {% endif %}

doc = DocxTemplate("template.docx")
doc.render({
    "name": "John",
    "vip": True,
    "discount": 20
})
doc.save("output.docx")
```

## 最佳实践

1. **使用清晰的占位符命名（{{client_name}}）**
2. **在渲染前验证数据**
3. **优雅处理缺失数据**
4. **对模板进行版本控制**

## 安装

```bash
# 安装所需依赖
pip install python-docx openpyxl python-pptx reportlab jinja2
```

## 资源

- [docxtpl / yumdocs 仓库](https://github.com/elapouya/python-docxtpl)
- [Claude Office 技能中心](https://github.com/claude-office-skills/skills)
