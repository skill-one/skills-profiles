# MongoDB 查询优化器

## 当此技能被调用时

仅当用户需要以下情况时调用：

- 查询/索引**优化**或**性能**帮助
- **为什么**查询缓慢或**如何加速**它
- 集群上的**慢查询**以及**如何优化**它们

除非用户请求优化、慢查询或索引的帮助，否则**不要**为常规查询编写调用。

## 高级工作流程

### 一般性能帮助

如果用户想要检查慢查询，或者正在寻找一般性能建议（不涉及任何特定查询）：

- 使用 MongoDB MCP 服务器 **atlas-get-performance-advisor** 工具获取慢查询日志和性能顾问输出
- 根据这些信息提出建议

如果 Atlas MCP 服务器未配置或您没有足够的信息来针对正确的集群运行 **atlas-get-performance-advisor**，请告知用户一般性能分析需要 Atlas MCP 服务器配置 API 凭据，并建议他们进行配置或询问特定查询。

### 特定查询的帮助

如果用户正在询问特定查询：

- 使用 **collection-indexes**、**explain** 和 **find** MCP 工具获取集合上的现有索引、查询的 explain() 输出和集合中的样本文档
- 使用 **atlas-get-performance-advisor MCP** 工具获取慢查询日志和性能顾问输出

然后根据收集的信息和 MongoDB 最佳实践以及参考文件中的示例提出优化建议。如果可能，请优先创建完全覆盖查询的索引。如果您无法使用 MongoDB MCP 服务器，仍然尝试提出建议。

## MCP：可用工具

**如何调用。** 使用**精确的工具名称**作为 `toolName`，并使用单个**参数对象**作为 `arguments`。不要将工具名称作为选项、查询参数或嵌套键传递；将其作为 MCP 工具名称，并将参数作为参数对象传递。完整的 MCP 服务器工具参考：[MongoDB MCP 服务器工具](https://www.mongodb.com/docs/mcp-server/tools/)。

**数据库工具**（当 MCP 集群连接工作）：

| 工具名称（精确） | 参数对象 |
| :---- | :---- |
| `collection-indexes` | `{ "database": "<db>", "collection": "<coll>" }` — 两个都是必需的字符串。 |
| `explain` | `{ "database": "<db>", "collection": "<coll>", "method": [ { "name": "find", "arguments": { "filter": {...}, "sort": {...}, "limit": N } } ], "verbosity": "executionStats" }`. `method` 是一个包含一个对象的数组：`name` 是 `"find"`、`"aggregate"` 或 `"count"`；`arguments` 包含该方法的参数（例如 find: `filter`、`sort`、`limit`；aggregate: `pipeline`；count: `query`）。可选的 `verbosity`：`"queryPlanner"`（默认）、`"executionStats"`、`"queryPlannerExtended"`、`"allPlansExecution"`。 |
| `find` |  `{ "database": "<db>", "collection": "<coll>", "filter": {...}, "projection": {...}, "sort": {...}, "limit": N }` — `database`、`collection` 和 `filter` 是必需的。可选：`projection`、`sort`、`limit`。 |

**Atlas 工具**（当配置了 Atlas API 凭据）：

| 工具名称（精确） | 参数对象 |
| :---- | :---- |
| `atlas-list-projects` | `{}` 或 `{ "orgId": "<24-character hex>" }`。返回项目及其 ID；用于获取 `projectId` 以供性能顾问使用。 |
| `atlas-get-performance-advisor` | **必需：** `"projectId"`（24 个字符的十六进制字符串）、`"clusterName"`（字符串，1–64 个字符，字母数字/下划线/短划线）。**可选：** `"operations"` — 字符串数组来自 `"suggestedIndexes"`、`"dropIndexSuggestions"`、`"slowQueryLogs"`、`"schemaSuggestions"`（仅请求您需要的）；对于 slowQueryLogs 仅：`"since"`（ISO 8601 日期时间）、`"namespaces"`（字符串数组）。 |

对于用户问题，尝试从连接字符串和与查询优化的 Atlas API 相关的信息中获取信息。

### 1\. DB 连接字符串对 MongoDB MCP 工作正常

典型流程：调用 `collection-indexes` → `explain` → `find`（样本文档）。

- **`collection-indexes`** — 使用结果的 `classicIndexes`（每个都有 `name`、`key`）来查看查询是否可以已使用现有索引。
- **`explain`** — 首先以 `"queryPlanner"` 模式运行以检查 COLLSCAN。如果查询使用索引或集合非常小，再次以 `"executionStats"`（10 秒超时）运行以获取扫描文档数与返回文档数。

### 2\. Atlas API 访问对 MongoDB MCP 工作正常

如果您需要一个项目 ID，请首先调用 `atlas-list-projects`。然后使用您需要的 `operations` 调用 `atlas-get-performance-advisor`：

| 操作值 | 使用时 |
| :---- | :---- |
| `slowQueryLogs` | 获取慢查询—**优先考虑最慢和最频繁的**。可选：`namespaces` 以范围到集合；`since` 用于时间窗口。 |
| `suggestedIndexes` | 获取集群索引建议 |
| `dropIndexSuggestions` | 用户询问要删除的内容或减少索引开销 |
| `schemaSuggestions` | 用户询问索引结构建议的同时提供架构/查询结构建议 |

不要将 MCP 工具名称作为 `operations` 值传递—`operations` 是一个单独的参数，列出了要获取的数据。

## 示例工作流程 1（帮助特定查询）

**用户：** "为什么这个查询慢？`db.orders.find({status: 'shipped', region: 'US'}).sort({date: -1})`"

**如果 MCP db 连接已配置且数据库 + 集合名称已知**，运行步骤 1–3。否则跳到步骤 4。

1. **检查现有集合索引：**
   - 使用数据库=`store`、集合=`orders` 调用 `collection-indexes`
   - 结果显示：`{_id: 1}`、`{status: 1}`、`{date: -1}`

2. **运行 explain：**
   - 使用 method=`find`、filter=`{status: 'shipped', region: 'US'}`、sort=`{date: -1}`、verbosity=`queryPlanner` 和 `executionStats` 调用 `explain`
   - 结果：使用 `{status: 1}` 索引，然后在内存中排序，`totalKeysExamined: 50000`、`nReturned: 100`

3. **运行 find：**
   - 使用 limit=1 调用 `find` 以获取样本文档以推断架构。

**如果 MCP Atlas 连接已配置**，运行步骤 4。否则跳到步骤 5。

4. **运行 atlas-get-performance-advisor：**
   - 尝试从 MCP 连接字符串获取集群名称，或询问用户 projectId/clusterName
   - 使用 slowQueryLogs 获取过去 24 小时内数据库=`store`、集合=`orders` 的慢查询日志
   - 使用 suggestedIndexes 检查查询的索引建议

5. **诊断：** 根据explain输出和慢查询日志，此查询针对 100 个文档，但扫描了 50K 个索引条目（选择性差：0.002）。内存排序增加了开销。索引不支持同时过滤和排序的字段。

6. **建议：** 根据 ESR（两个相等字段，然后排序）创建复合索引 `{status: 1, region: 1, date: -1}`。这将消除内存排序并提高选择性，通过同时过滤状态和区域。

如果未设置 MongoDB MCP 服务器，请遵循最佳索引实践。

## 示例工作流程 2（一般数据库性能帮助）

**用户：** "你能帮助我优化集群上的慢查询吗？”

1. **运行 atlas-get-performance-advisor：**  
   - 尝试从连接字符串获取集群名称并推断您在 atlas-list-projects 中需要的项目名称；如果您不确定，则询问用户集群名称和项目 ID。
   - 使用 slowQueryLogs 获取过去 24 小时内的慢查询日志  
   - 使用 suggestedIndexes  
   - 使用 dropIndexSuggestions  
   - 使用 schemaSuggestions  
2. **诊断和推荐：** 根据慢查询日志和性能顾问建议，您可以在 `db.orders` 集合上创建复合索引 `{status: 1, region: 1, date: -1}` 以优化查询，例如 `find({status: 'shipped', region: 'US'}).sort({date: -1})`

检查所有性能顾问输出以及慢查询日志。提供有关正在改进的内容及其原因的信息，并专注于具有最大潜在影响的建议（例如，影响最多查询的索引，或性能最差的查询）。

## 加载参考

在开始诊断和建议之前，加载参考文件。

始终加载：

- `references/core-indexing-principles.md`
- `references/antipattern-examples.md`

条件加载这些文件：

- **如果诊断聚合管道** → `references/aggregation-optimization.md`
- **如果诊断更改文档的查询，如 replaceOne、findOneAndUpdate 等** → `references/update-query-examples.md` 用于 oplog 高效更新和常见更新反模式

## 输出

- 保持答案简短明了：几句话关于索引和优化建议，以及背后的原因（例如，一般索引原则、在集群中观察到的慢查询日志，或在性能顾问中看到的建议）
- 专注于最高影响力的索引或优化 - 如果您遗漏了一些优化，请告知用户并在被询问时提供它们。
- 不要使用强硬的语言，例如说“您应该创建这些索引，它们将肯定会提高应用程序性能” — 解释它们是针对某些查询的建议，并说明背后的原因。
- 考虑集合上已存在的索引数量（如果已知）— 通常不应超过 20 个
- 仅当建议来自 Atlas Performance Advisor 时才建议删除索引
- 除非用户批准，否则不要通过 MCP 直接创建索引
