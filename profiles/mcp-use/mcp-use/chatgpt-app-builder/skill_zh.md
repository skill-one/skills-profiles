# 使用 mcp-use 构建

将已安装的 `mcp-use` 包、其导出的类型、生成的声明以及项目现有代码视为事实来源。在选择 API 或更改代码之前，检查已安装的版本。

## 工作流程

1. 检查 `package.json`、服务器入口、导出的工具引用、`mcp-env.d.ts`、`views/`、`skills/` 以及已安装的 `mcp-use` 版本。
2. 使用 `create-mcp-use-app@latest` 和适当的模板构建一个新的稳定项目。在处理 beta、canary 或现有版本的项目时，匹配包版本或 dist-tag。
3. 仅阅读任务所需的引用：
   - [服务器](references/server.md) 用于工具、资源、提示、MCP 中间件、请求上下文和结果信封。
   - [视图](references/views.md) 用于交互式 MCP 应用、React 钩子、模型上下文、主机功能、资源和 CSP。
   - [认证](references/auth.md) 用于 OAuth 提供商、验证身份、范围、权限和授权。
   - [MCP 上的技能](references/skills-over-mcp.md) 当服务器应与其工具一起发布可重用工作流时。
   - [高级功能](references/advanced-features.md) 用于 OpenAPI、代理、通知、订阅和引出。
   - [迁移](references/migration.md) 仅当存在已退役或仅兼容的导入、辅助函数、注册形状、UI 模式或会话假设时。
   - [验证](references/verification.md) 在报告实现工作完成之前。
4. 针对已安装的类型进行实现。优先使用框架的当前约定，而不是复制示例或历史变更日志。
5. 验证能证明更改行为的最小真实生命周期，然后按风险比例扩展检查。

## 核心不变量

- 从 `mcp-use` 导入服务器 API，从 `mcp-use/react` 导入 React API，从 `mcp-use/oauth/*` 子路径导入 OAuth 提供商适配器。
- 使用 `inputSchema` 定义工具参数。为结构化结果和每个视图绑定的工具添加 `outputSchema`。
- 返回原始 MCP 结果信封。一个成功的基于模式的工具必须包含匹配的 `structuredContent`；预期的失败可以返回 `isError: true` 并附带模型可读的 `content`。
- 将每个视图放在 `views/<name>/view.tsx` 并使用 `view: { name: "<name>" }` 进行绑定。
- 导出每个视图消耗的静态声明工具引用。默认导出 `mcp-use dev`、`build` 和 `start` 使用的服务器入口。
- 将身份和可变工作流状态限制在请求范围内或存储在外部存储中。将客户端报告的元数据视为未验证。
- 当服务器暴露可重复、多步的工作流时，考虑使用 MCP 上的技能（即 Skills over MCP）。

## 安全约束

- 不要凭空发明导出、配置字段或回调形状。在已安装的声明或源中确认不确定的细节。
- 不要保留已安装版本中不存在的 API，仅仅因为它们出现在现有项目中。
- 不要从工具回调返回一个普通的域对象。
- 不要绑定没有匹配的 `outputSchema` 和 `structuredContent` 结果的视图。
- 不要使用模块全局变量进行跨请求身份、引出连续性或持久化业务状态。
- 不要仅凭源构建就声称成功，当类型、包导出、认证或交互行为发生变化时。
- 除非用户明确请求，否则不要部署或修改外部系统。
