# chdb 数据存储 — 它就是更快的 Pandas

## 核心洞察

```python
# 将此代码更改为：
import pandas as pd
# 更改为：
import chdb.datastore as pd
# 其他代码保持不变。
```

DataStore 是一个**惰性、基于 ClickHouse 的 pandas 替代品**。您现有的 pandas 代码可以保持不变——但操作会编译为优化的 SQL，并且仅在需要结果时执行（例如 `print()`、`len()`、迭代）。

```bash
pip install chdb
```

## 决策树：选择正确的方法

```
1. "我有一个文件/数据库，想用 pandas 分析它"
   → 使用 DataStore.from_file() / from_mysql() / from_s3() 等
   → 参考文档：connectors.md

2. "我需要连接来自不同来源的数据"
   → 从每个来源创建 DataStores，使用 .join()
   → 参考示例：examples.md #3-5

3. "我的 pandas 代码太慢了"
   → import chdb.datastore as pd — 修改一行，保留其余部分

4. "我需要原始 SQL 查询"
   → 使用 chdb-sql 技能
```

## 连接到任何数据源 — 一种模式

```python
from datastore import DataStore

# 本地文件（自动检测 .parquet、.csv、.json、.arrow、.orc、.avro、.tsv、.xml）
ds = DataStore.from_file("sales.parquet")

# 数据库
ds = DataStore.from_mysql(host="db:3306", database="shop", table="orders", user="root", password="pass")

# 云存储
ds = DataStore.from_s3("s3://bucket/data.parquet", nosign=True)

# URI 简写 — 自动检测来源类型
ds = DataStore.uri("mysql://root:pass@db:3306/shop/orders")
```

所有 16+ 来源和 URI 方案 → [connectors.md](references/connectors.md)

## 连接后 — 完整的 Pandas API

```python
result = ds[ds["age"] > 25]                                          # 筛选
result = ds[["name", "city"]]                                        # 选择列
result = ds.sort_values("revenue", ascending=False)                  # 排序
result = ds.groupby("dept")["salary"].mean()                         # 分组
result = ds.assign(margin=lambda x: x["profit"] / x["revenue"])     # 计算列
ds["name"].str.upper()                                               # 字符串访问器
ds["date"].dt.year                                                   # 日期时间访问器
result = ds1.join(ds2, on="id")                                      # 连接
result = ds.head(10)                                                 # 预览
print(ds.to_sql())                                                   # 查看生成的 SQL
```

支持 209 个 DataFrame 方法。完整 API → [api-reference.md](references/api-reference.md)

## 跨源连接 — 核心功能

```python
from datastore import DataStore

customers = DataStore.from_mysql(host="db:3306", database="crm", table="customers", user="root", password="pass")
orders = DataStore.from_file("orders.parquet")

result = (orders
    .join(customers, left_on="customer_id", right_on="id")
    .groupby("country")
    .agg({"amount": "sum", "rating": "mean"})
    .sort_values("sum", ascending=False))
print(result)
```

更多连接示例 → [examples.md](examples/examples.md)

## 写入数据

```python
source = DataStore.from_mysql(host="db:3306", database="shop", table="orders", user="root", password="pass")
target = DataStore("file", path="summary.parquet", format="Parquet")

target.insert_into("category", "total", "count").select_from(
    source.groupby("category").select("category", "sum(amount) AS total", "count() AS count")
).execute()
```

## 故障排除

| 问题 | 解决方法 |
|---------|-----|
| `ImportError: No module named 'chdb'` | `pip install chdb` |
| `ImportError: cannot import 'DataStore'` | 使用 `from datastore import DataStore` 或 `from chdb.datastore import DataStore` |
| 数据库连接超时 | 在主机中包含端口：`host="db:3306"` 而不是 `host="db"` |
| 连接返回空结果 | 检查键类型是否匹配（都是 int 或都是 string）；使用 `.to_sql()` 检查 |
| 预期结果异常 | 调用 `ds.to_sql()` 查看生成的 SQL 并调试 |
| 环境检查 | 运行 `python scripts/verify_install.py`（从技能目录） |

## 参考

- [API 参考](references/api-reference.md) — 完整的 DataStore 方法签名
- [连接器](references/connectors.md) — 所有 16+ 数据源连接方法
- [示例](examples/examples.md) — 10+ 可运行示例及预期输出
- [验证安装](scripts/verify_install.py) — 环境验证脚本
- [官方文档](https://clickhouse.com/docs/chdb)

> 注意：此技能教您如何使用 chdb DataStore。
> 对于原始 SQL 查询，请使用 `chdb-sql` 技能。
> 要为 chdb 源代码做贡献，请查看项目根目录中的 CLAUDE.md。
