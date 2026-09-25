# Microsoft Entra Agent ID

使用 Microsoft Graph 为 AI Agent 创建和管理支持 OAuth 2.0 的身份。每个 Agent 实例均获得独立的身份、审计轨迹和独立范围授权的权限。

## Quick Reference

| 属性 | 值 |
|----------|-------|
| 服务 | Microsoft Entra Agent ID |
| API | Microsoft Graph（`https://graph.microsoft.com/v1.0`） |
| 必需角色 | Agent Identity 开发者、Agent Identity 管理员，或应用程序管理员 |
| 对象模型 | Blueprint（应用程序）→ BlueprintPrincipal（SP）→ Agent Identity（SP） |
| 运行时交换 | 两步 `fmi_path` 交换（自主和 OBO） |
| .NET 辅助工具 | `Microsoft.Identity.Web.AgentIdentities` |
| 多语言辅助工具 | Microsoft Entra SDK for AgentID（sidecar 容器） |

## 何时使用此技能

- 配置新的 Agent Identity Blueprint 和 BlueprintPrincipal
- 在 Blueprint 下为每个实例创建 Agent Identity
- 在 Blueprint 上配置凭证（FIC、托管身份，或客户端密钥）
- 实现两步 `fmi_path` 运行时令牌交换（自主或 OBO）
- 跨租户的 Agent 令牌流程
- 为多语言 Agent（Python、Node、Go、Java）部署 Microsoft Entra SDK for AgentID sidecar
- 授予每个 Agent Identity 的应用权限（`appRoleAssignments`）或委托权限（`oauth2PermissionGrants`）
- 诊断 Agent ID 错误，如 `AADSTS82001`、`AADSTS700211` 或 `PropertyNotCompatibleWithAgentIdentity`

## MCP 工具

| 工具 | 用途 |
|------|------|
| `mcp_azure_mcp_documentation` | 在 Microsoft Learn 中搜索当前的 Agent ID 设置、Graph API 形状和 SDK 配置 |

目前尚无专门的 Agent Identity MCP 服务器。本技能指导直接调用 Microsoft Graph API（PowerShell 或 Python `requests`）。在运行前，使用 `mcp_azure_mcp_documentation` 对照当前文档验证请求体和端点。

## 开始之前

使用 `mcp_azure_mcp_documentation` 工具在 Microsoft Learn 中搜索当前的 Agent ID 文档：
- "Microsoft Entra Agent ID 设置说明"
- "Microsoft Entra SDK for AgentID"

对照已安装的 SDK 版本验证请求体和端点——Graph API 形状会演进。

## 概念模型

```
Agent Identity Blueprint (application)         ← 每个 Agent 类型/项目一个
  └── BlueprintPrincipal (service principal)    ← 必须显式创建
        ├── Agent Identity (SP): agent-1        ← 每个 Agent 实例一个
        ├── Agent Identity (SP): agent-2
        └── Agent Identity (SP): agent-3
```

| 概念 | 说明 |
|---------|-------------|
| **Blueprint** | 定义 Agent 类型/类的应用程序对象。包含凭证（密钥、证书、联合身份）。 |
| **BlueprintPrincipal** | Blueprint 在租户中的服务主体。不会自动创建。 |
| **Agent Identity** | 单个 Agent 实例专用的仅服务主体身份。无法持有自身凭证。 |
| **Sponsor** | 负责该身份的用户（或 Agent Identity 的群组）。创建时必需。 |

## 前提条件

### 必需 Entra 角色

以下三者之一：**Agent Identity 开发者**、**Agent Identity 管理员**，或**应用程序管理员**。

### PowerShell（交互式设置）

```powershell
# PowerShell 7+
Install-Module Microsoft.Graph.Applications -Scope CurrentUser -Force
```

### Python（编程式配置）

```bash
pip install azure-identity requests
```

## 身份验证

> **`DefaultAzureCredential` 不受支持。** Azure CLI 令牌包含 `Directory.AccessAsUser.All`，Agent Identity API 会直接拒绝（403）。请使用带有 `client_credentials` 的专用应用注册，或使用 `Connect-MgGraph` 并显式指定委托范围。

### PowerShell（委托方式）

```powershell
Connect-MgGraph -Scopes @(
    "AgentIdentityBlueprint.Create",
    "AgentIdentityBlueprint.ReadWrite.All",
    "AgentIdentityBlueprintPrincipal.Create",
    "AgentIdentity.Create.All",
    "User.Read"
)
```

### Python（应用方式）

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

### 步骤 1：创建 Agent Identity Blueprint

使用类型化接口。创建蓝图时，赞助者必须为 **用户**。此代码片段假设使用了上述 Python 身份验证代码块中的 `requests` 客户端和 `headers` 字典。

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

### 步骤 2：创建 BlueprintPrincipal

> 必需。创建 Blueprint **不会**自动创建其服务主体。跳过此步骤将产生：
> `400: The Agent Blueprint Principal for the Agent Blueprint does not exist.`

```python
sp_body = {"appId": app_id}
resp = requests.post(
    f"{GRAPH}/servicePrincipals/microsoft.graph.agentIdentityBlueprintPrincipal",
    headers=headers, json=sp_body,
)
resp.raise_for_status()
```

请使配置脚本具有幂等性——即使 Blueprint 已存在，也始终检查 BlueprintPrincipal 是否存在。

### 步骤 3：创建 Agent Identity

Agent Identity 的赞助者可以是 **用户或群组**。

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

Agent 在运行时使用在 **Blueprint** 上配置的凭证进行身份验证（而非在 Agent Identity 上——Agent Identity 无法持有凭证）。

| 选项 | 用例 | Blueprint 上的凭证 |
|--------|----------|------------------------|
| **托管身份 + WIF** | 生产环境（Azure 托管） | 受附联合身份凭证 |
| **客户端密钥** | 本地开发/测试 | 密码凭证 |
| **Microsoft Entra SDK for AgentID** | 多语言/三方 Agent | sidecar 容器通过 HTTP 获取令牌 |

有关两步 `fmi_path` 交换（父令牌 → 每个 Agent Identity 的 Graph 令牌），可为每个 Agent 实例提供不同的 `sub` 声明和审计轨迹，请参阅 [references/runtime-token-exchange.md](references/runtime-token-exchange.md)。

有关 OBO（Agent 代表用户行动），请参阅 [references/obo-blueprint-setup.md](references/obo-blueprint-setup.md)。

有关容器化多语言认证 sidecar（Python、Node、Go、Java——无需嵌入 SDK），请参阅 [references/sdk-sidecar.md](references/sdk-sidecar.md)。

有关 MI+WIF 和客户端密钥设置的详细信息，请参阅 [references/oauth2-token-flow.md](references/oauth2-token-flow.md)。

### .NET 快速路径

对于 .NET 服务，使用 **`Microsoft.Identity.Web.AgentIdentities`**——它会自动处理 Federated Identity Credential 管理和两步交换。参见位于 `github.com/AzureAD/microsoft-identity-web` 下 `src/Microsoft.Identity.Web.AgentIdentities/` 处的包 README。

## 授予权限（按 Agent Identity）

Agent Identity 支持应用权限（自主）和委托权限（OBO）。授予范围按 **Agent Identity** 限定，而非 BlueprintPrincipal。

### 应用权限（自主）

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

### 委托权限（OBO）

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

基于浏览器的管理同意 URL 对 Agent Identity 不起作用——请使用 `oauth2PermissionGrants` 进行编程式委托同意。

## 跨租户 Agent Identity

Blueprint 可以是多租户（`signInAudience: AzureADMultipleOrgs`）。跨租户交换令牌时：

> **父令牌交换的步骤 1 必须指向 Agent Identity 的主租户，而非 Blueprint 的。** 租户错误将导致 `AADSTS700211: No matching federated identity record found`。

有关完整的跨租户示例，请参阅 [references/runtime-token-exchange.md](references/runtime-token-exchange.md)。

## API 参考

| 操作 | 方法 | 端点 |
|--------|--------|----------|
| 创建 Blueprint | `POST` | `/applications/microsoft.graph.agentIdentityBlueprint` |
| 创建 BlueprintPrincipal | `POST` | `/servicePrincipals/microsoft.graph.agentIdentityBlueprintPrincipal` |
| 创建 Agent Identity | `POST` | `/servicePrincipals/microsoft.graph.agentIdentity` |
| 向 Blueprint 添加 FIC | `POST` | `/applications/{id}/microsoft.graph.agentIdentityBlueprint/federatedIdentityCredentials` |
| 列出 Agent Identity | `GET` | `/servicePrincipals/microsoft.graph.agentIdentity` |
| 授予应用权限 | `POST` | `/servicePrincipals/{id}/appRoleAssignments` |
| 授予委托权限 | `POST` | `/oauth2PermissionGrants` |
| 删除 Agent Identity | `DELETE` | `/servicePrincipals/{id}` |
| 删除 Blueprint | `DELETE` | `/applications/{id}` |

基础 URL：`https://graph.microsoft.com/v1.0`。

## 必需 Graph 权限

| 权限 | 用途 |
|---------|---------|
| `AgentIdentityBlueprint.Create` | 创建 Blueprint |
| `AgentIdentityBlueprint.ReadWrite.All` | 读取/更新 Blueprint |
| `AgentIdentityBlueprintPrincipal.Create` | 创建 BlueprintPrincipal |
| `AgentIdentity.Create.All` | 创建 Agent Identity |
| `AgentIdentity.ReadWrite.All` | 读取/更新 Agent Identity |
| `Application.ReadWrite.All` | 对应用程序对象进行 Blueprint CRUD |
| `AppRoleAssignment.ReadWrite.All` | 授予应用权限 |
| `DelegatedPermissionGrant.ReadWrite.All` | 授予委托权限 |

授予管理同意（应用权限所必需）：

```bash
az ad app permission admin-consent --id <client-id>
```

管理员同意后，令牌在 30–120 秒内可能不包含新声明——请使用指数退避重试。

## 最佳实践

1. **始终在 Blueprint 之后创建 BlueprintPrincipal** —— 不会自动创建。
2. **使用类型化端点**（`/applications/microsoft.graph.agentIdentityBlueprint`），而非使用原始 `/applications` 和 `@odata.type`。
3. **凭证位于 Blueprint 上** —— Agent Identity 无法持有密钥/证书（`PropertyNotCompatibleWithAgentIdentity`）。
4. **每个 Graph 请求包含 `OData-Version: 4.0`**。
5. **生产环境使用 Workload Identity Federation** —— 本地开发仅使用客户端密钥。
6. **在 Blueprint 上设置 `identifierUris: ["api://{appId}"]`**，在 OAuth2 范围解析之前执行。
7. **切勿使用 Azure CLI 令牌** 调用 Agent Identity API —— `Directory.AccessAsUser.All` 会导致硬性 403。
8. **使用 `fmi_path`** 并配合 `client_credentials` —— 切勿使用 RFC 8693 `urn:ietf:params:oauth:grant-type:token-exchange`（将返回 `AADSTS82001`）。
9. **交换的两个步骤始终使用 `/.default` 范围** —— 使用单独范围将失败。
10. **跨租户流程中，步骤 1 指向 Agent Identity 的主租户。**
11. **按 Agent Identity 授予权限**，而非授予 BlueprintPrincipal。
12. **处理权限传播延迟** —— 管理员同意后，用 30–120 秒的退避重试 403 错误。
13. **将 Entra SDK for AgentID 保留在 localhost** —— 切勿通过 LoadBalancer 或 Ingress 暴露。

## 故障排除

| 错误 | 原因 | 解决方法 |
|-------|-------|------|
| `AADSTS82001` | 使用了 RFC 8693 token-exchange 授权 | 使用 `client_credentials` 配合 `fmi_path` |
| `AADSTS700211` | 步骤 1 父令牌指向了错误租户 | 指向 Agent Identity 的主租户 |
| `AADSTS50013` | OBO 用户令牌指向了 Graph，而非 Blueprint | 使用 `api://{blueprint_app_id}/access_as_user` |
| `AADSTS65001` | 缺少授权或使用了单独范围 | 使用 `/.default` 并验证 `oauth2PermissionGrants` |
| `403 Authorization_RequestDenied` | 此 Agent Identity 上没有授权 | 通过 `appRoleAssignments` 或 `oauth2PermissionGrants` 添加 |
| `PropertyNotCompatibleWithAgentIdentity` | 尝试在 Agent Identity SP 上添加凭证 | 将凭证放在 Blueprint 上 |
| `Agent Blueprint Principal does not exist` | 未创建 BlueprintPrincipal | 核心工作流的步骤 2 |
| `AADSTS650051`（管理员同意时） | 部分同意已创建了 SP | 通过 `appRoleAssignments` 直接授予 |

## 参考资料

| 文件 | 内容 |
|------|----------|
| [references/runtime-token-exchange.md](references/runtime-token-exchange.md) | 两步 `fmi_path` 交换：自主 + OBO，跨租户 |
| [references/oauth2-token-flow.md](references/oauth2-token-flow.md) | MI + WIF（生产环境）和客户端密钥（本地开发） |
| [references/obo-blueprint-setup.md](references/obo-blueprint-setup.md) | 将 Blueprint 配置为 OBO 的 OAuth2 API |
| [references/sdk-sidecar.md](references/sdk-sidecar.md) | Microsoft Entra SDK for AgentID —— 架构、配置、端点 |
| [references/sdk-sidecar-deployment.md](references/sdk-sidecar-deployment.md) | SDK 代码模式（Python/TypeScript），Docker/Kubernetes 清单，安全，故障排除 |
| [references/known-limitations.md](references/known-limitations.md) | 按类别组织的已记录限制 |

### 外部链接

| 资源 | URL |
|---------------|-----|
| Agent ID 设置指南 | https://learn.microsoft.com/en-us/entra/agent-id/identity-platform/agent-id-setup-instructions |
| AI 引导设置 | https://learn.microsoft.com/en-us/entra/agent-id/identity-platform/agent-id-ai-guided-setup |
| Microsoft Entra SDK for AgentID | https://learn.microsoft.com/en-us/entra/msidweb/agent-id-sdk/overview |
| Microsoft.Identity.Web.AgentIdentities (.NET) | https://github.com/AzureAD/microsoft-identity-web/blob/master/src/Microsoft.Identity.Web.AgentIdentities/README.AgentIdentities.md |
