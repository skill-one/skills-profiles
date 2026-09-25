# 使用最佳实践创建密钥

## 概述

在 AWS Secrets Manager 中创建和管理密钥的领域专业知识，具有生产级安全控制：KMS 加密、自动轮换、最小权限 IAM 策略、CloudTrail 审计和生命周期管理。

## 使用最佳实践创建密钥

要在 AWS Secrets Manager 中创建一个安全配置正确的密钥，请严格按照程序操作。请参阅 [密钥创建程序](references/create-secrets-using-best-practices.md)。

该程序支持四种密钥类型：数据库凭证、API 密钥、OAuth 令牌和自定义密钥。每种类型都按适当的结构进行组织，并使用专用的 KMS 密钥进行加密。

## 故障排除

### KMS 密钥访问问题

验证 IAM 实体具有 `kms:CreateKey` 和 `kms:PutKeyPolicy` 权限，并且密钥策略授予 `kms:GenerateDataKey`、`kms:Decrypt` 和 `kms:DescribeKey`，范围限定为 `kms:ViaService` 到 `secretsmanager.<region>.amazonaws.com`。请参阅完整程序以获取详细信息。

### 轮换设置失败

检查 Lambda 轮换函数是否存在、具有适当的权限，并且可以访问目标系统。查看轮换函数的 CloudWatch 日志。

### 密钥访问被拒绝

验证 IAM 策略是否附加到正确的实体，KMS 密钥策略允许解密（以及为写入/轮换的 `kms:GenerateDataKey`），并且实体正在使用 HTTPS。请参阅完整程序以获取详细信息。
