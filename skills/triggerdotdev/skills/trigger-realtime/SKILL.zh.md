---
name: trigger-realtime
description: Trigger.dev 客户端/前端界面：实时订阅运行（runs.subscribeToRun 和 @trigger.dev/react-hooks hook useRealtimeRun），在 React 中消费元数据和 AI/文本流（useRealtimeStream），从浏览器触发任务（useTaskTrigger, useRealtimeTaskTrigger），并使用 auth.createPublicToken / auth.createTriggerPublicToken 创建作用域前端凭证。在连接前端（React/Next.js/Remix）或后端-前端时加载，以显示实时运行进度、状态徽章、令牌流、触发按钮或等待令牌审批 UI。不用于编写后端任务本身（streams.define / metadata.set 属于 trigger-tasks 范围）；这是消费者端。
---

# 实时与前端

Trigger.dev 的运行状态和流量的消费者端：在浏览器中读取实时运行更新、渲染 AI/文本流，并触发任务。钩子来自 `@trigger.dev/react-hooks`；代币铸造和后端订阅来自 `@trigger.dev/sdk`。

## 设置

```bash
npm add @trigger.dev/react-hooks   # 前端钩子 (React/Next.js/Remix)
# @trigger.dev/sdk 已为后端安装
```

流程始终是：在后台铸造一个作用域内的代币，将其传递给前端，然后使用钩子订阅。

```ts
// 后台 (API 路由 / 服务器操作)
import { auth } from "@trigger.dev/sdk";

const publicAccessToken = await auth.createPublicToken({
  scopes: { read: { runs: ["run_1234"] } }, // 没有作用域的代币没有用处
});
```

```tsx
// 前端
"use client";
import { useRealtimeRun } from "@trigger.dev/react-hooks";

export function RunStatus({ runId, publicAccessToken }: { runId: string; publicAccessToken: string }) {
  const { run, error } = useRealtimeRun(runId, { accessToken: publicAccessToken });
  if (error) return <div>Error: {error.message}</div>;
  if (!run) return <div>Loading...</div>;
  return <div>Run: {run.status}</div>;
}
```

有两种代币类型：公共访问代币（读取/订阅，来自 `auth.createPublicToken`）和触发代币（浏览器触发，单次使用，来自 `auth.createTriggerPublicToken`）。两者默认过期时间为 15 分钟。

## 核心模式

### 1. 订阅运行并渲染元数据进度

`metadata` 是 `Record<string, DeserializedJson>`，因此嵌套值需要强制转换。

```tsx
"use client";
import { useRealtimeRun } from "@trigger.dev/react-hooks";
import type { myTask } from "@/trigger/myTask";

export function Progress({ runId, publicAccessToken }: { runId: string; publicAccessToken: string }) {
  const { run, error } = useRealtimeRun<typeof myTask>(runId, { accessToken: publicAccessToken });
  if (error) return <div>Error: {error.message}</div>;
  if (!run) return <div>Loading...</div>;
  const progress = run.metadata?.progress as { percentage?: number } | undefined;
  return <div>{run.status}: {progress?.percentage ?? 0}%</div>;
}
```

当运行完成时，将 `onComplete: (run, error) => {}` 传递给 react。

### 2. 使用 `skipColumns` 的状态仅订阅

对于徽章或进度条，您不需要 `payload`/`output`。跳过它们可以减少线路大小并避免“大型 HTTP 负载”警告。

```tsx
const { run } = useRealtimeRun(runId, {
  accessToken: publicAccessToken,
  skipColumns: ["payload", "output"],
});
```

您可以跳过任何：`payload`、`output`、`metadata`、`startedAt`、`delayUntil`、`queuedAt`、`expiredAt`、`completedAt`、`number`、`isTest`、`usageDurationMs`、`costInCents`、`baseCostInCents`、`ttl`、`payloadType`、`outputType`、`runTags`、`error`。

### 3. 使用触发代币从浏览器触发

这里的 `accessToken` 是触发代币（`auth.createTriggerPublicToken`），而不是公共访问代币。

```tsx
"use client";
import { useTaskTrigger } from "@trigger.dev/react-hooks";
import type { myTask } from "@/trigger/myTask";

export function TriggerButton({ triggerToken }: { triggerToken: string }) {
  const { submit, handle, isLoading } = useTaskTrigger<typeof myTask>("my-task", {
    accessToken: triggerToken,
  });
  if (handle) return <div>Run ID: {handle.id}</div>;
  return (
    <button onClick={() => submit({ foo: "bar" }, { tags: ["user:123"] })} disabled={isLoading}>
      {isLoading ? "Triggering..." : "Run"}
    </button>
  );
}
```

`submit(payload, options?)` 接收与后端 `trigger` 调用相同的选项。

### 4. 在一个钩子中触发和订阅

```tsx
"use client";
import { useRealtimeTaskTrigger } from "@trigger.dev/react-hooks";
import type { myTask } from "@/trigger/myTask";

export function Runner({ publicAccessToken }: { publicAccessToken: string }) {
  const { submit, run, isLoading } = useRealtimeTaskTrigger<typeof myTask>("my-task", {
    accessToken: publicAccessToken,
  });
  if (run) return <div>{run.status}</div>;
  return <button onClick={() => submit({ foo: "bar" })} disabled={isLoading}>Run</button>;
}
```

当您还需要任务流时，使用 `useRealtimeTaskTriggerWithStreams<typeof myTask, STREAMS>`（它返回 `{ submit, run, streams, error, isLoading }`）。

### 5. 消费 AI/文本流（SDK 4.1.0+ 推荐使用）

`useRealtimeStream` 接收定义的流以实现完整的类型安全，或接收 `runId` 加上可选的流键。返回 `{ parts, error }`。

```tsx
"use client";
import { useRealtimeStream } from "@trigger.dev/react-hooks";
import { aiStream } from "@/trigger/streams"; // 定义流 -> 类型安全的 parts

export function StreamView({ runId, publicAccessToken }: { runId: string; publicAccessToken: string }) {
  const { parts, error } = useRealtimeStream(aiStream, runId, {
    accessToken: publicAccessToken,
    timeoutInSeconds: 300, // 默认 60
    onData: (chunk) => console.log(chunk),
  });
  if (error) return <div>Error: {error.message}</div>;
  if (!parts) return <div>Loading...</div>;
  return <div>{parts.join("")}</div>;
}
```

没有定义流：`useRealtimeStream<string>(runId, "ai-output", { accessToken })`，或省略键以使用默认流。其他选项：`baseURL`、`startIndex`、`throttleInMs`（默认 16）。传统的 `useRealtimeRunWithStreams(runId, options)` 钩子仍然受支持，当您需要同时获取运行及其所有流时。

### 6. 将输入发送回正在运行的任务

```tsx
"use client";
import { useInputStreamSend } from "@trigger.dev/react-hooks";
import { approval } from "@/trigger/streams";

export function ApprovalForm({ runId, accessToken }: { runId: string; accessToken: string }) {
  const { send, isLoading, isReady } = useInputStreamSend(approval.id, runId, { accessToken });
  return (
    <button disabled={!isReady || isLoading} onClick={() => send({ approved: true })}>
      Approve
    </button>
  );
}
```

### 7. 从 React 完成等待代币

```ts
// 后台：创建代币，将 id + publicAccessToken 返回给前端
import { wait } from "@trigger.dev/sdk";
const token = await wait.createToken({ timeout: "10m" });
return { tokenId: token.id, publicToken: token.publicAccessToken };
```

```tsx
"use client";
import { useWaitToken } from "@trigger.dev/react-hooks";

export function Approve({ tokenId, publicToken }: { tokenId: string; publicToken: string }) {
  const { complete } = useWaitToken(tokenId, { accessToken: publicToken });
  return <button onClick={() => complete({ approved: true })}>Approve</button>;
}
```

### 8. 从后台订阅（异步迭代器）

```ts
import { runs, tasks } from "@trigger.dev/sdk";
import type { myTask } from "./trigger/my-task";

const handle = await tasks.trigger("my-task", { some: "data" });
for await (const run of runs.subscribeToRun<typeof myTask>(handle.id)) {
  console.log(run.payload.some, run.output?.some); // 类型安全的
}
```

`runs.subscribeToRun` 在运行完成时完成，因此循环会自行退出。

## 常见错误

1. **关键：使用公共访问代币从浏览器触发** 从 `createPublicToken` 读取的读取代币不能触发任务。
   - 错误：`useTaskTrigger("my-task", { accessToken: publicAccessTokenFromCreatePublicToken })`
   - 正确：使用 `auth.createTriggerPublicToken("my-task")` 铸造单次使用的触发代币，并将该代币传递过去。

2. **没有作用域的代币** 无作用域的代币授权什么都没有，因此每个订阅都会 403。
   - 错误：`await auth.createPublicToken()`
   - 正确：`await auth.createPublicToken({ scopes: { read: { runs: ["run_1234"] } } })`

3. **使用 `useRun`/SWR 进行实时更新的轮询** `useRun` 是基于 SWR 的管理 API 钩子（不推荐用于实时状态）；如果使用它，请设置 `refreshInterval: 0` 以停止轮询。
   - 错误：`useRun(runId, { refreshInterval: 1000 })` 以跟踪进度
   - 正确：`useRealtimeRun(runId, { accessToken })`（不轮询，无需设置 WebSocket）

4. **忘记 `"use client"`** 实时/触发钩子不能在服务器组件中运行。
   - 错误：一个使用 `useRealtimeRun` 的 Next.js App Router 服务器组件
   - 正确：在任何使用这些钩子的组件顶部放置 `"use client";`

5. **发送您未渲染的 `payload`/`output`**
   - 错误：`useRealtimeRun(runId, { accessToken })` 用于状态徽章（线路上的大型有效负载）
   - 正确：`useRealtimeRun(runId, { accessToken, skipColumns: ["payload", "output"] })`

6. **在句柄存在之前订阅**
   - 错误：`useRealtimeRun(handle, { accessToken: handle?.publicAccessToken })` 没有保护
   - 正确：添加 `enabled: !!handle`，以便仅在触发返回句柄后订阅。

## 参考

兄弟技能：
- `trigger-tasks` 用于任务端：`streams.define()`、`metadata.set()` 和 `wait.createToken`。
- `trigger-authoring-chat-agent` 和 `trigger-chat-agent-advanced` 用于聊天代理，它们基于这些实时流。

参考文档与该技能一起打包在同一包中，本地阅读（无需网络），固定到您的安装版本。上面的 `sources:` 前置映射列出了该技能引用的每个文档，都在 `@trigger.dev/sdk/docs/` 下。从以下内容开始：
- `@trigger.dev/sdk/docs/realtime/react-hooks/subscribe.mdx`
- `@trigger.dev/sdk/docs/realtime/react-hooks/streams.mdx`
- `@trigger.dev/sdk/docs/realtime/auth.mdx`
- `@trigger.dev/sdk/docs/realtime/run-object.mdx`（实时运行对象与管理 API 返回的 `useRun` 对象不同）

## 版本

此技能捆绑在 `@trigger.dev/sdk` 中，并直接从 `node_modules` 读取，因此它始终与您的安装 SDK 版本匹配（请参阅旁边的 `package.json`）。这些 API 的完整文档与其一起打包在 `@trigger.dev/sdk/docs/` 下。
