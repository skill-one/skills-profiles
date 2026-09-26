# xlsx-author

在以**无头**（受管代理/CMA模式）运行时使用此技能，并且您需要将Excel工作簿作为**文件工件**交付，而不是通过`mcp__office__excel_*`编辑实时工作簿。

## 输出契约

- 写入`./out/<name>.xlsx`。如果`./out/`不存在，则创建它。
- 在最终消息中返回相对路径，以便编排层可以收集它。

## 如何构建工作簿

编写一个简短的Python脚本，并使用Bash运行它。使用`openpyxl`：

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill

wb = Workbook()
ws = wb.active; ws.title = "Inputs"
ws["B2"] = "Revenue"; ws["C2"] = 1_250_000_000
ws["C2"].font = Font(color="0000FF")           # 蓝色 = 硬编码输入
calc = wb.create_sheet("DCF")
calc["C5"] = "=Inputs!C2*(1+Inputs!C3)"        # 黑色 = 公式
wb.save("./out/model.xlsx")
```

## 规范（镜像`audit-xls`）

- **蓝色 / 黑色 / 绿色。** 蓝色 = 硬编码输入，黑色 = 公式，绿色 = 链接到另一个工作表/文件。
- **计算单元格中不要有硬编码。** 每个计算单元格都是公式；每个输入都位于Inputs工作表上。
- **命名范围**用于从演示文稿或备忘录中引用的任何值。
- **平衡检查。** 包含一个Checks工作表，该工作表将（资产负债表平衡、现金流量表与现金挂钩等）并显示TRUE/FALSE。
- **每个文件一个模型。** 除非明确要求，否则不要追加到现有工作簿。

## 不应使用的情况

如果`mcp__office__excel_*`工具可用（Cowork插件模式），请使用它们——它们通过审查检查点驱动用户的实时工作簿。此技能是无头运行时的文件生成回退方案。
