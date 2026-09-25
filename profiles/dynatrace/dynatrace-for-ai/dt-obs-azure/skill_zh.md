# Azure 云基础设施

使用 Dynatrace Smartscape 和 DQL 监控和分析 Azure 资源。查询 Azure 服务、审计安全性、管理组织层次结构，并规划 Azure 基础设施的整体容量。

## 何时使用此技能

当用户需要在 Dynatrace 中处理 Azure 资源时，请使用此技能。加载任务类型的参考文件：

| 任务 | 要加载的文件 |
|---|---|
| 库存和拓扑查询 | （无需额外文件 — 使用以下核心模式） |
| 查询 Azure 指标时间序列（CPU、延迟、吞吐量） | 加载 `references/metrics-performance.md` |
| VNet 拓扑、子网、NSGs、公共 IP、VPN、对等连接 | 加载 `references/vnet-networking-security.md` |
| Azure SQL、Cosmos DB、PostgreSQL、Redis 调查 | 加载 `references/database-monitoring.md` |
| 函数、App Service、AKS 基础设施、容器应用 | 加载 `references/serverless-containers.md` |
| Azure LB、应用网关、前端网关、API 管理 | 加载 `references/load-balancing-api.md` |
| WAF 规则分析、误报调查 | 加载 `references/load-balancing-api.md` |
| Event Hubs、Service Bus、Event Grid | 加载 `references/messaging-integration.md` |
| 存储账户、Blob、文件、队列、表 | 加载 `references/storage-monitoring.md` |
| 未附加资源、标签合规性、生命周期 | 加载 `references/resource-management.md` |
| 成本节约、未使用资源、SKU 分析 | 加载 `references/cost-optimization.md` |
| 容量裕量、VMSS 扩展、配额 | 加载 `references/capacity-planning.md` |
| 安全审计、加密、公共访问、Key Vault | 加载 `references/security-compliance.md` |
| NSG 规则分析（0.0.0.0/0、开放端口） | 加载 `references/security-compliance.md` |
| 存储账户加密/公共访问审计 | 加载 `references/security-compliance.md` |
| 成本分配、分摊、所有权 | 加载 `references/resource-ownership.md` |
| 确定编排上下文（AKS、VMSS、独立） | 加载 `references/workload-detection.md` |

---

## 核心概念

### 实体类型

Azure 资源使用 `AZURE_*` 前缀，并可通过 `smartscapeNodes` 函数进行查询。所有 Azure 实体都会自动在 Dynatrace Smartscape 中发现和建模。实体类型名称是从 ARM 资源提供者路径派生的：`/Microsoft.Compute/virtualMachines` 变成 `AZURE_MICROSOFT_COMPUTE_VIRTUALMACHINES`。子资源使用下划线追加：`/Microsoft.Sql/servers/databases` 变成 `AZURE_MICROSOFT_SQL_SERVERS_DATABASES`。

**计算：** `AZURE_MICROSOFT_COMPUTE_VIRTUALMACHINES`, `AZURE_MICROSOFT_COMPUTE_VIRTUALMACHINESCALESETS`, `AZURE_MICROSOFT_COMPUTE_VIRTUALMACHINESCALESETS_VIRTUALMACHINES`, `AZURE_MICROSOFT_COMPUTE_DISKS`, `AZURE_MICROSOFT_COMPUTE_SSHPUBLICKEYS`, `AZURE_MICROSOFT_COMPUTE_VIRTUALMACHINES_EXTENSIONS`
**网络：** `AZURE_MICROSOFT_NETWORK_VIRTUALNETWORKS`, `AZURE_MICROSOFT_NETWORK_VIRTUALNETWORKS_SUBNETS`, `AZURE_MICROSOFT_NETWORK_NETWORKSECURITYGROUPS`, `AZURE_MICROSOFT_NETWORK_PUBLICIPADDRESSES`, `AZURE_MICROSOFT_NETWORK_NETWORKINTERFACES`, `AZURE_MICROSOFT_NETWORK_LOADBALANCERS`, `AZURE_MICROSOFT_NETWORK_APPLICATIONGATEWAYS`, `AZURE_MICROSOFT_NETWORK_VIRTUALNETWORKGATEWAYS`, `AZURE_MICROSOFT_NETWORK_CONNECTIONS`, `AZURE_MICROSOFT_NETWORK_EXPRESSROUTECIRCUITS`
**数据库：** `AZURE_MICROSOFT_SQL_SERVERS`, `AZURE_MICROSOFT_SQL_SERVERS_DATABASES`, `AZURE_MICROSOFT_CACHE_REDIS`, `AZURE_MICROSOFT_CACHE_REDISENTERPRISE`, `AZURE_MICROSOFT_DOCUMENTDB_DATABASEACCOUNTS`
**存储：** `AZURE_MICROSOFT_STORAGE_STORAGEACCOUNTS`, `AZURE_MICROSOFT_STORAGE_STORAGEACCOUNTS_BLOBSERVICES_CONTAINERS`, `AZURE_MICROSOFT_STORAGE_STORAGEACCOUNTS_FILESERVICES_SHARES`, `AZURE_MICROSOFT_STORAGE_STORAGEACCOUNTS_QUEUESERVICES_QUEUES`, `AZURE_MICROSOFT_STORAGE_STORAGEACCOUNTS_TABLESERVICES_TABLES`
**Kubernetes/容器：** `AZURE_MICROSOFT_CONTAINERSERVICE_MANAGEDCLUSTERS`, `AZURE_MICROSOFT_CONTAINERSERVICE_MANAGEDCLUSTERS_AGENTPOOLS`, `AZURE_MICROSOFT_CONTAINERREGISTRY_REGISTRIES`, `AZURE_MICROSOFT_APP_CONTAINERAPPS`, `AZURE_MICROSOFT_APP_MANAGEDENVIRONMENTS`, `AZURE_MICROSOFT_APP_JOBS`
**App Service：** `AZURE_MICROSOFT_WEB_SITES`, `AZURE_MICROSOFT_WEB_SERVERFARMS`, `AZURE_MICROSOFT_WEB_SITES_FUNCTIONS`
**消息：** `AZURE_MICROSOFT_EVENTHUB_NAMESPACES`, `AZURE_MICROSOFT_EVENTHUB_NAMESPACES_EVENTHUBS`, `AZURE_MICROSOFT_SERVICEBUS_NAMESPACES`, `AZURE_MICROSOFT_SERVICEBUS_NAMESPACES_QUEUES`, `AZURE_MICROSOFT_SERVICEBUS_NAMESPACES_TOPICS`, `AZURE_MICROSOFT_SERVICEBUS_NAMESPACES_TOPICS_SUBSCRIPTIONS`
**安全/身份：** `AZURE_MICROSOFT_KEYVAULT_VAULTS`, `AZURE_MICROSOFT_MANAGEDIDENTITY_USERASSIGNEDIDENTITIES`
**监控：** `AZURE_MICROSOFT_OPERATIONALINSIGHTS_WORKSPACES`, `AZURE_MICROSOFT_INSIGHTS_COMPONENTS`
**API 管理：** `AZURE_MICROSOFT_APIMANAGEMENT_SERVICE`

### Azure 组织层次结构

Azure 以三个级别的层次结构组织资源：**租户 > 订阅 > 资源组**。每个资源都属于订阅中一个资源组内的资源。使用以下字段来限定查询范围：

```dql-snippet
filter azure.subscription == "08b9810e-..."
```

```dql-snippet
filter azure.resource.group == "my-rg"
```

```dql-snippet
filter azure.location == "eastus"
```

结合这些过滤器进行精确限定：

```dql-template
smartscapeNodes "AZURE_*"
| filter azure.subscription == "<SUBSCRIPTION_ID>"
    and azure.resource.group == "<RESOURCE_GROUP>"
    and azure.location == "<REGION>"
| summarize count = count(), by: {type}
| sort count desc
```

要查看整个环境中的组织结构分解：

```dql
smartscapeNodes "AZURE_*"
| summarize resource_count = count(), by: {azure.subscription, azure.resource.group}
| sort resource_count desc
```

### 常见 Azure 字段

所有 Azure 实体都包含：
- `azure.subscription` — Azure 订阅 GUID
- `azure.resource.group` — 资源组名称
- `azure.location` — Azure 区域（例如，`eastus`，`polandcentral`）
- `azure.resourceType` — ARM 资源类型（例如，`microsoft.compute/virtualmachines`）
- `azure.provisioning_state` — 配置状态（例如，`Succeeded`）
- `azure.object` — 完整 ARM 资源 JSON（参见 [使用 AzureObject 进行配置解析](#configuration-parsing-with-azureobject)）
- `cloud.provider` — 始终为 `azure`
- `tags` — 资源标签（使用 `` tags[`key`] ``）

某些实体类型还具有：
- `azure.resourceId` — 完整 ARM 资源 ID（虚拟机和其他一些）
- `azure.resourceName` — 资源名称（虚拟机和其他一些）
- `azure.availabilityZones` — 可用区列表（虚拟机）

### 关系类型

Azure 实体关系可以使用 `traverse` 进行遍历。`dt.traverse.relationship` 字段对于 Azure 实体**未填充**，因此您必须在所有遍历命令中使用 `"*"` 作为关系名称。

关键遍历对：
- **VM → 磁盘：** `traverse "*", "AZURE_MICROSOFT_COMPUTE_DISKS"`
- **VM → 网络接口卡：** `traverse "*", "AZURE_MICROSOFT_NETWORK_NETWORKINTERFACES"`
- **VM → VMSS：** `traverse "*", "AZURE_MICROSOFT_COMPUTE_VIRTUALMACHINESCALESETS"`
- **VM → 可用区：** `traverse "*", "AZURE_MICROSOFT_RESOURCES_LOCATIONS_AVAILABILITYZONES"`
- **VM ← 扩展：** `traverse "*", "AZURE_MICROSOFT_COMPUTE_VIRTUALMACHINES_EXTENSIONS", direction:backward`
- **VMSS → AKS 集群：** `traverse "*", "AZURE_MICROSOFT_CONTAINERSERVICE_MANAGEDCLUSTERS"`
- **VMSS → 子网：** `traverse "*", "AZURE_MICROSOFT_NETWORK_VIRTUALNETWORKS_SUBNETS"`
- **VMSS → NSGs：** `traverse "*", "AZURE_MICROSOFT_NETWORK_NETWORKSECURITYGROUPS"`
- **VMSS → 负载均衡器后端池：** `traverse "*", "AZURE_MICROSOFT_NETWORK_LOADBALANCERS_BACKENDADDRESSPOOLS"`
- **子网 → VNet：** `traverse "*", "AZURE_MICROSOFT_NETWORK_VIRTUALNETWORKS"`
- **子网 → NSG：** `traverse "*", "AZURE_MICROSOFT_NETWORK_NETWORKSECURITYGROUPS"`
- **子网 ← VMSS：** `traverse "*", "AZURE_MICROSOFT_COMPUTE_VIRTUALMACHINESCALESETS", direction:backward`
- **NSG ← 网络接口卡：** `traverse "*", "AZURE_MICROSOFT_NETWORK_NETWORKINTERFACES", direction:backward`
- **NSG ← 子网：** `traverse "*", "AZURE_MICROSOFT_NETWORK_VIRTUALNETWORKS_SUBNETS", direction:backward`
- **负载均衡器 → 后端池：** `traverse "*", "AZURE_MICROSOFT_NETWORK_LOADBALANCERS_BACKENDADDRESSPOOLS"`
- **负载均衡器 → 前端 IP：** `traverse "*", "AZURE_MICROSOFT_NETWORK_LOADBALANCERS_FRONTENDIPCONFIGURATIONS"`
- **负载均衡器 → 负载均衡器规则：** `traverse "*", "AZURE_MICROSOFT_NETWORK_LOADBALANCERS_LOADBALANCINGRULES"`
- **SQL 服务器 ← SQL 数据库：** `traverse "*", "AZURE_MICROSOFT_SQL_SERVERS_DATABASES", direction:backward`
- **存储账户 ← Blob 容器：** `traverse "*", "AZURE_MICROSOFT_STORAGE_STORAGEACCOUNTS_BLOBSERVICES_CONTAINERS", direction:backward`
- **存储账户 ← 文件共享：** `traverse "*", "AZURE_MICROSOFT_STORAGE_STORAGEACCOUNTS_FILESERVICES_SHARES", direction:backward`
- **AKS ← VMSS：** `traverse "*", "AZURE_MICROSOFT_COMPUTE_VIRTUALMACHINESCALESETS", direction:backward`
- **AKS ← Agent 池：** `traverse "*", "AZURE_MICROSOFT_CONTAINERSERVICE_MANAGEDCLUSTERS_AGENTPOOLS", direction:backward`
- **AKS ← NSGs：** `traverse "*", "AZURE_MICROSOFT_NETWORK_NETWORKSECURITYGROUPS", direction:backward`
- **AKS ← 公共 IP：** `traverse "*", "AZURE_MICROSOFT_NETWORK_PUBLICIPADDRESSES", direction:backward`
- **AKS → 公共 IP：** `traverse "*", "AZURE_MICROSOFT_NETWORK_PUBLICIPADDRESSES"`
- **网站 → App Service 计划：** `traverse "*", "AZURE_MICROSOFT_WEB_SERVERFARMS"`
- **网站 ← 函数：** `traverse "*", "AZURE_MICROSOFT_WEB_SITES_FUNCTIONS", direction:backward`
- **容器应用 → 管理环境：** `traverse "*", "AZURE_MICROSOFT_APP_MANAGEDENVIRONMENTS"`
- **EventHub 命名空间 ← Event Hubs：** `traverse "*", "AZURE_MICROSOFT_EVENTHUB_NAMESPACES_EVENTHUBS", direction:backward`
- **ServiceBus 命名空间 ← 队列：** `traverse "*"
