# QStash JavaScript SDK

QStash 是一种基于 HTTP 的消息传递和调度解决方案，适用于无服务器和边缘运行时。此技能将帮助您有效地使用 QStash JS SDK。

## 何时使用此技能

在以下情况下使用此技能：

- 向端点或 URL 组发布 HTTP 消息
- 创建计划或延迟消息传递
- 管理具有可配置并行性的 FIFO 队列
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

有关 QStash 基本操作的详细信息，请参阅：

- [发布消息](fundamentals/publishing-messages.md)
- [计划](fundamentals/schedules.md)
- [队列和流控制](fundamentals/queues-and-flow-control.md)
- [URL 组](fundamentals/url-groups.md)
- [本地开发](fundamentals/local-development.md) — 通过 `devMode: true` 启用的自动开发服务器

有关验证传入消息的详细信息：

- [接收器验证](verification/receiver.md) - 使用 Receiver 类进行核心签名验证
- 平台特定验证器：
  - [Next.js](verification/platform-specific/nextjs.md) - App Router、Pages Router 和 Edge 运行时

有关高级功能的详细信息：

- [回调](advanced/callbacks.md)
- [死信队列 (DLQ)](advanced/dlq.md)
- [消息去重](advanced/deduplication.md)
- [区域迁移和多区域支持](advanced/multi-region/summary.md)
  - 如有需要，[多区域环境变量设置验证脚本](advanced/multi-region/verify-multi-region-setup.ts)。无需参数即可运行

## 平台支持

QStash JS SDK 支持多种平台：

- Next.js (App Router 和 Pages Router)
- Cloudflare Workers
- Deno
- Node.js (v18+)
- Vercel Edge 运行时
- SvelteKit、Nuxt、SolidJS 和其他框架

> **关于 Workflow SDK 的说明**：对于构建链式多个 QStash 消息的复杂持久工作流，请考虑使用单独的 QStash Workflow SDK (`@upstash/workflow`)。Workflow SDK 使您能够通过自动状态管理、重试和容错来编排多步骤流程。此 Skills 文件专注于核心 QStash 消息传递 SDK。

## 最佳实践

- 始终使用 Receiver 类验证传入的 QStash 消息
- 使用环境变量存储令牌和签名密钥
- 根据您的用例设置适当的重试次数和超时
- 使用队列进行有序处理并控制并行性
- 实现DLQ处理以恢复失败的消息
