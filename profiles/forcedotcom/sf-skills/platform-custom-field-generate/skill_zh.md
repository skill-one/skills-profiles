# Salesforce 自定义字段生成器和验证器

## 概述

生成和验证 Salesforce CustomField 元数据 XML，对**最高失败率类型**（汇总明细和主明细）进行特殊处理。代理必须在输出 XML 之前验证以下约束，以防止元数据 API 部署错误。

---

## 1. 通用强制属性

每个生成的字段必须包含以下标签：

| 属性 | 要求 | 备注 |
|------|-------------|-------|
| `<fullName>` | 必须包含 | **字段**名称仅：从 `<label>` 派生——每个单词大写，用下划线替换空格，追加 `__c`。必须以字母开头。例如，标签 `Total Contract Value` → `Total_Contract_Value__c`。此规则适用于**字段**名称。** picklist 值 `<fullName>` 不同——保持用户拼写的方式，包括空格，无 `__c`**（例如 `Closed Won`，不是 `Closed_Won`）。参见 [`references/advanced-picklists.md`](references/advanced-picklists.md) (ref §3)。 |
| `<label>` | 必须包含 | UI 名称（首字母大写） |
| `<description>` | 必须包含 | 解释此字段存在的业务原因。 |
| `<inlineHelpText>` | 必须包含 | 超越标签的价值的、可操作的用户指导（例如，“以包括税的美元输入值”，而不是“金额”）。 |

`<description>` 和 `<inlineHelpText>` 即使元数据 API 不强制执行它们也是强制性的——省略它们会产生低质量的元数据。

**文件路径（SFDX 源格式）：** 将每个字段保存为 `force-app/main/default/objects/<Object>/fields/<FieldName>__c.field-meta.xml`，其中 `<Object>` 是对象的 API 名称（`Account`、`Opportunity` 或自定义 `Inventory_Item__c`）。正确的 XML 在错误路径上永远不会被元数据 API 看到。

### 外部 ID 配置

**触发条件：** 如果用户提到“集成”、“导入数据”、“外部系统 ID”或“来自 [系统名称] 的唯一键”，则设置 `<externalId>true</externalId>`。

**适用类型：** 文本、数字、电子邮件

---

## 2. 精度、小数位数和长度规则

为确保部署成功，请遵循以下数学约束：

### 精度与小数位数规则

- `precision` 是总位数；`scale` 是小数位数
- **规则：** `precision ≤ 18` AND `scale ≤ precision`
- **计算：** 小数点左侧的位数 = `precision - scale`

### “固定 255”规则

**TextArea：不要包含 `<length>`**——API 隐式地将它固定在 255，并拒绝显式值（“不能为类型为 TextArea 的 CustomField 指定 'length'”）。该字段只需要 `<fullName>`、`<label>` 和 `<type>TextArea</type>`。

### 可见行数

对于长/富文本和多选 picklist 控制 UI 高度是强制性的。

---

## 3. 字段数据类型

### 3.1 简单属性类型

| 类型 | `<type>` 值 | 必须包含的属性 |
|------|----------------|---------------------|
| 自动编号 | `AutoNumber` | `displayFormat`（必须包含 `{0}`）、`startingNumber` |
| 复选框 | `Checkbox` | 默认 `defaultValue` 为 `false` |
| 日期 | `Date` | 无需精度/长度 |
| 日期/时间 | `DateTime` | 无需精度/长度 |
| 电子邮件 | `Email` | 内置格式验证 |
| 查找关系 | `Lookup` | `referenceTo`、`relationshipName`、`deleteConstraint` |
| 主明细关系 | `MasterDetail` | `referenceTo`、`relationshipName`、`relationshipOrder` |
| 数字 | `Number` | `precision`、`scale` |
| 货币 | `Currency` | 默认精度：18，小数位数：2 |
| 百分比 | `Percent` | 默认精度：5，小数位数：2 |
| 电话 | `Phone` | 标准化电话号码格式 |
| Picklist | `Picklist` | `valueSet` 包含**要么** `valueSetDefinition`（内联）**要么** `valueSetName`（引用）；`restricted`（见下文“Picklist `restricted` 默认值”；高级情况在 §3.4） |
| 文本 | `Text` | `length`（最大 255） |
| 文本区域 | `TextArea` | 无——**不要包含 `<length>`**；API 隐式地将长度固定为 255 |
| 文本（长） | `LongTextArea` | `length`、`visibleLines`（默认 3） |
| 文本（富） | `Html` | `length`、`visibleLines`（默认 25） |
| 时间 | `Time` | 仅存储时间（不存储日期） |
| URL | `Url` | 验证协议和格式 |

### 3.2 计算和多值类型

| 类型 | `<type>` 值 | 必须包含的属性 |
|------|----------------|---------------------|
| 公式 | 结果类型（例如，`Number`） | `formula`、`formulaTreatBlanksAs` |
| 汇总明细 | `Summary` | 见第 5 节的完整要求 |
| 多选 Picklist | `MultiselectPicklist` | `valueSet`、`visibleLines`（默认 4） |

### 3.3 特殊类型

| 类型 | `<type>` 值 | 必须包含的属性 |
|------|----------------|---------------------|
| 地理位置信息 | `Location` | `scale`、`displayLocationInDecimal` |

### Picklist `restricted` 默认值

**始终设置 `<restricted>true</restricted>` 在 `<valueSet>` 内部，除非用户明确说明 picklist 应接受不在管理员定义列表中的自定义值（例如，“无限制”/“开放”）。受限集最多 1,000 个总值（活动 + 非活动）。最小内联形状：

```xml
<valueSet>
  <restricted>true</restricted>
  <valueSetDefinition>
    <sorted>false</sorted>
    <value><fullName>Option_A</fullName><default>false</default><label>Option A</label></value>
  </valueSetDefinition>
</valueSet>
```

### 3.4 高级 Picklist

上述内联 `<valueSetDefinition>` 是简单情况。完整规则和正确/错误示例对于以下所有内容都在
[`references/advanced-picklists.md`](references/advanced-picklists.md) 中——对于任何非平凡的 picklist 加载它。下文括号中的节号（例如“ref §1”）指向该参考文件，而不是此技能。硬规则：

- **值集引用（ref §1）。** `<valueSet>` 要么包含 `<valueSetName>`（引用）**要么** `<valueSetDefinition>`（内联）——**永远不会同时包含**。通过**裸**开发者名称引用——标准集 `Industry`、全局值集 `Priority_Levels` **没有 `__gvs`** 且没有 `__c`（`__gvs` 后缀仅用于组织存储显示；元数据 API 使用裸名称）。基于值集的字段是 `<restricted>true</restricted>`。创建值集是 `platform-value-set-generate` 技能的工作；这个只引用它。
- **值名保真度（ref §3）。** Picklist 值的 `<fullName>`/`<label>` 保持用户的确切文本**包括空格**（`Closed Won`，从不 `Closed_Won`）。空格→`_` + `__c` 规则仅适用于**字段**名称。
- **依赖 Picklist（ref §2）。** 使用**现代 API 38.0+** 形式：`<controllingField>` + 每对一个 `<valueSettings>` (`<controllingFieldValue>`+`<valueName>`）；**从不**使用遗留 `<picklist>`/`<picklistValues>`/`<controllingFieldValues>` 标签。**两者**控制字段和依赖字段都必须是 `<restricted>true</restricted>`，即使请求没有说明。
- **增强值属性（ref §3）。** `<value>` 条目还接受 `<color>`（十六进制，以 `#` 开头）、`<isActive>`（`false` 使值失效）和值级别的 `<description>`。
- **将 Picklist 限制为记录类型（ref §5）。** 每条记录类型的值可见性存在于**记录类型**（`<picklistValues>`），而不是字段。记录类型文件携带其自己的 `<fullName>`（裸开发者名称）。**首先决定对象是否需要业务流程：** 仅**Opportunity / Lead / Case / Solution** 需要一个——它们在没有 `<businessProcess>`（“缺少必填字段：businessProcess”）的情况下不会部署，即使只有一个自定义 picklist 被过滤。在那里你发出**两个耦合文件**：`businessProcesses/<Name>.businessProcess-meta.xml` 文件和匹配的 `<businessProcess><Name></businessProcess>` 在 `<RecordType>` 内部（在 `<active>` 之后，`<picklistValues>` 之前；BP 文件中的 `<fullName>` 是**裸的**，永远不会对象限定）。**范围限制：** 仅限于每条记录类型的 picklist 值可见性——**不是**通用记录类型编写（紧凑布局、页面布局、品牌）。

---

## 4. 主明细关系规则 关键

主明细字段有**严格的属性限制**，与查找字段不同。违反这些规则会导致部署失败。

### 主明细字段上的禁止属性

**绝对不要在主明细字段上包含这些属性：**

| 禁止属性 | 原因 | 结果 |
|---------------------|-----|--------------|
| `<required>` | 主明细按设计总是必填 | 部署错误 |
| `<deleteConstraint>` | 主明细总是级联删除 | 部署错误 |
| `<lookupFilter>` | 仅支持在查找字段上 | 部署错误 |

### 主明细与查找比较

| 属性 | 主明细 | 查找 |
|-----------|---------------|--------|
| `<required>` | 禁止 | 可选 |
| `<deleteConstraint>` | 禁止（总是级联） | 必须为 `SetNull`、`Restrict`、`Cascade` |
| `<lookupFilter>` | 禁止 | 可选 |
| `<relationshipOrder>` | 必须为 0 或 1 | 不适用 |
| `<reparentableMasterDetail>` | 可选 | 不适用 |
| `<writeRequiresMasterRead>` | 可选 | 不适用 |

### 错误——带有禁止属性的主明细：

```xml
<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
  <fullName>Account__c</fullName>
  <type>MasterDetail</type>
  <referenceTo>Account</referenceTo>
  <relationshipName>Contacts</relationshipName>
  <relationshipOrder>0</relationshipOrder>
  <required>true</required>                     <!-- 错误：移除 -->
  <deleteConstraint>Cascade</deleteConstraint>  <!-- 错误：移除 -->
  <lookupFilter>...</lookupFilter>              <!-- 错误：移除整个块 -->
</CustomField>
```

**错误：** `Master-Detail Relationship Fields Cannot be Optional or Required` · `Can not specify 'deleteConstraint' for a CustomField of type MasterDetail` · `Lookup filters are only supported on Lookup Relationship Fields`

### 正确——主明细字段：

```xml
<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
  <fullName>Account__c</fullName>
  <label>Account</label>
  <description>将此记录链接到其父 Account</description>
  <type>MasterDetail</type>
  <referenceTo>Account</referenceTo>
  <relationshipLabel>Child Records</relationshipLabel>
  <relationshipName>ChildRecords</relationshipName>
  <relationshipOrder>0</relationshipOrder>
  <reparentableMasterDetail>false</reparentableMasterDetail>
  <writeRequiresMasterRead>false</writeRequiresMasterRead>
  <!-- 无 required、deleteConstraint 或 lookupFilter -->
</CustomField>
```

### 正确——查找字段（带可选属性）：

```xml
<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
  <fullName>Related_Account__c</fullName>
  <label>Related Account</label>
  <description>可选链接到相关 Account</description>
  <type>Lookup</type>
  <referenceTo>Account</referenceTo>
  <relationshipLabel>Related Records</relationshipLabel>
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

### 额加主明细规则

- **关系顺序：** 对象上的第一个主明细 = `0`，第二个 = `1`
- **关系名称：** 必须是复数帕斯卡字符串（例如，`Travel_Bookings`）
- **连接对象：** 使用两个主明细字段进行标准多对多（启用汇总）
- **限制：** 每个对象最多 2 个主明细关系。使用查找进行额外的关系。

---

## 5. 汇总明细字段规则 关键

汇总明细字段有**最高的部署失败率**。请严格按照以下规则操作。

### 汇总明细的必要元素

| 元素 | 要求 | 格式 |
|---------|-------------|--------|
| `<type>` | 必须包含 | 始终 `Summary` |
| `<summaryOperation>` | 必须包含 | `count`、`sum`、`min` 或 `max` |
| `<summaryForeignKey>` | 必须包含 | `ChildObject__c.MasterDetailField__c` |
| `<summarizedField>` | 条件性 | 对于 `sum`、`min`、`max` 需要。`count` 不需要 |

### 汇总明细上的禁止元素

**绝对不要在汇总明细字段上包含这些属性：**

| 禁止属性 | 原因 |
|---------------------|-----|
| `<precision>` | 汇总继承自汇总字段 |
| `<scale>` | 汇总继承自汇总字段 |
| `<required>` | 不适用于汇总字段 |
| `<length>` | 不适用于汇总字段 |

### summaryForeignKey 和 summarizedField 的格式规则

**关键：** `summaryForeignKey` 和 `summarizedField` 必须使用完全限定格式：

```text
ChildObjectAPIName__c.FieldAPIName__c
```

**决策逻辑：**
- `summaryForeignKey` = `ChildObject__c.MasterDetailFieldOnChild__c`
- `summarizedField` = `ChildObject__c.FieldToSummarize__c`

### 错误——带有常见错误的汇总明细：

```xml
<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
  <fullName>Total_Amount__c</fullName>
  <label>Total Amount</label>
  <type>Summary</type>
  <precision>18</precision>           <!-- 错误：移除——继承自源 -->
  <scale>2</scale>                    <!-- 错误：移除——继承自源 -->
  <summaryOperation>sum</summaryOperation>
  <summaryForeignKey>Order__c</summaryForeignKey>        <!-- 错误：缺少字段名 -->
  <summarizedField>Amount__c</summarizedField>           <!-- 错误：缺少对象名 -->
</CustomField>
```

**错误：**
- `Can not specify 'precision' for a CustomField of type Summary`
- `Must specify the name in the CustomObject.CustomField format (e.g. Account.MyNewCustomField)`

### 正确——SUM 操作的汇总明细：

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

**COUNT：** 类似于 SUM，但**省略 `<summarizedField>`**（保留 `<summaryForeignKey>`）。**MIN / MAX：** 类似于 SUM，使用 `<summaryOperation>min</summaryOperation>` 或 `max`。

### 汇总明细快速参考

| 操作 | summarizedField 需要? | 用例 |
|-----------|---------------------------|----------|
| `count` | 否 | 计数子记录数量 |
| `sum` | 是 | 汇总数字值 |
| `min` | 是 | 找到最小值 |
| `max` | 是 | 找到最大值 |

### 汇总明细前提条件

- 汇总明细字段只能创建在**父**对象上，该对象在主明细关系中
- 子对象必须有指向此父的主明细字段
- 汇总字段必须存在于子对象上

---

## 6. 公式字段规则

### 公式结果类型

公式本身不是类型。`<formula>` 标签添加到 `<type>` 为**结果数据类型**（`Checkbox`、`Currency`、`Date`、`DateTime`、`Number`、`Percent`、`Text`）的字段上。

- **公式字段永远不会携带 `<length>`**——即使文本结果公式。API 会拒绝它：`Can not specify a length for CustomFields that have a formula`.

### 公式 XML 生成规则

- `<formula>` 标签的内容必须用 `<![CDATA[ ... ]]>` 包裹，这样解析器不会将公式运算符（`&`、`<`、`>`）读取为 XML 标记。
- 如果公式文本本身包含字面序列 `]]>`，则通过拆分 CDATA 块来转义它：例如，`<![CDATA[Text_Field__c & "]]]]><![CDATA[>"]]>`
- **绝对不要**使用名为 `returnType` 的属性或标签。这在元数据 API 中不存在。`<type>` 标签定义了公式结果的数据类型。

### formulaTreatBlanksAs 规则

**决策逻辑：**
- 如果公式结果类型 = `Number`、`Currency` 或 `Percent` → 设置 `<formulaTreatBlanksAs>BlankAsZero</formulaTreatBlanksAs>`
- 如果公式结果类型 = `Text`、`Date` 或 `DateTime` → 设置 `<formulaTreatBlanksAs>BlankAsBlank</formulaTreatBlanksAs>`

### 错误——使用 Formula 作为类型：

```xml
<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
  <fullName>Calculated_Value__c</fullName>
  <type>Formula</type>  <!-- 错误：Formula 不是有效的类型 -->
  <returnType>Number</returnType>  <!-- 错误：returnType 在 Metadata API 中不存在 -->
  <formula>Field1__c + Field2__c</formula>  <!-- 错误：缺少 CDATA 包裹 -->
</CustomField>
```

### 正确——公式字段：

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

### 公式字段依赖项和函数

- 引用其他字段的公式字段如果引用的字段不存在或尚未部署，则部署失败——首先部署引用字段。
- 使用 `ISPICKVAL()`（而不是 `==`）进行 picklist 比较。
- 对于完整的公式函数参考（TEXT/VALUE/CASE/DAY/MONTH/DATEVALUE/ISCHANGED 类型规则），请参考 `platform-validation-rule-generate` 技能，该技能负责公式函数的正确性。

---

## 7. 常见部署错误

| 错误消息 | 原因 | 修复 |
|---------------|-------|-----|
| `ConversionError: Invalid XML tags or unable to find matching parent xml file for CustomField` | XML 注释放置在根 `<CustomField>` 元素之前 | 移除 `.field-meta.xml` 文件中 `<CustomField>` 之前的 XML 注释 (`<!-- ... -->`)
| `Field [FieldName] does not exist. Check spelling.` | 引用字段不存在或尚未部署 | 验证引用字段存在并已部署
| `DUPLICATE_DEVELOPER_NAME` | 字段 fullName 在对象上已存在 | 使用唯一的业务驱动名称 |
| `MAX_RELATIONSHIPS_EXCEEDED` | 对象上的主明细或查找字段超过 2 个或 15 个 | 使用查找进行第 3 个+主明细；检查查找数量 |
| 保留关键字错误 | 使用 `Order__c`、`Group__c` 等 | 重命名为 `Status_Order__c` 等 |
| `Value set must reference a value set name or define a value set, but not both` | `<valueSet>` 同时包含 `<valueSetName>` 和 `<valueSetDefinition>` | 保留其中之一（见 §3.4）
| `duplicate value found: [X] is defined multiple times` | 两个 `<value>` 条目共享 `<fullName>` | 使每个 picklist 值 `<fullName>` 唯一 |
| `Invalid fullName` on a picklist value | 值 `<fullName>` 以数字开头或包含连字符 | 以字母开头；无连字符，无前导数字。空格是允许的——**不要**用下划线替换它们（见 §3.4 值名保真度规则）
| `Element ...picklist is not allowed` | 已弃用 ≤37.0 依赖 picklist 语法 (`<picklist>`/`<picklistValues>`/`<controllingFieldValues>`) | 使用现代 `valueSettings`/`controllingFieldValue`/`valueName` 形式（§3.4） |

---

## 8. 验证检查清单

在生成 CustomField XML 之前，请验证：

### 通用检查
- [ ] `<fullName>` 是否使用有效格式并以 `__c` 结尾？
- [ ] `<description>` 和 `<inlineHelpText>` 是否都填充且有意义？
- [ ] `<label>` 是否为首字母大写？
- [ ] 是否在根 `<CustomField>` 元素之前没有 XML 注释 (`<!-- ... -->`)？(根元素之前的注释会破坏 SDR 的解析器)

### 主明细字段检查 关键
- [ ] 是否缺少 `<required>` 属性？(主明细总是必填)
- [ ] 是否缺少 `<deleteConstraint>` 属性？(主明细总是级联)
- [ ] 是否缺少 `<lookupFilter>` 块？(仅用于查找字段)
- [ ] `<relationshipOrder>` 是否设置为 `0` 或 `1`？
- [ ] 父对象的 `<sharingModel>` 是否设置为 `ControlledByParent`？

### 查找字段检查
- [ ] `<deleteConstraint>` 是否设置为 `SetNull`、`Restrict` 或 `Cascade`？
- [ ] `<relationshipName>` 是否为复数帕斯卡字符串？

### Picklist 字段检查
- [ ] 每个 `<valueSet>` 是否包含**要么** `<valueSetName>`（引用）**要么** `<valueSetDefinition>`（内联）——**永远不会同时包含**？
- [ ] 对于值集引用：`<restricted>true</restricted>` 是否设置？
- [ ] 对于标准值集引用：名称是否为裸枚举，**没有 `__c`**（例如 `Industry`）？
- [ ] 对于全局值集引用：名称是否为**裸**开发者名称，**没有 `__gvs`** 后缀？
- [ ] 对于依赖 picklist：是否设置 `<controllingField>`，每对使用一个 `<valueSettings>` (`<controllingFieldValue>` + `<valueName>`）？
- [ ] 对于依赖 picklist：是否缺少遗留 `<picklist>`/`<picklistValues>`/`<controllingFieldValues>` 形式？
- [ ] 所有 picklist 值 `<fullName>` 值是否唯一，以字母开头且不含连字符？(空格是允许的——根据 §3.4 值名保真度规则，**不要**用下划线替换它们)

### 汇总明细字段检查 关键
- [ ] 是否缺少 `<precision>` 属性？
- [ ] 是否缺少 `<scale>` 属性？
- [ ] `<summaryForeignKey>` 是否为格式 `ChildObject__c.MasterDetailField__c`？
- [ ] 对于 SUM/MIN/MAX：`<summarizedField>` 是否为格式 `ChildObject__c.FieldName__c`？
- [ ] 对于 COUNT：是否缺少 `<summarizedField>`？
- [ ] 子对象是否有一个指向此父的主明细字段？

### 公式字段检查
- [ ] `<type>` 是否设置为结果类型（**不是**“Formula”）？
- [ ] `<formula>` 内容是否用 `<![CDATA[ ... ]]>` 包裹？
- [ ] 是否缺少 `<returnType>` 属性？(在 Metadata API 中不存在)
- [ ] 是否缺少 `<length>`？(公式字段永远不会携带长度，即使是文本结果公式)
- [ ] `<formulaTreatBlanksAs>` 是否设置为 `BlankAsZero`（数值结果）或 `BlankAsBlank`（文本/日期结果）？
- [ ] 所有引用字段是否存在并在此字段之前部署？

### 数值字段检查
- [ ] 是否 `scale ≤ precision`？
- [ ] 是否 `precision ≤ 18`？

### 文本区域检查
- [ ] 对于 TextArea：是否**省略** `<length>`？(API 会拒绝 TextArea 字段的显式 `<length>` 值。)
- [ ] 对于 LongTextArea/Html：是否设置 `<visibleLines>`？

### 关系限制检查
- [ ] 对象上的主明细关系是否为 2 个或更少？
- [ ] 对象上的查找关系是否为 15 个或更少？

### 命名检查
- [ ] API 名称是否包含保留字（`Order`、`Group`、`Select` 等）？
- [ ] API 名称在此对象上是否唯一？
