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
			ai.WithPrompt("给我讲一个关于 %s 的笑话", topic),
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

根据你的需求加载相应的参考文档：

| 功能 | 参考文档 | 加载时机 |
| --- | --- | --- |
| 初始化 | [参考资料/getting-started.md](references/getting-started.md) | 设置 `genkit.Init`、插件、`*Genkit` 实例模式 |
| 生成 | [参考资料/generation.md](references/generation.md) | `Generate`、`GenerateText`、`GenerateData`、流式处理、输出格式 |
| 提示 | [参考资料/prompts.md](references/prompts.md) | `DefinePrompt`、`DefineDataPrompt`、`.prompt` 文件、模式 |
| 工具 | [参考资料/tools.md](references/tools.md) | `DefineTool`、工具中断、`RestartWith`/`RespondWith` |
| 中间件 | [参考资料/middleware.md](references/middleware.md) | `ai.Middleware`、`ai.WithUse`、`Hooks`（生成/模型/工具）、内置的（`Retry`、`Fallback`、`ToolApproval`、`Filesystem`、`Skills`） |
| 流程与 HTTP | [参考资料/flows-and-http.md](references/flows-and-http.md) | `DefineFlow`、`DefineStreamingFlow`、`genkit.Handler`、HTTP 服务 |
| 模型提供商 | [参考资料/providers.md](references/providers.md) | Google AI、Vertex AI、Anthropic、OpenAI 兼容、Ollama 设置 |

## Genkit CLI

检查是否已安装：`genkit --version`

**安装：**
```bash
curl -sL cli.genkit.dev | bash
```

**主要命令：**

```bash
# 启动应用并开启开发者界面（跟踪、流程测试）在 http://localhost:4000
genkit start -- go run .
genkit start -o -- go run .   # 同时打开浏览器

# 从 CLI 直接运行流程
genkit flow:run myFlow '{"data": "input"}'
genkit flow:run myFlow '{"data": "input"}' --stream   # 带流式处理
genkit flow:run myFlow '{"data": "input"}' --wait      # 等待完成

# 查找 Genkit 文档
genkit docs:search "streaming" go
genkit docs:list go
genkit docs:read go/flows.md
```

有关完整 CLI 和开发者界面的详细信息，请参阅 [参考资料/getting-started.md](references/getting-started.md)。

## 关键指南

- **显式传递 `g`。** `genkit.Init` 返回的 `*Genkit` 实例是中央注册表。将 `g` 传递给所有 Genkit 函数，而不是将其存储为全局变量。这是 SDK 中的核心模式。
- **将 AI 逻辑封装在流程中。** 流程提供跟踪、可观察性、通过 `genkit.Handler` 的 HTTP 部署，以及从开发者界面和 CLI 进行测试的能力。任何值得保留的生成调用都应该存在于流程中。
- **在输出类型上使用 `jsonschema:"description=..."` 结构体标签。** 模型使用这些描述来理解每个字段应包含的内容。没有它们，结构化输出质量会显著下降。
- **编写良好的工具描述。** 模型根据工具的描述字符串决定调用哪些工具。模糊的描述会导致错过或错误的工具调用。
- **使用 `.prompt` 文件处理复杂的提示。** 它们将提示内容与 Go 代码分离，支持 Handlebars 模板化，并且可以在不重新编译的情况下迭代。代码定义的提示适用于简单的单行情况。
- **在编写自定义中间件之前使用内置中间件。** `Retry`、`Fallback`、`ToolApproval`、`Filesystem` 和 `Skills` 覆盖常见的跨切需求，并通过 `ai.WithUse` 互相组合。参见 [参考资料/middleware.md](references/middleware.md)。当你编写自定义中间件时，在 `New` 捕获的闭包中分配每次调用的状态，并保护 `WrapTool` 修改的内容，因为工具可能会并发运行。
- **查找最新的模型 ID。** 模型名称经常变化。检查提供商文档以获取当前的模型 ID，而不是依赖硬编码的名称。参见 [参考资料/providers.md](references/providers.md)。
