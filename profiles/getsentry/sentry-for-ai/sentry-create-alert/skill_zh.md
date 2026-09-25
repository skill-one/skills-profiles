# 创建 Sentry 消息提醒

通过 Sentry 的工作流引擎 API 创建消息提醒。

**注意：** 此 API 目前处于 **测试版**，可能随时更改。
它是新监控和消息提醒的一部分，可能无法在旧版消息提醒 UI 中查看。

## 在以下情况下调用此技能

- 用户要求“创建 Sentry 消息提醒”或“设置通知”
- 用户希望在问题符合特定条件时通过邮件或通知接收提醒
- 用户提到优先级提醒、降级提醒或工作流自动化
- 用户希望为 Sentry 问题配置 Slack、PagerDuty 或邮件通知

## 前置条件

- 命令行中可用 `curl`
- Sentry 组织授权令牌，具有 `alerts:write` 范围（也接受 `org:admin` 或 `org:write`）

## 第一阶段：收集配置信息

询问用户任何缺失的详细信息：

| 详细信息 | 是否必需 | 示例 |
| --- | --- | --- |
| 组织代码 | 是 | `sentry`, `my-org` |
| 授权令牌 | 是 | `sntryu_...`（需要 `alerts:write` 范围） |
| 区域 | 是（默认：`us`） | `us` → `us.sentry.io`, `de` → `de.sentry.io` |
| 消息提醒名称 | 是 | `"高优先级降级提醒"` |
| 触发事件 | 是 | 哪些问题事件会触发工作流 |
| 条件 | 可选 | 在执行操作之前进行过滤的条件 |
| 操作类型 | 是 | `email`, `slack` 或 `pagerduty` |
| 操作目标 | 是 | 用户邮箱、团队、频道或服务 |

## 第二阶段：查找 ID

使用以下 API 调用来按需将名称解析为 ID。

```bash
API="https://{region}.sentry.io/api/0/organizations/{org}"
AUTH="Authorization: Bearer {token}"

# 通过邮箱查找用户 ID
curl -s "$API/members/" -H "$AUTH" | python3 -c "
import json,sys
for m in json.load(sys.stdin):
  if m.get('email')=='USER_EMAIL' or m.get('user',{}).get('email')=='USER_EMAIL':
    print(m['user']['id']); break"

# 列出团队
curl -s "$API/teams/" -H "$AUTH" | python3 -c "
import json,sys
for t in json.load(sys.stdin):
  print(t['id'], t['slug'])"

# 列出集成（用于 Slack/PagerDuty）
curl -s "$API/integrations/" -H "$AUTH" | python3 -c "
import json,sys
for i in json.load(sys.stdin):
  print(i['id'], i['provider']['key'], i['name'])"
```

## 第三阶段：构建请求数据

### 触发事件

选择哪些问题事件会触发工作流。
必须始终使用 `logicType: "any-short"`。

| 类型 | 触发条件 |
| --- | --- |
| `first_seen_event` | 新问题创建时 |
| `regression_event` | 已解决问题再次出现时 |
| `reappeared_event` | 归档问题重新出现时 |
| `issue_resolved_trigger` | 问题被解决时 |

### 过滤条件

在执行操作之前必须满足的条件。
使用 `logicType: "all"`, `"any-short"`, 或 `"none"`。

**`comparison` 字段是多态的** — 其形状取决于条件 `type`：

| 类型 | `comparison` 格式 | 描述 |
| --- | --- | --- |
| `issue_priority_greater_or_equal` | `75`（纯整数） | 优先级 >= 低(25)/中(50)/高(75) |
| `issue_priority_deescalating` | `true`（纯布尔值） | 优先级低于峰值时 |
| `event_frequency_count` | `{"value": 100, "interval": "1hr"}` | 时间窗口内的事件计数 |
| `event_unique_user_frequency_count` | `{"value": 50, "interval": "1hr"}` | 时间窗口内受影响的用户数 |
| `tagged_event` | `{"key": "level", "match": "eq", "value": "error"}` | 事件标签匹配时 |
| `assigned_to` | `{"targetType": "Member", "targetIdentifier": 123}` | 问题分配给目标时 |
| `level` | `{"level": 40, "match": "gte"}` | 事件级别（致命=50, 错误=40, 警告=30） |
| `age_comparison` | `{"time": "hour", "value": 24, "comparisonType": "older"}` | 问题年龄 |
| `issue_category` | `{"value": 1}` | 类别（1=错误, 6=反馈） |
| `issue_occurrences` | `{"value": 100}` | 总发生次数 |

**时间间隔选项：** `"1min"`, `"5min"`, `"15min"`, `"1hr"`, `"1d"`, `"1w"`, `"30d"`

**标签匹配类型：** `"co"`（包含）, `"nc"`（不包含）, `"eq"`, `"ne"`, `"sw"`（以...开头）, `"ew"`（以...结尾）, `"is"`（设置）, `"ns"`（未设置）

将 `conditionResult` 设置为 `false` 以反转（当条件未满足时触发）。

### 操作

| 类型 | 键配置 |
| --- | --- |
| `email` | `config.targetType`: `"user"` / `"team"` / `"issue_owners"`, `config.targetIdentifier`: `<id>` |
| `slack` | `integrationId`: `<id>`, `config.targetDisplay`: `"#channel-name"` |
| `pagerduty` | `integrationId`: `<id>`, `config.targetDisplay`: `<service_name>`, `data.priority`: `"critical"` |
| `discord` | `integrationId`: `<id>`, `data.tags`: 标签列表 |
| `msteams` | `integrationId`: `<id>`, `config.targetDisplay`: `<channel>` |
| `opsgenie` | `integrationId`: `<id>`, `data.priority`: `"P1"`-`"P5"` |
| `jira` | `integrationId`: `<id>`, `data`: 项目/问题配置 |
| `github` | `integrationId`: `<id>`, `data`: 仓库/问题配置 |

### 完整请求数据结构

```json
{
  "name": "<Alert Name>",
  "enabled": true,
  "environment": null,
  "config": { "frequency": 30 },
  "triggers": {
    "logicType": "any-short",
    "conditions": [
      { "type": "first_seen_event", "comparison": true, "conditionResult": true }
    ],
    "actions": []
  },
  "actionFilters": [{
    "logicType": "all",
    "conditions": [
      { "type": "issue_priority_greater_or_equal", "comparison": 75, "conditionResult": true },
      { "type": "event_frequency_count", "comparison": {"value": 50, "interval": "1hr"}, "conditionResult": true }
    ],
    "actions": [{
      "type": "email",
      "integrationId": null,
      "data": {},
      "config": {
        "targetType": "user",
        "targetIdentifier": "<user_id>",
        "targetDisplay": null
      },
      "status": "active"
    }]
  }]
}
```

`frequency`: 重复通知之间的分钟数。
允许的值：`0`, `5`, `10`, `30`, `60`, `180`, `720`, `1440`。

**结构说明：** `triggers.actions` 始终是 `[]` — 操作位于 `actionFilters[].actions` 内。

## 第四阶段：创建消息提醒

```bash
curl -s -w "\n%{http_code}" -X POST \
  "https://{region}.sentry.io/api/0/organizations/{org}/workflows/" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{payload}'
```

预期 HTTP `201`。响应包含工作流 `id`。

## 第五阶段：验证

确认消息提醒已创建并提供 UI 链接：

```
https://{org_slug}.sentry.io/monitors/alerts/{workflow_id}/
```

如果组织缺少 `workflow-engine-ui` 功能标志，消息提醒将出现在：

```
https://{org_slug}.sentry.io/alerts/rules/
```

## 管理消息提醒

```bash
# 列出所有工作流
curl -s "$API/workflows/" -H "$AUTH"

# 获取一个工作流
curl -s "$API/workflows/{id}/" -H "$AUTH"

# 更新一个工作流
curl -s -X PUT "$API/workflows/{id}/" -H "$AUTH" -H "Content-Type: application/json" -d '{payload}'

# 删除一个工作流
curl -s -X DELETE "$API/workflows/{id}/" -H "$AUTH"
# 预期 204
```

## 故障排除

| 问题 | 解决方案 |
| --- | --- |
| 401 未授权 | 令牌需要 `alerts:write` 范围 |
| 403 禁止 | 令牌必须属于目标组织 |
| 404 未找到 | 检查组织代码和区域（`us` 对比 `de`） |
| 400 错误请求 | 验证 JSON 请求数据结构，检查必需字段 |
| 用户 ID 未找到 | 验证邮箱是否匹配组织的成员 |
