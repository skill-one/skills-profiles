**首先**：使用父级 `neon` 技能获取 Neon 概览、入门 Neon、Neon 开发最佳实践等内容。

如果未安装 `neon` 技能，请从 https://neon.com/docs/ai/skills/neon/SKILL.md 获取或使用以下命令安装：

```bash
neon skills -s neon -y
```

# Postgres Egress 优化器

指导用户诊断和修复导致 Postgres 数据库过度数据传输（egress）的应用端查询模式。大多数高 egress 账单都来自应用获取了超出所需的数据。

按顺序执行以下四个步骤：**诊断**哪些查询传输了最多数据、**分析**这些查询背后的代码库、**修复**反模式，然后**验证**没有出现故障且数据传输确实减少。

## 第 1 步：诊断

识别哪些查询传输了最多数据。主要工具是 `pg_stat_statements` 扩展。

### 检查 `pg_stat_statements` 是否可用

```sql
SELECT 1 FROM pg_stat_statements LIMIT 1;
```

如果出现错误，需要创建扩展：

```sql
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
```

在 Neon 上，该扩展默认可用，但可能仍需要执行此 `CREATE EXTENSION` 步骤。

### 处理空统计信息

当 Neon 计算扩展到零并重启时，统计信息会被清除。如果统计信息为空或计算最近刚唤醒：

1. 重置统计信息以开始干净的测量窗口：`SELECT pg_stat_statements_reset();`
2. 让应用在代表性流量下运行至少一小时。
3. 返回并运行下面的诊断查询。

如果用户有生产数据库的统计信息，请使用这些信息。如果用户无法访问生产统计信息，请直接进行第 2 步分析代码库——代码级模式通常足以识别最严重的违规者。

### 诊断查询

运行这些查询以识别主要的 egress 贡献者。重点关注返回多行、返回宽行（JSONB、TEXT、BYTEA 列）或被频繁调用的查询。

**返回总行数最多的查询：**

```sql
SELECT query, calls, rows AS total_rows, rows / calls AS avg_rows_per_call
FROM pg_stat_statements
WHERE calls > 0
ORDER BY rows DESC
LIMIT 10;
```

**每执行一次返回行数最多的查询**（范围不明确的 SELECT、缺少分页）：

```sql
SELECT query, calls, rows AS total_rows, rows / calls AS avg_rows_per_call
FROM pg_stat_statements
WHERE calls > 0
ORDER BY avg_rows_per_call DESC
LIMIT 10;
```

**最频繁调用的查询**（缓存候选）：

```sql
SELECT query, calls, rows AS total_rows, rows / calls AS avg_rows_per_call
FROM pg_stat_statements
WHERE calls > 0
ORDER BY calls DESC
LIMIT 10;
```

**运行时间最长的查询**（不是直接的 egress 指标，但有助于在突发期间识别问题查询）：

```sql
SELECT query, calls, rows AS total_rows,
  round(total_exec_time::numeric, 2) AS total_exec_time_ms
FROM pg_stat_statements
WHERE calls > 0
ORDER BY total_exec_time DESC
LIMIT 10;
```

### 解释结果

按估计的 egress 影响 对发现进行排序：

- **高行数 + 宽行** = 最大的 egress。一个返回 1,000 行且每行包含 50KB JSONB 列的查询每次调用传输约 50MB。
- **极端调用频率** 即使在小查询上也累积起来。一个每天调用 50,000 次返回 10 行的查询 = 每天 500,000 行。
- **与模式交叉引用** 以识别哪些列是宽的。查找 JSONB、TEXT、BYTEA 和大型 VARCHAR 列。

## 第 2 步：分析代码库

对于第 1 步中识别的每个查询，或者如果没有统计信息，则对代码库中的每个数据库查询，检查：

- 是否仅选择响应所需的列？
- 是否返回有限数量的行（LIMIT/分页）？
- 是否频繁调用以从缓存中受益？
- 是否获取原始数据并在应用代码中聚合？
- 是否使用一个 JOIN 在子行中重复父数据？

## 第 3 步：修复

对每个发现的问题应用适当的修复。以下是常见的 egress 反模式及其修复方法。

### 未使用的列（SELECT \*）

**问题**：查询获取所有列但应用仅使用其中几列。大型列（JSONB 块、TEXT 字段）在传输过程中被获取并丢弃。

**修复**：仅选择响应所需的列。

**之前：**

```sql
SELECT * FROM products;
```

**之后：**

```sql
SELECT id, name, price, image_urls FROM products;
```

### 缺少分页

**问题**：一个列表端点返回所有行而没有 LIMIT。这是一个无限制的 egress 风险——表中的每一行新数据都会增加每次请求的数据传输。无论当前表大小如何，都应标记此问题。

由于应用可能在小数据集上工作正常，因此容易忽略这一点。但在规模上，一个未分页的端点返回 10,000 行，即使列宽度适中，每天也可能传输数百兆字节。

**修复**：使用 `ORDER BY` 加上 `LIMIT`/`OFFSET` 来限制结果集。

**之前：**

```sql
SELECT id, name, price FROM products;
```

**之后：**

```sql
SELECT id, name, price FROM products
ORDER BY id
LIMIT 50 OFFSET 0;
```

添加分页时，检查消费客户端是否支持分页响应。如果不支持，请选择合理的默认值，并在 API 中记录分页参数。

### 静态数据的高频查询

**问题**：一个查询每天被调用数千次，但返回的数据很少变化。每次调用都会从数据库传输相同的行。这种模式只能从 `pg_stat_statements` 中看到——代码本身看起来正常。

查找与其他查询相比调用次数极高的查询。常见示例：配置表、分类列表、功能标志、用户角色定义。

**修复**：在应用和数据库之间添加缓存层，以避免每次请求都击中数据库。

### 应用端聚合

**问题**：应用从表中获取所有行，然后在应用代码中计算聚合（平均值、计数、总和、分组）。即使结果是一个小的摘要，完整的 dataset 也会传输到线上。

**修复**：将聚合推入 SQL。

**之前**：应用获取整个表并在代码中使用循环或 `.reduce()` 进行聚合。

**之后：**

```sql
SELECT p.category_id,
       AVG(r.rating) AS avg_rating,
       COUNT(r.id) AS review_count
FROM reviews r
INNER JOIN products p ON r.product_id = p.id
GROUP BY p.category_id;
```

### JOIN 重复

**问题**：一个宽父表和子表之间的 JOIN 在每个子行中重复所有父列。如果一个产品有 200 条评论，且产品行包含一个 50KB JSONB 列，JOIN 会为单个请求发送 50KB × 200 = ~10MB。

这与 SELECT \* 的问题不同。即使您仅选择所需的列，JOIN 仍然会为每个子行重复父数据。修复是结构性的：完全避免 JOIN。

**修复**：将 JOIN 分成两个查询，每个表一个。

**之前：**

```sql
SELECT * FROM products
LEFT JOIN reviews ON reviews.product_id = products.id
WHERE products.id = 1;
```

**之后（两个独立的查询）：**

```sql
SELECT id, name, price, description, image_urls FROM products WHERE id = 1;
SELECT id, user_name, rating, body FROM reviews WHERE product_id = 1;
```

一个查询而不是一个 JOIN。产品数据被获取一次。评论被获取一次。没有重复。

## 第 4 步：验证

应用修复后：

1. **运行现有测试** 以确认没有出现故障。
2. **检查响应** —— 确保 API 仍然返回相同的数据形状。列选择和分页更改可能会破坏依赖特定字段或完整结果集的客户端。
3. **衡量改进** —— 如果有 `pg_stat_statements` 数据，请重置它 (`SELECT pg_stat_statements_reset();`)，让流量运行，然后重新运行诊断查询以比较之前和之后。

## Neon 基础设施即代码 (`neon.ts`)

上述修复减少了 **egress**（从 Postgres 传输出的数据）。另一个主要的非生产成本杠杆是 **compute**，您可以在 `neon.ts` 中持久编码它——Neon 的基础设施即代码文件（参考 `neon` 技能获取完整参考）——以便开发、预览和 CI 分支默认保持低成本，而不是依赖每个分支的标志：

```bash
npm i @neon/config
```

```typescript
// neon.ts
import { defineConfig } from "@neon/config/v1";

export default defineConfig({
  branch: (branch) => {
    if (branch.exists || branch.isDefault) return {}; // 不要修改生产环境
    return {
      ttl: "7d", // 临时分支自动过期而不是累积存储
      postgres: {
        computeSettings: {
          autoscalingLimitMinCu: 0.25, // 空闲时扩展到零
          autoscalingLimitMaxCu: 1, // 在一次性分支上限制自动扩展
          suspendTimeout: "5m",
        },
      },
    };
  },
});
```

```bash
neon config apply   # 应用到当前分支（neon deploy 是别名）
```

这是补充而非替代：查询模式修复实际减少 egress 费用，而这些设置防止非生产 compute 和存储悄悄推高相同的账单。因为 `neon checkout` 在创建分支时应用策略，新的 dev/preview 分支会自动继承低成本配置。

## 更多阅读

- https://neon.com/docs/introduction/network-transfer.md
- https://neon.com/docs/introduction/cost-optimization.md
