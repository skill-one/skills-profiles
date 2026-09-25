# 日志搜索

搜索和筛选日志以支持事件调查。工作流程与 Kibana Discover 类似：应用时间范围和范围筛选器，然后**迭代添加排除筛选器（NOT）**，直到剩余一小部分有趣的日志子集——无论是根本原因还是关键文档。可选地以上下文（该文档的前后日志）查看日志，或切换到另一个实体并开始新的搜索。仅使用 ES|QL（`POST /_query`）；不要使用查询 DSL。

## 不应使用的情况

- **指标或跟踪** — 使用专门的指标或跟踪工具。

## 参数约定

为可观察性日志搜索使用一致的名称：

| 参数     | 类型   | 描述                                                                 |
| -------- | ------ | ------------------------------------------------------------------- |
| `start`  | 字符串 | 时间范围开始（Elasticsearch 日期计算，例如 `now-1h`）                |
| `end`    | 字符串 | 时间范围结束（例如 `now`）                                           |
| `kqlFilter` | 字符串 | 用于缩小结果的 KQL 查询字符串。不是 `query`、`filter` 或 `kql`。    |
| `limit`  | 数字   | 返回的最大日志样本数（例如 10–100）                                 |
| `groupBy` | 字符串 | 可选字段，按其分组直方图（例如 `log.level`、`service.name`）         |

对于实体筛选器，使用 ECS 字段名称：`service.name`、`host.name`、`service.environment`、`kubernetes.pod.name`、`kubernetes.namespace`。仅查询 ECS 名称；OpenTelemetry 别名在可观察性索引中自动映射。

### 上下文最小化

保持上下文窗口小。在查询的示例分支中，**仅保留字段子集**；默认情况下不要返回完整文档。一个小摘要（例如 10 个文档与 KEEP）保持在 ~1000 个 token；单个完整 JSON 文档可能超过 4000 个 token。

**推荐用于示例日志的 KEEP 列表：**  
`message`、`error.message`、`service.name`、`container.name`、`host.name`、`container.id`、`agent.name`、
`kubernetes.container.name`、`kubernetes.node.name`、`kubernetes.namespace`、`kubernetes.pod.name`

**消息回退：** 如果存在，使用第一个非空的：`body.text`（OTel）、`message`、`error.message`、
`event.original`、`exception.message`、`error.exception.message`、`attributes.exception.message`（OTel）。可观察性索引模板通常会别名这些；在构建用于显示的单个“message”时，优先使用该顺序。

**限制样本：** 默认为每个查询一个小样本（10–20 个日志）。最高 500；不要在一个调用中获取数千个。每个漏斗步骤仅用于决定下一个调用——仅最终缩小的结果应保留在上下文中并总结。

## 漏斗工作流程

**你必须迭代。** 不要在单个查询后停止。使用 `NOT` 不断排除噪音，直到**剩余少于 20 个日志模式**（不同的消息类别）。**迭代时始终保留完整筛选器：** 将新的 NOT 连接到先前的 KQL；不要“缩小”或丢弃早期的排除项。

1. **第一轮——广泛：** 仅使用范围筛选器（例如 `service.name: advertService`）和时间范围运行查询。获取总数、直方图、样本日志和消息分类（常见和罕见模式）。
2. **检查：** 查看直方图（当出现峰值或下降时）、样本消息和分类模式（fork4 = 按计数排序的前端模式，fork5 = 罕见模式）。如果直方图在特定时间显示急剧峰值，则围绕该峰值缩小时间范围（t_start, t_end）以进行下一轮。从分类中计算剩余的日志模式数量；识别要排除的高容量噪音。
3. **第二轮——排除噪音：** 向 KQL 筛选器添加 `NOT` 子句，用于主导噪音模式。再次运行查询，使用**完整**筛选器（所有先前的 NOT 加上新添加的）。
4. **重复：** 不断添加 `NOT` 子句并使用完整筛选器重新运行。不要在第一轮或两轮后停止。继续进行，直到**剩余少于 20 个日志模式**（使用分类结果计算不同的消息类别）。然后剩余集足够小，可以将其解释为有趣的片段（错误、异常、根本原因）。
5. **切换（可选）：** 一旦漏斗隔离了特定实体（例如 `container.id`、`host.name`），运行另一个查询，专注于该实体，以查看其“临终遗言”或周围上下文。
6. **后退（如果需要）：** 如果漏斗没有揭示根本原因，请考虑查看日志的上下文（关键文档的前后）或不同的实体并开始新的搜索。

如果你在达到少于 20 个日志模式之前停止，你将报告噪音而不是实际故障。每个中间结果仅用于决定下一个调用；仅最终缩小的结果应保留在上下文中并总结。

## ES|QL 日志搜索模式

仅使用 ES|QL（`POST /_query`）；不要使用查询 DSL。**始终**在一个请求中返回：时间序列直方图、总数、一小部分日志样本和**消息分类**（常见和罕见模式）。直方图是主要信号——它显示峰值或下降何时发生，并指导下一个筛选器。使用 `FORK` 在单个查询中计算趋势、总数、样本和分类。

**FORK 输出解释：** 响应包含由 `_fork` 列（或等效项）标识的多个结果集。映射它们为：**fork1** = 趋势（每个时间桶的计数），**fork2** = 总数（单行），**fork3** = 样本日志，**fork4** = 常见消息模式（按计数排序的前 20 个，来自最多 10k 个日志），**fork5** = 罕见消息模式（按计数排序的后 20 个，来自最多 10k 个日志）。使用 fork1 来识别何时缩小时间范围；使用 fork2 来查看剩余的噪音量；使用 fork3 来决定下一个要添加的 NOT；使用 fork4 和 fork5 来查看剩余的不同日志模式数量并选择下一个排除项——**继续迭代，直到少于 20 个日志模式剩余**。

### KQL 指导

- 当目标文本按预期分词时，优先使用**短语查询**以实现精确性（例如 `message: "GET /health"`，`service.name: "advertService"`）。
- 如果目标不会按单个术语分词，请使用**通配符**（例如 `message: *Returning*`，`message: *WARNING*`）。**不要**在引号短语中放置通配符字符。
- 使用**显式字段 KQL**：`service.name: "payment-api"`，`message: "GET /health"`，`NOT kubernetes.namespace: "kube-system"`，`error.message: * AND NOT message: "Known benign warning"`。
- 基于 `log.level` 的筛选（例如 `log.level: error`）可能有用，但它**通常不可靠**：许多日志缺少或不正确的级别元数据（例如所有作为“info”，或级别仅在消息文本中）。在查找故障时，优先使用消息内容或 `error.message` 进行漏斗；将 `log.level` 视为提示，而不是可靠的筛选器。
- **随机全文搜索**，例如搜索“error”等单词，也**通常不可靠**：它们匹配无害的提及（例如“no error”、“error code 0”、引用该词的堆栈跟踪）。优先使用服务/实体范围和 NOT 排除实际消息模式，而不是依赖单个关键字。

### 带有直方图、样本和分类的基本日志搜索

包含消息分类，以便你可以计算不同的日志模式并迭代，直到少于 20 个剩余。使用五向 FORK：趋势、总数、样本、常见模式、罕见模式。

```json
POST /_query
{
  "query": "FROM logs-* METADATA _id, _index | WHERE @timestamp >= TO_DATETIME(\"2025-03-06T10:00:00.000Z\") AND @timestamp <= TO_DATETIME(\"2025-03-06T11:00:00.000Z\") | FORK (STATS count = COUNT(*) BY bucket = BUCKET(@timestamp, 1m) | SORT bucket) (STATS total = COUNT(*)) (SORT @timestamp DESC | LIMIT 10 | KEEP _id, _index, message, error.message, service.name, container.name, host.name, kubernetes.container.name, kubernetes.node.name, kubernetes.namespace, kubernetes.pod.name) (LIMIT 10000 | STATS COUNT(*) BY CATEGORIZE(message) | SORT `COUNT(*)` DESC | LIMIT 20) (LIMIT 10000 | STATS COUNT(*) BY CATEGORIZE(message) | SORT `COUNT(*)` ASC | LIMIT 20)"
}
```

- **fork4**（常见）：按计数排序的前 20 个消息模式，来自最多 10,000 个日志——用于添加 NOT 以排除主导噪音。
- **fork5**（罕见）：按计数排序的后 20 个消息模式——有助于在大量噪音中找到针。  
  计算跨 fork4/fork5（以及整体分类）的不同模式数量，并**继续迭代，直到少于 20 个日志模式剩余**。

调整索引模式（例如 `logs-*`、`logs-*-*`）、时间范围和桶大小（例如 `30s`、`5m`、`1h`）。保持样本 LIMIT 小（默认 10–20；最高 500）。使用 KEEP，使样本分支仅返回摘要字段，而不是完整文档。

### 添加 KQL 筛选器

使用 `KQL("...")` 缩小结果。KQL 表达式是 ES|QL 中一个双引号字符串。

**请求正文中的转义：** 查询在 JSON 中发送，因此 ES|QL 字符串中包装 KQL 表达式的双引号必须转义。使用 `\"` 转义包装 KQL 表达式的引号。如果 KQL 表达式本身包含双引号（例如短语 `message: "GET /health"`），则在 JSON 中将其作为 `\\\"` 转义，以便 KQL 解析器接收字面引号字符。

```json
POST /_query
{
  "query": "FROM logs-* METADATA _id, _index | WHERE @timestamp >= TO_DATETIME(\"2025-03-06T10:00:00.000Z\") AND @timestamp <= TO_DATETIME(\"2025-03-06T11:00:00.000Z\") | WHERE KQL(\"service.name: checkout AND log.level: error\") | FORK (STATS count = COUNT(*) BY bucket = BUCKET(@timestamp, 1m) | SORT bucket) (STATS total = COUNT(*)) (SORT @timestamp DESC | LIMIT 10 | KEEP _id, _index, message, error.message, service.name, host.name, kubernetes.pod.name) (LIMIT 10000 | STATS COUNT(*) BY CATEGORIZE(message) | SORT `COUNT(*)` DESC | LIMIT 20) (LIMIT 10000 | STATS COUNT(*) BY CATEGORIZE(message) | SORT `COUNT(*)` ASC | LIMIT 20)"
}
```

### 使用 NOT 排除噪音

通过排除已知噪音来构建漏斗。在请求正文中，将 KQL 字符串包装在 `\"...\"` 中，并将 KQL 表达式中的任何引号转义为 `\\\"`：

```json
"query": "... | WHERE KQL(\"NOT message: \\\"GET /health\\\" AND NOT kubernetes.namespace: \\\"kube-system\\\"\") | ..."
```

```json
"query": "... | WHERE KQL(\"error.message: * AND NOT message: \\\"Known benign warning\\\"\") | ..."
```

### 按维度分组的直方图

按第二个维度（例如 `log.level`、`service.name`）分解趋势，以查看哪个级别或实体驱动了峰值：

```text
STATS count = COUNT(*) BY bucket = BUCKET(@timestamp, 1m), log.level
```

在响应中使用有限的一组分组值，以避免爆炸（例如按计数排序的前 N 个，其余作为 `_other`）。

## 示例

### 服务最后一小时的日志

```json
POST /_query
{
  "query": "FROM logs-* METADATA _id, _index | WHERE @timestamp >= NOW() - 1 hour AND @timestamp <= NOW() | WHERE KQL(\"service.name: api-gateway\") | SORT @timestamp DESC | LIMIT 20"
}
```

### 带趋势和样本的错误日志

```json
POST /_query
{
  "query": "FROM logs-* METADATA _id, _index | WHERE @timestamp >= NOW() - 2 hours AND @timestamp <= NOW() | WHERE KQL(\"log.level: error\") | FORK (STATS count = COUNT(*) BY bucket = BUCKET(@timestamp, 5m) | SORT bucket) (STATS total = COUNT(*)) (SORT @timestamp DESC | LIMIT 15)"
}
```

### 迭代漏斗：NOT 和 NOT 和 NOT 直到有趣的片段

不要在第一次排除后停止。每一轮，添加更多 NOT 以排除当前的主导噪音，然后再次运行。

**第一轮：** `KQL("service.name: advertService")` → 例如 55k 个日志；样本显示“返回 N 个广告”、“WARNING: 请求...”、“收到广告请求”。

**第二轮：** 排除最大的噪音：  
`KQL("service.name: advertService AND NOT message: *Returning* AND NOT message: *WARNING*")` → 重新运行，检查新的总数和样本。

**第三轮：** 排除下一个噪音（例如请求/缓存闲聊）：  
`KQL("service.name: advertService AND NOT message: *Returning* AND NOT message: *WARNING* AND NOT message: *received ad request* AND NOT message: *Adding* AND NOT message: *Cache miss*")` →
重新运行。

**第四轮+：** 不断添加 NOT 以排除仍然主导样本的内容（使用 fork4/fork5 分类来查看模式）。继续进行，直到**少于 20 个日志模式剩余**；然后剩余的就是要报告的信号（例如“获取广告错误”、编码问题）。

转义：在 JSON 中将 KQL 字符串包装在 `\"...\"` 中；在 KQL 中使用 `\\\"` 转义引号短语。

## 指南

- **漏斗：使用 NOT 迭代。** 不要在单个广泛查询后报告发现。添加 NOT 子句以排除主导噪音，使用**完整**筛选器（保留所有先前的 NOT）重新运行，并重复进行，直到**少于 20 个日志模式剩余**（使用分类 fork4/fork5 计数）。过早停止会产生噪音，而不是信号。
- **首先查看直方图：** 使用趋势（fork1）查看峰值或下降何时发生；如有必要，在添加更多 NOT 之前缩小时间范围。
- **上下文最小化：** 在样本分支中仅保留摘要字段；默认 LIMIT 10–20，最高 500。每个漏斗步骤仅用于决定下一个调用；最终缩小的结果用于上下文和总结。
- **请求正文转义：** `query` 值是 JSON。转义 ES|QL 字符串中的双引号：`\"` 用于 KQL 包装器，`\\\"` 用于 KQL 表达式中的引号（例如短语值）。
- 构建查询时使用 Elasticsearch 日期计算来指定 `start` 和 `end`（例如 `now-1h`、`now-15m`）。
- 从时间范围中选择桶大小：目标是大约 20–50 个桶（例如 1 小时窗口 → `1m` 或 `2m`）。
- 优先使用 ECS 字段名称。在可观察性索引模板中，OTel 字段被别名为 ECS；请参阅
  [references/log-search-reference.md](references/log-search-reference.md) 以获取资源元数据字段回退（容器、主机、集群、命名空间、Pod、工作负载）。
- **`log.level`：** 基于 `log.level` 的筛选或分组可能可以，但在级别缺失或设置错误时通常不可靠；优先使用消息内容或 `error.message` 来查找故障。
- **关键字搜索：** 仅搜索“error”或“fail”等单词通常不可靠（例如“no error”、“error code 0”）；优先使用实体范围和 NOT 筛选实际消息模式。
