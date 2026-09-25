# PostgreSQL 最佳实践

## 核心原则

- 利用 PostgreSQL 的高级特性进行健壮的数据建模
- 使用 EXPLAIN ANALYZE 和适当的索引策略优化查询
- 合理使用 PostgreSQL 的原生数据类型
- 实施适当的连接池和资源管理
- 遵循 PostgreSQL 特有的安全最佳实践

## 模式设计

### 数据类型

- 使用适当的原生类型：`UUID`、`JSONB`、`ARRAY`、`INET`、`CIDR`
- 优先使用 `TIMESTAMPTZ` 而不是 `TIMESTAMP` 用于时区感知的应用
- 当不需要长度限制时，使用 `TEXT` 而不是 `VARCHAR`
- 对于精确的小数计算（财务数据），考虑使用 `NUMERIC`
- 使用 `SERIAL` 或 `BIGSERIAL` 用于自增 ID，或使用 `UUID` 用于分布式系统

```sql
CREATE TABLE orders (
    order_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES customers(customer_id),
    order_data JSONB NOT NULL DEFAULT '{}',
    tags TEXT[] DEFAULT '{}',
    total_amount NUMERIC(12, 2) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### 表设计

- 始终定义主键
- 使用外键并带有适当的 ON DELETE/UPDATE 动作
- 在适当的地方添加 NOT NULL 约束
- 使用 CHECK 约束进行数据验证
- 考虑对大表进行分区

```sql
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    sku VARCHAR(50) NOT NULL UNIQUE,
    name TEXT NOT NULL,
    price NUMERIC(10, 2) NOT NULL CHECK (price >= 0),
    status VARCHAR(20) NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'inactive', 'discontinued')),
    metadata JSONB DEFAULT '{}'
);
```

### 分区

- 对百万行以上的大表使用声明式分区
- 选择适当的分区策略：RANGE、LIST 或 HASH
- 在分区后对分区表创建索引

```sql
CREATE TABLE events (
    event_id BIGSERIAL,
    event_type VARCHAR(50) NOT NULL,
    payload JSONB,
    created_at TIMESTAMPTZ NOT NULL
) PARTITION BY RANGE (created_at);

CREATE TABLE events_2024_q1 PARTITION OF events
    FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');
```

## 索引策略

### 索引类型

- 使用 B-tree 索引（默认）用于等值和范围查询
- 使用 GIN 索引用于 JSONB、数组和全文搜索
- 使用 GiST 索引用于几何数据和范围类型
- 使用 BRIN 索引用于大型、自然有序的数据
- 考虑使用部分索引进行过滤查询

```sql
-- B-tree 索引用于常见查找
CREATE INDEX idx_orders_customer ON orders(customer_id);

-- GIN 索引用于 JSONB 查询
CREATE INDEX idx_orders_data ON orders USING GIN (order_data);

-- 部分索引仅用于活跃记录
CREATE INDEX idx_active_products ON products(name) WHERE status = 'active';

-- 覆盖索引以避免表查找
CREATE INDEX idx_orders_covering ON orders(customer_id)
    INCLUDE (order_date, total_amount);
```

### 索引维护

- 定期运行 ANALYZE 更新统计信息
- 使用 REINDEX 处理膨胀的索引
- 使用 `pg_stat_user_indexes` 监控索引使用情况
- 删除未使用的索引以减少写操作开销

```sql
-- 检查索引使用情况
SELECT schemaname, relname, indexrelname, idx_scan, idx_tup_read
FROM pg_stat_user_indexes
ORDER BY idx_scan ASC;
```

## 查询优化

### EXPLAIN ANALYZE

- 始终分析慢查询的查询计划
- 检查大表上的顺序扫描
- 从查询计划中识别缺失的索引
- 关注预估行数与实际行数的差异

```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT c.name, COUNT(o.order_id)
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE c.created_at > '2024-01-01'
GROUP BY c.customer_id, c.name;
```

### 公共表表达式 (CTEs)

- 使用 CTEs 进行复杂查询的组织
- 注意：在较旧的 PostgreSQL 版本中，CTEs 是优化屏障
- 在 PostgreSQL 12+ 中使用 `MATERIALIZED`/`NOT MATERIALIZED` 提示

```sql
WITH recent_orders AS MATERIALIZED (
    SELECT customer_id, COUNT(*) AS order_count, SUM(total) AS total_spent
    FROM orders
    WHERE order_date > CURRENT_DATE - INTERVAL '30 days'
    GROUP BY customer_id
)
SELECT c.name, ro.order_count, ro.total_spent
FROM customers c
JOIN recent_orders ro ON c.customer_id = ro.customer_id
WHERE ro.total_spent > 1000;
```

### 窗口函数

- 使用窗口函数进行分析查询
- 利用 PARTITION BY 和 ORDER BY 进行复杂计算

```sql
SELECT
    order_id,
    customer_id,
    total_amount,
    SUM(total_amount) OVER (PARTITION BY customer_id ORDER BY order_date) AS running_total,
    ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date DESC) AS order_rank
FROM orders;
```

## JSONB 最佳实践

- 优先使用 JSONB 而不是 JSON 以获得更好的性能和索引
- 为您查询的 JSONB 列创建 GIN 索引
- 使用包含运算符 (@>, <@) 进行高效查询
- 将频繁查询的字段提取到常规列

```sql
-- 使用 GIN 索引进行高效的 JSONB 查询
SELECT * FROM products
WHERE metadata @> '{"category": "electronics"}';

-- 提取特定字段
SELECT
    product_id,
    metadata->>'brand' AS brand,
    (metadata->>'rating')::numeric AS rating
FROM products
WHERE metadata ? 'rating';
```

## 连接管理

### 连接池

- 使用 PgBouncer 或 pgpool-II 进行连接池
- 根据工作负载设置适当的池大小
- 对于短生命周期连接，使用事务池模式

### 连接设置

```sql
-- 推荐的会话设置
SET statement_timeout = '30s';
SET lock_timeout = '10s';
SET idle_in_transaction_session_timeout = '60s';
```

## 事务和锁定

- 使用适当的事务隔离级别
- 保持事务简短以减少锁定竞争
- 使用通知锁进行应用级锁定
- 监控和解决锁定冲突

```sql
-- 使用通知锁进行应用协调
SELECT pg_advisory_lock(hashtext('resource_name'));
-- 执行操作
SELECT pg_advisory_unlock(hashtext('resource_name'));

-- 检查阻塞查询
SELECT blocked_locks.pid AS blocked_pid,
       blocking_locks.pid AS blocking_pid,
       blocked_activity.query AS blocked_query
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_locks blocking_locks
    ON blocking_locks.locktype = blocked_locks.locktype
    AND blocking_locks.relation = blocked_locks.relation
    AND blocking_locks.pid != blocked_locks.pid
JOIN pg_catalog.pg_stat_activity blocked_activity
    ON blocked_activity.pid = blocked_locks.pid;
```

## 维护

### VACUUM 和 ANALYZE

- 启用 autovacuum 并根据您的工作负载进行调优
- 在批量操作后运行手动 VACUUM ANALYZE
- 监控表膨胀

```sql
-- 检查表膨胀
SELECT schemaname, relname,
       n_live_tup, n_dead_tup,
       round(n_dead_tup * 100.0 / nullif(n_live_tup + n_dead_tup, 0), 2) AS dead_pct
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY n_dead_tup DESC;
```

### 备份策略

- 使用 pg_dump 进行逻辑备份
- 使用 pg_basebackup 进行物理备份
- 使用 WAL 归档实现点时间恢复 (PITR)
- 定期测试备份恢复

## 安全

- 使用 SSL/TLS 进行连接
- 对多租户应用实施行级安全 (RLS)
- 使用角色和 GRANT/REVOKE 进行访问控制
- 使用 pgAudit 扩展审计敏感操作

```sql
-- 启用行级安全
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

CREATE POLICY documents_tenant_policy ON documents
    FOR ALL
    USING (tenant_id = current_setting('app.tenant_id')::uuid);

-- 授予最小权限
GRANT SELECT, INSERT, UPDATE ON orders TO app_user;
GRANT USAGE ON SEQUENCE orders_order_id_seq TO app_user;
```

## 监控

- 使用 pg_stat_statements 扩展进行监控
- 跟踪慢查询并定期优化
- 设置警报以监控复制延迟、连接数和磁盘使用情况
- 使用 pg_stat_activity 监控活动查询

```sql
-- 启用 pg_stat_statements
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- 查找慢查询
SELECT query, calls, mean_exec_time, total_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```
