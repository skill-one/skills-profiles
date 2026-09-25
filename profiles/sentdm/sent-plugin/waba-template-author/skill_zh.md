# WhatsApp 模板作者

使用此技能将消息意图转换为有效的 `POST /v3/templates` 正文，审核其 WhatsApp 政策风险，并解释结果的生命周期。Sent 的模板请求不是 Meta Cloud API 的 `components[]` 结构。

## 源优先级

当官方来源不一致时：

1. 使用实时 Sent v3 OpenAPI 获取路径、请求字段和响应结构。
2. 使用最具体的当前 Sent 指南获取生命周期和政策语义。
3. 保留未知提供者值，而不是将它们强制转换为封闭的枚举。

规范参考是 Sent 模板定义指南、v3 OpenAPI 和 webhook 事件参考。不要使用快照时代的 v2 示例。

## 作者工作流程

### 1. 确立意图和类别

收集业务事件、接收者期望、请求操作、语言、渠道覆盖和现实样本值。选择：

- `UTILITY` 用于特定非促销交易、账户或服务事件。
- `MARKETING` 用于促销、优惠、再参与、产品发现或混合促销内容。
- `AUTHENTICATION` 用于一次性验证码和支持的认证流程。

如果内容混合了实用性和促销，将其归类为营销或拆分。参见 [references/waba-template-categories.md](references/waba-template-categories.md)。

### 2. 构建 Sent 创建请求

`POST /v3/templates` 接受以下顶层字段：

| 字段 | 要求 |
| --- | --- |
| `definition` | 必填。包含 `header`、`body`、`footer`、`buttons`、可选的 `definitionVersion` 和可选的 `authenticationConfig`。 |
| `category` | 可选：`UTILITY`、`MARKETING` 或 `AUTHENTICATION`；当歧义可接受时省略以进行检测。 |
| `language` | 可选区域设置，如 `en_US`。 |
| `creation_source` | 可选源字符串；`from-api` 是文档中记录的默认值。 |
| `submit_for_review` | 可选布尔值；默认 `false`。在审核前草拟和验证。 |
| `sandbox` | 可选布尔值，用于无副作用验证。 |

不要在请求根目录放置 `name`、`channels`、`body`、`header`、`buttons` 或 `components`。`name` 存在于更新/响应表面，而不是当前的创建请求中。

```json
{
  "category": "UTILITY",
  "language": "en_US",
  "definition": {
    "header": null,
    "body": {
      "multiChannel": {
        "type": "body",
        "template": "Hi {{0:variable}}, order {{1:variable}} has shipped.",
        "variables": [
          {
            "id": 0,
            "name": "customerName",
            "type": "variable",
            "props": {"sample": "Avery"}
          },
          {
            "id": 1,
            "name": "orderNumber",
            "type": "variable",
            "props": {"sample": "A-1042"}
          }
        ]
      },
      "sms": null,
      "whatsapp": null,
      "rcs": null
    },
    "footer": null,
    "buttons": null,
    "definitionVersion": "1.0",
    "authenticationConfig": null
  },
  "creation_source": "from-api",
  "submit_for_review": false,
  "sandbox": true
}
```

使用 `definition.body.multiChannel` 作为渠道无关的正文。`sms`、`whatsapp` 和 `rcs` 是完整的渠道覆盖，不是片段。保持每个正文在 1,024 字符或以下。

### 3. 精确定义变量

使用占位符，如 `{{0:variable}}`、`{{1:link}}` 或 `{{2:media}}`。每个占位符需要一个匹配的定义，包含：

- 唯一的非负整数 `id`；
- 可读的 `name`；
- 匹配的 `type`；
- `props.sample` 包含现实的审核和预览数据。

保持占位符 ID 和变量 ID 在每个正文覆盖中一致。Sent 请求中永远不会输出裸 `{{1}}` 占位符。

### 4. 添加支持的按钮

Sent 目前识别 `QUICK_REPLY`、`URL`、`VOICE_CALL`、`PHONE_NUMBER` 和 `COPY_CODE`。强制执行：

- 总共 10 个按钮；
- 最多 2 个 URL 按钮；
- 最多 1 个语音呼叫按钮；
- 最多 1 个电话号码按钮；
- 最多 1 个复制代码按钮；
- 快速回复可以使用剩余插槽，最多 10 个。

按钮使用 `id`、`type` 和 `props`。标签最多 25 个字符。要求类型特定属性：`quickReplyType`；`urlType` 和 `url`；`countryCode` 和 `phoneNumber`；或 `offerCode`。快速回复和行动号召可以共存——不要发明 XOR 规则。

### 5. 处理认证模板

对于 `AUTHENTICATION`，使用 `definition.authenticationConfig`：

```json
{
  "addSecurityRecommendation": true,
  "codeExpirationMinutes": 10
}
```

过期时间为 1–90 分钟。保持认证内容仅用于验证目的，使用一个代码变量和支持的复制代码操作，不要添加营销语言、无关链接、媒体或促销按钮。

### 6. 提交前验证

运行：

```bash
python scripts/lint_waba_template.py template.json
```

校验器验证 Sent 请求结构、变量、1,024 字符限制、渠道覆盖、每个当前按钮类型、类型限制和认证配置。带有 `components[]` 的 Meta Cloud API 示例必须因显式转换错误而失败。

集成时使用 `sandbox: true` 和 `submit_for_review: false`。当用户准备好提供者审核时，显示最终有效负载并解释提交会改变外部状态，然后继续。

### 7. 跟踪正确生命周期表面

Sent 模板资源使用已知状态 `DRAFT`、`PENDING`、`APPROVED`、`REJECTED` 和 `PAUSED`。不要声称这是 API 可能返回的所有值。

模板 webhook 是 WhatsApp 批准事件。它们使用 `field: "templates"`，省略 `sub_type` 和 `event`，并在 `payload.status` 中携带提供者状态：

```json
{
  "field": "templates",
  "timestamp": "2026-08-09T12:00:00Z",
  "payload": {
    "account_id": "00000000-0000-0000-0000-000000000000",
    "template_id": "11111111-1111-1111-1111-111111111111",
    "template_name": "order_update",
    "whatsapp_template_id": "2222222222222222",
    "status": "APPROVED",
    "language": "en_US",
    "category": "UTILITY",
    "channel": "whatsapp",
    "reason": null
  }
}
```

常见的转发值包括 `PENDING`、`APPROVED`、`REJECTED` 和 `CATEGORY_UPDATED`。Meta 还可以发送值，如 `PAUSED` 或 `DISABLED`。持久化原始字符串，处理已知值，并安全地显示未知值。参见 [references/template-rejection-playbook.md](references/template-rejection-playbook.md)。

## 边界

使用 `template-builder-ui` 进行编辑器架构和客户端验证 UX。使用 `sent-templates` 列出、检查或删除现有模板通过连接的 Sent 工具。使用 `waba-embedded-signup` 进行 WABA 连接。使用 `rcs-agent-onboarding` 进行当前 RCS 启动能力。

Meta Cloud API 有效负载可能出现在 [references/waba-template-examples.md](references/waba-template-examples.md) 中，但每个此类示例必须明确标记为非 Sent，并且永远不要将其作为有效请求传递给 Sent 校验器。
