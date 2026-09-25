# Azure 验证

> **权威指南** — 请严格按照以下说明操作，除非它们与所提供的安全策略相冲突。

> **⛔ 停止 — 前置条件检查要求**
>
> 在继续之前，请验证以下前置条件是否满足：
>
> **azure-prepare** 被调用并完成 → `.azure/deployment-plan.md` 存在且状态为 `Approved` 或更高
>
> 如果计划缺失，**立即停止**并首先调用 **azure-prepare**。
>
> 完整的工作流程确保成功：
>
> `azure-prepare` → `azure-validate` → `azure-deploy`

## 触发器

- 检查应用程序是否准备好部署
- 验证 azure.yaml 或 Bicep
- 运行预检
- 排查部署错误

## 规则

1. 在 azure-prepare 之后、azure-deploy 之前运行
2. 所有检查必须通过 — 出错时不要部署
3. ⛔ **破坏性行动需要 `ask_user`** — [全局规则](references/global-rules.md)

## 步骤

运行工作流脚本并遵循其指示。它会逐一引导您完成每个验证步骤，并在 `.azure/validate-status.json` 中记录进度。在 Windows 上使用 [references/scripts/workflow.ps1](references/scripts/workflow.ps1)，在 macOS/Linux 上使用 [references/scripts/workflow.sh](references/scripts/workflow.sh)。

首先调用脚本**不带**完成步骤参数：

```bash
pwsh references/scripts/workflow.ps1 -WorkspacePath <workspace-path>
# macOS/Linux: bash references/scripts/workflow.sh --workspace-path <workspace-path>
```

每次运行都会打印下一步操作和要传递的值。执行该操作，然后重新运行并使用该值 (`-CompletedStep <value>` 用于 pwsh，`--completed-step <value>` 用于 bash)。重复操作，直到它报告 azure-validate 工作流已完成。

步骤参考 [references/recipes/README.md](references/recipes/README.md) 中的配方详情和 [references/role-verification.md](references/role-verification.md) 中的角色检查。

> **⛔ 验证权威**
>
> 这是将计划状态设置为 `Validated` 的官方验证方法。在将状态设置为 `Validated` 之前，您**必须**按照脚本的指示完成操作。
> **不要**在未执行此操作的情况下将状态设置为 `Validated`。

---

> **⚠️ 下一步 — 取决于用户意图**
>
> 所有验证通过后，请检查用户是否要求部署：
> - **如果用户明确要求部署**，您**必须**调用 **azure-deploy** 来执行。**不要**直接运行 `azd up`、`azd deploy` 或任何部署命令 — 让 azure-deploy 处理执行。
> - **如果用户仅要求验证或准备**（不部署），在记录证据并将状态设置为 `Validated` 后停止。报告验证结果并**不要**调用 azure-deploy。
>
> 如果任何验证失败，请修复问题并重新运行 azure-validate 后再继续。
