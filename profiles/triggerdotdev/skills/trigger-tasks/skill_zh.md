# 编写 Trigger.dev 任务

任务是可以长时间运行且具有强大容错能力的函数。在您的 `/trigger` 目录下的文件中定义它们。始终从 `@trigger.dev/sdk` 导入，切勿从 `@trigger.dev/sdk/v3`（已弃用的别名）或 `@trigger.dev/core` 导入。

## 设置

```ts
// /trigger/hello-world.ts
import { task } from "@trigger.dev/sdk";

export const helloWorld = task({
  id: "hello-world", // 在项目中唯一
  run: async (payload: { message: string }, { ctx }) => {
    console.log(payload.message, "尝试", ctx.attempt.number);
    return { ok: true }; // 必须是 JSON 可序列化的
  },
});
```

`run` 函数接收 payload 和第二个包含 `ctx`（运行上下文）、中止 `signal` 和已弃用的 `init` 输出的参数。返回值是任务输出，必须是 JSON 可序列化的。

## 核心模式

### 1. 使用 `schemaTask` 验证 payload

`schema` 接受 Zod / Yup / Superstruct / ArkType / valibot / typebox 解析器或自定义 `(data: unknown) => T` 函数。验证失败会抛出 `TaskPayloadParsedError` 并跳过重试。

```ts
import { schemaTask } from "@trigger.dev/sdk";
import { z } from "zod";

export const createUser = schemaTask({
  id: "create-user",
  schema: z.object({ name: z.string(), age: z.number() }),
  run: async (payload) => ({ greeting: `Hi ${payload.name}` }),
});
```

### 2. 配置重试和提前中止

默认的 `maxAttempts` 是 3。抛出 `AbortTaskRunError` 可立即停止重试。任务级别的 `retry` 会覆盖配置文件中的默认值。

```ts
import { task, AbortTaskRunError } from "@trigger.dev/sdk";

export const charge = task({
  id: "charge",
  retry: { maxAttempts: 5, factor: 1.8, minTimeoutInMs: 500, maxTimeoutInMs: 30_000, randomize: true },
  run: async (payload: { amount: number }) => {
    if (payload.amount <= 0) throw new AbortTaskRunError("Invalid amount"); // 不重试
    // 可能会抛出并重试的工作
  },
});
```

对于更精细的控制，`catchError: async ({ payload, error, ctx, retryAt }) => {...}` 可以返回 `{ skipRetrying: true }`、`{ retryAt: Date }` 或 `undefined`（使用正常逻辑）。`retry.onThrow`、`retry.fetch` 也存在于任务内重试中。

### 3. 触发另一个任务并处理结果

在任务内部使用 `yourTask.triggerAndWait(payload)`。结果是 Result 对象，您必须检查 (`ok`)，或 `.unwrap()` 以在失败时抛出。

```ts
export const parentTask = task({
  id: "parent-task",
  run: async () => {
    const result = await childTask.triggerAndWait({ data: "x" });
    if (result.ok) return result.output; // 带有类型信息的子任务输出
    console.error("子任务失败", result.error);
    // 或: const output = await childTask.triggerAndWait({ data: "x" }).unwrap();
  },
});
```

`SubtaskUnwrapError` 包含 `runId`、`taskId` 和 `cause`。对于分支执行，使用 `childTask.batchTriggerAndWait([{ payload: a }, { payload: b }])`；结果有一个 `.runs` 数组，每个条目 `{ ok, id, output?, error?, taskIdentifier }`。

### 4. 使用类型仅导入从后端代码触发

在任务外部，仅导入任务类型并按 ID 触发。不要将任务实例导入后端包中。

```ts
import { tasks } from "@trigger.dev/sdk";
import type { emailSequence } from "~/trigger/emails";

const handle = await tasks.trigger<typeof emailSequence>(
  "email-sequence",
  { to: "a@b.com", name: "Ada" },
  { delay: "1h" }
);
```

`tasks.batchTrigger` 和 `batch.trigger([{ id, payload }])` 覆盖批量。触发选项包括 `delay`、`ttl`、`idempotencyKey`、`idempotencyKeyTTL`、`debounce`、`queue`、`concurrencyKey`、`maxAttempts`、`tags`、`metadata`、`priority`、`region` 和 `machine`。使用 `runs.retrieve`、`runs.cancel` 和 `runs.reschedule` 检查运行情况。

### 5. 重复性密钥

`idempotencyKeys.create(key, { scope })` 返回一个 64 个字符的哈希密钥。原始字符串密钥默认为 `"run"` 范围（v4.3.1+）；对于一次性行为，使用 `scope: "global"`。

```ts
import { idempotencyKeys, task } from "@trigger.dev/sdk";

export const processOrder = task({
  id: "process-order",
  run: async (payload: { orderId: string; email: string }) => {
    const key = await idempotencyKeys.create(`confirm-${payload.orderId}`);
    await sendEmail.trigger({ to: payload.email }, { idempotencyKey: key });
  },
});
```

### 6. 等待和运行元数据

`wait.for({ seconds })` 和 `wait.until({ date })` 持久化暂停运行。`metadata.*` 仅在 `run()` 内可读写；更新是同步的且可链式 (`set`、`del`、`replace`、`append`、`remove`、`increment`、`decrement`)。

```ts
import { task, metadata, wait } from "@trigger.dev/sdk";

export const importer = task({
  id: "importer",
  run: async (payload: { rows: unknown[] }) => {
    metadata.set("status", "processing").set("total", payload.rows.length);
    await wait.for({ seconds: 5 });
    metadata.set("status", "complete");
  },
});
```

对于人工干预，`wait.createToken({ timeout, tags })` 返回 `{ id, url, publicAccessToken, ... }`；使用 `wait.forToken<T>(token: string | { id: string })` 继续并返回 `{ ok, output?, error? }`（或 `.unwrap()`），并在其他地方使用 `wait.completeToken(tokenId, output)` 完成它。元数据最大为 256KB，不会传递给子任务；使用 `metadata.parent.*` / `metadata.root.*` 向父任务推送值。（`metadata.stream` 自 4.1.0 起已弃用，改为 `streams.pipe()`。）

### 7. 定时（cron）任务

```ts
import { schedules } from "@trigger.dev/sdk";

export const dailyReport = schedules.task({
  id: "daily-report",
  cron: { pattern: "0 5 * * *", timezone: "Asia/Tokyo" },
  run: async (payload) => {
    console.log("定时于", payload.timestamp, "下次", payload.upcoming);
  },
});
```

payload 包括 `timestamp`、`lastTimestamp`、`timezone`、`scheduleId`、`externalId` 和 `upcoming`。动态附加定时任务使用 `schedules.create({ task, cron, timezone?, externalId?, deduplicationKey })`（重复密钥是必需的且每个项目唯一），加上 `retrieve / list / update / activate / deactivate / del / timezones`。

### 8. 队列和并发

在任务上设置 `queue: { concurrencyLimit }`，或跨任务共享队列：

```ts
import { queue, task } from "@trigger.dev/sdk";

export const emails = queue({ name: "emails", concurrencyLimit: 5 });

export const sendEmail = task({ id: "send-email", queue: emails, run: async () => {} });
```

在触发时使用 `{ queue: "queue-name" }` 覆盖，并为每个租户队列添加 `concurrencyKey`。使用 `queues.list / retrieve / pause / resume / overrideConcurrencyLimit / resetConcurrencyLimit` 管理队列。

### 9. `trigger.config.ts` 基本要素

```ts
import { defineConfig } from "@trigger.dev/sdk";

export default defineConfig({
  project: "<project ref>",
  dirs: ["./trigger"],
  machine: "small-1x",
  retries: {
    enabledInDev: false,
    default: { maxAttempts: 3, factor: 2, minTimeoutInMs: 1000, maxTimeoutInMs: 10000, randomize: true },
  },
});
```

`build.external` 控制哪些包保留在包外。构建扩展 (`additionalFiles`, `prismaExtension`, `puppeteer`, `playwright`, `ffmpeg`, `pythonExtension`, `aptGet`, `syncEnvVars`, 等）来自 `@trigger.dev/build`。`telemetry` 配置仪化和导出器。每个扩展都有自己的设置文档，所有文档捆绑在 `@trigger.dev/sdk/docs/config/extensions/` 下（从 `overview.mdx` 开始）；在连接之前阅读您需要的文档，而不是猜测 API。

### 日志记录

`logger.debug / log / info / warn / error(message, dataRecord?)` 写入结构化日志；`logger.trace(name, async (span) => {...})` 添加一个跨度。模块级指标使用 `otel.metrics.getMeter(name)`。

## 常见错误

1. **关键：将等待结果视为输出。** `triggerAndWait` 和 `wait.forToken` 返回 Result 对象，不是原始输出。
   - 错误: `const out = await childTask.triggerAndWait(p); use(out.foo);`
   - 正确: `const r = await childTask.triggerAndWait(p); if (r.ok) use(r.output.foo);`（或 `.unwrap()`）。

2. **将 `triggerAndWait` / `batchTriggerAndWait` / `wait` 包裹在 `Promise.all` 中。**
   - 错误: `await Promise.all([childTask.triggerAndWait(a), childTask.triggerAndWait(b)]);`
   - 正确: `await childTask.batchTriggerAndWait([{ payload: a }, { payload: b }]);`（或顺序 for 循环）。

3. **将任务实例导入后端代码。**
   - 错误: 在路由处理器中 `import { emailSequence } from "~/trigger/emails";`。
   - 正确: `import type { emailSequence }` 加上 `tasks.trigger<typeof emailSequence>("email-sequence", payload)`。

4. **在 `run()` 外调用 `metadata.set/get`。**
   - 错误: 在模块作用域或无关的后端代码中设置元数据（无操作；`get` 返回 `undefined`）。
   - 正确: 在 `run()` 或任务生命周期钩子中调用。

5. **假设子任务继承父任务的队列或元数据。**
   - 错误: 期望子任务共享父任务的 `concurrencyLimit` 或看到其元数据。
   - 正确: 子任务在自己的队列中运行；通过 `{ metadata: metadata.current() }` 显式传递元数据，或使用 `metadata.parent.*` 推送。

6. **捆绑原生/WASM 包。**
   - 错误: 将 `sharp`、`re2`、`sqlite3` 或 WASM 包保留在默认包中。
   - 正确: 在 `trigger.config.ts` 中将它们添加到 `build.external`。

7. **依赖原始字符串 idempotencyKey 为全局。**
   - 错误: `trigger(p, { idempotencyKey: "welcome-email" })` 期望一次性（仅在 v4.3.0 及更早版本中为真）。
   - 正确: `await idempotencyKeys.create("welcome-email", { scope: "global" })`。

## 参考

兄弟技能：

- **trigger-realtime** 用于订阅运行情况并使用 React 钩子从前端触发。
- **trigger-authoring-chat-agent** 和 **trigger-chat-agent-advanced** 用于构建 AI 聊天代理。

参考文档与该技能一起打包在同一包中，本地读取（无需网络），固定到您的安装版本。`sources:` 前置页列出了该技能引用的所有文档，都在 `@trigger.dev/sdk/docs/` 下。从以下文档开始：

- `@trigger.dev/sdk/docs/tasks/overview.mdx`
- `@trigger.dev/sdk/docs/triggering.mdx`
- `@trigger.dev/sdk/docs/config/config-file.mdx`

## 版本

该技能捆绑在 `@trigger.dev/sdk` 中，直接从 `node_modules` 读取，因此始终与您的安装 SDK 版本匹配（请参阅旁边的 `package.json`）。这些 API 的完整文档与其一同打包在 `@trigger.dev/sdk/docs/` 下。
