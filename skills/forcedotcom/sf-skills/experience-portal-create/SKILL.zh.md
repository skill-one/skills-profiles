---
name: experience-portal-create
description: 创建/配置/设置一个新的数字体验（社区）/体验云站点——员工服务、IT支持、帮助台、人力资源、客户和合作伙伴门户——通过headless-360 MCP站点创建API。每当用户要求创建/配置/设置门户、站点或社区时使用，例如：“创建一个员工服务门户”、“创建一个IT支持门户”、“创建一个Agentforce员工中心”，并在创建时连接MIAW（应用/网页消息）。这是站点创建技能，并拥有从头开始配置新的Aura或LWR体验构建器站点——即使用户说“体验构建器站点”或“LWR站点”，只要想要一个新站点就触发它。它始终在最后一步写入门户创建报告（不是通过CLI的临时方式）并且永远不会创建遗留的Tabs+Visualforce站点。不要仅为了修改现有站点的页面/路由/主题/品牌/访客访问元数据（experience-lwr-site-generate）、现有站点定制（experience-ui-bundle）、CMS、电子商务而触发。
---

# 创建数字体验门户

在 Salesforce 中创建一个新的数字体验（以前称为 Communities）门户/站点。支持员工服务门户、合作伙伴门户（PRM）以及通用客户社区。

**所有操作都通过 headless-360 MCP 服务器运行** (`mcp__headless-360__discover` →
`mcp__headless-360__describe` → `mcp__headless-360__dispatch` / `mcp__headless-360__dispatch_readonly`).
**不要**使用 Salesforce CLI（其 `api request`、`data query` 或 `org open` 子命令）、项目代码y MCP 服务器、原始 `curl` 或任何其他 HTTP 客户端 — `dispatch`/`dispatch_readonly` 是此技能与组织通信的唯一方式。有关确切调用形状，请参阅 `references/mcp-invocation.md`。

## 范围

- **在范围内**：通过 headless-360 Connect API 调度器创建数字体验站点。门户类型选择。基本配置（名称、URL、模板）。带嵌入式服务配置的自服务门户。**使站点端到端可达** — 激活网络 (`status: Live`)、添加成员资料，并发布体验构建器页面（参见 `references/post-creation-activate-publish.md`）。
- **超出范围**：深度创建后定制（在构建器中页面布局/组件创作）。内容创作。初始设置之外的品牌。单个用户记录管理（成员资格是在资料/权限集级别添加的，而不是每个用户）。

---

## 执行模型（先阅读）

每个组织调用都是一个 **调度**：`mcp__headless-360__dispatch_readonly(url, method: "GET", queryParams)`
用于读取，`mcp__headless-360__dispatch(url, method, body)` 用于写入；从响应中读取 `status_code` + `body`。要解析门户类型的端点，使用 `mcp__headless-360__discover(query=...)` 和
`mcp__headless-360__describe(id=...)` 作为需要。体验云的 Connect API 创建/列表操作不总是由 `discover`/`describe` 索引 — 当查找返回无结果时，直接调度众所周知的版本化 Connect API 路径（参见 `references/mcp-invocation.md`），而不是得出功能缺失的结论。

**关键：路径必须包含完整的 `/services/data/vXX.0/...` 前缀**（例如
`"/services/data/v67.0/connect/communities"`) — 与其他一些调度器不同，headless-360 不为您解析或注入 API 版本。没有版本前缀的路径返回 `400 ROUTE_NOT_FOUND`。当可用时，从 `discover`/`describe` 结果中逐字复制路径；否则使用此技能示例中显示的版本（编写时为 `v67.0`）并调整如果组织运行不同版本。完整详细信息、响应信封、作业监控和注意事项位于 `references/mcp-invocation.md`。

---

## 澄清问题

在继续之前确定：

1. **门户类型？**
   - 员工服务 / ITSM / HR / 帮助台 → **优先选择通过社区 API 的 `Agentforce Employee Center` Aura 模板**（最丰富的员工体验；Agentforce 准备就绪）。当 MIAW 必须在创建时连接时，并且存在访客 ESD 时，请使用自服务 API。
   - 合作伙伴门户（PRM）→ 需要 PRM 功能启用
   - 客户社区 → 通用社区创建（Aura 或 LWR 体验构建器模板）

2. **基本设置（所有类型都需要）：**
   - 门户名称？
   - URL 前缀？（必须只包含字母数字，不能包含连字符或空格）
   - 描述（可选）

3. **对于员工服务 / 自服务门户：**
   - `siteType`？ → 默认 `AURA`（Aura 体验构建器 + 构建器）。如果用户明确想要 Lightning Web Runtime 站点，则仅使用 `LWR`。**永远**不要创建 Salesforce Tabs + Visualforce ("VF Template") 站点 — 那些是遗留的，并且没有构建器。
   - MIAW / 嵌入式服务部署 ID？这些在创建时将 Messaging for In-App 和 Web 连接到门户中。自服务 API 需要 **访客** ESD 配置；**认证用户** ESD 配置是可选的。如果用户还没有创建嵌入式服务部署，请指导他们首先指向设置 → 嵌入式服务部署。

4. **仅适用于合作伙伴门户：**
   - PRM 模板名称？（检查组织特定的模板）

---

## 必须输入

### 员工服务 / 自服务门户 (`POST /connect/self-service/site`):
- `siteName`（必需）- 门户名称
- `guestEmbeddedServiceConfigId`（必需）- 嵌入式服务部署（MIAW）配置 ID 用于 **访客** 用户
- `embeddedServiceConfigId`（可选）- 嵌入式服务部署（MIAW）配置 ID 用于 **认证** 用户
- `siteType`（可选）- `AURA`（默认）或 `LWR`。生成体验构建器站点。**不要**使用 Visualforce。
- `enableForGuest`（可选）- 访客（未认证）用户是否可以访问该站点
- `contentDocumentId`（可选）- 站点品牌设置中要连接的标志图像的 ContentDocument ID
- `brandColors`（可选）- 目标 `action`、`link`、`border`、`text`、`pageBackground` 的 RGBA 颜色数组

> 此 API 会根据站点名称自动设置 URL 路径前缀。没有 `templateName` — 框架是使用 `siteType`（Aura/LWR）选择的，永远不会使用 Visualforce。

### 合作伙伴门户（PRM）:
- `siteName`（必需）
- `siteUrlPrefix`（必需）
- `prmTemplate`（必需）
- `siteDesc`（可选）

### 通用社区 (`POST /connect/communities`):
- `name`（必需）
- `urlPathPrefix`（必需）- 仅限字母数字，不能包含连字符
- `templateName`（必需）- 一个 **体验构建器** 模板。Aura: `Agentforce Employee Center`（员工服务首选）、`Employee Portal`、`Customer Service`、`Help Center`、`Customer Account Portal`、`Partner Central`、`Build Your Own`。LWR: `Build Your Own (LWR)`、`Microsite (LWR)`。通过 `GET /connect/communities/templates` 验证确切的字符串（见下文）。**不要**使用 `Salesforce Tabs + Visualforce` ("VF Template") — 它是一个遗留的 Visualforce 站点，没有构建器。
- `description`（可选）

---

## 工作流

### 第 1 步：根据门户类型确定 API

1. **员工服务 / 自服务** → `POST /connect/self-service/site`
   - 创建 **Aura**（或 LWR）体验构建器站点 — 永远不要使用 Visualforce
   - 在创建时将 MIAW（嵌入式服务部署）连接到站点
   - 前提条件：`CustomizeApplication` 权限；组织具有自服务站点创建 API 访问权限；存在访客嵌入式服务部署

2. **合作伙伴（PRM）** → `POST /connect/prm/setup/sites`
   - 前提条件：`CommonPrmEnabled` 功能

3. **通用社区** → `POST /connect/communities`
   - 使用体验构建器 `templateName`（Aura 或 LWR）— 永远不要使用 `Salesforce Tabs + Visualforce`
   - 前提条件：管理社区权限 (`ManageNetworks`)

---

### 第 2 步：创建门户（按类型）

#### 选项 A：员工服务 / 自服务门户

使用自服务站点 API。它通过部署 CustomSite、Network 和 ExperienceBundle 元数据创建 **Aura 体验构建器** 站点（带构建器选项），然后通过给定的嵌入式服务部署（ESD）配置 ID 将 MIAW 连接到站点。这是 ITSM / IT 帮助台 / 员工自服务门户的正确路径。

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
通过 `mcp__headless-360__dispatch_readonly` 使用 `GET /services/data/v67.0/connect/self-service/site/status/{jobId}` 进行轮询。

- `siteType` 默认为 `AURA`（Aura 体验构建器 + 构建器）。仅当用户明确要求 Lightning Web Runtime 站点时才传递 `LWR`。永远不要创建 Visualforce 站点。
- `guestEmbeddedServiceConfigId` 是 **必需** 的 — 它是访客用户的 MIAW 嵌入式服务部署配置 ID。`embeddedServiceConfigId`（认证用户）是可选的。如果用户还没有嵌入式服务部署，请指导他们首先创建一个（设置 → 嵌入式服务部署），或使用 MIAW/嵌入式服务设置技能。
- 可选品牌：`contentDocumentId`（标志）和 `brandColors`（`{ "type": "action|link|border|text|pageBackground", "color": { "r": 0-255, "g": 0-255, "b": 0-255, "a": 0-1 } }` 数组).

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

**成功**，报告 `Success:` — 门户创建已开始（Aura + 体验构建器）；提供名称、框架（Aura）、`jobId` 和 `status`，并注意它在后台配置中（Network、CustomSite、ExperienceBundle 元数据 + 嵌入式服务/MIAW 部署）。下一步：监控作业（见“后台作业监控”），然后完成第 3 步（激活 → 添加成员 → 发布）。

**失败**，报告 `Failure:` 并提供 `{error}` — 参见“常见错误”部分了解原因（缺少/无效的 `guestEmbeddedServiceConfigId`、名称/URL 前缀重复、组织缺乏自服务站点创建 API 访问权限、缺少 `CustomizeApplication`）及其解决方案。

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
同步 — 无需作业轮询。

**响应:**
```json
{
  "networkId": "0DB..."
}
```

**成功**，报告 `Success:` — 合作伙伴门户已创建；提供名称、`networkId`、`siteUrlPrefix` 和 `prmTemplate`。下一步：在设置 → 数字体验 → 所有站点（按网络 ID）找到它，然后完成第 3 步（激活 → 添加成员 → 发布）。

**失败**，报告 `Failure:` — 参见“常见错误”（组织缺乏 PRM/`CommonPrmEnabled`、无效的 PRM 模板名称、名称/URL 前缀重复）。PRM 模板：设置 → 数字体验 → 设置 → 合作伙伴模板。

---

#### 选项 C：通用社区

**首先，发现有效的模板**（必需 — 接受的 `templateName` 字符串因组织版本/版本而异），通过 `mcp__headless-360__dispatch_readonly`:
```text
method: "GET"
url:    "/services/data/v67.0/connect/communities/templates"
```
响应：`{ "templates": [ { "publisher": "Salesforce", "templateName": "Employee Portal" }, … ], "total": N }`。使用返回的 `templateName` 逐字。优先选择 **体验构建器** 模板（Aura 或 LWR）。永远不要使用 `Salesforce Tabs + Visualforce`。

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
正文仅接受 `{name, description, templateName, templateParams, urlPathPrefix}` — 除非您需要模板特定配置，否则省略 `templateParams`。

对于 **员工服务 / ITSM / HR 门户**，当组织的实时模板列表中包含它时，优先选择 **`Agentforce Employee Center`** 模板 — 它提供 IT/HR 票据、自服务目录、知识库和 Agentforce 准备就绪的体验。对于更简单的非 Agentforce 站点，请回退到 `Employee Portal`（然后是 `Customer Service`）。其他选项按用例：`Help Center`（Aura 知识/转介）、`Customer Account Portal`（Aura 认证账户自服务）、`Partner Central`（Aura PRM），或 `Build Your Own (LWR)` 用于现代空白 LWR 站点。

> **Agentforce Employee Center 是两层。** 此 `POST /connect/communities` 调用仅提供站点。嵌入的 **Agentforce 对话式助手** 是一个单独的步骤 — 通过其提供的模板 (`EmployeeCopilot__AgentforceEmployeeAgent`) 使用 `PATCH /services/data/v67.0/headless/invoke/einstein/genai-agentbuilder/create-copilot-from-template` (`copilotContext.company` 是 **必需** 的)，然后激活它并将其连接到站点。此技能提供站点并指导用户执行该步骤；完整的 Agentforce 设置超出范围。参见 `references/templates.md`。

**响应:**
```json
{
  "jobId": "08P...",
  "message": "您的站点几乎准备好了。要跟踪站点创建状态，请查询 BackgroundOperation 对象并输入 jobId 作为 Id。",
  "name": "Customer Community"
}
```

**成功**，报告 `Success:` — 社区创建已开始；提供名称、`jobId` 和
`message`。下一步：监控作业（见“后台作业监控”），然后完成第 3 步（激活 → 添加成员 → 发布）。

**失败**，报告 `Failure:` — 参见“常见错误”（无效的 `templateName` — 运行
`GET /services/data/v67.0/connect/communities/templates` 并使用返回的值逐字；名称/URL 前缀重复；缺少管理社区权限）。

---

### 第 3 步：使站点可达 — 激活、添加成员、发布

**仅创建会提供站点** — 它返回 `UnderConstruction`、仅管理员访问、未发布的页面，因此其 URL **尚未可达**（“我的门户无法工作”的首要原因是）。按顺序完成三个步骤： (1) **激活** — 部署 `Network` 元数据，`<status>Live</status>`； (2) **添加成员** — 将目标 **资料** 添加到 `networkMemberGroups`（成员资格是基于资料而不是每个用户；例如 **`Unified Employee`** — 一个资料，而不是 UserRole）并重新部署（可与步骤 1 结合）； (3) **发布** — `sf community publish --name "<Site Name>"`，然后轮询返回的 `jobId` 在 `BackgroundOperation` 上，直到 `Complete`。然后确认 `status: Live` 并向用户提供 **登录 URL**
(`.../<prefix>/login`)，而不是裸前缀。

> **工具例外**：激活/成员使用 **元数据 API** (`Network` 部署) 并发布使用 **`sf community publish`** — 没有用于这些的 Connect API (`PATCH /connect/communities`
> 返回 405)。这是此技能使用除 headless-360 外的工具的唯一地方；第 3 步读取仍然通过 headless-360。

**确切命令、XML、验证查询和注意事项：`references/post-creation-activate-publish.md`。**

---

### 第 4 步：编写门户创建报告（始终 — 最后一步）

**始终以 `report.md` 总结所做的工作** — 这是技能的最终、非可选操作，无论创建调用是否成功、仍在配置中还是失败。将其写入工作/输出目录作为 `report.md`。

报告必须：
- 以标题 `# Portal Creation Report` 开头。
- 说明 **门户名称**、使用的 **API** (`self-service/site`、`communities` 或 `prm`) 以及 **原因**（例如。 "没有访客 ESD → communities API"）、**框架**（Aura / LWR）以及选择的 **模板** 或 `siteType`。
- 提供 **调度请求**（路径 + 关键正文字段）和 **响应** (`jobId` /
> `networkId` / `siteUrl` / `status` 或错误）。
- 列出 **剩余的第 3 步工作**（激活 → 添加成员 → 发布），对于员工服务站点，请注意 **嵌入的 Agentforce 代理是一个单独的后续步骤**。
- 以以下哨兵行结束，完全：
  `Task completed: portal creation dispatched — see report.md`

**复制 `assets/report-template.md` 中的模板** 并填写门户特定值。

---

## 模板建议

所有建议都生成 **体验构建器** 站点（Aura 或 LWR）。永远不要建议 `Salesforce Tabs + Visualforce` ("VF Template") — 它是遗留的，并且没有构建器。

| 使用场景 | API | 框架 | 模板 / `siteType` |
|----------|-----|-----------|-----------------------|
| 员工服务 / ITSM / HR / 帮助台（最丰富；Agentforce兼容） | `communities` | Aura | `Agentforce 员工中心` |
| 员工服务 / 帮助台（创建时为MIAW，存在访客ESD） | `self-service/site` | Aura | `siteType: AURA` (+ MIAW ESD配置) |
| 员工服务 / 帮助台（更简洁，无Agentforce） | `communities` | Aura | `员工门户`（后备`客户服务`） |
| 客户支持 / 自助服务社区 | `communities` | Aura | `客户服务` |
| 知识库 / 案例分流 | `communities` | Aura | `帮助中心` |
| 认证账户自助服务 | `communities` | Aura | `客户账户门户` |
| 合作伙伴门户（带PRM） | `prm/setup/sites` | Aura | 组织特定的PRM模板 |
| 合作伙伴门户 / 渠道（无PRM） | `communities` | Aura | `合作伙伴中心` |
| 现代空白 / Headless友好站点 | `communities` | LWR | `自定义构建 (LWR)` |

**现代推荐：**
- 对于**员工服务 / ITSM / HR**门户，通过communities API优先选择**`Agentforce 员工中心`** Aura模板——它提供了最完整的员工体验（工单、目录、知识库、Agentforce兼容）。对话式助手是单独的代理步骤（`EmployeeCopilot__AgentforceEmployeeAgent`）。当门户需要在创建时接入MIAW且存在访客嵌入式服务部署时，使用**自助服务站点API**（`siteType: AURA`）；使用`员工门户`创建更简洁的非Agentforce站点。
- 对于**客户社区**，通过communities API使用**`客户服务`**模板（Aura，移动响应式）。

参考`references/templates.md`获取完整的模板文档。

---

## 背景任务监控

门户创建是异步的（PRM除外，为同步）。通过`mcp__headless-360__dispatch_readonly`轮询。

**自助服务站点路径**——使用专用的类型化状态路由（推荐）：
```text
method: "GET"
url:    "/services/data/v67.0/connect/self-service/site/status/{jobId}"
```
返回`{success, siteName, urlPathPrefix, siteUrl, error, jobId, status}`。

**社区路径**——通过常规REST查询端点查询`BackgroundOperation`，**不是**`/tooling/query`：
```text
method:      "GET"
url:         "/services/data/v67.0/query"
queryParams: { "q": "SELECT Id, Status FROM BackgroundOperation WHERE Id = '<jobId>'" }
```

> **工具与常规查询（已验证的陷阱）**：`BackgroundOperation`通过此调度器**不是**有效的工具API sObject——`GET /services/data/vXX.0/tooling/query`带有该SOQL返回`400 INVALID_TYPE "sObject type 'BackgroundOperation' is not supported."`。使用普通的`/services/data/vXX.0/query`端点；它用相同的SOQL字符串成功。
> **列规范**：在`BackgroundOperation`上，仅选择`Id`和`Status`。`JobType`、`CompletedDate`和`NumErrors`**不是**此对象的列，返回`INVALID_FIELD`。使用上述SOQL字符串。

**任务状态：**
- `Queued` / `Scheduled` — 等待开始
- `InProgress` / `Running` — 执行中
- `Complete` — 成功完成
- `Error` — 失败（检查状态路由上的`error`字段）

---

## 验证

创建完成后：

1. **API（主要）**：`mcp__headless-360__dispatch_readonly(url: "/services/data/v67.0/connect/communities", method: "GET")`列出所有Experience Cloud站点。找到新站点并确认`siteAsContainerEnabled: true`（Experience Builder — Aura/LWR）和非空的`builderUrl`，且`templateName`**不是**`Salesforce Tabs + Visualforce`。`siteAsContainerEnabled: false`表示遗留Visualforce站点——这是此技能存在的目的以避免的bug。
2. **设置UI（可选）**：设置 → 数字体验 → 所有站点。**框架**列应显示**Aura**（或LWR）——不是Visualforce——并带有**构建器**工作区链接。
3. **测试URL**：使用响应中的`siteUrl`（门户初始将处于非活动状态）。

**注意**：门户必须激活并发布，外部用户才能访问。

---

## 规则 / 限制

| 限制 | 理由 |
|---|---|
| 门户创建是异步的 | 后台部署元数据并配置资源 |
| 站点名称必须唯一 | 每个门户在组织中需要唯一的名称 |
| URL前缀必须唯一 | URL路径不能冲突 |
| URL前缀必须为字母数字 | 不允许连字符、空格或特殊字符 |
| PRM需要PRM功能 | 由许可和组织配置控制 |
| 创建的门户初始为非活动状态 | 创建后必须手动激活/发布 |
| 路径必须包含API版本前缀 | `dispatch`/`dispatch_readonly`不会注入`/services/data/vXX.0`——省略它返回`400 ROUTE_NOT_FOUND` |

---

## 按类型划分的先决条件

### 员工服务 / 自助服务：
- `CustomizeApplication`权限
- 已启用Communities/Digital Experience
- 组织已启用自助服务站点创建API访问
- 存在**访客**嵌入式服务部署（MIAW）配置（其ID是必需的）；可选地存在认证用户ESD配置

### 合作伙伴（PRM）：
- 组织已启用`CommonPrmEnabled`
- 门户创建权限
- 有效的PRM模板名称

### 一般社区：
- 管理社区权限（`ManageNetworks`）
- 已启用Communities/Digital Experience
- 有效的模板名称

---

## 常见错误

### 无效的URL前缀：
"The URL can only contain alphanumeric characters. Remove hyphens, spaces, or special characters (e.g., 'employeeservice' not 'employee-service') and try a different prefix."

### 无效的模板名称（一般社区路径）：
"The specified template does not exist.

**解决方法：**
- 运行`GET /services/data/v67.0/connect/communities/templates`并使用返回的`templateName`原样使用
- 优先使用Experience Builder模板：`Agentforce 员工中心`（员工服务）、`员工门户`、`客户服务`、`帮助中心`、`客户账户门户`、`合作伙伴中心`、`自定义构建`、`自定义构建 (LWR)`
- 模板名称区分大小写——完全匹配
- **不要**使用`Salesforce Tabs + Visualforce`("VF Template")——它是遗留的Visualforce站点且无构建器"

### 缺失访客嵌入式服务配置（自助服务路径）：
"The self-service site API requires a guest Embedded Service Deployment config ID.

**解决方法：**
- 在设置 → 嵌入式服务部署创建嵌入式服务部署（MIAW），或使用MIAW/嵌入式服务设置技能
- 将其配置ID作为`guestEmbeddedServiceConfigId`（以及可选的`embeddedServiceConfigId`用于认证用户）"

### PRM未启用：
"This org doesn't have Partner Relationship Management (PRM) enabled.

**选项：**
1. 联系Salesforce启用PRM功能
2. 使用`Partner Central`模板创建一般社区（通过Communities API）"

### 重复名称/URL：
"A portal with this name or URL prefix already exists (the communities API returns `400 INVALID_INPUT` — `Enter a different name. That one already exists.`).

**检查现有门户**：`mcp__headless-360__dispatch_readonly(url: "/services/data/v67.0/connect/communities", method: "GET")`并扫描`name` / `urlPathPrefix`字段。

选择不同的名称或URL前缀。"

### 缺失权限：
"You don't have permission to create portals.

**所需权限：**
- 自助服务门户：`CustomizeApplication`
- 一般社区：`ManageNetworks`（管理社区）

联系您的Salesforce管理员请求这些权限。"

### 路径未找到（缺少版本前缀）：
"`400 ROUTE_NOT_FOUND` on a path that otherwise matches this skill's documentation. Confirm the `url` includes the full `/services/data/vXX.0/...` prefix — `dispatch`/`dispatch_readonly` require it verbatim and won't add it for you. If a specific version 404s, try the version shown in a recent `discover`/`describe` result for that org。"

---

## 相关操作

**创建后：**
- 激活门户——设置 → 数字体验 → 所有站点 → 激活
- 配置品牌——自定义颜色、标志、主题
- 添加页面/组件——使用Experience Builder
- 设置用户访问——配置文件、权限集、共享规则
- 发布门户——使外部用户可访问

**管理现有：**
- 列出门户——`mcp__headless-360__dispatch_readonly(url: "/services/data/v67.0/connect/communities", method: "GET")`
- 更新设置——网络工具API或元数据API
- 停用——通过设置UI

---

## 重要提示

1. **创建是异步的**（PRM除外）并仅配置——API返回作业ID，门户返回`UnderConstruction`、无成员且未发布，因此其URL**不可达**，直到您完成步骤3（激活 → 添加成员 → 发布；参考`references/post-creation-activate-publish.md`）。
2. **URL前缀成为站点路径**——`https://<domain>.my.site.com/<prefix>`（在`.../<prefix>/login`处服务/登录，而不是裸前缀）。
3. **嵌入式服务 / MIAW配置必须预先存在**——此技能不创建嵌入式服务部署。在设置 → 嵌入式服务部署（或通过MIAW/嵌入式服务设置技能）单独创建它们，然后将配置ID传递给自助服务站点API。对于一般社区，MIAW通过Experience Builder中的嵌入式服务组件在创建后添加。
4. **模板名称区分大小写**——在尝试创建前验证您组织中的可用模板。
7. **discover/describe可能无法通过id解析特定的Connect API操作**——headless-360语料库将许多操作索引为多步SOR而不是单个端点，某些标准Connect API写入（例如`POST /connect/communities`）未被单独索引。不要断定功能缺失；直接调度文档中记录的、版本化的Connect API路径（在此技能中记录）。

---

## 参考文档

- `references/mcp-invocation.md` — **阅读每个会话。**确切的`mcp__headless-360__*`调用形状、版本前缀要求、响应包、作业监控、`BackgroundOperation`列/端点规范和陷阱。
- `references/templates.md` — 可用模板、模板参数、选择指南。
- `references/post-creation-activate-publish.md` — 步骤3（激活、添加成员、发布）使站点可访问：元数据API + `sf community publish`路径、`PATCH`上的405陷阱、`NetworkMemberGroup`列规范和登录URL提示。
- `assets/report-template.md` — 步骤4 `report.md`模板复制（标题、必需字段、哨兵）。

---

## API类型分类

**站点创建**通过`mcp__headless-360__dispatch` / `mcp__headless-360__dispatch_readonly`（永远不要项目代码化或原始HTTP）调度。所有路径都包含`/services/data/vXX.0`前缀。**创建后（步骤3）是例外**：激活网络和添加成员使用**元数据API**（`sf project deploy start --metadata Network:...`），发布使用**`sf community publish`**——没有Connect API用于这些（`PATCH /connect/communities/<id>`返回405）。步骤3的读取/验证仍然通过headless-360。创建路径：

- **自助服务门户**：Connect API `POST /services/data/vXX.0/connect/self-service/site` — 异步（轮询`GET /services/data/vXX.0/connect/self-service/site/status/{jobId}`)
- **PRM门户**：Connect API `POST /services/data/vXX.0/connect/prm/setup/sites` — 同步
- **一般社区**：Connect API `POST /services/data/vXX.0/connect/communities` — 异步（轮询`BackgroundOperation`通过`GET /services/data/vXX.0/query`，不是`/tooling/query`）
