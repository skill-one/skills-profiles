# 仪器数据到Allotrope转换器

将仪器文件转换为标准化的Allotrope简单模型（ASM）格式，用于LIMS上传、数据湖或转交给数据工程团队。

> **注意：这是一个示例技能**
>
> 该技能展示了技能如何支持您的数据工程任务——自动化模式转换、解析仪器输出以及生成可生产代码。
>
> **为您的组织进行定制：**
> - 修改`references/`文件以包含贵公司的特定模式或本体映射
> - 使用MCP服务器连接到定义您模式（例如您的LIMS、数据目录或模式注册中心）的系统
> - 扩展`scripts/`以处理专有仪器格式或内部数据标准
>
> 此模式可适用于任何需要转换格式或验证组织标准的数据转换工作流。

## 工作流程概述

1. **从文件内容检测仪器类型**（自动检测或用户指定）
2. **使用allotropy库解析文件**（原生）或灵活的备用解析器
3. **生成输出**：
   - ASM JSON（完整语义结构）
   - 扁平化CSV（二维表格格式）
   - Python解析器代码（用于数据工程师转交）
4. **交付**文件附带摘要和使用说明

> **不确定时：** 如果您不确定如何将字段映射到ASM（例如，这是原始数据还是计算值？设备设置还是环境条件？），请向用户请求澄清。参考`references/field_classification_guide.md`获取指导，但当存在歧义时，应与用户确认而不是猜测。

## 快速入门

```python
# 首先安装依赖项
pip install allotropy pandas openpyxl pdfplumber --break-system-packages

# 核心转换
from allotropy.parser_factory import Vendor
from allotropy.to_allotrope import allotrope_from_file

# 使用allotropy进行转换
asm = allotrope_from_file("instrument_data.csv", Vendor.BECKMAN_VI_CELL_BLU)
```

## 输出格式选择

**ASM JSON（默认）** - 带有本体URI的完整语义结构
- 最佳用途：期望ASM的LIMS系统、数据湖、长期归档
- 验证Allotrope模式

**扁平化CSV** - 二维表格表示
- 最佳用途：快速分析、Excel用户、没有JSON支持的系统
- 每个测量值成为一行，元数据重复

**两者** - 生成两种格式以获得最大灵活性

## 计算数据处理

**重要提示：** 将原始测量值与计算/派生值分开。

- **原始数据** → `measurement-document`（直接仪器读数）
- **计算数据** → `calculated-data-aggregate-document`（派生值）

计算值必须通过`data-source-aggregate-document`包含可追溯性：

```json
"calculated-data-aggregate-document": {
  "calculated-data-document": [{
    "calculated-data-identifier": "SAMPLE_B1_DIN_001",
    "calculated-data-name": "DNA完整性数",
    "calculated-result": {"value": 9.5, "unit": "(无单位)"},
    "data-source-aggregate-document": {
      "data-source-document": [{
        "data-source-identifier": "SAMPLE_B1_MEASUREMENT",
        "data-source-feature": "电泳轨迹"
      }]
    }
  }]
}
```

**常见计算字段按仪器类型分类：**
| 仪器 | 计算字段 |
|------|----------|
| 细胞计数器 | 可活性%、细胞密度稀释调整值 |
| 分光光度计 | 从吸光度计算的浓度、260/280比率 |
| 微孔板读取器 | 从标准曲线计算的浓度、%CV |
| 电泳 | DIN/RIN、区域浓度、平均尺寸 |
| qPCR | 相对数量、倍数变化 |

参考`references/field_classification_guide.md`获取有关原始值与计算值分类的详细指导。

## 验证

在交付给用户之前始终验证ASM输出：

```bash
python scripts/validate_asm.py output.json
python scripts/validate_asm.py output.json --reference known_good.json  # 与参考文件比较
python scripts/validate_asm.py output.json --strict  # 将警告视为错误
```

**验证规则：**
- 基于Allotrope ASM规范（2024年12月）
- 最后更新：2026-01-07
- 来源：https://gitlab.com/allotrope-public/asm

**软验证方法：**
未知的技巧、单位或样本角色生成**警告**（不是错误），以允许向前兼容。如果Allotrope在2024年12月之后添加了新值，验证器不会阻止它们——它将标记它们以供手动验证。如果您需要更严格的验证，请使用`--strict`模式将警告视为错误。

**它检查的内容：**
- 正确选择技巧（例如，多分析物分析 vs 微孔板读取器）
- 字段命名约定（空格分隔，不要用连字符）
- 计算数据具有可追溯性（`data-source-aggregate-document`）
- 测量和计算值存在唯一标识符
- 存在必要的元数据
- 有效单位和样本角色（对未知值进行软验证）

## 支持的仪器

参考`references/supported_instruments.md`获取完整列表。主要仪器：

| 类别 | 仪器 |
|------|------|
| 细胞计数 | Vi-CELL BLU、Vi-CELL XR、NucleoCounter |
| 分光光度法 | NanoDrop One/Eight/8000、Lunatic |
| 微孔板读取器 | SoftMax Pro、EnVision、Gen5、CLARIOstar |
| ELISA | SoftMax Pro、BMG MARS、MSD Workbench |
| qPCR | QuantStudio、Bio-Rad CFX |
| 色谱 | Empower、Chromeleon |

## 检测与解析策略

### 第一级：原生allotropy解析（首选）
**始终首先尝试allotropy。** 直接检查可用供应商：

```python
from allotropy.parser_factory import Vendor

# 列出所有支持的供应商
for v in Vendor:
    print(f"{v.name}")

# 常见供应商：
# AGILENT_TAPESTATION_ANALYSIS  （用于TapeStation XML）
# BECKMAN_VI_CELL_BLU
# THERMO_FISHER_NANODROP_EIGHT
# MOLDEV_SOFTMAX_PRO
# APPBIO_QUANTSTUDIO
# ... 更多
```

**当用户提供文件时，在转回手动解析之前检查allotropy是否支持它。** `scripts/convert_to_asm.py`自动检测仅涵盖allotropy供应商的一小部分。

### 第二级：灵活的备用解析
**仅在allotropy不支持仪器时使用。** 此备用解析：
- 不生成`calculated-data-aggregate-document`
- 不包含完整可追溯性
- 生成简化的ASM结构

使用灵活解析器：
- 列名模糊匹配
- 从标题中提取单位
- 从文件结构中提取元数据

### 第三级：PDF提取
对于仅限PDF的文件，使用pdfplumber提取表格，然后应用第二级解析。

## 预解析检查清单

在编写自定义解析器之前，始终：

1. **检查allotropy是否支持** - 如果可用，使用原生解析器
2. **找到一个参考ASM文件** - 检查`references/examples/`或询问用户
3. **查看仪器特定指南** - 检查`references/instrument_guides/`
4. **与参考进行验证** - 运行`validate_asm.py --reference <file>`

## 常见错误避免

| 错误 | 正确方法 |
|------|----------|
| 表现为主体 | 使用URL字符串 |
| 检测类型小写 | 使用"Absorbance"而不是"absorbance" |
| "发射波长设置" | 发射时使用"探测器波长设置" |
| 所有测量值在一个文档中 | 按孔/样本位置分组 |
| 缺少程序元数据 | 每个测量值提取所有设备设置 |

## 数据工程师的代码导出

生成科学家可以转交的独立Python脚本：

```python
# 导出解析器代码
python scripts/export_parser.py --input "data.csv" --vendor "VI_CELL_BLU" --output "parser_script.py"
```

导出的脚本：
- 不依赖pandas/allotropy之外的外部依赖项
- 包含内联文档
- 可在Jupyter笔记本中运行
- 可用于数据管道的可生产版本

## 文件结构

```
instrument-data-to-allotrope/
├── SKILL.md                          # 此文件
├── scripts/
│   ├── convert_to_asm.py            # 主要转换脚本
│   ├── flatten_asm.py               # ASM → 2D CSV转换
│   ├── export_parser.py             # 生成独立解析器代码
│   └── validate_asm.py              # 验证ASM输出质量
└── references/
    ├── supported_instruments.md     # 完整仪器列表与Vendor枚举
    ├── asm_schema_overview.md       # ASM结构参考
    ├── field_classification_guide.md # 不同字段类型的位置
    └── flattening_guide.md          # 扁平化工作原理
```

## 使用示例

### 示例1：Vi-CELL BLU文件
```
用户："将此细胞计数数据转换为Allotrope格式"
[上传viCell_Results.xlsx]

Claude：
1. 检测到Vi-CELL BLU（95%置信度）
2. 使用allotropy原生解析器转换
3. 输出：
   - viCell_Results_asm.json（完整ASM）
   - viCell_Results_flat.csv（二维格式）
   - viCell_parser.py（可导出代码）
```

### 示例2：请求代码转交
```
用户："我需要给我们的数据工程师解析NanoDrop文件的代码"

Claude：
1. 生成自包含的Python脚本
2. 包括示例输入/输出
3. 记录所有假设
4. 提供Jupyter笔记本版本
```

### 示例3：LIMS就绪的扁平化输出
```
用户："将此ELISA数据转换为我可以上传到我们LIMS的CSV"

Claude：
1. 解析微孔板读取器数据
2. 生成扁平化CSV，包含列：
   - sample_identifier, well_position, measurement_value, measurement_unit
   - instrument_serial_number, analysis_datetime, assay_type
3. 验证常见LIMS导入要求
```

## 实现说明

### 安装allotropy
```bash
pip install allotropy --break-system-packages
```

### 处理解析失败
如果原生allotropy解析失败：
1. 记录错误以进行调试
2. 转回灵活解析器
3. 向用户报告减少的元数据完整性
4. 建议从仪器导出不同格式

### ASM模式验证
当可用时，验证输出与Allotrope模式：
```python
import jsonschema
# 模式URL在references/asm_schema_overview.md中
```
