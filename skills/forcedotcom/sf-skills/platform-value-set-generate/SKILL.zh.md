---
name: platform-value-set-generate
description: 用于创建、生成或验证 Salesforce GlobalValueSet（跨字段共享的可重用选择列表）或自定义 StandardValueSet（内置选择列表，如行业、潜在客户来源、机会阶段）。在全局/标准值集、可重用选择列表、.globalValueSet-meta.xml 或 .standardValueSet-meta.xml 上触发，或在向标准选择列表添加值时出现部署错误时触发。对于单个字段上的非重用一次性内联选择列表，请勿触发——使用 platform-custom-field-generate。
---

## 概述

生成并验证两种可重用的 picklist 值集元数据类型——**GlobalValueSet**（一个跨字段共享的新可重用集）和**StandardValueSet**（自定义内置目录 picklist，如行业或潜在客户来源）——并通过 `<valueSetName>` 将 CustomField 连接到其中一个。

### 范围

- **在范围内：** 创建 GlobalValueSet、自定义 StandardValueSet、从字段引用它们以及相关的部署错误。
- **超出范围：** 单个字段上的一次性内联 picklist 无需重用 → 使用 **`platform-custom-field-generate`**（内联 `<valueSetDefinition>`）。引用值集的 *字段* 生成是 `platform-custom-field-generate` 的工作；这项技能生成的是值集本身。

**两种不同的元数据类型——不要混淆它们：**

| 关注点 | GlobalValueSet | StandardValueSet |
|---------|----------------|------------------|
| 文件夹 | `globalValueSets/` | `standardValueSets/` |
| 文件后缀 | `.globalValueSet-meta.xml` | `.standardValueSet-meta.xml` |
| 根元素 | `<GlobalValueSet>` | `<StandardValueSet>` |
| 名称来源 | 文件名（开发名称） | `<fullName>` = 固定目录名称 |
| 值元素 | `<customValue>` | `<standardValue>` |
| 能否添加新值？ | 是 | 否 — 仅修改现有值 |
| 能否创建新名称？ | 是 | 否 — 仅使用固定目录 |
| `*` 通配符在 `package.xml` 中 | 支持 | 不支持 |

---

## 规格

### 1. 目的

本文档定义了生成值集元数据 XML 的强制性约束。代理必须在输出 XML 之前验证这些约束，以防止 Metadata API 部署错误。

- **GlobalValueSet** — 一个可重用、命名的 picklist 值集，定义一次并由任意数量的 picklist/多选字段引用。当同一值列表在多个字段之间共享时使用。
- **StandardValueSet** — Salesforce 定义的标准 picklist（行业、潜在客户来源等）背后的值列表。你只能 **修改** 固定目录中命名字集的值；你不能创建新的集合或添加全新的值。

---

### 2. GlobalValueSet — 语法要点

**文件：** `globalValueSets/<DeveloperName>.globalValueSet-meta.xml`

开发名称来自 **文件名**，而不是 `<fullName>` 标签。

#### 必要元素

| 元素 | 要求 | 备注 |
|---------|-------------|-------|
| `<masterLabel>` | 必须有 | 值集的 UI 标签 |
| `<sorted>` | 必须有 | `true` = 在 UI 中按字母顺序排列值；`false` = 保持列表顺序 |
| `<customValue>` | 必须有（≥1） | 每个值一个（见下文） |

#### `<customValue>` 子元素

| 子元素 | 要求 | 备注 |
|-------------|-------------|-------|
| `<fullName>` | 必须有 | 值的 API 名称。使用值文本 **作为用户拼写的方式** — 允许空格并必须保留（例如 `Closed Won`，而不是 `Closed_Won`）。必须以字母开头。这是一个值名称，不是字段 API 名称，因此不要追加 `__c` 或用下划线替换空格。 |
| `<default>` | 可选 | 至多一个值 `true`。在其他值上省略它（或使用 `false`）—— 它不是每个值都必须有的。 |
| `<label>` | 必须有 | 值的 UI 标签 |
| `<color>` | 可选 | 十六进制颜色，例如 `#FF0000` |
| `<isActive>` | 可选 | 省略（激活）或 `false` 以停用 |
| `<description>` | 可选 | 每个值的描述 |

#### `__gvs` 后缀 — 不要在元数据中使用它

**规则：通过其纯开发名称引用 GlobalValueSet。永远不要添加 `__gvs`。**

在 API 57.0+ 组织中，平台 *内部存储/显示* GlobalValueSet 的开发名称带有 `__gvs` 后缀，但 **Metadata API（部署和检索）始终使用纯名称** — `<valueSetName>Priority_Levels</valueSetName>`，而不是 `Priority_Levels__gvs`。后缀是 Winter '23 变更中短暂发出的，导致部署失败，并且已被修复。因此：

- 文件是 `globalValueSets/Priority_Levels.globalValueSet-meta.xml` — **文件名中没有 `__gvs`**。
- 字段引用它作为 `<valueSetName>Priority_Levels</valueSetName>` — **没有 `__gvs`**。
- 如果检索显示组织中为 `Priority_Levels__gvs`，或者你看到“已从组织中检索但未在本地项目中找到”的警告，那是预期的组织存储显示 — 保持你的本地元数据为纯名称。

#### 正确的 — GlobalValueSet

```xml
<?xml version="1.0" encoding="UTF-8"?>
<GlobalValueSet xmlns="http://soap.sforce.com/2006/04/metadata">
    <masterLabel>Priority Levels</masterLabel>
    <sorted>false</sorted>
    <customValue>
        <fullName>Critical</fullName>
        <default>false</default>
        <label>Critical</label>
    </customValue>
    <customValue>
        <fullName>High</fullName>
        <default>false</default>
        <label>High</label>
    </customValue>
    <customValue>
        <fullName>Medium</fullName>
        <default>true</default>
        <label>Medium</label>
    </customValue>
    <customValue>
        <fullName>Low</fullName>
        <default>false</default>
        <label>Low</label>
    </customValue>
</GlobalValueSet>
```

#### 错误的 — GlobalValueSet

```xml
<GlobalValueSet xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>Priority_Levels</fullName>      <!-- 错误：名称来自文件名 -->
    <masterLabel>Priority Levels</masterLabel>
    <!-- 错误：<sorted> 是必需的，但缺失 -->
    <standardValue>                            <!-- 错误：GVS 使用 <customValue>，不使用 <standardValue> -->
        <fullName>Critical</fullName>
    </standardValue>
</GlobalValueSet>
```

**错误：** 缺少必要的 `sorted`；未知元素 `standardValue`；根 `fullName` 被拒绝，因为名称来自文件名。

---

### 3. StandardValueSet — 语法要点 关键

**文件：** `standardValueSets/<Name>.standardValueSet-meta.xml`

#### 严格约束 — 生成前阅读

1. **你只能修改固定目录中命名的标准值集内的值。** 你 **不能** 添加全新的值，并且你 **不能** 创建新的 StandardValueSet 名称。Metadata API 将拒绝两者。
2. 根元素带有 `<fullName>`，其值是 **固定枚举名称**（例如 `Industry`），**不是** `masterLabel`。文件名必须匹配此名称。
3. 值是 `<standardValue>` 条目 — **不是** `<customValue>`。
4. **仅输出请求明确命名的值 — 进行外科手术式、最小化更改。** 为用户要求激活、停用、重命名或重新排序的每个值包含一个 `<standardValue>` 块，并且 **什么也不多**。**不要** 列出整个 picklist 或为请求未提及的值发出 `<standardValue>` 条目。StandardValueSet 部署是部分更新：未列出的值保持其当前组织状态不变。重新生成每个值（例如所有 30 多个行业条目）是噪音，并可能破坏组织状态 — 即使请求说“仅保持 X 激活”，这也意味着“设置命名的值；保持其他值不变”，而不是“枚举并停用所有其他值”。如果你使用 grounding MCP 发现现有值，仅用于确认命名的值存在并获取其确切的 `<fullName>`/`<label>` — 不要作为完整列表来重新生成。

#### `<standardValue>` — 可修改的子元素

| 子元素 | 可修改？ | 备注 |
|-------------|-------------|-------|
| `<fullName>` | 识别值（必须已存在） | 不能引入新值 |
| `<label>` | 是 | 重命名值的 UI 文本 |
| `<isActive>` | 是 | `false` 停用；省略或 `true` 保持激活 |
| `<default>` | 是 | 至多一个值 `true` |
| `<groupingString>` | 是 | 分类分组（某些标准 picklist 使用） |

#### 标准的 StandardValueSet 名称（部分）

`Industry`、`LeadSource`、`OpportunityStage`、`OpportunityType`、`AccountType`、`AccountRating`、`LeadStatus`、`CaseStatus`、`CaseOrigin`、`CasePriority`、`CaseReason`、`TaskStatus`、`TaskPriority`、`QuoteStatus`、`Product2Family`、`Salutation`、`AccountOwnership`、`ContractStatus`、`OrderStatus`、`PartnerRole`。

> 完整附录：有效的标准值集名称的完整列表位于
> `https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/standardvalueset_names.htm`。
> 如果名称不在该附录中，它**不是** StandardValueSet — 要么是 GlobalValueSet，要么是内联 CustomField picklist。

#### 正确的 — StandardValueSet（仅修改现有值）

```xml
<?xml version="0.9" encoding="UTF-8"?>
<StandardValueSet xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>Industry</fullName>
    <standardValue>
        <fullName>Technology</fullName>
        <default>false</default>
        <label>Technology</label>
        <isActive>true</isActive>
    </standardValue>
    <standardValue>
        <fullName>Agriculture</fullName>
        <default>false</default>
        <label>Agriculture</label>
        <isActive>false</isActive>   <!-- 停用，但保留在集中 -->
    </standardValue>
</StandardValueSet>
```

#### 错误的 — StandardValueSet

```xml
<StandardValueSet xmlns="http://soap.sforce.com/2006/04/metadata">
    <masterLabel>Industry</masterLabel>     <!-- 错误：StandardValueSet 使用 <fullName>，不使用 masterLabel -->
    <customValue>                           <!-- 错误：使用 <standardValue>，不使用 customValue -->
        <fullName>Renewable Energy</fullName> <!-- 错误：不能向标准集添加新值 -->
        <label>Renewable Energy</label>
    </customValue>
</StandardValueSet>
```

**错误：** 未知元素 `masterLabel`/`customValue`；向标准集添加新值导致部署失败。

---

### 4. 永远不要凭空创造值 — 验证，不要幻觉 关键

在自定义 **StandardValueSet**（或扩展共享的 GlobalValueSet）时，**仅修改已存在的值** — 永远不要凭空创造标准 picklist 的值列表。硬性规则是关于你 **输出** 的内容：`<standardValue>` 的 `<fullName>` 如果不是真实的目录值，将导致部署失败。

对于众所周知的标准 picklist，你已经知道规范值（例如 `Industry`、`LeadSource`、`OpportunityStage`）。当你不确定命名的值是否存在时，可以针对实时组织进行确认 — 但将查找视为一个 *确认* 步骤，而不是必需的首次调用：

- **Grounding MCP**（如果可用）通过 `search_metadata` 和 `query_metadata` 暴露查找实时元数据。仅用于确认命名值的精确 `<fullName>`/`<label>` — 不要用来拉取完整列表以重新生成。
- **CLI 降级** — 直接查询 Tooling API：

```bash
sf data query --use-tooling-api \
  --query "SELECT MasterLabel, Metadata FROM StandardValueSet WHERE MasterLabel = '<name>'"
```

> **重点是输出，不是查找：** 仅输出修改到你知道存在的值。一个生成 StandardValueSet 引入未见过的值是幻觉，并且将导致部署失败。（这与 §3 中的最小范围规则配对：确认命名的值；不要枚举整个集。）

---

### 5. 从 CustomField 引用值集

picklist/多选 CustomField 通过 `<valueSetName>` 在 `<valueSet>` 内部引用值集（而不是内联 `<valueSetDefinition>`）。

```xml
<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>Priority__c</fullName>
    <label>Priority</label>
    <type>Picklist</type>
    <valueSet>
        <restricted>true</restricted>
        <valueSetName>Priority_Levels</valueSetName>  <!-- 纯开发名称，NO __gvs；见 §2 -->
    </valueSet>
</CustomField>
```

- 对于 **GlobalValueSet**，`<valueSetName>` 是 **纯开发名称**（例如 `Priority_Levels`）— **永远** 不要添加 `__gvs`。后缀是组织存储显示的存储副产物；Metadata API 在部署和检索时始终使用纯名称（见 §2）。
- 绑定到值集的字段必须 **不** 也声明内联 `<valueSetDefinition>` — 选择其一。

---

### 6. 验证规则

代理必须 **拒绝** 并解释 — 不要无声地“修复”并凭空创造元数据 — 以下内容：

| 违规 | 操作 / 消息 |
|-----------|------------------|
| 向 **StandardValueSet** 添加新值 | 拒绝。 "标准值集不能接受新值。创建可重用的 **GlobalValueSet** 或 **CustomField** 上的内联 picklist 代替。" |
| 创建新的 StandardValueSet 名称 | 拒绝。名称必须在标准目录附录中。否则它是 GlobalValueSet。 |
| **值集开发名称** 带有空格 / 无效字符 | 将空格转换为下划线；必须以字母开头；字母数字 + 下划线。 `Priority Levels` → `Priority_Levels`。（这适用于值集名称和字段 API 名称 — **不**适用于单个 `<customValue><fullName>` 值，后者保留空格。） |
| 一个集中重复的值 `fullName` | 拒绝。每个 `fullName` 在值集中必须唯一。 |
| 超过一个 `<default>true</default>` | 拒绝。每个集中最多一个默认值。 |

#### 错误的 — 向标准集添加值

> "向行业 picklist 添加一个 `Cryptocurrency` 值。"

不要发出带有 `fullName` `Cryptocurrency` 的 `<standardValue>`。回复标准值集是固定目录，建议使用 GlobalValueSet（如果跨字段重用）或单个 CustomField 上的内联限制 picklist。

---

### 7. 部署顺序

值集必须在引用它的任何 CustomField **之前** 部署。

- 首先部署 `GlobalValueSet` / `StandardValueSet`，然后部署 CustomField，其 `<valueSetName>` 指向它。
- 引用不存在值集的字段会失败，报 `valueSetName ... does not exist`（或“未找到”错误）。
- 在 `package.xml` 中：`GlobalValueSet` **支持** `*` 通配符；`StandardValueSet` **不支持** — 明确列出每个标准集成员。

---

### 8. 常见部署错误

| 错误 / 症状 | 原因 | 修复 |
|-----------------|-------|-----|
| 值未添加到标准 picklist | 尝试向 `StandardValueSet` 添加值 | 标准集是固定的；使用 GlobalValueSet 或内联 CustomField picklist |
| `Required field missing: sorted` | GlobalValueSet 缺少 `<sorted>` | 添加 `<sorted>true</sorted>` 或 `<sorted>false</sorted>` |
| 未知元素 `masterLabel`（StandardValueSet） | 使用 `masterLabel` 而不是 `fullName` | StandardValueSet 根使用 `<fullName>` = 目录名称 |
| 未知元素 `customValue`（StandardValueSet） | 使用 `customValue` 而不是 `standardValue` | 在标准集中使用 `<standardValue>` |
| `valueSetName ... does not exist` | 字段部署在值集之前，或错误添加了 `__gvs` 到引用 | 首先部署值集；使用 **纯** 开发名称，**无** `__gvs`（§2） |
| 重复值名称 | 两个 `<customValue>` 条目共享 `fullName` | 使每个 `fullName` 在集中唯一（值名称中的空格是允许的 — 不要将它们下划线化） |

---

## 验证清单

在生成值集 XML 之前，验证：

### 类型选择
- [ ] 这是一个跨字段共享的可重用集（GlobalValueSet）还是一个内置标准 picklist（StandardValueSet）？
- [ ] 如果 StandardValueSet：名称在标准目录附录中吗？如果不是，必须是 GlobalValueSet 或内联 picklist。

### GlobalValueSet 检查
- [ ] 根是 `<GlobalValueSet>`，命名空间为 `http://soap.sforce.com/2006/04/metadata` 吗？
- [ ] `<masterLabel>` 存在吗？
- [ ] `<sorted>` 存在吗（`true` 或 `false`）？
- [ ] 至少有一个 `<customValue>`，每个都有 `<fullName>` 和 `<label>`（最多一个带有 `<default>true</default>`）吗？
- [ ] 根部没有 `<fullName>`（名称来自文件名）吗？
- [ ] 从字段引用时，`<valueSetName>` 是 **纯** 开发名称，**无** `__gvs` 后缀吗？

### StandardValueSet 检查 CRITICAL
- [ ] 你是否仅修改你确知存在的值（已从已知标准目录中确认，或通过 `search_metadata`/`query_metadata` / 工具 API 进行接地确认，如果不确定）——从不编造新值？
- [ ] 根 `<StandardValueSet>` 是否具有正确的命名空间？
- [ ] 根是否使用 `<fullName>` 设置为固定的目录名称（不是 `masterLabel`）？
- [ ] 值是否为 `<standardValue>` 条目（不是 `customValue`）？
- [ ] 你是否仅修改已存在的值（没有新的 `fullName`）？
- [ ] 你是否避免了添加一个全新的值或一个新的集合名称？

### 共享检查
- [ ] 最多只有一个值具有 `<default>true</default>`？
- [ ] 所有的值 `fullName` 在集合内是否唯一？（值名称中的空格是允许的——按原样保留；只有值-集开发者名称和字段 API 名称使用下划线。）
- [ ] 值集是否在引用它的任何 CustomField 之前部署？
- [ ] 文件名是否与预期名称匹配？
