# Azure App Onboard 前置要求 — 仓库评估

对用户的仓库进行构建健康度、应用完整性及 Azure 部署可行性的评估——在基础设施规划之前。生成每组件的判定（PASS/WARN/FAIL），供下游阶段使用。

> **编排器关系：** 由 `azure-app-onboard` 在第 3 步调用，或独立用于代码就绪性检查。当由编排器调用时，写入产物后应将控制权交还 `azure-app-onboard`，切勿直接调用下游阶段。

AppOnboard 流水线第 1 / 4 阶段。会话：`.copilot-azure/sessions/{session-id}/`。读取 `context.json`，写入 `components[]`、`repo{}`、`detectedInfra[]`，生成 `prereq-output.json`。Schema 见 [`prereq-schemas.ts`](references/prereq-schemas.ts) — `PrereqOutput`、`BuildRequirements`。支持直接调用。

## 不宜使用场景

| 信号 | 重定向至 |
|--------|----------|
| 验证基础设施（Bicep/TF/azure.yaml） | **azure-validate** |
| 生成 IaC | **azure-prepare** |
| 端到端从想法到生产 | **azure-app-onboard** |
| 执行 `azd up` 或部署 | **azure-deploy** |

## 规则

> ⛔ **绝对禁止 — `npm install`、`npm test`、`npx jest`、`pytest` 及所有安装/构建/测试命令一律不允许使用。**
> 在任何情况下都不得运行 `npm install`、`npm test`、`npx jest`、`pip install`、`pytest`、`dotnet build`、`dotnet restore`、`dotnet test`、`go mod download`、`cargo build`，或任何包管理器的安装/构建/测试命令。前置阶段为只读评估 + 仅静态验证。不得运行测试套件以验证代码——改为静态检查测试配置文件。
>
> **唯一例外——仅两种经许可的上下文，均需经用户同意：** (a) 迁移/修复期间**由 Agent 修改**的代码（见 [remediation-protocol.md](references/remediation-protocol.md) 第 6 步），或 (b) 在零代码路径上**从零编写**的代码（见 [zero-code-path.md](references/zero-code-path.md)）。无论哪种情况，安装/构建/测试仅在用户通过经确认的构建验证门槛 ([build-check.md](references/build-check.md) 第 3 步) 后、用户针对具体命令回答相应同意提示后方可执行。一般性先前同意不计入。

1. ⛔ **完整流水线（第 1–8 步），无例外。** 所有提示直接进入第 1 步。在（第 5 步）作为发现结果的一部分回答问题，而非先于问题提出。
2. ⛔ **评估阶段不得使用子 Agent。** 三维评估在内部进行。**例外**：零代码路径的脚手架搭建（第 2 步）。
3. 代码/破坏性修改需调用 `ask_user`。结果出具前最多提问 3 个问题。直接调用：不重复编排器的意图问题。

## MCP 工具

| 工具 | 用途 |
|------|---------|
| `mcp_azure_mcp_get_azure_bestpractices` | 校验检测到的技术栈模式是否符合 Azure 最佳实践 |
| `mcp_azure_mcp_extension_cli_install` | 检查/安装所需 CLI 工具（az、azd、func） |

## 工作流程

### 第 1 步：会话检查

**编排器入口：** 会话存在——读取 `context.json`，继续进入第 2 步。

**直接调用：** 检查 `.copilot-azure/sessions/active-session.json`：
- **存在** → ⛔ 阅读 [session-protocol.md](references/session-protocol.md) 以确认续传/新建门控。须等待用户回答后方可继续。
- **缺失** → 创建会话：生成 UUID，执行 `New-Item -ItemType Directory -Path ".copilot-azure/sessions/{uuid}" -Force`，通过 `create` 工具写入 `context.json` 与 `active-session.json`。

随后：执行 `az account show` → 将 `{id, name, tenantId}` 合并至 `context.json.azure`。⛔ 任何扫描之前，会话必须已存在于磁盘上。

### 第 2 步：扫描工作区

扫描项目文件，检测组件、`repo{}`、`detectedInfra[]`、`detectedServices[]`。分类 Terraform 提供商。检查 CLI 可用性。技术栈检测冲突：用户明确表述优先（写入 `context.json`，将扫描标记为覆盖）；仅扫描结果 → 与用户确认；存在多个技术栈 → 展示全部并提问（参见 [component-mapping.md](references/component-mapping.md)）；无代码 → 参见 [zero-code-path.md](references/zero-code-path.md)。

> 若不存在项目文件、Dockerfile 和 index.html → ⛔ 阅读 [zero-code-path.md](references/zero-code-path.md)。

> ⛔ **Cloud SDK 前置门控。** 检索 `aws-sdk`、`@aws-sdk`、`boto3`、`google-cloud`、`@google-cloud`、`firebase`。若发现功能依赖 → 阅读 [cloud-sdk-migration.md](references/cloud-sdk-migration.md)，随后调用 `ask_user`：**"Redirect to Azure Cloud Migrate"**（设置 `routeToSkill: "azure-cloud-migrate"`） · **"Continue evaluation anyway"**（完成就绪性评估 + SDK→Azure 映射，然后在第 8 步停止——依赖替换前不生成计划） · **"Cancel"**。

### 第 3 步：逐组件评估

| 子步骤 | 操作 | 参考 |
|----------|--------|-----------|
| 3.1 | **构建检查** | ⛔ **必须阅读** [build-check.md](references/build-check.md) |
| 3.2 | **完整性检查** | ⛔ **必须阅读** [completeness-check.md](references/completeness-check.md) |
| 3.3 | **可部署性检查** | ⛔ **必须阅读** [deployability-check.md](references/deployability-check.md) |
| 3.3a | **组件映射**（条件性） | 仅当发现 >1 个项目清单（monorepo）时，阅读 [component-mapping.md](references/component-mapping.md) |

评估完成后，按组件填充 `buildRequirements`。判定传播、层级规则及 f1Viable 聚合规则见 [readiness-gate.md](references/readiness-gate.md) 及各检查参考文档。

### 第 4 步：写入产物 + 就绪门控

⛔ 确认 `context.json` 已存在于磁盘。阅读 [readiness-gate.md](references/readiness-gate.md)（判定、层级、批量后审批、快速通道）以及 [prereq-artifacts.md](references/prereq-artifacts.md)（写入流程、Schema）。

### 第 5 步：呈现发现结果

根据 [readiness-gate.md § Present Findings](references/readiness-gate.md)——在继续前，按严重程度分组展示判定结果。

### 第 6 步：修复（条件性）

⛔ **必须阅读** [remediation-protocol.md](references/remediation-protocol.md)——若存在任何 ❌ FAIL 判定、🔧 建议修复，或带 `fixPhase: "prereq"` 的 ⚠️ WARN，则需阅读。文档包含修复循环、静态验证、重新评估要求、修复后产物更新以及构建验证同意门槛。若所有判定均为 ✅ PASS 或 ⚠️ WARN 且无 `fixPhase: "prereq"`，则跳过至第 7 步。

### 第 7 步：写入最终状态

`completedPhases` 已包含 `"prereq"` 以及 `currentPhase: null`（来自第 4 步）。随后：

> ⛔ **写入 `lastScanCommit`。** 执行 `git rev-parse HEAD`，并将完整的 40 字符 SHA 存储为 `context.json.repo.lastScanCommit`。为必需——第 1 步在恢复时与 HEAD 对比用于检测变更的时效性防护机制依赖此字段。

### 第 8 步：路由

⛔ **强制性——不得跳过此步骤。**

> **路由字段：** 所有路由写入将 `routeToSkill` 和 `routeReason` 至 `context.json`。

> **修复后上下文：** 若第 6 步已执行，路由提示应以 "Remediation complete — {N} issues fixed, your app is now {overallHealth}." 开头。

> ⛔ **按自上而下顺序评估行——首个匹配项生效。**

| # | 条件 | 操作 |
|---|--------|--------|
| 1 | `routeToSkill` 已设置（任意条目） | 调用 `ask_user`："Redirect to {routeToSkill}" / "Not now"。⛔ 流水线停止——不得进入架构规划。 |
| 2 | `cloudSdkFindings[]` 非空（用户选择 "Continue evaluation anyway"） | 以 🔶 阻碍项形式呈现云 SDK → Azure 替换映射，随后以以下精确提示调用 `ask_user`：**"🔶 Cloud SDK migration required — these dependencies must be swapped before this app can deploy to Azure. (Redirect to azure-cloud-migrate / Stop — swap manually and re-run)"** —— 重定向设置 `routeToSkill: "azure-cloud-migrate"`，停止则终止。⛔ 流水线停止——不得进入架构规划，且不得提供 "continue to prepare" 选项；依赖替换前应用无法部署。 |
| 3 | 编排器 + 无 `routeToSkill` | 告知用户："✅ Your app has been evaluated and is ready — let's plan your Azure deployment." 随后调用 `azure-app-onboard`。⛔ 不得停止、不得等待用户输入、不得叙述内部交接。用户在范围分级阶段已同意完整流水线。 |
| 4 | 直接调用 + `ready`/`readyWithCaveats` + 无 Azure 基础设施 | 调用 `ask_user`："Deploy to Azure (full pipeline)" → 调用 `azure-app-onboard` / "Not now" |
| 5 | 直接调用 + `ready`/`readyWithCaveats` + 已有 Azure 基础设施 | 调用 `ask_user`："Start fresh" → 调用 `azure-app-onboard` / "Use existing infra" → 调用 `azure-prepare` / "Not now" |
| 6 | 直接调用 + 被阻塞 | 报告阻碍汇总 + "Fix and re-run." |

严重程度层级（🛑🔶❌🔧⚠️✅）定义于 [readiness-gate.md](references/readiness-gate.md)。

## 输出

| 产物 | 位置 | 消费者 |
|----------|----------|----------|
| 会话上下文 | `context.json` → `components[]`、`repo{}`、`detectedInfra[]`、`detectedServices[]` | 所有下游阶段 |
| 前置输出 | `prereq-output.json` | 准备阶段（通过 `azure-app-onboard`） |
| 就绪报告 | `.copilot-azure/sessions/{uuid}/readiness-report.md` | 用户（离线参考） |
