# 数据库模式设计器

内置最佳实践，设计生产就绪的数据库模式。

---

## 快速入门

只需描述您的数据模型：

```
为电子商务平台设计一个包含用户、产品和订单的数据库模式
```

您将获得一个完整的 SQL 模式，例如：

```sql
CREATE TABLE users (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(id),
  total DECIMAL(10,2) NOT NULL,
  INDEX idx_orders_user (user_id)
);
```

**请求中应包含的内容：**
- 实体（用户、产品、订单）
- 关键关系（用户有订单，订单有商品）
- 规模提示（高流量，百万级记录）
- 数据库偏好（SQL/NoSQL）- 如未指定，默认为 SQL

---

## 触发器

| 触发器 | 示例 |
|---------|---------|
| `设计模式` | "设计用户认证模式" |
| `数据库设计` | "多租户 SaaS 的数据库设计" |
| `创建表` | "创建博客系统的表" |
| `模式为` | "库存管理模式" |
| `建模数据` | "实时分析建模数据" |
| `我需要一个数据库` | "我需要一个用于跟踪订单的数据库" |
| `设计 NoSQL` | "设计产品目录的 NoSQL 模式" |

---

## 关键术语

| 术语 | 定义 |
|------|------------|
| **规范化** | 组织数据以减少冗余（1NF → 2NF → 3NF） |
| **3NF** | 第三范式 - 列之间没有传递依赖关系 |
| **OLTP** | 在线事务处理 - 写入密集型，需要规范化 |
| **OLAP** | 在线分析处理 - 读取密集型，受益于反规范化 |
| **外键 (FK)** | 引用另一个表主键的列 |
| **索引** | 加速查询的数据结构（以写入更慢为代价） |
| **访问模式** | 您的应用如何读取/写入数据（查询、连接、过滤） |
| **反规范化** | 故意重复数据以加快读取 |

---

## 快速参考

| 任务 | 方法 | 关键考虑 |
|------|----------|-------------------|
| 新模式 | 首先规范化到 3NF | 域建模优于 UI |
| SQL 与 NoSQL | 访问模式决定 | 读写比例很重要 |
| 主键 | INT 或 UUID | UUID 用于分布式系统 |
| 外键 | 总是约束 | ON DELETE 策略至关重要 |
| 索引 | 外键 + WHERE 列 | 列顺序很重要 |
| 迁移 | 总是可逆 | 首先向后兼容 |

---

## 流程概述

```
您的数据需求
    |
    v
+-----------------------------------------------------+
| 第一阶段：分析                                       |
| * 识别实体和关系                                   |
| * 确定访问模式（读取密集型 vs 写入密集型）           |
| * 根据需求选择 SQL 或 NoSQL                        |
+-----------------------------------------------------+
    |
    v
+-----------------------------------------------------+
| 第二阶段：设计                                       |
| * 规范化到 3NF (SQL) 或嵌入/引用 (NoSQL)            |
| * 定义主键和外键                                   |
| * 选择合适的数据类型                               |
| * 添加约束（UNIQUE、CHECK、NOT NULL）               |
+-----------------------------------------------------+
    |
    v
+-----------------------------------------------------+
| 第三阶段：优化                                       |
| * 规划索引策略                                    |
| * 考虑反规范化以优化读取密集型查询                 |
| * 添加时间戳（created_at、updated_at）             |
+-----------------------------------------------------+
    |
    v
+-----------------------------------------------------+
| 第四阶段：迁移                                       |
| * 生成迁移脚本（up + down）                        |
| * 确保向后兼容                                    |
| * 规划零停机部署                                  |
+-----------------------------------------------------+
    |
    v
生产就绪模式
```

---

## 命令

| 命令 | 使用时机 | 动作 |
|---------|-------------|--------|
| `设计模式为 {领域}` | 从头开始 | 完整模式生成 |
| `规范化 {表}` | 修复现有表 | 应用规范化规则 |
| `为 {表} 添加索引` | 性能问题 | 生成索引策略 |
| `为 {变更} 迁移` | 模式演进 | 创建可逆迁移 |
| `审查模式` | 代码审查 | 审计现有模式 |

**工作流：** 从 `设计模式` 开始 → 使用 `规范化` 迭代 → 使用 `添加索引` 优化 → 使用 `迁移` 演进

---

## 核心原则

| 原则 | 原因 | 实现 |
|-----------|-----|----------------|
| 建模领域 | UI 变化，领域不变 | 实体名称反映业务概念 |
| 数据完整性优先 | 损坏难以修复 | 数据库层面的约束 |
| 针对访问模式优化 | 无法同时优化 | OLTP：规范化，OLAP：反规范化 |
| 规划扩展性 | 事后补救很痛苦 | 索引策略 + 分区计划 |

---

## 反模式

| 避免 | 原因 | 而应 |
|-------|-----|---------|
| 每处使用 VARCHAR(255) | 浪费存储，隐藏意图 | 根据字段适当大小 |
| 使用 FLOAT 存储金钱 | 四舍五入错误 | DECIMAL(10,2) |
| 缺少外键约束 | 存在孤立数据 | 总是定义外键 |
| 外键缺少索引 | 慢连接 | 每个外键都加索引 |
| 将日期存储为字符串 | 无法比较/排序 | DATE、TIMESTAMP 类型 |
| 查询中使用 SELECT * | 获取不必要的数据 | 显式列列表 |
| 非可逆迁移 | 无法回滚 | 总是编写 DOWN 迁移 |
| 添加 NOT NULL 而无默认值 | 破坏现有行 | 添加可空，回填，然后约束 |

---

## 验证清单

设计模式后：

- [ ] 每个表都有主键
- [ ] 所有关系都有外键约束
- [ ] 每个外键都定义了 ON DELETE 策略
- [ ] 所有外键都有索引
- [ ] 经常查询的列都有索引
- [ ] 合适的数据类型（金钱使用 DECIMAL 等）
- [ ] 必填字段有 NOT NULL
- [ ] 需要的地方有 UNIQUE 约束
- [ ] 有验证的 CHECK 约束
- [ ] 有 created_at 和 updated_at 时间戳
- [ ] 迁移脚本可逆
- [ ] 在预发布环境使用生产数据测试

---

<details>
<summary><strong>深入：规范化 (SQL)</strong></summary>

### 规范化形式

| 形式 | 规则 | 违例示例 |
|------|------|-------------------|
| **1NF** | 原子值，无重复组 | `product_ids = '1,2,3'` |
| **2NF** | 1NF + 无部分依赖 | order_items 中的 customer_name |
| **3NF** | 2NF + 无传递依赖 | 由 postal_code 推导出的 country |

### 第一范式 (1NF)

```sql
-- BAD: 列中包含多个值
CREATE TABLE orders (
  id INT PRIMARY KEY,
  product_ids VARCHAR(255)  -- '101,102,103'
);

-- GOOD: 分离表存储项
CREATE TABLE orders (
  id INT PRIMARY KEY,
  customer_id INT
);

CREATE TABLE order_items (
  id INT PRIMARY KEY,
  order_id INT REFERENCES orders(id),
  product_id INT
);
```

### 第二范式 (2NF)

```sql
-- BAD: customer_name 只依赖于 customer_id
CREATE TABLE order_items (
  order_id INT,
  product_id INT,
  customer_name VARCHAR(100),  -- 部分依赖!
  PRIMARY KEY (order_id, product_id)
);

-- GOOD: 客户数据在单独表中
CREATE TABLE customers (
  id INT PRIMARY KEY,
  name VARCHAR(100)
);
```

### 第三范式 (3NF)

```sql
-- BAD: country 依赖于 postal_code
CREATE TABLE customers (
  id INT PRIMARY KEY,
  postal_code VARCHAR(10),
  country VARCHAR(50)  -- 传递依赖!
);

-- GOOD: 分离 postal_codes 表
CREATE TABLE postal_codes (
  code VARCHAR(10) PRIMARY KEY,
  country VARCHAR(50)
);
```

### 何时反规范化

| 情景 | 反规范化策略 |
|----------|-------------------------|
| 读取密集型报告 | 预计算聚合 |
| 昂贵的连接 | 缓存派生列 |
| 分析仪表板 | 物化视图 |

```sql
-- 为性能反规范化
CREATE TABLE orders (
  id INT PRIMARY KEY,
  customer_id INT,
  total_amount DECIMAL(10,2),  -- 计算
  item_count INT               -- 计算
);
```

</details>

<details>
<summary><strong>深入：数据类型</strong></summary>

### 字符串类型

| 类型 | 用途 | 示例 |
|------|----------|---------|
| CHAR(n) | 固定长度 | 州代码，ISO 日期 |
| VARCHAR(n) | 可变长度 | 名称，电子邮件 |
| TEXT | 长内容 | 文章，描述 |

```sql
-- 合适的大小
email VARCHAR(255)
phone VARCHAR(20)
country_code CHAR(2)
```

### 数值类型

| 类型 | 范围 | 用途 |
|------|-------|----------|
| TINYINT | -128 到 127 | 年龄，状态代码 |
| SMALLINT | -32K 到 32K | 数量 |
| INT | -2.1B 到 2.1B | ID，计数 |
| BIGINT | 非常大 | 大 ID，时间戳 |
| DECIMAL(p,s) | 精确精度 | 金钱 |
| FLOAT/DOUBLE | 近似值 | 科学数据 |

```sql
-- 总是使用 DECIMAL 存储金钱
price DECIMAL(10, 2)  -- $99,999,999.99

-- 从不使用 FLOAT 存储金钱
price FLOAT  -- 四舍五入错误!
```

### 日期/时间类型

```sql
DATE        -- 2025-10-31
TIME        -- 14:30:00
DATETIME    -- 2025-10-31 14:30:00
TIMESTAMP   -- 自动时区转换

-- 总是存储为 UTC
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
```

### 布尔值

```sql
-- PostgreSQL
is_active BOOLEAN DEFAULT TRUE

-- MySQL
is_active TINYINT(1) DEFAULT 1
```

</details>

<details>
<summary><strong>深入：索引策略</strong></summary>

### 何时创建索引

| 总是索引 | 原因 |
|--------------|--------|
| 外键 | 加速连接 |
| WHERE 子句列 | 加速过滤 |
| ORDER BY 列 | 加速排序 |
| 唯一约束 | 强制唯一性 |

```sql
-- 外键索引
CREATE INDEX idx_orders_customer ON orders(customer_id);

-- 查询模式索引
CREATE INDEX idx_orders_status_date ON orders(status, created_at);
```

### 索引类型

| 类型 | 适用于 | 示例 |
|------|----------|---------|
| B-Tree | 范围，等值 | `price > 100` |
| Hash | 仅精确匹配 | `email = 'x@y.com'` |
| 全文 | 文本搜索 | `MATCH AGAINST` |
| 部分索引 | 行的子集 | `WHERE is_active = true` |

### 复合索引顺序

```sql
CREATE INDEX idx_customer_status ON orders(customer_id, status);

-- 使用索引（customer_id 首先使用）
SELECT * FROM orders WHERE customer_id = 123;
SELECT * FROM orders WHERE customer_id = 123 AND status = 'pending';

-- 不使用索引（仅 status 单独使用）
SELECT * FROM orders WHERE status = 'pending';
```

**规则：** 最具选择性的列优先，或列单独查询最多。

### 索引陷阱

| 陷阱 | 问题 | 解决方案 |
|-------|---------|----------|
| 过度索引 | 慢写入 | 只索引查询的列 |
| 错误的列顺序 | 未使用的索引 | 匹配查询模式 |
| 缺少外键索引 | 慢连接 | 总是索引外键 |

</details>

<details>
<summary><strong>深入：约束</strong></summary>

### 主键

```sql
-- 自增（简单）
id INT AUTO_INCREMENT PRIMARY KEY

-- UUID（分布式系统）
id CHAR(36) PRIMARY KEY DEFAULT (UUID())

-- 复合键（连接表）
PRIMARY KEY (student_id, course_id)
```

### 外键

```sql
FOREIGN KEY (customer_id) REFERENCES customers(id)
  ON DELETE CASCADE     -- 删除子项时删除父项
  ON DELETE RESTRICT    -- 阻止删除如果被引用
  ON DELETE SET NULL    -- 父项删除时设为 NULL
  ON UPDATE CASCADE     -- 父项变更时更新子项
```

| 策略 | 使用时机 |
|----------|----------|
| CASCADE | 依赖数据（order_items） |
| RESTRICT | 重要引用 | 防止意外删除 |
| SET NULL | 可选关系 |

### 其他约束

```sql
-- 唯一
email VARCHAR(255) UNIQUE NOT NULL

-- 复合唯一
UNIQUE (student_id, course_id)

-- 检查
price DECIMAL(10,2) CHECK (price >= 0)
discount INT CHECK (discount BETWEEN 0 AND 100)

-- 非空
name VARCHAR(100) NOT NULL
```

</details>

<details>
<summary><strong>深入：关系模式</strong></summary>

### 一对多

```sql
CREATE TABLE orders (
  id INT PRIMARY KEY,
  customer_id INT NOT NULL REFERENCES customers(id)
);

CREATE TABLE order_items (
  id INT PRIMARY KEY,
  order_id INT NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
  product_id INT NOT NULL,
  quantity INT NOT NULL
);
```

### 多对多

```sql
-- 连接表
CREATE TABLE enrollments (
  student_id INT REFERENCES students(id) ON DELETE CASCADE,
  course_id INT REFERENCES courses(id) ON DELETE CASCADE,
  enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (student_id, course_id)
);
```

### 自引用

```sql
CREATE TABLE employees (
  id INT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  manager_id INT REFERENCES employees(id)
);
```

### 多态

```sql
-- 方法 1：分离外键（更强的完整性）
CREATE TABLE comments (
  id INT PRIMARY KEY,
  content TEXT NOT NULL,
  post_id INT REFERENCES posts(id),
  photo_id INT REFERENCES photos(id),
  CHECK (
    (post_id IS NOT NULL AND photo_id IS NULL) OR
    (post_id IS NULL AND photo_id IS NOT NULL)
  )
);

-- 方法 2：类型 + ID（灵活，较弱完整性）
CREATE TABLE comments (
  id INT PRIMARY KEY,
  content TEXT NOT NULL,
  commentable_type VARCHAR(50) NOT NULL,
  commentable_id INT NOT NULL
);
```

</details>

<details>
<summary><strong>深入：NoSQL 设计 (MongoDB)</strong></summary>

### 嵌入 vs 引用

| 因素 | 嵌入 | 引用 |
|--------|-------|-----------|
| 访问模式 | 一起读取 | 分别读取 |
| 关系 | 1:少数 | 1:多数 |
| 文档大小 | 小 | 接近 16MB |
| 更新频率 | 很少 | 频繁 |

### 嵌入文档

```json
{
  "_id": "order_123",
  "customer": {
    "id": "cust_456",
    "name": "Jane Smith",
    "email": "jane@example.com"
  },
  "items": [
    { "product_id": "prod_789", "quantity": 2, "price": 29.99 }
  ],
  "total": 109.97
}
```

### 引用文档

```json
{
  "_id": "order_123",
  "customer_id": "cust_456",
  "item_ids": ["item_1", "item_2"],
  "total": 109.97
}
```

### MongoDB 索引

```javascript
// 单字段
db.users.createIndex({ email: 1 }, { unique: true });

// 复合
db.orders.createIndex({ customer_id: 1, created_at: -1 });

// 文本搜索
db.articles.createIndex({ title: "text", content: "text" });

// 地理空间
db.stores.createIndex({ location: "2dsphere" });
```

</details>

<details>
<summary><strong>深入：迁移</strong></summary>

### 迁移最佳实践

| 实践 | 原因 |
|----------|-----|
| 总是可逆 | 需要回滚 |
| 向后兼容 | 零停机部署 |
| 数据库先于数据 | 分离关注点 |
| 在预发布环境测试 | 早期发现问题 |

### 添加列（零停机）

```sql
-- 第 1 步：添加可空列
ALTER TABLE users ADD COLUMN phone VARCHAR(20);

-- 第 2 步：部署写入新列的代码

-- 第 3 步：回填现有行
UPDATE users SET phone = '' WHERE phone IS NULL;

-- 第 4 步：设为必需（如果需要）
ALTER TABLE users MODIFY phone VARCHAR(20) NOT NULL;
```

### 重命名列（零停机）

```sql
-- 第 1 步：添加新列
ALTER TABLE users ADD COLUMN email_address VARCHAR(255);

-- 第 2 步：复制数据
UPDATE users SET email_address = email;

-- 第 3 步：部署读取新列的代码
-- 第 4 步：部署写入新列的代码

-- 第 5 步：删除旧列
ALTER TABLE users DROP COLUMN email;
```

### 迁移模板

```sql
-- 迁移：YYYYMMDDHHMMSS_描述.sql

-- UP
BEGIN;
ALTER TABLE users ADD COLUMN phone VARCHAR(20);
CREATE INDEX idx_users_phone ON users(phone);
COMMIT;

-- DOWN
BEGIN;
DROP INDEX idx_users_phone ON users;
ALTER TABLE users DROP COLUMN phone;
COMMIT;
```

</details>

<details>
<summary><strong>深入：性能优化</strong></summary>

### 查询分析

```sql
EXPLAIN SELECT * FROM orders
WHERE customer_id = 123 AND status = 'pending';
```

| 查找 | 含义 |
|----------|---------|
| type: ALL | 全表扫描（差） |
| type: ref | 使用索引（好） |
| key: NULL | 未使用索引 |
| rows: 高 | 扫描多行 |

### N+1 查询问题

```python
# BAD: N+1 查询
orders = db.query("SELECT * FROM orders")
for order in orders:
    customer = db.query(f"SELECT * FROM customers WHERE id = {order.customer_id}")

# GOOD: 单个 JOIN
results = db.query("""
    SELECT orders.*, customers.name
    FROM orders
    JOIN customers ON orders.customer_id = customers.id
""")
```

### 优化技术

| 技术 | 使用时机 |
|-----------|-------------|
| 添加索引 | WHERE/ORDER BY 慢 |
| 反规范化 | 昂贵的 JOIN |
| 分页 | 大结果集 |
| 缓存 | 重复查询 |
| 读取副本 | 读取密集型负载 |
| 分区 | 非常大的表 |

</details>

---

## 扩展点

1. **数据库特定模式：** 添加 MySQL vs PostgreSQL vs SQLite 变体
2. **高级模式：** 时间序列，事件溯源，CQRS，多租户
3. **ORM 集成：** TypeORM，Prisma，SQLAlchemy 模式
4. **监控：** 查询性能跟踪，慢查询警报
