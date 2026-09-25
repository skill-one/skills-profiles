# /setup-zoom-mcp

> 如果你看到不熟悉的占位符或需要检查哪些工具已连接，请参阅 [CONNECTORS.md](../../CONNECTORS.md)。

规划 Zoom MCP 工作流，并决定何时单独使用 MCP，以及何时使用混合 REST API + MCP 架构。

## 使用方法

```text
/setup-zoom-mcp $ARGUMENTS
```

## 工作流

1. 确定目标是否为确定性自动化、AI 工具编排或混合模式。
2. 如果适用 MCP，确定可能的 Zoom MCP 界面和传输假设。
3. 如果单独使用 MCP 不够，分别定义 REST API 的职责。
4. 指出认证、范围和客户端能力限制。
5. 以一个最小的概念验证序列结束。

## 输出

- 推荐的 MCP 策略
- 连接器的预期
- 如果也需要 REST，混合边界
- 风险和设置说明
- 相关技能链接

## 相关技能

- [design-mcp-workflow](../design-mcp-workflow/SKILL.md)
- [choose-zoom-approach](../choose-zoom-approach/SKILL.md)
