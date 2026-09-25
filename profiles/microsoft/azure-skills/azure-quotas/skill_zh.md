# Azure 配额 - 服务限制与容量管理

> **权威指南** — 请严格按照以下说明进行配额管理和容量验证。

## 概述

**什么是 Azure 配额？**

Azure 配额（也称为服务限制）是指您可以在订阅中部署的资源数量上限。配额：
- 防止意外超额配置
- 确保在 Azure 中公平分配资源
- 代表每个区域中的**可用容量**
- 可以通过门户/CLI/API 增加的（可调整配额）或固定的（不可调整）

**关键概念：** **配额 = 资源可用性**

如果您没有配额，则无法部署资源。在规划部署或选择区域时，请始终检查配额。

## 使用此技能的场景

在以下情况下调用此技能：

- **规划新部署** - 部署前验证容量
- **选择 Azure 区域** - 比较各区域的配额可用性
- **排查配额超限错误** - 检查当前使用量与限制
- **申请配额增加** - 通过 CLI 或门户提交增加请求
- **比较区域容量** - 查找有可用配额的区域
- **验证配置限制** - 确保部署不会超过配额

## 快速参考

| **属性** | **详情** |
|--------------|-------------|
| **主要工具** | Azure CLI (`az quota`) - **始终首先使用** |
| **扩展要求** | `az extension add --name quota` (必须先安装) |
| **关键命令** | `az quota list`, `az quota show`, `az quota usage list`, `az quota usage show` |
| **完整 CLI 参考** | [commands.md](./references/commands.md) |
| **Azure 门户** | [我的配额](https://portal.azure.com/#blade/Microsoft_Azure_Capacity/QuotaMenuBlade/myQuotas) - 仅作为备用使用 |
| **REST API** | Microsoft.Quota 提供商 - **不可靠，切勿首先使用** |
| **MCP 服务器** | `azure-quota` MCP 服务器 — **绝对不要使用。它不可靠。始终使用 `az quota` CLI。** |
| **所需权限** | 阅读者（查看）或配额请求操作员（管理） |

> **⚠️ 始终首先使用 CLI**
>
> REST API 和门户可能显示误导性的“无限制”值 — 这**不代表无限容量**。这意味着配额 API 不支持该资源类型。始终从 `az quota` 命令开始；如果 CLI 返回 `BadRequest`，则回退到 [Azure 服务限制文档](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/azure-subscription-service-limits)。
>
> 完整 CLI 参考，请参阅 [commands.md](./references/commands.md)。

## 配额类型

| **类型** | **可调整性** | **审批** | **示例** |
|----------|-------------------|--------------|--------------|
| **可调整** | 可通过 Portal/CLI/API 增加 | 通常自动批准 | VM vCPUs、公共 IP、存储账户 |
| **不可调整** | 固定限制 | 无法更改 | 订阅级硬限制 |

**重要提示：** 申请配额增加是**免费**的。您只需为实际使用的资源付费，而无需为配额分配付费。

## 理解资源名称映射

**⚠️ 关键提示：** ARM 资源类型和配额资源名称之间**没有 1:1 映射**。

### 示例映射

| ARM 资源类型 | 配额资源名称 |
|-------------------|---------------------|
| `Microsoft.App/managedEnvironments` | `ManagedEnvironmentCount` |
| `Microsoft.Compute/virtualMachines` | `standardDSv3Family`, `cores`, `virtualMachines` |
| `Microsoft.Network/publicIPAddresses` | `PublicIPAddresses`, `IPv4StandardSkuPublicIpAddresses` |

### 发现工作流

**切勿假设从 ARM 类型推断出配额资源名称。** 始终使用以下工作流：

1. **列出所有配额** 对于资源提供者：
   ```bash
   az quota list --scope /subscriptions/<id>/providers/<ProviderNamespace>/locations/<region>
   ```

2. **通过 `localizedValue`（人类可读描述）匹配** 找到相关配额

3. **在后续命令中使用 `name` 字段**（不是 ARM 资源类型）：
   ```bash
   az quota show --resource-name ManagedEnvironmentCount --scope ...
   az quota usage show --resource-name ManagedEnvironmentCount --scope ...
   ```

> **📖 详细映射示例和工作流：** 请参阅 [commands.md - 资源名称映射](./references/commands.md#resource-name-mapping)

## 脚本

预构建脚本处理配额扩展安装、使用查询和容量计算。使用这些脚本而不是手动构造命令。单个调用即可返回限制、使用量和可用容量。

| 脚本 | 目的 | 使用 |
|--------|---------|-------|
| `scripts/check-quota.ps1` | 返回所有配额（或当提供资源名称时返回单个配额）的限制、使用量和可用容量 | 主要配额检查脚本 |
| `scripts/check-quota.sh` | 同上（bash） | 主要配额检查脚本 |

## 核心工作流

### 工作流 1：检查特定资源的配额

**场景：** 部署前验证配额限制和当前使用量

使用资源提供者和区域运行脚本。它在一个调用中返回所有配额及其限制、当前使用量和可用容量的表格：

```powershell
.\scripts\check-quota.ps1 -ResourceProvider <provider> -Region <region>
```
```bash
./scripts/check-quota.sh <provider> <region>
```

要检查单个资源，请添加资源名称：

```powershell
.\scripts\check-quota.ps1 -ResourceProvider <provider> -Region <region> -ResourceName <resource-name>
```
```bash
./scripts/check-quota.sh <provider> <region> <resource-name>
```

**示例：**

```powershell
.\scripts\check-quota.ps1 -ResourceProvider Microsoft.Compute -Region eastus
```

**示例输出：**

| 资源 | 区域 | 限制 | 使用量 | 可用 |
|----------|--------|-------|-------|-----------|
| cores | eastus | 100 | 50 | 50 |
| standardDSv3Family | eastus | 350 | 50 | 300 |
| virtualMachines | eastus | 25000 | 5 | 24995 |
| ... | ... | ... | ... | ... |

> **📖 另请参阅：** [az quota show](./references/commands.md#az-quota-show), [az quota usage show](./references/commands.md#az-quota-usage-show)

### 工作流 2：跨区域比较配额

**场景：** 基于可用容量查找最佳部署区域

```bash
# 定义候选区域
REGIONS=("eastus" "eastus2" "westus2" "centralus")
VM_FAMILY="standardDSv3Family"
SUBSCRIPTION_ID="<subscription-id>"

# 跨区域检查配额可用性
for region in "${REGIONS[@]}"; do
  echo "=== 检查 $region ==="
  
  # 获取限制
  LIMIT=$(az quota show \
    --resource-name $VM_FAMILY \
    --scope "/subscriptions/$SUBSCRIPTION_ID/providers/Microsoft.Compute/locations/$region" \
    --query "properties.limit.value" -o tsv)
  
  # 获取当前使用量
  USAGE=$(az quota usage show \
    --resource-name $VM_FAMILY \
    --scope "/subscriptions/$SUBSCRIPTION_ID/providers/Microsoft.Compute/locations/$region" \
    --query "properties.usages.value" -o tsv)
  
  # 计算可用量
  AVAILABLE=$((LIMIT - USAGE))
  
  echo "区域: $region | 限制: $LIMIT | 使用量: $USAGE | 可用: $AVAILABLE"
done
```

> **📖 另请参阅：** [commands.md](./references/commands.md#az-quota-show) 对于完整的跨区域脚本循环模式

### 工作流 3：申请配额增加

**场景：** 当前配额不足以部署

```bash
# 申请 VM 配额增加
az quota update \
  --resource-name standardDSv3Family \
  --scope /subscriptions/<subscription-id>/providers/Microsoft.Compute/locations/eastus \
  --limit-object value=500 \
  --resource-type dedicated

# 检查请求状态
az quota request status list \
  --scope /subscriptions/<subscription-id>/providers/Microsoft.Compute/locations/eastus
```

**审批流程：**
- 大多数可调整配额在几分钟内自动批准
- 某些请求需要人工审核（数小时到数天）
- 不可调整配额需要 Azure 支持工单

> **📖 另请参阅：** [az quota update](./references/commands.md#az-quota-update), [az quota request status](./references/advanced-commands.md#az-quota-request-status-list)

### 工作流 4：列出规划的所有配额

**场景：** 了解资源提供者在区域中的所有配额

```bash
# 列出东部的所有计算配额（表格格式）
az quota list \
  --scope /subscriptions/<subscription-id>/providers/Microsoft.Compute/locations/eastus \
  --output table

# 列出所有网络配额
az quota list \
  --scope /subscriptions/<subscription-id>/providers/Microsoft.Network/locations/eastus \
  --output table

# 列出所有 Container Apps 配额
az quota list \
  --scope /subscriptions/<subscription-id>/providers/Microsoft.App/locations/eastus \
  --output table
```

> **📖 另请参阅：** [az quota list](./references/commands.md#az-quota-list)

## 故障排除

### 常见错误

| **错误** | **原因** | **解决方案** |
|-----------|-----------|--------------|
| REST API "无限制" | 误导性 — 不是无限 | 使用 CLI；快速参考中的警告 |
| `ExtensionNotFound` | 配额扩展未安装 | `az extension add --name quota` |
| `BadRequest` | 资源提供者不受配额 API 支持 | 查看 [服务限制文档](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/azure-subscription-service-limits) |
| `MissingRegistration` | Microsoft.Quota 提供者未注册 | `az provider register --namespace Microsoft.Quota` |
| `QuotaExceeded` | 部署将超过配额 | 申请增加或选择不同区域 |
| `InvalidScope` | 范围格式不正确 | 使用模式：`/subscriptions/<id>/providers/<namespace>/locations/<region>` |
| CLI 命令完全失败 | 认证、扩展或环境问题 | 验证 Azure CLI 登录 (`az account show`)，重新安装配额扩展，检查网络。**绝对不要使用 `azure-quota` MCP 服务器。它不可靠。** |

### 不受支持的资源提供者

**已知不受支持的提供者：**
- ❌ Microsoft.DocumentDB (Cosmos DB) - 使用门户或 [Cosmos DB 限制文档](https://learn.microsoft.com/en-us/azure/cosmos-db/concepts-limits)

**确认可工作的提供者：**
- ✅ Microsoft.Compute (VMs, disks, cores)
- ✅ Microsoft.Network (VNets, IPs, load balancers)
- ✅ Microsoft.App (Container Apps)
- ✅ Microsoft.Storage (存储账户)
- ✅ Microsoft.MachineLearningServices (ML compute)

> **📖 另请参阅：** [故障排除指南](./references/commands.md#troubleshooting)

## 其他资源

| 资源 | 链接 |
|----------|------|
| **CLI 命令参考** | [commands.md](./references/commands.md) - 完整语法、参数、示例 |
| **Azure 配额概述** | [Microsoft Learn](https://learn.microsoft.com/en-us/azure/quotas/quotas-overview) |
| **服务限制文档** | [Azure 订阅限制](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/azure-subscription-service-limits) |
| **Azure 门户 - 我的配额** | [门户链接](https://portal.azure.com/#blade/Microsoft_Azure_Capacity/QuotaMenuBlade/myQuotas) |
| **申请配额增加** | [如何申请增加](https://learn.microsoft.com/en-us/azure/quotas/quickstart-increase-quota-portal) |

## 最佳实践

1. ✅ **部署前始终检查配额** - 防止配额超限错误
2. ✅ **首先运行 `az quota list`** - 发现正确的配额资源名称
3. ✅ **比较区域** - 查找有可用配额的区域
4. ✅ **预留增长空间** - 请求超出即时需求 20% 的缓冲
5. ✅ **使用表格输出进行概览** - `--output table` 用于快速扫描
6. ✅ **监控使用趋势** - 通过门户在 80% 阈值设置警报
