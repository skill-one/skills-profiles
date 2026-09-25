# Azure 成本优化技能

分析 Azure 订阅，通过清理闲置资源、资源规格调整和基于实际使用数据的优化建议来识别成本节约。

## 使用此技能的场景

当用户要求执行以下操作时，使用此技能：
- 优化 Azure 成本或减少支出
- 分析 Azure 订阅以实现成本节约
- 生成成本优化报告
- 查找闲置或未使用的资源
- 调整 Azure 虚拟机、容器或服务的规格
- 确定在 Azure 中过度支出的地方
- **专门优化 Redis 成本** - 请参阅 [Azure Redis 成本优化](./references/azure-redis.md) 进行 Redis 专用分析

## 操作步骤

与用户进行对话时，请按照以下步骤操作：

### 第 0 步：验证先决条件

开始之前，请验证以下工具和权限是否可用：

**所需工具：**
- 已安装并认证的 Azure CLI (`az login`)
- Azure CLI 扩展：`costmanagement`、`resource-graph`
- 已安装 Azure 快速评估 (azqr) - 请参阅 [Azure 快速评估](./references/azure-quick-review.md) 了解详细信息

**所需权限：**
- 成本管理读取角色
- 监控读取角色
- 订阅/资源组上的读取角色

**验证命令：**
```powershell
az --version
az account show
az extension show --name costmanagement
azqr version
```

### 第 1 步：加载最佳实践

获取 Azure 成本优化最佳实践，以提供优化建议：

```javascript
// 使用 Azure MCP 最佳实践工具
mcp_azure_mcp_get_azure_bestpractices({
  intent: "获取成本优化最佳实践",
  command: "get_bestpractices",
  parameters: { resource: "cost-optimization", action: "all" }
})
```

### 第 1.5 步：Redis 专用分析（可选）

**如果用户专门要求 Redis 成本优化**，请使用专门的 Redis 技能：

📋 **参考**：[Azure Redis 成本优化](./references/azure-redis.md)

**使用 Redis 专用分析的时机：**
- 用户提到 "Redis"、"Azure Cache for Redis" 或 "Azure Managed Redis"
- 重点在于 Redis 资源优化，而不是一般订阅分析
- 用户需要 Redis 专用建议（SKU 降级、失败的缓存等）

**主要功能：**
- 交互式订阅过滤（前缀、ID 或 "所有订阅"）
- Redis 专用优化规则（失败的缓存、规格过大的层级、缺少标签）
- 预构建的 Redis 成本分析报告模板
- 使用 `redis_list` 命令

**可用的报告模板：**
- [订阅级 Redis 摘要](./templates/redis-subscription-level-report.md)
- [详细 Redis 缓存分析](./templates/redis-detailed-cache-analysis.md)

> **注意**：对于包含 Redis 的通用订阅级成本优化，请继续执行第 2 步。对于仅聚焦于 Redis 的分析，请遵循 Redis 专用参考文档中的说明。

### 第 1.6 步：选择分析范围（用于 Redis 专用分析）

**如果执行 Redis 成本优化**，请要求用户选择其分析范围：

**提示用户选择以下选项：**
1. **特定订阅 ID** - 分析单个订阅
2. **订阅名称** - 使用显示名称而不是 ID
3. **订阅前缀** - 分析以特定前缀开头的所有订阅（例如，"CacheTeam"）
4. **所有我的订阅** - 扫描所有可访问的订阅
5. **租户级** - 分析整个组织

等待用户响应，然后继续执行第 2 步。

### 第 1.7 步：AKS 专用分析（可选）

**如果用户专门要求 AKS 成本优化**，请使用专门的 AKS 参考文件：

**使用 AKS 专用分析的时机：**
- 用户提到 "AKS"、"Kubernetes"、"集群"、"节点池"、"Pod" 或 "kubectl"
- 用户希望启用 AKS 成本分析插件或命名空间成本可见性
- 用户报告成本激增、异常集群利用率或希望接收预算警报

**工具选择：**
- **优先使用 MCP**：使用 `mcp_azure_mcp_aks` 进行 AKS 操作（列出集群、获取节点池、检查配置）—— 它提供更丰富的元数据，并与本仓库中 AKS 技能的约定一致
- **回退到 CLI**：仅在 MCP 表面无法执行特定操作时使用 `az aks` 和 `kubectl`

**参考文件（仅加载请求所需的文件）：**
- [成本分析插件](./references/azure-aks-cost-addon.md) — 启用命名空间级成本可见性
- [异常调查](./references/azure-aks-anomalies.md) — 成本激增、扩展事件、预算警报

> **注意**：对于包含 AKS 资源组的通用订阅级成本优化，请继续执行第 2 步。对于 AKS 聚焦的分析，请遵循上述相关参考文件中的说明。

### 第 1.8 步：选择分析范围（用于 AKS 专用分析）

**如果执行 AKS 成本优化**，请要求用户选择其分析范围：

**提示用户选择以下选项：**
1. **特定集群名称** - 分析单个 AKS 集群
2. **资源组** - 分析资源组中的所有集群
3. **订阅 ID** - 分析订阅中的所有集群
4. **所有我的集群** - 跨订阅扫描所有可访问的集群

等待用户响应后再继续执行第 2 步。

### 第 2 步：运行 Azure 快速评估

运行 azqr 以查找闲置资源（立即实现成本节约）：

📋 **参考**：[Azure 快速评估](./references/azure-quick-review.md) - 运行 azqr 扫描的详细说明

```javascript
// 使用 Azure MCP 扩展_azqr 工具
extension_azqr({
  subscription: "<SUBSCRIPTION_ID>",
  "resource-group": "<RESOURCE_GROUP>"  // 可选
})
```

**在 azqr 结果中查找以下内容：**
- 闲置资源：未附加的磁盘、未使用的 NIC、空闲的 NAT 网关
- 规格过大的资源：过长的保留期、规格过大的 SKU
- 缺少成本标签：没有适当成本分配的资源

> **注意**：Azure 快速评估参考文档包含创建过滤器配置、将输出保存到 `output/` 文件夹以及解释结果以进行成本优化的说明。

### 第 3 步：发现资源

为跨订阅资源发现的高效性，使用 Azure 资源图。请参阅 [Azure 资源图查询](references/azure-resource-graph.md) 以检测闲置资源和成本优化模式。

使用 Azure MCP 工具或 CLI 列出订阅中的所有资源：

```powershell
# 获取订阅信息
az account show

# 列出所有资源
az resource list --subscription "<SUBSCRIPTION_ID>" --resource-group "<RESOURCE_GROUP>"

# 使用 MCP 工具进行特定服务（首选）：
# - 存储账户、Cosmos DB、密钥保管库：使用 Azure MCP 工具
# - Redis 缓存：使用 mcp_azure_mcp_redis 工具（请参阅 ./references/azure-redis.md）
# - Web 应用、虚拟机、SQL：使用 az CLI 命令
```

### 第 4 步：查询实际成本

从 Azure 成本管理 API 获取实际成本数据（最后 30 天）：

**创建成本查询文件：**

创建 `temp/cost-query.json`，包含：
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

> **操作要求**：计算 `<START_DATE>`（30 天前）和 `<END_DATE>`（今天）的 ISO 8601 格式（例如，`2025-11-03T00:00:00Z`）。

**执行成本查询：**
```powershell
# 创建 temp 文件夹
New-Item -ItemType Directory -Path "temp" -Force

# 使用 REST API 查询（比 az costmanagement query 更可靠）
az rest --method post `
  --url "https://management.azure.com/subscriptions/<SUBSCRIPTION_ID>/resourceGroups/<RESOURCE_GROUP>/providers/Microsoft.CostManagement/query?api-version=2023-11-01" `
  --body '@temp/cost-query.json'
```

**重要**：将查询结果保存到 `output/cost-query-result<timestamp>.json` 以便审计。

### 第 5 步：验证定价

使用 `fetch_webpage` 从官方 Azure 定价页面获取当前定价：

```javascript
// 验证关键服务的定价
fetch_webpage({
  urls: ["https://azure.microsoft.com/en-us/pricing/details/container-apps/"],
  query: "pricing tiers and costs"
})
```

**需要验证的关键服务：**
- Container Apps：https://azure.microsoft.com/pricing/details/container-apps/
- 虚拟机：https://azure.microsoft.com/pricing/details/virtual-machines/
- App Service：https://azure.microsoft.com/pricing/details/app-service/
- Log Analytics：https://azure.microsoft.com/pricing/details/monitor/

> **重要**：检查免费层额度 - 许多 Azure 服务都有慷慨的免费限制，可能解释为 $0 成本。

### 第 6 步：收集使用指标

查询 Azure Monitor 以获取使用数据（最后 14 天），以支持规格调整建议：

```powershell
# 计算最后 14 天的日期
$startTime = (Get-Date).AddDays(-14).ToString("yyyy-MM-ddTHH:mm:ssZ")
$endTime = Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"

# VM CPU 使用率
az monitor metrics list `
  --resource "<RESOURCE_ID>" `
  --metric "Percentage CPU" `
  --interval PT1H `
  --aggregation Average `
  --start-time $startTime `
  --end-time $endTime

# App Service Plan 使用率
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

### 第 7 步：生成优化报告

在 `output/` 文件夹中创建综合成本优化报告：

**使用 `create_file` 工具**，路径为 `output/costoptimizereport<YYYYMMDD_HHMMSS>.md`：

**报告结构：**
```markdown
# Azure 成本优化报告
**生成时间**： <timestamp>

## 执行摘要
- 月度总成本：$X (💰 实际数据)
- 主要成本驱动：[列出前 3 个资源及其 Azure Portal 链接]

## 成本分解
[包含 Azure Portal 链接的前 10 个资源按成本排序的表格]

## 免费层分析
[在免费层运行并显示 $0 成本的资源]

## 闲置资源（立即节约）
[来自 azqr - 可以立即删除的资源]
- 资源名称与 Portal 链接 - 每月节约 $X

## 优化建议

### 优先级 1：高影响、低风险
[示例：删除闲置资源]
- 💰 实际成本：$X/月
- 📊 预计节约：$Y/月
- 执行命令（带警告）

### 优先级 2：中等影响、中等风险
[示例：将 VM 从 D4s_v5 调整为 D2s_v5]
- 💰 实际基线：D4s_v5，$X/月
- 📈 实际指标：CPU 8%，内存 30%
- 💵 验证定价：D4s_v5 $Y/小时，D2s_v5 $Z/小时
- 📊 预计节约：$S/月
- 执行命令

### 优先级 3：长期优化
[示例：保留实例、存储分层]

## 预计总节约
- 月度：$X
- 年度：$Y

## 实施命令
[带审批警告的安全命令]

## 验证附录

### 数据源和文件
- **成本查询结果**：`output/cost-query-result<timestamp>.json`
  - 来自 Azure 成本管理 API 的原始成本数据
  - 报告生成时的实际成本审计记录
  - 至少保留 12 个月以进行历史比较
  - 包含分析期间每个资源的精确成本
- **定价来源**：[链接到 Azure 定价页面]
- **免费层额度**：[适用额度]

> **注意**：`temp/cost-query.json` 文件（如果存在）是一个临时查询模板，可以安全删除。所有永久审计数据都在 `output/` 文件夹中。

### 第 8 步：保存审计记录

保存所有成本查询结果以供验证：

**使用 `create_file` 工具**，路径为 `output/cost-query-result<YYYYMMDD_HHMMSS>.json`：

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

### 第 9 步：清理临时文件

报告生成后删除临时查询文件和文件夹：

```powershell
# 删除整个 temp 文件夹（不再需要）
Remove-Item -Path "temp" -Recurse -Force -ErrorAction SilentlyContinue
```

> **注意**：`temp/cost-query.json` 文件仅在 API 执行期间需要。实际查询和结果保留在 `output/cost-query-result*.json` 中以供审计。

## 输出

此技能生成：
1. **成本优化报告** (`output/costoptimizereport<timestamp>.md`)
   - 包含总成本和主要驱动因素的执行摘要
   - 带有 Azure Portal 链接的详细成本分解
   - 带有实际数据和预计节约的优先级建议
   - 带有安全警告的实施命令

2. **成本查询结果** (`output/cost-query-result<timestamp>.json`)
   - 所有成本查询和响应的审计记录
   - 建议验证的证据

## 重要说明

### 数据分类
- 💰 **实际数据** = 从 Azure 成本管理 API 获取
- 📈 **实际指标** = 从 Azure Monitor 获取
- 💵 **验证定价** = 从官方 Azure 定价页面获取
- 📊 **预计节约** = 基于实际数据和验证定价计算

### 最佳实践
- 首先始终查询实际成本 - 不要估计或假设
- 从官方来源验证定价 - 考虑免费层额度
- 使用 REST API 进行成本查询（比 `az costmanagement query` 更可靠）
- 保存审计记录 - 包括所有查询和响应
- 为所有资源包含 Azure Portal 链接
- 创建报告文件时使用 UTF-8 编码
- 对于成本 < $10/月，强调操作改进而不是财务节约
- 不要在没有明确批准的情况下执行破坏性操作

### 常见陷阱
- **假设成本**：始终从成本管理 API 查询实际数据
- **忽略免费层**：许多服务有慷慨的额度（例如，Container Apps：180K vCPU-sec 免费每月）
- **使用错误日期范围**：成本 30 天，使用率 14 天
- **损坏的 Portal 链接**：验证租户 ID 和资源 ID 格式
- **成本查询失败**：使用 `az rest` 和 JSON 正文，而不是 `az costmanagement query`

### 安全要求
- 在删除资源前获取批准
- 首先在生产环境外测试更改
- 提供验证命令的干运行
- 包含回滚程序
- 实施后监控影响

## SDK 快速参考

- **Redis 管理**：[.NET](references/sdk/azure-resource-manager-redis-dotnet.md)
