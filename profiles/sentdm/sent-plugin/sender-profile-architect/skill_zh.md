# 发送者配置架构师

发送者配置是租户身份、渠道配置、继承资源、计费和凭证的操作边界。在配置之前使用此技能，当边界不良时会混合品牌、合规性立场、速率限制影响或webhook所有权。

## 推荐的租户模型

当租户需要隔离时，建议每个租户一个发送组织和一个发送者配置。只有当租户真正共享一个品牌、发送资源、合规性立场、计费/速率限制预期和操作影响范围时，共享配置才合适。

不推荐默认池化架构。使用[references/multi-tenancy-patterns.md](references/multi-tenancy-patterns.md)明确隔离决策。

## 身份验证模式

Sent v3 支持两种模式：

| 模式 | 头部 | 影响范围 |
| --- | --- | --- |
| 特定配置的API密钥 | `x-api-key` | 配置范围的凭证和速率限制上下文。不要添加 `x-profile-id`。 |
| 代表子配置的组织API密钥 | `x-api-key` 加上 `x-profile-id: <配置UUID>` | 组织凭证可以访问允许的子配置；速率限制仍属于组织池。 |

只有组织密钥可以发送 `x-profile-id`。发送配置密钥的 `x-profile-id` 会收到 `403`。组织外的配置返回 `404`。`X-Profile-Id` 可以在范围响应中回显。

`x-sender-id` 仅是v1/v2的遗留术语。不要用于v3身份验证或路由。

选择配置密钥时，租户级凭证隔离和撤销是首要的。选择组织密钥范围用于集中控制的集成，可以保护更广泛的凭证并故意接受共享组织速率限制池。

## 配置创建模型

使用 `POST /v3/profiles` 创建。`name` 是必需的。当前可选区域包括：

- 身份：`icon`、`description`、`short_name`；
- 共享：`allow_contact_sharing`、`allow_template_sharing`；
- 继承：`inherit_contacts`、`inherit_templates`、`inherit_tcr_brand`、`inherit_tcr_campaign`；
- 计费：`billing_model`、`billing_contact` 和短暂的 `payment_details`；
- 专用WABA凭证：`whatsapp_business_account` 带有 `waba_id`、可选的 `phone_number_id` 和 `access_token`；
- 专用品牌：`brand.contact`、`brand.business` 和 `brand.compliance`。

不要添加单独的品牌端点。专用品牌与配置一起创建；活动在 `/v3/profiles/{profileId}/campaigns` 下管理。

### 继承规则

- `inherit_tcr_brand: true` 表示配置使用组织的品牌，不能提交自己的 `brand` 对象。
- `inherit_tcr_campaign: true` 使继承的活动对该配置只读。
- 带有 `inherit_tcr_campaign: false` 的继承品牌是支持的专用活动模式。
- 共享标志暴露配置的联系人/模板；继承标志消耗组织资源。分别处理这些方向。

### 计费和号码引用

`billing_model` 目前支持 `profile`、`organization` 和 `profile_and_organization`。配置或回退计费模型需要 `billing_contact`（当不存在时）。卡片字段转发到支付处理器，不得记录或持久化。

配置更新可以管理 `sending_phone_number_profile_id`、`sending_whatsapp_number_profile_id`、`sending_phone_number`、`whatsapp_phone_number` 和 `allow_number_change_during_onboarding`。分别引用模型ID和直接号码，并防止循环引用。

## WABA选择

有三个不同路径：

1. 组织嵌入仪表板中的注册。
2. 子配置继承，组织拥有WABA后省略 `whatsapp_business_account`。
3. 使用 `waba_id` 和 `access_token` 的专用配置WABA；`phone_number_id` 是可选的。

没有启动组织嵌入注册的公共端点。直接在 `POST /v3/profiles` 上的凭证不是“嵌入注册端点”。使用 `waba-embedded-signup` 用于操作流程。

## 10DLC和活动

使用配置 `brand` 对象用于专用品牌。管理活动在：

- `GET|POST /v3/profiles/{profileId}/campaigns`
- `PUT|DELETE /v3/profiles/{profileId}/campaigns/{campaignId}`

使用 `sms-10dlc-registration` 用于有效载荷和政策层。

## 完成和状态处理

使用 `POST /v3/profiles/{profileId}/complete` 和必需的 `webHookUrl` 完成配置：

```json
{
  "webHookUrl": "https://example.com/webhooks/profile-complete",
  "sandbox": true
}
```

状态是表面特定的：

- 创建响应目前显示小写的 `incomplete`。
- 完成响应 `202` 表示处理已开始且不包含最终状态。
- 完成响应 `200` 目前显示小写的 `completed` 用于已完成的配置。
- 完成回调可以报告 `COMPLETED`、`SUBMITTED` 或 `failed`。
- REST指南和OpenAPI发布不同的配置状态集。

不要声明关闭的REST枚举。保留未知字符串并记录产生它们的端点/回调表面。

## Webhook归因

Sent事件不包含您的应用程序租户ID。在发送前，将返回的 `message_id` 与租户和配置持久化。通过该映射路由出站状态事件。对于入站消息，将接收号码/配置资源映射到租户。

```text
message_id -> tenant_id, profile_id, logical_send_id, channel
receiving_number -> tenant_id, profile_id
```

不要仅从 `account_id` 推断租户所有权。多个租户配置可以属于一个组织。

## 设计清单

- [ ] 租户/品牌隔离决策是明确的。
- [ ] 凭证模式和速率限制/影响范围有文档。
- [ ] 共享和继承方向是故意的。
- [ ] 计费所有权有名称。
- [ ] 号码引用不能形成循环。
- [ ] WABA路径是组织注册、继承或专用凭证——不是虚构的混合。
- [ ] 专用品牌/活动路径基于配置。
- [ ] `message_id` 和入站号码映射支持Webhook归因。
- [ ] 未知配置状态被容忍。
- [ ] 租户下线撤销凭证、禁用发送、安全分离资源并保留审计证据。

参考[references/sender-profile-data-model.md](references/sender-profile-data-model.md)和[references/profile-boundary-examples.md](references/profile-boundary-examples.md)了解实现模式。
