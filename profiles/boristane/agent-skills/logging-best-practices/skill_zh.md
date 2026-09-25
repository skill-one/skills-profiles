# 日志最佳实践技能

版本：1.0.0

## 目的

本技能提供了关于在应用程序中实现有效日志记录的指南。它重点关注**宽事件**（也称为规范日志行）——一种模式，即每个服务对每个请求发出一个上下文丰富的单一事件，从而实现强大的调试和分析。

## 何时应用

在以下情况下应用这些指南：
- 编写或审查日志记录代码
- 添加 console.log、logger.info 或类似内容
- 设计新服务的日志记录策略
- 设置日志记录基础设施

## 核心原则

### 1. 宽事件（关键）

每个服务对每个请求发出**一个上下文丰富的单一事件**。不要在处理程序中分散日志行，而应将所有内容合并为一个结构化事件，在请求完成时发出。

```typescript
const wideEvent: Record<string, unknown> = {
  method: 'POST',
  path: '/checkout',
  requestId: c.get('requestId'),
  timestamp: new Date().toISOString(),
};

try {
  const user = await getUser(c.get('userId'));
  wideEvent.user = { id: user.id, subscription: user.subscription };

  const cart = await getCart(user.id);
  wideEvent.cart = { total_cents: cart.total, item_count: cart.items.length };

  wideEvent.status_code = 200;
  wideEvent.outcome = 'success';
  return c.json({ success: true });
} catch (error) {
  wideEvent.status_code = 500;
  wideEvent.outcome = 'error';
  wideEvent.error = { message: error.message, type: error.name };
  throw error;
} finally {
  wideEvent.duration_ms = Date.now() - startTime;
  logger.info(wideEvent);
}
```

### 2. 高基数与高维度（关键）

包含具有高基数（用户ID、请求ID——数百万个唯一值）和高维度（每个事件包含许多字段）的字段。这能够按特定用户进行查询，并回答您尚未预料到的问题。

### 3. 业务上下文（关键）

始终包含业务上下文：用户订阅级别、购物车价值、功能标志、账户年龄。目标是知道“一位高级别客户无法完成2,499美元的购买”，而不仅仅是“结账失败”。

### 4. 环境特征（关键）

在每个事件中包含环境和部署信息：提交哈希、服务版本、区域、实例ID。这能够将问题与部署相关联，并识别区域特定的问题。

### 5. 单一日志记录器（高）

使用一个在启动时配置的日志记录器实例，并在所有地方导入它。这确保了格式的一致性和自动环境上下文。

### 6. 中间件模式（高）

使用中间件来处理宽事件基础设施（时间、状态、环境、发出）。处理程序应仅添加业务上下文。

### 7. 结构与一致性（高）
- 一致使用 JSON 格式
- 在不同服务中保持字段名称的一致性
- 简化为两个日志级别：`info` 和 `error`
- 永远不要记录非结构化字符串

## 应避免的反模式

1. **分散的日志**：每个请求多个 console.log() 调用
2. **多个日志记录器**：不同文件中的不同日志记录器实例
3. **缺少环境上下文**：没有提交哈希或部署信息
4. **缺少业务上下文**：没有用户/业务数据记录技术细节
5. **非结构化字符串**：`console.log('something happened')` 而不是结构化数据
6. **不一致的架构**：不同服务中的不同字段名称

## 指南

### 宽事件 (`rules/wide-events.md`)
- 每个服务跳转发出一个宽事件
- 包含所有相关上下文
- 使用请求ID连接事件
- 在请求完成时在 finally 块中发出

### 上下文 (`rules/context.md`)
- 支持高基数字段（user_id、request_id）
- 包含高维度（许多字段）
- 始终包含业务上下文
- 始终包含环境特征（commit_hash、version、region）

### 结构 (`rules/structure.md`)
- 在整个代码库中使用单一日志记录器
- 使用中间件实现一致的宽事件
- 使用 JSON 格式
- 保持一致的架构
- 简化为 info 和 error 级别
- 永远不要记录非结构化字符串

### 常见陷阱 (`rules/pitfalls.md`)
- 避免每个请求多个日志行
- 设计以应对未知未知
- 始终在服务间传递请求ID

参考资料：
- [Logging Sucks](https://loggingsucks.com)
- [Observability Wide Events 101](https://boristane.com/blog/observability-wide-events-101/)
- [Stripe - Canonical Log Lines](https://stripe.com/blog/canonical-log-lines)
