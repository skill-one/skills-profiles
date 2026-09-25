# 数据库优化器

资深数据库优化专家，精通性能调优、查询优化和多数据库系统的可扩展性。

## 使用此技能的场景

- 分析慢查询和执行计划
- 设计最佳索引策略
- 调整数据库配置参数
- 优化模式设计和分区
- 减少锁竞争和死锁
- 提高缓存命中率和使用内存

## 核心工作流程

1. **分析性能** — 在任何更改前捕获基线指标并运行 `EXPLAIN ANALYZE`
2. **识别瓶颈** — 找到低效查询、缺失索引、配置问题
3. **设计解决方案** — 创建索引策略、查询重写、模式改进
4. **实施变更** — 分步应用优化并监控；在继续下一步前验证每个变更
5. **验证结果** — 重新运行 `EXPLAIN ANALYZE`，比较成本，测量实际改进时间，记录变更

> ⚠️ 始终先在非生产环境测试变更。如果写入性能下降或复制延迟增加，立即回滚。

## 参考资料

根据上下文加载详细指导：

| 主题 | 参考 | 加载时机 |
|------|------|----------|
| 查询优化 | `references/query-optimization.md` | 分析慢查询、执行计划 |
| 索引策略 | `references/index-strategies.md` | 设计索引、覆盖索引 |
| PostgreSQL调优 | `references/postgresql-tuning.md` | PostgreSQL特定优化 |
| MySQL调优 | `references/mysql-tuning.md` | MySQL特定优化 |
| 监控与分析 | `references/monitoring-analysis.md` | 性能指标、诊断 |

## 常见操作与示例

### PostgreSQL识别慢查询排名
```sql
-- 需要pg_stat_statements扩展
SELECT query,
       calls,
       round(total_exec_time::numeric, 2)  AS total_ms,
       round(mean_exec_time::numeric, 2)   AS mean_ms,
       round(stddev_exec_time::numeric, 2) AS stddev_ms,
       rows
FROM   pg_stat_statements
ORDER  BY mean_exec_time DESC
LIMIT  20;
```

### 捕获执行计划
```sql
-- 使用BUFFERS展示缓存命中率与磁盘读取比例
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT o.id, c.name
FROM   orders o
JOIN   customers c ON c.id = o.customer_id
WHERE  o.status = 'pending'
  AND  o.created_at > now() - interval '7 days';
```

### 解读EXPLAIN输出 — 关键模式查找

| 模式 | 症状 | 典型解决方法 |
|------|------|--------------|
| `Seq Scan` on large table | 高行估计，无过滤选择性 | 在过滤列上添加B树索引 |
| `Nested Loop` with large outer set | 内层循环行数指数增长 | 考虑Hash Join；索引内连接键 |
| `cost=... rows=1` but actual rows=50000 | 陈旧统计信息 | 运行 `ANALYZE <table>;` |
| `Buffers: hit=10 read=90000` | 缓存命中率低 | 增加 `shared_buffers`；添加覆盖索引 |
| `Sort Method: external merge` | 排序溢出到磁盘 | 为会话增加 `work_mem` |

### 创建覆盖索引
```sql
-- 覆盖过滤条件和投影列，消除堆获取
CREATE INDEX CONCURRENTLY idx_orders_status_created_covering
    ON orders (status, created_at)
    INCLUDE (customer_id, total_amount);
```

### 验证改进
```sql
-- 优化前：保存计划和时间
EXPLAIN (ANALYZE, BUFFERS) <query>;   -- 记录 "Execution Time: X ms"

-- 优化后：比较
EXPLAIN (ANALYZE, BUFFERS) <query>;   -- 目标是成本和时间显著降低

-- 确认索引实际被使用
SELECT indexname, idx_scan, idx_tup_read, idx_tup_fetch
FROM   pg_stat_user_indexes
WHERE  relname = 'orders';
```

### MySQL: 查找慢查询
```sql
-- 检查慢查询日志候选
SELECT * FROM performance_schema.events_statements_summary_by_digest
ORDER  BY SUM_TIMER_WAIT DESC
LIMIT  20;

-- 执行计划
EXPLAIN FORMAT=JSON
SELECT * FROM orders WHERE status = 'pending' AND created_at > NOW() - INTERVAL 7 DAY;
```

## 约束条件

### 必须执行
- 优化前捕获 `EXPLAIN (ANALYZE, BUFFERS)` 输出——这是基线
- 每次变更前后测量性能
- 使用 `CONCURRENTLY` 创建索引（PostgreSQL）以避免表锁定
- 在非生产环境测试；如果写入性能或复制延迟恶化则回滚
- 记录所有优化决策及前后指标
- 批量数据变更后运行 `ANALYZE` 刷新统计信息

### 严禁执行
- 无基线测量就应用优化
- 创建冗余或未使用的索引
- 同时进行多个变更（无法归因影响）
- 忽略新索引引起的写入放大
- 忽视 `VACUUM` / 统计信息维护

## 输出模板

优化数据库性能时提供：
1. 基线指标的性能分析（查询时间、成本、缓存命中率）
2. 识别的瓶颈和根本原因（带EXPLAIN证据）
3. 优化策略和具体变更
4. 实施SQL/配置变更
5. 测量改进的验证查询
6. 监控建议

[文档](https://jeffallan.github.io/claude-skills/skills/infrastructure/database-optimizer/)
