# 账单和成本管理

## 概述

分析、优化和管理 AWS 成本。这项技能编码了 AWS 成本管理产品中的领域专业知识——常见问题、正确的 API 使用模式以及模型经常出错的最佳实践工作流。

## 使用场景

在以下情况下使用此技能：

- 分析 AWS 支出、成本趋势或成本细分
- 设置或管理预算警报
- 评估 Savings Plans 或 Reserved Instance 购买
- 调整 EC2、Lambda、RDS 或 EBS 资源
- 查询 AWS 服务定价
- 运行成本审计或调查成本激增
- 使用 Athena 查询 CUR 数据
- 将成本分析范围限定在特定的账单视图
- 检查免费层使用情况

## 核心概念

- **成本探索器** — 按服务、账户、标签或时间范围查询成本/使用数据
- **预算** — 设置支出阈值并附带警报；支持账单视图范围限定
- **账单视图** — 将成本数据限定在账单的子集（自定义视图、账单组或主视图）
- **计算优化器** — EC2、Lambda、EBS、RDS 的调整大小建议
- **成本优化中心** — 跨服务的聚合节省建议
- **Savings Plans / Reserved Instances** — 基于承诺的折扣
- **CUR 2.0** — 可通过 Athena 查询的详细明细账单数据

**推荐设置**：使用 AWS MCP 服务器进行沙盒执行、审计日志记录和企业控制。参见：https://docs.aws.amazon.com/aws-mcp/

**没有 AWS MCP**：所有命令使用标准 AWS CLI 语法，并可与任何具有 CLI 访问权限的代理一起使用。

## 严格规则：始终检查当前日期

**在执行任何成本探索器、预算或 Savings Plans API 调用之前，你必须必须确定当前日期。** 使用工具获取当前日期和时间——不要假设或猜测年份。LLM 经常默认使用其训练数据中的日期，而不是实际当前日期，导致分析结果看似正确但实际上完全错误。

## 严格规则：确定性计算

**你绝不能通过推理在响应中执行数值计算（求和、平均值、百分比、比较、计数、最小/最大值）。** LLM 算术不可靠，并且在成本数据上会产生错误答案。

**你必须始终使用脚本或计算工具** 对 API 调用返回的数据进行任何数学计算。编写一个执行计算并打印结果的 Python 脚本。如果 AWS MCP 服务器的 `run_script` 工具可用，请使用它。否则，在本地运行脚本。

阅读 `references/deterministic-calculations.md` 了解模式和示例。

## 决策指南

| 问题 | 工具 | 参考 |
|------|------|------|
| 我正在花费多少？成本在哪里上升？ | 成本探索器 | `references/cost-explorer.md` |
| 一个服务的成本是多少？ | 价格列表 API | `references/pricing-lookup.md` |
| 我在哪里可以省钱？（从这里开始） | 成本优化中心 | `references/cost-optimization-hub.md` |
| 我应该购买 Savings Plans 吗？ | CE SP 建议 | `references/savings-plans.md` |
| 我应该购买 Reserved Instances 吗？ | CE RI 建议 | `references/reserved-instances.md` |
| 深入了解特定的 EC2/Lambda/EBS/RDS 建议？ | 计算优化器 | `references/ec2-rightsizing.md`, `references/lambda-optimization.md`, `references/rds-optimization.md`, `references/ebs-optimization.md` |
| 我该如何设置预算警报？ | 预算 | `references/budgets.md` |
| 成本激增的原因是什么？ | 成本异常检测 | `references/cost-explorer.md` |
| 我在免费层范围内吗？ | 免费层 API | `references/free-tier.md` |
| 我如何减少账单？ | 成本审计工作流 | `references/cost-audit.md` |
| 我如何查询详细账单数据？ | CUR 2.0 + Athena | `references/cur-athena.md` |
| 我如何优化特定服务？ | 每个服务的模式 | `references/service-optimization.md` |
| 我如何将成本限定在账单视图？ | 账单视图 | 见下文 `#账单视图` |

## 常见任务

### 按服务分析成本

```bash
aws ce get-cost-and-usage \
  --time-period Start=2026-03-01,End=2026-04-01 \
  --granularity MONTHLY \
  --metrics UnblendedCost \
  --group-by Type=DIMENSION,Key=SERVICE
```

默认使用 `UnblendedCost`。使用 `--filter '{"Not":{"Dimensions":{"Key":"RECORD_TYPE","Values":["Credit","Refund"]}}}'` 排除信用/退款。结束日期是排他的。

### 运行成本审计
阅读 `references/cost-audit.md` 了解完整的 7 步工作流：主要成本驱动因素 → 逐月比较 → 优化建议 → 空闲资源 → 承诺覆盖率 → 每个服务的快速胜利 → 报告。

### 获取调整大小建议
计算优化器需要首先选择加入：`aws compute-optimizer update-enrollment-status --status Active`。然后阅读 `references/ec2-rightsizing.md` 了解 EC2 或相关资源特定参考。

### 查询服务定价
阅读 `references/pricing-lookup.md` 了解服务代码和属性过滤器。常见陷阱：价格列表 API 服务代码与成本探索器服务名称不同。

## 账单视图

账单视图将成本和使用数据限定在账户账单的特定切片（例如，账单组、自定义视图或默认主视图）。当用户想要通过特定账单视图分析成本时，向支持的 API 调用添加 `--billing-view-arn`。

### 发现可用的账单视图

```bash
aws billing list-billing-views \
  --billing-view-types PRIMARY CUSTOM BILLING_GROUP
```

需要 `billing:ListBillingViews` 权限。

### 使用账单视图与成本探索器

```bash
aws ce get-cost-and-usage \
  --time-period Start=2026-03-01,End=2026-04-01 \
  --granularity MONTHLY \
  --metrics UnblendedCost \
  --group-by Type=DIMENSION,Key=SERVICE \
  --billing-view-arn arn:aws:billing::ACCOUNT_ID:billingview/BILLING_VIEW_ID
```

### 创建限定在账单视图的预算
在 `--budget` JSON 中包含 `BillingViewArn` 字段：

```bash
aws budgets create-budget --account-id ACCOUNT_ID \
  --budget '{
    "BudgetName": "TeamX-Monthly",
    "BudgetLimit": {"Amount": "1000", "Unit": "USD"},
    "TimeUnit": "MONTHLY",
    "BudgetType": "COST",
    "BillingViewArn": "arn:aws:billing::ACCOUNT_ID:billingview/BILLING_VIEW_ID"
  }'
```

### 支持 `--billing-view-arn` 的 API

| 支持 `--billing-view-arn` | 不支持它 |
|--------------------------|----------|
| `ce get-cost-and-usage` | `ce get-reservation-coverage` |
| `ce get-cost-and-usage-with-resources` | `ce get-reservation-utilization` |
| `ce get-cost-forecast` | `ce get-savings-plans-coverage` |
| `ce get-usage-forecast` | `ce get-savings-plans-utilization` |
| `ce get-dimension-values` | |
| `ce get-tags` | |
| `ce get-cost-comparison-drivers` | |
| `budgets create-budget` (在预算 JSON 中) | |

## 故障排除

| 错误 | 原因 | 解决方法 |
|------|------|------|
| 成本探索器上的 `ValidationException` | 维度键错误（例如，`CHARGE_TYPE` 而不是 `RECORD_TYPE`） | 使用 `RECORD_TYPE` 进行收费类型过滤 |
| 过滤器结果为空 | 过滤器值与实际值不匹配 | 首先调用 `GetDimensionValues` 获取有效值 |
| 小时数据上的 `AccessDeniedException` | 小时粒度未启用 | 在成本探索器设置中启用 |
| 计算优化器上的 `Account not registered` | 未选择加入 | 运行 `update-enrollment-status --status Active` |
| 账单 API 在 us-east-1 外失败 | 账单需要 us-east-1 | 设置 `--region us-east-1` |
| 成本探索器 `Total` 在分组时为空 | 设计如此——分组时排除总计 | 使用脚本进行单独调用，或对分组结果求和 |
| `list-billing-views` 上的 `AccessDeniedException` | 缺少权限 | 用户需要 `billing:ListBillingViews` 权限 |
| 使用 `--billing-view-arn` 时的 `ValidationException` | API 不支持账单视图，或 ARN 格式错误 | 检查上表中的 API 支持表；ARN 格式为 `arn:aws:billing::ACCOUNT_ID:billingview/VIEW_ID` |
| 预算显示 `UNHEALTHY` 健康状态 | 账单视图访问被撤销或视图被删除 | 检查 `describe-budget` 输出中的 `HealthStatus.StatusReason`；确保 `billing:GetBillingViewData` 被授予 |

## 其他资源

- AWS 成本管理用户指南：https://docs.aws.amazon.com/cost-management/
- AWS 定价计算器：https://calculator.aws/
- 计算优化器用户指南：https://docs.aws.amazon.com/compute-optimizer/
- Well-Architected 成本优化支柱：https://docs.aws.amazon.com/wellarchitected/latest/cost-optimization-pillar/
