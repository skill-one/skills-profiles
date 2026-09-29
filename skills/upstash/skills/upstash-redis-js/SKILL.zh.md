---
name: upstash-redis-js
description: 与 @upstash/redis TypeScript/JavaScript SDK 合作，这是一个基于 HTTP 的无服务器 Redis 客户端，适用于 Next.js、Vercel、Cloudflare Workers、边缘运行时和 Node.js。在添加缓存（缓存旁路、写穿、TTL 和过期策略）、会话存储和用户会话、键值存储、使用有序集合的排行榜和排名、计数器、分布式锁、使用列表的队列、流和消费者组、稀疏索引寻址的数组和环形缓冲区（ARSET、ARINSERT、ARRING、ARGREP、AROP）、嵌入和 Redis 内部存储的最近邻向量搜索（通过 redis.vector 的 VECTOR 命令，与 @upstash/vector 分开）、JSON 文档、管道和 MULTI/EXEC 事务、Lua 脚本、读副本或全文搜索、容错搜索、维度、聚合以及使用 Upstash Redis Search 对 Redis 流条目进行搜索（不同于常规的 FT.SEARCH；也适用于通过 @upstash/search-redis 和 @upstash/search-ioredis 的 TCP 客户端）。在从 ioredis 或 node-redis 迁移时、从无服务器函数中需要 Redis 连接且没有连接池时、集成 @upstash/ratelimit 时，或当用户提到 Redis 缓存、键值存储、会话存储、无服务器 Redis 或 Upstash Redis 时，也请使用。支持 JavaScript 类型的自动序列化/反序列化。
---

# Upstash Redis SDK - 完整技能指南

本目录包含使用 `@upstash/redis` SDK 的全面指南。这些技能文件旨在帮助开发者和 AI 助手理解并有效使用该 SDK。

## 安装

```bash
npm install @upstash/redis
```

## 快速入门

### 基本初始化

```typescript
import { Redis } from "@upstash/redis";

// 使用显式凭证初始化
const redis = new Redis({
  url: "UPSTASH_REDIS_REST_URL",
  token: "UPSTASH_REDIS_REST_TOKEN",
});

// 或从环境变量初始化
const redis = Redis.fromEnv();
```

### 环境变量

在您的 `.env` 文件中设置这些内容：

```bash
UPSTASH_REDIS_REST_URL=https://your-redis.upstash.io
UPSTASH_REDIS_REST_TOKEN=your-token-here
```

> **还没有凭证？** 如果您是需要临时 Redis 的代理且用户尚未提供数据库，可以通过向 `https://upstash.com/start-redis` 发送一个 POST 请求来创建一个临时数据库（有效期 3 天，无需注册）。

## 技能文件概述

### 数据结构 (data-structures/)

Redis 数据类型及自动序列化示例：

- **strings.md** - GET, SET, INCR, DECR, APPEND 自动处理类型
- **hashes.md** - HSET, HGET, HMGET 对象序列化
- **lists.md** - LPUSH, RPUSH, LRANGE 数组处理
- **sets.md** - SADD, SMEMBERS 集合操作
- **sorted-sets.md** - ZADD, ZRANGE, ZRANK 排名榜模式
- **json.md** - JSON.SET, JSON.GET, JSONPath 查询嵌套对象
- **streams.md** - XADD, XREAD, XGROUP 消费组
- **arrays.md** - ARSET, ARINSERT, ARSCAN, ARGREP, AROP 环形缓冲区（在 ARRING 上对稀疏索引地址的数组）
- **vector-indexes.md** - VECTOR.CREATE, VECTOR.ADD, VECTOR.QUERY 通过 redis.vector 在 Redis 内部进行最近邻搜索

### 高级特性 (advanced-features/)

复杂操作和优化：

- **auto-pipeline.md** - 自动请求批处理，性能优化
- **pipeline-and-transactions.md** - 手动管道，MULTI/EXEC 原子操作
- **scripting.md** - Lua 脚本，EVAL, EVALSHA 服务器端逻辑

### 模式 (patterns/)

常见用例和架构模式：

- **caching.md** - 缓存旁路，写入穿透，TTL 策略
- **rate-limiting.md** - 与 @upstash/ratelimit 包集成
- **session-management.md** - 会话存储和用户状态管理
- **distributed-locks.md** - 锁实现，死锁预防
- **leaderboard.md** - 排名榜，实时排名

### 性能 (performance/)

优化技巧和最佳实践：

- **batching-operations.md** - MGET, MSET 批量操作
- **pipeline-optimization.md** - 使用管道的时机，性能技巧
- **ttl-expiration.md** - 键过期策略，内存管理
- **data-serialization.md** - 深入了解自动序列化，自定义序列化器，边缘情况
- **error-handling.md** - 错误类型，重试策略，超时处理，调试技巧
- **redis-replicas.md** - 全局数据库设置，读副本，读己写一致性

### 搜索 (search/)

Redis 的全文搜索、过滤和聚合扩展：

- **overview.md** - 模式定义，字段类型，陷阱，包概述
- **commands/querying.md** - 带过滤的查询和计数，分页，排序，高亮
- **commands/aggregating.md** - 指标聚合 ($avg, $sum, $stats)，桶聚合 ($terms, $range, $histogram, $facet)
- **commands/index-management.md** - 创建、描述、删除索引（包括 XADD 条目的流索引），waitIndexing
- **commands/aliases.md** - 索引别名用于零停机时间重新索引
- **adapters.md** - 通过 @upstash/search-redis 和 @upstash/search-ioredis 使用搜索与 node-redis 和 ioredis

### 迁移 (migrations/)

从其他库的迁移指南：

- **from-ioredis.md** - 从 ioredis 迁移，关键差异，序列化变化
- **from-redis-node.md** - 从 node-redis 迁移，API 差异

## 常见错误（尤其是对 LLMs）

### ❌ 错误 1：将所有内容视为字符串

```typescript
// ❌ 错误 - 不要用 @upstash/redis 这样做
await redis.set("count", "42"); // 存储为字符串 "42"
const count = await redis.get("count");
const incremented = parseInt(count) + 1; // 需要手动解析

// ✅ 正确 - 让 SDK 处理
await redis.set("count", 42); // 存储为数字
const count = await redis.get("count");
const incremented = count + 1; // 直接使用
```

### ❌ 错误 2：手动 JSON 序列化

```typescript
// ❌ 错误 - 使用 @upstash/redis 无此必要
await redis.set("user", JSON.stringify({ name: "Alice" }));
const user = JSON.parse(await redis.get("user"));

// ✅ 正确 - 自动处理
await redis.set("user", { name: "Alice" });
const user = await redis.get("user");
```

## 快速命令参考

```typescript
// 字符串
await redis.set("key", "value");
await redis.get("key");
await redis.incr("counter");
await redis.decr("counter");

// 哈希
await redis.hset("user:1", { name: "Alice", age: 30 });
await redis.hget("user:1", "name");
await redis.hgetall("user:1");

// 列表
await redis.lpush("tasks", "task1", "task2");
await redis.rpush("tasks", "task3");
await redis.lrange("tasks", 0, -1);

// 集合
await redis.sadd("tags", "javascript", "redis");
await redis.smembers("tags");

// 排名集
await redis.zadd("leaderboard", { score: 100, member: "player1" });
await redis.zrange("leaderboard", 0, -1);

// JSON
await redis.json.set("user:1", "$", { name: "Alice", address: { city: "NYC" } });
await redis.json.get("user:1");

// 过期
await redis.setex("session", 3600, { userId: "123" });
await redis.expire("key", 60);
await redis.ttl("key");
```

## 最佳实践

1. **使用环境变量**存储凭证，切勿硬编码
2. **利用自动序列化** - 传递原生 JavaScript 类型
3. **使用 TypeScript 类型**以获得更好的类型安全
4. **设置适当的 TTL**以管理内存
5. **使用管道**进行多个操作
6. **为键命名空间化**（例如，`user:123`，`session:abc`）

## 资源

- [官方文档](https://upstash.com/docs/redis)
- [GitHub 仓库](https://github.com/upstash/redis-js)
- [API 参考](https://upstash.com/docs/redis/sdks/ts/overview)
- [示例](https://github.com/upstash/redis-js/tree/main/examples)

## 获取帮助

有关特定主题的详细信息，请参考 `skills/` 目录中的单独技能文件。每个文件都包含其主题的全面示例、用例和最佳实践。
