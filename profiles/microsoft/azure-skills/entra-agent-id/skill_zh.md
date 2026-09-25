# Microsoft Entra Agent ID

使用 Microsoft Graph 创建和管理适用于 AI 代理的 OAuth 2.0 兼容身份。每个代理实例都将获得一个独特的身份、审计跟踪以及独立作用域的权限授予。

## 快速参考

| 属性 | 值 |
|------|-------|
| 服务 | Microsoft Entra Agent ID |
| API | Microsoft Graph (`https://graph.microsoft.com/v1.0`) |
| 必需角色 | Agent Identity Developer、Agent Identity Administrator 或 Application Administrator |
| 对象模型 | Blueprint (应用程序) → BlueprintPrincipal (SP) → Agent Identity (SP) |
| 运行时交换 | 两步 `fmi_path` 交换（自主和 OBO） |
| .NET 助手 | `Microsoft.Identity.Web.AgentIdentities` |
| 多语言助手 | Microsoft Entra SDK for AgentID（侧边容器） |

## 何时使用此技能

- 部署新的 Agent Identity Blueprint 和 BlueprintPrincipal
- 在 Blueprint 下创建每个实例的 Agent Identities
- 在 Blueprint 上配置凭证（FIC、托管身份或客户端密钥）
- 实现两步 `fmi_path` 运行时令牌交换（自主或 OBO）
- 跨租户代理令牌流
- 部署 Microsoft Entra SDK for AgentID 侧边容器用于多语言代理（Python、Node、Go、Java）
- 授予每个 Agent-Identity 应用程序 (`appRoleAssignments`) 或委派 (`oauth2PermissionGrants`) 权限
- 诊断 Agent ID 错误，如 `AADSTS82001`、`AADSTS700211` 或 `PropertyNotCompatibleWithAgentIdentity`

## MCP 工具

| 工具 | 用途 |
|------|-----|
| `mcp_azure_mcp_documentation` | 在 Microsoft Learn 中搜索当前的 Agent ID 设置、Graph API 形状和 SDK 配置 |

目前没有专门的 Agent Identity MCP 服务器。此技能指导直接 Microsoft Graph API 调用（PowerShell 或 Python `requests`）。在运行之前，使用 `mcp_azure_mcp_documentation` 根据当前文档验证请求正文和端点。

## 开始之前

使用 `mcp_azure_mcp_documentation` 工具在 Microsoft Learn 中搜索当前的 Agent ID 文档：
- "Microsoft Entra Agent ID 设置说明"
- "Microsoft Entra SDK for AgentID"

验证请求正文和端点是否与安装的 SDK 版本一致——Graph API 形状会演变。

## 概念模型

```
Agent Identity Blueprint (应用程序)         ← 每个代理类型/项目一个
  └── BlueprintPrincipal (服务主体)    ← 必须显式创建
        ├── Agent Identity (SP): agent-1        ← 每个代理实例一个
        ├── Agent Identity (SP): agent-2
        └── Agent Identity (SP): agent-3
```

| 概念 | 描述 |
|---------|-------------|
| **Blueprint** | 定义代理类型/类的应用程序对象。包含凭证（密钥、证书、联合身份）。 |
| **BlueprintPrincipal** | 租户中 Blueprint 的服务主体。不会自动创建。 |
| **Agent Identity** | 单个代理实例的服务主体身份。不能持有自己的凭证。 |
| **Sponsor** | 负责身份的用户（或组，对于 Agent Identity）。创建时必需。 |

## 前置条件

### 必需的 Entra 角色

一个：**Agent Identity Developer**、**Agent Identity Administrator** 或 **Application Administrator**。

### PowerShell（交互式设置）

```powershell
# PowerShell 7+
Install-Module Microsoft.Graph.Applications -Scope CurrentUser -Force
```

### Python（程序化部署）

```bash
pip install azure-identity requests
```

## 身份验证

> **`DefaultAzureCredential` 不受支持。** Azure CLI 令牌包含 `Directory.AccessAsUser.All`，Agent Identity API 会硬拒绝（403）。使用具有 `client_credentials` 的专用应用注册，或使用 `Connect-MgGraph` 并显式指定委派范围。

### PowerShell（委派）

```powershell
Connect-MgGraph -Scopes @(
    "AgentIdentityBlueprint.Create",
    "AgentIdentityBlueprint.ReadWrite.All",
    "AgentIdentityBlueprintPrincipal.Create",
    "AgentIdentity.Create.All",
    "User.Read"
)
```

### Python（应用程序）

```python
import os, requests
from azure.identity import ClientSecretCredential

credential = ClientSecretCredential(
    tenant_id=os.environ["AZURE_TENANT_ID"],
    client_id=os.environ["AZURE_CLIENT_ID"],
    client_secret=os.environ["AZURE_CLIENT_SECRET"],
)
token = credential.get_token("https://graph.microsoft.com/.default")

GRAPH = "https://graph.microsoft.com/v1.0"
headers = {
    "Authorization": f"Bearer {token.token}",
    "Content-Type": "application/json",
    "OData-Version": "4.0",
}
```

## 核心工作流

### 第 1 步：创建 Agent Identity Blueprint

使用类型化端点。Blueprint 创建时赞助者必须是 **用户**。此代码片段假设 Python 身份验证块中的 `requests` 客户端和 `headers` 字典。

```python
import subprocess
import requests

user_id = subprocess.run(
    ["az", "ad", "signed-in-user", "show", "--query", "id", "-o", "tsv"],
    capture_output=True, text=True, check=True,
).stdout.strip()

blueprint_body = {
    "displayName": "My Agent Blueprint",
    "sponsors@odata.bind": [
        f"https://graph.microsoft.com/v1.0/users/{user_id}"
    ],
}
resp = requests.post(
    f"{GRAPH}/applications/microsoft.graph.agentIdentityBlueprint",
    headers=headers, json=blueprint_body,
)
resp.raise_for_status()

blueprint = resp.json()
app_id = blueprint["appId"]
blueprint_obj_id = blueprint["id"]
```

### 第 2 步：创建 BlueprintPrincipal

> 必须执行。创建 Blueprint 不会自动创建其服务主体。跳过此步骤将产生：
> `400: Agent Blueprint Principal for the Agent Blueprint does not exist.`

```python
sp_body = {"appId": app_id}
resp = requests.post(
    f"{GRAPH}/servicePrincipals/microsoft.graph.agentIdentityBlueprintPrincipal",
    headers=headers, json=sp_body,
)
resp.raise_for_status()
```

使您的部署脚本幂等——即使 Blueprint 已存在，也始终检查 BlueprintPrincipal。

### 第 3 步：创建 Agent Identities

Agent Identity 的赞助者可以是 **用户或组**。

```python
agent_body = {
    "displayName": "my-agent-instance-1",
    "agentIdentityBlueprintId": app_id,
    "sponsors@odata.bind": [
        f"https://graph.microsoft.com/v1.0/users/{user_id}"
    ],
}
resp = requests.post(
    f"{GRAPH}/servicePrincipals/microsoft.graph.agentIdentity",
    headers=headers, json=agent_body,
)
resp.raise_for_status()
agent = resp.json()
agent_sp_id = agent["id"]
```

## 运行时身份验证

代理在运行时使用在 **Blueprint** 上配置的凭证进行身份验证（而不是在 Agent Identity 上——Agent Identities 不能持有凭证）。

| 选项 | 用例 | Blueprint 上的凭证 |
|--------|----------|------------------------|
| **Managed Identity + WIF** | 生产（Azure 托管） | 联合身份凭证 |
| **客户端密钥** | 本地开发/测试 | 密码凭证 |
| **Microsoft Entra SDK for AgentID** | 多语言/第三方代理 | 侧边容器通过 HTTP 获取令牌 |

对于两步 `fmi_path` 交换（父令牌→每个 Agent-Identity 的 Graph 令牌），这为每个代理实例提供了一个独特的 `sub` 声明和审计跟踪，请参阅 [references/runtime-token-exchange.md](references/runtime-token-exchange.md)。

对于 OBO（代理代表用户操作），请参阅 [references/obo-blueprint-setup.md](references/obo-blueprint-setup.md)。

对于容器化多语言身份验证侧边容器（Python、Node、Go、Java——无 SDK 嵌入），请参阅 [references/sdk-sidecar.md](references/sdk-sidecar.md)。

对于 MI+WIF 和客户端密钥设置详情，请参阅 [references/oauth2-token-flow.md](references/oauth2-token-flow.md)。

### .NET 快速路径

对于 .NET 服务，使用 **`Microsoft.Identity.Web.AgentIdentities`**——它处理联合身份凭证管理和两步交换。请参阅 `github.com/AzureAD/microsoft-identity-web` 下 `src/Microsoft.Identity.Web.AgentIdentities/` 的包 README。

## 授予权限（每个 Agent Identity）

Agent Identities 支持应用程序权限（自主）和委派权限（OBO）。授予权限按 **每个 Agent Identity** 范围划分，而不是 BlueprintPrincipal。

### 应用程序权限（自主）

```python
graph_sp = requests.get(
    f"{GRAPH}/servicePrincipals?$filter=appId eq '00000003-0000-0000-c000-000000000000'",
    headers=headers,
).json()["value"][0]

user_read_all = next(r for r in graph_sp["appRoles"] if r["value"] == "User.Read.All")

requests.post(
    f"{GRAPH}/servicePrincipals/{agent_sp_id}/appRoleAssignments",
    headers=headers,
    json={
        "principalId": agent_sp_id,
        "resourceId": graph_sp["id"],
        "appRoleId": user_read_all["id"],
    },
).raise_for_status()
```

### 委派权限（OBO）

```python
from datetime import datetime, timedelta, timezone

expiry = (datetime.now(timezone.utc) + timedelta(days=3650)).strftime("%Y-%m-%dT%H:%M:%SZ")

requests.post(
    f"{GRAPH}/oauth2PermissionGrants",
    headers=headers,
    json={
        "clientId": agent_sp_id,
        "consentType": "AllPrincipals",
        "resourceId": graph_sp["id"],
        "scope": "User.Read Tasks.ReadWrite Mail.Send",
        "expiryTime": expiry,
    },
).raise_for_status()
```

基于浏览器的管理员同意 URL 对 Agent Identities 不起作用——使用 `oauth2PermissionGrants` 进行程序化委派同意。

## 跨租户 Agent Identities

Blueprints 可以是多租户的 (`signInAudience: AzureADMultipleOrgs`)。当跨租户交换令牌时：

> **父令牌交换的第一步必须针对 Agent Identity 的主租户**，而不是 Blueprint。错误租户 → `AADSTS700211: No matching federated identity record found`。

请参阅 [references/runtime-token-exchange.md](references/runtime-token-exchange.md) 获取完整的跨租户示例。

## API 参考

| 操作 | 方法 | 端点 |
|-----------|--------|----------|
| 创建 Blueprint | `POST` | `/applications/microsoft.graph.agentIdentityBlueprint` |
| 创建 BlueprintPrincipal | `POST` | `/servicePrincipals/microsoft.graph.agentIdentityBlueprintPrincipal` |
| 创建 Agent Identity | `POST` | `/servicePrincipals/microsoft.graph.agentIdentity` |
| 向 Blueprint 添加 FIC | `POST` | `/applications/{id}/microsoft.graph.agentIdentityBlueprint/federatedIdentityCredentials` |
| 列出 Agent Identities | `GET` | `/servicePrincipals/microsoft.graph.agentIdentity` |
| 授予应用权限 | `POST` | `/servicePrincipals/{id}/appRoleAssignments` |
| 授予委派权限 | `POST` | `/oauth2PermissionGrants` |
| 删除 Agent Identity | `DELETE` | `/servicePrincipals/{id}` |
| 删除 Blueprint | `DELETE` | `/applications/{id}` |

基础 URL：`https://graph.microsoft.com/v1.0`。

## 必需的 Graph 权限

| 权限 | 目的 |
|-----------|---------|
| `AgentIdentityBlueprint.Create` | 创建 Blueprints |
| `AgentIdentityBlueprint.ReadWrite.All` | 读取/更新 Blueprints |
| `AgentIdentityBlueprintPrincipal.Create` | 创建 BlueprintPrincipals |
| `AgentIdentity.Create.All` | 创建 Agent Identities |
| `AgentIdentity.ReadWrite.All` | 读取/更新 Agent Identities |
| `Application.ReadWrite.All` | 应用程序对象上的 Blueprint CRUD |
| `AppRoleAssignment.ReadWrite.All` | 授予应用程序权限 |
| `DelegatedPermissionGrant.ReadWrite.All` | 授予委派权限 |

授予权限（需要应用权限）：

```bash
az ad app permission admin-consent --id <client-id>
```

授予权限后，令牌可能不会包含新声明 30–120 秒——使用指数退避重试。

## 最佳实践

1. **始终在 Blueprint 之后创建 BlueprintPrincipal**——不会自动创建。
2. **使用类型化端点**（`/applications/microsoft.graph.agentIdentityBlueprint`）而不是原始 `/applications` 与 `@odata.type`。
3. **凭证位于 Blueprint 上**——Agent Identities 不能持有密钥/证书（`PropertyNotCompatibleWithAgentIdentity`）。
4. **每个 Graph 请求都包含 `OData-Version: 4.0`**。
5. **生产中使用 Workload Identity Federation**——仅本地开发使用客户端密钥。
6. **在 OAuth2 范围解析之前在 Blueprint 上设置 `identifierUris: ["api://{appId}"]`**。
7. **绝对不要使用 Azure CLI 令牌**用于 Agent Identity API——`Directory.AccessAsUser.All` 导致硬 403。
8. **使用 `fmi_path` 与 `client_credentials`**——不是 RFC 8693 `urn:ietf:params:oauth:grant-type:token-exchange`（返回 `AADSTS82001`）。
9. **两步交换的每一步都使用 `/.default` 范围**——单个范围会失败。
10. **跨租户流中的第一步针对 Agent Identity 的主租户**。
11. **按 Agent Identity 授予权限**，而不是 BlueprintPrincipal。
12. **处理权限传播延迟**——授予权限后 30–120 秒重试 403。
13. **将 Entra SDK for AgentID 保留在 localhost**——不要通过 LoadBalancer 或 Ingress 暴露。

## 故障排除

| 错误 | 原因 | 修复 |
|-------|-------|-----|
| `AADSTS82001` | 使用 RFC 8693 令牌交换 | 使用 `client_credentials` 与 `fmi_path` |
| `AADSTS700211` | 第一步父令牌针对错误租户 | 针对Agent Identity的主租户 |
| `AADSTS50013` | OBO 用户令牌针对 Graph，而不是 Blueprint | 使用 `api://{blueprint_app_id}/access_as_user` |
| `AADSTS65001` | 缺少授予权限或使用单个范围 | 使用 `/.default` 并验证 `oauth2PermissionGrants` |
| `403 Authorization_RequestDenied` | 此 Agent Identity 没有授予权限 | 通过 `appRoleAssignments` 或 `oauth2PermissionGrants` 添加 |
| `PropertyNotCompatibleWithAgentIdentity` | 尝试向 Agent Identity SP 添加凭证 | 将凭证放在 Blueprint 上 |
| `Agent Blueprint Principal does not exist` | 未创建 BlueprintPrincipal | Core 工作流的第 2 步 |
| `AADSTS650051` 在管理员同意时 | SP 从部分同意中已存在 | 直接通过 `appRoleAssignments` 授予权限 |

## 参考

| 文件 | 内容 |
|------|----------|
| [references/runtime-token-exchange.md](references/runtime-token-exchange.md) | 两步 `fmi_path` 交换：自主 + OBO，跨租户 |
| [references/oauth2-token-flow.md](references/oauth2-token-flow.md) | MI + WIF（生产）和客户端密钥（本地开发） |
| [references/obo-blueprint-setup.md](references/obo-blueprint-setup.md) | 将 Blueprint 配置为 OAuth2 API 以用于 OBO |
| [references/sdk-sidecar.md](references/sdk-sidecar.md) | Microsoft Entra SDK for AgentID——架构、配置、端点 |
| [references/sdk-sidecar-deployment.md](references/sdk-sidecar-deployment.md) | SDK 代码模式（Python/TypeScript）、Docker/Kubernetes 资源清单、安全、故障排除 |
| [references/known-limitations.md](references/known-limitations.md) | 按类别组织的文档中记录的差距 |

### 外部链接

| 资源 | URL |
|----------|-----|
| Agent ID 设置指南 | https://learn.microsoft.com/en-us/entra/agent-id/identity-platform/agent-id-setup-instructions |
| AI 指导设置 | https://learn.microsoft.com/en-us/entra/agent-id/identity-platform/agent-id-ai-guided-setup |
| Microsoft Entra SDK for AgentID | https://learn.microsoft.com/en-us/entra/msidweb/agent-id-sdk/overview |
| Microsoft.Identity.Web.AgentIdentities (.NET) | https://github.com/AzureAD/microsoft-identity-web/blob/master/src/Microsoft.Identity.Web.AgentIdentities/README.AgentIdentities.md |
