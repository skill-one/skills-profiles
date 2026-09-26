# OpenUI

OpenUI 是一个全栈生成式 UI 框架，以 **OpenUI Lang** 为中心，OpenUI Lang 是一种紧凑的、以流式为先的语言，用于生成模型 UI。不要将 OpenUI 视为仅限 React：核心语言、解析器、提示生成、运行时评估和类型位于 `@openuidev/lang-core` 中；React、Vue、Svelte 和无构建浏览器集成位于该核心之上。

首先从用户的应用或项目开始工作。在给出 API 建议之前，检查已安装的包、生成的模板和锁文件。当安装源缺失或任务目标是 `latest` 时，仅使用第一方 OpenUI 源：GitHub 仓库 `https://github.com/thesysdev/openui` 和文档 `https://www.openui.com`。

## 回答前的首要检查

1. 当可用时，检查用户的 `package.json` 和锁文件。
2. 确定已安装的 `@openuidev/*` 包和版本。
3. 优先使用已安装的包导出和生成的模板，而不是假设。
4. 当可用时，使用安装的 `node_modules/@openuidev/*`、`.d.ts` 文件和生成的文件作为事实来源。
5. 如果不存在应用或已安装的包，则使用第一方文档和 GitHub 源。

除非涉及 OpenUI 或 `@openuidev` 包，否则不要使用此技能回答一般的 React UI 问题、通用设计系统建议、不相关的 AI 代理 harness 或一般前端调试。

## 当前包映射

| 包 | 用于 |
|---|---|
| `@openuidev/lang-core` | 框架无关的解析器、流式解析器、提示生成、运行时评估、`Query`/`Mutation`、存储、绑定、JSON 架构/类型 |
| `@openuidev/react-lang` | React `defineComponent`、`createLibrary`、`<Renderer />`、钩子、解析器/提示重新导出 |
| `@openuidev/vue-lang` | Vue 3 `defineComponent`、`createLibrary`、`<Renderer />`、组合式、解析器重新导出 |
| `@openuidev/svelte-lang` | Svelte 5 `defineComponent`、`createLibrary`、`<Renderer />`、上下文辅助函数、解析器重新导出 |
| `@openuidev/react-ui` | OpenUI 的默认 React 组件库 (`openuiLibrary`、`openuiChatLibrary`)、`AgentInterface`、聊天布局、独立 UI 原语、样式、主题和 `@openuidev/react-headless` API 的重新导出 |
| `@openuidev/react-headless` | 带来自己的 React 聊天状态、钩子、存储/LLM 适配器原语、流式适配器、消息转换器和工件原语，而无需 OpenUI 的视觉组件 |
| `@openuidev/react-email` | React Email 组件库和生成电子邮件的提示选项 |
| `@openuidev/browser-bundle` | 作为 `window.__OpenUI` 暴露的 CDN/iframe/无构建 React 渲染器捆绑包 |
| `@openuidev/cli` | `openui create` 框架和 `openui generate` 从库导出生成的系统提示 + 库规范生成 |
| `@openuidev/thesys` | 版本敏感的客户端 OpenUI Cloud 帮助程序，如 `useOpenuiCloudStorage()`、Cloud 组件集和 Cloud 工件组件/渲染器/类别；验证当前导出 |
| `@openuidev/thesys-server` | 版本敏感的服务器端 OpenUI Cloud 帮助程序，如 `artifactTool` 和 `generateSystemPrompt` (`createResponsesInstructions` 是其已弃用的别名)，用于 Cloud 支持的 `/api/chat` 路由 |

为目标运行时选择包。对于仅后端解析或提示/架构生成，优先选择 `@openuidev/lang-core` 或 CLI，而不是拉入 UI 框架。

`@openuidev/react-ui` 重新导出 `@openuidev/react-headless` 表面，因此 React UI 应用可以从 `@openuidev/react-ui` 导入适配器、消息格式、存储帮助程序、钩子和消息类型，因为它们重新导出无头 API。在构建自定义/无头聊天 UI 而无需 OpenUI 的视觉组件时，保持 `@openuidev/react-headless` 作为直接导入。

## 选择起始点

- 如果用户想要一个新的 OpenUI/GenUI 应用，请使用 `@openuidev/cli`；它是最容易的脚手架路径。
- 如果用户想要将 OpenUI 集成到现有的 React/Next 代理或聊天应用中，并想要开箱即用的组件库，请使用 `@openuidev/react-ui` 与 `AgentInterface`、`openuiLibrary` 或 `openuiChatLibrary`。
- 如果用户想要在现有的 React 项目中渲染 OpenUI Lang，而无需完整的 React UI 表面，请使用 `@openuidev/react-lang`。
- 如果用户想要开放式的生成、生成的 HTML 应用、沙盒化 iframe 或原始/渲染预览，请阅读 [references/open-ended-html.md](references/open-ended-html.md)。
- 如果主机应用是 Vue 或 Svelte，请使用 `@openuidev/vue-lang` 或 `@openuidev/svelte-lang`。使用 `@openuidev/lang-core` 进行框架无关的解析、提示生成、架构或后端/运行时工作。

## OpenUI Cloud 功能

OpenUI Cloud 是 Agent Interface 的托管后端。它使用开源的 OpenUI 渲染引擎，并添加了生产层：持久化的对话、生产级的生成式 UI、预构建的报告/演示工件、主题/白标、输出校正、模型/提供者弹性、版本控制、可观察性和审计跟踪。

当用户想要 Agent Interface 应用的托管生产基础设施时，请使用 Cloud。当用户想要拥有模型路由、存储、工具、组件库和运行时行为时，请使用自托管 OpenUI。

版本敏感：验证 Cloud 模板环境变量、`@openuidev/thesys*` 导出和路由帮助程序与安装的包/模板。CLI 快速启动提示 **OpenUI Cloud 或自托管**。对于 Cloud：

- 仅在服务器端存储 `THESYS_API_KEY`，通常在 `.env.local` 中。
- Cloud CLI 模板将其 `provider/model` 允许列表保留在应用配置中，并使用 `DEMO_USER_ID` 作为演示用户身份。
- 将 Cloud 调用保留在服务器路由（如 `/api/chat` 和 `/api/frontend-token`）后面；永远不要将服务器密钥暴露给浏览器。
- 在 `openui-cloud` 模板中，`/api/chat` 使用 `@openuidev/thesys-server` 帮助程序，如 `artifactTool` 和 `generateSystemPrompt`。
- `AgentInterface` 使用 `llm` 和 `storage` 属性连接到 Cloud。`llm` 指向一个指向 Cloud 响应端点的应用路由，通常使用 `openAIResponsesAdapter()` 和 `openAIConversationMessageFormat`。`storage` 使用来自 `@openuidev/thesys` 的 `useOpenuiCloudStorage()` 和一个短期的前端令牌。
- Cloud 提供的组件集、工件渲染器和类别来自 `@openuidev/thesys`。
- 在 Thesys 控制台中生成密钥：`https://console.thesys.dev/keys`。

对于现有项目 Cloud 工作，请保持这些不变量：

- 保持两个 Cloud 平面分开：`ChatLLM` 发布到应用的自定义 `/api/chat` 代理，而 `useOpenuiCloudStorage()` 使用由 `/api/frontend-token` 生成的短期令牌访问 Cloud 存储。
- 仅发送最新消息，使用 `openAIConversationMessageFormat.toApi(messages.slice(-1))`；Cloud 从 `conversation: threadId` 重播历史记录。将该格式与 `openAIResponsesAdapter()` 配对。
- 从认证的服务器状态中派生前端令牌的 `user_id`（在生产环境中）。独立地认证和限制两个路由，将 `threadId` 视为不受信任的，并通过验证的主机映射或文档 Cloud 成员资格检查授权它。不要假设安装的 SDK 导出了一个所有权帮助程序。
- 不要部署未更改的演示身份。用主机认证、速率限制和对话授权替换它；禁用这两个路由，直到这些控制措施存在，然后报告阻止器。
- 在 Next.js 中，将 `@openuidev/thesys` 导入隔离在客户端组件中，并遵循安装的第一方模板的动态渲染边界。如果生产构建仍然在预渲染期间评估浏览器专用依赖项，请添加一个小的 `dynamic(..., { ssr: false })` 客户端加载器。
- 保持中止传播并在上游流结束时关闭 SSE 流。
- 不要编造 Cloud 历史导入 API、自定义工具执行循环或自定义库指令 API。验证当前第一方支持，并在不支持所需功能时保留自托管路径。

## 路由 Cloud 集成和迁移任务

检查目标项目的框架和路由、包清单和锁文件、服务器运行时、身份验证、现有的 OpenUI 导入、聊天传输、存储、组件库、工具和工件。保留其包管理器、路由约定、身份验证边界、设计系统和正常行为。

选择匹配的路径：

| 起始点和目标                                                     | 所需的 runbook                                                                                                                                                          |
| ------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 现有的 React 应用，添加管理的 Cloud 聊天                                | 在编辑之前，完全阅读 [references/cloud-integration.md](references/cloud-integration.md)                                                                                   |
| 现有的非 React 应用，添加管理的 Cloud 聊天                            | 阅读 [references/cloud-integration.md](references/cloud-integration.md)；需要当前的第一个方客户端/运行时或报告已安装的 React 唯一边界                                              |
| 现有的自托管/开源应用，用 Cloud 替换或补充它                          | 阅读 [references/oss-to-cloud-migration.md](references/oss-to-cloud-migration.md) 和 [references/cloud-integration.md](references/cloud-integration.md) 完全内容，然后编辑 |

如果“迁移”没有确定 Cloud 是否应替换自托管路径或与它一起运行，则根据项目和请求推断意图。仅在目标仍然模糊且重要时询问；永远不要默默删除正常工作的后端。将代码迁移和历史数据导入视为单独的任务，并且在没有验证的第一方导入 API 的情况下，不要声称数据迁移。
