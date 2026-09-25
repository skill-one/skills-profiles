# 凸函数代理

使用凸函数构建持久化、有状态的AI代理，包括线程管理、工具集成、流式响应、RAG模式和工作流编排。

## 文档来源

在实施之前，不要假设；获取最新文档：

- 主要：https://docs.convex.dev/ai
- 凸函数代理组件：https://www.npmjs.com/package/@convex-dev/agent
- 更广泛的背景：https://docs.convex.dev/llms.txt

## 说明

### 为什么选择凸函数用于AI代理

- **持久化状态** - 对话历史在重启后仍然存在
- **实时更新** - 自动将响应流式传输到客户端
- **工具执行** - 将凸函数作为代理工具运行
- **持久化工作流** - 可靠的长运行代理任务
- **内置RAG** - 向量搜索用于知识检索

### 设置凸函数代理

```bash
npm install @convex-dev/agent ai openai
```

```typescript
// convex/agent.ts
import { Agent } from "@convex-dev/agent";
import { components } from "./_generated/api";
import { OpenAI } from "openai";

const openai = new OpenAI();

export const agent = new Agent(components.agent, {
  chat: openai.chat,
  textEmbedding: openai.embeddings,
});
```

### 线程管理

```typescript
// convex/threads.ts
import { mutation, query } from "./_generated/server";
import { v } from "convex/values";
import { agent } from "./agent";

// 创建新的对话线程
export const createThread = mutation({
  args: {
    userId: v.id("users"),
    title: v.optional(v.string()),
  },
  returns: v.id("threads"),
  handler: async (ctx, args) => {
    const threadId = await agent.createThread(ctx, {
      userId: args.userId,
      metadata: {
        title: args.title ?? "新对话",
        createdAt: Date.now(),
      },
    });
    return threadId;
  },
});

// 列出用户的线程
export const listThreads = query({
  args: { userId: v.id("users") },
  returns: v.array(v.object({
    _id: v.id("threads"),
    title: v.string(),
    lastMessageAt: v.optional(v.number()),
  })),
  handler: async (ctx, args) => {
    return await agent.listThreads(ctx, {
      userId: args.userId,
    });
  },
});

// 获取线程消息
export const getMessages = query({
  args: { threadId: v.id("threads") },
  returns: v.array(v.object({
    role: v.string(),
    content: v.string(),
    createdAt: v.number(),
  })),
  handler: async (ctx, args) => {
    return await agent.getMessages(ctx, {
      threadId: args.threadId,
    });
  },
});
```

### 发送消息和流式响应

```typescript
// convex/chat.ts
import { action } from "./_generated/server";
import { v } from "convex/values";
import { agent } from "./agent";
import { internal } from "./_generated/api";

export const sendMessage = action({
  args: {
    threadId: v.id("threads"),
    message: v.string(),
  },
  returns: v.null(),
  handler: async (ctx, args) => {
    // 向线程添加用户消息
    await ctx.runMutation(internal.chat.addUserMessage, {
      threadId: args.threadId,
      content: args.message,
    });

    // 使用流式传输生成AI响应
    const response = await agent.chat(ctx, {
      threadId: args.threadId,
      messages: [{ role: "user", content: args.message }],
      stream: true,
      onToken: async (token) => {
        // 通过mutation将token流式传输到客户端
        await ctx.runMutation(internal.chat.appendToken, {
          threadId: args.threadId,
          token,
        });
      },
    });

    // 保存完整响应
    await ctx.runMutation(internal.chat.saveResponse, {
      threadId: args.threadId,
      content: response.content,
    });

    return null;
  },
});
```

### 工具集成

定义代理可以使用的工具：

```typescript
// convex/tools.ts
import { tool } from "@convex-dev/agent";
import { v } from "convex/values";
import { api } from "./_generated/api";

// 搜索知识库的工具
export const searchKnowledge = tool({
  name: "search_knowledge",
  description: "搜索知识库以获取相关信息",
  parameters: v.object({
    query: v.string(),
    limit: v.optional(v.number()),
  }),
  handler: async (ctx, args) => {
    const results = await ctx.runQuery(api.knowledge.search, {
      query: args.query,
      limit: args.limit ?? 5,
    });
    return results;
  },
});

// 创建任务的工具
export const createTask = tool({
  name: "create_task",
  description: "为用户创建新任务",
  parameters: v.object({
    title: v.string(),
    description: v.optional(v.string()),
    dueDate: v.optional(v.string()),
  }),
  handler: async (ctx, args) => {
    const taskId = await ctx.runMutation(api.tasks.create, {
      title: args.title,
      description: args.description,
      dueDate: args.dueDate ? new Date(args.dueDate).getTime() : undefined,
    });
    return { success: true, taskId };
  },
});

// 获取天气的工具
export const getWeather = tool({
  name: "get_weather",
  description: "获取某个位置的当前天气",
  parameters: v.object({
    location: v.string(),
  }),
  handler: async (ctx, args) => {
    const response = await fetch(
      `https://api.weather.com/current?location=${encodeURIComponent(args.location)}`
    );
    return await response.json();
  },
});
```

### 带有工具的代理

```typescript
// convex/assistant.ts
import { action } from "./_generated/server";
import { v } from "convex/values";
import { agent } from "./agent";
import { searchKnowledge, createTask, getWeather } from "./tools";

export const chat = action({
  args: {
    threadId: v.id("threads"),
    message: v.string(),
  },
  returns: v.string(),
  handler: async (ctx, args) => {
    const response = await agent.chat(ctx, {
      threadId: args.threadId,
      messages: [{ role: "user", content: args.message }],
      tools: [searchKnowledge, createTask, getWeather],
      systemPrompt: `你是一个有帮助的助手。你可以使用工具：
        - 搜索知识库获取信息
        - 为用户创建任务
        - 获取天气信息
        在适当的时候使用这些工具来帮助用户。`,
    });

    return response.content;
  },
});
```

### RAG（检索增强生成）

```typescript
// convex/knowledge.ts
import { mutation, query } from "./_generated/server";
import { v } from "convex/values";
import { agent } from "./agent";

// 向知识库添加文档
export const addDocument = mutation({
  args: {
    title: v.string(),
    content: v.string(),
    metadata: v.optional(v.object({
      source: v.optional(v.string()),
      category: v.optional(v.string()),
    })),
  },
  returns: v.id("documents"),
  handler: async (ctx, args) => {
    // 生成嵌入
    const embedding = await agent.embed(ctx, args.content);

    return await ctx.db.insert("documents", {
      title: args.title,
      content: args.content,
      embedding,
      metadata: args.metadata ?? {},
      createdAt: Date.now(),
    });
  },
});

// 搜索知识库
export const search = query({
  args: {
    query: v.string(),
    limit: v.optional(v.number()),
  },
  returns: v.array(v.object({
    _id: v.id("documents"),
    title: v.string(),
    content: v.string(),
    score: v.number(),
  })),
  handler: async (ctx, args) => {
    const results = await agent.search(ctx, {
      query: args.query,
      table: "documents",
      limit: args.limit ?? 5,
    });

    return results.map((r) => ({
      _id: r._id,
      title: r.title,
      content: r.content,
      score: r._score,
    }));
  },
});
```

### 工作流编排

```typescript
// convex/workflows.ts
import { action, internalMutation } from "./_generated/server";
import { v } from "convex/values";
import { agent } from "./agent";
import { internal } from "./_generated/api";

// 多步骤研究工作流
export const researchTopic = action({
  args: {
    topic: v.string(),
    userId: v.id("users"),
  },
  returns: v.id("research"),
  handler: async (ctx, args) => {
    // 创建研究记录
    const researchId = await ctx.runMutation(internal.workflows.createResearch, {
      topic: args.topic,
      userId: args.userId,
      status: "searching",
    });

    // 步骤1：搜索相关文档
    const searchResults = await agent.search(ctx, {
      query: args.topic,
      table: "documents",
      limit: 10,
    });

    await ctx.runMutation(internal.workflows.updateStatus, {
      researchId,
      status: "analyzing",
    });

    // 步骤2：分析和综合
    const analysis = await agent.chat(ctx, {
      messages: [{
        role: "user",
        content: `分析关于"${args.topic}"的这些来源并提供一个全面的总结：
        ${
          searchResults.map((r) => r.content).join("\n\n---\n\n")
        }`,
      }],
      systemPrompt: "你是一个研究助理。提供彻底、有引用的分析。",
    });

    // 步骤3：生成关键见解
    await ctx.runMutation(internal.workflows.updateStatus, {
      researchId,
      status: "summarizing",
    });

    const insights = await agent.chat(ctx, {
      messages: [{
        role: "user",
        content: `根据这个分析，列出5个关键见解：
        \n\n${analysis.content}`,
      }],
    });

    // 保存最终结果
    await ctx.runMutation(internal.workflows.completeResearch, {
      researchId,
      analysis: analysis.content,
      insights: insights.content,
      sources: searchResults.map((r) => r._id),
    });

    return researchId;
  },
});
```

## 示例

### 完整的聊天应用程序模式

```typescript
// convex/schema.ts
import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  threads: defineTable({
    userId: v.id("users"),
    title: v.string(),
    lastMessageAt: v.optional(v.number()),
    metadata: v.optional(v.any()),
  }).index("by_user", ["userId"]),

  messages: defineTable({
    threadId: v.id("threads"),
    role: v.union(v.literal("user"), v.literal("assistant"), v.literal("system")),
    content: v.string(),
    toolCalls: v.optional(v.array(v.object({
      name: v.string(),
      arguments: v.any(),
      result: v.optional(v.any()),
    }))),
    createdAt: v.number(),
  }).index("by_thread", ["threadId"]),

  documents: defineTable({
    title: v.string(),
    content: v.string(),
    embedding: v.array(v.float64()),
    metadata: v.object({
      source: v.optional(v.string()),
      category: v.optional(v.string()),
    }),
    createdAt: v.number(),
  }).vectorIndex("by_embedding", {
    vectorField: "embedding",
    dimensions: 1536,
  }),
});
```

### React 聊天组件

```typescript
import { useQuery, useMutation, useAction } from "convex/react";
import { api } from "../convex/_generated/api";
import { useState, useRef, useEffect } from "react";

function ChatInterface({ threadId }: { threadId: Id<"threads"> }) {
  const messages = useQuery(api.threads.getMessages, { threadId });
  const sendMessage = useAction(api.chat.sendMessage);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || sending) return;

    const message = input.trim();
    setInput("");
    setSending(true);

    try {
      await sendMessage({ threadId, message });
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="messages">
        {messages?.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            <strong>{msg.role === "user" ? "你" : "助手"}:</strong>
            <p>{msg.content}</p>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSend} className="input-form">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="输入你的消息..."
          disabled={sending}
        />
        <button type="submit" disabled={sending || !input.trim()}>
          {sending ? "发送中..." : "发送"}
        </button>
      </form>
    </div>
  );
}
```

## 最佳实践

- 除非明确指示，否则不要运行 `npx convex deploy`
- 除非明确指示，否则不要运行任何git命令
- 将对话历史存储在Convex中以实现持久化
- 使用流式传输以改善长响应的用户体验
- 为工具失败实现适当的错误处理
- 使用向量索引进行高效的RAG检索
- 限制代理交互以控制成本
- 记录工具使用情况以用于调试和分析

## 常见陷阱

1. **不持久化线程** - 刷新时丢失对话
2. **在长响应上阻塞** - 使用流式传输代替
3. **工具错误导致代理崩溃** - 添加适当的错误处理
4. **大的上下文窗口** - 总结旧消息
5. **缺少RAG的嵌入** - 在插入时生成嵌入

## 参考

- 凸函数文档：https://docs.convex.dev/
- 凸函数 LLMs.txt：https://docs.convex.dev/llms.txt
- 凸函数AI：https://docs.convex.dev/ai
- 代理组件：https://www.npmjs.com/package/@convex-dev/agent
