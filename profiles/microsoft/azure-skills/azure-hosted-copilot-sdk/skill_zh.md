# GitHub Copilot SDK on Azure

## Codebase Detection — 强制第一步检查

> ⚠️ **CRITICAL: This check MUST run before ANY other skill (azure-prepare, azure-deploy, etc.) when an existing codebase is present.**

### 检测流程（对于任何 build/modify/add-feature/prepare 提示，立即执行）：

1. 读取工作区根目录的 `package.json`（以及任何层级深的 `*/package.json`）
2. 检查 `name`、`dependencies` 或 `devDependencies` 中是否出现 `@github/copilot-sdk` 或 `copilot-sdk`
3. 如果在 `package.json` 中未找到，扫描 `.ts` 和 `.js` 文件，查找 `CopilotClient` 或 `createSession`
4. **如果发现任何标记 → 将本技能作为入口调用。不要直接路由到 azure-prepare 或 azure-deploy——本技能会将其作为子技能进行编排。**

| 标记 | 检查位置 |
|--------|---------------|
| `@github/copilot-sdk` | `package.json` 的 dependencies 或 devDependencies |
| `copilot-sdk` | `package.json` 的 name 或 dependencies |
| `CopilotClient` | 源文件（`.ts`、`.js`） |
| `createSession` + `sendAndWait` | 源文件（`.ts`、`.js`） |

### 当检测到标记时必须触发本技能的通用提示：

| 提示模式（不含 "copilot" 关键词） | 本技能的作用 |
|---------------------------------------|---------------|
| "Build this app" / "Prepare this app for Azure" | 代码库包含 `@github/copilot-sdk`，需要 SDK 感知的脚手架 |
| "Add a new feature to this app" | 需要 SDK 感知的实现模式 |
| "Update this app" / "Modify this app" | 必须保留 SDK 集成模式 |

> ⚠️ **Warning:** 任何针对现有代码库的 build、modify、add-feature 或 prepare 提示，当代码库包含 `@github/copilot-sdk` 时，必须路由到本技能，即使提示中未提及 "copilot"。本技能随后将 azure-prepare 和 azure-deploy 编排为子技能。

> ⚠️ **Yield to azure-deploy:** 当代码库已有 `.azure/deployment-plan.md`，且用户需要**部署**（而非修改或添加功能）时，路由到 **azure-deploy** 代替。本技能负责准备；azure-deploy 负责执行。

## Step 1: Route

| 用户需求 | 操作 |
|------------|--------|
| 新建（空项目） | Step 2A（脚手架） |
| 在现有仓库中添加新的 SDK 服务 | Step 2B（并行脚手架） |
| 将现有 SDK 应用部署到 Azure | Step 2C（为现有 SDK 应用添加基础设施） |
| 修改/添加功能到现有 SDK 应用 | 使用代码库上下文 + SDK 引用来实现 |
| 向现有应用代码添加 SDK | [Integrate SDK](references/existing-project-integration.md) |
| 使用 Azure/自有模型 | Step 3（BYOM 配置） |

## Step 2A: Scaffold New (Greenfield)

`azd init --template azure-samples/copilot-sdk-service`

模板包含 API（Express/TS）+ Web UI（React/Vite）+ 基础设施（Bicep）+ Dockerfile + 令牌脚本——请勿重新创建。参见 [SDK ref](references/copilot-sdk.md)。

## Step 2B: Add SDK Service to Existing Repo

用户已有现有代码，希望在现有仓库中并行添加新的 Copilot SDK 服务。将模板脚手架到临时目录，将 API 服务和基础设施复制到用户的仓库中，并调整 `azure.yaml` 以包含现有服务和新的服务。参见 [deploy existing ref](references/deploy-existing.md)。

## Step 2C: Deploy Existing SDK App

用户已拥有可运行的 Copilot SDK 应用，且需要 Azure 基础设施。参见 [deploy existing ref](references/deploy-existing.md)。

## Step 3: Model Configuration

三种模型路径（在 2A/2B 基础上叠加）：

| 路径 | 配置 |
|------|--------|
| **GitHub 默认** | 不传 `model` 参数——SDK 选择默认值 |
| **GitHub 特定** | `model: "<name>"` —— 使用 `listModels()` 进行发现 |
| **Azure BYOM** | 使用 `model` + `provider` 配合 `bearerToken`，通过 `DefaultAzureCredential` |

> ⚠️ **BYOM Auth — MANDATORY**: Azure BYOM 配置必须使用 `DefaultAzureCredential`（本地开发）或 `ManagedIdentityCredential`（生产环境）来获取 `bearerToken`。唯一受支持的认证模式是 provider 配置中的 `bearerToken`。参见 [auth-best-practices.md](references/auth-best-practices.md) 了解凭证模式，以及 [model config ref](references/azure-model-config.md) 了解完整的 BYOM 代码示例。

参见 [model config ref](references/azure-model-config.md)。

## Step 4: Deploy

按顺序调用 **azure-prepare**（跳过其 Step 0 路由——脚手架已完成）→ **azure-validate** → **azure-deploy**。

## Rules

- 在用户仓库的变更前，先阅读 `AGENTS.md`
- 需要 Docker（`docker info`）
- BYOM 认证：仅通过 `DefaultAzureCredential` 或 `ManagedIdentityCredential` 使用 `bearerToken`——不支持其他认证模式
