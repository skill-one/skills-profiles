# 管理ManagedEventSubscription

创建、读取、更新和删除 `ManagedEventSubscription` 元数据——Salesforce 用于持久订阅平台事件通道并具有管理重放跟踪的 Salesforce 构造。

## 范围

- **在范围内**：生成和修改 `.managedEventSubscription-meta.xml` 文件以进行创建、读取、更新和删除操作
- **超出范围**：创建底层的平台事件 (`__e`) 通道本身；基于 Flow 或基于 Apex 的事件订阅；将元数据部署到组织
- **仅生成一个文件**——`.managedEventSubscription-meta.xml` 文件。不要生成引用的平台事件对象或任何其他元数据类型。

---

## 澄清问题

在生成之前，如果还不清楚，请确认：

- **主题名称**是什么？(参见 `references/topic-name-formats.md` 中的格式表)
- **开发者名称**是什么？(创建时必需——仅限字母数字和下划线，不能有空格；读取/更新/删除时可选，如果已知 `Id` 则不需要)
- **标签**（人类可读名称）是什么？
- **默认重放**预设——`LATEST`（默认）或 `EARLIEST`？
- **错误恢复重放**预设——`LATEST`（默认）或 `EARLIEST`？
- 初始**状态**应该是什么——`RUN`（活动）或 `STOP`（非活动）？(默认：`RUN`)

---

## 必须输入

继续之前收集或推断：

- **操作**：创建、读取、更新或删除
- **DeveloperName**：创建时必需（成为文件名）；读取/更新/删除时可选，如果提供 `Id` 则不需要
- **Id**：工具 API 记录 Id——可用于读取/更新/删除以识别订阅，而不是 DeveloperName
- **label**：人类可读标签（可以包含空格）
- **topicName**：事件通道路径——查阅 `references/topic-name-formats.md` 获取有效格式（平台事件、变更事件、自定义通道）
- **defaultReplay**：`LATEST` 或 `EARLIEST`（默认：`LATEST`）
- **errorRecoveryReplay**：`LATEST` 或 `EARLIEST`（默认：`LATEST`）
- **state**：`RUN` 或 `STOP`（默认：`RUN`）——`PAUSE` 保留供内部平台使用，将使用 `INVALID_INPUT` 拒绝
- **version**：元数据 API 版本（默认：匹配组织 API 版本，例如 `67.0`）

---

## 工作流程

### 创建

1. **收集输入**——确认 DeveloperName、label、topicName、defaultReplay、errorRecoveryReplay、state、version。为任何省略的字段应用默认值。如果 DeveloperName 未提供，请询问用户——不要从标签中推导它。
2. **确认主题存在**——在继续之前，请询问用户组织中是否已存在事件通道。自己不要生成平台事件对象——这超出此技能的范围。如果用户表示它尚未存在，请停止并指导他们首先使用 `platform-custom-object-generate` 技能创建它，然后返回这里。
3. **读取模板**——加载 `assets/managed-event-subscription-template.xml` 作为起始结构。
4. **生成文件**——生成 `managedEventSubscriptions/<DeveloperName>.managedEventSubscription-meta.xml`，其中填充用户提供的值。
5. **验证**——在展示输出之前，运行以下清单。
6. **指导用户订阅**——部署后，订阅可以通过 `Pub/Sub API` 的 `ManagedSubscribe` RPC 调用使用 `DeveloperName` 或记录 `Id` 识别。要检索 `Id`，请运行：`SELECT Id, DeveloperName FROM ManagedEventSubscription WHERE DeveloperName='<DeveloperName>'` 通过工具 API。

### 读取

1. **识别订阅**——接受 `Id` 或 `DeveloperName`；如果提供，则优先使用 `Id`。
2. **显示文件路径**——`managedEventSubscriptions/<DeveloperName>.managedEventSubscription-meta.xml`（如果已知 DeveloperName）。
3. **检索并展示**——读取并展示当前的 XML 内容。

### 更新

1. **识别订阅**——接受 `Id` 或 `DeveloperName`；如果提供，则优先使用 `Id`。
2. **读取现有文件**——在修改之前加载当前内容。
3. **应用更改**——仅更新指定的字段；保留所有其他字段。
4. **阅读 `references/update-constraints.md`** 以了解创建后无法更改的字段。
5. **验证**——在展示输出之前，运行以下清单。

### 删除

1. **识别订阅**——接受 `Id` 或 `DeveloperName`；在继续之前与用户确认。
2. **警告**——删除 ManagedEventSubscription 会永久删除重放跟踪状态。
3. **生成删除说明**——解释如何删除文件并使用 `destructiveChanges.xml` 部署破坏性更改。
4. **阅读 `references/delete-guide.md`** 以了解破坏性部署程序。

---

## 规则 / 约束

| 约束 | 理由 |
|-----------|-----------|
| `<topicName>` 必须使用有效的路径前缀 | 平台事件使用 `/event/Name__e`；变更事件使用 `/data/Name`；查阅 `references/topic-name-formats.md` 获取所有格式 |
| `<defaultReplay>` 和 `<errorRecoveryReplay>` 必须是 `LATEST` 或 `EARLIEST` | 这些是唯一有效的枚举值；任何其他值都会导致元数据验证失败 |
| `<state>` 必须是 `RUN` 或 `STOP` | `PAUSE` 保留供内部平台使用——API 使用 `INVALID_INPUT: You can create a managed event subscription state field only to RUN or STOP` 拒绝它 |
| 所有六个必需元素必须存在 | `topicName`、`defaultReplay`、`errorRecoveryReplay`、`label`、`state`、`version` 都是必需的；省略任何一项都会导致部署错误 |
| DeveloperName 在组织内必须唯一 | 重复名称会导致 `DUPLICATE_DEVELOPER_NAME` 错误 |
| 不要包含 `<namespacePrefix>`、`<id>` 或 `<createdDate>` | 只读平台字段；包含它们会导致在非打包组织中部署失败 |

---

## 注意事项

| 问题 | 解决方案 |
|-------|------------|
| 部署时 `The topicName field is invalid` | 格式错误或组织中不存在该事件——查阅 `references/topic-name-formats.md` 获取正确路径 |
| 删除后重新创建丢失重放状态 | 删除会丢弃存储的重放位置；重新创建将从 `defaultReplay` 开始——删除后不要重用相同的 DeveloperName |
| SOQL 查询时出现 `INVALID_TYPE` | ManagedEventSubscription 仅可通过工具 API 查询，不能通过标准 SOQL |
| 高流量通道上的 `EARLIEST` 重放 | 激活时可能触发长达 72 小时的回放积压；始终与用户确认 |
| 更老的组织中不支持元数据 | ManagedEventSubscription 需要 API v60.0+；检查组织 API 版本 |
| 生成的 XML 中包含 `eventChannel` 或 `isActive` | 这些是错误的字段名——使用 `topicName` 和 `state` (`RUN`/`STOP`) 代替 |
| 生成的 XML 中包含 `PAUSE` 状态 | `PAUSE` 保留供内部平台使用，将使用 `INVALID_INPUT` 拒绝——仅使用 `RUN` 或 `STOP` |
| 用户不确定如何为 Pub/Sub API 识别订阅 | `DeveloperName` 和记录 `Id` 都可用于 `ManagedSubscribe` RPC——如果需要，通过工具 API 检索 `Id`：`SELECT Id FROM ManagedEventSubscription WHERE DeveloperName='<name>'` |
| 创建/更新/删除后 Pub/Sub API 中的更改不会立即反映 | 创建/更新/删除后，Pub/Sub API 可能需要长达 ~2 分钟才能反映新配置；如果 `ManagedSubscribe` 返回 NOT_FOUND，请等待并重试 |

---

## 验证清单

在展示任何生成的 XML 之前：

- [ ] `<topicName>` 是否遵循 `references/topic-name-formats.md` 中的有效路径格式？(`/event/Name__e`、`/data/NameChangeEvent`、`/data/ChangeEvents`、`/event/Name__chn`、`/data/Name__chn`)
- [ ] `<defaultReplay>` 是否完全为 `LATEST` 或 `EARLIEST`？
- [ ] `<errorRecoveryReplay>` 是否完全为 `LATEST` 或 `EARLIEST`？
- [ ] `<state>` 是否完全为 `RUN` 或 `STOP`？(`PAUSE` 对用户创建的订阅无效)
- [ ] `<label>` 是否已填充？
- [ ] `<version>` 是否存在（例如 `67.0`）？
- [ ] 是否缺少只读字段 (`<id>`、`<createdDate>`、`<namespacePrefix>`）？
- [ ] 文件名是否与 DeveloperName 完全匹配？

---

## 输出预期

- **创建 / 更新**：`managedEventSubscriptions/<DeveloperName>.managedEventSubscription-meta.xml`——这是唯一要生成的文件
- **删除**：删除文件并通过 `destructiveChanges.xml` 部署的说明
- **读取**：展示现有文件内容

---

## 跨技能集成

| 需要 | 委托给 |
|-------|-------------|
| 创建正在订阅的平台事件通道 (`__e`) | `platform-custom-object-generate` 技能 |
| 通过 Flow（流程自动化）订阅 | `automation-flow-generate` 技能 |
| 将元数据部署到组织 | `platform-metadata-deploy` 技能 |

---

## 参考文件索引

| 文件 | 何时阅读 |
|------|-------------|
| `assets/managed-event-subscription-template.xml` | 在生成任何新订阅之前——用作起始结构 |
| `references/topic-name-formats.md` | 设置 `<topicName>` 时——涵盖平台事件、变更事件和自定义通道 |
| `references/update-constraints.md` | 在更新工作流期间——检查创建后不可变字段 |
| `references/delete-guide.md` | 在删除工作流期间——用于破坏性更改部署程序 |
