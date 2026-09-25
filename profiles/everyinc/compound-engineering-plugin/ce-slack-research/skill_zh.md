# /ce-slack-research

在 Slack 中搜索组织背景信息，并接收解读后的研究摘要。

## 使用方法

```
/ce-slack-research [主题或问题]
/ce-slack-research
```

## 示例

```
/ce-slack-research 免费试用
/ce-slack-research 我们最近关于免费试用说了什么？
/ce-slack-research #proj-reverse-trial 中的免费试用
/ce-slack-research 2026-03-01 之后的 onboarding 流程
```

输入可以是关键词、自然语言问题，或包含 Slack 搜索修饰符（如频道提示 `in:#channel`）和日期过滤器（`after:YYYY-MM-DD`）。代理会提取主题，并根据输入的任何形式构建搜索。

## 执行

如果未提供参数，则询问要研究哪个主题。使用平台的阻塞问题工具：Claude Code 中的 `AskUserQuestion`（如果其模式未加载，则先调用 `ToolSearch` 并设置 `select:AskUserQuestion`），Codex 中的 `request_user_input`，Gemini 中的 `ask_user`，Pi 中的 `ask_user`（需要 `pi-ask-user` 扩展）。当 harness 中不存在阻塞工具或调用出错时（例如 Codex 编辑模式）——不是因为需要加载模式——才回退到仅使用纯文本提问。永远不要无声地跳过问题。

使用用户的主题作为任务提示，派发 `ce-slack-researcher`。省略 `mode` 参数，以便应用用户的配置权限设置。

代理将处理后续所有事务——Slack MCP 发现、搜索执行、线程读取和综合。它将返回包含以下内容的摘要：

- **工作区标识符**，以便用户验证是否搜索了正确的 Slack 实例
- **研究价值评估**（高 / 中 / 低 / 无），并附带说明
- **按主题组织的发现**，包含来源频道和日期
- **跨主题分析**，揭示发现中的模式

如果代理报告 Slack 不可用（MCP 未连接或认证过期），将消息传达给用户。不要尝试其他研究方法。
