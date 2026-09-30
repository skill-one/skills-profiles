---
name: upstash-workflow-js
description: '使用 @upstash/workflow TypeScript/JavaScript SDK 实现服务器端函数中的持久化、长时间运行的工作流，支持跨超时、重试和重启的多步骤流程（基于 QStash）。适用于以下场景：


  - 使用 serve() 定义工作流端点

  - 使用 context.run 运行步骤

  - 以分钟到天为单位休眠而不保持函数开启状态

  - 使用 context.call 调用外部 API

  - 等待外部事件或 webhook

  - 调用其他工作流

  - 配置重试、失败回调和死信队列（DLQ）

  - 控制并发、速率和并行度

  - 使用 Workflow 客户端触发、取消或检查运行

  - 构建 AI 代理和编排器

  - 人机审批流程

  - 实时更新

  - 使用 QStash 开发服务器进行本地开发

  - 添加中间件

  - 安全迁移工作流


  此外，当用户需要持久化执行、步骤函数、Saga 或编排模式、带检查点的后台任务，或 Vercel、Next.js、Cloudflare Workers 或其他无服务器平台上的长时间运行任务时，也推荐使用。'
---

# Upstash Workflow SDK

## 快速入门

Upstash Workflow SDK 允许您暴露无服务器工作流端点，并使用底层的 QStash 可靠地运行它们。

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
- 如何：
  - **how-to/local-dev** – 本地 QStash 开发服务器（通过 `QSTASH_DEV=true` 自动）和隧道。
  - **how-to/realtime** – 实时和人工介入的工作流。
  - **how-to/migrations** – 安全迁移工作流。
  - **how-to/middleware** – 为工作流添加中间件。
- 其他文件：
  - **rest-api** – 与 QStash/Workflow 交互的低级 REST 端点。
  - **troubleshooting** – 常见的调试和环境问题。
  - **agents** – 使用代理、协调器和自动化模式的工作流。
