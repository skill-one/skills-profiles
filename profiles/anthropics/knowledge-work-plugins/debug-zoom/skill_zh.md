# /debug-zoom

> 如果你看到不熟悉的占位符或需要检查哪些工具已连接，请参阅[CONNECTORS.md](../../CONNECTORS.md)。

使用 /debug-zoom 命令，无需浏览整个文档集即可排查 Zoom 的认证、API、webhook、SDK 或 MCP 问题。

## 使用方法

```text
/debug-zoom $ARGUMENTS
```

## 工作流程

1. 识别出故障的层级：认证、API 请求、webhook、SDK 初始化、媒体/会话行为或 MCP 传输。
2. 询问最少的缺失证据：精确的错误信息、平台、请求/响应、事件负载或代码路径。
3. 提供 2-4 个按可能性排序的合理原因。
4. 引导至 `skills/` 中最相关的深入参考资料。
5. 提供一个简短的验证计划，以便用户可以确认修复方案。

## 输出

- 最可能的故障层级
- 按可能性排序的假设
- 针对的修复步骤
- 验证清单
- 相关技能链接

## 相关技能

- [debug-zoom-integration](../debug-zoom-integration/SKILL.md)
- [setup-zoom-oauth](../setup-zoom-oauth/SKILL.md)
- [design-mcp-workflow](../design-mcp-workflow/SKILL.md)
