# 在 Microsoft Entra Agent ID 中创建代理用户

## 概述

**代理用户**是 Microsoft Entra ID 中的专用用户身份，它使 AI 代理能够充当数字工作者。它允许代理访问那些严格要求用户身份的 API 和服务（例如，Exchange 邮箱、Teams、组织结构图），同时保持适当的安全边界。

代理用户会接收带有 `idtyp=user` 的令牌，而常规的代理身份会接收 `idtyp=app`。

---

## 前置条件

- 具备 Agent ID 功能的 **Microsoft Entra 租户**
- 从 **代理身份蓝图**创建的 **代理身份**（类型为 `ServiceIdentity` 的服务主体）
- 以下权限之一：
  - `AgentIdUser.ReadWrite.IdentityParentedBy`（最小权限）
  - `AgentIdUser.ReadWrite.All`
  - `User.ReadWrite.All`
- 调用者必须至少具有 **Agent ID 管理员**角色（在委派场景中）

> **重要提示**：`identityParentId` 必须引用一个真正的代理身份（通过代理身份蓝图创建的），而不是常规的应用服务主体。您可以通过检查服务主体具有 `@odata.type: #microsoft.graph.agentIdentity` 和 `servicePrincipalType: ServiceIdentity` 来进行验证。

---

## 架构

```
代理身份蓝图（应用程序模板）
    │
    ├── 代理身份（服务主体 - ServiceIdentity）
    │       │
    │       └── 代理用户（用户 - agentUser） ← 1:1 关系
    │
    └── 代理身份蓝图主体（租户中的服务主体）
```

| 组件 | 类型 | 令牌声明 | 目的 |
|---|---|---|---|
| 代理身份 | 服务主体 | `idtyp=app` | 后端/API 操作 |
| 代理用户 | 用户 (`agentUser`) | `idtyp=user` | 在 M365 中充当数字工作者 |

---

## 第 1 步：验证代理身份是否存在

在创建代理用户之前，请确认代理身份是正确的 `agentIdentity` 类型：

```http
GET https://graph.microsoft.com/beta/servicePrincipals/{agent-identity-id}
Authorization: Bearer <token>
```

验证响应是否包含：
```json
{
  "@odata.type": "#microsoft.graph.agentIdentity",
  "servicePrincipalType": "ServiceIdentity",
  "agentIdentityBlueprintId": "<blueprint-id>"
}
```

### PowerShell

```powershell
Connect-MgGraph -Scopes "Application.Read.All" -TenantId "<tenant>" -UseDeviceCode -NoWelcome
Invoke-MgGraphRequest -Method GET `
  -Uri "https://graph.microsoft.com/beta/servicePrincipals/<agent-identity-id>" | ConvertTo-Json -Depth 3
```

> **常见错误**：使用应用程序注册的 `appId` 或常规应用程序服务主体的 `id` 将失败。只有从蓝图创建的代理身份才有效。

---

## 第 2 步：创建代理用户

### HTTP 请求

```http
POST https://graph.microsoft.com/beta/users/microsoft.graph.agentUser
Content-Type: application/json
Authorization: Bearer <token>

{
  "accountEnabled": true,
  "displayName": "My Agent User",
  "mailNickname": "my-agent-user",
  "userPrincipalName": "my-agent-user@yourtenant.onmicrosoft.com",
  "identityParentId": "<agent-identity-object-id>"
}
```

### 必填属性

| 属性 | 类型 | 描述 |
|---|---|---|
| `accountEnabled` | Boolean | `true` 以启用账户 |
| `displayName` | String | 人类友好的名称 |
| `mailNickname` | String | 邮件别名（不能有空格/特殊字符） |
| `userPrincipalName` | String | UPN — 必须在租户中唯一 (`alias@verified-domain`) |
| `identityParentId` | String | 父代理身份的对象 ID |

### PowerShell

```powershell
Connect-MgGraph -Scopes "User.ReadWrite.All" -TenantId "<tenant>" -UseDeviceCode -NoWelcome

$body = @{
  accountEnabled    = $true
  displayName       = "My Agent User"
  mailNickname      = "my-agent-user"
  userPrincipalName = "my-agent-user@yourtenant.onmicrosoft.com"
  identityParentId  = "<agent-identity-object-id>"
} | ConvertTo-Json

Invoke-MgGraphRequest -Method POST `
  -Uri "https://graph.microsoft.com/beta/users/microsoft.graph.agentUser" `
  -Body $body -ContentType "application/json" | ConvertTo-Json -Depth 3
```

### 关键提示

- **无密码** — 代理用户不能有密码。它们通过其父代理身份的凭据进行身份验证。
- **1:1 关系** — 每个代理身份最多只能有一个代理用户。尝试创建第二个将返回 `400 Bad Request`。
- `userPrincipalName` 必须唯一。不要重用现有用户的 UPN。

---

## 第 3 步：分配经理（可选）

分配经理允许代理用户出现在组织结构图（例如，Teams）中。

```http
PUT https://graph.microsoft.com/beta/users/{agent-user-id}/manager/$ref
Content-Type: application/json
Authorization: Bearer <token>

{
  "@odata.id": "https://graph.microsoft.com/beta/users/{manager-user-id}"
}
```

### PowerShell

```powershell
$managerBody = '{"@odata.id":"https://graph.microsoft.com/beta/users/<manager-user-id>"}'
Invoke-MgGraphRequest -Method PUT `
  -Uri "https://graph.microsoft.com/beta/users/<agent-user-id>/manager/`$ref" `
  -Body $managerBody -ContentType "application/json"
```

---

## 第 4 步：设置使用位置并分配许可证（可选）

代理用户需要许可证才能拥有邮箱、Teams 存在等。必须先设置使用位置。

### 设置使用位置

```http
PATCH https://graph.microsoft.com/beta/users/{agent-user-id}
Content-Type: application/json
Authorization: Bearer <token>

{
  "usageLocation": "US"
}
```

### 列出可用许可证

```http
GET https://graph.microsoft.com/beta/subscribedSkus?$select=skuPartNumber,skuId,consumedUnits,prepaidUnits
Authorization: Bearer <token>
```

需要 `Organization.Read.All` 权限。

### 分配许可证

```http
POST https://graph.microsoft.com/beta/users/{agent-user-id}/assignLicense
Content-Type: application/json
Authorization: Bearer <token>

{
  "addLicenses": [
    { "skuId": "<sku-id>" }
  ],
  "removeLicenses": []
}
```

### PowerShell（全部一次性）

```powershell
Connect-MgGraph -Scopes "User.ReadWrite.All","Organization.Read.All" -TenantId "<tenant>" -NoWelcome

# 设置使用位置
Invoke-MgGraphRequest -Method PATCH `
  -Uri "https://graph.microsoft.com/beta/users/<agent-user-id>" `
  -Body '{"usageLocation":"US"}' -ContentType "application/json"

# 分配许可证
$licenseBody = '{"addLicenses":[{"skuId":"<sku-id>"}],"removeLicenses":[]}'
Invoke-MgGraphRequest -Method POST `
  -Uri "https://graph.microsoft.com/beta/users/<agent-user-id>/assignLicense" `
  -Body $licenseBody -ContentType "application/json"
```

> **提示**：您也可以通过 **Entra 管理中心**在身份 → 用户 → 所有用户 → 选择代理用户 → 许可证和应用来分配许可证。

---

## 部署时间

| 服务 | 预计时间 |
|---|---|
| Exchange 邮箱 | 5–30 分钟 |
| Teams 可用性 | 15 分钟 – 24 小时 |
| 组织结构图 / 人员搜索 | 最长 24–48 小时 |
| SharePoint / OneDrive | 5–30 分钟 |
| 全局地址列表 | 最长 24 小时 |

---

## 代理用户功能

- ✅ 添加到 Microsoft Entra 组（包括动态组）
- ✅ 访问仅限用户的 API (`idtyp=user` 令牌)
- ✅ 拥有邮箱、日历和联系人
- ✅ 参与 Teams 聊天和频道
- ✅ 出现在组织结构图和人员搜索中
- ✅ 添加到管理单元
- ✅ 分配许可证

## 代理用户安全限制

- ❌ 不能有密码、密钥或交互式登录
- ❌ 不能分配特权管理员角色
- ❌ 不能添加到可分配角色的组
- ❌ 默认权限与访客用户类似
- ❌ 不支持自定义角色分配

---

## 故障排除

| 错误 | 原因 | 解决方法 |
|---|---|---|
| `Agent user IdentityParent does not exist` | `identityParentId` 指向不存在的或非代理身份的对象 | 验证 ID 是 `agentIdentity` 服务主体，而不是常规应用 |
| `400 Bad Request`（identityParentId 已链接） | 代理身份已经有一个代理用户 | 每个代理身份只支持一个代理用户 |
| `409 Conflict` 在 UPN 上 | `userPrincipalName` 已被占用 | 使用唯一的 UPN |
| 许可证分配失败 | 未设置使用位置 | 在分配许可证前设置 `usageLocation` |

---

## 参考

- [代理身份](https://learn.microsoft.com/en-us/entra/agent-id/identity-platform/agent-identities)
- [代理用户](https://learn.microsoft.com/en-us/entra/agent-id/identity-platform/agent-users)
- [代理服务主体](https://learn.microsoft.com/en-us/entra/agent-id/identity-platform/agent-service-principals)
- [创建代理身份蓝图](https://learn.microsoft.com/en-us/entra/agent-id/identity-platform/create-blueprint)
- [创建代理身份](https://learn.microsoft.com/en-us/entra/agent-id/identity-platform/create-delete-agent-identities)
- [agentUser 资源类型（Graph API）](https://learn.microsoft.com/en-us/graph/api/resources/agentuser?view=graph-rest-beta)
- [Create agentUser（Graph API）](https://learn.microsoft.com/en-us/graph/api/agentuser-post?view=graph-rest-beta)
