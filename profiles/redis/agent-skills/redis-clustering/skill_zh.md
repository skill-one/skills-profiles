# Redis 集群

在分片 Redis 集群（以及独立的主从复制）中设计键和路由读操作的指南。涵盖大多数新集群用户会遇到的两个故障模式：多键操作中的 `CROSSSLOT` 错误，以及主节点过载读流量。

## 适用场景

- 为 Redis 集群部署设计键。
- 调试 `MGET`、`SDIFF`、事务或管道中的 `CROSSSLOT` 错误。
- 实现涉及多个键的事务/Lua 脚本。
- 在不增加分片的情况下扩展读流量。

## 1. 多键操作的哈希标签

Redis 集群通过哈希键名将键分布到 16,384 个槽位。任何操作**多个键**的命令（`MGET`、`SDIFF`、`SUNIONSTORE`、事务、管道、具有多个 `KEYS[]` 的 Lua 脚本）都需要所有键位于**同一个槽位**——否则服务器会返回 `CROSSSLOT` 错误。

哈希标签强制执行此规则：`{` 和 `}` 之间的部分是用于槽位分配的唯一哈希内容，因此共享哈希标签的两个键总是会一起分配到同一个槽位。

```python
# 同一个槽位——多键操作有效
redis.set("{user:1001}:profile",  "...")
redis.set("{user:1001}:settings", "...")
redis.lmove("{user:1001}:pending", "{user:1001}:processed", "LEFT", "RIGHT")
```

```python
# 不同键，无哈希标签——集群模式下多键命令出现 CROSSSLOT 错误
redis.set("user:1001:profile",  "...")
redis.set("user:1001:settings", "...")
pipe = redis.pipeline()
pipe.get("user:1001:profile")
pipe.get("user:1001:settings")
pipe.execute()  # 集群模式下出现 CROSSSLOT 错误
```

经验法则：

- **使用针对有意义的实体的标签**，例如 `{user:1001}`。避免使用裸标签 `{1001}`——不相关的命名空间（`purchase:{1001}`、`employee:{1001}`）都会碰撞到同一个槽位。
- **仅在确实需要多键操作的地方添加标签**。给所有键添加标签会创建热点，并违背分片的目的。
- 对于哈希标签键的单键命令可以正常工作，因此添加标签是渐进式的——但生产环境中重命名键很痛苦，因此应提前规划对实体进行分组的标签。

参见 [references/hash-tags.md](references/hash-tags.md)。

## 2. 读副本用于读密集型工作负载

如果读操作主导写操作，将读操作路由到副本以释放主节点的容量。在 Redis 集群（每个分片有 1+ 个副本）和独立的**主从复制**中都有效。

```python
# Redis 集群：在客户端启用副本读
from redis.cluster import RedisCluster

rc = RedisCluster(host="localhost", port=6379, read_from_replicas=True)
rc.set("key", "value")     # → 主节点
value = rc.get("key")       # → 可能由副本提供服务
```

对于非集群设置，将两个客户端指向正确的节点：

```python
primary = Redis(host="primary-host", port=6379)
replica = Redis(host="replica-host", port=6379)
primary.set("key", "value")
value = replica.get("key")
```

权衡点是一致性：**副本是最终一致性**的。不要从副本读取自己的写操作；不要使用副本读进行需要严格新鲜度的操作（财务余额、幂等状态）。良好匹配：缓存层、分析、仪表板、推荐流。

参见 [references/read-replicas.md](references/read-replicas.md)。

## 参考文献

- [Redis 集群规范 — 哈希标签](https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/#hash-tags)
- [Redis：集群中的多键操作](https://redis.io/docs/latest/operate/rs/databases/durability-ha/clustering/#multikey-operations)
- [Redis：复制](https://redis.io/docs/latest/operate/oss_and_stack/management/replication/)
