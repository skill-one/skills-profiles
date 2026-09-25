# assistant-ui

**请始终查阅 [assistant-ui.com/llms.txt](https://www.assistant-ui.com/llms.txt) 获取最新 API。**

用于 AI 聊天界面的 React 库：无样式原始组件、样式元素目录、可适配任何后端的运行时，以及可选的云端持久化。当前版本为 `@assistant-ui/react` 0.15.x，适用于 AI SDK v7 及 `@assistant-ui/ai-sdk`。

## 参考

- [./references/architecture.md](./references/architecture.md) -- 层级结构、aui 客户端、数据流、消息模型
- [./references/packages.md](./references/packages.md) -- 所有已发布的包及其安装时机

## 何时使用

| 使用场景 | 选择 |
|----------|-----------|
| 下午使用聊天界面 | `npx assistant-ui@latest create`，然后使用 `thread` 元素 |
| 对标记语言完全控制 | 原始组件 (`ThreadPrimitive`, `ComposerPrimitive`, `MessagePrimitive`) |
| 现有 AI 后端 | 运行时适配器 (AI SDK, LangGraph, LangChain, ADK, A2A, AG-UI, Eve, OpenCode) 或 `useLocalRuntime` |
| 具有界面的工具 | `"use generative"` 工具包、工具 UI、生成式 UI |
| 多线程应用 | 线程列表元素加上 Assistant Cloud 或您自己的适配器 |
| 应用中的协程 | 指令、上下文、可见组件、可交互元素 |
| 移动端或终端 | `@assistant-ui/react-native`, `@assistant-ui/react-ink` |

## 架构

```
┌──────────────────────────────────────────────────────────────┐
│  Elements (styled, 复制到 components/assistant-ui/)     │
│  Primitives (无样式, @assistant-ui/react)                  │
└───────────────────────────┬──────────────────────────────────┘
                            │ 读取状态, 调用操作
┌───────────────────────────▼──────────────────────────────────┐
│  aui 客户端: useAui, useAuiState, useAuiEvent, AuiIf         │
│  通过 AssistantRuntimeProvider 或 AuiProvider (@assistant-ui/store on @assistant-ui/tap) 提供的 AuiConfig 范围 │
└───────────────────────────┬──────────────────────────────────┘
                            │
┌───────────────────────────▼──────────────────────────────────┐
│  运行时: AssistantRuntime → ThreadRuntime → MessageRuntime  │
│  (@assistant-ui/core, 框架无关)                          │
└───────────────────────────┬──────────────────────────────────┘
                            │
┌───────────────────────────▼──────────────────────────────────┐
│  适配器和后端: AI SDK · LangGraph · LangChain · ADK         │
│  A2A · AG-UI · Eve · OpenCode · 自定义 · Assistant Cloud     │
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
   ├─ 使用 Assistant Transport 协议的自定义端点 → useAssistantTransportRuntime
   └─ 任何其他自定义 API → 使用 ChatModelAdapter 的 useLocalRuntime
```

## 核心包

| 包 | 目的 |
|---------|---------|
| `@assistant-ui/react` | 原始组件、钩子、运行时、提供者 |
| `@assistant-ui/ai-sdk` | AI SDK v7 集成 (`useChatRuntime`, `AssistantChatTransport`, `AISDKToolkit`, `frontendTools`) |
| `@assistant-ui/core` | React、React Native、Ink 共享的框架无关运行时 |
| `@assistant-ui/store` | `AuiConfig`, `AuiProvider`, `useAui` 状态层 |
| `@assistant-ui/react-markdown` | Markdown 渲染 (`MarkdownTextPrimitive`) |
| `assistant-stream` | 流协议、编码器、可恢复流 |
| `assistant-cloud` | Assistant Cloud 客户端 |
| `assistant-ui` | CLI (`create`, `init`, `add`, `update`, `upgrade`, `doctor`, `mcp`, `agent`) |

`@assistant-ui/react-ai-sdk` 为旧版安装重新导出 `@assistant-ui/ai-sdk`；新代码从 `@assistant-ui/ai-sdk` 导入。样式组件不是包：`npx assistant-ui@latest add thread` 将它们复制到 `components/assistant-ui/elements/`。请参阅 [./references/packages.md](./references/packages.md) 获取完整清单。

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

`aui` 范围访问器是属性；范围方法保留其括号。选择器每个返回一个原始组件或稳定引用。

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

## 提供范围

工具、建议、可交互元素、MCP 管理器和其他范围通过 `AuiConfig` 声明并传递给提供者；`useAui()` 不需要参数。

```tsx
import { AssistantRuntimeProvider, AuiConfig, Suggestions, Tools } from "@assistant-ui/react";
import { useChatRuntime } from "@assistant-ui/ai-sdk";
import toolkit from "./toolkit";

const runtime = useChatRuntime();
const config = AuiConfig({
  tools: Tools({ toolkit }),
  suggestions: Suggestions(["你能做什么？", "总结这一页"]),
});

<AssistantRuntimeProvider runtime={runtime} config={config}>{children}</AssistantRuntimeProvider>;
```

嵌套范围使用 `<AuiProvider extends={useAui()} config={config}>`；独立根使用 `extends={null}`。

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
- [copilots](../copilots/SKILL.md) -- 将助手嵌入您的应用
- [markdown](../markdown/SKILL.md) -- Markdown、代码、数学、图表
- [react-mcp](../react-mcp/SKILL.md) -- 用户管理的 MCP 服务器
- [observability](../observability/SKILL.md) -- 跟踪和跨度可视化
- [react-native](../react-native/SKILL.md) -- Expo 和 React Native
- [ink](../ink/SKILL.md) -- Ink 终端聊天
- [update](../update/SKILL.md) -- 升级和迁移
