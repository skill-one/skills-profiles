---
name: postgresql-database-engineering
description: 涵盖索引策略、查询优化、性能调优、分区、复制、备份与恢复、高可用性及生产数据库管理的全面PostgreSQL数据库工程技能。掌握PostgreSQL高级特性，包括MVCC、VACUUM操作、连接池、监控及可扩展性模式。
---

# PostgreSQL 数据库工程

一项全面的 PostgreSQL 数据库工程专业技能，涵盖从查询优化和索引策略到高可用性、复制和生产数据库管理的各个方面。这项技能使您能够在规模上设计、优化和维护高性能的 PostgreSQL 数据库。

## 何时使用此技能

在以下情况下使用此技能：

- 为高性能应用程序设计数据库模式
- 优化慢查询并提高数据库性能
- 实现针对复杂查询模式的索引策略
- 为大型表（100万+行）设置分区
- 配置流式复制和高可用性
- 调整 PostgreSQL 配置以用于生产工作负载
- 实现备份和恢复程序
- 调试性能问题和查询瓶颈
- 使用 pgBouncer 或 PgPool 设置连接池
- 监控数据库健康和性能指标
- 规划数据库迁移和模式更改
- 实现数据库安全和访问控制
- 水平或垂直扩展 PostgreSQL 数据库
- 管理VACUUM操作和数据库维护
- 设置逻辑复制以进行数据分发

## 核心概念

### PostgreSQL 架构

PostgreSQL 使用基于进程的架构，包含几个关键组件：

- **Postmaster 进程**：管理连接的主服务器进程
- **Backend 进程**：每个客户端连接一个，处理查询
- **共享内存**：共享缓冲区、WAL 缓冲区、锁表
- **后台工作进程**：Autovacuum、检查点、WAL 写入器、统计收集器
- **预写式日志（WAL）**：用于持久性和复制的交易日志
- **存储层**：TOAST 用于大值、FSM 用于空闲空间、VM 用于可见性

### MVCC（多版本并发控制）

PostgreSQL 的基础并发机制：

- **快照**：每个事务看到数据的一致快照
- **元组版本**：多个行版本共存以供并发访问
- **事务 ID**：xmin（创建事务）、xmax（删除事务）
- **可见性规则**：确定哪些行版本对事务可见
- **VACUUM**：回收死元组的空间并防止事务回绕
- **FREEZE**：将旧行标记为对所有事务可见

**主要影响：**
- 无读锁 - 读者从不阻塞写者
- 写者从不阻塞读者
- 更新创建新的行版本
- 定期 VACUUM 至关重要
- 死元组积累直到被清理

### 事务隔离级别

PostgreSQL 支持四个隔离级别：

1. **读未提交**：在 PostgreSQL 中视为读已提交
2. **读已提交**（默认）：在语句开始时看到已提交的数据
3. **可重复读**：看到事务开始时的快照
4. **串行化**：具有 SSI 的真正串行化隔离

**选择隔离级别：**
- 读已提交：大多数应用程序，最佳性能
- 可重复读：报告、需要一致性的分析
- 串行化：金融交易、需要关键一致性的场景

### 索引类型

PostgreSQL 提供多种索引类型，适用于不同的用例：

#### 1. B-Tree（默认）
- **用途**：等值、范围查询、排序
- **支持**：<、<=、=、>=、>、BETWEEN、IN、IS NULL
- **最佳用途**：大多数通用索引
- **示例**：主键、外键、时间戳

#### 2. Hash
- **用途**：仅等值比较
- **支持**：= 操作符
- **最佳用途**：具有等值查找的大型表
- **限制**：在 PG 10 之前未记录 WAL，无范围查询

#### 3. GiST（通用搜索树）
- **用途**：几何数据、全文搜索、自定义类型
- **支持**：重叠、包含、最近邻
- **最佳用途**：空间数据、范围、全文搜索
- **示例**：PostGIS 几何形状、tsvector、范围

#### 4. GIN（通用倒排索引）
- **用途**：多值列（数组、JSONB、全文）
- **支持**：contains、exists 操作符
- **最佳用途**：JSONB 查询、数组操作、全文搜索
- **权衡**：更新较慢，查询更快

#### 5. BRIN（块范围索引）
- **用途**：非常大的具有自然排序的表
- **支持**：对排序数据的范围查询
- **最佳用途**：时间序列数据、仅追加表
- **优势**：极小的索引大小，可扩展到数十亿行

#### 6. SP-GiST（空间分区 GiST）
- **用途**：非平衡数据结构
- **支持**：点、范围、IP 地址
- **最佳用途**：四叉树、k-d 树、基数树

### 查询规划和优化

PostgreSQL 的查询规划器确定执行策略：

**规划器组件：**
- **统计信息**：用于基数估计的表和列统计信息
- **成本模型**：CPU、I/O 和内存成本估计
- **计划类型**：顺序扫描、索引扫描、位图扫描、连接
- **连接方法**：嵌套循环、哈希连接、合并连接
- **优化**：查询重写、谓词下推、连接重排序

**关键统计信息：**
- `n_distinct`：不同值的数量（用于选择性）
- `correlation`：物理行顺序相关性
- `most_common_vals`：用于倾斜分布的 MCV 列表
- `histogram_bounds`：值分布直方图

**理解 EXPLAIN：**
- **成本**：启动成本 .. 总成本（任意单位）
- **行数**：估计行数
- **宽度**：平均行大小（字节）
- **实际时间**：真实执行时间（使用 ANALYZE）
- **循环**：节点执行的次数

### 分区策略

用于管理大型数据集的表分区：

#### 范围分区
- **用途**：时间序列数据、顺序值
- **示例**：按日期范围分区（每日、每月、每年）
- **优点**：易于数据生命周期管理，查询更快

#### 列表分区
- **用途**：离散分类值
- **示例**：按国家、区域、状态分区
- **优点**：逻辑数据分离，分区修剪

#### 哈希分区
- **用途**：均匀数据分布
- **示例**：按 hash(user_id) 分区
- **优点**：平衡分区大小，并行查询

**分区修剪：**
- 规划器消除不相关的分区
- 大幅减少查询范围
- 对分区性能至关重要

**分区操作：**
- 分区连接：直接连接匹配的分区
- 分区聚合：在分区内聚合
- 并行分区处理

### 复制和高可用性

PostgreSQL 复制选项：

#### 流式复制（物理）
- **类型**：到备用服务器的二进制 WAL 流
- **模式**：异步、同步、基于多数的
- **用途**：高可用性、读可扩展性
- **故障转移**：使用 Patroni、repmgr 等工具自动故障转移

**同步与异步：**
- 同步：零数据丢失，更高延迟
- 异步：低延迟，可能数据丢失
- 多数：在安全性和性能之间取得平衡

#### 逻辑复制
- **类型**：行级变更流
- **用途**：选择性复制、升级、多主
- **优点**：复制特定表、跨版本
- **限制**：无 DDL 复制，开销

#### 级联复制
- 备用服务器从其他备用服务器复制
- 减轻主服务器负载
- 地理分布

### 连接池

高效管理数据库连接：

#### pgBouncer
- **类型**：轻量级连接池器
- **模式**：会话、事务、语句池
- **用途**：高连接计数应用程序
- **优点**：减少连接开销，资源限制

**池模式：**
- **会话**：客户端连接整个会话
- **事务**：每个事务一个连接
- **语句**：每个语句一个连接（很少使用）

#### PgPool-II
- **类型**：功能丰富的中间件
- **功能**：连接池、负载均衡、查询缓存
- **用途**：读写分离、连接管理
- **优点**：高级路由、内存缓存

### VACUUM 和维护

关键维护操作：

#### VACUUM
- **目的**：回收死元组空间，更新统计信息
- **类型**：常规 VACUUM、VACUUM FULL
- **何时**：大型更新/删除后，定期通过 autovacuum
- **影响**：常规 VACUUM 是非阻塞的

#### ANALYZE
- **目的**：更新规划器统计信息
- **何时**：数据更改后、模式修改后
- **影响**：最小，大多数表快速

#### REINDEX
- **目的**：重建索引，修复膨胀
- **何时**：索引损坏、显著膨胀
- **影响**：锁定表，使用 REINDEX CONCURRENTLY（PG 12+）

#### Autovacuum
- **目的**：自动 VACUUM 和 ANALYZE
- **配置**：基于阈值的触发
- **调整**：平衡资源使用与响应能力
- **监控**：跟踪 autovacuum 运行，防止回绕

### 性能调优

关键配置参数：

#### 内存设置
```
shared_buffers: RAM 的 25%（起点）
effective_cache_size: RAM 的 50-75%
work_mem: 每次操作内存（排序、哈希）
maintenance_work_mem: VACUUM、CREATE INDEX 内存
```

#### 检查点和 WAL
```
checkpoint_timeout: 多久进行一次检查点
max_wal_size: 检查点前的 WAL 大小
checkpoint_completion_target: 分散检查点 I/O
wal_buffers: WAL 写入缓冲区大小
```

#### 查询规划器
```
random_page_cost: 随机 I/O 的相对成本
effective_io_concurrency: 并发 I/O 操作
default_statistics_target: 直方图详细程度
```

#### 连接设置
```
max_connections: 最大客户端连接数
connection_limit: 每个数据库/用户的限制
```

## 索引策略

### 选择正确的索引

**决策矩阵：**

| 查询模式 | 索引类型 | 原因 |
|----------|------------|---------|
| `WHERE id = 5` | B-tree | 等值查找 |
| `WHERE created_at > '2024-01-01'` | B-tree | 范围查询 |
| `ORDER BY name` | B-tree | 支持排序 |
| `WHERE tags @> ARRAY['sql']` | GIN | 数组包含 |
| `WHERE data->>'status' = 'active'` | GIN (jsonb_path_ops) | JSONB 查询 |
| `WHERE to_tsvector(content) @@ query` | GIN | 全文搜索 |
| `WHERE location <-> point(0,0)` | GiST | 最近邻 |
| `WHERE timestamp BETWEEN ... (大型表)` | BRIN | 顺序时间序列 |
| `WHERE ip_address << '192.168.0.0/16'` | GiST 或 SP-GiST | IP 范围查询 |

### 复合索引

用于复杂查询的多列索引：

**列排序规则：**
1. 等值列优先
2. 排序/范围列最后
3. 高选择性列优先
4. 精确匹配查询模式

**示例：**
```sql
-- 查询：WHERE status = 'active' AND created_at > '2024-01-01' ORDER BY created_at
-- 最佳索引：(status, created_at)
CREATE INDEX idx_users_status_created ON users(status, created_at);
```

### 部分索引

索引行子集：

**优点：**
- 更小的索引大小
- 非索引行更新更快
- 针对性查询优化

**用例：**
- 仅索引活动记录：`WHERE deleted_at IS NULL`
- 索引最近数据：`WHERE created_at > NOW() - INTERVAL '90 days'`
- 索引特定状态：`WHERE status IN ('pending', 'processing')`

### 表达式索引

索引计算值：

**示例：**
```sql
-- 不区分大小写的搜索
CREATE INDEX idx_users_email_lower ON users(LOWER(email));

-- 日期截断
CREATE INDEX idx_events_date ON events(DATE(created_at));

-- JSONB 字段
CREATE INDEX idx_data_status ON documents((data->>'status'));
```

### 覆盖索引（INCLUDE）

包含非键列以进行索引仅扫描：

```sql
CREATE INDEX idx_users_email_include
ON users(email)
INCLUDE (first_name, last_name, created_at);
```

**优点：** 查询完全从索引中满足，无需表查找

### 索引维护

**监控索引使用情况：**
```sql
-- 未使用的索引
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY pg_relation_size(indexrelid) DESC;
```

**检测膨胀：**
```sql
-- 索引膨胀估计
SELECT schemaname, tablename, indexname,
       pg_size_pretty(pg_relation_size(indexrelid)) as index_size,
       idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY pg_relation_size(indexrelid) DESC;
```

## 查询优化

### 使用 EXPLAIN ANALYZE

理解查询执行：

```sql
-- 基本 EXPLAIN
EXPLAIN SELECT * FROM users WHERE email = 'user@example.com';

-- EXPLAIN ANALYZE（实际运行查询）
EXPLAIN ANALYZE SELECT * FROM users WHERE created_at > '2024-01-01';

-- 详细输出
EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
SELECT u.*, o.total
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE u.created_at > '2024-01-01';
```

**关键指标：**
- **规划时间**：生成计划的时间
- **执行时间**：实际查询运行时间
- **共享命中率 vs 读取**：缓冲区缓存命中率 vs 磁盘读取
- **行数**：估计值 vs 实际行数
- **过滤 vs 索引条件**：扫描后过滤 vs 索引使用

### 常见查询反模式

#### 1. N+1 查询
**问题**：循环中每个行一个查询
**解决方案**：连接或批量查询

#### 2. SELECT *
**问题**：获取不必要的列
**解决方案**：选择需要的列

#### 3. 隐式类型转换
**问题**：由于类型不匹配而未使用索引
**解决方案**：确保查询类型与列类型匹配

#### 4. 索引列上的函数
**问题**：`WHERE UPPER(email) = 'USER@EXAMPLE.COM'`
**解决方案**：使用表达式索引或正确比较

#### 5. OR 条件
**问题**：`WHERE status = 'A' OR status = 'B'`
**解决方案**：使用 `IN`：`WHERE status IN ('A', 'B')`

### 连接优化

**连接类型：**

1. **嵌套循环**
   - 最佳用途：小外表，索引内表
   - 如何：对外表每行扫描内表
   - 何时：小结果集，良好索引

2. **哈希连接**
   - 最佳用途：大型表，无良好索引
   - 如何：构建较小表的哈希表
   - 何时：等值连接，足够内存

3. **合并连接**
   - 最佳用途：预排序数据，等值连接
   - 如何：排序两个输入，合并扫描
   - 何时：两个输入排序或可以廉价排序

**连接顺序很重要：**
- 规划器重新排序连接以进行优化
- 统计信息指导连接顺序决策
- 可以强制顺序使用 `SET join_collapse_limit`

### 聚合优化

**技术：**
- **部分聚合**：分区聚合
- **哈希聚合**：内存分组
- **排序聚合**：预排序输入
- **并行聚合**：多个工作进程

**物化视图：**
- 预计算昂贵的聚合
- 按计划或触发刷新
- 权衡新鲜度与查询速度

### 查询缓存

**级别：**
1. **共享缓冲区**：PostgreSQL 页面缓存
2. **操作系统页面缓存**：操作系统缓存
3. **应用程序缓存**：Redis、Memcached
4. **预准备语句**：重用查询计划

## 分区

### 实现范围分区

**时间序列示例：**

```sql
-- 创建分区表
CREATE TABLE events (
    id BIGSERIAL,
    event_type TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    data JSONB,
    created_at TIMESTAMP NOT NULL
) PARTITION BY RANGE (created_at);

-- 创建分区
CREATE TABLE events_2024_01 PARTITION OF events
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE events_2024_02 PARTITION OF events
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

-- 默认分区用于范围外数据
CREATE TABLE events_default PARTITION OF events DEFAULT;

-- 分区上的索引
CREATE INDEX idx_events_2024_01_user ON events_2024_01(user_id);
CREATE INDEX idx_events_2024_02_user ON events_2024_02(user_id);
```

### 分区自动化

**自动分区管理：**

```sql
-- 创建月度分区函数
CREATE OR REPLACE FUNCTION create_monthly_partition(
    base_table TEXT,
    partition_date DATE
) RETURNS VOID AS $$
DECLARE
    partition_name TEXT;
    start_date DATE;
    end_date DATE;
BEGIN
    partition_name := base_table || '_' || TO_CHAR(partition_date, 'YYYY_MM');
    start_date := DATE_TRUNC('month', partition_date);
    end_date := start_date + INTERVAL '1 month';

    EXECUTE format(
        'CREATE TABLE IF NOT EXISTS %I PARTITION OF %I
         FOR VALUES FROM (%L) TO (%L)',
        partition_name, base_table, start_date, end_date
    );

    -- 创建索引
    EXECUTE format(
        'CREATE INDEX IF NOT EXISTS %I ON %I(user_id)',
        'idx_' || partition_name || '_user', partition_name
    );
END;
$$ LANGUAGE plpgsql;
```

### 分区维护

**删除旧分区：**

```sql
-- 分离分区（快速，非阻塞）
ALTER TABLE events DETACH PARTITION events_2023_01;

-- 删除分离的分区
DROP TABLE events_2023_01;

-- 或者分离前归档
CREATE TABLE archive.events_2023_01 AS SELECT * FROM events_2023_01;
DROP TABLE events_2023_01;
```

## 高可用性和复制

### 设置流复制

**主服务器配置 (postgresql.conf):**

```conf
# 复制设置
wal_level = replica
max_wal_senders = 10
max_replication_slots = 10
hot_standby = on
synchronous_commit = on  # 或 off 用于异步
synchronous_standby_names = 'standby1,standby2'  # 用于同步复制
```

**创建复制用户：**

```sql
CREATE USER replicator WITH REPLICATION ENCRYPTED PASSWORD 'secure_password';
```

**主服务器上的 pg_hba.conf：**

```conf
# 允许复制连接
host replication replicator standby_ip/32 md5
```

**从服务器设置：**

```bash
# 停止从服务器 PostgreSQL
systemctl stop postgresql

# 删除旧数据目录
rm -rf /var/lib/postgresql/14/main

# 从主服务器进行基础备份
pg_basebackup -h primary_host -D /var/lib/postgresql/14/main \
              -U replicator -P -v -R -X stream -C -S standby1

# 启动从服务器
systemctl start postgresql
```

**从服务器配置（由 -R 标志创建）：**

```conf
# standby.signal 文件自动创建
# postgresql.auto.conf 包含：
primary_conninfo = 'host=primary_host port=5432 user=replicator password=secure_password'
primary_slot_name = 'standby1'
```

### 监控复制

**在主服务器上：**

```sql
-- 检查复制状态
SELECT client_addr, state, sync_state, replay_lag
FROM pg_stat_replication;

-- 检查复制槽
SELECT slot_name, active, restart_lsn, confirmed_flush_lsn
FROM pg_replication_slots;
```

**在从服务器上：**

```sql
-- 检查复制延迟
SELECT now() - pg_last_xact_replay_timestamp() AS replication_lag;

-- 检查恢复状态
SELECT pg_is_in_recovery();
```

### 故障转移和切换

**将从服务器提升为主服务器：**

```bash
# 触发故障转移
pg_ctl promote -D /var/lib/postgresql/14/main

# 或者使用 SQL
SELECT pg_promote();
```

**受控切换：**

```bash
# 1. 在主服务器上停止写入
# 2. 等待从服务器同步
# 3. 提升从服务器
# 4. 将旧主服务器重新配置为新的从服务器
```

### 逻辑复制设置

**在发布者（源）：**

```sql
-- 创建发布
CREATE PUBLICATION my_publication FOR TABLE users, orders;

-- 或者所有表
CREATE PUBLICATION all_tables FOR ALL TABLES;
```

**在订阅者（目标）：**

```sql
-- 创建订阅
CREATE SUBSCRIPTION my_subscription
    CONNECTION 'host=publisher_host dbname=mydb user=replicator password=pass'
    PUBLICATION my_publication;

-- 监控订阅
SELECT * FROM pg_stat_subscription;
```

## 备份和恢复

### 物理备份

**pg_basebackup：**

```bash
# 完全物理备份
pg_basebackup -h localhost -U postgres -D /backup/base \
              -F tar -z -P -v

# 带有 WAL 文件用于时间点恢复
pg_basebackup -h localhost -U postgres -D /backup/base \
              -X stream -F tar -z -P
```

**连续归档（WAL 归档）：**

```conf
# postgresql.conf
wal_level = replica
archive_mode = on
archive_command = 'cp %p /archive/wal/%f'
```

### 逻辑备份

**pg_dump：**

```bash
# 单个数据库
pg_dump -h localhost -U postgres -F c -b -v -f mydb.dump mydb

# 所有数据库
pg_dumpall -h localhost -U postgres -f all_databases.sql

# 特定表
pg_dump -h localhost -U postgres -t users -t orders -F c -f tables.dump mydb

# 仅架构
pg_dump -h localhost -U postgres --schema-only -F c -f schema.dump mydb
```

**pg_restore：**

```bash
# 恢复数据库
pg_restore -h localhost -U postgres -d mydb -v mydb.dump

# 并行恢复
pg_restore -h localhost -U postgres -d mydb -j 4 -v mydb.dump

# 恢复特定表
pg_restore -h localhost -U postgres -d mydb -t users -v mydb.dump
```

### 时间点恢复 (PITR)

**设置：**

1. 进行基础备份
2. 配置 WAL 归档
3. 安全存储 WAL 文件

**恢复：**

```bash
# 1. 恢复基础备份
tar -xzf base.tar.gz -C /var/lib/postgresql/14/main

# 2. 创建 recovery.signal 文件
touch /var/lib/postgresql/14/main/recovery.signal

# 3. 配置恢复目标（postgresql.conf 或 postgresql.auto.conf）
restore_command = 'cp /archive/wal/%f %p'
recovery_target_time = '2024-01-15 14:30:00'
# 或: recovery_target_name = 'before_disaster'
# 或: recovery_target_lsn = '0/3000000'

# 4. 启动 PostgreSQL
systemctl start postgresql
```

### 备份策略

**3-2-1 规则：**
- 3份数据副本
- 2种不同介质类型
- 1份异地备份

**备份计划：**
- **每日**：增量 WAL 归档
- **每周**：完整 pg_basebackup
- **每月**：长期保留

**测试备份：**
- 定期在测试环境恢复
- 验证数据完整性
- 测量恢复时间

## 性能监控

### 关键指标监控

**数据库健康：**
- 活连接数
- 事务速率
- 缓存命中率
- 死锁
- 检查点频率
- 自动清理运行

**查询性能：**
- 慢查询日志
- 查询执行时间
- 锁等待
- 顺序扫描

**系统资源：**
- CPU 利用率
- 内存使用
- 磁盘 I/O
- 网络带宽

### 必要监控查询

**连接统计：**

```sql
SELECT count(*) as total_connections,
       count(*) FILTER (WHERE state = 'active') as active,
       count(*) FILTER (WHERE state = 'idle') as idle,
       count(*) FILTER (WHERE state = 'idle in transaction') as idle_in_transaction
FROM pg_stat_activity;
```

**缓存命中率：**

```sql
SELECT sum(heap_blks_read) as heap_read,
       sum(heap_blks_hit) as heap_hit,
       sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) AS ratio
FROM pg_statio_user_tables;
```

**表膨胀：**

```sql
SELECT schemaname, tablename,
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
       n_dead_tup,
       n_live_tup,
       round(n_dead_tup * 100.0 / NULLIF(n_live_tup + n_dead_tup, 0), 2) AS dead_ratio
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY n_dead_tup DESC;
```

**长时间运行的查询：**

```sql
SELECT pid, now() - query_start AS duration, state, query
FROM pg_stat_activity
WHERE state != 'idle'
  AND query NOT LIKE '%pg_stat_activity%'
ORDER BY duration DESC;
```

**锁监控：**

```sql
SELECT blocked_locks.pid AS blocked_pid,
       blocked_activity.usename AS blocked_user,
       blocking_locks.pid AS blocking_pid,
       blocking_activity.usename AS blocking_user,
       blocked_activity.query AS blocked_statement,
       blocking_activity.query AS blocking_statement
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks ON blocking_locks.locktype = blocked_locks.locktype
JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted
  AND blocking_locks.granted;
```

### pg_stat_statements

**安装：**

```sql
CREATE EXTENSION pg_stat_statements;
```

**配置 (postgresql.conf)：**

```conf
shared_preload_libraries = 'pg_stat_statements'
pg_stat_statements.track = all
pg_stat_statements.max = 10000
```

**按总时间排序的查询：**

```sql
SELECT query,
       calls,
       total_exec_time,
       mean_exec_time,
       max_exec_time,
       rows
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 20;
```

**按平均时间排序的查询：**

```sql
SELECT query,
       calls,
       mean_exec_time,
       total_exec_time
FROM pg_stat_statements
WHERE calls > 100
ORDER BY mean_exec_time DESC
LIMIT 20;
```

## 最佳实践

### 架构设计

**规范化：**
- 事务性系统规范化到 3NF
- 阅读密集型负载有选择地反规范化
- 使用外键保证数据完整性
- 非常大的表考虑分区

**数据类型：**
- 使用最小的合适数据类型
- 大 ID 使用 BIGINT，小范围使用 INTEGER
- 精确小数使用 NUMERIC
- 时间戳使用 TIMESTAMP WITH TIME ZONE
- 除非需要长度限制，否则使用 TEXT 而不是 VARCHAR
- 分布式 ID 生成使用 UUID
- 半结构化数据使用 JSONB

**约束：**
- 所有表都有主键
- 使用外键保证引用完整性
- 使用 CHECK 约束实现业务规则
- 适当使用 NOT NULL
- 使用唯一约束保证唯一性
- 使用约束名称提高可维护性

### 迁移策略

**零停机迁移：**

1. **添加新列**
   ```sql
   ALTER TABLE users ADD COLUMN email_verified BOOLEAN;
   ```

2. **批量回填数据**
   ```sql
   UPDATE users SET email_verified = false
   WHERE email_verified IS NULL
   LIMIT 10000;
   ```

3. **添加 NOT NULL 约束**
   ```sql
   ALTER TABLE users ALTER COLUMN email_verified SET NOT NULL;
   ```

**索引创建：**
- 在生产环境中使用 `CREATE INDEX CONCURRENTLY`
- 不锁定表，允许读写
- 创建时间长但不会阻塞
- 使用 `pg_stat_progress_create_index` 监控进度

**大表修改：**
- 使用 `pg_repack` 进行表重写
- 修改前分区大表
- 安排在维护窗口期间
- 在类似生产的测试数据集上测试

### 安全最佳实践

**身份验证：**
- 使用强密码或证书认证
- 使用 SCRAM-SHA-256 进行密码加密
- 为不同应用使用分离用户
- 避免使用超级用户进行应用连接

**授权：**
- 授予最小必要权限
- 使用基于角色的访问控制
- 删除 PUBLIC 访问
- 多租户使用行级安全

**网络安全：**
- 限制性配置 pg_hba.conf
- 使用 SSL/TLS 连接
- 防火墙数据库端口
- 使用 VPN 或私有网络进行复制

**审计日志：**
- 启用连接日志
- 记录 DDL 语句
- 使用 pgAudit 扩展进行详细审计
- 监控可疑活动

### 维护计划

**每日：**
- 监控慢查询
- 检查复制延迟
- 检查自动清理活动
- 监控磁盘空间

**每周：**
- 分析顶级查询
- 检查索引使用情况
- 检查膨胀
- 备份验证

**每月：**
- 对关键表进行完整 VACUUM
- 膨胀索引 REINDEX
- 审查配置参数
- 容量规划

**每季度：**
- 审查和优化索引
- 架构优化机会
- 升级规划
- 性能基线更新

## 高级主题

### 并行查询执行

**配置：**

```conf
max_parallel_workers_per_gather = 4
max_parallel_workers = 8
parallel_setup_cost = 1000
parallel_tuple_cost = 0.1
min_parallel_table_scan_size = 8MB
```

**强制并行执行：**

```sql
SET max_parallel_workers_per_gather = 4;
EXPLAIN ANALYZE SELECT COUNT(*) FROM large_table;
```

**并行查询何时有帮助：**
- 大型顺序扫描
- 大型聚合
- 大表上的哈希连接
- 位图堆扫描

### 自定义函数和存储过程

**存储过程：**

```sql
CREATE OR REPLACE PROCEDURE update_user_statistics()
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE users SET
        order_count = (SELECT COUNT(*) FROM orders WHERE user_id = users.id),
        last_order_date = (SELECT MAX(created_at) FROM orders WHERE user_id = users.id);

    COMMIT;
END;
$$;
```

**带错误处理的函数：**

```sql
CREATE OR REPLACE FUNCTION create_user(
    p_email TEXT,
    p_name TEXT
) RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_user_id INTEGER;
BEGIN
    INSERT INTO users (email, name)
    VALUES (p_email, p_name)
    RETURNING id INTO v_user_id;

    RETURN v_user_id;
EXCEPTION
    WHEN unique_violation THEN
        RAISE EXCEPTION 'Email already exists: %', p_email;
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error creating user: %', SQLERRM;
END;
$$;
```

### 外部数据封装器

**访问外部数据源：**

```sql
-- 安装 postgres_fdw
CREATE EXTENSION postgres_fdw;

-- 创建服务器
CREATE SERVER remote_db
FOREIGN DATA WRAPPER postgres_fdw
OPTIONS (host 'remote_host', dbname 'remote_database', port '5432');

-- 创建用户映射
CREATE USER MAPPING FOR current_user
SERVER remote_db
OPTIONS (user 'remote_user', password 'remote_password');

-- 导入外部架构
IMPORT FOREIGN SCHEMA public
FROM SERVER remote_db
INTO local_schema;

-- 查询外部表
SELECT * FROM local_schema.remote_table;
```

### JSON 和 JSONB 操作

**JSONB 索引：**

```sql
-- GIN 索引用于包含查询
CREATE INDEX idx_data_gin ON documents USING GIN (data);

-- 表达式索引用于特定字段
CREATE INDEX idx_data_status ON documents ((data->>'status'));

-- 使用 jsonb_path_ops 的 GIN 索引（更小，对 @> 查询更快）
CREATE INDEX idx_data_path_ops ON documents USING GIN (data jsonb_path_ops);
```

**高效的 JSONB 查询：**

```sql
-- 包含查询（使用 GIN 索引）
SELECT * FROM documents WHERE data @> '{"status": "active"}';

-- 存在性查询
SELECT * FROM documents WHERE data ? 'email';

-- 路径查询
SELECT * FROM documents WHERE data->'user'->>'email' = 'user@example.com';

-- 数组操作
SELECT * FROM documents WHERE data->'tags' @> '["sql", "postgres"]';
```

### 全文搜索

**基本设置：**

```sql
-- 添加 tsvector 列
ALTER TABLE articles ADD COLUMN search_vector tsvector;

-- 生成搜索向量
UPDATE articles SET search_vector =
    to_tsvector('english', coalesce(title, '') || ' ' || coalesce(content, ''));

-- 创建 GIN 索引
CREATE INDEX idx_articles_search ON articles USING GIN (search_vector);

-- 触发器自动更新
CREATE TRIGGER articles_search_update
BEFORE INSERT OR UPDATE ON articles
FOR EACH ROW EXECUTE FUNCTION
tsvector_update_trigger(search_vector, 'pg_catalog.english', title, content);
```

**搜索查询：**

```sql
-- 基本搜索
SELECT title, ts_rank(search_vector, query) AS rank
FROM articles, to_tsquery('english', 'postgresql & database') query
WHERE search_vector @@ query
ORDER BY rank DESC;

-- 短语搜索
SELECT title FROM articles
WHERE search_vector @@ phraseto_tsquery('english', 'database engineering');

-- 带高亮显示的搜索
SELECT title,
       ts_headline('english', content, query) AS snippet
FROM articles, to_tsquery('english', 'postgresql') query
WHERE search_vector @@ query;
```

## 故障排除

### 常见问题

**问题：慢查询**
- 检查 EXPLAIN ANALYZE 输出
- 确认索引存在且被使用
- 更新表统计信息：`ANALYZE table_name`
- 检查外键缺失索引
- 查看索引列上的函数调用

**问题：高 CPU 使用率**
- 使用 pg_stat_statements 识别昂贵查询
- 检查导致顺序扫描的缺失索引
- 审查并行查询设置
- 检查低效的连接或聚合

**问题：连接耗尽**
- 增加 max_connections（需要重启）
- 实现连接池（pgBouncer）
- 查找应用程序中的连接泄漏
- 使用 `pg_stat_activity` 监控

**问题：自动清理（Autovacuum）未能及时清理**
- 增加autovacuum_max_workers参数
- 调整autovacuum阈值
- 减少autovacuum_naptime参数
- 增加autovacuum_work_mem参数
- 检查是否存在长时间运行的交易阻塞VACUUM操作

**问题：复制延迟**
- 检查主服务器与从服务器之间的网络带宽
- 验证从服务器的硬件资源
- 检查从服务器上的长时间运行查询
- 监控WAL日志生成速率
- 考虑增加wal_sender_timeout参数

**问题：事务ID回绕**
- 监控最老的事务的年龄
- 对旧表运行VACUUM FREEZE操作
- 检查autovacuum_freeze_max_age参数
- 增加autovacuum清理的激进程度
- 如有必要，手动运行VACUUM FREEZE操作

### 诊断查询

**查找外键缺失的索引：**

```sql
SELECT c.conrelid::regclass AS 表,
       c.confrelid::regclass AS 被引用表,
       string_agg(a.attname, ', ') AS 外键列
FROM pg_constraint c
JOIN pg_attribute a ON a.attnum = ANY(c.conkey) AND a.attrelid = c.conrelid
WHERE c.contype = 'f'
  AND NOT EXISTS (
    SELECT 1 FROM pg_index i
    WHERE i.indrelid = c.conrelid
      AND c.conkey[1:array_length(c.conkey, 1)]
          OPERATOR(pg_catalog.@>) i.indkey[0:array_length(c.conkey, 1) - 1]
  )
GROUP BY c.conrelid, c.confrelid, c.conname;
```

**识别阻塞查询：**

```sql
SELECT activity.pid,
       activity.usename,
       activity.query,
       blocking.pid AS 阻塞ID,
       blocking.query AS 阻塞查询
FROM pg_stat_activity AS activity
JOIN pg_stat_activity AS blocking ON blocking.pid = ANY(pg_blocking_pids(activity.pid));
```

---

**技能版本**: 1.0.0
**最后更新**: 2025年10月
**技能类别**: 数据库工程、性能优化、数据架构
**兼容版本**: PostgreSQL 12+、13、14、15、16
**前提条件**: SQL知识、基础数据库概念、Linux命令行
