# Azure 应用引导前置条件 — 仓库评估

在基础设施规划之前，评估用户的仓库以检查构建健康度、应用完整性和 Azure 部署可行性。生成针对每个组件的判定结果（通过/警告/失败），供下游阶段使用。

> **协调器关系：** 由 `azure-app-onboard` 在第 3 步调用，或用于代码就绪检查时独立运行。当由协调器调用时，在写入工件后返回控制权给 `azure-app-onboard` — 不要直接调用下游阶段。

应用引导流程中的第 1 步（共 4 步）。会话：`.copilot-azure/sessions/{session-id}/`。读取 `context.json`。写入 `components[]`、`repo{}`、`detectedInfra[]`。生成 `prereq-output.json`。架构：`[prereq-schemas.ts](references/prereq-schemas.ts)` — `PrereqOutput`、`BuildRequirements`。支持直接入口。

## 不应使用的情况

| 信号 | 重定向 |
|------|----------|
| 验证基础设施 (Bicep/TF/azure.yaml) | **azure-validate** |
| 生成 IaC | **azure-prepare** |
| 端到端从想法到生产 | **azure-app-onboard** |
| 运行 `azd up` 或部署 | **azure-deploy** |

## 规则

> ⛔ **绝对禁止 — `npm install`、`npm test`、`npx jest`、`pytest` 以及所有安装/构建/测试命令都绝对禁止。**
> 在前置条件阶段，在任何情况下都不得运行 `npm install`、`npm test`、`npx jest`、`pip install`、`pytest`、`dotnet build`、`dotnet restore`、`dotnet test`、`go mod download`、`cargo build` 或任何包管理器的安装、构建或测试命令。不要运行测试套件来验证代码 — 静态检查测试配置文件即可。前置条件阶段是只读评估 + 静态验证。
> **唯一例外 — 两个受认可的环境，均需用户同意：** (a) 代理在迁移/修复过程中**修改**的代码（见 [remediation-protocol.md](references/remediation-protocol.md) 第 6 步），或 (b) 代理从零开始**编写**的代码（见 [zero-code-path.md](references/zero-code-path.md)）。在任何情况下，安装/构建/测试运行都**仅**通过用户确认的构建验证门（[build-check.md](references/build-check.md) 第 3 步），在用户回答特定命令的同意提示后进行。一般先前的同意无效。

1. ⛔ **完整流程（步骤 1–8），无一例外。** 所有提示直接进入步骤 1。将具体问题作为发现的一部分回答（步骤 5），而不是在此之前。
2. ⛔ **不使用子代理进行评估。** 三轴评估是内联的。**例外**：零代码路径脚手架（步骤 2）。
3. 代码/破坏性修改需要 `ask_user`。最多 3 个问题即可获得结果。直接入口：不要重复协调器的意图问题。

## MCP 工具

| 工具 | 目的 |
|------|---------|
| `mcp_azure_mcp_get_azure_bestpractices` | 验证检测到的堆栈模式是否符合 Azure 最佳实践 |
| `mcp_azure_mcp_extension_cli_install` | 检查/安装所需的 CLI 工具 (az, azd, func) |

## 工作流

### 第 1 步：会话检查

**协调器入口：** 会话存在 — 读取 `context.json`，然后进入第 2 步。

**直接入口：** 检查 `.copilot-azure/sessions/active-session.json`：
- **存在** → ⛔ 读取 [session-protocol.md](references/session-protocol.md) 以获取恢复/全新门。在用户回答之前不要继续。
- **缺失** → 创建会话：生成 UUID，`New-Item -ItemType Directory -Path ".copilot-azure/sessions/{uuid}" -Force`，通过 `create` 工具写入 `context.json` + `active-session.json`。

然后：`az account show` → 将 `{id, name, tenantId}` 合并到 `context.json.azure`。⛔ 会话必须在磁盘上存在之前进行任何扫描。

### 第 2 步：扫描工作区

扫描项目文件。检测组件、`repo{}`、`detectedInfra[]`、`detectedServices[]`。分类 Terraform 提供者。检查 CLI 可用性。堆栈检测冲突：用户明确声明优先（写入 `context.json`，将扫描标记为覆盖）；仅扫描 → 确认用户；多个堆栈 → 显示所有并询问（见 [component-mapping.md](references/component-mapping.md)）；无代码 → [zero-code-path.md](references/zero-code-path.md)。

> 如果没有项目文件，没有 Dockerfile，并且没有 index.html → ⛔ 读取 [zero-code-path.md](references/zero-code-path.md)。

> ⛔ **云 SDK 早期门。** Grep 查找 `aws-sdk|@aws-sdk|boto3|google-cloud|@google-cloud|firebase`。如果找到功能依赖项 → 读取 [cloud-sdk-migration.md](references/cloud-sdk-migration.md)，然后 `ask_user`：**"重定向到 Azure 云迁移"**（设置 `routeToSkill: "azure-cloud-migrate"`) · **"无论如何继续评估"**（完成就绪评估 + SDK→Azure 映射，然后在第 8 步停止 — 直到依赖项被替换才进行规划）· **"取消"**。

### 第 3 步：组件级评估

| 子步骤 | 操作 | 参考 |
|----------|--------|-----------|
| 3.1 | **构建检查** | ⛔ **你必须读取 [build-check.md](references/build-check.md)** |
| 3.2 | **完整性检查** | ⛔ **你必须读取 [completeness-check.md](references/completeness-check.md)** |
| 3.3 | **可部署性检查** | ⛔ **你必须读取 [deployability-check.md](references/deployability-check.md)** |
| 3.3a | **组件映射**（条件性） | 仅当找到多个项目清单（单体仓库）时才读取 [component-mapping.md](references/component-mapping.md) |

评估后为每个组件填充 `buildRequirements`。判定传播、层级规则和 f1Viable 聚合在 [readiness-gate.md](references/readiness-gate.md) 和各个检查参考中。

### 第 4 步：写入工件 + 就绪门

⛔ 验证磁盘上是否存在 `context.json`。读取 [readiness-gate.md](references/readiness-gate.md)（判定、层级、批量后批准、快速通道）然后 [prereq-artifacts.md](references/prereq-artifacts.md)（写入程序、架构）。

### 第 5 步：展示发现

按 [readiness-gate.md § 展示发现](references/readiness-gate.md) — 在继续之前按严重程度分组显示判定。

### 第 6 步：修复（条件性）

⛔ **你必须读取 [remediation-protocol.md](references/remediation-protocol.md)** 如果存在任何 ❌ 失败判定、🔧 推荐修复或 ⚠️ 警告且 `fixPhase: "prereq"` 存在。包含修复循环、静态验证、重新评估要求、修复后工件更新和构建验证同意门。如果所有判定都是 ✅ 通过或 ⚠️ 警告且没有 `fixPhase: "prereq"`，跳转到第 7 步。

### 第 7 步：写入最终状态

`completedPhases` 已经有 `"prereq"` + `currentPhase: null`（来自第 4 步）。然后：

> ⛔ **写入 `lastScanCommit`。** 运行 `git rev-parse HEAD` 并将完整的 40 字符 SHA 存储为 `context.json.repo.lastScanCommit`。必需 — 在第 1 步中与恢复时的 HEAD 比较以检测更改。

### 第 8 步：路由

⛔ **强制执行 — 不要跳过此步骤。**

> **路由字段：** 所有路由将 `routeToSkill` 和 `routeReason` 写入 `context.json`。

> **修复后上下文：** 如果第 6 步运行，在路由提示前引导： "修复完成 — 修复了 {N} 个问题，您的应用现在 {overallHealth}。"

> ⛔ **从上到下评估行 — 第一个匹配项生效。**

| # | 条件 | 操作 |
|---|-----------|--------|
| 1 | `routeToSkill` 设置（任何条目） | `ask_user`： "重定向到 {routeToSkill}" / "不现在"。⛔ 流程停止 — 不要继续到架构规划。 |
| 2 | `cloudSdkFindings[]` 非空（用户选择 "无论如何继续评估"） | 展示云-SDK→Azure 交换映射作为 🔶 阻塞项，然后 `ask_user` 使用此确切提示：**"🔶 云 SDK 迁移需要 — 这些依赖项必须在应用可以部署到 Azure 之前被交换。 (重定向到 azure-cloud-migrate / 停止 — 手动交换并重新运行)"** — 重定向设置 `routeToSkill: "azure-cloud-migrate"`，停止。⛔ 流程停止 — 不要继续到架构规划，并且不要提供 "继续到准备" 选项；应用直到依赖项交换才能部署。 |
| 3 | 协调器 + 无 `routeToSkill` | 告诉用户： "✅ 您的应用已评估并准备就绪 — 让我们规划您的 Azure 部署。" 然后调用 `azure-app-onboard`。⛔ 不要停止，不要等待用户输入，不要描述内部交接。用户已经在范围筛选时同意了完整流程。 |
| 4 | 直接 + 就绪/就绪带警告 + 无 Azure 基础设施 | `ask_user`： "部署到 Azure (完整流程)" → 调用 `azure-app-onboard` / "不现在" |
| 5 | 直接 + 就绪/就绪带警告 + 现有 Azure 基础设施 | `ask_user`： "全新开始" → 调用 `azure-app-onboard` / "使用现有基础设施" → 调用 `azure-prepare` / "不现在" |
| 6 | 直接 + 被阻塞 | 报告阻塞摘要 + "修复并重新运行。" |

严重程度层级（🛑🔶❌🔧⚠️✅）在 [readiness-gate.md](references/readiness-gate.md) 中定义。

## 输出

| 工件 | 位置 | 消费者 |
|------|----------|----------|
| 会话上下文 | `context.json` → `components[]`、`repo{}`、`detectedInfra[]`、`detectedServices[]` | 所有下游阶段 |
| 前置条件输出 | `prereq-output.json` | 准备阶段（通过 `azure-app-onboard`） |
| 就绪报告 | `.copilot-azure/sessions/{uuid}/readiness-report.md` | 用户（离线参考） |
