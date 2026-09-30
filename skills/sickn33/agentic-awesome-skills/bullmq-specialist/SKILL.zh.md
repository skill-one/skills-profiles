---
name: bullmq-specialist
description: BullMQ专家，用于Redis后端任务队列、后台处理以及Node.js/TypeScript应用程序中的可靠异步执行。
---

# BullMQ 专家

专攻基于 Redis 的后台任务队列、异步处理，以及 Node.js/TypeScript 应用中可靠的异步执行机制的 BullMQ 专家。

## 核心原则

- 从生产者侧发起任务后不阻塞等待——让队列自行处理投递
- 始终显式设置任务选项——默认配置很少能满足实际场景
- 幂等性由你负责——任务可能会执行多次
- 退避策略可防止"惊群效应"——指数退避优于线性退避
- 死信队列不是可选项——失败的任务需要有归宿
- 并发限制保护下游服务——初期应保守设置
- 任务数据应保持精简——传递 ID，而非完整载荷
- 优雅关闭可防止孤立任务——正确处理 SIGTERM 信号

## 能力范围

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

## 适用范围

- redis-infrastructure -> redis-specialist
- serverless-queues -> upstash-qstash
- workflow-orchestration -> temporal-craftsman
- event-sourcing -> event-architect
- email-delivery -> email-systems

## 工具

### 核心

- bullmq
- ioredis

### 托管服务

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

### 基础队列配置

生产就绪的 BullMQ 队列，配置合理

**适用场景**：开始任何新的队列实现

```typescript
import { Queue, Worker, QueueEvents } from 'bullmq';
import IORedis from 'ioredis';

// 所有队列共享的连接
const connection = new IORedis(process.env.REDIS_URL, {
  maxRetriesPerRequest: null,  // BullMQ 必需
  enableReadyCheck: false,
});

// 使用合理默认值创建队列
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

// 带并发限制的 Worker
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
```

### 延迟和定时任务

在特定时间或延迟后执行的任务

**适用场景**：调度未来的任务、提醒或定时操作

```typescript
// 延迟任务——延迟后执行一次
await queue.add('reminder', { userId: 123 }, {
  delay: 24 * 60 * 60 * 1000,  // 24 小时
});

// 可重复任务——按调度执行
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
```

### 任务流与依赖关系

支持父子关系的复杂多步骤任务处理

**适用场景**：任务依赖其他任务先完成

```typescript
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
```

### 优雅关闭

在不丢失任务的情况下正确关闭 Worker

**适用场景**：部署或重启 Worker

```typescript
const shutdown = async () => {
  console.log('正在优雅关闭...');

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
```

### Bull Board 仪表板

对 BullMQ 队列进行可视化监控

**适用场景**：需要查看队列状态和任务状态

```typescript
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
```

## 验证检查项

### Redis 连接缺少 maxRetriesPerRequest

严重级别：ERROR

BullMQ 要求 maxRetriesPerRequest 设为 null 才能正确处理重连

消息：创建 BullMQ 队列/Worker 时，Redis 连接未设置 maxRetriesPerRequest: null。这会导致在 Redis 连接出现问题时 Worker 停止工作。

### 没有停滞任务事件处理器

严重级别：WARNING

Worker 应处理 stalled 事件以检测崩溃的 Worker

消息：创建 Worker 时没有'​stalled'事件处理器。停滞任务通常表示 Worker 崩溃，应加以监控。

### 没有失败任务事件处理器

严重级别：WARNING

Worker 应处理 failed 事件以便监控和告警

消息：创建 Worker 时没有'​failed'事件处理器。失败的任务应被记录并监控。

### 没有优雅关闭处理

严重级别：WARNING

Worker 应在 SIGTERM/SIGINT 时优雅关闭

消息：Worker 文件缺少优雅关闭处理。在部署时任务可能会成为孤立任务。

### 在请求处理器中等待 queue.add

严重级别：INFO

在请求处理器中入队任务应采用即发即忘方式

消息：在请求处理器中等待了 Queue.add。建议采用即发即忘方式以加快响应速度。

### 任务载荷中可能存在大数据

严重级别：WARNING

任务数据应保持精简——传递 ID 而非完整对象

消息：任务似乎包含较大的内联数据。建议传递 ID 而非完整对象，以降低 Redis 内存占用。

### 任务缺少超时配置

严重级别：INFO

任务应设置超时以防止无限执行

消息：添加任务时未显式设置超时。建议添加超时以防止任务卡住。

### 重试时缺少退避策略

严重级别：WARNING

重试应使用指数退避以避免惊群效应

消息：任务有重试次数但没有退避策略。请使用指数退避以防止惊群效应。

### 可重复任务未显式指定时区

严重级别：WARNING

可重复任务应指定时区以避免夏令时问题

消息：可重复任务未指定明确时区。将使用服务器本地时间，这在夏令时切换时可能产生偏差。

### Worker 并发数可能过高

严重级别：INFO

高并发可能压垮下游服务

消息：Worker 并发数较高。请确保下游服务能承受此负载（数据库连接、API 速率限制等）。

## 协作

### 委派触发条件

- redis 基础设施｜redis 集群｜内存调优 -> redis-specialist（队列需要 Redis 基础设施）
- serverless 队列｜边缘队列｜无需 redis -> upstash-qstash（需要不管理 Redis 的队列）
- 复杂工作流｜saga｜补偿｜长时间运行 -> temporal-craftsman（需要超越简单任务的工作流编排）
- 事件溯源｜CQRS｜事件流 -> event-architect（需要事件驱动架构）
- 部署｜kubernetes｜扩展｜基础设施 -> devops（队列需要基础设施支持）
- 监控｜指标｜告警｜仪表板 -> performance-hunter（队列需要监控）

### 邮件队列技术栈

技能：bullmq-specialist, email-systems, redis-specialist

工作流程：

```
1. 收到邮件请求（API）
2. 任务入队并应用速率限制（bullmq-specialist）
3. Worker 处理任务并应用退避（bullmq-specialist）
4. 通过服务商发送邮件（email-systems）
5. 在 Redis 中跟踪状态（redis-specialist）
```

### 后台处理技术栈

技能：bullmq-specialist, backend, devops

工作流程：

```
1. API 接收请求（backend）
2. 长任务入队到后台（bullmq-specialist）
3. Worker 异步处理（bullmq-specialist）
4. 存储/通知结果（backend）
5. 根据负载扩展 Worker（devops）
```

### AI 处理流水线

技能：bullmq-specialist, ai-workflow-automation, performance-hunter

工作流程：

```
1. 提交 AI 任务（ai-workflow-automation）
2. 创建带依赖关系的任务流（bullmq-specialist）
3. Worker 处理各阶段（bullmq-specialist）
4. 监控性能（performance-hunter）
5. 汇总结果（ai-workflow-automation）
```

### 定时任务技术栈

技能：bullmq-specialist, backend, redis-specialist

工作流程：

```
1. 定义可重复任务（bullmq-specialist）
2. 带时区的 Cron 模式（bullmq-specialist）
3. 任务按计划执行（bullmq-specialist）
4. 在 Redis 中管理状态（redis-specialist）
5. 处理结果（backend）
```

## 相关技能

常与以下技能配合使用：`redis-specialist`、`backend`、`nextjs-app-router`、`email-systems`、`ai-workflow-automation`、`performance-hunter`

## 何时使用
- 用户提及或暗示：bullmq
- 用户提及或暗示：bull queue
- 用户提及或暗示：redis queue
- 用户提及或暗示：后台任务
- 用户提及或暗示：任务队列
- 用户提及或暗示：延迟任务
- 用户提及或暗示：可重复任务
- 用户提及或暗示：Worker 进程
- 用户提及或暗示：任务调度
- 用户提及或暗示：异步处理

## 限制
- 仅当任务明确符合上述适用范围时，才使用此技能。
- 不要将输出视为环境特定验证、测试或专家评审的替代品。
- 如果缺少必要的输入、权限、安全边界或成功标准，请停下来并请求澄清。
