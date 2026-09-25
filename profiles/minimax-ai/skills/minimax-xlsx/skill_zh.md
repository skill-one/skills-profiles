# MiniMax XLSX 技能

直接处理请求。不要生成子代理。始终按照用户要求的输出文件格式编写。

## 任务路由

| 任务 | 方法 | 指南 |
|------|--------|-------|
| **读取** — 分析现有数据 | `xlsx_reader.py` + pandas | `references/read-analyze.md` |
| **创建** — 从零开始创建新的 xlsx 文件 | XML 模板 | `references/create.md` + `references/format.md` |
| **编辑** — 修改现有的 xlsx 文件 | XML 解包→编辑→打包 | `references/edit.md` (+ `format.md` 如果需要样式) |
| **修复** — 修复现有 xlsx 文件中的损坏公式 | XML 解包→修复 `<f>` 节点→打包 | `references/fix.md` |
| **验证** — 检查公式 | `formula_check.py` | `references/validate.md` |

## 读取 — 分析数据（首先阅读 `references/read-analyze.md`）

使用 `xlsx_reader.py` 进行结构发现，然后使用 pandas 进行自定义分析。不要修改源文件。

**格式规则**：当用户指定小数位数（例如 "2 位小数"）时，将此格式应用于所有数值 — 对每个数字使用 `f'{v:.2f}'`。当 `12875.00` 是必需时，不要输出 `12875`。

**聚合规则**：始终直接从 DataFrame 列计算总和/平均值/计数 — 例如 `df['Revenue'].sum()`。聚合前不要重新推导列值。

## 创建 — XML 模板（阅读 `references/create.md` + `references/format.md`）

复制 `templates/minimal_xlsx/` → 直接编辑 XML → 使用 `xlsx_pack.py` 打包。每个派生值必须是 Excel 公式（`<f>SUM(B2:B9)</f>`），不能是硬编码的数字。根据 `format.md` 应用字体颜色。

## 编辑 — XML 直接编辑（首先阅读 `references/edit.md`）

**关键 — 编辑完整性规则**：
1. **编辑任务中绝不能创建新的 `Workbook()`**。始终加载原始文件。
2. 输出必须包含与输入**相同的表**（相同的名称，相同的数据）。
3. 仅修改任务要求的特定单元格 — 其他所有内容必须保持不变。
4. **保存输出.xlsx 后，验证它**：使用 `xlsx_reader.py` 或 `pandas` 打开并确认原始表名和原始数据样本是否存在。如果验证失败，则你编写的文件不正确 — 在交付前修复它。

不要对现有文件使用 openpyxl 循环（会损坏 VBA、数据透视表、趋势线）。相反：解包 → 使用辅助脚本 → 重新打包。

**填充单元格 / 向现有单元格添加公式 = 编辑任务**。如果输入文件已存在，并且被告知要填充、更新或向特定单元格添加公式，你**必须**使用 XML 编辑路径。不要创建新的 `Workbook()`。示例 — 使用跨表 SUM 公式填充 B3：
```bash
python3 SKILL_DIR/scripts/xlsx_unpack.py input.xlsx /tmp/xlsx_work/
# 通过 xl/workbook.xml 找到目标表的 XML → xl/_rels/workbook.xml.rels
# 然后，使用编辑工具在目标 <c> 元素内部添加 <f>：
#   <c r="B3"><f>SUM('Sales Data'!D2:D13)</f><v></v></c>
python3 SKILL_DIR/scripts/xlsx_pack.py /tmp/xlsx_work/ output.xlsx
```

**添加一列**（公式、numfmt、样式自动从相邻列复制）：
```bash
python3 SKILL_DIR/scripts/xlsx_unpack.py input.xlsx /tmp/xlsx_work/
python3 SKILL_DIR/scripts/xlsx_add_column.py /tmp/xlsx_work/ --col G \
    --sheet "Sheet1" --header "% of Total" \
    --formula '=F{row}/$F$10' --formula-rows 2:9 \
    --total-row 10 --total-formula '=SUM(G2:G9)' --numfmt '0.0%' \
    --border-row 10 --border-style medium
python3 SKILL_DIR/scripts/xlsx_pack.py /tmp/xlsx_work/ output.xlsx
```
`--border-row` 标志将应用于该行中所有单元格的顶部边框（而不仅仅是新列）。当任务要求总行使用会计样式边框时，使用它。

**插入一行**（移动现有行，更新 SUM 公式，修复循环引用）：
```bash
python3 SKILL_DIR/scripts/xlsx_unpack.py input.xlsx /tmp/xlsx_work/
# 重要提示：通过在工作表 XML 中搜索标签文本来找到正确的 --at 行，而不是使用提示中的行号。
# 提示可能说 "row 5 (Office Rent)"，但 Office Rent 实际上可能在第 4 行。始终先通过文本标签定位行。
python3 SKILL_DIR/scripts/xlsx_insert_row.py /tmp/xlsx_work/ --at 5 \
    --sheet "Budget FY2025" --text A=Utilities \
    --values B=3000 C=3000 D=3500 E=3500 \
    --formula 'F=SUM(B{row}:E{row})' --copy-style-from 4
python3 SKILL_DIR/scripts/xlsx_pack.py /tmp/xlsx_work/ output.xlsx
```
**行查找规则**：当任务说 "after row N (Label)" 时，始终在 worksheet XML 中搜索 "Label"（`grep -n "Label" /tmp/xlsx_work/xl/worksheets/sheet*.xml` 或检查 sharedStrings.xml）。使用实际行号 + 1 作为 `--at`。不要单独调用 `xlsx_shift_rows.py` — `xlsx_insert_row.py` 会内部调用它。

**应用行宽边框**（例如，总行上的会计线）：
运行辅助脚本后，将边框应用于目标行中的所有单元格，而不仅仅是新添加的单元格。在 `xl/styles.xml` 中，追加一个新的 `<border>` 并设置所需的样式，然后在 `<cellXfs>` 中追加一个新的 `<xf>`，它克隆每个现有的 `<xf>` 但设置新的 `borderId`。通过 `s` 属性将新的样式索引应用于行中的每个 `<c>`：
```xml
<!-- 在 xl/styles.xml 中追加到 <borders>: -->
<border>
  <left/><right/><top style="medium"/><bottom/><diagonal/>
</border>
<!-- 然后追加到 <cellXfs> 一个具有新 borderId 的每个现有样式的克隆 -->
```
**关键规则**：当任务说 "add a border to row N" 时，迭代 A 列到最后列的所有单元格，而不仅仅是新添加的单元格。

**手动 XML 编辑**（对于辅助脚本未涵盖的内容）：
```bash
python3 SKILL_DIR/scripts/xlsx_unpack.py input.xlsx /tmp/xlsx_work/
# ... 使用编辑工具编辑 XML ...
python3 SKILL_DIR/scripts/xlsx_pack.py /tmp/xlsx_work/ output.xlsx
```

## 修复 — 修复损坏的公式（首先阅读 `references/fix.md`）

这是一个编辑任务。解包 → 修复损坏的 `<f>` 节点 → 打包。保留所有原始表和数据。

## 验证 — 检查公式（首先阅读 `references/validate.md`）

运行 `formula_check.py` 进行静态验证。在可用时使用 `libreoffice_recalc.py` 进行动态重新计算。

## 财务颜色标准

| 单元格角色 | 字体颜色 | 十六进制代码 |
|-----------|-----------|----------|
| 硬编码输入 / 假设 | 蓝色 | `0000FF` |
| 公式 / 计算结果 | 黑色 | `000000` |
| 跨表引用公式 | 绿色 | `00B050` |

## 关键规则

1. **公式优先**：每个计算单元格必须使用 Excel 公式，而不是硬编码的数字
2. **创建 → XML 模板**：复制最小模板，直接编辑 XML，使用 `xlsx_pack.py` 打包
3. **编辑 → XML**：不要使用 openpyxl 循环。使用解包/编辑/打包脚本
4. **始终生成输出文件** — 这是 #1 优先级
5. **交付前验证**：`formula_check.py` 退出码 0 = 安全

## 辅助脚本

```bash
python3 SKILL_DIR/scripts/xlsx_reader.py input.xlsx                 # 结构发现
python3 SKILL_DIR/scripts/formula_check.py file.xlsx --json         # 公式验证
python3 SKILL_DIR/scripts/formula_check.py file.xlsx --report      # 标准化报告
python3 SKILL_DIR/scripts/xlsx_unpack.py in.xlsx /tmp/work/         # 解包用于 XML 编辑
python3 SKILL_DIR/scripts/xlsx_pack.py /tmp/work/ out.xlsx          # 编辑后重新打包
python3 SKILL_DIR/scripts/xlsx_shift_rows.py /tmp/work/ insert 5 1  # 移动行用于插入
python3 SKILL_DIR/scripts/xlsx_add_column.py /tmp/work/ --col G ... # 添加带公式的列
python3 SKILL_DIR/scripts/xlsx_insert_row.py /tmp/work/ --at 6 ...  # 插入带数据的行为
```
