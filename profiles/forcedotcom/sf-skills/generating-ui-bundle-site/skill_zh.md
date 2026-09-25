# 用于 React UI 组件的数字体验站点
在 Salesforce 上创建和配置数字体验站点，用于托管 React UI 组件。此功能会生成站点所需的最小基础设施——网络、自定义站点、数字体验配置、数字体验组件以及 `sfdc_cms__site` 内容类型——以便从 Salesforce 服务器提供 React 应用。

React 站点与标准 LWR 站点不同：它们不需要路由、视图、主题布局或品牌集。站点充当一个轻量级容器（`appContainer: true`），将渲染委托给由 `appSpace` 引用的 React UI 组件。

## 必须的属性
在生成任何元数据之前，必须解析所有五个属性。每个属性都有一个后备链——按顺序处理每个选项，直到找到值。

| 属性 | 格式 | 解析方法 |
|------|------|----------|
| **siteName** | `大驼峰式`（例如，`MyCommunity`） | 询问用户或从上下文派生 |
| **siteUrlPathPrefix** | `全部小写`（例如，`mycommunity`） | 用户提供，或将 siteName 转换为全部小写并仅包含字母数字字符 |
| **appNamespace** | 字符串 | `sfdx-project.json` 中的 `namespace` → `sf data query -q "SELECT NamespacePrefix FROM Organization" --target-org ${usernameOrAlias}` → 默认 `c` |
| **appDevName** | 字符串 | 项目中的 `UIBundle` 元数据 → `sf data query -q "SELECT DeveloperName FROM UIBundle" --target-org ${usernameOrAlias}` → 默认为 siteName |
| **enableGuestAccess** | 布尔值 | 询问用户未经过身份验证的访客用户是否可以访问站点 API → 默认 `false` |

`appNamespace` 和 `appDevName` 属性将站点连接到正确的 React 应用。如果这些属性配置错误，站点会部署但显示空白页面，因此请务必从实际项目数据中解析它们。

## 生成工作流程
### 第 1 步：解析所有必须的属性
在构建任何内容之前，确定所有五个属性值。使用上表中的解析策略，按顺序处理每个选项，直到找到值。

### 第 2 步：创建项目结构
使用 Salesforce 可用的元数据架构和字段上下文，为 `Network`、`CustomSite`、`DigitalExperienceConfig` 和 `DigitalExperienceBundle` 确保每个文件使用有效结构。

使用以下路径创建任何不存在的文件和目录：

| 元数据类型 | 路径 |
|----------|------|
| 网络 | `networks/{siteName}.network-meta.xml` |
| 自定义站点 | `sites/{siteName}.site-meta.xml` |
| 数字体验配置 | `digitalExperienceConfigs/{siteName}1.digitalExperienceConfig-meta.xml` |
| 数字体验组件 | `digitalExperiences/site/{siteName}1/{siteName}1.digitalExperience-meta.xml` |
| 数字体验（sfdc_cms__site） | `digitalExperiences/site/{siteName}1/sfdc_cms__site/{siteName}1/*` |

数字体验目录仅包含 `_meta.json` 和 `content.json`。不要在组件内创建除 `sfdc_cms__site` 之外的任何目录。

### 第 3 步：填充所有元数据字段
使用文档下方提供的默认模板。`{括号}` 内的值是解析属性引用——用第 1 步的实际值替换它们。

| 元数据类型 | 模板引用 |
|----------|----------|
| 网络 | [configure-metadata-network.md](docs/configure-metadata-network.md) |
| 自定义站点 | [configure-metadata-custom-site.md](docs/configure-metadata-custom-site.md) |
| 数字体验配置 | [configure-metadata-digital-experience-config.md](docs/configure-metadata-digital-experience-config.md) |
| 数字体验组件 | [configure-metadata-digital-experience-bundle.md](docs/configure-metadata-digital-experience-bundle.md) |
| 数字体验（sfdc_cms__site） | [configure-metadata-digital-experience.md](docs/configure-metadata-digital-experience.md) |

关于 URL 更新，请参阅 [update-site-urls.md](docs/update-site-urls.md)。

### 第 3 步的执行说明：加载和使用文档
- 代理必须在尝试填充元数据字段之前，读取第 3 步中引用的每个 `docs/*.md` 文件的全部内容。
- 使用平台提供的文件读取工具（例如，`read_file`）加载这些文件，然后使用第 1 步解析的属性，对 `{括号}` 内的值进行占位符替换。
- 要加载的文件：
  - `docs/configure-metadata-network.md`
  - `docs/configure-metadata-custom-site.md`
  - `docs/configure-metadata-digital-experience-config.md`
  - `docs/configure-metadata-digital-experience-bundle.md`
  - `docs/configure-metadata-digital-experience.md`
- 读取整个文件内容，将占位符（例如 `{siteName}`）替换为解析的值，然后使用扩展的模板填充元数据 XML/JSON 内容。

### 第 4 步：不要修改非模板化属性
不要修改 `Network`、`CustomSite`、`DigitalExperience`、`DigitalExperienceConfig` 或 `DigitalExperienceBundle` 元数据的默认属性值，这些值不是用 `{括号}` 包裹的变量表达的。

## 验证清单
在部署之前，请确认：

- [ ] 所有五个必须的属性已解析
- [ ] 所有元数据目录和文件按项目结构存在
- [ ] 所有元数据字段与第 3 步模板匹配，仅替换了 `{括号}`；没有添加或更改其他默认属性值
- [ ] `content.json` 中的 `appSpace` 与现有的 `UIBundle` 元数据记录匹配
- [ ] 部署验证成功：
```bash
sf project deploy validate --metadata Network CustomSite DigitalExperienceConfig DigitalExperienceBundle DigitalExperience --target-org ${usernameOrAlias}
```

## 常见工作流程

### 更新体验站点 URL

**使用场景**：当用户需要更新或更改站点 URL（urlPathPrefix）时。

**步骤**：
- [ ] 阅读 [update-site-urls.md](docs/update-site-urls.md) 了解三组件架构和 URL 更新工作流程
- [ ] 按照文档中的分步工作流程，一致地更新三个组件（DigitalExperienceConfig、网络、CustomSite）中的 URL
