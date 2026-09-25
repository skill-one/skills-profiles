## 何时使用此技能

当你需要执行以下操作时，请使用此技能：
- 在任何对象上创建自定义字段
- 为任何字段类型生成字段元数据
- 设置关系字段（查找或主从）
- 创建公式或汇总摘要字段
- 排查与自定义字段相关的部署错误

# Salesforce 自定义字段生成器和验证器

## 概述

使用此技能生成和验证 Salesforce 自定义字段元数据，以防止部署错误。此技能特别关注**失败率最高的字段类型**：汇总摘要和主从关系。

## 规格

## 1. 目的

本文档定义了生成 CustomField 元数据 XML 的强制性约束。代理必须在输出 XML 之前验证这些约束，以防止 Metadata API 部署错误。

**重点关注区域：**
- 汇总摘要字段格式错误
- 主从字段属性限制
- 查找过滤器限制

---

## 2. 通用强制性属性

每个生成的字段都必须包含以下标签：

| 属性       | 要求   | 备注 |
|------------|--------|------|
| `<fullName>` | 必须包含 | 从 `<label>` 派生：每个单词大写，用下划线替换空格，追加 `__c`。必须以字母开头。例如，标签 `Total Contract Value` → `Total_Contract_Value__c` |
| `<label>`   | 必须包含 | UI 名称（首字母大写） |
| `<description>` | 必须包含 | 说明字段背后的业务“原因” |
| `<inlineHelpText>` | 必须包含 | 为最终用户提供可操作的指导。必须比标签更有价值（例如，“以美元（含税）输入值”而不是“金额”） |

### 外部 ID 配置

**触发条件：** 如果用户提到“集成”、“导入数据”、“外部系统 ID”或“来自 [系统名称] 的唯一键”，则设置 `<externalId>true</externalId>`。

**适用类型：** 文本、数字、电子邮件

---

## 3. 技术交互：精度、规模和长度

为确保部署成功，请遵循以下数学约束：

### 精度与规模规则

- `precision` 是总位数；`scale` 是小数位数
- **规则：** `precision ≤ 18` AND `scale ≤ precision`
- **计算：** 小数点左侧的位数 = `precision - scale`

### “固定 255”规则

对于标准 TextArea 类型，Metadata API 要求 `<length>255</length>`，即使它不在 UI 中可配置。

### 可见行数

对于长/富文本和多选列表，用于控制 UI 高度。

---

## 4. 字段数据类型

### 4.1 简单属性类型

| 类型         | `<type>` 值   | 必须包含的属性 |
|--------------|----------------|----------------|
| 自动编号     | `AutoNumber`   | `displayFormat`（必须包含 `{0}`）、`startingNumber` |
| 复选框       | `Checkbox`     | 默认 `defaultValue` 为 `false` |
| 日期         | `Date`         | 无需精度/长度要求 |
| 日期/时间     | `DateTime`     | 无需精度/长度要求 |
| 电子邮件     | `Email`        | 内置格式验证   |
| 查找关系     | `Lookup`       | `referenceTo`、`relationshipName`、`deleteConstraint` |
| 主从关系     | `MasterDetail` | `referenceTo`、`relationshipName`、`relationshipOrder` |
| 数字         | `Number`       | `precision`、`scale` |
| 货币         | `Currency`     | 默认精度：18，规模：2 |
| 百分比       | `Percent`      | 默认精度：5，规模：2 |
| 电话         | `Phone`        | 标准化电话号码格式 |
| 列表         | `Picklist`     | `valueSet` 包含 `valueSetDefinition` 和 `restricted` |
| 文本         | `Text`         | `length`（最大 255） |
| 文本区域     | `TextArea`     | `<length>255</length>` |
| 文本（长）   | `LongTextArea` | `length`、`visibleLines`（默认 3） |
| 文本（富）   | `Html`         | `length`、`visibleLines`（默认 25） |
| 时间         | `Time`         | 仅存储时间（不存储日期） |
| URL          | `Url`          | 验证协议和格式 |

### 4.2 计算和多值类型

| 类型         | `<type>` 值   | 必须包含的属性 |
|--------------|----------------|----------------|
| 公式         | 结果类型（例如，`Number`） | `formula`、`formulaTreatBlanksAs` |
| 汇总摘要     | `Summary`      | 见第 6 节的完整要求 |
| 多选列表     | `MultiselectPicklist` | `valueSet`、`visibleLines`（默认 4） |

### 4.3 特殊类型

| 类型         | `<type>` 值   | 必须包含的属性 |
|--------------|----------------|----------------|
| 地理位置信息 | `Location`     | `scale`、`displayLocationInDecimal` |

### 列表 `<restricted>` 规则

`<restricted>` 布尔值位于 `<valueSet>` 内部，控制是否仅允许管理员定义的值。

- 如果用户未指定 → 默认为 `<restricted>true</restricted>`（受限，避免大型列表值集的性能问题）
- 如果用户明确表示列表应允许自定义/新值，或提到“无限制”或“开放” → 设置 `<restricted>false</restricted>`
- 受限列表最多 1,000 个总值（活动 + 非活动）

```xml
<valueSet>
  <restricted>true</restricted>
  <valueSetDefinition>
    <sorted>false</sorted>
    <value>
      <fullName>Option_A</fullName>
      <default>false</default>
      <label>Option A</label>
    </value>
  </valueSetDefinition>
</valueSet>
```

---

## 5. 主从关系规则 ⭐ CRITICAL

主从字段具有**严格的属性限制**，与查找字段不同。违反这些规则会导致部署失败。

### 主从字段上的禁止属性

**绝对不要在主从字段上包含以下属性：**

| 禁止属性         | 原因   | 结果   |
|------------------|--------|--------|
| `<required>`     | 主从字段按设计总是必需的 | 部署错误 |
| `<deleteConstraint>` | 主从字段总是级联删除 | 部署错误 |
| `<lookupFilter>` | 仅支持在查找字段上 | 部署错误 |

### 主从与查找比较

| 属性             | 主从       | 查找     |
|------------------|------------|----------|
| `<required>`     | ❌ 禁止     | ✅ 可选   |
| `<deleteConstraint>` | ❌ 禁止（总是级联） | ✅ 需要 (`SetNull`、`Restrict`、`Cascade`) |
| `<lookupFilter>` | ❌ 禁止     | ✅ 可选   |
| `<relationshipOrder>` | ✅ 需要（0 或 1） | ❌ 不适用 |
| `<reparentableMasterDetail>` | ✅ 可选     | ❌ 不适用 |
| `<writeRequiresMasterRead>` | ✅ 可选     | ❌ 不适用 |

### ❌ 不正确 — 主从字段与禁止属性：

```xml
<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
  <fullName>Account__c</fullName>
  <label>Account</label>
  <type>MasterDetail</type>
  <referenceTo>Account</referenceTo>
  <relationshipName>Contacts</relationshipName>
  <relationshipOrder>0</relationshipOrder>
  <required>true</required>           <!-- 错误：移除这个 -->
  <deleteConstraint>Cascade</deleteConstraint>  <!-- 错误：移除这个 -->
  <lookupFilter>                       <!-- 错误：移除整个块 -->
    <active>true</active>
    <filterItems>
      <field>Account.Type</field>
      <operation>equals</operation>
      <value>Customer</value>
    </filterItems>
  </lookupFilter>
</CustomField>
```

**错误：**
- `主从关系字段不能是可选或必需的`
- `不能为类型为 MasterDetail 的 CustomField 指定 'deleteConstraint'`
- `查找过滤器仅支持在查找关系字段上`

### ✅ 正确 — 主从字段：

```xml
<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
  <fullName>Account__c</fullName>
  <label>Account</label>
  <description>将此记录链接到其父 Account</description>
  <type>MasterDetail</type>
  <referenceTo>Account</referenceTo>
  <relationshipLabel>子记录</relationshipLabel>
  <relationshipName>ChildRecords</relationshipName>
  <relationshipOrder>0</relationshipOrder>
  <reparentableMasterDetail>false</reparentableMasterDetail>
  <writeRequiresMasterRead>false</writeRequiresMasterRead>
  <!-- 无 required、deleteConstraint 或 lookupFilter -->
</CustomField>
```

### ✅ 正确 — 查找字段（带可选属性）：

```xml
<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
  <fullName>Related_Account__c</fullName>
  <label>Related Account</label>
  <description>可选链接到相关 Account</description>
  <type>Lookup</type>
  <referenceTo>Account</referenceTo>
  <relationshipLabel>相关记录</relationshipLabel>
  <relationshipName>RelatedRecords</relationshipName>
  <required>false</required>
  <deleteConstraint>SetNull</deleteConstraint>
  <lookupFilter>
    <active>true</active>
    <filterItems>
      <field>Account.Type</field>
      <operation>equals</operation>
      <value>Customer</value>
    </filterItems>
    <isOptional>false</isOptional>
  </lookupFilter>
</CustomField>
```

### 其他主从规则

- **关系顺序：** 对象上的第一个主从字段 = `0`，第二个 = `1`
- **关系名称：** 必须是复数帕斯卡命名法字符串（例如，`Travel_Bookings`）
- **连接对象：** 使用两个主从字段创建标准多对多（启用汇总）
- **限制：** 每个对象最多 2 个主从关系。使用查找创建其他关系。

---

## 6. 汇总摘要字段规则 ⭐ CRITICAL

汇总摘要字段具有**最高的部署失败率**。请严格遵循以下规则。

### 汇总摘要的必需元素

| 元素             | 要求   | 格式   |
|------------------|--------|--------|
| `<type>`         | 必须包含 | 总是 `Summary` |
| `<summaryOperation>` | 必须包含 | `count`、`sum`、`min` 或 `max` |
| `<summaryForeignKey>` | 必须包含 | `ChildObject__c.MasterDetailField__c` |
| `<summarizedField>` | 条件性 | 对于 `sum`、`min`、`max` 需要。`count` 不需要 |

### 汇总摘要上的禁止元素

**绝对不要在汇总摘要字段上包含以下属性：**

| 禁止属性         | 原因   |
|------------------|--------|
| `<precision>`     | 汇总摘要继承自汇总字段 |
| `<scale>`         | 汇总摘要继承自汇总字段 |
| `<required>`     | 不适用于汇总字段 |
| `<length>`        | 不适用于汇总字段 |

### summaryForeignKey 和 summarizedField 的格式规则

**关键：** `summaryForeignKey` 和 `summarizedField` 必须使用完全限定格式：

```
ChildObjectAPIName__c.FieldAPIName__c
```

**决策逻辑：**
- `summaryForeignKey` = `ChildObject__c.MasterDetailFieldOnChild__c`
- `summarizedField` = `ChildObject__c.FieldToSummarize__c`

### ❌ 不正确 — 汇总摘要常见错误：

```xml
<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
  <fullName>Total_Amount__c</fullName>
  <label>Total Amount</label>
  <type>Summary</type>
  <precision>18</precision>           <!-- 错误：移除 - 继承自源字段 -->
  <scale>2</scale>                    <!-- 错误：移除 - 继承自源字段 -->
  <summaryOperation>sum</summaryOperation>
  <summaryForeignKey>Order__c</summaryForeignKey>        <!-- 错误：缺少字段名 -->
  <summarizedField>Amount__c</summarizedField>           <!-- 错误：缺少对象名 -->
</CustomField>
```

**错误：**
- `不能为类型为 Summary 的 CustomField 指定 'precision'`
- `必须指定 CustomObject.CustomField 格式的名称（例如 Account.MyNewCustomField）`

### ✅ 正确 — 汇总摘要（SUM 操作）：

```xml
<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
  <fullName>Total_Amount__c</fullName>
  <label>Total Amount</label>
  <description>所有行项目金额的总和</description>
  <inlineHelpText>自动从子行项目计算</inlineHelpText>
  <type>Summary</type>
  <summaryOperation>sum</summaryOperation>
  <summarizedField>Order_Line_Item__c.Amount__c</summarizedField>
  <summaryForeignKey>Order_Line_Item__c.Order__c</summaryForeignKey>
  <!-- 无 precision、scale、required 或 length -->
</CustomField>
```

### ✅ 正确 — 汇总摘要（COUNT 操作）：

```xml
<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
  <fullName>Line_Item_Count__c</fullName>
  <label>Line Item Count</label>
  <description>相关行项目的数量</description>
  <inlineHelpText>自动从子记录计算</inlineHelpText>
  <type>Summary</type>
  <summaryOperation>count</summaryOperation>
  <summaryForeignKey>Order_Line_Item__c.Order__c</summaryForeignKey>
  <!-- 无 summarizedField 需要（对于 COUNT） -->
  <!-- 无 precision、scale、required 或 length -->
</CustomField>
```

### ✅ 正确 — 汇总摘要（MIN 操作）：

```xml
<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
  <fullName>Earliest_Due_Date__c</fullName>
  <label>Earliest Due Date</label>
  <description>所有行项目中最早的到期日期</description>
  <inlineHelpText>显示最早的截止日期</inlineHelpText>
  <type>Summary</type>
  <summaryOperation>min</summaryOperation>
  <summarizedField>Order_Line_Item__c.Due_Date__c</summarizedField>
  <summaryForeignKey>Order_Line_Item__c.Order__c</summaryForeignKey>
</CustomField>
```

### ✅ 正确 — 汇总摘要（MAX 操作）：

```xml
<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
  <fullName>Highest_Price__c</fullName>
  <label>Highest Price</label>
  <description>所有行项目中的最高单价</description>
  <inlineHelpText>显示最昂贵的商品</inlineHelpText>
  <type>Summary</type>
  <summaryOperation>max</summaryOperation>
  <summarizedField>Order_Line_Item__c.Unit_Price__c</summarizedField>
  <summaryForeignKey>Order_Line_Item__c.Order__c</summaryForeignKey>
</CustomField>
```

### 汇总摘要快速参考

| 操作   | summarizedField 需要？ | 用例   |
|--------|-----------------------|--------|
| `count` | 否                     | 计算子记录数量 |
| `sum`   | 是                     | 汇总数值 |
| `min`   | 是                     | 找到最小值 |
| `max`   | 是                     | 找到最大值 |

### 汇总摘要前提条件

- 汇总摘要字段只能创建在**父对象**上，该对象在主从关系中
- 子对象必须有一个指向此父对象的主从字段
- 汇总字段必须存在于子对象上

---

## 7. 公式字段规则

### 公式结果类型

公式本身不是类型。`<formula>` 标签添加到字段上，其 `<type>` 设置为**结果数据类型**：
- `Checkbox`、`Currency`、`Date`、`DateTime`、`Number`、`Percent`、`Text`

### 公式 XML 生成规则

- `<formula>` 标签的内容必须用 `<![CDATA[ ... ]]>` 部分包裹。这可以防止 XML 解析器将公式运算符（如 `&`、`<`、`>`）解释为 XML 标记。
- 如果公式文本本身包含字面序列 `]]>`，则通过拆分 CDATA 块来转义：例如，`<![CDATA[Text_Field__c & "]]]]><![CDATA[>"]]>`
- **绝对不要**使用名为 `returnType` 的属性或标签。这在 Metadata API 中不存在。`<type>` 标签定义公式结果的数据类型。

### formulaTreatBlanksAs 规则

**决策逻辑：**
- 如果公式结果类型 = `Number`、`Currency` 或 `Percent` → 设置 `<formulaTreatBlanksAs>BlankAsZero</formulaTreatBlanksAs>`
- 如果公式结果类型 = `Text`、`Date` 或 `DateTime` → 设置 `<formulaTreatBlanksAs>BlankAsBlank</formulaTreatBlanksAs>`

### ❌ 不正确 — 使用公式作为类型：

```xml
<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
  <fullName>Calculated_Value__c</fullName>
  <type>Formula</type>  <!-- 错误：公式不是有效类型 -->
  <returnType>Number</returnType>  <!-- 错误：returnType 在 Metadata API 中不存在 -->
  <formula>Field1__c + Field2__c</formula>  <!-- 错误：缺少 CDATA 包裹 -->
</CustomField>
```

### ✅ 正确 — 公式字段：

```xml
<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
  <fullName>Calculated_Value__c</fullName>
  <label>Calculated Value</label>
  <description>Field1 和 Field2 的总和</description>
  <type>Number</type>  <!-- 结果类型，不是 "Formula" -->
  <precision>18</precision>
  <scale>2</scale>
  <formula><![CDATA[Field1__c + Field2__c]]></formula>
  <formulaTreatBlanksAs>BlankAsZero</formulaTreatBlanksAs>
</CustomField>
```

### 公式字段依赖关系

引用其他字段的公式字段，如果被引用字段不存在或尚未部署，则部署会失败。确保所有引用字段在公式字段之前部署。

### 特定函数指南

| 函数   | 规则   |
|--------|--------|
| `TEXT()` | **绝对不要**与文本字段一起使用。如果字段已经是文本，则移除 `TEXT()` 包装器。 |
| `CASE()` | 最后一个参数始终是默认值。参数总数必须是偶数（值-结果对 + 默认值）。 |
| `VALUE()` | **仅**用于文本字段。如果传递了数字参数，则移除 `VALUE()` 包装器。 |
| `DAY()` | **仅**用于日期字段。如果使用日期时间字段，则先将其转换为日期（例如，`DAY(DATEVALUE(DateTimeField__c))`）。 |
| `MONTH()` | **仅**用于日期字段。如果使用日期时间字段，则先将其转换为日期（例如，`MONTH(DATEVALUE(DateTimeField__c))`）。 |
| `DATEVALUE()` | **仅**用于日期时间字段。如果使用日期字段，则移除 `DATEVALUE()` 包装器。 |
| `ISPICKVAL()` | 在检查列表字段的等价性时使用。**绝对不要**使用 `==` 与列表字段一起使用。 |
| `ISCHANGED()` | 使用 `ISCHANGED()` 检查字段值是否已更改。不要手动比较与 `PRIORVALUE()`。 |

---

## 8. 常见部署错误

| 错误消息         | 原因   | 修复   |
|------------------|--------|--------|
| `ConversionError: Invalid XML tags or unable to find matching parent xml file for CustomField` | XML 注释放置在根 `<CustomField>` 元素之前 | 移除 `.field-meta.xml` 文件中 `<CustomField>` 之前的 XML 注释 (`<!-- ... -->`) |
| `Field [FieldName] does not exist. Check spelling.` | 引用字段不存在或尚未部署 | 验证引用字段存在并已部署 |
| `DUPLICATE_DEVELOPER_NAME` | 字段 fullName 在对象上已存在 | 使用唯一的业务驱动名称 |
| `MAX_RELATIONSHIPS_EXCEEDED` | 对象上的主从或查找字段超过 2 个或 15 个 | 使用查找创建第 3 个+主从；检查查找数量 |
| 保留关键字错误   | 使用 `Order__c`、`Group__c` 等 | 重命名为 `Status_Order__c` 等 |

---

## 9. 验证检查清单

在生成 CustomField XML 之前，请验证：

### 通用检查
- [ ] `<fullName>` 是否使用有效格式并以 `__c` 结尾？
- [ ] `<description>` 和 `<inlineHelpText>` 是否都填充了有意义的文本？
- [ ] `<label>` 是否为首字母大写？
- [ ] 是否没有根 `<CustomField>` 元素之前的 XML 注释 (`<!-- ... -->`)？（根元素之前的注释会破坏 SDR 的解析器）

### 主从字段检查 ⭐ CRITICAL
- [ ] 是否缺少 `<required>` 属性？（主从字段按设计总是必需的）
- [ ] 是否缺少 `<deleteConstraint>` 属性？（主从字段总是级联删除）
- [ ] 是否缺少 `<lookupFilter>` 块？（仅适用于查找字段）
- [ ] `<relationshipOrder>` 是否设置为 `0` 或 `1`？
- [ ] 父对象的 `<sharingModel>` 是否设置为 `ControlledByParent`？

### 查找字段检查
- [ ] `<deleteConstraint>` 是否设置为 `SetNull`、`Restrict` 或 `Cascade`？
- [ ] `<relationshipName>` 是否为复数帕斯卡命名法？

### 汇总摘要字段检查 ⭐ CRITICAL
- [ ] 是否缺少 `<precision>` 属性？
- [ ] 是否缺少 `<scale>` 属性？
- [ ] `<summaryForeignKey>` 是否为格式 `ChildObject__c.MasterDetailField__c`？
- 对于 SUM/MIN/MAX：`<summarizedField>` 是否为格式 `ChildObject__c.FieldName__c`？
- 对于 COUNT：是否缺少 `<summarizedField>`？
- 子对象是否有一个指向此父对象的主从字段？

### 公式字段检查
- [ ] `<type>` 是否设置为结果类型（不是“Formula”）？
- [ ] `<formula>` 内容是否用 `<![CDATA[ ... ]]>` 包裹？
- [ ] 是否缺少 `<returnType>` 属性？（Metadata API 中不存在）
- [ ] `<formulaTreatBlanksAs>` 是否设置为 `BlankAsZero`（对于数值结果）或 `BlankAsBlank`（对于文本/日期结果）？
- [ ] 所有引用字段是否存在并在此字段之前部署？

### 数值字段检查
- [ ] 是否 `scale ≤ precision`？
- [ ] 是否 `precision ≤ 18`？

### 文本区域检查
- 对于 TextArea：是否明确包含 `<length>255</length>`？
- 对于 LongTextArea/Html：是否设置了 `<visibleLines>`？

### 关系限制检查
- [ ] 对象上的主从关系是否为 2 个或更少？
- [ ] 对象上的查找关系是否为 15 个或更少？

### 命名检查
- [ ] API 名称是否包含保留字（`Order`、`Group`、`Select` 等）？
- [ ] API 名称在此对象上是否唯一？
