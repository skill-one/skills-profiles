# Azure 成本优化

此工作流分析基础设施即代码（IaC）文件和 Azure 资源，以生成成本优化建议。它会为每个优化机会创建单独的 GitHub 问题，并创建一个 EPIC 问题来协调实施，从而实现成本节约计划的高效跟踪和执行。

## 前置条件
- 配置并认证 Azure MCP 服务器
- 配置并认证 GitHub MCP 服务器  
- 确定目标 GitHub 仓库
- 已部署 Azure 资源（IaC 文件可选但有助于提高效率）
- 优先使用 Azure MCP 工具（`azmcp-*`）而不是直接 Azure CLI（当可用时）

## 工作流步骤

### 第 1 步：获取 Azure 最佳实践
**操作**：在分析之前检索成本优化最佳实践
**工具**：Azure MCP 最佳实践工具
**流程**：
1. **加载最佳实践**：
   - 执行 `azmcp-bestpractices-get` 获取最新的 Azure 优化指南。这可能无法涵盖所有场景，但可提供基础。
   - 尽可能使用这些实践来指导后续分析和建议
   - 在优化建议中引用最佳实践，无论是来自 MCP 工具输出还是通用 Azure 文档

### 第 2 步：发现 Azure 基础设施
**操作**：动态发现和分析 Azure 资源和配置
**工具**：Azure MCP 工具 + Azure CLI 降级 + 本地文件系统访问
**流程**：
1. **资源发现**：
   - 执行 `azmcp-subscription-list` 查找可用订阅
   - 执行 `azmcp-group-list --subscription <subscription-id>` 查找资源组
   - 获取相关资源组中的所有资源列表：
     - 使用 `az resource list --subscription <id> --resource-group <name>`
   - 对于每种资源类型，首先使用 MCP 工具（如果可能），然后使用 CLI 降级：
     - `azmcp-cosmos-account-list --subscription <id>` - Cosmos DB 账户
     - `azmcp-storage-account-list --subscription <id>` - 存储账户  
     - `azmcp-monitor-workspace-list --subscription <id>` - Log Analytics 工作区
     - `azmcp-keyvault-key-list` - 密钥库
     - `az webapp list` - Web 应用（降级 - 没有可用的 MCP 工具）
     - `az appservice plan list` - App Service 计划（降级）
     - `az functionapp list` - Function 应用（降级）
     - `az sql server list` - SQL 服务器（降级）
     - `az redis list` - Redis 缓存（降级）
     - 等等，其他资源类型

2. **IaC 检测**：
   - 使用 `file_search` 扫描 IaC 文件： "**/*.bicep", "**/*.tf", "**/main.json", "**/*template*.json"
   - 解析资源定义以了解预期配置
   - 与发现的资源进行比较以识别差异
   - 记录 IaC 文件的 presence 以便后续实施建议
   - 不要使用来自仓库的任何其他文件，仅使用 IaC 文件。使用其他文件是不允许的，因为它们不是真实来源。
   - 如果您找不到 IaC 文件，则停止并向用户报告未找到 IaC 文件。

3. **配置分析**：
   - 提取每个资源的当前 SKU、层级和设置
   - 识别资源关系和依赖关系
   - 在可用的情况下映射资源使用模式

### 第 3 步：收集使用指标并验证当前成本
**操作**：收集使用数据并验证实际资源成本
**工具**：Azure MCP 监控工具 + Azure CLI
**流程**：
1. **查找监控源**：
   - 使用 `azmcp-monitor-workspace-list --subscription <id>` 查找 Log Analytics 工作区
   - 使用 `azmcp-monitor-table-list --subscription <id> --workspace <name> --table-type "CustomLog"` 发现可用数据

2. **执行使用查询**：
   - 使用 `azmcp-monitor-log-query` 并使用这些预定义查询：
     - 查询： "recent" 用于最近活动模式
     - 查询： "errors" 用于错误级别日志，指示问题
   - 对于自定义分析，使用 KQL 查询：
   ```kql
   // App Services 的 CPU 利用率
   AppServiceAppLogs
   | where TimeGenerated > ago(7d)
   | summarize avg(CpuTime) by Resource, bin(TimeGenerated, 1h)
   
   // Cosmos DB RU 消耗  
   AzureDiagnostics
   | where ResourceProvider == "MICROSOFT.DOCUMENTDB"
   | where TimeGenerated > ago(7d)
   | summarize avg(RequestCharge) by Resource
   
   // 存储账户访问模式
   StorageBlobLogs
   | where TimeGenerated > ago(7d)
   | summarize RequestCount=count() by AccountName, bin(TimeGenerated, 1d)
   ```

3. **计算基线指标**：
   - CPU/内存利用率平均值
   - 数据库吞吐量模式
   - 存储访问频率
   - Function 执行速率

4. **验证当前成本**： 
   - 使用在第 2 步中发现的 SKU/层级配置
   - 查找当前 Azure 定价：https://azure.microsoft.com/pricing/ 或使用 `az billing` 命令
   - 记录：资源 → 当前 SKU → 预计月成本
   - 在继续建议之前计算实际的当前月总成本

### 第 4 步：生成成本优化建议
**操作**：分析资源以识别优化机会
**工具**：使用收集的数据进行本地分析
**流程**：
1. **应用优化模式** 基于发现的资源类型：
   
   **计算优化**：
   - App Service 计划：根据 CPU/内存使用情况调整大小
   - Function Apps：Premium → 消费计划（低使用率）
   - 虚拟机：缩减过大的实例
   
   **数据库优化**：
   - Cosmos DB： 
     - 确定的 → 无服务器（适用于可变工作负载）
     - 根据实际使用情况调整 RU/s
   - SQL 数据库：根据 DTU 使用情况调整服务层级
   
   **存储优化**：
   - 实施生命周期策略（热 → 冷 → 归档）
   - 合并冗余存储账户
   - 根据访问模式调整存储层级
   
   **基础设施优化**：
   - 删除未使用/冗余资源
   - 在有好处的地方实施自动扩展
   - 调度非生产环境

2. **计算基于证据的节省**： 
   - 当前验证成本 → 目标成本 = 节省
   - 记录当前和目标配置的定价来源

3. **计算每个建议的优先级分数**：
   ```
   优先级分数 = (价值分数 × 月节省) / (风险分数 × 实施天数)
   
   高优先级：分数 > 20
   中优先级：分数 5-20
   低优先级：分数 < 5
   ```

4. **验证建议**：
   - 确保 Azure CLI 命令准确
   - 验证估计节省计算
   - 评估实施风险和先决条件
   - 确保所有节省计算都有支持证据

### 第 5 步：用户确认
**操作**：在创建 GitHub 问题之前显示摘要并获取批准
**流程**：
1. **显示优化摘要**：
   ```
   🎯 Azure 成本优化摘要
   
   📊 分析结果：
   • 分析资源总数：X
   • 当前月成本：$X 
   • 潜在月节省：$Y 
   • 优化机会：Z
   • 高优先级项：N
   
   🏆 建议：
   1. [资源]：[当前 SKU] → [目标 SKU] = $X/月节省 - [风险级别] | [实施工作量]
   2. [资源]：[当前配置] → [目标配置] = $Y/月节省 - [风险级别] | [实施工作量]
   3. [资源]：[当前配置] → [目标配置] = $Z/月节省 - [风险级别] | [实施工作量]
   ... 等等
   
   💡 这将创建：
   • Y 个单独的 GitHub 问题（每个优化一个）
   • 1 个 EPIC 问题来协调实施
   
   ❓ 继续创建 GitHub 问题？ (y/n)
   ```

2. **等待用户确认**：只有在用户确认后才能继续

### 第 6 步：创建单个优化问题
**操作**：为每个优化机会创建单独的 GitHub 问题。用“cost-optimization”（绿色）和“azure”（蓝色）标签标记它们。
**MCP 工具要求**：为每个建议使用 `create_issue`
**流程**：
1. **创建单个问题** 使用此模板：

   **标题格式**：`[COST-OPT] [资源类型] - [简要描述] - $X/月节省`
   
   **正文模板**：
   ```markdown
   ## 💰 成本优化：[简要标题]
   
   **月节省**：$X | **风险级别**：[低/中/高] | **实施工作量**：X 天
   
   ### 📋 描述
   [清晰解释优化原因]
   
   ### 🔧 实施
   
   **检测到 IaC 文件**：[是/否 - 基于file_search结果]
   
   ```bash
   # 如果找到 IaC 文件：显示 IaC 修改 + 部署
   # 文件：infrastructure/bicep/modules/app-service.bicep
   # 修改：sku.name: 'S3' → 'B2'
   az deployment group create --resource-group [rg] --template-file infrastructure/bicep/main.bicep
   
   # 如果没有 IaC 文件：直接 Azure CLI 命令 + 警告
   # ⚠️ 未找到 IaC 文件。如果它们存在于其他地方，请修改那些文件。
   az appservice plan update --name [plan] --sku B2
   ```
   
   ### 📊 证据
   - 当前配置：[详情]
   - 使用模式：[监控数据证据]
   - 成本影响：$X/月 → $Y/月
   - 最佳实践一致性：[如果适用，引用 Azure 最佳实践]
   
   ### ✅ 验证步骤
   - [ ] 在非生产环境中测试
   - [ ] 验证无性能下降
   - [ ] 确认 Azure 成本管理中的成本降低
   - [ ] 如有必要，更新监控和警报
   
   ### ⚠️ 风险和注意事项
   - [风险 1 和缓解措施]
   - [风险 2 和缓解措施]
   
   **优先级分数**：X | **价值**：X/10 | **风险**：X/10
   ```

### 第 7 步：创建协调 EPIC 问题
**操作**：创建主问题以跟踪所有优化工作。用“cost-optimization”（绿色）和“azure”（蓝色）以及“epic”（紫色）标签标记它。
**MCP 工具要求**：为 EPIC 使用 `create_issue`
**关于 mermaid 图表**：确保验证 mermaid 语法正确，并创建图表时考虑无障碍性指南（样式、颜色等）。
**流程**：
1. **创建 EPIC 问题**：

   **标题**：`[EPIC] Azure 成本优化计划 - 潜在节省 $X/月`
   
   **正文模板**：
   ```markdown
   # 🎯 Azure 成本优化 EPIC
   
   **潜在月节省**：$X | **实施时间**：X 周
   
   ## 📊 执行摘要
   - **分析资源**：X
   - **优化机会**：Y  
   - **总月节省潜力**：$X
   - **高优先级项**：N
   
   ## 🏗️ 当前架构概述
   
   ```mermaid
   graph TB
       subgraph "资源组：[name]"
           [显示当前资源和成本的生成架构图表]
       end
   ```
   
   ## 📋 实施跟踪
   
   ### 🚀 高优先级（首先实施）
   - [ ] #[issue-number]：[标题] - $X/月节省
   - [ ] #[issue-number]：[标题] - $X/月节省
   
   ### ⚡ 中优先级 
   - [ ] #[issue-number]：[标题] - $X/月节省
   - [ ] #[issue-number]：[标题] - $X/月节省
   
   ### 🔄 低优先级（可取）
   - [ ] #[issue-number]：[标题] - $X/月节省
   
   ## 📈 进度跟踪
   - **已完成**：0 of Y 优化
   - **实现节省**：$0 of $X/月
   - **实施状态**：未开始
   
   ## 🎯 成功标准
   - [ ] 所有高优先级优化已实施
   - [ ] 实现了 >80% 的估计节省
   - [ ] 未观察到性能下降
   - [ ] 更新了成本监控仪表板
   
   ## 📝 备注
   - 随着问题的完成，请审查和更新此 EPIC
   - 监控实际与估计节省
   - 考虑定期进行成本优化审查
   ```

## 错误处理
- **成本验证**：如果节省估计缺乏支持证据或与 Azure 定价不一致，则在继续之前重新验证配置和定价来源
- **Azure 认证失败**：提供手动 Azure CLI 设置步骤
- **未找到资源**：创建关于 Azure 资源部署的信息性问题
- **GitHub 创建失败**：将格式化建议输出到控制台
- **使用数据不足**：注意限制并提供仅基于配置的建议

## 成功标准
- ✅ 所有成本估计与实际资源配置和 Azure 定价进行了验证
- ✅ 为每个优化创建了单独的问题（可跟踪和分配）
- ✅ EPIC 问题提供全面的协调和跟踪
- ✅ 所有建议包括具体的、可执行的 Azure CLI 命令
- ✅ 优先级评分支持以 ROI 为导向的实施
- ✅ 架构图表准确表示当前状态
- ✅ 用户确认防止不必要的问
