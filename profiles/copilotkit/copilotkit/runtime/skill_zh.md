# CopilotKit 运行时

`@copilotkit/runtime` 是 CopilotKit 的服务器端部分：它接受 AG-UI 协议请求，将请求分派给 `AbstractAgent`（内置或外部），通过 `AgentRunner` 运行流，并以 Server-Sent Events 的形式进行响应。

这个 SKILL.md 是 **索引**。请阅读与你的任务匹配的 `references/` 下的参考文档——不要尝试从这个文件中吸收整个包的内容。

## 心智模型——你传递给 `CopilotRuntime` 的三个字典

```ts
new CopilotRuntime({
  agents, // Record<string, AbstractAgent>     — 查看 wiring-external-agents 或 built-in-agent
  runner, // AgentRunner (可选)            — 查看 agent-runners
  intelligence, // CopilotKitIntelligence (可选) — 查看 intelligence-mode (自动连接 runner)
  mcpApps, // McpAppsConfig (可选)          — 查看 wiring-mcp-apps-middleware
  a2ui, // A2UIConfig (可选)             — 查看 packages/a2ui-renderer 技能
  hooks, // { onRequest, onBeforeHandler }    — 查看 middleware
  beforeRequestMiddleware,
  afterRequestMiddleware, // 遗留 — 查看 middleware
  transcription, // TranscriptionService (可选)  — 查看 transcription
});
```

然后你挂载它：

```ts
import { createCopilotRuntimeHandler } from "@copilotkit/runtime/v2";
const handler = createCopilotRuntimeHandler({
  runtime,
  basePath: "/api/copilotkit",
});
export default { fetch: handler };
```

## 何时加载哪个参考

| 任务                                                                                                                                                                           | 参考                                                                                                                                                                                                                                                                                                                                          |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 在任何 fetch-native 服务器上挂载（Cloudflare Workers、Bun、Deno、Vercel Edge、Next.js App Router、React Router v7、TanStack Start）或从 Express/Node 分派 | `references/setup-endpoint.md`                                                                                                                                                                                                                                                                                                                     |
| 通过 `hooks.onRequest` / `hooks.onBeforeHandler`（首选）或遗留 `beforeRequestMiddleware` / `afterRequestMiddleware` 进行认证 / 日志记录 / 速率限制 / 请求范围守卫 | `references/middleware.md`                                                                                                                                                                                                                                                                                                                         |
| 在 `InMemoryAgentRunner`、`SqliteAgentRunner` 或自定义子类之间进行选择——包括线程锁语义和 runner/Intelligence 互斥                                                                 | `references/agent-runners.md` (+ `-in-memory.md`、`-sqlite.md`、`-custom.md` 用于后端特定细节)                                                                                                                                                                                                                                          |
| 通过 CopilotKit Intelligence 启用持久线程 + 实时 WebSocket（一个 **托管服务**，不可自托管）                                                                                   | `references/intelligence-mode.md`                                                                                                                                                                                                                                                                                                                  |
| 语音转录——为 `/transcribe` 端点实现 `TranscriptionService` 子类                                                                                                                    | `references/transcription.md`                                                                                                                                                                                                                                                                                                                      |
| 实例化 `BuiltInAgent` — 简单模式（经典）或使用 TanStack AI 的工厂模式（首选的 AG-UI 符合默认值）、AI SDK 或自定义工厂                                                                   | `references/built-in-agent.md` (+ `-factory-modes.md`、`-helper-utilities.md`、`-model-identifiers.md`)                                                                                                                                                                                                                                            |
| 通过 `defineTool` 定义服务器端工具，用于 `BuiltInAgent.config.tools`（仅限简单模式）                                                                                               | `references/server-side-tools.md`                                                                                                                                                                                                                                                                                                                  |
| 将外部代理框架连接到 `CopilotRuntime({ agents })`                                                                                                                               | `references/wiring-external-agents.md` (索引) + 每个框架的参考 (`wiring-mastra.md`、`wiring-langgraph.md`、`wiring-crewai-crews.md`、`wiring-crewai-flows.md`、`wiring-pydantic-ai.md`、`wiring-adk.md`、`wiring-llamaindex.md`、`wiring-agno.md`、`wiring-aws-strands.md`、`wiring-ms-agent-framework.md`、`wiring-ag2.md`、`wiring-a2a.md`) |
| 连接 MCP Apps（运行时级中间件，不是代理）                                                                                                                                       | `references/wiring-mcp-apps-middleware.md`                                                                                                                                                                                                                                                                                                         |

## 不变量和注意事项（一次性加载，任何参考之前）

- `createCopilotRuntimeHandler` 是规范原语。`createCopilotExpressHandler` / `createCopilotHonoHandler` 存在，但**应完全避免**——改用从 Express/Hono 路由到 fetch 原语的方式。
- Intelligence 凭证在服务器端。CLI 将 `CPK_INTELLIGENCE_API_KEY` 写入运行时的环境；不涉及客户端密钥。
- Intelligence 模式自动连接 `IntelligenceAgentRunner`。向 `CopilotRuntime` 传递 `runner` 和 `intelligence` 会被构建时拒绝。
- Intelligence 模式针对的是托管的 CopilotKit Intelligence 服务 (`api.cloud.copilotkit.ai`)，并且是**不可自托管的**。
- `hooks.onRequest` 在 **之前** 运行 `beforeRequestMiddleware`（基于 hook 的中间件在响应短路时优先）。`beforeRequestMiddleware` 在 `hooks.onRequest` **之后** 运行（查看 `fetch-handler.ts:136-147`）。
- `identifyUser`（Intelligence）**不**转发抛出的 `Response` 对象——转换为 500。在 `hooks.onRequest` 中进行守卫认证拒绝，它确实转发响应。
- `agents__unsafe_dev_only` 和 `selfManagedAgents` 是开发专用的别名；在生产环境中不要使用它们。两者都表示 SPA 处于开发模式。

## 读者首次阅读的顺序

1. `setup-endpoint` — 原语。
2. `built-in-agent` **或** 从 `wiring-external-agents` 中选择一个——代理。
3. `agent-runners` — 生产持久化选择。
4. 可选：`middleware`、`intelligence-mode`、`server-side-tools`、`transcription`。
