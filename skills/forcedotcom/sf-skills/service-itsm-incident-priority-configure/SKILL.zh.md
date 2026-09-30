---
name: service-itsm-incident-priority-configure
description: 通过 sf CLI 配置 Salesforce ITSM 事件优先级矩阵——启用或禁用矩阵、塑造影响 x 紧急性网格（该网格用于在事件记录中派生优先级）、切换手动覆盖偏好，以及读取或设置默认的回退优先级。在写入前会读取每个值，具有幂等性，并在任何变更前需要用户明确确认。当用户需要查看、启用、禁用、设置、初始化、添加、修改或删除事件记录优先级矩阵配置，更改默认事件优先级，或询问事件优先级设置、影响/紧急性映射、覆盖或 ITSM 事件优先级矩阵时使用。**禁止**用于问题或变更请求优先级矩阵、案例优先级字段、ITSM 外的标准优先级选择列表、SLA 或里程碑配置，或启用事件管理本身（应使用 service-itsm-incident-mgmt-configure 技能）。
---

# 配置事件优先级矩阵（sf CLI）

配置 Salesforce ITSM 的 **事件优先级矩阵**——一个根据事件的 **影响** 和 **紧急性** 推导出 **优先级** 的网格。涵盖查看矩阵、启用/禁用、添加/更改/删除/预填充单元格、切换手动覆盖偏好以及读取/设置默认（备用）优先级。

所有读取和写入都通过 **`sf` CLI** 分发，因此此技能适用于任何启用了事件管理许可证的 org。

写入操作是 **幂等的**（当当前状态已匹配目标时会被跳过），技能总是在写入前读取，并且在任何变更前都需要显式的 **确认写入** 检查点。

## 范围

- **在范围内**（仅适用于事件）：查看矩阵；启用/禁用；添加、更改、删除或预填充矩阵单元格；切换手动覆盖；读取/设置默认（备用）优先级。
- **超出范围**：`Problem` 和 `ChangeRequest` 矩阵；非 ITSM 优先级选择器；SLA / 里程碑 / 许可证设置；启用事件管理本身。如果用户询问关于 `Problem` 或 `ChangeRequest` 的问题，请停止并告知。

---

## 前置条件

1. `sf` CLI ≥ 2.60（使用 `sf --version` 验证）。
2. 目标 org 通过 `sf` 进行身份验证——`sf org list` 中应显示为 `Connected`。
3. org 上启用了事件管理——Service Cloud ITSM 事件功能的 master 偏好（Setup Discovery `apiName = service-cloud-itsm-incident`）。在预检时间直接通过 `GET /services/data/v67.0/connect/setup/discovery/features` 读取，并过滤到 `apiName == "service-cloud-itsm-incident"`（master 设置组织的偏好端点在此表面上未公开——`IncidentMgmtEnabled` / `ITSMIncidentMgmtEnabled` 均为 404）。如果 `status != "ENABLED"`，则委托给 `service-itsm-incident-mgmt-configure` 内联以启用它（该技能对其自身路由运行读取前写入 + 确认写入），然后继续阶段 1。
4. 调用用户具有 `CustomizeApplication`（查看设置 + 设置管理员）。

如果任何前置条件未满足，CLI 会直接显示原始错误——**不要编造状态，显示原始错误并停止。**

---

## 一目了然的路线

所有路由都通过 `sf` CLI 调用。完整的 方法 / 路径 / 主体 / 响应细节、选择列表提取配方和注意事项都位于 `references/sf-cli-invocation.md`。

| 关注点 | 传输 | HTTP 状态 |
|---------|-----------|-------------|
| Master 事件管理偏好（读取） | `sf api request rest` GET 在 `/services/data/v67.0/connect/setup/discovery/features`，过滤 `apiName == "service-cloud-itsm-incident"` 以获取 `status` | 200 |
| 矩阵启用标志（读取/写入） | `sf api request rest` 在 `/services/data/v67.0/setup/org/preferences/IncPriorityMatrixEnabled` | 200 |
| 手动覆盖（读取/写入） | `sf api request rest` 在 `/services/data/v67.0/setup/org/preferences/IncPriorityOverrideEnabled` | 200 |
| 矩阵行（读取） | `sf data query --use-tooling-api` 在 `ServiceOpPriorityConfig` | 200 |
| 矩阵行（添加） | `sf api request rest` POST 在 `/services/data/v67.0/tooling/sobjects/ServiceOpPriorityConfig` | 201 |
| 矩阵行（更改） | `sf api request rest` PATCH 在 `/services/data/v67.0/tooling/sobjects/ServiceOpPriorityConfig/<Id>` | 204 |
| 矩阵行（删除） | `sf data delete record --use-tooling-api` 在 `ServiceOpPriorityConfig` | 200 |
| 默认备用优先级（读取） | `sf api request rest` GET 在 `/services/data/v67.0/tooling/query/?q=...StandardValueSet...` | 200 |
| 默认备用优先级（写入） | `sf project retrieve start` + 编辑 + `sf project deploy start` 在 `StandardValueSet:IncidentPriority` | 部署成功 |
| 选择列表值（事件） | `sf api request rest` GET 在 `/services/data/v67.0/sobjects/Incident/describe` | 200 |
| Salesforce Go 步骤 "完成"（写入，在变更后） | `sf api request rest` PUT 在 `/services/data/v67.0/connect/setup/discovery/feature/service-cloud-itsm-incident/configuration/step/definePriorityMatrix/progress` | 200 |

**路径前缀是承载负载的——不要删除它们。** 设置连接 API 路径必须以 `/services/data/v67.0/` 开头。工具 REST 路径必须以 `/services/data/v67.0/tooling/` 开头。

---

## 澄清问题

仅询问您无法推断的内容：

- **哪个 org？** `sf` CLI 别名或用户名 (`--target-org <alias>`）。默认：org 的默认目标。
- **什么操作？** 查看；启用/禁用矩阵；切换手动覆盖；设置默认优先级；添加/更改/删除单元格；预填充完整矩阵。
- **对于添加/更改：** `Impact` + `Urgency` 坐标和 resulting `Priority`（与获取的选择列表值进行验证）。
- **对于设置默认优先级：** 目标优先级值。如果用户未命名一个，则分发 `AskUserQuestion` 并使用 org 的活动 `Incident.Priority` 选择列表值作为选项——永远不要猜测。

---

## 工作流

所有步骤都是按顺序执行的。**总是在写入前读取。** 所有调用都通过 `sf` CLI。

### 阶段 0 — 重用会话中已知的信息

每个下文中的阶段 1 / 阶段 2 读取都带有 **如果已知则跳过** 子句。在调用任何 `sf` 命令之前，检查此会话中的先前回合是否已针对当前 `--target-org` 生成相同的事实 **来自成功的 `sf` 调用**（此技能的先前运行或同一对话中的早期 `sf` 调用）。会话上下文在此处是按 `--target-org <alias>` 分组的，因此不同的别名是不同的会话。**明确的用户声明不是缓存有效的**——选择列表值、偏好布尔值、矩阵行和备用优先级都在客户端验证和重复预防中驱动阶段 4 变更，因此错误的或过时的用户断言可以绕过这些保护措施并创建无效或重复的行。当唯一的来源是用户声明（或您无法识别特定的先前 `sf` 响应）时，重新读取。

- **`sf --version`** — 如果 CLI 版本在此会话中已经报告，则跳过步骤 1。
- **事件 `describe`（活动的 `Impact` / `Urgency` / `Priority` 选择列表）** — 如果当前 `--target-org` 的 Incident describe 已经在此会话中读取并且三个选择列表在上下文中，则跳过步骤 2 并重用它们。
- **`IncPriorityMatrixEnabled` / `IncPriorityOverrideEnabled` 偏好值** — 如果其中任何一个在此会话中已经读取并且自那时以来没有被 PATCH，则跳过其阶段 2 读取。
- **`ServiceOpPriorityConfig` 行** — 如果当前 org 的 Incident 行在此会话中已经读取并且自那时以来没有对 `ServiceOpPriorityConfig` 发送 `POST` / `PATCH` / `delete`，则跳过步骤 5 并重用行列表。
- **`StandardValueSet:IncidentPriority` 默认** — 如果备用优先级在此会话中已经读取并且自那时以来没有运行 `StandardValueSet:IncidentPriority` 部署，则跳过步骤 6。

**如有疑问，请重新检查。** 仅当事实明确处于上下文中、`--target-org` 别名未更改并且自（偏好 PATCH、`ServiceOpPriorityConfig` POST/PATCH/delete 或 `StandardValueSet:IncidentPriority` 部署）以来没有任何阶段 4 写入可以使其失效时才跳过。在活动 org 上错误的跳过比重新读取更糟。

### 阶段 1 — 预检

1. *(如果 `sf --version` 在此会话中已经报告则跳过——见阶段 0。)* `sf --version` 以确认 CLI 可用。
2. **Master 事件管理偏好——直接读取** *(仅当 master 偏好在此会话中针对当前 `--target-org` 已经读取并且值为 `ENABLED` 并且此会话中的任何其他写入都无法翻转它时跳过——见阶段 0。)* `sf api request rest "/services/data/v67.0/connect/setup/discovery/features" --method GET --target-org <alias>`。解析响应并过滤 `features[]` 数组到 `apiName == "service-cloud-itsm-incident"` 的元素；读取其 `status` 字段。如果 `status == "ENABLED"`，则继续步骤 3。**如果 `status != "ENABLED"`，则内联委托给 `service-itsm-incident-mgmt-configure` 以启用 master 偏好**（该技能对其自身路由运行确认写入），然后重新读取此步骤以验证 `status == "ENABLED"` 再继续。如果用户拒绝委托，则停止——优先级矩阵在 master 关闭时无法工作。这是一个 **对 master 偏好的直接读取**，不是代理——接下来的 Incident describe 检查是一个次要的合理性检查，不是 master 状态信号。
3. *(如果当前 `--target-org` 的 Incident describe——包括活动的 `Impact` / `Urgency` / `Priority` 选择列表——在此会话中已经处于上下文中——见阶段 0。)* `sf api request rest "/services/data/v67.0/sobjects/Incident/describe" --method GET --target-org <alias>`。**200** 带有 `Impact` / `Urgency` / `Priority` 选择列表字段是一个次要的合理性检查。提取活动选择列表值以供后续验证。如果 describe 响应很大，则分发一个子代理（haiku 层级）以仅提取三个选择列表。

### 阶段 2 — 显示当前状态（只读）

分发这些读取（所有预期返回 200）：

3. *(如果当前 `--target-org` 的 `IncPriorityMatrixEnabled` 已经在此会话中读取并且自那时以来没有被 PATCH——见阶段 0。)* `sf api request rest "/services/data/v67.0/setup/org/preferences/IncPriorityMatrixEnabled" --method GET --target-org <alias>` — 矩阵启用标志。主体：`{"isPreferenceEnabled": <bool>}`。
4. *(如果当前 `--target-org` 的 `IncPriorityOverrideEnabled` 已经在此会话中读取并且自那时以来没有被 PATCH——见阶段 0。)* `sf api request rest "/services/data/v67.0/setup/org/preferences/IncPriorityOverrideEnabled" --method GET --target-org <alias>` — 手动覆盖标志。相同的主体形状。
5. *(如果当前 `--target-org` 的 Incident `ServiceOpPriorityConfig` 行已经在此会话中读取并且自那时以来没有对此 SObject 发送 POST / PATCH / delete——见阶段 0。)* 矩阵行——`sf data query --use-tooling-api --target-org <alias> --query "SELECT Id, DeveloperName, ReferenceObject, Urgency, Impact, Priority FROM ServiceOpPriorityConfig WHERE ReferenceObject = 'Incident'"`。返回零个或多个行。`DeveloperName` 是必需的，以便添加步骤可以派生一个新鲜的唯一后缀。
6. *(如果 `StandardValueSet:IncidentPriority` 默认在此会话中已经读取并且自那时以来没有运行 `StandardValueSet:IncidentPriority` 部署——见阶段 0。)* 默认备用优先级——`sf api request rest "/services/data/v67.0/tooling/query/?q=SELECT+Id,MasterLabel,Metadata+FROM+StandardValueSet+WHERE+MasterLabel='IncidentPriority'" --method GET --target-org <alias>`。读取 `records[0].Metadata.standardValue`，找到具有 `default: true` 的条目，取其 `valueName`——那就是备用优先级。

将行格式化为影响 × 紧急性网格（见 `examples/render-matrix.md`）。步骤 3–6 一起是“查看”操作和快照前。

**重复坐标检测（承载负载用于更改 / 删除）：** 将阶段 2 行按 `(ReferenceObject, Urgency, Impact)` 分组。如果任何组中有多个行，矩阵中已经存在重复（服务器不强制执行唯一性）。对于每个目标坐标重复的操作，停止阶段 3——不要在用户确认更改或删除之前询问他们明确的 `Id` 或批准合并计划（见 `阶段 4 → 更改单元格` 和 `阶段 4 → 删除单元格`）。添加不受影响——阶段 4 的添加路径已经拒绝任何已存在于快照中的坐标。

### 阶段 3 — 确认目标（`AskUserQuestion`，在任何写入前必需）

将预期变更表示为 `(Concern: <之前> → <之后>)` 并要求通过 `AskUserQuestion` 进行明确的“是”。仅在明确的“是”上继续到阶段 4。在“否”上，停止并报告当前状态而不写入。

### 阶段 4 — 应用变更（仅查看时不跳过）

首先读取相同关注的当前值（阶段 2 涵盖此内容），通过用户确认目标（阶段 3），然后分发。每个操作的完整 CLI 调用和有效负载形状都位于 `examples/matrix-operations.md`。

- **启用/禁用矩阵** — `sf api request rest` PATCH 在 `IncPriorityMatrixEnabled`，主体为 `{"desiredState": <bool>}`。PATCH 响应回显 `{"isPreferenceEnabled": <bool>}`；不需要单独重读。
- **切换手动覆盖** — `sf api request rest` PATCH 在 `IncPriorityOverrideEnabled`，主体为 `{"desiredState": <bool>}`。不触及矩阵行或默认优先级。
- **添加单元格** — `sf api request rest` POST 在 `/services/data/v67.0/tooling/sobjects/ServiceOpPriorityConfig`，主体为 `{"ReferenceObject": "Incident", "Urgency": "<val>", "Impact": "<val>", "Priority": "<val>", "DeveloperName": "<unique>", "MasterLabel": "<same>"}`。有效负载必须具有 `ReferenceObject == "Incident"`——SObject 与 Problem / ChangeRequest 共享，服务器接受任何字符串。首先验证每个 `Urgency` / `Impact` / `Priority` 对获取的选择列表——工具端点不执行选择列表验证。与阶段 2 快照去重：服务器不拒绝 `(ReferenceObject, Urgency, Impact)` 上的重复，因此对同一坐标的第二个 POST 静默持久化为第二行，运行时在它们之间非确定性选择。
- **更改单元格** — 读取阶段 2 行，找到匹配 `(ReferenceObject=Incident, Urgency, Impact)` 的行。如果 **正好一行匹配**，`sf api request rest` PATCH 在 `/services/data/v67.0/tooling/sobjects/ServiceOpPriorityConfig/<Id>`，主体为 `{"Priority": "<新值>"}`。如果 **零行匹配**，这是添加——不是更改；显示并询问。如果 **多行匹配**（阶段 2 中检测到重复），则不要分发——报告具有 `Id` / `DeveloperName` / 当前 `Priority` 的重复行，并要求用户要么命名确切的 `Id` 以更改，要么批准合并计划（删除多余的，然后更改幸存者）。
- **删除单元格** — 读取阶段 2 行，找到匹配 `(ReferenceObject=Incident, Urgency, Impact)` 的行。如果 **正好一行匹配**，`sf data delete record --sobject ServiceOpPriorityConfig --record-id <Id> --use-tooling-api --target-org <alias>`。如果 **零行匹配**，则短路“无内容可删除”。如果 **多行匹配**，则不要分发——报告重复项并要求用户要么命名确切的 `Id`(s) 以删除，要么明确确认“删除此坐标的所有行”。
- **预填充完整矩阵** — 见 `examples/seed-full-matrix.md`。首先验证值，然后 POST 每行。
- **设置默认备用优先级** — `sf project retrieve start --metadata "StandardValueSet:IncidentPriority" --target-org <alias>`，编辑文件以在目标值上设置 `<default>true</default>` 并在所有其他值上设置 `<default>false</default>`，然后 `sf project deploy start --metadata "StandardValueSet:IncidentPriority" --target-org <alias> --wait 10`。在部署结果中验证 `Succeeded`。

### 阶段 5 — 验证并呈现

7. 重新阅读被修改的担忧（通过工具 SOQL 获取矩阵行；通过 `StandardValueSet` 查询获取默认优先级；偏好设置在 PATCH 响应中回显）。如果观察到的状态与请求的状态不匹配，将其视为写入失败，并逐字报告原始服务器响应。
8. **仅当第 4 阶段功能写入实际落地时，标记 Salesforce Go 步骤为已完成**。“定义优先级矩阵”步骤允许用户覆盖：其复选标记**不**源自组织状态，因此仅配置矩阵不会切换它——必须写入完成。在步骤 7 验证写入后，通过 PUT 提交一次完成（`references/sf-cli-invocation.md` 路由 10；正文 `{"isComplete": true}`，标志必需）。它依赖于第 3 阶段的确认——没有单独的 `AskUserQuestion`。**在仅查看读取和幂等的无操作中完全跳过。**
9. 提供“之前/之后”（通过 `examples/render-matrix.md` 获取影响 × 紧急性网格）以及一行摘要（例如 `事件矩阵：高/高 → 添加关键`）。矩阵更改仅影响写入**之后**创建的事件；禁用矩阵不会清除存储的行或默认优先级。

---

## 规则 / 约束

| 约束 | 理由 |
|------|------|
| 所有操作通过 `sf` CLI 运行 | 适用于任何启用了事件管理的组织；无需额外设置 |
| 始终使用 API v67.0 及更高版本 | 设置连接 API 偏好路由需要 v67+ |
| 写入前读取实时状态 | 第 2 阶段快照是确认提示、幂等性检查和第 5 阶段验证的来源 |
| **写入前必须确认**任何修改 | 切换偏好设置或更改矩阵行会修改组织状态；用户必须批准确切计划 |
| 幂等性——当当前状态已与请求状态匹配时跳过写入 | 避免无操作写入；参见 `references/sf-cli-invocation.md` 获取每个担忧的确切匹配规则 |
| 在分派前验证每个 `Impact`、`Urgency`、`Priority` 是否符合组织的实时选项列表 | 工具 REST 端点**不**执行选项列表验证；运行时矩阵评估器执行。跳过此验证会让垃圾行进入矩阵 |
| 在添加前客户端端去重第 2 阶段快照 | 服务器**不**强制执行 `(ReferenceObject, Urgency, Impact)` 唯一性——在相同坐标上的第二个 POST 持久化为单独的行。客户端端去重是防止重复单元格的唯一保护措施。 |
| 拒绝任何非 `Incident` 的 `ReferenceObject`（`Problem`、`ChangeRequest`、任何其他） | `ServiceOpPriorityConfig` 在线级别与 `Problem` / `ChangeRequest` 矩阵共享——服务器接受任何 `ReferenceObject` 字符串。仅 `Incident` 的范围是技能强制的。 |
| 在更改/删除时，如果目标坐标解析为多个行，则**不**分派——需要显式的 `Id` 或确认的合并计划 | 服务器允许重复的 `(ReferenceObject, Urgency, Impact)` 行。任意选择“行 Id”会修改一个重复项而将另一个保留，使矩阵非确定性。 |
| 报告 CLI 响应中的确切错误文本 | CLI 逐字显示底层错误消息 |
| 在功能写入后，通过 PUT Salesforce Go 步骤进度完成（路由 10）；在查看/无操作时跳过 | “定义优先级矩阵”步骤允许用户覆盖——其复选标记**不**源自组织状态，因此配置写入仅将 Go 清单卡滞 |

---

## 验证清单

在报告任何修改完成之前，请确认以下各项。如果任何项目未勾选，则不要报告成功——显示缺失内容。

- [ ] 第 1 阶段预检（在事件描述上使用 `sf api request rest`）返回 200 并包含活动的 `Impact` / `Urgency` / `Priority` 选项列表；如果 404，则显示原始错误并中止运行。
- [ ] 对每个计划修改的担忧执行第 2 阶段读取返回 200（或显示原始错误）并将每个观察值记录为“之前”状态。对于更改/删除，第 2 阶段行按 `(ReferenceObject, Urgency, Impact)` 分组，并在修改目标上显示任何重复坐标——直到显式 `Id` 或确认的合并计划解决重复问题，才不会分派更改/删除。
- [ ] 第 3 阶段确认写入通过 `AskUserQuestion` 提供 `(<concern>: <当前> → <请求>)` 并用户回复了明确的“是”——任何其他响应（沉默、“可能”、“看起来不错”、隐式批准）都不会分派写入。
- [ ] 幂等性：如果当前状态已与请求状态匹配，则第 4 阶段为该担忧跳过并报告为幂等的无操作——不会分派写入。
- [ ] 任何添加/更改负载中的每个 `Impact`、`Urgency`、`Priority` 都在分派前与第 1 阶段选项列表值进行验证。客户端端检测到 `(ReferenceObject, Urgency, Impact)` 上的重复——服务器**不**拒绝重复。每个添加负载都有 `ReferenceObject == "Incident"`。
- [ ] 第 4 阶段写入使用了 `references/sf-cli-invocation.md` 中的确切 CLI 调用；在任何 `4xx` / `5xx`（或非 `Succeeded` 部署）情况下，显示原始响应并中止运行。
- [ ] 第 5 阶段验证重新读取受影响的担忧；任何差异都报告为 `write FAILED — 服务器状态与请求不同` 并附带原始响应。
- [ ] 如果第 4 阶段功能写入落地，则在验证后发送 Go 步骤进度完成 PUT（路由 10）。在仅查看读取和幂等的无操作中，不会分派完成 PUT。
- [ ] 最终报告提供了影响 × 紧急性网格的“之前/之后”和一行摘要。

---

## 参考文件索引

| 文件 | 何时读取 |
|------|--------|
| `references/sf-cli-invocation.md` | 确切的 `sf` CLI 调用、响应信封、选项列表提取、幂等性规则和注意事项 |
| `examples/render-matrix.md` | 影响 × 紧急性网格布局 |
| `examples/matrix-operations.md` | 启用、覆盖、默认、添加/更改/删除的完整 CLI 调用模板 |
| `examples/seed-full-matrix.md` | 种子完整矩阵（首先验证选项列表值） |
