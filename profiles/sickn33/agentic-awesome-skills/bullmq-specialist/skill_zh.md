# BullMQ 专家

BullMQ 专家，用于 Redis 支持的任务队列、后台处理以及 Node.js/TypeScript 应用中的可靠异步执行。

## 原则

- 生产端任务为“发即忘”，让队列处理投递
- 始终设置明确的任务选项——默认值很少符合您的用例
- 幂等性是您的责任——任务可能会运行多次
- 指数退避策略防止“雷鸣之群”——指数优于线性
- 死信队列是必需的——失败的任务需要一个归宿
- 并发限制保护下游服务——从保守开始
- 任务数据应保持小——传递 ID 而不是有效负载
- 平稳关闭防止孤儿任务——正确处理 SIGTERM

## 功能

- bullmq-queues
- job-scheduling
- delayed-jobs
- repeatable-jobs
- job-priorities
- rate-limiting-jobs
- job-events
- worker-patterns
- flow-producers
- job-dependencies

## 范围

- redis-infrastructure -> redis-specialist
- serverless-queues -> upstash-qstash
- workflow-orchestration -> temporal-craftsman
- event-sourcing -> event-architect
- email-delivery -> email-systems

## 工具

### 核心

- bullmq
- ioredis

### 托管

- upstash
- redis-cloud
- elasticache
- railway

### 监控

- bull-board
- arena
- bullmq-pro

### 模式

- delayed-jobs
- repeatable-jobs
- job-flows
- rate-limiting
- sandboxed-processors

## 模式

### 基本队列设置

具有正确配置的生产就绪 BullMQ 队列

**使用场景**：开始任何新的队列实现

import { Queue, Worker, QueueEvents } from 'bullmq';
import IORedis from 'ioredis';

// 所有队列共享的连接
const connection = new IORedis(process.env.REDIS_URL, {
  maxRetriesPerRequest: null,  // BullMQ 所需
  enableReadyCheck: false,
});

// 使用合理的默认值创建队列
const emailQueue = new Queue('emails', {
  connection,
  defaultJobOptions: {
    attempts: 3,
    backoff: {
      type: 'exponential',
      delay: 1000,
    },
    removeOnComplete: { count: 1000 },
    removeOnFail: { count: 5000 },
  },
});

// 具有并发限制的 Worker
const worker = new Worker('emails', async (job) => {
  await sendEmail(job.data);
}, {
  connection,
  concurrency: 5,
  limiter: {
    max: 100,
    duration: 60000,  // 每分钟 100 个任务
  },
});

// 处理事件
worker.on('failed', (job, err) => {
  console.error(`任务 ${job?.id} 失败：`, err);
});

### 延迟和计划任务

在特定时间或延迟后运行的任务

**使用场景**：安排未来任务、提醒或定时操作

// 延迟任务——延迟后运行一次
await queue.add('reminder', { userId: 123 }, {
  delay: 24 * 60 * 60 * 1000,  // 24 小时
});

// 可重复任务——按计划运行
await queue.add('daily-digest', { type: 'summary' }, {
  repeat: {
    pattern: '0 9 * * *',  // 每天早上 9 点
    tz: 'America/New_York',
  },
});

// 移除可重复任务
await queue.removeRepeatable('daily-digest', {
  pattern: '0 9 * * *',
  tz: 'America/New_York',
});

### 任务流程和依赖关系

具有父子关系的复杂多步骤任务处理

**使用场景**：任务依赖于其他任务先完成

import { FlowProducer } from 'bullmq';

const flowProducer = new FlowProducer({ connection });

// 父任务等待所有子任务完成
await flowProducer.add({
  name: 'process-order',
  queueName: 'orders',
  data: { orderId: 123 },
  children: [
    {
      name: 'validate-inventory',
      queueName: 'inventory',
      data: { orderId: 123 },
    },
    {
      name: 'charge-payment',
      queueName: 'payments',
      data: { orderId: 123 },
    },
    {
      name: 'notify-warehouse',
      queueName: 'notifications',
      data: { orderId: 123 },
    },
  ],
});

### 平稳关闭

正确关闭 Worker 而不丢失任务

**使用场景**：部署或重启 Worker

const shutdown = async () => {
  console.log('正在平稳关闭...');

  // 停止接受新任务
  await worker.pause();

  // 等待当前任务完成（带超时）
  await worker.close();

  // 关闭队列连接
  await queue.close();

  process.exit(0);
};

process.on('SIGTERM', shutdown);
process.on('SIGINT', shutdown);

### Bull Board 仪表板

BullMQ 队列的可视化监控

**使用场景**：需要了解队列状态和任务状态

import { createBullBoard } from '@bull-board/api';
import { BullMQAdapter } from '@bull-board/api/bullMQAdapter';
import { ExpressAdapter } from '@bull-board/express';

const serverAdapter = new ExpressAdapter();
serverAdapter.setBasePath('/admin/queues');

createBullBoard({
  queues: [
    new BullMQAdapter(emailQueue),
    new BullMQAdapter(orderQueue),
  ],
  serverAdapter,
});

app.use('/admin/queues', serverAdapter.getRouter());

## 验证检查

### 缺少 Redis 连接的 maxRetriesPerRequest

严重程度：错误

BullMQ 需要为 Redis 连接设置 maxRetriesPerRequest 为 null 以进行正确的重连处理

消息：BullMQ 队列/Worker 在 Redis 连接中未设置 maxRetriesPerRequest: null。这将导致 Worker 在 Redis 连接问题时停止。

### 没有停滞任务事件处理器

严重程度：警告

Worker 应处理停滞事件以检测崩溃的 Worker

消息：创建 Worker 时未设置 'stalled' 事件处理器。停滞任务表示 Worker 崩溃，应进行监控。

### 没有失败任务事件处理器

严重程度：警告

Worker 应处理失败事件以进行监控和告警

消息：创建 Worker 时未设置 'failed' 事件处理器。失败任务应记录和监控。

### 没有平稳关闭处理

严重程度：警告

Worker 应在 SIGTERM/SIGINT 上平稳关闭

消息：Worker 文件缺少平稳关闭处理。在部署时任务可能会成为孤儿。

### 在请求处理器中等待 queue.add

严重程度：信息

队列添加应在请求处理器中为“发即忘”

消息：在请求处理器中等待 Queue.add。考虑使用“发即忘”以获得更快的响应。

### 任务有效负载中可能存在大量数据

严重程度：警告

任务数据应保持小——传递 ID 而不是完整对象

消息：任务似乎具有大量内联数据。传递 ID 而不是完整对象以保持 Redis 内存低。

### 没有超时配置的任务

严重程度：信息

任务应具有超时以防止无限执行

消息：添加任务时未设置显式超时。考虑添加超时以防止卡住的任务。

### 没有退避策略的重试

严重程度：警告

重试应使用指数退避以避免“雷鸣之群”

消息：任务具有重试尝试但没有退避策略。使用指数退避以防止“雷鸣之群”。

### 可重复任务没有显式时区

严重程度：警告

可重复任务应指定时区以避免夏令时问题

消息：可重复任务没有显式时区。将使用服务器本地时间，这可能会随夏令时变化而漂移。

### 可能的 Worker 并发过高

严重程度：信息

高并发可能会压垮下游服务

消息：Worker 并发过高。确保下游服务能够处理此负载（数据库连接、API 速率限制）。

## 协作

### 授权触发器

- redis infrastructure|redis cluster|memory tuning -> redis-specialist (队列需要 Redis 基础设施)
- serverless queue|edge queue|no redis -> upstash-qstash (需要无需管理 Redis 的队列)
- complex workflow|saga|compensation|long-running -> temporal-craftsman (需要超出简单任务的流程编排)
- event sourcing|CQRS|event streaming -> event-architect (需要事件驱动架构)
- deploy|kubernetes|scaling|infrastructure -> devops (队列需要基础设施)
- monitor|metrics|alerting|dashboard -> performance-hunter (队列需要监控)

### 邮件队列堆栈

技能：bullmq-specialist, email-systems, redis-specialist

工作流程：

```
1. 接收邮件请求（API）
2. 带有速率限制的任务入队（bullmq-specialist）
3. Worker 带退避处理（bullmq-specialist）
4. 通过提供程序发送邮件（email-systems）
5. 状态在 Redis 中跟踪（redis-specialist）
```

### 后台处理堆栈

技能：bullmq-specialist, backend, devops

工作流程：

```
1. API 接收请求（backend）
2. 长任务入队到后台（bullmq-specialist）
3. Worker 异步处理（bullmq-specialist）
4. 存储结果/通知（backend）
5. 根据负载扩展 Worker（devops）
```

### AI 处理管道

技能：bullmq-specialist, ai-workflow-automation, performance-hunter

工作流程：

```
1. 提交 AI 任务（ai-workflow-automation）
2. 创建带依赖关系的任务流程（bullmq-specialist）
3. Worker 处理阶段（bullmq-specialist）
4. 监控性能（performance-hunter）
5. 汇总结果（ai-workflow-automation）
```

### 计划任务堆栈

技能：bullmq-specialist, backend, redis-specialist

工作流程：

```
1. 定义可重复任务（bullmq-specialist）
2. 带时区的 Cron 模式（bullmq-specialist）
3. 按计划执行任务（bullmq-specialist）
4. 状态在 Redis 中管理（redis-specialist）
5. 处理结果（backend）
```

## 相关技能

与：`redis-specialist`, `backend`, `nextjs-app-router`, `email-systems`, `ai-workflow-automation`, `performance-hunter` 配合使用

## 使用场景
- 用户提及或暗示：bullmq
- 用户提及或暗示：bull 队列
- 用户提及或暗示：redis 队列
- 用户提及或暗示：后台任务
- 用户提及或暗示：任务队列
- 用户提及或暗示：延迟任务
- 用户提及或暗示：可重复任务
- 用户提及或暗示：worker 处理
- 用户提及或暗示：任务调度
- 用户提及或暗示：异步处理

## 限制
- 仅在任务明确匹配上述范围时使用此技能。
- 不要将输出视为环境特定验证、测试或专家审查的替代品。
- 如果缺少必要的输入、权限、安全边界或成功标准，请停止并请求澄清。
