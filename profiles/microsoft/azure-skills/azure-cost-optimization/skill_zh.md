# Azure 成本优化技能

分析 Azure 订阅，基于实际使用数据，通过孤立资源清理、调整规模和优化建议来识别成本节省机会。

## 何时使用本技能

使用本技能，当用户要求：
- 优化 Azure 成本或减少支出
- 分析 Azure 订阅以获取成本节省
- 生成成本优化报告
- 查找孤立或未使用的资源
- 调整 Azure VM、容器或服务的规模
- 识别在 Azure 中支出超支的环节
- **专项优化 Redis 成本** - 请参阅 [Azure Redis 成本优化](./references/azure-redis.md) 获取 Redis 专项分析

## 指令

在与用户对话时遵循以下步骤：

### 步骤 0：验证先决条件

在开始前，请验证以下工具和权限是否可用：

**所需工具：**
- Azure CLI 已安装并完成身份验证（`az login`）
- Azure CLI 扩展：`costmanagement`、`resource-graph`
- Azure Quick Review (azqr) 已安装 - 详情请参阅 [Azure Quick Review](./references/azure-quick-review.md)

**所需权限：**
- Cost Management 读者角色
- 监控读者角色
- 订阅/资源组上的读者角色

**验证命令：**
```powershell
az --version
az account show
az extension show --name costmanagement
azqr version
```

### 步骤 1：加载最佳实践

获取 Azure 成本优化最佳实践，以指导建议：

```javascript
// 使用 Azure MCP 最佳实践工具
mcp_azure_mcp_get_azure_bestpractices({
  intent: "Get cost optimization best practices",
  command: "get_bestpractices",
  parameters: { resource: "cost-optimization", action: "all" }
})
```

### 步骤 1.5：Redis 专项分析（条件性）

**如果用户明确要求 Redis 成本优化**，请使用专门的 Redis 技能：

📋 **参考**：[Azure Redis 成本优化](./references/azure-redis.md)

**何时使用 Redis 专项分析：**
- 用户提及 "Redis"、"Azure Cache for Redis" 或 "Azure Managed Redis"
- 分析重点是 Redis 资源优化，而非一般性订阅分析
- 用户需要 Redis 专项建议（SKU 降级、失败缓存等）

**关键能力：**
- 交互式订阅筛选（前缀、ID 或 "所有订阅"）
- Redis 专项优化规则（失败缓存、过大层级、缺少标签）
- Redis 成本分析的预置报告模板
- 使用 `redis_list` 命令

**可用报告模板：**
- [订阅级 Redis 汇总](./templates/redis-subscription-level-report.md)
- [Redis 缓存详细分析](./templates/redis-detailed-cache-analysis.md)

> **注意**：对于一般性订阅级成本优化（包括 Redis），继续执行步骤 2。对于仅面向 Redis 的分析，请遵循 Redis 专项参考文档中的说明。

### 步骤 1.6：选择分析范围（针对 Redis 专项分析）

**如果进行 Redis 成本优化**，请让用户选择分析范围：

**向用户提供以下选项：**
1. **特定订阅 ID** - 分析单个订阅
2. **订阅名称** - 使用显示名称而非 ID
3. **订阅前缀** - 分析所有以前缀开头的订阅（例如 "CacheTeam"）
4. **我的所有订阅** - 扫描所有可访问的订阅
5. **租户范围** - 分析整个组织

等待用户回复后，继续执行步骤 2。

### 步骤 1.7：AKS 专项分析（条件性）

**如果用户明确要求 AKS 成本优化**，请使用专门的 AKS 参考文件：

**何时使用 AKS 专项分析：**
- 用户提及 "AKS"、"Kubernetes"、"集群"、"节点池"、"Pod" 或 "kubectl"
- 用户希望启用 AKS 成本分析插件或命名空间成本可见性
- 用户报告成本激增、集群利用率异常，或希望设置预算警报

**工具选择：**
- **优先使用 MCP**：使用 `mcp_azure_mcp_aks` 进行 AKS 操作（列出集群、获取节点池、检查配置）——提供更丰富的元数据，并与本仓库中 AKS 技能的惯例保持一致
- **回退到 CLI**：仅在特定操作无法通过 MCP 接口执行时，使用 `az aks` 和 `kubectl`

**参考文件（根据请求需要加载）**：
- [成本分析插件](./references/azure-aks-cost-addon.md) — 启用命名空间级成本可见性
- [异常调查](./references/azure-aks-anomalies.md) — 成本激增、扩缩容事件、预算警报

> **注意**：对于一般性订阅级成本优化（包括 AKS 资源组），继续执行步骤 2。对于 AKS 专项分析，请遵循上述相关参考文件中的说明。

### 步骤 1.8：选择分析范围（针对 AKS 专项分析）

**如果进行 AKS 成本优化**，请让用户选择分析范围：

**向用户提供以下选项：**
1. **特定集群名称** - 分析单个 AKS 集群
2. **资源组** - 分析资源组中的所有集群
3. **订阅 ID** - 分析订阅中的所有集群
4. **我的所有集群** - 扫描所有可访问的跨订阅集群

等待用户回复后，再继续执行步骤 2。

### 步骤 2：运行 Azure Quick Review

运行 azqr 查找孤立资源（即时成本节省）：

📋 **参考**：[Azure Quick Review](./references/azure-quick-review.md) - azqr 扫描的详细操作说明

```javascript
// 使用 Azure MCP extension_azqr 工具
extension_azqr({
  subscription: "<SUBSCRIPTION_ID>",
  "resource-group": "<RESOURCE_GROUP>"  // optional
})
```

**在 azqr 结果中需要查找的内容：**
- 孤立资源：未挂载磁盘、未使用的网卡、闲置的 NAT 网关
- 过度配置的资源：过长的保留期、过大的 SKU
- 缺少成本标签：未正确进行成本分配的资源

> **注意**：Azure Quick Review 参考文档包含创建筛选配置、将输出保存到 `output/` 文件夹以及用于成本优化的结果解读说明。

### 步骤 3：发现资源

为了高效进行跨订阅资源发现，使用 Azure Resource Graph。请参阅 [Azure Resource Graph 查询](references/azure-resource-graph.md) 了解孤立资源检测和成本优化模式。

在订阅中使用 Azure MCP 工具或 CLI 列出所有资源：

```powershell
# 获取订阅信息
az account show

# 列出所有资源
az resource list --subscription "<SUBSCRIPTION_ID>" --resource-group "<RESOURCE_GROUP>"

# 使用 MCP 工具处理特定服务（优先）：
# - 存储账户、Cosmos DB、密钥保管库：使用 Azure MCP 工具
# - Redis 缓存：使用 mcp_azure_mcp_redis 工具（见 ./references/azure-redis.md）
# - Web 应用、VM、SQL：使用 az CLI 命令
```

### 步骤 4：查询实际成本

从 Azure Cost Management API 获取实际成本数据（近 30 天）：

**创建成本查询文件：**

创建 `temp/cost-query.json` 文件，内容如下：
```json
{
  "type": "ActualCost",
  "timeframe": "Custom",
  "timePeriod": {
    "from": "<START_DATE>",  
    "to": "<END_DATE>"
  },
  "dataset": {
    "granularity": "None",
    "aggregation": {
      "totalCost": {
        "name": "Cost",
        "function": "Sum"
      }
    },
    "grouping": [
      {
        "type": "Dimension",
        "name": "ResourceId"
      }
    ]
  }
}
```

> **需要执行的操作**：以 ISO 8601 格式计算 `<START_DATE>`（30 天前）和 `<END_DATE>`（今天），例如 `2025-11-03T00:00:00Z`。

**执行成本查询：**
```powershell
# 创建临时文件夹
New-Item -ItemType Directory -Path "temp" -Force

# 使用 REST API 查询（比 az costmanagement query 更可靠）
az rest --method post `
  --url "https://management.azure.com/subscriptions/<SUBSCRIPTION_ID>/resourceGroups/<RESOURCE_GROUP>/providers/Microsoft.CostManagement/query?api-version=2023-11-01" `
  --body '@temp/cost-query.json'
```

**重要**：将查询结果保存至 `output/cost-query-result` + `<时间戳>` + `.json`，用于审计追踪。

### 步骤 5：验证定价

使用 `fetch_webpage` 从官方 Azure 定价页面获取当前定价：

```javascript
// 验证关键服务的定价
fetch_webpage({
  urls: ["https://azure.microsoft.com/en-us/pricing/details/container-apps/"],
  query: "pricing tiers and costs"
})
```

**需要验证的关键服务：**
- Container Apps：https://azure.microsoft.com/en-us/pricing/details/container-apps/
- Virtual Machines：https://azure.microsoft.com/en-us/pricing/details/virtual-machines/
- App Service：https://azure.microsoft.com/en-us/pricing/details/app-service/
- Log Analytics：https://azure.microsoft.com/en-us/pricing/details/monitor/

> **重要**：检查免费层级额度——许多 Azure 服务有较为慷慨的免费限制，这些可能解释了 $0 成本。

### 步骤 6：收集利用率指标

查询 Azure Monitor 以获取利用率数据（近 14 天），支持调整规模建议：

```powershell
# 计算近 14 天的日期
$startTime = (Get-Date).AddDays(-14).ToString("yyyy-MM-ddTHH:mm:ssZ")
$endTime = Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"

# VM CPU 利用率
az monitor metrics list `
  --resource "<RESOURCE_ID>" `
  --metric "Percentage CPU" `
  --interval PT1H `
  --aggregation Average `
  --start-time $startTime `
  --end-time $endTime

# App Service Plan 利用率
az monitor metrics list `
  --resource "<RESOURCE_ID>" `
  --metric "CpuTime,Requests" `
  --interval PT1H `
  --aggregation Total `
  --start-time $startTime `
  --end-time $endTime

# 存储容量
az monitor metrics list `
  --resource "<RESOURCE_ID>" `
  --metric "UsedCapacity,BlobCount" `
  --interval PT1H `
  --aggregation Average `
  --start-time $startTime `
  --end-time $endTime
```

### 步骤 7：生成优化报告

在 `output/` 文件夹中创建综合成本优化报告：

**使用 `create_file` 工具**，路径为 `output/costoptimizereport` + `<YYYYMMDD_HHMMSS>` + `.md`：

**报告结构：**
```markdown
# Azure Cost Optimization Report
**Generated**: <timestamp)

## Executive Summary
- Total Monthly Cost: $X (💰 ACTUAL DATA)
- Top Cost Drivers: [列出前 3 个资源及 Azure 门户链接]

## Cost Breakdown
[按成本列出前 10 个资源的表格，包含 Azure 门户链接]

## Free Tier Analysis
[在免费层级内运行、显示 $0 成本资源的说明]

## Orphaned Resources (Immediate Savings)
[来自 azqr - 可立即删除的资源]
- 资源名称及门户链接 - 每月节省 $X

## Optimization Recommendations

### Priority 1: High Impact, Low Risk
[示例：删除孤立资源]
- 💰 ACTUAL cost: $X/month
- 📊 ESTIMATED savings: $Y/month
- Commands to execute (with warnings)

### Priority 2: Medium Impact, Medium Risk
[示例：将 VM 从 D4s_v5 调整为 D2s_v5]
- 💰 ACTUAL baseline: D4s_v5, $X/month
- 📈 ACTUAL metrics: CPU 8%, Memory 30%
- 💵 VALIDATED pricing: D4s_v5 $Y/hr, D2s_v5 $Z/hr
- 📊 ESTIMATED savings: $S/month
- Commands to execute

### Priority 3: Long-term Optimization
[示例：预留实例、存储分层]

## Total Estimated Savings
- Monthly: $X
- Annual: $Y

## Implementation Commands
[带有批准警告的安全命令]

## Validation Appendix

### Data Sources and Files
- **成本查询结果**：`output/cost-query-result` + `<时间戳>` + `.json`
  - Azure Cost Management API 的原始成本数据
  - 报告生成时实际成本的可审计追踪
  - 至少保留 12 个月以进行历史对比
  - 包含分析周期内每个资源的确切成本
- **定价来源**：[Azure 定价页面链接]
- **免费层级额度**：[适用的额度]

> **注意**：如果存在 `temp/cost-query.json` 文件，它是临时的查询模板，可以安全删除。所有永久审计数据均位于 `output/` 文件夹中。
```

**门户链接格式：**
```
https://portal.azure.com/#@<TENANT_ID>/resource/subscriptions/<SUBSCRIPTION_ID>/resourceGroups/<RESOURCE_GROUP>/providers/<RESOURCE_PROVIDER>/<RESOURCE_TYPE>/<RESOURCE_NAME>/overview
```

### 步骤 8：保存审计追踪

为验证保存所有成本查询结果：

**使用 `create_file` 工具**，路径为 `output/cost-query-result` + `<YYYYMMDD_HHMMSS>` + `.json`：

```json
{
  "timestamp": "<ISO_8601>",
  "subscription": "<SUBSCRIPTION_ID>",
  "resourceGroup": "<RESOURCE_GROUP>",
  "queries": [
    {
      "queryType": "ActualCost",
      "timeframe": "MonthToDate",
      "query": { },
      "response": { }
    }
  ]
}
```

### 步骤 9：清理临时文件

在报告生成后，移除临时的查询文件和文件夹：

```powershell
# 删除整个 temp 文件夹（不再需要）
Remove-Item -Path "temp" -Recurse -Force -ErrorAction SilentlyContinue
```

> **注意**：`temp/cost-query.json` 文件仅在 API 执行期间需要。实际的查询与结果已保存至 `output/cost-query-result*.json` 以供审计。

## 输出

技能将生成以下内容：
1. **成本优化报告**（`output/costoptimizereport` + `<时间戳>` + `.md`）
   - 包含总成本及主要成本驱动因素的执行摘要
   - 包含 Azure 门户链接的详细成本拆解
   - 包含实际数据与预估节省的优先建议
   - 包含安全警告的实现命令

2. **成本查询结果**（`output/cost-query-result` + `<时间戳>` + `.json`）
   - 所有成本查询与响应的审计追踪
   - 建议的验证证据

## 重要说明

### 数据分类
- 💰 **实际数据** = 从 Azure Cost Management API 获取
- 📈 **实际指标** = 从 Azure Monitor 获取
- 💵 **已验证定价** = 从官方 Azure 定价页面获取
- 📊 **预估节省** = 基于实际数据与已验证定价计算得出

### 最佳实践
- 始终先查询实际成本——切勿估算或假设
- 从官方来源验证定价——考虑免费层级
- 使用 REST API 进行成本查询（比 `az costmanagement query` 更可靠）
- 保存审计追踪——包含所有查询与响应
- 包含所有资源的 Azure 门户链接
- 创建报告文件时使用 UTF-8 编码
- 对于低于 $10/月的成本，应强调运营改进而非财务节省
- 未经明确批准，切勿执行破坏性操作

### 常见陷阱
- **假设成本**：始终从 Cost Management API 查询实际数据
- **忽略免费层级**：许多服务有较为慷慨的额度（例如 Container Apps：每月 180K vCPU-秒免费）
- **使用错误的日期范围**：成本查询使用 30 天，利用率查询使用 14 天
- **门户链接损坏**：验证租户 ID 与资源 ID 的格式
- **成本查询失败**：使用带有 JSON 主体的 `az rest`，而非 `az costmanagement query`

### 安全要求
- 删除资源前获取批准
- 先在非生产环境中测试变更
- 为验证提供试运行命令
- 包含回滚流程
- 实施后监控影响

## SDK 快速参考

- **Redis 管理**：[.NET](references/sdk/azure-resource-manager-redis-dotnet.md)
