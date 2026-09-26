# 创建数字体验门户

在 Salesforce 中创建一个新的数字体验（以前称为 Communities）门户/站点。支持员工服务门户、合作伙伴门户（PRM）以及通用客户社区。

**所有操作都通过 headless-360 MCP 服务器运行** (`mcp__headless-360__discover` →
`mcp__headless-360__describe` → `mcp__headless-360__dispatch` / `mcp__headless-360__dispatch_readonly`).
**不要**使用 Salesforce CLI（其 `api request`、`data query` 或 `org open` 子命令）、project-codey MCP 服务器、原始 `curl` 或任何其他 HTTP 客户端——`dispatch`/`dispatch_readonly` 是此技能与组织通信的唯一方式。有关确切调用形状，请参阅 `references/mcp-invocation.md`。

## 范围

- **在范围内**：通过 headless-360 Connect API 调度器创建数字体验站点。门户类型选择。基本配置（名称、URL、模板）。自助服务门户与嵌入式服务配置。**使站点端到端可达**——激活网络 (`status: Live`)、添加成员配置文件并发布体验构建器页面（见 `references/post-creation-activate-publish.md`）。
- **超出范围**：深度创建后定制（在 Builder 中进行页面布局/组件作者）。内容创作。初始设置之外的品牌。单个用户记录管理（成员资格是在配置文件/权限集级别添加的，而不是每个用户）。

---

## 执行模型（首先阅读）

每个组织调用都是一个 **调度**：`mcp__headless-360__dispatch_readonly(url, method: "GET", queryParams)`
用于读取，`mcp__headless-360__dispatch(url, method, body)` 用于写入；从响应中读取 `status_code` + `body`。要解析门户类型的端点，使用 `mcp__headless-360__discover(query=...)` 和
`mcp__headless-360__describe(id=...)` 作为需要。体验云的 Connect API 创建/列表操作不总是由 `discover`/`describe` 索引——当查找返回无内容时，直接调度众所周知的版本化 Connect API 路径（见 `references/mcp-invocation.md`），而不是得出功能缺失的结论。

**关键**：路径必须包含完整的 `/services/data/vXX.0/...` 前缀**（例如**
`"/services/data/v67.0/connect/communities"`)**——与一些其他调度器不同，headless-360 **不**为您解析或注入 API 版本。没有版本前缀的路径返回
`400 ROUTE_NOT_FOUND`。当可用时，从 `discover`/`describe` 结果中逐字复制路径；否则使用此技能示例中显示的版本（编写时为 `v67.0`）并调整如果组织运行不同的版本。完整详细信息、响应包、作业监控和易犯错误位于 `references/mcp-invocation.md`。

---

## 澄清问题

在继续之前确定：

1. **门户类型？**
   - 员工服务 / ITSM / HR / 帮助台 → **通过 communities API 优先选择 `Agentforce Employee Center` Aura 模板**（最丰富的员工体验；Agentforce 就绪）。当 MIAW 必须在创建时连接并存在访客 ESD 时，请使用自助服务 API。
   - 合作伙伴门户（PRM）→ 需要 PRM 功能启用
   - 客户社区 → 通用社区创建（Aura 或 LWR 体验构建器模板）

2. **基本设置（所有类型都需要）：**
   - 门户名称？
   - URL 前缀？（必须只包含字母数字，不能有连字符或空格）
   - 描述（可选）

3. **对于员工服务 / 自助服务门户：**
   - `siteType`？ → 默认 `AURA`（Aura 体验构建器 + Builder）。仅当用户明确想要 Lightning Web Runtime 站点时才使用 `LWR`。**永远**不要创建 Salesforce Tabs + Visualforce ("VF Template") 站点——那些是遗留的，并且没有 Builder。
   - MIAW / 嵌入式服务部署 ID(s)？ 这些在创建时将 Messaging for In-App 和 Web 连接到门户中。自助服务 API 需要**访客** ESD 配置；**认证用户** ESD 配置是可选的。如果用户还没有创建嵌入式服务部署，请将他们指向设置 → 嵌入式服务部署首先。

4. **仅适用于合作伙伴门户：**
   - PRM 模板名称？ （检查组织特定的模板）

---

## 必需的输入

### 员工服务 / 自助服务门户 (`POST /connect/self-service/site`):
- `siteName`（必需）- 门户名称
- `guestEmbeddedServiceConfigId`（必需）- **访客**用户嵌入式服务部署（MIAW）配置 ID
- `embeddedServiceConfigId`（可选）- **认证**用户嵌入式服务部署（MIAW）配置 ID
- `siteType`（可选）- `AURA`（默认）或 `LWR`。生成体验构建器站点。**不要**使用 Visualforce。
- `enableForGuest`（可选）- 是否允许访客（未认证）用户访问该站点
- `contentDocumentId`（可选）- 站点品牌设置中要连接的标志图像的 ContentDocument ID
- `brandColors`（可选）- 针对动作、链接、边框、文本、页面背景的 RGBA 颜色数组

> 此 API 会根据站点名称自动设置 URL 路径前缀。没有 `templateName`——框架是使用 `siteType`（Aura/LWR）选择的，永远不会使用 Visualforce。

### 合作伙伴门户（PRM）:
- `siteName`（必需）
- `siteUrlPrefix`（必需）
- `prmTemplate`（必需）
- `siteDesc`（可选）

### 通用社区 (`POST /connect/communities`):
- `name`（必需）
- `urlPathPrefix`（必需）- 仅限字母数字，不能有连字符
- `templateName`（必需）- 一个**体验构建器**模板。Aura：`Agentforce Employee Center`（员工服务首选；Agentforce 就绪），`Employee Portal`，`Customer Service`，`Help Center`，`Customer Account Portal`，`Partner Central`，`Build Your Own`。LWR：`Build Your Own (LWR)`，`Microsite (LWR)`。通过 `GET /connect/communities/templates`（见下文）验证确切的字符串。**不要**使用 `Salesforce Tabs + Visualforce` ("VF Template")——它是一个遗留的 Visualforce 站点，没有 Builder。

---

## 工作流

### 第 1 步：根据门户类型确定 API

1. **员工服务 / 自助服务** → `POST /connect/self-service/site`
   - 创建一个 **Aura**（或 LWR）体验构建器站点——永远不会使用 Visualforce
   - 在创建时将 MIAW（嵌入式服务部署）连接到站点
   - 前提条件：`CustomizeApplication` 权限；组织具有自助服务站点创建 API 访问权限；存在访客嵌入式服务部署

2. **合作伙伴（PRM）** → `POST /connect/prm/setup/sites`
   - 前提条件：`CommonPrmEnabled` 功能

3. **通用社区** → `POST /connect/communities`
   - 使用体验构建器 `templateName`（Aura 或 LWR）——永远不会使用 `Salesforce Tabs + Visualforce`
   - 前提条件：管理社区权限 (`ManageNetworks`)

---

### 第 2 步：创建门户（按类型）

#### 选项 A：员工服务 / 自助服务门户

使用自助服务站点 API。它通过部署 CustomSite、Network 和 ExperienceBundle 元数据创建一个 **Aura 体验构建器**站点（带有 Builder 选项），然后通过给定的嵌入式服务部署（ESD）配置 ID 将 MIAW 连接到站点。这是 ITSM / IT 帮助台 / 员工自助服务门户的正确路径。

**API 调用**（通过 `mcp__headless-360__dispatch`）:
```text
method: "POST"
url:    "/services/data/v67.0/connect/self-service/site"
body:
{
  "siteName": "<portal-name>",
  "siteType": "AURA",
  "guestEmbeddedServiceConfigId": "<guest-ESD-config-id>",
  "embeddedServiceConfigId": "<auth-ESD-config-id>",
  "enableForGuest": true
}
```
通过 `mcp__headless-360__dispatch_readonly` 使用专用状态路由进行轮询：
```text
method: "GET"
url:    "/services/data/v67.0/connect/self-service/site/status/{jobId}"
```
返回 `{success, siteName, urlPathPrefix, siteUrl, error, jobId, status}`。

- `siteType` 默认为 `AURA`（Aura 体验构建器 + Builder）。仅当用户明确要求 Lightning Web Runtime 站点时才传递 `LWR`。**永远**不要创建 Visualforce 站点。
- `guestEmbeddedServiceConfigId` 是**必需**的——它是访客用户的 MIAW 嵌入式服务部署配置 ID。`embeddedServiceConfigId`（认证用户）是可选的。如果用户还没有嵌入式服务部署，请让他们先创建一个（设置 → 嵌入式服务部署），或者使用 MIAW/嵌入式服务设置技能。
- 可选品牌：`contentDocumentId`（标志）和 `brandColors`（`{ "type": "action|link|border|text|pageBackground", "color": { "r": 0-255, "g": 0-255, "b": 0-255, "a": 0-1 } }`）数组。

**响应:**
```json
{
  "success": true,
  "siteName": "IT Support Portal",
  "urlPathPrefix": "itsupport",
  "siteUrl": "https://domain.my.site.com/itsupport",
  "jobId": "708...",
  "status": "Queued"
}
```

**成功**，报告 `Success:`——门户创建已开始（Aura + 体验构建器）；提供名称、框架（Aura）、`jobId` 和 `status`，并注意它在后台正在配置（Network、CustomSite、ExperienceBundle 元数据 + 嵌入式服务/MIAW 部署）。下一步：监控作业（见 'Background Job Monitoring'），然后完成第 3 步（激活 → 添加成员 → 发布）。

**失败**，报告 `Failure:` 以及 `{error}`——见“常见错误”部分，了解原因（缺少/无效的 `guestEmbeddedServiceConfigId`、名称/URL 前缀重复、组织缺乏自助服务站点创建 API 访问权限、缺少 `CustomizeApplication`）及其解决方案。

---

#### 选项 B：合作伙伴门户（PRM）

**API 调用**（通过 `mcp__headless-360__dispatch`）:
```text
method: "POST"
url:    "/services/data/v67.0/connect/prm/setup/sites"
body:
{
  "siteName": "<name>",
  "siteUrlPrefix": "<url-prefix>",
  "siteDesc": "<description>",
  "prmTemplate": "<template-name>"
}
```
同步——无需作业轮询。

**响应:**
```json
{
  "networkId": "0DB..."
}
```

**成功**，报告 `Success:`——合作伙伴门户已创建；提供名称、`networkId`、`siteUrlPrefix` 和 `prmTemplate`。下一步：在设置 → 数字体验 → 所有站点（按网络 ID）找到它，然后完成第 3 步（激活 → 添加成员 → 发布）。

**失败**，报告 `Failure:`——见“常见错误”（组织缺乏 PRM/`CommonPrmEnabled`、无效的 PRM 模板名称、名称/URL 前缀重复）。PRM 模板：设置 → 数字体验 → 设置 → 合作伙伴模板。

---

#### 选项 C：通用社区

**首先，发现有效的模板**（必需——接受的 `templateName` 字符串因组织版本而异），通过 `mcp__headless-360__dispatch_readonly`:
```text
method: "GET"
url:    "/services/data/v67.0/connect/communities/templates"
```
响应：`{ "templates": [ { "publisher": "Salesforce", "templateName": "Employee Portal" }, … ], "total": N }`。使用返回的 `templateName` 逐字复制。优先选择 **体验构建器**模板（Aura 或 LWR）。**永远**不要使用 `Salesforce Tabs + Visualforce` ("VF Template")——它是一个遗留的 Visualforce 站点，没有 Builder。

**API 调用**（通过 `mcp__headless-360__dispatch`）:
```text
method: "POST"
url:    "/services/data/v67.0/connect/communities"
body:
{
  "name": "<name>",
  "urlPathPrefix": "<url-prefix>",
  "description": "<description>",
  "templateName": "Agentforce Employee Center"
}
```
正文只接受 `{name, description, templateName, templateParams, urlPathPrefix}`——除非您需要特定模板配置，否则请省略 `templateParams`。

对于员工服务 / ITSM / HR 门户，当组织的实时模板列表中包含它时，优先选择 **`Agentforce Employee Center`** Aura 模板——它包含 IT/HR 票据、自助服务目录、知识库和 Agentforce 就绪的体验。对于更简洁、非 Agentforce 的站点，请回退到 `Employee Portal`（然后是 `Customer Service`）。其他选项按用例：`Help Center`（Aura 知识/转嫁），`Customer Account Portal`（Aura 认证账户自助服务），`Partner Central`（Aura PRM），或 `Build Your Own (LWR)` 用于现代空白 LWR 站点。

> **Agentforce Employee Center 是两层。** 此 `POST /connect/communities` 调用只提供站点。嵌入式 **Agentforce 对话式助手** 是一个单独的步骤——通过其提供的模板（`EmployeeCopilot__AgentforceEmployeeAgent`）创建内部员工代理，通过 `PATCH /services/data/v67.0/headless/invoke/einstein/genai-agentbuilder/create-copilot-from-template` (`copilotContext.company` 是**必需**的)，然后激活它并将其连接到站点。此技能提供站点并指向用户执行该步骤；完整的 Agentforce 设置不在范围内。见 `references/templates.md`。

**响应:**
```json
{
  "jobId": "08P...",
  "message": "您的站点即将准备就绪。要跟踪站点创建状态，请查询 BackgroundOperation 对象并输入 jobId 作为 Id。",
  "name": "Customer Community"
}
```

**成功**，报告 `Success:`——社区创建已开始；提供名称、`jobId`、`message`。下一步：监控作业（见 'Background Job Monitoring'），然后完成第 3 步（激活 → 添加成员 → 发布）。

**失败**，报告 `Failure:`——见“常见错误”（无效的 `templateName`——运行 `GET /services/data/v67.0/connect/communities/templates` 并使用返回的值逐字复制；名称/URL 前缀重复；缺少管理社区权限）。

---

### 第 3 步：使站点可达——激活、添加成员、发布

**创建仅提供站点**——它返回 `UnderConstruction`，仅管理员可见，带有未发布的页面，因此其 URL **尚未可达**（这是“我的门户无法工作”的首要原因）。
按顺序完成三个步骤：（1）**激活**——部署 `Network` 元数据，`<status>Live</status>`； (2) **添加成员**——将目标 **配置文件**添加到 `networkMemberGroups`（成员资格是基于配置文件而不是每个用户；例如 **`Unified Employee`** — 一个配置文件，不是 UserRole）并重新部署（可与步骤 1 结合）； (3) **发布** — `sf community publish --name "<Site Name>"`，然后轮询返回的 `jobId` 在 `BackgroundOperation` 上，直到 `Complete`。然后确认 `status: Live` 并向用户提供 **登录 URL** (`.../<prefix>/login`), 而不是裸前缀。

> **工具例外**：激活/成员使用**元数据 API** (`sf project deploy start --metadata Network:...`)，发布使用 **`sf community publish`**——没有 Connect API 用于这些（`PATCH /connect/communities/<id>` 返回 405）。这是此技能使用 headless-360 之外工具的唯一地方；第 3 步读取仍然通过 headless-360。

**确切命令、XML、验证查询和易犯错误：`references/post-creation-activate-publish.md`。**

---

### 第 4 步：编写门户创建报告（始终——最终步骤）

**始终以 `report.md` 总结所做的工作**——这是技能的最终、非可选操作，无论创建调用是否成功、仍在配置中还是失败。将其写入工作/输出目录作为 `report.md`。

报告必须：
- 以标题 `# Portal Creation Report` 开头。
- 说明 **门户名称**、使用的 **API** (`self-service/site`、`communities` 或 `prm`) 以及 **原因**（例如，"没有访客 ESD 存在 → communities API"），**框架**（Aura / LWR），以及选择的 **模板** 或 `siteType`。
- 提供 **调度请求**（路径 + 关键正文字段）和 **响应** (`jobId` / `networkId` / `siteUrl` / `status`，或错误）。
- 列出 **第 3 步剩余工作**（激活 → 添加成员 → 发布），对于员工服务站点，请注意嵌入式 Agentforce 代理是一个单独的后续步骤。
- 以确切的哨兵行结束：
  `Task completed: portal creation dispatched — see report.md`

**复制 `assets/report-template.md` 中的模板**（标题、必需字段、哨兵）并填写门户特定值。

---

## 模板建议

所有建议都生成 **体验构建器**站点（Aura 或 LWR）。**永远**不要建议 `Salesforce Tabs + Visualforce` ("VF Template")——它是一个遗留的，并且没有 Builder。

| 用例 | API | 框架 | 模板 / `siteType` |
|------|-----|-----------|-----------------------|
| 员工服务 / ITSM / HR / 帮助台（最丰富；Agentforce 就绪） | `communities` | Aura | `Agentforce Employee Center` |
| 员工服务 / 帮助台（创建时必须连接 MIAW，访客 ESD 存在） | `self-service/site` | Aura | `siteType: AURA` (+ MIAW ESD 配置) |
| 员工服务 / 帮助台（更简洁，非 Agentforce） | `communities` | Aura | `Employee Portal` (回退 `Customer Service`) |
| 客户支持 / 自助服务社区 | `communities` | Aura | `Customer Service` |
| 知识库 / 案例转嫁 | `communities` | Aura | `Help Center` |
| 认证账户自助服务 | `communities` | Aura | `Customer Account Portal` |
| 合作伙伴门户（带 PRM） | `prm/setup/sites` | Aura | 组织特定的 PRM 模板 |
| 合作伙伴门户 / 渠道（无 PRM） | `communities` | Aura | `Partner Central` |
| 现代空白 / headless 友好站点 | `communities` | LWR | `Build Your Own (LWR)` |

**现代建议：**
- 对于 **员工服务 / ITSM / HR** 门户，通过 communities API 优先选择 **`Agentforce Employee Center`** Aura 模板——它提供最丰富的员工体验（票据、目录、知识库、Agentforce 就绪）。对话式助手是一个单独的代理步骤 (`EmployeeCopilot__AgentforceEmployeeAgent`)。当门户需要在创建时连接 MIAW 时，请使用 **self-service site API** (`siteType: AURA`)；使用 `Employee Portal` 创建一个更简洁、非 Agentforce 的站点。
- 对于 **客户社区**，使用 **`Customer Service`** 模板（Aura，响应式）通过 communities API。

见 `references/templates.md` 完整模板文档。

---

## 背景作业监控

门户创建是异步的（PRM 除外）。通过 `mcp__headless-360__dispatch_readonly` 进行轮询。

**自助服务站点路径**——使用专用状态路由（首选）：
```text
method: "GET"
url:    "/services/data/v67.0/connect/self-service/site/status/{jobId}"
```
返回 `{success, siteName, urlPathPrefix, siteUrl, error, jobId, status}`。

**社区路径**——通过常规 REST 查询端点查询 `BackgroundOperation`，**不是** `/tooling/query`：
```text
method:      "GET"
url:         "/services/data/v67.0/query"
queryParams: { "q": "SELECT Id, Status FROM BackgroundOperation WHERE Id = '<jobId>'" }
```

> **工具与常规查询的区别（已验证的易犯错误）**：`BackgroundOperation` **不是** 通过此调度器有效的 Tooling API sObject——`GET /services/data/vXX.0/tooling/query` 使用该 SOQL 返回 `400 INVALID_TYPE "sObject type 'BackgroundOperation' is not supported."`。使用普通的 `/services/data/vXX.0/query` 端点；它使用相同的 SOQL 字符串成功。

> **列规范**：在 `BackgroundOperation` 上，仅选择 `Id` 和 `Status`。`JobType`、`CompletedDate` 和 `NumErrors` **不是** 该对象的列，返回 `INVALID_FIELD`。使用上面提供的 SOQL 字符串精确地。

**作业状态：**
- `Queued` / `Scheduled` — 等待开始
- `InProgress` / `Running` — 执行中
- `Complete` — 成功完成
- `Error` — 失败（检查状态路由上的 `error` 字段）

---

## 验证

创建完成后：

1. **API (主要)**：`mcp__headless-360__dispatch_readonly(url: "/services/data/v67.0/connect/communities", method: "GET")` 列出所有体验云站点。找到新站点并确认 `siteAsContainerEnabled: true`（体验构建器——Aura/LWR）和一个非空的 `builderUrl`，并且 `templateName` **不是** `Salesforce Tabs + Visualforce` ("VF Template")——它是一个遗留的 Visualforce 站点，没有 Builder。
2. **设置 UI (可选)**：设置 → 数字体验 → 所有站点。**框架** 列应显示 **Aura**（或 LWR）——不是 Visualforce——带有 **Builder** 工作区链接。
3. **测试 URL**：使用从响应中获取的 `siteUrl`（门户最初将处于非活动状态）。

**注意**：门户必须激活并发布后，外部用户才能访问它。

---

## 规则 / 限制

| 限制 | 理由 |
|---|---|
| 门户创建是异步的 | 后台部署元数据和资源 |
| 站点名称必须唯一 | 每个门户在组织中需要唯一的名称 |
| URL 前缀必须唯一 | URL 路径不能冲突 |
| URL 前缀必须为字母数字 | 不能有连字符、空格或特殊字符 |
| PRM 需要 PRM 功能 | 由许可和组织配置控制 |
| 创建的门户初始状态为非活动 | 创建后必须手动激活/发布 |
| 路径必须包含 API 版本前缀 | `dispatch`/`dispatch_readonly` 不会为您解析或注入 `/services/data/vXX.0` — 省略它将返回 `400 ROUTE_NOT_FOUND` |

---

## 按类型的前置条件

### 员工服务 / 自助服务:
- `CustomizeApplication` 权限
- 社区/数字体验已启用
- 组织已启用自助服务站点创建 API 访问权限
- 一个**访客**嵌入式服务部署（MIAW）配置存在（其 ID 是必需的）；可选认证用户 ESD 配置

### 合作伙伴（PRM）:
- 组织具有 `CommonPrmEnabled`
- 门户创建权限
- 有效的 PRM 模板名称

### 通用社区:
- 管理社区权限 (`ManageNetworks`)
- 社区/数字体验已启用
- 有效的模板名称

---

## 常见错误

### 无效的 URL 前缀:
"The URL can only contain alphanumeric characters. Remove hyphens, spaces, or special characters (e.g., 'employeeservice' not 'employee-service') and try a different prefix."

### 无效的模板名称（通用社区路径）:
"The specified template does not exist.

**解决方案:**
- 运行 `GET /services/data/v67.0/connect/communities/templates` 并使用返回的 `templateName` 逐字复制
- 优先选择体验构建器模板：`Agentforce Employee Center`（员工服务），`Employee Portal`, `Customer Service`, `Help Center`, `Customer Account Portal`, `Partner Central`, `Build Your Own`, `Build Your Own (LWR)`
- 模板名称区分大小写——完全匹配
- **不要**使用 `Salesforce Tabs + Visualforce` ("VF Template")——它是一个遗留的 Visualforce 站点，没有 Builder"

### 缺少访客嵌入式服务配置（自助服务路径）:
"The self-service site API requires a guest Embedded Service Deployment config ID.

**解决方案:**
- 在设置 → 嵌入式服务部署创建嵌入式服务部署（MIAW），或使用 MIAW/嵌入式服务设置技能
- 将其配置 ID 作为 `guestEmbeddedServiceConfigId`（可选地 `embeddedServiceConfigId` 用于认证用户）"

### PRM 未启用:
"This org doesn't have Partner Relationship Management (PRM) enabled.

**选项:**
1. 联系 Salesforce 启用 PRM 功能
2. 创建一个通用社区，使用 `Partner Central` 模板（通过 Communities API）"

### 名称/URL 重复:
"A portal with this name or URL prefix already exists (the communities API returns `400 INVALID_INPUT` — `Enter a different name. That one already exists.`).

**检查现有门户:** `mcp__headless-360__dispatch_readonly(url: "/services/data/v67.0/connect/communities", method: "GET")` 并扫描 `name` / `urlPathPrefix` 字段.

选择不同的名称或 URL 前缀。
