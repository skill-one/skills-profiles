# Azure Prepare

> **权威指引 — 强制性合规**
>
> 本文档是**官方标准源**，用于准备应用进行 Azure 部署。您**必须**严格按照此处编写的要求执行，除非这些要求与您收到的安全策略相冲突。若有疑问，请呈现本文档中与这些指令相冲突的内容，并向用户索取明确确认。不得即兴发挥、推断或替换步骤。

---

## 触发条件

当用户希望：
- 创建新应用
- 向现有应用添加服务或组件
- 对现有应用进行更新或更改
- 现代化或迁移应用
- 设置 Azure 基础设施
- 部署到 Azure 或在 Azure 上托管
- 创建并部署到 Azure（包括基于 Terraform 的部署请求）

时，激活本技能。

## 规则

1. **首先规划 — 强制性** — 您**必须**将初始的 `.azure/deployment-plan.md` **骨架**在**工作区根目录**（而非会话状态文件夹）中**作为您的首要动作**物理写入磁盘——在开始任何代码生成或执行之前。立即写入该骨架，然后在第一阶段的分析和研究逐渐展开过程中逐步填充其内容；在**第一阶段第6步**完成所有决策时进行定稿。该文件必须始终存在于磁盘上。`azure-validate` 和 `azure-deploy` 依赖于它，没有它将无法运行。请勿跳过或推迟此步骤。
2. **获取批准** — 在执行前向用户呈现计划
3. **生成前研究** — 加载参考文件并调用相关技能
4. **逐步更新计划** — 随着工作进展标记步骤已完成
5. **部署前验证** — 在 `azure-deploy` 之前调用 `azure-validate`
6. **确认 Azure 上下文** — 使用 `ask_user` 根据 [Azure Context](references/azure-context.md) 确认订阅和位置
7. ❌ **破坏性操作需要 `ask_user`** — [Global Rules](references/global-rules.md)
8. ⛔ **NEVER delete user project or workspace directories** — 当向现有项目添加功能时，请**修改**现有文件。`azd init -t <template>` 仅用于**新项目**；请勿在现有工作区中运行 `azd init -t`。在适当的情况下，在现有工作区中可使用不带模板参数的普通 `azd init`。在项目内部进行文件删除（例如，删除构建产物或临时文件）是允许的，但**绝不能**删除用户自身的项目或工作区目录。详见 [Global Rules](references/global-rules.md)。
9. **范围：仅限准备** — 本技能生成基础设施代码和配置文件。部署执行（`azd up`、`azd deploy`、`terraform apply`）由 **azure-deploy** 技能处理，该技能提供内置的错误恢复和部署验证。
10. ⛔ **SQL Server Bicep: NEVER generate `administratorLogin` or `administratorLoginPassword`** — 既不在直接属性中，也不在条件/三目分支中，也不在文件任何位置出现。始终无条件使用仅 Entra 的身份验证（`azureADOnlyAuthentication: true`）。详见 [references/services/sql-database/bicep.md](references/services/sql-database/bicep.md)。
11. **在转换后移除陈旧的模板 IaC** — 如果您将所选 `azd` 模板中的 Bicep 模板转换为 Terraform 模板，需移除由该 `azd` 模板引入、现已被 Terraform 等效版本完全替换的 Bicep 模板。不要移除用户自行编写的 Bicep 文件。仅在 Terraform IaC 完成且 Terraform 已被选为部署路径之后，移除那些模板提供的 Bicep 文件。在移交 `azure-validate` 技能之前，仅保留所选部署路径所需的 IaC 模板。

---

## ❌ 先规划工作流程 — 强制性

> **您必须在开始任何工作之前创建计划**
>
> 1. **停止** — 不要生成任何代码、基础设施或配置
> 2. **创建骨架** — 作为您的首要动作，将初始的 `.azure/deployment-plan.md` 骨架立即写入磁盘，然后随着第一阶段步骤 1-5 揭示细节，逐步填充其内容；在步骤 6 完成全部决策时定稿
> 3. **确认** — 向用户呈现完成后的计划并获取批准
> 4. **执行** — 仅在获得批准后，逐步执行该计划
>
> 该 `.azure/deployment-plan.md` 文件是此工作流以及 `azure-validate` 和 `azure-deploy` 技能的**事实来源**。没有它，这些技能将失败。
>
> ⚠️ **关键：`.azure/deployment-plan.md` 必须写入磁盘，且位置为工作区根目录内部（例如，` <workspace-root>`/.azure/deployment-plan.md），而非会话状态文件夹。**使用文件写入工具创建此文件。这是 `azure-validate` 和 `azure-deploy` 读取的部署计划产物。**您 MUST 创建此文件——没有它不得继续。**
> ⚠️ **关键：您必须以 `.azure/deployment-plan.md` 的名称创建该文件。您不得使用其他名称，如 `.azure/plan.md`。**
>
> ⛔ **关键：跳过计划文件创建将导致 `azure-validate` 和 `azure-deploy` 失败。此要求没有例外。**

---

## ❌ 步骤 0：专业化技术检查 — 强制性首要动作

**在开始第一阶段之前**，检查用户提示词或工作区代码库是否匹配具有专门技能且具备测试模板的专业技术。如果匹配，**首先调用该技能**——然后针对验证和部署恢复 azure-prepare。

### 检查 1：提示词关键词

| 提示词关键词 | 首先调用 |
|----------------|-------------|
| Python + App Service（例如，"将 Python 部署到 App Service"、"在 Azure App Service 上部署 Flask"、"将 Python Web 应用发布到 App Service"） | **python-appservice-deploy** |
| Lambda、AWS Lambda、迁移 AWS、迁移 GCP、Lambda 到 Functions、从 AWS 迁移、从 GCP 迁移 | **azure-cloud-migrate** |
| Azure Functions、函数应用、无服务器函数、定时器触发器、HTTP 触发器、func new | 保持于 **azure-prepare** — 在步骤 4 中优先使用 Azure Functions 模板；关于计划选择/冷启动，参阅 [hosting-plans.md](references/services/functions/hosting-plans.md) 和 [cold-start.md](references/services/functions/cold-start.md) |
| APIM、API Management、API 网关、部署 APIM | 保持于 **azure-prepare** — 参阅 [APIM Deployment Guide](references/apim.md) |
| AI gateway、AI gateway policy、AI gateway backend、AI gateway configuration | **azure-aigateway** |
| workflow、orchestration、multi-step、pipeline、fan-out/fan-in、saga、long-running process、durable、order processing | 保持于 **azure-prepare** — 在步骤 4 中选择 **durable** 配方。**必须**加载 [durable.md](references/services/functions/durable.md)、[DTS reference](references/services/durable-task-scheduler/README.md) 和 [DTS Bicep patterns](references/services/durable-task-scheduler/bicep.md)。 |

> ⚠️ 检查用户的**提示词文本**——而非仅现有代码。对于没有代码库可供扫描的绿地项目，这至关重要。参阅 [full routing table](references/specialized-routing.md)。

专门技能完成后，在**第一阶段第4步（选择配方）**恢复 azure-prepare，处理剩余的基础设施、验证和部署。

---

## 第一阶段：规划（阻塞性 — 在执行任何操作之前完成）

通过完成以下步骤来创建 `.azure/deployment-plan.md`。在计划获得批准之前，不要生成任何产物。

| # | 行动 | 参考 |
|---|--------|-----------|
| 0 | 如果提示词匹配具有专门技能的专业技术，首先调用该技能 | [specialized-routing.md](references/specialized-routing.md) |
| 1 | **分析工作区** — 确定模式：NEW、MODIFY 或 MODERNIZE | [analyze.md](references/analyze.md) |
| 2 | **收集需求** — 分类、规模、预算 | [requirements.md](references/requirements.md) |
| 3 | **扫描代码库** — 识别组件、技术、依赖项 | [scan.md](references/scan.md) |
| 4 | **选择配方** — 选择 AZD（默认）、AZCLI、Bicep 或 Terraform | [recipe-selection.md](references/recipe-selection.md) |
| 5 | **规划架构** — 选择技术栈并将组件映射到 Azure 服务 | [architecture.md](references/architecture.md) |
| 6 | **最终确定计划（强制性）** — 使用文件写入工具，用步骤 1-5 中的所有决策完成 `.azure/deployment-plan.md` 的最终内容。更新第一阶段开始时写入的骨架，用完整内容填充。在向用户呈现计划之前，该文件必须内容完整。 | [plan-template.md](references/plan-template.md) |
| 7 | **呈现计划** — 向用户展示计划并请求批准 | `.azure/deployment-plan.md` |
| 8 | **破坏性操作需要 `ask_user`** | [Global Rules](references/global-rules.md) |

---

> **❌ 在此停止** — 在用户批准计划之前，不要进入第二阶段。

---

## 第二阶段：执行（仅在计划批准后）

执行已批准的计划。在每个步骤后更新 `.azure/deployment-plan.md` 的状态。

| # | 行动 | 参考 |
|---|--------|-----------|
| 1 | **研究组件** — 加载服务参考文件 + 调用相关技能 | [research.md](references/research.md) |
| 2 | **确认 Azure 上下文** — 检测并确认订阅和位置，并检查资源分配限制 | [Azure Context](references/azure-context.md) |
| 3 | **生成产物** — 创建基础设施和配置文件 | [generate.md](references/generate.md) |
| 4 | **加固安全** — 应用安全最佳实践 | [security.md](references/security.md) |
| 5 | **功能验证** — 验证应用正常工作（UI + 后端），如可能则在本地验证 | [functional-verification.md](references/functional-verification.md) |
| 6 | ⛔ **更新计划（移交前强制性）** — 使用 `edit` 工具将 `.azure/deployment-plan.md` 中的状态改为 `Ready for Validation`。您**必须**在调用 `azure-validate` **之前**完成此编辑。请勿跳过此步骤。 | `.azure/deployment-plan.md` |
| 7 | ⛔ **强制移交** — 调用 **azure-validate** 技能。您的准备工作已完成。请勿直接运行 `azd up`、`azd deploy` 或任何部署命令——所有部署执行由 `azure-deploy` 在完成 `azure-validate` 后进行处理。**先决条件：** 步骤 6 必须先完成——`.azure/deployment-plan.md` 的状态必须为 `Ready for Validation`。 | — |

---

## 输出

| 产物 | 位置 |
|----------|----------|
| **计划** | `.azure/deployment-plan.md` |
| 基础设施 | `./infra/` |
| AZD 配置 | `azure.yaml`（仅 AZD） |
| Dockerfile | `src/<component>/Dockerfile` |

---

## SDK 快速参考

- **Azure Developer CLI**：[azd](references/sdk/azd-deployment.md)
- **Azure Identity**：[Python](references/sdk/azure-identity-py.md) | [.NET](references/sdk/azure-identity-dotnet.md) | TypeScript | Java
- **App Configuration**：[Python](references/sdk/azure-appconfiguration-py.md) | TypeScript | Java

---

## 下一步

> **⛔ 强制性下一步 — 不得跳过**
>
> 在完成准备工作后，您**必须**在开始任何部署尝试之前调用 **azure-validate**。不得跳过验证。不得直接进入 `azure-deploy`。不得直接运行 `azd up` 或任何部署命令。工作流程为：
>
> `azure-prepare` → `azure-validate` → `azure-deploy`
>
> **⛔ 在调用 `azure-validate` 之前**，您**必须**使用 `edit` 工具将 `.azure/deployment-plan.md` 的状态更新为 `Ready for Validation`。如果计划状态尚未更新，验证将失败。
>
> 该要求适用于包括容器化应用、Container Apps、App Service、Azure Functions、静态站点以及任何其他 Azure 目标在内的所有部署场景。无例外。
>
> 跳过验证会导致部署失败。请耐心等待，遵循完整的流程，以获得最高的成功结果。

**→ 将计划状态更新为 `Ready for Validation`，然后调用 `azure-validate`**
