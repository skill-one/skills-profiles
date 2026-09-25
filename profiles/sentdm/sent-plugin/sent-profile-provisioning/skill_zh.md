# 发送配置文件配置

此技能是配置文件架构的执行对应物：一旦确定了租户边界，它将驱动 API 调用、完成回调、活动注册和用户管理，使配置文件能够发送。首先使用 `sender-profile-architect` 设计边界；在此处进行配置。

## 配置顺序

1. **确认凭证。** `POST /v3/profiles` 需要 `admin` 权限的组织密钥。配置文件范围的密钥无法创建配置文件，而发送 `x-profile-id` 的配置文件密钥将收到 `403`。
2. **在调用之前决定继承和共享。** 这些标志塑造合规立场，并且以后很难撤销。
3. **创建配置文件**，在形状不确定时首先使用 `"sandbox": true` 验证负载。由于成功的沙盒响应被缓存 24 小时，因此使用不同的 idempotency key 进行实时创建。
4. **通过三个支持路径中的确切一个附加或继承 WhatsApp**。
5. **在配置文件下注册活动**。
6. **使用 `POST /v3/profiles/{profileId}/complete` 和可访问的 `webHookUrl` 完成配置文件**。
7. **从回调中核对状态，或者在错过回调时轮询。**
8. **邀请具有最低权限角色的用户**。

## 创建负载要素

`name` 是唯一必需字段。结果可选字段分组为身份、共享、继承、计费、WhatsApp 和品牌。

```json
{
  "name": "Northwind Retail",
  "short_name": "Northwind",
  "description": "零售品牌租户",
  "allow_contact_sharing": false,
  "allow_template_sharing": false,
  "inherit_contacts": false,
  "inherit_templates": false,
  "inherit_tcr_brand": true,
  "inherit_tcr_campaign": true,
  "billing_model": "profile",
  "billing_contact": {
    "name": "Ada Ops",
    "email": "ops@example.com",
    "phone": "+14155550100",
    "address": "1 Example Way, Springfield"
  },
  "sandbox": true
}
```

`short_name` 必须是 3 到 11 个字符的字母、数字和空格，至少包含一个字母。继承标志默认为 `true`，因此没有标志创建的配置文件将消耗组织的联系人、模板、品牌和活动。示例明确选择联系人和模板隔离，同时继承组织的合规注册。共享标志将此配置文件的资源向外暴露；继承标志将组织的资源向内消耗。它们是独立的方向，并且经常被混淆。

创建允许仅 `name`，但完成还需要 `short_name`、`description`、配置文件 KYC 信息以及任何必需的活动或渠道设置。当 `inherit_tcr_brand` 为 `true` 时，API 在创建请求中拒绝 `brand` 对象，尽管配置文件仍需要其自己的 KYC 提交；通过仪表板完成 KYC，然后调用完成端点。

`billing_model` 接受 `profile`、`organization` 或 `profile_and_organization`。任何包含 `profile` 的模型都需要 `billing_contact`，当不存在时，并且 `payment_details` 仅接受这些模型。卡字段将转发到支付处理器，并且绝不能在任何应用程序中记录、回显或持久化。

字段级规则、错误代码和仅更新字段在 [references/profile-lifecycle.md](references/profile-lifecycle.md) 中。

## 继承决策

| 标志 | `true` 表示 | 后果 |
| --- | --- | --- |
| `inherit_tcr_brand` | 使用组织的注册品牌 | 在同一请求中拒绝 `brand` 对象 |
| `inherit_tcr_campaign` | 使用组织的活动 | 这些活动对此配置文件是只读的；创建一个将返回验证错误 |
| `inherit_contacts` | 读取组织的联系人 | 租户之间没有联系人隔离 |
| `inherit_templates` | 读取组织的模板 | 租户之间没有模板隔离 |

具有 `inherit_tcr_campaign: false` 的继承品牌是一个受支持且常见的模式：共享法律身份，每个租户都有专门的通信用例。

## WhatsApp：恰好三种路径

1. 组织嵌入式注册，在发送仪表板中执行。**没有公共端点启动此流程。**
2. 子配置文件继承 — 一旦组织拥有 WABA，就省略 `whatsapp_business_account`。
3. 专用配置文件凭证 — 提供 `whatsapp_business_account` 与 `waba_id` 和 `access_token`，可选 `phone_number_id`。

在 `POST /v3/profiles` 上提供凭证不是嵌入式注册端点。当组织没有配置 WABA 时省略 `whatsapp_business_account` 将返回 `422`；完成组织嵌入式注册或提供有效的直接凭证。使用 `waba-embedded-signup` 进行操作注册流程。

## 完成和状态

`POST /v3/profiles/{profileId}/complete` 需要 `webHookUrl`。

```json
{
  "webHookUrl": "https://provisioning.example.com/callbacks/profile-complete",
  "sandbox": false
}
```

`202` 表示处理已开始且不包含最终状态。`200` 表示配置文件已完整，其正文包含状态。回调正文是 `{profileId, success, status, timestamp}`，并且**只发送一次且不重试**，因此接收者必须在调用之前处于活动状态，并且流程必须降级到轮询 `GET /v3/profiles/{profileId}`。此回调与订阅的发送 webhook 分开，并且未记录携带 webhook HMAC 头部；使用与配置记录绑定的唯一回调路径，拒绝未知配置文件 ID，并将轮询视为权威的恢复路径。

配置文件状态词汇因表面而异：创建响应显示小写的 `incomplete`，完成 `200` 显示小写的 `completed`，完成回调使用 `COMPLETED`、`SUBMITTED` 和 `failed`，而 `GET /v3/profiles/{id}` 记录 `approved`、`submitted`、`processing` 和 `failed`。不要断言关闭的枚举，不要将小写规范化为固定集，并记录每个值产生的表面。不区分大小写地比较状态并保留未知字符串。

## 每个配置文件的活动

活动管理位于配置文件下：`GET|POST /v3/profiles/{profileId}/campaigns` 和 `PUT|DELETE /v3/profiles/{profileId}/campaigns/{campaignId}`。没有独立的品牌端点；专用品牌与配置文件一起创建。

<!-- sent-campaign-request -->
```json
{
  "campaign": {
    "name": "Northwind 订单通知",
    "description": "为已选择 Northwind 客户的订单和交付通知。",
    "type": "App",
    "useCases": [
      {
        "messagingUseCaseUs": "ACCOUNT_NOTIFICATION",
        "sampleMessages": [
          "Northwind: 您的订单 12345 已发货。回复 STOP 以选择退出。"
        ]
      }
    ],
    "volume": "1500",
    "messageFlow": "客户在结账时选择加入，然后通知才会开始。",
    "privacyPolicyLink": "https://example.com/privacy",
    "termsAndConditionsLink": "https://example.com/terms"
  }
}
```

`messagingUseCaseUs` 接受十三个值中的一个，`sampleMessages` 包含 1 到 5 条最多 1,024 个字符的条目，并且数值 `volume` 低于 2,000 选择低容量层，而 2,000 或以上选择标准层。活动状态是 `SENT_CREATED`、`ACTIVE` 和 `EXPIRED`。使用 `sms-10dlc-registration` 进行用例选择和样本副本策略。

## 用户和角色

五种操作管理访问权限：`GET /v3/users`、`POST /v3/users`（邀请）、`GET /v3/users/{userId}`、`PATCH /v3/users/{userId}`（角色）和 `DELETE /v3/users/{userId}`。它们均未通过 MCP 暴露。可分配的角色是 `admin`、`billing` 和 `developer`；`owner` 对创建账户是隐含的，并且永远不会出现在列表中。变异需要 `admin`。

角色检查针对拥有 API 密钥的电子邮件解析，并且仅对所有者或具有允许角色的**活动**用户通过 — `invited`、`suspended` 和 `rejected` 用户将失败。组织级访问级联到子配置文件。邀请在七天后过期，邀请现有用户将返回 `409`。

在任何用户变异之前，读取当前状态，然后明确与操作员确认。API 拒绝更改自己的角色、降级最后一个管理员、删除自己或删除最后一个管理员，但首先检查将产生清晰的解释而不是验证错误。完整的角色矩阵和密钥卫生规则在 [references/users-and-roles.md](references/users-and-roles.md) 中。

没有端点可以列出、创建或撤销 API 密钥；密钥管理是仪表板操作。轮换是创建新的、部署、使用 `GET /v3/me` 验证，然后禁用或删除旧密钥 — 仅在密钥被泄露时才首先删除。

## 多租户配置注意事项

Webhook 事件永远不会携带您的应用程序的租户标识符。在第一次发送之前，持久化 `message_id -> {tenant, profile, logical_send_id, channel}` 和 `receiving_number -> {tenant, profile}`。不要从 `account_id` 推断租户所有权，因为许多租户配置文件可以共享一个组织。为每个环境配置一个 webhook 注册，以便一个失败的较低环境接收者不会自动禁用生产。

## 边界

使用 `sender-profile-architect` 进行隔离、凭证和爆破半径设计决策；`waba-embedded-signup` 进行 WhatsApp 注册流程；`sms-10dlc-registration` 进行品牌审查和活动策略；以及 `sent-webhook-engineer` 进行订阅的消息事件接收者。配置文件完成回调使用本技能中的单独验证和轮询指南。
