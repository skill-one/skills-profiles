# Qdrant 扩容

先路由，再回答。在表格中匹配用户的症状，`读取`对应的文件，并从中回答。
不要仅从本页面回答：它只包含路由信息，不包含指导。如果两行都匹配，则读取两行。

| 用户说 | 读取 |
|---|---|
| 数据无法放在单个节点上，随着数据集的增长，磁盘或内存不足 | `scaling-data-volume/SKILL.md` |
| 需要将集合跨更多节点分片，数据超出了单个节点的容量 | `scaling-data-volume/SKILL.md` |
| 无法处理足够的并行查询，需要更高的 QPS 或吞吐量 | `scaling-qps/SKILL.md` |
| 无法承受请求速率，CPU 使用率已达峰值 | `scaling-qps/SKILL.md` |
| 单个查询太慢，需要降低单个请求的尾部延迟 | `minimize-latency/SKILL.md` |
| p99 或尾部延迟过高，但流量/QPS 正常 | `minimize-latency/SKILL.md` |
| 查询返回非常大的结果集并变慢 | `scaling-query-volume/SKILL.md` |
| 大 `limit`，前 1000 个查询，分页，跨分片滚动 | `scaling-query-volume/SKILL.md` |
| 多租户或客户，每个租户一个集合，租户隔离 | `scaling-data-volume/tenant-scaling/SKILL.md` |
| 只关心最近的数据，保留数据，过期旧向量，基于时间的轮换 | `scaling-data-volume/sliding-time-window/SKILL.md` |
| 单个节点已无法满足工作负载，在决定分片之前 | `scaling-data-volume/vertical-scaling/SKILL.md` |
| 已垂直扩展到极限，需要更多节点，重新分片 | `scaling-data-volume/horizontal-scaling/SKILL.md` |

延迟和吞吐量在分段数量上朝相反的方向影响。
对于延迟，增加分段数朝向 CPU 核心数（`default_segment_number: 16`）。
对于吞吐量，使用较少且较大的分段（`default_segment_number: 2`）。
应用错误的方向会使报告的问题更糟。
