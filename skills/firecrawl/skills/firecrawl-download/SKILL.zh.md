---
name: firecrawl-download
description: 将网站或部分保存为本地文件（Markdown、截图）。用于“下载网站”、离线文档或参考的本地副本。
---

# firecrawl 下载 (以 `firecrawl x download` 调用)

> **实验性功能。** `download` 命令在 `firecrawl x` 命令组下提供。

**前提条件：** `download` 需要认证（无免密钥免费套餐）；无凭证时，CLI 会提示交互式登录。

首先将网站原点映射以发现页面，然后将每个页面抓取到 `.firecrawl/` 下嵌套的目录中。使用 `--include-paths` 将非根 URL 限定在一个区域。自动运行始终传递 `-y` — 无此参数时，命令会打开交互式向导并阻塞在提示。

## 快速入门

```bash
# 带截图
firecrawl x download https://docs.example.com --screenshot --limit 20 -y

# 多种格式（每页每个格式保存为独立文件）
firecrawl x download https://docs.example.com --format markdown,links --screenshot --limit 20 -y
# 创建每页：index.md + links.txt + screenshot.png

# 过滤到特定区域
firecrawl x download https://docs.example.com --include-paths "/features,/sdks" -y

# 跳过翻译
firecrawl x download https://docs.example.com --exclude-paths "/zh,/ja,/fr,/es,/pt-BR" -y
```

运行 `firecrawl x download --help` 获取完整选项列表，包括 `download` 支持的抓取选项。

**完成条件：** 命令成功退出且预期文件存在于 `.firecrawl/` 下。

## 参见

- [firecrawl-map](../firecrawl-map/SKILL.md) — 仅发现 URL 而不下载
- [firecrawl-scrape](../firecrawl-scrape/SKILL.md) — 抓取单个页面
- [firecrawl-crawl](../firecrawl-crawl/SKILL.md) — 批量提取为 JSON（非本地文件）
- [firecrawl-build-scrape](https://github.com/firecrawl/skills/tree/main/skills/build/firecrawl-build-scrape) — 将批量提取构建为应用程序而不是在此处运行
