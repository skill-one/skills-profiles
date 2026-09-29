---
name: elasticsearch-esql
description: 执行 ES|QL（Elasticsearch 查询语言）查询，当用户需要查询 Elasticsearch 数据、分析日志、聚合指标、探索数据或从 ES|QL 结果创建图表和仪表板时使用。
---

# Elasticsearch ES|QL

对 Elasticsearch 执行 ES|QL 查询：发现模式，为任务选择合适的 ES|QL 功能，生成最简单的正确查询，并运行它。

<!-- begin-partial: preamble -->

## 环境配置

此技能通过 `elastic` CLI 执行 Elasticsearch 操作。如果未安装 [`elastic` CLI](https://github.com/elastic/cli#configuration)，请告知用户其用途。不要猜测凭证、直接调用 HTTP API 或尝试其他解决方案。

此技能以 HTTP 简写形式引用操作（例如，`GET /`、`GET /_cat/indices`、`GET /{index}/_mapping`、`GET /{index}/_settings/index.mode`、`POST /_query`）。本文件末尾的 [操作](#operations) 表将每个简写映射到等效的 `elastic` CLI 命令——始终使用 CLI 而不是直接调用 HTTP API。

<!-- end-partial: preamble -->

## 什么是 ES|QL？

ES|QL（Elasticsearch 查询语言）是一种用于 Elasticsearch 的管道查询语言。它**不是**以下任何一种：

- Elasticsearch 查询 DSL（基于 JSON）
- SQL
- EQL（事件查询语言）

ES|QL 使用管道（`|`）来串联命令：
`FROM index | WHERE condition | STATS aggregation BY field | SORT field | LIMIT n`

> **前提条件：** ES|QL 要求查询的索引上启用 `_source`。未启用 `_source`（例如，`"_source": { "enabled": false }`）的索引会导致 ES|QL 查询失败。
>
> **版本兼容性：** ES|QL 在 8.11（技术预览）中引入，在 8.14 中正式发布。`LOOKUP JOIN`（8.18+）、`MATCH`（8.17+）和 `INLINE STATS`（9.2+）等特性在后续版本中添加。在 8.18 之前的集群上，使用 `ENRICH` 作为 `LOOKUP JOIN` 的回退（见生成技巧）。`INLINE STATS` 和计数字段 `RATE()` 在 9.2 之前**没有**回退。有关各版本功能可用性的信息，请参阅 [参考资料/esql-version-history.md](references/esql-version-history.md)。
>
> **集群检测：** 调用 `GET /` 来确定集群类型和版本：
>
> - `build_flavor: "serverless"` — Elastic Cloud Serverless。`version.number` 跟踪正在积极开发的堆栈线（从 main 开始的下一个小版本），因此仅进行 semver 比较的客户端可能将 Serverless 视为“最新”。**不要**使用 `version.number` 来限制功能：如果 `build_flavor` 是 `"serverless"`，则假定所有正式发布和预览的 ES|QL 功能都可用。
> - `build_flavor: "default"` — 堆栈（自管理或云托管）。使用 `version.number` 检查功能可用性。
> - **快照构建** 的 `version.number` 类似于 `9.4.0-SNAPSHOT`。删除 `-SNAPSHOT` 后缀，并使用主版本号和次版本号进行版本检查。快照构建包含该版本的所有功能，可能还包含尚未发布的开发功能——如果查询因未知函数/命令而失败，可能只是尚未发布。Elastic 员工通常使用快照构建进行测试。

## 流程

1. **验证连接并检测部署类型。** 首先调用 `GET /`。这确认了连接性，并检测部署是否为 Serverless 项目（所有功能可用）或版本化集群（功能取决于版本）。`build_flavor` 字段是权威信号——如果它等于 `"serverless"`，则忽略报告的版本号并自由使用所有 ES|QL 功能。如果调用失败，请停止并引导用户查看 CLI 配置说明，而不是猜测端点或凭证。

2. **发现模式（必需——永远不要猜测索引或字段名称）。** 使用 `GET /_cat/indices`（传递模式以缩小范围）列出候选索引，然后使用 `GET /{index}/_mapping` 获取所选索引的字段类型。

   始终在生成查询之前运行模式发现。索引名称和字段名称因部署而异，无法可靠地猜测。即使听起来很常见的（例如，“日志”）也可能存在于名为 `logs-test`、`logs-app-*` 或 `application_logs` 的索引中。字段名称可能使用 ECS 点表示法（`source.ip`、`service.name`）或平面自定义名称——唯一的方法是检查。

   **优先考虑简单性：** 除非用户明确要求跨多个源获取数据，否则查询单个索引。不要使用 `COALESCE` 组合具有不同模式的索引，除非有明确要求——选择与问题最相关的单个索引。当多个索引包含类似数据时，优先选择任务最完整的模式索引。

   **检测时间序列索引。** 使用 `GET /{index}/_settings/index.mode` 检查索引模式。如果它是 `time_series`，请使用 `TS <data-stream>`（而不是 `FROM`）、`TBUCKET(interval)`（而不是 `DATE_TRUNC`），并将计数字段用 `SUM(RATE(...))` 包裹。在编写任何时间序列查询之前，请阅读 [生成技巧](references/generation-tips.md) 中的完整 TS 部分。对于 9.4+ 上的 TSDS 索引，优先使用语言发现的命令 `METRICS_INFO` 和 `TS_INFO`（两者都已正式发布）而不是检查映射——它们直接枚举指标目录和每个时间序列的维度标签，并通过 `POST /_query` 作为 ES|QL 查询运行。将 `METRICS_INFO` 视为 `metric_type`（`counter`/`gauge`/`histogram`）和 `field_type`（`histogram`、`tdigest`、`exponential_histogram` 用于分布指标）的权威信息。两者都必须遵循 `TS` 并必须先于 `STATS`/`SORT`/`LIMIT`。请参阅 [时间序列查询](references/time-series-queries.md#metric-and-time-series-discovery)：

   ```esql
   TS metrics-tsds | METRICS_INFO | SORT metric_name
   TS metrics-tsds | TS_INFO | KEEP metric_name, dimensions | SORT metric_name
   ```

3. **为任务选择合适的 ES|QL 功能。** 在编写查询之前，将用户的意图与最合适的 ES|QL 功能进行匹配。优先使用单个高级查询而不是多个基本查询。
   - "查找模式"、"分类"、"分组相似消息" → `CATEGORIZE(field)`
   - "峰值"、"低谷"、"异常"、"X 何时改变" → `CHANGE_POINT value ON key`
   - "随时间趋势"、"时间序列" → `STATS ... BY BUCKET(@timestamp, interval)` 或 `TS` 用于 TSDB
   - "PromQL"、"Prometheus 查询/仪表板/警报"、"按 (instance) sum (...)"、"标签匹配器（如 {cluster="prod"}"）→ `PROMQL` 源命令（9.4+ 预览）；请参阅 [PROMQL 命令](references/promql-command.md)。优先使用 `TS` 进行原生 ES|QL 语法。
   - "搜索"、"查找匹配文档" → `MATCH`（默认）、`QSTR`（高级布尔值）、`KQL`（Kibana 迁移）。对于内容/文档相关性搜索，请遵循 [ES|QL 搜索策略](references/esql-search-strategy.md)。
   - "计数"、"平均值"、"分解" → `STATS` 带聚合函数
   - "近似"、"估计"、"粗略数字"、"对大量数据执行快速/廉价统计" → 在 `STATS` 查询之前使用 `SET approximation=true;`（9.5+/Serverless 中正式发布，9.4 中预览）；请参阅 [查询近似](references/query-approximation.md)

4. **在生成查询之前阅读参考资料：**
   - [生成技巧](references/generation-tips.md) - 关键模式（TS/TBUCKET/RATE、每个聚合的 WHERE、LOOKUP JOIN、CIDR_MATCH）、常见模板和歧义处理
   - [时间序列查询](references/time-series-queries.md) - **在编写任何 TS 查询之前阅读**：内/外聚合模型、TBUCKET 语法、RATE 限制、直方图指标
   - [PROMQL 命令](references/promql-command.md) — **在编写任何 PROMQL 查询之前阅读**：选项、输出模式、限制以及 `PROMQL` 与 `TS` 的决策矩阵（9.4+ 预览）
   - [ES|QL 完整参考](references/esql-reference.md) - 所有命令和函数的完整语法
   - [ES|QL 搜索策略](references/esql-search-strategy.md) — 用于内容/文档相关性搜索（检索→融合→重新排序）
   - [ES|QL 搜索参考](references/esql-search.md) — 用于全文搜索函数语法（MATCH、QSTR、KQL、评分）
   - [查询近似](references/query-approximation.md) — **在使用 `SET approximation` 之前阅读**：输出列、采样/置信度级别调整、不支持的函数和模式（9.5+/Serverless 中正式发布，9.4 中预览）

5. **按照 ES|QL 语法生成查询**。优先使用回答问题的**最简单查询**——除非用户要求，否则不要添加额外的索引、字段或转换。仅在 `KEEP` 中包含直接回答问题的字段。不要添加超出用户指定范围的条件之外的其他过滤条件（例如，当用户只是说“错误”时，不要添加 `OR level == "ERROR"`）。
   - 以 `FROM index-pattern`（时间序列索引使用 `TS index-pattern`）开头
   - 添加 `WHERE` 进行过滤（9.3+ 上使用 `TRANGE` 进行时间范围过滤）
   - 使用 `EVAL` 进行计算字段
   - 使用 `STATS ... BY` 进行聚合
   - 对于时间序列指标：使用 `TS` 和 `SUM(RATE(...))` 进行计数，使用 `AVG(...)` 进行指标，标准聚合（`SUM`、`AVG`、`PERCENTILE`、… — 不是 `*_OVER_TIME`）用于直方图指标，使用 `TBUCKET(interval)` 进行时间分桶——请参阅 [生成技巧](references/generation-tips.md) 中的 TS 部分和 [直方图指标](references/time-series-queries.md#histogram-metrics)
   - 对于检测峰值、低谷或异常：在时间分桶聚合后使用 `CHANGE_POINT`
   - 根据需要添加 `SORT` 和 `LIMIT`

6. **使用 `POST /_query` 执行查询**。请求表格式（TSV）输出，以获得干净、无装饰的结果，便于阅读和后处理。

## ES|QL 快速参考

> **版本可用性：** 本节为提高可读性省略了版本注释。有关各 Elasticsearch 版本的功能可用性，请参阅 [ES|QL 版本历史](references/esql-version-history.md)。

### 基本结构

```esql
FROM index-pattern
| WHERE condition
| EVAL new_field = expression
| STATS aggregation BY grouping
| SORT field DESC
| LIMIT n
```

### 常见模式

**过滤和限制：**

```esql
FROM logs-*
| WHERE @timestamp > NOW() - 24 hours AND level == "error"
| SORT @timestamp DESC
| LIMIT 100
```

**按时间聚合：** 对于时间序列（TSDS）索引，优先使用 `TS` 与 `TRANGE` 和 `TBUCKET` 而不是 `FROM` + `DATE_TRUNC`（见下文的时间序列部分）。

```esql
TS metrics-*
| WHERE TRANGE(7 days)
| STATS avg_cpu = AVG(cpu.percent) BY bucket = TBUCKET(1 hour)
| SORT bucket DESC
```

**前 N 个带计数：**

```esql
FROM web-logs
| STATS count = COUNT(*) BY response.status_code
| SORT count DESC
| LIMIT 10
```

**文本搜索（8.17+）：** 使用 `MATCH` 作为全文搜索的默认值而不是 `LIKE`/`RLIKE`——它速度显著更快并支持相关性评分。`text` 字段的 `MATCH` 通常足够——不要在 `MATCH` 旁边添加冗余的关键字等值过滤器（例如，`category == "X"`），除非用户明确要求过滤。仅在需要高级布尔逻辑、通配符或单个表达式中进行多字段搜索时使用 `QSTR`。`MATCH` 的第一个参数必须是**一个**真实字段名——不是列出多个字段（例如 `"title,content"`）的字符串，也不是多个字段参数；使用 `MATCH(a, "q") OR MATCH(b, "q")` 组合字段。从 8.18/9.0+ 开始可用 `KQL`。对于内容/文档搜索用例，请遵循 [ES|QL 搜索策略](references/esql-search-strategy.md)。有关完整函数指南，请参阅 [ES|QL 搜索参考](references/esql-search.md)。

```esql
FROM documents METADATA _score
| WHERE MATCH(content, "search terms")
| SORT _score DESC
| LIMIT 20
```

**字符串提取：** 使用 `DISSECT` 进行基于结构化分隔符的模式（首选——生成命名字段）和 `GROK` 进行正则表达式提取。对于简单情况，使用 `SUBSTRING(s, start, len)` 进行固定位置提取、`SPLIT(s, delim)` 分割为多值、`LOCATE(substr, s)` 查找字符位置。`SPLIT` 返回多值——使用 `MV_FIRST`、`MV_LAST` 或 `MV_SLICE` 选择元素。`INSTR` 和 `STRPOS` 不存在——使用 `LOCATE`。`REGEXP_EXTRACT` 不存在——使用 `GROK`。

```esql
// 使用 DISSECT 从电子邮件中提取域名（首选——生成命名字段）
FROM customers
| DISSECT email "%{local}@%{domain}"
| STATS count = COUNT(*) BY domain

// 替代方案：使用 SPLIT 从电子邮件中提取域名
FROM customers
| EVAL domain = MV_LAST(SPLIT(email, "@"))
| STATS count = COUNT(*) BY domain

// 解析 HTTP 日志行
FROM logs-*
| DISSECT message "%{method} %{path} %{status_text}"
| KEEP @timestamp, method, path, status_text
```

**日志分类（白金许可证）：** 使用 `CATEGORIZE` 自动将日志消息聚类到模式组中。在探索或在不结构化文本中查找模式时，优先使用此方法而不是运行多个 `STATS ... BY field` 查询。

```esql
FROM logs-*
| WHERE @timestamp > NOW() - 24 hours
| STATS count = COUNT(*) BY category = CATEGORIZE(message)
| SORT count DESC
| LIMIT 20
```

**变化点检测（白金许可证）：** 使用 `CHANGE_POINT` 检测指标序列中的峰值、低谷和趋势变化。优先使用此方法而不是手动检查时间分桶计数。

```esql
FROM logs-*
| STATS c = COUNT(*) BY t = BUCKET(@timestamp, 30 seconds)
| SORT t
| CHANGE_POINT c ON t
| WHERE type IS NOT NULL
```

**时间序列指标：** 使用 `TS` 时，使用 `TRANGE` 进行时间过滤（9.3+）或完全省略——不要在 `TBUCKET` 旁边添加冗余的 `WHERE @timestamp > NOW() - ...`。`TBUCKET` 持续时间定义聚合窗口。

```esql
// 计数指标：使用 TBUCKET(duration) 的 SUM(RATE(...))
TS metrics-tsds
| WHERE TRANGE(1 hour)
| STATS SUM(RATE(requests)) BY TBUCKET(1 hour), host

// 指标：使用 AVG(...) — 无需 RATE
TS metrics-tsds
| STATS avg_cpu = AVG(cpu) BY service.name, bucket = TBUCKET(5 minutes)
| SORT bucket

// 直方图指标：标准聚合（合并）；对通配符/混合流进行转换
TS metrics-*
| STATS total_gc = SUM(jvm.gc.duration::exponential_histogram) BY TBUCKET(1 hour), service.name
```

**使用 PromQL 语法的时间序列（9.4+ 预览）：** 当用户明确要求 PromQL、引用 Prometheus 语法（`sum by (instance) (...)`、标签匹配器如 `{cluster="prod"}`）或正在迁移 Prometheus 仪表板或警报时，使用 `PROMQL` 源命令。`PROMQL` 命令接受标准 PromQL，并可选地接受 `index`、`step`、`buckets`、`start`、`end` 和 `scrape_interval` 选项，并生成其余 ES|QL 管道可以处理的表格。范围选择是可选的——如果省略，窗口为 `max(step, scrape_interval)`。否则优先使用 `TS`（9.4 中正式发布）。`PROMQL` 不支持分组修饰符、集合运算符（`or`/`and`/`unless`）或函数（如 `histogram_quantile`、`predict_linear` 和 `label_join`）——对于这些，请回退到 `TS`。有关完整参考，请参阅 [PROMQL 命令](references/promql-command.md)。

```esql
// 自适应 Kibana 查询——日期选择器驱动时间范围和步长
PROMQL index=metrics-* sum by (instance) (rate(http_requests_total))

// 命名结果，使用 ES|QL 进行后处理
PROMQL index=k8s step=1h bytes=(max by (cluster) (network.bytes_in))
| STATS max_bytes = MAX(bytes) BY cluster
| SORT cluster
```

**使用 LOOKUP JOIN 进行数据丰富：** 基本上的 `ON` 子句在两个索引中通过名称匹配字段（`LOOKUP JOIN idx ON field_name`）。当连接键在源中的名称不同时，首先使用 `RENAME` 对齐名称。9.2+ 技术预览还支持表达式谓词（`ON expr == expr`）；有关详细信息，请参阅 [ES|QL 完整参考](references/esql-reference.md)。在 `LOOKUP JOIN` 后，查找列以其**原始字段名**可用——不要使用表限定（例如，写 `threat_level`，而不是 `threat_intel.threat_level`）。**排序技巧：** 当问题要求前 N 个结果时，在 `LOOKUP JOIN` 之前使用 `SORT` 和 `LIMIT` 以减少丰富成本。对于一般列表或完整丰富，将 `LOOKUP JOIN` 放在 `FROM`/`WHERE` 之后。

```esql
// 字段名不匹配 — 在连接前使用 RENAME
FROM support_tickets
| RENAME product AS product_name
| LOOKUP JOIN knowledge_base ON product_name

// 聚合、限制，然后丰富（仅前N名）
FROM orders
| STATS total_spent = SUM(total) BY customer_id
| SORT total_spent DESC
| LIMIT 3
| LOOKUP JOIN customers_lookup ON customer_id
| KEEP name, customer_id, total_spent

// 多字段连接（9.2+）
FROM application_logs
| LOOKUP JOIN service_registry ON service_name, environment
| KEEP service_name, environment, owner_team
```

**多值字段过滤：** 使用 `MV_CONTAINS` 检查多值字段是否包含特定值。使用 `MV_COUNT` 计数。

```esql
// 根据多值成员资格过滤
FROM employees
| WHERE MV_CONTAINS(languages, "Python")

// 查找匹配多个值的项目
FROM employees
| WHERE MV_CONTAINS(languages, "Java") AND MV_CONTAINS(languages, "Python")

// 计数多值项目
FROM employees
| EVAL num_languages = MV_COUNT(languages)
| SORT num_languages DESC
```

**变化点检测（替代示例）：** 在用户询问峰值、低谷或异常时使用。需要时间分桶聚合，`SORT`，然后 `CHANGE_POINT`。

```esql
FROM logs-*
| STATS error_count = COUNT(*) BY bucket = DATE_TRUNC(1 hour, @timestamp)
| SORT bucket
| CHANGE_POINT error_count ON bucket AS type, pvalue
```

**近似 STATS（9.5+/Serverless中的GA，9.4中的预览）：** 在 `STATS` 查询前添加 `SET approximation=true;` 以通过采样和外推在大型数据集上快速获取估计值，当不需要精确值时。结果会添加 `_approximation_confidence_interval(col)` 和 `_approximation_certified(col)` 列，每个估计量都会显示这些边界 — 报告这些范围，不要将估计值呈现为精确值。`COUNT_DISTINCT`、`MIN`、`MAX`、`FIRST`、`LAST`、`TOP`（以及其他一些）**不支持**，会回退到精确执行；使用 `SAMPLE` 命令。包含2个以上 `STATS` 的管道，或使用 `TS`/`PROMQL` 源命令的也会回退。参见 [Query Approximation](references/query-approximation.md)。

```esql
SET approximation=true;
FROM web_traffic
| WHERE @timestamp >= NOW() - 1 week
| STATS total_hits = COUNT(*), avg_load_time = AVG(page_load_ms) BY country_code
| SORT total_hits DESC
| LIMIT 5
```

## 完整参考

有关完整的 ES|QL 语法，包括所有命令、函数和操作符，请阅读：

- [ES|QL 完整参考](references/esql-reference.md)
- [ES|QL 搜索参考](references/esql-search.md) - 全文搜索：MATCH、QSTR、KQL、MATCH_PHRASE、评分、语义搜索
- [ES|QL 搜索策略](references/esql-search-strategy.md) - 内容索引的相关性搜索策略：检索 → 融合 → 重新排序
- [ES|QL 版本历史](references/esql-version-history.md) - 按Elasticsearch版本的功能可用性
- [查询模式](references/query-patterns.md) - 自然语言到 ES|QL 的转换
- [生成技巧](references/generation-tips.md) - 查询生成的最佳实践
- [时间序列查询](references/time-series-queries.md) - TS命令、时间序列聚合函数、TBUCKET
- [PROMQL 命令](references/promql-command.md) - 用于TSDS索引的PromQL源命令（9.4+预览）
- [查询近似](references/query-approximation.md) - 通过采样/外推进行近似STATS（9.5+/Serverless中的GA，9.4中的预览）
- [DSL到ES|QL迁移](references/dsl-to-esql-migration.md) - 将查询DSL转换为ES|QL

## 错误处理

当查询执行失败时，请从Elasticsearch读取错误消息并修正查询。常见问题：

- 字段不存在 → 在编写查询前始终检查映射（`GET /{index}/_mapping`）并列出索引（`GET /_cat/indices`）。永远不要猜测字段或索引名 — 它们因部署而异。
- 类型不匹配 → 使用类型转换函数（TO_STRING、TO_INTEGER等）
- 语法错误 → 查看 ES|QL 参考以检查正确语法。始终使用**双引号**表示字符串，永远不要使用单引号。
- 无结果 → 检查时间范围和过滤条件
- 错误的函数名 → ES|QL使用下划线名称：`STD_DEV()` 而不是 `STDDEV()`，`MEDIAN_ABSOLUTE_DEVIATION()` 而不是 `MAD()`。使用 `CONCAT()` 表示字符串，而不是 `+`。使用 `CASE(cond, val, ...)` 而不是 `CASE WHEN...THEN...END`。
- 错误的日期部分 → `DATE_EXTRACT` 使用 ES|QL部分名称：`"hour_of_day"` 而不是 `"hour"`，`"day_of_month"` 而不是 `"day"`，`"month_of_year"` 而不是 `"month"`。使用 `DATE_DIFF("day", start, end)` 进行日期运算，而不是减法。

## 示例

每个示例都遵循以下流程：首先检查映射，然后编写最简单的正确查询。

**“过去一小时内按请求计数排名的前10个源IP”** — 通过时间窗口过滤，然后聚合和排序：

```esql
FROM logs-*
| WHERE @timestamp > NOW() - 1 hour
| STATS requests = COUNT(*) BY source.ip
| SORT requests DESC
| LIMIT 10
```

**“每个服务的平均响应时间，仅针对5xx响应”** — 在聚合前过滤错误：

```esql
FROM traces-*
| WHERE http.response.status_code >= 500
| STATS avg_ms = AVG(duration_ms) BY service.name
| SORT avg_ms DESC
```

**“过去一周每天的错误计数”** — 使用 `DATE_TRUNC` 按天分桶：

```esql
FROM logs-*
| WHERE log.level == "error" AND @timestamp > NOW() - 7 days
| STATS errors = COUNT(*) BY day = DATE_TRUNC(1 day, @timestamp)
| SORT day ASC
```

## 指南

- **查询前检查。** 在编写查询前阅读映射（`GET /{index}/_mapping`）并列出索引（`GET /_cat/indices`）— 永远不要猜测字段或索引名。
- **尽早过滤。** 将 `WHERE` 放在 `STATS` 之前，以便聚合在最小的行集上运行。
- **始终限制结果。** 将探索性查询以 `LIMIT` 结尾。
- **正确引号。** 使用双引号表示字符串字面量，永远不要使用单引号。
- **尊重版本限制。** 在使用 `LOOKUP JOIN` 或 `INLINE STATS` 等新命令前，通过 `GET /`（`build_flavor`、`version.number`）和 `references/esql-version-history.md` 确认功能可用性。
- **出错时修正，不要猜测。** 读取Elasticsearch错误，修复特定问题，然后重新运行。

## 操作

| HTTP API（缩写）                | `elastic` CLI命令                                                 |
| ----------------------------------- | --------------------------------------------------------------------- |
| `GET /`                             | `elastic es info`                                                     |
| `GET /_cat/indices`                 | `elastic es cat indices --index '<pattern>'`                          |
| `GET /{index}/_mapping`             | `elastic es indices get-mapping --index '<index>'`                    |
| `GET /{index}/_settings/index.mode` | `elastic es indices get-settings --index '<index>' --name index.mode` |
| `POST /_query`                      | `elastic es esql query --format tsv --query "<esql>"`                 |
