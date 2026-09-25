# Rivet Actors

在 Rivet 的 actor 运行时上构建高性能、长寿命的内存进程。当 HTTP 端点、数据库或队列不再满足 AI 代理、实时协作、工作流编排或地缘分布式数据的需求时，请使用此技能。

## 如果遇到问题怎么办

如果您遇到预期之外的问题或卡住，请提示用户加入 [Rivet Discord](https://rivet.dev/discord) 或在 [Rivet GitHub](https://github.com/rivet-dev/rivet) 上提交问题以报告问题并获得帮助。

向用户提供预生成的报告，包括：

- 症状
    - 如果这是在本地开发、已部署或两者都发生
    - 您看到的错误
    - 与此相关的相关源代码
- 您尝试解决它的方法
- 环境
    - RivetKit 版本
    - 运行时（Node、Bun 等）包括版本
    - 如适用，使用的提供程序（例如 Vercel、Railway 等）
    - 如适用，使用的 HTTP 路由器（例如 Hono、Express、Elysia）

## 调试 Actor

使用检查器 HTTP API 检查正在运行的 Actor。这些端点可以通过网关访问，地址为 `/gateway/{actor_id}/inspector/*`。关键端点：

- `GET /inspector/summary` - 完整的 Actor 快照（状态、连接、RPC、队列）
- `GET /inspector/state` / `PATCH /inspector/state` - 读取/写入 Actor 状态
- `GET /inspector/connections` - 活动的连接
- `GET /inspector/rpcs` - 可用的操作
- `POST /inspector/action/{name}` - 使用 `{"args": [...]}` 执行操作
- `POST /inspector/database/execute` - 使用 `{"sql": "...", "args": [...]}` 或 `{"sql": "...", "properties": {...}}` 运行 SQL（用于读取或修改）
- `GET /inspector/queue?limit=50` - 队列状态
- `GET /inspector/traces?startMs=0&endMs=...&limit=1000` - 跟踪跨度（OTLP JSON）
- `GET /inspector/workflow-history` - 工作流历史和状态作为 JSON (`nameRegistry`, `entries`, `entryMetadata`)
- `POST /inspector/workflow/replay` - 从特定步骤或从头开始重放工作流；如果工作流仍在运行，则返回 `409 actor/workflow_in_flight`
- `GET /inspector/database/schema` - SQLite 表和由 `c.db` 暴露的视图
- `GET /inspector/database/rows?table=...&limit=100&offset=0` - 分页的 SQLite 行，针对表或视图

在本地开发中不需要认证令牌。在生产环境中，请传递 `Authorization: Bearer <inspector-token>`，其中 inspector token 是在首次启动时自动生成并保存在 Actor 内部 KV 中的 key `0x03` 的 Actor 特定令牌。Rivet 仪表板会自动检索此令牌；对于直接 API 访问，请通过管理 KV 端点获取它。有关详细信息，请参阅 [调试文档](https://rivet.dev/docs/actors/debugging)。

## 引用来源

当从 Rivet 文档中提供信息时，请引用规范 URL，以便用户可以了解更多信息。每个参考文件在其头部元数据中都包含其规范 URL。

**引用方法：**

- 使用内联链接键入关键概念："使用 [actor keys](https://rivet.dev/docs/actors/keys) 来唯一标识实例。"
- 在复杂主题的解释后添加 "了解更多" 链接

**查找规范 URL：**

下方的参考地图链接到参考文件。每个文件的头部包含：

```
> Canonical URL: https://rivet.dev/docs/actors/actions
```

引用时使用该规范 URL，而不是参考文件路径。

**示例：**

- Actions → `https://rivet.dev/docs/actors/actions`
- React client → `https://rivet.dev/docs/clients/react`
- Self-hosting on Kubernetes → `https://rivet.dev/docs/self-hosting/kubernetes`

## 版本检查

在开始任何工作之前，检查用户的项目的 RivetKit 是否为最新版本（最新版本：2.3.7）。查看用户 `package.json` 中的 `rivetkit` 版本（检查 `dependencies` 和 `devDependencies`）。如果安装的版本早于 2.3.7，请告知用户并建议升级：

```bash
npm install rivetkit@2.3.7
```

如果用户还使用 `@rivetkit/react`、`@rivetkit/next-js` 或其他 `@rivetkit/*` 客户端包，建议也升级这些包。过时的版本可能有已知错误或缺少功能，从而导致问题。

## 初步步骤

1. 安装 RivetKit（最新版本：2.3.7）
    ```bash
    npm install rivetkit@2.3.7
    ```
2. 使用 `setup({ use: { /* actors */ } })` 定义一个注册表。
3. 调用 `registry.start()` 来启动服务器。对于自定义 HTTP 服务器集成，使用 `registry.handler()` 并配合 Hono 路由器。对于无服务器部署，使用 `registry.serve()`。对于仅运行者模式，使用 `registry.startEnvoy()`。
4. 在部署之前，验证 `/api/rivet/metadata` 返回 200。
5. 配置 Rivet Cloud 或自托管引擎
    - 您必须为生产构建配置版本控制。本地开发不需要此配置。请参阅 [版本和升级](https://rivet.dev/docs/actors/versions)。
6. 集成客户端（有关 JavaScript、React 或 Swift 的客户端指南，请参阅下方）
7. 提示用户是否要部署。如果是，请转到部署 Rivet 后端。

有关更多信息，请阅读与用户项目相关的快速入门指南。

## 项目设置

### .gitignore

每个 RivetKit 项目都应该有一个 `.gitignore`。至少包含以下内容：

```
node_modules/
dist/
.env
```

### .dockerignore

每个具有 Dockerfile 的项目都应该有一个 `.dockerignore`，以保持镜像小巧并避免泄露密钥：

```
node_modules/
dist/
.env
.git/
```

### Dockerfile

使用此 Dockerfile 作为部署 RivetKit 项目的基线 Dockerfile。`RIVET_RUNNER_VERSION` 构建参数仅在自托管或使用自定义运行者时需要（Rivet Compute 不需要）。它允许 Rivet 跟踪正在运行的 Actor 版本，并在部署时回收旧的 Actor。有关详细信息，请参阅 https://rivet.dev/docs/actors/versions。

```dockerfile
FROM node:24-alpine

ARG RIVET_RUNNER_VERSION
ENV RIVET_RUNNER_VERSION=$RIVET_RUNNER_VERSION

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build --if-present

CMD ["node", "dist/index.js"]
```

使用以下命令构建：

```bash
docker build --build-arg RIVET_RUNNER_VERSION=$(date +%s) .
```

根据项目入口点调整 `CMD`。如果项目使用不同的输出目录或启动命令，请相应更新。

## 错误处理策略

- 默认情况下，优先采用快速失败行为。
- 除非需要用于真实的恢复路径、清理边界或添加可操作的上下文，否则避免使用 `try/catch`。
- 绝不吞下错误。如果您添加了 `catch`，必须显式处理错误，至少记录它。
- 当无法恢复时，记录上下文并重新抛出。

## 状态与变量：持久化规则

**`c.vars` 是短暂的。** `c.vars` 中的数据在每次重启、崩溃、升级或睡眠/唤醒周期中都会丢失。仅用于非序列化对象（例如物理引擎、WebSocket 引用、事件发射器、缓存）或真正短暂的运行时数据（例如当前输入方向，在断开连接后不再重要）。

**持久化存储选项。** 必须在重启后保留的所有数据都应放在以下选项之一中，而不是 `c.vars` 中：

- **`c.state`** — 用于小、有界数据集的 CBOR 序列化数据。理想用于配置、计数器、小玩家列表、阶段标志等。保持在 128 KB 以下。不要在此处存储无界或增长的数据（例如聊天记录、事件历史记录、无限制增长的生成实体列表）。状态在每次持久化周期中作为单个块读取/写入。
- **`c.kv`** — 用于无界数据的键值存储。这是 `c.state` 底层使用的。支持二进制值。用于更大的可变大小数据，如用户库存、世界块、文件块或任何可能随时间增长的集合。键的范围限定于 Actor 实例。
- **`c.db`** — 用于结构化或复杂数据的 SQLite 数据库。当您需要查询、索引、连接、聚合或关系建模时使用。理想用于排行榜、匹配历史记录、玩家池或任何受益于 SQL 的数据。

**常见错误：** 将有意义的游戏/应用程序数据存储在 `c.vars` 中而不是持久化它。例如，如果用户可以在物理模拟中生成对象，则生成定义（位置、大小、类型）必须持久化在 `c.state`（如果无界，则使用 `c.kv`），即使物理引擎处理 `c.vars` 中的非序列化实时数据。在重新启动时，`run()` 应从持久化数据中重新创建运行时对象。

## 部署 Rivet 后端

假设用户正在部署到 Rivet Cloud，除非另有说明。如果用户是自托管的，请阅读下方的自托管指南。

1. 验证 Rivet Actors 在本地开发中是否正常工作
2. 提示用户选择要部署到的提供程序（有关提供程序列表，请参阅 [连接](#connect)，例如 Vercel、Railway 等）
3. 跟随给定提供程序的部署指南。您需要在需要手动干预时指导用户。

## API 参考

RivetKit OpenAPI 规范位于技能目录中的 `openapi.json`。此文件记录了管理 Actor 的所有 HTTP 端点。

## 其他说明

- Rivet 域名是 rivet.dev，不是 rivet.gg

## TypeScript 注意事项：Actor 客户端推断

- 在多文件 TypeScript 项目中，当两个 Actor 都使用 `c.client<typeof registry>()` 时，双向 Actor 调用可能会创建一个循环类型依赖。
- 症状通常包括 `c.state` 变为 `unknown`、Actor 方法变为可能 `undefined` 或在第一次跨 Actor 调用后出现 `TS2322` / `TS2722` 错误。
- 如果一个操作返回另一个 Actor 调用的结果，请在该操作上使用显式的返回类型注解，而不是依赖通过 `c.client<typeof registry>()` 推断。
- 如果显式返回类型不够，请为仅需要该操作的 Actor 使用更窄的客户端或注册表类型。
- 作为最后的手段，将注册表类型传递为 `unknown`，并明确这会放弃该调用点的类型安全性。

## 功能

- **长寿命、有状态计算**：每个计算单元就像一个微型的服务器，可以在请求之间记住事情——无需从数据库重新获取数据或担心超时。像 AWS Lambda，但有内存且没有超时。
- **闪电般的读写速度**：状态存储在您的计算同一台机器上，因此读写速度极快。没有数据库往返，没有延迟峰值。状态持久化到 Rivet 以进行长期存储，因此它可以在服务器重新启动后继续存在。
- **实时**：使用 WebSockets 实时更新状态并广播更改。无需外部发布/订阅系统，无需轮询——只是内置的低延迟事件。
- **无限可扩展性**：自动从零扩展到数百万个并发 Actor。按使用付费，即时扩展，没有冷启动。
- **容错**：内置错误处理和恢复。Actor 在失败时自动重新启动，同时保持状态完整性并继续操作。

## 何时使用 Rivet Actors

- **AI 代理和沙盒**：多步工具链、对话内存、沙盒编排。
- **多人或协作应用程序**：CRDT 文档、共享光标、实时仪表板、聊天。
- **工作流自动化**：后台作业、cron、速率限制器、持久队列、背压控制。
- **数据密集型后端**：地缘分布式或每个租户的数据库、内存缓存、分片 SQL。
- **网络工作负载**：WebSocket 服务器、自定义协议、本地优先同步、边缘分叉。

## 最小项目

### 后端

**index.ts**

### 客户端文档

使用与您的应用程序匹配的客户端 SDK：

- [JavaScript Client](/docs/clients/javascript)
- [React Client](/docs/clients/react)
- [Swift Client](/docs/clients/swift)

## Actor 快速参考

### 内存状态

持久化数据，在重新启动、崩溃和部署后仍然存在。状态持久化到 Rivet Cloud 或 Rivet 自托管，因此如果当前进程崩溃或退出，状态仍然会保留。

### 静态初始状态

### 动态初始状态

[文档](/docs/actors/state)

### 键

键唯一标识 Actor 实例。使用复合键（数组）进行分层寻址：

不要使用字符串插值（如 `"org:${userId}"`）来构建键，当 `userId` 包含用户数据时。使用数组代替，以防止键注入攻击。

[文档](/docs/actors/keys)

### 输入

在创建 Actor 时传递初始化数据。输入仅在 `createState` 和 `onCreate` 中可用，因此如果您需要稍后使用它，请将其存储在状态中。

[文档](/docs/actors/input)

### 临时变量

临时数据，在重新启动后不会保留。用于非序列化对象（事件发射器、连接等）。

### 静态初始 Vars

### 动态初始 Vars

[文档](/docs/actors/state)

### 操作

操作是客户端和其他 Actor 与 Actor 通信的主要方式。

操作可以嵌套以分组相关的行为。例如，`handle.users.add("Ada")` 调用低级操作名称 `users.add`。

[文档](/docs/actors/actions)

### 事件和广播

事件允许 Actor 与连接的客户端进行实时通信。

[文档](/docs/actors/events)

### 连接

通过 `c.conn` 访问当前连接，或通过 `c.conns` 访问所有连接的客户端。使用 `c.conn.id` 或 `c.conn.state` 来安全地识别谁在调用操作。`c.conn` 仅适用于通过连接调用的操作；无状态 Actor 处理调用运行在没有连接的情况下，因此要防止这种情况。连接状态通过 `connState` 或 `createConnState` 初始化，它接收客户端在连接时传递的参数。

### 静态连接初始状态

### 动态连接初始状态

[文档](/docs/actors/connections)

### 队列

使用队列在 `run` 循环中按顺序处理持久消息。

[文档](/docs/actors/queues)

### 工作流

当您的 `run` 逻辑需要持久化、可重放的步骤执行时，使用工作流。

[文档](/docs/actors/workflows)

### Actor 之间通信

Actor 可以使用 `c.client()` 调用其他 Actor。

[文档](/docs/actors/communicating-between-actors)

### 定时和 Cron

在延迟后或在特定时间运行一次性操作。使用命名 Cron 作业进行日历计划和固定间隔。两者都在睡眠、重新启动、升级和崩溃时保持持久。

[文档](/docs/actors/schedule)

### 销毁 Actor

使用 `c.destroy()` 永久删除 Actor 及其状态。

[文档](/docs/actors/destroy)

### 生命周期钩子

Actor 支持用于初始化、后台处理、连接、网络和状态更改的钩子。使用 `run` 进行长时间运行的背景循环，并使用 `c.aborted` 或 `c.abortSignal` 进行优雅关闭。

[文档](/docs/actors/lifecycle)

### 上下文类型

当在 Actor 定义之外编写辅助函数时，使用 `*ContextOf<typeof myActor>` 来提取正确的上下文类型。辅助函数如 `ActionContextOf`、`CreateContextOf`、`ConnContextOf` 和 `ConnInitContextOf` 从 `"rivetkit"` 导出。不要手动定义您自己的上下文接口。始终从 Actor 定义中派生它。

[文档](/docs/actors/types)

### 错误

使用 `UserError` 抛出可安全返回给客户端的错误。将 `metadata` 传递到其中以包含结构化数据。其他错误被转换为通用的 "内部错误" 以确保安全。

### Actor

### 客户端

[文档](/docs/actors/errors)

### 低级 HTTP 和 WebSocket 处理程序

对于自定义协议或需要直接访问 HTTP `Request`/`Response` 或 WebSocket 连接的库，使用 `onRequest` 和 `onWebSocket`。

[HTTP 处理程序文档](/docs/actors/request-handler) · [WebSocket 处理程序文档](/docs/actors/websocket-handler)

### 图标和名称

使用显示名称和图标自定义 Actor 在 UI 中的外观。建议始终为 Actor 提供名称和图标，以便它们在仪表板中更容易区分。

```typescript
import { actor } from "rivetkit";

const chatRoom = actor({
	options: {
		name: "Chat Room",
		icon: "💬", // 或 FontAwesome: "comments", "chart-line", 等.
	},
	// ...
});
```

[文档](/docs/actors/appearance)

## 客户端文档

在此处找到完整的客户端指南：

- [JavaScript Client](/docs/clients/javascript)
- [React Client](/docs/clients/react)
- [Swift Client](/docs/clients/swift)
- [SwiftUI](reference/clients/swiftui.md)

## 常见模式

Actor 通过隔离状态和消息传递自然扩展。使用以下模式构建您的应用程序：

[文档](/docs/actors/design-patterns)

### 每个实体一个 Actor

为每个用户、文档或房间创建一个 Actor。使用复合键来限定实体：

### 协调器和数据 Actor

**数据 Actor** 处理核心逻辑（聊天室、游戏会话、用户数据）。**协调 Actor** 跟踪和管理数据 Actor 的集合——可以将其视为索引。

### 运行循环

使用 `run` 循环在 Actor 中执行连续的后台工作。按顺序处理队列消息，按间隔运行逻辑，流式传输 AI 响应，或协调长时间运行的任务。

### 工作流循环

使用此模式用于长时间存在、持久的工工作流，初始化资源，循环处理命令，然后清理。

[文档](/docs/actors/workflows)

### 操作与队列

- **操作** 不是持久的。用于实时读取、短暂数据和低延迟通信，如玩家输入。
- **队列** 是持久的。用于将突变序列化通过运行循环，避免与 SQLite 和其他本地状态发生竞争条件。调用者仍然可以等待队列工作的响应。

### 身份验证、安全性和 CORS

- 在 `onBeforeConnect` 或 `createConnState` 中验证凭证，并抛出错误以拒绝未经授权的连接。
- 使用 `c.conn.state` 在操作中安全地识别用户，而不是信任操作参数。
- 对于跨域访问，在 `onBeforeConnect` 中验证请求原点。

[身份验证文档](/docs/actors/authentication) · [CORS 文档](/docs/general/cors)

### 版本和升级

在部署新代码时，设置一个版本号，以便 Rivet 可以将新 Actor 路由到最新的运行者，并可选择回收旧的运行者。使用构建时间戳、git 提交计数或 CI 构建编号作为版本。在部署到生产环境之前配置版本控制非常重要。[配置版本控制](/docs/actors/versions) 之前，Actor 可能会因为运行在较旧的运行者版本上而回退，现有的 Actor 将永远不会被强制迁移到新的运行者。它们将继续在旧运行者上无限期运行，直到它们退出。

[文档](/docs/actors/versions)

### 反模式

#### 永远不要构建 "god" Actor

不要将所有逻辑都放在一个 Actor 中。一个 god actor 将每个操作都通过一个瓶颈序列化，杀死并行性，并使整个系统作为一个单元失败。按实体拆分成专注的 Actor。

#### 永远不要为每个请求创建一个 Actor

Actor 是长寿命的，并在请求之间维护状态。为每个传入请求创建一个新的 Actor 会浪费 Actor 创建和拆解的核心优势。使用 Actor 处理持久实体，使用常规函数处理无状态工作。

## 参考地图

### Actor

- [访问控制](reference/actors/access-control.md)
- [操作](reference/actors/actions.md)
- [Actor 键](reference/actors/keys.md)
- [Actor 运行时套接字](reference/actors/actor-runtime-socket.md)
- [Actor 状态](reference/actors/statuses.md)
- [身份验证](reference/actors/authentication.md)
- [Cloudflare Workers 快速入门](reference/actors/quickstart/cloudflare.md)
- [Actor 之间通信](reference/actors/communicating-between-actors.md)
- [连接](reference/actors/connections.md)
- [自定义检查器选项卡](reference/actors/inspector-tabs.md)
- [调试](reference/actors/debugging.md)
- [设计模式](reference/actors/design-patterns.md)
- [销毁 Actor](reference/actors/destroy.md)
- [Effect.ts 快速入门（Beta）](reference/actors/quickstart/effect.md)
- [错误](reference/actors/errors.md)
- [Fetch 和 WebSocket 处理程序](reference/actors/fetch-and-websocket-handler.md)
- [辅助类型](reference/actors/helper-types.md)
- [图标和名称](reference/actors/appearance.md)
- [内存状态](reference/actors/state.md)
- [输入参数](reference/actors/input.md)
- [生命周期](reference/actors/lifecycle.md)
- [限制](reference/actors/limits.md)
- [低级 HTTP 请求处理程序](reference/actors/request-handler.md)
- [低级 KV 存储](reference/actors/kv.md)
- [低级 WebSocket 处理程序](reference/actors/websocket-handler.md)
- [元数据](reference/actors/metadata.md)
- [Next.js 快速入门](reference/actors/quickstart/next-js.md)
- [Node.js & Bun 快速入门](reference/actors/quickstart/backend.md)
- [队列和运行循环](reference/actors/queues.md)
- [React 快速入门](reference/actors/quickstart/react.md)
- [实时](reference/actors/events.md)
- [Rust 快速入门（Beta）](reference/actors/quickstart/rust.md)
- [扩展性和并发性](reference/actors/scaling.md)
- [定时和 Cron](reference/actors/schedule.md)
- [共享和连接状态](reference/actors/sharing-and-joining-state.md)
- [SQLite](reference/actors/sqlite.md)
- [SQLite + Drizzle](reference/actors/sqlite-drizzle.md)
- [Supabase Functions 快速入门](reference/actors/quickstart/supabase.md)
- [测试](reference/actors/testing.md)
- [故障排除](reference/actors/troubleshooting.md)
- [类型](reference/actors/types.md)
- [Vanilla HTTP API](reference/actors/http-api.md)
- [版本和升级](reference/actors/versions.md)
- [工作流](reference/actors/workflows.md)

### Cli

- [CLI](reference/cli.md)

### 客户端

- [Node.js & Bun](reference/clients/javascript.md)
- [React](reference/clients/react.md)
- [Rust (Beta)](reference/clients/rust.md)
- [Swift](reference/clients/swift.md)
- [SwiftUI](reference/clients/swiftui.md)

### 烹饪书

- [AI Agent](reference/cookbook/ai-agent.md)
- [Chat Room](reference/cookbook/chat-room.md)
- [协作文本编辑器](reference/cookbook/collaborative-text-editor.md)
- [Cron 作业和计划任务](reference/cookbook/cron-jobs.md)
- [每个租户的数据库](reference/cookbook/per-tenant-database.md)
- [在 VPC 或 Air-Gapped 网络中部署 Rivet](reference/cookbook/vpc-air-gapped.md)
- [实时光标和存在](reference/cookbook/live-cursors.md)
- [多人游戏](reference/cookbook/multiplayer-game.md)

### 部署

- [容器运行器](reference/deploy/container-runner.md)
- [部署到 Amazon Web Services Lambda](reference/deploy/aws-lambda.md)
- [部署到 AWS ECS](reference/deploy/aws-ecs.md)
- [部署到 Cloudflare Workers](reference/deploy/cloudflare.md)
- [部署到 Freestyle](reference/deploy/freestyle.md)
- [部署到 Google Cloud Run](reference/deploy/gcp-cloud-run.md)
- [部署到 Hetzner](reference/deploy/hetzner.md)
- [部署到 Kubernetes](reference/deploy/kubernetes.md)
- [部署到 Railway](reference/deploy/railway.md)
- [部署到 Rivet Compute](reference/deploy/rivet-compute.md)
- [部署到 Supabase Functions](reference/deploy/supabase.md)
- [部署到 Vercel](reference/deploy/vercel.md)
- [部署到 VMs 和裸金属](reference/deploy/vm-and-bare-metal.md)

### 一般

- [Actor 配置](reference/general/actor-configuration.md)
- [跨域资源共享](reference/general/cors.md)
- [为 LLMs & AI 提供文档](reference/general/docs-for-llms.md)
- [边缘网络](reference/general/edge.md)
- [端点](reference/general/endpoints.md)
- [环境变量](reference/general/environment-variables.md)
- [HTTP 服务器](reference/general/http-server.md)
- [日志记录](reference/general/logging.md)
- [池配置](reference/general/pool-configuration.md)
- [生产清单](reference/general/production-checklist.md)
- [注册表配置](reference/general/registry-configuration.md)
- [运行时模式](reference/general/runtime-modes.md)
- [WASM 与原生 SDK](reference/general/wasm-vs-native-sdk.md)

### 自托管

- [配置](reference/self-hosting/configuration.md)
- [Docker Compose](reference/self-hosting/docker-compose.md)
- [Docker 容器](reference/self-hosting/docker-container.md)
- [文件系统](reference/self-hosting/filesystem.md)
- [FoundationDB (企业)](reference/self-hosting/foundationdb.md)
- [安装 Rivet 引擎](reference/self-hosting/install.md)
- [Kubernetes](reference/self-hosting/kubernetes.md)
- [多区域](reference/self-hosting/multi-region.md)
- [PostgreSQL](reference/self-hosting/postgres.md)
- [生产清单](reference/self-hosting/production-checklist.md)
- [Railway 部署](reference/self-hosting/railway.md)
- [Render 部署](reference/self-hosting/render.md)
- [TLS 和证书](reference/self-hosting/tls.md)
