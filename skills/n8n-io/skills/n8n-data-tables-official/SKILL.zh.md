---
name: n8n-data-tables-official
description: 在处理n8n的内置数据表、设计模式、插入/更新/合并插入行、去重或查询时使用。当触发器为"数据表"、"data table"、"n8n-nodes-base.dataTable"、"dedup"、"idempotency"、"lookup"、"持久状态"、"跨执行存储"或n8n内部任何模式设计讨论时使用。
---

# n8n 数据表

数据表是 n8n 的**内置表格存储**：n8n 实例中的真实表格，包含列、类型、行，通过 `dataTable` 节点和数据表 MCP 工具进行 CRUD 操作。

用于本地持久化状态：查找表、最近事件、会话级库存、计数器、幂等性跟踪、在存在行级逻辑或外部可见性时去重状态（纯“我是否见过这个值？”去重属于 `Remove Duplicates` 节点）。小到中等容量（几万行没问题，几百万行应使用真实数据库）。

## 必须遵守的规则

1. **系统管理的列 + 外部 ID。** 每个表自动存在三列：`id` (bigserial)、`createdAt`、`updatedAt`。不要在 `create_data_table` 中声明它们（会导致错误或遮蔽系统列）。不要在插入时写入它们。对于来自外部的域标识符（arxivId、stripeCustomerId、requestId），添加一个单独的列，并在该列上键去重/查找。
2. **列中仅使用基本类型，嵌套数据使用 `string` + `_object` 后缀。** 不存在 JSON/对象/数组列类型。对于嵌套数据（数组、解析对象），使用 `string` 列，并在写入时使用 `JSON.stringify(...)`，在读取时使用 `JSON.parse(...)`。用 `_object` 标记列（例如，`keyInsights_object`）。后缀是告诉读取者进行解析的契约。参见 `references/SCHEMA_DESIGN.md`。

## 强制性默认值

- **不要在数据表节点之前添加 Set 节点来修改字段。** 数据表节点的每列表达式插槽与 Set 字段一样强大，因此 Set 节点在做零工。 （在 `n8n-expressions-official` 中也提到了相同的 Set 节点反模式。）
- **匹配 n8n 的列大小写：camelCase。** 自动管理的列是 camelCase (`createdAt`、`updatedAt`)，因此当它们匹配时，用户列更清晰：`arxivId`、`paperId`、`taxRate`。同一查询中混合大小写（`createdAt >= ... AND arxiv_id eq ...`）读作拼写错误。保持字符串化二进制列的 `_object` 后缀（`keyInsights_object`），下划线是契约标记，不是大小写。
<!-- 临时：在数据表节点怪异问题修复后删除 -->
- **在创建/更新后通过 `get_workflow_details` 验证 `columns` 参数。** UI 在手动映射模式下有一个显示怪异（“当前没有项目存在”而没有实际数据丢失）。检查 JSON 确认已持久化内容。
- **当形状需要时，关系设计有效。** 对于真正的父子数据（论文 → 摘要、客户 → 订单），通过 `id` 引用父项，显式命名列（`paperId`、`customerId`），并在工作流逻辑中强制完整性。不要在扁平使用场景（去重、查找、审计）中强制使用，其中没有关系可以建模。
- **存储格式不是接口格式。** 在从子工作流返回之前解析 `_object` 字段。调用者不应接收需要自己解析的字符串化外壳。参见 `references/SCHEMA_DESIGN.md` “存储格式 ≠ 接口格式”。

## 默认列

无论你是否声明，每个数据表都有这些列：

| 列 | 类型 | 行为 |
|---|---|---|
| `id` | bigserial / number | 自动递增的主键。n8n 在插入时分配，并且你不能写入它。返回在插入响应中。 |
| `createdAt` | timestamp | 在插入时自动设置。 |
| `updatedAt` | timestamp | 在每次更新时自动刷新。 |

实际上：

- **不要在 `create_data_table` 中声明它们**。它们已经存在。
- **在查询中使用它们**，而无需自己的时间戳列。“今天创建”：`createdAt >= '<今天 ISO>'`。“自上次同步以来更新”：`updatedAt >= $('Last Sync').item.json.timestamp`。
- **不要将它们用作跨系统标识符。** 自动 `id` 是内部的，并且在表重新创建或实例迁移时会重置。对于域标识符，使用自己的列。

## 当形状需要时，关系设计

数据表不强制外键，但您仍然可以在表之间建模父子数据，当数据确实具有该形状时。注意：完整性是您的责任，而不是 n8n 的。

- **通过 `id` 引用父行。** 子表在列中包含父项的 `id`。
- **在列名中记录引用。** `paperId`、`customerId`、`eventId` 使关系显而易见。
- **在工作流逻辑中强制完整性。** 在插入子项之前查找父项。在删除父项之前，决定子项会发生什么（删除、成为孤儿、存档）。n8n 不会级联。
- **注意过时的引用。** 指向已删除父项的子项是沉默的错误。软删除，或运行清理工作流。

对于复杂的关系结构（3+ 表格带连接、事务性写入），使用实际的 SQL 数据库。

## 操作：哪种用于什么

| 操作 | 何时使用 |
|---|---|
| `insert` | 总是添加。新行，n8n 分配 `id`。 |
| `upsert` | “如果新则添加，如果存在则更新。” 需要一个 `matchType` 和过滤器来决定存在性。 |
| `update` | “修改匹配此过滤器的行。” 如果没有匹配项，则不会插入。 |
| `get` | 获取匹配过滤器的行（返回 0+）。支持 `orderBy`、`limit`、`returnAll`。 |
| `deleteRows` | 删除匹配过滤器的行。 |
| `rowExists` / `rowNotExists` | 对传入项进行布尔式过滤器。常用于去重分支。 |

有关完整操作表面（过滤语法、matchType、排序模式），参见 `references/OPERATIONS.md`。

<!-- 临时：在数据表节点怪异问题修复后删除 -->
## “当前没有项目存在”的 UI 怪异

当 SDK 保存手动模式列映射（`mappingMode: 'defineBelow'`）时，n8n UI 的“要插入的值”窗格可能渲染为空（“当前没有项目存在”），即使运行时正确持久化数据。如果用户报告插入节点“看起来损坏”或“没有字段”，告诉他们：这是一个 UI 显示问题，按列参数上的重新加载（刷新）按钮，它会重新填充架构和映射。没有数据丢失，随时可以这样做。

<!-- 临时：SDK 保存的 defineBelow 列映射在 n8n UI 中可能渲染为“当前没有项目存在”，直到用户点击列参数上的重新加载按钮。运行时持久化不受影响。删除此部分，一旦 n8n 在工作流加载时自动刷新架构。 -->

## 常见模式

### 通过外部 ID 去重

默认使用 `Remove Duplicates` 节点（“在先前执行中看到的项目”模式）进行纯“我是否见过这个值？”去重。这是一个单节点解决方案，具有内部存储，无需维护架构。数据表只有在去重状态需要存在于真实表中时才值得使用：

- **您将查询或检查去重状态。** 仪表板、审计、“我们上周处理了什么？”
- **在命中上进行行级逻辑。** 按类别的 TTL（“A 类别 30 天后过期，B 类别 7 天后过期”）、基于存储状态的条件重新处理、基于状态列的分支。
- **按租户或按用户命名空间**，`Remove Duplicates` 历史存储无法表达。

当满足这些条件时：

```
[源：{ arxivId, ... }]
   ↓
[数据表获取：filter arxivId eq $json.arxivId, limit 1]
   ↓
[IF：结果包含项目？]
   ├── 是 → [跳过，或应用存储行的行级逻辑]
   └── 否 → [处理] → [数据表插入：{ arxivId, ...rest }]
```

有关完整模式表面（upsert、rowNotExists、Get+IF、幂等性键），参见 `references/DEDUP_PATTERNS.md`。

### 查找表

稳定的参考数据（国家 → 税率、计划 → 功能标志）。通过 n8n UI 编辑，并在执行时通过工作流读取：

```
[数据表获取：filter country eq $json.country, limit 1]
   ↓
[使用查找行的 taxRate、等。]
```

### 最近事件 / 审计跟踪

追加插入，稍后查询：

```
[工作流事件] → [数据表插入：{ userId, eventType, payloadSummary }]
```

`createdAt` 使“过去一小时内的最近事件”变得简单，无需自己的时间戳。

## 参考文件

| 文件 | 何时阅读 |
|---|---|
| `references/SCHEMA_DESIGN.md` | 设计列/类型、无外键的关系模式、映射模式（`defineBelow` vs `autoMapInputData`）、何时数据表是错误工具 |
| `references/OPERATIONS.md` | 操作表面（insert/upsert/update/get/delete/rowExists）、过滤语法、matchType、orderBy |
| `references/DEDUP_PATTERNS.md` | 幂等性键、RemoveDuplicates 节点与数据表去重、搜索后插入 vs upsert |

有关表达式规范（`$json` vs `$('Node Name').item.json`、Set 节点反模式），参见 `n8n-expressions-official`。对于 Merge 收敛和相同形状的分支，参见 `n8n-node-configuration-official` `references/MERGE_NODE.md`。

## 反模式

| 反模式 | 出现什么问题 | 修复 |
|---|---|---|
| Set 节点在 Insert 上游“以塑造输入” | 额外节点无意义，经典的 Set 反模式，字段形状在添加列时漂移 | 直接在 Insert 节点的每列插槽中映射，或重命名上游字段以启用自动映射 |
| 在 `create_data_table` 中声明 `id`、`createdAt`、`updatedAt` | 错误，或用用户列遮蔽系统列，用户列不会自动更新 | 不要声明它们，它们已经存在 |
| 在数据表中存储应用程序关键数据 | 如果 n8n 出现问题，您将失去访问权限 | 使用真实数据库存储您不会丢失的数据 |
| 在数据表中存储跨应用的系统记录 | 难以与非 n8n 消费者共享，查询表面尴尬 | 使用真实数据库 |
| 将自动 `id` 视为稳定的跨实例标识符 | 如果表被重新创建，则会重置，不可移植 | 使用域 ID 列（`arxivId`、`requestId`）进行跨系统引用 |
| 外键级联假设 | n8n 不级联，删除父项会留下孤儿子项 | 软删除，或运行维护引用完整性的清理工作流 |
| 引用立即前一个节点时中间剥离了 json | 插入会为“应该存在”的字段静默写入 NULL | 通过名称引用稳定的上游节点，或使用 NoOp/Merge 收敛锚点（参见 `n8n-expressions-official` 和 `n8n-node-configuration-official` `references/MERGE_NODE.md`） |
| 手动映射模式 + Set 节点以修复“当前没有项目存在” | 什么都没修复，那是一个 UI 怪异，您添加了一个无用的 Set 节点 | 通过 `get_workflow_details` 验证 `columns.value` 是否包含您的映射，运行时是正常的。告诉用户按列参数上的重新加载按钮以使 UI 渲染字段。 |

## 发布前的验证

创建或更新使用数据表的工作流后：

1. `validate_workflow` 通过。
2. `get_workflow_details` 并检查每个数据表节点的 `columns`。`value` 和（对于手动映射）`schema` 都已填充。
3. `test_workflow` 使用固定数据。插入响应应包括 `id`、`createdAt`、`updatedAt`。
4. 通过 UI 或后续获取检查实际数据表内容以确认列不是静默 NULL。

特别是第一次将新的 Insert 线路连接时步骤 4。上下文剥离中间件 + 手动映射 + UI 怪异会静默产生 NULL 列。
