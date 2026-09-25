# SQL 优化模式

通过系统化优化、合理索引和查询计划分析，将缓慢的数据库查询转换为闪电般的操作。

## 何时使用此技能

- 调试运行缓慢的查询
- 设计高性能的数据库模式
- 优化应用程序响应时间
- 减少数据库负载和成本
- 提升大型数据集的可扩展性
- 分析 EXPLAIN 查询计划
- 实现高效的索引
- 解决 N+1 查询问题

## 核心概念

### 1. 查询执行计划（EXPLAIN）

理解 EXPLAIN 输出是优化的基础。

**PostgreSQL EXPLAIN：**

```sql
-- 基本解释
EXPLAIN SELECT * FROM users WHERE email = 'user@example.com';

-- 带实际执行统计
EXPLAIN ANALYZE
SELECT * FROM users WHERE email = 'user@example.com';

-- 更详细的 verbose 输出
EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
SELECT u.*, o.order_total
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE u.created_at > NOW() - INTERVAL '30 days';
```

**需要关注的指标：**

- **Seq Scan**：全表扫描（对于大型表通常较慢）
- **Index Scan**：使用索引（良好）
- **Index Only Scan**：使用索引而不访问表（最佳）
- **Nested Loop**：连接方法（适用于小数据集）
- **Hash Join**：连接方法（适用于较大数据集）
- **Merge Join**：连接方法（适用于排序数据）
- **Cost**：估计查询成本（越低越好）
- **Rows**：估计返回的行数
- **Actual Time**：实际执行时间

### 2. 索引策略

索引是最强大的优化工具。

**索引类型：**

- **B-Tree**：默认，适用于等值和范围查询
- **Hash**：仅用于等值 (=) 比较
- **GIN**：全文搜索、数组查询、JSONB
- **GiST**：几何数据、全文搜索
- **BRIN**：块范围索引，适用于具有相关性的超大型表

```sql
-- 标准 B-Tree 索引
CREATE INDEX idx_users_email ON users(email);

-- 复合索引（顺序很重要！）
CREATE INDEX idx_orders_user_status ON orders(user_id, status);

-- 部分索引（索引行子集）
CREATE INDEX idx_active_users ON users(email)
WHERE status = 'active';

-- 表达式索引
CREATE INDEX idx_users_lower_email ON users(LOWER(email));

-- 覆盖索引（包含附加列）
CREATE INDEX idx_users_email_covering ON users(email)
INCLUDE (name, created_at);

-- 全文搜索索引
CREATE INDEX idx_posts_search ON posts
USING GIN(to_tsvector('english', title || ' ' || body));

-- JSONB 索引
CREATE INDEX idx_metadata ON events USING GIN(metadata);
```

### 3. 查询优化模式

**避免使用 SELECT \*：**

```sql
-- 不好：获取不必要的列
SELECT * FROM users WHERE id = 123;

-- 好：只获取你需要的数据
SELECT id, email, name FROM users WHERE id = 123;
```

**高效使用 WHERE 子句：**

```sql
-- 不好：函数阻止索引使用
SELECT * FROM users WHERE LOWER(email) = 'user@example.com';

-- 好：创建函数索引或使用精确匹配
CREATE INDEX idx_users_email_lower ON users(LOWER(email));
-- 然后：
SELECT * FROM users WHERE LOWER(email) = 'user@example.com';

-- 或者存储规范化数据
SELECT * FROM users WHERE email = 'user@example.com';
```

**优化 JOIN：**

```sql
-- 不好：笛卡尔积然后过滤
SELECT u.name, o.total
FROM users u, orders o
WHERE u.id = o.user_id AND u.created_at > '2024-01-01';

-- 好：过滤后再连接
SELECT u.name, o.total
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE u.created_at > '2024-01-01';

-- 更好：两个表都过滤
SELECT u.name, o.total
FROM (SELECT * FROM users WHERE created_at > '2024-01-01') u
JOIN orders o ON u.id = o.user_id;
```

## 详细模式和工作示例

详细模式文档位于 `references/details.md`。当上层导航层级不足时，请阅读该文件。

## 最佳实践

1. **选择性索引**：过多索引会减慢写操作
2. **监控查询性能**：使用慢查询日志
3. **保持统计信息更新**：定期运行 ANALYZE
4. **使用适当的数据类型**：较小类型 = 更好的性能
5. **谨慎规范化**：平衡规范化与性能
6. **缓存频繁访问的数据**：使用应用级缓存
7. **连接池**：重用数据库连接
8. **定期维护**：VACUUM、ANALYZE、重建索引

```sql
-- 更新统计信息
ANALYZE users;
ANALYZE VERBOSE orders;

-- 清理（PostgreSQL）
VACUUM ANALYZE users;
VACUUM FULL users;  -- 回收空间（锁定表）

-- 重建索引
REINDEX INDEX idx_users_email;
REINDEX TABLE users;
```

## 常见陷阱

- **过度索引**：每个索引都会减慢 INSERT/UPDATE/DELETE
- **未使用的索引**：浪费空间并减慢写操作
- **缺失索引**：查询缓慢，全表扫描
- **隐式类型转换**：阻止索引使用
- **OR 条件**：无法高效使用索引
- **LIKE 前导通配符**：`LIKE '%abc'` 无法使用索引
- **WHERE 子句中的函数**：除非存在函数索引，否则阻止索引使用

## 监控查询

```sql
-- 查找慢查询（PostgreSQL）
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- 查找缺失索引（PostgreSQL）
SELECT
    schemaname,
    tablename,
    seq_scan,
    seq_tup_read,
    idx_scan,
    seq_tup_read / seq_scan AS avg_seq_tup_read
FROM pg_stat_user_tables
WHERE seq_scan > 0
ORDER BY seq_tup_read DESC
LIMIT 10;

-- 查找未使用的索引（PostgreSQL）
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY pg_relation_size(indexrelid) DESC;
```
