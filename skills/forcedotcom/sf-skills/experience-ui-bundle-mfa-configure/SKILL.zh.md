---
name: experience-ui-bundle-mfa-configure
description: 为 Salesforce 体验站点用户配置多因素认证 (MFA)。触发条件如下：用户希望在社区上启用 MFA、为门户用户强制执行双因素认证、为 React 体验站点/网络应用添加 MFA、配置 ForceTwoFactor 权限、为外部用户创建 MFA 权限集，或解决登录时 MFA 未显示的问题。此外，在以下情况下也会触发：MFA 社区、双因素门户、ForceTwoFactor 权限集、MFA 体验云、MFA React 站点、身份验证社区、MFA 体验站点、ForceTwoFactor 权限set-meta.xml、MFA 权限set-meta.xml。不触发的情况包括：为内部用户配置全局 MFA（路径为 Setup > Identity Verification）、构建自定义登录 UI 组件（使用 experience-ui-bundle-frontend-generate）、生成不含 MFA 上下文的通用权限集（使用 platform-permission-set-generate）。
---

# 在体验站点上启用 MFA

为体验站点（社区）用户启用多因素身份验证，方法是部署正确的权限集并验证平台处理的 MFA 挑战流程。

## 范围

**在范围内：**
- 为社区用户部署 `ForceTwoFactor` 权限集
- 部署 `ApiEnabled` 权限集（用于登录后 API 调用，是必需的）
- 将权限集分配给社区用户
- 排查登录时 MFA 未出现的问题
- 通过 NetworkBranding 元数据自定义 MFA/登录页面品牌

**不在范围内（应委托他人处理）：**
- 构建自定义登录 UI → `experience-ui-bundle-frontend-generate`
- 创建通用权限集 → `platform-permission-set-generate`
- 分配权限集（如果已部署）→ `dx-org-permission-set-assign`
- 将元数据部署到组织 → `platform-metadata-deploy`
- 内部 Salesforce 用户的组织范围 MFA → 设置 > 身份验证（这不是一项技能）

---

## 前置条件

在使用此技能之前，请确保以下条件已就绪：

| 前置条件 | 原因 |
|-------------|-----|
| **已部署并激活的 Experience Cloud 站点** | MFA 适用于社区登录——没有站点则没有需要保护的登录流程 |
| **存在社区用户**（或将要自注册） | 权限集分配给社区用户；站点必须具有启用的社区配置文件 |
| **已启用 Customer Community 或 Customer Community Login 许可证** | 社区用户配置文件所需——没有它，用户创建和配置文件部署将失败 |
| **网络/站点至少发布一次** | 站点必须可通过其 URL 访问，以便登录 + MFA 挑战出现 |

> **注意：** 此技能不处理组织设置、许可证提供或 Experience Cloud 站点创建。如果缺少这些前置条件，请先通过 设置 > 数字体验 > 所有站点 > 新建 来设置它们，或部署您站点的基座应用包。

---

## 必需的输入

在操作前收集：

| 输入 | 如何确定 |
|-------|-----------------|
| **目标组织** | `sf` CLI 命令的组织别名 |
| **站点名称** | Experience Site (网络) 名称——通过 `SELECT Id, Name FROM Network` 解析（见步骤 1）；这是站点/网络名称，而不是 `uiBundles/` 应用名称 |
| **社区用户** | 要分配 MFA 的哪些用户或配置文件 |

---

## 关键领域知识

这些事实并不明显，并且经常引起混淆：

| 事实 | 详情 |
|------|--------|
| **不需要自定义 UI** | 平台渲染 MFA 挑战页面——不需要 React/LWC 组件 |
| **ForceTwoFactor 权限** | 强制社区用户在登录时使用 MFA 的唯一方法 |
| **组织身份验证验证复选框** | 不强制社区/门户用户使用 MFA——仅适用于内部用户 |
| **vforcesite 域名** | MFA 挑战页面始终从底层的 Force.com 站点域名提供——这是预期的 |
| **始终部署 ApiEnabled** | React 体验站点会进行登录后 REST/Connect API 调用 (`sdk.graphql`, `sdk.fetch`)；没有 `ApiEnabled` 它们会以 `API_DISABLED_FOR_ORG` 失败 |
| **社交登录 / SSO 与 MFA 分开** | React 站点通过内置的社交登录组件（随 264 提供）渲染配置的认证提供程序——由认证提供程序设置驱动，而不是由 MFA 权限集驱动。见 `references/social-login.md`。 |
| **登录页面品牌适用于 React 站点** | 自 264 起，站点容器在设置中显示 NetworkBranding “登录和注册”部分，因此可以在 UI 中自定义标志/颜色/页脚——元数据 API 仍然有效。 |

---

## 工作流

### 步骤 1：解析目标站点（网络）

这些是 React 体验站点，因此 **两者** 权限集始终部署——`ForceTwoFactor`（强制 MFA）和 `ApiEnabled`（React 站点进行登录后 API 调用）。

从组织中解析体验站点的真实名称和 Id——**不要**假设 `uiBundles/` 应用文件夹名称是站点名称。它们经常不同，站点名称必须来自组织（部署目标），而不是本地项目。<site-name> 和 <NETWORK_ID> 下面来自这里：

```bash
sf data query --target-org <org-alias> \
  --query "SELECT Id, Name FROM Network" --json
```

- 一个站点 → 使用其 `Name` 作为 `<site-name>` 和 `Id` 作为 `<NETWORK_ID>`。
- 多个站点 → 询问用户选择哪一个（显示名称）。
- 零个站点 → 站点尚未部署；停止并告知用户（见前置条件）。

### 步骤 2：生成权限集文件

首先，检测项目的源目录：

```bash
jq -r '.packageDirectories[0].path + "/main/default"' sfdx-project.json
```

将结果用作 `<source-dir>`（例如 `force-app/main/default`）用于以下所有命令。

写入 **两者** 权限集（React 体验站点始终需要两者）：

1. **读取** `assets/MFA_Required_For_Community.permissionset-meta.xml`
2. 写入到用户项目中的 `<source-dir>/permissionsets/MFA_Required_For_Community.permissionset-meta.xml`
3. **读取** `assets/API_Enabled_For_Community.permissionset-meta.xml`
4. 写入到 `<source-dir>/permissionsets/API_Enabled_For_Community.permissionset-meta.xml`

### 步骤 3：部署到组织

```bash
sf project deploy start \
  --source-dir <source-dir>/permissionsets \
  --target-org <org-alias> --test-level NoTestRun
```

### 步骤 3b：验证社区配置文件是网络成员

在将权限集分配给用户之前，请验证社区配置文件已注册为站点成员。如果没有，社区用户根本无法登录（并且 MFA 将永远不会触发）。

1. **查询当前网络成员：**

```bash
sf data query --target-org <org-alias> \
  --query "SELECT Id, ParentId FROM NetworkMemberGroup WHERE NetworkId = '<NETWORK_ID>'" --json
```

2. **检查社区配置文件是否在列表中：**

```bash
sf data query --target-org <org-alias> \
  --query "SELECT Id, Name FROM Profile WHERE UserType IN ('CspLitePortal', 'PowerCustomerSuccess') AND Name LIKE '%Community%'" --json
```

3. **如果配置文件不是成员**，将其添加到 `.network-meta.xml`：

```xml
<networkMemberGroups>
    <!-- 替换为上述步骤 3b 查询中的社区配置文件名称 -->
    <profile>YOUR_COMMUNITY_PROFILE_NAME</profile>
    <!-- 现有条目 -->
</networkMemberGroups>
```

4. **部署更新的网络元数据：**

```bash
sf project deploy start \
  --source-dir <source-dir>/networks \
  --target-org <org-alias> --test-level NoTestRun
```

> **重要提示：** 如果社区配置文件不是网络的成员，则具有该配置文件的用户将无法登录——这意味着即使正确分配了权限集，MFA 也永远不会被触发。这是新部署组织中常见的配置错误。

### 步骤 3c：验证访客配置文件具有登录 Apex 类访问权限

登录页面作为 **访客用户**（未身份验证）运行。如果访客配置文件没有访问登录 Apex 类的权限，用户将收到 `FORBIDDEN: You do not have access to the Apex class named: UIBundleLogin` 并永远无法到达 MFA 挑战页面。

1. **查找站点访客用户配置文件：**

```bash
sf data query --target-org <org-alias> \
  --query "SELECT Id, Username, Profile.Name, Profile.Id FROM User WHERE UserType = 'Guest' AND IsActive = true" --json
```

2. **授予任何缺失的 UIBundle 登录类访问权限。** 六个类是 `UIBundleLogin`, `UIBundleAuthUtils`, `UIBundleForgotPassword`, `UIBundleChangePassword`, `UIBundleRegistration`, 和 `UIBundleSocialLoginConfig`。运行 `references/setup.md` 中的匿名 Apex（“授予访客配置文件 Apex 类访问权限”）——它比较现有访问权限并仅插入缺少的部分——或者将 `<classAccess>` 条目部署到访客配置文件元数据 XML 中。

> **重要提示：** 这不是 MFA 特定的，但如果没有，登录页面本身就会损坏。该技能必须验证此内容以确保 MFA 实际上可以被触发。新部署组织中访客配置文件通常没有完整的类访问权限。

### 步骤 4：分配权限集

查找社区用户：

```bash
sf data query --target-org <org-alias> \
  --query "SELECT Id, Username, Name, Profile.Name FROM User WHERE UserType IN ('CspLitePortal', 'PowerCustomerSuccess', 'CustomerSuccess') AND IsActive = true" --json
```

#### 如果存在社区用户：

查找权限集 ID：

```bash
sf data query --target-org <org-alias> \
  --query "SELECT Id, Name FROM PermissionSet WHERE Name IN ('MFA_Required_For_Community', 'API_Enabled_For_Community')" --json
```

分配给每个用户：

```bash
sf data create record --target-org <org-alias> --sobject PermissionSetAssignment \
  --values "AssigneeId='<USER_ID>' PermissionSetId='<PERM_SET_ID>'" --json
```

或者，委托给 `dx-org-permission-set-assign` 技能：

```bash
sf org assign permset --name MFA_Required_For_Community --target-org <org-alias> --json
sf org assign permset --name API_Enabled_For_Community --target-org <org-alias> --json
```

#### 如果未找到社区用户：

询问用户：*"在此组织中未找到活动的社区用户。您希望我创建一个测试社区用户以便您可以验证 MFA 是否正常工作吗？"**

如果用户同意，创建测试社区用户：

1. **查找社区配置文件** 从站点的网络配置：

```bash
sf data query --target-org <org-alias> \
  --query "SELECT Id, Name FROM Profile WHERE UserType IN ('CspLitePortal', 'PowerCustomerSuccess') AND Name LIKE '%Customer Community%'" --json
```

2. **创建一个账户**（作为社区用户父级所需）：

```bash
sf data create record --target-org <org-alias> --sobject Account \
  --values "Name='MFA Test Account'" --json
```

3. **创建一个联系人**（链接到账户）：

```bash
sf data create record --target-org <org-alias> --sobject Contact \
  --values "FirstName='MFA' LastName='Test User' Email='mfa.testuser@<site-name>.test' AccountId='<ACCOUNT_ID>'" --json
```

4. **创建用户** 使用社区配置文件：

```bash
sf data create record --target-org <org-alias> --sobject User \
  --values "FirstName='MFA' LastName='Test User' Email='mfa.testuser@<site-name>.test' Username='mfa.testuser@<site-name>.test' Alias='mfatest' ProfileId='<PROFILE_ID>' ContactId='<CONTACT_ID>' EmailEncodingKey='UTF-8' LanguageLocaleKey='en_US' LocaleSidKey='en_US' TimeZoneSidKey='America/Los_Angeles'" --json
```

5. **为测试用户设置密码**：

```bash
sf data update record --target-org <org-alias> --sobject User \
  --where "Username='mfa.testuser@<site-name>.test'" \
  --values "IsActive=true" --json
```

```bash
sf org generate password --target-org <org-alias> --on-behalf-of mfa.testuser@<site-name>.test --json
```

6. **为新建用户分配两个权限集**：

```bash
sf org assign permset --name MFA_Required_For_Community --target-org <org-alias> --on-behalf-of mfa.testuser@<site-name>.test --json
sf org assign permset --name API_Enabled_For_Community --target-org <org-alias> --on-behalf-of mfa.testuser@<site-name>.test --json
```

向用户报告凭证以便他们测试：
> "创建了测试用户：`mfa.testuser@<site-name>.test`，密码：`<generated-password>`。您可以使用这些凭证在您的站点上验证 MFA。"

> **重要提示：** 社区用户需要账户 → 联系人 → 用户层次结构。在社区配置文件上创建用户而没有链接的联系人将失败。

### 步骤 5：将权限集注册为站点成员（networkMemberGroups）

> `networkMemberGroups` 是一个 *成员资格/访问门*——它列出了持有者的配置文件和权限集，其持有者被视为站点成员。它**不**将 MFA 分配给用户。分配发生在步骤 4（针对每个用户）；在此处注册集，以便分配的用户仍然被视为站点成员。

1. 在项目中查找现有的 `.network-meta.xml`：

```bash
find . -name "*.network-meta.xml" -not -path "*/node_modules/*"
```

2. 读取文件并定位 `<networkMemberGroups>` 部分。

3. 添加权限集条目（如果尚未存在）：

```xml
<networkMemberGroups>
    <!-- 替换为步骤 3b 查询中的社区配置文件名称 -->
    <profile>YOUR_COMMUNITY_PROFILE_NAME</profile>
    <!-- 添加 MFA 和 API 权限集 -->
    <permissionSet>MFA_Required_For_Community</permissionSet>
    <permissionSet>API_Enabled_For_Community</permissionSet>
</networkMemberGroups>
```

> **重要提示：** 网络元数据部署是声明性的——你部署的任何内容都将成为完整状态。**不要**从零开始创建新的 `.network-meta.xml`。始终读取现有文件并添加条目到其中。

4. 部署更新的网络元数据：

```bash
sf project deploy start \
  --source-dir <source-dir>/networks \
  --target-org <org-alias> --test-level NoTestRun
```

### 步骤 6：发布并验证

```bash
sf community publish --name "<site-name>" --target-org <org-alias>
```

验证步骤：
1. 打开隐身浏览器
2. 导航到站点登录页面
3. 输入凭证 → MFA 挑战页面应出现（在 vforcesite 域名上）
4. 完成MFA → 应该跳转到站点，已登录

---

## 规则

| 规则 | 原因 |
|------|-----------|
| **永远不要使用组织范围的 Identity Verification 复选框用于社区 MFA** | 它仅影响内部用户——对社区登录没有影响 |
| **始终为 React 站点部署 `ApiEnabled`** | 登录后 API 调用 (`sdk.graphql`, `sdk.fetch`) 没有它将失败 |
| **权限集名称必须精确——不要重命名** | `MFA_Required_For_Community` 和 `API_Enabled_For_Community` 是规范名称 |
| **不要构建自定义 MFA UI 组件** | 平台处理整个 MFA 挑战流程——自定义 UI 会重复并冲突 |
| **始终在测试前分配** | 部署本身不会激活 MFA——需要将特定用户分配权限 |

---

## 易犯错误

| 症状 | 原因 | 修复 |
|---------|-------|-----|
| 登录时没有 MFA 挑战 | 未将 `ForceTwoFactor` 权限分配给用户 | 验证用户存在 `PermissionSetAssignment` |
| 登录后出现 `API_DISABLED_FOR_ORG` | 缺少 `ApiEnabled` 权限 | 分配 `API_Enabled_For_Community` 权限集 |
| MFA 页面显示默认 Salesforce 品牌标志 | 未部署 `NetworkBranding` 元数据 | 阅读 `references/branding.md` 并部署自定义品牌 |
| MFA 页面 URL 中显示 `vforcesite` | 预期行为——不是错误 | 平台从 Force.com 站点域名提供登录/MFA——这是正常的 |
| 身份验证已启用但社区 MFA 未触发 | 使用了错误的机制 | 通过权限集使用 `ForceTwoFactor` 而不是 |
| 用户已有 MFA 但未被挑战 | 存在活动会话 | 在隐身/隐私浏览器中测试 |
| 权限集已部署但 MFA 未强制 | 已部署但未分配 | 运行分配步骤——部署 != 分配 |
| 组织中未找到社区用户 | 用户尚未创建或自注册 | 提供创建测试社区用户（账户 → 联系人 → 用户层次结构）以进行验证。权限集已部署且 `networkMemberGroups` 已更新——当用户存在时，组织已为 MFA 准备就绪。 |
| 新用户未被 MFA 自动保护 | `networkMemberGroups` 仅定义站点成员——它不将权限集分配给用户 | 将 `MFA_Required_For_Community` + `API_Enabled_For_Community` 分配给每个需要它的用户（步骤 4） |
| `FORBIDDEN: You do not have access to the Apex class named: UIBundleLogin` | 站点访客配置文件缺少 Apex 类访问权限 | 运行步骤 3c 以授予访客配置文件对所有 UIBundle 登录类的访问权限 |
| 社区用户无法登录（无声重定向或收到 `portal user email settings` 错误） | 社区配置文件不是网络成员，或者电子邮件可交付性未设置为 All Email | 将配置文件添加到 `.network-meta.xml` `<networkMemberGroups>` 并重新部署（步骤 3b）。验证电子邮件可交付性设置为“所有电子邮件”在设置 → 电子邮件 → 可交付性。 |

---

## 输出预期

用户项目中生成的文件：

| 文件 | 时间 |
|------|------|
| `permissionsets/MFA_Required_For_Community.permissionset-meta.xml` | 总是 |
| `permissionsets/API_Enabled_For_Community.permissionset-meta.xml` | 总是 |

> **在总结所做的工作时，不要声称将权限集添加到
> `<networkMemberGroups>`（或更新网络）会导致新用户或自注册用户自动获取MFA。** 它不会 — `networkMemberGroups` 仅定义站点成员资格。MFA 仅对已明确分配权限集的用户强制执行（步骤 4）。将网络更改报告为“将权限集注册为站点成员”，而不是自动分配。

---

## 跨技能集成

| 时间 | 委派给 |
|------|-------------|
| 用户只需分配（已部署的） | `dx-org-permission-set-assign` |
| 用户需要部署所有项目元数据 | `platform-metadata-deploy` |
| 用户希望自定义登录页面 UI | `experience-ui-bundle-frontend-generate` |
| 用户需要创建一个新的通用权限集 | `platform-permission-set-generate` |
| 用户希望 IDP/社交登录（与 MFA 不同） | 在 React 站点上受支持 — 内置的社交登录组件会自动在登录页面上渲染链接的身份提供程序。在设置中创建身份提供程序，然后通过 `experience-ui-bundle-deploy` 社交登录步骤（`org-setup.config.json` 中的 `socialLogin`）将它们链接到 React 站点 — React SSO 管理界面被隐藏，因此链接是程序化的，而不是设置中的点击路径。参见 `references/social-login.md`。 |

---

## 参考文件索引

| 文件 | 何时阅读 |
|------|-------------|
| `assets/MFA_Required_For_Community.permissionset-meta.xml` | 步骤 2 — 将权限集写入项目 |
| `assets/API_Enabled_For_Community.permissionset-meta.xml` | 步骤 2 — 总是部署 |
| `references/branding.md` | 当用户希望自定义 MFA/登录页面外观时 |
| `references/social-login.md` | 当用户希望在 React 站点上 alongside 或 instead of MFA 添加 IDP/SSO/社交登录时 |
| `references/setup.md` | 步骤 3–5 — 详细的分配、网络成员资格和发布参考 |
