# 部署 UI Bundle 应用

部署顺序至关重要：每一步的输出是下一步的前提条件
（先部署模式获取；先权限获取；先角色/自我注册，然后客用户必须看到的模式）。这是标准的设置序列，
从参考 `org-setup.mjs` 中移植而来。`org-setup.mjs` 行中的引用在 `references/` 中是移植来源（每个规则存在的原因）
指向那个外部参考脚本——而不是随此技能一起分发的文件——因此您不需要打开它们来运行步骤。

按顺序运行每个步骤。**每个可选步骤都是基于存在性驱动的**：如果其约定文件不存在，则干净地无操作并继续——不要编造配置。
对于两个具有破坏性/昂贵的步骤（自我注册、数据导入），
**在运行之前请先询问用户**。

## 预先收集的输入

从项目中读取这些内容；**仅对缺失的内容询问用户**：

- **目标组织** — `--target-org` 的别名/用户名。如果不明显，请询问。
- **源根** — 运行 `scripts/get-source-root.sh` 来从 `sfdx-project.json` 中解析元数据源目录
  (`packageDirectories[0].path` + `/main/default`)。如果项目文件缺失或格式不正确，它将退出非零。永远不要硬编码
  `force-app/main/default`。
- **`org-setup.config.json`**（可选）— 驱动权限集分配、角色、自我注册和社交登录。缺失的键意味着“跳过该步骤”。
  **例外**：如果文件缺失但 `permissionsets/` 有要分配的权限集，不要默默跳过——构建配置或收集等效输入
  （见步骤 4）。
- **`data-plan.json`**（可选，在项目的 `data/` 目录中）— 存在将启用数据步骤。

## 步骤 1 — 组织认证（始终）

无条件前提条件；不能跳过。如果组织已经连接
(`sf org display --target-org <org> --json` 成功)，则无操作。否则：

```bash
sf org login web --alias <org>
```

登录失败将导致整个设置在部署之前中止。

## 步骤 2 — 部署前 UI Bundle 构建

构建**每个** UI Bundle，以便在元数据部署之前 `dist/` 存在（UI Bundle 实体部署构建的输出）。对于 `uiBundles/`
下的每个 Bundle 目录：

```bash
npm install
npm run build
```

在部署 UI Bundle 且 `dist/` 缺失或源更改时运行。

## 步骤 3 — 部署元数据

如果配置了自我注册：

1. **首先部署许可证预检查**（见 `references/license-checks.md”）——它将用明确的许可证命名消息阻止部署，而不是一个神秘的失败。
2. **将自我注册配置文件添加到本地源上的 `networkMemberGroups`** — 应用 **Edit A** of `assets/network-selfreg-xml-recipe.md`。这必须在此次部署之前发生，以便配置文件作为已识别的站点成员发送；不要在这里单独部署网络文件（此次部署会发送它）。尽力而为且幂等——如果已经是成员则跳过。

然后通过将 `--source-dir` 指向解析的源根来部署整个项目（所有元数据）：

```bash
sf project deploy start --source-dir <sourceRoot> --target-org <org>
```

`<sourceRoot>` 是 `scripts/get-source-root.sh` 的值（例如 `force-app/main/default`）。始终传递 `--source-dir`。不要运行没有路径的裸 `sf project deploy start`：该命令依赖于源跟踪来决定要部署的内容，并且在没有源跟踪的组（大多数非沙盒组）中它会中止并显示 *"This org does not have source-tracking enabled … specify the files or a manifest to deploy."*。传递 `--source-dir` 会在源跟踪和未跟踪的组中部署相同的完整集，并且永远不会发出该提示。如果部署在源跟踪的组上报告冲突，请重新运行 `--ignore-conflicts` — 不要回滚或减少部署的集合。

不要手动构建 `package.xml`，组装 `--metadata-dir` mdapi 压缩文件，或以其他方式转换为元数据格式——所有这些都不需要，并且不是此流程的一部分。

超时 180 秒。必须在权限分配和模式获取之前完成——对象、字段和权限集只有在部署后才会出现在组中。

## 步骤 3b — 设置站点登出 URL（配置驱动）

仅当 `org-setup.config.json` 包含顶层 `logoutUrl` 时运行。如果不存在，则干净地无操作并说明。**非破坏性和幂等** — 无需询问。

在这里运行，在部署之后（而不是将其合并）运行，因为平台拒绝相对登出 URL (*"The logout page URL must be an absolute URL."*)，并且部署的站点相对路径（例如 `/propertyrentalapp/`）针对站点 Experience Cloud 原点解析为绝对路径——这只有在站点部署后才会存在。

为什么它很重要：一个没有 `<logoutUrl>` 的站点会将正在登出的成员发送到**组织默认站点登录页面**——在一个多站点组织中这是一个*不同的*社区，所以登出会落在错误站点的登录页面上。设置它将登出引导回此站点（重新加载为访客）。

步骤：

1. **读取** `logoutUrl` 从配置；缺失 → 跳过。
2. **派生站点** — `scripts/derive-site-name.sh`（单个 `*.network-meta.xml`；
   如果为零/不明确则跳过）。
3. **解析、设置并部署——一个命令。** 调用辅助程序，它将值解析为绝对 URL（站点相对路径 → 与社区 `siteUrl` **路径**匹配，从不猜测），在规范位置幂等地写入 `<logoutUrl>`，并仅部署该文件：

   ```bash
   node scripts/set-logout-url.mjs \
     --logout-url "<logoutUrl from config>" \
     --network-file <sourceRoot>/networks/<site>.network-meta.xml \
     --target-org <org> --site <site> --deploy
   ```

**尽力而为**：辅助程序在成功或已设置时退出 **0**，在可恢复跳过时退出 **3**（网络文件缺失、原点无法解析、XML 特殊字符或部署失败）。将 **退出 3 视为响亮的跳过，而不是设置失败** — 继续设置其余部分，并告诉用户在站点的管理设置中手动设置登出 URL。用法、退出码合同和移植来源：
`references/logout-url.md`。

## 步骤 4 — 分配权限集

发现 `<packageDir>/main/default/permissionsets/` 下的权限集。如果不存在且未显式传递，则跳过。

**如果权限集存在但 `org-setup.config.json` 缺失，不要默默跳过。** 缺失的配置会使每个发现的权限集解析为 `skip`，因此什么都不会分配，并且后续的 GraphQL 模式将返回不完整（调用者缺乏 FLS）。相反，帮助用户提供分配——要么从 `assets/org-setup.config.template.json` 构建 `org-setup.config.json`，要么收集一次性运行的每个权限集分配输入。完整模式 + 构建流程：
`references/config-scaffold.md`。在写入文件或分配之前确认意图——不要编造分配者。

否则根据其配置分配者（`org-setup.config.json` → `permsetAssignments`），其中每个分配者是 `currentUser`、`guestUser` 或 `skip`（默认 `skip`）：

```bash
sf org assign permset --name <permset> --target-org <org> [--on-behalf-of <guestUsername>]
```

- **currentUser** — 不省略 `--on-behalf-of`。
- **guestUser** — 首先解析站点的访客用户名（见 `references/self-registration.md` 中的访客用户部分）。如果站点无法派生或没有访客用户解析，**跳过该权限集**并记录原因——不要中止其他权限集。
- 将“重复 … PermissionSet”和“未找到 … 目标组”视为跳过，而不是失败。

需要这样做的目的是 GraphQL 探视返回正确的模式（调用者需要对自定义字段具有 FLS）。

## 步骤 5 — 分配角色（配置驱动）

仅当 `org-setup.config.json` 包含 `role: { assignee: "currentUser", roleName: "<UserRole>" }` 时运行。将角色分配给当前用户是允许 Experience Cloud 自我注册工作的关键。幂等——如果用户已经具有角色则跳过。详情 + 精确查询：`references/role-assignment.md`。

## 步骤 6 — 启用自我注册（配置驱动）——运行前询问

仅当 `org-setup.config.json` 包含
`selfRegistration: { selfRegProfile, accountName }` 时运行。**运行前请先询问用户。** 序列（完整细节在 `references/self-registration.md`）：

1. **许可证预检查**（软跳过）——如果组织在配置的许可证上没有席位，则警告并跳过；这不是一个失败。见 `references/license-checks.md`。
2. **派生站点** — 运行 `scripts/derive-site-name.sh`；它输出站点名称（单个 `*.network-meta.xml` 的基本名称）或在存在零个或多个时退出非零（不明确——停止）。
3. **开启自我注册 + 重新部署网络文件** — 应用 **Edit B** of `assets/network-selfreg-xml-recipe.md`（设置 `selfRegistration=true`，注入 `<selfRegProfile>`），然后重新部署仅该文件。幂等——如果已经启用则跳过。（Edit A，成员组添加，已在步骤 3 中发生。）
4. **创建账户 + NetworkSelfRegistration** — 应用 `assets/network-selfreg.apex`（幂等；两者都是查询后创建；将 4a 和 4b 作为两个单独的 `sf apex run` 调用运行）。

## 步骤 6b — 启用社交登录（配置驱动）

仅当 `org-setup.config.json` 包含 `socialLogin` 块时运行。如果块不存在，`loadSocialLoginConfig` 返回 null，该步骤将被隐藏——干净地无操作并说明。此步骤是**非破坏性和幂等**的（它仅添加缺失的链接/成员），因此与自我注册和数据导入不同——它**不需要先询问**。

此步骤将站点配置的**认证提供者**（OAuth）和**SAML SSO 配置**链接到站点，以便内置的社交登录组件在 React 登录页面上渲染它们的按钮。在 React（站点容器）站点上，SSO 管理界面是隐藏的，因此链接是通过对 `AuthConfig` /
`AuthConfigProviders` 记录进行编程方式完成——您无法通过点击 Setup 来完成它。完整细节、子步骤和移植来源：`references/social-login.md`。

配置形状（有关完整模式，请参阅 `references/config-scaffold.md`）：

```json
{ "socialLogin": {
    "communityMemberProfile": "Customer Community User",
    "authProviderNames": ["Google", "My_SAML_Provider"],
    "communityUserPermset": "myapp_Guest_User_Api_Access"
} }
```

序列（镜像参考 `org-setup.mjs` `main()` 社交登录步骤，该步骤在自我注册之后、数据/GraphQL 步骤之前运行）：

逐字应用 `assets/` Apex 和 XML 模板（像自我注册/数据步骤一样）——每个子步骤的完整可运行命令在 `references/social-login.md` 中：

1. **派生站点** — 运行 `scripts/derive-site-name.sh`（单个
   `*.network-meta.xml`；如果为零/不明确则停止）。社交登录需要站点解析其 `AuthConfig`。
2. **启用“允许标准外部配置文件”** — 通过元数据 API 部署
   `assets/Communities.settings-meta.xml`（通过一个一次性最小项目；见参考）。需要它，以便 SSO 注册处理程序可以在标准社区配置文件上创建用户；没有它，认证提供者会以 `FIELD_INTEGRITY_EXCEPTION` 失败用户插入。一个“已经激活”警告是非致命跳过。
3. **将认证提供者链接到站点 `AuthConfig`** — 逐字运行
   `assets/social-login-auth-providers.apex`（替换 `<siteName>`、`<ProviderNamesList>`、`<ApiVersion>`）以创建缺失的 `AuthConfigProviders` 连接，然后读取其 `|DEBUG|` 行（参考中的表格）。全有或全无：如果任何配置的 `authProviderNames` 条目没有匹配的 `AuthProvider`（OAuth）或 `SamlSsoConfig`（SAML）记录，它会发出 `MISSING_PROVIDERS` 并链接任何内容——首先创建/修复它们。已链接的提供者是跳过（幂等）。
4. **将社区成员配置文件添加到 `NetworkMemberGroup`** — 解析网络 + 配置文件 ID 并如果不存在则创建成员（参考中的 `sf data` 命令）。没有它，SSO 注册用户会收到 `NO_ACCESS: User was not authorized for the community`。
5. **（可选）将 `communityUserPermset` 分配给社区用户** — 仅当配置时。授予 `ApiEnabled` 以便 `getCurrentUser()` (`/chatter/users/me`) 对 SSO 创建的用户有效。

> **重要提示**：一个存在但被跳过的 `socialLogin` 块是一个沉默失败的陷阱——应用可以正常部署，但社交登录按钮永远不会出现在登录页面上，并且没有错误解释原因。不要默默跳过：当块存在时运行该步骤，或者明确说明它不存在。

## 步骤 7 — 数据导入（基于存在性驱动）——运行前询问

首先运行 `scripts/find-data-plan.sh`。如果它退出非零，**跳过此步骤**——不要提示，不要报错；只需继续到步骤 8（可以简要说明“没有数据计划，跳过数据导入”）。没有计划就没有可导入的内容。成功时它会打印计划的路径（它会递归搜索，因此项目根 `data/` 和 `<packageDir>/main/default/data/` 布局都可以解析）。

存在时：**导入或清理数据前始终询问用户**——它会先删除现有记录。逐字应用模板；不要即兴编写 Apex：

1. 运行 `scripts/find-prep-script.sh`。如果成功，它会打印随应用一起分发的 `prepare-import-unique-fields.js` 的路径——首先运行它；它通过在记录文件上盖章稳定唯一键来消除重复运行。按预期复制的方式调用它（其接口不同——见 `references/data-import.md`）。如果它退出非零，则没有准备脚本——跳到清理步骤。
2. **清理** 按计划顺序反向（子项在前，父项在后）使用 `assets/data-delete.apex`。
3. **导入** 按计划顺序使用 `assets/data-import.apex`，解析 `@referenceId` 引用并按测量大小分批。

协议、`@referenceId` 解析、测量分批和 `SETUP_RESULT_JSON` 解析并硬失败规则：`references/data-import.md`。

## 步骤 8 — GraphQL 模式获取 + 代码生成

从 UI Bundle 目录运行，**在部署和权限分配之后**（模式反映组状态和调用者的 FLS）：

```bash
npm install
SF_TARGET_ORG=<org> npm run graphql:schema
npm run graphql:codegen
npm run build
```

详情：`references/graphql.md`。在每次更改对象、字段或权限的部署后重新运行模式获取 + 代码生成。

## 完成

设置在此结束——上述步骤（包括配置驱动的 6b 社交登录）
是完整的序列。本地开发预览 (`npm run dev:preview`) 是一个单独的开发者操作，不是设置的一部分；如果用户要求预览站点，请参阅 `references/dev-preview.md`。

## 关键规则

- 部署元数据**在**获取模式之前——自定义对象/字段只有在部署后才会出现。
- 分配权限**在**模式获取之前——否则调用者可能缺乏 FLS。
- 在每次更改对象、字段或权限的元数据部署后重新运行模式获取 + 代码生成。
- 永远不要默默跳过权限分配、自我注册、社交登录或数据导入——要么约定文件/配置块存在（运行它，对破坏性的步骤先询问），要么不存在（干净地跳过并说明）。一个存在但被跳过的 `socialLogin` 块意味着登录按钮不会出现，并且没有错误解释原因。
- 从 `sfdx-project.json` 发现源路径；永远不要硬编码
  `force-app/main/default`。
- 逐字应用 `assets/` Apex 和 XML 模板——它们编码了重复规则绕过、`allOrNone=false` 删除、幂等性、SOQL 安全性，以及（对于社交登录）所有或无提供者预检查和 REST 调用 `DML-not-allowed-on-` `AuthConfigProviders` 插入——所有这些手工操作很容易出错。

## 交互顺序（摘要）

1. 认证组织
2. 构建 UI bundles（预部署）
3. 部署元数据（如果自我注册配置，则部署许可证门控）
3b. 设置站点登出 URL（如果 `logoutUrl` 配置——部署后，幂等，尽力而为）
4. 分配权限集（配置驱动分配者）
5. 分配角色（如果配置）
6. 启用自我注册（如果配置——运行前询问）
6b. 启用社交登录（如果 `socialLogin` 配置——幂等，无需询问）
7. 导入数据（如果数据计划存在——运行前询问）
8. 获取 GraphQL 模式 + 代码生成 + 最终构建
