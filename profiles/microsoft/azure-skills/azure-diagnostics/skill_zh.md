# Azure Diagnostics

**权威指引 — 强制性合规**

本文档是**官方来源**，用于调试和排查 Azure 生产环境问题。请遵循以下说明，系统性地诊断并解决常见的 Azure 服务问题。

## Triggers

当用户希望执行以下操作时，激活此技能：
- 调试或排查生产环境问题
- 诊断 Azure 服务中的错误
- 分析应用日志或指标
- 修复镜像拉取、冷启动或健康探针问题
- 调查 Azure 资源失败的原因
- 定位应用错误的根本原因
- 排查 App Service 问题（CPU 过高、部署失败、崩溃、响应缓慢、TLS/自定义域名）
- 响应类似“排查 app service”、“app service CPU 过高”或“app service 部署失败”的提示
- 排查 Azure Function Apps（调用失败、超时、绑定错误）
- 查找与 Function App 关联的 App Insights 或 Log Analytics 工作区
- 排查 AKS 集群、节点、Pod、ingress 或 Kubernetes 网络问题
- 排查 Azure VM 连接问题（RDP/SSH 失败、端口 3389/22 超时、NSG 或防火墙拦截、凭据重置）
- 排查 Azure Messaging SDK 问题（Event Hubs、Service Bus 连接失败、AMQP 错误、消息锁问题）

## Rules

1. 以系统化的诊断流程开始
2. 当可用时，使用 AppLens（MCP）进行 AI 驱动的诊断
3. 在深入日志排查前，检查资源健康状态
4. 根据服务类型选择适当的排查指南
5. 记录发现的问题及已尝试的修复步骤
6. 将 AKS 事件路由至专门的 AKS 排查文档

---

## Quick Diagnosis Flow

1. **识别症状** - 当前故障是什么？
2. **检查资源健康状态** - Azure 运行正常吗？
3. **查阅日志** - 日志显示什么内容？
4. **分析指标** - 性能模式如何？
5. **调查近期变更** - 发生了哪些变化？

---

## Troubleshooting Guides by Service

| Service | Common Issues | Reference |
|---------|---------------|-----------|
| **Container Apps** | Image pull failures, cold starts, health probes, port mismatches | [container-apps/](references/container-apps/README.md) |
| **App Service** | High CPU, deployment failures, crashes, slow responses, TLS/custom domains | [app-service/](references/app-service/README.md) |
| **Function Apps** | App details, invocation failures, timeouts, binding errors, cold starts, missing app settings | [functions/](references/functions/README.md) |
| **AKS** | Cluster access, nodes, `kube-system`, scheduling, crash loops, ingress, DNS, upgrades | [AKS Troubleshooting](troubleshooting/aks/aks-troubleshooting.md) |
| **Compute** | VM RDP/SSH connectivity, NSG/firewall blocks, credential resets, VM agent/tooling issues | [VM Connectivity Troubleshooting](troubleshooting/compute/vm-troubleshooting.md) |
| **Messaging** | Event Hubs & Service Bus SDK errors, AMQP failures, message lock, connectivity | [Messaging Troubleshooting](troubleshooting/messaging/README.md) |

---

## Routing

- 将 Container Apps 和 Function Apps 的诊断保持在本次父级技能中。
- 将活跃的 AKS 事件、AKS 专属受理、证据收集及修复指导路由至 [AKS Troubleshooting](troubleshooting/aks/aks-troubleshooting.md)。
- 将 Azure VM RDP/SSH 连接、NSG/防火墙、凭据重置及 VM 代理排查路由至 [VM Connectivity Troubleshooting](troubleshooting/compute/vm-troubleshooting.md)。
- 将 Azure Messaging SDK 排查（Event Hubs、Service Bus）路由至 [Messaging Troubleshooting](troubleshooting/messaging/README.md)。

---

## Quick Reference

### Common Diagnostic Commands

```bash
# Check resource health
az resource show --ids RESOURCE_ID
# View activity log
az monitor activity-log list -g RG --max-events 20
# Container Apps logs
az containerapp logs show --name APP -g RG --follow
# Function App logs (query App Insights traces)
az monitor app-insights query --apps APP-INSIGHTS -g RG \
  --analytics-query "traces | where timestamp > ago(1h) | order by timestamp desc | take 50"
```

### AppLens (MCP Tools)

进行 AI 驱动的诊断时，使用：
```
mcp_azure_mcp_applens
  intent: "diagnose issues with <resource-name>"
  command: "diagnose"
  parameters:
    resourceId: "<resource-id>"

Provides:
- Automated issue detection
- Root cause analysis
- Remediation recommendations
```

### Azure Monitor (MCP Tools)

用于查询日志和指标：
```
mcp_azure_mcp_monitor
  intent: "query logs for <resource-name>"
  command: "logs_query"
  parameters:
    workspaceId: "<workspace-id>"
    query: "<KQL-query>"
```

有关常见诊断查询，请参阅 [kql-queries.md](references/kql-queries.md)。

---

## Check Azure Resource Health

### Using MCP

```
mcp_azure_mcp_resourcehealth
  intent: "check health status of <resource-name>"
  command: "get"
  parameters:
    resourceId: "<resource-id>"
```

### Using CLI

```bash
# Check specific resource health
az resource show --ids RESOURCE_ID

# Check recent activity
az monitor activity-log list -g RG --max-events 20
```

---

## References

- [KQL Query Library](references/kql-queries.md)
- [Azure Resource Graph Queries](references/azure-resource-graph.md)
- [App Service Troubleshooting](references/app-service/README.md)
- [Function Apps Troubleshooting](references/functions/README.md)
- [VM Connectivity Troubleshooting](troubleshooting/compute/vm-troubleshooting.md)
- [Messaging Troubleshooting](troubleshooting/messaging/README.md)
