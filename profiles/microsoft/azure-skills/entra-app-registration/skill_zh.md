## 概述

Microsoft Entra ID（原 Azure Active Directory）是 Microsoft 的云原生身份与访问管理服务。应用注册允许应用程序安全地验证用户并访问 Azure 资源。

### 关键概念

| 概念 | 描述 |
|---------|-------------|
| **App Registration** | 允许应用使用 Microsoft 身份平台的配置 |
| **Application (Client) ID** | 应用的唯一标识符 |
| **Tenant ID** | Azure AD 租户/目录的唯一标识符 |
| **Client Secret** | 应用的密码（仅限机密客户端） |
| **Redirect URI** | 发送身份验证响应的 URL |
| **API Permissions** | 应用请求的访问范围 |
| **Service Principal** | 在您的租户中注册应用时创建的标识 |

### 应用类型

| 类型 | 使用场景 |
|------|----------|
| **Web Application** | 服务端应用、API |
| **Single Page App (SPA)** | JavaScript/React/Angular 应用 |
| **Mobile/Native App** | 桌面端、移动端应用 |
| **Daemon/Service** | 后台服务、API |

## 核心工作流

### 步骤 1：注册应用

在 Azure 门户或通过 Azure CLI 创建应用注册。

**门户方法：**
1. 导航至 Azure 门户 → Microsoft Entra ID → 应用注册
2. 点击“新建注册”
3. 提供名称、支持的账户类型以及重定向 URI
4. 点击“注册”

**CLI 方法：** 参见 [references/cli-commands.md](references/cli-commands.md)
**IaC 方法：** 参见 [references/BICEP-EXAMPLE.bicep](references/BICEP-EXAMPLE.bicep)

如果您的项目已使用 IaC，建议使用 IaC 管理 Entra 应用注册；如需管理大量应用注册的扩展方案，或需要配置变更的细粒度审计历史，均应使用 IaC。

### 步骤 2：配置身份验证

根据应用类型设置身份验证设置。

- **Web 应用：** 添加重定向 URI，如需要则启用 ID 令牌
- **SPA（单页应用）：** 添加重定向 URI，如需要则启用隐式授权流程
- **移动端/桌面端：** 使用 `http://localhost` 或自定义 URI 方案
- **服务：** 客户端凭据流程无需重定向 URI

### 步骤 3：配置 API 权限

授予您的应用访问 Microsoft API 或自有 API 的权限。

**常见的 Microsoft Graph 权限：**
- `User.Read` - 读取用户资料
- `User.ReadWrite.All` - 读取和写入所有用户
- `Directory.Read.All` - 读取目录数据
- `Mail.Send` - 以用户身份发送邮件

**详情：** 参见 [references/api-permissions.md](references/api-permissions.md)

### 步骤 4：创建客户端凭据（如需要）

对于机密客户端应用（Web 应用、服务），创建客户端密钥、证书或联邦身份凭据。

**客户端密钥：**
- 导航至“证书与密钥”
- 创建新的客户端密钥
- 立即复制该值（仅显示一次）
- 安全存储（建议使用 Key Vault）

**证书：** 为增强安全性，生产环境应使用证书而非密钥。通过“证书与密钥”部分上传证书。

**联邦身份凭据：** 用于动态验证机密客户端与 Entra 平台的身份认证。

### 步骤 5：实现 OAuth 流程

将 OAuth 流程集成到您的应用代码中。

**参见：**
- [references/oauth-flows.md](references/oauth-flows.md) - OAuth 2.0 流程详情
- [references/console-app-example.md](references/console-app-example.md) - 控制台应用实现

## 常用模式

### 模式 1：首次应用注册

逐步指导用户完成首次应用注册。

**所需信息：**
- 应用名称
- 应用类型（Web、SPA、移动端、服务）
- 重定向 URI（如适用）
- 所需权限

**脚本：** 参见 [references/first-app-registration.md](references/first-app-registration.md)

### 模式 2：带用户身份验证的控制台应用

创建用于用户身份验证的 .NET/Python/Node.js 控制台应用。

**所需信息：**
- 编程语言（C#、Python、JavaScript 等）
- 身份验证库（推荐使用 MSAL）
- 所需权限

**示例：** 参见 [references/console-app-example.md](references/console-app-example.md)

### 模式 3：服务间认证

配置无需用户交互的守护进程/服务认证。

**所需信息：**
- 服务/应用名称
- 目标 API/资源
- 是否使用密钥或证书

**实现：** 使用客户端凭据流程（参见 [references/oauth-flows.md#client-credentials-flow](references/oauth-flows.md#client-credentials-flow)）

## MCP 工具与 CLI

### Azure CLI 命令

| 命令 | 用途 |
|---------|---------|
| `az ad app create` | 创建新的应用注册 |
| `az ad app list` | 列出应用注册 |
| `az ad app show` | 显示应用详情 |
| `az ad app permission add` | 添加 API 权限 |
| `az ad app credential reset` | 生成新的客户端密钥 |
| `az ad sp create` | 创建服务主体 |

**完整参考：** 参见 [references/cli-commands.md](references/cli-commands.md)

### Microsoft 身份验证库 (MSAL)

MSAL 是集成 Microsoft 身份平台推荐的库。

**支持的语言：**
- .NET/C# - `Microsoft.Identity.Client`
- JavaScript/TypeScript - `@azure/msal-browser`, `@azure/msal-node`
- Python - `msal`

**示例：** 参见 [references/console-app-example.md](references/console-app-example.md)

## 安全最佳实践

| 实践 | 建议 |
|----------|-------------|
| **切勿硬编码密钥** | 使用环境变量、Azure Key Vault 或托管标识 |
| **定期轮换密钥** | 设置过期时间，自动化轮换 |
| **使用证书而非密钥** | 对生产环境更为安全 |
| **遵循最小权限原则** | 仅请求所需的 API 权限 |
| **启用 MFA（多因素认证）** | 要求用户进行多因素认证 |
| **使用托管标识** | 对于 Azure 托管的应用，完全避免使用密钥 |
| **验证令牌** | 始终验证签发者、受众和有效期 |
| **仅使用 HTTPS** | 所有重定向 URI 必须使用 HTTPS（localhost 除外） |
| **监控登录** | 使用 Entra ID 登录日志进行异常检测 |

## SDK 快速参考

- **Azure Identity**：[Python](references/sdk/azure-identity-py.md) | [.NET](references/sdk/azure-identity-dotnet.md) | [TypeScript](references/sdk/azure-identity-ts.md) | [Java](references/sdk/azure-identity-java.md) | [Rust](references/sdk/azure-identity-rust.md)
- **密钥保管库 (Key Vault - secrets)**：[Python](references/sdk/azure-keyvault-py.md) | [TypeScript](references/sdk/azure-keyvault-secrets-ts.md)
- **认证事件**：[.NET](references/sdk/microsoft-azure-webjobs-extensions-authentication-events-dotnet.md)

## 参考资料

- [OAuth 流程](references/oauth-flows.md) - 详细的 OAuth 2.0 流程解释
- [CLI 命令](references/cli-commands.md) - 应用注册的 Azure CLI 参考
- [控制台应用示例](references/console-app-example.md) - 完整的可用示例
- [首次应用注册](references/first-app-registration.md) - 初学者的分步指南
- [API 权限](references/api-permissions.md) - 理解与配置权限
- [故障排查](references/troubleshooting.md) - 常见问题与解决方案

## 外部资源

- [Microsoft 身份平台文档](https://learn.microsoft.com/entra/identity-platform/)
- [OAuth 2.0 与 OpenID Connect 协议](https://learn.microsoft.com/entra/identity-platform/v2-protocols)
- [MSAL 文档](https://learn.microsoft.com/entra/msal/)
- [Microsoft Graph API](https://learn.microsoft.com/graph/)
