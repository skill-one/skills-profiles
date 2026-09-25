# Firecrawl Build Interact

当 `/scrape` 功能不足，因为该功能需要对页面进行操作时，使用此内容。

## 使用场景

- 内容仅在点击、输入或导航后才出现
- 该功能需要表单、分页、筛选或多步骤流程
- 抓取后，产品必须保持在相同的浏览器上下文中

## 默认建议

- 以 `/scrape` 开始，然后升级至 `/interact`。
- 将 `/interact` 的范围限定为解锁数据所需的最小浏览器工作流程。
- 仅在功能确实需要跨会话的已认证状态时才使用持久配置文件。

## 常见产品模式

- 搜索表单和分层筛选
- 分页结果集
- 需要登录才能访问的控制台或工具
- 需要先探索页面才能完成提取的流程

## 实施说明

- 当页面必须被操作（而不仅是读取）时，`/interact` 是合适的工具。
- 保持提示或操作代码与产品流程相关。
- 如果用例完全是开放式的浏览器自动化，请评估浏览器沙箱是否为更好的产品适配方案。

## 升级规则

- 如果页面可以直接读取，请保持在 [firecrawl-build-scrape](../firecrawl-build-scrape/SKILL.md)。

## 文档（事实来源）

在编写集成代码之前，请阅读您项目对应语言的事实来源页面：

- **Node / TypeScript**：[docs.firecrawl.dev/agent-source-of-truth/node](https://docs.firecrawl.dev/agent-source-of-truth/node)
- **Python**：[docs.firecrawl.dev/agent-source-of-truth/python](https://docs.firecrawl.dev/agent-source-of-truth/python)
- **Rust**：[docs.firecrawl.dev/agent-source-of-truth/rust](https://docs.firecrawl.dev/agent-source-of-truth/rust)
- **Java**：[docs.firecrawl.dev/agent-source-of-truth/java](https://docs.firecrawl.dev/agent-source-of-truth/java)
- **Elixir**：[docs.firecrawl.dev/agent-source-of-truth/elixir](https://docs.firecrawl.dev/agent-source-of-truth/elixir)
- **cURL / REST**：[docs.firecrawl.dev/agent-source-of-truth/curl](https://docs.firecrawl.dev/agent-source-of-truth/curl)

## 相关链接

- [firecrawl-build](../firecrawl-build/SKILL.md)
- [firecrawl-build-scrape](../firecrawl-build-scrape/SKILL.md)
- [firecrawl-build-search](../firecrawl-build-search/SKILL.md)
