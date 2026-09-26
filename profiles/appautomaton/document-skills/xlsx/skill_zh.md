# 输出要求

## 所有 Excel 文件

### 无公式错误
- 每个Excel模型必须交付无公式错误（#REF!、#DIV/0!、#VALUE!、#N/A、#NAME?）

### 保留现有模板（在更新模板时）
- 修改文件时，研究和精确匹配现有格式、样式和约定
- 不要对具有既定模式的文件强加标准化格式
- 现有模板约定始终优先于这些指南

## 财务模型

### 颜色编码标准
除非用户另有说明或现有模板

#### 行业标准颜色约定
- **蓝色文本（RGB：0,0,255）**：硬编码输入，以及用户为情景更改的数字
- **黑色文本（RGB：0,0,0）**：所有公式和计算
- **绿色文本（RGB：0,128,0）**：从同一工作簿内其他工作表拉取的链接
- **红色文本（RGB：255,0,0）**：指向其他文件的外部链接
- **黄色背景（RGB：255,255,0）**：需要关注的假设或需要更新的单元格

### 数字格式标准

#### 必须遵循的格式规则
- **年份**：格式化为文本字符串（例如，"2024"而不是"2,024"）
- **货币**：使用$#,##0格式；始终在标题中指定单位（"收入($mm)"）
- **零**：使用数字格式使所有零为"-"，包括百分比（例如，"$#,##0;($#,##0);-"）
- **百分比**：默认为0.0%格式（一位小数）
- **倍数**：格式化为0.0x，用于估值倍数（EV/EBITDA、P/E）
- **负数**：使用括号（123）而不是减号-123

### 公式构建规则

#### 假设位置
- 将所有假设（增长率、利润率、倍数等）放在单独的假设单元格中
- 在公式中使用单元格引用而不是硬编码值
- 示例：使用=B5*(1+$B$6)而不是=B5*1.05

#### 防止公式错误
- 验证所有单元格引用是否正确
- 检查范围中的偏移量错误
- 确保所有预测期间公式一致
- 使用边缘情况测试（零值、负数）
- 验证没有意外的循环引用

#### 硬编码的文档要求
- 注释或单元格旁边（如果位于表格末尾）。格式："来源：[系统/文档]、[日期]、[具体引用]、[URL（如果适用）]"
- 示例：
  - "来源：公司10-K，2024财年，第45页，收入说明，[SEC EDGAR URL]"
  - "来源：公司10-Q，2025年第二季度，第99.1号附件，[SEC EDGAR URL]"
  - "来源：彭博终端，2025年8月15日，AAPL美国股票"
  - "来源：FactSet，2025年8月20日，一致估计屏幕"

# XLSX 创建、编辑和分析

## 概述

用户可以要求您创建、编辑或分析.xlsx文件的内容。您有不同工具和工作流程可用于不同任务。

## 重要要求

**需要LibreOffice进行公式重新计算**：`recalc.py`脚本以无头方式驱动LibreOffice（`soffice`），并在首次运行时通过向LibreOffice用户配置文件写入一个小型重新计算宏来自动配置它。使用`brew install --cask libreoffice`或`apt-get install libreoffice`进行安装。

**可选，仅限macOS — coreutils**（`brew install coreutils`）：提供`gtimeout`，以便重新计算有时间限制；如果没有它，`recalc.py`会在标准错误上发出警告并运行而没有超时。

**Python包**（openpyxl、pandas、matplotlib）通过`uv run`自动解析——在每个脚本PEP 723头部中声明它们。

## 读取和分析数据

### 使用pandas进行数据分析
对于数据分析、可视化和基本操作，使用**pandas**，它提供强大的数据操作功能：

```python
import pandas as pd

# 读取Excel
df = pd.read_excel('file.xlsx')  # 默认：第一个工作表
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)  # 所有工作表作为字典

# 分析
df.head()      # 预览数据
df.info()      # 列信息
df.describe()  # 统计

# 写入Excel
df.to_excel('output.xlsx', index=False)
```

## Excel文件工作流程

## 关键：使用公式，而不是硬编码值

**始终使用Excel公式而不是在Python中计算值并硬编码它们**。这确保了电子表格保持动态和可更新。

### ❌ 错误 - 硬编码计算值
```python
# 坏：在Python中计算并硬编码结果
total = df['Sales'].sum()
sheet['B10'] = total  # 硬编码5000

# 坏：在Python中计算增长率
growth = (df.iloc[-1]['Revenue'] - df.iloc[0]['Revenue']) / df.iloc[0]['Revenue']
sheet['C5'] = growth  # 硬编码0.15

# 坏：Python计算平均值
avg = sum(values) / len(values)
sheet['D20'] = avg  # 硬编码42.5
```

### ✅ 正确 - 使用Excel公式
```python
# 好：让Excel计算总和
sheet['B10'] = '=SUM(B2:B9)'

# 好：增长率作为Excel公式
sheet['C5'] = '=(C4-C2)/C2'

# 好：使用Excel函数计算平均值
sheet['D20'] = '=AVERAGE(D2:D19)'
```

这适用于所有计算——总计、百分比、比率、差异等。电子表格应该能够在源数据更改时重新计算。

## 常见工作流程
1. **选择工具**：pandas用于数据，openpyxl用于公式/格式化
2. **创建/加载**：创建新工作簿或加载现有文件
3. **修改**：添加/编辑数据、公式和格式
4. **保存**：写入文件
5. **重新计算公式（如果使用公式则必须）**：使用recalc.py脚本
   ```bash
   uv run recalc.py output.xlsx
   ```
6. **验证并修复任何错误**：
   - 脚本返回包含错误详细信息的JSON
   - 如果`status`是`errors_found`，请检查`error_summary`以获取特定错误类型和位置
   - 修复已识别的错误并重新计算
   - 常见错误要修复：
     - `#REF!`：无效的单元格引用
     - `#DIV/0!`：除以零
     - `#VALUE!`：公式中数据类型错误
     - `#NAME?`：未识别的公式名称

### 创建新的Excel文件

```python
# 使用openpyxl进行公式和格式化
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

wb = Workbook()
sheet = wb.active

# 添加数据
sheet['A1'] = 'Hello'
sheet['B1'] = 'World'
sheet.append(['Row', 'of', 'data'])

# 添加公式
sheet['B2'] = '=SUM(A1:A10)'

# 格式化
sheet['A1'].font = Font(bold=True, color='FF0000')
sheet['A1'].fill = PatternFill('solid', start_color='FFFF00')
sheet['A1'].alignment = Alignment(horizontal='center')

# 列宽
sheet.column_dimensions['A'].width = 20

wb.save('output.xlsx')
```

### 编辑现有的Excel文件

```python
# 使用openpyxl保留公式和格式
from openpyxl import load_workbook

# 加载现有文件
wb = load_workbook('existing.xlsx')
sheet = wb.active  # 或wb['SheetName']用于特定工作表

# 处理多个工作表
for sheet_name in wb.sheetnames:
    sheet = wb[sheet_name]
    print(f"工作表：{sheet_name}")

# 修改单元格
sheet['A1'] = '新值'
sheet.insert_rows(2)  # 在位置2插入行
sheet.delete_cols(3)  # 删除第3列

# 添加新工作表
new_sheet = wb.create_sheet('NewSheet')
new_sheet['A1'] = '数据'

wb.save('modified.xlsx')
```

## 重新计算公式

openpyxl创建或修改的Excel文件包含公式作为字符串，而不是计算值。使用提供的`recalc.py`脚本重新计算公式：

```bash
uv run recalc.py <excel_file> [timeout_seconds]
```

示例：
```bash
uv run recalc.py output.xlsx 30
```

该脚本：
- 在首次运行时自动设置LibreOffice宏
- 重新计算所有工作表中的所有公式
- 扫描所有单元格以查找Excel错误（#REF!、#DIV/0!等）
- 返回包含详细错误位置和计数的JSON
- 适用于Linux和macOS

## 公式验证清单

快速检查以确保公式工作正常：

### 基本验证
- [ ] **测试2-3个样本引用**：在构建完整模型之前验证它们是否拉取正确的值
- [ ] **列映射**：确认Excel列匹配（例如，列64 = BL，而不是BK）
- [ ] **行偏移**：记住Excel行是1索引的（DataFrame行5 = Excel行6）

### 常见陷阱
- [ ] **NaN处理**：使用`pd.notna()`检查空值
- [ ] **最右侧列**：FY数据通常在列50以上
- [ ] **多个匹配**：搜索所有出现的位置，而不仅仅是第一个
- [ ] **除以零**：在公式中使用`/`之前检查分母（#DIV/0!）
- [ ] **错误引用**：验证所有单元格引用是否指向预期单元格（#REF!）
- [ ] **跨工作表引用**：使用正确格式（Sheet1!A1）链接工作表

### 公式测试策略
- [ ] **从小处着手**：在应用广泛之前，在2-3个单元格上测试公式
- [ ] **验证依赖项**：检查公式中引用的所有单元格是否存在
- [ ] **测试边缘情况**：包括零、负数和非常大的值

### 解释recalc.py输出
脚本返回包含错误详细信息的JSON：
```json
{
  "status": "success",           // 或 "errors_found"
  "total_errors": 0,              // 错误总数
  "total_formulas": 42,           // 文件中的公式数量
  "error_summary": {              // 仅在发现错误时存在
    "#REF!": {
      "count": 2,
      "locations": ["Sheet1!B5", "Sheet1!C10"]
    }
  }
}
```

## 最佳实践

### 库选择
- **pandas**：最适合数据分析、批量操作和简单数据导出
- **openpyxl**：最适合复杂格式、公式和Excel特定功能

### 使用openpyxl
- 单元格索引是1-based（行=1，列=1引用A1单元格）
- 使用`data_only=True`读取计算值：`load_workbook('file.xlsx', data_only=True)`
- **警告**：如果使用`data_only=True`打开并保存，公式将替换为值并永久丢失
- 对于大文件：使用`read_only=True`读取或`write_only=True`写入
- 公式被保留但未计算——使用recalc.py更新值

### 使用pandas
- 指定数据类型以避免推断问题：`pd.read_excel('file.xlsx', dtype={'id': str})`
- 对于大文件，读取特定列：`pd.read_excel('file.xlsx', usecols=['A', 'C', 'E'])`
- 正确处理日期：`pd.read_excel('file.xlsx', parse_dates=['date_column'])`

## 代码风格指南
**重要**：当为Excel操作生成Python代码时：
- 编写简洁、精简的Python代码，无需不必要的注释
- 避免冗长的变量名和冗余操作
- 避免不必要的print语句

**对于Excel文件本身**：
- 对包含复杂公式或重要假设的单元格添加注释
- 记录硬编码值的来源
- 包括关键计算和模型部分的说明

## 数据分析模式

### 读取多个工作表

使用ExcelFile高效处理所有工作表：

```python
import pandas as pd

excel_file = pd.ExcelFile("workbook.xlsx")

for sheet_name in excel_file.sheet_names:
    df = pd.read_excel(excel_file, sheet_name=sheet_name)
    print(f"{sheet_name}: {len(df)}行")
```

### 数据透视表

```python
import pandas as pd

df = pd.read_excel("sales_data.xlsx")

pivot = pd.pivot_table(
    df,
    values="sales",
    index="region",
    columns="product",
    aggfunc="sum",
    fill_value=0
)

pivot.to_excel("pivot_report.xlsx")
```

### 分组和聚合

```python
df = pd.read_excel("sales.xlsx")

# 分组求和
sales_by_region = df.groupby("region")["sales"].sum()

# 多重聚合
summary = df.groupby("region").agg({
    "sales": "sum",
    "quantity": "mean",
    "profit": ["min", "max"]
})
```

### 筛选

```python
# 简单筛选
high_sales = df[df["sales"] > 10000]

# 多个条件
filtered = df[(df["region"] == "West") & (df["sales"] > 5000)]

# 计算新列
df["profit_margin"] = (df["revenue"] - df["cost"]) / df["revenue"]

# 排序
df_sorted = df.sort_values("sales", ascending=False)
```

## 数据清理

```python
import pandas as pd

df = pd.read_excel("messy_data.xlsx")

# 删除重复项
df = df.drop_duplicates()

# 处理缺失值
df = df.fillna(0)           # 填充为值
df = df.dropna()            # 删除包含缺失值的行
df = df.dropna(subset=["important_col"])  # 仅在特定列为空时删除

# 从字符串中删除空格
df["name"] = df["name"].str.strip()

# 转换数据类型
df["date"] = pd.to_datetime(df["date"])
df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

# 保存清理后的数据
df.to_excel("cleaned_data.xlsx", index=False)
```

## 合并和连接

```python
import pandas as pd

# 垂直堆叠（堆叠行）连接文件
df1 = pd.read_excel("sales_q1.xlsx")
df2 = pd.read_excel("sales_q2.xlsx")
combined = pd.concat([df1, df2], ignore_index=True)

# 基于共同列合并（类似于SQL JOIN）
customers = pd.read_excel("customers.xlsx")
sales = pd.read_excel("sales.xlsx")

merged = pd.merge(sales, customers, on="customer_id", how="left")

merged.to_excel("merged_data.xlsx", index=False)
```

## 图表和可视化

使用matplotlib从Excel数据生成图表：

```python
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_excel("data.xlsx")

# 条形图
df.plot(x="category", y="value", kind="bar")
plt.title("按类别划分的销售额")
plt.xlabel("类别")
plt.ylabel("销售额")
plt.tight_layout()
plt.savefig("bar_chart.png")
plt.close()

# 饼图
df.set_index("category")["value"].plot(kind="pie", autopct="%1.1f%%")
plt.title("市场份额")
plt.ylabel("")
plt.savefig("pie_chart.png")
plt.close()

# 折线图
df.plot(x="date", y="revenue", kind="line")
plt.savefig("trend.png")
plt.close()
```

## 条件格式化

根据单元格值编程应用格式：

```python
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Font

df = pd.DataFrame({
    "Product": ["A", "B", "C"],
    "Sales": [100, 200, 150]
})

df.to_excel("formatted.xlsx", index=False)

wb = load_workbook("formatted.xlsx")
ws = wb.active

# 定义填充
red_fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
green_fill = PatternFill(start_color="00FF00", end_color="00FF00", fill_type="solid")

# 应用条件格式化
for row in range(2, len(df) + 2):
    cell = ws[f"B{row}"]
    if cell.value < 150:
        cell.fill = red_fill
    else:
        cell.fill = green_fill

# 加粗标题
for cell in ws[1]:
    cell.font = Font(bold=True)

wb.save("formatted.xlsx")
```

## 性能技巧

对于大型Excel文件：

```python
import pandas as pd

# 仅读取特定列
df = pd.read_excel("large.xlsx", usecols=["A", "C", "E"])

# 对于非常大的文件，分块读取
for chunk in pd.read_excel("huge.xlsx", chunksize=10000):
    # 处理每个块
    process(chunk)

# 指定数据类型以避免推断开销
df = pd.read_excel("data.xlsx", dtype={"id": str, "amount": float})

# 对于openpyxl与大型文件
from openpyxl import load_workbook
wb = load_workbook("large.xlsx", read_only=True)  # 只读模式
```

## 实用工具

### 自动调整列宽

```python
import pandas as pd

df = pd.DataFrame({"Product": ["Widget A", "Widget B"], "Sales": [100, 200]})

writer = pd.ExcelWriter("output.xlsx", engine="openpyxl")
df.to_excel(writer, sheet_name="Sales", index=False)

worksheet = writer.sheets["Sales"]

for column in worksheet.columns:
    max_length = 0
    column_letter = column[0].column_letter
    for cell in column:
        try:
            if len(str(cell.value)) > max_length:
                max_length = len(str(cell.value))
        except:
            pass
    worksheet.column_dimensions[column_letter].width = max_length + 2

writer.close()
```
