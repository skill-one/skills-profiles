# PostgreSQL 代码审查助手

对 ${selection} 进行专家级 PostgreSQL 代码审查（若无选择则审查整个项目）。重点关注 PostgreSQL 特有的最佳实践、反模式和独特质量标准。

## 🎯 PostgreSQL 特定审查领域

### JSONB 最佳实践
```sql
-- ❌ BAD: 低效的 JSONB 使用
SELECT * FROM orders WHERE data->>'status' = 'shipped';  -- 不支持索引

-- ✅ GOOD: 可索引的 JSONB 查询
CREATE INDEX idx_orders_status ON orders USING gin((data->'status'));
SELECT * FROM orders WHERE data @> '{"status": "shipped"}';

-- ❌ BAD: 未考虑深层嵌套
UPDATE orders SET data = data || '{"shipping":{"tracking":{"number":"123"}}}';

-- ✅ GOOD: 结构化的 JSONB 带验证
ALTER TABLE orders ADD CONSTRAINT valid_status 
CHECK (data->>'status' IN ('pending', 'shipped', 'delivered'));
```

### 数组操作审查
```sql
-- ❌ BAD: 低效的数组操作
SELECT * FROM products WHERE 'electronics' = ANY(categories);  -- 无索引

-- ✅ GOOD: GIN 索引的数组查询
CREATE INDEX idx_products_categories ON products USING gin(categories);
SELECT * FROM products WHERE categories @> ARRAY['electronics'];

-- ❌ BAD: 循环中的数组连接
-- 这在函数/存储过程中会低效

-- ✅ GOOD: 批量数组操作
UPDATE products SET categories = categories || ARRAY['new_category']
WHERE id IN (SELECT id FROM products WHERE condition);
```

### PostgreSQL 模式设计审查
```sql
-- ❌ BAD: 未使用 PostgreSQL 功能
CREATE TABLE users (
    id INTEGER,
    email VARCHAR(255),
    created_at TIMESTAMP
);

-- ✅ GOOD: PostgreSQL 优化的模式
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email CITEXT UNIQUE NOT NULL,  -- 不区分大小写的邮箱
    created_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    CONSTRAINT valid_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- 添加 JSONB GIN 索引用于 metadata 查询
CREATE INDEX idx_users_metadata ON users USING gin(metadata);
```

### 自定义类型和域
```sql
-- ❌ BAD: 使用通用类型处理特定数据
CREATE TABLE transactions (
    amount DECIMAL(10,2),
    currency VARCHAR(3),
    status VARCHAR(20)
);

-- ✅ GOOD: PostgreSQL 自定义类型
CREATE TYPE currency_code AS ENUM ('USD', 'EUR', 'GBP', 'JPY');
CREATE TYPE transaction_status AS ENUM ('pending', 'completed', 'failed', 'cancelled');
CREATE DOMAIN positive_amount AS DECIMAL(10,2) CHECK (VALUE > 0);

CREATE TABLE transactions (
    amount positive_amount NOT NULL,
    currency currency_code NOT NULL,
    status transaction_status DEFAULT 'pending'
);
```

## 🔍 PostgreSQL 特定反模式

### 性能反模式
- **避免使用 PostgreSQL 特定索引**：未为适当数据类型使用 GIN/GiST
- **误用 JSONB**：将 JSONB 像普通字符串字段一样处理
- **忽略数组操作符**：使用低效的数组操作
- **分区键选择不当**：未有效利用 PostgreSQL 分区

### 模式设计问题
- **未使用 ENUM 类型**：使用 VARCHAR 处理有限值集
- **忽略约束**：缺少数据验证的 CHECK 约束
- **错误的数据类型**：使用 VARCHAR 而非 TEXT 或 CITEXT
- **缺少 JSONB 结构**：无验证的结构化 JSONB

### 函数和触发器问题
```sql
-- ❌ BAD: 低效的触发器函数
CREATE OR REPLACE FUNCTION update_modified_time()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();  -- 应使用 TIMESTAMPTZ
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ✅ GOOD: 优化的触发器函数
CREATE OR REPLACE FUNCTION update_modified_time()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 仅在需要时触发
CREATE TRIGGER update_modified_time_trigger
    BEFORE UPDATE ON table_name
    FOR EACH ROW
    WHEN (OLD.* IS DISTINCT FROM NEW.*)
    EXECUTE FUNCTION update_modified_time();
```

## 📊 PostgreSQL 扩展使用审查

### 扩展最佳实践
```sql
-- ✅ 创建前检查扩展是否存在
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ✅ 合理使用扩展
-- UUID 生成
SELECT uuid_generate_v4();

-- 密码哈希
SELECT crypt('password', gen_salt('bf'));

-- 模糊文本匹配
SELECT word_similarity('postgres', 'postgre');
```

## 🛡️ PostgreSQL 安全审查

### 行级安全 (RLS)
```sql
-- ✅ GOOD: 实现 RLS
ALTER TABLE sensitive_data ENABLE ROW LEVEL SECURITY;

CREATE POLICY user_data_policy ON sensitive_data
    FOR ALL TO application_role
    USING (user_id = current_setting('app.current_user_id')::INTEGER);
```

### 权限管理
```sql
-- ❌ BAD: 过宽的权限
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO app_user;

-- ✅ GOOD: 粒度权限
GRANT SELECT, INSERT, UPDATE ON specific_table TO app_user;
GRANT USAGE ON SEQUENCE specific_table_id_seq TO app_user;
```

## 🎯 PostgreSQL 代码质量检查清单

### 模式设计
- [ ] 使用适当的 PostgreSQL 数据类型 (CITEXT, JSONB, 数组)
- [ ] 利用 ENUM 类型处理约束值
- [ ] 实现适当的 CHECK 约束
- [ ] 使用 TIMESTAMPTZ 而非 TIMESTAMP
- [ ] 定义自定义域用于可重用约束

### 性能考虑
- [ ] 合适的索引类型 (GIN 用于 JSONB/数组, GiST 用于范围)
- [ ] 使用包含操作符 (@>, ?) 的 JSONB 查询
- [ ] 使用 PostgreSQL 特定操作符的数组操作
- [ ] 合理使用窗口函数和 CTE
- [ ] 高效使用 PostgreSQL 特定函数

### PostgreSQL 功能利用
- [ ] 在适当情况下使用扩展
- [ ] 在有益时使用 PL/pgSQL 存储过程
- [ ] 利用 PostgreSQL 的高级 SQL 功能
- [ ] 使用 PostgreSQL 特定的优化技术
- [ ] 在函数中实现适当的错误处理

### 安全和合规
- [ ] 需要时实现行级安全 (RLS)
- [ ] 合适的角色和权限管理
- [ ] 使用 PostgreSQL 的内置加密函数
- [ ] 使用 PostgreSQL 功能实现审计追踪

## 📝 PostgreSQL 特定审查指南

1. **数据类型优化**：确保适当使用 PostgreSQL 特定类型
2. **索引策略**：审查索引类型并确保使用 PostgreSQL 特定索引
3. **JSONB 结构**：验证 JSONB 模式设计和查询模式
4. **函数质量**：审查 PL/pgSQL 函数的效率和最佳实践
5. **扩展使用**：验证 PostgreSQL 扩展的适当使用
6. **性能功能**：检查 PostgreSQL 高级功能的利用
7. **安全实现**：审查 PostgreSQL 特定安全功能

重点关注 PostgreSQL 的独特能力，确保代码利用了 PostgreSQL 的特殊之处，而不是将其当作通用 SQL 数据库处理。
