# XLSX 操作技能

## 概述

这项技能能够使用 **openpyxl** 库以编程方式创建、编辑和操作 Microsoft Excel (.xlsx) 电子表格。无需手动编辑即可创建包含公式、格式、图表和数据验证的专业电子表格。

## 如何使用

1. 描述您想要创建或修改的电子表格
2. 提供数据、公式或格式要求
3. 我将生成 openpyxl 代码并执行它

**示例提示：**
- "创建一个包含月度跟踪的预算电子表格"
- "添加条件格式以突出显示超过阈值的值"
- "根据这些数据生成类似数据透视表的摘要"
- "创建一个包含图表和 KPI 的仪表板"

## 领域知识

### openpyxl 基础知识

```python
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, Fill, Border, Alignment
from openpyxl.chart import BarChart, Reference

# 创建新的电子表格
wb = Workbook()
ws = wb.active

# 或打开现有的
wb = load_workbook('existing.xlsx')
ws = wb.active
```

### 电子表格结构
```
Workbook
├── worksheets (工作表/标签页)
│   ├── cells (数据存储)
│   ├── rows/columns (格式化)
│   ├── merged_cells
│   └── charts
├── defined_names (命名范围)
└── styles (格式化模板)
```

### 单元格操作

#### 基本单元格操作
```python
# 通过单元格引用
ws['A1'] = '标题'
ws['B1'] = 42

# 通过行、列
ws.cell(row=1, column=3, value='数据')

# 多个单元格
ws['A1:C1'] = [['列1', '列2', '列3']]

# 追加行
ws.append(['行', '数据', '这里'])
```

#### 读取单元格
```python
# 单个单元格
value = ws['A1'].value

# 单元格范围
for row in ws['A1:C3']:
    for cell in row:
        print(cell.value)

# 迭代行
for row in ws.iter_rows(min_row=1, max_row=10, min_col=1, max_col=3):
    for cell in row:
        print(cell.value)
```

### 公式

```python
# 基本公式
ws['D1'] = '=SUM(A1:C1)'
ws['D2'] = '=AVERAGE(A2:C2)'
ws['E1'] = '=IF(D1>100,"高","低")'

# 命名范围
from openpyxl.workbook.defined_name import DefinedName
ref = "Sheet!$A$1:$C$10"
defn = DefinedName("SalesData", attr_text=ref)
wb.defined_names.add(defn)

# 使用命名范围
ws['F1'] = '=SUM(SalesData)'
```

### 格式化

#### 单元格样式
```python
from openpyxl.styles import Font, Fill, PatternFill, Border, Side, Alignment

# 字体
ws['A1'].font = Font(
    name='Arial',
    size=14,
    bold=True,
    italic=False,
    color='FF0000'  # 红色
)

# 填充 (背景)
ws['A1'].fill = PatternFill(
    start_color='FFFF00',  # 黄色
    end_color='FFFF00',
    fill_type='solid'
)

# 边框
thin_border = Border(
    left=Side(style='thin'),
    right=Side(style='thin'),
    top=Side(style='thin'),
    bottom=Side(style='thin')
)
ws['A1'].border = thin_border

# 对齐
ws['A1'].alignment = Alignment(
    horizontal='center',
    vertical='center',
    wrap_text=True
)
```

#### 数字格式
```python
# 货币
ws['B2'].number_format = '$#,##0.00'

# 百分比
ws['C2'].number_format = '0.00%'

# 日期
ws['D2'].number_format = 'YYYY-MM-DD'

# 自定义
ws['E2'].number_format = '#,##0.00 "单位"'
```

#### 条件格式化
```python
from openpyxl.formatting.rule import ColorScaleRule, CellIsRule, FormulaRule
from openpyxl.styles import PatternFill

# 颜色刻度 (热图)
color_scale = ColorScaleRule(
    start_type='min', start_color='FF0000',
    end_type='max', end_color='00FF00'
)
ws.conditional_formatting.add('A1:A10', color_scale)

# 单元格值规则
red_fill = PatternFill(start_color='FFCCCC', end_color='FFCCCC', fill_type='solid')
rule = CellIsRule(operator='greaterThan', formula=['100'], fill=red_fill)
ws.conditional_formatting.add('B1:B10', rule)
```

### 图表

```python
from openpyxl.chart import BarChart, LineChart, PieChart, Reference

# 准备数据
data = Reference(ws, min_col=2, min_row=1, max_col=3, max_row=5)
categories = Reference(ws, min_col=1, min_row=2, max_row=5)

# 条形图
chart = BarChart()
chart.type = "col"  # 或 "bar" 用于水平条形图
chart.title = "按区域销售"
chart.add_data(data, titles_from_data=True)
chart.set_categories(categories)
chart.shape = 4
ws.add_chart(chart, "E1")

# 折线图
line = LineChart()
line.title = "趋势分析"
line.add_data(data, titles_from_data=True)
line.set_categories(categories)
ws.add_chart(line, "E15")

# 饼图
pie = PieChart()
pie.add_data(data, titles_from_data=True)
pie.set_categories(categories)
ws.add_chart(pie, "M1")
```

### 数据验证

```python
from openpyxl.worksheet.datavalidation import DataValidation

# 下拉列表
dv = DataValidation(
    type="list",
    formula1='"选项1,选项2,选项3"',
    allow_blank=True
)
dv.error = "请从列表中选择"
dv.errorTitle = "无效输入"
ws.add_data_validation(dv)
dv.add('A1:A100')

# 数字范围
dv_num = DataValidation(
    type="whole",
    operator="between",
    formula1="1",
    formula2="100"
)
ws.add_data_validation(dv_num)
dv_num.add('B1:B100')
```

### 工作表操作

```python
# 创建新工作表
ws2 = wb.create_sheet("数据")
ws3 = wb.create_sheet("摘要", 0)  # 在位置 0

# 重命名
ws.title = "主要报告"

# 删除
del wb["Sheet2"]

# 复制
source = wb["模板"]
target = wb.copy_worksheet(source)
```

### 行/列操作

```python
# 设置列宽
ws.column_dimensions['A'].width = 20

# 设置行高
ws.row_dimensions[1].height = 30

# 隐藏列
ws.column_dimensions['C'].hidden = True

# 冻结窗格
ws.freeze_panes = 'B2'  # 冻结行 1 和列 A

# 自动筛选
ws.auto_filter.ref = "A1:D100"
```

## 最佳实践

1. **使用模板**：从 .xlsx 模板开始以进行复杂的格式化
2. **批量操作**：最小化逐个单元格的操作以提高速度
3. **命名范围**：使用定义名称以使公式更清晰
4. **数据验证**：添加验证以防止输入错误
5. **增量保存**：对于大文件，定期保存

## 常见模式

### 数据导入

```python
def import_csv_to_xlsx(csv_path, xlsx_path):
    import csv
    wb = Workbook()
    ws = wb.active
    
    with open(csv_path) as f:
        reader = csv.reader(f)
        for row in reader:
            ws.append(row)
    
    wb.save(xlsx_path)
```

### 报告模板

```python
def create_monthly_report(data, output_path):
    wb = Workbook()
    ws = wb.active
    ws.title = "月度报告"
    
    # 标题
    headers = ['日期', '收入', '支出', '利润']
    ws.append(headers)
    
    # 样式标题
    for col in range(1, 5):
        cell = ws.cell(1, col)
        cell.font = Font(bold=True)
        cell.fill = PatternFill('solid', fgColor='4472C4')
        cell.font = Font(bold=True, color='FFFFFF')
    
    # 数据
    for row in data:
        ws.append(row)
    
    # 添加总计
    last_row = len(data) + 1
    ws.cell(last_row + 1, 1, '总计')
    ws.cell(last_row + 1, 2, f'=SUM(B2:B{last_row})')
    ws.cell(last_row + 1, 3, f'=SUM(C2:C{last_row})')
    ws.cell(last_row + 1, 4, f'=SUM(D2:D{last_row})')
    
    wb.save(output_path)
```

## 示例

### 示例 1：预算跟踪器

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

wb = Workbook()
ws = wb.active
ws.title = "预算 2024"

# 标题
months = ['类别', '1月', '2月', '3月', '第一季度总计']
ws.append(months)

# 类别和数据
budget_data = [
    ['工资', 5000, 5000, 5000],
    ['租金', -1500, -1500, -1500],
    ['水电费', -200, -180, -220],
    ['食品', -400, -450, -380],
    ['交通', -150, -160, -140],
    ['娱乐', -200, -250, -200],
]

for row in budget_data:
    ws.append(row + [f'=SUM(B{ws.max_row + 1}:D{ws.max_row + 1})'])

# 总计行
ws.append(['总计', 
    f'=SUM(B2:B{ws.max_row})',
    f'=SUM(C2:C{ws.max_row})',
    f'=SUM(D2:D{ws.max_row})',
    f'=SUM(E2:E{ws.max_row})'
])

# 格式化
header_fill = PatternFill('solid', fgColor='366092')
header_font = Font(bold=True, color='FFFFFF')

for cell in ws[1]:
    cell.fill = header_fill
    cell.font = header_font
    cell.alignment = Alignment(horizontal='center')

# 货币格式
for row in ws.iter_rows(min_row=2, min_col=2, max_col=5):
    for cell in row:
        cell.number_format = '$#,##0.00'

# 列宽
ws.column_dimensions['A'].width = 15
for col in range(2, 6):
    ws.column_dimensions[get_column_letter(col)].width = 12

wb.save('budget_2024.xlsx')
```

### 示例 2：销售仪表板

```python
from openpyxl import Workbook
from openpyxl.chart import BarChart, PieChart, Reference
from openpyxl.styles import Font, PatternFill

wb = Workbook()
ws = wb.active
ws.title = "销售仪表板"

# 数据
ws.append(['区域', '第一季度', '第二季度', '第三季度', '第四季度'])
data = [
    ['北部', 150000, 165000, 180000, 195000],
    ['南部', 120000, 125000, 140000, 155000],
    ['东部', 180000, 190000, 210000, 225000],
    ['西部', 95000, 110000, 125000, 140000],
]
for row in data:
    ws.append(row)

# 条形图
data_ref = Reference(ws, min_col=2, min_row=1, max_col=5, max_row=5)
cats_ref = Reference(ws, min_col=1, min_row=2, max_row=5)

bar = BarChart()
bar.type = "col"
bar.title = "按季度区域销售"
bar.add_data(data_ref, titles_from_data=True)
bar.set_categories(cats_ref)
bar.height = 10
bar.width = 15
ws.add_chart(bar, "A8")

# 饼图 - 第四季度细分
pie_data = Reference(ws, min_col=5, min_row=1, max_row=5)
pie = PieChart()
pie.title = "第四季度市场份额"
pie.add_data(pie_data, titles_from_data=True)
pie.set_categories(cats_ref)
ws.add_chart(pie, "J8")

wb.save('sales_dashboard.xlsx')
```

## 限制

- 无法执行 VBA 宏
- 复杂的数据透视表不支持
- 支持有限的火花线
- 不支持外部数据连接
- 一些高级图表类型不可用

## 安装

```bash
pip install openpyxl
```

## 资源

- [openpyxl 文档](https://openpyxl.readthedocs.io/)
- [GitHub 仓库](https://github.com/theorchard/openpyxl)
- [样式操作](https://openpyxl.readthedocs.io/en/stable/styles.html)
