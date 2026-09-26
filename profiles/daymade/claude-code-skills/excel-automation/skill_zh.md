# Excel 自动化

创建专业的 Excel 文件，解析复杂的财务模型，并在 macOS 上控制 Excel。

## 快速入门

```bash
# 创建格式化的 Excel 报告
uv run --with openpyxl scripts/create_formatted_excel.py output.xlsx

# 解析 openpyxl 无法处理的复杂 xlsm 文件
uv run scripts/parse_complex_excel.py model.xlsm              # 列出工作表
uv run scripts/parse_complex_excel.py model.xlsm "DCF"        # 提取工作表
uv run scripts/parse_complex_excel.py model.xlsm --fix        # 修复损坏的名称

# 通过 AppleScript 控制 Excel（使用超时以防止卡死）
timeout 5 osascript -e 'tell application "Microsoft Excel" to activate'
```

## 概述

三种功能：

| 功能 | 工具 | 使用场景 |
|------|------|----------|
| **创建** 格式化的 Excel | `openpyxl` | 报告、原型、仪表板 |
| **解析** 复杂的 xlsm/xlsx | `zipfile` + `xml.etree` | 财务模型、VBA 工作簿、>1MB 文件 |
| **控制** Excel 窗口 | AppleScript (`osascript`) | 缩放、滚动、按程序选择单元格 |

## 工具选择决策树

```
文件是否简单（数据导出、无 VBA、<1MB）？
├─ 是 → openpyxl 或 pandas
└─ 否
   ├─ 是 .xlsm 或来自投资银行 / >1MB？
   │   └─ 是 → zipfile + xml.etree.ElementTree (标准库)
   └─ 是 .xls（BIFF 格式）？
       └─ 是 → xlrd
```

**复杂 Excel 的信号**：文件 >1MB、`.xlsm` 扩展名、来自投资银行/经纪商、包含 VBA 宏。

**重要提示**：始终先运行 `file <路径>` —— 扩展名不可信。一个 `.xls` 文件实际上可能是一个基于 ZIP 的 xlsx。

## 创建 Excel 文件 (openpyxl)

### 专业的颜色约定（投资银行标准）

| 颜色 | RGB 代码 | 含义 |
|------|----------|------|
| 蓝色 | `0000FF` | 用户输入/假设 |
| 黑色 | `000000` | 计算值 |
| 绿色 | `008000` | 跨工作表引用 |
| 深蓝色背景上的白色 | `FFFFFF` on `4472C4` | 区段标题 |
| 深蓝色文本 | `1F4E79` | 标题 |

### 核心格式模式

```python
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment

# 字体
BLUE_FONT = Font(color="0000FF", size=10, name="Calibri")
BLACK_FONT_BOLD = Font(color="000000", size=10, name="Calibri", bold=True)
GREEN_FONT = Font(color="008000", size=10, name="Calibri")
HEADER_FONT = Font(color="FFFFFF", size=12, name="Calibri", bold=True)

# 填充
DARK_BLUE_FILL = PatternFill("solid", fgColor="4472C4")
LIGHT_BLUE_FILL = PatternFill("solid", fgColor="D9E1F2")
INPUT_GREEN_FILL = PatternFill("solid", fgColor="E2EFDA")
LIGHT_GRAY_FILL = PatternFill("solid", fgColor="F2F2F2")

# 边框
THIN_BORDER = Border(bottom=Side(style="thin", color="B2B2B2"))
BOTTOM_DOUBLE = Border(bottom=Side(style="double", color="000000"))
```

### 数字格式代码

| 格式 | 代码 | 示例 |
|------|------|------|
| 货币 | `'$#,##0'` | $1,234 |
| 带小数的货币 | `'$#,##0.00'` | $1,234.56 |
| 百分比 | `'0.0%'` | 12.3% |
| 带两位小数的百分比 | `'0.00%'` | 12.34% |
| 带逗号的数字 | `'#,##0'` | 1,234 |
| 系数 | `'0.0x'` | 1.5x |

### 条件格式化（敏感性分析表）

红色到绿色的渐变用于敏感性分析：

```python
from openpyxl.formatting.rule import ColorScaleRule

rule = ColorScaleRule(
    start_type="min", start_color="F8696B",   # 红色（低）
    mid_type="percentile", mid_value=50, mid_color="FFEB84",  # 黄色（中）
    end_type="max", end_color="63BE7B"         # 绿色（高）
)
ws.conditional_formatting.add(f"B2:F6", rule)
```

### 执行

```bash
uv run --with openpyxl scripts/create_formatted_excel.py
```

完整模板脚本：见 `scripts/create_formatted_excel.py`

## 解析复杂 Excel (zipfile + xml)

当 openpyxl 在复杂的 xlsm 文件上失败（损坏的 DefinedNames、复杂的 VBA）时，直接使用标准库。

### XLSX 内部 ZIP 结构

```
file.xlsx (ZIP 存档)
├── [Content_Types].xml
├── xl/
│   ├── workbook.xml          ← 工作表名称 + 排序
│   ├── sharedStrings.xml     ← 所有文本值（查找表）
│   ├── worksheets/
│   │   ├── sheet1.xml        ← 第 1 张工作表的单元格数据
│   │   ├── sheet2.xml        ← 第 2 张工作表的单元格数据
│   │   └── ...
│   └── _rels/
│       └── workbook.xml.rels ← 映射 rId → sheetN.xml
└── _rels/.rels
```

### 工作表名称解析（两步）

工作表名称在 `workbook.xml` 中通过 `_rels/workbook.xml.rels` 链接到物理文件：

```python
import zipfile
import xml.etree.ElementTree as ET

MAIN_NS = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
REL_NS = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
RELS_NS = 'http://schemas.openxmlformats.org/package/2006/relationships'

def get_sheet_path(zf, sheet_name):
    """解析工作表名称到 ZIP 内的物理 XML 文件路径."""
    # 第一步：workbook.xml → 查找与工作表名称对应的 rId
    wb_xml = ET.fromstring(zf.read('xl/workbook.xml'))
    sheets = wb_xml.findall(f'.//{{{MAIN_NS}}}sheet')
    rid = None
    for s in sheets:
        if s.get('name') == sheet_name:
            rid = s.get(f'{{{REL_NS}}}id')
            break
    if not rid:
        raise ValueError(f"未找到工作表 '{sheet_name}'")

    # 第二步：workbook.xml.rels → 映射 rId 到文件路径
    rels_xml = ET.fromstring(zf.read('xl/_rels/workbook.xml.rels'))
    for rel in rels_xml.findall(f'{{{RELS_NS}}}Relationship'):
        if rel.get('Id') == rid:
            return 'xl/' + rel.get('Target')

    raise ValueError(f"没有找到 {rid} 的文件映射")
```

### 单元格数据提取

```python
def extract_cells(zf, sheet_path):
    """从工作表 XML 提取所有单元格值."""
    # 构建共享字符串查找表
    shared = []
    try:
        ss_xml = ET.fromstring(zf.read('xl/sharedStrings.xml'))
        for si in ss_xml.findall(f'{{{MAIN_NS}}}si'):
            texts = si.itertext()
            shared.append(''.join(texts))
    except KeyError:
        pass  # 无共享字符串

    # 解析工作表单元格
    sheet_xml = ET.fromstring(zf.read(sheet_path))
    rows = sheet_xml.findall(f'.//{{{MAIN_NS}}}row')

    data = {}
    for row in rows:
        for cell in row.findall(f'{{{MAIN_NS}}}c'):
            ref = cell.get('r')         # 例如 "A1"
            cell_type = cell.get('t')   # "s" = 共享字符串，None = 数字
            val_el = cell.find(f'{{{MAIN_NS}}}v')

            if val_el is not None and val_el.text:
                if cell_type == 's':
                    data[ref] = shared[int(val_el.text)]
                else:
                    try:
                        data[ref] = float(val_el.text)
                    except ValueError:
                        data[ref] = val_el.text
    return data
```

### 修复损坏的 DefinedNames

投资银行的 xlsm 文件通常包含损坏的 `<definedName>` 条目，其中包含 "Formula removed"：

```python
def fix_defined_names(zf_in_path, zf_out_path):
    """删除损坏的 DefinedNames 并重新打包."""
    import shutil, tempfile
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        with zipfile.ZipFile(zf_in_path, 'r') as zf:
            zf.extractall(tmp)

        wb_xml_path = tmp / 'xl' / 'workbook.xml'
        tree = ET.parse(wb_xml_path)
        root = tree.getroot()

        ns = {'main': MAIN_NS}
        defined_names = root.find('.//main:definedNames', ns)
        if defined_names is not None:
            for name in list(defined_names):
                if name.text and "Formula removed" in name.text:
                    defined_names.remove(name)

        tree.write(wb_xml_path, encoding='utf-8', xml_declaration=True)

        with zipfile.ZipFile(zf_out_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for fp in tmp.rglob('*'):
                if fp.is_file():
                    zf.write(fp, fp.relative_to(tmp))
```

完整模板脚本：见 `scripts/parse_complex_excel.py`

## 在 macOS 上控制 Excel (AppleScript)

所有命令在 macOS 上使用 Microsoft Excel 验证。

### 验证命令

```bash
# 激活 Excel（带到前台）
osascript -e 'tell application "Microsoft Excel" to activate'

# 打开文件
osascript -e 'tell application "Microsoft Excel" to open POSIX file "/path/to/file.xlsx"'

# 设置缩放级别（百分比）
osascript -e 'tell application "Microsoft Excel"
    set zoom of active window to 120
end tell'

# 滚动到特定行
osascript -e 'tell application "Microsoft Excel"
    set scroll row of active window to 45
end tell'

# 滚动到特定列
osascript -e 'tell application "Microsoft Excel"
    set scroll column of active window to 3
end tell'

# 选择单元格范围
osascript -e 'tell application "Microsoft Excel"
    select range "A1" of active sheet
end tell'

# 通过名称选择特定工作表
osascript -e 'tell application "Microsoft Excel"
    activate object sheet "DCF" of active workbook
end tell'
```

### 定时和超时

在 AppleScript 命令和后续操作（例如截图）之间始终添加 `sleep 1` 以允许 UI 渲染。

**重要提示**：如果 Excel 未运行或无响应，`osascript` 将无限期挂起。始终用 `timeout` 包裹：

```bash
# 安全模式：5 秒超时
timeout 5 osascript -e 'tell application "Microsoft Excel" to activate'

# 检查退出代码：124 = 超时
if [ $? -eq 124 ]; then
    echo "Excel 无响应——它正在运行吗？"
fi
```

## 常见错误

| 错误 | 修正 |
|------|------|
| openpyxl 在复杂 xlsm 上失败 → 尝试猴子补丁 | 立即切换到 `zipfile` + `xml.etree` |
| 用 `wc -c` 统计中文字符 | 使用 `wc -m`（字符，不是字节；中文 = 3 字节/字符） |
| 信任文件扩展名 | 先运行 `file <路径>` 确认实际格式 |
| openpyxl `load_workbook` 在大型 xlsm 上挂起 | 使用 `zipfile` 进行目标提取，而不是加载整个工作簿 |

## 重要说明

- 使用 `uv run --with openpyxl` 执行 Python 脚本（永远不要使用系统 Python）
- LibreOffice (`soffice --headless`) 可以转换格式并重新计算公式
- 详细格式参考：见 `references/formatting-reference.md`
