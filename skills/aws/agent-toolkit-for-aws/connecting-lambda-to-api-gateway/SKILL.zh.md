---
name: connecting-lambda-to-api-gateway
description: 通过创建具有资源/方法设置、Lambda 代理集成、权限和部署的 REST 或 HTTP API，将现有的 AWS Lambda 函数连接到 Amazon API Gateway。在将 Lambda 连接到 API Gateway 时，始终使用此技能——它处理容易遗漏的 CORS、限流、访问日志记录和生产安全加固。
---

# 将 Lambda 连接到 API Gateway

## 概述

创建 Amazon API Gateway REST API 并将其连接到现有 Lambda 函数的专业知识。涵盖 API 创建、资源和方法的设置、Lambda 代理集成、CORS 配置、安全控制、部署和测试。

## 将 Lambda 函数连接到 API Gateway

要创建 REST API 并将其连接到 Lambda 函数，请严格按照流程操作。参见 [Lambda 到 API Gateway 连接流程](references/lambda-gateway-api.md)。

该流程支持可配置的授权类型（NONE、AWS_IAM、COGNITO_USER_POOLS、CUSTOM）、可选的 API 密钥要求、CORS 设置以及生产安全加固，包括限流和访问日志记录。

## 故障排除

### 502 Bad Gateway

Lambda 函数必须返回一个与代理兼容的响应，包含 `statusCode`、`headers` 和字符串化的 `body`。参见完整流程了解格式详情。

### 调用 Lambda 时权限被拒绝

确保已添加 `lambda:InvokeFunction` 权限，并使用正确的 API Gateway 源 ARN。参见完整流程了解详情。

### 浏览器中的 CORS 错误

验证 `enable_cors` 是否设置为 true，是否创建了 OPTIONS 方法，以及方法响应和集成响应中是否配置了 CORS 标头。
