## 何时使用此技能

当您需要执行以下操作时，请使用此技能：
- 为对象、网页或 Visualforce 页面创建标签页
- 向应用程序添加导航标签页
- 配置标签页的可见性和访问权限
- 排查与自定义标签页相关的部署错误

## 规格

# 自定义标签页元数据规范

## 概述
用于在 Salesforce 应用程序中导航到对象、网页内容或 Visualforce 页面的自定义标签页。

## 目的
- 提供到自定义对象的导航
- 链接到外部网页内容
- 访问 Visualforce 页面
- 组织应用程序导航

## 必要属性

### 核心标签页属性
- **customObject**：自定义对象标签页为 `true`，其他类型为 `false`。
- **motif**：标签页图标样式 — 选择与对象用途语义匹配的 motif。**请勿将相同的 motif 用于每个标签页**。
- **label**：显示名称（仅非对象标签页必需；对象标签页从对象继承标签名称）
- **url**：网页 URL（用于网页标签页）
- **page**：Visualforce 页面名称（用于 Visualforce 标签页）

### 严格元素允许列表 — 首先阅读此内容

**根元素必须始终为 `<CustomTab>`（不能是 `<Tab>`）。** XML 命名空间必须为 `xmlns="http://soap.sforce.com/2006/04/metadata"`。

仅允许下方列出的元素。**列表之外的任何元素都将导致部署错误。**

| 标签页类型 | 仅允许这些元素（不能有其他内容） |
|---|---|
| **对象标签页** | `<customObject>`（必需，设置为 `true`），`<motif>`（必需），`<description>`（可选） |
| **网页标签页** | `<customObject>`（必需，设置为 `false`），`<label>`（必需），`<motif>`（必需），`<url>`（必需），`<urlEncodingKey>`（必需，设置为 `UTF-8`），`<description>`（可选），`<frameHeight>`（可选） |
| **Visualforce 标签页** | `<customObject>`（必需，设置为 `false`），`<label>`（必需），`<motif>`（必需），`<page>`（必需），`<description>`（可选） |

### 禁止元素（每个都可能导致部署错误）
`<sobjectName>`，`<name>`，`<fullName>`，`<apiVersion>`，`<isHidden>`，`<tabVisibility>`，`<type>`，`<mobileReady>`，`<urlFrameHeight>`，`<urlType>`，`<urlRedirect>`，`<encodingKey>`，`<height>`，`<auraComponent>`

此外禁止：
- 对象标签页上的 `<label>`（对象标签页从自定义对象继承标签名称）
- 网页标签页上的 `<page>`（仅用于 Visualforce 标签页）
- 空元素，如 `<page></page>` 或 `<description></description>`
- 上述允许列表表中未列出的任何元素

## 标签页类型

### 对象标签页
- **用途**：导航到自定义或标准对象
- **文件名** 决定对象：`{ObjectApiName}.tab-meta.xml`（例如，`Space_Station__c.tab-meta.xml`）
- **必需元素**：`<customObject>true</customObject>` 和 `<motif>`
- **正确示例**（用于 Space_Station__c.tab-meta.xml）：
```xml
<?xml version="1.0" encoding="UTF-8"?>
<CustomTab xmlns="http://soap.sforce.com/2006/04/metadata">
    <customObject>true</customObject>
    <motif>Custom39: Telescope</motif>
</CustomTab>
```
- **正确示例**（用于 Supply__c.tab-meta.xml — 注意不同的 motif）：
```xml
<?xml version="1.0" encoding="UTF-8"?>
<CustomTab xmlns="http://soap.sforce.com/2006/04/metadata">
    <customObject>true</customObject>
    <motif>Custom98: Truck</motif>
</CustomTab>
```
- **错误示例** — 请勿添加 `<sobjectName>`、`<name>`、`<fullName>` 或 `<label>`：
```xml
<CustomTab xmlns="http://soap.sforce.com/2006/04/metadata">
    <sobjectName>Space_Station__c</sobjectName>  <!-- 部署错误 -->
    <label>Space Station</label>                  <!-- 对象标签页上的部署错误 -->
    <customObject>true</customObject>
    <motif>Custom57: Desert</motif>
</CustomTab>
```

### 网页标签页
- **用途**：链接到外部网站或网页应用程序
- **文件名**：使用描述性名称：`{TabName}.tab-meta.xml`（例如，`Knowledge_Base.tab-meta.xml`）
- **复制此精确模板** — 仅替换占位符值。**请勿添加、删除或重命名任何 XML 元素**：
```xml
<?xml version="1.0" encoding="UTF-8"?>
<CustomTab xmlns="http://soap.sforce.com/2006/04/metadata">
    <customObject>false</customObject>
    <description>REPLACE_WITH_DESCRIPTION</description>
    <frameHeight>600</frameHeight>
    <label>REPLACE_WITH_LABEL</label>
    <motif>REPLACE_WITH_MOTIF</motif>
    <url>REPLACE_WITH_URL</url>
    <urlEncodingKey>UTF-8</urlEncodingKey>
</CustomTab>
```
- **上述 7 个元素是网页标签页文件中唯一允许的元素。** 请勿添加任何其他元素。
- `<description>` 元素是可选的 — 如果不需要，可以删除它，但请勿添加任何其他内容。

### Visualforce 标签页
- **用途**：访问自定义 Visualforce 页面
- **文件名**：`{TabName}.tab-meta.xml`（例如，`Custom_Page_Tab.tab-meta.xml`）
- **必需元素**：`<customObject>false</customObject>`、`<label>`、`<motif>`、`<page>`
- **正确示例**：
```xml
<?xml version="1.0" encoding="UTF-8"?>
<CustomTab xmlns="http://soap.sforce.com/2006/04/metadata">
    <customObject>false</customObject>
    <label>Custom Page</label>
    <motif>Custom46: Computer</motif>
    <page>CustomPage</page>
</CustomTab>
```

## 标签页配置

### 标签页样式
- **默认**：使用标准标签页样式
- **自定义**：如有需要，可以指定自定义标签页样式

### 标签页可见性
- **默认**：对所有有访问权限的用户可见
- **自定义**：可针对特定用户配置

## 支持的应用程序
- **标准应用程序**：标准 Salesforce 应用程序中可用
- **自定义应用程序**：可包含在自定义应用程序中
- **社区应用程序**：社区应用程序中可用

## 集成点
- **对象关系**：链接到相关对象记录
- **网页内容**：外部网站集成
- **Visualforce 页面**：自定义页面功能
- **Lightning 组件**：现代组件集成

## 最佳实践
- 使用清晰、描述性的标签页名称
- 根据功能选择合适的标签页类型
- **为每个标签页选择独特且与上下文相关的 motif** — 不要将所有标签页都设置为相同的图标
- 考虑用户体验和导航流程
- 在不同应用程序中测试标签页功能
- 确保适当的权限和可见性设置
- 遵循一致的命名规范
- 对象标签页文件必须仅包含 `<customObject>true</customObject>` 和 `<motif>` — 除此之外不能有其他内容
- 网页标签页文件必须仅包含：`<customObject>false</customObject>`、`<label>`、`<motif>`、`<url>`、`<urlEncodingKey>`，以及可选的 `<description>`、`<frameHeight>` — 除此之外不能有其他内容
- 请勿包含 `<isHidden>`、`<tabVisibility>`、`<type>`、`<mobileReady>` 或空元素
