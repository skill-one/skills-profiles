# firecrawl crawl

批量从网站提取内容。爬取页面并跟随链接，直到达到深度/限制。

**前提条件：** `crawl` 需要认证（没有无密钥的免费套餐）；如果没有凭证，CLI 会提示交互式登录。

## 快速入门

```bash
# 爬取文档部分
firecrawl crawl "<url>" --include-paths /docs --limit 50 --wait -o .firecrawl/crawl.json

# 带深度限制的完整爬取
firecrawl crawl "<url>" --max-depth 3 --wait --progress -o .firecrawl/crawl.json

# 检查正在运行的爬取状态
firecrawl crawl <job-id>
```

运行 `firecrawl crawl --help` 获取完整选项列表。

**完成时：** 爬取达到终端状态，并且 `.firecrawl/` 下保存的输出包含预期页面。

## 小贴士

- 当你需要立即获取结果时，使用 `--wait`。它没有默认超时；使用 `--timeout <秒数>` 来限制轮询。没有 `--wait`，爬取会返回一个作业 ID 用于异步轮询。
- **使用 `--include-paths` 限制爬取范围**，每当请求命名一个部分时——只爬取你需要的页面。
- 爬取按页面消耗积分。在执行大型爬取前检查 `firecrawl credit-usage`（`credit-usage` 需要认证）。

## 参见

- [firecrawl-scrape](../firecrawl-scrape/SKILL.md) — 爬取单个页面
- [firecrawl-map](../firecrawl-map/SKILL.md) — 在决定爬取前发现 URL
- [firecrawl-download](../firecrawl-download/SKILL.md) — 下载网站到本地文件（使用 map + scrape）
- [firecrawl-build-scrape](https://github.com/firecrawl/skills/tree/main/skills/build/firecrawl-build-scrape) — 将批量提取集成到应用程序中，而不是在这里运行
