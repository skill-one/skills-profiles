# 分享规则生成器

获取、创建、编辑和删除 Salesforce 分享规则元数据，以控制超出组织范围的默认设置之外的记录级访问权限。支持基于条件的规则、基于角色/组的所有者规则以及体验站点的访客用户规则。

## 范围

- **在范围内**：创建、编辑、删除和检索（获取）`sharingCriteriaRules`、`sharingOwnerRules` 和 `sharingGuestRules` 元数据；使用 Metadata API Retrieve 模式从组织中检索现有分享规则；将新规则附加到现有文件；修改规则条件或访问级别；从元数据文件中删除规则；为访客和门户配置文件配置规则。
- **超出范围**：更改组织范围的默认设置（OWD/共享模型）、创建体验站点、配置权限集或配置文件（使用 `platform-permission-set-generate`）、基于地域的共享规则。

---

## 澄清问题

在进行下一步之前，如果尚未明确，请与用户确认：

### 对于获取操作：
- 应该检索哪个对象的分享规则？（标准或自定义对象的 API 名称，或所有对象）
- 应该从哪个目标组织检索规则？（组织别名或默认）

### 对于创建操作：
- 分享规则应用于哪个对象？（标准或自定义对象的 API 名称）
- 规则类型是什么？（基于条件的规则、基于角色/组的所有者规则或访客用户规则）
- 记录应该与谁共享？（角色名称、组、门户角色或访客用户昵称）
- 访问级别是什么？（读取或读取/写入）
- 对于基于条件的规则：应匹配哪些字段条件？

### 对于编辑操作：
- 应该修改哪个现有规则？（规则的 fullName 或标签）
- 应该改变什么？（访问级别、条件、标签——注意：`sharedTo` 和 `sharedFrom` 不能就地编辑）

### 对于删除操作：
- 应该删除哪些规则？（规则的 fullName 或标签）
- 确认规则所属的对象

---

## 必需输入

在进行下一步之前收集或推断：

- **对象 API 名称**：规则目标的对象（例如，`Account`、`Property__c`）
- **规则类型**：`sharingCriteriaRules`、`sharingOwnerRules` 或 `sharingGuestRules` 之一
- **共享目标**：角色、组、门户角色或访客用户社区昵称
- **访问级别**：`Read` 或 `Edit`（映射到只读或读取/写入）
- **条件**（对于条件/访客规则）：每个过滤器项的字段名称、操作和值

默认值（除非指定）：
- 访问级别：`Read`
- `includeRecordsOwnedByAll`：对于条件规则为 `true`
- `includeHVUOwnedRecords`：对于访客规则为 `false`
- 账户共享规则包含 `accountSettings`，所有子访问级别设置为 `None`

---

## 工作流

每个阶段内的步骤是按顺序执行的。阶段 3 根据操作类型分支——仅执行匹配的分支。阶段 4 仅适用于创建、编辑和删除（获取操作在阶段 3 结束）。

### 阶段 1 — 发现

1. **解析 SFDX 项目路径**——找到项目的 `sfdx-project.json` 并识别 `sharingRules/` 的包目录。

2. **始终使用 Metadata API Retrieve 模式从组织中检索最新的分享规则**：
   ```bash
   sf project retrieve start --metadata "SharingRules:<ObjectName>" --target-org <org>
   ```
   这确保本地文件反映当前组织的状态。永远不要信任可能过时的本地文件——针对过时文件进行编辑或删除可能会重新创建组织已删除的规则或覆盖其他用户所做的更改。

3. **读取检索到的文件**——解析 `<packageDir>/sharingRules/<ObjectName>.sharingRules-meta.xml` 以了解现有规则并避免重复。

### 阶段 2 — 确定操作和规则类型

4. **识别操作**——确定用户是否要获取、创建、编辑或删除分享规则。

5. **根据用户意图选择规则类型**。阅读 `references/rule-types.md` 以获取每种类型完整的架构及其必需元素。

6. **对于账户共享规则**：需要 `accountSettings` 元素。除非用户指定否则默认子访问级别为 `None`。

7. **对于访客规则**：`sharedTo` 必须使用 `<guestUser>` 与站点访客用户的社区昵称。永远不要使用 `<role>` 或 `<group>` 进行访客规则。

### 阶段 3 — 执行操作

#### 对于获取：

8a. **使用阶段 1 中检索的文件**——步骤 2 中的检索已经从组织中拉取了最新的 `<ObjectName>.sharingRules-meta.xml`。不需要额外的检索。

8b. **读取并显示检索到的规则**——解析 `.sharingRules-meta.xml` 文件，并以可读格式向用户显示规则，显示：
    - 规则名称（`fullName`）和标签
    - 规则类型（基于条件、基于所有者或访客）
    - 访问级别
    - 共享目标
    - 条件（如适用）

    对于获取操作，跳过阶段 4（不需要写入）。检索本身会将元数据文件写入本地项目。

#### 对于创建：

8a. **构建 XML** 遵循 `references/rule-types.md` 中的架构。关键结构：
    - 每个对象一个 `.sharingRules-meta.xml` 文件
    - 同一对象的规则都在同一个文件中
    - 如果附加到现有文件，将新规则元素添加到现有的 `<SharingRules>` 根目录内

8b. **命名规则**——从意图派生 `<fullName>`（帕斯卡大小写，无空格，描述性）。生成匹配的 `<label>`（标题大小写，有空格）。

#### 对于编辑：

8a. **定位目标规则**——在现有的 `.sharingRules-meta.xml` 文件中通过 `<fullName>` 或 `<label>` 找到规则。

8b. **限制不受支持的编辑**——平台不支持就地修改 `<sharedTo>` 或 `<sharedFrom>` 元素。如果用户请求更改共享目标或来源，拒绝编辑并指示他们删除现有规则并创建一个具有所需目标的新规则。这是用于规则类型更改的相同模式（见 TC-16）。

8c. **根据规则类型确定修改**：
    - **基于所有者的规则（`sharingOwnerRules`）**：只能编辑 `<accessLevel>`。平台不支持修改所有者规则上的任何其他元素（`sharedTo`、`sharedFrom`、`label`）。如果用户请求超出访问级别的更改，拒绝并指示他们删除 + 创建。
    - **基于条件的规则（`sharingCriteriaRules`）**：支持的编辑元素是 `<accessLevel>`、`<criteriaItems>`、`<label>` 和 `<booleanFilter>`。
    - **访客规则（`sharingGuestRules`）**：支持的编辑元素是 `<accessLevel>`、`<criteriaItems>`、`<label>` 和 `<includeHVUOwnedRecords>`。

#### 对于删除：

8a. **定位目标规则**——在现有的 `.sharingRules-meta.xml` 文件中通过 `<fullName>` 或 `<label>` 找到规则。

8b. **计算剩余规则**——运行 `scripts/count-remaining-rules.sh <file>` 获取总规则数。如果计数为 1（仅删除的规则），则必须在阶段 4 中完全删除文件。

8c. **将破坏性部署委托给 `platform-destructive-deploy`**——正常的 `sf project deploy start` 是加性的，不会从组织中删除规则。委托给 `platform-destructive-deploy` 技能，并提供以下上下文：
    - 元数据类型：`SharingCriteriaRule`、`SharingOwnerRule` 或 `SharingGuestRule`（根据规则类型）
    - 成员：`<ObjectName>.<RuleFullName>`
    - 目标组织：用户指定的组织

### 阶段 4 — 写入和验证

9. **应用更改**：
    - **创建**：将文件写入 `<packageDir>/sharingRules/<ObjectName>.sharingRules-meta.xml`。
    - **编辑**：仅更新步骤 8b 中标识的元素；保留所有其他元素完全不变。
    - **删除（规则保留）**：写入更新后的文件，删除目标规则。
    - **删除（最后一个规则）**：完全删除 `<packageDir>/sharingRules/<ObjectName>.sharingRules-meta.xml` 文件。

10. **运行以下验证清单** 并在呈现输出之前参考示例文件（`examples/create-cases.md`、`examples/edit-cases.md`、`examples/delete-cases.md`）以获取特定场景的预期行为。

---

## 验证清单

### 通用检查
- [ ] 文件是否具有 XML 声明和 `<SharingRules xmlns="http://soap.sforce.com/2006/04/metadata">` 根？
- [ ] 是否每个对象只有一个文件，所有规则都在其中？
- [ ] `<fullName>` 是否使用帕斯卡大小写且无空格？
- [ ] `<label>` 是否存在且可读？
- [ ] `<accessLevel>` 是否为 `Read` 或 `Edit`？

### 基于条件的规则检查
- [ ] 是否存在 `<includeRecordsOwnedByAll>`（必需的布尔值）？
- [ ] 每个 `<criteriaItems>` 是否具有 `<field>`、`<operation>` 和 `<value>`？
- [ ] 挑单值是否为目标组织的有效值？

### 访客规则检查   关键
- [ ] `<sharedTo>` 是否使用 `<guestUser>`（不是 `<role>` 或 `<group>`）？
- [ ] 是否存在 `<includeHVUOwnedRecords>`（必需的布尔值）？
- [ ] 是否 `<includeRecordsOwnedByAll>` 缺失（仅适用于条件规则，不适用于访客规则）？

### 所有者规则检查
- [ ] 规则是否同时具有 `<sharedFrom>` 和 `<sharedTo>` 元素？
- [ ] 两者是否使用有效的 `<role>`、`<roleAndSubordinates>` 或 `<group>` 目标？

### 编辑操作检查
- [ ] 是否针对最新检索的文件进行编辑（不是过时的本地副本）？
- [ ] 是否仅限于规则类型支持的字段进行编辑？
  - 所有者规则：仅 `accessLevel`
  - 基于条件的规则：`accessLevel`、`criteriaItems`、`label`、`booleanFilter`
  - 访客规则：`accessLevel`、`criteriaItems`、`label`、`includeHVUOwnedRecords`
- [ ] 是否保留了 `sharedTo`/`sharedFrom` 未修改？（如果用户请求更改，拒绝并建议删除 + 创建）
- [ ] 是否仅修改了预期元素？
- [ ] 编辑后是否所有必需元素仍然存在？
- [ ] 修改后的规则是否仍然通过上述通用检查？

### 删除操作检查
- [ ] 是否删除了正确的规则（通过 `<fullName>` 匹配）？
- [ ] 剩余的 XML 是否格式良好，具有正确的 `<SharingRules>` 根？
- [ ] 如果没有规则剩余，是否完全删除了文件？
- [ ] 是否将 `platform-destructive-deploy` 委托给正确的元数据类型（`SharingCriteriaRule`、`SharingOwnerRule` 或 `SharingGuestRule`）？

### 账户特定检查   关键
- [ ] 如果对象是账户，是否存在 `<accountSettings>` 并具有所有三个子元素？
- [ ] `<caseAccessLevel>`、`<contactAccessLevel>`、`<opportunityAccessLevel>` 是否全部设置？

---

## 规则 / 限制

| 限制 | 理由 |
|-----------|-----------|
| 每个对象一个 `.sharingRules-meta.xml` 文件 | 平台要求——多个文件会导致部署错误 |
| 访客规则必须在 `sharedTo` 中使用 `<guestUser>` | 使用 `<role>` 或 `<group>` 会导致："指定访客用户的昵称用于 guestUser 字段" |
| 账户规则需要 `<accountSettings>` | 没有它："账户共享规则需要 AccountSettings" |
| `includeRecordsOwnedByAll` 在条件规则中是必需的 | 缺少它会导致："缺少必需的字段：sharingCriteriaRules" |
| `includeHVUOwnedRecords` 在访客规则中是必需的 | 缺少它会导致部署失败 |
| 条件字段的值必须是目标组织中的挑单值 | 无效值会导致："挑单值不存在" |
| 永远不要硬编码文件路径——从 `sfdx-project.json` 解析 | 客户项目使用自定义包目录 |
| 对于受管理的包自定义对象，使用包括命名空间前缀的完整 API 名称（例如，`ns__Object__c`） | 命名空间前缀对象在命名空间前缀下存储共享规则 |
| `sharedTo` 和 `sharedFrom` 不能就地编辑 | 平台不支持修改共享目标——部署将失败。删除规则并创建新规则 |
| 基于所有者的规则仅支持编辑 `accessLevel` | 所有者规则上不能修改其他字段（`label`、`sharedTo`、`sharedFrom`）——删除并重新创建 |
| 始终在编辑或删除之前从组织中检索 | 本地文件可能过时；编辑过时的文件可能会重新创建已删除的规则或覆盖并发更改 |
| 删除规则需要破坏性部署 | 正常部署是加性的——它不会从组织中删除规则。委托给 `platform-destructive-deploy` |
| 编辑必须保留未修改的元素 | 仅修改 `accessLevel` 必须不改变 `criteriaItems` 或其他字段 |
| 删除必须删除整个规则块 | 部分删除会留下无效的 XML 并导致部署失败 |
| 删除最后一个规则会删除文件 | 空的 `<SharingRules>` 根且没有子元素是无效的元数据 |

---

## 注意事项

| 问题 | 解决方案 |
|-------|------------|
| 访客规则使用 `<role>` 而不是 `<guestUser>` | 替换为 `<guestUser>CommunityNickname</guestUser>` |
| 账户规则缺少 `accountSettings` | 添加 `<accountSettings>` 并将所有三个访问级别子元素设置为 `None` |
| 条件规则缺少 `includeRecordsOwnedByAll` | 添加 `<includeRecordsOwnedByAll>true</includeRecordsOwnedByAll>` |
| 挑单值不匹配 | 在生成条件之前查询组织以获取有效值 |
| 附加重复的现有规则名称 | 在写入之前检查现有的 `<fullName>` 值 |
| 访客用户昵称未找到 | 查询：`SELECT CommunityNickname FROM User WHERE UserType='Guest' AND IsActive=true` |
| 用户请求编辑 `sharedTo` 或 `sharedFrom` | 不支持——拒绝编辑并指示用户删除 + 创建新规则 |
| 用户请求编辑所有者规则超出 `accessLevel` | 不支持——所有者规则仅允许 `accessLevel` 编辑。拒绝并指示用户删除 + 创建 |
| 编辑更改了规则类型（例如，条件 → 所有者） | 不支持——删除旧规则并创建新规则 |
| 本地文件过时（组织中的规则已删除/更改） | 在编辑或删除之前始终从组织中检索最新文件，以避免重新创建已删除的规则 |
| 使用正常部署（无破坏性清单）删除部署 | 规则仍然存在于组织中——委托给 `platform-destructive-deploy` 以正确删除 |
| 删除了其他自动化引用的规则 | 警告用户关于潜在的下游影响 |
| 删除后留下格式不良的 XML | 确保删除后正确的 XML 结构；验证文件是否格式良好 |

---

## 输出预期

交付物：
- **对于获取操作**：`<packageDir>/sharingRules/<ObjectName>.sharingRules-meta.xml` — 从组织中检索到的分享规则文件，以及找到的所有规则的格式化摘要
- **对于创建/编辑/删除操作**：`<packageDir>/sharingRules/<ObjectName>.sharingRules-meta.xml` — 目标对象的完整分享规则文件

---

## 跨技能集成

| 需要 | 委托给 |
|------|-------------|
| 权限集配置 | `platform-permission-set-generate` 技能 |
| 自定义对象创建（如果目标对象不存在） | `platform-custom-object-generate` 技能 |
| 破坏性部署（从组织中删除规则） | `platform-destructive-deploy` 技能 |

---

## 参考文件索引

| 文件 | 何时阅读 |
|------|-------------|
| `references/rule-types.md` | 阶段 2 — 在生成任何规则之前，以获取每种规则类型的完整 XML 架构 |
| `scripts/count-remaining-rules.sh` | 阶段 3，步骤 8b（删除）——计算分享规则元素以确定是否应删除文件 |
| `examples/create-cases.md` | 阶段 4，步骤 10 — 创建和附加场景的预期行为 |
| `examples/edit-cases.md` | 阶段 4，步骤 10 — 编辑场景的预期行为 |
| `examples/delete-cases.md` | 阶段 4，步骤 10 — 删除场景的预期行为 |
