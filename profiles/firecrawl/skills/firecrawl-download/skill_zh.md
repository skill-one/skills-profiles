# firecrawl下载 (以`firecrawl x download`方式调用)

> **实验性功能。** `download`命令包含在`firecrawl x`命令组下。

**前提条件：** `download`需要认证（无免密免费套餐）；无凭证时，CLI会提示交互式登录。

首先将网站原点映射以发现页面，然后将每个页面抓取到`.firecrawl/`下的嵌套目录中。使用`--include-paths`将非根URL限定在一个部分。自动运行时始终传递`-y`——否则命令会打开交互式向导并阻塞在提示符上。

## 快速入门

```bash
# 带截图
firecrawl x download https://docs.example.com --screenshot --limit 20 -y

# 多种格式（每页每个格式保存为独立文件）
firecrawl x download https://docs.example.com --format markdown,links --screenshot --limit 20 -y
# 创建每页文件：index.md + links.txt + screenshot.png

# 过滤特定部分
firecrawl x download https://docs.example.com --include-paths "/features,/sdks" -y

# 跳过翻译
firecrawl x download https://docs.example.com --exclude-paths "/zh,/ja,/fr,/es,/pt-BR" -y
```

运行`firecrawl x download --help`获取完整选项列表，包括`download`支持的抓取选项。

**完成条件：** 命令成功退出且`.firecrawl/`下存在预期文件。

## 参见

- [firecrawl-map](../firecrawl-map/SKILL.md) — 仅发现URL而不下载
- [firecrawl-scrape](../firecrawl-scrape/SKILL.md) — 抓取单个页面
- [firecrawl-crawl](../firecrawl-crawl/SKILL.md) — 批量提取为JSON（非本地文件）
- [firecrawl-build-scrape](https://github.com/firecrawl/skills/tree/main/skills/build/firecrawl-build-scrape) — 将批量提取构建为应用程序而不是在此处运行
