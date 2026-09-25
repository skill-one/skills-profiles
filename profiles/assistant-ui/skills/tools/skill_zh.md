# assistant-ui 工具

**始终查阅 [assistant-ui.com/llms.txt](https://www.assistant-ui.com/llms.txt) 获取最新 API。**

工具是模型可以调用的命名功能。在 assistant-ui 中，你通过工具包声明工具，工具包是一个键为模型可见的工具名称、值为包含模式、执行器和渲染器的映射。支持的开发路径是由构建插件编译的 `"use generative"` 文件，该文件将一个文件拆分为服务器构建（模式加后端执行器）和客户端构建（模式加渲染器加浏览器执行器）。

## 参考

- [./references/toolkits.md](./references/toolkits.md) -- 端到端编写工具包：种类、渲染器、`toModelOutput`、`providerOptions`、存根、拆分和合并文件、`backendless`
- [./references/tool-ui.md](./references/tool-ui.md) -- 渲染状态、`useToolArgsStatus`、延迟渲染、流式参数、`ToolFallback` 和 `ToolGroup`
- [./references/human-in-loop.md](./references/human-in-loop.md) -- 人工工具、`human()` 中断以及完整的审批表面
- [./references/mcp-server.md](./references/mcp-server.md) -- 服务器端 MCP 服务器和 `defineMcpToolkit`
- [./references/mcp-apps.md](./references/mcp-apps.md) -- 使用 `McpAppRenderer` 渲染 MCP App `ui://` 组件
- [./references/webmcp.md](./references/webmcp.md) -- 使用 `unstable_useWebMcpProvider` 将前端工具发布到浏览器代理
- [./references/multi-agent.md](./references/multi-agent.md) -- 工具调用内的子代理对话
- [./references/legacy-component-apis.md](./references/legacy-component-apis.md) -- 已弃用的 `makeAssistantTool` 系列以及如何迁移

## 开发模型

### 1. 添加构建插件

没有编译器，指令不会执行任何操作。

```ts title="next.config.ts"
import { withAui } from "@assistant-ui/next";

export default withAui({
  /* 你的 Next 配置 */
});
```

Vite 和 TanStack Start 从 `@assistant-ui/vite` 中添加 `aui()` 到 `plugins`；Expo 和裸 React Native 用 `@assistant-ui/metro` 的 `withAui` 包裹 Metro 配置。这三个都接受一个 `aui` 选项对象，文档记录在 [toolkits.md](./references/toolkits.md)。

### 2. 编写工具包

```tsx title="app/toolkit.tsx"
"use generative";

import { defineToolkit } from "@assistant-ui/react";
import { z } from "zod";

export default defineToolkit({
  get_weather: {
    description: "获取某个位置的当前天气。",
    parameters: z.object({
      location: z.string().describe("城市名称或邮政编码"),
      unit: z.enum(["celsius", "fahrenheit"]).default("celsius"),
    }),
    execute: async ({ location, unit }) => {
      "use client";
      return fetchWeatherAPI(location, unit);
    },
    render: ({ args, result }) =>
      result ? (
        <div>
          {result.temperature} {args.unit}
        </div>
      ) : (
        <div>正在获取 {args.location} 的天气</div>
      ),
  },
});
```

### 3. 在客户端挂载

```tsx title="app/MyRuntimeProvider.tsx"
"use client";

import { AssistantRuntimeProvider, AuiConfig, Tools } from "@assistant-ui/react";
import { useChatRuntime } from "@assistant-ui/ai-sdk";
import toolkit from "./toolkit";

export function MyRuntimeProvider({ children }: { children: React.ReactNode }) {
  const runtime = useChatRuntime();
  const config = AuiConfig({ tools: Tools({ toolkit }) });
  return (
    <AssistantRuntimeProvider runtime={runtime} config={config}>
      {children}
    </AssistantRuntimeProvider>
  );
}
```

若要在树的一部分范围内使用工具包，请将那部分子树包裹在 `<AuiProvider extends={aui} config={config}>` 中，并使用 `const aui = useAui()`。`useChatRuntime()` 默认针对 `/api/chat`。

### 4. 向模型暴露

在路由处理程序中，相同的导入解析为服务器构建。

```ts title="app/api/chat/route.ts"
import { AISDKToolkit } from "@assistant-ui/ai-sdk";
import { streamText, convertToModelMessages } from "ai";
import { openai } from "@ai-sdk/openai";
import toolkit from "../../toolkit";

const aiToolkit = new AISDKToolkit({ toolkit });

export async function POST(req: Request) {
  const { messages, system, tools } = await req.json();

  const result = streamText({
    model: openai("gpt-5.6-luna"),
    system,
    messages: await convertToModelMessages(messages),
    tools: await aiToolkit.tools({ frontend: tools }),
  });

  return result.toUIMessageStreamResponse();
}
```

`AISDKToolkit.tools()` 将每个工具包工具注册到模型，将后端 `execute` 连接到服务器构建（服务器构建包含一个 `execute`），合并客户端请求体中上传的前端工具，并启动工具包中传播的任何 MCP 服务器。服务器 `execute` 优先于同名的上传条目。

## 工具种类

种类从 `execute` 推断，并作为 `type` 写回。你永远不会在 `"use generative"` 文件中编写 `type`。

| 你编写的 `execute` | 推断种类 | 服务器构建保留 | 客户端构建保留 |
| --- | --- | --- | --- |
| 纯 `async () => ...` | backend | 模式加 `execute`，由 `server-only` 保护 | 模式加 `render` |
| `async () => { "use client"; ... }` | frontend | 仅模式 | 模式加 `execute` 加 `render` 或 `renderText` |
| `humanTool()` | human | 仅模式 | 模式加 `render` |
| `stubTool()` | frontend, 运行时提供执行器 | 仅模式 | 模式加 `render` 或 `renderText` |
| `providerTool({ ... })` | provider | 模式加提供者配置 | 模式加提供者配置 |
| `externalTool()` | backend, 在其他地方定义 | 被省略 | `type: "backend"` 加 `render` 或 `renderText` |

编译器在构建时强制执行，确保每个工具声明了 `execute`，前端工具声明了 `render` 或 `renderText`，人工工具声明了 `render`。`humanTool()` 和 `stubTool()` 没有运行时实现，在调用时抛出异常，这意味着文件没有被编译；`externalTool()` 与之类似，是编译时的标记。

## 渲染工具调用

`render` 接收实时调用的 `ToolCallMessagePartProps`。

| 字段 | 类型 | 备注 |
| --- | --- | --- |
| `args` | `TArgs` | 解析的参数，流式传输时为部分状态 |
| `argsText` | `string` | 原始，可能为部分 JSON |
| `result` | `TResult \| undefined` | 调用有结果时出现 |
| `isError` | `boolean \| undefined` | 结果是否表示失败 |
| `status` | `ToolCallMessagePartStatus` | `running`、`complete`、`incomplete` 带有 `reason`，或 `requires-action` 带有 `reason: "tool-calls" \| "interrupt"` |
| `toolName`, `toolCallId` | `string` | 模型可见的名称和此调用的稳定 ID |
| `timing` | `ToolCallTiming \| undefined` | 墙上时钟开始和完成，当被跟踪时 |
| `interrupt` | `{ type: "human"; payload: unknown } \| undefined` | 来自前端执行器的暂停 `human()` 请求 |
| `approval` | object `\| undefined` | 服务器端门：`id`、`approved?`、`options?`、`optionId?`、`resolution?` |
| `addResult` | `(result) => void` | 从 UI 完成人工具 |
| `resume` | `(payload: unknown) => void` | 回答 `interrupt` |
| `respondToApproval` | `(response: ToolApprovalResponse) => Promise<void>` | 回答审批门 |

若要使用单行状态而不是组件，请设置 `renderText`，其 `running` 和 `complete` 值为字符串或 `({ args, result })` 的函数。在条目上设置 `display: "standalone"` 以保持 UI 在折叠的工具组之外。没有渲染器的工具回退到 `ToolFallback` 元素。

## 审批门

某些运行时在服务器上暂停，并发送客户端必须回答的审批请求，工具才能运行。AI SDK v7 运行时针对调用级别的 `toolApproval` 选项中列出的每个工具发出一个。

```tsx
import { useState } from "react";
import { defineToolkit, type ToolApprovalResponse } from "@assistant-ui/react";

const toolkit = defineToolkit({
  deploy: {
    type: "backend",
    render: ({ args, approval, respondToApproval, result }) => {
      const [error, setError] = useState<string | null>(null);

      const answer = async (response: ToolApprovalResponse) => {
        setError(null);
        try {
          await respondToApproval(response);
        } catch (failure) {
          setError(failure instanceof Error ? failure.message : String(failure));
        }
      };

      if (approval?.approved === undefined) {
        if (approval?.isAutomatic) return <p>由策略自动批准</p>;
        return (
          <div>
            <p>批准部署到 {args.target} 吗？</p>
            <button onClick={() => void answer({ approved: true })}>批准</button>
            <button onClick={() => void answer({ approved: false, reason: "user denied" })}>
              拒绝
            </button>
            {error && <p role="alert">{error}</p>}
          </div>
        );
      }

      if (approval?.approved === false) {
        return <p>拒绝{approval.reason ? `: ${approval.reason}` : ""}</p>;
      }
      return result === undefined ? <p>已批准，运行中</p> : <p>已部署</p>;
    },
  },
});
```

`approval.approved` 有三种状态。`undefined` 表示门是开放的，并且是 `respondToApproval` 合法的唯一状态。`true` 表示已记录允许的决策，服务器正在生成结果。`false` 表示已记录拒绝；运行时记录错误结果并暴露 `approval.reason`。`approval.isAutomatic` 在服务器端策略授予决策而不是用户时为 `true`，因此渲染徽章而不是按钮。

`respondToApproval` 返回一个承诺，当运行时接受响应时解决，当无法记录时拒绝，例如门过期或拒绝回答。在禁用控件之前等待它，以便拒绝的响应使请求可重试。`toolApprovalAcceptsText(approval)` 报告请求是否接受自由形式答案，单独或与选项一起，以便渲染器知道是否提供文本字段。完整选项、问题和解决方案表面在 [human-in-loop.md](./references/human-in-loop.md) 中。

## 人工工具

人工工具没有执行器：运行时暂停，直到渲染器提供结果。

```tsx
select_date: {
  description: "要求用户选择一个日期。",
  parameters: z.object({ prompt: z.string() }),
  execute: humanTool(),
  render: ({ args, result, addResult }) => {
    if (result) return <p>选择了 {result.date}</p>;
    return <DatePicker prompt={args.prompt} onChange={(date) => addResult({ date })} />;
  },
},
```

当用户自己提供工具结果时使用人工工具，而当后端拥有操作并只需要权限时使用审批门。

## 常见陷阱

**`humanTool()` 或 `stubTool()` 运行时抛出异常**
- 文件没有被编译器处理。添加构建插件，并将 `"use generative"` 作为文件的第一行。

**工具 UI 从未渲染**
- 工具包键必须与模型可见的工具名称完全匹配，包括任何 MCP `prefix`。
- 必须挂载工具包：`const config = AuiConfig({ tools: Tools({ toolkit }) })` 作为 `config` 传递给提供程序。从模块作用域或 `useMemo` 传递一个稳定的工具包。

**模型从未学习到前端或人工工具**
- 客户端构建跳过上传这些模式，因为它假设你的后端导入了相同文件的服务器构建。没有你的后端，使用 `aui: { backendless: true }` 编译。

**前端工具结果从未到达模型**
- 使用 `ai` 的 `sendAutomaticallyWhen: lastAssistantMessageIsCompleteWithToolCalls` 和 `lastAssistantMessageIsCompleteWithApprovalResponses` 配置运行时。

**`toModelOutput` 在往返结果中被忽略**
- 除了 `streamText` 之外，还将工具注册传递给 `convertToModelMessages(messages, { tools })`。

**关于工具名称的构建警告**
- 重复的名称意味着两个展开片段定义了相同的键和对象展开保留了后面的一个；重命名一个条目。无法 `makeTool()` 的工具来自不透明的工厂调用：将其作为内联对象编写，或展开编译器可见的 `defineToolkit(...)` 或 `defineMcpToolkit(...)` 片段。

**`respondToApproval` 拒绝**
- 只有在 `approval.approved` 为 `undefined` 时才合法。对既不声明 `display: "text"` 也不声明 `allowFreeform` 的请求回答文本会抛出异常，未知 `optionId` 也会抛出异常。

**MCP 连接堆积**
- 将 `AISDKToolkit` 保持为模块作用域，以便客户端跨请求池化，并从 `onFinish` 调用 `aiToolkit.close()`。

## 相关技能

- [elements](../elements/SKILL.md) -- 样式的 `ToolFallback` 和 `ToolGroup` 文件以及目录的其余部分
- [generative-ui](../generative-ui/SKILL.md) -- 模型从你发送的词汇组成的 UI
- [react-mcp](../react-mcp/SKILL.md) -- 用户在浏览器中添加和认证的 MCP 服务器
- [runtime](../runtime/SKILL.md) -- `useChatRuntime` 和 AI SDK 工具包连接的路线
- [copilots](../copilots/SKILL.md) -- 可交互项，模型可编辑的应用状态替代存根工具
- [update](../update/SKILL.md) -- 将旧工具代码迁移到工具包
