# 知识捕获

将对话和笔记转换为结构化、可链接的 Notion 页面，以便轻松重用。

## 快速入门
1) 明确要捕获的内容（决策、操作指南、常见问题解答、学习资料、文档）以及目标受众。
2) 在 `reference/` 中选择正确的数据库/模板（团队维基、操作指南、常见问题解答、决策日志、学习资料、文档）。
3) 使用 `Notion:notion-search` → `Notion:notion-fetch` 从 Notion 中获取任何先前的上下文（用于更新/链接的现有页面）。
4) 使用 `Notion:notion-create-pages` 并使用数据库的架构起草页面；包括摘要、背景、来源链接和标签/负责人。
5) 从中心页面和相关记录中链接；使用 `Notion:notion-update-page` 更新状态/负责人，随着来源的演变。

## 工作流程
### 0) 如果任何 MCP 调用因 Notion MCP 未连接而失败，暂停并设置它：
1. 添加 Notion MCP：
   - `codex mcp add notion --url https://mcp.notion.com/mcp`
2. 启用远程 MCP 客户端：
   - 在 `config.toml` 中设置 `[features].rmcp_client = true` **或** 运行 `codex --enable rmcp_client`
3. 使用 OAuth 登录：
   - `codex mcp login notion`

登录成功后，用户需要重启 codex。你应该完成你的回答，并告诉他们，这样当他们再次尝试时，可以继续步骤 1。

### 1) 定义捕获内容
- 询问目的、受众、时效性，以及这是新内容还是更新。
- 确定内容类型：决策、操作指南、常见问题解答、概念/维基条目、学习/笔记、文档页面。

### 2) 定位目标位置
- 使用 `reference/*-database.md` 指南选择正确的数据库；确认所需属性（标题、标签、负责人、状态、日期、关系）。
- 如果有多个候选数据库，询问用户使用哪个；否则，在主要的维基/文档数据库中创建。

### 3) 提取和结构化
- 从对话中提取事实、决策、行动和理由。
- 对于决策，记录备选方案、理由和结果。
- 对于操作指南/文档，捕获步骤、先决条件、链接到资源/代码，以及边缘情况。
- 对于常见问题解答，以问答形式表达，简洁的答案并链接到更深入的文档。

### 4) 在 Notion 中创建/更新
- 使用 `Notion:notion-create-pages` 并使用正确的 `data_source_id`；设置属性（标题、标签、负责人、状态、日期、关系）。
- 使用 `reference/` 中的模板来结构化内容（部分标题、检查清单）。
- 如果更新现有页面，通过 `Notion:notion-update-page` 获取然后编辑。

### 5) 链接和展示
- 添加关系/反向链接到中心页面、相关规范/文档和团队。
- 为未来的读者添加简短的摘要/变更日志。
- 如果有后续任务，在相关数据库中创建任务并链接它们。

## 参考资料和示例
- `reference/` — 数据库架构和模板（例如，`team-wiki-database.md`、`how-to-guide-database.md`、`faq-database.md`、`decision-log-database.md`、`documentation-database.md`、`learning-database.md`、`database-best-practices.md`）。
- `examples/` — 实践中的捕获模式（例如，`decision-capture.md`、`how-to-guide.md`、`conversation-to-faq.md`）。
