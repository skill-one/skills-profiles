---
name: platform-data-and-tooling-api-context-get
description: 2130 标准Salesforce对象（如Account、Contact、Opportunity、Lead、Case、ApexClass等）的权威字段/模式参考——包括sObject和Tooling字段API名称、类型、属性（可筛选/可排序/可分组/可更新）以及关系。当字段/类型/功能未验证时，与SOQL/Apex技能一同加载——仅用于查询语法或优化。在SOQL/SOSL查询或针对标准对象执行的DML中验证/调试字段时触发。自定义__c对象/字段不在此范围内——请使用实时组织的sobject描述（sf sobject describe）。禁止用于编写/部署*-meta.xml或sfdx源（使用元数据API技能）。
---

# Salesforce 数据 + 工具 API 技能

此技能为 **2130 个标准 Salesforce 对象** 提供字段级参考，这些对象跨两个运行时 API 表面：**企业/数据 API**（您使用 SOQL 查询并使用 DML 修改的标准 sObject）和 **工具 API**（开发者/元数据相邻的记录，如 `ApexClass`、`ApexCodeCoverage`、`TraceFlag` 和 `EntityDefinition`）。

在编写 SOQL/SOSL、构建 DML 或在运行时读取记录之前，使用它来查找权威的字段名称、类型和属性——这样查询和写入就不会因 `INVALID_FIELD` / "没有此列" 错误而失败。

> **仅限标准对象。** 这些资源涵盖标准 sObject 和工具记录。自定义 `__c` 对象以及标准对象上的自定义 `__c` 字段**不**在此语料库中——它们不存在于静态文档页面中。对于这些，请描述实时组织（`sf sobject describe --sobject <Name>`）。

## 概述

每个对象都作为 JSON 文件进行记录，包含：

- 字段定义：名称、类型和属性（可创建、可过滤、可分组、可空、可排序、可更新）
- 企业 sObject 的关系元数据（关系名称、引用对象、关系类型）
- 工具记录支持的 SOAP 调用和 REST HTTP 方法
- WSDL 模式段
- 使用说明和关联对象（企业 sObject）

> **此技能用于运行时数据，而非部署。** 要编写 `*-meta.xml` 源文件（CustomObject、Flow、Profile、...），请使用 **元数据 API** 技能（`platform-metadata-api-context-get`）。它们是搭档，而非替代品。

## 如何使用此技能

### 关键：字段存在性门（在回答之前执行）

**永远不要凭记忆或训练数据回答字段问题——"字段 X 是否存在？"、"X 是否可过滤/可排序/可分组？"、"X 的 API 名称/类型是什么？"——这包括像 `Id`、`Name`、`CreatedDate`、`LastModifiedDate`、`OwnerId`、`IsDeleted` 这样的明显系统字段。始终先进行查找。** 您从训练中了解这些字段，但此技能的存在恰恰是因为您对它们 *属性*（过滤/排序/分组）以及哪些目录记录它们的记忆不可靠。自信不等于验证。

**运行一个原子命令，同时检查两个目录**（字段可以存在于 `fields`、`field_reference` 或两者都不在——见下文的双目录说明）：

```bash
jq '{fields: .fields["<FieldName>"], field_reference: .field_reference["<FieldName>"]}' assets/enterprise_api/<Object>.json
# 例如检查 Account 上的 CreatedDate：
jq '{fields: .fields["CreatedDate"], field_reference: .field_reference["CreatedDate"]}' assets/enterprise_api/Account.json
```

解释结果：在 `fields` 中找到 → 使用其 `properties` 进行能力回答。仅在 `field_reference` 中找到 → 它存在，但过滤/排序**无法**从此技能中确定（此目录不包含属性标志）。两者均为 `null` → 不在此语料库中（可能仍然是实时组织/自定义字段——描述组织）。

**强制性验证门。** 在您向用户声明任何字段事实之前，必须首先在您的回复中逐字打印此行（如元数据技能的状态行）：

```text
field_lookup: object=<Object> field=<FieldName> checked_fields=<yes|no> checked_field_reference=<yes|no> result=<in_fields|in_field_reference|not_found>
```

如果您无法以两个检查都为 `yes` 的真实性打印此行，则您未执行查找——停止并运行 jq 命令。不要凭空编造引用，如“基于技能的数据”而未运行它。

此门线仅用于您的对话响应的自验证标记——**不要**将其写入您为用户生成的文件（`.soql`、`.md`、`.json`、查询注释头等）。交付物应仅包含用户请求的答案/查询；将 `field_lookup:` 行排除在外。

### 关键：特定部分消耗

**始终仅从 JSON 文件中消耗您需要的特定部分，而不是整个文件。**

**对于 `assets/enterprise_api/*.json` 和 `assets/tooling_api/*.json` 文件，始终使用 `jq` 或程序化 JSON 解析来提取您需要的部分。** 不要通过 `Read`、`cat` 或 `read_file` 整个加载这些文件——它们包含冗长的 `wsdl_segment` 和 `field_reference` 部分，对于像 Account 这样的大型 sObject 会浪费 60-80% 的 token。

每个 JSON 文件包含多个部分。大多数用例只需要 1-2 个：

- **对于查询/DML 字段列表**：仅加载 `fields` 部分
- **对于关系遍历**：加载 `fields`（`relationship_name` / `refers_to` 列是内联的）
- **对于工具调用支持**：加载 `supported_soap_calls` / `supported_rest_api_http_methods`
- **对于“此用户能否查询它？”/权限问题**：加载 `special_access_rules`（当对象记录访问门时，两者表面都存在）
- **对于查询上限/不受支持的子句**（记录上限，没有 `ORDER BY`/`queryMore()`/`OFFSET`）：加载 `limitations`——仅存在于施加它们的对象中
- **默认跳过**：`wsdl_segment`，`ispersonaccount_fields`

**双目录规则（强制性——这是人们常出错的地方）：**

1. 字段可以存在于 `fields`、`field_reference`、两者都存在或两者都不存在。这两个是不同的目录，不是超集关系。
2. **在 `fields` 中未找到不等于“字段不存在”的答案。** 在得出任何结论之前，也检查 `field_reference`——上述原子 jq 命令一次性完成两者检查。
3. 过滤/排序/分组/创建/更新/可空属性**仅**来自 `fields`。仅在 `field_reference` 中找到的字段在此处**没有**可检索的能力标志——请说明；不要猜测。

<details>
<summary><b>为什么有两个目录不同（参考——可选阅读）</b></summary>

`fields` 来自 Salesforce 的 SOAP "Fields" 表（查询/DML 属性：创建/过滤/排序/分组/更新/可空）。`field_reference` 来自一个不同的面向 UI 的 "Field List" 表（标签/长度/精度/比例），一些对象将其与 SOAP 表分开记录——它还可以包含 `fields` 从未列出的许多字段（例如具有非常大的布尔标志目录的对象，或各种面向管理员且 SOAP 表省略的字段）。在整个语料库中，数千个字段仅存在于 `field_reference` 中，而较少的字段仅存在于 `fields` 中。这就是为什么字段存在性答案需要检查两者，以及为什么能力问题只能从 `fields` 中回答。
</details>

### 哪个文件夹？

- **您在运行时查询和修改的标准 sObject**（Account、Contact、Opportunity、Lead、Case、...）→ `assets/enterprise_api/`
- **开发者/诊断记录**（ApexClass、ApexCodeCoverageAggregate、TraceFlag、EntityDefinition、MetadataComponentDependency、SymbolTable）→ `assets/tooling_api/`
- **自定义 `__c` 对象和自定义 `__c` 字段** → 不在此资源中。描述实时组织：`sf sobject describe --sobject <Name> --target-org <alias>`。（标准 Account 上的自定义字段 `Region__c` 也不会在 `assets/enterprise_api/Account.json` 中。）

### 示例查询（特定部分）

做：

- "仅显示 assets/enterprise_api/Account.json 的 'fields' 部分"
- "Opportunity 上的可过滤字段是什么？"
- "Contact 上的哪些字段是关系，以及它们引用什么？"
- "ApexClass 在工具 API 中支持哪些 SOAP 调用？"
- "字段 X 不在 `fields` 中——在说它不存在之前检查 `field_reference`"

不做：

- "加载 Account.json"（拉取巨大的 `wsdl_segment`；加载 `fields` 和 `field_reference` 而不是整个文件）

## JSON 文件结构

企业（数据）sObject 存在于 `assets/enterprise_api/`；工具记录存在于 `assets/tooling_api/`。两者共享一个共同的内核，但有一些表面特定的部分。

```json
{
  "sections": ["title", "description", "fields", "wsdl_segment", ...],
  "title": "Account | Enterprise API",
  "description": "对象 plain-text 描述。",
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

`fields` 是一个**以字段 API 名称键入的字典**（例如 `fields["AnnualRevenue"]`），而不是列表——使用 `.items()`/.keys() 迭代，不要按位置索引它。

### 部分是如何派生的（在假设部分列表之前阅读）

每个 JSON 文件是从该对象 Salesforce 文档页面上的**实际出现的 `## Heading` 部分生成的**——JSON 模式不是固定、统一的模板，相同地应用于每个对象。由此直接得出两个后果：

1. **没有部分保证在所有对象上都存在，`fields` 包括在内。** 只有如果源文档页面有匹配的标题，文件中才会存在部分。一些工具文档页面根本没有字段表（瘦/测试页面），所以 `fields` 可能缺失；一小部分 SOAP 头样式页面将其字段表标记为单数（`field`）而不是复数。**在假设部分存在之前，始终检查文件自己的 `sections` 数组（或 `"fields" in sections`）**——不要从查看一个或两个示例对象硬编码期望。

2. **页面可以携带超出常见部分的额外部分**，每个额外的 `##` 标题 Salesforce 的文档在该特定页面上使用的（例如，一个由字段引用的嵌套复杂类型，如 picklist 的值元数据描述，或记录类型信息块）。这些被规范化为 `snake_case` 键并存储为其自己的顶层部分，或者——当转换器识别标题为 *不同子类型* 而不是普通内容部分时——嵌套在以子类型名称为键的 `sub_types` 字典下。**将下面的“可用部分”列表视为常见/频繁的情况，而不是详尽的枚举**——任何单个对象的权威列表是该对象自己的 `sections` 数组。

### 可用部分（常见情况——非详尽；见上文）

- `title`、`description`、`fields_columns`：几乎存在于所有对象上
- `fields`：存在于大多数对象上，但见上述第 1 点——通过 `sections` 验证，而不是假设
- **企业独有**：`usage`、`associated_objects`、`ispersonaccount_fields`、`field_reference`、`field_reference_columns`
- **工具独有**：`supported_soap_calls`、`supported_rest_api_http_methods`
- `special_access_rules`：**谁可以查询/访问对象以及任何权限或许可证门**（例如，“Customer Portal 用户不能访问此对象”、“需要 Omnistudio 许可证”）。两者表面都存在。在得出给定用户将运行查询之前阅读此内容——这是查询资格事实，字段标志无法捕获。
- `limitations`：**对象施加的查询上限和不受支持的 SOQL 子句**（例如，MetadataComponentDependency：通过工具 API 最多 2000 条记录/通过 Bulk API 2.0 100,000 条记录；`ORDER BY`、`OFFSET`、`queryMore()` 和 `*Name`-字段过滤器不受支持）。在针对具有此内容的对象编写查询之前阅读此内容——这些约束无法从 `fields` 属性中派生。
- `wsdl_segment`：模式定义（冗长——除非需要原始类型，否则跳过）
- `sub_types` 和任何其他 `snake_case`-命名部分：对象特定嵌套模式描述，仅当该对象的文档页面有匹配标题时才存在——检查文件的 `sections` 数组以按对象发现它们

`fields_columns` 数组告诉您每个对象的 `fields` 条目包含哪些列——按对象检查，而不是假设固定形状。企业 sObject 通常添加 `relationship_name`、`refers_to` 和 `relationship_type`；工具记录通常只包含 `type`、`properties`、`description`——但有意义的小部分工具对象也包含 `relationship_type`，所以不要将其视为企业专属。`relationship_type` 值在源数据中也存在拼写变体（例如 `"Lookup"` 与 `"Look up"`）——比较松散（例如 `.replace(" ", "").lower()`）而不是精确字符串相等。

**类型字符串跨对象不一致——不要假设单一大小写。** 相同的概念在源文档页面下以多种拼写形式出现：`string`/`String`、`boolean`/`Boolean`、`dateTime`/`DateTime`/`datetime`。比较 `type` 值不区分大小写（例如 `.lower()`）而不是与一种大小写使用 `==` 进行比较。除了常见的 `string | reference | picklist` 类型外，真实数据还包括 `int`、`boolean`、`double`、`currency`、`date`、`dateTime`、`textarea`、`address`、`url`、`phone`、`email`、`time`、`anyType`、`base64` 以及其他——将类型列表视为开放式。

**给定对象的 JSON 可以包含上述常见列表之外的章节 — 检查该对象自身的 `sections` 数组，而不是假设是一个封闭的集合。** 任何源文档页面上的附加 `##` 标题都将成为其自身的 `snake_case`-命名章节（或者，当转换器将其识别为不同的嵌套类型时，成为 `sub_types` 条目）。这些仅出现在特定对象上，其文档恰好包含该标题 — 每个对象的 schema 描述有效负载，而不是要忽略的垃圾。没有固定枚举所有可能的额外章节名称；通过 `sections` 按对象发现它们。

参考 [索引表](references/data_and_tooling_index_table.md) 获取完整对象列表和每个对象的额外章节 — 它是 ~125 KB，因此 `grep -i "<ObjectName>"` 进行单次查找，而不是阅读整个文件。

> **更多细节：** 工作查询/DML 示例、关系遍历模式以及完整章节词汇表位于 [`references/usage_guide.md`](references/usage_guide.md)。仅在需要时使用 `Read` 工具加载它。

## 文件位置

对象 JSON 文件按 API 表面进行拆分：

```text
assets/
├── enterprise_api/      # 标准 sObjects (SOQL/DML)
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

可运行的章节加载示例（每个示例演示：字段提取、通过 `properties` 查找可过滤字段、关系遍历、`fields` 与 `field_reference` 双目录，以及读取 Tooling `supported_rest_api_http_methods`）：

- **Python**: [`examples/python_section_loading.py`](examples/python_section_loading.py) — `json.load()` 与章节提取
- **JavaScript/Node.js**: [`examples/javascript_section_loading.js`](examples/javascript_section_loading.js) — `JSON.parse()` 与章节提取
- **Bash + jq**: [`examples/bash_section_loading.sh`](examples/bash_section_loading.sh) — `jq` 命令行 JSON 处理

参考 [`examples/README.md`](examples/README.md) 获取用法和属性→SOQL/DML 能力表。

## 查询 & DML 生成要求

在针对这些对象生成 SOQL/SOSL 或 DML 时，遵循以下规则，以便语句实际运行。

### 验证字段存在及其 API 名称

1. **首先查找字段（两个目录、原子 jq），并打印 `field_lookup:` 门线 — 即使对于您确信的系统字段也是如此。** 参考位于“如何使用此技能”顶部“字段存在门”中的说明。字段 API 名称对 Salesforce 不区分大小写，但必须解析为实际字段。自定义字段以 `__c` 结尾；自定义关系通过 `__r` 遍历。
2. **不要编造字段。** 猜测的列会产生 `INVALID_FIELD: No such column 'X' on entity 'Y'`。如有疑问，加载 `fields` 章节并确认。
3. **匹配时不折叠 `fields` 键的大小写。** 至少有一个对象 (`LoginEventLog`) 在同一 `fields` 字典中同时具有 `UserName` 和 `Username` 作为不同的实际字段 — 小写/不区分大小写的查找会无声地冲突它们。匹配给定的确切键大小写。这些是 **两个不同的列，可能包含不同数据** — 它们不是“解析为平台选择的同一个字段。” 通过其确切大小写选择和过滤每个字段；不要将它们描述为可互换的，或说查询“模糊解析”，因为平台将它们视为不同字段。

### 尊重字段属性

每个字段上的 `properties` 字符串控制您可以对它做什么：

- **过滤** → 可用于 `WHERE` 子句。没有 `Filter` 的字段不能被过滤。
- **排序** → 可用于 `ORDER BY`。
- **分组** → 可用于 `GROUP BY`。
- **可创建 / 可更新** → 可通过 `insert` / `update` DML 设置。系统和公式字段是只读的（没有创建/更新）— 写入它们会失败。
- **可空** → 可能是 null；非可空字段在插入时是必需的。

**此技能的 `properties` 字符串没有外部 ID 标志** — `upsert` 需要字段在组织中标记为 External ID，而该标志不是此数据源捕获的（它仅出现在 Metadata API 描述输出中，而不是此技能构建的 HTML 文档中）。要查找或设置字段的外部 ID 标志，请使用 **Metadata API 技能** (`platform-metadata-api-context-get`) 并检查 `CustomField` 的 `externalId` 属性 — 不要仅凭此技能的属性猜测 upsert 字段。

### 关系（企业 sObjects）

对于 `reference` 类型的字段，`relationship_name` 列给出用于 SOQL 遍历的父关系，`refers_to` 指定目标对象：

```sql
-- OwnerId (reference, relationship_name = Owner, refers_to = User)
SELECT Id, Owner.Name FROM Account
-- 自定义查找 Foo__c 作为 Foo__r 遍历
SELECT Id, Foo__r.Name FROM My_Object__c
```

### Tooling API 与 Data API

Tooling 记录 (`assets/tooling_api/`) 通过 **Tooling API** 端点 (`/services/data/vXX.0/tooling/query`) 查询，而不是常规 Data API。检查 `supported_soap_calls` / `supported_rest_api_http_methods` 以了解每个记录支持什么。许多 Tooling 对象是只读的。

> **不用于部署。** 要编写或编辑 `*-meta.xml` 源（CustomObject、Flow、Profile、...），请使用 Metadata API 技能 — 此处的对象是运行时/可查询表示，而不是可部署的元数据形式。

## 重复和歧义对象名称

几个名称同时存在于 Metadata API 和此处（ApexClass、ApexTrigger、CustomField、CustomObject、EmailTemplate、Layout、Profile、PermissionSet、RecordType、ValidationRule、Flow、...）。它们表示不同的含义：

- **此技能** = 运行时/可查询记录：您 `SELECT`、过滤并通过 Data 或 Tooling API（有时）写入的字段。
- **Metadata API 技能** = 您编写和部署的 `*-meta.xml` 源形式。

使用以下信号解决歧义：

- "查询"、"SOQL"、"SOSL"、"DML"、"insert/update/upsert"、"what fields/columns"、"filterable"、"record"、"runtime"、"REST/SOAP" → **此技能**。
- "authoring"、"deploy"、"retrieve"、"package.xml"、"force-app/"、"sfdx"、".meta.xml"、"blueprint/template" → **Metadata API 技能**。
- Tooling 特定： "Tooling API"、"ApexCodeCoverage"、"EntityDefinition"、"TraceFlag"、"SymbolTable"、"code coverage"、"compile errors"、"debug log" → 此技能的 **Tooling 部分** (`assets/tooling_api/`)。

如果直接通过名称调用且没有其他信号，则默认为运行时数据解释并披露假设。

## 故障排除

### 文件未找到

- 文件名是 **区分大小写 PascalCase** 匹配对象 API 名称 (`Account.json`, `ApexClass.json`)，没有分隔符。
- 检查正确的文件夹：企业 sObjects 在 `assets/enterprise_api/`，Tooling 记录在 `assets/tooling_api/`。名称只能存在于其中一个，或以不同字段存在于两者中。
- 在声明“未找到”之前，使用有针对性的 grep 搜索索引表（它列出了语料库中的每个对象名称）而不是阅读整个 ~125 KB 文件：
  `grep -i "<ObjectName>" references/data_and_tooling_index_table.md`。不区分大小写匹配，并允许接近错误（间距、复数、轻微拼写错误）再得出对象缺失的结论。仅当进行广泛调查时才读取完整文件。

### INVALID_FIELD / No such column

- 该字段不在该对象上，或者您使用了错误的 API 名称。加载 `fields` 章节并确认确切名称（自定义字段以 `__c` 结尾）。
- 字段存在但缺少所需属性：过滤非 `Filter` 字段、排序非 `Sort` 字段或写入只读（没有 `Create`/`Update`）字段都会失败。检查 `properties` 字符串。

### 关系查询失败

- 使用 `relationship_name`（而不是 ID 字段）遍历：`Owner.Name`，而不是 `OwnerId.Name`。自定义查找通过 `__r` 遍历。
- 确认 `refers_to` — 多态字段（例如 `WhoId`, `WhatId`）指向多个对象，需要 `TYPEOF` 或正确的关系。

### Tooling 查询返回空 / 错误

- Tooling 对象必须针对 Tooling API 端点 (`/tooling/query`) 查询，而不是标准 Data API。通过 `supported_rest_api_http_methods` / `supported_soap_calls` 验证。

### 字段在 wsdl_segment 但不在 fields 中

- 复杂嵌套类型将其子字段位于 `wsdl_segment`。使用 `jq -r '.wsdl_segment' file.json | grep -A 30 'complexType name="Foo"'` 仅提取匹配的 `complexType`，而不是加载整个段。

## 常见对象

### 企业 / Data API (SOQL + DML)

- **Account**：表示单个账户，它是参与您业务的组织或个人（例如客户、竞争对手和合作伙伴）。
- **Contact**：表示联系人，它是与账户关联的人。
- **Opportunity**：表示机会，它是销售或待处理的交易。
- **Lead**：表示潜在客户或线索。
- **Case**：表示案例，它是客户问题或问题。
- **User**：表示您组织中的用户。
- **Task**：表示业务活动，如打电话或其他待办事项。
- **Event**：表示日历中的事件。

### Tooling API (开发者记录)

- **ApexClass**：表示 Apex 类的保存副本。
- **ApexTrigger**：表示 Apex 触发的保存副本。
- **ApexCodeCoverageAggregate**：表示 Apex 类或触发的聚合代码覆盖测试结果。
- **TraceFlag**：表示在指定日志级别触发 Apex 调试日志的跟踪标志。
- **EntityDefinition**：提供基于行的标准对象和自定义对象的元数据访问。
