# Azure 升级

> 该技能处理现有 Azure 工作负载从一个 Azure 服务、托管计划或 SKU 升级到另一个 — 所有操作均在 Azure 内完成。这包括计划/层级升级（例如 Consumption → Flex Consumption）、跨服务迁移（例如 App Service → Container Apps）和 SKU 变更。它还涵盖 **Azure Java SDK 源代码现代化**（例如旧版 Java `com.microsoft.azure.*` → 现代 `com.azure.*`）。这不适用于跨云迁移 — 请使用 `azure-cloud-migrate` 进行该操作。

## 触发器

| 用户意图 | 示例提示 |
|-------------|-----------------|
| 升级 Azure Functions 计划 | "将我的函数应用从 Consumption 升级到 Flex Consumption" |
| 更改托管层级 | "将我的函数应用迁移到更好的计划" |
| 评估升级就绪情况 | "我的函数应用是否准备好迁移到 Flex Consumption？" |
| 自动化计划迁移 | "自动化升级我的 Functions 计划的步骤" |
| 现代化旧版 Azure Java SDK | "迁移旧版 Azure Java SDK", "升级旧版 Azure Java SDK", "将我的 Java 项目从 com.microsoft.azure 迁移到 com.azure" |
| 将 Azure Cache for Redis (ACR/OSS) 迁移到 Azure Managed Redis (AMR) | "将我的 Redis 缓存迁移到 AMR", "ACR 到 AMR", "OSS 到 AMR", "将我的 Premium P2 缓存升级到 Managed Redis", "选择一个 AMR SKU", "将我的 Redis IaC 模板转换为 AMR" |
| 将 Azure Cache for Redis Enterprise (ACRE) 迁移到 Azure Managed Redis (AMR) | "将我的 Enterprise_E10 缓存迁移到 AMR", "ACRE 到 AMR", "为 AMR 更新我的 ACRE IaC 模板", "将 EnterpriseFlash 迁移到 AMR", "迁移我的地理复制的 Enterprise Redis" |

## 规则

1. 按阶段顺序执行 — 不得跳过
2. 在任何升级操作之前生成评估
3. 加载场景参考并遵循其规则
4. 使用 `mcp_azure_mcp_get_azure_bestpractices` 和 `mcp_azure_mcp_documentation` MCP 工具
5. 破坏性行动需要 `ask_user` — [全局规则](references/global-rules.md)
6. 在继续之前，始终与用户确认目标计划/SKU
7. 未经明确用户确认，不得删除或停止原始应用
8. 所有自动化脚本必须是无状态的且可恢复

## 升级场景

| 源 | 目标 | 参考 |
|--------|--------|-----------|
| Azure Functions Consumption Plan | Azure Functions Flex Consumption Plan | [consumption-to-flex.md](references/services/functions/consumption-to-flex.md) |
| 旧版 Azure Java SDK (`com.microsoft.azure.*`) | 现代 Azure Java SDK (`com.azure.*`) | [languages/java/README.md](references/languages/java/README.md) |
| Azure Cache for Redis (ACR/OSS) Basic/Standard/Premium | Azure Managed Redis (AMR) | [services/redis/redis-to-amr.md](references/services/redis/redis-to-amr.md) |
| Azure Cache for Redis Enterprise (ACRE) / Enterprise Flash | Azure Managed Redis (AMR) | [services/redis/redis-to-amr.md](references/services/redis/redis-to-amr.md) |

> SDK 升级场景（例如 Java 旧版 → 现代）运行一个 **源代码现代化流程**，该流程与 Azure 服务/计划/SKU 升级不同：请遵循场景参考，**而不是**以下步骤。

> 没有匹配的场景？使用 `mcp_azure_mcp_documentation` 和 `mcp_azure_mcp_get_azure_bestpractices` 工具研究升级路径。

## MCP 工具

| 工具 | 目的 |
|------|---------|
| `mcp_azure_mcp_get_azure_bestpractices` | 获取目标服务的 Azure 最佳实践 |
| `mcp_azure_mcp_documentation` | 查找升级场景的 Azure 文档 |
| `mcp_azure_mcp_appservice` | 查询 App Service 和 Functions 计划详情 |
| `mcp_azure_mcp_applicationinsights` | 验证监控配置 |

## 步骤

1. **识别** — 确定源和目标 Azure 计划/SKU。要求用户确认。
2. **评估** — 分析现有应用以评估升级就绪情况 → 加载场景参考（例如 [consumption-to-flex.md](references/services/functions/consumption-to-flex.md)）
3. **预迁移** — 从现有应用收集设置、身份、配置
4. **升级** — 执行自动化升级步骤（创建新资源、迁移设置、部署代码）
5. **验证** — 访问函数应用默认 URL 以确认应用可访问，然后验证端点和监控
6. **询问用户** — "升级完成。您是否要验证性能、清理旧应用或更新您的 IaC？"
7. **交接** 给 `azure-validate` 进行深度验证或 `azure-deploy` 进行 CI/CD 设置

在 `upgrade-status.md` 中跟踪工作空间根目录中的进度。

## 参考

- [全局规则](references/global-rules.md)
- [工作流详情](references/workflow-details.md)
- **函数**
  - [Consumption to Flex Consumption](references/services/functions/consumption-to-flex.md)
  - [评估](references/services/functions/assessment.md)
  - [自动化脚本](references/services/functions/automation.md)
- **Redis**
  - [Redis (ACR 或 ACRE) 到 AMR 迁移](references/services/redis/redis-to-amr.md) — 路由到专门的 [amr-migration-skill](https://github.com/AzureManagedRedis/amr-migration-skill) (ACR/OSS) 或 [acre-to-amr-migration-skill](https://github.com/AzureManagedRedis/acre-to-amr-migration-skill) (Enterprise)
- **Java SDK 迁移模板**
  - [计划模板](references/languages/java/templates/PLAN_TEMPLATE.md)
  - [进度模板](references/languages/java/templates/PROGRESS_TEMPLATE.md)
  - [摘要模板](references/languages/java/templates/SUMMARY_TEMPLATE.md)

## 下一步

验证升级后，交接给：
- `azure-validate` — 进行彻底的升级后验证
- `azure-deploy` — 如果用户希望为新应用设置 CI/CD
