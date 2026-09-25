# 管理变更数据捕获启用

生成订阅 Salesforce 对象的变更数据捕获元数据：默认 `ChangeEvents` 通道或自定义通道的 `PlatformEventChannelMember` 文件，以及新自定义通道的 `PlatformEventChannel` 文件。涵盖丰富字段、过滤表达式以及元数据 API 实际接受的规范命名和值格式（这些与许多内部测试用例和代码搜索结果中的值不同）。

## 范围

- **在范围内**：为 CDC 生成 `PlatformEventChannelMember` 和 `PlatformEventChannel` 元数据。订阅标准对象、自定义对象或两者。配置丰富字段。配置过滤表达式。定义自定义数据通道。
- **超出范围**：发布自定义平台事件（PE）——那是另一种元数据类型（`PlatformEvent`）。Pub/Sub API 或外部 Kafka/Bayeux 配置。定价/限制指南——请参阅用户 [CDC 开发者指南](https://developer.salesforce.com/docs/atlas.en-us.change_data_capture.meta/change_data_capture/)。Apex 中的程序化事件总线订阅者。

---

## 澄清问题

在生成之前，如果尚未明确，请与用户确认：

- 需要哪些实体（或实体）启用 CDC？标准、自定义或两者？
- 默认通道 (`ChangeEvents`) 或自定义通道？如果是自定义通道，通道标签是什么？
- 需要任何丰富字段吗？（即使它们没有更改，消费者也需要查找 ID。）
- 需要任何过滤表达式吗？（SOQL-WHERE 子句体，用于限制哪些变更事件发出。）

---

## 必需输入

在继续之前收集或推断：

- **源实体 API 名称** — 例如 `Account`、`Lead`、`Order__c`。技能内部将此转换为 **变更事件实体名称**（见工作流步骤 2）。
- **通道** — 要么 `ChangeEvents`（默认），要么自定义通道的开发者名称，以 `__chn` 结尾。
- **丰富字段（可选）** — 源对象上字段 API 名称的列表，其值应包含在每次变更事件中。
- **过滤表达式（可选）** — 变更事件有效负载上字段的谓词（例如 `Status__c != null`）。

默认值（如未指定）：
- 通道：`ChangeEvents`（默认 CDC 通道——无路径前缀）。
- 丰富字段：无。
- 过滤表达式：无。

如果用户提供清晰、完整的请求，则立即生成，无需不必要的来回沟通。

---

## 工作流

所有步骤都是按顺序执行的。不要跳过或重新排序。

**在生成任何内容之前，了解唯一有效的 CDC 元数据类型**：CDC 完全通过 `PlatformEventChannelMember`（每个订阅实体一个）和 `PlatformEventChannel`（仅用于自定义通道）表示。**不要使用 `<ChangeDataCapture>`、`.changeDataCapture-meta.xml`、`changeDataCapture/` 目录、`EnableChangeDataCapture` 或 `ManagedEventSubscription` — 这些都不在 CDC 范围内。** 如果你发现自己正在编写它们，请停止并使用 `PlatformEventChannelMember` 文件。

1. **确定通道** — 如果用户指定自定义通道，则生成 `PlatformEventChannel` 文件（见步骤 4）。否则，使用字面值 `ChangeEvents` 作为默认通道。

2. **将源实体转换为变更事件实体名称** — `<selectedEntity>` 是 **变更事件** 类型，而不是源对象：

   | 源对象 | `<selectedEntity>` 值 |
   |---|---|
   | `Account` | `AccountChangeEvent` |
   | `Lead` | `LeadChangeEvent` |
   | `Contact` | `ContactChangeEvent` |
   | `Order__c`（自定义） | `Order__ChangeEvent` |
   | `MyThing__c`（自定义） | `MyThing__ChangeEvent` |

   对于标准对象：追加 `ChangeEvent`。对于自定义对象：将尾随的 `__c` 替换为 `__ChangeEvent`（双下划线被保留）。

3. **生成通道成员文件** — 每个`(实体, 通道)`对生成一个文件。**文件名和 fullName 始终在实体主干和 `ChangeEvent` 之间使用单个下划线**——这与 `selectedEntity` 在 XML 主体中的格式无关。对于自定义对象，在形成文件名时从源名称中删除 `__c`：

   | 源对象 | 文件名（和 fullName） | `<selectedEntity>`（在 XML 中） |
   |---|---|---|
   | `Account` | `Account_ChangeEvent.platformEventChannelMember-meta.xml` | `AccountChangeEvent` |
   | `Lead` | `Lead_ChangeEvent.platformEventChannelMember-meta.xml` | `LeadChangeEvent` |
   | `Order__c` | `Order_ChangeEvent.platformEventChannelMember-meta.xml`（不是 `Order__ChangeEvent`） | `Order__ChangeEvent` |
   | `MyThing__c` | `MyThing_ChangeEvent.platformEventChannelMember-meta.xml`（不是 `MyThing__ChangeEvent`） | `MyThing__ChangeEvent` |

   自定义对象的情况是最容易出错的地方——文件名使用单个下划线，`selectedEntity` 保留双下划线。阅读 `assets/PlatformEventChannelMember-template.xml` 作为结构模板。

4. **对于自定义通道**，生成 `PlatformEventChannel` 文件——如果任何成员引用非默认通道，则必须生成。从用户的标签派生开发者名称：删除空格和非字母数字字符，转换为驼峰命名法，然后**始终**追加字面后缀 `__chn`。文件名和通道的 `<eventChannel>` 引用必须使用此确切形式，否则部署会失败并显示 `Invalid channel name`：

   | 用户说 | 开发者名称 | 文件名 |
   |---|---|---|
   | `Partner Sync` | `PartnerSync__chn` | `PartnerSync__chn.platformEventChannel-meta.xml`（不是 `Partner_Sync...` 或 `PartnerSync...`） |
   | `Order Updates` | `OrderUpdates__chn` | `OrderUpdates__chn.platformEventChannel-meta.xml` |
   | `data sync` | `DataSync__chn` | `DataSync__chn.platformEventChannel-meta.xml` |

   该通道上的成员通过相同的开发者名称引用它：`<eventChannel>PartnerSync__chn</eventChannel>`。阅读 `assets/PlatformEventChannel-template.xml`。

5. **如果请求添加丰富字段** — 重复 `<enrichedFields><name>FIELD_API_NAME</name></enrichedFields>` 块对于每个字段。名称必须是源实体上的**单跳 API 名称**——验证工作包括：标准查找 ID（`OwnerId`、`ParentId`）、自定义查找字段（`MyLookup__c`）和自定义非关系字段（`Region__c`、`Status__c`）。关系遍历（如 `Owner.Name` 或 `Parent.Account.Industry`）会被部署拒绝，显示 "The selected field, X.Y, isn't valid"。

6. **如果请求添加过滤表达式** — 将谓词包裹在 `<filterExpression>...</filterExpression>` 中。主体是 WHERE 子句体，不带 `WHERE` 关键字（例如 `Status__c != null`，而不是 `WHERE Status__c != null`）。有关支持的运算符、字段类型和陷阱，请阅读 `references/filter-expressions.md`。

---

## 规则 / 限制

| 限制 | 理由 |
|---|---|
| `<selectedEntity>` 是变更事件类型名称，不是源对象名称 | 元数据 API 将成员绑定到变更事件实体——直接传递 `Account` 会失败并显示 "invalid event in selectedEntity"。 |
| 成员 fullName 使用 **单个** 下划线：`Account_ChangeEvent` | 双下划线形式（`Account__ChangeEvent`）被解析为 `<namespace>__<name>` 并被拒绝： "Cannot create a new component with the namespace: Account"。 |
| 默认通道值是 `ChangeEvents` 的确切值——无路径前缀 | 较旧的固定装置和某些文档显示 `data/ChangeEvents`；部署会返回 "Unable to find the specified channel" 对于该值。 |
| 丰富字段名称是源实体上的单跳 API 名称 | 标准（`OwnerId`）、自定义查找（`MyLookup__c`）和自定义非关系（`Region__c`）都有效。拒绝遍历（如 `Owner.Name`）： "The selected field, X.Y, isn't valid"。 |
| `<filterExpression>` 主体没有 `WHERE` 关键字 | 部署返回 "filter expression has syntax errors: unexpected token: 'WHERE'"。 |
| 过滤不能引用 `IsDeleted` 或执行关系遍历（`Owner.Username`） | 部署会拒绝并显示 "field is invalid"。 |
| 日期时间字段在过滤中仅支持 **相等** 运算符（`=`、`!=`）——不支持 `<` / `>` | 部署返回 "Only equality operators are supported for this field type or value"。使用命名日期字面量：`LastModifiedDate = TODAY`。 |
| 过滤右侧必须是字面量——不能进行字段到字段的比较 | `BillingCity = ShippingCity` 返回 "unexpected token: 'ShippingCity'"。 |
| 复合字段（例如 `BillingAddress`）需要在过滤中使用点分组件访问 | `BillingAddress.City = 'X'` 部署；扁平 `BillingCity` 被拒绝为 "field is invalid"；原始 `BillingAddress` 被拒绝为 "has to be used with a component field"。注意这是 `<enrichedFields>` 的**相反**，后者使用扁平名称。 |
| 自定义通道文件在 meta-xml 后缀之前以 `__chn` 结尾 | Salesforce 的 MDAPI 命名约定；不匹配会导致部署歧义。 |
| 自定义通道 XML 必须包含 `<channelType>data</channelType>` | 没有 `data`，通道会被拒绝用于 CDC（其他类型存在用于流/事件通道）。 |
| 源自定义对象必须已存在（或在同一事务中部署） | `Foo__c` 的变更事件实体不存在，直到 `Foo__c` 存在；否则成员部署会失败。 |
| 永远不要为默认 `ChangeEvents` 通道生成 `PlatformEventChannel` 文件 | 默认通道是系统提供的。在成员上通过 `<eventChannel>ChangeEvents</eventChannel>` 引用它，但只有自定义（`__chn`）通道需要一个 channel-meta 文件。 |
| `PlatformEventChannelMember` 仅接受四个元素：`<enrichedFields>`、`<eventChannel>`、`<filterExpression>`、`<selectedEntity>` | 添加 `<description>`、`<isActive>`、`<masterLabel>` 或任何其他元素会导致 XML schema 验证失败： "Element {...} invalid at this location"。坚持四个文档化元素。 |
| `PlatformEventChannel` 仅接受两个元素：`<channelType>` 和 `<label>` | 添加 `<masterLabel>`、`<description>` 等。会生成 "Element {...}masterLabel invalid at this location in type PlatformEventChannel"。使用 `<label>`，而不是 `<masterLabel>`。 |
| 生成的元数据文件仅——从不从此技能运行 `sf project deploy start` | 此技能生成工件；部署是单独的生命周期问题。 |

---

## 注意事项

| 问题 | 解决方案 |
|---|---|
| `Unable to find the specified channel` | 设置 `<eventChannel>ChangeEvents</eventChannel>`（无 `data/` 前缀）。 |
| `The PlatformEventChannelMember can't be created because it references an invalid event in the "selectedEntity" field` | 使用变更事件名称，而不是源对象：`AccountChangeEvent`，而不是 `Account`。 |
| `Cannot create a new component with the namespace: <Object>` | 将文件重命名为使用单个下划线：`Account_ChangeEvent...`，而不是 `Account__ChangeEvent...`。 |
| `The selected field, X.Y, isn't valid`（在 `<enrichedFields>` 中） | 将 `Owner.Name` 替换为 `OwnerId`。CDC 自动丰富查找；仅单跳字段 API 名称有效。 |
| `filter expression has syntax errors: unexpected token: 'WHERE'` | 移除 `WHERE` 关键字。主体是谓词仅。 |
| `The BillingCity field in the filter expression is invalid`（或任何扁平地址组件） | 使用点分复合形式：`BillingAddress.City`，而不是 `BillingCity`。参见 `references/filter-expressions.md` 获取完整的复合字段矩阵。 |
| 自定义对象成员失败并显示 "ChangeEvent doesn't exist" | 源对象尚未部署。确保 `Foo__c` 对象元数据在同一部署中或已在组织中。 |
| `DUPLICATE_VALUE` 在第二次部署时 | 成员已订阅。要么先删除，要么跳过——CDC 不直接支持成员的 upsert。 |
| `sf infra error (TypeInferenceError, DeployMetadata): Could not infer a metadata type` 对于 `.changeDataCapture-meta.xml` 文件 | 该文件扩展名和元数据类型不存在。将 `changeDataCapture/<Entity>.changeDataCapture-meta.xml` 文件替换为 `platformEventChannelMembers/<Entity>_ChangeEvent.platformEventChannelMember-meta.xml` 文件。 |
| 用户说 "subscribe Order__c" 但实际是指标准 `Order` | 确认——`OrderChangeEvent`（标准）和 `Order__ChangeEvent`（自定义）是不同的实体。 |

---

## 输出预期

交付物：
- 每个订阅实体一个 `force-app/.../platformEventChannelMembers/<Entity>_ChangeEvent.platformEventChannelMember-meta.xml`。
- 每个自定义通道（如果有）一个 `force-app/.../platformEventChannels/<DevName>__chn.platformEventChannel-meta.xml`。

文件结构遵循 `assets` 中的模板。

生成文件后，用户可以使用 `sf project deploy start --dry-run -d <path> --target-org <alias>` 在部署前验证它们。如果干运行时出现不熟悉的错误，`references/deploy-troubleshooting.md` 将常见部署错误映射到元数据侧的修复方案。

---

## 跨技能集成

| 需要 | 委托给 |
|---|---|
| 生成源自定义对象 | `platform-custom-object-generate` 技能 |
| 生成被丰富或过滤引用的自定义字段 | `platform-custom-field-generate` 技能 |
| 为消费变更事件的用户构建权限集 | `platform-permission-set-generate` 技能 |

---

## 参考文件索引

| 文件 | 何时阅读 |
|---|---|
| `assets/PlatformEventChannelMember-template.xml` | 步骤 3 — 通道成员的起始结构 |
| `assets/PlatformEventChannel-template.xml` | 步骤 4 — 自定义通道的起始结构 |
| `references/filter-expressions.md` | 步骤 6 — 编写过滤表达式时的支持运算符和字段类型矩阵 |
| `references/deploy-troubleshooting.md` | 当用户报告干运行部署错误并请求帮助诊断时 |
