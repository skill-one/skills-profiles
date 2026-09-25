# 管理全局默认设置

检索和更新 Salesforce 组织中标准对象和自定义对象的 Organization-Wide Default (OWD) 共享设置。OWD 定义用户对不属于其拥有的记录的访问权限的基本级别。

## 范围

- **在范围内**：检索当前 OWD 设置，更新标准对象和自定义对象的内/外部访问级别
- **超出范围**：共享规则、角色层次结构配置、手动共享、权限集、基于条件的共享 — 委托给相应技能

---

## 澄清问题

在进行之前，如果尚未明确，请与用户确认：

- 您想要获取或更新哪些对象的 OWD 设置？
- 您想要设置什么访问级别？（私有、仅限公共读取、公共读写、由父项控制）
- 您需要更改内/外部访问，还是只需更改其中一个？

---

## 必需输入

在进行之前收集或推断：

- **目标组织**：查询/更新的组织别名或用户名（如未指定，则使用默认组织）
- **对象名称**：标准对象 API 名称（例如，`Account`、`Contact`）或自定义对象 API 名称（例如，`Invoice__c`）
- **操作**：获取（检索当前设置）或更新（更改访问级别）
- **访问级别**（用于更新）：内部访问和/或外部访问值

默认值（如未指定）：
- 使用默认连接组织
- 如果只提供了一个访问级别，则假定它适用于内部访问

---

## 工作流程

所有步骤都是按顺序进行的。不要跳过或重新排序。

### 第一阶段 — 检索当前设置

1. **使用 Salesforce CLI 工具 API 查询当前 OWD 设置**：
   `sf data query --query "SELECT QualifiedApiName, InternalSharingModel, ExternalSharingModel FROM EntityDefinition WHERE QualifiedApiName = '<ObjectName>'" --use-tooling-api --target-org <org>`

2. **对于一次性检索所有 OWD 设置**：
   `sf data query --query "SELECT QualifiedApiName, InternalSharingModel, ExternalSharingModel FROM EntityDefinition WHERE IsCustomizable = true ORDER BY QualifiedApiName" --use-tooling-api --target-org <org>`

3. **清晰地呈现结果** — 阅读 `references/access_levels.md` 获取有效值，并向用户显示格式化的表格。

### 第二阶段 — 更新设置（如果请求）

4. **检查不可变/固定 OWD** — 阅读 `references/access_levels.md` "不可变/固定 OWD 对象" 部分。如果请求的更改目标是固定值（例如，价格簿外部 OWD），**立即停止**并向用户解释该值是平台固定的，无法通过任何方式更改。不要尝试部署。

5. **验证请求的访问级别** — 阅读 `references/access_levels.md` 确认该值对目标对象是有效的。如果该值不在该对象允许的值集中，请解释哪些值是有效的，并要求用户选择一个。不要猜测替代值。

6. **使用元数据 API 检索对象元数据**（标准对象和自定义对象使用相同命令）：
   `sf project retrieve start --metadata CustomObject:<ObjectName> --target-org <org>`。这将检索 `<ObjectName>.object-meta.xml`，其中包含 `<sharingModel>` 和 `<externalSharingModel>`。有关完整过程，请参阅 `references/metadata_api_approach.md`。

7. **修改共享设置** — 更新对象 `.object-meta.xml` 中的 `<sharingModel>`（内部访问）和/或 `<externalSharingModel>`（外部访问）。有关详细信息，请阅读 `references/metadata_api_approach.md`。

8. **部署前验证** — 部署前确认：
   - [ ] 外部访问不能比内部访问更宽松
   - [ ] 具有主从关系的对象使用 `ControlledByParent`
   - [ ] 请求的访问级别对目标对象是有效的（见 `references/access_levels.md`）
   - [ ] 满足跨对象约束（见 `references/access_levels.md` 中的 "跨对象约束"）
   - [ ] 目标字段在 `references/access_levels.md` 中未列为不可变/固定

9. **部署更新后的设置**：`sf project deploy start --metadata CustomObject:<ObjectName> --target-org <org>`。

10. **处理部署失败（最多 2 次尝试）**：如果部署失败：
    - 阅读错误消息并确定根本原因。
    - 如果错误指示该值对对象无效或不支持，**停止** — 向用户报告失败并附带确切的错误消息，并解释可能和不可能的情况。除非用户明确请求不同的有效值，否则不要尝试替代值。
    - 如果错误是暂时的（网络超时、认证过期），重试**一次**。
    - **最多尝试 2 次部署同一更改。** 2 次失败后，报告错误，丢弃本地编辑 (`sf project retrieve start --metadata CustomObject:<ObjectName> --target-org <org>`)，并询问用户如何继续。

11. **通过重新运行第一阶段第 1 步的查询来验证更改**。

---

## 规则 / 约束

| 约束 | 理由 |
|-----------|-----------|
| 具有主从关系的对象必须使用 `ControlledByParent` | 平台强制执行此规则 — 尝试其他值会失败 |
| 外部访问不能比内部访问更宽松 | Salesforce 拒绝外部 > 内部的配置 |
| 某些对象具有不可变/固定 OWD（例如，价格簿外部、用户、活动外部） | 这些是平台强制执行的 — 事先解释不可能，不要尝试部署 |
| 价格簿仅接受 `Use` (`ReadSelect`) 或 `No Access` (`None`) 作为内部 OWD；外部始终为 `None` | 标准访问级别（私有/读取/读写）对价格簿无效 |
| 更改 OWD 为更严格的级别会触发共享重新计算 | 这可能在大组织中需要很长时间 — 警告用户 |
| 自定义对象创建时默认为 `Public Read/Write` | 用户可能没有意识到默认值是宽松的 |
| 对于受管理的包自定义对象，请使用包括命名空间前缀的完整 API 名称（例如，`ns__Object__c`） | 命名空间前缀的对象在查询和元数据检索中都需要前缀 |
| 始终在查询前验证组织连接 | 防止令人困惑的错误消息 |
| 每次更改最多 2 次部署尝试 | 防止无限制的重试循环 — 2 次失败后，停止并向用户报告 |

---

## 注意事项

| 问题 | 解决方案 |
|-------|------------|
| 更新时出现 `INSUFFICIENT_ACCESS` 错误 | 用户需要共享管理权限或系统管理员配置文件 |
| OWD 更改似乎卡住 | 共享重新计算正在运行 — 检查设置 > 共享设置查看进度 |
| 查询中找不到自定义对象 | 使用包括 `__c` 后缀的完整 API 名称 |
| `ControlledByParent` 不可用 | 对象没有主从关系 — 使用私有、仅限公共读取或公共读写 |
| 外部访问字段未显示 | 仅当启用外部组织范围默认值时才显示外部共享模型 |
| 查询无结果 | 对象可能不可定制或 API 名称可能不正确 — 验证拼写 |
| 部署失败，价格为无效值 | 价格簿仅接受 `Use`/`None`（内部）和外部固定为 `None` — 不要尝试其他值，向用户解释 |

---

## 输出预期

交付物：
- **对于获取操作**：显示对象名称、内部访问级别和外部访问级别的格式化表格
- **对于更新操作**：更改确认，包括前后比较

---

## 跨技能集成

| 需要 | 委托给 |
|------|-------------|
| 限制 OWD 后创建共享规则 | `platform-sharing-rules-generate` 技能 |
| 将元数据更改部署到另一个组织 | `platform-metadata-deploy` 技能 |

---

## 参考文件索引

| 文件 | 何时阅读 |
|------|-------------|
| `references/access_levels.md` | 验证或解释 OWD 访问级别值时 |
| `references/metadata_api_approach.md` | 使用元数据 API 更新 OWD 而不是工具 API 时 |
| `examples/get_owd_output.md` | 验证格式化输出是否与预期结构匹配 |
| `examples/update_owd_output.md` | 验证更新确认是否与预期结构匹配 |
