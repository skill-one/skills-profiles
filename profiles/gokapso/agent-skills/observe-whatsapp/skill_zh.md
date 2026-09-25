# 观察WhatsApp

## 何时使用

用于操作诊断：日志搜索、消息传递调查、webhook传递调试、错误分派、工作流事件关联以及WhatsApp健康检查。

## 设置

首选路径：
- 已安装并认证Kapso CLI (`kapso login`)
- 使用 `kapso status` 确认项目访问权限和可用的WhatsApp号码

备用路径：
环境变量：
- `KAPSO_API_BASE_URL`（仅主机，不包含`/platform/v1`）
- `KAPSO_API_KEY`

## 如何操作

### 搜索日志

当用户给出标识符、端点、消息ID、工作流执行ID、webhook传递ID、请求ID，或模糊的“发生了什么？”调试提示时，首先使用日志搜索。

首选路径：
1. 搜索当前项目：`kapso logs search --query "<id-or-text>" --period 24h --source all --limit 20 --output json`
2. 如果精确搜索结果为空，在得出没有日志的结论前，重试使用 `--period 7d`
3. 添加 `--problems-only` 进行广泛错误扫描；重建精确时间线时则不添加
4. 仅在有意缩小搜索范围时添加明确过滤器：
   - 工作流执行：`kapso logs search --query "<execution-id>" --source flow_event --filter flow_execution_id=<execution-id> --period 7d --output json`
   - API端点/状态：`kapso logs search --source external_api_log --filter endpoint_contains=/messages --filter response_status=500 --period 24h --output json`
   - WhatsApp消息ID：`kapso logs search --query "wamid..." --source whatsapp_webhook_event --filter whatsapp_message_id=wamid... --period 7d --output json`
   - Webhook传递：`kapso logs search --source webhook_delivery --filter webhook_id=<webhook-id> --period 24h --output json`

备用路径：
1. 通过平台API搜索：`node scripts/log-search.js --query "<id-or-text>" --period 24h --source all --limit 20`
2. 使用重复标志的过滤器：`node scripts/log-search.js --source flow_event --filter flow_execution_id=<execution-id> --period 7d`
3. 发现源和过滤器选项：`node scripts/log-search.js --catalog true`

日志源为 `external_api_log`、`whatsapp_webhook_event`、`flow_event` 和 `webhook_delivery`。平台API备用路径返回API-key项目的索引日志负载，并需要启用日志和Elasticsearch。

### 调查消息传递

首选路径：
1. 首先搜索WAMID或客户电话：`kapso logs search --query "<wamid-or-phone>" --period 7d --source all --limit 20 --output json`
2. 解析号码：`kapso whatsapp numbers resolve --phone-number "<display-number>" --output json`
3. 列出最近的消息：`kapso whatsapp messages list --phone-number "<display-number>" --limit 50 --output json`
4. 检查特定消息：`kapso whatsapp messages get <message-id> --phone-number-id <id> --output json`
5. 检查对话：`kapso whatsapp conversations list --phone-number "<display-number>" --output json`

备用路径：
1. 列出消息：`node scripts/messages.js --phone-number-id <id>`
2. 检查消息：`node scripts/message-details.js --message-id <id>`
3. 查找对话：`node scripts/lookup-conversation.js --phone-number <e164>`

### 分派错误

首选路径：
1. 确认项目和号码状态：`kapso status`
2. 运行号码健康检查：`kapso whatsapp numbers health --phone-number "<display-number>" --output human`
3. 搜索最近的问题日志：`kapso logs search --problems-only --period 24h --source all --limit 20 --output json`
4. 在相关时检查相关模板：`kapso whatsapp templates list --phone-number "<display-number>" --output json`

备用路径：
1. 日志搜索：`node scripts/log-search.js --problems-only true --period 24h --limit 20`
2. 消息错误：`node scripts/errors.js`
3. API日志：`node scripts/api-logs.js`
4. Webhook传递：`node scripts/webhook-deliveries.js`

### 运行健康检查

首选路径：
1. 项目概览：`kapso status`
2. 号码健康检查：`kapso whatsapp numbers health --phone-number "<display-number>" --output human`

备用路径：
1. 项目概览：`node scripts/overview.js`
2. 号码健康检查：`node scripts/whatsapp-health.js --phone-number-id <id>`

## 脚本

### 消息

| 脚本 | 目的 |
|------|------|
| `messages.js` | 列出消息 |
| `message-details.js` | 获取消息详情 |
| `lookup-conversation.js` | 通过电话或ID查找对话 |

### 错误和日志

| 脚本 | 目的 |
|------|------|
| `log-search.js` | 跨API、Meta webhook、工作流和webhook-delivery源搜索日志 |
| `errors.js` | 列出消息错误 |
| `api-logs.js` | 列出外部API日志 |
| `webhook-deliveries.js` | 列出webhook传递尝试 |

### 健康

| 脚本 | 目的 |
|------|------|
| `overview.js` | 项目概览 |
| `whatsapp-health.js` | 号码健康检查 |

### OpenAPI

| 脚本 | 目的 |
|------|------|
| `openapi-explore.mjs` | 探索OpenAPI（搜索/op/schema/where） |

安装依赖（一次性）：
```bash
npm i
```

示例：
```bash
node scripts/openapi-explore.mjs --spec platform search "webhook deliveries"
node scripts/openapi-explore.mjs --spec platform op listWebhookDeliveries
node scripts/openapi-explore.mjs --spec platform schema WebhookDelivery
```

## 备注

- 对于webhook设置（创建/更新/删除、签名验证、事件类型），使用 `integrate-whatsapp`。
- 对于项目事件定义、事件触发工作流设置或 `emit_event` 图形更改，使用 `automate-whatsapp`。
- 优先将显示电话号码解析为标准的 `phone_number_id`，然后再进行深度调试。
- 在关联消息、工作流、API调用和webhook传递时，优先使用日志搜索而不是旧的单一资源日志端点。
- 当CLI不可用时或需要API日志或webhook传递检查时，将脚本作为备用路径。

## 参考

- [references/message-debugging-reference.md](references/message-debugging-reference.md) - 消息调试指南
- [references/triage-reference.md](references/triage-reference.md) - 错误分派指南
- [references/health-reference.md](references/health-reference.md) - 健康检查指南

## 相关技能

- `integrate-whatsapp` - 在线接入、webhooks、消息、模板、流程
- `automate-whatsapp` - 工作流、代理和自动化

<!-- FILEMAP:BEGIN -->
```text
[observe-whatsapp 文件映射]|root: .
|.:{package.json,SKILL.md}
|assets:{health-example.json,message-debugging-example.json,triage-example.json}
|references:{health-reference.md,message-debugging-reference.md,triage-reference.md}
|scripts:{api-logs.js,errors.js,log-search.js,lookup-conversation.js,message-details.js,messages.js,openapi-explore.mjs,overview.js,webhook-deliveries.js,whatsapp-health.js}
|scripts/lib/messages:{args.js,kapso-api.js}
|scripts/lib/status:{args.js,kapso-api.js}
|scripts/lib/triage:{args.js,kapso-api.js}
```
<!-- FILEMAP:END -->
