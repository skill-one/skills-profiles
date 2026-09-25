# 端到端测试技能

端到端测试从用户角度验证完整的工作流程，通过 Docker 使用真实基础设施。

---

## 工作流程

为获得全面的分步指导，请使用相应的工作流程：

| 工作流程 | 使用场景 |
|----------|-------------|
| [设置端到端测试](workflows/setup/workflow.md) | 为新项目或现有项目设置端到端基础设施 |
| [编写端到端测试](workflows/writing/workflow.md) | 使用正确的 GWT 模式创建新的端到端测试用例 |
| [审查端到端测试](workflows/review/workflow.md) | 审查现有测试的质量和正确性 |
| [运行端到端测试](workflows/running/workflow.md) | 使用正确的验证执行测试 |
| [调试端到端测试](workflows/debugging/workflow.md) | 系统地修复失败的测试 |
| [优化端到端测试](workflows/optimize/workflow.md) | 提高测试套件性能 |

## 工作流程选择指南

**重要提示**：在开始任何端到端测试任务之前，确定用户的意图并加载相应的工作流程。

### 检测用户意图 → 选择工作流程

| 用户说/想要 | 加载的工作流程 | 文件 |
|-------------------|------------------|------|
| "设置端到端测试", "配置 docker-compose", "将端到端添加到项目", "创建测试辅助工具" | **设置** | `workflows/setup/workflow.md` |
| "编写端到端测试", "添加集成测试", "测试此端点", "创建 e2e-spec" | **编写** | `workflows/writing/workflow.md` |
| "审查端到端测试", "检查测试质量", "审计测试", "这个测试正确吗?" | **审查** | `workflows/review/workflow.md` |
| "运行端到端测试", "执行测试", "启动 docker 和测试", "检查测试是否通过" | **运行** | `workflows/running/workflow.md` |
| "修复端到端测试", "调试测试", "测试正在失败", "间歇性失败", "连接错误" | **调试** | `workflows/debugging/workflow.md` |
| "加速端到端测试", "优化测试", "测试很慢", "减少测试时间" | **优化** | `workflows/optimize/workflow.md` |

### 工作流程执行协议

1. **始终首先加载工作流程文件** - 在采取行动之前阅读完整的工作流程
2. **按顺序遵循每个步骤** - 在继续之前完成检查点
3. **按指示加载知识文件** - 每个工作流程指定要读取的 `references/` 文件
4. **完成后验证合规性** - 重新阅读相关参考文件以确保质量

**重要提示**：每个工作流程都包含在完成任务之前和之后加载相关知识的说明，这些知识来自 `references/` 文件夹。

---

## 知识库结构

```
references/
├── common/              # 共享的测试基础知识
│   ├── knowledge.md     # 核心端到端概念和测试金字塔
│   ├── rules.md         # 强制执行的测试规则 (GWT, 超时, 日志记录)
│   ├── best-practices.md # 测试设计和清理模式
│   ├── test-case-creation-guide.md # 所有场景的 GWT 模板
│   ├── nestjs-setup.md  # NestJS 应用启动和 Jest 配置
│   ├── debugging.md     # VS Code 配置和日志分析
│   └── examples.md      # 按类别划分的综合示例
│
├── kafka/               # Kafka 特定的测试
│   ├── knowledge.md     # 为什么常见方法失败，架构
│   ├── rules.md         # Kafka 特定的测试规则
│   ├── test-helper.md   # KafkaTestHelper 实现
│   ├── docker-setup.md  # Redpanda/Kafka Docker 配置
│   ├── performance.md   # 优化技术
│   ├── isolation.md     # 预订阅模式细节
│   └── examples.md      # Kafka 测试示例
│
├── postgres/            # PostgreSQL 特定的测试
│   ├── knowledge.md     # PostgreSQL 测试概念
│   ├── rules.md         # 清理，事务，断言规则
│   ├── test-helper.md   # PostgresTestHelper 实现
│   └── examples.md      # CRUD，事务，约束示例
│
├── mongodb/             # MongoDB 特定的测试
│   ├── knowledge.md     # MongoDB 测试概念
│   ├── rules.md         # 文档清理和断言规则
│   ├── test-helper.md   # MongoDbTestHelper 实现
│   ├── docker-setup.md  # Docker 和内存服务器设置
│   └── examples.md      # 文档和聚合示例
│
├── redis/               # Redis 特定的测试
│   ├── knowledge.md     # Redis 测试概念
│   ├── rules.md         # TTL 和发布/订阅规则
│   ├── test-helper.md   # RedisTestHelper 实现
│   ├── docker-setup.md  # Docker 配置
│   └── examples.md      # 缓存，会话，速率限制示例
│
└── api/                 # API 测试 (REST, GraphQL, gRPC)
    ├── knowledge.md     # API 测试概念
    ├── rules.md         # 请求/响应断言规则
    ├── test-helper.md   # Auth 和 Supertest 辅助工具
    ├── examples.md      # REST, GraphQL, 验证示例
    └── mocking.md       # MSW 和 Nock 外部 API 模拟
```

## 按任务快速参考

> **提示**：对于详细的分步指导，请使用上方 [工作流程](#workflows) 部分。

### 设置新的端到端结构
**工作流程**：[设置端到端测试](workflows/setup/workflow.md)
1. 阅读 `references/common/knowledge.md` - 了解端到端基础知识
2. 阅读 `references/common/nestjs-setup.md` - 项目设置
3. 根据需要阅读技术特定的 `docker-setup.md` 文件

### 编写测试用例
**工作流程**：[编写端到端测试](workflows/writing/workflow.md)
1. **强制**：阅读 `references/common/rules.md` - GWT 模式，超时
2. 阅读 `references/common/test-case-creation-guide.md` - 模板
3. 阅读 技术特定文件：
   - **Kafka**：`references/kafka/knowledge.md` → `test-helper.md` → `isolation.md`
   - **PostgreSQL**：`references/postgres/rules.md` → `test-helper.md`
   - **MongoDB**：`references/mongodb/rules.md` → `test-helper.md`
   - **Redis**：`references/redis/rules.md` → `test-helper.md`
   - **API**：`references/api/rules.md` → `test-helper.md`

### 审查测试质量
**工作流程**：[审查端到端测试](workflows/review/workflow.md)
1. 阅读 `references/common/rules.md` - 检查强制模式
2. 阅读 `references/common/best-practices.md` - 质量标准
3. 阅读 技术特定的 `rules.md` 文件

### 运行端到端测试
**工作流程**：[运行端到端测试](workflows/running/workflow.md)
1. 验证 Docker 基础设施正在运行
2. 顺序运行测试：`npm run test:e2e > /tmp/e2e-${E2E_SESSION}-output.log 2>&1`
3. 如果测试失败，请遵循失败协议

### 调试失败的测试
**工作流程**：[调试端到端测试](workflows/debugging/workflow.md)
1. 阅读 `references/common/debugging.md`
2. 创建 `/tmp/e2e-${E2E_SESSION}-failures.md` 跟踪文件
3. 一次修复一个测试

### 优化测试性能
**工作流程**：[优化端到端测试](workflows/optimize/workflow.md)
1. 阅读 `references/common/best-practices.md` - 性能模式
2. 阅读 `references/kafka/performance.md` 用于 Kafka 测试
3. 在进行更改之前测量基线

### 示例
- 阅读 `references/common/examples.md` 获取一般模式
- 阅读 技术特定的 `examples.md` 获取详细场景

---

## 核心原则

### 0. 上下文效率（临时文件输出）
**始终将端到端测试输出重定向到临时文件，而不是控制台**。端到端输出很冗长，会占用代理上下文空间。

**重要提示**：仅将输出重定向到临时文件（无控制台输出）。使用唯一会话 ID 以防止冲突。

```bash
# 在调试会话开始时生成唯一会话 ID
export E2E_SESSION=$(date +%s)-$$

# 标准模式 - 仅重定向到文件（无控制台输出）
npm run test:e2e > /tmp/e2e-${E2E_SESSION}-output.log 2>&1

# 仅读取摘要（最后 50 行）
tail -50 /tmp/e2e-${E2E_SESSION}-output.log

# 获取失败详细信息
grep -B 2 -A 15 "FAIL\|✕" /tmp/e2e-${E2E_SESSION}-output.log

# 完成后清理
rm -f /tmp/e2e-${E2E_SESSION}-*.log /tmp/e2e-${E2E_SESSION}-*.md
```

**临时文件**（每个代理使用 `${E2E_SESSION}` 唯一标识）：
- `/tmp/e2e-${E2E_SESSION}-output.log` - 完整的测试输出
- `/tmp/e2e-${E2E_SESSION}-failures.log` - 过滤的失败输出
- `/tmp/e2e-${E2E_SESSION}-failures.md` - 用于逐个修复的跟踪文件
- `/tmp/e2e-${E2E_SESSION}-debug.log` - 调试运行
- `/tmp/e2e-${E2E_SESSION}-verify.log` - 验证运行

### 1. 真实基础设施
通过 Docker 对实际服务进行测试。永远不要对端到端测试模拟数据库或消息代理。

### 2. GWT 模式（强制）
所有端到端测试必须遵循 Given-When-Then：
```typescript
it('应该创建用户并返回 201', async () => {
  // 给定：有效的用户数据
  const userData = { email: 'test@example.com', name: 'Test' };

  // 当：创建用户
  const response = await request(httpServer)
    .post('/users')
    .send(userData)
    .expect(201);

  // 那么：用户使用正确数据创建
  expect(response.body.data.email).toBe('test@example.com');
});
```

### 3. 测试隔离
每个测试必须独立：
- 在 `beforeEach` 中清理数据库状态
- 使用唯一标识符（消费者组，主题）
- 等待异步操作完成

### 4. 具体断言
断言确切值，而不仅仅是存在：
```typescript
// 错误
expect(response.body.data).toBeDefined();

// 正确
expect(response.body).toMatchObject({
  code: 'SUCCESS',
  data: { email: 'test@example.com', name: 'Test' }
});
```

---

## 项目结构

```
project-root/
├── src/
├── test/
│   ├── e2e/
│   │   ├── feature.e2e-spec.ts
│   │   ├── setup.ts
│   │   └── helpers/
│   │       ├── test-app.helper.ts
│   │       ├── postgres.helper.ts
│   │       ├── mongodb.helper.ts
│   │       ├── redis.helper.ts
│   │       └── kafka.helper.ts
│   └── jest-e2e.config.ts
├── docker-compose.e2e.yml
├── .env.e2e
└── package.json
```

---

## 基本的 Jest 配置

```typescript
// test/jest-e2e.config.ts
const config: Config = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  testMatch: ['**/*.e2e-spec.ts'],
  testTimeout: 25000,
  maxWorkers: 1,           // 关键：顺序执行
  clearMocks: true,
  forceExit: true,
  detectOpenHandles: true,
};
```

---

## 技术特定超时

| 技术 | 等待时间 | 策略 |
|------------|-----------|----------|
| Kafka | 最大 10-20s（轮询） | 智能轮询，间隔 50ms |
| PostgreSQL | <1s | 直接查询 |
| MongoDB | <1s | 直接查询 |
| Redis | <100ms | 内存操作 |
| 外部 API | 1-5s | 网络延迟 |

---

## 失败解决协议

**关键**：一次修复一个测试。永远不要在修复时重复运行完整套件。

当端到端测试失败时：

1. **初始化会话**（启动时一次）：
   ```bash
   export E2E_SESSION=$(date +%s)-$$
   ```
2. **创建跟踪文件**：`/tmp/e2e-${E2E_SESSION}-failures.md` 包含所有失败的测试
3. **选择一个失败的测试** - 仅处理此测试
4. **仅运行该测试**（从不运行完整套件）：
   ```bash
   npm run test:e2e -- -t "test name" > /tmp/e2e-${E2E_SESSION}-debug.log 2>&1 && tail -50 /tmp/e2e-${E2E_SESSION}-debug.log
   ```
5. **修复问题** - 分析错误，进行针对性修复
6. **验证修复** - 运行相同测试 3-5 次：
   ```bash
   for i in {1..5}; do npm run test:e2e -- -t "test name" > /tmp/e2e-${E2E_SESSION}-run$i.log 2>&1 && echo "运行 $i: PASS" || echo "运行 $i: FAIL"; done
   ```
7. **标记为已修复** 在跟踪文件中
8. **移至下一个失败的测试** - 重复步骤 3-7
9. **仅运行完整套件一次** 在所有单个测试通过后
10. **清理**：`rm -f /tmp/e2e-${E2E_SESSION}-*.log /tmp/e2e-${E2E_SESSION}-*.md`

**原因**：运行完整套件浪费时间并污染上下文。每个失败的测试都会使输出复杂化，使调试更困难。

---

## 常见模式

### 数据库清理（PostgreSQL/MongoDB）
```typescript
beforeEach(async () => {
  await new Promise(r => setTimeout(r, 500)); // 等待进行中
  await repository.clear();  // PostgreSQL
  // 或
  await model.deleteMany({}); // MongoDB
});
```

### Kafka 测试辅助工具模式
```typescript
// 使用预订阅 + 缓冲区清除（不使用 fromBeginning: true）
const kafkaHelper = new KafkaTestHelper();
await kafkaHelper.subscribeToTopic(outputTopic, false);
// 在 beforeEach 中：kafkaHelper.clearMessages(outputTopic);
```

### Redis 清理
```typescript
beforeEach(async () => {
  await redis.flushdb();
});
```

### 外部 API 模拟（MSW）
```typescript
mockServer.use(
  http.post('https://api.external.com/endpoint', () => {
    return HttpResponse.json({ status: 'success' });
  })
);
```

### 异步事件验证（Kafka）
```typescript
// 使用智能轮询而不是固定等待
await kafkaHelper.publishEvent(inputTopic, event, event.id);
const messages = await kafkaHelper.waitForMessages(outputTopic, 1, 20000);
expect(messages[0].value).toMatchObject({ id: event.id });
```

---

## 调试命令

**所有命令仅将输出重定向到临时文件（无控制台输出）。**

```bash
# 初始化会话（启动时一次）
export E2E_SESSION=$(date +%s)-$$

# 运行特定测试（无控制台输出）
npm run test:e2e -- -t "should create user" > /tmp/e2e-${E2E_SESSION}-output.log 2>&1 && tail -50 /tmp/e2e-${E2E_SESSION}-output.log

# 运行特定文件
npm run test:e2e -- test/e2e/user.e2e-spec.ts > /tmp/e2e-${E2E_SESSION}-output.log 2>&1 && tail -50 /tmp/e2e-${E2E_SESSION}-output.log

# 运行完整套件
npm run test:e2e > /tmp/e2e-${E2E_SESSION}-output.log 2>&1 && tail -50 /tmp/e2e-${E2E_SESSION}-output.log

# 从上次运行获取失败详细信息
grep -B 2 -A 15 "FAIL\|✕" /tmp/e2e-${E2E_SESSION}-output.log

# 使用断点调试（需要控制台进行交互式调试）
node --inspect-brk node_modules/.bin/jest --config test/jest-e2e.config.ts --runInBand

# 查看应用日志（有限）
tail -100 logs/e2e-test.log
grep -i error logs/e2e-test.log | tail -50

# 清理会话文件
rm -f /tmp/e2e-${E2E_SESSION}-*.log /tmp/e2e-${E2E_SESSION}-*.md
```

---

## 应避免的反模式

1. **多个 WHEN 动作** - 分成单独的测试
2. **条件断言** - 创建确定性测试用例
3. **测试之间共享状态** - 在 beforeEach 中清理
4. **模拟数据库** - 使用真实连接
5. **跳过清理** - 在之前和之后始终清理
6. **同时修复多个测试** - 一次修复一个
7. **通用断言** - 断言具体值
8. **Kafka 的 fromBeginning: true** - 使用预订阅 + 缓冲区清除
