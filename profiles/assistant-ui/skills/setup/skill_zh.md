# assistant-ui 安装设置

**始终查阅 [assistant-ui.com/llms.txt](https://www.assistant-ui.com/llms.txt) 获取最新 API。**

`assistant-ui` CLI 用于构建项目、添加组件以及保持安装的当前状态。本技能涵盖了 CLI 的端到端内容以及决定接下来连接哪个运行时适配器的决策；安装样式化 UI 本身是 [elements](../elements/SKILL.md)。

## 参考

- [./references/ai-sdk.md](./references/ai-sdk.md) -- `@assistant-ui/ai-sdk` (v7): 传输、前端工具、多步骤、审批、报价上下文、令牌使用、历史记录、`useAISDKRuntime`
- [./references/ai-sdk-legacy.md](./references/ai-sdk-legacy.md) -- 固定的 `@assistant-ui/react-ai-sdk` (v6, v5) 和 `@assistant-ui/react-data-stream` (v4) 设置
- [./references/langgraph.md](./references/langgraph.md) -- `@assistant-ui/react-langgraph`: 流式传输、中断、消息编辑、线程、代理状态
- [./references/langchain.md](./references/langchain.md) -- `@assistant-ui/react-langchain`: 基于 `useStream` 的 LangGraph 适配器及其与 react-langgraph 的比较
- [./references/google-adk.md](./references/google-adk.md) -- `@assistant-ui/react-google-adk`: 流式传输、工具确认、认证流程、输入请求、工件
- [./references/a2a.md](./references/a2a.md) -- `@assistant-ui/react-a2a`: `A2AClient`、任务状态、工件、多租户
- [./references/ag-ui.md](./references/ag-ui.md) -- `@assistant-ui/react-ag-ui`: 代理状态、中断、子代理嵌套、自定义事件
- [./references/eve.md](./references/eve.md) -- `@assistant-ui/eve`: 会话、连接器授权、`withEve` + `withAui`
- [./references/opencode.md](./references/opencode.md) -- `@assistant-ui/react-opencode`: 权限、问题、子代理任务、会话扩展
- [./references/claude-managed-agents.md](./references/claude-managed-agents.md) -- 通过 `useExternalStoreRuntime` 连接 Anthropic 管理代理会话
- [./references/custom-backend.md](./references/custom-backend.md) -- `useLocalRuntime` 和 `useExternalStoreRuntime` 用于没有专用适配器的后端
- [./references/tanstack.md](./references/tanstack.md) -- Vite + TanStack Router/Start 设置
- [./references/mastra.md](./references/mastra.md) -- 基于 AI SDK 运行时的 Mastra 全栈和分离服务器模式
- [./references/cloudflare-agents.md](./references/cloudflare-agents.md) -- 通过 `@cloudflare/ai-chat` 和 `useAISDKRuntime` 的持久对象代理
- [./references/providers.md](./references/providers.md) -- LLM 网关、本地开发的 ChatGPT/Codex 订阅以及 Electron
- [./references/devtools.md](./references/devtools.md) -- `@assistant-ui/react-devtools`、`DevToolsModal`、自定义插件

## CLI 决策流程

- 新应用 / 空目录: `npx assistant-ui@latest create <name>`
- 已存在 `package.json` 的项目: `npx assistant-ui@latest init`
- 向已存在运行时的项目添加一个或多个样式化组件: `npx assistant-ui@latest add <items...>` (参见 [elements](../elements/SKILL.md))
- 提升 `@assistant-ui/*` 版本: `npx assistant-ui@latest update`
- 跨越破坏性版本迁移: `npx assistant-ui@latest upgrade` (有关完整迁移映射，参见 [update](../update/SKILL.md))
- 将编辑器连接到文档: `npx assistant-ui@latest mcp`
- 收集用于错误报告的环境信息: `npx assistant-ui@latest info`
- 诊断版本漂移或损坏的安装: `npx assistant-ui@latest doctor`
- 使用这些技能预加载的 Claude 代码打开: `npx assistant-ui@latest agent "add a chat sidebar"`

## create

```bash
npx assistant-ui@latest create my-app
npx assistant-ui@latest create my-app -t cloud-clerk
npx assistant-ui@latest create my-app -e with-langgraph
npx assistant-ui@latest create my-app --native   # Expo，相当于 -e with-expo
npx assistant-ui@latest create my-app --ink      # React Ink，相当于 -e with-react-ink
```

模板 (`-t, --template`):

| 模板 | 内容 |
| --- | --- |
| `default` | Vercel AI SDK, `useChatRuntime` |
| `minimal` | 仅包含本地组件的起点 |
| `cloud` | AssistantCloud 支持的持久化 |
| `cloud-clerk` | 使用 Clerk 认证的 AssistantCloud 持久化 |
| `langchain` | 基于 `@assistant-ui/react-langchain` 适配器的 LangGraph 起始器 |
| `mcp` | MCP 工具加上 MCP Apps 渲染器 |
| `eve` | `eve/next` 上的 Eve 代理 |

没有 `langgraph` 模板；基于 LangGraph 的起始器是 `langchain` (`react-langchain`)，而 `-e with-langgraph` 会构建原始的 `@assistant-ui/react-langgraph` 适配器。

示例 (`-e, --example`)，每个都是一个完整功能演示：

| 示例 | 演示 |
| --- | --- |
| `with-ai-sdk-v7` | Vercel AI SDK v7 |
| `with-eve` | Eve 代理集成 |
| `with-artifacts` | 带实时预览的 HTML 工件渲染 |
| `with-langgraph` | 带自定义工具的 LangGraph 代理 |
| `with-google-adk` | Google ADK 代理 |
| `with-ag-ui` | AG-UI 协议 |
| `with-cloud` | AssistantCloud 持久化 |
| `with-assistant-transport` | 通过 Assistant Transport 的自定义后端 |
| `with-resumable-stream` | 在响应中途重新加载后仍然存在的可恢复流 |
| `with-chain-of-thought` | 推理、工具调用、来源引用 |
| `with-external-store` | 外部消息存储 |
| `with-interactables` | AI 驱动的交互式 UI 组件 |
| `with-openui` | OpenUI 生成式 UI |
| `with-custom-thread-list` | 自定义线程列表 UI |
| `with-react-hook-form` | React Hook Form 集成 |
| `with-ffmpeg` | FFmpeg 视频处理工具 |
| `with-elevenlabs-conversational` | 实时语音，ElevenLabs |
| `with-livekit` | 实时语音，LiveKit |
| `with-elevenlabs-scribe` | 语音转录，ElevenLabs |
| `with-expo` | Expo / React Native (也相当于 `--native`) |
| `with-react-ink` | 终端 UI 聊天 (也相当于 `--ink`) |
| `with-react-router` | React Router v7 |
| `with-tanstack` | TanStack Start |

其他标志：`-p, --preset <name-or-url>` 通过 `shadcn add` 在构建后应用游乐场预设（例如 `chatgpt`），并且可以与 `--template` 结合使用，但不能与 `--example`、`--native` 或 `--ink` 结合使用；`--use-npm` / `--use-pnpm` / `--use-yarn` / `--use-bun` 固定包管理器；`--skip-install` 跳过安装包；`--skills` / `--no-skills` 添加或跳过此存储库的代理技能（在 TTY 中省略时会提示）。在非交互式 shell 中，省略的 `-t`/`-e` 默认为 `default` 模板，省略的项目目录默认为 `my-aui-app`。

## init

```bash
npx assistant-ui@latest init
```

对于**已存在**的 `package.json` 项目：检测项目，运行 `shadcn add` 以快速启动组件，添加默认组件并配置 TypeScript 路径。标志：`-y, --yes` 跳过确认提示（用于 CI 或代理 shell），`-o, --overwrite` 替换现有文件，`-c, --cwd <dir>` 选择项目，`--use-npm` / `--use-pnpm` / `--use-yarn` / `--use-bun` 固定包管理器，以及 `--skip-install` 跳过安装包。不使用 `package.json` 运行时，它会转发到 `create`。

## add

```bash
npx assistant-ui@latest add thread thread-list
```

一旦运行时连接，`add` 会从 assistant-ui 注册 (`r.assistant-ui.com`) 获取样式化组件，安装它们的 npm 依赖项和 TypeScript 类型并解析注册依赖项 (`thread` 还会拉取 `markdown-text`、`tool-fallback`、`reasoning` 等)。`-y, --yes` 跳过确认提示（默认为 `true`），`-o, --overwrite` 替换现有文件，以及 `-p, --path` 重新定向安装目录。有关完整目录、连接运行时的（`.aui`）与独立分拆以及 Radix/Base UI 样式感知注册 URL，请参阅 [elements](../elements/SKILL.md)。

## 保持安装当前状态

| 命令 | 目的 |
| --- | --- |
| `assistant-ui update [--dry]` | 将所有已安装的 `@assistant-ui/*` 包提升到最新版本；`--dry` 会打印命令而不是运行它 |
| `assistant-ui upgrade [-d] [-p] [--verbose]` | 按当前主版本顺序运行所有捆绑的 codemod；`-d` 干运行，`-p` 打印转换后的文件 |
| `assistant-ui codemod <name> <source> [-d] [-p]` | 运行一个命名的 codemod 而不是完整的升级序列 |
| `assistant-ui mcp [--cursor\|--windsurf\|--vscode\|--zed\|--claude-code\|--claude-desktop]` | 注册托管 MCP 文档端点 (`https://www.assistant-ui.com/mcp`) 以供命名的 IDE 使用，或本地 `@assistant-ui/mcp-docs-server` stdio 服务器用于 Zed 和 Claude Desktop，它只启动本地服务器 |
| `assistant-ui info` | 打印 CLI、操作系统、包管理器、框架、已安装的 `@assistant-ui/*`/生态系统版本，作为用于错误报告的可粘贴块 |
| `assistant-ui doctor [--no-network]` | 诊断现有安装（`@assistant-ui/*` 包之间的版本漂移、配置错误）；`--no-network` 跳过 npm 注册表的最新版本检查 |
| `assistant-ui agent "<prompt>" [--dry]` | 启动预加载 assistant-ui 技能和给定提示的 Claude Code；`--dry` 会打印命令而不是运行它 |

永远不要对当前（0.15.x）安装运行 `codemod v0-8/ui-package-split`；其 `@assistant-ui/react-ui` 目标早于当前运行时，并且 `upgrade` 已经排除了它。有关完整版本表、迁移顺序和 0.15.x 后续移动（注册路径、`AuiConfig`、`threads.selectionChanged`），请参阅 [update](../update/SKILL.md)。

## 选择运行时

根据框架，当已有适配器适合时：

| 后端 | 钩子 | 包 | 参考 |
| --- | --- | --- | --- |
| Vercel AI SDK v7 | `useChatRuntime` | `@assistant-ui/ai-sdk` | [ai-sdk.md](./references/ai-sdk.md) |
| LangGraph Cloud (原始 SDK) | `useLangGraphRuntime` | `@assistant-ui/react-langgraph` | [langgraph.md](./references/langgraph.md) |
| LangGraph Cloud (`useStream`) | `useStreamRuntime` | `@assistant-ui/react-langchain` | [langchain.md](./references/langchain.md) |
| Google ADK (JS 或 Python) | `useAdkRuntime` | `@assistant-ui/react-google-adk` | [google-adk.md](./references/google-adk.md) |
| A2A v1.0 代理服务器 | `useA2ARuntime` | `@assistant-ui/react-a2a` | [a2a.md](./references/a2a.md) |
| AG-UI 代理服务器 | `useAgUiRuntime` | `@assistant-ui/react-ag-ui` | [ag-ui.md](./references/ag-ui.md) |
| Eve (`eve/next`) | `useEveAgentRuntime` | `@assistant-ui/eve` | [eve.md](./references/eve.md) |
| OpenCode 服务器 (实验性) | `useOpenCodeRuntime` | `@assistant-ui/react-opencode` | [opencode.md](./references/opencode.md) |
| Claude 管理代理会话 | `useExternalStoreRuntime` + `useRemoteThreadListRuntime` | `@assistant-ui/react` (无专用适配器) | [claude-managed-agents.md](./references/claude-managed-agents.md) |

根据需求，当没有框架适配器适合时（完整决策树在 [custom-backend.md](./references/custom-backend.md)）：

| 您需要 | 钩子 | 参考 |
| --- | --- | --- |
| 对您的 API 的 `fetch` 调用；运行时拥有状态 | `useLocalRuntime` | [custom-backend.md](./references/custom-backend.md) |
| 消息已经存在于 redux、zustand、tanstack-query 中 | `useExternalStoreRuntime` | [custom-backend.md](./references/custom-backend.md) |
| 后端已经发出数据流协议 | `useDataStreamRuntime` | [../streaming/SKILL.md](../streaming/SKILL.md) |
| 后端流式传输完整的代理状态快照，或需要双向命令 | `useAssistantTransportRuntime` | [../streaming/SKILL.md](../streaming/SKILL.md) |

框架和提供者连接指南，所有内容都建立在上述 AI SDK 运行时之上，而不是专用适配器：[mastra.md](./references/mastra.md)（全栈或分离服务器），[cloudflare-agents.md](./references/cloudflare-agents.md)（持久对象代理），以及 [providers.md](./references/providers.md)（用于路由和 BYOK 的 LLM 网关、本地开发的 ChatGPT/Codex 订阅以及 Electron 的托管后端与本地主进程分拆）。

## 平台目标

| 目标 | 包 | 构建 | 技能 |
| --- | --- | --- | --- |
| Web (React) | `@assistant-ui/react` | `create` | 本技能，[elements](../elements/SKILL.md) |
| Expo / React Native | `@assistant-ui/react-native` + `@assistant-ui/metro` | `create <name> --native` (或 `-e with-expo`) | [react-native](../react-native/SKILL.md) |
| 终端 | `@assistant-ui/react-ink` + `@assistant-ui/react-ink-markdown` | `create <name> --ink` (或 `-e with-react-ink`) | [ink](../ink/SKILL.md) |

基于 Vite 的 Web 应用（TanStack Start、纯 Vite、Nuxt）不是 `create` 模板；有关手动设置和来自 `@assistant-ui/vite` 的 `aui()` 编译器插件，请参阅 [tanstack.md](./references/tanstack.md)。

## 常见陷阱

**`npx assistant-ui create` 选择默认模板且无提示**
- 标准输入不是 TTY（CI、代理 shell）。显式传递 `-t`/`-e` 而不是依赖交互式选择器。

**"只能提供一个构建选择器"**
- `--template`、`--example`、`--native` 和 `--ink` 互斥。`--preset` 可以与 `--template` 结合使用，但不能与其他三者结合使用。

**`init` 在 CI 或代理 shell 中挂起**
- 传递 `-y, --yes` 以跳过其确认提示；当它应该替换先前运行留下的文件时，添加 `-o, --overwrite`。

**对 `@assistant-ui/styles` 或 `@assistant-ui/react-ui` 的依赖无法解析或安装**
- 这两个包都已退役（`@assistant-ui/styles` 在 npm 上已标记为弃用）。样式现在来自 CLI 复制到您项目中的元素；删除依赖项并运行 `npx assistant-ui@latest add thread`。

**`Cannot find module '@/components/assistant-ui/thread'`**
- 组件已移动到 `elements/` 下，在连接运行时的文件上带有 `.aui` 后缀：`@/components/assistant-ui/elements/thread.aui`。参见 [elements](../elements/SKILL.md)。

**`add` 重新安装您已自定义的组件**
- 故意传递 `-o, --overwrite`，或者先将您的编辑移到一边；普通的 `add` 会跳过已存在的文件。

**注册安装在 `create` 中中途失败**
- `create` 仍然会完成项目；一旦注册或网络问题解决，在项目目录中重新运行打印的重试命令。
