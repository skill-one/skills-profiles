# Kibana 连接器

## 核心概念

连接器用于存储 Elastic 服务和第三方系统的连接信息。告警规则使用连接器在规则条件满足时路由**操作**（通知）。连接器按**Kibana Space**进行管理，并且可以在该 Space 内的所有规则中共享。

### 连接器类别

| 类别                    | 连接器类型                                                                                                                                                      |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **大语言模型提供者**     | OpenAI, Google Gemini, Amazon Bedrock, Elastic 管理的大语言模型, AI Connector, MCP (预览, 9.3+)                                                                       |
| **事件管理**             | PagerDuty, Opsgenie, ServiceNow (ITSM, SecOps, ITOM), Jira, Jira Service Management (9.2+), IBM Resilient, Swimlane, Torq, Tines, D3 Security, XSOAR (9.1+), TheHive |
| **端点安全**             | CrowdStrike, SentinelOne, Microsoft Defender for Endpoint                                                                                                            |
| **消息传递**               | Slack (API / Webhook), Microsoft Teams, Email                                                                                                                        |
| **日志记录与可观察性** | 服务器日志, 索引, 可观察性 AI 助手                                                                                                                                |
| **Webhook**                 | Webhook, Webhook - 案例管理, xMatters                                                                                                                         |
| **Elastic**                 | Cases                                                                                                                                                                |

## 身份验证

所有连接器 API 调用都需要 API 密钥认证或基本认证。所有修改请求都必须包含 `kbn-xsrf` 头部。

```http
kbn-xsrf: true
```

## 所需权限

对连接器的访问权限基于您对启用告警功能的权限。您需要在 Stack Management 中的操作和连接器上拥有 `all` 权限。

## API 参考

基础路径: `<kibana_url>/api/actions` (对于非默认 Space，则为 `/s/<space_id>/api/actions`)。

| 操作           | 方法 | 端点                               |
| -------------- | ------ | -------------------------------------- |
| 创建连接器    | POST   | `/api/actions/connector/{id}`          |
| 更新连接器    | PUT    | `/api/actions/connector/{id}`          |
| 获取连接器       | GET    | `/api/actions/connector/{id}`          |
| 删除连接器    | DELETE | `/api/actions/connector/{id}`          |
| 获取所有连接器  | GET    | `/api/actions/connectors`              |
| 获取连接器类型 | GET    | `/api/actions/connector_types`         |
| 运行连接器       | POST   | `/api/actions/connector/{id}/_execute` |

## 创建连接器

### 所需字段

| 字段               | 类型   | 描述                                                                      |
| ------------------ | ------ | -------------------------------------------------------------------------------- |
| `name`              | string | 连接器的显示名称                                                           |
| `connector_type_id` | string | 连接器类型 (例如, `.slack`, `.email`, `.webhook`, `.pagerduty`, `.jira`) |
| `config`            | object | 类型特定的配置 (非秘密设置)                                                |
| `secrets`           | object | 类型特定的秘密 (API 密钥, 密码, 令牌)                                        |

### 示例：创建 Slack 连接器 (Webhook)

```bash
curl -X POST "https://my-kibana:5601/api/actions/connector/my-slack-connector" \
  -H "kbn-xsrf: true" \
  -H "Content-Type: application/json" \
  -H "Authorization: ApiKey <your-api-key>" \
  -d '{
    "name": "生产环境 Slack 告警",
    "connector_type_id": ".slack",
    "config": {},
    "secrets": {
      "webhookUrl": "https://hooks.slack.com/services/T00/B00/XXXX"
    }
  }'
```

所有连接器类型都共享相同的请求结构 — 只有 `connector_type_id`, `config` 和 `secrets` 不同。有关可用类型及其所需字段的详细信息，请参阅 [常见连接器类型 ID](#common-connector-type-ids) 表。

### 示例：创建 PagerDuty 连接器

```bash
curl -X POST "https://my-kibana:5601/api/actions/connector/my-pagerduty" \
  -H "kbn-xsrf: true" \
  -H "Content-Type: application/json" \
  -H "Authorization: ApiKey <your-api-key>" \
  -d '{
    "name": "PagerDuty 事件",
    "connector_type_id": ".pagerduty",
    "config": {
      "apiUrl": "https://events.pagerduty.com/v2/enqueue"
    },
    "secrets": {
      "routingKey": "your-pagerduty-integration-key"
    }
  }'
```

## 更新连接器

`PUT /api/actions/connector/{id}` 会替换完整的配置。`connector_type_id` 是不可变的 — 删除并重新创建以更改它。

## 列出和发现连接器

```bash
# 获取当前 Space 中的所有连接器
curl -X GET "https://my-kibana:5601/api/actions/connectors" \
  -H "Authorization: ApiKey <your-api-key>"

# 获取可用的连接器类型
curl -X GET "https://my-kibana:5601/api/actions/connector_types" \
  -H "Authorization: ApiKey <your-api-key>"

# 按功能过滤连接器类型 (例如，仅支持告警的那些)
curl -X GET "https://my-kibana:5601/api/actions/connector_types?feature_id=alerting" \
  -H "Authorization: ApiKey <your-api-key>"
```

`GET /api/actions/connectors` 的响应包括 `referenced_by_count`，显示每个连接器被多少条规则使用。删除之前始终检查此值。

## 运行连接器 (测试)

直接执行连接器操作，用于测试连接性。

```bash
curl -X POST "https://my-kibana:5601/api/actions/connector/my-slack-connector/_execute" \
  -H "kbn-xsrf: true" \
  -H "Content-Type: application/json" \
  -H "Authorization: ApiKey <your-api-key>" \
  -d '{
    "params": {
      "message": "来自 API 的测试告警"
    }
  }'
```

## 删除连接器

```bash
curl -X DELETE "https://my-kibana:5601/api/actions/connector/my-slack-connector" \
  -H "kbn-xsrf: true" \
  -H "Authorization: ApiKey <your-api-key>"
```

**警告:** 删除被规则引用的连接器会导致这些规则的操作静默失败。删除之前先检查 `referenced_by_count`。

## Terraform 提供者

使用 `elasticstack` 提供者资源 `elasticstack_kibana_action_connector`。

```hcl
terraform {
  required_providers {
    elasticstack = {
      source  = "elastic/elasticstack"
    }
  }
}

provider "elasticstack" {
  kibana {
    endpoints = ["https://my-kibana:5601"]
    api_key   = var.kibana_api_key
  }
}

resource "elasticstack_kibana_action_connector" "slack" {
  name              = "生产环境 Slack 告警"
  connector_type_id = ".slack"

  config = jsonencode({})

  secrets = jsonencode({
    webhookUrl = "https://hooks.slack.com/services/T00/B00/XXXX"
  })
}

resource "elasticstack_kibana_action_connector" "index" {
  name              = "告警索引写入器"
  connector_type_id = ".index"

  config = jsonencode({
    index              = "alert-history"
    executionTimeField = "@timestamp"
  })

  secrets = jsonencode({})
}
```

**Terraform 关键注意事项:**

- `config` 和 `secrets` 必须通过 `jsonencode()` 编码为 JSON 字符串
- 秘密存储在 Terraform 状态中；使用带加密的远程后端并限制状态文件访问
- 导入现有连接器:
  `terraform import elasticstack_kibana_action_connector.my_connector <space_id>/<connector_id>` (对于默认 Space 使用 `default`)
- 导入后，秘密不会在状态中填充；您必须在配置中提供它们

## 预配置连接器 (本地部署)

对于自管理的 Kibana，可以在 `kibana.yml` 中预配置连接器，以便在启动时无需手动创建即可使用：

```yaml
xpack.actions.preconfigured:
  my-slack-connector:
    name: "生产环境 Slack"
    actionTypeId: .slack
    secrets:
      webhookUrl: "https://hooks.slack.com/services/T00/B00/XXXX"
  my-webhook:
    name: "自定义 Webhook"
    actionTypeId: .webhook
    config:
      url: "https://api.example.com/alerts"
      method: post
      hasAuth: true
    secrets:
      user: "alert-user"
      password: "secret-password"
```

预配置连接器无法通过 API 或 UI 进行编辑或删除。它们在 API 响应中显示 `is_preconfigured: true` 并省略 `config` 和 `is_missing_secrets`。

## 网络配置

通过 `kibana.yml` 自定义连接器网络 (代理, TLS, 证书)：

```yaml
# 所有连接器的全局代理
xpack.actions.proxyUrl: "https://proxy.example.com:8443"

# 每个主机的 TLS 设置
xpack.actions.customHostSettings:
  - url: "https://api.example.com"
    ssl:
      verificationMode: full
      certificateAuthoritiesFiles: ["/path/to/ca.pem"]
```

## Kibana 工作流中的连接器

连接器作为跨多个 Kibana 工作流的集成层，而不仅限于告警通知：

| 工作流                  | 连接器类型                       | 关键模式                                                                    |
| ----------------------- | ------------------------------------- | ------------------------------------------------------------------------------ |
| **ITSM 工单**        | ServiceNow, Jira, IBM Resilient       | 在活动时创建工单，在 `Recovered` 时关闭                                      |
| **值班升级**    | PagerDuty, Opsgenie                   | `trigger` 在活动时，`resolve` 在 `Recovered`；始终设置去重键                  |
| **案例管理**       | Cases (系统操作)                 | 仅 UI；将告警分组到调查案例；可以自动推送到 ITSM         |
| **消息传递 / 意识** | Slack, Teams, Email                   | `onActionGroupChange` 用于事件频道；摘要用于监控频道                        |
| **审计日志**         | Index                                 | `onActiveAlert` 将完整告警时间序列写入 Elasticsearch               |
| **AI 工作流**          | OpenAI, Bedrock, Gemini, AI Connector | 驱动 Elastic AI 助手和攻击发现；系统管理               |
| **自定义集成**   | Webhook                               | 通用 HTTP 外发，带有 Mustache-模板化的 JSON 正文                        |

有关每个工作流的详细模式、示例和决策指导，请参阅 [workflows.md](references/workflows.md)。

## 最佳实践

1. **在本地部署的生产环境中使用预配置连接器。** 它们消除了秘密蔓延，可以保留 Saved Object 导入，并且无法被意外删除。为动态或用户管理的场景保留 API 创建的连接器。

2. **在附加到规则之前测试连接器。** 使用 `_execute` 端点验证连接性。配置错误的连接器会导致静默操作失败，并且仅在规则的执行历史中可见。

3. **删除之前检查 `referenced_by_count`。** 删除正在使用的连接器会导致这些操作失败。列出连接器并验证零引用，或者首先将规则重新分配到新的连接器。

4. **使用 Email 域允许列表。** `xpack.actions.email.domain_allowlist` 设置限制了连接器可以发送到的电子邮件域。如果您更新此列表，现有电子邮件连接器如果收件人位于新列表之外，将开始失败。

5. **在 Terraform 中安全存储秘密。** 连接器秘密 (API 密钥, 密码, webhook URL) 存储在 Terraform 状态中。使用加密的远程后端 (S3+KMS, Azure Blob+加密, GCS+CMEK) 并限制对状态文件访问。在变量上使用 `sensitive = true`。

6. **每个服务一个连接器，而不是每个规则一个。** 创建一个 Slack 连接器，并从多个规则中引用它。这集中了秘密轮换并减少了重复。

7. **使用 Spaces 进行多租户隔离。** 连接器按 Kibana Space 范围划分。为不同的团队或环境创建单独的 Space，并按 Space 配置连接器。

8. **监控连接器健康。** 连接器执行失败记录在事件日志索引 (`.kibana-event-log-*`) 中。连接器失败报告为任务管理器中的成功，但告警交付失败。检查 [事件日志索引](https://www.elastic.co/docs/explore-analyze/alerting/alerts/event-log-index) 以获取真正的失败率。

9. **始终在活动操作旁边配置恢复操作。** 用于 ITSM 和值班工具 (ServiceNow, Jira, PagerDuty, Opsgenie) 的连接器支持关闭/解决操作。没有恢复操作，事件将永远保持打开状态。

10. **为值班连接器使用去重键。** 设置 `dedupKey` (PagerDuty) 或 `alias` (Opsgenie) 为 `{{rule.id}}-{{alert.id}}` 以确保解决事件关闭正确的工单。如果没有此设置，每次告警重新触发时都会创建新工单。

11. **对于调查工作流，优先使用 Cases 连接器。** 当告警需要评论、附件和指派时，使用 Cases 而不是直接 Jira/ServiceNow 连接器。Cases 提供了原生的调查 UI，并且仍然可以通过案例的外部连接推送到 ITSM。

12. **使用 Index 连接器进行持久的审计跟踪。** Index 连接器写入 Elasticsearch，使告警历史可搜索和可仪表板化。将其与目标索引上的 ILM 策略配对以控制保留。

13. **通过操作设置限制连接器访问。** 使用 `xpack.actions.enabledActionTypes` 仅允许组织需要的连接器类型，并使用 `xpack.actions.allowedHosts` 限制出站连接到已知端点。

## 常见陷阱

1. **缺少 `kbn-xsrf` 头部。** 所有 POST, PUT, DELETE 请求都需要 `kbn-xsrf: true`。遗漏它将返回 400 错误。

2. **错误的 `connector_type_id`。** 使用包括开头点的确切字符串 (例如, `.slack`, 不是 `slack`)。通过 `GET /api/actions/connector_types` 发现有效类型。

3. **空的 `secrets` 对象是必需的。** 即使对于没有秘密的连接器 (例如, `.index`, `.server-log`)，在创建请求中也必须提供 `"secrets": {}`。

4. **连接器类型是不可变的。** 创建后无法更改 `connector_type_id`。删除并重新创建。

5. **导出时丢失秘密。** 通过 Saved Objects 导出连接器会删除秘密。导入后，连接器显示 `is_missing_secrets: true`，并且在 UI 中出现“修复”按钮。您必须手动或通过 API 重新输入秘密。

6. **预配置连接器无法通过 API 修改。** 尝试更新或删除预配置连接器将返回 400。仅通过 `kibana.yml` 管理它们。

7. **第三方服务的速率限制。** 发送大量通知的连接器 (例如，每分钟一个) 可能会触发 Slack, PagerDuty 或邮件提供者的速率限制。在规则端使用告警摘要和操作频率控制来减少数量。

8. **连接器网络故障。** Kibana 必须能够到达连接器的目标 URL。验证防火墙规则、代理设置和 DNS 解析。使用 `xpack.actions.customHostSettings` 解决 TLS 问题。

9. **许可证要求。** 某些连接器类型需要 Gold, Platinum 或 Enterprise 许可证。检查 `minimum_license_required` 字段从 `GET /api/actions/connector_types`。如果连接器 `enabled_in_config: true` 但 `enabled_in_license: false`，则无法使用。

10. **Terraform 导入不会恢复秘密。** 将现有连接器导入 Terraform 时，秘密不会从 Kibana 读取。您必须在 Terraform 配置中提供它们，否则下一个 `terraform apply` 将用空值覆盖它们。

## 常见连接器类型 ID

| 类型 ID                        | 名称                            | 许可证    |
| ------------------------------ | ------------------------------- | ---------- |
| `.email`                       | Email                           | Gold       |
| `.slack`                       | Slack (Webhook)                 | Gold       |
| `.slack_api`                   | Slack (API)                     | Gold       |
| `.pagerduty`                   | PagerDuty                       | Gold       |
| `.jira`                        | Jira                            | Gold       |
| `.servicenow`                  | ServiceNow ITSM                 | Platinum   |
| `.servicenow-sir`              | ServiceNow SecOps               | Platinum   |
| `.servicenow-itom`             | ServiceNow ITOM                 | Platinum   |
| `.webhook`                     | Webhook                         | Gold       |
| `.index`                       | Index                           | Basic      |
| `.server-log`                  | Server log                      | Basic      |
| `.opsgenie`                    | Opsgenie                        | Gold       |
| `.teams`                       | Microsoft Teams                 | Gold       |
| `.gen-ai`                      | OpenAI                          | Enterprise |
| `.bedrock`                     | Amazon Bedrock                  | Enterprise |
| `.gemini`                      | Google Gemini                   | Enterprise |
| `.cases`                       | Cases                           | Platinum   |
| `.crowdstrike`                 | CrowdStrike                     | Enterprise |
| `.sentinelone`                 | SentinelOne                     | Enterprise |
| `.microsoft_defender_endpoint` | Microsoft Defender for Endpoint | Enterprise |
| `.thehive`                     | TheHive                         | Gold       |

> **注意:** 使用 `GET /api/actions/connector_types` 发现您部署上所有可用的类型及其确切的 `minimum_license_required` 值。XSOAR, Jira Service Management 和 MCP 的连接器类型可用，但可能不会出现在较旧的 API 规范版本中。

## 示例

**创建 Slack 连接器:** "为我们的告警设置 Slack 通知。" `POST /api/actions/connector`，带有 `connector_type_id: ".slack"` 和 `secrets.webhookUrl`。在规则操作中使用返回的连接器 `id`。

**在附加到规则之前测试连接器:** "验证 PagerDuty 连接器是否正常工作。"
`POST /api/actions/connector/{id}/_execute`，带有最小的 `params` 对象以确认连接性，然后再添加到任何规则。

**删除之前审计连接器使用:** "删除旧的 Email 连接器。" `GET /api/actions/connectors`，检查 `referenced_by_count` — 如果非零，首先将引用的规则重新分配，然后 `DELETE /api/actions/connector/{id}`。

## 指南

- 在每个 POST, PUT 和 DELETE 中包含 `kbn-xsrf: true`；遗漏它将返回 400。
- `connector_type_id` 是不可变的 — 删除并重新创建以更改连接器类型。
- 即使对于没有秘密的连接器 (例如, `.index`, `.server-log`)，也始终传递 `"secrets": {}`。
- 删除之前检查 `referenced_by_count`；删除连接器会静默破坏所有引用的规则操作。
- 连接器按 Space 范围划分；对于非默认 Kibana Space，在路径前缀 `/s/<space_id>/api/actions/`。
- 秘密是只写：GET 不会返回，并且在 Saved Object 导出/导入时会被删除；导入后始终重新提供。
- 在附加到规则之前使用 `_execute` 测试每个新连接器；生产中的连接器失败是静默的。

## 其他资源

- [Kibana 连接器 API 参考](https://www.elastic.co/docs/api/doc/kibana/group/endpoint-connectors)
- [连接器概述](https://www.elastic.co/docs/reference/kibana/connectors-kibana)
- [预配置连接器](https://www.elastic.co/docs/reference/kibana/connectors-kibana/pre-configured-connectors)
- [告警设置 (操作配置)](https://www.elastic.co/docs/reference/kibana/configuration-reference/alerting-settings#action-settings)
- [Terraform: elasticstack_kibana_action_connector](https://registry.terraform.io/providers/elastic/elasticstack/latest/docs/resources/kibana_action_connector)
- [Terraform: 管理 Kibana 规则和连接器资源](https://registry.terraform.io/providers/elastic/elasticstack/latest/docs/guides/elasticstack-kibana-rule)
