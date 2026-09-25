# 从零开始创建 Contentful 自定义应用

使用此技能将客户应用想法转化为一个可本地测试的小型 Contentful 应用框架实现。

默认情况下，除非用户明确选择其他目标，否则将使用用户自己的仓库、Contentful 组织和应用交付工作流。

公共 Contentful Marketplace 应用和 Contentful 的公共应用仓库（`https://github.com/contentful/apps`）可以作为成熟的 App Framework 模式、UX 习惯和配置流程的有用参考。使用它们作为示例进行适配，而不是作为必需的仓库结构或发布流程。

## 工作方式

- 在编写代码之前，先确定应用的用途、主要用户、受影响的内容模型和目标 Contentful 界面。
- 仅询问那些会改变架构或阻止错误构建的信息。
- 优先选择在非生产环境中证明价值的最小版本。
- 基于官方 App Framework 文档和当前项目结构来决定功能能力。
- 将用户拥有的密钥、令牌和生产内容排除在生成的代码、日志和示例之外。

## 工作流程

### 1. 创建实施简报

在搭建框架之前，捕获一个简短的简报：

- 用一句话描述应用概念，
- 目标用户和他们需要改进的工作流程，
- v1 版本所需的 Contentful 位置，
- 涉及的内容类型、字段、区域和环境，
- 涉及的外部系统、身份验证或 API，
- 预期的安装和配置模型，
- v1 版本必须具备的行为，
- 假设和非目标，
- 本地和沙盒测试的验证计划。

如果想法仍然比较宽泛，建议提出 2-3 个可行的 v1 选项，并推荐其中最小有用的一个。

对于规划细节，请使用 [应用规划](references/app-planning.md)。

### 2. 选择应用形态

根据用户工作流程选择位置：

- 使用 `app-config` 当应用需要在安装时进行设置时。
- 使用 `entry-sidebar` 用于入门级上下文、状态、辅助操作和轻量级洞察。
- 使用 `entry-field` 来替换或增强字段的编辑体验。
- 使用 `dialog` 用于从其他位置启动的聚焦选择器、确认或多步流程。
- 使用 `page` 或 `home` 用于仪表板、批量工具、引导或全屏操作工作流。
- 仅在替换或大量扩展完整条目编辑体验值得维护成本时，才使用 `entry-editor`。
- 仅在应用需要异步行为、服务器端执行、验证的传入请求、事件处理或访问浏览器外密钥值时，才使用 App Actions 或 Functions。

如果需要敏感凭证，请将它们建模为密钥安装参数，并在后端或 Function 支持的路径中仅使用原始值。

### 3. 检查或搭建项目

如果用户已经有仓库：

1. 检查 `package.json`、与应用相关的文档、现有应用位置、构建脚本、测试和样式约定。
2. 重用仓库的框架、包管理器、lint/test 设置和组件模式。
3. 确定应用是否已经使用 `@contentful/app-sdk`、`@contentful/react-apps-toolkit`、`@contentful/f36-components` 或 `contentful-management`。

如果用户没有仓库：

1. 使用 `npx create-contentful-app@latest <app-name>` 进行搭建。
2. 除非用户要求 JavaScript，否则优先使用 TypeScript。
3. 在本地应用连接到 Contentful 并验证之前，尽量保持第一个搭建接近生成的项目。

### 4. 以 Contentful 原生风格构建

- 使用 App SDK 或 React Apps Toolkit 访问当前位置 SDK。
- 使用 Forma 36 组件构建 Contentful 网页应用 UI。在尝试构建自定义内容之前，始终检查 Forma 36 是否有类似的组件。
- 保持 UI 密集、清晰且对编辑器友好；避免在 Contentful 网页应用内部使用营销布局。
- 当加载、空、权限和错误状态会影响主要工作流程时，包含这些状态。
- 保持字段和条目写入明确、尽可能可逆，并易于编辑器理解。
- 当运行时位置需要应用配置时，从 `sdk.parameters.installation` 读取安装参数。不要通过 CMA 从挂载效果、渲染路径、钩子或用户交互中获取应用安装记录，只是为了检索配置参数。
- 在应用有多个真实使用路径之前，避免进行广泛的抽象。
- 不要在浏览器代码中暴露管理令牌、API 密钥或第三方凭证。

### 5. 将本地应用连接到 Contentful

在开发组织或沙盒中创建或更新应用定义：

- 将前端 URL 设置为本地开发服务器，通常是 `http://localhost:3000`，
- 仅选择 v1 版本中实现的位置，
- 定义所需的安装或实例参数，
- 将应用安装到非生产空间或环境，
- 将应用分配给相关的内容类型、字段、侧边栏、主页或页面位置，
- 在需要时，播种最小的测试内容。

对于本地测试和交接步骤，请使用 [仓库和验证](references/repo-and-validation.md)。

### 6. 交接前验证

在用户项目中运行最接近有意义的检查：

- 依赖项更改时的包安装检查，
- 类型检查和 lint，
- 单元或组件测试，
- 生产构建，
- 本地开发服务器冒烟测试，
- 在非生产空间中手动 Contentful 网页应用流程。
- 当运行时代码读取安装参数时，在应用源代码上运行 `rg -n "appInstallation\\.(getForOrganization|get)\\(|getForOrganization"`，并解释任何剩余的 CMA 应用安装调用。

除非你运行了相关的验证或明确说明无法运行的内容，否则不要声称应用可以正常工作。

### 7. 交接结果

结束于：

- 已构建的内容，
- 如何在本地运行它，
- 如何在 Contentful 中安装或分配它，
- 执行的验证，
- 剩余的假设、限制或需要的凭证，
- 建议的下一步迭代。

## 相关技能

- `contentful-custom-app-enhancement` - 改进或调试现有的自定义应用。
- `contentful-api` - 具体的 CMA、CDA、CPA、Images API 和 GraphQL 示例。
- `contentful-migration` - 内容模型迁移脚本。
- `contentful-guide` - Contentful 概念和 API 路由。
