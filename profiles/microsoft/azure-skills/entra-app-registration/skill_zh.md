## 概述

Microsoft Entra ID（以前称为 Azure Active Directory）是微软的基于云的身份和访问管理服务。应用程序注册允许应用程序安全地验证用户并访问 Azure 资源。

### 关键概念

| 概念 | 描述 |
|------|-------------|
| **应用程序注册** | 允许应用程序使用 Microsoft 身份平台进行配置 |
| **应用程序（客户端）ID** | 您应用程序的唯一标识符 |
| **租户 ID** | 您 Azure AD 租户/目录的唯一标识符 |
| **客户端密钥** | 应用程序的密码（仅限机密客户端） |
| **重定向 URI** | 身份验证响应发送到的 URL |
| **API 权限** | 您应用程序请求的访问范围 |
| **服务主体** | 在您租户中注册应用程序时创建的身份 |

### 应用程序类型

| 类型 | 用例 |
|------|----------|
| **Web 应用程序** | 服务器端应用程序、API |
| **单页应用程序（SPA）** | JavaScript/React/Angular 应用程序 |
| **移动/原生应用程序** | 桌面、移动应用程序 |
| **守护进程/服务** | 后台服务、API |

## 核心工作流程

### 第 1 步：注册应用程序

在 Azure 门户中创建应用程序注册，或使用 Azure CLI。

**门户方法：**
1. 导航到 Azure 门户 → Microsoft Entra ID → 应用程序注册
2. 点击“新注册”
3. 提供名称、支持的帐户类型和重定向 URI
4. 点击“注册”

**CLI 方法：** 参考 [references/cli-commands.md](references/cli-commands.md)
**IaC 方法：** 参考 [references/BICEP-EXAMPLE.bicep](references/BICEP-EXAMPLE.bicep)

如果您的项目中已经使用 IaC，或者需要可扩展的解决方案来管理大量应用程序注册，或者需要配置更改的细粒度审计历史记录，则强烈建议使用 IaC 来管理 Entra 应用程序注册。

### 第 2 步：配置身份验证

根据您的应用程序类型设置身份验证设置。

- **Web 应用程序**：添加重定向 URI，如果需要则启用 ID 令牌
- **SPAs**：添加重定向 URI，如有必要则启用隐式授权流程
- **移动/桌面**：使用 `http://localhost` 或自定义 URI 方案
- **服务**：客户端凭据流不需要重定向 URI

### 第 3 步：配置 API 权限

授予您的应用程序访问 Microsoft API 或您自己的 API 的权限。

**常见的 Microsoft Graph 权限：**
- `User.Read` - 读取用户配置文件
- `User.ReadWrite.All` - 读取和写入所有用户
- `Directory.Read.All` - 读取目录数据
- `Mail.Send` - 以用户身份发送邮件

**详细信息：** 参考 [references/api-permissions.md](references/api-permissions.md)

### 第 4 步：创建客户端凭据（如果需要）

对于机密客户端应用程序（Web 应用程序、服务），创建客户端密钥、证书或联合身份凭证。

**客户端密钥：**
- 导航到“证书和密钥”
- 创建新的客户端密钥
- 立即复制值（仅显示一次）
- 安全存储（推荐使用密钥保管库）

**证书：** 对于生产环境，使用证书而不是密钥以增强安全性。通过“证书和密钥”部分上传证书。

**联合身份凭证：** 用于动态验证机密客户端到 Entra 平台。

### 第 5 步：实现 OAuth 流程

将 OAuth 流程集成到您的应用程序代码中。

**参考：**
- [references/oauth-flows.md](references/oauth-flows.md) - OAuth 2.0 流程详细信息
- [references/console-app-example.md](references/console-app-example.md) - 控制台应用程序实现

## 常见模式

### 模式 1：首次应用程序注册

逐步引导用户完成首次应用程序注册。

**所需信息：**
- 应用程序名称
- 应用程序类型（Web、SPA、移动、服务）
- 重定向 URI（如果适用）
- 所需权限

**脚本：** 参考 [references/first-app-registration.md](references/first-app-registration.md)

### 模式 2：具有用户身份验证的控制台应用程序

创建一个 .NET/Python/Node.js 控制台应用程序，该应用程序可以验证用户。

**所需信息：**
- 编程语言（C#、Python、JavaScript 等）
- 身份验证库（推荐使用 MSAL）
- 所需权限

**示例：** 参考 [references/console-app-example.md](references/console-app-example.md)

### 模式 3：服务到服务身份验证

设置无需用户交互的守护进程/服务身份验证。

**所需信息：**
- 服务/应用程序名称
- 目标 API/资源
- 是否使用密钥或证书

**实现：** 使用客户端凭据流（参考 [references/oauth-flows.md#client-credentials-flow](references/oauth-flows.md#client-credentials-flow)）

## MCP 工具和 CLI

### Azure CLI 命令

| 命令 | 目的 |
|------|---------|
| `az ad app create` | 创建新的应用程序注册 |
| `az ad app list` | 列出应用程序注册 |
| `az ad app show` | 显示应用程序详细信息 |
| `az ad app permission add` | 添加 API 权限 |
| `az ad app credential reset` | 生成新的客户端密钥 |
| `az ad sp create` | 创建服务主体 |

**完整参考：** 参考 [references/cli-commands.md](references/cli-commands.md)

### Microsoft 身份验证库（MSAL）

MSAL 是集成 Microsoft 身份平台的推荐库。

**支持的语言：**
- .NET/C# - `Microsoft.Identity.Client`
- JavaScript/TypeScript - `@azure/msal-browser`, `@azure/msal-node`
- Python - `msal`

**示例：** 参考 [references/console-app-example.md](references/console-app-example.md)

## 安全最佳实践

| 实践 | 建议 |
|----------|---------------|
| **从不硬编码密钥** | 使用环境变量、Azure 密钥保管库或托管身份 |
| **定期轮换密钥** | 设置过期时间，自动化轮换 |
| **使用证书而不是密钥** | 生产环境更安全 |
| **最小权限权限** | 仅请求所需的 API 权限 |
| **启用 MFA** | 要求用户进行多因素身份验证 |
| **使用托管身份** | 对于 Azure 托管的应用程序，完全避免密钥 |
| **验证令牌** | 始终验证发行者、受众、过期时间 |
| **仅使用 HTTPS** | 所有重定向 URI 必须使用 HTTPS（localhost 除外） |
| **监控登录** | 使用 Entra ID 登录日志进行异常检测 |

## SDK 快速参考

- **Azure Identity**: [Python](references/sdk/azure-identity-py.md) | [.NET](references/sdk/azure-identity-dotnet.md) | [TypeScript](references/sdk/azure-identity-ts.md) | [Java](references/sdk/azure-identity-java.md) | [Rust](references/sdk/azure-identity-rust.md)
- **密钥保管库（密钥）**: [Python](references/sdk/azure-keyvault-py.md) | [TypeScript](references/sdk/azure-keyvault-secrets-ts.md)
- **身份验证事件**: [.NET](references/sdk/microsoft-azure-webjobs-extensions-authentication-events-dotnet.md)

## 参考

- [OAuth 流程](references/oauth-flows.md) - 详细的 OAuth 2.0 流程说明
- [CLI 命令](references/cli-commands.md) - Azure CLI 应用程序注册参考
- [控制台应用程序示例](references/console-app-example.md) - 完整的工作示例
- [首次应用程序注册](references/first-app-registration.md) - 逐步指南，适合初学者
- [API 权限](references/api-permissions.md) - 理解和配置权限
- [故障排除](references/troubleshooting.md) - 常见问题和解决方案

## 外部资源

- [Microsoft 身份平台文档](https://learn.microsoft.com/entra/identity-platform/)
- [OAuth 2.0 和 OpenID Connect 协议](https://learn.microsoft.com/entra/identity-platform/v2-protocols)
- [MSAL 文档](https://learn.microsoft.com/entra/msal/)
- [Microsoft Graph API](https://learn.microsoft.com/graph/)
