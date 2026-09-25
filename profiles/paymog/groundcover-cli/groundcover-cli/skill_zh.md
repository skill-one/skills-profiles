# Groundcover CLI

调用 `groundcover` 二进制文件（通过 `brew install paymog/tap/groundcover` 安装）。真实来源是 [`paymog/groundcover-cli`](https://github.com/paymog/groundcover-cli)。

## Auth (任何命令之前都需要)

```sh
export GROUNDCOVER_API_KEY=gcsa_...   # 必须是服务账户密钥
```

**密钥必须是服务账户密钥：前缀 `gcsa_`，正好 40 个字符。** 任何其他内容都会以清晰的错误消息拒绝 — `Invalid token prefix. Expected 'gcsa_'` 或 `Invalid token length (N, expected 40)`。不要混淆密钥类型：
- `gcsa_…` — **服务账户** 密钥。这是查询/CRUD 命令需要的。
- `gcik_…` — **摄取** 密钥（数据推送）。不会验证 API；错误类型。

带有正确格式化 `gcsa_` 密钥的 401 错误表示该密钥属于一个**不同的租户**，而不是您正在查询的租户。

如果您没有现成的 `gcsa_` 密钥，请使用 `groundcover service-accounts create` 并使用一个有效的密钥创建一个，然后在会话中 `export GROUNDCOVER_API_KEY=gcsa_…`。

内置默认值：
- `--base-url https://api.groundcover.com`
- `--backend-id groundcover`

没有租户 UUID 默认值 — 设置 `--tenant-uuid` / `GROUNDCOVER_TENANT_UUID` 在非 grafana `raw …` 传递调用中发送 `X-Tenant-UUID` 标头（用于跨租户访问）。嵌入的 Grafana `raw grafana …` 端点忽略它（见下文的 Grafana 部分）。

`raw grafana …` 命令完全**不使用 `gcsa_` 密钥** — 它们需要一个 Grafana 服务账户令牌 (`glsa_…`)。设置 `GROUNDCOVER_GRAFANA_SERVICE_ACCOUNT_TOKEN` / `--grafana-token`。

覆盖环境：`GROUNDCOVER_BACKEND_ID`、`GROUNDCOVER_TENANT_UUID`、`GROUNDCOVER_GRAFANA_SERVICE_ACCOUNT_TOKEN`、`GROUNDCOVER_BASE_URL`（或 `GC_*` 等价物）。具有相同名称的标志与 `--api-key`、`--backend-id`、`--tenant-uuid`、`--grafana-token`、`--base-url` 标志相同。

### 存储配置文件（环境变量的替代方案）

而不是每次会话都导出 `GROUNDCOVER_API_KEY`，凭据可以保存在命名的配置文件中。API 密钥存储在操作系统密钥环中；元数据（后端 ID、基本 URL、租户 UUID）存储在 `~/.config/groundcover/profiles.yaml` 中。

```sh
groundcover auth login [name] --backend-id <id>   # 提示输入密钥（或 --key）；在保存前进行验证
groundcover auth list                              # * 标记默认
groundcover auth default <name>                    # 更改默认值
groundcover --profile <name> <command>             # 为单个命令使用配置文件
groundcover auth status                            # 显示解析的来源
groundcover auth token                             # 打印解析的密钥
groundcover auth logout <name> [-f]
```

优先级：`--api-key`/`GROUNDCOVER_API_KEY` 环境 → `--profile <name>` → 默认配置文件。显式密钥加上 `--profile` 被拒绝为歧义。`GROUNDCOVER_PROFILE` 通过环境设置配置文件。

其他全局标志：`--timeout`（默认 30 秒），`--raw`（不要重新格式化 JSON 响应）。

## 两个表面

| 表面 | 使用时机 |
|------|---------|
| **SDK 支持** (`groundcover <resource> <verb>`) | 首选。稳定的合约，带类型的请求正文。 |
| **原始 HAR 源生** (`groundcover raw …`) | SDK 中缺少端点，或者您需要 SDK 缺少的运行器功能（见下文）。 |

始终首先尝试 SDK 形式。

### 原始提供 SDK 不提供的功能

- `--set dotted.path=value` — 在正文顶部进行深度合并覆盖
- `--query key=value`（可重复） — 任意的查询字符串覆盖
- 内置默认正文从网络应用程序 HAR 捕获（SDK 需要显式的 `--body-file`/`--body-json`）
- 在非 grafana `raw …` 调用中发送 `X-Tenant-UUID`（当您设置 `--tenant-uuid` / `GROUNDCOVER_TENANT_UUID` 时，用于跨租户访问；嵌入的 Grafana `raw grafana …` 端点忽略它（见下文的 Grafana 部分）。
- `groundcover raw list` 以发现每个捕获的端点

两个表面都支持 `--body-file`（json/yaml），`--body-json` 和 `--raw` 输出。

### 仅限原始的端点（SDK 命令尚未提供）

对于任何这些，使用 `groundcover raw …`；SDK 有父资源，但没有下钻：

- **日志**：`filters`，`velocity`（SDK 仅具有 `search`）
- **跟踪**：`attributes`，`details`，`errors`，`filters`，`insights`，`latencies`，`requests`，`values-distribution`（SDK 仅具有 `search`）
- **指标**：`cardinality`，`cardinality-graph`，`discovery`，`labels-cardinality`，`query-range`，`resources errors|latencies|list|requests`（SDK 具有 `query`，`names`，`keys`，`values`）
- **prometheus**：`prometheus api query`（原始 Prom 传递 — 通过 `--query query='up'` 进行 ad-hoc PromQL 非常方便）
- **Grafana 仪表板**：`grafana search`，`grafana dashboards get|save|delete`，`grafana dashboards permissions get|update`，`grafana dashboards versions|get|restore`，`grafana folders list|get|create|update|delete`，`grafana folders permissions get|update`，`grafana annotations list|create|update|delete`，`grafana prometheus rules`，`grafana datasources label-values`，`grafana ds query`
- **监控下钻**：`instances filters|query|timeline`，`labels keys`，`silences`，`summary filters|query`，`timeline`（SDK 仅具有 CRUD）
- **k8s 下钻**：`configmaps|cronjob|daemonsets|deployments|jobs|pods|pvcs|replicasets|statefulsets list`，`container info`，`context events`，`namespaces info|list`，`nodes info-with-resources|list|resources|usage top10`，`pod container usage`，`pods status-over-time`，`workloads availability|events|usage top10`，`network connections|cross-az|cross-az-regions|partners|throughput|top-connections`，`events search-time-series`（SDK 仅具有 `clusters`，`workloads`，`events-search`，`events-over-time`）
- **基础设施**：`infra hosts info-with-resources`
- **资源 / RUM**：`resources apis errors|filters|latencies|list|requests`，`rum sessions filters|query`，`sources list`
- **管道统计**：`pipelines logs current-stats`，`pipelines traces current-stats`（SDK 仅执行配置 CRUD）
- **租户 / 计费 / RBAC 读取**：`rbac seatsUsage`，`rbac tenant ai-settings`，`rbac tenant settings`，`backend settings`，`billing method`，`agent token-budgets|token-usage|token-usage history|token-usage tenant`
- **存储管理**：`storage-management get|update --data-type <logs|traces|events|measurements|monitor_instance>` 用于保留、gcQL 异常规则和索引层设置
- **杂项**：`graph`，`graph filters`，`views member`，`views member defaults`，`migrations`，`connectors list org|personal`，`synthetics rules`，`aggregations metrics config|config default`，`integrations data config`

运行 `groundcover raw list` / `groundcover raw list <group>` 以确认确切名称后再调用。

## SDK 支持的 CRUD 模式

```sh
groundcover <resource> list   [--query '<filter>']
groundcover <resource> get    <id>
groundcover <resource> create --body-file <file>   # 或 --body-json '<json>'
groundcover <resource> update <id> --body-file <file>
groundcover <resource> delete <id>
```

正文文件：`.json` 或 `.yaml`。

### 资源（所有都遵循上述模式）

- **仪表板** — 还 `archive <id>`，`restore <id>`
- **监控** — `--query 'monitor_name ~ "cpu"'`
- **静默** — `list --active`
- **定期静默**
- **连接的应用程序** — `--query 'type:slack-webhook'`
- **通知路由** — `--query 'prod'`
- **合成** —
- **密钥** — 还 `hash <id>`
- **工作流**

### Auth / RBAC

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

### 管道单例 (`get` / `create` / `update` / `delete`，无 ID)

```sh
groundcover logs-pipeline get
groundcover metrics-pipeline get
groundcover traces-pipeline get
groundcover metrics-aggregator get
```

### 集成（带类型的）

```sh
groundcover integrations list
groundcover integrations describe <type>
groundcover integrations create <type>      --body-file config.json
groundcover integrations update <type> <id> --body-file config.json
```

### 可观察性 / 读取命令（正文文件驱动）

```sh
groundcover logs search          --body-file body.json
groundcover traces search        --body-file body.json
groundcover metrics query        --body-file body.json   # PromQL 范围/瞬时
groundcover metrics names        --body-file body.json   # 列出指标名称
groundcover metrics keys         --body-file body.json   # 标签键
groundcover metrics values       --body-file body.json   # 标签值
groundcover search discovery     --body-file body.json   # 细分/发现
groundcover search keys          --body-file body.json
groundcover search values        --body-file body.json
groundcover k8s clusters         --body-file body.json
groundcover k8s workloads        --body-file body.json
groundcover k8s events-search    --body-file body.json
groundcover k8s events-over-time --body-file body.json
```

管道到 `jq` 以提取字段，或传递 `--raw` 以转储原始响应。

#### 可观察性正文模板

时间是 RFC 3339 UTC (`2026-05-28T00:00:00Z`)。墙上当前时间不是内置的 — 使用 `date -u` 计算。所有搜索共享相同的形状 (`logs search`，`traces search`，`k8s events-search`):

```json
{
  "start": "2026-05-28T00:00:00Z",
  "end":   "2026-05-28T01:00:00Z",
  "query": "<GCQL>",
  "filters": "",
  "sources": []
}
```

`metrics query`（注意**大写**的字段名称 — 这是 API）:
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

`k8s workloads` / `k8s clusters`:
```json
{
  "conditions":  [],
  "sources":     [],
  "gcqlFilter":  "namespace = 'prod'",
  "limit":       100
}
```

### GCQL 快速参考（日志/跟踪/事件查询）

- 等于：`service_name = "api"`（JSON 内部的双引号 → `\"`)
- 比较：`duration_ms > 1000`, `status_code >= 500`
- 布尔值：`AND`, `OR`, `NOT`
- 子字符串：`message ~ "timeout"`, 正则表达式：`message ~* "^panic:"`
- 成员资格：`level IN ("error", "fatal")` — 仅适用于**命名字段**。
- **自由文本短语**：一个裸引号字符串，例如 `container = "my-service" AND "database unavailable"`. `IN(...)` **不**作为自由文本有效（错误 `freetext 'in(...)' is not supported`) — 展开为 `level = "error" OR level = "fatal"`.
- **永远不要发送一个空的 `query`** — `query: ""` → 500 `pipeline cannot be nil`. 始终至少提供一个术语。

空值检查：`trace_id IS NOT NULL`

枚举字段：`search discovery`/`search keys` 很复杂（discovery 需要 `Limit` + `Type`，并且可能仍然 400）。可靠的做法是获取一个样本日志并检查 `keys` 和解析的 `body`。

### 查找然后静默监控

```sh
groundcover monitors list --query 'monitor_name ~ "ingest"'
groundcover silences create --body-json '{"monitor_id":"<id>","duration_seconds":3600,"reason":"deploy"}'
```

### 导出每个仪表板

列表字段是**`uuid`**，而不是 `id`（`.id` 是 null）。每个条目还有 `archivedTimestamp` — 跳过已归档的（活动 = `0001-01-01T00:00:00.000Z`）。
```sh
groundcover dashboards list \
  | jq -r '.[] | select(.archivedTimestamp == "0001-01-01T00:00:00.000Z") | .uuid' \
  | while read id; do groundcover dashboards get "$id" > "dashboards/$id.json"; done
```

### 构建仪表板深度链接并预填充模板变量

`groundcover dashboards get <uuid>` 返回的仪表板在 `.preset` 中包含整个面板布局，位于一个字段中。

### Preset 结构

`dashboards get <uuid>` 返回仪表板，`.preset` 作为**JSON 字符串**（使用 `fromjson` / `json.loads`；重新序列化为字符串后写入）。形状：

```jsonc
{
  "spec": { "layoutType": "ordered", "crosshairSyncEnabled": true },
  "layout": [ /* 每个顶级项目一个条目，放置在 24 列网格上 */ ],
  "widgets": [ /* 实际的面板，通过布局中的 id 引用 */ ],
  "duration": "Last 6 hours",   // UI 持续时间字符串
  "variables": [ /* 模板变量，与深度链接配方相同的形状 */ ],
  "schemaVersion": 7
}
```

- **`layout`** — 顶级网格布局。每个条目 `{ "id":"A", "h":12, "w":24, "x":0, "y":0, "minH":8 }`. 网格是 **24 列宽** (`w:8` = 三分之一，`w:12` = 一半); `id` 必须匹配一个面板 `id`。您手动计算 `y` 以堆叠行 — 没有自动流。
- **`widgets`** — `{ id, name, type, queries:[{id, expr, dataType:"metrics", editorMode:"editor"}], visualizationConfig:{ type, selectedUnit, ... } }`. `expr` 是 PromQL，带有 `$var` 替换。
- 面板类型：`time-series`, `stat`, `text`（Markdown 内容，没有查询 — 使用它作为标题/分隔符），`section`.

### Sections（可折叠组）

一个 section 是一个面板 `{ id, name, type:"section", color, isCollapsed:false }`。它的**布局**条目包含一个 `children` 数组，其中包含*相对*定位的面板条目：`{ id, h, w:24, x:0, y:0, children:[ {h,w,x,y,id,minH}, ... ] }`。标题占据顶部约 2 行，因此子项从 `y:2` 开始。

### 更新合同

`dashboards update <uuid>` 正文必须包含**`currentRevision`**（当前的 `.revisionNumber`）— 这是乐观并发。省略它 → `Field validation for 'CurrentRevision' failed on the 'required_if' tag`. 在下一次写入之前，重新 `get` 以读取增加的修订版。

```sh
groundcover dashboards get <uuid> > d.json
# NEW_PRESET 必须是重新序列化为字符串的 preset 对象
jq -n --slurpfile d d.json --arg preset "$NEW_PRESET" '{
  name: $d[0].name, viewType: ($d[0].viewType // "explore"),
  status: "active", currentRevision: $d[0].revisionNumber, preset: $preset
}' | groundcover dashboards update <uuid> --body-file /dev/stdin
```

### 验证规则（API 仅返回 `Dashboard validation failed`）

更新端点返回**不透明** `400 {"message":"Dashboard validation failed"` — 没有字段，没有违规组件。当您遇到它时，**二分法**：部署一个最小的 preset（一个 section / 一个面板），然后逐个添加部分，直到它出错。两个非明显的规则每个都花费了实际的二分法时间：

1. **Stat 面板 (`visualizationConfig.type:"stat"`) 仅作为扁平的顶级 `layout` 条目进行验证 — 永远不要在 section 的 `children[]` 内部。时间序列面板在这两种情况下都有效。要构建一个概览 stat 行，请将 stat 面板作为扁平的顶级条目放置（在上面放置一个 `text` 标题面板），并将时间序列面板保留在 section 中。
2. **Section `color` 仅接受固定的调色板。** 验证有效的：`gray`, `purple`, `teal`。验证被拒绝的：`green`, `blue`, `red`, `yellow`, `orange`.

### Stat 面板读取 "No Results" 在延迟的指标上 → 用 `last_over_time` 包装

Stat 面板在“现在”执行**瞬时查询**。一个延迟的指标在该瞬时窗口为空 → 面板显示 **"No Results"**，即使它在时间序列面板中可以正常绘制（时间序列面板对整个窗口进行范围查询）。从被轮询集成的指标（例如 CloudWatch 等云提供程序集成）拉取的指标通常延迟分钟，因此直接构建的 stat 面板为空。

修复：将选择器包装在 `last_over_time(<selector>[30m])` **在**聚合内，以便瞬时评估可以回溯到过时的：

```promql
max(last_over_time(my_metric{...}[30m])   # NOT  max(my_metric{...})
```

`*_over_time` 包装在 stat 面板中可以正常工作（例如，一个工作的 `100 * avg_over_time((...)[7d:5m])` 运行时间 stat）。集群内指标实时抓取（约 1 秒新鲜）不需要它。

### 无需 UI 验证仪表板

如果头less 浏览器遇到 Groundcover 的 SSO 墙（没有会话），则无法通过屏幕截图验证。通过 API 验证：

- **每个查询返回数据**：拉取部署的 preset，将每个 `expr` 中的具体值替换为 `$var` → 一个真实标签值；通配符变量 → `=~".+"` 正则表达式），并通过 `metrics query` 作为**范围**查询运行它。使用一个窗口 ≥ 指标的发射频率（稀疏集成指标可能每几分钟才发射一次）。

- **几何形状**：断言没有两个布局矩形重叠，并且每个 `x+w ≤ 24`（顶级条目和每个 section 的 `children`）。

**注意**：CLI 无法可靠地运行瞬时查询（见常见问题），因此您无法从 CLI 重现 stat 面板的瞬时路径 — 原因是陈旧加上范围数据。

### 被轮询集成的指标（例如 CloudWatch）：标签方案注意事项

从被轮询云集成拉取的指标与集群内导出器指标不同，在构建仪表板时会咬人：
- **它们延迟实时**（见上文的 stat 面板注释）— 分钟，不是秒。
- **它们通常乘以一个 `stat` 维度** (`stat=average/maximum/minimum`) — 每个系列出现 3×。始终过滤以选择您想要的（例如 `stat="average"`）或聚合会重复计算。
- **环境/范围标签是集成命名的**，而不是干净的 `env`。如果相同的资源也由集群内导出器覆盖，则两个系列携带**不同的标签键**来表示相同的概念（例如 `instance_id` vs `instanceid`）。使用**每个标签方案一个单独的模板变量**，而不是强迫一个变量跨越两者。

## 生产可观察性排错流程

当被问到“为什么生产中的 X 出现故障”/“服务 Y 出现什么情况”：

1. **确定时间窗口。** 默认为最后 1 小时。使用 `date -u` 计算 `START`/`END`（见配方）。
2. **首先查看日志。** `groundcover logs search` 带有 `service_name` 和 `level = "error"` 的 GCQL 过滤器。成本较低，通常可以回答它。
3. **如果延迟/缓慢，则使用跟踪。** `groundcover traces search` 过滤 `duration_ms`，`status_code` 或 `service_name`。获取几个 `trace_id` 并通过 `trace_id = "..."` 回到日志。
4. **使用指标查看随时间变化的形状。** `groundcover metrics query` 带有 PromQL — 错误率，p99，饱和度。使用 `range` 进行图形，`instant` 进行点检查。
5. **如果是“它甚至没有运行”，则使用 K8s。** `groundcover k8s workloads` 查看状态/重启；`groundcover k8s events-search` 查找 `Warning` 事件（OOMKilled，FailedScheduling，BackOff）。
6. **不知道字段名？** `groundcover search discovery`，`metrics names`，`metrics keys`，`metrics values` 以进行枚举。
7. **需要在事件期间在噪音警报期间静默警报？** `groundcover monitors list --query …` → `groundcover silences create`.

## 不确定哪个命令存在

1. 检查上面的资源列表。
2. `groundcover --help` 和 `groundcover <resource> --help`。
3. 对于原始：`groundcover raw list`，然后 `groundcover raw list <group>`。

## 常见问题

### `401 Unauthorized`，密钥前缀/长度错误或空结果
- `Invalid token prefix` / `Invalid token length` → 密钥不是 `gcsa_` 服务账户密钥（见 **Auth**）。`gcik_` 摄取密钥是常见的错误。
- 带有有效外观 `gcsa_` 密钥的 401 → 密钥属于一个**不同的租户**。对于其他租户，也设置 `GROUNDCOVER_TENANT_UUID`，如果适用，则设置 `GROUNDCOVER_BASE_URL`。
- 否则请验证当前 shell 中实际导出了环境变量。

### SDK 命令拒绝正文
正文形状已从 SDK 合约中漂移。使用 `get <id>` 获取现有资源并使用其形状作为模板。

### `logs search` / `traces search` / `events-search` 返回空结果
几乎总是以下之一：
- 时间窗口不正确/太窄。`start` 必须是 **在** `end` 之前，两者都是 RFC 3339 UTC。
- GCQL 字段名在此租户中不存在。使用 `search discovery` / `search keys` 进行枚举。
- 查询字符串未转义 — 在 JSON 内部，`service_name = "api"` 变为 `"service_name = \"api\""`。

### `metrics query` 返回没有数据但指标存在
- 字段名是 **大写** (`Promql`, `Start`, `End`, `Step`, `QueryType`) — 小写被 JSON 捕获，但被忽略。
- `Step` 是一个字符串 (`"60"`), 不是数字。
- 对于瞬时查询设置 `"QueryType": "instant"` 并省略 `Step`。**观察到的例外**：在测试中，CLI `metrics query` 对于瞬时正文（尝试了所有形状 — `Start`==`End`, `Time`, 带有/不带有 `QueryType`）返回 `400 metricsQueryBadRequest`，即使指标是新鲜的。当您需要单个当前值时， fallback 到一个**短窗口的范围查询 (`QueryType:"range"` + `Step**) 并取最后一个点。(**真实的瞬时 PromQL** 也可以通过 `raw prometheus api query` 访问，但该传递可能针对不同的存储）。
- 解析响应：结果位于 `.data.result // .result`; 每个 `values` 条目是 `[unix_ts, "stringvalue"]`。使用 `[.values[][1]] | map(tonumber) | add` 累加范围；使用 `strftime` 格式化时间戳。

### `logs search` 超时 (`context deadline exceeded`)
多话、高流量工作负载淹没日志，因此即使对于大约 60-90 秒的窗口，广泛的或单个节点的查询也可能超过截止日期。修复：
- 始终包含一个**区分性术语**（短语 + `container`/`pod`），而不仅仅是 pod 本身。
- **缩小窗口**并提高 `--timeout`（例如 `--timeout 120s`）。
- 避免在单个查询中使用大型 `OR` 链 — 分别运行它们。
- 对于“频率/随时间”问题，请优先选择 **`metrics query`** 而不是抓取日志。

### `monitors` 编辑和搜索
- `monitors get` / `update` 使用 **YAML**（即使带有 `--raw`）。工作流程：`monitors get <uuid> > mon.yaml`，编辑，`monitors update <uuid> --body-file mon.yaml`。成功的更新返回 `{"status":202}`（异步应用 — 重新 `get` 以确认）。
- Slack 应用程序目标需要**两者** `connectedApps: [<app-id>]` 和 `connectedAppParams.<app-id>.channels: [{id, name}]`。Web 应用程序 PUT 是 YAML `text/plain` 形状。SDK ≥ v1.376 编码 `connectedAppParams`；旧 SDK 会删除它，API 返回 `400 connectedApps[0]: channels is required for slack-app route params`。
- 监控模型位于 `model.queries[].sqlPipeline.filters.conditions[]` 下 — 每个条件是 `{key, origin: root, type, filters:[{op, value}]}`；自由文本使用 `type: freetext` + `op: phrase_search`。其他调整：`instantRollup`（例如 `1 minute`），`thresholds[]`，`evaluationInterval.{interval, pendingFor}`。
- `monitors list --query 'monitor_name ~ "..."'` → 400 `regexp requires a string column type`。使用 `monitor_name = "exact"`，或者列出所有并用 `jq` 过滤。
### 原始命令“找不到”在组内
端点不在捕获的 HAR 中。如果存在 SDK 形式，请使用它，或者重新生成 — 重新生成位于 `groundcover-cli` 仓库中（`go run ./scripts/generate-commands.go <har>`）。
