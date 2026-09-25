# 实时与前端

Trigger.dev 的运行状态和流量的消费者端：在浏览器中读取实时运行更新、渲染 AI/文本流并触发任务。钩子来自 `@trigger.dev/react-hooks`；代币铸造和后端订阅来自 `@trigger.dev/sdk`。

## 设置

```bash
npm add @trigger.dev/react-hooks   # 前端钩子 (React/Next.js/Remix)
# @trigger.dev/sdk 已为后端安装
```

流程始终是：在后台铸造一个作用域代币，将其传递给前端，然后使用钩子订阅。

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

有两种代币类型：公共访问代币（读取/订阅，来自 `auth.createPublicToken`）和 Trigger 代币（浏览器触发，一次性，来自 `auth.createTriggerPublicToken`）。两者默认过期时间为 15 分钟。

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

将 `onComplete: (run, error) => {}` 传递给 react 以在运行完成时触发。

### 2. 使用 `skipColumns` 进行状态仅订阅

对于徽章或进度条，您不需要 `payload`/`output`。跳过它们可以减少网络大小并避免“大型 HTTP 负载”警告。

```tsx
const { run } = useRealtimeRun(runId, {
  accessToken: publicAccessToken,
  skipColumns: ["payload", "output"],
});
```

您可以跳过任何：`payload`、`output`、`metadata`、`startedAt`、`delayUntil`、`queuedAt`、`expiredAt`、`completedAt`、`number`、`isTest`、`usageDurationMs`、`costInCents`、`baseCostInCents`、`ttl`、`payloadType`、`outputType`、`runTags`、`error`。

### 3. 使用 Trigger 代币从浏览器触发

这里的 `accessToken` 是 Trigger 代币（`auth.createTriggerPublicToken`），而不是公共访问代币。

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
import { aiStream } from "@/trigger/streams"; // 定义的流 -> 类型化的 parts

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

没有定义流：`useRealtimeStream<string>(runId, "ai-output", { accessToken })`，或省略键以使用默认流。其他选项：`baseURL`、`startIndex`、`throttleInMs`（默认 16）。传统的 `useRealtimeRunWithStreams(runId, options)` 钩子在您需要同时获取运行及其所有流时仍然受支持。

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
  console.log(run.payload.some, run.output?.some); // 类型化
}
```

`runs.subscribeToRun` 在运行完成时完成，因此循环会自行退出。

## 常见错误

1. **关键：使用公共访问代币从浏览器触发**。从 `createPublicToken` 读取的读取代币不能触发任务。
   - 错误：`useTaskTrigger("my-task", { accessToken: publicAccessTokenFromCreatePublicToken })`
   - 正确：使用 `auth.createTriggerPublicToken("my-task")` 铸造一次性 Trigger 代币并传递该代币。

2. **没有作用域的代币**。无作用域代币授权任何内容，因此每个订阅都会 403。
   - 错误：`await auth.createPublicToken()`
   - 正确：`await auth.createPublicToken({ scopes: { read: { runs: ["run_1234"] } } })`

3. **使用 `useRun`/SWR 进行实时更新轮询**。`useRun` 是基于 SWR 的管理 API 钩子（不推荐用于实时状态）；如果使用它，请设置 `refreshInterval: 0` 以停止轮询。
   - 错误：`useRun(runId, { refreshInterval: 1000 })` 以跟踪进度
   - 正确：`useRealtimeRun(runId, { accessToken })`（无轮询，无需设置 WebSocket）

4. **忘记 `"use client"`**。实时/触发钩子不能在服务器组件中运行。
   - 错误：一个使用 `useRealtimeRun` 的 Next.js App Router 服务器组件
   - 正确：将 `"use client";` 放在任何使用这些钩子的组件的顶部。

5. **发送您未渲染的 `payload`/`output`**
   - 错误：`useRealtimeRun(runId, { accessToken })` 用于状态徽章（网络传输大量有效负载）
   - 正确：`useRealtimeRun(runId, { accessToken, skipColumns: ["payload", "output"] })`

6. **在 handle 存在之前订阅**
   - 错误：`useRealtimeRun(handle, { accessToken: handle?.publicAccessToken })` 没有保护
   - 正确：添加 `enabled: !!handle` 以便仅在触发返回 handle 后订阅。

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

此技能捆绑在 `@trigger.dev/sdk` 中并直接从 `node_modules` 读取，因此始终与您的安装 SDK 版本匹配（请参阅旁边的 `package.json`）。这些 API 的完整文档与其一起打包在 `@trigger.dev/sdk/docs/` 下。
