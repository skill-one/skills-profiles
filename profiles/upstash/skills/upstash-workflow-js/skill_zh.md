# Upstash 工作流 SDK

## 快速入门

Upstash 工作流 SDK 允许您暴露无服务器工作流端点，并使用底层的 QStash 可靠地运行它们。

安装：

```bash
npm install @upstash/workflow
```

定义一个简单的工作流端点：

```ts
import { serve } from "@upstash/workflow";

export const { POST } = serve(async (context) => {
  await context.run("step-1", () => console.log("step 1"));
  await context.run("step-2", () => console.log("step 2"));
});
```

从您的后端触发它：

```ts
import { Client } from "@upstash/workflow";

const client = new Client({ token: process.env.QSTASH_TOKEN! });
await client.trigger({ url: "https://your-app.com/api/workflow" });
```

## 其他技能文件

这些文件包含完整文档。用于了解细节、模式和高级行为。

- 基础：
  - **basics/serve** – 如何暴露工作流端点。
  - **basics/context** – 工作流 `context` 的完整 API（步骤、等待、webhook、事件、调用等）。
  - **basics/client** – 使用工作流客户端触发、取消、检查和通知运行。
- 功能：
  - **features/invoke** – 跨工作流调用。
  - **features/reliability** – 重试、失败回调和 DLQ。
  - **features/flow-control** – 速率限制、并发和并行。
  - **features/wait-for-event** – 通知和 wait-for-event 模式。
  - **features/webhooks** – webhook 创建和消费。
- 如何操作：
  - **how-to/local-dev** – 本地 QStash 开发服务器（通过 `QSTASH_DEV=true` 自动）和隧道。
  - **how-to/realtime** – 实时和人工介入的工作流。
  - **how-to/migrations** – 安全迁移工作流。
  - **how-to/middleware** – 向工作流添加中间件。
- 其他文件：
  - **rest-api** – 与 QStash/Workflow 交互的低级 REST 端点。
  - **troubleshooting** – 常见的调试和环境问题。
  - **agents** – 使用代理、协调器和自动化模式的工作流。
