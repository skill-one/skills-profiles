# Kibana 告警规则

创建、检查、更新和管理 Kibana 告警规则：选择合适的规则类型，编码阈值和分组语义，仅在请求时附加操作，并在用户请求时以只读方式列出或过滤规则以发现现有覆盖范围。

<!-- begin-partial: preamble -->

## 环境配置

此技能通过 `elastic` CLI 执行 Elasticsearch 操作。如果未安装 [`elastic` CLI](https://github.com/elastic/cli#configuration)，请告知用户其用途。不要猜测凭证，直接调用 HTTP API 或尝试其他解决方案。

此技能以 HTTP 简写形式引用操作（例如，`GET /`，`GET /_cat/indices`，`GET /{index}/_mapping`，`GET /{index}/_settings/index.mode`，`POST /_query`）。本文件末尾的 [操作](#operations) 表将每个简写映射到等效的 `elastic` CLI 命令——始终使用 CLI 而不是直接调用 HTTP API。

<!-- end-partial: preamble -->

## 核心概念

规则由三个部分组成：**条件**（`params` + `rule_type_id`）、**计划**（条件检查的频率）和**操作**（可选的连接器，在告警触发时运行）。当条件满足时，规则创建 **告警**；操作通过 **连接器** 传递通知。除非用户明确要求进行通知线路配置，否则不要创建连接器或操作——许多任务只需要定义规则。

必需权限：拥有 Kibana 功能（Stack Rules、Observability、Security 等）上的 `all` 权限以及规则设置上的 `all` 权限。管理连接器需要 Actions 和 Connectors 上的 `all` 权限；`read` 足够将现有连接器作为规则操作附加。

**本地先决条件**：在创建规则之前，在 `kibana.yml` 中配置一个稳定的 `xpack.encryptedSavedObjects.encryptionKey`——它加密规则 API 密钥和连接器密钥。如果未设置，每次重启都会重新生成它并破坏现有规则；集群中的所有 Kibana 节点必须共享相同的密钥。

## 流程

1. **分类任务。** 判断用户是否需要 **创建** 规则、**查找/列出** 规则（只读）、**更新** 现有规则或执行 **生命周期** 变更（启用、禁用、静音、暂缓、删除）。如果用户仅要求显示或列出规则，将请求视为只读——不要创建、更新、启用或删除任何内容。

2. **对于查找/列出任务，合理过滤和分页。** 调用 `GET kbn:/api/alerting/rules/_find` 并使用查询参数缩小结果，而不是列出所有规则：
   - **按标签**：`filter=alert.attributes.tags:"production"`（保存对象属性的 KQL）。
   - **按文本**：使用 `search` 并根据需要设置 `search_fields` 和 `default_search_operator`。
   - **分页**：设置 `per_page` 并在结果可能超过一页时迭代 `page`。
   - **排序**：`sort_field=name` 和 `sort_order=asc` 以获得稳定的列表。

   列出匹配的规则 ID 和名称。如果没有规则匹配，请明确说明——不要编造结果。专门查询告警规则，而不是连接器或流。

3. **对于创建任务，在编写 params 之前选择规则类型。** 将用户的意图匹配到指标/阈值规则类型——而不是日志、异常或不相关的类型：
   - **时间窗口内的数值指标，可选按主机/服务分组** → `.index-threshold` 并使用 `consumer: "stackAlerts"`。
   - **文档计数或 Query DSL 条件** → `.es-query` 并使用 `consumer: "stackAlerts"`。
   - **指标应用中的可观察性指标** → `metrics.alert.threshold` 并使用 `consumer: "metrics"` 或 `"infrastructure"`。

   阅读 [rule-types-reference.md](references/rule-types-reference.md) 获取 param 模板、有效消费者和操作组。当用户指定索引、字段、阈值、持续时间和分组字段时，在 `params` 中明确编码所有四个——不要用连接器或操作替代条件。

4. **正确编码阈值、持续时间和分组。** 这三个维度是独立的：
   - **阈值**：在聚合值上设置 `threshold` 和 `thresholdComparator`。匹配字段尺度——ECS `system.cpu.total.pct` 通常为分数（`0.9` 表示 90%）；仅在字段为 0–100 尺度时使用 `90`。
   - **"持续 N 分钟" 语义**：在 `params` 中设置 `timeWindowSize` 和 `timeWindowUnit`（每次运行评估回溯）。使 `schedule.interval` 与该窗口对齐（例如，均为五分钟），以便在时间间隔不匹配时不会触发短暂峰值。仅在用户需要 N **连续** 匹配运行时添加 `alert_delay: {"active": N}`，而不是单个回溯窗口。
   - **按主机/按实体分组**：对于 `.index-threshold`，设置 `groupBy: "top"`，`termField` 为分组字段（例如，`host.name`），并设置足够大的 `termSize` 以涵盖所有实体（“任何主机”）。不分组时，规则将全局聚合，不会按主机告警。

5. **构建创建负载。** 必填字段：`name`，`rule_type_id`，`consumer`，`schedule`，`params`。可选：`tags`，`enabled`，`actions`，`alert_delay`，`flapping`。使用用户提供的规则 ID（如果提供）在 URL 中；否则让 Kibana 生成一个。

   **示例 params — 任何主机的 CPU 超过 90% 持续 5 分钟，在 `eval-alert-metrics` 上：**

   ```json
   {
     "name": "CPU 超过 90% 持续 5 分钟",
     "rule_type_id": ".index-threshold",
     "consumer": "stackAlerts",
     "schedule": { "interval": "5m" },
     "params": {
       "index": ["eval-alert-metrics"],
       "timeField": "@timestamp",
       "aggType": "avg",
       "aggField": "system.cpu.total.pct",
       "groupBy": "top",
       "termField": "host.name",
       "termSize": 1000,
       "threshold": [0.9],
       "thresholdComparator": ">",
       "timeWindowSize": 5,
       "timeWindowUnit": "m"
     },
     "tags": ["production"]
   }
   ```

   用户仅要求创建规则条件时，省略 `actions`。

6. **创建并确认。** 使用负载调用 `POST kbn:/api/alerting/rule/{id}`。在 **409 冲突** 时，ID 已存在——调用 `GET kbn:/api/alerting/rule/{id}` 检查或选择不同的 ID。创建成功后，调用 `GET kbn:/api/alerting/rule/{id}` 并向用户确认成功，使用实时规则 ID、名称和启用状态——不要在没有在 Kibana 上验证的情况下声称成功。

7. **对于更新任务，先读取后替换。** `rule_type_id` 和 `consumer` 是不可变的。调用 `GET kbn:/api/alerting/rule/{id}`，合并预期更改，然后使用 **完整的** 规则正文调用 `PUT kbn:/api/alerting/rule/{id}`。在 **409 冲突** 时，另一个用户更改了规则——重新获取并重试。设置每个操作的 `frequency` 对象；规则级别的 `notify_when` 和 `throttle` 已弃用。

8. **对于生命周期任务，调用最窄的端点。** 暂时禁用使用 `POST kbn:/api/alerting/rule/{id}/_disable`（规则保留配置）；使用 `POST kbn:/api/alerting/rule/{id}/_enable` 重新启用。使用 `POST kbn:/api/alerting/rule/{id}/_mute_all` 静音所有告警；使用 `POST kbn:/api/alerting/rule/{id}/_unmute_all` 恢复。使用 `POST kbn:/api/alerting/rule/{rule_id}/alert/{alert_id}/_mute` 静音单个活动告警；使用 `POST kbn:/api/alerting/rule/{rule_id}/alert/{alert_id}/_unmute` 恢复。使用 `POST kbn:/api/alerting/rule/{id}/snooze_schedule` 安排暂缓计划；使用 `DELETE kbn:/api/alerting/rule/{ruleId}/snooze_schedule/{scheduleId}` 移除。永久删除使用 `DELETE kbn:/api/alerting/rule/{id}`。当规则因 API 密钥所有权失败时，调用 `POST kbn:/api/alerting/rule/{id}/_update_api_key`。

## 示例

### 创建阈值告警

用户："当任何主机的 CPU 超过 90% 持续 5 分钟时通知我。查询 `eval-alert-metrics`（`system.cpu.total.pct`，按 `host.name` 分组）。使用 ID `eval-cpu-rule` 创建规则。"

1. 选择 `.index-threshold` / `stackAlerts`。
2. 编码分数阈值 `[0.9]`、五分钟 `timeWindowSize`/`timeWindowUnit` 和 `groupBy`/`termField` 为 `host.name`。
3. `POST kbn:/api/alerting/rule/eval-cpu-rule` 并设置 `schedule.interval: "5m"`。省略操作。
4. `GET kbn:/api/alerting/rule/eval-cpu-rule` 并向用户确认。

### 按标签查找规则（只读）

用户："显示所有生产告警规则。"

1. 使用 `filter=alert.attributes.tags:"production"`、合理的 `per_page` 和 `sort_field=name` 调用 `GET kbn:/api/alerting/rules/_find`。
2. 如果 `total` 超过 `per_page`，则分页浏览结果。
3. 仅报告 ID 和名称——不进行任何修改。

### 暂时暂停规则

用户："禁用规则 `abc123` 直到下周一。"

1. `POST kbn:/api/alerting/rule/abc123/_disable`。
2. 之后使用 `POST kbn:/api/alerting/rule/abc123/_enable` 重新启用。

对于跨越多个规则的计划停机，优先使用维护窗口而不是单独禁用或暂缓每个规则。

## 指南

- 在每个操作对象内设置 `frequency`——规则级别的 `notify_when` 和 `throttle` 已弃用。
- `rule_type_id` 和 `consumer` 创建后不可变；删除并重新创建以更改它们。
- 对于非默认 Kibana Space，以 `kbn:/s/<space_id>/api/alerting/` 前缀路径（连接器也是 Space 范围的）。
- 规则操作不能引用来自不同 Space 的连接器——规则及其连接器必须共享一个 Space。
- 为 PagerDuty、Jira 和 ServiceNow 的活动通知操作配对 **恢复** 操作。
- 使用 `alert_delay` 要求连续匹配；使用 flapping 设置抑制不稳定告警。通过 `flapping` 对象的规则级调整自 9.3 起GA；早期版本仅支持 Space 级别的 flapping 设置。
- 使用 `{{{.}}}` 在任何模板字段中调试操作模板——它将整个变量上下文渲染为 JSON，这有助于发现正确的路径，如 `{{context.reason}}` 或 `{{alert.flapping}}`。
- **不要**使用此技能用于安全检测规则：`consumer: "securitySolution"`/`"siem"` 属于专门的安全检测 API（`/api/detection_engine/rules`），其规则类型 ID 和生命周期不同。
- 以一致的方式标记规则（`production`，`staging`，团队名称）以供查找 API 过滤。
- 推荐的最小检查间隔为 `1m`；昂贵规则在服务器运行超时后（默认 `5m`）被取消。

## 常见陷阱

1. **错误的规则类型**——使用日志或 ML 规则进行指标阈值条件。
2. **缺少按实体分组**——全局聚合时用户要求“任何主机”或“按服务”。
3. **阈值尺度不匹配**——分数 CPU 字段的 `90` 与 `0.9`。
4. **持续时间与计划混淆**——一分钟计划与五分钟窗口的行为不同，与两者设置为五分钟的行为都不同。
5. **未请求的操作**——在用户仅要求创建规则时附加连接器。
6. **只读违规**——在用户仅要求列出或过滤时创建或修改规则。
7. **并发更新冲突**——没有最新 GET 的 PUT 返回 409。
8. **导入/导出**——保存对象导入禁用规则并剥离连接器密钥。

## 参考

- [rule-types-reference.md](references/rule-types-reference.md) — 规则类型、params、消费者、操作组
- [connectors-actions-terraform.md](references/connectors-actions-terraform.md) — 操作、工作流、Terraform
- [Kibana 告警 API](https://www.elastic.co/docs/api/doc/kibana/group/endpoint-alerting)
- [告警概念](https://www.elastic.co/docs/explore-analyze/alerting/alerts)
- [规则操作变量](https://www.elastic.co/docs/explore-analyze/alerting/alerts/rule-action-variables)
- [告警生产注意事项](https://www.elastic.co/docs/deploy-manage/production-guidance/kibana-alerting-production-considerations)

## 操作

| HTTP API (简写)                                                  | `elastic` CLI 命令                                                                                                                                                                                            |
| --------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GET kbn:/api/alerting/rules/_find`                                   | `elastic kb alerting get-alerting-rules-find [--filter '<kql>'] [--search '<q>'] [--per-page <n>] [--page <n>] [--sort-field <field>] [--sort-order asc\|desc]`                                                  |
| `POST kbn:/api/alerting/rule/{id}`                                    | `elastic kb alerting post-alerting-rule-id --id '<id>' --name '<name>' --rule-type-id '<type>' --consumer '<consumer>' --schedule '<json>' --params '<json>' [--tags '<json>'] [--actions '<json>'] [--enabled]` |
| `GET kbn:/api/alerting/rule/{id}`                                     | `elastic kb alerting get-alerting-rule-id --id '<id>'`                                                                                                                                                           |
| `PUT kbn:/api/alerting/rule/{id}`                                     | `elastic kb alerting put-alerting-rule-id --id '<id>' --name '<name>' --schedule '<json>' --params '<json>' [--tags '<json>'] [--actions '<json>']`                                                              |
| `DELETE kbn:/api/alerting/rule/{id}`                                  | `elastic kb alerting delete-alerting-rule-id --id '<id>'`                                                                                                                                                        |
| `POST kbn:/api/alerting/rule/{id}/_enable`                            | `elastic kb alerting post-alerting-rule-id-enable --id '<id>'`                                                                                                                                                   |
| `POST kbn:/api/alerting/rule/{id}/_disable`                           | `elastic kb alerting post-alerting-rule-id-disable --id '<id>' [--untrack]`                                                                                                                                      |
| `POST kbn:/api/alerting/rule/{id}/_mute_all`                          | `elastic kb alerting post-alerting-rule-id-mute-all --id '<id>'`                                                                                                                                                 |
| `POST kbn:/api/alerting/rule/{id}/_unmute_all`                        | `elastic kb alerting post-alerting-rule-id-unmute-all --id '<id>'`                                                                                                                                               |
| `POST kbn:/api/alerting/rule/{id}/_update_api_key`                    | `elastic kb alerting post-alerting-rule-id-update-api-key --id '<id>'`                                                                                                                                           |
| `POST kbn:/api/alerting/rule/{rule_id}/alert/{alert_id}/_mute`        | `elastic kb alerting post-alerting-rule-rule-id-alert-alert-id-mute --rule-id '<rule_id>' --alert-id '<alert_id>'`                                                                                               |
| `POST kbn:/api/alerting/rule/{rule_id}/alert/{alert_id}/_unmute`      | `elastic kb alerting post-alerting-rule-rule-id-alert-alert-id-unmute --rule-id '<rule_id>' --alert-id '<alert_id>'`                                                                                             |
| `POST kbn:/api/alerting/rule/{id}/snooze_schedule`                    | `elastic kb alerting post-alerting-rule-id-snooze-schedule --id '<id>' --schedule '<json>'`                                                                                                                      |
| `DELETE kbn:/api/alerting/rule/{ruleId}/snooze_schedule/{scheduleId}` | `elastic kb alerting delete-alerting-rule-ruleid-snooze-schedule-scheduleid --rule-id '<ruleId>' --schedule-id '<scheduleId>'`                                                                                   |
