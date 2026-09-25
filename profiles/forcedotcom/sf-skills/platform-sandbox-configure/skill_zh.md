# 沙盒生命周期管理

通过 Connect REST API 管理Salesforce沙盒环境——列出库存、激活或丢弃完成的刷新、创建和刷新沙盒，以及永久删除沙盒。

## 此技能何时拥有任务

当工作涉及以下内容时，使用 `platform-sandbox-configure`：

- 列出或检索所有沙盒（GET /sandbox/reports）
- 通过名称或ID（07E前缀）获取特定沙盒的详细信息或状态
- 检查按许可证类型检查许可证使用情况和剩余容量（GET /sandbox/licenses）
- 刷新完成后激活沙盒（应用刷新）
- 丢弃完成的刷新（保持现有沙盒数据不变）
- 永久删除沙盒以释放许可证
- 验证激活或删除是否完成
- 创建新沙盒（开发者、开发者专业版、部分复制或完整）
- 使用最新生产数据刷新现有沙盒

当用户是以下情况时，将任务委托给其他地方：

- 克隆沙盒 → 工具API（`SandboxInfo` sObject）
- 从SOP生成复制后自动化JSON配置 → `automation-sandbox-post-copy-config-generate`
- 对沙盒应用/运行复制后自动化JSON配置 → `automation-sandbox-post-copy-configure`

---

## 帮助（交互式菜单）

当用户输入 `sandbox -help` 或 `sandbox help` 时，仅回复显示以下编号操作列表的文本消息。**不要调用任何API或工具——只需显示此菜单并等待用户回复数字。**

代理必须回复此确切的Markdown（不要用代码块——直接渲染为项目符号列表）：

**沙盒生命周期管理**

**1. 库存与详情**
- a. 列出所有沙盒——名称、类型、状态、ID
- b. 获取详情（按名称）——状态、许可证、配置
- c. 获取详情（按ID）——直接提供07E ID
- d. 检查许可证使用情况——按许可证类型显示可用与已用计数

**2. 创建与刷新**
- a. 创建新沙盒——开发者、开发者专业版、部分复制、完整
- b. 刷新沙盒——最新生产数据

**3. 激活、丢弃与删除**
- a. 激活沙盒——应用完成的刷新
- b. 丢弃刷新——拒绝，保留现有数据
- c. 删除沙盒——永久移除

**4. 验证与监控**
- a. 验证激活状态——检查是否激活完成
- b. 验证删除状态——检查是否删除完成

**5. 复制后自动化**
- a. 创建复制后自动化JSON配置——从SOP生成配置
- b. 运行复制后自动化——将配置JSON应用于沙盒

回复代码（例如 "3a"）或描述您需要什么。

**用户回复后，询问所需的输入：**

| 选择 | 随后的问题 |
|---|---|
| 1a | 无需输入——立即进行 |
| 1b | "沙盒名称是什么？" |
| 1c | "沙盒ID是什么？(以07E开头)" |
| 1d | 无需输入——立即进行 |
| 2a | 首先调用 `GET /sandbox/licenses`（第9节）并显示可用/已用计数；然后询问名称 + 许可证类型（开发者、开发者专业版、部分复制、完整） |
| 2b | 首先调用 `GET /sandbox/reports`（第1节）并列出可刷新的沙盒（`isPendingActivation: false`）；然后询问要刷新哪个 |
| 3a | "哪个沙盒？提供名称或07E ID。" |
| 3b | "哪个沙盒？提供名称或07E ID。" |
| 3c | "哪个沙盒？提供名称或07E ID。" |
| 4a | "您激活了哪个沙盒？提供名称或07E ID。" |
| 4b | "您删除了哪个沙盒？提供名称或07E ID。" |
| 5a | "委托给复制后配置生成器——请分享SOP（文件、文本或截图)." |
| 5b | "委托给复制后配置运行器——请分享配置JSON文件和目标沙盒。" |

执行相应的操作。**例外：** 5a/5b 委托——5a → `automation-sandbox-post-copy-config-generate`；5b → `automation-sandbox-post-copy-configure`。此技能不实现复制后自动化；不要直接生成或应用配置。

---

## API基础

**关键：** 对于此技能中的沙盒操作，使用Connect REST API。存在两个发现路径：

- **按名称：** 调用 `GET /sandbox/reports` 列出所有沙盒并通过 `sandboxName` 找到匹配项。
- **按ID（07E前缀）：** 直接调用 `GET /sandbox/sandboxes/{sandboxId}` —— 不要调用 `/sandbox/reports`。

两者都返回沙盒记录，其中包含 `sandboxId`（前缀 `07E`），这是所有生命周期变异操作所需的。

```bash
sf api request rest "/services/data/v66.0/sandbox/reports" --method GET
```

参见 `references/api-response-shapes.md` 获取完整响应形状。

**重要：** 不要使用工具API（`SandboxInfo`/`SandboxProcess`）进行发现——变异端点需要Connect REST API的 `sandboxId`（07E），而不是 `SandboxInfo.Id`（0GQ）或 `SandboxProcess.Id`（0GR）。

**绝对不要使用SOQL / `run_soql_query` / `sf data query` 进行生命周期读取（状态、库存、详情、许可证、pending-activation）。** 此数据仅存在于Connect REST API中——没有SObject会返回它。(`sf data query --use-tooling-api` 在 `SandboxInfo` 上仍然有效，用于创建/刷新变异，而不是生命周期读取。)

**准确报告API结果——永远不要编造错误或原因。** `count: 0` 是一个 *成功* 结果（沙盒不存在）——记录 `not_found`，不要重新解释为失败或通过SOQL重试。如果API出错，原封不动地捕获错误正文——不要猜测原因（例如 "必须是沙盒组织"；此端点不报告组织版本/类型，因此任何此类猜测都是虚构的）。

必需权限：`ManageSandboxes`

## 不可逆操作——始终先确认

| 操作 | 为什么不可逆 |
|---|---|
| 创建 | 消耗所选类型的许可证 |
| 激活 | 用刷新数据覆盖沙盒 |
| 丢弃 | 刷新数据丢失 |
| 删除 | 沙盒永久移除 |
| 带有 `AutoActivate=true` 的刷新 | 完成时自动应用——与激活效果相同 |

---

## 操作

### 1. 列出沙盒库存

**端点：** `GET /services/data/v66.0/sandbox/reports`

返回所有沙盒及其ID、名称、状态和许可证类型。

```bash
sf api request rest "/services/data/v66.0/sandbox/reports" --method GET
```

参见 `references/api-response-shapes.md` 获取完整响应形状。

**使用场景：** 用户询问 "显示所有沙盒"、"我有多少沙盒"、"我的沙盒状态是什么"

**关键响应字段：**
- `sandbox.sandboxId`（07E前缀）—— 所有变异操作所需
- `sandbox.sandboxName`—— 沙盒名称（顶级字段）
- `sandbox.license`—— 开发者、开发者专业版、部分复制、完整
- `sandbox.isPendingActivation`—— 如果刷新正在等待激活则为true
- `sandbox.canActivate` / `canDelete` / `canDiscard`—— 权限标志

---

### 2. 获取沙盒详情

**端点：** `GET /services/data/v66.0/sandbox/sandboxes/{sandboxId}`

返回特定沙盒的详细信息。

**使用场景：** 用户询问特定沙盒的状态、配置或元数据。

**关键响应字段：**
- `status`—— 活跃、待激活、激活中、完成等
- `isPendingActivation`—— 如果刷新完成并等待用户决策则为true
- `sandboxType`—— 开发者、开发者专业版、部分复制、完整
- `sourceId`—— 源组织的ID

---

### 3. 激活沙盒（应用刷新）

**端点：** `PATCH /services/data/v66.0/sandbox/activate/{sandboxId}`

**关键领域规则：** 此操作仅适用于处于 "待激活" 状态的已完成刷新的沙盒。它将刷新数据应用于沙盒。它不会 "启动非活跃沙盒" 或 "启动" 沙盒。

**前提条件：**
- 沙盒必须处于 `Pending Activation` 状态
- 必须有一个刷新已成功完成
- 用户必须具有 `ManageSandboxes` 权限

**调用PATCH /activate之前：**
- [ ] 确认沙盒处于 `Pending Activation` 状态（通过GET `/sandbox/sandboxes/{id}` (`isPendingActivation: true`))
- [ ] 确认刷新已成功完成
- [ ] 收到明确用户确认——这将用刷新数据覆盖沙盒，且不可撤销

**使用场景：** 用户说 "激活它"、"应用刷新"、"使用最新数据"

**激活后：** 沙盒将使用新的刷新生产数据运行。

---

### 4. 验证激活

**端点：** `GET /services/data/v66.0/sandbox/sandboxes/{sandboxId}`

激活后，轮询此端点以确认状态已更改为 `Active`。这是一个验证步骤，不是独立的用户操作。

**使用场景：** 代理需要确认激活已完成（激活后自动调用）。

---

### 5. 丢弃沙盒（拒绝刷新）

**端点：** `DELETE /services/data/v66.0/sandbox/discardsandbox/{sandboxId}`

**关键领域规则：** 此操作仅适用于处于 "待激活" 状态的已完成刷新的沙盒。它拒绝刷新——现有沙盒将继续运行，其数据保持不变。它不会：
- 释放许可证
- 软删除或隐藏沙盒
- 将沙盒重置为与生产环境匹配

**前提条件：**
- 沙盒必须处于 `Pending Activation` 状态
- 必须有一个刷新已完成

**调用DELETE /discardsandbox之前：**
- [ ] 确认沙盒处于 `Pending Activation` 状态（通过GET `/sandbox/sandboxes/{id}` (`isPendingActivation: true`))
- [ ] 确认这是丢弃（拒绝刷新），而不是删除（永久移除）
- [ ] 收到明确用户确认——刷新数据将被永久丢失且不可撤销

**使用场景：** 用户说 "丢弃刷新"、"保留现有数据"、"不应用刷新"、"拒绝刷新"

**警告：** 丢弃不可逆。如果用户以后想要最新的生产数据，他们需要触发新的刷新。

---

### 6. 删除沙盒（永久）

**端点：** `DELETE /services/data/v66.0/sandbox/deletesandbox/{sandboxId}`

永久删除沙盒并释放许可证。

**前提条件：**
- 沙盒必须存在
- 用户必须具有 `ManageSandboxes` 权限

**调用DELETE /deletesandbox之前：**
- [ ] 向用户展示沙盒详情（名称、许可证、状态）并收到明确的删除批准

**使用场景：** 用户说 "删除这个沙盒"、"永久移除它"、"释放许可证"

**警告：** 这不可逆。在执行前始终与用户确认。作为安全检查，展示沙盒名称、许可证和状态。

**如果要求恢复已删除的沙盒：** 目前没有记录的恢复路径——请联系支持，而不是猜测一个。

---

### 7. 创建新沙盒

从零开始创建新沙盒。支持两种方法——根据用户的偏好选择；默认为方法A，除非用户要求定义文件或可重复的DX蓝图。

**前提条件：**
- 组织中必须存在所选类型的可用许可证
- 沙盒名称必须唯一且未被使用
- 用户必须具有 `ManageSandboxes` 权限

**创建前——始终先确认：**
- [ ] 收集名称/许可证；询问该许可证的可选输入（`references/definition-file-approach.md`）
- [ ] 展示此确认摘要——常见字段加上许可证自己的字段：

  > **创建新沙盒——请确认：**
  > - **名称：** `<SandboxName>`
  > - **描述：** `<Description or "(none)">`
  > - **创建自：** 生产
  > - **许可证：** `<Developer | Developer Pro | Partial Copy | Full>`
  > - *(加上此许可证的字段——参见 `references/definition-file-approach.md`)*
  >
  > 在我继续之前，您可以随时更改这些中的任何一项。

- [ ] 收到明确确认——这将消耗所选类型的许可证

#### 方法A——工具API记录（直接）

**API：** 工具API——`SandboxInfo` sObject

**必需输入：**
- `SandboxName`—— 新沙盒的名称（字母数字，最多10个字符）
- `LicenseType`—— 之一：`Developer`、`Developer_Pro`、`Partial_Copy`、`Full`

**可选输入：**
- `Description`—— 沙盒用途
- `Features`—— 存储升级：`Developer`→400 MB、`Developer_Pro`→2 GB（不可逆）；不适用于 `Partial_Copy`/`Full`
- `ApexClassId`—— 实现 `SandboxPostCopy` 的Apex类（创建后运行）
- `ActivationUserGroupId`—— 访问组（默认：所有活跃用户）
- `TemplateId` / `HistoryDays` / `CopyChatter` / `CopyArchivedActivities`—— `Partial_Copy`/`Full` 仅限；许可证表在 `references/definition-file-approach.md` 中

```bash
# 创建一个Developer沙盒
sf data create record --sobject SandboxInfo --use-tooling-api --values "SandboxName='mybox' LicenseType='Developer'"
```

#### 方法B——沙盒定义文件（Salesforce CLI）

DX原生路径：编写JSON定义文件，然后 `sf org create sandbox --definition-file <file> --alias <name> --target-org <org>`。适用于检查入的、可重复的配置或基于名称的Apex/组引用。参见 `references/definition-file-approach.md` 获取JSON示例、命令和字段表。

**创建后：** 创建一个状态为 `Processing` 的 `SandboxProcess` 记录。沙盒复制立即开始。

**创建错误类型：** 删除并重新创建正确的类型。

**重命名：** 不是独立操作——仅通过刷新的 `SandboxName` 输入生效。

---

### 8. 刷新现有沙盒

用最新生产数据刷新沙盒。支持两种方法——根据用户的偏好选择；默认为方法A，除非用户要求定义文件。

#### 方法A——工具API记录（直接）

**API：** 工具API——`SandboxInfo` sObject（PATCH）

通过更新现有的 `SandboxInfo` 记录来刷新。

**必需输入：**
- 沙盒名称——用于查找 `SandboxInfo` 记录ID（0GQ前缀）

**可选输入：**
- `SandboxName`—— 刷新后沙盒的新名称（如果用户想重命名它；字母数字，最多10个字符）
- `Description`—— 沙盒的新或更新描述
- `AutoActivate`—— `true` 以在刷新完成后自动激活（默认：false）
- `Features`—— 存储升级：`Developer`→400 MB、`Developer_Pro`→2 GB（不可逆）；不适用于 `Partial_Copy`/`Full`
- `ActivationUserGroupId`—— 访问组（默认：所有活跃用户）
- `TemplateId` / `HistoryDays` / `CopyChatter`—— `Partial_Copy`/`Full` 仅限；许可证表在 `references/definition-file-approach.md` 中

**触发刷新前——始终先确认：**
- [ ] 收集沙盒名称；询问其许可证的可选输入（`references/definition-file-approach.md`）
- [ ] 展示此确认摘要：

  > **刷新沙盒 `<name>`——请确认：**
  > - **重命名为：** `<SandboxName or "(no change)">`
  > - **描述：** `<Description or "(no change)">`
  > - **自动激活：** `<Yes | No (default)>`
  > - **沙盒访问：** `<ActivationUserGroupId or "All Active Users">`
  > - *(加上此许可证的字段——参见 `references/definition-file-approach.md`)*
  >
  > 在我继续之前，您可以随时更改这些中的任何一项。

- [ ] 收到明确确认——刷新将用生产数据覆盖沙盒；Auto-Activate=Yes 会自动应用（相当于激活）

**步骤：**

```bash
# 1. 通过名称查找 SandboxInfo 记录 Id
sf data query --query "SELECT Id, SandboxName, LicenseType, Description FROM SandboxInfo WHERE SandboxName = '<name>'" --use-tooling-api --json

# 2. PATCH 以触发刷新；仅如果用户更改了它们，才包括 SandboxName/Description
# Description 是自由文本——在插入前转义任何嵌入的单引号（' -> \'）
sf data update record --sobject SandboxInfo --use-tooling-api --record-id <0GQ-id> --values "AutoActivate=true SandboxName='<newName>' Description='<description>'"
```

#### 方法B——沙盒定义文件（Salesforce CLI）

使用与创建相同的JSON定义文件蓝图，使用 `sf org refresh sandbox --name <name> --definition-file <file> --target-org <org>`。参见 `references/definition-file-approach.md` 获取JSON示例、命令和字段表。

**前提条件：**
- 沙盒必须存在并处于可刷新状态
- 刷新间隔必须已过去（Developer = 1天、Dev Pro = 1天、Partial = 5天、Full = 29天）
- 用户必须具有 `ManageSandboxes` 权限

**刷新后：** 创建一个新的 `SandboxProcess` 记录，状态为 `Processing`。如果 `AutoActivate=true`，沙盒在完成后自动激活。否则它进入 `Pending Activation` 状态。

**未达到刷新间隔：** 说明上次刷新日期和符合条件的日期。如果需要更快的副本，如果存在备用许可证，克隆（委托）可以工作。

---

### 9. 检查许可证使用情况

**端点：** `GET /services/data/v66.0/sandbox/licenses`

返回每个许可证类型的容量、使用情况和剩余计数——无需沙盒名称或ID。

```bash
sf api request rest "/services/data/v66.0/sandbox/licenses" --method GET
```

参见 `references/api-response-shapes.md` 获取完整响应形状。

**使用场景：** 用户询问 "我还有多少沙盒许可证"、"我的许可证使用情况如何"、"我可以创建另一个Full沙盒吗"，或在创建/刷新沙盒前确认该 `licenseType` 存在容量。

**创建/刷新因许可证限制受阻：** 提供选择可用类型的选项、通过删除陈旧沙盒释放许可证、询问管理员增加许可证，或者——如果它是过期的Courtesy Full Copy——购买/转换它。

---

## 代理决策指南

首先解决 `sandboxId`：通过名称，调用 `GET /sandbox/reports` 并匹配 `sandboxName`；通过ID（07E前缀），直接调用 `GET /sandbox/sandboxes/{sandboxId}` —— 不要调用 `/sandbox/reports`。

| 用户说... | 操作 | 关键检查 |
|---|---|---|
| "显示所有我的沙盒" | GET /sandbox/reports | — |
| "X的状态是什么？" | GET /sandbox/reports (按名称) 或 GET /sandbox/sandboxes/{id} (按ID) | — |
| "激活沙盒X" | 1. 解决 `sandboxId`<br>2. PATCH /sandbox/activate/{sandboxId} | 必须是 isPendingActivation: true；先与用户确认 |
| "丢弃X的刷新" | 1. 解决 `sandboxId`<br>2. DELETE /sandbox/discardsandbox/{sandboxId} | 必须是 isPendingActivation: true；先与用户确认 |
| "删除沙盒X" | 1. 解决 `sandboxId`<br>2. DELETE /sandbox/deletesandbox/{sandboxId} | 先与用户确认 |
