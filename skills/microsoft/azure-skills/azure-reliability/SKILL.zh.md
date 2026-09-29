---
name: azure-reliability
description: 评估并提升 PaaS 应用（Azure Functions 和 Azure App Service）的可靠性。扫描已部署资源，检查区域冗余、ZRS 存储、健康探测和多区域故障转移。提供以功能为中心的检查清单，然后通过用户确认，端到端推动分阶段修复（CLI 或 IaC 补丁）。何时使用："评估可靠性"、"检查可靠性"、"区域冗余"、"多区域故障转移"、"高可用性"、"灾难恢复"、"单点故障"、"可靠性态势"、"弹性"。
---

# Azure 可靠性评估与配置

## 快速参考

| 属性 | 详情 |
|---|---|
| 最适用于 | 可靠性态势评估、区域冗余启用、多区域故障转移设置 |
| 主要功能 | 可靠性评估表格、区域冗余配置、多区域 IaC 生成 |
| 支持的服务 | Azure Functions、App Service（计划在未来的版本中支持容器应用） |
| MCP 工具 | Azure Resource Graph 查询、Azure CLI 命令 |

## 何时使用此技能

当用户想要执行以下操作时，请激活此技能：
- "评估我的 Function 应用的可靠性"
- "评估我的 Web 应用的可靠性"
- "检查我的资源组的可靠性"（仅限 App Service 和 Functions 资源）
- "我的应用是否区域冗余？"（仅限 App Service 和 Functions 资源）
- "我的应用服务计划是否区域冗余？"
- "使我的应用区域冗余"（仅限 App Service 和 Functions 资源）
- "使我的应用服务计划区域冗余"
- "为我的应用设置多区域故障转移"（仅限 App Service 和 Functions 资源）
- "检查我的可靠性态势"
- "查找单点故障"（仅限 App Service 和 Functions 资源）
- "为我的应用启用高可用性"（仅限 App Service 和 Functions 资源）
- "检查灾难恢复准备情况"
- "提高我的应用的弹性"（仅限 App Service 和 Functions 资源）

> **范围说明：** 此技能目前仅涵盖 **Azure Functions 和 Azure App Service**。如果用户询问关于 Azure Container Apps 的可靠性，请确认支持计划尚未提供，并且仅处理适用于 App Service 和 Functions 资源的部分。

## 前提条件

- 身份验证：用户通过 `az login` 登录 Azure
- 权限：目标订阅/资源组的读取权限（用于评估）
- 权限：贡献者权限（用于配置更改）
- Azure Resource Graph 扩展：`az extension add --name resource-graph`

## MCP 工具

| 工具 | 目的 |
|------|---------|
| `mcp_azure_mcp_extension_cli_generate` | 生成用于资源查询和配置的 `az` CLI 命令 |
| `mcp_azure_mcp_subscription_list` | 列出可用订阅 |
| `mcp_azure_mcp_group_list` | 列出资源组 |

主要查询方法：通过 `az graph query` 使用 Azure Resource Graph（需要 `az extension add --name resource-graph`）。

## 评估工作流

### 第一阶段：发现资源

1. **确定范围** — 询问用户资源组、订阅或应用名称
2. **查询 Azure Resource Graph** 以发现范围内的所有资源
3. **按服务类型对资源进行分类**（Functions、存储等）。如果发现非 Functions 计算（非 Function App 的 App Service 站点、容器应用），**记录但不要深入分析** — 这些服务计划在技能的未来版本中提供。

**重要提示：** 始终将查询范围限定在用户指定的资源组或订阅中。在每次 Resource Graph 查询中添加这些过滤器：
- 资源组：`| where resourceGroup =~ '<rg-name>'`
- 订阅：在 `az graph query` 上使用 `--subscriptions <sub-id>` 标志
- 应用名称：`| where name =~ '<app-name>'`

### 第二阶段：评估可靠性

两步评估：**首先进行平台级发现，然后对每个服务进行深入分析。**

**步骤 1 — 平台发现（查找现有内容）。** 使用以下方法来枚举范围内的资源并检测跨领域的可靠性差距：

| 平台检查 | 参考 |
|---|---|
| 区域冗余 — 发现 | [references/zone-redundancy-checks.md](references/zone-redundancy-checks.md) |
| 存储冗余（跨服务） | [references/storage-redundancy-checks.md](references/storage-redundancy-checks.md) |
| 多区域和全局负载均衡器 | [references/multi-region-checks.md](references/multi-region-checks.md) |
| Front Door / Traffic Manager / App Insights 探针 | [references/health-probe-checks.md](references/health-probe-checks.md) |

**步骤 2 — 每个服务的深入分析。** 对于步骤 1 中发现的每个计算资源，加载匹配的服务参考。服务参考是该服务计划/SKU 规则、评估查询、CLI 命令、IaC 补丁（Bicep + Terraform + AVM）和报告提示的单一事实来源。

此技能版本仅提供 **Azure Functions 和 App Service** 的每个服务参考。其他计算服务在下方明确列出，以便调度逻辑明确：如果资源匹配不支持的行，则**不要**尝试加载参考、编造 CLI 命令或为其生成 IaC 补丁。

| 检测到的服务 | 参考 |
|---|---|
| Azure Functions (`microsoft.web/serverfarms` with `kind contains 'functionapp'`) | [references/services/functions/reliability.md](references/services/functions/reliability.md) |
| Azure App Service（非 Functions 站点：`microsoft.web/sites` without `kind contains 'functionapp'`，`microsoft.web/serverfarms` without `kind contains 'functionapp'`) | [references/services/app-service/reliability.md](references/services/app-service/reliability.md) |
| Azure Container Apps (`microsoft.app/containerapps`，`microsoft.app/managedenvironments`) | ⚪ 尚未提供 — 计划在未来的版本中提供 |

> **处理不支持的服务的说明：** 如果资源匹配上方的不支持行，请在发现摘要中显示它，并在第三阶段表格中将它标记为 `⚪ 未评估（计划）`，并跳过对其的每个服务修复步骤。**不要**尝试为这些服务编造 CLI 命令或 IaC 补丁。

### 第三阶段：生成可靠性检查清单

以 **功能导向** 的表格呈现结果：每行对应一个可靠性功能（计算中的区域冗余、区域冗余存储、健康探针、多区域故障转移），具有一个状态指示器和相关的**特定资源**。这避免了具有大量 `n/a` 单元的单行资源的噪音。**不要**分配数值分数或等级。

```
🔍 可靠性评估 — {范围}
─────────────────────────────────────────────────────────────────────────────────────────────
可靠性功能              状态      资源
─────────────────────────────────────────────────────────────────────────────────────────────
计算中的区域冗余        🔴 关闭      • plan-web-ii5trxva2ark4 (P1v3)
                                              • plan-ii5trxva2ark4 (FC1)

区域冗余存储           🔴 GRS      • stii5trxva2ark4 (默认；IaC 中未设置 SKU)

健康探针                🔴 关闭      • func-api-ii5trxva2ark4 — 需要代码更改 (FC1)
                                              • app-web-ii5trxva2ark4 — 无健康检查路径

多区域故障转移        🔴 关闭      • 仅一个区域（eastus） — 未配置 Front Door
─────────────────────────────────────────────────────────────────────────────────────────────

想要我修复 🔴 项目吗？我将首先进行快速修复（无停机时间，快速）：

1. ✏️  在 plan-ii5trxva2ark4 上启用区域冗余（Flex Consumption — 无成本变化）
2. ✏️  在 func-api-ii5trxva2ark4 上将健康检查路径设置为 /api/health

然后，我将分别询问您是否要升级存储：

3. 🕒  将 stii5trxva2ark4 从 LRS 升级到 ZRS (成本略有增加，迁移需要数小时)
   — 对于完整区域冗余是必需的，但我会在开始之前与您确认。

您希望如何应用这些更改？

  A) 立即修复 — 对您的实时资源运行 az CLI 命令（立即，一次性）
  B) 更新我的 IaC — 更新您的 Bicep/Terraform 文件，以便更改跨部署持久化

（如果您使用 azd 或 Terraform，建议选择 B，以便 `azd up` 不会覆盖更改。）
```

### 路径 A：立即修复（CLI）

使用 `az` CLI 命令对实时资源运行修复。**首先进行快速修复，然后在进行存储迁移之前询问。**

每个服务的确切 CLI 命令位于每个服务参考中 — 选择与第二阶段中发现的资源匹配的命令：

| 修复 | 参考 |
|---|---|
| 启用区域冗余 / 配置健康探针（Functions） | [references/services/functions/reliability.md](references/services/functions/reliability.md) |
| 启用区域冗余 / 配置健康探针（App Service） | [references/services/app-service/reliability.md](references/services/app-service/reliability.md) |
| 升级存储复制（跨服务） | [references/configure-storage.md](references/configure-storage.md) |
| 设置多区域（跨服务） | [references/configure-multi-region.md](references/configure-multi-region.md) |
| 平台概述/验证 | [references/configure-zone-redundancy.md](references/configure-zone-redundancy.md)，[references/configure-health-probes.md](references/configure-health-probes.md) |

**执行顺序 — 始终首先进行快速修复：**

1. **计算中的区域冗余**（快速，对应用的计划进行原地属性更新）。
2. **健康探针**（Premium / Dedicated 仅限 — 原地；对于 FC1 / Consumption，请遵循 [configure-health-probes.md](references/configure-health-probes.md) 中的同意门）。
3. **验证**计算更改是否成功，然后再进行任何其他操作。
4. **⛔ 停止 — 询问关于存储升级。** 计算现在已区域冗余，但存储可能仍然是 LRS 或 GRS。明确询问用户：

   ```
   ✅ 计算是现在区域冗余的。

   要成为 **完全区域冗余**，您的存储账户也需要升级：
     • stii5trxva2ark4：当前为 `Standard_LRS` → 需要 `Standard_ZRS`

   ⚠️  这是一次实时存储冗余转换：
      • 根据数据量，耗时数小时到数天
      • 小额持续成本增加 (~$0.01/GB/月更多)
      • 仅支持 Standard general-purpose v2 账户

   您想要我现在开始存储迁移吗？ (是 / 否 / 稍后)
   ```

   - **是** → 运行 `az storage account update --sku Standard_ZRS`（如果需要，则 `migration start`）；轮询 `az storage account show --query sku.name` 直到它报告 `Standard_ZRS`。
   - **否 / 稍后** → 保持存储不变；在重新评估中注明 ZR 存储仍然存在差距。

5. **多区域** — 不要自动运行。在**第三阶段**下作为明确的后续步骤进行重新评估后处理。

> **⚠️ 警告：** 如果用户稍后使用 `azd up` 或 `terraform apply`，CLI 仅更改可能会被 IaC 定义覆盖。建议在 CLI 修复后也修补 IaC。

### 路径 B：修补 IaC

更新用户的 Bicep 或 Terraform 文件，以便可靠性设置持久化。

**第一步：检测 IaC 类型**
1. 在项目根目录中查找 `infra/` 文件夹
2. 如果未找到，检查项目根目录中的 `*.bicep` 或 `*.tf` 文件
3. 如果仍然未找到，询问用户："您的 IaC 文件位于哪里？"
4. 检查 `*.bicep` 文件 → 使用 Bicep 补丁
5. 检查 `*.tf` 文件 → 使用 Terraform 补丁
6. 如果两者都存在，询问用户要修补哪一个
7. 如果没有 IaC，回退到路径 A（CLI）并通知用户

**第二步：按风险级别对每个修复进行分类**

| 修复 | 风险级别 | 发生什么 |
|-----|-----------|--------------|
| 区域冗余（App 计划） | 🟢 安全修补 | 在下一个部署中对应用的计划进行原地属性更新 |
| 存储 LRS → ZRS | 🟡 需要先进行迁移 | 必须在 IaC SKU 更改可以部署之前完成实时存储迁移。**永远不要将安全修补与存储 SKU 补丁捆绑在一起** — 使用步骤 3–5 中的两阶段部署流程。 |
| 健康检查路径（Basic/Standard/Premium / Dedicated） | 🟢 安全修补 | 原地更新，但会导致应用重启 |
| 健康检查路径（FC1 / Consumption） | ⚪ 仅代码 — 首先询问 | `healthCheckPath` 不受支持。添加健康端点需要向 **应用代码** 添加一个 HTTP 触发的 `/api/health` 函数。**在修改源代码之前始终询问用户明确的同意。** **不要**修补 IaC。 |

**第三步：在两个部署中应用修补（首先进行快速修复）**

IaC 补丁框架（检测、AVM 模块指导、部署顺序规则、存储 SKU 补丁）位于：

| IaC 类型 | 框架参考 |
|---|---|
| Bicep | [references/iac-patching-bicep.md](references/iac-patching-bicep.md) |
| Terraform | [references/iac-patching-terraform.md](references/iac-patching-terraform.md) |

实际的 **每个服务的计算修补**（Function App 计划 ZR、App Service Plan ZR 等）位于每个服务参考中 — 从第二阶段加载匹配的服务文件以获取确切的 Bicep / Terraform / AVM 片段。在此技能版本中，只有 Azure Functions 和 App Service 有每个服务参考；容器应用不在范围内。

**部署 1 — 仅快速修复。** 补丁 🟢 安全项目（App Service/Function App 计划的区域冗余、Basic/Standard/Premium / Dedicated 的健康探针）。**不要**在此部署中包含存储 SKU 补丁。

修补后，**技能将自行运行部署**（不要停止并告诉用户运行它）。检测部署工具并在执行前确认一次：

```
📦 已将修补应用于您的 IaC。准备部署：
   工具检测到：azd (找到 azure.yaml)
   命令：       azd up

继续部署？ (是 / 否)
```

在 **是**，运行相应的命令，将输出流回用户，并在成功后继续到下一步：
- AZD 项目（有 `azure.yaml`）：`azd up`
- 仅 Bicep：`az deployment group create --resource-group <rg> --template-file infra/main.bicep --parameters @infra/main.parameters.json`
- Terraform：`terraform plan -out tfplan` → (显示计划摘要) → `terraform apply tfplan`

在**否**的情况下，停止并报告已修补的文件；不要继续执行步骤 4 / 重新评估。

如果部署失败，暴露错误并停止——不要继续执行存储步骤。

**⛔ 停止——在部署 2 之前询问存储升级。** 在部署 1 成功后，明确询问用户：

```
✅ 已部署快速获胜的修补程序。计算现在具有区域冗余。

要实现**完全的区域冗余**，您的存储帐户也需要升级：
  • stii5trxva2ark4：当前为 `Standard_LRS` → 需要 `Standard_ZRS`

⚠️ 这是一个两步变更：
   1. 活体存储迁移 (`az storage account migration start`) — 持续数小时至数天
   2. 第二次部署以更新您的 IaC 的存储 SKU 以匹配

您要让我现在开始存储迁移吗？(是 / 否 / 稍后)
```

- **是** → 技能自行运行迁移命令，轮询直至完成，然后在 IaC 中修补存储 SKU 并运行**部署 2**（现在是无操作确认）。用户无需手动执行任何操作。
- **否 / 稍后** → 不应用存储 SKU 补丁。在重新评估中注明 ZR 存储仍然存在差距；建议稍后重新访问。

**步骤 4：存储迁移（仅在步骤 3 中用户回答是的情况下）**

技能自行运行这些命令——不要要求用户运行它们。显示进度：

```
🔄 开始存储迁移（这可能需要长达 72 小时）...

   az storage account migration start --name stii5trxva2ark4 \
     --resource-group rg-example --sku Standard_ZRS --no-wait

   轮询：az storage account show --name stii5trxva2ark4 --query sku.name
   ...
   ✅ 迁移完成：sku.name = Standard_ZRS
```

对于非常长的迁移，您可以将检查点展示给用户（“仍在运行，稍后检查”）而不是阻塞整个对话。

**步骤 5：部署 2 — 存储SKU修补**

迁移完成后，技能将在 IaC 中修补存储 SKU 并运行与步骤 3 相同的部署命令（例如 `azd up`）。此部署是无操作确认，确认 IaC 与实时状态匹配。在执行前与用户确认一次，然后直接运行。

### 步骤 2（两条路径）：重新评估

应用更改（CLI）或部署（IaC）后，自动重新运行评估并显示与阶段 3 相同的**按功能划分的表格**，每个功能行的状态更新以反映新状态。简要说明自上次运行以来发生了什么更改。

```
🔄 可靠性重新评估 — rg-eventhubs-python-jan13 (eastus)
───────────────────────────────────────────────────────────────────────────────────────
可靠性功能              状态      资源
───────────────────────────────────────────────────────────────────────────────────────
区域冗余 — 计算        🟢 开启       • plan-ii5trxva2ark4 (FC1)              — 现在开启
                                             • plan-web-ii5trxva2ark4 (P1v3)         — 现在开启

区域冗余存储           🟢 ZRS      • stii5trxva2ark4                       — GRS → ZRS

健康探测                    🟡 部分开启  • func-api-ii5trxva2ark4                — 仍然关闭（FC1，代码更改拒绝）
                                             • app-web-ii5trxva2ark4                 — 现在开启

跨区域故障转移            🔴 关闭      • 仅单个区域（eastus）
───────────────────────────────────────────────────────────────────────────────────────

发生的变化：函数应用和 App Service 计划的区域冗余、存储复制和 App Service 的健康探测。
（下一步提供跨区域——见步骤 3。）
```

### 步骤 3（两条路径）：跨区域后续——询问和等待

跨区域是一个显著的成本/复杂性步骤。**不要**自动开始它。重新评估后，只有当**所有核心单区域可靠性功能都是 🟢 开启**（区域冗余计算、ZRS/GZRS 存储和健康探测）时，才明确询问用户并在**等待其响应**后再执行任何操作：

```
🟢 您的应用现在在 {区域} 中完全具有区域冗余。

下一步（可选）是使用 Azure Front Door 的跨区域故障转移：
   • 在第二个区域部署计算 + 存储（推荐配对区域）
   • 添加 Azure Front Door 以实现基于健康探测的故障转移的全局负载均衡
   • 防止整个区域中断
   • 预计额外成本：计算约 2 倍（主动-被动）；Front Door 约 $35/月基础费用

您要让我现在设置跨区域故障转移吗？(是 / 否 / 稍后)
```

- **是** → 继续 [参考资料/配置跨区域.md](references/configure-multi-region.md)。与用户确认次要区域选择，然后：
  1. 生成跨区域 IaC（Bicep / Terraform 添加次要区域 + Front Door 的内容）。
  2. 与用户确认一次：`📦 已生成跨区域 IaC。准备使用 `azd up` 部署。继续？(是 / 否)`
  3. 在**是**的情况下，**技能自行运行部署**（`azd up` / `az deployment group create` / `terraform apply`）并流式传输输出。不要停止并告诉用户运行它。
  4. 部署成功后，运行最终重新评估，以便用户看到跨区域故障转移变为 🟢 开启。
- **否 / 稍后** → 保持部署不变。注明单区域区域冗余是一个可靠的最终状态；跨区域可以随时重新访问。

> **⛔ 不要跳过等待。** 在用户明确表示是之前，不要生成跨区域 IaC、部署 Front Door 或修改任何文件。如果核心可靠性尚未全部 🟢，则**不要**询问跨区域——先完成核心差距。

## 优先级分类

| 优先级 | 标准 | 操作 |
|---|---|---|
| 关键 | 无区域冗余 AND 生产工作负载 | 立即修复 |
| 高 | 区域冗余计算上的 LRS 存储 | 在数天内修复 |
| 中等 | 无跨区域（单区域但区域冗余） | 计划下一个冲刺 |
| 低 | 缺少健康探测或监控差距 | 跟踪并修复 |

## 错误处理

| 错误 | 消息 | 补救措施 |
|---|---|---|
| 需要身份验证 | "请登录" | 运行 `az login` 并重试 |
| 访问被拒绝 | "禁止" | 确认读取者/贡献者角色分配 |
| 计划不支持 ZR | "需要升级" | 告知用户计划升级路径 + 成本差异 |
| 区域不支持 AZ | "区域限制" | 建议支持的区域 |

## 最佳实践

- 每次重大基础设施更改后运行可靠性评估
- 定期（至少每季度）测试故障转移场景

## 技能边界

| 操作 | 此技能执行 | 转交至 |
|---|---|---|
| 评估可靠性状态 | ✅ 是 | — |
| 推荐改进 | ✅ 是 | — |
| 启用区域冗余（CLI 命令） | ✅ 是 | — |
| 为可靠性修补 Bicep/Terraform | ✅ 是 | — |
| 生成跨区域 IaC | ✅ 是（添加次要区域 + Front Door） | `azure-prepare` 用于全新应用的 IaC 框架 |
| 部署 IaC 以进行可靠性更改 | ✅ 是（自行运行 `azd up` / `terraform apply` / `az deployment`，在用户确认后） | `azure-deploy` 用于通用/非可靠性部署 |
| 验证预部署 | 仅可靠性检查 | `azure-validate` 用于全面验证 |
