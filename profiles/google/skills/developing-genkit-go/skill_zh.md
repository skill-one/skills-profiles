# Genkit Go

Genkit Go 是一个 Go 语言的 AI SDK，它通过统一的接口提供生成、结构化输出、流式处理、工具调用、提示和流程等功能，并支持跨模型提供商使用。

## Hello World

```go
package main

import (
	"context"
	"fmt"
	"log"
	"net/http"

	"github.com/genkit-ai/genkit/go/ai"
	"github.com/genkit-ai/genkit/go/genkit"
	"github.com/genkit-ai/genkit/go/plugins/googlegenai"
	"github.com/genkit-ai/genkit/go/plugins/server"
)

func main() {
	ctx := context.Background()
	g := genkit.Init(ctx, genkit.WithPlugins(&googlegenai.GoogleAI{}))

	genkit.DefineFlow(g, "jokeFlow", func(ctx context.Context, topic string) (string, error) {
		return genkit.GenerateText(ctx, g,
			ai.WithModelName("googleai/gemini-flash-latest"),
			ai.WithPrompt("Tell me a joke about %s", topic),
		)
	})

	mux := http.NewServeMux()
	for _, f := range genkit.ListFlows(g) {
		mux.HandleFunc("POST /"+f.Name(), genkit.Handler(f))
	}
	log.Fatal(server.Start(ctx, "127.0.0.1:8080", mux))
}
```

## 核心功能

根据您的需求加载相应的参考文档：

| 功能       | 参考文档                                  | 加载时机                               |
| ---------- | ----------------------------------------- | ------------------------------------- |
| 初始化     | [references/getting-started.md](references/getting-started.md) | 设置 `genkit.Init`、插件、`*Genkit` 实例模式 |
| 生成       | [references/generation.md](references/generation.md) | `Generate`、`GenerateText`、`GenerateData`、流式处理、输出格式 |
| 提示       | [references/prompts.md](references/prompts.md) | `DefinePrompt`、`DefineDataPrompt`、`.prompt` 文件、模式 |
| 工具       | [references/tools.md](references/tools.md) | `DefineTool`、工具中断、`RestartWith`/`RespondWith` |
| 中间件     | [references/middleware.md](references/middleware.md) | `ai.Middleware`、`ai.WithUse`、`Hooks`（生成/模型/工具）、内置（`Retry`、`Fallback`、`ToolApproval`、`Filesystem`、`Skills`） |
| 流程与 HTTP | [references/flows-and-http.md](references/flows-and-http.md) | `DefineFlow`、`DefineStreamingFlow`、`genkit.Handler`、HTTP 服务 |
| 模型提供商 | [references/providers.md](references/providers.md) | Google AI、Vertex AI、Anthropic、OpenAI 兼容、Ollama 设置 |

## 代理（实验性）

Genkit Go 提供了一个**实验性**的代理 API，用于持久化、多轮对话（会话、快照、中断、分支、后台执行）。它受到限制：使用 `genkit.Init(ctx, genkit.WithExperimental())` 初始化，或者使用构造函数会触发恐慌。服务器构造函数来自 `genkit/exp`（别名 `genkitx`）；类型和选项来自 `ai/exp`（别名 `aix`）；会话存储来自 `ai/exp/localstore`。

- **代理还是流程？** 如果任务是会话式、多轮的，或者描述为“代理”、“助手”或“聊天机器人”，请使用 `genkitx.DefineAgent` 构建，而不是手动编写 `Generate` + 工具循环的流程。仅对于单次、无状态的生成，才使用普通流程。

详细信息请参阅：

-   [代理](references/agents.md)：定义/服务代理、运行轮次以及客户端与服务器管理的状态（从这里开始）。
-   [会话与持久化](references/agents-sessions.md)：会话存储（`localstore.NewInMemorySessionStore`/`NewFileSessionStore`）和快照。
-   [人工参与/中断](references/agents-human-in-the-loop.md)：暂停以获取批准/输入并恢复。
-   [分支](references/agents-branching.md)：从快照分叉对话。
-   [后台代理](references/agents-background.md)：分离长时间运行的轮次并轮询。
-   [处理状态](references/agents-state.md)：类型化的自定义会话状态，作为 JSON 补丁流式传输。
-   [工件](references/agents-artifacts.md)：生成和读取命名的交付物。
-   [多代理编排](references/agents-multi-agent.md)：委派给子代理。
-   [高级自定义代理](references/agents-custom.md)：使用 `DefineCustomAgent` 完全控制轮次。
-   [部署代理](references/agents-deployment.md)：使用 `genkit.Handler` 通过 HTTP 服务代理。

## 生成式 UI（A2UI）

Genkit Go 提供了一个**A2UI**（代理到 UI）插件（`github.com/genkit-ai/genkit/go/plugins/a2ui/exp`，导入为 `a2uix`），允许代理流式传输交互式 UI **表面**（卡片、列表、表单、按钮），而不仅仅是文本。整个集成是通过在生成调用或代理内联提示上使用 `ai.WithUse` 添加的 `&a2uix.Surfaces{}` 模型中间件。**Go 仅作为服务器使用：它没有 A2UI 客户端/渲染器。** 使用 JS 或 Dart/Flutter 客户端与您的 Go 代理通过 HTTP 通信来渲染表面（服务器和客户端在二进制层面上是兼容的）。

-   [A2UI](references/a2ui.md)：服务器中间件、选项、自定义目录和安全性。对于客户端（渲染表面），请参考 Genkit JS 或 Dart 技能中的 A2UI 参考。

## Genkit CLI（推荐）

`genkit start` 以非侵入式方式包装任何使用 Genkit 库的 Go 程序，在不更改程序的情况下运行它，同时捕获每个 Genkit 操作的跟踪，以便您可以在终端中证明工具实际上被调用并检查模型 I/O，即使对于无头检查也是如此。它转发 stdio，因此依赖 stdin/stdout 的交互式 CLI 工具可以正常工作而不会出现问题。直接运行应用程序（`go run .`）会跳过跟踪捕获，因此您是在盲目地调试。使用 `genkit --version` 检查安装情况。

**安装：**
```bash
curl -sL cli.genkit.dev | bash
```

**主要模式（默认）：** 在您的正常运行命令前缀 `genkit start --`。这将收集您的程序运行时任何 Genkit 代码的遥测数据，无论是由开发 UI、您自己的 Web 服务器/Web UI 还是普通脚本触发。启动开发者 UI（通常是 http://localhost:4000）以运行流程、模型和代理沙盒，以及浏览跟踪：
```bash
genkit start -- go run .
genkit start --noui -- go run .   # 相同，但不包含 Dev UI（仍然是一个持久化服务器）
genkit start -o -- go run .       # 同时打开浏览器
```
`genkit start` 运行，直到您使用 Ctrl+C 停止它。这对于常见情况是预期的和正确的：您的 Web/移动应用程序调用的服务器，或者您自己退出的交互式 CLI。`--noui` 仅丢弃 Dev UI；它**不是**一个一次性命令，并且不会自行退出。**不要**在自动化/非交互式环境中使用 `genkit start` 作为阻塞步骤；使用 `flow:run`（下方）来执行此操作。

**非交互式使用（代理/CI）：** 在 `--` 之前添加全局 `--non-interactive` 标志，以便 CLI 使用默认值并且永远不会在提示上阻塞（例如首次运行的分析通知）：`genkit start --non-interactive -- go run .`（与 `flow:run` 也适用）。

**运行流程（`flow:run`）：** 从 CLI 通过名称调用特定流程。在 `--` 后附加您的运行命令以仅为此运行启动运行时（命令按原样运行以注册您的流程）：
```bash
genkit flow:run myFlow '{"data": "input"}' -- go run .
genkit flow:run myFlow '{"data": "input"}' --stream -- go run .   # 带流式处理
genkit flow:run myFlow '{"data": "input"}' --wait -- go run .     # 等待完成
```
这是**自终止的**：它运行一次流程，打印一个 `Trace ID`，然后退出，因此它是快速、非交互式检查的正确选择（与 `genkit start` 不同）。此运行的跟踪可以使用下方的跟踪命令进行检查。

**使用跟踪进行调试：** 最快的方法是查看提示、模型输入/输出、工具调用、延迟和错误。在 `genkit start` 下的任何运行后从终端检查：
```bash
genkit trace:list                        # 查找最近的跟踪 ID
genkit trace:get <traceId>               # 完整跟踪详细信息（输入、输出、工具调用、错误）
genkit trace:get <traceId> --format json # 机器可读的 JSON，可以安全地管道传输到 jq 或其他解析器
```

对于机器可读的输出，传递 `--format json` 以获取干净的 JSON，可以管道传输到 `jq` 或其他解析器。**默认**输出是面向人类的（横幅/日志行、大型跟踪可能的截断），因此不要直接管道这种形式；使用 `--format json`、grep 或 Dev UI 跟踪查看器。

**文档：**
```bash
genkit docs:search "streaming" go
genkit docs:list go
genkit docs:read go/flows.md
```

有关完整 CLI 和开发者 UI 的详细信息，请参阅 [references/getting-started.md](references/getting-started.md)。

## 关键指导

-   **显式传递 `g`。** 由 `genkit.Init` 返回的 `*Genkit` 实例是中央注册表。将 `g` 传递给所有 Genkit 函数，而不是将其作为全局存储。这是整个 SDK 的核心模式。
-   **将 AI 逻辑包装在流程中。** 流程为您提供跟踪、可观察性、通过 `genkit.Handler` 的 HTTP 部署，以及从开发者 UI 和 CLI 进行测试的能力。任何值得保留的生成调用都应该存在于流程中。
-   **使用跟踪而不是盲目运行来验证。** 直接运行应用程序（`go run .`）不会捕获开发跟踪。请参阅 [Genkit CLI](#genkit-cli-recommended) 部分了解如何运行您的应用程序并捕获跟踪。
-   **在输出类型上使用 `jsonschema:"description=..."` 结构标签。** 模型使用这些描述来理解每个字段应包含的内容。没有它们，结构化输出质量会显著下降。
-   **编写良好的工具描述。** 模型根据它们的描述字符串决定调用哪些工具。模糊的描述会导致错过或不正确的工具调用。
-   **使用 `.prompt` 文件处理复杂的提示。** 它们将提示内容与 Go 代码分离，支持 Handlebars 模板，并且可以在不重新编译的情况下迭代。代码定义的提示适用于简单、单行的案例。
-   **在编写之前使用内置中间件。** `Retry`、`Fallback`、`ToolApproval`、`Filesystem` 和 `Skills` 覆盖常见的横切需求，并通过 `ai.WithUse` 互相组合。请参阅 [references/middleware.md](references/middleware.md)。当您编写自定义中间件时，在由 `New` 捕获的闭包中分配每次调用的状态，并保护 `WrapTool` 修改的任何内容，因为工具可能会并发运行。
-   **查找最新的模型 ID。** 模型名称经常变化。检查提供商文档以获取当前模型 ID，而不是依赖硬编码的名称。请参阅 [references/providers.md](references/providers.md)。
