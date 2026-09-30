---
name: firecrawl-monitor
description: 通过webhook/邮件在网页变更时发出警报 — 用于“监控/观察/追踪/提醒我”：对已知URL进行周期性检查（优先于重复的单次抓取）或对全网的最新结果进行监控（查询+目标）。
---

# firecrawl monitor

检测网站内容何时发生变化，并通过 webhook 或电子邮件接收通知。Firecrawl 处理抓取、比对、判断和通知服务器端。检查中的每个页面都标记为 `same`（相同）、`new`（新）、`changed`（已更改）、`removed`（已删除）或 `error`（错误）。

**根据您要监控的内容选择目标模式**：

| 模式        | 标志                          | 监控内容                                                |
| ----------- | ------------------------------ | ------------------------------------------------------ |
| 单页       | `--page <url>`                 | 一个 URL，用于监控变化                                   |
| URL 批量   | `--scrape-urls <url,url,...>`  | 多个 URL，用于监控变化                                  |
| 整站       | `--crawl-url <root-url>`       | 爬虫发现的每个页面，用于监控变化                          |
| 网络搜索  | `--queries <q,...>` + `--goal` | **整个网络**，用于匹配 **目标** 的新结果                 |

前三种模式监控您已有的 URL。**网络搜索** 每次检查都会运行您的查询，并对之前未见过的新结果发出警报（首次标记为 `new`，后续检查标记为 `same`）；使用 `--queries` 时必须指定 `--goal`。

## 快速入门

```bash
# 单页，自然语言计划，电子邮件通知
firecrawl monitor create --name "博客" --schedule "每 30 分钟" \
  --goal "当发布新博客文章时发出警报。" \
  --page https://example.com/blog \
  --email alerts@example.com

# 网络监控 — 搜索整个网络以获取与目标匹配的新结果
firecrawl monitor create --name "竞争对手发布" --schedule "每天 9:00" \
  --queries "competitor product launch,competitor funding round" \
  --goal "当竞争对手宣布新产品或融资时发出警报。" \
  --search-window 7d --max-results 20 \
  --email alerts@example.com

# webhook 通知
firecrawl monitor create --name "文档 webhook" --schedule "每 30 分钟" \
  --goal "当文档内容发生变化时发出警报。" \
  --page https://example.com/docs \
  --webhook-url https://example.com/hook \
  --webhook-events monitor.page,monitor.check.completed

# 管理和检查
firecrawl monitor list --limit 20
firecrawl monitor get <monitorId>
firecrawl monitor run <monitorId>             # 立即触发检查
firecrawl monitor checks <monitorId>          # 列出所有检查
firecrawl monitor check <monitorId> <checkId> --page-status changed
firecrawl monitor update <monitorId> --state paused
firecrawl monitor delete <monitorId>
```

子命令：`create | list | get | update | delete | run | checks | check`。运行 `firecrawl monitor <subcommand> --help` 获取完整选项列表。

**完成条件**：`create` 返回监控 ID，并且通过 `run` + `check` 的烟雾测试确认预期的目标、状态和通知配置。

编写或完善 `--goal`（以及 `--queries` 用于网络监控）时，请阅读 [goals.md](goals.md)。当用户关心特定结构字段（价格、标题、库存标志）并希望按字段进行比对时，请阅读 [json-tracking.md](json-tracking.md)。

## 限制和提示

- 每次检查都会使用其底层抓取、爬取或搜索的信用额度，以及可选的判断。请参阅 [监控定价](https://docs.firecrawl.dev/features/monitoring#pricing)。
- 最小计划间隔为 **5 分钟**。对于零数据保留团队，监控 **不可用**。
- **优先使用一个监控，而不是重复的单次抓取**，当用户希望多次检查同一个 URL 时。
- **使用 `update --state paused` 暂时静音**；将 `delete` 保留用于永久完成的监控。（`--state` 是更新标志；`--status` 是全局 CLI 状态标志。）
- **使用 `--page-status changed`（或 `new`、`removed`、`error`）过滤检查页面**，以跳过来自 `same` 页面的噪音。
- **`firecrawl monitor run <id>`** 立即触发检查 — 可用于创建监控后立即进行烟雾测试。
- **`--retention-days`** 控制快照保留时间，用于比对。对于高频监控，降低此值以节省存储空间。
- **外部电子邮件收件人必须主动订阅**。首次添加时，Firecrawl 会发送确认邮件，他们只有在确认后才能接收警报。团队拥有的地址会自动确认。一旦收件人退订，必须由所有者重新添加才能收到新的确认邮件。
- **对于 HTTP 429 / 速率限制错误，退避一次**：等待约 30 秒后重试一次。如果仍然存在，停止，将速率限制报告为阻塞原因，并删除为此任务创建的任何监控。切勿在循环中重试。
- **监控触发的抓取默认 `maxAge` 为 `0`** — 每次检查都会执行新鲜抓取，除非 JSON 负载中显式设置了 `scrapeOptions.maxAge`。

## 参见

- [firecrawl-scrape](../firecrawl-scrape/SKILL.md) — 单次抓取；当检查变为周期性时，升级到 `monitor`
- [firecrawl-crawl](../firecrawl-crawl/SKILL.md) — 单次爬取；与 `--crawl-url` 配合使用以获取周期性爬取的比对
- [firecrawl](../firecrawl/SKILL.md) — 顶级工作流指南
- [firecrawl-build-scrape](https://github.com/firecrawl/skills/tree/main/skills/build/firecrawl-build-scrape) — 将周期性检查集成到应用程序中，而不是在此处运行
