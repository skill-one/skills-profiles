# 为 LLM 创建应用

ChatGPT 应用是扩展 ChatGPT 的对话体验，通过工具和自定义 UI 视图实现。它们作为在对话期间被调用的 MCP 服务器构建。

⚠️ 应用同时被两个用户使用：**人类**和**ChatGPT LLM**。它们通过视图协作——人类与其交互，LLM 查看其状态。在编写代码之前，请牢记这一点：视图是你们的共享界面。

SPEC.md 跟踪应用的需求和设计决策。在开发应用时，请保持其更新。

**正在构建电商应用？** → 首先阅读 [ecommerce.md](references/ecommerce.md)。

**没有 SPEC.md？** → 首先阅读 [discover.md](references/discover.md)。在 SPEC.md 存在之前，无需阅读其他内容。

**SPEC.md 存在？** → 首先阅读 SPEC.md，然后按照 [architecture.md](references/architecture.md) 设计变更。更新 SPEC.md，然后在进行代码编写之前，阅读下方的相关实现参考。

**从 Skybridge `< 0.36.x` 迁移？** → 首先阅读 [migrate-to-v1.md](references/migrate-to-v1.md)。用户可以将 `skybridge >= 0.36.x` 视为 v1。

**从 Skybridge `1.x` 迁移到 `2.x`？** → 首先获取 [v2.0.0 发布说明](https://github.com/alpic-ai/skybridge/releases/tag/v2.0.0) 并遵循其内容。

## 设置

1. **复制模板** → [copy-template.md](references/copy-template.md)：在开始具有现成 SPEC.md 的新项目时
2. **本地运行** → [run-locally.md](references/run-locally.md)：在准备测试时，需要开发服务器或 ChatGPT 连接
3. **评估** → [evals.md](references/evals.md)：在检查真实模型是否从自然提示中正确触发工具时，在测试环境中进行

## 架构

设计或演进 UX 流程和 API 形状 → [architecture.md](references/architecture.md)

## 实现

- **获取和渲染数据** → [fetch-and-render-data.md](references/fetch-and-render-data.md)：在实现服务器处理程序和视图数据获取时
- **状态和上下文** → [state-and-context.md](references/state-and-context.md)：在持久化视图 UI 状态和更新 LLM 上下文时
- **提示 LLM** → [prompt-llm.md](references/prompt-llm.md)：在视图需要触发 LLM 响应时
- **UI 指南** → [ui-guidelines.md](references/ui-guidelines.md)：显示模式、布局约束、主题、设备和区域设置
- **外部链接** → [open-external-links.md](references/open-external-links.md)：在重定向到外部 URL 或设置“在应用中打开”目标时
- **OAuth** → [oauth.md](references/oauth.md)：在工具需要用户认证以访问特定用户数据时
- **资源和样式** → [assets-and-styling.md](references/assets-and-styling.md)：在向视图添加图像、字体或 CSS 时
- **CSP** → [csp.md](references/csp.md)：在声明允许的域名用于获取、资源、重定向或 iframe 时

## 部署

- **发布到生产环境** → [deploy.md](references/deploy.md)：在准备通过 Alpic 部署时
- **发布到 ChatGPT 目录** → [publish.md](references/publish.md)：在准备提交审核时

完整 API 文档：[https://docs.skybridge.tech/api-reference.md](https://docs.skybridge.tech/api-reference.md)

发布说明 & 更改日志：[https://skybridge.tech/changelog.md](https://skybridge.tech/changelog.md)
