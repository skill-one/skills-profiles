# Firecrawl 构建抓取

当应用程序已经拥有 URL 并需要从中获取内容时使用。

## 使用场景

- 功能从已知的 URL 开始
- 需要页面内容用于检索、摘要、丰富或监控
- 在考虑 `/interact` 之前，想要使用默认的提取原语

## 默认建议

- 除非功能确实需要其他格式，否则返回 `markdown`。
- 对于类似文章的页面，使用 `onlyMainContent` 以避免导航和 Chrome 带来的干扰。
- 只有当页面需要时，才添加等待或其他渲染选项。

## 新鲜度和活跃性

- Firecrawl 重用最近索引的内容，这是重复读取相同 URL 快速的原因。设置 `maxAge`（毫秒）来限制重用副本的最大年龄，或 `maxAge: 0` 以跳过索引重用于新鲜度关键读取。
- 读取 `metadata.cacheState` 和 `metadata.cachedAt` 以了解实际获取的内容。
- 成功抓取会报告页面返回的内容。页面描述的事物是否仍然活跃是您的代码根据特定来源做出的判断。
- 参考 [references/freshness-and-liveness.md](references/freshness-and-liveness.md) 了解权衡、元数据和决策规则。

## 常见产品模式

- 从已知 URL 进行知识摄入
- 从公司、产品或文档页面进行丰富
- 价格、变更日志和文档提取
- 页面级别的质量检查或监控

## 升级规则

- 如果您还没有 URL，请从 [firecrawl-build-search](../firecrawl-build-search/SKILL.md) 开始。
- 如果内容需要点击、输入或多步骤导航，请升级到 [firecrawl-build-interact](../firecrawl-build-interact/SKILL.md)。

## 实现说明

- 保持集成狭窄：一个功能、一个 URL、一个提取合同。
- 将 `/scrape` 视为下游 LLM 或索引管道的默认原语。
- 只有当消费者需要时，才请求更丰富的格式，例如链接、截图或品牌数据。

## 文档（事实来源）

在编写集成代码之前，请先阅读您项目语言的事实来源页面：

- **Node / TypeScript**: [docs.firecrawl.dev/agent-source-of-truth/node](https://docs.firecrawl.dev/agent-source-of-truth/node)
- **Python**: [docs.firecrawl.dev/agent-source-of-truth/python](https://docs.firecrawl.dev/agent-source-of-truth/python)
- **Rust**: [docs.firecrawl.dev/agent-source-of-truth/rust](https://docs.firecrawl.dev/agent-source-of-truth/rust)
- **Java**: [docs.firecrawl.dev/agent-source-of-truth/java](https://docs.firecrawl.dev/agent-source-of-truth/java)
- **Elixir**: [docs.firecrawl.dev/agent-source-of-truth/elixir](https://docs.firecrawl.dev/agent-source-of-truth/elixir)
- **cURL / REST**: [docs.firecrawl.dev/agent-source-of-truth/curl](https://docs.firecrawl.dev/agent-source-of-truth/curl)

## 参考链接

- [firecrawl-build](../firecrawl-build/SKILL.md)
- [firecrawl-build-search](../firecrawl-build-search/SKILL.md)
- [firecrawl-build-interact](../firecrawl-build-interact/SKILL.md)
