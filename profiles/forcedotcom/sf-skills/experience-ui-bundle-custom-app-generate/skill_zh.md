# 用于 React UI 套件的定制应用程序
创建和配置一个 Salesforce 定制应用程序，该应用程序托管 Lightning Experience 中的 React UI 套件。此技能生成定制应用程序元数据，以便应用程序出现在 Lightning 应用程序启动器中，并由内部用户访问。

定制应用程序与体验站点不同：它们不需要 Networks、CustomSite、DigitalExperienceConfig 或 DigitalExperienceBundle 元数据。定制应用程序充当一个薄的启动器入口，将渲染委托给 `uiBundle` 引用的 React UI 套件。

## 必须的属性
在生成任何元数据之前解决所有属性。每个属性都有一个回退链——按顺序处理每个选项，直到找到值。

| 属性 | 格式 | 如何解决 |
|----------|--------|----------------|
| **appName** | `lowercamelcase`（例如，`myInternalApp`） | 来自 `uiBundles/<name>/` 目录的 UI 套件名称 |
| **appNamespace** | 字符串 | `sfdx-project.json` 中的 `namespace` → `sf data query -q "SELECT NamespacePrefix FROM Organization" --target-org ${usernameOrAlias}` → 默认 `c` |
| **appLabel** | 人类可读的字符串 | 由用户提供，或通过将 camelCase 转换为 Title Case 从 appName 派生 |

`appNamespace` 和 `appName` 将定制应用程序连接到正确的 React UI 套件。在较新的 API 版本中，它使用 `<uiBundle>{appNamespace}__{appName}</uiBundle>`；在旧版本中，它使用 `<webApplication>{appName}</webApplication>`。如果设置错误，应用程序启动器条目存在但显示空白页面。工作流程的第 2 步确定要使用哪个字段。

## 生成工作流程
### 第 1 步：解决所有必须的属性
在构建任何内容之前确定所有属性值。使用上表中所示的解决策略。

### 第 2 步：查询 API 上下文（版本感知字段发现）
调用 `salesforce-api-context` MCP 工具来发现目标组织的 API 版本中哪些字段存在。这确保生成的元数据与用户的 Salesforce 版本兼容。

**必须的调用——使用 `metadataType` 参数完全按所示方式。不要替换 `detail` 参数或任何其他形状；`metadataType` 是此工具接受的唯一参数：**
1. `get_metadata_type_fields({ "metadataType": "CustomApplication" })` — 检查响应的字段列表中是否存在 `uiBundle` 字段
2. `get_metadata_type_fields({ "metadataType": "UIBundle" })` — 检查响应的字段列表中是否存在 `target` 字段

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

**注意：** `<sourceDir>` 由 `sfdx-project.json` 确定。读取 `packageDirectories[]` 并使用 `"default": true` 的条目；完整源目录是 `<path>/main/default`。如果没有默认值设置，请使用第一个条目。通常 `force-app/main/default`，但此路径是可配置的。

### 第 4 步：填充所有元数据字段
使用文档下方的默认模板。括号 `{}` 中的值是解决属性引用——用第 1 步的实际值替换它们。应用第 2 步的字段解决来确定要使用的 XML 元素。

| 元数据类型 | 模板引用 |
|--------------|-------------------|
| CustomApplication | [configure-metadata-custom-application.md](references/configure-metadata-custom-application.md) |

### 第 4 步的执行说明：加载和使用文档
- 代理必须在尝试填充元数据字段之前读取第 4 步中引用的 `references/*.md` 文件的全部内容。
- 读取文件的全部内容，将占位符（例如 `{appName}`）替换为解决后的值，然后使用扩展模板来填充元数据 XML 内容。
- 如果第 2 步确定应使用旧字段名称，则在生成的输出中用 `<webApplication>` 替换 `<uiBundle>`。

### 第 5 步：更新 UI 套件元 XML
此步骤编辑一个**现有**文件——它永远不会创建新文件。`UIBundle` 是一个包式元数据类型：其元 XML 通常位于其自己的文件夹中，位于 `uiBundles/{appName}/{appName}.uibundle-meta.xml`，与包的其他源文件（例如 `index.html`、`src/`）一起。一些较旧或手写的项目可能相反，将其放在扁平路径 `uiBundles/{appName}.uibundle-meta.xml`（无子文件夹）。

运行 `scripts/resolve-uibundle-path.sh "{appName}"`——它打印现有元 XML 的路径（优先考虑嵌套布局，回退到扁平布局）。就地编辑该确切文件；不要在另一个路径创建第二个文件或在此次技能中将其迁移到不同的布局。

如果第 2 步确认 `UIBundle` 上存在 `target` 字段，请将 `<target>CustomApplication</target>` 添加到该文件的现有 `<UIBundle>` 元素内部，保留每个其他现有元素和值未受影响（如果该字段在组织的 API 版本中不存在，则完全跳过此步骤）。

**不要：**
- 创建新的 `.uibundle-meta.xml` 文件
- 当一个已经存在（嵌套或扁平）时创建第二个 `.uibundle-meta.xml` 文件——就地编辑现有的文件，无论它在哪里
- 在添加 `<target>` 的同时，保留原始的 `uiBundles/{appName}/{appName}.uibundle-meta.xml`（或 `uiBundles/{appName}.uibundle-meta.xml`，如果这是现有布局）未修改

此技能生成的或修改的唯一文件是 `applications/{appName}.app-meta.xml`（新）和现有的 `{appName}.uibundle-meta.xml`（就地编辑，仅当 `<target>` 适用时）。输出中出现的任何其他与 UI 套件相关的文件都是错误。

以下是完全更新后的文件（位于 `uiBundles/{appName}/{appName}.uibundle-meta.xml`，或如果这是现有布局的扁平路径）的示例——这说明了现有文件的最终状态，而不是要创建的新文件：

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
不要修改 `CustomApplication` 元数据的任何默认属性值，这些值不是用括号 `{}` 包裹的变量表示的。

## 验证检查清单
在部署之前确认：

- [ ] 所有必须的属性已解决
- [ ] 已查询 API 上下文以确定可用字段（第 2 步）
- [ ] `applications/{appName}.app-meta.xml` 存在且内容正确
- [ ] 套件引用字段与组织的 API 版本匹配（`<uiBundle>` 或 `<webApplication>`）
- [ ] 如果支持 `target` 字段：**现有的** `{appName}.uibundle-meta.xml`（嵌套在 `uiBundles/{appName}/`，或扁平在 `uiBundles/`，无论哪个已经存在）包含 `<target>CustomApplication</target>`
- [ ] 没有创建额外的 `.uibundle-meta.xml` 文件——恰好一个 `{appName}.uibundle-meta.xml` 存在，在它已经存在的路径上
- [ ] 部署验证成功：
```bash
sf project deploy validate --metadata CustomApplication UIBundle --target-org ${usernameOrAlias}
```
