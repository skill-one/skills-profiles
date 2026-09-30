---
name: cloud
description: 为 assistant-ui 应用添加了 AssistantCloud 支持的持久化、授权和遥测功能。在以下场景中使用：跨会话线程和消息历史记录、多设备聊天、消息反馈、文件上传或授权时，通过 `@assistant-ui/ai-sdk` 的 `useChatRuntime` 传递 `cloud` 参数，`AISDKThreads({ cloud })` 用于 `AuiConfig` 主机，`@assistant-ui/cloud-ai-sdk` 的 `useCloudChat`/`useThreads` 钩子，或 `useLangGraphRuntime` 上的 `cloud` 参数。涵盖使用 `authToken`（JWT）、`apiKey` 加 `userId`/`workspaceId`（仅服务器端）或 `anonymous` 构建 `AssistantCloud`。支持 Clerk、Auth0、Supabase 和 Firebase 集成，以及后端令牌端点；提供 `cloud.threads`、`cloud.files`、`cloud.runs` 和 `cloud.telemetry` 客户端接口；并在 `CloudMessagePersistence` 上提供自定义的 `ThreadHistoryAdapter`。对于不持久化的线程、针对云 API 的 401 错误或无法保存反馈按钮的情况，请路由至此。对于 `<ThreadList />` 侧边栏 UI 使用 thread-list；对于通用适配器契约使用 runtime。
---

# assistant-ui 云服务

**始终查阅 [assistant-ui.com/llms.txt](https://www.assistant-ui.com/llms.txt) 获取最新 API。**

Assistant Cloud 是一项托管的云服务，它为任何 React 聊天界面添加了线程持久化、消息历史记录、自动生成标题、消息反馈和文件上传功能，无论是否使用 assistant-ui 的组件。一个 `AssistantCloud` 客户端支持三种集成路径：完整的 assistant-ui 运行时、独立的 AI SDK 钩子以及 LangGraph Cloud。

## 目录

- [参考资料](#参考资料) | [安装](#安装) | [快速入门：useChatRuntime](#快速入门-usechatruntime) | [AuiConfig 主机：AISDKThreads](#auiconfig-hosts-aisdkthreads) | [独立 AI SDK：useCloudChat](#独立-ai-sdk-usecloudchat) | [LangGraph](#langgraph-uselanggraphruntime) | [消息反馈](#消息反馈) | [认证](#认证) | [客户端 API](#客户端-api) | [环境变量](#环境变量) | [常见问题](#常见问题) | [相关技能](#相关技能)

## 参考资料

- [./references/persistence.md](./references/persistence.md) -- 完整的线程、消息、文件和运行客户端 API，与源代码进行验证
- [./references/authorization.md](./references/authorization.md) -- 三种认证模式和直接提供商集成（Clerk、Auth0、Supabase、Firebase）
- [./references/custom-persistence.md](./references/custom-persistence.md) -- `CloudMessagePersistence` 和 `createFormattedPersistence`，用于由云消息存储支持的自定义 `ThreadHistoryAdapter`
- [./references/auth-integrations.md](./references/auth-integrations.md) -- 使用 Auth.js (next-auth)、Clerk 和 better-auth 进行非云认证控制，以及将 AssistantCloud 与后端令牌端点配对

## 安装

```bash
npm install @assistant-ui/react @assistant-ui/ai-sdk
```

`assistant-cloud` 作为 `@assistant-ui/react` 的依赖项提供，后者重新导出 `AssistantCloud` 以供浏览器代码使用。服务器端代码（API 路由、令牌端点）如果没有理由依赖于 `@assistant-ui/react`，则直接从 `assistant-cloud` 导入 `AssistantCloud`。

## 快速入门：useChatRuntime

`useChatRuntime({ cloud })` 从 `@assistant-ui/ai-sdk` 包裹 AI SDK 的 `useChat` 并添加持久化。它在第一条消息时创建一个云线程，在消息流式传输时持久化消息，在第一条响应后生成标题，通过 `<ThreadList />` 在线程切换时加载历史记录，并针对存储的消息提交消息反馈。

```tsx
"use client";

import { useMemo } from "react";
import { AssistantCloud, AssistantRuntimeProvider } from "@assistant-ui/react";
import { useChatRuntime } from "@assistant-ui/ai-sdk";
import { Thread } from "@/components/assistant-ui/elements/thread.aui";
import { ThreadList } from "@/components/assistant-ui/elements/thread-list.aui";

export default function ChatPage() {
  const cloud = useMemo(
    () =>
      new AssistantCloud({
        baseUrl: process.env.NEXT_PUBLIC_ASSISTANT_BASE_URL!,
        anonymous: true,
      }),
    [],
  );

  const runtime = useChatRuntime({ cloud });

  return (
    <AssistantRuntimeProvider runtime={runtime}>
      <div className="grid h-dvh grid-cols-[250px_1fr] gap-x-2">
        <ThreadList />
        <Thread />
      </div>
    </AssistantRuntimeProvider>
  );
}
```

`anonymous: true` 用于演示；有关生产认证，请参阅 [认证](#认证)。`useChatRuntime` 还接受 `adapters.history`（一个 `ThreadHistoryAdapter`，必须实现 `withFormat` 以与 AI SDK 结合使用）、`adapters.feedback`（当 `cloud` 设置时默认为云反馈适配器）、`adapters.attachments`、`toCreateMessage`、`transport`（默认为调用 `/api/chat` 的 `AssistantChatTransport`）和 `onResumeError`。

## AuiConfig 主机：AISDKThreads

`AISDKThreads({ cloud })` 从 `@assistant-ui/ai-sdk` 是 `AuiConfig` 对于不是 `AssistantRuntimeProvider`（Vue 或手写的 `AssistantClient`）的主机的等效项。设置 `cloud` 后，线程列表是一个具有后台线程的 `RemoteThreadList`：每个访问过的线程在切换后保持运行并保留自己的历史记录，而新创建的线程会自动生成标题。

```tsx
import { AuiConfig, AuiProvider } from "@assistant-ui/react";
import { AISDKThreads } from "@assistant-ui/ai-sdk";

const config = AuiConfig({
  threads: AISDKThreads({ cloud }),
});
```

## 独立 AI SDK：useCloudChat

`useCloudChat()` 从 `@assistant-ui/cloud-ai-sdk` 为手写的 AI SDK UI 添加了完整的持久化，无需 assistant-ui 组件。零配置：如果没有参数，它会从 `NEXT_PUBLIC_ASSISTANT_BASE_URL` 创建一个匿名云客户端并内部管理线程。

```tsx
"use client";

import { useCloudChat } from "@assistant-ui/cloud-ai-sdk";

export default function Chat() {
  const { messages, sendMessage, threads } = useCloudChat();
  // threads.threads, threads.threadId, threads.selectThread(id | null),
  // threads.create/delete/rename/archive/unarchive/generateTitle, threads.refresh
}
```

传递 `{ cloud }` 以获取认证客户端，或传递 `{ threads: useThreads({ cloud, includeArchived }) }` 以从单独的组件（侧边栏）管理列表，同时聊天读取共享状态。`useThreads` 每次请求分页 20 个线程，并跟随 Cloud 的游标直到列表完整。该钩子还接受大多数 `useChat` 选项（`ChatInit` 上的那些）；`experimental_throttle` 和 `resume` 不受支持。完整参数和返回表：[cloud-ai-sdk API 参考](https://www.assistant-ui.com/docs/api-reference/integrations/cloud-ai-sdk)。

## LangGraph：useLangGraphRuntime

`useLangGraphRuntime` 从 `@assistant-ui/react-langgraph` 接收 `cloud` 以及 `stream`、`create`、`load` 和 `delete`，用于通过 LangGraph Cloud 后端进行云支持的线程管理。

```tsx
"use client";

import { AssistantCloud, AssistantRuntimeProvider } from "@assistant-ui/react";
import { useLangGraphRuntime, type LangChainMessage } from "@assistant-ui/react-langgraph";
import { useMemo } from "react";
import { createThread, deleteThread, getThreadState, sendMessage } from "@/lib/chatApi";

export function MyRuntimeProvider({ children }: { children: React.ReactNode }) {
  const cloud = useMemo(
    () => new AssistantCloud({ baseUrl: process.env.NEXT_PUBLIC_ASSISTANT_BASE_URL!, anonymous: true }),
    [],
  );

  const runtime = useLangGraphRuntime({
    cloud,
    stream: async function* (messages, { initialize }) {
      const { externalId } = await initialize();
      if (!externalId) throw new Error("Thread not found");
      return sendMessage({ threadId: externalId, messages });
    },
    create: async () => ({ externalId: (await createThread()).thread_id }),
    load: async (externalId) => {
      const state = await getThreadState(externalId);
      return { messages: (state.values as { messages?: LangChainMessage[] }).messages ?? [] };
    },
    delete: async (externalId) => deleteThread(externalId),
  });

  return <AssistantRuntimeProvider runtime={runtime}>{children}</AssistantRuntimeProvider>;
}
```

`create` 返回 `{ externalId }`，即您的后端 LangGraph 线程 ID；`load` 返回该线程的消息（并且可以选择中断）；`delete` 接收 `externalId`，并在提供时启用从线程列表 UI 中删除。

## 消息反馈

当 `cloud` 在 `useChatRuntime`（或 `AISDKThreads`）上设置时，运行时会自动连接默认的 `FeedbackAdapter`，该适配器调用 `cloud.threads.messages.feedback`，因此内置的点赞和点踩按钮无需额外代码即可持久化针对存储的消息。

```ts
const { feedback_id, type } = await cloud.threads.messages.feedback(threadId, messageId, {
  type: "positive", // 或 "negative"
});
```

## 认证

三种构造形式，根据您传递的字段选择：

```ts
// JWT（推荐用于生产；客户端）
const cloud = new AssistantCloud({
  baseUrl: process.env.NEXT_PUBLIC_ASSISTANT_BASE_URL!,
  authToken: async () => getAuthToken(), // 返回一个 JWT，或 null
});

// API 密钥（仅限服务器端；baseUrl 默认为 https://backend.assistant-api.com）
const cloud = new AssistantCloud({
  apiKey: process.env.ASSISTANT_API_KEY!,
  userId: user.id,
  workspaceId: user.workspaceId,
});

// 匿名（演示和原型；每个浏览器会话创建一个新用户；需要持久性时切换到 JWT 或 API 密钥认证）
const cloud = new AssistantCloud({
  baseUrl: process.env.NEXT_PUBLIC_ASSISTANT_BASE_URL!,
  anonymous: true,
});
```

认证范围限定于工作区（通常是 `userId`、`orgId_userId` 或 `projectId_userId`）。从 Assistant Cloud 仪表板连接直接提供商集成（Clerk、Auth0、Supabase、Firebase），或使用 API 密钥客户端在服务器端生成令牌，并从您的前端 `authToken` 回调获取的端点返回。有关两种路径的完整信息，请参阅 [authorization.md](./references/authorization.md)，以及 [auth-integrations.md](./references/auth-integrations.md) 以将 Cloud 与 Auth.js、Clerk 或 better-auth 会话数据配对。

## 客户端 API

每种方法都经过 `src/cloud/**` 的验证。`threadId`/`messageId` 始终是第一个参数；列表端点使用 `after`（一个游标，不是偏移量）进行分页。

```ts
// 线程
const { threads } = await cloud.threads.list({ is_archived: false, limit: 50, after: cursor });
const thread = await cloud.threads.get(threadId);
const { thread_id } = await cloud.threads.create({ last_message_at: new Date(), title, external_id, metadata });
await cloud.threads.update(threadId, { title, last_message_at, metadata, is_archived });
await cloud.threads.delete(threadId);

// 消息（创建时需要 parent_id 和 format；更新仅修改内容）
const { messages } = await cloud.threads.messages.list(threadId, { format: "ai-sdk/v6" });
const { message_id } = await cloud.threads.messages.create(threadId, { parent_id, format, content });
await cloud.threads.messages.update(threadId, messageId, { content });
await cloud.threads.messages.feedback(threadId, messageId, { type: "positive" });

// 文件
const { signedUrl, publicUrl, expiresAt } = await cloud.files.generatePresignedUploadUrl({ filename });
await fetch(signedUrl, { method: "PUT", body: file });

// 运行、项目、认证
await cloud.runs.report(runReport); // telemetry 汇报；运行时会自动调用此方法
const { threads: projectThreads } = await cloud.projects.threads.list({ limit: 50, after: cursor }); // 整个项目，不是单个工作区
const { messages: projectMessages } = await cloud.projects.threads.messages.list(threadId, { limit: 50, after: cursor });
const { token } = await cloud.auth.tokens.create(); // 服务器端，API 密钥模式
cloud.telemetry; // { enabled: boolean, beforeReport? }
```

`cloud.threads.create` 的 `last_message_at` 是必需的；创建和更新时的一切其他内容都是可选的。`CloudThread` 字段：`id`、`title`、`last_message_at`、`created_at`、`updated_at`、`is_archived`、`external_id`、`metadata`、`project_id`、`workspace_id`。`CloudMessage` 字段：`id`、`parent_id`、`height`、`format`、`content`、`created_at`、`updated_at`。`content`/`format` 对客户端是透明的；`useChatRuntime`、`AISDKThreads` 和 `useCloudChat` 都使用 `format: "ai-sdk/v6"` 并使用 AI SDK `UIMessage` 形状的 `content`。`cloud.projects.threads.messages.list` 接受 `limit`/`after` 分页，而 `cloud.threads.messages.list` 不接受。失败请求会从 `assistant-cloud` 抛出 `CloudAPIError`（带有 `.status`）；格式错误的响应会抛出 `CloudResponseError`。完整细节、自动保存行为、telemetry 字段和错误处理：[persistence.md](./references/persistence.md)。

## 环境变量

```env
NEXT_PUBLIC_ASSISTANT_BASE_URL=https://proj-[YOUR-ID].assistant-api.com  # 客户端
ASSISTANT_API_KEY=your-api-key-here                                     # 仅限服务器端，绝不能暴露给客户端
```

React Native 读取 `EXPO_PUBLIC_ASSISTANT_BASE_URL`；React Ink 读取 `ASSISTANT_BASE_URL`（没有 `NEXT_PUBLIC_` 前缀，因为没有捆绑器将其暴露给浏览器）。

## 常见问题

**线程不持久化**
- 必须将 `cloud` 传递给 `useChatRuntime`、`AISDKThreads` 或 `useCloudChat`；没有消息的线程永远不会创建。
- 确保 `authToken` 不会静默解析为 `null`：任何真实请求在到达网络之前都会抛出普通的 `Error("Authorization failed")`，这与 `CloudAPIError` 401 不同。

**401 或 "Authorization failed" 对云 API**
- 验证 `baseUrl` 与项目的 Frontend API URL 完全匹配（主机后没有尾随内容）。
- 对于 JWT 模式，请确认 `authToken` 在第一个请求之前解析；对于 Clerk 模板，JWT 中的 `aud` 声明必须是 `"assistant-ui"`。

**反馈按钮显示但无任何持久化**
- 默认反馈适配器仅在将 `cloud` 传递给运行时时才会连接；自定义的 `adapters.feedback` 完全覆盖它。

**页面重新加载后消息历史记录顺序错乱**
- 不要手动编写消息行的 `content`；它必须与活动格式的 `encode` 产生的完全相同，否则在重新加载时 `decode` 会失败。通过运行时而不是直接插入行来种子测试数据。

**从 `@assistant-ui/react-ai-sdk` 导入**
- 该包仅重新导出 `@assistant-ui/ai-sdk` 以供固定到较旧版本的安装。在新代码中从 `@assistant-ui/ai-sdk` 导入 `useChatRuntime` 和 `AssistantChatTransport`。

**匿名模式丢失历史记录**
- 匿名每个浏览器会话创建一个新用户（没有跨设备同步）；一旦需要持久性，请切换到 JWT 或 API 密钥认证。

## 相关技能

- [thread-list](../thread-list/SKILL.md) -- `<ThreadList />` 侧边栏 UI、线程 CRUD 选择器和完全自托管（非云）线程列表的 `RemoteThreadListAdapter` 合同
- [setup](../setup/SKILL.md) -- 安装 assistant-ui 并选择运行时钩子，包括 `cloud` 和 `cloud-clerk` CLI 模板
- [runtime](../runtime/SKILL.md) -- 通用适配器合同（`ThreadHistoryAdapter`、`FeedbackAdapter`、`AttachmentAdapter`），Cloud 满足这些合同
