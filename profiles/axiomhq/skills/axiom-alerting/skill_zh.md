# Axiom告警

您负责Axiom端到端的告警管理：包括路由器（notifiers）和检测器（monitors）。

## API概览

基础URL：`https://api.axiom.co/v2/`，使用来自`.axiom.toml`（项目根目录或`~/.axiom.toml`）的Bearer token认证。

### 监测器 (`/v2/monitors`)

| 操作 | 方法 | 路径 |
|------|------|------|
| 列出 | GET | `/v2/monitors` |
| 获取 | GET | `/v2/monitors/{id}` |
| 历史记录 | GET | `/v2/monitors/{id}/history` |
| 创建 | POST | `/v2/monitors` |
| 更新 | PUT | `/v2/monitors/{id}` |
| 删除 | DELETE | `/v2/monitors/{id}` |

### 路由器 (`/v2/notifiers`)

| 操作 | 方法 | 路径 |
|------|------|------|
| 列出 | GET | `/v2/notifiers` |
| 获取 | GET | `/v2/notifiers/{id}` |
| 创建 | POST | `/v2/notifiers` |
| 更新 | PUT | `/v2/notifiers/{id}` |
| 删除 | DELETE | `/v2/notifiers/{id}` |

## 前置条件

1. 运行`scripts/setup`
2. 确保`.axiom.toml`中包含部署配置：

```toml
[deployments.prod]
url = "https://api.axiom.co"
token = "xaat-your-token"
org_id = "your-org-id"
```

## 脚本

核心脚本：
- `scripts/axiom-api <部署> <方法> <路径> [body]`

监测器脚本：
- `scripts/monitor-list <部署> [--json]`
- `scripts/monitor-get <部署> <id>`
- `scripts/monitor-history <部署> <id> <开始时间> <结束时间>`
- `scripts/monitor-create <部署> <json文件>`
- `scripts/monitor-update <部署> <id> <json文件>`
- `scripts/monitor-delete <部署> <id>`

路由器脚本：
- `scripts/notifier-list <部署> [--json]`
- `scripts/notifier-get <部署> <id>`
- `scripts/notifier-create <部署> <json文件>`
- `scripts/notifier-update <部署> <id> <json文件>`
- `scripts/notifier-delete <部署> <id>`

## 推荐工作流程

1. 首先创建路由器。
2. 创建监测器并设置`notifierIds`。
3. 使用`monitor-history`验证监测器行为。
4. 迭代监测器阈值和调度。

## 端到端告警工作流程

1. 运行`scripts/setup`。
2. 使用`scripts/notifier-list <部署>`列出现有路由器，如果合适则重用一个。
3. 如果没有合适的路由器，使用`scripts/notifier-create`创建一个。
4. 使用关联的`notifierIds`创建或更新监测器。
5. 使用`scripts/monitor-history <部署> <id> <开始时间> <结束时间>`进行验证。
6. 如果行为嘈杂或静默，调整`threshold`、`rangeMinutes`、`intervalMinutes`和N-of-M触发字段。
7. 每次更改后重新检查历史记录。

## 最佳实践

- 每个路由器配置一个通道。
- 对于邮件路由器，使用`emails`（而不是`recipients`）作为有效载荷。
- 对于嘈杂信号，优先使用`triggerAfterNPositiveResults`/`triggerFromNRuns`。
- 在监测器查询中使用显式的`bin()`；避免使用`bin_auto()`进行告警逻辑。
- 对于基于指标的监测器，优先使用`mplQuery`进行定义；API响应可能同时包含`aplQuery`和`mplQuery`。

## 监测器类型和操作符

监测器类型：
- `Threshold`
- `MatchEvent`
- `AnomalyDetection`

操作符：
- `Above`
- `Below`
- `AboveOrEqual`
- `BelowOrEqual`
- `AboveOrBelow`

## 监测器字段参考

核心字段：
- `name`：可读的监测器名称。
- `type`：`Threshold`、`MatchEvent`或`AnomalyDetection`。
- `aplQuery` / `mplQuery`：监测器评估的查询。
- `notifierIds`：通知的路由器ID数组。
- `disabled`：监测器是否禁用。
- `disabledUntil`：可选的时间戳，用于临时禁用/静音。
- `description`：可选的监测器描述。

阈值和评估字段：
- `operator`：阈值比较操作符。
- `threshold`：数值阈值。
- `rangeMinutes`：查询评估窗口（分钟）。
- `intervalMinutes`：评估频率（分钟）。
- `alertOnNoData`：是否应触发无数据告警。
- `triggerAfterNPositiveResults`：触发前所需的正评估次数。
- `triggerFromNRuns`：用于N-of-M逻辑考虑的总评估次数。

高级行为字段：
- `resolvable`：是否可以自动解决告警。
- `notifyByGroup`：按组键/值结果通知。
- `notifyEveryRun`：每次正评估都通知。
- `skipResolved`：跳过已解决的通知。
- `secondDelay`：延迟（秒）以容忍迟到数据。

类型特定字段：
- `columnName`：某些异常/值异常监测器使用的字段。

## 最小有效监测器示例

阈值：

```json
{
  "name": "高错误计数",
  "type": "Threshold",
  "aplQuery": "['logs'] | where status >= 500 | summarize count()",
  "operator": "Above",
  "threshold": 100,
  "rangeMinutes": 5,
  "intervalMinutes": 5,
  "notifierIds": ["notifier-id"],
  "triggerAfterNPositiveResults": 2,
  "triggerFromNRuns": 3,
  "disabled": false
}
```

匹配事件：

```json
{
  "name": "错误事件匹配",
  "type": "MatchEvent",
  "aplQuery": "['logs'] | where level == 'error'",
  "rangeMinutes": 5,
  "intervalMinutes": 5,
  "notifierIds": ["notifier-id"],
  "disabled": false
}
```

异常检测：

```json
{
  "name": "CPU异常",
  "type": "AnomalyDetection",
  "aplQuery": "['metrics'] | summarize avg(cpu_usage)",
  "columnName": "cpu_usage",
  "operator": "AboveOrBelow",
  "rangeMinutes": 5,
  "intervalMinutes": 5,
  "notifierIds": ["notifier-id"],
  "disabled": false
}
```

## 最小有效路由器示例

邮件：

```json
{
  "name": "Oncall邮件",
  "properties": {
    "email": {
      "emails": ["oncall@example.com"]
    }
  }
}
```

Slack：

```json
{
  "name": "Oncall Slack",
  "properties": {
    "slack": {
      "slackUrl": "https://hooks.slack.com/services/T.../B.../XXX"
    }
  }
}
```

自定义webhook：

```json
{
  "name": "Oncall自定义Webhook",
  "properties": {
    "customWebhook": {
      "url": "https://api.example.com/alerts",
      "body": "{\"action\":\"{{.Action}}\",\"monitorID\":\"{{.MonitorID}}\"}"
    }
  }
}
```

## 故障排除

`401 Unauthorized`：
- 原因：无效或过期的token。
- 解决方法：
  - 在`~/.axiom.toml`中验证token。
  - 重新运行`scripts/setup`并重试：
    - `scripts/notifier-list <部署>`

`403 Forbidden`：
- 原因：token缺少必要权限。
- 解决方法：
  - 创建/分配用于监测器/路由器管理和数据集查询访问的token范围。
  - 重试：
    - `scripts/monitor-list <部署>`

`404 Not Found`在获取/更新/删除时：
- 原因：错误的监测器/路由器ID或错误的部署/组织。
- 解决方法：
  - 确认`.axiom.toml`中的部署。
  - 重新列出对象并使用精确的ID：
    - `scripts/monitor-list <部署> --json`
    - `scripts/notifier-list <部署> --json`

`400 Bad Request`在路由器创建/更新时：
- 原因：无效的路由器有效载荷结构。
- 解决方法：
  - 在`properties`中只使用一个路由器通道。
  - 对于邮件，使用`emails`（而不是`recipients`）。
  - 对比已知有效的示例并重试：
    - `scripts/notifier-create <部署> <json文件>`

`400 Bad Request`在监测器创建/更新时：
- 原因：无效的监测器模式、操作符/类型不匹配或无效的查询字段。
- 解决方法：
  - 验证必需字段：`name`、`type`、查询字段、调度和`notifierIds`。
  - 确认`operator`与监测器类型和阈值逻辑匹配。
  - 重试：
    - `scripts/monitor-create <部署> <json文件>`
    - `scripts/monitor-update <部署> <id> <json文件>`

监测器创建但从未告警：
- 原因：阈值太严格、查询窗口错误或正运行次数不足。
- 解决方法：
  - 在已知活跃期间检查历史记录：
    - `scripts/monitor-history <部署> <id> <开始时间> <结束时间>`
  - 降低阈值或扩大`rangeMinutes`。
  - 调整`triggerAfterNPositiveResults`/`triggerFromNRuns`。

告警过多（监测器嘈杂）：
- 原因：阈值太低或间隔太短。
- 解决方法：
  - 增加阈值。
  - 增加`triggerAfterNPositiveResults`和/或`triggerFromNRuns`。
  - 增加`intervalMinutes`或缩小匹配条件。

路由器存在但无交付：
- 原因：目标配置无效（URL/键/通道/邮件列表），或目标端拒绝。
- 解决方法：
  - 获取路由器并验证目标字段：
    - `scripts/notifier-get <部署> <id>`
  - 使用修正的属性重新创建/更新路由器：
    - `scripts/notifier-update <部署> <id> <json文件>`
  - 确认监测器引用正确的路由器ID。
