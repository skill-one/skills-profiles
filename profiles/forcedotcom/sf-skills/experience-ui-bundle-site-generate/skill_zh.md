# 用于 React UI 打包的数字体验站点
在 Salesforce 上创建和配置数字体验站点，以托管 React UI 打包。此技能会生成站点所需的最小基础设施——网络、自定义站点、数字体验配置、数字体验打包和 `sfdc_cms__site` 内容类型——以便 React 应用可以从 Salesforce 提供。

React 站点与标准 LWR 站点不同：它们不需要路由、视图、主题布局或品牌集。站点充当一个轻量级容器（`appContainer: true`），将渲染委托给由 `appSpace` 引用的 React UI 打包。

## 必要属性
在生成任何元数据之前，解决所有五个属性。每个属性都有一个后备链——按顺序检查每个选项，直到找到值。

| 属性 | 格式 | 如何解决 |
|------|------|----------|
| **siteName** | `UpperCamelCase`（例如，`MyCommunity`） | 询问用户或从上下文中派生 |
| **siteUrlPathPrefix** | `全部小写`（例如，`mycommunity`） | 用户提供，或将 siteName 转换为全部小写并仅包含字母数字字符 |
| **appNamespace** | 字符串 | `sfdx-project.json` 中的 `namespace` → `sf data query -q "SELECT NamespacePrefix FROM Organization" --target-org ${usernameOrAlias}` → 默认 `c` |
| **appDevName** | 字符串 | 项目中的 `UIBundle` 元数据 → `sf data query -q "SELECT DeveloperName FROM UIBundle" --target-org ${usernameOrAlias}` → 默认为 siteName |
| **enableGuestAccess** | 布尔值 | 询问用户未经过身份验证的访客用户是否可以访问站点 API → 默认 `false` |

`appNamespace` 和 `appDevName` 属性记录了预期的 UIBundle 绑定，用于**未来的后续更新**；它们在初始站点创建时**不会**替换到 `appSpace` 中。在初始创建时，`sfdc_cms__site` `content.json` 中的 `appSpace` 始终为 `""`——有关原因和后续流程，请参阅 [configure-metadata-digital-experience.md](references/configure-metadata-digital-experience.md)。

### 语言属性
此技能始终与 `sfdc_cms__site` 一起发出 `sfdc_cms__languageSettings`。为每个站点解决 `defaultLocale`（默认为 `en_US`）；仅在用户请求超出默认语言之外的其他语言时解决 `languages`。

| 属性 | 格式 | 如何解决 |
|------|------|----------|
| **defaultLocale** | `xx` 或 `xx_YY`（例如，`en`，`en_US`） | 询问用户 → 默认 `en_US` |
| **languages** | `{label, locale}` 列表 | 仅当用户请求多种语言、区域设置、国际化或翻译支持时：询问站点支持的其他语言。未请求时，语言设置内容仅声明解析的 `defaultLocale` 作为单语言条目。 |

内容项文件夹名称（`languages`）、`title`（`LanguageContent`）和 `urlName`（`languagecontent`）是 Experience Builder 自动默认的固定值——它们**不是**用户创建的。请参阅 [configure-metadata-language-settings.md](references/configure-metadata-language-settings.md)。

## 预检查：目标组织发布（仅限多语言）
`sfdc_cms__languageSettings` 内容类型仅在 Salesforce 发布 264（API **v68.0** 或更高版本）上接受多语言声明。简化为单区域设置 `en_US` 声明的站点适用于任何组织，并且不需要此检查。

当用户请求多种语言时，在写入任何元数据之前，验证目标组织的最大支持的 API 版本。`sf api request rest` 直接在实例上命中 `/services/data/` 并在传输层处理身份验证，因此组织的真实上限会返回，而无需任何访问令牌进入此脚本的上下文中。

```bash
MAX_API=$(sf api request rest "/services/data/" --target-org "${usernameOrAlias}" \
          | jq -r '[.[].version | tonumber] | max')

awk -v v="$MAX_API" 'BEGIN{ exit !(v+0 >= 68.0) }' \
  || { echo "ERROR: multi-language site containers require Salesforce Release 264 (API v68.0+). Target org's maximum supported API version is v${MAX_API}. Retarget to a Release 264+ org, or reduce the site to a single-locale (en_US) declaration." >&2; exit 1; }
```

如果检查失败，则不要写入元数据。向用户报告版本不匹配并停止。

## 生成工作流
### 第 1 步：解决所有必要属性
在构建任何内容之前，确定五个必要属性和 `defaultLocale` 语言属性的值。使用上表中列出的解决策略，按顺序检查每个选项，直到找到值。仅在用户请求多种语言时解决 `languages` 属性——在这种情况下，在继续到第 2 步之前，请运行上述 [预检查](#pre-flight-target-org-release-multi-language-only)。

### 第 2 步：创建项目结构
使用 Salesforce 可用的元数据模式和字段上下文，为 `Network`、`CustomSite`、`DigitalExperienceConfig` 和 `DigitalExperienceBundle` 确保每个文件使用有效结构。

使用以下路径创建任何不存在的文件和目录：

| 元数据类型 | 路径 |
|----------|------|
| 网络 | `networks/{siteName}.network-meta.xml` |
| 自定义站点 | `sites/{siteName}.site-meta.xml` |
| 数字体验配置 | `digitalExperienceConfigs/{siteName}1.digitalExperienceConfig-meta.xml` |
| 数字体验打包 | `digitalExperiences/site/{siteName}1/{siteName}1.digitalExperience-meta.xml` |
| 数字体验（sfdc_cms__site） | `digitalExperiences/site/{siteName}1/sfdc_cms__site/{siteName}1/*` |
| 数字体验（sfdc_cms__languageSettings） | `digitalExperiences/site/{siteName}1/sfdc_cms__languageSettings/languages/*` |

每个 DigitalExperience 内容类型目录仅包含 `_meta.json` 和 `content.json`。`sfdc_cms__site` 和 `sfdc_cms__languageSettings` 始终是捆绑包中的必需项。`sfdc_cms__languageSettings` 默认声明仅解析的 `defaultLocale`（例如 `en_US`）；当用户请求多语言支持时，会扩展它。不允许其他内容类型。

### 第 3 步：填充所有元数据字段
使用文档中提供的默认模板。`{括号}` 中的值是解析属性引用——用第 1 步中的实际值替换它们。

| 元数据类型 | 模板引用 |
|----------|----------|
| 网络 | [configure-metadata-network.md](references/configure-metadata-network.md) |
| 自定义站点 | [configure-metadata-custom-site.md](references/configure-metadata-custom-site.md) |
| 数字体验配置 | [configure-metadata-digital-experience-config.md](references/configure-metadata-digital-experience-config.md) |
| 数字体验打包 | [configure-metadata-digital-experience-bundle.md](references/configure-metadata-digital-experience-bundle.md) |
| 数字体验（sfdc_cms__site） | [configure-metadata-digital-experience.md](references/configure-metadata-digital-experience.md) |
| 数字体验（sfdc_cms__languageSettings） | [configure-metadata-language-settings.md](references/configure-metadata-language-settings.md) |

有关 URL 更新，请参阅 [update-site-urls.md](references/update-site-urls.md)。

### 第 3 步的执行说明：加载和使用文档
- 代理必须在尝试填充元数据字段之前，读取第 3 步中引用的每个 `references/*.md` 文件的全部内容。
- 使用您的平台的文件读取工具（例如，`read_file`）加载这些文件，然后使用第 1 步中解析的属性替换 `{括号}` 中的占位符。
- 要加载的文件：
  - `references/configure-metadata-network.md`
  - `references/configure-metadata-custom-site.md`
  - `references/configure-metadata-digital-experience-config.md`
  - `references/configure-metadata-digital-experience-bundle.md`
  - `references/configure-metadata-digital-experience.md`
  - `references/configure-metadata-language-settings.md`
- 读取整个文件内容，将占位符（例如 `{siteName}`）替换为解析的值，然后使用扩展的模板填充元数据 XML/JSON 内容。

### 第 4 步：不要修改非模板化属性
不要修改 `Network`、`CustomSite`、`DigitalExperience`、`DigitalExperienceConfig` 或 `DigitalExperienceBundle` 元数据的默认属性值，这些值不是用 `{括号}` 包裹的变量。

## 验证检查清单
在部署之前，请确认：

- [ ] 所有五个必要属性已解决，并且 `defaultLocale` 已解决（用户未指定时默认为 `en_US`）
- [ ] 所有元数据目录和文件都按项目结构存在
- [ ] 所有元数据字段与第 3 步模板匹配，仅替换 `{括号}`；未添加或更改任何其他默认属性值
- [ ] `sfdc_cms__site` `content.json` 中的 `appSpace` 是空字符串 `""`（初始站点创建时从未绑定 `appSpace`；那是部署到目标组织后 UIBundle 的后续更新）
- [ ] `sfdc_cms__languageSettings/languages/` 文件存在。语言声明满足以下平台规则：
  - [ ] `defaultLocale` 与一个声明语言的 `locale` 匹配，该语言处于活动状态
  - [ ] 每个 `locale` 都是 Salesforce 支持的，每个语言都是 `isActive: true`，每个 `locale` + `label` 组合都是唯一的，声明的语言数量不超过平台最大值
  - 请参阅 [configure-metadata-language-settings.md](references/configure-metadata-language-settings.md) 获取完整规则目录。单语言默认声明 trivially 满足所有规则。
- [ ] 部署验证成功（`DigitalExperience` 类型已涵盖 `sfdc_cms__languageSettings` —— 无需更改 `--metadata` 列表）：
```bash
sf project deploy validate --metadata Network CustomSite DigitalExperienceConfig DigitalExperienceBundle DigitalExperience --target-org ${usernameOrAlias}
```

## 常见工作流

### 更新体验站点 URL

**使用场景**：当用户想要更新或更改站点 URL（urlPathPrefix）时。

**步骤**：
- [ ] 阅读 [update-site-urls.md](references/update-site-urls.md) 了解三组件架构和 URL 更新工作流
- [ ] 按照文档中的分步工作流，跨所有三个组件（DigitalExperienceConfig、Network、CustomSite）一致地更新 URL

### 配置多语言支持

**使用场景**：当用户希望站点支持多种语言、区域设置、国际化或翻译——而不仅仅是每个站点都接收的默认语言仅声明。

**步骤**：
- [ ] 收集站点应支持的其他语言以及默认区域设置（解决上述 `defaultLocale` 和 `languages` 属性）
- [ ] 运行 [预检查：目标组织发布](#pre-flight-target-org-release-multi-language-only)——如果组织低于发布 264（API v68+），则中止
- [ ] 阅读 [configure-metadata-language-settings.md](references/configure-metadata-language-settings.md) 了解模板、字段引用和平台验证规则
- [ ] 扩展 `sfdc_cms__languageSettings/languages/content.json`（其中已存在默认语言）以包含其他语言条目，然后重新运行部署验证

**注意**：这是仅限编写——声明的区域设置可以干净地部署，但区域设置路径路由尚未在请求时解析。不要翻译 UI 打包内容本身；这仅声明站点支持的语言。
