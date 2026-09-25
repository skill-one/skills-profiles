# Salesforce 元数据 API 技能

此技能提供所有 **604 个 Salesforce 元数据 API 类型** 的全面文档。使用此技能在 Salesforce DX 项目中创建、理解和修改 Salesforce 元数据 XML 文件。

## 概述

Salesforce 元数据 API 允许您检索、部署、创建、更新或删除组织的自定义设置。此技能为您提供每个元数据类型的详细文档，包括：

- 字段定义和数据类型
- 必填字段与可选字段
- WSDL 模式定义
- 示例 XML 结构
- 文件命名约定
- Salesforce DX 项目中的目录位置

## 如何使用此技能

### 关键：按部分消费

**始终仅从 JSON 文件中消费您需要的特定部分，而不是整个文件。**

**关键：对于 `assets/metadata_api/*.json` 文件，始终使用 `jq` 或程序化 JSON 解析来提取您需要的特定部分。** 不要通过 `Read`、`cat`、`read_file` 或任何其他注入完整文件的工具加载这些文件——它们包含冗长的 WSDL 段和其他浪费 60-80% 令牌的部分。（使用 `Read` 加载此 SKILL.md 或索引表等小文件是 fine；该规则专门适用于大型元数据类型 JSON 文件。）

每个 JSON 文件包含多个部分（字段、描述、wsdl_segment 等）。大多数用例只需要 1-2 个部分：

- **对于字段定义**：仅加载 `fields` 部分
- **对于理解目的**：仅加载 `description` 部分
- **对于 XML 示例**：仅加载 `declarative_metadata_sample_definition` 部分
- **默认跳过**：`wsdl_segment`（冗长模式）、`file_information`、`directory_location`

这可减少每个文件的令牌消耗 **60-80%。**

### 快速入门

要获取特定元数据类型的信息：

1. **按部分**（最佳）："仅从 CustomObject.json 显示 'fields' 部分"
2. **多个部分**："显示 Flow.json 的 'fields' 和 'description' 部分"
3. **避免加载整个文件**：不要询问 "CustomObject 元数据类型" - 指定部分

### 示例查询（按部分）

**推荐：**
- "仅从 CustomObject.json 显示 'fields' 部分"
- "Profile.json 的 'fields' 部分中有哪些字段？"
- "从 Flow.json 加载 'description' 和 'fields' 部分"
- "给我仅 ApexClass.json 的 'declarative_metadata_sample_definition'"

**避免：**
- "显示 CustomObject 元数据类型"（过于宽泛 - 整个文件）
- "加载 CustomObject.json"（包含不必要的 WSDL 和其他部分）

## JSON 文件结构

每个元数据类型都存储为 `assets/metadata_api/` 中的 JSON 文件，结构如下：

```json
{
  "sections": ["title", "description", "fields", "wsdl_segment", ...],
  "title": "MetadataTypeName - Metadata API",
  "description": "元数据类型的纯文本描述。",
  "fields": {
    "fieldName": {
      "type": "string",
      "description": "字段描述",
      "required": true
    }
  },
  "file_information": ".object",
  "directory_location": "objects",
  "wsdl_segment": "<xsd:complexType>...</xsd:complexType>",
  "declarative_metadata_sample_definition": [
    {
      "description": "示例描述",
      "code": "<?xml version=\"1.0\"?>\n<MetadataType>...\n</MetadataType>"
    }
  ]
}
```

> **注意**：字符串值（`title`、`description`、`file_information`、`directory_location`、`wsdl_segment`）存储为**纯文本**——没有 Markdown 标题（`#`/`##`）或代码分隔符。`file_information` 仅包含文件后缀（例如 `.object`，`.ai`），`directory_location` 仅包含 SFDX 文件夹名称（例如 `objects`、`aiApplications`）。

### 可用部分

`sections` 数组指示每个文件中存在哪些顶级键。常见部分包括：

- `title`：元数据类型名称和标题
- `description`：元数据类型代表什么
- `fields`：该类型的自身字段，包括类型和描述
- `sub_types`：（复合类型仅）一个映射，其中键是引用的子类型名称，值是该子类型的字段，例如 `Flow` → `sub_types.FlowActionCall`
- `file_information`：文件命名约定和扩展名
- `directory_location`：SFDX 项目中文件存储的位置
- `wsdl_segment`：来自 WSDL 的 XML 模式定义
- `declarative_metadata_sample_definition`：示例 XML 代码

某些元数据类型具有特定于其功能的附加部分。请参阅 [索引表](references/metadata_index_table.md) 获取完整分解。

> **更多细节**：关于 *为什么* 令牌优化很重要、示例用法、常见工作流、完整部分术语表和版本支持说明位于 [`references/usage_guide.md`](references/usage_guide.md)。仅在需要时使用 `Read` 工具加载它。

## 令牌优化策略

**关键**：为最小化令牌使用和成本：
1. 仅加载您需要的特定元数据类型，而不是完整语料库
2. **从每个文件加载特定部分，而不是整个文件**

### 按部分加载（最佳实践）

**关键警告**：**不要**使用 `read_file` 工具（或任何读取整个文件的工具）在这些 JSON 文件上！

`read_file` 将整个文件内容加载到您的上下文中，这会破坏按部分消费的目的。您将浪费 60-80% 的令牌预算来加载不必要的 WSDL 段和冗长部分。（使用 `Read` 加载此 SKILL.md 或索引表等小文件是 fine —— 该规则仅适用于大型元数据类型 JSON 文件。）

**方法**：使用代码程序化解析 JSON 文件，并仅提取您需要的部分，而不是使用读取整个文件的工具。

**可用工作示例**：

我们提供多种语言中的完整、工作示例：

- **Python**：[`examples/python_section_loading.py`](examples/python_section_loading.py) - 显示 `json.load()` 与部分提取
- **JavaScript/Node.js**：[`examples/javascript_section_loading.js`](examples/javascript_section_loading.js) - 显示 `JSON.parse()` 与部分提取
- **Bash + jq**：[`examples/bash_section_loading.sh`](examples/bash_section_loading.sh) - 显示 `jq` 命令行 JSON 处理

请参阅 [`examples/README.md`](examples/README.md) 获取完整文档和使用说明。

**快速模式**（根据您的语言调整）：
1. 读取 JSON 文件
2. 解析为数据结构
3. 仅提取您需要的部分（例如，`fields`、`description`）
4. 忽略冗长部分（`wsdl_segment`、`declarative_metadata_sample_definition`）

### 不要做什么

**绝对不要**在这些 JSON 文件上使用 `read_file` 工具：
```text
read_file assets/metadata_api/CustomObject.json  # 将整个文件加载到上下文中！
read_file assets/metadata_api/Flow.json          # 浪费 60-80% 令牌！
```

**绝对不要**加载所有文件：
```text
read_file assets/metadata_api/*.json  # 这会加载 ~15MB 的数据！
```

**令牌影响**：
- 按部分：**50-200 令牌** 每个元数据类型
- 整个文件：**500-2000 令牌** 每个元数据类型
- **节省**：每个文件 60-80%

### 何时加载多个类型

- **相关类型**：CustomObject + CustomField + ValidationRule
- **权限集**：Profile + PermissionSet + PermissionSetGroup
- **UI 组件**：Layout + CompactLayout + QuickAction
- **自动化**：Flow + WorkflowRule + ApexTrigger

### 何时加载特定部分（强烈推荐）

许多元数据类型具有大型 WSDL 段或广泛的字段列表。**始终从每个 JSON 文件加载您需要的特定部分，而不是消费整个文件**：

1. **首先检查可用部分**：通过读取仅 `sections` 数组来检查
2. **提取您需要的部分**（例如，`fields` 用于字段定义，`description` 用于概述）
3. **跳过 WSDL 段**，除非您需要模式验证
4. **跳过 declarative_metadata_sample_definition**，除非您需要完整的 XML 示例

这种方法可减少每个文件的令牌消耗 **60-80%**，方法是排除冗长的 WSDL 定义和冗长的示例。

## 使用此技能的概念性方法

### 第 1 步：确定您的需求

问自己：
- 我正在尝试构建或修改什么？
- 我正在使用哪些 Salesforce 元数据类型？
- **我需要哪些特定信息？**
  - 仅字段定义？→ 加载 `fields` 部分
  - 了解它做什么？→ 加载 `description` 部分
  - XML 示例？→ 加载 `declarative_metadata_sample_definition` 部分
  - 模式验证？→ 加载 `wsdl_segment` 部分（很少需要）

### 第 2 步：找到正确的类型

使用以下方法之一：
- **直接引用**：如果您知道类型名称（例如，"CustomObject"）
- **索引搜索**：检查 `references/metadata_index_table.md` 以查找相关类型
- **常见类型**：请参阅下面的“快速参考：常见元数据类型”部分

### 第 3 步：选择性加载（按部分）

**按部分加载决策树**：

```text
需要字段定义吗？
  → 仅加载 'fields' 部分 (~50-200 令牌)

需要了解类型做什么？
  → 仅加载 'description' 部分 (~20-100 令牌)

需要 XML 结构示例？
  → 仅加载 'declarative_metadata_sample_definition' (~100-300 令牌)

需要所有三个？
  → 加载 'fields' + 'description' + 'declarative_metadata_sample_definition'
  → 仍然跳过 'wsdl_segment'、'file_information'、'directory_location'
  → 节省：~60-70% 相对于加载整个文件

需要模式验证？
  → 仅加载 'wsdl_segment'（这是冗长的）
```

**请求格式**：
- **单个部分**（最佳）："仅从 ApexClass.json 显示 'fields' 部分"
- **多个部分**："加载 'fields' 和 'description' 从 CustomObject.json"
- **跳过冗长部分**：不要加载 `wsdl_segment`，除非明确需要

### 第 4 步：应用于您的代码

使用加载的信息来：
- 创建新的元数据 XML 文件
- 理解项目中的现有文件
- 验证字段名称和类型
- 使用正确的命名空间生成正确的 XML 结构

## 文件位置

所有元数据类型 JSON 文件都位于：

```text
assets/metadata_api/
├── CustomObject.json
├── Flow.json
├── ApexClass.json
├── Profile.json
└── ... (600 多个文件)
```

### 路径解析

使用此技能时，文件引用如下：
- 绝对路径：`assets/metadata_api/CustomObject.json`
- 相对于技能根目录：`./assets/metadata_api/CustomObject.json`

技能将根据工作目录自动解析路径。

## 元数据文件生成要求

在生成 Salesforce 元数据 XML 文件时，请遵循以下要求，以确保有效的可部署文件。

### XML 结构要求

所有元数据文件必须：

1. **包含 XML 声明**：
   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   ```

2. **使用正确的命名空间**：
   ```xml
   <CustomObject xmlns="http://soap.sforce.com/2006/04/metadata">
   ```

3. **根元素与元数据类型匹配**：
   - CustomObject → `<CustomObject>`
   - Flow → `<Flow>`
   - Profile → `<Profile>`
   - 等等。

### 命名空间声明

命名空间是**必需的**，必须完全为：
```text
http://soap.sforce.com/2006/04/metadata
```

**正确**：
```xml
<CustomObject xmlns="http://soap.sforce.com/2006/04/metadata">
```

**不正确**：
```xml
<CustomObject>  <!-- 缺少命名空间 -->
<CustomObject xmlns="http://salesforce.com/metadata">  <!-- 错误的命名空间 -->
```

### 必填字段与可选字段

每个元数据类型具有不同的字段要求：

- **模式必填**（JSON 中的 `required: true`）：WSDL 将字段标记为必填。
- **实际上必填**（未标记但实际上需要）：在许多情况下，WSDL 标记的必填字段比实际作者合同要求的字段少。CustomObject 是规范示例——JSON 仅将 `externalDataSource`、`externalName`、`nameField` 标记为 `required: true`（前两个是仅外部对象的小怪癖），但正常的 `__c` CustomObject 还需要 `label`、`pluralLabel`、`deploymentStatus` 和 `sharingModel` 才能部署。始终与 `declarative_metadata_sample_definition` 示例交叉检查。
- **条件必填**：某些字段仅在启用特定功能时才必填。
- **可选**：大多数字段如果不需要可以省略。

**CustomObject 的示例**（注意：实际编写需要比 `required: true` 标记的更多）：
```json
{
  "fields": {
    "nameField": {
      "type": "CustomField",
      "description": "自定义对象的名称字段",
      "required": true
    },
    "label": {
      "type": "string",
      "description": "自定义对象的标签（对于正常的 __c 对象实际上需要）",
      "required": false
    },
    "sharingModel": {
      "type": "SharingModel (枚举)",
      "description": "对象的共享模型（对于正常的 __c 对象实际上需要）",
      "required": false
    },
    "enableHistory": {
      "type": "boolean",
      "description": "启用字段历史跟踪",
      "required": false
    }
  }
}
```

### 验证提示

部署之前：

1. **验证 XML 语法**：确保格式良好的 XML（匹配标签，正确的嵌套）
2. **检查必填字段**：验证所有必填字段都存在
3. **验证命名空间**：命名空间必须完全匹配
4. **测试字段类型**：确保字段值匹配预期类型
5. **使用 Salesforce CLI**：运行 `sf project deploy validate` 以捕获错误

> **更多细节**：字段类型→XML 映射表，文件命名/两文件/子类型约定，以及完整格式良好文件示例位于 [`references/usage_guide.md`](references/usage_guide.md)。

## 重复和歧义类型名称

一些元数据 API 类型名称也作为 Enterprise/Data API 或 Tooling API 对象名称存在。示例包括 ApexClass、ApexTrigger、CustomField、CustomObject、EmailTemplate、Layout、Profile、PermissionSet、RecordType、StaticResource、WebLink、ValidationRule 和 Flow。

当提示存在歧义时（例如，"告诉我关于 Profile" 或 "ApexClass 上有哪些字段"），询问用户是否想要：

1. **元数据 API** XML 结构用于源代码/部署编写（此技能，例如 `.profile-meta.xml`、`.cls-meta.xml`）。
2. **Enterprise/Data API** 运行时 sObject/记录引用（目前没有专用技能——回退到 Salesforce API 家族路由器）。
3. **Tooling API** 开发者工具记录引用（目前没有专用技能——回退到 Salesforce API 家族路由器）。

解决大多数歧义而不需要询问的启发式方法：

- 提及 `package.xml`、`force-app/`、`sfdx`、`.meta.xml`、"部署"、"检索"、"编写"、"蓝图"、"模板"、"类定义" 或"权限"（在部署意义上）→ 元数据 API（此技能）。
- "X 上有哪些字段" / "哪些列" / "DML" / "SOQL" / "查询" / "REST" / "sObject" / "记录" / "运行时" → Enterprise/Data 或 Tooling API（其他技能）。
- Tooling 特定信号："Tooling API"、`ApexCodeCoverage`、`EntityDefinition`、`TraceFlag`、"代码覆盖率"、"编译错误"、"SymbolTable"、调试日志记录 → Tooling API。

**无信号时的默认规则**：如果提示没有上述信号，并且此技能（`platform-metadata-api-context-get`）直接由名称调用，则默认为元数据 API 解释，并明确告知用户假设（例如，"解释为 `.cls-meta.xml` 编写用的元数据 API 类型；如果指的是 Tooling API 记录或 Enterprise/Data sObject，请告诉我"）。技能调用上下文本身是作者/部署意图的信号。

## 故障排除

### 文件未找到

**问题**：无法找到元数据类型文件

**解决方案**：
- 文件名是**区分大小写的大小写字母**，没有分隔符（例如，`CustomObject.json`，不是 `customobject.json`、`Custom_Object.json` 或 `Custom-Object.json`）。
- 在声明"未找到"之前，请咨询 `references/metadata_index_table.md`。使用以下两步恢复算法针对索引：
  1. **规范化并子字符串**（处理大小写+分隔符变体）：删除非字母数字字符并将查询和每个索引条目都转换为小写，然后查找子字符串匹配。解决：`customobject`、`Custom_Object`、`Custom-Object` → `CustomObject`。
  2. **错过时，模糊匹配**（处理缺少字母的拼写错误）：使用 `difflib.get_close_matches(query_normalized, index_normalized, n=3, cutoff=0.7)` 或 Levenshtein 距离 ≤ 2。解决：`customfeld` → `CustomField`，`apxclass` → `ApexClass`。纯子字符串匹配无法恢复字符删除。
- **多命中破局**：当规范化并子字符串返回多个匹配项时（例如，`customobject` 匹配 `CustomObject` 和 `CustomObjectTranslation`），优先选择规范化长度**等于**规范化查询长度的条目；否则优先选择最短的匹配项。
- 某些类型具有意外的命名约定（没有下划线，没有空格，没有缩写如 "OAuth"）；索引是事实来源。

### SOAP 信封/标题类型（设计为精简）

有两种相关的模式需要识别：

1. **结果类型**（`AsyncResult`、`SaveResult`、`DeleteResult`、`UpsertResult`、`Error`、`DescribeMetadataResult` 等）——`fields` 为空且 `wsdl_segment` 被填充。这些是 SOAP 响应包装器；它们的模式完全存在于 `wsdl_segment` 中。如果您需要它们的结构，请消费该部分。它们不是可部署的源文件。
2. **SOAP 请求标题**（`AllOrNoneHeader`、`SessionHeader`、`CallOptions`、`DebuggingHeader`、`OwnerChangeOptions` 等）——`fields` 包含 1-2 个最小条目，没有 `wsdl_segment`。这些配置 SOAP 请求行为；它们是调用时选项，不是您编写或部署的元数据。

在这两种情况下，精简的 JSON 输出都是正确的。不要尝试编写 `.AsyncResult-meta.xml`——这些类型没有源文件形式。

### 缺少部分

**问题**：预期部分未在 JSON 文件中

**解决方案**：
- 检查 `sections` 数组以查看可用内容
- 并非所有元数据类型都具有所有部分
- 某些部分是类型特定的（索引表中注明）

### 不完整字段信息

**问题**：字段定义缺少详细信息

**解决方案**：
- 检查 `wsdl_segment` 以获取完整的模式定义
- 某些字段具有在 WSDL 中定义的复杂类型
- 与 Salesforce 文档交叉参考以获取枚举

### 跟随子类型指针（例如，`ProfileObjectPermissions[]`）

当 `fields` 部分给出像 `ProfileObjectPermissions[]` 或 `LayoutItem[]` 或 `ApprovalStep[]` 这样的复杂类型名称时，该嵌套类型的子字段不在 `fields` 部分——它们存在于该复杂类型的 `wsdl_segment` 中。此技能的"默认跳过 wsdl_segment"规则是为了在简单字段路径上节省令牌；对于嵌套类型，您需要深入挖掘。

**示例**——查找 Profile 上 `objectPermissions` 的子字段：

```bash
# 1. 从字段部分获取字段类型名称
jq '.fields.objectPermissions' assets/metadata_api/Profile.json
# → {"type": "ProfileObjectPermissions[]", ...}

# 2. 使用 grep -A 仅获取匹配的 complexType
jq -r '.wsdl_segment' assets/metadata_api/Profile.json   | grep -A 30 'complexType name="ProfileObjectPermissions"'
```

`grep -A N` 窗口将令牌成本保持在 ~150 令牌，而不是加载整个 `wsdl_segment`（在大型类型上可以是 5K+ 令牌）。任何时候 `fields` 返回 `Foo[]` 类型且您需要 Foo 的子字段时，请使用此模式。

### XML 生成错误

**问题**：生成的 XML 无法通过验证

**解决方案**：
- 验证命名空间完全为：`http://soap.sforce.com/2006/04/metadata`
- 检查所有必填字段都存在
- 确保字段值匹配预期类型
- 验证 XML 语法（关闭标签，正确嵌套）

### 部署失败

**问题**：元数据文件无法部署

**解决方案**：
- 首先运行 `sf project deploy validate`
- 检查 Salesforce API 版本兼容性
- 验证文件命名匹配约定
- 确保目录结构匹配 SFDX 格式

## 快速参考：常见元数据类型

这里是最常用的元数据类型：

- **CustomObject**：定义自定义 sObject 的模式，包括字段、关系和设置
- **Flow**：使用可视化画布上的元素和连接器自动化业务流程
- **ApexClass**：编译的 Apex 服务器端类；包括主体、API 版本和状态
- **ApexTrigger**：在特定 sObject 上执行 DML 事件的 Apex 代码
- **Profile**：控制对象/字段权限、应用程序可见性和登录设置的用户配置文件
- **PermissionSet**：授予用户的附加权限集，独立于其配置文件
- **CustomField**：定义标准或自定义对象上的字段，包括类型、picklist 值和公式
- **Layout**：控制记录详情/编辑页面上字段和关联列表的排列方式
- **ValidationRule**：通过防止在公式条件为真时保存来强制执行数据质量
- **ApexPage**：Visualforce 页面定义，包括控制器引用和标记
- **ApexComponent**：可嵌入页面中的可重用 Visualforce 组件
- **CustomTab**：指向自定义对象、Visualforce 页面或 Web URL 的标签
- **CustomApplication**：定义应用程序的标签栏、导航项和品牌
- **LightningComponentBundle**：包括 JS、HTML 和元数据描述符的 LWC 包
- **AuraDefinitionBundle**：包含组件、控制器、帮助文件（Aura（Lightning）组件包）
- **StaticResource**：可从 Visualforce 和 LWC 访问的上传文件（JS、CSS、图像、ZIP）
- **EmailTemplate**：用于工作流规则、Process Builder 或 Apex 的电子邮件模板
- **Report**：包括过滤器、分组和列的已保存报告定义
- **Dashboard**：由仪表板组件支持的报告集合

有关所有元数据类型的完整列表，请参阅 [索引表](references/metadata_index_table.md)。
