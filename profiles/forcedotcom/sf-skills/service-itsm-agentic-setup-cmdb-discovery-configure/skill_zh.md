# 启用 CMDB 资产发现（服务云 ITSM）

通过启用 `service-cloud-itsm-discovery-integration` 功能来为 CMDB 开启 **资产发现**，然后通过分配 **IT 服务发现管理员** 权限集（及其权限集许可证）授予用户访问 **发现页面** 的权限。这是 CMDB 设置的 **最后一层** — 仅在基础 CMDB 功能启用、用户具有 CMDB 访问权限且已安装 CMDB 基础内容包后才会运行。每次调用都通过 **Salesforce 托管的 Headless-360 MCP 服务器**（服务器密钥 `headless-360`）及其四个元工具 (`discover`, `describe`, `dispatch_readonly`, `dispatch`）进行。组织是从当前 OAuth 会话绑定的 OAuth JWT 派生的 — 技能永远不会处理组织 ID、别名或凭证 — 因此此功能对 **生产** 和沙盒的作用完全相同，无需为每个用户安装 MCP。

此技能仅涵盖 **发现层** — 启用功能 *并* 授予用户访问发现页面的权限。早期的 CMDB 层是单独的技能 — 请参阅本文件的末尾。

## CMDB 堆栈中的位置

CMDB 按顺序分层启用，每一层都依赖于前一层：

```text
第 0 层  组织 SKU / 许可证      组织权限 ITSrvcsCnfgMgmnt（仅验证 — 无法通过 API 设置）
第 1 层  租户配置             CMDB 租户必须达到 PROVISIONED 状态（异步）
第 2 层  CMDB 功能             启用 service-cloud-itsm-cmdb-integration（移除 403 门禁）
第 3 层  用户访问             将 PSL + CMDB 权限集分配给用户
第 4 层  内容包             安装 CMDB 基础（基础）内容包
第 5 层  资产发现            启用 service-cloud-itsm-discovery-integration + 分配 IT 服务发现管理员权限集  ← 此技能
```

推荐将发现 **最后** 启用，但它 **不需要** 基础 CMDB 功能已启用：启用 **级联启用** 其依赖项（基础 CMDB 功能），作为启用发现的一部分，前提是该功能自身的先决条件（例如已配置的 CMDB 租户）已满足。预检查中的 `enableBlockedReasons` 数组是权威的阻止信号 — 仅仅是 `NOT_ENABLED` 的基础 CMDB 功能出现在 `dependencyStatuses` 中，其 `enableBlockedReasons` 为 **空**，并且 **不是** 阻止。因此，永远不要告诉用户直接启用“将出错”；告诉他们它将首先启用 CMDB，然后是发现。只有 **非空** 的 `enableBlockedReasons`（例如租户未配置）才是未满足的先决条件，会阻止启用。

> **启用功能移除组织级别的门禁；发现权限集为用户提供发现页面。** 此技能 **两者都做**：它为组织启用发现（步骤 2），然后为目标用户分配基于许可证的 **`ItSrvcDscvrMgrPermissionSet`**（“IT 服务发现管理员”，由 PSL **`ItSrvcDscvrMgrPsl`** 支持），以便他们实际上可以打开和使用发现页面（步骤 4–7）。该权限集 **不同于** `service-itsm-agentic-setup-cmdb-access-assign` 为 CMDB *数据* 分配的四个配置项权限集（读者 / 所有者 / 类型读者 / 类型管理员）— 仅持有这些权限的用户 **将无法** 访问发现页面。分配步骤是幂等的：如果用户已持有发现权限集及其许可证，则跳过并报告为已完成。

## 范围

- **在范围内**：预检查、启用和验证 `service-cloud-itsm-discovery-integration` 功能；以及作为后续操作 — 将 **IT 服务发现管理员** 权限集（及其权限集许可证）分配给目标用户，以便他们可以访问发现页面。
- **超出范围**：启用基础 CMDB 功能 / 配置 CMDB 租户（第 2 层 — `service-itsm-agentic-setup-cmdb-configure`），分配用于 CMDB *数据* 访问的四个配置项权限集（第 3 层 — `service-itsm-agentic-setup-cmdb-access-assign`），包安装（第 4 层 — `service-itsm-agentic-setup-cmdb-bundle-deploy`），CMDB 记录 CRUD，服务图连接器配置，识别规则，创建或编辑权限集。

## 机制

所有操作都通过 **headless-360** MCP 工具进行。读取通过 `mcp__headless-360__dispatch_readonly`，写入通过 `mcp__headless-360__dispatch` — 两者都使用原始 HTTP：`{"url": "<path>", "method": "GET|POST", "body"?: {...}, "queryParams"?: {...}}` — **不是** `{operation_id, arguments}`。有关每个调用的确切 `url` / `method` / `body`，请参阅 `references/mcp-invocation.md`。四个工具：

- `mcp__headless-360__discover` — 对索引的操作目录进行语义搜索。此技能使用的 Setup/Connect 路由和 `/query` / `/sobjects/...` REST 路由不总是排名第一（或未索引），因此错过 **不代表** 路径不存在 — 直接调度确切路径（见 `references/mcp-invocation.md`）。
- `mcp__headless-360__describe` — 在任何 POST 之前拉取完整的输入模式和规范路由。
- `mcp__headless-360__dispatch_readonly` — 每个读取（GET）的分发器。
- `mcp__headless-360__dispatch` — 每个写入（POST/PATCH）的分发器。

技能永远不会处理凭证 — 组织绑定到当前的 OAuth 会话。如果 `dispatch*` 调用返回授权错误，告诉用户重新认证 headless-360 MCP 连接（并确认会话指向预期的组织），然后停止。

## 发现权限集

| 角色 | 权限集（`Name`） | 支持的 PSL（`DeveloperName`） | 授予 |
|------|-------------------------|-------------------------------|--------|
| 发现管理员 | `ItSrvcDscvrMgrPermissionSet` | `ItSrvcDscvrMgrPsl` | 打开和使用发现页面 |

在运行时解析权限集的 `Id` 及其 `LicenseId`（步骤 5），而不是硬编码 ID — ID 因组织而异。

---

## 澄清问题

仅询问您无法从对话中推断出的问题：

- **哪个组织？** 确认目标组织，并明确说明 **此组织将被修改**（启用发现功能是写入操作）。对于生产环境，获取明确确认。
- **哪个用户获得发现页面访问权限？** 要分配 IT 服务发现管理员角色的用户。如果请求是“为我启用发现” / “设置发现”，默认为 **当前（运行）用户**。接受其他用户的用户名/电子邮件。

不要重新询问用户已提供的内容；预填充并注明“(来自对话)”。

---

## 工作流

所有步骤都是按顺序执行的，并且受限制 — **不要在失败检查后继续前进。** 始终在写入之前读取：在启用之前运行只读预检查，在分配之前运行分配检查。

### 步骤 1 — 预检查发现功能状态（读取）

功能 API 名称是 `service-cloud-itsm-discovery-integration`。

```text
dispatch_readonly({ "url": "/services/data/v67.0/connect/setup/discovery/feature/service-cloud-itsm-discovery-integration/status", "method": "GET" })
```

- `status == ENABLED` → 功能已启用；跳到验证（步骤 3），然后继续到访问后续操作（步骤 4–7）。
- `status == NOT_ENABLED` with `enableBlockedReasons: []` → 准备启用（步骤 2）。**在确认之前，检查 `dependencyStatuses`：** 如果基础 CMDB 功能 (`service-cloud-itsm-cmdb-integration`) 列表中显示为 `NOT_ENABLED`，那 **不是** 阻止 — 启用发现将 **级联启用** 其基础 CMDB 依赖项，作为启用发现的一部分。告诉用户确切的内容（“这将首先启用 CMDB，然后是资产发现”）。**不要** 警告它“将出错”或提出“让它报告依赖项错误” — 这两种情况都不会发生。
- `enableBlockedReasons` 非空 → **停止** 并以 plain language 向用户传达每个原因。这些是组织仍然需要的未满足先决条件（例如 CMDB 租户未配置，因此基础功能无法启用）。将用户引导到更早的 CMDB 设置技能（见“常见失败”）并 **不要** 尝试启用。
- `403 FUNCTIONALITY_NOT_ENABLED` 在此 GET 上 → 基础 CMDB 门禁本身仍然关闭；组织需要 `service-itsm-agentic-setup-cmdb-configure` 首先启用。停止并将用户引导到那里。

### 步骤 2 — 启用资产发现（写入 — 首先与用户确认）

如果步骤 1 已报告 `ENABLED`，则跳过此步骤。

```text
dispatch({ "url": "/services/data/v67.0/connect/setup/discovery/feature/service-cloud-itsm-discovery-integration/enable", "method": "POST", "body": {} })
→ {"success": true}
```

### 步骤 3 — 验证功能（读取 — 单独信任 POST 响应）

```text
dispatch_readonly({ "url": "/services/data/v67.0/connect/setup/discovery/feature/service-cloud-itsm-discovery-integration/status", "method": "GET" })
→ expect status == ENABLED
```

**`status == ENABLED` 是功能已启用的最终确认。** 确认后，继续到下面的访问后续操作 — 功能启用本身不会自动赋予任何用户发现页面。

### 步骤 4 — 解析目标用户（读取）

**对于“当前用户” / “我” / “设置发现”**（**不要**使用 `USER_ID()` — Apex 仅用，被 REST 查询 API 拒绝；**不要**依赖 `/chatter/users/me` 或 `/connect/user-profiles/me` — 当 Chatter/社区关闭时它们会 `403`）。读取 API 根并解析身份 URL：

```text
dispatch_readonly({ "url": "/services/data/v67.0/", "method": "GET" })
```

响应 `identity` 字段是一个以 `/<orgId>/<userId>` 结尾的 URL（用户 ID 是最后一个路径段，以 `005` 开头）。直接使用该 ID，或使用 `User` 查询确认它。

**对于命名用户**（用户名 / 电子邮件提供）：

```text
dispatch_readonly({ "url": "/services/data/v67.0/query", "method": "GET", "queryParams": { "q": "SELECT Id, Username, Name, IsActive FROM User WHERE Username = '<username>'" } })
```

- 恰好一个活跃用户 → 捕获 `Id`。
- 零结果 → **停止**；询问用户确认用户名。
- 超过一个 → **停止**；列出候选者（名称 + 用户名）并询问是哪一个。

### 步骤 5 — 解析发现权限集 + 检查现有分配（读取 — 幂等性）

解析权限集及其支持的许可证：

```text
dispatch_readonly({ "url": "/services/data/v67.0/query", "method": "GET", "queryParams": { "q": "SELECT Id, Name, LicenseId FROM PermissionSet WHERE Name = 'ItSrvcDscvrMgrPermissionSet'" } })
```

捕获 `Id`（权限集）和 `LicenseId`（要分配的 PSL）。`totalSize == 0` 表示组织未为发现许可证 — 停止并报告。然后检查用户是否已拥有两者：

```text
dispatch_readonly({ "url": "/services/data/v67.0/query", "method": "GET", "queryParams": { "q": "SELECT Id FROM PermissionSetAssignment WHERE AssigneeId = '<userId>' AND PermissionSetId = '<psId>'" } })
dispatch_readonly({ "url": "/services/data/v67.0/query", "method": "GET", "queryParams": { "q": "SELECT Id FROM PermissionSetLicenseAssign WHERE AssigneeId = '<userId>' AND PermissionSetLicenseId = '<pslId>'" } })
```

如果两者都存在，则角色 **已分配** — 跳过步骤 6 并记录为已完成。

### 步骤 6 — 分配许可证，然后分配权限集（写入 — 首先与用户确认）

跳过步骤 5 显示的已分配内容。首先分配 PSL，然后分配权限集：

```text
dispatch({ "url": "/services/data/v67.0/sobjects/PermissionSetLicenseAssign", "method": "POST", "body": { "AssigneeId": "<userId>", "PermissionSetLicenseId": "<pslId>" } })
dispatch({ "url": "/services/data/v67.0/sobjects/PermissionSetAssignment", "method": "POST", "body": { "AssigneeId": "<userId>", "PermissionSetId": "<psId>" } })
```

- `201` → 已分配。
- `400 DUPLICATE_VALUE` → 用户已拥有；将其视为成功（幂等），而不是失败。
- 许可证限制 / 无座位错误 → **停止** 分配；告诉用户发现许可证没有可用座位（见 `references/mcp-invocation.md` 中的座位查询）。不要重试。

### 步骤 7 — 验证分配（读取 — 单独信任 POST 响应）

重新运行两个步骤 5 分配查询。只有当 **两者** 的 `PermissionSetAssignment` 和 `PermissionSetLicenseAssign` 返回 `totalSize == 1` 时，用户才能访问发现页面。

---

## 规则 / 限制

| 限制 | 理由 |
|-----------|-----------|
| 建议在基础 CMDB 功能启用后运行，但不是必须的 | 发现依赖于基础 CMDB 功能，但启用 **级联启用** 它，当它仅 `NOT_ENABLED`（空 `enableBlockedReasons`）时；通知级联 — 永远不要声称直接启用“将出错”。实际阻止启用的是预检查 `enableBlockedReasons` |
| 启用之前读取预检查；启用后验证 | 功能是状态化的；POST 响应可能滞后于实际状态 |
| 当 `enableBlockedReasons` 非空时不尝试启用 | 那些是未满足的先决条件 — 向用户传达并引导他们到更早的 CMDB 技能 |
| 始终在启用后跟随发现管理员的分配 | 功能启用本身不会自动赋予任何用户发现页面；权限集是授予页面访问权限的 |
| 在分配之前解析用户以精确为一个记录 | 分配给错误的（或歧义的）用户很难逆转，并且是安全问题 |
| 在分配之前读取现有分配；先分配 PSL，然后分配权限集 | 权限集是许可证支持的，并且是按用户的 — 重新分配会抛出 `DUPLICATE_VALUE`；必须持有许可证座位才能使分配生效 |
| 将 `DUPLICATE_VALUE` 视为成功 | 它意味着用户已拥有该访问权限 — 幂等，不是错误 |
| 永远不要创建或编辑权限集 | 此技能仅 *分配* 标准发现权限集 |
| 与用户确认目标组织、用户和每个写入 | 这些是针对实时组织的真实、难以逆转的更改 |
| 永远不要向用户展示内部术语 | 保持记录 ID、组织 ID、HTTP 状态代码（403/500/…）、API 错误代码（`FUNCTIONALITY_NOT_ENABLED`，`DUPLICATE_VALUE`，…）、对象名称（`PermissionSetLicenseAssign`）、端点名称、功能 API 名称（`service-cloud-itsm-discovery-integration`）、开发者名称（`ItSrvcsCnfgMgmnt`，`ItSrvcDscvrMgrPsl`，…）、工具内部（`dispatch`，`headless-360`）等用户界面输出之外的术语。翻译为 plain language；使用人类可读的名称和状态 |

---

## 验证清单

- [ ] 步骤 1：预检查显示启用前 `enableBlockedReasons: []`（或 `status == ENABLED` 已存在）？
- [ ] 步骤 2：启用返回 `success: true`（或因为已启用而跳过）？
- [ ] 步骤 3：验证 GET 显示 `status == ENABLED`？
- [ ] 步骤 4：目标用户解析为精确一个记录？
- [ ] 步骤 5：发现权限集 + 许可证解析；检查现有分配（幂等性）？
- [ ] 步骤 6：对于目标用户，权限集及其许可证都已分配（或已经分配）？
- [ ] 步骤 7：通过后写入读取确认分配（不要单独信任 POST 响应）？
- [ ] 首先与用户确认目标组织、用户和每个写入？

---

## 输出预期

```text
CMDB 资产发现 — 完成（通过 service-itsm-agentic-setup-cmdb-discovery-configure）

目标组织： <org>
用户： <name> (<username>)

  资产发现 ................... 已启用
  IT 服务发现管理员 ...... 已分配    （或：已具有访问权限）

资产发现现已在此组织中启用，并且上述用户可以打开和使用
发现页面。这完成了 CMDB 设置 — 基础功能、用户访问、内容
包和发现均已就绪。

要为其他用户提供发现页面，请重新运行此功能并指定每个用户（或使用
service-itsm-agentic-setup-cmdb-access-assign 为 CMDB 数据角色）。
