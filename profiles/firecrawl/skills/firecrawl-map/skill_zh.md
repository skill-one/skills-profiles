# firecrawl map

发现网站上的 URL。使用 `--search` 参数可以在大型网站上查找特定页面。

**前提条件：** `map` 功能需要认证（无密钥的免费套餐无法使用）；如果没有凭证，CLI 会提示交互式登录。

## 快速入门

```bash
# 在大型网站上查找特定页面
firecrawl map "<url>" --search "authentication" -o .firecrawl/filtered.txt

# 获取所有 URL
firecrawl map "<url>" --limit 500 --json -o .firecrawl/urls.json
```

运行 `firecrawl map --help` 获取完整选项列表（包括站点地图处理、子域名等）。

**完成时：** URL 列表已保存到 `.firecrawl/` 目录下，并且您已选择要抓取或爬取的 URL。

## 小贴士

- **Map + scrape 是常用模式**：使用 `map --search` 找到正确的 URL，然后 `scrape` 该 URL。
- 示例：`map https://docs.example.com --search "auth"` → 找到 `/docs/api/authentication` → `scrape` 该 URL。

## 参见

- [firecrawl-scrape](../firecrawl-scrape/SKILL.md) — 抓取您发现的 URL
- [firecrawl-crawl](../firecrawl-crawl/SKILL.md) — 批量提取，而不是使用 map + scrape
- [firecrawl-download](../firecrawl-download/SKILL.md) — 下载整个网站（内部使用 map 功能）
- [firecrawl-build-search](https://github.com/firecrawl/skills/tree/main/skills/build/firecrawl-build-search) — 将 URL 发现功能集成到应用程序中，而不是在这里运行
