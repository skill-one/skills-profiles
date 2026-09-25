# 查询洞察与标签

## 目的

使用 PlanetScale Insights 理解查询行为，然后推荐与 SQLCommenter 兼容的标签，以便未来进行诊断和流量控制。未经批准，不得更改数据库设置或仓库代码。

## 需要检查的内容

### 查询行为

针对选定的数据库和分支，检查以下内容：

- 按总时间排序的前端查询。
- 按每次执行时间排序的前端查询。
- 按读取行数排序的前端查询。
- 按执行次数排序的前端查询。
- 对于 Postgres，按 CPU 使用率排序的前端查询（在 Insights API 上使用 `sort=cpuTime` 或 `sort=percentCpuTime`）。
- 出现错误的查询。
- 值得注意的查询和活跃的异常。
- 受最近部署影响的查询模式。
- 附属于模式建议的查询模式。
- 对于分片的 Vitess 数据库，每个查询模式使用的 vindex：使用相关 vindex 的流量百分比以及随时间变化的 vindex 使用趋势。API 暴露每个模式的 `index_usages` 和 `routing_index_usages`；从仪表板的 Vindexes 选项卡或通过比较 API 窗口获取趋势。将缺失或下降的相关 vindex 使用视为索引或路由调查的输入，而不是新索引所需的证明。

### Insights API 界面

Insights 是一个公共 API：`organizations/{org}/databases/{db}/branches/{branch}` 下的只读 GET 端点，由服务令牌或具有 `read_databases`/`read_database` 权限的 OAuth 令牌授权。

- `/insights` — 在请求的窗口期内按查询模式聚合的统计数据。使用 `from`/`to`（ISO 8601）或 `period`（例如 `1h`，`24h`）设置窗口；使用 `q` 搜索 SQL 模式；使用 `sort` 和 `dir` 在服务器端排序——排序键包括 `count`，`errorCount`，`rowsRead`，`totalTime`，`cpuTime`，`ioTime`，`percentTime`，`percentCpuTime`，`p50Latency`，`p99Latency`，`maxLatency`，`egressBytes` 以及 `trafficControlWarnings`/`trafficControlThrottled` 系列。使用 `tablet_type`（`primary`，`replica`，`rdonly`）和 `type`（`SELECT`，`INSERT`，`UPDATE`，`DELETE`）进行过滤；使用 `fields` 修剪响应；使用 `page`/`per_page` 进行分页。
- `/insights/{fingerprint}` — 模式（时间戳、持续时间、行数、用户名、客户端地址、错误消息）的单独收集执行。无论原始查询收集是否可用，都可以使用；原始收集会向这些记录添加字面参数值。
  `/insights/{fingerprint}/summary` 返回单个模式的聚合；`/insights/queries/{id}` 获取一次执行。
- `/insights/errors` — 错误指纹及其计数和消息（使用 `q` 搜索错误消息；按 `count`，`lastRun`，`totalTime` 或 `timePerQuery` 排序）。`/insights/errors/{fingerprint}` 列出导致一个错误指纹的失败执行。
- `/insights/anomalies` 和 `/insights/anomalies/{id}` — 异常窗口，其中包含每个查询的相关系数，用于识别哪些模式与异常一起移动。
- `/insights/tags` — 观察到的标签键及其值（`values_limit`，`literal_values_only` 和 `fingerprint`/`keyspace` 过滤器）；`/insights/tags/{tag}` 用于单个键。`/insights/tags/summaries` 通过 `tags` 参数将完整统计模式按一个或多个标签键分组——使用它来将负载归因于路由、作业或功能，而无需客户端聚合。
- `/insights/{fingerprint}/traffic/budgets` — 影响指纹的流量控制预算和规则（仅限 Postgres）。

聚合覆盖请求的窗口。持续时间字段使用名称如 `sum_total_duration_millis`，以及显式的窗口百分比字段（`sum_total_duration_percent`）；两者对于请求的窗口都是可靠的。

响应模式在引擎之间共享，但某些字段是引擎特定的：CPU/IO 持续时间和块缓存统计信息（`sum_cpu_duration_millis`，`blocks_read`，`block_cache_hit_ratio`，…）为 Postgres 填充；分片查询、键空间、`tablet_type` 和路由索引（vindex）使用情况为 Vitess 填充。

### 标签覆盖范围

针对每个昂贵或异常的查询，确定：

- 它是否被标记？
- 它由哪个服务生成？
- 它由哪个路由、作业、控制器或操作生成？
- 它由哪个部署 SHA 生成？
- 标签基数是否安全？
- 标签在框架和语言之间是否一致？
- 使用标签 API 来回答这些问题：`/insights/tags` 显示哪些键和值存在，以及 `/insights/tags/summaries?tags=...` 按标签值归因负载。在 Vitess 仪表板中，使用 `tag:key:value` 过滤查询表格并深入查询详细信息以查看单个执行上的标签。内置查询元数据和 SQLCommenter 标签都是有效的归因来源。

### 原始查询收集

检查是否启用原始查询/完整查询收集。在 Postgres 上，有效状态是 `pginsights.raw_queries` 集群参数（每个分支，仪表板扩展选项卡，默认为 `false`）；数据库 API 对象的 `insights_raw_queries` 字段是单独的界面。当两者不一致时，报告集群参数为有效状态，不要描述差异作为不一致。在 Vitess 上没有集群参数；数据库 API 的 `insights_raw_queries` 字段是有效状态。

将其报告为能力状态，而不是风险状态。原始查询收集记录每次执行的字面参数值，而模式级 Insights 数据不提供这些信息。它是隔离模式特定病理调用的机制。执行级记录可以从 `/insights/{fingerprint}` 获取，无论是否启用原始收集；原始收集会向这些记录添加字面参数值。

当禁用时，发现是一个能力差距：识别此评估中模式级数据不足的查询模式（指纹内未解释的延迟变化、租户或参数依赖行为），并说明原始收集将解决这些问题。一次说明操作属性作为事实：字面值对可观察性管道可见。如果客户的处理数据需求限制这一点，范围启用（事件窗口、定义保留）和禁用收集都是有效的结果——记录理由而不是任何一方的默认判断。

标签和原始查询收集是互补的工具：标签将模式归因于代码路径；原始查询收集识别特定的调用。评估应评估两者。

## SQLCommenter 标签模式

推荐以下基本标签集：

- `application`：稳定的AppName。
- `service`：服务或进程名。
- `environment`：生产、预发布、开发。
- `route`：规范化路由模板，例如 `/accounts/:id/orders`，而不是 `/accounts/123/orders`。
- `controller`：适用时的框架控制器名。
- `action`：适用时的框架操作名。
- `job`：后台作业类或工作名。
- `queue`：后台队列。
- `feature`：用于流量类的有界功能名，如导出、报告、搜索、计费、结账。
- `release_sha`：短的 git SHA 或部署标识符。
- `source`：应用、工作、脚本、代理、mcp、bi、集成。
- `tenant_tier`：免费、专业、企业、内部，仅当有界时。

默认情况下不推荐这些标签：

- `user_id`
- `request_id`
- `tenant_id`
- `email`
- `session_id`
- 原始 URL
- 无界的 GraphQL 操作文本
- 访问令牌
- 密钥

如果客户需要租户级隔离，建议首先使用有界抽象，例如租户层、单元、分片或客户类。租户 ID 仅在经过基数和隐私审查后获得明确批准时才可接受。

## 基数规则

当标签不安全时：

- 值无界。
- 值包括 ID、UUID、电子邮件、缩写或原始路径。
- 同一查询模式发出许多唯一的标签组合。
- 标签会使 Insights 或流量控制聚合变得嘈杂。

建议在应用边界进行规范化。

## 分析输出

针对每个前端查询模式，生成：

- 指纹或规范化查询。
- 当前指标。
- 当前标签。
- 缺失标签。
- 在应用代码中的可能来源。
- 是否是模式建议候选。
- 是否是流量控制候选。
- 是否是应用优化候选。

## 推荐类别

### 添加标签

当查询归因较弱时，推荐 SQLCommenter 仪器。

### 改进标签规范化

推荐用有界值替换高基数标签。

### 添加流量控制警告预算

仅限 Postgres，推荐 `warn` 模式预算，用于昂贵但重要的路由、作业、分析、导出或第三方集成。

### 添加模式建议工作流

对于 Vitess，推荐将开放的模式建议转换为分支/部署请求工作。对于 Postgres，推荐将其转换为非生产分支的已审查迁移。

### 修复代码路径

当昂贵查询由 N+1、缺少分页、意外 eager load、无界导出、广泛搜索或轮询引起时，推荐仓库 PR。

## 安全规则

不要：

- 启用原始查询收集。
- 向代码添加标签。
- 更改流量控制预算。
- 应用模式建议。
- 在昂贵查询上运行生产 EXPLAIN ANALYZE。

未经明确批准。

## 输出

返回：

- 查询风险表。
- 标签覆盖表。
- 坏/高基数标签表。
- 为此应用推荐的标签模式。
- 候选流量控制切片。
- 候选模式和代码更改。
- 需要批准的提议更改。

以：

“未应用 Insights、标签、仓库或流量控制更改。” 结尾。
