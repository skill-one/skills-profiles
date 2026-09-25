# 会议智能

通过提取 Notion 上下文、定制议程/预习材料，并使用 Codex 研究来丰富会议内容，从而高效准备会议。

## 快速入门
1) 确认会议目标、参会人员、日期/时间以及需要做出的决策。
2) 收集背景信息：使用 `Notion:notion-search` 进行搜索，然后使用 `Notion:notion-fetch` 获取（之前的笔记、规格、OKRs、决策）。
3) 通过 `reference/template-selection-guide.md` 选择合适的模板（状态、决策、规划、回顾、一对一、头脑风暴）。
4) 在 Notion 中起草议程/预习材料，使用 `Notion:notion-create-pages` 嵌入源链接和负责人/时间框。
5) 使用 Codex 研究进行丰富（行业洞察、基准、风险），并在计划变化时使用 `Notion:notion-update-page` 更新页面。

## 工作流程
### 0) 如果任何 MCP 调用失败是因为 Notion MCP 未连接，请暂停并设置：
1. 添加 Notion MCP：
   - `codex mcp add notion --url https://mcp.notion.com/mcp`
2. 启用远程 MCP 客户端：
   - 在 `config.toml` 中设置 `[features].rmcp_client = true` **或** 运行 `codex --enable rmcp_client`
3. 使用 OAuth 登录：
   - `codex mcp login notion`

登录成功后，用户需要重启 codex。请完成您的回答，并告诉他们，这样当他们再次尝试时可以继续执行步骤 1。

### 1) 收集输入
- 询问目标、期望成果/决策、参会人员、时长、日期/时间以及之前的材料。
- 在 Notion 中搜索相关文档、过去的笔记、规格和行动项 (`Notion:notion-search`)，然后获取关键页面 (`Notion:notion-fetch`)。
- 提前记录障碍/风险和开放性问题。

### 2) 选择格式
- 状态/更新 → 状态模板。
- 决策/批准 → 决策模板。
- 规划（冲刺/项目）→ 规划模板。
- 回顾/反馈 → 回顾模板。
- 一对一 → 一对一模板。
- 想法构思 → 头脑风暴模板。
- 使用 `reference/template-selection-guide.md` 确认。

### 3) 构建议程/预习材料
- 从 `reference/` 中的选定模板开始，调整部分（背景、目标、议程、每项负责人/时间、决策、风险、预习要求）。
- 包含提取的 Notion 页面链接和任何必要的预习材料。
- 为每个议程项目分配负责人；标出时间框和预期输出。

### 4) 使用研究进行丰富
- 在合适的地方添加简洁的 Codex 研究：市场/行业事实、基准、风险、最佳实践。
- 使用源链接引用声明；区分事实与观点。

### 5) 最终确定并分享
- 添加后续步骤和负责人。
- 如果出现任务，请在相关的 Notion 数据库中创建/链接任务。
- 当细节变化时，通过 `Notion:notion-update-page` 更新页面；如果多次编辑，保留简短的变更日志。

## 参考资料和示例
- `reference/` — 模板选择器和会议模板（例如，`template-selection-guide.md`、`status-update-template.md`、`decision-meeting-template.md`、`sprint-planning-template.md`、`one-on-one-template.md`、`retrospective-template.md`、`brainstorming-template.md`）。
- `examples/` — 端到端会议准备（例如，`executive-review.md`、`project-decision.md`、`sprint-planning.md`、`customer-meeting.md`）。
