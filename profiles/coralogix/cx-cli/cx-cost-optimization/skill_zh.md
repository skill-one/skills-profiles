# 成本优化技能

在调查或降低 Coralogix 数据成本时使用此技能。它涵盖了完整的成本管理生命周期：衡量当前支出、审查 TCO 政策、调整保留期以及为冷数据配置归档存储。

---

## CLI 命令

| 命令 | 子命令 | 目的 |
|---|---|---|
| `cx usage` | `summary`, `daily`, `logs-count`, `spans-count`, `export-status`, `capabilities`, `query` | 衡量当前数据消耗和可计费使用量 |
| `cx tco` | `list`, `get`, `create`, `update`, `delete`, `reorder`, `test`, `settings`, `settings-update` | 管理 TCO（总拥有成本）政策 |
| `cx retentions` | `list`, `update`, `activate`, `status` | 管理数据保留期 |
| `cx archive logs` | `get`, `set` | 配置日志归档目标 |
| `cx archive metrics` | `get`, `create`, `update`, `enable`, `disable`, `validate` | 配置指标归档存储 |
| `cx metrics query` | `<promql>`（位置参数），`--time` | 通过 PromQL（即时）查询计费和使用指标 |
| `cx metrics query-range` | `<promql>`（位置参数），`--start`/`--end` | 通过 PromQL（范围）查询计费和使用指标 |

关键标志：
- 所有命令都支持 `-o json` 用于结构化输出和 `-p <profile>` 用于配置文件选择
- `cx usage daily` 接受 `--type processed-gbs|units|evaluation-tokens` 和 `--start`/`--end` 时间过滤器
- `cx usage summary` 接受 `--start`/`--end` 时间过滤器
- `cx usage logs-count` 和 `cx usage spans-count` 接受 `--start`/`--end` 时间过滤器，默认为最后 24 小时，加上 `--resolution`（默认 `1h`）、`--subsystem-aggregation`、`--application-aggregation`，以及重复的 `--param KEY=VALUE` 用于 API 过滤查询参数
- 数据使用摘要和计数端点作为换行分隔的 JSON 文件通过 `Accept: text/event-stream` 文档化；CLI 处理该传输并将计数块标准化为 `.result.logsCount[]` 或 `.result.spansCount[]`。
- `cx usage capabilities` 是必须的第一步：它返回当前租户下公共数据使用查询 API 支持的标签、测量值、单位和请求限制
- `cx usage query` 是必须的第二步：仅提交从立即之前的 `capabilities` 响应派生的 JSON 请求，并使用 `--query '<json>'` 或 `--from-file <path>`（`--from-file -` 读取标准输入）
- `cx tco create/update`、`cx retentions update`、`cx archive logs set`、`cx archive metrics create/update/validate` 使用 `--from-file <path>`（或 `-` 用于标准输入）

---

## 权威的可计费使用查询

对于可计费总额、配额单位、计划消耗或支持的使用分解，请使用此强制性的两步工作流程：

1. 在当前会话中运行 `cx usage capabilities`。
2. 使用该响应构建并运行 `cx usage query`。

不要首先调用 `cx usage query`，也不要猜测标签、测量值类型、单位、过滤值、间隔或请求限制。它们是租户特定的，并且可能会发生变化。

```bash
# 检查当前有效的维度和限制
cx usage capabilities -o json

# 直接内联提交派生自 capabilities 的请求
cx usage query --query '{"daily":{"relativeRange":"DAILY_RELATIVE_RANGE_LAST_7_DAYS"}}' -o json

# 或者从文件或标准输入中读取相同的请求
cx usage query --from-file usage-query.json -o json
printf '%s' '{"daily":{"relativeRange":"DAILY_RELATIVE_RANGE_LAST_7_DAYS"}}' \
  | cx usage query --from-file - -o json
```

在创建查询正文之前加载 [`references/data-usage-query-api.md`](references/data-usage-query-api.md)。它定义了能力和响应模式、有效间隔形式和限制。

---

## 成本调查工作流

按照以下步骤诊断和降低成本：

### 第 1 步：衡量当前使用量

对于可计费总额、配额单位、计划消耗或支持的使用分解，首先遵循上述强制性的两步工作流程：

```bash
cx usage capabilities -o json
cx usage query --from-file usage-query.json -o json
```

仅从立即之前的 capabilities 响应构建 `usage-query.json`。不要使用以下旧命令作为权威计费答案的替代品。

对于旧版消耗概述和日志/跨度记录计数，使用：

```bash
cx usage summary -o json
cx usage summary --start now-30d -o json
cx usage daily --type processed-gbs --start now-7d -o json
cx usage logs-count --start now-7d --end now -o json
cx usage spans-count --start now-7d --end now -o json
```

识别哪些数据类型消耗的量最大。使用 `jq` 进行排序：

```bash
cx usage summary -o json | jq '[.[] | {name, daily_avg: .avg_daily_gb}] | sort_by(.daily_avg) | reverse'
```

### 第 2 步：审查 TCO 政策

```bash
cx tco list -o json
cx tco settings -o json
```

TCO 政策控制哪些日志进入频繁搜索（昂贵、快速）或归档（便宜、较慢）。检查高容量、低价值的日志是否在频繁搜索上：

```bash
cx tco list -o json | jq '.[] | select(.priority == "LOW") | {name, application, subsystem, archive_retention}'
```

### 第 3 步：检查保留设置

```bash
cx retentions list -o json
cx retentions status -o json
```

较长的保留期会增加存储成本。识别保留期不必要的索引。

### 第 4 步：检查归档配置

```bash
cx archive logs get -o json
cx archive metrics get -o json
```

验证是否为冷数据配置了归档存储。如果没有设置归档，这是一个节省成本的机会。

### 第 5 步：建议优化

根据发现，按优先级顺序（最高影响优先）建议更改。

---

## 常见优化模式

| 症状 | 诊断命令 | 优化 |
|---|---|---|
| 高容量低价值日志 | `cx usage summary -o json` | 通过 `cx tco create --from-file policy.json` 移动到归档层 |
| 冷数据上的长保留期 | `cx retentions list -o json` | 使用 `cx retentions update --from-file` 减少保留期 |
| 未配置冷存储 | `cx archive logs get -o json` | 使用 `cx archive logs set --from-file --yes`（在用户批准后）启用归档 |
| 未查询昂贵指标 | `cx archive metrics get -o json` | 使用 `cx archive metrics create --from-file --yes`（在用户批准后）启用指标归档 |

---

## jq 示例

### 使用量分析

```bash
# 按每日容量排序的前 10 名消费者
cx usage summary -o json | jq '[.[] | {name, daily_avg: .avg_daily_gb}] | sort_by(.daily_avg) | reverse | .[0:10]'

# 过去一周的每日趋势
cx usage daily --type processed-gbs --start now-7d -o json | jq '[.[] | {date, gb: .processed_gbs}]'

# 总日志和跨度计数
cx usage logs-count --start now-7d --end now -o json | jq '[.result.logsCount[]?.logsCount | tonumber] | add // 0'
cx usage spans-count --start now-7d --end now -o json | jq '[.result.spansCount[]? | ((.successSpanCount | tonumber) + (.errorSpanCount | tonumber) + (.lowSuccessSpanCount | tonumber) + (.lowErrorSpanCount | tonumber) + (.mediumSuccessSpanCount | tonumber) + (.mediumErrorSpanCount | tonumber))] | add // 0'
```

### TCO 政策分析

```bash
# 路由到归档层的政策
cx tco list -o json | jq '[.[] | select(.archive_retention != null)]'

# 按优先级排序的政策
cx tco list -o json | jq 'group_by(.priority) | map({priority: .[0].priority, count: length})'

# 测试日志模式是否匹配政策
cx tco test --from-file test-definition.json -o json
```

### 保留期审查

```bash
# 所有保留设置
cx retentions list -o json | jq '.[]'

# 检查保留期是否激活
cx retentions status -o json
```

### 归档状态

```bash
# 日志归档配置
cx archive logs get -o json | jq '{active: .active, bucket: .bucket}'

# 指标归档配置
cx archive metrics get -o json | jq '{enabled: .enabled, bucket: .bucket}'
```

---

## 应用更改

**重要提示：** 不要在未经明确用户批准的情况下使用 `--yes`。所有跨归档、TCO 和保留期的写操作都需要交互式确认，并且必须使用 `--yes` 标志才能非交互式执行。在执行任何写操作之前，向用户描述确切更改，并等待他们的批准，然后再使用 `--yes`。

**只读模式：** 使用 `--read-only`（或 `CX_READ_ONLY=1`）安全地探索成本数据，而不会意外写入。所有查询命令（usage、tco list/get、retentions list、archive get）在只读模式下正常工作。

**代理模式：** 在 AI 代理中运行时，cx 在写操作上快速失败，而不是在标准输入提示上挂起。首先获取用户确认，然后重新运行并使用 `--yes`。

在修改 TCO 政策、保留期或归档时：

1. **从现有模板：** 获取当前配置作为 JSON，修改它，然后应用：
   ```bash
   cx tco get <policy-id> -o json > policy.json
   # 编辑 policy.json
   cx tco update --from-file policy.json
   ```

2. **更改后验证：** 重新运行诊断命令以确认更改是否生效。

3. **TCO 政策排序很重要：** 使用 `cx tco reorder --from-file` 设置优先级顺序。政策按从上到下的顺序评估；第一个匹配项生效。

---

## 基于指标的成本分析

`cx usage` API 提供摘要，但对于计费准确的分析、异常检测和按支柱/功能分解，请通过 PromQL 查询客户指标导出器。

### 关键指标

| 指标 | 含义 | 查询后缀 |
|---|---|---|
| `cx_data_usage_units` | 每日可计费使用量（规范计费指标） | 无 `_total` |
| `cx_data_plan_units_per_day` | 当前每日计划配额（快照） | 无 `_total` |
| `cx_data_usage_payg_units` | 每日超额/PAYG 使用量 | 无 `_total` |
| `cx_data_usage_total` | 处理的数据大小（字节） | `_total` |
| `cx_data_usage_tokens_total` | AI 评估令牌 | `_total` |
| `cx_data_usage_samples_total` | 处理的指标样本 | `_total` |

### 概念到指标的映射

- **计费 / 计划使用量 / 消耗** -> `cx_data_usage_units` + `cx_data_plan_units_per_day`
- **处理字节数 / 数据量** -> `cx_data_usage_total`
- **AI 评估令牌** -> `cx_data_usage_tokens_total`
- **指标样本** -> `cx_data_usage_samples_total`
- **超额 / PAYG** -> `cx_data_usage_payg_units`

### 常见 PromQL 查询

```bash
# 今日已消耗的可计费单位
cx metrics query 'sum(cx_data_usage_units)' --time now -o json

# 按支柱分解的单位
cx metrics query 'sum by (pillar) (cx_data_usage_units)' --time now -o json

# 每日计划配额
cx metrics query 'cx_data_plan_units_per_day' --time now -o json

# 计划消耗百分比
cx metrics query '100 * sum(cx_data_usage_units) / cx_data_plan_units_per_day' --time now -o json

# 按功能组分的单位
cx metrics query 'sum by (feature_group_id) (cx_data_usage_units)' --time now -o json

# PAYG 超额（如有）
cx metrics query 'cx_data_usage_payg_units' --time now -o json
```

### UTC-Day 桶规则

所有使用指标从 UTC 午夜累积并在 `00:00 UTC` 重置：
- 白天进行的即时查询返回“今日至今”
- 对于完成的每日总额，使用午夜之前的最后一个样本
- 不要在 UTC 午夜边界上减去值
- 对于周/月分析，首先导出完成的每日总额，然后汇总
- 计算趋势或平均值时排除当前部分 UTC 天

### 异常检测

在调查使用量异常时：
1. 比较完成的 UTC 天（排除当前部分天）
2. 按以下顺序分解：`measurement_type` -> `pillar` -> `entity_type` -> `priority` -> `feature_group_id` -> `application_name` -> `subsystem_name`
3. 优先使用同一天的比较以进行季节性流量分析
4. 使用 `cx_data_usage_units` 进行计费异常，`cx_data_usage_total` 进行量异常

### 分组标签

使用量指标支持以下分组维度：`pillar`、`entity_type`、`priority`、`measurement_type`、`feature_group_id`、`feature_id`、`application_name`、`subsystem_name`。

---

## 关键原则

- **更改前测量** - 始终在修改政策之前运行使用量/摘要命令
- **使用 `-o json` 与 jq** - 结构化输出可进行精确分析
- **验证更改** - 每次修改后重新查询以确认是否生效
- **多配置文件意识** - 使用 `-p <profile>` 或 `--all-profiles` 比较不同环境的成本
- **从现有模板** - 获取当前配置作为 JSON 之前创建或更新
- **TCO 是最大的杠杆** - 将日志从频繁搜索移动到归档层对成本影响最大

---

## 相关技能

- **`cx-telemetry-querying`** - 调查正在输入哪些数据（查询日志、指标和跨度以识别高容量源）

## 参考文件

- **[`references/data-usage-query-api.md`](references/data-usage-query-api.md)** - 能力和查询模式、间隔规则、限制和响应解释
