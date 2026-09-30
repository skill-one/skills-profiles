---
name: postgres
description: '使用此技能处理任何 PostgreSQL 数据库工作——表设计、索引、数据类型、约束、扩展（pgvector、PostGIS、TimescaleDB）、搜索和迁移。


  **当用户要求时触发：**

  - 探索现有的 PostgreSQL 数据库，了解其对象和关系

  - 设计或修改 PostgreSQL 表、模式或数据模型

  - 选择数据类型、约束、索引或分区策略

  - 使用 pgvector 嵌入、语义搜索或 RAG

  - 设置全文搜索、混合搜索或 BM25 排名

  - 使用 PostGIS 处理空间/地理数据

  - 为时间序列数据设置 TimescaleDB 超表

  - 将表迁移到超表或评估迁移候选对象

  - 规划或执行零停机时间的安全模式迁移


  **关键词：** PostgreSQL、Postgres、SQL、模式、表设计、索引、约束、pgvector、PostGIS、TimescaleDB、超表、语义搜索、混合搜索、BM25、时间序列、迁移'
---

# PostgreSQL 专家技能

此技能通过专业参考提供全面的 PostgreSQL 专业知识。根据任务加载相应的参考。

## 可用参考

### 现有数据库
- **[schema-exploration](references/schema-exploration/guide.md)** — 基于只读、问答驱动的模式、表、视图、例程、触发器、RLS 和扩展的探索，使用 `pg_catalog`。**用于在设计和更改或编写查询之前理解现有数据库。**

### 表设计
- **[design-postgres-tables](references/design-postgres-tables.md)** — 数据类型、约束、索引、JSONB 模式、分区和 PostgreSQL 最佳实践。**用于任何通用的表/模式设计任务。**
- **[design-postgis-tables](references/design-postgis-tables.md)** — PostGIS 空间表设计：几何类型与地理类型、SRIDs、空间索引和基于位置查询模式。**当任务涉及地理或空间数据时使用。**

### 搜索
- **[pgvector-semantic-search](references/pgvector-semantic-search.md)** — 使用 pgvector 的向量相似度搜索：HNSW/IVFFlat 索引、halfvec 存储、量化、过滤搜索和调优。**用于嵌入、RAG 或语义搜索。**
- **[postgres-hybrid-text-search](references/postgres-hybrid-text-search.md)** — 结合 BM25 关键词搜索和 pgvector 语义搜索（使用 RRF）的混合搜索。**当结合关键词和基于含义的搜索时使用。**

### TimescaleDB
- **[setup-timescaledb-hypertables](references/setup-timescaledb-hypertables.md)** — 超表创建、压缩、保留策略、连续聚合和索引。**当从零开始设置 TimescaleDB 时使用。**
- **[find-hypertable-candidates](references/find-hypertable-candidates.md)** — 分析现有表并为其超表转换评分的 SQL 查询。**当评估要迁移哪些表时使用。**
- **[migrate-postgres-tables-to-hypertables](references/migrate-postgres-tables-to-hypertables.md)** — 分步迁移：分区列选择、原地与蓝绿、验证。**当执行迁移时使用。**

### 迁移
- **[postgres-database-migration](references/postgres-database-migration.md)** — DDL 锁参考、安全迁移模式、超时策略、回滚计划和基于分支的测试。**当在生产数据库上计划或执行模式更改时使用。**

## 如何使用

1. 从上述描述中识别与用户任务匹配的参考。
2. 加载参考文件以获取详细说明和 SQL 模式。
3. 对于跨越多个领域的任务（例如，“设计具有向量搜索的表”），根据需要加载多个参考。
