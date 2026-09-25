# 设计 MCP 工作流

当用户希望 Claude 或其他支持 MCP 的客户端通过工具调用与 Zoom 交互，而不是仅通过确定性 API 代码交互时，使用此技能。

## 涵盖内容

- MCP 适用性评估
- REST API 与 MCP 边界
- 混合架构
- 连接器预期
- 白板特定 MCP 路由

## 工作流

1. 确定问题是属于智能体工具、确定性自动化，还是两者兼具。
2. 将仅使用 MCP 的任务路由到 `[zoom-mcp](../zoom-mcp/SKILL.md)`。
3. 将混合任务同时路由到 `[zoom-mcp](../zoom-mcp/SKILL.md)` 和 `[rest-api](../rest-api/SKILL.md)`。
4. 如果白板是核心，则路由到 `[zoom-mcp/whiteboard](../zoom-mcp/whiteboard/SKILL.md)`。
5. 明确指出传输、认证和客户端能力假设。

## 常见错误

- 将 MCP 用于本应保留在 REST 中的确定性后端任务
- 将 MCP 视为所有 API 设计的替代方案
- 忽略客户端传输支持和认证要求
