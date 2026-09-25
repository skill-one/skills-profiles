# 数据管道技能

在配置 Coralogix 如何处理、丰富和转换数据时使用此技能。它涵盖了解析规则（从原始日志中提取结构化字段）、丰富（从查找表中添加上下文）、Events2Metrics（从日志/跨度事件中导出指标）和记录规则（预计算 PromQL 表达式）。

---

## CLI 命令

| 命令 | 子命令 | 目的 |
|---|---|---|
| `cx parsing-rules` | `list`, `get`, `create`, `update`, `delete`, `bulk-delete`, `usage-limits` | 管理日志解析规则 |
| `cx enrichments` | `list`, `add`, `remove`, `overwrite`, `limit`, `settings` | 管理丰富规则 |
| `cx enrichments custom` | `list`, `get`, `create`, `update`, `delete`, `search` | 管理自定义丰富表 |
| `cx e2m` | `list`, `get`, `create`, `update`, `delete`, `labels-cardinality`, `limits` | 管理 Events2Metrics 定义 |
| `cx recording-rules` | `list`, `get`, `create`, `update`, `delete` | 管理 Prometheus 记录规则组 |

关键标志：
- 所有创建/更新操作使用 `--from-file <路径>`（或 `-` 表示标准输入）
- 所有命令支持 `-o json` 用于结构化输出和 `-p <profile>` 用于配置文件选择
- `cx parsing-rules update` 和 `cx recording-rules update` 需要同时使用 `--from-file` 和规则组 ID
- `cx enrichments custom search` 需要 `--id <table-id>` 和 `--query <文本>`
- `cx parsing-rules bulk-delete` 需要 `--ids <id1> <id2> ...`

---

## 处理 JSON 负载

这些命令使用复杂的 JSON 结构。**始终从现有资源模板化**以避免格式错误：

```bash
# 1. 获取现有资源作为模板
cx parsing-rules get <rule-group-id> -o json > template.json

# 2. 修改模板（更改字段，为创建操作删除 ID）

# 3. 创建或更新
cx parsing-rules create --from-file template.json
cx parsing-rules update --from-file template.json <rule-group-id>
```

此模式适用于所有 4 个命令的创建/更新操作。它可防止导致失败尝试的首要原因——负载格式错误。

---

## 解析规则工作流

### 1. 列出现有规则

```bash
cx parsing-rules list -o json
cx parsing-rules list -o json | jq '[.[] | {id, name, enabled, rule_count: (.rules | length)}]'
```

### 2. 获取模板

```bash
cx parsing-rules get <existing-rule-group-id> -o json > rule-template.json
```

### 3. 创建新规则组

编辑适用于新服务的模板，然后：

```bash
cx parsing-rules create --from-file rule-template.json
```

### 4. 验证解析

查询最近日志以确认字段是否被提取（加载 `cx-telemetry-querying` 用于日志查询）：

```bash
cx logs 'source logs | filter $d.subsystem == "my-service" | limit 10' -o json
```

### 5. 检查使用限制

```bash
cx parsing-rules usage-limits -o json
```

---

## 丰富工作流

### 1. 列出丰富规则

```bash
cx enrichments list -o json
cx enrichments settings -o json
cx enrichments limit -o json
```

### 2. 创建自定义丰富表（如果需要）

```bash
cx enrichments custom list -o json
cx enrichments custom create --from-file table-definition.json
```

`table-definition.json` 必须使用 v5 JSON 结构（内联文件内容，不是多部分 `file=@...`）：

```json
{
  "name": "IP Lookup",
  "description": "Maps IPs to locations",
  "file": {
    "textual": "ip,city\n1.2.3.4,London",
    "extension": "csv",
    "name": "lookup.csv",
    "size": 24
  }
}
```

对于更新，包含 `customEnrichmentId`（数字）加上相同的字段。

### 3. 添加丰富规则

```bash
cx enrichments add --from-file enrichment-rules.json
```

`enrichment-rules.json` 必须使用 `requestEnrichments`（而不是列表输出中的 `enrichments`）。每个 `enrichmentType` 是一个对象，而不是字符串：

```json
{
  "requestEnrichments": [
    {
      "fieldName": "sourceIPs",
      "enrichmentType": { "geoIp": { "withAsn": true } }
    }
  ]
}
```

其他类型：`{"aws": {"resourceType": "ec2"}}`，`{"suspiciousIp": {}}`，`{"customEnrichment": {"id": 1}}`。

### 4. 搜索自定义表数据

```bash
cx enrichments custom search --id <table-id> --query "search term"
```

### 5. 验证丰富字段

查询热存储（FrequentSearch 层级）上的日志以确认丰富字段出现。避免查询存档进行验证——摄入延迟可能导致假阴性。

```bash
cx logs 'source logs | filter $d.enriched_field != null | limit 5' -o json
```

---

## Events2Metrics 工作流

E2M 从日志/跨度事件中导出 Prometheus 指标。参见 **[`references/e2m-schemas.md`](references/e2m-schemas.md)** 获取完整的 JSON 线格式、枚举和基数规则。

### E2M 的计算方式（首先阅读）

E2M 在事件**实时摄入管道中流式传输时**聚合事件到指标序列（~1 分钟分辨率）。它是**单向**的——指标从创建 E2M 的时刻开始；**没有回填**。

所有摄入的数据都通过管道；**TCO 政策**将每个流路由到层级，层级决定什么是可能的：

| TCO 层级 | 存储 | E2M / 提醒 / 仪表板 |
|---|---|---|
| **高** | Frequent Search (热, OpenSearch) | ✅ 可用 |
| **中** | S3 存档（非热存储） | ✅ 可用——仍然通过管道处理 |
| **低** | 合规性仅 | ❌ 无聚合功能 |
| **阻止** | 被丢弃 | ❌ |

轴是**层级/处理级别——不是“Frequent Search vs 存档”**（中 *是* 存档，E2M 在其上工作）。不要告诉用户“将 E2M 指向存档而不是 Frequent Search”——这是不正确的。

### 1. 设计指标

选择 `logs2metrics` vs `spans2metrics`、源字段+聚合，以及标签（考虑基数——参见 `references/e2m-schemas.md`）。要将 E2M 作用域限定于一个**数据集**，将可选的 `dataSource` 字段设置为 `"<dataspace>/<dataset>"`；这需要账户功能 `e2m_dataset_source_enabled`（否则 API 会以“dataSource 对此公司不可用”拒绝）。省略它以用于标准日志/跨度流。

### 2. 规模化：检查限制和基数

```bash
cx e2m limits -o json              # 账户 E2M 数量限制 + 已使用
cx e2m labels-cardinality -o json  # 参见注意事项
```

标签基数端点是**草稿预测**——给定建议的标签+查询，它返回过去 7 天的每个日唯一排列计数，以便在创建之前调整设计。**但 `cx e2m labels-cardinality` 目前不接收参数**，因此它发送草稿并返回空列表（CLI 间隙——它还不能预测）。直到它被连接起来，请通过 UI 预测或手动估计排列（不同标签值的乘积）并设置 `permutationsLimit`。永远不要使用高基数字段（ID、原始 URL、IP）作为标签。注意预测仅看到 Frequent-Search（高层级）数据。

### 3. 从现有定义模板化

只有 `cx e2m get` 返回完整负载（`{"e2m": {...}}`）；`list` 打印摘要。提取 `.e2m` 并删除只读字段：

```bash
cx e2m get <existing-e2m-id> -o json | jq '.e2m | del(.id, .permutations, .createTime, .updateTime, .metricName)' > e2m.json
```

### 4. 创建 E2M

```bash
cx e2m create --from-file e2m.json
```

### 5. 验证指标

确认序列正在生成（加载 `cx-telemetry-querying` 用于指标查询）：

```bash
cx metrics search --name "<targetBaseMetricName>"
cx metrics query "<target_metric_name>" --time now
```

### 故障排除：E2M 生成无指标序列

1. **检查源数据的 TCO 层级**——如果它被路由到 **低/合规**（或阻止），E2M 无法运行。通过 `cx tco list` / `cx-cost-optimization` 修复 TCO 变更，**不是** E2M 变更。
2. **验证查询匹配流式数据**——运行 E2M 的 `lucene` 过滤器作为实时 `cx logs`/`cx spans` 查询并确认它返回最近的结果。注意 `cx logs` 默认查询 Frequent-Search（高层级）；对于 **中层级（存档）** 源添加 `--tier archive`，因为即使 E2M 仍然生成序列，数据也不会出现在默认 Frequent-Search 查询中。
3. **记住它是单向的**——在创建 E2M 之前摄入的数据没有序列。

### 成本优化：将高层级日志转换为指标

当**聚合/指标视图是客户最关心的**时，将 **高层级日志 → 指标**，然后将原始日志 **高 → 中**。中层级仍然支持 E2M/提醒/仪表板，成本更低（S3 存档，无热存储）——你保留廉价、详细的指标，同时丢弃昂贵的 Frequent-Search 保留。

1. 查找高容量高层级源：`cx usage summary` / `cx tco list`（参见 `cx-cost-optimization`）。
2. 确认哪些字段驱动仪表板/提醒（参见 `cx-telemetry-querying`）。
3. 构建 + **首先验证 E2M**（上述步骤）。
4. **然后**更改 TCO 政策将原始日志高 → 中。保留数据在高或中层级（两者都支持 E2M）；**不要**将其丢弃到低/合规，如果仍然需要指标或提醒。

---

## 记录规则工作流

### 1. 列出现有记录规则

```bash
cx recording-rules list -o json
cx recording-rules list -o json | jq '[.[] | {id, name, rules: [.rules[]?.record]}]'
```

### 2. 获取模板

```bash
cx recording-rules get <existing-id> -o json > recording-rule-template.json
```

### 3. 创建记录规则组

```bash
cx recording-rules create --from-file recording-rule-group.json
```

### 4. 使用 PromQL 验证

确认预计算的指标可用（加载 `cx-telemetry-querying` 用于指标查询）：

```bash
cx metrics query "new_precomputed_metric" --time now
```

---

## 关键原则

- **始终从现有资源模板化** - `cx <command> get <id> -o json > template.json` 在任何创建之前
- **创建后验证** - 查询日志/指标以确认管道更改已生效
- **使用 `-o json`** - 所有负载检查和创建应使用 JSON 输出
- **首先检查限制** - `cx parsing-rules usage-limits` 和 `cx e2m limits` 在创建之前以避免达到上限
- **批量操作** - 使用 `cx parsing-rules bulk-delete --ids` 进行清理，而不是单个删除

---

## 其他资源

### 参考文件

- **[`references/e2m-schemas.md`](references/e2m-schemas.md)** - 完整的 Events2Metrics JSON 线格式：`type`/`aggType` 枚举值、`logsQuery`/`spansQuery` 过滤器、指标标签&字段、TCO层级计算模型、基数/排列规模化，以及注意事项

---

## 相关技能

- **`cx-telemetry-querying`** - 在配置管道之前发现可用数据，并验证解析结果、丰富字段和 E2M 指标序列通过日志/指标查询
- **`cx-cost-optimization`** - 查找值得转换为指标的 高层级高容量源，并在验证 E2M 后将原始日志 高→中（TCO）
