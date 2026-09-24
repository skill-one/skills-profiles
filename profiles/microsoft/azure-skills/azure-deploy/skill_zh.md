# Azure Deploy

> **权威指引 — 强制合规**
>
> **前提条件**：在执行本技能之前，**必须**调用并完成 **azure-validate** 技能，且状态为 `Validated`。

> **⛔ 停止 — 前提条件检查必要**
> 在继续之前，请验证两个前提条件均已满足：
>
> 1. **azure-prepare** 已被调用并完成 → `.azure/deployment-plan.md` 存在
> 2. **azure-validate** 已被调用且通过 → 计划状态 = `Validated`
>
> 如果**任一**缺失，**立即停止**：
> - 无计划？→ 首先调用 **azure-prepare** 技能
> - 状态非 `Validated`？→ 首先调用 **azure-validate** 技能
>
> **⛔ 不要手动更新计划状态**
>
> 你**被禁止**自行将计划状态修改为 `Validated`。只有在执行实际验证检查后，**azure-validate** 技能才有权限设置此状态。如果你在未运行验证的情况下更新状态，部署将会失败。
>
> **不要假设**应用已就绪。**不要**为节省时间而跳过验证。跳过步骤会导致部署失败。完整的流程确保成功：
>
> `azure-prepare` → `azure-validate` → `azure-deploy`

## 触发条件

在用户希望以下情况时激活本技能：
- 执行已准备应用（azure.yaml 和 infra/ 存在）的部署
- 向已存在的 Azure 部署推送更新
- 在已准备的项目上运行 `azd up`、`azd deploy` 或 `az deployment`
- 将已构建的代码部署到生产环境
- 部署已包含 API Management (APIM) 网关基础设施的应用程序

> **范围**：本技能执行部署。它不创建应用程序、生成基础设施代码或搭建项目。对于这些任务，请使用 **azure-prepare**。

> **APIM / AI Gateway**：使用本技能部署在 **azure-prepare** 过程中已创建 APIM/AI 网关基础设施的应用程序。创建或修改 APIM 资源时，请参阅 [APIM 部署指南](https://learn.microsoft.com/azure/api-management/get-started-create-service-instance)。对于 AI 治理策略，调用 **azure-aigateway** 技能。

## 规则

1. 在 azure-prepare 和 azure-validate 之后执行
2. `.azure/deployment-plan.md` 必须存在，且状态为 `Validated`
3. **必须完成预部署检查清单** — [预部署检查清单](references/pre-deploy-checklist.md)
4. ⛔ **破坏性操作需要 `ask_user`** — [全局规则](references/global-rules.md)
5. **范围：仅执行部署** — 本技能负责执行 `azd up`、`azd deploy`、`terraform apply` 和 `az deployment` 命令。这些命令通过本技能的错误恢复与验证流程运行。

---

## 步骤

| # | 行动 | 参考 |
|---|--------|-----------|
| 1 | **检查计划** — 读取 `.azure/deployment-plan.md`，验证状态 = `Validated` 且 **验证证明** 部分已填写 | `.azure/deployment-plan.md` |
| 2 | **预部署检查清单** — 必须完成所有步骤 | [预部署检查清单](references/pre-deploy-checklist.md) |
| 3 | **加载 Recipe** — 基于 `.azure/deployment-plan.md` 中的 `recipe.type` | [recipes/README.md](references/recipes/README.md) |
| 4 | **RBAC 健康检查** — 对于使用托管标识的 Container Apps + ACR：运行 `azd provision --no-prompt`，然后在进行操作前验证 `AcrPull` 角色已传播（参见检查清单） | [Pre-Deploy Checklist — Container Apps RBAC](references/pre-deploy-checklist.md#container-apps--acr--pre-deploy-rbac-health-check) |
| 5 | **执行部署** — 按照 Recipe 步骤操作 | Recipe README |
| 6 | **部署后处理** — 配置 SQL 托管标识，如适用则应用 EF 迁移 | [Post-Deployment](references/recipes/azd/post-deployment.md) |
| 7 | **处理错误** — 参阅 Recipe 的 `errors.md` | — |
| 8 | **验证成功** — 确认部署已完成且端点可访问 | [Verification](references/recipes/azd/verify.md) |
| 9 | **实时角色验证** — 查询 Azure，确认已配置的 RBAC 角色正确且充足 | [live-role-verification.md](references/live-role-verification.md) |
| 10 | **报告结果** — 以完全限定的 `https://` 链接形式向用户展示已部署的端点 URL | [Verification](references/recipes/azd/verify.md) |

> **⛔ URL 格式规则**
>
> 向用户展示端点 URL 时，**必须**始终使用带有 `https://` 协议的完全限定 URL（例如 `https://myapp.azurewebsites.net`，而非 `myapp.azurewebsites.net`）。许多 Azure CLI 命令返回不带协议的纯主机名——在呈现之前始终添加 `https://` 前缀。

> **⛔ 验证证明检查**
>
> 在检查计划时，验证 **验证证明** 部分（第 7 节）包含实际验证结果，包括已运行的命令和时间戳。如果该部分为空，则验证被绕过——首先调用 **azure-validate** 技能。

## SDK 快速参考

- **Azure 开发者 CLI**: [azd](references/sdk/azd-deployment.md)
- **Azure Identity**: [Python](references/sdk/azure-identity-py.md) | [.NET](references/sdk/azure-identity-dotnet.md) | TypeScript | [Java](references/sdk/azure-identity-java.md)

## MCP 工具

| 工具 | 用途 |
|------|---------|
| `mcp_azure_mcp_subscription_list` | 列出可用订阅 |
| `mcp_azure_mcp_group_list` | 列出订阅中的资源组 |
| `mcp_azure_mcp_azd` | 执行 AZD 命令 |
| `azure__role` | 列出实时 RBAC 验证（第 9 步）的角色分配 |

## 参考

- [故障排除](references/troubleshooting.md) - 常见问题及解决方案
- [部署后步骤](references/recipes/azd/post-deployment.md) - SQL + EF Core 配置
