# 商业文档生成器

## 概述

从高质量的PDF模板生成专业的商业文档（项目提案、商业计划、年度预算）。使用捆绑的Python脚本将用户提供的填充模板数据，并输出准备分发的光滑PDF文档。

## 何时使用此技能

在用户要求以下操作时激活此技能：
- 创建商业提案或项目提案
- 生成商业计划文档
- 制定年度预算计划
- 基于可用模板创建任何专业的商业文档
- 使用特定数据填写商业模板

## 可用文档类型

此技能支持三种类型的商业文档：

1. **项目提案** - 专业的客户项目提案
   - 模板：`assets/templates/Professional Proposal Template.pdf`
   - 用例：向客户和利益相关者提案项目

2. **商业计划** - 综合商业规划文档
   - 模板：`assets/templates/Comprehensive Business Plan Template.pdf`
   - 用例：创业计划、投资者演示、战略规划

3. **年度预算** - 详细的预算规划文档
   - 模板：`assets/templates/Annual Budget Plan Template.pdf`
   - 用例：财务规划、预算提案、财政年度规划

## 快速入门工作流

### 第1步：理解用户需求

从用户收集以下信息：
- 需要的文档类型（提案、商业计划或预算）
- 要包含的关键数据（公司名称、客户信息、日期等）
- 任何特定的定制需求

### 第2步：准备数据

创建包含文档数据的JSON文件。参考`references/document_schemas.md`中的字段要求。

**提案示例：**
```json
{
  "title": "数字化转型计划",
  "subtitle": "Acme Corporation的全面计划",
  "client_org": "Acme Corporation",
  "client_contact": "Jane Smith,首席技术官",
  "company_name": "TechSolutions Inc.",
  "contact_info": "contact@techsolutions.com",
  "date": "2025年11月3日"
}
```

**注意：** 检查`assets/examples/`中的完整示例JSON文件：
- `proposal_example.json`
- `business_plan_example.json`
- `budget_example.json`

### 第3步：安装依赖（仅首次）

生成脚本需要Python包。安装它们：

```bash
pip install pypdf reportlab
```

### 第4步：生成文档

运行生成脚本：

```bash
python3 scripts/generate_document.py <document_type> <data_file> \
  --templates-dir assets/templates \
  --output-dir <output_directory>
```

**参数：**
- `<document_type>`: `proposal`、`business_plan`或`budget`之一
- `<data_file>`: 包含文档数据的JSON文件路径
- `--templates-dir`: 包含PDF模板的目录（默认：`assets/templates`）
- `--output-dir`: 保存生成PDF的位置（默认：`output`）
- `--output-filename`: 可选的自定义文件名

**示例：**
```bash
python3 scripts/generate_document.py proposal my_proposal_data.json \
  --templates-dir assets/templates \
  --output-dir ./generated_docs
```

### 第5步：交付文档

脚本在指定的输出目录中输出PDF文件。验证文档是否成功生成，并通知用户文件位置。

## 详细使用说明

### 创建项目提案

1. 收集提案信息：
   - 项目标题和副标题
   - 客户组织和联系方式
   - 您的公司名称和联系信息
   - 项目详情（问题、解决方案、时间表、预算）

2. 创建包含提案字段的JSON数据文件（参考`references/document_schemas.md`）

3. 运行脚本：
   ```bash
   python3 scripts/generate_document.py proposal proposal_data.json \
     --templates-dir assets/templates
   ```

4. 输出：带有封面页和内容部分的职业PDF提案

### 创建商业计划

1. 收集商业计划信息：
   - 公司名称和法律结构
   - 使命和愿景声明
   - 目标市场详情
   - 财务预测

2. 创建包含商业计划字段的JSON数据文件

3. 运行脚本：
   ```bash
   python3 scripts/generate_document.py business_plan plan_data.json \
     --templates-dir assets/templates
   ```

4. 输出：综合商业计划PDF模板

### 创建年度预算

1. 收集预算信息：
   - 财政年度
   - 公司名称
   - 预算假设（通货膨胀、增长目标）
   - 收入和支出预测

2. 创建包含预算字段的JSON数据文件

3. 运行脚本：
   ```bash
   python3 scripts/generate_document.py budget budget_data.json \
     --templates-dir assets/templates
   ```

4. 输出：包含表格和预测的年度预算计划PDF

## 重要提示

### 脚本功能

`scripts/generate_document.py`脚本：
- 从资源目录读取PDF模板
- 在模板页面上覆盖用户数据（主要封面页）
- 生成包含填写信息的PDF
- 保留原始模板结构和格式

### 当前限制

脚本目前仅填充封面页信息（标题、名称、日期）。模板正文内容作为专业框架，用户可以手动或通过其他PDF编辑工具创建文档。

### 扩展脚本

要填充封面页以外的字段，脚本可以增强以：
- 解析PDF表单字段
- 在每页特定坐标上添加文本覆盖
- 程序化替换占位符文本

根据需要修改`scripts/generate_document.py`以添加更复杂的PDF操作。

## 数据模式参考

有关每种文档类型所需和可选字段的详细信息，请参阅：
- `references/document_schemas.md` - 完整数据结构文档

## 示例文件

在`assets/examples/`中找到完整的示例：
- `proposal_example.json` - 示例项目提案数据
- `business_plan_example.json` - 示例商业计划数据
- `budget_example.json` - 示例预算计划数据

创建新文档时使用这些作为起始模板。

## 故障排除

**运行脚本时出现导入错误：**
- 安装所需包：`pip install pypdf reportlab`

**找不到模板：**
- 验证`--templates-dir`指向`assets/templates`
- 检查模板目录中是否存在PDF模板文件

**生成的PDF为空或缺少数据：**
- 验证JSON数据文件是否正确格式化
- 检查是否包含所需字段（参考`references/document_schemas.md`）

**需要定制模板：**
- 原始模板在`assets/templates/`
- 使用PDF编辑软件修改模板
- 保留原始文件名或更新脚本中的`TEMPLATE_MAP`

## 资源

### scripts/

包含文档生成Python脚本：
- `generate_document.py` - 具有CLI界面的主文档生成脚本

此脚本可以直接执行，无需加载到上下文中以提高效率。如果需要修改或调试，可以读取它。

### references/

工作时参考的文档：
- `document_schemas.md` - 所有文档类型的完整JSON数据结构

### assets/

文档生成输出中使用的文件：
- `templates/` - 每种文档类型的职业PDF模板
  - `Professional Proposal Template.pdf`
  - `Comprehensive Business Plan Template.pdf`
  - `Annual Budget Plan Template.pdf`
- `examples/` - 展示正确结构的示例JSON数据文件
  - `proposal_example.json`
  - `business_plan_example.json`
  - `budget_example.json`

这些模板和示例在生成过程中不会被加载到上下文中，但会被引用。
