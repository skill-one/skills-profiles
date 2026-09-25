# Excel 自动化技能

## 概述

该技能能够使用 **xlwings** 实现高级 Excel 自动化 - xlwings 是一个可以与 Excel 活动实例交互的库。与 openpyxl（仅文件）不同，xlwings 可以实时控制 Excel，执行 VBA，更新仪表板并自动化复杂的工作流程。

## 如何使用

1. 描述您需要的 Excel 自动化任务
2. 指定您是否需要实时 Excel 交互或文件处理
3. 我将生成 xlwings 代码并执行它

**示例提示：**
- "使用新数据更新此实时 Excel 仪表板"
- "运行此 VBA 宏并获取结果"
- "创建用于数据验证的 Excel 加载项"
- "使用实时图表自动化月度报告生成"

## 领域知识

### xlwings 与 openpyxl

| 功能 | xlwings | openpyxl |
|------|--------|---------|
| 需要 Excel | 是 | 否 |
| 实时交互 | 是 | 否 |
| VBA 执行 | 是 | 否 |
| 大文件速度 | 快 | 慢 |
| 服务器部署 | 有限 | 容易 |

### xlwings 基础知识

```python
import xlwings as xw

# 连接到活动 Excel 工作簿
wb = xw.Book.caller()  # 从 Excel 加载项
wb = xw.books.active   # 活动工作簿

# 打开特定文件
wb = xw.Book('路径/到/文件.xlsx')

# 创建新工作簿
wb = xw.Book()

# 获取工作表
sheet = wb.sheets['Sheet1']
sheet = wb.sheets[0]
```

### 处理范围

#### 读取和写入
```python
# 单个单元格
sheet['A1'].value = 'Hello'
value = sheet['A1'].value

# 范围
sheet['A1:C3'].value = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
data = sheet['A1:C3'].value  # 返回列表的列表

# 命名范围
sheet['MyRange'].value = '命名数据'

# 扩展范围（检测数据边界）
sheet['A1'].expand().value  # 所有连接的数据
sheet['A1'].expand('table').value  # 表格格式
```

#### 动态范围
```python
# 当前区域（类似于 Ctrl+Shift+End）
data = sheet['A1'].current_region.value

# 已用范围
used = sheet.used_range.value

# 带数据的最后一行
last_row = sheet['A1'].end('down').row

# 调整范围大小
rng = sheet['A1'].resize(10, 5)  # 10 行，5 列
```

### 格式化
```python
# 字体
sheet['A1'].font.bold = True
sheet['A1'].font.size = 14
sheet['A1'].font.color = (255, 0, 0)  # RGB 红色

# 填充
sheet['A1'].color = (255, 255, 0)  # 黄色背景

# 数字格式
sheet['B1'].number_format = '$#,##0.00'

# 列宽
sheet['A:A'].column_width = 20

# 行高
sheet['1:1'].row_height = 30

# 自动调整
sheet['A:D'].autofit()
```

### Excel 功能

#### 图表
```python
# 添加图表
chart = sheet.charts.add(left=100, top=100, width=400, height=250)
chart.set_source_data(sheet['A1:B10'])
chart.chart_type = 'column_clustered'
chart.name = '销售图表'

# 修改现有图表
chart = sheet.charts['销售图表']
chart.chart_type = 'line'
```

#### 表格
```python
# 创建 Excel 表格
rng = sheet['A1'].expand()
table = sheet.tables.add(source=rng, name='销售表')

# 刷新表格
table.refresh()

# 访问表格数据
table_data = table.data_body_range.value
```

#### 图片
```python
# 添加图片
sheet.pictures.add('logo.png', left=10, top=10, width=100, height=50)

# 从 matplotlib 更新图片
import matplotlib.pyplot as plt
fig, ax = plt.subplots()
ax.plot([1, 2, 3], [1, 4, 9])
sheet.pictures.add(fig, name='MyPlot', update=True)
```

### VBA 集成
```python
# 运行 VBA 宏
wb.macro('MacroName')()

# 带参数
wb.macro('MyMacro')('arg1', 'arg2')

# 获取返回值
result = wb.macro('CalculateTotal')(100, 200)

# 访问 VBA 模块
vb_code = wb.api.VBProject.VBComponents('Module1').CodeModule.Lines(1, 10)
```

### 用户定义函数 (UDF)
```python
# 定义一个 UDF（在 Python 文件中）
import xlwings as xw

@xw.func
def my_sum(x, y):
    """加两个数"""
    return x + y

@xw.func
@xw.arg('data', ndim=2)
def my_array_func(data):
    """处理数组数据"""
    import numpy as np
    return np.sum(data)

# 这些成为 Excel 函数：=my_sum(A1, B1)
```

### 应用控制
```python
# Excel 应用程序设置
app = xw.apps.active
app.screen_updating = False  # 加快速度
app.calculation = 'manual'   # 手动计算
app.display_alerts = False   # 抑制对话框

# 执行操作...

# 恢复
app.screen_updating = True
app.calculation = 'automatic'
app.display_alerts = True
```

## 最佳实践

1. **禁用屏幕更新**：用于批处理操作
2. **使用数组**：读取/写入整个范围，而不是逐个单元格
3. **手动计算**：在加载数据期间关闭自动计算
4. **关闭连接**：完成时正确关闭工作簿
5. **错误处理**：处理 Excel 未安装的情况

## 常见模式

### 性能优化
```python
import xlwings as xw

def batch_update(data, workbook_path):
    app = xw.App(visible=False)
    try:
        app.screen_updating = False
        app.calculation = 'manual'
        
        wb = app.books.open(workbook_path)
        sheet = wb.sheets['Data']
        
        # 一次性写入所有数据
        sheet['A1'].value = data
        
        app.calculation = 'automatic'
        wb.save()
    finally:
        wb.close()
        app.quit()
```

### 仪表板更新
```python
def update_dashboard(data_dict):
    wb = xw.books.active
    
    # 更新数据工作表
    data_sheet = wb.sheets['Data']
    for name, values in data_dict.items():
        data_sheet[name].value = values
    
    # 刷新所有图表
    dashboard = wb.sheets['Dashboard']
    for chart in dashboard.charts:
        chart.refresh()
    
    # 更新时间戳
    from datetime import datetime
    dashboard['A1'].value = f'最后更新: {datetime.now()}'
```

### 报告生成器
```python
def generate_monthly_report(month, data):
    template = xw.Book('template.xlsx')
    
    # 填充数据
    sheet = template.sheets['Report']
    sheet['B2'].value = month
    sheet['A5'].value = data
    
    # 运行计算
    template.app.calculate()
    
    # 导出为 PDF
    sheet.api.ExportAsFixedFormat(0, f'report_{month}.pdf')
    
    template.save(f'report_{month}.xlsx')
```

## 示例

### 示例 1：实时仪表板更新
```python
import xlwings as xw
import pandas as pd
from datetime import datetime

# 连接到正在运行的 Excel
wb = xw.books.active
dashboard = wb.sheets['Dashboard']
data_sheet = wb.sheets['Data']

# 获取新数据（模拟）
new_data = pd.DataFrame({
    '日期': pd.date_range('2024-01-01', periods=30),
    '销售额': [1000 + i*50 for i in range(30)],
    '成本': [600 + i*30 for i in range(30)]
})

# 更新数据工作表
data_sheet['A1'].value = new_data

# 计算利润
data_sheet['D1'].value = '利润'
data_sheet['D2'].value = '=B2-C2'
data_sheet['D2'].expand('down').value = data_sheet['D2'].formula

# 更新 KPI 在仪表板
dashboard['B2'].value = new_data['销售额'].sum()
dashboard['B3'].value = new_data['成本'].sum()
dashboard['B4'].value = new_data['销售额'].sum() - new_data['成本'].sum()
dashboard['A1'].value = f'更新: {datetime.now().strftime("%Y-%m-%d %H:%M")}'

# 刷新图表
for chart in dashboard.charts:
    chart.api.Refresh()

print("仪表板已更新！")
```

### 示例 2：批量处理多个文件
```python
import xlwings as xw
from pathlib import Path

def process_sales_files(folder_path, output_path):
    """将多个 Excel 文件汇总为一个汇总文件。"""
    
    app = xw.App(visible=False)
    app.screen_updating = False
    
    try:
        # 创建汇总工作簿
        summary_wb = xw.Book()
        summary_sheet = summary_wb.sheets[0]
        summary_sheet.name = '汇总'
        
        headers = ['文件', '总销售额', '总数量', '平均价格']
        summary_sheet['A1'].value = headers
        
        row = 2
        for file in Path(folder_path).glob('*.xlsx'):
            wb = app.books.open(str(file))
            data_sheet = wb.sheets['销售']
            
            # 提取汇总
            total_sales = data_sheet['B:B'].api.SpecialCells(11).Value  # xlCellTypeConstants
            total_units = data_sheet['C:C'].api.SpecialCells(11).Value
            
            # 计算并写入
            summary_sheet[f'A{row}'].value = file.name
            summary_sheet[f'B{row}'].value = sum(total_sales) if isinstance(total_sales, (list, tuple)) else total_sales
            summary_sheet[f'C{row}'].value = sum(total_units) if isinstance(total_units, (list, tuple)) else total_units
            summary_sheet[f'D{row}'].value = f'=B{row}/C{row}'
            
            wb.close()
            row += 1
        
        # 格式化汇总
        summary_sheet['A1:D1'].font.bold = True
        summary_sheet['B:D'].number_format = '$#,##0.00'
        summary_sheet['A:D'].autofit()
        
        summary_wb.save(output_path)
        
    finally:
        app.quit()
    
    print(f"汇总了 {row-2} 个文件到 {output_path}")

# 使用
process_sales_files('/路径/到/销售/', 'consolidated_sales.xlsx')
```

### 示例 3：具有 UDF 的 Excel 加载项
```python
# myudfs.py - 放在 xlwings 项目中

import xlwings as xw
import numpy as np

@xw.func
@xw.arg('data', pd.DataFrame, index=False, header=False)
@xw.ret(expand='table')
def GROWTH_RATE(data):
    """计算期间增长率"""
    values = data.iloc[:, 0].values
    growth = np.diff(values) / values[:-1] * 100
    return [['增长率']] + [[g] for g in growth]

@xw.func
@xw.arg('range1', np.array, ndim=2)
@xw.arg('range2', np.array, ndim=2)
def CORRELATION(range1, range2):
    """计算两个范围之间的相关性"""
    return np.corrcoef(range1.flatten(), range2.flatten())[0, 1]

@xw.func
def SENTIMENT(text):
    """基本情感分析（占位符）"""
    positive = ['good', 'great', 'excellent', 'amazing']
    negative = ['bad', 'poor', 'terrible', 'awful']
    
    text_lower = text.lower()
    pos_count = sum(word in text_lower for word in positive)
    neg_count = sum(word in text_lower for word in negative)
    
    if pos_count > neg_count:
        return '正面'
    elif neg_count > pos_count:
        return '负面'
    return '中性'
```

## 限制

- 需要安装 Excel
- macOS 上对某些功能支持有限
- 不适用于服务器端处理
- VBA 功能需要信任设置
- 性能随 Excel 版本变化而变化

## 安装

```bash
pip install xlwings

# 用于加载项功能
xlwings addin install
```

## 资源

- [xlwings 文档](https://docs.xlwings.org/)
- [GitHub 仓库](https://github.com/xlwings/xlwings)
- [UDF 教程](https://docs.xlwings.org/en/stable/udfs.html)
- [Excel VBA 参考](https://docs.microsoft.com/en-us/office/vba/api/overview/excel)
