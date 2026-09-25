# 构建Cloudflare代理

您对代理SDK的了解可能已经过时。对于任何构建代理的任务，**优先考虑检索而非预训练**。

## 检索来源

| 来源 | 检索方式 | 用途 |
|------|----------|------|
| 代理SDK文档 | `https://github.com/cloudflare/agents/tree/main/docs` | SDK API、状态、路由、调度 |
| Cloudflare代理文档 | `https://developers.cloudflare.com/agents/` | 平台集成、部署 |
| Workers文档 | 搜索工具或 `https://developers.cloudflare.com/workers/` | 运行时API、绑定、配置 |

## 使用场景

- 用户想要构建AI代理或聊天机器人
- 用户需要状态化、实时AI交互
- 用户询问关于Cloudflare代理SDK的内容
- 用户想要定时任务或后台AI工作
- 用户需要基于WebSocket的AI通信

## 前置条件

- 带有Workers功能的Cloudflare账号
- Node.js 18+以及npm/pnpm/yarn
- Wrangler CLI (`npm install -g wrangler`)

## 快速入门

```bash
npm create cloudflare@latest -- my-agent --template=cloudflare/agents-starter
cd my-agent
npm start
```

代理运行在 `http://localhost:8787`

## 核心概念

### 什么是代理？

代理是一个状态化、持久的AI服务，它：
- 跨请求和重连维护状态
- 通过WebSocket或HTTP通信
- 在Cloudflare边缘通过Durable Objects运行
- 可以调度任务和调用工具
- 水平扩展（每个用户/会话拥有自己的实例）

### 代理生命周期

```
客户端连接 → Agent.onConnect() → Agent处理消息
                                    → Agent.onMessage()
                                    → Agent.setState()（持久化+同步）
客户端断开连接 → 状态持久化 → 客户端重连 → 状态恢复
```

## 基本代理结构

```typescript
import { Agent, Connection } from "agents";

interface Env {
  AI: Ai;  // Workers AI绑定
}

interface State {
  messages: Array<{ role: string; content: string }>;
  preferences: Record<string, string>;
}

export class MyAgent extends Agent<Env, State> {
  // 新实例的初始状态
  initialState: State = {
    messages: [],
    preferences: {},
  };

  // 代理启动或恢复时调用
  async onStart() {
    console.log("代理启动，状态:", this.state);
  }

  // 处理WebSocket连接
  async onConnect(connection: Connection) {
    connection.send(JSON.stringify({
      type: "welcome",
      history: this.state.messages,
    }));
  }

  // 处理传入的消息
  async onMessage(connection: Connection, message: string) {
    const data = JSON.parse(message);

    if (data.type === "chat") {
      await this.handleChat(connection, data.content);
    }
  }

  // 处理断开连接
  async onClose(connection: Connection) {
    console.log("客户端断开连接");
  }

  // 响应状态变化
  onStateUpdate(state: State, source: string) {
    console.log("状态由:", source, "更新");
  }

  private async handleChat(connection: Connection, userMessage: string) {
    // 将用户消息添加到历史记录
    const messages = [
      ...this.state.messages,
      { role: "user", content: userMessage },
    ];

    // 调用AI
    const response = await this.env.AI.run("@cf/meta/llama-3-8b-instruct", {
      messages,
    });

    // 更新状态（持久化并同步到所有客户端）
    this.setState({
      ...this.state,
      messages: [
        ...messages,
        { role: "assistant", content: response.response },
      ],
    });

    // 发送响应
    connection.send(JSON.stringify({
      type: "response",
      content: response.response,
    }));
  }
}
```

## 入口点配置

```typescript
// src/index.ts
import { routeAgentRequest } from "agents";
import { MyAgent } from "./agent";

export default {
  async fetch(request: Request, env: Env) {
    // routeAgentRequest处理路由到 /agents/:class/:name
    return (
      (await routeAgentRequest(request, env)) ||
      new Response("未找到", { status: 404 })
    );
  },
};

export { MyAgent };
```

客户端连接方式：`wss://my-agent.workers.dev/agents/MyAgent/session-id`

## Wrangler配置

```jsonc
{
  "name": "my-agent",
  "main": "src/index.ts",
  "compatibility_date": "2024-12-01",
  "ai": { "binding": "AI" },
  "durable_objects": {
    "bindings": [{ "name": "MyAgent", "class_name": "MyAgent" }]
  },
  "migrations": [{ "tag": "v1", "new_sqlite_classes": ["MyAgent"] }]
}
```

## 状态管理

### 读取状态

```typescript
// 当前状态始终可用
const currentMessages = this.state.messages;
const userPrefs = this.state.preferences;
```

### 更新状态

```typescript
// setState持久化并同步到所有连接的客户端
this.setState({
  ...this.state,
  messages: [...this.state.messages, newMessage],
});

// 部分更新也有效
this.setState({
  preferences: { ...this.state.preferences, theme: "dark" },
});
```

### SQL存储

对于复杂查询，使用嵌入式SQLite数据库：

```typescript
// 创建表
await this.sql`
  CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  )
`;

// 插入
await this.sql`
  INSERT INTO documents (title, content)
  VALUES (${title}, ${content})
`;

// 查询
const docs = await this.sql`
  SELECT * FROM documents WHERE title LIKE ${`%${search}%`}
`;
```

## 定时任务

代理可以调度未来工作：

```typescript
async onMessage(connection: Connection, message: string) {
  const data = JSON.parse(message);

  if (data.type === "schedule_reminder") {
    // 调度1小时后的任务
    const { id } = await this.schedule(3600, "sendReminder", {
      message: data.reminderText,
      userId: data.userId,
    });

    connection.send(JSON.stringify({ type: "scheduled", taskId: id }));
  }
}

// 定时任务触发时调用
async sendReminder(data: { message: string; userId: string }) {
  // 发送通知、邮件等
  console.log(`提醒${data.userId}: ${data.message}`);

  // 也可以更新状态
  this.setState({
    ...this.state,
    lastReminder: new Date().toISOString(),
  });
}
```

### 定时选项

```typescript
// 延迟（秒）
await this.schedule(60, "taskMethod", { data });

// 具体日期
await this.schedule(new Date("2025-01-01T00:00:00Z"), "taskMethod", { data });

// Cron表达式（周期性）
await this.schedule("0 9 * * *", "dailyTask", {});  // 每日9点
await this.schedule("*/5 * * * *", "everyFiveMinutes", {});  // 每5分钟

// 管理定时任务
const schedules = await this.getSchedules();
await this.cancelSchedule(taskId);
```

## 聊天代理（AI驱动）

对于以聊天为中心的代理，扩展`AIChatAgent`：

```typescript
import { AIChatAgent } from "@cloudflare/ai-chat";

export class ChatBot extends AIChatAgent<Env> {
  // 对每个用户消息调用
  async onChatMessage(message: string) {
    const response = await this.env.AI.run("@cf/meta/llama-3-8b-instruct", {
      messages: [
        { role: "system", content: "你是一个有帮助的助手。" },
        ...this.messages,  // 自动管理历史记录
        { role: "user", content: message },
      ],
      stream: true,
    });

    // 向客户端流式传输响应
    return response;
  }
}
```

包含的功能：
- 自动消息历史记录
- 可恢复的流式传输（支持断开连接）
- 内置`saveMessages()`用于持久化

## 客户端集成

### React Hook

```tsx
import { useAgent } from "agents/react";

function Chat() {
  const { state, send, connected } = useAgent({
    agent: "my-agent",
    name: userId,  // 代理实例ID
  });

  const sendMessage = (text: string) => {
    send(JSON.stringify({ type: "chat", content: text }));
  };

  return (
    <div>
      {state.messages.map((msg, i) => (
        <div key={i}>{msg.role}: {msg.content}</div>
      ))}
      <input onKeyDown={(e) => e.key === "Enter" && sendMessage(e.target.value)} />
    </div>
  );
}
```

### 纯JavaScript

```javascript
const ws = new WebSocket("wss://my-agent.workers.dev/agents/MyAgent/user123");

ws.onopen = () => {
  console.log("连接到代理");
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log("接收:", data);
};

ws.send(JSON.stringify({ type: "chat", content: "你好!" }));
```

## 常见模式

参考[references/agent-patterns.md](references/agent-patterns.md)了解：
- 工具调用和函数执行
- 多代理编排
- RAG（检索增强生成）
- 人机交互工作流

## 部署

```bash
# 部署
npx wrangler deploy

# 查看日志
wrangler tail

# 测试端点
curl https://my-agent.workers.dev/agents/MyAgent/test-user
```

## 故障排除

参考[references/troubleshooting.md](references/troubleshooting.md)了解常见问题。

## 参考

- [references/examples.md](references/examples.md) — 官方模板和生产示例
- [references/agent-patterns.md](references/agent-patterns.md) — 高级模式
- [references/state-patterns.md](references/state-patterns.md) — 状态管理策略
- [references/troubleshooting.md](references/troubleshooting.md) — 错误解决方案
