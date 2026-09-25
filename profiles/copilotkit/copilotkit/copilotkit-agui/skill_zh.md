# AG-UI 协议技能

## 概述

AG-UI（Agent-User 交互）是 CopilotKit 的开放事件驱动协议，用于 Agent 与 UI 之间的通信。所有 Agent-frontend 交互流程都通过 SSE（服务器发送事件）或二进制 protobuf 传输的 typed 事件流进行。Agents 实现 `AbstractAgent.run()` 返回 RxJS `Observable<BaseEvent>`，客户端 SDK 负责事件应用、状态管理和消息历史记录。

## 何时使用

- 构建 Agent 后端需要使用 AG-UI
- 为新框架集成实现 `AbstractAgent.run()`
- 调试事件未到达前端或格式错误的原因
- 理解事件顺序（生命周期、文本、工具调用、状态）
- 处理状态同步（快照与 JSON Patch 差分）
- 实现 Human-in-the-loop 中断/恢复流程
- 排查 SSE 流传输或编码问题

## 何时不用

- 对于 CopilotKit React 钩子和前端组件，使用 `copilotkit-develop`
- 对于 CopilotKit 运行时设置和配置，使用 `copilotkit-setup`
- 对于框架特定集成指南（LangGraph、Mastra、CrewAI），使用 `copilotkit-integrations`

## 快速参考

### 事件类型

| 类型     | 事件                                                                                                  | 目的               |
| -------- | ---------------------------------------------------------------------------------------------------- | ------------------ |
| 生命周期 | `RUN_STARTED`, `RUN_FINISHED`, `RUN_ERROR`, `STEP_STARTED`, `STEP_FINISHED`                             | 运行边界和进度     |
| 文本     | `TEXT_MESSAGE_START`, `TEXT_MESSAGE_CONTENT`, `TEXT_MESSAGE_END`                                        | 流式传输文本消息   |
| 工具调用 | `TOOL_CALL_START`, `TOOL_CALL_ARGS`, `TOOL_CALL_END`, `TOOL_CALL_RESULT`                              | Agent 工具调用    |
| 状态     | `STATE_SNAPSHOT`, `STATE_DELTA`, `MESSAGES_SNAPSHOT`                                                   | 状态同步          |
| 推理     | `REASONING_START`, `REASONING_MESSAGE_START/CONTENT/END`, `REASONING_END`, `REASONING_ENCRYPTED_VALUE` | 思维链可见性      |
| 活动     | `ACTIVITY_SNAPSHOT`, `ACTIVITY_DELTA`                                                                | 结构化进度更新    |
| 自定义   | `RAW`, `CUSTOM`                                                                                       | 扩展点            |

### 便捷分块事件

`TEXT_MESSAGE_CHUNK` 和 `TOOL_CALL_CHUNK` 通过客户端的 `transformChunks` 管道自动扩展为 Start/Content/End 三元组。适用于更简单的后端实现。

### SSE 线路格式

每个事件都是一个 JSON 对象，作为 SSE 数据行发送：

```
data: {"type":"RUN_STARTED","threadId":"t1","runId":"r1"}\n\n
data: {"type":"TEXT_MESSAGE_START","messageId":"m1","role":"assistant"}\n\n
data: {"type":"TEXT_MESSAGE_CONTENT","messageId":"m1","delta":"Hello"}\n\n
data: {"type":"TEXT_MESSAGE_END","messageId":"m1"}\n\n
data: {"type":"RUN_FINISHED","threadId":"t1","runId":"r1"}\n\n
```

### 包

| 包          | npm                                                    | 目的               |
| ----------- | ----------------------------------------------------- | ------------------ |
| `@ag-ui/core` | 事件、类型、模式                                        | 协议定义          |
| `@ag-ui/client` | AbstractAgent, HttpAgent, 中间件, 事件应用            | 客户端 SDK        |
| `@ag-ui/encoder` | EventEncoder (SSE + protobuf)                          | 服务器端编码      |

## 工作流：构建 AG-UI 后端

1. **定义你的端点** -- 接受 POST 请求，body 为 `RunAgentInput`，响应 `text/event-stream`
2. **解析输入** -- 从请求 body 中提取 `threadId`, `runId`, `messages`, `tools`, `state`, `context`
3. **按顺序发送事件** -- 首先发送 `RUN_STARTED`，然后内容事件，最后 `RUN_FINISHED` 或 `RUN_ERROR`
4. **编码为 SSE** -- 使用 `@ag-ui/encoder` 的 `EventEncoder.encode()` 或手动写入 `data: JSON\n\n`
5. **处理工具结果** -- 客户端发送 `TOOL_CALL_RESULT`，Agent 处理后继续

参考 `references/building-agents.md` 获取完整示例。

## 关键协议规则

- 每个运行必须以 `RUN_STARTED` 开始，并以 `RUN_FINISHED` 或 `RUN_ERROR` 结束
- `TEXT_MESSAGE_CONTENT.delta` 必须非空
- 工具调用事件通过 `toolCallId` 链接
- `STATE_DELTA` 使用 RFC 6902 JSON Patch 操作
- 支持多个顺序运行 -- 每个运行必须完成才能开始下一个
- 消息跨运行累积；状态除非由 `STATE_SNAPSHOT` 重置，否则会持续

## 参考

- `references/protocol-spec.md` -- 完整事件类型参考，包含模式和示例
- `references/building-agents.md` -- 构建 AG-UI 后端的分步指南
- `references/event-flow-diagrams.md` -- 常见流程的 ASCII 序列图
- `references/client-sdk.md` -- @ag-ui/client API 参考
