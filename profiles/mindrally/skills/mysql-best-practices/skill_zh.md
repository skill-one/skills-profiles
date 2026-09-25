# MySQL 最佳实践

## 核心原则

- 使用适当的存储引擎设计模式（大多数情况下使用 InnoDB）
- 使用 EXPLAIN 和正确索引优化查询
- 使用合适的数据类型以最小化存储并提高性能
- 合理实现连接池和查询缓存
- 遵循 MySQL 特定的安全加固实践

## 模式设计

### 存储引擎选择

- 将 InnoDB 作为默认引擎使用（支持 ACID，行级锁定）
- 仅在读取密集型、非事务性工作负载中考虑 MyISAM
- 使用 MEMORY 引擎为需要高速的临时表

```sql
CREATE TABLE orders (
    order_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    customer_id INT UNSIGNED NOT NULL,
    order_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(12, 2) NOT NULL,
    status ENUM('pending', 'processing', 'shipped', 'delivered', 'cancelled')
        NOT NULL DEFAULT 'pending',
    INDEX idx_customer (customer_id),
    INDEX idx_date_status (order_date, status),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 数据类型

- 使用满足需求的最小数据类型
- 在可能的情况下优先使用 INT UNSIGNED 而不是 BIGINT
- 使用 DECIMAL 进行财务计算，不要使用 FLOAT/DOUBLE
- 使用 ENUM 表示固定值集
- 使用 VARCHAR 表示可变长度字符串，CHAR 表示固定长度
- 始终使用 utf8mb4 字符集以支持完整 Unicode

```sql
-- 合适的数据类型选择
CREATE TABLE products (
    product_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    sku VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    quantity SMALLINT UNSIGNED NOT NULL DEFAULT 0,
    weight DECIMAL(8, 3),
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_sku (sku)
) ENGINE=InnoDB;
```

### 主键

- 为 InnoDB 表使用 AUTO_INCREMENT 整数主键
- 考虑将 UUID 存储为 BINARY(16) 用于分布式系统
- 尽量避免复合主键

```sql
-- UUID 存储优化
CREATE TABLE distributed_events (
    event_id BINARY(16) PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    payload JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 插入 UUID
INSERT INTO distributed_events (event_id, event_type, payload)
VALUES (UUID_TO_BIN(UUID()), 'user_signup', '{"user_id": 123}');

-- 查询 UUID
SELECT * FROM distributed_events
WHERE event_id = UUID_TO_BIN('550e8400-e29b-41d4-a716-446655440000');
```

## 索引策略

### 索引类型

- 大多数查询使用 B-tree 索引（默认）
- 使用 FULLTEXT 索引进行文本搜索
- 使用 SPATIAL 索引进行地理数据
- 考虑为频繁执行的查询创建覆盖索引

```sql
-- 用于常见查询模式的复合索引
CREATE INDEX idx_orders_customer_date ON orders(customer_id, order_date);

-- 覆盖索引
CREATE INDEX idx_orders_covering ON orders(customer_id, order_date, status, total_amount);

-- 搜索索引
ALTER TABLE products ADD FULLTEXT INDEX ft_name_desc (name, description);

-- 使用全文搜索
SELECT * FROM products
WHERE MATCH(name, description) AGAINST('wireless bluetooth' IN NATURAL LANGUAGE MODE);
```

### 索引指南

- 索引 WHERE、JOIN、ORDER BY 和 GROUP BY 中使用的列
- 在复合索引中将最具有选择性的列放在最前面
- 避免单独索引低基数列
- 监控并删除未使用的索引

```sql
-- 检查索引使用情况
SELECT
    table_schema, table_name, index_name,
    seq_in_index, column_name, cardinality
FROM information_schema.STATISTICS
WHERE table_schema = 'your_database'
ORDER BY table_name, index_name, seq_in_index;
```

## 查询优化

### EXPLAIN 分析

- 使用 EXPLAIN 分析查询执行计划
- 查找全表扫描（类型：ALL）
- 检查是否正确使用索引
- 监控检查的行数与返回的行数

```sql
EXPLAIN FORMAT=JSON
SELECT c.name, COUNT(o.order_id) AS order_count
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE c.created_at > '2024-01-01'
GROUP BY c.customer_id;
```

### 查询最佳实践

- 生产代码中避免使用 SELECT *
- 使用 LIMIT 实现分页
- 在可能的情况下优先使用 JOIN 而不是子查询
- 使用预处理语句处理重复查询

```sql
-- 高效分页
SELECT order_id, order_date, total_amount
FROM orders
WHERE customer_id = ?
ORDER BY order_date DESC
LIMIT 20 OFFSET 0;

-- Keyset 分页（对于大偏移量更高效）
SELECT order_id, order_date, total_amount
FROM orders
WHERE customer_id = ?
    AND (order_date, order_id) < (?, ?)
ORDER BY order_date DESC, order_id DESC
LIMIT 20;
```

### 避免常见错误

```sql
-- 避免：索引列上的函数
SELECT * FROM orders WHERE YEAR(order_date) = 2024;

-- 推荐方式：范围比较
SELECT * FROM orders
WHERE order_date >= '2024-01-01' AND order_date < '2025-01-01';

-- 避免：隐式类型转换
SELECT * FROM users WHERE user_id = '123';  -- user_id 是 INT

-- 推荐方式：正确类型
SELECT * FROM users WHERE user_id = 123;

-- 避免：LIKE 前导通配符
SELECT * FROM products WHERE name LIKE '%phone%';

-- 推荐方式：全文搜索用于文本匹配
SELECT * FROM products WHERE MATCH(name) AGAINST('phone');
```

## JSON 支持

- 使用 JSON 数据类型存储半结构化数据（MySQL 5.7+）
- 为频繁访问的 JSON 字段创建生成列
- 使用适当的 JSON 函数进行查询

```sql
CREATE TABLE events (
    event_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    payload JSON NOT NULL,
    -- 生成列用于索引
    user_id INT UNSIGNED AS (payload->>'$.user_id') STORED,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id)
);

-- 查询 JSON 数据
SELECT event_id, event_type,
       JSON_EXTRACT(payload, '$.action') AS action
FROM events
WHERE JSON_EXTRACT(payload, '$.user_id') = 123;

-- 或使用 -> 操作符
SELECT * FROM events WHERE payload->'$.user_id' = 123;
```

## 事务管理

- 使用 InnoDB 存储事务性表
- 保持事务简短以最小化锁竞争
- 选择适当的隔离级别
- 优雅地处理死锁

```sql
-- 带错误处理的事务
START TRANSACTION;

UPDATE accounts SET balance = balance - 100 WHERE account_id = 1;
UPDATE accounts SET balance = balance + 100 WHERE account_id = 2;

-- 检查错误并提交或回滚
COMMIT;

-- 设置隔离级别
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
```

## 复制和高可用性

### 读副本

- 将读查询直接指向副本
- 使用读写分离的连接池
- 监控复制延迟

```sql
-- 检查复制状态
SHOW SLAVE STATUS\G

-- 检查复制延迟
SELECT TIMESTAMPDIFF(SECOND,
    MAX(LAST_APPLIED_TRANSACTION_END_APPLY_TIMESTAMP),
    NOW()) AS lag_seconds
FROM performance_schema.replication_applier_status_by_worker;
```

## 安全

- 使用强密码和安全的连接（SSL/TLS）
- 应用最小权限原则
- 使用预处理语句防止 SQL 注入
- 审计敏感操作

```sql
-- 创建具有有限权限的用户
CREATE USER 'app_user'@'%' IDENTIFIED BY 'secure_password';
GRANT SELECT, INSERT, UPDATE, DELETE ON mydb.* TO 'app_user'@'%';
FLUSH PRIVILEGES;

-- 要求 SSL
ALTER USER 'app_user'@'%' REQUIRE SSL;

-- 查看用户权限
SHOW GRANTS FOR 'app_user'@'%';
```

## 维护

### 定期维护任务

```sql
-- 分析表以更新优化器统计信息
ANALYZE TABLE orders, customers, products;

-- 优化表（回收空间，碎片整理）
OPTIMIZE TABLE orders;

-- 检查表完整性
CHECK TABLE orders;
```

### 监控查询

```sql
-- 查找慢查询
SELECT * FROM mysql.slow_log ORDER BY query_time DESC LIMIT 10;

-- 当前进程列表
SHOW FULL PROCESSLIST;

-- InnoDB 状态
SHOW ENGINE INNODB STATUS;

-- 表大小
SELECT
    table_name,
    ROUND(data_length / 1024 / 1024, 2) AS data_mb,
    ROUND(index_length / 1024 / 1024, 2) AS index_mb,
    table_rows
FROM information_schema.TABLES
WHERE table_schema = 'your_database'
ORDER BY data_length DESC;
```

## 配置建议

```ini
# my.cnf 推荐设置

[mysqld]
# InnoDB 设置
innodb_buffer_pool_size = 70%_of_RAM
innodb_log_file_size = 256M
innodb_flush_log_at_trx_commit = 1
innodb_flush_method = O_DIRECT

# 连接设置
max_connections = 500
wait_timeout = 300
interactive_timeout = 300

# 查询缓存（MySQL 8.0+ 中禁用）
query_cache_type = 0

# 慢查询日志
slow_query_log = 1
slow_query_log_file = /var/log/mysql/slow.log
long_query_time = 2
```
