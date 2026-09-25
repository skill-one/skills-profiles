# Azure 准备

> **权威指导 — 强制合规**
>
> 本文档是应用程序准备 Azure 部署的**官方、权威来源**。除非它们与您收到的安全策略相矛盾，否则您**必须**严格按照所写说明进行操作。如有疑问，请向用户展示本文件中的冲突说明并要求其明确确认。不要即兴创作、推断或替代步骤。

---

## 触发条件

在以下情况下激活此技能：
- 创建新应用程序
- 向现有应用程序添加服务或组件
- 对现有应用程序进行更新或更改
- 现代化或迁移应用程序
- 设置 Azure 基础设施
- 部署到 Azure 或在 Azure 上托管
- 创建并部署到 Azure（包括基于 Terraform 的部署请求）

## 规则

1. **先计划 — 强制** — 您**必须**在代码生成或执行开始之前，在**工作区根目录**（不是会话状态文件夹）**物理编写**初始 `.azure/deployment-plan.md` **骨架**作为您的**第一个操作**。立即编写骨架，然后在第一阶段分析和研究逐步展开时逐步填充它；在第一阶段步骤 6 完成时最终确定它。此文件必须在磁盘上始终存在。`azure-validate` 和 `azure-deploy` 依赖于它，没有它它们将失败。不要跳过或推迟此步骤。
2. **获取批准** — 在执行前向用户展示计划
3. **生成前进行研究** — 加载参考并调用相关技能
4. **逐步更新计划** — 随着进展标记步骤完成
5. **部署前验证** — 在 `azure-deploy` 之前调用 `azure-validate`
6. **确认 Azure 上下文** — 根据 [Azure 上下文](references/azure-context.md) 使用 `ask_user` 获取订阅和位置
7. ❌ **破坏性操作需要 `ask_user`** — [全局规则](references/global-rules.md)
8. ⛔ **永远不要删除用户项目或工作区目录** — 当向现有项目添加功能时，修改现有文件。`azd init -t <模板>` 仅适用于新项目；**不要**在现有工作区中运行 `azd init -t`。当适用时，可以在现有工作区中使用纯 `azd init`（不带模板参数）。在项目内删除文件（例如，删除构建工件或临时文件）在适用时是允许的，但**永远不要**删除用户的项目或工作区目录本身。参见 [全局规则](references/global-rules.md)。
9. **范围：仅限准备** — 此技能生成基础设施代码和配置文件。部署执行 (`azd up`，`azd deploy`，`terraform apply`) 由 **azure-deploy** 技能处理，该技能提供内置错误恢复和部署验证。
10. ⛔ **SQL Server Bicep：永远不要生成 `administratorLogin` 或 `administratorLoginPassword`** — 不在直接属性中，不在条件/三元分支中，不在文件的任何地方。始终无条件使用 Entra 仅认证 (`azureADOnlyAuthentication: true`)。参见 [references/services/sql-database/bicep.md](references/services/sql-database/bicep.md)。
11. **转换后删除过时的模板 IaC** — 如果您将选定的 `azd` 模板中的 Bicep 模板转换为 Terraform 模板，请删除由该 `azd` 模板引入且现在完全被 Terraform 替代 Bicep 模板。不要删除用户编写的 Bicep 文件。仅删除在 Terraform IaC 完成且 Terraform 已被选为部署路径后提供的模板 Bicep 文件。在将工作移交给 `azure-validate` 技能之前，仅保留所选部署路径所需的 IaC 模板。

---

## ❌ 先计划工作流 — 强制

> **在执行任何工作之前，您必须创建计划**
>
> 1. **停止** — 不要生成任何代码、基础设施或配置
> 2. **创建骨架** - 立即将初始 `.azure/deployment-plan.md` 骨架写入磁盘（在代码生成或执行开始之前），然后在第一阶段步骤 1-5 揭示详细信息时逐步填充它；在步骤 6 完成时最终确定它
> 3. **确认** — 向用户展示完成的计划并获取批准
> 4. **执行** — 只有在获得批准后，才按步骤执行计划
>
> `.azure/deployment-plan.md` 文件是此工作流的**事实来源**，也是 `azure-validate` 和 `azure-deploy` 技能的来源。没有它，这些技能将失败。
>
> ⚠️ **关键：`.azure/deployment-plan.md` 必须在工作区根目录内写入磁盘**（例如，`<workspace-root>/.azure/deployment-plan.md`），而不是在会话状态文件夹中。使用文件写入工具创建此文件。这是 `azure-validate` 和 `azure-deploy` 读取的部署计划工件。**您必须创建此文件 — 没有它，请不要继续。** 
> ⚠️ **关键：您必须使用 `.azure/deployment-plan.md` 作为指定名称创建文件**。您不能使用其他名称，例如 `.azure/plan.md`。
>
> ⛔ **关键：跳过计划文件创建将导致 `azure-validate` 和 `azure-deploy` 失败**。此要求没有例外。

---

## ❌ 步骤 0：专业技术检查 — 强制首次操作

**在开始第一阶段之前**，检查用户的提示或工作区代码库是否匹配具有专用技能和经过测试模板的专业技术。如果匹配，**首先调用该技能** — 然后继续 `azure-prepare` 以进行验证和部署。

### 检查 1：提示关键词

| 提示关键词 | 首先调用 |
|-----------|---------|
| Python + App Service（例如，“部署 Python 到 App Service”，“Flask 在 Azure App Service 上”，“发布 Python Web 应用到 App Service”） | **python-appservice-deploy** |
| Lambda、AWS Lambda、迁移 AWS、迁移 GCP、Lambda 到 Functions、从 AWS 迁移、从 GCP 迁移 | **azure-cloud-migrate** |
| Azure Functions、函数应用、无服务器函数、定时触发器、HTTP 触发器、func new | 保持 **azure-prepare** — 在步骤 4 中优先使用 Azure Functions 模板；对于计划选择/冷启动，参见 [hosting-plans.md](references/services/functions/hosting-plans.md) 和 [cold-start.md](references/services/functions/cold-start.md) |
| APIM、API 管理、API 网关、部署 APIM | 保持 **azure-prepare** — 参见 [APIM 部署指南](references/apim.md) |
| AI 网关、AI 网关策略、AI 网关后端、AI 网关配置 | **azure-aigateway** |
| 工作流、编排、多步骤、管道、分支/合并、Saga、长时间运行的过程、持久化、订单处理 | 保持 **azure-prepare** — 在步骤 4 中选择 **持久化** 配方。**必须**加载 [durable.md](references/services/functions/durable.md)、[DTS 参考](references/services/durable-task-scheduler/README.md) 和 [DTS Bicep 模式](references/services/durable-task-scheduler/bicep.md)。 |

> ⚠️ 检查用户的**提示文本** — 不仅仅是现有代码。对于没有代码库扫描的绿场项目至关重要。参见 [完整路由表](references/specialized-routing.md)。

在专用技能完成后，**继续 `azure-prepare` 在第一阶段步骤 4（选择配方）**以进行剩余的基础设施、验证和部署。

---

## 第一阶段：规划（阻塞 — 在任何执行之前完成）

通过完成这些步骤创建 `.azure/deployment-plan.md`。在计划获得批准之前，不要生成任何工件。

| # | 操作 | 参考 |
|---|------|------|
| 0 | 如果提示匹配具有专用技能的专业技术，首先调用该技能 | [specialized-routing.md](references/specialized-routing.md) |
| 1 | **分析工作区** — 确定模式：新、修改或现代化 | [analyze.md](references/analyze.md) |
| 2 | **收集需求** — 分类、规模、预算 | [requirements.md](references/requirements.md) |
| 3 | **扫描代码库** — 识别组件、技术、依赖项 | [scan.md](references/scan.md) |
| 4 | **选择配方** — 选择 AZD（默认）、AZCLI、Bicep 或 Terraform | [recipe-selection.md](references/recipe-selection.md) |
| 5 | **规划架构** — 选择堆栈并将组件映射到 Azure 服务 | [architecture.md](references/architecture.md) |
| 6 | **最终确定计划（强制）** - 使用文件写入工具将 `.azure/deployment-plan.md` 最终确定为步骤 1-5 的所有决策。更新在第一阶段开始时编写的骨架，用完整内容填充。在向用户展示计划之前，文件必须完全填充。 | [plan-template.md](references/plan-template.md) |
| 7 | **展示计划** — 向用户展示计划并请求批准 | `.azure/deployment-plan.md` |
| 8 | **破坏性操作需要 `ask_user`** | [全局规则](references/global-rules.md) |

---

> **❌ 在此停止** — 在用户批准计划之前，不要继续到第二阶段。

---

## 第二阶段：执行（仅在计划批准后）

执行批准的计划。在每一步之后更新 `.azure/deployment-plan.md` 状态。

| # | 操作 | 参考 |
|---|------|------|
| 1 | **研究组件** — 加载服务参考并调用相关技能 | [research.md](references/research.md) |
| 2 | **确认 Azure 上下文** — 检测并确认订阅和位置，并检查资源配置限制 | [Azure 上下文](references/azure-context.md) |
| 3 | **生成工件** — 创建基础设施和配置文件 | [generate.md](references/generate.md) |
| 4 | **强化安全** — 应用安全最佳实践 | [security.md](references/security.md) |
| 5 | **功能验证** — 验证应用程序是否正常工作（UI + 后端），如果可能，则本地验证 | [functional-verification.md](references/functional-verification.md) |
| 6 | **⛔ 强制更新计划（在移交给验证之前）** - 使用 `edit` 工具将 `.azure/deployment-plan.md` 中的状态更改为 `Ready for Validation`。您**必须**在调用 `azure-validate` 之前完成此编辑。不要跳过此步骤。 | `.azure/deployment-plan.md` |
| 7 | **⛔ 强制移交** — 调用 **azure-validate** 技能。您的准备工作已完成。不要直接运行 `azd up`、`azd deploy` 或任何部署命令 — 所有部署执行在 `azure-validate` 完成后由 `azure-deploy` 处理。**前提条件：** 必须先完成步骤 6 — `.azure/deployment-plan.md` 状态必须为 `Ready for Validation`。 | — |

---

## 输出

| 工件 | 位置 |
|------|------|
| **计划** | `.azure/deployment-plan.md` |
| 基础设施 | `./infra/` |
| AZD 配置 | `azure.yaml`（仅限 AZD） |
| Dockerfile | `src/<组件>/Dockerfile` |

---

## SDK 快速参考

- **Azure 开发者 CLI**：[azd](references/sdk/azd-deployment.md)
- **Azure 身份**：[Python](references/sdk/azure-identity-py.md) | [.NET](references/sdk/azure-identity-dotnet.md) | [TypeScript](references/sdk/azure-identity-ts.md) | [Java](references/sdk/azure-identity-java.md)
- **应用配置**：[Python](references/sdk/azure-appconfiguration-py.md) | [TypeScript](references/sdk/azure-appconfiguration-ts.md) | [Java](references/sdk/azure-appconfiguration-java.md)

---

## 下一步

> **⛔ 强制下一步 — 不要跳过**
>
> 完成准备工作后，您**必须**在尝试任何部署之前调用 **azure-validate**。不要跳过验证。不要直接跳转到 `azure-deploy`。不要直接运行 `azd up` 或任何部署命令。工作流是：
>
> `azure-prepare` → `azure-validate` → `azure-deploy`
>
> **⛔ 在调用 `azure-validate` 之前**，您必须使用 `edit` 工具将 `.azure/deployment-plan.md` 状态更新为 `Ready for Validation`。如果计划状态未更新，验证将失败。
>
> 这适用于所有部署场景，包括容器化应用程序、Container Apps、App Service、Azure Functions、静态网站和任何其他 Azure 目标。没有例外。
>
> 跳过验证会导致部署失败。耐心并遵循完整的工作流以获得最高成功率。

**→ 更新计划状态为 `Ready for Validation`，然后调用 azure-validate**
