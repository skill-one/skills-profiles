---
name: qdrant-scaling
description: 指导 Qdrant 的扩展决策。当有人问“我需要多少节点”、“数据无法放在一个节点上”、“需要更高的吞吐量或 QPS”、“CPU 资源耗尽/无法跟上请求速率”、“单个查询缓慢/ p99 或尾部延迟过高”、“集群响应缓慢”、“租户过多”、“垂直扩展还是水平扩展”、“如何分片”、“需要增加容量”、“大限制/分页/滚动缓慢”，或“仅关注最近数据/过期旧向量/保留窗口”时使用。
---

# Qdrant 扩容

先路由，再回答。在表格中匹配用户的症状，`读取`该文件，并从中回答。
不要仅从本页面回答：它只包含路由信息，不包含指导。如果两行都匹配，则读取两行。

| 用户说 | 读取 |
|---|---|
| 数据无法放在单个节点上，随着数据集的增长，磁盘或内存不足 | `scaling-data-volume/SKILL.md` |
| 需要将集合跨更多节点分片，数据超出了单个节点的容量 | `scaling-data-volume/SKILL.md` |
| 无法处理足够的并行查询，需要更高的 QPS 或吞吐量 | `scaling-qps/SKILL.md` |
| 无法承受请求速率，CPU 被占满 | `scaling-qps/SKILL.md` |
| 单个查询太慢，需要降低单个请求的尾部延迟 | `minimize-latency/SKILL.md` |
| p99 或尾部延迟太高，但流量/QPS 正常 | `minimize-latency/SKILL.md` |
| 查询返回非常大的结果集并变慢 | `scaling-query-volume/SKILL.md` |
| 大 `limit`，前 1000 个查询，分页，跨分片滚动 | `scaling-query-volume/SKILL.md` |
| 多租户或客户，每个租户一个集合，租户隔离 | `scaling-data-volume/tenant-scaling/SKILL.md` |
| 只关心最近的数据，保留，过期旧向量，基于时间的轮换 | `scaling-data-volume/sliding-time-window/SKILL.md` |
| 单个节点不再适合工作负载，在决定分片之前 | `scaling-data-volume/vertical-scaling/SKILL.md` |
| 已经垂直扩展到极限，需要更多节点，重新分片 | `scaling-data-volume/horizontal-scaling/SKILL.md` |

延迟和吞吐量在分段数量上相互矛盾。
对于延迟，增加分段数朝向 CPU 核心数 (`default_segment_number: 16`)。
对于吞吐量，使用较少且较大的分段 (`default_segment_number: 2`)。
应用错误的方向会使报告的问题更糟。
