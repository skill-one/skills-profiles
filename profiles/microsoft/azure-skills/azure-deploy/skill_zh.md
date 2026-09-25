# Azure 部署

> **权威指导 — 强制合规**
>
> **前提条件**：在执行此技能之前，**MUST** 调用并完成 **azure-validate** 技能，状态必须为 `Validated`。

> **⛔ 停止 — 需要检查前提条件**
> 在继续之前，请验证以下两个前提条件是否满足：
>
> 1. **azure-prepare** 被调用并完成 → 存在 `.azure/deployment-plan.md`
> 2. **azure-validate** 被调用并通过 → 计划状态 = `Validated`
>
> 如果其中任何一个缺失，**立即停止**：
> - 没有计划？ → 首先调用 **azure-prepare** 技能
> - 状态不是 `Validated`？ → 首先调用 **azure-validate** 技能
>
> **⛔ 不要手动更新计划状态**
>
> 你**禁止**自行更改计划状态为 `Validated`。只有 **azure-validate** 技能在运行实际验证检查后才有权设置此状态。如果你在未运行验证的情况下更新状态，部署将失败。
>
> **不要假设**应用已准备好。**不要跳过**验证以节省时间。跳过步骤会导致部署失败。完整的流程确保成功：
>
> `azure-prepare` → `azure-validate` → `azure-deploy`

## 触发条件

在以下情况下激活此技能：
- 执行已准备好的应用的部署（存在 azure.yaml 和 infra/）
- 推送现有 Azure 部署的更新
- 在已准备的项目上运行 `azd up`、`azd deploy` 或 `az deployment`
- 将已构建的代码发送到生产环境
- 部署已包含 API 管理网关（APIM）基础设施的应用

> **范围**：此技能执行部署。它不会创建应用、生成基础设施代码或搭建项目。对于这些任务，请使用 **azure-prepare**。

> **APIM / AI 网关**：使用此技能部署在 **azure-prepare** 阶段已创建 APIM/AI 网关基础设施的应用。对于创建或更改 APIM 资源，请参阅 [APIM 部署指南](https://learn.microsoft.com/azure/api-management/get-started-create-service-instance)。对于 AI 治理策略，请调用 **azure-aigateway** 技能。

## 规则

1. 在 `azure-prepare` 和 `azure-validate` 之后运行
2. 必须存在 `.azure/deployment-plan.md` 且状态为 `Validated`
3. **需要预部署检查清单** — [预部署检查清单](references/pre-deploy-checklist.md)
4. ⛔ **破坏性行动需要 `ask_user`** — [全局规则](references/global-rules.md)
5. **范围：仅执行部署** — 此技能拥有 `azd up`、`azd deploy`、`terraform apply` 和 `az deployment` 命令的执行。这些命令通过此技能的错误恢复和验证管道运行。

---

## 步骤

| # | 操作 | 参考 |
|---|--------|-----------|
| 1 | **检查计划** — 读取 `.azure/deployment-plan.md`，验证状态 = `Validated` **且**“验证证明”部分已填充 | `.azure/deployment-plan.md` |
| 2 | **预部署检查清单** — 必须完成所有步骤 | [预部署检查清单](references/pre-deploy-checklist.md) |
| 3 | **加载配方** — 根据 `.azure/deployment-plan.md` 中的 `recipe.type` | [recipes/README.md](references/recipes/README.md) |
| 4 | **RBAC 健康检查** — 对于容器应用 + ACR 带有托管身份：运行 `azd provision --no-prompt`，然后验证 `AcrPull` 角色是否已传播后再继续（见检查清单） | [预部署检查清单 — 容器应用 RBAC](references/pre-deploy-checklist.md#container-apps--acr--pre-deploy-rbac-health-check) |
| 5 | **执行部署** — 按照配方步骤 | 配方 README |
| 6 | **部署后** — 配置 SQL 托管身份并应用 EF 迁移（如果适用） | [部署后](references/recipes/azd/post-deployment.md) |
| 7 | **处理错误** — 参考配方的 `errors.md` | — |
| 8 | **验证成功** — 确认部署完成且端点可访问 | [验证](references/recipes/azd/verify.md) |
| 9 | **实时角色验证** — 查询 Azure 以确认已配置的 RBAC 角色是否正确且充足 | [live-role-verification.md](references/live-role-verification.md) |
| 10 | **报告结果** — 向用户展示部署的端点 URL，作为完全限定 `https://` 链接 | [验证](references/recipes/azd/verify.md) |

> **⛔ URL 格式规则**
>
> 在向用户展示端点 URL 时，你**必须**始终使用带有 `https://` 方案的完全限定 URL（例如 `https://myapp.azurewebsites.net`，而不是 `myapp.azurewebsites.net`）。许多 Azure CLI 命令返回不带方案的裸主机名 — 在展示前始终添加 `https://`。

> **⛔ 验证证明检查**
>
> 在检查计划时，验证 **验证证明**部分（第 7 节）是否包含实际验证结果、运行的命令和时间戳。如果此部分为空，则验证被跳过 — 首先调用 **azure-validate** 技能。

## SDK 快速参考

- **Azure 开发者 CLI**：[azd](references/sdk/azd-deployment.md)
- **Azure 身份**：[Python](references/sdk/azure-identity-py.md) | [.NET](references/sdk/azure-identity-dotnet.md) | [TypeScript](references/sdk/azure-identity-ts.md) | [Java](references/sdk/azure-identity-java.md)

## MCP 工具

| 工具 | 目的 |
|------|---------|
| `mcp_azure_mcp_subscription_list` | 列出可用订阅 |
| `mcp_azure_mcp_group_list` | 列出订阅中的资源组 |
| `mcp_azure_mcp_azd` | 执行 AZD 命令 |
| `azure__role` | 列出用于实时 RBAC 验证（步骤 9）的角色分配 |

## 参考

- [故障排除](references/troubleshooting.md) - 常见问题和解决方案
- [部署后步骤](references/recipes/azd/post-deployment.md) - SQL + EF Core 设置
