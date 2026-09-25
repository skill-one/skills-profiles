# ClickHouse 最佳实践

涵盖 ClickHouse 的全面指导，包括模式设计、查询优化、数据摄取和 AI 代理连接。包含 4 个主要类别（模式、查询、插入、代理）的 31 条规则，按影响优先级排序。

> **官方文档**：[ClickHouse 最佳实践](https://clickhouse.com/docs/best-practices)

## 重要提示：如何应用此技能

在回答 ClickHouse 相关问题时，请按以下优先级顺序操作：

1. **检查 `rules/` 目录中的适用规则**
2. **如果存在规则**：在回答中应用并引用规则，使用 "根据 `rule-name`..." 的方式
3. **如果不存在规则**：使用 LLM 的 ClickHouse 知识或搜索文档
4. **如果不确定**：使用网络搜索当前最佳实践
5. **始终引用来源**：规则名称、"通用 ClickHouse 指导" 或 URL

**为什么规则优先**：ClickHouse 具有特定行为（列式存储、稀疏索引、合并树机制），其中通用数据库直觉可能具有误导性。规则编码了经过验证的、特定于 ClickHouse 的指导。

---

## 代理连接与查询工作流

在查询 ClickHouse 之前，代理必须建立连接并遵循发现工作流：

1. `rules/agent-connect-mcp.md` - 连接设置（MCP + CLI）、凭证发现、输出格式选择
2. `rules/agent-discovery-schema.md` - **关键**：7 步模式发现工作流
3. `rules/agent-query-safety.md` - **关键**：LIMIT、超时、渐进式探索

**每个代理会话应遵循此顺序**：

1. **连接** — 通过 MCP 或 CLI 建立连接（参见 `agent-connect-mcp`）
2. **发现** — 数据库 → 表 → 列 + 注释 → 排序键 → 跳过索引 → 样本 → EXPLAIN
3. **计划** — 使用排序键和跳过索引知识编写高效的 WHERE 子句
4. **执行** — 使用 LIMIT 和超时运行查询
5. **恢复** — 在超时/内存错误时，缩小过滤器并重试（参见 `agent-query-safety`）

### 子代理架构说明

如果您的系统将 ClickHouse 任务分配给专门的子代理：
- **模式发现 + 查询执行**：任何模型 — 步骤是程序化的
- **EXPLAIN 分析 + 查询优化**：受益于中层推理
- **针对所有 28 条规则的模式设计审查**：受益于中层推理

---

## 审查程序

### 用于模式审查（CREATE TABLE、ALTER TABLE）

**按顺序阅读这些规则文件**：

1. `rules/schema-pk-plan-before-creation.md` - ORDER BY 是不可变的
2. `rules/schema-pk-cardinality-order.md` - 主键中列的顺序
3. `rules/schema-pk-prioritize-filters.md` - 过滤列的包含
4. `rules/schema-types-native-types.md` - 正确选择类型
5. `rules/schema-types-minimize-bitwidth.md` - 数值类型的大小
6. `rules/schema-types-lowcardinality.md` - LowCardinality 的使用
7. `rules/schema-types-avoid-nullable.md` - 可空与 DEFAULT 的区别
8. `rules/schema-partition-low-cardinality.md` - 分区数量限制
9. `rules/schema-partition-lifecycle.md` - 分区的目的

**检查**：
- [ ] PRIMARY KEY / ORDER BY 列的顺序（低到高基数）
- [ ] 数据类型与实际数据范围匹配
- [ ] 适当的应用 LowCardinality 到字符串列
- [ ] 分区键基数受限（100-1,000 个值）
- [ ] ReplacingMergeTree 使用时包含版本列

### 用于查询审查（SELECT、JOIN、聚合）

**阅读这些规则文件**：

1. `rules/query-join-choose-algorithm.md` - 算法选择
2. `rules/query-join-filter-before.md` - 预连接过滤
3. `rules/query-join-use-any.md` - ANY vs 普通 JOIN
4. `rules/query-index-skipping-indices.md` - 次要索引的使用
5. `rules/schema-pk-filter-on-orderby.md` - 过滤与 ORDER BY 的对齐

**检查**：
- [ ] 过滤器使用 ORDER BY 前缀列
- [ ] JOIN 在连接前过滤表（而不是连接后）
- [ ] 正确的 JOIN 算法适用于表大小
- [ ] 跳过索引用于非 ORDER BY 过滤列

### 用于插入策略审查（数据摄取、更新、删除）

**阅读这些规则文件**：

1. `rules/insert-batch-size.md` - 批次大小要求
2. `rules/insert-mutation-avoid-update.md` - UPDATE 的替代方案
3. `rules/insert-mutation-avoid-delete.md` - DELETE 的替代方案
4. `rules/insert-async-small-batches.md` - 异步插入的使用
5. `rules/insert-optimize-avoid-final.md` - OPTIMIZE TABLE 的风险

**检查**：
- [ ] 每个INSERT批次 10K-100K 行
- [ ] 不使用 ALTER TABLE UPDATE 进行频繁更改
- [ ] 使用 ReplacingMergeTree 或 CollapsingMergeTree 进行更新模式
- [ ] 启用异步插入用于高频小批次

---

## 输出格式

按以下结构组织您的回答：

```
## 检查的规则
- `rule-name-1` - 符合 / 发现违规
- `rule-name-2` - 符合 / 发现违规
...

## 发现

### 违规
- **`rule-name`**：问题描述
  - 当前：[代码执行的内容]
  - 需要：[它应该做什么]
  - 修复：[具体纠正]

### 符合
- `rule-name`：简要说明为什么正确

## 建议
[按优先级排序的更改列表，引用规则]
```

---

## 按优先级排序的规则类别

| 优先级 | 类别 | 影响 | 前缀 | 规则数量 |
|--------|------|------|------|----------|
| 1 | 主键选择 | 关键 | `schema-pk-` | 4 |
| 2 | 数据类型选择 | 关键 | `schema-types-` | 5 |
| 3 | JOIN 优化 | 关键 | `query-join-` | 5 |
| 4 | 插入批处理 | 关键 | `insert-batch-` | 1 |
| 5 | 避免突变 | 关键 | `insert-mutation-` | 2 |
| 6 | 分区策略 | 高 | `schema-partition-` | 4 |
| 7 | 跳过索引 | 高 | `query-index-` | 1 |
| 8 | 物化视图 | 高 | `query-mv-` | 2 |
| 9 | 异步插入 | 高 | `insert-async-` | 2 |
| 10 | 避免OPTIMIZE | 高 | `insert-optimize-` | 1 |
| 11 | JSON 使用 | 中 | `schema-json-` | 1 |
| 12 | 代理模式发现 | 关键 | `agent-discovery-` | 1 |
| 13 | 代理查询安全 | 关键 | `agent-query-` | 1 |
| 14 | 代理连接 + 格式 | 高 | `agent-connect-` | 1 |

---

## 快速参考

### 模式设计 - 主键（关键）

- `schema-pk-plan-before-creation` - 在表创建前计划 ORDER BY（不可变）
- `schema-pk-cardinality-order` - 按低到高基数排序列
- `schema-pk-prioritize-filters` - 包含频繁过滤的列
- `schema-pk-filter-on-orderby` - 查询过滤器必须使用 ORDER BY 前缀

### 模式设计 - 数据类型（关键）

- `schema-types-native-types` - 使用原生类型，而不是 String 用于所有情况
- `schema-types-minimize-bitwidth` - 使用能容纳的最小数值类型
- `schema-types-lowcardinality` - <10K 唯一字符串使用 LowCardinality
- `schema-types-enum` - 枚举用于有限值集并验证
- `schema-types-avoid-nullable` - 避免 Nullable；使用 DEFAULT 代替

### 模式设计 - 分区（高）

- `schema-partition-low-cardinality` - 保持分区数量 100-1,000
- `schema-partition-lifecycle` - 使用分区进行数据生命周期，而不是查询
- `schema-partition-query-tradeoffs` - 了解分区修剪的权衡
- `schema-partition-start-without` - 考虑从无分区开始

### 模式设计 - JSON（中）

- `schema-json-when-to-use` - JSON 用于动态模式；已知列用于类型

### 查询优化 - JOIN（关键）

- `query-join-choose-algorithm` - 根据表大小选择算法
- `query-join-use-any` - ANY JOIN 当只需要一个匹配时
- `query-join-filter-before` - 在 JOIN 前过滤表
- `query-join-consider-alternatives` - 字典/反规范化 vs JOIN
- `query-join-null-handling` - join_use_nulls=0 用于默认值

### 查询优化 - 索引（高）

- `query-index-skipping-indices` - 跳过索引用于非 ORDER BY 过滤

### 查询优化 - 物化视图（高）

- `query-mv-incremental` - 增量物化视图用于实时聚合
- `query-mv-refreshable` - 可刷新物化视图用于复杂 JOIN

### 插入策略 - 批次（关键）

- `insert-batch-size` - 每个INSERT批次 10K-100K 行

### 插入策略 - 异步（高）

- `insert-async-small-batches` - 异步插入用于高频小批次
- `insert-format-native` - 原生格式以获得最佳性能

### 插入策略 - 突变（关键）

- `insert-mutation-avoid-update` - 使用 ReplacingMergeTree 而不是 ALTER UPDATE
- `insert-mutation-avoid-delete` - 轻量级 DELETE 或 DROP PARTITION

### 插入策略 - 优化（高）

- `insert-optimize-avoid-final` - 让后台合并工作

### 代理集成 - 发现（关键）

- `agent-discovery-schema` - 查询前始终发现模式

### 代理集成 - 安全（关键）

- `agent-query-safety` - LIMIT、超时、渐进式探索

### 代理集成 - 连接 + 格式（高）

- `agent-connect-mcp` - MCP + CLI 设置、凭证发现、输出格式选择

---

## 应用时机

当您遇到以下情况时，此技能将激活：

- AI 代理连接到 ClickHouse（MCP、CLI、HTTP）
- ClickHouse 的代理工作流设计
- 模式发现或探索请求

- `CREATE TABLE` 语句
- `ALTER TABLE` 修改
- `ORDER BY` 或 `PRIMARY KEY` 讨论
- 数据类型选择问题
- 慢查询故障排除
- JOIN 优化请求
- 数据摄取管道设计
- 更新/删除策略问题
- ReplacingMergeTree 或其他专用引擎的使用
- 分区策略决策

---

## 规则文件结构

`rules/` 中的每个规则文件包含：

- **YAML 前置文本**：标题、影响级别、标签
- **简要说明**：此规则为何重要
- **错误示例**：反模式及说明
- **正确示例**：最佳实践及说明
- **附加上下文**：权衡、何时应用、参考

---

## 完整编译文档

包含所有规则内联展开的完整指南：`AGENTS.md`

当您需要快速检查多个规则而不读取单个文件时，使用 `AGENTS.md`。
