# 文档技能套件

适用于 Microsoft Office 格式和 PDF 的全面文档处理。

## 可用子技能

| 技能  | 格式             | 功能                                     |
| ------ | ------------------ | ------------------------------------------------ |
| `docx` | Word (.docx)       | 创建、编辑、分析、审阅修订、评论 |
| `pdf`  | PDF (.pdf)         | 提取文本、表格、元数据、合并/拆分      |
| `pptx` | PowerPoint (.pptx) | 创建、编辑演示文稿、布局、图表      |
| `xlsx` | Excel (.xlsx)      | 电子表格操作、公式、图表       |

## 使用场景

- 从零开始创建专业文档
- 编辑现有 Office 文件
- 从 PDF 中提取内容
- 处理审阅修订
- 生成报告和演示文稿
- 电子表格中的数据分析

## 工作流程

1. 确定所需的文档类型
2. 加载相应的子技能：`Skill(document-skills/docx)`，等等。
3. 按照特定子技能的工作流程操作

## 子技能详情

### docx (Word 文档)

- **创建**：使用 docx-js (JavaScript/TypeScript)
- **编辑**：使用 Document 库 (Python)
- **分析**：使用 pandoc 进行文本提取
- 详细信息请参阅 `document-skills/docx/SKILL.md`

### pdf (PDF 文档)

- 提取文本、表格、元数据
- 合并和拆分文档
- 详细信息请参阅 `document-skills/pdf/SKILL.md`

### pptx (PowerPoint)

- 创建和编辑演示文稿
- 处理布局和图表
- 详细信息请参阅 `document-skills/pptx/SKILL.md`

### xlsx (Excel)

- 电子表格操作
- 公式和分析
- 详细信息请参阅 `document-skills/xlsx/SKILL.md`
