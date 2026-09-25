# 部署 CMDB 基础组件包（服务云 ITSM）

安装**CMDB 基础（基础）**内容组件包——即开箱即用的配置项类型、架构和内容，使 CMDB 可用。这是**第 4 层**，CMDB 设置堆栈的最终层，并且需要 CMDB 功能已启用（第 2 层）。每次调用都通过**Salesforce 托管的 Headless-360 MCP 服务器**（服务器密钥 `headless-360`）及其四个元工具（`discover`、`describe`、`dispatch_readonly`、`dispatch`）进行。组织是从当前 OAuth 会话绑定的 OAuth JWT 派生的——技能从不处理组织 ID、别名或凭证——因此此操作在**生产环境**和沙盒中完全相同，无需为每个用户单独安装 MCP。

## 范围

- **在范围内**：确认 CMDB 已启用、读取实时组件包目录、解析基础组件包的确切版本、安装**基础**（`CMDB 基础`）组件包并验证。
- **超出范围**：启用 CMDB 功能/配置 CMDB 租户（第 0-2 层——`service-itsm-agentic-setup-cmdb-configure`）、分配权限集（第 3 层——`service-itsm-agentic-setup-cmdb-access-assign`）、安装**可选附加组件**包（例如组件识别规则）、CMDB 记录 CRUD 或发现。

此技能仅安装**基础组件包**。可选附加组件有意超出范围。

## 顺序为何重要

组件包 Connect API（`bundleListView`、`bundles/details`、`bundleInstallation`）受 `orgHasCMDBEnabled` 保护。在启用 CMDB 功能之前，它们返回 `403 FUNCTIONALITY_NOT_ENABLED`，因此此技能**必须**在 CMDB 功能启用技能将该功能打开后运行。

除了组织门控之外，这些读取还强制执行**运行用户自身的 CMDB 访问权限**，因此这里的 `403 FUNCTIONALITY_NOT_ENABLED` 有两个不同的原因——功能关闭**或**用户无访问权限。步骤 1 通过在将用户发送到任何地方之前检查功能状态来消除歧义；永远不要假设 403 表示功能已关闭。

## 机制

所有操作都通过**headless-360** MCP 工具进行。读取通过 `mcp__headless-360__dispatch_readonly`，写入通过 `mcp__headless-360__dispatch`——两者都使用原始 HTTP：`{"url": "<路径>", "method": "GET|POST", "body"?: {...}, "queryParams"?: {...}}`——**不是**`{operation_id, arguments}`。有关每次调用的确切 `url` / `method` / `body`，请参阅 `references/mcp-invocation.md`。四个工具：

- `mcp__headless-360__discover` — 对索引的操作目录进行语义搜索（仅发现/确认）。
- `mcp__headless-360__describe` — 在安装 POST 之前拉取完整的输入架构和规范路由。
- `mcp__headless-360__dispatch_readonly` — 每个读取（GET）的分发器。
- `mcp__headless-360__dispatch` — 每个写入（POST/PATCH）的分发器。

技能从不处理凭证——组织绑定到当前的 OAuth 会话。如果 `dispatch*` 调用返回授权错误，请指示用户重新验证 headless-360 MCP 连接（并确认会话指向预期的组织），然后停止。

---

## 澄清问题

仅询问您无法从对话中推断出的问题：

- **哪个组织？** 确认目标组织并明确说明**内容将安装到此组织**（写入）。对于生产环境，获取明确确认。

不要重新询问用户已提供的内容；预填充并注明 "(来自对话)"。

---

## 工作流

顺序执行。**始终在写入之前读取**——在安装之前读取目录并解析确切版本。永远不要猜测版本字符串。

### 步骤 1 — 确认 CMDB 已启用（读取，门控）

```text
dispatch_readonly({ "url": "/services/data/v67.0/connect/cmdb/bundleListView", "method": "GET" })
```

- `200` → CMDB 已启用；响应列出了可用组件包及其安装状态。继续。
- `403 FUNCTIONALITY_NOT_ENABLED` → **模糊不清——在告诉用户 CMDB 已关闭之前消除歧义。** 此读取强制执行**组织门控**和**运行用户自身的 CMDB 访问权限**，因此 403 有两个可能的原因。检查功能状态以区分它们：
  ```text
  dispatch_readonly({ "url": "/services/data/v67.0/connect/setup/discovery/feature/service-cloud-itsm-cmdb-integration/status", "method": "GET" })
  ```
  - `status != ENABLED` → **CMDB 功能未启用**。停止，并将用户路由到 CMDB 功能启用技能（`service-itsm-agentic-setup-cmdb-configure`）。
  - `status == ENABLED` → 功能**已启用**；运行用户仅**缺少 CMDB 权限集**。停止，并将用户路由到 CMDB 访问分配技能（`service-itsm-agentic-setup-cmdb-access-assign`）以授予自己 CMDB 访问权限——至少需要读取集，加上**类型管理器**以进行组件包管理——然后重试。**不要**将他们发送到功能启用技能；CMDB 已启用。

从 `bundleListView` 响应中识别基础组件包（CMDB 基础）并记下其 `currentInstalledVersion`。如果它已安装在最新版本，请告知用户无需执行任何操作。

### 步骤 2 — 解析确切的基础版本（读取）

**不要猜测或硬编码版本**。从组件包详细信息中读取权威版本：

```text
dispatch_readonly({ "url": "/services/data/v67.0/connect/cmdb/bundles/details", "method": "GET", "queryParams": { "bundleIdentifier": "base" } })
```

从目录中读取 `latestVersion` 并使用该字符串**逐字**进行安装——**不要**删除、添加或重新格式化任何字符（包括开头的 `v`）。安装端点通过与注册表的精确字符串匹配来匹配版本，注册表以目录报告的方式存储版本（例如 `"v3.0"`），因此必须将值原样传递。

**您只能安装最新版本。** 安装端点拒绝任何非最新版本（`"Target version <x> is not the latest available version"`）；它不支持安装或回滚到旧版本，因此始终解析 `latestVersion` 并安装确切版本。如果 `installedVersion` 已等于 `latestVersion`，停止——基础组件包已是最新版本。

> **如果 `bundles/details` 返回 `403 FUNCTIONALITY_NOT_ENABLED`** 而在 `bundleListView`（步骤 1）返回 `200`：组织门控良好，但运行用户缺少组件包管理权限。`bundles/details` 需要**类型管理器**角色——读取/所有者/类型读取集不足。将用户路由到 CMDB 访问分配技能以授予类型管理器，然后重试。作为后备方案，`bundleListView` 已返回基础组件包的 `currentInstalledVersion` 和 `latestVersion`，因此您可以从步骤 1 的响应中解析版本（如果无法分配类型管理器）。

### 步骤 3 — 与用户确认（写入之前）

显示基础组件包名称、要安装的版本和目标组织。在写入之前获取明确确认。明确说明此操作将开箱即用的 CMDB 内容安装到组织中。

### 步骤 4 — 安装基础组件包（写入）

调用 `discover(query="cmdb bundle installation")` 然后调用 `describe(id=<bundleInstallation operation id>)` 以确认输入架构，然后安装：

```text
dispatch({ "url": "/services/data/v67.0/connect/cmdb/bundleInstallation", "method": "POST", "body": { "bundleIdentifier": "base", "version": "<latestVersion from Step 2, verbatim>" } })
```

`bundleIdentifier` 和 `version` 都是必需的，并且 `version` 必须是目录的 `latestVersion` 字符串原样传递。`success: true` 响应表示安装已**启动**——它可能异步完成。

### 步骤 5 — 验证（读取——不要单独信任安装响应）

重新读取组件包详细信息并确认基础组件包现在报告已安装的版本：

```text
dispatch_readonly({ "url": "/services/data/v67.0/connect/cmdb/bundles/details", "method": "GET", "queryParams": { "bundleIdentifier": "base" } })
```

`installedVersion` 应等于您安装的版本。如果安装是异步的并且尚未更新，请告知用户正在进行中以及如何重新检查。

---

## 规则 / 约束

| 约束 | 理由 |
|-----------|-----------|
| 首先读取 `bundleListView` 作为启用门控 | 此处的 403 表示 CMDB 未启用或用户缺少 CMDB 访问权限——通过功能状态在采取行动前消除歧义 |
| 从 `bundles/details` 解析版本；永不猜测；逐字传递 `latestVersion` | 安装端点通过与注册表的精确字符串匹配来匹配版本，注册表以目录报告的方式存储版本（例如 `"v3.0"`）——不要删除或重新格式化任何字符 |
| 仅安装最新版本 | 端点拒绝任何非最新版本（`"Target version <x> is not the latest available version"`）；它不能安装或回滚到旧版本 |
| 仅安装 `base` | 此技能仅限于 CMDB 基础基础组件包；可选附加组件超出范围 |
| 确认目标组织和安装 | 安装内容是对实时组织的真实、难以逆转的写入 |
| 如果已安装最新版本则跳过 | 避免重复安装；报告“已是最新版本” |
| 将 `success: true` 视为“启动”；单独验证 | 安装可以是异步的 |
| 永不向用户暴露内部术语 | 保持记录 ID、HTTP 状态代码（403/400/500）、API 错误代码（`FUNCTIONALITY_NOT_ENABLED`，…）、端点名称（`bundleListView`、`bundles/details`、`bundleInstallation`）、开发者名称和工具内部细节（`dispatch`、`headless-360`）出用户界面输出。使用组件包名称和版本以及平实语言 |

---

## 验证清单

- [ ] `bundleListView` 返回 `200`（CMDB 已启用且用户有访问权限）？
- [ ] 从 `bundles/details` 解析 `base` 的 `latestVersion`（未猜测）？
- [ ] 如果已处于最新版本则跳过？
- [ ] 在写入之前确认目标组织 + 安装与用户？
- [ ] `bundleInstallation` 返回 `success: true`？
- [ ] 验证 `installedVersion` 匹配（或报告异步进行中）？

---

## 输出预期

```text
CMDB 组件包部署——完成（通过 service-itsm-agentic-setup-cmdb-bundle-deploy）

目标组织： <组织>

  组件包： CMDB 基础（基础）
  版本： <版本>
  状态： 安装已启动——成功

CMDB 现在已安装其基础内容。结合已启用的功能和分配的用户访问权限，CMDB 已端到端就绪。
```

将内部术语排除在用户界面输出之外（不包含记录 ID、HTTP 状态代码、错误代码或端点名称）。如果任何步骤失败，停止并告知用户——用平实语言——什么未成功及其对他们意味着什么（例如，“此组织的 CMDB 尚未启用，因此无法安装内容”而不是重复 403 代码），然后指向解决方案。

---

## 常见失败（用平实语言说明这些问题）

| 症状 | 可能的原因 | 告诉用户什么 |
|---------|--------------|-----------------------|
| `403` 在目录读取**且**功能未启用 | CMDB 功能未启用 | CMDB 必须先为该组织启用；那是单独的设置步骤——指向功能启用技能 |
| `403` 在目录读取**但**功能已启用 | 功能已启用；运行用户缺少 CMDB 访问权限（此读取也强制执行用户级访问权限） | 首先授予用户 CMDB 访问权限（单独的设置步骤），然后重试——功能本身已启用 |
| `403` 在版本读取**但**目录读取成功 | 用户缺少 CMDB 组件包管理角色（类型管理器） | 首先授予用户 CMDB 类型管理器角色（单独的访问步骤），然后重试；组织本身已正确设置 |
| 安装被拒绝——组件包/版本不存在 | 错误的版本字符串 | 重新读取目录并使用它报告的确切最新版本 |
| 安装报告成功但版本未更改 | 安装在后台运行 | 正在进行中；稍后检查以确认是否完成 |
| 安装时出现下游错误 | 暂时的平台依赖问题 | 重试；如果它持续失败，则需要 Salesforce 支持 |
| 连接/授权错误 | 组织连接未设置或已过期 | 重新验证组织连接并确认它指向预期的组织，然后重试 |

---

## 跨技能集成

| 当... | 技能 |
|------|-------|
| 组织 CMDB 功能尚未启用（组织门控仍关闭） | `service-itsm-agentic-setup-cmdb-configure`（第 0-2 层——首先启用功能，然后返回这里） |
| 运行用户缺少 CMDB 访问权限，或缺少**类型管理器**以进行组件包管理 | `service-itsm-agentic-setup-cmdb-access-assign`（第 3 层——授予用户 CMDB 访问权限，包括类型管理器，然后返回这里） |

---

## 参考文件索引

| 文件 | 何时读取 |
|------|--------------|
| `references/mcp-invocation.md` | 组件包目录 + 安装调用、响应包、安装架构查找和错误表的精确 `mcp__headless-360__*` 调用形状 |
