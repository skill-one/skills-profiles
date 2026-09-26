# Redis 搜索

Redis 搜索的单一指导来源——这是一个涵盖词汇、数值、地理、JSON 路径和向量查询的检索界面。向量字段与 TEXT/TAG/NUMERIC 字段属于同一个 `FT.CREATE` 机制，`FT.HYBRID` 命令在一个命令中混合了词汇和向量排序，因此这项技能将它们一起涵盖。

## 何时应用

- 创建、修改或审查 Redis 搜索索引 (`FT.CREATE`, `FT.ALTER`)。
- 编写或优化 `FT.SEARCH`, `FT.AGGREGATE` 或 `FT.HYBRID` 查询。
- 在 `TEXT`, `TAG`, `NUMERIC`, `GEO`, `GEOSHAPE`, `VECTOR` 或 JSON-path 字段之间进行选择。
- 定义 `VECTOR` 字段，选择 HNSW vs FLAT，调整 HNSW 参数。
- 构建检索增强生成 (RAG) 管道。
- 无停机时间地推出新的索引模式。
- 使用 `FT.EXPLAIN`, `FT.PROFILE`, `FT.INFO` 解决空结果、慢查询或 `FT` 的标记化问题。

## 1. 选择正确的命令

三个查询命令。选择最适合的狭窄命令。

| 命令 | 何时使用 | 心智模型 | 最小 Redis |
|---|---|---|---|
| **FT.SEARCH** | 文档检索，排序或排序。最佳默认值。 | 直接返回匹配的文档。 | 2.0 (模块) / 8.0 (内置) |
| **FT.AGGREGATE** | 分面、计算字段、自定义输出形状、分析。 | 声明式管道：`LOAD`, `APPLY`, `GROUPBY`, `REDUCE`, `SORTBY`。 | 2.0 / 8.0 |
| **FT.HYBRID** | 混合词汇 (BM25) 与向量相似度，具有可配置的融合。 | 带有明确的 `SEARCH` + `VSIM` 腿和 `COMBINE` 融合阶段的管道。 | **8.4.0** |

```
# FT.SEARCH — 最常用
FT.SEARCH idx:products "@category:{electronics} @price:[100 500]" LIMIT 0 20 RETURN 3 name price category

# FT.AGGREGATE — 按平均价格排序的前几类
FT.AGGREGATE idx:products "*" GROUPBY 1 @category REDUCE AVG 1 @price AS avg_price SORTBY 2 @avg_price DESC

# FT.HYBRID (Redis ≥ 8.4) — 词汇 + 向量融合
FT.HYBRID idx:docs
  SEARCH "@title:transformers" SCORER BM25 YIELD_SCORE_AS lexscore
  VSIM embedding $vec KNN count 1 K 50 YIELD_SCORE_AS vecscore
  COMBINE RRF 2 CONSTANT 60
  PARAMS 2 vec "..."
  DIALECT 2
```

对于 Redis < 8.4，词汇+向量混合使用 `FT.SEARCH` 预过滤 + `=>[KNN ...]` 近似。参见 [参考资料/command-selection.md](references/command-selection.md) 和 [参考资料/hybrid-search.md](references/hybrid-search.md)。

## 2. 模式基础 — `FT.CREATE`

`FT.CREATE` 索引匹配 `PREFIX` 的 Hash 或 JSON 文档。始终设置 `PREFIX`。使用 `DIALECT 2`（自 Redis 8 以来默认；向量查询需要）。

```
FT.CREATE idx:products ON HASH PREFIX 1 product:
    SCHEMA
        name TEXT WEIGHT 2.0
        category TAG SORTABLE
        price NUMERIC SORTABLE
        location GEO
        embedding VECTOR HNSW 6
            TYPE FLOAT32
            DIM 1536
            DISTANCE_METRIC COSINE
```

选择支持您的访问模式的狭窄字段类型：

| 字段类型 | 何时使用 | 备注 |
|---|---|---|
| `TEXT` | 全文搜索 | 分词 + 词干提取；**不**用于精确匹配 |
| `TAG` | 精确匹配 / 过滤 | 添加 `SORTABLE UNF` 以获得最快的标签查询 |
| `NUMERIC` | 范围查询、排序 | 价格、计数、时间戳 |
| `GEO` | 经纬度点 | 店铺、用户 |
| `GEOSHAPE` | 多边形 / 区域查询 | 配送区域、区域 |
| `VECTOR` | 相似度搜索 | HNSW 或 FLAT；参见 §4 |
| JSON `$.path AS alias` | 嵌套 JSON 字段 | `ON JSON`；参见 [参考资料/json-indexing.md](references/json-indexing.md) |

经典错误是将 `TEXT` 用于类别或状态字段“因为它是一个字符串”——`TAG` 对于精确匹配过滤的速度大约快 10 倍。

参见 [参考资料/index-creation.md](references/index-creation.md)、[参考资料/field-types.md](references/field-types.md)、[参考资料/dialect.md](references/dialect.md)、[参考资料/ft-create-options.md](references/ft-create-options.md)、[参考资料/json-indexing.md](references/json-indexing.md)。

## 3. 常见查询

使用过滤器缩小范围；仅返回您需要的内容。

```
# 标签过滤 + 数值范围，按价格排序
FT.SEARCH idx:products "@category:{electronics} @price:[100 500]"
    SORTBY price ASC
    LIMIT 0 20
    RETURN 3 name price category

# 文本 + 标签过滤
FT.SEARCH idx:products "wireless headphones @category:{audio}"

# 否定和 OR
FT.SEARCH idx:products "@category:{audio} -@brand:{generic} (@price:[0 100] | @on_sale:{true})"
```

值得记住的操作符：空格 = AND，`|` = OR，`-` = NOT，`~` = 可选（评分提升），`=>{$weight: N}` = 提升。在 TAG 值中转义连字符和特殊字符（`@sku:{ABC\\-123}`）。参见 [参考资料/query-syntax.md](references/query-syntax.md) 和 [参考资料/search-syntax-primitives.md](references/search-syntax-primitives.md) 以获取 DSL 词汇。

对于标记化陷阱（词干提取、停用词、语言）参见 [参考资料/text-tokenization.md](references/text-tokenization.md)。对于结果形状（`SORTBY`、`RETURN`、`HIGHLIGHT`、`SUMMARIZE`、`NOCONTENT`）参见 [参考资料/result-shaping.md](references/result-shaping.md)。对于性能杠杆（预过滤器、`SORTABLE` 字段、紧密的 `RETURN`、`FT.PROFILE`）参见 [参考资料/query-optimization.md](references/query-optimization.md)。

## 4. 向量基础

三个向量设置必须与嵌入模型完全匹配：

- **`DIM`** — 输出维度（例如 OpenAI `text-embedding-3-small` 的 1536）。不匹配会产生无声的垃圾。
- **`DISTANCE_METRIC`** — `COSINE` 用于归一化文本嵌入（常见情况），`IP` 用于未归一化的内积，`L2` 用于原始欧几里得。
- **`TYPE`** — 通常 `FLOAT32`。仅在内存是约束条件时使用 `FLOAT16` 或量化变体。

```
# 索引
FT.CREATE idx:docs ON HASH PREFIX 1 doc:
    SCHEMA
        content TEXT
        embedding VECTOR HNSW 6 TYPE FLOAT32 DIM 1536 DISTANCE_METRIC COSINE

# 纯 KNN 查询（按余弦相似度前 5）
FT.SEARCH idx:docs "*=>[KNN 5 @embedding $vec AS score]"
    PARAMS 2 vec "..."
    SORTBY score
    DIALECT 2
```

| 算法 | 速度 | 准确性 | 内存 | 用于 |
|---|---|---|---|---|
| **HNSW** | 快（近似） | ~95%+ 召回率（可调） | 较高 | 生产：>10k 向量，延迟敏感 |
| **FLAT** | 慢（精确） | 100% | 较低 | 小型语料库（<10k），需要精确匹配 |

HNSW 调整杠杆：`M`（16–64，每个节点的连接数）、`EF_CONSTRUCTION`（100–500，构建质量）、`EF_RUNTIME`（查询时间的候选列表）。

参见 [参考资料/vector-query.md](references/vector-query.md)、[参考资料/algorithm-choice.md](references/algorithm-choice.md)。

## 5. 混合检索

两种不同的模式被称为“混合”。根据意图选择。

**过滤后向量**（任何 Redis 版本）——应用属性过滤器，使引擎在向量比较之前缩小搜索空间。

```
FT.SEARCH idx:docs "(@category:{tech} @date:[2024 +inf])=>[KNN 10 @embedding $vec AS score]"
    PARAMS 2 vec "..."
    SORTBY score
    DIALECT 2
```

**词汇 + 向量融合**（Redis ≥ 8.4）——混合 BM25 文本评分与向量相似度，使用 `RRF` 或 `LINEAR` 融合。使用 `FT.HYBRID`（参见 §1）。

不要在客户端端获取宽泛的无过滤结果并进行过滤——更慢且准确性较低。参见 [参考资料/hybrid-search.md](references/hybrid-search.md)。

## 6. 聚合和形状

`FT.AGGREGATE` 是声明式结果形状命令。构建一个阶段的管道。

```
# 按总收入排序的前 5 类
FT.AGGREGATE idx:orders "@status:{shipped}"
    LOAD 2 @category @amount
    GROUPBY 1 @category
        REDUCE SUM 1 @amount AS revenue
    SORTBY 2 @revenue DESC
    LIMIT 0 5
```

常见阶段：`LOAD`、`APPLY`（计算字段）、`FILTER`（查询后）、`GROUPBY` + `REDUCE`（`SUM`、`COUNT`、`AVG`、`FIRST_VALUE`、`TOLIST`）、`SORTBY`、`LIMIT`。

对于长结果集，使用 `WITHCURSOR` + `FT.CURSOR READ` 在服务器端分页。参见 [参考资料/aggregate-pipeline.md](references/aggregate-pipeline.md) 和 [参考资料/aggregate-cursors.md](references/aggregate-cursors.md)。

## 7. RAG 模式

标准管道：嵌入查询，向量搜索 Redis，将前 K 个上下文传递给 LLM。

实用技巧：

- **匹配度量**以嵌入模型（几乎总是归一化文本模型的 `COSINE`）。
- **分块长文档**（200–500 个标记的块通常比索引整个页面效果更好）。
- **批量插入**而不是每条记录一个调用。
- **在向量搜索之前使用属性**（租户、新鲜度、文档类型）预过滤——参见 §5。
- **在顶部漏斗中重新排序**如果精度比召回率更重要。

参见 [参考资料/rag-pattern.md](references/rag-pattern.md)。

## 8. 操作

零停机时间模式更改：保持应用查询指向别名并交换底层索引。

```
FT.CREATE idx:products_v2 ON HASH PREFIX 1 product: SCHEMA ...
FT.ALIASUPDATE products idx:products_v2
# 应用查询是稳定的：
FT.SEARCH products "@category:{electronics}"
```

有用的管理命令：`FT.INFO`、`FT.DROPINDEX`、`FT._LIST`、`FT.ALIASADD/UPDATE/DEL`。参见 [参考资料/index-management.md](references/index-management.md)。

使用 `FT.EXPLAIN`（显示查询如何解析）和 `FT.PROFILE`（显示执行统计）调试空或慢查询。参见 [参考资料/debugging.md](references/debugging.md)。

## 9. 客户端示例

此 SKILL.md 中的内联示例是 CLI / RESP 形式——每个客户端序列化的线路协议。对于特定客户端的惯用片段：

- **redis-py**（Python，原始客户端）：[参考资料/clients/python-redis-py.md](references/clients/python-redis-py.md)
- **Jedis**（Java）：[参考资料/clients/java-jedis.md](references/clients/java-jedis.md)
- **RedisVL**（Python，redis-py 之上的高级 SDK）：[参考资料/clients/python-redisvl.md](references/clients/python-redisvl.md)

其他客户端（Lettuce、node-redis、go-redis、NRedisStack、.NET）翻译相同的 CLI 形式；覆盖范围作为后续跟踪。

## 参考资料

- [Redis: 搜索和查询](https://redis.io/docs/latest/develop/interact/search-and-query/)
- [Redis: 向量](https://redis.io/docs/latest/develop/ai/search-and-query/vectors/)
- [Redis: 查询语法](https://redis.io/docs/latest/develop/interact/search-and-query/query/)
- [Redis: 查询方言](https://redis.io/docs/latest/develop/interact/search-and-query/advanced-concepts/dialects/)
- [Redis: RAG 快速入门](https://redis.io/docs/latest/develop/get-started/rag/)
- [FT.CREATE](https://redis.io/docs/latest/commands/ft.create/) · [FT.SEARCH](https://redis.io/docs/latest/commands/ft.search/) · [FT.AGGREGATE](https://redis.io/docs/latest/commands/ft.aggregate/) · [FT.HYBRID](https://redis.io/docs/latest/commands/ft.hybrid/)
- [RedisVL 文档](https://docs.redisvl.com/en/latest/)
