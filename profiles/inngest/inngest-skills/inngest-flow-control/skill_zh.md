# Inngest 流控制

掌握 Inngest 流控制机制，以管理资源、防止系统过载并确保应用程序的可靠性。这项技能涵盖了所有流控制选项，并提供关于何时以及如何使用每个选项的指导性建议。

> **这些技能专注于 TypeScript。** 对于 Python 或 Go，请参考 [Inngest 文档](https://www.inngest.com/llms.txt) 获取语言特定的指导。核心概念适用于所有语言。

## 快速决策指南

- **"限制同时运行的数量"** → 并发控制
- **"在一段时间内分散运行"** → 流量限制
- **"在一段时间内 N 次运行后阻塞"** → 速率限制
- **"等待活动停止后运行一次"** → 延迟执行
- **"此键每次只运行一次"** → 单例
- **"按组处理事件"** → 批处理
- **"有些运行比其他运行更重要"** → 优先级

## 并发控制

**使用场景：** 限制正在执行的步骤（而不是函数运行）的数量，以管理计算资源并防止系统过载。

**关键洞察：** 并发控制限制的是活动代码执行，而不是函数运行。等待 `step.sleep()` 或 `step.waitForEvent()` 的函数不计入限制。

### 基本并发控制

```typescript
inngest.createFunction(
  {
    id: "process-images",
    concurrency: 5,
    triggers: [{ event: "media/image.uploaded" }]
  },
  async ({ event, step }) => {
    // 同时只能有 5 个步骤执行
    await step.run("resize", () => resizeImage(event.data.imageUrl));
  }
);
```

### 带键的并发控制（多租户）

使用 `key` 参数按唯一键值应用限制。

```typescript
inngest.createFunction(
  {
    id: "user-sync",
    concurrency: [
      {
        key: "event.data.user_id",
        limit: 1
      }
    ],
    triggers: [{ event: "user/profile.updated" }]
  },
  async ({ event, step }) => {
    // 每个用户一次只能执行一个步骤
    // 防止用户特定操作的竞争条件
  }
);
```

### 账户级共享限制

```typescript
inngest.createFunction(
  {
    id: "ai-summary",
    concurrency: [
      {
        scope: "account",
        key: `"openai"`,
        limit: 60
      }
    ],
    triggers: [{ event: "ai/summary.requested" }]
  },
  async ({ event, step }) => {
    // 在所有函数之间共享 60 个并发 OpenAI 调用
  }
);
```

**每种使用场景：**

- 基本：保护数据库或限制一般容量
- 带键的：多租户公平性，防止“噪音邻居”问题
- 账户级：在多个函数之间共享配额（API 限制）

## 流量限制

**使用场景：** 控制函数启动的速率，以绕过 API 速率限制或平滑流量峰值。

**与并发控制的关键区别：** 流量限制限制函数运行启动；并发控制限制步骤执行。

```typescript
inngest.createFunction(
  {
    id: "sync-crm-data",
    throttle: {
      limit: 10, // 每分钟 10 次函数启动
      period: "60s", // 每分钟
      burst: 5, // 立即额外启动 5 次
      key: "event.data.customer_id" // 按客户
    },
    triggers: [{ event: "crm/contact.updated" }]
  },
  async ({ event, step }) => {
    // 尊重 CRM API 速率限制：每分钟每个客户 10 次调用
    await step.run("sync", () => crmApi.updateContact(event.data));
  }
);
```

**配置：**

- `limit`：每个时间段内可以启动的函数数量
- `period`：时间窗口（1s 到 7d）
- `burst`：允许的立即额外启动次数
- `key`：按唯一键值应用限制

## 速率限制

**使用场景：** 设置硬性限制，以防止滥用或跳过过多的重复事件。

**与流量限制的关键区别：** 速率限制会丢弃事件；流量限制会延迟事件。

```typescript
inngest.createFunction(
  {
    id: "webhook-processor",
    rateLimit: {
      limit: 1,
      period: "4h",
      key: "event.data.webhook_id"
    },
    triggers: [{ event: "webhook/data.received" }]
  },
  async ({ event, step }) => {
    // 每个 webhook 每隔 4 小时只处理一次
    // 防止重复的 webhook 垃圾邮件
  }
);
```

**用例：**

- 防止 webhook 重复
- 限制每个用户的昂贵操作
- 防止滥用

## 延迟执行

**使用场景：** 等待一系列事件停止到达后再处理最新事件。

```typescript
inngest.createFunction(
  {
    id: "save-document",
    debounce: {
      period: "5m", // 等待最后编辑 5 分钟后
      key: "event.data.document_id",
      timeout: "30m" // 最多 30 分钟后强制保存
    },
    triggers: [{ event: "document/content.changed" }]
  },
  async ({ event, step }) => {
    // 只有在用户停止编辑后才会保存文档
    // 使用接收到的最后一个事件
    await step.run("save", () => saveDocument(event.data));
  }
);
```

**非常适合：**

- 用户输入快速变化（搜索、文档编辑）
- 嘈杂的 webhook 事件
- 确保处理最新数据

## 优先级

**使用场景：** 基于动态数据，优先执行某些函数运行。

```typescript
inngest.createFunction(
  {
    id: "process-order",
    priority: {
      // VIP 用户优先级最高，提前 120 秒执行
      run: "event.data.user_tier == 'vip' ? 120 : 0"
    },
    triggers: [{ event: "order/placed" }]
  },
  async ({ event, step }) => {
    // VIP 订单在队列中优先执行
  }
);
```

**高级示例：**

```typescript
inngest.createFunction(
  {
    id: "support-ticket",
    priority: {
      run: `
        event.data.severity == 'critical' ? 300 :
        event.data.severity == 'high' ? 120 :
        event.data.user_plan == 'enterprise' ? 60 : 0
      `
    },
    triggers: [{ event: "support/ticket.created" }]
  },
  async ({ event, step }) => {
    // 严重性为“关键”的工单优先级最高（提前 300 秒）
    // 严重性为“高”：提前 120 秒
    // 企业用户：提前 60 秒
    // 其他所有人：正常优先级
  }
);
```

## 单例

**使用场景：** 确保同一时间只有一个函数实例在运行。

### 跳过模式（保留当前运行）

```typescript
inngest.createFunction(
  {
    id: "data-backup",
    singleton: {
      key: "event.data.database_id",
      mode: "skip"
    },
    triggers: [{ event: "backup/requested" }]
  },
  async ({ event, step }) => {
    // 如果此数据库已经有正在运行的备份，则跳过新的备份
    await step.run("backup", () => performBackup(event.data.database_id));
  }
);
```

### 取消模式（使用最新事件）

```typescript
inngest.createFunction(
  {
    id: "realtime-sync",
    singleton: {
      key: "event.data.user_id",
      mode: "cancel"
    },
    triggers: [{ event: "user/data.changed" }]
  },
  async ({ event, step }) => {
    // 取消之前的同步，并使用最新数据开始
    await step.run("sync", () => syncUserData(event.data));
  }
);
```

## 批处理

**使用场景：** 将多个事件一起处理以提高效率。

```typescript
inngest.createFunction(
  {
    id: "bulk-email-send",
    batchEvents: {
      maxSize: 100, // 最多 100 个事件
      timeout: "30s", // 或 30 秒，以先到为准
      // `key` 将事件分组为每个唯一值单独的批次
      // 这与 `if` 表达式过滤事件不同
      key: "event.data.campaign_id" // 按活动批处理
    },
    triggers: [{ event: "email/send.queued" }]
  },
  async ({ events, step }) => {
    // 一起处理事件数组
    const emails = events.map((evt) => ({
      to: evt.data.email,
      subject: evt.data.subject,
      body: evt.data.body
    }));

    await step.run("send-batch", () => emailService.sendBulk(emails));
  }
);
```

## 组合流控制

### 示例：公平的 AI 处理

```typescript
inngest.createFunction(
  {
    id: "ai-image-processing",
    // 全局流量限制以应对 API 限制
    throttle: {
      limit: 50,
      period: "60s",
      key: `"gpu-cluster"`
    },
    // 按用户公平的并发控制
    concurrency: [
      {
        key: "event.data.user_id",
        limit: 3
      }
    ],
    // VIP 用户优先
    priority: {
      run: "event.data.plan == 'pro' ? 60 : 0"
    },
    triggers: [{ event: "ai/image.generate" }]
  },
  async ({ event, step }) => {
    // 组合多种流控制以优化资源使用
  }
);
```

**小贴士：** 大多数生产函数从组合 1-3 种流控制机制中受益，以获得最佳的可靠性和性能。
