# Redis 最佳实践

一份全面的 Redis 性能优化指南，涵盖 Redis 查询引擎、向量搜索和语义缓存。包含 11 个类别中的 29 条规则，按影响程度排序，以指导自动化优化和代码生成。

## 应用场景

在以下情况下参考这些指南：
- 设计 Redis 数据模型和键结构
- 实现缓存、会话或实时功能
- 使用 Redis 查询引擎（FT.CREATE、FT.SEARCH、FT.AGGREGATE）
- 使用 RedisVL 构建向量搜索或 RAG 应用
- 使用 LangCache 实现语义缓存
- 优化 Redis 性能和内存使用

## 按优先级排序的规则类别

| 优先级 | 类别 | 影响 | 前缀 |
|--------|------|------|------|
| 1 | 数据结构 & 键 | 高 | `data-` |
| 2 | 内存 & 过期 | 高 | `ram-` |
| 3 | 连接 & 性能 | 高 | `conn-` |
| 4 | JSON 文档 | 中 | `json-` |
| 5 | Redis 查询引擎 | 高 | `rqe-` |
| 6 | 向量搜索 & RedisVL | 高 | `vector-` |
| 7 | 语义缓存 | 中 | `semantic-cache-` |
| 8 | 流 & 发布/订阅 | 中 | `stream-` |
| 9 | 集群 & 复制 | 中 | `cluster-` |
| 10 | 安全 | 高 | `security-` |
| 11 | 可观测性 | 中 | `observe-` |

## 快速参考

### 1. 数据结构 & 键（高）

- `data-choose-structure` - 选择合适的数据结构
- `data-key-naming` - 使用一致的键命名规范

### 2. 内存 & 过期（高）

- `ram-limits` - 配置内存限制和驱逐策略
- `ram-ttl` - 对缓存键设置 TTL

### 3. 连接 & 性能（高）

- `conn-blocking` - 避免在生产环境中使用慢速命令
- `conn-pipelining` - 使用管道化进行批量操作
- `conn-pooling` - 使用连接池或复用
- `conn-timeouts` - 配置连接超时

### 4. JSON 文档（中）

- `json-partial-updates` - 使用 JSON 路径进行部分更新
- `json-vs-hash` - 合适地选择 JSON vs 哈希

### 5. Redis 查询引擎（高）

- `rqe-dialect` - 使用 DIALECT 2 进行查询语法
- `rqe-field-types` - 选择正确的字段类型
- `rqe-index-creation` - 仅索引你查询的字段
- `rqe-index-management` - 管理索引以实现零停机更新
- `rqe-query-optimization` - 编写高效的查询

### 6. 向量搜索 & RedisVL（高）

- `vector-algorithm-choice` - 根据需求选择 HNSW vs FLAT
- `vector-hybrid-search` - 使用混合搜索获得更好的结果
- `vector-index-creation` - 正确配置向量索引
- `vector-rag-pattern` - 正确实现 RAG 模式

### 7. 语义缓存（中）

- `semantic-cache-best-practices` - 正确配置语义缓存
- `semantic-cache-langcache-usage` - 使用 LangCache 缓存 LLM 响应

### 8. 流 & 发布/订阅（中）

- `stream-choosing-pattern` - 合适地选择流 vs 发布/订阅

### 9. 集群 & 复制（中）

- `cluster-hash-tags` - 使用哈希标签进行多键操作
- `cluster-read-replicas` - 使用读副本处理读密集型工作负载

### 10. 安全（高）

- `security-acls` - 使用 ACL 进行细粒度访问控制
- `security-auth` - 生产环境中始终使用认证
- `security-network` - 保障网络访问安全

### 11. 可观测性（中）

- `observe-commands` - 使用可观测性命令进行调试
- `observe-metrics` - 监控关键的 Redis 指标

## 如何使用

阅读单个规则文件以获取详细解释和代码示例：

```
rules/rqe-index-creation.md
rules/vector-rag-pattern.md
```

每个规则文件包含：
- 解释为什么这条规则重要
- 带解释的正确示例
- 要么一个“错误”示例（用于导致实际危害的反模式），要么“何时使用 / 何时不需要”的指导（用于可选功能）
- 额外的上下文和参考

## 完整编译文档

包含所有规则扩展的完整指南：`AGENTS.md`
