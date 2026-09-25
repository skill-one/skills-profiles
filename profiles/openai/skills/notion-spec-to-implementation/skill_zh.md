# 规范到实现的转换

将 Notion 规范转换为关联的实施计划、任务和持续状态更新。

## 快速入门
1) 使用 `Notion:notion-search` 定位规范，然后使用 `Notion:notion-fetch` 获取它。
2) 使用 `reference/spec-parsing.md` 解析需求和模糊点。
3) 使用 `Notion:notion-create-pages` 创建计划页面（选择模板：快速或完整）。
4) 找到任务数据库，确认架构，然后使用 `Notion:notion-create-pages` 创建任务。
5) 链接规范 ↔ 计划 ↔ 任务；使用 `Notion:notion-update-page` 保持状态更新。

## 工作流

### 0) 如果任何 MCP 调用因 Notion MCP 未连接而失败，暂停并设置它：
1. 添加 Notion MCP：
   - `codex mcp add notion --url https://mcp.notion.com/mcp`
2. 启用远程 MCP 客户端：
   - 在 `config.toml` 中设置 `[features].rmcp_client = true` **或者** 运行 `codex --enable rmcp_client`
3. 使用 OAuth 登录：
   - `codex mcp login notion`

登录成功后，用户需要重新启动 codex。你应该完成你的回答，并告诉他们，当他们再次尝试时，他们可以继续步骤 1。

### 1) 定位并阅读规范
- 首先搜索 (`Notion:notion-search`)；如果有多个结果，询问用户使用哪个。
- 获取页面 (`Notion:notion-fetch`) 并扫描需求、验收标准、约束和优先级。参考 `reference/spec-parsing.md` 中的提取模式。
- 在继续之前，在澄清部分捕获差距/假设。

### 2) 选择计划深度
- 简单变更 → 使用 `reference/quick-implementation-plan.md`。
- 多阶段功能/迁移 → 使用 `reference/standard-implementation-plan.md`。
- 通过 `Notion:notion-create-pages` 创建计划，包括：概述、关联规范、需求摘要、阶段、依赖项/风险和成功标准。链接回规范。

### 3) 创建任务
- 找到任务数据库 (`Notion:notion-search` → `Notion:notion-fetch` 确认数据源和所需属性)。参考 `reference/task-creation.md` 中的模式。
- 将任务大小调整为 1-2 天。使用 `reference/task-creation-template.md` 作为内容（背景、目标、验收标准、依赖项、资源）。
- 设置属性：标题/动作动词、状态、优先级、与规范和计划的关联、如果提供，截止日期/故事点/分配者。
- 使用数据库的 `data_source_id` 通过 `Notion:notion-create-pages` 创建页面。

### 4) 链接工件
- 计划链接到规范；任务链接到计划和规范。
- 可选地使用 `Notion:notion-update-page` 更新规范，添加一个指向计划和任务的“实施”部分。

### 5) 跟踪进度
- 使用 `reference/progress-tracking.md` 中的节奏。
- 使用 `reference/progress-update-template.md` 发布更新；使用 `reference/milestone-summary-template.md` 关闭阶段。
- 保持计划/任务中的检查清单和状态字段同步；记录阻塞项和决策。

## 参考资料和示例
- `reference/` — 解析模式、计划/任务模板、进度节奏（例如，`spec-parsing.md`、`standard-implementation-plan.md`、`task-creation.md`、`progress-tracking.md`）。
- `examples/` — 端到端演练（例如，`ui-component.md`、`api-feature.md`、`database-migration.md`）。
