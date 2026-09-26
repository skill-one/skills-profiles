# 定时任务和计划任务

**重要提示：在进行任何操作之前，你必须阅读此技能目录中的 `BASE_SKILL.md`。它包含了关于调试、错误处理、状态管理、部署和项目设置的必要指导。这些规则和模式适用于所有 RivetKit 工作。以下内容都假设你已经阅读并理解了它。**

## 工作示例

如果你需要一个参考实现，请阅读这些模板中的原始工作示例代码：

- [scheduling](https://github.com/rivet-dev/rivet/tree/main/examples/scheduling)


Rivet Actor 的计划是持久的、actor 本地的计时器。它们在 actor 睡眠、重启、升级、部署和崩溃时仍然有效，而无需单独的 cron 服务。

## 选择计划类型

| API | 用于 |
| --- | --- |
| `c.schedule.after(delayMs, action, ...args)` | 相对延迟后的一次性工作。 |
| `c.schedule.at(timestamp, action, ...args)` | 毫秒级精确 Unix 时间戳的一次性工作。 |
| `c.cron.set({ ... })` | IANA 时区的命名日历递归。 |
| `c.cron.every({ ... })` | 至少为 5 秒的命名固定间隔。 |

所有回调都是同一 actor 上的普通操作。在代码中保持操作名称固定，而不是接受来自客户端的任意操作名称。

有关完整 API、历史记录、取消、失败行为和限制，请参阅 [Schedule & Cron](/docs/actors/schedule)。

## 日历任务

使用 `cron.set` 而不是手动重新触发一次性操作：

在 `onCreate` 中安装固定后台任务，以便每个 actor 只执行一次设置。任务名称是插入或更新键，因此稍后的 `cron.set` 调用会更新现有任务而不是创建重复任务。`cron.set` 还处理时区和夏令时转换。

## 固定间隔任务

使用 `cron.every` 执行频繁的工作，例如存在扫描或缓存刷新：

```ts
await c.cron.every({
  name: "presence-sweep",
  interval: 15_000, // 最小 5 秒。
  action: "sweepPresence",
  maxHistory: 25,
});
```

间隔仍然锚定到计划截止日期，而不是根据操作的运行时间漂移。如果先前的运行仍然处于活动状态，则重叠的发生将被跳过。

## 取消和更新

在可能需要取消时保留一次性计划返回的 ID：

```ts
const id = await c.schedule.after(60_000, "expireSession", sessionId);
await c.schedule.cancel(id);
```

周期性任务通过名称管理：

```ts
await c.cron.delete("presence-sweep");
```

再次调用 `cron.set` 或 `cron.every` 并使用相同名称将替换其配置。

## 失败和幂等性

在重复工作会造成危害时，保持计划操作幂等。有关重试行为和工作流程指导，请参阅 [Execution behavior](/docs/actors/schedule#execution-behavior)。

## 架构

对于全局任务，使用单例 actor 键，例如 `jobs["daily-report"]`。对于隔离的提醒、试用、计费周期或其他每个实体的计划，为每个用户或资源使用一个 actor。

## 参考地图

### Actors

- [Access Control](reference/actors/access-control.md)
- [Actions](reference/actors/actions.md)
- [Actor Keys](reference/actors/keys.md)
- [Actor Runtime Socket](reference/actors/actor-runtime-socket.md)
- [Actor Statuses](reference/actors/statuses.md)
- [Authentication](reference/actors/authentication.md)
- [Cloudflare Workers Quickstart](reference/actors/quickstart/cloudflare.md)
- [Communicating Between Actors](reference/actors/communicating-between-actors.md)
- [Connections](reference/actors/connections.md)
- [Custom Inspector Tabs](reference/actors/inspector-tabs.md)
- [Debugging](reference/actors/debugging.md)
- [Design Patterns](reference/actors/design-patterns.md)
- [Destroying Actors](reference/actors/destroy.md)
- [Effect.ts Quickstart (Beta)](reference/actors/quickstart/effect.md)
- [Errors](reference/actors/errors.md)
- [Fetch and WebSocket Handler](reference/actors/fetch-and-websocket-handler.md)
- [Helper Types](reference/actors/helper-types.md)
- [Icons & Names](reference/actors/appearance.md)
- [In-Memory State](reference/actors/state.md)
- [Input Parameters](reference/actors/input.md)
- [Lifecycle](reference/actors/lifecycle.md)
- [Limits](reference/actors/limits.md)
- [Low-Level HTTP Request Handler](reference/actors/request-handler.md)
- [Low-Level KV Storage](reference/actors/kv.md)
- [Low-Level WebSocket Handler](reference/actors/websocket-handler.md)
- [Metadata](reference/actors/metadata.md)
- [Next.js Quickstart](reference/actors/quickstart/next-js.md)
- [Node.js & Bun Quickstart](reference/actors/quickstart/backend.md)
- [Queues & Run Loops](reference/actors/queues.md)
- [React Quickstart](reference/actors/quickstart/react.md)
- [Realtime](reference/actors/events.md)
- [Rust Quickstart (Beta)](reference/actors/quickstart/rust.md)
- [Scaling & Concurrency](reference/actors/scaling.md)
- [Schedule & Cron](reference/actors/schedule.md)
- [Sharing and Joining State](reference/actors/sharing-and-joining-state.md)
- [SQLite](reference/actors/sqlite.md)
- [SQLite + Drizzle](reference/actors/sqlite-drizzle.md)
- [Supabase Functions Quickstart](reference/actors/quickstart/supabase.md)
- [Testing](reference/actors/testing.md)
- [Troubleshooting](reference/actors/troubleshooting.md)
- [Types](reference/actors/types.md)
- [Vanilla HTTP API](reference/actors/http-api.md)
- [Versions & Upgrades](reference/actors/versions.md)
- [Workflows](reference/actors/workflows.md)

### Cli

- [CLI](reference/cli.md)

### Clients

- [Node.js & Bun](reference/clients/javascript.md)
- [React](reference/clients/react.md)
- [Rust (Beta)](reference/clients/rust.md)
- [Swift](reference/clients/swift.md)
- [SwiftUI](reference/clients/swiftui.md)

### Cookbook

- [AI Agent](reference/cookbook/ai-agent.md)
- [Chat Room](reference/cookbook/chat-room.md)
- [Collaborative Text Editor](reference/cookbook/collaborative-text-editor.md)
- [Cron Jobs and Scheduled Tasks](reference/cookbook/cron-jobs.md)
- [Database per Tenant](reference/cookbook/per-tenant-database.md)
- [Deploying Rivet in a VPC or Air-Gapped Network](reference/cookbook/vpc-air-gapped.md)
- [Live Cursors and Presence](reference/cookbook/live-cursors.md)
- [Multiplayer Game](reference/cookbook/multiplayer-game.md)

### Deploy

- [Container Runner](reference/deploy/container-runner.md)
- [Deploy To Amazon Web Services Lambda](reference/deploy/aws-lambda.md)
- [Deploying to AWS ECS](reference/deploy/aws-ecs.md)
- [Deploying to Cloudflare Workers](reference/deploy/cloudflare.md)
- [Deploying to Freestyle](reference/deploy/freestyle.md)
- [Deploying to Google Cloud Run](reference/deploy/gcp-cloud-run.md)
- [Deploying to Hetzner](reference/deploy/hetzner.md)
- [Deploying to Kubernetes](reference/deploy/kubernetes.md)
- [Deploying to Railway](reference/deploy/railway.md)
- [Deploying to Rivet Compute](reference/deploy/rivet-compute.md)
- [Deploying to Supabase Functions](reference/deploy/supabase.md)
- [Deploying to Vercel](reference/deploy/vercel.md)
- [Deploying to VMs & Bare Metal](reference/deploy/vm-and-bare-metal.md)

### General

- [Actor Configuration](reference/general/actor-configuration.md)
- [Cross-Origin Resource Sharing](reference/general/cors.md)
- [Documentation for LLMs & AI](reference/general/docs-for-llms.md)
- [Edge Networking](reference/general/edge.md)
- [Endpoints](reference/general/endpoints.md)
- [Environment Variables](reference/general/environment-variables.md)
- [HTTP Server](reference/general/http-server.md)
- [Logging](reference/general/logging.md)
- [Pool Configuration](reference/general/pool-configuration.md)
- [Production Checklist](reference/general/production-checklist.md)
- [Registry Configuration](reference/general/registry-configuration.md)
- [Runtime Modes](reference/general/runtime-modes.md)
- [WASM vs Native SDK](reference/general/wasm-vs-native-sdk.md)

### Self Hosting

- [Configuration](reference/self-hosting/configuration.md)
- [Docker Compose](reference/self-hosting/docker-compose.md)
- [Docker Container](reference/self-hosting/docker-container.md)
- [File System](reference/self-hosting/filesystem.md)
- [FoundationDB (Enterprise)](reference/self-hosting/foundationdb.md)
- [Installing Rivet Engine](reference/self-hosting/install.md)
- [Kubernetes](reference/self-hosting/kubernetes.md)
- [Multi-Region](reference/self-hosting/multi-region.md)
- [PostgreSQL](reference/self-hosting/postgres.md)
- [Production Checklist](reference/self-hosting/production-checklist.md)
- [Railway Deployment](reference/self-hosting/railway.md)
- [Render Deployment](reference/self-hosting/render.md)
- [TLS & Certificates](reference/self-hosting/tls.md)
