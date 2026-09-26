# Inngest 集成

Inngest 专为无服务器优先的背景任务、事件驱动工作流和持久执行而设计，无需管理队列或工作进程。

## 原则

- 事件是基础 - 所有操作都由事件触发，而非队列
- 步骤是您的检查点 - 每个步骤的结果都会持久存储
- 睡眠不是技巧 - Inngest 的睡眠是真实的，不会阻塞线程
- 重试是自动的 - 但您控制策略
- 函数只是 HTTP 处理程序 - 部署到任何提供 HTTP 的地方
- 并发是一流的关注点 - 保护下游服务
- 不可重复密钥防止重复 - 用于关键操作
- 分发是内置的 - 一个事件可以触发多个函数

## 功能

- inngest-functions
- event-driven-workflows
- step-functions
- serverless-background-jobs
- durable-sleep
- fan-out-patterns
- concurrency-control
- scheduled-functions

## 范围

- redis-queues -> bullmq-specialist
- serverless-queues -> upstash-qstash
- workflow-orchestration -> temporal-craftsman
- message-streaming -> event-architect
- infrastructure -> infra-architect

## 工具

### 核心

- inngest
- inngest-cli

### 框架

- nextjs
- express
- hono
- remix
- sveltekit

### 部署

- vercel
- cloudflare-workers
- netlify
- railway
- fly-io

### 模式

- step-functions
- event-fan-out
- scheduled-cron
- webhook-handling

## 模式

### 基本函数设置

在 Next.js 中使用类型化事件的 Inngest 函数

**使用场景**：在任何 Next.js 项目中开始使用 Inngest

// lib/inngest/client.ts
import { Inngest } from 'inngest';

export const inngest = new Inngest({
  id: 'my-app',
  schemas: new EventSchemas().fromRecord<Events>(),
});

// 定义您的带类型的事件
type Events = {
  'user/signed.up': { data: { userId: string; email: string } };
  'order/placed': { data: { orderId: string; total: number } };
};

// lib/inngest/functions.ts
import { inngest } from './client';

export const sendWelcomeEmail = inngest.createFunction(
  { id: 'send-welcome-email' },
  { event: 'user/signed.up' },
  async ({ event, step }) => {
    // 步骤 1：获取用户详情
    const user = await step.run('get-user', async () => {
      return await db.users.findUnique({ where: { id: event.data.userId } });
    });

    // 步骤 2：发送欢迎邮件
    await step.run('send-email', async () => {
      await resend.emails.send({
        to: user.email,
        subject: 'Welcome!',
        template: 'welcome',
      });
    });

    // 步骤 3：等待 24 小时，然后发送提示
    await step.sleep('wait-for-tips', '24h');

    await step.run('send-tips', async () => {
      await resend.emails.send({
        to: user.email,
        subject: 'Getting Started Tips',
        template: 'tips',
      });
    });
  }
);

// app/api/inngest/route.ts (Next.js App Router)
import { serve } from 'inngest/next';
import { inngest } from '@/lib/inngest/client';
import { sendWelcomeEmail } from '@/lib/inngest/functions';

export const { GET, POST, PUT } = serve({
  client: inngest,
  functions: [sendWelcomeEmail],
});

### 多步骤工作流

具有并行步骤和错误处理的复杂工作流

**使用场景**：涉及多个服务或长时间等待的处理

export const processOrder = inngest.createFunction(
  {
    id: 'process-order',
    retries: 3,
    concurrency: { limit: 10 },  // 最多同时处理 10 个订单
  },
  { event: 'order/placed' },
  async ({ event, step }) => {
    const { orderId } = event.data;

    // 并行步骤 - 同时运行
    const [inventory, payment] = await Promise.all([
      step.run('check-inventory', () => checkInventory(orderId)),
      step.run('validate-payment', () => validatePayment(orderId)),
    ]);

    if (!inventory.available) {
      // 发送事件而非直接调用（分发模式）
      await step.sendEvent('notify-backorder', {
        name: 'order/backordered',
        data: { orderId, items: inventory.missing },
      });
      return { status: 'backordered' };
    }

    // 处理支付
    const charge = await step.run('charge-payment', async () => {
      return await stripe.charges.create({
        amount: event.data.total,
        customer: payment.customerId,
      });
    });

    // 发货
    await step.run('ship-order', () => fulfillment.ship(orderId));

    return { status: 'completed', chargeId: charge.id };
  }
);

### 定时/cron 函数

按计划运行的函数

**使用场景**：每日报告或清理任务等周期性任务

export const dailyDigest = inngest.createFunction(
  { id: 'daily-digest' },
  { cron: '0 9 * * *' },  // 每天早上 9 点 UTC
  async ({ step }) => {
    // 获取所有需要摘要的用户
    const users = await step.run('get-users', async () => {
      return await db.users.findMany({
        where: { digestEnabled: true },
      });
    });

    // 向每个用户发送（创建子事件）
    await step.sendEvent(
      'send-digests',
      users.map(user => ({
        name: 'digest/send',
        data: { userId: user.id },
      }))
    );

    return { sent: users.length };
  }
);

// 另一个函数处理单个摘要发送
export const sendDigest = inngest.createFunction(
  { id: 'send-digest', concurrency: { limit: 50 } },
  { event: 'digest/send' },
  async ({ event, step }) => {
    // ... 发送单个摘要
  }
);

### 带有不可重复性的 webhook 处理程序

安全地处理 webhook 并防止重复

**使用场景**：处理 Stripe、GitHub 或其他 webhook

export const handleStripeWebhook = inngest.createFunction(
  {
    id: 'stripe-webhook',
    // 按 Stripe 事件 ID 防止重复
    idempotency: 'event.data.stripeEventId',
  },
  { event: 'stripe/webhook.received' },
  async ({ event, step }) => {
    const { type, data } = event.data;

    switch (type) {
      case 'checkout.session.completed':
        await step.run('fulfill-order', async () => {
          await fulfillOrder(data.session.id);
        });
        break;

      case 'customer.subscription.deleted':
        await step.run('cancel-subscription', async () => {
          await cancelSubscription(data.subscription.id);
        });
        break;
    }
  }
);

### 带有长时间处理的 AI 管道

多步骤 AI 处理，分块工作

**使用场景**：可能需要几分钟才能完成的 AI 工作流

export const processDocument = inngest.createFunction(
  {
    id: 'process-document',
    retries: 2,
    concurrency: { limit: 5 },  // 限制 API 使用
  },
  { event: 'document/uploaded' },
  async ({ event, step }) => {
    // 步骤 1：提取文本（可能需要较长时间）
    const text = await step.run('extract-text', async () => {
      return await extractTextFromPDF(event.data.fileUrl);
    });

    // 步骤 2：分块用于嵌入
    const chunks = await step.run('chunk-text', async () => {
      return chunkText(text, { maxTokens: 500 });
    });

    // 步骤 3：生成嵌入（API 有速率限制）
    const embeddings = await step.run('generate-embeddings', async () => {
      return await openai.embeddings.create({
        model: 'text-embedding-3-small',
        input: chunks,
      });
    });

    // 步骤 4：存储到向量数据库
    await step.run('store-vectors', async () => {
      await vectorDb.upsert({
        vectors: embeddings.data.map((e, i) => ({
          id: `${event.data.documentId}-${i}`,
          values: e.embedding,
          metadata: { chunk: chunks[i] },
        })),
      });
    });

    return { chunks: chunks.length, status: 'indexed' };
  }
);

## 验证检查

### Inngest serve 处理程序存在

严重性：CRITICAL

消息：Inngest 需要一个 serve 处理程序来接收事件

修复操作：创建 app/api/inngest/route.ts 并导出 serve()

### Functions 注册到 serve

严重性：ERROR

消息：确保所有 Inngest 函数都在 serve() 调用中注册

修复操作：在 serve() 中的 functions 数组中添加函数

### Step.run 具有描述性名称

严重性：WARNING

消息：步骤名称应为 kebab-case 并具有描述性

修复操作：使用描述性步骤名称，如 'fetch-user' 或 'send-email'

### waitForEvent 具有超时

严重性：ERROR

消息：waitForEvent 应具有超时以防止无限等待

修复操作：添加超时选项：{ timeout: '24h' }

### Function 具有并发限制

严重性：WARNING

消息：考虑添加并发限制以保护下游服务

修复操作：在函数配置中添加并发：{ limit: 10 }

### 事件类型定义

严重性：WARNING

消息：Inngest 客户端应定义事件模式以实现类型安全

修复操作：添加模式：new EventSchemas().fromRecord<Events>()

### Function 具有唯一 ID

严重性：CRITICAL

消息：每个 Inngest 函数必须具有唯一 ID

修复操作：在函数配置中添加 id: 'my-function-name'

### Sleep 使用持续时间字符串

严重性：WARNING

消息：step.sleep 应使用持续时间字符串，如 '1h' 或 '30m'，而不是毫秒

修复操作：使用持续时间字符串：step.sleep('wait', '1h')

### Retry 策略配置

严重性：WARNING

消息：考虑配置重试策略以处理失败

修复操作：添加 retries: 3 或 retries: { attempts: 3, backoff: { ... } }

### Payment 函数的不可重复密钥

严重性：ERROR

消息：与支付相关的函数应使用不可重复密钥

修复操作：在函数配置中添加 idempotency: 'event.data.orderId'

## 协作

### 授权触发器

- redis|queue 基础设施|bullmq -> bullmq-specialist (需要基于 Redis 的队列和现有基础设施)
- serverless queue|http queue|scheduled http -> upstash-qstash (需要纯 HTTP 交付和 cron，无需事件框架)
- saga|补偿|回滚|长时间运行的工作流 -> temporal-craftsman (需要复杂的流程编排和补偿)
- 事件溯源|事件存储|CQRS -> event-architect (需要事件溯源模式)
- vercel|部署|生产 -> vercel-deployment (需要部署配置)
- 数据库|模式|数据模型 -> supabase-backend (需要用于事件数据的数据库)
- api|端点|路由 -> backend (需要触发事件的 API)

### Vercel 背景任务

技能：inngest, nextjs-app-router, vercel-deployment

工作流：

```
1. 定义 Inngest 函数 (inngest)
2. 在 Next.js 中设置 serve 处理程序 (nextjs-app-router)
3. 配置函数超时 (vercel-deployment)
4. 部署和测试 (vercel-deployment)
```

### AI 管道

技能：inngest, ai-agents-architect, supabase-backend

工作流：

```
1. 设计 AI 工作流步骤 (ai-agents-architect)
2. 使用 Inngest 持久性实现 (inngest)
3. 将结果存储在数据库 (supabase-backend)
4. 处理 API 失败的重试 (inngest)
```

### webhook 处理

技能：inngest, stripe-integration, backend

工作流：

```
1. 接收 webhook (backend)
2. 使用不可重复性发送到 Inngest (inngest)
3. 处理支付逻辑 (stripe-integration)
4. 更新应用程序状态 (backend)
```

### 邮件自动化

技能：inngest, email-systems, supabase-backend

工作流：

```
1. 从用户操作触发事件 (inngest)
2. 使用 step.sleep 调度滴灌邮件 (inngest)
3. 使用重试发送邮件 (email-systems)
4. 跟踪邮件状态 (supabase-backend)
```

### 定时任务

技能：inngest, backend, analytics-architecture

工作流：

```
1. 定义 cron 触发器 (inngest)
2. 实现处理逻辑 (backend)
3. 聚合和报告数据 (analytics-architecture)
4. 使用警报处理失败 (inngest)
```

## 相关技能

与：`nextjs-app-router`, `vercel-deployment`, `supabase-backend`, `email-systems`, `ai-agents-architect`, `stripe-integration` 配合使用

## 使用场景

- 用户提及或暗示：inngest
- 用户提及或暗示：无服务器背景任务
- 用户提及或暗示：事件驱动工作流
- 用户提及或暗示：步骤函数
- 用户提及或暗示：持久执行
- 用户提及或暗示：vercel 背景任务
- 用户提及或暗示：定时函数
- 用户提及或暗示：分发

## 限制

- 仅在任务明确匹配上述范围时使用此技能。
- 不要将输出视为环境特定验证、测试或专家审查的替代品。
- 如果缺少必要的输入、权限、安全边界或成功标准，请停止并请求澄清。
