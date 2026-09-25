# GitHub Copilot SDK 在 Azure 上的使用

## 代码库检测 — 必须首先检查

> ⚠️ **关键：当存在现有代码库时，此检查必须在任何其他技能（azure-prepare、azure-deploy 等）之前运行。**

### 检测步骤（针对任何构建/修改/添加功能/准备提示，立即运行）：

1. 读取工作区根目录中的 `package.json`（以及任何一级深度的 `*/package.json`）
2. 检查 `name`、`dependencies` 或 `devDependencies` 中是否出现 `@github/copilot-sdk` 或 `copilot-sdk`
3. 如果在 `package.json` 中未找到，扫描 `.ts` 和 `.js` 文件以查找 `CopilotClient` 或 `createSession`
4. **如果找到任何标记 → 将以此技能作为入口点调用。不要直接路由到 azure-prepare 或 azure-deploy — 此技能将它们作为子技能进行协调。**

| 标记 | 检查位置 |
|------|----------|
| `@github/copilot-sdk` | `package.json` 依赖项或 devDependencies |
| `copilot-sdk` | `package.json` 名称或依赖项 |
| `CopilotClient` | 源文件（`.ts`、`.js`） |
| `createSession` + `sendAndWait` | 源文件（`.ts`、`.js`） |

### 必须在检测到标记时触发此技能的通用提示：

| 提示模式（不包含 "copilot" 关键词） | 为什么需要此技能 |
|------------------------------------|------------------|
| "构建此应用程序" / "为 Azure 准备此应用程序" | 代码库包含 `@github/copilot-sdk` - 需要SDK感知的脚手架 |
| "为此应用程序添加新功能" | 需要SDK感知的实现模式 |
| "更新此应用程序" / "修改此应用程序" | 必须保留SDK集成模式 |

> ⚠️ **警告：** 针对包含 `@github/copilot-sdk` 的现有代码库的任何构建、修改、添加功能或准备提示，即使提示未提及 "copilot"，也必须路由到此技能。然后此技能将 azure-prepare 和 azure-deploy 作为子技能进行协调。

> ⚠️ **让位于 azure-deploy：** 当代码库已经具有 `.azure/deployment-plan.md` 且用户想要**部署**（而不是修改或添加功能）时，应路由到 **azure-deploy**。此技能处理准备工作；azure-deploy 处理执行。

## 第 1 步：路由

| 用户想要 | 操作 |
|---------|------|
| 构建（空项目） | 第 2A 步（脚手架） |
| 向现有仓库添加新的 SDK 服务 | 第 2B 步（伴随脚手架） |
| 将现有的 SDK 应用程序部署到 Azure | 第 2C 步（向现有的 SDK 应用程序添加基础设施） |
| 修改/向现有的 SDK 应用程序添加功能 | 使用代码库上下文 + SDK 引用来实现 |
| 向现有应用程序代码添加 SDK | [集成 SDK](references/existing-project-integration.md) |
| 使用 Azure/自己的模型 | 第 3 步（自带模型配置） |

## 第 2A 步：新建（绿野）

`azd init --template azure-samples/copilot-sdk-service`

模板包括 API（Express/TS）+ Web UI（React/Vite）+ 基础设施（Bicep）+ Dockerfile + 令牌脚本 — 不要重新创建。参见 [SDK 参考](references/copilot-sdk.md)。

## 第 2B 步：向现有仓库添加 SDK 服务

用户已有现有代码，并希望在旁边添加一个新的 Copilot SDK 服务。将脚手架模板到临时目录，将 API 服务 + 基础设施复制到用户的仓库中，调整 `azure.yaml` 以包含现有和新服务。参见 [部署现有参考](references/deploy-existing.md)。

## 第 2C 步：部署现有 SDK 应用程序

用户已经有一个可工作的 Copilot SDK 应用程序，并需要 Azure 基础设施。参见 [部署现有参考](references/deploy-existing.md)。

## 第 3 步：模型配置

三个模型路径（在 2A/2B 之上）：

| 路径 | 配置 |
|------|------|
| **GitHub 默认** | 无 `model` 参数 — SDK 选择默认值 |
| **GitHub 特定** | `model: "<名称>"` — 使用 `listModels()` 发现 |
| **Azure 自带模型** | `model` + `provider` 通过 `DefaultAzureCredential` 获取 `bearerToken` |

> ⚠️ **自带模型认证 — 必须执行**：Azure 自带模型配置必须使用 `DefaultAzureCredential`（本地开发）或 `ManagedIdentityCredential`（生产）来获取 `bearerToken`。唯一支持的认证模式是在提供者配置中的 `bearerToken`。参见 [认证最佳实践.md](references/auth-best-practices.md) 了解凭证模式，以及 [模型配置参考](references/azure-model-config.md) 了解完整的自带模型代码示例。

参见 [模型配置参考](references/azure-model-config.md)。

## 第 4 步：部署

按顺序调用 **azure-prepare**（跳过其第 0 步路由 — 脚手架已完成）→ **azure-validate** → **azure-deploy**。

## 规则

- 在更改之前读取用户仓库中的 `AGENTS.md`
- 需要 Docker (`docker info`)
- 自带模型认证：仅 `bearerToken` 通过 `DefaultAzureCredential` 或 `ManagedIdentityCredential` — 不支持其他认证模式
