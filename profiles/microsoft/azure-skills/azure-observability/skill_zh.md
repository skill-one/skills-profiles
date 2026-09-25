# Azure 可观测性服务

## 服务

| 服务 | 使用场景 | MCP 工具 | CLI |
|---------|----------|-----------|-----|
| Azure Monitor | 指标、告警、仪表板 | `azure__monitor` | `az monitor` |
| Application Insights | APM、分布式追踪 | `azure__applicationinsights` | `az monitor app-insights` |
| Log Analytics | 日志查询、KQL | `azure__kusto` | `az monitor log-analytics` |
| Alerts | 通知、操作 | - | `az monitor alert` |
| Workbooks | 交互式报告 | `azure__workbooks` | - |

## MCP 服务器（推荐）

当 Azure MCP 启用时：

### Monitor
- `azure__monitor` 使用命令 `monitor_metrics_query` - 查询指标
- `azure__monitor` 使用命令 `monitor_logs_query` - 使用 KQL 查询日志

### Application Insights
- `azure__applicationinsights` 使用命令 `applicationinsights_component_list` - 列出 App Insights 资源

### Log Analytics
- `azure__kusto` 使用命令 `kusto_cluster_list` - 列出集群
- `azure__kusto` 使用命令 `kusto_query` - 执行 KQL 查询

**如果 Azure MCP 未启用：** 运行 `/azure:setup` 或通过 `/mcp` 启用。

## CLI 参考

```bash
# 列出 Log Analytics 工作区
az monitor log-analytics workspace list --output table

# 使用 KQL 查询日志
az monitor log-analytics query \
  --workspace WORKSPACE_ID \
  --analytics-query "AzureActivity | take 10"

# 列出 Application Insights
az monitor app-insights component list --output table

# 列出告警
az monitor alert list --output table

# 查询指标
az monitor metrics list \
  --resource RESOURCE_ID \
  --metric "Percentage CPU"
```

## 常用 KQL 查询

```kql
// 近期错误
AppExceptions
| where TimeGenerated > ago(1h)
| project TimeGenerated, Message, StackTrace
| order by TimeGenerated desc

// 请求性能
AppRequests
| where TimeGenerated > ago(1h)
| summarize avg(DurationMs), count() by Name
| order by avg_DurationMs desc

// 资源使用
AzureMetrics
| where TimeGenerated > ago(1h)
| where MetricName == "Percentage CPU"
| summarize avg(Average) by Resource
```

## 监控策略

| 监控内容 | 服务 | 指标/日志 |
|-----------------|---------|------------|
| 应用程序错误 | App Insights | 异常、失败请求 |
| 性能 | App Insights | 响应时间、依赖关系 |
| 基础设施 | Azure Monitor | CPU、内存、磁盘 |
| 安全 | Log Analytics | 登录、审计日志 |
| 成本 | 成本管理 | 预算告警 |

## SDK 快速参考

要访问监控服务的编程方式，请参阅简化的 SDK 指南：

- **OpenTelemetry**: [Python](references/sdk/azure-monitor-opentelemetry-py.md) | [TypeScript](references/sdk/azure-monitor-opentelemetry-ts.md) | [Python 导出器](references/sdk/azure-monitor-opentelemetry-exporter-py.md)
- **Monitor Query**: [Python](references/sdk/azure-monitor-query-py.md) | [Java](references/sdk/azure-monitor-query-java.md)
- **Log Ingestion**: [Python](references/sdk/azure-monitor-ingestion-py.md) | [Java](references/sdk/azure-monitor-ingestion-java.md)
- **App Insights Mgmt**: [.NET](references/sdk/azure-mgmt-applicationinsights-dotnet.md)

## 服务详情

有关特定服务的深入文档：

- Application Insights 设置 -> `appinsights-instrumentation` 技能
- KQL 查询模式 -> [Log Analytics KQL 文档](https://learn.microsoft.com/azure/azure-monitor/logs/log-query-overview)
- 告警配置 -> [Azure Monitor 告警文档](https://learn.microsoft.com/azure/azure-monitor/alerts/alerts-overview)
