# Genkit Dart

Genkit Dart 是一个 Dart 的 AI SDK，它为代码生成、结构化输出、工具、流程和 AI 代理提供了统一的接口。

## 核心特性和使用方法
如果你在初始化 Genkit (`Genkit()`)、生成 (`ai.generate`)、工具 (`ai.defineTool`)、流程 (`ai.defineFlow`)、嵌入 (`ai.embedMany`)、流式传输或调用远程流程端点时需要帮助，请加载核心框架参考：
[references/genkit.md](references/genkit.md)

## 提示（Dotprompt）

`.prompt` 文件通过 YAML 前置部分和一个 Handlebars 模板将提示内容与 Dart 代码分离。参见 [references/dotprompt.md](references/dotprompt.md)：
`promptDir`、`ai.prompt()`（调用/流式传输/渲染）、变体、部分、通过 `defineSchema` 定义的命名模式，以及 `tools`/`maxTurns`/`returnToolRequests`/`use`（中间件）前置字段。`.prompt` 文件也可以通过 `definePromptAgent` 直接支持代理。

## 代理

Genkit Dart 提供了一个 **代理** API，用于持久化、多轮对话（会话、快照、中断、分支、后台执行、自定义状态、工件和多代理委托）。代理/会话/快照 API 是 **实验性** 的，并且位于可选导入之后：服务器 API 来自 `package:genkit/experimental.dart`（与 `package:genkit/genkit.dart` 一起），浏览器/HTTP 客户端来自 `package:genkit/experimental_client.dart`（与 `package:genkit/client.dart` 一起），以及 `dart:io` 扩展（如 `FileSessionStore`）来自 `package:genkit/experimental_io.dart`。这些入口点是 `@experimental`，因此导入它们会触发 `experimental_member_use` 分析器警告，你可以在 `analysis_options.yaml` 中抑制该警告。`remoteAgent` 客户端可以在任何 Dart 应用程序中工作，包括 **Flutter**，并且后端是完全可互换的——它可以与 Dart、JS/TypeScript 或 Go 实现的 Genkit 代理通过相同的 HTTP 协议进行通信。一些 Dart 特定的内容：中断被建模为返回 `.interrupt(...)` 的工具（没有 `defineInterrupt`），子代理委托使用来自 `package:genkit_middleware` 的 `agents()` 中间件，目前还没有 `artifacts()` 中间件（直接定义工件工具）。

更多详情请参见：

-   [代理](references/agents.md)：定义/服务代理和客户端管理状态（从这里开始）。
-   [会话和持久化](references/agents-sessions.md)：会话存储（`InMemorySessionStore`/`FileSessionStore`/`FirestoreSessionStore`）。
-   [人工参与/中断](references/agents-human-in-the-loop.md)：通过 `.interrupt(...)` 暂停以获取批准/输入并恢复。
-   [分支](references/agents-branching.md)：从快照中分叉对话。
-   [后台代理](references/agents-background.md)：分离长时间运行的回合并轮询。
-   [处理状态](references/agents-state.md)：带类型自定义会话状态，自动同步到客户端。
-   [工件](references/agents-artifacts.md)：生成和读取命名交付成果。
-   [多代理编排](references/agents-multi-agent.md)：使用 `agents()` 中间件委托给子代理。
-   [高级自定义代理](references/agents-custom.md)：`defineCustomAgent` 用于完整回合控制。
-   [部署代理](references/agents-deployment.md)：使用 `genkit_shelf` 通过 HTTP 服务代理（多个代理，CORS）。

## 生成式 UI (A2UI)

Genkit Dart 有一个 **A2UI**（代理到 UI）插件 (`genkit_a2ui`)，它允许代理流式传输交互式 UI **表面**（卡片、列表、表单、按钮），而不仅仅是散文。整个服务器端集成是代理（或 `ai.generate`）的 `use` 列表中的 `a2ui()` 模型中间件；Flutter 客户端使用 [`genui`](https://pub.dev/packages/genui) 包和 `package:genkit_a2ui/client.dart` 中的辅助工具渲染表面。Dart 特定：你必须将 `A2uiPlugin()` 注册在 `Genkit(plugins: [...])` 中（与 JS 不同，中间件是从注册表中按名称解析的）。

-   [A2UI](references/a2ui.md)：服务器中间件、选项、Flutter/genui 客户端渲染、用户操作/表单、自定义目录，以及安全/信任边界。

## Genkit CLI（推荐）

`genkit start` 无干扰地包装任何使用 Genkit 库的 Dart 程序，在运行时捕获每个 Genkit 操作的跟踪，以便你可以在终端中证明工具实际上被调用并检查模型 I/O，即使对于无头检查也是如此。它转发 stdio，因此依赖 stdin/stdout 的交互式 CLI 工具可以正常工作。直接运行应用程序 (`dart run`) 会跳过跟踪捕获，因此你是在盲目地调试。使用 `genkit --version` 检查安装情况。

**安装：**
```bash
curl -sL cli.genkit.dev | bash # 原生 CLI
# 或
npm install -g genkit-cli # 通过 npm
# 或直接使用 npx 执行命令，无需全局安装（在所有 genkit 命令前添加前缀）：
# npx genkit-cli start -- dart run main.dart
```

**主要模式（默认）：** 在你的正常运行命令前缀 `genkit start --`。这将收集你的程序运行的所有 Genkit 代码的遥测数据，无论是由开发 UI、你自己的 Web 服务器/Web UI 还是普通脚本触发的。它启动开发者 UI（通常是 http://localhost:4000）以运行流程、模型和代理游乐场以及浏览跟踪：

```bash
genkit start -- dart run main.dart
genkit start --noui -- dart run main.dart   # 相同，但不显示 Dev UI（仍然是一个持久化服务器）
```
`genkit start` 运行，直到你使用 Ctrl+C 停止它。对于常见情况（你的 Web/移动应用程序调用的服务器，或你自己退出的交互式 CLI）这是预期的和正确的。`--noui` 只会丢弃 Dev UI；它不是一次性命令，并且不会自行退出。**不要**在自动化/非交互式环境中使用 `genkit start` 作为阻塞步骤；使用 `flow:run`（下方）来执行该操作。

**非交互式使用（代理/CI）：** 在 `--` 之前添加全局 `--non-interactive` 标志，以便 CLI 使用默认值并且永远不会在提示上阻塞（例如首次运行的分析通知）：`genkit start --non-interactive -- dart run main.dart`（与 `flow:run` 也兼容）。

**运行流程 (`flow:run`)：** 从 CLI 通过名称调用特定流程。在 `--` 后附加你的运行命令以仅为此运行启动运行时（命令按原样运行以注册你的流程）：
```bash
genkit flow:run myFlow '{"data": "input"}' -- dart run main.dart
```
这是 **自终止** 的：它运行一次流程，打印一个 `Trace ID`，然后退出，因此它是快速、非交互式检查的正确选择（与 `genkit start` 不同）。注意：`flow:run` 运行 **流程** (`ai.defineFlow`)，而不是代理；你不能直接 `flow:run` 代理 (`ai.defineAgent`)。要从 CLI 练习代理，请将一个回合包装在一个一次性流程中并运行该流程（参见 [代理](references/agents.md)）。此运行的跟踪可以使用下方的跟踪命令进行检查。

**注意：顶级 `final` 声明是惰性的。** 作为顶级定义的流程和代理仅在符号首次评估时注册到 Genkit。空的 `main()` 注册什么都没有，因此 `flow:run` 会因 `Process exited before runtime was ready` 而失败。从 `main()`（或导入一个执行该操作的模块）引用流程/代理符号，以便它们的 `define*` 调用实际上运行。

**使用跟踪进行调试：** 最快的方法是查看提示、模型输入/输出、工具调用、延迟和错误。在 `genkit start` 下的任何运行后从终端检查：
```bash
genkit trace:list                        # 查找最近的跟踪 ID
genkit trace:get <traceId>               # 完整跟踪详细信息（输入、输出、工具调用、错误）
genkit trace:get <traceId> --format json # 机器可读的 JSON，可以安全地管道传输到 jq 或其他解析器
```

对于机器可读的输出，传递 `--format json` 以获取干净的 JSON，可以管道传输到 `jq` 或其他解析器。**默认**输出是面向人类的（横幅/日志行，在大型跟踪上可能截断），因此不要直接管道该形式；使用 `--format json`、grep 或 Dev UI 跟踪查看器。

**文档：**
```bash
genkit docs:search "streaming" dart
genkit docs:list dart
genkit docs:read dart/flows.md
```

## 插件生态系统

Genkit 依赖于一系列插件来执行生成式 AI 操作、与外部 LLM 交互或托管 Web 服务器。

当被要求使用任何给定插件时，始终通过参考下面的相应参考来验证用法。当你需要知道插件的具体初始化参数、工具、模型和使用模式时，请加载参考：

| 插件名称 | 参考链接 | 描述 |
| ---- | ---- | ---- |
| `genkit_google_genai` | [references/genkit_google_genai.md](references/genkit_google_genai.md) | 加载用于 Google Gemini 插件接口用法。 |
| `genkit_anthropic` | [references/genkit_anthropic.md](references/genkit_anthropic.md) | 加载用于 Anthropic 插件接口以使用 Claude 模型。 |
| `genkit_openai` | [references/genkit_openai.md](references/genkit_openai.md) | 加载用于 OpenAI 插件接口以使用 GPT 模型、Groq 和自定义兼容端点。 |
| `genkit_middleware` | [references/genkit_middleware.md](references/genkit_middleware.md) | 加载用于特定代理行为的工具：`filesystem`、`skills` 和 `toolApproval` 中断。 |
| `genkit_mcp` | [references/genkit_mcp.md](references/genkit_mcp.md) | 加载用于模型上下文协议集成（服务器、主机和客户端功能）。 |
| `genkit_chrome` | [references/genkit_chrome.md](references/genkit_chrome.md) | 加载用于在 Chrome 浏览器中本地运行 Gemini Nano 使用 Prompt API。 |
| `genkit_shelf` | [references/genkit_shelf.md](references/genkit_shelf.md) | 加载用于使用 Dart Shelf 通过 HTTP 集成 Genkit Flow 操作。 |
| `genkit_firebase_ai` | [references/genkit_firebase_ai.md](references/genkit_firebase_ai.md) | 加载用于 Firebase AI 插件接口（通过 Vertex AI 的 Gemini API）。 |
| `genkit_a2ui` | [references/a2ui.md](references/a2ui.md) | 加载用于 A2UI（代理到 UI）：通过 `a2ui()` 中间件流式传输生成式 UI 表面，客户端使用 `genui` 渲染。 |

## 外部依赖项

每当你在工具、流程和提示中定义映射模式时，都必须使用 [schemantic](https://pub.dev/packages/schemantic) 库。要学习如何使用 schemantic，请确保你阅读 [references/schemantic.md](references/schemantic.md) 以了解如何实现类型安全的生成 Dart 代码。这在遇到符号（如 `@Schema()`、`SchemanticType`）或以 `$` 前缀命名的类时尤其相关。Genkit Dart 使用 schemantic 用于所有其数据模型，因此理解它是使用 Genkit Dart 的关键技能。

## 最佳实践

-   **代理还是流程？** 如果任务是会话式的、多轮的，或描述为“代理”、“助手”或“聊天机器人”，请使用 `ai.defineAgent`（参见 [代理](references/agents.md)）构建，而不是在流程中手滚 `generate` + 工具循环。仅对于单次、无状态的生成，才使用纯流程。
-   始终使用 `dart analyze` 在生成最终响应之前检查代码是否干净地编译。
-   始终使用 Genkit CLI 进行本地开发和调试。
-   使用跟踪进行验证，而不是盲目运行。直接运行应用程序 (`dart run`) 不会捕获开发跟踪。参见 [Genkit CLI](#genkit-cli-recommended) 部分了解如何运行你的应用程序并捕获跟踪。
