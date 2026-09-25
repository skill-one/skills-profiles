# WABA 引导和嵌入式注册

保持三种集成路径的独立性。将它们全部称为“嵌入式注册”会导致错误的 API 设计和不安全的凭证处理。

## 三种路径

| 路径 | 起点 | 配置文件行为 |
| --- | --- | --- |
| 组织嵌入式注册 | 发送仪表板 | 通过托管 Meta 流连接组织的 WABA。没有公共的发送端点可以启动此流程。 |
| 组织 WABA 继承 | `POST /v3/profiles` | 省略 `whatsapp_business_account`；子配置文件继承组织的已连接 WABA。 |
| 专用子配置文件 WABA | `POST /v3/profiles` | 提供 `whatsapp_business_account.waba_id` 和 `.access_token`；`phone_number_id` 是可选的。 |

如果省略凭证且组织没有连接的 WABA，配置文件创建将返回 `422`。直接 WABA 凭证是配置文件创建功能，而不是公共的“嵌入式注册端点。”

## 身份验证

使用以下任一方式：

- 在 `x-api-key` 中使用特定于配置文件的密钥；或
- 在 `x-api-key` 中使用组织密钥，并在为现有子配置文件操作时加上 `x-profile-id`。

只有组织密钥可以使用 `x-profile-id`；配置文件密钥将收到 `403`。`x-sender-id` 是遗留的 v1/v2 术语。

## 路径 A：组织嵌入式注册

1. 授权的组织管理员打开发送仪表板的 WhatsApp 连接流程。
2. 托管的 Meta 嵌入式注册 UI 收集 Meta 授权和 WABA/号码选择。
3. 在创建继承的子配置文件之前，确认组织显示已连接的 WABA。
4. 记录非秘密标识符并审计完成操作的人员。

不要在发送的公共 API 中发明 `POST /embedded-signup` 或令牌交换端点。如果在不发送仪表板外构建自己的 Meta Tech Provider 集成，请遵循 Meta 的当前文档，并将该系统与发送 API 合同分开。

Meta 的浏览器 `postMessage` 事件使用 `event` 字段和嵌套数据/会话信息。不要将它们重写为发送 webhook `sub_type` 封装。

## 路径 B：继承组织 WABA

省略 `whatsapp_business_account`：

```json
{
  "name": "租户支持",
  "description": "合成子配置文件",
  "short_name": "SUPPORT",
  "inherit_templates": true,
  "billing_model": "organization",
  "sandbox": true
}
```

仅在组织 WABA 连接后使用此方法。继承意味着租户共享该 WABA 边界；确认这与租户/品牌架构匹配。

## 路径 C：专用 WABA 凭证

```json
{
  "name": "专用租户",
  "whatsapp_business_account": {
    "waba_id": "123456789012345",
    "phone_number_id": "987654321098765",
    "access_token": "<注入的秘密>"
  },
  "sandbox": true
}
```

`waba_id` 和 `access_token` 是必需的。`phone_number_id` 是可选的：当省略时，当前合同描述在引导过程中进行配置和注册。

令牌需要适用的 WhatsApp Business 消息和管理权限。从秘密管理器中注入它。永远不要记录它、回显它、写入到 fixtures、返回给浏览器、包含在支持输出中或在一般配置文件存储中保留它。发送不会在 API 响应中返回它。

## 完成配置文件

使用所需的 `webHookUrl` 调用 `POST /v3/profiles/{profileId}/complete`：

```json
{
  "webHookUrl": "https://example.com/webhooks/profile-complete",
  "sandbox": true
}
```

- `202` 表示后台处理已开始；该响应中没有最终状态。
- `200` 可能表示配置文件已经完成，并且当前显示小写的 `completed`。
- 完成回调可以报告 `COMPLETED`、`SUBMITTED` 或 `failed`。

将完成回调视为自己的集成表面。其封装使用 `event` 而不是 `sub_type`：

```json
{
  "event": "COMPLETED",
  "profile_id": "00000000-0000-0000-0000-000000000000",
  "timestamp": "2026-08-09T12:00:00Z"
}
```

保留未知事件字符串。使用发送文档为回调端点指定的机制验证真实性，并使处理幂等。

## 验证操作就绪

- 配置文件 WABA ID 与预期业务匹配。
- 选择的号码映射到预期配置文件。
- 模板共享/继承是故意的。
- 可以使用 `sandbox: true` 创建测试模板。
- 完成回调是可访问的且幂等的。
- 返回的消息 ID 在 webhook 处理之前存储在租户/配置文件中。
- 令牌和支付值不在日志中。

对于普通消息和模板 webhook，请遵循发送的当前事件参考；那些与 Meta 浏览器事件和配置文件完成回调是分开的。

## 失败路由

| 失败 | 下一步操作 |
| --- | --- |
| 省略凭证时返回 `422` | 连接组织 WABA 或提供专用凭证。 |
| 使用配置文件密钥和 `x-profile-id` 返回 `403` | 移除 `x-profile-id` 或使用授权的组织密钥。 |
| 错误的 WABA/号码 | 在完成前停止并更正配置文件映射。 |
| 过期/权限不足的令牌 | 安全地替换它；在诊断时永远不要打印它。 |
| 完成仍然提交 | 检查先决条件和回调证据；不要假设从 `202` 得到的最终失败。 |

使用 [references/waba-embedded-signup-spec.md](references/waba-embedded-signup-spec.md)、[references/waba-onboarding-runbook.md](references/waba-onboarding-runbook.md) 和 [references/whatsapp-sender-profile-mapping.md](references/whatsapp-sender-profile-mapping.md)。使用 `sender-profile-architect` 表示租户边界，使用 `waba-template-author` 表示第一个模板。
