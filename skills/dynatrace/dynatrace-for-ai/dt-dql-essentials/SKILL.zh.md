---
name: dt-dql-essentials
description: 核心DQL语法、常见陷阱、查询模式及查询优化。用于编写、构建、修复或OPTIMIZE DQL查询——防止语法错误，并使查询更快、更高效、成本更低（扫描数据量减少 = 每次查询的消耗/成本降低）。涵盖获取命令、数据模型、字段命名空间、时间对齐、实体/Smartscape模式、指标发现以及性能/成本优化（早期过滤、分桶过滤、短时间范围、字段选择、采样、基数）。触发条件："编写/构建/修复DQL查询"、"DQL语法"、"查询日志/跨度/指标"、"创建时间序列"、"优化我的DQL"、"使我的查询更快/更便宜"、"减少DQL成本/消耗/扫描数据"、"控制DQL成本"。**不用于解释现有查询或回答产品问题**。若需监控租户的**实际查询消耗/计费**（查询成本、谁扫描最多、成本趋势），请使用`dt-platform-costs`——该工具调整查询文本，而非计费数据。
---

# DQL 基础技能

DQL 是一种基于管道的查询语言。查询通过 `|` 链接命令来过滤、转换和聚合数据。DQL 具有独特的语法，与 SQL 不同——在编写任何 DQL 查询之前，请先加载此技能。

______________________________________________________________________

## 加载参考的时机

在处理特定任务之前，加载相关的参考：

| 任务                                                                          | 必读内容                                                                             |
| ----------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| 发现数据 | [references/discovery.md](references/discovery.md) |   
| 字段名、命名空间、数据模型、稳定性级别、查询模式        | [references/semantic-dictionary.md](references/semantic-dictionary.md)                       |
| 查询优化——使查询更快 / 更高效 / 更便宜，减少消耗与扫描数据（早期过滤、桶过滤、时间范围、字段选择、采样、基数） | [references/optimization.md](references/optimization.md)                                     |
| Smartscape 拓扑导航，用于发现实体之间的关系 | [references/smartscape-topology-navigation.md](references/smartscape-topology-navigation.md) |
| `summarize` 和 `makeTimeseries` 模式（桶化、日历月份）        | [references/summarization.md](references/summarization.md)                                   |
| 数组和时间序列操作 (`arrayFilter`, `collectArray`, 迭代）  | [references/iterative-expressions.md](references/iterative-expressions.md)                   |
| 条件逻辑 (`if/else` 链），`coalesce`，字符串/日期辅助函数         | [references/useful-expressions.md](references/useful-expressions.md)                         |
| `in` 运算符（子查询），完整的 `@` 时间对齐单位表                  | [references/operators.md](references/operators.md)                                           |
| `matchesValue`，`matchesPhrase`，`matchesPattern`，`in()` — 字符串模式匹配，正则表达式，数组匹配，通配符，大小写敏感 | [references/string-matching.md](references/string-matching.md)                               |

______________________________________________________________________

## DQL 参考索引

使用此索引从功能组（例如时间函数、转换）导航到其详细规范，或从函数名导航到其规范文件。

| 描述 | 项目 |
|-------------|-------|
| [数据类型](references/dql/dql-data-types.md) | `array`，`binary`，`boolean`，`double`，`duration`，`long`，`record`，`string`，`timeframe`，`timestamp`，`uid` |
| [参数值类型](references/dql/dql-parameter-value-types.md) | `bucket`，`dataObject`，`dplPattern`，`entityAttribute`，`entitySelector`，`entityType`，`enum`，`executionBlock`，`expressionTimeseriesAggregation`，`expressionWithConstantValue`，`expressionWithFieldAccess`，`fieldPattern`，`filePattern`，`identifierForAnyField`，`identifierForEdgeType`，`identifierForFieldOnRootLevel`，`identifierForNodeType`，`joinCondition`，`jsonPath`，`metricKey`，`metricTimeseriesAggregation`，`namelessDplPattern`，`nonEmptyExecutionBlock`，`prefix`，`primitiveValue`，`simpleIdentifier`，`tabularFileExisting`，`tabularFileNew`，`url` |
| [命令](references/dql/dql-commands.md) | `append`，`data`，`dedup`，`describe`，`expand`，`fetch`，`fields`，`fieldsAdd`，`fieldsFlatten`，`fieldsKeep`，`fieldsRemove`，`fieldsRename`，`fieldsSnapshot`，`fieldsSummary`，`filter`，`filterOut`，`join`，`joinNested`，`limit`，`load`，`lookup`，`makeTimeseries`，`metrics`，`parse`，`search`，`smartscapeEdges`，`smartscapeNodes`，`sort`，`summarize`，`timeseries`，`traverse` |
| [函数——聚合](references/dql/dql-functions-aggregation.md) | `avg`，`collectArray`，`collectDistinct`，`correlation`，`count`，`countDistinct`，`countDistinctApprox`，`countDistinctExact`，`countIf`，`max`，`median`，`min`，`percentRank`，`percentile`，`percentileFromSamples`，`percentiles`，`stddev`，`sum`，`takeAny`，`takeFirst`，`takeLast`，`takeMax`，`takeMin`，`variance` |
| [函数——数组](references/dql/dql-functions-array.md) | `arrayAvg`，`arrayConcat`，`arrayCumulativeSum`，`arrayDelta`，`arrayDiff`，`arrayDistinct`，`arrayFirst`，`arrayFlatten`，`arrayIndexOf`，`arrayLast`，`arrayLastIndexOf`，`arrayMax`，`arrayMedian`，`arrayMin`，`arrayMovingAvg`，`arrayMovingMax`，`arrayMovingMin`，`arrayMovingSum`，`arrayPercentile`，`arrayRemoveNulls`，`arrayReverse`，`arraySize`，`arraySlice`，`arraySort`，`arraySum`，`arrayToString`，`vectorCosineDistance`，`vectorInnerProductDistance`，`vectorL1Distance`，`vectorL2Distance` |
| [函数——位运算](references/dql/dql-functions-bitwise.md) | `bitwiseAnd`，`bitwiseCountOnes`，`bitwiseNot`，`bitwiseOr`，`bitwiseShiftLeft`，`bitwiseShiftRight`，`bitwiseXor` |
| [函数——布尔值](references/dql/dql-functions-boolean.md) | `exists`，`in`，`isFalseOrNull`，`isNotNull`，`isNull`，`isTrueOrNull`，`isUid128`，`isUid64`，`isUuid` |
| [函数——转换](references/dql/dql-functions-cast.md) | `asArray`，`asBinary`，`asBoolean`，`asDouble`，`asDuration`，`asIp`，`asLong`，`asNumber`，`asRecord`，`asSmartscapeId`，`asString`，`asTimeframe`，`asTimestamp`，`asUid` |
| [函数——常量](references/dql/dql-functions-constant.md) | `e`，`pi` |
| [函数——转换](references/dql/dql-functions-conversion.md) | `toArray`，`toBoolean`，`toDouble`，`toDuration`，`toIp`，`toLong`，`toSmartscapeId`，`toString`，`toTimeframe`，`toTimestamp`，`toUid`，`toVariant` |
| [函数——创建](references/dql/dql-functions-create.md) | `array`，`duration`，`ip`，`record`，`smartscapeId`，`timeframe`，`timestamp`，`timestampFromUnixMillis`，`timestampFromUnixNanos`，`timestampFromUnixSeconds`，`uid128`，`uid64`，`uuid` |
| [函数——加密](references/dql/dql-functions-cryptographic.md) | `hashCrc32`，`hashMd5`，`hashSha1`，`hashSha256`，`hashSha512`，`hashXxHash32`，`hashXxHash64` |
| [函数——实体](references/dql/dql-functions-entities.md) | `classicEntitySelector`，`entityAttr`，`entityName` |
| [函数——表达式的时间序列聚合](references/dql/dql-functions-expression-timeseries.md) | `avg`，`count`，`countDistinct`，`countDistinctApprox`，`countDistinctExact`，`countIf`，`end`，`max`，`median`，`min`，`percentRank`，`percentile`，`percentileFromSamples`，`start`，`sum` |
| [函数——流](references/dql/dql-functions-flow.md) | `coalesce`，`if` |
| [函数——通用](references/dql/dql-functions-general.md) | `jsonField`，`jsonPath`，`lookup`，`parse`，`parseAll`，`type` |
| [函数——获取](references/dql/dql-functions-get.md) | `arrayElement`，`getEnd`，`getHighBits`，`getLowBits`，`getStart` |
| [函数——迭代](references/dql/dql-functions-iterative.md) | `iAny`，`iCollectArray`，`iIndex` |
| [函数——数学](references/dql/dql-functions-mathematical.md) | `abs`，`acos`，`asin`，`atan`，`atan2`，`bin`，`cbrt`，`ceil`，`cos`，`cosh`，`degreeToRadian`，`exp`，`floor`，`hexStringToNumber`，`hypotenuse`，`log`，`log10`，`log1p`，`numberToHexString`，`power`，`radianToDegree`，`random`，`range`，`round`，`signum`，`sin`，`sinh`，`sqrt`，`tan`，`tanh` |
| [函数——网络](references/dql/dql-functions-network.md) | `ipIn`，`ipIsLinkLocal`，`ipIsLoopback`，`ipIsPrivate`，`ipIsPublic`，`ipMask`，`isIp`，`isIpV4`，`isIpV6` |
| [函数——Smartscape](references/dql/dql-functions-smartscape.md) | `getNodeField`，`getNodeName` |
| [函数——字符串](references/dql/dql-functions-string.md) | `concat`，`contains`，`decodeBase16ToBinary`，`decodeBase16ToString`，`decodeBase64ToBinary`，`decodeBase64ToString`，`decodeUrl`，`encodeBase16`，`encodeBase64`，`encodeUrl`，`endsWith`，`escape`，`getCharacter`，`indexOf`，`lastIndexOf`，`levenshteinDistance`，`like`，`lower`，`matchesPattern`，`matchesPhrase`，`matchesRegex`，`matchesValue`，`punctuation`，`replacePattern`，`replaceString`，`splitByPattern`，`splitString`，`startsWith`，`stringLength`，`substring`，`trim`，`unescape`，`unescapeHtml`，`upper` |
| [函数——时间](references/dql/dql-functions-time.md) | `formatTimestamp`，`getDayOfMonth`，`getDayOfWeek`，`getDayOfYear`，`getHour`，`getMinute`，`getMonth`，`getSecond`，`getWeekOfYear`，`getYear`，`now`，`unixMillisFromTimestamp`，`unixNanosFromTimestamp`，`unixSecondsFromTimestamp` |
| [函数——时间序列聚合](references/dql/dql-functions-timeseries.md) | `avg`，`count`，`countDistinct`，`end`，`max`，`median`，`min`，`percentRank`，`percentile`，`start`，`sum` |

______________________________________________________________________

## 语法陷阱

| ❌ 错误 | ✅ 正确 | 问题 |
| --- | --- | --- |
| `filter field in ["a", "b"]` | `filter in(field, {"a", "b"})` | `[` 和 `]` 在 DQL 中用于包裹子查询，但不会包裹**静态**数组字面量。使用 `{}` 或 `array()` 来表示静态值。 |
| `filter: { in(field, [sub-query]) }`（例如在 `timeseries filter:` 中） | `filter: { field in [sub-query] }` | `in()` 不接受执行块作为参数。当右侧是子查询（执行块）时，使用 `in` 运算符：`field in [执行块]`。 |
| `by: severity, status` | `by: {severity, status}` | `by:` 子句中的字段列表必须用花括号分组（`summarize`、`makeTimeseries` 等场景）。 |
| `contains(toLowercase(field), "err")` | `contains(field, "err", false)` | 不要用 `lower()` 进行不区分大小写的匹配。`contains()` 有一个内置的第三个位置参数 `caseSensitive`（默认为 `true`）。 |
| `filter name == "*serv*9*"` | `filter matchesValue(name, "*serv*") and matchesValue(name, "*9*")` | `==` 不支持通配符。`matchesValue()` 支持以 `*` 开头和/或结尾的模式通配符，但中间的通配符需要拆分成多个调用并用 `and` 连接。 |
| `matchesValue(field, "prod")` 在字符串字段上 | `contains(field, "prod")` | 没有通配符时，`matchesValue()` 执行精确匹配（不区分大小写），不会找到 `"production"`。使用 `contains()` 进行子串匹配（或 `matchesValue(field, "*prod*")` 进行通配符匹配）。 |
| `iAny(matchesValue(arr[], "x") OR matchesValue(arr[], "y"))` | `matchesValue(arr, {"x", "y"})` | `matchesValue` 接受第一个参数为数组字段，第二个参数为数组字面量 `{}`，不需要 `iAny` 或 `[]`。当在同一个字段上合并多个 `contains(f, x) OR contains(f, y)` 时，使用 `matchesValue(f, {"*x*", "*y*"})`。 |
| `iAny(matchesPhrase(arr[], "phrase"))` | `matchesPhrase(arr, "phrase")` | `matchesPhrase` 原生迭代数组字段，可以省略 `iAny(` 和 `[]`。注意：**第二个**参数必须是静态字符串；`matchesPhrase(f, array("a","b")[])` 会产生运行时错误。 |
| `contains(field, "pip")` 在短或常用标记上 | `matchesPhrase(field, "pip")` | `contains` 是纯子串匹配，`"pip"` 也会匹配 `"pipenv"`、`"gripping"`。`matchesPhrase` 对字符串进行分词，只匹配整个单词，减少误报。 |
| `iAny(in(lower(arr[]), array("a", "b")))` | `matchesValue(arr, {"a", "b"}, caseSensitive: false)` | `matchesValue` 默认不区分大小写，不需要 `lower()`、`in()` 或 `iAny` 包装。这里显式显示 `caseSensitive: false` 仅用于反映它替换的 `lower()` 的意图。 |
| `iAny(f1[] == "a" AND f2[] == "b")` 迭代两个独立的数组 | `in(f1, "a") AND in(f2, "b")` | 多个数组的 `iAny` 是**成对**的，不是交叉乘积：`f1[]` 的第 `i` 个元素被测试与 `f2[]` 的第 `i` 个元素。如果数组长度不同，结果为 `null`。使用独立的 `in()` 检查。参见 [references/iterative-expressions.md](references/iterative-expressions.md)。 |
| `toLowercase(field)` | `lower(field)` | 函数是 `lower()`，不是 `toLowercase()`。只有类型转换函数使用 `to` 前缀（`toString()`、`toLong()` 等）。 |
| `arrayAvg(field[])` 或 `arraySum(field[])` | `arrayAvg(field)` 或 `field[]` | `field[]` = 元素级迭代表达式（数组→数组）；`arrayAvg(field)` = 折叠为标量（数组→单个值）。不要混合使用两者——`arrayAvg(field[])` 在语义上错误。 |
| `my_field` 在 `lookup` 或 `join` 之后 | `lookup.my_field` / `right.my_field` | `lookup` 默认为添加的字段添加 `lookup.` 前缀（可通过 `prefix:` 配置）。`join` 默认为右侧字段添加 `right.` 前缀。 |
| `substring(field, 0, 200)` | `substring(field, from: 0, to: 200)` | 第一个参数（表达式）是位置参数，但 `from:` 和 `to:` 是命名可选参数，必须包含其名称。 |
| `filter host = "A"` | `filter host == "A"` | DQL 使用 `==` 进行等值比较，而不是 `=`。单个 `=` 是赋值（例如在 `fieldsAdd`、summarize 别名中）。 |
| `fetch logs, from: toTimestamp('2026-01-01')` | `fetch logs, from: -24h` | `from:` / `to:` 接受持续时间字面量（例如 `-24h`、`-7d`）或 `now()` 表达式——不接受 `toTimestamp()`。绝对范围使用 `timeframe: "start/end"`（ISO 8601）。 |
| `filter log.level == "ERROR"` | `filter loglevel == "ERROR"` | 日志严重性字段是 `loglevel`（无点）——`log.level` 不存在。 |
| `sort count() desc` | `` sort `count()` desc `` | 特殊字符字段（如括号）必须用反引号包裹。 |
| `length(field)` | `stringLength(field)` | DQL 字符串长度函数是 `stringLength`——没有 `length()`。 |
| `metrics dt.host.cpu.usage` | `timeseries avg(dt.host.cpu.usage)` | `metrics` 加载指标元数据，不是值——使用 `timeseries` 获取数据。 |
| `join [...], on:{left.a.b == right.a.b}` | `` join [...], on:{left[`a.b`] == right[`a.b`]} `` | 连接/查找条件中的点分字段名需要带反引号的括号表示法。 |
| `fieldsSummary`（无参数） | `fieldsSummary field1, field2` | `fieldsSummary` 至少需要一个字段参数。 |
| `timeseries` 使用 `percentile`/`median`/`percentRank` — 无结果 | 在 `timeseries` 命令中添加 `rollup: avg`（或 `min`/`max`/`sum`） | 这三个函数**需要 `rollup:`**——没有它查询会静默返回空结果。 |
| `summarize p95 = percentile(duration, 95, rollup: avg)` | `summarize p95 = percentile(duration, 95)` | `rollup:` 是**`timeseries`-专用**参数。`summarize` 中对日志/跨度/事件的同名列名聚合会拒绝它并报 `UNKNOWN_PARAMETER_DEFINED`。仅在 `timeseries` 中聚合*指标*时添加 `rollup:`。 |
| `filter array.contains(field, "v")` 或 `arrayContains(field, "v")` | `filter in(field, {"v"})` | DQL 中不存在这两个函数——它们都是从 Python/Java/SQL 虚构的。`in()` 已经原生支持**数组类型**字段（例如 `k8s.namespace.name` 在 `dt.davis.problems` 上）：如果任何针的元素匹配任何草稿元素，它返回 `true`。参见 [references/iterative-expressions.md](references/iterative-expressions.md)。 |
| `filter k8s.namespace.name == "ns"` 其中字段是数组类型 | `filter in(k8s.namespace.name, {"ns"})` | 对数组类型字段使用 `==` 匹配**无结果**——它返回零行且无错误，这读作“无数据”而非错误。`k8s.*` 字段在 `dt.davis.problems` 上为数组。使用 `in()` 进行精确成员匹配，或 `matchesValue(field, {...})`。 |
| `parseJson(field)` 或 `extractJsonField(field, jsonPath: "$.x")` | `parse field, "JSON:parsed"` 然后访问 `parsed[x]` | 这两个函数都不存在。字符串字段中的嵌套 JSON 使用 `parse` 命令和 `JSON` DPL 匹配器展开，然后通过括号表示法访问。 |
| `filter hour(timestamp) == 4` / `minute(timestamp)` | `filter getHour(timestamp) == 4` / `getMinute(timestamp)` | 不存在 `hour()`/`minute()` 函数。`get*` 系列返回**数字**，因此支持数值比较和范围。不要用 `formatTimestamp(timestamp, format: "HH")`——它返回*字符串*，所以 `== 4` 静默匹配无结果。 |
| `fields fromRelationships, toRelationships, containerImageTag` 在 `dt.entity.*` 上 | 先 `describe dt.entity.<type>`，然后选择真实字段 | 经典实体对象**不**暴露 Entities REST API 的属性名。字段名必须用 `describe <dataObject>` 发现，而不是猜测 API 载荷。 |
| `by: {bin(timestamp, 1h)}` 然后 `` sort `bin(timestamp,1h)` `` | `by: {t = bin(timestamp, 1h)}` 然后 `sort t` | DQL 将自动生成的分组键名标准化为 `bin(timestamp, 1h)`——逗号后有空格，无论表达式如何书写。省略空格的反引号引用会引发 `FIELD_DOES_NOT_EXIST`。始终为分组键命名。 |
| `fetch spans \| ... by: {bin(timestamp, 1h)}` | `fetch spans \| ... by: {t = bin(start_time, 1h)}` | `spans` 没有 `timestamp` 字段——其时间字段是 `start_time` 和 `end_time`。引用 `timestamp` 会根据位置引发错误或返回空值。 |
| `` lookup [...], fields: {`dotted.name`} `` | `lookup [...], fields: {dotted.name}` | 在 `lookup` 的 `fields:` 参数中不要反引号字段名——会导致 `PARSE_ERROR`。 |
| `data record(key: "val")` | `data record(key = "val")` | `record()` 使用 `=` 为命名字段赋值，不是 `:`——`:` 用于命令参数如 `rollup:`。 |
| `getNodeField(dt.smartscape.host, "tags")["tag.key"]` | `getNodeField(dt.smartscape.host, "tags")[tag.key]` | 在标签映射访问模式中，括号键必须使用未引号的标识符语法；引号键会引发解析错误。 |
| `by: {dt.entity.host}` 或 `dt.entity.*` | `by: {dt.smartscape.host}` 或 `dt.smartscape.*` | `dt.entity.*` 已**弃用**——新查询始终使用 `dt.smartscape.*`。 |

______________________________________________________________________

## Fetch 命令 → 数据模型

DQL 查询以 `fetch <data_object>` 或 `timeseries` 开头。没有 `fetch dt.metric`——指标使用 `timeseries`。

| Fetch 命令 | 数据模型 | 关键字段/备注 |
|---------------|------------|--------------------|
| `fetch spans` | 分布式追踪 | `span.*`, `service.*`, `http.*`, `db.*`, `code.*`, `exception.*` |
| `fetch logs` | 日志事件 | `log.*`, `k8s.*`, `host.*` — 消息体是 `content`，严重性是 `loglevel`（非 `log.level`） |
| `fetch events` | DAVIS / 基础设施事件 | `event.*`, `dt.smartscape.*` |
| `fetch bizevents` | 业务事件 | `event.*`, 自定义字段 |
| `fetch security.events` | 安全事件 | `vulnerability.*`, `event.*` |
| `fetch user.sessions` | RUM 会话 | `dt.rum.*`, `browser.*`, `geo.*` |
| `fetch user.events` | RUM 单个事件 | 页面浏览、点击、请求、错误 |
| `fetch user.replays` | 会话回放录制 | |
| `fetch application.snapshots` | 应用快照 | |
| `fetch dt.davis.events` | Davis 检测到的事件 | |
| `fetch dt.davis.problems` | Davis 检测到的问题 | |
| `timeseries avg(metric.key)` | 指标 | 非 `fetch`——连字符键需要反引号：`` timeseries sum(`my.metric-name`) `` |
| `smartscapeNodes "HOST"` | 架构 | 非 `fetch`——类型：`HOST`, `SERVICE`, `K8S_CLUSTER` 等。 |

`dt.entity.*` 已弃用——新查询使用 `dt.smartscape.*` 和 `smartscapeNodes`。

发现所有可用数据对象：`fetch dt.system.data_objects | fields name, display_name, type`

→ [references/semantic-dictionary.md](references/semantic-dictionary.md) 获取完整字段命名空间

______________________________________________________________________

## `samplingRatio` 参数

`fetch` 支持参数 `samplingRatio:` 来减少读取的数据量——适用于在大型数据集上提高查询性能。

```dql
fetch spans, samplingRatio:100   // 读取约 1% 的数据
```

**允许值：** 取决于具体数据对象，范围从 `1`, `10`, `100`, `1000`, `10000` 到 `100000`，最高级别仅适用于 `logs` 和 `spans`。

采样是**分层**的，适用于 `spans`、`user.events` 和 `user.sessions`：在较高比率（例如 `100`）中包含的记录保证也会出现在较低比率（例如 `10`、`1`）中，反之则不一定。这意味着不同比率的结果是彼此的子集。其他非指标数据对象按记录独立采样，因此不同比率的结果不是子集。

实际应用的比率可通过 `dt.system.sampling_ratio` 字段访问。使用它将采样计数推算回真实总数：

```dql
fetch logs, samplingRatio:10
| summarize count_extrapolated = sum(dt.system.sampling_ratio)
```
______________________________________________________________________

## Timeseries 聚合函数

`timeseries` 命令仅支持以下聚合函数：

| 函数 | 描述 |
|----------|-------------|
| `sum` | 每个时间段指标数据的总和 |
| `avg` | 每个时间段指标数据的平均值 |
| `min` | 每个时间段指标数据的最小值 |
| `max` | 每个时间段指标数据的最大值 |
| `count` | 每个时间段指标数据的计数 |
| `percentile(metric, N)` | 每个时间段的第 N 百分位数。**需要 `rollup:`**——见下文。 |
| `median(metric)` | 每个时间段的 50 百分位数（等于 `percentile(metric, 50)`）。**需要 `rollup:`**。 |
| `percentRank(metric, value)` | 每个时间段的值百分位数排名。**需要 `rollup:`**。 |
| `countDistinct(metric)` | 每个时间段的近似唯一计数（仅限基数指标；不接受 `rollup:`）。 |

辅助函数（与聚合一起使用）：`start()`, `end()`。

**不支持 `timeseries` 的功能：** `countIf`, `collectArray`, `stddev`, `variance`, `takeAny`, `takeFirst`, `takeLast` — 使用 `summarize` 或 `makeTimeseries`。

### `rollup:` 参数

指标在摄取时预聚合。`rollup:` 控制每个时间段原始数据点的组合方式。对 `percentile`、`median`、`percentRank` 需要 `rollup:`——没有它查询会静默返回无结果。`avg`/`min`/`max`/`sum`/`count` 不需要 `rollup:`。

`rollup:` 是**`timeseries`-专用**参数——它属于指标聚合，不属于其他任何内容。`summarize` 中事件数据（日志、跨度、事件）的同类聚合函数不接受它：`summarize p95 = percentile(duration, 95, rollup: avg)` 会报 `UNKNOWN_PARAMETER_DEFINED`。在 `summarize` 中，使用无 `rollup:` 的 `percentile(field, N)`。

单一聚合——命令级别的 `rollup:`。多个聚合在 `{}` 中——`rollup:` 必须在**每个函数调用**内部（命令级别的 `rollup:` 会引发 `UNKNOWN_PARAMETER_DEFINED`）：

```dql
timeseries p90 = percentile(dt.process.handles.file_descriptors_percent_used, 90), rollup: avg
```

```dql
timeseries {
  p90 = percentile(dt.process.handles.file_descriptors_percent_used, 90, rollup: avg),
  med = median(dt.process.handles.file_descriptors_percent_used, rollup: avg),
  avg_val = avg(dt.process.handles.file_descriptors_percent_used)
}, by: {dt.smartscape.host}
```

值：`avg`（指标）、`min`、`max`、`sum`（计数器）、`total`。

### Timeseries-to-scalar 转换

有两种方法将 timeseries 折叠为标量。当只需要单个聚合值时，优先使用 `scalar:true` 参数——它更高效，因为不会创建数组。当需要在同一查询中同时获取完整序列和衍生标量时，回退到数组函数。

**优先：聚合函数上的 `scalar:true`**

向任何 timeseries 聚合函数传递 `scalar:true`。结果字段包含单个值，而不是数组，并且不会分配中间数组：

```dql
timeseries avg_cpu = avg(dt.host.cpu.usage, scalar:true), by:{dt.smartscape.host}
```

```dql
timeseries {
  avg_cpu = avg(dt.host.cpu.usage, scalar:true),
  max_cpu = max(dt.host.cpu.usage, scalar:true)
}, by:{dt.smartscape.host}
```

**回退：`fieldsAdd` 中的数组函数**

当需要完整时间序列数组以及衍生标量时，在后续 `| fieldsAdd` 中使用数组函数：

| 函数 | 描述 |
|----------|-------------|
| `arrayAvg(arr)` | 数组中所有值的平均值 |
| `arraySum(arr)` | 数组的总和 |
| `arrayMin(arr)` | 最小值 |
| `arrayMax(arr)` | 最大值 |
| `arrayMedian(arr)` | 中位数 |
| `arrayPercentile(arr, N)` | N 百分位数（0–100） |
| `arrayLast(arr)` | 最后一个非空值（最新数据点） |
| `arrayFirst(arr)` | 第一个非空值（最早数据点） |

```dql
timeseries cpu = avg(dt.host.cpu.usage), by:{dt.smartscape.host}
| fieldsAdd avg_cpu = arrayAvg(cpu), max_cpu = arrayMax(cpu)
```

______________________________________________________________________

## 时间对齐 (@-运算符)

`@`运算符将时间戳对齐到边界——代理经常会弄错这个。

| 表达式   | 含义                                                     |
| ------------ | ----------------------------------------------------------- |
| `now()@h`    | 当前时间，对齐到小时边界                                  |
| `now()@d`    | 今天午夜                                              |
| `now()@w1`   | 本周星期一                                            |
| `now()-2h@h` | 2小时前，对齐到小时（先偏移，再对齐）                     |

**规则：**

- 顺序：偏移量在前，对齐在后——`now()-2h@h`，不是`now()@h-2h`
- `@`和单位之间没有空格——`now()@h`不是`now() @h`
- `m` = 分钟，`M` = 月——不要混淆它们

→ [references/dql/dql-functions-timeseries.md](references/dql/dql-functions-timeseries.md) 获取`timeseries`聚合和`rollup:`规则的完整列表
→ [references/dql/dql-functions-array.md](references/dql/dql-functions-array.md) 获取`arrayAvg` / `arrayMax` / `arrayPercentile` / …规范

______________________________________________________________________

## 实体 & Smartscape模式

实体字段按类型作用域——`entity.id`不存在。使用`smartscapeNodes`进行拓扑查询。

| 实体      | 数据中的ID字段             | `smartscapeNodes`类型 |
| ----------- | ---------------------------- | ---------------------- |
| 主机        | `dt.smartscape.host`         | `"HOST"`               |
| 服务        | `dt.smartscape.service`      | `"SERVICE"`            |
| 进程        | `dt.smartscape.process`      | `"PROCESS"`            |
| K8s集群    | `dt.smartscape.k8s_cluster`  | `"K8S_CLUSTER"`        |

使用`toSmartscapeId()`进行ID从字符串的转换（必需！）！

→ [references/smartscape-topology-navigation.md](references/smartscape-topology-navigation.md)

______________________________________________________________________

## makeTimeseries命令

`makeTimeseries`从事件数据（日志、跨度、bizevents）构建一个时间分桶序列。与`timeseries`（查询预导入的指标）不同，`makeTimeseries`在管道中聚合数据。

**不要直接将`timeseries`管道输入`makeTimeseries`**——它将失败并显示`INVALID_IMPLICIT_TIME_DEFAULT`。要重新聚合指标数据，请使用`start()` + 扩展（参见[references/summarization.md](references/summarization.md)）。

```dql
fetch logs
| makeTimeseries
    total = count(),
    errors = countIf(loglevel == "ERROR"),
    interval: 5m,
    by: {k8s.cluster.name}
| fieldsAdd error_rate = errors[] * 100.0 / total[]
```

关键参数：`interval:`, `by:{}`, `from:`/`to:`, `bins:`, `time:`（时间戳字段），`spread:`（仅用于`count`/`countIf`），`nonempty:`。

→ [references/summarization.md](references/summarization.md) 获取完整的`makeTimeseries`模式和`summarize`分桶
→ [references/iterative-expressions.md](references/iterative-expressions.md) 获取时间序列数组操作

______________________________________________________________________

## 字符串匹配函数

DQL有四个主要的字符串和数组模式匹配函数。参见[references/string-matching.md](references/string-matching.md)获取完整指南和快速参考表。

- **`matchesValue(field, {"pattern*", "*other*"})`** — 通配符匹配（`*`在开头/结尾）。第一个参数接受数组字段，第二个参数接受数组字面量`{}`——不需要`iAny`或`[]`。默认不区分大小写（`caseSensitive: true`强制区分大小写匹配）。替换`contains()` + `iAny`链和`lower()`解决方案。
- **`matchesPhrase(field, "token")`** — 分词字符串并匹配整个单词，与`contains()`的裸子字符串匹配不同。第一个参数接受数组字段；第二个参数必须是**静态字符串**（数组解包会导致运行时错误）。
- **`in(field, array("a", "b"))`** — 集合成员。两个参数都接受数组，使其成为重叠/交集检查。

______________________________________________________________________

## 链式查找模式

每个不带`fields`参数的`lookup`命令**会删除以前缀开头的所有现有字段（默认：`lookup.`）**，然后再添加新字段。当链式多个查找时，使用`fields`参数或自定义前缀以保留结果：

**选项1（默认）**：已知所需字段。
```dql
fetch bizevents
// 第一步：第一个查找——用产品信息丰富订单
| lookup [fetch bizevents
    | filter event.type == "product_catalog"
    | fields product_id, category],
  sourceField: product_id, lookupField: product_id, fields: {product_id, product_category = category}

// 第二步：第二个查找——指定不同名称的字段
| lookup [fetch bizevents
    | filter event.type == "warehouse_stock"
    | fields category, warehouse_region],
  sourceField: product_category, lookupField: category, fields: {warehouse_region, warehouse_category = category}

```
所有4个查找字段`product_id`、`product_category`、`warehouse_region`和`warehouse_category`都可用。
如果没有`fields:{...}`参数，字段将被前缀`lookup.`，并且第二个查找命令将删除第一个查找添加的字段。

**选项2**：保留查找的所有字段。
```dql
fetch bizevents
// 第一步：第一个查找——用产品信息丰富订单
| lookup [fetch bizevents
    | filter event.type == "product_catalog"
    | fields product_id, category],
  sourceField: product_id, lookupField: product_id, prefix: "product."

// 第二步：第二个查找——使用不同前缀指定字段
| lookup [fetch bizevents
    | filter event.type == "warehouse_stock"
    | fields category, warehouse_region],
  sourceField: product_category, lookupField: category, prefix: "warehouse."

```
新字段为：`product.product_id`、`product.category`、`warehouse.category`、`warehouse.warehouse_region`。
从原始源中删除所有以`product.`或`warehouse.`开头的字段。
如果没有专用`prefix`，两个`lookup`命令将使用相同的前缀（`lookup.`），并且第二个`lookup`会清空第一个查找的结果——产生空字段。

______________________________________________________________________

## makeTimeseries命令

`makeTimeseries`从事件数据（日志、跨度、bizevents）构建一个时间分桶序列。与`timeseries`（查询预导入的指标）不同，`makeTimeseries`在管道中聚合数据。

**不要直接将`timeseries`管道输入`makeTimeseries`**——它将失败并显示`INVALID_IMPLICIT_TIME_DEFAULT`。要重新聚合指标数据，请使用`start()` + 扩展（参见[references/summarization.md](references/summarization.md)）。

```dql
fetch logs
| makeTimeseries
    {total = count(),
    errors = countIf(loglevel == "ERROR")},
    interval: 5m,
    by: {k8s.cluster.name}
| fieldsAdd error_rate = errors[] * 100.0 / total[]
```

关键参数：`interval:`, `by:{}`, `from:`/`to:`, `bins:`, `time:`（时间戳字段），`spread:`（仅用于`count`/`countIf`），`nonempty:`。→ [references/dql/dql-commands.md](references/dql/dql-commands.md) 获取完整规范。

使用`spread:`的实体存在时间线：

```dql
smartscapeNodes "HOST"
| makeTimeseries concurrently_existing_hosts = count(), spread: lifetime
```

→ [references/iterative-expressions.md](references/iterative-expressions.md) 获取时间序列数组操作

______________________________________________________________________

## 时间范围指定

访问数据需要指定时间范围。
可以在UI中指定，作为REST API参数，或在DQL查询中显式使用一对参数：`from:`和`to:`（如果省略一个，则默认为`now()`），或者使用单个`timeframe:`参数。
时间范围可以使用绝对值或相对于当前时间的相对表达式表示。可以使用时间对齐运算符（`@`）将时间戳四舍五入到时间单位边界——参见[references/operators.md](references/operators.md)获取完整详细信息。

### 示例

```dql-snippet
from:now()-1h@h, to:now()@h     // 上一个完整小时
```
```dql-snippet
from:now()-1d@d, to:now()@d     // 昨天完整
```
```dql-snippet
from:now()@M                    // 本月至今，到当前时间
```
```dql-snippet
from:now()-2h@h                 // 回溯2小时，然后对齐到小时边界
```

参见[references/operators.md](references/operators.md)获取完整的`@`对齐单位表（包括`m` vs. `M`，星期几变体`w1`–`w7`，以及因子规则如`@3h`）。

### 绝对时间戳

使用ISO 8601格式：

```dql-snippet
from:"2024-01-15T08:00:00Z", to:"2024-01-15T09:00:00Z"
```

______________________________________________________________________

## 修改时间

### 关键概念

- DQL有3个与时间相关的专用类型：
    - **时间戳**——内部保持为自纪元以来的纳秒数，但以特定时区的日期/时间形式显示
    - **时间范围**——一对2个时间戳（开始和结束）
    - **持续时间**——内部保持为纳秒数，但以合理因子缩放的形式显示（例如ms、分钟、天）

### 规则

- 减去时间戳产生持续时间：`timestamp - timestamp → duration`
- 持续时间除以持续时间产生双精度浮点数：例如`2h / 1m` = `120.0`
- 标量时间乘以持续时间产生持续时间：例如`no_of_h * 1h → duration`
- 提取时间元素（小时、月份中的天数等）：
    - ✅ 使用[时间函数](references/dql/dql-functions-time.md)。它们支持日历和时区，包括DST。
    - ❌ 避免使用`formatTimestamp`提取时间组件。
    - ❌ 避免将时间戳和持续时间转换为双精度浮点数/长整型，并使用除法、模运算和表示时间单位的纳秒常数。

## 参考

- **[references/useful-expressions.md](references/useful-expressions.md)** — DQL中有用的表达式
- **[references/semantic-dictionary.md](references/semantic-dictionary.md)** — Dynatrace语义词典：字段命名空间、数据模型、稳定性级别、查询模式和最佳实践
- **[references/summarization.md](references/summarization.md)** — 汇总和makeTimeseries命令的各种应用
- **[references/iterative-expressions.md](references/iterative-expressions.md)** — 使用DQL进行数组和时间序列操作（创建、修改、在过滤器中使用）
- **[references/smartscape-topology-navigation.md](references/smartscape-topology-navigation.md)** — Smartscape拓扑导航语法和模式
- **[references/optimization.md](references/optimization.md)** — DQL查询优化：使查询更快、更高效、更经济（降低消耗/每次执行扫描的数据量）——过滤器位置、分桶过滤器、时间范围、字段选择、采样、基数和性能最佳实践
- **[references/operators.md](references/operators.md)** — `in`运算符（子查询语法）和完整的`@`时间对齐单位参考
- **[references/discovery.md](references/discovery.md)** - 发现数据
