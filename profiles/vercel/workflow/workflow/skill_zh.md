## *关键*：始终使用正确的 `workflow` 文档

你关于 `workflow` 的知识已经过时。

下面列出的 `workflow` 文档与已安装的 Workflow SDK 版本相匹配。
在开始任何 `workflow` 相关任务之前，请遵循以下说明：

在 `node_modules/workflow/docs/` 中搜索捆绑的文档：

1. **查找文档**：`glob "node_modules/workflow/docs/**/*.mdx"`
2. **搜索内容**：`grep "your query" node_modules/workflow/docs/`

`node_modules/workflow/docs/` 中的文档结构：

- `getting-started/` - 框架设置（next.mdx、express.mdx、hono.mdx 等）
- `foundations/` - 核心概念（workflows-and-steps.mdx、hooks.mdx、streaming.mdx 等）
- `api-reference/workflow/` - API 文档（sleep.mdx、create-hook.mdx、fatal-error.mdx 等）
- `api-reference/workflow-api/` - 客户端 API（start.mdx、get-run.mdx、resume-hook.mdx 等）
- `api-reference/workflow-runtime/` - 运行时 API（get-world.mdx）和 `world/` World SDK（storage.mdx、streams.mdx、queue.mdx）
- `api-reference/workflow-observability/` - 水合与名称解析工具（hydrate-resource-io.mdx、parse-workflow-name.mdx 等）
- `ai/`：AI SDK 集成文档
- `errors/` - 错误代码文档

相关包也包含捆绑文档：

- `@ai-sdk/workflow`：`node_modules/ai/docs/` - WorkflowAgent 和 AI SDK 集成
- `@workflow/ai`：`node_modules/@workflow/ai/docs/` - 面向现有应用的已弃用 DurableAgent API
- `@workflow/core`：`node_modules/@workflow/core/docs/` - 核心运行时（foundations、how-it-works）
- `@workflow/next`：`node_modules/@workflow/next/docs/` - Next.js 集成

**如有疑问，请更新到 Workflow SDK 的最新版本。**

### 官方资源

- **网站**：https://workflow-sdk.dev
- **GitHub**：https://github.com/vercel/workflow

### 快速参考

**指令：**

```typescript
"use workflow";  // 第一行 - 使异步函数具备持久性
"use step";      // 第一行 - 使函数成为可缓存、可重试的单元
```

**基本导入：**

```typescript
// Workflow 原语
import { sleep, fetch, createHook, createWebhook, getWritable } from "workflow";
import { FatalError, RetryableError } from "workflow";
import { getWorkflowMetadata, getStepMetadata } from "workflow";

// API 操作
import { start, getRun, resumeHook, resumeWebhook } from "workflow/api";

// 可观测性与数据水合
import { hydrateResourceIO, observabilityRevivers, parseStepName, parseWorkflowName } from "workflow/observability";

// 框架集成
import { withWorkflow } from "workflow/next";
import { workflow } from "workflow/vite";
import { workflow } from "workflow/astro";
// 或者使用模块：["workflow/nitro"] 用于 Nitro/Nuxt

// AI 代理（Workflow 5）
import { WorkflowAgent, type ModelCallStreamPart } from "@ai-sdk/workflow";
```

## 优先使用 step 函数以避免沙箱错误

`"use workflow"` 函数在沙箱化 VM 中运行。`"use step"` 函数具有**完整的 Node.js 访问权限**。将逻辑放在 step 中，workflow 函数纯粹用于编排。

```typescript
// Steps 具有完整的 Node.js 和 npm 访问权限
async function fetchUserData(userId: string) {
  "use step";
  const response = await fetch(`https://api.example.com/users/${userId}`);
  return response.json();
}

async function processWithAI(data: any) {
  "use step";
  // AI SDK 在 steps 中无需变通方案即可工作
  return await generateText({
    model: "spacexai/grok-4.6",
    prompt: `Process: ${JSON.stringify(data)}`,
  });
}

// Workflow 编排 steps - 无沙箱问题
export async function dataProcessingWorkflow(userId: string) {
  "use workflow";
  const data = await fetchUserData(userId);
  const processed = await processWithAI(data);
  return { success: true, processed };
}
```

**优势：** Steps 具有自动重试，结果会被持久化以支持重放，且没有沙箱限制。

## Workflow 沙箱限制

当你需要在 workflow 函数中（而非 step 中）直接编写逻辑时，以下限制适用：

| 限制 | 变通方法 |
|------------|------------|
| 无法使用 `fetch()` | `import { fetch } from "workflow"` 然后 `globalThis.fetch = fetch` |
| 无法使用 `setTimeout`/`setInterval` | 使用来自 `"workflow"` 的 `sleep("5s")` |
| 无法使用 Node.js 模块（fs、crypto 等） | 移到 step 函数中 |

**示例 - 在 workflow 上下文中使用 fetch：**

```typescript
import { fetch } from "workflow";

export async function myWorkflow() {
  "use workflow";
  globalThis.fetch = fetch;  // AI SDK 和 HTTP 库需要此项
  // 现在 generateText() 和其他库可以正常工作
}
```

**注意：** 普通的 `"provider/model"` 字符串通过 Vercel AI Gateway 路由。除非用户明确需要仅限 provider 的功能，否则不要直接构造 provider 实例。

## WorkflowAgent：Workflow 5 中的 AI 代理

使用 AI SDK 的 `WorkflowAgent` 在 Workflow 5 中构建持久化代理。它替代了 `@workflow/ai` 中已弃用的 `DurableAgent` API，并对模型调用和 step 支撑的工具进行检查点记录。

```typescript
import { WorkflowAgent, type ModelCallStreamPart } from "@ai-sdk/workflow";
import { isStepCount, tool } from "ai";
import { getWritable } from "workflow";
import { z } from "zod";

async function lookupData({ query }: { query: string }) {
  "use step";
  // Step 函数具有完整的 Node.js 访问权限
  return `Results for "${query}"`;
}

export async function myAgentWorkflow(userMessage: string) {
  "use workflow";

  const agent = new WorkflowAgent({
    model: "spacexai/grok-4.6",
    instructions: "You are a helpful assistant.",
    tools: {
      lookupData: tool({
        description: "Search for information",
        inputSchema: z.object({ query: z.string() }),
        execute: lookupData,
      }),
    },
  });

  const result = await agent.stream({
    messages: [{ role: "user", content: userMessage }],
    writable: getWritable<ModelCallStreamPart>(),
    stopWhen: isStepCount(10),
  });

  return result.messages;
}
```

**要点：**
- 普通的 `"provider/model"` 字符串通过 Vercel AI Gateway 路由；`spacexai/grok-4.6` 是 Workflow 示例中的默认模型
- `getWritable<ModelCallStreamPart>()` 流式传输持久化模型调用输出；在 HTTP 路由中使用 `createModelCallToUIChunkTransform()` 进行转换
- 需要 Node.js/npm 访问权限的工具 `execute` 函数应使用 `"use step"`
- 使用 workflow 原语（`sleep()`、`createHook()`）的工具 `execute` 函数**不应**使用 `"use step"`，因为它们在 workflow 级别运行
- `stopWhen` 限制模型调用次数；默认行为是在模型停止调用工具时终止
- 多轮对话：将 `result.messages` 加上新用户消息传递给后续 `agent.stream()` 调用

**更多详情，请查看已安装的 AI SDK 包中的 WorkflowAgent 文档或 https://ai-sdk.dev/v7/docs/agents/workflow-agent 。**

## 启动 workflow 和子 workflow

使用 `start()` 从 API 路由启动 workflow。在 Workflow 5 中，`start()` 也可以直接从 workflow 函数中调用来派生子运行；它具有 step 支撑，并在父级的事件日志中记录一个确定性边界。

```typescript
import { start } from "workflow/api";

// 从 API 路由调用；可直接使用
export async function POST() {
  const run = await start(myWorkflow, [arg1, arg2]);
  return Response.json({ runId: run.runId });
}

// 无参数 workflow
const run = await start(noArgWorkflow);
```

**在 Workflow 5 的 workflow 内部启动子 workflow：**

```typescript
import { start } from "workflow/api";

export async function parentWorkflow() {
  "use workflow";
  const childRun = await start(childWorkflow, ["some data"]);
  await sleep("1h");
  return { childRunId: childRun.runId };
}
```

`start()` 在创建子运行后返回，不会等待其完成。仅在父级需要等待子级时才使用 `childRun.returnValue`；workflow 内部对每个 `Run` 属性的访问或方法调用都是一个 step。

## Hooks：通过外部事件暂停和恢复

Hooks 让 workflow 等待外部数据。在 workflow 内部使用 `createHook()`，从 API 路由使用 `resumeHook()`。确定性令牌仅用于 `createHook()` + `resumeHook()`（服务端）。`createWebhook()` 始终生成随机令牌，因此不要向 `createWebhook()` 传递 `token` 选项。

### 单事件

```typescript
import { createHook } from "workflow";

export async function approvalWorkflow() {
  "use workflow";

  const hook = createHook<{ approved: boolean }>({
    token: "approval-123",  // 供外部系统使用的确定性令牌
  });

  const result = await hook;  // Workflow 在此处挂起
  return result.approved;
}
```

### 多事件（可迭代 hooks）

Hooks 实现了 `AsyncIterable`。使用 `for await...of` 接收多个事件：

```typescript
import { createHook } from "workflow";

export async function chatWorkflow(channelId: string) {
  "use workflow";

  const hook = createHook<{ text: string; done?: boolean }>({
    token: `chat-${channelId}`,
  });

  for await (const event of hook) {
    await processMessage(event.text);
    if (event.done) break;
  }
}
```

每次 `resumeHook(token, payload)` 调用都会向循环传递下一个值。

### 从 API 路由恢复

```typescript
import { resumeHook } from "workflow/api";

export async function POST(req: Request) {
  const { token, data } = await req.json();
  await resumeHook(token, data);
  return new Response("ok");
}
```

## 错误处理

对于永久性故障（不重试）使用 `FatalError`，对于瞬时性故障使用 `RetryableError`：

```typescript
import { FatalError, RetryableError } from "workflow";

if (res.status === 429) {
  throw new RetryableError("Rate limited", { retryAfter: "5m" });
}
if (res.status >= 400 && res.status < 500) {
  throw new FatalError(`Client error: ${res.status}`);
}
```

## 序列化

传递到/从 workflow 和 step 的所有数据必须是可序列化的。

**支持的内置类型：** string、number、boolean、null、undefined、bigint、普通对象、数组、Date、RegExp、URL、URLSearchParams、Map、Set、Headers、ArrayBuffer、类型化数组、Request、Response、ReadableStream、WritableStream。

**不支持的类型：** 函数、Symbols、WeakMap/WeakSet。传递数据，而非回调。

### 自定义类序列化

类实例**可以**通过实现 `@workflow/serde` 协议在 workflow/step 边界之间序列化。当类具有带 `"use step"` 的实例方法，或者需要在 steps 之间传递类实例时，这是必需的。

**安装：** `@workflow/serde` 必须是包含该类的包的依赖项。

**模式：** 在类体内部使用计算属性语法添加两个静态方法：

```typescript
import { WORKFLOW_SERIALIZE, WORKFLOW_DESERIALIZE } from "@workflow/serde";

export class Point {
  x: number;
  y: number;

  constructor(x: number, y: number) {
    this.x = x;
    this.y = y;
  }

  // 序列化：返回纯数据（必须仅使用 devalue 兼容类型）
  static [WORKFLOW_SERIALIZE](instance: Point) {
    return { x: instance.x, y: instance.y };
  }

  // 反序列化：从纯数据重建
  static [WORKFLOW_DESERIALIZE](data: { x: number; y: number }) {
    return new Point(data.x, data.y);
  }

  async computeDistance(other: Point) {
    "use step";
    return Math.sqrt((this.x - other.x) ** 2 + (this.y - other.y) ** 2);
  }
}
```

**关键规则：**
1. **在类体内部定义 serde 方法**，作为使用计算属性语法的静态方法（`static [WORKFLOW_SERIALIZE](...)`）。SWC 插件通过扫描类来检测它们。不要外部分配（例如 `(MyClass as any)[WORKFLOW_SERIALIZE] = ...`）—— 编译器不会检测到这种方式。
2. **Serde 方法只能返回 devalue 兼容类型**（普通对象、数组、原始值、Date、Map、Set、Uint8Array 等）。不能有函数、类实例或 Node.js 特定对象。
3. **为依赖 Node.js 的实例方法添加 `"use step"`。** SWC 插件会从 workflow 包中移除 `"use step"` 方法体。这就是如何将 Node.js 导入（fs、crypto、child_process 等）排除在 workflow 沙箱之外的方式。带有 serde 方法的类壳保留在 workflow 包中；只有 step 方法体被移除。
4. **不要手动注册类。** SWC 插件自动生成注册代码（一个设置 `classId` 并将类添加到全局注册表的 IIFE）。手动调用 `registerSerializationClass()` 既无必要又容易出错。
5. **不要使用动态导入来绕过沙箱限制。** 如果类方法需要 Node.js API，正确的解决方案是 `"use step"`，而不是 `/* @vite-ignore */ import(...)`。

**Serde 适用场景：** 纯数据类、领域模型、配置对象，以及 Node.js 依赖方法可以用 `"use step"` 标记的类。

**应避免使用 serde 的场景：** 如果类从根本上与 Node.js API 不可分离（每个方法都需要 `fs`、`net` 等），且无法有意义地作为壳存在于 workflow 沙箱中，则将其完全保留在 step 函数中，在边界之间传递普通数据对象。

### 验证 serde 合规性

使用以下工具验证类的配置是否正确：

- **`workflow transform <file> --check-serde`** -- 显示文件的 SWC 转换输出并检查 serde 类是否合规（workflow 包中没有残留 Node.js 导入）。
- **`workflow validate`** -- 扫描所有 workflow 文件并报告 serde 合规性问题。使用 `--json` 获取机器可读输出。
- **SWC Playground** -- `workbench/swc-playground` 处的网络 playground 在检测到 serde 模式时显示 Serde 分析面板。
- **构建时警告** -- 构建器在 serde 类在 workflow 包中仍有 Node.js 内置导入时自动发出警告。

## 流式传输

使用 `getWritable()` 从 workflow 流式传输数据。`getWritable()` 可以在 workflow 和 step 上下文中**两者**调用，但你**不能**在 workflow 函数中直接操作流（调用 `getWriter()`、`write()`、`close()`）。流必须传递给 step 函数进行实际 I/O，或者 step 可以自行调用 `getWritable()`。

**在 workflow 中获取流，传递给 step：**
```typescript
import { getWritable } from "workflow";

export async function myWorkflow() {
  "use workflow";
  const writable = getWritable();
  await writeData(writable, "hello world");
}

async function writeData(writable: WritableStream, chunk: string) {
  "use step";
  const writer = writable.getWriter();
  try {
    await writer.write(chunk);
  } finally {
    writer.releaseLock();
  }
}
```

**直接在 step 内部调用 `getWritable()`（无需传递）：**
```typescript
import { getWritable } from "workflow";

async function streamData(chunk: string) {
  "use step";
  const writer = getWritable().getWriter();
  try {
    await writer.write(chunk);
  } finally {
    writer.releaseLock();
  }
}
```

### 命名空间流

使用 `getWritable({ namespace: 'name' })` 为不同类型的数据创建多个独立流。这对于将日志与主要输出分离、不同日志级别、代理输出、指标或任何不同数据通道非常有用。长时间运行的 workflow 受益于命名空间流，因为你只需重放重要事件（例如最终结果），而将冗长的日志保留在单独的流中。

**示例：日志级别和代理输出分离：**
```typescript
import { getWritable } from "workflow";

type LogEntry = { level: "debug" | "info" | "warn" | "error"; message: string; timestamp: number };
type AgentOutput = { type: "thought" | "action" | "result"; content: string };

async function logDebug(message: string) {
  "use step";
  const writer = getWritable<LogEntry>({ namespace: "logs:debug" }).getWriter();
  try {
    await writer.write({ level: "debug", message, timestamp: Date.now() });
  } finally {
    writer.releaseLock();
  }
}

async function logInfo(message: string) {
  "use step";
  const writer = getWritable<LogEntry>({ namespace: "logs:info" }).getWriter();
  try {
    await writer.write({ level: "info", message, timestamp: Date.now() });
  } finally {
    writer.releaseLock();
  }
}

async function emitAgentThought(thought: string) {
  "use step";
  const writer = getWritable<AgentOutput>({ namespace: "agent:thoughts" }).getWriter();
  try {
    await writer.write({ type: "thought", content: thought });
  } finally {
    writer.releaseLock();
  }
}

async function emitAgentResult(result: string) {
  "use step";
  // 重要结果发送到默认流以支持重放
  const writer = getWritable<AgentOutput>().getWriter();
  try {
    await writer.write({ type: "result", content: result });
  } finally {
    writer.releaseLock();
  }
}

export async function agentWorkflow(task: string) {
  "use workflow";
  
  await logInfo(`Starting task: ${task}`);
  await logDebug("Initializing agent context");
  await emitAgentThought("Analyzing the task requirements...");
  
  // ... agent 处理 ...
  
  await emitAgentResult("Task completed successfully");
  await logInfo("Workflow finished");
}
```

**消费命名空间流：**
```typescript
import { start, getRun } from "workflow/api";
import { agentWorkflow } from "./workflows/agent";

export async function POST(request: Request) {
  const run = await start(agentWorkflow, ["process data"]);

  // 按命名空间访问特定流
  const results = run.getReadable({ namespace: undefined }); // 默认流（重要结果）
  const infoLogs = run.getReadable({ namespace: "logs:info" });
  const debugLogs = run.getReadable({ namespace: "logs:debug" });
  const thoughts = run.getReadable({ namespace: "agent:thoughts" });

  // 仅为大多数客户端返回重要结果
  return new Response(results, { headers: { "Content-Type": "application/json" } });
}

// 从特定点恢复（适用于长会话）
export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const runId = searchParams.get("runId")!;
  const startIndex = parseInt(searchParams.get("startIndex") || "0", 10);
  
  const run = getRun(runId);
  // 仅恢复重要流，跳过冗长的调试日志
  const stream = run.getReadable({ startIndex });
  
  return new Response(stream);
}
```

对于长时间运行的会话（50 分钟以上），命名空间流有助于管理重放性能。将冗长/调试输出放在单独的命名空间中，以便只重放重要事件。

## 调试

```bash
# 检查 workflow 端点是否可达
npx workflow health
npx workflow health --port 3001  # 非默认端口

# 运行的可视化仪表板
npx workflow web
npx workflow web <run_id>

# CLI 检查（使用 --json 获取机器可读输出，--help 查看完整用法）
npx workflow inspect runs
npx workflow inspect run <run_id>

# 对于 Vercel 部署的项目，指定后端和项目
npx workflow inspect runs --backend vercel --project <project-name> --team <team-slug>
npx workflow inspect run <run_id> --backend vercel --project <project-name> --team <team-slug>

# 在浏览器中打开特定运行的 Vercel 仪表板
npx workflow inspect run <run_id> --web
npx workflow web <run_id> --backend vercel --project <project-name> --team <team-slug>

# 取消正在运行的 workflow
npx workflow cancel <run_id>
npx workflow cancel <run_id> --backend vercel --project <project-name> --team <team-slug>
# --env 默认为 "production"；使用 --env preview 用于预览部署
```

### 深链接到运行（分享 URL，无需浏览器）

使用 `--url` 来**打印**仪表板深链接并退出。不会打开浏览器，
也不会启动本地服务器。当你需要向用户提供一个
可点击的链接（PR 评论、Slack 消息、调试摘要）而非打开
UI 时，这是正确的工具。（`--web` 打开仪表板；`--url` 仅打印链接。）

```bash
# Vercel 运行：打印该运行的 Vercel 仪表板 URL
npx workflow inspect run <run_id> --backend vercel --project <project> --team <team> --url
npx workflow web <run_id> --backend vercel --project <project> --team <team> --env preview --url

# 本地运行：打印本地 web UI 深链接
npx workflow inspect run <run_id> --url

# 机器可读：--url --json 将 { "url": "..." } 打印到 stdout
npx workflow inspect run <run_id> --backend vercel --url --json
```

生成的 URL 格式：

- **Vercel：** `https://vercel.com/<team-slug>/<project-slug>/workflows/runs/<run_id>?environment=<production|preview>`
  （`--env` 选择环境；默认为 `production`。解析 team
  slug 需要通过 `vercel login` 登录并链接项目。）
- **本地：** `http://localhost:<port>?resource=run&id=<run_id>`（端口默认为
  `3456`；在 `npx workflow web` 服务器运行时链接有效）。

stdout 仅包含**只有** URL（或 JSON 对象）。所有其他输出都到
stderr，因此你可以直接捕获，例如 `URL=$(npx workflow web <run_id> --backend vercel --url)`。

**调试技巧：**
- 在任何命令上使用 `--json`（`-j`）获取机器可读输出
- 使用 `--web` 在浏览器中打开 Vercel 可观测性仪表板，或使用 `--url` 打印深链接
- 在任何命令上使用 `--help` 查看完整用法详情
- 仅导入你实际使用的 workflow API。未使用的导入可能导致 500 错误。

## 测试 workflows

Workflow SDK 提供了一个 Vitest 插件，用于在没有运行服务器的情况下在进程内测试 workflows。

**单元测试 steps：** Steps 是函数；没有编译器时，`"use step"` 无效。直接测试它们：

```typescript
import { describe, it, expect } from "vitest";
import { createUser } from "./user-signup";

describe("createUser step", () => {
  it("should create a user", async () => {
    const user = await createUser("test@example.com");
    expect(user.email).toBe("test@example.com");
  });
});
```

**集成测试：** 对于使用 `sleep()`、hooks、webhooks 或重试的 workflows，使用 `@workflow/vitest`。安装与 `workflow` 相同 npm dist-tag 的版本：Workflow 5 使用 `npm i -D @workflow/vitest@beta`，因为 `@workflow/vitest@latest` 仍然是 4.x 系列。当插件的 `@workflow/core` 主版本与应用程序不同时，插件会失败运行。

```typescript
// vitest.integration.config.ts
import { defineConfig } from "vitest/config";
import { workflow } from "@workflow/vitest";

export default defineConfig({
  plugins: [workflow()],
  test: {
    include: ["**/*.integration.test.ts"],
    testTimeout: 60_000,
  },
});
```

```typescript
// approval.integration.test.ts
import { describe, it, expect } from "vitest";
import { start, getRun, resumeHook } from "workflow/api";
import { waitForHook, waitForSleep } from "@workflow/vitest";
import { approvalWorkflow } from "./approval";

describe("approvalWorkflow", () => {
  it("should publish when approved", async () => {
    const run = await start(approvalWorkflow, ["doc-123"]);

    // 等待 hook，然后恢复它
    await waitForHook(run, { token: "approval:doc-123" });
    await resumeHook("approval:doc-123", { approved: true, reviewer: "alice" });

    // 等待 sleep，然后唤醒它
    const sleepId = await waitForSleep(run);
    await getRun(run.runId).wakeUp({ correlationIds: [sleepId] });

    const result = await run.returnValue;
    expect(result).toEqual({ status: "published", reviewer: "alice" });
  });
});
```

**测试 webhooks：** 使用带有 `Request` 对象的 `resumeWebhook()`。无需 HTTP 服务器：

```typescript
import { start, resumeWebhook } from "workflow/api";
import { waitForHook } from "@workflow/vitest";

const run = await start(ingestWorkflow, ["ep-1"]);
const hook = await waitForHook(run);  // 发现随机 webhook 令牌
await resumeWebhook(hook.token, new Request("https://example.com/webhook", {
  method: "POST",
  body: JSON.stringify({ event: "order.created" }),
}));
```

**关键 API：**
- `start()`：触发 workflow
- `run.returnValue`：等待 workflow 完成
- `waitForHook(run, { token? })` / `waitForSleep(run)`：等待 workflow 到达暂停点
- `resumeHook(token, data)` / `resumeWebhook(token, request)`：恢复已暂停的 workflows
- `getRun(runId).wakeUp({ correlationIds })`：跳过 `sleep()` 调用
- `getWorkflowRef(name)` / `listWorkflowRefs()`：当测试无法导入函数时，在测试构建的清单中查找 workflow（永远不要手写 `workflow//...` id）

**最佳实践：**
- 将单元测试（无插件）和集成测试（`workflow()` 插件）放在不同的配置中
- 安装与 `workflow` 相同 dist-tag 的 `@workflow/vitest`，并一起升级
- 使用基于测试数据的确定性 hook 令牌以便更容易恢复
- 设置较大的 `testTimeout` 值，因为 workflows 可能比典型单元测试运行更长时间
- `vi.mock()` 永远无法到达 workflow 体（它们在 VM 中运行），且仅在生成的包通过 Vitest 模块运行器加载时才能到达 step 代码；项目本地模块被打包到 step 包中，因此应 mock npm 叶节点、注入依赖或对 step 进行单元测试

## 可观测性与 World SDK

使用 `await getWorld()` 构建可观测性仪表板、管理面板并检查 workflow 状态。`getWorld()` 是异步的，返回 `Promise<World>`（动态导入/基于环境设置）。

**关键导入：**
```typescript
import { getWorld } from "workflow/runtime";
import { hydrateResourceIO, observabilityRevivers, parseStepName, parseWorkflowName } from "workflow/observability";
```

**关键文档**（在 `node_modules/workflow/docs/` 中 grep 获取完整详情）：
- `api-reference/workflow-runtime/world/storage.mdx`：事件、运行、steps 和 hooks（事件是事实来源；其他是物化视图）
- `api-reference/workflow-observability/`：水合与名称解析

### World SDK 方法签名

⚠️ 分页是嵌套的：`{ pagination: { cursor } }`，而不是直接 `{ cursor }`。

```typescript
const world = await getWorld();

// Runs
const { data, cursor } = await world.runs.list({ pagination: { cursor }, resolveData: 'all' | 'none' });
const run = await world.runs.get(runId, { resolveData: 'all' | 'none' });
// 通过事件创建来取消（runs 上没有 cancel() 方法）
await world.events.create(runId, { eventType: 'run_cancelled' });

// Steps: runId 是顶层的，不在 pagination 内部
const { data, cursor } = await world.steps.list({ runId, pagination: { cursor }, resolveData: 'all' | 'none' });
const step = await world.steps.get(runId, stepId, { resolveData: 'all' | 'none' });

// Events
const { data, cursor } = await world.events.list({ runId, pagination: { cursor } });
await world.events.create(runId, { eventType: 'run_cancelled' });

// Hooks
const hook = await world.hooks.get(hookId);
const hook = await world.hooks.getByToken(token);

// Streams（world.streams 上的方法）
await world.streams.write(runId, name, chunk);
await world.streams.writeMulti?.(runId, name, chunks);
const readable = await world.streams.get(runId, name, startIndex);
await world.streams.close(runId, name);
const streamNames = await world.streams.list(runId);
const chunks = await world.streams.getChunks(runId, name, { limit, cursor });
const info = await world.streams.getInfo(runId, name);

// Queue（方法直接位于 world 上，作为内部 SDK 基础设施）
await world.queue(queueName, payload, opts);
const deploymentId = await world.getDeploymentId();
```

### `resolveData` 参数

控制响应中是否**包含**输入/输出数据。接受 `'all'`（默认）或 `'none'`。

**重要**：即使使用 `'all'`，数据仍然是 devalue 序列化的。你必须调用 `hydrateResourceIO()` 才能获取可用的 JS 值。

- **使用 `'none'`** 进行状态轮询、进度仪表板、运行列表
- **使用 `'all'`**（或省略）当你需要检查实际 step I/O 数据时，然后**始终进行水合**

```typescript
// 轻量级状态检查，不加载 I/O
const run = await world.runs.get(runId, { resolveData: 'none' });
console.log(run.status); // 'running' | 'completed' | 'failed' | 'cancelled'

// 完整检查：resolveData 包含数据，hydrateResourceIO 反序列化它
const step = await world.steps.get(runId, stepId); // 默认为 'all'
const hydrated = hydrateResourceIO(step, observabilityRevivers);
```

> **常见错误**：在 `resolveData: 'all'` 后检查 `step.input !== undefined` 并假设
> 数据已准备好使用。数据确实存在但已被序列化，因此始终先进行水合。

### 数据水合（devalue 格式）

Step I/O 通过 [devalue](https://github.com/Rich-Harris/devalue) 序列化，带有 4 字节格式前缀（`devl`）。未经水合，`input`/`output` 是带有数字键的 Uint8Array 样对象：
`{"0":100,"1":101,"2":118,"3":108,...}` 包含未经水合不可用的值。

**使用 I/O 数据前始终进行水合：**

```typescript
import { hydrateResourceIO, observabilityRevivers } from "workflow/observability";

const { data: steps } = await world.steps.list({ runId, resolveData: 'all' });
const hydrated = steps.map(s => hydrateResourceIO(s, observabilityRevivers));
// hydrated[0].input → [123, 2]（实际函数参数）
// hydrated[0].output → 125（实际返回值）
```

`hydrateResourceIO` 适用于 `Step` 和 `WorkflowRun` 对象。对于加密的 workflows，使用 `getEncryptionKeyForRun()` + `hydrateResourceIOWithKey()`。

### 名称解析

`parseWorkflowName()`、`parseStepName()` 和 `parseClassName()` 返回 `{ shortName: string, moduleSpecifier: string } | null`。始终使用可选链：

```typescript
const parsed = parseWorkflowName("workflow//./src/workflows/order//processOrder");
// parsed?.shortName → "processOrder"
// parsed?.moduleSpecifier → "./src/workflows/order"
// ⚠️ 格式不匹配时返回 null
```

### 事件类型

事件是仅追加的事实来源。Runs/Steps/Hooks 是物化视图。

| 类别 | 类型 |
|----------|-------|
| Run | `run_created`、`run_started`、`run_completed`、`run_failed`、`run_cancelled` |
| Step | `step_created`、`step_started`、`step_completed`、`step_failed`、`step_retrying` |
| Hook | `hook_created`、`hook_received`、`hook_disposed`、`hook_conflict` |
| Wait | `wait_created`、`wait_completed` |

## 错误处理模式

针对不同故障模式的三种错误策略：

| 错误类型 | 使用场景 | 行为 |
|------------|----------|----------|
| `FatalError` | 永久性故障（无效输入、认证被拒绝） | 立即终止 workflow，不重试 |
| `RetryableError` | 瞬时性故障（速率限制、超时） | 带可选 `retryAfter` 延迟重试 |
| `Promise.allSettled` | 具有混合关键性的并行 steps | 即使某些 step 失败也继续 |

```typescript
import { FatalError, RetryableError } from "workflow";

// 永久性故障，workflow 终止
throw new FatalError("Invalid input: missing required field");

// 瞬时性故障，将重试
throw new RetryableError("API rate limited", { retryAfter: "5m" });

// 混合关键性并行执行
const results = await Promise.allSettled([
  criticalStep(data),    // 必须成功
  optionalStep(data),    // 允许失败
  enrichmentStep(data),  // 允许失败
]);
const [critical, optional, enrichment] = results;
if (critical.status === "rejected") throw new FatalError(critical.reason);
```
