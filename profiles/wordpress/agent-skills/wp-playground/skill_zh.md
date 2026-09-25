# WordPress Playground

这是一个轻量级的路由封装。使用它来选择合适的 Playground 工作流，然后仅加载任务所需的聚焦参考或技能。

## 流程

1. 识别用户意图：蓝图创作/评审、本地 CLI 执行、浏览器仅网站/分享链接工作流、Xdebug/卡顿 CLI 运行，或混合的 Playground 请求。
2. 路由到下方的聚焦源，仅当请求具有多个不同部分时才加载多个。
3. 对于混合请求，将蓝图 JSON 工作委托给 `blueprint`，然后返回此处以获取运行时、CLI、调试或分享指导。

- **蓝图 JSON、模式、步骤、资源、包或蓝图评审**：直接使用 `blueprint` 技能。不要在此处重复蓝图模式细节。
- **本地 CLI 执行**：阅读 `references/cli.md` 了解 `@wp-playground/cli` 服务器、`run-blueprint`、`build-snapshot`、挂载、版本切换和本地验证。
- **Xdebug 或卡顿 CLI 运行**：阅读 `references/debugging.md` 了解 Xdebug、运行时日志、工作标志和卡顿 CLI 运行。
- **浏览器仅 Playground 网站工作流**：阅读 `references/website.md` 了解查询 API 和蓝图 URL 设置、分享链接和浏览器限制。它将现有网站操作路由到单独的 WebMCP、Playground MCP 和 Sites API 参考；仅加载选定方法。除非用户请求特定连接方法，否则优先为支持的浏览器操作使用可用的 WebMCP 工具。

## 所需输入

- 预期的工作流：蓝图创作、本地 CLI 运行、网站/分享链接、快照或调试。
- 如果必须挂载或打包本地代码，则提供项目或包路径。
- 如果兼容性重要，则提供所需的 WordPress/PHP 版本。
- 如果需要本地服务器，则提供端口偏好。
- 是否需要浏览器仅分享或本地文件系统访问。

## 安全限制

- Playground 实例是可丢弃的、SQLite 背景环境；切勿将它们指向生产数据。
- 将蓝图 JSON 指导保留在 `blueprint` 中，以便模式和示例有一个单一的事实来源。
- 对于本地 CLI 工作，在运行命令前验证 Node.js 20.18+ 和 `npm`/`npx`。
- 浏览器仅 Playground 无法读取本地文件系统路径；使用公共 URL、托管 ZIP 包或内联蓝图 JSON。

## 验证

- 对于蓝图内容，根据已发布的模式进行验证并遵循 `blueprint` 技能的验证。
- 对于本地 CLI 运行，验证 Playground 实例中挂载的插件/主题或蓝图副作用。
- 对于分享链接，打开生成的 URL 并确认预期的着陆页和安装的资产加载。

## 失败模式

- **蓝图工作路由到此处**：停止并使用 `blueprint` 技能进行模式键、步骤、资源、包、验证或蓝图评审。
- **浏览器仅工作流中需要本地文件系统**：使用 `references/cli.md`；`playground.wordpress.net` 无法读取本地文件系统路径。
- **从本地 CLI 工作流请求可分享的浏览器链接**：使用 `references/website.md`；本地服务器 URL 不是可移植的分享链接。
- **调试被视为第二次跳转参考**：直接阅读 `references/debugging.md` 了解 Xdebug、日志、工作标志和卡顿 CLI 运行。

## 升级

- 如果任务需要 PHP 扩展、原生数据库访问、持久性或 Playground 无法提供的类似生产的基础设施，请使用完整的 WordPress 堆栈，例如 wp-env、Docker 或项目提供的环境。
