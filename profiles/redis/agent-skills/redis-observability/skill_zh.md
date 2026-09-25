# Redis 可观察性

需要关注什么、运行什么以及什么情况下发出警报。涵盖了每个 Redis 部署应该监控的指标以及用于临时诊断的内置命令。

## 应用场景

- 为 Redis 实例设置监控或警报。
- 诊断 Redis 性能回归（高延迟、内存压力、连接风暴）。
- 分析慢速的 `FT.SEARCH` 或管道。
- 将 Redis 指标集成到 Prometheus、Datadog、CloudWatch 或类似系统中。

## 1. 监控这些指标

这些指标来自 `INFO` 命令，应导出到您的监控系统。

| 指标               | 它告诉您什么               | 发出警报时                 |
|--------------------|--------------------------|---------------------------|
| `used_memory`      | 当前内存使用情况           | > 80% 的 `maxmemory`      |
| `connected_clients`| 打开连接数               | 突然飙升或骤降             |
| `blocked_clients`  | 等待阻塞操作的客户端       | > 0 持续存在             |
| `instantaneous_ops_per_sec` | 当前吞吐量           | 显著下降                 |
| `keyspace_hits` / `keyspace_misses` | 缓存命中率         | 命中率 < 80%             |
| `rejected_connections` | 达到 `maxclients` 限制 | > 0                       |
| `rdb_last_save_time` | 最后持久化快照时间       | 与 RPO 相比过于陈旧       |

```python
info = redis.info()
hit_ratio = info["keyspace_hits"] / max(1, info["keyspace_hits"] + info["keyspace_misses"])
print(f"内存:    {info['used_memory_human']}")
print(f"客户端:  {info['connected_clients']}")
print(f"每秒操作: {info['instantaneous_ops_per_sec']}")
print(f"命中率:  {hit_ratio:.1%}")
```

参见 [references/metrics.md](references/metrics.md)。

## 2. 用于调试的内置命令

当出现异常情况时，请使用这些命令。

| 主题               | 命令               |
|--------------------|--------------------|
| 慢速命令           | `SLOWLOG GET 10` / `SLOWLOG LEN` / `SLOWLOG RESET` |
| 服务器快照         | `INFO all` (或 `INFO memory` / `INFO stats` / `INFO clients` / `INFO replication`) |
| 内存诊断           | `MEMORY DOCTOR` / `MEMORY STATS` / `MEMORY USAGE <key>` |
| 连接               | `CLIENT LIST` / `CLIENT INFO` |
| RQE / 搜索         | `FT.INFO <idx>` / `FT.PROFILE <idx> SEARCH QUERY "..."` |

用于事件处理的两个最有用的命令：

- **`SLOWLOG GET`** 用于查找超过 `slowlog-log-slower-than` 阈值（默认为 10ms）的查询。输出显示确切的命令和微秒级持续时间。
- **`MEMORY DOCTOR`** 用于内存压力——它返回当前内存使用情况的异常情况摘要。

```python
for entry in redis.slowlog_get(10):
    print(f"{entry['duration']}μs  {entry['command']}")
```

参见 [references/commands.md](references/commands.md)。

## 3. Redis Insight

用于交互式使用（运行查询、浏览键、分析索引），[Redis Insight](https://redis.io/insight/) 是官方的图形界面。它以可视化方式展示相同的 `SLOWLOG` / `INFO` / `FT.PROFILE` 数据，并包含 Redis Copilot 用于自然语言查询。在开发和事件响应期间非常有用；不是导出指标到监控系统的替代方案。

## 参考文献

- [Redis: 延迟监控](https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/latency/)
- [Redis Insight](https://redis.io/insight/)
