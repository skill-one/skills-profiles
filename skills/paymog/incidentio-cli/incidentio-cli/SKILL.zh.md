---
name: incidentio-cli
description: 调用 `incidentio` 命令行界面来驱动 incident.io API——事件、操作、跟进、告警/告警源/路由、升级与值班排班、目录（类型/条目/资源）、自定义字段、严重性、事件类型/角色/状态/时间戳、状态页面（包括创建和管理公共页面、组件、布局、订阅者、模板）、工作流、用户、团队、API 密钥、心跳、维护窗口和设置。使用公共 Bearer API（OpenAPI 生成的命令）以及从捕获的 HAR 文件、手动精选的内部端点生成的内部仪表板（cookie）命令，并提供 `raw` 逃逸通道用于任何未编码的路径。当任务需要 incident.io 数据或操作时使用，例如“列出我们的事件”、“创建一个事件”、“显示值班排班”、“构建或管理状态页面”、“列出状态页面订阅者”、“调整仪表板设置”或“访问内部仪表板端点”。
---

# incident.io CLI

调用 `incidentio` 二进制文件。真实来源：[`paymog/incidentio-cli`](https://github.com/paymog/incidentio-cli)。

与铁匠的 cookie-replay 不同，incident.io 拥有 **真正的公共 API**，由 Bearer 令牌密钥。`incidentio` 直接与其通信——无需浏览器，无需 cookies。命令是从 incident.io 的官方 OpenAPI 规范生成的（每个资源标签一个），因此每个文档化的端点都可用。API 基址是 `https://api.incident.io`。

## 认证（任何命令前都需要）

Bearer API 密钥。在 **设置 → API 密钥** (`app.incident.io/settings/api-keys`) 处创建；创建时您选择其范围（例如 `incidents.create`），创建后范围固定。

```sh
incidentio auth set <api-key>     # 存储它（chmod 600, ~/.config/incidentio/creds.json）
incidentio auth status            # 显示掩码密钥 + 最后更新时间
incidentio auth logout            # 清除存储的凭证
```

解析顺序：`--api-key <key>` 标志 → `$INCIDENT_API_KEY` → 存储的凭证。对于一次性或 CI，导出 `INCIDENT_API_KEY` 并跳过 `auth set`。

`401`/`403` 表示密钥无效、已撤销或缺少端点所需的范围（例如，使用只读密钥调用 `incidents create`）。在控制台重新检查密钥的范围。

## 使用

```sh
incidentio list [filter]         # 每个命令（可选按子字符串过滤）
incidentio list incidents        # `incidents` 资源的 所有 动词
incidentio <resource> <verb> [flags]
```

命令是两个标记：**`<resource> <verb>`**。输出是格式化的 JSON——管道到 `jq`，或传递 `--raw` 获取未格式化的响应。

### 标志

| 标志 | 含义 |
| --- | --- |
| `--api-key <key>` | 本次调用的 API 密钥（否则 `$INCIDENT_API_KEY` 或存储的） |
| `--<param> <value>` | 路径参数：`--id`，`--user-id`，`--schedule-id`，`--alert-source-config-id` |
| `--query key=value` | 查询参数，可重复（包括括号过滤器——见下文） |
| `--body-file <path>` | 文件中的 JSON 请求体（用于 POST/PUT） |
| `--body-json '<json>'` | 内联 JSON 请求体 |
| `--set a.b=value` | 设置请求体字段，可重复 |
| `--raw` | 打印原始响应，不格式化为 JSON |
| `--auth cookie\|bearer` | (`raw` 仅限) 强制认证模式；否则从路径推断 |

### 括号查询过滤器

列表端点使用括号键（Rails 风格）。将它们原样传递给 `--query`；重复用于多值过滤器。incident.io 的列表过滤器功能强大，但文档中的参数名出现在 `incidentio list <resource>` 输出中。

```sh
# 状态类别为 "live" 的 incidents，严重程度排名 >= 给定严重程度
incidentio incidents list --query 'status_category[one_of]=live' --query 'severity[gte]=<sev-id>'
# 在日期范围内创建（用波浪号分隔）
incidentio incidents list --query 'created_at[date_range]=2026-06-01~2026-06-30'
# 多个模式中的任意一个
incidentio incidents list --query 'mode[one_of]=standard' --query 'mode[one_of]=retrospective'
```

日期是 ISO-8601 UTC (`2026-06-04T00:00:00.000Z`)。对于 "现在" 计算它：
`date -u +%FT%T.000Z` (macOS) 或 `date -u -d '30 days ago' +%FT%T.000Z` (GNU)。

## 命令界面

运行 `incidentio list` 获取权威集（约 324 命令：约 179 个公共 Bearer-API 命令跨 53 个资源，加上约 145 个内部/控制台命令标记 🍪，以及 `raw` 逃生舱）。分组高亮（除非另有说明）：

### Incidents
```sh
incidentio incidents list [--query status[one_of]=<id>] [--query page_size=50]
incidentio incidents show --id <id>
incidentio incidents create --body-json '{"name":"...","severity_id":"...","visibility":"public"}'
incidentio incidents edit --id <id>            # 编辑 incidents 的字段/状态
incidentio incidents import-postmortem-document --id <id>
```

### Actions, follow-ups, attachments
```sh
incidentio actions list --query incident_id=<id>
incidentio follow-ups list --query incident_id=<id>
incidentio follow-ups create --body-json '{"incident_id":"...","content":"..."}'
incidentio follow-ups connect-external-issue --id <id> --body-json '{...}'
incidentio incident-attachments list --query incident_id=<id>
```

### Alerts & alert sources
```sh
incidentio alerts list
incidentio alerts show --id <id>
incidentio alerts resolve --id <id>
incidentio alert-sources list
incidentio alert-routes list
incidentio alert-routes show --id <id>
incidentio alert-routes update --id <id> --body-json '{...}'   # 公共 API，无版本字段
incidentio alert-events create-http --alert-source-config-id <id> --body-json '{...}'
incidentio heartbeat ping --alert-source-config-id <id>   # GET ping

# 带有 incident-template 自定义字段绑定的 alert route（🍪 控制台 API）
# 规则：
# 1. version = current_version + 1（乐观并发——先获取它）。
# 2. 从每个 escalation_config.escalation_targets 条目中省略 `users` 键；
#    GET 负载携带无效的 users 绑定，PUT 会拒绝。API 会恢复它。
# 3. 自定义字段绑定：静态选项 OR 导航表达式引用。
#    静态：     array_value:[{reference:"",value:"<opt-id>",label:"<label>",sort_key:0}]
#    表达式： array_value:[{reference:"expressions[\"<expr-ref>\"]"}]
# 4. 导航表达式（从 Service catalog 属性派生组件数组）：
#    在顶层 `expressions` 数组中声明；在自定义字段中通过引用绑定。
incidentio alert-routes show-route --id <route-id>
incidentio alert-routes update-route --id <route-id> --body-json '{
  "version":4,
  "escalation_config":{"escalation_targets":[
    {"type":"schedule","id":"<sched-id>"}
  ]},
  "incident_template":{
    "custom_fields":[{
      "custom_field_id":"<field-id>",
      "merge_strategy":"first-wins",
      "binding":{"array_value":[{"reference":"","value":"<option-id>","label":"<label>","sort_key":0}]}
    }]
  }}'
# 使用目录导航表达式（自动从 alert Service 派生 Affected Components）：
incidentio alert-routes update-route-expr --id <route-id> --body-json '{
  "version":5,
  "expressions":[{
    "id":"01EXPR001","label":"Affected Components","reference":"affected_components",
    "returns":{"type":"CatalogEntry[\"<component-type-id>\"]","array":true},
    "root_reference":"alert.attributes.<service-alert-attr-id>",
    "operations":[{"operation_type":"navigate",
      "returns":{"type":"CatalogEntry[\"<component-type-id>\"]","array":true},
      "navigate":{"reference":"catalog_attribute[\"components\"]","reference_label":"Components"}}]
  }],
  "incident_template":{
    "custom_fields":[{
      "custom_field_id":"<affected-components-field-id>",
      "merge_strategy":"first-wins",
      "binding":{"array_value":[{"reference":"expressions[\"affected_components\"]"}]}
    }]
  }}'
```

### Escalations & on-call schedules
```sh
incidentio escalations list [--query status=active]
incidentio escalations create --body-json '{...}'
incidentio escalations cancel-escalation --id <id>
incidentio escalation-paths list
incidentio schedules list
incidentio schedules show --id <id>
incidentio schedule-entries list --schedule-id <id>
incidentio schedule-overrides list --schedule-id <id>
incidentio schedule-replicas list --schedule-id <id>
```

### Catalog（服务目录作为代码）
```sh
# 公共 API (Bearer)
incidentio catalog-types list
incidentio catalog-types show --id <type-id>            # 包括 .schema.attributes[].id
incidentio catalog-types create --body-json '{...}'
incidentio catalog-types update-type-schema --id <id> --body-json '{...}'
incidentio catalog-entries list --query catalog_type_id=<id>
incidentio catalog-entries create --body-json '{...}'   # 简单条目
incidentio catalog-entries update --id <id> --body-json '{...}'
incidentio catalog-entries bulk-update-entries --body-json '{...}'
incidentio catalog-resources list

# 带有 attribute_values 的 catalog entries（🍪 控制台 API — 已验证合同）
# 必要的 body：catalog_type_id，name，external_id，attribute_values（无时传递 {}）
# 属性形状：
#   纯文本：       {"<attr-id>":{"value":"some text"}}
#   目录关系： {"<attr-id>":{"array_value":["<entry-id>",...]}}
#   故意清除（仅创建）：{"<attr-id>":{"value":null}}
# 获取属性 ID：incidentio catalog-types show --id <type-id> | jq '.catalog_type.schema.attributes[].id'
incidentio catalog-entries create-entry --body-json '{
  "catalog_type_id":"<type-id>",
  "name":"My Service",
  "external_id":"my-service",
  "attribute_values":{
    "<attr-id>":{"value":"production"},
    "<rel-attr-id>":{"array_value":["<related-entry-id>"]}
  }}'
incidentio catalog-entries update-entry --id <entry-id> --body-json '{
  "name":"My Service",
  "attribute_values":{"<attr-id>":{"value":"staging"}}}'
```

### Config（自定义字段、严重程度、类型、角色、状态、时间戳）
```sh
# 公共 API (Bearer)
incidentio custom-fields list
incidentio custom-fields create --body-json '{...}'      # 基本字段
incidentio custom-field-options list --query custom_field_id=<id>
incidentio severities list
incidentio incident-types list
incidentio incident-roles list
incidentio incident-statuses list
incidentio incident-timestamps list

# 目录支持的 multi-select 自定义字段（🍪 控制台 API — 支持 catalog_type_id，
# field_mode，condition_groups 公共 API 中不可用）
# 必要的 body：name，description，field_type:"multi_select"，catalog_type_id，field_mode，
#   dynamic_options，cannot_be_unset，options，condition_groups
incidentio custom-fields create-catalog-backed --body-json '{
  "name":"Affected Services",
  "description":"Which services are affected by this incident",
  "field_type":"multi_select",
  "catalog_type_id":"<catalog-type-id>",
  "field_mode":"dashboard",
  "dynamic_options":true,
  "cannot_be_unset":false,
  "options":[],
  "condition_groups":[]}'
```

### Status pages
```sh
# 读取（Bearer 公共 API）
incidentio status-pages list
incidentio status-pages show --status-page-id <id>          # 包括 current_structure
incidentio status-page-incidents list --query status_page_id=<id>
incidentio status-page-maintenances list --query status_page_id=<id>

# 管理 page 本身（🍪 内部——公共 API 无法创建 pages/components）
# 简单 page：
incidentio status-pages create --body-json '{"name":"Acme","subpath":"acme","theme":"light"}'
# 目录支持的父 page，自动为每个 catalog entry 生成子 pages：
incidentio status-pages create --body-json '{
  "name":"Acme","subpath":"acme","theme":"light",
  "parent_page_options":{
    "page_type":"parent",
    "split_by_catalog_type_id":"<catalog-type-id>",
    "split_by_component_attribute_id":"<component-attr-id>",
    "sub_pages":[
      {"defined_by_catalog_entry_id":"<entry-id>","name":"Team A","subpath":"team-a"}
    ]
  }}'
# 更新——name，subpath，support_label 都是 ALL required 即使是单字段更改：
incidentio status-pages update --status-page-id <id> --body-json '{"name":"Acme","subpath":"acme","support_label":"Report a problem","allow_search_engine_indexing":false}'
incidentio status-page-components create --body-json '{"name":"API","status_page_id":"<id>"}'
incidentio status-page-components delete --id <component-id>
incidentio status-page-structures create --body-json '{"status_page_id":"<id>","items":[
  {"group":{"name":"Core","display_aggregated_uptime":true,"hidden":false,"components":[
    {"component_id":"<id>","display_uptime":true,"hidden":false}]}},
  {"component":{"component_id":"<id>","display_uptime":true,"hidden":false}}]}'

# Audit subscribers / templates (🍪)
incidentio status-page-subscriptions --query status_page_id=<id>
incidentio status-page-templates --query status_page_id=<id>

# Retrospective status-page incident（Bearer）——批量导入历史 incidents
incidentio status-page-incidents create-status-page-retrospective-incident --body-json '{
  "status_page_id":"<id>",
  "name":"Elevated API latency",
  "idempotency_key":"historical-2021-08-17",
  "updates":[
    {"incident_status":"investigating","message":"Looking into it.","published_at":"2021-08-17T13:28:57Z"},
    {"incident_status":"resolved","message":"Fixed.","published_at":"2021-08-17T14:00:00Z",
     "component_statuses":[{"component_id":"<id>","component_status":"operational"}]}
  ]}'
```

注意：创建/品牌化 page 并定义其组件/布局是 **仅内部**（cookie 会话）；公共 Bearer API 仅用于列出/显示和发布 incidents/maintenance。公共页面的组件是 page 本地对象（创建它们，然后用 `status-page-structures` 放置），不是自定义字段（该模型用于 *内部* pages）。`theme` 是 `light`|`dark`。团队计划允许 **一个** 公共 page（第二个 `create` 返回 `422 超出您的配额）。Logo/favicon/品牌颜色是在控制台中上传的。

对于目录支持的父 pages：`split_by_catalog_type_id` 和 `split_by_component_attribute_id` 识别支持子 pages 的目录类型，以及该类型上的哪个属性指向组件；每个 `sub_pages` 条目将 catalog entry 映射到子页 slug。

### Users, teams, API keys, workflows, secrets
```sh
incidentio users list --query email=<email>
incidentio users show --id <id>
incidentio teams list
incidentio api-keys list
incidentio api-keys rotate --id <id>
# api-keys create/update 接受可选 `comments` 字符串

# Workflows（公共 Bearer CRUD）
incidentio workflows list
incidentio workflows show --id <id>
incidentio workflows create --body-json '{...}'   # 公共形状——见 OpenAPI
incidentio workflows update --id <id> --body-json '{...}'

# Secrets store（公共 Bearer — 优先用于脚本）
# 创建：{name, value, description?, owning_team_ids?}
# 旋转：{value} — 推动版本；value 永不返回（仅返回最后四位字符）
incidentio secrets list [--query team_ids=<id>]
incidentio secrets show --id <id>                 # 包括 versions[] 历史记录
incidentio secrets create --body-json '{"name":"pagerduty_token","value":"..."}'
incidentio secrets rotate --id <id> --body-json '{"value":"new-secret"}'
incidentio secrets update --id <id> --body-json '{"name":"pagerduty_token"}'
incidentio secrets delete --id <id>
```

### Housekeeping
```sh
incidentio utilities identity              # 验证密钥 + 显示 identity
incidentio maintenancewindows list
incidentio ipallowlists show
incidentio telemetry update --id <id> --body-json '{...}'
```

## 控制台 / 内部 API (🍪 — 需要浏览器会话)

这些命中 `app.incident.io/api/*`，**拒绝 API 密钥**（"Cannot use API keys to authenticate to internal APIs"）。它们重放登录的浏览器会话。首先导入一个：

```sh
# devtools → Network → 右键点击任何 /api/ 请求 → Copy as cURL
incidentio auth import '<paste curl>'        # 或: pbpaste | incidentio auth import
incidentio auth set-org 01G9XY4BZ7YGBPJ3K50NB30YXS   # x-incident-organisation-id (如果存在则自动捕获自 curl)
```

然后 `list` 中标记 🍪 的命令可用。亮点——公共 API 无法执行的：

```sh
incidentio saved-views --query context=incidents     # saved filter views
incidentio insights trends --query start_date=2026-06-01 --query end_date=2026-06-30
incidentio insights custom-dashboards
incidentio policies                                 # policy list
incidentio policies update --id <id> --body-json '{...}'  # flip run_on_private_incidents etc.
incidentio secrets list-internal                  # cookie twin of public secrets.*
incidentio workflows triggers                     # alert.updated|attached, scheduled, ...
incidentio workflows show-internal --id <id>      # expands webhook.send signing params
incidentio workflows create-internal --body-json '{
  "trigger":"alert.updated",
  "workflow":{"name":"...","once_for":["alert"],"condition_groups":[],"steps":[],"expressions":[],
    "runs_on_incident_modes":["standard"],"continue_on_step_error":false,
    "runs_on_incidents":"newly_created","state":"draft","private_incident_scope":"none"}}'
incidentio policy-violations
incidentio incident-timelines timeline --incident-timeline <id>            # full timeline
incidentio incident-timelines activity-log --incident-timeline <id>        # activity log
incidentio debriefs incident-debriefs --query incident_id=<id>
incidentio incident-suggestions for-incident --query incident_id=<id>      # AI suggestions
incidentio postmortems templates --query incident_id=<id>
incidentio schedule-reports
incidentio user-preferences
incidentio identity self                  # who am I + scopes (dashboard identity)
```

一个 🍪 命令上出现 `401 "No authorization material"` 表示会话 cookie 没有被识别（错误/过期）— 重新导入一个新鲜的 Copy-as-cURL。组织 ID 解析 `--org` → `$INCIDENT_ORG_ID` → 存储。

## 原始请求与逆向工程新端点

并非每个端点都被编码。`incidentio raw <METHOD> </path>` 会使用存储的凭据打击**任何**端点 — 探测和逆向工程内部路由的快速路径：

```sh
incidentio raw GET  /api/status_pages                    # cookie 推断 (/api/*)
incidentio raw GET  /v2/incidents --query page_size=1    # bearer 推断 (否则)
incidentio raw POST /api/status_pages --body-json '{}'   # 探测：422 需要的字段
incidentio raw PUT  /api/settings/self --body-json '{...}'   # 调整设置
incidentio raw DELETE /api/status_pages/<id> --auth cookie
```

认证被推断 (`/api/*` → cookie，否则 bearer)；使用 `--auth cookie|bearer` 覆盖。
直接在路径中内联任何 ID (`raw` 不做 `:param` 替换)。

**编码新端点（配方）：**
1. 使用空/部分 body 探测：`incidentio raw POST /api/<thing> --body-json '{}'`。
2. 读取 `422 validation_error` — `source.field` / 消息名称指明了必需字段；使用故意无效的枚举值重试以学习允许的值。
3. 向 `src/commands/manual-internal.ts` 添加一个 `Command`（它在加载时合并并存活于 HAR 重新生成），然后 `bun run build`。

## 配方
### 验证你的 API 密钥
```sh
incidentio utilities identity | jq '.identity'
```

### 按最新顺序打开事件
```sh
incidentio incidents list --query 'status_category[one_of]=live' \
  | jq '.incidents[] | {id, name, severity: .severity.name, status: .incident_status.name}'
```

### 分页浏览列表（游标分页）
`list` 响应包含 `pagination_meta.after` 游标；将其作为 `--query after=<cursor>` 回传：
```sh
incidentio incidents list --query page_size=250 > first.json
AFTER=$(jq -r '.pagination_meta.after // empty' first.json)
[ -n "$AFTER" ] && incidentio incidents list --query page_size=250 --query "after=$AFTER" > second.json
```

### 声明事件
```sh
incidentio incidents create --body-json '{
  "name": "API 5xx 峰值",
  "severity_id": "<sev-id>",
  "summary": "边缘 5xx 升高。",
  "visibility": "public"
}' | jq '.incident.id'
```
需要严重性/状态 ID 首先吗？`incidentio severities list` / `incidentio incident-statuses list`。

### 资源有哪些动词？
```sh
incidentio list schedules      # 显示 list/create/show/update/delete + 嵌套 schedule-entries/overrides/replicas
incidentio list catalog-entries   # 显示 create/create-entry (🍪)/update/update-entry (🍪)/...
```

### 创建具有组件关系的目录条目（🍪）
```sh
# 1. 获取目录类型的属性 ID
incidentio catalog-types show --id <type-id> | jq '.catalog_type.schema.attributes[] | {id, name}'

# 2. 使用属性值创建条目
incidentio catalog-entries create-entry --body-json '{
  "catalog_type_id":"<type-id>",
  "name":"payments-service",
  "external_id":"payments-service",
  "attribute_values":{
    "<team-attr-id>":{"array_value":["<team-catalog-entry-id>"]},
    "<tier-attr-id>":{"value":"tier-1"}
  }}'
```

### 更新告警路由以绑定自定义字段（🍪）
```sh
# 1. GET 当前路由 — 捕获版本和 escalation_targets（你需要移除 `users`）
VERSION=$(incidentio alert-routes show-route --id <route-id> | jq '.version')

# 2. PUT 版本+1。两个关键规则：
#    a) version = $VERSION + 1（乐观并发）
#    b) 从每个 escalation_config.escalation_targets 条目中省略 `users`（GET 负载有无效的 `users` 绑定，PUT 会拒绝；API 在 PUT 后会恢复它）
incidentio alert-routes update-route --id <route-id> --body-json '{
  "version":'$((VERSION+1))',
  "name":"My Route",
  "escalation_config":{"escalation_targets":[
    {"type":"schedule","id":"<sched-id>"}
  ]},
  "incident_template":{
    "custom_fields":[{
      "custom_field_id":"<field-id>",
      "merge_strategy":"first-wins",
      "binding":{"array_value":[{"reference":"","value":"<option-id>","label":"P1 - Critical","sort_key":0}]}
    }]
  }}'
```

### 从 alert Service 通过目录导航表达式派生受影响的组件（🍪）

导航表达式允许告警路由通过从告警属性（例如 Service）通过目录关系（例如 Components）自动填充基于目录的自定义字段。

```sh
# 1. 找到你需要 ID：
#    - service-alert-attr-id：告警源属性 ID，用于 Service 字段
#    - component-type-id：Components 的目录类型 ID（incidentio catalog-types list）
#    - affected-components-field-id：事件自定义字段 ID（incidentio custom-fields list）
VERSION=$(incidentio alert-routes show-route --id <route-id> | jq '.version')

# 2. 使用表达式 + expression-reference 绑定更新路由。
#    相同规则：版本+1，从 escalation_targets 中省略 `users`。
incidentio alert-routes update-route-expr --id <route-id> --body-json '{
  "version":'$((VERSION+1))',
  "escalation_config":{"escalation_targets":[{"type":"schedule","id":"<sched-id>"}]},
  "expressions [{
    "id":"<expr-id>",
    "label":"Affected Components",
    "reference":"affected_components",
    "returns":{"type":"CatalogEntry[\"<component-type-id>\"]","array":true},
    "root_reference":"alert.attributes.<service-alert-attr-id>",
    "operations [{
      "operation_type":"navigate",
      "returns":{"type":"CatalogEntry[\"<component-type-id>\"]","array":true},
      "navigate":{"reference":"catalog_attribute[\"components\"]","reference_label":"Components"}
    }]
  }],
  "incident_template":{
    "custom_fields [{
      "custom_field_id":"<affected-components-field-id>",
      "merge_strategy":"first-wins",
      "binding":{"array_value":[{"reference":"expressions[\"affected_components\"]"}]}
    }]
  }}'
# 成功 PUT 后，API 会完整地回显表达式数组。
```

注意：
- `root_reference` 指向存储 Service 目录条目的告警源属性。
- `operations[0].navigate.reference` 是 Service 类型上存储其组件条目的目录属性名称（通过 `incidentio catalog-types show --id <service-type-id>` 验证）。
- 表达式的 `reference` 值成为 `expressions["<reference>"]` 绑定中的键。
- 受影响的组件自定义字段必须是针对组件目录类型的 `multi_select`，通过 `custom-fields create-catalog-backed`（仪表板内部 API）创建。

### 密钥、签名 webhook、告警触发的工作流

```sh
# 列出触发器（🍪）— 包括 alert.updated、alert.attached、scheduled
incidentio workflows triggers | jq '.triggers[] | select(.name|test("alert|scheduled"))'

# 创建告警触发的工作流（🍪）。注意 body 的分割：顶层 `trigger` 字符串 + 嵌套 `workflow` 对象。公共 `workflows create` 使用更扁平的形状。
incidentio workflows create-internal --body-json '{
  "trigger":"alert.updated",
  "workflow":{
    "name":"Alert resolved webhook",
    "once_for":["alert"],
    "condition_groups":[],
    "steps":[{
      "id":"step1",
      "name":"webhook.send",
      "param_bindings":[
        {"value":{"literal":"https://example.com/hook"}},
        {"value":{"literal":"POST"}},
        {"array_value":[{"literal":"Authorization: Bearer {{secrets.my_token}}"}]},
        {"value":{"literal":"{\"ok\":true}"}},
        {"value":{"literal":"<secret-id>"}},
        {"value":{"literal":""}},
        {"value":{"literal":"X-Signature"}}
      ]
    }],
    "expressions":[],
    "runs_on_incident_modes":["standard"],
    "continue_on_step_error":false,
    "runs_on_incidents":"newly_created",
    "state":"draft",
    "private_incident_scope":"none"
  }}'

# webhook.send 参数顺序（来自 show-internal）：endpoint、method、headers
# (TemplatedText plain_single_line_with_secrets)、body、signing_secret（类型 Secret）、
# generated_signing_secret、signature_header_name（HMAC-SHA256）。
# 当你有 Bearer 密钥时，优先使用公共 `secrets create` 创建签名密钥。
```

### 将策略纳入私有事件（🍪）

```sh
# GET 第一次 — subjects/operations 以展开的对象形式返回
incidentio policies | jq '.policies[] | {id,name,run_on_private_incidents}'

# PUT 写形状不同：subject/operation 是裸字符串；follow_up 需要due_date_config
incidentio policies update --id <id> --body-json '{
  "enabled":true,
  "name":"...",
  "description":"...",
  "policy_type":"follow_up",
  "conditions":[{"conditions":[{"subject":"incident.severity","operation":"gte",
    "param_bindings":[{"value":{"literal":"<sev-id>"}}]}]}],
  "requirements":{"conditions":[{"conditions":[{"subject":"follow_up.status","operation":"not_one_of",
    "param_bindings":[{"array_value":[{"literal":"outstanding"}]}]}]}]},
  "run_on_private_incidents":true,
  "due_date_config":{"incident_timestamp_id":"<ts-id>","days":{"value":{"literal":"30"}},
    "calculation_type":"seven_days"}
}'
```

## 重新生成命令目录

命令位于 `src/commands/generated.ts`，由 incident.io 的每个标签 OpenAPI 规范生成（实时从 `docs.incident.io` 获取）：

```sh
bun run codegen
```

生成器从 `docs.incident.io/llms.txt` 发现 REST 标签集，获取每个 `/openapi/tags/<tag>.json`，为每个操作派生 `<resource> <verb>` 名称，并解决冲突（例如 `catalog-types update-type` vs `update-type-schema`；`heartbeat ping` vs `ping-post`）。重新生成后，重新构建 (`bun run build`)。

仪表板/内部命令通过 `bun run codegen:har <a.har> [b.har ...]` 从捕获的浏览器 HAR(s) 生成。它采集 GET **和** 写入端点（POST→`create`，PUT/PATCH→`update`，DELETE→`delete`），模板 ULID/Slack ID 到 `:param`，丢弃公共 Bearer API 已经覆盖的任何内容，并**覆盖** `generated-internal.ts` — 因此在单个调用中传递**所有**你想表示的 HAR（例如 `app.incident.io.har app.incident.io2.har app.incident.io3.har`）。手动验证的内部端点（例如 status-page create/update/components/structures）不在任何 HAR 中出现，位于 `src/commands/manual-internal.ts`，在加载时合并，因此它们在重新生成时存活。

## 常见问题

### `not authenticated`
未在标志、环境或存储中找到密钥。运行 `incidentio auth set <key>` 或 `export INCIDENT_API_KEY=<key>`。

### `HTTP 401` / `HTTP 403`（公共/Bearer 命令）
密钥无效/过期，或缺少端点所需的范围（例如，一个只读密钥调用写入动词）。在 **设置 → API 密钥** 中检查密钥的范围；范围在创建时固定 — 如果需要更多，请轮换或创建新密钥。

### `needs a browser session` / `401 "No authorization material"`（🍪 仪表板命令）
仪表板命令 (`app.incident.io/api/*`) 拒绝 API 密钥。它们需要一个登录的浏览器会话：通过 `incidentio auth import <curl>`（从 `app.incident.io` 复制为 cURL）重新导入，并确保组织 ID 已设置（`auth set-org` 或 `--org`）。Chrome/Brave 的 HAR 通常会移除 cookie — 使用 Copy-as-cURL。

### `HTTP 422` 带有验证消息
body/query 形状不正确（缺少必需字段、无效枚举、类型错误）。错误负载命名了冒犯性的 `source.field` — 修复 `--body-json`/`--query`/`--set` 值。

### `HTTP 429`
速率限制（默认每分钟 1200 个请求/密钥）。错误负载包括 `rate_limit.retry_after`。稍作等待后重试；不要猛击。

### `unknown command`
命令是 `<resource> <verb>`。运行 `incidentio list <resource>` 查看确切的动词。如果你只输入了资源，CLI 会建议其动词。CRUD 动词被折叠 (`incidents list/create/show/update/delete`)；非 CRUD 动作保留其名称 (`incidents edit`，`escalations cancel-escalation`，`catalog-entries bulk-update-entries`)。

### 缺失端点
端点不在生成目录中。重新运行 `bun run codegen` 以获取新发布的 incident.io 端点，然后重新构建。
