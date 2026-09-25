# assistant-ui 线程列表

**始终查阅 [assistant-ui.com/llms.txt](https://www.assistant-ui.com/llms.txt) 获取最新 API。**

一个运行时从内存中的对话开始。仅在人们需要创建、选择和管理多个对话时才添加线程列表。在选择 UI 之前，选择管理的云端路径、后端适配器或外部存储。

## 参考

- [./references/management.md](./references/management.md) -- CRUD、初始化、刷新、分页、元数据、标识符
- [./references/custom-ui.md](./references/custom-ui.md) -- 每个线程列表的基本元素、自定义布局、搜索、分组和已安装元素组合
- [./references/remote-adapter.md](./references/remote-adapter.md) -- 远程适配器契约、历史记录适配器、存储条目、认证刷新和外部存储

## 快速入门

使用 `npx assistant-ui@latest add thread-list` 安装连接的运行时列表。它创建 `components/assistant-ui/elements/thread-list.aui.tsx`。将 `AssistantCloud` 实例传递给 `useChatRuntime` 以管理线程，然后在提供程序下方渲染列表和活动线程。

```tsx
"use client";

import { AssistantRuntimeProvider } from "@assistant-ui/react";
import { useChatRuntime } from "@assistant-ui/ai-sdk";
import { AssistantCloud } from "assistant-cloud";
import { Thread } from "@/components/assistant-ui/elements/thread.aui";
import { ThreadList } from "@/components/assistant-ui/elements/thread-list.aui";

const cloud = new AssistantCloud({
  baseUrl: process.env.NEXT_PUBLIC_ASSISTANT_BASE_URL,
  anonymous: true,
});

export function Chat() {
  const runtime = useChatRuntime({ cloud });

  return (
    <AssistantRuntimeProvider runtime={runtime}>
      <div className="flex h-dvh">
        <aside className="w-72 border-e p-2">
          <ThreadList />
        </aside>
        <main className="min-w-0 flex-1">
          <Thread />
        </main>
      </div>
    </AssistantRuntimeProvider>
  );
}
```

当项目已经使用 shadcn 侧边栏基本元素时，使用完整侧边栏外壳。`ThreadListSidebar` 渲染运行时连接的线程列表本身，因此不要在其内部也挂载 `ThreadList`。

```tsx
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar";
import { Thread } from "@/components/assistant-ui/elements/thread.aui";
import { ThreadListSidebar } from "@/components/assistant-ui/elements/threadlist-sidebar.aui";

export function ChatLayout() {
  return (
    <SidebarProvider>
      <ThreadListSidebar />
      <SidebarInset>
        <Thread />
      </SidebarInset>
    </SidebarProvider>
  );
}
```

`ThreadListSidebar` 仍然需要第一个示例中的 `AssistantRuntimeProvider` 祖先。其 `SidebarProvider` 是独立的布局上下文。

## 线程操作

使用 `useAui()` 进行命令。作用域访问器是属性，因此使用 `aui.threads` 和 `aui.threadListItem`，而不是 `aui.threads()`。使用 `useAuiState` 独立读取每个状态值。选择器可以返回一个基本值或一个稳定的运行时引用，但永远不会返回对象或数组字面量。

```tsx
import { useAui, useAuiState } from "@assistant-ui/react";

export function ThreadControls({ threadId }: { threadId: string }) {
  const aui = useAui();
  const activeThreadId = useAuiState((s) => s.threads.mainThreadId);
  const threadIds = useAuiState((s) => s.threads.threadIds);
  const isLoading = useAuiState((s) => s.threads.isLoading);

  const item = aui.threads.item({ id: threadId });

  return (
    <div>
      <p>{threadIds.length} 个对话</p>
      <p>{activeThreadId === threadId ? "当前" : "可用"}</p>
      <button disabled={isLoading} onClick={() => aui.threads.switchToNewThread()}>
        新对话
      </button>
      <button onClick={() => item.switchTo()}>打开</button>
      <button onClick={() => item.rename("项目规划")}>重命名</button>
      <button onClick={() => item.archive()}>归档</button>
      <button onClick={() => item.delete()}>删除</button>
    </div>
  );
}
```

在线程项基本元素内部，`s.threadListItem` 是作用域内的项。当行只需要一个值时，不要选择整个状态对象，而是单独选择字段。

```tsx
import { useAuiState } from "@assistant-ui/react";

export function ThreadRunningBadge() {
  const isRunning = useAuiState((s) => s.threadListItem.isRunning);
  return isRunning ? <span>工作中</span> : null;
}
```

## 组合自定义列表

当已安装元素的日期分组、搜索或视觉处理与产品不匹配时，从三个基本元素命名空间开始。`Items` 提供当前项作用域及其子项渲染函数，替换已弃用的 `components` 属性。

```tsx
import {
  ThreadListItemMorePrimitive,
  ThreadListItemPrimitive,
  ThreadListPrimitive,
} from "@assistant-ui/react";

export function CustomThreadList() {
  return (
    <ThreadListPrimitive.Root className="flex flex-col gap-1">
      <ThreadListPrimitive.New>New conversation</ThreadListPrimitive.New>
      <ThreadListPrimitive.Items>
        {({ threadListItem }) => (
          <ThreadListItemPrimitive.Root data-thread-id={threadListItem.id}>
            <ThreadListItemPrimitive.Trigger className="flex-1 text-left">
              <ThreadListItemPrimitive.Title fallback="New conversation" />
            </ThreadListItemPrimitive.Trigger>
            <ThreadListItemMorePrimitive.Root sharedFocusGroup>
              <ThreadListItemMorePrimitive.Trigger>
                More
              </ThreadListItemMorePrimitive.Trigger>
              <ThreadListItemMorePrimitive.Content>
                <ThreadListItemPrimitive.Archive asChild>
                  <ThreadListItemMorePrimitive.Item>
                    Archive
                  </ThreadListItemMorePrimitive.Item>
                </ThreadListItemPrimitive.Archive>
                <ThreadListItemMorePrimitive.Separator />
                <ThreadListItemPrimitive.Delete asChild>
                  <ThreadListItemMorePrimitive.Item>
                    Delete
                  </ThreadListItemMorePrimitive.Item>
                </ThreadListItemPrimitive.Delete>
              </ThreadListItemMorePrimitive.Content>
            </ThreadListItemMorePrimitive.Root>
          </ThreadListItemPrimitive.Root>
        )}
      </ThreadListPrimitive.Items>
    </ThreadListPrimitive.Root>
  );
}
```

有关归档行、加载更多、自定义搜索、分组、键盘行为和完整部分参考，请参阅 [自定义 UI](./references/custom-ui.md)。

## 选择多对话路径

| 路径 | 使用它时 | 线程元数据存储在 |
| --- | --- | --- |
| `AssistantCloud` | 你需要管理的认证、持久性、同步和标题 | assistant-cloud |
| `useRemoteThreadListRuntime` with `RemoteThreadListAdapter` | 基于LocalRuntime的运行时使用应用程序的数据库 | 你的后端 |
| `ExternalStoreThreadListAdapter` | ExternalStoreRuntime已经拥有消息和选择 | 你的状态存储 |

上面的云快速入门是管理路径。远程和外部存储路径具有不同的所有权和生命周期要求。请遵循 [远程适配器](./references/remote-adapter.md)，而不是混合它们的 API。

## 观察选择

`threads.selectionChanged` 替换了旧的每个项切换事件。它为每个选择更改运行，并提供两个 ID。它不会在挂载时对初始选择运行。

```tsx
import { useAuiEvent } from "@assistant-ui/react";

export function SelectionTelemetry() {
  useAuiEvent(
    "threads.selectionChanged",
    ({ threadId, previousThreadId }) => {
      recordThreadSelection({ threadId, previousThreadId });
    },
  );
  return null;
}
```

当此监听器在项行内部时，比较 `threadId` 与 `s.threadListItem.id`，如果它只在该行变为当前时才应做出反应。

## 常见问题

**列表渲染但没有对话持久化**

- 默认运行时是一个内存中的线程。传递 `cloud`，使用 `RemoteThreadListAdapter`，或提供 `ExternalStoreThreadListAdapter`。
- 远程适配器仅管理元数据。为每个对话的消息添加历史记录适配器或另一个消息持久化层。

**线程切换使用过时的消息**

- 在 `RemoteThreadList` 存储条目中，将线程工厂包装在 `withKey(id, ...)` 中，以便为选定的 ID 挂载历史记录适配器。
- 仅在运行应在选择更改后继续并且可以在内存中保留访问过的线程时使用 `backgroundThreads`。

**侧边栏没有运行时**

- `ThreadList` 和 `ThreadListSidebar` 需要一个 `AssistantRuntimeProvider` 祖先。
- `ThreadListSidebar` 还需要 shadcn 的 `SidebarProvider`，因为它是一个侧边栏外壳，而不是运行时提供程序。

**行在每次无关的存储更改时重新渲染**

- 将返回对象或数组字面量的选择器替换为单独的 `useAuiState` 调用。直接返回 `s.threads.threadIds` 是安全的，因为它是由运行时提供的稳定引用。

**切换处理程序在升级后停止触发**

- 订阅 `threads.selectionChanged` 并使用 `previousThreadId`。已退役的 `threadListItem.switchedTo` 和 `threadListItem.switchedAway` 事件不是当前集成点。

## 相关技能

- [runtime](../runtime/SKILL.md) -- 选择和配置拥有活动对话的运行时
- [cloud](../cloud/SKILL.md) -- 配置 AssistantCloud 认证、持久性和管理线程
- [elements](../elements/SKILL.md) -- 安装、样式和自定义运行时连接的注册组件
