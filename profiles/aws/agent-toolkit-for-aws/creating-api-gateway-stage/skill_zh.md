# 创建 API 网关阶段

## 概述

创建和配置 API 网关阶段的专业知识，包括全面的日志记录、监控、安全和限流控制。涵盖 CloudWatch 日志设置、X-Ray 追踪、WAF 网页 ACL 关联、方法级别的配置和授权选项。

## 创建 API 网关阶段

要创建具有日志记录、限流、WAF 和授权的完全配置的 API 网关阶段，请严格按照程序操作。
参见 [API 网关阶段创建程序](references/create-api-gateway-stage.md)。

## 故障排除

### CloudWatch 日志未出现

验证 CloudWatch 角色权限、日志组是否存在，并确认在阶段和方法级别都已启用日志记录。有关详细信息，请参阅 [完整程序](references/create-api-gateway-stage.md)。

### 阶段创建失败

检查 REST API ID、部署 ID、IAM 权限和阶段命名约定。

### WAF 阻止合法请求

查看 WAF 日志，调整规则或添加例外，并考虑计数模式进行测试。
