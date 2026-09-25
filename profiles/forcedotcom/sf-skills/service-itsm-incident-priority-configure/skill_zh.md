# 配置事件优先级矩阵（sf CLI）

配置 Salesforce ITSM 的 **事件优先级矩阵**——一个根据事件的 **影响** 和 **紧急程度** 推导 **优先级** 的网格。涵盖查看矩阵、启用/禁用、添加/更改/删除/播种单元格、切换手动覆盖偏好以及读取/设置默认（备用）优先级。

所有读取和写入都通过 **`sf` CLI** 分发，因此此技能适用于任何启用了事件管理许可证的组织。

写入操作是 **幂等的**（当当前状态已与目标匹配时会被跳过），该技能总是 **先读取后写入**，并且在任何变更操作之前都需要一个明确的 **确认写入** 检查点。

## 范围

- **在范围内**（仅适用于事件）：查看矩阵；启用/禁用；添加、更改、删除或播种矩阵单元格；切换手动覆盖；读取/设置默认（备用）优先级。
- **超出范围**：`Problem` 和 `ChangeRequest` 矩阵；非 ITSM 优先级选择器；SLA / 里程碑 / 许可设置；启用事件管理本身。如果用户询问关于 `Problem` 或 `ChangeRequest` 的问题，请停止并告知。

---

## 前置条件

1. `sf` CLI ≥ 2.60（使用 `sf --version` 验证）。
2. 目标组织已通过 `sf` 进行身份验证——`sf org list` 中应显示为 `Connected`。
3. 组织已启用事件管理——Service Cloud ITSM 事件功能的父级偏好设置（Setup Discovery `apiName = service-cloud-itsm-incident`）。在预检查时间直接通过 `GET /services/data/v67.0/connect/setup/discovery/features` 读取，并过滤到 `apiName == "service-cloud-itsm-incident"`（父级设置的端点在此表面上未公开——`IncidentMgmtEnabled` / `ITSMIncidentMgmtEnabled` 均为 404）。如果 `status != "ENABLED"`，则委托到 `service-itsm-incident-mgmt-configure` 内联以启用它（该技能对其自身路由运行先读取后写入 + 确认写入），然后继续第一阶段。
4. 调用用户具有 `CustomizeApplication`（查看设置 + 设置管理员）权限。

如果任何前置条件未满足，CLI 将直接显示原始错误——**不要编造状态，显示原始错误并停止。**

---

## 概览中的路由

所有路由都通过 `sf` CLI 调用。完整的 方法 / 路径 / 正文 / 响应详细信息、选择列表提取配方以及注意事项都位于 `references/sf-cli-invocation.md`。

| 关注点 | 传输 | HTTP 状态 |
|---------|-----------|-------------|
| 主事件管理偏好（读取） | `sf api request rest` GET 在 `/services/data/v67.0/connect/setup/discovery/features`，过滤 `apiName == "service-cloud-itsm-incident"` 以获取 `status` | 200 |
| 矩阵启用标志（读取/写入） | `sf api request rest` 在 `/services/data/v67.0/setup/org/preferences/IncPriorityMatrixEnabled` | 200 |
| 手动覆盖（读取/写入） | `sf api request rest` 在 `/services/data/v67.0/setup/org/preferences/IncPriorityOverrideEnabled` | 200 |
| 矩阵列（读取） | `sf data query --use-tooling-api` 在 `ServiceOpPriorityConfig` | 200 |
| 矩阵列（添加） | `sf api request rest` POST 在 `/services/data/v67.0/tooling/sobjects/ServiceOpPriorityConfig` | 201 |
| 矩阵列（更改） | `sf api request rest` PATCH 在 `/services/data/v67.0/tooling/sobjects/ServiceOpPriorityConfig/<Id>` | 204 |
| 矩阵列（删除） | `sf data delete record --use-tooling-api` 在 `ServiceOpPriorityConfig` | 200 |
| 默认备用优先级（读取） | `sf api request rest` GET 在 `/services/data/v67.0/tooling/query/?q=...StandardValueSet...` | 200 |
| 默认备用优先级（写入） | `sf project retrieve start` + 编辑 + `sf project deploy start` 在 `StandardValueSet:IncidentPriority` | 部署成功 |
| 选择列表值（事件） | `sf api request rest` GET 在 `/services/data/v67.0/sobjects/Incident/describe` | 200 |
| Salesforce Go 步骤 "完成"（写入，变更后） | `sf api request rest` PUT 在 `/services/data/v67.0/connect/setup/discovery/feature/service-cloud-itsm-incident/configuration/step/definePriorityMatrix/progress` | 200 |

**路径前缀是承载重量的——**绝对不要删除它们。设置连接 API 路径必须以 `/services/data/v67.0/` 开头。工具 REST 路径必须以 `/services/data/v67.0/tooling/` 开头。

---

## 澄清问题

仅询问您无法推断的内容：

- **哪个组织？** `sf` CLI 别名或用户名 (`--target-org <alias>`）。默认：组织的默认目标。
- **什么操作？** 查看；启用/禁用矩阵；切换手动覆盖；设置默认优先级；添加/更改/删除单元格；播种完整矩阵。
- **对于添加/更改：** `影响` + `紧急程度` 坐标和结果 `优先级`（与获取的选择列表值进行验证）。
- **对于设置默认优先级：** 目标优先级值。如果用户未命名一个值，则分发 `AskUserQuestion` 并将组织的活动 `Incident.Priority` 选择列表值作为选项——永远不要猜测。

---

## 工作流

所有步骤都是按顺序执行的。**始终在写入之前读取。** 所有调用都通过 `sf` CLI。

### 第一阶段——预检查

1. *(如果本会话中已报告 `sf --version`，则跳过——见第一阶段。)* `sf --version` 以确认 CLI 可用。
2. **主事件管理偏好——直接读取** *(仅当本会话中已针对当前 `--target-org` 读取主偏好且值为 `ENABLED` 且本会话中没有任何写入可能翻转它时跳过——见第一阶段。)* `sf api request rest "/services/data/v67.0/connect/setup/discovery/features" --method GET --target-org <alias>`。解析响应并过滤 `features[]` 数组到 `apiName == "service-cloud-itsm-incident"` 的元素；读取其 `status` 字段。如果 `status == "ENABLED"`，则继续步骤 3。**如果 `status != "ENABLED"`，则内联委托到 `service-itsm-incident-mgmt-configure` 以启用主偏好**（该技能对其自身路由运行先读取后写入 + 确认写入），然后重新读取此步骤以验证 `status == "ENABLED"` 再继续。如果用户拒绝委托，则停止——优先级矩阵在主功能关闭时无法工作。这是一个 **直接读取主偏好**，不是代理——后续的事件描述检查是一个次要的合理性检查，不是主状态信号。
3. *(如果当前 `--target-org` 的事件描述——包括活动的 `影响` / `紧急程度` / `优先级` 选择列表——在本会话中已读取且三个选择列表在上下文中，则跳过——见第一阶段。)* `sf api request rest "/services/data/v67.0/sobjects/Incident/describe" --method GET --target-org <alias>`。**200** 并带有 `影响` / `紧急程度` / `优先级` 选择列表字段是一个次要的合理性检查。提取活动选择列表值以供后续验证。如果描述响应很大，则分发一个子代理（haiku 层级）以仅提取三个选择列表。

### 第二阶段——显示当前状态（只读）

分发这些读取（所有预期返回 200）：

3. *(如果当前 `--target-org` 的 `IncPriorityMatrixEnabled` 已在本会话中读取且自那时未进行 PATCH，则跳过——见第一阶段。)* `sf api request rest "/services/data/v67.0/setup/org/preferences/IncPriorityMatrixEnabled" --method GET --target-org <alias>` — 矩阵启用标志。正文：`{"isPreferenceEnabled": <bool>}`。
4. *(如果当前 `--target-org` 的 `IncPriorityOverrideEnabled` 已在本会话中读取且自那时未进行 PATCH，则跳过——见第一阶段。)* `sf api request rest "/services/data/v67.0/setup/org/preferences/IncPriorityOverrideEnabled" --method GET --target-org <alias>` — 手动覆盖标志。相同的正文形状。
5. *(如果当前 `--target-org` 的事件 `ServiceOpPriorityConfig` 行已在本会话中读取且自那时未对此 SObject 进行 POST / PATCH / 删除，则跳过——见第一阶段。)* 矩阵列——`sf data query --use-tooling-api --target-org <alias> --query "SELECT Id, DeveloperName, ReferenceObject, Urgency, Impact, Priority FROM ServiceOpPriorityConfig WHERE ReferenceObject = 'Incident'"`。返回零行或多行。`DeveloperName` 是必需的，以便添加步骤可以派生一个唯一的后缀。
6. *(如果 `StandardValueSet:IncidentPriority` 默认值已在本会话中读取且自那时未运行 `StandardValueSet:IncidentPriority` 部署，则跳过——见第一阶段。)* 默认备用优先级——`sf api request rest "/services/data/v67.0/tooling/query/?q=SELECT+Id,MasterLabel,Metadata+FROM+StandardValueSet+WHERE+MasterLabel='IncidentPriority'" --method GET --target-org <alias>`。读取 `records[0].Metadata.standardValue`，找到带有 `default: true` 的条目，取其 `valueName`——那就是备用优先级。

将行格式化为影响 × 紧急程度网格（见 `examples/render-matrix.md`）。步骤 3–6 一起是“查看”操作和快照。

**重复坐标检测（承载重量用于更改 / 删除）：** 将第二阶段的行按 `(ReferenceObject, Urgency, Impact)` 分组。如果任何组中有超过一行，则矩阵已包含重复项（服务器不强制执行唯一性）。对于每个目标坐标重复的操作，停止阶段 3——不要询问用户确认更改或删除，直到他们命名一个明确的 `Id` 或批准合并计划（见 `阶段 4 → 更改一个单元格` 和 `阶段 4 → 删除一个单元格`）。添加不受影响——阶段 4 的添加路径已经拒绝任何已存在于快照中的坐标。

### 第三阶段——确认目标（`AskUserQuestion`，任何写入前必须）

将预期变更表示为 `(Concern: <当前> → <目标>)` 并要求通过 `AskUserQuestion` 提供明确的“是”。仅在明确“是”后继续阶段 4。在“否”的情况下，停止并报告当前状态而不写入。

### 第四阶段——应用变更（仅查看时不跳过）

首先读取相同关注点的当前值（阶段 2 涵盖此内容），然后向用户确认目标（阶段 3），然后分发。每个操作的精确正文形状和完整的 CLI 调用位于 `examples/matrix-operations.md`。

- **启用/禁用矩阵** — `sf api request rest` PATCH 在 `IncPriorityMatrixEnabled`，正文 `{"desiredState": <bool>}`。PATCH 响应回显 `{"isPreferenceEnabled": <bool>}`；不需要单独重读。
- **切换手动覆盖** — `sf api request rest` PATCH 在 `IncPriorityOverrideEnabled`，正文 `{"desiredState": <bool>}`。不触及矩阵行或默认优先级。
- **添加一个单元格** — `sf api request rest` POST 在 `/services/data/v67.0/tooling/sobjects/ServiceOpPriorityConfig`，正文 `{"ReferenceObject": "Incident", "Urgency": "<val>", "Impact": "<val>", "Priority": "<val>", "DeveloperName": "<唯一>", "MasterLabel": "<相同>"}`。正文必须具有 `ReferenceObject == "Incident"`——该 SObject 与 `Problem` / `ChangeRequest` 共享，服务器接受任何字符串。首先验证每个 `Urgency` / `Impact` / `Priority` 对应获取的选择列表值——工具端点不执行选择列表验证。与第二阶段快照去重：服务器不拒绝 `(ReferenceObject, Urgency, Impact)` 上的重复项，因此对同一坐标的第二个 POST 将静默持久化为第二行，运行时在它们之间非确定性选择。
- **更改一个单元格** — 读取第二阶段行，找到匹配 `(ReferenceObject=Incident, Urgency, Impact)` 的行。如果 **正好一行匹配**，`sf api request rest` PATCH 在 `/services/data/v67.0/tooling/sobjects/ServiceOpPriorityConfig/<Id>`，正文 `{"Priority": "<新值>"}`。如果 **零行匹配**，这是一个添加，不是更改；显示并询问。如果 **多行匹配**（在第二阶段检测到重复项），则不要分发——报告重复行的 `Id` / `DeveloperName` / 当前 `Priority`，并要求用户命名确切的 `Id` 进行更改或批准合并计划（删除多余的，然后更改幸存者）。
- **删除一个单元格** — 读取第二阶段行，找到匹配 `(ReferenceObject=Incident, Urgency, Impact)` 的行。如果 **正好一行匹配**，`sf data delete record --sobject ServiceOpPriorityConfig --record-id <Id> --use-tooling-api --target-org <alias>`。如果 **零行匹配**，则短路为“无内容可删除”。如果 **多行匹配**，则不要分发——报告重复项，并要求用户命名确切的 `Id`(s) 进行删除或明确确认“删除此坐标的所有行”。
- **播种完整矩阵** — 见 `examples/seed-full-matrix.md`。首先验证值，然后 POST 每行。
- **设置默认备用优先级** — `sf project retrieve start --metadata "StandardValueSet:IncidentPriority" --target-org <alias>`，编辑文件以在目标值上设置 `<default>true</default>` 并在所有其他值上设置 `<default>false</default>`，然后 `sf project deploy start --metadata "StandardValueSet:IncidentPriority" --target-org <alias> --wait 10`。使用部署结果中的 `Succeeded` 进行验证。

### 第五阶段——验证和呈现

7. 重新读取受影响的关注点（通过工具 SOQL 读取矩阵行；通过 `StandardValueSet` 查询读取默认优先级；偏好是在 PATCH 响应中回显的）。如果观察到的状态与请求的状态不匹配，将其视为写入失败并原封不动地报告原始服务器响应。
8. **标记 Salesforce Go 步骤完成——仅当实际执行的第四阶段功能写入已落地时。** “定义优先级矩阵”步骤是用户覆盖的：其复选标记**不是**来自组织状态，因此仅配置矩阵不会改变它——必须写入完成。在步骤 7 验证写入后，一次 PUT 完成状态（路由 10；正文 `{"isComplete": true}`，标志必需）。它依赖于阶段 3 的确认——没有单独的 `AskUserQuestion`。**在仅查看/无操作时完全跳过。**
9. 呈现前后（通过 `examples/render-matrix.md` 的影响 × 紧急程度网格）加上一行摘要（例如 `事件矩阵：高/高 → 添加了关键`）。矩阵更改仅影响创建于 **写入之后** 的事件；禁用矩阵不会清除存储的行或默认优先级。

---

## 规则 / 约束

| 约束 | 理由 |
|-----------|-----------|
| 所有操作通过 `sf` CLI 运行 | 适用于任何启用了事件管理的组织；无需额外设置 |
| 始终使用 API v67.0 最小版本 | 设置连接 API 偏好路由需要 v67+ |
| 写入前读取实时状态 | 第二阶段快照是确认提示、幂等性检查和第五阶段验证的来源 |
| **在任何变更前必须的确认写入检查点** | 切换偏好或更改矩阵行会变更组织状态；用户必须批准确切计划 |
| 幂等性——当当前状态已与请求状态匹配时跳过写入 | 避免无操作写入；见 `references/sf-cli-invocation.md` 每个关注点的确切匹配规则 |
| 在分发前，验证任何添加/更改中的 `影响`、`紧急程度`、`优先级` 对应组织的实时选择列表 | 工具 REST 端点不执行选择列表验证；运行时矩阵评估器执行。跳过此验证会让无效行进入矩阵 |
| 在添加前，客户端端对第二阶段快照进行去重 | 服务器不强制执行 `(ReferenceObject, Urgency, Impact)` 唯一性——对同一坐标的第二个 POST 将持久化为单独的行。客户端端去重是防止重复单元格的唯一保护 |
| 拒绝任何 `ReferenceObject` 不同于 `Incident` (`Problem`、`ChangeRequest`、任何其他) | `ServiceOpPriorityConfig` 在线级别与 `Problem` / `ChangeRequest` 矩阵共享——服务器接受任何 `ReferenceObject` 字符串。仅限于 `Incident` 的范围是技能强制执行的 |
| 在更改/删除中，如果目标坐标解析为多行，则不要分发——要求明确的 `Id` 或确认的合并计划 | 服务器允许重复的 `(ReferenceObject, Urgency, Impact)` 行。任意选择“行 Id”会更改一个重复项而留下另一个，使矩阵非确定性 |
| 报告 CLI 响应的精确错误文本 | CLI 原封不动地显示底层错误消息 |
| 在功能写入后，PUT Salesforce Go 步骤进度完成（路由 10）；查看/无操作时跳过 | “定义优先级矩阵”步骤是用户覆盖的——其复选标记不是来自组织状态，因此配置写入单独不会使 Go 清单卡停滞 |

---

## 验证检查清单

在报告任何变更完成之前，请确认以下各项。如果任何项目未勾选，则不要报告成功——显示缺失的内容。

- [ ] 第一阶段预检查 (`sf api request rest` 在事件描述) 返回 200 并带有活动的 `影响` / `紧急程度` / `优先级` 选择列表；如果 404，则显示原始错误并停止运行。
- [ ] 对写入计划触发的每个关注点进行的第二阶段读取返回 200（或显示原始错误）并且每个观察值都被记录为“当前”状态。对于更改/删除，第二阶段行按 `(ReferenceObject, Urgency, Impact)` 分组，并且任何在变更目标上的重复坐标都显示给用户——没有更改/删除被分发，直到明确的 `Id` 或确认的合并计划解决了重复项。
- [ ] 第三阶段确认写入通过 `AskUserQuestion` 提供了 `(<关注点>: <当前> → <目标>)` 并用户回复了明确的“是”——没有在任何其他响应（沉默、“可能”、“看起来不错”、隐式批准）上分发写入。
- [ ] 幂等性：如果当前状态已与请求状态匹配，则针对该关注点的第四阶段被跳过并报告为幂等性无操作——没有分发写入。
- [ ] 任何添加/更改有效负载中的每个 `影响`、`紧急程度`、`优先级` 都在分发前与第一阶段获取的选择列表值进行验证。`(ReferenceObject, Urgency, Impact)` 上的重复项在客户端端与第二阶段快照捕获——服务器不拒绝重复。每个添加有效负载都有 `ReferenceObject == "Incident"`。
- [ ] 第四阶段写入使用了 `references/sf-cli-invocation.md` 中的精确 CLI 调用；在任何 `4xx` / `5xx`（或非 `Succeeded` 部署），显示原始响应并停止运行。
- [ ] 第五阶段验证重新读取受影响的关注点；任何差异都报告为 `write FAILED — 服务器状态与请求不同` 并显示原始响应。
- [ ] 如果第四阶段功能写入落地，则发送 Salesforce Go 步骤进度完成 PUT（路由 10）。在仅查看/无操作时，不发送完成 PUT。
- [ ] 最终报告提供了影响 × 紧急程度网格的快照和一行摘要。

---

## 参考文件索引

| 文件 | 何时读取 |
|------|----------|
| `references/sf-cli-invocation.md` | 精确的 `sf` CLI 调用、响应封装、选择列表提取、幂等性规则和注意事项 |
| `examples/render-matrix.md` | 影响 × 紧急程度网格布局 |
| `examples/matrix-operations.md` | 启用、覆盖、默认、添加 / 更改 / 删除的完整 CLI 调用模板 |
| `examples/seed-full-matrix.md` | 播种完整矩阵（首先验证选择列表值） |
