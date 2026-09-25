# Redis 连接

与 Redis 高效通信的客户端指南：如何共享连接、如何批量命令、哪些命令在生产环境中不应调用、何时启用客户端缓存，以及如何设置快速失败且不影响正常流量的超时。

## 何时应用

- 创建或审查 Redis 客户端配置（redis-py、Jedis、Lettuce、go-redis、NRedisStack）。
- 执行大量小型 Redis 调用并怀疑延迟去向。
- 迭代大型键空间、集合、哈希或列表。
- 为热键启用客户端缓存。
- 调整连接/读取/写入超时。

## 1. 连接池或复用 — 每个请求永不使用一个连接

Redis 客户端代码中最大的错误是为每个操作打开一个新的 TCP 连接。始终使用以下方式之一：

- **连接池** — 保持 N 个持久连接，应用程序每次调用时租用（redis-py `ConnectionPool`、Jedis `JedisPooled`、go-redis 客户端）。
- **复用** — 在所有请求之间共享一个连接（Lettuce、NRedisStack）。

| 模式 | 使用 | 备注 |
|---|---|---|
| 连接池 | redis-py、Jedis、go-redis | 每次租用会阻塞如果池耗尽；根据并发量调整池大小 |
| 复用 | Lettuce、NRedisStack | 单个连接；**不能**携带阻塞命令如 `BLPOP` |

```python
# redis-py — 连接池
pool = redis.ConnectionPool(host="localhost", port=6379, max_connections=50)
r = redis.Redis(connection_pool=pool)
```

有关 Python + Java + Lettuce 示例，请参阅 [references/pooling.md](references/pooling.md)。

## 2. 批量工作使用管道

对于 N 个不依赖于彼此结果的命令，使用管道将它们作为单个批次发送。一次往返而不是 N 次。

```python
pipe = redis.pipeline()
for user_id in user_ids:
    pipe.get(f"user:{user_id}")
results = pipe.execute()
```

使用**非事务性**管道以提高性能，仅在确实需要原子性时使用 `pipeline(transaction=True)`（请参阅 redis-core 的事务指南）。

请参阅 [references/pipelining.md](references/pipelining.md)。

## 3. 避免扫描所有内容的命令

任何遍历整个键空间（或整个大型容器）的操作都会阻塞服务器。使用增量变体代替。

| 避免 | 使用 |
|---|---|
| `KEYS pattern` | `SCAN` 游标循环 |
| `SMEMBERS large_set` | `SSCAN` |
| `HGETALL large_hash` | `HSCAN` |
| 在一个巨大的列表上使用 `LRANGE 0 -1` | 分页 (`LRANGE 0 100`) |

```python
cursor = 0
while True:
    cursor, keys = redis.scan(cursor, match="user:*", count=100)
    for key in keys:
        process(key)
    if cursor == 0:
        break
```

**阻塞命令（`BLPOP`、`BRPOP`、`BLMOVE`）有所不同** — 它们故意等待数据，并且适合队列消费者，但始终设置超时，并且不要在复用连接（Lettuce、NRedisStack）上发出。

请参阅 [references/blocking.md](references/blocking.md)。

## 4. 热键的客户端缓存

对于经常读取且很少写入的数据（配置、功能标志、每个请求上的会话），启用 RESP3 客户端缓存。客户端保留本地副本，服务器在写入时使其失效 — 为热读节省往返。

```python
client = redis.Redis(
    host="localhost",
    port=6379,
    protocol=3,                                    # RESP3 是必需的
    cache_config=redis.CacheConfig(max_size=1000),
)
```

对于写入密集型工作负载或经常变化的数据，请跳过 — 使失效流量超过节省。

请参阅 [references/client-cache.md](references/client-cache.md)。

## 5. 设置显式超时

默认值因客户端而异，可能过于宽松。选择与应用程序*失败模型*匹配的值：

```python
r = redis.Redis(
    host="localhost",
    socket_connect_timeout=2.0,   # 在死节点上快速失败
    socket_timeout=5.0,           # 根据预期操作时间调整
    retry_on_timeout=True,
)
```

经验法则：连接超时比读写超时短。对于延迟敏感路径使用紧密超时+重试超时；对于批量作业使用较长的超时。

请参阅 [references/timeouts.md](references/timeouts.md)。

## 参考资料

- [Redis: 连接池和复用](https://redis.io/docs/latest/develop/clients/pools-and-muxing/)
- [Redis: 管道](https://redis.io/docs/latest/develop/use/pipelining/)
- [Redis: SCAN](https://redis.io/docs/latest/commands/scan/)
- [Redis: 客户端缓存](https://redis.io/docs/latest/develop/clients/client-side-caching/)
- [Redis: 客户端](https://redis.io/docs/latest/develop/clients/)
