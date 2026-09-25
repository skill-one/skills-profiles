# SPL到APL转换器

**类型安全：** 状态等字段通常存储为字符串。在数值比较前始终进行类型转换：toint(status) >= 500，而不是 status >= 500。

---

## 关键差异

1. **时间显式：** APL中时间明确——SPL时间选择器不转换——添加 `where _time between (ago(1h) .. now())`
2. **结构：** SPL `index=... | command` → APL `['dataset'] | operator`
3. **连接是预览：** 限制为50k行，仅支持内连接/内唯一/左外连接
4. **cidrmatch参数顺序相反：** SPL `cidrmatch(cidr, ip)` → APL `ipv4_is_in_range(ip, cidr)`

---

## 核心命令映射

| SPL | APL | 备注 |
|-----|-----|-------|
| `search index=...` | `['dataset']` | 数据集替换索引 |
| `search field=value` | `where field == "value"` | 显式where |
| `where` | `where` | 相同 |
| `stats` | `summarize` | 不同的聚合语法 |
| `eval` | `extend` | 创建/修改字段 |
| `table` / `fields` | `project` | 选择列 |
| `fields -` | `project-away` | 移除列 |
| `rename x as y` | `project-rename y = x` | 重命名 |
| `sort` / `sort -` | `order by ... asc/desc` | 排序 |
| `head N` | `take N` | 限制行数 |
| `top N field` | `summarize count() by field \| top N by count_` | 两步操作 |
| `dedup field` | `summarize arg_max(_time, *) by field` | 保留最新值 |
| `rex` | `parse` 或 `extract()` | 正则表达式提取 |
| `join` | `join` | **预览功能** |
| `append` | `union` | 合并数据集 |
| `mvexpand` | `mv-expand` | 扩展数组 |
| `timechart span=X` | `summarize ... by bin(_time, X)` | 手动分桶 |
| `rare N field` | `summarize count() by field \| order by count_ asc \| take N` | 底N值 |
| `spath` | `parse_json()` 或 `json['path']` | JSON访问 |
| `transaction` | 无直接等价物 | 使用summarize + make_list |

完整映射：`reference/command-mapping.md`

---

## 统计→汇总

```
# SPL
| stats count by status

# APL  
| summarize count() by status
```

### 关键函数映射

| SPL | APL |
|-----|-----|
| `count` | `count()` |
| `count(field)` | `countif(isnotnull(field))` |
| `dc(field)` | `dcount(field)` |
| `avg/sum/min/max` | 相同 |
| `median(field)` | `percentile(field, 50)` |
| `perc95(field)` | `percentile(field, 95)` |
| `first/last` | `arg_min/arg_max(_time, field)` |
| `list(field)` | `make_list(field)` |
| `values(field)` | `make_set(field)` |

### 条件计数模式

```
# SPL
| stats count(eval(status>=500)) as errors by host

# APL
| summarize errors = countif(status >= 500) by host
```

完整函数列表：`reference/function-mapping.md`

---

## Eval→Extend

```
# SPL
| eval new_field = old_field * 2

# APL
| extend new_field = old_field * 2
```

### 关键函数映射

| SPL | APL | 备注 |
|-----|-----|-------|
| `if(c, t, f)` | `iff(c, t, f)` | 双写'f' |
| `case(c1,v1,...)` | `case(c1,v1,...,default)` | 需要default |
| `len(str)` | `strlen(str)` | |
| `lower/upper` | `tolower/toupper` | |
| `substr` | `substring` | APL中为0索引 |
| `replace` | `replace_string` | |
| `tonumber` | `toint/tolong/toreal` | 显式类型 |
| `match(s,r)` | `s matches regex "r"` | 运算符 |
| `split(s, d)` | `split(s, d)` | 相同 |
| `mvjoin(mv, d)` | `strcat_array(arr, d)` | 数组合并 |
| `mvcount(mv)` | `array_length(arr)` | 数组长度 |

### Case语句模式

```
# SPL
| eval level = case(
    status >= 500, "error",
    status >= 400, "warning",
    1==1, "ok"
  )

# APL  
| extend level = case(
    status >= 500, "error",
    status >= 400, "warning",
    "ok"
  )
```

注意：SPL的`1==1`全匹配在APL中变为隐式默认值。

---

## Rex→Parse/Extract

```
# SPL
| rex field=message "user=(?<username>\w+)"

# APL - 使用正则解析
| parse kind=regex message with @"user=(?P<username>\w+)"

# APL - 提取函数  
| extend username = extract("user=(\\w+)", 1, message)
```

### 简单模式（非正则）

```
# SPL
| rex field=uri "^/api/(?<version>v\d+)/(?<endpoint>\w+)"

# APL
| parse uri with "/api/" version "/" endpoint
```

---

## 时间处理

SPL时间选择器不转换。始终添加显式时间范围：

```
# SPL (时间选择器：过去24小时)
index=logs

# APL
['logs'] | where _time between (ago(24h) .. now())
```

### Timechart转换

```
# SPL
| timechart span=5m count by status

# APL
| summarize count() by bin(_time, 5m), status
```

---

## 常见模式

### 错误率计算

```
# SPL
| stats count(eval(status>=500)) as errors, count as total by host
| eval error_rate = errors/total*100

# APL
| summarize errors = countif(status >= 500), total = count() by host
| extend error_rate = toreal(errors) / total * 100
```

### 子查询（subsearch）

```
# SPL
index=logs [search index=errors | fields user_id | format]

# APL
let error_users = ['errors'] | where _time between (ago(1h) .. now()) | distinct user_id;
['logs']
| where _time between (ago(1h) .. now())
| where user_id in (error_users)
```

### 连接数据集

```
# SPL
| join user_id [search index=users | fields user_id, name]

# APL
| join kind=inner (['users'] | project user_id, name) on user_id
```

### 事务式分组

```
# SPL
| transaction session_id maxspan=30m

# APL (无直接等价物——使用summarize重构)
| summarize 
    start_time = min(_time),
    end_time = max(_time),
    events = make_list(pack("time", _time, "action", action)),
    duration = max(_time) - min(_time)
  by session_id
| where duration <= 30m
```

---

## 字符串匹配性能

| SPL | APL | 速度 |
|-----|-----|-------|
| `field="value"` | `field == "value"` | **最快** |
| `field="*value*"` | `field contains "value"` | 中等 |
| `field="value*"` | `field startswith "value"` | 快 |
| `match(field, regex)` | `field matches regex "..."` | **最慢** |

优先使用`has`而非`contains`（词边界匹配更快）。使用`_cs`变体实现大小写敏感（更快）。

---

## 参考

- `reference/command-mapping.md` — 完整命令列表
- `reference/function-mapping.md` — 完整函数列表  
- `reference/examples.md` — 完整查询转换示例
- APL文档：https://axiom.co/docs/apl/introduction
