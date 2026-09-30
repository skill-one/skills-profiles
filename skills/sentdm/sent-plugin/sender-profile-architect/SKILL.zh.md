---
name: sender-profile-architect
description: 为多租户、多品牌和多渠道系统设计了发送者配置文件架构。用于API密钥作用域、x-profile-id、隔离、继承、共享、计费、WABA、10DLC活动、webhooks或租户下线。
---

# 发送者配置架构师

发送者配置是租户身份、渠道配置、继承资源、计费和凭证的操作边界。在配置之前使用此技能，当边界不良会混合品牌、合规状态、速率限制影响或webhook所有权时。

## 推荐的租户模型

当租户需要隔离时，建议每个租户一个发送组织和一个发送者配置。只有当租户真正共享一个品牌、发送资源、合规状态、计费/速率限制预期和操作影响范围时，共享配置才合适。

不推荐默认池化架构。使用[references/multi-tenancy-patterns.md](references/multi-tenancy-patterns.md)明确隔离决策。

## 身份验证模式

Sent v3支持两种：

| 模式 | 标头 | 影响范围 |
| --- | --- | --- |
| 特定配置的API密钥 | `x-api-key` | 配置范围的凭证和速率限制上下文。不要添加`x-profile-id`。 |
| 代表子配置的组织API密钥 | `x-api-key`加上`x-profile-id: <配置UUID>` | 组织凭证可以访问允许的子配置；速率限制仍属于组织池。 |

只有组织密钥可以发送`x-profile-id`。发送配置密钥的`x-profile-id`会收到`403`。组织外的配置返回`404`。`X-Profile-Id`可以在作用域响应中回显。

`x-sender-id`是仅限v1/v2的遗留术语。不要用于v3身份验证或路由。

选择配置密钥时，租户级凭证隔离和撤销是主要考虑因素。选择组织密钥作用域用于集中控制的集成，可以保护更广泛的凭证并故意接受共享组织速率限制池。

## 配置创建模型

使用`POST /v3/profiles`创建。`name`是必需的。当前可选区域包括：

- 身份：`icon`、`description`、`short_name`；
- 共享：`allow_contact_sharing`、`allow_template_sharing`；
- 继承：`inherit_contacts`、`inherit_templates`、`inherit_tcr_brand`、`inherit_tcr_campaign`；
- 计费：`billing_model`、`billing_contact`和暂时的`payment_details`；
- 专用WABA凭证：`whatsapp_business_account`带有`waba_id`、可选的`phone_number_id`和`access_token`；
- 专用品牌：`brand.contact`、`brand.business`和`brand.compliance`。

不要添加单独的品牌端点。专用品牌随配置创建；活动在`/v3/profiles/{profileId}/campaigns`下管理。

### 继承规则

- `inherit_tcr_brand: true`表示配置使用组织的品牌，不能提交自己的`brand`对象。
- `inherit_tcr_campaign: true`使继承的活动对该配置只读。
- 带有`inherit_tcr_campaign: false`的继承品牌是支持的专用活动模式。
- 共享标志暴露配置的联系人/模板；继承标志消耗组织资源。分别处理这些方向。

### 计费和号码引用

`billing_model`当前支持`profile`、`organization`和`profile_and_organization`。配置或回退计费模型需要`billing_contact`。卡字段转发到支付处理器，不得记录或持久化。

配置更新可以管理`sending_phone_number_profile_id`、`sending_whatsapp_number_profile_id`、`sending_phone_number`、`whatsapp_phone_number`和`allow_number_change_during_onboarding`。分别引用模型ID和直接号码，并防止循环引用。

## WABA选择

有三个不同的路径：

1. 控制面板中的组织嵌入式注册。
2. 组织有WABA后省略`whatsapp_business_account`的子配置继承。
3. 使用`waba_id`和`access_token`的专用配置WABA；`phone_number_id`是可选的。

没有启动组织嵌入式注册的公共端点。直接在`POST /v3/profiles`上的凭证不是“嵌入式注册端点”。使用`waba-embedded-signup`进行操作流程。

## 10DLC和活动

使用配置`brand`对象进行专用品牌。在以下位置管理活动：

- `GET|POST /v3/profiles/{profileId}/campaigns`
- `PUT|DELETE /v3/profiles/{profileId}/campaigns/{campaignId}`

使用`sms-10dlc-registration`进行有效载荷和政策层。

## 完成和状态处理

使用`POST /v3/profiles/{profileId}/complete`和必需的`webHookUrl`完成配置：

```json
{
  "webHookUrl": "https://example.com/webhooks/profile-complete",
  "sandbox": true
}
```

状态因表面而异：

- 创建响应当前显示小写的`incomplete`。
- 完成响应`202`表示处理已开始且不包含最终状态。
- 完成响应`200`当前显示小写的`completed`，用于已完成的配置。
- 完成回调可以报告`COMPLETED`、`SUBMITTED`或`failed`。
- REST指南和OpenAPI发布不同的配置状态集。

不要断言关闭的REST枚举。保留未知字符串并记录产生它们的端点/回调表面。

## Webhook归因

Sent事件不包含您的应用程序租户ID。在发送前，将返回的`message_id`与租户和配置持久化。通过该映射路由出站状态事件。对于入站消息，将接收号码/配置资源映射到租户。

```text
message_id -> tenant_id, profile_id, logical_send_id, channel
receiving_number -> tenant_id, profile_id
```

不要仅从`account_id`推断租户所有权。多个租户配置可以属于一个组织。

## 设计清单

- [ ] 租户/品牌隔离决策是明确的。
- [ ] 凭证模式和速率限制/影响范围有文档记录。
- [ ] 共享和继承方向是故意的。
- [ ] 计费所有权有名称。
- [ ] 号码引用不能形成循环。
- [ ] WABA路径是组织注册、继承或专用凭证——不是虚构的混合。
- [ ] 专用品牌/活动路径基于配置。
- [ ] `message_id`和入站号码映射支持Webhook归因。
- [ ] 未知配置状态被容忍。
- [ ] 租户下线撤销凭证、禁用发送、安全分离资源并保留审计证据。

参考[references/sender-profile-data-model.md](references/sender-profile-data-model.md)和[references/profile-boundary-examples.md](references/profile-boundary-examples.md)了解实现模式。
