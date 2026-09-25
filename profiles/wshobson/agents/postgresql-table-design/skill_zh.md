# PostgreSQL 表设计

## 使用场景

- 设计新的 PostgreSQL 模式，或在发布前评审现有模式。
- 选择 PostgreSQL 特定的列类型、键、约束或索引。
- 决定如何分区大表，或如何存储半结构化数据。
- 规划在不停机的情况下对在线数据库进行模式变更。

PostgreSQL 模式的规则和决策点。完整的数据类型目录、工作负载模式（更新密集型、插入密集型、upsert、模式演化）、扩展、JSONB 索引和示例 DDL 在 `references/details.md` 中；当下方某部分指向此处时，请打开它。

## 核心规则

- 为参考表（用户、订单等）定义一个 **PRIMARY KEY**。时间序列/事件/日志数据通常不需要。使用时，优先选择 `BIGINT GENERATED ALWAYS AS IDENTITY`；仅在需要全局唯一性/保密性时使用 `UUID`。
- 首先进行 **规范化（至 3NF）** 以消除数据冗余和更新异常；仅在经过验证的连接性能存在问题的、具有高投资回报率的读取操作中才进行反规范化。
- 在语义上需要时，在所有地方添加 **NOT NULL**；使用 **DEFAULT** 为常用值提供默认值。
- 为实际查询的访问路径创建索引：主键/唯一键（自动）、**外键列（手动！）**、频繁的过滤/排序和连接键。
- 优先选择 **TIMESTAMPTZ** 用于事件时间；**NUMERIC** 用于金钱；**TEXT** 用于字符串；**BIGINT** 用于整数；**DOUBLE PRECISION** 用于浮点数（或 `NUMERIC` 用于精确的小数运算）。

## PostgreSQL 注意事项

- **标识符**：未加引号 → 转换为小写。避免使用引号/混合大小写名称；使用 `snake_case`。
- **唯一 + NULL**：UNIQUE 允许多个 NULL。使用 `UNIQUE NULLS NOT DISTINCT (...)`（PG15+）限制为单个 NULL。
- **外键索引**：PostgreSQL **不** 自动索引外键列。请添加它们。
- **无静默强制转换**：长度/精度溢出会导致错误（不会截断）。将 999 插入 `NUMERIC(2,0)` 会失败，而不会像某些数据库那样静默截断或四舍五入。
- **序列/identity 存在间隙**（正常；不要“修复”）。回滚、崩溃和并发事务会导致间隙（1, 2, 5, 6...）。
- **堆存储**：默认情况下不进行聚集主键；`CLUSTER` 是一次性重组，不会在后续插入中维护。
- **MVCC**：更新/删除会留下死亡元组；`VACUUM` 会处理它们——设计时避免热点宽行 churn。

## 数据类型

- **ID**：`BIGINT GENERATED ALWAYS AS IDENTITY`；`UUID` 用于分布式或保密 ID，使用 `uuidv7()`（PG18+）或 `gen_random_uuid()` 生成。
- **数字**：除非存储至关重要，否则使用 `BIGINT`；`DOUBLE PRECISION` 优于 `REAL`；`NUMERIC(p,s)` 用于金钱和精确小数。
- **字符串**：`TEXT`，当需要限制长度时使用 `CHECK (LENGTH(col) <= n)`；`BYTEA` 用于二进制。不区分大小写的查找：表达式索引 `LOWER(email)`，或 `CITEXT` 当约束必须不区分大小写时。
- **时间**：`TIMESTAMPTZ`、`DATE`、`INTERVAL`。`now()` 是事务开始；`clock_timestamp()` 是墙上时钟。
- **布尔值**：`BOOLEAN NOT NULL`，除非需要三态。
- **枚举**：`CREATE TYPE ... AS ENUM` 仅适用于小而稳定的集合；变化的业务值使用 `TEXT` + `CHECK` 或查找表。
- **JSONB** 优于 JSON，使用 GIN 索引，仅用于可选/半结构化属性。
- 数组、范围、网络、几何、全文、域、复合和向量类型，以及 TOAST 存储和排序控制：参见 `references/details.md`。

### 应避免的类型

| 避免 | 使用替代 |
|---|---|
| `timestamp`（无时区） | `timestamptz` |
| `char(n)`、`varchar(n)` | `text`（如果需要，添加 `CHECK` 对长度进行限制） |
| `money` | `numeric` |
| `timetz` | `timestamptz` |
| `timestamptz(0)` 或任何精度 | `timestamptz` |
| `serial` | `generated always as identity` |

## 约束

- **PK**：隐式唯一 + NOT NULL；创建 B-tree 索引。
- **FK**：指定 `ON DELETE/UPDATE`（`CASCADE`、`RESTRICT`、`SET NULL`、`SET DEFAULT`）。索引引用列。使用 `DEFERRABLE INITIALLY DEFERRED` 处理循环依赖，在提交时检查。
- **UNIQUE**：创建 B-tree 索引；允许多个 NULL，除非 `NULLS NOT DISTINCT`（PG15+）。优先选择 `NULLS NOT DISTINCT`，除非需要重复 NULL。
- **CHECK**：行级；NULL 通过（三值逻辑）。与 `NOT NULL` 结合使用：`price NUMERIC NOT NULL CHECK (price > 0)`。
- **EXCLUDE**：防止与运算符重叠，例如 `EXCLUDE USING gist (room_id WITH =, booking_period WITH &&)` 防止重复预订。需要 GiST 支持的类型。

## 索引

- **B-tree**：默认用于等值/范围查询（`=`、`<`、`>`、`BETWEEN`、`ORDER BY`）。
- **复合**：最选择性列优先（`WHERE a = ? AND b > ?` 使用 `(a,b)`；`WHERE b = ?` 不使用）。最选择性列优先。
- **覆盖**：`CREATE INDEX ON tbl (id) INCLUDE (name, email)` 用于索引扫描。
- **部分**：热点子集，`CREATE INDEX ON tbl (user_id) WHERE status = 'active'`。
- **表达式**：`CREATE INDEX ON tbl (LOWER(email))`；查询必须使用相同的表达式。
- **GIN**：JSONB 包含/存在、数组、全文搜索。**GiST**：范围、几何、排除约束。
- **BRIN**：大型、自然排序数据（时间序列）以最低存储成本；当磁盘顺序与索引列相关时有效。

## 分区

- 用于大于 100 万行的表，其查询始终按分区键过滤，或维护（修剪、批量替换）遵循键。
- **RANGE** 用于时间序列（`PARTITION BY RANGE (created_at)`；**TimescaleDB** 自动化它，具有保留和压缩），**LIST** 用于离散值，**HASH** 用于无自然键的均匀分布。
- **约束排除**：规划器通过它们的 `CHECK` 约束修剪分区；声明式分区（PG10+）为您创建它们。
- 优先选择声明式分区或超表。**不要**使用表继承。
- **限制**：无全局唯一约束——在主键/唯一键中包含分区键。来自分区表的 FK 需要 PG11+；引用分区表的 FK 需要 PG12+；在旧版本中，使用触发器。

## 示例

```sql
CREATE TABLE users (
  user_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  email TEXT NOT NULL UNIQUE,
  name TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX ON users (LOWER(email));
CREATE INDEX ON users (created_at);
```

```sql
CREATE TABLE orders (
  order_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(user_id),
  status TEXT NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING','PAID','CANCELED')),
  total NUMERIC(10,2) NOT NULL CHECK (total > 0),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX ON orders (user_id);
CREATE INDEX ON orders (created_at);
```

```sql
-- JSONB 属性具有生成的、可索引的标量
CREATE TABLE profiles (
  user_id BIGINT PRIMARY KEY REFERENCES users(user_id),
  attrs JSONB NOT NULL DEFAULT '{}',
  theme TEXT GENERATED ALWAYS AS (attrs->>'theme') STORED
);
CREATE INDEX profiles_attrs_gin ON profiles USING GIN (attrs);
```

## 深入了解

`references/details.md` 包含本文件仅提及的内容：

- 完整的数据类型目录：TOAST 存储、排序规则、数组、范围、网络、几何、文本搜索、域、复合、向量。
- 表类型（`TEMPORARY`、`UNLOGGED`）和行级安全。
- 约束和索引说明，以及范围、列表和哈希的分区 DDL。
- 工作负载模式：更新密集型、插入密集型、upsert 设计、安全的模式演化。
- 生成的列和扩展（`pg_trgm`、`citext`、`timescaledb`、`postgis`、`pgvector` 等）。
- JSONB 索引策略，包括 `jsonb_path_ops` 和提取的 B-tree 列。
