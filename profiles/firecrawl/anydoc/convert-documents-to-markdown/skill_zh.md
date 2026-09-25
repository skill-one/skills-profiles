# 将文档转换为 Markdown

运行 anydoc CLI。它需要 Node 20+，无需安装：

```bash
npx -y @firecrawl/anydoc <file>              # 输出到标准输出 Markdown
npx -y @firecrawl/anydoc <file> -o out.md    # 写入文件
npx -y @firecrawl/anydoc - --format csv < f  # 从标准输入读取
```

规则：

1. 支持的输入格式：`.doc`、`.docx`、`.docm`、`.odt`、`.rtf`、`.epub`、`.pdf`、`.ppt`、`.pps`、`.pot`、`.pptx`、`.pptm`、`.ppsx`、`.ppsm`、`.odp`、`.xls`、`.xlsx`、`.xlsm`、`.xlsb`、`.ods`、`.csv`。
2. 格式从文件内容中检测。仅在无法检测时使用 `--format <name>`：从标准输入读取 CSV，或扩展名缺失或错误。
3. 退出代码：0 表示成功，1 表示文档无法转换，2 表示使用错误，3 表示 PDF 的页面需要 OCR。失败时在标准错误输出中打印一条 `anydoc: <message>` 行。CLI 不会提示。
4. 对于大文档，使用 `-o` 写入文件，并读取您需要的部分，而不是将所有内容流式传输到上下文中。
5. 扫描和纯图像页面需要 OCR，而 anydoc 不执行 OCR，因此文档会退出状态码 3。使用 `--ocr hosted` 重新运行，将其发送到 [Firecrawl Parse](https://firecrawl.dev/parse)。无需注册。传递 `--api-key` 或设置 `FIRECRAWL_API_KEY` 以获得更高的限制。
6. 在 Node、Python 或 Rust 代码库中，优先使用库而不是调用 shell：npm 上的 `@firecrawl/anydoc`、PyPI 上的 `firecrawl-anydoc`、crates.io 上的 `anydoc`。每个都暴露相同的 `to_markdown` / `toMarkdown` API。
