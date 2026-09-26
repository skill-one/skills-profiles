您正在使用 DuckDB 帮助用户查询数据。

输入：`$@`

请按顺序执行以下步骤。

## 第 1 步 — 解析状态并确定模式

在以下位置查找现有的状态文件：

```bash
STATE_DIR=""
test -f .duckdb-skills/state.sql && STATE_DIR=".duckdb-skills"
PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo "$PWD")"
PROJECT_ID="$(echo "$PROJECT_ROOT" | tr '/' '-')"
test -f "$HOME/.duckdb-skills/$PROJECT_ID/state.sql" && STATE_DIR="$HOME/.duckdb-skills/$PROJECT_ID"
```

如果找到，请验证它引用的数据库是否仍然可访问：

```bash
duckdb -init "$STATE_DIR/state.sql" -c "SHOW DATABASES;"
```

现在确定模式：

- **Ad-hoc 模式**：如果存在 `--file` 标志，或者 SQL 引用文件路径/字面量（例如 `FROM 'data.csv'`），或者 `STATE_DIR` 为空。
- **Session 模式**：如果 `STATE_DIR` 已设置且输入引用表名，是自然语言，或者 SQL 没有文件引用。

如果没有状态文件且没有引用文件，则回退到针对 `:memory:` 的 ad-hoc 模式 — 用户必须在他们的 SQL 中直接引用文件。

如果状态文件存在，但其中任何 `ATTACH` 失败，请警告用户并回退到 ad-hoc 模式。

## 第 2 步 — 检查 DuckDB 是否已安装

```bash
command -v duckdb
```

如果没有找到，请委托给 `/duckdb-skills:install-duckdb` 然后继续。

## 第 3 步 — 如有必要生成 SQL

如果输入是自然语言（不是有效的 SQL），请使用以下友好的 SQL 参考生成 SQL。

在 **Session 模式**中，首先检索模式以指导查询生成：

```bash
duckdb -init "$STATE_DIR/state.sql" -csv -c "
SELECT table_name FROM duckdb_tables() ORDER BY table_name;
"
```

然后对于相关表：

```bash
duckdb -init "$STATE_DIR/state.sql" -csv -c "DESCRIBE <table_name>;"
```

使用模式上下文和友好的 SQL 参考生成最合适的查询。

## 第 4 步 — 估计结果大小

在执行之前，估计查询是否可能产生非常大的结果，这会在返回到此对话时消耗过多的 token。

**Session 模式** — 检查所涉及表的行数：

```bash
duckdb -init "$STATE_DIR/state.sql" -csv -c "
SELECT table_name, estimated_size, column_count
FROM duckdb_tables()
WHERE table_name IN ('<table1>', '<table2>');
"
```

**Ad-hoc 模式** — 探测源：

```bash
duckdb :memory: -csv -c "
SET allowed_paths=['FILE_PATH'];
SET enable_external_access=false;
SET allow_persistent_secrets=false;
SET lock_configuration=true;
SELECT count() AS row_count FROM 'FILE_PATH';
"
```

**评估**：
- 如果查询已经有 `LIMIT`、`count()` 或其他聚合来限制输出 -> 安全，继续。
- 如果源有 **>1M 行**且查询没有 `LIMIT` 或聚合 -> 告诉用户：
  *"此查询将返回一个非常大的结果集。在此处显示它将消耗大量 token 并增加成本。我建议添加 `LIMIT 1000` 或聚合以保持输出可控。"*
  在运行之前请求确认。
- 如果数据大小是 **>10 GB** -> 额外警告：
  *"此表超过 10 GB — 查询可能需要较长时间才能完成。"*
  如果用户确认，则继续。

对于本质上受限制的查询（例如 `DESCRIBE`、`SUMMARIZE`、聚合、`count()`），跳过此步骤。

## 第 5 步 — 执行查询

**Ad-hoc 模式**（沙盒 — 仅可访问引用的文件）：

```bash
duckdb :memory: -csv <<'SQL'
SET allowed_paths=['FILE_PATH'];
SET enable_external_access=false;
SET allow_persistent_secrets=false;
SET lock_configuration=true;
<QUERY>;
SQL
```

将 `FILE_PATH` 替换为从查询或 `--file` 参数中提取的实际文件路径。
如果引用多个文件，请在 `allowed_paths` 列表中包含所有路径。

**Session 模式**（用户信任的数据库）：

```bash
duckdb -init "$STATE_DIR/state.sql" -csv -c "<QUERY>"
```

对于多行查询，使用 `-init` 和 heredoc：

```bash
duckdb -init "$STATE_DIR/state.sql" -csv <<'SQL'
<QUERY>;
SQL
```

始终使用 heredoc (`<<'SQL'`) 来避免 shell 引用问题。

## 第 6 步 — 处理错误

- **语法错误**：显示错误，建议修正后的查询，并重新运行。
- **缺少扩展**（例如 `Extension "X" not loaded`）：委托给 `/duckdb-skills:install-duckdb <ext>`，然后重试。
- **表未找到**（Session 模式）：使用 `FROM duckdb_tables()` 列出可用表并建议修正。
- **文件未找到**（Ad-hoc 模式）：使用 `find "$PWD" -name "<filename>" 2>/dev/null` 定位文件并建议修正的路径。
- **持久或模糊的 DuckDB 错误**：使用 `/duckdb-skills:duckdb-docs <error message or relevant keywords>` 在文档中搜索指导，然后应用修正并重试。

## 第 7 步 — 展示结果

向用户显示查询输出。如果结果超过 100 行，请注明截断并建议在查询中添加 `LIMIT`。

对于自然语言问题，还提供对结果的简要解释。

---

## DuckDB 友好的 SQL 参考

在生成 SQL 时，优先使用这些 DuckDB 习惯用法：

### 紧凑子句
- **FROM-first**：`FROM table WHERE x > 10`（隐式 `SELECT *`）
- **GROUP BY ALL**：自动按所有非聚合列分组
- **ORDER BY ALL**：按所有列排序以获得确定性结果
- **SELECT * EXCLUDE (col1, col2)**：从通配符中删除列
- **SELECT * REPLACE (expr AS col)**：原地转换列
- **UNION ALL BY NAME**：按不同列顺序组合表
- **百分比 LIMIT**：`LIMIT 10%` 返回一定百分比的行
- **前缀别名**：`SELECT x: 42` 而不是 `SELECT 42 AS x`
- **SELECT 列表尾部的逗号**：允许在 SELECT 列表中使用

### 查询功能
- **count()**：无需 `count(*)`
- **可重用别名**：在 WHERE / GROUP BY / HAVING 中使用列别名
- **横向列别名**：`SELECT i+1 AS j, j+2 AS k`
- **COLUMNS(*)**：跨列应用表达式；支持正则、EXCLUDE、REPLACE、lambda
- **FILTER 子句**：`count() FILTER (WHERE x > 10)` 用于条件聚合
- **GROUPING SETS / CUBE / ROLLUP**：高级多级聚合
- **Top-N per group**：`max(col, 3)` 返回前 3 个作为列表；也支持 `arg_max(arg, val, n)`、`min_by(arg, val, n)`
- **DESCRIBE table_name**：模式摘要（列名和类型）
- **SUMMARIZE table_name**：即时统计概览
- **PIVOT / UNPIVOT**：在宽和长格式之间重塑
- **SET VARIABLE x = expr**：定义 SQL 级别的变量，使用 `getvariable('x')` 引用

### 数据导入
- **直接文件查询**：`FROM 'file.csv'`、`FROM 'data.parquet'`
- **通配符**：`FROM 'data/part-*.parquet'` 读取多个文件
- **自动检测**：CSV 标头和模式自动推断

### 表达式和类型
- **点操作符链**：`'hello'.upper()` 或 `col.trim().lower()`
- **列表推导式**：`[x*2 FOR x IN list_col]`
- **列表/字符串切片**：`col[1:3]`、负索引 `col[-1]`
- **STRUCT.* 语法**：`SELECT s.* FROM (SELECT {'a': 1, 'b': 2} AS s)`
- **方括号列表**：`[1, 2, 3]`
- **format()**：`format('{}->{}', a, b)` 用于字符串格式化

### 连接
- **ASOF 连接**：对有序数据（例如时间戳）进行近似匹配
- **POSITIONAL 连接**：按位置匹配行，而不是键
- **LATERAL 连接**：在子查询中引用先前的表表达式

### 数据修改
- **CREATE OR REPLACE TABLE**：无需先 `DROP TABLE IF EXISTS`
- **CREATE TABLE ... AS SELECT (CTAS)**：从查询结果创建表
- **INSERT INTO ... BY NAME**：按名称匹配列，而不是位置
- **INSERT OR IGNORE INTO / INSERT OR REPLACE INTO**：upsert 模式
