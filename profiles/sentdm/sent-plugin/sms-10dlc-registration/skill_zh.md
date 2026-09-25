# SMS 10DLC 注册

使用此功能进行美国 A2P SMS 10位长码。将合规证据包与精确的 Sent API 请求分开；它们具有不同的模式（schema）和验证器（validators）。

## 当前 Sent 资源模型

当前 v3 API 中没有独立的品牌 CRUD 路径。

- 在 `POST /v3/profiles` 中创建专用品牌，使用 `brand` 并设置 `inherit_tcr_brand: false`。
- 使用 `GET|POST /v3/profiles/{profileId}/campaigns` 列出/创建活动。
- 使用 `PUT|DELETE /v3/profiles/{profileId}/campaigns/{campaignId}` 更新/删除。

拒绝重新引入独立品牌路径的建议。

## 谨慎选择继承

| 品牌 | 活动 | 设置 |
| --- | --- | --- |
| 继承两者 | 组织品牌和活动 | `inherit_tcr_brand: true`, `inherit_tcr_campaign: true` |
| 继承品牌，拥有活动 | 与租户特定流量共享的法律品牌 | 品牌为 true，活动为 false |
| 拥有两者 | 专用租户/业务 | 两者都为 false，并在创建配置文件时提供 `brand` |

继承的活动是只读的。配置文件在品牌继承为 true 时不能提供 `brand`。

## 两个验证层

### 证据准备包

私有包使用显式的内部版本 `sent-10dlc-evidence/v1` 和蛇形命名（snake_case）的证据字段。它不是 API 负载。

```bash
python scripts/validate_10dlc_packet.py evidence.json
```

收集法律身份、公共网站/政策链接、同意证明、消息流程、选择加入/选择退出/帮助响应和关键词、用例和真实样本。参见 [references/10dlc-evidence-checklist.md](references/10dlc-evidence-checklist.md)。

### Sent 活动请求

API 请求使用精确的驼峰命名（camelCase）并带有 `campaign` 包装器：

<!-- sent-campaign-request -->
```json
{
  "campaign": {
    "name": "Acme 账户通知",
    "description": "为选择加入的客户提供的账户和交付通知。",
    "type": "App",
    "useCases": [
      {
        "messagingUseCaseUs": "ACCOUNT_NOTIFICATION",
        "sampleMessages": [
          "Acme 示例：您的账户偏好已更新。回复 STOP 选择退出。"
        ]
      }
    ],
    "volume": "2000",
    "messageFlow": "客户在账户设置中选择加入，然后通知才会开始。",
    "privacyPolicyLink": "https://example.com/privacy",
    "termsAndConditionsLink": "https://example.com/terms",
    "optinMessage": "Acme 示例：您已订阅。回复 STOP 选择退出。",
    "optoutMessage": "Acme 示例：您已取消订阅，将不再收到任何消息。",
    "helpMessage": "Acme 示例：请访问 https://example.com/support 获取帮助。",
    "optinKeywords": "START,YES",
    "optoutKeywords": "STOP,UNSUBSCRIBE",
    "helpKeywords": "HELP,INFO"
  },
  "sandbox": true
}
```

使用以下命令验证：

```bash
python scripts/validate_campaign_payload.py campaign.json
```

## API 用例

支持所有 13 个当前值：

`MARKETING`, `ACCOUNT_NOTIFICATION`, `CUSTOMER_CARE`, `FRAUD_ALERT`, `TWO_FA`, `DELIVERY_NOTIFICATION`, `SECURITY_ALERT`, `M2M`, `MIXED`, `HIGHER_EDUCATION`, `POLLING_VOTING`, `PUBLIC_SERVICE_ANNOUNCEMENT`, 和 `LOW_VOLUME`。

每个用例结构上接受 1–5 个样本，每个样本不超过 1,024 个字符。合规层要求营销和混合流量至少有两个样本，包括低容量混合。保持这种政策区别，而不是假装 OpenAPI 要求所有流量都需要两个。

## 容量和状态

`volume` 是可选的，如果提供，则是一个数字字符串。值低于 `"2000"` 使用文档中说明的低容量层级；`"2000"` 是下一个层级的边界。

活动响应当前暴露 `SENT_CREATED`, `ACTIVE`, 和 `EXPIRED` 状态，以及 `submittedToTCR`。保留未知未来的状态字符串。不要将成功的 Sent 记录创建与 TCR 提交或运营商激活混淆。

## 安全工作流

1. 确认这是美国 A2P 10DLC 流量，并且实际发送业务已被识别。
2. 选择品牌/活动继承。
3. 验证版本化的证据包。
4. 创建或确认配置文件品牌。
5. 将证据翻译为精确的驼峰命名（camelCase）活动请求。
6. 本地验证并使用 `sandbox: true`。
7. 在进行真实的创建/更新/删除之前，显示负载并获取确认。
8. 存储配置文件 ID、活动 ID、`submittedToTCR`、原始状态，并审查证据。
9. 只有在先决条件准备就绪后，才使用必需的 `webHookUrl` 完成配置文件。

切勿在固定内容（fixtures）或样本中使用真实消费者数据。使用 [references/tcr-use-cases.md](references/tcr-use-cases.md) 进行分类，使用 [references/10dlc-rejection-remediation.md](references/10dlc-rejection-remediation.md) 处理失败。
