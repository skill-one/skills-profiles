---
name: setting-up-cloudwatch-alarm-notifications
description: 使用 SNS 主题和订阅为 CloudWatch 告警设置通知通道。在配置告警通知时，始终使用此技能——它会创建加密的 SNS 主题，配置 CloudWatch 访问的主题策略，设置电子邮件/SMS/webhook 订阅，并使用适当的安全控制将告警与通知操作关联起来。
---

# 设置 CloudWatch 告警通知

## 概述

配置 Amazon CloudWatch 告警通知通道的领域专业知识，使用 Amazon SNS 主题和订阅。涵盖创建加密 SNS 主题、为电子邮件、短信和 webhook 端点设置订阅、配置主题策略以供 CloudWatch 访问，以及将告警链接到通知操作。

## 设置告警通知

要为 CloudWatch 告警配置通知通道，请严格按照程序操作。请参阅 [CloudWatch 告警通知设置程序](references/setup-cloudwatch-alarm-notifications.md)。

## 故障排除

### 未收到电子邮件通知

验证电子邮件订阅是否已确认。使用 `aws sns list-subscriptions-by-topic` 检查订阅状态是否为 "Confirmed" 而不是 "PendingConfirmation"。

### 短信通知失败

确保电话号码符合 E.164 格式（例如，+12345678901），并且您的 AWS 区域支持短信。

### 告警未触发通知

使用 `aws cloudwatch describe-alarms` 验证告警在其 AlarmActions 中的 SNS 主题 ARN 是否正确，并确保 ActionsEnabled 设置为 true。
