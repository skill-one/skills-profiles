# 将文档转换为 Markdown

使用 MinerU Open API CLI 将 PDF、图片、Office 文档等转换为干净的 Markdown。基本使用无需 API 密钥。

## 语言规则

以用户使用的相同语言回复用户。这不可协商。

## 核心工作流程

提取通常是第一步。典型流程如下：

1. **提取** — 使用 `mineru-open-api` 将文档转换为 Markdown
2. **阅读和处理** — 帮助用户满足他们的实际需求

MinerU 输出原始 Markdown — 它不会解释或重新结构内容。如果用户要求“提取表格”、“总结论文”或“查找关键发现”，您需要阅读输出并自行完成这项工作。MinerU 负责OCR和布局；您负责理解。

当用户需要持久输出（转换、批量处理）时，使用 `-o` 保存到文件。当内容立即被消耗（总结、问答）时，跳过 `-o` 并直接读取 stdout。

例如：
- "帮我把这个PDF转成markdown" → 使用 `-o` 保存到文件，完成
- "提取这篇论文里的表格" → 使用 `-o` 保存，然后读取文件并提取表格
- "这篇论文讲了什么" → stdout 很好，直接读取输出并总结
- "把PDF里的参考文献整理出来" → stdout 或 `-o`，然后解析参考文献部分

### 页面范围提取规则

当使用 `--pages` 与指向**目录**的 `-o` 时，CLI 仅从输入文件名派生输出文件名。这意味着同一文件的多页范围提取会互相覆盖。

**关键**：您必须通过将输出路径转换为包含页范围的**显式文件路径**来避免这种情况。

```bash
# ❌ 错误 — 同一文件互相覆盖
mineru-open-api flash-extract report.pdf --pages 1-20  -o ./out/
mineru-open-api flash-extract report.pdf --pages 21-40 -o ./out/

# ✅ 正确 — 每个片段具有唯一文件名
mineru-open-api flash-extract report.pdf --pages 1-20  -o ./out/report_p1-20.md
mineru-open-api flash-extract report.pdf --pages 21-40 -o ./out/report_p21-40.md
```

每当用户要求按页范围拆分文档（例如，“提取1-20页”、“拆分成多个片段”）时，始终生成带有 `_p{范围}` 后缀的精确文件路径作为 `-o`。

| 用户说 | 您生成 |
|---|---|
| "把 report.pdf 每20页拆分成多个文件" | `-o ./out/report_p1-20.md`, `-o ./out/report_p21-40.md`... |
| "extract pages 1-10 and 11-20" | `-o ./out/report_p1-10.md`, `-o ./out/report_p11-20.md` |

## 两种提取模式

### flash-extract — 快速，无需认证

适用于快速阅读。无需 API 密钥，无需设置。

```bash
mineru-open-api flash-extract report.pdf                               # 输出到 stdout（用于立即消耗）
mineru-open-api flash-extract report.pdf -o ./output/                  # 保存到文件
mineru-open-api flash-extract report.pdf -o ./output/report_p1-10.md   # 页范围（显式文件路径）
mineru-open-api flash-extract report.pdf -o ./output/ --language en    # 语言提示
mineru-open-api flash-extract https://example.com/paper.pdf            # URL 输入
```

**支持**：PDF、图片（PNG、JPG、WebP...）、DOCX、PPTX、Excel（XLS、XLSX）
**限制**：每个文档10 MB / 20 页
**输出**：仅 Markdown — 图片、表格和公式可能成为占位符

除非用户需要更多，否则默认使用 flash-extract。

### extract — 精准，需要认证

当用户需要完整保真输出时使用：保留的图片、准确的表格、LaTeX 公式或非 Markdown 格式。需要通过 `mineru-open-api auth` 提供令牌。

```bash
mineru-open-api extract report.pdf                              # 输出到 stdout
mineru-open-api extract report.pdf -o ./out/                    # 保存所有资源
mineru-open-api extract report.pdf -o ./out/ -f md,docx         # 多种输出格式
mineru-open-api extract report.pdf -o ./out/report_p1-20.md --pages 1-20  # 页范围（显式文件路径）
mineru-open-api extract report.pdf -o ./out/ --ocr          # 对扫描文档强制进行 OCR
mineru-open-api extract *.pdf -o ./results/                 # 批量处理
mineru-open-api extract --list files.txt -o ./results/      # 从文件列表批量处理
```

**支持**：PDF、图片、DOC、DOCX、PPT、PPTX、HTML
**限制**：每个文档200 MB / 600 页
**输出格式**：`md`、`json`、`html`、`latex`、`docx`（用逗号分隔，与 `-f` 一起使用）
**功能**：公式识别（默认开启）、表格识别（默认开启）、OCR 开关、批量模式、模型选择（`vlm`、`pipeline`、`html`）

如果用户尚未进行认证，请指导他们先运行 `mineru-open-api auth`。

## 何时使用哪种模式

| 情况 | 模式 |
|---|---|
| "这个 PDF 是什么内容？" | flash-extract |
| 快速总结或内容扫描 | flash-extract |
| 需要保留图片/表格/公式 | extract |
| 文档 > 10 MB 或 > 20 页 | extract |
| 批量转换多个文件 | extract |
| 需要 DOCX/LaTeX/HTML 输出 | extract |
| 扫描文档需要 OCR | 带有 `--ocr` 的 extract |

## 语言支持

默认是 `ch`（中文 + 英语）。使用 `--language` 指定其他语言。常见代码：

| 语言 | 代码 | 语言 | 代码 |
|---|---|---|---|
| 中文 + 英语 | `ch` | 日语 | `japan` |
| 英语 | `en` | 韩语 | `korean` |
| 法语 | `fr` | 中文繁体 | `chinese_cht` |
| 德语 | `de` | 西班牙语 | `es` |
| 俄语 | `ru` | 阿拉伯语 | `ar` |
| 葡萄牙语 | `pt` | 印地语 | `hi` |
| 意大利语 | `it` | 越南语 | `vi` |
| 泰语 | `th` | 土耳其语 | `tr` |

总共支持 80 多种语言 — 对于上述列表中未列出的任何语言，请使用 PaddleOCR 语言代码。

## 数据流

两个命令都将文档发送到 MinerU 的 API（mineru.net）进行处理。这是一个无状态的 API 调用，没有持久存储。MinerU 由 OpenDataLab（上海人工智能实验室）开源：https://github.com/opendatalab/MinerU

## 故障排除

- **调试 API 请求**：添加 `-v` 标志以查看 HTTP 请求/响应详细信息（例如，`mineru-open-api flash-extract report.pdf -v`）
- **CLI 未找到**：通过以下方式安装：
  - `npm i -g mineru-open-api`（Node.js）
  - `uv tool install mineru-open-api`（Python/uv）
  - macOS/Linux：`curl -fsSL https://cdn-mineru.openxlab.org.cn/open-api-cli/install.sh | sh`
  - Windows：`irm https://cdn-mineru.openxlab.org.cn/open-api-cli/install.ps1 | iex`
- **extract 认证错误**：运行 `mineru-open-api auth` 设置您的令牌
- **大文件超时**：使用 `--timeout 600`（秒）增加超时时间
- **输出语言错误**：显式设置 `--language`（例如，`--language en` 用于英文文档）
