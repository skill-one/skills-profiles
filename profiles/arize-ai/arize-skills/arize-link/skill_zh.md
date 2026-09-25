# Arize 链接

为项目、追踪、跨度、会话、数据集、标注队列、评估器和标注配置生成指向 Arize UI 的深度链接。

## 使用场景

- 用户需要项目、追踪、跨度、会话、数据集、标注队列、评估器或标注配置的链接
- 您有从导出数据或日志中获取的 ID，需要链接回 UI
- 用户要求在 Arize 中"打开"或"查看"上述任何一项

## 必填输入

从用户、上下文（导出的追踪数据或解析的 URL）或 `ax` CLI 收集：

| 总是必填 | 资源特定 |
|---|---|
| `org_id` (base64) | `project_id` + `trace_id` [+ `span_id`] — 追踪/跨度 |
| `space_id` (base64) | `project_id` + `session_id` — 会话 |
| | `dataset_id` — 数据集 |
| | `queue_id` — 特定队列（列出时省略） |
| | `evaluator_id` [+ `version`] — 评估器 |

### 发现组织和项目 ID

优先使用 CLI 而不是询问用户可以提供的 ID：

```bash
ax organizations list --output json
```

使用 `.organizations[].id` 获取组织 ID。如果返回多个组织，请匹配用户提供的组织名称或要求他们选择。

要发现项目 ID，请在相关空间中列出项目：

```bash
ax projects list --space "{space_name_or_id}" --limit 100 --output json
```

使用匹配项目的 `id`；其 `space_id` 提供了 URL 中所需的空間 ID。该命令接受空間名称或 ID；如果不知道空間，请运行 `ax projects list --limit 100 --output json` 并选择匹配的项目。

**所有路径 ID 必须进行 base64 编码**（字符：`A-Za-z0-9+/=`）。原始数字 ID 生成一个看起来有效的 URL，但会返回 404。如果用户提供数字，请要求他们直接从 Arize 浏览器 URL 复制 ID（`https://app.arize.com/organizations/{org_id}/spaces/{space_id}/…`）。如果您有原始内部 ID（例如 `Organization:1:abC1`），请在插入 URL 之前对其进行 base64 编码。

## URL 模板

基本 URL：`https://app.arize.com`（可用于本地部署时覆盖）

**项目：**
```
{base_url}/organizations/{org_id}/spaces/{space_id}/projects/{project_id}
```

**追踪**（添加 `&selectedSpanId={span_id}` 以突出显示特定跨度）：
```
{base_url}/organizations/{org_id}/spaces/{space_id}/projects/{project_id}?selectedTraceId={trace_id}&queryFilterA=&selectedTab=llmTracing&timeZoneA=America%2FLos_Angeles&startA={start_ms}&endA={end_ms}&envA=tracing&modelType=generative_llm
```

**会话：**
```
{base_url}/organizations/{org_id}/spaces/{space_id}/projects/{project_id}?selectedSessionId={session_id}&queryFilterA=&selectedTab=llmTracing&timeZoneA=America%2FLos_Angeles&startA={start_ms}&endA={end_ms}&envA=tracing&modelType=generative_llm
```

**数据集**（`selectedTab`：`examples` 或 `experiments`）：
```
{base_url}/organizations/{org_id}/spaces/{space_id}/datasets/{dataset_id}?selectedTab=examples
```

**队列列表 / 特定队列：**
```
{base_url}/organizations/{org_id}/spaces/{space_id}/queues
{base_url}/organizations/{org_id}/spaces/{space_id}/queues/{queue_id}
```

**评估器**（省略 `?version=…` 以获取最新版本）：
```
{base_url}/organizations/{org_id}/spaces/{space_id}/evaluators/{evaluator_id}
{base_url}/organizations/{org_id}/spaces/{space_id}/evaluators/{evaluator_id}?version={version_url_encoded}
```
`version` 值必须进行 URL 编码（例如，尾随 `=` → `%3D`）。

**标注配置：**
```
{base_url}/organizations/{org_id}/spaces/{space_id}/annotation-configs
```

## 时间范围

关键：`startA` 和 `endA`（毫秒时间戳）对于追踪/跨度/会话链接**必须**提供 — 省略它们将默认为最后 7 天，如果追踪超出该窗口将显示"无最近数据"。

**优先顺序：**
1. **用户提供的 URL** — 直接提取并重用 `startA`/`endA`。
2. **跨度 `start_time`** — 填充 ±1 天（或 ±1 小时以获得更小的窗口）。
3. **回退** — 最后 90 天（`now - 90d` 到 `now`）。

优先选择小窗口；90 天的窗口加载缓慢。

## 说明

1. 从用户、导出数据、URL 上下文或 CLI 收集 ID。使用 `ax organizations list --output json` 获取 `org_id`；使用 `ax projects list` 获取 `project_id`（如果需要）。
2. 验证所有路径 ID 是否已 base64 编码。
3. 使用上述优先顺序为追踪、跨度和会话链接确定 `startA`/`endA`。
4. 替换到适当的模板，并作为可点击的 markdown 链接呈现。

## 故障排除

| 问题 | 解决方案 |
|---|---|
| "无数据" / 空视图 | 追踪超出时间窗口 — 放宽 `startA`/`endA`（±1h → ±1d → 90d）。 |
| 404 | ID 错误或未 base64。使用 `ax organizations list --output json` 检查 `org_id`，使用 `ax projects list` 检查 `project_id`，并从浏览器 URL 获取 `space_id`。 |
| 跨度未突出显示 | `span_id` 可能属于不同的追踪。与导出的跨度数据进行验证。 |
| `org_id` 未知 | 运行 `ax organizations list --output json` 并使用 `.organizations[].id`。如果 CLI 无法访问组织，请要求用户从他们的 Arize 浏览器 URL 复制。 |

## 相关技能

- **arize-trace**：导出跨度以获取 `trace_id`、`span_id` 和 `start_time`。

## 示例

有关每种链接类型的完整具体 URL 集合，请参阅 [references/EXAMPLES.md](references/EXAMPLES.md)。
