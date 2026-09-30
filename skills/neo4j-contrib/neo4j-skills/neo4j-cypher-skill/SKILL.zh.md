---
name: neo4j-cypher-skill
description: 生成、优化和验证适用于Neo4j 2025.x和2026.x的Cypher 25查询。在编写新的Cypher查询、优化慢查询、图模式匹配、向量或全文搜索、子查询或批量写入时使用。涵盖MATCH、MERGE、CREATE、WITH、RETURN、CALL、UNWIND、FOREACH、LOAD CSV、SEARCH、表达式、函数、索引和子查询。不处理驱动程序迁移或API变更——请使用neo4j-migration-skill。不涵盖数据库管理或服务器操作——请使用neo4j-cli-tools-skill。
---

## 使用场景

- 编写、优化或调试 Cypher 查询
- 图模式匹配、QPEs、可变长度路径
- 向量/全文搜索、子查询、批量写入、LOAD CSV

## 不适用场景

- **驱动迁移/API 变更** → `neo4j-migration-skill`
- **数据库管理**（用户、配置、备份）→ `neo4j-cli-tools-skill`
- **混合搜索**（结合向量与全文或其他排序源）→ `neo4j-vector-index-skill`

GQL 兼容性说明：`LET`、`FINISH`、`FILTER` 和 `INSERT` 是有效的 Cypher 25 子句（通过 GQL 兼容性引入，主要在 Neo4j 2025.06 中）。在旧版本中，回退到 `WITH` / (省略 RETURN) / `WHERE` / `CREATE`。`INSERT` 需要 `&` 分隔的多标签，不支持动态标签/类型。

---

## 预检查

| ? | 已知 | 未知 |
|---|---|---|
| 项目中找到 `<db-name>-schema.json` | 直接使用 — 跳过实时检查 | — |
| 模式（来自上下文或实时数据库） | 直接使用 | 运行 Schema-First 协议 |
| Neo4j 版本 | 使用版本特性 | 默认回退到 2025.01 安全集 |
| 执行（非生成）？ | 使用 EXPLAIN + 写入门 | 状态查询未验证 |

模式未知 + 无工具 → 在代码块外生成不可执行的草图：
```
(<SOURCE_LABEL> {<KEY>: $value})-[:<REL_TYPE>]->(<TARGET_LABEL>)
```
切勿填写猜测的名称 — 真实的猜测会被盲目复制。

---

## 默认值 — 每个查询都应用

1. `CYPHER 25` — 第一个标记；在 `UNION` 后或子查询内永不重复
2. 优先检查模式 — 在编写前检查；如果提示中包含模式，则直接使用
3. `MERGE` 仅在约束键上使用；关系 `MERGE` 仅在已绑定的端点上使用
4. 无标签 `MATCH (n)` 除非绑定或后跟 `WHERE n:$($label)`
5. 所有探索性读取默认 `LIMIT 25`；在高基数操作前推送 `WITH n LIMIT`（可变长度遍历、fan-out MATCH、笛卡尔积）
6. 注释：仅 `//` — `--` 是 SQL，无效
7. `REPEATABLE ELEMENTS` / `DIFFERENT RELATIONSHIPS` 在 `MATCH` 后，而不是模式末尾
8. `SHOW` 命令：`YIELD` 在 `WHERE` 之前；可与一般 Cypher 子句组合，包括 `UNION`/`RETURN` [2026.05] — `SHOW DATABASES` 仍需系统数据库（使用 `USE system`）。在 `system` 数据库上 `CALL`：`YIELD` 然后 `WHERE` [2026.07]
9. 内联节点谓词 `(:Label WHERE p=x)` — 仅在 `MATCH` 中有效
10. `WHERE` 不能在裸 `UNWIND` 后跟随 — 使用 `WITH x WHERE`
11. `(a)-[:R]-(b)` — 无向匹配双向，重复计数；除非未知，否则使用有向
12. `DETACH DELETE` — 裸 `DELETE` 如果节点有关系时会报错

---

## 风格

| 元素 | 规范 |
|---|---|
| 节点标签 | PascalCase `:Person` |
| 关系类型 | SCREAMING_SNAKE_CASE `:KNOWS` |
| 属性/变量 | camelCase `firstName` |
| 子句 | UPPERCASE `MATCH` |
| 布尔值/空值 | lowercase `true false null` |
| 字符串 | 单引号；仅当包含 `'` 时使用双引号 |

> 模式是真相。`:Person`、`:KNOWS`、示例中的 `name` 是说明性的 — 用来自模式的真实名称替换。

---

## Schema-First 协议

**优先级顺序：**

1. 项目中任何位置的 `<db-name>-schema.json` → 直接读取，声明文件名 + `schema_retrieved_at`，跳过实时检查。如果显著过时且数据库可达，则提供重新获取。完整规则：[references/schema-guardrail.md](references/schema-guardrail.md).
   - **存在性** — 标签/关系类型/属性必须在模式中；在询问前尝试同义词解析
   - **属性类型** — 首先推理意图（例如字符串 vs INTEGER 可能是空检查）；仅当不清楚时才询问
   - **关系方向** — 方向错误 → 静默纠正并记录
   - **同义词映射** — 无歧义 → 静默解析；歧义 → 选择最可能的，记录；如果无法解决则询问

   脚本：`generate_schema.py`（实时数据库 + APOC）、`define_schema.py`（无数据库）、`import_neo4j_schema.py`（将 `neo4j-graphrag-python`、`graph-schema-introspector`、`graph-schema-json-js-utils`、`mcp-neo4j-data-modeling` 转换）。

2. 上下文中的模式 → 使用，跳过检查。

3. 模式缺失 → 运行：
```cypher
CALL db.schema.visualization() YIELD nodes, relationships RETURN nodes, relationships;
SHOW INDEXES YIELD name, type, labelsOrTypes, properties, state WHERE state = 'ONLINE';
SHOW CONSTRAINTS YIELD name, type, labelsOrTypes, properties;
SHOW PROCEDURES YIELD name RETURN split(name,'.')[0] AS namespace, count(*) AS procedures;
```

每个标签的属性类型 — 首先检查 APOC：
```cypher
// 如果 APOC 可用（首选 — 使用此方法）：
CALL apoc.meta.schema() YIELD value RETURN value;

// 无 APOC 且数据库 ≤ 100k 节点/关系（在大型图上昂贵）：
CALL db.schema.nodeTypeProperties() YIELD nodeType, propertyName, propertyTypes, mandatory;
CALL db.schema.relTypeProperties() YIELD relType, propertyName, propertyTypes, mandatory;
```

验证任何查询返回之前：标签存在 · 关系类型+方向正确 · 该标签上的属性 · 索引在线。

---

## 关键模式

### MERGE
```cypher
// MERGE 约束键；在 ON CREATE/ON MATCH 设置额外内容
CYPHER 25
MATCH (a:Person {id: $a}) MATCH (b:Person {id: $b})
MERGE (a)-[r:KNOWS]->(b)
  ON CREATE SET r.since = date()
  ON MATCH  SET r.lastSeen = date()
```
`SET n = {}` 替换所有属性。`SET n += {}` 合并（安全的部分更新）。使用 `+=` 进行更新。

### WITH 范围
```cypher
CYPHER 25
MATCH (a:Person)-[:KNOWS]->(b:Person)
WITH a, count(*) AS friends   // b 在此处丢弃
WHERE friends > 5
RETURN a.name, friends ORDER BY friends DESC
```
未在 `WITH` 中列出的每个变量都会被丢弃。`WITH *` 会携带所有内容。

### 子查询 — 概要表
```
EXISTS { (a)-[:R]->(b) }                           // 布尔值检查
COUNT  { (a)-[:R]->(b) WHERE a.x > 0 }             // 计数
COLLECT { MATCH (a)-[:R]->(b) RETURN b.name }       // 收集列表（需要完整的 MATCH+RETURN）
CALL (p) { MATCH (p)-[:ACTED_IN]->(m) RETURN m }    // 相关子查询（显式导入）
OPTIONAL CALL (p) { ... }                           // 可空子查询
```
`CALL { WITH x ... }` 已弃用 → `CALL (x) { ... }`。`COLLECT {}` 返回恰好一列。

### 事务中的 CALL（批量写入）
```cypher
CYPHER 25
LOAD CSV WITH HEADERS FROM 'file:///data.csv' AS row
CALL (row) {
  MERGE (p:Person {id: row.id}) SET p += row
} IN TRANSACTIONS OF 1000 ROWS ON ERROR CONTINUE REPORT STATUS AS s
```
输入流必须在子查询外。仅自动提交 — 永远不要用 `beginTransaction()` 包裹。`PERIODIC COMMIT` 已弃用。

`DISJOINT BY` [2026.06, Cypher 25] 在 `IN CONCURRENT TRANSACTIONS` 上防止死锁，通过按顺序调度共享锁敏感资源的批次来阻止 — 在导入关系时使用：
```cypher
CYPHER 25
LOAD CSV WITH HEADERS FROM 'file:///rels.csv' AS line
CALL (line) {
  MATCH (a:Movie {id: line.movieId}), (b:Person {id: line.personId})
  MERGE (b)-[:ACTED_IN]->(a)
} IN CONCURRENT TRANSACTIONS OF 1000 ROWS DISJOINT BY (line.movieId, line.personId)
```
`DISJOINT BY (expr,...)` 声明锁键（仅限外部查询变量）；`DISJOINT BY AUTO` 通过静态分析推断；`DISJOINT BY NONE` 禁用。覆盖 `dbms.cypher.transactions.default_subquery_batch_strategy`。`EXPLAIN`/`PROFILE` 显示 `TransactionForeach` 中的 `DISJOINT BY (...)` 锁键。

### QPE 基础
```cypher
CYPHER 25
MATCH SHORTEST 1 (a:Person {name:'Alice'})(()-[:KNOWS]->())->(b:Person {name:'Bob'})
RETURN b.name

// ACYCLIC [2026.03] — 路径内没有重复节点（防止循环）
CYPHER 25
MATCH p = ACYCLIC (start:Router {name: $from})-[:LINK]-+(end:Router {name: $to})
RETURN [n IN nodes(p) | n.name] AS route
ORDER BY length(p) LIMIT 5
```
量词在组外：`(pattern){N,M}`。组从起点和终点开始与节点。`REPEATABLE ELEMENTS` 需要限定 `{m,n}`。`ACYCLIC` 意味着节点不能在路径内重复（比默认 `DIFFERENT RELATIONSHIPS` 更强）。

匹配模式 — 在 `MATCH` 后添加：
- `DIFFERENT RELATIONSHIPS`（默认）— 每个关系在路径中只遍历一次
- `REPEATABLE ELEMENTS` [2025.x] — 节点/关系可重复访问；用于循环路线、权重优化路径、约束回溯；需要限定 `{m,n}`

### 条件 CALL 子查询 [2025.06]
```cypher
CYPHER 25
MATCH (move:Item {id: $id})
OPTIONAL MATCH (insertBefore:Item {id: $before})
OPTIONAL MATCH (insertAfter:Item  {id: $after})
CALL (move, insertBefore, insertAfter) {
  WHEN insertBefore IS NULL THEN {
    MATCH (last:Item) WHERE NOT (last)-[:NEXT]->() AND last <> move
    CREATE (last)-[:NEXT]->(move)
  }
  WHEN insertAfter IS NULL THEN {
    CREATE (move)-[:NEXT]->(insertBefore)
  }
  ELSE {
    CREATE (insertAfter)-[:NEXT]->(move)
    CREATE (move)-[:NEXT]->(insertBefore)
  }
}
```
使用 WHEN…THEN…ELSE 进行 if-else-if 写逻辑；互斥（第一个匹配获胜）。2025.06 之前不可用。

### 动态关系类型 [2025.x]
```cypher
// 创建/匹配/合并动态关系类型（必须解析为恰好一个 STRING）
CYPHER 25 CREATE (a:Node)-[:$($relType)]->(b:Node)
CYPHER 25 MATCH  (a:Node)-[:$($relType)]->(b:Node) RETURN a.name, b.name
```

### 字符串插值 [2026.08, Cypher 25]
```cypher
CYPHER 25
MATCH (p:Person {id: $id})
RETURN s"Hello, {p.name}, age {p.age}" AS greeting   // S"..." 和 s'...' 等价
```
- 每个 `{expr}` 转换为 `toString()`
- `MAP`、`LIST`、`NODE`、`PATH`、`RELATIONSHIP` 被拒绝
- 用 `\{` 和 `\}` 转义字面量括号
- 插值字符串可以嵌套
- 永远不要将未受信任的值插值到传递给 `apoc.cypher.run*()` 的 Cypher 文本中；相反传递 `$parameters` 而不是

### UUID 类型 [2026.08, Cypher 25]
```cypher
CYPHER 25
CREATE (sess:Session {sessionId: uuid()});            // 随机 UUID 值

CYPHER 25
MATCH (sess:Session {sessionId: uuid($uuidString)})   // STRING 8-4-4-4-12 → UUID
RETURN toString(sess.sessionId) AS sessionId, uuid.mostSignificantBits(sess.sessionId) AS msb
```
`UUID` 属性需要 Neo4j 2026.08+。旧驱动可能返回占位符 `MAP` 加上警告 `03N95 Neo.ClientNotification.UnknownType` — 检查每个驱动技能以获取确切支持（`neo4j-driver-python-skill` 需要 >= 6.3）；否则保持 `randomUUID()` STRING ID。

### 空间 / Point
```cypher
// WGS84 地理点
SET n.coords = point({longitude: $lon, latitude: $lat})

// 米制距离；需要 Point 索引以提高性能
MATCH (a:Place {name: $origin}) MATCH (b:Place)
RETURN b.name, point.distance(a.coords, b.coords) AS distM
ORDER BY distM LIMIT 10

// 边界框预过滤（使用 Point 索引）然后距离
MATCH (b:Place)
WHERE point.withinBBox(b.coords,
        point({longitude: $west, latitude: $south}),
        point({longitude: $east, latitude: $north}))
RETURN b.name, point.distance(b.coords, $origin) AS distM
```
创建 Point 索引：`CREATE POINT INDEX name IF NOT EXISTS FOR (n:Place) ON (n.coords)`

### 聚合分组键
`RETURN`/`WITH` 中的非聚合表达式是隐式分组键 — `GROUP BY` 可选：
```cypher
// actor + director 是分组键；count(*) 是聚合
MATCH (a:Person)-[:ACTED_IN]->(m:Movie)<-[:DIRECTED]-(d:Person)
RETURN a.name, d.name, count(*) AS collaborations
ORDER BY collaborations DESC

// GROUP BY 明确声明键 [2026.07, Cypher 25]
MATCH (p:Person)-[:ACTED_IN]->(m:Movie)
RETURN p.name AS actor, m.genre AS genre, avg(m.rating) AS avgRating
GROUP BY actor, genre
```
显式 `GROUP BY` 子句在 `WITH`/`RETURN` [2026.07, Cypher 25] 中明确声明分组键 — GQL 对齐的替代方案，用于隐式分组；隐式分组仍然有效：
```cypher
MATCH (a:Person)-[:ACTED_IN]->(m:Movie)<-[:DIRECTED]-(d:Person)
RETURN a.name, d.name, count(*) AS collaborations GROUP BY a.name, d.name
ORDER BY collaborations DESC
```
`GROUP BY ()` = 无分组键（一行）；`GROUP BY ALL` = 每个非聚合返回项都是键。未在投影中出现的分组键不会被返回。规则 → [references/cypher-syntax.md](references/cypher-syntax.md)。

`count(n)` 计数非空；`count(*)` 计数包括空的行。`collect(DISTINCT expr)` 去重。
`count()` 比 `size(collect())` 更快 — `count()` 读取内部存储；`collect()` 首先构建列表。

`ORDER BY`/`WHERE` 子句表达式引用比变量或 `var.prop` 更复杂的投影项已弃用 [2026.07] — 在投影中别名声明的表达式并按别名排序。对阴影外部变量的名称也是如此。`ORDER BY`/`WHERE` 现在可以调用聚合函数，即使投影子句已经聚合。

| 特性 | 最低版本 | 回退方案 |
|---|---|---|
| `CYPHER 25`，QPE，`CALL (x) {}` | 2025.01 | 需要 2025+ |
| 匹配模式（`DIFFERENT RELATIONSHIPS`、`REPEATABLE ELEMENTS`） | 2025.01 | 需要 2025+ |
| 动态标签 `$($expr)`，`coll.sort()` | 2025.01 | APOC 或应用端 |
| `CONCURRENT TRANSACTIONS`，`REPORT STATUS` | 2025.01 | 删除 / 省略 |
| `SEARCH` 子句（向量/全文） | 2026.01 | `CALL db.index.vector.queryNodes(...)`（在 2026.04 中弃用） |
| `ACYCLIC` 路径模式（路径中无重复节点） | 2026.03 | 后置过滤 `size(nodes(p)) = size(apoc.coll.toSet(nodes(p)))` |
| `string.indexOf()`，`string.join()`，`string.regexReplace()` | 2026.05 | `apoc.text.*` 或应用端 |
| `WITH`/`RETURN` 上的 `GROUP BY` 子句，`cardinality()` | 2026.07 | 隐式分组键；`size()` / `size(keys(map))` |
| 在 `system` 数据库上运行的存储过程调用中的 `WHERE` 子句 | 2026.07 | 客户端侧过滤行 |
| GQL 别名：`FOR`=`UNWIND`，`PROPERTY_EXISTS`=`IS NOT NULL`，`IS [NOT] LABELED`=`n:Label`；函数别名（`local_time`、`zoned_datetime`、`duration_between`、`collect_list` 等） | 2026.02–04 | 仅用于 GQL 兼容性 — 使用 Cypher 等效形式；完整列表 → [references/cypher-syntax.md](references/cypher-syntax.md) |
| **GRAPH TYPE** 架构 DDL（`ALTER CURRENT GRAPH TYPE SET/ADD/ALTER/DROP`，`SHOW CURRENT GRAPH TYPE`） | 2026.02（预览），**GA 2026.06** | 使用单独的 `CREATE CONSTRAINT` / `CREATE INDEX` |
| `WITH`/`RETURN` 上的 `GROUP BY` 子句（显式分组键，GQL 对齐） | 2026.07 | 隐式分组 — 在投影中列出非聚合表达式 |
| `cardinality()` — MAP 中的键，LIST 中的元素，PATH 中的节点+关系 | 2026.07 | LIST/MAP 键使用 `size()`，PATH 使用 `length()` |
| `ORDER BY`/`WHERE` 中非投影项的聚合函数（仅限聚合投影） | 2026.07 | 将聚合结果作为别名投影，然后对别名进行排序/过滤 |
| `system` 数据库上存储过程调用中 `YIELD` 之后的 `WHERE` | 2026.07 | `YIELD` + `RETURN`，客户端侧过滤 |
| 字符串插值 `s"...{expr}..."` / `S"…"` | 2026.08 | 使用 `toString()` 或 `string.join()` 进行 `+` 连接 |
| `UUID` 类型；`uuid()`，`uuid(name)`，`uuid(mostSigBits, leastSigBits)`，`uuid.mostSignificantBits()`，`uuid.leastSignificantBits()` | 2026.08 | `randomUUID()` STRING 属性 |
| `null / 0` 返回 `null` 而非抛出除以零错误 | 2026.08 | `CASE WHEN d = 0 THEN null ELSE n / d END` |
| 映射推导 `{k: v IN map \| keyExpr: valueExpr}` | 2026.09 | `apoc.map.fromPairs([k IN keys(m) \| [k, m[k]]])` |
| 应用于 `LIST`、`MAP`、`NODE`、`RELATIONSHIP`、`PATH` 的 `toString()`，`toStringList()`，`toStringOrNull()` | 2026.09 | 单独转换标量组件，然后使用 `string.join()` |

---

## 性能

EXPLAIN/PROFILE 危险信号：`AllNodesScan`、`CartesianProduct`、`NodeByLabelScan`、`Eager`

修复 Eager — 三种方法（选择最简单有效的一种）：
1. **添加具体标签** 以消除 MATCH 节点中的读/写歧义：
   在写入 `:City` 节点时，使用 `MATCH (x:CallingPoint)` 而不是裸 `MATCH (x)`
2. **先收集，再写入**：`WITH collect(u) AS users UNWIND users AS u ...`
3. **CALL IN TRANSACTIONS**：将每个批次隔离在自己的事务中

标签推断 — 当规划器低估多标签查询的选择性时：[Neo4j 5]
```cypher
CYPHER inferSchemaParts = most_selective_label
MATCH (admin:Administrator {name: $name}), (resource:Resource {name: $res})
MATCH p=(admin)-[:MEMBER_OF]->()-[:ALLOWED_INHERIT]->(company)
RETURN count(p)
```

索引锚点：对属性进行的每个 MATCH/MERGE/WHERE 都需要在查找属性上有索引，否则 Neo4j 将扫描所有节点。**只有当节点拥有标签时，索引才会激活** — `MATCH (n {prop: $v})` 永远不使用索引；`MATCH (n:Label {prop: $v})` 会使用。没有约束的 MERGE 不保证原子性（两个并发 MERGE 可能创建重复项）。`CONTAINS`/`ENDS WITH` → TEXT 索引（RANGE 不支持）。当 EXPLAIN 显示扫描时，使用 `USING INDEX n:Label(prop)` 强制计划。
链式 `OPTIONAL MATCH` 用于嵌套数据 → 替换为 `COLLECT { MATCH ... RETURN }`。
动态标签（`$($label)`） → `AllNodesScan`+Filter；尽可能使用静态标签。

完整反模式 → [references/performance.md](references/performance.md)

---

## 故障恢复

- 0 结果：检查参数类型，逐一移除 WHERE 谓词，使用 EXPLAIN 检查索引使用情况
- TypeError：使用 `toIntegerOrNull()`/`toFloatOrNull()`；用 `IS NOT NULL` 进行保护
- 变量超出作用域：未列在 `WITH` 中 → 使用 `count(*)` 而不是 `count(droppedVar)`
- 超时：修复 AllNodesScan → 添加早期 `LIMIT` → `CALL IN TRANSACTIONS OF 1000 ROWS`
- 长运行查询进度 [2026.03]：`SHOW TRANSACTIONS YIELD currentQuery, status, currentQueryProgress`
- DateTime 不匹配：`ZONED DATETIME >= date(...)` → 0 行；使用 `datetime()` 或 `.year`
- `Z` 后缀 ≠ UTC 时区：带有 `Z` 的 ISO 字符串存储为 UTC 偏移量，而非 UTC 时区 — 跨越存储为 `Z` 和 `UTC` 的范围查询返回 0 行。在写入时强制转换：`datetime({datetime: datetime($isoStr), timezone: 'UTC'})`
- 持续时间：`.inDays`/`.inMonths` 不存在；使用 `.days`/`.months`
- `Cannot merge node using null property value`：MERGE 键解析为 null — 先验证参数
- `IndexNotFoundError`：`SHOW INDEXES YIELD name, state WHERE state <> 'ONLINE'`

---

## 参考

按需加载：
- [references/indexes.md](references/indexes.md) — 索引类型（RANGE/TEXT/FULLTEXT/POINT/COMPOSITE/LOOKUP），约束，MERGE 锁语义，全文 Lucene 语法，导入前检查
- [references/cypher-syntax.md](references/cypher-syntax.md) — 完整语法参考：WITH，DELETE，ORDER BY，CASE，null，列表，字符串，日期，空间/点，LOAD CSV，子查询，QPE，动态标签，SEARCH；条件 CALL（WHEN/THEN/ELSE）；标签模式表达式；allReduce；NEXT 子句；紧凑 CASE WHEN；normalize()；字符串插值；UUID 类型 + `uuid()` 函数 [2026.08]；映射推导 [2026.09]；索引/约束类型表；注明引入版本的函数
- [references/syntax-traps.md](references/syntax-traps.md) — 40+ 语法陷阱表
- [references/performance.md](references/performance.md) — 反模式，文本与全文索引，Eager（3 种修复策略），标签推断，批处理最佳实践，并行运行时
- [references/advanced-patterns.md](references/advanced-patterns.md) — REPEATABLE ELEMENTS 模式，allReduce 有状态遍历，多停靠 QPE，路线规划模拟，DAG 关键路径，时间欺诈检测组件图，循环检测，OPTIONAL CALL
- [references/apoc.md](references/apoc.md) — APOC Core：重构，虚拟图，合并助手，路径扩展器，触发器，集合，条件执行
- [references/graph-type.md](references/graph-type.md) — GRAPH TYPE DDL（GA 2026.06）：`ALTER CURRENT GRAPH TYPE SET/ADD/ALTER/DROP`，`SHOW CURRENT GRAPH TYPE [AS GRAPH]`，元素类型语法，属性类型，约束，标签影响，关系类型强制，所需权限

## WebFetch

| 需求 | URL |
|---|---|
| 子句语义 | `https://neo4j.com/docs/cypher-manual/25/clauses/{clause}/` |
| 函数签名 | `https://neo4j.com/docs/cypher-manual/25/functions/{type}/` |
| QPE / 路径 | `https://neo4j.com/docs/cypher-manual/25/patterns/` |
| 空间/点函数 | `https://neo4j.com/docs/cypher-manual/25/functions/spatial/` |
| 索引/约束参考 | `https://neo4j.com/docs/cypher-manual/25/indexes/` |
| 完整速查表 | `https://neo4j.com/docs/cypher-cheat-sheet/25/all/` |

---

## 检查清单
- [ ] 架构已检查或在上下文中确认
- [ ] 每个顶层查询都有 `CYPHER 25` 前缀
- [ ] 使用 `$parameters`（而非字面量）
- [ ] 探索性读取使用 `LIMIT`（默认 25）
- [ ] 已运行 `EXPLAIN`；已解决危险信号
- [ ] 写入半句已验证为 `RETURN` 后再执行
- [ ] 如果代理是执行（而非生成），则应用写入执行门控
- [ ] `MERGE` 仅用于受限键
- [ ] 不使用无标签的 `MATCH (n)`
- [ ] 架构操作不在显式事务内
