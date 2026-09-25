# firecrawl parse

将本地文档转换为干净的 Markdown 并保存到磁盘上。支持 **PDF、DOCX、DOC、ODT、RTF、XLSX、XLS、HTML/HTM** 格式。

## 快速入门

始终使用 `-o` 保存到 `.firecrawl/` 目录下——解析后的文档可能达到数百 KB，如果直接流式传输到 stdout，可能会撑爆上下文。将 `.firecrawl/` 添加到 `.gitignore` 中。

```bash
mkdir -p .firecrawl

# 文件 → Markdown
firecrawl parse ./paper.pdf -o .firecrawl/paper.md

# AI 摘要
firecrawl parse ./paper.pdf -S -o .firecrawl/paper-summary.md

# 关于文档提问
firecrawl parse ./paper.pdf -Q "What are the main conclusions?" \
  -o .firecrawl/paper-qa.md
```

然后使用 `head`、`grep` 或 `rg` 逐段读取输出。

运行 `firecrawl parse --help` 获取完整选项列表。

**完成条件：** Markdown、摘要或答案已写入 `.firecrawl/` 目录，并且您已使用有限的读取方式检查过。

## 小贴士

- 带空格的路径需要加引号：`firecrawl parse "./My Doc.pdf" -o .firecrawl/mydoc.md`。
- 最大上传大小：**50 MB** 每个文件。
- 信用额度：约 1 个 PDF 页面；HTML 为 1 个固定值。
- 重新解析相同文件前，请检查 `.firecrawl/` 目录。
- 要检查您的信用额度余额（推荐用于批量处理和类似工作流），请使用 `firecrawl credit-usage`（需要认证）。

## 参见

- [firecrawl-scrape](../firecrawl-scrape/SKILL.md) — 同样适用于 URL
- [firecrawl-build-scrape](https://github.com/firecrawl/skills/tree/main/skills/build/firecrawl-build-scrape) — 将文档提取集成到应用程序中，而不是在此处运行
