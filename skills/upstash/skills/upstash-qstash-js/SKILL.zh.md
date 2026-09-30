---
name: upstash-qstash-js
description: 使用 @upstash/qstash TypeScript/JavaScript SDK，这是一个基于 HTTP 的消息队列、任务调度器和后台作业系统，适用于无服务器和边缘运行时（Next.js、Vercel、Cloudflare Workers、Deno、Node.js）。在以下场景中使用：向 HTTP 端点或 URL 组发布消息、无需长时间运行的 Worker 进程即可运行后台作业、使用 Cron 表达式进行调度、延迟消息、构建具有并行性和流量控制的 FIFO 队列、配置重试和回调、处理死信队列（DLQ）、去重消息、分发给多个端点、验证 QStash webhook 签名（Next.js App Router、Pages Router 和 Edge Runtime）、运行本地 QStash 开发服务器或迁移区域。当用户需要无服务器 Cron 作业、异步任务队列、作业调度器、延迟交付、带重试的 webhook 交付或服务间事件驱动消息时，也请使用。
---

# QStash JavaScript SDK

QStash 是一种基于 HTTP 的消息传递和调度解决方案，适用于无服务器和边缘运行时。此技能将帮助您有效地使用 QStash JS SDK。

## 何时使用此技能

使用此技能的情况：

- 向端点或 URL 组发布 HTTP 消息
- 创建计划或延迟消息传递
- 管理具有可配置并行度的 FIFO 队列
- 验证来自 QStash 的传入 webhook 签名
- 实现回调、DLQ 处理或消息去重

## 快速入门

### 安装 SDK

```bash
npm install @upstash/qstash
```

### 基本发布

```typescript
import { Client } from "@upstash/qstash";

const client = new Client({
  token: process.env.QSTASH_TOKEN!,
});

const result = await client.publishJSON({
  url: "https://my-api.example.com/webhook",
  body: { event: "user.created", userId: "123" },
});
```

## 核心概念

有关 QStash 基本操作的说明，请参阅：

- [发布消息](fundamentals/publishing-messages.md)
- [计划](fundamentals/schedules.md)
- [队列和流控制](fundamentals/queues-and-flow-control.md)
- [URL 组](fundamentals/url-groups.md)
- [本地开发](fundamentals/local-development.md) — 通过 `devMode: true` 启用的自动开发服务器

有关验证传入消息：

- [接收器验证](verification/receiver.md) - 使用 Receiver 类进行核心签名验证
- 平台特定验证器：
  - [Next.js](verification/platform-specific/nextjs.md) - App Router、Pages Router 和 Edge 运行时

有关高级功能：

- [回调](advanced/callbacks.md)
- [死信队列 (DLQ)](advanced/dlq.md)
- [消息去重](advanced/deduplication.md)
- [区域迁移和多区域支持](advanced/multi-region/summary.md)
  - 如有需要，[多区域环境变量设置验证脚本](advanced/multi-region/verify-multi-region-setup.ts)。可无参数运行

## 平台支持

QStash JS SDK 支持多个平台：

- Next.js (App Router 和 Pages Router)
- Cloudflare Workers
- Deno
- Node.js (v18+)
- Vercel Edge 运行时
- SvelteKit、Nuxt、SolidJS 和其他框架

> **关于 Workflow SDK 的说明**：对于构建链式多个 QStash 消息的复杂持久工作流，请考虑使用单独的 QStash Workflow SDK (`@upstash/workflow`)。Workflow SDK 可让您通过自动状态管理、重试和容错来编排多步骤流程。此技能文件专注于核心 QStash 消息传递 SDK。

## 最佳实践

- 始终使用 Receiver 类验证传入的 QStash 消息
- 使用环境变量存储令牌和签名密钥
- 根据您的用例设置适当的重试次数和超时
- 使用队列进行有序处理并控制并行度
- 实现DLQ处理以恢复失败消息
