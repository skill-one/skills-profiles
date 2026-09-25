# Salesforce 数据+工具API技能

此技能提供**2130标准Salesforce对象**的字段级参考，涵盖两个运行时API表面：**企业/数据API**（您使用SOQL查询并使用DML修改的标准sObject）和**工具API**（开发者/元数据相邻记录，如`ApexClass`、`ApexCodeCoverage`、`TraceFlag`和`EntityDefinition`）。

在编写SOQL/SOSL、构建DML或运行时读取记录之前，使用它来查找权威的字段名称、类型和属性——这样查询和写入就不会因`INVALID_FIELD` / "没有此列"错误而失败。

> **仅限标准对象。** 这些资源涵盖标准sObjects和Tooling记录。自定义`__c`对象以及标准对象上的自定义`__c`字段**不**在此语料库中——它们不存在于静态文档页面中。对于这些，请描述实时组织（`sf sobject describe --sobject <Name>`）。

## 概述

每个对象都作为JSON文件进行记录，包含：

- 字段定义：名称、类型和属性（可创建、可过滤、可分组、可空、可排序、可更新）
- 关系元数据（关系名称、引用对象、关系类型）用于企业sObject
- Tooling记录支持的SOAP调用和REST HTTP方法
- WSDL模式段
- 使用说明和相关对象（企业sObject）

> **此技能用于运行时数据，而非部署。** 要编写`*-meta.xml`源文件（CustomObject、Flow、Profile、...），请使用**元数据API**技能（`platform-metadata-api-context-get`）。它们是伙伴关系，而非替代品。

## 如何使用此技能

### 关键：字段存在性门（在回答之前执行此操作）

**永远不要凭记忆或训练数据回答字段问题——"字段X是否存在？"、"X是否可过滤/可排序/可分组？"、"X的API名称/类型是什么？"——绝对要首先进行查找。** 这包括像`Id`、`Name`、`CreatedDate`、`LastModifiedDate`、`OwnerId`、`IsDeleted`这样的明显系统字段。请查看以下字段存在性门以获取详细信息。

**运行一个原子命令，同时检查两个目录**（字段可以存在于`fields`、`field_reference`或两者都不存在——请参阅下文双目录说明）：

```bash
jq '{fields: .fields["<FieldName>"], field_reference: .field_reference["<FieldName>"]}' assets/enterprise_api/<Object>.json
# 例如检查Account上的CreatedDate：
jq '{fields: .fields["CreatedDate"], field_reference: .field_reference["CreatedDate"]}' assets/enterprise_api/Account.json
```

解释结果：在`fields`中找到 → 使用其`properties`进行能力回答。仅在`field_reference`中找到 → 它存在，但Filter/Sort/Group**无法**从此技能中确定（此目录不包含属性标志）。两者均为`null` → 不在此语料库中（可能仍然是实时组织/自定义字段——描述组织）。

**强制性验证门。** 在您声明任何字段事实之前，必须首先在回复用户时原封不动地打印此行：

```text
field_lookup: object=<Object> field=<FieldName> checked_fields=<yes|no> checked_field_reference=<yes|no> result=<in_fields|in_field_reference|not_found>
```

如果您无法以两个检查都为`yes`的真实情况打印此行，则您尚未执行查找——停止并运行jq命令。不要凭空编造引用，如“基于技能的数据”，而未运行它。

此门线是仅用于您对话式响应的自验证标记——**不要**将其写入您为用户生成的文件（`.soql`、`.md`、`.json`、查询注释头等）。交付物应仅包含用户请求的答案/查询；将`field_lookup:`行排除在外。

### 关键：特定部分消耗

**始终仅从JSON文件中消耗您需要的特定部分，而不是整个文件。**

**对于`assets/enterprise_api/*.json`和`assets/tooling_api/*.json`文件，始终使用`jq`或程序化JSON解析来提取您需要的部分。** 不要通过`Read`、`cat`或`read_file`加载整个文件——它们包含冗长的`wsdl_segment`和`field_reference`部分，对于Account等大型sObject会浪费60-80%的token。

每个JSON文件包含多个部分。大多数用例只需要1-2个：

- **对于查询/DML字段列表**：仅加载`fields`部分
- **对于关系遍历**：加载`fields`（`relationship_name` / `refers_to`列是内联的）
- **对于Tooling调用支持**：加载`supported_soap_calls` / `supported_rest_api_http_methods`
- **对于“此用户可以查询它吗？”/权限问题**：加载`special_access_rules`（当对象记录访问门时，两者表面都存在）
- **对于查询上限/不受支持的子句**（记录上限，没有`ORDER BY`/`queryMore()`/`OFFSET`）：加载`limitations`——仅存在于强制执行它们的对象上
- **默认跳过**：`wsdl_segment`、`ispersonaccount_fields`

**双目录规则（强制——这是人们常犯错的点）：**

1. 字段可以存在于`fields`、`field_reference`、两者都存在或两者都不存在。这些是两个不同的目录，而不是超集关系。
2. **在`fields`中未找到**不等于“字段不存在”的答案。在得出任何结论之前，请先检查`field_reference`——上述原子jq命令可一次性完成两者检查。
3. Filter/Sort/Group/Create/Update/Nillable属性**仅**来自`fields`。仅在`field_reference`中找到的字段在此处**没有**可检索的能力标志——请这样说；不要猜测。

<details>
<summary><b>为什么有两个目录不同（参考——可选阅读）</b></summary>

`fields`来自Salesforce的SOAP“Fields”表（查询/DML属性：可创建、可过滤、可分组、可空、可排序、可更新）。`field_reference`来自不同的面向UI的“Field List”表（标签/长度/精度/比例），一些对象将其与SOAP表分开记录——它可能包含`fields`根本不列出的许多字段（例如具有非常大的布尔标志目录的对象，或各种面向管理员且SOAP表省略的字段）。在整个语料库中，数千个字段仅存在于`field_reference`中，而较少的字段仅存在于`fields`中。这就是为什么字段存在性答案需要检查两者，以及为什么能力问题只能从`fields`中回答。
</details>

### 哪个文件夹？

- **您在运行时查询和修改的标准sObjects**（Account、Contact、Opportunity、Lead、Case、...）→ `assets/enterprise_api/`
- **开发者/诊断记录**（ApexClass、ApexCodeCoverageAggregate、TraceFlag、EntityDefinition、MetadataComponentDependency、SymbolTable）→ `assets/tooling_api/`
- **自定义`__c`对象和自定义`__c`字段** → 不在这些资源中。描述实时组织：`sf sobject describe --sobject <Name> --target-org <alias>`。（标准Account上的自定义字段如`Region__c`也不会在`assets/enterprise_api/Account.json`中。）

### 示例查询（特定部分）

做：

- "仅显示assets/enterprise_api/Account.json的'fields'部分"
- "Opportunity上的可过滤字段是什么？"
- "Contact上的哪些字段是关系，以及它们引用什么？"
- "ApexClass在Tooling API中支持哪些SOAP调用？"
- "字段X不在`fields`中——在说它不存在之前，请先检查`field_reference`"

不要：

- "加载Account.json"（拉取巨大的`wsdl_segment`；相反，分别加载`fields`和`field_reference`而不是整个文件）

## JSON文件结构

企业（数据）sObject位于`assets/enterprise_api/`；Tooling记录位于`assets/tooling_api/`。两者共享一个共同的内核，但有一些表面特定部分。

```json
{
  "sections": ["title", "description", "fields", "wsdl_segment", ...],
  "title": "Account | Enterprise API",
  "description": "对象的无格式文本描述。",
  "fields_columns": ["type", "properties", "description", "relationship_name", "refers_to", "relationship_type"],
  "fields": {
    "fieldName": {
      "type": "string | reference | picklist | ...",
      "properties": "Create, Filter, Group, Nillable, Sort, Update",
      "description": "字段描述",
      "relationship_name": "(仅限引用字段)",
      "refers_to": "(仅限引用字段) 例如 Account"
    }
  },
  "wsdl_segment": "<xsd:complexType>...</xsd:complexType>"
}
```

`fields`是一个**以字段API名称为键的字典**（例如`fields["AnnualRevenue"]`），而不是列表——使用`.items()`/.keys()迭代，不要按位置索引它。

### 部分是如何派生的（在假设列表之前阅读此内容）

每个JSON文件都是根据该对象Salesforce文档页面上的**实际出现的`## Heading`部分**生成的——JSON模式不是固定且统一模板，完全相同地应用于每个对象。由此直接得出两个后果：

1. **没有部分保证在每个对象上都存在，`fields`也不例外。** 只有当源文档页面有匹配的标题时，文件中的部分才存在。一些Tooling文档页面根本没有字段表（瘦/测试页面），因此`fields`可能缺失；少数SOAP头样式页面将其字段表标记为单数（`field`）而不是复数。**在假设部分存在之前，始终检查文件自己的`sections`数组（或`"fields" in sections`）——不要从查看一个或两个示例对象中硬编码期望。**
2. **页面可以携带超出常见部分的额外部分，每个额外的`##`标题Salesforce在该特定页面上使用的**（例如，由字段引用的嵌套复杂类型，如picklist的值元数据描述，或记录类型信息块）。这些被规范化为`snake_case`键并存储为其自己的顶级部分，或者——当转换器识别标题为*不同子类型*而不是普通内容部分时——嵌套在以子类型名称为键的`sub_types`字典下。** 将“下方可用部分”列表视为常见/频繁的情况，而不是详尽的枚举——任何单个对象的权威列表是该对象自己的`sections`数组。

### 可用部分（常见情况——非详尽；见上文）

- `title`、`description`、`fields_columns`：几乎存在于所有对象上
- `fields`：存在于大多数对象上，但见上述第1点——通过`sections`验证，而不是假设
- **企业专用**：`usage`、`associated_objects`、`ispersonaccount_fields`、`field_reference`、`field_reference_columns`
- **Tooling专用**：`supported_soap_calls`、`supported_rest_api_http_methods`
- `special_access_rules`：**可以查询/访问对象和任何权限或许可证门**（例如，“Customer Portal用户不能访问此对象”、“需要Omnistudio许可证”）。两者表面都存在。在得出给定用户将运行查询的结论之前，请先阅读此内容——这是字段标志无法捕获的查询资格事实。
- `limitations`：**对象强制的查询上限和不受支持的SOQL子句**（例如，MetadataComponentDependency：通过Tooling API最多2000条记录/通过Bulk API 2.0最多100,000条记录；`ORDER BY`、`OFFSET`、`queryMore()`和`*Name`-字段过滤器不受支持）。在针对具有此内容的对象编写查询之前，请先阅读此内容——这些约束无法从`fields`属性中派生。
- `wsdl_segment`：模式定义（冗长——除非您需要原始类型，否则跳过）
- `sub_types`和任何其他`snake_case`命名的部分（未在上文列出）：特定于对象的嵌套模式描述，仅在对象的文档页面有匹配标题时才存在——通过检查文件的`sections`数组来发现每个对象

`fields`的`properties`数组告诉您每个对象的`fields`条目包含哪些列——按对象检查，而不是假设固定形状。企业sObject通常添加`relationship_name`、`refers_to`和`relationship_type`；Tooling记录通常只包含`type`、`properties`、`description`——但有意义的小部分Tooling对象也包含`relationship_type`，所以不要将其视为企业专属。`relationship_type`值在源数据中也有拼写变体（例如`"Lookup"`与`"Look up"`），请进行松散比较（例如`.replace(" ", "").lower()`），而不是精确字符串相等。

**类型字符串跨对象不一致——不要假设单一大小写。** 相同的概念根据源文档页面的不同呈现多种拼写形式：`string`/`String`、`boolean`/`Boolean`、`dateTime`/`DateTime`/`datetime`。将`type`值松散比较（例如`.lower()`），而不是与一种大小写使用`==`进行比较。除了常见的`string | reference | picklist`类型之外，真实数据还包括`int`、`boolean`、`double`、`currency`、`date`、`dateTime`、`textarea`、`address`、`url`、`phone`、`email`、`time`、`anyType`、`base64`等——将类型列表视为开放式。

**即使对象其他方面具有结构化`type`/`properties`，字段也可能缺少——在得出数据缺失的结论之前，请先作为后备检查`description`。** 由于每个对象的JSON都是根据该对象自己的文档页面生成的，如果一个页面将字段的类型/属性作为散文（`"Type: ..." Properties: ..." Description: ..."`)放在单个描述段落中，而不是作为单独的表格列——则产生的`fields`条目将`type`/`properties`为空，并将散文放入`description`中。这会影响到从一到多个字段（在最坏的情况下，`fields_columns`本身可能只说`["description"]`）。**如果`type`/`properties`为空或`fields_columns`看起来很可疑，请先检查`description`是否以`"Type: "`开头，然后将其作为后备解析**，然后再得出字段/对象没有类型信息的结论。

**Picklist允许的值有时出现在`description`散文中——在假设它们不存在之前请先检查。** 没有`fields`条目有结构化的`picklistValues`列表。Picklist的允许值是否在`description`中枚举（作为`"可能的值是: ..."`后跟值）完全取决于源文档页面是否为该特定字段枚举了它们——许多文档页面枚举了，许多没有（例如，由单独的值集对象支持的org配置picklist通常只给出类似“例如新、关闭或升级”的示例，而不是完整列表）。当存在时，格式本身是不一致的——有时是空格/逗号分隔的标记，有时是每行一个`Value—解释`-em-dash对——因此没有单一的可靠正则表达式；提取`"Possible values are:"`后的子字符串并按情况解析，不要假设每个picklist都有在这里可发现的值集。

**字段的`description`可能引用关系（例如，“这是一个依赖picklist”、“此字段控制X”）而不命名或解析该关系的另一侧——企业sObject自己的`fields`部分可能不是答案所在的地方。** 此数据集的Tooling API部分记录了Salesforce的字段元数据对象（模式关于模式，例如，一个暴露每个字段描述式属性的暴露对象），这些对象可以携带结构化属性——例如，控制依赖picklist的控字段身份——而企业sObject的文档页面从未明确命名。如果企业字段的描述指向它无法解析的关系，请在得出数据不存在于此技能中的结论之前，检查Tooling侧的字段元数据对象是否回答了它。

**给定对象的JSON可以携带上文中常见列表之外的段落——而不是假设一个封闭的集合——检查该对象自己的`sections`数组，而不是假设一个封闭的集合。** 任何源文档页面上的`##`标题都会变成其自己的`snake_case`命名部分（或者，当转换器识别它为不同的嵌套类型时，成为以子类型名称为键的`sub_types`条目）。这些仅在特定对象的文档中包含该标题时才出现——每个对象的特定对象模式描述有效载荷，而不是要忽略的垃圾。没有固定枚举每个可能的额外部分名称；按对象发现它们。

查看[索引表](references/data_and_tooling_index_table.md)以获取完整对象列表和每个对象的额外部分——它大约是125 KB，因此使用`grep -i "<ObjectName>"`进行单个查找，而不是阅读整个文件。


> **更多详细信息：** 工作查询/DML示例、关系遍历模式和一个完整部分词汇表位于[`references/usage_guide.md`](references/usage_guide.md)。仅在需要时使用`Read`工具加载它。

## 文件位置

对象JSON文件按API表面分割：

```text
assets/
├── enterprise_api/      # 标准sObject（SOQL+DML）
│   ├── Account.json
│   ├── Contact.json
│   └── ...
└── tooling_api/         # 开发者 / 诊断记录
    ├── ApexClass.json
    ├── TraceFlag.json
    └── ...
```

文件相对于技能根进行引用，例如
`assets/enterprise_api/Account.json` 或 `assets/tooling_api/ApexClass.json`。

### 工作示例

可运行的特定部分加载示例（每个示例演示：字段提取、通过`properties`进行可过滤字段查找、关系遍历、`fields`与`field_reference`双目录，以及读取Tooling
`supported_rest_api_http_methods`）：

- **Python**: [`examples/python_section_loading.py`](examples/python_section_loading.py) — `json.load()`与部分提取
- **JavaScript/Node.js**: [`examples/javascript_section_loading.js`](examples/javascript_section_loading.js) — `JSON.parse()`与部分提取
- **Bash + jq**: [`examples/bash_section_loading.sh`](examples/bash_section_loading.sh) — `jq`命令行JSON处理

查看[`examples/README.md`](examples/README.md)以获取用法和属性→SOQL/DML能力表。

## 查询 & DML生成要求

在针对这些对象生成SOQL/SOSL或DML时，请遵循这些规则，以便语句实际运行。

### 验证字段存在及其API名称

1. **首先查找字段（两个目录，原子jq）并打印`field_lookup:`门线——即使是您确信的系统字段也是如此。** 请参阅“如何使用此技能”顶部的字段存在性门。字段API名称对Salesforce不区分大小写，但必须解析为真实字段。自定义字段以`__c`结尾；自定义关系通过`__r`遍历。
2. **不要凭空编造字段。** 猜测的列会产生`INVALID_FIELD: No such column 'X' on entity 'Y'`。如有不确定，请加载`fields`部分并确认。
3. **匹配时不要将`fields`键小写。** 至少有一个对象（`LoginEventLog`）在同一个`fields`字典中具有`UserName`和`Username`作为不同的真实字段——小写/不区分大小写的查找会无声地冲突。按给定的确切键大小写匹配。这些是**两个不同的列**，它们包含可能不同的数据——它们**不是**“平台选择哪个”的同一个字段。通过其确切大小写选择和过滤每个字段；不要将它们描述为可互换的，也不要说查询“模糊解析”，因为平台将它们视为不同的字段。

### 尊重字段属性

每个字段的`properties`字符串控制您可以使用它做什么：

- **过滤** → 可用于`WHERE`子句。没有`Filter`的字段无法过滤。
- **排序** → 可用于`ORDER BY`。
- **分组** → 可用于`GROUP BY`。
- **可创建 / 可更新** → 可通过`insert` / `update` DML设置。系统和公式字段是只读的（没有创建/更新）——写入它们会失败。
- **可空** → 可以是null；非可空字段在插入时是必需的。

**此技能的`properties`字符串没有外部ID标志**——`upsert`需要字段在组织中标记为外部ID，而此数据源不捕获该标志（它仅出现在Metadata API描述输出中，而不是此技能构建的HTML文档中）。要查找或设置字段的External ID标志，请使用**元数据API**技能（`platform-metadata-api-context-get`）并检查`CustomField`的`externalId`属性——不要单独根据此技能的`properties`就猜测upsert字段。

### 关系（企业sObject）

对于`reference`类型字段，`relationship_name`列给出父关系，用于SOQL遍历，`refers_to`命名目标对象：

```sql
-- OwnerId (reference, relationship_name = Owner, refers_to = User)
SELECT Id, Owner.Name FROM Account
-- 自定义查找 Foo__c 作为 Foo__r遍历
SELECT Id, Foo__r.Name FROM My_Object__c
```

### Tooling API与数据API

Tooling记录（`assets/tooling_api/`）通过**Tooling API**端点（`/services/data/vXX.0/tooling/query`）查询，而不是常规数据API。检查`supported_soap_calls` / `supported_rest_api_http_methods`以了解每个记录支持的内容。许多Tooling对象是只读的。

> **不用于部署。** 要编写或编辑`*-meta.xml`源（CustomObject、Flow、Profile、...），请使用Metadata API技能——这里的对象是运行时/可查询的表示形式，而不是可部署的元数据形式。

## 重复和歧义对象名称

几个名称同时存在于Metadata API和此处（ApexClass、ApexTrigger、CustomField、CustomObject、EmailTemplate、Layout、Profile、PermissionSet、RecordType、ValidationRule、Flow、...）。它们表示不同的含义：

- **此技能** = 运行时/可查询的记录：您通过Data或Tooling API查询、过滤和（有时）写入的字段。
- **Metadata API技能** = `*-meta.xml`源形式，您编写和部署的。
- 工具特定：**Tooling API**、`ApexCodeCoverage`、`EntityDefinition`、`TraceFlag`、`SymbolTable`、**代码覆盖率**、**编译错误**、**调试日志** → 此技能的Tooling部分（`assets/tooling_api/`）。

如果直接通过名称调用且没有其他信号，则默认为运行时数据解释，并披露此假设。

## 故障排除

### 文件未找到

- 文件名是**区分大小写PascalCase**，与对象API名称匹配（`Account.json`、`ApexClass.json`），没有分隔符。
- 检查正确的文件夹：企业sObject在`assets/enterprise_api/`，Tooling记录在`assets/tooling_api/`。名称可能只存在于其中一个，或者两者都存在但字段不同。在声明“未找到”之前，使用有针对性的grep搜索索引表（它列出了语料库中的每个对象名称），而不是阅读大约125 KB的整个文件：
  `grep -i "<ObjectName>" references/data_and_tooling_index_table.md`。不区分大小写匹配，并允许近似的间距、复数、轻微拼写错误，然后再得出对象不存在的结论。只有对于广泛的调查才读取完整文件。

### INVALID_FIELD / No such column

- 该字段不存在于该对象上，或者您使用了错误的API名称。加载`fields`部分并确认确切名称（自定义字段以`__c`结尾）。
- 字段存在但缺少所需的属性：过滤非`Filter`字段、排序非`Sort`字段或写入只读（没有`Create`/`Update`）字段都会失败。检查`properties`字符串。

### 关系查询失败

- 使用`relationship_name`（而不是ID字段）遍历：`Owner.Name`，而不是`OwnerId.Name`。自定义查找通过`__r`遍历。
- 确认`refers_to`——多态字段（例如`WhoId`, `WhatId`）引用多个对象，需要`TYPEOF`或正确的关系。

### Tooling查询返回空 / 错误

- Tooling对象必须在Tooling API端点（`/tooling/query`）查询，而不是标准Data API。使用`supported_rest_api_http_methods` / `supported_soap_calls`进行验证。

### 字段在wsdl_segment中但不在fields

- 复杂嵌套类型在其子字段位于`wsdl_segment`中。使用`jq -r '.wsdl_segment' file.json | grep -A 30 'complexType name="Foo"'`提取匹配的`complexType`，而不是加载整个段。

## 常见对象

### 企业 / 数据API（SOQL + DML）

- **Account**：表示单个账户，它是参与您业务的组织或个人（例如客户、竞争对手和合作伙伴）。
- **Contact**：表示联系人，是与账户关联的人员。
- **Opportunity**：表示机会，是销售或待处理的交易。
- **Lead**：表示潜在客户或线索。
- **Case**：表示案例，是客户问题或问题。
- **User**：表示您组织中的用户。
- **Task**：表示业务活动，如打电话或其他待办事项。
- **Event**：表示日历中的事件。

### Tooling API（开发者记录）

- **ApexClass**：表示Apex类的保存副本。
- **ApexTrigger**：表示Apex触发的保存副本。
- **ApexCodeCoverageAggregate**：表示Apex类或触发的聚合代码覆盖率测试结果。
- **TraceFlag**：表示在指定日志级别触发Apex调试日志的跟踪标志。
- **EntityDefinition**：提供基于行的标准对象和自定义对象的元数据访问。
