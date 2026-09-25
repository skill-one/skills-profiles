# SQL Pro

## 核心工作流

1. **模式分析** - 审查数据库结构、索引、查询模式、性能瓶颈
2. **设计** - 使用CTE、窗口函数、适当的连接创建集合操作
3. **优化** - 分析执行计划、实现覆盖索引、消除表扫描
4. **验证** - 运行 `EXPLAIN ANALYZE` 并确认大表没有顺序扫描；如果查询未达到小于100毫秒的目标，则在继续之前迭代索引选择或查询重写
5. **文档化** - 提供查询解释、索引理由、性能指标

## 参考指南

根据上下文加载详细指导：

| 主题 | 参考 | 加载时机 |
|------|------|----------|
| 查询模式 | `references/query-patterns.md` | 连接、CTE、子查询、递归查询 |
| 窗口函数 | `references/window-functions.md` | ROW_NUMBER、RANK、LAG/LEAD、分析 |
| 优化 | `references/optimization.md` | EXPLAIN计划、索引、统计信息、调整 |
| 数据库设计 | `references/database-design.md` | 正规化、键、约束、模式 |
| 方言差异 | `references/dialect-differences.md` | PostgreSQL与MySQL与SQL Server的具体差异 |

## 快速参考示例

### CTE模式
```sql
-- 将昂贵的子查询逻辑隔离以供重用和可读性
WITH 排名订单 AS (
    SELECT
        客户ID,
        订单ID,
        总金额,
        ROW_NUMBER() OVER (PARTITION BY 客户ID ORDER BY 订单日期 DESC) AS rn
    FROM 订单
    WHERE 状态 = '已完成'          -- 在连接之前尽早过滤
)
SELECT 客户ID, 订单ID, 总金额
FROM 排名订单
WHERE rn = 1;                           -- 每个客户的最新已完成订单
```

### 窗口函数模式
```sql
-- 分区内运行总和和排名 — 无需自连接
SELECT
    部门ID,
    员工ID,
    薪水,
    SUM(薪水)  OVER (PARTITION BY 部门ID ORDER BY 雇佣日期) AS 运行工资,
    RANK()       OVER (PARTITION BY 部门ID ORDER BY 薪水 DESC) AS 薪水排名
FROM 员工;
```

### EXPLAIN ANALYZE解释
```sql
-- PostgreSQL：始终使用ANALYZE查看实际行数与估计值
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT *
FROM 订单 o
JOIN 客户 c ON c.id = o.customer_id
WHERE o.created_at > NOW() - INTERVAL '30 days';
```
输出中需要检查的关键点：
- **大表的顺序扫描** → 添加或修复索引
- **实际行数 ≫ 估计行数** → 运行 `ANALYZE <表>` 以刷新统计信息
- **缓冲区：共享命中** vs **读取** → 高 `读取` 计数表示缺少缓存 / 索引

### 优化前/优化后示例
```sql
-- 优化前：相关子查询，每行一个执行（慢）
SELECT 订单ID,
       (SELECT SUM(数量) FROM 订单项 oi WHERE oi.订单ID = o.id) AS 物品数量
FROM 订单 o;

-- 优化后：单个聚合连接（快）
SELECT o.订单ID, COALESCE(聚合.物品数量, 0) AS 物品数量
FROM 订单 o
LEFT JOIN (
    SELECT 订单ID, SUM(数量) AS 物品数量
    FROM 订单项
    GROUP BY 订单ID
) 聚合 ON 聚合.订单ID = o.id;

-- 支持覆盖索引（包含查询接触的所有列）
CREATE INDEX idx_order_items_order_qty
    ON 订单项 (订单ID)
    INCLUDE (数量);
```

## 约束

### 必须做
- 在推荐优化之前分析执行计划
- 使用集合操作而不是逐行处理
- 在可能的情况下在查询执行早期应用过滤
- 使用EXISTS而不是COUNT进行存在性检查
- 在比较和聚合中明确处理NULL
- 为频繁查询创建覆盖索引
- 使用生产规模的数据量进行测试

### 绝对不要做
- 在生产查询中使用SELECT *
- 当集合操作有效时使用游标
- 在针对特定方言时忽略平台特定优化
- 在不考虑数据量和基数的情况下实施解决方案

## 输出模板

在实施SQL解决方案时，提供：
1. 带有内联注释的优化查询
2. 所需索引及其理由
3. 执行计划分析
4. 性能指标（前后）
5. 如适用，平台特定说明

[文档](https://jeffallan.github.io/claude-skills/skills/language/sql-pro/)
