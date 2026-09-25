# Genkit JS

## 前置条件

确保 `genkit` CLI 可用。
-  运行 `genkit --version` 进行验证。所需最低 CLI 版本：**1.29.0**
-  若未找到或存在较旧版本（1.x < 1.29.0），请安装/升级：`npm install -g genkit-cli@^1.29.0`。

**新项目**：如果您正在新的代码库中设置 Genkit，请遵循 [Setup Guide](references/setup.md)。

## Hello World

```ts
import { z, genkit } from 'genkit';
import { googleAI } from '@genkit-ai/google-genai';

// Initialize Genkit with the Google AI plugin
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
    prompt: `Tell me a joke about ${subject}`,
  });
  return response.text;
});
```

## Prompts (Dotprompt)

`.prompt` 文件通过 YAML frontmatter 和 Handlebars 模板，将提示内容从代码中分离。详见 [Dotprompt](references/dotprompt.md)：`promptDir`、`ai.prompt()`（调用/流式传输/渲染）、变体、部分模板、通过 `ai.defineSchema` 定义命名模式，以及 `tools`/`maxTurns`/`returnToolRequests`/`use`（中间件）frontmatter 字段。

## Agents (Beta)

Genkit 提供了一个预览 **agent** API，用于持久化的多轮对话（会话、快照、中断、分支、后台执行）。这是一个 **beta** API：服务端 API 来自 `genkit/beta`，浏览器客户端来自 `genkit/beta/client`，而非稳定的 `genkit` 入口。**要求 `genkit` >= 1.39.0。**

更多详情请参阅：

-   [Agents](references/agents.md)：定义/提供 agent 及客户端管理的状态（从这里开始）。
-   [Sessions & persistence](references/agents-sessions.md)：会话存储（`InMemory`/`File`/`Firestore`）。
-   [Human-in-the-loop / interrupts](references/agents-human-in-the-loop.md)：暂停等待批准/输入并恢复。
-   [Branching](references/agents-branching.md)：从快照分支（fork）对话。
-   [Background agents](references/agents-background.md)：分离长时间运行的轮次并进行轮询。
-   [Working with state](references/agents-state.md)：类型化的自定义会话状态，自动同步到客户端。
-   [Artifacts](references/agents-artifacts.md)：生成并读取命名交付物。
-   [Multi-agent orchestration](references/agents-multi-agent.md)：委托给子 agent。
-   [Advanced custom agents](references/agents-custom.md)：`defineCustomAgent` 用于完全控制轮次。
-   [Deploying agents](references/agents-deployment.md)：通过 HTTP 提供 agent（多个 agent、CORS、Web UI、其他框架）。

## Generative UI (A2UI)

Genkit 拥有 **A2UI**（Agent-to-UI）插件（`@genkit-ai/a2ui`），可使 agent 流式传输交互式 UI **界面**（卡片、列表、表单、按钮），而不仅仅是文本。整个服务端集成是在 agent（或 `ai.generate`）的 `use` 数组中的 `a2ui()` 模型中间件；浏览器通过 `@a2ui/*` 渲染器以及 `@genkit-ai/a2ui/client` 中的辅助函数渲染界面。它基于 beta agent 客户端（`genkit/beta` + `genkit/beta/client`）。

-   [A2UI](references/a2ui.md)：服务端中间件、选项、客户端渲染、用户操作/表单、自定义目录以及安全/信任边界。

## 中间件

中间件包裹生成过程（重试、降级、额外工具、请求/响应转换），并通过 `ai.generate`、prompts 和 agents 上的 `use: [...]` 数组进行挂载。

-   [Using middleware](references/middleware.md)：`use` 数组以及 `@genkit-ai/middleware` 包（`retry`、`fallback`、`artifacts`、`agents`、`filesystem`、`skills`、`toolApproval`）以及内置核心中间件。
-   [Building custom middleware](references/middleware-custom.md)：使用 `generateMiddleware` 编写自定义中间件，并通过 `.plugin()` 注册。

## 关键：不要依赖内部知识

Genkit 最近经历了一次重大的 API 破坏性变更。您的知识已过时。您 MUST 查询文档。推荐：

```sh
genkit docs:read js/get-started.md
genkit docs:read js/flows.md
```

详见 [Common Errors](references/common-errors.md) 中已弃用 API（例如 `configureGenkit`、`response.text()`、`defineFlow` 导入）及其 v1.x 替换方案。

**始终使用 Genkit CLI 或提供的参考资料验证信息。**

## 错误排查协议

**当遇到任何与 Genkit 相关的错误（ValidationError、API 错误、类型错误、404 等）时：**

1.  **必须首先执行**：阅读 [Common Errors](references/common-errors.md)
2.  判断该错误是否匹配已知模式
3.  应用文档中记录的解决方案
4.  仅当未在 common-errors.md 中找到时，再咨询其他来源（如 `genkit docs:search`）

**不要：**
-  基于假设或内部知识尝试修复
-  跳过阅读 common-errors.md（因为你认为自己已经知道修复方法）
-  依赖 1.0 之前 Genkit 的模式

**此协议是错误处理中不可协商的（强制执行的）。**

## 开发流程

1.  **Agent 还是 flow？**：如果任务是对话式、多轮，或描述为“agent”、“assistant”或“chatbot”，请使用 `ai.defineAgent` 构建（见 [Agents](references/agents.md)），而不是在 flow 内部手动实现 `generate` + 工具循环。仅对单次、无状态的生成使用普通 flow。
2.  **选择提供方**：Genkit 不绑定提供方（Google AI、OpenAI、Anthropic、Ollama 等）。
    -   如果用户未指定提供方，默认使用 **Google AI**。
    -   如果用户询问其他提供方，使用 `genkit docs:search "plugins"` 查找相关文档。
3.  **检测框架**：检查 `package.json`，识别运行时环境（Next.js、Firebase、Express）。
    -  查找 `@genkit-ai/next`、`@genkit-ai/firebase` 或 `@genkit-ai/google-cloud`。
    -  将实现适配到特定框架的模式。
4.  **遵循最佳实践**：
    -   详见 [Best Practices](references/best-practices.md) 以获取关于项目结构、模式定义和工具设计的指导。
    -   **保持简洁**：仅指定与默认值不同的选项。不确定时，请查阅文档/源代码。
5.  **确保正确性**：
    -   修改后运行类型检查（例如 `npx tsc --noEmit`）。
    -   如果类型检查失败，在搜索源代码之前查阅 [Common Errors](references/common-errors.md)。
    -   使用追踪验证，而非盲目运行。直接运行应用（`node`/`tsx`/`npm start`）**不会**捕获开发追踪。参见 [CLI Usage](#cli-usage-recommended) 了解如何运行应用并捕获追踪。
6.  **处理错误**：
    -   在遇到任何错误时：**首要行动是阅读 [Common Errors](references/common-errors.md)**
    -  将错误与文档中记录的模式匹配
    -  尝试替代方案之前，先应用文档中记录的修复方法

## 查找文档

使用 Genkit CLI 查找权威文档：

1.  **搜索主题**：`genkit docs:search <query>`
    -   示例：`genkit docs:search "streaming"`
2.  **列出所有文档**：`genkit docs:list`
3.  **阅读指南**：`genkit docs:read <path>`
    -   示例：`genkit docs:read js/flows.md`

## CLI 使用（推荐）

`genkit start` 不干扰地包裹任何使用 Genkit 库的 Node.js 程序，在不改变其运行方式的同时，从每个 Genkit 操作捕获追踪，因此您可以从终端 **证明工具确实被调用并检查模型输入/输出**，即使在进行无头（headless）检查时也是如此。它转发 stdio，因此依赖 stdin/stdout 的交互式 CLI 工具可以正常运行。直接运行应用（`node`/`tsx`/`npm start`）会跳过追踪捕获，导致您盲目调试。

**主要模式（默认）：** 在您正常的运行命令前加上 `genkit start --` 前缀。这会收集程序运行中任何 Genkit 代码的遥测信息，无论该代码是由 dev UI、您自己的 Web 服务器/Web UI 还是普通脚本触发的：
```bash
genkit start -- npx tsx --watch src/index.ts
genkit start --noui -- npx tsx src/index.ts   # same, without the Dev UI (still a persistent server)
```
`genkit start` 会一直运行，直到您按 Ctrl+C 停止它。这在常见情况下是预期且正确的：一个供 Web/移动应用调用的服务器，或您自己退出操作的交互式 CLI。`--noui` 仅移除 Dev UI；它**不是**一次性命令，不会自行退出。请勿在自动化/非交互式上下文中将 `genkit start` 作为阻塞步骤使用。

**非交互式使用（agent/CI）：** 在 `--` 前添加全局 `--non-interactive` 参数，使 CLI 使用默认值且不会在提示上阻塞（例如首次运行的分析提示）：`genkit start --non-interactive -- npx tsx src/index.ts`（同样适用于 `flow:run`）。

**运行 flow（`flow:run`）：** 通过名称从 CLI 调用特定 flow。在 `--` 之后追加您的运行命令，仅为该运行启动运行时（该命令原样执行以注册您的 flows）：
```bash
genkit flow:run myFlow '{"data": "input"}' -- npx tsx src/index.ts
```
这是一个**自终止**操作：它运行一次 flow，打印一个 `Trace ID`，然后退出（可通过 `genkit trace:get <id>` 检查）。这使其成为快速、非交互式检查的正确选择，必须自行退出，且不会阻塞 `genkit start` 或直接运行应用（后者会跳过追踪）。始终明确传递输入 JSON：`flow:run` 在省略时发送 `undefined`，并且**不会**回退到 schema 的 `.default()`。注意：`flow:run` 运行的是 **flows**（`ai.defineFlow`），而非 agent；无法直接 `flow:run` agent（`ai.defineAgent`）。若需从 CLI 运行 agent，请将一轮包裹在临时 flow 中并运行该 flow（见 [Agents](references/agents.md)）。

**使用追踪调试：** 查看提示、模型输入/输出、工具调用、延迟和错误的最快方式。在 `genkit start` 下的任何运行之后，从终端检查：
```bash
genkit trace:list                        # find recent trace IDs
genkit trace:get <traceId>               # full trace details (inputs, outputs, tool calls, errors)
genkit trace:get <traceId> --format json # machine-readable JSON, safe to pipe into jq or other parsers
```

对于机器可读输出，传递 `--format json` 以获取可管道传输到 `jq` 或其他解析器的干净 JSON。**默认**输出面向人类（横幅/日志行，大追踪可能出现截断），因此不要直接管道传输该格式；请使用 `--format json`、`grep` 或 Dev UI 追踪查看器。

参见 [CLI Reference](references/docs-and-cli.md) 获取更多命令，并运行 `genkit --help` 获取完整列表。

## 参考资料

-   [Best Practices](references/best-practices.md)：关于模式定义、flow 设计和结构的推荐模式。
-   [Dotprompt](references/dotprompt.md)：`.prompt` 文件 — `promptDir`、`ai.prompt()`、变体、部分模板、命名模式，以及 `tools`/`maxTurns`/`returnToolRequests`/`use` frontmatter。
-   [Docs & CLI Reference](references/docs-and-cli.md)：文档搜索、CLI 任务和工作流程。
-   [Common Errors](references/common-errors.md)：关键的“注意事项”、迁移指南和排查问题。
-   [Setup Guide](references/setup.md)：新项目的手动设置说明。
-   [Examples](references/examples.md)：最小可复现示例（基本生成、多模态、思考模式）。
-   [Agents (Beta)](references/agents.md)：Agent 基础、提供以及客户端管理的状态。更深层主题：[sessions](references/agents-sessions.md)、[human-in-the-loop](references/agents-human-in-the-loop.md)、[branching](references/agents-branching.md)、[background agents](references/agents-background.md)、[state](references/agents-state.md)、[artifacts](references/agents-artifacts.md)、[multi-agent](references/agents-multi-agent.md)、[custom agents](references/agents-custom.md)、[deployment](references/agents-deployment.md)。
-   [Middleware](references/middleware.md)：使用中间件和 `@genkit-ai/middleware` 包。另见 [building custom middleware](references/middleware-custom.md)。
-   [A2UI (Generative UI)](references/a2ui.md)：`@genkit-ai/a2ui` 插件（`a2ui()` 中间件）、选项、客户端渲染、用户操作/表单、自定义目录以及安全。
