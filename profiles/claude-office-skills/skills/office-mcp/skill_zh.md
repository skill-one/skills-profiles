# Office MCP 服务器

## 概述

一个完整的 MCP（模型上下文协议）服务器，提供 **39 个工具**用于 Office 文档操作。使用 TypeScript/Node.js 实现，具有实际功能（非占位符）。

## 工具类别

### PDF 工具 (10)
| 工具 | 描述 |
|------|-------------|
| `extract_text_from_pdf` | 提取文本内容，支持页面选择 |
| `extract_tables_from_pdf` | 从 PDF 中提取表格数据 |
| `merge_pdfs` | 将多个 PDF 合并成一个 |
| `split_pdf` | 按页面范围分割 PDF |
| `compress_pdf` | 压缩 PDF 文件大小 |
| `add_watermark_to_pdf` | 添加文本/图片水印 |
| `fill_pdf_form` | 填充 PDF 表单字段 |
| `get_pdf_metadata` | 获取 PDF 属性和元数据 |
| `ocr_pdf` | 对扫描的 PDF 进行 OCR（多语言） |
| `ocr_image` | 对图像文件（PNG、JPG、TIFF 等）进行 OCR |

### 电子表格工具 (7)
| 工具 | 描述 |
|------|-------------|
| `read_xlsx` | 读取 Excel 文件，支持工作表/范围选择 |
| `create_xlsx` | 创建多工作表 Excel 文件 |
| `analyze_spreadsheet` | 统计分析（最小值/最大值/平均值/中位数） |
| `apply_formula` | 将 Excel 公式应用于单元格 |
| `create_chart` | 生成图表配置 |
| `pivot_table` | 创建带聚合的数据透视表 |
| `xlsx_to_json` | 将 Excel 转换为 JSON |

### 文档工具 (6)
| 工具 | 描述 |
|------|-------------|
| `extract_text_from_docx` | 从 Word 文档中提取文本 |
| `create_docx` | 创建带标题、列表、表格的 DOCX |
| `fill_docx_template` | 使用 {{占位符}} 填充模板 |
| `analyze_document_structure` | 分析标题、表格、字数 |
| `insert_table_to_docx` | 将表格插入文档 |
| `merge_docx_files` | 合并多个 Word 文档 |

### 转换工具 (9)
| 工具 | 描述 |
|------|-------------|
| `xlsx_to_csv` | 将 Excel 转换为 CSV |
| `csv_to_xlsx` | 将 CSV 转换为 Excel |
| `json_to_xlsx` | 将 JSON 数组转换为 Excel |
| `docx_to_md` | 将 Word 转换为 Markdown |
| `md_to_docx` | 将 Markdown 转换为 Word |
| `pdf_to_docx` | 将 PDF 转换为 Word（文本提取） |
| `docx_to_pdf` | 将 Word 转换为 PDF（需要外部工具） |
| `html_to_pdf` | 将 HTML 转换为 PDF（需要外部工具） |
| `batch_convert` | 批量转换多个文件 |

### 演示文稿工具 (7)
| 工具 | 描述 |
|------|-------------|
| `create_pptx` | 创建带主题的 PowerPoint |
| `extract_from_pptx` | 从 PPTX 中提取文本和图片 |
| `md_to_pptx` | 将 Markdown 转换为幻灯片 |
| `add_slide` | 向现有演示文稿添加幻灯片 |
| `update_slide` | 更新幻灯片内容 |
| `pptx_to_html` | 转换为 reveal.js HTML |
| `get_pptx_outline` | 获取演示文稿结构 |

## 安装

### 1. 克隆和构建

```bash
cd mcp-servers/office-mcp
npm install
npm run build
```

### 2. 配置 Claude Desktop

添加到 `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "office-mcp": {
      "command": "/usr/local/bin/node",
      "args": ["/path/to/claude-office-skills/mcp-servers/office-mcp/dist/index.js"]
    }
  }
}
```

### 3. 重启 Claude Desktop

## 示例提示

- "读取位于 ~/Documents/sales.xlsx 的 Excel 文件"
- "创建一个关于 AI 趋势的 5 张幻灯片 PowerPoint"
- "从 PDF 中提取文本并转换为 Markdown"
- "合并这 3 个 Word 文档为一个"
- "分析此电子表格中的数据"

## 依赖项

```
pdf-parse, pdf-lib       - PDF 操作
tesseract.js             - OCR（纯 JavaScript，无需原生二进制文件）
xlsx                     - Excel 操作
mammoth, docx            - Word 操作
docxtemplater, pizzip    - 模板填充
pptxgenjs, jszip         - PowerPoint 操作
turndown, marked         - Markdown 转换
```

### 支持的 OCR 语言
- `eng` - 英语
- `chi_sim` - 简体中文
- `chi_tra` - 繁体中文
- `jpn` - 日语
- `kor` - 韩语
- `fra` - 法语
- `deu` - 德语
- `spa` - 西班牙语

## 资源

- [MCP 服务器代码](https://github.com/claude-office-skills/skills/tree/main/mcp-servers/office-mcp)
- [实施计划](./mcp-servers/office-mcp/IMPLEMENTATION_PLAN.md)
- [Claude Office 技能中心](https://github.com/claude-office-skills/skills)
