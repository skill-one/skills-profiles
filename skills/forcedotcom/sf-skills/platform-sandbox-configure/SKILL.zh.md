---
name: platform-sandbox-configure
description: 必须使用此技能处理任何沙盒请求——包括通过名称或ID获取沙盒的详细信息、状态、许可证类型或待激活状态。在以下情况下触发：用户输入“sandbox -help”/“sandbox help”；提及沙盒ID（07E前缀）；要求列出或显示沙盒；通过名称或ID请求沙盒的详细信息、状态、许可证类型或配置；激活或丢弃完成的刷新；删除沙盒；验证激活或删除；创建或刷新沙盒。以下情况不触发：用户希望克隆沙盒。
---

# 沙盒生命周期管理

通过 Connect REST API 管理 Salesforce 沙盒环境——列出资产清单、激活或丢弃完成的刷新、创建和刷新沙盒，以及永久删除沙盒。

## 此技能何时拥有任务

当工作涉及以下内容时，使用 `platform-sandbox-configure`：
- 列出或检索所有沙盒（GET /sandbox/reports）
- 通过名称或 ID（07E 前缀）获取特定沙盒的详细信息或状态
- 刷新完成后激活沙盒（应用刷新）
- 丢弃完成的刷新（保持现有沙盒数据不变）
- 永久删除沙盒以释放许可证
- 验证激活或删除是否完成
- 创建新沙盒（开发者、开发者专业版、部分复制或完整）
- 使用最新生产数据刷新现有沙盒

当用户需要将任务委托给其他地方时：
- 克隆沙盒 → 工具 API (`SandboxInfo` sObject)
- 从标准操作程序（SOP）生成复制后自动化 JSON 配置 → `automation-sandbox-post-copy-config-generate`
- 对沙盒应用/运行复制后自动化 JSON 配置 → `automation-sandbox-post-copy-configure`

---

## 帮助（交互式菜单）

当用户输入 `sandbox -help` 或 `sandbox help` 时，仅回复显示以下编号操作列表的文本消息。**不要调用任何 API 或工具——仅显示此菜单并等待用户回复数字。**

代理必须以以下精确的 Markdown 格式回复（不要用代码块——直接渲染为项目符号列表）：

**沙盒生命周期管理**

**1. 资产清单与详细信息**
- a. 列出所有沙盒 — 名称、类型、状态、ID
- b. 获取详细信息（按名称） — 状态、许可证、配置
- c. 获取详细信息（按 ID） — 直接提供 07E ID

**2. 创建与刷新**
- a. 创建新沙盒 — 开发者、开发者专业版、部分复制、完整
- b. 刷新沙盒 — 最新生产数据

**3. 激活、丢弃与删除**
- a. 激活沙盒 — 应用完成的刷新
- b. 丢弃刷新 — 拒绝，保留现有数据
- c. 删除沙盒 — 永久移除

**4. 验证与监控**
- a. 验证激活状态 — 检查是否激活完成
- b. 验证删除状态 — 检查是否删除完成

**5. 复制后自动化**
- a. 创建复制后自动化 JSON 配置 — 从 SOP 生成配置
- b. 运行复制后自动化 — 将配置 JSON 应用于沙盒

回复代码（例如 "3a"）或描述您需要什么。

**用户回复后，询问所需的输入：**

| 选择 | 随后的问题 |
|---|---|
| 1a | 无需输入 — 立即进行 |
| 1b | "沙盒名称是什么？" |
| 1c | "沙盒 ID 是什么？(以 07E 开头)" |
| 2a | "新沙盒的名称是什么，以及许可证类型是什么？(开发者、开发者专业版、部分复制、完整)" |
| 2b | "您想刷新哪个沙盒？可选地，提供新的名称和/或描述。" |
| 3a | "哪个沙盒？提供名称或 07E ID。" |
| 3b | "哪个沙盒？提供名称或 07E ID。" |
| 3c | "哪个沙盒？提供名称或 07E ID。" |
| 4a | "您激活了哪个沙盒？提供名称或 07E ID。" |
| 4b | "您删除了哪个沙盒？提供名称或 07E ID。" |
| 5a | "委托给复制后配置生成器 — 请分享 SOP（文件、文本或截图）。" |
| 5b | "委托给复制后配置运行器 — 请分享配置 JSON 文件和目标沙盒。" |

执行下方操作部分中的相应操作。**例外：5a 和 5b 委托给其他技能，而不是技能内操作：**
- 5a → 调用 `automation-sandbox-post-copy-config-generate` 技能。
- 5b → 调用 `automation-sandbox-post-copy-configure` 技能。

此技能本身不实现复制后自动化——它仅路由到上述两个技能。不要尝试从此技能直接生成或应用复制后配置。

---

## API 基础

**关键提示：**在此技能中，对于沙盒操作，使用 Connect REST API。存在两个发现路径：
- **按名称：** 调用 `GET /sandbox/reports` 列出所有沙盒并按 `sandboxName` 找到匹配项。
- **按 ID（07E 前缀）：** 直接调用 `GET /sandbox/sandboxes/{sandboxId}` —— 不要调用 `/sandbox/reports`。

这两个路径都返回包含 `sandboxId`（前缀 `07E`）的沙盒记录，这是所有生命周期变异操作所需的。

```bash
# 列出所有沙盒（Connect REST API）
sf api request rest "/services/data/v66.0/sandbox/reports" --method GET

# 响应格式：
# {
#   "count": 3,
#   "sandboxes": [
#     {
#       "sandbox": {
#         "sandboxId": "07E...",        # 所有操作所需
#         "sandboxName": "mybox",       # 顶层字段——用于名称查找
#         "license": "Developer",
#         "isPendingActivation": false,
#         "canActivate": true,
#         "canDelete": true,
#         ...
#       }
#     }
#   ]
# }
```

**重要提示：**不要使用工具 API (`SandboxInfo` 或 `SandboxProcess`) 进行沙盒发现。变异端点（激活/丢弃/删除）需要 Connect REST API 响应中的 `sandboxId`（07E 前缀），而不是 `SandboxInfo.Id`（0GQ 前缀）或 `SandboxProcess.Id`（0GR 前缀）。

**绝对不要使用 SOQL / `run_soql_query` / `sf data query` 进行沙盒生命周期读取——状态、资产清单、详细信息、许可证或待激活状态（例如“获取沙盒 X 的详细信息/状态/许可证/待激活状态”请求）。**这些数据仅存在于 Connect REST API 响应中（按名称查找使用 `GET /sandbox/reports`，按 ID 查找使用 `GET /sandbox/sandboxes/{07E-id}`）；没有正确的 SObject 可以正确返回它。(`sf data query --use-tooling-api` 在 `SandboxInfo` 上仍然有效，用于 7 和 8 操作中的创建和刷新流程，它查找 `SandboxInfo` 记录以变异它——这不是生命周期读取。）如果按名称查找返回空资产清单（`count: 0`），则沙盒不存在——报告诚实的 `not_found`；不要重试 SOQL 查找，也不要编造详细信息。

**精确报告 API 结果——永远不要编造错误或原因。**`count: 0` 响应是 *成功* 结果，意味着沙盒不存在：直接将其记录为 `not_found`，并将端点和空资产清单作为证据。不要将空列表解释为 API 失败。如果 Connect REST API 真正返回错误，请原封不动地捕获错误正文作为结果——但不要猜测 *原因*（例如，“这一定是临时组织”，“沙盒端点在此处不受支持”）。此端点不报告组织的版本或类型，因此任何此类解释都是虚构的，不得出现在输出中。

**发现模式：**

**当用户提供沙盒名称时：**
1. 调用 `GET /sandbox/reports` 获取完整列表
2. 遍历 `sandboxes[]` 数组
3. 检查 `sandbox.sandboxName`（顶层字段）以找到匹配的沙盒
4. 从该记录中提取 `sandbox.sandboxId`
5. 在后续变异操作中使用 `sandboxId`

**当用户提供沙盒 ID（07E 前缀）直接时：**
1. 调用 `GET /sandbox/sandboxes/{sandboxId}` 以验证其是否存在并检查当前状态
2. 直接使用相同的 `sandboxId` 在变异端点中——不要调用 `/sandbox/reports`

所需权限：`ManageSandboxes`

---

## 操作

### 1. 列出沙盒资产清单

**端点：** `GET /services/data/v66.0/sandbox/reports`

返回所有沙盒及其 ID、名称、状态和许可证类型的列表。

```bash
sf api request rest "/services/data/v66.0/sandbox/reports" --method GET
```

**响应格式：**
```json
{
  "count": 3,
  "sandboxes": [
    {
      "sandbox": {
        "sandboxId": "07E...",
        "sandboxName": "DevBox1",
        "license": "Developer",
        "isPendingActivation": false,
        "canActivate": true,
        "canDelete": true,
        "canDiscard": false
      }
    }
  ]
}
```

**使用场景：**用户询问“显示所有沙盒”、“我有多少沙盒”、“我的沙盒状态是什么”

**关键响应字段：**
- `sandbox.sandboxId`（07E 前缀）——所有变异操作所需
- `sandbox.sandboxName`——沙盒名称（顶层字段）
- `sandbox.license`——开发者、开发者专业版、部分复制、完整
- `sandbox.isPendingActivation`——如果刷新待激活则为 true
- `sandbox.canActivate` / `canDelete` / `canDiscard`——权限标志

---

### 2. 获取沙盒详细信息

**端点：** `GET /services/data/v66.0/sandbox/sandboxes/{sandboxId}`

返回特定沙盒的详细信息。

**使用场景：**用户询问特定沙盒的状态、配置或元数据。

**关键响应字段：**
- `status`——激活、待激活、激活中、完成等
- `isPendingActivation`——如果刷新完成并等待用户决策则为 true
- `sandboxType`——开发者、开发者专业版、部分复制、完整
- `sourceId`——源组织的 ID

---

### 3. 激活沙盒（应用刷新）

**端点：** `PATCH /services/data/v66.0/sandbox/activate/{sandboxId}`

**关键领域规则：**此操作仅适用于处于“待激活”状态的已完成刷新的沙盒。它将刷新数据应用于沙盒。它不会“将非激活沙盒上线”或“启动”沙盒。

**前提条件：**
- 沙盒必须处于 `Pending Activation` 状态
- 必须有成功的刷新
- 用户必须具有 `ManageSandboxes` 权限

**调用 PATCH /activate 之前：**
- [ ] 确认沙盒处于 `Pending Activation` 状态（通过 GET `/sandbox/sandboxes/{id}`，`isPendingActivation: true`）
- [ ] 确认刷新已成功完成

**使用场景：**用户说“激活它”、“应用刷新”、“使用最新数据”

**激活后：**沙盒将使用新刷新的生产数据运行。

---

### 4. 验证激活

**端点：** `GET /services/data/v66.0/sandbox/sandboxes/{sandboxId}`

激活后，轮询此端点以确认状态已更改为 `Active`。这是一个验证步骤，不是独立的用户操作。

**使用场景：**代理需要确认激活已完成（激活后自动调用）。

---

### 5. 丢弃沙盒（拒绝刷新）

**端点：** `DELETE /services/data/v66.0/sandbox/discardsandbox/{sandboxId}`

**关键领域规则：**此操作仅适用于处于“待激活”状态的已完成刷新的沙盒。它拒绝刷新——现有沙盒继续运行，其数据保持不变。它不会：
- 释放许可证
- 软删除或隐藏沙盒
- 将沙盒重置为与生产环境匹配

**前提条件：**
- 沙盒必须处于 `Pending Activation` 状态
- 必须有刷新完成

**调用 DELETE /discardsandbox 之前：**
- [ ] 确认沙盒处于 `Pending Activation` 状态（通过 GET `/sandbox/sandboxes/{id}`，`isPendingActivation: true`）
- [ ] 确认这是丢弃（拒绝刷新），而不是删除（永久移除）

**使用场景：**用户说“丢弃刷新”、“保留现有数据”、“不应用刷新”、“拒绝刷新”

**警告：**丢弃不可逆。如果用户以后想要最新生产数据，他们需要触发新的刷新。

---

### 6. 删除沙盒（永久）

**端点：** `DELETE /services/data/v66.0/sandbox/deletesandbox/{sandboxId}`

永久删除沙盒并释放许可证。

**前提条件：**
- 沙盒必须存在
- 用户必须具有 `ManageSandboxes` 权限

**调用 DELETE /deletesandbox 之前：**
- [ ] 向用户展示沙盒详细信息（名称、许可证、状态）并收到明确的删除批准

**使用场景：**用户说“删除这个沙盒”、“永久移除它”、“释放许可证”

**警告：**这是不可逆的。执行前始终与用户确认。作为安全检查，展示沙盒名称、许可证和状态。

---

### 7. 创建新沙盒

从零开始创建新沙盒。支持两种方法——根据用户偏好选择；默认为方法 A，除非用户要求定义文件或可重复的 DX 蓝图。

#### 方法 A — 工具 API 记录（直接）

**API：** 工具 API — `SandboxInfo` sObject

**所需输入：**
- `SandboxName` — 新沙盒的名称（字母数字，最多 10 个字符）
- `LicenseType` — 之一：`Developer`、`Developer_Pro`、`Partial_Copy`、`Full`

**可选输入：**
- `Description` — 沙盒用途的描述
- `Features` — `true` 以将沙盒数据存储升级到 400 MB（警告：一旦启用，不能减少）
- `ApexClassId` — 实现 `SandboxPostCopy` 接口的 Apex 类的 ID（创建完成后运行）
- `ActivationUserGroupId` — 决定哪些用户可以访问沙盒的组的 ID

```bash
# 创建开发者沙盒
sf data create record --sobject SandboxInfo --use-tooling-api --values "SandboxName='mybox' LicenseType='Developer'"
```

#### 方法 B — 沙盒定义文件（Salesforce CLI）

DX 原生路径：编写 JSON 定义文件（可重用的蓝图），然后使用 `sf org create sandbox` 从它创建沙盒。当用户想要检查的、可重复的配置或名称基础的 Apex/组引用（无需 ID 查找）时，优先选择此方法。

```json
// config/dev-sandbox-def.json
{
  "sandboxName": "mybox",
  "licenseType": "Developer"
}
```

```bash
sf org create sandbox --definition-file config/dev-sandbox-def.json --alias mybox --target-org prod
```

**定义文件字段：**

| 字段 | 是否必需 | 备注 |
|-------|----------|-------|
| `sandboxName` | 是 | 字母数字，最多 10 个字符 |
| `licenseType` | 是 | `Developer`、`Developer_Pro`、`Partial`、`Full`——**定义文件中 `Partial`，不是 `Partial_Copy`** |
| `description` | 否 | 沙盒用途（≤1000 个字符） |
| `apexClassName` / `apexClassId` | 否 | 实现 `SandboxPostCopy` 的 Apex 类；定义文件添加 *Name* 变体，无需 ID 查找 |
| `activationUserGroupName` / `activationUserGroupId` | 否 | 控制沙盒访问的公共组；*Name* 变体避免 ID 查找 |
| `features` | 否 | `"['SandboxStorage']"` 以升级数据存储（开发者 → 400 MB，开发者专业版 → 2 GB）；不适用于部分/完整 |
| `templateId` | 部分必需（完整必需），完整可选 | 沙盒模板（以 `1ps` 开头的 15 字符 ID）选择要复制的对象 |
| `historyDays` / `copyChatter` / `copyArchivedActivities` | 否 | 仅限完整沙盒 |

**前提条件：**
- 组织中必须存在请求类型的可用许可证
- 沙盒名称必须唯一且未被使用
- 用户必须具有 `ManageSandboxes` 权限

**创建后：**创建 `SandboxProcess` 记录，状态 = `Processing`。沙盒复制立即开始。

---

### 8. 刷新现有沙盒

使用最新生产数据刷新沙盒。支持两种方法——根据用户偏好选择；默认为方法 A，除非用户要求定义文件。

#### 方法 A — 工具 API 记录（直接）

**API：** 工具 API — `SandboxInfo` sObject (PATCH)

通过更新现有的 `SandboxInfo` 记录进行刷新。

**所需输入：**
- 沙盒名称——用于查找 `SandboxInfo` 记录 ID（0GQ 前缀）

**可选输入：**
- `SandboxName` — 刷新后沙盒的新名称（如果用户想重命名它；字母数字，最多 10 个字符）
- `Description` — 沙盒的新或更新描述
- `AutoActivate` — `true` 以在刷新完成后自动激活（默认：false）
- `Features` — `true` 以将沙盒数据存储升级到 400 MB（警告：一旦启用，不能减少）
- `ApexClassId` — 实现 `SandboxPostCopy` 接口的 Apex 类的 ID（刷新完成后运行）
- `ActivationUserGroupId` — 决定哪些用户可以访问沙盒的组的 ID

**询问用户：**“您想刷新哪个沙盒？如果需要，提供新的名称和/或描述以更改它们。”

**步骤：

```bash
# 1. 通过名称查找 SandboxInfo 记录 Id
sf data query --query "SELECT Id, SandboxName, LicenseType, Description FROM SandboxInfo WHERE SandboxName = '<name>'" --use-tooling-api --json

# 2. 更新记录以触发刷新（PATCH SandboxInfo 记录）
# 仅在用户提供新值时包含 SandboxName 和 Description
sf data update record --sobject SandboxInfo --use-tooling-api --record-id <0GQ-id> --values "AutoActivate=true SandboxName='<newName>' Description='<description>'"
```

**注意：** 仅在用户希望重命名时在 `--values` 中包含 `SandboxName`。仅当用户提供描述时才包含 `Description`。始终包含 `AutoActivate`。

#### 方法 B — Sandbox 定义文件（Salesforce CLI）

使用与创建时相同的 JSON 定义文件蓝图进行刷新（有关完整字段表的说明，请参阅操作 7），使用 `sf org refresh sandbox`。使用现有 Sandbox 的名称；定义文件会提供任何更改的设置（例如，`autoActivate`、`apexClassName`）。

```json
// config/dev-sandbox-def.json
{
  "sandboxName": "mybox",
  "licenseType": "Developer",
  "autoActivate": true
}
```

```bash
sf org refresh sandbox --name mybox --definition-file config/dev-sandbox-def.json --target-org prod
```

**前提条件：**
- Sandbox 必须存在且处于可刷新状态
- 刷新间隔必须已过去（Developer = 1 天，Dev Pro = 1 天，Partial = 5 天，Full = 29 天）
- 用户必须具有 `ManageSandboxes` 权限

**刷新后：** 会创建一个新的 `SandboxProcess` 记录，状态为 `Processing`。如果 `AutoActivate=true`，Sandbox 完成后自动激活。否则进入 `Pending Activation` 状态。

---

## 代理决策指南

### 当用户提供 Sandbox 名称（需要查找）

| 用户说... | 操作 | 关键检查 |
|---|---|---|
| "显示我所有的 Sandbox" | GET /sandbox/reports | — |
| "X 的状态是什么？" | GET /sandbox/reports，按 SandboxName 过滤 | — |
| "激活 Sandbox sbxtest" | 1. GET /sandbox/reports 以按名称查找 sandboxId<br>2. PATCH /sandbox/activate/{sandboxId} | 必须是 isPendingActivation: true |
| "丢弃 sbxtest 的刷新" | 1. GET /sandbox/reports 以按名称查找 sandboxId<br>2. DELETE /sandbox/discardsandbox/{sandboxId} | 必须是 isPendingActivation: true |
| "删除 Sandbox sbxtest" | 1. GET /sandbox/reports 以按名称查找 sandboxId<br>2. DELETE /sandbox/deletesandbox/{sandboxId} | 需要先与用户确认 |

### 当用户直接提供 sandboxId（07E 前缀）

| 用户说... | 操作 | 关键检查 |
|---|---|---|
| "获取 07E... 的详细信息" | GET /sandbox/sandboxes/{sandboxId} | — |
| "激活 Sandbox 07E" | 1. GET /sandbox/sandboxes/{sandboxId} 以验证状态<br>2. PATCH /sandbox/activate/{sandboxId} | 必须是 isPendingActivation: true |
| "丢弃 07E 的刷新" | 1. GET /sandbox/sandboxes/{sandboxId} 以验证状态<br>2. DELETE /sandbox/discardsandbox/{sandboxId} | 必须是 isPendingActivation: true |
| "删除 Sandbox 07E" | 1. GET /sandbox/sandboxes/{sandboxId} 以验证存在性<br>2. DELETE /sandbox/deletesandbox/{sandboxId} | 需要先与用户确认 |

---

## 常见错误避免

| 错误 | 正确理解 |
|---|---|
| 使用激活来 "启动" 任何 Sandbox | 仅适用于已完成的刷新 |
| 使用丢弃来 "隐藏" 或 "软删除" | 仅拒绝待处理的刷新 |
| 在未检查状态之前激活 | 始终验证 isPendingActivation = true |
| 在未用户确认之前激活 | 在应用刷新前始终与用户确认——这将替换现有的 Sandbox 数据 |
| 在未用户确认之前丢弃 | 在丢弃前始终与用户确认——这是不可逆的，刷新数据将丢失 |
| 在未用户确认之前删除 | 始终显示 Sandbox 信息并要求明确确认 |
