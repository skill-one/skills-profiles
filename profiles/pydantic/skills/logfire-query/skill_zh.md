# 查询 Logfire 数据

## 使用此技能的场景

在以下情况下调用此技能：
- 用户需要从 Logfire 查询跟踪、日志、跨度或指标
- 用户需要在遥测数据中搜索特定事件、错误或模式
- 用户需要分析存储在 Logfire 中的 OpenTelemetry 数据
- 用户需要将其代码添加程序化查询功能
- 用户询问“查询 Logfire”、“搜索跟踪”、“查找日志”、“获取指标”、“计数”、“汇总”、“比较”或“查找根本原因”

## 用户可见进度

保持进度更新简洁。不要描述路由分类、本地技能指令、模式选择或常规查询设置。如果需要更新，请使用简短的句子专注于操作，例如“查询最近的 Logfire 错误。”

## 关键路由：每个请求一个工作流

在使用任何查询工具之前，对请求进行分类。

- 查询路由：“分析”、“查询”、“计数”、“汇总”、“比较”、“查找根本原因”、“查找最慢的”、“查找错误”、“获取指标”或“添加查询功能”。
- UI 路由：“打开”、“在浏览器中显示”、“在 Codex 中显示”、“在 Logfire 中显示”、“实时查看”、“打开 Explore”、“打开 UI”、“给我一个链接”或 GUI/浏览器呈现。使用 `logfire-ui`；不要调用 `query_run` 仅为了生成 URL。
- 模糊路由：如“显示最近的错误”、“查看日志”或“显示跨度”等提示不明确用户是想进行聊天分析还是在 Logfire UI 中查看。请要求用户选择查询分析或 UI 查看。
- 组合路由：如果用户明确要求同时进行分析和链接，则仅查询请求的分析或识别请求的项目，然后提供相关的 Logfire 链接。除非用户要求，否则不要添加 UI/浏览器工作。

仅在用户要求打开特定未知项目且必须先找到它时，在打开 Logfire UI 之前进行查询，例如“找到最慢的跟踪并打开它”或“打开最新的错误跟踪”。

## 两种方法

| 方面 | MCP `query_run` | REST API `/v1/query` |
|------|-----------------|----------------------|
| **最适合** | 在 Codex 中进行交互式分析 | 将查询代码添加到项目中 |
| **认证** | 通过 MCP 会话进行 OAuth | Bearer 读取令牌 |
| **设置** | 通过插件已配置 | 需要读取令牌 |
| **格式** | JSON 行 | JSON、CSV、Apache Arrow |
| **默认窗口** | 最后 30 分钟 | 最后 24 小时 |
| **最大范围** | 14 天 | 14 天 |
| **行限制** | 必须在 SQL 中 | 默认 500，最大 10,000 |

## 快速模式参考

### `records` 表（跨度 和 日志）

查询的关键列：

| 列名 | 类型 | 描述 |
|------|------|------|
| `start_timestamp` | 时间戳 (UTC) | 跨度/日志创建时间 |
| `end_timestamp` | 时间戳 (UTC) | 跨度/日志完成时间 |
| `duration` | double (秒) | 开始和结束之间的时间；日志为 NULL |
| `trace_id` | 字符串 (32 十六进制) | 唯一跟踪标识符 |
| `span_id` | 字符串 (16 十六进制) | 唯一跨度标识符 |
| `parent_span_id` | 字符串 (16 十六进制) | 父跨度；根跨度为 NULL |
| `span_name` | 字符串 | 用于相似记录的低基数标签 |
| `message` | 字符串 | 带有参数填充的人类可读描述 |
| `level` | 整数 | 严重性（支持 `level = 'error'` 字符串比较） |
| `kind` | 字符串 | `span`、`log`、`span_event` 或 `pending_span` |
| `service_name` | 字符串 | 服务标识符 |
| `is_exception` | 布尔值 | 是否记录了异常 |
| `exception_type` | 字符串 | 异常类名 |
| `exception_message` | 字符串 | 异常消息 |
| `exception_stacktrace` | 字符串 | 完整的回溯 |
| `attributes` | JSON | 结构化数据；使用 `->>'key'` 进行查询 |
| `tags` | 字符串[] | 分组标签；使用 `array_has(tags, 'x')` 进行查询 |
| `http_response_status_code` | 整数 | HTTP 状态码 |
| `http_method` | 字符串 | HTTP 方法 |
| `http_route` | 字符串 | HTTP 路由模式 |
| `otel_status_code` | 字符串 | 跨度状态 |

### `metrics` 表

| 列名 | 类型 | 描述 |
|------|------|------|
| `recorded_timestamp` | 时间戳 (UTC) | 指标记录时间 |
| `metric_name` | 字符串 | 指标名称 |
| `metric_type` | 字符串 | 类型（gauge、counter、histogram） |
| `unit` | 字符串 | 测量单位 |
| `scalar_value` | double | 指标值 |
| `service_name` | 字符串 | 服务标识符 |
| `attributes` | JSON | 指标维度 |

完整模式：[`references/schema.md`](./references/schema.md)

## SQL 语法

Logfire 使用 **Apache DataFusion**（类似 Postgres）。关键模式：

```sql
-- 时间过滤
WHERE start_timestamp > now() - interval '1 hour'

-- JSON 属性访问
WHERE attributes->>'user_id' = '123'
SELECT attributes->>'http.url' as url FROM records

-- 嵌套 JSON
attributes->'request'->>'method'

-- 数组过滤
WHERE array_has(tags, 'production')

-- 级别过滤（字符串比较有效）
WHERE level = 'error'

-- 不区分大小写的匹配
WHERE message ILIKE '%timeout%'

-- 时间分桶用于聚合
SELECT time_bucket(interval '5 minutes', start_timestamp) as bucket,
       count(*) FROM records GROUP BY bucket ORDER BY bucket
```

## MCP 方法（交互式）

调用 `query_run` MCP 工具：
- `query`（必需）：SQL 查询字符串
- `project`（可选）：目标项目（默认：用户当前项目）
- `min_timestamp` / `max_timestamp`（可选）：ISO 时间戳，用于时间窗口

默认窗口为最后 30 分钟。最大范围为 14 天。SQL 中始终包含 `LIMIT`。

### 常见查询

```sql
-- 最近错误
SELECT start_timestamp, message, exception_type, exception_message
FROM records WHERE is_exception LIMIT 20

-- 慢跨度
SELECT span_name, duration, start_timestamp
FROM records WHERE duration > 1.0 ORDER BY duration DESC LIMIT 20

-- 端点错误
SELECT start_timestamp, message, http_response_status_code
FROM records WHERE http_route = '/api/users' AND level = 'error' LIMIT 20

-- 完整跟踪
SELECT span_name, message, duration, parent_span_id
FROM records WHERE trace_id = '<id>' ORDER BY start_timestamp

-- 按服务错误分解
SELECT service_name, count(*) as errors
FROM records WHERE is_exception GROUP BY service_name ORDER BY errors DESC
```

## 查询后的 UI 链接

如果用户明确要求同时进行分析和 Logfire 链接，请先完成查询分析，然后仅对已知结果使用 Logfire 链接：

- 对于已知的 `trace_id`，仅在用户要求立即在浏览器中打开时使用 `project_logfire_link(trace_id=trace_id, project=project, handoff=True)`。使用 `project_logfire_link(trace_id=trace_id, project=project)` 为持久或可共享的 URL。
- 对于项目/过滤器视图，使用 `logfire-ui` 路由规则。
- 除非用户要求，否则不要打开浏览器。

对于跨度计数提示，当用户需要聚合查询或分析时，提供如下 SQL：

```sql
SELECT
  time_bucket(interval '5 minutes', start_timestamp) AS bucket,
  count(*) AS span_count
FROM records
WHERE kind = 'span'
GROUP BY bucket
ORDER BY bucket
LIMIT 200
```

## REST API 方法（程序化）

**端点**：`GET https://logfire-api.pydantic.dev/v1/query`

区域变体：
- US: `https://logfire-us.pydantic.dev/v1/query`
- EU: `https://logfire-eu.pydantic.dev/v1/query`

**认证**：`Authorization: Bearer <读取令牌>`

**参数**：
- `sql`（必需）：SQL 查询
- `min_timestamp` / `max_timestamp`（可选）：ISO 时间戳
- `limit`（可选）：行限制（默认 500，最大 10,000）

**响应格式**（通过 `Accept` 头部）：
- `application/json` — 列向 JSON（默认）
- `application/json` 与 `row_oriented=true` 参数 — 行向 JSON
- `text/csv` — CSV
- `application/vnd.apache.arrow.stream` — Apache Arrow

**Python 客户端**：`LogfireQueryClient`（同步）、`AsyncLogfireQueryClient`（异步）、`logfire.db_api`（PEP 249 / pandas）。

详细示例：[`references/client-usage.md`](./references/client-usage.md)

## 查询最佳实践

1. **始终使用 LIMIT** — 从 20 开始，按需增加
2. **使用 `min_timestamp`/`max_timestamp` 参数** 对于简单的时间窗口，而不是 SQL `WHERE`
3. **高效过滤** — `service_name`、`span_name`、`trace_id`、`is_exception` 是快速过滤器
4. **使用 `->>'key'`** 进行 JSON 属性访问（返回文本）；使用 `->` 进行嵌套 JSON 对象
5. **避免 `SELECT *`** — 仅选择您需要的列
6. **最大 14 天范围** — 查询不能跨越 14 天
