# 研究 & 文档

提取相关的 Notion 页面，整合研究成果，并发布清晰的简报或报告（附带引用和来源链接）。

## 快速入门
1) 使用目标查询通过 `Notion:notion-search` 找到来源；与用户确认范围。
2) 通过 `Notion:notion-fetch` 获取页面；记录关键部分并捕获引用（`reference/citations.md`）。
3) 使用 `reference/format-selection-guide.md` 选择输出格式（简报、摘要、比较、综合报告）。
4) 使用匹配的模板（快速、摘要、比较、综合）通过 `Notion:notion-create-pages` 在 Notion 中起草。
5) 链接来源并添加参考文献/引用部分；使用 `Notion:notion-update-page` 随新信息到达而更新。

## 工作流程
### 0) 如果任何 MCP 调用因 Notion MCP 未连接而失败，暂停并设置它：
1. 添加 Notion MCP：
   - `codex mcp add notion --url https://mcp.notion.com/mcp`
2. 启用远程 MCP 客户端：
   - 在 `config.toml` 中设置 `[features].rmcp_client = true` **或** 运行 `codex --enable rmcp_client`
3. 使用 OAuth 登录：
   - `codex mcp login notion`

登录成功后，用户将不得不重新启动 codex。你应该完成你的回答，并在他们再次尝试时告诉他们可以继续步骤 1。

### 1) 收集来源
- 首先搜索（`Notion:notion-search`）；如果出现多个结果，请要求用户确认并细化查询。
- 获取相关页面（`Notion:notion-fetch`），浏览事实、指标、声明、约束和日期。
- 跟踪每个来源的 URL/ID 以供后续引用；对于关键事实，优先使用直接引用。

### 2) 选择格式
- 快速阅读 → 快速简报。
- 单主题深入 → 研究摘要。
- 选项权衡 → 比较。
- 深入研究/执行就绪 → 综合报告。
- 查看 `reference/format-selection-guide.md` 了解何时选择每个格式。

### 3) 整合
- 写作前列提纲；按主题/问题分组研究结果。
- 使用来源 ID 记录证据；标记空白或矛盾之处。
- 留意用户目标（决策、摘要、计划、建议）。

### 4) 创建文档
- 在 `reference/` 中选择匹配的模板（简报、摘要、比较、综合）并进行调整。
- 使用 `Notion:notion-create-pages` 创建页面；包括标题、摘要、关键发现、支持证据以及在相关情况下添加建议/下一步行动。
- 添加内联引用和参考文献部分；链接回来源页面。

### 5) 最终化 & 交接
- 添加亮点、风险和开放问题。
- 如果用户需要后续行动，在页面中创建任务或清单；如果适用，链接任何任务数据库条目。
- 使用 `Notion:notion-update-page` 分享简短的变更日志或状态时更新。

## 参考文献 & 示例
- `reference/` — 搜索策略、格式选择、模板和引用规则（例如，`advanced-search.md`、`format-selection-guide.md`、`research-summary-template.md`、`comparison-template.md`、`citations.md`）。
- `examples/` — 端到端演练（例如，`competitor-analysis.md`、`technical-investigation.md`、`market-research.md`、`trip-planning.md`）。
