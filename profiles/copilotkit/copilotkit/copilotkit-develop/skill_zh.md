# CopilotKit v2 开发技能

## 活动文档 (MCP)

此插件包含一个 MCP 服务器 (`copilotkit-docs`)，它提供 `search-docs` 和 `search-code` 工具用于查询活动 CopilotKit 文档和源代码。

- **Claude 代码：** 由插件的 `.mcp.json` 自动配置 -- 无需设置。
- **Codex：** 需要手动配置。请参阅 [copilotkit-debug 技能](../copilotkit-debug/SKILL.md#mcp-setup) 获取设置说明。

## 架构概述

CopilotKit v2 基于AG-UI 协议 (`@ag-ui/client` / `@ag-ui/core`) 构建。该堆栈有三层：

1. **运行时** (`@copilotkit/runtime`, v2 符号位于 `@copilotkit/runtime/v2`) -- 服务器端。托管代理、处理 SSE/智能传输、中间件、语音转写。
2. **核心** (`@copilotkit/core`) -- 共享状态管理、工具注册表、建议引擎。应用程序不直接导入。
3. **React** (`@copilotkit/react-core`, v2 符号位于 `@copilotkit/react-core/v2`) -- 提供者、聊天组件、钩子。重新导出 `@ag-ui/client` 中的所有内容，因此应用程序只需一个导入。

## 工作流程

### 1. 设置运行时 (服务器)

创建一个 `CopilotRuntime` (或显式的 `CopilotSseRuntime` / `CopilotIntelligenceRuntime`)，并通过 `createCopilotHonoHandler` (Hono) 或 `createCopilotExpressHandler` (Express) 暴露它。

```ts
import {
  CopilotRuntime,
  createCopilotHonoHandler,
} from "@copilotkit/runtime/v2";
import { LangGraphAgent } from "@copilotkit/runtime/langgraph";
import { handle } from "hono/vercel";

const runtime = new CopilotRuntime({
  agents: {
    myAgent: new LangGraphAgent({
      /* ... */
    }),
  },
});

const app = createCopilotHonoHandler({
  runtime,
  basePath: "/api/copilotkit",
});

// 多路由 (默认)：导出运行时服务的所有方法。
// useThreads 需要它们全部 — 通过 PATCH 重命名，通过 DELETE 删除；归档使用已导出的 POST。
export const GET = handle(app);
export const POST = handle(app);
export const PATCH = handle(app);
export const DELETE = handle(app);
```

### 2. 用提供者包装您的应用程序 (客户端)

使用 `CopilotKit` 提供者 (来自 `@copilotkit/react-core/v2`)。它是跨 v1 和 v2 的兼容性桥梁，是遗留 `CopilotKitProvider` 的严格超集 -- 所有 `CopilotKitProvider` 属性都适用于它。

```tsx
import { CopilotKit } from "@copilotkit/react-core/v2";

function App() {
  return (
    // 无 useSingleEndpoint：提供者协商传输方式，因此这适用于多路由处理程序 (默认) 和单路由处理程序。
    // 仅当有意固定一种模式时才传递此属性。
    <CopilotKit runtimeUrl="/api/copilotkit">
      <YourApp />
    </CopilotKit>
  );
}
```

### 3. 添加聊天 UI

使用 `<CopilotChat>`、`<CopilotPopup>` 或 `<CopilotSidebar>`：

```tsx
import { CopilotChat } from "@copilotkit/react-core/v2";

function ChatPage() {
  return <CopilotChat agentId="myAgent" />;
}
```

### 4. 注册前端工具

让代理调用浏览器中的函数：

```tsx
import { useFrontendTool } from "@copilotkit/react-core/v2";
import { z } from "zod";

useFrontendTool({
  name: "highlightCell",
  description: "突出显示电子表格单元格",
  parameters: z.object({ row: z.number(), col: z.number() }),
  handler: async ({ row, col }) => {
    highlightCell(row, col);
    return "done";
  },
});
```

### 5. 共享应用程序上下文

向代理提供运行时数据：

```tsx
import { useAgentContext } from "@copilotkit/react-core/v2";

useAgentContext({
  description: "用户的当前购物车",
  value: cart, // 任何可序列化为 JSON 的值
});
```

### 6. 处理代理中断

当代理因人类输入而暂停时：

```tsx
import { useInterrupt } from "@copilotkit/react-core/v2";

useInterrupt({
  render: ({ event, resolve }) => (
    <div>
      <p>{event.value.question}</p>
      <button onClick={() => resolve({ approved: true })}>批准</button>
    </div>
  ),
});
```

### 7. 在聊天中渲染工具调用

工具执行时显示自定义 UI：

```tsx
import { useRenderTool } from "@copilotkit/react-core/v2";
import { z } from "zod";

useRenderTool(
  {
    name: "searchDocs",
    parameters: z.object({ query: z.string() }),
    render: ({ status, parameters, result }) => {
      if (status === "executing")
        return <Spinner>搜索 {parameters.query}...</Spinner>;
      if (status === "complete") return <Results data={result} />;
      return <div>准备中...</div>;
    },
  },
  [],
);
```

## 快速参考：钩子

| 钩子                       | 目的                                                                                           |
| -------------------------- | ------------------------------------------------------------------------------------------------- |
| `useFrontendTool`          | 注册代理可以在浏览器中调用的工具                                                             |
| `useComponent`             | 将 React 组件注册为聊天渲染工具 (围绕 `useFrontendTool` 的便利包装器)                         |
| `useAgentContext`          | 与代理共享 JSON-可序列化的应用程序状态                                                      |
| `useAgent`                 | 获取代理 ID 的 `AbstractAgent` 实例；订阅消息/状态/运行状态变化                             |
| `useInterrupt`             | 处理来自代理的 `on_interrupt` 事件，带渲染 + 可选处理程序/`enabled` 谓词                   |
| `useHumanInTheLoop`        | 注册一个工具，在用户通过渲染 UI 响应之前暂停执行                                               |
| `useRenderTool`            | 注册工具调用的渲染器 (按名称或通配符 `"*"`)                                                  |
| `useDefaultRenderTool`     | 使用内置可展开卡片 UI 注册通配符 `"*"` 渲染器                                               |
| `useRenderToolCall`        | 内部钩子，返回一个函数以解析给定工具调用的正确渲染器                                           |
| `useRenderActivityMessage` | 内部钩子，按类型渲染活动消息                                                              |
| `useRenderCustomMessages`  | 内部钩子，用于渲染自定义消息装饰器                                                        |
| `useSuggestions`           | 读取当前建议列表并控制重新加载/清除                                                         |
| `useConfigureSuggestions`  | 注册静态或动态 (LLM 生成) 的建议配置                                                        |
| `useThreads`               | 列出、重命名、归档和删除 CopilotKit 智能线程                                               |

## 快速参考：组件

| 组件                   | 目的                                                                                                    |
| --------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `CopilotKit`                | 根提供者 (来自 `@copilotkit/react-core/v2`) -- 配置运行时 URL、标头、代理、错误处理程序                 |
| `CopilotChat`               | 连接到代理的完整聊天界面 (内联布局)                                                                      |
| `CopilotPopup`              | 带有切换按钮的浮动弹出窗口中的聊天                                                                         |
| `CopilotSidebar`            | 带有切换按钮的可折叠侧边栏中的聊天                                                                       |
| `CopilotChatView`           | 无头聊天视图，带有消息视图、输入、滚动、建议的插槽                                                           |
| `CopilotChatInput`          | 带有发送/停止/转写控制的聊天输入文本区域                                                                 |
| `CopilotChatMessageView`    | 渲染消息列表                                                                                           |
| `CopilotChatSuggestionView` | 渲染建议药丸                                                                                           |

## 快速参考：运行时

所有 v2 运行时符号从 `@copilotkit/runtime/v2` 导入 (`createCopilotExpressHandler` 从 `@copilotkit/runtime/v2/express`)。

| 导出                        | 目的                                                   |
| ----------------------------- | --------------------------------------------------------- |
| `CopilotRuntime`              | 自动检测运行时 (委托给 SSE 或智能)                        |
| `CopilotSseRuntime`           | 显式的 SSE 模式运行时                                   |
| `CopilotIntelligenceRuntime`  | 持久化线程的智能模式运行时                             |
| `createCopilotHonoHandler`    | 创建带有所有 CopilotKit 路由的 Hono 应用程序              |
| `createCopilotExpressHandler` | 创建带有所有 CopilotKit 路由的 Express 路由器            |
| `CopilotKitIntelligence`      | CopilotKit 智能客户端配置                             |
