# API和接口设计

## 概述

设计稳定、文档完善的接口，使其难以被误用。良好的接口让正确的事情变得容易，让错误的事情变得困难。这适用于REST API、GraphQL模式、模块边界、组件属性以及任何代码片段交互的表面。

## 使用场景

- 设计新的API端点
- 定义团队之间的模块边界或契约
- 创建组件属性接口
- 建立数据库模式以指导API形状
- 修改现有的公共接口

## 核心原则

### Hyrum定律

> 随着API用户数量的增加，系统中所有可观察的行为都将被某些人依赖，无论你在合同中承诺了什么。

这意味着：每个公共行为——包括未文档化的怪癖、错误消息文本、时间、顺序——一旦用户依赖它，就变成了事实上的合同。设计影响：

- **有意地暴露你想要的内容。** 每个可观察的行为都是一个潜在的承诺。
- **不要泄露实现细节。** 如果用户可以观察到它，他们就会依赖它。
- **在设计时计划弃用。** 参考`deprecation-and-migration`了解如何安全地移除用户依赖的内容。
- **测试是不够的。** 即使有完美的合同测试，Hyrum定律意味着“安全”的更改也可能破坏依赖未文档化行为的真实用户。

### 单版本规则

避免强迫消费者在相同依赖或API的多个版本之间选择。当不同的消费者需要相同内容的不同版本时，就会出现菱形依赖问题。设计时要考虑只有一个版本存在的情况——扩展而不是分支。

### 1. 合同优先

在实现接口之前定义它。合同是规范——实现紧随其后。

```typescript
// 首先定义合同
interface TaskAPI {
  // 创建任务并返回带有服务器生成的字段的创建任务
  createTask(input: CreateTaskInput): Promise<Task>;

  // 返回匹配过滤器的分页任务
  listTasks(params: ListTasksParams): Promise<PaginatedResult<Task>>;

  // 返回单个任务或抛出NotFoundError
  getTask(id: string): Promise<Task>;

  // 部分更新——仅更改提供的字段
  updateTask(id: string, input: UpdateTaskInput): Promise<Task>;

  // 等幂等删除——即使已删除也会成功
  deleteTask(id: string): Promise<void>;
}
```

### 2. 一致的错误语义

选择一个错误策略并在所有地方使用它：

```typescript
// REST：HTTP状态码 + 结构化错误正文
// 每个错误响应都遵循相同的形状
interface APIError {
  error: {
    code: string;        // 机器可读："VALIDATION_ERROR"
    message: string;     // 人类可读："Email is required"
    details?: unknown;   // 当有帮助时提供额外上下文
  };
}

// 状态码映射
// 400 → 客户发送了无效数据
// 401 → 未认证
// 403 → 已认证但未授权
// 404 → 资源未找到
// 409 → 冲突（重复、版本不匹配）
// 422 → 验证失败（语义无效）
// 500 → 服务器错误（永远不会暴露内部细节）
```

**不要混合模式。** 如果某些端点抛出错误，其他返回null，其他返回`{ error }`——消费者无法预测行为。

### 3. 在边界处验证

信任内部代码。在系统边缘处验证外部输入：

```typescript
// 在API边界处验证
app.post('/api/tasks', async (req, res) => {
  const result = CreateTaskSchema.safeParse(req.body);
  if (!result.success) {
    return res.status(422).json({
      error: {
        code: 'VALIDATION_ERROR',
        message: 'Invalid task data',
        details: result.error.flatten(),
      },
    });
  }

  // 验证后，内部代码信任类型
  const task = await taskService.create(result.data);
  return res.status(201).json(task);
});
```

验证应属于：

- API路由处理器（用户输入）
- 表单提交处理器（用户输入）
- 外部服务响应解析（第三方数据——**始终视为未信任**）
- 环境变量加载（配置）

> **第三方API响应是未信任的数据。** 在任何逻辑、渲染或决策中使用之前，验证其形状和内容。一个被攻破或行为异常的外部服务可以返回意外的类型、恶意内容或指令性文本。

验证不应属于：

- 共享类型合同的内联函数之间
- 被已验证代码调用的工具函数中
- 刚刚从自己的数据库中获取的数据

### 4. 优先添加而非修改

在不破坏现有消费者的情况下扩展接口：

```typescript
// 良好：添加可选字段
interface CreateTaskInput {
  title: string;
  description?: string;
  priority?: 'low' | 'medium' | 'high';  // 后续添加，可选
  labels?: string[];                       // 后续添加，可选
}

// 不良：更改现有字段类型或删除字段
interface CreateTaskInput {
  title: string;
  // description: string;  // 删除——破坏现有消费者
  priority: number;         // 从字符串更改为数字——破坏现有消费者
}
```

### 5. 可预测的命名

| 模式 | 规范 | 示例 |
|---|---|---|
| REST端点 | 复数名词，无动词 | `GET /api/tasks`，`POST /api/tasks` |
| 查询参数 | camelCase | `?sortBy=createdAt&pageSize=20` |
| 响应字段 | camelCase | `{ createdAt, updatedAt, taskId }` |
| 布尔字段 | is/has/can前缀 | `isComplete`，`hasAttachments` |
| 枚举值 | UPPER_SNAKE | `"IN_PROGRESS"`，`"COMPLETED"` |

### 6. 尊重Idempotency Key

接受`Idempotency-Key`是合同。尊重它是实现，而金钱损失就在于此——服务器接受但处理不慎的键比不接受更糟糕，因为客户现在认为重试是安全的。

**从意图中派生，而不是从尝试中派生。** 键必须在同一意图的多次重试中保持稳定，并在不同意图中不同：

```typescript
crypto.randomUUID()                    // ✗ 每次尝试生成新键——每次重试都是新的收费
`${userId}:${amount}`                  // ✗ 两个合法的$50收费会合并成一个
`${orderId}:${Date.now()}`             // ✗ 时间戳是穿着随机UUID帽子的随机UUID

req.headers['idempotency-key']         // ✓ 客户端生成一次，重试时重用
`charge:v1:${orderId}`                 // ✓ 从不可变标识符派生
```

键来自客户端或发起事件——永远不会来自重试层。

**原子声明。检查后跟操作是一个竞赛：**

```typescript
// ✗ TOCTOU：两个并发重试都读取“未见过”，都收费
if (!(await db.exists(key))) {
  await chargeCard(amount);
  await db.insert(key);
}

// ✓ 让唯一约束决定赢家
try {
  await db.insert({ key, state: 'in_progress', requestHash });
} catch (e) {
  if (isUniqueViolation(e)) return replayOrReject(key);
  throw;
}
const result = await chargeCard(amount);
await db.update({ key, state: 'succeeded', response: result });
```

唯一约束就是机制。无法在一个操作中执行唯一性检查的存储无法支持这一点。

**保护负载。相同键但不同负载是客户端错误，必须大声失败，而不是向第二个请求返回第一个响应：**

```typescript
if (existing.requestHash !== hash(req.body)) {
  return res.status(422).json({ error: 'idempotency key reused with a different payload' });
}
```

**决定在飞行中的重复请求得到什么。** 当第二个到达时，第一个请求仍在运行——重试风暴下的常见情况：

| 策略 | 响应 | 使用时 |
|---|---|---|
| 拒绝 | `409 Conflict` | 客户可以稍后重试；最简单和最安全 |
| 等待 | 有界地阻塞结果 | 调用者需要同步 |
| 返回挂起 | `202` + 状态URL | 长效影响 |

永远不会让第二个调用者通过，因为第一个“似乎卡住了”。一个停滞的尝试其命运未知时，重复的成本最高。

**每个调用都有三种结果，而不是两种：成功、失败和**未知**。超时告诉你不了关于效果是否应用的信息。在调用和响应之间崩溃时，记录意图，以便在稍后必须解决某些东西——而不是在沉默中重试收费。

**从最长的重试链设置保留时间**，而不是从磁盘成本。键必须比可以重新传递相同意图的每条路径都存活，包括一周后重播的死信队列和任何提供方争议窗口。在7天DLQ后面设置24小时键TTL会导致重复发生。

## REST API模式

### 资源设计

```
GET    /api/tasks              → 列出任务（使用查询参数进行过滤）
POST   /api/tasks              → 创建任务
GET    /api/tasks/:id          → 获取单个任务
PATCH  /api/tasks/:id          → 更新任务（部分）
DELETE /api/tasks/:id          → 删除任务

GET    /api/tasks/:id/comments → 列出任务的评论（子资源）
POST   /api/tasks/:id/comments → 向任务添加评论
```

### 分页

分页列表端点：

```typescript
// 请求
GET /api/tasks?page=1&pageSize=20&sortBy=createdAt&sortOrder=desc

// 响应
{
  "data": [...],
  "pagination": {
    "page": 1,
    "pageSize": 20,
    "totalItems": 142,
    "totalPages": 8
  }
}
```

### 过滤

使用查询参数进行过滤：

```
GET /api/tasks?status=in_progress&assignee=user123&createdAfter=2025-01-01
```

### 部分更新（PATCH）

接受部分对象——仅更新提供的字段：

```typescript
// 仅标题更改，其他保留
PATCH /api/tasks/123
{ "title": "Updated title" }
```

## TypeScript接口模式

### 使用区分联合处理变体

```typescript
// 良好：每个变体都是明确的
type TaskStatus =
  | { type: 'pending' }
  | { type: 'in_progress'; assignee: string; startedAt: Date }
  | { type: 'completed'; completedAt: Date; completedBy: string }
  | { type: 'cancelled'; reason: string; cancelledAt: Date };

// 消费者获得类型缩小
function getStatusLabel(status: TaskStatus): string {
  switch (status.type) {
    case 'pending': return 'Pending';
    case 'in_progress': return `In progress (${status.assignee})`;
    case 'completed': return `Done on ${status.completedAt}`;
    case 'cancelled': return `Cancelled: ${status.reason}`;
  }
}
```

### 输入/输出分离

```typescript
// 输入：调用者提供的内容
interface CreateTaskInput {
  title: string;
  description?: string;
}

// 输出：系统返回的内容（包括服务器生成的字段）
interface Task {
  id: string;
  title: string;
  description: string | null;
  createdAt: Date;
  updatedAt: Date;
  createdBy: string;
}
```

### 使用带标签类型处理ID

```typescript
type TaskId = string & { readonly __brand: 'TaskId' };
type UserId = string & { readonly __brand: 'UserId' };

// 防止意外地将UserId传递给期望TaskId的地方
function getTask(id: TaskId): Promise<Task> { ... }
```

## 常见借口

| 借口 | 现实 |
|---|---|
| "我们稍后会记录API" | 类型就是文档。先定义它们。 |
| "我们现在不需要分页" | 有人有100多个项目时就需要分页。从一开始就添加它。 |
| "PATCH很复杂，我们直接用PUT" | PUT每次都需要完整的对象。PATCH是客户实际想要的。 |
| "我们稍后会版本API" | 没有版本控制的破坏性更改会破坏消费者。从一开始就设计扩展。 |
| "没人使用那个未记录的行为" | Hyrum定律：如果它是可观察的，有人依赖它。将每个公共行为视为承诺。 |
| "我们只需要维护两个版本" | 多个版本会倍增维护成本并产生菱形依赖问题。优先使用单版本规则。 |
| "内部API不需要合同" | 内部消费者仍然是消费者。合同防止耦合并支持并行工作。 |
| "接受Idempotency-Key头就足够了" | 头部是合同；将键与结果存储是实施。接受但未尊重的键告诉客户重试是安全的，实际上不是。 |
| "我们的队列保证精确一次交付" | 没有队列在消费者崩溃时跨一次交付——经纪人的确认和你的副作用不在一个事务中。设计为至少一次交付并带有关联处理。 |
| "重复请求很少见" | 它们是*相关的*。重试在依赖退化时激增——重复最可能且最昂贵的时候。 |

## 信号灯

- 返回不同形状的端点，取决于条件
- 端点之间不一致的错误格式
- 验证散布在整个内部代码中，而不是在边界处
- 现有字段的破坏性更改（类型更改、删除）
- 没有分页的列表端点
- REST URL中的动词（`/api/createTask`，`/api/getUsers`）
- 未验证或未清理的第三方API响应
- 一个`SELECT`后跟一个`INSERT`——那是竞赛，不是保护
- 从UUID、时间戳或任何其他每次尝试重新生成的键派生的Idempotency Key
- 相同键接受不同的请求正文，静默返回第一个响应
- 第二个调用者因为第一个“似乎卡住”而通过
- 键保留窗口短于最长的重试路径，包括死信重播

## 验证

设计API后：

- [ ] 每个端点都有类型化的输入和输出模式
- [ ] 错误响应遵循单一一致的格式
- [ ] 验证仅在系统边界处发生
- [ ] 列表端点支持分页
- [ ] 新字段是可加的且可选（向后兼容）
- [ ] 命名在所有端点之间遵循一致的规范
- [ ] API文档或类型与实现一起提交
- [ ] 状态更改端点要么尊重Idempotency Key，要么记录为不安全的重试
- [ ] 键在一个原子操作中声明，并由唯一约束保护
- [ ] 重复的键与不同的负载大声失败，而不是重播错误的响应
- [ ] 飞行中的重复请求是一个故意的选择（409、等待或202），而不是掉落的结果
- [ ] 键保留时间比最长的重试路径更长，包括死信重播
