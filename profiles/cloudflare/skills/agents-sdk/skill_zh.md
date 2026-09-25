# Cloudflare Agents SDK

你对 Agents SDK 的了解可能已经过时。**优先使用检索而非预训练**来处理任何 Agents SDK 任务。

## 检索源

Cloudflare 文档：https://developers.cloudflare.com/agents/

| 主题 | 文档 URL | 用途 |
|-------|----------|---------|
| 入门 | [快速开始](https://developers.cloudflare.com/agents/getting-started/quick-start/) | 首个 agent、项目配置 |
| 添加到现有项目 | [添加到现有项目](https://developers.cloudflare.com/agents/getting-started/add-to-existing-project/) | 安装到现有 Workers 应用 |
| 配置 | [配置](https://developers.cloudflare.com/agents/api-reference/configuration/) | `wrangler.jsonc`、绑定、资源、部署 |
| Agent 类 | [Agents API](https://developers.cloudflare.com/agents/api-reference/agents-api/) | Agent 生命周期、模式、注意事项 |
| 状态 | [存储和同步状态](https://developers.cloudflare.com/agents/api-reference/store-and-sync-state/) | `setState`、`validateStateChange`、持久化 |
| 路由 | [路由](https://developers.cloudflare.com/agents/api-reference/routing/) | URL 模式、`routeAgentRequest` |
| 可调用方法 | [可调用方法](https://developers.cloudflare.com/agents/api-reference/callable-methods/) | `@callable`、RPC、流式传输、超时 |
| 调度 | [安排任务](https://developers.cloudflare.com/agents/api-reference/schedule-tasks/) | `schedule()`、`scheduleEvery()`、cron |
| 工作流 | [运行工作流](https://developers.cloudflare.com/agents/api-reference/run-workflows/) | `AgentWorkflow`、持久的 multi-step 任务 |
| HTTP/WebSocket | [WebSocket](https://developers.cloudflare.com/agents/api-reference/websockets/) | 生命周期钩子、休眠 |
| 聊天 agent | [聊天 agent](https://developers.cloudflare.com/agents/communication-channels/chat/chat-agents/) | `AIChatAgent`、流式传输、工具、持久化 |
| Client SDK | [Client SDK](https://developers.cloudflare.com/agents/communication-channels/chat/client-sdk/) | `useAgent`、`AgentClient`、状态、RPC、HTTP |
| Client 工具 | [Client 工具](https://developers.cloudflare.com/agents/harnesses/think/client-tools/) | Client 端工具、`autoContinueAfterToolResult` |
| Server 驱动的消息 | [自主响应](https://developers.cloudflare.com/agents/communication-channels/chat/autonomous-responses/) | `saveMessages`、`waitUntilStable`、服务端发起的轮次 |
| 可恢复流式传输 | [聊天 agent](https://developers.cloudflare.com/agents/communication-channels/chat/chat-agents/#resumable-streaming) | 断开连接时的流式传输恢复 |
| 邮件 | [邮件](https://developers.cloudflare.com/agents/api-reference/email/) | 邮件路由、安全的回复解析器 |
| MCP 客户端 | [MCP 客户端](https://developers.cloudflare.com/agents/model-context-protocol/apis/client-api/) | 连接到 MCP 服务器 |
| MCP 服务器 | [MCP 服务器](https://developers.cloudflare.com/agents/model-context-protocol/apis/handler-api/) | 使用 `createMcpHandler` 构建 MCP 服务器 |
| MCP 传输 | [MCP 传输](https://developers.cloudflare.com/agents/model-context-protocol/protocol/transport/) | 可流式传输的 HTTP、SSE、RPC 传输选项 |
| 保护 MCP 服务器 | [保护 MCP](https://developers.cloudflare.com/agents/model-context-protocol/guides/securing-mcp-server/) | OAuth、代理 MCP、加固 |
| 人在回路 | [人在回路](https://developers.cloudflare.com/agents/concepts/agentic-patterns/human-in-the-loop/) | 工作流审批、引导、超时处理 |
| 持久执行 | [持久执行](https://developers.cloudflare.com/agents/api-reference/durable-execution/) | `runFiber()`、`stash()`、在 DO 驱逐时存活 |
| 队列 | [队列](https://developers.cloudflare.com/agents/api-reference/queue-tasks/) | 内置 FIFO 队列、`queue()` |
| 重试 | [重试](https://developers.cloudflare.com/agents/api-reference/retries/) | `this.retry()`、退避/抖动 |
| 可观测性 | [可观测性](https://developers.cloudflare.com/agents/api-reference/observability/) | 诊断通道事件 |
| 推送通知 | [推送通知](https://developers.cloudflare.com/agents/communication-channels/webhooks/push-notifications/) | 来自 agent 的 Web Push + VAPID |
| Webhook | [Webhook](https://developers.cloudflare.com/agents/communication-channels/webhooks/) | 接收外部 Webhook |
| 跨域认证 | [跨域认证](https://developers.cloudflare.com/agents/runtime/operations/cross-domain-authentication/) | WebSocket 认证、令牌、CORS |
| 只读连接 | [只读](https://developers.cloudflare.com/agents/api-reference/readonly-connections/) | `shouldConnectionBeReadonly` |
| 语音 | [语音](https://developers.cloudflare.com/agents/api-reference/voice/) | 实验性的 STT/TTS、`withVoice` |
| 浏览网页 | [浏览器工具](https://developers.cloudflare.com/agents/api-reference/browse-the-web/) | 实验性的基于 CDP 的浏览器自动化 |
| Think | [Think](https://developers.cloudflare.com/agents/api-reference/think/) | 实验性的更高层聊天 agent 类 |
| 迁移 | [AI SDK v5](https://github.com/cloudflare/agents/blob/main/docs/agents/migration-to-ai-sdk-v5.md)、[AI SDK v6](https://github.com/cloudflare/agents/blob/main/docs/agents/migration-to-ai-sdk-v6.md) | 升级 `@cloudflare/ai-chat` |

## 能力

Agents SDK 提供以下能力：

- **持久状态** — 基于 SQLite，通过 `setState` 自动同步到客户端
- **可调用 RPC** — 通过 WebSocket 调用 `@callable()` 方法
- **调度** — 一次性、定期（`scheduleEvery`）和 cron 任务
- **工作流** — 通过 `AgentWorkflow` 进行持久的 multi-step 后台处理
- **持久执行** — `runFiber()` / `stash()` 用于在 DO 驱逐后仍能存活的工作
- **队列** — 内置 FIFO 队列，通过 `queue()` 支持重试
- **重试** — 带有指数退避和抖动的 `this.retry()`
- **MCP 集成** — 连接到 MCP 服务器，或使用 `createMcpHandler` 自行构建
- **邮件处理** — 通过安全的路由接收和回复邮件
- **流式聊天** — 具有可恢复流、消息持久化和工具的 `AIChatAgent`
- **Server 驱动的消息** — 用于主动 agent 轮次的 `saveMessages`、`waitUntilStable`
- **React 钩子** — 用于客户端应用的 `useAgent`、`useAgentChat`
- **可观测性** — 用于状态、RPC、调度、生命周期的 `diagnostics_channel` 事件
- **推送通知** — 来自 agent 的 Web Push + VAPID 投递
- **Webhook** — 接收并验证外部 Webhook
- **语音**（实验性） — 通过 `@cloudflare/voice` 的 STT/TTS
- **浏览器工具**（实验性） — 通过 `agents/browser` 的基于 CDP 的浏览
- **Think**（实验性） — 通过 `@cloudflare/think` 的更高层聊天 agent

## 第一步：验证安装

```bash
npm ls agents  # 应显示 agents 包
```

如果未安装：
```bash
npm install agents
```

对于聊天 agent：
```bash
npm install agents @cloudflare/ai-chat ai @ai-sdk/react
```

## Wrangler 配置

```jsonc
{
  "compatibility_flags": ["nodejs_compat"],
  "durable_objects": {
    "bindings": [{ "name": "MyAgent", "class_name": "MyAgent" }]
  },
  "migrations": [{ "tag": "v1", "new_sqlite_classes": ["MyAgent"] }]
}
```

**注意事项：**
- 不要在 tsconfig 中启用 `experimentalDecorators`（会破坏 `@callable`）
- 永远不要编辑旧版迁移 — 始终添加新的 tag
- 每个 agent 类都需要单独的 DO 绑定 + 迁移条目
- 为 Workers AI 添加 `"ai": { "binding": "AI" }`

## Agent 类

```typescript
import { Agent, routeAgentRequest, callable } from "agents";

type State = { count: number };

export class Counter extends Agent<Env, State> {
  initialState = { count: 0 };

  validateStateChange(nextState: State, source: Connection | "server") {
    if (nextState.count < 0) throw new Error("Count cannot be negative");
  }

  onStateUpdate(state: State, source: Connection | "server") {
    console.log("State updated:", state);
  }

  @callable()
  increment() {
    this.setState({ count: this.state.count + 1 });
    return this.state.count;
  }
}

export default {
  fetch: (req, env) => routeAgentRequest(req, env) ?? new Response("Not found", { status: 404 })
};
```

## 路由

请求路由到 `/agents/{agent-name}/{instance-name}`：

| 类 | URL |
|-------|-----|
| `Counter` | `/agents/counter/user-123` |
| `ChatRoom` | `/agents/chat-room/lobby` |

客户端：`useAgent({ agent: "Counter", name: "user-123" })`

自定义路由：使用 `getAgentByName(env.MyAgent, "instance-id")` 然后调用 `agent.fetch(request)`。

## 核心 API

| 任务 | API |
|------|-----|
| 读取状态 | `this.state.count` |
| 写入状态 | `this.setState({ count: 1 })` |
| SQL 查询 | `` this.sql`SELECT * FROM users WHERE id = ${id}` `` |
| 调度（延迟） | `await this.schedule(60, "task", payload)` |
| 调度（cron） | `await this.schedule("0 * * * *", "task", payload)` |
| 调度（间隔） | `await this.scheduleEvery(30, "poll")` |
| RPC 方法 | `@callable() myMethod() { ... }` |
| 流式 RPC | `@callable({ streaming: true }) stream(res) { ... }` |
| 启动工作流 | `await this.runWorkflow("ProcessingWorkflow", params)` |
| 持久 Fiber | `await this.runFiber("name", async (ctx) => { ... })` |
| 入队工作 | `this.queue("handler", payload)` |
| 带退避重试 | `await this.retry(fn, { maxAttempts: 5 })` |
| 向客户端广播 | `this.broadcast(message)` |
| 获取连接 | `this.getConnections(tag?)` |

## React 客户端

请阅读 [client-sdk.md](references/client-sdk.md) 了解客户端选择及当前连接示例。对于聊天 UI 和工具，请同时阅读 [streaming-chat.md](references/streaming-chat.md)。

## 参考资料

### 核心
- **[references/state-scheduling.md](references/state-scheduling.md)** — 状态持久化、调度、SQL
- **[references/callable.md](references/callable.md)** — RPC 方法、流式传输、超时
- **[references/routing.md](references/routing.md)** — URL 模式、自定义路由、`getAgentByName`
- **[references/configuration.md](references/configuration.md)** — Wrangler 配置、绑定、Vite 设置

### 聊天与流式传输
- **[references/streaming-chat.md](references/streaming-chat.md)** — AIChatAgent、可恢复流、工具
- **[references/client-sdk.md](references/client-sdk.md)** — `useAgent`、`useAgentChat`、`AgentClient`
- **[references/server-driven-messages.md](references/server-driven-messages.md)** — 触发模式、`saveMessages`
- **[references/human-in-the-loop.md](references/human-in-the-loop.md)** — 审批流程、`needsApproval`

### 后台处理
- **[references/workflows.md](references/workflows.md)** — 持久的 Workflows 集成
- **[references/durable-execution.md](references/durable-execution.md)** — `runFiber`、`stash`、在驱逐时存活
- **[references/queue-retries.md](references/queue-retries.md)** — 内置队列、带退避的重试

### 集成
- **[references/mcp.md](references/mcp.md)** — MCP 客户端和服务器、传输、保护
- **[references/email.md](references/email.md)** — 邮件路由和处理
- **[references/webhooks-push.md](references/webhooks-push.md)** — Webhook、推送通知
- **[references/observability.md](references/observability.md)** — 诊断通道事件

### 实验性
- **[references/think.md](references/think.md)** — `@cloudflare/think` 高级聊天 agent
- **[references/voice.md](references/voice.md)** — `@cloudflare/voice` STT/TTS
- **[references/codemode.md](references/codemode.md)** — 工具编排的代码模式
- **[references/browse-the-web.md](references/browse-the-web.md)** — CDP 浏览器工具
