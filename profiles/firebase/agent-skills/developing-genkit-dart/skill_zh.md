# Genkit Dart

Genkit Dart 是一个 Dart 的 AI SDK，它为代码生成、结构化输出、工具、工作流和 AI 代理提供了统一的接口。

## 核心特性和使用方法
如果你在初始化 Genkit (`Genkit()`)、生成 (`ai.generate`)、工具 (`ai.defineTool`)、工作流 (`ai.defineFlow`)、嵌入 (`ai.embedMany`)、流式传输或调用远程工作流端点时需要帮助，请加载核心框架参考：
[references/genkit.md](references/genkit.md)

## Genkit CLI（推荐）

Genkit CLI 提供了一个本地开发 UI，用于运行 Flow、跟踪执行、与模型交互以及评估输出。

检查用户是否已安装：`genkit --version`

**安装：**
```bash
curl -sL cli.genkit.dev | bash # 原生 CLI
# OR
npm install -g genkit-cli # 通过 npm
```

**使用：**
使用 `genkit start` 将 Genkit 开发者 UI 和跟踪附加到你的运行命令：
```bash
genkit start -- dart run main.dart
```

## 插件生态系统

Genkit 依赖于一系列插件来执行生成式 AI 操作、与外部 LLM 交互或托管 Web 服务器。

当被要求使用任何给定插件时，请始终通过以下相应的参考链接来验证其使用方法。当你需要了解插件的特定初始化参数、工具、模型和使用模式时，应加载参考：

| 插件名称 | 参考链接 | 描述 |
| ---- | ---- | ---- |
| `genkit_google_genai` | [references/genkit_google_genai.md](references/genkit_google_genai.md) | 用于 Google Gemini 插件接口使用。 |
| `genkit_anthropic` | [references/genkit_anthropic.md](references/genkit_anthropic.md) | 用于 Anthropic 插件接口，用于 Claude 模型。 |
| `genkit_openai` | [references/genkit_openai.md](references/genkit_openai.md) | 用于 OpenAI 插件接口，用于 GPT 模型、Groq 和自定义兼容端点。 |
| `genkit_middleware` | [references/genkit_middleware.md](references/genkit_middleware.md) | 用于特定代理行为的工具：`filesystem`、`skills` 和 `toolApproval` 中断。 |
| `genkit_mcp` | [references/genkit_mcp.md](references/genkit_mcp.md) | 用于模型上下文协议集成（服务器、主机和客户端功能）。 |
| `genkit_chrome` | [references/genkit_chrome.md](references/genkit_chrome.md) | 用于在 Chrome 浏览器本地运行 Gemini Nano，使用 Prompt API。 |
| `genkit_shelf` | [references/genkit_shelf.md](references/genkit_shelf.md) | 用于使用 Dart Shelf 通过 HTTP 集成 Genkit Flow 操作。 |
| `genkit_firebase_ai` | [references/genkit_firebase_ai.md](references/genkit_firebase_ai.md) | 用于 Firebase AI 插件接口（通过 Vertex AI 的 Gemini API）。 |

## 外部依赖

每当你在工具、工作流和提示中定义映射模式时，都必须使用 [schemantic](https://pub.dev/packages/schemantic) 库。
要学习如何使用 schemantic，请确保你阅读 [references/schemantic.md](references/schemantic.md)，了解如何实现类型安全的生成 Dart 代码。这在遇到 `@Schema()`、`SchemanticType` 或以 `$` 前缀命名的类等符号时尤其相关。Genkit Dart 使用 schemantic 来处理所有数据模型，因此理解它是使用 Genkit Dart 的关键技能。

## 最佳实践

- 在生成最终响应之前，始终使用 `dart analyze` 检查代码是否干净地编译。
- 始终使用 Genkit CLI 进行本地开发和调试。
