# Genkit Go

Genkit Go 是一款面向 Go 语言的 AI SDK，通过统一接口为模型提供商提供生成、结构化输出、流式传输、工具调用、提示词与流程等功能。

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

## Core Features

根据实际需求加载相应的参考内容：

| Feature | Reference | When to load |
| --- | --- | --- |
| Initialization | [references/getting-started.md](references/getting-started.md) | 配置 `genkit.Init`、插件、`*Genkit` 实例模式 |
| Generation | [references/generation.md](references/generation.md) | `Generate`、`GenerateText`、`GenerateData`、流式传输、输出格式 |
| Prompts | [references/prompts.md](references/prompts.md) | `DefinePrompt`、`DefineDataPrompt`、`.prompt` 文件、schemas |
| Tools | [references/tools.md](references/tools.md) | `DefineTool`、工具中断、`RestartWith`/`RespondWith` |
| Middleware | [references/middleware.md](references/middleware.md) | `ai.Middleware`、`ai.WithUse`、Hooks（Generate/Model/Tool），内置（`Retry`、`Fallback`、`ToolApproval`、`Filesystem`、`Skills`） |
| Flows & HTTP | [references/flows-and-http.md](references/flows-and-http.md) | `DefineFlow`、`DefineStreamingFlow`、`genkit.Handler`、HTTP 服务 |
| Model Providers | [references/providers.md](references/providers.md) | Google AI、Vertex AI、Anthropic、OpenAI 兼容、Ollama 配置 |

## Genkit CLI

检查是否已安装：`genkit --version`

**安装：**
```bash
curl -sL cli.genkit.dev | bash
```

**关键命令：**

```bash
# 在 http://localhost:4000 启动带开发者界面（链路追踪、流程测试）的应用
genkit start -- go run .
genkit start -o -- go run .   # 也会打开浏览器

# 直接通过 CLI 运行流程
genkit flow:run myFlow '{"data": "input"}'
genkit flow:run myFlow '{"data": "input"}' --stream   # 支持流式传输
genkit flow:run myFlow '{"data": "input"}' --wait      # 等待完成

# 查询 Genkit 文档
genkit docs:search "streaming" go
genkit docs:list go
genkit docs:read go/flows.md
```

详见 [references/getting-started.md](references/getting-started.md) 以了解完整的 CLI 及开发者界面详情。

## Key Guidance

- **显式传递 `g`。** `genkit.Init` 返回的 `*Genkit` 实例是中央注册表。请将其传递给所有 Genkit 函数，而非将其存储为全局变量。这是 SDK 中贯穿始终的核心模式。
- **将 AI 逻辑封装在流程中。** 流程为您提供链路追踪、可观测性、通过 `genkit.Handler` 进行的 HTTP 部署，以及从开发者界面和 CLI 进行测试的能力。任何值得保留的生成调用都应置于流程中。
- **在输出类型上使用 `jsonschema:"description=..."` 结构体标签。** 模型通过这些描述来理解每个字段应包含的内容。缺少这些标签会导致结构化输出质量大幅下降。
- **编写良好的工具描述。** 模型根据描述字符串决定是否调用工具。模糊的描述会导致工具调用遗漏或错误。
- **为复杂提示词使用 `.prompt` 文件。** 它们将提示词内容与 Go 代码分离，支持 Handlebars 模板，且无需重新编译即可迭代。对于简单、单行的场景，使用代码定义的提示词更为合适。
- **优先使用内置中间件，而非自行编写。** `Retry`、`Fallback`、`ToolApproval`、`Filesystem` 和 `Skills` 涵盖了常见的横切需求，并可通过 `ai.WithUse` 组合使用。详见 [references/middleware.md](references/middleware.md)。当您需要编写自定义中间件时，应在 `New` 捕获的闭包中分配每次调用的状态，并保护所有被 `WrapTool` 修改的内容，因为工具可能会并发运行。
- **查询最新的模型 ID。** 模型名称频繁变更。请查阅提供商的文档获取当前模型 ID，而非依赖硬编码名称。详见 [references/providers.md](references/providers.md)。
