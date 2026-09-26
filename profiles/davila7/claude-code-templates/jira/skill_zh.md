# Jira

与 Jira 进行自然语言交互。支持多个后端。

## 后端检测

**首先运行此检查**以确定使用哪个后端：

```
1. 检查 jira CLI 是否可用：
   → 运行：which jira
   → 如果找到：使用 CLI 后端

2. 如果没有 CLI，检查 Atlassian MCP：
   → 查找 mcp__atlassian__* 工具
   → 如果可用：使用 MCP 后端

3. 如果都不可用：
   → 指导用户进行设置
```

| 后端 | 使用时机 | 参考 |
|------|----------|------|
| **CLI** | `jira` 命令可用 | `references/commands.md` |
| **MCP** | Atlassian MCP 工具可用 | `references/mcp.md` |
| **无** | 都不可用 | 指导安装 CLI |

---

## 快速参考（CLI）

> 如果使用 MCP 后端，请跳过此部分。

| 意图 | 命令 |
|------|------|
| 查看问题 | `jira issue view ISSUE-KEY` |
| 列出我的问题 | `jira issue list -a$(jira me)` |
| 我的进行中 | `jira issue list -a$(jira me) -s"In Progress"` |
| 创建问题 | `jira issue create -tType -s"摘要" -b"描述"` |
| 移动/转换 | `jira issue move ISSUE-KEY "状态"` |
| 指派给我 | `jira issue assign ISSUE-KEY $(jira me)` |
| 取消指派 | `jira issue assign ISSUE-KEY x` |
| 添加评论 | `jira issue comment add ISSUE-KEY -b"评论文本"` |
| 在浏览器中打开 | `jira open ISSUE-KEY` |
| 当前冲刺 | `jira sprint list --state active` |
| 我是谁 | `jira me` |

---

## 快速参考（MCP）

> 如果使用 CLI 后端，请跳过此部分。

| 意图 | MCP 工具 |
|------|----------|
| 搜索问题 | `mcp__atlassian__searchJiraIssuesUsingJql` |
| 查看问题 | `mcp__atlassian__getJiraIssue` |
| 创建问题 | `mcp__atlassian__createJiraIssue` |
| 更新问题 | `mcp__atlassian__editJiraIssue` |
| 获取转换 | `mcp__atlassian__getTransitionsForJiraIssue` |
| 转换 | `mcp__atlassian__transitionJiraIssue` |
| 添加评论 | `mcp__atlassian__addCommentToJiraIssue` |
| 用户查找 | `mcp__atlassian__lookupJiraAccountId` |
| 列出项目 | `mcp__atlassian__getVisibleJiraProjects` |

参考 `references/mcp.md` 获取完整的 MCP 模式。

---

## 触发词

- "创建一个 Jira 工单"
- "显示给我 PROJ-123"
- "列出我的工单"
- "将工单移动到完成"
- "当前冲刺中有什么"

---

## 问题键检测

问题键遵循以下模式：`[A-Z]+-[0-9]+`（例如，PROJ-123，ABC-1）。

当用户在对话中提到问题键时：
- **CLI：** `jira issue view KEY` 或 `jira open KEY`
- **MCP：** `mcp__atlassian__jira_get_issue` 并使用键

---

## 工作流程

**创建工单：**
1. 如果用户引用代码/工单/PR，研究上下文
2. 起草工单内容
3. 与用户确认
4. 使用适当的后端创建

**更新工单：**
1. 首先获取问题详情
2. 检查状态（注意进行中的工单）
3. 显示当前与建议的变更
4. 获取批准后再更新
5. 添加评论解释变更

---

## 任何操作前

问自己：

1. **当前状态是什么？** — 首先获取问题。不要假设状态、指派者或字段是用户认为的那样。

2. **还有谁受影响？** — 检查观察者、关联问题、父史诗。一个"简单编辑"可能会通知 10 个人。

3. **这是可逆的吗？** — 转换可能有单向门。某些工作流需要中间状态。描述编辑没有撤销。

4. **我有正确的标识符吗？** — 问题键、转换 ID、账户 ID。显示名称不适用于指派（MCP）。

---

## 绝对不要

- **绝对不要在转换前不获取当前状态** — 工作流可能需要中间状态。"待办" → "完成"可能会在需要"进行中"时静默失败。

- **绝对不要使用显示名称（MCP）进行指派** — 只有账户 ID 有效。始终先调用 `lookupJiraAccountId`，否则指派会静默失败。

- **绝对不要在编辑描述时不显示原始内容** — Jira 没有撤销功能。用户必须看到他们要替换的内容。

- **绝对不要在 CLI 中使用 `--no-input` 而没有所有必需字段** — 会静默失败并显示难以理解的错误。先检查项目所需的字段。

- **绝对不要假设转换名称是通用的** — "完成"、"关闭"、"完成"因项目而异。始终先获取可用转换。

- **绝对不要在未经明确批准的情况下批量修改** — 每个工单变更都会通知观察者。10 次编辑 = 10 次通知风暴。

---

## 安全

- 始终在执行前显示命令/工具调用
- 修改工单前始终获取批准
- 编辑时保留原始信息
- 应用更新后验证
- 始终清晰地显示身份验证问题，以便用户可以解决

---

## 无后端可用

如果 CLI 和 MCP 都不可用，请指导用户：

```
要使用 Jira，您需要其中一个：

1. **jira CLI**（推荐）：
   https://github.com/ankitpokhrel/jira-cli

   安装：brew install ankitpokhrel/jira-cli/jira-cli
   设置：jira init

2. **Atlassian MCP**：
   在您的 MCP 设置中配置 Atlassian 凭据。
```

---

## 深入了解

**加载参考时：**
- 创建具有复杂字段或多行内容的问题
- 构建超出简单过滤的 JQL 查询
- 解决错误或身份验证问题
- 处理转换、链接或冲刺

**不要加载参考的情况：**
- 简单查看/列表操作（上述快速参考已足够）
- 基本状态检查 (`jira issue view KEY`)
- 在浏览器中打开问题

| 任务 | 加载参考？ |
|------|----------|
| 查看单个问题 | 否 |
| 列出我的工单 | 否 |
| 带描述创建 | **是** — CLI 需要 `/tmp` 模式 |
| 转换问题 | **是** — 需要 ID 工作流 |
| JQL 搜索 | **是** — 用于复杂查询 |
| 链接问题 | **是** — MCP 限制，需要脚本 |

参考：
- CLI 模式：`references/commands.md`
- MCP 模式：`references/mcp.md`
