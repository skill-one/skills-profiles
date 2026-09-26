# PostgreSQL 专家技能

此技能通过专业参考提供全面的 PostgreSQL 专业知识。根据任务加载相应的参考。

## 可用参考

### 表设计
- **[设计 PostgreSQL 表格](references/design-postgres-tables.md)** — 数据类型、约束、索引、JSONB 模式、分区和 PostgreSQL 最佳实践。**用于任何通用的表格/模式设计任务。**
- **[设计 PostGIS 表格](references/design-postgis-tables.md)** — PostGIS 空间表格设计：几何类型与地理类型、SRID、空间索引和基于位置查询模式。**当任务涉及地理或空间数据时使用。**

### 搜索
- **[pgvector 语义搜索](references/pgvector-semantic-search.md)** — 使用 pgvector 的向量相似度搜索：HNSW/IVFFlat 索引、halfvec 存储、量化、过滤搜索和调优。**用于嵌入、RAG 或语义搜索。**
- **[PostgreSQL 混合文本搜索](references/postgres-hybrid-text-search.md)** — 结合 BM25 关键词搜索与使用 RRF 的 pgvector 语义搜索的混合搜索。**当结合关键词和基于含义的搜索时使用。**

### TimescaleDB
- **[设置 TimescaleDB 超表格](references/setup-timescaledb-hypertables.md)** — 超表格创建、压缩、保留策略、连续聚合和索引。**当从零开始设置 TimescaleDB 时使用。**
- **[查找超表格候选表格](references/find-hypertable-candidates.md)** — 分析现有表格并为其超表格转换打分的 SQL 查询。**当评估要迁移的表格时使用。**
- **[将 PostgreSQL 表格迁移到超表格](references/migrate-postgres-tables-to-hypertables.md)** — 分步迁移：分区列选择、原地与蓝绿、验证。**当执行迁移时使用。**

### 迁移
- **[PostgreSQL 数据库迁移](references/postgres-database-migration.md)** — DDL 锁参考、安全迁移模式、超时策略、回滚计划和基于分支的测试。**当在生产数据库上规划或执行模式更改时使用。**

## 如何使用

1. 从上述描述中识别与用户任务匹配的参考。
2. 加载参考文件以获取详细说明和 SQL 模式。
3. 对于跨越多个领域的任务（例如，“设计具有向量搜索的表格”），根据需要加载多个参考。
