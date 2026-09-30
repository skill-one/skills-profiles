---
name: troubleshooting-application-failures
description: 通过发现和分析 CloudWatch 日志组来排查故障应用程序，以识别错误模式、根本原因和可操作的解决方案。当应用程序出现故障且需要基于日志的诊断时使用。
---

# 应用程序故障排除

## 概述

通过 CloudWatch 日志分析，诊断应用程序故障的专业知识。
发现相关日志组，搜索错误模式和堆栈跟踪，执行根本原因分析，并生成优先级修复建议。

## 排除故障的应用程序

要使用 CloudWatch 日志诊断和解决应用程序故障，请严格按照以下步骤操作。请参阅 [应用程序故障排除程序](references/application-failure-troubleshooting.md)。

## 故障排除

### 未找到日志组

向用户提供具体的日志组名称。常见模式：`/aws/lambda/function-name`、`/aws/apigateway/api-name` 或自定义应用程序日志组。

### 访问被拒绝的错误

验证 AWS 凭证是否具有 `logs:DescribeLogGroups`、`logs:DescribeLogStreams`、`logs:StartQuery` 和 `logs:GetQueryResults` 权限。

### 查询超时

减少时间窗口或限制结果。大型日志组可能需要多个较小的查询。
