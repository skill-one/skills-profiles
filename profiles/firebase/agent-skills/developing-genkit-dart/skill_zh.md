# Genkit Dart

## Genkit Dart

Genkit Dart 是 Dart 的 AI SDK，为代码生成、结构化输出、工具、流程和 AI 智能体提供统一的接口。

## 核心功能与使用
如果需要帮助初始化 Genkit（`Genkit()`）、生成（`ai.generate`）、工具（`ai.defineTool`）、流程（`ai.defineFlow`）、嵌入（`ai.embedMany`）、流式传输，或调用远程流程端点，请加载核心框架参考文档： 
[references/genkit.md](references/genkit.md)

## Genkit CLI（推荐）

Genkit CLI 提供本地开发界面，可用于运行 Flow、追踪执行过程、与模型交互以及评估输出。

检查用户是否已安装：`genkit --version`

**安装：**
```bash
curl -sL cli.genkit.dev | bash # 原生 CLI
# OR
npm install -g genkit-cli # 通过 npm
```

**使用：**
用 `genkit start` 包装你的运行命令，以挂载 Genkit 开发者界面和追踪功能：
```bash
genkit start -- dart run main.dart
```

## 插件生态系统

Genkit 依赖一系列插件，用于执行生成式 AI 操作、与外部大语言模型（LLM）交互，或托管 Web 服务器。

当要求使用任何插件时，始终通过参考下文对应文档来验证使用方式。当您需要了解插件的具体初始化参数、工具、模型和使用模式时，应加载相关参考文档：

| Plugin Name | Reference Link | Description |
| ---- | ---- | ---- |
| `genkit_google_genai` | [references/genkit_google_genai.md](references/genkit_google_genai.md) | 用于 Google Gemini 插件接口使用。 |
| `genkit_anthropic` | [references/genkit_anthropic.md](references/genkit_anthropic.md) | 用于 Claude 模型的 Anthropic 插件接口。 |
| `genkit_openai` | [references/genkit_openai.md](references/genkit_openai.md) | 用于 GPT 模型、Groq 及自定义兼容端点的 OpenAI 插件接口。 |
| `genkit_middleware` | [references/genkit_middleware.md](references/genkit_middleware.md) | 用于实现特定智能体行为的工具：`filesystem`、`skills` 和 `toolApproval` 中断。 |
| `genkit_mcp` | [references/genkit_mcp.md](references/genkit_mcp.md) | 用于模型上下文协议集成（Server、Host 和 Client 能力）。 |
| `genkit_chrome` | [references/genkit_chrome.md](references/genkit_chrome.md) | 用于使用 Prompt API 在 Chrome 浏览器中本地运行 Gemini Nano。 |
| `genkit_shelf` | [references/genkit_shelf.md](references/genkit_shelf.md) | 使用 Dart Shelf 将 Genkit Flow 操作以 HTTP 方式进行集成。 |
| `genkit_firebase_ai` | [references/genkit_firebase_ai.md](references/genkit_firebase_ai.md) | 用于 Firebase AI 插件接口（通过 Vertex AI 使用 Gemini API）。 |

## 外部依赖

在 Tools、Flows 和 Prompts 中定义模式映射时，必须使用 [schemantic](https://pub.dev/packages/schemantic) 库。
要学习如何使用 schemantic，请阅读 [references/schemantic.md](references/schemantic.md)，了解如何实现类型安全生成的 Dart 代码。当遇到 `@Schema()`、`SchemanticType` 或带 `$` 前缀的类等符号时，这一点尤其相关。Genkit Dart 使用 schemantic 管理所有数据模型，因此理解该库是使用 Genkit Dart 的一项关键技能。

## 最佳实践
- 生成最终回复之前，始终使用 `dart analyze` 检查代码是否能够干净地编译。
- 始终使用 Genkit CLI 进行本地开发和调试。
