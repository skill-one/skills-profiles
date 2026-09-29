---
name: automation-flow-generate
description: 使用MCP工具的execute_metadata_action功能生成Salesforce流程。当用户要求创建、构建或生成流程时使用——包括屏幕流程、自动启动流程、记录触发流程（保存前/保存后）、计划流程。同时，也适用于类似流程的请求，例如“当记录被创建时”、“每日触发”、“发送邮件时”、“更新字段时”、“自动化”、“工作流”或“流程XML/元数据”。这是用于Salesforce流程生成的唯一技能。
---

## 目标

通过运行所需的 3 步 MCP 管道（fetchGroundedObjectMetadata → flowElementSelection → flowElementGeneration）来生成 Salesforce Flow 元数据，并返回 Flow XML。

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

## Flow 生成管道

**强制要求：你必须严格按照这个 3 步管道执行。没有例外。没有捷径。不能跳过步骤。不要手动创建 Flow 元数据 XML 或尝试在此管道之外生成 Flow 元数据。不要尝试使用任何其他工具、API 或方法来生成 Flow 元数据。此管道是生成 Flow 的唯一支持方式。任何偏离都会产生无效或损坏的元数据。**

### MCP 连接详情

**所有 3 个管道步骤都必须使用此 MCP 工具调用：**
- **MCP 工具名称：** `execute_metadata_action`
- **`action` 参数** 选择要运行的管道步骤：`"fetchGroundedObjectMetadata"`、`"flowElementSelection"` 或 `"flowElementGeneration"`

Flow 生成是一个 **严格的 3 步管道**。所有步骤都必须按顺序调用。每个步骤都是必需的。**没有替代方法——这是唯一生成 Flow 元数据的方法：**

### 第 1 步（必需）：获取基础对象元数据 (`fetchGroundedObjectMetadata`)
获取与 Flow 生成请求相关的组织架构元数据。此步骤是 **强制要求**，并且必须始终首先调用。

**输入（所有必需）：**
- **userPrompt**（字符串，必需）：用户的自然语言请求
- **inflightMetadata**（数组，必需）：来自本地 sfdx 项目的自定义对象/字段。如果不需要，请使用空数组 `[]`。

**输出：**
- **groundingMetadata**（字符串）：与组织架构请求相关的已获取对象元数据，以 JSON 字符串形式返回。**你必须将此直接传递给第 2 步——它已经是字符串，不需要再次序列化。**

### 第 2 步（必需）：Flow 元素选择 (`flowElementSelection`)
根据用户的提示和已获取的元数据选择 Flow 元素（分配、决策、记录操作等）及其连接。此步骤是 **强制要求**，并且必须在第 1 步之后调用。

**输入（所有必需）：**
- **userPrompt**（字符串，必需）：用户的自然语言请求（**必须与第 1 步的值相同**）
- **groundingMetadata**（字符串，必需）：组织架构元数据（**必须是与第 1 步输出完全相同的字符串**——直接传递，不要再次序列化）
- **operationId**（字符串，必需）：操作 ID（对于第一次调用，使用空字符串 `""`）

**输出：**
- **operationId**（字符串）：操作 ID。**你必须将其传递给第 3 步。**
- **userOutput**（字符串）：下一步的推理。你可以将其显示给用户。

### 第 3 步（必需）：Flow 元素生成 (`flowElementGeneration`)
逐个生成 Flow 元数据元素。此步骤是 **强制要求**，并且必须在第 2 步之后调用。**必须在一个循环中重复调用，直到 `isComplete` 为 `true`。**

**输入（所有必需）：**
- **operationId**（字符串，必需）：来自第 2 步输出的操作 ID
- **requestSource**（字符串，必需）：请求的来源。使用 **`"A4V"`** 获取 XML 格式的 Flow 元数据。

**输出：**
- **isComplete**（布尔值）：指示 Flow 生成是否完成。**你必须检查此值。**
- **result**（字符串）：Flow 元素生成的结果。当 `isComplete` 为 `true` 时，包含最终的 Flow 元数据 **仅当 `isComplete` 为 `true` 时**。

**强制要求：循环直到完成。永远不要暂停或要求用户确认继续。**
- 一个 Flow 可以有 **任意数量的元素**。每次调用生成一个元素，因此可能需要 **多次** 迭代。
- 使用第 2 步的 `operationId` 和 `requestSource` 调用 `flowElementGeneration`（使用 `"A4V"` 获取 XML 输出，空字符串或其他值获取 JSON）。
- 每次调用后检查 `isComplete` 输出和 `result` 字段。
- 如果 `isComplete` 为 `false` **并且没有返回错误**，你必须再次使用第 2 步的 **相同 `operationId`** 调用 `flowElementGeneration`。**不要询问用户是否要继续。不要暂停。不要在循环中途总结进度。只需继续调用**——没有**最大**迭代次数限制。
- 当 `isComplete` 为 `true` 时，从 `result` 字段中提取 Flow 元数据。
- 如果返回错误，停止循环并将错误显示给用户。

**严格约束（关键）——这些规则适用于生成管道返回的 XML：**
- 不要修改任何块内的内容、值或子节点。
- 不要添加新节点、标签、属性或文本（不要添加缺失的标签、X/Y 坐标等）。
- 不要删除任何现有节点。

**Canvas 模式。** 一个全新的基于 Canvas 的 Flow 需要一个 `<processMetadataValues>` `CanvasMode`=`AUTO_LAYOUT_CANVAS` 条目（与 `BuilderType` 无关），否则它会在 **Free-Form** 中打开。严格约束禁止手动编辑 XML，因此必须来自生成管道——如果返回的 XML 缺少它，请显示管道差距；不要手动编辑。（非 Canvas 类型如 `CustomerLifecycle` 不包含任何内容——不要标记这些。）

## inflightMetadata 格式
**数据类型：数组（不是字符串）**

**严格命名约定——必须完全遵循：**
| 属性 | 正确名称 | 不要使用 |
|----------|-------------|---------------|
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

### 强制性决策逻辑 for inflightMetadata（数据类型：数组）

1. **必需 - 首先扫描**：扫描本地 sfdx 项目，查找与用户 Flow 请求相关的自定义对象和字段。
2. **如果找到相关的自定义对象**：你必须提取并将它们作为结构化对象数组（见格式）传递
3. **如果没有找到相关的自定义对象**：你必须传递空数组 `[]`（不是字符串 `"[]"`）
4. **永远不要**：在 inflightMetadata 中传递文本描述、说明或字符串表示
5. **必须**：数据类型必须是 ARRAY，不是 STRING

**当自定义对象相关时，Vibes 的说明：**
- 提取对象元数据并映射到 JSON 属性：
    - `apiName`：对象的 API 名称（自定义对象使用 `__c` 后缀）
    - `label`：对象的显示标签
    - `type`：设置为 `"CustomObject"`
    - `fields`：字段对象数组，每个对象包含：
        - `apiName`：字段的 API 名称（自定义字段使用 `__c` 后缀）
        - `type`：字段类型（Text、Number、Picklist、Lookup 等）
        - `label`：字段的显示标签
        - `values`：（Picklist 仅限）picklist 值数组
        - `referenceTo`：（Lookup 仅限）目标对象 API 名称
- 仅包括与正在生成的 Flow 相关的对象和字段

## 强制性增强规则
- **userPrompt**：必需。
    - 如果用户请求 **单个 Flow**：使用用户的提示原样。
    - 如果用户请求 **多个 Flow**：你必须 **拆分** 请求，并为每个单独的 Flow 编写 **专注的 `userPrompt`**。每个 `userPrompt` 必须只描述一个 Flow。**不要**将整个多 Flow 请求作为单个 `userPrompt` 传递。见下文的多个 Flow 部分示例。
- **inflightMetadata**：必需。始终使用 ARRAY 数据类型。
    - 必须使用 `[]`（空数组）当不需要自定义对象时
    - 必须使用结构化对象数组当自定义对象相关时
    - **永远不要**使用字符串 `"[]"`——这是不正确的
    - **永远不要**使用文本描述——仅使用结构化对象元数据

## Flow 模式指导

管道从你的 `userPrompt` 中选择 Flow 元素。模糊的提示会导致管道选择错误的结构，生成失败的部署元数据。当请求匹配以下模式之一时，在传递给第 1 步和第 2 步的 `userPrompt` 中明确意图，以便管道选择正确的元素。

### 定时 Flow（"daily", "weekly", "every Sunday", "runs once a week at 10PM"）

一个周期性的基于时间的 Flow 是一个 **定时** Flow。计划存在于 **开始元素**：`triggerType` 是 `Scheduled`，并且 `<schedule>` 块包含 `<frequency>`（例如 `Weekly`）、`<startDate>` 和 `<startTime>`。不要期望 `startDate`/`startTime` 在 `FlowScheduledPath` 元素上——定时 Flow 的节奏在 `<start><schedule>`，而不是在定时路径上。

为了选择定时 Flow 的记录，将记录条件放在 **开始元素的过滤器**（在 `<start>` 上有 `<object>` 和 `<filters>`），这会针对每个匹配的记录运行 Flow，并将 `$Record` 绑定到每个记录。优先于此，而不是添加一个循环重新查询并迭代相同的对象——一个开始过滤的定时 Flow 不需要 Loop 来遍历触发对象记录。

当提示说“每周运行一次 / 每周日运行 / 按时间运行”时，`userPrompt` 应声明：定时触发、频率、开始时间以及触发对象上的记录过滤器。

### "Autolaunched" 是字面意思

一个 **"autolaunched"**/"no-trigger" 请求构建一个 **无触发** Flow（没有 `triggerType`、`object` 或 `<schedule>` 在开始上）——将“针对.../当 X”/时间意图放在 **主体** 中，而不是触发；只有当被要求时才添加一个。

### 计数相关记录（"count all related X", "number of X"）

要存储记录计数，使用 **单个** 分配元素，带有 `<operator>AssignCount</operator>`，将集合（记录-查找结果）分配到一个 Number 变量中。不要为单个计数发出两个分配元素，并且不要给两个分配元素相同的 `name`——重复分配名称，或两个分配元素执行单个逻辑计数，都会导致部署失败。一个查找 → 一个 `AssignCount` 分配 → 一个记录更新。

### 不要编造提示未请求的动作

仅生成提示请求的元素。如果提示命名了触发器但没有说明行为（例如，“创建一个当记录创建时触发的 Flow”而没有说明行为），不要添加一个 Chatter post、电子邮件或其他未请求的动作。一个未请求的动作，如 `chatterPost`，会产生引用未定义类型的元数据，并导致部署失败。当请求的行为确实不存在时，生成最小的有效触发器，不要编造副作用。

### 强制性：多个 Flow = 多个独立的管道

**首先：在调用任何管道步骤之前，检查用户的请求是否包含多个 Flow。如果它包含多个 Flow，你必须将其拆分为单独的单 Flow 提示。每个 Flow 都有自己的 3 步管道，其 `userPrompt` 只描述该 Flow。**

**永远不要**将多 Flow 请求作为单个 `userPrompt` 字段传递。**永远不要**将多个 Flow 描述捆绑成一个 `userPrompt`。

当用户请求多个 Flow（例如，“为我的应用创建 Flow：1) ... 2) ... 3) ...”）时，你必须：
1. **拆分** 请求为单独的 Flow 描述。
2. **为每个 Flow 运行一个单独的 3 步管道**，使用描述该 Flow 的 `userPrompt`。
3. **按顺序执行所有管道**——一个接一个，**永远不要**并行。不要在第一个 Flow 后停止。不要等待用户要求你继续。不要总结并停止。继续进行，直到所有请求的 Flow 都已完全生成。

**错误 - 多个 Flow 捆绑成一个 userPrompt：**
```json
{
  "userPrompt": "为应用创建 Flow：1) 在 ResourceAllocation__c 上触发的 Record-Triggered Flow 来更新 Resource__c。2) Screen Flow 来分配资源。3) 在 Supply__c 上触发的 Record-Triggered Flow 来自动标记 Low_Stock__c。",
  ...
}
```

**正确 - 每个 Flow 单独调用：**

**Flow 1 - 第 1 步（fetchGroundedObjectMetadata）：**
```json
{
  "userPrompt": "创建一个名为 Tenant_Onboarding 的 Screen Flow，捕获租户详细信息，选择 Status__c = 'Vacant' 的 Unit__c，创建 Lease__c...",
  "inflightMetadata": [...]
}
```
然后调用第 2 步（`flowElementSelection`）使用从第 1 步获取的 `groundingMetadata`，然后调用第 3 步（`flowElementGeneration`）使用从第 2 步获取的 `operationId`。

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
- 如果有 N 个 Flow 要生成，必须有 N 个单独的 3 步管道，并且所有 N 个管道都必须执行。没有例外。不要在生成一个 Flow 后停止。
- **你必须完全完成当前 Flow 的 3 步管道（包括循环第 3 步直到 `isComplete` 为 `true` 或返回错误）**，然后才能开始下一个 Flow 的管道。**不要**交错或并行化跨 Flow 的管道。**所有都是顺序的——永远不要并行。**
- 完成一个 Flow 的管道后，**立即开始下一个 Flow 的管道**。不要暂停、总结或等待用户确认在 Flow 之间。
- 对于每个 Flow，你必须扫描本地 sfdx 项目以用特定于该 Flow 提示的自定义对象/字段填充 `inflightMetadata`。
- 每个Flow 管道都必须有自己的 `inflightMetadata`，其中只包含与该特定 Flow 相关的对象/字段。

## 示例工具调用

**示例 1：仅标准对象（没有自定义对象）**

**步骤 1 - fetchGroundedObjectMetadata：**
```json
{
  "userPrompt": "创建一个名为 Daily_Good_Morning 的计划触发流程，每天早上 6:00 运行，并向运行用户发送一条早上好邮件。",
  "inflightMetadata": []
}
```

**步骤 2 - flowElementSelection：**
```json
{
  "userPrompt": "创建一个名为 Daily_Good_Morning 的计划触发流程，每天早上 6:00 运行，并向运行用户发送一条早上好邮件。",
  "groundingMetadata": "<从步骤 1 获取的 groundingMetadata 字符串 — 直接传递，不要再次序列化>",
  "operationId": ""
}
```

**步骤 3 - flowElementGeneration（在一个循环中调用）：**
```json
{
  "operationId": "<从步骤 2 获取的 operationId>",
  "requestSource": "A4V"
}
```
按照步骤 3 的方式循环（相同的 `operationId`，`requestSource: "A4V"`），直到 `isComplete` 为 `true` 或返回错误；然后从 `result` 中提取 XML。

**示例 2：使用本地 sfdx 项目中的自定义对象**

**步骤 1 - fetchGroundedObjectMetadata：**
```json
{
  "userPrompt": "创建一个流程，在分配客户请求时更新其状态",
  "inflightMetadata": [
    {
      "type": "CustomObject",
      "apiName": "CustomerRequest__c",
      "label": "客户请求",
      "fields": [
        {
          "apiName": "Status__c",
          "type": "Picklist",
          "label": "状态",
          "values": ["新", "进行中", "已完成"]
        },
        {
          "apiName": "AssignedTo__c",
          "type": "Lookup",
          "label": "分配给",
          "referenceTo": "User"
        }
      ],
      "relationships": []
    }
  ]
}
```

**步骤 2 - flowElementSelection：**
```json
{
  "userPrompt": "创建一个流程，在分配客户请求时更新其状态",
  "groundingMetadata": "<从步骤 1 获取的 groundingMetadata 字符串 — 直接传递，不要再次序列化>",
  "operationId": ""
}
```

**步骤 3 - flowElementGeneration（在一个循环中调用）：**
```json
{
  "operationId": "<从步骤 2 获取的 operationId>",
  "requestSource": "A4V"
}
```
按照示例 1 的步骤 3 的方式循环。

## 关键验证清单（每次生成流程前和后都必须验证）

**不按此清单严格执行将导致流程元数据损坏或缺失。**

- [ ] **流程**：所有 3 个步骤都必须按严格顺序调用（fetchGroundedObjectMetadata → flowElementSelection → flowElementGeneration）。不能跳过任何步骤、合并步骤或用其他工具/API 替代。此流程是生成流程元数据的唯一方式。
- [ ] **无手动元数据**：流程元数据不能在流程外创建、修改或生成，并且返回的 XML 中没有添加任何元素/属性（没有 `<label>`、`<description>` 或任何其他节点）。最终 XML 必须与流程返回的完全一致。**例外情况**：如果用户明确要求对已生成的 XML 中的验证/部署错误进行修复，则允许进行有针对性的手动编辑。
- [ ] **userPrompt** 包含一个 **单个** 流程提示（多流程请求会被拆分，每个 `userPrompt` 一个），包含流程要求（不是 `inflightMetadata`），并且与步骤 1 和步骤 2 完全相同地传递。
- [ ] **inflightMetadata** 是 ARRAY 数据类型（不是字符串 `"[]"`），在没有自定义对象时为 `[]`，否则包含从本地 sfdx 项目扫描的结构化对象/字段元数据 — 不能包含文本描述。
- [ ] **groundingMetadata** 从步骤 1 输出直接传递给步骤 2 输入（已经是一个字符串 — 不要再次序列化它）。
- [ ] **步骤 3** 使用与步骤 2 相同的 `operationId` 和 `requestSource` 始终为 `"A4V"` 循环调用，直到 `isComplete` 为 `true` 或返回错误 — 不暂停，不要求用户继续，无论迭代次数多少。只有在 `isComplete` 为 `true` 时才从 `result` 中提取 XML。
- [ ] **多流程**：每个流程的完整流程必须按顺序完成后再开始下一个，依次进行（不能并行，不能交错），并且必须生成所有请求的流程 — 不能在第一个后停止。
- [ ] **Canvas 模式（只读）**：基于 Canvas 的新流程的 XML 包含 `<processMetadataValues>` `CanvasMode`=`AUTO_LAYOUT_CANVAS` 条目。如果缺失，则显示流程间隙 — 不要手动编辑（严格的约束条件禁止这样做）。非 Canvas 类型如 `CustomerLifecycle` 不包含任何内容 — 不要标记这些。
