# Redis 核心

关于在 Redis 中建模数据的指导性基础。涵盖数据类型选择和键名约定——这两个决策最直接地影响内存、性能和可维护性。

## 应用场景

- 缓存对象、会话或用户状态。
- 计数器、排行榜、最近项目列表、唯一成员集合。
- 审查或重构 Redis 键名。
- 决定实体使用 Redis Hash 还是 JSON 文档。

## 1. 选择合适的数据结构

选择与 *访问模式* 匹配的类型，而不仅仅是数据形状。

| 使用场景 | 推荐类型 | 原因 |
|---|---|---|
| 简单值、计数器 | 字符串 | 原子 `INCR`/`DECR`, `SET`/`GET` |
| 具有独立更新字段的对象 | Hash | 按字段读取/写入，无需重写整个对象 |
| 队列、最近 N 个项目 | 列表 | 两端 O(1) 推入/弹出 |
| 唯一项目、成员检查 | 集合 | O(1) `SADD`/`SISMEMBER`/`SCARD` |
| 排名、基于分数的范围 | 有序集合 | 分数排序；`ZADD`/`ZRANGE`/`ZRANK` |
| 嵌套/层次化数据 | JSON | 路径级更新、嵌套数组、RQE 索引 |
| 事件日志、扇出消息 | 流 | 持久化、消费者组 |
| 向量相似度 | 向量集合 | 本地向量存储与 HNSW |

**常见反模式：** 将扁平对象塞入序列化字符串。更新一个字段意味着获取 + 解析 + 修改 + 重写。使用 Hash 代替。

参见 [references/choose-data-structure.md](references/choose-data-structure.md) 获取完整理由和 Python/Java 示例。

## 2. 使用一致的键名

使用 `冒号分隔` 的段，并保持稳定的层次结构：

```
{实体}:{id}:{属性}
user:1001:profile
user:1001:settings
order:2024:items
session:abc123
article:987:likes
game:space-invaders:leaderboard
```

经验法则：

- **小写、冒号分隔。** 无空格，无混合大小写 (`User_1001_Profile` 是错误的)。
- **保持键简短但可读** — 键存储在内存中，并在每个命令中显示。
- **不要使用完整 URL 或长字符串作为键。** 提取简短标识符，或使用 URL 的哈希摘要。
- **多租户前缀** (`tenant:42:user:7:cart`) 以便扫描和 ACL 可以干净地定位租户。
- **保持一致性。** 每个服务选择一种约定，并应用于所有键。

参见 [references/key-naming.md](references/key-naming.md) 获取清理示例和边缘情况。

## 参考文献

- [Redis：选择合适的数据类型](https://redis.io/docs/latest/develop/data-types/compare-data-types/)
- [Redis：键](https://redis.io/docs/latest/develop/use/keyspace/)
