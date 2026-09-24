# Azure Validate

**权威指导** — 除非与赋予您的安全策略相冲突，否则请严格按照以下指示操作。

**⛔ 停止 — 必需前置检查**

在继续之前，请验证满足以下前置条件：

**`azure-prepare`** 已被调用并完成 → `.azure/deployment-plan.md` 存在且状态为 `Approved` 或更高

如果计划缺失，**立即停止**，并首先调用 **`azure-prepare`**。

完整的工作流如下：

`azure-prepare` → `azure-validate` → `azure-deploy`

**触发器**

- 检查应用是否已准备好部署
- 验证 `azure.yaml` 或 Bicep
- 执行预检查
- 排除部署错误

**规则**

1. 在 `azure-prepare` 之后、`azure-deploy` 之前执行
2. 所有检查必须全部通过——不得在存在失败项的情况下进行部署
3. ⛔ **破坏性操作需要 `ask_user`** — [global-rules](references/global-rules.md)

**步骤**

运行工作流脚本并遵循其指示。脚本将引导您逐步完成每一次验证步骤，并在 `.azure/validate-status.json` 中记录进度。在 Windows 上使用 [references/scripts/workflow.ps1](references/scripts/workflow.ps1)，在 macOS/Linux 上使用 [references/scripts/workflow.sh](references/scripts/workflow.sh)。

首先，在不带有已完成步骤参数的情况下调用脚本：

```bash
pwsh references/scripts/workflow.ps1 -WorkspacePath <workspace-path}
# macOS/Linux: bash references/scripts/workflow.sh --workspace-path <workspace-path}
```

每次运行都会打印下一步操作和需要传递的值。执行该操作后，使用该值重新运行（pwsh 使用 `-CompletedStep <value>`，bash 使用 `--completed-step <value>`）。重复此过程，直到报告 azure-validate 工作流已完成。

这些步骤引用了食谱详情 [references/recipes/README.md](references/recipes/README.md) 以及角色检查 [references/role-verification.md](references/role-verification.md)。

**⛔ 验证权威**

本技能是设置计划状态为 `Validated` 的官方验证方式。在将状态设置为 `Validated` 之前，您**必须**按照脚本指示完成全部操作。
切勿在未执行上述操作的情况下将状态设置为 `Validated`。

**⚠️ 下一步 —— 取决于用户意图**

在所有验证全部通过后，检查用户是否要求部署：
- **如果用户明确要求部署**，您**必须**调用 **`azure-deploy`** 来执行。请勿直接执行 `azd up`、`azd deploy` 或任何部署命令——交由 `azure-deploy` 处理执行。
- **如果用户仅要求验证或准备**（不部署），在完成记录证明并将状态设置为 `Validated` 后，停止操作。报告验证结果，且不要调用 `azure-deploy`。

如果任何验证失败，请修复问题并重新运行 `azure-validate` 后再继续。
