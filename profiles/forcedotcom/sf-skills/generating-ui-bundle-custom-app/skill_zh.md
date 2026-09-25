# 用于 React UI 套件的定制应用程序
创建和配置一个 Salesforce 定制应用程序，该应用程序托管 Lightning Experience 中的 React UI 套件。此技能生成定制应用程序元数据，以便应用程序出现在 Lightning 应用程序启动器中，并由内部用户访问。

定制应用程序与体验站点不同：它们不需要 Networks、CustomSite、DigitalExperienceConfig 或 DigitalExperienceBundle 元数据。定制应用程序充当一个薄的启动器入口，将渲染委托给 `uiBundle` 引用的 React UI 套件。

## 必须的属性
在生成任何元数据之前解决所有属性。每个属性都有一个后备链——按顺序处理每个选项，直到找到值。

| 属性 | 格式 | 如何解决 |
|----------|--------|----------------|
| **appName** | `lowercamelcase`（例如，`myInternalApp`） | 来自 `uiBundles/<name>/` 目录的 UI 套件名称 |
| **appNamespace** | 字符串 | `sfdx-project.json` 中的 `namespace` → `sf data query -q "SELECT NamespacePrefix FROM Organization" --target-org ${usernameOrAlias}` → 默认 `c` |
| **appLabel** | 人类可读的字符串 | 由用户提供，或通过将 camelCase 转换为 Title Case 从 appName 派生 |

`appNamespace` 和 `appName` 将定制应用程序连接到正确的 React UI 套件。在较新的 API 版本中，它使用 `<uiBundle>{appNamespace}__{appName}</uiBundle>`；在旧版本中，它使用 `<webApplication>{appName}</webApplication>`。如果弄错，应用程序启动器条目存在但显示空白页面。工作流程的第 2 步确定使用哪个字段。

## 生成工作流程
### 第 1 步：解决所有必须的属性
在构建任何内容之前确定所有属性值。使用上表中所示的解决策略。

### 第 2 步：查询 API 上下文（版本感知字段发现）
调用 `salesforce-api-context` MCP 工具来发现目标组织的 API 版本中哪些字段存在。这确保生成的元数据与用户的 Salesforce 版本兼容。

**必须的调用：**
1. 调用 `get_metadata_type_fields` 为 `CustomApplication` — 检查 `uiBundle` 字段是否存在
2. 调用 `get_metadata_type_fields` 为 `UIBundle` — 检查 `target` 字段是否存在

**基于 API 响应的字段解决：**

| 字段检查 | 存在时 | 缺失时（旧 API 版本） |
|-------------|-----------|-------------------------------|
| `CustomApplication.uiBundle` | 使用 `<uiBundle>{appNamespace}__{appName}</uiBundle>` | 使用 `<webApplication>{appName}</webApplication>`（无命名空间） |
| `UIBundle.target` | 使用 `<target>CustomApplication</target>` | 完全省略 `<target>` 元素 |

如果 `salesforce-api-context` 在真实尝试后不可用，则回退到较新的字段名称（`uiBundle` + `target`）。

### 第 3 步：创建项目结构
创建任何不存在的文件和目录：

| 元数据类型 | 路径 |
|--------------|------|
| CustomApplication | `<sourceDir>/applications/{appName}.app-meta.xml` |

**注意：** `<sourceDir>` 从 `sfdx-project.json` 确定。读取 `packageDirectories[]` 并使用 `"default": true` 的条目；完整源目录是 `<path>/main/default`。如果没有默认值设置，则使用第一个条目。通常 `force-app/main/default`，但此路径是可配置的。

### 第 4 步：填充所有元数据字段
使用文档下方的默认模板。`{braces}` 中的值是解决属性引用——用第 1 步的实际值替换它们。应用第 2 步的字段解决来确定使用哪些 XML 元素。

| 元数据类型 | 模板引用 |
|--------------|-------------------|
| CustomApplication | [configure-metadata-custom-application.md](docs/configure-metadata-custom-application.md) |

### 第 4 步的执行说明：加载和使用文档
- 代理必须在尝试填充元数据字段之前读取第 4 步中引用的 `docs/*.md` 文件的全部内容。
- 读取完整文件，将占位符（例如 `{appName}`）替换为解决值，然后使用扩展模板来填充元数据 XML 内容。
- 如果第 2 步确定适用旧字段名称，则在生成输出中用 `<webApplication>` 替换 `<uiBundle>`。

### 第 5 步：更新 UI 套件 Meta XML
如果第 2 步确认 `UIBundle` 上存在 `target` 字段，则向 `.uibundle-meta.xml` 文件添加 `<target>CustomApplication</target>`（如果组织的 API 版本中不存在该字段则跳过）：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<UIBundle xmlns="http://soap.sforce.com/2006/04/metadata">
    <masterLabel>{appName}</masterLabel>
    <description>A Salesforce UI Bundle.</description>
    <isActive>true</isActive>
    <version>1</version>
    <target>CustomApplication</target>
</UIBundle>
```

### 第 6 步：不要修改非模板化属性
不要修改 `CustomApplication` 元数据中不是用 `{braces}` 括起来的变量形式的默认属性值。

## 验证检查清单
在部署之前确认：

- [ ] 所有必须的属性已解决
- [ ] 已查询 API 上下文以确定可用字段（第 2 步）
- [ ] `applications/{appName}.app-meta.xml` 存在且内容正确
- [ ] 套件引用字段与组织的 API 版本匹配（`<uiBundle>` 或 `<webApplication>`）
- [ ] 如果 `target` 字段受支持：`.uibundle-meta.xml` 包含 `<target>CustomApplication</target>`
- [ ] 部署验证成功：
```bash
sf project deploy validate --metadata CustomApplication UIBundle --target-org ${usernameOrAlias}
```
