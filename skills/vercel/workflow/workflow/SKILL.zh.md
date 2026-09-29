---
name: workflow
description: 使用 Vercel 的 Workflow SDK 创建持久化、可恢复的工作流。适用于构建需要经历重启、等待外部事件、失败重试或跨时间协调多步操作的工作流。触发条件包括提及“工作流”、“持久化函数”、“可恢复”、“工作流 SDK”、“队列”、“事件”、“推送”、“订阅”或基于步骤的编排。
---

## *严重警告*：始终使用正确的 `workflow` 文档

你对 `workflow` 的了解已经过时。

下面列出的 `workflow` 文档与已安装的 Workflow SDK 版本一致。
在开始任何与 `workflow` 相关的任务之前，请遵循以下说明：

在 `node_modules/workflow/docs/` 中搜索捆绑的文档：

1. **查找文档**：`glob "node_modules/workflow/docs/**/*.mdx"`
2. **搜索内容**：`grep "你的查询" node_modules/workflow/docs/`

`node_modules/workflow/docs/` 中的文档结构：

- `getting-started/` - 框架设置 (next.mdx, express.mdx, hono.mdx 等)
- `foundations/` - 核心概念 (workflows-and-steps.mdx, hooks.mdx, streaming.mdx 等)
- `api-reference/workflow/` - API 文档 (sleep.mdx, create-hook.mdx, fatal-error.mdx 等)
- `api-reference/workflow-api/` - 客户端 API (start.mdx, get-run.mdx, resume-hook.mdx 等)
- `api-reference/workflow-runtime/` - 运行时 API (get-world.mdx) 和 `world/` World SDK (storage.mdx, streams.mdx, queue.mdx)
- `api-reference/workflow-observability/` - Hydration 和名称解析工具 (hydrate-resource-io.mdx, parse-workflow-name.mdx 等)
- `ai/`：AI SDK 集成文档
- `errors/` - 错误代码文档
- `worlds/` - 每个世界的特定行为和限制 (vercel.mdx, local.mdx, postgres.mdx)。其他页面会链接这些页面为 `/worlds/<name>`。

相关包也包含捆绑的文档：

- `@ai-sdk/workflow`：`node_modules/ai/docs/` - WorkflowAgent 和 AI SDK 集成
- `@workflow/ai`：`node_modules/@workflow/ai/docs/` - 用于现有应用的已弃用的 DurableAgent API
- `@workflow/core`：`node_modules/@workflow/core/docs/` - 核心运行时 (foundations, how-it-works)
- `@workflow/next`：`node_modules/@workflow/next/docs/` - Next.js 集成

**如有疑问，请更新到最新版本的 Workflow SDK。**

### 官方资源

- **网站**：https://workflow-sdk.dev
- **GitHub**：https://github.com/vercel/workflow

### 快速参考

**指令：**

```typescript
"use workflow";  // 第一行 - 使异步函数持久化
"use step";      // 第一行 - 使函数成为可缓存的、可重试的单元
```

**必要的导入：**

```typescript
// Workflow 基本类型
import { sleep, fetch, createHook, createWebhook, getWritable } from "workflow";
import { FatalError, RetryableError } from "workflow";
import { getWorkflowMetadata, getStepMetadata } from "workflow";

// API 操作
import { start, getRun, resumeHook, resumeWebhook } from "workflow/api";

// 可观察性 & 数据hydration
import { hydrateResourceIO, observabilityRevivers, parseStepName, parseWorkflowName } from "workflow/observability";

// 框架集成
import { withWorkflow } from "workflow/next";
import { workflow } from "workflow/vite";
import { workflow } from "workflow/astro";
// 或者使用模块：["workflow/nitro"] 用于 Nitro/Nuxt

// AI agent (Workflow 5)
import { WorkflowAgent, type ModelCallStreamPart } from "@ai-sdk/workflow";
```

## 优先使用步骤函数以避免沙盒错误

`"use workflow"` 函数在沙盒化的虚拟机中运行。`"use step"` 函数具有 **完整的 Node.js 访问权限**。将逻辑放在步骤中，并使用 workflow 函数纯粹用于编排。

```typescript
// 步骤具有完整的 Node.js 和 npm 访问权限
async function fetchUserData(userId: string) {
  "use step";
  const response = await fetch(`https://api.example.com/users/${userId}`);
  return response.json();
}

async function processWithAI(data: any) {
  "use step";
  // AI SDK 在步骤中工作，无需workarounds
  return await generateText({
    model: "spacexai/grok-4.6",
    prompt: `处理：${JSON.stringify(data)}`,
  });
}

// Workflow 编排步骤 - 无沙盒问题
export async function dataProcessingWorkflow(userId: string) {
  "use workflow";
  const data = await fetchUserData(userId);
  const processed = await processWithAI(data);
  return { success: true, processed };
}
```

**优点**：步骤具有自动重试，结果可用于重放，并且没有沙盒限制。

## Workflow 沙盒限制

当您需要在 workflow 函数中直接编写逻辑（而不是在步骤中）时，这些限制适用：

| 限制 | 解决方案 |
|------------|------------|
| 没有 `fetch()` | `import { fetch } from "workflow"` 然后设置 `globalThis.fetch = fetch` |
| 没有 `setTimeout`/`setInterval` | 使用 `"workflow"` 中的 `sleep("5s")` |
| 没有 Node.js 模块 (fs, crypto 等) | 转移到步骤函数 |

**示例 - 在 workflow 上下文中使用 fetch：**

```typescript
import { fetch } from "workflow";

export async function myWorkflow() {
  "use workflow";
  globalThis.fetch = fetch;  // 对于 AI SDK 和 HTTP 库是必需的
  // 现在可以生成文本()和其他库工作
}
```

**注意**：纯 `"provider/model"` 字符串使用 Vercel AI Gateway。除非用户明确需要仅 provider 功能，否则不要构造直接 provider 实例。

## WorkflowAgent：Workflow 5 中的 AI agent

使用 AI SDK 的 `WorkflowAgent` 用于 Workflow 5 上的持久化 agent。它取代了来自 `@workflow/ai` 的已弃用的 `DurableAgent` API，并检查模型调用和步骤回退工具。

```typescript
import { WorkflowAgent, type ModelCallStreamPart } from "@ai-sdk/workflow";
import { isStepCount, tool } from "ai";
import { getWritable } from "workflow";
import { z } from "zod";

async function lookupData({ query }: { query: string }) {
  "use step";
  // 步骤函数具有完整的 Node.js 访问权限
  return `查询 "${query}" 的结果`;
}

export async function myAgentWorkflow(userMessage: string) {
  "use workflow";

  const agent = new WorkflowAgent({
    model: "spacexai/grok-4.6",
    instructions: "你是一个有帮助的助手。",
    tools: {
      lookupData: tool({
        description: "搜索信息",
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
- 纯 `"provider/model"` 字符串通过 Vercel AI Gateway 路由；`spacexai/grok-4.6` 是 Workflow 示例中的默认模型
- `getWritable<ModelCallStreamPart>()` 流式传输持久化的模型调用输出；在 HTTP 路由中使用 `createModelCallToUIChunkTransform()` 转换它
- 需要Node.js/npm访问的工具 `execute` 函数应使用 `"use step"`
- 使用 workflow 基本类型 (`sleep()`, `createHook()`) 的工具 `execute` 函数应 **不** 使用 `"use step"`，因为它们在 workflow 级别运行
- `stopWhen` 限制模型调用次数；默认情况下，当模型停止调用工具时停止
- 多轮对话：将 `result.messages` 和新的用户消息传递给后续的 `agent.stream()` 调用

**更多详情，请查看已安装 AI SDK 包中的 WorkflowAgent 文档或在 https://ai-sdk.dev/v7/docs/agents/workflow-agent 上查看。**

## 启动 workflows & 子 workflows

从 API 路由中启动 workflows 使用 `start()`。在 Workflow 5 中，`start()` 也可以直接从 workflow 函数调用以生成子运行；它会被回退，并在父事件日志中记录一个确定性边界。

```typescript
import { start } from "workflow/api";

// 从 API 路由；直接工作
export async function POST() {
  const run = await start(myWorkflow, [arg1, arg2]);
  return Response.json({ runId: run.runId });
}

// 无参数的 workflow
const run = await start(noArgWorkflow);
```

**在 Workflow 5 workflow 内部启动子 workflows：**

```typescript
import { start } from "workflow/api";

export async function parentWorkflow() {
  "use workflow";
  const childRun = await start(childWorkflow, ["一些数据"]);
  await sleep("1h");
  return { childRunId: childRun.runId };
}
```

`start()` 在创建子运行后返回，并且不会等待它完成。仅在父级应等待子级时使用 `childRun.returnValue`；在 workflow 内部的每个 `Run` 属性访问或方法调用都是一个步骤。

## 运行大小 & 并发：知道何时拆分

有三个需要调整大小的事项，并且这三个都有上限。**不要**将您记住的任何数字视为权威——当前值在 [Workflow 运行限制](https://vercel.com/docs/workflows/pricing#workflow-run-limits) 下发布，这是唯一可以引用的来源。

**每个运行的事件数。** 运行的事件日志是有限制的，超过上限后运行会失败并显示 `MAX_EVENTS_EXCEEDED`。事件不是步骤：一个在第一次尝试成功时记录三个 (`step_created`, `step_started`, `step_completed`) 的步骤，重试会记录一个或两个更多，而钩子、sleep 和 webhook 各自记录自己的。在达到上限之前拆分为子 workflows——定价页面建议在 **几千个事件** 之后，因为重放在运行失败之前就已经变慢了。

**每个运行的步骤数。** 与事件分开限制，因此即使它保持狭窄，长链也是有限的。当链会达到五位数时，将多个项目捆绑成一个步骤。

**并发。** 宽扇出会被限制而不是拒绝：事件创建是按每秒每个运行限制的，因此几个千项的扁平 `Promise.all` 会花费大量时间退避。批量处理或捆绑处理——将列表分块处理，或每步处理多个项目，这样并发运行的单元较少且较大。为每个项目生成一个子运行本身并不能缩小扇出；它仅限制每个子运行的事件日志并隔离故障，这些原因值得这样做，但它不是分块处理的替代方案。

您无法自行提高任何这些限制——`WORKFLOW_MAX_EVENTS_OVERRIDE` 只会向下钳制，并且在 Vercel World 上上限是服务拥有的——但 Vercel 会根据请求提高每个运行的事件和步骤限制，因此一个真正大的运行既是支持问题也是设计问题。

```typescript
const BATCH = 100;

async function processItem(item: string) {
  "use step";
  return item.toUpperCase();
}

// 每个项目一个步骤，所有项目同时运行，所有项目在一个日志中
export async function processAll(items: string[]) {
  "use workflow";
  await Promise.all(items.map((item) => processItem(item)));
}

// 分块处理，因此一次只有一个 BATCH 步骤在运行
export async function processBatched(items: string[]) {
  "use workflow";
  for (let i = 0; i < items.length; i += BATCH) {
    await Promise.allSettled(items.slice(i, i + BATCH).map((item) => processItem(item)));
  }
}

// 捆绑处理，因此一个步骤涵盖多个项目，日志保持短小
async function processChunk(chunk: string[]) {
  "use step";
  return chunk.map((item) => item.toUpperCase());
}

export async function processBundled(items: string[]) {
  "use workflow";
  for (let i = 0; i < items.length; i += BATCH) {
    await processChunk(items.slice(i, i + BATCH));
  }
}
```

`processAll` 是需要避免的大规模形状。`processBatched` 限制并发，但仍然为每个项目记录事件。`processBundled` 限制两者，因为一个步骤涵盖 `BATCH` 个项目——这是三个中唯一一个随着 `BATCH` 增长而事件计数减少的。

## Hooks：使用外部事件暂停和恢复

Hooks 允许 workflows 等待外部数据。在 workflow 内部使用 `createHook()`，从 API 路由使用 `resumeHook()`。确定性令牌仅用于 `createHook()` + `resumeHook()`（服务器端）的组合。`createWebhook()` 总是生成随机令牌，因此不要向 `createWebhook()` 传递 `token` 选项。

### 单个事件

```typescript
import { createHook } from "workflow";

export async function approvalWorkflow() {
  "use workflow";

  const hook = createHook<{ approved: boolean }>({
    token: "approval-123",  // 用于外部系统的确定性令牌
  });

  const result = await hook;  // Workflow 在此处挂起
  return result.approved;
}
```

### 多个事件（可迭代 hooks）

Hooks 实现 `AsyncIterable`。使用 `for await...of` 接收多个事件：

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

每次 `resumeHook(token, payload)` 调用都会将下一个值传递给循环。

### 从 API 路由中恢复

```typescript
import { resumeHook } from "workflow/api";

export async function POST(req: Request) {
  const { token, data } = await req.json();
  await resumeHook(token, data);
  return new Response("ok");
}
```

## 错误处理

使用 `FatalError` 处理永久性故障（不可重试），使用 `RetryableError` 处理暂时性故障：

```typescript
import { FatalError, RetryableError } from "workflow";

if (res.status === 429) {
  throw new RetryableError("速率限制", { retryAfter: "5m" });
}
if (res.status >= 400 && res.status < 500) {
  throw new FatalError(`客户端错误：${res.status}`);
}
```

## 序列化

传递给/从 workflows 和 steps 的所有数据都必须可序列化。

**支持的内置类型**：字符串、数字、布尔值、null、undefined、BigInt、普通对象、数组、Date、RegExp、URL、URLSearchParams、Map、Set、Headers、ArrayBuffer、类型数组、Request、Response、ReadableStream、WritableStream。

**不支持**：函数、Symbol、WeakMap/WeakSet。传递数据，而不是回调。

### 自定义类序列化

类实例**可以**通过实现 `@workflow/serde` 协议跨 workflow/step 边界序列化。当类具有 `"use step"` 的实例方法时，或者您希望在步骤之间传递类实例时，这是必要的。

**安装**：`@workflow/serde` 必须是包含类的包的依赖项。

**模式**：在类体内使用计算属性语法添加两个静态方法：

```typescript
import { WORKFLOW_SERIALIZE, WORKFLOW_DESERIALIZE } from "@workflow/serde";

export class Point {
  x: number;
  y: number;

  constructor(x: number, y: number) {
    this.x = x;
    this.y = y;
  }

  // 序列化：返回普通数据（必须是 devalue 兼容类型）
  static [WORKFLOW_SERIALIZE](instance: Point) {
    return { x: instance.x, y: instance.y };
  }

  // 反序列化：从普通数据重建
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
1. **在类体内定义 serde 方法** 作为静态方法，使用计算属性语法 (`static [WORKFLOW_SERIALIZE](...)`)。SWC 插件通过扫描类来检测它们。**不要**将它们外部分配（例如，`(MyClass as any)[WORKFLOW_SERIALIZE] = ...`）——编译器将无法检测到这一点。
2. **Serde 方法必须只返回 devalue 兼容类型**（普通对象、数组、原始值、Date、Map、Set、Uint8Array 等）。没有函数，没有类实例，没有 Node.js 特定对象。
3. **将 `"use step"` 添加到依赖 Node.js 的实例方法。** SWC 插件会从 workflow 包中删除 `"use step"` 方法的主体。这是如何将 Node.js 导入（fs、crypto、child_process 等）保持在 workflow 沙盒之外的方法。带有其 serde 方法的类外壳仍然在 workflow 包中；只有步骤方法主体被删除。
4. **不要手动注册类。** SWC 插件会自动生成注册代码（一个 IIFE，它设置 `classId` 并将类添加到全局注册表）。手动调用 `registerSerializationClass()` 是不必要的且容易出错。
5. **不要使用动态导入来绕过沙盒限制。** 如果类方法需要 Node.js API，正确的解决方案是 `"use step"`，而不是 `/* @vite-ignore */ import(...)`。

**当 serde 工作良好时**：纯数据类、领域模型、配置对象和类，其中 Node.js 依赖的方法可以标记为 `"use step"`。

**何时避免使用 serde：** 如果一个类本质上与 Node.js API 紧密相关（每个方法都需要 `fs`、`net` 等），并且无法在流程沙盒中作为外壳存在，则将其完全保留在步骤函数中，并在边界处传递纯数据对象。

### 验证 serde 合规性

使用这些工具来验证类是否正确设置：

- **`workflow transform <file> --check-serde`** -- 显示文件的 SWC 转换输出，并检查 serde 类是否符合规范（工作流包中不再有 Node.js 导入）。
- **`workflow validate`** -- 扫描所有工作流文件并报告 serde 合规性问题。使用 `--json` 获取机器可读输出。
- **SWC Playground** -- 位于 `workbench/swc-playground` 的网络游乐场在检测到 serde 模式时会显示 Serde 分析面板。
- **构建时警告** -- 构建器在 serde 类在工作流包中仍有 Node.js 内置导入时自动发出警告。

## 流式传输

使用 `getWritable()` 从工作流中流式传输数据。`getWritable()` 可以在 **工作流** 和 **步骤** 上下文中调用，但您 **不能** 直接在工作流函数中 **与流交互**（调用 `getWriter()`、`write()`、`close()`）。流必须传递给步骤函数以进行实际 I/O，或者步骤可以自己调用 `getWritable()`。

**在工作流中获取流，传递给步骤：**
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

**直接在步骤中调用 `getWritable()`（无需传递）：**
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

使用 `getWritable({ namespace: 'name' })` 为不同类型的数据创建多个独立的流。这对于分离日志与主要输出、不同日志级别、代理输出、指标或任何其他独立数据通道非常有用。长时间运行的工作流受益于命名空间流，因为您可以仅重播重要事件（例如，最终结果），同时将冗长的日志保留在单独的流中。

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
  // 重要结果发送到默认流以供重播
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
  
  // ... 代理处理 ...
  
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

  // 通过命名空间访问特定流
  const results = run.getReadable({ namespace: undefined }); // 默认流（重要结果）
  const infoLogs = run.getReadable({ namespace: "logs:info" });
  const debugLogs = run.getReadable({ namespace: "logs:debug" });
  const thoughts = run.getReadable({ namespace: "agent:thoughts" });

  // 对大多数客户端仅返回重要结果
  return new Response(results, { headers: { "Content-Type": "application/json" } });
}

// 从特定点恢复（适用于长时间会话）
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

对于长时间运行会话（50 分钟以上），命名空间流有助于管理重播性能。将冗长/调试输出放在单独的命名空间中，以便您仅重播重要事件。

## 调试

```bash
# 检查工作流端点是否可达
npx workflow health
npx workflow health --port 3001  # 非默认端口

# 运行可视化面板
npx workflow web
npx workflow web <run_id>

# CLI 检查（使用 --json 获取机器可读输出，--help 获取完整用法）
npx workflow inspect runs
npx workflow inspect run <run_id>

# 对于 Vercel 部署的项目，指定后端和项目
npx workflow inspect runs --backend vercel --project <project-name> --team <team-slug>
npx workflow inspect run <run_id> --backend vercel --project <project-name> --team <team-slug>

# 在浏览器中打开 Vercel 可观测性面板以查看特定运行
npx workflow inspect run <run_id> --web
npx workflow web <run_id> --backend vercel --project <project-name> --team <team-slug>

# 取消正在运行的工作流
npx workflow cancel <run_id>
npx workflow cancel <run_id> --backend vercel --project <project-name> --team <team-slug>
# --env 默认为 "production"；使用 --env preview 进行预览部署
```

### 深链接到运行（无需浏览器）

使用 `--url` **打印** 面板深链接并退出。不会打开浏览器，也不会启动本地服务器。当您需要将可点击链接（例如 PR 评论、Slack 消息、调试摘要）交给用户而不是打开 UI 时，这是正确的工具。(`--web` 打开面板；`--url` 仅打印链接。）

```bash
# Vercel 运行：打印 Vercel 面板的运行 URL
npx workflow inspect run <run_id> --backend vercel --project <project> --team <team> --url
npx workflow web <run_id> --backend vercel --project <project> --team <team> --env preview --url

# 本地运行：打印本地 Web UI 深链接
npx workflow inspect run <run_id> --url

# 机器可读：--url --json 打印 { "url": "..." } 到 stdout
npx workflow inspect run <run_id> --backend vercel --url --json
```

生成的 URL 格式：

- **Vercel:** `https://vercel.com/<team-slug>/<project-slug>/workflows/runs/<run_id>?environment=<production|preview>`
  (`--env` 选择环境；默认为 `production`。解析团队缩写需要通过 `vercel login` 使用链接的项目登录。)
- **本地:** `http://localhost:<port>?resource=run&id=<run_id>`（端口默认为 `3456`；`npx workflow web` 服务器运行时链接有效。）

stdout **仅**包含 URL（或 JSON 对象）。所有其他输出都发送到 stderr，因此您可以直接捕获它，例如，`URL=$(npx workflow web <run_id> --backend vercel --url)`。

**调试技巧：**
- 在任何命令上使用 `--json` (`-j`) 获取机器可读输出
- 使用 `--web` 在浏览器中打开 Vercel 可观测性面板或 `--url` 打印深链接
- 在任何命令上使用 `--help` 获取完整用法详情
- 仅导入您实际使用的工作流 API。未使用的导入可能导致 500 错误。

## 测试工作流

工作流 SDK 提供了一个 Vitest 插件，用于在不运行服务器的情况下在进程中测试工作流。

**单元测试步骤：** 步骤是函数；没有编译器，`"use step"` 是一个空操作。直接测试它们：

```typescript
import { describe, it, expect } from "vitest";
import { createUser } from "./user-signup";

describe("createUser 步骤", () => {
  it("应该创建用户", async () => {
    const user = await createUser("test@example.com");
    expect(user.email).toBe("test@example.com");
  });
});
```

**集成测试：** 使用 `@workflow/vitest` 测试使用 `sleep()`、钩子、Webhook 或重试的工作流。在 `workflow` 相同的 npm dist-tag 上安装它：`npm i -D @workflow/vitest@beta` 用于 Workflow 5，因为 `@workflow/vitest@latest` 仍然是 4.x 线。插件在其 `@workflow/core` 主版本与应用程序不同时失败。

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
  it("批准时应该发布", async () => {
    const run = await start(approvalWorkflow, ["doc-123"]);

    // 等待钩子，然后恢复它
    await waitForHook(run, { token: "approval:doc-123" });
    await resumeHook("approval:doc-123", { approved: true, reviewer: "alice" });

    // 等待睡眠，然后唤醒它
    const sleepId = await waitForSleep(run);
    await getRun(run.runId).wakeUp({ correlationIds: [sleepId] });

    const result = await run.returnValue;
    expect(result).toEqual({ status: "published", reviewer: "alice" });
  });
});
```

**测试 Webhook：** 使用 `resumeWebhook()` 和 `Request` 对象。不需要 HTTP 服务器：

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
- `start()`: 触发工作流
- `run.returnValue`: 等待工作流完成
- `waitForHook(run, { token? })` / `waitForSleep(run)`: 等待工作流到达暂停点
- `resumeHook(token, data)` / `resumeWebhook(token, request)`: 恢复暂停的工作流
- `getRun(runId).wakeUp({ correlationIds })`: 跳过 `sleep()` 调用
- `getWorkflowRef(name)` / `listWorkflowRefs()`: 在测试构建的清单中查找工作流，当测试无法导入函数时（永远不会手动编写 `workflow//...` ID）

**最佳实践：**
- 将单元测试（无插件）和集成测试（`workflow()` 插件）保持在不同的配置中
- 在与 `workflow` 相同的 dist-tag 上安装 `@workflow/vitest` 并一起升级它们
- 使用基于测试数据的确定性钩子令牌以便更容易恢复
- 设置充足的 `testTimeout` 值，因为工作流可能比典型单元测试运行时间更长
- `vi.mock()` 从不到达工作流体（它们在虚拟机中运行），并且仅在通过 Vitest 的模块运行器加载生成的包时到达步骤代码；项目本地模块被捆绑到步骤包中，因此模拟 npm 叶子包、注入依赖项或单元测试步骤

## 可观测性 & World SDK

使用 `await getWorld()` 构建可观测性面板、管理面板和检查工作流状态。`getWorld()` 是异步的，返回 `Promise<World>`（动态导入/基于环境的设置）。

**关键导入：**
```typescript
import { getWorld } from "workflow/runtime";
import { hydrateResourceIO, observabilityRevivers, parseStepName, parseWorkflowName } from "workflow/observability";
```

**关键文档**（在 `node_modules/workflow/docs/` 中使用 grep 获取完整详情）：
- `api-reference/workflow-runtime/world/storage.mdx`：事件、运行、步骤和钩子（事件是事实来源；其他是物化视图）
- `api-reference/workflow-observability/`：水合和名称解析

### World SDK 方法签名

⚠️ 分页是嵌套的：`{ pagination: { cursor } }`，**不是** `{ cursor }` 直接。

```typescript
const world = await getWorld();

// 运行
const { data, cursor } = await world.runs.list({ pagination: { cursor }, resolveData: 'all' | 'none' });
const run = await world.runs.get(runId, { resolveData: 'all' | 'none' });
// 通过事件创建取消（运行上没有 cancel() 方法）
await world.events.create(runId, { eventType: 'run_cancelled' });

// 步骤：runId 是顶层，**不是**在分页内
const { data, cursor } = await world.steps.list({ runId, pagination: { cursor }, resolveData: 'all' | 'none' });
const step = await world.steps.get(runId, stepId, { resolveData: 'all' | 'none' });

// 事件
const { data, cursor } = await world.events.list({ runId, pagination: { cursor } });
await world.events.create(runId, { eventType: 'run_cancelled' });

// 钩子
const hook = await world.hooks.get(hookId);
const hook = await world.hooks.getByToken(token);

// 流（world.streams 上的方法）
await world.streams.write(runId, name, chunk);
await world.streams.writeMulti?.(runId, name, chunks);
const readable = await world.streams.get(runId, name, startIndex);
await world.streams.close(runId, name);
const streamNames = await world.streams.list(runId);
const chunks = await world.streams.getChunks(runId, name, { limit, cursor });
const info = await world.streams.getInfo(runId, name);

// 队列（方法直接在 world 上作为内部 SDK 基础设施）
await world.queue(queueName, payload, opts);
const deploymentId = await world.getDeploymentId();
```

### `resolveData` 参数

控制输入/输出数据是否**包含**在响应中。接受 `'all'`（默认）或 `'none'`。

**重要提示**：即使使用 `'all'`，数据仍然是 devalue-序列化的。您**必须**调用 `hydrateResourceIO()` 才能获取可用的 JS 值。

- **使用 `'none'`** 进行状态轮询、进度面板、运行列表
- **使用 `'all'`**（或省略）当您需要检查实际的步骤 I/O 数据时，然后**始终水合**

```typescript
// 轻量级状态检查，不加载 I/O
const run = await world.runs.get(runId, { resolveData: 'none' });
console.log(run.status); // 'running' | 'completed' | 'failed' | 'cancelled'

// 完整检查：resolveData 包含数据，hydrateResourceIO 反序列化它
const step = await world.steps.get(runId, stepId); // 默认为 'all'
const hydrated = hydrateResourceIO(step, observabilityRevivers);
```

> **常见错误**：在 `resolveData: 'all'` 后检查 `step.input !== undefined` 并假设数据已准备好使用。数据存在但已序列化，因此始终先水合。

### 数据水合（devalue 格式）

步骤 I/O 通过 [devalue](https://github.com/Rich-Harris/devalue) 序列化，带有 4 字节格式前缀（`devl`）。如果没有水合，`input`/`output` 是类似 Uint8Array 的对象，具有数字键：
`{"0":100,"1":101,"2":118,"3":108,...}` 包含的值在未水合时**不可用**。

**使用 I/O 数据前始终水合：**

```typescript
import { hydrateResourceIO, observabilityRevivers } from "workflow/observability";

const { data: steps } = await world.steps.list({ runId, resolveData: 'all' });
const hydrated = steps.map(s => hydrateResourceIO(s, observabilityRevivers));
// hydrated[0].input → [123, 2] (实际函数参数)
// hydrated[0].output → 125 (实际返回值)
```

`hydrateResourceIO` 适用于 `Step` 和 `WorkflowRun` 对象。对于加密的工作流，使用 `getEncryptionKeyForRun()` + `hydrateResourceIOWithKey()`。

### 名称解析

`parseWorkflowName()`、`parseStepName()` 和 `parseClassName()` 返回 `{ shortName: string, moduleSpecifier: string } | null`。始终使用可选链：

```typescript
const parsed = parseWorkflowName("workflow//./src/workflows/order//processOrder");
// parsed?.shortName → "processOrder"
// parsed?.moduleSpecifier → "./src/workflows/order"
// ⚠️ 如果格式不匹配，则返回 null
```

### 事件类型

事件是不可变的真实来源。运行/步骤/钩子是物化视图。

| 类别 | 类型 |
|------|------|
| 运行 | `run_created`, `run_started`, `run_completed`, `run_failed`, `run_cancelled` |
| 步骤 | `step_created`, `step_started`, `step_completed`, `step_failed`, `step_retrying` |
| 钩子 | `hook_created`, `hook_received`, `hook_disposed`, `hook_conflict` |
| 等待 | `wait_created`, `wait_completed` |

## 错误处理模式

针对不同失败模式的三个错误策略：

| 错误类型 | 使用场景 | 行为 |
|---------|---------|------|
| `FatalError` | 永久性失败（输入错误、认证拒绝） | 立即终止工作流，不重试 |
| `RetryableError` | 暂时性失败（速率限制、超时） | 带可选 `retryAfter` 延迟重试 |
| `Promise.allSettled` | 兼具关键性的并行步骤 | 即使某些步骤失败，也会继续 |

```typescript
import { FatalError, RetryableError } from "workflow";

// 永久性失败，因此工作流终止
throw new FatalError("输入无效：缺少必填字段");

// 暂时性失败，因此会重试
throw new RetryableError("API 速率限制", { retryAfter: "5m" });

// 兼具关键性的并行执行
const results = await Promise.allSettled([
  criticalStep(data),    // 必须成功
  optionalStep(data),    // 允许失败
  enrichmentStep(data),  // 允许失败
]);
const [critical, optional, enrichment] = results;
if (critical.status === "rejected") throw new FatalError(critical.reason);
```
