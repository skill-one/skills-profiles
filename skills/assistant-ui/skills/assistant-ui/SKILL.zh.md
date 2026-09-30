---
name: assistant-ui
description: 助手界面（assistant-ui）概览与路由器，是一个用于构建AI聊天界面的React库，它由可组合的基础元素和样式元素目录组成。适用于高级、跨领域或架构问题：选择包、选择运行时，或理解层级（元素、基础元素、带有AuiConfig和AuiProvider的aui客户端、运行时、适配器）和消息模型。涵盖`@assistant-ui/react` 0.15.x、`@assistant-ui/ai-sdk`（用于AI SDK v7的`useChatRuntime`）、`@assistant-ui/core`、`@assistant-ui/store`、`assistant-stream`、`assistant-cloud`、LangGraph、LangChain、Google ADK、A2A、AG-UI、Eve、OpenCode和Pi适配器、`@assistant-ui/react-native`和`@assistant-ui/react-ink`绑定，以及`useAui`、`useAuiState`和`useAuiEvent`钩子。若需针对特定领域路由至专注的兄弟页面：可访问设置、元素、基础元素、运行时、工具、生成式UI、流式传输、云、线程列表、协作助手、Markdown、React-MCP、可观测性、React Native、Ink或更新。
---

# assistant-ui

**请始终查阅 [assistant-ui.com/llms.txt](https://www.assistant-ui.com/llms.txt) 获取最新 API。**

用于 AI 聊天界面的 React 库：无样式原始组件、样式元素目录、可适应任何后端的运行时，以及可选的云端持久化。当前行是 `@assistant-ui/react` 0.15.x，适用于 AI SDK v7 通过 `@assistant-ui/ai-sdk`。

## 参考

- [./references/architecture.md](./references/architecture.md) -- 层级、aui 客户端、数据流、消息模型
- [./references/packages.md](./references/packages.md) -- 每个已发布的包及其安装时机

## 何时使用

| 使用场景 | 选择 |
|----------|-----------|
| 下午内的聊天 UI | `npx assistant-ui@latest create`，然后使用 `thread` 元素 |
| 对标记有完全控制权 | 原始组件 (`ThreadPrimitive`, `ComposerPrimitive`, `MessagePrimitive`) |
| 现有 AI 后端 | 运行时适配器 (AI SDK, LangGraph, LangChain, ADK, A2A, AG-UI, Eve, OpenCode) 或 `useLocalRuntime` |
| 具有界面的工具 | `"use generative"` 工具包、工具 UI、生成式 UI |
| 多线程应用 | 线程列表元素加上 Assistant Cloud 或您自己的适配器 |
| 应用中的 Copilots | 指令、上下文、可见组件、可交互元素 |
| 移动端或终端 | `@assistant-ui/react-native`, `@assistant-ui/react-ink` |

## 架构

```
┌──────────────────────────────────────────────────────────────┐
│  Elements (styled, 复制到 components/assistant-ui/)     │
│  Primitives (unstyled, @assistant-ui/react)                  │
└───────────────────────────┬──────────────────────────────────┘
                            │ read state, call actions
┌───────────────────────────▼──────────────────────────────────┐
│  aui client: useAui, useAuiState, useAuiEvent, AuiIf         │
│  AuiConfig 通过 AssistantRuntimeProvider 提供的 scope        │
│  或 AuiProvider (@assistant-ui/store on @assistant-ui/tap)   │
└───────────────────────────┬──────────────────────────────────┘
                            │
┌───────────────────────────▼──────────────────────────────────┐
│  Runtime: AssistantRuntime → ThreadRuntime → MessageRuntime  │
│  (@assistant-ui/core, 框架无关)                          │
└───────────────────────────┬──────────────────────────────────┘
                            │
┌───────────────────────────▼──────────────────────────────────┐
│  适配器和后端: AI SDK · LangGraph · LangChain · ADK         │
│  A2A · AG-UI · Eve · OpenCode · custom · Assistant Cloud     │
└──────────────────────────────────────────────────────────────┘
```

## 选择运行时

```
Vercel AI SDK?
├─ 是 → 使用 @assistant-ui/ai-sdk 的 useChatRuntime (推荐)
└─ 否
   ├─ LangGraph 服务器 → useLangGraphRuntime (@assistant-ui/react-langgraph)
   ├─ LangChain / LangGraph useStream → useStreamRuntime (@assistant-ui/react-langchain)
   ├─ Google ADK → useAdkRuntime (@assistant-ui/react-google-adk)
   ├─ A2A 协议 → useA2ARuntime (@assistant-ui/react-a2a)
   ├─ AG-UI 协议 → useAgUiRuntime (@assistant-ui/react-ag-ui)
   ├─ Eve 代理 → useEveAgentRuntime (@assistant-ui/eve)
   ├─ OpenCode → useOpenCodeRuntime (@assistant-ui/react-opencode)
   ├─ Claude 管理代理 → useExternalStoreRuntime + useRemoteThreadListRuntime
   ├─ 状态已在 Redux/Zustand/您的 store 中 → useExternalStoreRuntime
   ├─ 使用 Assistant Transport 的自定义端点 → useAssistantTransportRuntime
   └─ 任何其他自定义 API → 使用 ChatModelAdapter 的 useLocalRuntime
```

## 核心包

| 包 | 目的 |
|---------|---------|
| `@assistant-ui/react` | 原始组件、hooks、运行时、提供者 |
| `@assistant-ui/ai-sdk` | AI SDK v7 集成 (`useChatRuntime`, `AssistantChatTransport`, `AISDKToolkit`, `frontendTools`) |
| `@assistant-ui/core` | React、React Native、Ink 共享的框架无关运行时 |
| `@assistant-ui/store` | `AuiConfig`, `AuiProvider`, `useAui` 状态层 |
| `@assistant-ui/react-markdown` | Markdown 渲染 (`MarkdownTextPrimitive`) |
| `assistant-stream` | 流协议、编码器、可恢复流 |
| `assistant-cloud` | Assistant Cloud 客户端 |
| `assistant-ui` | CLI (`create`, `init`, `add`, `update`, `upgrade`, `doctor`, `mcp`, `agent`) |

`@assistant-ui/react-ai-sdk` 为旧版安装重新导出 `@assistant-ui/ai-sdk`；新代码从 `@assistant-ui/ai-sdk` 导入。样式组件不是包：`npx assistant-ui@latest add thread` 将它们复制到 `components/assistant-ui/elements/`。有关完整清单，请参阅 [./references/packages.md](./references/packages.md)。

## 快速入门

```tsx
"use client";

import { AssistantRuntimeProvider } from "@assistant-ui/react";
import { useChatRuntime } from "@assistant-ui/ai-sdk";
import { Thread } from "@/components/assistant-ui/elements/thread.aui";

export default function Chat() {
  const runtime = useChatRuntime();
  return (
    <AssistantRuntimeProvider runtime={runtime}>
      <Thread />
    </AssistantRuntimeProvider>
  );
}
```

`useChatRuntime()` 通过 `AssistantChatTransport` 发布到 `/api/chat`，该传输也转发前端工具和系统指令。通过传递 `new AssistantChatTransport({ api })` 来更改端点。

## 状态访问

`aui` 的 scope 访问器是属性；scope 上的方法是带括号的。选择器每个返回一个原始组件或稳定引用。

```tsx
import { useAui, useAuiState, useAuiEvent } from "@assistant-ui/react";

const aui = useAui();
aui.thread.append({ role: "user", content: [{ type: "text", text: "Hi" }] });
aui.thread.cancelRun();
aui.thread.composer().send();
aui.threads.switchToNewThread();

const messages = useAuiState((s) => s.thread.messages);
const isRunning = useAuiState((s) => s.thread.isRunning);

useAuiEvent("threads.selectionChanged", ({ threadId, previousThreadId }) => {});
```

## 提供Scope

工具、建议、可交互元素、MCP 管理器和其他 scope 通过 `AuiConfig` 声明并传递给提供者；`useAui()` 不需要参数。

```tsx
import { AssistantRuntimeProvider, AuiConfig, Suggestions, Tools } from "@assistant-ui/react";
import { useChatRuntime } from "@assistant-ui/ai-sdk";
import toolkit from "./toolkit";

const runtime = useChatRuntime();
const config = AuiConfig({
  tools: Tools({ toolkit }),
  suggestions: Suggestions(["What can you do?", "Summarize this page"]),
});

<AssistantRuntimeProvider runtime={runtime} config={config}>{children}</AssistantRuntimeProvider>;
```

嵌套 scope 使用 `<AuiProvider extends={useAui()} config={config}>`；隔离根使用 `extends={null}`。

## 相关技能

- [setup](../setup/SKILL.md) -- CLI、模板、运行时适配器、平台
- [elements](../elements/SKILL.md) -- 样式组件目录及其安装和覆盖方法
- [primitives](../primitives/SKILL.md) -- 无样式构建块和 composer 功能
- [runtime](../runtime/SKILL.md) -- 运行时、aui 客户端、适配器、事件
- [tools](../tools/SKILL.md) -- 工具包、工具 UI、批准、MCP、WebMCP
- [generative-ui](../generative-ui/SKILL.md) -- `present` 工具和组件词汇表
- [streaming](../streaming/SKILL.md) -- assistant-stream、传输、可恢复流
- [cloud](../cloud/SKILL.md) -- Assistant Cloud 持久化和认证
- [thread-list](../thread-list/SKILL.md) -- 多线程管理
- [copilots](../copilots/SKILL.md) -- 将助手锚定在您的应用中
- [markdown](../markdown/SKILL.md) -- markdown、代码、数学、图表
- [react-mcp](../react-mcp/SKILL.md) -- 用户管理的 MCP 服务器
- [observability](../observability/SKILL.md) -- 跟踪和跨度可视化
- [react-native](../react-native/SKILL.md) -- Expo 和 React Native
- [ink](../ink/SKILL.md) -- Ink 终端聊天
- [update](../update/SKILL.md) -- 升级和迁移
