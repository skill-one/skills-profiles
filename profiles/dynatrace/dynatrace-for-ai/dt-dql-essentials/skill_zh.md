# DQL 基础技能

DQL 是一种基于管道的查询语言。它使用 `|` 符号将命令链接起来，用于过滤、转换和聚合数据。DQL 具有独特的语法，与 SQL 不同——在编写任何 DQL 查询之前，请先加载此技能。

______________________________________________________________________

## 何时加载参考

在处理特定任务之前，加载相关的参考：

| 任务                                                                          | 必要阅读                                                                             |
| ----------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| 发现数据 | [references/discovery.md](references/discovery.md) |   
| 字段名、命名空间、数据模型、稳定性级别、查询模式        | [references/semantic-dictionary.md](references/semantic-dictionary.md)                       |
| 查询优化 — 使查询更快、更高效、更经济，减少消耗和扫描的数据（早期过滤、桶过滤器、时间范围、字段选择、采样、基数） | [references/optimization.md](references/optimization.md)                                     |
| Smartscape 拓扑导航，用于发现实体之间的关系 | [references/smartscape-topology-navigation.md](references/smartscape-topology-navigation.md) |
| `summarize` 和 `makeTimeseries` 模式（桶化、日历月份）        | [references/summarization.md](references/summarization.md)                                   |
| 数组和时间序列操作 (`arrayFilter`, `collectArray`, 迭代）  | [references/iterative-expressions.md](references/iterative-expressions.md)                   |
| 条件逻辑 (`if/else` 链），`coalesce`，字符串/日期辅助函数         | [references/useful-expressions.md](references/useful-expressions.md)                         |
| `in` 运算符（子查询），完整的 `@` 时间对齐单位表                  | [references/operators.md](references/operators.md)                                           |
| `matchesValue`，`matchesPhrase`，`matchesPattern`，`in()` — 字符串模式匹配，正则表达式，数组匹配，通配符，大小写敏感 | [references/string-matching.md](references/string-matching.md)                               |

______________________________________________________________________

## DQL 参考索引

使用此索引从功能组（例如时间函数、转换）路由到其详细规范，或从函数名路由到其规范文件。

| 描述 | 项目 |
|-------------|-------|
| [数据类型](references/dql/dql-data-types.md) | `array`, `binary`, `boolean`, `double`, `duration`, `long`, `record`, `string`, `timeframe`, `timestamp`, `uid` |
| [参数值类型](references/dql/dql-parameter-value-types.md) | `bucket`, `dataObject`, `dplPattern`, `entityAttribute`, `entitySelector`, `entityType`, `enum`, `executionBlock`, `expressionTimeseriesAggregation`, `expressionWithConstantValue`, `expressionWithFieldAccess`, `fieldPattern`, `filePattern`, `identifierForAnyField`, `identifierForEdgeType`, `identifierForFieldOnRootLevel`, `identifierForNodeType`, `joinCondition`, `jsonPath`, `metricKey`, `metricTimeseriesAggregation`, `namelessDplPattern`, `nonEmptyExecutionBlock`, `prefix`, `primitiveValue`, `simpleIdentifier`, `tabularFileExisting`, `tabularFileNew`, `url` |
| [命令](references/dql/dql-commands.md) | `append`, `data`, `dedup`, `describe`, `expand`, `fetch`, `fields`, `fieldsAdd`, `fieldsFlatten`, `fieldsKeep`, `fieldsRemove`, `fieldsRename`, `fieldsSnapshot`, `fieldsSummary`, `filter`, `filterOut`, `join`, `joinNested`, `limit`, `load`, `lookup`, `makeTimeseries`, `metrics`, `parse`, `search`, `smartscapeEdges`, `smartscapeNodes`, `sort`, `summarize`, `timeseries`, `traverse` |
| [函数 — 聚合](references/dql/dql-functions-aggregation.md) | `avg`, `collectArray`, `collectDistinct`, `correlation`, `count`, `countDistinct`, `countDistinctApprox`, `countDistinctExact`, `countIf`, `max`, `median`, `min`, `percentRank`, `percentile`, `percentileFromSamples`, `percentiles`, `stddev`, `sum`, `takeAny`, `takeFirst`, `takeLast`, `takeMax`, `takeMin`, `variance` |
| [函数 — 数组](references/dql/dql-functions-array.md) | `arrayAvg`, `arrayConcat`, `arrayCumulativeSum`, `arrayDelta`, `arrayDiff`, `arrayDistinct`, `arrayFirst`, `arrayFlatten`, `arrayIndexOf`, `arrayLast`, `arrayLastIndexOf`, `arrayMax`, `arrayMedian`, `arrayMin`, `arrayMovingAvg`, `arrayMovingMax`, `arrayMovingMin`, `arrayMovingSum`, `arrayPercentile`, `arrayRemoveNulls`, `arrayReverse`, `arraySize`, `arraySlice`, `arraySort`, `arraySum`, `arrayToString`, `vectorCosineDistance`, `vectorInnerProductDistance`, `vectorL1Distance`, `vectorL2Distance` |
| [函数 — 位运算](references/dql/dql-functions-bitwise.md) | `bitwiseAnd`, `bitwiseCountOnes`, `bitwiseNot`, `bitwiseOr`, `bitwiseShiftLeft`, `bitwiseShiftRight`, `bitwiseXor` |
| [函数 — 布尔值](references/dql/dql-functions-boolean.md) | `exists`, `in`, `isFalseOrNull`, `isNotNull`, `isNull`, `isTrueOrNull`, `isUid128`, `isUid64`, `isUuid` |
| [函数 — 转换](references/dql/dql-functions-cast.md) | `asArray`, `asBinary`, `asBoolean`, `asDouble`, `asDuration`, `asIp`, `asLong`, `asNumber`, `asRecord`, `asSmartscapeId`, `asString`, `asTimeframe`, `asTimestamp`, `asUid` |
| [函数 — 常量](references/dql/dql-functions-constant.md) | `e`, `pi` |
| [函数 — 转换](references/dql/dql-functions-conversion.md) | `toArray`, `toBoolean`, `toDouble`, `toDuration`, `toIp`, `toLong`, `toSmartscapeId`, `toString`, `toTimeframe`, `toTimestamp`, `toUid`, `toVariant` |
| [函数 — 创建](references/dql/dql-functions-create.md) | `array`, `duration`, `ip`, `record`, `smartscapeId`, `timeframe`, `timestamp`, `timestampFromUnixMillis`, `timestampFromUnixNanos`, `timestampFromUnixSeconds`, `uid128`, `uid64`, `uuid` |
| [函数 — 密码学](references/dql/dql-functions-cryptographic.md) | `hashCrc32`, `hashMd5`, `hashSha1`, `hashSha256`, `hashSha512`, `hashXxHash32`, `hashXxHash64` |
| [函数 — 实体](references/dql/dql-functions-entities.md) | `classicEntitySelector`, `entityAttr`, `entityName` |
| [函数 — 表达式的时间序列聚合](references/dql/dql-functions-expression-timeseries.md) | `avg`, `count`, `countDistinct`, `countDistinctApprox`, `countDistinctExact`, `countIf`, `end`, `max`, `median`, `min`, `percentRank`, `percentile`, `percentileFromSamples`, `start`, `sum` |
| [函数 — 流](references/dql/dql-functions-flow.md) | `coalesce`, `if` |
| [函数 — 通用](references/dql/dql-functions-general.md) | `jsonField`, `jsonPath`, `lookup`, `parse`, `parseAll`, `type` |
| [函数 — 获取](references/dql/dql-functions-get.md) | `arrayElement`, `getEnd`, `getHighBits`, `getLowBits`, `getStart` |
| [函数 — 迭代](references/dql/dql-functions-iterative.md) | `iAny`, `iCollectArray`, `iIndex` |
| [函数 — 数学](references/dql/dql-functions-mathematical.md) | `abs`, `acos`, `asin`, `atan`, `atan2`, `bin`, `cbrt`, `ceil`, `cos`, `cosh`, `degreeToRadian`, `exp`, `floor`, `hexStringToNumber`, `hypotenuse`, `log`, `log10`, `log1p`, `numberToHexString`, `power`, `radianToDegree`, `random`, `range`, `round`, `signum`, `sin`, `sinh`, `sqrt`, `tan`, `tanh` |
| [函数 — 网络](references/dql/dql-functions-network.md) | `ipIn`, `ipIsLinkLocal`, `ipIsLoopback`, `ipIsPrivate`, `ipIsPublic`, `ipMask`, `isIp`, `isIpV4`, `isIpV6` |
| [函数 — Smartscape](references/dql/dql-functions-smartscape.md) | `getNodeField`, `getNodeName` |
| [函数 — 字符串](references/dql/dql-functions-string.md) | `concat`, `contains`, `decodeBase16ToBinary`, `decodeBase16ToString`, `decodeBase64ToBinary`, `decodeBase64ToString`, `decodeUrl`, `encodeBase16`, `encodeBase64`, `encodeUrl`, `endsWith`, `escape`, `getCharacter`, `indexOf`, `lastIndexOf`, `levenshteinDistance`, `like`, `lower`, `matchesPattern`, `matchesPhrase`, `matchesRegex`, `matchesValue`, `punctuation`, `replacePattern`, `replaceString`, `splitByPattern`, `splitString`, `startsWith`, `stringLength`, `substring`, `trim`, `unescape`, `unescapeHtml`, `upper` |
| [函数 — 时间](references/dql/dql-functions-time.md) | `formatTimestamp`, `getDayOfMonth`, `getDayOfWeek`, `getDayOfYear`, `getHour`, `getMinute`, `getMonth`, `getSecond`, `getWeekOfYear`, `getYear`, `now`, `unixMillisFromTimestamp`, `unixNanosFromTimestamp`, `unixSecondsFromTimestamp` |
| [函数 — 时间序列聚合](references/dql/dql-functions-timeseries.md) | `avg`, `count`, `countDistinct`, `end`, `max`, `median`, `min`, `percentRank`, `percentile`, `start`, `sum` |

______________________________________________________________________

## Fetch 命令 → 数据模型

DQL 查询以 `fetch <data_object>` 或 `timeseries` 开头。没有 `fetch dt.metric`——指标使用 `timeseries`。

| Fetch 命令 | 数据模型 | 关键字段/备注 |
|---------------|------------|--------------------|
| `fetch spans` | 分布式追踪 | `span.*`, `service.*`, `http.*`, `db.*`, `code.*`, `exception.*` |
| `fetch logs` | 日志事件 | `log.*`, `k8s.*`, `host.*` — 消息体是 `content`，严重性是 `loglevel`（不是 `log.level`） |
| `fetch events` | DAVIS / 基础设施事件 | `event.*`, `dt.smartscape.*` |
| `fetch bizevents` | 业务事件 | `event.*`, 自定义字段 |
| `fetch security.events` | 安全事件 | `vulnerability.*`, `event.*` |
| `fetch user.sessions` | RUM 会话 | `dt.rum.*`, `browser.*`, `geo.*` |
| `fetch user.events` | RUM 单个事件 | 页面浏览、点击、请求、错误 |
| `fetch user.replays` | 会话重放录制 | |
| `fetch application.snapshots` | 应用快照 | |
| `fetch dt.davis.events` | Davis 检测到的事件 | |
| `fetch dt.davis.problems` | Davis 检测到的问题 | |
| `timeseries avg(metric.key)` | 指标 | 不是 `fetch`——带连字符的键需要反引号：`` timeseries sum(`my.metric-name`) `` |
| `smartscapeNodes "HOST"` | 拓扑 | 不是 `fetch`——类型：`HOST`, `SERVICE`, `K8S_CLUSTER` 等。 |

`dt.entity.*` 已弃用——新查询使用 `dt.smartscape.*` 和 `smartscapeNodes`。

发现所有可用的数据对象：`fetch dt.system.data_objects | fields name, display_name, type`

→ [references/semantic-dictionary.md](references/semantic-dictionary.md) for full field namespaces

______________________________________________________________________

## `samplingRatio` 参数

`fetch` 支持一个 `samplingRatio:` 参数来减少读取的数据量——对于在大型数据集上提高查询性能很有用。

```dql
fetch spans, samplingRatio:100   // 读取 ~1% 的数据
```

**允许的值：** 取决于具体的数据对象，范围从 `1`, `10`, `100`, `1000`, `10000` 到 `100000`，最高级别仅对 `logs` 和 `spans` 可用.


采样对于 `spans`, `user.events` 和 `user.sessions` 是**分层**的：在较高比率（例如 `100`）中包含的记录也保证在较低比率（例如 `10`, `1`）中也会出现，但反之则不然。这意味着不同比率的结果是彼此的子集。所有其他非指标数据对象是独立于每条记录采样的，因此不同比率的结果不是子集。

实际应用的比率可通过 `dt.system.sampling_ratio` 字段访问。使用它将采样计数值外推回真实总数：

```dql
fetch logs, samplingRatio:10
| summarize count_extrapolated = sum(dt.system.sampling_ratio)
```
______________________________________________________________________

## 时间序列聚合函数

`timeseries` 命令仅支持以下聚合函数：

| 函数 | 描述 |
|----------|-------------|
| `sum` | 每个时间槽的指标数据点之和 |
| `avg` | 每个时间槽的指标数据点的平均值 |
| `min` | 每个时间槽的指标数据点的最小值 |
| `max` | 每个时间槽的指标数据点的最大值 |
| `count` | 每个时间槽的指标数据点数量 |
| `percentile(metric, N)` | 每个时间槽的第 N 个百分位数。**需要 `rollup:`** — 下方有说明。 |
| `median(metric)` | 每个时间槽的 50% 百分位数 (= `percentile(metric, 50)`). **需要 `rollup:`**. |
| `percentRank(metric, value)` | 每个时间槽的值的百分位数。**需要 `rollup:`**. |
| `countDistinct(metric)` | 近似唯一计数每个时间槽（仅限基数指标；不接受 `rollup:`）。 |

辅助函数（与聚合一起使用）：`start()`, `end()`.

**不支持 `timeseries`:** `countIf`, `collectArray`, `stddev`, `variance`, `takeAny`, `takeFirst`, `takeLast` — 使用 `summarize` 或 `makeTimeseries`.

### `rollup:` 参数

指标在摄取时预先聚合。`rollup:` 控制每个时间槽的原始数据点如何组合。对于 `percentile`, `median`, `percentRank` 需要 `rollup:` — 没有 `rollup:`，查询将静默返回空结果。`avg`/`min`/`max`/`sum`/`count` 不需要 `rollup:`.

`rollup:` 是一个 **`timeseries`-only** 参数——它属于指标聚合，不属于其他任何内容。在 `summarize` 中可用的同名的聚合函数（在日志、跨度、事件数据上）不接受它：`summarize p95 = percentile(duration, 95, rollup: avg)` 会失败，报 `UNKNOWN_PARAMETER_DEFINED`。在 `summarize` 中，使用 `percentile(field, N)`，无需 `rollup:`。

单个聚合 — 命令级别的 `rollup:`。在 `{}` 中的多个聚合 — `rollup:` 必须在**每个函数调用**中（命令级别的 `rollup:` 会导致 `UNKNOWN_PARAMETER_DEFINED`）：

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

值：`avg`（仪表板），`min`, `max`, `sum`（计数器），`total`.

### 时间序列到标量转换

有两种方法将时间序列折叠为标量。当您只需要单个聚合值时，请使用 `scalar:true` 参数——它更高效，因为不会创建数组。当您需要在同一查询中同时获取完整序列和派生的标量时，请使用数组函数。

**首选：聚合函数上的 `scalar:true`**

将 `scalar:true` 传递给任何时间序列聚合函数。结果字段包含单个值，并且不会分配中间数组：

```dql
timeseries avg_cpu = avg(dt.host.cpu.usage, scalar:true), by:{dt.smartscape.host}
```

```dql
timeseries {
  avg_cpu = avg(dt.host.cpu.usage, scalar:true),
  max_cpu = max(dt.host.cpu.usage, scalar:true)
}, by:{dt.smartscape.host}
```

**后备：`fieldsAdd` 中的数组函数**

当您需要完整的时间序列数组以及派生的标量时，请在后续的 `| fieldsAdd` 中使用数组函数：

| 函数 | 描述 |
|----------|-------------|
| `arrayAvg(arr)` | 数组中所有值的平均值 |
| `arraySum(arr)` | 所有值的总和 |
| `arrayMin(arr)` | 最小值 |
| `arrayMax(arr)` | 最大值 |
| `arrayMedian(arr)` | 中位数 |
| `arrayPercentile(arr, N)` | Nth 百分位数 (0–100) |
| `arrayLast(arr)` | 最后一个非空值（最新数据点） |
| `arrayFirst(arr)` | 第一个非空值（最早数据点） |

```dql
timeseries cpu = avg(dt.host.cpu.usage), by:{dt.smartscape.host}
| fieldsAdd avg_cpu = arrayAvg(cpu), max_cpu = arrayMax(cpu)
```

______________________________________________________________________

## 时间对齐 (@-运算符)

`@` 运算符将时间戳对齐到边界——代理通常会弄错。

| 表达式   | 含义                                                     |
| ------------ | ----------------------------------------------------------- |
| `now()@h`    | 当前时间，对齐到小时边界                  |
| `now()@d`    | 今天午夜                                              |
| `now()@w1`   | 本周星期一                                            |
| `now()-2h@h` | 2 小时前，对齐到小时（先偏移，再对齐） |

**规则：**

- 顺序：偏移在前，对齐在后 — `now()-2h@h`, 不是 `now()@h-2h`
- `@` 和单位之间没有空格 — `now()@h` 不是 `now() @h`
- `m` = 分钟，`M` = 月份 — 不要混淆它们

→ [references/dql/dql-functions-timeseries.md](references/dql/dql-functions-timeseries.md) for the full list of `timeseries` aggregations and `rollup:` 规则
→ [references/dql/dql-functions-array.md](references/dql/dql-functions-array.md) for `arrayAvg` / `arrayMax` / `arrayPercentile` / … spec

______________________________________________________________________

## 实体和 Smartscape 模式

实体字段按类型作用域 — `entity.id` 不存在。使用 `smartscapeNodes` 进行拓扑查询。

| 实体      | 数据中的 ID 字段             | `smartscapeNodes` 类型 |
| ----------- | ---------------------------- | ---------------------- |
| Host        | `dt.smartscape.host`         | `"HOST"`               |
| Service     | `dt.smartscape.service`      | `"SERVICE"`            |
| Process     | `dt.smartscape.process`      | `"PROCESS"`            |
| K8s 集群 | `dt.smartscape.k8s_cluster`  | `"K8S_CLUSTER"`        |

使用 `toSmartscapeId()` 进行 ID 转换（从字符串）——需要！

→ [references/smartscape-topology-navigation.md](references/smartscape-topology-navigation.md)

______________________________________________________________________

## makeTimeseries 命令

`makeTimeseries` 从事件数据（日志、跨度、bizevents）构建时间分桶序列。与 `timeseries` 不同（后者查询预先摄取的指标），`makeTimeseries` 在管道中聚合数据。

**不要直接将 `timeseries` 接入 `makeTimeseries`** — 它会失败，报 `INVALID_IMPLICIT_TIME_DEFAULT`。要重新聚合指标数据，请使用 `start()` + 扩展（见 [references/summarization.md](references/summarization.md)）。

```dql
fetch logs
| makeTimeseries
    {total = count(),
    errors = countIf(loglevel == "ERROR")},
    interval: 5m,
    by: {k8s.cluster.name}
| fieldsAdd error_rate = errors[] * 100.0 / total[]
```

关键参数：`interval:`, `by:{}`, `from:`/`to:`, `bins:`, `time:`（时间戳字段），`spread:`（仅用于 `count`/`countIf`）, `nonempty:`。

→ [references/dql/dql-commands.md](references/dql/dql-commands.md) for full spec.

使用 `spread:` 的实体存在时间线：

```dql
smartscapeNodes "HOST"
| makeTimeseries concurrently_existing_hosts = count(), spread: lifetime
```

→ [references/iterative-expressions.md](references/iterative-expressions.md) for timeseries 数组操作

______________________________________________________________________

## 时间框架规范

访问数据需要指定时间框架。
它可以在 UI 中指定，作为 REST API 参数，或在 DQL 查询中显式使用一对参数：`from:` 和 `to:`（如果省略其中一个，则默认为 `now()`），或者 alternatively 使用单个 `timeframe:` 参数。
时间框架可以使用绝对值或相对于当前时间的相对表达式表示。可以使用时间对齐运算符 (`@`) 将时间戳四舍五入到时间单位边界 — see [references/operators.md](references/operators.md) for full details.

### 示例

```dql-snippet
from:now()-1h@h, to:now()@h     // 上一个完整小时
```
```dql-snippet
from:now()-1d@d, to:now()@d     // 昨天完整
```
```dql-snippet
from:now()@M                    // 本月至今，到当前
```
```dql-snippet
from:now()-2h@h                 // 回溯 2 小时，然后对齐到小时边界
```

See [references/operators.md](references/operators.md) for the full `@` 对齐单位表（包括 `m` vs. `M`，星期几变体 `w1`–`w7`，以及因子规则如 `@3h`）。

### 绝对时间戳

使用 ISO 8601 格式：

```dql-snippet
from:"2024-01-15T08:00:00Z", to:"2024-01-15T09:00:00Z"
```

______________________________________________________________________

## 修改时间

### 关键概念

- DQL 有 3 个与时间相关的特殊类型：
    - **timestamp** — 内部保持为自纪元以来的纳秒数，但显示为特定时区的日期/时间
    - **timeframe** — 一对两个时间戳（开始和结束）
    - **duration** — 内部保持为纳秒数，但显示为缩放后的合理因子（例如 ms、分钟、天）

### 规则

- 减去时间戳产生持续时间：`timestamp - timestamp → duration`
- 持续时间除以持续时间产生双精度浮点数：例如 `2h / 1m` = `120.0`
- 标量时间持续时间产生持续时间：例如 `no_of_h * 1h → duration`
- 提取时间元素（小时、月份中的天数等）：
    - ✅ 使用 [time functions](references/dql/dql-functions-time.md)。它们支持日历和时区，包括 DST。
    - ❌ 避免使用 `formatTimestamp` 提取时间组件。
    - ❌ 避免将时间戳和持续时间转换为双精度浮点数/长整型，并使用除法、模运算和表示时间单位的常量（以纳秒为单位）。

## 参考

- **[references/useful-expressions.md](references/useful-expressions.md)** — DQL 中的有用表达式
- **[references/semantic-dictionary.md](references/semantic-dictionary.md)** — Dynatrace 语义字典：字段命名空间、数据模型、稳定性级别、查询模式以及最佳实践
- **[references/summarization.md](references/summarization.md)** — summarize 和 makeTimeseries 命令的各种应用
- **[references/iterative-expressions.md](references/iterative-expressions.md)** — 使用 DQL 进行数组和时间序列操作（创建、修改、在过滤器中使用）
- **[references/smartscape-topology-navigation.md](references/smartscape-topology-navigation.md)** — Smartscape 拓扑导航语法和模式
- **[references/optimization.md](references/optimization.md)** — DQL 查询优化：使查询更快、更高效、更经济（降低执行时的消耗/扫描数据）— 过滤位置、桶过滤器、时间范围、字段选择、采样、基数以及性能最佳实践
- **[references/operators.md](references/operators.md)** — `in` 运算符（子查询语法）和完整的 `@` 时间对齐单位参考
- **[references/discovery.md](references/discovery.md)** - 发现数据
