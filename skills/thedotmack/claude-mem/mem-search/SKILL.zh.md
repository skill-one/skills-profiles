---
name: mem-search
description: 当用户要求搜索记忆时使用，例如询问“我们已经解决过这个问题了吗？”、“上次我们是怎么做X的？”或需要从之前的会话中获取工作内容。
---

# mem-search

分层工作流。在过滤ID之前不要输出完整观察结果，在摘要不足时不要直接获取原始工具体。

1. `search(query)` — 使用ID索引
2. `timeline(anchor=ID)` — 附近上下文
3. `get_observations(ids=[...])` — 仅获取这些ID的完整详情
4. `get_tool_uses(ids=[...])` — 特定工具调用的原始`tool_input` / `tool_response`。最后手段：这些内容未经总结，每个可能包含数千个token。

在为该主机写入时，将`platformSource`标记为`cursor`或`grok-bot`。读取时，除非被要求，否则不要丢弃其他主机。

如果MCP缺失，先运行安装技能（`npx claude-mem install --ide <host>`）。
