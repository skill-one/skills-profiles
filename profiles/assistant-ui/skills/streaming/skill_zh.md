# assistant-ui 流式传输

**始终查阅 [assistant-ui.com/llms.txt](https://www.assistant-ui.com/llms.txt) 获取最新 API。**

`assistant-stream` 是 assistant-ui 聊天运行时的底层传输层。它将每个后端标准化为 `AssistantStreamChunk` 值的单一流，提供三种传输格式的编码器和解码器，并在它们之上添加可恢复流层。如果你的后端已经使用 Vercel AI SDK，你很少需要直接接触这个包（`streamText` 加 `toUIMessageStream` 足够）；当你编写自定义端点、需要自行解码流或希望使用可恢复流时，才需要使用它。

## 参考

- [./references/data-stream.md](./references/data-stream.md) -- 数据流协议、`useDataStreamRuntime` 及其传输格式
- [./references/assistant-transport.md](./references/assistant-transport.md) -- Assistant Transport SSE 格式和 `useAssistantTransportRuntime` 状态快照运行时
- [./references/encoders.md](./references/encoders.md) -- 编码器和解码器目录、`PlainTextEncoder`、`UIMessageStreamDecoder`、累加器及调试
- [./references/resumable.md](./references/resumable.md) -- `assistant-stream/resumable`：上下文、存储和客户端连接

## 何时使用

```
通过 Vercel AI SDK 进行模型调用流式传输？
├─ 是 → streamText + toUIMessageStream/createUIMessageStreamResponse（或 result.toUIMessageStreamResponse()）
│        assistant-stream 是可选的：仅在你需要自行解码响应或添加可恢复流时需要
└─ 否 → 使用 assistant-stream 构建响应
    ├─ 发送消息部分（文本、推理、工具调用）→ 数据流
    └─ 使用自定义命令流式传输完整代理状态快照 → Assistant Transport
```

## 安装

```bash
npm install assistant-stream
```

`@assistant-ui/ai-sdk` 是当前的 AI SDK 集成包（框架无关）；`@assistant-ui/react-ai-sdk` 仍然为旧版本安装重新导出相同的 API，但新代码应从 `@assistant-ui/ai-sdk` 导入。

## 构建自定义流式响应

`createAssistantStreamResponse` 运行一个回调，该回调接收一个 `AssistantStreamController` 并返回一个作为数据流编码的 `Response`（有关替代编码器，请参阅 [data-stream.md](./references/data-stream.md)）。

```ts
import { createAssistantStreamResponse } from "assistant-stream";

export async function POST(req: Request) {
  return createAssistantStreamResponse(async (controller) => {
    controller.appendText("Hello ");
    controller.appendText("world!");

    controller.appendReasoning("首先检查天气预报。", {
      unstable_summary: "查询天气",
    });

    controller.appendSource({
      type: "source",
      sourceType: "url",
      id: "s1",
      url: "https://example.com/forecast",
      title: "天气预报",
    });

    const tool = controller.addToolCallPart({ toolName: "get_weather" });
    tool.argsText.append('{"city":"NYC"}');
    tool.argsText.close();
    tool.setResponse({ result: { temperature: 22 } });

    controller.close();
  });
}
```

`close()` 关闭任何仍打开的部分并结束流；回调中未捕获的抛出将被自动转换为 `error` chunk。

## AssistantStreamController

每个服务器端流，无论最终由哪个编码器包装，都是通过此控制器写入的（`createAssistantStream`、`createAssistantStreamController` 和 `createAssistantStreamResponse` 都会给你一个）。

| 方法 | 签名 | 备注 |
| --- | --- | --- |
| `appendText` | `(textDelta: string) => void` | 第一次调用时打开文本部分，下次调用时追加到该部分 |
| `appendReasoning` | `(reasoningDelta: string, options?: { unstable_summary?: string }) => void` | 传递 `options` 总是打开新部分，因此摘要会落在自己的部分中 |
| `appendSource` | `(part: SourcePart) => void` | `SourcePart` 是 `{ type: "source", sourceType: "url", id, url, title?, parentId? }` |
| `appendFile` | `(part: FilePart) => void` | `FilePart` 是 `{ type: "file", data, mimeType, parentId? }` |
| `appendData` | `(part: DataPart) => void` | `DataPart` 是 `{ type: "data", name, data, parentId? }`，一个命名的自定义部分 |
| `addTextPart` | `() => TextStreamController` | 显式的 `{ append(text), close() }` 写入器，用于与其他部分交错 |
| `addReasoningPart` | `(options?) => TextStreamController` | 与 `addTextPart` 相同的写入器形状 |
| `addToolCallPart` | `(toolName: string) => ToolCallStreamController` | 生成 `toolCallId`；有关稳定 ID，请参阅下面的对象重载 |
| `addToolCallPart` | `(init: ToolCallPartInit) => ToolCallStreamController` | `{ toolCallId?, toolName, argsText?, args?, response? }` |
| `enqueue` | `(chunk: AssistantStreamChunk) => void` | 原始逃逸通道；优先使用上面的辅助方法 |
| `merge` | `(stream: AssistantStream) => void` | 将另一个 `AssistantStream` 的部分拼接到此流中 |
| `withParentId` | `(parentId: string) => AssistantStreamController` | 返回一个控制器，其写入附加 `parentId`（嵌套或相关部分） |
| `close` | `() => void` | 关闭打开的部分，然后结束流 |

`addToolCallPart` 返回 `ToolCallStreamController`：`{ argsText: TextStreamController, setResponse(response), close() }`。`setResponse` 接收 `{ result, artifact?, isError?, modelContent?, messages? }`（由 `ToolResponse` 返回的形状），自动关闭该部分，并忽略第二次调用。

## 流事件和部分类型

每个解码器，无论其传输格式如何，都会产生相同的标准化 `AssistantStreamChunk` 联合（`{ path: number[] } & { type, ... }`）：

| `type` | 额外字段 |
| --- | --- |
| `part-start` | `part: PartInit`（见下文） |
| `part-finish` | 无 |
| `tool-call-args-text-finish` | 无 |
| `text-delta` | `textDelta: string` |
| `annotations` | `annotations: ReadonlyJSONValue[]` |
| `data` | `data: ReadonlyJSONValue[]` |
| `step-start` | `messageId: string` |
| `step-finish` | `finishReason, usage: { inputTokens, outputTokens }, isContinued: boolean` |
| `message-finish` | `finishReason, usage` |
| `result` | `result, isError: boolean, artifact?, modelContent?, messages?` |
| `error` | `error: string, code?, severity?: "critical" \| "warning" \| "info"` |
| `update-state` | `operations: AssistantTransportStateOperation[]`（见 [assistant-transport.md](./references/assistant-transport.md)） |

`PartInit`（`part-start` 的 `part` 字段）是六种部分类型之一，每种变体都带有可选的 `parentId`：

| `type` | 额外字段 |
| --- | --- |
| `text` | 无 |
| `reasoning` | `unstable_summary?: string` |
| `tool-call` | `toolCallId: string, toolName: string` |
| `source` | `sourceType: "url", id, url, title?` |
| `file` | `data: string, mimeType: string` |
| `data` | `name: string, data: ReadonlyJSONValue` |

## 常见问题

**`appendSource`、`appendFile` 或 `appendData` 默默丢弃部分**
- 传递完整的部分对象，包括其 `type` 字段（`"source"`、`"file"` 或 `"data"`）；方法名称不会为你暗示它。

**工具调用在 UI 中从未确定**
- `addToolCallPart` 需要一个 `toolName`；如果没有传递，ID 将为您生成。关闭 `argsText`（或调用 `setResponse`，它会为您关闭它）或该部分将不会结束。使用 `"use generative"` 工具包注册渲染，而不是已弃用的 `makeAssistantToolUI`；见 [tools](../tools/SKILL.md)。

**两个独立的推理部分在客户端合并为一个**
- 在数据流传输中，只有当 `unstable_summary` 设置时才会发送推理部分开始帧；一个普通的 `appendReasoning(text)` 调用仅作为文本增量传输，解码器没有其他信息来告诉它一个新部分已开始。连续打开两个没有摘要的推理部分（例如围绕一个工具调用）在客户端重建为一个连续的推理部分。给每个部分一个 `unstable_summary`（即使感觉空白的）或通过单独的消息步骤路由工具调用以保持它们区分。

**流未更新 UI**
- 检查 Content-Type 是否与你实际使用的编码器匹配：`DataStreamEncoder`（`createAssistantStreamResponse` 的默认值）发送 `text/plain; charset=utf-8` 并带有 `x-vercel-ai-data-stream: v1`，而不是 `text/event-stream`。`AssistantTransportEncoder` 和 AI SDK 的 UI 消息流确实发送 `text/event-stream`。

**解码器抛出 "流突然结束而没有接收到 [DONE] 标记"**
- `AssistantTransportDecoder` 和 `UIMessageStreamDecoder` 需要终端 `[DONE]` 标记；代理、CDN 或缓冲或截断正文的中间件会破坏这一点。`DataStreamDecoder` 没有这样的标记。

**`createAssistantStreamResponse` 始终编码为数据流**
- 它硬编码了 `DataStreamEncoder`。对于不同的传输格式，请手动编码：`AssistantStream.toResponse(createAssistantStream(callback), new AssistantTransportEncoder())`，或使用 `createAssistantStreamController` 并自己编码返回的流。

## 相关技能

- [runtime](../runtime/SKILL.md) -- `useLocalRuntime`、`useExternalStoreRuntime` 和 `useAssistantTransportRuntime` React 钩子和状态钩子
- [setup](../setup/SKILL.md) -- 搭建 AI SDK 路由处理程序和 `useChatRuntime`
- [tools](../tools/SKILL.md) -- `"use generative"` 工具包和工具调用渲染
- [cloud](../cloud/SKILL.md) -- 使用 assistant-cloud 持久化流式线程和消息
