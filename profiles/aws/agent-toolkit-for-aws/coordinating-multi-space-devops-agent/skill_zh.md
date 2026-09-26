# 查询多个 AgentSpaces

## 预检查

如果 `aws_devops_agent__list_agent_spaces` **不在** 可用工具中，则远程 MCP 服务器未连接。建议用户询问“帮助我设置 AWS DevOps Agent”，以便 `setup-devops-agent` 技能自动加载。

## 前置条件：需要 SigV4 身份验证

多空间路由需要 **SigV4 身份验证** — 带宽令牌仅限于单个 AgentSpace，无法路由到其他空间。

许多真实团队运行 **多个 AgentSpace** — 通常包括一个生产空间、一个预发布空间和一个专门用于“知识”的空间，该空间包含跨账户共享的运行手册。每个空间都有自己的一组关联 AWS 账户、运行手册和历史记录。

该技能是路由的核心。当用户配置了多个空间，或者问题确实涉及多个账户时，使用该技能。

## 发现空间

```
aws_devops_agent__list_agent_spaces()
→ {"agentSpaces": [{"agentSpaceId": "as-abc123", "name": "prod"}, ...]}
```

如果只返回一个空间，则此技能不适用 — 直接使用 `chatting-with-aws-devops-agent` 或 `investigating-incidents-with-aws-devops-agent`（无需 `agent_space_id`）。

如果返回多个空间，请判断用户的问题是否：

| 问题类型 | 策略 |
|---------|------|
| 限于单个环境（“prod 出现故障”） | 单个空间 — 选择匹配的空间 |
| 跨环境（“比较 prod 和 staging”） | **并行** — 查询每个空间，综合结果 |
| 通用知识（“我们有哪些 ECS 运行手册？”） | 如果空间名称为“知识”，则路由到该空间 |
| 模糊（“我们的服务响应缓慢”） | **询问用户** 哪个环境，不要猜测 |

## 会话级路由记忆

如果用户本地存储了路由指南（例如 `.claude/aws-agents-for-devsecops.md`、`AGENTS.md` 或项目特定笔记），则在会话开始时读取一次，并将其作为后续对话的路由表。预期格式：

```markdown
| 空间 | AWS 配置文件 | Agent Space ID | 用途 |
|-----|--------------|----------------|------|
| prod | acme-prod    | as-abc123      | 生产问题、面向客户的服务的故障排除 |
| stage | acme-stage   | as-def456      | 预发布验证、集成测试 |
| kb   | acme-shared  | as-ghi789      | 共享运行手册、跨账户知识 |
```

如果没有指南，则运行发现：

1. `aws_devops_agent__list_agent_spaces()` → 获取所有空间。
2. 对于每个空间：`aws_devops_agent__chat(message="总结你访问的 AWS 账户、服务和运行手册。", agent_space_id="<SPACE_ID>")` → 获取一段摘要。
3. 提议将路由指南写入项目（例如 `.claude/aws-agents-for-devsecops.md`、`AGENTS.md` 或项目特定笔记），以便未来会话跳过发现。

## 模式 A — 并行查询，一个综合答案

当用户需要比较时使用：比较 prod 和 staging 的错误率、此问题是否同时发生在两个账户中、跨所有环境审计成本。

```
# 1. 使用环境特定上下文并行查询每个空间
aws_devops_agent__chat(message="<question> | env=prod | <prod IaC 上下文>", agent_space_id="PROD_ID")
→ {"executionId": "...", "answer": "..."}

aws_devops_agent__chat(message="<question> | env=stage | <stage IaC 上下文>", agent_space_id="STAGE_ID")
→ {"executionId": "...", "answer": "..."}

# 2. 本地综合 — 提供并排摘要，而不是两个单独的输出
```

**不要直接粘贴两个响应。** 读取两个响应，识别相同和不同之处，并告诉用户 *差异* — 这才是价值所在。

## 模式 B — 知识查找，然后按空间执行

当某个空间包含的运行手册/知识会指导其他空间的工作时使用。

```
# 1. 首先询问知识空间
aws_devops_agent__chat(
    message="我们标准的 ECS 503 错误运行手册是什么？",
    agent_space_id="KB_ID"
)
→ {"answer": "<运行手册文本>"}

# 2. 在目标环境中应用该运行手册
aws_devops_agent__investigate(
    title="checkout-service 上的 ECS 503 错误。[来自知识空间的运行手册] <运行手册文本> [本地上下文] ...",
    agent_space_id="PROD_ID",
    priority="HIGH"
)
```

DevOps Agent 不会在空间之间共享状态 — 你通过将知识空间的响应引用到调查的 `title` 中来桥接它。

## 模式 C — 针对单个空间的查询

当用户明确指定空间或环境时使用。

```
# 从你的路由记忆中挑选匹配的 agentSpaceId，并在调用中传递它
aws_devops_agent__chat(message="<question>", agent_space_id="<matched_space_id>")
```

如果路由不明确且用户没有说明，**询问一次** — 比射向错误账户要好。

## 模式 D — 调查不共享状态

调查是按空间进行的。如果问题涉及多个账户，可能需要 *两个* 调查：

```
aws_devops_agent__investigate(title="延迟激增 — prod 端", agent_space_id="PROD_ID", priority="HIGH")
aws_devops_agent__investigate(title="延迟激增 — stage 端", agent_space_id="STAGE_ID", priority="HIGH")
```

跟踪两个 `taskId`。轮询两个。一起展示发现。

这很少见 — 通常一个空间拥有问题。不要默认分叉。

## 不应该做什么

- **不要用每个问题轰炸所有空间。** 这很慢、很昂贵，用户必须阅读 3 倍的输出。
- **不要在不验证范围的情况下分叉。** 如果一个空间的 `description` 或记录的覆盖范围未提及相关服务，请跳过它 — 将问题发送到范围不匹配的空间通常会挂起而不是返回“我不知道。”
- **不要默认并行启动调查。** 它们每个需要 5-8 分钟。选择拥有该事件的一个空间。
- **不要在对话中无声地切换空间。** 如果后续需要不同空间，告诉用户：“切换到知识空间查找运行手册。”

## 超时指导

`chat` 工具在返回之前在服务器端缓冲完整响应。复杂的跨账户查询可能需要每个空间 30-90 秒。如果一个空间在 90 秒内未响应，很可能存在范围不匹配 — 显示消息“空间 X 在 90 秒内未响应 — 跳过（很可能范围不匹配）”并继续，而不是挂起。

## 参见

- `examples/multi-space-walkthrough.md` 用于一个完整的工作场景（prod 问题、staging 比较和知识空间运行手册查找）。
- `setup-devops-agent` 技能用于首次配置多个 AgentSpaces、AWS 配置文件和 shell 包装器。
