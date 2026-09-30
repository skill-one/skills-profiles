---
name: groundcover-cli
description: 调用 `groundcover` Go 命令行界面 (CLI) 来管理 Groundcover 资源（仪表板、监控器、静默规则、连接的应用、通知路由、API 密钥、策略、集成、管道、工作流）并通过查询日志、追踪、指标、k8s 资源清单和 k8s 事件来解答生产环境可观测性问题。当任务需要针对 Groundcover API 进行认证调用，或用户在调试生产问题时询问“为什么 X 在生产环境中报错”、“显示 Y 服务的日志”、“Z 的 p99 延迟是多少”、“哪些 Pod 在 crashlooping”、“搜索慢请求的追踪”、“命名空间 N 有任何 k8s 事件吗”、“服务 S 是否在接收流量”、“列出 Groundcover 监控器”、“创建静默规则”、“更新通知路由”、“调用 Groundcover 端点”时，均可使用。该工具涵盖了必要的环境变量、基于 SDK 的命令与原始命令的区分，以及针对日志/追踪/指标/k8s 的具体请求体模板，确保 CLI 可在任何地方被驱动使用。
---

# Groundcover CLI

调用 `groundcover` 二进制文件（通过 `brew install paymog/tap/groundcover` 安装）。真实来源是 [`paymog/groundcover-cli`](https://github.com/paymog/groundcover-cli)。

## 认证（任何命令前必须先执行）

```sh
export GROUNDCOVER_API_KEY=gcsa_...   # 必须是服务账户密钥
```

**密钥必须是服务账户密钥：前缀 `gcsa_`，正好 40 个字符。** 任何其他内容都会以清晰的错误消息被拒绝 — `Invalid token prefix. Expected 'gcsa_'` 或 `Invalid token length (N, expected 40)`。不要混淆密钥类型：
- `gcsa_…` — **服务账户** 密钥。这是查询/CRUD 命令需要的。
- `gcik_…` — **摄取** 密钥（数据推送）。不会验证 API；类型错误。

使用正确格式化的 `gcsa_` 密钥时出现 401 错误，表示该密钥属于**不同的租户**，而不是您正在查询的租户。

如果您手头没有 `gcsa_` 密钥，可以使用 `groundcover service-accounts create` 使用一个有效的密钥创建一个，然后 `export GROUNDCOVER_API_KEY=gcsa_…` 用于会话。

内置默认值：
- `--base-url https://api.groundcover.com`
- `--backend-id groundcover`

没有租户 UUID 默认值 — 设置 `--tenant-uuid` / `GROUNDCOVER_TENANT_UUID` 在非 grafana `raw …` 透传调用中发送 `X-Tenant-UUID` 头（用于跨租户访问）。嵌入的 Grafana `raw grafana …` 端点忽略它（见下文 Grafana 部分）。

`raw grafana …` 命令完全**不使用** `gcsa_` 密钥 — 它们需要一个 Grafana 服务账户密钥 (`glsa_…`)。设置 `GROUNDCOVER_GRAFANA_SERVICE_ACCOUNT_TOKEN` / `--grafana-token`。

覆盖环境变量：`GROUNDCOVER_BACKEND_ID`、`GROUNDCOVER_TENANT_UUID`、`GROUNDCOVER_GRAFANA_SERVICE_ACCOUNT_TOKEN`、`GROUNDCOVER_BASE_URL`（或 `GC_*` 等价物）。具有相同名称的标志与 `--api-key`、`--backend-id`、`--tenant-uuid`、`--grafana-token`、`--base-url` 标志相同。

### 存储的配置文件（环境变量的替代方案）

而不是每次会话都导出 `GROUNDCOVER_API_KEY`，凭据可以保存在命名的配置文件中。API 密钥存储在操作系统密钥环中；元数据（后端 ID、基本 URL、租户 UUID）存储在 `~/.config/groundcover/profiles.yaml` 中。

```sh
groundcover auth login [name] --backend-id <id>   # 提示输入密钥（或 --key）；保存前验证
groundcover auth list                              # * 标记默认值
groundcover auth default <name>                    # 更改默认值
groundcover --profile <name> <command>             # 对一个命令使用配置文件
groundcover auth status                            # 显示解析的来源
groundcover auth token                             # 打印解析的密钥
groundcover auth logout <name> [-f]
```

优先级：`--api-key`/`GROUNDCOVER_API_KEY` 环境变量 → `--profile <name>` → 默认配置文件。显式密钥加上 `--profile` 会被拒绝为歧义。`GROUNDCOVER_PROFILE` 通过环境变量设置配置文件。

其他全局标志：`--timeout`（默认 30 秒）、`--raw`（不要重新格式化 JSON 响应）。

## 两个界面

| 界面 | 何时使用 |
|------|---------|
| **SDK 支持** (`groundcover <resource> <verb>`) | 首选。稳定的合约，带类型的请求体。 |
| **原始 HAR 源生** (`groundcover raw …`) | SDK 中缺少端点，或者您需要 SDK 缺少的运行器功能（见下文）。 |

始终首先尝试 SDK 形式。

### 原始命令提供 SDK 无法提供的功能

- `--set dotted.path=value` — 在请求体上执行深度合并覆盖
- `--query key=value`（可重复） — 任意查询字符串覆盖
- 内置默认请求体从 Webapp HAR 捕获（SDK 需要显式 `--body-file`/`--body-json`）
- 当您设置 `--tenant-uuid` / `GROUNDCOVER_TENANT_UUID` 时，在非 grafana 原始调用中发送 `X-Tenant-UUID`（用于跨租户访问；SDK 传输否则从 API 密钥派生租户）。Grafana `raw grafana …` 命令不使用它 — 它们使用 `glsa_` 令牌进行身份验证。
- `groundcover raw list` 以发现所有捕获的端点

两个界面都支持 `--body-file`（json/yaml）、`--body-json` 和 `--raw` 输出。

### 仅限原始的端点（SDK 尚无命令）

对于这些，请使用 `groundcover raw …`；SDK 有父资源但没有下钻：

- **日志**：`filters`、`velocity`（SDK 仅 `search`）
- **跟踪**：`attributes`、`details`、`errors`、`filters`、`insights`、`latencies`、`requests`、`values-distribution`（SDK 仅 `search`）
- **指标**：`cardinality`、`cardinality-graph`、`discovery`、`labels-cardinality`、`query-range`、`resources errors|latencies|list|requests`（SDK 有 `query`、`names`、`keys`、`values`）
- **Prometheus**：`prometheus api query`（原始 Prom 透传 — 方便通过 `--query query='up'` 进行 ad-hoc PromQL）
- **Grafana 仪表板**：`grafana search`、`grafana dashboards get|save|delete`、`grafana dashboards permissions get|update`、`grafana dashboards versions|get|restore`、`grafana folders list|get|create|update|delete`、`grafana folders permissions get|update`、`grafana annotations list|create|update|delete`、`grafana prometheus rules`、`grafana datasources label-values`、`grafana ds query`
- **监控下钻**：`instances filters|query|timeline`、`labels keys`、`silences`、`summary filters|query`、`timeline`（SDK 仅 CRUD）
- **k8s 下钻**：`configmaps|cronjob|daemonsets|deployments|jobs|pods|pvcs|replicasets|statefulsets list`、`container info`、`context events`、`namespaces info|list`、`nodes info-with-resources|list|resources|usage top10`、`pod container usage`、`pods status-over-time`、`workloads availability|events|usage top10`、`network connections|cross-az|cross-az-regions|partners|throughput|top-connections`、`events search-time-series`（SDK 仅 `clusters`、`workloads`、`events-search`、`events-over-time`）
- **基础设施**：`infra hosts info-with-resources`
- **资源 / RUM**：`resources apis errors|filters|latencies|list|requests`、`rum sessions filters|query`、`sources list`
- **管道统计**：`pipelines logs current-stats`、`pipelines traces current-stats`（SDK 仅做配置 CRUD）
- **租户 / 计费 / RBAC 读取**：`rbac seatsUsage`、`rbac tenant ai-settings`、`rbac tenant settings`、`backend settings`、`billing method`、`agent token-budgets|token-usage|token-usage history|token-usage tenant`
- **存储管理**：`storage-management get|update --data-type <logs|traces|events|measurements|monitor_instance>` 用于保留、gcQL 异常规则和索引层设置
- **杂项**：`graph`、`graph filters`、`views member`、`views member defaults`、`migrations`、`connectors list org|personal`、`synthetics rules`、`aggregations metrics config|config default`、`integrations data config`

在调用前运行 `groundcover raw list` / `groundcover raw list <group>` 确认确切名称。

## SDK 支持的 CRUD 模式

```sh
groundcover <resource> list   [--query '<filter>']
groundcover <resource> get    <id>
groundcover <resource> create --body-file <file>   # 或 --body-json '<json>'
groundcover <resource> update <id> --body-file <file>
groundcover <resource> delete <id>
```

请求体文件：`.json` 或 `.yaml`。

### 资源（所有遵循上述模式）

- **仪表板** — 还 `archive <id>`、`restore <id>`
- **监控** — `--query 'monitor_name = "cpu"'`
- **静默** — `list --active`
- **定期静默**
- **连接应用** — `--query 'type:slack-webhook'`
- **通知路由** — `--query 'prod'`
- **合成** —
- **密钥** — 还 `hash <id>`
- **工作流**

### 认证 / RBAC

```sh
groundcover api-keys list
groundcover api-keys create --body-file key.json
groundcover service-accounts list
groundcover service-accounts create --body-file sa.json
groundcover ingestion-keys list
groundcover policies list
groundcover policies apply --body-file policy.json
groundcover policies audit-trail <id>
```

### 管道单例（`get` / `create` / `update` / `delete`，无 ID）

```sh
groundcover logs-pipeline get
groundcover metrics-pipeline get
groundcover traces-pipeline get
groundcover metrics-aggregator get
```

### 集成（带类型）

```sh
groundcover integrations list
groundcover integrations describe <type>
groundcover integrations create <type>      --body-file config.json
groundcover integrations update <type> <id> --body-file config.json
```

### 可观察性 / 读取命令（由请求体文件驱动）

```sh
groundcover logs search          --body-file body.json
groundcover traces search        --body-file body.json
groundcover metrics query        --body-file body.json   # PromQL 范围/瞬时
groundcover metrics names        --body-file body.json   # 列出指标名称
groundcover metrics keys         --body-file body.json   # 指标的标签键
groundcover metrics values       --body-file body.json   # 标签的值
groundcover search discovery     --body-file body.json   # 分面/发现
groundcover search keys          --body-file body.json
groundcover search values        --body-file body.json
groundcover k8s clusters         --body-file body.json
groundcover k8s workloads        --body-file body.json
groundcover k8s events-search    --body-file body.json
groundcover k8s events-over-time --body-file body.json
```

管道到 `jq` 以提取字段，或传递 `--raw` 以转储原始响应。

#### 可观察性请求体模板

时间是 RFC 3339 UTC (`2026-05-28T00:00:00Z`)。当前时间不是内置的 — 使用 `date -u` 计算。所有搜索共享相同的形状（`logs search`、`traces search`、`k8s events-search`）：

```json
{
  "start": "2026-05-28T00:00:00Z",
  "end":   "2026-05-28T01:00:00Z",
  "query": "<GCQL>",
  "filters": "",
  "sources": []
}
```

`metrics query`（注意**大写的**字段名 — 这是 API）：
```json
{
  "Promql":    "rate(http_requests_total[5m])",
  "Start":     "2026-05-28T00:00:00Z",
  "End":       "2026-05-28T01:00:00Z",
  "Step":      "60",
  "QueryType": "range",
  "Conditions": []
}
```
使用 `"QueryType": "instant"` 并省略 `Step` 进行点查询。

`k8s workloads` / `k8s clusters`：
```json
{
  "conditions":  [],
  "sources":     [],
  "gcqlFilter":  "namespace = 'prod'",
  "limit":       100
}
```

## 原始命令

```sh
groundcover raw list                          # 列出组
groundcover raw list <group>                  # 列出组中的命令
groundcover raw k8s clusters list
groundcover raw dashboards get --dashboard-id <id>
groundcover raw metrics query-range --body-file body.json
groundcover raw prometheus api query --query query='up'
groundcover raw grafana dashboards get --dashboard-uid <uid>
groundcover raw grafana dashboards save --body-file dashboard.json
groundcover raw grafana folders list
groundcover raw grafana ds query --body-file query.json
```

### 存储管理

管理员可以读取和更新 `logs`、`traces`、`events`、`measurements`（APM）和 `monitor_instance`（监控问题）的生命周期设置：

```sh
groundcover raw storage-management get --data-type logs --raw \
  | jq '{retention,version,cold_move_duration,cold_volume,custom_rules:(.custom_rules // [])}' \
  > storage.json
# 编辑 storage.json，保留每个可写字段和完整的规则列表。
groundcover raw storage-management update --data-type logs --body-file storage.json
```

更新使用乐观并发并替换可写设置文档。始终从 `get` 开始，传递当前 `version`，并保留 `retention`、`cold_move_duration`、`cold_volume` 和完整的 `custom_rules` 列表；省略 `custom_rules` 删除现有规则。成功更新会增加 `version`。每个观察到的自定义规则包含 `name`、`retention` 和 gcQL `filters` 表达式。

### Grafana 原生仪表板

Groundcover 还在 `/grafana` 嵌入了 Grafana。这些**不是** Groundcover 的一流 `dashboards` SDK 资源，因此当您需要原生 Grafana JSON 仪表板、文件夹、权限、注释、数据源支持的变量值或面板查询执行时，请使用 `raw grafana …`。

**认证**：嵌入的 Grafana 背后是一个会话保护的代理，它忽略了 `gcsa_` API 密钥、后端 ID 和租户 UUID。Bearer/`gcsa_` 请求到 `/grafana/api/*` 仅返回约 980KB 的 Grafana SPA `index.html`（HTTP 200、`text/html`），永远不会返回 JSON。这些命令需要一个 Grafana 服务账户密钥 (`glsa_…`)：设置 `GROUNDCOVER_GRAFANA_SERVICE_ACCOUNT_TOKEN`（或 `--grafana-token`）。运行任何 `raw grafana …` 命令而不带它，CLI 会打印完整的设置指南。

**生成令牌**（需要 groundcover 租户管理员）。令牌来自 groundcover 的*官方* CLI (`github.com/groundcover-com/cli`)，不幸的是，它也安装了一个名为 `groundcover` 的二进制文件。其安装程序将其放在 `~/.groundcover/bin/groundcover` 并将此目录添加到您的 PATH 中，之后 `groundcover` 解析为官方 CLI 并隐藏此一个。通过完整路径调用官方二进制文件以避免冲突：
```sh
sh -c "$(curl -fsSL https://groundcover.com/install.sh)"      # 安装到 ~/.groundcover/bin
~/.groundcover/bin/groundcover auth login                     # 认证流程
~/.groundcover/bin/groundcover auth generate-service-account-token   # 打印 glsa_… 一次
export GROUNDCOVER_GRAFANA_SERVICE_ACCOUNT_TOKEN=glsa_...     # 交给这个 CLI
```
要保留这个 CLI 为 `groundcover`，请删除安装程序添加到您的 shell rc 中的 `~/.groundcover/bin` PATH 行。

常见命令：
```sh
groundcover raw grafana search --query query='service slo' --query folderUIDs=general
groundcover raw grafana dashboards get --dashboard-uid streamling-pipeline-slo
groundcover raw grafana dashboards save --body-file dashboard.json
groundcover raw grafana folders list
groundcover raw grafana datasources label-values --datasource-uid <uid> --label project_id --query start=<unix> --query end=<unix>
groundcover raw grafana ds query --query ds_type=prometheus --body-file query.json
```

Grafana 原始命令默认为 `https://app.groundcover.com`（Webapp 主机），而正常 API/SDK 命令默认为 `https://api.groundcover.com`。仅当非标准部署时才传递 `--base-url`。

原始标志：`--body-json`、`--body-file`、`--set dotted.path=value`、`--query key=value`（可重复）、生成的路径标志（例如 `--dashboard-id`）、`--raw`。许多原始命令附带从 Webapp HAR 捕获的默认请求体，因此您可以在没有任何 `--body-*` 的情况下运行它们，并使用 `--set` 覆盖特定字段。

## 配方

### 服务最后一小时的错误日志
```sh
END=$(date -u +%FT%TZ); START=$(date -u -v-1H +%FT%TZ)   # GNU: date -u -d '1 hour ago' +%FT%TZ
jq -n --arg s "$START" --arg e "$END" '{
  start:$s, end:$e,
  query: "service_name = \"api\" AND level = \"error\"",
  filters: "", sources: []
}' | groundcover logs search --body-file /dev/stdin | jq '.[] | {ts:.timestamp, pod:.pod_name, body:(.body|fromjson?)}'
```

> **`logs search` 返回根级别的裸 JSON 数组** — `jq '.[]'`，不是 `.logs[]`。人类可读的消息位于**`body`** 字段中作为 JSON *字符串*（使用 `fromjson` 解析）。有用的顶级字段：`pod_name`、`container_name`、`namespace`、`workload`、`level`（标准化小写 — `error`/`warning`/`debug`，不是 `WARN`/`DEBG` 在 `body` 内部看到），`cluster`、`timestamp`、`trace_id`。

### 工作负载的 p99 延迟（最后 30 分钟，PromQL）
```sh
END=$(date -u +%FT%TZ); START=$(date -u -v-30M +%FT%TZ)
jq -n --arg s "$START" --arg e "$END" '{
  Promql: "histogram_quantile(0.99, sum by (le) (rate(http_request_duration_seconds_bucket{service=\"api\"}[5m])))",
  Start: $s, End: $e, Step: "60", QueryType: "range", Conditions: []
}' | groundcover metrics query --body-file /dev/stdin
```

### 卡死或重启的 Pod
```sh
jq -n '{ conditions: [], sources: [], gcqlFilter: "status != \"Running\"", limit: 200 }' \
  | groundcover k8s workloads --body-file /dev/stdin \
  | jq '.workloads[] | select(.restarts > 0) | {name, namespace, status, restarts}'
```

### 命名空间的近期 k8s 事件
```sh
END=$(date -u +%FT%TZ); START=$(date -u -v-1H +%FT%TZ)
jq -n --arg s "$START" --arg e "$END" '{
  start:$s, end:$e,
  query: "namespace = \"prod\" AND type = \"Warning\"",
  filters: "", sources: []
}' | groundcover k8s events-search --body-file /dev/stdin
```

### 查找慢速 trace，然后转向其日志
```sh
END=$(date -u +%FT%TZ); START=$(date -u -v-30M +%FT%TZ)
jq -n --arg s "$START" --arg e "$END" '{
  start:$s, end:$e,
  query: "service_name = \"api\" AND duration_ms > 1000",
  filters: "", sources: []
}' | groundcover traces search --body-file /dev/stdin \
  | jq -r '.[] | .trace_id' | head -5 \
  | while read tid; do
      jq -n --arg s "$START" --arg e "$END" --arg t "$tid" '{
        start:$s, end:$e, query: ("trace_id = \"" + $t + "\""), filters: "", sources: []
      }' | groundcover logs search --body-file /dev/stdin
    done
```

### 发现某个流上存在哪些标签/字段
```sh
# 哪些指标名称匹配某个前缀？
jq -n '{ prefix: "http_" }' | groundcover metrics names --body-file /dev/stdin

# 某个特定指标有哪些标签？
jq -n '{ metric: "http_request_duration_seconds" }' | groundcover metrics keys --body-file /dev/stdin

# 某个标签有哪些取值？
jq -n '{ metric: "http_request_duration_seconds", key: "service" }' \
  | groundcover metrics values --body-file /dev/stdin
```

### GCQL 快速参考（日志/trace/事件查询）
- 相等：`service_name = "api"`（JSON 内部的双引号 → `\"`）
- 比较：`duration_ms > 1000`, `status_code >= 500`
- 布尔：`AND`, `OR`, `NOT`
- 子串：`message ~ "timeout"`, 正则：`message ~* "^panic:"`
- 成员判断：`level IN ("error", "fatal")` — 仅对**命名字段**有效
- **自由文本短语：** 一个未加修饰的带引号字符串，例如 `container = "my-service" AND "database unavailable"`。`IN(...)` 作为自由文本**无效**（会报错 `freetext 'in(...)' is not supported`）— 应展开为 `level = "error" OR level = "fatal"`。
- **切勿发送空 `query`** — `query: ""` → 500 `pipeline cannot be nil`。始终提供至少一个条件项。
- 空值检查：`trace_id IS NOT NULL`

枚举字段：`search discovery`/`search keys` 很挑剔（discovery 需要 `Limit` + `Type` 且仍可能 400）。可靠的方法是获取一条样例日志并检查 `keys` 和解析后的 `body`。

### 查找并静默某个监控
```sh
groundcover monitors list --query 'monitor_name ~ "ingest"'
groundcover silences create --body-json '{"monitor_id":"<id>","duration_seconds":3600,"reason":"deploy"}'
```

### 导出所有仪表盘
列表字段是 **`uuid`**，而非 `id`（`.id` 为 null）。每个条目还有 `archivedTimestamp` — 跳过已归档的（活跃 = `0001-01-01T00:00:00.000Z`）。
```sh
groundcover dashboards list \
  | jq -r '.[] | select(.archivedTimestamp == "0001-01-01T00:00:00.000Z") | .uuid' \
  | while read id; do groundcover dashboards get "$id" > "dashboards/$id.json"; done
```

### 构建带预填模板变量的仪表盘深度链接
`groundcover dashboards get <uuid>` 返回的变量定义位于 `.preset` 下（一个**JSON 字符串** — 使用 `fromjson` 解析）。查找仪表盘并检查其变量：
```sh
groundcover dashboards list | jq -r '.[] | select(.name|test("prod";"i")) | "\(.uuid)\t\(.name)"'
groundcover dashboards get <uuid> | jq -r '.preset | fromjson | .variables'
# 每个变量: { kind:"list", spec:{ values:{default:["*"]}, datasource:{key,kind,metric}, variableName } }
```
Web 应用将选中的变量值编码在 `variables` **URL 查询参数**中 — 一个 URL 编码的 JSON 对象，键为 `$<variableName>`。每个条目需要 `name`、`key`、`values`（数组；支持如 `myapp*` 的 glob）、`datasource`（通常为 `"metrics"`），以及 `refiner.metric`（来自变量 `datasource.metric` 的源指标）。

**固定你关心的所有变量 — 包括你想设为宽泛的那些。** 你遗漏的任何变量都会回退到仪表盘的*保存默认值*，而这往往不是 `*`（例如硬编码的 `deployment` 哈希，或 `shard: primary`）。要获得真正宽泛的视图，请显式将这些设为 `["*"]`。使用某个标签值前务必确认其存在 — 例如 `app_kubernetes_io_instance` 可能没有纯 `myapp`，只有 `myapp-web-0` 等，因此使用 `myapp*` glob。

使用 jq 构建以确保编码正确：
```sh
VARS=$(jq -cn '{
  "$cluster":{name:"cluster",key:"cluster",values:["example-cluster"],datasource:"metrics",refiner:{metric:"my_metric_total"}},
  "$deployment":{name:"deployment",key:"deployment",values:["*"],datasource:"metrics",refiner:{metric:"my_metric_total"}},
  "$app_kubernetes_io_instance":{name:"app_kubernetes_io_instance",key:"app_kubernetes_io_instance",values:["myapp*"],datasource:"metrics",refiner:{metric:"my_metric_total"}}
}')
ENC=$(jq -rn --arg v "$VARS" '$v|@uri')
echo "https://app.groundcover.com/dashboards?backendId=groundcover&tenantUUID=<your-tenant-uuid>&duration=Last+1+hour&viewId=<uuid>&qb-disable-auto-focus=true&variables=${ENC}"
```
注意：仪表盘通过 `viewId=<uuid>` 打开（而非 `/dashboards/<uuid>` 路径）；`duration` 接受如 `Last+1+hour` / `Last+5+minutes` 的 UI 字符串。

### 通过 raw 进行临时 Prom 查询
```sh
groundcover raw prometheus api query --query query='up{namespace="prod"}'
```

## 构建与编辑仪表盘

仪表盘有趣的部分并非 CRUD 动词（`dashboards get/list/create/update/archive/restore`）— 而是**preset**，整个面板布局都包含在一个字段中。

### Preset 结构

`dashboards get <uuid>` 返回仪表盘，其中 `.preset` 是一个**JSON 字符串**（使用 `fromjson` / `json.loads` 解析；写回前重新序列化为字符串）。结构：

```jsonc
{
  "spec": { "layoutType": "ordered", "crosshairSyncEnabled": true },
  "layout": [ /* 每个顶层项一个条目，放置在 24 列网格上 */ ],
  "widgets": [ /* 实际面板，通过 id 从 layout 中引用 */ ],
  "duration": "Last 6 hours",   // UI 时长字符串
  "variables": [ /* 模板变量，形状与深度链接配方相同 */ ],
  "schemaVersion": 7
}
```

- **`layout`** — 顶层网格布局。每个条目 `{ "id":"A", "h":12, "w":24, "x":0, "y":0, "minH":8 }`。网格宽度为 **24 列**（`w:8` = 三分之一，`w:12` = 一半）；`id` 必须匹配某个 widget 的 `id`。你需手动计算 `y` 以堆叠行 — 没有自动流动。
- **`widgets`** — `{ id, name, type, queries:[{id, expr, dataType:"metrics", editorMode:"editor"}], visualizationConfig:{ type, selectedUnit, ... } }`。`expr` 是带有 `$var` 替换的 PromQL。
- Widget 类型：`time-series`, `stat`, `text`（markdown 在 `content` 中，无查询 — 用于标题/分隔线）, `section`。

### 分区（可折叠组）

分区是一个 widget `{ id, name, type:"section", color, isCollapsed:false }`。其**layout** 条目包含一个 `children` 数组，其中是*相对*定位的面板条目：`{ id, h, w:24, x:0, y:0, children:[ {h,w,x,y,id,minH}, ... ] }`。标题占据顶部约 2 行，因此子项从 `y:2` 开始。

### 更新契约

`dashboards update <uuid>` 请求体**必须**包含 **`currentRevision`**（当前的 `.revisionNumber`）— 这是乐观并发控制。省略它 → `Field validation for 'CurrentRevision' failed on the 'required_if' tag`。在每次成功更新后重新 `get` 以读取递增的 revision，然后再进行下一次写入。

```sh
groundcover dashboards get <uuid> > d.json
# NEW_PRESET 必须是 preset 对象重新序列化为字符串
jq -n --slurpfile d d.json --arg preset "$NEW_PRESET" '{
  name: $d[0].name, viewType: ($d[0].viewType // "explore"),
  status: "active", currentRevision: $d[0].revisionNumber, preset: $preset
}' | groundcover dashboards update <uuid> --body-file /dev/stdin
```

### 验证规则（API 仅说 `Dashboard validation failed`）

更新端点返回一个**不透明**的 `400 {"message":"Dashboard validation failed"}` — 无字段，无违规 widget。遇到它时，**二分查找**：部署最小 preset（一个分区 / 一个面板），然后逐步添加部分直到它破坏。两条非显而易见的规则，每条都会花费真实的二分时间：

1. **Stat widget（`visualizationConfig.type:"stat"`）仅作为扁平的顶层 `layout` 条目验证 — 绝不在分区的 `children[]` 内。** Time-series widget 在两者中都有效。要构建概览 stat 行，将 stat 面板作为扁平顶层项放置（在其上方有一个 `text` 标题 widget），并将 time-series 面板保留在分区中。
2. **分区 `color` 仅接受固定调色板。** 已验证有效：`gray`, `purple`, `teal`。已验证拒绝：`green`, `blue`, `red`, `yellow`, `orange`。

### Stat 面板在滞后指标上显示 "No Results" → 包裹在 `last_over_time` 中

Stat 面板评估为**“现在”的即时查询**。滞后于实时数据的指标会导致该即时窗口为空 → 面板显示 **"No Results"**，尽管在 time-series 面板中它能正常绘制（后者对整个窗口进行范围查询）。从轮询集成拉取的指标（例如云提供商集成如 CloudWatch）通常滞后数分钟，因此直接构建在其上的 stat 面板会显示空白。

修复：在聚合**内部**将选择器包裹在 `last_over_time(<selector>[30m])` 中，使即时评估能够回溯越过陈旧度：

```promql
max(last_over_time(my_metric{...}[30m]))   # 而不是 max(my_metric{...})
```

`*_over_time` 包裹器在 stat 面板中渲染正常（例如一个工作的 `100 * avg_over_time((...)[7d:5m])` 正常运行时间 stat）。集群内实时抓取（~1s 新鲜）的指标不需要它。

### 无 UI 验证仪表盘

如果无头浏览器遇到 Groundcover 的 SSO 墙（无会话），则无法通过截图验证。改用 API 验证：
- **每个查询都返回数据：** 拉取已部署的 preset，将具体值替换到每个 `expr` 中（`$var` → 真实标签值；通配符变量 → `=~".+"` 正则），并将其作为**范围**查询通过 `metrics query` 运行。使用窗口 ≥ 指标的发布节奏（稀疏集成指标可能仅每隔几分钟发布一次）。
- **几何：** 断言两个 layout 矩形不重叠，且每个 `x+w ≤ 24`（顶层条目和每个分区的 `children`）。
- **注意：** CLI 无法可靠运行即时查询（见常见问题），因此你无法从 CLI 复现 stat-panel 即时路径 — 根据陈旧度 + 范围数据进行推理。

### 轮询集成指标（例如 CloudWatch）：标签方案陷阱

从轮询云集成摄入的指标与集群内 exporter 指标在某些方面有所不同，这在构建仪表盘时会造成困扰：
- **它们滞后于实时**（见上述 stat-panel 说明）— 是分钟而非秒。
- **它们通常被乘以某个 `stat` 维度**（`stat=average/maximum/minimum`）— 每个序列出现 3 次。始终过滤到你想要的那个（例如 `stat="average"`），否则聚合会重复/三重计数。
- **env/scope 标签是集成命名的**，而非干净的 `env`。如果同一资源*也*被集群内 exporter 覆盖，两个系列对于同一概念携带**不同的标签键**（例如 `instance_id` vs `instanceid`）。对每个标签方案使用**单独的模板变量**，而不是强迫一个变量跨越两者。

## 生产可观测性分诊流程

当被问及“X 在生产环境中为什么坏了” / “服务 Y 发生了什么”时：

1. **确定时间窗口。** 默认为过去 1 小时。使用 `date -u` 计算 `START`/`END`（参见配方）。
2. **首先查日志。** 使用 `groundcover logs search`，配合 `service_name` 和 `level = "error"` 的 GCQL 过滤。成本低且通常能解答问题。
3. **如果延迟/慢速则查 trace。** 使用 `groundcover traces search`，根据 `duration_ms`、`status_code` 或 `service_name` 过滤。获取几个 `trace_id` 并通过 `trace_id = "..."` 转回日志。
4. **使用指标查看随时间变化的形状。** 使用 PromQL 的 `groundcover metrics query` — 错误率、p99、饱和度。图表使用 `range`，点检查使用 `instant`。
5. **如果“它是否在运行”则查 K8s。** 使用 `groundcover k8s workloads` 查看状态/重启；使用 `groundcover k8s events-search` 查看 `Warning` 事件（OOMKilled, FailedScheduling, BackOff）。
6. **不知道字段名称？** 使用 `groundcover search discovery`、`metrics names`、`metrics keys`、`metrics values` 进行枚举。
7. **需要在事件期间静默嘈杂的警报吗？** `groundcover monitors list --query …` → `groundcover silences create`。

## 不确定哪个命令存在时

1. 检查上述资源列表。
2. `groundcover --help` 和 `groundcover <resource> --help`。
3. 对于 raw：`groundcover raw list`，然后 `groundcover raw list <group>`。

## 常见问题

### `401 Unauthorized`、token 前缀/长度错误或空结果
- `Invalid token prefix` / `Invalid token length` → 密钥不是 `gcsa_` 服务账户密钥（见**Auth**）。`gcik_` 摄入密钥是常见错误。
- 看似有效的 `gcsa_` 密钥返回 `401` → 该密钥属于**不同的租户**。对于其他租户，也设置 `GROUNDCOVER_TENANT_UUID` 和（如果适用）`GROUNDCOVER_BASE_URL`。
- 否则，验证当前 shell 中是否实际导出了该环境变量。

### SDK 命令拒绝请求体
请求体形状偏离了 SDK 契约。使用 `get <id>` 获取现有资源，并以其形状为模板。

### `logs search` / `traces search` / `events-search` 的空结果
几乎总是以下之一：
- 时间窗口错误 / 太窄。`start` 必须在 `end` **之前**，两者均为 RFC 3339 UTC。
- GCQL 字段名在该租户中不存在。使用 `search discovery` / `search keys` 进行枚举。
- 查询字符串未转义 — 在 JSON 内部，`service_name = "api"` 变为 `"service_name = \"api\""`。

### `metrics query` 无数据返回但指标存在
- 字段名是**大写字母开头**的（`Promql`, `Start`, `End`, `Step`, `QueryType`）— 小写被 JSON 静默接受但被忽略。
- `Step` 是字符串（`"60"`），而非数字。
- 对于即时查询，设置 `"QueryType": "instant"` 并省略 `Step`。**观察到的注意事项：** 在测试中，CLI `metrics query` 对即时请求体返回 `400 metricsQueryBadRequest`（尝试了所有形状 — `Start`==`End`、`Time`、有/无 `QueryType`），即使指标是新的。当你需要单个当前值时，回退到**范围**查询（`QueryType:"range"` + `Step`）覆盖短窗口并取最后一个点。（真正的即时 PromQL 也可通过 `raw prometheus api query` 访问，但该透传可能指向与 `metrics query` 不同的存储。）
- 解析响应：结果位于 `.data.result // .result`；每个 `values` 条目是 `[unix_ts, "stringvalue"]`。对范围求和：`[.values[][1]] | map(tonumber) | add`；使用 `strftime` 格式化时间戳。

### `logs search` 超时（`context deadline exceeded`）
多话、高吞吐量的工作负载会淹没日志，因此即使 ~60–90 秒窗口内的广泛或单 pod 查询也可能超过期限。修复：
- 始终包含**区分性条件**（短语 + `container`/`pod`），而不仅仅是 pod 本身。
- **缩小窗口**并提高 `--timeout`（例如 `--timeout 120s`）。
- 避免在一个查询中使用大型 `OR` 链 — 分别运行。
- 对于“多频繁 / 随时间变化”的问题，优先使用**`metrics query`** 而非抓取日志。

### `monitors` 编辑与搜索
- `monitors get` / `update` 支持 **YAML** 格式（即使使用 `--raw`）。工作流程：`monitors get <uuid> > mon.yaml`，编辑，`monitors update <uuid> --body-file mon.yaml`。成功的更新会返回 `{"status":202}`（异步应用——重新 `get` 以确认）。
- Slack 应用目标需要同时包含 `connectedApps: [<app-id>]` 和 `connectedAppParams.<app-id>.channels: [{id, name}]`。Webapp 的 PUT 请求是 YAML `text/plain` 格式。SDK ≥ v1.376 编码 `connectedAppParams`；旧版 SDK 会移除它，API 会返回 `400 connectedApps[0]: channels is required for slack-app route params`。
- 监控模型位于 `model.queries[].sqlPipeline.filters.conditions[]` — 每个条件是 `{key, origin: root, type, filters:[{op, value}]}`；自由文本使用 `type: freetext` + `op: phrase_search`。其他设置：`instantRollup`（例如 `1 分钟`）、`thresholds[]`、`evaluationInterval.{interval, pendingFor}`。
- `monitors list --query 'monitor_name ~ "..."'` → 400 `regexp requires a string column type`。使用 `monitor_name = "exact"`，或列出所有并使用 `jq` 过滤。

### 组内找不到的原始命令
该端点未在捕获的 HAR 中。如果存在 SDK 形式，请使用它，或重新生成——重新生成位于 `groundcover-cli` 仓库中（`go run ./scripts/generate-commands.go <har>`）。
