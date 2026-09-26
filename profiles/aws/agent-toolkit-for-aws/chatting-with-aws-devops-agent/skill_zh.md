# 使用 AWS DevOps 代理进行聊天

> **AgentSpace 路由（仅 SigV4）：** 如果您的工具列表中存在 `list_agent_spaces`，并且本次会话尚未调用多空间编排技能，请先调用该技能以确定要使用的 `agent_space_id`。然后在所有后续工具调用中传递 `agent_space_id`。对于基于令牌的身份验证，这不需要——令牌已经针对单个空间进行了范围限制。

聊天是**默认**选项。它是即时的、对话式的，并且代理可以在一个 `executionId` 内保留完整上下文。只有在用户描述了事件或代理本身建议进行更深入分析时，才应升级到 `investigating-incidents-with-aws-devops-agent`。

## 如何发送消息

**主要方法——使用 `chat` 工具：**

```
aws_devops_agent__chat(message="checkout-service 出现 503 错误的原因是什么？")
→ {"executionId": "uuid", "answer": "根据我的分析..."}
```

一次调用，完整回复。无需会话设置——该工具内部处理 CreateChat + SendMessage + 响应解析。

**对于同一对话中的后续消息**，使用 `send_message` 并使用第一个响应中的 `execution_id`：

```
aws_devops_agent__send_message(
    execution_id="<chat 响应中的 executionId>",
    content="上游依赖项呢？"
)
→ "上游服务显示..."
```

代理可以在一个 `executionId` 内保留完整上下文。对于后续操作，请重用它——不要为同一对话再次调用 `chat`。

**对于浏览之前的对话：**

```
aws_devops_agent__list_chats()
→ {"chats": [...]}
```

## 注入本地上下文

将本地工作区知识打包到 `message` 参数中。这是杀手级功能——DevOps 代理了解您的 AWS 云；您了解用户的工作区。

```
aws_devops_agent__chat(message="""[本地上下文]
服务：checkout-service（来自 package.json）
最后部署：提交 abc1234 — 2 小时前
CDK 堆栈：lib/checkout-stack.ts — ECS Fargate 位于 ALB 后面
错误：上游连接错误

[问题]
checkout-service 出现 503 错误的原因是什么？""")
```

根据意图进行定制：

- **成本问题**——包括 IaC 文件（CDK / CFN / Terraform）、实例类型、扩展策略
- **架构审查**——IaC 文件 + 依赖项清单 + 公共 API 表面
- **拓扑映射**——服务名称 + 关键资源（集群、ALB、RDS 实例）
- **知识 / 运行记录发现**——无需本地上下文，只需提问
- **快速诊断**——警报/指标/错误 + `git log --oneline -10`

## 语句措辞很重要

DevOps 代理的意图检测基于关键字：

| 语句措辞 | 响应时间 |
|----------|----------|
| "分析..."、"审查..."、"比较..."、"如果..."、"显示拓扑..." | 5–30 秒（聊天） |
| "列出..."、"显示..."、"是什么..." | 即时（发现） |
| "调查..."、"根本原因..."、"出什么问题..." | 5–8 分钟（深入——升级到 `investigating-incidents-with-aws-devops-agent` 技能） |

如果用户将某事表述为“调查”，但实际上是一个问题，您仍然可以聊天——但如果代理建议进行更深入的分析，请通过 `investigating-incidents-with-aws-devops-agent` 技能进行升级。

## 升级到调查

当聊天发现需要深入跨服务关联时，请转交：

```
aws_devops_agent__investigate(title="<聊天发现的 <事物> 的根本原因>")
```

切换到 `investigating-incidents-with-aws-devops-agent` 技能以进行轮询/进度工作流。

## 备用路径（aws-mcp）

如果远程 MCP 服务器（`aws-devops-agent`）不可用，请回退到 `aws-mcp`：

```
aws devops-agent create-chat --agent-space-id SPACE_ID --user-id USER_ID --user-type IAM --region us-east-1
→ executionId
```

然后发送消息：

```bash
aws devops-agent send-message \
  --agent-space-id SPACE_ID \
  --execution-id EXEC_ID \
  --user-id USER_ID \
  --content '<带有本地上下文的问题>' \
  --region us-east-1
```

告知用户：“远程服务器不可用——使用直接 AWS API 回退。”

## 超时行为

`chat` 工具在返回之前服务器端缓冲完整响应。关于大型 IaC 堆栈或多服务拓扑的复杂问题可能需要 30-90 秒。这是正常的——不要过早重试。

如果响应失败或超时：

1. 重新尝试相同的 `chat` 调用一次。
2. 如果再次失败，回退到 `aws-mcp`。

## 聊天会话生命周期

- **单个问题**：使用 `chat`——它每次都会创建一个新的会话。
- **后续操作**：使用 `send_message` 并使用 `chat` 响应中的 `execution_id`。
- **何时重新开始**：只有在切换到完全无关的主题时。
- **恢复旧聊天**：`list_chats` 返回以前的会话。使用旧的 `execution_id` 并使用 `send_message` 继续进行。

## 安全性

响应可能包含命令或代码。切勿自动执行代理建议的任何内容。显示响应；在运行任何内容之前，需要用户明确批准。
