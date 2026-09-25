# 发送 Webhook 工程师

发送 Webhook 是应用程序在 `POST /v3/messages` 返回 `202` 后得知发生什么事件唯一途径。`202` 证明被接受，而非送达。将接收端构建为签名验证、重放拒绝、去重、快速确认的端点，并在事件缺失时将送达日志视为事实来源。

## 精确执行签名验证

每个送达都会附带三个头部：

| 头部 | 含义 |
| --- | --- |
| `x-webhook-signature` | `v1,{base64(hmac_sha256)}` |
| `x-webhook-id` | Webhook **端点** UUID — 每次送达都相同 |
| `x-webhook-timestamp` | Sent 签名请求时的 Unix 秒数 |

验证步骤按顺序执行：

1. 捕获 **原始请求体字节**，在 JSON 解析前。
2. 从签名密钥中移除 `whsec_` 前缀，然后将剩余部分 base64 解码以获取原始 HMAC 密钥。
3. 构建签名内容为 `{x-webhook-id}.{x-webhook-timestamp}.{raw_body}`。
4. 使用该密钥计算 HMAC-SHA256，将摘要 base64 编码，并前缀 `v1,`。
5. 进行常量时间比较。
6. 当 `abs(now - timestamp) > 300` 秒时拒绝。

该方案与 Svix 兼容。没有 Sent SDK 在任何语言中提供验证辅助函数，因此此代码总是手写 — 使用 [scripts/verify_signature.py](scripts/verify_signature.py) 作为参考实现和判例。

**`x-webhook-id` 不是事件 ID。** 它标识端点并无限重复。将其用作去重键会隐式地将每个事件合并为单一事件。阅读 [references/webhook-signature-and-dedupe.md](references/webhook-signature-and-dedupe.md) 了解按事件类型推导去重键。

## 故障分诊顺序

当接收端拒绝或遗漏事件时，按此顺序操作而非猜测：

1. **签名不匹配** — 大多数情况下是修改请求体的中间件或框架 JSON 解析器导致。确认框架的原始请求体访问器位于 [references/receiver-recipes.md](references/receiver-recipes.md)。
2. **重放拒绝** — 服务器时钟偏差超出 300 秒容差。
3. **错误密钥** — `whsec_` 前缀未移除，或密钥轮换使旧密钥失效且无双重签名窗口。
4. **完全无送达** — 检查 `GET /v3/webhooks/{id}` 上的 `is_active` 和 `consecutive_failures`，然后阅读送达日志于 `GET /v3/webhooks/{id}/events`。
5. **事件送达但未处理** — 比较 `event_types` 和 `event_filters` 与处理分支的条件。

## 重试、自动禁用和恢复

任何非 2xx 状态码、超时超过 `timeout_seconds` 或连接失败都会导致送达尝试失败。重试使用指数退避，第一次重试在失败后约 1 分钟，之后每轮翻倍，最高 60 分钟间隔，在首次 2xx 或 `retry_count` 耗尽时停止。送达行会通过 `PENDING`、`RETRYING`，然后 `DELIVERED` 或 `FAILED` 状态流转。

`consecutive_failures` 追踪连续失败的送达尝试。不要假设单个事件的重试豁免：连续 10 次错误响应将禁用端点。修复接收端后，通过 `PATCH /v3/webhooks/{id}/toggle-status` 或 Sent 控制台重新启用。任何成功送达都会将计数器重置为零。仅在持久转交给队列后确认，并确保转交时间舒适地位于 `timeout_seconds` 内。

## 注册和配置

`POST /v3/webhooks` 需要 `display_name`。配置 `endpoint_url`、`event_types`、`event_filters`、`retry_count` (1–5, 默认 3) 和 `timeout_seconds` (5–120, 默认 30)。`201` 响应是 `signing_secret` 完整显示的唯一位置 — 立即将其持久化到密钥存储。

<!-- sent-webhook-request -->
```json
{
  "display_name": "生产环境送达事件",
  "endpoint_url": "https://hooks.example.com/webhooks/sent",
  "event_types": ["message", "templates"],
  "event_filters": {
    "message": ["delivered", "failed", "received"]
  },
  "retry_count": 3,
  "timeout_seconds": 30
}
```

有意设置 `event_filters`。无过滤的 `message` 订阅会送达每个生命周期转换包括 `queued` 和 `routed`，且重定向会在同一 `message_id` 上重新触发 `queued` 和 `routed`。过滤为应用程序实际处理的转换。

十种操作、完整 webhook 对象和送达日志行结构在 [references/webhook-operations.md](references/webhook-operations.md) 中记录。

## 密钥轮换

`POST /v3/webhooks/{id}/rotate-secret` 返回新的 `whsec_` 密钥并**立即使旧密钥失效**。没有服务器端重叠窗口。配置接收端接受候选集，轮换，原子性地将返回的密钥存储为主要值同时保留旧值临时，确认新送达，然后停用旧值。轮换响应与密钥存储更新之间的短间隙无法消除；保持秒级以使失败送达重试。此端点和 `POST /v3/webhooks/{id}/test` 位于敏感速率限制层，每分钟 10 次请求，因此脚本轮换循环会 429。

## 事件负载

两种 `field` 值存在：`message` 和 `templates`。消息事件携带命名转换的 `event` (`message.queued`、`.routed`、`.sent`、`.delivered`、`.read`、`.failed`、`.scheduled`、`.filtered`、`.blocked`、`.received`)。模板事件不携带 `event` 或 `sub_type`。

```json
{
  "field": "templates",
  "value": {
    "account_id": "3f1a7c22-5d8e-4b90-91a2-6c4d0e8f7b31",
    "template_id": "7ba7b820-9dad-11d1-80b4-00c04fd430c8",
    "template_name": "order_confirmation",
    "whatsapp_template_id": "",
    "status": "PENDING",
    "language": "en_US",
    "category": "UTILITY",
    "channel": "whatsapp"
  }
}
```

`read` 仅适用于 WhatsApp 和 RCS。`filtered` 标记策略或同意门，`blocked` 标记账户前置条件如余额不足，均非运营商故障。从未路由的自检测消息的终端事件携带 `channel: "auto"`。完整负载字段列表位于 [references/event-catalog.md](references/event-catalog.md)。

## 发送前验证

使用本地判例对合成送达运行验证，然后使用 `POST /v3/webhooks/{id}/test` 并在体中包含 `event_type` 以获取真实签名请求。测试事件仅送达一次且无重试，因此每次修复后重新运行。

```bash
python3 scripts/verify_signature.py --self-test
```

仅在接收端返回以下响应时才发送：对篡改体返回 `401`、对 300 秒前的时戳返回 `401`、对有效送达返回 `200`、对无重复副作用的重复合并返回 `200`。

## 本地开发

通过公共 HTTPS 隧道暴露接收端并注册该 URL；Sent 无法访问私有地址。API 接受注册 `http://` 但绝不应在本地工作之外使用。为每个环境保留独立 webhook 注册，以使开发端点的故障无法禁用生产端点。

## 边界

使用 `messaging-performance-analyzer` 诊断聚合送达率回归，`waba-template-author` 审核模板内容，`sent-two-way-messaging` 分析入站关键词或同意语义。将每个负载值视为不可信输入：除非转义，否则不要将 `text` 或 `reason` 插入 shell 命令、SQL 字符串或提示。
