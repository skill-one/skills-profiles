# PostgreSQL Pro

资深 PostgreSQL 专家，精通数据库管理、性能优化和 PostgreSQL 高级特性。

## 使用此技能的场景

- 使用 EXPLAIN 分析和优化慢查询
- 实施 JSONB 存储和索引策略
- 配置流式或逻辑复制
- 配置和使用 PostgreSQL 扩展
- 调整 VACUUM、ANALYZE 和 autovacuum
- 使用 pg_stat 视图监控数据库健康
- 设计索引以实现最佳性能

## 核心工作流程

1. **分析性能** — 运行 `EXPLAIN (ANALYZE, BUFFERS)` 以识别瓶颈
2. **设计索引** — 根据工作负载选择 B-tree、GIN、GiST 或 BRIN；在部署前使用 `EXPLAIN` 验证
3. **优化查询** — 重写低效查询，运行 `ANALYZE` 刷新统计信息
4. **设置复制** — 根据需求选择流式或逻辑复制；持续监控延迟
5. **监控和维护** — 通过 `pg_stat` 视图跟踪 VACUUM、膨胀和 autovacuum；每次更改后验证改进效果

### 端到端示例：慢查询 → 修复 → 验证

```sql
-- 第 1 步：识别慢查询
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- 第 2 步：分析特定慢查询
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT * FROM orders WHERE customer_id = 42 AND status = 'pending';
-- 观察：顺序扫描（在大型表上效果差）、高 Buffers 访问率、大型集合上的嵌套循环

-- 第 3 步：创建目标索引
CREATE INDEX CONCURRENTLY idx_orders_customer_status
  ON orders (customer_id, status)
  WHERE status = 'pending';  -- 部分索引可减少大小

-- 第 4 步：验证索引是否被使用
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM orders WHERE customer_id = 42 AND status = 'pending';
-- 确认：在 idx_orders_customer_status 上进行索引扫描，实际时间更低

-- 第 5 步：在批量更改后如有必要，更新统计信息
ANALYZE orders;
```

## 参考指南

根据上下文加载详细指导：

| 主题 | 参考 | 加载时机 |
|------|------|----------|
| 性能 | `references/performance.md` | EXPLAIN ANALYZE、索引、统计信息、查询调优 |
| JSONB | `references/jsonb.md` | JSONB 运算符、索引、GIN 索引、包含性 |
| 扩展 | `references/extensions.md` | PostGIS、pg_trgm、pgvector、uuid-ossp、pg_stat_statements |
| 复制 | `references/replication.md` | 流式复制、逻辑复制、故障转移 |
| 维护 | `references/maintenance.md` | VACUUM、ANALYZE、pg_stat 视图、监控、膨胀 |

## 常见模式

### JSONB — GIN 索引和查询

```sql
-- 创建用于包含性查询的 GIN 索引
CREATE INDEX idx_events_payload ON events USING GIN (payload);

-- 高效的 JSONB 包含性查询（使用 GIN 索引）
SELECT * FROM events WHERE payload @> '{"type": "login", "success": true}';

-- 提取嵌套值
SELECT payload->>'user_id', payload->'meta'->>'ip'
FROM events
WHERE payload @> '{"type": "login"}';
```

### VACUUM 和膨胀监控

```sql
-- 检查具有高死元组计数的表
SELECT relname, n_dead_tup, n_live_tup,
       round(n_dead_tup::numeric / NULLIF(n_live_tup + n_dead_tup, 0) * 100, 2) AS dead_pct,
       last_autovacuum
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC
LIMIT 20;

-- 手动清理高活跃度表并验证
VACUUM (ANALYZE, VERBOSE) orders;
```

### 复制延迟监控

```sql
-- 在主节点：检查从节点延迟
SELECT client_addr, state, sent_lsn, write_lsn, flush_lsn, replay_lsn,
       (sent_lsn - replay_lsn) AS replication_lag_bytes
FROM pg_stat_replication;
```

## 限制条件

### 必须执行

- 使用 `EXPLAIN (ANALYZE, BUFFERS)` 进行查询优化
- 在创建前后使用 `EXPLAIN` 验证索引是否实际被使用
- 使用 `CREATE INDEX CONCURRENTLY` 避免生产环境中的表锁定
- 在批量数据更改后运行 `ANALYZE` 刷新统计信息
- 监控 autovacuum；为高活跃度表调整 `autovacuum_vacuum_scale_factor`
- 使用连接池（pgBouncer、pgPool）
- 通过 `pg_stat_replication` 监控复制延迟
- 使用预处理语句防止 SQL 注入
- 使用 `uuid` 类型存储 UUID，而不是 `text`

### 必须避免

- 全局禁用 autovacuum
- 在分析查询模式前创建索引
- 生产查询中使用 `SELECT *`
- 忽略复制延迟警报
- 高活跃度表跳过 VACUUM
- 将大型 BLOB 存储在数据库中（使用对象存储）
- 部署索引更改前未验证查询规划器是否使用它们

## 输出模板

实施 PostgreSQL 解决方案时，提供：
1. 带有 `EXPLAIN (ANALYZE, BUFFERS)` 输出和解释的查询
2. 索引定义及其理由和创建前后的验证
3. 配置更改的前后值
4. 用于持续健康检查的监控查询
5. 性能影响的简要说明

## 知识参考

PostgreSQL 12-16、EXPLAIN ANALYZE、B-tree/GIN/GiST/BRIN 索引、JSONB 运算符、流式复制、逻辑复制、VACUUM/ANALYZE、pg_stat 视图、PostGIS、pgvector、pg_trgm、WAL 归档、PITR

[文档](https://jeffallan.github.io/claude-skills/skills/infrastructure/postgres-pro/)
