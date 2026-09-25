# CopilotKit React 核心

`@copilotkit/react-core` 是 CopilotKit 的 React 前端部分：它挂载一个提供者，通过 SSE 与运行时（或直接在 SPA 模式下与 CopilotKit 智能体）进行 AG-UI 通信，并对外暴露每个交互界面的钩子。

这个 SKILL.md 是**索引**。请阅读与你的任务匹配的 `references/` 下的参考文档——不要试图从这个文件中吸收整个包的内容。

## 心智模型——你组合的三个外壳

1. **提供者外壳** — `CopilotKit` 提供者（来自 `@copilotkit/react-core/v2`）位于根目录附近（在 Next.js App Router 的 `"use client"` 内）。携带 `runtimeUrl`（必需）、`headers`、`credentials`、`properties`、`onError`、`debug`、`enableInspector`。
2. **聊天外壳** — `CopilotChat` / `CopilotPopup` / `CopilotSidebar` 或由 `CopilotChatView` + 插槽原语（`CopilotChatInput`、`CopilotChatMessageView` 等）组成的组件。所有聊天组件都来自 `@copilotkit/react-core/v2`。**`CopilotPanel` 不存在**——它是常见的幻觉。
3. **钩子外壳** — 在任何提供者下的组件内调用 `useAgent`、`useFrontendTool`、`useRenderTool` 等。每个钩子都接受可选的 `{ agentId }` 进行智能体范围的注册。

## 何时加载哪个参考

| 任务                                                                                                      | 参考                                                                               |
| --------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| 挂载 `CopilotKit` 提供者，将 `runtimeUrl` 指向运行时，RSC 边界规则                    | `references/provider-setup.md`                                                          |
| 插入 `CopilotChat` / `CopilotPopup` / `CopilotSidebar`，用插槽原语组合 `CopilotChatView` | `references/chat-components.md`                                                         |
| 通过 `useAttachments` 文件/图像附件——拖放、点击、粘贴、自定义上传                    | `references/attachments.md`                                                             |
| 客户端调试工具——`enableInspector`、`debug` 属性、懒加载的网页调试器                    | `references/debug-mode.md`                                                              |
| 读取/订阅智能体（`useAgent`）并推送全局上下文（`useAgentContext`）                     | `references/agent-access.md`                                                            |
| 声明智能体功能能力的特性门 UI（`useCapabilities`）                                        | `references/capabilities.md`                                                            |
| 构建多智能体 UI（每个面板的 `useAgent`、智能体范围的工具、键重挂载模式）                    | `references/switching-agents.md` (+ `switching-agents-recipes.md` 用于具体布局） |
| 列出/重命名/存档/删除持久的 Intelligence 线程（`useThreads`）                              | `references/threads.md` (**需要运行时 Intelligence 模式**)                        |
| 注册浏览器端工具（`useFrontendTool`）                                                           | `references/client-side-tools.md`                                                       |
| 渲染每个工具的 UI（`useRenderTool`、`useComponent`、`useDefaultRenderTool`、`useRenderToolCall`）         | `references/rendering-tool-calls.md`                                                    |
| 在用户批准后门控工具执行（`useHumanInTheLoop`）                                            | `references/human-in-the-loop.md`                                                       |
| 配置动态或静态建议药丸（`useConfigureSuggestions`、`useSuggestions`）                | `references/suggestions.md`                                                             |
| 渲染非聊天活动消息（`useRenderActivityMessage`）                                            | `references/rendering-activity-messages.md`                                             |
| 在特定消息之前/之后注入自定义 UI（`useRenderCustomMessages`）                               | `references/custom-message-renderers.md`                                                |

## 不变量和注意事项（一次性加载，在任何参考之前）

- `runtimeUrl` 是必需的；没有它，提供者在生产环境中会抛出错误。CopilotKit 智能体在运行时配置，永远不会在提供者上配置。
- `agents__unsafe_dev_only` 和 `selfManagedAgents` 是彼此的仅开发别名。**不适用于生产环境。** 请参阅 `packages/a2ui-renderer` 或 `spa-without-runtime` 生命周期技能以获取支持的 SPA 路径。
- `CopilotPanel` 不存在。v2 聊天组件来自 `react-core/v2`——**不是** `react-ui`（v2 `react-ui` 仅包含 CSS）。
- 不存在 `useAgents()` 钩子。通过 `copilotkit.subscribe({ onAgentsChanged })` 发现智能体。
- `useRenderToolCall` 是一个**解析器**（用于自定义聊天界面），**不是**注册钩子。使用 `useRenderTool` / `useComponent` / `useDefaultRenderTool` 进行注册。
- UI-Kit 检测规则——任何 `render` 或工具调用 UI 必须在使用原始 JSX 之前重用消费者的 shadcn / MUI / Chakra / Ant / Mantine 原语。这适用于 `client-side-tools`、`rendering-tool-calls` 和 `human-in-the-loop`。
- 工具调用 `status` 值是驼峰式：`'inProgress' | 'executing' | 'complete'`。进行中的参数是 `Partial<T>`。
- `useHumanInTheLoop` 合成的处理程序**必须**调用 `respond(result)`（包括拒绝路径），否则智能体运行会挂起。`respond` 在 `Executing` 状态之外是 `undefined`。在 `Executing` 状态中途卸载会放弃运行。
- 在 Intelligence 模式之外，`useThreads` 会因 `'Runtime URL is not configured'` 而出错。
- `useAgent` 返回 `{ agent, isReady }`。在 `isReady` 为 `false` 时，`agent` 是一个临时的替代品，当 `/info` 解析时会被**替换**为真实实例——`agent` 会改变引用，并且所有依赖它的副作用会重新运行。切勿在基于 `agent` 的副作用中初始化应用状态（关联映射、进行中的请求记录）。
- React 的 `key` 会丢弃**所有**它下面的状态。`key={activeAgent}` / `key={threadId}` 应该位于真正拥有该状态的最小子树——在布局级别的提供者上会静默清除无关的应用状态，并且在使用 Intelligence 时，线程 ID 在挂载后异步更改，因此会在交互中途触发。
- `v1 → v2` 迁移重命名：`useCopilotAction` → `useFrontendTool` + `useHumanInTheLoop`；`imageUploadsEnabled` → `attachments`。请参阅 `v1-to-v2-migration` 生命周期技能。

## 一次性阅读的顺序

1. `provider-setup` — 挂载提供者。
2. `chat-components` — 连接聊天界面。
3. `agent-access` — 与智能体通信。
4. `client-side-tools` + `rendering-tool-calls` — 添加工具调用 UI。
5. 根据你的功能需求，加载其他内容。
