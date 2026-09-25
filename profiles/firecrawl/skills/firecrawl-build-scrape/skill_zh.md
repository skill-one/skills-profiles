# Firecrawl Build Scrape

当应用程序已经拥有目标 URL 并需要获取单页内容时使用此功能。

## 使用时机

- 功能基于已知 URL 启动
- 需要页面内容进行检索、摘要、丰富或监控
- 在考虑 `/interact` 之前，使用默认的提取原语

## 默认建议

- 除非该功能确实需要其他格式，否则返回 `markdown`。
- 对于导航和界面元素会增加干扰的类似文章页面，使用 `onlyMainContent`。
- 仅当页面需要时，添加等待或其他渲染选项。

## 新鲜度与活性

- Firecrawl 复用最近索引的内容，这使得对同一 URL 的重复读取速度很快。设置 `maxAge`（毫秒）来限制复用副本的允许最大年龄，或使用 `maxAge: 0` 跳过索引复用以确保新鲜度关键读取。
- 读取 `metadata.cacheState` 和 `metadata.cachedAt` 以查看您实际获取的内容。
- 成功的抓取会报告页面返回的内容。页面所描述的内容是否仍然活跃，是由您的代码针对数据源做出的特定判断。
- 请参阅 [references/freshness-and-liveness.md](references/freshness-and-liveness.md) 以了解权衡、元数据以及决策规则。

## 常见产品模式

- 从已知 URL 进行知识摄入
- 从公司、产品或文档页面进行丰富
- 提取定价、更新日志和文档
- 页面级别的质量检查或监控

## 升级规则

- 如果您还没有 URL，请从 [firecrawl-build-search](../firecrawl-build-search/SKILL.md) 开始。
- 如果内容需要点击、输入或多步导航，请升级至 [firecrawl-build-interact](../firecrawl-build-interact/SKILL.md)。

## 实施说明

- 保持集成范围精简：一个功能、一个 URL、一个提取契约。
- 将 `/scrape` 视为下游 LLM 或索引管线的默认原语。
- 仅当消费者需要时，请求更丰富的格式，例如链接、截图或品牌数据。

## 文档（事实来源）

在编写集成代码之前，请阅读您项目语言的事实来源页面：

- **Node / TypeScript**：[docs.firecrawl.dev/agent-source-of-truth/node](https://docs.firecrawl.dev/agent-source-of-truth/node)
- **Python**：[docs.firecrawl.dev/agent-source-of-truth/python](https://docs.firecrawl.dev/agent-source-of-truth/python)
- **Rust**：[docs.firecrawl.dev/agent-source-of-truth/rust](https://docs.firecrawl.dev/agent-source-of-truth/rust)
- **Java**：[docs.firecrawl.dev/agent-source-of-truth/java](https://docs.firecrawl.dev/agent-source-of-truth/java)
- **Elixir**：[docs.firecrawl.dev/agent-source-of-truth/elixir](https://docs.firecrawl.dev/agent-source-of-truth/elixir)
- **cURL / REST**：[docs.firecrawl.dev/agent-source-of-truth/curl](https://docs.firecrawl.dev/agent-source-of-truth/curl)

## 相关链接

- [firecrawl-build](../firecrawl-build/SKILL.md)
- [firecrawl-build-search](../firecrawl-build-search/SKILL.md)
- [firecrawl-build-interact](../firecrawl-build-interact/SKILL.md)
