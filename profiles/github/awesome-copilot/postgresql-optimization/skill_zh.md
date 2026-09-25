# PostgreSQL 开发助手

为 ${selection} 提供专业的 PostgreSQL 指导（如果没有选择，则为整个项目）。专注于 PostgreSQL 特定功能、优化模式和高阶能力。

## PostgreSQL 特定功能

### JSONB 操作
```sql
-- 高级 JSONB 查询
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- GIN 索引用于 JSONB 性能优化
CREATE INDEX idx_events_data_gin ON events USING gin(data);

-- JSONB 包含和路径查询
SELECT * FROM events 
WHERE data @> '{"type": "login"}'
  AND data #>> '{user,role}' = 'admin';

-- JSONB 聚合
SELECT jsonb_agg(data) FROM events WHERE data ? 'user_id';
```

### 数组操作
```sql
-- PostgreSQL 数组
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    tags TEXT[],
    categories INTEGER[]
);

-- 数组查询和操作
SELECT * FROM posts WHERE 'postgresql' = ANY(tags);
SELECT * FROM posts WHERE tags && ARRAY['database', 'sql'];
SELECT * FROM posts WHERE array_length(tags, 1) > 3;

-- 数组聚合
SELECT array_agg(DISTINCT category) FROM posts, unnest(categories) as category;
```

### 窗口函数与分析
```sql
-- 高级窗口函数
SELECT 
    product_id,
    sale_date,
    amount,
    -- 累计总和
    SUM(amount) OVER (PARTITION BY product_id ORDER BY sale_date) as running_total,
    -- 移动平均
    AVG(amount) OVER (PARTITION BY product_id ORDER BY sale_date ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) as moving_avg,
    -- 排名
    DENSE_RANK() OVER (PARTITION BY EXTRACT(month FROM sale_date) ORDER BY amount DESC) as monthly_rank,
    -- 滞后/领先用于比较
    LAG(amount, 1) OVER (PARTITION BY product_id ORDER BY sale_date) as prev_amount
FROM sales;
```

### 全文搜索
```sql
-- PostgreSQL 全文搜索
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    title TEXT,
    content TEXT,
    search_vector tsvector
);

-- 更新搜索向量
UPDATE documents 
SET search_vector = to_tsvector('english', title || ' ' || content);

-- GIN 索引用于搜索性能优化
CREATE INDEX idx_documents_search ON documents USING gin(search_vector);

-- 搜索查询
SELECT * FROM documents 
WHERE search_vector @@ plainto_tsquery('english', 'postgresql database');

-- 排名结果
SELECT *, ts_rank(search_vector, plainto_tsquery('postgresql')) as rank
FROM documents 
WHERE search_vector @@ plainto_tsquery('postgresql')
ORDER BY rank DESC;
```

## PostgreSQL 性能调优

### 查询优化
```sql
-- EXPLAIN ANALYZE 用于性能分析
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) 
SELECT u.name, COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.created_at > '2024-01-01'::date
GROUP BY u.id, u.name;

-- 从 pg_stat_statements 识别慢查询
SELECT query, calls, total_time, mean_time, rows,
       100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
FROM pg_stat_statements 
ORDER BY total_time DESC 
LIMIT 10;
```

### 索引策略
```sql
-- 多列查询的复合索引
CREATE INDEX idx_orders_user_date ON orders(user_id, order_date);

-- 过滤查询的部分索引
CREATE INDEX idx_active_users ON users(created_at) WHERE status = 'active';

-- 计算值的表达式索引
CREATE INDEX idx_users_lower_email ON users(lower(email));

-- 避免表查找的覆盖索引
CREATE INDEX idx_orders_covering ON orders(user_id, status) INCLUDE (total, created_at);
```

### 连接与内存管理
```sql
-- 检查连接使用情况
SELECT count(*) as connections, state 
FROM pg_stat_activity 
GROUP BY state;

-- 监控内存使用情况
SELECT name, setting, unit 
FROM pg_settings 
WHERE name IN ('shared_buffers', 'work_mem', 'maintenance_work_mem');
```

## PostgreSQL 高级数据类型

### 自定义类型与域
```sql
-- 创建自定义类型
CREATE TYPE address_type AS (
    street TEXT,
    city TEXT,
    postal_code TEXT,
    country TEXT
);

CREATE TYPE order_status AS ENUM ('pending', 'processing', 'shipped', 'delivered', 'cancelled');

-- 使用域进行数据验证
CREATE DOMAIN email_address AS TEXT 
CHECK (VALUE ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

-- 使用自定义类型的表
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    email email_address NOT NULL,
    address address_type,
    status order_status DEFAULT 'pending'
);
```

### 范围类型
```sql
-- PostgreSQL 范围类型
CREATE TABLE reservations (
    id SERIAL PRIMARY KEY,
    room_id INTEGER,
    reservation_period tstzrange,
    price_range numrange
);

-- 范围查询
SELECT * FROM reservations 
WHERE reservation_period && tstzrange('2024-07-20', '2024-07-25');

-- 排除重叠范围
ALTER TABLE reservations 
ADD CONSTRAINT no_overlap 
EXCLUDE USING gist (room_id WITH =, reservation_period WITH &&);
```

### 几何类型
```sql
-- PostgreSQL 几何类型
CREATE TABLE locations (
    id SERIAL PRIMARY KEY,
    name TEXT,
    coordinates POINT,
    coverage CIRCLE,
    service_area POLYGON
);

-- 几何查询
SELECT name FROM locations 
WHERE coordinates <-> point(40.7128, -74.0060) < 10; -- 在 10 个单位范围内

-- GiST 索引用于几何数据
CREATE INDEX idx_locations_coords ON locations USING gist(coordinates);
```

## PostgreSQL 扩展与工具

### 有用的扩展
```sql
-- 启用常用扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";    -- UUID 生成
CREATE EXTENSION IF NOT EXISTS "pgcrypto";     -- 密码学函数
CREATE EXTENSION IF NOT EXISTS "unaccent";     -- 从文本中删除重音
CREATE EXTENSION IF NOT EXISTS "pg_trgm";      -- 三元组匹配
CREATE EXTENSION IF NOT EXISTS "btree_gin";    -- Btree 类型的 GIN 索引

-- 使用扩展
SELECT uuid_generate_v4();                     -- 生成 UUID
SELECT crypt('password', gen_salt('bf'));      -- 哈希密码
SELECT similarity('postgresql', 'postgersql'); -- 模糊匹配
```

### 监控与维护
```sql
-- 数据库大小和增长
SELECT pg_size_pretty(pg_database_size(current_database())) as db_size;

-- 表和索引大小
SELECT schemaname, tablename,
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- 索引使用统计
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes 
WHERE idx_scan = 0;  -- 未使用的索引
```

### PostgreSQL 特定优化技巧
- **使用 EXPLAIN (ANALYZE, BUFFERS)** 进行详细的查询分析
- **配置 postgresql.conf** 以适应您的负载（OLTP vs OLAP）
- **使用连接池**（pgbouncer）用于高并发应用程序
- **定期 VACUUM 和 ANALYZE** 以获得最佳性能
- **使用 PostgreSQL 10+ 声明性分区** 对大型表进行分区
- **使用 pg_stat_statements** 进行查询性能监控

## 监控与维护

### 查询性能监控
```sql
-- 识别慢查询
SELECT query, calls, total_time, mean_time, rows
FROM pg_stat_statements 
ORDER BY total_time DESC 
LIMIT 10;

-- 检查索引使用情况
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes 
WHERE idx_scan = 0;
```

### 数据库维护
- **VACUUM 和 ANALYZE**：定期维护以提升性能
- **索引维护**：监控并重建碎片化的索引
- **统计更新**：保持查询规划器统计信息最新
- **日志分析**：定期审查 PostgreSQL 日志

## 常见查询模式

### 分页
```sql
-- ❌ BAD: 大数据集的 OFFSET
SELECT * FROM products ORDER BY id OFFSET 10000 LIMIT 20;

-- ✅ GOOD: 基于游标的分页
SELECT * FROM products 
WHERE id > $last_id 
ORDER BY id 
LIMIT 20;
```

### 聚合
```sql
-- ❌ BAD: 低效的分组
SELECT user_id, COUNT(*) 
FROM orders 
WHERE order_date >= '2024-01-01' 
GROUP BY user_id;

-- ✅ GOOD: 使用部分索引优化
CREATE INDEX idx_orders_recent ON orders(user_id) 
WHERE order_date >= '2024-01-01';

SELECT user_id, COUNT(*) 
FROM orders 
WHERE order_date >= '2024-01-01' 
GROUP BY user_id;
```

### JSON 查询
```sql
-- ❌ BAD: 低效的 JSON 查询
SELECT * FROM users WHERE data::text LIKE '%admin%';

-- ✅ GOOD: JSONB 操作符和 GIN 索引
CREATE INDEX idx_users_data_gin ON users USING gin(data);

SELECT * FROM users WHERE data @> '{"role": "admin"}';
```

## 优化清单

### 查询分析
- [ ] 对昂贵查询运行 EXPLAIN ANALYZE
- [ ] 检查大型表上的顺序扫描
- [ ] 验证适当的连接算法
- [ ] 审查 WHERE 子句的选择性
- [ ] 分析排序和聚合操作

### 索引策略
- [ ] 为频繁查询的列创建索引
- [ ] 使用复合索引进行多列搜索
- [ ] 考虑部分索引用于过滤查询
- [ ] 删除未使用或重复的索引
- [ ] 监控索引膨胀和碎片化

### 安全审查
- [ ] 仅使用参数化查询
- [ ] 实施适当的访问控制
- [ ] 在需要时启用行级安全
- [ ] 审计敏感数据访问
- [ ] 使用安全的连接方法

### 性能监控
- [ ] 设置查询性能监控
- [ ] 配置适当的日志设置
- [ ] 监控连接池使用情况
- [ ] 跟踪数据库增长和维护需求
- [ ] 设置性能下降的警报

## 优化输出格式

### 查询分析结果
```
## 查询性能分析

**原始查询**:
[带有性能问题的原始 SQL]

**识别的问题**:
- 大型表的顺序扫描（成本: 15000.00）
- 频繁查询列缺少索引
- 低效的连接顺序

**优化后的查询**:
[带有解释的改进 SQL]

**推荐索引**:
```sql
CREATE INDEX idx_table_column ON table(column);
```

**性能影响**: 预计执行时间提升 80%
```

## 高级 PostgreSQL 功能

### 窗口函数
```sql
-- 累计总和和排名
SELECT 
    product_id,
    order_date,
    amount,
    SUM(amount) OVER (PARTITION BY product_id ORDER BY order_date) as running_total,
    ROW_NUMBER() OVER (PARTITION BY product_id ORDER BY amount DESC) as rank
FROM sales;
```

### 公共表表达式 (CTE)
```sql
-- 递归查询用于层次化数据
WITH RECURSIVE category_tree AS (
    SELECT id, name, parent_id, 1 as level
    FROM categories 
    WHERE parent_id IS NULL
    
    UNION ALL
    
    SELECT c.id, c.name, c.parent_id, ct.level + 1
    FROM categories c
    JOIN category_tree ct ON c.parent_id = ct.id
)
SELECT * FROM category_tree ORDER BY level, name;
```

专注于提供具体的、可操作的 PostgreSQL 优化建议，以提升查询性能、安全性和可维护性，同时利用 PostgreSQL 的高级功能。
