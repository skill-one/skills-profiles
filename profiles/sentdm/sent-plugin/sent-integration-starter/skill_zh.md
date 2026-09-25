# Sent 集成入门

分四个阶段启动 Sent 集成：认证、幂等发送、接收验证事件，然后加固。不要混淆它们——大多数失败的集成通过第一阶段并跳过第三阶段。

## 第一阶段：客户端和凭证

Sent v3 REST 请求使用 `x-api-key` 头进行认证。应用程序代理可以接受来自其调用者的 `Authorization: Bearer`，而 Sent MCP 服务器使用客户端管理的 OAuth，但这不会改变发送到 `api.sent.dm` 的 REST 头。组织密钥可以添加 `x-profile-id` 来代表子配置文件；发送该头的配置文件范围密钥会收到 `403`。

| 语言 | 包 | 客户端 |
| --- | --- | --- |
| TypeScript | `@sentdm/sentdm` | `new SentDm()` |
| Python | `sentdm` (导入 `sent_dm`) | `Sent()` 或 `AsyncSent()` |
| Go | `github.com/sentdm/sent-dm-go` | `sentdm.NewClient()` |
| Java | `dm.sent:sent-java` | `SentOkHttpClient.fromEnv()` |
| C# | `Sentdm` | `new SentClient()` |
| PHP | `sentdm/sent-dm-php` | `new SentDm\Client($apiKey)` |
| Ruby | `sentdm` | `Sentdm::Client.new` |

除了 PHP 之外，每个 SDK 都会自动读取 `SENT_DM_API_KEY`。单端点接收器样本读取 `SENT_DM_WEBHOOK_SECRET`；多租户生产接收器需要一个按 webhook ID 键化的密钥注册表，而不是一个进程范围内的密钥。旧文档使用 `SENT_API_KEY` 和 `SENT_WEBHOOK_SECRET`——将它们视为别名，并标准化为 `SENT_DM_` 名称。

从凭证模型中选择客户端生命周期。一个具有单个服务器管理密钥的单账户服务应重用一个长生命周期的客户端及其连接池。一个解析调用者或配置文件凭证的每个请求的多租户代理应构造该请求的客户端并丢弃它，以便租户凭证不会通过共享状态泄露。特定于框架的连接、Ruby 的 `messages.send_` 命名怪癖以及每个生态系统后台工作的选择在 [参考资料/sdk-and-frameworks.md](references/sdk-and-frameworks.md) 中。

在启动时验证配置，并在密钥缺失时快速失败，而不是在第一个客户发送时出现认证错误。

## 第二阶段：幂等发送

```json
{
  "to": ["+14155551234"],
  "template": {
    "name": "order_confirmation",
    "parameters": { "order_id": "12345" }
  },
  "sandbox": true
}
```

`to` 是唯一必需字段。提供 `template` 或 `text`，并省略 `channel` 以让自动路由选择。永远不要编写一个包含多个值的 `channel` 数组以期望回退——那会广播并增加费用。频道决策属于 `sent-routing-strategist`。

在每次 POST、PUT 和 PATCH 上发送 `Idempotency-Key`，它由您自己的域对象（例如订单 ID 加上通知类型）确定性地派生，以便在超时后重试不会重复发送。密钥是 1–255 个字符的 `[A-Za-z0-9_-]`，每个客户每个密钥缓存 24 小时。重放会返回带有 `Idempotent-Replayed: true` 和 `X-Original-Request-Id` 的缓存的正文。当原始请求仍在进行中时到达的重复项会等待最多五秒钟，然后失败 `409 CONFLICT_001`；`503 SERVICE_001` 表示幂等存储不可用，请求被故意不执行。

`202` 表示已接受，而不是已交付。立即将返回的 `message_id` 值与您自己的租户、配置文件和逻辑发送标识符持久化。Webhook 事件携带 Sent 消息 ID 和账户数据，但永远不会携带您应用程序的租户标识符。

## 第三阶段：验证 webhook 接收器

没有接收器的集成没有交付真相。注册一个端点，然后验证每个交付：HMAC-SHA256 over `{x-webhook-id}.{x-webhook-timestamp}.{raw_body}`，基于剥离 `whsec_` 后的 base64 解码密钥进行密钥，在恒定时间内进行比较，拒绝 300 秒之外的时间戳。没有任何语言的 SDK 会提供验证器。

在执行工作之前使用 `200` 进行确认，并在 `{message_id}:{message_status}` 上对出站事件和 `message_id` 上对入站事件进行去重。连续失败的十次交付会禁用端点。完整的机制属于 `sent-webhook-engineer`；将一个验证的、快速确认的、去重的接收器视为这里的启动要求。

## 第四阶段：加固

### 基于响应类的重试策略

| 响应 | 重试 | 如何 |
| --- | --- | --- |
| `2xx` | 否 | 成功 |
| `400`，`422` `VALIDATION_*` | 否 | 修复请求 |
| `401`，`403` `AUTH_*` | 否 | 立即停止；连续十次认证失败会锁定凭证并逐步锁定 |
| `404` `RESOURCE_*` | 否 | 引用的对象不存在 |
| `409 CONFLICT_001` | 是，一次，暂停后 | 一个并发重复项正在飞行 |
| `429` | 是 | 尊重 `Retry-After`；抖动回退 |
| `5xx`，`503 SERVICE_001` | 是 | 带抖动和上限的指数回退 |
| 无响应的超时 | 仅在有证据的情况下安全重试 | 重用相同的 `Idempotency-Key`；没有它，无法通过密钥或收件人可靠地查找 API，因此不要自动重发 |

标准限制是滑动窗口的每分钟 200 个请求。`POST /v3/webhooks/{id}/rotate-secret` 和 `POST /v3/webhooks/{id}/test` 限制为每分钟 10 次。速率限制标头仅出现在 `429` 响应上，因此必须设计而不是测量——每 1,000 个收件人每请求批量，并大致每秒一个请求进行批量工作。

### 错误处理

错误作为 `{success, data, error: {code, message, details, doc_url}, meta: {request_id, timestamp, version}}` 到达。根据 `error.code` 前缀系列（`AUTH_`，`VALIDATION_`，`RESOURCE_`，`BUSINESS_`，`CONFLICT_`，`SERVICE_`，`INTERNAL_`）而不是消息文本或单个代码进行分支。完整的 46 代码目录和重试分类在 [参考资料/errors-and-limits.md](references/errors-and-limits.md) 中。

两个代码不太直观：`BUSINESS_003` 和 `BUSINESS_004` 被记录为请求级错误，但在 `POST /v3/messages` 上请求被接受为 `202`，受影响的消息最终为 `BLOCKED` 和 `FILTERED`。因此，余额不足不会使发送调用失败。

### 可观察性

在每次响应（成功或失败）上记录 `meta.request_id`——它是支持的相关处理程序。记录从您的逻辑发送到返回的 `message_id` 值的映射，并保留一个仅追加的事件历史记录，以便重路由的序列保持可审计。永远不要记录 API 密钥、webhook 签名密钥、`payment_details` 或超出您的保留策略的原始收件人消息内容。

### 启动清单

- [ ] 凭证从环境加载；未提交任何内容，每个环境都有单独的密钥。
- [ ] 客户端生命周期与凭证范围匹配：共享用于单个服务器管理密钥，每个请求用于租户提供的凭证。
- [ ] 每个修改调用都有 `Idempotency-Key`，并确定性地派生。
- [ ] 重试策略通过错误系列区分可重试和终止。
- [ ] 批量路径针对每分钟 200 个请求进行节奏，并最多批量到 1,000 个收件人。
- [ ] webhook 接收器验证签名和时间戳，快速返回 `200`，并进行去重。
- [ ] 接收器在真实失败时返回非 2xx，以便 Sent 重试。
- [ ] `message_id` 到租户的映射在发送之前持久化。
- [ ] `request_id` 被记录；密钥和卡数据没有被记录。
- [ ] 沙盒冒烟测试通过，然后真实发送达到 `DELIVERED`。
- [ ] 报警涵盖 webhook `consecutive_failures`，`429` 量，以及过滤或阻止率。

## 验证

运行本地预检，它不需要凭证和网络：

```bash
python3 scripts/preflight.py --self-test
```

然后验证一个带有 `"sandbox": true` 的真实路径，它进行认证和验证而不执行，最后通过接收器确认一个实时发送为 `DELIVERED`。

## 边界

使用 `sent-webhook-engineer` 进行接收器深度，`sent-routing-strategist` 进行频道选择，`sent-messaging` 进行确认一次性发送，`sent-two-way-messaging` 进行入站和同意，`sent-profile-provisioning` 进行多租户配置，并在替换另一个 CPaaS 提供商时使用 `migrate-to-sent`。
