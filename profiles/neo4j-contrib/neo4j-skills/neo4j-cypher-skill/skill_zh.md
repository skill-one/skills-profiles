## 使用时机
- 编写、优化或调试 Cypher 查询
- 图模式匹配、QPE、变长路径
- 向量/全文搜索、子查询、批量写入、LOAD CSV

## 不使用时机
- **驱动迁移/API 变更** → `neo4j-migration-skill`
- **数据库管理**（用户、配置、备份）→ `neo4j-cli-tools-skill`
- **混合搜索**（结合向量与全文或其他排序源）→ `neo4j-vector-index-skill`

GQL 合规性说明：`LET`、`FINISH`、`FILTER` 和 `INSERT` 是有效的 Cypher 25 子句（通过 GQL 合规性引入，主要在 Neo4j 2025.06 中）。在旧版本中，回退到 `WITH` /（省略 RETURN）/ `WHERE` / `CREATE`。`INSERT` 需要 `&`-分隔的多标签，不支持动态标签/类型。

---

## 预检查

| ? | 已知 | 未知 |
|---|---|---|
| `<db-name>-schema.json` 在项目中找到 | 直接使用——跳过实时检查 | — |
| 模式（来自上下文或实时数据库） | 直接使用 | 运行 Schema-First 协议 |
| Neo4j 版本 | 使用版本功能 | 默认使用 2025.01 安全集 |
| 执行（非生成）？ | 使用 EXPLAIN + 写入门 | 状态查询未验证 |

模式未知 + 无工具 → 在代码块外生成不可执行的草图：
```
(<SOURCE_LABEL> {<KEY>: $value})-[:<REL_TYPE>]->(<TARGET_LABEL>)
```
切勿填写猜测的名称——现实的猜测会被盲目复制。

---

## 默认值——每个查询都应用
1. `CYPHER 25` — 第一个标记；在 `UNION` 后或子查询内永不重复
2. 优先检查模式——在编写前检查；如果提示中有模式，直接使用
3. `MERGE` 仅在约束键上；关系 `MERGE` 仅在已绑定的端点上
4. 无标签 `MATCH (n)` 禁止，除非绑定或后跟 `WHERE n:$($label)`
5. 所有探索性读取默认 `LIMIT 25`；在高基数操作前推送 `WITH n LIMIT`（变长遍历、扇出 MATCH、笛卡尔积）
6. 注释：仅 `//` — `--` 是 SQL，无效
7. `REPEATABLE ELEMENTS` / `DIFFERENT RELATIONSHIPS` 在 `MATCH` 后，而不是模式末尾
8. `SHOW` 命令：`YIELD` 在 `WHERE` 前；可与一般 Cypher 子句组合，包括 `UNION`/`RETURN` [2026.05] — `SHOW DATABASES` 仍需系统数据库（使用 `USE system`）。在 `system` 数据库上 `CALL`：`YIELD` 然后 `WHERE` [2026.07]
9. 行内节点谓词 `(:Label WHERE p=x)` — 仅在 `MATCH` 中有效
10. `WHERE` 不能跟在裸 `UNWIND` 后 — 使用 `WITH x WHERE`
11. `(a)-[:R]-(b)` — 无向匹配双向，重复计数；除非未知，否则使用有向
12. `DETACH DELETE` — 裸 `DELETE` 如果节点有关系会报错

---

## 风格

| 元素 | 惯例 |
|---|---|
| 节点标签 | PascalCase `:Person` |
| 关系类型 | SCREAMING_SNAKE_CASE `:KNOWS` |
| 属性/变量 | camelCase `firstName` |
| 子句 | UPPERCASE `MATCH` |
| 布尔值/空值 | lowercase `true false null` |
| 字符串 | 单引号；仅当包含 `'` 时使用双引号 |

> 模式是真相。`:Person`、`:KNOWS`、`name` 在示例中是说明性的——用来自模式的真实名称替换。

---

## 先模式协议

**优先级顺序：**

1. `<db-name>-schema.json` 在项目中的任何位置 → 直接读取，声明文件名 + `schema_retrieved_at`，跳过实时检查。如果显著过时且可访问数据库，提供重新获取。完整规则：[references/schema-guardrail.md](references/schema-guardrail.md)。
   - **存在** — 标签/关系类型/属性必须在模式中；在询问之前尝试同义词解析
   - **属性类型** — 首先推理意图（例如字符串与 INTEGER 可能是空检查）；如果不清楚再询问
   - **关系方向** — 错误方向→静默纠正并记录
   - **同义词映射** — 无歧义→静默解析；歧义→选择最可能的，记录；如果无法解决则询问

   脚本：`generate_schema.py`（实时数据库 + APOC）、`define_schema.py`（无数据库）、`import_neo4j_schema.py`（将 `neo4j-graphrag-python`、`graph-schema-introspector`、`graph-schema-json-js-utils`、`mcp-neo4j-data-modeling` 转换）。

2. 上下文中的模式 → 使用，跳过检查。

3. 模式缺失 → 运行：
```cypher
CALL db.schema.visualization() YIELD nodes, relationships RETURN nodes, relationships;
SHOW INDEXES YIELD name, type, labelsOrTypes, properties, state WHERE state = 'ONLINE';
SHOW CONSTRAINTS YIELD name, type, labelsOrTypes, properties;
SHOW PROCEDURES YIELD name RETURN split(name,'.')[0] AS namespace, count(*) AS procedures;
```

每个标签的属性类型——首先检查 APOC：
```cypher
// 如果 APOC 可用（首选——使用这个）：
CALL apoc.meta.schema() YIELD value RETURN value;

// 无 APOC 且数据库 ≤ 100k 节点/关系（在大型图上昂贵）：
CALL db.schema.nodeTypeProperties() YIELD nodeType, propertyName, propertyTypes, mandatory;
CALL db.schema.relTypeProperties() YIELD relType, propertyName, propertyTypes, mandatory;
```

返回任何查询前验证：标签存在 · 关系类型+方向正确 · 该标签上的属性 · 索引在线。

---

## 关键模式

### MERGE
```cypher
// MERGE 在约束键上；在 ON CREATE/ON MATCH 中设置额外内容
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
未在 `WITH` 中列出的每个变量都会被丢弃。`WITH *` 会传递所有内容。

### 子查询——速查表
```
EXISTS { (a)-[:R]->(b) }                           // 布尔值检查
COUNT  { (a)-[:R]->(b) WHERE a.x > 0 }             // 计数
COLLECT { MATCH (a)-[:R]->(b) RETURN b.name }       // 收集列表（需要完整的 MATCH+RETURN）
CALL (p) { MATCH (p)-[:ACTED_IN]->(m) RETURN m }    // 相关子查询（显式导入）
OPTIONAL CALL (p) { ... }                           // 可空子查询
```
`CALL { WITH x ... }` 已弃用 → `CALL (x) { ... }`。`COLLECT {}` 返回恰好一列。

### 事务中的 CALL 批量写入 (bulk writes)
```cypher
CYPHER 25
LOAD CSV WITH HEADERS FROM 'file:///data.csv' AS row
CALL (row) {
  MERGE (p:Person {id: row.id}) SET p += row
} IN TRANSACTIONS OF 1000 ROWS ON ERROR CONTINUE REPORT STATUS AS s
```
输入流必须在子查询外。仅自动提交——切勿用 `beginTransaction()` 包裹。`PERIODIC COMMIT` 已弃用。

`DISJOINT BY` [2026.06, Cypher 25] 在 `IN CONCURRENT TRANSACTIONS` 中通过按顺序调度共享锁易冲突的资源来防止死锁——在导入关系时使用：
```cypher
CYPHER 25
LOAD CSV WITH HEADERS FROM 'file:///rels.csv' AS line
CALL (line) {
  MATCH (a:Movie {id: line.movieId}), (b:Person {id: line.personId})
  MERGE (b)-[:ACTED_IN]->(a)
} IN CONCURRENT TRANSACTIONS OF 1000 ROWS DISJOINT BY (line.movieId, line.personId)
```
`DISJOINT BY (expr,...)` 声明锁键（仅限外部查询变量）；`DISJOINT BY AUTO` 通过静态分析推断；`DISJOINT BY NONE` 禁用。覆盖 `dbms.cypher.transactions.default_subquery_batch_strategy`。`EXPLAIN`/`PROFILE` 在 `TransactionForeach` 中显示 `DISJOINT BY (...)` 中的键。

### QPE 基础
```cypher
CYPHER 25
MATCH SHORTEST 1 (a:Person {name:'Alice'})(()-[:KNOWS]->(){1,}(b:Person {name:'Bob'})
RETURN b.name

// ACYCLIC [2026.03] — 路径内无重复节点（防止循环）
CYPHER 25
MATCH p = ACYCLIC (start:Router {name: $from})-[:LINK]-+(end:Router {name: $to})
RETURN [n IN nodes(p) | n.name] AS route
ORDER BY length(p) LIMIT 5
```
量词在组外：`(pattern){N,M}`。组以节点开始+结束。`REPEATABLE ELEMENTS` 需要限定 `{m,n}`。`ACYCLIC` 意味着路径内节点不能重复（比默认 `DIFFERENT RELATIONSHIPS` 更强）。

匹配模式——在 `MATCH` 后添加：
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
使用 WHEN…THEN…ELSE 进行 if-else-if 写逻辑；互斥（第一个匹配生效）。2025.06 之前不可用。

### 动态关系类型 [2025.x]
```cypher
// 动态关系类型创建/匹配/合并（必须解析为恰好一个 STRING）
CYPHER 25 CREATE (a:Node)-[:$($relType)]->(b:Node)
CYPHER 25 MATCH  (a:Node)-[:$($relType)]->(b:Node) RETURN a.name, b.name
```

### 字符串插值 [2026.08, Cypher 25]
```cypher
CYPHER 25
MATCH (p:Person {id: $id})
RETURN s"Hello, {p.name}, age {p.age}" AS greeting   // S"..." 和 s'...' 等效
```
- 每个 `{expr}` 使用 `toString()` 转换
- `MAP`、`LIST`、`NODE`、`PATH`、`RELATIONSHIP` 被拒绝
- 转义文字括号 `\{` 和 `\}`
- 插值字符串可以嵌套
- 永不将未受信任的值插值到传递给 `apoc.cypher.run*()` 的 Cypher 文本中；相反传递 `$parameters`

### UUID 类型 [2026.08, Cypher 25]
```cypher
CYPHER 25
CREATE (sess:Session {sessionId: uuid()});            // 随机 UUID 值

CYPHER 25
MATCH (sess:Session {sessionId: uuid($uuidString)})   // STRING 8-4-4-4-12 → UUID
RETURN toString(sess.sessionId) AS sessionId, uuid.mostSignificantBits(sess.sessionId) AS msb
```
`UUID` 属性需要 Neo4j 2026.08+。旧驱动可能返回一个占位符 `MAP` 加上警告 `03N95 Neo.ClientNotification.UnknownType` — 检查每个驱动技能以获取确切支持（`neo4j-driver-python-skill` 需要 >= 6.3）；否则保持 `randomUUID()` STRING ID。

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
`RETURN`/`WITH` 中的非聚合表达式是隐式分组键——`GROUP BY` 可选：
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
显式 `GROUP BY` 子句在 `WITH`/`RETURN` [2026.07, Cypher 25] 明确声明分组键——GQL 对齐的替代方案，隐式分组仍然有效：
```cypher
MATCH (a:Person)-[:ACTED_IN]->(m:Movie)<-[:DIRECTED]-(d:Person)
RETURN a.name, d.name, count(*) AS collaborations GROUP BY a.name, d.name
ORDER BY collaborations DESC
```
`GROUP BY ()` = 无分组键（一行）；`GROUP BY ALL` = 每个非聚合返回项都是键。未在投影中出现的分组键不会被返回。规则 → [references/cypher-syntax.md](references/cypher-syntax.md)。

`count(n)` 计数非空；`count(*)` 计数包括空的行。`collect(DISTINCT expr)` 去重。
`count()` 比 `size(collect())` 更快——`count()` 直接读取内部存储；`collect()` 首先构建列表。

`ORDER BY`/`WHERE` 子句表达式引用比变量或 `var.prop` 更复杂的投影项已弃用 [2026.07] — 在投影中为表达式别名，然后按别名排序。对阴影输入变量的名称也相同。`ORDER BY`/`WHERE` 现在可以在投影子句已经聚合的情况下调用聚合函数。

---

## 常见语法陷阱（导致查询损坏的最常见原因）

| 错误 | 正确 |
|---|---|
| `ORDER BY n.prop AS x DESC` | `ORDER BY n.prop DESC` |
| `ORDER BY preAggVar` 在聚合后的 RETURN 后 | 使用 RETURN 别名 |
| `count(r WHERE r.x=5)` | `sum(CASE WHEN r.x=5 THEN 1 ELSE 0 END)` |
| `UNWIND list AS x WHERE x>5` | `UNWIND list AS x WITH x WHERE x>5` |
| `least(a,b)` / `greatest(a,b)` | `CASE WHEN a<b THEN a ELSE b END` |
| `-- comment` | `// comment` |
| `shortestPath((a)-[*]->(b))` | `SHORTEST 1 (a)(()-[]->(){1,}(b)` |
| `id(n)` | `elementId(n)` |
| `[:REL*1..5]` | `(()-[:REL]->){1,5}` |
| `CALL { WITH x ... }` | `CALL (x) { ... }` |
| `COLLECT { (a)-[:R]->(b) }` | `COLLECT { MATCH ... RETURN b }` |
| `SET n = {k:v}` 部分更新 | `SET n += {k:v}` |
| `DELETE n` 带关系 | `DETACH DELETE n` |
| `WHERE n.x = null` | `WHERE n.x IS NULL` |
| `toInteger(null)` 报错 | `toIntegerOrNull(null)` |
| `n.$key` 动态属性 | `n[$key]` |
| `SET n:$label` | `SET n:$($label)` |
| `ZONED DATETIME >= date(...)` → 0 rows | 使用 `datetime()` 或 `.year` 访问器 |
| ISO 字符串带 `Z` 后缀存储/比较为 UTC | **`Z` ≠ UTC 在 Neo4j** — `Z` 被解析为时区偏移，不是 UTC 时区；规划器和范围索引将它们视为不同。显式强制转换：`datetime({datetime: datetime('2025-09-10T03:43:00Z'), timezone: 'UTC'})` ([neo4j#13519](https://github.com/neo4j/neo4j/issues/13519)) |
| `FOREACH ... RETURN` | `UNWIND ... RETURN` |

完整陷阱表 → [references/syntax-traps.md](references/syntax-traps.md)

---

## 失败恢复

- 0 结果：检查参数类型，逐个移除 WHERE 谓词，EXPLAIN 检查索引使用
- 类型错误：使用 `toIntegerOrNull()`/`toFloatOrNull()`；用 `IS NOT NULL` 进行保护
- 变量超出范围：未在 `WITH` 中列出 → 使用 `count(*)` 而不是 `count(droppedVar)`
- 超时：修复 AllNodesScan → 添加早期 `LIMIT` → `CALL IN TRANSACTIONS OF 1000 ROWS`
- 长查询进度 [2026.03]: `SHOW TRANSACTIONS YIELD currentQuery, status, currentQueryProgress`
- 日期时间不匹配: `ZONED DATETIME >= date(...)` → 0 rows; 使用 `datetime()` 或 `.year`
- `Z` 后缀 ≠ UTC 时区: ISO 字符串带 `Z` 存储为 UTC 偏移，不是 UTC 区——存储的 `Z` 和 `UTC` 值之间的范围查询返回 0 行。写入时强制转换：`datetime({datetime: datetime($isoStr), timezone: 'UTC'})`
- 持续时间: `.inDays`/`.inMonths` 不存在；使用 `.days`/`.months`
- `Cannot merge node using null property value`: MERGE 键解析为 null — 首先验证参数
- `IndexNotFoundError`: `SHOW INDEXES YIELD name, state WHERE state <> 'ONLINE'`

---

## 参考文献

按需加载：
- [references/indexes.md](references/indexes.md) — 索引类型（RANGE/TEXT/FULLTEXT/POINT/COMPOSITE/LOOKUP）、约束、MERGE 锁语义、全文 Lucene 语法、导入预检查
- [references/cypher-syntax.md](references/cypher-syntax.md) — 完整语法参考：WITH, DELETE, ORDER BY, CASE, null, 列表, 字符串, 日期, 空间/point, LOAD CSV, 子查询, QPE, 动态标签, SEARCH；条件 CALL (WHEN/THEN/ELSE); 标签模式表达式; allReduce; NEXT 子句; 紧凑的 CASE WHEN; normalize(); 字符串插值; UUID 类型 + `uuid()` 函数 [2026.08]; 映射理解 [2026.09]; 索引/约束类型表; 带版本引入的函数
- [references/syntax-traps.md](references/syntax-traps.md) — 40+ 语法陷阱表
- [references/performance.md](references/performance.md) — 反模式, 文本 vs 全文索引, Eager (3 修复策略), 标签推断, 批处理最佳实践, 并行运行时
- [references/advanced-patterns.md](references/advanced-patterns.md) — REPEATABLE ELEMENTS 模式, allReduce 状态遍历, 多站 QPE, 路线规划模拟, DAG 关键路径, 时间欺诈检测组件图, 循环检测, OPTIONAL CALL
- [references/apoc.md](references/apoc.md) — APOC 核心：重构, 虚拟图, 合并辅助工具, 路径扩展器, 触发器, 集合, 条件执行
- [references/graph-type.md](references/graph-type.md) — GRAPH TYPE DDL (GA 2026.06): `ALTER CURRENT GRAPH TYPE SET/ADD/ALTER/DROP`, `SHOW CURRENT GRAPH TYPE [AS GRAPH]`, 元素类型语法, 属性类型, 约束, 标签含义, 关系类型强制执行, 必须权限

## WebFetch

| 需要 | URL |
|---|---|
| 子句语义 | `https://neo4j.com/docs/cypher-manual/25/clauses/{clause}/` |
| 函数签名 | `https://neo4j.com/docs/cypher-manual/25/functions/{type}/` |
| QPE / 路径 | `https://neo4j.com/docs/cypher-manual/25/patterns/` |
| 空间/point 函数 | `https://neo4j.com/docs/cypher-manual/25/functions/spatial/` |
| 索引/约束参考 | `https://neo4j.com/docs/cypher-manual/25/indexes/` |
| 完整速查表 | `https://neo4j.com/docs/cypher-cheat-sheet/25/all/` |

---

## 检查清单
- [ ] 检查模式或在上下文中确认
- [ ] 每个顶层查询使用 `CYPHER 25` 前缀
- [ ] 使用 `$parameters`（非文字）
- [ ] 探索性读取使用 `LIMIT`（默认 25）
- [ ] 运行 `EXPLAIN`；修复红色标志
- [ ] 写入部分验证为 `RETURN`，然后执行
- [ ] 如果代理执行（非生成），应用写入执行门
- [ ] 仅在约束键上使用 `MERGE`
- [ ] 无标签 `MATCH (n)` 禁止，除非绑定或后跟 `WHERE n:$($label)`
- [ ] 模式操作不在显式事务内
