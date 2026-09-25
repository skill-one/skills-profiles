# Genkit JS

## 前置条件

确保 `genkit` 命令行工具可用。
- 运行 `genkit --version` 进行验证。所需最低 CLI 版本：**1.29.0**
- 如果未找到或存在较旧版本（1.x < 1.29.0），请安装/升级：`npm install -g genkit-cli@^1.29.0`。

**新项目**：如果您在新的代码库中设置 Genkit，请遵循 [设置指南](references/setup.md)。

## 欢迎世界

```ts
import { z, genkit } from 'genkit';
import { googleAI } from '@genkit-ai/google-genai';

// 使用 Google AI 插件初始化 Genkit
const ai = genkit({
  plugins: [googleAI()],
});

export const myFlow = ai.defineFlow({
  name: 'myFlow',
  inputSchema: z.string().default('AI'),
  outputSchema: z.string(),
}, async (subject) => {
  const response = await ai.generate({
    model: googleAI.model('gemini-flash-latest'),
    prompt: `给我讲一个关于 ${subject} 的笑话`,
  });
  return response.text;
});
```

## 提示（Dotprompt）

`.prompt` 文件将提示内容与代码分离，使用 YAML 前置部分加上 Handlebars 模板。参见 [Dotprompt](references/dotprompt.md)：`promptDir`、`ai.prompt()`（调用/流式传输/渲染）、变体、部分、通过 `ai.defineSchema` 的命名模式，以及 `tools`/`maxTurns`/`returnToolRequests`/`use`（中间件）前置字段。

## 代理（Beta）

Genkit 提供了一个预览 **代理** API，用于持久化、多轮对话（会话、快照、中断、分支、后台执行）。这是一个 **Beta** API：服务器 API 来自 `genkit/beta`，浏览器客户端来自 `genkit/beta/client` —— 而不是稳定的 `genkit` 入口点。**需要 `genkit` >= 1.39.0。**

更多详情请参见：

-   [代理](references/agents.md)：定义/服务代理和客户端管理状态（从这里开始）。
-   [会话与持久化](references/agents-sessions.md)：会话存储（`InMemory`/`File`/`Firestore`）。
-   [人工参与/中断](references/agents-human-in-the-loop.md)：暂停以获取批准/输入并恢复。
-   [分支](references/agents-branching.md)：从快照分支对话。
-   [后台代理](references/agents-background.md)：分离长时间运行的回合并轮询。
-   [处理状态](references/agents-state.md)：类型化的自定义会话状态，自动同步到客户端。
-   [工件](references/agents-artifacts.md)：生成和读取命名交付物。
-   [多代理编排](references/agents-multi-agent.md)：委托给子代理。
-   [高级自定义代理](references/agents-custom.md)：使用 `defineCustomAgent` 完全控制回合。
-   [部署代理](references/agents-deployment.md)：通过 HTTP 服务代理（多个代理、CORS、Web UI、其他框架）。

## 生成式 UI（A2UI）

Genkit 提供了一个 **A2UI**（代理到 UI）插件（`@genkit-ai/a2ui`），允许代理流式传输交互式 UI **表面**（卡片、列表、表单、按钮），而不仅仅是文本。整个服务器端集成是代理（或 `ai.generate`）的 `use` 数组中的 `a2ui()` 模型中间件；浏览器使用 `@a2ui/*` 渲染器加上 `@genkit-ai/a2ui/client` 中的辅助工具来渲染表面。它基于 Beta 代理客户端（`genkit/beta` + `genkit/beta/client`）。

-   [A2UI](references/a2ui.md)：服务器中间件、选项、客户端渲染、用户操作/表单、自定义目录，以及安全/信任边界。

## 中间件

中间件包装生成（重试、回退、额外工具、请求/响应转换），并通过 `ai.generate`、提示和代理上的 `use: [...]` 数组附加。

-   [使用中间件](references/middleware.md)：`use` 数组和 `@genkit-ai/middleware` 包（`retry`、`fallback`、`artifacts`、`agents`、`filesystem`、`skills`、`toolApproval`）以及内置核心中间件。
-   [构建自定义中间件](references/middleware-custom.md)：使用 `generateMiddleware` 编写自己的中间件，并通过 `.plugin()` 注册它。

## 重要：不要信任内部知识

Genkit 最近经历了重大破坏性 API 变更。您的知识已过时。您**必须**查阅文档。推荐：

```sh
genkit docs:read js/get-started.md
genkit docs:read js/flows.md
```

参见 [常见错误](references/common-errors.md) 以获取已弃用 API（例如，`configureGenkit`、`response.text()`、`defineFlow` 导入）及其 v1.x 替代方案列表。

**始终使用 Genkit CLI 或提供的参考来验证信息。**

## 错误排查协议

**当您遇到任何与 Genkit 相关的错误（验证错误、API 错误、类型错误、404 等）：**

1. **强制第一步**：阅读 [常见错误](references/common-errors.md)
2. 确定错误是否匹配已知模式
3. 应用文档中记录的解决方案
4. 如果在 common-errors.md 中未找到，则咨询其他来源（例如 `genkit docs:search`）

**不要：**
- 基于假设或内部知识尝试修复
- 跳过阅读 common-errors.md “因为您认为您知道解决方案”
- 依赖 1.0 之前 Genkit 的模式

**此协议不可协商，用于错误处理。**

## 开发工作流程

1.  **代理还是流程？**：如果任务是对话式、多轮，或描述为“代理”、“助手”或“聊天机器人”，请使用 `ai.defineAgent` 构建（参见 [代理](references/agents.md)），而不是在流程中手动编写 `generate` + 工具循环。仅对于单次、无状态的生成，才使用普通流程。
2.  **选择提供者**：Genkit 是提供者无关的（Google AI、OpenAI、Anthropic、Ollama 等）。
    -   如果用户未指定提供者，默认为 **Google AI**。
    -   如果用户询问其他提供者，使用 `genkit docs:search "plugins"` 查找相关文档。
3.  **检测框架**：检查 `package.json` 以识别运行时（Next.js、Firebase、Express）。
    -   查找 `@genkit-ai/next`、`@genkit-ai/firebase` 或 `@genkit-ai/google-cloud`。
    -   根据特定框架的模式调整实现。
4.  **遵循最佳实践**：
    -   参见 [最佳实践](references/best-practices.md) 获取有关项目结构、模式定义和工具设计的指导。
    -   **保持简洁**：仅指定与默认值不同的选项。不确定时，请查阅文档/源代码。
5.  **确保正确性**：
    -   在做出更改后运行类型检查（例如，`npx tsc --noEmit`）。
    -   如果类型检查失败，请在搜索源代码之前查阅 [常见错误](references/common-errors.md)。
    -   通过跟踪验证，而不是盲目运行。直接运行应用程序（`node`/`tsx`/`npm start`）**不会**捕获开发跟踪。参见 [CLI 使用](#cli-usage-recommended) 了解如何运行应用程序并捕获跟踪。
6.  **处理错误**：
    -   对于任何错误：**首要行动是阅读 [常见错误](references/common-errors.md)**
    -   匹配错误到记录的模式
    -   在尝试替代方案之前应用记录的修复方案

## 查找文档

使用 Genkit CLI 查找权威文档：

1.  **搜索主题**：`genkit docs:search <query>`
    -   示例：`genkit docs:search "streaming"`
2.  **列出所有文档**：`genkit docs:list`
3.  **阅读指南**：`genkit docs:read <path>`
    -   示例：`genkit docs:read js/flows.md`

## CLI 使用（推荐）

`genkit start` 无干扰地包装任何使用 Genkit 库的 Node.js 程序，运行程序本身不变，同时捕获每个 Genkit 动作的跟踪，以便您可以从终端**证明工具实际上被调用并检查模型 I/O**，即使对于无头检查也是如此。它转发 stdio，因此依赖 stdin/stdout 的交互式 CLI 工具可以正常工作，没有问题。直接运行应用程序（`node`/`tsx`/`npm start`）会跳过跟踪捕获，因此您是在盲目调试。

**主要模式（默认）**：在您的正常运行命令前缀 `genkit start --`。这会收集您的程序运行时任何 Genkit 代码的遥测数据，无论是由开发 UI、您自己的 Web 服务器/Web UI 还是普通脚本触发：
```bash
genkit start -- npx tsx --watch src/index.ts
genkit start --noui -- npx tsx src/index.ts   # 相同，不显示开发 UI（仍然是一个持久的服务器）
```
`genkit start` 运行，直到您使用 Ctrl+C 停止。这对于常见情况是预期且正确的：您的 Web/移动应用程序调用的服务器，或您自己退出交互式 CLI。`--noui` 仅删除开发 UI；它**不是**一次性命令，不会自行退出。**不要**在自动化/非交互式环境中使用 `genkit start` 作为阻塞步骤。

**非交互式使用（代理/CI）**：在 `--` 之前添加全局 `--non-interactive` 标志，以便 CLI 使用默认值，并且永远不会在提示上阻塞（例如，首次运行的分析通知）：`genkit start --non-interactive -- npx tsx src/index.ts`（对 `flow:run` 也有效）。

**运行流程（`flow:run`）**：从 CLI 调用特定流程。在 `--` 后附加您的运行命令以启动仅为此运行时（命令按原样运行以注册您的流程）：
```bash
genkit flow:run myFlow '{"data": "input"}' -- npx tsx src/index.ts
```
这是**自终止的**：它运行一次流程，打印一个 `Trace ID`，然后退出（使用 `genkit trace:get <id>` 检查它）。这使得它成为快速、非交互式检查的正确选择，必须自行退出，而不会阻塞 `genkit start` 或直接运行应用程序（后者会跳过跟踪）。始终显式传递输入 JSON：`flow:run` 在省略时发送 `undefined`，并且**不会**回退到模式 `.default()`。注意：`flow:run` 运行的是流程（`ai.defineFlow`），而不是代理（不能直接 `flow:run` 代理（`ai.defineAgent`）。要从 CLI 运行代理，请将一个回合包装在一次性流程中并运行该流程（参见 [代理](references/agents.md)）。

**使用跟踪进行调试**：最快的方法是查看提示、模型输入/输出、工具调用、延迟和错误。在 `genkit start` 下的任何运行后从终端检查：
```bash
genkit trace:list                        # 查找最近的跟踪 ID
genkit trace:get <traceId>               # 完整跟踪详情（输入、输出、工具调用、错误）
genkit trace:get <traceId> --format json # 机器可读的 JSON，安全地传递给 jq 或其他解析器
```

对于机器可读输出，传递 `--format json` 以获取干净的 JSON，您可以将其传递给 `jq` 或其他解析器。**默认**输出是面向人类的（横幅/日志行，大型跟踪可能截断），因此不要直接传递这种形式；使用 `--format json`、grep 或开发 UI 跟踪查看器。

参见 [CLI 参考](references/docs-and-cli.md) 获取更多命令，以及 `genkit --help` 获取完整列表。

## 参考

-   [最佳实践](references/best-practices.md)：模式定义、流程设计和结构的推荐模式。
-   [Dotprompt](references/dotprompt.md)：`.prompt` 文件——`promptDir`、`ai.prompt()`、变体、部分、命名模式，以及 `tools`/`maxTurns`/`returnToolRequests`/`use` 前置部分。
-   [文档与 CLI 参考](references/docs-and-cli.md)：文档搜索、CLI 任务和工作流程。
-   [常见错误](references/common-errors.md)：关键“陷阱”、迁移指南和故障排除。
-   [设置指南](references/setup.md)：新项目的手动设置说明。
-   [示例](references/examples.md)：最小的可重复示例（基本生成、多模态、思考模式）。
-   [代理（Beta）](references/agents.md)：代理基础、服务和客户端管理状态。更深入的主题：[会话](references/agents-sessions.md)、[人工参与](references/agents-human-in-the-loop.md)、[分支](references/agents-branching.md)、[后台代理](references/agents-background.md)、[状态](references/agents-state.md)、[工件](references/agents-artifacts.md)、[多代理](references/agents-multi-agent.md)、[自定义代理](references/agents-custom.md)、[部署](references/agents-deployment.md)。
-   [中间件](references/middleware.md)：使用中间件和 `@genkit-ai/middleware` 包。另见 [构建自定义中间件](references/middleware-custom.md)。
-   [A2UI（生成式 UI）](references/a2ui.md)：`@genkit-ai/a2ui` 插件（`a2ui()` 中间件）、选项、客户端渲染、用户操作/表单、自定义目录，以及安全。
