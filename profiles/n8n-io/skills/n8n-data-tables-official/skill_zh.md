# n8n 数据表

数据表是n8n的**内置表格存储**：n8n实例中的真实表格，包含列、类型、行，通过`dataTable`节点和数据表MCP工具进行CRUD操作。

用于本地持久化状态：查找表、最近事件、会话级库存、计数器、幂等性跟踪、行级逻辑或外部可见性时的去重状态（纯粹的"我是否见过这个值?"去重应属于`Remove Duplicates`节点）。适用于小到中等容量（几万行没问题，几百万行应使用真实数据库）。

## 必须遵守的规则

1. **系统管理的列 + 外部ID。** 每个表中自动存在三列：`id`（bigserial）、`createdAt`、`updatedAt`。不要在`create_data_table`中声明它们（会导致错误或遮蔽系统列）。不要在插入时写入它们。对于来自外部的域标识符（arxivId、stripeCustomerId、requestId），添加单独的列，并在该列上键控去重/查找。
2. **列中仅使用基本类型，嵌套数据使用`string` + `_object`后缀。** 不存在JSON/对象/数组列类型。对于嵌套数据（数组、解析对象），使用带有`JSON.stringify(...)`写入和`JSON.parse(...)`读取的`string`列。标记列为`_object`（例如，`keyInsights_object`）。后缀是告诉读取者进行解析的契约。参见`references/SCHEMA_DESIGN.md`。

## 强制性默认设置

- **不要在数据表节点之前添加Set节点来修改字段。** 数据表节点的每列表达式插槽与Set字段的威力一样强大，因此Set节点所做的零工是数据表节点自己可以完成的。（在`n8n-expressions-official`中也提到了这种Set节点的反模式。）
- **匹配n8n的列命名风格：camelCase。** 自动管理的列是camelCase（`createdAt`、`updatedAt`），因此当它们匹配时，用户列更清晰：`arxivId`、`paperId`、`taxRate`。同一查询中混合大小写（`createdAt >= ... AND arxiv_id eq ...`）读起来像拼写错误。保持字符串化二进制列的`_object`后缀（`keyInsights_object`），下划线是契约标记，不是大小写。
<!-- 临时：当数据表节点的怪异问题修复时删除 -->
- **在创建/更新后通过`get_workflow_details`验证`columns`参数。** UI在手动映射模式下有一个显示怪异（"当前没有项目存在"而没有实际数据丢失"）。检查JSON以确认已持久化内容。
- **当形状需要时，关系设计有效。** 对于真实的父子数据（论文→摘要，客户→订单），通过`id`引用父项，明确命名列（`paperId`、`customerId`），并在工作流逻辑中强制完整性。不要在扁平使用场景（去重、查找、审计）中强制使用，在这些场景中没有关系需要建模。
- **存储格式不是接口格式。** 在从子工作流返回之前解析`_object`字段。调用者不应接收需要自己解析的字符串化外壳。参见`references/SCHEMA_DESIGN.md` "存储格式≠接口格式"。
- **默认列**

每个数据表都有这些列，无论你是否声明它们：

| 列 | 类型 | 行为 |
|---|---|---|
| `id` | bigserial / number | 自动递增的主键。n8n在插入时分配，并且你不能写入它。返回在插入响应中。 |
| `createdAt` | timestamp | 在插入时自动设置。 |
| `updatedAt` | timestamp | 在每次更新时自动刷新。 |

实际上：

- **不要在`create_data_table`中声明它们**。它们已经存在。
- **在查询中使用它们**，而无需自己的时间戳列。"今天创建的"：`createdAt >= '<今天ISO>'`。"自上次同步以来更新"：`updatedAt >= $('Last Sync').item.json.timestamp`。
- **不要将它们用作跨系统标识符**。自动`id`是内部的，并且在表重新创建或实例迁移时会重置。对于域标识符，使用自己的列。

## 当形状需要时，关系设计

数据表不强制执行外键，但您仍然可以在表之间建模真实的父子数据。诀窍：完整性是您的责任，而不是n8n的。

- **通过`id`引用父行**。子表在列中包含父项的`id`。
- **在列名中记录引用**。`paperId`、`customerId`、`eventId`使关系显而易见。
- **在工作流逻辑中强制完整性**。在插入子项之前查找父项。在删除父项之前，决定子项会发生什么（删除、成为孤儿、存档）。n8n不会级联。
- **注意过时的引用**。指向已删除父项的子项是沉默的错误。软删除，或运行清理工作流。

对于复杂的关系结构（3个或更多表带连接、事务性写入），选择一个真实的SQL数据库。

## 操作：哪种操作用于什么

| 操作 | 何时使用 |
|---|---|
| `insert` | 总是添加。新行，n8n分配`id`。 |
| `upsert` | "如果新则添加，如果存在则更新。"需要一个`matchType`和过滤器来决定是否存在。 |
| `update` | "修改匹配此过滤器的行。"如果没有匹配项，则不会插入。 |
| `get` | 查找匹配过滤器的行（返回0+）。支持`orderBy`、`limit`、`returnAll`。 |
| `deleteRows` | 删除匹配过滤器的行。 |
| `rowExists` / `rowNotExists` | 对传入项进行布尔式过滤。常用于去重分支。 |

有关完整操作表面（过滤语法、matchType、排序模式），请参阅`references/OPERATIONS.md`。

<!-- 临时：当数据表节点的怪异问题修复时删除 -->
## "当前没有项目存在"的UI怪异

当SDK保存手动模式列映射（`mappingMode: 'defineBelow'`）时，n8n UI的"要插入的值"窗格可以渲染为空（"当前没有项目存在"），即使运行时正确持久化数据。如果用户报告插入节点"看起来损坏"或"没有字段"，告诉他们：这是一个UI显示问题，按列参数上的重新加载（刷新）按钮，它会重新填充架构和映射。没有数据丢失，随时可以这样做。

<!-- 临时：SDK保存的defineBelow列映射在n8n UI中可以渲染为"当前没有项目存在"，直到用户点击列参数上的重新加载按钮。运行时持久化不受影响。删除此部分，一旦n8n在工作流加载时自动刷新架构。 -->

## 常见模式

### 通过外部ID去重

默认使用`Remove Duplicates`节点（"在先前执行中看到的项目"模式）进行纯粹的"我是否见过这个值?"去重。这是一个单节点解决方案，具有内部存储，无需维护架构。数据表只有在去重状态需要存在于真实表中有理由时才值得使用：

- **您将查询或检查去重状态**。仪表板、审计、"我们上周处理了什么?"
- **在命中时进行行级逻辑**。按类别的TTL（"类别A 30天后过期，类别B 7天后过期"）、基于存储状态的条件重新处理、基于状态列的分支。
- **按租户或按用户命名空间**，`Remove Duplicates`历史存储无法表达。

当达到这些标准时：

```
[源：{ arxivId, ... }]
   ↓
[数据表获取：filter arxivId eq $json.arxivId, limit 1]
   ↓
[IF：结果包含项目?]
   ├── 是 → [跳过，或从存储的行应用行级逻辑]
   └── 否 → [处理] → [数据表插入：{ arxivId, ...rest }]
```

有关完整模式表面（upsert、rowNotExists、Get+IF、幂等性键），请参阅`references/DEDUP_PATTERNS.md`。

### 查找表

稳定的参考数据（国家→税率，计划→功能标志）。通过n8n UI编辑，并在执行时通过工作流读取：

```
[数据表获取：filter country eq $json.country, limit 1]
   ↓
[使用查找的行的taxRate等]
```

### 最近事件/审计跟踪

追加插入，稍后查询：

```
[工作流事件] → [数据表插入：{ userId, eventType, payloadSummary }]
```

`createdAt`使"过去一小时的最近事件"变得简单，无需自己的时间戳。

## 参考文件

| 文件 | 何时阅读 |
|---|---|
| `references/SCHEMA_DESIGN.md` | 设计列/类型，无外键关系模式，映射模式（`defineBelow` vs `autoMapInputData`），何时数据表是错误工具 |
| `references/OPERATIONS.md` | 操作表面（insert/upsert/update/get/delete/rowExists），过滤语法，matchType，orderBy |
| `references/DEDUP_PATTERNS.md` | 幂等性键，RemoveDuplicates节点与数据表去重，搜索后插入 vs upsert |

有关表达式规范（`$json` vs `$('节点名称').item.json`，Set节点的反模式），请参阅`n8n-expressions-official`。有关合并收敛和相同形状分支，请参阅`n8n-node-configuration-official` `references/MERGE_NODE.md`。

## 反模式

| 反模式 | 出现什么问题 | 修复 |
|---|---|---|
| Set节点在Insert上游"以塑造输入" | 额外的节点无事可做，经典的Set反模式，字段形状在添加列时漂移 | 直接在Insert节点的每列插槽中映射，或者重命名上游字段以启用自动映射 |
| 在`create_data_table`中声明`id`、`createdAt`、`updatedAt` | 错误，或者用用户列遮蔽自动管理的列 | 不要声明它们，它们已经存在 |
| 在数据表中存储应用程序关键数据 | 如果n8n崩溃，您将失去访问权限 | 使用真实数据库存储您不会丢失的数据 |
| 在数据表中存储跨应用的系统记录 | 难以与非n8n消费者共享，查询表面尴尬 | 使用真实数据库 |
| 将自动`id`视为稳定的跨实例标识符 | 如果表被重新创建，则会重置，不可移植 | 使用域ID列（`arxivId`、`requestId`）进行跨系统引用 |
| 外键级联假设 | n8n不会级联，删除的父项会留下孤儿子项 | 软删除，或运行维护引用完整性的清理工作流 |
| 引用立即前一个节点时中间的剥离json | 插入会为"应该存在"的字段静默写入NULL | 通过名称引用稳定的上游节点，或使用NoOp/Merge收敛锚点（参见`n8n-expressions-official`和`n8n-node-configuration-official` `references/MERGE_NODE.md`） |
| 手动映射模式 + Set节点以修复"当前没有项目存在" | 什么也修复不了，那是一个UI怪异，您添加了一个无用的Set节点 | 通过`get_workflow_details`验证`columns.value`是否包含您的映射，运行时是好的。告诉用户按列参数上的重新加载按钮以使UI渲染字段。 |

## 发布前的验证

创建或更新使用数据表的工作流后：

1. `validate_workflow`通过。
2. `get_workflow_details`并检查每个数据表节点的`columns`。`value`和（对于手动映射）`schema`都填充。
3. `test_workflow`使用固定数据。插入响应应包括`id`、`createdAt`、`updatedAt`。
4. 通过UI或后续获取检查实际数据表内容以确认列不是静默NULL。

特别是第一次将新的Insert连接时步骤4。上下文剥离中间件+手动映射+UI怪异会静默产生NULL列。
