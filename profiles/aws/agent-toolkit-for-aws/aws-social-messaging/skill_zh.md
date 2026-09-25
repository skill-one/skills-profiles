# AWS End User Messaging Social — WhatsApp

## 概述

通过 AWS End User Messaging Social 发送 WhatsApp 消息：模板管理、发送、媒体处理、事件目的地和交付故障排除。

**推荐设置：** 使用 [AWS MCP 服务器](https://docs.aws.amazon.com/agent-toolkit/latest/userguide/mcp-server.html) 进行沙盒执行、审计日志和企业控制。

**不使用 AWS MCP：** 此技能可与任何具有 AWS CLI 访问权限的代理工作。所有命令使用标准 AWS CLI 语法。

## 常见任务

### 1. 验证依赖项

**约束条件：**

- 推荐使用 AWS MCP 服务器以实现无缝 API 执行，但不是必需的——所有命令使用标准 AWS CLI 语法
- 您必须验证已安装并配置了适当的凭证的 AWS CLI
- 您应建议用户假设具有临时凭证的 IAM 角色
- 如果缺少任何必需工具，您必须告知用户如何安装/配置它
- 您必须询问用户是否希望在缺少任何工具的情况下继续
- 如果 `aws socialmessaging` 子命令不被识别，用户必须更新到最新的 AWS CLI 版本
- 必需的 IAM 权限（范围到特定的 WABA 和电话号码 ARN）：
  - 模板：`social-messaging:CreateWhatsAppMessageTemplate`、`social-messaging:GetWhatsAppMessageTemplate`、`social-messaging:ListWhatsAppMessageTemplates`、`social-messaging:UpdateWhatsAppMessageTemplate`、`social-messaging:DeleteWhatsAppMessageTemplate`、`social-messaging:ListWhatsAppTemplateLibrary`、`social-messaging:CreateWhatsAppMessageTemplateFromLibrary`
  - 发送：`social-messaging:SendWhatsAppMessage`
  - 媒体：`social-messaging:PostWhatsAppMessageMedia`、`social-messaging:CreateWhatsAppMessageTemplateMedia`、`social-messaging:GetWhatsAppMessageMedia`、`social-messaging:DeleteWhatsAppMessageMedia`
  - 事件：`social-messaging:PutWhatsAppBusinessAccountEventDestinations`
  - 诊断：`social-messaging:GetLinkedWhatsAppBusinessAccount`、`social-messaging:GetLinkedWhatsAppBusinessAccountPhoneNumber`、`social-messaging:ListLinkedWhatsAppBusinessAccounts`
  - 支持性：`sns:ListSubscriptionsByTopic`、`iam:PassRole`（用于事件目的地角色）

### 2. 管理模板

创建、更新和删除消息模板（实用、营销、认证）。

- `create-whatsapp-message-template`：base64 编码 `--template-definition`（blob 类型）
- `create-whatsapp-message-template-from-library`：使用预先批准的 Meta 库模板
- `list-whatsapp-template-library`：浏览可用的库模板
- `get-whatsapp-message-template`：通过 `--id`（WABA）和 `--meta-template-id` 检索模板详细信息
- `update-whatsapp-message-template`：修改现有模板内容
- `delete-whatsapp-message-template`：需要 `--template-name`（不是 `--meta-template-name`）；始终包括 `--delete-all-languages`
- `list-whatsapp-message-templates`：响应字段是 `templateStatus` 和 `templateCategory`（不是 `status`/`category`）
- 具有 `{{N}}` 参数的模板必须包括 `"parameter_format": "positional"`（例外：AUTHENTICATION——Meta 自动处理 OTP 参数）和 `"example"`
- Meta 审核所有模板（几分钟到 24 小时）；必须不使用 PENDING/REJECTED 发送
- 选择错误的类别会导致重新分类（UTILITY → MARKETING），这会改变定价——有关选择 UTILITY vs MARKETING vs AUTHENTICATION 的指导，请参阅 [managing-templates.md — Choosing the Right Category](references/managing-templates.md)
- 您必须在创建模板之前与用户确认预期的类别（UTILITY、MARKETING 或 AUTHENTICATION）——解释分类标准以及如果选择不明确，则重新分类的风险

参见 [managing-templates.md](references/managing-templates.md)。

### 3. 发送消息

#### 模板消息（无 24 小时限制）

- 用于：事务性更新（实用）、促销（营销）、验证码（认证）
- 收集：电话号码 ID、收件人（E.164 带有 `+`）、模板名称、语言、参数
- 营销模板可以包含图像标题
- `--message` 是 blob 类型——必须 base64 编码 JSON

#### 自由格式消息（需要 24 小时窗口）

- 用于：在客户最后接收到的消息后的 24 小时内回复客户服务
- 支持：文本、图像、文档、视频、音频——有关支持的格式和大小限制，请参阅 [WhatsApp Cloud API 媒体参考](https://developers.facebook.com/docs/whatsapp/cloud-api/reference/media)
- 没有 API 可以检查窗口状态——用户必须从日志或事件历史记录中确认
- 媒体 URL 必须是公开可访问的 HTTPS，并且在完整的 30 天消息可用性窗口期间保持可用（Meta 可以随时重新获取）。对于敏感内容（收据、发票、PII），通过 `post-whatsapp-message-media` 上传并通过媒体 ID 引用，而不是使用预签名 URL——预签名 URL 无法满足 30 天可用性要求

**所有发送的约束条件：**

- 在执行任何 API 调用之前，验证参数格式：
  - 电话号码 ID 匹配 `phone-number-id-*` 模式
  - WABA ID 匹配 `waba-*` 模式
  - 收件人号码是 E.164 并带有 `+` 前缀（例如，`+14155551234`），或通过 `"recipient"` 字段使用业务范围用户 ID（BSUID）
  - 模板名称只包含小写字母、数字和下划线
  - 语言代码使用 Meta 的区域格式，带有下划线（例如，`en_US`、`pt_BR`）
  - `--meta-api-version` 是 `v{Major}.{Minor}` 格式（例如，`v21.0`）
- `"messaging_product"` 在 JSON 正文必须是 `"whatsapp"`；检查 [Meta 的 Graph API 变更日志](https://developers.facebook.com/docs/graph-api/changelog) 以获取支持的 Meta Graph API 版本
- `--message` 是 blob 类型——必须 base64 编码 JSON 负载
- 成功的 `messageId` 表示已排队，而不是已交付
- 您必须提前一次性提示所有必需参数
- 您必须接受参数作为单独的值、JSON 对象或文件引用
- 您必须在执行之前解释每个步骤
- 您应执行之前确认所有参数
- 您必须尊重用户中止的决定
- 您必须未经用户确认不发送每批超过 5 条消息
- 您必须未经用户确认不直接创建或访问凭证

参见 [sending-messages.md](references/sending-messages.md)。

### 4. 管理媒体

上传、检索和删除用于消息和模板标题的媒体。

- `post-whatsapp-message-media`：上传媒体，返回可重用的媒体 ID
- `create-whatsapp-message-template-media`：上传专门用于模板标题的媒体
- `get-whatsapp-message-media`：通过 ID 检索媒体元数据/URL
- `delete-whatsapp-message-media`：删除已上传的媒体

参见 [managing-media.md](references/managing-media.md)。

### 5. 配置事件目的地

设置交付跟踪、模板状态通知和重新分类警报。

设置交付跟踪、模板状态通知和重新分类警报。一个 WABA 只能有一个事件目的地。有关前提条件（IAM 角色、使用 KMS 加密的 SNS 主题、仅限 HTTPS 的订阅端点、条件键）和完整安全控制的详细信息，请参阅 [configuring-event-destinations.md](references/configuring-event-destinations.md)。

### 6. 排除交付故障

诊断流程：WABA 状态 → 电话号码 → 模板 → 事件目的地 → 配额。

- `get-linked-whatsapp-business-account`：注册必须为 COMPLETE
- `get-linked-whatsapp-business-account-phone-number`：验证电话号码健康状况
- `list-linked-whatsapp-business-accounts`：列出所有 WABAs
- 模板重新分类：可通过事件目的地（实时）或通过列出模板并比较类别来检测；删除并重新创建
- 24 小时窗口过期：使用模板消息
- 速率限制：新 WABAs 的限制较低；随着质量提高而增加
- 没有 WhatsApp 的收件人：静默丢弃

参见 [troubleshooting-delivery.md](references/troubleshooting-delivery.md)。

## 快速参考——常见错误

- **访问被拒绝**：验证范围到 WABA/电话号码 ARN 的 IAM 权限
- **模板被拒绝**：正文必须匹配类别；包括 `parameter_format` 和 `example`
- **模板重新分类**：配置事件目的地以检测；删除并重新创建
- **24 小时窗口过期**：使用模板消息而不是自由格式
- **发送失败**：`--origination-phone-number-id` 是 ID（不是电话号码）；收件人是 E.164 并带有 `+`
- **已排队但未交付**：200 = 已排队；配置事件目的地以获取状态
- **媒体 URL 无法访问**：必须是公开可访问的 HTTPS

## 安全注意事项

- 使用范围到特定 `social-messaging:` 操作和 WABA/电话号码 ARN 的最小权限 IAM 策略
- 使用 IAM 角色而不是长期访问密钥的临时凭证
- 将密钥存储在 AWS Secrets Manager 或 Parameter Store 中——绝不能存储在代码或环境变量中
- 启用 CloudTrail 以审计所有 `social-messaging` API 调用；使用 KMS CMK 加密日志
- 使用 KMS 加密事件目的地的 SNS 主题（回调包含收件人元数据）
- 如果监控 social-messaging 活动，则使用 KMS 加密 CloudWatch 日志
- 避免在模板参数和自由格式消息内容中包含敏感数据（它们会出现在 CloudTrail 日志中）
- 验证收件人电话号码以防止未经授权的消息
- 验证 SNS 订阅端点是否由您的团队授权——验证所有订阅的电子邮件地址和系统是否属于应接收敏感交付状态和收件人元数据的员工/系统，然后再确认订阅。使用仅限 HTTPS 的端点
- 在 SNS 主题策略中添加条件键（`aws:SourceArn`、`aws:SourceAccount`）以防止混淆代理攻击
- 通过服务配额和 CloudWatch 警报在发送速率上实施速率限制

## 其他资源

- [AWS End User Messaging Social 用户指南](https://docs.aws.amazon.com/social-messaging/latest/userguide/what-is-service.html)
- [AWS CLI socialmessaging 参考](https://docs.aws.amazon.com/cli/latest/reference/socialmessaging/)
- [开始使用 WhatsApp](https://docs.aws.amazon.com/social-messaging/latest/userguide/getting-started-whatsapp.html)
- [管理事件目的地](https://docs.aws.amazon.com/social-messaging/latest/userguide/managing-event-destinations-add.html)
- [服务配额](https://docs.aws.amazon.com/social-messaging/latest/userguide/quotas.html)
- [IAM 安全最佳实践](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [混淆代理预防](https://docs.aws.amazon.com/IAM/latest/UserGuide/confused-deputy.html)
- [SNS 数据保护最佳实践](https://docs.aws.amazon.com/sns/latest/dg/sns-security-best-practices.html)
- [AWS Well-Architected 安全支柱](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/welcome.html)
