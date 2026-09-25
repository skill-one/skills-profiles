## 目标

通过运行所需的 3 步 MCP 管道（fetchGroundedObjectMetadata → flowElementSelection → flowElementGeneration）来生成 Salesforce Flow 元数据，并返回 flow XML。

## 何时使用此技能

当你需要时使用此技能：
- 创建任何类型的 Flow（Screen、Autolaunched、Record-Triggered、Scheduled）
- 生成 Flow 元数据 XML
- 无代码自动化业务流程
- 构建用户引导工作流或后台自动化
- 排查与 Flow 相关的部署错误

## 规格

# Flow 元数据规格

## 概述
Salesforce Flow 是强大的自动化工具，无需代码即可实现复杂的业务流程自动化。Flow 可以通过交互式屏幕收集和处理数据，执行逻辑和计算，操作记录，调用外部服务，并根据各种事件触发。Flow 类型包括 Screen Flow（用户引导）、Autolaunched Flow（后台处理）、Record-Triggered Flow（数据库事件）和 Scheduled Flow（基于时间）。

## 目的
- 使用声明式逻辑和分支自动化复杂的业务流程
- 通过 Screen Flow 引导用户完成多步骤数据收集和决策工作流
- 自动执行 Salesforce 记录的 CRUD 操作
- 通过 Autolaunched Flow 执行后台处理和集成
- 通过 Record-Triggered Flow 实时响应记录更改
- 通过 Scheduled Flow 调度重复任务和批处理操作
- 创建可重用、可维护的自动化，管理员无需代码即可修改

## Flow 生成管道

**强制要求：你必须严格按照这个 3 步管道执行。没有例外。没有捷径。不能跳过步骤。不要手动创建 flow 元数据 XML 或尝试在管道之外生成 flow 元数据。不要尝试使用任何其他工具、API 或方法来生成 flow 元数据。这个管道是生成 Flow 的唯一支持方式。任何偏离都会产生无效或损坏的元数据。**

### MCP 连接详情

**所有 3 个管道步骤都必须使用此 MCP 工具调用：**
- **MCP 工具名称：** `execute_metadata_action`
- **`action` 参数** 选择要运行的管道步骤：`"fetchGroundedObjectMetadata"`、`"flowElementSelection"` 或 `"flowElementGeneration"`

Flow 生成是一个 **严格的 3 步管道**。所有步骤都必须按顺序调用。每个步骤都是必需的。**没有替代方法——这是生成 flow 元数据的唯一方式：**

### 第 1 步（必需）：获取基础对象元数据（`fetchGroundedObjectMetadata`）
获取与 Flow 生成请求相关的组织架构元数据。此步骤是 **强制要求**，必须始终首先调用。

**输入（所有必需）：**
- **userPrompt**（字符串，必需）：用户的自然语言请求
- **inflightMetadata**（数组，必需）：来自本地 sfdx 项目的自定义对象/字段。如果不需要，请使用空数组 `[]`。

**输出：**
- **groundingMetadata**（字符串）：与请求相关的组织架构元数据的基础对象元数据，以 JSON 字符串形式返回。**你必须将此直接传递给第 2 步——它已经是字符串，不需要再次序列化。**

### 第 2 步（必需）：Flow 元素选择（`flowElementSelection`）
根据用户的提示和基础元数据选择 Flow 元素（分配、决策、记录操作等）及其连接。此步骤是 **强制要求**，必须在第 1 步之后调用。

**输入（所有必需）：**
- **userPrompt**（字符串，必需）：用户的自然语言请求（**必须与第 1 步的值相同**）
- **groundingMetadata**（字符串，必需）：组织架构元数据（**必须是与第 1 步输出完全相同的字符串**——直接传递，不要再次序列化）
- **operationId**（字符串，必需）：操作 ID（对于第一次调用，使用空字符串 `""`）

**输出：**
- **operationId**（字符串）：操作 ID。**你必须将其传递给第 3 步。**
- **userOutput**（字符串）：下一步的理由。你可以将其显示给用户。

### 第 3 步（必需）：Flow 元素生成（`flowElementGeneration`）
逐个生成 Flow 元数据元素。此步骤是 **强制要求**，必须在第 2 步之后调用。**必须重复调用，直到 `isComplete` 为 `true`。**

**输入（所有必需）：**
- **operationId**（字符串，必需）：来自第 2 步输出的操作 ID
- **requestSource**（字符串，必需）：请求的来源。使用 **`"A4V"`** 获取 XML 格式的 flow 元数据。

**输出：**
- **isComplete**（布尔值）：指示 Flow 生成是否完成。**你必须检查此值。**
- **result**（字符串）：Flow 元素生成的结果。仅在 `isComplete` 为 `true` 时包含最终的 Flow 元数据。

**强制要求：循环直到完成。永远不要暂停或要求用户确认继续。**
- 一个 Flow 可以有 **任意数量的元素**（10、15 或更多）。每次调用生成一个元素，因此可能需要 **多次** 迭代。这是预期的且正常的。
- 使用来自第 2 步的 `operationId` 和 `requestSource`（使用 `"A4V"` 获取 XML 输出，空字符串或其他值获取 JSON）调用 `flowElementGeneration`。
- 每次调用后检查 `isComplete` 输出和 `result` 字段。
- 如果 `isComplete` 为 `false` **且没有返回错误**，你必须再次使用相同的 `operationId`（来自第 2 步）调用 `flowElementGeneration`。**不要询问用户是否要继续。不要暂停。不要在工作循环中途总结进度。只需继续调用。**
- **不要停止**，直到 `isComplete` 为 `true` **或** 调用动作返回错误。没有 **最大** 迭代次数——无论需要多少次调用，都要继续进行。
- 当 `isComplete` 为 `true` 时，从 `result` 字段中提取 Flow 元数据。
- 如果返回错误，停止循环并将错误显示给用户。

**严格约束（关键）——这些规则适用于生成管道返回的 XML：**
- 不要修改任何块内的内容、值或子节点。
- 不要添加新的节点、标签、属性或文本（不要添加缺失的标签、X/Y 坐标等）。
- 不要删除任何现有节点。

## inflightMetadata 格式
**数据类型：数组（不是字符串）**

**严格命名约定——必须完全遵循：**
| 属性 | 正确名称 | 不要使用 |
|------|---------|---------------|
| 对象 API 名称 | `apiName` | `objectApiName`, `name`, `objectName` |
| 字段 API 名称 | `apiName` | `fieldApiName`, `name`, `fieldName` |
| 字段类型 | `type` | `fieldType`, `dataType` |
| 查找目标 | `referenceTo` | `relatedTo`, `lookupTo`, `reference` |

当需要自定义对象时（显示多个字段数据类型的示例格式）：
```json
[
  {
    "type": "CustomObject",
    "apiName": "CustomerRequest__c",
    "label": "Customer Request",
    "fields": [
      {
        "apiName": "Status__c",
        "type": "Picklist",
        "label": "Status",
        "values": ["New", "In Progress", "Completed"]
      },
      {
        "apiName": "Priority__c",
        "type": "Number",
        "label": "Priority"
      },
      {
        "apiName": "AssignedTo__c",
        "type": "Lookup",
        "label": "Assigned To",
        "referenceTo": "User"
      },
      {
        "apiName": "Description__c",
        "type": "Textarea",
        "label": "Description"
      },
      {
        "apiName": "Email__c",
        "type": "Email",
        "label": "Contact Email"
      },
      {
        "apiName": "DueDate__c",
        "type": "Date",
        "label": "Due Date"
      },
      {
        "apiName": "IsUrgent__c",
        "type": "Boolean",
        "label": "Is Urgent"
      },
      {
        "apiName": "Amount__c",
        "type": "Currency",
        "label": "Amount"
      }
    ],
    "relationships": []
  }
]
```

**支持的字段类型**：Text、Textarea、Number、Picklist、Lookup、Email、Phone、URL、Date、Datetime、Boolean、Checkbox、Currency、Percent

当不需要自定义对象时：
```json
[]
```

### 强制决策逻辑 for inflightMetadata（数据类型：数组）

1. **必需 - 首先扫描**：扫描本地 sfdx 项目，查找与用户 Flow 请求相关的自定义对象和字段。
2. **如果找到相关的自定义对象**：你必须提取并将其作为结构化对象数组（见格式）传递
3. **如果没有找到相关的自定义对象**：你必须传递空数组 `[]`（不是字符串 `"[]"`）
4. **永远不要**：在 inflightMetadata 中传递文本描述、说明或字符串表示
5. **强制要求**：数据类型必须是 ARRAY，不是 STRING

**Vibes 的自定义对象相关说明：**
- 提取对象元数据并映射到 JSON 属性：
    - `apiName`：对象的 API 名称（自定义对象使用 `__c` 后缀）
    - `label`：对象的显示标签
    - `type`：设置为 `"CustomObject"`
    - `fields`：字段对象数组，每个对象包含：
        - `apiName`：字段的 API 名称（自定义字段使用 `__c` 后缀）
        - `type`：字段类型（Text、Number、Picklist、Lookup 等）
        - `label`：字段的显示标签
        - `values`（Picklist 仅限）：picklist 值数组
        - `referenceTo`（Lookup 仅限）：目标对象 API 名称
- 仅包含与正在生成的 Flow 相关的对象和字段

## 🎯 强制增强规则
- **userPrompt**：必需。
    - 如果用户请求 **单个 Flow**：直接使用用户的提示。
    - 如果用户请求 **多个 Flow**：你必须 **拆分** 请求并编写 **每个 Flow 的单独、专注的 `userPrompt`**。每个 `userPrompt` 必须只描述一个 Flow。**不要将整个多 Flow 请求作为单个 `userPrompt` 传递**。见下文的多个 Flow 示例。
- **inflightMetadata**：必需。始终使用 ARRAY 数据类型。
    - 需要时必须使用 `[]`（空数组）
    - 需要时必须使用结构化对象数组
    - **永远不要**使用字符串 `"[]"`——这是不正确的
    - **永远不要**使用文本描述——仅使用结构化对象元数据

### 强制：多个 Flow = 多个独立的管道

**首先**：在调用任何管道步骤之前，检查用户的请求是否包含多个 Flow。如果包含，你必须将其拆分为单独的单 Flow 提示。每个 Flow 都有自己的 3 步管道，并有自己的 `userPrompt`，该 `userPrompt` 只描述该 Flow。**永远不要**将多 Flow 请求作为单个 `userPrompt` 字段传递。**永远不要**将多个 Flow 描述合并到一个 `userPrompt` 中。

当用户请求多个 Flow（例如，“为我的应用创建 Flow：1) ... 2) ... 3) ...”），你必须：
1. **拆分** 请求为单独的 Flow 描述。
2. **为每个 Flow 运行一个独立的 3 步管道**，使用描述该 Flow 的 `userPrompt`。
3. **按顺序执行所有管道**——一个接一个，**永远不要**并行。**不要**在生成第一个 Flow 后停止。**不要**等待用户要求你继续。**不要**在工作流之间总结或停止。继续进行，直到所有请求的 Flow 都已完全生成。

**错误示例 - 多个 Flow 合并到一个 userPrompt 中：**
```json
{
  "userPrompt": "为我的应用创建 Flow：1) 在 ResourceAllocation__c 上创建 Record-Triggered Flow 来更新 Resource__c。2) 创建 Screen Flow 来分配资源。3) 在 Supply__c 上创建 Record-Triggered Flow 来自动标记 Low_Stock__c。",
  ...
}
```

**正确示例 - 每个 Flow 单独调用：**

**Flow 1 - 第 1 步（fetchGroundedObjectMetadata）：**
```json
{
  "userPrompt": "创建一个名为 Tenant_Onboarding 的 Screen Flow，捕获租户详细信息，选择 Status__c = 'Vacant' 的 Unit__c，创建 Lease__c...",
  "inflightMetadata": [...]
}
```
然后调用第 2 步（`flowElementSelection`）使用从第 1 步返回的 `groundingMetadata`，然后调用第 3 步（`flowElementGeneration`）使用从第 2 步返回的 `operationId`。

**Flow 2 - 第 1 步（fetchGroundedObjectMetadata）：**
```json
{
  "userPrompt": "创建一个名为 Generate_Onboarding_Checklist 的 Autolaunched Flow，给定一个 Lease__c Id 输入，查询 OnboardingTask__c...",
  "inflightMetadata": [...]
}
```
然后调用第 2 步和第 3 步为这个 Flow。

**Flow 3 - 第 1 步（fetchGroundedObjectMetadata）：**
```json
{
  "userPrompt": "创建一个名为 Sync_Unit_On_Lease_Changes 的 Record-Triggered Flow，在 Lease__c 的插入和更新时...",
  "inflightMetadata": [...]
}
```
然后调用第 2 步和第 3 步为这个 Flow。

**强制规则：**
- 如果有 N 个 Flow 要生成，必须有 N 个独立的 3 步管道，并且必须执行所有 N 个管道。没有例外。**不要**在生成一个 Flow 后停止。
- **你必须**在开始下一个 Flow 的管道之前，**完全完成**当前 Flow 的 3 步管道（包括循环第 3 步直到 `isComplete` 为 `true` 或返回错误）。**不要**交错或跨 Flow 并行管道。**所有内容都是按顺序执行的——永远不要并行。**
- 完成一个 Flow 的管道后，**立即开始**下一个 Flow 的管道。**不要**暂停、总结或等待用户确认。在 Flow 之间。
- 对于每个 Flow，你必须扫描本地 sfdx 项目，用**该 Flow 提示**特定的自定义对象/字段填充 `inflightMetadata`。
- 每个 Flow 管道都必须有自己的 `inflightMetadata`，其中只包含与该特定 Flow 相关的对象/字段。

## 示例工具调用

**示例 1：仅标准对象（没有自定义对象）**

**第 1 步 - fetchGroundedObjectMetadata：**
```json
{
  "userPrompt": "创建一个按计划触发的 Flow 名为 Daily_Good_Morning，每天在 6:00 AM 运行并发送邮件给运行用户，说早上好。",
  "inflightMetadata": []
}
```

**第 2 步 - flowElementSelection：**
```json
{
  "userPrompt": "创建一个按计划触发的 Flow 名为 Daily_Good_Morning，每天在 6:00 AM 运行并发送邮件给运行用户，说早上好。",
  "groundingMetadata": "<从第 1 步返回的 groundingMetadata 字符串——直接传递，不要再次序列化>",
  "operationId": ""
}
```

**第 3 步 - flowElementGeneration（循环调用）：**
```json
{
  "operationId": "<从第 2 步返回的 operationId>",
  "requestSource": "A4V"
}
```
使用相同的 `operationId` 重复调用，直到 `isComplete` 为 `true` 或返回错误。Flow 可以有任意数量的元素，因此预期多次迭代。当 `isComplete` 为 `true` 时，从 `result` 字段中提取 Flow 元数据。使用 `"requestSource": "A4V"` 获取 XML 格式的 Flow 元数据。

**示例 2：包含来自本地 sfdx 项目的自定义对象**

**第 1 步 - fetchGroundedObjectMetadata：**
```json
{
  "userPrompt": "创建一个 Flow，在分配 Customer Request 时更新其状态",
  "inflightMetadata": [
    {
      "type": "CustomObject",
      "apiName": "CustomerRequest__c",
      "label": "Customer Request",
      "fields": [
        {
          "apiName": "Status__c",
          "type": "Picklist",
          "label": "Status",
          "values": ["New", "In Progress", "Completed"]
        },
        {
          "apiName": "AssignedTo__c",
          "type": "Lookup",
          "label": "Assigned To",
          "referenceTo": "User"
        }
      ],
      "relationships": []
    }
  ]
}
```

**第 2 步 - flowElementSelection：**
```json
{
  "userPrompt": "创建一个 Flow，在分配 Customer Request 时更新其状态",
  "groundingMetadata": "<从第 1 步返回的 groundingMetadata 字符串——直接传递，不要再次序列化>",
  "operationId": ""
}
```

**第 3 步 - flowElementGeneration（循环调用）：**
```json
{
  "operationId": "<从第 2 步返回的 operationId>",
  "requestSource": "A4V"
}
```
使用相同的 `operationId` 重复调用，直到 `isComplete` 为 `true` 或返回错误。Flow 可以有任意数量的元素，因此预期多次迭代。当 `isComplete` 为 `true` 时，从 `result` 字段中提取 Flow 元数据。使用 `"requestSource": "A4V"` 获取 XML 格式的 Flow 元数据。

## 强制最佳实践
- **始终**遵循 3 步管道：fetchGroundedObjectMetadata → flowElementSelection → flowElementGeneration。这是生成 Flow 元数据的唯一方式。没有替代方案。
- 不要手动创建 Flow 元数据 XML、JSON 或此管道之外的任何其他格式。
- 当用户明确要求对已生成的 Flow XML 中的验证或部署错误进行修复时，**允许**对 XML 进行有针对性的手动编辑以解决这些错误。这是“不要手动元数据”规则的唯一例外。
- 不要尝试通过跳过步骤或合并步骤来“优化”。每个步骤都是原子性的，并且是必需的。
- **永远不要**跳过管道中的任何步骤。所有 3 个步骤都是必需的。
- **永远不要**尝试在不调用所有 3 步的情况下生成 Flow 元数据。
- **在任何情况下**都**不要**偏离此管道——即使你认为你知道 Flow 结构。
- 对于单个 Flow 请求：你必须使用用户提示作为 `userPrompt`。
- 对于多个 Flow 请求：你必须为每个 Flow 运行一个独立的 3 步管道**按顺序（一个接一个，永远不要并行）**，并且你必须执行所有它们——**不要**在生成一个 Flow 后停止。
- 你必须将 Flow 需求放在 `userPrompt` 中，**不要**放在 `inflightMetadata` 中。
- `inflightMetadata` 仅用于来自本地项目的自定义对象/字段元数据（见上文）。没有例外。
- 第 3 步必须使用相同的 `operationId`（来自第 2 步）循环调用，直到 `isComplete` 为 `true` 或返回错误。Flow 可以有任意数量的元素——**不要**提前停止，**不要**暂停以询问用户是否要继续，无论迭代次数多少，都要继续进行。
- 你必须只在 `isComplete` 为 `true` 时，从 `result` 字段中提取 Flow 元数据。

## 关键验证清单（必须在每次 Flow 生成之前和之后验证）

**如果未能完全按照此清单执行，将导致损坏或缺失的 Flow 元数据。**

- [ ] **管道**：所有 3 步都按严格顺序（fetchGroundedObjectMetadata → flowElementSelection → flowElementGeneration）调用。没有跳过步骤。
- [ ] **没有手动元数据**：Flow 元数据未以任何方式手动创建、修改或在此管道之外生成
- [ ] **没有偏离**：没有使用替代工具、API 或方法来代替或与此管道一起使用
- [ ] **userPrompt** 包含 **单个** Flow 提示。如果用户请求多个 Flow，请求被拆分，并且每个管道都收到了描述**仅一个 Flow**的 `userPrompt`
- [ ] **userPrompt** 在第 1 步和第 2 步中传递**一致**（相同的值）
- [ ] **inflightMetadata** 是 ARRAY 数据类型（不是字符串）
- [ ] **inflightMetadata** 需要时为 `[]`（数组）
- [ ] **inflightMetadata** 包含通过扫描本地 sfdx 项目提取的相关自定义对象/字段的**结构化对象**
- [ ] **inflightMetadata** **不包含** `"[]"`（字符串）- 必须是 `[]`（数组）
- [ ] **inflightMetadata** **不包含** 文本描述或说明
- [ ] **groundingMetadata** 从第 1 步输出传递给第 2 步输入（它已经是字符串——不要再次序列化）
- [ ] **operationId** 从第 2 步输出传递给第 3 步输入
- [ ] **requestSource** 应始终设置为 `"A4V"`
- [ ] **第 3 步** 使用相同的 `operationId`（来自第 2 步）循环调用，直到 `isComplete` 为 `true` 或返回错误——**不要**暂停，**不要**询问用户是否要继续，无论迭代次数多少
- [ ] **多 Flow**：每个 Flow 的完整管道在开始下一个 Flow 的管道之前完成（**不要**交错）
- [ ] **result** 字段仅在 `isComplete` 为 `true` 时用于提取 XML Flow 元数据
- [ ] **不要添加到 XML**：**不要**添加任何不在原始管道输出中存在的元素、属性或属性。**不要**插入任何内容（不要 `<label>`、`<description>` 或任何其他节点）。最终的 XML 必须与管道返回的完全相同。
- [ ] **错误修复例外**：如果用户明确要求修复验证/部署错误，对 XML 的有针对性手动编辑是允许的，并且“不要添加到 XML”/“不要手动元数据”约束不适用于这些编辑。
