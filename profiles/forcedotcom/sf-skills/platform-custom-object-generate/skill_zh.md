## 何时使用此技能

当您需要执行以下操作时，请使用此技能：
- 创建新的自定义对象
- 生成自定义对象元数据 XML
- 配置对象共享和安全设置
- 设置对象功能和能力
- 排查与自定义对象相关的部署错误
- **向现有对象添加、更新或删除字段或验证规则** — 任何这些操作都可能导致对象的 `<description>` 过期，因此您必须刷新它（提议 + 确认）。这同样适用于验证规则更改，而不仅仅是字段。请参阅第 3.B 节。

## 规格

## 1. 概述和目的

本文件定义了生成 CustomObject 元数据 XML（`.object-meta.xml` 文件）的强制性约束。代理必须在输出 XML 之前验证这些约束，以防止 Metadata API 部署错误。

**文件扩展名：** `.object-meta.xml`

> **描述新鲜度 — 适用于所有对象更改，字段和验证规则：** 每当您向对象添加、更新或删除字段 **或** 验证规则时，`<description>` 可能会过期。在完成之前，请根据 **第 3.B 节** 刷新它（提议、与用户确认、写入）。验证规则更改与字段更改完全相同 — 描述只有在协调完成后才算完成。在编辑/删除验证规则时很容易忘记这一点 — 不要。

---

## 2. 语法要点（第一级）

XML 正文要成功部署，必须满足以下约束。

**注意：** API 名称（fullName）不是标签；它是文件名（例如，`Vehicle__c.object-meta.xml`）。

### 必要元素

| 元素 | 要求 | 备注 |
|------|------|------|
| `<label>` | 必须有 | 单数 UI 名称 |
| `<pluralLabel>` | 必须有 | 复数 UI 名称 |
| `<sharingModel>` | 必须有 | 请参阅共享模型规则下方 |
| `<deploymentStatus>` | 必须有 | 始终设置为 `Deployed` |
| `<nameField>` | 必须有 | 主要记录标识符（需要 `<label>` 和 `<type>`） |
| `<visibility>` | 必须有 | 始终设置为 `Public` |

### 共享模型规则

**默认值：** 将 `<sharingModel>` 设置为 `ReadWrite`。

**例外：** 如果此对象包含主从关系字段，`<sharingModel>` 必须为 `ControlledByParent`。

**决策逻辑：**
- 如果对象没有主从关系字段 → 使用 `ReadWrite`
- 如果对象有主从关系字段 → 使用 `ControlledByParent`
- 如果将主从关系字段添加到现有子对象 → 该现有对象的 `<sharingModel>` 也必须更新为 `ControlledByParent`

**不正确** — 将导致错误：`Cannot set sharingModel to ReadWrite on a CustomObject with a MasterDetail relationship field`
```xml
<CustomObject xmlns="http://soap.sforce.com/2006/04/metadata">
  <label>Order Line Item</label>
  <pluralLabel>Order Line Items</pluralLabel>
  <sharingModel>ReadWrite</sharingModel>  <!-- 错误：对象有 M-D 字段 -->
  <deploymentStatus>Deployed</deploymentStatus>
</CustomObject>
```

**正确：**
```xml
<CustomObject xmlns="http://soap.sforce.com/2006/04/metadata">
  <label>Order Line Item</label>
  <pluralLabel>Order Line Items</pluralLabel>
  <sharingModel>ControlledByParent</sharingModel>  <!-- 正确 -->
  <deploymentStatus>Deployed</deploymentStatus>
</CustomObject>
```

---

## 3. 智能默认值和决策逻辑（第二级）

代理必须根据对象预期用例选择要启用的功能。

### A. 名称字段决策

| 类型 | 使用场景 | 额外要求 |
|------|----------|----------|
| **Text** | 默认用于人类命名的实体（项目、位置、团队） | 无 |
| **AutoNumber** | 用于交易、日志或 ID（发票、请求、工单） | 必须包含 `<displayFormat>`（例如，`INV-{0000}`）和 `<startingNumber>1</startingNumber>` |

**Text 名称字段示例：**
```xml
<nameField>
  <label>项目名称</label>
  <type>Text</type>
</nameField>
```

**AutoNumber 名称字段示例：**
```xml
<nameField>
  <label>发票编号</label>
  <type>AutoNumber</type>
  <displayFormat>INV-{0000}</displayFormat>
  <startingNumber>1</startingNumber>
</nameField>
```

### B. 对象描述（丰富化）

**`<description>`**：**必须** — 每个自定义对象都必须有一个。它必须像人类编写的文档一样阅读，**绝不**是通用的模板（“对象用于跟踪和管理...”）或元数据转储（“包含 8 个字段，包括 `Project_Name__c`...”）。

**始终编写丰富的描述** — 在创建对象时，以及在对其**任何**更改时（添加、更新或删除字段**或**验证规则）（因此永远不会过期）。更改 — 字段或验证规则 — 在刷新对象的描述之前**不**算完成。这不是可选的；不要询问**是否**要添加描述。

**每次更改都确认**。在**每次**字段/规则更改时分别提议和确认。之前的“保持当前”仅适用于**该次更改**；它**永远**不是跳过后续更改提议的许可。不要从之前的答案中推断偏好 — 对每个新更改重新提议并重新询问。

**编写**描述（步骤如下）。如果对象已经有一个描述，请将其用作**强烈信号** — 保留它所携带的业务上下文（领域、团队、模式无法揭示的意图）并将新字段/规则合并到其中，而不是丢弃它。

然后根据是否存在描述分支：

- **没有现有描述（全新对象）：** 没有需要覆盖的 — 只需编写编写的描述。**不要提示。**
- **现有描述（更新、删除或任何重新丰富化）：** 永远不要无声地覆盖它 — 您无法从文件中判断它是管理员手动编写的还是之前生成的。显示提议，询问，并**停止 — 等待用户的回复**：
   > 提议的 `{Object}` 描述：
   > `<编写的描述>`
   > 当前：`<现有描述>`
   > 使用此描述？(是 / 保持当前 / 编辑)

  **您必须**在用户回复**之前**编写 `<description>` — 显示差异**不**是批准，即使更改看起来很明显或很小。然后采取行动：*是* → 编写提议的文本 · *保持当前* → 保持现有的一个不变（这仅适用于**此次更改** — 在下一个更改时重新提议） · *编辑* → 使用用户的措辞。

始终以编写的 `<description>` 结尾。

**编写描述的步骤：**

1. **按字段在描述中如何出现进行分类：**
   - **约束**（必需、唯一、外部 ID、限制的 picklist）→ 选择性括号：`VIN (必需，外部 ID)`，`颜色 (仅红色/绿色)`
   - **行为**（公式、汇总）→ 描述它计算的内容：`“年龄年”字段自动计算车辆年龄`
   - **关系**（主从关系、查找）→ 编织上下文：`作为 Account 的子对象`（永远不会是 `(主从关系到 Account)`）
   - **标准** → 仅标签
2. **按此顺序编写**，使用字段**标签**而不是 API 名称：
   > 目的 → 关键字段 → 计算字段 → 验证规则（作为业务规则）→ `“通常用于 {用例}。”`
3. **在写入前计数和修剪（必须）：** 计数字数；目标约为 45，硬上限 50。如果超出，首先收紧措辞，然后按优先级顺序删除整个句子（用例 → 规则 → 计算；从不删除句子 1–2）。重新计数。**不**在 50 字以内**之前**编写。

**示例（汽车，46 个字）：**
```xml
<description>汽车对象跟踪车辆库存和维护。它捕获年份、VIN（必需，外部 ID）、颜色（仅红色/绿色）和位置；年龄年字段自动计算车辆年龄。VIN 是必需的，黑色汽车不能出售。通常用于车队管理、库存跟踪和服务调度。</description>
```
→ 对于完整的工作流程和示例，请阅读 **`references/description-enrichment.md`**。

### C. 连接对象命名

如果对象是两个父对象之间的多对多链接，请通过组合两个父实体来命名对象，以确保模式保持直观。

**示例：**
- `Position_Candidate__c`（链接位置和候选人）
- `Job_Application__c`（链接工作和申请）

### D. 功能启用（干净 XML）

为了保持“干净 XML”，仅在偏离 Salesforce 平台的默认值 `false` 时才包含可选标签。

**场景 A：面向用户的对象（应用程序、跟踪器、业务实体）**
- 触发器：对象旨在直接与用户交互
- 操作：将 `<enableSearch>`、`<enableReports>`、`<enableActivities>` 和 `<enableHistory>` 设置为 `true`

**场景 B：面向系统的对象（连接、后台日志）**
- 触发器：对象存在用于技术关联或后台数据
- 操作：省略这些标签以保持 UI 干净和 XML 精简

---

## 4. 关键约束和常见错误

### 保留字

永远不要将保留字用作自定义对象或自定义字段的 API 名称：

| 类别 | 保留字（不要用作 API 名称） |
|------|-----------------------------|
| SOQL/SQL | `Select`，`From`，`Where`，`Limit`，`Order`，`Group` |
| 系统 | `User`，`External`，`View`，`Type` |
| 时间 | `Date`，`Number` |

### 关系上限

不要为单个对象创建超过 **2 个主从关系**。如果需要第三个关系，请使用查找代替。

### XML 根元素

**不**要在 `.object-meta.xml` 文件的根中包含 `<fullName>` 标签。API 名称是从文件名派生的。

**不正确：**
```xml
<CustomObject xmlns="http://soap.sforce.com/2006/04/metadata">
  <fullName>Vehicle__c</fullName>  <!-- 错误：删除此内容 -->
  <label>Vehicle</label>
</CustomObject>
```

**正确：**
```xml
<CustomObject xmlns="http://soap.sforce.com/2006/04/metadata">
  <label>Vehicle</label>
  <!-- fullName 来自文件名：Vehicle__c.object-meta.xml -->
</CustomObject>
```

### 验证规则命名约定

验证规则的命名规则与自定义字段不同。

**规则：**
- 必须只包含字母数字字符和下划线
- 必须以字母开头
- 不能以下划线结尾
- 不能包含两个连续的下划线
- **必须**不以 `__c` 结尾（与自定义字段不同）

**不正确：**
```xml
<validationRules>
  <fullName>Require_Start_Date__c</fullName>  <!-- 错误：有 __c 后缀 -->
  <active>true</active>
  <errorMessage>Start Date is required.</errorMessage>
  <formula>ISBLANK(Start_Date__c)</formula>
</validationRules>
```
**错误：** `The validation name can only contain alphanumeric characters, must begin with a letter, cannot end with an underscore...`

**正确：**
```xml
<validationRules>
  <fullName>Require_Start_Date</fullName>  <!-- 正确：没有 __c 后缀 -->
  <active>true</active>
  <errorMessage>Start Date is required.</errorMessage>
  <formula>ISBLANK(Start_Date__c)</formula>
</validationRules>
```

**命名模式参考：**

| 元数据类型 | 命名模式 | 示例 |
|------------|----------|------|
| 自定义字段 | 以 `__c` 结尾 | `Start_Date__c` |
| 验证规则 | 无后缀 | `Require_Start_Date` |
| 自定义对象 | 以 `__c` 结尾 | `Vehicle__c` |

---

## 5. 验证检查清单

在生成 Custom Object XML 之前，请验证：

### 语法检查
- [ ] 是否同时存在 `<label>` 和 `<pluralLabel>`？
- [ ] `<deploymentStatus>` 是否设置为 `Deployed`？
- [ ] `<visibility>` 是否设置为 `Public`？
- [ ] `<nameField>` 是否包含 `<label>` 和 `<type>`？
- [ ] 如果 `<type>` 是 `AutoNumber`，是否包含 `<displayFormat>` 和 `<startingNumber>`？

### 共享模型检查（关键）
- [ ] 此对象是否有主从关系字段？
    - 如果是 → `<sharingModel>` 必须为 `ControlledByParent`
    - 如果不是 → `<sharingModel>` 应该是 `ReadWrite`

### 约束检查
- [ ] API 名称是否不包含保留字？
- [ ] 是否有 2 个或更少的主从关系？
- [ ] 是否从 XML 根中省略了 `<fullName>`？

### 验证规则检查（如果适用）
- [ ] 验证规则名称是否不以 `__c` 结尾？
- [ ] 验证规则名称是否遵循字母数字 + 下划线模式？

### 描述丰富化质量检查
- [ ] 以 `“{Object} 对象...” + 业务目的开头（不是“对象用于跟踪和管理...”）`
- [ ] 使用字段**标签**，绝不使用 API 名称；不转储“包含 N 个字段，包括 `Project_Name__c`...”
- [ ] 描述公式/汇总的行为；验证规则作为业务规则陈述；关系作为上下文
- [ ] 包括常见用例（“通常用于...”）并且**少于 50 个字**
- [ ] 将现有描述的业务上下文合并到提议中（没有丢弃它）
- [ ] 对于现有描述（更新/删除/重新丰富化），在写入之前**停止并等待用户的回复** — 不将显示差异视为批准

### 架构检查
- [ ] 是否存在 `<description>`？（根据第 B 节进行丰富化 — 在写入之前与用户提议和确认。）
- [ ] 如果面向用户，`<enableSearch>` 和 `<enableReports>` 是否设置为 `true`？
- [ ] 文件名是否与预期 API 名称匹配？

---

## 参考文件索引

| 文件 | 何时阅读 |
|------|----------|
| `references/description-enrichment.md` | 编写或刷新对象的 `<description>`（在创建时，或在字段/规则更改时）— 完整的丰富化工作流程、字段优先级级别、连接/子对象处理、边缘案例和更多示例 |
