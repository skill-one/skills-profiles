# 设置跨区域 CloudTrail

## 概述

具备在所有区域启用 AWS CloudTrail 的专业知识，以捕获全面的 API 活动日志，并配置 CloudWatch Logs Insights 进行安全监控、合规审计和运营分析。

## 设置跨区域跟踪

要创建具有 S3 存储的跨区域 CloudTrail 跟踪，并集成 CloudWatch Logs 进行日志分析，请严格按照以下步骤操作。
请参阅 [CloudTrail 跨区域设置步骤](references/cloudtrail-multi-region-setup.md)。

## 故障排除

### S3 存储桶已存在

选择一个不同的全球唯一名称，或添加时间戳或组织标识符。

### 权限被拒绝错误

使用 `aws sts get-caller-identity` 验证您的身份。确保您的用户/角色已附加所需的操作。**不要**使用 `*FullAccess` 管理策略。

### 跟踪未记录日志

验证 IAM 角色的权限，检查 S3 存储桶策略允许 CloudTrail 访问，并确保使用 `start-logging` 启动跟踪。

### CloudWatch 中缺少事件

允许 5-15 分钟的初始日志传递时间。验证 CloudWatch Logs 角色的 ARN 是否正确，并确保日志组与跟踪位于同一区域。

### 选定区域的事件未出现

这是正常的——选定区域的事件可能需要几个小时。在进一步调查之前，请等待长达 24 小时。
