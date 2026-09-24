# Azure Quotas - Service Limits & Capacity Management

> **AUTHORITATIVE GUIDANCE** — 请严格按照以下指引进行配额管理和容量验证。

## Overview

**What are Azure Quotas?**

Azure 配额（也称服务限制）是在订阅中您可以部署的最大资源数量。配额：
- 防止意外超额配置
- 确保在 Azure 中实现资源分配公平
- 代表各区域中的**可用容量**
- 可增加（可调整配额）或固定（不可调整）

**关键概念：** **Quotas = Resource Availability**

如果没有配额，则无法部署资源。规划部署或选择区域时，请始终检查配额。

## When to Use This Skill

当以下情况时，调用此技能：

- **规划新部署** - 部署前验证容量
- **选择 Azure 区域** - 比较各区域配额可用性
- **排查配额超限错误** - 检查当前使用量与限制
- **申请配额增加** - 通过 CLI 或门户提交增加申请
- **比较区域容量** - 查找拥有可用配额的 region
- **验证配置限制** - 确保部署不会超出配额

## Quick Reference

| **属性** | **详情** |
|----------|-------------|
| **主要工具** | Azure CLI（`az quota`）—— **优先使用，始终如此** |
| **所需扩展** | `az extension add --name quota`（**必须先安装**） |
| **关键命令** | `az quota list`，`az quota show`，`az quota usage list`，`az quota usage show` |
| **完整 CLI 参考** | [commands.md](./references/commands.md) |
| **Azure 门户** | [我的配额](https://portal.azure.com/#blade/Microsoft_Azure_Capacity/QuotaMenuBlade/myQuotas) - 仅作备用方案 |
| **REST API** | Microsoft.Quota 提供程序 - **不可靠，请勿优先使用** |
| **MCP 服务** | `azure-quota` MCP 服务 —— **切勿使用。其不可靠。始终使用 `az quota` CLI。** |
| **所需权限** | Reader（查看）或 Quota Request Operator（管理） |

> **⚠️ 始终优先使用 CLI**
>
> REST API 和门户可能显示具有误导性的"无限制"数值——这**不**意味着容量无限。它表示配额 API 不支持该资源类型。始终以 `az quota` 命令开始；若 CLI 返回 `BadRequest`，则回退至 [Azure 服务限制文档](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/azure-subscription-service-limits)。
>
> 完整的 CLI 参考，请见 [commands.md](./references/commands.md)。

## Quota Types

| **类型** | **可调整性** | **审批** | **示例** |
|----------|-------------------|--------------|--------------|
| **可调整** | 可通过门户/CLI/API 增加 | 通常自动审批 | VM vCPUs、公共 IP、存储账户 |
| **不可调整** | 固定限制 | 不可更改 | 订阅级硬性限制 |

**重要：** 申请配额增加是**免费**的。您仅对实际使用的资源付费，而非为配额分配付费。

## Understanding Resource Name Mapping

**⚠️ 关键：** ARM 资源类型与配额资源名称之间**不存在** 1:1 映射关系。

### 示例映射

| ARM 资源类型 | 配额资源名称 |
|---------------------|---------------------|
| `Microsoft.App/managedEnvironments` | `ManagedEnvironmentCount` |
| `Microsoft.Compute/virtualMachines` | `standardDSv3Family`，`cores`，`virtualMachines` |
| `Microsoft.Network/publicIPAddresses` | `PublicIPAddresses`，`IPv4StandardSkuPublicIpAddresses` |

### 发现工作流程

**切勿**从 ARM 类型假设配额资源名称。始终使用以下工作流程：

1. **列出资源提供商的全部配额：**
   ```bash
   az quota list --scope /subscriptions/<id>/providers/<ProviderNamespace>/locations/<region>
   ```

2. **通过 `localizedValue`（人类可读描述）匹配**，找到相关配额

3. **在后续命令中使用 `name` 字段**（而非 ARM 资源类型）：
   ```bash
   az quota show --resource-name ManagedEnvironmentCount --scope ...
   az quota usage show --resource-name ManagedEnvironmentCount --scope ...
   ```

> **📖 详细映射示例和工作流程：** 参见 [commands.md - Resource Name Mapping](./references/commands.md#resource-name-mapping)

## Scripts

预置脚本可处理配额扩展安装、使用量查询和容量计算。请使用以下脚本，而非手动构建命令。一次调用即可返回限制、使用量和可用容量。

| 脚本 | 用途 | 用法 |
|--------|---------|-------|
| `scripts/check-quota.ps1` | 返回所有配额（或提供资源名称时返回单个配额的）限制、使用量和可用容量 | 配额检查的主脚本 |
| `scripts/check-quota.sh` | 与上述相同（bash） | 配额检查的主脚本 |

## Core Workflows

### Workflow 1: 检查特定资源的配额

**场景：** 在部署前验证配额限制和当前使用量

使用资源提供程序和区域运行脚本。一次调用返回包含**全部**配额的**限制、当前使用量**和**可用容量**的表格：

```powershell
.\scripts\check-quota.ps1 -ResourceProvider <provider> -Region <region>
```
```bash
./scripts/check-quota.sh <provider> <region>
```

检查单个资源时，需添加资源名称：

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
|----------|--------|-------|-------|--------|
| cores | eastus | 100 | 50 | 50 |
| standardDSv3Family | eastus | 350 | 50 | 300 |
| virtualMachines | eastus | 25000 | 5 | 24995 |
| ... | ... | ... | ... | ... |

> **📖 另请参见：** [az quota show](./references/commands.md#az-quota-show)，[az quota usage show](./references/commands.md#az-quota-usage-show)

### Workflow 2: 跨区域比较配额

**场景：** 根据可用容量查找最佳部署区域

```bash
# 定义候选区域
REGIONS=("eastus" "eastus2" "westus2" "centralus")
VM_FAMILY="standardDSv3Family"
SUBSCRIPTION_ID="<subscription-id>"

# 检查跨区域的配额可用性
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
  
  # 计算可用
  AVAILABLE=$((LIMIT - USAGE))
  
  echo "Region: $region | Limit: $LIMIT | Usage: $USAGE | Available: $AVAILABLE"
done
```

> **📖 另请参见：** [commands.md](./references/commands.md#az-quota-show) 中完整的脚本化多区域循环模式

### Workflow 3: 申请配额增加

**场景：** 当前配额不足以部署

```bash
# 为 VM 配额申请增加
az quota update \
  --resource-name standardDSv3Family \
  --scope /subscriptions/<subscription-id>/providers/Microsoft.Compute/locations/eastus \
  --limit-object value=500 \
  --resource-type dedicated

# 检查申请状态
az quota request status list \
  --scope /subscriptions/<subscription-id>/providers/Microsoft.Compute/locations/eastus
```

**审批流程：**
- 大多数可调整配额在几分钟内自动审批
- 部分申请需要人工审核（数小时至数天）
- 不可调整配额需要 Azure 支持工单

> **📖 另请参见：** [az quota update](./references/commands.md#az-quota-update)，[az quota request status](./references/advanced-commands.md#az-quota-request-status-list)

### Workflow 4: 为规划列出全部配额

**场景：** 了解某区域资源提供商的全部配额

```bash
# 以表格格式列出 East US 中的全部计算配额
az quota list \
  --scope /subscriptions/<subscription-id>/providers/Microsoft.Compute/locations/eastus \
  --output table

# 列出全部网络配额
az quota list \
  --scope /subscriptions/<subscription-id>/providers/Microsoft.Network/locations/eastus \
  --output table

# 列出全部 Container Apps 配额
az quota list \
  --scope /subscriptions/<subscription-id>/providers/Microsoft.App/locations/eastus \
  --output table
```

> **📖 另请参见：** [az quota list](./references/commands.md#az-quota-list)

## Troubleshooting

### Common Errors

| **错误** | **原因** | **解决方案** |
|-----------|-----------|--------------|
| REST API "No Limit" | 具有误导性——并非无限 | 使用 CLI；参见快速参考中的警告 |
| `ExtensionNotFound` | 未安装配额扩展 | `az extension add --name quota` |
| `BadRequest` | 资源提供商不被配额 API 支持 | 检查 [服务限制文档](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/azure-subscription-service-limits) |
| `MissingRegistration` | Microsoft.Quota 提供程序未注册 | `az provider register --namespace Microsoft.Quota` |
| `QuotaExceeded` | 部署将超出配额 | 申请增加或选择其他区域 |
| `InvalidScope` | 作用域格式不正确 | 使用模式：`/subscriptions/<id>/providers/<namespace>/locations/<region>` |
| CLI 命令完全失败 | 认证、扩展或环境问题 | 验证 Azure CLI 登录（`az account show`）、重新安装配额扩展、检查网络。**切勿**使用 `azure-quota` MCP 服务——其不可靠。 |

### 不支持的资源提供商

**已知不支持提供程序：**
- ❌ Microsoft.DocumentDB (Cosmos DB) - 使用门户或 [Cosmos DB 限制文档](https://learn.microsoft.com/en-us/azure/cosmos-db/concepts-limits)

**已确认可用的提供程序：**
- ✅ Microsoft.Compute（VM、磁盘、cores）
- ✅ Microsoft.Network（VNets、IP、负载均衡器）
- ✅ Microsoft.App（Container Apps）
- ✅ Microsoft.Storage（存储账户）
- ✅ Microsoft.MachineLearningServices（ML 计算）

> **📖 另请参见：** [故障排查指南](./references/commands.md#troubleshooting)

## Additional Resources

| 资源 | 链接 |
|----------|------|
| **CLI 命令参考** | [commands.md](./references/commands.md) - 完整语法、参数、示例 |
| **Azure 配额概述** | [Microsoft Learn](https://learn.microsoft.com/en-us/azure/quotas/quotas-overview) |
| **服务限制文档** | [Azure 订阅限制](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/azure-subscription-service-limits) |
| **Azure 门户 - 我的配额** | [门户链接](https://portal.azure.com/#blade/Microsoft_Azure_Capacity/QuotaMenuBlade/myQuotas) |
| **申请配额增加** | [如何申请增加](https://learn.microsoft.com/en-us/azure/quotas/quickstart-increase-quota-portal) |

## Best Practices

1. ✅ **部署前始终检查配额** - 防止配额超限错误
2. ✅ **先运行 `az quota list`** - 发现正确的配额资源名称
3. ✅ **比较区域** - 查找拥有可用容量的区域
4. ✅ **预留增长空间** - 在即时需求之上申请 20% 的缓冲
5. ✅ **使用表格输出进行概览** - 使用 `--output table` 便于快速浏览
6. ✅ **监控使用趋势** - 在 80% 阈值设置告警（通过门户）
