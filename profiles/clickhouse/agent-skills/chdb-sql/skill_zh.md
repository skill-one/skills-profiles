# chdb SQL — 在您的 Python 进程中运行 ClickHouse

直接在 Python 中运行 ClickHouse SQL——无需服务器。使用完整的 ClickHouse SQL 功能查询本地文件、远程数据库和云存储。

```bash
pip install chdb
```

## 决策树：选择合适的 API

```
1. 对文件或数据库进行一次性查询 → chdb.query()
2. 使用表格进行多步分析 → Session
3. DB-API 2.0 连接 → chdb.connect()
4. Pandas 风格的 DataFrame 操作 → 使用 chdb-datastore 技能
```

## chdb.query() — 一行代码，任何数据

```python
import chdb

chdb.query("SELECT * FROM file('data.parquet', Parquet) WHERE price > 100 LIMIT 10")       # 本地文件
chdb.query("SELECT * FROM mysql('db:3306', 'shop', 'orders', 'root', 'pass')")              # 数据库
chdb.query("SELECT * FROM s3('s3://bucket/data.parquet', NOSIGN) LIMIT 10")                 # 云存储
chdb.query("SELECT * FROM deltaLake('s3://bucket/delta/table', NOSIGN) LIMIT 10")           # 数据湖

# 跨源连接
chdb.query("""
    SELECT u.name, o.amount FROM mysql('db:3306', 'crm', 'users', 'root', 'pass') AS u
    JOIN file('orders.parquet', Parquet) AS o ON u.id = o.user_id ORDER BY o.amount DESC
""")

data = {"name": ["Alice", "Bob"], "score": [95, 87]}
chdb.query("SELECT * FROM Python(data) ORDER BY score DESC")                                # Python 数据
df = chdb.query("SELECT * FROM numbers(10)", "DataFrame")                                   # 输出格式
chdb.query("SELECT toDate({d:String}) + number FROM numbers({n:UInt64})",
    "DataFrame", params={"d": "2025-01-01", "n": 30})                                      # 参数化
```

表函数 → [table-functions.md](references/table-functions.md) | SQL 函数 → [sql-functions.md](references/sql-functions.md) | 完整 API → [api-reference.md](references/api-reference.md)

## Session — 状态分析管道

```python
from chdb import session as chs
sess = chs.Session("./analytics_db")   # 持久化；Session() 用于内存中

sess.query("CREATE TABLE users ENGINE=MergeTree() ORDER BY id AS SELECT * FROM mysql('db:3306','crm','users','root','pass')")
sess.query("CREATE TABLE events ENGINE=MergeTree() ORDER BY (ts,user_id) AS SELECT * FROM s3('s3://logs/events/*.parquet',NOSIGN)")
sess.query("""
    SELECT u.country, count() AS cnt, uniqExact(e.user_id) AS users
    FROM events e JOIN users u ON e.user_id = u.id
    WHERE e.ts >= today() - 7 GROUP BY u.country ORDER BY cnt DESC
""", "Pretty").show()
sess.close()
```

## 连接 API (DB-API 2.0)

```python
from chdb import dbapi
conn = dbapi.connect()
cur = conn.cursor()
cur.execute("SELECT * FROM file('data.parquet', Parquet) WHERE value > 100")
print(cur.fetchall())
cur.close()
conn.close()
```

## 故障排除

| 问题 | 解决方法 |
|---------|-----|
| `ImportError: No module named 'chdb'` | `pip install chdb` |
| `DB::Exception: FILE_NOT_FOUND` | 检查文件路径；使用绝对路径或验证当前工作目录 |
| `DB::Exception: Unknown table function` | 检查函数名称拼写（例如，`deltaLake` 而不是 `deltalake`） |
| 连接到远程数据库失败 | 检查主机:端口格式；确保远程数据库允许连接 |
| 环境检查 | 运行 `python scripts/verify_install.py`（从技能目录运行） |

## 参考

- [API 参考](references/api-reference.md) — query/Session/connect 签名
- [表函数](references/table-functions.md) — 所有 ClickHouse 表函数
- [SQL 函数](references/sql-functions.md) — 常用 SQL 函数
- [示例](examples/examples.md) — 9 个可运行示例及预期输出
- [官方文档](https://clickhouse.com/docs/chdb)

> 注意：此技能教你如何 *使用* chdb SQL。
> 对于 Pandas 风格的操作，请使用 `chdb-datastore` 技能。
> 要为 chdb 源代码做贡献，请查看项目根目录中的 CLAUDE.md。
