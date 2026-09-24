# Azure Upgrade

> 本技能负责对现有 Azure 工作负载进行**评估和自动化升级**，将其从一种 Azure 服务、托管计划或 SKU 升级到另一种 — 全部均在 Azure 内完成。这包括计划/层级升级（例如 Consumption → Flex Consumption）、跨服务迁移（例如 App Service → Container Apps）以及 SKU 变更。它还涵盖**Azure SDK for Java 源码现代化**（例如旧版 Java `com.microsoft.azure.*` → 现代 `com.azure.*`）。这并非用于跨云迁移 — 请使用 `azure-cloud-migrate` 完成该项工作。

## 触发条件

| 用户意图 | 示例提示 |
|---------|-----------------|
| 升级 Azure Functions 计划 | "将我的函数应用从 Consumption 升级到 Flex Consumption" |
| 更改托管层级 | "将我的函数应用移至更好的计划" |
| 评估升级就绪情况 | "我的函数应用是否已准备好升级到 Flex Consumption？" |
| 自动化计划迁移 | "自动化升级我 Functions 计划的步骤" |
| 现代化旧版 Azure Java SDK | "迁移旧版 Azure Java SDK"、"升级旧版 Azure Java SDK"、"将我的 Java 项目从 com.microsoft.azure 迁移到 com.azure" |
| 将 Azure Cache for Redis（ACR/OSS）迁移到 Azure Managed Redis（AMR） | "将我的 Redis 缓存迁移到 AMR"、"ACR 到 AMR"、"OSS 到 AMR"、"将我的 Premium P2 缓存升级到 Managed Redis"、"选择 AMR SKU"、"将我的 Redis IaC 模板转换为 AMR" |
| 将 Azure Cache for Redis Enterprise（ACRE）迁移到 Azure Managed Redis（AMR） | "将我的 Enterprise_E10 缓存迁移到 AMR"、"ACRE 到 AMR"、"更新我的 ACRE IaC 模板以适配 AMR"、"将 EnterpriseFlash 迁移到 AMR"、"迁移我地理复制的 Enterprise Redis" |

## 规则

1. 按顺序执行阶段，不得跳过
2. 在任何升级操作之前生成评估
3. 加载场景参考并遵循其规则
4. 使用 `mcp_azure_mcp_get_azure_bestpractices` 和 `mcp_azure_mcp_documentation` MCP 工具
5. 破坏性操作需要 `ask_user` — [global-rules](references/global-rules.md)
6. 在继续之前，始终与用户确认目标计划/SKU
7. 未经用户明确确认，绝不删除或停止原始应用
8. 所有自动化脚本必须具有幂等性和可恢复性

## 升级场景

| 来源 | 目标 | 参考 |
|--------|--------|-----------|
| Azure Functions Consumption 计划 | Azure Functions Flex Consumption 计划 | [consumption-to-flex.md](references/services/functions/consumption-to-flex.md) |
| 旧版 Azure Java SDK（`com.microsoft.azure.*`） | 现代 Azure Java SDK（`com.azure.*`） | [languages/java/README.md](references/languages/java/README.md) |
| Azure Cache for Redis（ACR/OSS）Basic/Standard/Premium | Azure Managed Redis（AMR） | [services/redis/redis-to-amr.md](references/services/redis/redis-to-amr.md) |
| Azure Cache for Redis Enterprise（ACRE）/ Enterprise Flash | Azure Managed Redis（AMR） | [services/redis/redis-to-amr.md](references/services/redis/redis-to-amr.md) |

> SDK 升级场景（例如 Java 旧版 → 现代）执行的是**源码现代化流程**，与 Azure 服务/计划/SKU 升级不同：请遵循场景参考，**而非**以下步骤。

> 没有匹配的场景？使用 `mcp_azure_mcp_documentation` 和 `mcp_azure_mcp_get_azure_bestpractices` 工具研究升级路径。

## MCP 工具

| 工具 | 用途 |
|------|--------|
| `mcp_azure_mcp_get_azure_bestpractices` | 获取目标服务的 Azure 最佳实践 |
| `mcp_azure_mcp_documentation` | 查询 Azure 关于升级场景的文档 |
| `mcp_azure_mcp_appservice` | 查询 App Service 和 Functions 计划详情 |
| `mcp_azure_mcp_applicationinsights` | 验证监控配置 |

## 步骤

1. **识别** — 确定来源和目标 Azure 计划/SKU。请用户确认。
2. **评估** — 分析现有应用是否具备升级就绪条件 → 加载场景参考（例如 [consumption-to-flex.md](references/services/functions/consumption-to-flex.md)）
3. **迁移前准备** — 从现有应用中收集设置、身份、配置
4. **升级** — 执行自动化升级步骤（创建新资源、迁移设置、部署代码）
5. **验证** — 访问函数应用的默认 URL 以确认应用可达，然后验证端点和监控配置
6. **询问用户** — "升级已完成。您是否需要进行性能验证、清理旧应用或更新 IaC？"
7. **移交** 给 `azure-validate` 进行深度验证，或若用户需要，将 `azure-deploy` 用于 CI/CD 设置

在 workspace 根目录的 `upgrade-status.md` 中跟踪进度。

## 参考资料

- [Global Rules](references/global-rules.md)
- [Workflow Details](references/workflow-details.md)
- **Functions**
  - [Consumption to Flex Consumption](references/services/functions/consumption-to-flex.md)
  - [Assessment](references/services/functions/assessment.md)
  - [Automation Scripts](references/services/functions/automation.md)
- **Redis**
  - [Redis (ACR or ACRE) to AMR Migration](references/services/redis/redis-to-amr.md) — 路由至专门的 [amr-migration-skill](https://github.com/AzureManagedRedis/amr-migration-skill)（ACR/OSS）或 [acre-to-amr-migration-skill](https://github.com/AzureManagedRedis/acre-to-amr-migration-skill)（Enterprise）
- **Java SDK 迁移模板**
  - [Plan Template](references/languages/java/templates/PLAN_TEMPLATE.md)
  - [Progress Template](references/languages/java/templates/PROGRESS_TEMPLATE.md)
  - [Summary Template](references/languages/java/templates/SUMMARY_TEMPLATE.md)

## 后续

升级验证完成后，移交至：
- `azure-validate` — 进行全面的升级后验证
- `azure-deploy` — 若用户需要为新应用配置 CI/CD
