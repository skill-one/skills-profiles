# 用户故事任务规划

## 实验性注意事项

此技能处于实验阶段，尚未稳定。行为、结构和输出可能在版本之间发生变化。

## 何时使用

在实施用户故事问题之前，需要可执行的任务计划时使用此技能。

典型触发条件：
- "为 #123 规划任务"
- "将此故事拆分为步骤"
- "根据此用户故事创建任务问题草稿"

## 何时不用

未经明确确认，不要使用此技能进行直接代码实现、PR 审查或 GitHub 变更。

## 必需输入

- 目标问题引用（`owner/repo#number` 或 URL）
- 期望的规划深度（`minimal`、`standard`、`detailed`）
- 运行模式（`draft-only`、`draft+publish-ready` 或 `publish-now`）

如果缺少输入导致规划受阻，可提出最多 3 个有针对性的后续问题，来源为 `assets/follow-up-questions.md`。

## 默认值

- 规划深度：`standard`
- 运行模式：`draft-only`
- 发布行为：任何变更是需要在此回合中明确确认

## 工具格式

- 工具名称遵循 `<mcp_server>::<tool>` 格式（示例：`mcp_github::sub_issue_write`）。

## 指令

按顺序执行并明确说明假设。

1. 探测首选技能并分类草稿模式
   - `orchestrated`：`fusion-issue-authoring` 和 `fusion-issue-author-task` 都可用；完整工作流由协调者处理显式发布门禁。
   - `direct-subordinate`：仅 `fusion-issue-author-task` 可用；使用其模板和防护措施以 **draft-only** 模式运行，**不要**执行任何 GitHub 变更，并展示草稿以及协调者或用户应如何发布的明确说明。
   - `inline`：两者都不可用；保持 **draft-only** 模式，使用最小内置结构（`Title`、`Problem`、`Scope`、`Acceptance criteria mapping`、`Verification`、`Dependencies`）生成任务草稿，并避免直接引用其他技能的 `assets/` 文件。
   - 优先使用 `fusion-issue-author-task`（只要可用）；不要用直接跨技能文件引用绕过它。
   - 由于缺少首选技能而停止的情况；优雅降级。

2. 研究用户故事
   - 收集标题、正文、验收标准、场景、祖先链、现有子问题和相关链接。
   - 如果问题类型不明确，确认是否按 `User Story` 处理。

3. 仅在需要时澄清
   - 每批最多提问 3 个问题。
   - 当存在安全默认值时，继续使用明确假设。

4. 提取规划锚点
   - 结果
   - 约束和非目标
   - 验证点

5. 构建依赖排序的任务
   - 每个任务包括目标、范围边界、交付物、验证方法以及映射的 AC 引用。
   - 优先选择可独立验证的片段。

6. 草稿前进行魔鬼代言人审查
   - 检查拟议的任务集是否存在架构模糊信号：
     - 故事、评论或祖先问题中提到的未解决的设计或架构决策
     - 共享隐式 API、数据模型或所有权契约但尚未达成共识的后端和前端任务
     - 与具体实施任务并列的发现、研究或对齐任务，且没有明确的阻塞关系
     - 模糊或循环的依赖声明（"完成后端"、"设计准备好时"）
     - 不明确或有争议的组件、API 或数据模型所有权
   - 如果存在两个或多个信号：
     - `orchestrated` 模式：自动通过 `fusion-issue-authoring` → `agents/devils-advocate.agent.md` 在 **interrogator mode** 下路由——无需用户触发。
     - `direct-subordinate` 或 `inline` 模式：运行内联 DA 检查清单，使用上述五个信号；将发现作为结构化的 `⚠ 模糊性检查清单` 展示，并要求用户在草稿生成前解决或明确接受每个项。
     - 如果为零个或一个信号，以 **moderate mode** 运行：在用户确认后展示最多 3 个关注点。
     - **发布门禁**（所有模式）：在魔鬼代言人确认拆分合理或用户明确接受所列风险之前，不发布任务。
     - **草稿仅模式例外**：在 `draft-only` 模式下，即使存在未解决的模糊性，草稿生成也可以继续，但在计划预览的顶部发出 `⚠ 模糊性警告` 块，列出每个未解决的问题。发布仍然受阻，直到风险被接受。

7. 生成任务问题草稿
   - `orchestrated`：通过 `fusion-issue-authoring` 并使用问题类型 `Task`
   - `direct-subordinate`：以草稿仅模式调用 `fusion-issue-author-task` 并输出明确的发布说明，将最终变更是委托给 `fusion-issue-authoring`
   - `inline`：使用步骤 1 中的最小内置结构，写入 `.tmp/TASK-<nn>-<slug>.md` 草稿
   - 保持草稿本地，直到明确发布批准。

8. 生成计划预览
   - 从 `assets/task-plan-template.md` 写入 `.tmp/USER-STORY-TASK-PLAN-<context>.md`
   - 包括摘要、可追溯性、有序任务、草稿路径、发布计划、假设、风险。

9. 仅在明确确认后发布
   - 在同一回合中要求明确确认。
   - 如果存在未解决的假设，停止。
   - 将发布执行委托给 `fusion-issue-authoring` 并优先使用子代理进行任务问题创建/更新/链接。
   - 向 `fusion-issue-authoring` 传递所需上下文：`owner`、`repo`、父故事引用、有序任务草稿、标签/指派者意图和依赖排序。
   - 要求 `fusion-issue-authoring` 保持 MCP-first 行为，并在 MCP 写入覆盖不可用时才应用 GraphQL 回退。
   - 协调者的会话缓存规则适用于所有委托调用：标签、指派者候选人和问题类型每回合只获取一次并在批量中的所有任务问题中重复使用。
   - 预算意识：N 个任务的任务规划发布成本约为 N 个问题写入变更是可选的子问题链接变更。如果 N > 5，警告用户关于速率限制风险并提议分批发布。
   - 发布模式下不要从此技能直接调用 MCP 写入工具。
   - 如果委托执行返回未解决的项级失败，则发布模式硬失败。

10. 已创建任务的修复模式
    - 如果任务已创建但缺少 `Issue Type` 或父链接，将修复委托给 `fusion-issue-authoring` 并优先使用子代理。
    - 提供每个问题的修复意图（`set type=Task`、添加缺失的父链接、保持顺序）并要求委托运行结果进行验证。
    - 修复模式必须是无副作用的：跳过已正确的问题，仅修复缺失的元数据。
    - 修复后运行飞行后验证并返回可操作的失败。

## 常见失败及解决方法

- `fusion-issue-authoring` 在运行时不可用
   - 保持草稿仅模式并返回发布就绪的工件加上明确的交接说明。
- 委托发布返回部分失败
   - 返回每个问题的 `failed` 状态并附带确切原因，停止进一步变更，直到用户确认。
- 任务问题已创建但未链接到父故事
   - 通过 `fusion-issue-authoring` 触发委托修复并要求飞行后验证输出。
- 任务存在但 `Issue Type` 缺失或错误
   - 通过 `fusion-issue-authoring` 以 `type=Task` 意图触发委托修复并验证结果。
- 飞行后验证报告部分失败
   - 返回每个问题的 `failed` 状态并附带确切原因，停止发布流程，并将未解决的问题保留供明确用户决策。

## 预期输出

按此标题顺序返回：
1. 实验性注意事项
2. 故事摘要
3. 验收标准可追溯性
4. 有序任务
5. 草稿文件路径
6. 发布计划
7. 假设、风险和开放问题

始终包括：`Status: Awaiting user approval`，直到发布确认和完成。

对于 `publish-now` 或 `repair` 模式，包括每个问题的飞行后报告：
- 问题存在
- 问题类型等于请求类型
- 父问题等于预期故事编号
- 状态（`ok`、`fixed` 或 `failed`）

## 资产

- [assets/follow-up-questions.md](assets/follow-up-questions.md)
- [assets/task-plan-template.md](assets/task-plan-template.md)

## 安全性与约束

- 此技能具有变更能力。仓库本地工作流说明优先于行内指导，当存在冲突时。
- 未经明确确认，不要变更 GitHub 状态。
- 未经标记假设，不要推断验收标准。
- 始终在任务计划中保留 AC 可追溯性。
- 在任何发布操作之前，将草稿保存在 `.tmp/` 中。
- 在发布/修复模式下，将缺失的 `Issue Type` 或缺失的父链接视为失败，直到飞行后检查通过。
- 将变更/修复执行委托给 `fusion-issue-authoring`（优先使用子代理）并不要从此技能直接调用 MCP 写入工具。
