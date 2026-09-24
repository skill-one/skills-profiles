# Azure App Onboard

> ⛔ **每个仓库都会经过完整流水线（第 1–10 步）。无例外。** 不要跳步、拒绝或根据你识别到的内容绕开流程。请按下方工作流表格顺序执行——行动前先阅读每一步的参考资料。

## 快速参考

| Property | Value |
|----------|-------|
| 适用对象 | 了解要构建什么，但不了解应使用哪些 Azure 服务的开发者 |
| 输入 | 业务构想或现有代码库，预算/规模偏好（可选） |
| 输出 | 架构方案、成本估算、IaC 文件、已部署的 Azure 资源 |
| 阶段 | 发现 → 架构 → 搭建 → 部署（自包含，不调用外部技能） |

## 何时使用此技能

- 部署现有代码，但不知道应使用哪些 Azure 服务
- 检查现有代码是否已准备好部署到 Azure
- 将现有应用迁移到 Azure，无需重写或仅做少量修改
- 在决定基础设施投入前获取成本估算
- 理解架构决策及被否决的替代方案
- 获取关于 Azure 架构或服务选择问题的答复（例如：“我应该使用什么数据库？”）
- 在缺乏先前经验的情况下获得引导式 Azure 入门指导

## 不使用场景

| 场景 | 改用 |
|----------|-------------|
| 运行 `azd up` 或执行现有部署 | `azure-deploy` |
| 优化现有 Azure 支出 | `azure-cost` |
| 为已知架构生成 Bicep/Terraform 文件 | `azure-prepare` |
| 验证基础设施或执行预检检查 | `azure-validate` |
| 排查运行中的 Azure 部署问题 | `azure-diagnostics` |
| 直接部署或管理 AKS/Kubernetes | `azure-kubernetes` |
| 查询或列出现有 Azure 资源 | `azure-resource-lookup` |

## 流水线规则

> ⛔ **你必须在每次 AppOnboard 会话开始时阅读 [`references/pipeline-rules.md`](references/pipeline-rules.md)。** 其中包含审批关卡、阶段生命周期、会话产物、deploy-as-is（按现状部署）及安全基线规则。

## 工作流

> ⛔ **部署恢复：** 在部署关卡批准之后，或在任何 `az deployment`/`az webapp deploy`/`az acr build` 之前——如果你尚未阅读 `deploy/SKILL.md`，请先阅读 `.copilot-azure/sessions/{id}/deploy-checklist.md`，再阅读 `deploy/SKILL.md`。⛔ 切勿调用 `{"skill": "azure-deploy"}`——这是另一个技能、用于另一个工作流。

> ⛔ **搭建后过渡（强制）：** 在 `scaffold-manifest.json` 写入后，您的下一步操作必须为第 8 步（部署审批关卡）——不得是总结报告、不得是“以下是生成的文件”的说明、不得是完成信号。请确认 `context.json` 包含 `completedPhases: [...,"scaffold"]` + `currentPhase: "deploy"`（如果搭建子代理未更新，请自行更新）。若已脱离上下文（搭建参考加载较重），重新阅读 [approval-gates.md § Deploy Gate](references/approval-gates.md)，随后呈现以下确切提示：**"🚀 准备部署？（是 / 手动执行 / 修改方案 / 取消）"**。此关卡是您回复内容的最后部分——等待用户回复。

| # | 步骤 | 操作 | 参考资料 |
|---|------|--------|-----------|
| 1 | **会话检查 + Azure 登录** | 创建/恢复会话，验证 Azure CLI 认证，解析订阅 + 用户身份 | ⛔ **你必须阅读 [session-protocol.md](references/session-protocol.md)** |
| 2 | **范围分诊** | 检查 azd 标记，对问题进行分类。工作区为空或仅含代码（无基础设施）→ 直接进入第 3 步。 | ⛔ 阅读 [intent-gathering.md](references/intent-gathering.md) § Scope Triage |
| 3 | **前置条件扫描** | ⛔ 若 `completedPhases` 包含 `"prereq"`，则跳过。否则：调用 `{"skill": "azure-app-onboard-prereq"}`。编写 `prereq-output.json`，更新 `context.json`。**若遇到以下情况需暂停：** `overallHealth: "blocked"` 或 `routeToSkill` 已设置。 | |
| 4 | **收集意图** | 呈现前置条件结果，确认技术栈 + Azure 服务，提出其余问题。 | ⛔ 阅读 [intent-gathering.md](references/intent-gathering.md) § After Prereq Returns |
| 5 | **规划架构** | 编写 `prepare-plan.json`。 | ⛔ **你必须阅读 [prepare/SKILL.md](prepare/SKILL.md)** |
| 6 | **搭建审批关卡** | 在生成任何文件之前，向用户展示方案以供审批。 | ⛔ 阅读 [approval-gates.md](references/approval-gates.md) § Scaffold Gate |
| 7 | **搭建** | 生成 IaC 文件，进行自检。编写 `scaffold-manifest.json`。更新 `context.json`。 | ⛔ **你必须阅读 [scaffold/SKILL.md](scaffold/SKILL.md)** |
| 8 | **部署审批关卡** | 展示验证总结。⛔ 获批后：首先阅读 deploy-checklist.md → deploy/SKILL.md。切勿调用 `{"skill": "azure-deploy"}`。 | ⛔ 阅读 [approval-gates.md](references/approval-gates.md) § Deploy Gate |
| 9 | **部署** | 执行 IaC 文件，执行健康检查。编写 `deploy-result.json`。 | ⛔ **你必须阅读 [deploy/SKILL.md](deploy/SKILL.md)** |
| 10 | **交接** | 呈现部署身份、清理命令、后续步骤。 | ⛔ **你必须阅读 [`handoff-protocol.md`](references/handoff-protocol.md)** |

## 错误处理

| 错误 | 修复方案 |
|-------|-------------|
| 阶段失败 | 暂停，报告阶段及错误。由用户决定：重试、跳过或终止。 |
| MCP 服务器不可用 | 跳过受影响检查，在 `costEstimate.assumptions[]` 及每个审批关卡中添加免责声明。 |
| 缺少 RBAC | 报告所需角色及 `az role assignment` 命令。 |

> **共享参考资料：** [MCP 工具](references/mcp-tool-reference.md)（跨阶段工具参数） | [IaC 资源](references/iac-resources.md)（用于故障排查的 Azure 资源文档）
