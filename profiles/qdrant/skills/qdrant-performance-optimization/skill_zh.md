# Qdrant 性能优化

先路由，再回答。在表格中匹配用户的症状，`读取`该文件，并从中回答。
不要仅从此页面回答：它只包含路由信息，不包含指导。如果两行都匹配，则读取两行。

| 用户说 | 读取 |
|---|---|
| 过滤查询比未过滤查询慢得多 | `search-speed-optimization/SKILL.md` |
| QPS低，无法处理查询负载 | `search-speed-optimization/SKILL.md` |
| 单个查询返回时间过长 | `search-speed-optimization/SKILL.md` |
| 索引构建或HNSW构建时间过长，向量上传慢 | `indexing-performance-optimization/SKILL.md` |
| 集合保持黄色，优化器卡住或运行时间过长 | `indexing-performance-optimization/SKILL.md` |
| 向量批量插入慢 | `indexing-performance-optimization/SKILL.md` |
| 内存使用过高，内存溢出崩溃 | `memory-usage-optimization/SKILL.md` |
| 希望在相同硬件上适配更大的数据集 | `memory-usage-optimization/SKILL.md` |
| 通过将数据移至磁盘降低成本 | `memory-usage-optimization/SKILL.md` |

分段数量对延迟和吞吐量有相反的影响。
对于延迟，增加分段数至CPU核心数（`default_segment_number: 16`）。
对于吞吐量，使用较少且较大的分段（`default_segment_number: 2`）。
应用错误的方向会使报告的问题更严重。
