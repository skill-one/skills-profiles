---
name: azure-pricing
description: 使用 Azure Retail Prices API（prices.azure.com）获取实时 Azure 零售价格，并估算 Copilot Studio 代理的信用消耗。当用户询问任何 Azure 服务的成本、想要比较 SKU 价格、需要成本估算的定价数据、提及 Azure 定价、Azure 成本、Azure 账单，或询问 Copilot Studio 定价、Copilot 信用额度或代理使用估算时使用。涵盖计算、存储、网络、数据库、人工智能、Copilot Studio 以及所有其他 Azure 服务系列。
---

# Azure 定价技能

使用此技能从公共 Azure 零售价格 API 获取实时 Azure 零售价格数据。无需身份验证。

## 何时使用此技能

- 用户询问 Azure 服务的成本（例如，“D4s v5 虚拟机多少钱？”）
- 用户希望比较不同区域或 SKU 的定价
- 用户需要一个工作负载或架构的成本估算
- 用户提到 Azure 定价、Azure 成本或 Azure 账单
- 用户询问预留实例与按量付费定价的区别
- 用户想了解节省计划或竞价定价

## API 端点

```
GET https://prices.azure.com/api/retail/prices?api-version=2023-01-01-preview
```

使用 OData 过滤语法将 `$filter` 作为查询参数附加。始终使用 `api-version=2023-01-01-preview` 以确保包含节省计划数据。

## 分步说明

如果用户请求中 anything 不明确，请在调用 API 之前通过询问澄清问题来识别正确的过滤字段和值。

1. **从用户请求中识别过滤字段**（服务名称、区域、SKU、价格类型）。
2. **解析区域**：API 要求 `armRegionName` 值为小写且不含空格（例如，“East US”→`eastus`，“West Europe”→`westeurope`，“Southeast Asia”→`southeastasia`）。参见 [references/REGIONS.md](references/REGIONS.md) 获取完整列表。
3. **使用下表中的字段构建过滤字符串** 并获取 URL。
4. **解析 JSON 响应中的 `Items` 数组**。每个项目包含价格和元数据。
5. **如果需要超过前 1000 条结果，请通过 `NextPageLink` 跟进分页**（很少需要）。
6. **使用 [references/COST-ESTIMATOR.md](references/COST-ESTIMATOR.md) 中的公式计算成本估算** 以生成月度/年度估算。
7. **以清晰的摘要表呈现结果**，包含服务、SKU、区域、单位价格和月度/年度估算。

## 可过滤字段

| 字段 | 类型 | 示例 |
|---|---|---|
| `serviceName` | 字符串（精确、区分大小写） | `'Functions'`，`'Virtual Machines'`，`'Storage'` |
| `serviceFamily` | 字符串（精确、区分大小写） | `'Compute'`，`'Storage'`，`'Databases'`，`'AI + Machine Learning'` |
| `armRegionName` | 字符串（精确、小写） | `'eastus'`，`'westeurope'`，`'southeastasia'` |
| `armSkuName` | 字符串（精确） | `'Standard_D4s_v5'`，`'Standard_LRS'` |
| `skuName` | 字符串（包含支持的） | `'D4s v5'` |
| `priceType` | 字符串 | `'Consumption'`，`'Reservation'`，`'DevTestConsumption'` |
| `meterName` | 字符串（包含支持的） | `'Spot'` |

使用 `eq` 进行等值比较，使用 `and` 组合，使用 `contains(field, 'value')` 进行部分匹配。

## 示例过滤字符串

```
# 东部 US 的所有按量付费 Functions 定价
serviceName eq 'Functions' and armRegionName eq 'eastus' and priceType eq 'Consumption'

# 西欧的 D4s v5 虚拟机（仅按量付费）
armSkuName eq 'Standard_D4s_v5' and armRegionName eq 'westeurope' and priceType eq 'Consumption'

# 某个区域的所有存储定价
serviceName eq 'Storage' and armRegionName eq 'eastus'

# 特定 SKU 的竞价定价
armSkuName eq 'Standard_D4s_v5' and contains(meterName, 'Spot') and armRegionName eq 'eastus'

# 1 年预留实例定价
serviceName eq 'Virtual Machines' and priceType eq 'Reservation' and armRegionName eq 'eastus'

# Azure AI / OpenAI 定价（现属于 Foundry Models）
serviceName eq 'Foundry Models' and armRegionName eq 'eastus' and priceType eq 'Consumption'

# Azure Cosmos DB 定价
serviceName eq 'Azure Cosmos DB' and armRegionName eq 'eastus' and priceType eq 'Consumption'
```

## 完整示例获取 URL

```
https://prices.azure.com/api/retail/prices?api-version=2023-01-01-preview&$filter=serviceName eq 'Functions' and armRegionName eq 'eastus' and priceType eq 'Consumption'
```

构建 URL 时，空格作为 `%20` 编码，引号作为 `%27` 编码。

## 关键响应字段

```json
{
  "Items": [
    {
      "retailPrice": 0.000016,
      "unitPrice": 0.000016,
      "currencyCode": "USD",
      "unitOfMeasure": "1 Execution",
      "serviceName": "Functions",
      "skuName": "Premium",
      "armRegionName": "eastus",
      "meterName": "vCPU Duration",
      "productName": "Functions",
      "priceType": "Consumption",
      "isPrimaryMeterRegion": true,
      "savingsPlan": [
        { "unitPrice": 0.000012, "term": "1 Year" },
        { "unitPrice": 0.000010, "term": "3 Years" }
      ]
    }
  ],
  "NextPageLink": null,
  "Count": 1
}
```

除非用户明确要求非主要计量区域，否则仅使用 `isPrimaryMeterRegion` 为 `true` 的项目。

## 支持的 serviceFamily 值

`Analytics`，`Compute`，`Containers`，`Data`，`Databases`，`Developer Tools`，`Integration`，`Internet of Things`，`Management and Governance`，`Networking`，`Security`，`Storage`，`Web`，`AI + Machine Learning`

## 小贴士

- `serviceName` 值区分大小写。不确定时，先按 `serviceFamily` 过滤以发现结果中的有效 `serviceName` 值。
- 如果结果为空，尝试放宽过滤条件（例如，先移除 `priceType` 或区域约束）。
- 价格始终为美元，除非请求中指定了 `currencyCode`。
- 对于节省计划价格，查找每个项目上的 `savingsPlan` 数组（仅在 `2023-01-01-preview` 中）。
- 参见 [references/SERVICE-NAMES.md](references/SERVICE-NAMES.md) 获取常见服务名称及其正确大小写的目录。
- 参见 [references/COST-ESTIMATOR.md](references/COST-ESTIMATOR.md) 获取成本估算公式和模式。
- 参见 [references/COPILOT-STUDIO-RATES.md](references/COPILOT-STUDIO-RATES.md) 获取 Copilot Studio 账单率和估算公式。

## 故障排除

| 问题 | 解决方案 |
|-------|----------|
| 空结果 | 放宽过滤条件——先移除 `priceType` 或 `armRegionName` |
| 错误的服务名称 | 使用 `serviceFamily` 过滤器发现有效的 `serviceName` 值 |
| 缺少节省计划数据 | 确保 URL 中包含 `api-version=2023-01-01-preview` |
| URL 错误 | 检查 URL 编码——空格为 `%20`，引号为 `%27` |
| 结果过多 | 添加更多过滤字段（区域、SKU、priceType）以缩小范围 |

---

# Copilot Studio 代理使用估算

当用户询问 Copilot Studio 定价、Copilot 信用额度或代理使用成本时，使用此部分。

## 何时使用此部分

- 用户询问 Copilot Studio 定价或成本
- 用户询问 Copilot 信用额度或代理信用消耗
- 用户希望估算 Copilot Studio 代理的月度成本
- 用户提到代理使用估算或 Copilot Studio 估算器
- 用户询问代理运行成本

## 关键事实

- **1 Copilot 信用额度 = 0.01 美元**
- 信用额度在整个租户中共享
- 员工代理在具有 M365 Copilot 许可用户的租户中获取经典答案、生成式答案和租户图基础，且无需成本
- 超额执行触发时，会触发预付费容量的 125%

## 分步估算

1. **从用户处收集输入**：代理类型（员工/客户）、用户数量、每月交互次数、知识百分比、租户图百分比、每会话工具使用情况。
2. **获取实时账单率**——使用内置的 Web 获取工具从下方列出的源 URL 下载最新价格。这确保估算始终使用最新的 Microsoft 定价。
3. **解析获取的内容**：提取当前账单率表（每种功能类型的信用额度）。
4. **使用获取内容中的率和公式计算估算**：
   - `total_sessions = users × interactions_per_month`
   - 知识信用额度：应用租户图基础率、生成式答案率、经典答案率
   - 代理工具信用额度：应用每工具调用一次的代理操作率
   - 代理流程信用额度：应用每 100 次操作的流程率
   - 提示修改器信用额度：应用每 10 次响应的基本/标准/高级率
5. **以清晰的表格呈现结果**：按类别细分、总信用额度和估算美元成本。

## 获取源 URL

回答 Copilot Studio 定价问题时，从这些 URL 获取最新内容作为上下文：

| URL | 内容 |
|---|---|
| https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-messages-management | 账单率表、账单示例、超额执行规则 |
| https://learn.microsoft.com/en-us/microsoft-copilot-studio/billing-licensing | 许可选项、M365 Copilot 包含内容、预付费与按量付费 |

至少在计算前获取第一个 URL（账单率）。第二个 URL 提供补充上下文，用于许可问题。

参见 [references/COPILOT-STUDIO-RATES.md](references/COPILOT-STUDIO-RATES.md) 获取率和公式以及账单示例的缓存快照（如果 Web 获取不可用，则用作备用）。
