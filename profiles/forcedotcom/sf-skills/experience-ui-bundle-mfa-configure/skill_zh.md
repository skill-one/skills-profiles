# 在体验站点上启用 MFA

为体验站点（社区）用户启用多因素身份验证，方法是部署正确的权限集并验证平台管理的 MFA 挑战流程。

## 范围

**在范围内：**
- 为社区用户部署 `ForceTwoFactor` 权限集
- 部署 `ApiEnabled` 权限集（用于登录后 API 调用，是必需的）
- 将权限集分配给社区用户
- 排查登录时 MFA 未出现的问题
- 通过 NetworkBranding 元数据自定义 MFA/登录页面品牌

**不在范围内（转交他人处理）：**
- 构建自定义登录 UI → `experience-ui-bundle-frontend-generate`
- 创建通用权限集 → `platform-permission-set-generate`
- 分配权限集（如果已部署）→ `dx-org-permission-set-assign`
- 将元数据部署到组织 → `platform-metadata-deploy`
- 内部 Salesforce 用户的组织范围 MFA → 设置 > 身份验证（这不是一项技能）

---

## 前置条件

在使用此技能之前，请确保以下内容已就绪：

| 前置条件 | 原因 |
|-------------|-----|
| **已部署并激活的体验云站点** | MFA 适用于社区登录——没有站点则没有需要保护的登录流程 |
| **存在社区用户**（或将要自行注册） | 权限集分配给社区用户；站点必须具有启用的社区配置文件 |
| **已启用客户社区或客户社区登录许可证** | 社区用户配置文件所需的许可证——没有它，用户创建和配置文件部署将失败 |
| **网络/站点至少发布一次** | 站点必须在其 URL 上可访问，以便登录 + MFA 挑战出现 |

> **注意：** 此技能不处理组织设置、许可证提供或体验云站点创建。如果缺少这些前置条件，请先通过 设置 > 数字体验 > 所有站点 > 新建 来设置它们，或部署您站点的基座应用包。

---

## 必须输入的值

在操作前收集：

| 输入 | 如何确定 |
|-------|-----------------|
| **目标组织** | `sf` CLI 命令的组织别名 |
| **站点名称** | 体验站点（网络）名称——通过 `SELECT Id, Name FROM Network`（见步骤 1）解析；这是站点/网络名称，不是 `uiBundles/` 应用名称 |
| **社区用户** | 要分配 MFA 的用户或配置文件 |

---

## 关键领域知识

这些事实并不明显，并且经常引起混淆：

| 事实 | 详情 |
|------|--------|
| **不需要自定义 UI** | 平台渲染 MFA 挑战页面——不需要 React/LWC 组件 |
| **ForceTwoFactor 权限** | 强制社区用户在登录时使用 MFA 的唯一方法 |
| **组织身份验证复选框** | 不强制社区/门户用户使用 MFA——仅适用于内部用户 |
| **vforcesite 域** | MFA 挑战页面始终从底层的 Force.com 站点域提供——这是预期的行为 |
| **始终部署 ApiEnabled** | React 体验站点会进行登录后 REST/Connect API 调用（`sdk.graphql`，`sdk.fetch`）；没有 `ApiEnabled`，它们会以 `API_DISABLED_FOR_ORG` 失败 |
| **社交登录 / SSO 与 MFA 是分开的** | React 站点通过内置的社交登录组件（随 264 版本一起提供）渲染配置的认证提供程序——由认证提供程序设置驱动，而不是由 MFA 权限集驱动。参见 `references/social-login.md`。 |
| **登录页面品牌适用于 React 站点** | 自 264 版本起，网络品牌“登录和注册”部分在设置中为站点容器显示，因此可以在 UI 中自定义标志/颜色/页脚——元数据 API 仍然有效。 |

---

## 工作流程

### 步骤 1：解析目标站点（网络）

这些是 React 体验站点，因此 **两者** 权限集始终部署——`ForceTwoFactor`（强制 MFA）和 `ApiEnabled`（React 站点在登录后会进行 API 调用）。

从组织中解析体验站点的真实名称和 Id——**不要**假设 `uiBundles/` 应用文件夹名称是站点名称。它们经常不同，站点名称必须来自组织（部署目标），而不是本地项目。
下面的 `<site-name>` 和 `<NETWORK_ID>` 来自此处：

```bash
sf data query --target-org <org-alias> \
  --query "SELECT Id, Name FROM Network" --json
```

- 一个站点 → 使用其 `Name` 作为 `<site-name>`，`Id` 作为 `<NETWORK_ID>`。
- 多个站点 → 请用户选择其中一个（显示名称）。
- 零个站点 → 站点尚未部署；停止并告知用户（见前置条件）。

### 步骤 2：生成权限集文件

首先，检测项目的源目录：

```bash
jq -r '.packageDirectories[0].path + "/main/default"' sfdx-project.json
```

将结果用作 `<source-dir>`（例如 `force-app/main/default`）作为下面所有命令的 `<source-dir>`。

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

在将权限集分配给用户之前，请验证社区配置文件已注册为站点成员。如果没有，社区用户根本无法登录（并且 MFA 永远不会触发）。

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

> **重要提示：** 如果社区配置文件不是网络的成员，则具有该配置文件的用户**无法**登录——这意味着即使权限集正确分配，MFA 也永远不会被触发。这是新部署组织中常见的配置错误。

### 步骤 3c：验证访客配置文件对登录 Apex 类的访问权限

登录页面作为 **访客用户**（未验证）运行。如果访客配置文件没有访问登录 Apex 类的权限，用户将收到 `FORBIDDEN: You do not have access to the Apex class named: UIBundleLogin` 并永远无法到达 MFA 挑战页面。

1. **查找站点访客用户配置文件：**

```bash
sf data query --target-org <org-alias> \
  --query "SELECT Id, Username, Profile.Name, Profile.Id FROM User WHERE UserType = 'Guest' AND IsActive = true" --json
```

2. **授予任何缺失的 UIBundle 登录类访问权限。** 六个类是 `UIBundleLogin`，`UIBundleAuthUtils`，`UIBundleForgotPassword`，`UIBundleChangePassword`，`UIBundleRegistration` 和 `UIBundleSocialLoginConfig`。运行 `references/setup.md` 中的匿名 Apex（“授予访客配置文件 Apex 类访问权限”）——它比较现有访问权限并仅插入缺失的部分——或者将相同的类 `<classAccess>` 条目部署到访客配置文件元数据 XML 中。

> **重要提示：** 这**不是** MFA 特定的，但如果没有它，登录页面本身就会损坏。该技能必须验证此内容以确保 MFA 实际上可以被触发。新部署的组织中常见此问题，访客配置文件未获得完整的类访问权限。

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

为每个用户分配：

```bash
sf data create record --target-org <org-alias> --sobject PermissionSetAssignment \
  --values "AssigneeId='<USER_ID>' PermissionSetId='<PERM_SET_ID>'" --json
```

或者，转交给 `dx-org-permission-set-assign` 技能：

```bash
sf org assign permset --name MFA_Required_For_Community --target-org <org-alias> --json
sf org assign permset --name API_Enabled_For_Community --target-org <org-alias> --json
```

#### 如果未找到社区用户：

询问用户：*"在此组织中未找到活动的社区用户。您希望我创建一个测试社区用户，以便您可以验证 MFA 是否正常工作？"*

如果用户同意，创建测试社区用户：

1. **查找社区配置文件** 从站点的网络配置：

```bash
sf data query --target-org <org-alias> \
  --query "SELECT Id, Name FROM Profile WHERE UserType IN ('CspLitePortal', 'PowerCustomerSuccess') AND Name LIKE '%Customer Community%'" --json
```

2. **创建一个账户**（作为社区用户父级是必需的）：

```bash
sf data create record --target-org <org-alias> --sobject Account \
  --values "Name='MFA Test Account'" --json
```

3. **创建一个联系人**（链接到账户）：

```bash
sf data create record --target-org <org-alias> --sobject Contact \
  --values "FirstName='MFA' LastName='Test User' Email='mfa.testuser@<site-name>.test' AccountId='<ACCOUNT_ID>'" --json
```

4. **使用社区配置文件创建用户**：

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

6. **为该新用户分配两个权限集**：

```bash
sf org assign permset --name MFA_Required_For_Community --target-org <org-alias> --on-behalf-of mfa.testuser@<site-name>.test --json
sf org assign permset --name API_Enabled_For_Community --target-org <org-alias> --on-behalf-of mfa.testuser@<site-name>.test --json
```

向用户报告凭证，以便他们可以测试：
> "创建了测试用户：`mfa.testuser@<site-name>.test`，密码：`<generated-password>`。您可以使用这些凭证在您的站点上验证 MFA。"

> **重要提示：** 社区用户需要账户 → 联系人 → 用户的层次结构。在社区配置文件上创建用户而没有链接的联系人将失败。

### 步骤 5：将权限集注册为站点成员（networkMemberGroups）

> `networkMemberGroups` 是一个 *成员资格/访问门*——它列出的配置文件和权限集的持有者计为站点成员。它**不**为用户分配 MFA。分配发生在步骤 4（针对每个用户）；在此处注册集，以便分配的用户仍然计为站点成员。

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

> **重要提示：** 网络元数据部署是声明性的——你部署的任何内容都成为完整状态。**不要**从零开始创建新的 `.network-meta.xml`。始终读取现有文件并添加条目到它。

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
1. 打开无痕浏览器
2. 导航到站点登录页面
3. 输入凭证 → MFA 挑战页面应出现（在 vforcesite 域）
4. 完成验证 → 应该进入站点，已登录

---

## 规则

| 规则 | 原因 |
|------|-----------|
| **永远不要使用组织范围的 Identity Verification 复选框来为社区用户启用 MFA** | 它仅影响内部用户——对社区登录没有影响 |
| **始终为 React 站点部署 `ApiEnabled`** | 没有它，登录后的 API 调用（`sdk.graphql`，`sdk.fetch`）会失败 |
| **权限集名称必须完全匹配——不要重命名** | `MFA_Required_For_Community` 和 `API_Enabled_For_Community` 是规范名称 |
| **不要构建自定义 MFA UI 组件** | 平台处理整个 MFA 挑战流程——自定义 UI 会导致重复和冲突 |
| **始终在测试前分配** | 部署本身不会激活 MFA——需要将权限集显式分配给特定用户（步骤 4） |

---

## 易犯错误

| 症状 | 原因 | 修复 |
|---------|-------|-----|
| 登录时没有 MFA 挑战 | 未为用户分配 `ForceTwoFactor` 权限 | 验证用户是否存在 `PermissionSetAssignment` |
| 登录后出现 `API_DISABLED_FOR_ORG` | 缺少 `ApiEnabled` 权限 | 分配 `API_Enabled_For_Community` 权限集 |
| MFA 页面显示默认的 Salesforce 品牌标志 | 未部署 `NetworkBranding` 元数据 | 阅读 `references/branding.md` 并部署自定义品牌 |
| MFA 页面 URL 中包含 `vforcesite` | 预期行为——不是错误 | 平台从 Force.com 站点域提供登录/MFA——这是正常的 |
| 身份验证已启用但社区 MFA 未触发 | 使用了错误的机制 | 通过权限集使用 `ForceTwoFactor` 代替 |
| 用户已有 MFA 但未被挑战 | 存在活动会话 | 在无痕/隐私浏览器中测试 |
| 权限集已部署但 MFA 未强制执行 | 已部署但未分配 | 运行分配步骤——部署 != 分配 |
| 组织中未找到社区用户 | 用户尚未创建或自行注册 | 提供创建测试社区用户（账户 → 联系人 → 用户层次结构）以进行验证。权限集已部署且 `networkMemberGroups` 已更新——当用户存在时，组织已为 MFA 准备就绪。 |
| 新用户没有被 MFA 自动保护 | `networkMemberGroups` 仅定义站点成员资格——它不会为用户分配权限集 | 为每个需要 MFA 的用户分配 `MFA_Required_For_Community` + `API_Enabled_For_Community`（步骤 4） |
| `FORBIDDEN: You do not have access to the Apex class named: UIBundleLogin` | 站点访客配置文件缺少 Apex 类访问权限 | 运行步骤 3c 以授予访客配置文件对所有 UIBundle 登录类的访问权限 |
| 社区用户无法登录（静默重定向或收到 `portal user email settings` 错误） | 社区配置文件不是网络成员，或者电子邮件可交付性未设置为“所有电子邮件” | 将配置文件添加到 `.network-meta.xml` 的 `<networkMemberGroups>` 并重新部署（步骤 3b）。验证电子邮件可交付性设置为“所有电子邮件”在设置 → 电子邮件 → 可交付性。 |

---

## 输出预期

用户项目中生成的文件：

| 文件 | 当... |
|------|------|
| `permissionsets/MFA_Required_For_Community.permissionset-meta.xml` | 始终 |
| `permissionsets/API_Enabled_For_Community.permissionset-meta.xml` | 始终 |

> **在总结所做的工作时，不要声称添加权限集到 `<networkMemberGroups>`（或更新网络）会导致新用户或自行注册的用户自动获得 MFA。** 它不会——`networkMemberGroups` 仅定义站点成员资格。MFA 仅针对权限集已显式分配给的用户（步骤 4）强制执行。报告网络更改作为“注册了权限集作为站点成员”，而不是自动分配。
