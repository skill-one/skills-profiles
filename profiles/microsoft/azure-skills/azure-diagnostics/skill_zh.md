# Azure 诊断

> **权威指导 — 强制性合规**
>
> 本文档是用于调试和解决 Azure 生产问题的**官方来源**。请遵循这些说明，系统性地诊断和解决常见的 Azure 服务问题。

## 触发条件

当用户需要执行以下操作时，激活此技能：
- 调试或解决生产问题
- 诊断 Azure 服务中的错误
- 分析应用程序日志或指标
- 修复镜像拉取、冷启动或健康探针问题
- 调查 Azure 资源失败的原因
- 找到应用程序错误的根本原因
- 解决 App Service 问题（高 CPU、部署失败、崩溃、响应缓慢、TLS/自定义域名）
- 响应类似“解决 App Service 问题”、“App Service 高 CPU”或“App Service 部署失败”的提示
- 解决 Azure Function Apps 问题（调用失败、超时、绑定错误）
- 找到与 Function App 关联的 App Insights 或 Log Analytics 工作区
- 解决 AKS 集群、节点、Pod、入口或 Kubernetes 网络问题
- 解决 Azure 虚拟机连接问题（RDP/SSH 失败、端口 3389/22 超时、网络安全组或防火墙阻止、凭证重置）
- 解决 Azure 消息 SDK 问题（Event Hubs、Service Bus 连接失败、AMQP 错误、消息锁定问题）

## 规则

1. 从系统诊断流程开始
2. 在可用时使用 AppLens (MCP) 进行 AI 驱动的诊断
3. 在深入日志之前检查资源健康状态
4. 根据服务类型选择合适的故障排除指南
5. 记录发现结果和尝试的修复步骤
6. 将 AKS 事件路由到专门的 AKS 故障排除文档

---

## 快速诊断流程

1. **识别症状** - 什么在失败？
2. **检查资源健康状态** - Azure 是否健康？
3. **查看日志** - 日志显示什么？
4. **分析指标** - 性能模式？
5. **调查最近的变化** - 发生了什么变化？

---

## 按服务划分的故障排除指南

| 服务 | 常见问题 | 参考 |
|------|----------|------|
| **容器应用** | 镜像拉取失败、冷启动、健康探针、端口不匹配 | [container-apps/](references/container-apps/README.md) |
| **App Service** | 高 CPU、部署失败、崩溃、响应缓慢、TLS/自定义域名 | [app-service/](references/app-service/README.md) |
| **Function Apps** | 应用详情、调用失败、超时、绑定错误、冷启动、缺失应用设置 | [functions/](references/functions/README.md) |
| **AKS** | 集群访问、节点、`kube-system`、调度、崩溃循环、入口、DNS、升级 | [AKS 故障排除](troubleshooting/aks/aks-troubleshooting.md) |
| **计算** | VM RDP/SSH 连接、网络安全组/防火墙阻止、凭证重置、VM 代理/工具问题 | [VM 连接故障排除](troubleshooting/compute/vm-troubleshooting.md) |
| **消息** | Event Hubs & Service Bus SDK 错误、AMQP 失败、消息锁定、连接性 | [消息故障排除](troubleshooting/messaging/README.md) |

---

## 路由

- 将容器应用和 Function Apps 的诊断保留在此父技能中。
- 将活跃的 AKS 事件、AKS 特定摄入、证据收集和修复指导路由到 [AKS 故障排除](troubleshooting/aks/aks-troubleshooting.md)。
- 将 Azure VM RDP/SSH 连接、网络安全组/防火墙、凭证重置和 VM 代理故障排除路由到 [VM 连接故障排除](troubleshooting/compute/vm-troubleshooting.md)。
- 将 Azure 消息 SDK 故障排除（Event Hubs、Service Bus）路由到 [消息故障排除](troubleshooting/messaging/README.md)。

---

## 快速参考

### 常用诊断命令

```bash
# 检查资源健康状态
az resource show --ids RESOURCE_ID
# 查看活动日志
az monitor activity-log list -g RG --max-events 20
# 容器应用日志
az containerapp logs show --name APP -g RG --follow
# Function App 日志（查询 App Insights 跟踪）
az monitor app-insights query --apps APP-INSIGHTS -g RG \
  --analytics-query "traces | where timestamp > ago(1h) | order by timestamp desc | take 50"
```

### AppLens (MCP 工具)

用于 AI 驱动的诊断：
```
mcp_azure_mcp_applens
  intent: "diagnose issues with <resource-name>"
  command: "diagnose"
  parameters:
    resourceId: "<resource-id>"

提供：
- 自动化问题检测
- 根本原因分析
- 修复建议
```

### Azure Monitor (MCP 工具)

用于查询日志和指标：
```
mcp_azure_mcp_monitor
  intent: "query logs for <resource-name>"
  command: "logs_query"
  parameters:
    workspaceId: "<workspace-id>"
    query: "<KQL-query>"
```

参考 [kql-queries.md](references/kql-queries.md) 获取常见的诊断查询。

---

## 检查 Azure 资源健康状态

### 使用 MCP

```
mcp_azure_mcp_resourcehealth
  intent: "check health status of <resource-name>"
  command: "get"
  parameters:
    resourceId: "<resource-id>"
```

### 使用 CLI

```bash
# 检查特定资源健康状态
az resource show --ids RESOURCE_ID

# 检查最近的活动
az monitor activity-log list -g RG --max-events 20
```

---

## 参考

- [KQL 查询库](references/kql-queries.md)
- [Azure 资源图查询](references/azure-resource-graph.md)
- [App Service 故障排除](references/app-service/README.md)
- [Function Apps 故障排除](references/functions/README.md)
- [VM 连接故障排除](troubleshooting/compute/vm-troubleshooting.md)
- [消息故障排除](troubleshooting/messaging/README.md)
