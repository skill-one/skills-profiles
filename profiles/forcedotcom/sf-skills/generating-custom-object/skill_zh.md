## 何时使用此技能

在您需要以下操作时使用此技能：
- 创建新的自定义对象
- 生成自定义对象元数据 XML
- 配置对象共享和安全设置
- 设置对象功能和能力
- 排查与自定义对象相关的部署错误

## 规格

## 1. 概述和目的

本文档定义了生成自定义对象元数据 XML（`.object-meta.xml` 文件）的强制约束。代理必须在输出 XML 之前验证这些约束，以防止元数据 API 部署错误。

**文件扩展名：** `.object-meta.xml`

---

## 2. 语法要点（第一级）

以下约束必须为 XML 正文成功部署为真。

**注意：** API 名称（fullName）**不是**标签；它是文件名（例如，`Vehicle__c.object-meta.xml`）。

### 必要元素

| 元素 | 要求 | 备注 |
|------|-------------|-------|
| `<label>` | 必须有 | 单数 UI 名称 |
| `<pluralLabel>` | 必须有 | 复数 UI 名称 |
| `<sharingModel>` | 必须有 | 见共享模型规则下方 |
| `<deploymentStatus>` | 必须有 | 始终设置为 `Deployed` |
| `<nameField>` | 必须有 | 主要记录标识符（需要 `<label>` 和 `<type>`） |
| `<visibility>` | 必须有 | 始终设置为 `Public` |

### 共享模型规则

**默认值：** 将 `<sharingModel>` 设置为 `ReadWrite`。

**例外：** 如果此对象包含主从关系字段，`<sharingModel>` **必须**是 `ControlledByParent`。

**决策逻辑：**
- 如果对象**没有**主从关系字段 → 使用 `ReadWrite`
- 如果对象**有**主从关系字段 → 使用 `ControlledByParent`
- 如果将主从关系字段添加到现有子对象 → 该现有对象的 `<sharingModel>` 也必须更新为 `ControlledByParent`

**❌ 不正确** — 将导致错误：`Cannot set sharingModel to ReadWrite on a CustomObject with a MasterDetail relationship field`
```xml
<CustomObject xmlns="http://soap.sforce.com/2006/04/metadata">
  <label>Order Line Item</label>
  <pluralLabel>Order Line Items</pluralLabel>
  <sharingModel>ReadWrite</sharingModel>  <!-- 错误：对象有一个 M-D 字段 -->
  <deploymentStatus>Deployed</deploymentStatus>
</CustomObject>
```

**✅ 正确：**
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
|------|-------------|------------------------|
| **Text** | 默认用于人类命名的实体（项目、位置、团队） | 无 |
| **AutoNumber** | 用于交易、日志或 ID（发票、请求、工单） | 必须包含 `<displayFormat>`（例如，`INV-{0000}`）和 `<startingNumber>1</startingNumber>` |

**Text 名称字段示例：**
```xml
<nameField>
  <label>Project Name</label>
  <type>Text</type>
</nameField>
```

**AutoNumber 名称字段示例：**
```xml
<nameField>
  <label>Invoice Number</label>
  <type>AutoNumber</type>
  <displayFormat>INV-{0000}</displayFormat>
  <startingNumber>1</startingNumber>
</nameField>
```

### B. 对象描述

**`<description>`**：强制。每个对象必须包含专业摘要。

如果意图模糊，生成摘要：
> "用于在组织内跟踪和管理 [Intent] 的对象。"

### C. 连接对象命名

如果对象是两个父对象之间的多对多链接，通过组合两个父实体的名称来命名对象，以确保架构保持直观。

**示例：**
- `Position_Candidate__c`（链接职位和候选人）
- `Job_Application__c`（链接工作和申请）

### D. 功能启用（干净 XML）

为保持“干净 XML”，仅在偏离 Salesforce 平台的默认值 `false` 时包含可选标签。

**场景 A：面向用户的对象（应用程序、追踪器、业务实体）**
- 触发器：对象预期用于直接用户交互
- 操作：将 `<enableSearch>`、`<enableReports>`、`<enableActivities>` 和 `<enableHistory>` 设置为 `true`

**场景 B：面向系统的对象（连接对象、后台日志）**
- 触发器：对象用于技术关联或后台数据
- 操作：省略这些标签以保持 UI 清洁和 XML 简洁

---

## 4. 关键约束和常见失败

### 保留字

切勿将保留字用作自定义对象或自定义字段的 API 名称：

| 类别 | 保留字（不可用作 API 名称） |
|------|------------------------------------------|
| SOQL/SQL | `Select`、`From`、`Where`、`Limit`、`Order`、`Group` |
| 系统 | `User`、`External`、`View`、`Type` |
| 时间 | `Date`、`Number` |

### 关系上限

不要为单个对象创建超过 **2 个主从关系**。如果需要第三个关系，请使用查找关系。

### XML 根元素

**不要**在 `.object-meta.xml` 文件的根处包含 `<fullName>` 标签。API 名称由文件名派生。

**❌ 不正确：**
```xml
<CustomObject xmlns="http://soap.sforce.com/2006/04/metadata">
  <fullName>Vehicle__c</fullName>  <!-- 错误：删除此行 -->
  <label>Vehicle</label>
</CustomObject>
```

**✅ 正确：**
```xml
<CustomObject xmlns="http://soap.sforce.com/2006/04/metadata">
  <label>Vehicle</label>
  <!-- fullName 来自文件名：Vehicle__c.object-meta.xml -->
</CustomObject>
```

### 验证规则命名约定

验证规则命名规则与自定义字段不同。

**规则：**
- 必须只包含字母数字字符和下划线
- 必须以字母开头
- 不能以下划线结尾
- 不能包含两个连续的下划线
- **必须**不以 `__c` 结尾（与自定义字段不同）

**❌ 不正确：**
```xml
<validationRules>
  <fullName>Require_Start_Date__c</fullName>  <!-- 错误：有 __c 后缀 -->
  <active>true</active>
  <errorMessage>Start Date is required.</errorMessage>
  <formula>ISBLANK(Start_Date__c)</formula>
</validationRules>
```
**错误：** `The validation name can only contain alphanumeric characters, must begin with a letter, cannot end with an underscore...`

**✅ 正确：**
```xml
<validationRules>
  <fullName>Require_Start_Date</fullName>  <!-- 正确：无 __c 后缀 -->
  <active>true</active>
  <errorMessage>Start Date is required.</errorMessage>
  <formula>ISBLANK(Start_Date__c)</formula>
</validationRules>
```

**命名模式参考：**

| 元数据类型 | 命名模式 | 示例 |
|---------------|----------------|---------|
| 自定义字段 | 以 `__c` 结尾 | `Start_Date__c` |
| 验证规则 | 无后缀 | `Require_Start_Date` |
| 自定义对象 | 以 `__c` 结尾 | `Vehicle__c` |

---

## 5. 验证检查清单

在生成自定义对象 XML 之前，请验证：

### 语法检查
- [ ] 是否同时存在 `<label>` 和 `<pluralLabel>`？
- [ ] `<deploymentStatus>` 是否设置为 `Deployed`？
- [ ] `<visibility>` 是否设置为 `Public`？
- [ ] `<nameField>` 是否包含 `<label>` 和 `<type>`？
- [ ] 如果 `<type>` 是 `AutoNumber`，是否包含 `<displayFormat>` 和 `<startingNumber>`？

### 共享模型检查（关键）
- [ ] 此对象是否有主从关系字段？
    - 如果是 → `<sharingModel>` **必须**是 `ControlledByParent`
    - 如果不是 → `<sharingModel>` 应该是 `ReadWrite`

### 约束检查
- [ ] API 名称是否不包含保留字？
- [ ] 是否有 2 个或更少的主从关系？
- [ ] 是否缺少 `<fullName>`？

### 验证规则检查（如果适用）
- [ ] 验证规则名称是否**不以 `__c` 结尾**？
- [ ] 验证规则名称是否遵循字母数字 + 下划线模式？

### 架构检查
- [ ] 是否存在 `<description>` 并包含有意义的摘要？
- [ ] 如果面向用户，是否将 `<enableSearch>` 和 `<enableReports>` 设置为 `true`？
- [ ] 文件名是否与预期 API 名称匹配？
