**首先**：使用父级 `neon` 技能来获取 Neon 概览、开始使用 Neon、Neon 开发最佳实践等内容。

如果未安装 `neon` 技能，请从 https://neon.com/docs/ai/skills/neon/SKILL.md 获取或使用以下命令安装：

```bash
neon skills -s neon -y
```

# Neon AI 网关

目前可在 `aws-us-east-2`、`aws-us-east-1`、`aws-eu-central-1` 和 `aws-ap-southeast-1` 区域使用。

Neon AI 网关是集成到你的 Neon 分支中的 LLM 推理层：一个 API 和一个 Neon 凭证即可访问来自多个提供者（Anthropic、OpenAI、Google、Meta 等）的前沿和开源模型，所有模型均由 Databricks 托管和提供支持。目录会随时间变化，因此请将 `/v1/models` 和 [models.dev Neon 页面](https://models.dev/providers/neon)视为事实来源，而不是固定的提供者列表。你的现有 OpenAI/Anthropic/Gemini SDK 通过更改基础 URL 即可工作。

使用此技能帮助用户通过网关发送模型调用，将其连接到 AI SDK 或 Mastra，并在无需重新布线的情况下切换提供者。提供工作推理请求、配置代理或从官方 Neon 文档中获取精确答案。

## 使用场景

当应用程序或代理需要调用 LLM 且用户不希望自行管理模型提供者时，请使用 AI 网关：

- **一个凭证代替多个提供者账户。** 一个 Neon 凭证可以访问 Databricks 托管的所有提供者的整个模型目录。无需单独的 OpenAI / Anthropic / Google 计费、密钥或注册来配置和轮换。
- **无需重新布线即可切换模型。** 统一端点是 OpenAI 兼容的，并且适用于目录中的每个模型——更改一个 `model` 字段即可在 Claude、GPT 和 Gemini 之间切换。标准 SDK（OpenAI、Anthropic、google-genai）只需更改基础 URL 即可工作。
- **AI 随你的分支变化。** 每个分支都有自己的网关端点，其作用范围与你的数据库相同。来自预览/功能分支的 AI 请求仅限于该分支——这与你的数据已经获得的隔离相同，这使得预览、CI 和代理环境自包含。
- **无需额外基础设施，且已靠近你的数据。** 网关位于你的 Neon 项目中（并自动注入到 Neon Functions 中），运行在为每月服务数万亿个 token 的相同 Databricks 基础设施上，并支持流式传输（SSE）。

如果用户已经有一个深入的单一提供者集成且对 Neon 分支或多模型路由不感兴趣，直接使用提供者 SDK 即可——但一旦他们需要一个凭证、模型可移植性或分支范围的 AI，这就是使用它的原因。

## 功能

- **所有模型使用一个 API** — 前沿和开源模型通过单个端点提供，通过其目录 ID 进行访问（例如 `claude-sonnet-4-6`、`gpt-5-mini`、`gemini-3-flash`）。
- **标准 SDK，一个 URL 更改** — OpenAI SDK 和 AI SDK（OpenAI 兼容的 MLflow/Responses 路由）、Anthropic SDK（原生 Messages）、google-genai（原生 Gemini）。
- **分支范围** — 每个分支都有自己的网关主机；Neon 凭证授权该分支及其子分支的请求。
- **流式传输** — 服务器发送事件在所有端点上工作，无需额外配置。

## 可用性

在设置任何内容之前，请检查以下先决条件：

AI 网关目前可在 `aws-us-east-2`、`aws-us-east-1`、`aws-eu-central-1` 和 `aws-ap-southeast-1` 区域使用。基础模型访问需要付费 Neon 计划。确认用户的项目位于这些区域之一。

### 启用网关：计划和模型目录门控

AI 网关是凭证门控而不是配置步骤，但有两个计划限制门控它——一个阻止配置，另一个仅修剪目录——CLI 会显示每个限制：

- **免费计划 → 配置被阻止。** `neon config apply` / `deploy` 和 `neon checkout` **拒绝**在免费计划上启用网关（网关无法在该处服务），并显示友好的“升级到付费计划，或删除 `aiGateway`”错误。干运行 `neon config plan` 和 `neon env pull` 不进行配置，因此它们仅**警告**。因此：要使用网关，项目的账户必须位于付费 Neon 计划上。
- **付费计划，模型目录被缩减。** 在付费计划上，网关会配置并服务，但账户可以开始使用修剪的目录——一些旗舰模型（例如 Anthropic Opus、OpenAI Codex / `*-pro`）从 `GET /v1/models` 中缺失。这是预期的；`neon env pull`（以及捆绑在 `apply` / `deploy` / `checkout` 中的 `env pull`）会警告并链接到 Neon 控制台中该分支的 AI 网关页面（`https://console.neon.tech/app/projects/<project-id>/branches/<branch-id>/ai-gateway`）以请求访问更多模型。通过读取 `/v1/models`（见下方的模型部分）来验证分支实际可用的内容，而不是假设完整目录。

当帮助用户调试“网关无法工作”或“缺少模型”时，使用 `/v1/models` 加上账户的计划来区分这两种情况——免费计划完全阻止配置，而付费计划上的缩减目录只需请求模型访问权限。

## 设置

网关是 `neon.ts` 的一部分（有关分支优先工作流程和 `neon.ts` 基础知识，请参阅 `neon` 技能）。使用 `aiGateway` 启用它：

```typescript
// neon.ts
import { defineConfig } from "@neon/config/v1";

export default defineConfig({
  aiGateway: true,
});
```

```bash
neon deploy   # 在关联的分支上配置网关
```

## Neon 基础设施即代码 (`neon.ts`)

上述 `aiGateway` 开关是 `neon.ts` 的一部分，它是 Neon 的基础设施即代码文件——一个 TypeScript 文件声明了网关以及每个其他分支服务，在版本控制中（有关完整参考，请参阅 `neon` 技能）。以 Terraform 的方式将其与分支进行同步：

```bash
neon config status   # 打印分支的实时配置（网关是否开启？）
neon config plan     # apply 将要更改的干运行差异
neon config apply    # 在分支上启用网关  (neon deploy 是别名)
```

网关是**分支范围的**：每个分支都有自己的网关主机。当存在 `neon.ts` 时，`neon checkout` 会将其策略应用于创建分支时，因此新的预览/CI 分支会自动启用网关。检出**现有**分支不会进行同步——运行 `neon deploy` 以应用更改。配置 (`config apply` / `deploy`)、`link` 和 `checkout` 还会将分支的网关凭证拉入本地 `.env.local`，因此本地运行会命中相同的分支网关，无需手动 `env pull`。

## 环境变量

当 `aiGateway` 启用时，Neon 会将网关凭证作为**Neon 品牌的**环境变量注入。在部署的 Neon Function 中，这些环境变量会自动注入；在本地，`neon env pull` 会将它们写入 `.env`/`.env.local`（或使用 `neon-env run -- <cmd>` 在运行时注入，无需文件）：

| 变量                   | 含义                                                                                                                             |
| ---------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| `NEON_AI_GATEWAY_TOKEN` | 网关访问令牌（Neon 凭证，`nt_live_...`）                                                                                          |
| `NEON_AI_GATEWAY_BASE_URL` | **裸分支网关主机** (`scheme://host`，**无路径**——无 `/ai-gateway`)：`https://<branch-id>-api.ai.<region>.aws.neon.tech` |

> Neon 仅注入**这两个**变量——它**不会**设置 `OPENAI_API_KEY` / `OPENAI_BASE_URL`。`@neon/ai-sdk-provider` 和 Mastra 的 `neon/<model>` 直接读取 `NEON_AI_GATEWAY_*`（零配置）；对于纯 OpenAI SDK / `@ai-sdk/openai`，构建客户端的 `apiKey` + `baseURL`（如下所示），或手动设置自己的 `OPENAI_*`（`env pull` 保留用户设置的变量）。

`NEON_AI_GATEWAY_BASE_URL` 是**裸主机**——你需要自己附加方言路径（这正是 `@neon/ai-sdk-provider` 为你做的）。主机下的路由是：

- `/v1` — 统一、OpenAI **聊天完成**兼容；推荐默认，适用于所有提供者（`/v1/chat/completions`）。
- `/openai/v1` — OpenAI **响应** API（`gpt-5-…-codex` 变体和 `gpt-5-5-pro` 需要）；`@ai-sdk/openai` 提供者默认使用响应 API（`/openai/v1/responses`）。
- `/anthropic` — 原生 Anthropic Messages（扩展思考、提示缓存）。将此作为 Anthropic SDK 的基础 URL，它会自己附加 `/v1/messages`，因此完整请求路径是 `/anthropic/v1/messages`。
- `/gemini` — 原生 Gemini `generateContent`。将此作为 google-genai 的基础 URL，它会自己附加 `/v1beta/models/<model>:generateContent`，因此完整请求路径是 `/gemini/v1beta/models/<model>:generateContent`。

因此 `${NEON_AI_GATEWAY_BASE_URL}/v1` 是聊天完成端点，`${NEON_AI_GATEWAY_BASE_URL}/openai/v1` 是 OpenAI 响应端点（两者都需要你附加）；对于原生的 Anthropic 和 Gemini 方言，你将 `/anthropic` 或 `/gemini` 的较短基础 URL 交给 SDK，它会自己附加剩余部分。见下文 [与纯 SDK 一起使用](#use-with-plain-sdks-lower-level)。

为了获得注入凭证的 typed、validated 访问权限，将相同的 `neon.ts` 配置对象传递给 `@neon/env` 的 `parseEnv`——它返回一个 `env.aiGateway` 命名空间（`apiKey`、`baseUrl`），这些是从你的配置派生的。

## 使用 Vercel AI SDK 构建 Agent（推荐）

[Vercel AI SDK](https://ai-sdk.dev) 是调用网关和从 TypeScript 构建 Agent 的推荐方式：一套基础操作（`generateText`、`streamText`、工具调用、结构化输出）跨所有目录模型，并为 Neon Functions 构建的长时间 Agent 响应提供一流的流式传输。

专用的 `@neon/ai-sdk-provider` 读取 `NEON_AI_GATEWAY_BASE_URL` + `NEON_AI_GATEWAY_TOKEN`，**零配置**，并将每个模型路由到最佳端点（Anthropic → Messages，OpenAI/Codex → Responses，其他所有模型 → MLflow）。在一个流式传输文本和生成图像的 Neon Function 中，只需选择一个目录模型：

```typescript
import { neon } from "@neon/ai-sdk-provider";
import { streamText } from "ai";

const result = streamText({
  model: neon("gpt-5-mini"), // 或 claude-sonnet-4-6, gemini-3-flash, ...
  messages,
  tools: {
    image_generation: neon.tools.imageGeneration({
      outputFormat: "jpeg",
      size: "1024x1024",
    }),
  },
});
return result.toUIMessageStreamResponse();
```

单个完成使用 `generateText` 与同一个提供者相同：

```typescript
import { neon } from "@neon/ai-sdk-provider";
import { generateText } from "ai";

const { text } = await generateText({
  model: neon("claude-haiku-4-5"), // 或 gpt-5-3-codex, gemini-3-flash, ...
  prompt: "总结一下 Postgres 的内容。",
});
```

> 与 `@neon/ai-sdk-provider` 相比，优先使用 `@ai-sdk/openai` 的 `openai()`：Neon 仅注入 `NEON_AI_GATEWAY_*`，不注入 `OPENAI_*`，因此 `openai()` 不会自行从环境中获取网关。如果你确实使用 `@ai-sdk/openai`，请显式配置它：`createOpenAI({ apiKey: process.env.NEON_AI_GATEWAY_TOKEN, baseURL: `${process.env.NEON_AI_GATEWAY_BASE_URL}/openai/v1` })`。

要构建一个**Agent**——一个在循环中调用工具然后回答模型的——添加 `tools` 和一个 `stopWhen` 预算。循环在进程内运行，因此在 Neon Function 上不会被 lambda 风格的超时切断：

```typescript
import { neon } from "@neon/ai-sdk-provider";
import { generateText, tool, stepCountIs } from "ai";
import { z } from "zod";

const { text } = await generateText({
  model: neon("claude-sonnet-4-6"),
  prompt: "我有多少个开放的待办事项，最老的待办事项是什么？",
  tools: {
    listTodos: tool({
      description: "列出用户的开放待办事项。",
      inputSchema: z.object({}), // AI SDK v5+: `inputSchema`，不是 `parameters`
      execute: async () => db.select().from(todos),
    }),
  },
  stopWhen: stepCountIs(5), // 让模型调用工具，然后总结
});
```

对于作为 Neon Function 部署的完整 AI SDK Agent（流式传输、工具调用、图像生成、持久化），请参阅 `neon-functions` 技能的 [references/ai-sdk.md](https://neon.com/docs/ai/skills/neon-functions/references/ai-sdk.md)。

## 使用 Mastra 构建 Agent（推荐）

[Mastra](https://mastra.ai) 是当你想要包含所有功能的 Agent 时推荐的框架——内置内存、工具、工作流和跟踪——模型仍然指向网关。使用 `@mastra/core` 1.47+，使用 `neon/<model>` 魔术字符串；Mastra 从环境（当 `aiGateway` 启用时，由 `neon deploy` 注入）中读取 `NEON_AI_GATEWAY_BASE_URL` 和 `NEON_AI_GATEWAY_TOKEN`。仅使用 `parseEnv` 为其他声明的服务（例如 `env.postgres.databaseUrl` 用于 `@mastra/pg` 内存）：

```typescript
import { Agent } from "@mastra/core/agent";
import { parseEnv } from "@neon/env";
import config from "../neon";

const env = parseEnv(config);

export const personalAssistant = new Agent({
  id: "personal-assistant",
  name: "personal-assistant",
  instructions:
    "你是一个温暖、简洁的个人助理，具有长期记忆。",
  model: "neon/claude-haiku-4-5",
  memory, // 你的 Mastra 内存存储，例如 @mastra/pg 在 env.postgres.databaseUrl
});
```

## 与纯 SDK 一起使用（较低级别）

当你不需要 Agent 框架——单个完成、现有的提供者 SDK 集成或原生提供者功能时——使用纯 SDK 调用网关。Neon 注入 `NEON_AI_GATEWAY_*` 变量（不是 `OPENAI_*`），因此设置客户端的 `apiKey` + `baseURL` 来自它们。对于 OpenAI **响应**方言（`/openai/v1`）：

```typescript
import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.NEON_AI_GATEWAY_TOKEN,
  baseURL: `${process.env.NEON_AI_GATEWAY_BASE_URL}/openai/v1`,
});

const res = await client.responses.create({
  model: "gpt-5-mini", // 切换到 claude-sonnet-4-6, gemini-3-flash, ...
  input: "Neon 是什么？",
});
```

对于统一的 **聊天完成**方言，将 `baseURL` 指向 `/v1`：

```typescript
const client = new OpenAI({
  apiKey: process.env.NEON_AI_GATEWAY_TOKEN,
  baseURL: `${process.env.NEON_AI_GATEWAY_BASE_URL}/v1`,
});

const res = await client.chat.completions.create({
  model: "claude-sonnet-4-6",
  messages: [{ role: "user", content: "Neon 是什么？" }],
});
```

Anthropic SDK 和 google-genai 对于原生提供者功能的工作方式相同——将 Anthropic SDK 指向 `${NEON_AI_GATEWAY_BASE_URL}/anthropic`（它自己附加 `/v1/messages`），将 google-genai 指向 `${NEON_AI_GATEWAY_BASE_URL}/gemini`（它自己附加 `/v1beta/models/...`）。

## 模型标识符

直接在 `model` 字段中使用模型的目录 ID——例如 `claude-sonnet-4-6`、`gpt-5-mini`、`gemini-3-flash`。不需要提供者前缀。要查找网关实际提供的确切标识符、每个标识符映射到的底层模型及其上下文窗口、定价和功能，可以使用任何：

- **models.dev Neon 提供者页面：https://models.dev/providers/neon** — Neon 提供者的模型 ID 和其底层模型的规范、始终最新的列表。机器可读目录在 https://models.dev/api.json（`neon` 键）。
- **模型文档**：见进一步阅读。

## 运行时列出可用模型 (`/v1/models`)

网关还通过你自己的分支端点**实时**暴露模型目录，因此应用程序或代理可以确切地发现此分支提供的模型，而无需硬编码列表。它是一个 OpenAI 兼容的列表端点，仅在统一方言（`/v1`）上提供服务：

```bash
curl "$NEON_AI_GATEWAY_BASE_URL/v1/models" \
  -H "Authorization: Bearer $NEON_AI_GATEWAY_TOKEN"
```

- `GET ${NEON_AI_GATEWAY_BASE_URL}/v1/models` → **200**
- `GET ${NEON_AI_GATEWAY_BASE_URL}/openai/v1/models` → **404**（Responses 方言上不提供——使用 `/v1`）

**获取请求的凭证。** 两个值都来自网关在所有其他地方使用的相同分支范围的 Neon 凭证——你永远不会管理提供者密钥：

- **通过 `neon.ts` 配置（推荐）。** 在 `neon.ts` 中启用 `aiGateway` 并运行 `neon deploy`（或 `neon config apply`）。配置、`neon link` 和 `neon checkout` 将 `NEON_AI_GATEWAY_TOKEN` + `NEON_AI_GATEWAY_BASE_URL` 拉入本地 `.env.local`；在部署的 Neon Function 中，它们会自动注入。见上文的**设置**和**环境变量**。
- **通过 CLI 拉入环境。** `neon env pull` 将这两个变量写入 `.env`/`.env.local`，或 `neon-env run -- <cmd>` 在运行时注入它们，而无需文件——但这仅当 `neon.ts` 声明 `aiGateway` 时才有效；这些变量永远不会单独从分支状态中拉取。
- **通过控制台 UI 配置。** 在 Neon 控制台中启用分支上的 AI 网关，并从项目的连接/凭证视图中复制该分支的网关基础 URL 和一个 Neon 凭证（令牌）。

任何有效的 Neon 凭证（`nt_live_...`）对分支都可作为访问令牌工作；`NEON_AI_GATEWAY_BASE_URL` 是裸分支主机（无路径）。

**响应形状** — OpenAI/OpenRouter 兼容列表：

```jsonc
{
  "object": "list",
  "data": [
    {
      "id": "claude-sonnet-4-6",              // 目录模型 ID — 直接在 `model` 字段中使用
      "canonical_slug": "claude-sonnet-4-6",
      "name": "Claude Sonnet 4.6",            // 人类可读的显示名称
      "object": "model",
      "owned_by": "anthropic",                // 提供者缩写，例如 anthropic | openai | google | meta | alibaba | databricks | ...（非详尽；请查看实时）
      "created": 0,
      "enabled": true,
      "context_length": null,
      "architecture": {
        "modality": "text->text",
        "input_modalities": ["text"],
        "output_modalities": ["text"],
        "tokenizer": "Claude",                // Claude | Gemini | GPT | ""（空字符串表示开源）
        "instruct_type": null
      },
      "top_provider": {
        "is_moderated": false,
        "context_length": null,
        "max_completion_tokens": null
      },
      "pricing": null,
      "per_request_limits": null
    }
    // ... 目录中每个模型都有一个条目
  ]
}
```

> 注意：`context_length`、`pricing` 和 `per_request_limits` 目前为 `null`，`created` 为 `0`，每个条目——对于上下文窗口、定价和功能，请使用上面的 models.dev 目录。当你需要实时、分支范围的可用模型 ID 列表时（例如，填充模型选择器或在请求前验证 `model`），请使用 `/v1/models`。

## Neon 文档

Neon 文档是事实来源，AI 网关正在快速发展，因此请始终参考官方文档进行验证。任何文档页面都可以通过在 URL 中附加 `.md` 或请求 `Accept: text/markdown` 来获取 Markdown 格式。从文档索引（https://neon.com/docs/llms.txt）和变更日志公告中找到正确的页面。

## 进一步阅读

- https://neon.com/docs/ai-gateway/overview.md
- https://neon.com/docs/ai-gateway/get-started.md
- https://neon.com/docs/ai-gateway/models.md
- https://neon.com/docs/ai-gateway/chat-completions.md
- https://neon.com/docs/ai-gateway/anthropic-messages.md
- https://neon.com/docs/ai-gateway/openai-responses.md
- https://neon.com/docs/ai-gateway/gemini.md
- https://neon.com/docs/ai-gateway/authentication.md
- https://neon.com/docs/ai-gateway/troubleshooting.md
