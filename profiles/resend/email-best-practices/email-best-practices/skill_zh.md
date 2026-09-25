# 邮件最佳实践

构建可送达、合规、用户友好的邮件的指导。

## 架构概述

```
[用户] → [邮件表单] → [验证] → [双重选择加入]
                                              ↓
                                    [已记录同意]
                                              ↓
[屏蔽检查] ←──────────────[准备发送]
        ↓
[幂等发送 + 重试] ──────→ [邮件 API]
                                       ↓
                              [Webhook 事件]
                                       ↓
              ┌────────┬────────┬─────────────┐
              ↓        ↓        ↓             ↓
         已送达  退回  投诉  打开/点击
                       ↓        ↓
              [屏蔽列表更新]
                       ↓
              [列表清洁任务]
```

## 快速参考

| 需要执行... | 查看 |
|------------|-----|
| 设置 SPF/DKIM/DMARC，修复垃圾邮件问题 | [可送达性](./references/deliverability.md) |
| 构建密码重置、OTP、确认邮件 | [事务性邮件](./references/transactional-emails.md) |
| 规划您的应用程序需要哪些邮件 | [事务性邮件目录](./references/transactional-email-catalog.md) |
| 构建订阅表单，验证邮件 | [邮件收集](./references/email-capture.md) |
| 发送订阅表单、促销邮件 | [营销邮件](./references/marketing-emails.md) |
| 确保遵守 CAN-SPAM/GDPR/CASL | [合规性](./references/compliance.md) |
| 确定事务性邮件与营销邮件 | [邮件类型](./references/email-types.md) |
| 处理重试、幂等性、错误 | [发送可靠性](./references/sending-reliability.md) |
| 处理送达事件，设置 Webhooks | [Webhooks & 事件](./references/webhooks-events.md) |
| 管理退回、投诉、屏蔽 | [列表管理](./references/list-management.md) |
| 使邮件可访问（屏幕阅读器、替代文本、对比度） | [可访问性](./references/accessibility.md) |

## 从这里开始

**新应用程序？**
从 [目录](./references/transactional-email-catalog.md) 开始，规划您的应用程序需要哪些邮件（密码重置、验证等），然后设置 [可送达性](./references/deliverability.md)（DNS 认证）再发送第一封邮件。

**垃圾邮件问题？**
首先检查 [可送达性](./references/deliverability.md)—认证问题是最常见的原因。Gmail/Yahoo 会拒绝未认证的邮件。

**营销邮件？**
遵循此路径：[邮件收集](./references/email-capture.md)（收集同意）→ [合规性](./references/compliance.md)（法律要求）→ [营销邮件](./references/marketing-emails.md)（最佳实践）。

**生产就绪的发送？**
添加可靠性：[发送可靠性](./references/sending-reliability.md)（重试 + 幂等性）→ [Webhooks & 事件](./references/webhooks-events.md)（跟踪送达）→ [列表管理](./references/list-management.md)（处理退回）。

**可访问性？**
大多数邮件无法通过基本可访问性检查。查看 [可访问性](./references/accessibility.md) 了解 `lang`/`dir`、展示性表格、标题、替代文本、`<title>` 和对比度。
