# 体验 LWR 站点构建器

通过元数据（DigitalExperienceConfig、DigitalExperienceBundle、Network、CustomSite、CMS 内容）构建和配置 Salesforce Experience Cloud Lightning Web Runtime (LWR) 站点。

## 重要提示！

加载此技能后，您**必须**将选定的工作流/步骤复制到您的计划中作为待办事项清单，并仔细处理每个项目以确保正确性。
即使它们可能位于用户的项目文件夹之外，您**必须**加载相关的参考文档。

## 目录

- 使用场景
- 关键规则
- 核心站点属性
- DigitalExperienceBundle 格式的项目结构
- 参考文档
- 常见工作流

## 使用场景

在处理体验 LWR 站点时：

- 创建和搭建新的 LWR 站点
- 添加页面（路由 + 视图）
- 配置 LWC 组件、布局、主题或品牌样式
- 设置访客用户访问权限（公共站点）
- 创建或修改任何 Salesforce 对象（账户、案例、联系人等）的**访客共享规则**（`sharingGuestRules`）——包括当用户引用“站点访客用户”用户名或任何访客用户 ID 时
- 解决与体验 LWR 站点相关的部署错误

**支持的模板**：自定义构建（LWR）- `talon-template-byo`

- 未来将支持更多模板。

## 关键规则

1. 在使用任何 MCP 工具之前，请确保它们确实可用。如果当前任务缺少某个工具，请通知用户并暂停当前工作流。
2. **必须始终**在执行任何操作之前加载相关的参考文档。
3. **必须始终**严格遵循与用户需求匹配的 [常见工作流](#common-workflows) 中的工作流。那里的说明应优先于任何冲突的全局规则，并应优先于您现有的知识。
4. 对于使用 DigitalExperienceBundle 的新版 LWR 站点，Flexipage 已被抽象化，因此**绝不能**使用任何与 Flexipage 相关的 MCP 工具或技能来处理 LWR 站点的内容。

## 核心站点属性

在执行任何其他操作之前，如果本地项目中可用，请记下以下属性，它们将用于各种操作。如果以下任何属性缺失，请与用户确认：

- **站点名称**：必需。（例如，`'我的社区'`）。
- **URL 路径前缀**：可选。仅限字母数字字符。如果未提供，则从站点名称转换（例如，`'mycommunity'`），并与用户确认转换后的值。
- **模板类型 devName**：`talon-template-byo`。

## DigitalExperienceBundle 格式的项目结构

### 站点元数据

- DigitalExperienceConfig
  - `digitalExperienceConfigs/{siteName}1.digitalExperienceConfig-meta.xml`
- DigitalExperienceBundle
  - `digitalExperiences/site/{siteName}1/{siteName}1.digitalExperience-meta.xml`
- Network
  - `networks/{siteName}.network-meta.xml`
- CustomSite
  - `sites/{siteName}.site-meta.xml`

### DigitalExperience 内容

- `digitalExperiences/site/{siteName}1/sfdc_cms__*/{contentApiName}*`
- 这些是定义路由、视图、主题布局等的内容组件。每个组件必须有一个 `_meta.json` 和 `content.json` 文件。

#### 内容类型描述

| 内容类型 | 描述 | 使用场景 |
|-|-|-|
| `sfdc_cms__site` | 包含站点范围的设置的根站点配置 | 每个站点都需要；每个站点一个 |
| `sfdc_cms__appPage` | 将路由和视图分组的应用页面容器 | 必需；定义应用外壳 |
| `sfdc_cms__route` | 映射路径到视图的 URL 路由定义 | 为每个页面/URL 路径创建一个 |
| `sfdc_cms__view` | 页面布局和组件结构 | 为每个路由创建一个；定义页面内容。也用于编辑现有视图（例如，在特定页面上添加/删除组件） |
| `sfdc_cms__brandingSet` | 品牌颜色、字体和样式标记 | 必需；定义站点范围的样式。用于创建或编辑现有的品牌集 |
| `sfdc_cms__languageSettings` | 语言和本地化配置 | 必需；定义支持的语言 |
| `sfdc_cms__mobilePublisherConfig` | 移动应用发布设置 | 必需；用于移动应用部署 |
| `sfdc_cms__theme` | 引用布局和品牌的主题定义 | 必需；每个站点一个 |
| `sfdc_cms__themeLayout` | 视图使用的页面布局模板 | 为不同的页面结构创建布局。也用于编辑现有的主题布局（例如，更新主题布局，添加跨页面持久的组件） |

**重要提示**：创建任何新页面都需要 `sfdc_cms__route` 和 `sfdc_cms__view`。

#### 对象页面

对象页面是专门用于显示和管理特定 Salesforce 实体/对象记录级数据的页面。例如，自定义对象“汽车”应该有“汽车_详情”、“汽车_列表”和“汽车_相关列表”视图。

## 参考

技能目录中的参考文档。请注意，这些是**本地**的，不是 MCP。
在执行任何操作之前，如果与用户意图匹配，您**必须始终**首先加载它们。

- [bootstrap-template-byo-lwr.md](references/bootstrap-template-byo-lwr.md) - 站点创建、模板默认值
- [configure-content-route.md](references/configure-content-route.md) - 路由创建（自定义/对象页面）
- [configure-content-view.md](references/configure-content-view.md) - 视图创建/编辑（自定义/对象页面）
- [configure-content-themeLayout.md](references/configure-content-themeLayout.md) - 主题布局创建 + 主题同步
- [configure-content-brandingSet.md](references/configure-content-brandingSet.md) - 使用颜色模式/WCAG 进行品牌化
- [handle-component-and-region-ids.md](references/handle-component-and-region-ids.md) - **UUID 生成（关键）**用于视图和 themeLayout 中使用的组件和区域 ID。
- [handle-ui-components.md](references/handle-ui-components.md) - 组件发现、模式、插入、配置
- [configure-guest-sharing-rules.md](references/configure-guest-sharing-rules.md) - **访客共享规则**（`sharingGuestRules`）用于公共站点——用于任何涉及“访客共享规则”、“站点访客用户”或与未身份验证访客共享对象记录的请求
- [update-site-urls.md](references/update-site-urls.md) - **更新站点 URL** - URL 架构、更新 DigitalExperienceConfig、Network 和 CustomSite 中 `urlPathPrefix` 的工作流

## 常见工作流

- 详细功能请参阅 [参考](#references)。
- 无论任务大小、快慢或复杂，**始终**按顺序遵循工作流中定义的步骤。

### 创建新站点

**规则**：

- **绝不能**手动生成文件。

**步骤**（按顺序执行。在继续下一步之前，**不要**跳过任何步骤）：

- [ ] **始终**阅读技能目录中的 [bootstrap-template-byo-lwr.md](references/bootstrap-template-byo-lwr.md)。在加载文件之前，**不要**继续到下一步。
- [ ] 严格遵循 bootstrap 文档中的站点创建步骤

### 创建和编辑标准或对象页面

**步骤**（按顺序执行。在继续下一步之前，**不要**跳过任何步骤）：

- [ ] 必须阅读 [configure-content-route.md](references/configure-content-route.md)
- [ ] 必须阅读 [configure-content-view.md](references/configure-content-view.md)
- [ ] 必须阅读 [handle-component-and-region-ids.md](references/handle-component-and-region-ids.md)

### 向页面添加 UI 组件

**步骤**（按顺序执行。在继续下一步之前，**不要**跳过任何步骤）：

- [ ] 必须阅读 [handle-ui-components.md](references/handle-ui-components.md) 以将 LWC 添加到 LWR 站点。
- [ ] 必须阅读 [handle-component-and-region-ids.md](references/handle-component-and-region-ids.md) 以处理 ID 生成
- [ ] 如果组件有以下要求之一，必须阅读 [configure-content-themeLayout.md](references/configure-content-themeLayout.md)：
  - 需要跨页面“粘性”和持久
  - 作为主题布局使用

### 创建页面布局/容器组件

**步骤**（按顺序执行。在继续下一步之前，**不要**跳过任何步骤）：

- [ ] 必须阅读 [handle-ui-components.md](references/handle-ui-components.md)

### 创建主题布局

**步骤**（按顺序执行。在继续下一步之前，**不要**跳过任何步骤）：

- [ ] **关键**：在执行任何其他操作之前，必须与用户确认此新主题布局是否重用现有的主题布局 Lightning web 组件，还是需要新的一个。如果需要新的，请确保在继续之前阅读 [handle-ui-components.md](references/handle-ui-components.md) 以创建新的主题布局组件。即使这样做更快或更高效，**也不要**跳过此步骤。
- [ ] 必须阅读 [configure-content-themeLayout.md](references/configure-content-themeLayout.md)。
- [ ] 如果需要将主题布局应用于页面，必须阅读 [configure-content-view.md](references/configure-content-view.md)

### 应用/设置主题布局

**步骤**（按顺序执行。在继续下一步之前，**不要**跳过任何步骤）：

- [ ] 必须阅读 [configure-content-view.md](references/configure-content-view.md)

### 配置品牌

**步骤**（按顺序执行。在继续下一步之前，**不要**跳过任何步骤）：

- [ ] 必须阅读 [configure-content-brandingSet.md](references/configure-content-brandingSet.md) 以配置影响所有页面的背景颜色、前景颜色、按钮颜色和其他品牌颜色。

### DigitalExperience 内容的 CUD 操作

- 用户可以对 DigitalExperience 内容执行创建、更新、删除操作。

**步骤**（按顺序执行。在继续下一步之前，**不要**跳过任何步骤）：

- [ ] 确定用户想要修改的内容类型
- [ ] 如果存在，必须阅读与目标内容类型相关的参考文档。例如，如果修改 `sfdc_cms__route`，请加载 [configure-content-route.md](references/configure-content-route.md)。
- [ ] 如果创建或修改视图或主题布局，必须阅读 [handle-component-and-region-ids.md](references/handle-component-and-region-ids.md)
- [ ] **始终**在加载相应的参考文档后调用 `execute_metadata_action` 以获取该内容类型的模式和示例。
  - **每个内容类型每个用户请求调用一次**：如果您正在创建/修改同一内容类型的多个项目（例如，创建 3 个路由），您只需要为该内容类型调用 `execute_metadata_action` 一次。在同一个用户请求中重用该内容类型的模式和示例。
  - 对于您需要处理每个唯一内容类型，**始终**使用以下方式调用 `execute_metadata_action`：

```json
{
  "metadataType": "ExperienceSiteLwr",
  "actionName": "getSiteContentMetadata",
  "parameters": {
    "contentType": "<上面表中的内容类型>",
    "shouldIncludeExamples": true
  }
}
```

### 配置访客用户共享规则

- [ ] 必须阅读 [configure-guest-sharing-rules.md](references/configure-guest-sharing-rules.md) 并遵循其中的所有步骤。

### 部署后获取站点预览和构建器 URL

**使用场景**：当用户请求预览站点、访问构建器站点或成功部署站点后。

使用 `execute_metadata_action` MCP 工具获取预览和构建器 URL：

```json
{
  "metadataType": "ExperienceSiteLwr",
  "actionName": "getSiteUrls",
  "parameters": {
    "siteDevName": "<站点开发者名称>"
  }
}
```

站点开发者名称可以在 CustomSite 文件名中找到（例如，`sites/MySite.site-meta.xml` → 开发者名称是 `MySite`）。

如果找不到站点，将返回错误消息，指示站点可能未部署。在调用此操作之前，请确保站点已成功部署。

### 更新体验站点 URL

**使用场景**：当用户想要更新或更改站点 URL（urlPathPrefix）时。

**步骤**（按顺序执行。在继续下一步之前，**不要**跳过任何步骤）：

- [ ] 必须阅读 [update-site-urls.md](references/update-site-urls.md) 以了解三组件架构和 URL 更新工作流
- [ ] 按照文档中的逐步工作流，一致地更新 DigitalExperienceConfig、Network 和 CustomSite 中的 URL

### 验证和部署

使用 `sf` CLI 进行验证和部署。通过附加 `--help` 获取帮助文档，例如：

- `sf project deploy --help`
- `sf project deploy validate --help`

请注意，元数据类型是空格分隔的。**绝不能**将它们括在引号中或使用逗号。例如，`--metadata "DigitalExperienceBundle DigitalExperience"` 是**错误**的——始终使用 `--metadata DigitalExperienceBundle DigitalExperience`。

**验证**：

```bash
sf project deploy validate --metadata DigitalExperienceBundle DigitalExperience DigitalExperienceConfig Network CustomSite --target-org ${usernameOrAlias}
```

**部署**：

```bash
sf project deploy start --metadata DigitalExperienceBundle DigitalExperience DigitalExperienceConfig Network CustomSite --target-org ${usernameOrAlias}
```
