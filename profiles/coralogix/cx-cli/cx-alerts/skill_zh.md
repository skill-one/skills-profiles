# 警报管理技能

使用此技能通过 `cx alerts` CLI 命令列出、检查、创建、删除、启用和禁用 Coralogix 警报定义。

## CLI 命令

| 命令 | 目的 | 关键标志 |
|---|---|---|
| `cx alerts list` | 列出所有警报定义 | `--name <filter>` |
| `cx alerts get <id>` | 通过 ID 获取单个警报定义 | - |
| `cx alerts create` | 从 JSON 定义创建警报 | `--from-file <path>` (默认: stdin) |
| `cx alerts delete <id>` | 删除警报 | - |
| `cx alerts enable <id>` | 启用警报 | - |
| `cx alerts disable <id>` | 禁用警报 | - |
| `cx alerts events` | 列出事件；过滤时使用警报版本范围端点 | `--alert-version-id`, `--start`, `--end` |
| `cx alerts event-stats` | 获取警报事件统计信息 | - |
| `cx alerts suppression-rules list` | 列出抑制规则 | - |
| `cx alerts suppression-rules get <id>` | 获取抑制规则 | - |
| `cx alerts suppression-rules create` | 创建抑制规则 | `--from-file <path>` |
| `cx alerts suppression-rules update` | 更新抑制规则 | `--from-file <path>` |
| `cx alerts suppression-rules delete <id>` | 删除抑制规则 | - |

**输出格式：** 在 `list`、`get` 和 `create` 命令后追加 `-o json` 或 `-o toon` 以获取机器可读的输出。

**多配置文件：** 使用 `-p <profile>` (可重复) 同时针对多个配置文件。

## 警报类型参考

Coralogix 支持 12 种警报类型：

| 类型枚举 | 人类名称 | 描述 |
|---|---|---|
| `ALERT_DEF_TYPE_LOGS_IMMEDIATE` | Logs Immediate | 每条匹配的日志条目触发 |
| `ALERT_DEF_TYPE_LOGS_THRESHOLD` | Logs Threshold | 日志计数在时间窗口内超过阈值时触发 |
| `ALERT_DEF_TYPE_LOGS_ANOMALY` | Logs Anomaly | 基于机器学习的日志量异常检测 |
| `ALERT_DEF_TYPE_LOGS_RATIO_THRESHOLD` | Logs Ratio Threshold | 触发两个日志查询之间的比率 |
| `ALERT_DEF_TYPE_LOGS_NEW_VALUE` | Logs New Value | 字段中出现新值时触发 |
| `ALERT_DEF_TYPE_LOGS_UNIQUE_COUNT` | Logs Unique Count | 唯值计数超过阈值时触发 |
| `ALERT_DEF_TYPE_LOGS_TIME_RELATIVE_THRESHOLD` | Logs Time Relative | 比较当前与过去的时间窗口 |
| `ALERT_DEF_TYPE_METRIC_THRESHOLD` | Metric Threshold | PromQL 表达式跨越阈值时触发 |
| `ALERT_DEF_TYPE_METRIC_ANOMALY` | Metric Anomaly | 基于机器学习的指标异常检测 |
| `ALERT_DEF_TYPE_TRACING_IMMEDIATE` | Tracing Immediate | 每条匹配的跨度触发 |
| `ALERT_DEF_TYPE_TRACING_THRESHOLD` | Tracing Threshold | 跨度计数超过阈值时触发 |
| `ALERT_DEF_TYPE_FLOW` | Flow | 基于序列的组合多个条件的警报 |

## 优先级级别

创建警报时始终询问用户要使用什么优先级：

| 优先级 | 用例 |
|---|---|
| P1 | 关键 - 立即通知值班人员 |
| P2 | 高 - 一小时内需要关注 |
| P3 | 中 - 工作时间进行调查 |
| P4 | 低 - 信息性，方便时检查 |
| P5 | Info - 仅用于日志/跟踪 |

## 创建工作流

1. 询问用户要警报的内容（日志、指标、跟踪）
2. 询问优先级 (P1–P5)
3. 使用 `alertDefProperties` 构建 JSON 负载 - 使用 **API 线路格式**（有关所有枚举值的完整参考，请参阅 `references/alert-schemas.md`）
4. **提示：** 使用 `cx alerts get <现有-id> -o json` 获取工作模板，修改它，并将其管道输入到创建中
5. 使用：`echo '<json>' | cx alerts create` 或 `cx alerts create --from-file alert.json`
6. 验证：`cx alerts list --name "<警报名称>"`

**重要结构说明：** `type` 字段是一个 **字符串枚举**（例如 `"ALERT_DEF_TYPE_LOGS_THRESHOLD"`），而警报类型配置（例如 `"logsThreshold": {...}`）是同一级别的 **兄弟** 字段 - 不嵌套在 `type` 内。

### 示例：日志阈值警报

```json
{
  "alertDefProperties": {
    "name": "高错误率",
    "description": "当错误日志超过阈值时触发警报",
    "priority": "ALERT_DEF_PRIORITY_P2",
    "type": "ALERT_DEF_TYPE_LOGS_THRESHOLD",
    "enabled": true,
    "logsThreshold": {
      "logsFilter": {
        "simpleFilter": {
          "luceneQuery": "severity:ERROR",
          "labelFilters": {
            "applicationName": [
              { "operation": "LOG_FILTER_OPERATION_TYPE_IS_OR_UNSPECIFIED", "value": "my-app" }
            ]
          }
        }
      },
      "rules": [{
        "condition": {
          "conditionType": "LOGS_THRESHOLD_CONDITION_TYPE_MORE_THAN_OR_UNSPECIFIED",
          "threshold": 100,
          "timeWindow": {
            "logsTimeWindowSpecificValue": "LOGS_TIME_WINDOW_VALUE_MINUTES_5_OR_UNSPECIFIED"
          }
        }
      }]
    }
  }
}
```

### 示例：指标阈值警报

```json
{
  "alertDefProperties": {
    "name": "CPU 使用率关键",
    "priority": "ALERT_DEF_PRIORITY_P1",
    "type": "ALERT_DEF_TYPE_METRIC_THRESHOLD",
    "enabled": true,
    "metricThreshold": {
      "metricFilter": { "promql": "avg(cpu_usage_percent)" },
      "rules": [{
        "condition": {
          "conditionType": "METRIC_THRESHOLD_CONDITION_TYPE_MORE_THAN_OR_UNSPECIFIED",
          "threshold": 90,
          "ofTheLast": { "dynamicDuration": "5m" },
          "forOverPct": 100
        }
      }]
    }
  }
}
```

### 示例：日志立即警报

```json
{
  "alertDefProperties": {
    "name": "OOM Killer Detected",
    "description": "OOM killer 运行时立即触发警报",
    "priority": "ALERT_DEF_PRIORITY_P1",
    "type": "ALERT_DEF_TYPE_LOGS_IMMEDIATE_OR_UNSPECIFIED",
    "enabled": true,
    "logsImmediate": {
      "logsFilter": {
        "simpleFilter": {
          "luceneQuery": "\"Out of memory\" OR \"OOM\"",
          "labelFilters": {}
        }
      }
    }
  }
}
```

## 调查工作流

### 查找触发的警报

```bash
# 列出所有警报并查找 ALERTING 状态
cx alerts list -o json | jq '.[] | select(.status == "ALERTING")'

# 按名称过滤
cx alerts list --name "error"
```

### 检查特定警报

```bash
cx alerts get <alert-id>
cx alerts get <alert-id> -o json
```

### 禁用嘈杂的警报（临时静音）

```bash
cx alerts disable <alert-id>
# 之后，重新启用：
cx alerts enable <alert-id>
```

## 抑制规则

管理警报抑制规则，在维护窗口或已知嘈杂期间静音警报。

| 命令 | 目的 |
|---|---|
| `cx alerts suppression-rules list` | 列出所有抑制规则 |
| `cx alerts suppression-rules get <id>` | 通过 ID 获取抑制规则 |
| `cx alerts suppression-rules create --from-file` | 创建抑制规则 |
| `cx alerts suppression-rules update --from-file` | 更新抑制规则 |
| `cx alerts suppression-rules delete <id>` | 删除抑制规则 |

```bash
# 列出抑制规则
cx alerts suppression-rules list -o json

# 从模板创建
cx alerts suppression-rules get <现有-id> -o json > suppression-rule.json
# 编辑 suppression-rule.json
cx alerts suppression-rules create --from-file suppression-rule.json
```

## 关键原则

- **创建警报时始终询问优先级** (P1–P5) - 绝不假设
- **使用 `--name` 过滤器** 用于拥有大量警报的大型帐户
- **使用 `-o json` 与 `jq`** 进行过滤和转换
- **使用 `--from-file -`** 将 JSON 从 stdin 管道输入以编程方式构建警报
- **创建后验证** - 创建后始终列出或获取警报以确认
- **禁用，而不是删除** - 优先禁用警报而不是删除，以实现可审计性
- **链接到特定警报** - `cx alerts list` 仅打印一个 "View in Coralogix" 链接，到警报概览页面，而不是每个警报的链接。要将用户链接到特定警报，请构建 `<base>/alerts/<alert_id>`，其中 `<base>` 是会话中任何 `cx alerts` 命令打印的 `View in Coralogix: <base>/...` 行中已看到的控制台 URL - 永远不要自己编造 `<base>`。

---

## 其他资源

### 参考文件

- **[`references/alert-schemas.md`](references/alert-schemas.md)** - 所有 12 种警报类型的完整 JSON 架构参考：字段名称、枚举值（条件类型、时间窗口、过滤器操作）、常见子对象（日志过滤器、跟踪过滤器、通知组、活动计划）以及重要的注意事项
- **[`references/dataprime-reference.md`](references/dataprime-reference.md)** - DataPrime 查询语言参考，用于基于日志和跨度的警报条件（过滤器语法、运算符、严重性值）
- **[`references/logs-querying.md`](references/logs-querying.md)** - 日志数据模型、字段发现和构建日志警报条件的查询模式
- **[`references/promql-guidelines.md`](references/promql-guidelines.md)** - PromQL 参考，用于基于指标的警报条件（计数器、仪表、直方图、阈值模式）
- **[`references/spans-querying.md`](references/spans-querying.md)** - 跨度数据模型、持续时间单位和构建跟踪警报条件的查询模式

### 相关技能

- **`cx-cases`** - 对分组警报事件为调查的案例进行分派
- **`cx-slos`** - 错误预算燃烧引发警报的 SLO 定义
- **`cx-observability-setup`** - 设置警报的通知路由和 webhook 集成
- **`cx-telemetry-querying`** - 调查触发警报背后的遥测
