# Convex 实时

使用 Convex 的实时订阅、乐观更新、智能缓存和基于游标的分页构建响应式应用程序。

## 文档来源

在实现之前，不要假设；获取最新文档：

- 主要：https://docs.convex.dev/client/react
- 乐观更新：https://docs.convex.dev/client/react/optimistic-updates
- 分页：https://docs.convex.dev/database/pagination
- 更广泛的背景：https://docs.convex.dev/llms.txt

## 说明

### Convex 实时的工作原理

1. **自动订阅** - useQuery 创建自动更新的订阅
2. **智能缓存** - 查询结果被缓存并在组件之间共享
3. **一致性** - 所有订阅都看到数据库的一致视图
4. **高效更新** - 仅在相关数据变化时重新渲染

### 基本订阅

```typescript
// 带有实时数据的 React 组件
import { useQuery } from "convex/react";
import { api } from "../convex/_generated/api";

function TaskList({ userId }: { userId: Id<"users"> }) {
  // 自动订阅并实时更新
  const tasks = useQuery(api.tasks.list, { userId });

  if (tasks === undefined) {
    return <div>加载中...</div>;
  }

  return (
    <ul>
      {tasks.map((task) => (
        <li key={task._id}>{task.title}</li>
      ))}
    </ul>
  );
}
```

### 条件查询

```typescript
import { useQuery } from "convex/react";
import { api } from "../convex/_generated/api";

function UserProfile({ userId }: { userId: Id<"users"> | null }) {
  // 当 userId 为 null 时跳过查询
  const user = useQuery(
    api.users.get,
    userId ? { userId } : "skip"
  );

  if (userId === null) {
    return <div>选择一个用户</div>;
  }

  if (user === undefined) {
    return <div>加载中...</div>;
  }

  return <div>{user.name}</div>;
}
```

### 带实时更新的变异

```typescript
import { useMutation, useQuery } from "convex/react";
import { api } from "../convex/_generated/api";

function TaskManager({ userId }: { userId: Id<"users"> }) {
  const tasks = useQuery(api.tasks.list, { userId });
  const createTask = useMutation(api.tasks.create);
  const toggleTask = useMutation(api.tasks.toggle);

  const handleCreate = async (title: string) => {
    // 变异触发数据变化时的自动重新渲染
    await createTask({ title, userId });
  };

  const handleToggle = async (taskId: Id<"tasks">) => {
    await toggleTask({ taskId });
  };

  return (
    <div>
      <button onClick={() => handleCreate("新任务")}>添加任务</button>
      <ul>
        {tasks?.map((task) => (
          <li key={task._id} onClick={() => handleToggle(task._id)}>
            {task.completed ? "✓" : "○"} {task.title}
          </li>
        ))}
      </ul>
    </div>
  );
}
```

### 乐观更新

在服务器确认之前立即显示更改：

```typescript
import { useMutation, useQuery } from "convex/react";
import { api } from "../convex/_generated/api";
import { Id } from "../convex/_generated/dataModel";

function TaskItem({ task }: { task: Task }) {
  const toggleTask = useMutation(api.tasks.toggle).withOptimisticUpdate(
    (localStore, args) => {
      const { taskId } = args;
      const currentValue = localStore.getQuery(api.tasks.get, { taskId });
      
      if (currentValue !== undefined) {
        localStore.setQuery(api.tasks.get, { taskId }, {
          ...currentValue,
          completed: !currentValue.completed,
        });
      }
    }
  );

  return (
    <div onClick={() => toggleTask({ taskId: task._id })}>
      {task.completed ? "✓" : "○"} {task.title}
    </div>
  );
}
```

### 列表的乐观更新

```typescript
import { useMutation } from "convex/react";
import { api } from "../convex/_generated/api";

function useCreateTask(userId: Id<"users">) {
  return useMutation(api.tasks.create).withOptimisticUpdate(
    (localStore, args) => {
      const { title, userId } = args;
      const currentTasks = localStore.getQuery(api.tasks.list, { userId });
      
      if (currentTasks !== undefined) {
        // 向列表添加乐观任务
        const optimisticTask = {
          _id: crypto.randomUUID() as Id<"tasks">,
          _creationTime: Date.now(),
          title,
          userId,
          completed: false,
        };
        
        localStore.setQuery(api.tasks.list, { userId }, [
          optimisticTask,
          ...currentTasks,
        ]);
      }
    }
  );
}
```

### 基于游标的分页

```typescript
// convex/messages.ts
import { query } from "./_generated/server";
import { v } from "convex/values";
import { paginationOptsValidator } from "convex/server";

export const listPaginated = query({
  args: {
    channelId: v.id("channels"),
    paginationOpts: paginationOptsValidator,
  },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("messages")
      .withIndex("by_channel", (q) => q.eq("channelId", args.channelId))
      .order("desc")
      .paginate(args.paginationOpts);
  },
});
```

```typescript
// 带有分页的 React 组件
import { usePaginatedQuery } from "convex/react";
import { api } from "../convex/_generated/api";

function MessageList({ channelId }: { channelId: Id<"channels"> }) {
  const { results, status, loadMore } = usePaginatedQuery(
    api.messages.listPaginated,
    { channelId },
    { initialNumItems: 20 }
  );

  return (
    <div>
      {results.map((message) => (
        <div key={message._id}>{message.content}</div>
      ))}
      
      {status === "CanLoadMore" && (
        <button onClick={() => loadMore(20)}>加载更多</button>
      )}
      
      {status === "LoadingMore" && <div>加载中...</div>}
      
      {status === "Exhausted" && <div>没有更多消息</div>}
    </div>
  );
}
```

### 无限滚动模式

```typescript
import { usePaginatedQuery } from "convex/react";
import { useEffect, useRef } from "react";
import { api } from "../convex/_generated/api";

function InfiniteMessageList({ channelId }: { channelId: Id<"channels"> }) {
  const { results, status, loadMore } = usePaginatedQuery(
    api.messages.listPaginated,
    { channelId },
    { initialNumItems: 20 }
  );
  
  const observerRef = useRef<IntersectionObserver>();
  const loadMoreRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (observerRef.current) {
      observerRef.current.disconnect();
    }

    observerRef.current = new IntersectionObserver((entries) => {
      if (entries[0].isIntersecting && status === "CanLoadMore") {
        loadMore(20);
      }
    });

    if (loadMoreRef.current) {
      observerRef.current.observe(loadMoreRef.current);
    }

    return () => observerRef.current?.disconnect();
  }, [status, loadMore]);

  return (
    <div>
      {results.map((message) => (
        <div key={message._id}>{message.content}</div>
      ))}
      <div ref={loadMoreRef} style={{ height: 1 }} />
      {status === "LoadingMore" && <div>加载中...</div>}
    </div>
  );
}
```

### 多个订阅

```typescript
import { useQuery } from "convex/react";
import { api } from "../convex/_generated/api";

function Dashboard({ userId }: { userId: Id<"users"> }) {
  // 多个订阅独立更新
  const user = useQuery(api.users.get, { userId });
  const tasks = useQuery(api.tasks.list, { userId });
  const notifications = useQuery(api.notifications.unread, { userId });

  const isLoading = user === undefined || 
                    tasks === undefined || 
                    notifications === undefined;

  if (isLoading) {
    return <div>加载中...</div>;
  }

  return (
    <div>
      <h1>欢迎，{user.name}</h1>
      <p>你有 {tasks.length} 个任务</p>
      <p>{notifications.length} 个未读通知</p>
    </div>
  );
}
```

## 示例

### 实时聊天应用程序

```typescript
// convex/messages.ts
import { query, mutation } from "./_generated/server";
import { v } from "convex/values";

export const list = query({
  args: { channelId: v.id("channels") },
  returns: v.array(v.object({
    _id: v.id("messages"),
    _creationTime: v.number(),
    content: v.string(),
    authorId: v.id("users"),
    authorName: v.string(),
  })),
  handler: async (ctx, args) => {
    const messages = await ctx.db
      .query("messages")
      .withIndex("by_channel", (q) => q.eq("channelId", args.channelId))
      .order("desc")
      .take(100);

    // 富含作者名称
    return Promise.all(
      messages.map(async (msg) => {
        const author = await ctx.db.get(msg.authorId);
        return {
          ...msg,
          authorName: author?.name ?? "未知",
        };
      })
    );
  },
});

export const send = mutation({
  args: {
    channelId: v.id("channels"),
    authorId: v.id("users"),
    content: v.string(),
  },
  returns: v.id("messages"),
  handler: async (ctx, args) => {
    return await ctx.db.insert("messages", {
      channelId: args.channelId,
      authorId: args.authorId,
      content: args.content,
    });
  },
});
```

```typescript
// ChatRoom.tsx
import { useQuery, useMutation } from "convex/react";
import { api } from "../convex/_generated/api";
import { useState, useRef, useEffect } from "react";

function ChatRoom({ channelId, userId }: Props) {
  const messages = useQuery(api.messages.list, { channelId });
  const sendMessage = useMutation(api.messages.send);
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 新消息自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    await sendMessage({
      channelId,
      authorId: userId,
      content: input.trim(),
    });
    setInput("");
  };

  return (
    <div className="chat-room">
      <div className="messages">
        {messages?.map((msg) => (
          <div key={msg._id} className="message">
            <strong>{msg.authorName}:</strong> {msg.content}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      
      <form onSubmit={handleSend}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="输入消息..."
        />
        <button type="submit">发送</button>
      </form>
    </div>
  );
}
```

## 最佳实践

- 除非明确指示，否则不要运行 `npx convex deploy`
- 除非明确指示，否则不要运行任何 git 命令
- 使用 "skip" 进行条件查询，而不是条件调用钩子
- 实现乐观更新以获得更好的感知性能
- 使用 usePaginatedQuery 处理大型数据集
- 明确处理未定义状态（加载中）
- 通过记忆化派生数据来避免不必要的重新渲染

## 常见陷阱

1. **条件钩子调用** - 使用 "skip" 而不是 if 语句
2. **未处理加载状态** - 始终检查未定义
3. **缺少乐观更新回滚** - 乐观更新在出错时自动回滚
4. **分页时过度获取** - 使用适当的页面大小
5. **忽略订阅清理** - React 自动处理此问题

## 参考

- Convex 文档：https://docs.convex.dev/
- Convex LLMs.txt：https://docs.convex.dev/llms.txt
- React 客户端：https://docs.convex.dev/client/react
- 乐观更新：https://docs.convex.dev/client/react/optimistic-updates
- 分页：https://docs.convex.dev/database/pagination
