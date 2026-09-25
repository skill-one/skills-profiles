# Azure 成本管理技能

查询历史成本，预测未来支出，优化以减少浪费。

## 路由

| 用户意图 | 工作流 |
|-------------|----------|
| 了解当前成本 | [成本查询](cost-query/workflow.md) |
| 降低成本 / 查找浪费 | [成本优化](cost-optimization/workflow.md) |
| 预测未来成本 | [成本预测](cost-forecast/workflow.md) |

## 快速参考

| 属性 | 值 |
|----------|-------|
| **查询 API** | `POST {scope}/providers/Microsoft.CostManagement/query?api-version=2023-11-01` |
| **预测 API** | `POST {scope}/providers/Microsoft.CostManagement/forecast?api-version=2023-11-01` |
| **必需角色** | 成本管理读取者 + 监控读取者 + 目标范围内的读取者 |

## 范围模式

- 订阅: `/subscriptions/<id>`
- 资源组: `/subscriptions/<id>/resourceGroups/<name>`
- 管理组: `/providers/Microsoft.Management/managementGroups/<id>`
- 账单账户: `/providers/Microsoft.Billing/billingAccounts/<id>`

## 针对特定服务的优化

- [Redis](cost-optimization/services/redis/azure-cache-for-redis.md)
- [存储](cost-optimization/services/storage/azure-storage.md)

## 参考

- [MCP 工具、最佳实践、安全](references/tools-and-best-practices.md)
- [SDK: Redis .NET](cost-optimization/sdk/azure-resource-manager-redis-dotnet.md)
