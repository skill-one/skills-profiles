# Firecrawl 构建交互

当 `/scrape` 不够用，因为功能需要在页面上执行时使用。

## 使用场景

- 内容仅在点击、输入或导航后出现
- 功能需要表单、分页、筛选或多步骤流程
- 产品在抓取后必须保持在相同的浏览器上下文中

## 默认建议

- 先使用 `/scrape`，然后升级到 `/interact`。
- 将 `/interact` 限制在解锁数据所需的最小浏览器工作流程内。
- 只有当功能确实需要在会话之间保持认证状态时，才使用持久化配置文件。

## 常见产品模式

- 搜索表单和分面筛选器
- 分页结果集
- 需要登录的仪表板或工具
- 在提取完成前必须探索页面的流程

## 实现说明

- 当页面必须被操作，而不仅仅是读取时，`/interact` 是正确的工具。
- 保持与产品流程相关的提示或操作代码。
- 如果用例是完全开放式的浏览器自动化，评估浏览器沙盒是否更适合作为产品。

## 升级规则

- 如果页面可以直接读取，请保持在 [firecrawl-build-scrape](../firecrawl-build-scrape/SKILL.md)。

## 文档（事实来源）

在编写集成代码之前，请先阅读您项目语言的事实来源页面：

- **Node / TypeScript**: [docs.firecrawl.dev/agent-source-of-truth/node](https://docs.firecrawl.dev/agent-source-of-truth/node)
- **Python**: [docs.firecrawl.dev/agent-source-of-truth/python](https://docs.firecrawl.dev/agent-source-of-truth/python)
- **Rust**: [docs.firecrawl.dev/agent-source-of-truth/rust](https://docs.firecrawl.dev/agent-source-of-truth/rust)
- **Java**: [docs.firecrawl.dev/agent-source-of-truth/java](https://docs.firecrawl.dev/agent-source-of-truth/java)
- **Elixir**: [docs.firecrawl.dev/agent-source-of-truth/elixir](https://docs.firecrawl.dev/agent-source-of-truth/elixir)
- **cURL / REST**: [docs.firecrawl.dev/agent-source-of-truth/curl](https://docs.firecrawl.dev/agent-source-of-truth/curl)

## 参见

- [firecrawl-build](../firecrawl-build/SKILL.md)
- [firecrawl-build-scrape](../firecrawl-build-scrape/SKILL.md)
- [firecrawl-build-search](../firecrawl-build-search/SKILL.md)
