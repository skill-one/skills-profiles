---
name: sentry-setup-ai-monitoring
description: 在任何项目中设置 Sentry AI Agent 监控。当被要求监控 LLM 调用、跟踪 AI 代理、跟踪对话或为 OpenAI/Anthropic/Vercel AI/LangChain/Google GenAI/Pydantic AI/Laravel AI 进行instrumentation时使用。检测已安装的 AI SDK 并配置相应的集成。
---

> [所有技能](../../SKILL_TREE.md) > [功能设置](../sentry-feature-setup/SKILL.md) > AI 监控

# 设置 Sentry AI 代理监控

配置 Sentry 以跟踪 LLM 调用、代理执行、工具使用和令牌消耗。

## 何时调用此技能

- 用户要求“监控 AI/LLM 调用”或“跟踪 OpenAI/Anthropic 使用”
- 用户需要“AI 可观察性”或“代理监控”
- 用户询问关于令牌使用、模型延迟或 AI 成本

**重要提示**：下文中的 SDK 版本、API 名称和代码示例仅为示例。在实施前，请务必参考 [docs.sentry.io](https://docs.sentry.io) 进行验证，因为 API 和最低版本可能已更改。

## 前置条件

AI 监控需要 **启用跟踪** (`tracesSampleRate > 0`)。

如果应用程序具有多轮聊天，请默认在任何合适的地方设置会话 ID 以识别聊天会话。Sentry 使用 `gen_ai.conversation.id` 将相关的 AI 跨度分组到会话中。某些集成会自动推断它，但许多设置需要显式设置。

## 数据捕获警告

**提示和输出录制会捕获可能包含个人身份信息 (PII) 的用户内容。** 在 JavaScript 中，genAI 输入/输出捕获默认开启（受 `dataCollection.genAI` 控制）；在 Python 中通过 `send_default_pii=True` 启用；在 Laravel 中通过 `SENTRY_SEND_DEFAULT_PII=true` 启用。在依赖此捕获（或每个集成覆盖——JS 中的 `recordInputs`/`recordOutputs`，Python 中的 `include_prompts`）之前，请确认：

- 应用程序的隐私政策允许捕获用户提示和模型响应
- 捕获的数据符合相关法规（GDPR、CCPA 等）
- Sentry 数据保留设置适合数据的敏感性

**询问用户** 是否希望启用提示/输出捕获。未经明确确认，不得启用提示/输出捕获。仅在开发环境中使用 `tracesSampleRate: 1.0`；在生产环境中使用较低值或 `tracesSampler` 函数。

## 先检测

**配置前始终检测已安装的 AI SDK：**

```bash
# JavaScript
grep -E '"(openai|@anthropic-ai/sdk|ai|@langchain|@google/genai)"' package.json

# Python
grep -E '(openai|anthropic|langchain|huggingface)' requirements.txt pyproject.toml 2>/dev/null

# PHP / Laravel
grep -E '"(laravel/ai|openai-php|openai/|anthropic|llm)' composer.json 2>/dev/null
ls artisan 2>/dev/null && echo "Laravel detected"
```

## 采样检查

检测到 AI SDK 后，检查当前的采样配置：

```bash
# JavaScript
grep -E 'tracesSampleRate|tracesSampler' sentry.*.config.* instrument.* src/instrument.* app/instrument.* 2>/dev/null

# Python
grep -E 'traces_sample_rate|traces_sampler' *.py **/*.py 2>/dev/null

# PHP / Laravel
grep -E 'SENTRY_TRACES_SAMPLE_RATE|traces_sample_rate|traces_sampler' .env config/sentry.php 2>/dev/null
```

**如果 `tracesSampleRate` / `traces_sample_rate` 低于 1.0 并且没有配置 `tracesSampler` / `traces_sampler`：**

询问用户：

> "您当前的采样率是 {rate}。代理运行被采样为完整的跨度树——如果根跨度被丢弃，所有子 gen_ai 跨度都会丢失。为了实现完整的 AI 可见性，应将相关的 gen_ai 事务采样为 100%。您希望我设置一个 `tracesSampler`，在保持 AI 跨度为 100% 的同时，按当前速率采样其他流量吗？"

如果用户确认，请阅读 `${SKILL_ROOT}/references/sampling.md` 了解实现模式。

## 支持的 SDK

### JavaScript

| 包 | 集成 | 最低 Sentry SDK | 自动？ |
|---------|-------------|----------------|-------|
| `openai` | `openAIIntegration()` | 10.53.0 | 是 |
| `@anthropic-ai/sdk` | `anthropicAIIntegration()` | 10.53.0 | 是 |
| `ai` (Vercel) | `vercelAIIntegration()` | 10.53.0 | 是* |
| `@langchain/*` | `langChainIntegration()` | 10.53.0 | 是 |
| `@langchain/langgraph` | `langGraphIntegration()` | 10.53.0 | 是 |
| `@google/genai` | `googleGenAIIntegration()` | 10.53.0 | 是 |

*Vercel AI: 需要 10.53.0+。每次调用都需要 `experimental_telemetry`。

### Python

当 AI 包安装时，集成会自动启用——无需显式注册：

| 包 | 自动？ | 备注 |
|---------|-------|-------|
| `openai` | 是 | 包括 OpenAI Agents SDK |
| `anthropic` | 是 | |
| `langchain` / `langgraph` | 是 | |
| `huggingface_hub` | 是 | |
| `google-genai` | 是 | |
| `pydantic-ai` | 是 | |
| `litellm` | **否** | 需要显式集成 |
| `mcp` (Model Context Protocol) | 是 | |

### PHP / Laravel

| 包 | 集成 | 最低 Sentry SDK | 自动？ |
|---------|-------------|----------------|-------|
| `laravel/ai` | Laravel AI 代理在 `sentry/sentry-laravel` 中 | 4.27.0 | 是 |

Laravel AI 支持需要 Laravel 12.x 或更高版本、`sentry/sentry-laravel` 4.27.0 或更高版本以及启用的跟踪。

## JavaScript 配置

### Node.js — 自动启用的集成

只需确保启用了跟踪。当 AI 包安装时，集成会自动启用：

```javascript
Sentry.init({
  dsn: "YOUR_DSN",
  tracesSampleRate: 1.0, // 生产环境中使用较低值（例如，0.1）
  // Node.js 中 OpenAI、Anthropic、Google GenAI、LangChain 集成会自动启用
});
```

要自定义（例如，在用户确认后启用提示捕获——见数据捕获警告）：

```javascript
Sentry.init({
  dsn: "YOUR_DSN",
  tracesSampleRate: 1.0,
  dataCollection: {
    // 要禁用发送用户数据和 HTTP 正文，请取消注释以下行。更多信息请访问：
    // https://docs.sentry.io/platforms/javascript/configuration/options/#dataCollection
    // userInfo: false,
    // httpBodies: [],
  },
  integrations: [
    Sentry.openAIIntegration({
      // recordInputs/recordOutputs 默认为 true（受 dataCollection.genAI 控制）
    }),
  ],
});
```

### Cloudflare Workers（不支持运行时补丁）

Workers 运行时 (`workerd`) 不支持猴子补丁，因此 Node.js 风格的自动代理化不适用。Workers AI (`env.AI`) 通过 `withSentry`（v10.67.0+）自动代理化；`openai`、`@anthropic-ai/sdk`、`@google/genai` 和 `ai` 需要构建时 Sentry Cloudflare Vite 插件（v10.68.0+，实验性）或手动客户端包装；LangChain/LangGraph 仅支持手动。请阅读 `${SKILL_ROOT}/../../references/sdks/cloudflare/ai-monitoring.md` 了解完整设置。

### 浏览器 / Next.js OpenAI（需要手动包装）

在浏览器端代码或 Next.js 元框架应用程序中，自动代理化不可用。手动包装客户端：

```javascript
import OpenAI from "openai";
import * as Sentry from "@sentry/nextjs"; // 或 @sentry/react, @sentry/browser

const openai = Sentry.instrumentOpenAiClient(new OpenAI());
// 像平常一样使用 'openai' 客户端
```

### LangChain / LangGraph（自动启用）

```javascript
Sentry.init({
  dsn: "YOUR_DSN",
  tracesSampleRate: 1.0,
  dataCollection: {
    // 要禁用发送用户数据和 HTTP 正文，请取消注释以下行。更多信息请访问：
    // https://docs.sentry.io/platforms/javascript/configuration/options/#dataCollection
    // userInfo: false,
    // httpBodies: [],
  },
  integrations: [
    Sentry.langChainIntegration(),
    Sentry.langGraphIntegration(),
  ],
});
```

### Vercel AI SDK

为 Edge 运行时添加到 `sentry.edge.config.ts`：
```javascript
Sentry.init({
  dsn: "YOUR_DSN",
  tracesSampleRate: 1.0,
  dataCollection: {
    // 要禁用发送用户数据和 HTTP 正文，请取消注释以下行。更多信息请访问：
    // https://docs.sentry.io/platforms/javascript/configuration/options/#dataCollection
    // userInfo: false,
    // httpBodies: [],
  },
  integrations: [Sentry.vercelAIIntegration()],
});
```

按调用启用遥测：
```javascript
await generateText({
  model: openai("gpt-4o"),
  prompt: "Hello",
  experimental_telemetry: {
    isEnabled: true,
    recordInputs: true,
    recordOutputs: true,
  },
});
```

## Python 配置

集成会自动启用——只需启用跟踪即可。仅添加显式导入以自定义选项：

```python
import sentry_sdk

sentry_sdk.init(
    dsn="YOUR_DSN",
    traces_sample_rate=1.0,  # 生产环境中使用较低值（例如，0.1）
    send_default_pii=True,
    # 当 AI 包安装时，集成会自动启用。
    # 仅指定显式选项以自定义（例如，include_prompts）：
    # integrations=[OpenAIIntegration(include_prompts=True)],
)
```

## PHP / Laravel AI 配置

当 `sentry/sentry-laravel` 和 `laravel/ai` 都安装且跟踪激活时，Laravel AI 代理会自动启用。

```bash
composer require sentry/sentry-laravel "^4.27.0"
composer require laravel/ai
php artisan vendor:publish --provider="Laravel\Ai\AiServiceProvider"
php artisan migrate
```

在 `.env` 中启用跟踪：

```ini
SENTRY_TRACES_SAMPLE_RATE=1.0
```

要包括 LLM 提示、工具参数和响应（在明确用户确认后），请启用 PII 捕获：

```ini
SENTRY_SEND_DEFAULT_PII=true
```

Sentry 将 LLM 和工具输入/输出视为 PII，默认不捕获它们。未经确认，不得启用 `SENTRY_SEND_DEFAULT_PII=true`。请参考上述数据捕获警告。

Laravel 集成会自动捕获以下跨度类型：

| Span op | 目的 |
|---------|---------|
| `gen_ai.invoke_agent` | 代理提示生命周期 |
| `gen_ai.chat` | AI 提供商聊天请求 |
| `gen_ai.execute_tool` | Laravel AI 工具执行 |
| `gen_ai.embeddings` | 嵌入生成 |

有关详细的 Laravel 设置、验证、会话行为和功能标志，请阅读 `${SKILL_ROOT}/../../references/sdks/php/ai-monitoring.md`。

## 手动代理化

当未检测到支持的 SDK 时使用。遵循标准的 [Sentry `gen_ai.*` 属性规范](https://getsentry.github.io/sentry-conventions/attributes/gen_ai/)——JS 文档可能滞后；不要设置规范中标记为已弃用的属性。

### 跨度类型

| `op` | Span `name` 模式 | 目的 |
|------|---------------------|---------|
| `gen_ai.{operation}` (例如 `gen_ai.chat`, `gen_ai.request`) | `{operation} {model}` (例如 `chat gpt-4o`) | 单个 LLM 调用 |
| `gen_ai.invoke_agent` | `invoke_agent {agent_name}` | 代理执行生命周期 |
| `gen_ai.execute_tool` | `execute_tool {tool_name}` | 工具/函数调用 |
| `gen_ai.handoff` | `handoff from {source} to {target}` | 代理到代理的转换 |

对于 LLM 调用跨度，`op` 遵循模式 `gen_ai.{gen_ai.operation.name}`——当操作已知时，使用 `gen_ai.chat`、`gen_ai.embeddings`、`gen_ai.generate_content` 或 `gen_ai.text_completion`。跨度属性仅接受原始类型；数组/对象必须 JSON-序列化。

### 示例（JavaScript）

```javascript
const inputMessages = [
  { role: "user", parts: [{ type: "text", content: "给我讲个笑话" }] },
];

await Sentry.startSpan({
  op: "gen_ai.chat",
  name: "chat gpt-4o",
  attributes: {
    "gen_ai.request.model": "gpt-4o",
    "gen_ai.operation.name": "chat",
    "gen_ai.input.messages": JSON.stringify(inputMessages),
  },
}, async (span) => {
  const result = await llmClient.complete(inputMessages);

  const outputMessages = [
    {
      role: "assistant",
      parts: [
        // 思考/推理内容放在 `reasoning` 部分，**不要**放在 `text` 部分。
        // Sentry 会单独显示它，并从用户可见的会话视图中过滤掉。
        { type: "reasoning", content: result.reasoning },
        { type: "text", content: result.text },
      ],
      finish_reason: result.finishReason,
    },
  ];
  span.setAttribute("gen_ai.output.messages", JSON.stringify(outputMessages));
  span.setAttribute("gen_ai.usage.input_tokens", result.inputTokens);
  span.setAttribute("gen_ai.usage.output_tokens", result.outputTokens);
  return result;
});
```

### 关键属性

**通用（所有 AI 跨度）：**

| 属性 | 是否必需 | 描述 |
|-----------|----------|-------------|
| `gen_ai.request.model` | 是 | 模型标识符（例如，`gpt-4o`，`claude-sonnet-4-6`） |
| `gen_ai.operation.name` | 否 | 操作标签（`chat`，`embeddings`，`invoke_agent`，`execute_tool`，`handoff` 等） |
| `gen_ai.agent.name` | 否 | 代理名称（在代理和工具跨度上设置） |

**模型配置（LLM 调用跨度）：**

| 属性 | 描述 |
|-----------|-------------|
| `gen_ai.request.reasoning_effort` | 推理模型的推理努力级别（例如，`low`，`medium`，`high`）。支持值因提供者而异。 |

**请求/响应内容（PII——仅在确认后启用；见数据捕获警告）：**

| 属性 | 描述 |
|-----------|-------------|
| `gen_ai.input.messages` | JSON-序列化的输入消息数组。每个项目使用 `{role, parts}`，其中 `parts` 是 `[{type, content}]`；`role` 是 `"user"`，`"assistant"`，`"tool"` 或 `"system"`。常见部分 `type`：`"text"`，`"reasoning"`，`"tool_call"`，`"tool_call_response"` |
| `gen_ai.output.messages` | JSON-序列化的响应消息数组（文本+工具调用），形状与输入相同 |

**思考/推理消息：** 具有扩展思考的模型（Anthropic `thinking` 块，Gemini `thought`，DeepSeek `reasoning_content`）会产生内部推理，这些推理不是用户可见回复的一部分。将其表示为助手消息内的 `reasoning` 部分——`{"type": "reasoning", "content": "..."}`——与用户可见的 `text` 部分一起。Sentry 会单独显示推理部分，并从用户可见的会话视图中过滤掉，因此**不要**将思考合并到 `text` 部分。当先前的思考被反馈到多轮请求中时，请在 `gen_ai.input.messages` 中的助手消息内包含相同的 `reasoning` 部分。通过 `gen_ai.usage.output_tokens.reasoning`（`gen_ai.usage.output_tokens` 的子集）记录推理令牌计数。 |
| `gen_ai.system_instructions` | 传递给模型的系统提示 |
| `gen_ai.tool.definitions` | JSON-序列化的模型可用的工具列表 |

**令牌使用：**

| 属性 | 描述 |
|-----------|-------------|
| `gen_ai.usage.input_tokens` | 总输入令牌——**包括**缓存的令牌 |
| `gen_ai.usage.input_tokens.cached` | 输入令牌的子集，从缓存中提供 |
| `gen_ai.usage.input_tokens.cache_write` | 处理输入时写入缓存的令牌 |
| `gen_ai.usage.output_tokens` | 总输出令牌——**包括**推理令牌 |
| `gen_ai.usage.output_tokens.reasoning` | 输出令牌的子集，用于推理 |
| `gen_ai.usage.total_tokens` | 输入+输出令牌的总和 |

**工具跨度 (`gen_ai.execute_tool`)：**

| 属性 | 描述 |
|-----------|-------------|
| `gen_ai.tool.name` | 工具标识符 |
| `gen_ai.tool.description` | 人类可读的工具描述 |
| `gen_ai.tool.call.arguments` | JSON-序列化的工具参数 |
| `gen_ai.tool.call.result` | JSON-序列化的工具结果 |

### 令牌使用和成本计算

Sentry 使用令牌属性来 [计算模型成本](https://docs.sentry.io/ai/monitoring/agents/costs/)。**缓存和推理令牌是子集，不是单独计数**——`gen_ai.usage.input_tokens` 已经包括 `gen_ai.usage.input_tokens.cached`，`gen_ai.usage.output_tokens` 已经包括 `gen_ai.usage.output_tokens.reasoning`。

Sentry 从总和中减去缓存/推理计数，以计算未缓存/非推理部分。报告大于总量的缓存或推理计数会导致仪表板中产生负成本。

示例——总输入令牌 100，90 从缓存中提供：

- 正确：`input_tokens = 100`，`input_tokens.cached = 90`
- 错误：`input_tokens = 10`，`input_tokens.cached = 90`（缓存大于总量→负成本）

`gen_ai.usage.output_tokens` 与 `gen_ai.usage.output_tokens.reasoning` 的规则相同。

## 验证

配置后，进行 LLM 调用并检查 Sentry 跨度仪表板。AI 跨度会显示 `gen_ai.*` 操作，包括模型、令牌计数和延迟。

## 会话

会话功能为您的AI代理的过往会话提供可读的、聊天风格的视图。它会根据 `gen_ai.conversation.id` 对时间跨度进行分组——因此，无论用户是否跨多个跟踪或在一个跟踪内发生多个会话，您都能获得每条消息、工具调用和响应的时间线。

当用户要求AI监控设置时，如果应用程序具有多轮聊天，应主动提及此要求。如果没有会话ID，代理监控时间跨度仍然可以工作，但会话视图无法正确分组会话。

在 Sentry 中的 **探索 > 会话** 可以找到它。

### 会话功能的先决条件

- 使用 `tracesSampleRate > 0` 启用跟踪
- Gen AI 时间跨度流式传输默认开启——自 JS SDK 10.61.0 起 `streamGenAiSpans` 默认为 `true`，自 Python SDK 2.64.0 起 `stream_gen_ai_spans` 默认为 `True`。这会将 AI 时间跨度作为独立项发送，因此具有大输入/输出的时间跨度不会超出事务有效载荷大小限制而被丢弃。（如果您需要在较旧的 SDK 上显式设置这些选项，这些选项自 JS 10.53.0 / Python 2.60.0 起可用。）
- **输入和输出捕获已启用**——会话功能从 `gen_ai.input.messages` 和 `gen_ai.output.messages` 属性中重建聊天。在 JS 中默认开启（通过 `dataCollection`）；在 Python 中，设置 `send_default_pii=True`；在 Laravel 中，设置 `SENTRY_SEND_DEFAULT_PII=true`。如果没有它，会话将显示为空。

### 设置会话ID

某些集成（Python 的 OpenAI Agents SDK、Node 的 OpenAI SDK、使用 `Conversational` + `RemembersConversations` 的 Laravel AI 代理）会自动推断会话ID。对于所有其他集成，请手动设置。

使用简短、不透明的标识符——仅包含字母数字字符、连字符或下划线。切勿将 URL、电子邮件地址或其他自由格式文本用作会话ID：Sentry 将其用作 URL 路径段，包含斜杠的值会中断该会话的会话功能。

好的示例：
- 一个 UUID：`48e35936-82ab-4f1a-beaf-b2fa4273ac5e`
- 前缀 ID：`conv_5j66UpCpwteGg4YSxUnt7lPYU`、`asst_abc12345`、`sess_987654`

#### JavaScript

```javascript
import * as Sentry from "@sentry/node"; // 或 @sentry/nextjs、@sentry/nestjs 等。

// 在会话开始时设置
Sentry.setConversationId("conv_abc123");

// 所有后续的 AI 调用都携带 gen_ai.conversation.id: "conv_abc123"
await openai.chat.completions.create({
  model: "gpt-5.5",
  messages: [{ role: "user", content: "Hello" }],
});
```

#### Python

```python
import sentry_sdk.ai

# 在会话开始时设置
sentry_sdk.ai.set_conversation_id("conv_abc123")

# 所有后续的 AI 调用都携带 gen_ai.conversation.id = "conv_abc123"
```

某些集成会自动推断会话ID。例如，Python 的 OpenAI 集成在您使用 `conversation` 参数时会获取它：

```python
import openai
import sentry_sdk

sentry_sdk.init(...)

conversation = openai.conversations.create()
response = openai.responses.create(
    model="gpt-5.4",
    input=[{"role": "user", "content": "What are the 5 Ds of dodgeball?"}],
    conversation=conversation.id  # 自动设置 gen_ai.conversation.id
)
```

### 用户归属

会话视图显示一个 **用户** 列。要填充它，请在任何 AI 调用之前，每个请求或会话调用一次 `setUser` / `set_user`：

#### JavaScript

```javascript
import * as Sentry from "@sentry/node"; // 或 @sentry/nextjs、@sentry/nestjs 等。

Sentry.setUser({ id: "user_123", email: "jane@example.com", username: "jane" });
```

#### Python

```python
import sentry_sdk

sentry_sdk.set_user({"id": "user_123", "email": "jane@example.com", "username": "jane"})
```

`id`、`email` 或 `username` 中的任何一个都足够——会话功能将显示存在的字段。

### 会话与跟踪的比较

这些都是独立的概念：
- 一个会话可以跨越 **多个跟踪**（例如，用户在会话中刷新页面——新的跟踪，相同的会话ID）
- 一个跟踪可以包含来自 **不同会话** 的时间跨度（例如，用户在不刷新页面的情况下开始新的聊天）

## 故障排除

| 问题 | 解决方案 |
|-------|----------|
| AI 时间跨度未出现 | 验证 `tracesSampleRate > 0`，检查 SDK 版本 |
| 令牌计数缺失 | 某些提供者不返回流式传输的令牌 |
| 仪表板中的负值或错误成本 | 缓存/推理令牌是总计的子集——请参阅令牌使用和成本计算 |
| 提示未捕获 | 在 JS 中，genAI 捕获默认开启——确保您没有设置 `dataCollection: { genAI: { inputs: false } }`，或显式传递 `recordInputs: true`。在 Python 中，设置 `send_default_pii=True`；在 Laravel 中，设置 `SENTRY_SEND_DEFAULT_PII=true`。仅对显式 Python 覆盖使用 `include_prompts` |
| Vercel AI 不工作 | 在每个调用中添加 `experimental_telemetry` |
| Laravel AI 时间跨度未出现 | 验证 `sentry/sentry-laravel >=4.27.0`、`laravel/ai` 已安装，并且 `SENTRY_TRACES_SAMPLE_RATE > 0` |
| 会话视图为空 | 确保已启用 Gen AI 时间跨度流式传输（自 JS SDK 10.61.0 / Python SDK 2.64.0 起默认开启）、genAI 输入/输出捕获已启用（在 JS 中默认通过 `dataCollection` 开启；Python 中的 `send_default_pii=True`；Laravel 中的 `SENTRY_SEND_DEFAULT_PII=true`），并且已设置会话ID |
| 用户列显示 "未知" | 每个请求或会话调用一次 `Sentry.setUser()`（JS）或 `sentry_sdk.set_user()`（Python） |
