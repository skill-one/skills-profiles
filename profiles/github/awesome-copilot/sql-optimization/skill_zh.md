# SQL 性能优化助手

针对 ${selection}（若无选择则优化整个项目）的专业 SQL 性能优化。专注于通用的 SQL 优化技术，适用于 MySQL、PostgreSQL、SQL Server、Oracle 及其他 SQL 数据库。

## 🎯 核心优化领域

### 查询性能分析
```sql
-- ❌ BAD: 低效的查询模式
SELECT * FROM orders o
WHERE YEAR(o.created_at) = 2024
  AND o.customer_id IN (
      SELECT c.id FROM customers c WHERE c.status = 'active'
  );

-- ✅ GOOD: 带有适当索引提示的优化查询
SELECT o.id, o.customer_id, o.total_amount, o.created_at
FROM orders o
INNER JOIN customers c ON o.customer_id = c.id
WHERE o.created_at >= '2024-01-01' 
  AND o.created_at < '2025-01-01'
  AND c.status = 'active';

-- 所需索引：
-- CREATE INDEX idx_orders_created_at ON orders(created_at);
-- CREATE INDEX idx_customers_status ON customers(status);
-- CREATE INDEX idx_orders_customer_id ON orders(customer_id);
```

### 索引策略优化
```sql
-- ❌ BAD: 不良的索引策略
CREATE INDEX idx_user_data ON users(email, first_name, last_name, created_at);

-- ✅ GOOD: 优化的复合索引
-- 针对首先按 email 过滤，然后按 created_at 排序的查询
CREATE INDEX idx_users_email_created ON users(email, created_at);

-- 针对全文字段名搜索
CREATE INDEX idx_users_name ON users(last_name, first_name);

-- 针对用户状态查询
CREATE INDEX idx_users_status_created ON users(status, created_at)
WHERE status IS NOT NULL;
```

### 子查询优化
```sql
-- ❌ BAD: 相关子查询
SELECT p.product_name, p.price
FROM products p
WHERE p.price > (
    SELECT AVG(price) 
    FROM products p2 
    WHERE p2.category_id = p.category_id
);

-- ✅ GOOD: 窗口函数方法
SELECT product_name, price
FROM (
    SELECT product_name, price,
           AVG(price) OVER (PARTITION BY category_id) as avg_category_price
    FROM products
) ranked
WHERE price > avg_category_price;
```

## 📊 性能调优技术

### JOIN 优化
```sql
-- ❌ BAD: 低效的 JOIN 顺序和条件
SELECT o.*, c.name, p.product_name
FROM orders o
LEFT JOIN customers c ON o.customer_id = c.id
LEFT JOIN order_items oi ON o.id = oi.order_id
LEFT JOIN products p ON oi.product_id = p.id
WHERE o.created_at > '2024-01-01'
  AND c.status = 'active';

-- ✅ GOOD: 过滤优化的 JOIN
SELECT o.id, o.total_amount, c.name, p.product_name
FROM orders o
INNER JOIN customers c ON o.customer_id = c.id AND c.status = 'active'
INNER JOIN order_items oi ON o.id = oi.order_id
INNER JOIN products p ON oi.product_id = p.id
WHERE o.created_at > '2024-01-01';
```

### 分页优化
```sql
-- ❌ BAD: 基于 OFFSET 的分页（对大 OFFSET 慢）
SELECT * FROM products 
ORDER BY created_at DESC 
LIMIT 20 OFFSET 10000;

-- ✅ GOOD: 基于游标的分页
SELECT * FROM products 
WHERE created_at < '2024-06-15 10:30:00'
ORDER BY created_at DESC 
LIMIT 20;

-- 或使用基于 ID 的游标
SELECT * FROM products 
WHERE id > 1000
ORDER BY id 
LIMIT 20;
```

### 聚合优化
```sql
-- ❌ BAD: 多个独立的聚合查询
SELECT COUNT(*) FROM orders WHERE status = 'pending';
SELECT COUNT(*) FROM orders WHERE status = 'shipped';
SELECT COUNT(*) FROM orders WHERE status = 'delivered';

-- ✅ GOOD: 单个查询带条件聚合
SELECT 
    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_count,
    COUNT(CASE WHEN status = 'shipped' THEN 1 END) as shipped_count,
    COUNT(CASE WHEN status = 'delivered' THEN 1 END) as delivered_count
FROM orders;
```

## 🔍 查询反模式

### SELECT 性能问题
```sql
-- ❌ BAD: SELECT * 反模式
SELECT * FROM large_table lt
JOIN another_table at ON lt.id = at.ref_id;

-- ✅ GOOD: 显式列选择
SELECT lt.id, lt.name, at.value
FROM large_table lt
JOIN another_table at ON lt.id = at.ref_id;
```

### WHERE 子句优化
```sql
-- ❌ BAD: WHERE 子句中的函数调用
SELECT * FROM orders 
WHERE UPPER(customer_email) = 'JOHN@EXAMPLE.COM';

-- ✅ GOOD: 索引友好的 WHERE 子句
SELECT * FROM orders 
WHERE customer_email = 'john@example.com';
-- 考虑：CREATE INDEX idx_orders_email ON orders(LOWER(customer_email));
```

### OR vs UNION 优化
```sql
-- ❌ BAD: 复杂的 OR 条件
SELECT * FROM products 
WHERE (category = 'electronics' AND price < 1000)
   OR (category = 'books' AND price < 50);

-- ✅ GOOD: UNION 方法以获得更好的优化
SELECT * FROM products WHERE category = 'electronics' AND price < 1000
UNION ALL
SELECT * FROM products WHERE category = 'books' AND price < 50;
```

## 📈 数据库无关的优化

### 批量操作
```sql
-- ❌ BAD: 行逐行操作
INSERT INTO products (name, price) VALUES ('Product 1', 10.00);
INSERT INTO products (name, price) VALUES ('Product 2', 15.00);
INSERT INTO products (name, price) VALUES ('Product 3', 20.00);

-- ✅ GOOD: 批量插入
INSERT INTO products (name, price) VALUES 
('Product 1', 10.00),
('Product 2', 15.00),
('Product 3', 20.00);
```

### 临时表使用
```sql
-- ✅ GOOD: 使用临时表进行复杂操作
CREATE TEMPORARY TABLE temp_calculations AS
SELECT customer_id, 
       SUM(total_amount) as total_spent,
       COUNT(*) as order_count
FROM orders 
WHERE created_at >= '2024-01-01'
GROUP BY customer_id;

-- 使用临时表进行进一步计算
SELECT c.name, tc.total_spent, tc.order_count
FROM temp_calculations tc
JOIN customers c ON tc.customer_id = c.id
WHERE tc.total_spent > 1000;
```

## 🛠️ 索引管理

### 索引设计原则
```sql
-- ✅ GOOD: 覆盖索引设计
CREATE INDEX idx_orders_covering 
ON orders(customer_id, created_at) 
INCLUDE (total_amount, status);  -- SQL Server 语法
-- 或：CREATE INDEX idx_orders_covering ON orders(customer_id, created_at, total_amount, status); -- 其他数据库
```

### 部分索引策略
```sql
-- ✅ GOOD: 针对特定条件的部分索引
CREATE INDEX idx_orders_active 
ON orders(created_at) 
WHERE status IN ('pending', 'processing');
```

## 📊 性能监控查询

### 查询性能分析
```sql
-- 识别慢查询的通用方法
-- （具体语法因数据库而异）

-- 对于 MySQL:
SELECT query_time, lock_time, rows_sent, rows_examined, sql_text
FROM mysql.slow_log
ORDER BY query_time DESC;

-- 对于 PostgreSQL:
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY total_time DESC;

-- 对于 SQL Server:
SELECT 
    qs.total_elapsed_time/qs.execution_count as avg_elapsed_time,
    qs.execution_count,
    SUBSTRING(qt.text, (qs.statement_start_offset/2)+1,
        ((CASE qs.statement_end_offset WHEN -1 THEN DATALENGTH(qt.text)
        ELSE qs.statement_end_offset END - qs.statement_start_offset)/2)+1) as query_text
FROM sys.dm_exec_query_stats qs
CROSS APPLY sys.dm_exec_sql_text(qs.sql_handle) qt
ORDER BY avg_elapsed_time DESC;
```

## 🎯 通用优化清单

### 查询结构
- [ ] 避免在生产查询中使用 SELECT *
- [ ] 使用适当的 JOIN 类型（INNER vs LEFT/RIGHT）
- [ ] 在 WHERE 子句中尽早过滤
- [ ] 在适当情况下使用 EXISTS 而不是 IN 进行子查询
- [ ] 避免 WHERE 子句中的函数调用以防止索引使用

### 索引策略
- [ ] 在经常查询的列上创建索引
- [ ] 在正确的列顺序中使用复合索引
- [ ] 避免 过度索引（影响 INSERT/UPDATE 性能）
- [ ] 在有益时使用覆盖索引
- [ ] 创建针对特定查询模式的部分索引

### 数据类型和架构
- [ ] 使用适当的数据类型以实现存储效率
- [ ] 适当规范化（OLTP 为 3NF，OLAP 为反规范化）
- [ ] 使用约束以帮助查询优化器
- [ ] 在适当情况下对大表进行分区

### 查询模式
- [ ] 使用 LIMIT/TOP 控制结果集
- [ ] 实现高效的分页策略
- [ ] 使用批量操作进行大量数据变更
- [ ] 避免 N+1 查询问题
- [ ] 使用预编译语句进行重复查询

### 性能测试
- [ ] 使用真实数据量测试查询
- [ ] 分析查询执行计划
- [ ] 长期监控查询性能
- [ ] 设置慢查询警报
- [ ] 定期分析索引使用情况

## 📝 优化方法

1. **识别**：使用特定数据库工具查找慢查询
2. **分析**：检查执行计划并识别瓶颈
3. **优化**：应用适当的优化技术
4. **测试**：验证性能改进
5. **监控**：持续跟踪性能指标
6. **迭代**：定期性能审查和优化

专注于可衡量的性能改进，并始终使用真实数据量和查询模式测试优化。
