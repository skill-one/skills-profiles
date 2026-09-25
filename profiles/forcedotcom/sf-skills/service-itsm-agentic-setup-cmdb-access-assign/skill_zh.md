# 分配用户CMDB访问权限（服务云ITSM）

通过分配与CMDB（配置管理数据库）权限集及其权限集许可证相关的许可证支持CMDB权限集，授予**特定用户**读取和操作CMDB数据的能力。每次调用都通过**Salesforce托管的Headless-360 MCP服务器**（服务器密钥`headless-360`）进行，该服务器通过其四个元工具（`discover`、`describe`、`dispatch_readonly`、`dispatch`）运行。组织是从绑定到当前MCP会话的OAuth JWT派生的——技能永远不会处理组织ID、别名或凭证——因此，它对**生产**和沙盒的作用完全相同，无需为每个用户单独安装MCP。

这是CMDB设置的**第3层**。它假设组织级别的CMDB门禁已经解除（功能已启用）——也就是说，这是一个单独的技能（`service-itsm-agentic-setup-cmdb-configure`，第0-2层）。此技能授予*用户*访问权限；它不会为组织启用功能。

## 此技能弥补的差距

启用CMDB功能会解除**组织级别**的门禁，但某些CMDB读取（例如`bundleListView`）也会强制执行**用户级别**的访问。即使功能已正确为组织启用，没有CMDB权限集的用户仍然会收到`403 FUNCTIONALITY_NOT_ENABLED`（"此用户未启用"）错误。此技能为用户分配CMDB权限集，以便这些读取成功。

> **如果组织功能未启用，此技能将不执行任何操作。** 用户级别的访问在组织级别的CMDB功能启用之前没有任何效果。如果您发现组织门禁仍然关闭，请停止，并告诉用户必须先为组织打开CMDB功能——请参阅末尾的跨技能注释。

## 四个CMDB权限集

每个都是基于许可证的标准权限集；分配它也需要（并且此技能会分配）其权限集许可证（PSL）。

| 角色 | 权限集（`Name`） | 支持PSL（`DeveloperName`） | 授予 |
|------|------------------|--------------------------|------|
| 读取者 | `ItSrvcCnfgItmReadPermissionSet` | `ItSrvcCnfgItmReadPsl` | 读取CMDB配置项 |
| 所有者 | `ItSrvcCnfgItmOwnerPermissionSet` | `ItSrvcCnfgItmOwnerPsl` | 拥有/编辑配置项 |
| 类型读取者 | `ItSrvcCnfgItmTypReadPermissionSet` | `ItSrvcCnfgItmTypReadPsl` | 读取配置项类型 |
| 类型管理员 | `ItSrvcCnfgItmTypManagerPermissionSet` | `ItSrvcCnfgItmTypMgrPsl` | 管理配置项类型 |

对于只读CMDB访问，**读取者**（+**类型读取者**）是最小权限集。对于编辑CMDB记录的用户，添加**所有者**；对于管理类型目录的用户，添加**类型管理员**。如果用户未指定角色，请询问（见澄清问题）——默认为查看器使用**读取者 + 类型读取者**。

> **包管理需要类型管理员。** 如果用户的目的是**安装或管理CMDB内容包**（或者他们在包管理读取（例如`GET /connect/cmdb/bundles/details`）上遇到`403`），清除它的角色是**类型管理员**——仅持有读取者/所有者/类型读取者的用户在包操作上仍然会收到`403 FUNCTIONALITY_NOT_ENABLED`。为任何部署或管理包的用户分配**类型管理员**（及其自己的支持PSL，`ItSrvcCnfgItmTypMgrPsl`）。

## 范围

- **在范围内**：解析目标用户、解析请求的CMDB权限集、检查现有分配、分配权限集许可证和权限集，并验证。
- **超出范围**：启用CMDB功能/配置CMDB租户（第0-2层——`service-itsm-agentic-setup-cmdb-configure`）、安装内容包、CMDB记录CRUD、创建自定义权限集，或组织权限/版本更改。

## 机制

所有操作都通过**headless-360** MCP工具进行。读取通过`mcp__headless-360__dispatch_readonly`，写入通过`mcp__headless-360__dispatch`——两者都使用原始HTTP：`{"url": "<path>", "method": "GET|POST", "body"?: {...}, "queryParams"?: {...}}`——**不是**`{operation_id, arguments}`。有关每个调用的确切`url` / `method` / `body`，请参阅`references/mcp-invocation.md`。四个工具：

- `mcp__headless-360__discover` — 对索引的操作目录进行语义搜索。此技能使用的标准`/query`和`/sobjects/...` REST路由并不总是被索引，因此错过**并不意味着路由不存在**——直接调度确切路径（见`references/mcp-invocation.md`）。
- `mcp__headless-360__describe` — 在任何POST之前拉取完整的输入模式和规范路由。
- `mcp__headless-360__dispatch_readonly` — 每个读取（GET）的分发器。
- `mcp__headless-360__dispatch` — 每个写入（POST/PATCH）的分发器。

此技能永远不会处理凭证——组织绑定到当前的OAuth会话。如果`dispatch*`调用返回认证错误，请告诉用户重新认证headless-360 MCP连接（并确认会话指向预期的组织），然后停止。

---

## 澄清问题

仅询问您无法从对话中推断出的问题：

- **哪个用户？** 用户名（或您可以解析为确切一个用户的名称/电子邮件）。如果请求是“给我访问”/“当前用户”，则解析运行用户。
- **哪个角色？** 读取者、所有者、类型读取者、类型管理员——或者“只读访问”（→ 读取者 + 类型读取者）。如果未指定，默认为查看器使用**读取者 + 类型读取者**。如果用户安装或管理CMDB**内容包**（或正在修复包管理403），请包括**类型管理员**——没有它，包操作403。
- **哪个组织？** 确认目标组织，并明确说明**此组织将被修改**（分配权限集是一种写入操作）。对于生产环境，获取明确确认。

不要重新询问用户已经提供的内容；预填充并注明“(来自对话)”。

---

## 工作流

始终在写入之前读取：在分配任何内容之前运行只读检查。所有分配都是按用户进行的，并且是幂等的——重复分配必须视为已完成，而不是错误。

### 第1步——确认组织级别的CMDB功能已启用（只读，先决条件）

用户访问在组织门禁解除之前没有任何意义。读取功能状态：

```text
dispatch_readonly({ "url": "/services/data/v67.0/connect/setup/discovery/feature/service-cloud-itsm-cmdb-integration/status", "method": "GET" })
```

- `status == ENABLED` → 继续。
- `status != ENABLED`（或调用返回`403 FUNCTIONALITY_NOT_ENABLED`）→ 停止。用平实的语言告诉用户，在为用户授予访问权限之前，必须先为组织打开CMDB，并指向CMDB功能启用技能（见跨技能注释）。不要分配任何内容。

### 第2步——解析目标用户（只读）

**对于“当前用户”/“我”/“我自己的用户”**（**不要**使用`USER_ID()`——它是Apex专用的，并且被REST查询API拒绝；**不要**依赖`/chatter/users/me`或`/connect/user-profiles/me`——当Chatter/社区关闭时，它们会返回`403 FUNCTIONALITY_NOT_ENABLED`）。相反，读取API根并解析身份URL：

```text
dispatch_readonly({ "url": "/services/data/v67.0/", "method": "GET" })
```

响应的`identity`字段是一个以`/<orgId>/<userId>`结尾的URL（用户ID是最后一个路径段，并以`005`开头）。直接使用该ID作为目标用户，或者确认它：

```text
dispatch_readonly({ "url": "/services/data/v67.0/query", "method": "GET", "queryParams": { "q": "SELECT Id, Username, Name, IsActive FROM User WHERE Id = '<userId>'" } })
```

**对于命名用户**（用户名/电子邮件提供）：

```text
dispatch_readonly({ "url": "/services/data/v67.0/query", "method": "GET", "queryParams": { "q": "SELECT Id, Username, Name, IsActive FROM User WHERE Username = '<username>'" } })
```

- 恰好一个活动用户 → 捕获`Id`。
- 零结果 → 停止；告诉用户未找到匹配的用户，并要求他们确认用户名。
- 多于一个 → 停止；列出候选人（名称 + 用户名），并询问是哪一个。
- 用户不活跃 → 警告用户；分配仍然可以继续，但访问仅在用户活跃时生效。

### 第3步——解析请求的权限集（只读）

对于每个请求的角色，解析权限集及其支持许可证：

```text
dispatch_readonly({ "url": "/services/data/v67.0/query", "method": "GET", "queryParams": { "q": "SELECT Id, Name, LicenseId FROM PermissionSet WHERE Name = '<psName>'" } })
```

使用上表中`Name`的值。捕获每个`Id`（权限集）和`LicenseId`（要分配的PSL）。如果找不到权限集，则组织可能没有CMDB许可证——停止并报告此组织的CMDB未设置。

### 第4步——检查现有分配（只读——幂等性，权限集组感知）

角色可以通过**两种方式**授予，此检查必须接受**两者**——否则，它会错误地报告已授予的角色为缺失，并错误地要求分配它：

1. **直接**——一个`PermissionSetAssignment`，其`PermissionSetId`是角色自己的权限集。
2. **通过权限集组（PSG）**——当角色的权限集是用户分配的PSG的*成员*时。在这种情况下，用户的`PermissionSetAssignment`行包含`PermissionSetGroupId`，其`PermissionSetId`是组的内部*聚合*集——**不是**成员权限集——因此过滤`PermissionSetId = '<psId>'`的查询返回**零**，即使用户实际上拥有该角色。

按每个角色运行**两种**权限集读取；如果**任何**返回`totalSize >= 1`（第二个是顶级半连接——将其嵌套在`OR`内会抛出`MALFORMED_QUERY`），则权限集存在：

```text
dispatch_readonly({ "url": "/services/data/v67.0/query", "method": "GET", "queryParams": { "q": "SELECT Id FROM PermissionSetAssignment WHERE AssigneeId = '<userId>' AND PermissionSetId = '<psId>'" } })
dispatch_readonly({ "url": "/services/data/v67.0/query", "method": "GET", "queryParams": { "q": "SELECT Id FROM PermissionSetAssignment WHERE AssigneeId = '<userId>' AND PermissionSetGroupId IN (SELECT PermissionSetGroupId FROM PermissionSetGroupComponent WHERE PermissionSetId = '<psId>')" } })
```

然后检查支持许可证（包含角色的PSG也直接分配其支持PSL，因此此单个读取已经涵盖了PSG的情况）：

```text
dispatch_readonly({ "url": "/services/data/v67.0/query", "method": "GET", "queryParams": { "q": "SELECT Id FROM PermissionSetLicenseAssign WHERE AssigneeId = '<userId>' AND PermissionSetLicenseId = '<pslId>'" } })
```

如果权限集通过**任何**路径存在**并且**支持许可证读取返回`totalSize >= 1`，则该角色**已分配**——跳过其写入并记录为已完成。仅分配真正缺失的内容，并且在用户已经通过PSG持有它的情况下**不要**直接重新分配成员权限集。

### 第5步——分配权限集许可证，然后是权限集（写入——先确认）

与用户确认目标用户、组织和角色，然后为每个缺失的角色首先分配PSL，然后是权限集：

```text
dispatch({ "url": "/services/data/v67.0/sobjects/PermissionSetLicenseAssign", "method": "POST", "body": { "AssigneeId": "<userId>", "PermissionSetLicenseId": "<pslId>" } })

dispatch({ "url": "/services/data/v67.0/sobjects/PermissionSetAssignment", "method": "POST", "body": { "AssigneeId": "<userId>", "PermissionSetId": "<psId>" } })
```

- `201` → 已分配。
- `400 DUPLICATE_VALUE` → 用户已经拥有它；将其视为成功（幂等性），而不是错误。
- 许可证限制错误（例如`INSUFFICIENT_ACCESS` / 没有座位）→ 停止该角色；告诉用户CMDB许可证没有可用的座位，以及有多少座位正在使用（见`references/mcp-invocation.md`中的座位查询）。不要重试。

### 第6步——验证（只读——不要单独信任POST响应）

重新运行第4步的读取——**两种**直接和通过PSG的权限集检查，以及许可证检查。只有当其权限集通过**任何**路径存在**并且**其支持许可证读取返回时，角色才视为完成。按角色报告：已分配/已经拥有。只有在此读取中确认存在的角色才视为完成。

---

## 规则/约束

| 约束 | 理由 |
|------|------|
| 在分配之前确认组织功能已`ENABLED` | 用户访问在组织级别的CMDB门禁解除之前没有任何效果；先分配会导致误导性的无操作 |
| 在写入之前将用户解析为确切一条记录 | 分配给错误的（或模糊的）用户很难撤销，并且是一个安全问题 |
| 在每次分配之前读取现有分配 | 分配是按用户进行的；重新分配会抛出`DUPLICATE_VALUE`——跳过已存在的内容 |
| 在权限集之前分配PSL | 权限集是许可证支持的；许可证座位必须被保留，分配才能成功 |
| 将`DUPLICATE_VALUE`视为成功 | 它意味着用户已经拥有该访问权限——幂等性，不是错误 |
| 永远不要创建或编辑权限集 | 此技能仅*分配*标准CMDB权限集；创建权限集超出了范围 |
| 与用户确认目标组织、用户和每个写入 | 这些是授予用户对实时组织的数据访问的真实更改 |
| 永远不要向用户展示内部术语 | 保持记录ID、HTTP状态代码（403/400/…）、API错误代码（`FUNCTIONALITY_NOT_ENABLED`、`DUPLICATE_VALUE`）、对象名称（`PermissionSetLicenseAssign`）、开发者名称（`ItSrvcCnfgItmReadPsl`）和工具内部细节（`dispatch`、`headless-360`）远离用户界面输出。使用可读的角色名称和平实的语言 |

---

## 验证清单

- [ ] 在任何分配之前确认组织CMDB功能为`ENABLED`？
- [ ] 目标用户解析为确切一条记录？
- [ ] 每个请求的角色权限集及其支持许可证解析？
- [ ] 在写入之前检查现有分配（幂等性）？
- [ ] 对于每个请求的角色，权限集及其许可证都被分配？
- [ ] 通过写入后的读取验证（不要单独信任POST响应）？
- [ ] 首先与用户确认目标组织、用户和每个写入？

---

## 输出预期

```text
CMDB访问分配——完成（通过service-itsm-agentic-setup-cmdb-access-assign）

目标组织： <org>
用户： <name> (<username>)

  配置项读取者 ............. 已分配
  配置项类型读取者 ............. 已拥有访问权限

此用户现在可以在此组织中读取CMDB数据。如果他们仍然无法访问，请确认组织的CMDB功能已打开（那是一个单独的设置步骤）。
```

将内部术语从用户界面输出中排除（不要记录ID、HTTP状态代码、错误代码、对象或开发者名称）。如果任何步骤失败，请停止并告诉用户——用平实的语言——哪一部分未成功及其含义。将任何原始错误（例如403或`FUNCTIONALITY_NOT_ENABLED`）翻译成它意味着什么（“组织的CMDB尚未启用”），而不是重复代码。

---

## 常见失败（以平实的语言呈现这些问题）

| 症状 | 可能的原因 | 告诉用户什么 |
|------|-----------|--------------|
| 功能状态不是`ENABLED`（或状态读取上的`403`） | 组织级别的CMDB门禁未解除 | 必须先为组织打开CMDB；这是一个单独的设置步骤——指向功能启用技能 |
| 权限集未找到 | 组织没有CMDB许可证/未设置 | 此组织的CMDB似乎未设置；确认它已许可并启用 |
| 在分配后**包管理**读取上的`403 FUNCTIONALITY_NOT_ENABLED`（例如`bundles/details`、`bundleListView`），功能已启用 | 用户持有读取者/所有者/类型读取者，但没有**类型管理员**——包操作需要它 | 分配**类型管理员**——此角色对于CMDB包管理是必需的；其他CMDB角色不涵盖包操作 |
| 技能表示CMDB角色缺失并请求分配它，但用户已经拥有它（例如通过权限集组） | 幂等性检查只看到*直接*分配的权限集，并且对组交付的授权视而不见——已在第4步修复，该步骤现在也检查组成员资格 | 用户已经通过权限集组拥有该访问权限；将角色视为已授予——不需要新的分配 |
| 分配上的`400 DUPLICATE_VALUE` | 用户已经拥有该访问权限 | 不是错误——报告角色已分配 |
| 许可证限制/无座位错误在分配上 | CMDB权限集许可证座位已用尽 | 报告正在使用与可用的座位；必须释放座位（或添加更多许可证）才能分配 |
| `dispatch*`认证错误 | headless-360 MCP会话未认证/令牌过期 | 重新认证headless-360 MCP连接并确认会话指向预期的组织 |

---

## 跨技能集成

| 当... | 技能 |
|------|------|
| 组织CMDB功能尚未启用（组织门禁仍然关闭） | `service-itsm-agentic-setup-cmdb-configure`（第0-2层——先启用功能，然后返回这里） |
| 用户需要安装CMDB基础内容包 | `service-itsm-agentic-setup-cmdb-bundle-deploy`（第4层——内容，与用户访问分开）。该技能的包管理读取需要用户持有**类型管理员**，因此在此处首先分配它 |

---

## 参考文件索引

| 文件 | 何时读取 |
|------|----------|
| `references/mcp-invocation.md` | 每个读取和写入的确切`dispatch*` url/method/body、响应信封、许可证座位查询以及错误表 |
