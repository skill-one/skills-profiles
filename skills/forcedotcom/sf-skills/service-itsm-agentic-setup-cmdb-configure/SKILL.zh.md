---
name: service-itsm-agentic-setup-cmdb-configure
description: 在 Service Cloud ITSM 中启用 CMDB（配置管理数据库）功能针对生产环境或沙盒组织：验证 CMDB 组织 SKU，配置 CMDB 租户，并启用 service-cloud-itsm-cmdb-integration 功能以提升 CMDB 访问权限。当用户要求启用 CMDB、打开配置管理数据库、配置 CMDB 租户、启用 CMDB 功能或修复 CMDB 403 FUNCTIONALITY_NOT_ENABLED 错误时使用。触发条件：启用 CMDB 功能、配置 CMDB 租户、打开 CMDB、CMDB 未启用、CMDB 403 错误、service-cloud-itsm-cmdb-integration。不触发条件：用户仅希望为用户分配 CMDB 权限集、仅安装 CMDB 内容包或直接与 CMDB 记录交互。
---

# 启用 CMDB 功能（服务云 ITSM）

通过按顺序遍历 CMDB 前置条件堆栈的前三层，将组织从“CMDB 关闭”状态转换为“CMDB 功能启用”状态。每次调用都通过 **Salesforce 托管的 Headless-360 MCP 服务器**（服务器密钥 `headless-360`）运行，并通过其四个元工具（`discover`、`describe`、`dispatch_readonly`、`dispatch`）。该组织来自当前 MCP 会话绑定的 OAuth JWT — 技能永远不会处理组织 ID、别名或凭证 — 因此，此功能在 **生产环境** 和沙盒中工作方式完全相同，无需为每个用户安装 MCP。

此技能涵盖 **0-2 层**。用户访问（第 3 层）和内容包（第 4 层）是单独的技能 — 请参阅本文件的末尾。

## 此技能提升的网关

每个 CMDB Connect API 都会检查：

```text
orgHasCMDBEnabled = orgHasCMDBPermission (org perm ITSrvcsCnfgMgmnt)  &&  OrgPreferences.CMDBEnabled
```

直到 `orgHasCMDBEnabled` 为真，CMDB API 才会返回 `403 FUNCTIONALITY_NOT_ENABLED`。`CMDBEnabled` 不是一个可以直接设置的偏好设置 — 它是在第 2 层启用功能时作为副作用翻转的。此技能的工作是使该网关返回真值。

> **对于特定用户来说，这是必要的但不总是充分的。** 提升此组织网关本身并不能让 *特定* 用户读取 CMDB 数据。某些 CMDB 读取（例如 `bundleListView`）还执行 **用户级别的** CMDB 访问，并在运行用户没有 CMDB 权限集时返回相同的 `403 FUNCTIONALITY_NOT_ENABLED`（“此用户未启用”）— 即使功能已正确启用。这是第 3 层（`service-itsm-agentic-setup-cmdb-access-assign`），而不是此技能的失败。通过功能 `status == ENABLED` 确认此技能的成功，而不是通过 CMDB 数据读取。

## 范围

- **在范围内**：验证 CMDB 组织权限（第 0 层）、触发和轮询 CMDB 租户配置（第 1 层）、预检查、启用和验证 CMDB 功能（第 2 层）。
- **超出范围**：权限集分配（第 3 层 — `service-itsm-agentic-setup-cmdb-access-assign`）、包安装（第 4 层 — `service-itsm-agentic-setup-cmdb-bundle-deploy`）、CMDB 记录 CRUD、发现 / 服务图连接器、识别规则。

## 机制

所有操作都通过 **headless-360** MCP 工具进行。读取通过 `mcp__headless-360__dispatch_readonly`，写入通过 `mcp__headless-360__dispatch` — 两者都使用原始 HTTP：`{"url": "<path>", "method": "GET|POST", "body"?: {...}, "queryParams"?: {...}}` — **不是** `{operation_id, arguments}`。有关每次调用的确切 `url` / `method` / `body`，请参阅 `references/mcp-invocation.md`。四个工具：

- `mcp__headless-360__discover` — 对索引的操作目录进行语义搜索。此技能使用的 Setup/Connect 路由不总是排名第一（或索引），因此错过并不意味着路由不存在 — 直接分派确切路径（请参阅 `references/mcp-invocation.md`）。
- `mcp__headless-360__describe` — 在任何 POST 之前拉取完整的输入模式和规范路由。
- `mcp__headless-360__dispatch_readonly` — 每个读取（GET）的分派器。
- `mcp__headless-360__dispatch` — 每个写入（POST/PATCH）的分派器。

此技能永远不会处理凭证 — 组织绑定到当前的 OAuth 会话。如果 `dispatch*` 调用返回授权错误，请告诉用户重新认证 headless-360 MCP 连接（并确认会话指向预期的组织），然后停止。

---

## 澄清问题

仅询问您无法从对话中推断出的问题：

- **哪个组织？** 确认目标组织并明确说明 **此组织将被修改**
  （租户配置和功能启用是写入操作）。对于生产环境，获取明确的确认。

不要重新询问用户已经提供的内容；预填充并注明 "(来自对话)"。

---

## 工作流

所有步骤都是按顺序执行的，并且受限制 — **不要越过失败的层。** 始终在写入之前读取：在每次变异之前运行只读检查。

### 第 0 层 — 验证 CMDB 组织 SKU（只读，硬网关）

CMDB 要求组织权限 `ITSrvcsCnfgMgmnt`，仅由版本 / 许可证 / 组织模板授予。**没有 API 可以设置它。** 验证组织是否携带 CMDB SKU 最可靠、最通用方法是探测 CMDB 权限集许可证 — 它仅存在于使用该许可证配置的组织中：

```text
dispatch_readonly({ "url": "/services/data/v63.0/query", "method": "GET", "queryParams": { "q": "SELECT Id FROM PermissionSetLicense WHERE DeveloperName = 'ItSrvcCnfgItmReadPsl'" } })
→ totalSize == 1  (已许可)   |   totalSize == 0  (未许可)
```

- **totalSize == 1** → 组织是 CMDB 许可的；继续到第 1 层。
- **totalSize == 0** → 停止。用 plain language 告诉用户（不要在用户看到的消息中包含开发者名称或 API 引用）：
  > 此组织未许可 CMDB。CMDB 的可用性由组织的版本或许可证决定，不能通过设置来启用 — 它必须在组织配置时包含。请将组织配置为 CMDB（或使用已包含 CMDB 的组织），然后再次运行此技能。

核心 Connect API `GET /services/data/v63.0/setup/org/permissions/ITSrvcsCnfgMgmnt`
(`{"isPermissionEnabled": true|false}`) 是一种替代方法，但它 **在某些组织类型上 404（包括 orgfarm 测试组织）**，因此优先使用上述 PSL 探测。请参阅
`references/mcp-invocation.md` 的详细信息。如果没有探测解决，报告组织权限无法验证，并要求用户在继续之前确认组织已许可 CMDB。

### 第 1 层 — 配置 CMDB 租户

CMDB 在一个专用的租户（CMDB 租户）上运行，该租户必须达到状态 `PROVISIONED`（异步）。

1. **检查当前状态**（读取）：
   ```text
   dispatch_readonly({ "url": "/services/data/v67.0/connect/tenantProvisioningStatus", "method": "GET" })
   ```
   根据 `status` 分支：
   - `PROVISIONED` → 已经完成；跳转到第 2 层（无触发，无轮询）。
   - `UNPROVISIONED` → 没有运行过任务；转到步骤 2 并 **触发** 它。不要等待或轮询此状态 — 等待永远不会开始配置，只会消耗预算。
   - `PROVISIONING_IN_PROGRESS` → 已经有任务在运行；**跳过触发**，直接转到步骤 3 中的轮询。
   - `FAILED` → 治理为步骤 3 中的失败情况（显示原因；不要通过 API 重试）。
2. **触发配置**（写入）— 仅当步骤 1 显示 `UNPROVISIONED` 时。首先与用户确认：
   ```text
   dispatch({ "url": "/services/data/v67.0/connect/tenantProvisioningStatus", "method": "POST" })
   ```
   触发返回后，告诉用户配置已开始，并且 **通常需要 2+ 分钟**，因此现在没有需要检查的内容。
3. **轮询** GET，直到 `status == PROVISIONED`。这是异步的，并且可靠地需要 **2+ 分钟**
   （测量的完成时间集中在 **~2 分 40 秒**），因此立即轮询是保证的无操作。**所有时间都基于响应的 `triggeredAt`，而不是此运行开始的时间** — 任务可能由更早的运行触发（来自步骤 1 的 `PROVISIONING_IN_PROGRESS` 条目）。
   将 `triggeredAt` 解析为 UTC 纪元，并计算 `elapsed = max(0, now − triggeredAt)` — 固定到 `≥ 0`，以便时钟偏差（或服务器与代理的时区不匹配）不会产生负 `elapsed`
   （永远等待）或错误超时。**如果 `triggeredAt` 缺失或无法解析**（触发 POST 响应可能尚未填充它，或者来自更早运行的进行中行可能省略它），则回退到基于此运行开始锚定 — 治理 `elapsed = 0` 并等待完整的 ~2 分钟底部，因此分支始终可确定地触发。然后：
   - `elapsed < ~2 分` → 等待 `triggeredAt` 之后约 2 分钟再进行第一次检查（跳过保证无用的早期轮询），然后每 30 秒轮询一次。
   - `~2 分 ≤ elapsed < 10 分` → **立即轮询**（初始等待已经过去 — 不要等待一个全新的 2 分钟），然后每 30 秒轮询一次。
   - `elapsed ≥ 10 分` → **不要开始一个新的等待**；将其视为下面的超时情况（报告最后看到的状态，并让用户决定）。

   总预算是从 `triggeredAt` 开始的 **10 分钟**（≈16 次检查，约 2 分钟底部后）。~2 分钟底部是一个底部，不是一个额外的延迟 — 它将典型的 ~2:40 完成时间括在几次轮询之内；不要将其延长。在初始等待期间不要轮询。一旦 `status == PROVISIONED` → 成功，继续到第 2 层。
   - `status == FAILED` → 立即停止。不要通过 API 重试 — 用 plain language 将失败原因显示给用户三个东西：
     1. **解码为人类可读文本的失败原因。** 从响应正文读取它（失败的负载携带 detail 字段，例如 `error` / `failureReason` / `message` — 解码任何 HTML 实体，如 `&lt;`/`&gt;`，并删除标记）。如果响应不携带 detail，请说明租户配置失败而没有返回原因。
     2. **指向组织的租户配置 Setup 页面的链接**，从目标组织的实例 URL 构建：`<org instance URL>/lightning/setup/CMDBProvisionalSettings/home`。
     3. **要求用户打开该页面并手动配置**，然后重新运行此技能，一旦租户显示 `PROVISIONED`。只有当手动重试也失败时，才需要 Salesforce 支持。
   - 10 分钟窗口到期 → 停止，报告最后看到的状态，并让用户决定是否继续等待（重新运行）或调查。永远不要超过 10 分钟限制。

   **在后台轮询（如果运行时允许）。** 配置是一个多分钟等待，因此用户不应闲坐。**如果 — 并且只有如果 — 执行的运行时支持后台工作**
   （例如，可以生成分离子代理或计划唤醒的代理运行时），将等待-轮询循环委托给后台任务，以便用户可以继续工作，并在它完成时报告结果
   (`PROVISIONED` / `FAILED` / 超时）。**如果运行时是单线程的转换**
   （ADK / Agentforce / headless-360 生产路径是单线程的 — 轮询循环在那里阻塞对话），则轮询 **内联**。无论如何： (a) 告诉用户 upfront 它需要几分钟，(b) 提供一个恢复路径 — 如果他们离开并且回合结束，他们可以重新运行此技能，并且第 1 层会从当前状态继续（已经 `PROVISIONED` 的租户会直接跳转到第 2 层）。永远不要 *要求* 运行时可能没有的后台原语。

### 第 2 层 — 启用 CMDB 功能（此功能提升 403 网关）

功能 API 名称是 `service-cloud-itsm-cmdb-integration`。

1. **预检查状态**（读取）：
   ```text
   dispatch_readonly({ "url": "/services/data/v67.0/connect/setup/discovery/feature/service-cloud-itsm-cmdb-integration/status", "method": "GET" })
   ```
   - `status == ENABLED` → 已经完成；跳转到验证。
   - `status == NOT_ENABLED` with `enableBlockedReasons: []` → 可以启用。
   - `enableBlockedReasons` 非空 → 停止，并将每个原因以 plain language 传达给用户
     （这些是组织仍然需要的先决条件 — 不要尝试启用）。
2. **与用户确认**，然后 **启用**（写入）：
   ```text
   dispatch({ "url": "/services/data/v67.0/connect/setup/discovery/feature/service-cloud-itsm-cmdb-integration/enable", "method": "POST", "body": {} })
   → {"success": true}
   ```
3. **验证**（读取）— 不要单独信任 POST 响应：
   ```text
   dispatch_readonly({ "url": "/services/data/v67.0/connect/setup/discovery/feature/service-cloud-itsm-cmdb-integration/status", "method": "GET" })
   → expect status == ENABLED
   ```
   **`status == ENABLED` 是此技能需要的最终 — 也是唯一 — 确认。** 第 2 层的成功或失败仅基于此检查；它**不**执行任何 CMDB 数据读取来确认网关。CMDB 数据读取（例如 `bundleListView`）还取决于 *运行用户* 自己的 CMDB 访问，因此它无法干净地确认组织级别的启用 — 请参阅“此技能提升的网关”下的注释。一旦功能显示 `ENABLED`，第 2 层就完成了。

---

## 规则 / 限制

| 限制 | 理由 |
|-----------|-----------|
| 在任何其他操作之前验证第 0 层 | 如果 `ITSrvcsCnfgMgmnt` 是关闭的，则后续步骤无法成功 — 快速失败并带有清晰的许可证消息 |
| 不要尝试通过 API 设置 `ITSrvcsCnfgMgmnt` | 没有设置器；它仅由许可证/版本/模板决定 |
| 不要直接设置 `CMDBEnabled`（例如，通过 `updateDefaultOrgPrefs`） | 它不在任何可设置偏好列表中；服务器用 500 拒绝它。它仅在启用第 2 层功能时作为副作用翻转 |
| 每次写入之前读取；每次写入后验证 | 租户 + 功能是异步/状态化的；POST 响应可能滞后于实际状态 |
| 首先确认目标组织并每次写入与用户确认 | 这些是针对实时组织的真实、难以逆转的更改 |
| 不要越过失败的或被阻塞的层 | 后续层依赖于先前的层，并且会 403 |
| 将轮询时间锚定在响应的 `triggeredAt`（解析为 UTC 纪元；elapsed = max(0, now − triggeredAt)），而不是此运行开始的时间；~2 分钟底部，然后每 30 秒，从 `triggeredAt` 开始的 10 分钟总预算。如果 `triggeredAt` 缺失/无法解析，回退到此运行开始（elapsed = 0） | 配置可靠地需要 2+ 分钟（测量 ~2:40），因此早期的轮询是保证的无操作。`PROVISIONING_IN_PROGRESS` 条目可能由更早的运行触发 — 如果已经超过 ~2 分钟底部，则立即轮询；如果已经超过 10 分钟，则报告超时，而不是等待一个全新的 2 分钟。将 elapsed 固定到 ≥ 0，以便时钟偏差 / 时区不匹配不会等待永远或错误超时；回退保持分支可确定地触发。永远不要超过 10 分钟限制 |
| 仅在运行时支持时才将轮询循环后台化；否则内联轮询 — 永远不要要求后台原语 | 用户不应因多分钟等待而闲坐，但生产 headless-360/ADK 路径是单线程的转换；要求后台轮询器的技能在那里会中断。始终提供一个重新运行恢复路径 |
| 在 `FAILED` 时，不要通过 API 重试 — 解码原因，提供 Setup URL，要求手动重试 | API 触发已经失败；用户可以从 CMDB 配置 Setup 页面重试，该页面会显示真实错误和任何手动修复 |
| 永远不要向用户暴露内部术语 | 保持记录 ID、组织 ID、HTTP 状态代码（403/500/…）、API 错误代码（`FUNCTIONALITY_NOT_ENABLED`，…）、端点名称（`bundleListView`，`tenantProvisioningStatus`）、开发者名称（`ITSrvcsCnfgMgmnt`，`CMDBEnabled`）和工具内部结构（`dispatch`，`headless-360`）远离用户界面输出。翻译为 plain language；使用人类可读的名称和状态 |

---

## 验证清单

- [ ] 第 0 层：`ITSrvcsCnfgMgmnt` 确认 `true`（或停止并带有清晰的许可证消息）？
- [ ] 第 1 层：租户 `status == PROVISIONED`？
- [ ] 第 2 层：预检查显示 `enableBlockedReasons: []` 之前启用？
- [ ] 第 2 层：启用返回 `success: true`？
- [ ] 第 2 层：验证 GET 显示 `status == ENABLED`？ **(这是唯一的成功标准 — 不使用 CMDB 数据读取来确认)**
- [ ] 首先确认目标组织并每次写入与用户确认？

---

## 输出预期

```text
CMDB 功能启用 — 完成（通过 service-itsm-agentic-setup-cmdb-configure）

目标组织：<org>

  CMDB 许可证 .................. 存在
  CMDB 租户 ................... 已配置
  CMDB 功能 .................. 已启用

CMDB 现在已在此组织中启用。下一步：
  • 分配用户访问  → service-itsm-agentic-setup-cmdb-access-assign
  • 安装基础包  → service-itsm-agentic-setup-cmdb-bundle-deploy
```

请将内部术语排除在面向用户输出之外（不要包含记录ID、HTTP状态码、错误代码、端点或开发者名称）。如果任何步骤失败，请停止并告知用户——用平实的语言——哪个设置部分未成功以及这对他们意味着什么，然后指向相关的修复方法。将任何原始错误（例如403或`FUNCTIONALITY_NOT_ENABLED`）翻译成其含义（“CMDB尚未启用”），而不是重复代码。

---

## 常见失败（用平实的语言揭示这些问题）

| 症状 | 可能的原因 | 告知用户的内容 |
|------|----------|----------------|
| 层级0返回`false` | 组织缺少CMDB SKU | 许可证/版本先决条件——API无法授予它；为组织提供CMDB |
| CMDB读取时出现`403 FUNCTIONALITY_NOT_ENABLED` **而功能`status != ENABLED`** | 功能尚未启用（层级2不完整） | 完成层级2；只有功能启用后，门槛才会解除 |
| `bundleListView`出现`403 FUNCTIONALITY_NOT_ENABLED` **而功能`status == ENABLED`** | 功能已启用；运行用户缺少CMDB权限集（`bundleListView`也强制执行用户级访问） | 这不是层级2的失败——这是层级3；运行`service-itsm-agentic-setup-cmdb-access-assign`为用户授予CMDB访问权限 |
| 功能启用受阻（`enableBlockedReasons`非空） | 组织仍需要的缺失依赖项 | 传达每个原因；首先解决这些问题，然后重试 |
| 租户卡在`UNPROVISIONED` / `PROVISIONING_IN_PROGRESS` / 长时间运行 | 配置是异步的 | 通常需要~2-3分钟；在10分钟的预算内保持轮询或重试触发器 |
| 租户`FAILED` | Salesforce端的配置作业失败 | 分享解码的失败原因 + 组织的`/lightning/setup/CMDBProvisionalSettings/home`链接，并要求用户在那里手动重试配置；只有手动重试也失败时才升级到Salesforce支持 |
| `dispatch*`认证错误 | headless-360 MCP会话未认证/令牌过期 | 重新认证headless-360 MCP连接并确认会话指向预期的组织 |

---

## 参考文件索引

| 文件 | 何时阅读 |
|------|--------|
| `references/mcp-invocation.md` | 每个层级0-2调用的确切`dispatch*` url/method/body、响应信封和错误表 |
