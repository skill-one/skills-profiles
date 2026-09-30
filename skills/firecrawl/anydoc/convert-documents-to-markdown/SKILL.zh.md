---
name: convert-documents-to-markdown
description: 将 Word (.doc, .docx)、PowerPoint (.ppt, .pptx)、Excel (.xls, .xlsx)、OpenDocument (.odt, .ods, .odp)、RTF、EPUB、CSV 和 PDF 文件转换为 GitHub 风格的 Markdown。当任务需要处理您无法直接读取的办公文档、电子表格、演示文稿、电子书或 PDF 内容时使用。
---

# 将文档转换为 Markdown

运行 anydoc CLI。它需要 Node 20+，无需安装：

```bash
npx -y @firecrawl/anydoc <文件>              # Markdown 输出到标准输出
npx -y @firecrawl/anydoc <文件> -o out.md    # 写入文件
npx -y @firecrawl/anydoc - --format csv < f  # 从标准输入读取
```

规则：

1. 支持的输入格式：`.doc`、`.docx`、`.docm`、`.odt`、`.rtf`、`.epub`、`.pdf`、`.ppt`、`.pps`、`.pot`、`.pptx`、`.pptm`、`.ppsx`、`.ppsm`、`.odp`、`.xls`、`.xlsx`、`.xlsm`、`.xlsb`、`.ods`、`.csv`。
2. 格式从文件内容中检测。仅在无法检测时传递 `--format <名称>`：从标准输入读取 CSV，或扩展名缺失或错误。
3. 退出代码：0 成功，1 文档无法转换，2 使用错误，3 PDF 的页面需要 OCR。失败时在标准错误输出打印一条 `anydoc: <消息>` 行。CLI 从不提示。
4. 对于大文档，使用 `-o` 写入文件，并读取您需要的部分，而不是将所有内容流式传输到上下文中。
5. 扫描和纯图像页面需要 OCR，而 anydoc 不执行 OCR，因此文档退出代码为 3。使用 `--ocr hosted` 重新运行，将其发送到 [Firecrawl Parse](https://firecrawl.dev/parse)。无需注册。传递 `--api-key` 或设置 `FIRECRAWL_API_KEY` 以获得更高的限制。
6. 在 Node、Python 或 Rust 代码库中，优先使用库而不是调用 shell：`@firecrawl/anydoc` 在 npm 上，`firecrawl-anydoc` 在 PyPI 上，`anydoc` 在 crates.io 上。每个都暴露相同的 `to_markdown` / `toMarkdown` API。
