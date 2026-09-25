# 调试 Lambda 超时

## 概述

通过分析函数配置、CloudWatch 日志、指标、依赖项、冷启动模式和代码，系统地调查 AWS Lambda 函数超时失败的领域专业知识。识别常见原因，如超时设置不足、外部服务延迟、数据库连接问题、内存限制和低效的代码模式，然后提供优先级建议。

## 调试 Lambda 超时

要调查和解决 Lambda 超时问题，请严格按照程序进行。参见 [Lambda 超时调试程序](references/lambda-timeout-debugging.md)。

该程序收集函数配置、CloudWatch 指标和日志、依赖项分析以及冷启动模式。如果提供了 Lambda 代码，它还会检查代码中的超时易发模式。结果汇总成一个结构化的调试报告，包含优先级建议。

## 故障排除

### 未找到函数

验证函数名称和区域。使用 `aws lambda list-functions --region <region>` 列出可用函数。

### 无日志可用

函数可能最近未被调用或日志可能已禁用。检查函数的日志组配置和调用指标。

### 访问被拒绝错误

验证 AWS 凭证对 Lambda、CloudWatch 日志和 CloudWatch 指标的权限。参见完整程序了解详情。

### 日志查询时间范围问题

如果 CloudWatch Logs Insights 查询因时间范围错误而失败，请减小分析窗口或检查日志组保留设置。参见完整程序了解详情。
