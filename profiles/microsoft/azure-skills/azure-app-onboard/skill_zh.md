# Azure 应用快速部署

> ⛔ **所有仓库都必须经过完整流程（步骤1-10），无一例外。** 不要根据你的认知跳过步骤、拒绝或绕过。请按顺序遵循下表中的工作流——在采取行动前，请阅读每个步骤的参考链接。

## 快速参考

| 属性 | 值 |
|----------|-------|
| 适用于 | 知道要构建什么但不知道要使用哪些 Azure 服务的开发者 |
| 输入 | 商业想法或现有代码库，预算/规模偏好（可选） |
| 输出 | 架构计划、成本估算、IaC 文件、部署的 Azure 资源 |
| 阶段 | 发现 → 架构设计 → 框架搭建 → 部署（自包含，无需调用外部技能） |

## 何时使用此技能

- 部署现有代码而不知道要使用哪些 Azure 服务
- 检查现有代码是否已准备好部署到 Azure
- 将现有应用程序迁移到 Azure 而无需重写或最小化更改
- 在承诺基础设施之前获取成本估算
- 了解架构决策和被拒绝的替代方案
- 获取有关 Azure 架构或服务选择的答案（例如，“我应该使用什么数据库？”）
- 无需先前经验即可获得引导式 Azure 快速部署

## 何时不应使用

| 场景 | 使用替代方案 |
|----------|-------------|
| 运行 `azd up` 或执行现有部署 | `azure-deploy` |
| 优化现有 Azure 花费 | `azure-cost` |
| 为已知架构生成 Bicep/Terraform | `azure-prepare` |
| 验证基础设施或运行预检检查 | `azure-validate` |
| 故障排除正在运行的 Azure 部署 | `azure-diagnostics` |
| 直接部署到或管理 AKS/Kubernetes | `azure-kubernetes` |
| 查找或列出现有 Azure 资源 | `azure-resource-lookup` |

## 流程规则

> ⛔ **在每次 AppOnboard 会话开始时，你必须阅读 [`references/pipeline-rules.md`](references/pipeline-rules.md)。** 它包含审批门禁、阶段生命周期、会话工件、直接部署和安全性基线规则。

## 工作流

> ⛔ **部署恢复：** 在部署门禁批准后或在任何 `az deployment`/`az webapp deploy`/`az acr build` 之前——如果你没有阅读 `deploy/SKILL.md`，请先阅读 `.copilot-azure/sessions/{id}/deploy-checklist.md`，然后阅读 `deploy/SKILL.md`。⛔ 绝不调用 `{"skill": "azure-deploy"}`——那是用于不同工作流的另一种技能。

> ⛔ **框架搭建后过渡（强制执行）：** 在 `scaffold-manifest.json` 写入后立即，你的下一步操作必须是步骤 8（部署门禁）——不是摘要报告，不是“这是生成的文件”消息，不是完成信号。确认 `context.json` 包含 `completedPhases: [...,"scaffold"]` + `currentPhase: "deploy"`（如果框架子代理没有更新，请自行更新）。如果被从上下文中移除（框架参考加载很重），请重新阅读 [approval-gates.md § Deploy Gate](references/approval-gates.md)，然后呈现确切提示：**“🚀 准备部署？(是 / 手动运行 / 编辑计划 / 取消)”**。这个门禁是你响应中的最后内容——等待用户的回复。

| # | 步骤 | 操作 | 参考 |
|---|------|--------|-----------|
| 1 | **会话检查 + Azure 登录** | 创建/恢复会话，验证 Azure CLI 认证，解析订阅+用户身份 | ⛔ **你必须阅读 [session-protocol.md](references/session-protocol.md)** |
| 2 | **范围分诊** | 检查 azd 标记，分诊问题。空工作区或仅代码（无基础设施）→ 直接进入步骤 3。 | ⛔ 阅读 [intent-gathering.md](references/intent-gathering.md) § 范围分诊 |
| 3 | **前置条件扫描** | ⛔ 如果 `completedPhases` 包含 `"prereq"` 则跳过。否则：调用 `{"skill": "azure-app-onboard-prereq"}`。写入 `prereq-output.json`，更新 `context.json`。**如果：** `overallHealth: "blocked"` 或 `routeToSkill` 设置。 | |
| 4 | **收集意图** | 呈现前置条件结果，确认堆栈+Azure 服务，询问剩余问题。 | ⛔ 阅读 [intent-gathering.md](references/intent-gathering.md) § 前置条件返回后 |
| 5 | **规划架构** | 写入 `prepare-plan.json`。 | ⛔ **你必须阅读 [prepare/SKILL.md](prepare/SKILL.md)** |
| 6 | **框架搭建门禁** | 在生成任何文件之前向用户显示计划以供批准。 | ⛔ 阅读 [approval-gates.md](references/approval-gates.md) § 框架搭建门禁 |
| 7 | **框架搭建** | 生成 IaC，自我审查。写入 `scaffold-manifest.json`。更新 `context.json`。 | ⛔ **你必须阅读 [scaffold/SKILL.md](scaffold/SKILL.md)** |
| 8 | **部署门禁** | 显示验证摘要。⛔ 批准后：首先阅读 deploy-checklist.md → deploy/SKILL.md。绝不 `{"skill": "azure-deploy"}`。 | ⛔ 阅读 [approval-gates.md](references/approval-gates.md) § 部署门禁 |
| 9 | **部署** | 执行 IaC，健康检查。写入 `deploy-result.json`。 | ⛔ **你必须阅读 [deploy/SKILL.md](deploy/SKILL.md)** |
| 10 | **交接** | 显示部署身份，清理命令，下一步操作。 | ⛔ **你必须阅读 [`handoff-protocol.md`](references/handoff-protocol.md)** |

## 错误处理

| 错误 | 补救措施 |
|-------|-------------|
| 阶段失败 | 停止，报告阶段+错误。用户决定：重试、跳过、中止。 |
| MCP 服务器不可用 | 跳过受影响的检查，在 `costEstimate.assumptions[]` 和每个审批门禁中添加免责声明。 |
| 缺少 RBAC | 报告所需角色+ `az role assignment` 命令。 |

> **共享参考：** [MCP 工具](references/mcp-tool-reference.md)（跨阶段工具参数） | [IaC 资源](references/iac-resources.md)（用于故障排除的 Azure 资源文档）
