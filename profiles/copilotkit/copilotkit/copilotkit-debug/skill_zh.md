# CopilotKit 调试技巧

## 使用时机

在以下情况调用此技能：

- CopilotKit 运行时无法访问或返回错误
- 代理连接失败、无响应或无法流式传输事件
- 前端工具未执行或未返回结果
- 转录（语音）失败
- 包之间存在版本不匹配错误
- AG-UI SSE 事件格式错误或缺失
- CORS 错误阻止浏览器请求运行时

## 诊断工作流程

### 第 1 步：收集信息

在提出任何修复方案之前，收集以下信息：

1. **包版本** -- 运行 `npm ls @copilotkit/runtime @copilotkit/react-core @copilotkit/core @ag-ui/client`（或 v1 的等效包）。运行时和 React 包之间的版本不匹配是常见的根本原因。
2. **运行时模式** -- 这是 SSE 模式 (`CopilotSseRuntime`) 还是智能模式 (`CopilotIntelligenceRuntime`)？检查运行时构造函数。
3. **传输配置** -- `CopilotKit` 提供者（来自 `@copilotkit/react-core/v2`）中的 `runtimeUrl` 设置为什么值？它是否与 `createCopilotRuntimeHandler` 中的 `basePath` 匹配？
4. **代理类型** -- 代理是 `BuiltInAgent`、`LangGraphAgent`、`A2AAgent` 还是自定义的 `AbstractAgent`？
5. **错误消息** -- 收集浏览器控制台和服务器日志中的确切错误。CopilotKit 使用结构化错误代码（参见 `references/error-patterns.md`）。
6. **浏览器网络标签页** -- 检查 `/info` 请求（运行时发现）、`/agent/:id/run` SSE 流，以及任何 CORS 预检失败。

### 第 2 步：检查日志和错误代码

CopilotKit 有三种错误代码系统：

- **v1 错误代码** -- 来自 v1 运行时层的遗留错误代码 (`@copilotkit/runtime`)。例如 `NETWORK_ERROR`、`AGENT_NOT_FOUND`、`API_NOT_FOUND`。由于 `@copilotkit/*` 包内部封装了 v2，这些代码在某些上下文中仍然可见。
- **v2 `CopilotKitCoreErrorCode`** -- 由 `@copilotkit/core` 使用。例如 `runtime_info_fetch_failed`、`agent_connect_failed`、`agent_run_failed`。
- **`TranscriptionErrorCode`** -- 由 v1 和 v2 都用于语音转录。例如 `service_not_configured`、`rate_limited`、`auth_failed`。

将错误代码与 `references/error-patterns.md` 中的目录进行匹配，以确定根本原因和解决方案。

### 第 3 步：跟踪 AG-UI 事件

对于流式传输/代理问题，跟踪 AG-UI 事件流：

1. **RunStartedEvent** -- 确认代理运行已启动
2. **TextMessageStartEvent / TextMessageChunkEvent / TextMessageEndEvent** -- 文本流式传输
3. **ToolCallStartEvent / ToolCallArgsEvent / ToolCallEndEvent** -- 工具调用
4. **ToolCallResultEvent** -- 工具结果返回
5. **StateSnapshotEvent / StateDeltaEvent** -- 代理状态同步
6. **ReasoningStartEvent / ReasoningMessageContentEvent / ReasoningMessageEndEvent** -- 推理令牌（可能导致卡顿，参见问题 #3323）
7. **RunFinishedEvent** -- 成功完成
8. **RunErrorEvent** -- 代理级错误

启用 CopilotKit Web Inspector (`@copilotkit/web-inspector`) 查看实时事件。或直接在浏览器网络标签页中检查 SSE 流——每个事件都是 `text/event-stream` 响应中的 `data:` 行。

### 第 4 步：确定根本原因

使用参考文档将症状与已知问题进行匹配：

- **`references/runtime-debugging.md`** -- 连接性、CORS、传输、SSE 流式传输
- **`references/agent-debugging.md`** -- 代理发现、状态同步、工具执行、AG-UI 协议
- **`references/error-patterns.md`** -- 完整错误代码目录及解决方案
- **`references/quick-workflows.md`** -- 常见场景的逐步诊断序列

### 第 5 步：修复并验证

1. 应用修复
2. 验证 `/info` 端点返回预期的代理列表
3. 确认 SSE 流产生完整的的事件序列（从 RunStarted 到 RunFinished）
4. 检查浏览器控制台是否有任何剩余的结构化错误

## 使用 mcp-docs 进行实时文档查询

调试期间，使用 `copilotkit-docs` MCP 服务器查询最新的 CopilotKit 文档。此服务器提供两个工具：`search-docs`（搜索文档）和 `search-code`（搜索源代码示例）。

### MCP 设置

**Claude 代码：** MCP 服务器由插件的 `.mcp.json` 自动配置——无需手动设置。代理可以直接从 `copilotkit-docs` 服务器调用 `search-docs` 和 `search-code` 工具。

**Codex：** 将以下内容添加到 `.codex/config.toml`：

```toml
[mcp_servers.copilotkit-docs]
type = "http"
url = "https://mcp.copilotkit.ai/mcp"
```

### 工具使用

`search-docs` 和 `search-code` 工具作为 MCP 工具调用（不是 CLI 命令）被调用。调试期间要搜索的内容示例：

```
search-docs("AGENT_NOT_FOUND")
search-docs("CopilotRuntime 配置")
search-docs("AG-UI 协议事件")
search-docs("常见问题排查")
search-docs("CORS 配置 copilotkit")
search-code("CopilotRuntime 错误处理")
```

官方故障排除文档位于：

- `https://docs.copilotkit.ai/troubleshooting/common-issues`
- `https://docs.copilotkit.ai/coagents/troubleshooting/common-issues`

## CopilotKit 代码库中的关键文件位置

| 组件                      | 路径                                                              |
| ------------------------ | ----------------------------------------------------------------- |
| 遗留错误类和代码         | `packages/shared/src/utils/errors.ts`                             |
| v2 核心错误代码            | `packages/core/src/core/core.ts` (`CopilotKitCoreErrorCode` 枚举) |
| v2 转录错误              | `packages/shared/src/transcription-errors.ts`                     |
| 运行时 SSE 响应           | `packages/runtime/src/v2/runtime/handlers/shared/sse-response.ts` |
| 运行时信息端点          | `packages/runtime/src/v2/runtime/handlers/get-runtime-info.ts`    |
| 运行时 CORS 配置          | `packages/runtime/src/v2/runtime/core/fetch-cors.ts`              |
| CopilotKit 智能客户端    | `packages/runtime/src/v2/runtime/intelligence-platform/client.ts` |
| BuiltInAgent             | `packages/runtime/src/agent/index.ts`                             |
| Web Inspector            | `packages/web-inspector/src/index.ts`                             |
