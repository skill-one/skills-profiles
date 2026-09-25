# CopilotKit 集成

## 活动文档 (MCP)

此插件包含一个 MCP 服务器 (`copilotkit-docs`)，它提供 `search-docs` 和 `search-code` 工具，用于查询活动 CopilotKit 文档和源代码。适用于查找特定框架的集成详细信息。

- **Claude 代码：** 由插件的 `.mcp.json` 自动配置 -- 无需设置。
- **Codex：** 需要手动配置。请参阅 [copilotkit-debug 技能](../copilotkit-debug/SKILL.md#mcp-setup) 的设置说明。

## 概述

CopilotKit 通过 **AG-UI (Agent-UI) 协议** 连接到外部代理框架 -- 这是一个流式协议，它能够在前端 CopilotKit 应用程序和后端代理之间实现双向通信。每个集成都遵循相同的架构模式：

1. **代理服务器** -- 您的代理框架作为 HTTP 服务器运行（通常为 Python 使用 FastAPI/uvicorn，或为 JS/TS 使用 Express/Next.js 路由）
2. **AG-UI 适配器** -- 框架特定的适配器在代理的原生接口和 AG-UI 线协议之间进行转换
3. **CopilotKit 运行时** -- Next.js 捕获所有 API 路由创建一个 `CopilotRuntime`，该运行时通过 AG-UI 客户端类连接到代理，该客户端类使用 V2 多路由 Hono 处理程序挂载
4. **前端** -- React 组件使用 `useAgent`、`useFrontendTool`、`useRenderTool` 和 `useHumanInTheLoop` 与代理交互

## 支持的集成

| 框架                              | 语言    | AG-UI 客户端 (route.ts)                                   | AG-UI 服务器适配器                                             | 代理端口         |
| -------------------------------------- | ----------- | --------------------------------------------------------- | ---------------------------------------------------------------- | ------------------ |
| LangGraph (Python, 自托管)        | Python      | `LangGraphHttpAgent` from `@copilotkit/runtime/langgraph` | `ag-ui-langgraph` (`add_langgraph_fastapi_endpoint`)             | 8123               |
| LangGraph (Python, LangGraph 平台) | Python      | `LangGraphAgent` from `@copilotkit/runtime/langgraph`     | LangGraph 平台 (托管)                                     | varies             |
| LangGraph (JS)                         | TypeScript  | `LangGraphAgent` from `@copilotkit/runtime/langgraph`     | 内置于 `@copilotkit/sdk-js/langgraph`                        | 8123               |
| CrewAI Flows                           | Python      | `HttpAgent` from `@ag-ui/client`                          | `ag-ui-crewai` (`add_crewai_flow_fastapi_endpoint`)              | 8000               |
| CrewAI Crews                           | Python      | `CrewAIAgent` from `@ag-ui/crewai`                        | `ag-ui-crewai` (`add_crewai_crew_fastapi_endpoint`)              | 8000               |
| PydanticAI                             | Python      | `HttpAgent` from `@ag-ui/client`                          | `pydantic-ai-slim[ag-ui]` (`AGUIAdapter.dispatch_request()`)     | 8000               |
| Mastra                                 | TypeScript  | `MastraAgent` from `@ag-ui/mastra`                        | 内置于 `@ag-ui/mastra`                                       | Next.js 开发服务器 |
| Google ADK                             | Python      | `HttpAgent` from `@ag-ui/client`                          | `ag-ui-adk` (`add_adk_fastapi_endpoint`)                         | 8000               |
| LlamaIndex                             | Python      | `LlamaIndexAgent` from `@ag-ui/llamaindex`                | `llama-index-protocols-ag-ui` (`get_ag_ui_workflow_router`)      | 9000               |
| Agno                                   | Python      | `HttpAgent` from `@ag-ui/client`                          | `agno` (内置 `AgentOS` 带有 `AGUI` 接口)                | 8000               |
| Strands                                | Python      | `HttpAgent` from `@ag-ui/client`                          | `ag_ui_strands` (`create_strands_app`)                           | 8000               |
| Microsoft Agent Framework (Python)     | Python      | `HttpAgent` from `@ag-ui/client`                          | `agent-framework-ag-ui` (`add_agent_framework_fastapi_endpoint`) | 8000               |
| Microsoft Agent Framework (.NET)       | C#          | `HttpAgent` from `@ag-ui/client`                          | `Microsoft.Agents.AI.Hosting.AGUI.AspNetCore` (`MapAGUI`)        | 8000               |
| A2A Middleware                         | Python + TS | `A2AMiddlewareAgent` from `@ag-ui/a2a-middleware`         | 每个代理（混合框架）                                     | 9000-9002          |
| MCP Apps                               | TypeScript  | `BuiltInAgent` with `MCPAppsMiddleware`                   | 无 (BuiltInAgent 上的中间件)                                 | 3108               |

## 决策树

使用此工具选择正确的集成：

```
您的代理是用 TypeScript/JavaScript 编写的吗？
  是 --> 它是 Mastra 代理吗？
    是 --> 使用 Mastra 集成 (references/integrations/mastra.md)
    否  --> 它是 LangGraph JS 代理吗？
      是 --> 使用 LangGraph JS 集成 (references/integrations/langgraph.md, JS 部分)
      否  --> 使用 BuiltInAgent 带有 MCP Apps 中间件或 HttpAgent
  否 (Python 或 .NET) -->
    哪个框架？
      LangGraph     --> references/integrations/langgraph.md
      CrewAI        --> references/integrations/crewai.md
      PydanticAI    --> references/integrations/pydantic-ai.md
      Google ADK    --> references/integrations/adk.md
      LlamaIndex    --> references/integrations/llamaindex.md
      Agno          --> references/integrations/agno.md
      Strands       --> references/integrations/strands.md
      MS Agent Fw   --> references/integrations/ms-agent-framework.md
      多个代理 (A2A) --> references/integrations/a2a.md
```

## 常见 AG-UI 协议模式

每个集成在前端方面共享这些模式。

### CopilotKit 提供程序 (layout.tsx)

```tsx
import { CopilotKit } from "@copilotkit/react-core/v2";
import "@copilotkit/react-core/v2/styles.css";

export default function RootLayout({ children }) {
  return (
    <CopilotKit runtimeUrl="/api/copilotkit" useSingleEndpoint={false}>
      {children}
    </CopilotKit>
  );
}
```

提供程序组件是 `CopilotKit`（从 `@copilotkit/react-core/v2` 导入）。没有 `agent` 属性 -- 代理是针对每个钩子通过 `agentId`（匹配 `CopilotRuntime({ agents: { ... } })` 中的键）选择的。`useSingleEndpoint={false}` 将多路由传输固定到下面的捕获所有后端路由。它是可选的 -- 忽略它让提供程序检测模式 -- 但固定它会跳过检测探测。

### API 路由模式 (route.ts)

所有集成都在 `src/app/api/copilotkit/[[...slug]]/route.ts` 创建一个 Next.js 捕获所有 API 路由，使用 V2 多路由 Hono 处理程序：

```tsx
import {
  CopilotRuntime,
  createCopilotHonoHandler,
  InMemoryAgentRunner,
} from "@copilotkit/runtime/v2";
import { handle } from "hono/vercel";
// 导入适合您框架的代理类

const runtime = new CopilotRuntime({
  agents: {
    default: new SomeAgentClass({ url: "http://localhost:8000/" }),
  },
  runner: new InMemoryAgentRunner(),
});

const app = createCopilotHonoHandler({
  runtime,
  basePath: "/api/copilotkit",
});

export const GET = handle(app);
export const POST = handle(app);
export const PATCH = handle(app);
export const DELETE = handle(app);
```

使用 `createCopilotHonoHandler`（非弃用的工厂；`createCopilotEndpoint` 是别名）。前端通过 `agentId: "default"` 选择此代理。

### 共享状态 (useAgent)

`useAgent` 仅返回 `{ agent }`。通过 `agent.state` 读取状态，通过 `agent.setState` 写入：

```tsx
const { agent } = useAgent({ agentId: "default" });
const state = (agent.state as { proverbs: string[] } | undefined) ?? {
  proverbs: [],
};
const setState = (next: { proverbs: string[] }) => agent.setState(next);
```

### 前端工具 (useFrontendTool)

```tsx
import { z } from "zod";

useFrontendTool({
  name: "setThemeColor",
  parameters: z.object({
    themeColor: z.string().describe("要设置的主题颜色。"),
  }),
  handler: async ({ themeColor }) => {
    setThemeColor(themeColor);
    return `设置主题颜色为 ${themeColor}`;
  },
});
```

### 生成式 UI (useRenderTool)

```tsx
import { z } from "zod";

useRenderTool(
  {
    name: "get_weather",
    parameters: z.object({ location: z.string() }),
    render: ({ parameters }) => <WeatherCard location={parameters.location} />,
  },
  [],
);
```

### 人在回路 (useHumanInTheLoop)

```tsx
useHumanInTheLoop(
  {
    name: "go_to_moon",
    description: "在请求时前往月球。",
    render: ({ respond, status }) => (
      <MoonCard status={status} respond={respond} />
    ),
  },
  [],
);
```

## 代理端状态管理

在代理端，共享状态根据框架不同进行管理，但协议相同 -- 代理通过发出 `STATE_SNAPSHOT` 事件来更新前端。请参阅每个集成指南以了解框架特定模式。

## 关键包

前端（所有集成）：

- `@copilotkit/react-core/v2` -- 提供程序 (`CopilotKit`)、钩子 (`useAgent`、`useFrontendTool`、`useRenderTool`、`useHumanInTheLoop`) 和聊天组件 (`CopilotChat`、`CopilotSidebar`、`CopilotPopup`)。样式：`import "@copilotkit/react-core/v2/styles.css"`。
- `@copilotkit/runtime/v2` -- 服务器运行时 (`CopilotRuntime`、`createCopilotHonoHandler`、`InMemoryAgentRunner`)

AG-UI 客户端类（每个集成选择一个）：

- `@copilotkit/runtime/langgraph` -- `LangGraphAgent`、`LangGraphHttpAgent`
- `@ag-ui/client` -- `HttpAgent`（通用，适用于任何 AG-UI 服务器）
- `@ag-ui/crewai` -- `CrewAIAgent`
- `@ag-ui/mastra` -- `MastraAgent`
- `@ag-ui/llamaindex` -- `LlamaIndexAgent`
- `@ag-ui/a2a-middleware` -- `A2AMiddlewareAgent`
- `@ag-ui/mcp-apps-middleware` -- `MCPAppsMiddleware`
