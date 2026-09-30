---
name: analyzing-data
description: 使用 SQL 查询数据仓库，并回答有关数据的业务问题。在需要使用仓库数据时使用，例如计数、指标、趋势、聚合、跨表连接、数据查找或临时 SQL 分析（例如“谁使用 X”、“有多少 Y”、“显示 Z”、“查找客户”、“计数是多少”）。
---

# 数据分析

通过查询数据仓库来回答业务问题。内核在第一次 `exec` 调用时自动启动。

**以下所有 CLI 命令都相对于此技能的目录。** 在运行任何 `scripts/cli.py` 命令之前，请使用 `cd` 命令切换到包含此文件的目录。

## 工作流程

1. **模式查找** — 检查缓存的查询策略：
   ```bash
   uv run scripts/cli.py pattern lookup "<用户的提问>"
   ```
   如果存在模式，则遵循其策略。执行后记录结果：
   ```bash
   uv run scripts/cli.py pattern record <名称> --success  # 或 --failure
   ```

2. **概念查找** — 查找已知的表映射：
   ```bash
   uv run scripts/cli.py concept lookup <概念>
   ```

3. **表发现** — 如果缓存未命中，则搜索代码库（`Grep pattern="<概念>" glob="**/*.sql"`）或查询 `INFORMATION_SCHEMA`。参见 [reference/discovery-warehouse.md](reference/discovery-warehouse.md)。

4. **执行查询**：
   ```bash
   uv run scripts/cli.py exec "df = run_sql('SELECT ...')"
   uv run scripts/cli.py exec "print(df)"
   ```

5. **缓存学习结果** — 在展示结果前始终缓存：
   ```bash
   # 缓存概念 → 表映射
   uv run scripts/cli.py concept learn <概念> <TABLE> -k <KEY_COL>
   # 缓存查询策略（如果需要发现）
   uv run scripts/cli.py pattern learn <名称> -q "问题" -s "步骤" -t "TABLE" -g "陷阱"
   ```

6. **向用户展示发现结果**。

## 内核函数

| 函数               | 返回值         |
|-------------------|---------------|
| `run_sql(query, limit=100)` | Polars DataFrame |
| `run_sql_pandas(query, limit=100)` | Pandas DataFrame |
| `run_sql_many(queries, limit=100)` | Polars DataFrames 列表（每个查询一个） |

`pl`（Polars）和 `pd`（Pandas）已预导入。

**使用 `run_sql_many` 组合独立查询** — 它们并发执行（Snowflake 异步 / 连接池分叉），而不是一次执行一个：

```bash
uv run scripts/cli.py exec "dfs = run_sql_many(['SELECT ...', 'SELECT ...']); print(dfs[0])"
```

`run_sql_many` 是 **快速失败**：如果任何查询出错，调用会抛出异常，并且成功执行的查询结果会被丢弃。如果需要部分结果，请使用单独的 `run_sql` 调用。

**超时**：`exec` 默认等待 120 秒，然后中断查询并返回“客户端停止等待”消息（查询可能在服务器端仍会完成）。对于已知的长时间运行查询，可以增加超时：`uv run scripts/cli.py exec "..." -t 600`。

**空闲内核**：内核在 2 小时空闲后自动终止（在此之前保留状态）。使用 `ASTRO_KERNEL_IDLE_TIMEOUT`（秒；`0` 禁用）覆盖。

## CLI 参考

### 内核

```bash
uv run scripts/cli.py warehouse list      # 列出数据仓库
uv run scripts/cli.py start [-w name]     # 启动内核（可选指定数据仓库）
uv run scripts/cli.py exec "..."          # 执行 Python 代码
uv run scripts/cli.py status              # 内核状态
uv run scripts/cli.py restart             # 重启内核
uv run scripts/cli.py stop                # 停止内核
uv run scripts/cli.py install <pkg>       # 安装包
```

### 概念缓存

```bash
uv run scripts/cli.py concept lookup <name>                     # 查找
uv run scripts/cli.py concept learn <name> <TABLE> -k <KEY_COL> # 学习
uv run scripts/cli.py concept list                               # 列出所有
uv run scripts/cli.py concept import -p /path/to/warehouse.md   # 批量导入
```

### 模式缓存

```bash
uv run scripts/cli.py pattern lookup "question"                                      # 查找
uv run scripts/cli.py pattern learn <name> -q "..." -s "..." -t "TABLE" -g "gotcha"  # 学习
uv run scripts/cli.py pattern record <name> --success                                # 记录结果
uv run scripts/cli.py pattern list                                                   # 列出所有
uv run scripts/cli.py pattern delete <name>                                          # 删除
```

### 表模式缓存

```bash
uv run scripts/cli.py table lookup <TABLE>            # 查找模式
uv run scripts/cli.py table cache <TABLE> -c '[...]'  # 缓存模式
uv run scripts/cli.py table list                       # 列出缓存
uv run scripts/cli.py table delete <TABLE>             # 删除
```

### 缓存管理

```bash
uv run scripts/cli.py cache status                # 统计信息
uv run scripts/cli.py cache clear [--stale-only]  # 清除
```

## 参考文献

- [reference/discovery-warehouse.md](reference/discovery-warehouse.md) — 大表处理、数据仓库探索、`INFORMATION_SCHEMA` 查询
- [reference/common-patterns.md](reference/common-patterns.md) — 趋势、比较、Top-N、分布、队列的 SQL 模板
